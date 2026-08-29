import numpy as np, soundfile as sf, json

x, sr = sf.read(".analysis/stems/htdemucs/ref-audio/no_vocals.wav")
if x.ndim > 1: x = x.mean(1)
FPS = 30.0

# ---- tempo, from the onset envelope's autocorrelation ----------------------
n, hop = 2048, 256
S = np.array([np.abs(np.fft.rfft(x[i:i+n] * np.hanning(n)))
              for i in range(0, len(x)-n, hop)])
flux = np.maximum(0, np.diff(S, axis=0)).sum(1)
flux = (flux - flux.mean()) / (flux.std() + 1e-9)
fps_env = sr / hop
ac = np.correlate(flux, flux, "full")[len(flux)-1:]
lo, hi = int(fps_env * 60/200), int(fps_env * 60/60)      # 60-200 BPM
bpm = 60 * fps_env / (lo + int(np.argmax(ac[lo:hi])))
print(f"bed tempo          {bpm:5.1f} BPM   ({60/bpm:.3f}s per beat, {60/bpm*FPS:.1f} frames)")

# ---- tonic, from the long-term spectrum folded to pitch classes ------------
NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
mag = np.abs(np.fft.rfft(x * np.hanning(len(x))))
freq = np.fft.rfftfreq(len(x), 1/sr)
pc = np.zeros(12)
m = (freq > 55) & (freq < 2000)
midi = 69 + 12*np.log2(freq[m]/440.0)
np.add.at(pc, np.round(midi).astype(int) % 12, mag[m]**2)
pc /= pc.max()
order = np.argsort(pc)[::-1]
print(f"strongest pitches  {', '.join(f'{NAMES[i]} ({pc[i]:.2f})' for i in order[:5])}")

# ---- energy arc, per second, and where the big moves are ------------------
sec = int(sr)
lv = np.array([20*np.log10(np.sqrt((x[i:i+sec]**2).mean())+1e-12)
               for i in range(0, len(x)-sec, sec)])
print(f"\nenergy arc, 1 s buckets (dBFS):")
print("  " + " ".join(f"{v:.0f}" for v in lv))
print(f"  range {lv.min():.1f} to {lv.max():.1f} dB, quietest at {int(np.argmin(lv))}s, "
      f"loudest at {int(np.argmax(lv))}s")

# ---- how much room does it leave the voice? -------------------------------
def band(lo_, hi_):
    mm = (freq >= lo_) & (freq < hi_)
    return 10*np.log10((mag[mm]**2).mean() + 1e-12)
ref = band(500, 800)
print(f"\nspectral shape, relative to its own 500-800 Hz:")
for lo_, hi_ in [(30,80),(80,150),(150,300),(300,500),(500,800),(800,1500),
                 (1500,3000),(3000,6000),(6000,12000)]:
    print(f"  {lo_:5d}-{hi_:5d} Hz  {band(lo_,hi_)-ref:+6.1f} dB")
json.dump({"bpm": float(bpm), "arc": [float(v) for v in lv]},
          open(".analysis/bed-analysis.json","w"), indent=1)
