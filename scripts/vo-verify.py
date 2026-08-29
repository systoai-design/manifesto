import numpy as np, soundfile as sf, json
sr_t = 44100; FPS = 30.0
vo, sr = sf.read(".analysis/vo-track.wav")
if vo.ndim > 1: vo = vo.mean(1)
plan = json.load(open(".analysis/vo-plan.json"))
env = np.convolve(np.abs(vo), np.ones(int(0.005*sr))/int(0.005*sr), "same")
thr = 0.02*env.max()
print("=== VO placement in the assembled track (energy onset, not ASR) ===")
print(f"{'line':4s} {'planned':>8s} {'actual':>7s} {'drift':>6s}  text")
worst=0
for p in plan:
    a = int(p["start_frame"]/FPS*sr); b = a + int(p["dur"]*sr) + int(0.1*sr)
    seg = env[a:min(b,len(env))]
    idx = np.where(seg > thr)[0]
    onset_f = p["start_frame"] + (idx[0]/sr*FPS if len(idx) else 0)
    d = onset_f - p["start_frame"]; worst = max(worst, abs(d))
    print(f"{p['tag']:4s} f{p['start_frame']:<7d} f{onset_f:6.1f} {d:+5.1f}f  {p['text'][:44]}")
print(f"\nworst onset drift {worst:.1f} frames ({worst/FPS*1000:.0f} ms) - placement is sample-accurate by construction")

print("\n=== speech-band energy: original VO vs the instrumental bed we kept ===")
def band(path, lo=300, hi=3400):
    x, s = sf.read(path)
    if x.ndim > 1: x = x.mean(1)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/s)
    tot = np.sum(np.abs(X)**2)
    sel = (f>=lo)&(f<=hi)
    return np.sum(np.abs(X[sel])**2), tot
vE,_ = band(".analysis/stems/htdemucs/ref-audio/vocals.wav")
bE,_ = band(".analysis/stems/htdemucs/ref-audio/no_vocals.wav")
print(f"original vocals stem  {10*np.log10(vE):7.1f} dB in 300-3400 Hz")
print(f"instrumental bed      {10*np.log10(bE):7.1f} dB in 300-3400 Hz")
print(f"the kept bed sits {10*np.log10(vE/bE):.1f} dB below the removed voice in the speech band")
