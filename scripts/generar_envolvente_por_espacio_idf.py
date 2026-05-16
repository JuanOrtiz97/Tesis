from __future__ import annotations

import argparse
import math
from collections import defaultdict
from pathlib import Path


def parse_number(value: str) -> float | None:
    value = value.strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_idf(path: Path) -> list[tuple[str, list[str]]]:
    clean_lines: list[str] = []
    for line in path.read_text(encoding="latin-1").splitlines():
        line = line.split("!", 1)[0].strip()
        if line:
            clean_lines.append(line)

    objects: list[tuple[str, list[str]]] = []
    for raw in "\n".join(clean_lines).split(";"):
        raw = raw.strip()
        if not raw:
            continue
        fields = [field.strip() for field in raw.split(",")]
        objects.append((fields[0], fields[1:]))
    return objects


def tex_escape(value: str) -> str:
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


def fmt(value: float | None, decimals: int = 2) -> str:
    if value is None or not math.isfinite(value):
        return "--"
    return f"{value:.{decimals}f}".replace(".", ",")


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


def construction_label(name: str) -> str:
    label = name
    for token in ("_Reversed_Rev", "_Reversed", "_Rev"):
        label = label.replace(token, "")
    return label


def vertices_from_fields(fields: list[str], start: int) -> list[tuple[float, float, float]]:
    count_index = None
    count = None
    for index in range(start, len(fields)):
        try:
            candidate = int(float(fields[index]))
        except ValueError:
            continue
        remaining = len(fields) - index - 1
        if candidate > 0 and remaining >= candidate * 3:
            count_index = index
            count = candidate
            break

    if count_index is None or count is None:
        return []

    values = fields[count_index + 1 : count_index + 1 + count * 3]
    coords = [parse_number(value) for value in values]
    if any(value is None for value in coords):
        return []
    numbers = [float(value) for value in coords if value is not None]
    return [(numbers[i], numbers[i + 1], numbers[i + 2]) for i in range(0, len(numbers), 3)]


def polygon_area(vertices: list[tuple[float, float, float]]) -> float:
    if len(vertices) < 3:
        return 0.0
    nx = ny = nz = 0.0
    for current, following in zip(vertices, vertices[1:] + vertices[:1]):
        nx += (current[1] - following[1]) * (current[2] + following[2])
        ny += (current[2] - following[2]) * (current[0] + following[0])
        nz += (current[0] - following[0]) * (current[1] + following[1])
    return 0.5 * math.sqrt(nx * nx + ny * ny + nz * nz)


def category_for_surface(surface_type: str) -> str:
    surface_type = surface_type.lower()
    if surface_type == "wall":
        return "muros"
    if surface_type in {"floor", "ceiling"}:
        return "piso_cielo"
    if surface_type == "roof":
        return "cubierta"
    return "otros"


def category_for_opening(surface_type: str) -> str:
    surface_type = surface_type.lower()
    if surface_type == "window":
        return "ventanas"
    if surface_type == "door":
        return "puertas"
    return "aberturas"


def join_items(items: dict[str, float]) -> str:
    if not items:
        return "--"
    merged: defaultdict[str, float] = defaultdict(float)
    for name, area in items.items():
        if area < 0.005 or name == "IRTSurface":
            continue
        merged[construction_label(name)] += area
    if not merged:
        return "--"
    parts = []
    for name, area in sorted(merged.items()):
        parts.append(f"{name} ({fmt(area)} m2)")
    return "; ".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera una tabla LaTeX de envolvente por espacio desde un archivo IDF.")
    parser.add_argument("idf", type=Path, help="Ruta del archivo IDF exportado desde DesignBuilder/EnergyPlus.")
    parser.add_argument("--out-dir", type=Path, default=Path("insumos"), help="Carpeta de salida para la tabla .tex.")
    args = parser.parse_args()

    objects = parse_idf(args.idf)
    zones: dict[str, tuple[str, str]] = {}
    surfaces: dict[str, dict[str, object]] = {}
    zone_data: dict[str, dict[str, defaultdict[str, float]]] = {}

    for object_type, fields in objects:
        kind = object_type.lower()
        if kind == "zone" and fields:
            zones[fields[0]] = normalize_zone(fields[0])
            zone_data.setdefault(
                fields[0],
                {
                    "muros": defaultdict(float),
                    "piso_cielo": defaultdict(float),
                    "cubierta": defaultdict(float),
                    "ventanas": defaultdict(float),
                    "puertas": defaultdict(float),
                    "aberturas": defaultdict(float),
                },
            )
        elif kind == "buildingsurface:detailed" and len(fields) >= 4:
            name = fields[0]
            surface_type = fields[1]
            construction = fields[2]
            zone = fields[3]
            area = polygon_area(vertices_from_fields(fields, 9))
            surfaces[name] = {
                "type": surface_type,
                "construction": construction,
                "zone": zone,
                "area": area,
            }
            if zone in zone_data and area > 0:
                zone_data[zone][category_for_surface(surface_type)][construction] += area
        elif kind == "fenestrationsurface:detailed" and len(fields) >= 4:
            surface_type = fields[1]
            construction = fields[2]
            parent = fields[3]
            parent_surface = surfaces.get(parent)
            if not parent_surface:
                continue
            zone = str(parent_surface["zone"])
            area = polygon_area(vertices_from_fields(fields, 8))
            if zone in zone_data and area > 0:
                zone_data[zone][category_for_opening(surface_type)][construction] += area

    order = {
        "Planta baja": 0,
        "Primera planta alta": 1,
        "Segunda planta alta": 2,
        "Cubierta": 3,
    }
    rows = []
    for zone, data in zone_data.items():
        floor, space = zones.get(zone, normalize_zone(zone))
        rows.append(
            (
                order.get(floor, 99),
                floor,
                space,
                join_items(data["muros"]),
                join_items(data["piso_cielo"]),
                join_items(data["cubierta"]),
                join_items({**data["ventanas"], **data["puertas"], **data["aberturas"]}),
            )
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        r"{\fontsize{7}{9}\selectfont",
        r"\begin{longtable}{p{2.1cm}p{1.6cm}p{3.3cm}p{3.1cm}p{2.5cm}p{2.7cm}}",
        r"  \caption{Envolvente y materiales asignados por espacio en el caso base} \\",
        r"  \toprule",
        r"  Planta & Espacio & Muros & Piso y cielo & Cubierta & Ventanas y puertas \\",
        r"  \midrule",
        r"  \endfirsthead",
        r"  \caption[]{Envolvente y materiales asignados por espacio en el caso base (continuacion)} \\",
        r"  \toprule",
        r"  Planta & Espacio & Muros & Piso y cielo & Cubierta & Ventanas y puertas \\",
        r"  \midrule",
        r"  \endhead",
        r"  \bottomrule",
        r"  \endfoot",
    ]
    for _, floor, space, walls, floor_ceiling, roof, openings in sorted(rows):
        lines.append(
            "  "
            + " & ".join(
                [
                    tex_escape(floor),
                    tex_escape(space),
                    tex_escape(walls),
                    tex_escape(floor_ceiling),
                    tex_escape(roof),
                    tex_escape(openings),
                ]
            )
            + r" \\"
        )
    lines.extend(
        [
            r"\end{longtable}",
            r"}",
            r"\fuente{Elaboracion propia a partir de las superficies \texttt{BuildingSurface:Detailed} y \texttt{FenestrationSurface:Detailed} del archivo IDF \texttt{Caso Base-5.idf}. Las areas corresponden a las superficies geometricas asignadas a cada zona termica.}",
        ]
    )
    (args.out_dir / "envolvente-por-espacio-tabla.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
