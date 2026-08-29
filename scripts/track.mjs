#!/usr/bin/env node
// Track one screen region across a frame range: top edge, bottom edge, left/right
// edge and ink mass per frame. This is how you tell mechanics apart:
//
//   bottom fixed + top rising      -> clip/mask reveal (element does not move)
//   top and bottom rising together -> translation (element moves through a mask)
//   left fixed + right growing     -> typing / horizontal wipe
//   both edges expanding from mid  -> scale
//
//   node track.mjs <dir> --from <sec> --to <sec> [--x0 N --x1 N] [--y0 N --y1 N]
//
// x/y bounds are in SOURCE pixels. Prints one row per frame.

import fs from 'node:fs';
import path from 'node:path';

const dir = process.argv[2];
const rest = process.argv.slice(3);
const arg = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : Number(rest[i + 1]); };
if (!dir) { console.error('usage: track.mjs <dir> --from S --to S [--x0 N --x1 N]'); process.exit(1); }

const meta = JSON.parse(fs.readFileSync(path.join(dir, 'meta.json'), 'utf8'));
const { w: W, h: H, fps, frames } = meta;
const SX = meta.sourceW / W, SY = meta.sourceH / H;
const FRAME = W * H * 3;

const f0 = Math.max(0, Math.round(arg('--from', 0) * fps));
const f1 = Math.min(frames - 1, Math.round(arg('--to', meta.duration) * fps));
const X0 = Math.floor(arg('--x0', 0) / SX), X1 = Math.ceil(arg('--x1', meta.sourceW) / SX);
const Y0 = Math.floor(arg('--y0', 0) / SY), Y1 = Math.ceil(arg('--y1', meta.sourceH) / SY);

const fd = fs.openSync(path.join(dir, 'raw.bin'), 'r');
const buf = Buffer.allocUnsafe(FRAME);
const INK_T = 42;

console.log('frame    t     top   bot   left  right  ink    meanA');
for (let f = f0; f <= f1; f++) {
  fs.readSync(fd, buf, 0, FRAME, f * FRAME);
  // background from the frame corners
  const cor = [];
  const PS = Math.max(4, Math.round(Math.min(W, H) * 0.05));
  for (const [ox, oy] of [[0, 0], [W - PS, 0], [0, H - PS], [W - PS, H - PS]]) {
    let s = 0;
    for (let y = oy; y < oy + PS; y++) for (let x = ox; x < ox + PS; x++) {
      const p = (y * W + x) * 3;
      s += 0.2126 * buf[p] + 0.7152 * buf[p + 1] + 0.0722 * buf[p + 2];
    }
    cor.push(s / (PS * PS));
  }
  cor.sort((a, b) => a - b);
  const bg = (cor[1] + cor[2]) / 2;

  let top = 1e9, bot = -1, left = 1e9, right = -1, ink = 0, alpha = 0;
  for (let y = Y0; y < Y1; y++) {
    for (let x = X0; x < X1; x++) {
      const p = (y * W + x) * 3;
      const L = 0.2126 * buf[p] + 0.7152 * buf[p + 1] + 0.0722 * buf[p + 2];
      const d = Math.abs(L - bg);
      if (d <= INK_T) continue;
      ink++;
      alpha += d / 255;
      if (y < top) top = y;
      if (y > bot) bot = y;
      if (x < left) left = x;
      if (x > right) right = x;
    }
  }
  const fmt = (v, s) => (v === 1e9 || v === -1 ? '  -  ' : String(Math.round(v * s)).padStart(5));
  console.log(
    String(f).padStart(5),
    (f / fps).toFixed(3).padStart(6),
    fmt(top, SY), fmt(bot, SY), fmt(left, SX), fmt(right, SX),
    String(ink).padStart(6),
    (ink ? alpha / ink : 0).toFixed(3).padStart(6),
  );
}
fs.closeSync(fd);
