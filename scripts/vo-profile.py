import numpy as np, soundfile as sf, json
x, sr = sf.read(".analysis/stems/htdemucs/ref-audio/vocals.wav")
if x.ndim > 1: x = x.mean(1)
vo = json.load(open(".analysis/ref-vo.json"))
# autocorrelation pitch over voiced frames only, inside transcribed spans
f0s = []
for s in vo:
    a, b = int(s["start"]*sr), int(s["end"]*sr)
    seg = x[a:b]
    win = int(0.04*sr); hop = int(0.01*sr)
    for i in range(0, max(0,len(seg)-win), hop):
        w = seg[i:i+win]
        if np.sqrt((w**2).mean()) < 0.02: continue
        w = w - w.mean()
        c = np.correlate(w, w, "full")[win-1:]
        lo, hi = int(sr/300), int(sr/70)          # 70-300 Hz search
        if hi >= len(c): continue
        pk = lo + int(np.argmax(c[lo:hi]))
        if c[pk] > 0.30*c[0]: f0s.append(sr/pk)
f0s = np.array(f0s)
words = sum(len(s["words"]) for s in vo)
speech = sum(s["end"]-s["start"] for s in vo)
print(f"voiced frames      {len(f0s)}")
print(f"median f0          {np.median(f0s):.1f} Hz   (male 85-155, female 165-255)")
print(f"f0 10-90 pct       {np.percentile(f0s,10):.0f} - {np.percentile(f0s,90):.0f} Hz")
print(f"words              {words}")
print(f"speech time        {speech:.2f}s of 25.87s  ({speech/25.87*100:.0f}% talking)")
print(f"rate               {words/speech:.2f} words/sec  ({words/speech*60:.0f} wpm)")
