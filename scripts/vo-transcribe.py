"""Transcribe the reference's isolated vocal with word-level timestamps.

The word times are the second clock: they say which frame each word lands on,
which is what lets a replacement read be placed against the original's own
rhythm rather than against a guess.

Expects the demucs vocal stem at the standard build location. Override the input
with an argument, and the cache location with HF_HOME.

  python vo-transcribe.py [vocals.wav] [--model small.en] [--out .analysis/ref-vo.json]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _models import hf_cache

DEFAULT_IN = '.analysis/stems/htdemucs/ref-audio/vocals.wav'

ap = argparse.ArgumentParser()
ap.add_argument('vocals', nargs='?', default=DEFAULT_IN)
ap.add_argument('--model', default='small.en')
ap.add_argument('--fps', type=float, default=30.0)
ap.add_argument('--out', default='.analysis/ref-vo.json')
a = ap.parse_args()

if not os.path.exists(a.vocals):
    sys.exit('no vocal stem at %s\n'
             'Separate one first:  demucs --two-stems=vocals -n htdemucs <audio>\n'
             'or pass the path as the first argument.' % a.vocals)

cache = hf_cache()
from faster_whisper import WhisperModel

m = WhisperModel(a.model, device='cpu', compute_type='int8', download_root=cache)
segs, info = m.transcribe(a.vocals, word_timestamps=True, vad_filter=False, beam_size=5)

out = []
for s in segs:
    out.append({'start': round(s.start, 3), 'end': round(s.end, 3), 'text': s.text.strip(),
                'words': [{'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)}
                          for w in (s.words or [])]})
    print('[%6.2f -> %6.2f]  f%3d-%3d  %s'
          % (s.start, s.end, int(s.start * a.fps), int(s.end * a.fps), s.text.strip()))

os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
json.dump(out, open(a.out, 'w'), indent=1)
print('\n--- words with frames ---')
for s in out:
    for w in s['words']:
        print('f%3d  %s' % (int(w['s'] * a.fps), w['w']))
print('\nwrote %s' % a.out)
