from faster_whisper import WhisperModel
import json, os
os.environ.setdefault("HF_HOME", "D:/hf-cache")
m = WhisperModel("small.en", device="cpu", compute_type="int8", download_root="D:/hf-cache")
segs, info = m.transcribe(".analysis/stems/htdemucs/ref-audio/vocals.wav",
                          word_timestamps=True, vad_filter=False, beam_size=5)
out = []
for s in segs:
    out.append({"start": round(s.start,3), "end": round(s.end,3), "text": s.text.strip(),
                "words": [{"w": w.word.strip(), "s": round(w.start,3), "e": round(w.end,3)} for w in s.words]})
    print(f"[{s.start:6.2f} -> {s.end:6.2f}]  f{int(s.start*30):3d}-{int(s.end*30):3d}  {s.text.strip()}")
json.dump(out, open(".analysis/ref-vo.json","w"), indent=1)
print("\n--- words with frames ---")
for s in out:
    for w in s["words"]:
        print(f"f{int(w['s']*30):3d}  {w['w']}")
