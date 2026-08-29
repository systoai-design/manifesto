#!/usr/bin/env node
// Connected-component analysis of one frame: find every distinct ink blob,
// group blobs into words, and report each word's box and colour.
//
// This is how you reconstruct a scattered/tiled background (a word wall, a
// confetti field, a logo grid) instead of guessing its layout — measure where
// every element actually is, then place yours at the same coordinates.
//
//   node components.mjs <raw.bin> --w 1280 --h 720 --frame 0 \
//        [--min-px 250] [--sat 0.22] [--vmin 40] [--exclude-bright 200]
//        [--gap 0.42] [--json out.json]
//
// --exclude-bright drops near-white pixels (a white hero word sitting on top of
// the field), so the field behind it can be measured on its own.
// --gap is the max horizontal blob gap, as a fraction of blob height, that still
// counts as the same word.

import fs from 'node:fs';

const file = process.argv[2];
const rest = process.argv.slice(3);
const num = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : Number(rest[i + 1]); };
const str = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : rest[i + 1]; };
if (!file) { console.error('usage: components.mjs <raw.bin> --w N --h N --frame N'); process.exit(1); }

const W = num('--w', 1280), H = num('--h', 720), FI = num('--frame', 0);
const MINPX = num('--min-px', 250), SAT = num('--sat', 0.22), VMIN = num('--vmin', 40);
const BRIGHT = num('--exclude-bright', 200), GAPF = num('--gap', 0.42);
const outJson = str('--json', null);

const FRAME = W * H * 3;
const fd = fs.openSync(file, 'r');
const buf = Buffer.allocUnsafe(FRAME);
fs.readSync(fd, buf, 0, FRAME, FI * FRAME);
fs.closeSync(fd);

// ---- mask: coloured field pixels only (not background, not the bright hero)
const mask = new Uint8Array(W * H);
for (let i = 0; i < W * H; i++) {
  const p = i * 3, r = buf[p], g = buf[p + 1], b = buf[p + 2];
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b);
  const sat = mx ? (mx - mn) / mx : 0;
  const bright = (r + g + b) / 3;
  if (mx >= VMIN && sat >= SAT && bright < BRIGHT) mask[i] = 1;
}

// ---- connected components (4-neighbour, iterative flood fill)
const label = new Int32Array(W * H).fill(-1);
const comps = [];
const stack = new Int32Array(W * H);
for (let s = 0; s < W * H; s++) {
  if (!mask[s] || label[s] !== -1) continue;
  const id = comps.length;
  let sp = 0; stack[sp++] = s; label[s] = id;
  let n = 0, x0 = W, x1 = -1, y0 = H, y1 = -1, sr = 0, sg = 0, sb = 0;
  while (sp > 0) {
    const q = stack[--sp];
    const x = q % W, y = (q / W) | 0;
    n++;
    if (x < x0) x0 = x; if (x > x1) x1 = x;
    if (y < y0) y0 = y; if (y > y1) y1 = y;
    const p = q * 3; sr += buf[p]; sg += buf[p + 1]; sb += buf[p + 2];
    if (x > 0 && mask[q - 1] && label[q - 1] === -1) { label[q - 1] = id; stack[sp++] = q - 1; }
    if (x < W - 1 && mask[q + 1] && label[q + 1] === -1) { label[q + 1] = id; stack[sp++] = q + 1; }
    if (y > 0 && mask[q - W] && label[q - W] === -1) { label[q - W] = id; stack[sp++] = q - W; }
    if (y < H - 1 && mask[q + W] && label[q + W] === -1) { label[q + W] = id; stack[sp++] = q + W; }
  }
  comps.push({ id, n, x0, x1, y0, y1, r: sr / n, g: sg / n, b: sb / n });
}

const blobs = comps.filter(c => c.n >= MINPX)
  .sort((a, b) => (a.y0 + a.y1) - (b.y0 + b.y1) || a.x0 - b.x0);

// ---- group blobs into words: vertical overlap + small horizontal gap
function vOverlap(a, b) {
  const lo = Math.max(a.y0, b.y0), hi = Math.min(a.y1, b.y1);
  if (hi < lo) return 0;
  return (hi - lo) / Math.min(a.y1 - a.y0, b.y1 - b.y0);
}
const used = new Set();
const words = [];
// Seed from the LARGEST blob outwards. Seeding in reading order lets a stray
// accent mark (an i-dot) start its own group, and nothing can then join it
// because every "is this a small attachment?" test is relative to the seed.
const seeds = [...blobs].sort((a, b) => b.n - a.n);
for (const a of seeds) {
  if (used.has(a.id)) continue;
  const group = [a]; used.add(a.id);
  let changed = true;
  while (changed) {
    changed = false;
    const gx0 = Math.min(...group.map(c => c.x0)), gx1 = Math.max(...group.map(c => c.x1));
    const gy0 = Math.min(...group.map(c => c.y0)), gy1 = Math.max(...group.map(c => c.y1));
    const hgt = gy1 - gy0;
    for (const b of blobs) {
      if (used.has(b.id)) continue;
      const gap = b.x0 > gx1 ? b.x0 - gx1 : (gx0 > b.x1 ? gx0 - b.x1 : 0);
      if (gap > hgt * GAPF) continue;
      // Normal case: the blob shares a baseline band with the group.
      const shares = vOverlap({ y0: gy0, y1: gy1 }, b) >= 0.30;
      // Accent case: a small mark (an i/j dot, an umlaut) sits ABOVE the
      // x-height, so it shares no vertical band with the letters it belongs to.
      // Claim it when it sits inside the group's horizontal span and inside its
      // vertical extent, and is small relative to the group.
      const inX = b.x1 >= gx0 - hgt * 0.08 && b.x0 <= gx1 + hgt * 0.08;
      const inY = b.y0 >= gy0 - hgt * 0.15 && b.y1 <= gy1 + hgt * 0.15;
      const small = (b.y1 - b.y0) <= hgt * 0.45 && (b.x1 - b.x0) <= hgt * 0.45;
      if (shares || (inX && inY && small)) { group.push(b); used.add(b.id); changed = true; }
    }
  }
  const x0 = Math.min(...group.map(c => c.x0)), x1 = Math.max(...group.map(c => c.x1));
  const y0 = Math.min(...group.map(c => c.y0)), y1 = Math.max(...group.map(c => c.y1));
  const tot = group.reduce((s, c) => s + c.n, 0);
  const col = [0, 0, 0];
  for (const c of group) { col[0] += c.r * c.n; col[1] += c.g * c.n; col[2] += c.b * c.n; }
  words.push({
    x0, x1, y0, y1, w: x1 - x0 + 1, h: y1 - y0 + 1,
    cx: Math.round((x0 + x1) / 2), cy: Math.round((y0 + y1) / 2),
    px: tot, parts: group.length,
    color: col.map(v => Math.round(v / tot)),
    hex: '#' + col.map(v => Math.round(v / tot).toString(16).padStart(2, '0')).join(''),
    clippedLeft: x0 <= 1, clippedRight: x1 >= W - 2,
    clippedTop: y0 <= 1, clippedBottom: y1 >= H - 2,
  });
}
words.sort((a, b) => a.cy - b.cy || a.cx - b.cx);

// ---- infer rows from the y-centres
const rows = [];
for (const w of words) {
  const r = rows.find(r => Math.abs(r.cy - w.cy) < Math.max(24, w.h * 0.45));
  if (r) { r.items.push(w); r.cy = r.items.reduce((s, i) => s + i.cy, 0) / r.items.length; }
  else rows.push({ cy: w.cy, items: [w] });
}
rows.sort((a, b) => a.cy - b.cy);

const result = { frame: FI, w: W, h: H, wordCount: words.length, words, rows: rows.map(r => ({
  cy: Math.round(r.cy),
  count: r.items.length,
  xs: r.items.map(i => i.cx),
  pitch: r.items.length > 1
    ? Math.round((r.items[r.items.length - 1].cx - r.items[0].cx) / (r.items.length - 1)) : null,
  heights: r.items.map(i => i.h),
})) };

if (outJson) fs.writeFileSync(outJson, JSON.stringify(result, null, 2));

console.log(`frame ${FI}: ${comps.length} blobs -> ${words.length} words in ${rows.length} rows\n`);
console.log('row  cy    n  pitch  xs');
for (const r of result.rows) {
  console.log(String(rows.indexOf(rows.find(x => Math.round(x.cy) === r.cy))).padStart(3),
    String(r.cy).padStart(5), String(r.count).padStart(3),
    String(r.pitch ?? '-').padStart(6), ' ', r.xs.join(', '));
}
console.log('\nword  cx    cy    w    h    colour     clipped');
for (const w of words) {
  const cl = [w.clippedLeft && 'L', w.clippedRight && 'R', w.clippedTop && 'T', w.clippedBottom && 'B']
    .filter(Boolean).join('');
  console.log('     ', String(w.cx).padStart(5), String(w.cy).padStart(5),
    String(w.w).padStart(4), String(w.h).padStart(4), ' ', w.hex, '  ', cl);
}
