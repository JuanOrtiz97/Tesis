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
OUT_MD = ROOT / "insumos" / "graficos-epw-san-cristobal.md"

COLS = [
    "year",
    "month",
    "day",
    "hour",
    "minute",
    "flags",
    "dry_bulb",
    "dew_point",
    "rh",
    "pressure",
    "etr_horiz",
    "etr_direct",
    "horiz_ir",
    "ghi",
    "dni",
    "dhi",
    "global_h_illum",
    "direct_normal_illum",
    "diffuse_h_illum",
    "zenith_lum",
    "wind_dir",
    "wind_speed",
    "total_sky_cover",
    "opaque_sky_cover",
    "visibility",
    "ceiling_height",
    "present_weather_obs",
    "present_weather_codes",
    "precipitable_water",
    "aerosol_optical_depth",
    "snow_depth",
    "days_since_snow",
    "albedo",
    "liquid_precip_depth",
    "liquid_precip_quantity",
]

MONTHS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
DIRECTIONS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]


def parse_epw() -> tuple[list[str], list[dict[str, float | str]]]:
    lines = EPW.read_text(encoding="latin1").splitlines()
    rows: list[dict[str, float | str]] = []
    for raw in csv.reader(lines[8:]):
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
    return lines[:8], rows


def valid(value: float, field: str) -> bool:
    ranges = {
        "dry_bulb": (-70, 70),
        "dew_point": (-70, 70),
        "rh": (0, 100),
        "pressure": (50000, 120000),
        "ghi": (0, 1500),
        "dni": (0, 1500),
        "dhi": (0, 1500),
        "horiz_ir": (0, 1000),
        "wind_speed": (0, 60),
        "wind_dir": (0, 360),
        "total_sky_cover": (0, 10),
        "liquid_precip_depth": (0, 500),
    }
    low, high = ranges[field]
    return low <= value <= high


def vals(rows: list[dict[str, float | str]], field: str) -> list[float]:
    return [float(r[field]) for r in rows if isinstance(r[field], float) and valid(float(r[field]), field)]


def avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def monthly(rows: list[dict[str, float | str]]) -> dict[str, list[float]]:
    out: dict[str, list[float]] = defaultdict(list)
    for month in range(1, 13):
        month_rows = [r for r in rows if int(float(r["month"])) == month]
        out["temp"].append(avg(vals(month_rows, "dry_bulb")))
        out["rh"].append(avg(vals(month_rows, "rh")))
        out["ghi"].append(sum(vals(month_rows, "ghi")) / 1000)
        out["dni"].append(sum(vals(month_rows, "dni")) / 1000)
        out["dhi"].append(sum(vals(month_rows, "dhi")) / 1000)
        out["wind"].append(avg(vals(month_rows, "wind_speed")))
        out["sky"].append(avg(vals(month_rows, "total_sky_cover")))
        out["precip"].append(sum(vals(month_rows, "liquid_precip_depth")))
    return out


def hourly(rows: list[dict[str, float | str]]) -> dict[str, list[float]]:
    out: dict[str, list[float]] = defaultdict(list)
    for hour in range(1, 25):
        hour_rows = [r for r in rows if int(float(r["hour"])) == hour]
        out["temp"].append(avg(vals(hour_rows, "dry_bulb")))
        out["ghi"].append(avg(vals(hour_rows, "ghi")))
    return out


def setup_canvas(path: Path, title: str, subtitle: str = "") -> canvas.Canvas:
    page = landscape((720, 430))
    c = canvas.Canvas(str(path), pagesize=page)
    c.setTitle(title)
    c.setFillColor(colors.HexColor("#1f2933"))
    c.setFont("Helvetica-Bold", 17)
    c.drawString(44, 392, title)
    if subtitle:
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#52616b"))
        c.drawString(44, 376, subtitle)
    return c


def draw_axes(c: canvas.Canvas, x: float, y: float, w: float, h: float, y_label: str = "") -> None:
    c.setStrokeColor(colors.HexColor("#98a1a8"))
    c.setLineWidth(0.7)
    c.line(x, y, x + w, y)
    c.line(x, y, x, y + h)
    if y_label:
        c.saveState()
        c.translate(x - 34, y + h / 2)
        c.rotate(90)
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#52616b"))
        c.drawCentredString(0, 0, y_label)
        c.restoreState()


def scale(value: float, minimum: float, maximum: float, length: float) -> float:
    if maximum == minimum:
        return 0
    return (value - minimum) / (maximum - minimum) * length


def line_plot(c: canvas.Canvas, x: float, y: float, w: float, h: float, data: list[float], ymin: float, ymax: float, color) -> None:
    points = []
    for i, value in enumerate(data):
        px = x + (i / (len(data) - 1)) * w
        py = y + scale(value, ymin, ymax, h)
        points.append((px, py))
    c.setStrokeColor(color)
    c.setLineWidth(2.0)
    for p1, p2 in zip(points[:-1], points[1:]):
        c.line(p1[0], p1[1], p2[0], p2[1])
    c.setFillColor(color)
    for px, py in points:
        c.circle(px, py, 2.2, fill=1, stroke=0)


def bar_plot(c: canvas.Canvas, x: float, y: float, w: float, h: float, data: list[float], ymax: float, color) -> None:
    step = w / len(data)
    bar_w = step * 0.66
    c.setFillColor(color)
    for i, value in enumerate(data):
        bh = scale(value, 0, ymax, h)
        c.rect(x + i * step + (step - bar_w) / 2, y, bar_w, bh, stroke=0, fill=1)


def draw_month_labels(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    step = w / 12
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#52616b"))
    for i, month in enumerate(MONTHS):
        c.drawCentredString(x + i * step + step / 2, y - 15, month)


def legend(c: canvas.Canvas, items: list[tuple[str, object]], x: float, y: float) -> None:
    c.setFont("Helvetica", 8)
    for label, color in items:
        c.setFillColor(color)
        c.rect(x, y - 6, 10, 10, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#334e68"))
        c.drawString(x + 15, y - 4, label)
        x += 120


def chart_temp_humidity(data: dict[str, list[float]]) -> Path:
    path = FIG_DIR / "epw-temperatura-humedad-mensual.pdf"
    c = setup_canvas(path, "Temperatura y humedad relativa mensual", "EPW San Cristobal TMYx 2011-2025")
    x, y, w, h = 70, 80, 585, 265
    draw_axes(c, x, y, w, h, "Temperatura (C)")
    for value in range(20, 31, 2):
        py = y + scale(value, 20, 30, h)
        c.setStrokeColor(colors.HexColor("#e6eaed"))
        c.line(x, py, x + w, py)
        c.setFillColor(colors.HexColor("#52616b"))
        c.setFont("Helvetica", 7)
        c.drawRightString(x - 6, py - 2, str(value))
    line_plot(c, x, y, w, h, data["temp"], 20, 30, colors.HexColor("#d95f02"))
    # RH scaled on the same visual field, labeled on right.
    line_plot(c, x, y, w, h, data["rh"], 70, 90, colors.HexColor("#1f78b4"))
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#52616b"))
    for value in range(70, 91, 5):
        py = y + scale(value, 70, 90, h)
        c.drawString(x + w + 6, py - 2, f"{value}%")
    draw_month_labels(c, x, y, w)
    legend(c, [("Temperatura media", colors.HexColor("#d95f02")), ("Humedad relativa", colors.HexColor("#1f78b4"))], 70, 358)
    c.showPage()
    c.save()
    return path


def chart_radiation(data: dict[str, list[float]]) -> Path:
    path = FIG_DIR / "epw-radiacion-mensual.pdf"
    c = setup_canvas(path, "Radiacion solar mensual", "GHI, DNI y DHI acumuladas por mes")
    x, y, w, h = 70, 80, 585, 265
    ymax = 230
    draw_axes(c, x, y, w, h, "kWh/m2 mes")
    for value in range(0, 231, 50):
        py = y + scale(value, 0, ymax, h)
        c.setStrokeColor(colors.HexColor("#e6eaed"))
        c.line(x, py, x + w, py)
        c.setFillColor(colors.HexColor("#52616b"))
        c.setFont("Helvetica", 7)
        c.drawRightString(x - 6, py - 2, str(value))
    bar_plot(c, x, y, w, h, data["ghi"], ymax, colors.HexColor("#f6c343"))
    line_plot(c, x, y, w, h, data["dni"], 0, ymax, colors.HexColor("#d95f02"))
    line_plot(c, x, y, w, h, data["dhi"], 0, ymax, colors.HexColor("#6a9f58"))
    draw_month_labels(c, x, y, w)
    legend(c, [("GHI", colors.HexColor("#f6c343")), ("DNI", colors.HexColor("#d95f02")), ("DHI", colors.HexColor("#6a9f58"))], 70, 358)
    c.showPage()
    c.save()
    return path


def chart_wind(rows: list[dict[str, float | str]]) -> Path:
    path = FIG_DIR / "epw-viento-direcciones.pdf"
    c = setup_canvas(path, "Distribucion de viento por direccion", "Frecuencia horaria y velocidad media por sector")
    sectors = [0] * 16
    speed_sum = [0.0] * 16
    for row in rows:
        direction = float(row["wind_dir"])
        speed = float(row["wind_speed"])
        if not valid(direction, "wind_dir") or not valid(speed, "wind_speed"):
            continue
        idx = int(((direction + 11.25) % 360) // 22.5)
        sectors[idx] += 1
        speed_sum[idx] += speed
    frequency = [v / sum(sectors) * 100 for v in sectors]
    speed = [speed_sum[i] / sectors[i] if sectors[i] else 0 for i in range(16)]
    x, y, w, h = 70, 80, 585, 265
    draw_axes(c, x, y, w, h, "Frecuencia (%)")
    ymax = max(frequency) * 1.15
    for value in range(0, int(math.ceil(ymax)) + 1, 5):
        py = y + scale(value, 0, ymax, h)
        c.setStrokeColor(colors.HexColor("#e6eaed"))
        c.line(x, py, x + w, py)
        c.setFillColor(colors.HexColor("#52616b"))
        c.setFont("Helvetica", 7)
        c.drawRightString(x - 6, py - 2, str(value))
    bar_plot(c, x, y, w, h, frequency, ymax, colors.HexColor("#5aa9a6"))
    line_plot(c, x, y, w, h, speed, 0, max(speed) * 1.2, colors.HexColor("#334e68"))
    step = w / 16
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#52616b"))
    for i, label in enumerate(DIRECTIONS):
        c.drawCentredString(x + i * step + step / 2, y - 15, label)
    legend(c, [("Frecuencia", colors.HexColor("#5aa9a6")), ("Velocidad media", colors.HexColor("#334e68"))], 70, 358)
    c.showPage()
    c.save()
    return path


def chart_sky_precip(data: dict[str, list[float]]) -> Path:
    path = FIG_DIR / "epw-cielo-precipitacion-mensual.pdf"
    c = setup_canvas(path, "Cobertura de cielo y precipitacion mensual", "Cobertura en octas y precipitacion liquida del EPW")
    x, y, w, h = 70, 80, 585, 265
    ymax = max(data["precip"]) * 1.25
    draw_axes(c, x, y, w, h, "Precipitacion (mm)")
    for value in range(0, int(math.ceil(ymax)) + 1, 5):
        py = y + scale(value, 0, ymax, h)
        c.setStrokeColor(colors.HexColor("#e6eaed"))
        c.line(x, py, x + w, py)
        c.setFillColor(colors.HexColor("#52616b"))
        c.setFont("Helvetica", 7)
        c.drawRightString(x - 6, py - 2, str(value))
    bar_plot(c, x, y, w, h, data["precip"], ymax, colors.HexColor("#4c78a8"))
    line_plot(c, x, y, w, h, data["sky"], 0, 10, colors.HexColor("#7b8794"))
    draw_month_labels(c, x, y, w)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#52616b"))
    for value in range(0, 11, 2):
        py = y + scale(value, 0, 10, h)
        c.drawString(x + w + 6, py - 2, str(value))
    legend(c, [("Precipitacion", colors.HexColor("#4c78a8")), ("Cobertura cielo", colors.HexColor("#7b8794"))], 70, 358)
    c.showPage()
    c.save()
    return path


def chart_hourly(data: dict[str, list[float]]) -> Path:
    path = FIG_DIR / "epw-perfil-horario-temperatura-radiacion.pdf"
    c = setup_canvas(path, "Perfil horario medio", "Temperatura exterior y radiacion global horizontal")
    x, y, w, h = 70, 80, 585, 265
    draw_axes(c, x, y, w, h, "Temperatura (C)")
    for value in range(20, 30, 2):
        py = y + scale(value, 20, 29, h)
        c.setStrokeColor(colors.HexColor("#e6eaed"))
        c.line(x, py, x + w, py)
        c.setFillColor(colors.HexColor("#52616b"))
        c.setFont("Helvetica", 7)
        c.drawRightString(x - 6, py - 2, str(value))
    line_plot(c, x, y, w, h, data["temp"], 20, 29, colors.HexColor("#d95f02"))
    line_plot(c, x, y, w, h, data["ghi"], 0, max(data["ghi"]) * 1.1, colors.HexColor("#f6c343"))
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#52616b"))
    for hour in range(0, 25, 4):
        px = x + ((hour if hour else 1) - 1) / 23 * w
        c.drawCentredString(px, y - 15, f"{hour:02d}h")
    legend(c, [("Temperatura", colors.HexColor("#d95f02")), ("GHI promedio", colors.HexColor("#f6c343"))], 70, 358)
    c.showPage()
    c.save()
    return path


def chart_heatmap(rows: list[dict[str, float | str]]) -> Path:
    path = FIG_DIR / "epw-mapa-calor-temperatura.pdf"
    c = setup_canvas(path, "Mapa horario de temperatura exterior", "Dias del ano meteorologico tipico vs hora")
    x, y, w, h = 70, 70, 585, 280
    temps = []
    for row in rows:
        value = float(row["dry_bulb"])
        if valid(value, "dry_bulb"):
            temps.append(value)
    tmin, tmax = min(temps), max(temps)
    cell_w = w / 365
    cell_h = h / 24

    def color_for(value: float):
        ratio = (value - tmin) / (tmax - tmin)
        if ratio < 0.5:
            local = ratio / 0.5
            r = int(57 + (246 - 57) * local)
            g = int(117 + (195 - 117) * local)
            b = int(173 + (67 - 173) * local)
        else:
            local = (ratio - 0.5) / 0.5
            r = int(246 + (213 - 246) * local)
            g = int(195 + (94 - 195) * local)
            b = int(67 + (0 - 67) * local)
        return colors.Color(r / 255, g / 255, b / 255)

    for idx, row in enumerate(rows):
        day = int((idx // 24))
        hour = int(float(row["hour"])) - 1
        temp = float(row["dry_bulb"])
        c.setFillColor(color_for(temp))
        c.rect(x + day * cell_w, y + hour * cell_h, cell_w + 0.2, cell_h + 0.2, stroke=0, fill=1)

    c.setStrokeColor(colors.HexColor("#98a1a8"))
    c.rect(x, y, w, h, stroke=1, fill=0)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#52616b"))
    for m, label in enumerate(MONTHS):
        day = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334][m]
        c.drawCentredString(x + day / 365 * w + 12, y - 14, label)
    for hour in range(0, 25, 6):
        c.drawRightString(x - 6, y + hour / 24 * h - 2, f"{hour:02d}")
    c.drawString(x, 48, f"Rango: {tmin:.1f} C a {tmax:.1f} C")
    c.showPage()
    c.save()
    return path


def write_summary(headers: list[str], rows: list[dict[str, float | str]], data: dict[str, list[float]], figures: list[Path]) -> None:
    mean_temp = avg(vals(rows, "dry_bulb"))
    mean_rh = avg(vals(rows, "rh"))
    annual_ghi = sum(vals(rows, "ghi")) / 1000
    mean_wind = avg(vals(rows, "wind_speed"))
    lines = [
        "# Graficos EPW San Cristobal",
        "",
        "Fuente local: `datos/ECU_GA_San.Cristobal.Intl.AP.840080_TMYx.2011-2025.epw`",
        "",
        "## Encabezado EPW",
        "",
    ]
    for header in headers[:8]:
        lines.append(f"- `{header}`")
    lines.extend(
        [
            "",
            "## Indicadores principales",
            "",
            f"- Temperatura media anual: {mean_temp:.2f} °C.",
            f"- Humedad relativa media anual: {mean_rh:.2f} %.",
            f"- Radiacion global horizontal anual: {annual_ghi:.2f} kWh/m2.",
            f"- Radiacion global horizontal media diaria: {annual_ghi / 365:.2f} kWh/m2 por dia.",
            f"- Velocidad media del viento: {mean_wind:.2f} m/s.",
            "",
            "## Figuras generadas",
            "",
        ]
    )
    for figure in figures:
        lines.append(f"- `figuras/{figure.name}`")
    lines.extend(["", "## Datos mensuales usados", ""])
    lines.append("| Mes | Temp. media (°C) | HR media (%) | GHI (kWh/m2) | DNI (kWh/m2) | DHI (kWh/m2) | Viento (m/s) | Cielo (octas) | Precip. (mm) |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for i, month in enumerate(MONTHS):
        lines.append(
            f"| {month} | {data['temp'][i]:.2f} | {data['rh'][i]:.1f} | {data['ghi'][i]:.1f} | "
            f"{data['dni'][i]:.1f} | {data['dhi'][i]:.1f} | {data['wind'][i]:.2f} | "
            f"{data['sky'][i]:.2f} | {data['precip'][i]:.1f} |"
        )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    headers, rows = parse_epw()
    monthly_data = monthly(rows)
    hourly_data = hourly(rows)
    figures = [
        chart_temp_humidity(monthly_data),
        chart_radiation(monthly_data),
        chart_wind(rows),
        chart_sky_precip(monthly_data),
        chart_hourly(hourly_data),
        chart_heatmap(rows),
    ]
    write_summary(headers, rows, monthly_data, figures)
    for figure in figures:
        print(figure.relative_to(ROOT))
    print(OUT_MD.relative_to(ROOT))


if __name__ == "__main__":
    main()
