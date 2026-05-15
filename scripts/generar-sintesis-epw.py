from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
EPW = ROOT / "datos" / "ECU_GA_San.Cristobal.Intl.AP.840080_TMYx.2011-2025.epw"
OUT = ROOT / "figuras" / "epw-sintesis-climatica.pdf"

COLS = [
    "year", "month", "day", "hour", "minute", "flags", "dry_bulb", "dew_point",
    "rh", "pressure", "etr_horiz", "etr_direct", "horiz_ir", "ghi", "dni", "dhi",
    "global_h_illum", "direct_normal_illum", "diffuse_h_illum", "zenith_lum",
    "wind_dir", "wind_speed", "total_sky_cover", "opaque_sky_cover", "visibility",
    "ceiling_height", "present_weather_obs", "present_weather_codes",
    "precipitable_water", "aerosol_optical_depth", "snow_depth", "days_since_snow",
    "albedo", "liquid_precip_depth", "liquid_precip_quantity",
]

MONTHS = ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]

INK = colors.HexColor("#17212b")
MUTED = colors.HexColor("#5b6773")
GRID = colors.HexColor("#d9e0e6")
PANEL = colors.HexColor("#f8fafc")
TEMP = colors.HexColor("#d95f02")
RH = colors.HexColor("#1f78b4")
GHI = colors.HexColor("#f59f00")
DNI = colors.HexColor("#ef476f")
DHI = colors.HexColor("#3a86ff")
WIND = colors.HexColor("#2a9d8f")
SKY = colors.HexColor("#6c757d")
PRECIP = colors.HexColor("#4dabf7")


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
        "total_sky_cover": (0, 10),
        "liquid_precip_depth": (0, 500),
    }
    low, high = ranges[field]
    return low <= value <= high


def values(rows: list[dict[str, float | str]], field: str) -> list[float]:
    return [float(r[field]) for r in rows if isinstance(r[field], float) and ok(float(r[field]), field)]


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


def panel(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str) -> None:
    c.setFillColor(PANEL)
    c.setStrokeColor(colors.HexColor("#c9d3dc"))
    c.setLineWidth(0.6)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x + 10, y + h - 16, title)


def axes(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.setStrokeColor(GRID)
    c.setLineWidth(0.4)
    for i in range(1, 4):
        yy = y + h * i / 4
        c.line(x, yy, x + w, yy)
    c.setStrokeColor(colors.HexColor("#8d99a6"))
    c.setLineWidth(0.6)
    c.line(x, y, x + w, y)
    c.line(x, y, x, y + h)


def month_labels(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    c.setFont("Helvetica", 6.5)
    c.setFillColor(MUTED)
    step = w / 12
    for i, month in enumerate(MONTHS):
        c.drawCentredString(x + i * step + step / 2, y - 10, month)


def legend(c: canvas.Canvas, items: list[tuple[str, object]], x: float, y: float) -> None:
    c.setFont("Helvetica", 6.5)
    for label, color in items:
        c.setFillColor(color)
        c.rect(x, y - 5, 8, 8, fill=1, stroke=0)
        c.setFillColor(MUTED)
        c.drawString(x + 11, y - 3, label)
        x += 74


def draw_line(c: canvas.Canvas, x: float, y: float, w: float, h: float, data: list[float], low: float, high: float, color) -> None:
    points = [
        (x + i / (len(data) - 1) * w, y + scale(value, low, high, h))
        for i, value in enumerate(data)
    ]
    c.setStrokeColor(color)
    c.setLineWidth(1.6)
    for a, b in zip(points[:-1], points[1:]):
        c.line(a[0], a[1], b[0], b[1])
    c.setFillColor(color)
    for px, py in points:
        c.circle(px, py, 1.5, fill=1, stroke=0)


def draw_bars(c: canvas.Canvas, x: float, y: float, w: float, h: float, data: list[float], high: float, color, offset: float = 0, width_factor: float = 0.65) -> None:
    step = w / len(data)
    bar_w = step * width_factor
    c.setFillColor(color)
    for i, value in enumerate(data):
        bh = scale(value, 0, high, h)
        c.rect(x + i * step + (step - bar_w) / 2 + offset, y, bar_w, bh, fill=1, stroke=0)


def draw_dashboard(rows: list[dict[str, float | str]]) -> None:
    data = monthly(rows)
    grid = hourly_grid(rows)
    c = canvas.Canvas(str(OUT), pagesize=landscape((760, 540)))
    c.setTitle("Síntesis climática EPW San Cristóbal")

    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 17)
    c.drawString(34, 508, "Síntesis climática EPW - San Cristóbal")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(MUTED)
    c.drawString(34, 493, "TMYx 2011-2025 | Variables principales para simulación energética del caso base")

    # Temperatura y humedad.
    panel(c, 34, 305, 330, 165, "a) Temperatura y humedad relativa mensual")
    x, y, w, h = 62, 337, 270, 92
    axes(c, x, y, w, h)
    draw_line(c, x, y, w, h, data["temp_mean"], 20, 30, TEMP)
    draw_line(c, x, y, w, h, data["rh"], 70, 90, RH)
    month_labels(c, x, y, w)
    legend(c, [("Temp. media (°C)", TEMP), ("HR media (%)", RH)], x, 316)

    # Radiación.
    panel(c, 396, 305, 330, 165, "b) Radiación solar mensual")
    x, y, w, h = 424, 337, 270, 92
    axes(c, x, y, w, h)
    high_rad = max(data["ghi"] + data["dni"] + data["dhi"]) * 1.15
    draw_bars(c, x, y, w, h, data["ghi"], high_rad, GHI, offset=-5, width_factor=0.22)
    draw_bars(c, x, y, w, h, data["dni"], high_rad, DNI, offset=0, width_factor=0.22)
    draw_bars(c, x, y, w, h, data["dhi"], high_rad, DHI, offset=5, width_factor=0.22)
    month_labels(c, x, y, w)
    legend(c, [("GHI", GHI), ("DNI", DNI), ("DHI", DHI)], x, 316)

    # Viento, cielo y precipitación.
    panel(c, 34, 115, 330, 165, "c) Viento, cobertura de cielo y precipitación")
    x, y, w, h = 62, 147, 270, 92
    axes(c, x, y, w, h)
    draw_line(c, x, y, w, h, data["wind"], 0, 8, WIND)
    draw_line(c, x, y, w, h, data["sky"], 0, 10, SKY)
    draw_bars(c, x, y, w, h, data["precip"], max(data["precip"]) * 1.2 or 1, PRECIP, width_factor=0.35)
    month_labels(c, x, y, w)
    legend(c, [("Viento (m/s)", WIND), ("Cielo (0-10)", SKY), ("Precip.", PRECIP)], x, 126)

    # Mapa horario de temperatura.
    panel(c, 396, 115, 330, 165, "d) Temperatura exterior por mes y hora")
    x, y, w, h = 424, 145, 270, 100
    cell_w = w / 24
    cell_h = h / 12
    all_temps = [value for row in grid for value in row]
    low, high = min(all_temps), max(all_temps)
    for m, row in enumerate(grid):
        for hour, value in enumerate(row):
            ratio = scale(value, low, high, 1)
            color = colors.Color(0.1 + ratio * 0.85, 0.32 + ratio * 0.38, 0.72 - ratio * 0.55)
            c.setFillColor(color)
            c.rect(x + hour * cell_w, y + (11 - m) * cell_h, cell_w + 0.2, cell_h + 0.2, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#8d99a6"))
    c.rect(x, y, w, h, fill=0, stroke=1)
    c.setFont("Helvetica", 6.5)
    c.setFillColor(MUTED)
    for i, month in enumerate(MONTHS):
        c.drawRightString(x - 4, y + (11 - i) * cell_h + 2, month)
    for hour in [0, 6, 12, 18, 24]:
        c.drawCentredString(x + hour / 24 * w, y - 10, str(hour))
    c.drawRightString(x + w, y - 22, f"{low:.1f} a {high:.1f} °C")

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawString(34, 42, "Lectura integrada: clima cálido-húmedo, alta humedad relativa, radiación relevante y vientos persistentes; variables base para el modelo energético.")
    c.save()


def main() -> None:
    draw_dashboard(parse_epw())


if __name__ == "__main__":
    main()
