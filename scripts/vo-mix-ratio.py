import numpy as np, soundfile as sf, json
bed, sr = sf.read(".analysis/stems/htdemucs/ref-audio/no_vocals.wav")
voc, _  = sf.read(".analysis/stems/htdemucs/ref-audio/vocals.wav")
if bed.ndim>1: bed = bed.mean(1)
if voc.ndim>1: voc = voc.mean(1)
n = min(len(bed), len(voc)); bed, voc = bed[:n], voc[:n]
vo = json.load(open(".analysis/ref-vo.json"))
speech = np.zeros(n, bool)
for s in vo: speech[int(s["start"]*sr):min(n,int(s["end"]*sr))] = True
def rms(x): return float(np.sqrt((x**2).mean())) if len(x) else 0.0
bs, bq = rms(bed[speech]), rms(bed[~speech])
print("=== did the ORIGINAL mix duck its bed under the voice? ===")
print(f"bed during speech   {20*np.log10(bs+1e-12):7.2f} dBFS")
print(f"bed during silence  {20*np.log10(bq+1e-12):7.2f} dBFS")
print(f"difference          {20*np.log10(bs/bq):+7.2f} dB")
print("  -> " + ("no ducking: the bed holds a constant level" if abs(20*np.log10(bs/bq))<2.0
        else "the original DID duck"))
vs = rms(voc[speech])
print(f"\n=== the original mix balance ===")
print(f"voice during speech {20*np.log10(vs+1e-12):7.2f} dBFS")
print(f"bed during speech   {20*np.log10(bs+1e-12):7.2f} dBFS")
print(f"voice sits {20*np.log10(vs/bs):+.2f} dB above the bed  <- the ratio to reproduce")
json.dump({"voice_over_bed_db": float(20*np.log10(vs/bs))}, open(".analysis/mixratio.json","w"))
