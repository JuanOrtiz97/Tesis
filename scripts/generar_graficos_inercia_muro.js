const fs = require("fs");
const path = require("path");
const { PDFDocument, StandardFonts, rgb } = require("pdf-lib");

const OUT = path.join(process.cwd(), "figuras");
fs.mkdirSync(OUT, { recursive: true });

function drawText(page, font, text, x, y, size = 9, color = rgb(0, 0, 0)) {
  page.drawText(text, { x, y, size, font, color });
}

function drawPolyline(page, points, color, width = 1.2) {
  for (let i = 1; i < points.length; i += 1) {
    page.drawLine({
      start: { x: points[i - 1][0], y: points[i - 1][1] },
      end: { x: points[i][0], y: points[i][1] },
      thickness: width,
      color,
    });
  }
}

function mapLinear(value, inMin, inMax, outMin, outMax) {
  return outMin + ((value - inMin) / (inMax - inMin)) * (outMax - outMin);
}

async function createProfileFigure() {
  const pdf = await PDFDocument.create();
  const page = pdf.addPage([680, 350]);
  const font = await pdf.embedFont(StandardFonts.Helvetica);
  const bold = await pdf.embedFont(StandardFonts.HelveticaBold);

  const plot = { x: 58, y: 58, w: 390, h: 230 };
  const xScale = (v) => mapLinear(v, 0, 180, plot.x, plot.x + plot.w);
  const yScale = (v) => mapLinear(v, 16, 34, plot.y, plot.y + plot.h);

  drawText(page, bold, "Perfil de temperatura en el muro exterior", 150, 316, 12);
  drawText(page, font, "Temperatura [C]", 12, 182, 9);
  drawText(page, font, "Espesor del componente [mm]", 170, 26, 9);

  const layers = [
    [0, 15, "1", "Yeso 15 mm"],
    [15, 165, "2", "Bloque de hormigon 150 mm"],
    [165, 180, "3", "Enlucido cemento 15 mm"],
  ];
  for (const [start, end] of layers) {
    page.drawRectangle({
      x: xScale(start),
      y: plot.y,
      width: xScale(end) - xScale(start),
      height: plot.h,
      color: start === 15 ? rgb(0.93, 0.93, 0.93) : rgb(0.84, 0.84, 0.84),
      borderColor: rgb(0.55, 0.55, 0.55),
      borderWidth: 0.4,
    });
  }

  for (let t = 16; t <= 34; t += 2) {
    const y = yScale(t);
    page.drawLine({ start: { x: plot.x, y }, end: { x: plot.x + plot.w, y }, thickness: 0.3, color: rgb(0.82, 0.82, 0.82) });
    drawText(page, font, String(t), plot.x - 22, y - 3, 8);
  }
  for (let mm = 0; mm <= 180; mm += 20) {
    const x = xScale(mm);
    page.drawLine({ start: { x, y: plot.y }, end: { x, y: plot.y - 4 }, thickness: 0.5, color: rgb(0, 0, 0) });
    drawText(page, font, String(mm), x - 5, plot.y - 17, 8);
  }
  page.drawRectangle({ x: plot.x, y: plot.y, width: plot.w, height: plot.h, borderColor: rgb(0, 0, 0), borderWidth: 0.8 });

  const brown = rgb(0.38, 0.08, 0.05);
  const red = rgb(0.75, 0.05, 0.05);
  const xs = Array.from({ length: 120 }, (_, i) => (180 * i) / 119);
  const curvesBrown = [
    (x) => 21.2 + 0.2 * (x / 180) + 0.15 * Math.sin((Math.PI * x) / 180),
    (x) => 22.0 + 5.8 * (x / 180) - 0.3 * Math.sin((Math.PI * x) / 180),
    (x) => 26.0 + 5.8 * (x / 180) + 0.7 * Math.sin((1.2 * Math.PI * x) / 180),
  ];
  const curvesRed = [
    (x) => 24.2 - 6.5 * (x / 180) + 0.8 * Math.sin((Math.PI * x) / 180),
    (x) => 28.8 - 7.4 * (x / 180) - 0.5 * Math.sin((1.1 * Math.PI * x) / 180),
    (x) => 27.8 + 0.8 * (x / 180) - 1.6 * Math.sin((Math.PI * x) / 180),
  ];
  for (const fn of curvesBrown) drawPolyline(page, xs.map((x) => [xScale(x), yScale(fn(x))]), brown, 1.2);
  for (const fn of curvesRed) drawPolyline(page, xs.map((x) => [xScale(x), yScale(fn(x))]), red, 1.1);

  drawText(page, font, "Interior", plot.x - 10, 40, 8);
  drawText(page, font, "Exterior", plot.x + plot.w - 20, 40, 8);
  drawText(page, font, "Temperatura a 15h, 11h y 7h", 485, 260, 9, brown);
  drawText(page, font, "Temperatura a 19h, 23h y 3h", 485, 240, 9, red);
  for (const [start, end, number, label] of layers) {
    const x = xScale((start + end) / 2);
    const y = 272;
    page.drawCircle({ x, y, size: 9, color: rgb(1, 1, 1), borderColor: rgb(0, 0, 0), borderWidth: 0.8 });
    drawText(page, bold, number, x - 3, y - 3, 8);
    drawText(page, font, `${number}. ${label}`, 485, 210 - Number(number) * 18, 9);
  }

  fs.writeFileSync(path.join(OUT, "perfil-temperatura-muro-exterior.pdf"), await pdf.save());
}

async function createSurfaceFigure() {
  const pdf = await PDFDocument.create();
  const page = pdf.addPage([680, 350]);
  const font = await pdf.embedFont(StandardFonts.Helvetica);
  const bold = await pdf.embedFont(StandardFonts.HelveticaBold);

  const plot = { x: 58, y: 58, w: 430, h: 230 };
  const xScale = (v) => mapLinear(v, 12, 36, plot.x, plot.x + plot.w);
  const yScale = (v) => mapLinear(v, 16, 34, plot.y, plot.y + plot.h);

  drawText(page, bold, "Temperatura superficial durante el dia", 190, 316, 12);
  drawText(page, font, "Temperatura [C]", 12, 182, 9);
  drawText(page, font, "Hora del dia", 230, 26, 9);

  for (let t = 16; t <= 34; t += 2) {
    const y = yScale(t);
    page.drawLine({ start: { x: plot.x, y }, end: { x: plot.x + plot.w, y }, thickness: 0.3, color: rgb(0.84, 0.84, 0.84) });
    drawText(page, font, String(t), plot.x - 22, y - 3, 8);
  }
  const labels = ["12", "14", "16", "18", "20", "22", "24", "2", "4", "6", "8", "10", "12"];
  for (let i = 0; i < labels.length; i += 1) {
    const hour = 12 + i * 2;
    const x = xScale(hour);
    page.drawLine({ start: { x, y: plot.y }, end: { x, y: plot.y + plot.h }, thickness: 0.25, color: rgb(0.84, 0.84, 0.84) });
    drawText(page, font, labels[i], x - 5, plot.y - 17, 8);
  }
  page.drawRectangle({ x: plot.x, y: plot.y, width: plot.w, height: plot.h, borderColor: rgb(0, 0, 0), borderWidth: 0.8 });

  const hours = Array.from({ length: 220 }, (_, i) => 12 + (24 * i) / 219);
  const outside = hours.map((h) => 25 + 7.2 * Math.cos((2 * Math.PI * (h - 16)) / 24));
  const inside = hours.map((h) => 25 + 4.0 * Math.cos((2 * Math.PI * (h - 21.2)) / 24));
  drawPolyline(page, hours.map((h, i) => [xScale(h), yScale(outside[i])]), rgb(0.65, 0, 0), 1.5);
  drawPolyline(page, hours.map((h, i) => [xScale(h), yScale(inside[i])]), rgb(0, 0.08, 0.62), 1.5);

  const x1 = xScale(16);
  const x2 = xScale(21.2);
  page.drawLine({ start: { x: x1, y: yScale(16) }, end: { x: x1, y: yScale(34) }, thickness: 0.6, color: rgb(0.45, 0.45, 0.45) });
  page.drawLine({ start: { x: x2, y: yScale(16) }, end: { x: x2, y: yScale(34) }, thickness: 0.6, color: rgb(0.45, 0.45, 0.45) });
  page.drawLine({ start: { x: x1, y: 82 }, end: { x: x2, y: 82 }, thickness: 0.8, color: rgb(0.35, 0.35, 0.35) });
  page.drawLine({ start: { x: x1, y: 82 }, end: { x: x1 + 6, y: 88 }, thickness: 0.8, color: rgb(0.35, 0.35, 0.35) });
  page.drawLine({ start: { x: x1, y: 82 }, end: { x: x1 + 6, y: 76 }, thickness: 0.8, color: rgb(0.35, 0.35, 0.35) });
  page.drawLine({ start: { x: x2, y: 82 }, end: { x: x2 - 6, y: 88 }, thickness: 0.8, color: rgb(0.35, 0.35, 0.35) });
  page.drawLine({ start: { x: x2, y: 82 }, end: { x: x2 - 6, y: 76 }, thickness: 0.8, color: rgb(0.35, 0.35, 0.35) });
  drawText(page, font, "Desfase: 5,2 h", (x1 + x2) / 2 - 28, 66, 9, rgb(0.3, 0.3, 0.3));
  drawText(page, font, "Exterior", 525, 255, 9, rgb(0.65, 0, 0));
  drawText(page, font, "Interior", 525, 235, 9, rgb(0, 0.08, 0.62));

  fs.writeFileSync(path.join(OUT, "temperatura-superficial-muro-exterior.pdf"), await pdf.save());
}

async function main() {
  await createProfileFigure();
  await createSurfaceFigure();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
