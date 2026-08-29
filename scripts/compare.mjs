#!/usr/bin/env node
// Score a replica against its reference, objectively.
//
//   node compare.mjs <refDir> <mineDir> [--ref-video X --mine-video Y]
//
// Two independent scores:
//   1. Per-frame SSIM/PSNR straight from ffmpeg (needs --ref-video/--mine-video).
//      This is the headline number: 1.0 = pixel identical.
//   2. Metric-space deltas from the measured motion.json of each side — tells you
//      WHERE the divergence is (which card, and in which property), which raw
//      SSIM cannot.
//
// Prints a per-card table plus overall scores, and writes <mineDir>/score.json.

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const [refDir, mineDir, ...rest] = process.argv.slice(2);
if (!refDir || !mineDir) { console.error('usage: compare.mjs <refDir> <mineDir> [--ref-video X --mine-video Y]'); process.exit(1); }
const sarg = (f) => { const i = rest.indexOf(f); return i === -1 ? null : rest[i + 1]; };

const R = JSON.parse(fs.readFileSync(path.join(refDir, 'motion.json'), 'utf8'));
const Mi = JSON.parse(fs.readFileSync(path.join(mineDir, 'motion.json'), 'utf8'));
const RB = JSON.parse(fs.readFileSync(path.join(refDir, 'beats.json'), 'utf8'));
const fps = R.meta.fps;
const N = Math.min(R.frames.length, Mi.frames.length);

// ---------------------------------------------------------------- 1. SSIM
let ssim = null, psnr = null, ssimSeries = null;
const rv = sarg('--ref-video'), mv = sarg('--mine-video');
if (rv && mv) {
  const logFile = path.join(mineDir, 'ssim.log');
  const r = spawnSync('ffmpeg', [
    '-v', 'error', '-y', '-i', mv, '-i', rv,
    '-lavfi', `[0:v]scale=1280:720,fps=${fps},setpts=PTS-STARTPTS[a];` +
              `[1:v]scale=1280:720,fps=${fps},setpts=PTS-STARTPTS[b];` +
              `[a][b]ssim=stats_file=${logFile.replace(/\\/g, '/')}`,
    '-f', 'null', '-',
  ], { encoding: 'utf8', maxBuffer: 1 << 28 });
  if (r.status === 0 && fs.existsSync(logFile)) {
    ssimSeries = fs.readFileSync(logFile, 'utf8').trim().split('\n').map(line => {
      const m = line.match(/All:([0-9.]+)/);
      return m ? Number(m[1]) : null;
    }).filter(v => v != null);
    ssim = ssimSeries.reduce((s, v) => s + v, 0) / ssimSeries.length;
  }
  // psnr prints its summary at info level, so -v error would swallow it
  const p = spawnSync('ffmpeg', [
    '-v', 'info', '-y', '-i', mv, '-i', rv,
    '-lavfi', `[0:v]scale=1280:720,fps=${fps},setpts=PTS-STARTPTS[a];` +
              `[1:v]scale=1280:720,fps=${fps},setpts=PTS-STARTPTS[b];[a][b]psnr`,
    '-f', 'null', '-',
  ], { encoding: 'utf8', maxBuffer: 1 << 28 });
  const pm = (p.stderr || '').match(/average:([0-9.]+)/);
  if (pm) psnr = Number(pm[1]);
}

// ------------------------------------------------------- 2. metric-space delta
const norm = (v, s) => (v == null ? null : v / s);
function frameDelta(a, b) {
  // scale-normalised so each component is comparable
  const parts = [];
  parts.push(Math.abs(a.inkFrac - b.inkFrac) * 6);
  parts.push(Math.abs(a.bgL - b.bgL) / 255);
  if (a.bbox && b.bbox) {
    for (let k = 0; k < 4; k++) {
      parts.push(Math.abs(a.bbox[k] - b.bbox[k]) / (k % 2 ? 720 : 1280));
    }
  } else if (a.bbox || b.bbox) parts.push(1);
  if (a.cx != null && b.cx != null) {
    parts.push(Math.abs(a.cx - b.cx) / 1280);
    parts.push(Math.abs(a.cy - b.cy) / 720);
  }
  return parts.reduce((s, v) => s + v, 0) / parts.length;
}

const per = [];
for (let f = 0; f < N; f++) per.push(frameDelta(R.frames[f], Mi.frames[f]));
const meanDelta = per.reduce((s, v) => s + v, 0) / per.length;

// per-card rollup, using the reference's own segmentation
const cards = RB.segments.map(s => {
  const a = s.startFrame, b = Math.min(s.endFrame, N - 1);
  if (b < a) return null;
  const win = per.slice(a, b + 1);
  const ss = ssimSeries ? ssimSeries.slice(a, b + 1) : null;
  return {
    seg: s.index,
    start: s.start, dur: s.duration, bg: s.bg,
    delta: +(win.reduce((x, y) => x + y, 0) / win.length).toFixed(4),
    worst: +Math.max(...win).toFixed(4),
    ssim: ss && ss.length ? +(ss.reduce((x, y) => x + y, 0) / ss.length).toFixed(4) : null,
  };
}).filter(Boolean);

const out = {
  refFrames: R.frames.length, mineFrames: Mi.frames.length,
  frameCountDelta: Mi.frames.length - R.frames.length,
  ssim, psnr, meanDelta: +meanDelta.toFixed(4), cards,
};
fs.writeFileSync(path.join(mineDir, 'score.json'), JSON.stringify(out, null, 2));

console.log(`frames  ref=${R.frames.length}  mine=${Mi.frames.length}  (delta ${out.frameCountDelta})`);
if (ssim != null) console.log(`SSIM    ${ssim.toFixed(4)}   PSNR ${psnr != null ? psnr.toFixed(2) + ' dB' : 'n/a'}`);
console.log(`metric  meanDelta ${meanDelta.toFixed(4)} (lower is better)\n`);
console.log('seg  start   dur   bg     delta   worst   ssim');
for (const c of [...cards].sort((a, b) => b.delta - a.delta)) {
  console.log(
    String(c.seg).padStart(3),
    c.start.toFixed(2).padStart(6),
    c.dur.toFixed(2).padStart(5),
    c.bg.padEnd(6),
    c.delta.toFixed(4).padStart(7),
    c.worst.toFixed(4).padStart(7),
    c.ssim != null ? c.ssim.toFixed(4).padStart(7) : '      -',
  );
}
