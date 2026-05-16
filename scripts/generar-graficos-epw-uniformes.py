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

COLS = [
    "year", "month", "day", "hour", "minute", "flags", "dry_bulb", "dew_point",
    "rh", "pressure", "etr_horiz", "etr_direct", "horiz_ir", "ghi", "dni", "dhi",
    "global_h_illum", "direct_normal_illum", "diffuse_h_illum", "zenith_lum",
    "wind_dir", "wind_speed", "total_sky_cover", "opaque_sky_cover", "visibility",
    "ceiling_height", "present_weather_obs", "present_weather_codes",
    "precipitable_water", "aerosol_optical_depth", "snow_depth", "days_since_snow",
    "albedo", "liquid_precip_depth", "liquid_precip_quantity",
]

MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
MONTHS_SHORT = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
DIRECTIONS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]

INK = colors.HexColor("#173f3d")
MUTED = colors.HexColor("#4c6765")
GRID = colors.HexColor("#d4dddb")
MONTH_LINE = colors.HexColor("#ef4b43")
CORAL = colors.HexColor("#f47c5c")
RED = colors.HexColor("#ef4b43")
SAND = colors.HexColor("#dfc8ba")
BLUE = colors.HexColor("#7c9fd6")
LIGHT_BLUE = colors.HexColor("#b7c9e3")
CYAN = colors.HexColor("#31b7cf")
GREEN = colors.HexColor("#a8c889")
DEEP_GREEN = colors.HexColor("#174d49")
ORANGE = colors.HexColor("#ff8b3d")
GRAY = colors.HexColor("#a9adae")

PAGE = landscape((1280, 900))


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
        "wind_dir": (0, 360),
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


def daily(rows: list[dict[str, float | str]]) -> list[dict[str, float]]:
    grouped: dict[tuple[int, int], list[dict[str, float | str]]] = defaultdict(list)
    for row in rows:
        grouped[(int(float(row["month"])), int(float(row["day"])))].append(row)

    out: list[dict[str, float]] = []
    index = 0
    for month in range(1, 13):
        days = sorted(day for m, day in grouped if m == month)
        for day in days:
            subset = grouped[(month, day)]
            temps = values(subset, "dry_bulb")
            rhs = values(subset, "rh")
            winds = values(subset, "wind_speed")
            ghi = values(subset, "ghi")
            dni = values(subset, "dni")
            dhi = values(subset, "dhi")
            sky = values(subset, "total_sky_cover")
            rain = values(subset, "liquid_precip_depth")
            out.append({
                "index": index,
                "month": month,
                "temp_min": min(temps),
                "temp_mean": mean(temps),
                "temp_max": max(temps),
                "rh_min": min(rhs),
                "rh_mean": mean(rhs),
                "rh_max": max(rhs),
                "wind_min": min(winds),
                "wind_mean": mean(winds),
                "wind_max": max(winds),
                "ghi_mean": mean(ghi),
                "ghi_total": sum(ghi) / 1000,
                "dni_total": sum(dni) / 1000,
                "dhi_total": sum(dhi) / 1000,
                "sky_mean": mean(sky),
                "rain_total": sum(rain),
            })
            index += 1
    return out


def monthly_from_daily(days: list[dict[str, float]]) -> dict[str, list[float]]:
    data: dict[str, list[float]] = defaultdict(list)
    for month in range(1, 13):
        subset = [d for d in days if int(d["month"]) == month]
        data["ghi"].append(sum(d["ghi_total"] for d in subset))
        data["dni"].append(sum(d["dni_total"] for d in subset))
        data["dhi"].append(sum(d["dhi_total"] for d in subset))
    return data


def wind_direction_bins(rows: list[dict[str, float | str]]) -> list[float]:
    bins = [0.0] * 16
    total = 0
    for row in rows:
        direction = row.get("wind_dir")
        speed = row.get("wind_speed")
        if not isinstance(direction, float) or not isinstance(speed, float):
            continue
        if not valid(direction, "wind_dir") or not valid(speed, "wind_speed") or speed <= 0:
            continue
        bins[int(((direction + 11.25) % 360) // 22.5)] += 1
        total += 1
    return [(value / total * 100) if total else 0 for value in bins]


def predominant_direction(rows: list[dict[str, float | str]]) -> tuple[str, float]:
    bins = wind_direction_bins(rows)
    index = max(range(len(bins)), key=lambda i: bins[i])
    return DIRECTIONS[index], bins[index]


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


def x_for(index: float, x: float, w: float, count: int) -> float:
    return x + (index / max(1, count - 1)) * w


def setup(path: Path, title: str) -> canvas.Canvas:
    c = canvas.Canvas(str(path), pagesize=PAGE)
    c.setTitle(title)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(34, 846, "EPW TMYx 2011-2025")
    return c


def finish(c: canvas.Canvas) -> None:
    c.setFont("Helvetica", 11)
    c.setFillColor(MUTED)
    c.drawRightString(1240, 34, "Fuente: archivo EPW San Cristobal TMYx 2011-2025.")
    c.save()


def ring(c: canvas.Canvas, x: float, y: float, r: float, title: str, value: str, unit: str = "", subtitle: str = "PROMEDIO", color=CORAL) -> None:
    c.setStrokeColor(color)
    c.setLineWidth(12)
    c.circle(x, y, r, stroke=1, fill=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(x, y + r + 32, title)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(x, y + 3, value)
    if unit:
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(x, y - 26, unit)
        sub_y = y - 48
    else:
        sub_y = y - 26
    c.setFont("Helvetica", 10)
    c.drawCentredString(x, sub_y, subtitle)


def chart_axes(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    ymin: float,
    ymax: float,
    ylabel: str,
    count: int,
    y_steps: int = 6,
    month_lines: bool = True,
) -> None:
    c.setStrokeColor(GRID)
    c.setLineWidth(0.6)
    c.setFont("Helvetica", 9)
    c.setFillColor(MUTED)
    for i in range(y_steps + 1):
        value = ymin + (ymax - ymin) * i / y_steps
        yy = y + h * i / y_steps
        c.line(x, yy, x + w, yy)
        c.drawRightString(x - 10, yy - 3, f"{value:.0f}")
    c.saveState()
    c.translate(x - 58, y + h / 2)
    c.rotate(90)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(0, 0, ylabel)
    c.restoreState()

    if month_lines:
        start = 0
        for month in range(1, 13):
            month_count = 31 if month in {1, 3, 5, 7, 8, 10, 12} else 30
            if month == 2:
                month_count = 28
            xx = x_for(start, x, w, count)
            c.setStrokeColor(MONTH_LINE)
            c.setLineWidth(0.5)
            c.line(xx, y - 16, xx, y + h + 35)
            c.saveState()
            c.translate(xx - 3, y + h + 42)
            c.rotate(90)
            c.setFillColor(INK)
            c.setFont("Helvetica", 9)
            c.drawString(0, 0, MONTHS[month - 1])
            c.restoreState()
            start += month_count


def draw_series(c: canvas.Canvas, x: float, y: float, w: float, h: float, data: list[float], ymin: float, ymax: float, color, width: float = 1.6) -> None:
    count = len(data)
    points = [(x_for(i, x, w, count), y + scale(value, ymin, ymax, h)) for i, value in enumerate(data)]
    c.setStrokeColor(color)
    c.setLineWidth(width)
    for a, b in zip(points[:-1], points[1:]):
        c.line(a[0], a[1], b[0], b[1])


def draw_area_bars(c: canvas.Canvas, x: float, y: float, w: float, h: float, data: list[float], ymin: float, ymax: float, color) -> None:
    count = len(data)
    step = w / count
    c.setFillColor(color)
    for i, value in enumerate(data):
        xx = x + i * step
        yy = y + scale(value, ymin, ymax, h)
        c.rect(xx, y, max(0.4, step + 0.2), yy - y, stroke=0, fill=1)


def draw_temperature(days: list[dict[str, float]]) -> None:
    c = setup(FIG_DIR / "epw-uniforme-temperatura-mensual.pdf", "Temperatura del aire")
    temp_min = [d["temp_min"] for d in days]
    temp_mean = [d["temp_mean"] for d in days]
    temp_max = [d["temp_max"] for d in days]
    amp = [mx - mn for mx, mn in zip(temp_max, temp_min)]
    rings = [
        ("TEMPERATURA MAXIMA", f"{mean(temp_max):.2f}", "C", CORAL),
        ("TEMPERATURA MEDIA", f"{mean(temp_mean):.2f}", "C", colors.HexColor("#ff9a7d")),
        ("TEMPERATURA MINIMA", f"{mean(temp_min):.2f}", "C", SAND),
        ("MAXIMA ABSOLUTA", f"{max(temp_max):.2f}", "C", RED),
        ("MINIMA ABSOLUTA", f"{min(temp_min):.2f}", "C", LIGHT_BLUE),
        ("AMPLITUD TERMICA", f"{mean(amp):.2f}", "C", colors.HexColor("#f8bb82")),
    ]
    for i, item in enumerate(rings):
        ring(c, 112 + i * 204, 690, 58, item[0], item[1], item[2], color=item[3])
    x, y, w, h = 94, 105, 1135, 395
    ymin = math.floor(min(temp_min) - 1)
    ymax = math.ceil(max(temp_max) + 1)
    chart_axes(c, x, y, w, h, ymin, ymax, "Temperatura C", len(days))
    draw_series(c, x, y, w, h, temp_max, ymin, ymax, RED, 1.5)
    draw_series(c, x, y, w, h, temp_mean, ymin, ymax, colors.HexColor("#ffb985"), 1.5)
    draw_series(c, x, y, w, h, temp_min, ymin, ymax, LIGHT_BLUE, 1.5)
    finish(c)


def draw_humidity(days: list[dict[str, float]]) -> None:
    c = setup(FIG_DIR / "epw-uniforme-humedad-relativa.pdf", "Humedad relativa")
    rh_min = [d["rh_min"] for d in days]
    rh_mean = [d["rh_mean"] for d in days]
    rh_max = [d["rh_max"] for d in days]
    amp = [mx - mn for mx, mn in zip(rh_max, rh_min)]
    rings = [
        ("HUMEDAD MAXIMA", f"{mean(rh_max):.2f}", "%", colors.HexColor("#2d61a8")),
        ("HUMEDAD MEDIA", f"{mean(rh_mean):.2f}", "%", BLUE),
        ("HUMEDAD MINIMA", f"{mean(rh_min):.2f}", "%", LIGHT_BLUE),
        ("MAXIMA ABSOLUTA", f"{max(rh_max):.2f}", "%", colors.HexColor("#2a5aa0")),
        ("MINIMA ABSOLUTA", f"{min(rh_min):.2f}", "%", colors.HexColor("#b7c9e3")),
        ("AMPLITUD", f"{mean(amp):.2f}", "%", colors.HexColor("#d5e0f2")),
    ]
    for i, item in enumerate(rings):
        ring(c, 112 + i * 204, 690, 58, item[0], item[1], item[2], color=item[3])
    x, y, w, h = 94, 105, 1135, 395
    chart_axes(c, x, y, w, h, 0, 100, "Humedad %", len(days), y_steps=10)
    draw_series(c, x, y, w, h, rh_max, 0, 100, colors.HexColor("#3f75d7"), 1.4)
    draw_series(c, x, y, w, h, rh_mean, 0, 100, GRAY, 1.4)
    draw_series(c, x, y, w, h, rh_min, 0, 100, ORANGE, 1.4)
    finish(c)


def draw_radiation(days: list[dict[str, float]], monthly: dict[str, list[float]]) -> None:
    c = setup(FIG_DIR / "epw-uniforme-radiacion-solar.pdf", "Radiacion solar")
    daily_ghi = [d["ghi_mean"] for d in days]
    daily_energy = [d["ghi_total"] for d in days]
    rings = [
        ("RADIACION SOLAR", f"{mean(daily_ghi):.2f}", "W/m2", CORAL),
        ("RADIACION MAXIMA", f"{max(daily_ghi):.2f}", "W/m2", RED),
        ("RADIACION MINIMA", f"{min(daily_ghi):.2f}", "W/m2", SAND),
        ("ENERGIA SOLAR", f"{mean(daily_energy):.2f}", "kWh/m2", CORAL),
    ]
    for i, item in enumerate(rings):
        ring(c, 150 + i * 260, 690, 58, item[0], item[1], item[2], color=item[3])
    x, y, w, h = 94, 365, 1135, 205
    ymax = math.ceil(max(daily_ghi) / 50) * 50
    chart_axes(c, x, y, w, h, 0, ymax, "Radiacion solar W/m2", len(days), y_steps=5)
    draw_area_bars(c, x, y, w, h, daily_ghi, 0, ymax, colors.HexColor("#ff7a59"))
    x2, y2, w2, h2 = 94, 85, 640, 175
    ymax2 = math.ceil(max(daily_energy) / 2) * 2
    chart_axes(c, x2, y2, w2, h2, 0, ymax2, "Energia solar kWh/m2", len(days), y_steps=4)
    draw_area_bars(c, x2, y2, w2, h2, daily_energy, 0, ymax2, colors.HexColor("#ff8b3d"))
    x3, y3, w3, h3 = 815, 85, 360, 175
    ymax3 = max(monthly["ghi"] + monthly["dni"] + monthly["dhi"]) * 1.15
    chart_axes(c, x3, y3, w3, h3, 0, ymax3, "kWh/m2 mes", 12, y_steps=4, month_lines=False)
    step = w3 / 12
    for i in range(12):
        for j, (key, color) in enumerate([("ghi", CORAL), ("dni", RED), ("dhi", BLUE)]):
            c.setFillColor(color)
            bh = scale(monthly[key][i], 0, ymax3, h3)
            c.rect(x3 + i * step + 5 + j * 8, y3, 7, bh, stroke=0, fill=1)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawCentredString(x3 + i * step + step / 2, y3 - 16, MONTHS_SHORT[i])
    finish(c)


def draw_wind(days: list[dict[str, float]], rows: list[dict[str, float | str]]) -> None:
    c = setup(FIG_DIR / "epw-uniforme-viento-mensual.pdf", "Viento")
    wind_min = [d["wind_min"] * 3.6 for d in days]
    wind_mean = [d["wind_mean"] * 3.6 for d in days]
    wind_max = [d["wind_max"] * 3.6 for d in days]
    direction, share = predominant_direction(rows)
    rings = [
        ("VELOCIDAD VIENTO", f"{mean(wind_mean):.2f}", "Km/h", CORAL),
        ("VIENTO MAXIMO", f"{max(wind_max):.2f}", "Km/h", RED),
        ("VIENTO MINIMO", f"{min(wind_min):.2f}", "Km/h", GREEN),
        ("DIRECCION VIENTO", direction, "", DEEP_GREEN),
    ]
    for i, item in enumerate(rings):
        subtitle = "PREDOMINANTE" if i == 3 else "PROMEDIO"
        ring(c, 540 + i * 210, 690, 66, item[0], item[1], item[2], subtitle=subtitle, color=item[3])
    c.setFont("Helvetica", 10)
    c.setFillColor(MUTED)
    c.drawCentredString(1170, 612, f"{share:.1f}% de horas")
    x, y, w, h = 128, 105, 1120, 395
    ymax = math.ceil(max(wind_max) / 5) * 5
    chart_axes(c, x, y, w, h, 0, ymax, "Velocidad viento Km/h", len(days), y_steps=6)
    c.setStrokeColor(RED)
    c.setLineWidth(2.0)
    c.line(x, y + scale(max(wind_max), 0, ymax, h), x + w, y + scale(max(wind_max), 0, ymax, h))
    c.setStrokeColor(GREEN)
    c.line(x, y + scale(min(wind_min), 0, ymax, h), x + w, y + scale(min(wind_min), 0, ymax, h))
    draw_series(c, x, y, w, h, wind_mean, 0, ymax, colors.HexColor("#4b81c4"), 1.5)
    finish(c)


def draw_wind_rose(direction_data: list[float]) -> None:
    c = setup(FIG_DIR / "epw-uniforme-rosa-vientos.pdf", "Direccion predominante del viento")
    cx, cy = 640, 430
    radius = 220
    max_value = max(direction_data) or 1
    c.setStrokeColor(GRID)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    for ring_index in range(1, 5):
        c.circle(cx, cy, radius * ring_index / 4, stroke=1, fill=0)
    c.setFillColor(DEEP_GREEN)
    c.setStrokeColor(DEEP_GREEN)
    for i, value in enumerate(direction_data):
        angle = math.radians(90 - i * 22.5)
        length = radius * value / max_value
        width = math.radians(7)
        path = c.beginPath()
        path.moveTo(cx, cy)
        path.lineTo(cx + math.cos(angle - width) * length, cy + math.sin(angle - width) * length)
        path.lineTo(cx + math.cos(angle + width) * length, cy + math.sin(angle + width) * length)
        path.close()
        c.drawPath(path, stroke=1, fill=1)
    for i, label in enumerate(DIRECTIONS):
        angle = math.radians(90 - i * 22.5)
        c.setStrokeColor(GRID)
        c.line(cx, cy, cx + math.cos(angle) * radius, cy + math.sin(angle) * radius)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(cx + math.cos(angle) * (radius + 30), cy + math.sin(angle) * (radius + 30) - 4, label)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    c.drawString(106, 116, f"Anillo exterior: {max_value:.1f}% de horas.")
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
    c = setup(FIG_DIR / "epw-uniforme-mapa-horario-temperatura.pdf", "Mapa horario de temperatura exterior")
    x, y, w, h = 130, 145, 1020, 520
    low = min(min(row) for row in grid)
    high = max(max(row) for row in grid)
    cell_w = w / 24
    cell_h = h / 12
    for month, row in enumerate(grid):
        for hour, value in enumerate(row):
            c.setFillColor(temp_color(value, low, high))
            c.rect(x + hour * cell_w, y + (11 - month) * cell_h, cell_w + 0.3, cell_h + 0.3, stroke=0, fill=1)
    c.setStrokeColor(GRID)
    c.rect(x, y, w, h, stroke=1, fill=0)
    c.setFont("Helvetica", 12)
    c.setFillColor(MUTED)
    for hour in [1, 6, 12, 18, 24]:
        c.drawCentredString(x + (hour - 0.5) * cell_w, y - 24, str(hour))
    for i, month in enumerate(MONTHS_SHORT):
        c.drawRightString(x - 16, y + (11 - i + 0.36) * cell_h, month)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(INK)
    c.drawString(x, y + h + 46, "Temperatura media por mes y hora del dia")
    c.setFont("Helvetica", 11)
    c.setFillColor(MUTED)
    c.drawString(x, y + h + 25, f"Rango cromatico: {low:.1f} C a {high:.1f} C")
    finish(c)


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    rows = parse_epw()
    days = daily(rows)
    draw_temperature(days)
    draw_humidity(days)
    draw_radiation(days, monthly_from_daily(days))
    draw_wind(days, rows)
    draw_wind_rose(wind_direction_bins(rows))
    draw_temperature_heatmap(hourly_grid(rows))


if __name__ == "__main__":
    main()
