#!/usr/bin/env node
// Locate every instance of a repeated element in a frame by template matching.
//
// Use when a background is the SAME element repeated at one size (a word wall,
// a logo field, an icon scatter). Component analysis fails on these because the
// elements touch and occlude each other; correlation against a template of the
// element itself does not — a partly hidden tile still produces a peak.
//
//   node match-tiles.mjs <sceneRaw> --frame N --template <tplRaw> --tpl-frame N \
//        --tpl-box "x0,y0,x1,y1" [--w 1280] [--h 720] [--step 2]
//        [--thresh 0.45] [--scale 1.0] [--json out.json]
//
// The template is a box around ONE clean instance, taken from any frame of
// either video (your own render is usually the easiest place to find a clean,
// unoccluded one at a known size).

import fs from 'node:fs';

const scene = process.argv[2];
const rest = process.argv.slice(3);
const num = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : Number(rest[i + 1]); };
const str = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : rest[i + 1]; };
if (!scene) { console.error('usage: match-tiles.mjs <sceneRaw> --template <tplRaw> --tpl-box "x0,y0,x1,y1"'); process.exit(1); }

const W = num('--w', 1280), H = num('--h', 720);
const FI = num('--frame', 0), STEP = num('--step', 2);
const THRESH = num('--thresh', 0.45);
const SCALE = num('--scale', 1.0);
const tplFile = str('--template', scene), tplFrame = num('--tpl-frame', 0);
const box = str('--tpl-box', '').split(',').map(Number);
const outJson = str('--json', null);
if (box.length !== 4) { console.error('--tpl-box "x0,y0,x1,y1" required'); process.exit(1); }

const FRAME = W * H * 3;
function inkMask(file, idx) {
  const fd = fs.openSync(file, 'r');
  const b = Buffer.allocUnsafe(FRAME);
  fs.readSync(fd, b, 0, FRAME, idx * FRAME);
  fs.closeSync(fd);
  const m = new Float32Array(W * H);
  for (let i = 0; i < W * H; i++) {
    const p = i * 3, r = b[p], g = b[p + 1], bl = b[p + 2];
    const mx = Math.max(r, g, bl), mn = Math.min(r, g, bl);
    const sat = mx ? (mx - mn) / mx : 0;
    if (mx >= 40 && sat >= 0.22 && (r + g + bl) / 3 < 200) m[i] = 1;
  }
  return m;
}

const scn = inkMask(scene, FI);
const tplFull = inkMask(tplFile, tplFrame);

// crop + optionally rescale the template
const [bx0, by0, bx1, by1] = box;
const tw0 = bx1 - bx0 + 1, th0 = by1 - by0 + 1;
const TW = Math.max(4, Math.round(tw0 * SCALE)), TH = Math.max(4, Math.round(th0 * SCALE));
const tpl = new Float32Array(TW * TH);
let tplSum = 0;
for (let y = 0; y < TH; y++) {
  const sy = by0 + Math.round(y / SCALE);
  for (let x = 0; x < TW; x++) {
    const sx = bx0 + Math.round(x / SCALE);
    const v = (sx >= 0 && sx < W && sy >= 0 && sy < H) ? tplFull[sy * W + sx] : 0;
    tpl[y * TW + x] = v; tplSum += v;
  }
}
if (tplSum < 50) { console.error('template is nearly empty — check --tpl-box'); process.exit(1); }

// correlation: fraction of template ink that lands on scene ink
const cw = Math.floor((W - TW) / STEP) + 1, ch = Math.floor((H - TH) / STEP) + 1;
const corr = new Float32Array(cw * ch);
for (let cy = 0; cy < ch; cy++) {
  const oy = cy * STEP;
  for (let cx = 0; cx < cw; cx++) {
    const ox = cx * STEP;
    let hit = 0;
    for (let y = 0; y < TH; y += 2) {
      const row = (oy + y) * W;
      for (let x = 0; x < TW; x += 2) {
        if (tpl[y * TW + x]) hit += scn[row + ox + x];
      }
    }
    corr[cy * cw + cx] = hit / (tplSum / 4);
  }
}

// peak picking with non-maximum suppression
const peaks = [];
// Separation must be close to the real element pitch, or one element yields
// several peaks and a grid of N tiles reads back as 2N.
const minSep = num('--min-sep', Math.min(TW, TH) * 0.55);
const order = [];
for (let i = 0; i < corr.length; i++) if (corr[i] >= THRESH) order.push(i);
order.sort((a, b) => corr[b] - corr[a]);
for (const i of order) {
  const cx = (i % cw) * STEP + TW / 2, cy = ((i / cw) | 0) * STEP + TH / 2;
  if (peaks.some(p => Math.hypot(p.cx - cx, p.cy - cy) < minSep)) continue;
  peaks.push({ cx: Math.round(cx), cy: Math.round(cy), score: +corr[i].toFixed(3) });
}
peaks.sort((a, b) => a.cy - b.cy || a.cx - b.cx);

const out = { frame: FI, template: { w: TW, h: TH, ink: Math.round(tplSum) }, count: peaks.length, peaks };
if (outJson) fs.writeFileSync(outJson, JSON.stringify(out, null, 2));

console.log(`template ${TW}x${TH} (ink ${Math.round(tplSum)}) -> ${peaks.length} matches at >=${THRESH}\n`);
console.log('   cx     cy   score');
for (const p of peaks) console.log(String(p.cx).padStart(5), String(p.cy).padStart(6), String(p.score).padStart(7));
