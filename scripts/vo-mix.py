import numpy as np, soundfile as sf, json
FPS, N_F = 30.0, 776
TARGET_DB = json.load(open(".analysis/mixratio.json"))["voice_over_bed_db"]
vo, sr = sf.read(".analysis/vo-eq.wav")
bed, sr2 = sf.read(".analysis/stems/htdemucs/ref-audio/no_vocals.wav")
assert sr == sr2
if vo.ndim == 1: vo = np.stack([vo,vo],1)
if bed.ndim == 1: bed = np.stack([bed,bed],1)
N = int(round(N_F/FPS*sr))
def fit(x):
    return x[:N] if len(x) >= N else np.pad(x, ((0,N-len(x)),(0,0)))
vo, bed = fit(vo), fit(bed)
# speech mask from the placed clips, so the ratio is measured where it matters
plan = json.load(open(".analysis/vo-plan.json"))
m = np.zeros(N, bool)
for p in plan:
    a = int(round(p["start_frame"]/FPS*sr)); m[a:min(N,a+int(p["dur"]*sr))] = True
def rms(x): return float(np.sqrt((x**2).mean())) + 1e-12
# bed to a fixed level - constant for the whole film, no ducking anywhere
bed *= 0.075/rms(bed)
# voice to the reference's measured ratio above the bed, during speech
want = rms(bed[m]) * (10**(TARGET_DB/20))
vo *= want/rms(vo[m])
mix = bed + vo
pk = np.abs(mix).max()
if pk > 0.97: mix *= 0.97/pk
sf.write(".analysis/mixed2.wav", mix, sr)
# verify what we actually built
bs, bq = rms(bed[m]), rms(bed[~m])
print(f"bed during speech   {20*np.log10(bs):7.2f} dBFS")
print(f"bed during silence  {20*np.log10(bq):7.2f} dBFS")
print(f"bed variation       {20*np.log10(bs/bq):+7.2f} dB   (reference: +1.40, ours is one constant gain)")
print(f"voice above bed     {20*np.log10(rms(vo[m])/bs):+7.2f} dB   (reference: {TARGET_DB:+.2f})")
print(f"peak                {20*np.log10(pk):7.2f} dBFS")
