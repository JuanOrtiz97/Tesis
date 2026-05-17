from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path


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


def as_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip().replace(",", ".")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def fmt(value: float | None, digits: int = 2) -> str:
    if value is None or not math.isfinite(value):
        return "--"
    return f"{value:.{digits}f}".replace(".", ",")


def tex(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def normalize_zone(raw: str) -> tuple[str, str]:
    if raw.startswith("PEOPLE "):
        raw = raw.removeprefix("PEOPLE ")
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


def table_records(rows: list[list[str]]) -> list[dict[str, str]]:
    header = rows[0]
    return [dict(zip(header, row)) for row in rows[1:] if row]


def read_summary(path: Path) -> dict[str, list[list[str]]]:
    parser = EnergyPlusTableParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    return dict(parser.tables)


def read_hourly_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="latin-1", newline="") as handle:
        reader = csv.reader(handle, delimiter=";")
        header = [item.strip('"') for item in next(reader)]
        next(reader, None)
        rows = []
        for row in reader:
            if not row or not row[0].strip('"'):
                continue
            rows.append({header[index]: row[index].strip('"') if index < len(row) else "" for index in range(len(header))})
        return rows


def column_values(rows: list[dict[str, str]], column: str) -> list[float]:
    return [value for value in (as_float(row.get(column)) for row in rows) if value is not None]


def sum_negative_abs(rows: list[dict[str, str]], column: str) -> float:
    return sum(-value for value in column_values(rows, column) if value < 0)


def max_abs_with_time(rows: list[dict[str, str]], column: str) -> tuple[float | None, str]:
    best_value: float | None = None
    best_time = ""
    for row in rows:
        value = as_float(row.get(column))
        if value is None:
            continue
        if best_value is None or abs(value) > abs(best_value):
            best_value = value
            best_time = row.get("Date/Time", "")
    return best_value, best_time


def find_row(records: list[dict[str, str]], label: str) -> dict[str, str]:
    for record in records:
        if record.get("", "") == label:
            return record
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera una sintesis simple del caso base desde Summary HTML y CSV horario.")
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("insumos/caso-base-sintesis-tablas.tex"))
    args = parser.parse_args()

    tables = read_summary(args.summary)
    hourly = read_hourly_csv(args.csv)

    zone_rows = table_records(tables["FullName:Input Verification and Results Summary_Entire Facility_Zone Summary"])
    cooling_rows = table_records(tables["FullName:HVAC Sizing Summary_Entire Facility_Zone Sensible Cooling"])
    adaptive_rows = table_records(tables["FullName:Adaptive Comfort Summary_Entire Facility_Time Not Meeting the Adaptive Comfort Models during Occupied Hours"])
    building_area = table_records(tables["FullName:Annual Building Utility Performance Summary_Entire Facility_Building Area"])
    end_uses = table_records(tables["FullName:Annual Building Utility Performance Summary_Entire Facility_End Uses"])
    wwr = table_records(tables["FullName:Input Verification and Results Summary_Entire Facility_Window-Wall Ratio"])
    opaque = table_records(tables["FullName:Envelope Summary_Entire Facility_Opaque Exterior"])
    fenestration = table_records(tables["FullName:Envelope Summary_Entire Facility_Exterior Fenestration"])

    cooling_by_zone: dict[tuple[str, str], dict[str, str]] = {}
    for row in cooling_rows:
        floor, zone = normalize_zone(row.get("", ""))
        cooling_by_zone[(floor, zone)] = row

    adaptive_by_zone: dict[tuple[str, str], dict[str, str]] = {}
    for row in adaptive_rows:
        floor, zone = normalize_zone(row.get("", ""))
        adaptive_by_zone[(floor, zone)] = row

    floor_order = {
        "Planta baja": 0,
        "Primera planta alta": 1,
        "Segunda planta alta": 2,
        "Cubierta": 3,
    }
    floor_data: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    space_rows: list[tuple[int, str, str, dict[str, str]]] = []
    for row in zone_rows:
        raw_zone = row.get("", "")
        if raw_zone in {"Total", "Conditioned Total", "Unconditioned Total", "Not Part of Total"}:
            continue
        floor, zone = normalize_zone(raw_zone)
        space_rows.append((floor_order.get(floor, 99), floor, zone, row))
        data = floor_data[floor]
        data["zonas"] += 1
        for source, target in [
            ("Area [m2]", "area"),
            ("Volume [m3]", "volumen"),
            ("Above Ground Gross Wall Area [m2]", "muro"),
            ("Window Glass Area [m2]", "vidrio"),
            ("Opening Area [m2]", "aberturas"),
        ]:
            data[target] += as_float(row.get(source)) or 0

    total_area = as_float(find_row(building_area, "Total Building Area").get("Area [m2]"))
    conditioned_area = as_float(find_row(building_area, "Net Conditioned Building Area").get("Area [m2]"))
    wall_area = as_float(find_row(wwr, "Gross Wall Area [m2]").get("Total"))
    window_area = as_float(find_row(wwr, "Window Opening Area [m2]").get("Total"))
    wwr_total = as_float(find_row(wwr, "Gross Window-Wall Ratio [%]").get("Total"))
    cooling_energy = sum_negative_abs(hourly, "Total Cooling")
    peak_cooling, peak_cooling_time = max_abs_with_time(hourly, "Total Cooling")
    op_values = column_values(hourly, "Operative Temperature")
    outside_values = column_values(hourly, "Outside Dry-Bulb Temperature")
    vent_values = column_values(hourly, "Mech Vent + Nat Vent + Infiltration")
    solar_ext = column_values(hourly, "Solar Gains Exterior Windows")
    lighting = as_float(find_row(end_uses, "Interior Lighting").get("Electricity [kWh]"))
    equipment = as_float(find_row(end_uses, "Interior Equipment").get("Electricity [kWh]"))

    lines: list[str] = []
    lines.extend(
        [
            r"{\fontsize{9}{11}\selectfont",
            r"\begin{longtable}{p{5.2cm}p{3cm}p{5.2cm}}",
            r"  \caption{Sintesis general del caso base} \\",
            r"  \toprule",
            r"  Indicador & Valor & Lectura para el caso base \\",
            r"  \midrule",
            r"  \endfirsthead",
            r"  \caption[]{Sintesis general del caso base (continuacion)} \\",
            r"  \toprule",
            r"  Indicador & Valor & Lectura para el caso base \\",
            r"  \midrule",
            r"  \endhead",
            r"  \bottomrule",
            r"  \endfoot",
            f"  Area total modelada & ${fmt(total_area)}\\,m^2$ & Area usada como base para intensidades y comparaciones. \\\\",
            f"  Area condicionada & ${fmt(conditioned_area)}\\,m^2$ & Todo el modelo se reporta como condicionado en el Summary. \\\\",
            f"  Zonas termicas & {len(space_rows)} & Espacios exportados desde DesignBuilder/EnergyPlus. \\\\",
            f"  Muros exteriores & ${fmt(wall_area)}\\,m^2$ & Superficie opaca vertical expuesta. \\\\",
            f"  Ventanas & ${fmt(window_area)}\\,m^2$ & Superficie transparente reportada por EnergyPlus. \\\\",
            f"  Relacion ventana-muro & ${fmt(wwr_total)}\\%$ & Indicador de exposicion solar y ganancias por vidrio. \\\\",
            f"  Enfriamiento anual horario & ${fmt(cooling_energy)}\\,kWh$ & Suma absoluta del enfriamiento horario del CSV. \\\\",
            f"  Pico de enfriamiento & ${fmt(abs(peak_cooling) if peak_cooling is not None else None)}\\,kW$ & Mayor demanda horaria: {tex(peak_cooling_time)}. \\\\",
            f"  Temperatura operativa media & ${fmt(statistics.mean(op_values) if op_values else None)}\\,^\\circ C$ & Promedio anual horario interior. \\\\",
            f"  Temperatura operativa maxima & ${fmt(max(op_values) if op_values else None)}\\,^\\circ C$ & Valor horario maximo interior. \\\\",
            r"\end{longtable}",
            r"}",
            r"\fuente{Elaboracion propia a partir de \texttt{Sumarry 2.htm} y \texttt{datos simulacion 1.csv}.}",
            "",
        ]
    )

    lines.extend(
        [
            r"{\fontsize{9}{11}\selectfont",
            r"\begin{longtable}{p{3.1cm}p{1.3cm}p{1.6cm}p{1.7cm}p{1.8cm}p{1.6cm}p{1.8cm}}",
            r"  \caption{Resumen geometrico y de envolvente por planta} \\",
            r"  \toprule",
            r"  Planta & Zonas & Area & Volumen & Muro ext. & Vidrio & Aberturas \\",
            r"  & & $m^2$ & $m^3$ & $m^2$ & $m^2$ & $m^2$ \\",
            r"  \midrule",
            r"  \endfirsthead",
            r"  \caption[]{Resumen geometrico y de envolvente por planta (continuacion)} \\",
            r"  \toprule",
            r"  Planta & Zonas & Area & Volumen & Muro ext. & Vidrio & Aberturas \\",
            r"  & & $m^2$ & $m^3$ & $m^2$ & $m^2$ & $m^2$ \\",
            r"  \midrule",
            r"  \endhead",
            r"  \bottomrule",
            r"  \endfoot",
        ]
    )
    for floor, data in sorted(floor_data.items(), key=lambda item: floor_order.get(item[0], 99)):
        lines.append(
            f"  {tex(floor)} & {int(data['zonas'])} & ${fmt(data['area'])}$ & ${fmt(data['volumen'])}$ & ${fmt(data['muro'])}$ & ${fmt(data['vidrio'])}$ & ${fmt(data['aberturas'])}$ \\\\"
        )
    lines.extend([r"\end{longtable}", r"}", r"\fuente{Basado en la tabla \textit{Zone Summary} de EnergyPlus.}", ""])

    lines.extend(
        [
            r"{\fontsize{8}{10}\selectfont",
            r"\begin{longtable}{p{2.5cm}p{1.8cm}p{1.3cm}p{1.5cm}p{1.5cm}p{1.5cm}p{1.6cm}p{1.6cm}}",
            r"  \caption{Espacios del caso base y variables principales de envolvente} \\",
            r"  \toprule",
            r"  Planta & Espacio & Area & Muro ext. & Vidrio & Aberturas & Carga enfr. & No confort 80\% \\",
            r"  & & $m^2$ & $m^2$ & $m^2$ & $m^2$ & $W/m^2$ & h \\",
            r"  \midrule",
            r"  \endfirsthead",
            r"  \caption[]{Espacios del caso base y variables principales de envolvente (continuacion)} \\",
            r"  \toprule",
            r"  Planta & Espacio & Area & Muro ext. & Vidrio & Aberturas & Carga enfr. & No confort 80\% \\",
            r"  & & $m^2$ & $m^2$ & $m^2$ & $m^2$ & $W/m^2$ & h \\",
            r"  \midrule",
            r"  \endhead",
            r"  \bottomrule",
            r"  \endfoot",
        ]
    )
    for _, floor, zone, row in sorted(space_rows):
        cooling = cooling_by_zone.get((floor, zone), {})
        adaptive = adaptive_by_zone.get((floor, zone), {})
        lines.append(
            "  "
            + " & ".join(
                [
                    tex(floor),
                    tex(zone),
                    f"${fmt(as_float(row.get('Area [m2]')))}$",
                    f"${fmt(as_float(row.get('Above Ground Gross Wall Area [m2]')))}$",
                    f"${fmt(as_float(row.get('Window Glass Area [m2]')))}$",
                    f"${fmt(as_float(row.get('Opening Area [m2]')))}$",
                    f"${fmt(as_float(cooling.get('User Design Load per Area [W/m2]')))}$",
                    f"${fmt(as_float(adaptive.get('ASHRAE55 80% Acceptability Limits [Hours]')))}$",
                ]
            )
            + r" \\"
        )
    lines.extend([r"\end{longtable}", r"}", r"\fuente{Basado en \textit{Zone Summary}, \textit{HVAC Sizing Summary} y \textit{Adaptive Comfort Summary} del reporte EnergyPlus.}", ""])

    exterior_constructions: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in opaque:
        construction = row.get("Construction", "")
        if not construction:
            continue
        exterior_constructions[construction]["area"] += as_float(row.get("Gross Area [m2]")) or 0
        exterior_constructions[construction]["u_area"] += (as_float(row.get("U-Factor with Film [W/m2-K]")) or 0) * (as_float(row.get("Gross Area [m2]")) or 0)
    fen_constructions: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in fenestration:
        construction = row.get("Construction", "")
        if not construction:
            continue
        area = as_float(row.get("Glass Area [m2]")) or as_float(row.get("Area of Multiplied Openings [m2]")) or 0
        fen_constructions[construction]["area"] += area
        fen_constructions[construction]["u_area"] += (as_float(row.get("Glass U-Factor [W/m2-K]")) or 0) * area
        fen_constructions[construction]["shgc_area"] += (as_float(row.get("Glass SHGC")) or 0) * area

    lines.extend(
        [
            r"{\fontsize{8}{10}\selectfont",
            r"\begin{longtable}{p{4.2cm}p{2.2cm}p{2.2cm}p{2.2cm}p{3.2cm}}",
            r"  \caption{Envolvente exterior principal del caso base} \\",
            r"  \toprule",
            r"  Sistema & Tipo & Area & U prom. & Observacion \\",
            r"  \midrule",
            r"  \endfirsthead",
            r"  \caption[]{Envolvente exterior principal del caso base (continuacion)} \\",
            r"  \toprule",
            r"  Sistema & Tipo & Area & U prom. & Observacion \\",
            r"  \midrule",
            r"  \endhead",
            r"  \bottomrule",
            r"  \endfoot",
        ]
    )
    for construction, data in sorted(exterior_constructions.items(), key=lambda item: item[1]["area"], reverse=True)[:8]:
        area = data["area"]
        if area <= 0:
            continue
        u_value = data["u_area"] / area if area else None
        lines.append(f"  {tex(construction)} & Opaco exterior & ${fmt(area)}\\,m^2$ & ${fmt(u_value)}$ & Muros, cubiertas o superficies exteriores. \\\\")
    for construction, data in sorted(fen_constructions.items(), key=lambda item: item[1]["area"], reverse=True):
        area = data["area"]
        u_value = data["u_area"] / area if area else None
        shgc = data["shgc_area"] / area if area else None
        lines.append(f"  {tex(construction)} & Ventana & ${fmt(area)}\\,m^2$ & ${fmt(u_value)}$ & SHGC promedio: {fmt(shgc)}. \\\\")
    lines.extend([r"\end{longtable}", r"}", r"\fuente{Basado en el \textit{Envelope Summary} de EnergyPlus.}", ""])

    hours_op_26 = sum(1 for value in op_values if value > 26)
    hours_op_28 = sum(1 for value in op_values if value > 28)
    hours_op_30 = sum(1 for value in op_values if value > 30)
    lines.extend(
        [
            r"{\fontsize{9}{11}\selectfont",
            r"\begin{longtable}{p{4.5cm}p{2.5cm}p{6cm}}",
            r"  \caption{Resultados horarios principales del caso base} \\",
            r"  \toprule",
            r"  Variable & Valor & Interpretacion \\",
            r"  \midrule",
            r"  \endfirsthead",
            r"  \caption[]{Resultados horarios principales del caso base (continuacion)} \\",
            r"  \toprule",
            r"  Variable & Valor & Interpretacion \\",
            r"  \midrule",
            r"  \endhead",
            r"  \bottomrule",
            r"  \endfoot",
            f"  Enfriamiento total horario & ${fmt(cooling_energy)}\\,kWh$ & Demanda anual acumulada de enfriamiento reportada en el CSV. \\\\",
            f"  Pico horario de enfriamiento & ${fmt(abs(peak_cooling) if peak_cooling is not None else None)}\\,kW$ & Ocurre el {tex(peak_cooling_time)}. \\\\",
            f"  Temperatura exterior media & ${fmt(statistics.mean(outside_values) if outside_values else None)}\\,^\\circ C$ & Condicion climatica promedio del archivo horario. \\\\",
            f"  Temperatura operativa media & ${fmt(statistics.mean(op_values) if op_values else None)}\\,^\\circ C$ & Promedio interior del caso base. \\\\",
            f"  Horas con $T_{{op}}>28\\,^\\circ C$ & {hours_op_28} h & Periodos de mayor riesgo de disconfort termico. \\\\",
            f"  Horas con $T_{{op}}>30\\,^\\circ C$ & {hours_op_30} h & Horas criticas de sobrecalentamiento. \\\\",
            f"  Ventilacion/infiltracion media & ${fmt(statistics.mean(vent_values) if vent_values else None)}\\,ACH$ & Renovacion de aire promedio reportada por el modelo. \\\\",
            f"  Ganancia solar exterior maxima & ${fmt(max(solar_ext) if solar_ext else None)}\\,kW$ & Ganancia horaria maxima por ventanas exteriores. \\\\",
            f"  Iluminacion anual & ${fmt(lighting)}\\,kWh$ & Consumo electrico anual de iluminacion interior del Summary. \\\\",
            f"  Equipos interiores anuales & ${fmt(equipment)}\\,kWh$ & Consumo electrico anual de equipos interiores del Summary. \\\\",
            r"\end{longtable}",
            r"}",
            r"\fuente{Elaboracion propia a partir de la serie horaria \texttt{datos simulacion 1.csv} y del \textit{Annual Building Utility Performance Summary}.}",
        ]
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
