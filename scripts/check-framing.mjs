#!/usr/bin/env node
// Sweep a render for framing faults across the WHOLE film.
//
// Two uses:
//   1. before reframing - report the widest content, which sets the largest
//      safe scale for a narrower crop
//   2. after reframing - confirm nothing drifted off centre and nothing is
//      clipped by the new edges
//
//   node check-framing.mjs render.mp4 --w 1920 --h 1080 [--every 4]
//   node check-framing.mjs render.mp4 --w 1080 --h 1920 --fullbleed 216-231,854-865
//
// --fullbleed lists frames that are MEANT to fill or overflow the frame (a slam
// zoom, a wipe covering frame, a full-bleed texture card). Without it they are
// reported as faults.
//
// Written after shipping a build that was verified on a single frame and was
// wrong on every other one. One frame is not a check.
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const [, , file, ...rest] = process.argv;
const arg = (k, d) => { const i = rest.indexOf("--" + k); return i >= 0 ? rest[i + 1] : d; };
const W = Number(arg("w")), H = Number(arg("h"));
const EVERY = Number(arg("every", 4));
if (!file || !W || !H) { console.error("usage: check-framing.mjs <render.mp4> --w N --h N [--every 4] [--fullbleed a-b,c-d]"); process.exit(1); }

const skip = new Set();
for (const part of (arg("fullbleed", "") || "").split(",").filter(Boolean)) {
  const [a, b] = part.split("-").map(Number);
  for (let f = a; f <= (b ?? a); f++) skip.add(f);
}

// decode small - we want geometry, not detail
const sw = W >= H ? 240 : 135, sh = Math.round(sw * H / W);
const raw = path.join(os.tmpdir(), `framing_${process.pid}.raw`);
execFileSync("ffmpeg", ["-v", "error", "-y", "-i", file, "-vf",
  `scale=${sw}:${sh},select=not(mod(n\\,${EVERY}))`, "-vsync", "0",
  "-pix_fmt", "rgb24", "-f", "rawvideo", raw]);
const buf = fs.readFileSync(raw);
fs.unlinkSync(raw);
const n = Math.floor(buf.length / (sw * sh * 3));

const median = a => { const b = [...a].sort((x, y) => x - y); return b[b.length >> 1]; };
let rows = [], edge = [], widest = { w: -1, f: -1 };

for (let i = 0; i < n; i++) {
  const f = i * EVERY;
  const off = i * sw * sh * 3;
  const g = new Float64Array(sw * sh);
  for (let p = 0; p < sw * sh; p++) {
    g[p] = (buf[off + p * 3] + buf[off + p * 3 + 1] + buf[off + p * 3 + 2]) / 3;
  }
  const bg = median(g);
  let x0 = 1e9, x1 = -1, y0 = 1e9, y1 = -1;
  for (let y = 0; y < sh; y++) for (let x = 0; x < sw; x++) {
    if (Math.abs(g[y * sw + x] - bg) > 28) {
      if (x < x0) x0 = x; if (x > x1) x1 = x;
      if (y < y0) y0 = y; if (y > y1) y1 = y;
    }
  }
  if (x1 < 0) continue;                     // blank frame - a real part of the edit
  const wpx = (x1 - x0 + 1) / sw * W;
  if (!skip.has(f)) {
    if (wpx > widest.w) widest = { w: Math.round(wpx), f };
    rows.push([Math.abs((x0 + x1) / 2 / sw * W - W / 2), Math.abs((y0 + y1) / 2 / sh * H - H / 2), f]);
    if (x0 <= 0 || x1 >= sw - 1) edge.push(f);
  }
}

const mean = a => a.reduce((s, v) => s + v, 0) / (a.length || 1);
rows.sort((a, b) => b[0] - a[0]);
console.log(`${file}  ${W}x${H}`);
console.log(`  ${rows.length} frames checked (every ${EVERY}), ${skip.size} excluded as full-bleed\n`);
console.log(`  widest content        ${widest.w} px at f${widest.f}`);
console.log(`  mean offset from centre   x ${mean(rows.map(r => r[0])).toFixed(1)} px   y ${mean(rows.map(r => r[1])).toFixed(1)} px`);
console.log(`  worst horizontal offset   ${rows[0][0].toFixed(0)} px at f${rows[0][2]}`);
console.log(`  frames touching a side edge: ${edge.length}${edge.length ? "  " + edge.slice(0, 8).join(", ") : "  - none"}`);
console.log(`\n  largest safe scale for a narrower crop, from the widest content:`);
for (const target of [1080, 1920]) {
  for (const m of [40, 80]) {
    console.log(`    fit ${target} wide with ${m}px margin -> ${((target - 2 * m) / widest.w).toFixed(3)}x`);
  }
}
console.log(`\n  A worst-offset frame is usually a line mid-reveal, not a fault.`);
console.log(`  Frames touching an edge that are NOT in --fullbleed are faults.`);
