from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


SOURCE = Path("datos/cooling-design-designbuilder.csv")
TARGET = Path("insumos/cooling-design-resumen-tabla.tex")
SUMMARY = Path("insumos/cooling-design-resumen.md")


KEY_COLUMNS = [
    "Total Cooling",
    "Sensible Cooling",
    "Zone Sensible Cooling",
    "Solar Gains Exterior Windows",
    "Solar Gains Interior Windows",
    "Glazing",
    "Walls",
    "Roofs",
    "Mech Vent + Nat Vent + Infiltration",
    "External Infiltration",
    "General Lighting",
    "Miscellaneous",
    "Computer + Equip",
    "Occupancy",
    "Air Temperature",
    "Operative Temperature",
    "Outside Dry-Bulb Temperature",
    "Relative Humidity",
]

LABELS = {
    "Total Cooling": "Enfriamiento total",
    "Sensible Cooling": "Enfriamiento sensible",
    "Zone Sensible Cooling": "Enfriamiento sensible de zona",
    "Solar Gains Exterior Windows": "Ganancias solares por ventanas exteriores",
    "Solar Gains Interior Windows": "Ganancias solares por ventanas interiores",
    "Glazing": "Acristalamiento",
    "Walls": "Muros",
    "Roofs": "Cubiertas",
    "Mech Vent + Nat Vent + Infiltration": "Ventilación e infiltración",
    "External Infiltration": "Infiltración exterior",
    "General Lighting": "Iluminación general",
    "Miscellaneous": "Misceláneos",
    "Computer + Equip": "Computadores y equipos",
    "Occupancy": "Ocupación",
    "Air Temperature": "Temperatura del aire",
    "Operative Temperature": "Temperatura operativa",
    "Outside Dry-Bulb Temperature": "Temperatura exterior de bulbo seco",
    "Relative Humidity": "Humedad relativa",
}


def parse_number(value: str) -> float:
    text = value.strip().replace(",", ".")
    if not text:
        return 0.0
    return float(text)


def parse_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%d/%m/%Y %H:%M:%S")


def tex_time(value: str) -> str:
    return parse_datetime(value).strftime("%H:%M")


def tex_number(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def tex_escape(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("#", "\\#")
    )


def read_rows() -> tuple[list[dict[str, str]], dict[str, str]]:
    with SOURCE.open("r", encoding="cp1252", newline="") as handle:
        reader = csv.reader(handle, delimiter=";")
        headers = next(reader)
        units = dict(zip(headers, next(reader)))
        return [dict(zip(headers, row)) for row in reader if row and row[0]], units


def main() -> None:
    rows, units = read_rows()
    if not rows:
        raise RuntimeError("No se encontraron datos en cooling design.")

    total_peak = max(rows, key=lambda row: parse_number(row["Total Cooling"]))
    total_min = min(rows, key=lambda row: parse_number(row["Total Cooling"]))

    summaries = []
    for column in KEY_COLUMNS:
        values = [(parse_number(row[column]), row["Date/Time"]) for row in rows]
        max_value, max_time = max(values, key=lambda item: item[0])
        min_value, min_time = min(values, key=lambda item: item[0])
        summaries.append((column, min_value, min_time, max_value, max_time))

    lines = [
        r"{\fontsize{9}{11}\selectfont",
        r"\begin{longtable}{p{3.8cm}p{1.2cm}p{1.6cm}p{2.1cm}p{1.6cm}p{2.1cm}}",
        r"  \caption{Resumen del día de diseño de enfriamiento del caso base} \\",
        r"  \toprule",
        r"  Variable & Unidad & Mínimo & Hora mín. & Máximo & Hora máx. \\",
        r"  \midrule",
        r"  \endfirsthead",
        r"  \caption[]{Resumen del día de diseño de enfriamiento del caso base (continuación)} \\",
        r"  \toprule",
        r"  Variable & Unidad & Mínimo & Hora mín. & Máximo & Hora máx. \\",
        r"  \midrule",
        r"  \endhead",
        r"  \bottomrule",
        r"  \endfoot",
    ]
    for column, min_value, min_time, max_value, max_time in summaries:
        lines.append(
            "  {name} & {unit} & ${min_value}$ & {min_time} & ${max_value}$ & {max_time} \\\\".format(
                name=tex_escape(LABELS.get(column, column)),
                unit=tex_escape(units.get(column, "")),
                min_value=tex_number(min_value),
                min_time=tex_escape(tex_time(min_time)),
                max_value=tex_number(max_value),
                max_time=tex_escape(tex_time(max_time)),
            )
        )
    lines.extend(
        [
            r"\end{longtable}",
            r"}",
            r"\fuente{Basado en el archivo \texttt{cooling design.csv} exportado desde DesignBuilder.}",
            "",
        ]
    )
    TARGET.write_text("\n".join(lines), encoding="utf-8")

    peak_time = parse_datetime(total_peak["Date/Time"])
    min_time = parse_datetime(total_min["Date/Time"])
    md = [
        "# Resumen del dia de diseno de enfriamiento",
        "",
        f"Fuente local: `{SOURCE.as_posix()}`",
        "",
        f"- Maximo Total Cooling: {tex_number(parse_number(total_peak['Total Cooling']))} kW en {peak_time:%d/%m/%Y %H:%M}.",
        f"- Minimo Total Cooling: {tex_number(parse_number(total_min['Total Cooling']))} kW en {min_time:%d/%m/%Y %H:%M}.",
        f"- Temperatura operativa en el maximo: {tex_number(parse_number(total_peak['Operative Temperature']))} °C.",
        f"- Temperatura exterior en el maximo: {tex_number(parse_number(total_peak['Outside Dry-Bulb Temperature']))} °C.",
        "",
    ]
    SUMMARY.write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    main()
