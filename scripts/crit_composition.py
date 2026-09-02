#!/usr/bin/env python3
"""crit_composition.py -- the COMPOSITION family of the motion-graphics rubric:
C3 simultaneity, C7 arcs, C8 secondary motion, C9 anticipation, C22 framing and
C24 eye-trace.

The specification is canon.md section 7 (the twenty-four-criterion table), with
section 1.3, 1.7, 1.8, 1.2, 2.1, 2.3 and 5 for the definitions and section 8 for
the calibrated amateur tells. grading-rubric.md supplies only the measurement
machinery canon does not restate: the two channels, the shared definitions of
move / onset / settle / progress curve, and the manifest shape.

Every function has the same signature and returns the same dict, so the
integrator can call them in a loop:

    row = c3_simultaneity(ctx)
    # {"id","name","band","weight","na","measured","worstFrames",
    #  "basis","note","declarations"}

`band` is one of "S" / "A" / "B" / "C", or None when `na` is True.
`declarations` names the manifest keys this row actually consumed, so the
report can print the declaration budget per criterion rather than only in
aggregate.


THE CONTEXT OBJECT
------------------
`ctx` is built by the integrator. Attribute access is preferred; a plain dict
with the same keys also works. Everything below is read, nothing is written.

  ctx.src         The SOURCE channel, already resolved: a Source when
                  probe-source.mjs ran, a PixelSource fitted from tracked
                  components when it did not, or None when neither exists.
                  Used through: .moves, .elements, .fps, .W, .H, .diag,
                  .frames, .register, .manifest, .clips, .num, .pi,
                  .prop(el, name), .box_at(el, f),
                  .is_named(el, names), .text_elements(),
                  .settled_window(el, cuts), .s_at(mv, f), .still_delta().
  ctx.src_basis   "source" | "pixel-fit" | None. Only used for the note; the
                  fitted channel says so in every row it touches.
  ctx.px          The PIXEL channel (grade-mg.py's Pixel), decoded at
                  DEC_W x DEC_H. Used through: .n, .fps, .grey, .ground,
                  .mask, .ink_frac, .frame_delta, .centroid, .comps, .tracks.
                  May be None; the rows that need it then go N/A.
  ctx.manifest    grade.json as a dict.
  ctx.fps         Delivered frame rate (float).
  ctx.frames      Delivered frame count (int).
  ctx.width       Delivered pixel width, ctx.height the delivered height.
  ctx.beats       [(firstFrame, lastFrame)] content runs, from beats_from_cuts.
  ctx.cuts        [int] cut frames, from detect_cuts.
  ctx.audio       grade-mg.py's Audio, or None. Used through .present, .hits
                  (seconds), .grid.
  ctx.heroes      The hero move list (hero_moves(src, beats, px)) or None; when
                  None and a hero list is needed the row falls back to the
                  largest-travel move per beat and says so.
  ctx.register    "premium" | "corporate" | "playful" | "energetic".
  ctx.genre       "continuous-camera" | "mixed" | "card-based".
  ctx.delivery    "broadcast" | "web" | "social" | None.
  ctx.dec_w       Pixel-channel decode width (default 640), ctx.dec_h (360).

A move dict is grade-mg.py's, unchanged: el, key, clip, start, dur, startF,
endF, durF, onsetF, settleF, props, spatial, paint, kind, ease, easeSamples,
samples, curveBasis, class, role, family, repeat, startAt, to, mechanical,
organic, impact, ambient, dx, dy, dist, scaleFrom, scaleTo, scaleDelta,
opFrom, opTo, cxFrom, cyFrom, cxTo, cyTo, boxW, boxH.


MEASUREMENT CAUTIONS carried from grade-mg.py's docstring, all of which bite
in this family:
  - decoding a RANGE gives (n, H, W, 3); reduce over axis 3, never axis 2
  - clip windows are [start, start + duration); bias both ends inward
  - smooth an ink count before looking for reversals, grain manufactures them
  - never measure motion on a bounding box, use the ink COUNT integral
  - exempt by NAME through the manifest, never by loosening a threshold
  - worstFrames is ranked by SEVERITY, never by frame number


WHAT CHANGED, AND WHY
---------------------
C3   The C band no longer fires on concurrency. Canon's C band is exactly
     "undeclared same-frame start of unrelated elements"; the old rubric also
     charged conc_max > 0.75, and conc_max is 1.0 on every hard-cut card film
     ever measured here because a card's elements are all in flight during the
     card's entrance, which canon 1.3 calls correct. Concurrency now gates S
     and A only, and is counted over ARRIVALS (a motivated same-frame cluster,
     a declared lockup, a detected cascade) rather than over tweens, so a
     six-item stagger reads as one thing moving, which is what it is.
     Motivation is applied per CLUSTER, not per beat: the old code exempted a
     beat only when SI was exactly 1.0, so a card that arrives as one composed
     unit plus one late accent scored 0.833 and failed.
C7   Arc depth is a fraction of the CHORD, not of frame height (canon 1.7:
     "15 px of sagitta is a deliberate arc on a 200 px move and invisible on a
     1600 px move"). The criterion is N/A unless organic elements are declared,
     its C band is jitter faults, and its reporting job is inverted: an arc on
     type or a card is an amateur tell (canon section 8 item 10) and is
     reported as one.
C8   The unit is the declared PAIR, not the parent move, so a parent with ten
     moves and one reacting child no longer scores 0.1. Both canonical forms
     are accepted and named: secondary action (1-3 frames later, 30-50 % of the
     primary, a different ease family) and follow-through (50-150 ms behind,
     same direction, decaying). lockedRate is reported and never banded.
C9   Three fixes. Qualification is the declared impact verb, not hero status,
     so an impact that is not its beat's largest element is still graded. The
     wind-up detector reads the move's OWN progress curve going negative, which
     is the professional form canon 1.2 prescribes ("one curve, not two
     tweens") and which the old two-tween-only detector could not see. And
     moves whose 10 % counter-travel would be under about 12 px at 1080p are
     excluded, because canon 1.2 says percentage rules stop working there and
     the correct authoring choice is to omit the prep. The corporate and
     premium ceiling now BANDS: anticipation on more than 30 % of hero moves is
     amateur tell 11, and a ceiling that cannot fail is decorative.
C22  New. Alignment positions on the best-fitting anchor per axis, counted
     over composed BLOCKS inside their own clip windows; margin drift within
     one margin on an anchored axis; focal-point count by visual weight (area x
     contrast, canon 2.3); and optical versus geometric centring as a report
     line.
C24  New, report-only. Attention is measured where it actually sits - the
     centroid of the heaviest ink region on the frame before the cut and on the
     settled frame after it - not at a tween's endpoint.


ONE THING THIS MODULE DOES NOT INHERIT
--------------------------------------
`Source.group_of` in grade-mg.py falls back to the plain DOM parent when an
element has no tweened ancestor, which makes every sibling under one `.clip`
div a single element. C3 then goes N/A on `_controls/bad`, the negative control
built specifically so that "every element in a beat starts on the same frame".
`_group_key` here stops at the declared lockup and the tweened ancestor, which
is what canon and the rubric both say, and the per-letter cascade that fallback
was reaching for is handled by the cascade collapse instead - which needs
ordered onsets and one ease family and therefore cannot absorb a same-frame
start. Worth reconciling when the families are merged.
"""

import json
import math
import os
import sys

import numpy as np


# =============================================================================
# CONSTANTS.  Every threshold this family uses lives here and nowhere else.
# Names are C<criterion>_*, matching grade-mg.py's convention.
# =============================================================================

# ---- shared ----------------------------------------------------------------
DEC_W, DEC_H = 640, 360          # pixel-channel working size (grade-mg.py)
TRANSLATE_PROPS = {"x", "y", "xPercent", "yPercent", "translateX", "translateY"}
DEFAULT_REGISTER = "corporate"
SHAPE_RADIUS = 0.06              # C2's cluster radius, reused wherever this
                                 # family asks "is this the same curve"

# ---- C3 simultaneity (weight 2) --------------------------------------------
C3_MIN_ELEMENTS = 3              # the 1/3 rule applies "with 3+ animated elements"
C3_CLUSTER_FRAMES = 1            # onsets within +/- 1 frame are one cluster
C3_SHARED_EVENT_MS = 50          # a declared trigger group may start within this
C3_HIT_LOCK_MS = 40.0            # a declared on-beat cut is honoured only if a
                                 # measured audio onset sits this close to it
C3_CASCADE_MIN = 3               # this many ordered onsets is a stagger, and a
                                 # stagger is ONE thing moving (canon 1.3)
C3_CASCADE_MAX_STEP_MS = 500     # canon 2.2's UI stagger cap; a wider step is
                                 # two separate events, not one cascade
C3_CASCADE_SHAPE_RADIUS = SHAPE_RADIUS   # "one easing family across a stagger"
C3_MIN_GRADED_BEATS = 2          # a weight-2 band drawn from ONE observation
                                 # is a band awarded for measuring nothing. On
                                 # a 26-beat film built one card at a time, 25
                                 # beats fall under the three-group census and
                                 # the row used to carry weight 2 off the one
                                 # that did not, with an empty note. The same
                                 # discipline the strobe share already applies
                                 # to its own denominator.
C3_S_MAX, C3_S_CONC = 0.34, 0.34
C3_A_MAX, C3_A_CONC = 0.50, 0.50
C3_B_MAX = 0.75
# There is deliberately no C3_C_CONC. Canon's C band is "undeclared same-frame
# start of unrelated elements" and nothing else; concurrency gates S and A.

# ---- C7 arcs ----------------------------------------------------------------
# Depth is a fraction of the CHORD (canon 1.7), never of frame height.
C7_MIN_CHORD_DIAGONAL = 0.10     # shorter moves cannot show an arc at all
C7_MIN_SAGITTA_PX = 1.5          # absolute floor: below this it is quantisation
C7_MIN_FRAMES = 4                # a three-sample path has no shape
C7_CHORD_BAND = {                # register: (min depth, max depth) of the chord
    "premium": (0.03, 0.08),     # canon 1.7: 3-8 % corporate, 10-25 % organic
    "corporate": (0.03, 0.08),
    "playful": (0.10, 0.25),
    "energetic": (0.10, 0.25),
}
C7_ONE_SIDED = 0.80              # share of deviations on one side of the chord
C7_JITTER_MIN_CHORD = 0.03       # a wander this deep counts once it also wanders
C7_JITTER_SIGN_CHANGES = 3       # ... back and forth this many times
C7_S_RATE, C7_A_RATE, C7_B_RATE = 0.80, 0.60, 0.40
C7_MIN_QUALIFYING = 3
C7_SWOOP_CHORD = 0.03            # canon section 8 item 10's detector, on type
                                 # and cards. Reported, never banded.

# ---- C8 secondary motion ----------------------------------------------------
C8_LAG_FRAMES = (1, 3)           # canon 1.8 secondary action, at 30 fps
C8_FOLLOW_LAG_MS = (50.0, 150.0) # canon 1.5 follow-through child lag
C8_STOP_LAG_MS = (50.0, 200.0)
C8_AMP_RATIO = (0.30, 0.50)      # canon 1.8: secondary is 30-50 % of primary
C8_FOLLOW_AMP_RATIO = (0.05, 0.50)   # follow-through decays, so it may be small
C8_PARENT_MIN_TRAVEL = 0.02      # of frame diagonal; below this the parent has
                                 # not moved enough for anything to react to
C8_PAIR_CONFORM = 0.50           # a pair conforms when this share of its
                                 # parent's moves carry a reaction
C8_S_RATE, C8_A_RATE, C8_B_RATE = 1.0, 0.75, 0.50

# ---- C9 anticipation ---------------------------------------------------------
C9_GRADED_REGISTERS = ("playful", "energetic")   # corporate and premium: ceiling
C9_CEILING = 0.30                # canon section 8 item 11's over-animated tell
# There is deliberately no travel or scale qualifier here. Canon grades the
# DECLARED impact verb, and the old "1/3 of the frame or a 2x scale jump" gate
# is the same move C11 classes as a transition and forbids, which is the
# C9/C11 contradiction corrections.md item 217 names and resolves.
C9_SKIP_MS = 150.0               # micro-feedback needs no wind-up ...
C9_SKIP_TRAVEL = 0.10            # ... but only where it also travels this little
C9_WINDOW_MS = 300.0             # how far before the onset to look
C9_COUNTER_MAG = (0.08, 0.20)    # canon 1.2: net opposite / total travel
C9_COUNTER_MS = (100.0, 200.0)   # canon 1.2: 100-200 ms of prep
C9_COUNTER_FRAMES = (2, 6)       # canon 1.2: a run of 2-6 frames, at 30 fps
C9_MIN_COUNTER_PX = 12.0         # at 1080p. Canon 1.2: below about 12-15 px of
                                 # counter-travel the percentage rules stop
                                 # working and omitting the prep is correct.
C9_REF_HEIGHT = 1080.0
C9_EASE_NEGATIVE = 0.05          # the move's own curve dipping this far below 0
C9_EASE_NEGATIVE_MAX = 0.30      # ... and no further, or it is a second move
C9_EASE_WINDOW = 0.40            # the dip has to be in the first 40 % of the curve
C9_SCALE_DIP = 0.03
C9_BLANK_INK = 0.002             # a held blank gap before an off-frame hit is
                                 # the scene winding up (canon 1.2)
C9_BLANK_MIN_FRAMES = 2
C9_S_RATE, C9_A_RATE, C9_B_RATE = 0.80, 0.50, 0.25
C9_MIN_QUALIFYING = 3

# ---- C22 framing -------------------------------------------------------------
C22_ALIGN_TOL = 0.01             # fraction of the frame; edges within this align
C22_PIXEL_ALIGN_TOL = 0.02       # wider on the pixel fallback, where a box is
                                 # a tracked component and not a layout rect
C22_MIN_ELEMENTS = 3
C22_VISIBLE_OPACITY = 0.5
C22_WRAPPER_AREA = 0.60          # an element covering this much of the frame is
                                 # a wrapper or a ground plane, and its edges
                                 # are not an alignment position
C22_BLOCK_GAP_X = 0.06           # of frame width: boxes closer than this on one
C22_BLOCK_GAP_Y = 0.04           # of frame height: ... baseline or line grid are
                                 # ONE block. A headline split per word or per
                                 # letter is one alignment decision, not eight;
                                 # counting the spans reported a centred Swiss
                                 # film as having thirty alignment positions.
C22_BEAT_SAMPLES = 2             # two settled samples per beat, so a beat can
                                 # legitimately carry two focal points over time
                                 # while each frame carries one. Each is the
                                 # STILLEST frame of its half of the beat, not a
                                 # fixed fraction: framing is a property of a
                                 # composed frame, and a fixed fraction lands
                                 # mid-move on anything with a long entrance.
C22_S_MIN_POSITIONS, C22_S_POSITIONS = 2, 3      # canon C22 S: "two or three"
C22_A_POSITIONS, C22_B_POSITIONS = 4, 6
C22_S_ALIGNED, C22_A_ALIGNED, C22_C_ALIGNED = 0.90, 0.75, 0.50
C22_MARGIN_BAND = 0.25           # only elements anchored within this of an edge
                                 # are in the margin census
C22_S_MARGIN_DRIFT = 0.002       # of the frame: 4 px at 1920. Two cards whose
C22_A_MARGIN_DRIFT = 0.005       # left margin differs by more than this have a
C22_B_MARGIN_DRIFT = 0.010       # visible wobble, not an indent scale.
C22_MIN_MARGIN_SAMPLES = 3
C22_FOCAL_RATIO = 0.60           # a region at this share of the heaviest one is
                                 # a second focal point
C22_FOCAL_MERGE = 0.06           # of frame width; glyph components closer than
                                 # this are one region, not one focal point each
C22_FOCAL_MIN_WEIGHT = 0.02      # of the frame's total ink weight; below this a
                                 # region is trim, not a focal point
C22_S_ONE_FOCAL, C22_A_ONE_FOCAL = 1.00, 0.90    # share of settled frames
C22_C_FOCAL = 3
C22_C_FOCAL_SHARE = 0.25
C22_OPTICAL_RISE = (0.02, 0.05)  # optical centre sits this far above geometric

# ---- C24 eye-trace (report only) ---------------------------------------------
C24_COMFORT_DIAGONAL = 0.20      # canon 5: within roughly 15-20 % of the diagonal
C24_JUMP_DIAGONAL = 0.50
C24_FIND_FRAMES = 8              # a deliberate displacement gets 6-8 frames
C24_POST_SAMPLE = 0.75           # where in the incoming beat the subject settles
C24_DIR_FRAMES = 3               # frames either side of a cut for the direction
C24_DIR_MIN_STEP = 0.6           # px/frame at the decode size
C24_PARALLAX_MIN_STEP = 0.5      # px/frame at the decode size
C24_PARALLAX_MIN_FRAMES = 4
C24_PARALLAX_MIN_LAYERS = 2
C24_REVERSAL_DEG = 135.0

# ---- weights (canon section 7) ----------------------------------------------
WEIGHTS = {"C3": 2, "C7": 1, "C8": 1, "C9": 1, "C22": 1, "C24": 1}

NAMES = {
    "C3": "simultaneity",
    "C7": "arcs",
    "C8": "secondary motion",
    "C9": "anticipation",
    "C22": "framing",
    "C24": "eye-trace",
}

BASIS = {
    "C3": "canon 1.3 unmotivated simultaneity only; declared groups and lockups "
          "count as one element, declared audio hits exempt",
    "C7": "canon 1.7 arcs are for organic elements; depth as a fraction of the "
          "chord; section 8 item 10 swoop detector",
    "C8": "canon 1.8 declared pairs only; secondary action and follow-through "
          "distinguished; lockedRate reported not banded",
    "C9": "canon 1.2 anticipation as one curve; register-gated, with the "
          "section 8 item 11 over-animated ceiling",
    "C22": "canon 2.3 hierarchy by visual weight; C22 alignment, margins, focal "
           "points, optical centring",
    "C24": "canon 5 eye-trace across the cut, parallax ratios, screen direction",
}


# =============================================================================
# small helpers.  clamp, fscale, smooth_box and rank_worst are byte-equivalent
# to grade-mg.py's; the integrator may delete them here and import instead.
# =============================================================================

def _get(ctx, name, default=None):
    """Read a context field from either an object or a plain dict."""
    if ctx is None:
        return default
    if isinstance(ctx, dict):
        return ctx.get(name, default)
    return getattr(ctx, name, default)


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def fscale(frames_at_30, fps):
    """Every frame-count threshold in the rubric is quoted at the authoring fps,
    which the rubric fixes at 30. A 60 fps render doubles every run length."""
    return max(1, int(round(frames_at_30 * fps / 30.0)))


def smooth_box(a, w):
    """Box smoothing that keeps the ARRAY LENGTH, so an index into the smoothed
    series still means the same frame."""
    a = np.asarray(a, dtype=float)
    if w <= 1 or len(a) < w:
        return a
    lo = w // 2
    ap = np.pad(a, (lo, w - 1 - lo), mode="edge")
    return np.convolve(ap, np.ones(w) / w, mode="valid")


def rank_worst(pairs, n=6):
    """Frames worst-first. `pairs` is [(severity, frame)]; higher is worse."""
    out, seen = [], set()
    for _, f in sorted(pairs, key=lambda p: -float(p[0])):
        f = int(f)
        if f in seen:
            continue
        seen.add(f)
        out.append(f)
        if len(out) >= n:
            break
    return out


def _row(cid, measured, band, worst=None, note="", na=False, declarations=None):
    return {
        "id": cid,
        "name": NAMES[cid],
        "band": None if na else band,
        "weight": WEIGHTS[cid],
        "na": bool(na),
        "measured": measured,
        "worstFrames": [int(f) for f in dict.fromkeys(worst or [])][:6],
        "basis": BASIS[cid],
        "note": note,
        "declarations": sorted(set(declarations or [])),
    }


def _declared(manifest, *keys):
    """The subset of `keys` the manifest actually carries, for the row's
    declaration list. A key present but empty is not a claim."""
    out = []
    for k in keys:
        v = (manifest or {}).get(k)
        if v is None or v is False:
            continue
        if isinstance(v, (list, tuple, dict, str)) and len(v) == 0:
            continue
        out.append(k)
    return out


def _shape_key(mv):
    """(s at .25, .5, .75, peak overshoot) -- C2's shape vector, reused so this
    family's "same curve" test cannot disagree with C2's cluster count."""
    s = mv.get("samples")
    if s is None:
        s = mv.get("easeSamples")
    s = np.asarray(s, dtype=float)
    if s.size < 101:
        s = np.interp(np.linspace(0, 1, 101), np.linspace(0, 1, max(s.size, 2)),
                      s if s.size >= 2 else np.array([0.0, 1.0]))
    return np.array([s[25], s[50], s[75], max(0.0, float(s.max()) - 1.0)])


def _shape_dist(a, b):
    return float(np.linalg.norm(np.asarray(a) - np.asarray(b)))


def _fit_residual(xs, ys):
    """Max perpendicular deviation from the chord, the share of deviations on
    one side, the chord LENGTH, and the number of sign changes in the smoothed
    deviation series. Canon 1.7 wants depth as a fraction of the chord, so the
    chord length comes back with the deviation rather than being re-derived by
    every caller against a different denominator."""
    p = np.stack([np.asarray(xs, float), np.asarray(ys, float)], axis=1)
    if len(p) < 3:
        return 0.0, 1.0, 0.0, 0
    a, b = p[0], p[-1]
    v = b - a
    L = float(np.hypot(v[0], v[1]))
    if L < 1e-6:
        return 0.0, 1.0, 0.0, 0
    nvec = np.array([-v[1], v[0]]) / L
    dev = (p - a) @ nvec
    pos = float((dev > 0).sum())
    neg = float((dev < 0).sum())
    tot = max(pos + neg, 1.0)
    # smooth before counting sign changes: centroid grain manufactures them
    sm = smooth_box(dev, 3)
    sig = sm[np.abs(sm) > max(C7_MIN_SAGITTA_PX * 0.5, 1e-9)]
    changes = int((np.diff(np.sign(sig)) != 0).sum()) if len(sig) >= 2 else 0
    return float(np.abs(dev).max()), max(pos, neg) / tot, L, changes


def _travel_frac(mv, diag):
    """Travel as a fraction of the frame diagonal, counting a scale change as
    the movement of the element's own box edge, so a scaling parent and a
    translating child are comparable in one unit."""
    t = mv.get("dist", 0.0) / max(diag, 1.0)
    box = max(mv.get("boxW", 0.0) or 0.0, mv.get("boxH", 0.0) or 0.0)
    t += mv.get("scaleDelta", 0.0) * box / max(diag, 1.0)
    return t


C3_MIN_BEAT_FRAMES = 10          # at 30 fps, matching C4's own rapid-fire merge


def _merge_short_beats(beats, fps):
    """Beats long enough for a choreography to exist in them, merged forward."""
    want = max(1, int(round(C3_MIN_BEAT_FRAMES * fps / 30.0)))
    out = []
    for (a, b) in beats:
        if out and (out[-1][1] - out[-1][0] + 1) < want:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    while len(out) > 1 and (out[-1][1] - out[-1][0] + 1) < want:
        out[-2] = (out[-2][0], out[-1][1])
        out.pop()
    return out


def _group_key(src, el):
    """The element that stands for this one in the C3 onset census.

    Canon 1.3: "count one declared group or lockup as ONE element". That is a
    DECLARED lockup, or a `.clip` sub-group, and a sub-group is established by
    a tweened ancestor inside the clip - which is what probe-source.mjs's
    `element.group` already resolves.

    This does NOT fall back to the plain DOM parent. Four sibling headlines
    under one `.clip` div share a parent and are four elements; collapsing them
    makes every card in a card-based film one element, at which point C3 goes
    N/A on the amateur control that was built to fail it. A per-letter cascade
    under a wrapper is handled where it belongs, by the cascade collapse below,
    which requires ordered onsets and one ease family and therefore cannot
    absorb a same-frame start.


    Collapsing on the recorded `subGroup` instead was tried and REJECTED, and
    the reason is arithmetic rather than taste: the sub-group is also the
    denominator of the concurrency term, `conc = peak arrivals / groups in the
    beat`, so merging a line's words into one group takes the same beat from
    five groups to three and its concurrency from 0.60 to 0.75 without one
    frame of the film changing. It also swallows the cascade collapse, which
    needs the members to still be separate units when it runs. A grouping rule
    that moves a band by shrinking a denominator is not a measurement."""
    for i, group in enumerate((getattr(src, "manifest", {}) or {}).get("lockups", [])):
        try:
            if src.is_named(el, set(group)):
                return "lockup%d" % i
        except Exception:
            continue
    try:
        e = src.elements[el]
    except Exception:
        return "el%d" % el
    g = e.get("group")
    if g is not None and g >= 0 and g != el:
        return "el%d" % int(g)
    return "el%d" % el


def _heroes(ctx, src):
    """The hero list the integrator supplied, or a fallback of the
    largest-travel spatial move per beat. The fallback is named in the note
    wherever it is used, because a hero chosen by travel is exactly the
    displacement-ranked test canon 2.3 says fails a correct build."""
    heroes = _get(ctx, "heroes")
    if heroes:
        return list(heroes), False
    out = []
    for (a, b) in _get(ctx, "beats", []) or []:
        cand = [m for m in src.moves
                if a <= m["onsetF"] <= b and m["kind"] == "spatial"]
        if cand:
            out.append(max(cand, key=lambda m: m.get("dist", 0.0)))
    return out, True


# ---- pixel-channel regions --------------------------------------------------

def _regions(px, f, merge_px):
    """Connected ink components at frame `f`, merged into REGIONS by proximity,
    each carrying its visual weight = ink area x contrast (canon 2.3 ranks
    hierarchy by change in visual weight, roughly area x contrast).

    A headline is thirty glyph components and one focal point. Counting
    components would report thirty."""
    comps = px.comps[int(clamp(f, 0, px.n - 1))]
    if not comps:
        return []
    f = int(clamp(f, 0, px.n - 1))
    grey = px.grey[f].astype(np.float32)
    ground = float(px.ground[f])
    mask = px.mask[f]
    boxes, weights, cents, areas = [], [], [], []
    for (area, cx, cy, x0, y0, x1, y1) in comps:
        sub = grey[int(y0):int(y1) + 1, int(x0):int(x1) + 1]
        sm = mask[int(y0):int(y1) + 1, int(x0):int(x1) + 1]
        w = float(np.abs(sub[sm] - ground).sum()) if sm.any() else 0.0
        boxes.append([float(x0), float(y0), float(x1), float(y1)])
        weights.append(w)
        cents.append((float(cx), float(cy)))
        areas.append(float(area))
    n = len(boxes)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i in range(n):
        bi = boxes[i]
        for j in range(i + 1, n):
            bj = boxes[j]
            if (bi[0] - merge_px <= bj[2] and bj[0] - merge_px <= bi[2]
                    and bi[1] - merge_px <= bj[3] and bj[1] - merge_px <= bi[3]):
                ra, rb = find(i), find(j)
                if ra != rb:
                    parent[max(ra, rb)] = min(ra, rb)
    agg = {}
    for i in range(n):
        r = find(i)
        a = agg.get(r)
        if a is None:
            agg[r] = {"weight": weights[i], "area": areas[i],
                      "sx": cents[i][0] * areas[i], "sy": cents[i][1] * areas[i],
                      "box": list(boxes[i]), "parts": 1}
        else:
            a["weight"] += weights[i]
            a["area"] += areas[i]
            a["sx"] += cents[i][0] * areas[i]
            a["sy"] += cents[i][1] * areas[i]
            a["box"][0] = min(a["box"][0], boxes[i][0])
            a["box"][1] = min(a["box"][1], boxes[i][1])
            a["box"][2] = max(a["box"][2], boxes[i][2])
            a["box"][3] = max(a["box"][3], boxes[i][3])
            a["parts"] += 1
    out = []
    for a in agg.values():
        ar = max(a["area"], 1e-6)
        out.append({"weight": a["weight"], "area": a["area"],
                    "cx": a["sx"] / ar, "cy": a["sy"] / ar,
                    "box": a["box"], "parts": a["parts"]})
    out.sort(key=lambda r: -r["weight"])
    return out


def _focal_count(regions):
    """Regions heavy enough to compete for the eye. A trim rule at 1 % of the
    frame's ink weight is not a focal point however far it sits from the
    headline."""
    if not regions:
        return 0, 0.0
    total = sum(r["weight"] for r in regions) or 1.0
    top = regions[0]["weight"]
    n = sum(1 for r in regions
            if r["weight"] >= C22_FOCAL_RATIO * top
            and r["weight"] >= C22_FOCAL_MIN_WEIGHT * total)
    return max(n, 1), top / total


def _attention_point(px, f, merge_px):
    """Where the eye is on frame `f`: the centroid of the heaviest ink region,
    in decode pixels. None on a blank frame."""
    regs = _regions(px, f, merge_px)
    if not regs:
        return None
    return (regs[0]["cx"], regs[0]["cy"])


# =============================================================================
# C3  SIMULTANEITY                                                   weight 2
# =============================================================================
#
# WHAT IT MEASURES NOW.  Per beat with at least three animated element groups:
# the largest UNMOTIVATED same-frame onset cluster as a share of the beat's
# groups (SI), and the largest number of independent ARRIVALS in flight at one
# moment as a share of those groups (conc). A declared lockup, a declared
# trigger group whose members start within 50 ms, and a detected cascade (three
# or more ordered onsets sharing one ease family) each count as ONE element.
# A same-frame cluster sitting on a declared on-beat hard cut is motivated, and
# where the film has audio the declaration is checked against a measured onset
# before it is honoured.
#
# S  SI_max <= 0.34 and conc_max <= 0.34
# C  SI_max > 0.75, or any beat where every one of three or more unrelated
#    element groups starts on one frame with no declaration behind it.
#
# STILL SCORES C ON:  the PowerPoint open. Four headlines as siblings under one
# clip, no lockup, no trigger group, no onBeatHardCuts entry, every tween at
# f(0) -- which is _controls/bad's clip A exactly, and its clip B again at f120.

def _cascade_units(units, fps):
    """Collapse ordered onset runs that share one ease family into single
    units. Canon 1.3: "a six-item stagger has all six active" and that is
    correct practice, so a stagger is one thing moving, not six."""
    max_step = max(1, int(round(C3_CASCADE_MAX_STEP_MS / 1000.0 * fps)))
    order = sorted(range(len(units)), key=lambda i: units[i]["onset"])
    merged, i = [], 0
    while i < len(order):
        run = [order[i]]
        j = i + 1
        while j < len(order):
            prev, cur = units[run[-1]], units[order[j]]
            step = cur["onset"] - prev["onset"]
            if step < 1 or step > max_step:
                break
            if _shape_dist(prev["shape"], cur["shape"]) > C3_CASCADE_SHAPE_RADIUS:
                break
            run.append(order[j])
            j += 1
        if len(run) >= C3_CASCADE_MIN:
            members = [units[k] for k in run]
            merged.append({
                "onset": min(m["onset"] for m in members),
                "end": max(m["end"] for m in members),
                "shape": members[0]["shape"],
                "groups": sum(m["groups"] for m in members),
                "cascade": True,
            })
            i = j
        else:
            u = dict(units[run[0]])
            u["cascade"] = False
            merged.append(u)
            i += 1
    return merged


def c3_simultaneity(ctx):
    src = _get(ctx, "src")
    manifest = _get(ctx, "manifest", {}) or {}
    beats = _get(ctx, "beats", []) or []
    audio = _get(ctx, "audio")
    fitted = _get(ctx, "src_basis") == "pixel-fit"
    decls = _declared(manifest, "lockups", "triggerGroups", "onBeatHardCuts",
                      "mechanical")
    if src is None or not beats:
        return _row("C3", {"beats": len(beats)}, None, na=True,
                    note="no source channel and no fitted fallback: onsets "
                         "cannot be located",
                    declarations=decls)

    fps = float(src.fps)
    shared_frames = max(0, int(round(C3_SHARED_EVENT_MS / 1000.0 * fps)))
    on_beat = [int(c) for c in manifest.get("onBeatHardCuts", [])]
    lock_s = max(C3_HIT_LOCK_MS, 1000.0 / fps) / 1000.0
    trigger_groups = manifest.get("triggerGroups", []) or []

    have_audio = audio is not None and getattr(audio, "present", False)
    hits = list(getattr(audio, "hits", None) or []) if have_audio else []
    # NOT `onsets`: the per-beat loop below binds that name to a list of
    # frame numbers, and a closure captures the variable rather than the
    # value, so `motivated` would compare seconds against frames from the
    # second beat on and silently never fire.
    audio_onsets = list(getattr(audio, "onsets", None) or []) if have_audio else []

    def motivated(frame):
        """Canon 1.3: exempt same-frame starts on a declared audio hit, and
        count a grid landing together on the downbeat as professional.

        Two independent routes, reported separately so a reader can tell a
        claim from a measurement:
          declaration  the frame is inside a declared onBeatHardCuts entry
          audio        a measured onset sits inside the lock window

        The declaration IS re-verified, against the same track and the same
        window C17 uses. It was not, and the reason given was that the detector
        keeps only the strongest quartile of flux peaks so a real cut on a
        pad-led bed has no hit near it -- true of `audio.hits`, and not true of
        `audio.onsets`, the full onset track C17 already reads. Two criteria
        checking one claim by two different standards is how a manifest ends up
        describing a check that does not happen: one manifest in this corpus
        stated that "the declaration only rescues a cut that a measured audio
        ONSET actually falls within the C18 sync window of", which was true of
        C17 and false here. `onBeatHardCuts` is a claim about the EDIT and the
        AUDIO together and both halves are now measured, so a declared cut with
        no onset near it buys nothing."""
        for c in on_beat:
            if abs(frame - c) > C3_CLUSTER_FRAMES:
                continue
            # the claim is about the CUT, so the onset is looked for at the cut
            # and not at the cluster frame: a cluster that starts one frame
            # after its cut is 17 ms further from the hit at 60 fps, and
            # measuring from the wrong end of that failed a declaration the
            # audio supports. Same window C17 uses on the same claim.
            if audio_onsets and any(abs(t - c / fps) <= lock_s
                                    for t in audio_onsets):
                return "declaration"
        if hits and any(abs(t - frame / fps) <= lock_s for t in hits):
            return "audio"
        return None

    def trigger_key(el):
        for i, grp in enumerate(trigger_groups):
            names = grp.get("elements", grp) if isinstance(grp, dict) else grp
            try:
                if src.is_named(el, set(names)):
                    return "trig%d" % i
            except Exception:
                continue
        return None

    si_max, conc_max, n_bad, graded, skipped = 0.0, 0.0, 0, 0, 0
    worst, cascades = [], 0
    by_declaration, by_audio = 0, 0
    # A beat shorter than this is a transition, not a beat, and everything on
    # the outgoing card starting together in it is the card LEAVING. C4 already
    # merges the same units for the same reason -- "a cut list with five cuts
    # inside fourteen frames is a rapid-fire run, and asking a two-frame beat to
    # hold 30 % of its frames charges a professional flurry as a fault". Here it
    # was worse than a fault: a three-frame chromatic-split cut to black, which
    # the film's own manifest names as a device, reported six of eight element
    # groups starting on one frame and set the piece's SI at 0.75.
    beats = _merge_short_beats(beats, fps)
    for (a, b) in beats:
        in_beat = [m for m in src.moves
                   if not m.get("ambient") and not m.get("mechanical")
                   and not m.get("repeat")
                   and a <= m["startF"] <= b and m["kind"] != "other"]
        if not in_beat:
            continue
        # -- the census counts GROUPS, and each group's FIRST start in the beat.
        # Counting every tween lets a beat that also holds later, deliberately
        # staggered moves dilute a genuinely simultaneous open.
        first, rep, trig = {}, {}, {}
        for m in in_beat:
            k = _group_key(src, m["el"])
            if k not in first or m["startF"] < first[k]:
                first[k] = m["startF"]
                rep[k] = m
            elif m["settleF"] > rep[k]["settleF"]:
                rep[k] = dict(rep[k], settleF=m["settleF"])
            tg = trigger_key(m["el"])
            if tg is not None:
                trig.setdefault(k, tg)
        n_groups = len(first)
        if n_groups < C3_MIN_ELEMENTS:
            continue
        units = []
        for k, on in first.items():
            m = rep[k]
            units.append({"onset": int(on), "end": int(m["settleF"]),
                          "shape": _shape_key(m), "groups": 1, "key": k,
                          "trig": trig.get(k)})
        # A declared trigger group is one onset only when its members really do
        # start together: the rubric's allowance is "within 50 ms of each
        # other", so members spread wider than that stay separate elements and
        # the declaration buys nothing.
        by_trig = {}
        for u in units:
            if u["trig"] is not None:
                by_trig.setdefault(u["trig"], []).append(u)
        dropped = set()
        for tg, members in by_trig.items():
            members.sort(key=lambda u: u["onset"])
            keep = members[0]
            for u in members[1:]:
                if u["onset"] - keep["onset"] <= shared_frames:
                    keep["end"] = max(keep["end"], u["end"])
                    keep["groups"] += u["groups"]
                    # by identity: a unit carries a numpy shape vector, so `==`
                    # on the dict raises rather than comparing
                    dropped.add(id(u))
        if dropped:
            units = [u for u in units if id(u) not in dropped]
        before_cascade = len(units)
        units = _cascade_units(units, fps)
        cascades += sum(1 for u in units if u.get("cascade"))
        graded += 1

        # -- same-frame clusters over units; motivation applies per CLUSTER
        onsets = sorted(u["onset"] for u in units)
        clusters = []
        for o in onsets:
            members = [u for u in units if abs(u["onset"] - o) <= C3_CLUSTER_FRAMES]
            clusters.append((o, members))
        arrivals, seen = [], set()
        for o, members in sorted(clusters, key=lambda c: -len(c[1])):
            fresh = [u for u in members if id(u) not in seen]
            if not fresh:
                continue
            for u in fresh:
                seen.add(id(u))
            arrivals.append({
                "onset": min(u["onset"] for u in fresh),
                "end": max(u["end"] for u in fresh),
                "size": len(fresh),
                "motivated": motivated(o),
            })
        for x in arrivals:
            if x["size"] > 1 and x["motivated"] == "declaration":
                by_declaration += 1
            elif x["size"] > 1 and x["motivated"] == "audio":
                by_audio += 1
        unmot = [x for x in arrivals if not x["motivated"]]
        biggest = max((x["size"] for x in unmot), default=0)
        si = biggest / max(before_cascade, 1)
        if biggest <= 1:
            si = 0.0
        if not unmot:
            skipped += 1
        at = next((x["onset"] for x in unmot if x["size"] == biggest), a)
        if si > si_max:
            si_max = si
            worst.insert(0, (2.0 + si, at))
        if biggest >= C3_MIN_ELEMENTS and biggest >= before_cascade:
            n_bad += 1
            worst.append((3.0 + biggest, at))

        # -- concurrency over ARRIVALS, normalised by the group census. One
        # composed arrival of six elements is one thing in flight; six
        # independent arrivals overlapping are six.
        peak = 0
        for f in range(a, b + 1):
            peak = max(peak, sum(1 for x in arrivals
                                 if x["onset"] <= f <= max(x["end"], x["onset"])))
        conc = peak / max(n_groups, 1)
        if conc > conc_max:
            conc_max = conc
            if conc > C3_A_CONC:
                worst.append((1.0 + conc, a))

    if graded < C3_MIN_GRADED_BEATS:
        why = ("no beat carries %d or more animated element groups"
               % C3_MIN_ELEMENTS) if graded == 0 else (
            "only %d beat of %d carries %d or more animated element groups: one "
            "observation is not a measurement, and this row weighs 2"
            % (graded, len(beats), C3_MIN_ELEMENTS))
        return _row("C3", {"beatsGraded": graded, "beats": len(beats),
                           "SI_max": round(si_max, 3),
                           "conc_max": round(conc_max, 3)},
                    None, na=True, note=why, declarations=decls)

    if si_max <= C3_S_MAX and conc_max <= C3_S_CONC:
        band = "S"
    elif si_max <= C3_A_MAX and conc_max <= C3_A_CONC:
        band = "A"
    elif si_max <= C3_B_MAX:
        band = "B"
    else:
        band = "C"
    if n_bad:
        band = "C"

    note = ""
    if n_bad:
        note = ("%d beat(s) start every one of their element groups on one "
                "frame, with no lockup, trigger group or declared hit behind it"
                % n_bad)
    elif si_max > C3_A_MAX:
        note = ("largest undeclared same-frame start is %.0f%% of a beat's "
                "element groups" % (si_max * 100))
    elif conc_max > C3_A_CONC:
        note = ("%.0f%% of a beat's element groups are in flight as separate "
                "arrivals at once" % (conc_max * 100))
    if not note:
        # A band with no stated cause is a band the reader cannot act on. The
        # row used to print B with an empty note on a weight-2 criterion, so a
        # designer was handed a two-weight downgrade and no reason for it.
        note = ("largest undeclared same-frame start is %.0f%% of a beat's "
                "element groups and peak concurrency is %.0f%%, over %d graded "
                "beat(s) of %d" % (si_max * 100, conc_max * 100, graded,
                                   len(beats)))
    if fitted:
        note = (note + "; " if note else "") + \
            "reduced confidence: onsets fitted from tracked components"
    return _row("C3", {
        "SI_max": round(si_max, 3), "conc_max": round(conc_max, 3),
        "nBad": n_bad, "beatsGraded": graded, "allMotivated": skipped,
        "exemptByDeclaration": by_declaration, "exemptByAudio": by_audio,
        "cascades": cascades,
        "basis": "pixel-fit" if fitted else "source",
    }, band, rank_worst(worst), note, declarations=decls)


# =============================================================================
# C7  ARCS                                                           weight 1
# =============================================================================
#
# WHAT IT MEASURES NOW.  N/A unless the manifest declares organic elements, and
# then only those are graded. Arc depth is the maximum perpendicular deviation
# from the chord divided by the CHORD LENGTH (canon 1.7), never by frame
# height: 15 px of sagitta is a deliberate arc on a 200 px move and invisible
# on a 1600 px move. A designed arc is one-sided and inside the register's
# depth band; a path that wanders back and forth across its own chord is a
# jitter fault. Separately, and as a REPORT line in both the graded and the N/A
# case, unmotivated arcs on type and cards are counted at canon section 8 item
# 10's detector, one-sided deviation above 3 % of chord.
#
# S  arc rate >= 0.80 on declared organic moves, one-sided, no jitter
# C  any jitter fault, or arc rate 0 across three or more declared organic
#    moves (the author declared these elements organic and then travelled every
#    one of them in a straight line)
#
# STILL SCORES C ON:  a declared organic mover whose centroid path crosses its
# own chord three times with a deviation over 3 % of the chord -- the hand-keyed
# wander that a two-tween x/y pair produces when the curves are not in phase.

def _ancestor_shift(src, el, a, b):
    """The translation this element inherits from its ancestors over [a, b].

    Read from each ancestor's own TRANSFORM track, not from its rect: a
    parent's rect moves partly because this very child moved inside it, so
    subtracting the rect would subtract the move under test.

    Why it has to be subtracted at all: a masked word rising on yPercent inside
    a wrapper that is simultaneously whipped sideways travels a curved path ON
    SCREEN while its own tween is dead straight. C1 already projects onto the
    axis the tween drives for exactly this reason; the arc detector did not,
    and it named a straight one-tween masked rise as a film's worst
    unmotivated arc at 35% of its chord."""
    n = b - a + 1
    dx = np.zeros(n, dtype=float)
    dy = np.zeros(n, dtype=float)
    if n < 2:
        return dx, dy
    cur, seen = el, set()
    for _ in range(8):
        p = src.elements[cur].get("parent")
        if p is None or p < 0 or p == cur or p in seen:
            break
        seen.add(p)
        try:
            x = np.asarray(src.prop(p, "x")[a:b + 1], float)
            y = np.asarray(src.prop(p, "y")[a:b + 1], float)
            xp = np.asarray(src.prop(p, "xPercent")[a:b + 1], float)
            yp = np.asarray(src.prop(p, "yPercent")[a:b + 1], float)
            w = np.asarray(src.prop(p, "w")[a:b + 1], float)
            h = np.asarray(src.prop(p, "h")[a:b + 1], float)
        except (KeyError, IndexError):
            break
        if len(x) != n:
            break
        sx = x + xp / 100.0 * w
        sy = y + yp / 100.0 * h
        dx += sx - sx[0]
        dy += sy - sy[0]
        cur = p
    return dx, dy


def _path_of(src, m):
    """The move's on-screen path with inherited translation removed."""
    a = int(clamp(m["onsetF"], 0, src.frames - 1))
    b = int(clamp(m["settleF"], 0, src.frames - 1))
    if b <= a:
        return None, None
    cx = np.asarray(src.prop(m["el"], "cx")[a:b + 1], float)
    cy = np.asarray(src.prop(m["el"], "cy")[a:b + 1], float)
    dx, dy = _ancestor_shift(src, m["el"], a, b)
    return cx - dx, cy - dy


def _arc_scan(src, moves, register):
    lo, hi = C7_CHORD_BAND.get(register, C7_CHORD_BAND[DEFAULT_REGISTER])
    good, jitter, qual, worst, depths = 0, 0, 0, [], []
    for m in moves:
        if m["kind"] != "spatial" or not set(m.get("spatial", [])) & TRANSLATE_PROPS:
            continue
        a, b = int(m["onsetF"]), int(m["settleF"])
        if b - a + 1 < C7_MIN_FRAMES:
            continue
        a = int(clamp(a, 0, src.frames - 1))
        b = int(clamp(b, 0, src.frames - 1))
        if b <= a:
            continue
        cx, cy = _path_of(src, m)
        if cx is None:
            continue
        res, one, chord, changes = _fit_residual(cx, cy)
        # qualify on the MEASURED chord, not on the move's path length: a
        # deviation over a chord that is shorter than the path is the ratio
        # exploding, not an arc
        if chord < C7_MIN_CHORD_DIAGONAL * src.diag:
            continue
        qual += 1
        depth = res / chord
        depths.append(depth)
        if res < C7_MIN_SAGITTA_PX:
            # below the absolute floor the path is straight, whatever the ratio
            worst.append((abs(depth - (lo + hi) / 2), a))
            continue
        if depth >= C7_JITTER_MIN_CHORD and (one < C7_ONE_SIDED
                                             or changes >= C7_JITTER_SIGN_CHANGES):
            jitter += 1
            worst.append((10.0 + depth, a))
        elif lo <= depth <= hi and one >= C7_ONE_SIDED and changes <= 1:
            good += 1
        else:
            worst.append((abs(depth - (lo + hi) / 2), a))
    return good, jitter, qual, worst, depths


def _swoops(src, moves):
    """Canon section 8 item 10: one-sided perpendicular deviation above about
    3 % of the chord on a TEXT or CARD element. Reported, never banded, because
    canon's C7 row says report."""
    bad = []
    for m in moves:
        if m.get("organic") or m["kind"] != "spatial":
            continue
        if not set(m.get("spatial", [])) & TRANSLATE_PROPS:
            continue
        a, b = int(clamp(m["onsetF"], 0, src.frames - 1)), \
            int(clamp(m["settleF"], 0, src.frames - 1))
        if b - a + 1 < C7_MIN_FRAMES:
            continue
        cx, cy = _path_of(src, m)
        if cx is None:
            continue
        res, one, chord, changes = _fit_residual(cx, cy)
        if chord < C7_MIN_CHORD_DIAGONAL * src.diag or res < C7_MIN_SAGITTA_PX:
            continue
        depth = res / chord
        if depth >= C7_SWOOP_CHORD and one >= C7_ONE_SIDED \
                and changes < C7_JITTER_SIGN_CHANGES:
            bad.append((depth, a, m.get("key", "?")))
    bad.sort(key=lambda t: -t[0])
    return bad


def c7_arcs(ctx):
    src = _get(ctx, "src")
    manifest = _get(ctx, "manifest", {}) or {}
    register = _get(ctx, "register") or manifest.get("register", DEFAULT_REGISTER)
    organic = manifest.get("organic", []) or []
    decls = _declared(manifest, "organic", "mechanicalPiece", "register")

    if src is None or _get(ctx, "src_basis") != "source":
        # A tracked component's centroid path is not a move path: a merge, a
        # split or a track swap moves it further than the element ever went, so
        # deviation over chord is unbounded and every long path reads as an arc.
        # C7 is a source-channel criterion or it is nothing.
        return _row("C7", {"declaredOrganic": len(organic)}, None, na=True,
                    note="organic elements and their paths cannot be resolved "
                         "without the source channel", declarations=decls)

    graded_moves = [m for m in src.moves
                    if not m.get("repeat") and not m.get("ambient")]
    swoops = _swoops(src, graded_moves)
    non_organic = sum(1 for m in graded_moves
                      if not m.get("organic") and m["kind"] == "spatial"
                      and set(m.get("spatial", [])) & TRANSLATE_PROPS
                      and m.get("dist", 0.0) >= C7_MIN_CHORD_DIAGONAL * src.diag)
    swoop_note = ""
    if swoops:
        swoop_note = ("%d unmotivated arc(s) on type or cards, worst %s at "
                      "%.1f%% of its chord (canon section 8 item 10)"
                      % (len(swoops), swoops[0][2], swoops[0][0] * 100))
    swoop_measured = {
        "swoops": len(swoops),
        "swoopRate": round(len(swoops) / non_organic, 3) if non_organic else 0.0,
    }

    if manifest.get("mechanicalPiece") or not organic:
        reason = ("declared a mechanical piece (kinetic type / UI)"
                  if manifest.get("mechanicalPiece") else
                  "no organic elements declared: type, cards, panels and wipes "
                  "travel in straight lines by design")
        measured = dict(swoop_measured)
        measured["declaredOrganic"] = len(organic)
        return _row("C7", measured, None,
                    [s[1] for s in swoops[:3]],
                    reason + (("; " + swoop_note) if swoop_note else ""),
                    na=True, declarations=decls)

    organic_moves = [m for m in graded_moves if m.get("organic")]
    good, jitter, qual, worst, depths = _arc_scan(src, organic_moves, register)
    if qual < C7_MIN_QUALIFYING:
        measured = dict(swoop_measured)
        measured.update({"qualifying": qual, "declaredOrganic": len(organic)})
        return _row("C7", measured, None, [s[1] for s in swoops[:3]],
                    "fewer than %d declared organic moves travel %d%% of the "
                    "frame diagonal" % (C7_MIN_QUALIFYING,
                                        int(C7_MIN_CHORD_DIAGONAL * 100))
                    + (("; " + swoop_note) if swoop_note else ""),
                    na=True, declarations=decls)

    rate = good / qual
    if jitter:
        band = "C"
    elif rate >= C7_S_RATE:
        band = "S"
    elif rate >= C7_A_RATE:
        band = "A"
    elif rate >= C7_B_RATE:
        band = "B"
    elif rate > 0.0:
        band = "B"
    else:
        band = "C"

    if jitter:
        note = ("%d declared organic path(s) wander across their own chord: "
                "that is a jitter fault, not an arc" % jitter)
    elif rate == 0.0:
        note = ("%d declared organic move(s) all travel in straight lines; "
                "the declaration says they should arc" % qual)
    elif rate < C7_A_RATE:
        note = "%d/%d declared organic moves travel in straight lines" % (
            qual - good, qual)
    else:
        note = ""
    if swoop_note:
        note = (note + "; " if note else "") + swoop_note
    measured = dict(swoop_measured)
    measured.update({
        "arcRate": round(rate, 3), "qualifying": qual, "jitter": jitter,
        "medianDepth": round(float(np.median(depths)), 4) if depths else 0.0,
        "basis": "source",
    })
    return _row("C7", measured, band,
                rank_worst(worst) + [s[1] for s in swoops[:2]],
                note, declarations=decls)


# =============================================================================
# C8  SECONDARY MOTION                                               weight 1
# =============================================================================
#
# WHAT IT MEASURES NOW.  Declared secondaryPairs only, and the unit is the
# PAIR. For each declared parent element, its qualifying moves (spatial, over
# 2 % of the frame diagonal, not a loop); the pair conforms when at least half
# of them carry a reaction on the declared child, in either of the two forms
# canon 1.8 distinguishes:
#   secondary action  1-3 frames later, 30-50 % of the primary's travel, a
#                     different ease shape or a different property
#   follow-through    50-150 ms behind, same direction, stopping 50-200 ms
#                     after the parent, decaying
# lockedRate -- children that start on the parent's frame with the parent's
# curve -- is REPORTED and never banded: rigid parenting is correct for a
# lockup, because a wordmark and its symbol are one object.
#
# S  every declared pair conforms
# C  fewer than half of the declared pairs conform
#
# STILL SCORES C ON:  three declared parent/child pairs whose children have no
# tween at all, or whose children are rigidly parented so they start on the
# parent's frame with the parent's curve -- which is the null-and-parent
# workflow, and is a lock, not a reaction.

def _pair_reaction(src, parent, child_moves, diag, fps):
    """The kind of reaction `parent` gets from `child_moves`, or None."""
    lag_lo = fscale(C8_LAG_FRAMES[0], fps)
    lag_hi = fscale(C8_LAG_FRAMES[1], fps)
    p_amp = _travel_frac(parent, diag)
    if p_amp <= 1e-9:
        return None, False
    p_shape = _shape_key(parent)
    locked = False
    kind = None
    for m in child_moves:
        lag_f = m["onsetF"] - parent["onsetF"]
        lag_ms = lag_f / fps * 1000.0
        stop_ms = (m["settleF"] - parent["settleF"]) / fps * 1000.0
        amp = _travel_frac(m, diag) / p_amp
        same_curve = _shape_dist(_shape_key(m), p_shape) <= SHAPE_RADIUS
        if lag_f == 0 and same_curve:
            locked = True
            continue
        same_dir = (m.get("dx", 0.0) * parent.get("dx", 0.0)
                    + m.get("dy", 0.0) * parent.get("dy", 0.0)) > 0
        diff_prop = bool(set(m.get("props", [])) ^ set(parent.get("props", [])))
        if (lag_lo <= lag_f <= lag_hi
                and C8_AMP_RATIO[0] <= amp <= C8_AMP_RATIO[1]
                and (not same_curve or diff_prop)):
            kind = kind or "secondary"
        elif (C8_FOLLOW_LAG_MS[0] <= lag_ms <= C8_FOLLOW_LAG_MS[1]
                and C8_STOP_LAG_MS[0] <= stop_ms <= C8_STOP_LAG_MS[1]
                and same_dir
                and C8_FOLLOW_AMP_RATIO[0] <= amp <= C8_FOLLOW_AMP_RATIO[1]):
            kind = kind or "followThrough"
    return kind, locked


def c8_secondary(ctx):
    src = _get(ctx, "src")
    manifest = _get(ctx, "manifest", {}) or {}
    pairs = manifest.get("secondaryPairs", []) or []
    decls = _declared(manifest, "secondaryPairs")

    no_source = src is None or _get(ctx, "src_basis") != "source"
    if no_source:
        # The channel comes FIRST. Reporting "no secondaryPairs declared" on the
        # pixel-only path says that declaring a pair would enable the
        # measurement, and it would not: lead and follow both need the source
        # rect track, so the row is N/A whatever the manifest says.
        return _row("C8", {"declaredPairs": len(pairs)}, None, na=True,
                    note="lead and follow rects need the source channel",
                    declarations=decls)
    if not pairs:
        return _row("C8", {"declaredPairs": 0}, None, na=True,
                    note="no secondaryPairs declared", declarations=decls)

    resolved = []
    for p in pairs:
        if not isinstance(p, dict) or "parent" not in p or "child" not in p:
            continue
        par = [e["i"] for e in src.elements if src.is_named(e["i"], {p["parent"]})]
        chi = [e["i"] for e in src.elements if src.is_named(e["i"], {p["child"]})]
        for a in par:
            for b in chi:
                if a != b:
                    resolved.append((a, b, p))
    if not resolved:
        return _row("C8", {"declaredPairs": len(pairs)}, None, na=True,
                    note="declared secondaryPairs match no element in the "
                         "composition", declarations=decls)

    fps = float(src.fps)
    diag = src.diag
    conform, locked_pairs, live, worst = 0, 0, 0, []
    kinds = {"secondary": 0, "followThrough": 0}
    no_parent_move = 0
    for (pa, ch, _p) in resolved:
        parent_moves = [m for m in src.moves
                        if m["el"] == pa and m["kind"] == "spatial"
                        and not m.get("repeat")
                        and _travel_frac(m, diag) >= C8_PARENT_MIN_TRAVEL]
        if not parent_moves:
            no_parent_move += 1
            continue
        child_moves = [m for m in src.moves
                       if m["el"] == ch and m["kind"] != "other"
                       and not m.get("repeat")]
        live += 1
        hit, lock_hits = 0, 0
        for h in parent_moves:
            kind, locked = _pair_reaction(src, h, child_moves, diag, fps)
            if kind:
                hit += 1
                kinds[kind] += 1
            else:
                worst.append((1.0 + _travel_frac(h, diag), h["onsetF"]))
            if locked:
                lock_hits += 1
        if hit / len(parent_moves) >= C8_PAIR_CONFORM:
            conform += 1
        if lock_hits / len(parent_moves) >= C8_PAIR_CONFORM:
            locked_pairs += 1

    if live == 0:
        return _row("C8", {"declaredPairs": len(resolved),
                           "pairsWithNoParentMove": no_parent_move}, None,
                    na=True,
                    note="no declared parent element carries a move over %d%% "
                         "of the frame diagonal"
                         % int(C8_PARENT_MIN_TRAVEL * 100),
                    declarations=decls)

    rate = conform / live
    locked_rate = locked_pairs / live
    if rate >= C8_S_RATE:
        band = "S"
    elif rate >= C8_A_RATE:
        band = "A"
    elif rate >= C8_B_RATE:
        band = "B"
    else:
        band = "C"
    note = ""
    if conform < live:
        note = "%d/%d declared pairs have no conforming reaction" % (
            live - conform, live)
    if locked_rate > 0:
        note = (note + "; " if note else "") + \
            ("%.0f%% of declared pairs are rigidly locked to their parent "
             "(reported, not charged: a lockup moves as one object)"
             % (locked_rate * 100))
    return _row("C8", {
        "reactRate": round(rate, 3), "lockedRate": round(locked_rate, 3),
        "declaredPairs": len(resolved), "gradedPairs": live,
        "pairsWithNoParentMove": no_parent_move,
        "secondary": kinds["secondary"], "followThrough": kinds["followThrough"],
        "basis": "source",
    }, band, rank_worst(worst), note, declarations=decls)


# =============================================================================
# C9  ANTICIPATION                                                   weight 1
# =============================================================================
#
# WHAT IT MEASURES NOW.  Register-gated.
#   playful / energetic  graded on DECLARED impact verbs. Every move on a
#       declared impact element qualifies (not only the one that happens to be
#       its beat's hero), except moves whose 10 % counter-travel would be under
#       about 12 px at 1080p, where canon 1.2 says the percentage rules stop
#       working and omitting the prep is the correct authoring choice.
#   corporate / premium  N/A, but carrying a CEILING. Anticipation on more than
#       30 % of hero moves is amateur tell 11, so the ceiling bands C rather
#       than printing a note nothing reads.
# A wind-up is found in any of four forms: the move's own progress curve going
# negative early (canon 1.2, "one curve, not two tweens" -- the professional
# form, which a two-tween-only detector cannot see); a separate counter tween
# of 100-200 ms at 8-20 % of the travel; a scale dip resolving at the onset;
# and for an element entering from off frame, a held blank gap immediately
# before the hit, which is the only wind-up an off-frame element can have.
#
# S  anticRate >= 0.80 in a graded register
# C  anticRate 0 with three or more declared impact verbs, or -- in corporate
#    and premium -- a wind-up on more than 30 % of hero moves
#
# STILL SCORES C ON:  a playful piece declaring three impact elements whose
# slams each start from rest and run straight to target on a power4.out, with
# no counter tween, no scale dip and no negative-going curve. And, in the other
# direction, a premium piece that puts a back.in wind-up on five of its eight
# hero moves.

def _negative_curve_run(mv, fps):
    """Frames the move's own progress spends below zero at the head of the
    curve, and the depth of that excursion. Canon 1.2's professional form."""
    s = mv.get("samples")
    if s is None:
        s = mv.get("easeSamples")
    s = np.asarray(s, dtype=float)
    if s.size < 8:
        return 0, 0.0
    head = s[: max(3, int(round(len(s) * C9_EASE_WINDOW)))]
    if head.min() >= 0.0:
        return 0, 0.0
    neg = int((head < 0).sum())
    frames = neg / float(len(s)) * max(int(mv.get("durF", 1)), 1)
    return frames, float(-head.min())


def _has_windup(src, px, mv, win_frames, min_counter_px, fps):
    """(found, form). Four forms, in the order canon presents them."""
    a0 = max(0, int(mv["onsetF"]) - win_frames)
    onset = int(mv["onsetF"])

    # 1. the move's own curve goes negative early
    frames, depth = _negative_curve_run(mv, fps)
    if C9_EASE_NEGATIVE <= depth <= C9_EASE_NEGATIVE_MAX \
            and fscale(C9_COUNTER_FRAMES[0], fps) <= frames <= fscale(C9_COUNTER_FRAMES[1], fps):
        return True, "curve"

    # 2. a separate counter tween on the same element
    for m in src.moves:
        if m["el"] != mv["el"] or m is mv or m["kind"] != "spatial":
            continue
        if not (a0 <= m["onsetF"] < onset):
            continue
        ms = m.get("dur", 0.0) * 1000.0
        if not (C9_COUNTER_MS[0] <= ms <= C9_COUNTER_MS[1]):
            continue
        same_dir = (m.get("dx", 0.0) * mv.get("dx", 0.0)
                    + m.get("dy", 0.0) * mv.get("dy", 0.0)) > 0
        mag = m.get("dist", 0.0) / max(mv.get("dist", 0.0), 1e-6)
        if not same_dir and m.get("dist", 0.0) >= min_counter_px \
                and C9_COUNTER_MAG[0] <= mag <= C9_COUNTER_MAG[1]:
            return True, "counterTween"

    # 3. a scale dip resolving at the onset
    try:
        sc = src.prop(mv["el"], "scale")[a0:onset + 1]
    except Exception:
        sc = np.zeros(0)
    if len(sc) > 2 and float(sc.max()) > 1e-6:
        dip = (float(sc.max()) - float(sc.min())) / float(sc.max())
        if dip >= C9_SCALE_DIP and float(sc[-1]) <= float(sc.min()) * 1.01:
            return True, "scaleDip"

    # 4. an off-frame element cannot wind up, but the scene can: a held blank
    #    gap immediately before the hit (canon 1.2)
    off_frame = (mv.get("cxFrom", 0.0) < 0 or mv.get("cyFrom", 0.0) < 0
                 or mv.get("cxFrom", 0.0) > src.W or mv.get("cyFrom", 0.0) > src.H)
    if off_frame and px is not None:
        lo = int(clamp(onset - fscale(C9_BLANK_MIN_FRAMES, fps), 0, px.n - 1))
        hi = int(clamp(onset, 0, px.n - 1))
        if hi > lo and bool((px.ink_frac[lo:hi] < C9_BLANK_INK).all()):
            return True, "blankGap"
    return False, None


def c9_anticipation(ctx):
    src = _get(ctx, "src")
    px = _get(ctx, "px")
    manifest = _get(ctx, "manifest", {}) or {}
    fitted = _get(ctx, "src_basis") == "pixel-fit"
    decls = _declared(manifest, "impact", "register", "hero")
    if src is None:
        return _row("C9", {}, None, na=True,
                    note="qualifying moves need the source channel or a fitted "
                         "fallback", declarations=decls)

    register = _get(ctx, "register") or getattr(src, "register", DEFAULT_REGISTER)
    fps = float(src.fps)
    win = max(1, int(round(C9_WINDOW_MS / 1000.0 * fps)))
    min_counter_px = C9_MIN_COUNTER_PX * (src.H / C9_REF_HEIGHT)
    heroes, hero_fallback = _heroes(ctx, src)
    graded_register = register in C9_GRADED_REGISTERS

    fit_note = ("reduced confidence: moves fitted from tracked components, so "
                "only the curve and counter-tween tests run") if fitted else ""
    hero_note = ("hero moves fell back to largest travel per beat, which "
                 "canon 2.3 warns ranks hierarchy by the wrong quantity"
                 ) if hero_fallback else ""

    # ---- corporate and premium: the ceiling ---------------------------------
    if not graded_register:
        wound, worst = 0, []
        for h in heroes:
            ok, form = _has_windup(src, px, h, win, min_counter_px, fps)
            if ok:
                wound += 1
                worst.append((_travel_frac(h, src.diag) + 1.0, h["onsetF"]))
        share = wound / max(len(heroes), 1)
        measured = {"register": register, "heroMoves": len(heroes),
                    "windUps": wound, "windUpShare": round(share, 3),
                    "ceiling": C9_CEILING,
                    "basis": "pixel-fit" if fitted else "source"}
        if heroes and share > C9_CEILING:
            note = ("%.0f%% of hero moves carry a wind-up, over the %.0f%% "
                    "ceiling for a %s piece: that is the over-animated tell"
                    % (share * 100, C9_CEILING * 100, register))
            for extra in (hero_note, fit_note):
                if extra:
                    note += "; " + extra
            return _row("C9", measured, "C", rank_worst(worst), note,
                        declarations=decls)
        note = ("%s register: anticipation is N/A and graded as a ceiling only "
                "(canon: corporate anticipation is minimal by design)" % register)
        for extra in (hero_note, fit_note):
            if extra:
                note += "; " + extra
        return _row("C9", measured, None, [], note, na=True, declarations=decls)

    # ---- playful and energetic: declared impact verbs ------------------------
    impact_moves = [m for m in src.moves
                    if m.get("impact") and m["kind"] == "spatial"
                    and not m.get("repeat") and not m.get("ambient")]
    qual, skipped_small, skipped_micro, found, forms, worst = [], 0, 0, 0, {}, []
    for h in impact_moves:
        travel = max(abs(h.get("dx", 0.0)) / src.W, abs(h.get("dy", 0.0)) / src.H)
        if (h.get("dur", 0.0) * 1000.0) < C9_SKIP_MS and travel < C9_SKIP_TRAVEL \
                and h.get("scaleDelta", 0.0) < 0.5:
            skipped_micro += 1
            continue
        # canon 1.2: below about 12-15 px of counter-travel the percentage rules
        # stop working, and omitting the prep is the correct choice
        if C9_COUNTER_MAG[0] * h.get("dist", 0.0) < min_counter_px \
                and h.get("scaleDelta", 0.0) < C9_SCALE_DIP:
            skipped_small += 1
            continue
        qual.append(h)
        ok, form = _has_windup(src, px, h, win, min_counter_px, fps)
        if ok:
            found += 1
            forms[form] = forms.get(form, 0) + 1
        else:
            worst.append((max(travel, h.get("scaleDelta", 0.0)), h["onsetF"]))

    measured = {"register": register, "qualifying": len(qual),
                "declaredImpactMoves": len(impact_moves),
                "skippedTooSmall": skipped_small, "skippedMicro": skipped_micro,
                "basis": "pixel-fit" if fitted else "source"}
    if len(qual) < C9_MIN_QUALIFYING:
        note = ("fewer than %d declared impact moves are large enough to carry "
                "a legible wind-up" % C9_MIN_QUALIFYING)
        if fit_note:
            note += "; " + fit_note
        return _row("C9", measured, None, [], note, na=True, declarations=decls)

    rate = found / len(qual)
    if rate >= C9_S_RATE:
        band = "S"
    elif rate >= C9_A_RATE:
        band = "A"
    elif rate >= C9_B_RATE:
        band = "B"
    else:
        band = "C"
    if rate == 0.0:
        band = "C"
    measured["anticRate"] = round(rate, 3)
    measured["forms"] = forms
    note = ""
    if found < len(qual):
        note = "%d/%d declared impacts arrive with no wind-up" % (
            len(qual) - found, len(qual))
    if fit_note:
        note = (note + "; " if note else "") + fit_note
    return _row("C9", measured, band, rank_worst(worst), note,
                declarations=decls)


# =============================================================================
# C22  FRAMING                                                       weight 1
# =============================================================================
#
# WHAT IT MEASURES NOW (new criterion).  The unit is the BLOCK: elements are
# collapsed to their group, restricted to their own clip window, then merged by
# proximity, so a headline split per word or per letter is one alignment
# decision rather than eight. Four things:
#   alignment   For each axis the anchor (left / centre / right on x, top /
#               middle / bottom on y) that puts the blocks on the fewest,
#               tightest positions is chosen, and the positions on that anchor
#               are split into those TWO OR MORE blocks use (the grid) and
#               those exactly one block uses (orphans). Choosing the anchor is
#               what lets one rule measure a centred Swiss layout and a
#               left-ragged editorial layout. Alignment uses one sample per
#               beat, so a block cannot align with its own second sample.
#   margins     Drift WITHIN one margin, on an anchored axis only, in frame
#               fractions. Not the spread between margins: a piece using three
#               deliberate indents has a high CV and a perfect grid, and on a
#               centred layout the distance to the nearest edge is whatever the
#               copy length leaves over. Declared fullBleed windows and
#               croppedType elements are exempt by name.
#   focal       Ink components merged into regions by proximity and weighted by
#               area x contrast (canon 2.3 ranks hierarchy by visual weight,
#               not by displacement); regions within 60 % of the heaviest are
#               competing focal points. Two samples per beat, because a beat
#               may carry two focal points over time while each frame carries
#               one.
#   centring    The signed offset of the frame's ink centroid from geometric
#               centre, reported so optical centring is visible. Report only:
#               dead-centre single-block composition is canonical Swiss work,
#               not a fault.
#
# S  two or three alignment positions in use, no orphaned blocks beyond 10 %,
#    one focal point on every settled frame, margin drift under 0.2 % of frame
# C  more than half the blocks orphaned - one alignment position per element,
#    nothing lining up with anything - or three or more focal points on more
#    than a quarter of settled frames
#
# STILL SCORES C ON:  eight text blocks each set at its own left offset, so
# every position carries exactly one block and orphanShare is 1.0. That is the
# layout with no grid, and it is what _controls/bad measures at 0.60.

def _align_positions(values, tol):
    """(positions the piece actually USES, orphan share).

    A position is "used" when two or more blocks sit on it; a block sitting on
    a position nothing else uses is an ORPHAN, and canon's C band for C22 is
    exactly the all-orphan layout, "one alignment position per element". The
    census takes one sample per beat, so a block cannot align with its own
    second sample from the same card, and a position shared across two cards is
    the grid working, which is what it is."""
    if not values:
        return 0, 0, 1.0, 0.0
    vs = sorted(values)
    groups, cur = [], [vs[0]]
    for v in vs[1:]:
        if v - cur[0] <= tol:
            cur.append(v)
        else:
            groups.append(cur)
            cur = [v]
    groups.append(cur)
    used = sum(1 for g in groups if len(g) >= 2)
    orphans = sum(len(g) for g in groups if len(g) < 2)
    spread = sum(g[-1] - g[0] for g in groups)
    return used, len(groups), orphans / float(len(vs)), spread


def _best_anchor(boxes, axis, size, tol):
    """(anchor, usedPositions, totalPositions, orphanShare) for the anchor that
    best explains the layout on this axis. `boxes` is [(box, frame, key)].

    Fewest distinct positions wins, then fewest orphans, then the tightest
    clusters. The third key matters: on a film with one centred block per card,
    left, centre and right can all return the same position count, and the
    anchor the piece actually uses is the one whose values are identical rather
    than merely inside the tolerance. Getting it wrong sends the margin census
    down an axis that has no margin decision on it."""
    if axis == "x":
        cands = [("left", lambda b: b[0] / size),
                 ("centre", lambda b: (b[0] + b[2]) / 2.0 / size),
                 ("right", lambda b: b[2] / size)]
    else:
        cands = [("top", lambda b: b[1] / size),
                 ("middle", lambda b: (b[1] + b[3]) / 2.0 / size),
                 ("bottom", lambda b: b[3] / size)]
    best = None
    for name, fn in cands:
        used, total, orphan, spread = _align_positions(
            [fn(b) for (b, _f, _o) in boxes], tol)
        key = (total, orphan, round(spread, 6))
        if best is None or key < best[0]:
            best = (key, name, used, total, orphan)
    return best[1], best[2], best[3], best[4]


def _merge_frame_boxes(boxes, gap_x, gap_y):
    """Union boxes that sit close enough to read as one block. `boxes` is a
    list of (x0, y0, x1, y1) from ONE frame; returns the merged list."""
    n = len(boxes)
    if n < 2:
        return [list(b) for b in boxes]
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i in range(n):
        bi = boxes[i]
        for j in range(i + 1, n):
            bj = boxes[j]
            if (bi[0] - gap_x <= bj[2] and bj[0] - gap_x <= bi[2]
                    and bi[1] - gap_y <= bj[3] and bj[1] - gap_y <= bi[3]):
                ra, rb = find(i), find(j)
                if ra != rb:
                    parent[max(ra, rb)] = min(ra, rb)
    agg = {}
    for i in range(n):
        r = find(i)
        b = boxes[i]
        a = agg.get(r)
        if a is None:
            agg[r] = [b[0], b[1], b[2], b[3]]
        else:
            a[0] = min(a[0], b[0])
            a[1] = min(a[1], b[1])
            a[2] = max(a[2], b[2])
            a[3] = max(a[3], b[3])
    return list(agg.values())


def _settled_samples(px, src, beats, n_frames, per_beat=2):
    """`per_beat` sample frames per beat, each the STILLEST frame of its share
    of the beat. Framing is a property of a composed frame, and a fixed
    fraction of the beat lands mid-move on anything with a long entrance, which
    reports a perfectly gridded layout as having a position per element."""
    still = None
    if px is not None:
        still = np.asarray(px.frame_delta, dtype=float)
    elif src is not None:
        try:
            still = np.asarray(src.still_delta(), dtype=float)
        except Exception:
            still = None
    out = []
    for (a, b) in beats:
        a = int(clamp(a, 0, n_frames - 1))
        b = int(clamp(b, a, n_frames - 1))
        if b <= a:
            out.append(a)
            continue
        # the LAST share of the beat is where the card is settled, so a single
        # sample takes the second half rather than the middle
        n_take = max(1, int(per_beat))
        edges = np.linspace(a, b + 1, n_take + 1) if n_take > 1 \
            else np.array([a + (b + 1 - a) / 2.0, b + 1])
        for k in range(n_take):
            lo = int(clamp(math.floor(edges[k]), a, b))
            hi = int(clamp(math.ceil(edges[k + 1]) - 1, lo, b))
            if still is None or hi >= len(still):
                out.append(int((lo + hi) // 2))
            else:
                out.append(int(lo + int(np.argmin(still[lo:hi + 1]))))
    return sorted(set(int(clamp(f, 0, n_frames - 1)) for f in out))


def _c22_boxes_from_source(src, beats, manifest, samples):
    """(box, frame, groupKey) for every composed unit visible on a sampled
    settled frame, in composition pixels.

    The unit is the GROUP, not the tween target. A headline split into per-word
    spans is one block on the page and one alignment decision; counting the
    spans reports a perfectly centred line as five distinct centre positions,
    which is how the first pass read a 26-card Swiss film as having thirty
    alignment positions. Declared cropped type and declared full-bleed windows
    are exempt by name."""
    cropped = set(manifest.get("croppedType", []) or [])
    full_bleed = manifest.get("fullBleed", []) or []

    def bleed_frame(f):
        return any(w.get("from", 0) <= f <= w.get("to", 10 ** 9)
                   and not w.get("box") for w in full_bleed
                   if isinstance(w, dict))
    # An element is on screen only inside its own clip window. Opacity alone is
    # not enough: a hard-cut card whose elements are never faded reads as
    # opacity 1 for the whole film, so every card's elements appear on every
    # other card's frames, and on a stack of lines that bridges the gaps
    # between them until the merge swallows the frame. Windows are
    # [start, start + duration) with both ends biased inward.
    fps = float(src.fps)
    windows = {}
    for e in src.elements:
        el = e["i"]
        c = None
        try:
            c = src.clip_of(el)
        except Exception:
            c = None
        if c:
            a = int(math.ceil(c["start"] * fps - 1e-6))
            b = int(math.floor((c["start"] + c.get("duration", 0.0)) * fps - 1e-6))
            windows[el] = (a, max(a, b))

    out = []
    for f in samples:
        if bleed_frame(f):
            continue
        groups = {}
        for e in src.elements:
            el = e["i"]
            if src.is_named(el, cropped):
                continue
            w = windows.get(el)
            if w is not None and not (w[0] <= f <= w[1]):
                continue
            try:
                op = float(src.prop(el, "opacity")[int(clamp(f, 0, src.frames - 1))])
            except Exception:
                continue
            if op < C22_VISIBLE_OPACITY:
                continue
            x0, y0, x1, y1 = src.box_at(el, f)
            if (x1 - x0) < 1.0 or (y1 - y0) < 1.0:
                continue
            if x1 <= 0 or y1 <= 0 or x0 >= src.W or y0 >= src.H:
                continue
            # a wrapper or ground plane has edges, but they are the frame's
            # edges and not an alignment position anybody chose
            if (x1 - x0) * (y1 - y0) >= C22_WRAPPER_AREA * src.W * src.H:
                continue
            k = _group_key(src, el)
            b = groups.get(k)
            if b is None:
                groups[k] = [x0, y0, x1, y1]
            else:
                b[0] = min(b[0], x0)
                b[1] = min(b[1], y0)
                b[2] = max(b[2], x1)
                b[3] = max(b[3], y1)
        blocks = _merge_frame_boxes(list(groups.values()),
                                    C22_BLOCK_GAP_X * src.W,
                                    C22_BLOCK_GAP_Y * src.H)
        # no wrapper test after merging: a merged block that covers most of the
        # frame is a dense composition, not a wrapper, and dropping it leaves
        # the frame with nothing to measure
        for k, b in enumerate(blocks):
            out.append(((b[0], b[1], b[2], b[3]), int(f), "f%d_%d" % (int(f), k)))
    return out


def _c22_boxes_from_pixels(px, samples):
    """The pixel fallback: merged ink regions as boxes, in decode pixels. A
    region is its own object, so only regions sharing an edge INSIDE one frame
    count as aligned, which is the conservative reading."""
    out = []
    merge = C22_FOCAL_MERGE * DEC_W
    for f in samples:
        for k, r in enumerate(_regions(px, f, merge)):
            b = r["box"]
            if (b[2] - b[0]) < 4 or (b[3] - b[1]) < 4:
                continue
            out.append(((b[0], b[1], b[2], b[3]), int(f), "f%d_%d" % (int(f), k)))
    return out


def c22_framing(ctx):
    src = _get(ctx, "src")
    px = _get(ctx, "px")
    manifest = _get(ctx, "manifest", {}) or {}
    beats = _get(ctx, "beats", []) or []
    decls = _declared(manifest, "fullBleed", "croppedType")
    if px is None and src is None:
        return _row("C22", {}, None, na=True,
                    note="framing needs either channel", declarations=decls)
    if not beats:
        return _row("C22", {}, None, na=True,
                    note="no content beats to sample", declarations=decls)

    n_frames = px.n if px is not None else src.frames
    # Two censuses on different samples. Focal points want two frames per beat,
    # because a beat may legitimately carry two focal points over time while
    # each frame carries one. Alignment wants ONE frame per beat, so a block
    # cannot align with its own second sample from the same card.
    samples = _settled_samples(px, src, beats, n_frames, C22_BEAT_SAMPLES)
    align_samples = _settled_samples(px, src, beats, n_frames, 1)

    # a fitted source channel carries tracked components, not layout rects, so
    # it goes down the pixel path with the wider tolerance and the reduced
    # confidence note rather than pretending to be a layout
    if src is not None and _get(ctx, "src_basis") == "source":
        boxes = _c22_boxes_from_source(src, beats, manifest, align_samples)
        W, H, tol, basis = src.W, src.H, C22_ALIGN_TOL, "source"
    elif px is not None:
        boxes = _c22_boxes_from_pixels(px, align_samples)
        W, H, tol, basis = float(DEC_W), float(DEC_H), C22_PIXEL_ALIGN_TOL, "pixel"
    else:
        return _row("C22", {}, None, na=True,
                    note="framing needs the pixel channel when the source "
                         "channel is fitted", declarations=decls)

    per_frame = {}
    for (_b, f, _o) in boxes:
        per_frame[f] = per_frame.get(f, 0) + 1
    blocks_per_frame = float(np.median(list(per_frame.values()))) if per_frame else 0.0
    if len(boxes) < C22_MIN_ELEMENTS:
        return _row("C22", {"blocks": len(boxes), "basis": basis}, None, na=True,
                    note="fewer than %d settled blocks to measure a grid on"
                         % C22_MIN_ELEMENTS, declarations=decls)

    # -- alignment -----------------------------------------------------------
    bs = [tuple(float(v) for v in b) for (b, _f, _o) in boxes]
    x_anchor, x_used, x_total, x_orphan = _best_anchor(boxes, "x", W, tol)
    y_anchor, y_used, y_total, y_orphan = _best_anchor(boxes, "y", H, tol)
    orphan_share = min(x_orphan, y_orphan)
    aligned_share = 1.0 - orphan_share

    # -- margins -------------------------------------------------------------
    # Two corrections over the obvious version. A margin is a design decision
    # only on an ANCHORED axis: on a centred layout the distance to the nearest
    # edge is whatever the copy length leaves over, so its spread charges a
    # correctly centred Swiss film for having words of different lengths. And
    # the fault is DRIFT WITHIN one margin, not spread between margins: a piece
    # using three deliberate indents has a high CV and a perfect grid, while a
    # piece whose left margin is 0.110 on one card and 0.118 on the next has a
    # low CV and a visible 15 px wobble at 1920. So the banded number is the
    # largest spread inside a single margin cluster; the CV is reported beside
    # it and never banded.
    margin_sets = []
    if x_anchor == "left":
        margin_sets.append([x0 / W for (x0, _y0, _x1, _y1) in bs])
    elif x_anchor == "right":
        margin_sets.append([(W - x1) / W for (_x0, _y0, x1, _y1) in bs])
    if y_anchor == "top":
        margin_sets.append([y0 / H for (_x0, y0, _x1, _y1) in bs])
    elif y_anchor == "bottom":
        margin_sets.append([(H - y1) / H for (_x0, _y0, _x1, y1) in bs])
    margins, margin_drift = [], None
    for vals in margin_sets:
        vals = sorted(v for v in vals if 0.0 <= v <= C22_MARGIN_BAND)
        if len(vals) < C22_MIN_MARGIN_SAMPLES:
            continue
        margins += vals
        cur = [vals[0]]
        for v in vals[1:]:
            if v - cur[0] <= tol:
                cur.append(v)
            else:
                if len(cur) >= 2:
                    margin_drift = max(margin_drift or 0.0, float(cur[-1] - cur[0]))
                cur = [v]
        if len(cur) >= 2:
            margin_drift = max(margin_drift or 0.0, float(cur[-1] - cur[0]))
    margin_cv = None
    if len(margins) >= C22_MIN_MARGIN_SAMPLES:
        mg = np.asarray(margins, dtype=float)
        margin_cv = float(mg.std() / max(abs(mg.mean()), 1e-6))
    margin_axes = "".join(a[0] for a in (x_anchor, y_anchor)
                          if a in ("left", "right", "top", "bottom")) or "none"

    # -- focal points and centring -------------------------------------------
    focal_counts, optical = [], []
    if px is not None:
        merge = C22_FOCAL_MERGE * DEC_W
        worst_focal = []
        for f in samples:
            pf = int(clamp(f, 0, px.n - 1))
            regs = _regions(px, pf, merge)
            if not regs:
                continue
            n, _top = _focal_count(regs)
            focal_counts.append(n)
            if n >= C22_C_FOCAL:
                worst_focal.append((float(n), pf))
            cy = px.centroid[pf, 1]
            if not np.isnan(cy):
                optical.append(0.5 - float(cy))
    else:
        worst_focal = []
    one_focal = (sum(1 for n in focal_counts if n <= 1) / len(focal_counts)) \
        if focal_counts else None
    crowded = (sum(1 for n in focal_counts if n >= C22_C_FOCAL) / len(focal_counts)) \
        if focal_counts else 0.0
    optical_offset = float(np.median(optical)) if optical else None

    # -- bands ---------------------------------------------------------------
    band = "B"
    reasons = []
    if aligned_share < C22_C_ALIGNED:
        band = "C"
        reasons.append("%.0f%% of blocks sit on an alignment position nothing "
                       "else uses: %d positions carry two or more blocks, %d "
                       "carry one" % (orphan_share * 100, x_used,
                                      x_total - x_used))
    elif crowded > C22_C_FOCAL_SHARE:
        band = "C"
        reasons.append("%.0f%% of settled frames carry %d or more competing "
                       "focal points" % (crowded * 100, C22_C_FOCAL))
    else:
        margin_ok_s = margin_drift is None or margin_drift <= C22_S_MARGIN_DRIFT
        margin_ok_a = margin_drift is None or margin_drift <= C22_A_MARGIN_DRIFT
        margin_ok_b = margin_drift is None or margin_drift <= C22_B_MARGIN_DRIFT
        focal_ok_s = one_focal is None or one_focal >= C22_S_ONE_FOCAL
        focal_ok_a = one_focal is None or one_focal >= C22_A_ONE_FOCAL
        if (C22_S_MIN_POSITIONS <= x_used <= C22_S_POSITIONS
                and aligned_share >= C22_S_ALIGNED
                and margin_ok_s and focal_ok_s):
            band = "S"
        elif (x_used <= C22_A_POSITIONS and aligned_share >= C22_A_ALIGNED
                and margin_ok_a and focal_ok_a):
            band = "A"
        elif x_used <= C22_B_POSITIONS and margin_ok_b:
            band = "B"
        else:
            band = "B"
            reasons.append("%d alignment positions in use on the %s anchor, "
                           "%.0f%% of blocks orphaned"
                           % (x_used, x_anchor, orphan_share * 100))
    if optical_offset is not None and band in ("S", "A"):
        lo, hi = C22_OPTICAL_RISE
        if optical_offset < 0:
            reasons.append("the ink centroid sits %.1f%% of frame height BELOW "
                           "geometric centre; optical centring raises it %.0f-%.0f%%"
                           % (-optical_offset * 100, lo * 100, hi * 100))
    if basis == "pixel":
        reasons.append("reduced confidence: boxes are tracked ink regions, not "
                       "layout rects")
    measured = {
        "alignPositions": x_used, "xAnchor": x_anchor,
        "xPositionsTotal": x_total,
        "yPositions": y_used, "yAnchor": y_anchor,
        "alignedShare": round(aligned_share, 3),
        "orphanShare": round(orphan_share, 3),
        "blocks": len(boxes), "blocksPerFrame": round(blocks_per_frame, 1),
        "marginDrift": round(margin_drift, 4) if margin_drift is not None else None,
        "marginCv": round(margin_cv, 3) if margin_cv is not None else None,
        "marginSamples": len(margins), "marginAxes": margin_axes,
        "focalMedian": int(np.median(focal_counts)) if focal_counts else None,
        "focalMax": int(max(focal_counts)) if focal_counts else None,
        "oneFocalShare": round(one_focal, 3) if one_focal is not None else None,
        "opticalOffset": round(optical_offset, 4)
        if optical_offset is not None else None,
        "basis": basis,
    }
    return _row("C22", measured, band, rank_worst(worst_focal),
                "; ".join(reasons), declarations=decls)


# =============================================================================
# C24  EYE-TRACE AND SCREEN DIRECTION                    weight 1, REPORT ONLY
# =============================================================================
#
# WHAT IT MEASURES (new criterion, and canon marks it report-only in both the S
# and the C column, so it never bands and never moves W):
#   jump      Where attention actually sat, not where a tween ended: the
#             centroid of the heaviest ink region on the last frame before the
#             cut, against the same measurement on the settled frame after it,
#             as a fraction of the frame diagonal. Canon 5 wants the incoming
#             subject inside roughly 15-20 % of the diagonal, or displaced
#             deliberately with 6-8 frames to find it.
#   parallax  For frames where two or more element groups translate at once,
#             the ratio of each layer's per-frame step to the largest layer's,
#             and the variation of that ratio through the move. Canon 5: fixed
#             ratios are correct for a LATERAL move only; under a push the
#             ratio follows d/(d-t) and must change, so a constant ratio inside
#             a push is the sliding-planes tell.
#   direction The compass bin of the incoming motion at each cut, and the share
#             of consecutive cuts that reverse screen direction. The sequence
#             is a compact string: uppercase N E S W for the cardinals,
#             lowercase n e s w for the diagonal between that cardinal and the
#             next clockwise one, "." for a cut whose incoming frame does not
#             move, and "-" for a blank one.
#
# S  report only.  C  report only.
# It cannot score C by construction, which is canon's instruction for this row.

def _dir_bin(dx, dy):
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return "-"
    ang = math.degrees(math.atan2(-dy, dx)) % 360.0
    names = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"]
    return names[int(((ang + 22.5) % 360.0) // 45.0)]


def _angle_between(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def c24_eye_trace(ctx):
    px = _get(ctx, "px")
    src = _get(ctx, "src")
    manifest = _get(ctx, "manifest", {}) or {}
    beats = _get(ctx, "beats", []) or []
    fps = float(_get(ctx, "fps", 30.0) or 30.0)
    decls = _declared(manifest, "cuts")
    if px is None or len(beats) < 2:
        return _row("C24", {"beats": len(beats)}, None, na=True,
                    note="eye-trace needs the pixel channel and at least two "
                         "beats", declarations=decls)

    merge = C22_FOCAL_MERGE * DEC_W
    diag = math.hypot(DEC_W, DEC_H)

    # -- attention jump across each cut ---------------------------------------
    jumps, worst, short, unmeasured = [], [], 0, []
    for i in range(len(beats) - 1):
        a0, b0 = beats[i]
        a1, b1 = beats[i + 1]
        pre = _attention_point(px, b0, merge)
        post_f = int(clamp(a1 + C24_POST_SAMPLE * max(b1 - a1, 0), 0, px.n - 1))
        post = _attention_point(px, post_f, merge)
        if pre is None or post is None:
            # a blank lead-in, a dip to ground or an all-over field has no
            # single point of interest, so the boundary is NOT measured. Saying
            # "0 of 20 cuts" over a 26-cut film reads as an eye-trace check
            # across the whole edit, and it was not one.
            unmeasured.append(int(a1))
            continue
        j = math.hypot(pre[0] - post[0], pre[1] - post[1]) / diag
        jumps.append(j)
        if j > C24_COMFORT_DIAGONAL:
            worst.append((j, a1))
            if (b1 - a1 + 1) < fscale(C24_FIND_FRAMES, fps) * 2:
                short += 1

    # -- parallax ratios ------------------------------------------------------
    # source channel only: a tracked component's per-frame step is dominated by
    # merges and splits, and a ratio built from two of them measures the
    # tracker, not the layer depth
    ratios, ratio_cvs, layer_pairs = [], [], 0
    if src is not None and _get(ctx, "src_basis") == "source":
        for (a, b) in beats:
            movers = {}
            for m in src.moves:
                if m["kind"] != "spatial" or m.get("repeat"):
                    continue
                if m["endF"] < a or m["onsetF"] > b:
                    continue
                if not set(m.get("spatial", [])) & TRANSLATE_PROPS:
                    continue
                movers.setdefault(_group_key(src, m["el"]), []).append(m)
            if len(movers) < C24_PARALLAX_MIN_LAYERS:
                continue
            steps = {}
            for k, ms in movers.items():
                el = ms[0]["el"]
                lo = int(clamp(a, 0, src.frames - 2))
                hi = int(clamp(b, lo + 1, src.frames - 1))
                cx = src.prop(el, "cx")[lo:hi + 1].astype(float)
                cy = src.prop(el, "cy")[lo:hi + 1].astype(float)
                steps[k] = np.hypot(np.diff(cx), np.diff(cy))
            keys = list(steps)
            if len(keys) < 2:
                continue
            ref = max(keys, key=lambda k: float(np.nansum(steps[k])))
            base = steps[ref]
            for k in keys:
                if k == ref:
                    continue
                other = steps[k]
                n = min(len(base), len(other))
                if n < C24_PARALLAX_MIN_FRAMES:
                    continue
                live = (base[:n] >= C24_PARALLAX_MIN_STEP) & \
                       (other[:n] >= C24_PARALLAX_MIN_STEP)
                if int(live.sum()) < C24_PARALLAX_MIN_FRAMES:
                    continue
                r = other[:n][live] / base[:n][live]
                layer_pairs += 1
                ratios.append(round(float(np.median(r)), 2))
                ratio_cvs.append(float(np.std(r) / max(abs(np.mean(r)), 1e-9)))

    # -- screen direction across the cuts -------------------------------------
    seq, angles = [], []
    span = fscale(C24_DIR_FRAMES, fps)
    for (a, b) in beats:
        f0 = int(clamp(a, 0, px.n - 1))
        f1 = int(clamp(a + span, 0, px.n - 1))
        p0 = _attention_point(px, f0, merge)
        p1 = _attention_point(px, f1, merge)
        if p0 is None or p1 is None:
            seq.append("-")
            angles.append(None)
            continue
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        if math.hypot(dx, dy) < C24_DIR_MIN_STEP:
            seq.append(".")
            angles.append(None)
            continue
        seq.append(_dir_bin(dx, dy))
        angles.append(math.degrees(math.atan2(-dy, dx)) % 360.0)
    pairs = [(angles[i], angles[i + 1]) for i in range(len(angles) - 1)
             if angles[i] is not None and angles[i + 1] is not None]
    reversals = sum(1 for (p, q) in pairs
                    if _angle_between(p, q) >= C24_REVERSAL_DEG)
    reversal_share = reversals / len(pairs) if pairs else None

    j = np.asarray(jumps, dtype=float)
    over_comfort = int((j > C24_COMFORT_DIAGONAL).sum()) if len(j) else 0
    over_half = int((j > C24_JUMP_DIAGONAL).sum()) if len(j) else 0
    note_bits = []
    if len(j):
        note_bits.append("%d of %d measured beat boundaries move the point of "
                         "interest more than %d%% of the frame diagonal"
                         % (over_comfort, len(j), int(C24_COMFORT_DIAGONAL * 100)))
    if unmeasured:
        note_bits.append("%d boundary/boundaries carry no single point of "
                         "interest on either side and were not measured (f%s)"
                         % (len(unmeasured),
                            ", f".join(str(x) for x in unmeasured[:6])))
    if short:
        note_bits.append("%d of them land in a beat too short to give the eye "
                         "%d frames to find the new subject"
                         % (short, fscale(C24_FIND_FRAMES, fps)))
    if ratio_cvs:
        note_bits.append("%d parallax layer pair(s), median ratio spread %.2f"
                         % (layer_pairs, float(np.median(ratio_cvs))))
    if reversal_share is not None and reversal_share > 0.5:
        note_bits.append("%.0f%% of consecutive cuts reverse screen direction"
                         % (reversal_share * 100))
    measured = {
        "boundaries": len(beats) - 1,
        "boundariesMeasured": len(jumps),
        "boundariesUnmeasured": len(unmeasured),
        "medianJump": round(float(np.median(j)), 3) if len(j) else None,
        "maxJump": round(float(j.max()), 3) if len(j) else None,
        "overComfort": over_comfort, "overHalf": over_half,
        "unresolvedJumps": short,
        "parallaxPairs": layer_pairs,
        "parallaxRatios": sorted(set(ratios))[:8],
        "parallaxRatioCv": round(float(np.median(ratio_cvs)), 3)
        if ratio_cvs else None,
        "directionSequence": "".join(s if len(s) == 1 else s[0].lower()
                                     for s in seq)[:48],
        "directionLegend": "NESW cardinal, nesw diagonal, . still, - blank",
        "reversalShare": round(reversal_share, 3)
        if reversal_share is not None else None,
    }
    return _row("C24", measured, None, rank_worst(worst),
                "report only: " + "; ".join(note_bits) if note_bits
                else "report only", na=True, declarations=decls)


# =============================================================================
# family entry point
# =============================================================================

CRITERIA = (c3_simultaneity, c7_arcs, c8_secondary, c9_anticipation,
            c22_framing, c24_eye_trace)


def run_all(ctx):
    """Every row this family owns, in criterion order."""
    return [fn(ctx) for fn in CRITERIA]


class Ctx(object):
    """A plain holder, so an integrator that has the values but not a context
    class can build one in a line. Every field is documented in the module
    docstring."""

    def __init__(self, **kw):
        self.src = None
        self.src_basis = None
        self.px = None
        self.manifest = {}
        self.fps = 30.0
        self.frames = 0
        self.width = 0
        self.height = 0
        self.beats = []
        self.cuts = []
        self.audio = None
        self.heroes = None
        self.register = DEFAULT_REGISTER
        self.genre = None
        self.delivery = None
        self.dec_w, self.dec_h = DEC_W, DEC_H
        for k, v in kw.items():
            setattr(self, k, v)


def _main():
    """Load a context previously dumped by the integrator and print the rows.

    The dump is a pickle, because the context holds numpy arrays and the two
    channel objects. Nothing else in this module needs it.
    """
    path = sys.argv[1] if len(sys.argv) > 1 else "ctx.pkl"
    if not os.path.exists(path):
        print("crit_composition: no dumped context at %s" % path)
        print("usage: python crit_composition.py <ctx.pkl>")
        return 1
    import pickle
    with open(path, "rb") as f:
        ctx = pickle.load(f)
    rows = run_all(ctx)
    print(json.dumps(rows, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
