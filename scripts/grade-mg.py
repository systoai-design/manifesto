#!/usr/bin/env python3
"""
grade-mg.py -- grade an original motion graphic against the corrected canon.

SPECIFICATION: references/canon.md section 7,
the twenty-four-criterion table, its four gates and its weights. Observed
professional practice in _research/playlist-lessons.md outranks any rubric
written from award criteria; _research/corrections.md carries the claims
already downgraded once under adversarial review; the superseded
_research/grading-rubric.md is used only for measurement machinery canon does
not restate (the two channels, the shared definitions of move, onset, settle
and progress curve, and the manifest shape).

grade.mjs scores a replica against its reference by pixel similarity. An
original film has no reference, so that number does not exist for it. This
grades any motion graphic against canon's twenty-four criteria with S / A / B
/ C bands, a weighted total and four gates.

  usage: python grade-mg.py <render.mp4> --composition <dir> \
                            [--manifest grade.json] [--target A]

Exits non-zero when the overall band is below --target, so a bad render cannot
ship quietly.

WHAT THIS FILE IS NOW. It owns the two channels, the cut and beat model, the
shared move model, the aggregate and the report. It owns no criterion. The
twenty-four criteria live in four sibling modules, each of which carries its
own constants block at its own top, because a threshold belongs beside the
measurement it thresholds:

  crit_motion.py       C1  C2  C6  C10 C11 C21
  crit_composition.py  C3  C7  C8  C9  C22 C24
  crit_legibility.py   C12 C13 C14 C15 C16 C20
  crit_structure.py    C4  C5  C17 C18 C18D C19 C23 C23D

Each module exposes functions of one shared context object and returns rows of
one shape: id, name, band, weight, gate, na, measured, worstFrames, basis,
note, declarations. This file builds that context once, normalises weight and
gate against canon (a module's own table is a cross-check, never the
authority), aggregates, and prints.

BANDS AND THE AGGREGATE, canon section 7 verbatim:

  points   S 100  A 85  B 65  C 30
  W        sum(points * weight) / sum(weight) over APPLICABLE criteria
  S        every applicable criterion at S or N/A
  A        W >= 90 and no C
  B        W >= 75 and at most two Cs, none of them gates
  C        anything else, or any gate at C

  weights  2: C1 C3 C17 C19.  0: C13 C20 C18D C23D (the gates).  1: the rest.

The gates carry weight 0 so one legibility problem does not also destroy the
craft score, and a C on a gate caps the overall at C on its own. Dead frames
and safe margins are NOT gates: the first gates out animation on twos,
deliberate freezes and end cards, and the cheapest way to pass it was per-frame
grain; the second gates out every web-only deliverable and every deliberately
cropped full-bleed treatment.

THE DECLARATION BUDGET. Every hard criterion has an escape hatch and the author
writes the manifest, so the report prints the number of declarations and the
number of criteria whose band improved because of one. The second number is
measured, not asserted: every criterion is re-run with the relief-granting keys
removed and the two band tables are compared. Keys that DESCRIBE the piece
(register, genre, delivery, cuts, palette, typeScale) are not relief and are
not stripped -- declaring broadcast delivery makes C14 stricter, and declaring
a palette is what makes C16 gradeable at all.

Cautions carried from the manifesto skill, each of which cost an hour once:
  - decoding a RANGE gives (n, H, W, 3); reduce over axis 3, never axis 2
  - clip windows are [start, start + duration); bias both ends inward
  - smooth an ink count before looking for reversals, grain manufactures them
  - never measure motion on a bounding box, use the ink COUNT integral
  - exempt by NAME through the manifest, never by loosening a threshold
  - worstFrames is ranked by SEVERITY, never by frame number: the frame the
    note names has to be the first frame the reader opens
"""

import argparse
import copy
import io
import json
import math
import os
import re
import subprocess
import sys

import numpy as np

# =============================================================================
# CONSTANTS.  Every threshold and band boundary in the rubric lives here and
# nowhere else, because all of them will be re-tuned.  Names are C<criterion>_*.
# =============================================================================

# ---- decode and shared measurement ----------------------------------------
DEC_W, DEC_H = 640, 360          # rubric 4.1 pixel channel working size
INK_DELTA = 28                   # |luma - ground| for the ink mask
CORE_DELTA = 70                  # |luma - ground| for the type core mask
COMPONENT_MIN_PX = 40            # components smaller than this are noise at 640 wide
TRACK_AREA_LO, TRACK_AREA_HI = 0.5, 2.0   # a component that doubles is a different one
AUDIO_SR = 22050

ONSET_PROGRESS = 0.02            # s(t) >= this is the onset
SETTLE_EPS = 0.005               # |s - 1| < this, and stays there, is the settle
MOVE_MIN_FRAMES = 2              # a move is a spatial tween of at least this long
FRAME_SNAP_TOL = 0.05            # frames. Windows bias INWARD, but a composition writes
                                 # data-start to five decimals, so 0.16667 s at 30 fps is
                                 # 5.0001 frames and a bare ceil puts the tween a whole
                                 # frame late. The tolerance absorbs the authored rounding
                                 # and still biases a genuinely mid-frame boundary inward.
SHAPE_MIN_FRAMES = 4             # below this a tween carries fewer than two intermediate
                                 # samples and cannot express an ease at all: a 33 ms
                                 # slam at 60 fps is unclassifiable, not linear
SPATIAL_PROPS = {"x", "y", "xPercent", "yPercent", "scale", "scaleX", "scaleY",
                 "rotation", "rotationX", "rotationY", "rotationZ", "clipPath",
                 "translateX", "translateY", "top", "left", "width", "height"}
TRANSLATE_PROPS = {"x", "y", "xPercent", "yPercent", "translateX", "translateY"}
PAINT_PROPS = {"opacity", "autoAlpha", "filter", "color", "backgroundColor",
               "backgroundPosition", "boxShadow", "borderColor", "fill", "stroke"}
DEFAULT_REGISTER = "corporate"   # rubric 4.2, the middle of the LottieFiles tables
DEFAULT_GENRE = "mixed"          # rubric C4; declare the genre to get the right fences
REGISTERS = ("premium", "corporate", "playful", "energetic")
GENRES = ("continuous-camera", "mixed", "card-based")
DELIVERIES = ("broadcast", "web", "social")

# Ambient, defined ONCE (rubric 4.2): duration >= 2 s AND travel < 5% of frame.
# Three criteria used to define it three different ways, so the same tween was
# ambient for one and primary for another and the aggregate was not reproducible.
# The old 2%-of-frame-height amplitude test sat exactly on the boundary of the
# commonest correct case, a scale 1 -> 1.04 Ken Burns.
AMBIENT_MIN_S = 2.0
AMBIENT_MAX_TRAVEL = 0.05        # of frame height, and of scale

# ---- cut detection (the blank-run model, SKILL.md 3.2) --------------------
CUT_BLANK_INK = 0.002            # ink fraction below this is a blank frame
CUT_GROUND_FLIP = 20.0           # luma step in the frame's median = ground flip
CUT_COLPROFILE_L1 = 1.20         # normalised column-profile L1 distance = content swap
CUT_MIN_SEPARATION = 6           # frames at 30 fps; closer boundaries are one cut

# ---- constants the SHARED machinery uses ----------------------------------
# Every band boundary and every criterion threshold now lives at the top of the
# module that owns the criterion. What is left here is the constants the two
# channels themselves need: the curve classifier the Source and the PixelSource
# both run, the duplicate and flash statistics the Pixel reports, the onset
# picker in the Audio, and the strobe scan C11 and C19 share. They keep their
# C<criterion>_* names because the criterion that consumes the measurement is
# the only thing that says what the number is for.
C1_LINEAR_TOL = 0.05             # |s(q) - q| under this at all three quarters
C1_OUT_MID, C1_OUT_Q1 = 0.60, 0.35
C1_IN_MID = 0.40
C1_INOUT_MID_TOL, C1_INOUT_Q1, C1_INOUT_Q3 = 0.10, 0.20, 0.80
C1_OVERSHOOT_PEAK = 1.005
C1_OVERSHOOT_FLOOR = 0.005       # steps under 0.5% of travel are grain, not a reversal
C1_MIN_MEASURED_TRAVEL_PX = 0.75 # below this the rect track is quantisation, not travel
C1_EXIT_AT_CUT_FRAMES = 2        # a move still running when its clip ends is an exit: the
                                 # cut takes the element away, whatever its opacity does
C1_COMPOUND_PEAK = 1.50          # a measured curve peaking past this is the sum of two
C1_COMPOUND_DIP = 0.15           # motions, not one move; elastic peaks near 1.30 and
                                 # back.in dips to about -0.10, so both stay measurable
C2_FIT_CLUSTER_RADIUS = 0.04     # tighter on the pixel channel, where curves are fitted
C6_SMOOTH = 3                    # box smoothing width before looking for sign changes
C15_READABLE_PROGRESS = 0.80     # a word 80% arrived is legible; the reading window
                                 # opens there, not at the settle
PIXEL_MOVE_MIN_FRAMES = 4        # a fitted curve needs frames to have a shape
PIXEL_MOVE_MIN_TRAVEL = 4.0      # px at 640 wide; below this it is centroid grain
PIXEL_SEG_AREA_LO, PIXEL_SEG_AREA_HI = 0.7, 1.4   # one element, not a merge
C5_DUP_CODE_VALUE = 2            # a pixel moving by more than this really moved
C5_DUP_MEAN_LEVELS = 0.10        # mean absolute luma difference over the frame
C5_DUP_CHANGED_FRAC = 0.005      # share of pixels over C5_DUP_CODE_VALUE
C10_GRID_TOL_FRAMES = 2          # a cut within this of a bar line is on the grid
C18_ONSET_QUARTILE = 0.75        # keep the strongest quartile of flux peaks as hits
C11_STROBE_FRAC = 0.005          # 0.5% of FRAME WIDTH per frame: 10 px at 1920,
                                 # 5 px at 960, 20 px at 3840
C11_STROBE_FPS_REF = 30.0        # "halve at 24 fps, roughly double at 60": the
                                 # tolerated per-frame jump scales WITH the rate
C11_STROBE_MIN_AREA = 200        # a component too small to carry a hard edge
C11_STROBE_MAX_COMPS = 8         # the largest regions in a frame; below them is
                                 # dust no viewer reads as an edge
C11_STROBE_MATCH_SHARE = 0.25    # a box covering this much of the smaller of a
                                 # pair is the same region between two frames.
                                 # More than one such partner on either side is
                                 # a merge or a split, and in both the box jumps
                                 # to a union without anything moving
C11_STROBE_MOVING_PX = 0.5       # at 640 wide; below this the region is still
C11_STROBE_TRANSIT_FILL = 0.45   # a moving region whose box covers this much of
                                 # the frame is a full-frame wipe, an infinite
                                 # zoom or a card flying through, and canon 5
                                 # exempts all three BY CLASS: "whip pans,
                                 # full-frame wipes, cards flying through frame
                                 # and infinite zooms cross the whole frame in a
                                 # straight line at one acceleration, and
                                 # should". Its edge travels fast by design and
                                 # neither the strobe test nor the blur-coverage
                                 # test is about it.
C20_LUM_STEP = 0.10              # WCAG general flash threshold
C20_DARK_MAX = 0.80              # ... where the darker of the pair is below this
C20_AREA_SHARE = 0.25            # over a significant portion of the central field
C20_CENTRE_FRAC = 0.50           # the central 10 degrees, as half width and height
C20_FLASH_W, C20_FLASH_H = 320, 180



C24_JUMP_DIAGONAL = 0.50         # a cut moving the point of interest this far jumps

# ---- section 6 aggregation -------------------------------------------------
BAND_POINTS = {"S": 100, "A": 85, "B": 65, "C": 30}
BAND_ORDER = ["S", "A", "B", "C"]
# Rubric 6: weight 2 is exactly {C1, C3, C17, C19}; the gates carry weight 0 in
# W, because a gate already caps the overall grade at C, so weighting it as well
# double-penalises the same defect and destroys W as a craft signal.
WEIGHT_2 = {"C1", "C3", "C17", "C19"}
GATES = {"C13", "C20", "C18D", "C23D"}
OVERALL_HEAVY_WEIGHT = 2         # canon section 7's own weight-2 set. All four
                                 # have to be measurable for the aggregate to
                                 # mean anything; see Grade.aggregate.
OVERALL_A_W = 90.0
OVERALL_B_W = 75.0
OVERALL_B_MAX_C = 2
OVERALL_MIN_GRADED = 10          # of the twenty-six rows. Below this the
                                 # weighted score is WITHHELD rather than
                                 # printed, and the piece is unrated.
                                 # W is a mean over applicable criteria, so a
                                 # file with almost nothing in it is scored on
                                 # almost nothing: a two-second static colour
                                 # bars card with a six-key manifest scored
                                 # 66.7 over 4 of 26 rows with no gate failed,
                                 # and thereby outranked a 26 s ad measured on
                                 # twenty. Printing the denominator beside the
                                 # number is a caveat next to a headline, not a
                                 # correction to it. Damping the score toward
                                 # the bottom of its band by the graded
                                 # fraction was the alternative and is worse:
                                 # it produces a number that looks comparable
                                 # and is not. A score over four rows is not a
                                 # score.

# Rubric 4.3: every hard criterion has a declaration escape and the author of
# the piece writes the manifest, so the report prints how many declarations
# there are and how many criteria improved because of one.
# Keys that DESCRIBE the piece. They are declarations and are counted as such,
# but they cannot buy a pass and are not stripped for the budget re-run:
# declaring broadcast delivery makes C14 stricter rather than looser, declaring
# a palette is what makes C16 gradeable at all, declaring the cut list is what
# the beat model is built from, and stripping it would grade a different edit.
DESCRIPTIVE_KEYS = [
    "cuts", "register", "genre", "delivery", "palette", "typeScale",
    "socialSafe", "footageRegions", "durationFrames", "duration",
]
# Keys that grant RELIEF. The declaration budget re-runs every criterion with
# exactly these removed and counts the criteria whose band got better because
# one was present. A key is on this list if any criterion reads it and can
# score better for it, whatever else it also does.
EXEMPTION_KEYS = [
    "silent", "holds", "freezes", "cadence", "posterize", "gapCadence",
    "handoffs", "fullBleed", "croppedType", "decorativeType", "mechanical",
    "mechanicalPiece", "organic", "loops", "impact", "hero", "secondaryPairs",
    "onBeatHardCuts", "shutterFrames", "echoTrails", "revealDevices",
    "triggerGroups", "lockups", "themeChanges", "loudnessTarget",
    "truePeakMax", "posterFrame", "looping", "endCard",
]
DECLARATION_KEYS = DESCRIPTIVE_KEYS + EXEMPTION_KEYS
DECLARATION_FLAG_IMPROVED = 3    # canon 7: "Flag any pass that depends on more
                                 # than a few" declarations


# =============================================================================
# small helpers



def sh_err(args):
    return subprocess.run(args, capture_output=True, text=True,
                          errors="replace").stderr


def sh_out(args):
    return subprocess.run(args, capture_output=True).stdout


def band_better(a, b):
    """True when band a is strictly better than band b. None is 'not graded'."""
    if a is None or b is None:
        return False
    return BAND_ORDER.index(a) < BAND_ORDER.index(b)


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def fscale(frames_at_30, fps):
    """Every frame-count threshold in the rubric is quoted at the authoring fps,
    which the rubric fixes at 30 ("frame numbers are integers at the authoring
    fps"). A 60 fps render doubles every run length, so an 8-frame blank gap
    becomes 16 and every one of them reads as a stall unless the constants
    scale with the delivered rate."""
    return max(1, int(round(frames_at_30 * fps / 30.0)))


def smooth_box(a, w):
    """Box smoothing that keeps the ARRAY LENGTH, so an index into the smoothed
    series still means the same frame. mode="valid" shifted every index by one
    and the settle-entry scan silently read the wrong frame."""
    a = np.asarray(a, dtype=float)
    if w <= 1 or len(a) < w:
        return a
    lo = w // 2
    ap = np.pad(a, (lo, w - 1 - lo), mode="edge")
    return np.convolve(ap, np.ones(w) / w, mode="valid")


def rel_lum_rgb(c):
    s = np.asarray(c, dtype=float) / 255.0
    lin = np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)
    return float(lin @ np.array([0.2126, 0.7152, 0.0722]))


# =============================================================================
# connected components, without a scipy dependency
# =============================================================================

def components(mask, min_px=COMPONENT_MIN_PX):
    """Row-run union-find labelling. Returns [(area, cx, cy, x0, y0, x1, y1)].

    Ink is a percent or two of the frame, so the run list is short and this is
    much faster than any pixel-wise pass would be.
    """
    h = mask.shape[0]
    parent = []

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    prev_runs = []
    runs = []          # (row, x0, x1_exclusive, label)
    for y in range(h):
        row = mask[y]
        if not row.any():
            prev_runs = []
            continue
        idx = np.flatnonzero(np.diff(np.concatenate(([0], row.view(np.int8), [0]))))
        cur = []
        for i in range(0, len(idx), 2):
            x0, x1 = int(idx[i]), int(idx[i + 1])
            lbl = len(parent)
            parent.append(lbl)
            for (px0, px1, plbl) in prev_runs:
                if x0 < px1 and px0 < x1:      # 8-connectivity along the row overlap
                    union(lbl, plbl)
            cur.append((x0, x1, lbl))
            runs.append((y, x0, x1, lbl))
        prev_runs = cur

    if not runs:
        return []
    agg = {}
    for (y, x0, x1, lbl) in runs:
        r = find(lbl)
        n = x1 - x0
        sx = (x0 + x1 - 1) * n / 2.0
        a = agg.get(r)
        if a is None:
            agg[r] = [n, sx, y * n, x0, y, x1 - 1, y]
        else:
            a[0] += n
            a[1] += sx
            a[2] += y * n
            a[3] = min(a[3], x0)
            a[4] = min(a[4], y)
            a[5] = max(a[5], x1 - 1)
            a[6] = max(a[6], y)
    out = []
    for a in agg.values():
        if a[0] < min_px:
            continue
        out.append((a[0], a[1] / a[0], a[2] / a[0], a[3], a[4], a[5], a[6]))
    out.sort(key=lambda c: -c[0])
    return out


def track_components(per_frame):
    """Nearest-centroid tracking with an area-ratio gate. Returns tracks as
    dicts {frames: [...], cx: [...], cy: [...], area: [...]}. A component that
    doubles in one frame is a different component (rubric 4.1)."""
    tracks = []
    live = {}                                  # track index -> last frame seen
    for f, comps in enumerate(per_frame):
        used = set()
        prev = [(ti, tracks[ti]) for ti, lf in live.items() if lf == f - 1]
        for (area, cx, cy, x0, y0, x1, y1) in comps:
            best, bestd = None, 1e18
            for ti, tr in prev:
                if ti in used:
                    continue
                r = area / max(tr["area"][-1], 1e-6)
                if r < TRACK_AREA_LO or r > TRACK_AREA_HI:
                    continue
                d = (cx - tr["cx"][-1]) ** 2 + (cy - tr["cy"][-1]) ** 2
                if d < bestd:
                    best, bestd = ti, d
            if best is None:
                tracks.append({"frames": [f], "cx": [cx], "cy": [cy], "area": [area],
                               "box": [(x0, y0, x1, y1)]})
                live[len(tracks) - 1] = f
            else:
                tr = tracks[best]
                tr["frames"].append(f)
                tr["cx"].append(cx)
                tr["cy"].append(cy)
                tr["area"].append(area)
                tr["box"].append((x0, y0, x1, y1))
                live[best] = f
                used.add(best)
    return tracks


# =============================================================================
# the pixel channel
# =============================================================================

class Pixel:
    def __init__(self, path, fps, frames, width, height):
        self.path = path
        self.fps = fps
        self.width = float(width)
        self.height = float(height)
        raw = sh_out(["ffmpeg", "-v", "error", "-i", path, "-vf",
                      f"scale={DEC_W}:{DEC_H},format=gray",
                      "-vsync", "0", "-f", "rawvideo", "-"])
        g = np.frombuffer(raw, dtype=np.uint8)
        n = len(g) // (DEC_W * DEC_H)
        if n == 0:
            raise SystemExit(f"grade-mg: decoded zero frames from {path}")
        self.grey = g[: n * DEC_W * DEC_H].reshape(n, DEC_H, DEC_W)
        self.n = n
        gf = self.grey.astype(np.float32)
        self.ground = np.median(gf.reshape(n, -1), axis=1)
        self.mask = np.abs(gf - self.ground[:, None, None]) > INK_DELTA
        self.core = np.abs(gf - self.ground[:, None, None]) > CORE_DELTA
        self.ink = self.mask.reshape(n, -1).sum(axis=1).astype(np.float64)
        self.ink_frac = self.ink / (DEC_W * DEC_H)
        self.col_profile = self.mask.sum(axis=1).astype(np.float32)   # (n, W)
        self.row_profile = self.mask.sum(axis=2).astype(np.float32)   # (n, H)
        # frame-to-frame change, in grey levels, for stillness work
        if n > 1:
            dif = np.abs(np.diff(self.grey.astype(np.int16), axis=0))
            d = dif.reshape(n - 1, -1).mean(axis=1)
            ch = (dif > 1).reshape(n - 1, -1).mean(axis=1)
        else:
            d = ch = np.zeros(0)
        self.frame_delta = np.concatenate(([255.0], d))
        self.changed_frac = np.concatenate(([1.0], ch))
        self.centroid = np.full((n, 2), np.nan)
        ys, xs = np.mgrid[0:DEC_H, 0:DEC_W]
        for i in range(n):
            s = self.ink[i]
            if s < 200:
                continue
            m = self.mask[i]
            self.centroid[i, 0] = xs[m].mean() / DEC_W
            self.centroid[i, 1] = ys[m].mean() / DEC_H
        self._comps = None
        self._tracks = None
        self._rgb_cache = {}
        self._dup = None
        self._flash = None

    @property
    def comps(self):
        if self._comps is None:
            self._comps = [components(self.mask[i]) for i in range(self.n)]
        return self._comps

    @property
    def tracks(self):
        if self._tracks is None:
            self._tracks = track_components(self.comps)
        return self._tracks

    def rgb(self, frame_list):
        """Pull specific frames as RGB at the decode size. Decoding the whole
        film in colour costs a gigabyte for a 26 s piece; the criteria that need
        colour need a few hundred frames."""
        want = sorted({int(f) for f in frame_list if 0 <= int(f) < self.n})
        need = [f for f in want if f not in self._rgb_cache]
        for i in range(0, len(need), 300):
            chunk = need[i:i + 300]
            expr = "+".join(f"eq(n\\,{f})" for f in chunk)
            raw = sh_out(["ffmpeg", "-v", "error", "-i", self.path, "-vf",
                          f"select='{expr}',scale={DEC_W}:{DEC_H}",
                          "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
            arr = np.frombuffer(raw, dtype=np.uint8)
            got = len(arr) // (DEC_W * DEC_H * 3)
            arr = arr[: got * DEC_W * DEC_H * 3].reshape(got, DEC_H, DEC_W, 3)
            for k in range(min(got, len(chunk))):
                self._rgb_cache[chunk[k]] = arr[k]
        return {f: self._rgb_cache[f] for f in want if f in self._rgb_cache}

    def duplicates(self):
        """Frame-to-frame duplicate flags, measured at the render's FULL
        resolution on luma. Rubric C5 b. Decoding full-resolution luma for a
        26 s 1080p film is about 1.6 GB, so the pass is streamed in chunks and
        only the two summary numbers per frame are kept."""
        if self._dup is not None:
            return self._dup
        W, H = int(self.width), int(self.height)
        plane = W * H
        proc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-i", self.path, "-vf", "format=gray",
             "-vsync", "0", "-f", "rawvideo", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        mean_d = np.zeros(self.n, dtype=np.float64)
        chg = np.zeros(self.n, dtype=np.float64)
        mean_d[0], chg[0] = 255.0, 1.0
        prev = None
        i = 0
        while i < self.n:
            buf = proc.stdout.read(plane)
            if not buf or len(buf) < plane:
                break
            cur = np.frombuffer(buf, dtype=np.uint8).reshape(H, W).astype(np.int16)
            if prev is not None:
                d = np.abs(cur - prev)
                mean_d[i] = float(d.mean())
                chg[i] = float((d > C5_DUP_CODE_VALUE).mean())
            prev = cur
            i += 1
        try:
            proc.stdout.close()
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        dup = (mean_d < C5_DUP_MEAN_LEVELS) & (chg < C5_DUP_CHANGED_FRAC)
        dup[0] = False
        self._dup = (dup, mean_d, chg)
        return self._dup

    def flash_transitions(self):
        """(frames, signs) of full-frame luminance transitions over the WCAG
        general flash threshold inside the central field. Cached; C20 is a gate
        and C19 reads the same decode."""
        if self._flash is not None:
            return self._flash
        W, H = C20_FLASH_W, C20_FLASH_H
        raw = sh_out(["ffmpeg", "-v", "error", "-i", self.path, "-vf",
                      f"scale={W}:{H}", "-vsync", "0", "-f", "rawvideo",
                      "-pix_fmt", "rgb24", "-"])
        a = np.frombuffer(raw, dtype=np.uint8)
        n = len(a) // (W * H * 3)
        if n < 2:
            self._flash = ([], [])
            return self._flash
        a = a[: n * W * H * 3].reshape(n, H, W, 3).astype(np.float32) / 255.0
        lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        # a range decodes to (n, H, W, 3): reduce over the LAST axis, never axis 2
        L = lin @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        m = C20_CENTRE_FRAC
        y0, y1 = int(H * (1 - m) / 2), int(H * (1 + m) / 2)
        x0, x1 = int(W * (1 - m) / 2), int(W * (1 + m) / 2)
        Lc = L[:, y0:y1, x0:x1]
        d = np.diff(Lc, axis=0)
        darker = np.minimum(Lc[:-1], Lc[1:])
        hit = (np.abs(d) >= C20_LUM_STEP) & (darker < C20_DARK_MAX)
        frac = hit.reshape(n - 1, -1).mean(axis=1)
        mean_d = d.reshape(n - 1, -1).mean(axis=1)
        frames, signs = [], []
        for i in np.flatnonzero(frac > C20_AREA_SHARE):
            frames.append(int(i) + 1)
            signs.append(1 if mean_d[i] > 0 else -1)
        self._flash = (frames, signs)
        return self._flash


# =============================================================================
# the source channel
# =============================================================================

MECHANICAL_EASES = ("none", "linear")


SETTLE_STILL_PX = 1.0            # px per frame at this frame height, below
SETTLE_STILL_REF_H = 1080.0      # which an element is holding still rather than
SETTLE_STILL_MIN_FRAMES = 2      # moving. Canon 3.1: "Card life: entrance ->
                                 # settle -> hold -> exit -> gap. ONLY THE HOLD
                                 # COUNTS as reading time, and the hold is
                                 # measured from the settle." An element with no
                                 # tween of its own inherits every move from its
                                 # ancestors, so its own tween list says it is
                                 # settled for its whole clip; the delivered box
                                 # says otherwise and is what the viewer sees. A
                                 # window with no still run at all is left alone
                                 # rather than dropped.


def _is_mechanical_tween(mv):
    """Is this particular tween the constant-velocity driver a `mechanical`
    declaration is about. Authored `ease: "none"` (or "linear"), or a move
    already auto-classified ambient, which is canon C1's own second exemption
    and needs no declaration at all."""
    if mv.get("ambient") or mv.get("repeat"):
        return True
    ease = str(mv.get("ease") or "").strip().lower()
    return ease in MECHANICAL_EASES


def _resample101(y):
    y = np.asarray(y, dtype=float)
    if len(y) < 2:
        return None
    return np.interp(np.linspace(0, 1, 101), np.linspace(0, 1, len(y)), y)


class Source:
    """tracks.json plus tweens.json, turned into elements, moves and windows."""

    def __init__(self, tracks, tweens, fps, manifest):
        self.fps = fps
        self.frames = tracks["frames"]
        self.W = float(tracks["width"])
        self.H = float(tracks["height"])
        self.diag = math.hypot(self.W, self.H)
        self.elements = tracks["elements"]
        self.clips = tracks.get("clips", [])
        self.numeric_props = tracks["numericProps"]
        self.pi = {p: i for i, p in enumerate(self.numeric_props)}
        P = len(self.numeric_props)
        self.num = [np.asarray(a, dtype=np.float32).reshape(-1, P) for a in tracks["num"]]
        self.style_runs = tracks["styleRuns"]
        self.char_runs = tracks["charRuns"]
        self.own_char_runs = tracks.get("ownCharRuns") or tracks["charRuns"]
        # Line boxes per element, run-length encoded like the character runs.
        # Absent from a probe written before the sampler recorded it, in which
        # case lines_at returns None and the criteria that need it say so.
        self.line_runs = tracks.get("lineRuns")
        self.tweens = tweens["tweens"]
        self.moves = []
        self.apply_manifest(manifest)
        self._build_moves()
        self.apply_manifest(manifest)      # tag the moves once they exist

    # -- manifest ------------------------------------------------------------
    def apply_manifest(self, manifest):
        """Re-point the source at a manifest without re-probing. The declaration
        budget (rubric 4.3) grades the piece twice, once with the declarations
        and once without, and re-running the browser probe for that would cost
        a minute per film."""
        self.manifest = manifest
        self.register = manifest.get("register", DEFAULT_REGISTER)
        self.mechanical = set(manifest.get("mechanical", []))
        self.organic = set(manifest.get("organic", []))
        self.impact = set(manifest.get("impact", []))
        for mv in self.moves:
            # `mechanical` is a claim about a MOVE, not about an element. A
            # camera drift, a conveyor and an idle push are constant-velocity
            # drivers (canon 1.4: one `ease: "none"` driver with an onUpdate),
            # and the elements that carry one usually also carry a real
            # arrival: #sent takes its idle ramp at ease "none" and its exit on
            # power2.out four lines later. Honouring the declaration on the
            # element exempted the exit as well, which is how a naming a single
            # idle push lifted an ease row a whole band. The manifest still
            # names the element -- an author cannot name a tween -- and the
            # grader applies it to the tweens on that element that are actually
            # mechanical: authored linear, or measured linear where the ease is
            # not readable.
            named = self.is_named(mv["el"], self.mechanical)
            mv["mechanical"] = bool(named and _is_mechanical_tween(mv))
            mv["mechanicalNamed"] = named
            mv["organic"] = self.is_named(mv["el"], self.organic)
            mv["impact"] = self.is_named(mv["el"], self.impact)

    # -- per-element accessors ------------------------------------------------
    def prop(self, el, name):
        return self.num[el][:, self.pi[name]]

    def style_at(self, el, name, f):
        runs = self.style_runs[el].get(name) or []
        v = None
        for (start, val) in runs:
            if start <= f:
                v = val
            else:
                break
        return v

    def chars_at(self, el, f, own=True):
        runs = (self.own_char_runs[el] if own else self.char_runs[el]) or []
        v = 0
        for (start, val) in runs:
            if start <= f:
                v = val
            else:
                break
        return v

    def lines_at(self, el, f):
        """How many LINE BOXES this element's own text occupies at frame f, or
        None when the probe did not record it. This is the only honest test of
        whether a reading unit wraps. The box-height test it replaces --
        height > 1.6 x font-size -- fires on a single word and even on a single
        digit, because a masked-rise wrapper is routinely 1.8 to 2.1 times the
        font size, and that is the dominant construction in kinetic type."""
        if not self.line_runs or el >= len(self.line_runs):
            return None
        runs = self.line_runs[el] or []
        v = None
        for (start, val) in runs:
            if start <= f:
                v = val
            else:
                break
        return v

    def leaves_frame(self, mv):
        """True when a move labelled `exit` really takes the element away.

        The role heuristic calls any translate that resolves from rest to an
        offset an exit, which is right for a masked exit and wrong for a
        mid-card reposition. Closing the reading window on the wrong one put a
        ONE-FRAME window on a headline that is legible for three and a half
        seconds, and the readability criterion then charged it as a flashed
        card. The evidence, not the label, decides: after the move the element
        is transparent, or its box no longer overlaps the frame."""
        f = int(clamp(mv["endF"], 0, self.frames - 1))
        if float(self.prop(mv["el"], "opacity")[f]) < 0.5:
            return True
        x0, y0, x1, y1 = self.box_at(mv["el"], f)
        return bool(x1 <= 0 or y1 <= 0 or x0 >= self.W or y0 >= self.H)

    def window_moves(self, el):
        """(moves, basis) for the element's settled window.

        An element with no tween of its own is still on screen and still has to
        be read: a card written as a plain div inside a clip that is cut in and
        cut out carries no tween anywhere, and one animated only by an ancestor
        container inherits that ancestor's settle. Returning None for both is
        what made the three shortest cards in a 26 s film -- 14, 16 and 20
        frames, all under the absolute display floor -- invisible to every text
        criterion, which is precisely the case C15 exists to catch."""
        mine = [m for m in self.moves if m["el"] == el]
        if mine:
            return mine, "own"
        cur, seen = el, set()
        for _ in range(8):
            nxt = self.elements[cur].get("parent")
            if nxt is None or nxt < 0 or nxt == cur or nxt in seen:
                break
            seen.add(nxt)
            up = [m for m in self.moves if m["el"] == nxt]
            if up:
                return up, "ancestor"
            cur = nxt
        return [], "clip"

    def clip_of(self, el):
        cid = self.elements[el].get("clip")
        for c in self.clips:
            if c["id"] == cid:
                return c
        return None

    def is_named(self, el, names):
        if not names:
            return False
        e = self.elements[el]
        for name in names:
            n = name[1:] if str(name).startswith("#") else name
            if e.get("id") == n or e.get("key") == name:
                return True
        return False

    def is_mechanical(self, el):
        return self.is_named(el, self.mechanical)

    def group_of(self, el):
        """The element that stands for this one in the C3 onset census. Rubric
        C3: elements inside one .clip sub-group or one declared lockup count as
        ONE element, because a logo lockup resolving as one unit and a chart
        whose bars grow together are professional, not everything-at-once."""
        for i, group in enumerate(self.manifest.get("lockups", [])):
            if self.is_named(el, set(group)):
                return f"lockup{i}"
        e = self.elements[el]
        sub = e.get("subGroup")
        if sub:
            return f"{e.get('clip')}/{sub}"
        g = e.get("group")
        if g is not None and g >= 0 and g != el:
            return f"el{int(g)}"
        return f"el{el}"

    # -- moves ---------------------------------------------------------------
    def _build_moves(self):
        fps = self.fps
        for tw in self.tweens:
            props = [p for p in tw.get("props", [])]
            spatial = [p for p in props if p in SPATIAL_PROPS]
            paint = [p for p in props if p in PAINT_PROPS]
            samples = tw.get("easeSamples")
            samples = np.asarray(samples, dtype=float) if samples else \
                np.linspace(0, 1, 101)
            # Frame windows are biased INWARD (rubric 7, "bias clip boundaries
            # inward"). A tween starting at 0.9666 s at 30 fps belongs to frame
            # 29, not 28, and one ending mid-frame does not own the frame it
            # ends inside.
            sf = int(math.ceil(tw["start"] * fps - FRAME_SNAP_TOL))
            ef = int(math.floor((tw["start"] + tw["duration"]) * fps + FRAME_SNAP_TOL))
            if ef < sf:
                ef = sf
            nf = ef - sf
            kind = "spatial" if spatial else ("paint" if paint else "other")
            if kind == "spatial" and nf + 1 < MOVE_MIN_FRAMES:
                kind = "micro"
            for el in tw["targets"]:
                mv = {
                    "tween": tw["i"], "el": el,
                    "key": self.elements[el]["key"],
                    "clip": self.elements[el].get("clip"),
                    "start": tw["start"], "dur": tw["duration"],
                    "startF": sf, "endF": ef, "durF": max(nf, 1),
                    "props": props, "spatial": spatial, "paint": paint,
                    "kind": kind,
                    "ease": tw.get("easeString", "none"),
                    "easeSamples": samples,
                    "repeat": tw.get("repeat", 0),
                    "startAt": tw.get("startAt") or {},
                    "to": tw.get("to") or {},
                    "mechanical": False, "organic": False, "impact": False,
                }
                mv["onsetF"] = self._onset(mv)
                mv["settleF"] = self._settle(mv)
                mv.update(self._geometry(mv))
                # Rubric C1: classify from the MEASURED per-frame geometry, not
                # from the ease attached to the tween. Under the HyperFrames
                # contract a clip wrapper, a parent group and a child can each
                # carry a tween, so a child with ease "none" inside a parent
                # with power2.out is not linear on screen, and a child with
                # power2.out inside a linearly moving parent is not an ease-out.
                meas, basis = self._measured_curve(mv)
                mv["samples"] = meas if meas is not None else samples
                mv["curveBasis"] = basis
                mv["class"] = ("micro" if basis == "none"
                               else "inert" if basis == "inert"
                               else self._classify(mv["samples"]))
                mv["role"] = self._role(mv)
                mv["family"] = ease_family(mv["ease"], mv["easeSamples"])
                mv["ambient"] = (mv["dur"] >= AMBIENT_MIN_S
                                 and mv["dist"] < AMBIENT_MAX_TRAVEL * self.H
                                 and mv["scaleDelta"] < AMBIENT_MAX_TRAVEL)
                self.moves.append(mv)

    def s_at(self, mv, f):
        if mv["dur"] <= 1e-9:
            return 1.0
        p = clamp((f / self.fps - mv["start"]) / mv["dur"], 0.0, 1.0)
        return float(mv["easeSamples"][int(round(p * 100))])

    def _onset(self, mv):
        for f in range(mv["startF"], mv["endF"] + 1):
            if self.s_at(mv, f) >= ONSET_PROGRESS:
                return f
        return mv["endF"]

    def _settle(self, mv):
        for f in range(mv["startF"], mv["endF"] + 1):
            if all(abs(self.s_at(mv, g) - 1.0) < SETTLE_EPS
                   for g in range(f, mv["endF"] + 1)):
                return f
        return mv["endF"]

    def _geometry(self, mv):
        el = mv["el"]
        a = int(clamp(mv["startF"], 0, self.frames - 1))
        b = int(clamp(mv["settleF"], 0, self.frames - 1))
        cx, cy = self.prop(el, "cx"), self.prop(el, "cy")
        sc = self.prop(el, "scale")
        op = self.prop(el, "opacity")
        w, h = self.prop(el, "w"), self.prop(el, "h")
        dx, dy = float(cx[b] - cx[a]), float(cy[b] - cy[a])
        return {
            "dx": dx, "dy": dy, "dist": math.hypot(dx, dy),
            "scaleFrom": float(sc[a]), "scaleTo": float(sc[b]),
            "scaleDelta": abs(float(sc[b]) - float(sc[a])),
            "opFrom": float(op[a]), "opTo": float(op[b]),
            "cxFrom": float(cx[a]), "cyFrom": float(cy[a]),
            "cxTo": float(cx[b]), "cyTo": float(cy[b]),
            "boxW": float(w[b]), "boxH": float(h[b]),
        }

    def _measured_curve(self, mv):
        """s(t) from the on-screen rect and transform track, for the property
        with the largest normalised travel. Returns (samples101, basis)."""
        a = int(clamp(mv["startF"], 0, self.frames - 1))
        b = int(clamp(mv["endF"], 0, self.frames - 1))
        if b - a + 1 < SHAPE_MIN_FRAMES:
            # one intermediate sample cannot express an ease; a 33 ms slam is
            # not linear, it is unclassifiable, and gating a weight-2 criterion
            # on it is a false positive
            return None, "none"
        el = mv["el"]
        cx = self.prop(el, "cx")[a:b + 1].astype(float)
        cy = self.prop(el, "cy")[a:b + 1].astype(float)
        bw = self.prop(el, "w")[a:b + 1].astype(float)
        bh = self.prop(el, "h")[a:b + 1].astype(float)
        rot = self.prop(el, "rotation")[a:b + 1].astype(float)
        op = self.prop(el, "opacity")[a:b + 1].astype(float)
        # Every candidate is weighed in the SAME unit -- the fraction of the
        # frame diagonal that the element's own geometry travels on screen --
        # so a 0.02 scale change cannot outrank a 22 px slide and hand the
        # criterion the wrong curve. Size comes from the rect, not from
        # gsap.getProperty("scale"), because the rect composes a parent's scale
        # and the property does not.
        # Only the properties THIS tween animates may supply the curve. The
        # rect composes a parent's motion into whichever channel the tween
        # drives, which is the point of measuring geometry, but letting an
        # unrelated concurrent tween supply the series is not composition: a
        # 22 px power2.out slide read as linear because a mechanical scale ramp
        # on the same card grew the box 59 px over the same twelve frames.
        props = set(mv["props"])
        cands = []
        if props & (TRANSLATE_PROPS | {"top", "left"}):
            # Project onto the AXIS the tween drives. A masked word rising on
            # yPercent inside a wrapper that is simultaneously whipped sideways
            # has a net displacement dominated by the whip, and projecting onto
            # that vector read a clean expo.out rise as an ease-in.
            xs = bool(props & {"x", "xPercent", "translateX", "left"})
            ys = bool(props & {"y", "yPercent", "translateY", "top"})
            dx, dy = cx[-1] - cx[0], cy[-1] - cy[0]
            if xs and not ys:
                dy = 0.0
            elif ys and not xs:
                dx = 0.0
            tot = math.hypot(dx, dy)
            if tot >= C1_MIN_MEASURED_TRAVEL_PX:
                proj = ((cx - cx[0]) * dx + (cy - cy[0]) * dy) / (tot * tot)
                cands.append((tot / self.diag, proj))
        if props & {"scale", "scaleX", "scaleY", "width", "height"}:
            dw, dh = bw[-1] - bw[0], bh[-1] - bh[0]
            if max(abs(dw), abs(dh)) >= C1_MIN_MEASURED_TRAVEL_PX:
                series, d_ = (bw, dw) if abs(dw) >= abs(dh) else (bh, dh)
                cands.append((abs(d_) / self.diag, (series - series[0]) / d_))
        if props & {"rotation", "rotationX", "rotationY", "rotationZ"}:
            dro = rot[-1] - rot[0]
            if abs(dro) > 0.5:
                r = 0.5 * math.hypot(float(bw[-1]), float(bh[-1]))
                cands.append((abs(math.radians(dro)) * r / self.diag,
                              (rot - rot[0]) / dro))
        if mv["kind"] == "paint":
            dop = op[-1] - op[0]
            if abs(dop) > 0.02:
                cands.append((abs(dop), (op - op[0]) / dop))
        if not cands and (props & {"clipPath"}):
            # a clip-path wipe changes no rect: the box is the same and the
            # paint is masked, so the parsed ease is the only evidence there is
            return None, "ease"
        if not cands:
            # A spatial tween whose element never moves on screen is INERT: the
            # composition claims motion the viewer never sees. Falling back to
            # the parsed ease is exactly what rubric C1 forbids, and it hid a
            # masked word rise whose transform the browser was ignoring because
            # the target was an inline element.
            return None, ("inert" if mv["kind"] == "spatial" else "ease")
        _, series = max(cands, key=lambda c: c[0])
        out = _resample101(series)
        if out is None:
            return None, "ease"
        # A compound path. When a second tween on the same element (or on a
        # parent) runs across this one, the on-screen path is their sum and its
        # projection onto the net displacement can leave 0..1 entirely: one
        # scale settle measured a peak of 4.12, which C6 then read as a 312%
        # overshoot. A real overshoot peaks near 1.10 and elastic near 1.30, so
        # past C1_COMPOUND_PEAK the measurement is not of one move and the
        # parsed ease is the better evidence. Reported, not hidden.
        if float(out.max()) > C1_COMPOUND_PEAK or float(out.min()) < -C1_COMPOUND_DIP:
            return None, "ease-compound"
        return out, "measured"

    @staticmethod
    def _classify(s):
        s = np.asarray(s, dtype=float)
        q1, q2, q3 = float(s[25]), float(s[50]), float(s[75])
        # overshoot first: back.out has a high midpoint and would read as "out",
        # and that single tell is the one the sources call the number one
        # instant turn-off in agent-made video
        d = np.diff(smooth_box(s, C6_SMOOTH))
        settle = np.flatnonzero(np.asarray(smooth_box(s, C6_SMOOTH)) >= 1.0 - SETTLE_EPS)
        pre = len(d) if not len(settle) else max(int(settle[0]), 1)
        dd = d[:pre]
        sig = dd[np.abs(dd) > C1_OVERSHOOT_FLOOR]
        reversed_before_settle = len(sig) >= 2 and bool((np.diff(np.sign(sig)) != 0).any())
        if float(s.max()) > C1_OVERSHOOT_PEAK or reversed_before_settle:
            return "overshoot"
        if (abs(q1 - 0.25) < C1_LINEAR_TOL and abs(q2 - 0.5) < C1_LINEAR_TOL
                and abs(q3 - 0.75) < C1_LINEAR_TOL):
            return "linear"
        if abs(q2 - 0.5) <= C1_INOUT_MID_TOL and q1 <= C1_INOUT_Q1 and q3 >= C1_INOUT_Q3:
            return "inOut"
        if q2 >= C1_OUT_MID and q1 >= C1_OUT_Q1:
            return "out"
        if q2 <= C1_IN_MID:
            return "in"
        return "custom"

    def _role(self, mv):
        """Rubric 4.2 plus one addition, rule 5: a translate tween that resolves
        TO the element's rest position (offset -> 0) is an entrance, and one that
        leaves it (0 -> offset) is an exit. Without it the masked word-rise --
        the commonest entrance in kinetic type, where opacity never changes and
        the glyph never leaves the frame -- reads as a reposition and C1 cannot
        see a backwards ease on it."""
        if mv["opFrom"] < 0.05 and mv["opTo"] > 0.5:
            return "entrance"
        if mv["opTo"] < 0.05 and mv["opFrom"] > 0.5:
            return "exit"
        if mv["scaleFrom"] < 0.02 <= mv["scaleTo"]:
            return "entrance"
        if mv["scaleTo"] < 0.02 <= mv["scaleFrom"]:
            return "exit"
        outside = lambda x, y: x < 0 or y < 0 or x > self.W or y > self.H
        if outside(mv["cxFrom"], mv["cyFrom"]) and not outside(mv["cxTo"], mv["cyTo"]):
            return "entrance"
        if outside(mv["cxTo"], mv["cyTo"]) and not outside(mv["cxFrom"], mv["cyFrom"]):
            return "exit"
        for p in mv["spatial"]:
            if p not in TRANSLATE_PROPS:
                continue
            f0 = mv["startAt"].get(p)
            f1 = mv["to"].get(p)
            if f0 is None or f1 is None:
                continue
            if abs(f0) > 1e-6 and abs(f1) < 1e-6:
                return "entrance"
            if abs(f0) < 1e-6 and abs(f1) > 1e-6:
                return "exit"
        return "reposition"

    def ends_at_cut(self, mv):
        """True when the move is still running as its own clip ends: the cut is
        what takes the element away."""
        c = self.clip_of(mv["el"])
        if not c:
            return False
        end = int(math.floor((c["start"] + c["duration"]) * self.fps
                             + FRAME_SNAP_TOL)) - 1
        return mv["endF"] >= end - fscale(C1_EXIT_AT_CUT_FRAMES, self.fps)

    # -- text ----------------------------------------------------------------
    def text_elements(self):
        """Elements that carry characters of their OWN, not their descendants'.

        A container whose words live in per-word spans is not a text element:
        measuring it read a full-bleed word wall as one 112-character line at
        420 characters per second, and put that wall's deliberate full-frame
        bleed into the title-safe count as if it were overflowing type."""
        out = []
        for e in self.elements:
            i = e["i"]
            if not any(v for _, v in (self.own_char_runs[i] or [])):
                continue
            if not self.style_at(i, "fontSize", 0):
                continue
            out.append(i)
        return out

    def font_px(self, el, f):
        fs = self.style_at(el, "fontSize", f) or ""
        try:
            return float(re.sub(r"[^\d.]", "", fs) or 0)
        except ValueError:
            return 0.0

    def settled_window(self, el, cuts):
        """Entrance settle to exit onset, or the cut. Legibility is measured
        only inside this window (grade-original.py check 3).

        The clip is the authority on where the card ends when the source channel
        exists. Falling back to the next DETECTED cut collapsed several windows
        to two or three frames, because the blank-run model puts a boundary
        wherever a word arrives inside a card."""
        mine, basis = self.window_moves(el)
        c = self.clip_of(el)
        clip_a = clip_b = None
        if c:
            clip_a = int(math.ceil(c["start"] * self.fps - FRAME_SNAP_TOL))
            clip_b = int(math.floor((c["start"] + c["duration"]) * self.fps
                                    + FRAME_SNAP_TOL)) - 1
        if basis == "clip" and clip_a is None:
            # nothing animates it and no clip bounds it: there is no window to
            # measure, and inventing the whole film as one would put a static
            # background label into every text criterion
            return None
        if mine:
            ent = [m for m in mine if m["role"] == "entrance"]
            ext = [m for m in mine
                   if m["role"] == "exit" and self.leaves_frame(m)]
            a = max((m["settleF"] for m in ent),
                    default=min(m["startF"] for m in mine))
            ends = [m["onsetF"] - 1 for m in ext]
        else:
            a, ends = clip_a, []
        # An element with no exit tween stays on screen until its clip or the
        # next cut takes it away. Defaulting to the last tween's end frame
        # instead closed the window on the settle frame itself, and every text
        # criterion reported "no settled text elements" for a card that sits on
        # screen for most of a second.
        if clip_b is not None:
            ends.append(clip_b)
        else:
            nxt = [x for x in cuts if x > a]
            ends.append(nxt[0] - 1 if nxt else self.frames - 1)
        b = int(min(min(ends), self.frames - 1))
        if b < 0:
            return None
        if a > b:
            # The entrance does not settle before the cut takes the element
            # away. It is on screen for those frames and it is read in them,
            # however briefly, so the window opens where the element arrives
            # rather than not opening at all: a masked rise whose own clip cuts
            # mid-tween used to disappear from every text criterion, and a card
            # that is unreadably short is the finding, not an absence.
            a = max(0, min(int(a), b))
        op = self.prop(el, "opacity")
        a2 = int(clamp(a, 0, self.frames - 1))
        while a2 <= b and op[int(clamp(a2, 0, self.frames - 1))] < 0.9:
            a2 += 1
        if a2 > b:
            return None
        return self._still_span(el, a2, b)

    def _still_span(self, el, a, b):
        """Trim a window to the frames on which the element is actually STILL.

        Canon C13 measures "settled window only" and canon 3.1 defines the hold
        as the part of a card's life between the settle and the exit: "Card
        life: entrance -> settle -> hold -> exit -> gap. ONLY THE HOLD COUNTS."
        The window above is built from the element's OWN tweens, and an element
        with no tween of its own has none: a caption inside a card that the
        composition scales in and then pushes 132 px up the frame reported its
        whole 86-frame clip as settled, so a legibility criterion measured its
        colour on the frames it was flying off the top of the screen and named
        those frames as the worst. The delivered box already carries every
        ancestor transform, so stillness is read straight off it.

        A window that never goes still is returned unchanged rather than
        dropped: an element that never rests is a finding for C15's dwell row,
        not an element that leaves the contrast test."""
        a = int(clamp(a, 0, self.frames - 1))
        b = int(clamp(b, 0, self.frames - 1))
        if b <= a:
            return (a, b)
        box = np.asarray([self.box_at(el, f) for f in range(a, b + 1)], dtype=float)
        step = np.abs(np.diff(box, axis=0)).max(axis=1)
        thr = SETTLE_STILL_PX * (self.H / SETTLE_STILL_REF_H)
        still = np.concatenate(([True], step <= thr))
        idx = np.flatnonzero(still)
        if not len(idx):
            return (a, b)
        # the longest run of still frames, which is the hold
        best, run0, best0, best1 = 0, idx[0], a, b
        prev = idx[0]
        for i in list(idx[1:]) + [None]:
            if i is not None and i == prev + 1:
                prev = i
                continue
            if prev - run0 + 1 > best:
                best, best0, best1 = prev - run0 + 1, a + run0, a + prev
            if i is None:
                break
            run0, prev = i, i
        if best < SETTLE_STILL_MIN_FRAMES:
            return (a, b)
        return (int(best0), int(best1))

    def readable_window(self, el, cuts):
        """The settled window, but opened at the frame the element is READABLE
        rather than the frame it stops moving. A word that rises over fourteen
        frames on an expo.out is legible from about the third of them, and
        measuring only the frames after the settle understated the dwell of
        every masked word rise in the medium C15 was rewritten for: a card on
        screen for 400 ms reported nine settled frames and failed an absolute
        floor of 267."""
        win = self.settled_window(el, cuts)
        if not win:
            return None
        a, b = win
        ent = [m for m in self.moves if m["el"] == el and m["role"] == "entrance"]
        if not ent:
            return win
        first = a
        for m in ent:
            f = m["startF"]
            while f < m["settleF"] and self.s_at(m, f) < C15_READABLE_PROGRESS:
                f += 1
            first = min(first, f)
        op = self.prop(el, "opacity")
        while first < a and op[int(clamp(first, 0, self.frames - 1))] < C15_READABLE_PROGRESS:
            first += 1
        return (int(min(max(first, 0), a)), b)

    def box_at(self, el, f):
        f = int(clamp(f, 0, self.frames - 1))
        r = self.num[el][f]
        cx, cy, w, h = r[0], r[1], r[2], r[3]
        return (cx - w / 2.0, cy - h / 2.0, cx + w / 2.0, cy + h / 2.0)

    def still_delta(self):
        """Per-frame maximum on-screen movement of any element, in px. A
        composition under C5_SOURCE_STILL_EPS is frozen; a duplicate run over a
        composition above it is ambient the codec ate, not a stall."""
        d = np.zeros(self.frames, dtype=np.float32)
        for a in self.num:
            g = np.abs(np.diff(a[:, :4], axis=0)).max(axis=1)
            d[1:] = np.maximum(d[1:], g[: self.frames - 1])
        return d


class PixelSource:
    """The same interface as Source, fitted to tracked components instead of a
    timeline. It exists so C1, C2, C3 and C6 keep running when only the mp4 is
    given: the rubric says the ease CLASS can be fitted to the tracked curve,
    and a class fitted from pixels is worth more than an N/A.

    What it cannot know, and does not pretend to: which property drove a move,
    what the ease was called, whether an element is mechanical by name, and any
    text. Those criteria keep their own pixel branches or stay N/A."""

    def __init__(self, px, manifest):
        self.fps = px.fps
        self.frames = px.n
        self.W, self.H = float(DEC_W), float(DEC_H)
        self.diag = math.hypot(self.W, self.H)
        self.manifest = manifest
        self.register = manifest.get("register", DEFAULT_REGISTER)
        self.mechanical = set()
        self.organic = set()
        self.impact = set()
        self.clips = []
        self.numeric_props = ["cx", "cy", "w", "h", "x", "y", "xPercent", "yPercent",
                              "scale", "scaleX", "scaleY", "rotation", "opacity"]
        self.pi = {p: i for i, p in enumerate(self.numeric_props)}
        self.elements, self.num, self.moves = [], [], []
        for ti, tr in enumerate(px.tracks):
            self.elements.append({"i": ti, "key": f"track{ti}", "id": None, "tag": "TRACK",
                                  "cls": "", "clip": None, "parentIdx": -1, "parent": -1,
                                  "group": ti, "text": "", "depth": 0})
            a = np.zeros((px.n, 13), dtype=np.float32)
            for k, f in enumerate(tr["frames"]):
                x0, y0, x1, y1 = tr["box"][k]
                a[f] = [tr["cx"][k], tr["cy"][k], x1 - x0 + 1, y1 - y0 + 1,
                        0, 0, 0, 0, 1, 1, 1, 0, 1]
            self.num.append(a)
        self._build_moves(px)

    def apply_manifest(self, manifest):
        self.manifest = manifest
        self.register = manifest.get("register", DEFAULT_REGISTER)

    def prop(self, el, name):
        return self.num[el][:, self.pi[name]]

    def style_at(self, el, name, f):
        return None

    def chars_at(self, el, f, own=True):
        return 0

    def lines_at(self, el, f):
        return None

    def window_moves(self, el):
        return [m for m in self.moves if m["el"] == el], "own"

    def clip_of(self, el):
        return None

    def is_named(self, el, names):
        return False

    def is_mechanical(self, el):
        return False

    def group_of(self, el):
        return f"el{el}"

    def font_px(self, el, f):
        return 0.0

    def text_elements(self):
        return []

    def settled_window(self, el, cuts):
        return None

    def still_delta(self):
        return np.zeros(self.frames, dtype=np.float32)

    def box_at(self, el, f):
        f = int(clamp(f, 0, self.frames - 1))
        r = self.num[el][f]
        return (r[0] - r[2] / 2, r[1] - r[3] / 2, r[0] + r[2] / 2, r[1] + r[3] / 2)

    def s_at(self, mv, f):
        if mv["durF"] <= 0:
            return 1.0
        p = clamp((f - mv["onsetF"]) / mv["durF"], 0.0, 1.0)
        return float(mv["samples"][int(round(p * 100))])

    def _build_moves(self, px):
        for ti, tr in enumerate(px.tracks):
            fr, cx, cy = tr["frames"], tr["cx"], tr["cy"]
            ar = tr["area"]
            segs, cur = [], [0]
            for k in range(1, len(fr)):
                stable = (PIXEL_SEG_AREA_LO <= ar[k] / max(ar[k - 1], 1e-6) <= PIXEL_SEG_AREA_HI)
                if fr[k] != fr[k - 1] + 1 or not stable:
                    segs.append(cur)
                    cur = [k]
                else:
                    cur.append(k)
            segs.append(cur)
            for seg in segs:
                if len(seg) < PIXEL_MOVE_MIN_FRAMES:
                    continue
                xs = np.array([cx[k] for k in seg], float)
                ys = np.array([cy[k] for k in seg], float)
                step = np.hypot(np.diff(xs), np.diff(ys))
                total = float(step.sum())
                if total < PIXEL_MOVE_MIN_TRAVEL:
                    continue
                s = np.concatenate(([0.0], np.cumsum(step))) / total
                f0 = fr[seg[0]]
                on = f0 + int(np.argmax(s >= ONSET_PROGRESS))
                st = f0 + int(np.argmax(s >= 1 - SETTLE_EPS))
                if st - on < PIXEL_MOVE_MIN_FRAMES - 1:
                    continue
                # resample the fitted curve onto the rubric's 101 points
                loc = np.linspace(0, 1, st - on + 1)
                samples = np.interp(np.linspace(0, 1, 101), loc,
                                    (s[on - f0:st - f0 + 1] - s[on - f0])
                                    / max(s[st - f0] - s[on - f0], 1e-9))
                role = "reposition"
                if seg[0] == 0 and fr[0] > 0:
                    role = "entrance"
                elif seg[-1] == len(fr) - 1 and fr[-1] < px.n - 1:
                    role = "exit"
                mv = {
                    "tween": -1, "el": ti, "key": f"track{ti}", "clip": None,
                    "start": on / px.fps, "dur": (st - on) / px.fps,
                    "startF": on, "endF": st, "durF": max(st - on, 1),
                    "onsetF": on, "settleF": st,
                    "props": ["fitted"], "spatial": ["x"], "paint": [], "kind": "spatial",
                    "ease": "fit", "samples": samples, "easeSamples": samples,
                    "curveBasis": "measured", "repeat": 0,
                    "startAt": {}, "to": {}, "mechanical": False,
                    "organic": False, "impact": False,
                    "dx": float(xs[-1] - xs[0]), "dy": float(ys[-1] - ys[0]),
                    "dist": total,
                    "scaleFrom": 1.0, "scaleTo": 1.0, "scaleDelta": 0.0,
                    "opFrom": 1.0, "opTo": 1.0,
                    "cxFrom": float(xs[0]), "cyFrom": float(ys[0]),
                    "cxTo": float(xs[-1]), "cyTo": float(ys[-1]),
                    "boxW": float(tr["box"][seg[-1]][2] - tr["box"][seg[-1]][0] + 1),
                    "boxH": float(tr["box"][seg[-1]][3] - tr["box"][seg[-1]][1] + 1),
                    "role": role,
                }
                mv["class"] = Source._classify(mv["samples"])
                mv["family"] = ease_family("function", mv["samples"])
                mv["ambient"] = (mv["dur"] >= AMBIENT_MIN_S
                                 and mv["dist"] < AMBIENT_MAX_TRAVEL * self.H)
                self.moves.append(mv)


def ease_family(ease_string, samples):
    """power1..4, sine, expo, circ, back, elastic, bounce, steps, none, custom.
    Reported as a label only: C2 counts clusters of measured SHAPE, because a
    name-based count is inflatable by an author who does nothing, and a piece
    built with hand-shaped speed graphs reports one family and scores C."""
    s = (ease_string or "").strip()
    m = re.match(r"^(power[0-4]|sine|expo|circ|back|elastic|bounce|steps|slow|rough|none|linear)",
                 s, re.I)
    if m:
        return m.group(1).lower()
    if s in ("function", "", None):
        q = (round(float(samples[25]) / C2_FIT_CLUSTER_RADIUS),
             round(float(samples[50]) / C2_FIT_CLUSTER_RADIUS),
             round(float(samples[75]) / C2_FIT_CLUSTER_RADIUS))
        return f"fit{q}"
    return s.split(".")[0].lower()


# =============================================================================
# cuts
# =============================================================================

def detect_cuts(px, manifest, source):
    if manifest.get("cuts"):
        return sorted({int(c) for c in manifest["cuts"]}), "manifest"
    sep = fscale(CUT_MIN_SEPARATION, px.fps)
    blank = px.ink_frac < CUT_BLANK_INK
    cuts = {0}
    # a blank run is a cut boundary AND a rhythm feature (SKILL.md 3.2)
    f = 0
    while f < px.n:
        if blank[f]:
            g = f
            while g < px.n and blank[g]:
                g += 1
            if g < px.n:
                cuts.add(g)
            f = g
        else:
            f += 1
    ground = px.ground
    for f in range(1, px.n):
        if abs(ground[f] - ground[f - 1]) > CUT_GROUND_FLIP:
            cuts.add(f)
    cp = px.col_profile
    norm = cp / np.maximum(cp.sum(axis=1, keepdims=True), 1.0)
    l1 = np.abs(np.diff(norm, axis=0)).sum(axis=1)
    for f in range(1, px.n):
        if blank[f] or blank[f - 1]:
            continue
        if l1[f - 1] > CUT_COLPROFILE_L1:
            cuts.add(f)
    out = []
    for c in sorted(cuts):
        if not out or c - out[-1] >= sep:
            out.append(c)
    return out, "blank-run model"


def reconcile_cuts(cuts, source, fps):
    """Rubric step 4: reconcile the detected cut list against the tween table's
    clip boundaries and report any mismatch. Reported, never silently applied --
    a composition whose clips and whose visible cuts disagree is telling you
    something, and quietly preferring one of them hides it."""
    if source is None or not source.clips:
        return None
    starts = sorted({int(math.ceil(c["start"] * fps - FRAME_SNAP_TOL))
                     for c in source.clips})
    tol = fscale(2, fps)
    matched = sum(1 for s in starts if any(abs(s - c) <= tol for c in cuts))
    extra = [c for c in cuts if not any(abs(s - c) <= tol for s in starts)]
    return {"clipStarts": len(starts), "matched": matched,
            "unmatchedClipStarts": len(starts) - matched, "extraCuts": extra}


def beats_from_cuts(cuts, n, px):
    """A beat is a CONTENT run. Trailing blank frames belong to the gap after
    the card, not to the card, and an all-blank stretch is not a beat at all --
    counting the lead-in as one put a 74-frame "beat" of nothing into every
    rhythm statistic."""
    blank = px.ink_frac < CUT_BLANK_INK
    b = []
    for i, c in enumerate(cuts):
        e = cuts[i + 1] - 1 if i + 1 < len(cuts) else n - 1
        while e > c and blank[e]:
            e -= 1
        if e > c and not blank[c:e + 1].all():
            b.append((c, e))
    return b


def blank_runs(px):
    blank = px.ink_frac < CUT_BLANK_INK
    runs, f = [], 0
    while f < px.n:
        if blank[f]:
            g0 = f
            while f < px.n and blank[f]:
                f += 1
            runs.append((g0, f - 1))
        else:
            f += 1
    return runs


# =============================================================================
# audio
# =============================================================================

class Audio:
    def __init__(self, path, fps, manifest):
        self.present = False
        self.stream = False
        self.onsets = []
        self.hits = []
        self.lufs = None
        self.true_peak = None
        self.sample_peak = None
        self.rate = None
        self.channels = None
        self.grid = None
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
             "stream=codec_name,sample_rate,channels", "-of", "json", path],
            capture_output=True, text=True).stdout
        try:
            streams = json.loads(probe).get("streams", [])
        except json.JSONDecodeError:
            streams = []
        if not streams:
            return
        self.stream = True
        try:
            self.rate = int(streams[0].get("sample_rate") or 0)
            self.channels = int(streams[0].get("channels") or 0)
        except (TypeError, ValueError):
            pass
        raw = sh_out(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1",
                      "-ar", str(AUDIO_SR), "-"])
        sig = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
        if len(sig) < AUDIO_SR // 4 or float(np.abs(sig).max()) < 1e-5:
            return
        self.present = True
        self.sig = sig
        self.onsets, self.hits = self._flux_onsets(sig)
        eb = sh_err(["ffmpeg", "-v", "info", "-i", path, "-af", "ebur128=peak=true",
                     "-f", "null", "-"])
        m = re.findall(r"I:\s+(-?[\d.]+) LUFS", eb)
        self.lufs = float(m[-1]) if m else None
        # Gate on TRUE peak, not sample peak: inter-sample peaks after lossy
        # encoding can exceed sample peak by more than 1 dB, which is why every
        # published standard specifies dBTP. The ebur128 pass already reports it
        # and the old code threw the line away and read volumedetect instead.
        tp = re.search(r"True peak:\s*\n\s*Peak:\s*(-?[\d.]+) dBFS", eb)
        if tp:
            self.true_peak = float(tp.group(1))
        else:
            m = re.findall(r"TPK:\s*(-?[\d.]+)\s+(-?[\d.]+)", eb)
            if m:
                self.true_peak = max(float(m[-1][0]), float(m[-1][1]))
        vd = sh_err(["ffmpeg", "-v", "info", "-i", path, "-af", "volumedetect",
                     "-f", "null", "-"])
        m = re.findall(r"max_volume:\s+(-?[\d.]+)", vd)
        self.sample_peak = float(m[-1]) if m else None
        if self.true_peak is None:
            self.true_peak = self.sample_peak
        self.grid = self._fit_grid(fps)

    @staticmethod
    def _flux_onsets(sig):
        n_fft, hop = 1024, 256
        if len(sig) < n_fft * 4:
            return [], []
        w = np.hanning(n_fft)
        nfr = 1 + (len(sig) - n_fft) // hop
        idx = np.arange(n_fft)[None, :] + hop * np.arange(nfr)[:, None]
        S = np.abs(np.fft.rfft(sig[idx] * w, axis=1))
        flux = np.maximum(0.0, np.diff(S, axis=0)).sum(axis=1)
        if not len(flux) or flux.max() <= 0:
            return [], []
        # adaptive threshold: local mean plus a fraction of the local spread
        k = 21
        pad = np.pad(flux, (k // 2, k // 2), mode="edge")
        loc = np.convolve(pad, np.ones(k) / k, mode="valid")[: len(flux)]
        thr = loc + 0.35 * flux.std()
        peaks = []
        for i in range(1, len(flux) - 1):
            if flux[i] > thr[i] and flux[i] >= flux[i - 1] and flux[i] > flux[i + 1]:
                if peaks and (i - peaks[-1][0]) < 4:
                    if flux[i] > peaks[-1][1]:
                        peaks[-1] = (i, flux[i])
                    continue
                peaks.append((i, flux[i]))
        times = [((i + 1) * hop + n_fft / 2) / AUDIO_SR for i, _ in peaks]
        if not peaks:
            return [], []
        vals = np.array([v for _, v in peaks])
        cut = np.quantile(vals, C18_ONSET_QUARTILE)
        hits = [t for t, (_, v) in zip(times, peaks) if v >= cut]
        return times, hits

    def _fit_grid(self, fps):
        """Beat period and phase in FRAMES, by direct search over the onset
        list. Autocorrelation of the flux envelope on a 26 s bed gave a top
        peak of 0.238 against a runner-up of 0.234, which is no peak at all;
        fitting the grid to the onsets themselves is unambiguous or it fails
        loudly, and C10 and C18 both need it to fail loudly."""
        if len(self.onsets) < 8:
            return None
        of = np.asarray(self.onsets, float) * fps
        best = None
        tol = float(C10_GRID_TOL_FRAMES)
        for P in np.arange(fps * 60.0 / 200.0, fps * 60.0 / 60.0, 0.25):
            for ph in np.arange(0.0, P, 0.5):
                r = np.abs(((of - ph + P / 2) % P) - P / 2)
                c = int((r <= tol).sum())
                if best is None or c > best[0]:
                    best = (c, float(P), float(ph))
        if best is None:
            return None
        share = best[0] / len(of)
        return {"period": best[1], "phase": best[2], "onsetShare": share,
                "bpm": 60.0 * fps / best[1]}

    def bar_lines(self, fps, n_frames, beats_per_bar=4):
        if not self.grid:
            return []
        P = self.grid["period"] * beats_per_bar
        ph = self.grid["phase"]
        out, k = [], 0
        while ph + k * P < n_frames:
            out.append(ph + k * P)
            k += 1
        return out


# =============================================================================
# the report
# =============================================================================

CRITERIA_NAMES = {
    "C1": "ease discipline", "C2": "ease vocabulary", "C3": "simultaneity",
    "C4": "hold ratio", "C5": "frame integrity", "C6": "settle quality",
    "C7": "arcs", "C8": "secondary motion", "C9": "anticipation",
    "C10": "timing contrast", "C11": "distance-duration", "C12": "type hierarchy",
    "C13": "contrast", "C14": "safe margins", "C15": "readability",
    "C16": "palette", "C17": "transition design", "C18": "audio sync",
    "C18D": "audio delivery", "C19": "reveal craft and blur",
    "C20": "photosensitive flash", "C21": "restraint", "C22": "framing",
    "C23": "encode QC", "C23D": "duration and cadence", "C24": "eye-trace",
}

BASIS = {
    "C1": "LottieFiles CRITICAL linear-on-spatial; Disney principle 6",
    "C2": "techniques.md 3 easings; gsap-easing 'bounce everywhere reads cheap'",
    "C3": "LottieFiles choreography 1/3 rule; School of Motion mistake 5",
    "C4": "LottieFiles 100-200 ms stillness; HyperFrames build/breathe/resolve",
    "C5": "rubric C5 rewrite: flash frames, cadence, full-resolution duplicates",
    "C6": "LottieFiles overshoot budget by personality; grade-original.py check 8",
    "C7": "Disney principle 7 arcs, declared organic elements only",
    "C8": "Disney principles 5 and 8; declared secondaryPairs only",
    "C9": "Disney principle 2 anticipation, register-gated",
    "C10": "HyperFrames 'slowest scene 3x slower'; bar multiples on a grid",
    "C11": "LottieFiles distance-duration table; 0.5% of frame width per frame",
    "C12": "type scale adherence; video-composition.md 18-24 px floor",
    "C13": "WCAG 2.2 SC 1.4.3 large text 3:1, tiled; APCA Lc advisory",
    "C14": "SMPTE ST 2046-1, action-safe on broadcast delivery only",
    "C15": "Netflix timed text 5/6 s and 17-20 cps; RSVP 200-300 ms per word",
    "C16": "palette adherence at CIEDE2000 8; hue census as a report line",
    "C17": "HyperFrames transitions overview rules 1-3; direction continuity",
    "C18": "EBU R37 / ITU-R BT.1359-1; one-frame-early lock window",
    "C18D": "EBU R128 / AES TD1008 loudness and true peak by delivery",
    "C19": "quality-checklist CRITICAL opacity-only; 'motion blur on, always'",
    "C20": "W3C SC 2.3.1 three flashes or below threshold",
    "C21": "motion-principles.md 'alive with ONE ambient motion'",
    "C22": "rubric C22, alignment and margin consistency (report only)",
    "C23": "rubric C23 encode and delivery QC",
    "C23D": "rubric C23, duration and frame count exactly as authored",
    "C24": "rubric C24, eye-trace across the cut (report only)",
}



def strobe_scan(px, src, cuts, manifest, fps):
    """The per-frame EDGE-travel map. Returns (travel, strobe, moving, thr, fast),
    where travel[f] is the largest per-frame edge displacement on frame f as a
    fraction of frame WIDTH, and the tolerated jump scales WITH the delivered
    rate (halve at 24, roughly double at 60). Canon section 8 item 8 states the
    tell in exactly these terms: "per-frame edge travel over 0.5 % of frame
    width".

    Regions are paired between consecutive frames by bounding-box overlap and
    the displacement measured is the largest of the four EDGES, not the
    centroid. A centroid moves whenever a component grows, merges or splits
    with nothing on screen translating: measured against the centroid, a 26 s
    film reported 218, 325 and 132 px of per-frame travel on frames whose real
    edge displacement was 2.6, 1.9 and 21 px.

    The pairing is guarded three ways, because an unguarded pair IS the merge
    the centroid version could not see either: only the largest
    C11_STROBE_MAX_COMPS regions of a frame are considered, a partner has to
    cover C11_STROBE_MATCH_SHARE of the smaller box, and a region with more
    than one such partner on either side is a merge or a split and is dropped
    -- in both the box jumps to a union without anything moving.

    `strobe` is the set this function would charge and `fast` the same set
    before declared shutter passes are removed. Both are advisory here: the
    corrected C11 policy -- a shutter DOUBLES the tolerance instead of
    exempting the frames, and a run whose own travel crosses half the frame is
    a transition by class -- lives in crit_motion.strobe_scan, which reads the
    travel map from here so C11 and C19 measure one thing.
    """
    thr = C11_STROBE_FRAC * (float(fps) / C11_STROBE_FPS_REF)
    shutter = (manifest or {}).get("shutterFrames", []) or []
    near_cut = set()
    for c in (cuts or []):
        near_cut.update(range(int(c) - 1, int(c) + 2))

    def biggest(f):
        cs = [c for c in px.comps[f] if c[0] >= C11_STROBE_MIN_AREA]
        cs.sort(key=lambda c: -c[0])
        return cs[:C11_STROBE_MAX_COMPS]

    def share(a, b):
        ix = min(a[5], b[5]) - max(a[3], b[3])
        iy = min(a[6], b[6]) - max(a[4], b[4])
        if ix <= 0 or iy <= 0:
            return 0.0
        inter = float(ix * iy)
        small = min(max((a[5] - a[3]) * (a[6] - a[4]), 1.0),
                    max((b[5] - b[3]) * (b[6] - b[4]), 1.0))
        return inter / small

    travel, moving, strobe, fast = {}, set(), {}, {}
    prev = biggest(0) if px.n else []
    for f in range(1, px.n):
        cur = biggest(f)
        best = 0.0
        for c in cur:
            partners = [q for q in prev if share(c, q) >= C11_STROBE_MATCH_SHARE]
            if len(partners) != 1:
                continue                  # no partner, or a merge
            q = partners[0]
            back = [x for x in cur if share(q, x) >= C11_STROBE_MATCH_SHARE]
            if len(back) != 1:
                continue                  # a split
            fill = (float(c[5] - c[3]) * float(c[6] - c[4])) / float(DEC_W * DEC_H)
            if fill >= C11_STROBE_TRANSIT_FILL:
                continue                  # a transition by class, canon 5
            d = max(abs(c[3] - q[3]), abs(c[5] - q[5]),
                    abs(c[4] - q[4]), abs(c[6] - q[6]))
            best = max(best, float(d))
        prev = cur
        if best <= 0.0:
            continue
        if best > C11_STROBE_MOVING_PX:
            moving.add(f)
        frac = best / DEC_W
        travel[f] = frac
        if frac > thr and f not in near_cut:
            fast[f] = frac
            if not any(a <= f <= b for (a, b) in shutter):
                strobe[f] = frac
    return travel, strobe, moving, thr, fast

def hero_moves(src, beats, px=None):
    """One hero move per beat: the move on the element with the largest settled
    INK area, or the element the manifest names. Rubric 4.2 says ink area; a
    bounding box was the one place this file substituted a box for an ink count,
    which its own docstring forbids, and it feeds C8, C9, C10 and C18."""
    if src is None:
        return []
    named = src.manifest.get("hero", {})
    out = []
    for bi, (a, b) in enumerate(beats):
        cand = [m for m in src.moves if a <= m["onsetF"] <= b and m["kind"] == "spatial"]
        if not cand:
            continue
        want = named.get(str(bi)) or named.get(str(bi + 1))
        if want:
            named_moves = [m for m in cand if m["key"] == want
                           or src.elements[m["el"]].get("id") == str(want).lstrip("#")]
            if named_moves:
                out.append(max(named_moves, key=lambda m: m["dist"]))
                continue

        def ink_area(m):
            f = int(clamp(m["settleF"], 0, src.frames - 1))
            r = src.num[m["el"]][f]
            if r[12] <= 0.5:
                return 0.0
            if px is None:
                return float(r[2] * r[3])
            x0, y0, x1, y1 = src.box_at(m["el"], f)
            sx, sy = DEC_W / src.W, DEC_H / src.H
            bx0 = int(clamp(x0 * sx, 0, DEC_W - 1))
            bx1 = int(clamp(x1 * sx, 1, DEC_W))
            by0 = int(clamp(y0 * sy, 0, DEC_H - 1))
            by1 = int(clamp(y1 * sy, 1, DEC_H))
            pf = int(clamp(f, 0, px.n - 1))
            if bx1 <= bx0 or by1 <= by0:
                return 0.0
            return float(px.mask[pf, by0:by1, bx0:bx1].sum())
        out.append(max(cand, key=ink_area))
    return out



def ffprobe_video(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
         "-show_entries",
         "stream=nb_read_frames,avg_frame_rate,width,height,duration,pix_fmt,"
         "color_range,color_primaries,color_transfer",
         "-of", "json", path], capture_output=True, text=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = s["avg_frame_rate"].split("/")
    fps = float(num) / float(den)
    return {
        "fps": fps,
        "frames": int(s["nb_read_frames"]),
        "width": int(s["width"]),
        "height": int(s["height"]),
        "duration": float(s.get("duration", 0) or 0),
        "pix_fmt": s.get("pix_fmt"),
        "color_range": s.get("color_range"),
        "color_primaries": s.get("color_primaries"),
        "color_transfer": s.get("color_transfer"),
    }


def composition_entry(comp):
    if os.path.isdir(comp):
        return os.path.join(comp, "index.html")
    return comp


def read_declared(entry):
    if not entry or not os.path.exists(entry):
        return None
    html = io.open(entry, encoding="utf-8", errors="replace").read()

    def grab(pat):
        m = re.search(pat, html)
        return float(m.group(1)) if m else None
    return {"duration": grab(r'data-duration="([\d.]+)"'),
            "fps": grab(r'data-fps="([\d.]+)"'),
            "width": grab(r'data-width="([\d.]+)"'),
            "height": grab(r'data-height="([\d.]+)"')}


def read_probe(out_dir):
    """Load a probe dump written by an earlier run. --reuse-probe exists so a
    calibration sweep does not re-open a headless browser twenty-five times;
    it is never the default, because a stale dump grades a film that no longer
    exists."""
    tp = os.path.join(out_dir, "tracks.json")
    wp = os.path.join(out_dir, "tweens.json")
    if not (os.path.exists(tp) and os.path.exists(wp)):
        return None
    tracks = json.load(io.open(tp, encoding="utf-8"))
    tweens = json.load(io.open(wp, encoding="utf-8"))
    if tracks.get("skipped"):
        return None
    return tracks, tweens


def run_probe(comp, fps, out_dir):
    here = os.path.dirname(os.path.abspath(__file__))
    script = os.path.join(here, "probe-source.mjs")
    r = subprocess.run(["node", script, comp, "--fps", str(fps), "--out", out_dir],
                       capture_output=True, text=True, errors="replace")
    sys.stderr.write(r.stderr)
    if r.returncode != 0:
        return None
    tp = os.path.join(out_dir, "tracks.json")
    wp = os.path.join(out_dir, "tweens.json")
    if not (os.path.exists(tp) and os.path.exists(wp)):
        return None
    tracks = json.load(io.open(tp, encoding="utf-8"))
    tweens = json.load(io.open(wp, encoding="utf-8"))
    if tracks.get("skipped"):
        sys.stderr.write(f"grade-mg: source channel skipped ({tracks['reason']})\n")
        return None
    return tracks, tweens


def count_declarations(manifest):
    """Named declarations, not manifest keys: 27 cuts and 20 hero entries are 47
    claims about the piece, and the rubric's budget is about claims."""
    n = 0
    for k in DECLARATION_KEYS:
        v = manifest.get(k)
        if v is None:
            continue
        if isinstance(v, bool):
            n += 1 if v else 0
        elif isinstance(v, (list, tuple, dict)):
            n += len(v)
        else:
            n += 1
    return n


def strip_exemptions(manifest):
    m = copy.deepcopy(manifest)
    for k in EXEMPTION_KEYS:
        m.pop(k, None)
    return m



# =============================================================================
# the aggregate, canon section 7
# =============================================================================

# One authoritative table. A criterion module carries its own copy so it can be
# run standalone; the integrator's copy WINS, because a family that disagrees
# with canon about its own weight must not be able to move the total.
CANON_WEIGHTS = {
    "C1": 2, "C2": 1, "C3": 2, "C4": 1, "C5": 1, "C6": 1, "C7": 1, "C8": 1,
    "C9": 1, "C10": 1, "C11": 1, "C12": 1, "C13": 0, "C14": 1, "C15": 1,
    "C16": 1, "C17": 2, "C18": 1, "C18D": 0, "C19": 2, "C20": 0, "C21": 1,
    "C22": 1, "C23": 1, "C23D": 0, "C24": 1,
}
ORDER = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11",
         "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C18D", "C19",
         "C20", "C21", "C22", "C23", "C23D", "C24"]


class Grade:
    """The twenty-six rows of canon's twenty-four criteria, the aggregate and
    the worst-first table. C18 and C23 each report a craft row and a gate row,
    which is why there are twenty-six."""

    def __init__(self, rows=None):
        self.rows = list(rows or [])

    def add_row(self, row):
        """Normalise one family's row against canon. weight and gate come from
        CANON_WEIGHTS and GATES, never from the module, and a band is None
        exactly when the row is N/A."""
        cid = row["id"]
        if cid not in CANON_WEIGHTS:
            raise SystemExit("grade-mg: criterion %s is not in canon section 7" % cid)
        na = bool(row.get("na"))
        band = None if na else row.get("band")
        if not na and band not in BAND_POINTS:
            raise SystemExit("grade-mg: %s returned band %r and na False" % (cid, band))
        self.rows.append({
            "id": cid,
            "name": row.get("name") or CRITERIA_NAMES.get(cid, cid),
            "weight": CANON_WEIGHTS[cid],
            "gate": cid in GATES,
            "na": na,
            "measured": row.get("measured") or {},
            "band": band,
            # worstFrames arrives RANKED BY SEVERITY and is not re-sorted
            "worstFrames": [int(f) for f in dict.fromkeys(row.get("worstFrames") or [])][:6],
            "basis": row.get("basis") or BASIS.get(cid, ""),
            "note": row.get("note") or "",
            "declarations": list(row.get("declarations") or []),
        })

    def by_id(self):
        return {r["id"]: r for r in self.rows}

    def aggregate(self):
        """Canon section 7, verbatim.

          W = sum(points * weight) / sum(weight) over APPLICABLE criteria
          S = every applicable criterion at S or N/A
          A = W >= 90 and no C
          B = W >= 75 and at most two Cs, none of them gates
          C = anything else, or any gate at C
        """
        live = [r for r in self.rows if not r["na"]]
        num = sum(BAND_POINTS[r["band"]] * r["weight"] for r in live)
        den = sum(r["weight"] for r in live)
        w = (num / den) if den else 0.0
        cs = [r["id"] for r in live if r["band"] == "C"]
        gates_failed = [r["id"] for r in live if r["gate"] and r["band"] == "C"]
        self.unrated = ""
        # CANON'S OWN PRIORITIES DECIDE WHETHER THE PIECE WAS GRADED AT ALL.
        # Section 7 gives weight 2 to exactly four criteria -- C1 ease
        # discipline, C3 simultaneity, C17 transition design, C19 reveal craft
        # -- which is canon stating what a motion graphic is judged on. A piece
        # on which one of those cannot be measured has not been graded on this
        # rubric, and W over whatever remains is an average of the rows it
        # happened to exercise. That is not a hypothetical: a 3.5 s static title
        # card with five word rises leaves C1 and C3 unmeasurable, keeps twelve
        # absence-of-defect rows that are all S or A because there is nothing in
        # the file to fault, and scores 90.4 -- above every finished film in the
        # corpus. The two weight-2 rows it does keep cannot save it either, and
        # sending them to N/A as well makes the number GO UP, because removing
        # an above-average row raises an average. The floor has to be on
        # coverage, and canon's weights are where the coverage line already is.
        heavy = [r for r in self.rows if r["weight"] >= OVERALL_HEAVY_WEIGHT]
        heavy_na = [r["id"] for r in heavy if r["na"]]
        if heavy_na:
            self.unrated = (
                "%s could not be measured, and canon section 7 gives weight 2 to "
                "exactly four criteria: a piece that does not exercise all of "
                "them has not been graded on this rubric. The weighted score is "
                "withheld and the piece is unrated."
                % ", ".join(heavy_na))
            return "C", w, gates_failed
        if len(live) < OVERALL_MIN_GRADED:
            # Too little of the film is measurable for W to mean anything, so
            # the number is withheld and the piece does not pass a target. This
            # is the empty-file case: absence of evidence scored as evidence of
            # quality is the one way a grader can be gamed for free.
            self.unrated = ("only %d of %d criteria could be measured, under the "
                            "minimum of %d: the weighted score is withheld and "
                            "the piece is unrated"
                            % (len(live), len(self.rows), OVERALL_MIN_GRADED))
            return "C", w, gates_failed
        if gates_failed:
            overall = "C"
        elif live and all(r["band"] == "S" for r in live):
            overall = "S"
        elif w >= OVERALL_A_W and not cs:
            overall = "A"
        elif w >= OVERALL_B_W and len(cs) <= OVERALL_B_MAX_C:
            overall = "B"
        else:
            overall = "C"
        return overall, w, gates_failed

    def report(self, overall, w, gates_failed, inputs, budget):
        # canon 7: print the worst-first table BEFORE the aggregate, a studio
        # reads only the table; and print the declaration budget, because the
        # author of the piece writes the manifest.
        print()
        print("  declarations %d in the manifest, %d consumed by a criterion"
              "   criteria improved by one: %d%s"
              % (budget["declarations"], budget["consumed"], budget["improved"],
                 ("  (" + ", ".join(budget["improvedIds"]) + ")")
                 if budget["improvedIds"] else ""))
        if budget["flag"]:
            print("  " + budget["flag"])
        order = {"C": 0, "B": 1, "A": 2, "S": 3, None: 4}
        rows = sorted(self.rows, key=lambda r: (order[r["band"]], -r["weight"],
                                                ORDER.index(r["id"])))
        print()
        print("  %-6s%-24s%2s  %-5s%-46s %s"
              % ("", "criterion", "w", "band", "measured", "worst@"))
        print("  " + "-" * 106)
        for r in rows:
            band = "N/A" if r["na"] else r["band"]
            parts = ["%s=%.3g" % (k, v) if isinstance(v, float) else "%s=%s" % (k, v)
                     for k, v in r["measured"].items()]
            meas = ""
            for part in parts:                      # never truncate mid-number
                nxt = (meas + ", " + part) if meas else part
                if len(nxt) > 46:
                    break
                meas = nxt
            worst = ",".join(str(f) for f in r["worstFrames"]) or "-"
            gate = "*" if r["gate"] else " "
            print("  %-6s%-24s%2d%s %-5s%-46s %s"
                  % (r["id"], r["name"], r["weight"], gate, band, meas, worst))
            if r["note"]:
                print("         -> " + r["note"])
            if r["id"] in budget["improvedIds"]:
                # a row that improved but names no claim of its own improved
                # because a key it does not read was removed from the manifest
                # -- `silent` taking the audio rows out of scope is the usual
                # one -- so the relief keys the manifest actually carries are
                # named instead of the word "a declaration"
                caused = r.get("causedBy") or []
                claims = (", ".join(caused[:6]) if caused
                          else ", ".join(r["declarations"][:6])
                          or "a declaration")
                print("         -> band improved by a DECLARATION: " + claims)
        print("  " + "-" * 106)
        chans = "+".join(inputs["channels"])
        live = sum(1 for r in self.rows if not r["na"])
        unrated = getattr(self, "unrated", "")
        print("  weighted %s over %d/%d graded   overall %s%s   [%s]"
              % ("--" if unrated else ("%.1f" % w), live, len(self.rows),
                 "UNRATED" if unrated else overall,
                 ("   GATES FAILED: " + ", ".join(gates_failed)) if gates_failed else "",
                 chans))
        if unrated:
            print("  " + unrated)
        print()


# =============================================================================
# the shared context, and the four families
# =============================================================================

class Ctx(object):
    """One context object, built once, handed to all twenty-four criteria.

    Every attribute any of the four modules reads is set here, so a module can
    never quietly fall back to a default the report does not print.
    `copy_with` exists for one thing only: crit_motion's C11 unpacks
    ctx.strobe as four values and crit_structure's C19 needs the fifth, the
    PRE-shutter-exclusion fast set, because blur coverage computed over a set
    the covered frames were already removed from reports 0 % by construction."""

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def copy_with(self, **kw):
        d = dict(self.__dict__)
        d.update(kw)
        return Ctx(**d)


def build_context(src, px, audio, manifest, cuts, beats, v, declared,
                  render, src_basis):
    """The shared context canon's twenty-four criteria are measured against.

    The strobe scan runs ONCE and is handed to both C11 and C19 so the two rows
    cannot disagree about which frames are fast, and the hero move per beat is
    resolved ONCE so C2, C9, C10, C18 and C21 grade the same element."""
    fitted = src_basis == "pixel-fit"
    heroes = hero_moves(src, beats, px) if src is not None else []
    # ONE scan, and it is the corrected one. crit_motion's owns the two
    # definition fixes canon 1.9 and canon 5 ask for: a declared shutter range
    # DOUBLES the tolerated per-frame travel rather than exempting the frames,
    # and a strobing run whose own total travel crosses half the frame is a
    # whip, a wipe or a card flying through and is a transition by class.
    # `fast` is the same scan with the shutter declaration removed, which is
    # what C19 has to measure blur coverage over: coverage computed over a set
    # the covered frames were already taken out of reports 0 % by construction.
    import crit_motion
    bare = dict(manifest or {})
    bare.pop("shutterFrames", None)
    travel, strobe, moving, thr = crit_motion.strobe_scan(px, cuts, manifest,
                                                          v["fps"], DEC_W)
    fast = crit_motion.strobe_scan(px, cuts, bare, v["fps"], DEC_W)[1]
    ctx = Ctx(
        # identity of the delivered file
        fps=float(v["fps"]), frames=int(px.n), n_frames=int(px.n),
        width=int(v["width"]), height=int(v["height"]),
        render=render, video=v, declared=declared,
        # channels
        px=px, src=src, audio=audio, src_basis=src_basis, fitted=fitted,
        dec_w=DEC_W, dec_h=DEC_H,
        # the edit
        manifest=manifest, cuts=list(cuts), beats=list(beats),
        register=(src.register if src is not None
                  else manifest.get("register", DEFAULT_REGISTER)),
        genre=manifest.get("genre", DEFAULT_GENRE),
        delivery=manifest.get("delivery"),
        # shared derived measurements
        heroes=heroes,
        strobe=(travel, strobe, moving, thr, fast),
        cache={},
    )
    # canon 5, applied ONCE so C11 and C19 cannot disagree: "Transitions are
    # exempt from the 1/3 travel rule BY CLASS. Whip pans, full-frame wipes,
    # cards flying through frame and infinite zooms cross the whole frame in a
    # straight line at one acceleration, and should." Their leading edge is
    # fast because that is what they are, and at the pixel level a circle wipe
    # growing over the frame is indistinguishable from the content behind it
    # moving: what an edge tracker follows there is the occlusion boundary. The
    # class comes from the source channel, which is the only one that can see
    # it, and it is crit_motion's own compound classification so the two rows
    # read one definition.
    transit = transition_frames(ctx)
    if transit:
        ctx.strobe = (travel,
                      {f: v for f, v in strobe.items() if f not in transit},
                      moving, thr,
                      {f: v for f, v in fast.items() if f not in transit})
    return ctx


def transition_frames(ctx):
    """Frames covered by a move that is a transition by class: a declared
    impact, a travel across half the frame, or a scale change of 1.0 or more."""
    src = getattr(ctx, "src", None)
    if src is None:
        return set()
    out = set()
    try:
        import crit_motion
        cms = crit_motion.compound_moves(ctx)
    except Exception:
        cms = None
    if cms:
        for cm in cms:
            if cm.get("transition"):
                out.update(range(int(cm["onsetF"]), int(cm["endF"]) + 1))
        return out
    W, H = float(src.W), float(src.H)
    for m in src.moves:
        if m.get("impact") or abs(m.get("dx", 0.0)) >= 0.5 * W                 or abs(m.get("dy", 0.0)) >= 0.5 * H                 or m.get("scaleDelta", 0.0) >= 1.0:
            out.update(range(int(m["onsetF"]), int(m["endF"]) + 1))
    return out


def evaluate(ctx):
    """Run all twenty-four criteria and return a Grade.

    A family is imported, not inlined, and its rows are normalised against
    canon on the way in. A missing or duplicated id is a hard error: a rubric
    that silently drops a criterion grades a different film every run."""
    import crit_motion
    import crit_composition
    import crit_legibility
    import crit_structure

    if ctx.src is not None:
        ctx.src.apply_manifest(ctx.manifest)
    rows = []
    # crit_motion's C11 unpacks ctx.strobe as (travel, strobe, moving, thr)
    rows += crit_motion.all_criteria(ctx.copy_with(strobe=ctx.strobe[:4]))
    rows += crit_composition.run_all(ctx)
    rows += crit_legibility.evaluate(ctx)
    rows += crit_structure.evaluate(ctx)          # reads the five-tuple

    seen = [r["id"] for r in rows]
    dupes = sorted(set(c for c in seen if seen.count(c) > 1))
    missing = [c for c in ORDER if c not in seen]
    extra = [c for c in seen if c not in CANON_WEIGHTS]
    if dupes or missing or extra:
        raise SystemExit("grade-mg: criterion set is wrong -- duplicated %s, "
                         "missing %s, unknown %s" % (dupes, missing, extra))
    g = Grade()
    for cid in ORDER:
        g.add_row(next(r for r in rows if r["id"] == cid))
    return g


CRITERION_MODULE = {
    "C1": "crit_motion", "C2": "crit_motion", "C6": "crit_motion",
    "C10": "crit_motion", "C11": "crit_motion", "C21": "crit_motion",
    "C3": "crit_composition", "C7": "crit_composition", "C8": "crit_composition",
    "C9": "crit_composition", "C22": "crit_composition",
    "C24": "crit_composition",
    "C12": "crit_legibility", "C13": "crit_legibility", "C14": "crit_legibility",
    "C15": "crit_legibility", "C16": "crit_legibility", "C20": "crit_legibility",
    "C4": "crit_structure", "C5": "crit_structure", "C17": "crit_structure",
    "C18": "crit_structure", "C18D": "crit_structure", "C19": "crit_structure",
    "C23": "crit_structure", "C23D": "crit_structure",
}
CRITERION_FN = {
    "C1": "c1_ease_discipline", "C2": "c2_ease_vocabulary",
    "C6": "c6_settle_quality", "C10": "c10_timing_contrast",
    "C11": "c11_distance_duration", "C21": "c21_restraint",
    "C3": "c3_simultaneity", "C7": "c7_arcs", "C8": "c8_secondary",
    "C9": "c9_anticipation", "C22": "c22_framing", "C24": "c24_eye_trace",
    "C12": "c12_type_hierarchy", "C13": "c13_contrast",
    "C14": "c14_safe_margins", "C15": "c15_readability", "C16": "c16_palette",
    "C20": "c20_flash", "C4": "c4_hold_ratio", "C5": "c5_frame_integrity",
    "C17": "c17_transition_design", "C18": "c18_audio_sync",
    "C18D": "c18d_audio_delivery", "C19": "c19_reveal_craft",
    "C23": "c23_encode_qc", "C23D": "c23d_duration",
}


def evaluate_one(ctx, cid):
    """Run ONE criterion. The declaration budget needs a criterion re-measured
    with a single key removed, and re-running all twenty-four for each of eight
    keys is a minute of work to attribute one line of the report."""
    import importlib
    mod = importlib.import_module(CRITERION_MODULE[cid])
    fn = getattr(mod, CRITERION_FN[cid], None)
    if fn is None:
        return None
    if ctx.src is not None:
        ctx.src.apply_manifest(ctx.manifest)
    sub = ctx.copy_with(strobe=ctx.strobe[:4]) if CRITERION_MODULE[cid] == "crit_motion" else ctx
    try:
        return fn(sub)
    except Exception:
        return None


def declaration_budget(ctx, g):
    """Canon 7: the report prints the number of declarations and the number of
    criteria whose band improved because of one.

    The second number is MEASURED. Every criterion is re-run with the
    relief-granting keys removed and the two band tables are compared. Keys
    that describe the piece rather than relieving it -- cuts, register, genre,
    delivery, palette, typeScale, socialSafe -- are not stripped: declaring
    broadcast delivery makes C14 stricter and declaring a palette is what makes
    C16 gradeable at all, so neither can buy a pass."""
    bare = strip_exemptions(ctx.manifest)
    bare_ctx = ctx.copy_with(manifest=bare, cache={})
    g_bare = evaluate(bare_ctx)
    if ctx.src is not None:
        ctx.src.apply_manifest(ctx.manifest)

    a, b = g.by_id(), g_bare.by_id()
    improved = [k for k in ORDER
                if k in a and k in b and band_better(a[k]["band"], b[k]["band"])]
    # An N/A that replaces a C is also a pass bought by a declaration: the row
    # stops being graded at all rather than getting better.
    improved += [k for k in ORDER
                 if k in a and k in b and a[k]["na"] and not b[k]["na"]
                 and b[k]["band"] == "C" and k not in improved]
    # WHICH key bought it, measured rather than listed. The row used to print
    # the claims the criterion consumed, which includes descriptive keys that
    # `strip_exemptions` never removes and so cannot have moved anything: a
    # contrast row printed "delivery, fullBleed" when neither is stripped. Each
    # improved row is now re-run once per relief key the manifest carries, with
    # that key alone removed, and only the keys whose removal actually reverts
    # the band are named.
    present = [k for k in EXEMPTION_KEYS if ctx.manifest.get(k)]
    caused = {}
    for cid in improved:
        hits = []
        for key in present:
            one = dict(ctx.manifest)
            one.pop(key, None)
            row = evaluate_one(ctx.copy_with(manifest=one, cache={}), cid)
            if row is None:
                continue
            if band_better(a[cid]["band"], row["band"]) or \
                    (a[cid]["na"] and not row["na"] and row["band"] == "C"):
                hits.append(key)
        caused[cid] = hits
    if ctx.src is not None:
        ctx.src.apply_manifest(ctx.manifest)
    for r in g.rows:
        if r["id"] in caused:
            r["causedBy"] = caused[r["id"]]
    consumed = sorted(set(d for r in g.rows for d in r["declarations"]))
    n_decl = count_declarations(ctx.manifest)
    flag = ""
    if len(improved) > DECLARATION_FLAG_IMPROVED:
        flag = ("FLAG: %d criteria pass only because of a declaration. "
                "A declaration is a claim about intent and should be read as one."
                % len(improved))
    return {"declarations": n_decl, "consumed": len(consumed),
            "causedBy": caused,
            "consumedClaims": consumed,
            "reliefKeys": [k for k in EXEMPTION_KEYS if ctx.manifest.get(k)],
            "improved": len(improved),
            "improvedIds": sorted(improved, key=ORDER.index),
            "flag": flag}


# =============================================================================
# main
# =============================================================================

def main():
    ap = argparse.ArgumentParser(description="grade a motion graphic against the canon")
    ap.add_argument("render")
    ap.add_argument("--composition",
                    help="composition dir or index.html (enables the source channel)")
    ap.add_argument("--manifest", help="grade.json; defaults to <composition>/grade.json")
    ap.add_argument("--target", default="A", choices=BAND_ORDER)
    ap.add_argument("--out", help="grade-report.json path")
    ap.add_argument("--probe-out", help="where to write tracks.json / tweens.json")
    ap.add_argument("--no-probe", action="store_true", help="pixel channel only")
    ap.add_argument("--reuse-probe", action="store_true",
                    help="read tracks.json / tweens.json from the probe dir "
                         "instead of re-running probe-source.mjs")
    args = ap.parse_args()

    if not os.path.exists(args.render):
        raise SystemExit("grade-mg: no such render: " + args.render)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    v = ffprobe_video(args.render)
    fps, n_frames = v["fps"], v["frames"]
    print("\n  %s  %dx%d  %g fps  %d frames  %.3fs"
          % (os.path.basename(args.render), v["width"], v["height"], fps,
             n_frames, n_frames / fps))

    entry = composition_entry(args.composition) if args.composition else None
    declared = read_declared(entry)

    manifest = {}
    mpath = args.manifest
    if not mpath and args.composition:
        cand = os.path.join(args.composition if os.path.isdir(args.composition)
                            else os.path.dirname(args.composition), "grade.json")
        if os.path.exists(cand):
            mpath = cand
    if mpath and os.path.exists(mpath):
        manifest = json.load(io.open(mpath, encoding="utf-8"))
        print("  manifest " + mpath)
    for key, allowed in (("register", REGISTERS), ("genre", GENRES),
                         ("delivery", DELIVERIES)):
        if manifest.get(key) is not None and manifest[key] not in allowed:
            raise SystemExit("grade-mg: manifest %s must be one of %s" % (key, allowed))

    channels = ["pixel"]
    src, src_basis = None, None
    if entry and not args.no_probe:
        out_dir = args.probe_out or os.path.join(
            args.composition if os.path.isdir(args.composition) else os.path.dirname(entry),
            ".probe")
        got = (read_probe(out_dir) if args.reuse_probe
               else run_probe(args.composition, fps, out_dir))
        if got:
            src = Source(got[0], got[1], fps, manifest)
            src_basis = "source"
            channels.insert(0, "source")
        else:
            sys.stderr.write("grade-mg: source channel unavailable, C7, C8, C9, C15, "
                             "C19 and C22 degrade or go N/A\n")

    px = Pixel(args.render, fps, n_frames, v["width"], v["height"])
    if src is None:
        src = PixelSource(px, manifest)
        src_basis = "pixel-fit"
        channels.insert(0, "pixel-fit")
    audio = Audio(args.render, fps, manifest)
    if audio.present:
        channels.append("audio")
    cuts, cut_basis = detect_cuts(px, manifest, src if src_basis == "source" else None)
    beats = beats_from_cuts(cuts, px.n, px)
    recon = reconcile_cuts(cuts, src, fps) if src_basis == "source" else None
    print("  %d cuts (%s), %d beats, %s+pixel channel%s%s"
          % (len(cuts), cut_basis, len(beats), src_basis,
             (", %d audio hits" % len(audio.hits)) if audio.present else ", silent",
             ("   %.0f BPM grid on %.0f%% of onsets"
              % (audio.grid["bpm"], 100 * audio.grid["onsetShare"]))
             if audio.present and audio.grid else ""))
    if recon:
        print("  cut reconciliation: %d/%d clip starts matched, %d detected cuts "
              "with no clip%s"
              % (recon["matched"], recon["clipStarts"], len(recon["extraCuts"]),
                 (" at %s" % recon["extraCuts"][:8]) if recon["extraCuts"] else ""))

    ctx = build_context(src, px, audio, manifest, cuts, beats, v, declared,
                        args.render, src_basis)
    g = evaluate(ctx)
    budget = declaration_budget(ctx, g)
    overall, w, gates_failed = g.aggregate()

    inputs = {"render": os.path.abspath(args.render),
              "composition": (os.path.abspath(args.composition)
                              if args.composition else None),
              "manifest": (os.path.abspath(mpath) if mpath else None),
              "fps": fps, "frames": n_frames, "width": v["width"], "height": v["height"],
              "channels": channels, "cuts": cuts, "cutBasis": cut_basis,
              "beats": len(beats), "cutReconciliation": recon,
              "pixFmt": v.get("pix_fmt"),
              "register": ctx.register, "genre": ctx.genre,
              "delivery": manifest.get("delivery")}
    g.report(overall, w, gates_failed, inputs, budget)

    report = {
        "overall": {"band": overall,
                    "weighted": (None if getattr(g, "unrated", "") else round(w, 1)),
                    "unrated": getattr(g, "unrated", ""),
                    "graded": sum(1 for r in g.rows if not r["na"]),
                    "criteria": len(g.rows),
                    "gatesFailed": gates_failed,
                    "cCount": sum(1 for r in g.rows
                                  if not r["na"] and r["band"] == "C")},
        "declarationBudget": budget,
        "criteria": g.rows,
        "inputs": inputs,
    }
    out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.render)),
                                   "grade-report.json")
    with io.open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    print("  wrote " + out)
    ok = BAND_ORDER.index(overall) <= BAND_ORDER.index(args.target)
    if not ok:
        print("  FAIL: overall %s is below the --target %s\n" % (overall, args.target))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
