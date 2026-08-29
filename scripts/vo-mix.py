import numpy as np, soundfile as sf, json, subprocess
FPS, DUR = 30.0, 776/30.0
bed, sr = sf.read(".analysis/stems/htdemucs/ref-audio/no_vocals.wav")
if bed.ndim == 1: bed = np.stack([bed, bed], 1)
N = int(round(DUR*sr))
bed = bed[:N] if len(bed) >= N else np.pad(bed, ((0, N-len(bed)), (0,0)))
vo = np.zeros((N, 2), dtype=np.float64)
plan = json.load(open(".analysis/vo-plan.json"))
for p in plan:
    x, xsr = sf.read(f".analysis/vo/{p['tag']}.wav")
    assert xsr == sr, (xsr, sr)
    if x.ndim == 1: x = np.stack([x, x], 1)
    a = int(round(p["start_frame"]/FPS*sr))
    b = min(N, a+len(x))
    # 8ms ramps so a placed clip never clicks at its edges
    r = int(0.008*sr); seg = x[:b-a].copy()
    if len(seg) > 2*r:
        seg[:r] *= np.linspace(0,1,r)[:,None]; seg[-r:] *= np.linspace(1,0,r)[:,None]
    vo[a:b] += seg
def lufs_gain(x, target):
    rms = np.sqrt((x**2).mean()); return target/max(rms,1e-9)
vo *= lufs_gain(vo[np.abs(vo).max(1) > 0.01], 0.13)     # voice forward
bed *= lufs_gain(bed, 0.055)                             # bed under it
sf.write(".analysis/vo-track.wav", np.clip(vo,-1,1), sr)
sf.write(".analysis/bed-track.wav", np.clip(bed,-1,1), sr)
print(f"VO track  {len(plan)} lines placed, {vo.shape[0]/sr:.3f}s")
print(f"bed       {bed.shape[0]/sr:.3f}s")
