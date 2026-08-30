#!/usr/bin/env node
// Identify a reference's typeface by GLYPH OVERLAP, not by column profile.
//
// Column-profile correlation cannot tell fonts apart - it mostly measures
// stroke weight and spacing, and on real material it ranked a visibly wrong
// face first. Cropping both renders to their ink boxes, normalising size, and
// measuring intersection-over-union of the ink compares letterform SHAPE, which
// is what actually differs between faces.
//
// Calibration from a known-wrong substitution: a face fitted to within 0.05% of
// the reference's ink mass still scored 32% IoU. Treat < 50% as wrong, 50-75%
// as a near relative, > 85% as the face (or a clone of it).
//
//   node font-identify.mjs <fontsDir> "the string" <refFrame.raw> \
//        --w 1276 --h 718 --box x0,y0,x1,y1 [--weight 500]
//
// refFrame.raw is a rgb24 dump of one reference frame:
//   ffmpeg -i ref.mp4 -vf "select=eq(n\,700)" -frames:v 1 -vsync 0 \
//          -pix_fmt rgb24 -f rawvideo f700.raw
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const [, , fontsDir, text, refRaw, ...rest] = process.argv;
const arg = (k, d) => { const i = rest.indexOf("--" + k); return i >= 0 ? rest[i + 1] : d; };
const W = Number(arg("w", 1276)), H = Number(arg("h", 718));
const WEIGHT = arg("weight", "500");
const BOX = (arg("box", "") || "").split(",").map(Number);
if (!fontsDir || !text || !refRaw || BOX.length !== 4) {
  console.error('usage: font-identify.mjs <fontsDir> "text" <ref.raw> --box x0,y0,x1,y1 [--w] [--h] [--weight]');
  process.exit(1);
}

const fonts = fs.readdirSync(fontsDir).filter(f => /\.ttf$/i.test(f)).map(f => f.replace(/\.ttf$/i, ""));
if (!fonts.length) { console.error("no .ttf in " + fontsDir); process.exit(1); }

const ROW = 96, SIZE = 76;
const CH = Math.max(H, fonts.length * ROW + 40);
const faces = fonts.map(f => `@font-face{font-family:'${f}';src:url('f/${f}.ttf') format('truetype');font-weight:1 999;}`).join("\n");
const rows = fonts.map((f, i) =>
  `<div class="r" style="font-family:'${f}';top:${20 + i * ROW}px">${text}</div>`).join("\n");

const dir = fs.mkdtempSync(path.join(process.env.TEMP || "/tmp", "fontid"));
// the renderer will not load file:// URLs, so the faces have to sit beside the page
fs.mkdirSync(path.join(dir, "f"));
for (const f of fonts) fs.copyFileSync(path.join(fontsDir, f + ".ttf"), path.join(dir, "f", f + ".ttf"));
fs.writeFileSync(path.join(dir, "index.html"), `<!doctype html><html><head><meta charset="utf-8"><title>fid</title><style>
${faces}
html,body{margin:0;background:#fff}
#fid{position:relative;width:${W}px;height:${CH}px;background:#fff;overflow:hidden}
.r{position:absolute;left:0;right:0;text-align:center;color:#000;font-size:${SIZE}px;
   font-weight:${WEIGHT};white-space:nowrap;letter-spacing:0}
</style></head><body>
<div id="fid" data-composition-id="fid" data-fps="30" data-duration="0.2" data-width="${W}" data-height="${CH}">
<div class="clip" data-start="0" data-duration="0.19" style="position:absolute;inset:0">${rows}</div>
</div><script>window.__timelines=[];<\/script></body></html>`);
for (const f of ["hyperframes.json", "package.json"]) {
  const src = path.join(process.cwd(), f);
  if (fs.existsSync(src)) fs.copyFileSync(src, path.join(dir, f));
}
execFileSync("npx", ["hyperframes", "render", "-q", "high", "--crf", "12", "-o", "o.mp4"],
  { cwd: dir, stdio: "ignore", shell: true });
execFileSync("ffmpeg", ["-v", "error", "-y", "-i", path.join(dir, "o.mp4"), "-vf", "select=eq(n\\,2)",
  "-frames:v", "1", "-vsync", "0", "-pix_fmt", "rgb24", "-f", "rawvideo", path.join(dir, "c.raw")]);

const gray = (buf, w, h) => {
  const g = new Float64Array(w * h);
  for (let i = 0; i < w * h; i++) g[i] = (buf[i * 3] + buf[i * 3 + 1] + buf[i * 3 + 2]) / 3;
  return g;
};
const maskBox = (g, w, y0, y1, thr = 140) => {
  let x0 = 1e9, x1 = -1, ya = 1e9, yb = -1;
  for (let y = y0; y < y1; y++) for (let x = 0; x < w; x++)
    if (g[y * w + x] < thr) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < ya) ya = y; if (y > yb) yb = y; }
  return { x0, x1, y0: ya, y1: yb };
};
// resample a cropped binary mask onto a fixed grid, so size never confounds shape
const N = 260, M = 90;
const norm = (g, w, b) => {
  const out = new Uint8Array(N * M), bw = b.x1 - b.x0 + 1, bh = b.y1 - b.y0 + 1;
  for (let j = 0; j < M; j++) for (let i = 0; i < N; i++) {
    const sx = b.x0 + Math.floor(i * bw / N), sy = b.y0 + Math.floor(j * bh / M);
    out[j * N + i] = g[sy * w + sx] < 140 ? 1 : 0;
  }
  return out;
};

const refG = gray(fs.readFileSync(refRaw), W, H);
const refN = norm(refG, W, { x0: BOX[0], y0: BOX[1], x1: BOX[2], y1: BOX[3] });
const capG = gray(fs.readFileSync(path.join(dir, "c.raw")), W, CH);

const res = [];
for (let i = 0; i < fonts.length; i++) {
  const b = maskBox(capG, W, 20 + i * ROW - 14, 20 + i * ROW + ROW - 10);
  if (b.x1 < 0) continue;
  const cn = norm(capG, W, b);
  let inter = 0, uni = 0;
  for (let k = 0; k < N * M; k++) { const a = refN[k], c = cn[k]; if (a | c) uni++; if (a & c) inter++; }
  res.push({ font: fonts[i], iou: inter / uni, w: b.x1 - b.x0 + 1, h: b.y1 - b.y0 + 1 });
}
res.sort((a, b) => b.iou - a.iou);
console.log(`glyph IoU vs the reference   (string "${text}", weight ${WEIGHT})\n`);
console.log(`${"font".padEnd(20)}${"IoU".padStart(8)}${"aspect".padStart(9)}`);
const refAsp = (BOX[2] - BOX[0] + 1) / (BOX[3] - BOX[1] + 1);
for (const r of res) console.log(`${r.font.padEnd(20)}${(r.iou * 100).toFixed(1).padStart(7)}%${(r.w / r.h).toFixed(2).padStart(9)}`);
console.log(`\nreference aspect ${refAsp.toFixed(2)}`);
console.log(`best: ${res[0].font} at ${(res[0].iou * 100).toFixed(1)}%`);
console.log(res[0].iou > 0.85 ? "  -> this is the face (or a clone)"
  : res[0].iou > 0.5 ? "  -> a near relative; expect a real ceiling on type-heavy cards"
  : "  -> none of these is it. Reconstruct the face, or quote the ceiling.");
fs.rmSync(dir, { recursive: true, force: true });
