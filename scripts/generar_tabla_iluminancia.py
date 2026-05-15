from __future__ import annotations

import csv
from pathlib import Path


SOURCE = Path("datos/iluminancia-designbuilder.csv")
TARGET = Path("insumos/iluminancia-resumen-tabla.tex")


def decimal_to_float(value: str) -> float | None:
    value = value.strip().replace(".", "").replace(",", ".")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def tex_number(value: str, digits: int = 2) -> str:
    number = decimal_to_float(value)
    if number is None:
        return "--"
    return f"{number:.{digits}f}".replace(".", ",")


def tex_escape(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("#", "\\#")
    )


def main() -> None:
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        rows = [row for row in reader if row["Block"] != "Total"]

    lines = [
        r"{\fontsize{9}{11}\selectfont",
        r"\begin{longtable}{p{2.8cm}p{2.0cm}p{1.4cm}p{1.7cm}p{1.7cm}p{1.5cm}p{1.5cm}}",
        r"  \caption{Resumen de iluminancia natural por espacio del caso base} \\",
        r"  \toprule",
        r"  Planta & Espacio & Área & Área sobre umbral & FLD prom. & Ilum. mín. & Ilum. máx. \\",
        r"  & & $\mathrm{m}^{2}$ & \% & \% & lux & lux \\",
        r"  \midrule",
        r"  \endfirsthead",
        r"  \caption[]{Resumen de iluminancia natural por espacio del caso base (continuación)} \\",
        r"  \toprule",
        r"  Planta & Espacio & Área & Área sobre umbral & FLD prom. & Ilum. mín. & Ilum. máx. \\",
        r"  & & $\mathrm{m}^{2}$ & \% & \% & lux & lux \\",
        r"  \midrule",
        r"  \endhead",
        r"  \bottomrule",
        r"  \endfoot",
    ]

    for row in rows:
        lines.append(
            "  {block} & {zone} & ${area}$ & ${area_threshold}$ & ${df_avg}$ & ${lux_min}$ & ${lux_max}$ \\\\".format(
                block=tex_escape(row["Block"]),
                zone=tex_escape(row["Zone"]),
                area=tex_number(row["Floor Area (m2)"]),
                area_threshold=tex_number(row["Floor Area above Threshold (%)"]),
                df_avg=tex_number(row["Average Daylight Factor (%)"]),
                lux_min=tex_number(row["Min Illuminance (lux)"]),
                lux_max=tex_number(row["Max Illuminance (lux)"]),
            )
        )

    lines.extend(
        [
            r"\end{longtable}",
            r"}",
            r"\fuente{Basado en los resultados de iluminancia exportados desde DesignBuilder.}",
            "",
        ]
    )
    TARGET.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
