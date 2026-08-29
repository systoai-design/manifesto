#!/usr/bin/env node
// Per-frame measurement of a raw.bin produced by extract.mjs.
//
//   node measure.mjs <dir>
//
// Writes <dir>/motion.json (per-frame scalars) and <dir>/profiles.bin
// (Uint16 column+row ink profiles, for word-level segmentation).
//
// Metrics per frame:
//   bgL      background luma (median of corner patches) — detects card flips
//   meanL    mean luma
//   ink      count of pixels differing from background (the "content")
//   bbox     [x0,y0,x1,y1] of ink, in source pixels
//   cx,cy    ink centroid, in source pixels
//   edge     mean |gradient| over ink pixels — DROPS when motion blur smears
//            an otherwise-sharp frame, so this is the motion-blur detector
//   sat      mean saturation over ink pixels (colored vs monochrome cards)
//   hueL/M/R mean hue of saturated ink in left/middle/right thirds
//            (tracks gradient sweeps across a headline)

import fs from 'node:fs';
import path from 'node:path';

const dir = process.argv[2];
if (!dir) { console.error('usage: measure.mjs <dir>'); process.exit(1); }
const meta = JSON.parse(fs.readFileSync(path.join(dir, 'meta.json'), 'utf8'));
const { w: W, h: H, frames, fps } = meta;
const FRAME = W * H * 3;
const SX = meta.sourceW / W, SY = meta.sourceH / H;

const COLBINS = 160, ROWBINS = 90;
const colW = W / COLBINS, rowH = H / ROWBINS;

const fd = fs.openSync(path.join(dir, 'raw.bin'), 'r');
const buf = Buffer.allocUnsafe(FRAME);
const luma = new Float32Array(W * H);
const profiles = new Uint16Array(frames * (COLBINS + ROWBINS));

const INK_T = 42;   // luma delta from background that counts as content
const out = [];

for (let f = 0; f < frames; f++) {
  fs.readSync(fd, buf, 0, FRAME, f * FRAME);

  for (let i = 0, p = 0; i < W * H; i++, p += 3) {
    luma[i] = 0.2126 * buf[p] + 0.7152 * buf[p + 1] + 0.0722 * buf[p + 2];
  }

  // Background = median of four corner patches (robust to a centered subject).
  const patch = [];
  const PS = Math.max(4, Math.round(Math.min(W, H) * 0.05));
  for (const [ox, oy] of [[0, 0], [W - PS, 0], [0, H - PS], [W - PS, H - PS]]) {
    let s = 0;
    for (let y = oy; y < oy + PS; y++) for (let x = ox; x < ox + PS; x++) s += luma[y * W + x];
    patch.push(s / (PS * PS));
  }
  patch.sort((a, b) => a - b);
  const bgL = (patch[1] + patch[2]) / 2;

  let ink = 0, sumL = 0, x0 = W, y0 = H, x1 = -1, y1 = -1, sx = 0, sy = 0;
  let edgeSum = 0, edgeN = 0, satSum = 0;
  const hueAcc = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];   // [r,g,b] sums per third
  const hueN = [0, 0, 0];
  const cbase = f * (COLBINS + ROWBINS);

  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const i = y * W + x;
      const L = luma[i];
      sumL += L;
      if (Math.abs(L - bgL) <= INK_T) continue;
      ink++;
      if (x < x0) x0 = x;
      if (x > x1) x1 = x;
      if (y < y0) y0 = y;
      if (y > y1) y1 = y;
      sx += x; sy += y;
      profiles[cbase + Math.min(COLBINS - 1, (x / colW) | 0)]++;
      profiles[cbase + COLBINS + Math.min(ROWBINS - 1, (y / rowH) | 0)]++;

      // gradient magnitude (forward difference, clamped at edges)
      if (x + 1 < W && y + 1 < H) {
        edgeSum += Math.abs(luma[i + 1] - L) + Math.abs(luma[i + W] - L);
        edgeN++;
      }
      const p = i * 3, r = buf[p], g = buf[p + 1], b = buf[p + 2];
      const mx = Math.max(r, g, b), mn = Math.min(r, g, b);
      const sat = mx ? (mx - mn) / mx : 0;
      satSum += sat;
      if (sat > 0.30 && mx > 60) {
        const t = x < W / 3 ? 0 : x < 2 * W / 3 ? 1 : 2;
        hueAcc[t][0] += r; hueAcc[t][1] += g; hueAcc[t][2] += b; hueN[t]++;
      }
    }
  }

  const rec = {
    i: f,
    t: +(f / fps).toFixed(4),
    bgL: +bgL.toFixed(2),
    meanL: +(sumL / (W * H)).toFixed(2),
    ink,
    inkFrac: +(ink / (W * H)).toFixed(5),
    bbox: ink ? [Math.round(x0 * SX), Math.round(y0 * SY), Math.round(x1 * SX), Math.round(y1 * SY)] : null,
    cx: ink ? +((sx / ink) * SX).toFixed(2) : null,
    cy: ink ? +((sy / ink) * SY).toFixed(2) : null,
    edge: edgeN ? +(edgeSum / edgeN).toFixed(3) : 0,
    sat: ink ? +(satSum / ink).toFixed(4) : 0,
    hue: hueN.map((n, k) => n ? hueAcc[k].map(v => Math.round(v / n)) : null),
  };
  out.push(rec);
}
fs.closeSync(fd);

fs.writeFileSync(path.join(dir, 'profiles.bin'), Buffer.from(profiles.buffer));
fs.writeFileSync(path.join(dir, 'motion.json'), JSON.stringify({
  meta, bins: { col: COLBINS, row: ROWBINS }, frames: out,
}));
console.log(`measured ${out.length} frames -> ${path.join(dir, 'motion.json')}`);
