import numpy as np, soundfile as sf, subprocess, itertools, os

REF = ".analysis/stems/htdemucs/ref-audio/vocals.wav"
SRC = ".analysis/vo-track.wav"
TMP = ".analysis/_eqtry.wav"

def ltas(path):
    x, sr = sf.read(path)
    if x.ndim > 1: x = x.mean(1)
    n, hop = 4096, 2048
    acc = np.zeros(n // 2 + 1); c = 0
    for i in range(0, len(x) - n, hop):
        w = x[i:i + n]
        if np.sqrt((w ** 2).mean()) < 0.02: continue
        acc += np.abs(np.fft.rfft(w * np.hanning(n))) ** 2; c += 1
    return np.fft.rfftfreq(n, 1 / sr), 10 * np.log10(acc / max(c, 1) + 1e-12)

def band(f, S, lo, hi):
    m = (f >= lo) & (f < hi)
    return float(S[m].mean())

fr, Sr = ltas(REF)
r0 = band(fr, Sr, 500, 800)
# only the bands where excess energy causes the muffle. Presence (2-4.5k) is
# deliberately left out: ours is brighter than the reference and should stay so.
MUD = [(80, 150), (150, 300), (300, 500), (800, 1200)]
TARGET = {b: band(fr, Sr, *b) - r0 for b in MUD}

def score(hp, g180, g260, g1k):
    af = (f"highpass=f={hp}:p=2,"
          f"equalizer=f=180:t=q:w=0.9:g={g180},"
          f"equalizer=f=260:t=q:w=1.2:g={g260},"
          f"equalizer=f=1000:t=q:w=1.2:g={g1k},"
          f"equalizer=f=3500:t=q:w=1.1:g=2.5,"
          f"acompressor=threshold=0.08:ratio=3:attack=8:release=180:makeup=2")
    subprocess.run(["ffmpeg","-v","error","-y","-i",SRC,"-af",af,TMP], check=True)
    f, S = ltas(TMP)
    o0 = band(f, S, 500, 800)
    err = sum((band(f, S, *b) - o0 - TARGET[b]) ** 2 for b in MUD)
    return err, af, {b: round(band(f, S, *b) - o0, 1) for b in MUD}

best = None
for hp in (110, 130, 150):
    for g180 in (-4, -6, -8):
        for g260 in (-2, -4):
            for g1k in (-2, -3):
                e, af, got = score(hp, g180, g260, g1k)
                if best is None or e < best[0]:
                    best = (e, af, got, hp, g180, g260, g1k)
os.remove(TMP)
e, af, got, hp, g180, g260, g1k = best
print(f"best: highpass {hp} Hz, 180 Hz {g180:+g} dB, 260 Hz {g260:+g} dB, 1k {g1k:+g} dB")
print(f"residual {np.sqrt(e/len(MUD)):.2f} dB rms across the mud bands\n")
print(f"{'band':>12s} {'reference':>9s} {'ours now':>9s}")
for b in MUD:
    print(f"{b[0]:5d}-{b[1]:5d} {TARGET[b]:+8.1f} {got[b]:+9.1f}")
open(".analysis/eq.txt", "w").write(af)
print(f"\nchain written to .analysis/eq.txt")
