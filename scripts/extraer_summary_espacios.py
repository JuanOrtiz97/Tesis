from __future__ import annotations

import argparse
import csv
from html.parser import HTMLParser
from pathlib import Path


ZONE_SUMMARY = "FullName:Input Verification and Results Summary_Entire Facility_Zone Summary"


class EnergyPlusTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.last_comment = ""
        self.tables: list[tuple[str, list[list[str]]]] = []
        self.in_table = False
        self.in_cell = False
        self.rows: list[list[str]] = []
        self.row: list[str] = []
        self.cell: list[str] = []

    def handle_comment(self, data: str) -> None:
        self.last_comment = data.strip()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self.in_table = True
            self.rows = []
        elif self.in_table and tag == "tr":
            self.row = []
        elif self.in_table and tag == "td":
            self.in_cell = True
            self.cell = []

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.in_table and tag == "td":
            self.in_cell = False
            self.row.append(" ".join("".join(self.cell).split()))
        elif self.in_table and tag == "tr":
            self.rows.append(self.row)
        elif tag == "table" and self.in_table:
            self.tables.append((self.last_comment, self.rows))
            self.in_table = False


def normalize_zone(raw: str) -> tuple[str, str]:
    if ":" not in raw:
        return "", raw

    raw_floor, raw_zone = raw.split(":", 1)
    floor_map = {
        "PLANTABAJA": "Planta baja",
        "PRIMERAPLANTAALTA": "Primera planta alta",
        "SEGUNDAPLANTAALTA": "Segunda planta alta",
        "CUBIERTA": "Cubierta",
    }
    floor = floor_map.get(raw_floor, raw_floor)

    zone = raw_zone
    if zone.startswith("PBX"):
        zone = "PB-" + zone[3:].replace("X", "-")
    elif zone.startswith("1PAX"):
        zone = "1PA-" + zone[4:].replace("X", "-")
    elif zone.startswith("2PAX"):
        zone = "2PA-" + zone[4:].replace("X", "-")

    return floor, zone


def as_float(value: str) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def fmt(value: str, digits: int = 2) -> str:
    number = as_float(value)
    if number is None:
        return ""
    return f"{number:.{digits}f}"


def fmt_latex(value: str, digits: int = 2) -> str:
    value = fmt(value, digits)
    return value.replace(".", ",")


def yes_no(value: str) -> str:
    if value == "Yes":
        return "Sí"
    if value == "No":
        return "No"
    return value


def latex_escape(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("#", "\\#")
    )


def read_zone_summary(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    parser = EnergyPlusTableParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))

    rows: list[list[str]] | None = None
    for comment, table_rows in parser.tables:
        if comment == ZONE_SUMMARY:
            rows = table_rows
            break

    if not rows:
        raise RuntimeError("No se encontro la tabla Zone Summary en el HTML.")

    header = ["Zone"] + rows[0][1:]
    records: list[dict[str, str]] = []
    for row in rows[1:]:
        if not row or row[0] in {"Total", "Conditioned Total", "Unconditioned Total", "Not Part of Total"}:
            continue
        floor, zone = normalize_zone(row[0])
        data = dict(zip(header, row))
        data["Planta"] = floor
        data["Espacio"] = zone
        records.append(data)

    return header, records


def write_csv(records: list[dict[str, str]], path: Path) -> None:
    fields = [
        "planta",
        "espacio",
        "area_m2",
        "condicionado",
        "parte_area_total",
        "volumen_m3",
        "multiplicador",
        "muro_exterior_m2",
        "muro_subterraneo_m2",
        "vidrio_m2",
        "aberturas_m2",
        "iluminacion_w_m2",
        "ocupacion_m2_persona",
        "equipos_w_m2",
    ]
    mapping = {
        "planta": "Planta",
        "espacio": "Espacio",
        "area_m2": "Area [m2]",
        "condicionado": "Conditioned (Y/N)",
        "parte_area_total": "Part of Total Floor Area (Y/N)",
        "volumen_m3": "Volume [m3]",
        "multiplicador": "Multipliers",
        "muro_exterior_m2": "Above Ground Gross Wall Area [m2]",
        "muro_subterraneo_m2": "Underground Gross Wall Area [m2]",
        "vidrio_m2": "Window Glass Area [m2]",
        "aberturas_m2": "Opening Area [m2]",
        "iluminacion_w_m2": "Lighting [W/m2]",
        "ocupacion_m2_persona": "People [m2 per person]",
        "equipos_w_m2": "Plug and Process [W/m2]",
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow({field: record.get(mapping[field], "") for field in fields})


def write_markdown(records: list[dict[str, str]], path: Path) -> None:
    lines = [
        "# Espacios extraidos del Summary de EnergyPlus",
        "",
        "Fuente local: `C:/Users/juand/Desktop/Defensoria del Pueblo/Sumarry 1.htm`",
        "",
        "| Planta | Espacio | Area (m2) | Volumen (m3) | Condicionado | Muro ext. (m2) | Vidrio (m2) | Aberturas (m2) | Ilum. (W/m2) | Ocup. (m2/persona) | Equipos (W/m2) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for record in records:
        lines.append(
            "| {planta} | `{espacio}` | {area} | {volumen} | {cond} | {muro} | {vidrio} | {aberturas} | {ilum} | {ocup} | {equipos} |".format(
                planta=record["Planta"],
                espacio=record["Espacio"],
                area=fmt(record["Area [m2]"]),
                volumen=fmt(record["Volume [m3]"]),
                cond=yes_no(record["Conditioned (Y/N)"]),
                muro=fmt(record["Above Ground Gross Wall Area [m2]"]),
                vidrio=fmt(record["Window Glass Area [m2]"]),
                aberturas=fmt(record["Opening Area [m2]"]),
                ilum=fmt(record["Lighting [W/m2]"]),
                ocup=fmt(record["People [m2 per person]"]),
                equipos=fmt(record["Plug and Process [W/m2]"]),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_latex(records: list[dict[str, str]], path: Path) -> None:
    lines = [
        r"{\fontsize{9}{11}\selectfont",
        r"\begin{longtable}{p{2.8cm}p{2.2cm}p{1.4cm}p{1.5cm}p{1.4cm}p{1.5cm}p{1.5cm}}",
        r"  \caption{Geometría y envolvente de los espacios del caso base} \\",
        r"  \toprule",
        r"  Planta & Espacio & Área & Volumen & Muro ext. & Vidrio & Aberturas \\",
        r"  & & $\mathrm{m}^{2}$ & $\mathrm{m}^{3}$ & $\mathrm{m}^{2}$ & $\mathrm{m}^{2}$ & $\mathrm{m}^{2}$ \\",
        r"  \midrule",
        r"  \endfirsthead",
        r"  \caption[]{Geometría y envolvente de los espacios del caso base (continuación)} \\",
        r"  \toprule",
        r"  Planta & Espacio & Área & Volumen & Muro ext. & Vidrio & Aberturas \\",
        r"  & & $\mathrm{m}^{2}$ & $\mathrm{m}^{3}$ & $\mathrm{m}^{2}$ & $\mathrm{m}^{2}$ & $\mathrm{m}^{2}$ \\",
        r"  \midrule",
        r"  \endhead",
        r"  \bottomrule",
        r"  \endfoot",
    ]
    for record in records:
        lines.append(
            "  {planta} & {espacio} & ${area}$ & ${volumen}$ & ${muro}$ & ${vidrio}$ & ${aberturas}$ \\\\".format(
                planta=latex_escape(record["Planta"]),
                espacio=latex_escape(record["Espacio"]),
                area=fmt_latex(record["Area [m2]"]),
                volumen=fmt_latex(record["Volume [m3]"]),
                muro=fmt_latex(record["Above Ground Gross Wall Area [m2]"]),
                vidrio=fmt_latex(record["Window Glass Area [m2]"]),
                aberturas=fmt_latex(record["Opening Area [m2]"]),
            )
        )
    lines.extend(
        [
            r"\end{longtable}",
            r"}",
            r"\fuente{Basado en el reporte \textit{Summary} de EnergyPlus exportado desde DesignBuilder.}",
            "",
            r"{\fontsize{9}{11}\selectfont",
            r"\begin{longtable}{p{2.8cm}p{2.2cm}p{1.7cm}p{1.7cm}p{1.7cm}p{1.5cm}}",
            r"  \caption{Cargas internas asignadas a los espacios del caso base} \\",
            r"  \toprule",
            r"  Planta & Espacio & Iluminación & Ocupación & Equipos & Condic. \\",
            r"  & & $\mathrm{W/m}^{2}$ & $\mathrm{m}^{2}/\mathrm{pers.}$ & $\mathrm{W/m}^{2}$ & \\",
            r"  \midrule",
            r"  \endfirsthead",
            r"  \caption[]{Cargas internas asignadas a los espacios del caso base (continuación)} \\",
            r"  \toprule",
            r"  Planta & Espacio & Iluminación & Ocupación & Equipos & Condic. \\",
            r"  & & $\mathrm{W/m}^{2}$ & $\mathrm{m}^{2}/\mathrm{pers.}$ & $\mathrm{W/m}^{2}$ & \\",
            r"  \midrule",
            r"  \endhead",
            r"  \bottomrule",
            r"  \endfoot",
        ]
    )
    for record in records:
        lines.append(
            "  {planta} & {espacio} & ${ilum}$ & {ocup} & ${equipos}$ & {cond} \\\\".format(
                planta=latex_escape(record["Planta"]),
                espacio=latex_escape(record["Espacio"]),
                ilum=fmt_latex(record["Lighting [W/m2]"]),
                ocup=f"${fmt_latex(record['People [m2 per person]'])}$" if record["People [m2 per person]"] else "--",
                equipos=fmt_latex(record["Plug and Process [W/m2]"]),
                cond=yes_no(record["Conditioned (Y/N)"]),
            )
        )
    lines.extend(
        [
            r"\end{longtable}",
            r"}",
            r"\fuente{Basado en el reporte \textit{Summary} de EnergyPlus exportado desde DesignBuilder.}",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("insumos"))
    args = parser.parse_args()

    _, records = read_zone_summary(args.html)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(records, args.out_dir / "summary-espacios.csv")
    write_markdown(records, args.out_dir / "summary-espacios.md")
    write_latex(records, args.out_dir / "summary-espacios-tablas.tex")


if __name__ == "__main__":
    main()
