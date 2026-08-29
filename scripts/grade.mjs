#!/usr/bin/env node
// Grade a replica against its reference, per card, against each card's own
// ceiling — never as one blended number for the film.
//
//   node grade.mjs <refVideo> <mineVideo> --beats <beats.json> [--out DIR]
//                  [--w 640] [--h 360] [--diffmaps] [--target 99]
//
// Three numbers per card, all in the same units so they can be compared:
//   similarity   100 - mean|delta| / 255 * 100      (swipefile's measure)
//   within16     % of pixels whose channels all differ by <= 16/255
//   ceiling      the same similarity measured reference-vs-REENCODED-reference
//
// The ceiling matters: both files are lossy H.264, so even a pixel-perfect
// clone cannot score 100. A card sitting at its ceiling is FINISHED. Chasing it
// further measures the codec, not the replica. Grades are therefore reported as
// a percentage OF the ceiling, and that is the number to drive to 99-100.

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const [refVideo, mineVideo, ...rest] = process.argv.slice(2);
const sarg = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : rest[i + 1]; };
const narg = (f, d) => { const i = rest.indexOf(f); return i === -1 ? d : Number(rest[i + 1]); };
const has = f => rest.includes(f);
if (!refVideo || !mineVideo) {
  console.error('usage: grade.mjs <refVideo> <mineVideo> --beats beats.json [--out DIR] [--diffmaps]');
  process.exit(1);
}
const W = narg('--w', 640), H = narg('--h', 360);
const OUT = sarg('--out', '.grade');
const TARGET = narg('--target', 99);
const beatsPath = sarg('--beats', null);
fs.mkdirSync(OUT, { recursive: true });

const FRAME = W * H * 3;
function decode(video, tag) {
  const out = path.join(OUT, tag + '.bin');
  const r = spawnSync('ffmpeg', ['-v', 'error', '-y', '-i', video,
    '-vf', `scale=${W}:${H}:flags=bilinear`, '-f', 'rawvideo', '-pix_fmt', 'rgb24', out],
    { encoding: 'utf8' });
  if (r.status !== 0) { console.error(r.stderr); process.exit(1); }
  return out;
}

// The ceiling arm: push the reference through an encode/decode cycle so we can
// measure how much of the residual is simply codec noise.
const reenc = path.join(OUT, 'ref-reencoded.mp4');
if (!fs.existsSync(reenc)) {
  const r = spawnSync('ffmpeg', ['-v', 'error', '-y', '-i', refVideo,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-an', reenc],
    { encoding: 'utf8' });
  if (r.status !== 0) { console.error('re-encode failed:\n' + r.stderr); process.exit(1); }
}

const refBin = decode(refVideo, 'ref');
const mineBin = decode(mineVideo, 'mine');
const ceilBin = decode(reenc, 'ceil');

const nRef = fs.statSync(refBin).size / FRAME;
const nMine = fs.statSync(mineBin).size / FRAME;
const nCeil = fs.statSync(ceilBin).size / FRAME;
const N = Math.min(nRef, nMine, nCeil);

const fdR = fs.openSync(refBin, 'r'), fdM = fs.openSync(mineBin, 'r'), fdC = fs.openSync(ceilBin, 'r');
const bR = Buffer.allocUnsafe(FRAME), bM = Buffer.allocUnsafe(FRAME), bC = Buffer.allocUnsafe(FRAME);

// per-frame stats for both arms
const sim = new Float64Array(N), w16 = new Float64Array(N);
const csim = new Float64Array(N), cw16 = new Float64Array(N);
const worstPix = new Float64Array(N);

function statPair(a, b) {
  let sum = 0, ok = 0, mx = 0;
  for (let i = 0; i < FRAME; i += 3) {
    const d0 = Math.abs(a[i] - b[i]), d1 = Math.abs(a[i + 1] - b[i + 1]), d2 = Math.abs(a[i + 2] - b[i + 2]);
    sum += d0 + d1 + d2;
    const m = d0 > d1 ? (d0 > d2 ? d0 : d2) : (d1 > d2 ? d1 : d2);
    if (m <= 16) ok++;
    if (m > mx) mx = m;
  }
  const px = FRAME / 3;
  return { sim: 100 - (sum / FRAME) / 255 * 100, w16: ok / px * 100, max: mx };
}

for (let f = 0; f < N; f++) {
  fs.readSync(fdR, bR, 0, FRAME, f * FRAME);
  fs.readSync(fdM, bM, 0, FRAME, f * FRAME);
  fs.readSync(fdC, bC, 0, FRAME, f * FRAME);
  const a = statPair(bR, bM); sim[f] = a.sim; w16[f] = a.w16; worstPix[f] = a.max;
  const c = statPair(bR, bC); csim[f] = c.sim; cw16[f] = c.w16;
}
fs.closeSync(fdR); fs.closeSync(fdM); fs.closeSync(fdC);

// ---- cards
let cards;
if (beatsPath && fs.existsSync(beatsPath)) {
  const B = JSON.parse(fs.readFileSync(beatsPath, 'utf8'));
  cards = B.segments.map(s => ({
    id: 's' + s.index, start: s.startFrame, end: Math.min(s.endFrame, N - 1), t: s.start,
  })).filter(c => c.end >= c.start);
} else {
  cards = [];
  for (let a = 0; a < N; a += 30) cards.push({ id: 'f' + a, start: a, end: Math.min(a + 29, N - 1), t: a / 30 });
}

const mean = (arr, a, b) => { let s = 0; for (let i = a; i <= b; i++) s += arr[i]; return s / (b - a + 1); };

function letter(p) {
  if (p >= 99.5) return 'A+'; if (p >= 99) return 'A'; if (p >= 98) return 'A-';
  if (p >= 96) return 'B+'; if (p >= 94) return 'B'; if (p >= 92) return 'B-';
  if (p >= 88) return 'C+'; if (p >= 84) return 'C'; if (p >= 80) return 'C-';
  if (p >= 70) return 'D'; return 'F';
}

const rows = cards.map(c => {
  const s = mean(sim, c.start, c.end), ceil = mean(csim, c.start, c.end);
  const pct = ceil > 0 ? Math.min(100, s / ceil * 100) : 0;
  let worstF = c.start, worstV = Infinity;
  for (let i = c.start; i <= c.end; i++) if (sim[i] < worstV) { worstV = sim[i]; worstF = i; }
  return {
    ...c, frames: c.end - c.start + 1,
    sim: s, ceiling: ceil, pctOfCeiling: pct, grade: letter(pct),
    within16: mean(w16, c.start, c.end), ceilWithin16: mean(cw16, c.start, c.end),
    worstFrame: worstF, worstSim: worstV,
    done: pct >= TARGET,
  };
});

const overallSim = mean(sim, 0, N - 1), overallCeil = mean(csim, 0, N - 1);
const overallPct = Math.min(100, overallSim / overallCeil * 100);

const report = {
  refVideo, mineVideo, frames: { ref: nRef, mine: nMine, compared: N },
  frameCountMatch: nRef === nMine,
  overall: {
    similarity: +overallSim.toFixed(3), ceiling: +overallCeil.toFixed(3),
    pctOfCeiling: +overallPct.toFixed(2), grade: letter(overallPct),
    within16: +mean(w16, 0, N - 1).toFixed(2), ceilWithin16: +mean(cw16, 0, N - 1).toFixed(2),
  },
  target: TARGET,
  cardsBelowTarget: rows.filter(r => !r.done).length,
  cards: rows.map(r => ({
    id: r.id, t: r.t, frames: r.frames,
    similarity: +r.sim.toFixed(3), ceiling: +r.ceiling.toFixed(3),
    pctOfCeiling: +r.pctOfCeiling.toFixed(2), grade: r.grade,
    within16: +r.within16.toFixed(2), worstFrame: r.worstFrame,
    worstSim: +r.worstSim.toFixed(3), done: r.done,
  })),
};
fs.writeFileSync(path.join(OUT, 'grade.json'), JSON.stringify(report, null, 2));

// ---- diffmaps for the worst cards
if (has('--diffmaps')) {
  const worst = [...rows].sort((a, b) => a.pctOfCeiling - b.pctOfCeiling).slice(0, 6);
  for (const c of worst) {
    const f = c.worstFrame;
    spawnSync('ffmpeg', ['-v', 'error', '-y',
      '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', `${W}x${H}`, '-i', refBin,
      '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', `${W}x${H}`, '-i', mineBin,
      '-filter_complex',
      `[0:v]select=eq(n\\,${f})[a];[1:v]select=eq(n\\,${f})[b];` +
      `[a][b]blend=all_mode=difference,eq=contrast=4:brightness=0.1`,
      '-frames:v', '1', '-vsync', '0', path.join(OUT, `diff-${c.id}-f${f}.png`)]);
  }
}

// ---- report
const g = report.overall;
console.log(`\n  ${refVideo.split(/[\\/]/).pop()}  vs  ${mineVideo.split(/[\\/]/).pop()}`);
console.log(`  frames ref=${nRef} mine=${nMine}` + (report.frameCountMatch ? '  (match)' : '  ** MISMATCH **'));
console.log(`\n  OVERALL  ${g.pctOfCeiling}% of ceiling   grade ${g.grade}`);
console.log(`           similarity ${g.similarity}%   ceiling ${g.ceiling}%   within16 ${g.within16}% (ceiling ${g.ceilWithin16}%)`);
console.log(`  ${report.cardsBelowTarget} of ${rows.length} cards below the ${TARGET}% target\n`);
console.log('  card   t       n    sim%    ceil%   %ceil  grade  within16  worst@');
for (const r of [...rows].sort((a, b) => a.pctOfCeiling - b.pctOfCeiling)) {
  console.log(
    '  ' + r.id.padEnd(5),
    String(r.t.toFixed(2)).padStart(6),
    String(r.frames).padStart(4),
    r.sim.toFixed(2).padStart(7),
    r.ceiling.toFixed(2).padStart(8),
    r.pctOfCeiling.toFixed(2).padStart(7),
    ' ' + r.grade.padEnd(5),
    r.within16.toFixed(1).padStart(7) + '%',
    String('f' + r.worstFrame).padStart(7),
    r.done ? '' : '  <-- below target',
  );
}
console.log(`\n  wrote ${path.join(OUT, 'grade.json')}`);
