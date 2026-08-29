#!/usr/bin/env node
// Turn per-frame measurements into a beat sheet: frame-exact cuts, per-segment
// motion signals, per-word reveal frames, and a best-fit GSAP ease for every
// transition found.
//
//   node segment.mjs <dir> [--blank 0.0006] [--swap 0.5] [--min-seg 3]
//
// Writes <dir>/beats.json and prints a human-readable beat sheet.
//
// Cut model (learned from real kinetic-typography references): cards are
// separated either by BLANK frames (ink ~ 0) or by a hard content SWAP (large
// column-profile L1 with content on both sides), or by a background flip.
// Blank runs are reported explicitly — they are a rhythm feature, not noise.

import fs from 'node:fs';
import path from 'node:path';

const dir = process.argv[2];
if (!dir) { console.error('usage: segment.mjs <dir>'); process.exit(1); }
const rest = process.argv.slice(3);
const arg = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : Number(rest[i + 1]); };
const BLANK = arg('--blank', 0.0006);
const SWAP = arg('--swap', 0.5);
const MIN_SEG = arg('--min-seg', 3);

const M = JSON.parse(fs.readFileSync(path.join(dir, 'motion.json'), 'utf8'));
const F = M.frames, N = F.length, fps = M.meta.fps;
const { col: COLBINS, row: ROWBINS } = M.bins;
const prof = new Uint16Array(fs.readFileSync(path.join(dir, 'profiles.bin')).buffer);
const colAt = f => prof.subarray(f * (COLBINS + ROWBINS), f * (COLBINS + ROWBINS) + COLBINS);
const SX = M.meta.sourceW / COLBINS;

// ---------------------------------------------------------------- ease library
const P = (n, t) => Math.pow(t, n);
const EASES = {
  'none': t => t,
  'power1.in': t => P(2, t), 'power1.out': t => 1 - P(2, 1 - t),
  'power1.inOut': t => t < .5 ? 2 * P(2, t) : 1 - P(2, -2 * t + 2) / 2,
  'power2.in': t => P(3, t), 'power2.out': t => 1 - P(3, 1 - t),
  'power2.inOut': t => t < .5 ? 4 * P(3, t) : 1 - P(3, -2 * t + 2) / 2,
  'power3.in': t => P(4, t), 'power3.out': t => 1 - P(4, 1 - t),
  'power3.inOut': t => t < .5 ? 8 * P(4, t) : 1 - P(4, -2 * t + 2) / 2,
  'power4.in': t => P(5, t), 'power4.out': t => 1 - P(5, 1 - t),
  'power4.inOut': t => t < .5 ? 16 * P(5, t) : 1 - P(5, -2 * t + 2) / 2,
  'sine.in': t => 1 - Math.cos(t * Math.PI / 2), 'sine.out': t => Math.sin(t * Math.PI / 2),
  'sine.inOut': t => -(Math.cos(Math.PI * t) - 1) / 2,
  'expo.out': t => t === 1 ? 1 : 1 - Math.pow(2, -10 * t),
  'expo.in': t => t === 0 ? 0 : Math.pow(2, 10 * t - 10),
  'circ.out': t => Math.sqrt(1 - P(2, t - 1)), 'circ.in': t => 1 - Math.sqrt(1 - P(2, t)),
};
for (const s of [1.0, 1.2, 1.4, 1.7, 2.0, 2.5, 3.0]) {
  EASES[`back.out(${s})`] = t => 1 + (s + 1) * P(3, t - 1) + s * P(2, t - 1);
  EASES[`back.in(${s})`] = t => (s + 1) * P(3, t) - s * P(2, t);
}
function fitEase(samples) {
  const res = [];
  for (const [name, fn] of Object.entries(EASES)) {
    let se = 0;
    for (const [t, v] of samples) { const d = fn(t) - v; se += d * d; }
    res.push({ ease: name, rmse: Math.sqrt(se / samples.length) });
  }
  return res.sort((a, b) => a.rmse - b.rmse);
}

// ---------------------------------------------------------------- cut model
const isBlank = f => F[f].inkFrac < BLANK;
const dColArr = [0];
for (let f = 1; f < N; f++) {
  const a = colAt(f), b = colAt(f - 1);
  let l1 = 0, tot = 0;
  for (let k = 0; k < COLBINS; k++) { l1 += Math.abs(a[k] - b[k]); tot += a[k] + b[k]; }
  dColArr.push(tot ? l1 / tot : 0);
}

// Content runs = maximal spans of non-blank frames.
const runs = [];
let s = null;
for (let f = 0; f < N; f++) {
  if (!isBlank(f)) { if (s === null) s = f; }
  else if (s !== null) { runs.push([s, f - 1]); s = null; }
}
if (s !== null) runs.push([s, N - 1]);

// Split each run further at hard swaps / background flips.
const segs = [];
for (const [a, b] of runs) {
  let cur = a;
  for (let f = a + 1; f <= b; f++) {
    const flip = Math.abs(F[f].bgL - F[f - 1].bgL) > 25;
    const swap = dColArr[f] > SWAP;
    if ((flip || swap) && f - cur >= MIN_SEG) { segs.push([cur, f - 1]); cur = f; }
  }
  if (b - cur + 1 >= 1) segs.push([cur, b]);
}

// ---------------------------------------------------------- signals per segment
const SIGNALS = [
  ['inkFrac', f => f.inkFrac, 'mass (reveal / wipe / type-on)'],
  ['bboxTop', f => f.bbox && f.bbox[1], 'top edge (rise / drop)'],
  ['bboxBot', f => f.bbox && f.bbox[3], 'bottom edge (rise / drop)'],
  ['bboxW', f => f.bbox && (f.bbox[2] - f.bbox[0]), 'width (typing / zoom / scale)'],
  ['bboxH', f => f.bbox && (f.bbox[3] - f.bbox[1]), 'height (grow / zoom)'],
  ['cx', f => f.cx, 'centroid x (pan / recenter)'],
  ['cy', f => f.cy, 'centroid y (vertical move)'],
];

function mainRun(vals) {
  let best = null;
  for (const dir of [1, -1]) {
    let st = 0;
    for (let i = 1; i <= vals.length; i++) {
      const brk = i === vals.length || vals[i] == null ||
        (vals[i - 1] != null && dir * (vals[i] - vals[i - 1]) < -Math.abs(vals[i - 1]) * 0.06 - 1e-6);
      if (brk) {
        if (i - st >= 4 && vals[st] != null && vals[i - 1] != null) {
          const span = Math.abs(vals[i - 1] - vals[st]);
          if (!best || span > best.span) best = { s: st, e: i - 1, span, dir };
        }
        st = i;
      }
    }
  }
  return best;
}

// Per-word reveal: contiguous active column-blocks, and the frame each first fills.
function wordReveals(a, b) {
  const active = [];                       // per bin: first frame it is meaningfully on
  const last = colAt(b);
  const peak = Math.max(...last) || 1;
  const on = k => last[k] > peak * 0.05;
  const blocks = [];
  let k = 0;
  while (k < COLBINS) {
    if (!on(k)) { k++; continue; }
    let j = k;
    while (j + 1 < COLBINS && (on(j + 1) || (j + 2 < COLBINS && on(j + 2)))) j++;
    blocks.push([k, j]);
    k = j + 1;
  }
  return blocks.map(([k0, k1]) => {
    let target = 0;
    for (let q = k0; q <= k1; q++) target += last[q];
    let first = null;
    for (let f = a; f <= b; f++) {
      const c = colAt(f);
      let v = 0;
      for (let q = k0; q <= k1; q++) v += c[q];
      if (v > target * 0.55) { first = f; break; }
    }
    return {
      xFrom: Math.round(k0 * SX), xTo: Math.round((k1 + 1) * SX),
      frame: first, t: first == null ? null : +(first / fps).toFixed(3),
    };
  });
}

const segments = [];
for (let c = 0; c < segs.length; c++) {
  const [a, b] = segs[c];
  const fr = F.slice(a, b + 1);
  const withInk = fr.filter(f => f.inkFrac > BLANK && f.edge > 0);
  const edges = withInk.map(f => f.edge);
  const seg = {
    index: c,
    startFrame: a, endFrame: b, frames: b - a + 1,
    start: +(a / fps).toFixed(3), end: +(b / fps).toFixed(3),
    duration: +((b - a + 1) / fps).toFixed(3),
    gapBefore: c === 0 ? a : a - segs[c - 1][1] - 1,
    bg: fr[Math.floor(fr.length / 2)].bgL > 128 ? 'white' : 'black',
    peakInk: +Math.max(...fr.map(f => f.inkFrac)).toFixed(5),
    edgeMin: edges.length ? +Math.min(...edges).toFixed(2) : null,
    edgeMax: edges.length ? +Math.max(...edges).toFixed(2) : null,
    motions: [],
    words: wordReveals(a, b),
  };
  // Motion blur signature: sharpest frame vs blurriest frame within the card.
  seg.blurDrop = seg.edgeMax ? +(1 - seg.edgeMin / seg.edgeMax).toFixed(3) : 0;

  for (const [name, get, mech] of SIGNALS) {
    const vals = fr.map(get);
    if (vals.some(v => v == null)) continue;
    const run = mainRun(vals);
    if (!run) continue;
    const v0 = vals[run.s], v1 = vals[run.e];
    const rel = Math.abs(v1 - v0) / (Math.abs(v0) + Math.abs(v1) + 1e-6);
    if (rel < 0.04) continue;
    const n = run.e - run.s;
    if (n < 4) continue;
    const samples = [];
    for (let k = 0; k <= n; k++) samples.push([k / n, (vals[run.s + k] - v0) / (v1 - v0)]);
    const fits = fitEase(samples);
    seg.motions.push({
      signal: name, mechanic: mech,
      fromFrame: a + run.s, toFrame: a + run.e,
      from: +v0.toFixed(3), to: +v1.toFixed(3),
      startS: +((a + run.s) / fps).toFixed(3),
      durS: +(n / fps).toFixed(3),
      ease: fits[0].ease, rmse: +fits[0].rmse.toFixed(4),
      alt: fits.slice(1, 4).map(x => `${x.ease}(${x.rmse.toFixed(3)})`),
    });
  }
  segments.push(seg);
}

fs.writeFileSync(path.join(dir, 'beats.json'),
  JSON.stringify({ meta: M.meta, segments }, null, 2));

// ----------------------------------------------------------------- report
const blurAll = segments.filter(s => s.blurDrop).map(s => s.blurDrop);
console.log(`${segments.length} segments over ${N} frames @${fps}fps (${(N / fps).toFixed(3)}s)`);
console.log(`median blurDrop ${blurAll.sort((a, b) => a - b)[blurAll.length >> 1]}\n`);
for (const s of segments) {
  console.log(`#${String(s.index).padStart(2)} f${String(s.startFrame).padStart(3)}-${String(s.endFrame).padStart(3)} ` +
    `${s.start.toFixed(2)}s +${s.duration.toFixed(2)}s ${s.bg.padEnd(5)} gap=${s.gapBefore} ` +
    `ink=${s.peakInk} blur=${s.blurDrop}`);
  const w = s.words.filter(x => x.frame != null);
  if (w.length > 1) {
    console.log(`      words: ` + w.map(x => `x${x.xFrom}@${x.t.toFixed(2)}`).join('  '));
  }
  for (const m of s.motions.slice(0, 3)) {
    console.log(`      ${m.signal.padEnd(8)} ${m.from}->${m.to} @${m.startS.toFixed(2)}s +${m.durS.toFixed(2)}s ` +
      `ease=${m.ease} (${m.rmse}) alt=${m.alt.join(',')}`);
  }
}
