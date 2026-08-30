#!/usr/bin/env node
// Track what a card DOES across its frames: focus, ink, size and position.
// Settled geometry is only half a card - most of the residual on a graded build
// lives in the entry, and this is what finds it.
//
//   node card-motion.mjs ref.mp4 --from 519 --to 556 --w 1276 --h 718
//   node card-motion.mjs ref.mp4 --from 519 --to 556 --w 1276 --h 718 --cmp mine.mp4
//
// Columns, and what a change in each one means:
//
//   sharp  mean |gradient|. RISING through the first frames means the card
//          enters DEFOCUSED and resolves - a blur entry, easy to miss by eye and
//          common in this style. Flat means no blur.
//   ink    pixels differing from the background. Rising = elements arriving.
//          A settled difference against the reference means type is the wrong
//          SIZE, not the wrong position.
//   w/h    ink bounding box. Growing together = a push-in. Growing apart = an
//          element arriving.
//   cy     ink centroid. Drifting with a steady box = the card is scrolling.
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const [, , file, ...rest] = process.argv;
const arg = (k, d) => { const i = rest.indexOf("--" + k); return i >= 0 ? rest[i + 1] : d; };
const W = Number(arg("w", 1276)), H = Number(arg("h", 718));
const A = Number(arg("from", 0)), B = Number(arg("to", 0));
const STEP = Number(arg("step", 3));
const CMP = arg("cmp", null);
if (!file || !B) { console.error("usage: card-motion.mjs <video> --from N --to N --w N --h N [--step 3] [--cmp other.mp4]"); process.exit(1); }

function load(f) {
  const raw = path.join(os.tmpdir(), `cardmo_${process.pid}_${path.basename(f)}.raw`);
  execFileSync("ffmpeg", ["-v", "error", "-y", "-i", f, "-vf", `select='between(n,${A},${B})'`,
    "-vsync", "0", "-pix_fmt", "rgb24", "-f", "rawvideo", raw]);
  const buf = fs.readFileSync(raw);
  fs.unlinkSync(raw);
  return buf;
}
function probe(buf, k) {
  const off = k * W * H * 3;
  const g = new Float64Array(W * H);
  for (let i = 0; i < W * H; i++) {
    const j = off + i * 3;
    g[i] = (buf[j] + buf[j + 1] + buf[j + 2]) / 3;
  }
  let grad = 0;
  for (let y = 0; y < H; y++) for (let x = 1; x < W; x++) grad += Math.abs(g[y * W + x] - g[y * W + x - 1]);
  for (let y = 1; y < H; y++) for (let x = 0; x < W; x++) grad += Math.abs(g[y * W + x] - g[(y - 1) * W + x]);
  grad /= (W * H * 2);
  const bgv = g[8 * W + 8];
  let ink = 0, x0 = 1e9, x1 = -1, y0 = 1e9, y1 = -1, sy = 0;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    if (Math.abs(g[y * W + x] - bgv) > 55) {
      ink++; sy += y;
      if (x < x0) x0 = x; if (x > x1) x1 = x;
      if (y < y0) y0 = y; if (y > y1) y1 = y;
    }
  }
  return { grad, ink, w: x1 < 0 ? 0 : x1 - x0 + 1, h: y1 < 0 ? 0 : y1 - y0 + 1, cy: ink ? sy / ink : 0 };
}

const a = load(file);
const b = CMP ? load(CMP) : null;
const n = Math.floor(a.length / (W * H * 3));
console.log(CMP ? `${path.basename(file)}  vs  ${path.basename(CMP)}\n` : `${path.basename(file)}\n`);
console.log(CMP
  ? `${"f".padStart(5)}${"sharp".padStart(9)}${"sharp'".padStart(9)}${"ink".padStart(9)}${"ink'".padStart(9)}${"cy".padStart(7)}${"cy'".padStart(7)}`
  : `${"f".padStart(5)}${"sharp".padStart(9)}${"ink".padStart(9)}${"w".padStart(6)}${"h".padStart(6)}${"cy".padStart(7)}`);
for (let k = 0; k < n; k += STEP) {
  const p = probe(a, k);
  if (CMP && k < Math.floor(b.length / (W * H * 3))) {
    const q = probe(b, k);
    console.log(`${String(A + k).padStart(5)}${p.grad.toFixed(3).padStart(9)}${q.grad.toFixed(3).padStart(9)}` +
      `${String(p.ink).padStart(9)}${String(q.ink).padStart(9)}${p.cy.toFixed(0).padStart(7)}${q.cy.toFixed(0).padStart(7)}`);
  } else {
    console.log(`${String(A + k).padStart(5)}${p.grad.toFixed(3).padStart(9)}${String(p.ink).padStart(9)}` +
      `${String(p.w).padStart(6)}${String(p.h).padStart(6)}${p.cy.toFixed(0).padStart(7)}`);
  }
}
console.log(`\n  sharp rising over the first frames -> the card enters defocused`);
console.log(`  ink settling below the reference   -> your type is undersized`);
console.log(`  cy drifting with a steady box      -> the card scrolls`);
