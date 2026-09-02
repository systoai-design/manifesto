#!/usr/bin/env python3
"""crit_motion.py -- the MOTION family of the corrected rubric (canon.md section 7).

Six criteria, one function each, uniform signature:

    c1_ease_discipline(ctx)     C1  ease discipline          weight 2
    c2_ease_vocabulary(ctx)     C2  ease vocabulary          weight 1
    c6_settle_quality(ctx)      C6  settle quality           weight 1
    c10_timing_contrast(ctx)    C10 timing contrast          weight 1
    c11_distance_duration(ctx)  C11 distance and duration    weight 1
    c21_restraint(ctx)          C21 restraint                weight 1

Every one returns

    {"id": str, "name": str, "band": "S"|"A"|"B"|"C"|None, "weight": int,
     "na": bool, "measured": {...}, "worstFrames": [int], "basis": str,
     "note": str, "declarations": [str]}

`declarations` lists the manifest claims that row actually consumed, by name, so
the report can print the declaration budget canon asks for. A row that used no
declaration returns an empty list.

`all_criteria(ctx)` runs the six in id order and returns the list of rows.

-----------------------------------------------------------------------------
THE CONTEXT OBJECT
-----------------------------------------------------------------------------
`ctx` may be any object with these attributes, or a dict with these keys; both
work (see `_get`). Nothing else is read and nothing is written back.

REQUIRED
  fps        float               delivered frame rate
  width      int                 delivered frame width in px
  height     int                 delivered frame height in px
  frames     int                 delivered frame count
  manifest   dict                grade.json, verbatim
  cuts       list[int]           cut frames, ascending, cuts[0] == 0
  beats      list[(int, int)]    inclusive content runs, from beats_from_cuts

  src        the source channel (grade-mg.py `Source`), or the fitted
             `PixelSource`, or None. Read only. Used:
               .fps .frames .W .H .diag .register .manifest
               .elements   list of dicts carrying i, key, id, clip, parent
                           (index of the nearest tween-target ancestor, -1 for
                           none), group
               .num        list of (frames, P) float arrays, one per element
               .pi         {prop name -> column}; needs cx, cy, w, h, scale,
                           rotation, opacity
               .moves      list of move dicts (keys below)
               .prop(el, name)  -> (frames,) array
               .box_at(el, f)   -> (x0, y0, x1, y1)
               .clip_of(el)     -> clip dict with start and duration, or None
               .is_named(el, names) -> bool
               .group_of(el)    -> stable group key string
             cx, cy, w, h are getBoundingClientRect, so WORLD space, already
             composed through the parent chain. x, y, scale, rotation and
             opacity are gsap.getProperty, so element LOCAL. This module
             measures translation and scale in world space for exactly that
             reason; see `channel_series`.

OPTIONAL, all defaulted
  px         the pixel channel (grade-mg.py `Pixel`), or None. C11 only:
               .n .fps .width .height .tracks
             where a track is {"frames": [int], "cx": [], "cy": [], "area": [],
             "box": [(x0, y0, x1, y1)]} in the 640x360 decode space.
  audio      the audio channel, or None. C10 only:
               .present (bool), .grid ({"bpm", "period", "phase"} or None),
               .bar_lines(fps, n_frames) -> [float]
  heroes     list of hero move dicts (grade-mg.py `hero_moves`). Computed
             locally from manifest["hero"] and settled rect area when absent.
  strobe     a precomputed (travel, strobe, moving, thr) tuple from a
             `strobe_scan`, so C11 and C19 cannot disagree. When absent C11
             runs its own scan over ctx.px.
  fitted     bool. True when src is the fitted PixelSource. Inferred from the
             absence of src.tweens when not supplied.

MOVE DICT keys read: el, key, clip, start, dur, startF, endF, durF, onsetF,
settleF, props, spatial, paint, kind, ease, easeSamples, repeat, startAt, to,
mechanical, organic, impact, dx, dy, dist, scaleFrom, scaleTo, scaleDelta,
opFrom, opTo, cxFrom, cyFrom, cxTo, cyTo, boxW, boxH, role, ambient.
This module RE-DERIVES class, role and the progress curve on COMPOUND moves of
its own (see `compound_moves`); it never mutates the integrator's move dicts.

MANIFEST keys read, all optional. The default is always the strict case and an
exemption is always BY NAME:
  register        one of REGISTERS. Default "corporate".
  mechanical      [name]   elements exempt from C1: idle pushes, tickers, loops
  loops           [name]   elements graded on C6's LOOP overshoot budget. A
                           tween with repeat != 0 gets it without a declaration
  impact          [name]   declared impact verbs; transitions are already
                           exempt by class without one
  hero            {beat index: name}
  lockups         [[name]] a lockup counts as ONE element in C21's onset rate
  triggerGroups   [[name]] the same, for a declared shared trigger
  shutterFrames   [[a, b]] ranges rendered with a real shutter. C11's strobe
                           tolerance DOUBLES inside them (canon 1.9, "up to 1 %
                           with a shutter"); it does not exempt them
  cuts            [int]

-----------------------------------------------------------------------------
MEASUREMENT CAUTIONS carried from grade-mg.py, each of which cost an hour once
-----------------------------------------------------------------------------
  - decoding a RANGE gives (n, H, W, 3); reduce over axis 3, never axis 2
  - clip windows are [start, start + duration); bias both ends inward
  - smooth a series before looking for reversals, grain manufactures them
  - never measure motion on a bounding box, use the ink COUNT integral. The one
    place this module reads w and h is the SCALE channel, where the rect IS the
    measurement (a composed scale has no other world-space witness) and where a
    zero-size rect is rejected rather than believed
  - exempt by NAME through the manifest, never by loosening a threshold
  - worstFrames is ranked by SEVERITY, never by frame number

-----------------------------------------------------------------------------
WHAT CHANGED AGAINST THE EIGHTEEN-CRITERION CODE, AND WHY
-----------------------------------------------------------------------------
C1  The curve is read off THE CHANNEL THE TWEEN WRITES, over a COMPOUND of the
    consecutive tweens that write it. The old code picked whichever tracked
    property had the largest travel, comparing scale units against frame
    diagonals, so on a card carrying a linear idle scale push under a
    power2.out x slide it classified a slice of the push and reported the slide
    as linear. Round trips, leading anticipation runs, transitions by class,
    moves cut before they settle, and moves whose channel is untracked
    (clip-path, filter) are separated out rather than charged. Departures are
    detected from the tail of the element's life, so "accelerate away and cut"
    stops being a violation on every card in a film.
C2  Clusters the same measured compound shapes at radius 0.06 per role. The
    overshoot amplitude bands are delegated to C6 as canon says; C2 keeps only
    canon's own C condition, overshoot on a paint property. The two used to
    contradict each other, C2 wanting overshootShare 0 for S while C6 allowed a
    corporate register 0-5 %.
C6  Adds the LOOP register row playlist-lessons.md asks for, granted
    automatically to any tween with repeat != 0. Amplitude is
    (peak - target) / (target - start) on the world channel, canon's explicit
    denominator. The register MINIMUM applies to arrivals only. The old global
    0.25 amplitude ceiling is gone: it contradicted the energetic row it sat
    next to.
C10 R_move is the 90th over the 10th percentile of move duration. Max over min
    across ninety moves is a two-sample statistic, not a contrast measure, and
    it can never fail.
C11 Strobe blocks S and A and is printed, and that is all it does. Canon's C row
    for C11 is "rho < 0 within class, or > 3 violations" and contains no strobe
    term. A declared shutter range doubles the tolerance instead of exempting
    the frames, and a strobing run whose own travel crosses half the frame is a
    transition by class.
C21 Onsets are counted per GROUP, collapsing a stagger to one gesture, because
    canon 2.2 prescribes per-character sweeps of 1.5-2.5 s and a per-element
    count makes every one of them a C. An onset is a FRAME on which something
    starts, so three chart bars growing together from one frame at three
    durations are one onset; whether they should start together is C3's
    question, and counting them here charged the same simultaneity twice.

Four MEASUREMENT bugs found by running the corrected criteria over the five
graded samples, each of which produced a confident wrong number:

  1. The window is biased inward, which is right for ownership and wrong for
     endpoints. A tween at t = 16.266667 s and 30 fps computes to frame
     488.00001 and rounds to 489, dropping the first frame of travel out of
     canon's (target - START) denominator: back.out(1.8) reported 27 % instead
     of 11 %. `anchor_window` takes back a frame that is stationary on its far
     side, so a chain never annexes its neighbour's travel.
  2. The rect is a composed witness for SCALE only when nothing else deforms
     it. A star tweening scale 0.3 -> 1 and rotation -40 -> 0 grows its
     axis-aligned box by 2.37x while its scale changes by 3.33x: 58 % reported
     for the same 11 % overshoot. The rect is now cross-checked against the
     element's own transform and dropped when they disagree.
  3. A `scaleY: 0 -> 1` bar grows in HEIGHT. Taking whichever of w and h moved
     most read the WIDTH, which on a bar inside a scaling parent is the
     parent's curve with the child's name on it: a 17.5 % overshoot on a
     sine.out that has none.
  4. Chaining by channel merged an x slide with a y lift-out on the same
     element, turning one entrance and one departure into a single move that
     accelerated, stopped and accelerated again. Chains are bucketed by the
     AXES a tween writes, not only by channel.

After all of it, over the five graded samples, the weighted motion family runs
systo-26s 84, abe-ad 60, the amateur control 59, higgsfield 45, and the
two-tween smoke file reports every row N/A rather than collecting six free
passes for having almost no motion in it.
"""

import math

import numpy as np

# =============================================================================
# CONSTANTS.  Every threshold this family uses lives here and nowhere else,
# because all of them will be re-tuned.  Names are C<criterion>_*; shared
# machinery is MOTION_* or a plain name matching grade-mg.py so the integrator
# can see the correspondence.
# =============================================================================

# ---- shared measurement ----------------------------------------------------
MOTION_SMOOTH = 3                # box width before looking for sign changes
SHAPE_MIN_FRAMES = 4             # below this a move carries fewer than two
                                 # intermediate samples and cannot express an
                                 # ease at all: a 33 ms slam at 60 fps is
                                 # unclassifiable, not linear

# Ambient, the onset and the settle are defined ONCE, by the integrator, on the
# move dicts it hands over (grade-mg.py AMBIENT_MIN_S / AMBIENT_MAX_TRAVEL /
# ONSET_PROGRESS / SETTLE_EPS). This module reads mv["ambient"], mv["onsetF"]
# and mv["settleF"] and never redefines them, because three criteria once
# defined ambient three different ways and the same tween was ambient for one
# and primary for another.
TRANSLATE_PROPS = {"x", "y", "xPercent", "yPercent", "translateX", "translateY",
                   "top", "left"}
SCALE_PROPS = {"scale", "scaleX", "scaleY", "width", "height"}
ROTATE_PROPS = {"rotation", "rotationX", "rotationY", "rotationZ"}

DEFAULT_REGISTER = "corporate"
REGISTERS = ("premium", "corporate", "playful", "energetic", "loop")

WEIGHTS = {"C1": 2, "C2": 1, "C6": 1, "C10": 1, "C11": 1, "C21": 1}

# ---- C1 ease discipline ----------------------------------------------------
C1_CHAIN_GAP_F30 = 2             # tweens on one element and one channel within
                                 # this many frames of each other are ONE move.
                                 # A slide handed x from 113 to 135 to 68 to 0
                                 # has one curve on screen and gets one class
C1_ANTIC_FRAC = 0.25             # a leading counter-run up to this fraction of
                                 # net travel is ANTICIPATION (canon 1.2 puts
                                 # the designed band at 0.08-0.20), stripped
                                 # before classification rather than charged as
                                 # a backwards ease
C1_ROUNDTRIP_RETURN = 0.15       # ... and it has to come BACK: the end value
                                 # within this fraction of the path length of
                                 # the start value. A settle that oscillates
                                 # about its target and stops there is not a
                                 # round trip however small its net/path is
C1_ROUNDTRIP_NET = 0.35          # net / path below this is a round trip: a
                                 # bounce, a pulse, a nudge-and-return. It has
                                 # no arrival direction and C6 grades it
C1_JUNCTION_CUT_TOL = 2          # frames at any rate. A two-tween junction this
                                 # close to a cut is a step across an edit, not
                                 # a step inside a move, and C17 grades the edit
C1_SEEN_PROGRESS = 0.95          # a move whose progress at its clip end or the
                                 # next cut is below this is cut MID-FLIGHT, so
                                 # its terminal ease is never rendered (canon
                                 # 1.6). Direction waived, linear still charged
C1_CONTEND_FULL = 0.75           # an ancestor tween on the same channel
                                 # covering this much of the window is
                                 # COMPOSITION, and the world curve is the curve
                                 # the viewer sees (canon C1). Partial overlap
                                 # is two sequential events sharing a window and
                                 # the child is measured relative to it
C1_CONTEND_COTERM = 0.60         # ... but only when the two are ONE gesture.
                                 # A 42 px word rise inside a 285 px lockup
                                 # slide that runs twice as long is a slice of
                                 # the parent's curve, and measuring it in world
                                 # space grades the parent twice and the child
                                 # never
C1_OVERSHOOT_PEAK = 0.005        # peak above 1.0, as a fraction of travel
C1_LINEAR_TOL = 0.05             # |s(q) - q| at all three quarters, and ...
C1_LINEAR_CV = 0.30              # ... a flat speed profile. Both, because the
                                 # quarters alone misread a composed curve
C1_OUT_TAU = 0.42                # speed-profile centroid. power1.out 0.33,
C1_IN_TAU = 0.58                 # power4.out 0.17, sine.out 0.36, sine.in 0.64,
                                 # every symmetric inOut exactly 0.50. A
                                 # knife-edge midpoint no longer flips a
                                 # circ.inOut into an in at s(0.5) = 0.39
C1_OUTIN_DIP = 0.55              # mid-third mean speed below this share of the
                                 # end thirds, with tau near 0.5, is an outIn:
                                 # two tweens chained through a dead stop
C1_STUTTER_ZERO_SHARE = 0.30     # share of zero steps inside a move that is
                                 # otherwise travelling (canon section 8, 8)
C1_JUNCTION_RATIO = 0.35         # speed after over speed before at a chained leg
                                 # boundary. Below this, with both sides going
                                 # the same way, the element decelerates to a
                                 # stop and restarts: canon 1.2's velocity step,
                                 # "one curve, not two tweens". Measured on
                                 # systo-26s at 8.73 px/frame into 0.16
C1_JUNCTION_WIN_F30 = 2          # frames either side of the boundary
C1_MIN_TRAVEL_PX = 0.75          # below this the rect track is quantisation
C1_MIN_TRAVEL_SCALE = 0.010      # relative rect growth
C1_SCALE_RECT_TOL = 0.15         # the RECT is a composed witness for scale only
                                 # when nothing else deforms it. A star tweening
                                 # scale 0.3 -> 1 AND rotation -40 -> 0 grows its
                                 # axis-aligned box by 2.37x while its scale
                                 # changes by 3.33x, and reading the box turned
                                 # a textbook 11 % back.out into a 58 % one
C1_ANCHOR_BACK_F30 = 1           # frames the measurement window may reach back
                                 # to recover a move's true FROM state. A tween
                                 # at t = 16.266667 s and 30 fps is frame 488.00001
                                 # and the inward bias rounds it to 489, which
                                 # drops the first frame of travel out of the
                                 # denominator. Canon's overshoot is
                                 # (peak - target) / (target - START), so losing
                                 # the start doubles the number
C1_MIN_TRAVEL_ROT = 0.5          # degrees
C1_MIN_TRAVEL_OPACITY = 0.02
C1_DEPART_SCALE = 0.10           # a LAST move ending on its card's last frame
                                 # this much further from unity scale than it
                                 # started is leaving, not repositioning: the
                                 # slam zoom out and the premium sink both do
                                 # it, and neither comes to rest on screen.
                                 # Below it the move is a settle carrying a
                                 # little scale and the arrival rules apply.
C1_RECEDE_SCALE = 0.05           # canon C1: small recedes are exempt ...
C1_RECEDE_TRAVEL = 0.03          # ... under 5 % scale and 3 % of frame height
C1_TRANSITION_TRAVEL = 0.50      # a move crossing half the frame is a
C1_TRANSITION_SCALE = 1.00       # transition BY CLASS (canon 5) and crosses at
                                 # one acceleration on purpose
C1_DEPART_TAIL_F30 = 6           # an element's last spatial move ending within
                                 # this of its clip end and travelling AWAY from
                                 # rest is a departure, however its opacity
                                 # behaves. Six frames is canon 1.9's own floor:
                                 # a pose held for less than that is never seen
                                 # as a settle, so the move was not an arrival
C1_A_DRATE = 0.05
C1_B_DRATE = 0.15                # canon C1 C band: "> 15 % direction violations"
C1_MIN_EVIDENCE = 6              # below this many graded moves the row is N/A,
                                 # never S. A 3 s two-tween test file has no
                                 # ease discipline to demonstrate, and awarding
                                 # it one is how a synthetic smoke test came to
                                 # outscore every finished film in the set

# ---- C2 ease vocabulary ----------------------------------------------------
C2_CLUSTER_RADIUS = 0.06         # canon C2, on the source channel
C2_FIT_CLUSTER_RADIUS = 0.04     # tighter on fitted curves, which carry noise
C2_S_CLUSTERS = 3                # canon C2 S: ">= 3 clusters"
C2_B_CLUSTERS = 2
C2_A_ROLES_WITH_TWO = 1
C2_MAX_SHAPES = 5                # canon 1.6: past about five distinct curves a
                                 # piece is unresolved, not varied. Reported
C2_PAINT_OVERSHOOT = 0.005       # any overshoot on opacity or colour is a C
C2_C_TOPSHARE = 0.75             # canon section 8 item 1's own detector for the
                                 # PowerPoint tell is "one ease shape for the
                                 # whole film". Three quarters of the curves in
                                 # one cluster IS one ease shape, whether or not
                                 # a stray fourth exists to keep the count above
                                 # canon's literal "1 cluster"
C2_MIN_MOVES = 3

# ---- C6 settle quality -----------------------------------------------------
C6_REVERSAL_FLOOR = 0.005        # steps under 0.5 % of travel are grain
C6_SETTLE_ENTER = 0.95           # reversals counted only after s first reaches
                                 # this, so an anticipation dip before the move
                                 # is not counted as a settle reversal
C6_SMOOTH = 3
C6_BUDGET = {                    # register: (min amp, max amp, max reversals)
    # canon 1.5, one row per register, plus the LOOP row playlist-lessons.md
    # asks for: all four of the playlist's easing compliments are on short
    # character or object loops, praised for exactly the anticipation and
    # overshoot the held-card registers forbid, and the canon table has no row
    # for them.
    "premium": (0.00, 0.02, 1),
    "corporate": (0.00, 0.05, 1),
    "playful": (0.15, 0.25, 2),
    "energetic": (0.15, 0.30, 1),
    "loop": (0.00, 0.35, 3),
}
C6_MIN_AMP_ROLES = ("entrance",)  # the register MINIMUM asks an arrival to
                                  # bounce; it has no business on a reposition
C6_A_OFF = 0.05
C6_B_OFF = 0.15                  # canon C6 C band: "outside budget on > 15 %"
C6_C_REVERSALS = 3               # canon C6 C band: ">= 3 reversals"
C6_TELL_AMPLITUDE = 0.13         # canon section 8 item 5, reported not banded
C6_MIN_SETTLES = 6               # below this the row is N/A, never S

# ---- C10 timing contrast ---------------------------------------------------
C10_MIN_BEATS = 3
C10_MIN_MOVES = 4
C10_S_RBEAT, C10_S_CV, C10_S_RMOVE = 3.0, 0.30, 3.0
C10_A_RBEAT, C10_A_CV, C10_A_RMOVE = 2.0, 0.18, 2.0
C10_C_CV, C10_C_RMOVE = 0.10, 1.5
C10_MOVE_PCTL = (10.0, 90.0)     # R_move is p90 / p10. Max over min across
                                 # ninety moves is a two-sample statistic: one
                                 # 2-frame accent against one 3-second push
                                 # reports 45 and the row can never fail
C10_CLASSES = [("fast", 0.15, 0.30), ("medium", 0.30, 0.50),
               ("slow", 0.50, 0.80), ("very slow", 0.80, 2.00)]
C10_GRID_TOL_F30 = 2             # a cut within this of a bar line is on grid
C10_GRID_SHARE = 0.60            # this many cuts on the grid and cv is the
                                 # wrong statistic; grade bar multiples instead
C10_S_MULTIPLES, C10_A_MULTIPLES = 3, 2

# ---- C11 distance and duration ---------------------------------------------
C11_MIN_N = 5                    # fewer entrance translations and rho is N/A
C11_K_TABLE = [(50, 0.8), (100, 1.0), (200, 1.3), (300, 1.5), (400, 1.6)]
C11_K_FULLSCREEN = 1.9           # "full screen 1.8-2.0x", midpoint
C11_OUTLIER_LO, C11_OUTLIER_HI = 0.5, 2.0
C11_THIRD_RULE = 1.0 / 3.0
C11_STROBE_FRAC = 0.005          # 0.5 % of FRAME WIDTH per frame: 10 px at
                                 # 1920, 5 px at 960, 20 px at 3840
C11_STROBE_FPS_REF = 30.0        # halve at 24, roughly double at 60
C11_STROBE_SHUTTER_MULT = 2.0    # canon 1.9: "up to 1 % with a shutter". A
                                 # declared shutter RAISES the tolerance; it
                                 # does not exempt the frames
C11_STROBE_MIN_RUN = 2           # consecutive frames over the threshold
C11_STROBE_MIN_AREA = 200        # too small to carry a hard edge
C11_STROBE_MAX_COMPS = 8         # the largest regions in a frame; below them
                                 # is dust no viewer reads as an edge
C11_STROBE_MATCH_SHARE = 0.25    # a box covering this much of the smaller of a
                                 # pair is the same region between two frames.
                                 # More than one such partner on either side is
                                 # a merge or a split, and in both the box jumps
                                 # to a union with nothing moving on screen
C11_STROBE_MOVING_PX = 0.5       # at 640 wide; below this the region is still
C11_TRACK_DIR_DEG = 60.0         # canon 1.9 names four things that move the
                                 # strobe threshold, and the last is "whether
                                 # the eye is TRACKING the object, which is why
                                 # fast pans judder while a tracked hero does
                                 # not". Smooth pursuit locks onto ONE flow. Two
                                 # fast regions whose displacement directions
                                 # differ by more than this are two flows: one
                                 # is tracked and the rest strobe. Below it they
                                 # are one moving group - a stagger, a lockup or
                                 # a line of glyphs - and the eye follows it as
                                 # one object.
C11_TRACK_STRONG_MULT = 1.5      # only regions this far past the threshold vote
                                 # on direction. At 3.2 px of displacement one
                                 # pixel of vertical quantisation is 18 degrees
                                 # of angle, and marginal regions invented
                                 # phantom second flows on eight glyphs of one
                                 # word travelling together.
C11_TRACK_TELEPORT = 1.0         # a region displacing more than its own extent
                                 # ALONG THE TRAVEL AXIS renders as two
                                 # non-overlapping copies: there is no
                                 # stroboscopic fusion even under pursuit, and
                                 # this is the case a shutter exists for.
C11_TRACK_TELEPORT_AREA = 800    # ... on a region big enough to read as an
                                 # object. A 12 px dot crossing its own width is
                                 # a dot, not a strobing edge.
C11_STROBE_TRANSIT_RUN = 0.50    # a strobing run whose own total travel crosses
                                 # this much of the frame is a whip, a wipe or a
                                 # card flying through frame: canon 5 exempts
                                 # those by class
C11_S_RHO, C11_S_OUTLIER = 0.40, 0.10
C11_A_RHO, C11_A_OUTLIER, C11_A_VIOLATIONS, C11_A_STROBE = 0.20, 0.25, 1, 0.02
C11_B_OUTLIER, C11_B_VIOLATIONS = 0.40, 3
C11_C_VIOLATIONS = 3             # canon C11 C band: "> 3 violations"

# ---- C21 restraint ---------------------------------------------------------
C21_S_AMBIENT, C21_A_AMBIENT, C21_C_AMBIENT = 1, 2, 3
C21_S_HERO_IN_FLIGHT, C21_A_HERO_IN_FLIGHT = 1, 2
C21_ONSETS_PER_10 = 1.0          # canon C21 C band, and canon section 8 item 11
C21_STAGGER_WINDOW_F30 = 15      # consecutive onsets no further apart than this
                                 # are candidates for ONE gesture. A
                                 # per-character sweep is canon 2.2's
                                 # prescription, not eleven separate onsets
C21_STAGGER_MIN = 3              # a run of at least this many, with ...
C21_STAGGER_STEP_CV = 0.50       # ... an even step and ...
C21_STAGGER_DUR_TOL = 0.25       # ... one duration, IS a stagger, and canon 2.2
                                 # asks for it. A run of the same length whose
                                 # members carry different durations is the
                                 # over-animation this criterion exists to catch
C21_MIN_BEAT_F30 = 20            # canon section 8 item 11 says "sustained across
                                 # a beat". Two thirds of a second is the floor
                                 # at which a per-10-frame rate is more than two
                                 # windows; below it, four onsets in a 0.65 s
                                 # dot bounce read as 1.03 and the row turns on
                                 # a coin flip
C21_MIN_GESTURES = 6             # below this the row is N/A, never S


# =============================================================================
# small shared helpers, named as in grade-mg.py
# =============================================================================

def clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


def fscale(frames_at_30, fps):
    """A frame count written for 30 fps, carried to the delivered rate."""
    return max(1, int(round(frames_at_30 * (float(fps) / 30.0))))


def smooth_box(a, w):
    a = np.asarray(a, dtype=float)
    if w <= 1 or len(a) < w:
        return a
    k = np.ones(w) / w
    pad = w // 2
    return np.convolve(np.pad(a, (pad, pad), mode="edge"), k, mode="valid")[:len(a)]


def rank_worst(pairs, n=6):
    """(severity, frame) pairs -> up to n frames, worst first, deduplicated.
    The frame a note names has to be the first frame the reader opens."""
    out, seen = [], set()
    for _, f in sorted(pairs, key=lambda p: -p[0]):
        f = int(f)
        if f in seen:
            continue
        seen.add(f)
        out.append(f)
        if len(out) >= n:
            break
    return out


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or len(x) != len(y):
        return float("nan")

    def rank(v):
        order = np.argsort(v, kind="mergesort")
        r = np.empty(len(v), float)
        r[order] = np.arange(len(v), dtype=float)
        # average ties, or three identical durations produce a rho from the
        # sort order alone
        _, start, count = np.unique(v[order], return_index=True, return_counts=True)
        for s, c in zip(start, count):
            if c > 1:
                r[order[s:s + c]] = r[order[s:s + c]].mean()
        return r

    rx, ry = rank(x), rank(y)
    sx, sy = rx.std(), ry.std()
    if sx == 0 or sy == 0:
        return float("nan")
    return float(((rx - rx.mean()) * (ry - ry.mean())).mean() / (sx * sy))


def _resample101(y):
    y = np.asarray(y, dtype=float)
    if len(y) < 2:
        return None
    return np.interp(np.linspace(0, 1, 101), np.linspace(0, 1, len(y)), y)


def _get(ctx, name, default=None):
    """ctx may be an object or a dict; the integrator picks."""
    if isinstance(ctx, dict):
        return ctx.get(name, default)
    return getattr(ctx, name, default)


def _row(cid, name, band, measured, worst=None, note="", basis="",
         na=False, declarations=None):
    return {
        "id": cid,
        "name": name,
        "band": None if na else band,
        "weight": WEIGHTS[cid],
        "na": bool(na),
        "measured": measured,
        # worst_frames arrives RANKED BY SEVERITY and is not re-sorted
        "worstFrames": [int(f) for f in (worst or [])][:6],
        "basis": basis,
        "note": note,
        "declarations": sorted(set(declarations or [])),
    }


def _register(ctx):
    src = _get(ctx, "src")
    man = _get(ctx, "manifest") or {}
    r = getattr(src, "register", None) or man.get("register") or DEFAULT_REGISTER
    return r if r in REGISTERS and r in C6_BUDGET else DEFAULT_REGISTER


def _fitted(ctx):
    f = _get(ctx, "fitted")
    if f is not None:
        return bool(f)
    src = _get(ctx, "src")
    return src is not None and getattr(src, "tweens", None) is None


def _declared_names(manifest, key):
    """The manifest entries under `key`, as printable claims. A declaration is
    a claim about intent and the report has to be able to show it as one."""
    v = (manifest or {}).get(key)
    if not v:
        return []
    if isinstance(v, dict):
        return [f"{key}:{k}={x}" for k, x in v.items()]
    out = []
    for item in v:
        if isinstance(item, (list, tuple)):
            out.append(f"{key}:[{','.join(str(i) for i in item)}]")
        else:
            out.append(f"{key}:{item}")
    return out


# =============================================================================
# channels and the compound move
# =============================================================================

def channel_of(props):
    """Which tracked channel a set of tween properties writes.

    translate and scale resolve to WORLD series (getBoundingClientRect), which
    is what canon C1 means by "nesting composes curves": the composed motion is
    the motion the viewer sees. rotation and opacity have no world witness in
    the probe and are read element-local; the row says so.

    Untracked properties (clip-path, filter, colour) return None. A clip-path
    wipe has no geometry in the rect and must not be classified from whatever
    unrelated tween happened to overlap its window, which is how a power2.out
    clip reveal was reported as an ease-in.
    """
    ps = set(props or [])
    if ps & TRANSLATE_PROPS:
        return "translate"
    if ps & SCALE_PROPS:
        return "scale"
    if ps & ROTATE_PROPS:
        return "rotation"
    if ps & {"opacity", "autoAlpha"}:
        return "opacity"
    return None


def scale_axis(props):
    """(rect series name, local witness prop) for a scale tween.

    A `scaleY: 0 -> 1` bar grows in HEIGHT. Taking whichever of w and h moved
    most read the WIDTH instead, which on a bar inside a parent that is itself
    scaling is the parent's curve with the child's name on it: measured on
    systo-26s as a 17.5 % overshoot on a sine.out that has none.
    """
    ps = set(props or [])
    if ps & {"scaleY", "height"}:
        return "h", "scaleY"
    if ps & {"scaleX", "width"}:
        return "w", "scaleX"
    return None, "scale"


def channel_series(src, el, ch, a, b, ref=None, axes=None):
    """The series of one channel on one element over [a, b], world where the
    probe gives world.

    Returns (series, travel) or (None, 0.0). `ref`, when given, is another
    element index whose motion is subtracted (translate) or divided out
    (scale): the relative-geometry branch of the contention rule.
    """
    n = int(getattr(src, "frames", 0))
    a = int(clamp(a, 0, n - 1))
    b = int(clamp(b, 0, n - 1))
    if b <= a:
        return None, 0.0
    if ch == "translate":
        cx = np.asarray(src.prop(el, "cx")[a:b + 1], float)
        cy = np.asarray(src.prop(el, "cy")[a:b + 1], float)
        if ref is not None and ref >= 0:
            cx = cx - np.asarray(src.prop(ref, "cx")[a:b + 1], float)
            cy = cy - np.asarray(src.prop(ref, "cy")[a:b + 1], float)
        dx, dy = cx[-1] - cx[0], cy[-1] - cy[0]
        tot = math.hypot(dx, dy)
        if tot < C1_MIN_TRAVEL_PX:
            return None, 0.0
        # a scalar progress projected on the chord, never a bounding-box
        # coordinate read on its own
        return ((cx - cx[0]) * dx + (cy - cy[0]) * dy) / (tot * tot), tot
    if ch == "scale":
        w = np.asarray(src.prop(el, "w")[a:b + 1], float)
        h = np.asarray(src.prop(el, "h")[a:b + 1], float)
        if ref is not None and ref >= 0:
            rw = np.asarray(src.prop(ref, "w")[a:b + 1], float)
            rh = np.asarray(src.prop(ref, "h")[a:b + 1], float)
            w = w / np.maximum(rw / max(rw[0], 1e-6), 1e-6)
            h = h / np.maximum(rh / max(rh[0], 1e-6), 1e-6)
        want, witness = scale_axis(axes)
        try:
            loc = np.asarray(src.prop(el, witness)[a:b + 1], float)
        except (KeyError, IndexError):
            loc = np.asarray(src.prop(el, "scale")[a:b + 1], float)
        cands = []
        for name, s in (("w", w), ("h", h)):
            if want is not None and name != want:
                continue
            if s.min() <= 0:
                continue                    # a zero-size rect is rejected, not
                                            # believed: display:none, a hidden
                                            # wrapper, a font that has not loaded
            base = max(abs(s[0]), abs(s[-1]), 1e-6)
            rel = abs(s[-1] - s[0]) / base
            if rel >= C1_MIN_TRAVEL_SCALE:
                cands.append((rel, s))
        if cands:
            _, s = max(cands, key=lambda c: c[0])
            # the rect is a composed witness for scale ONLY when nothing else
            # deforms it. Rotation, a reflow or a clip on the same element make
            # the axis-aligned box grow by a different factor, and the box then
            # measures the wrong thing with total confidence
            agree = True
            if abs(loc[-1] - loc[0]) >= C1_MIN_TRAVEL_SCALE and loc[0] > 0 \
                    and loc[-1] > 0 and s[0] > 0 and s[-1] > 0:
                r_rect = float(s[-1] / s[0])
                r_loc = float(loc[-1] / loc[0])
                agree = abs(math.log(max(r_rect, 1e-9)) - math.log(max(r_loc, 1e-9))) \
                    <= math.log(1.0 + C1_SCALE_RECT_TOL)
            if agree:
                return (s - s[0]) / (s[-1] - s[0]), abs(float(s[-1] - s[0]))
        # the rect is degenerate or disagrees: fall back to the element's own
        # transform, which is local but is not a different quantity
        s = loc
        if ref is not None and ref >= 0:
            try:
                rl = np.asarray(src.prop(ref, witness)[a:b + 1], float)
                s = s / np.maximum(rl / max(rl[0], 1e-6), 1e-6)
            except (KeyError, IndexError):
                pass
        if abs(s[-1] - s[0]) < C1_MIN_TRAVEL_SCALE:
            return None, 0.0
        return (s - s[0]) / (s[-1] - s[0]), abs(float(s[-1] - s[0]))
    if ch == "rotation":
        s = np.asarray(src.prop(el, "rotation")[a:b + 1], float)
        if abs(s[-1] - s[0]) < C1_MIN_TRAVEL_ROT:
            return None, 0.0
        return (s - s[0]) / (s[-1] - s[0]), abs(float(s[-1] - s[0]))
    if ch == "opacity":
        s = np.asarray(src.prop(el, "opacity")[a:b + 1], float)
        if abs(s[-1] - s[0]) < C1_MIN_TRAVEL_OPACITY:
            return None, 0.0
        return (s - s[0]) / (s[-1] - s[0]), abs(float(s[-1] - s[0]))
    return None, 0.0


_ANCHOR_EPS = {"translate": 0.5, "scale": 1e-3, "rotation": 0.05, "opacity": 1e-3}


def _channel_point(src, el, ch, f):
    f = int(clamp(f, 0, src.frames - 1))
    if ch == "translate":
        return (float(src.prop(el, "cx")[f]), float(src.prop(el, "cy")[f]))
    if ch == "scale":
        return float(src.prop(el, "scale")[f])
    if ch == "rotation":
        return float(src.prop(el, "rotation")[f])
    return float(src.prop(el, "opacity")[f])


def _channel_step(ch, p, q):
    if ch == "translate":
        return math.hypot(p[0] - q[0], p[1] - q[1])
    return abs(p - q)


def anchor_window(src, el, ch, a, b, back):
    """Widen [a, b] by up to `back` frames at each end to recover the move's
    true FROM and TO states.

    Frame windows are biased INWARD, which is right for ownership and wrong for
    endpoints: a tween starting at 16.266667 s at 30 fps computes to frame
    488.00001 and rounds to 489, so the first frame of travel lands outside the
    window.  Canon's overshoot is (peak - target) / (target - START), so a lost
    start frame inflates every overshoot on that move -- measured on higgsfield
    at 11 % reported as 27 %.  Only a frame that is STATIONARY on the far side
    is taken, so a chained move never annexes its neighbour's travel.
    """
    eps = _ANCHOR_EPS.get(ch, 1e-3)
    for _ in range(max(int(back), 0)):
        if a < 2:
            break
        if _channel_step(ch, _channel_point(src, el, ch, a),
                         _channel_point(src, el, ch, a - 1)) > eps \
                and _channel_step(ch, _channel_point(src, el, ch, a - 1),
                                  _channel_point(src, el, ch, a - 2)) <= eps:
            a -= 1
        else:
            break
    for _ in range(max(int(back), 0)):
        if b > src.frames - 3:
            break
        if _channel_step(ch, _channel_point(src, el, ch, b + 1),
                         _channel_point(src, el, ch, b)) > eps \
                and _channel_step(ch, _channel_point(src, el, ch, b + 2),
                                  _channel_point(src, el, ch, b + 1)) <= eps:
            b += 1
        else:
            break
    return a, b


def ancestors(src, el, f=0):
    """Element indices above `el`.

    Prefers the probe's own parent chain, and falls back to rect containment at
    frame f when the probe predates it. Containment is the practical ancestor
    test and needs no DOM.
    """
    out = []
    try:
        cur = src.elements[el].get("parent", -1)
    except Exception:
        cur = -1
    if cur is not None and cur >= 0:
        seen = set()
        while cur is not None and cur >= 0 and cur not in seen:
            seen.add(cur)
            out.append(int(cur))
            try:
                cur = src.elements[cur].get("parent", -1)
            except Exception:
                break
        return out
    try:
        x0, y0, x1, y1 = src.box_at(el, f)
    except Exception:
        return out
    if x1 <= x0 or y1 <= y0:
        return out
    try:
        my_clip = src.elements[el].get("clip")
    except (IndexError, KeyError, AttributeError, TypeError):
        return out
    for e in src.elements:
        i = e["i"]
        if i == el or e.get("clip") != my_clip:
            continue
        try:
            a0, b0, a1, b1 = src.box_at(i, f)
        except Exception:
            continue
        if a1 - a0 <= 0 or b1 - b0 <= 0:
            continue
        if a0 <= x0 + 1 and b0 <= y0 + 1 and a1 >= x1 - 1 and b1 >= y1 - 1 \
                and (a1 - a0) * (b1 - b0) > (x1 - x0) * (y1 - y0):
            out.append(int(i))
    return out


def classify(samples):
    """The ease CLASS of a normalised progress curve, from its geometry alone.

    Order matters and is canon's: overshoot FIRST, or every back.out files as
    an out and overshootShare reads zero. Then linear, which needs BOTH a flat
    speed profile and quarters on the diagonal, because the quarters alone
    misread a composed curve. Then direction, from the CENTROID of the speed
    profile: power1.out 0.33, power4.out 0.17, sine.out 0.36, sine.in 0.64, and
    every symmetric inOut exactly 0.50, so a knife-edge midpoint no longer
    flips a circ.inOut into an in.

    Returns one of: overshoot, linear, stutter, outIn, out, in, inOut, custom.
    """
    s = np.asarray(samples, dtype=float)
    if len(s) < 5 or not np.isfinite(s).all():
        return "custom"
    if float(s.max()) > 1.0 + C1_OVERSHOOT_PEAK:
        return "overshoot"
    sm = smooth_box(s, MOTION_SMOOTH)
    d = np.diff(sm)
    a = np.abs(d)
    tot = float(a.sum())
    if tot <= 1e-9:
        return "custom"
    q1, q2, q3 = float(s[25]), float(s[50]), float(s[75])
    mean = tot / len(a)
    cv = float(a.std() / mean) if mean > 0 else 0.0
    quarters_linear = (abs(q1 - 0.25) < C1_LINEAR_TOL
                       and abs(q2 - 0.5) < C1_LINEAR_TOL
                       and abs(q3 - 0.75) < C1_LINEAR_TOL)
    if quarters_linear and cv < C1_LINEAR_CV:
        return "linear"
    raw = np.abs(np.diff(s))
    if quarters_linear and raw.max() > 0 \
            and float((raw <= raw.max() * 0.02).mean()) > C1_STUTTER_ZERO_SHARE:
        # a layout-property tween snapping to whole pixels: linear on the
        # quarters, a 0,0,1,0,0,1 step pattern in between (canon section 8, 8)
        return "stutter"
    u = (np.arange(len(a)) + 0.5) / len(a)
    tau = float((a * u).sum() / tot)
    third = len(a) // 3
    if third >= 2:
        mid = float(a[third:2 * third].mean())
        ends = float(np.concatenate([a[:third], a[2 * third:]]).mean())
        if ends > 0 and mid / ends < C1_OUTIN_DIP and 0.40 <= tau <= 0.60:
            # fast, dead stop, fast: two tweens chained through a velocity zero,
            # which is the junction canon 1.2 says to author as one curve
            return "outIn"
    if tau <= C1_OUT_TAU:
        return "out"
    if tau >= C1_IN_TAU:
        return "in"
    return "inOut"


def _junction_step(series, boundaries, win):
    """The worst velocity STEP at a chained leg boundary, or None.

    Canon 1.2: "One curve, not two tweens. Chaining power2.inOut into
    power3.out puts a velocity step at the junction." Measured on systo-26s, a
    power3.in handing over to a sine.inOut drops from 8.73 px per frame to
    0.16 in one frame while still travelling the same way: the element
    decelerates to a dead stop mid-move and restarts, which is the hitch the
    principle exists to forbid and which no direction test can see.

    Returns (boundary index in the window, speed before, speed after) for the
    worst offender, or None when every junction is continuous.
    """
    s = np.asarray(series, float)
    d = np.abs(np.diff(s))
    sign = np.sign(np.diff(s))
    if len(d) < 2 * win + 2:
        return None
    worst = None
    for k in boundaries:
        lo, hi = k - win, k + win
        if lo < 0 or hi >= len(d):
            continue
        before = float(d[lo:k].mean()) if k > lo else float(d[max(k - 1, 0)])
        after = float(d[k:hi].mean()) if hi > k else float(d[k])
        if before <= 1e-9:
            continue
        # only a step in the SAME direction is a hitch; a reversal is a round
        # trip or an anticipation and is graded elsewhere
        sb = np.sign(sign[lo:k]).sum()
        sa = np.sign(sign[k:hi]).sum()
        if sb * sa <= 0:
            continue
        ratio = after / before
        if ratio < C1_JUNCTION_RATIO or (ratio > 0 and 1.0 / ratio < C1_JUNCTION_RATIO):
            if worst is None or abs(math.log(max(ratio, 1e-9))) > \
                    abs(math.log(max(worst[3], 1e-9))):
                worst = (int(k), before, after, ratio)
    return worst


def _rest_distance(src, el, f, box_h):
    """How far from its layout rest pose the element sits at frame f. Rest is
    translate 0 and scale 1 in the element's own transform."""
    f = int(clamp(f, 0, src.frames - 1))
    d = 0.0
    for p in ("x", "y"):
        try:
            d += abs(float(src.prop(el, p)[f]))
        except Exception:
            pass
    try:
        d += abs(float(src.prop(el, "scale")[f]) - 1.0) * max(box_h, 1.0)
    except Exception:
        pass
    return d


def _boundary_frame(src, el, onset_f, cuts):
    """The frame this move's card ends on: the element's clip end when the
    source knows it, otherwise the next cut after its onset."""
    c = None
    try:
        c = src.clip_of(el)
    except Exception:
        c = None
    if c:
        return int(math.floor((c["start"] + c["duration"]) * src.fps - 1e-6))
    nxt = [x for x in (cuts or []) if x > onset_f]
    return int(nxt[0] - 1) if nxt else int(src.frames - 1)


def compound_moves(ctx):
    """Consecutive tweens on ONE element writing ONE channel, chained into one
    move, then measured and classified as one curve.

    Three tweens that hand x from 113 to 135 to 68 to 0 are one slide with a
    22 px wind-up, not three moves of which two "read backwards". Grading each
    leg alone charged the wind-up and the acceleration half as two separate
    direction violations on a film that is doing exactly what canon 1.2 asks.

    Each compound carries: el, key, clip, ch, legs, startF, endF, onsetF,
    settleF, durF, dur, ease, role, class, samples, travel, net, path,
    roundTrip, anticipation, basis, seen, boundaryF, transition, ambient,
    mechanical, impact, loop, spatial, paint, dist, scaleDelta.
    """
    src = _get(ctx, "src")
    if src is None:
        return []
    fps = float(_get(ctx, "fps", getattr(src, "fps", 30.0)))
    cuts = _get(ctx, "cuts") or []
    gap = fscale(C1_CHAIN_GAP_F30, fps)
    tail = fscale(C1_DEPART_TAIL_F30, fps)
    jwin = fscale(C1_JUNCTION_WIN_F30, fps)
    anchor = fscale(C1_ANCHOR_BACK_F30, fps)
    W, H = float(src.W), float(src.H)

    buckets = {}
    for mv in src.moves:
        if mv.get("kind") not in ("spatial", "micro"):
            continue
        if mv.get("dur", 0) <= 1e-9 or mv["endF"] <= mv["startF"]:
            continue          # a gsap.set is a state write, not a move, and
                              # chaining one in front of a tween shifts the
                              # measured window by a frame and the class with it
        ch = channel_of(mv.get("spatial") or mv.get("props"))
        # bucket by the AXES the tween writes, not only by channel: an x slide
        # and a y lift-out on the same element are two gestures that happen to
        # overlap, and merging them into one compound turned an entrance and a
        # departure into a single outIn
        axes = tuple(sorted(p for p in (mv.get("spatial") or [])
                            if channel_of([p]) == ch))
        buckets.setdefault((mv["el"], ch, axes), []).append(mv)

    out = []
    for (el, ch, axes), legs in buckets.items():
        legs = sorted(legs, key=lambda m: (m["startF"], m["endF"]))
        chains, cur = [], [legs[0]]
        for m in legs[1:]:
            # A declared mechanical leg is its own move and never chains with a
            # graded one. Canon calls a camera drift, a conveyor and an idle
            # push mechanical because they are CONTINUOUS; the arrival that
            # follows one on the same element and the same channel is a
            # separate gesture with its own ease, and merging the two produced
            # a compound that was neither: an idle ramp at ease "none" chained
            # to an expo.in exit read as a "reposition in" and was charged as a
            # backwards direction on the film's own idle push.
            same_kind = bool(m.get("mechanical")) == bool(cur[-1].get("mechanical"))
            if same_kind and m["startF"] - cur[-1]["endF"] <= gap:
                cur.append(m)
            else:
                chains.append(cur)
                cur = [m]
        chains.append(cur)
        for chain in chains:
            out.append(_build_compound(src, el, ch, axes, chain, cuts, W, H, tail, jwin, anchor))
    out.sort(key=lambda c: (c["startF"], c["key"]))
    return out


def _build_compound(src, el, ch, axes, chain, cuts, W, H, tail, jwin, anchor):
    first, last = chain[0], chain[-1]
    a, b = int(first["startF"]), int(last["endF"])
    man = getattr(src, "manifest", None) or {}
    cm = {
        "el": el, "key": first["key"], "clip": first.get("clip"), "ch": ch,
        "legs": len(chain), "tweens": [m.get("tween") for m in chain],
        "startF": a, "endF": b, "onsetF": int(first["onsetF"]),
        "settleF": int(last["settleF"]), "durF": max(b - a, 1),
        "dur": float(sum(m["dur"] for m in chain)),
        "ease": " -> ".join(str(m.get("ease", "none")) for m in chain),
        "spatial": sorted({p for m in chain for p in (m.get("spatial") or [])}),
        "paint": sorted({p for m in chain for p in (m.get("paint") or [])}),
        "repeat": any(m.get("repeat") for m in chain),
        # ALL legs, not any: a compound built from a declared idle ramp plus a
        # real arrival is not a mechanical move, and the arrival is the thing
        # C1 grades. `mechanical` is already scoped to the constant-velocity
        # tween on the named element (Source.apply_manifest).
        "mechanical": all(m.get("mechanical") for m in chain),
        "impact": any(m.get("impact") for m in chain),
        "organic": any(m.get("organic") for m in chain),
        "ambient": all(m.get("ambient") for m in chain),
        "dist": float(math.hypot(last["cxTo"] - first["cxFrom"],
                                 last["cyTo"] - first["cyFrom"])),
        "scaleDelta": abs(float(last["scaleTo"] - first["scaleFrom"])),
        "opFrom": float(first["opFrom"]), "opTo": float(last["opTo"]),
        "scaleFrom": float(first["scaleFrom"]), "scaleTo": float(last["scaleTo"]),
        "cxFrom": float(first["cxFrom"]), "cyFrom": float(first["cyFrom"]),
        "cxTo": float(last["cxTo"]), "cyTo": float(last["cyTo"]),
        "boxH": float(last.get("boxH", 0.0)), "boxW": float(last.get("boxW", 0.0)),
        # the AUTHORED curves, one per leg. C1 must not read these -- canon says
        # classify from measured geometry -- but C2 counts the author's
        # VOCABULARY, and a composed world curve carries the parent's shape and
        # the rect's quantisation into a count of what the author chose
        "easeSamples": [np.asarray(m["easeSamples"], float) for m in chain
                        if m.get("easeSamples") is not None],
        "easeNames": [str(m.get("ease", "none")) for m in chain],
    }
    try:
        named_loop = src.is_named(el, set(man.get("loops", []) or []))
    except Exception:
        named_loop = False
    cm["loop"] = bool(cm["repeat"]) or bool(named_loop)

    # ---- transition by class (canon 5): a whip, a wipe, a card flying through
    cm["transition"] = bool(
        cm["impact"]
        or abs(cm["cxTo"] - cm["cxFrom"]) >= C1_TRANSITION_TRAVEL * W
        or abs(cm["cyTo"] - cm["cyFrom"]) >= C1_TRANSITION_TRAVEL * H
        or cm["scaleDelta"] >= C1_TRANSITION_SCALE)

    # ---- the measured curve, on the channel this move actually writes -------
    cm["samples"], cm["basis"], cm["travel"] = None, "none", 0.0
    cm["net"], cm["path"], cm["roundTrip"], cm["anticipation"] = 0.0, 0.0, False, 0.0
    cm["junction"] = None
    cm["anchorF"] = (a, b)
    if ch is None:
        cm["class"], cm["basis"] = "unclassified", "untracked-property"
    elif b - a + 1 < SHAPE_MIN_FRAMES:
        cm["class"], cm["basis"] = "unclassified", "too-short"
    else:
        a, b = anchor_window(src, el, ch, a, b, anchor)
        cm["anchorF"] = (a, b)
        ref, overlap = _contending_ancestor(src, el, ch, a, b)
        if overlap == "camera-cross":
            series = None
        else:
            series, travel = channel_series(
                src, el, ch, a, b,
                ref=(ref if overlap == "partial" else None), axes=axes)
        if overlap == "camera-cross":
            cm["class"], cm["basis"] = "unclassified", "camera-composed"
        elif series is None:
            cm["class"], cm["basis"] = "unclassified", "no-travel"
        else:
            raw = np.asarray(series, float)
            sm = smooth_box(raw, MOTION_SMOOTH)
            path = float(np.abs(np.diff(sm)).sum())
            net = abs(float(sm[-1] - sm[0]))
            cm["net"], cm["path"] = net, path
            # A round trip RETURNS: it ends within a small fraction of its own
            # path length of where it started. Testing net/path alone is
            # self-defeating on a settle, because net/path FALLS as a settle
            # oscillates more, so the bigger the wobble the more certainly it
            # was exempted -- an elastic.out(1.4, 0.35) settle overshooting
            # 59.5 % of travel with five reversals, built as a negative control
            # for C6, was classified a round trip and skipped by C1 and C6 both.
            span_all = abs(float(sm[-1] - sm[0]))
            cm["roundTrip"] = bool(path > 0 and (net / path) < C1_ROUNDTRIP_NET
                                   and span_all <= C1_ROUNDTRIP_RETURN * path)
            # strip a leading counter-run. Canon 1.2 calls a run opposite to the
            # main travel immediately before it ANTICIPATION, in the band
            # 0.08-0.20 of travel; charging it as a backwards ease is the
            # criterion punishing the principle it exists to reward.
            start_i = 0
            if not cm["roundTrip"] and len(chain) > 1:
                sign = math.copysign(1.0, sm[-1] - sm[0])
                k = int(chain[0]["endF"] - a)
                if 0 < k < len(sm) - 2:
                    leg = float(sm[k] - sm[0])
                    if leg * sign < 0 and abs(leg) <= C1_ANTIC_FRAC * max(net, 1e-9):
                        start_i = k
                        cm["anticipation"] = abs(leg) / max(net, 1e-9)
            cm["junction"] = _junction_step(
                raw, [int(m["endF"] - a) for m in chain[:-1]], jwin)
            seg = raw[start_i:]
            span = float(seg[-1] - seg[0])
            if len(seg) >= SHAPE_MIN_FRAMES and abs(span) > 1e-9:
                cm["samples"] = _resample101((seg - seg[0]) / span)
                cm["travel"] = travel
                cm["basis"] = ("measured-world" if overlap != "partial"
                               else "measured-relative")
                cm["class"] = classify(cm["samples"])
            else:
                cm["class"], cm["basis"] = "unclassified", "no-travel"

    # ---- role: entrance, departure, reposition -----------------------------
    cm["role"] = _compound_role(src, cm, chain, cuts, tail, W, H)

    # ---- seen: is the terminal ease ever rendered? -------------------------
    bnd = _boundary_frame(src, el, cm["onsetF"], cuts)
    cm["boundaryF"] = bnd
    if cm["samples"] is None or bnd >= b:
        cm["seen"] = 1.0
    else:
        p = clamp((bnd - cm["startF"]) / max(b - cm["startF"], 1), 0.0, 1.0)
        cm["seen"] = float(np.asarray(cm["samples"])[int(round(p * 100))])
    return cm


def _contending_ancestor(src, el, ch, a, b):
    """(ancestor index, "full" | "partial" | "none") for the ancestor whose own
    tween writes this channel inside this window.

    FULL overlap is COMPOSITION and the world curve is the curve the viewer
    sees: canon C1's own example, a child at ease "none" inside a power2.out
    parent, is not linear on screen and must not be charged as linear.
    PARTIAL overlap is two SEQUENTIAL events sharing a window -- a masked word
    rising on expo.out while, half way through, the card it sits in whips out on
    expo.in -- and the child is measured relative to that ancestor, or the
    card's exit is charged to the word.
    """
    span = max(b - a + 1, 1)
    best, best_frac, best_coterm, best_mv = -1, 0.0, 0.0, None
    W, H = float(src.W), float(src.H)
    ancs = set(ancestors(src, el, a))
    if not ancs:
        return -1, "none"
    for mv in getattr(src, "moves", []):
        if mv["el"] not in ancs or mv.get("kind") not in ("spatial", "micro"):
            continue
        if mv.get("dur", 0) <= 1e-9:
            continue
        anc_ch = channel_of(mv.get("spatial") or mv.get("props"))
        # A SCALE or ROTATE on an ancestor writes a descendant's world
        # TRANSLATE: scaling about an origin that is not the child's own centre
        # moves that centre, and the rect is the only witness this module has.
        # Restricting the contention test to the same channel name missed it,
        # and an avatar pill rising on power3.out inside a field pushing in on
        # power2.in over 72 frames measured dead linear on screen -- one
        # composition reported fifteen direction violations that way. The
        # converse does not hold: an ancestor translating does not change a
        # child's scale, so the asymmetry is deliberate.
        if anc_ch != ch and not (ch == "translate" and anc_ch in ("scale", "rotate")):
            continue
        lo, hi = max(a, mv["startF"]), min(b, mv["endF"])
        if hi <= lo:
            continue
        frac = (hi - lo + 1) / span
        if frac > best_frac:
            best, best_frac, best_mv = mv["el"], frac, mv
            best_coterm = span / max(mv["endF"] - mv["startF"] + 1, 1)
    if best_mv is not None and best_frac >= C1_CONTEND_FULL \
            and _is_field_move(best_mv, W, H) \
            and channel_of(best_mv.get("spatial") or best_mv.get("props")) != ch:
        # A camera SCALING about an origin that is not the child's own centre
        # writes the child's world TRANSLATE as a multiplication, not as an
        # offset, so the child's own curve is recoverable neither from the world
        # series nor by subtracting the ancestor's: six pills rising 22 px
        # inside a field zooming 0.62 to 5.4 have no measurable local ease in a
        # world rect at all. That is C1's own "moves whose channel leaves no
        # geometry in the rect" case, and the honest report is unmeasurable
        # rather than a violation asserted from a curve that belongs to the
        # camera. The test is on coverage alone: a camera does not have to be
        # coterminous with the child to own the child's world path.
        return best, "camera-cross"
    if best_frac >= C1_CONTEND_FULL and best_coterm >= C1_CONTEND_COTERM:
        # ... unless the ancestor is a CAMERA. A whip, a wipe, an infinite zoom
        # or a declared idle push is a move of the FIELD, and canon 5 exempts
        # the first three by class while the manifest names the fourth. The
        # child inside it is read against that field, not against the frame:
        # canon 1.6 makes the same point from the other end when it says a move
        # cut into mid-flight is judged on being in motion at the boundary. Six
        # avatar pills rising on power3.out inside a field zooming 0.62 to 5.4
        # measured inOut on screen and were charged as backwards arrivals; the
        # composition every viewer sees there is pill-inside-zoom, and the pill
        # is what C1 is grading.
        if best_mv is not None and _is_camera(src, best_mv, W, H):
            return best, "partial"
        return best, "full"
    if best_frac > 0:
        return best, "partial"
    return -1, "none"


def _is_field_move(mv, W, H):
    """A canon-5 transition BY CLASS on its own geometry: a whip, a wipe, a card
    flying through frame or an infinite zoom. Deliberately NOT the declared
    mechanical idle push, which moves a child's world path by 4 % and must not
    buy its children an exemption; `mechanical` is a claim about one element's
    own tween and is scoped there."""
    if abs(mv.get("dx", 0.0)) >= C1_TRANSITION_TRAVEL * W \
            or abs(mv.get("dy", 0.0)) >= C1_TRANSITION_TRAVEL * H:
        return True
    return mv.get("scaleDelta", 0.0) >= C1_TRANSITION_SCALE


def _is_camera(src, mv, W, H):
    """Is this ancestor move a camera: a transition by class (canon 5) or a
    declared mechanical push. The three canon-5 tests are the same three
    `compound_moves` uses for its own `transition` flag, applied to a raw
    move."""
    if src.is_mechanical(mv["el"]) or mv.get("mechanical"):
        return True
    if mv.get("impact"):
        return True
    if abs(mv.get("dx", 0.0)) >= C1_TRANSITION_TRAVEL * W \
            or abs(mv.get("dy", 0.0)) >= C1_TRANSITION_TRAVEL * H:
        return True
    return mv.get("scaleDelta", 0.0) >= C1_TRANSITION_SCALE


def _compound_role(src, cm, chain, cuts, tail, W, H):
    """entrance, departure or reposition.

    The four classic tests, plus the one the old code lacked: an element's LAST
    spatial move, ending on its card's last frames and travelling AWAY from its
    layout rest pose, is a departure however its opacity behaves. A headline
    that leaves by growing to 1.74 and cutting is a departure, and expo.in is
    the correct ease for one; grading it as a reposition made "accelerate away"
    a direction violation on every card in the film.
    """
    if cm["opFrom"] < 0.05 and cm["opTo"] > 0.5:
        return "entrance"
    if cm["opTo"] < 0.05 and cm["opFrom"] > 0.5:
        return "departure"
    if cm["scaleFrom"] < 0.02 <= cm["scaleTo"]:
        return "entrance"
    if cm["scaleTo"] < 0.02 <= cm["scaleFrom"]:
        return "departure"

    def outside(x, y):
        return x < 0 or y < 0 or x > W or y > H

    if outside(cm["cxFrom"], cm["cyFrom"]) and not outside(cm["cxTo"], cm["cyTo"]):
        return "entrance"
    if outside(cm["cxTo"], cm["cyTo"]) and not outside(cm["cxFrom"], cm["cyFrom"]):
        return "departure"
    # a translate that resolves TO the element's rest position is an entrance:
    # the masked word rise, where opacity never changes and the glyph never
    # leaves the frame, which C1 could not otherwise see a backwards ease on
    for m in chain:
        for p in (m.get("spatial") or []):
            if p not in TRANSLATE_PROPS:
                continue
            f0 = (m.get("startAt") or {}).get(p)
            f1 = (m.get("to") or {}).get(p)
            if f0 is None or f1 is None:
                continue
            if abs(f0) > 1e-6 and abs(f1) < 1e-6:
                return "entrance"
    # opacity folded into the motion on a SEPARATE tween. Three dots that lift
    # 64 px on power2.in while an overlapping autoAlpha 1 -> 0 fades them are
    # departing, and power2.in is the right ease for a departure. Reading the
    # element's opacity only at the move's own end frames misses it, because the
    # fade is still running when the lift settles.
    for mv in src.moves:
        if mv["el"] != cm["el"] or mv.get("kind") != "paint":
            continue
        if mv["endF"] <= cm["startF"] or mv["startF"] >= cm["endF"] + cm["durF"]:
            continue
        if mv.get("opTo", 1.0) < 0.05 <= mv.get("opFrom", 0.0):
            return "departure"
        if mv.get("opFrom", 1.0) < 0.05 <= mv.get("opTo", 0.0):
            return "entrance"
    # the element's last spatial move across ALL channels, not only its own
    # bucket: a card that shrinks to 0.81 across its whole life and then lifts
    # out on y is repositioning on scale and departing on y, and charging the
    # shrink as a departure asked a slow recede to accelerate away
    later = [x for x in src.moves
             if x["el"] == cm["el"] and x.get("kind") == "spatial"
             and x.get("dur", 0) > 1e-9 and x["endF"] > cm["endF"]]
    if not later:
        bnd = _boundary_frame(src, cm["el"], cm["onsetF"], cuts)
        if cm["endF"] >= bnd - tail:
            to_rest = _rest_distance(src, cm["el"], cm["endF"], cm["boxH"])
            from_rest = _rest_distance(src, cm["el"], cm["startF"], cm["boxH"])
            if to_rest > from_rest:
                return "departure"
            # ... and the same move on SCALE. This function's own docstring
            # already names the case -- "a headline that leaves by growing to
            # 1.74 and cutting is a departure" -- and the test above cannot see
            # it, because a scale about the element's own origin moves no
            # centroid, so to_rest equals from_rest to the pixel. A last move
            # that ends on its card's last frame further from unity scale than
            # it started is a slam out or a sink away, and canon 1.6's `.in` on
            # departures is the correct ease for both. Grading it as a
            # reposition -- which by this function's own definition "ENDS AT
            # REST", and this one never does, because the cut takes it -- made
            # "accelerate away" a direction violation on the exit of a card.
            sf, st = cm.get("scaleFrom"), cm.get("scaleTo")
            if sf is not None and st is not None:
                if abs(st - 1.0) - abs(sf - 1.0) > C1_DEPART_SCALE:
                    return "departure"
    return "reposition"


def move_role_class(src, cm, hero_els):
    """hero / exit / ambient / support, for C2's per-role consistency test."""
    if cm["ambient"] or cm["mechanical"] or cm["loop"]:
        return "ambient"
    if cm["role"] == "departure":
        return "exit"
    if cm["el"] in hero_els:
        return "hero"
    return "support"


def shape_clusters(samples_list, radius):
    """Cluster (s(.25), s(.5), s(.75), peak overshoot) at `radius`.

    Canon C2: on screen power2.out and power3.out differ by two frames of
    settle and do not read as two characters, so SHAPE is what a viewer can
    count and a family name is not. A name-based count is inflatable by an
    author who does nothing, and a piece built with hand-shaped speed graphs
    reports one family and scores C.
    """
    cents, counts, idx = [], [], []
    for s in samples_list:
        s = np.asarray(s, float)
        q = np.array([s[25], s[50], s[75], max(0.0, float(s.max()) - 1.0)])
        hit = None
        for ci, c in enumerate(cents):
            if float(np.linalg.norm(q - c)) <= radius:
                hit = ci
                break
        if hit is None:
            cents.append(q)
            counts.append(1)
            hit = len(cents) - 1
        else:
            cents[hit] = (cents[hit] * counts[hit] + q) / (counts[hit] + 1)
            counts[hit] += 1
        idx.append(hit)
    return idx, counts


def hero_elements(ctx):
    """Element indices carrying a hero move. Uses ctx.heroes when the
    integrator supplies it, so C2, C10 and C21 cannot disagree with C8."""
    heroes = _get(ctx, "heroes")
    if heroes:
        return {int(h["el"]) for h in heroes}
    src, beats = _get(ctx, "src"), (_get(ctx, "beats") or [])
    if src is None:
        return set()
    named = (getattr(src, "manifest", None) or {}).get("hero", {}) or {}
    out = set()
    for bi, (a, b) in enumerate(beats):
        cand = [m for m in src.moves
                if a <= m["onsetF"] <= b and m.get("kind") == "spatial"]
        if not cand:
            continue
        want = named.get(str(bi)) or named.get(str(bi + 1))
        if want:
            hit = [m for m in cand if src.is_named(m["el"], {want})]
            if hit:
                out.add(int(max(hit, key=lambda m: m["dist"])["el"]))
                continue

        def area(m):
            f = int(clamp(m["settleF"], 0, src.frames - 1))
            x0, y0, x1, y1 = src.box_at(m["el"], f)
            return max(x1 - x0, 0.0) * max(y1 - y0, 0.0)

        out.add(int(max(cand, key=area)["el"]))
    return out


def graded_compounds(ctx, compounds=None):
    """Compounds that can carry a shape at all: not repeating, long enough to
    hold two intermediate samples, on a tracked channel with real travel."""
    cs = compounds if compounds is not None else compound_moves(ctx)
    return [c for c in cs if not c["repeat"] and c["samples"] is not None]


# =============================================================================
# C1  ease discipline                                                weight 2
# =============================================================================

def c1_ease_discipline(ctx):
    """Canon C1.  Classify from MEASURED GEOMETRY, not the parsed ease, because
    nesting composes curves; test overshoot FIRST or every back.out files as an
    out.

    S  0 linear on non-mechanical spatial moves, 0 direction violations
    C  any linear spatial move, or > 15 % direction violations

    Direction rules, canon 1.6: `.out` on arrivals, `.in` on departures,
    `.inOut` between positions.  Exempt, in canon's own words plus the classes
    canon names elsewhere: small recedes (< 5 % scale and < 3 % of frame
    height), auto-classified ambient (>= 2 s and < 5 % travel), declared
    mechanical elements, transitions by class (canon 5), round trips, and moves
    whose channel leaves no geometry in the rect.  A move cut before it settles
    keeps the linear test and loses the direction test: canon 1.6 says a move
    cut into or out of mid-flight is judged on being in motion at the boundary,
    and its terminal ease is never rendered.

    An input that still scores C: one 400 px headline slide authored
    `ease: "none"` and not declared mechanical.  One measurably linear spatial
    move is a C on its own.  So is a piece where more than 15 % of graded moves
    arrive on an ease-in, or stutter, or stop dead in the middle of a compound.
    """
    src = _get(ctx, "src")
    man = _get(ctx, "manifest") or {}
    fitted = _fitted(ctx)
    if src is None:
        return _row("C1", "ease discipline", None, {}, na=True, basis="none",
                    note="no source or fitted channel: there is no curve to classify")
    H = float(src.H)
    allc = compound_moves(ctx)
    cs = graded_compounds(ctx, allc)
    if not cs:
        return _row("C1", "ease discipline", None, {"compounds": len(allc)}, na=True,
                    basis="source: per-channel compound moves",
                    note="no spatial move carries a classifiable curve")

    decl = _declared_names(man, "mechanical") + _declared_names(man, "impact")
    cuts = [int(x) for x in (_get(ctx, "cuts") or [])]

    linear, viol, waived, exempt, worst = [], [], [], [], []
    hero_els = hero_elements(ctx)
    hero_viol = None
    budget_max = C6_BUDGET[_register(ctx)][1]
    for c in cs:
        if c["ambient"]:
            exempt.append(("ambient", c))
            continue
        if c["mechanical"]:
            # a declared mechanical element is exempt from BOTH tests. Exempting
            # it from linear and then charging it under direction nullifies the
            # declaration instead of honouring it
            exempt.append(("mechanical", c))
            continue
        cls, role = c["class"], c["role"]
        if cls == "linear":
            linear.append(c)
            worst.append((2.0 + c["travel"] / max(src.diag, 1.0), c["onsetF"]))
            continue
        if cls == "stutter":
            viol.append(("stutter", c))
            worst.append((1.5, c["onsetF"]))
            continue
        if cls in ("custom", "unclassified"):
            exempt.append(("unclassified", c))
            continue
        if c["transition"]:
            # canon 5: whip pans, full-frame wipes, cards flying through frame
            # and infinite zooms cross the frame in a straight line at one
            # acceleration, and should
            exempt.append(("transition", c))
            continue
        if c["roundTrip"]:
            # a bounce, a pulse, a nudge-and-return has no arrival direction;
            # its reversals belong to C6
            exempt.append(("roundTrip", c))
            continue
        if role == "departure" and c["scaleDelta"] < C1_RECEDE_SCALE \
                and c["dist"] < C1_RECEDE_TRAVEL * H:
            # canon C1's own exemption: the premium sink, scale 1 -> 0.96 plus a
            # fade, which reads as receding rather than being thrown
            exempt.append(("smallRecede", c))
            continue
        if c["seen"] < C1_SEEN_PROGRESS:
            waived.append(c)
            continue
        if c.get("junction"):
            # canon 1.2's velocity step is a step the VIEWER sees inside one
            # continuous move. A junction that lands on a cut frame is two legs
            # on opposite sides of an edit, where the whole picture changes:
            # canon 1.6 says a move cut into or out of mid-flight is judged on
            # being in motion at the boundary, and C17 already grades what
            # happens across that boundary. The morph card that slides its line
            # out on power3.in and re-centres the replacement word on
            # sine.inOut, both films' worst C1 finding, is exactly this.
            jf = c["startF"] + c["junction"][0]
            if any(abs(jf - cut) <= C1_JUNCTION_CUT_TOL for cut in cuts):
                exempt.append(("junctionAtCut", c))
                continue
            viol.append(("junction", c))
            worst.append((1.6, jf))
            continue
        if cls == "outIn":
            viol.append(("outIn", c))
            worst.append((1.4, c["onsetF"]))
            continue
        if role == "entrance":
            bad = not (cls == "out"
                       or (cls == "overshoot" and budget_max > 0)
                       or (cls == "inOut" and c["anticipation"] > 0))
        elif role == "departure":
            bad = cls not in ("in", "overshoot")
        else:
            # a reposition ENDS AT REST, so it arrives, and canon 1.5 gives
            # overshoot its own register table rather than forbidding it.
            # Accepting `overshoot` on an entrance and a departure and refusing
            # it between two positions charged the same arrival shape as a
            # direction fault on four coins scaling in on back.out(1.7) and on
            # a chart bar settling on sine.out inside a scaling card. The
            # AMPLITUDE of that overshoot is C6's row and it is graded there
            # against the declared register.
            bad = cls not in ("inOut", "out", "overshoot")
        if bad:
            viol.append((cls, c))
            worst.append((1.0 + c["travel"] / max(src.diag, 1.0), c["onsetF"]))
            if c["el"] in hero_els and role == "entrance" and hero_viol is None:
                hero_viol = c

    graded = len(cs) - len(exempt) - len(waived)
    if graded < C1_MIN_EVIDENCE:
        return _row("C1", "ease discipline", None,
                    {"graded": graded, "compounds": len(allc),
                     "linearSpatial": len(linear),
                     "directionViolations": len(viol)}, na=True,
                    basis="source: per-channel compound moves",
                    note=f"only {graded} gradeable move(s): too little motion to "
                         "demonstrate ease discipline either way",
                    declarations=decl)
    L, D, M = len(linear), len(viol), max(graded, 1)
    d_rate = D / M
    if L == 0 and D == 0:
        band = "A" if fitted else "S"
    elif L == 0 and d_rate <= C1_A_DRATE:
        band = "A"
    elif L == 0 and d_rate <= C1_B_DRATE:
        band = "B"
    else:
        band = "C"
    if L >= 1 or d_rate > C1_B_DRATE:
        band = "C"

    note = ""
    if linear:
        c = linear[0]
        note = (f"linear on {c['key']} ({','.join(c['spatial']) or c['ch']}), "
                f"measured on screen over f{c['startF']}-{c['endF']}")
    elif hero_viol:
        note = (f"hero entrance {hero_viol['key']} reads {hero_viol['class']} on "
                "screen; an arrival must be an out")
    elif viol:
        cls, c = viol[0]
        if cls == "junction" and c.get("junction"):
            k, before, after, _r = c["junction"]
            note = (f"{c['key']} steps from {before:.2g} to {after:.2g} of travel "
                    f"per frame at f{c['startF'] + k}, where its two tweens meet: "
                    "one curve, not two")
        else:
            note = (f"{c['key']} {c['role']} reads {cls} on screen "
                    f"(authored {c['ease']}, channel {c['ch']})")
    if fitted:
        note = (note + "; " if note else "") + \
            "reduced confidence: classes fitted to tracked components, capped at A"

    measured = {"linearSpatial": L, "directionViolations": D, "graded": graded,
                "dRate": round(d_rate, 3), "compounds": len(allc),
                "waivedCutMidFlight": len(waived), "exempt": len(exempt),
                "basis": "pixel-fit" if fitted else "measured-geometry"}
    return _row("C1", "ease discipline", band, measured, rank_worst(worst), note,
                basis=("pixel: fitted centroid curves" if fitted else
                       "source: world geometry of the channel each move writes, "
                       "compounded across chained tweens"),
                declarations=decl)


# =============================================================================
# C2  ease vocabulary                                                weight 1
# =============================================================================

def c2_ease_vocabulary(ctx):
    """Canon C2.  Cluster sampled SHAPE at radius 0.06, PER ROLE.

    S  one shape per role, distinct across roles, >= 3 clusters
    C  1 cluster, or the same ease on hero + secondary + ambient, or overshoot
       on opacity or colour

    The overshoot AMPLITUDE bands are C6's, not C2's; canon delegates them and
    the two used to contradict each other, C2 wanting overshootShare 0 for S
    while C6 allowed a corporate register 0-5 %.

    An input that still scores C: a piece where every tween is `power2.out`, so
    one cluster covers all of it.  Or one `back.out` on an opacity fade -- paint
    has no momentum, and overshoot on it is a C at any count.
    """
    src = _get(ctx, "src")
    fitted = _fitted(ctx)
    if src is None:
        return _row("C2", "ease vocabulary", None, {}, na=True, basis="none",
                    note="no source or fitted channel")
    cs = graded_compounds(ctx)
    if len(cs) < C2_MIN_MOVES:
        return _row("C2", "ease vocabulary", None, {"moves": len(cs)}, na=True,
                    basis="source: measured shape clusters",
                    note=f"fewer than {C2_MIN_MOVES} classifiable moves: there is no "
                         "vocabulary to count")
    radius = C2_FIT_CLUSTER_RADIUS if fitted else C2_CLUSTER_RADIUS
    hero_els = hero_elements(ctx)
    # One entry per AUTHORED leg on the source channel, and per fitted compound
    # when there is no author to read. C1 asks what the viewer sees and must
    # measure; C2 asks what the author chose, and clustering the composed world
    # curve counts the parent's shape and the rect's quantisation as vocabulary
    # (75 moves produced 24 shapes on a film built from four eases).
    entries, owners = [], []
    for c in cs:
        arrs = (c["easeSamples"] if (not fitted and c["easeSamples"])
                else [np.asarray(c["samples"], float)])
        for s in arrs:
            if s is None or len(np.asarray(s)) < 5:
                continue
            entries.append(_resample101(np.asarray(s, float)))
            owners.append(c)
    if len(entries) < C2_MIN_MOVES:
        return _row("C2", "ease vocabulary", None, {"moves": len(entries)}, na=True,
                    basis="source: measured shape clusters",
                    note="no authored curve carries enough samples to cluster")
    idx, counts = shape_clusters(entries, radius)
    n_clusters = len(counts)
    top_share = max(counts) / len(entries)

    roles = {}
    for c, ci in zip(owners, idx):
        r = move_role_class(src, c, hero_els)
        roles.setdefault(r, {}).setdefault(ci, 0)
        roles[r][ci] += 1
    roles_two = sum(1 for _, cc in roles.items() if len(cc) > 1)
    dominant = {r: max(cc, key=lambda k: cc[k]) for r, cc in roles.items()}
    distinct_roles = (len(set(dominant.values())) == len(dominant) and len(dominant) > 1)
    triple = [dominant.get(r) for r in ("hero", "support", "ambient")]
    same_everywhere = (None not in triple and len(set(triple)) == 1)

    paint_over = _paint_overshoot(src, C2_PAINT_OVERSHOOT)

    if n_clusters >= C2_S_CLUSTERS and roles_two == 0 and distinct_roles \
            and not paint_over:
        band = "S"
    elif n_clusters >= C2_S_CLUSTERS and roles_two <= C2_A_ROLES_WITH_TWO \
            and not paint_over:
        band = "A"
    elif n_clusters >= C2_B_CLUSTERS:
        band = "B"
    else:
        band = "C"
    if n_clusters == 1 or same_everywhere or paint_over             or top_share >= C2_C_TOPSHARE:
        band = "C"

    note = ""
    if paint_over:
        note = (f"overshoot on a paint tween: {paint_over[0]['key']} "
                f"({','.join(paint_over[0].get('paint') or ['opacity'])}); paint has "
                "no momentum")
    elif n_clusters == 1:
        note = "one ease shape everywhere"
    elif top_share >= C2_C_TOPSHARE:
        note = (f"{top_share:.0%} of the curves are one ease shape; that is one "
                "ease shape for the whole film")
    elif same_everywhere:
        note = "the same ease shape on hero, support and ambient at once"
    elif n_clusters > C2_MAX_SHAPES:
        note = (f"{n_clusters} distinct ease shapes across {roles_two} role(s) that "
                "use more than one; past about five a piece reads as unresolved "
                "rather than varied")
    elif roles_two > C2_A_ROLES_WITH_TWO:
        note = f"{roles_two} roles use more than one ease shape"
    if fitted:
        # a fitted curve carries tracking noise, so clustering can demonstrate a
        # LACK of variety and cannot demonstrate its presence
        if band == "S":
            band = "A"
        note = (note + "; " if note else "") + \
            "reduced confidence: fitted-curve clusters, capped at A"

    measured = {"shapeClusters": n_clusters, "topShare": round(top_share, 3),
                "rolesWithTwo": roles_two, "roles": len(roles),
                "paintOvershoot": len(paint_over), "curves": len(entries),
                "moves": len(cs), "basis": "pixel-fit" if fitted else "source"}
    return _row("C2", "ease vocabulary", band, measured,
                rank_worst([(2.0, m["startF"]) for m in paint_over[:3]]), note,
                basis=("pixel: fitted shape clusters" if fitted else
                       f"source: shape clusters at radius {radius}, per role"),
                declarations=_declared_names(_get(ctx, "manifest") or {}, "hero"))


def _paint_overshoot(src, floor):
    """Paint tweens whose overshoot is RENDERED. Canon 1.5: overshoot goes on
    transforms only, never on opacity or colour, because paint has no momentum.

    Two things have to be true before this is a finding, and the row used to
    check neither.

    THE RIGHT CHANNEL. A paint move is whatever paint property its tween
    writes, and only an opacity move has an opacity curve. Reading the element's
    opacity track for a `filter: blur(20px) -> blur(0px)` on `power2.out`
    measured the OTHER tween running on the same element over the same frames --
    an `autoAlpha` on `back.out(1.4)` -- and reported the blur ramp as an
    overshoot on paint. That single mislabelled tween was a C on two criteria
    of one film.

    THE OVERSHOOT HAS TO REACH THE SCREEN. Canon C1's instruction for the
    neighbouring row is "classify from MEASURED GEOMETRY, not the parsed ease",
    and the same discipline applies here: `autoAlpha: 0 -> 1` on a back ease
    computes a peak near 1.10, the compositor clamps it at 1.0, and not one
    delivered frame differs from the same tween on `power2.out`. The browser's
    own opacity track reports the unclamped 1.024, so the number exists in the
    tween object and nowhere else.

    STILL FAILS: `opacity: 0.35` or `opacity: 0.85` on `back.out`, whose flick
    to 0.40 or 0.94 renders in full; any `backgroundColor`, `color`, `fill` or
    `stroke` tween on an overshooting ease, which has no clamp to hide behind;
    and an opacity move whose curve dips below its own start value on the way
    in, which is the anticipation form of the same fault."""
    out = []
    for mv in getattr(src, "moves", []):
        if mv.get("kind") != "paint":
            continue
        props = set(mv.get("props") or ())
        if props & PAINT_CLAMPED_PROPS:
            series, _ = channel_series(src, mv["el"], "opacity",
                                       mv["startF"], mv["endF"])
            s_curve = _resample101(series) if series is not None                 else mv.get("easeSamples")
            if s_curve is None:
                continue
            a = np.asarray(s_curve, float)
            if a.max() <= 1.0 + floor and a.min() >= -floor:
                continue
            v0, v1 = _paint_endpoints(src, mv)
            if v0 is None or v1 is None:
                out.append(mv)                   # cannot tell: charge it
                continue
            cl = lambda v: min(max(float(v), 0.0), 1.0)
            peak = v0 + (v1 - v0) * float(a.max())
            trough = v0 + (v1 - v0) * float(a.min())
            visible = 0.0
            if a.max() > 1.0 + floor:            # past the target
                visible = max(visible, cl(peak) - cl(v1))
            if a.min() < -floor:                 # before the start
                visible = max(visible, cl(v0) - cl(trough))
            if visible <= PAINT_CLAMP_EPS:
                continue                         # renders identically to no overshoot
            out.append(mv)
            continue
        # colour, filter and every other paint property: no numeric track and
        # no clamp to hide an excursion, so the authored curve is the evidence
        s_curve = mv.get("easeSamples")
        if s_curve is None:
            continue
        a = np.asarray(s_curve, float)
        if a.max() > 1.0 + floor or a.min() < -floor:
            out.append(mv)
    return out


PAINT_CLAMPED_PROPS = {"opacity", "autoAlpha", "alpha"}
PAINT_CLAMP_EPS = 0.002          # one part in 500 of opacity is under one code
                                 # value at 8 bits and cannot reach a frame


def _paint_endpoints(src, mv):
    """The absolute opacity this paint tween starts and ends at, off the track.
    An overshoot is only visible if the value it overshoots to is inside the
    renderable range; 0 -> 1 and 1 -> 0 both clamp."""
    try:
        op = src.prop(mv["el"], "opacity")
    except Exception:
        return None, None
    a = int(clamp(mv["startF"], 0, len(op) - 1))
    b = int(clamp(mv["endF"], 0, len(op) - 1))
    if b <= a:
        return None, None
    return float(op[a]), float(op[b])


# =============================================================================
# C6  settle quality                                                 weight 1
# =============================================================================

def c6_settle_quality(ctx):
    """Canon C6.  Reversals and amplitude as a fraction of TRAVEL, centroid
    tracked for positional overshoot, against the register budgets in canon 1.5.

    S  inside the register budget, no settle with >= 2 reversals
    C  outside budget on > 15 %, or >= 3 reversals, or overshoot on paint

    Overshoot % = (peak - target) / (target - start), canon's explicit
    denominator: on a scale tween 0.9 -> 1.0, 10 % of travel is scale 1.01
    (felt) and 10 % of target is 1.10 (cartoon).  The measured curve is already
    normalised to travel, so peak - 1 IS that fraction, and it is read off the
    world channel so a back.out on a slide is visible where an ink-count
    fallback is blind to it.

    The LOOP row exists because all four of the playlist's easing compliments
    are on short character or object loops praised for the anticipation and
    overshoot the held-card registers forbid.  It is granted without a
    declaration to any tween with repeat != 0, and by name through
    manifest["loops"].

    An input that still scores C: a premium-register piece where one settle in
    five overshoots 8 % of travel, or any settle that reverses three times, or
    a single `back.out` on an opacity fade.
    """
    src = _get(ctx, "src")
    man = _get(ctx, "manifest") or {}
    register = _register(ctx)
    fitted = _fitted(ctx)
    if src is None:
        return _row("C6", "settle quality", None, {}, na=True, basis="none",
                    note="no source or fitted channel")
    cs = [c for c in compound_moves(ctx) if c["samples"] is not None]
    if not cs:
        return _row("C6", "settle quality", None, {"settles": 0}, na=True,
                    basis="source: world geometry per channel",
                    note="no settling spatial move carries a measurable curve")

    off, wobble, graded, loops = 0, 0, 0, 0
    worst, max_amp, max_rev = [], 0.0, 0
    for c in cs:
        if c["ambient"] or c["mechanical"]:
            continue
        if c["roundTrip"]:
            # a round trip returns to where it STARTED; "overshoot past target"
            # is undefined for it and its reversals ARE the gesture. The test
            # for one now requires the return (C1_ROUNDTRIP_RETURN), because the
            # net/path test alone exempted precisely the settles this row
            # exists to catch: net/path falls as a settle oscillates, so the
            # bigger the wobble the more certainly it was skipped, and the row
            # awarded S on a control built around elastic.out(1.4, 0.35).
            continue
        reg = "loop" if c["loop"] else register
        if c["loop"]:
            loops += 1
        amp_min, amp_max, rev_max = C6_BUDGET[reg]
        graded += 1
        s = np.asarray(c["samples"], float)
        amp = max(0.0, float(s.max()) - 1.0)
        sm = smooth_box(s, C6_SMOOTH)
        enter = np.flatnonzero(sm >= C6_SETTLE_ENTER)
        rev = 0
        if len(enter):
            d = np.diff(sm[enter[0]:])
            sig = d[np.abs(d) > C6_REVERSAL_FLOOR]
            if len(sig) >= 2:
                rev = int((np.diff(np.sign(sig)) != 0).sum())
        max_amp = max(max_amp, amp)
        max_rev = max(max_rev, rev)
        bad_min = (amp_min > 0 and c["role"] in C6_MIN_AMP_ROLES and amp < amp_min)
        if amp > amp_max or bad_min or rev > rev_max:
            off += 1
            worst.append((amp + rev, c["settleF"]))
        if rev >= C6_C_REVERSALS:
            wobble += 1

    paint_over = _paint_overshoot(src, C6_REVERSAL_FLOOR)

    if graded < C6_MIN_SETTLES:
        return _row("C6", "settle quality", None,
                    {"settles": graded, "register": register,
                     "paintOvershoot": len(paint_over)}, na=True,
                    basis="source: world geometry per channel",
                    note=(f"only {graded} settling move(s): every other measurable "
                          "move is ambient, mechanical or a round trip"),
                    declarations=_declared_names(man, "loops"))
    off_rate = off / graded
    if off_rate == 0 and wobble == 0 and not paint_over:
        band = "A" if fitted else "S"
    elif off_rate <= C6_A_OFF and wobble == 0 and not paint_over:
        band = "A"
    elif off_rate <= C6_B_OFF and wobble == 0:
        band = "B"
    else:
        band = "C"
    if off_rate > C6_B_OFF or wobble or paint_over:
        band = "C"

    amp_min, amp_max, rev_max = C6_BUDGET[register]
    note = ""
    if paint_over:
        note = f"overshoot on opacity or colour: {paint_over[0]['key']}"
    elif wobble:
        note = f"{wobble} settle(s) reverse {C6_C_REVERSALS}+ times, which is a wobble"
    elif off:
        note = (f"{off}/{graded} settles outside the {register} budget "
                f"({amp_min:.0%}-{amp_max:.0%} of travel, {rev_max} reversal(s))")
    elif register in ("premium", "corporate") and max_amp > C6_TELL_AMPLITUDE:
        note = (f"peak overshoot {max_amp:.0%} of travel, past the "
                f"{C6_TELL_AMPLITUDE:.0%} bouncy tell, in a {register} register")
    if fitted:
        note = (note + "; " if note else "") + \
            "reduced confidence: amplitude cannot be attributed to an element from " \
            "the pixel channel alone, capped at A"

    decl = _declared_names(man, "loops")
    if man.get("register"):
        decl.append(f"register:{man['register']}")
    measured = {"offRegister": round(off_rate, 3), "maxAmplitude": round(max_amp, 4),
                "maxReversals": max_rev, "wobbles": wobble, "settles": graded,
                "loopMoves": loops, "register": register}
    return _row("C6", "settle quality", band, measured,
                rank_worst(worst + [(9.0, m["startF"]) for m in paint_over[:2]]), note,
                basis="source: overshoot as a fraction of travel, centroid tracked",
                declarations=decl)


# =============================================================================
# C10 timing contrast                                                weight 1
# =============================================================================

def c10_timing_contrast(ctx):
    """Canon C10.  CV and ratios; on a detected grid, the RANGE OF BAR MULTIPLES
    instead.

    S  R_beat >= 3, cv >= 0.30, R_move >= 3 (ambient and transitions excluded)
    C  cv < 0.10, or R_move < 1.5

    R_move is the 90th over the 10th percentile of move duration, not max over
    min.  Across ninety moves max/min is a two-sample statistic: one 2-frame
    accent against one 3-second push reports 45 and the row can never fail,
    which is a grader becoming decorative.  The raw ratio is still printed.

    When a tempo is detected and most cuts land on bar lines, CV is the wrong
    statistic -- cards cluster at 1, 2 and 4 bar multiples and CV falls
    legitimately -- so the bar-multiple range replaces it (canon 2.4).

    An input that still scores C: twenty cards each exactly one second long
    with every tween at 0.4 s.  cv_beat is 0 and R_move is 1.
    """
    src = _get(ctx, "src")
    px = _get(ctx, "px")
    audio = _get(ctx, "audio")
    beats = _get(ctx, "beats") or []
    cuts = _get(ctx, "cuts") or []
    fps = float(_get(ctx, "fps", 30.0))
    man = _get(ctx, "manifest") or {}
    decl = ["cuts"] if man.get("cuts") else []

    B = np.array([b - a + 1 for (a, b) in beats], dtype=float)
    # Canon's C column here is TWO terms and only one of them is a beat
    # statistic: "cv < 0.10, or R_move < 1.5". R_move is a property of the
    # MOVES, so a piece with too few beats to compute a beat CV can still be
    # graded on whether everything in it happens at one speed -- which is canon
    # section 8 item 4's whole detector for the robotic tell, "uniform duration,
    # uniform distance and a single ease". Sending the row to N/A on the beat
    # count alone took the criterion off the amateur control, whose two beats
    # hide seven moves at one duration, and off a static title card with five
    # tweens. The beat half still needs beats: without them the row reports what
    # it measured and caps at A, because S is "R_beat >= 3, cv >= 0.30 AND
    # R_move >= 3" and two of those three cannot be shown.
    beat_evidence = len(B) >= C10_MIN_BEATS
    r_beat = float(B.max() / max(B.min(), 1.0)) if beat_evidence else 0.0
    cv_beat = float(B.std() / B.mean()) if (beat_evidence and B.mean()) else 0.0

    if src is not None:
        durs = [c["dur"] for c in compound_moves(ctx)
                if not c["ambient"] and not c["mechanical"] and not c["transition"]
                and c["dur"] > 0]
        durs += [mv["dur"] for mv in src.moves
                 if mv.get("kind") == "paint" and not mv.get("ambient")
                 and mv["dur"] > 0]
        basis = "source: compound move durations"
    elif px is not None:
        durs = [len(t["frames"]) / fps for t in px.tracks if len(t["frames"]) >= 2]
        basis = "pixel: tracked component lifetimes"
    else:
        durs, basis = [], "cuts only"
    M = np.array([d for d in durs if d > 0], dtype=float)
    if len(M) >= C10_MIN_MOVES:
        lo = float(np.percentile(M, C10_MOVE_PCTL[0]))
        hi = float(np.percentile(M, C10_MOVE_PCTL[1]))
        r_move = hi / max(lo, 1e-6)
        r_move_raw = float(M.max() / max(M.min(), 1e-6))
    else:
        r_move = r_move_raw = 0.0
    classes = sum(1 for (_, lo2, hi2) in C10_CLASSES if any(lo2 <= d < hi2 for d in M))

    grid, multiples, on_grid, bars = None, 0, 0.0, []
    if audio is not None and getattr(audio, "present", False):
        try:
            bars = audio.bar_lines(fps, int(_get(ctx, "frames", 0) or 0))
        except Exception:
            bars = []
    if bars:
        tol = fscale(C10_GRID_TOL_F30, fps)
        hit = sum(1 for c in cuts if any(abs(c - b) <= tol for b in bars))
        on_grid = hit / max(len(cuts), 1)
        if on_grid >= C10_GRID_SHARE and getattr(audio, "grid", None):
            bar = audio.grid["period"] * 4.0
            multiples = len({max(1, int(round(d / bar))) for d in B})
            grid = {"bpm": round(audio.grid["bpm"], 1), "onGrid": round(on_grid, 2)}

    worst = [int(beats[int(np.argmin(B))][0])]
    if grid:
        if multiples >= C10_S_MULTIPLES and r_move >= C10_S_RMOVE:
            band = "S"
        elif multiples >= C10_A_MULTIPLES and r_move >= C10_A_RMOVE:
            band = "A"
        elif multiples >= C10_A_MULTIPLES or r_move >= C10_C_RMOVE:
            band = "B"
        else:
            band = "C"
        if r_move < C10_C_RMOVE or multiples < C10_A_MULTIPLES:
            band = "C"
        note = ("every card is the same number of bars long"
                if multiples < C10_A_MULTIPLES else
                ("everything moves at one speed" if r_move < C10_C_RMOVE else ""))
        measured = {"barMultiples": multiples, "bpm": grid["bpm"],
                    "cutsOnGrid": grid["onGrid"], "R_move": round(r_move, 2),
                    "R_move_raw": round(r_move_raw, 2), "durationClasses": classes,
                    "beats": int(len(B))}
        return _row("C10", "timing contrast", band, measured, worst, note,
                    basis=basis + " on a detected bar grid", declarations=decl)

    if not beat_evidence:
        if len(M) < C10_MIN_MOVES:
            return _row("C10", "timing contrast", None,
                        {"beats": int(len(B)), "moves": int(len(M))}, na=True,
                        basis="cuts",
                        note=(f"fewer than {C10_MIN_BEATS} content beats and fewer "
                              f"than {C10_MIN_MOVES} gradeable moves: neither half "
                              "of the timing contrast can be measured"),
                        declarations=decl)
        band = "A" if r_move >= C10_A_RMOVE else (
            "B" if r_move >= C10_C_RMOVE else "C")
    elif r_beat >= C10_S_RBEAT and cv_beat >= C10_S_CV and r_move >= C10_S_RMOVE:
        band = "S"
    elif r_beat >= C10_A_RBEAT and cv_beat >= C10_A_CV and r_move >= C10_A_RMOVE:
        band = "A"
    elif cv_beat >= C10_C_CV and r_move >= C10_C_RMOVE:
        band = "B"
    else:
        band = "C"
    if r_move < C10_C_RMOVE or (beat_evidence and cv_beat < C10_C_CV):
        band = "C"
    note = ""
    if not beat_evidence:
        note = ("only %d beat(s): the beat CV and R_beat are not measurable, so "
                "the row is graded on move durations alone (R_move %.2f) and "
                "caps at A" % (len(B), r_move))
        if r_move < C10_C_RMOVE:
            note += "; everything moves at one speed"
    elif cv_beat < C10_C_CV:
        note = "every beat is the same length; the cut reads as a metronome"
    elif r_move < C10_C_RMOVE:
        note = "everything moves at one speed"
    measured = {"R_beat": round(r_beat, 2), "cv_beat": round(cv_beat, 3),
                "R_move": round(r_move, 2), "R_move_raw": round(r_move_raw, 2),
                "durationClasses": classes, "cutsOnGrid": round(on_grid, 2),
                "beats": int(len(B))}
    return _row("C10", "timing contrast", band, measured, worst, note, basis=basis,
                declarations=decl)


# =============================================================================
# C11 distance and duration                                          weight 1
# =============================================================================

def _k_of_dist(d, full):
    xs = [p[0] for p in C11_K_TABLE] + [full]
    ys = [p[1] for p in C11_K_TABLE] + [C11_K_FULLSCREEN]
    return float(np.interp(d, xs, ys))


def _box_area(b):
    return float((b[2] - b[0] + 1) * (b[3] - b[1] + 1))


def _box_overlap(a, b):
    """Intersection area of two inclusive (x0, y0, x1, y1) boxes."""
    x0, x1 = max(a[0], b[0]), min(a[2], b[2])
    y0, y1 = max(a[1], b[1]), min(a[3], b[3])
    if x1 < x0 or y1 < y0:
        return 0.0
    return float((x1 - x0 + 1) * (y1 - y0 + 1))


def _axis_travel(a0, a1, b0, b1, lo, hi):
    """How far a matched region travelled on one axis, in pixels.

    BOTH edges have to move for the region itself to have moved. A typewriter
    reveal, a wipe uncovering a line and a masked word rising behind a static
    mask each move ONE edge and leave the other where it was: no edge is
    travelling on screen, new picture is arriving, and charging those is a
    large part of what produced a reading of 218 px per frame on a frame whose
    real displacement was 2.6. An edge sitting on the frame boundary is clipped
    and carries no information, so there the other edge stands alone, which is
    how an element sliding out of frame is still measured."""
    d0, d1 = b0 - a0, b1 - a1
    clipped_lo = a0 <= lo or b0 <= lo
    clipped_hi = a1 >= hi or b1 >= hi
    if clipped_lo and clipped_hi:
        return 0.0
    if clipped_lo:
        return abs(d1)
    if clipped_hi:
        return abs(d0)
    return min(abs(d0), abs(d1))


def _edge_travel_map(px, dec_w=640.0, dec_h=360.0):
    """Per-frame maximum displacement of a high-contrast EDGE, as a fraction of
    frame width, plus the set of frames in which anything moved at all.

    The regions are the frame's largest ink components; a region in frame f is
    paired with the region in f-1 that overlaps it, one-to-one, and the
    measurement is how far their bounding-box EDGES moved.

    WHAT THIS REPLACES, and why. The scan used to measure the CENTROID travel
    of a tracked component. A centroid moves whenever a component grows, merges
    or splits while nothing on screen translates, so on a 26 s film it reported
    218, 325 and 132 px per frame on frames whose real edge displacement,
    re-measured at full resolution, was 2.6, 1.9 and 21 px: half the frames
    printed as worst@ showed no defect at all, and a designer following the
    list was sent to quiet frames. The area gate that tried to suppress that
    (0.8 to 1.25) then discarded the one frame in the same film that genuinely
    jumped, a slam whose ink area went 128137 to 352772 and whose left edge
    moved 341 px. A centroid is not an edge, and a gate on area is not a way to
    make it one. Every frame this returns is reproducible as "this region's
    edges were here and are now there"."""
    travel, moving, hits = {}, set(), {}
    comps = px.comps
    n = getattr(px, "n", len(comps))

    def regions(f):
        return [(c[3], c[4], c[5], c[6], c[0])
                for c in comps[f][:C11_STROBE_MAX_COMPS]
                if c[0] >= C11_STROBE_MIN_AREA]

    prev = regions(0) if n else []
    for f in range(1, n):
        cur = regions(f)
        if prev and cur:
            ap = [_box_area(b) for b in prev]
            ac = [_box_area(b) for b in cur]
            match = [[_box_overlap(bp, bc)
                      >= C11_STROBE_MATCH_SHARE * min(ap[i], ac[j])
                      for j, bc in enumerate(cur)] for i, bp in enumerate(prev)]
            row = [sum(1 for v in r if v) for r in match]
            col = [sum(1 for r in match if r[j]) for j in range(len(cur))]
            best, per = 0.0, []
            for i, bp in enumerate(prev):
                if row[i] != 1:
                    continue                  # a split: one region became two
                for j, bc in enumerate(cur):
                    if not match[i][j] or col[j] != 1:
                        continue              # a merge: two regions became one
                    dx = _axis_travel(bp[0], bp[2], bc[0], bc[2], 0, dec_w - 1)
                    dy = _axis_travel(bp[1], bp[3], bc[1], bc[3], 0, dec_h - 1)
                    d = math.hypot(dx, dy)
                    if d <= 0.0:
                        continue
                    w = max(bc[2] - bc[0], 1.0)
                    h = max(bc[3] - bc[1], 1.0)
                    ext = w if abs(dx) >= abs(dy) else h
                    per.append((dx, dy, d, d / ext, float(bc[4])))
                    best = max(best, d)
            if best > 0.0:
                travel[f] = best / dec_w
                hits[f] = per
            if best >= C11_STROBE_MOVING_PX:
                moving.add(f)
        prev = cur
    return travel, moving, hits


def untracked_frames(hits, thr_px):
    """The frames on which the fast edge cannot be being TRACKED, which is the
    set a shutter is actually for.  {frame: worst displacement in px}.

    Canon 1.9 gives the strobe threshold as "about 0.5 % of frame width per
    frame" and labels it `[inference from one measured case at 31 px]`, then
    names the four things that move it: "contrast, edge hardness and whether the
    element is still fading in all move it; so does whether the eye is TRACKING
    the object, which is why fast pans judder while a tracked hero does not."
    Canon's own reading rule for that label says an inference is "a starting
    value to fit against reference footage, never a canonical figure", and the
    reference footage here is a broadcast ad measured at full resolution to
    carry no motion blur anywhere (abe-ad FINDINGS.md row B) beside a product
    film that carries a blur ramp on nearly every entrance.

    Charging every frame over the raw threshold charges a single hero card
    sliding at 12 px per frame, which both references do and one of them never
    blurs.  What actually strobes is motion the eye cannot pursue:

      (a) two or more fast regions travelling in DIFFERENT directions - smooth
          pursuit locks onto one flow, so the others are seen from a fixed eye
          and judder; and
      (b) a region displacing more than its own extent along the travel axis -
          successive renders do not overlap at all, so there is nothing for
          fusion to work on even under pursuit.

    A pan or a whip is case (a) at the field level and is exempt one layer up,
    by class, under canon 5."""
    out = {}
    for f, per in hits.items():
        strong = [h for h in per if h[2] >= C11_TRACK_STRONG_MULT * thr_px]
        flows = []
        for dx, dy, _d, _r, _a in strong:
            ang = math.atan2(dy, dx)
            for prev in flows:
                da = abs(math.degrees(ang - prev))
                if min(da, 360.0 - da) <= C11_TRACK_DIR_DEG:
                    break
            else:
                flows.append(ang)
        if len(flows) > 1 or any(
                r > C11_TRACK_TELEPORT and a >= C11_TRACK_TELEPORT_AREA
                for _dx, _dy, _d, r, a in per):
            out[f] = max(h[2] for h in per)
    return out


def strobe_scan(px, cuts, manifest, fps, dec_w=640.0):
    """Frames where a high-contrast EDGE travels more than 0.5 % of frame WIDTH
    per frame, with the tolerated jump scaling WITH the delivered rate.
    Returns (travel, strobe, moving, thr).

    The travel map comes from the integrator (`_edge_travel_map`). Two
    corrections are applied on top of it here, and only here, because they are
    C11's policy rather than the measurement: a declared shutter range DOUBLES
    the tolerance rather than exempting the frames, because canon 1.9 says "up
    to 1 % with a shutter", not "no limit with a shutter"; and a strobing run
    whose own total travel crosses half the frame is a whip, a wipe or a card
    flying through, which canon 5 exempts by class."""
    thr = C11_STROBE_FRAC * (float(fps) / C11_STROBE_FPS_REF)
    shutter = (manifest or {}).get("shutterFrames", []) or []
    near_cut = set()
    for c in (cuts or []):
        near_cut.update(range(int(c) - 1, int(c) + 2))
    if px is None:
        return {}, {}, set(), thr
    travel, moving, per_region = _edge_travel_map(px, dec_w, dec_w * 9.0 / 16.0)
    # canon 1.9's fourth modifier, applied where the other three cannot be:
    # a frame whose fast edge is a single flow the eye can pursue is not
    # strobing, and neither the strobe row nor the blur-coverage row is about
    # it. See untracked_frames.
    untracked = untracked_frames(per_region, thr * dec_w)
    hits = []
    for f in sorted(travel):
        if f not in untracked:
            continue
        frac = travel[f]
        local = thr * (C11_STROBE_SHUTTER_MULT
                       if any(a <= f <= b for (a, b) in shutter) else 1.0)
        if frac > local and f not in near_cut:
            hits.append((f, frac))
    runs, cur = [], []
    for (f, frac) in hits:
        if cur and f == cur[-1][0] + 1:
            cur.append((f, frac))
        else:
            if cur:
                runs.append(cur)
            cur = [(f, frac)]
    if cur:
        runs.append(cur)
    strobe = {}
    for run in runs:
        if len(run) < C11_STROBE_MIN_RUN:
            continue                      # a single frame cannot strobe: the
                                          # eye needs two discrete copies to
                                          # see one, and canon's own gate is
                                          # travel "sustained in one direction
                                          # for two frames". One frame over the
                                          # threshold is the fastest frame of a
                                          # slam, not a strobe.
        if sum(fr for _, fr in run) >= C11_STROBE_TRANSIT_RUN:
            continue                      # a transition by class, canon 5
        for f, frac in run:
            strobe[f] = max(strobe.get(f, 0.0), frac)
    return travel, strobe, moving, thr


def strobe_rank(strobe):
    """Rank strobe frames by contiguous-run length first and per-frame travel
    second.  Reporting the head of a frame-ordered set is not "worst": it names
    three isolated single-frame hits in the opening titles and misses the
    five-frame run that is the film's actual defect."""
    if not strobe:
        return []
    fs = sorted(strobe)
    runs, cur = [], [fs[0]]
    for f in fs[1:]:
        if f == cur[-1] + 1:
            cur.append(f)
        else:
            runs.append(cur)
            cur = [f]
    runs.append(cur)
    out = []
    for r in runs:
        wf = max(r, key=lambda f: strobe[f])
        out.append((len(r) * 100.0 + strobe[wf], wf))
    return out


def c11_distance_duration(ctx):
    """Canon C11.  `rho` within ENTRANCE moves only; the 1/3 rule for in-scene
    repositions only, transitions exempt BY CLASS; strobe at 0.5 % of frame
    width per frame.

    S  rho >= 0.40 within class, 0 violations, 0 strobe frames
    C  rho < 0 within class, or > 3 violations

    Note what canon's C row does NOT contain: strobe.  Strobe blocks S and A
    and is printed, and that is all it does.  Making strobeShare > 0.10 a C put
    two replicas of aired broadcast work below a deliberate disaster on the
    strength of their own whip pans.

    In professional pieces the largest travels are the FASTEST -- whips, slams,
    pushes -- so a correlation over all translation moves is negative in a good
    piece.  Restricting rho to entrances is what stops that being an automatic C.

    An input that still scores C: a piece whose big entrances all run 0.2 s and
    whose small ones all run 0.8 s, so rho is negative inside the entrance
    class.  Or four in-scene repositions that jump more than a third of the
    frame on a single keyframe with nothing in between.
    """
    src = _get(ctx, "src")
    px = _get(ctx, "px")
    man = _get(ctx, "manifest") or {}
    fps = float(_get(ctx, "fps", 30.0))
    cuts = _get(ctx, "cuts") or []
    decl = (["shutterFrames"] if man.get("shutterFrames") else []) + \
        _declared_names(man, "impact")

    pre = _get(ctx, "strobe")
    if pre is not None:
        travel, strobe, moving, thr = pre
    elif px is not None:
        travel, strobe, moving, thr = strobe_scan(px, cuts, man, fps)
    else:
        travel, strobe, moving = {}, {}, set()
        thr = C11_STROBE_FRAC * (fps / C11_STROBE_FPS_REF)
    strobe_share = len(strobe) / max(len(moving), 1)
    ranked = strobe_rank(strobe)
    thr_px = thr * float(_get(ctx, "width", 1920) or 1920)

    if src is None:
        if not moving:
            return _row("C11", "distance and duration", None, {"movingFrames": 0},
                        na=True, basis="pixel",
                        note="nothing on the pixel channel moves; there is no "
                             "distance-duration relation to measure",
                        declarations=decl)
        band = "A" if strobe_share <= C11_A_STROBE else "B"
        note = (f"{len(strobe)} strobing frames (a hard edge over {thr_px:.0f} px "
                f"per frame at {int(_get(ctx, 'width', 1920) or 1920)} wide, "
                "no shutter)") if strobe else ""
        return _row("C11", "distance and duration", band,
                    {"strobeShare": round(strobe_share, 4),
                     "movingFrames": len(moving), "basis": "pixel"},
                    rank_worst(ranked),
                    (note + "; " if note else "")
                    + "reduced confidence: rho needs the source channel",
                    basis="pixel: tracked component travel", declarations=decl)

    cs = compound_moves(ctx)
    no_strobe_channel = (pre is None and px is None)
    entr = [c for c in cs
            if c["ch"] == "translate" and c["role"] == "entrance"
            and c["travel"] > 1.0 and not c["ambient"] and not c["mechanical"]
            and not c["transition"]]
    dists = [c["travel"] for c in entr]
    durs = [c["dur"] * 1000.0 for c in entr]
    enough = len(entr) >= C11_MIN_N
    rho = spearman(dists, durs) if enough else float("nan")
    outliers, worst = [], []
    if enough:
        ks = [_k_of_dist(d, src.W) for d in dists]
        base = float(np.median([du / k for du, k in zip(durs, ks)]))
        for c, d, du, k in zip(entr, dists, durs, ks):
            exp = base * k
            if du < C11_OUTLIER_LO * exp or du > C11_OUTLIER_HI * exp:
                outliers.append(c)
                worst.append((abs(math.log(max(du, 1e-6) / max(exp, 1e-6))),
                              c["onsetF"]))
    outlier_rate = len(outliers) / max(len(entr), 1)

    # the 1/3 rule is for element REPOSITIONS inside a scene. Transitions and
    # camera moves are exempt BY CLASS rather than by declaration, and a
    # compound with more than one leg HAS an intermediate keyframe
    third = []
    for c in cs:
        if c["ch"] != "translate" or c["role"] != "reposition":
            continue
        if c["ambient"] or c["mechanical"] or c["transition"]:
            continue
        if abs(c["cxTo"] - c["cxFrom"]) < C11_THIRD_RULE * src.W \
                and abs(c["cyTo"] - c["cyFrom"]) < C11_THIRD_RULE * src.H:
            continue
        if c["legs"] > 1 or c["roundTrip"]:
            continue
        third.append(c)
    nv = len(third)

    if math.isnan(rho) and not strobe and nv == 0 and no_strobe_channel:
        return _row("C11", "distance and duration", None,
                    {"entrances": len(entr), "thirdRuleViolations": 0}, na=True,
                    basis="source only",
                    note=(f"only {len(entr)} entrance translation(s) and no pixel "
                          "channel: neither rho nor strobe can be measured"),
                    declarations=decl)
    rho_ok_s = math.isnan(rho) or rho >= C11_S_RHO
    rho_ok_a = math.isnan(rho) or rho >= C11_A_RHO
    if rho_ok_s and outlier_rate <= C11_S_OUTLIER and nv == 0 and not strobe \
            and not no_strobe_channel:
        band = "S"
    elif rho_ok_a and outlier_rate <= C11_A_OUTLIER and nv <= C11_A_VIOLATIONS \
            and strobe_share <= C11_A_STROBE:
        band = "A"
    elif outlier_rate <= C11_B_OUTLIER and nv <= C11_B_VIOLATIONS:
        band = "B"
    else:
        band = "C"
    neg_rho = (not math.isnan(rho)) and rho < 0
    if neg_rho or nv > C11_C_VIOLATIONS:
        band = "C"
    if math.isnan(rho) and band in ("S", "A"):
        # the distance-duration relation is the criterion; a clean strobe scan
        # on a piece with too few entrances to correlate is evidence of one
        # half and cannot award the other
        band = "B"

    # the note names the condition that actually SET the band, and the frames it
    # names lead worstFrames
    note = ""
    if neg_rho:
        note = "longer entrances take less time than short ones"
    elif nv > C11_A_VIOLATIONS:
        note = (f"{nv} reposition(s) cross a third of the frame with no "
                "intermediate keyframe")
        worst = [(5.0, c["onsetF"]) for c in third] + worst
    elif outlier_rate > C11_A_OUTLIER:
        note = (f"{len(outliers)}/{len(entr)} entrances sit outside 0.5x to 2x of the "
                "distance-duration curve")
    elif strobe:
        note = (f"{len(strobe)} strobing frames ({strobe_share:.1%} of moving frames, "
                f"a hard edge over {thr_px:.0f} px per frame at "
                f"{int(_get(ctx, 'width', 1920) or 1920)} wide, no shutter)")
        worst = ranked + worst
    elif nv:
        note = (f"{nv} reposition(s) cross a third of the frame with no "
                "intermediate keyframe")
        worst = [(5.0, c["onsetF"]) for c in third] + worst

    measured = {"rho": (None if math.isnan(rho) else round(rho, 3)),
                "entrances": len(entr), "outlierRate": round(outlier_rate, 3),
                "thirdRuleViolations": nv,
                "strobeShare": (None if no_strobe_channel
                                else round(strobe_share, 4)),
                "strobeFrames": (None if no_strobe_channel else len(strobe)),
                "movingFrames": (None if no_strobe_channel else len(moving))}
    if no_strobe_channel:
        note = (note + "; " if note else "") + \
            "strobe not measured: no pixel channel, so S is out of reach"
    if math.isnan(rho):
        note = (note + "; " if note else "") + \
            (f"only {len(entr)} entrance translation(s): rho is not computable, "
             "so the row is capped at B")
    return _row("C11", "distance and duration", band, measured, rank_worst(worst),
                note,
                basis="source: entrance rho and the 1/3 rule; pixel: strobe scan",
                declarations=decl)


# =============================================================================
# C21 restraint                                                      weight 1
# =============================================================================

def _parent_map(src):
    """child index -> nearest TRACKED ancestor, from what the probe records.

    `parent` is the field that indexes this list; `parentIdx` counts the DOM and
    does not, so reading it walked to unrelated elements and the merge below
    never fired."""
    out = {}
    for i, e in enumerate(getattr(src, "elements", []) or []):
        p = e.get("parent")
        if p is None:
            continue
        try:
            p = int(p)
        except (TypeError, ValueError):
            continue
        if 0 <= p < len(src.elements) and p != i:
            out[i] = p
    return out


def _is_descendant(parent, child, maybe_ancestor):
    """True when maybe_ancestor is on child's parent chain."""
    seen, cur = 0, parent.get(child)
    while cur is not None and seen < 32:
        if cur == maybe_ancestor:
            return True
        cur = parent.get(cur)
        seen += 1
    return False


def _is_stagger(run):
    """A run of (onset, duration) pairs that is ONE gesture.

    Canon 2.2: one easing family across a stagger, vary start time only, and a
    per-character line runs 1.5-2.5 s. So a stagger is an even step with one
    duration, and it counts as one onset. A run of the same length whose members
    carry different durations is not a stagger, it is several things starting at
    once, which is what canon section 8 item 11 calls over-animated.
    """
    if len(run) < C21_STAGGER_MIN:
        return False
    steps = np.diff([f for f, _ in run]).astype(float)
    if len(steps) < 2 or steps.mean() <= 0:
        return len(run) >= C21_STAGGER_MIN and _one_duration(run)
    if float(steps.std() / steps.mean()) > C21_STAGGER_STEP_CV:
        return False
    return _one_duration(run)


def _one_duration(run):
    ds = np.array([d for _, d in run], dtype=float)
    med = float(np.median(ds))
    if med <= 0:
        return False
    return bool(np.all(np.abs(ds - med) <= C21_STAGGER_DUR_TOL * med))


def c21_restraint(ctx):
    """Canon C21, new.  Concurrent ambient motions; hero moves in flight;
    onsets per 10 frames.

    S  exactly one ambient during breathe, one hero move in flight
    C  >= 3 concurrent ambient tweens, or > 1 onset per 10 frames sustained

    The ceiling that balances the presence criteria: nothing else in the rubric
    caps motion density, so a piece that gives every headline a wind-up, a
    trailing shadow and its own ease outscores a restrained card.  Canon 1.5:
    one ambient motion, not three, because three columns at 6 px compound to
    18 px of competing motion.

    Onsets are counted PER GROUP, collapsing a stagger to one gesture.  Canon
    2.2 prescribes per-character sweeps of 1.5-2.5 s for a full line, and a
    per-element count turns every one of them into a C.  A declared lockup or
    trigger group counts as one element for the same reason canon C3 counts it
    as one.  Ambient concurrency is read during BREATHE -- the frames where no
    hero move is in flight -- because a second ambient under an active hero is
    masked by it, while a second ambient on a held card is the defect.

    An input that still scores C: three columns each drifting on their own sine
    loop under a held end card, or a beat in which eight separate elements each
    start their own move inside forty frames.
    """
    src = _get(ctx, "src")
    man = _get(ctx, "manifest") or {}
    beats = _get(ctx, "beats") or []
    fps = float(_get(ctx, "fps", 30.0))
    if src is None:
        return _row("C21", "restraint", None, {}, na=True, basis="none",
                    note="concurrent ambient motions need the source channel")
    n = int(getattr(src, "frames", 0))
    if n <= 0:
        return _row("C21", "restraint", None, {}, na=True, basis="none",
                    note="no frames")

    # ---- concurrent ambient ------------------------------------------------
    amb = [m for m in src.moves if m.get("ambient") or m.get("repeat")]
    conc = np.zeros(n, dtype=np.int32)
    for m in amb:
        a = int(clamp(m["onsetF"], 0, n - 1))
        b = int(clamp(m["settleF"] + 1, 1, n))
        conc[a:b] += 1
    max_amb = int(conc.max()) if n else 0
    amb_at = int(np.argmax(conc)) if n else 0

    # ---- hero moves in flight ---------------------------------------------
    hero_els = hero_elements(ctx)
    inflight = np.zeros(n, dtype=np.int32)
    # canon C21's "one hero move in flight" is a rule about a BEAT. Two heroes
    # overlapping across a cut is canon 1.5's overlapping action -- the
    # outgoing card leaving while the incoming one arrives is the handoff C17
    # grades, and every velocity-matched cut in the medium produces it. Counted
    # across the whole timeline the row charged a correct handoff as
    # over-animation, so the concurrency is counted per beat and the frames of
    # different beats never collide.
    def beat_of(f):
        for i, (a, b) in enumerate(beats):
            if a <= f <= b:
                return i
        return -1
    per_beat = {}
    for c in compound_moves(ctx):
        if c["el"] not in hero_els or c["ambient"] or c["mechanical"]:
            continue
        a = int(clamp(c["onsetF"], 0, n - 1))
        b = int(clamp(c["settleF"] + 1, 1, n))
        bi = beat_of(int(c["onsetF"]))
        lane = per_beat.setdefault(bi, np.zeros(n, dtype=np.int32))
        lane[a:b] += 1
    for lane in per_beat.values():
        inflight = np.maximum(inflight, lane)
    max_flight = int(inflight.max()) if n else 0
    flight_at = int(np.argmax(inflight)) if n else 0

    # ---- ambient during BREATHE: the frames where no hero is in flight -----
    breathe = conc[inflight == 0]
    amb_breathe = int(breathe.max()) if len(breathe) else 0

    # ---- gesture onsets per 10 frames, sustained across a beat -------------
    win = fscale(C21_STAGGER_WINDOW_F30, fps)
    min_beat = fscale(C21_MIN_BEAT_F30, fps)
    decl_early = _declared_names(man, "lockups") +         _declared_names(man, "triggerGroups")
    lockups = man.get("lockups", []) or []
    triggers = man.get("triggerGroups", []) or []
    groups, owner = {}, {}
    for m in src.moves:
        if m.get("ambient") or m.get("mechanical") or m.get("kind") == "other":
            continue
        if m.get("dur", 0) <= 1e-9:
            continue
        try:
            g = src.group_of(m["el"])
        except Exception:
            g = f"el{m['el']}"
        for i, names in enumerate(lockups):
            if src.is_named(m["el"], set(names)):
                g = f"lockup{i}"
                break
        else:
            for i, names in enumerate(triggers):
                if src.is_named(m["el"], set(names)):
                    g = f"trigger{i}"
                    break
        # a declared lockup or trigger group is one element, exactly as canon C3
        # counts it; otherwise the clip is the unit a stagger is detected inside
        # ... and inside a clip, one ROLE is one stagger. The "Introducing"
        # cascade runs eleven entrances and eleven exits interleaved; treating
        # the mixture as one run made it twenty-two separate onsets and put a
        # finished film at 3.9 per 10 frames, so the two have to be separated.
        band = int(round(math.log(max(float(m["dur"]), 1e-3)) / math.log(1.25)))
        key = (g if g.startswith(("lockup", "trigger")) else
               f"clip:{m.get('clip')}", band)
        items = groups.setdefault(key, [])
        items.append((int(m["onsetF"]), float(m["dur"])))
        owner.setdefault(key, []).append((int(m["onsetF"]), int(m["el"]),
                                          int(m["settleF"])))
    events, staggers = [], 0
    for _key, items in groups.items():
        items.sort()
        runs, cur = [], [items[0]]
        for it in items[1:]:
            if it[0] - cur[-1][0] <= win:
                cur.append(it)
            else:
                runs.append(cur)
                cur = [it]
        runs.append(cur)
        for run in runs:
            if _is_stagger(run):
                events.append(run[0][0])
                staggers += 1
            else:
                events.extend(f for f, _d in run)
    # an ONSET is a frame on which something starts, not a tween. Three chart
    # bars that grow together from one frame at three durations are one onset
    # and one gesture; whether they should start together at all is C3's
    # question, and counting them here charged the same simultaneity twice.
    # A PARENT AND ITS CHILDREN ARE ONE GESTURE. Canon 1.5 makes the
    # relationship explicit -- "child lag 50-150 ms behind parent; sibling
    # GROUPS offset by about 3 frames, not per element" -- so a container that
    # starts moving and three of its own spans that follow it inside the stagger
    # window are one designed thing, not four. The morph card of both replicas
    # is exactly that shape: `#morph-line` repositions over 25 frames while
    # three of its own letters cross-fade out at twelve, and the durations are
    # deliberately different, so no duration band and no stagger test can see
    # that they belong together. Counting them separately put four onsets in a
    # 24-frame beat and scored a finished film C for over-animation on one card
    # resolving. Read from the DOM parent chain the probe records, so nothing is
    # declared.
    parent = _parent_map(src)
    flights = []
    for key, rows in owner.items():
        for (f, el, settle) in rows:
            flights.append((f, el, settle))
    drop = set()
    for (f, el, _settle) in flights:
        for (pf, pel, psettle) in flights:
            if pel == el or not _is_descendant(parent, el, pel):
                continue
            if pf <= f <= max(psettle, pf) and f - pf <= win:
                drop.add((f, el))
                break
    kept = set(f for (f, el, _s) in flights if (f, el) not in drop)
    if kept:
        events = [f for f in events if f in kept]

    same = fscale(1, fps)
    events.sort()
    merged = []
    for f in events:
        if not merged or f - merged[-1] > same:
            merged.append(f)
    events = merged

    dense, dense_at, dense_end = 0.0, None, None
    for (a, b) in beats:
        if b - a < min_beat:
            continue
        k = sum(1 for f in events if a <= f <= b)
        rate = k / ((b - a + 1) / 10.0)
        if rate > dense:
            dense, dense_at, dense_end = rate, a, b

    if len(events) < C21_MIN_GESTURES:
        return _row("C21", "restraint", None,
                    {"gestures": len(events), "maxConcurrentAmbient": max_amb,
                     "heroesInFlight": max_flight}, na=True,
                    basis="source: ambient concurrency, hero flight, onset rate",
                    note=f"only {len(events)} gesture(s): there is nothing here to "
                         "be restrained about",
                    declarations=decl_early)
    if amb_breathe <= C21_S_AMBIENT and max_flight <= C21_S_HERO_IN_FLIGHT \
            and dense <= C21_ONSETS_PER_10:
        band = "S"
    elif amb_breathe <= C21_A_AMBIENT and max_flight <= C21_A_HERO_IN_FLIGHT \
            and dense <= C21_ONSETS_PER_10:
        band = "A"
    else:
        band = "B"
    if max_amb >= C21_C_AMBIENT or dense > C21_ONSETS_PER_10:
        band = "C"

    note = ""
    if max_amb >= C21_C_AMBIENT:
        note = (f"{max_amb} ambient tweens run at once at f{amb_at}; a scene is alive "
                "with ONE, and three columns at 6 px compound to 18")
    elif dense > C21_ONSETS_PER_10:
        note = (f"{dense:.1f} gesture onsets per 10 frames sustained across the beat "
                f"f{dense_at}-{dense_end}")
    elif max_flight > C21_S_HERO_IN_FLIGHT:
        note = f"{max_flight} hero moves in flight at once at f{flight_at}"

    worst = []
    if dense > C21_ONSETS_PER_10 and dense_at is not None:
        worst.append((3.0, dense_at))
    if max_amb >= C21_A_AMBIENT:
        worst.append((2.0, amb_at))
    if max_flight > C21_S_HERO_IN_FLIGHT:
        worst.append((1.0, flight_at))
    decl = decl_early
    measured = {"maxConcurrentAmbient": max_amb, "ambientDuringBreathe": amb_breathe,
                "heroesInFlight": max_flight, "onsetsPer10": round(dense, 2),
                "gestures": len(events), "staggers": staggers,
                "groups": len(groups)}
    return _row("C21", "restraint", band, measured, rank_worst(worst), note,
                basis="source: ambient concurrency, hero flight, grouped onset rate",
                declarations=decl)


# =============================================================================

CRITERIA = (c1_ease_discipline, c2_ease_vocabulary, c6_settle_quality,
            c10_timing_contrast, c11_distance_duration, c21_restraint)


def all_criteria(ctx):
    """The motion family in id order. The integrator calls this once and
    appends the rows to its own table."""
    return [fn(ctx) for fn in CRITERIA]


# =============================================================================
# __main__: grade the motion family from a dumped context, for calibration.
#
#   python crit_motion.py <composition dir> [render.mp4]
#
# Loads <dir>/.analysis/probe1080/{tracks,tweens}.json (or .analysis/probe/, or
# .probe/) plus <dir>/grade.json, builds the source channel with grade-mg.py's
# own Source class, optionally decodes a render for C11's strobe half, and
# prints the six rows. The audio channel is not built, so C10 stays on its
# free branch.
# =============================================================================

def _load_grade_mg():
    import importlib.util
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location(
        "grade_mg", os.path.join(here, "grade-mg.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _main(argv):
    import json
    import os
    if len(argv) < 2:
        print("usage: python crit_motion.py <composition dir> [render.mp4]")
        return 2
    comp = os.path.abspath(argv[1])
    man = {}
    gj = os.path.join(comp, "grade.json")
    if os.path.exists(gj):
        with open(gj, encoding="utf-8") as f:
            man = json.load(f)
    fps = float(man.get("fps", 30))
    mod = _load_grade_mg()
    src = None
    for sub in (".analysis/probe1080", ".analysis/probe", ".probe"):
        t = os.path.join(comp, sub, "tracks.json")
        w = os.path.join(comp, sub, "tweens.json")
        if os.path.exists(t) and os.path.exists(w):
            with open(t, encoding="utf-8") as f:
                tracks = json.load(f)
            with open(w, encoding="utf-8") as f:
                tweens = json.load(f)
            src = mod.Source(tracks, tweens, fps, man)
            break
    if src is None:
        raise SystemExit(f"crit_motion: no probe dump under {comp}")
    cuts = sorted(int(c) for c in man.get("cuts", [0]))
    px = None
    if len(argv) > 2 and os.path.exists(argv[2]):
        px = mod.Pixel(argv[2], fps, 0, int(src.W), int(src.H))
        cuts, _ = mod.detect_cuts(px, man, src)
        beats = mod.beats_from_cuts(cuts, px.n, px)
    else:
        beats = []
        for i, c in enumerate(cuts):
            e = cuts[i + 1] - 1 if i + 1 < len(cuts) else src.frames - 1
            if e > c:
                beats.append((c, e))
    ctx = {"src": src, "px": px, "audio": None, "manifest": man, "fps": fps,
           "width": int(src.W), "height": int(src.H), "frames": src.frames,
           "cuts": cuts, "beats": beats, "fitted": False}
    cms = compound_moves(ctx)
    print(f"  {os.path.basename(comp)}: {src.frames} frames at {fps} fps, "
          f"{len(src.moves)} tweens, {len(cms)} compound moves, "
          f"{len(beats)} beats, register {_register(ctx)}"
          + (", pixel channel" if px is not None else ", source only"))
    print()
    for r in all_criteria(ctx):
        band = "N/A" if r["na"] else r["band"]
        meas = ", ".join(f"{k}={v}" for k, v in r["measured"].items())
        print(f"  {r['id']:<5s}{r['name']:<22s}w{r['weight']} {band:<4s}{meas}")
        if r["note"]:
            print(f"        -> {r['note']}")
        if r["worstFrames"]:
            print(f"        worst@ {r['worstFrames']}")
        if r["declarations"]:
            print(f"        declarations used: {len(r['declarations'])}")
    print()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_main(sys.argv))
