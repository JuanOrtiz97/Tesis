from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
EPW = ROOT / "datos" / "ECU_GA_San.Cristobal.Intl.AP.840080_TMYx.2011-2025.epw"
FIG_DIR = ROOT / "figuras"

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

INK = colors.HexColor("#17212b")
MUTED = colors.HexColor("#5b6773")
GRID = colors.HexColor("#d9e0e6")
AXIS = colors.HexColor("#8d99a6")
TEMP = colors.HexColor("#d95f02")
TEMP_MIN = colors.HexColor("#74a9cf")
TEMP_MAX = colors.HexColor("#ef476f")
RH = colors.HexColor("#1f78b4")
GHI = colors.HexColor("#f59f00")
DNI = colors.HexColor("#ef476f")
DHI = colors.HexColor("#3a86ff")
WIND = colors.HexColor("#2a9d8f")
SKY = colors.HexColor("#6c757d")
PRECIP = colors.HexColor("#4dabf7")


def parse_epw() -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for raw in csv.reader(EPW.read_text(encoding="latin1").splitlines()[8:]):
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


def valid(value: float, field: str) -> bool:
    ranges = {
        "dry_bulb": (-70, 70),
        "rh": (0, 100),
        "ghi": (0, 1500),
        "dni": (0, 1500),
        "dhi": (0, 1500),
        "wind_speed": (0, 60),
        "total_sky_cover": (0, 10),
        "liquid_precip_depth": (0, 500),
    }
    low, high = ranges[field]
    return low <= value <= high


def values(rows: list[dict[str, float | str]], field: str) -> list[float]:
    return [float(r[field]) for r in rows if isinstance(r[field], float) and valid(float(r[field]), field)]


def mean(items: list[float]) -> float:
    return sum(items) / len(items) if items else 0.0


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


def hourly_grid(rows: list[dict[str, float | str]]) -> list[list[float]]:
    grid = []
    for month in range(1, 13):
        month_values = []
        for hour in range(1, 25):
            subset = [
                r for r in rows
                if int(float(r["month"])) == month and int(float(r["hour"])) == hour
            ]
            month_values.append(mean(values(subset, "dry_bulb")))
        grid.append(month_values)
    return grid


def scale(value: float, low: float, high: float, size: float) -> float:
    return 0 if high == low else (value - low) / (high - low) * size


def setup(path: Path, title: str, subtitle: str) -> canvas.Canvas:
    c = canvas.Canvas(str(path), pagesize=landscape((720, 430)))
    c.setTitle(title)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 17)
    c.drawString(44, 392, title)
    c.setFont("Helvetica", 9)
    c.setFillColor(MUTED)
    c.drawString(44, 376, subtitle)
    return c


def finish(c: canvas.Canvas) -> None:
    c.setFont("Helvetica", 7)
    c.setFillColor(MUTED)
    c.drawRightString(676, 28, "Fuente: archivo EPW San Cristobal TMYx 2011-2025.")
    c.save()


def chart_area(c: canvas.Canvas) -> tuple[float, float, float, float]:
    x, y, w, h = 78, 82, 570, 260
    c.setStrokeColor(GRID)
    c.setLineWidth(0.45)
    for i in range(1, 5):
        yy = y + h * i / 5
        c.line(x, yy, x + w, yy)
    c.setStrokeColor(AXIS)
    c.setLineWidth(0.7)
    c.line(x, y, x + w, y)
    c.line(x, y, x, y + h)
    return x, y, w, h


def month_labels(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    step = w / 12
    for i, month in enumerate(MONTHS):
        c.drawCentredString(x + i * step + step / 2, y - 16, month)


def y_labels(c: canvas.Canvas, x: float, y: float, h: float, low: float, high: float, suffix: str = "") -> None:
    c.setFont("Helvetica", 7)
    c.setFillColor(MUTED)
    for i in range(6):
        value = low + (high - low) * i / 5
        yy = y + h * i / 5
        c.drawRightString(x - 8, yy - 2, f"{value:.0f}{suffix}")


def legend(c: canvas.Canvas, items: list[tuple[str, object]], x: float, y: float) -> None:
    c.setFont("Helvetica", 8)
    for label, color in items:
        c.setFillColor(color)
        c.rect(x, y - 6, 10, 10, fill=1, stroke=0)
        c.setFillColor(MUTED)
        c.drawString(x + 15, y - 4, label)
        x += 128


def draw_line(c: canvas.Canvas, x: float, y: float, w: float, h: float, data: list[float], low: float, high: float, color) -> None:
    points = [
        (x + i / (len(data) - 1) * w, y + scale(value, low, high, h))
        for i, value in enumerate(data)
    ]
    c.setStrokeColor(color)
    c.setLineWidth(2.0)
    for a, b in zip(points[:-1], points[1:]):
        c.line(a[0], a[1], b[0], b[1])
    c.setFillColor(color)
    for px, py in points:
        c.circle(px, py, 2.2, fill=1, stroke=0)


def draw_grouped_bars(c: canvas.Canvas, x: float, y: float, w: float, h: float, groups: list[tuple[list[float], object]], high: float) -> None:
    step = w / 12
    bar_w = step * 0.2
    offsets = [-bar_w, 0, bar_w]
    for (data, color), offset in zip(groups, offsets):
        c.setFillColor(color)
        for i, value in enumerate(data):
            bh = scale(value, 0, high, h)
            c.rect(x + i * step + step / 2 + offset - bar_w / 2, y, bar_w, bh, fill=1, stroke=0)


def draw_bars(c: canvas.Canvas, x: float, y: float, w: float, h: float, data: list[float], high: float, color) -> None:
    step = w / 12
    bar_w = step * 0.54
    c.setFillColor(color)
    for i, value in enumerate(data):
        bh = scale(value, 0, high, h)
        c.rect(x + i * step + (step - bar_w) / 2, y, bar_w, bh, fill=1, stroke=0)


def draw_temp_humidity(data: dict[str, list[float]]) -> None:
    c = setup(
        FIG_DIR / "epw-uniforme-temperatura-humedad.pdf",
        "Temperatura y humedad relativa mensual",
        "Promedios mensuales del archivo EPW de San Cristobal.",
    )
    x, y, w, h = chart_area(c)
    y_labels(c, x, y, h, 20, 30, " C")
    month_labels(c, x, y, w)
    draw_line(c, x, y, w, h, data["temp_min"], 20, 30, TEMP_MIN)
    draw_line(c, x, y, w, h, data["temp_mean"], 20, 30, TEMP)
    draw_line(c, x, y, w, h, data["temp_max"], 20, 30, TEMP_MAX)
    draw_line(c, x, y, w, h, data["rh"], 70, 90, RH)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7)
    c.drawString(654, 336, "HR: 70-90 %")
    legend(c, [("Temp. min.", TEMP_MIN), ("Temp. media", TEMP), ("Temp. max.", TEMP_MAX), ("HR media", RH)], 82, 60)
    finish(c)


def draw_radiation(data: dict[str, list[float]]) -> None:
    c = setup(
        FIG_DIR / "epw-uniforme-radiacion-solar.pdf",
        "Radiacion solar mensual",
        "Energia solar acumulada mensual: GHI, DNI y DHI.",
    )
    x, y, w, h = chart_area(c)
    high = max(data["ghi"] + data["dni"] + data["dhi"]) * 1.15
    y_labels(c, x, y, h, 0, high, " kWh/m2")
    month_labels(c, x, y, w)
    draw_grouped_bars(c, x, y, w, h, [(data["ghi"], GHI), (data["dni"], DNI), (data["dhi"], DHI)], high)
    legend(c, [("GHI", GHI), ("DNI", DNI), ("DHI", DHI)], 82, 60)
    finish(c)


def draw_wind_sky_precip(data: dict[str, list[float]]) -> None:
    c = setup(
        FIG_DIR / "epw-uniforme-viento-cielo-precipitacion.pdf",
        "Viento, cielo y precipitacion mensual",
        "Velocidad media del viento, cobertura de cielo y lluvia registrada en el EPW.",
    )
    x, y, w, h = chart_area(c)
    y_labels(c, x, y, h, 0, 10)
    month_labels(c, x, y, w)
    draw_bars(c, x, y, w, h, data["precip"], max(data["precip"]) * 1.25, PRECIP)
    draw_line(c, x, y, w, h, data["wind"], 0, 10, WIND)
    draw_line(c, x, y, w, h, data["sky"], 0, 10, SKY)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7)
    c.drawString(654, 336, "Lluvia: escala relativa")
    legend(c, [("Viento (m/s)", WIND), ("Cielo (0-10)", SKY), ("Precipitacion", PRECIP)], 82, 60)
    finish(c)


def temp_color(value: float, low: float, high: float) -> colors.Color:
    ratio = max(0, min(1, (value - low) / (high - low)))
    stops = [
        (0.00, colors.HexColor("#2b6cb0")),
        (0.35, colors.HexColor("#2a9d8f")),
        (0.62, colors.HexColor("#f4d35e")),
        (1.00, colors.HexColor("#d95f02")),
    ]
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        if p0 <= ratio <= p1:
            t = (ratio - p0) / (p1 - p0)
            return colors.Color(
                c0.red + (c1.red - c0.red) * t,
                c0.green + (c1.green - c0.green) * t,
                c0.blue + (c1.blue - c0.blue) * t,
            )
    return stops[-1][1]


def draw_temperature_heatmap(grid: list[list[float]]) -> None:
    c = setup(
        FIG_DIR / "epw-uniforme-mapa-horario-temperatura.pdf",
        "Mapa horario de temperatura exterior",
        "Temperatura media por mes y hora del dia en el ano meteorologico tipico.",
    )
    x, y, w, h = chart_area(c)
    cell_w = w / 24
    cell_h = h / 12
    low = min(min(row) for row in grid)
    high = max(max(row) for row in grid)
    for month, row in enumerate(grid):
        for hour, value in enumerate(row):
            c.setFillColor(temp_color(value, low, high))
            c.rect(x + hour * cell_w, y + (11 - month) * cell_h, cell_w + 0.2, cell_h + 0.2, stroke=0, fill=1)
    c.setStrokeColor(AXIS)
    c.rect(x, y, w, h, stroke=1, fill=0)
    c.setFont("Helvetica", 7)
    c.setFillColor(MUTED)
    for hour in [1, 6, 12, 18, 24]:
        c.drawCentredString(x + (hour - 0.5) * cell_w, y - 15, str(hour))
    for i, month in enumerate(MONTHS):
        c.drawRightString(x - 8, y + (11 - i + 0.35) * cell_h, month)
    c.drawString(x + w - 92, 60, f"{low:.1f} C")
    c.drawRightString(x + w, 60, f"{high:.1f} C")
    for i in range(80):
        c.setFillColor(temp_color(low + (high - low) * i / 79, low, high))
        c.rect(x + w - 80 + i, 68, 1.1, 8, stroke=0, fill=1)
    finish(c)


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    rows = parse_epw()
    data = monthly(rows)
    draw_temp_humidity(data)
    draw_radiation(data)
    draw_wind_sky_precip(data)
    draw_temperature_heatmap(hourly_grid(rows))


if __name__ == "__main__":
    main()
