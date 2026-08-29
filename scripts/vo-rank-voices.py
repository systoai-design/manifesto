import numpy as np, soundfile as sf, subprocess, glob, os, json
TARGET_F0 = 216.7
def prof(path):
    wav = path + ".conv.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-i",path,"-ar","44100","-ac","1",wav],check=True)
    x, sr = sf.read(wav); os.remove(wav)
    if x.ndim > 1: x = x.mean(1)
    win, hop = int(0.04*sr), int(0.01*sr)
    f0s, voiced = [], 0
    for i in range(0, max(0,len(x)-win), hop):
        w = x[i:i+win]
        if np.sqrt((w**2).mean()) < 0.02: continue
        voiced += 1
        w = w - w.mean()
        c = np.correlate(w,w,"full")[win-1:]
        lo, hi = int(sr/300), int(sr/70)
        if hi >= len(c): continue
        pk = lo + int(np.argmax(c[lo:hi]))
        if c[pk] > 0.30*c[0]: f0s.append(sr/pk)
    if len(f0s) < 30: return None
    f0s = np.array(f0s)
    return dict(f0=float(np.median(f0s)), spread=float(np.percentile(f0s,90)-np.percentile(f0s,10)),
                voiced_ratio=voiced/max(1,(len(x)-win)//hop), dur=len(x)/sr)
rows=[]
for name, vid, url in json.load(open(".analysis/voices.json")):
    p = glob.glob(f".analysis/voices/{name}.*")
    if not p: continue
    try: r = prof(p[0])
    except Exception as e: r=None
    if r: rows.append((name, vid, r))
rows.sort(key=lambda t: abs(t[2]["f0"]-TARGET_F0))
print(f"reference VO: f0 {TARGET_F0} Hz, spread 114 Hz, 194 wpm\n")
print(f"{'voice':10s} {'f0':>7s} {'d_f0':>6s} {'spread':>7s} {'voiced':>7s}")
for name, vid, r in rows:
    print(f"{name:10s} {r['f0']:6.1f}  {r['f0']-TARGET_F0:+6.1f}  {r['spread']:6.0f}  {r['voiced_ratio']*100:6.0f}%")
json.dump([{"name":n,"id":v,**r} for n,v,r in rows], open(".analysis/voice-rank.json","w"), indent=1)
