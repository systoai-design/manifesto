#!/usr/bin/env node
// Decode a video to a raw RGB24 plane file for random-access per-frame analysis.
// No image-decoding dependency: one ffmpeg pass, then fd reads by byte offset.
//
//   node extract.mjs <video> <outDir> [--w 640] [--h 360]
//
// Writes <outDir>/raw.bin and <outDir>/meta.json.

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const [video, outDir, ...rest] = process.argv.slice(2);
if (!video || !outDir) {
  console.error('usage: extract.mjs <video> <outDir> [--w N] [--h N]');
  process.exit(1);
}
const arg = (flag, dflt) => {
  const i = rest.indexOf(flag);
  return i === -1 ? dflt : Number(rest[i + 1]);
};
const W = arg('--w', 640);
const H = arg('--h', 360);

fs.mkdirSync(outDir, { recursive: true });

const probe = spawnSync('ffprobe', [
  '-v', 'error', '-select_streams', 'v:0', '-count_frames',
  '-show_entries', 'stream=nb_read_frames,avg_frame_rate,width,height',
  '-of', 'json', video,
], { encoding: 'utf8', maxBuffer: 1 << 26 });
if (probe.status !== 0) { console.error(probe.stderr); process.exit(1); }
const st = JSON.parse(probe.stdout).streams[0];
const [fnum, fden] = String(st.avg_frame_rate).split('/').map(Number);
const fps = fnum / (fden || 1);
const frames = Number(st.nb_read_frames);

const rawPath = path.join(outDir, 'raw.bin');
const enc = spawnSync('ffmpeg', [
  '-v', 'error', '-y', '-i', video,
  '-vf', `scale=${W}:${H}:flags=bilinear`,
  '-f', 'rawvideo', '-pix_fmt', 'rgb24', rawPath,
], { stdio: ['ignore', 'ignore', 'pipe'], encoding: 'utf8' });
if (enc.status !== 0) { console.error(enc.stderr); process.exit(1); }

const bytes = fs.statSync(rawPath).size;
const actual = bytes / (W * H * 3);
if (!Number.isInteger(actual)) {
  console.error(`raw.bin is not a whole number of ${W}x${H} frames (${actual})`);
  process.exit(1);
}

const meta = {
  source: path.resolve(video),
  w: W, h: H, fps,
  frames: actual,
  sourceFrames: frames,
  sourceW: st.width, sourceH: st.height,
  duration: actual / fps,
};
fs.writeFileSync(path.join(outDir, 'meta.json'), JSON.stringify(meta, null, 2));
console.log(JSON.stringify(meta, null, 2));
