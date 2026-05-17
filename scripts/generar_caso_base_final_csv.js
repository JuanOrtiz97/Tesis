const fs = require("fs");
const path = require("path");
const { PDFDocument, StandardFonts, rgb } = require("pdf-lib");

const INPUT = "C:/Users/juand/Desktop/Defensoria del Pueblo/Datos Caso Base/Datos Caso Base3.csv";
const OUT_TEX = path.join(process.cwd(), "insumos", "caso-base-final-tablas.tex");
const OUT_FIG = path.join(process.cwd(), "figuras");

fs.mkdirSync(path.dirname(OUT_TEX), { recursive: true });
fs.mkdirSync(OUT_FIG, { recursive: true });

function parseNumber(value) {
  if (value === undefined || value === null) return null;
  const clean = String(value).replace(",", ".").trim();
  if (!clean) return null;
  const number = Number(clean);
  return Number.isFinite(number) ? number : null;
}

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined || !Number.isFinite(value)) return "--";
  return value.toFixed(digits).replace(".", ",");
}

function tex(value) {
  return String(value)
    .replace(/\\/g, "\\textbackslash{}")
    .replace(/&/g, "\\&")
    .replace(/%/g, "\\%")
    .replace(/\$/g, "\\$")
    .replace(/#/g, "\\#")
    .replace(/_/g, "\\_")
    .replace(/{/g, "\\{")
    .replace(/}/g, "\\}");
}

function parseCsv(file) {
  const lines = fs.readFileSync(file, "latin1").trim().split(/\r?\n/);
  const headers = lines[0].split(";").map((x) => x.replace(/^"|"$/g, ""));
  const units = lines[1].split(";").map((x) => x.replace(/^"|"$/g, ""));
  const rows = lines.slice(2).filter(Boolean).map((line) => {
    const cells = line.split(";").map((x) => x.replace(/^"|"$/g, ""));
    const row = {};
    headers.forEach((header, index) => {
      if (header) row[header] = cells[index] || "";
    });
    const [day, month, year] = row["Date/Time"].split("/").map((x) => Number(x));
    row.__date = new Date(year, month - 1, day);
    row.__month = month;
    return row;
  });
  return { headers, units, rows };
}

function values(rows, column) {
  return rows.map((row) => parseNumber(row[column])).filter((value) => value !== null);
}

function sum(rows, column) {
  return values(rows, column).reduce((total, value) => total + value, 0);
}

function avg(rows, column) {
  const data = values(rows, column);
  return data.length ? data.reduce((total, value) => total + value, 0) / data.length : null;
}

function min(rows, column) {
  const data = values(rows, column);
  return data.length ? Math.min(...data) : null;
}

function max(rows, column) {
  const data = values(rows, column);
  return data.length ? Math.max(...data) : null;
}

function maxAbsRow(rows, column) {
  let best = null;
  for (const row of rows) {
    const value = parseNumber(row[column]);
    if (value === null) continue;
    if (!best || Math.abs(value) > Math.abs(best.value)) best = { row, value };
  }
  return best;
}

function monthName(month) {
  return ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"][month - 1];
}

function monthly(rows) {
  const out = [];
  for (let month = 1; month <= 12; month += 1) {
    const mr = rows.filter((row) => row.__month === month);
    out.push({
      month,
      label: monthName(month),
      coolingElectricity: sum(mr, "Cooling (Electricity)"),
      totalCooling: Math.abs(sum(mr, "Total Cooling")),
      solarExterior: sum(mr, "Solar Gains Exterior Windows"),
      operativeAvg: avg(mr, "Operative Temperature"),
      operativeMax: max(mr, "Operative Temperature"),
      outsideAvg: avg(mr, "Outside Dry-Bulb Temperature"),
    });
  }
  return out;
}

function drawText(page, font, text, x, y, size = 9, color = rgb(0, 0, 0)) {
  page.drawText(String(text), { x, y, size, font, color });
}

function map(value, inMin, inMax, outMin, outMax) {
  if (inMax === inMin) return outMin;
  return outMin + ((value - inMin) / (inMax - inMin)) * (outMax - outMin);
}

async function chartMonthlyCooling(data) {
  const pdf = await PDFDocument.create();
  const page = pdf.addPage([650, 360]);
  const font = await pdf.embedFont(StandardFonts.Helvetica);
  const bold = await pdf.embedFont(StandardFonts.HelveticaBold);
  const plot = { x: 58, y: 62, w: 500, h: 230 };
  const maxCooling = Math.max(...data.map((d) => d.coolingElectricity)) * 1.12;
  drawText(page, bold, "Enfriamiento electrico mensual del caso base", 165, 322, 12);
  drawText(page, font, "kWh/mes", 18, 180, 9);
  for (let i = 0; i <= 5; i += 1) {
    const value = (maxCooling / 5) * i;
    const y = map(value, 0, maxCooling, plot.y, plot.y + plot.h);
    page.drawLine({ start: { x: plot.x, y }, end: { x: plot.x + plot.w, y }, thickness: 0.3, color: rgb(0.82, 0.82, 0.82) });
    drawText(page, font, formatNumber(value, 0), plot.x - 45, y - 3, 8);
  }
  const barW = plot.w / data.length * 0.62;
  data.forEach((d, i) => {
    const cx = plot.x + (i + 0.5) * (plot.w / data.length);
    const h = map(d.coolingElectricity, 0, maxCooling, 0, plot.h);
    page.drawRectangle({ x: cx - barW / 2, y: plot.y, width: barW, height: h, color: rgb(0.27, 0.49, 0.76) });
    drawText(page, font, d.label, cx - 9, plot.y - 18, 8);
  });
  page.drawRectangle({ x: plot.x, y: plot.y, width: plot.w, height: plot.h, borderColor: rgb(0, 0, 0), borderWidth: 0.8 });
  fs.writeFileSync(path.join(OUT_FIG, "caso-base-final-enfriamiento-mensual.pdf"), await pdf.save());
}

async function chartMonthlyTemperature(data) {
  const pdf = await PDFDocument.create();
  const page = pdf.addPage([650, 360]);
  const font = await pdf.embedFont(StandardFonts.Helvetica);
  const bold = await pdf.embedFont(StandardFonts.HelveticaBold);
  const plot = { x: 58, y: 62, w: 500, h: 230 };
  drawText(page, bold, "Temperatura mensual del caso base", 215, 322, 12);
  drawText(page, font, "Temperatura [C]", 12, 180, 9);
  for (let t = 20; t <= 32; t += 2) {
    const y = map(t, 20, 32, plot.y, plot.y + plot.h);
    page.drawLine({ start: { x: plot.x, y }, end: { x: plot.x + plot.w, y }, thickness: 0.3, color: rgb(0.82, 0.82, 0.82) });
    drawText(page, font, String(t), plot.x - 22, y - 3, 8);
  }
  const line = (key, color) => {
    const pts = data.map((d, i) => [
      plot.x + (i + 0.5) * (plot.w / data.length),
      map(d[key], 20, 32, plot.y, plot.y + plot.h),
    ]);
    for (let i = 1; i < pts.length; i += 1) {
      page.drawLine({ start: { x: pts[i - 1][0], y: pts[i - 1][1] }, end: { x: pts[i][0], y: pts[i][1] }, thickness: 1.5, color });
    }
    pts.forEach(([x, y]) => page.drawCircle({ x, y, size: 2.3, color }));
  };
  line("operativeAvg", rgb(0.76, 0.20, 0.20));
  line("outsideAvg", rgb(0.16, 0.39, 0.67));
  data.forEach((d, i) => drawText(page, font, d.label, plot.x + (i + 0.5) * (plot.w / data.length) - 9, plot.y - 18, 8));
  drawText(page, font, "Operativa interior", 495, 285, 8, rgb(0.76, 0.20, 0.20));
  drawText(page, font, "Exterior", 495, 270, 8, rgb(0.16, 0.39, 0.67));
  page.drawRectangle({ x: plot.x, y: plot.y, width: plot.w, height: plot.h, borderColor: rgb(0, 0, 0), borderWidth: 0.8 });
  fs.writeFileSync(path.join(OUT_FIG, "caso-base-final-temperatura-mensual.pdf"), await pdf.save());
}

async function chartHeatBalance(balance) {
  const pdf = await PDFDocument.create();
  const page = pdf.addPage([650, 390]);
  const font = await pdf.embedFont(StandardFonts.Helvetica);
  const bold = await pdf.embedFont(StandardFonts.HelveticaBold);
  const plot = { x: 200, y: 58, w: 360, h: 260 };
  const maxAbs = Math.max(...balance.map((d) => Math.abs(d.value))) * 1.15;
  drawText(page, bold, "Balance anual por componentes del caso base", 180, 352, 12);
  const zeroX = map(0, -maxAbs, maxAbs, plot.x, plot.x + plot.w);
  page.drawLine({ start: { x: zeroX, y: plot.y }, end: { x: zeroX, y: plot.y + plot.h }, thickness: 0.8, color: rgb(0.2, 0.2, 0.2) });
  balance.forEach((d, i) => {
    const y = plot.y + plot.h - (i + 1) * (plot.h / balance.length) + 5;
    const x = map(Math.min(0, d.value), -maxAbs, maxAbs, plot.x, plot.x + plot.w);
    const x2 = map(Math.max(0, d.value), -maxAbs, maxAbs, plot.x, plot.x + plot.w);
    page.drawRectangle({ x, y, width: Math.max(1, x2 - x), height: 12, color: d.value < 0 ? rgb(0.30, 0.53, 0.78) : rgb(0.80, 0.34, 0.25) });
    drawText(page, font, d.label, 30, y + 2, 8);
    drawText(page, font, formatNumber(d.value, 0), x2 + 5, y + 2, 8);
  });
  drawText(page, font, "Perdidas (-) y ganancias (+) [kWh/ano]", 245, 32, 9);
  fs.writeFileSync(path.join(OUT_FIG, "caso-base-final-balance-componentes.pdf"), await pdf.save());
}

function writeTex(rows, monthData, balance) {
  const totalCooling = Math.abs(sum(rows, "Total Cooling"));
  const coolingElectricity = sum(rows, "Cooling (Electricity)");
  const roomElectricity = sum(rows, "Room Electricity");
  const lighting = sum(rows, "Lighting");
  const solarExterior = sum(rows, "Solar Gains Exterior Windows");
  const solarInterior = sum(rows, "Solar Gains Interior Windows");
  const opAvg = avg(rows, "Operative Temperature");
  const opMax = max(rows, "Operative Temperature");
  const outsideAvg = avg(rows, "Outside Dry-Bulb Temperature");
  const ventAvg = avg(rows, "Mech Vent + Nat Vent + Infiltration");
  const peakCooling = maxAbsRow(rows, "Total Cooling");
  const peakElectric = maxAbsRow(rows, "Cooling (Electricity)");
  const daysOp28 = values(rows, "Operative Temperature").filter((v) => v > 28).length;
  const daysOp30 = values(rows, "Operative Temperature").filter((v) => v > 30).length;

  const lines = [];
  lines.push("{\\fontsize{9}{11}\\selectfont");
  lines.push("\\begin{longtable}{p{4.9cm}p{3cm}p{5.5cm}}");
  lines.push("  \\caption{Sintesis final de resultados del caso base} \\\\");
  lines.push("  \\toprule");
  lines.push("  Indicador & Valor & Lectura \\\\");
  lines.push("  \\midrule");
  lines.push("  \\endfirsthead");
  lines.push("  \\caption[]{Sintesis final de resultados del caso base (continuacion)} \\\\");
  lines.push("  \\toprule");
  lines.push("  Indicador & Valor & Lectura \\\\");
  lines.push("  \\midrule");
  lines.push("  \\endhead");
  lines.push("  \\bottomrule");
  lines.push("  \\endfoot");
  lines.push(`  Enfriamiento sensible total & $${formatNumber(totalCooling)}\\,\\mathrm{kWh/ano}$ & Demanda termica anual acumulada del caso base. \\\\`);
  lines.push(`  Electricidad para enfriamiento & $${formatNumber(coolingElectricity)}\\,\\mathrm{kWh/ano}$ & Consumo electrico anual asociado a enfriamiento. \\\\`);
  lines.push(`  Electricidad de equipos & $${formatNumber(roomElectricity)}\\,\\mathrm{kWh/ano}$ & Equipos, miscelaneos y cargas internas electricas. \\\\`);
  lines.push(`  Electricidad de iluminacion & $${formatNumber(lighting)}\\,\\mathrm{kWh/ano}$ & Consumo anual de iluminacion del modelo. \\\\`);
  lines.push(`  Ganancias solares por ventanas exteriores & $${formatNumber(solarExterior)}\\,\\mathrm{kWh/ano}$ & Ganancia solar directa por acristalamientos exteriores. \\\\`);
  lines.push(`  Pico diario de enfriamiento & $${formatNumber(Math.abs(peakCooling.value))}\\,\\mathrm{kWh/dia}$ & Dia critico: ${tex(peakCooling.row["Date/Time"])}. \\\\`);
  lines.push(`  Pico diario de electricidad de enfriamiento & $${formatNumber(peakElectric.value)}\\,\\mathrm{kWh/dia}$ & Dia critico: ${tex(peakElectric.row["Date/Time"])}. \\\\`);
  lines.push(`  Temperatura operativa media & $${formatNumber(opAvg)}\\,^\\circ C$ & Promedio diario anual del caso base. \\\\`);
  lines.push(`  Temperatura operativa maxima & $${formatNumber(opMax)}\\,^\\circ C$ & Mayor promedio diario de temperatura operativa. \\\\`);
  lines.push(`  Dias con $T_{op}>28\\,^\\circ C$ & ${daysOp28} dias & Periodos con mayor riesgo de disconfort termico. \\\\`);
  lines.push(`  Ventilacion e infiltracion media & $${formatNumber(ventAvg)}\\,\\mathrm{ACH}$ & Renovacion media diaria reportada por el modelo. \\\\`);
  lines.push("\\end{longtable}");
  lines.push("}");
  lines.push("\\fuente{Elaboracion propia a partir de \\texttt{Datos Caso Base3.csv}.}");
  lines.push("");

  lines.push("{\\fontsize{8}{10}\\selectfont");
  lines.push("\\begin{longtable}{p{1.5cm}p{2.2cm}p{2.2cm}p{2.2cm}p{2.1cm}p{2.1cm}}");
  lines.push("  \\caption{Resultados mensuales principales del caso base} \\\\");
  lines.push("  \\toprule");
  lines.push("  Mes & Enfriamiento electrico & Enfriamiento termico & Ganancia solar ext. & $T_{op}$ media & $T_{ext}$ media \\\\");
  lines.push("  & kWh & kWh & kWh & $^\\circ C$ & $^\\circ C$ \\\\");
  lines.push("  \\midrule");
  lines.push("  \\endfirsthead");
  lines.push("  \\caption[]{Resultados mensuales principales del caso base (continuacion)} \\\\");
  lines.push("  \\toprule");
  lines.push("  Mes & Enfriamiento electrico & Enfriamiento termico & Ganancia solar ext. & $T_{op}$ media & $T_{ext}$ media \\\\");
  lines.push("  & kWh & kWh & kWh & $^\\circ C$ & $^\\circ C$ \\\\");
  lines.push("  \\midrule");
  lines.push("  \\endhead");
  lines.push("  \\bottomrule");
  lines.push("  \\endfoot");
  monthData.forEach((m) => {
    lines.push(`  ${m.label} & $${formatNumber(m.coolingElectricity)}$ & $${formatNumber(m.totalCooling)}$ & $${formatNumber(m.solarExterior)}$ & $${formatNumber(m.operativeAvg)}$ & $${formatNumber(m.outsideAvg)}$ \\\\`);
  });
  lines.push("\\end{longtable}");
  lines.push("}");
  lines.push("\\fuente{Elaboracion propia a partir de \\texttt{Datos Caso Base3.csv}.}");
  lines.push("");

  lines.push("{\\fontsize{8}{10}\\selectfont");
  lines.push("\\begin{longtable}{p{4.4cm}p{2.7cm}p{6cm}}");
  lines.push("  \\caption{Balance anual por componentes del caso base} \\\\");
  lines.push("  \\toprule");
  lines.push("  Componente & Balance anual & Interpretacion \\\\");
  lines.push("  \\midrule");
  lines.push("  \\endfirsthead");
  lines.push("  \\caption[]{Balance anual por componentes del caso base (continuacion)} \\\\");
  lines.push("  \\toprule");
  lines.push("  Componente & Balance anual & Interpretacion \\\\");
  lines.push("  \\midrule");
  lines.push("  \\endhead");
  lines.push("  \\bottomrule");
  lines.push("  \\endfoot");
  balance.forEach((b) => {
    const reading = b.value < 0 ? "Perdida neta de calor en el periodo anual." : "Ganancia neta de calor en el periodo anual.";
    lines.push(`  ${tex(b.label)} & $${formatNumber(b.value)}\\,\\mathrm{kWh}$ & ${reading} \\\\`);
  });
  lines.push("\\end{longtable}");
  lines.push("}");
  lines.push("\\fuente{Elaboracion propia a partir de \\texttt{Datos Caso Base3.csv}.}");
  lines.push("");

  lines.push("\\begin{figure}[H]");
  lines.push("  \\centering");
  lines.push("  \\includegraphics[width=0.9\\textwidth]{figuras/caso-base-final-enfriamiento-mensual.pdf}");
  lines.push("  \\caption{Enfriamiento electrico mensual del caso base final}");
  lines.push("  \\fuente{Elaboracion propia a partir de \\texttt{Datos Caso Base3.csv}.}");
  lines.push("\\end{figure}");
  lines.push("");
  lines.push("\\begin{figure}[H]");
  lines.push("  \\centering");
  lines.push("  \\includegraphics[width=0.9\\textwidth]{figuras/caso-base-final-temperatura-mensual.pdf}");
  lines.push("  \\caption{Temperatura mensual interior y exterior del caso base final}");
  lines.push("  \\fuente{Elaboracion propia a partir de \\texttt{Datos Caso Base3.csv}.}");
  lines.push("\\end{figure}");
  lines.push("");
  lines.push("\\begin{figure}[H]");
  lines.push("  \\centering");
  lines.push("  \\includegraphics[width=0.9\\textwidth]{figuras/caso-base-final-balance-componentes.pdf}");
  lines.push("  \\caption{Balance anual por componentes del caso base final}");
  lines.push("  \\fuente{Elaboracion propia a partir de \\texttt{Datos Caso Base3.csv}.}");
  lines.push("\\end{figure}");
  lines.push("");
  lines.push(`La serie diaria final confirma que el caso base presenta una demanda anual relevante de enfriamiento, con mayor presion durante los meses de mayor ganancia solar y temperatura exterior. Las ventanas exteriores aportan $${formatNumber(solarExterior)}\\,\\mathrm{kWh/ano}$ de ganancia solar, por lo que las medidas de control solar y sombreamiento siguen siendo prioritarias antes de depender exclusivamente de sistemas activos.`);

  fs.writeFileSync(OUT_TEX, lines.join("\n") + "\n", "utf8");
}

async function main() {
  const { rows } = parseCsv(INPUT);
  const monthData = monthly(rows);
  const balanceColumns = [
    ["Glazing", "Acristalamientos"],
    ["Walls", "Muros"],
    ["Ground Floors", "Piso sobre terreno"],
    ["Roofs", "Cubiertas"],
    ["Ceilings (int)", "Cielos interiores"],
    ["Floors (int)", "Pisos interiores"],
    ["Partitions (int)", "Particiones interiores"],
    ["Internal Natural vent.", "Ventilacion natural interna"],
    ["External Air", "Aire exterior"],
    ["External Vent.", "Ventilacion exterior"],
    ["Occupancy", "Ocupacion"],
    ["Solar Gains Interior Windows", "Ganancia solar interior"],
    ["Solar Gains Exterior Windows", "Ganancia solar exterior"],
  ];
  const balance = balanceColumns
    .map(([column, label]) => ({ label, value: sum(rows, column) }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
  writeTex(rows, monthData, balance);
  await chartMonthlyCooling(monthData);
  await chartMonthlyTemperature(monthData);
  await chartHeatBalance(balance.slice(0, 10));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
