#!/usr/bin/env node
// Report every element on one frame: horizontal bands, and the column runs
// inside a band. This is the measurement that actually rebuilds a card.
//
//   node card-elements.mjs ref.mp4 --frame 664 --w 1276 --h 718
//   node card-elements.mjs ref.mp4 --frame 664 --w 1276 --h 718 --band 220,480
//
// Two rules learned the hard way, both encoded here:
//
// 1. NEVER isolate an element with a colour mask alone. A mask for one element
//    silently swallows its neighbours, and constraining the mask by x or y to
//    stop that CLIPS the element and reports it at the wrong size. On real
//    material that put two cards on top of each other. Column-occupancy runs
//    inside a band separate adjacent elements without either failure.
//
// 2. The colour it prints for a band is the median over ANTI-ALIASED ink, which
//    reads far lighter than the real colour. Setting text to a printed median
//    of #615F62 washed out type that is actually #1B191B. Treat it as a hint.
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const [, , file, ...rest] = process.argv;
const arg = (k, d) => { const i = rest.indexOf("--" + k); return i >= 0 ? rest[i + 1] : d; };
const W = Number(arg("w", 1276)), H = Number(arg("h", 718));
const FRAME = Number(arg("frame", 0));
const THR = Number(arg("thr", 247));           // "not background" cutoff
const band = (arg("band", "") || "").split(",").map(Number);
if (!file) { console.error("usage: card-elements.mjs <video> --frame N --w N --h N [--band y0,y1] [--thr 247]"); process.exit(1); }

const raw = path.join(os.tmpdir(), `cardel_${process.pid}.raw`);
execFileSync("ffmpeg", ["-v", "error", "-y", "-i", file, "-vf", `select=eq(n\\,${FRAME})`,
  "-frames:v", "1", "-vsync", "0", "-pix_fmt", "rgb24", "-f", "rawvideo", raw]);
const buf = fs.readFileSync(raw);
fs.unlinkSync(raw);

const px = (x, y) => { const i = (y * W + x) * 3; return [buf[i], buf[i + 1], buf[i + 2]]; };
const lum = (x, y) => { const p = px(x, y); return (p[0] + p[1] + p[2]) / 3; };
// background = the modal corner value, so this works on white and dark cards
const corners = [[8, 8], [W - 9, 8], [8, H - 9], [W - 9, H - 9]].map(([x, y]) => lum(x, y));
const bg = corners.sort((a, b) => a - b)[2];
const isInk = (x, y) => Math.abs(lum(x, y) - bg) > (255 - THR) + 6;

function bands(y0, y1) {
  const out = []; let s = null;
  for (let y = y0; y < y1; y++) {
    let c = 0;
    for (let x = 0; x < W; x++) if (isInk(x, y)) { c++; if (c > 3) break; }
    const on = c > 3;
    if (on && s === null) s = y;
    else if (!on && s !== null) { if (y - s > 3) out.push([s, y - 1]); s = null; }
  }
  if (s !== null) out.push([s, y1 - 1]);
  return out;
}
function extent(y0, y1) {
  let x0 = 1e9, x1 = -1, n = 0, r = 0, g = 0, b = 0;
  for (let y = y0; y <= y1; y++) for (let x = 0; x < W; x++) if (isInk(x, y)) {
    if (x < x0) x0 = x; if (x > x1) x1 = x;
    const p = px(x, y); r += p[0]; g += p[1]; b += p[2]; n++;
  }
  return { x0, x1, n, col: n ? [r / n, g / n, b / n].map(v => Math.round(v)) : [0, 0, 0] };
}
// column-occupancy runs: the reliable way to split elements sitting side by side
function runs(y0, y1, minGap = 12) {
  const occ = new Uint8Array(W);
  for (let x = 0; x < W; x++) {
    let c = 0;
    for (let y = y0; y <= y1; y++) if (isInk(x, y)) c++;
    occ[x] = c > Math.max(2, (y1 - y0) * 0.03) ? 1 : 0;
  }
  const out = []; let s = null;
  for (let x = 0; x < W; x++) {
    if (occ[x] && s === null) s = x;
    else if (!occ[x] && s !== null) { if (x - s > minGap) out.push([s, x - 1]); s = null; }
  }
  if (s !== null) out.push([s, W - 1]);
  return out;
}

console.log(`${file}  frame ${FRAME}  ${W}x${H}   background luma ${bg.toFixed(0)}\n`);
if (band.length === 2) {
  const r = runs(band[0], band[1]);
  console.log(`column runs in y ${band[0]}-${band[1]}:`);
  for (const [a, b] of r) console.log(`   x ${String(a).padStart(4)}-${String(b).padStart(4)}  (w ${b - a + 1})`);
  console.log(`\n${r.length} element(s) side by side. Gaps between runs are real gaps -`);
  console.log(`a colour mask would have merged or clipped them.`);
} else {
  const bs = bands(0, H);
  console.log(`${"band".padEnd(22)}${"x".padStart(14)}${"width".padStart(7)}  mean ink colour`);
  for (const [a, b] of bs) {
    const e = extent(a, b);
    if (e.x1 < 0) continue;
    const hex = "#" + e.col.map(v => v.toString(16).padStart(2, "0")).join("");
    console.log(`y ${String(a).padStart(3)}-${String(b).padStart(3)} (h ${String(b - a + 1).padStart(3)})   ` +
      `${String(e.x0).padStart(4)}-${String(e.x1).padStart(4)}${String(e.x1 - e.x0 + 1).padStart(7)}  ${hex}  (a median over AA - the real ink is darker)`);
  }
  console.log(`\nRe-run with --band y0,y1 on any band holding more than one element.`);
}
