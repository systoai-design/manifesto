"""
Grade an ORIGINAL film against its own standards.

The motion-replicate skill's grade.mjs scores a replica against a reference by
pixel similarity, as a percentage of that reference's re-encode ceiling. This
film has no reference, so that number does not exist for it. What CAN be graded
is whether the film obeys the rules it was built to obey -- and those have all
been measured by hand at some point this session, which is exactly the argument
for making them a harness instead.

Every check is pass/fail against a stated threshold, reported per-check and as
one overall percentage. A check that cannot fail is not a check, so each one
below is written to actually catch the specific defect that produced it.

  usage: python scripts/grade-film.py out/systo-35s-360p.mp4
"""

import io
import json
import re
import subprocess
import sys

import numpy as np

W, H = 640, 360
SR = 24000


def sh(args: list[str]) -> str:
    return subprocess.run(args, capture_output=True, text=True).stderr


def frames(path: str, every: int = 3) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vf",
         f"select=not(mod(n\\,{every})),scale={W}:{H},format=gray",
         "-vsync", "0", "-f", "rawvideo", "-"],
        capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W).astype(np.float32)


def rgb_frames(path: str, every: int = 3) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vf",
         f"select=not(mod(n\\,{every})),scale={W}:{H}",
         "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W, 3).astype(np.float32)


def audio(path: str) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def rel_lum(c: np.ndarray) -> np.ndarray:
    s = c / 255.0
    lin = np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)
    return lin @ np.array([0.2126, 0.7152, 0.0722])


class Grade:
    def __init__(self):
        self.rows = []

    def check(self, group: str, name: str, value, target: str, ok: bool, detail: str = ""):
        self.rows.append((group, name, value, target, ok, detail))

    def report(self) -> int:
        print(f"\n{'':2}{'check':38s} {'measured':>14s}  {'target':<18s} {'':4}")
        print("  " + "-" * 78)
        last = None
        for g, n, v, t, ok, d in self.rows:
            if g != last:
                print(f"  {g}")
                last = g
            mark = "PASS" if ok else "FAIL"
            vs = f"{v:.2f}" if isinstance(v, float) else str(v)
            print(f"    {n:36s} {vs:>14s}  {t:<18s} {mark}")
            if d and not ok:
                print(f"      -> {d}")
        passed = sum(1 for r in self.rows if r[4])
        pct = passed / len(self.rows) * 100
        letter = "A" if pct == 100 else "B" if pct >= 90 else "C" if pct >= 80 else "D"
        print("  " + "-" * 78)
        print(f"  {passed}/{len(self.rows)} checks pass -> {pct:.1f}%   grade {letter}\n")
        return 0 if passed == len(self.rows) else 1


def main() -> int:
    vid = sys.argv[1] if len(sys.argv) > 1 else "out/systo-35s-360p.mp4"
    beats = json.load(io.open("scripts/vo-timing.json", encoding="utf-8"))
    film = json.load(io.open("scripts/film.json", encoding="utf-8"))
    g = Grade()

    # ---------------------------------------------------------------- frames
    gr = frames(vid)
    rgb = rgb_frames(vid)
    n = len(gr)

    dup = sh(["ffmpeg", "-v", "error", "-i", vid, "-vf",
              "mpdecimate=hi=1:lo=1:frac=1,metadata=print", "-f", "null", "-"]).count("pts")
    g.check("FRAME", "duplicate consecutive frames", dup, "0", dup == 0,
            "a hold rendered as bit-identical frames reads as a stall")

    ground = np.median(gr.reshape(n, -1), axis=1)
    mask = np.abs(gr - ground[:, None, None]) > 28
    occ = mask.reshape(n, -1).mean(axis=1) * 100

    # ----------------------------------------------------------- legibility
    # Title-safe: nothing within 4% of any edge. Catches the oversized-type
    # overflow that "a Business" hit when its beat was cut short.
    #
    # Three gestures cross the frame edge ON PURPOSE and are excluded by name,
    # not by loosening the threshold: the ground flips (a disc of the incoming
    # colour opening across the whole frame), the Through treatment (which
    # scales its line to 7x so it passes the camera), and the "a" that S1Split
    # strikes out of frame. Everything else in the margin is an overflow.
    ts_beats = io.open("src/verbs/beats.ts", encoding="utf-8").read()
    exempt = []
    for f in film["flips"]:
        exempt.append((f - 0.10, f + 0.45))
    for m in re.finditer(r'at: ([\d.]+), dur: ([\d.]+), fx: "(through|s1-split)"', ts_beats):
        a, d = float(m.group(1)), float(m.group(2))
        exempt.append((a, a + d + 0.2))

    def exempted(sec):
        return any(a <= sec <= b for a, b in exempt)

    mx, my = int(W * 0.04), int(H * 0.04)
    edge = mask.copy()
    edge[:, my:-my, mx:-mx] = False
    breach = [i for i in range(n)
              if edge[i].sum() > 40 and not exempted(i * 3 / 60)]
    bad_edge = len(breach)
    g.check("LEGIBILITY", "frames with ink in the safe margin", bad_edge, "0", bad_edge == 0,
            "type is running off frame")

    # Contrast of type against its own ground, WCAG ratio.
    # Sampled on the type CORE (delta > 70), not on everything above the
    # detection threshold. The looser mask picks up antialiasing and the blur
    # halo of a word mid-gesture, which reported 1.31:1 for type that is
    # perfectly legible once it settles.
    # Measured only while a beat is SETTLED -- after its entrance, before its
    # dissolve. Type mid-fade is deliberately blending into the ground and its
    # contrast is meaningless: "People do." measured 2.24:1 four frames into
    # its exit and 15:1 while it was on screen to be read. The question this
    # check asks is whether type is legible when someone is reading it.
    settled = []
    for m in re.finditer(r'at: ([\d.]+), dur: ([\d.]+), fx: "[a-z0-9-]+", chunks: \[([^\]]*)\]', ts_beats):
        if not m.group(3).strip():
            continue
        a, d = float(m.group(1)), float(m.group(2))
        settled.append((a + 0.35, a + d * 0.62))

    def is_settled(sec):
        return any(x <= sec <= y for x, y in settled)

    core = np.abs(gr - ground[:, None, None]) > 70
    worst, worst_t = 99.0, 0.0
    for i in range(n):
        if core[i].mean() * 100 < 0.4 or not is_settled(i * 3 / 60):
            continue
        m = core[i]
        fg = rel_lum(rgb[i][m].mean(axis=0))
        bg = rel_lum(rgb[i][~m].mean(axis=0))
        hi, lo = max(fg, bg), min(fg, bg)
        ratio = (hi + 0.05) / (lo + 0.05)
        if ratio < worst:
            worst, worst_t = ratio, i * 3 / 60
    # 3:1 is WCAG AA for LARGE text, and every size in this film (52-132px) is
    # far past the large-text boundary. 4.5:1 is the body-copy figure and does
    # not apply to display type.
    #
    # The binding case is Flare #FF532E on Paper #FFF4E8, which is a hue
    # contrast rather than a luminance one and computes to 2.95:1 by
    # construction -- so the emphasis line sits essentially ON the floor. It
    # passes, but there is no margin in it, and that is a brand-palette fact
    # worth knowing rather than a defect in the film.
    g.check("LEGIBILITY", "worst type/ground contrast", worst, ">= 3.00:1 (large)",
            worst >= 3.0,
            f"at {worst_t:.1f}s")
    if 3.0 <= worst < 3.5:
        print(f"  note: worst contrast {worst:.2f}:1 clears the large-text floor by "
              f"{worst - 3.0:.2f} — Flare on Paper has no headroom.")

    # ---------------------------------------------------------- composition
    cx, cy = [], []
    for i in range(n):
        if mask[i].sum() < 200:
            continue
        ys, xs = np.nonzero(mask[i])
        cx.append(xs.mean() / W); cy.append(ys.mean() / H)
    cx, cy = np.array(cx), np.array(cy)
    midv = ((cy > 0.40) & (cy < 0.60)).mean() * 100
    g.check("COMPOSITION", "vertical positional spread (sd)", float(cy.std()), ">= 0.090",
            cy.std() >= 0.090, "everything sits at the same height")
    g.check("COMPOSITION", "frames in the middle third (vert)", float(midv), "<= 85%",
            midv <= 85, "centre is the only place anything is")

    # ---------------------------------------------------- type hierarchy
    ts = io.open("src/verbs/beats.ts", encoding="utf-8").read()
    sizes = sorted({int(x) for x in re.findall(r"sizes: \[(\d+)", ts)})
    g.check("TYPE", "distinct sizes in the timeline", len(sizes), ">= 3",
            len(sizes) >= 3, f"found {sizes}")

    # ------------------------------------------------------------- continuity
    # No beat that carries words may render an empty frame in its middle -- that
    # is the signature of a treatment whose internal timeline outran its beat.
    # Only beats that put WORDS on screen. The blackout, the close hop and the
    # close morph carry chunks: [] -- the animation is the line there, and an
    # empty type layer is the correct result, not a hole.
    worded = set()
    for m in re.finditer(r'at: ([\d.]+), dur: [\d.]+, fx: "[a-z0-9-]+", chunks: \[([^\]]*)\]', ts_beats):
        if m.group(2).strip():
            worded.add(round(float(m.group(1)), 2))

    holes = []
    for b in beats["lines"]:
        if round(b["at"], 2) not in worded:
            continue
        a, e = b["at"], b["end"]
        mid = [occ[i] for i in range(n) if a + 0.15 < i * 3 / 60 < e - 0.05]
        if mid and max(mid) < 0.30:
            holes.append(f'{b["i"]} "{b["text"][:28]}"')
    g.check("CONTINUITY", "spoken beats with an empty frame", len(holes), "0",
            not holes, "; ".join(holes[:3]))

    # ------------------------------------------------------------------ motion
    #
    # The film's FIRST stated law (treatments.tsx) is one easing curve and NO
    # overshoot, and until now nothing enforced it -- the Pragma squash that
    # popped the body 22px on the frame it settled was found by reading code,
    # not by measuring the render.
    #
    # Measured as: within a beat's settled window, take the content's bounding
    # box area, remove a LINEAR trend (the idle push is a deliberate 1.4% ramp
    # and must not be flagged), and look at what is left. A monotonic drift
    # leaves nothing; an element that passes its rest value and comes back
    # leaves a bump.
    # Ink COUNT, not bounding box. A bbox is a min/max extremum: at 360p a
    # single row of antialiasing crossing the mask threshold flips the height
    # from 25px to 26px and swings the area 4%, which reads as an oscillation
    # in type that is provably still. Ink count is an integral over the whole
    # frame, so the same antialiasing moves it by a fraction of a percent.
    def ink_count(i):
        c = int(mask[i].sum())
        return float(c) if c >= 200 else None

    # Overshoot is a DIRECTION REVERSAL -- a value that reaches its rest and
    # comes back past it. It is not "the area changes", which was the first
    # attempt and which flagged the Hammer at 61%: that treatment stamps its
    # word three times inside one beat, and every stamp settles monotonically
    # from above. Big movement is not overshoot. Turning around is.
    #
    # A stamp re-trigger appears as a large positive jump and starts a new
    # segment rather than counting as a reversal. Within a segment, any
    # significant change of sign fails.
    worst_os, worst_os_t = 0, 0.0
    for a_s, b_s in settled:
        vals = [(i, ink_count(i)) for i in range(n) if a_s <= i * 3 / 60 <= b_s]
        vals = [(i, v) for i, v in vals if v]
        if len(vals) < 8:
            continue
        raw = np.array([v for _, v in vals], dtype=float)

        # Segment on the RAW series. A treatment that re-triggers -- the Hammer
        # stamps its word three times inside one beat -- shows a sharp jump up,
        # and each stamp is its own settle. Smoothing first would spread that
        # jump across three samples and hide it, turning a re-trigger into a
        # false rebound.
        bounds = [0] + [k for k in range(1, len(raw)) if raw[k] > raw[k - 1] * 1.15] + [len(raw)]

        for s0, s1 in zip(bounds, bounds[1:]):
            seg = raw[s0:s1]
            if len(seg) < 6:
                continue
            # Smooth WITHIN the segment: grain is uncorrelated frame to frame,
            # a settle is not.
            sm = np.convolve(seg, np.ones(3) / 3, mode="valid")
            d = np.diff(sm)
            sig = d[np.abs(d) > sm.mean() * 0.020]
            if len(sig) < 2:
                continue
            flips = int((np.diff(np.sign(sig)) != 0).sum())
            if flips > worst_os:
                worst_os, worst_os_t = flips, vals[s0][0] * 3 / 60
    g.check("MOTION", "settle direction reversals", worst_os, "0", worst_os == 0,
            f"from {worst_os_t:.1f}s — an element passes rest and comes back")

    # Pacing. A run of identical beat lengths reads as a metronome; the graded
    # reference's cards vary by a factor of four. Measured on the spoken beats
    # only, since the wordless ones are structural.
    durs = [float(m.group(2)) for m in
            re.finditer(r'at: ([\d.]+), dur: ([\d.]+), fx: "[a-z0-9-]+", chunks: \[([^\]]+)\]', ts_beats)]
    cv = float(np.std(durs) / np.mean(durs)) if durs else 0.0
    g.check("MOTION", "beat-length variation (cv)", cv, ">= 0.18", cv >= 0.18,
            "every beat is the same length — the cut reads as a metronome")

    # ------------------------------------------------------------------ audio
    eb = sh(["ffmpeg", "-v", "info", "-i", vid, "-af", "ebur128=peak=true", "-f", "null", "-"])
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", eb)[-1])
    vd = sh(["ffmpeg", "-v", "info", "-i", vid, "-af", "volumedetect", "-f", "null", "-"])
    peak = float(re.findall(r"max_volume:\s+(-?[\d.]+)", vd)[-1])
    g.check("AUDIO", "integrated loudness", lufs, "-17.0 .. -15.0", -17.0 <= lufs <= -15.0)
    g.check("AUDIO", "peak", peak, "<= -1.0 dBFS", peak <= -1.0, "clipping risk")

    vo, mu = audio("public/vo.wav"), audio("public/music.wav")
    ln = min(len(vo), len(mu)); vo, mu = vo[:ln], mu[:ln]
    h = int(0.02 * SR)
    env = lambda x: np.sqrt(np.array(
        [x[i:i + h].astype(np.float64) ** 2 for i in range(0, ln - h, h)]).mean(axis=1) + 1e-12)
    ev, em = env(vo), env(mu)
    db = lambda a: 20 * np.log10(a + 1e-12)
    t = np.arange(len(ev)) * 0.02
    voiced = ev > ev.max() * 0.02
    playing = (db(em) > -55) & (t > 2.5) & (t < film["total"] - 4.0)
    duck = db(em[~voiced & playing]).mean() - db(em[voiced & playing]).mean()
    g.check("AUDIO", "sidechain duck depth", float(duck), "<= 6.0 dB", duck <= 6.0,
            "the bed audibly pumps under the read")
    sep = db(ev[voiced]).mean() - db(em[voiced & playing]).mean()
    g.check("AUDIO", "music below voice", float(sep), "6.0 .. 14.0 dB", 6.0 <= sep <= 14.0)

    # Per-line read consistency -- the complaint that produced per-line generation.
    lv = []
    for b in beats["lines"]:
        seg = vo[int(b["at"] * SR):int(b["end"] * SR)]
        if len(seg):
            lv.append(db(np.sqrt((seg.astype(np.float64) ** 2).mean())))
    spread = max(lv) - min(lv)
    g.check("AUDIO", "per-line read level spread", float(spread), "<= 3.0 dB", spread <= 3.0,
            "some lines are audibly quieter than others")

    # The blackout has to be genuinely silent, not just quiet.
    bo = film["blackout"] + 1.2
    seg = mu[int(bo * SR):int((bo + 0.5) * SR)]
    bl = float(db(np.sqrt((seg.astype(np.float64) ** 2).mean()))) if len(seg) else 0.0
    g.check("AUDIO", "music floor inside the blackout", bl, "<= -60 dB", bl <= -60.0)

    # --------------------------------------------------------------- sync
    late = []
    for b in beats["lines"]:
        if round(b["at"], 2) not in worded:
            continue
        i = int(b["at"] * 60 / 3)
        if i < n and occ[min(i + 6, n - 1)] < 0.20:
            late.append(f'{b["i"]} "{b["text"][:24]}"')
    g.check("SYNC", "lines with nothing on screen", len(late), "0", not late,
            "; ".join(late[:3]))

    return g.report()


if __name__ == "__main__":
    sys.exit(main())
