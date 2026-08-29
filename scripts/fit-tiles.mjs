#!/usr/bin/env node
// Fit the positions of a repeated background element by OPTIMISING them against
// the reference, instead of detecting them once and hoping.
//
// Detection (components / template match) recovers only the elements a given
// frame actually shows. When a large subject occludes half the frame, that is
// never all of them. This does the inverse: it stamps a real glyph template at
// candidate positions, scores the whole layer against every frame of the shot at
// once, and hill-climbs the positions until the overlap stops improving.
//
//   node fit-tiles.mjs <refRaw> --w 640 --h 360 --first 108 --frames 8 \
//        --scales "1.131,..." --tpl-frame 7 --tpl-box "280,7,430,111" \
//        --rot 2 [--seed tiles.json] [--out fitted.json] [--passes 3]
//
// --tpl-box is in the RAW file's own pixel space, around one clean instance.
// Positions are reported in authored space: screen = C + R(rot)·(A − C)·scale.

import fs from 'node:fs';

const file = process.argv[2];
const rest = process.argv.slice(3);
const num = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : Number(rest[i + 1]); };
const str = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : rest[i + 1]; };
if (!file) { console.error('usage: fit-tiles.mjs <refRaw> --scales "..." --tpl-box "x0,y0,x1,y1"'); process.exit(1); }

const W = num('--w', 640), H = num('--h', 360);
const FIRST = num('--first', 0), NF = num('--frames', 8);
const ROT = num('--rot', 0) * Math.PI / 180;
const CX = num('--cx', W / 2), CY = num('--cy', H / 2);
const PASSES = num('--passes', 3);
const scales = str('--scales', '').split(',').map(Number);
const tplFrame = num('--tpl-frame', NF - 1);
const box = str('--tpl-box', '').split(',').map(Number);
const seedFile = str('--seed', null);
const tplFile = str('--tpl-file', null);   // take the template from a DIFFERENT video
const outFile = str('--out', null);
if (scales.length !== NF) { console.error(`--scales needs ${NF} values`); process.exit(1); }

const FRAME = W * H * 3;
const fd = fs.openSync(file, 'r');
function maskOf(idx) {
  const b = Buffer.allocUnsafe(FRAME);
  fs.readSync(fd, b, 0, FRAME, idx * FRAME);
  const m = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) {
    const p = i * 3, r = b[p], g = b[p + 1], bl = b[p + 2];
    const mx = Math.max(r, g, bl), mn = Math.min(r, g, bl);
    const sat = mx ? (mx - mn) / mx : 0;
    if (mx >= 40 && sat >= 0.22 && (r + g + bl) / 3 < 200) m[i] = 1;
  }
  return m;
}
// hero mask: bright, low-saturation pixels are the foreground subject and must be
// excluded from scoring — the layer behind them is simply not visible there.
function heroOf(idx) {
  const b = Buffer.allocUnsafe(FRAME);
  fs.readSync(fd, b, 0, FRAME, idx * FRAME);
  const m = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) {
    const p = i * 3, r = b[p], g = b[p + 1], bl = b[p + 2];
    const mx = Math.max(r, g, bl), mn = Math.min(r, g, bl);
    const sat = mx ? (mx - mn) / mx : 0;
    if (mx > 170 && sat < 0.12) m[i] = 1;
  }
  return m;
}

const refM = [], heroM = [];
for (let k = 0; k < NF; k++) { refM.push(maskOf(FIRST + k)); heroM.push(heroOf(FIRST + k)); }

// The template should be YOUR glyph, not the reference's: the fit then answers
// "where do MY elements go to best match the reference", which is the question
// that actually transfers to the render.
let tplFd = fd;
if (tplFile) tplFd = fs.openSync(tplFile, 'r');
function maskOfFd(f, idx) {
  const b = Buffer.allocUnsafe(FRAME);
  fs.readSync(f, b, 0, FRAME, idx * FRAME);
  const m = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) {
    const p = i * 3, r = b[p], g = b[p + 1], bl = b[p + 2];
    const mx = Math.max(r, g, bl), mn = Math.min(r, g, bl);
    const sat = mx ? (mx - mn) / mx : 0;
    if (mx >= 40 && sat >= 0.22 && (r + g + bl) / 3 < 200) m[i] = 1;
  }
  return m;
}

// ---- template, lifted into authored space
const [bx0, by0, bx1, by1] = box;
const tplS = scales[tplFrame];
const tw = Math.round((bx1 - bx0 + 1) / tplS), th = Math.round((by1 - by0 + 1) / tplS);
const tpl = new Uint8Array(tw * th);
{
  const src = maskOfFd(tplFd, FIRST + tplFrame);
  for (let y = 0; y < th; y++) {
    const sy = by0 + Math.round(y * tplS);
    for (let x = 0; x < tw; x++) {
      const sx = bx0 + Math.round(x * tplS);
      if (sx >= 0 && sx < W && sy >= 0 && sy < H) tpl[y * tw + x] = src[sy * W + sx];
    }
  }
}
let tplInk = 0; for (const v of tpl) tplInk += v;
fs.closeSync(fd);
if (tplFile) fs.closeSync(tplFd);
if (tplInk < 40) { console.error('template nearly empty — check --tpl-box'); process.exit(1); }

// ---- forward model: stamp all tiles for one frame
const cosR = Math.cos(ROT), sinR = Math.sin(ROT);
function render(tiles, k) {
  const s = scales[k];
  const out = new Uint8Array(W * H);
  for (const t of tiles) {
    // authored centre -> screen centre
    const dx = t.x - CX, dy = t.y - CY;
    const rx = dx * cosR - dy * sinR, ry = dx * sinR + dy * cosR;
    const scx = CX + rx * s, scy = CY + ry * s;
    const hw = tw * s / 2, hh = th * s / 2;
    const x0 = Math.max(0, Math.floor(scx - hw)), x1 = Math.min(W - 1, Math.ceil(scx + hw));
    const y0 = Math.max(0, Math.floor(scy - hh)), y1 = Math.min(H - 1, Math.ceil(scy + hh));
    for (let y = y0; y <= y1; y++) {
      // inverse-rotate + inverse-scale into template space
      const py = y - scy;
      for (let x = x0; x <= x1; x++) {
        const px = x - scx;
        const ux = (px * cosR + py * sinR) / s, uy = (-px * sinR + py * cosR) / s;
        const tx = Math.round(ux + tw / 2), ty = Math.round(uy + th / 2);
        if (tx < 0 || tx >= tw || ty < 0 || ty >= th) continue;
        if (tpl[ty * tw + tx]) out[y * W + x] = 1;
      }
    }
  }
  return out;
}

function score(tiles) {
  let inter = 0, uni = 0;
  for (let k = 0; k < NF; k++) {
    const mine = render(tiles, k), ref = refM[k], hero = heroM[k];
    for (let i = 0; i < W * H; i++) {
      if (hero[i]) continue;                 // occluded: unknowable, so unscored
      const a = ref[i], b = mine[i];
      if (a && b) inter++;
      if (a || b) uni++;
    }
  }
  return uni ? inter / uni : 0;
}

// ---- seed
let tiles;
if (seedFile && fs.existsSync(seedFile)) {
  tiles = JSON.parse(fs.readFileSync(seedFile, 'utf8')).map(t => ({ x: t[0] / 2, y: t[1] / 2 }));
} else {
  tiles = [];
  for (let r = -1; r <= 3; r++) for (let c = -1; c <= 4; c++) tiles.push({ x: 65 + c * 250, y: 34 + r * 136 });
}

console.log(`template ${tw}x${th} authored (ink ${tplInk}); seeding ${tiles.length} tiles`);
let best = score(tiles);
console.log(`start IoU ${best.toFixed(4)}`);

// ---- coordinate descent on every tile, plus prune
for (let pass = 0; pass < PASSES; pass++) {
  for (const step of [24, 12, 6, 3]) {
    let improved = true, guard = 0;
    while (improved && guard++ < 6) {
      improved = false;
      for (const t of tiles) {
        const ox = t.x, oy = t.y;
        let bx = ox, by = oy, bs = best;
        for (const [dx, dy] of [[step, 0], [-step, 0], [0, step], [0, -step],
                                [step, step], [step, -step], [-step, step], [-step, -step]]) {
          t.x = ox + dx; t.y = oy + dy;
          const sc = score(tiles);
          if (sc > bs) { bs = sc; bx = t.x; by = t.y; }
        }
        t.x = bx; t.y = by;
        if (bs > best) { best = bs; improved = true; }
      }
    }
  }
  // prune tiles that hurt
  for (let i = tiles.length - 1; i >= 0; i--) {
    const kept = tiles[i];
    tiles.splice(i, 1);
    const sc = score(tiles);
    if (sc > best) { best = sc; } else { tiles.splice(i, 0, kept); }
  }
  console.log(`pass ${pass + 1}: IoU ${best.toFixed(4)}  (${tiles.length} tiles)`);
}

const authored = tiles.map(t => [Math.round(t.x * 2), Math.round(t.y * 2)]);
if (outFile) fs.writeFileSync(outFile, JSON.stringify(authored));
console.log(`\nfinal IoU ${best.toFixed(4)} with ${tiles.length} tiles`);
console.log('TILES (authored, full-res coords):');
console.log('    ' + authored.map(t => `[${t[0]}, ${t[1]}]`).join(', '));
