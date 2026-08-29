#!/usr/bin/env node
// Detect audio onsets and test whether the reference's picture cuts are locked
// to them. If they are, the soundtrack is a second, independent clock you can
// align the replica against — and any cut that drifts off it reads as "wrong"
// even when the picture alone looks fine.
//
//   node audio-beats.mjs <video> [--dir <analysisDir>] [--fps 30]
//
// With --dir, cross-references the cut list in <analysisDir>/beats.json.

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const video = process.argv[2];
const rest = process.argv.slice(3);
const sarg = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : rest[i + 1]; };
const narg = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : Number(rest[i + 1]); };
if (!video) { console.error('usage: audio-beats.mjs <video> [--dir D] [--fps N]'); process.exit(1); }
const FPS = narg('--fps', 30);
const dir = sarg('--dir', null);

// Mono 8 kHz signed 16-bit — plenty for an energy envelope.
const SR = 8000;
const r = spawnSync('ffmpeg', ['-v', 'error', '-i', video, '-vn',
  '-ac', '1', '-ar', String(SR), '-f', 's16le', '-'],
  { maxBuffer: 1 << 28 });
if (r.status !== 0 || !r.stdout || !r.stdout.length) {
  console.error('no audio track, or ffmpeg failed');
  process.exit(1);
}
const pcm = new Int16Array(r.stdout.buffer, r.stdout.byteOffset,
  Math.floor(r.stdout.length / 2));

// RMS per video frame
const hop = Math.round(SR / FPS);
const nF = Math.floor(pcm.length / hop);
const rms = new Float64Array(nF);
for (let f = 0; f < nF; f++) {
  let s = 0;
  for (let i = f * hop; i < (f + 1) * hop; i++) s += pcm[i] * pcm[i];
  rms[f] = Math.sqrt(s / hop) / 32768;
}
// Spectral-flux-ish onset strength: positive energy jumps vs local median
const onset = new Float64Array(nF);
const WIN = 8;
for (let f = 1; f < nF; f++) {
  const a = Math.max(0, f - WIN);
  const local = Array.from(rms.slice(a, f)).sort((x, y) => x - y);
  const med = local.length ? local[local.length >> 1] : 0;
  onset[f] = Math.max(0, rms[f] - Math.max(med, rms[f - 1]));
}
const sorted = Array.from(onset).sort((a, b) => a - b);
const thresh = sorted[Math.floor(sorted.length * 0.94)] || 1e-9;

const peaks = [];
for (let f = 1; f < nF - 1; f++) {
  if (onset[f] > thresh && onset[f] >= onset[f - 1] && onset[f] >= onset[f + 1]) {
    if (!peaks.length || f - peaks[peaks.length - 1] >= 4) peaks.push(f);
  }
}

console.log(`audio ${(pcm.length / SR).toFixed(3)}s -> ${nF} frames @${FPS}fps`);
console.log(`${peaks.length} onsets (94th pct threshold)\n`);
console.log('onset frames: ' + peaks.map(f => `${f}(${(f / FPS).toFixed(2)}s)`).join('  '));

if (dir && fs.existsSync(path.join(dir, 'beats.json'))) {
  const B = JSON.parse(fs.readFileSync(path.join(dir, 'beats.json'), 'utf8'));
  const cuts = B.segments.map(s => s.startFrame);
  let hits = 0;
  const rows = [];
  for (const c of cuts) {
    let best = null;
    for (const p of peaks) {
      const d = p - c;
      if (best === null || Math.abs(d) < Math.abs(best)) best = d;
    }
    if (best !== null && Math.abs(best) <= 3) hits++;
    rows.push({ cut: c, t: +(c / FPS).toFixed(3), nearestOnsetDelta: best });
  }
  console.log(`\ncuts locked to an onset (within 3 frames): ${hits}/${cuts.length}`);
  console.log('\ncut    t       onsetDelta(frames)');
  for (const r of rows) {
    console.log(String(r.cut).padStart(4), r.t.toFixed(3).padStart(7),
      String(r.nearestOnsetDelta).padStart(8),
      Math.abs(r.nearestOnsetDelta) <= 3 ? '  <- locked' : '');
  }
  fs.writeFileSync(path.join(dir, 'audio.json'),
    JSON.stringify({ fps: FPS, onsets: peaks, cuts: rows }, null, 2));
}
