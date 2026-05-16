from __future__ import annotations

import argparse
import math
from collections import Counter, defaultdict
from pathlib import Path


def parse_number(value: str) -> float | None:
    value = value.strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def extract_aliases(path: Path) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for line in path.read_text(encoding="latin-1").splitlines():
        if "!-" not in line:
            continue
        left, comment = line.split("!-", 1)
        parts = [part.strip() for part in left.split(",")]
        if len(parts) >= 2 and parts[0].lower() in {"windowmaterial:gas", "windowmaterial:glazing"}:
            aliases[parts[1]] = comment.strip()
    return aliases


def parse_idf(path: Path) -> list[tuple[str, list[str]]]:
    text = path.read_text(encoding="latin-1")
    clean_lines: list[str] = []
    for line in text.splitlines():
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


def fmt(value: float | None, decimals: int = 3) -> str:
    if value is None or not math.isfinite(value):
        return "--"
    return f"{value:.{decimals}f}".replace(".", ",")


def material_label(name: str, aliases: dict[str, str] | None = None) -> str:
    if aliases and name in aliases:
        return aliases[name]
    cleaned = name
    for suffix in (".15", ".02", ".018", ".015", ".01", ".1319", ".1", ".013", ".035", ".008", ".005", ".2", ".14"):
        if cleaned.endswith("_" + suffix):
            cleaned = cleaned[: -(len(suffix) + 1)]
            break
    return cleaned


def construction_label(name: str) -> str:
    label = name
    for token in ("_Reversed_Rev", "_Reversed", "_Rev"):
        label = label.replace(token, "")
    return label


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera tablas LaTeX de materiales y construcciones desde un archivo IDF.")
    parser.add_argument("idf", type=Path, help="Ruta del archivo IDF exportado desde DesignBuilder/EnergyPlus.")
    parser.add_argument("--out-dir", type=Path, default=Path("insumos"), help="Carpeta de salida para las tablas .tex.")
    args = parser.parse_args()

    aliases = extract_aliases(args.idf)
    objects = parse_idf(args.idf)

    materials: dict[str, dict[str, float | str | None]] = {}
    constructions: dict[str, list[str]] = {}
    usage: dict[str, Counter[str]] = defaultdict(Counter)

    for object_type, values in objects:
        kind = object_type.lower()
        if kind == "material" and len(values) >= 6:
            materials[values[0]] = {
                "kind": "opaco",
                "name": values[0],
                "thickness": parse_number(values[2]),
                "conductivity": parse_number(values[3]),
                "density": parse_number(values[4]),
                "specific_heat": parse_number(values[5]),
                "resistance": None,
                "solar_t": None,
                "visible_t": None,
            }
        elif kind == "material:nomass" and len(values) >= 3:
            materials[values[0]] = {
                "kind": "sin masa",
                "name": values[0],
                "thickness": None,
                "conductivity": None,
                "density": None,
                "specific_heat": None,
                "resistance": parse_number(values[2]),
                "solar_t": None,
                "visible_t": None,
            }
        elif kind == "material:infraredtransparent" and values:
            materials[values[0]] = {
                "kind": "infrarrojo transparente",
                "name": values[0],
                "thickness": None,
                "conductivity": None,
                "density": None,
                "specific_heat": None,
                "resistance": None,
                "solar_t": None,
                "visible_t": None,
            }
        elif kind == "windowmaterial:glazing" and len(values) >= 14:
            materials[values[0]] = {
                "kind": "vidrio",
                "name": values[0],
                "thickness": parse_number(values[3]),
                "conductivity": parse_number(values[13]),
                "density": None,
                "specific_heat": None,
                "resistance": None,
                "solar_t": parse_number(values[4]),
                "visible_t": parse_number(values[7]),
            }
        elif kind == "windowmaterial:gas" and len(values) >= 3:
            materials[values[0]] = {
                "kind": "camara de aire",
                "name": values[0],
                "thickness": parse_number(values[2]),
                "conductivity": None,
                "density": None,
                "specific_heat": None,
                "resistance": None,
                "solar_t": None,
                "visible_t": None,
            }
        elif kind == "construction" and len(values) >= 2:
            constructions[values[0]] = [value for value in values[1:] if value]
        elif kind == "buildingsurface:detailed" and len(values) >= 3:
            usage[values[2]][values[1]] += 1
        elif kind == "fenestrationsurface:detailed" and len(values) >= 3:
            usage[values[2]][values[1]] += 1

    material_use: Counter[str] = Counter()
    for construction, layers in constructions.items():
        if construction in usage:
            for layer in layers:
                material_use[layer] += sum(usage[construction].values())

    args.out_dir.mkdir(parents=True, exist_ok=True)

    material_rows = []
    for name, data in sorted(materials.items(), key=lambda item: material_label(item[0], aliases).lower()):
        if material_use[name] == 0:
            continue
        if data["kind"] == "infrarrojo transparente":
            continue
        thickness = data.get("thickness")
        conductivity = data.get("conductivity")
        resistance = data.get("resistance")
        if resistance is None and isinstance(thickness, float) and isinstance(conductivity, float) and conductivity > 0:
            resistance = thickness / conductivity
        material_rows.append(
            "  "
            + " & ".join(
                [
                    tex_escape(material_label(name, aliases)),
                    tex_escape(str(data["kind"])),
                    fmt(thickness, 4),
                    fmt(conductivity, 3),
                    fmt(data.get("density") if isinstance(data.get("density"), float) else None, 0),
                    fmt(data.get("specific_heat") if isinstance(data.get("specific_heat"), float) else None, 0),
                    fmt(resistance if isinstance(resistance, float) else None, 3),
                ]
            )
            + r" \\"
        )

    material_table = "\n".join(
        [
            r"{\fontsize{8}{10}\selectfont",
            r"\begin{longtable}{p{3.2cm}p{1.9cm}p{1.4cm}p{1.6cm}p{1.5cm}p{1.7cm}p{1.5cm}}",
            r"  \caption{Propiedades termicas de materiales usados en el modelo base} \\",
            r"  \toprule",
            r"  Material & Tipo & Espesor (m) & Conductividad (W/mK) & Densidad (kg/m\textsuperscript{3}) & Calor esp. (J/kgK) & R capa (m\textsuperscript{2}K/W) \\",
            r"  \midrule",
            r"  \endfirsthead",
            r"  \caption[]{Propiedades termicas de materiales usados en el modelo base (continuacion)} \\",
            r"  \toprule",
            r"  Material & Tipo & Espesor (m) & Conductividad (W/mK) & Densidad (kg/m\textsuperscript{3}) & Calor esp. (J/kgK) & R capa (m\textsuperscript{2}K/W) \\",
            r"  \midrule",
            r"  \endhead",
            r"  \bottomrule",
            r"  \endfoot",
            *material_rows,
            r"\end{longtable}",
            r"}",
            r"\fuente{Elaboracion propia a partir del archivo IDF \texttt{Caso Base-5.idf} exportado desde DesignBuilder.}",
        ]
    )
    (args.out_dir / "materiales-caso-base-tabla.tex").write_text(material_table + "\n", encoding="utf-8")

    def layer_signature(layer: str) -> str:
        data = materials.get(layer)
        if not data:
            return layer
        resistance = data.get("resistance")
        thickness = data.get("thickness")
        conductivity = data.get("conductivity")
        if isinstance(resistance, float):
            return f"R:{resistance:.5f}"
        if isinstance(thickness, float) and isinstance(conductivity, float):
            return f"{material_label(layer, aliases)}:{thickness:.5f}:{conductivity:.5f}"
        return material_label(layer, aliases)

    grouped: dict[str, dict[str, object]] = {}
    for construction, layers in constructions.items():
        if construction not in usage:
            continue
        if "IRTMaterial" in layers:
            continue
        key = construction_label(construction) + " | " + " | ".join(sorted(layer_signature(layer) for layer in layers))
        item = grouped.setdefault(
            key,
            {
                "names": set(),
                "uses": Counter(),
                "layers": layers,
            },
        )
        item["names"].add(construction_label(construction))  # type: ignore[index]
        item["uses"].update(usage[construction])  # type: ignore[index]

    construction_rows = []
    for item in sorted(grouped.values(), key=lambda value: ", ".join(sorted(value["names"]))):  # type: ignore[index]
        layers = item["layers"]  # type: ignore[assignment]
        names = sorted(item["names"])  # type: ignore[index]
        uses = item["uses"]  # type: ignore[assignment]
        thickness_total = 0.0
        resistance_total = 0.0
        opaque_u_possible = not any(
            token in " / ".join(names).lower()
            for token in ("vidrio", "glazing", "clr", "clear")
        )
        layer_labels = []
        for layer in layers:
            data = materials.get(layer)
            layer_labels.append(material_label(layer, aliases))
            if not data:
                opaque_u_possible = False
                continue
            thickness = data.get("thickness")
            conductivity = data.get("conductivity")
            resistance = data.get("resistance")
            if isinstance(thickness, float):
                thickness_total += thickness
            if data.get("kind") in {"vidrio", "camara de aire", "infrarrojo transparente"}:
                opaque_u_possible = False
            elif isinstance(resistance, float):
                resistance_total += resistance
            elif isinstance(thickness, float) and isinstance(conductivity, float) and conductivity > 0 and data.get("kind") != "camara de aire":
                resistance_total += thickness / conductivity
            else:
                opaque_u_possible = False
        u_value = 1 / resistance_total if opaque_u_possible and resistance_total > 0 else None
        use_text = "; ".join(f"{tex_escape(surface)}: {count}" for surface, count in sorted(uses.items()))
        construction_rows.append(
            "  "
            + " & ".join(
                [
                    tex_escape(" / ".join(names)),
                    tex_escape(use_text),
                    tex_escape(" + ".join(layer_labels)),
                    fmt(thickness_total if thickness_total > 0 else None, 4),
                    fmt(resistance_total if resistance_total > 0 else None, 3),
                    fmt(u_value, 2),
                ]
            )
            + r" \\"
        )

    construction_table = "\n".join(
        [
            r"{\fontsize{8}{10}\selectfont",
            r"\begin{longtable}{p{3.2cm}p{2.1cm}p{4.6cm}p{1.4cm}p{1.4cm}p{1.4cm}}",
            r"  \caption{Configuracion constructiva de la envolvente del caso base} \\",
            r"  \toprule",
            r"  Construccion IDF & Uso en modelo & Capas principales & Espesor (m) & R total & U aprox. \\",
            r"  \midrule",
            r"  \endfirsthead",
            r"  \caption[]{Configuracion constructiva de la envolvente del caso base (continuacion)} \\",
            r"  \toprule",
            r"  Construccion IDF & Uso en modelo & Capas principales & Espesor (m) & R total & U aprox. \\",
            r"  \midrule",
            r"  \endhead",
            r"  \bottomrule",
            r"  \endfoot",
            *construction_rows,
            r"\end{longtable}",
            r"}",
            r"\fuente{Elaboracion propia a partir del archivo IDF \texttt{Caso Base-5.idf}. El valor U se calcula como aproximacion capa a capa sin resistencias superficiales; los sistemas de acristalamiento se mantienen como configuracion de EnergyPlus cuando incluyen camaras de gas.}",
        ]
    )
    (args.out_dir / "envolvente-caso-base-tabla.tex").write_text(construction_table + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
