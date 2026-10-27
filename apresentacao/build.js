const pptxgen = require("pptxgenjs");
const path = require("path");
const NOTES = require("./notes");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "TCC - Robo Seguidor de Linha";
pptx.company = "Feira de Ciencias";
pptx.subject = "Aprendizado por reforco em um robo seguidor de linha";
pptx.title = "Como um robo aprende?";
pptx.lang = "pt-BR";

const SW = 13.333, SH = 7.5, M = 0.85;
const C = {
  paper: "F4F1EA",
  ink: "171512",
  muted: "6E6960",
  rule: "D9D2C5",
  terra: "C24E2E",
  sand: "E7DCCB",
  sandLight: "EFE7DA",
  sage: "7D8577",
  dark: "171512",
  paperDim: "C9C1B3",
  watermark: "E2D7C6",
  darkWatermark: "2B2722",
};
const F = {
  display: "Bahnschrift Light",
  sans: "Bahnschrift",
  body: "Segoe UI",
  serif: "Georgia",
  mono: "Consolas",
};
const ASSETS = path.join(__dirname, "assets");

function bg(s, color = C.paper) { s.background = { color }; }

function tx(s, text, x, y, w, h, o = {}) {
  s.addText(text, {
    x, y, w, h,
    margin: 0,
    fontFace: o.face || F.body,
    fontSize: o.size || 14,
    color: o.color || C.ink,
    bold: !!o.bold,
    italic: !!o.italic,
    align: o.align || "left",
    valign: o.valign || "top",
    charSpacing: o.spacing || 0,
    lineSpacing: o.lh || undefined,
    transparency: o.transparency || 0,
    rotate: o.rotate || 0,
    fit: "none",
  });
}

function kicker(s, text, dark = false) {
  tx(s, text.toUpperCase(), M, 0.52, 7.5, 0.25, {
    face: F.mono, size: 9, color: dark ? C.paperDim : C.muted, spacing: 2.1,
  });
}

function footer(s, dark = false) {
  tx(s, "Como um robô aprende · Feira de Ciências 2026", M, 7.12, 7.5, 0.18, {
    size: 7.5, color: dark ? "8E877A" : C.muted,
  });
}

function page(s, n, dark = false) {
  tx(s, String(n).padStart(2, "0"), 12.0, 7.1, 0.5, 0.2, {
    face: F.mono, size: 8, color: dark ? "8E877A" : C.muted, align: "right",
  });
}

function line(s, x1, y1, x2, y2, color = C.rule, width = 0.75, head = false) {
  s.addShape(pptx.ShapeType.line, {
    x: Math.min(x1, x2), y: Math.min(y1, y2),
    w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001,
    flipH: x2 < x1, flipV: y2 < y1,
    line: {
      color, width,
      beginArrowType: "none",
      endArrowType: head ? "triangle" : "none",
    },
    fill: { color: C.paper, transparency: 100 },
  });
}

function rect(s, x, y, w, h, fill = C.sand, o = {}) {
  s.addShape(pptx.ShapeType.rect, {
    x, y, w, h,
    fill: { color: fill, transparency: o.transparency || 0 },
    line: { color: o.line || fill, width: o.lineWidth || 0, transparency: o.lineTransparency || 0 },
    rectRadius: o.radius || undefined,
    rotate: o.rotate || 0,
  });
}

function roundRect(s, x, y, w, h, fill = C.sand, o = {}) {
  s.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    fill: { color: fill, transparency: o.transparency || 0 },
    line: { color: o.line || fill, width: o.lineWidth || 0, transparency: o.lineTransparency || 0 },
    rectRadius: o.radius || 0.04,
    rotate: o.rotate || 0,
  });
}

function dot(s, x, y, d, color = C.terra, o = {}) {
  s.addShape(pptx.ShapeType.ellipse, {
    x, y, w: d, h: d,
    fill: { color, transparency: o.transparency || 0 },
    line: o.outline ? { color: o.outline, width: o.outlineWidth || 0.75 } : { color, width: 0 },
  });
}

function titleLines(s, lines, y = 1.12, o = {}) {
  const size = o.size || 50;
  const lh = o.lh || (size * 0.98) / 72;
  lines.forEach((ln, i) => {
    tx(s, ln.text, M, y + i * lh, o.w || 11.6, lh * 1.25, {
      face: ln.face || o.face || F.display,
      size: ln.size || size,
      color: ln.color || C.ink,
      italic: ln.italic,
      bold: ln.bold,
      lh: (ln.size || size) * 0.95,
      spacing: ln.spacing || 0,
    });
  });
}

function stat(s, num, label, x, y, w, o = {}) {
  tx(s, num, x, y, w, 0.95, {
    face: F.display, size: o.size || 76, color: o.color || C.ink, align: o.align || "left",
  });
  tx(s, label.toUpperCase(), x, y + (o.labelGap || 1.0), w, 0.3, {
    face: F.mono, size: o.labelSize || 8.5, color: o.labelColor || C.muted,
    spacing: 1.5, align: o.align || "left",
  });
}

function tag(s, text, x, y, color = C.terra) {
  tx(s, text.toUpperCase(), x, y, 3.0, 0.2, {
    face: F.mono, size: 8, color, spacing: 1.6,
  });
}

function addImage(s, file, x, y, w, h, alt = "") {
  s.addImage({ path: path.join(ASSETS, file), x, y, w, h, altText: alt });
}

/* =====================================================================
   01 — CAPA
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "Feira de Ciências · 2026");
  tx(s, "Q-LEARNING  ·  8 ESTADOS  ·  3 AÇÕES", 9.1, 0.55, 3.4, 0.25, {
    face: F.mono, size: 7.5, color: C.muted, spacing: 1.3, align: "right",
  });

  tx(s, "Como um", M, 1.55, 8.0, 1.05, { face: F.display, size: 82, color: C.ink });
  tx(s, "robô aprende?", M, 2.55, 9.2, 1.15, { face: F.display, size: 82, color: C.ink });

  tx(s, "Um seguidor de linha que descobre o caminho por tentativa e erro.", M, 4.25, 6.3, 0.9, {
    size: 19, color: C.muted, lh: 25,
  });

  tx(s, "ROBÓTICA  ·  INTELIGÊNCIA ARTIFICIAL", M, 5.55, 6.0, 0.25, {
    face: F.mono, size: 8.5, color: C.terra, spacing: 2.0,
  });

  // motif 8 x 3
  tx(s, "8 × 3", 8.65, 1.05, 4.0, 2.4, {
    face: F.display, size: 128, color: C.watermark, align: "center",
  });
  tx(s, "estados × ações", 9.35, 3.55, 3.3, 0.3, {
    face: F.mono, size: 9, color: C.muted, spacing: 1.6, align: "center",
  });
  dot(s, 12.18, 2.18, 0.10, C.terra);

  line(s, M, 6.55, 12.48, 6.55, C.rule, 0.75);
  tx(s, "O ROBÔ ESTÁ AO LADO  ·  PERGUNTE A ELE", M, 6.72, 6.0, 0.25, {
    face: F.mono, size: 8, color: C.muted, spacing: 1.5,
  });
  tx(s, "2026", 12.0, 6.72, 0.5, 0.25, {
    face: F.mono, size: 8, color: C.muted, align: "right",
  });
  s.addNotes(NOTES["01"]);
}

/* =====================================================================
   02 — O DESAFIO
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "01 · O desafio");

  titleLines(s, [
    { text: "Seguir uma linha" },
    { text: "parece simples." },
  ], 1.15, { size: 56 });

  tx(s, "Para uma máquina, é decidir 10 vezes por segundo.", M, 3.05, 9.2, 0.55, {
    face: F.serif, size: 26, italic: true, color: C.terra,
  });

  tx(s, "A cada passo, o robô lê o chão, escolhe uma entre três ações e move dois motores. Sem parar.", M, 3.95, 6.9, 0.85, {
    size: 15, color: C.muted, lh: 21,
  });

  stat(s, "3", "sensores infravermelhos", M, 5.15, 2.3);
  stat(s, "3", "ações possíveis", 3.6, 5.15, 2.3);
  stat(s, "10×", "decisões por segundo", 6.3, 5.15, 3.2);

  footer(s); page(s, 2);
  s.addNotes(NOTES["02"]);
}

/* =====================================================================
   03 — DUAS ABORDAGENS
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "02 · Duas abordagens");

  titleLines(s, [
    { text: "Regras prontas" },
    { text: "ou aprender fazendo?" },
  ], 1.15, { size: 52 });

  tx(s, "Todo robô seguidor de linha precisa responder à mesma pergunta: para onde ir agora? A diferença está em como a resposta é produzida.", M, 3.0, 10.7, 0.7, {
    size: 14.5, color: C.muted, lh: 20,
  });

  const y = 4.0, h = 1.85, w = 5.45;
  rect(s, M, y, w, h, C.sandLight);
  rect(s, 7.05, y, w, h, C.sandLight);

  tag(s, "Regras prontas", M + 0.35, y + 0.28, C.muted);
  tx(s, "if (esq && !dir)\n    virar(ESQUERDA)\nelse if (!esq && dir)\n    virar(DIREITA)", M + 0.35, y + 0.6, w - 0.7, 1.0, {
    face: F.mono, size: 11, color: C.ink, lh: 16,
  });
  tx(s, "O programador decide cada caso.", M + 0.35, y + 1.5, w - 0.7, 0.25, {
    size: 10.5, color: C.muted,
  });

  tag(s, "Aprender fazendo", 7.05 + 0.35, y + 0.28, C.terra);
  tx(s, "ação  →  recompensa  →  nova nota", 7.05 + 0.35, y + 0.7, w - 0.7, 0.35, {
    face: F.mono, size: 11, color: C.ink,
  });
  tx(s, "O robô descobre o que funciona.", 7.05 + 0.35, y + 1.16, w - 0.7, 0.3, {
    size: 12, color: C.muted,
  });
  tx(s, "Sem regras escritas à mão.", 7.05 + 0.35, y + 1.48, w - 0.7, 0.3, {
    size: 12, color: C.muted,
  });

  tx(s, "O primeiro repete. O segundo se adapta.", M, 6.18, 10.0, 0.5, {
    face: F.serif, size: 23, italic: true, color: C.ink,
  });

  footer(s); page(s, 3);
  s.addNotes(NOTES["03"]);
}

/* =====================================================================
   04 — RECOMPENSA
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "03 · A regra do jogo");

  tx(s, "A recompensa", M, 1.12, 8.5, 0.95, { face: F.display, size: 58, color: C.ink });
  tx(s, "é o professor.", M, 1.92, 8.5, 0.95, { face: F.serif, size: 54, italic: true, color: C.terra });

  tx(s, "Não é uma instrução. É uma nota que chega depois da ação — e diz se ela foi boa ou ruim.", M, 3.25, 9.0, 0.6, {
    size: 15, color: C.muted, lh: 21,
  });

  const items = [
    { n: "+1,0", label: "centro na linha", bits: [0, 1, 0], color: C.terra },
    { n: "-0,5", label: "sensor lateral ativo", bits: [1, 0, 0], color: C.ink },
    { n: "-3,0", label: "perdeu a linha", bits: [0, 0, 0], color: C.ink },
  ];

  items.forEach((it, i) => {
    const x = M + i * 3.95;
    tx(s, it.n, x, 4.15, 3.2, 1.1, { face: F.display, size: 72, color: it.color });
    for (let k = 0; k < 3; k++) {
      dot(s, x + k * 0.30, 5.35, 0.13, it.bits[k] ? C.terra : C.paper, {
        outline: it.bits[k] ? C.terra : C.ink, outlineWidth: 0.9,
      });
    }
    tx(s, it.label, x + 1.15, 5.28, 2.7, 0.35, { size: 11, color: C.muted });
  });

  line(s, M, 6.0, 12.48, 6.0, C.rule, 0.75);
  tx(s, "Como petiscos para um cachorro — só que o petisco é um número.", M, 6.2, 10.5, 0.45, {
    face: F.serif, size: 21, italic: true, color: C.muted,
  });

  footer(s); page(s, 4);
  s.addNotes(NOTES["04"]);
}

/* =====================================================================
   05 — OITO ESTADOS
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "04 · O mundo do robô");

  titleLines(s, [
    { text: "Três sensores." },
    { text: "Oito situações." },
  ], 1.15, { size: 52 });

  tx(s, "Cada sensor responde apenas 0 ou 1: branco ou preto. Três sensores binários geram 2³ = 8 leituras possíveis.", M, 3.05, 5.3, 1.0, {
    size: 14.5, color: C.muted, lh: 21,
  });

  tx(s, "2", M, 4.28, 0.8, 1.2, { face: F.display, size: 78, color: C.terra });
  tx(s, "3", M + 0.68, 4.18, 0.5, 0.7, { face: F.display, size: 36, color: C.terra });
  tx(s, "=", M + 1.18, 4.28, 0.8, 1.2, { face: F.display, size: 78, color: C.terra });
  tx(s, "8", M + 2.0, 4.28, 0.9, 1.2, { face: F.display, size: 78, color: C.terra });
  tx(s, "Toda a percepção do robô cabe em oito códigos.", M, 5.65, 4.5, 0.7, {
    size: 14, color: C.ink, lh: 20,
  });

  const states = ["000", "001", "010", "011", "100", "101", "110", "111"];
  const x = 7.15, y0 = 1.82, rh = 0.55;
  tx(s, "L   M   R", x + 1.2, y0 - 0.22, 1.2, 0.2, { face: F.mono, size: 8, color: C.muted, spacing: 1.4 });
  states.forEach((st, i) => {
    const yy = y0 + i * rh;
    if (st === "010") {
      rect(s, x - 0.15, yy - 0.08, 5.15, 0.46, C.sand, { transparency: 25 });
    }
    tx(s, st, x, yy, 0.85, 0.32, { face: F.mono, size: 11.5, color: C.ink });
    for (let k = 0; k < 3; k++) {
      const on = st[k] === "1";
      dot(s, x + 1.18 + k * 0.34, yy + 0.05, 0.13, on ? C.terra : C.paper, {
        outline: on ? C.terra : C.ink, outlineWidth: 0.9,
      });
    }
    if (st === "010") {
      tx(s, "na linha", x + 2.55, yy + 0.02, 1.1, 0.25, {
        face: F.mono, size: 8, color: C.terra,
      });
    }
  });
  tx(s, "● 1 = preto   ○ 0 = branco", x, 6.35, 4.0, 0.25, {
    face: F.mono, size: 8, color: C.muted,
  });

  footer(s); page(s, 5);
  s.addNotes(NOTES["05"]);
}

/* =====================================================================
   06 — A Q-TABLE
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "05 · A tabela");

  titleLines(s, [
    { text: "Uma tabela" },
    { text: "de notas." },
  ], 1.15, { size: 54 });

  tx(s, "Oito situações nas linhas. Três ações nas colunas. Cada célula guarda quanto vale escolher aquela ação naquela situação.", M, 3.0, 4.5, 1.3, {
    size: 14.5, color: C.muted, lh: 21,
  });

  tx(s, "A maior nota da linha vira a decisão.", M, 4.55, 4.3, 0.5, {
    face: F.serif, size: 20, italic: true, color: C.terra,
  });

  tx(s, "8 × 3 = 24 notas.", M, 5.45, 4.0, 0.4, { face: F.mono, size: 11, color: C.ink });
  tx(s, "É só isso que ele precisa guardar.", M, 5.78, 4.0, 0.4, { size: 11, color: C.muted });

  const Q = [
    [-11.23, -9.52, -8.83],
    [-1.39, 6.67, 7.83],
    [7.71, 8.96, 8.35],
    [6.83, 8.59, 9.04],
    [8.38, 6.35, -0.08],
    [0.0, 0.0, 0.0],
    [9.01, 8.61, 7.21],
    [3.42, 0.74, 0.0],
  ];
  const states = ["000", "001", "010", "011", "100", "101", "110", "111"];
  const tX = 5.95, tY = 1.72, lw = 0.82, cw = 1.58, ch = 0.46, gapx = 0.06, gapy = 0.08;

  const heads = ["← ESQ", "RETO ↑", "DIR →"];
  heads.forEach((h, j) => {
    tx(s, h, tX + lw + j * (cw + gapx), tY - 0.3, cw, 0.25, {
      face: F.mono, size: 8, color: C.muted, spacing: 0.8,
    });
  });

  states.forEach((st, i) => {
    const yy = tY + i * (ch + gapy);
    tx(s, st, tX, yy + 0.09, lw, 0.25, { face: F.mono, size: 9.5, color: C.muted });
    let best = 0;
    for (let j = 1; j < 3; j++) if (Q[i][j] > Q[i][best]) best = j;
    for (let j = 0; j < 3; j++) {
      const v = Q[i][j];
      const isBest = j === best;
      const fill = isBest ? C.terra : (v < -0.5 ? C.sage : (v > 0.5 ? C.terra : C.sandLight));
      const trans = isBest ? 0 : (v < -0.5 || v > 0.5 ? 82 : 45);
      rect(s, tX + lw + j * (cw + gapx), yy, cw, ch, fill, { transparency: trans });
      const label = (v > 0 ? "+" : "") + v.toFixed(1).replace(".", ",");
      tx(s, label, tX + lw + j * (cw + gapx), yy + 0.1, cw, 0.25, {
        face: F.mono, size: 10.5, color: isBest ? C.paper : C.ink,
        bold: isBest, align: "center",
      });
    }
  });

  tx(s, "célula terracota = melhor ação da linha", tX, 6.14, 4.0, 0.22, {
    face: F.mono, size: 7.8, color: C.muted,
  });
  tx(s, "0,0 = estado ainda sem experiência", tX, 6.4, 4.0, 0.22, {
    face: F.mono, size: 7.8, color: C.muted,
  });
  tx(s, "EXEMPLO  010 → RETO  (+9,0)", tX, 6.68, 4.0, 0.22, {
    face: F.mono, size: 8.2, color: C.terra,
  });

  footer(s); page(s, 6);
  s.addNotes(NOTES["06"]);
}

/* =====================================================================
   07 — EVOLUÇÃO DA Q-TABLE
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "06 · Aprendizado");

  titleLines(s, [
    { text: "No começo, tudo zero." },
    { text: "Depois, cada linha ganha preferência." },
  ], 1.05, { size: 40, lh: 0.62, w: 11.8 });

  tx(s, "A mesma grade 8×3 em quatro momentos. A cada episódio, uma célula muda um pouco.", M, 2.42, 10.2, 0.35, {
    size: 14, color: C.muted,
  });

  addImage(s, "qtable_evolution.png", M, 2.92, 11.4, 2.92,
    "Quatro grades 8 por 3 mostrando a Q-table nos episódios 10, 50, 100 e 200.");

  tx(s, "verde = nota negativa   ·   terracota = nota positiva", M, 5.98, 6.2, 0.25, {
    face: F.mono, size: 8, color: C.muted,
  });

  line(s, M, 6.38, 12.48, 6.38, C.rule, 0.75);
  tx(s, "24 números. É só isso que o robô precisa guardar.", M, 6.55, 8.5, 0.3, {
    face: F.serif, size: 19, italic: true, color: C.ink,
  });

  footer(s); page(s, 7);
  s.addNotes(NOTES["07"]);
}

/* =====================================================================
   08 — O CICLO
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "07 · O ciclo");

  titleLines(s, [
    { text: "Sensar. Escolher." },
    { text: "Agir. Medir." },
  ], 1.05, { size: 50 });

  tx(s, "Um ciclo curto, repetido sem parar.", M, 2.65, 8.0, 0.35, {
    size: 15, color: C.muted,
  });

  const blocks = [
    { n: "01", t: "SENSAR", d: "lê os três sensores", x: 1.0, y: 3.05 },
    { n: "02", t: "ESCOLHER", d: "consulta a linha da tabela", x: 8.25, y: 3.05 },
    { n: "03", t: "AGIR", d: "aciona os dois motores", x: 8.25, y: 4.95 },
    { n: "04", t: "MEDIR", d: "recebe a recompensa", x: 1.0, y: 4.95 },
  ];
  blocks.forEach(b => {
    tx(s, b.n, b.x, b.y, 0.5, 0.25, { face: F.mono, size: 9, color: C.terra, spacing: 1.2 });
    tx(s, b.t, b.x, b.y + 0.28, 3.6, 0.4, { face: F.sans, size: 20, color: C.ink });
    tx(s, b.d, b.x, b.y + 0.72, 3.4, 0.3, { size: 11, color: C.muted });
  });

  // setas do loop
  line(s, 3.95, 3.38, 8.2, 3.38, C.terra, 1.2, true);
  line(s, 10.65, 3.62, 10.65, 4.9, C.terra, 1.2, true);
  line(s, 8.2, 5.32, 3.95, 5.32, C.terra, 1.2, true);
  line(s, 2.55, 4.9, 2.55, 3.62, C.terra, 1.2, true);

  tx(s, "10×/s", 5.78, 4.02, 1.55, 0.35, {
    face: F.mono, size: 15, color: C.terra, align: "center",
  });
  tx(s, "uma volta", 5.78, 4.33, 1.55, 0.22, {
    face: F.mono, size: 7.5, color: C.muted, align: "center", spacing: 1.0,
  });

  tx(s, "A cada volta, uma única célula da tabela é atualizada.", M, 6.45, 10.0, 0.35, {
    face: F.serif, size: 19, italic: true, color: C.muted,
  });

  footer(s); page(s, 8);
  s.addNotes(NOTES["08"]);
}

/* =====================================================================
   09 — EXPLORAR VS CONFIAR
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "08 · Exploração");

  titleLines(s, [
    { text: "No começo, ele chuta." },
    { text: "Depois, ele confia." },
  ], 1.05, { size: 48 });

  tx(s, "Se só chutar, nunca aprende. Se só repetir, nunca descobre algo melhor. A curiosidade cai aos poucos.", M, 2.55, 10.8, 0.65, {
    size: 14.5, color: C.muted, lh: 20,
  });

  addImage(s, "epsilon.png", M, 3.25, 6.45, 3.12,
    "Curva de exploração caindo de 1,00 para 0,13 ao longo de 200 episódios.");

  tx(s, "1,00", 7.85, 3.15, 2.2, 0.9, { face: F.display, size: 62, color: C.ink });
  tx(s, "EXPLORAÇÃO NO INÍCIO", 7.9, 4.02, 2.8, 0.25, { face: F.mono, size: 8, color: C.muted, spacing: 1.2 });
  tx(s, "→", 8.05, 4.45, 0.7, 0.5, { face: F.display, size: 30, color: C.terra });
  tx(s, "0,13", 8.75, 4.28, 2.2, 0.9, { face: F.display, size: 62, color: C.terra });
  tx(s, "APÓS 200 EPISÓDIOS", 8.8, 5.15, 2.8, 0.25, { face: F.mono, size: 8, color: C.muted, spacing: 1.2 });
  tx(s, "mínimo de 0,02 no código", 7.9, 5.62, 3.2, 0.25, { size: 10, color: C.muted });

  footer(s); page(s, 9);
  s.addNotes(NOTES["09"]);
}

/* =====================================================================
   10 — TREINAMENTO
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "09 · Treinamento");

  titleLines(s, [
    { text: "200 vidas em" },
    { text: "uma pista de mentira." },
  ], 1.05, { size: 48 });

  tx(s, "No simulador, errar é barato. Cada episódio começa em um ponto diferente; 15 passos fora da linha encerram a tentativa.", M, 2.7, 5.7, 0.9, {
    size: 14, color: C.muted, lh: 20,
  });

  tx(s, "200", M, 3.6, 2.4, 1.0, { face: F.display, size: 76, color: C.ink });
  tx(s, "EPISÓDIOS", M, 4.72, 2.2, 0.25, { face: F.mono, size: 8.5, color: C.muted, spacing: 1.4 });
  tx(s, "1.000", 3.1, 3.6, 2.4, 1.0, { face: F.display, size: 76, color: C.ink });
  tx(s, "PASSOS POR EPISÓDIO", 3.15, 4.72, 2.5, 0.25, { face: F.mono, size: 8.5, color: C.muted, spacing: 1.4 });

  // 200 pontos = 200 episódios
  const gx = 7.2, gy = 2.55, cols = 20, rows = 10, step = 0.245, d = 0.075;
  tx(s, "200 EPISÓDIOS = 200 PONTOS", gx, gy - 0.32, 5.4, 0.25, {
    face: F.mono, size: 8, color: C.muted, spacing: 1.2,
  });
  for (let i = 0; i < 200; i++) {
    const r = Math.floor(i / cols), c = i % cols;
    const mark = (i === 9 || i === 49 || i === 99 || i === 199);
    dot(s, gx + c * step, gy + r * step, d, mark ? C.terra : C.rule);
  }
  tx(s, "cada ponto é um episódio · terracota = snapshot mostrado", gx, 5.2, 5.4, 0.25, {
    face: F.mono, size: 7.8, color: C.muted,
  });

  line(s, M, 6.15, 12.48, 6.15, C.rule, 0.75);
  tx(s, "Depois, a mesma tabela vai para o robô de verdade.", M, 6.32, 9.0, 0.3, {
    face: F.serif, size: 19, italic: true, color: C.ink,
  });

  footer(s); page(s, 10);
  s.addNotes(NOTES["10"]);
}

/* =====================================================================
   11 — RESULTADO (DARK)
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s, C.dark);
  kicker(s, "10 · Resultado", true);
  tx(s, "200 EPISÓDIOS · RECOMPENSA MÉDIA", M, 1.45, 6.0, 0.25, {
    face: F.mono, size: 8.5, color: C.paperDim, spacing: 1.5,
  });

  tx(s, "-49", M, 1.95, 3.2, 1.5, { face: F.display, size: 118, color: C.paper });
  tx(s, "→", 3.85, 2.35, 1.2, 1.0, { face: F.display, size: 72, color: C.terra });
  tx(s, "+559", 5.0, 1.95, 5.4, 1.5, { face: F.display, size: 118, color: C.paper });

  tx(s, "primeiros 20 episódios  →  últimos 20 episódios", M, 3.55, 8.0, 0.3, {
    size: 12, color: C.paperDim,
  });

  tx(s, "A recompensa não é um prêmio. É o sinal de que ele passa mais tempo na linha.", M, 4.2, 6.6, 0.9, {
    size: 17, color: C.paper, lh: 24,
  });

  addImage(s, "sparkline_dark.png", 7.0, 4.05, 5.4, 0.95,
    "Tendência da recompensa média ao longo do treinamento.");

  line(s, M, 6.45, 12.48, 6.45, "3A342C", 0.75);
  tx(s, "O mesmo experimento, 200 vezes. A curva completa está no slide 13.", M, 6.6, 8.0, 0.3, {
    face: F.mono, size: 8.5, color: C.paperDim,
  });
  page(s, 11, true);
  s.addNotes(NOTES["11"]);
}

/* =====================================================================
   12 — COMPORTAMENTO
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "11 · Comportamento");

  titleLines(s, [
    { text: "Antes: 5 passos." },
    { text: "Depois: 120 de 120." },
  ], 1.05, { size: 46 });

  tx(s, "A mesma pista, o mesmo ponto de partida. À esquerda, uma política aleatória; à direita, a política aprendida.", M, 2.55, 10.5, 0.55, {
    size: 14, color: C.muted,
  });

  tx(s, "5", M, 3.18, 1.0, 0.8, { face: F.display, size: 54, color: C.terra });
  tx(s, "SEM APRENDIZADO", 1.7, 3.3, 1.6, 0.22, { face: F.mono, size: 7.5, color: C.muted, spacing: 1.0 });
  tx(s, "fora da linha", 1.7, 3.54, 1.5, 0.25, { size: 10.5, color: C.muted });

  tx(s, "120", M, 4.03, 1.65, 0.8, { face: F.display, size: 54, color: C.terra });
  tx(s, "COM A Q-TABLE", 2.62, 4.15, 1.0, 0.22, { face: F.mono, size: 7.5, color: C.muted, spacing: 1.0 });
  tx(s, "sobre a linha", 2.62, 4.39, 0.95, 0.25, { size: 10.5, color: C.muted });

  addImage(s, "online_strip.png", 3.75, 3.24, 8.7, 1.13,
    "Faixas de 120 passos: a política aleatória fica na linha 5 passos; a política aprendida, 120.");

  tx(s, "cada quadrado = 1 passo · terracota = sobre a linha", 3.75, 4.52, 7.0, 0.25, {
    face: F.mono, size: 8, color: C.muted,
  });

  line(s, M, 5.55, 12.48, 5.55, C.rule, 0.75);
  tx(s, "A política aprendida corrige o desvio antes de sair da linha. A aleatória sai em cinco passos.", M, 5.75, 10.0, 0.6, {
    face: F.serif, size: 20, italic: true, color: C.ink, lh: 26,
  });

  footer(s); page(s, 12);
  s.addNotes(NOTES["12"]);
}

/* =====================================================================
   13 — A CURVA
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "12 · Aprendizado");

  titleLines(s, [
    { text: "A curva não é lisa." },
    { text: "O comportamento mudou." },
  ], 1.02, { size: 44, lh: 0.62 });

  tx(s, "Cada linha clara é um episódio. A linha escura é a média móvel de 10.", M, 2.32, 10.5, 0.3, {
    size: 13, color: C.muted,
  });

  addImage(s, "learning_curve.png", M, 2.68, 10.35, 3.66,
    "Recompensa por episódio, com média móvel subindo de menos 49 para mais 559.");

  tx(s, "MELHOR EPISÓDIO  +822", M, 6.45, 3.2, 0.25, { face: F.mono, size: 8, color: C.muted, spacing: 1.2 });
  tx(s, "ÚLTIMOS 20  +559", 4.55, 6.45, 3.2, 0.25, { face: F.mono, size: 8, color: C.muted, spacing: 1.2 });
  tx(s, "200 EPISÓDIOS", 8.35, 6.45, 2.5, 0.25, { face: F.mono, size: 8, color: C.muted, spacing: 1.2 });

  footer(s); page(s, 13);
  s.addNotes(NOTES["13"]);
}

/* =====================================================================
   14 — DO SIMULADOR AO ROBÔ
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "13 · Arquitetura");

  titleLines(s, [
    { text: "Ensinar no PC." },
    { text: "Executar no robô." },
  ], 1.05, { size: 50 });

  tx(s, "A mesma Q-table pode ser treinada no Python ou dentro do Arduino. São 24 números — cabe na memória de um microcontrolador.", M, 2.6, 10.5, 0.65, {
    size: 14.5, color: C.muted, lh: 20,
  });

  const cols = [
    { n: "01", t: "SIMULADOR", d: "Python\n200 episódios\nQ-table 8×3", x: M },
    { n: "02", t: "PONTE", d: "USB 115200\nleitura → ação\nsem PC no robô", x: 4.55 },
    { n: "03", t: "ROBÔ", d: "Arduino / ESP32\nQ-table na RAM\ndecisão local", x: 8.25 },
  ];
  cols.forEach(c => {
    tx(s, c.n, c.x, 3.7, 0.6, 0.25, { face: F.mono, size: 10, color: C.terra, spacing: 1.2 });
    tx(s, c.t, c.x, 4.02, 3.2, 0.4, { face: F.sans, size: 20, color: C.ink });
    tx(s, c.d, c.x, 4.5, 3.2, 0.9, { face: F.mono, size: 9.5, color: C.muted, lh: 16 });
  });

  line(s, M, 3.55, 12.48, 3.55, C.rule, 0.75);
  [M, 4.55, 8.25].forEach(x => dot(s, x, 3.49, 0.11, C.terra));
  line(s, 4.05, 3.55, 4.45, 3.55, C.terra, 1.0, true);
  line(s, 7.75, 3.55, 8.15, 3.55, C.terra, 1.0, true);

  line(s, M, 6.1, 12.48, 6.1, C.rule, 0.75);
  tx(s, "O modo if/else fica como linha de base: repete, mas não aprende.", M, 6.28, 9.5, 0.3, {
    size: 12, color: C.muted,
  });
  tx(s, "4 arquiteturas · detalhes no apêndice", 9.7, 6.28, 2.8, 0.3, {
    face: F.mono, size: 7.5, color: C.muted, align: "right",
  });

  footer(s); page(s, 14);
  s.addNotes(NOTES["14"]);
}

/* =====================================================================
   15 — POR QUE IMPORTA
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "14 · O que fica");

  titleLines(s, [
    { text: "Aprender no lugar," },
    { text: "com poucos recursos." },
  ], 1.05, { size: 50 });

  tx(s, "O robô não precisa de internet, câmera ou um computador potente. Ele guarda 24 números e decide em tempo real.", M, 2.7, 10.6, 0.65, {
    size: 15, color: C.muted, lh: 21,
  });

  const items = [
    { t: "EDGE AI", d: "Decisão local, sem nuvem.", n: "01" },
    { t: "ADAPTAÇÃO", d: "O comportamento muda com a experiência.", n: "02" },
    { t: "EDUCAÇÃO", d: "Uma forma concreta de ensinar reforço.", n: "03" },
  ];
  items.forEach((it, i) => {
    const x = M + i * 3.95;
    line(s, x, 3.85, x + 3.35, 3.85, C.rule, 0.75);
    tx(s, it.n, x, 4.0, 0.5, 0.25, { face: F.mono, size: 8.5, color: C.terra, spacing: 1.2 });
    tx(s, it.t, x, 4.3, 3.3, 0.35, { face: F.sans, size: 17, color: C.ink });
    tx(s, it.d, x, 4.7, 3.2, 0.7, { size: 12.5, color: C.muted, lh: 18 });
  });

  tx(s, "Nem toda inteligência precisa da nuvem.", M, 6.25, 10.0, 0.5, {
    face: F.serif, size: 24, italic: true, color: C.terra,
  });

  footer(s); page(s, 15);
  s.addNotes(NOTES["15"]);
}

/* =====================================================================
   16 — LIMITES
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "15 · Honestidade");

  titleLines(s, [
    { text: "O que ele ainda" },
    { text: "não sabe." },
  ], 1.05, { size: 52 });

  tx(s, "8", 10.2, 1.35, 2.0, 2.2, { face: F.display, size: 150, color: C.watermark, align: "center" });
  tx(s, "→ ∞", 10.55, 3.55, 2.2, 0.7, { face: F.display, size: 56, color: C.terra, align: "center" });
  tx(s, "estados discretos  →  mundo contínuo", 9.55, 4.35, 3.4, 0.25, {
    face: F.mono, size: 7.5, color: C.muted, align: "center",
  });

  tag(s, "Limites", M, 2.7, C.terra);
  tx(s, "•  8 estados é pouco para curvas e cruzamentos.\n•  A linha ainda pode ser perdida.\n•  Simulador não é o chão de verdade.", M, 3.0, 5.4, 1.3, {
    size: 13.5, color: C.ink, lh: 24,
  });

  tag(s, "Próximos passos", 6.1, 2.7, C.terra);
  tx(s, "•  Mais sensores e mais resolução.\n•  Câmera e estados contínuos.\n•  Testar em pistas e pisos diferentes.", 6.1, 3.0, 5.4, 1.3, {
    size: 13.5, color: C.ink, lh: 24,
  });

  line(s, M, 5.55, 12.48, 5.55, C.rule, 0.75);
  tx(s, "O próximo passo é sair do discreto — e continuar aprendendo.", M, 5.75, 10.0, 0.5, {
    face: F.serif, size: 21, italic: true, color: C.muted,
  });

  footer(s); page(s, 16);
  s.addNotes(NOTES["16"]);
}

/* =====================================================================
   17 — FECHAMENTO (DARK)
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s, C.dark);
  kicker(s, "Fim · obrigado", true);

  tx(s, "Ele não nasceu", M, 1.25, 8.5, 0.95, { face: F.display, size: 62, color: C.paper });
  tx(s, "sabendo.", M, 2.02, 8.5, 0.95, { face: F.display, size: 62, color: C.paper });
  tx(s, "Aprendeu.", M, 3.08, 7.0, 1.1, { face: F.serif, size: 76, italic: true, color: C.terra });

  tx(s, "Agora veja o robô ao vivo.", M, 4.85, 6.5, 0.45, {
    face: F.serif, size: 26, italic: true, color: C.paper,
  });
  tx(s, "Pergunte a ele: e se a linha acabar?", M, 5.4, 6.5, 0.35, {
    size: 12, color: C.paperDim,
  });

  tx(s, "8 × 3", 8.65, 1.25, 4.0, 2.4, {
    face: F.display, size: 128, color: C.darkWatermark, align: "center",
  });
  tx(s, "24 NOTAS · UMA POLÍTICA", 9.35, 3.7, 3.0, 0.25, {
    face: F.mono, size: 8, color: "8E877A", spacing: 1.5, align: "center",
  });
  dot(s, 12.18, 2.38, 0.10, C.terra);

  line(s, M, 6.45, 12.48, 6.45, "3A342C", 0.75);
  tx(s, "OBRIGADO.", M, 6.62, 4.0, 0.25, { face: F.mono, size: 8.5, color: C.paperDim, spacing: 1.6 });
  page(s, 17, true);
  s.addNotes(NOTES["17"]);
}

/* =====================================================================
   APÊNDICE 1 — Q-LEARNING
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "Apêndice · Q-learning");

  tx(s, "A conta por trás da tabela.", M, 1.1, 9.5, 0.7, { face: F.display, size: 42, color: C.ink });

  tx(s, "Q[s,a]  ←  Q[s,a]  +  α · ( r  +  γ · max Q[s′,a′]  −  Q[s,a] )", M, 2.0, 11.5, 0.6, {
    face: F.mono, size: 19, color: C.ink,
  });

  const params = [
    { k: "α = 0,1", d: "taxa de aprendizado", sub: "quanto da novidade entra na nota" },
    { k: "γ = 0,9", d: "desconto do futuro", sub: "o quanto o amanhã importa" },
    { k: "ε  1,0 → 0,13", d: "exploração", sub: "curiosidade que cai a cada episódio" },
  ];
  params.forEach((p, i) => {
    const x = M + i * 3.95;
    line(s, x, 3.3, x + 3.35, 3.3, C.rule, 0.75);
    tx(s, p.k, x, 3.5, 3.2, 0.45, { face: F.mono, size: 20, color: C.terra });
    tx(s, p.d, x, 4.0, 3.2, 0.3, { face: F.sans, size: 13, color: C.ink });
    tx(s, p.sub, x, 4.32, 3.2, 0.6, { size: 11, color: C.muted, lh: 16 });
  });

  tx(s, "Recompensa:  centro +1,0  ·  lateral −0,5  ·  perdeu −3,0", M, 5.55, 10.5, 0.3, {
    face: F.mono, size: 10, color: C.muted,
  });
  tx(s, "O Q-update acontece antes da próxima escolha. A tabela é atualizada uma célula por passo.", M, 5.95, 10.5, 0.6, {
    size: 12, color: C.muted, lh: 18,
  });
  tx(s, "SUTTON & BARTO, 2018 · CAP. 6", M, 6.55, 6.0, 0.22, {
    face: F.mono, size: 7.5, color: C.muted, spacing: 1.2,
  });

  footer(s); page(s, 18);
  s.addNotes(NOTES["18"]);
}

/* =====================================================================
   APÊNDICE 2 — SE O ROBÔ FOSSE UM BICHO
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "Apêndice · Analogia");

  tx(s, "Se o robô fosse um bicho.", M, 1.05, 11.2, 0.85, {
    face: F.display, size: 50, color: C.ink,
  });
  tx(s, "O instinto é uma tabela.", M, 1.88, 9.0, 0.55, {
    face: F.serif, size: 27, italic: true, color: C.terra,
  });

  tx(s, "Um cachorro não nasce sabendo onde tem comida. Ele cheira, escolhe um caminho, ganha um petisco ou um susto — e ajusta o instinto.", M, 2.65, 4.3, 1.0, {
    size: 14, color: C.muted, lh: 20,
  });
  tx(s, "O robô faz o mesmo. Em vez de focinho, tem sensores. Em vez de patas, motores. Em vez de instinto, uma tabela de 24 notas.", M, 3.55, 4.3, 1.0, {
    size: 14, color: C.muted, lh: 20,
  });
  tx(s, "O robô não sonha. Ele consulta.", M, 4.85, 4.2, 0.4, {
    face: F.serif, size: 18, italic: true, color: C.terra,
  });

  const rows = [
    ["focinho", "3 sensores IR"],
    ["patas", "2 motores DC"],
    ["instinto", "Q-table 8 × 3"],
    ["petisco / susto", "recompensa (+1 / −3)"],
    ["uma tarde", "um episódio"],
    ["curiosidade", "ε (exploração)"],
    ["paciência", "γ (futuro)"],
  ];
  const tX = 5.55, tW = 6.9, lW = 2.05, rW = 4.85, y0 = 2.45, rh = 0.44;
  tx(s, "CACHORRO", tX, 2.18, lW, 0.22, { face: F.mono, size: 8, color: C.terra, spacing: 1.3 });
  tx(s, "ROBÔ", tX + lW, 2.18, rW, 0.22, { face: F.mono, size: 8, color: C.terra, spacing: 1.3 });
  line(s, tX, y0, tX + tW, y0, C.ink, 0.8);
  rows.forEach((r, i) => {
    const yy = y0 + 0.13 + i * rh;
    tx(s, r[0], tX, yy, lW, 0.3, { face: F.serif, size: 13.5, italic: true, color: C.ink });
    tx(s, r[1], tX + lW, yy, rW, 0.3, { face: F.mono, size: 10, color: C.ink });
    line(s, tX, yy + 0.38, tX + tW, yy + 0.38, C.rule, 0.5);
  });

  rect(s, M, 5.98, 11.63, 0.72, C.sandLight);
  tx(s, "A EQUAÇÃO, TRADUZIDA", 1.05, 6.05, 3.5, 0.2, {
    face: F.mono, size: 7.2, color: C.terra, spacing: 1.3,
  });
  tx(s, "nova nota  =  nota antiga  +  10% × ( petisco agora  +  90% da melhor nota futura  −  nota antiga )", 1.05, 6.24, 11.1, 0.32, {
    face: F.mono, size: 11.2, color: C.ink,
  });

  footer(s); page(s, 19);
  s.addNotes(NOTES["19"]);
}

/* =====================================================================
   APÊNDICE 2 — ARQUITETURAS
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "Apêndice · Arquiteturas");

  tx(s, "Quatro formas de montar.", M, 1.1, 9.5, 0.7, { face: F.display, size: 42, color: C.ink });
  tx(s, "A mesma ideia, distribuída de formas diferentes entre PC e microcontrolador.", M, 1.85, 10.5, 0.35, {
    size: 13, color: C.muted,
  });

  const rows = [
    ["1 · if/else", "físico", "regras fixas", "não", "referência"],
    ["2 · sim.py", "simulado", "Python", "sim", "treino rápido"],
    ["3 · onboard", "físico", "Arduino", "sim", "robô autônomo"],
    ["4 · serial", "simulado", "Arduino / ESP32", "sim", "valida no hardware"],
  ];
  const headers = ["MODO", "AMBIENTE", "AGENTE", "APRENDE?", "PARA QUE SERVE"];
  const xs = [M, 2.55, 4.65, 7.35, 9.0];
  const widths = [1.6, 2.0, 2.6, 1.5, 3.4];

  line(s, M, 2.55, 12.48, 2.55, C.ink, 1.0);
  headers.forEach((h, j) => tx(s, h, xs[j], 2.65, widths[j], 0.25, {
    face: F.mono, size: 7.5, color: C.muted, spacing: 1.0,
  }));

  rows.forEach((r, i) => {
    const y = 3.02 + i * 0.82;
    line(s, M, y, 12.48, y, C.rule, 0.6);
    r.forEach((cell, j) => tx(s, cell, xs[j], y + 0.2, widths[j], 0.35, {
      face: j === 0 ? F.mono : F.body,
      size: j === 0 ? 9.5 : 11,
      color: i === 2 && j === 0 ? C.terra : C.ink,
      bold: i === 2 && j === 0,
    }));
  });
  line(s, M, 6.3, 12.48, 6.3, C.ink, 1.0);

  tx(s, "O modo 4 valida a Q-table no hardware antes de soltar o robô autônomo.", M, 6.45, 10.0, 0.3, {
    face: F.serif, size: 16, italic: true, color: C.muted,
  });

  footer(s); page(s, 20);
  s.addNotes(NOTES["20"]);
}

/* =====================================================================
   APÊNDICE 3 — NÚMEROS
   ===================================================================== */
{
  const s = pptx.addSlide();
  bg(s);
  kicker(s, "Apêndice · Números");

  tx(s, "O experimento em números.", M, 1.1, 9.5, 0.7, { face: F.display, size: 42, color: C.ink });

  tag(s, "Parâmetros", M, 2.15, C.terra);
  const left = [
    ["200", "episódios"],
    ["1.000", "passos por episódio"],
    ["8 × 3", "estados × ações"],
    ["α 0,1 · γ 0,9", "aprendizado e desconto"],
  ];
  left.forEach((r, i) => {
    const y = 2.55 + i * 0.8;
    tx(s, r[0], M, y, 3.0, 0.4, { face: F.mono, size: 17, color: C.ink });
    tx(s, r[1], 3.1, y + 0.1, 3.0, 0.3, { size: 12, color: C.muted });
    line(s, M, y + 0.55, 6.0, y + 0.55, C.rule, 0.6);
  });

  tag(s, "Resultados", 7.0, 2.15, C.terra);
  const right = [
    ["-49 → +559", "recompensa média"],
    ["+822", "melhor episódio"],
    ["5 → 120", "passos na linha"],
    ["24", "notas na Q-table"],
  ];
  right.forEach((r, i) => {
    const y = 2.55 + i * 0.8;
    tx(s, r[0], 7.0, y, 2.8, 0.4, { face: F.mono, size: 17, color: i === 0 ? C.terra : C.ink });
    tx(s, r[1], 9.95, y + 0.1, 2.6, 0.3, { size: 12, color: C.muted });
    line(s, 7.0, y + 0.55, 12.48, y + 0.55, C.rule, 0.6);
  });

  line(s, M, 6.05, 12.48, 6.05, C.rule, 0.75);
  tx(s, "Números do simulador. No robô real, atrito, ruído e bateria mudam o jogo.", M, 6.2, 10.5, 0.3, {
    face: F.serif, size: 17, italic: true, color: C.muted,
  });

  footer(s); page(s, 21);
  s.addNotes(NOTES["21"]);
}

pptx.writeFile({ fileName: "Como_um_robo_aprende.pptx" })
  .then(f => console.log("ok", f))
  .catch(e => { console.error(e); process.exit(1); });
