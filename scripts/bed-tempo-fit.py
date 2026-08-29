import numpy as np, json

FPS = 30.0
# Our film's own cuts. The bed should lock to the picture, not to the
# reference's music - the edit is ours, so the grid derived from it is ours too.
CUTS = [37,53,65,91,100,108,116,134,158,173,181,191,216,261,273,311,347,
        433,457,476,493,527,534,578,634,661,718]
# Weight the structural cuts - the ones a viewer feels as a section change.
MAJOR = {37,108,116,216,311,347,433,493,534,578,634,661,718}

best = []
for bpm10 in range(700, 1500):                       # 70.0 - 150.0 BPM
    bpm = bpm10 / 10.0
    fpb = 60.0 / bpm * FPS                           # frames per beat
    for off in np.arange(0, fpb, 0.5):
        err = 0.0
        for c in CUTS:
            k = round((c - off) / fpb)
            d = abs(c - (off + k * fpb))
            err += (d ** 2) * (3.0 if c in MAJOR else 1.0)
        best.append((err, bpm, float(off), fpb))
best.sort()
print(f"{'BPM':>7s} {'frames/beat':>12s} {'offset':>7s} {'err':>9s}")
for e, bpm, off, fpb in best[:6]:
    print(f"{bpm:7.1f} {fpb:12.2f} {off:7.1f} {e:9.1f}")

e, bpm, off, fpb = best[0]
print(f"\nchosen {bpm:.1f} BPM, first beat at frame {off:.1f}, {fpb:.2f} frames/beat")
print(f"bar (4 beats) = {fpb*4:.1f} frames = {fpb*4/FPS:.2f}s; "
      f"{776/(fpb*4):.1f} bars over the film\n")
print("how the structural cuts land on the grid:")
for c in sorted(MAJOR):
    k = (c - off) / fpb
    print(f"  f{c:<4d} beat {k:6.2f}  off by {abs(k-round(k))*fpb:4.1f} frames")
json.dump({"bpm": bpm, "offset": off, "fpb": fpb}, open(".analysis/grid.json","w"), indent=1)
