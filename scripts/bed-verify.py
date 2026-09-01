"""Answer one question about a delivered file: which bed is actually in it?

A findings document records intent. The rendered file is a separate object, and
the two drift the moment a track is swapped in for a listening test and not
swapped back. Correlate the render's own audio against every candidate and let
the number decide - the separation is wide enough that it is never a judgement
call.

    python bed-verify.py renders/out.mp4 --against composed.wav --against supplied.mp3
"""
import argparse, subprocess, sys, tempfile, os
import numpy as np

SR = 22050  # plenty for identifying a bed, and keeps the FFT cheap


def load(path):
    """Decode anything ffmpeg reads to mono float32 at SR."""
    with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as t:
        raw = t.name
    try:
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", path, "-vn",
             "-ac", "1", "-ar", str(SR), "-f", "f32le", raw],
            check=True)
        x = np.fromfile(raw, dtype=np.float32)
    finally:
        os.unlink(raw)
    if not x.size:
        sys.exit(f"no audio stream in {path}")
    return x.astype(np.float64)


def correlate(a, b):
    """Peak normalised cross-correlation, allowing any lag.

    The bed may sit at an offset in the mix and may be scaled, so compare
    shapes rather than samples: zero-mean both, correlate via FFT, and divide
    by the energies. Voice over the top drags the peak down without moving it,
    which is why the threshold is loose and the gap between candidates is what
    carries the verdict.
    """
    n = len(a) + len(b)
    nfft = 1 << (n - 1).bit_length()
    a = a - a.mean()
    b = b - b.mean()
    A = np.fft.rfft(a, nfft)
    B = np.fft.rfft(b, nfft)
    c = np.fft.irfft(A * np.conj(B), nfft)
    denom = np.sqrt((a @ a) * (b @ b))
    if denom == 0:
        return 0.0, 0
    peak = int(np.argmax(np.abs(c)))
    lag = peak if peak < nfft // 2 else peak - nfft
    return float(np.abs(c[peak]) / denom), lag


ap = argparse.ArgumentParser()
ap.add_argument("render", help="the delivered file, or any audio")
ap.add_argument("--against", action="append", required=True, metavar="FILE",
                help="candidate bed; repeat for each one you want ruled out")
a = ap.parse_args()

mix = load(a.render)
print(f"{os.path.basename(a.render)}: {len(mix)/SR:.2f}s\n")
print(f"{'candidate':<38}{'corr':>8}{'lag':>10}")

scored = []
for cand in a.against:
    r, lag = correlate(mix, load(cand))
    scored.append((r, cand))
    print(f"{os.path.basename(cand):<38}{r:8.3f}{lag/SR:9.2f}s")

scored.sort(reverse=True)
best, runner = scored[0], (scored[1] if len(scored) > 1 else None)
print(f"\nin the file: {os.path.basename(best[1])} ({best[0]:.3f})")
if runner and best[0] - runner[0] < 0.15:
    print(f"NOT CONCLUSIVE - {os.path.basename(runner[1])} scores {runner[0]:.3f}. "
          f"Candidates sharing an arrangement can both correlate; separate them by ear.")
