#!/usr/bin/env node
// Reconstruct a scattered background layer (a word wall, a logo field, a
// confetti scatter) from a MOVING shot, in authored coordinates.
//
// The trick: when the layer scales or pans across a shot, elements hidden
// behind the subject in one frame are visible in another. Detect on every
// frame, map each detection back through that frame's known transform into
// authored space, then cluster the detections. Occlusion stops being a problem
// because no single element is hidden in every frame.
//
//   node reconstruct.mjs <raw.bin> --w 1280 --h 720 --frames 8 \
//        --scales "1.131,1.125,..." [--cx 640] [--cy 360]
//        [--gap 0.13] [--min-px 400] [--merge 0.28] [--json out.json]
//
// --scales is the layer's scale at each frame (derive it from a element whose
// size you can measure on every frame, e.g. a foreground hero word).
// Authored position:  A = C + (P - C) / s

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const file = process.argv[2];
const rest = process.argv.slice(3);
const num = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : Number(rest[i + 1]); };
const str = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : rest[i + 1]; };
if (!file) { console.error('usage: reconstruct.mjs <raw.bin> --scales "s0,s1,..."'); process.exit(1); }

const W = num('--w', 1280), H = num('--h', 720);
const NF = num('--frames', 8);
const CX = num('--cx', W / 2), CY = num('--cy', H / 2);
const MERGE = num('--merge', 0.28);
const GAP = str('--gap', '0.13'), MINPX = str('--min-px', '400');
const outJson = str('--json', null);
const scales = str('--scales', '').split(',').map(Number);
if (scales.length !== NF) { console.error(`--scales needs ${NF} values`); process.exit(1); }

// ---- detect on every frame via components.mjs
const dets = [];
for (let f = 0; f < NF; f++) {
  const tmp = path.join(path.dirname(file), `.rc-${f}.json`);
  const r = spawnSync('node', [path.join(HERE, 'components.mjs'), file,
    '--w', String(W), '--h', String(H), '--frame', String(f),
    '--gap', GAP, '--min-px', MINPX, '--json', tmp], { encoding: 'utf8' });
  if (r.status !== 0) { console.error(r.stderr); process.exit(1); }
  const j = JSON.parse(fs.readFileSync(tmp, 'utf8'));
  fs.unlinkSync(tmp);
  const s = scales[f];
  for (const w of j.words) {
    // Skip detections clipped by the frame edge in a dimension we need, and
    // skip suspiciously wide blobs (two touching elements merged into one).
    dets.push({
      frame: f, s,
      ax: CX + (w.cx - CX) / s,
      ay: CY + (w.cy - CY) / s,
      aw: w.w / s, ah: w.h / s,
      clipped: w.clippedLeft || w.clippedRight || w.clippedTop || w.clippedBottom,
      clippedX: w.clippedLeft || w.clippedRight,
      clippedY: w.clippedTop || w.clippedBottom,
      color: w.color, px: w.px,
    });
  }
}

// Typical authored element height, from unclipped detections only.
const cleanH = dets.filter(d => !d.clippedY).map(d => d.ah).sort((a, b) => a - b);
const typH = cleanH.length ? cleanH[cleanH.length >> 1] : 200;

// ---- cluster detections in authored space
const clusters = [];
for (const d of dets.sort((a, b) => b.px - a.px)) {
  let best = null, bestDist = Infinity;
  for (const c of clusters) {
    const dx = c.ax - d.ax, dy = c.ay - d.ay;
    const dist = Math.hypot(dx, dy);
    if (dist < typH * MERGE * 2 && dist < bestDist) { best = c; bestDist = dist; }
  }
  if (best) { best.items.push(d); }
  else clusters.push({ ax: d.ax, ay: d.ay, items: [d] });
  if (best) {
    best.ax = best.items.reduce((s, i) => s + i.ax, 0) / best.items.length;
    best.ay = best.items.reduce((s, i) => s + i.ay, 0) / best.items.length;
  }
}

const med = a => { const s = [...a].sort((x, y) => x - y); return s.length ? s[s.length >> 1] : 0; };
const tiles = clusters.map(c => {
  const un = c.items.filter(i => !i.clipped);
  const unY = c.items.filter(i => !i.clippedY);
  const unX = c.items.filter(i => !i.clippedX);
  const src = un.length ? un : c.items;
  return {
    ax: Math.round(med(src.map(i => i.ax))),
    ay: Math.round(med(src.map(i => i.ay))),
    aw: Math.round(med((unX.length ? unX : c.items).map(i => i.aw))),
    ah: Math.round(med((unY.length ? unY : c.items).map(i => i.ah))),
    seen: c.items.length,
    everClean: un.length,
    color: [0, 1, 2].map(k => Math.round(med(src.map(i => i.color[k])))),
    hex: '#' + [0, 1, 2].map(k => Math.round(med(src.map(i => i.color[k]))).toString(16).padStart(2, '0')).join(''),
  };
}).filter(t => t.seen >= 2)          // seen on at least two frames = real
  .sort((a, b) => a.ay - b.ay || a.ax - b.ax);

const out = { frames: NF, typicalHeight: Math.round(typH), tileCount: tiles.length, tiles };
if (outJson) fs.writeFileSync(outJson, JSON.stringify(out, null, 2));

console.log(`${dets.length} detections over ${NF} frames -> ${tiles.length} tiles (authored space)`);
console.log(`typical authored height ${Math.round(typH)}px\n`);
console.log('  ax     ay     aw    ah   seen clean  colour');
for (const t of tiles) {
  console.log(
    String(t.ax).padStart(6), String(t.ay).padStart(6),
    String(t.aw).padStart(6), String(t.ah).padStart(5),
    String(t.seen).padStart(5), String(t.everClean).padStart(5), '  ' + t.hex);
}
