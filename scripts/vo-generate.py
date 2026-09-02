"""Generate a replacement read, one clip per line, fitted to its frame budget.

Each line gets the frame it must start on and the frame before the next line
needs the air. The generator then searches speeds and keeps the one landing
closest to that budget WITHOUT exceeding it, because a line that overruns pushes
every later line off its frame while one that comes in short only leaves a
little more silence.

The lines are DATA, not code: pass a JSON file. Baking one film's script into
the skill is how this script previously only worked for the film it was written
for.

  python vo-generate.py lines.json [--voice af_heart] [--fps 30] [--out .analysis/vo]

lines.json is a list of objects, or of [tag, startFrame, endFrame, text] arrays:

  [
    {"tag": "1a", "from": 22, "to": 90,  "text": "When you run a small business,"},
    {"tag": "1b", "from": 97, "to": 135, "text": "AI can be a huge job."}
  ]

Model weights: set KOKORO_HOME, or put kokoro-v1.0.onnx and voices-v1.0.bin in
./models/kokoro/. See _models.py.
"""
import argparse
import json
import os
import sys
import warnings

import numpy as np
import soundfile as sf

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _models import kokoro_files

SPEEDS = [1.00, 1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 0.95, 0.90]

ap = argparse.ArgumentParser()
ap.add_argument('lines', help='JSON file of lines with their frame windows')
ap.add_argument('--voice', default='af_heart')
ap.add_argument('--lang', default='en-us')
ap.add_argument('--fps', type=float, default=30.0)
ap.add_argument('--out', default='.analysis/vo')
ap.add_argument('--plan', default='.analysis/vo-plan.json')
a = ap.parse_args()


def load_lines(path):
    """Accept either the object form or the terse array form."""
    raw = json.load(open(path, encoding='utf-8'))
    out = []
    for i, r in enumerate(raw):
        if isinstance(r, dict):
            out.append((str(r.get('tag', i)), int(r['from']), int(r['to']), r['text']))
        else:
            out.append((str(r[0]), int(r[1]), int(r[2]), r[3]))
    return out


def trim(x, sr, thr=0.012):
    """Strip the model's lead-in and tail so the budget measures speech.

    Untrimmed, the silence a TTS model pads each clip with counts against the
    line's budget and every line reads as over-long.
    """
    w = max(1, int(0.01 * sr))
    env = np.convolve(np.abs(x), np.ones(w) / w, 'same')
    idx = np.where(env > thr)[0]
    if not len(idx):
        return x
    pad = int(0.02 * sr)
    return x[max(0, idx[0] - pad):min(len(x), idx[-1] + pad)]


LINES = load_lines(a.lines)
model, voices = kokoro_files()
from kokoro_onnx import Kokoro
k = Kokoro(model, voices)

os.makedirs(a.out, exist_ok=True)
plan = []
for tag, f0, f1, text in LINES:
    budget = (f1 - f0) / a.fps
    best = None
    for sp in SPEEDS:
        x, sr = k.create(text, voice=a.voice, speed=sp, lang=a.lang)
        if x.ndim > 1:
            x = x.mean(1)
        x = trim(x, sr)
        d = len(x) / sr
        # overrunning is penalised four times as hard as coming in short
        cost = abs(d - budget) if d <= budget else (d - budget) * 4.0
        if best is None or cost < best[0]:
            best = (cost, sp, d, x, sr)
    _, sp, d, x, sr = best
    sf.write(os.path.join(a.out, tag + '.wav'), x, sr)
    plan.append(dict(tag=tag, start_frame=f0, start_s=round(f0 / a.fps, 3),
                     budget=round(budget, 3), dur=round(d, 3), speed=sp,
                     fit=round(d / budget, 3), text=text, sr=sr))
    print('%-3s f%-4d budget %5.2fs  got %5.2fs  speed %.2f  fit %5.1f%%  %s'
          % (tag, f0, budget, d, sp, d / budget * 100, text))

os.makedirs(os.path.dirname(a.plan) or '.', exist_ok=True)
json.dump(plan, open(a.plan, 'w'), indent=1)
over = [p for p in plan if p['fit'] > 1.0]
print('\n%d lines, %d over budget%s'
      % (len(plan), len(over), (': ' + ', '.join(p['tag'] for p in over)) if over else ''))
print('wrote %s and %s/' % (a.plan, a.out))
