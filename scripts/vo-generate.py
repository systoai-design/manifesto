import numpy as np, soundfile as sf, json, os, warnings
warnings.filterwarnings("ignore")
from kokoro_onnx import Kokoro
k = Kokoro("D:/kokoro/kokoro-v1.0.onnx", "D:/kokoro/voices-v1.0.bin")
VOICE = "af_heart"
FPS = 30.0
# Windows taken from the reference VO's own word timings: each line starts on
# the frame the original speaker started, and its budget runs to the frame
# before the next line needs the air.
LINES = [
 ("1a",  22,  90, "When you run a small business,"),
 ("1b",  97, 135, "AI can be a huge job."),
 ("2",  160, 210, "At first, there was just one of you."),
 ("3a", 217, 250, "One tool."),
 ("3b", 258, 290, "Then it was six."),
 ("4",  310, 412, "And six tools could mean twenty logins to manage."),
 ("5a", 457, 490, "That's not automation."),
 ("5b", 493, 548, "That's just more work for you."),
 ("6",  572, 612, "That's where we come in."),
 ("7",  632, 694, "Introducing Sisto."),
 ("8",  719, 774, "You own the AI. We operate it."),
]
os.makedirs(".analysis/vo", exist_ok=True)
def trim(x, sr, thr=0.012):
    e = np.abs(x)
    w = int(0.01*sr)
    env = np.convolve(e, np.ones(w)/w, "same")
    idx = np.where(env > thr)[0]
    if len(idx) == 0: return x
    pad = int(0.02*sr)
    return x[max(0,idx[0]-pad):min(len(x),idx[-1]+pad)]
out = []
for tag, f0, f1, text in LINES:
    budget = (f1 - f0) / FPS
    # find the speed that lands closest to the budget without exceeding it
    best = None
    for sp in [1.00,1.05,1.10,1.15,1.20,1.25,1.30,0.95,0.90]:
        x, sr = k.create(text, voice=VOICE, speed=sp, lang="en-us")
        if x.ndim > 1: x = x.mean(1)
        x = trim(x, sr)
        d = len(x)/sr
        cand = (abs(d-budget) if d <= budget else (d-budget)*4.0, sp, d, x, sr)
        if best is None or cand[0] < best[0]: best = cand
    _, sp, d, x, sr = best
    sf.write(f".analysis/vo/{tag}.wav", x, sr)
    out.append(dict(tag=tag, start_frame=f0, start_s=round(f0/FPS,3), budget=round(budget,3),
                    dur=round(d,3), speed=sp, fit=round(d/budget,3), text=text, sr=sr))
    print(f"{tag:3s} f{f0:<4d} budget {budget:5.2f}s  got {d:5.2f}s  speed {sp:.2f}  fit {d/budget*100:5.1f}%  {text}")
json.dump(out, open(".analysis/vo-plan.json","w"), indent=1)
over = [o for o in out if o["fit"] > 1.0]
print(f"\n{len(out)} lines, {len(over)} over budget" + (": " + ", ".join(o['tag'] for o in over) if over else ""))
