from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
EPW = ROOT / "datos" / "ECU_GA_San.Cristobal.Intl.AP.840080_TMYx.2011-2025.epw"
FIG_DIR = ROOT / "figuras"
SUMMARY = ROOT / "insumos" / "graficos-epw-san-cristobal.md"

COLS = [
    "year", "month", "day", "hour", "minute", "flags", "dry_bulb", "dew_point",
    "rh", "pressure", "etr_horiz", "etr_direct", "horiz_ir", "ghi", "dni", "dhi",
    "global_h_illum", "direct_normal_illum", "diffuse_h_illum", "zenith_lum",
    "wind_dir", "wind_speed", "total_sky_cover", "opaque_sky_cover", "visibility",
    "ceiling_height", "present_weather_obs", "present_weather_codes",
    "precipitable_water", "aerosol_optical_depth", "snow_depth", "days_since_snow",
    "albedo", "liquid_precip_depth", "liquid_precip_quantity",
]

MONTHS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def parse_epw() -> list[dict[str, float | str]]:
    lines = EPW.read_text(encoding="latin1").splitlines()[8:]
    rows: list[dict[str, float | str]] = []
    for raw in csv.reader(lines):
        if len(raw) < len(COLS):
            continue
        row = dict(zip(COLS, raw[: len(COLS)]))
        for key in COLS:
            if key in {"flags", "present_weather_codes"}:
                continue
            try:
                row[key] = float(row[key])
            except ValueError:
                pass
        rows.append(row)
    return rows


def ok(value: float, field: str) -> bool:
    ranges = {
        "dry_bulb": (-70, 70),
        "rh": (0, 100),
        "ghi": (0, 1500),
        "dni": (0, 1500),
        "dhi": (0, 1500),
        "wind_speed": (0, 60),
        "wind_dir": (0, 360),
        "total_sky_cover": (0, 10),
        "liquid_precip_depth": (0, 500),
    }
    low, high = ranges[field]
    return low <= value <= high


def values(rows: list[dict[str, float | str]], field: str) -> list[float]:
    return [float(r[field]) for r in rows if isinstance(r[field], float) and ok(float(r[field]), field)]


def mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def monthly(rows: list[dict[str, float | str]]) -> dict[str, list[float]]:
    data: dict[str, list[float]] = defaultdict(list)
    for month in range(1, 13):
        subset = [r for r in rows if int(float(r["month"])) == month]
        temps = values(subset, "dry_bulb")
        data["temp_mean"].append(mean(temps))
        data["temp_min"].append(min(temps))
        data["temp_max"].append(max(temps))
        data["rh"].append(mean(values(subset, "rh")))
        data["ghi"].append(sum(values(subset, "ghi")) / 1000)
        data["dni"].append(sum(values(subset, "dni")) / 1000)
        data["dhi"].append(sum(values(subset, "dhi")) / 1000)
        data["wind"].append(mean(values(subset, "wind_speed")))
        data["sky"].append(mean(values(subset, "total_sky_cover")))
        data["precip"].append(sum(values(subset, "liquid_precip_depth")))
    return data


def hourly_by_month(rows: list[dict[str, float | str]]) -> list[list[float]]:
    grid = []
    for month in range(1, 13):
        row = []
        for hour in range(1, 25):
            subset = [r for r in rows if int(float(r["month"])) == month and int(float(r["hour"])) == hour]
            row.append(mean(values(subset, "dry_bulb")))
        grid.append(row)
    return grid


def new_canvas(path: Path, title: str, subtitle: str = "") -> canvas.Canvas:
    c = canvas.Canvas(str(path), pagesize=landscape((720, 430)))
    c.setTitle(title)
    c.setFillColor(colors.HexColor("#17212b"))
    c.setFont("Helvetica-Bold", 17)
    c.drawString(44, 392, title)
    if subtitle:
        c.setFillColor(colors.HexColor("#52616b"))
        c.setFont("Helvetica", 9)
        c.drawString(44, 375, subtitle)
    return c


def axis(c: canvas.Canvas, x: float, y: float, w: float, h: float, label: str = "") -> None:
    c.setStrokeColor(colors.HexColor("#9aa6b2"))
    c.setLineWidth(0.7)
    c.line(x, y, x + w, y)
    c.line(x, y, x, y + h)
    if label:
        c.saveState()
        c.translate(x - 34, y + h / 2)
        c.rotate(90)
        c.setFillColor(colors.HexColor("#52616b"))
        c.setFont("Helvetica", 8)
        c.drawCentredString(0, 0, label)
        c.restoreState()


def scale(v: float, vmin: float, vmax: float, size: float) -> float:
    return 0 if vmax == vmin else (v - vmin) / (vmax - vmin) * size


def month_labels(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    step = w / 12
    c.setFillColor(colors.HexColor("#52616b"))
    c.setFont("Helvetica", 8)
    for i, m in enumerate(MONTHS):
        c.drawCentredString(x + i * step + step / 2, y - 15, m)


def legend(c: canvas.Canvas, items: list[tuple[str, object]], x: float, y: float) -> None:
    c.setFont("Helvetica", 8)
    for label, color in items:
        c.setFillColor(color)
        c.rect(x, y - 6, 10, 10, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#334e68"))
        c.drawString(x + 15, y - 4, label)
        x += 135


def line(c: canvas.Canvas, x: float, y: float, w: float, h: float, data: list[float], vmin: float, vmax: float, color, width: float = 2.0) -> None:
    pts = []
    for i, value in enumerate(data):
        pts.append((x + i / (len(data) - 1) * w, y + scale(value, vmin, vmax, h)))
    c.setStrokeColor(color)
    c.setLineWidth(width)
    for a, b in zip(pts[:-1], pts[1:]):
        c.line(a[0], a[1], b[0], b[1])
    c.setFillColor(color)
    for px, py in pts:
        c.circle(px, py, 2, fill=1, stroke=0)


def chart_area_temp(data: dict[str, list[float]]) -> Path:
    path = FIG_DIR / "epw-tipo-area-rango-temperatura.pdf"
    c = new_canvas(path, "Area: rango mensual de temperatura", "Minima, media y maxima horaria del EPW")
    x, y, w, h = 70, 80, 585, 265
    axis(c, x, y, w, h, "Temperatura (C)")
    ymin, ymax = 14, 34
    step = w / 11
    top = [(x + i * step, y + scale(v, ymin, ymax, h)) for i, v in enumerate(data["temp_max"])]
    bottom = [(x + i * step, y + scale(v, ymin, ymax, h)) for i, v in enumerate(data["temp_min"])]
    p = c.beginPath()
    p.moveTo(*bottom[0])
    for px, py in bottom[1:]:
        p.lineTo(px, py)
    for px, py in reversed(top):
        p.lineTo(px, py)
    p.close()
    c.setFillColor(colors.Color(0.93, 0.35, 0.20, alpha=0.28))
    c.drawPath(p, fill=1, stroke=0)
    line(c, x, y, w, h, data["temp_mean"], ymin, ymax, colors.HexColor("#d95f02"), 2.5)
    for value in range(14, 35, 4):
        py = y + scale(value, ymin, ymax, h)
        c.setStrokeColor(colors.HexColor("#e6eaed"))
        c.line(x, py, x + w, py)
        c.setFillColor(colors.HexColor("#52616b"))
        c.setFont("Helvetica", 7)
        c.drawRightString(x - 6, py - 2, str(value))
    month_labels(c, x, y, w)
    legend(c, [("Rango min-max", colors.HexColor("#ef6c45")), ("Temperatura media", colors.HexColor("#d95f02"))], 70, 358)
    c.showPage()
    c.save()
    return path


def chart_bars_wind(data: dict[str, list[float]]) -> Path:
    path = FIG_DIR / "epw-tipo-barras-viento-mensual.pdf"
    c = new_canvas(path, "Barras: velocidad media del viento", "Promedio mensual en m/s")
    x, y, w, h = 110, 65, 500, 290
    axis(c, x, y, w, h, "Mes")
    maxv = max(data["wind"]) * 1.15
    step = h / 12
    c.setFillColor(colors.HexColor("#5aa9a6"))
    for i, value in enumerate(data["wind"]):
        yy = y + i * step + step * 0.18
        bw = scale(value, 0, maxv, w)
        c.rect(x, yy, bw, step * 0.62, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#334e68"))
        c.setFont("Helvetica", 8)
        c.drawRightString(x - 8, yy + 4, MONTHS[i])
        c.drawString(x + bw + 4, yy + 4, f"{value:.2f}")
        c.setFillColor(colors.HexColor("#5aa9a6"))
    c.showPage()
    c.save()
    return path


def chart_columns_3d(data: dict[str, list[float]]) -> Path:
    path = FIG_DIR / "epw-tipo-columnas-3d-radiacion.pdf"
    c = new_canvas(path, "Columnas 3D: radiacion global horizontal", "GHI mensual acumulada")
    x, y, w, h = 70, 80, 585, 265
    axis(c, x, y, w, h, "kWh/m2 mes")
    ymax = max(data["ghi"]) * 1.12
    step = w / 12
    bw = step * 0.55
    depth = 8
    for i, value in enumerate(data["ghi"]):
        bx = x + i * step + (step - bw) / 2
        bh = scale(value, 0, ymax, h)
        c.setFillColor(colors.HexColor("#f6c343"))
        c.rect(bx, y, bw, bh, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#d99d00"))
        p = c.beginPath()
        p.moveTo(bx + bw, y)
        p.lineTo(bx + bw + depth, y + depth)
        p.lineTo(bx + bw + depth, y + bh + depth)
        p.lineTo(bx + bw, y + bh)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#ffe082"))
        p = c.beginPath()
        p.moveTo(bx, y + bh)
        p.lineTo(bx + depth, y + bh + depth)
        p.lineTo(bx + bw + depth, y + bh + depth)
        p.lineTo(bx + bw, y + bh)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
    month_labels(c, x, y, w)
    c.showPage()
    c.save()
    return path


def chart_donut_temp(rows: list[dict[str, float | str]]) -> Path:
    path = FIG_DIR / "epw-tipo-anillos-rangos-temperatura.pdf"
    c = new_canvas(path, "Anillos: horas por rango de temperatura", "Distribucion anual de temperatura exterior")
    bins = [("<22 C", 0), ("22-24 C", 0), ("24-26 C", 0), ("26-28 C", 0), (">28 C", 0)]
    for temp in values(rows, "dry_bulb"):
        idx = 0 if temp < 22 else 1 if temp < 24 else 2 if temp < 26 else 3 if temp < 28 else 4
        label, count = bins[idx]
        bins[idx] = (label, count + 1)
    total = sum(count for _, count in bins)
    cx, cy, radius = 230, 215, 105
    palette = [colors.HexColor("#4c78a8"), colors.HexColor("#72b7b2"), colors.HexColor("#f2cf5b"), colors.HexColor("#f58518"), colors.HexColor("#d95f02")]
    start = 90
    for (label, count), color in zip(bins, palette):
        extent = 360 * count / total
        c.setFillColor(color)
        c.wedge(cx - radius, cy - radius, cx + radius, cy + radius, start, start - extent, fill=1, stroke=0)
        start -= extent
    c.setFillColor(colors.white)
    c.circle(cx, cy, 54, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#17212b"))
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(cx, cy + 5, "8760 h")
    c.setFont("Helvetica", 8)
    c.drawCentredString(cx, cy - 10, "EPW")
    y = 295
    for (label, count), color in zip(bins, palette):
        c.setFillColor(color)
        c.rect(410, y - 6, 12, 12, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#334e68"))
        c.setFont("Helvetica", 9)
        c.drawString(430, y - 4, f"{label}: {count} h ({count / total * 100:.1f}%)")
        y -= 26
    c.showPage()
    c.save()
    return path


def chart_radar(data: dict[str, list[float]]) -> Path:
    path = FIG_DIR / "epw-tipo-radar-indicadores-climaticos.pdf"
    c = new_canvas(path, "Radar: perfil climatico anual", "Indicadores normalizados del EPW")
    metrics = [
        ("Temp.", mean(data["temp_mean"]), 18, 30),
        ("HR", mean(data["rh"]), 60, 90),
        ("Radiacion", sum(data["ghi"]), 1500, 2400),
        ("Viento", mean(data["wind"]), 0, 7),
        ("Cielo", mean(data["sky"]), 0, 10),
        ("Precip.", sum(data["precip"]), 0, 200),
    ]
    vals_norm = [max(0, min(1, (value - low) / (high - low))) for _, value, low, high in metrics]
    cx, cy, r = 350, 210, 130
    for ring in range(1, 6):
        rr = r * ring / 5
        pts = []
        for i in range(len(metrics)):
            angle = math.radians(90 - i * 360 / len(metrics))
            pts.append((cx + math.cos(angle) * rr, cy + math.sin(angle) * rr))
        p = c.beginPath()
        p.moveTo(*pts[0])
        for point in pts[1:]:
            p.lineTo(*point)
        p.close()
        c.setStrokeColor(colors.HexColor("#d5dce2"))
        c.drawPath(p, fill=0, stroke=1)
    pts = []
    for i, val in enumerate(vals_norm):
        angle = math.radians(90 - i * 360 / len(metrics))
        pts.append((cx + math.cos(angle) * r * val, cy + math.sin(angle) * r * val))
        c.setStrokeColor(colors.HexColor("#c8d0d7"))
        c.line(cx, cy, cx + math.cos(angle) * r, cy + math.sin(angle) * r)
        c.setFillColor(colors.HexColor("#334e68"))
        c.setFont("Helvetica", 9)
        c.drawCentredString(cx + math.cos(angle) * (r + 26), cy + math.sin(angle) * (r + 20), metrics[i][0])
    p = c.beginPath()
    p.moveTo(*pts[0])
    for point in pts[1:]:
        p.lineTo(*point)
    p.close()
    c.setFillColor(colors.Color(0.12, 0.47, 0.71, alpha=0.25))
    c.setStrokeColor(colors.HexColor("#1f78b4"))
    c.setLineWidth(2)
    c.drawPath(p, fill=1, stroke=1)
    c.showPage()
    c.save()
    return path


def chart_scatter(rows: list[dict[str, float | str]]) -> Path:
    path = FIG_DIR / "epw-tipo-xy-temperatura-humedad.pdf"
    c = new_canvas(path, "XY dispersion: temperatura y humedad", "Muestra horaria cada 6 registros")
    x, y, w, h = 70, 80, 585, 265
    axis(c, x, y, w, h, "Humedad relativa (%)")
    temps = values(rows, "dry_bulb")
    ymin, ymax = 55, 100
    xmin, xmax = math.floor(min(temps)), math.ceil(max(temps))
    c.setFillColor(colors.HexColor("#6a51a3"))
    for row in rows[::6]:
        temp = float(row["dry_bulb"])
        rh = float(row["rh"])
        if not ok(temp, "dry_bulb") or not ok(rh, "rh"):
            continue
        px = x + scale(temp, xmin, xmax, w)
        py = y + scale(rh, ymin, ymax, h)
        c.circle(px, py, 1.4, fill=1, stroke=0)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#52616b"))
    for value in range(int(xmin), int(xmax) + 1, 3):
        px = x + scale(value, xmin, xmax, w)
        c.drawCentredString(px, y - 15, str(value))
    c.drawCentredString(x + w / 2, y - 34, "Temperatura exterior (C)")
    for value in range(60, 101, 10):
        py = y + scale(value, ymin, ymax, h)
        c.drawRightString(x - 6, py - 2, str(value))
    c.showPage()
    c.save()
    return path


def chart_combined(data: dict[str, list[float]]) -> Path:
    path = FIG_DIR / "epw-tipo-combinado-radiacion-temperatura.pdf"
    c = new_canvas(path, "Combinado: radiacion y temperatura", "Columnas GHI mensual y linea de temperatura media")
    x, y, w, h = 70, 80, 585, 265
    axis(c, x, y, w, h, "GHI (kWh/m2 mes)")
    ymax = max(data["ghi"]) * 1.15
    step = w / 12
    bw = step * 0.6
    c.setFillColor(colors.HexColor("#f6c343"))
    for i, value in enumerate(data["ghi"]):
        c.rect(x + i * step + (step - bw) / 2, y, bw, scale(value, 0, ymax, h), fill=1, stroke=0)
    line(c, x, y, w, h, data["temp_mean"], 20, 30, colors.HexColor("#d95f02"), 2.5)
    month_labels(c, x, y, w)
    legend(c, [("GHI mensual", colors.HexColor("#f6c343")), ("Temperatura media", colors.HexColor("#d95f02"))], 70, 358)
    c.showPage()
    c.save()
    return path


def chart_surface_3d(grid: list[list[float]]) -> Path:
    path = FIG_DIR / "epw-tipo-superficie-3d-temperatura.pdf"
    c = new_canvas(path, "Superficie 3D: temperatura por mes y hora", "Promedio horario mensual de temperatura exterior")
    ox, oy = 130, 105
    dx, dy = 30, 10
    zscale = 10
    tmin = min(min(row) for row in grid)
    tmax = max(max(row) for row in grid)
    for month in reversed(range(12)):
        for hour in range(0, 24, 2):
            temp = grid[month][hour]
            x = ox + hour * dx / 2 + month * 10
            y = oy + month * dy + (temp - tmin) * zscale
            ratio = (temp - tmin) / (tmax - tmin)
            col = colors.Color(0.25 + 0.65 * ratio, 0.45 - 0.20 * ratio, 0.70 - 0.55 * ratio)
            p = c.beginPath()
            p.moveTo(x, y)
            p.lineTo(x + dx, y + 7)
            p.lineTo(x + dx + 10, y + 7 + dy)
            p.lineTo(x + 10, y + dy)
            p.close()
            c.setFillColor(col)
            c.setStrokeColor(colors.HexColor("#ffffff"))
            c.drawPath(p, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#52616b"))
    c.setFont("Helvetica", 8)
    c.drawString(110, 62, f"Rango promedio mensual-horario: {tmin:.1f} C a {tmax:.1f} C")
    c.drawString(110, 48, "Eje horizontal: hora del dia; profundidad: meses.")
    c.showPage()
    c.save()
    return path


def append_summary(figures: list[Path]) -> None:
    text = SUMMARY.read_text(encoding="utf-8") if SUMMARY.exists() else "# Graficos EPW San Cristobal\n"
    lines = [
        "",
        "## Figuras complementarias por tipo de grafico",
        "",
    ]
    for figure in figures:
        lines.append(f"- `figuras/{figure.name}`")
    SUMMARY.write_text(text.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    rows = parse_epw()
    data = monthly(rows)
    grid = hourly_by_month(rows)
    figures = [
        chart_area_temp(data),
        chart_bars_wind(data),
        chart_columns_3d(data),
        chart_donut_temp(rows),
        chart_radar(data),
        chart_scatter(rows),
        chart_combined(data),
        chart_surface_3d(grid),
    ]
    append_summary(figures)
    for figure in figures:
        print(figure.relative_to(ROOT))


if __name__ == "__main__":
    main()
