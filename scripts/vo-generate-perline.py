"""
Generate the film's read, one line at a time.

Voice is Kokoro `af_heart` -- the same local model and voice used for the Apple
motion replication in D:/New Claude/motion-replicate, whose read this film is
matching.

Two things here are deliberate and both fix real complaints about the previous
ElevenLabs pass:

  * ONE GENERATION PER LINE. The previous read was a single 36-line request with
    <break> tags, and the model drifted across it -- delivery wandered and some
    lines came out noticeably quieter than their neighbours. A line generated on
    its own cannot drift relative to any other line.

  * LEVELS RECONCILED AFTERWARDS. Each line is pulled toward a common RMS, but
    only most of the way (see LEVEL_PULL), so the read stays even without being
    flattened into a monotone.

Because every gap is authored here rather than discovered afterwards, this also
emits the timeline directly -- no transcription step, and each line lands exactly
where it was placed rather than within a tolerance of it.

  usage: <venv-python> scripts/generate_vo.py
"""

import io
import json
import os
import sys

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

MODEL = "D:/kokoro/kokoro-v1.0.onnx"
VOICES = "D:/kokoro/voices-v1.0.bin"
VOICE = "af_heart"

SR_OUT = 48000

# How far each line is pulled toward the common level. 1.0 would make every
# line identical and kill the read's dynamics; 0.0 leaves the drift that was
# the complaint. 0.75 removes the swings and keeps the shape.
LEVEL_PULL = 0.75

# (line, pause after it in seconds, speed).
#
# The 35-second cut. 22.5s of speech against 33.2s in the long version -- a
# third of the script gone -- so every remaining line is load-bearing.
#
# What survives and why: the two verb runs, because the burden returning is
# Act 1's whole argument and it is the SECOND "Again." that earns "Enough.";
# the tool/operator contrast, because "operator" means nothing without the
# thing it is not; and "Nothing ships until a person says yes", because a film
# about handing work to AI cannot drop the line where the human stays in it.
#
# What went: the calendar's line, the second conveyor run, the whole
# manage-them-at-all beat, and "That's the whole job."
#
# Gaps are allocated, not uniform. Verb runs get 0.2s so the list reads as
# closing in; the turn gets a second; speed drops under 1.0 on the weighted
# lines because this register is certain, and certainty is slow.
SCRIPT: list[tuple[str, float, float]] = [
    ("You started a business.", 0.42, 0.95),
    ("Then it started running you.", 0.52, 0.95),
    ("Answer it.", 0.20, 1.03),
    ("Chase it.", 0.34, 1.03),
    ("Again. Again. And again.", 0.50, 0.93),
    ("Post it.", 0.20, 1.05),
    ("Send it.", 0.38, 1.05),
    ("Again.", 0.55, 0.90),
    ("Enough.", 0.88, 0.88),
    ("Software doesn't run a business.", 0.34, 0.95),
    ("People do.", 0.60, 0.92),
    ("We don't hand you a tool.", 0.32, 0.98),
    ("We hand you an operator.", 0.44, 0.92),
    ("A person.", 0.56, 0.90),
    ("They answer it.", 0.22, 1.00),
    ("They chase it.", 0.22, 1.00),
    ("They book it.", 0.34, 1.00),
    ("All of it.", 0.46, 0.92),
    ("In your name.", 0.56, 0.92),
    ("Nothing ships until a person says yes.", 0.62, 0.94),
    ("You own the AI.", 0.34, 0.94),
    ("We operate it.", 0.60, 0.92),
    ("Systo. Hire an operator.", 0.0, 0.92),
]

# Silence inserted BEFORE a line, for the beats where the animation is the line.
# There are only two now: at 35s there is no room for a wordless sequence, so
# the mascot act is gone and the blackout is the film's one held breath.
STRUCTURAL: dict[int, float] = {
    0: 0.90,    # cold open
    9: 0.72,    # the blackout, on top of the pause after "Enough."
}
TAIL = 1.65


def trim(x: np.ndarray, sr: int, thr: float = 0.012) -> np.ndarray:
    """Strip the model's lead-in/out silence so the authored gap is the only gap."""
    w = int(0.01 * sr)
    env = np.convolve(np.abs(x), np.ones(w) / w, "same")
    idx = np.where(env > thr)[0]
    if len(idx) == 0:
        return x
    pad = int(0.02 * sr)
    return x[max(0, idx[0] - pad): min(len(x), idx[-1] + pad)]


def main() -> None:
    k = Kokoro(MODEL, VOICES)

    clips, sr = [], None
    for i, (text, _, speed) in enumerate(SCRIPT):
        x, sr = k.create(text, voice=VOICE, speed=speed, lang="en-us")
        if x.ndim > 1:
            x = x.mean(1)
        x = trim(np.asarray(x, dtype=np.float64), sr)
        clips.append(x)
        print(f"{i:3d}  {len(x)/sr:5.2f}s  sp {speed:.2f}  {text}")

    rms = np.array([np.sqrt((c ** 2).mean() + 1e-12) for c in clips])
    target = float(np.median(rms))
    print(f"\nlevel: median RMS {20*np.log10(target):.2f} dB, "
          f"spread {20*np.log10(rms.max()/rms.min()):.2f} dB before")
    clips = [c * (1.0 + LEVEL_PULL * (target / r - 1.0)) for c, r in zip(clips, rms)]
    after = np.array([np.sqrt((c ** 2).mean() + 1e-12) for c in clips])
    print(f"       spread {20*np.log10(after.max()/after.min()):.2f} dB after")

    sil = lambda d: np.zeros(int(d * sr))
    out, lines, t = [], [], 0.0
    for i, (c, (text, gap, _)) in enumerate(zip(clips, SCRIPT)):
        if i in STRUCTURAL:
            out.append(sil(STRUCTURAL[i]))
            t += STRUCTURAL[i]
        at = t
        out.append(c)
        t += len(c) / sr
        lines.append({"i": i, "text": text, "at": round(at, 3), "end": round(t, 3),
                      "raw": [round(at, 3), round(t, 3)],
                      "gap_before": None if not i else round(at - lines[-1]["end"], 3)})
        if gap:
            out.append(sil(gap))
            t += gap
    out.append(sil(TAIL))
    t += TAIL

    y = np.concatenate(out)
    peak = np.abs(y).max()
    y = y / peak * 0.89 if peak > 0 else y

    os.makedirs("public", exist_ok=True)
    sf.write("public/vo-raw.wav", y, sr)
    os.system(
        f'ffmpeg -y -v error -i public/vo-raw.wav -ar {SR_OUT} -ac 2 '
        f'-af "highpass=f=75,loudnorm=I=-16:TP=-1.5:LRA=7" public/vo.wav'
    )

    io.open("scripts/vo-timing.json", "w", encoding="utf-8").write(
        json.dumps({"total": round(t, 3), "lines": lines}, indent=2))

    print(f"\n{'#':>3} {'at':>7} {'end':>7} {'gap':>6}  line")
    for o in lines:
        g = f"{o['gap_before']:.2f}" if o["gap_before"] is not None else "  -"
        print(f"{o['i']:3d} {o['at']:7.3f} {o['end']:7.3f} {g:>6}  {o['text']}")
    print(f"\nTOTAL {t:.3f}s -> public/vo.wav")


if __name__ == "__main__":
    main()
