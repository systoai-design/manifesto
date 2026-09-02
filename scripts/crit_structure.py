#!/usr/bin/env python3
"""
crit_structure.py -- the STRUCTURE family of the corrected rubric.

Spec: references/canon.md section 7 (twenty-four
criteria, four gates, weights 2 / 1 / 0). Where canon restates a band, canon
wins. Where it does not, the measurement machinery and the shared definitions
of move, onset, settle, progress curve and manifest shape come from
grading-rubric.md, which canon supersedes but does not replace as plumbing.
Observed practice in playlist-lessons.md outranks both.

This module owns six criteria, eight report rows:

    C4   hold ratio                     weight 1
    C5   frame integrity                weight 1   (no longer a gate)
    C17  transition design              weight 2
    C18  audio sync                     weight 1
    C18D audio delivery                 weight 0   GATE
    C19  reveal craft and motion blur   weight 2   (new)
    C23  encode and delivery QC         weight 1   (new)
    C23D duration and cadence           weight 0   GATE (new)

Every function has the same signature and returns the same shape:

    def c4_hold_ratio(ctx) -> dict:
        {"id": "C4", "name": "hold ratio", "band": "S|A|B|C|None",
         "weight": int, "gate": bool, "na": bool, "measured": {...},
         "worstFrames": [int], "basis": str, "note": str,
         "declarations": [str]}

`declarations` names every manifest claim the row actually consumed, so the
report can print the declaration budget canon requires: the number of
declarations, and the number of criteria whose band improved because of one.
A declaration is a claim about intent and has to be visible as one.


THE CONTEXT OBJECT
------------------
`ctx` is built once by the integrator and passed to every criterion. Anything
with these attributes works; grade-mg.py's own objects satisfy it as they
stand.

REQUIRED

  ctx.fps        float   delivered frame rate (grade-mg.py: v["fps"])
  ctx.n_frames   int     decoded frame count, == ctx.px.n
  ctx.width      int     render width in pixels
  ctx.height     int     render height in pixels
  ctx.render     str     path to the delivered mp4; C5 and C23 re-open it at
                         full resolution and canon requires that
  ctx.manifest   dict    grade.json
  ctx.cuts       list[int]        cut frames, declared or detected, ascending
  ctx.beats      list[(int,int)]  content runs, from beats_from_cuts
  ctx.video      dict    ffprobe_video(): fps, frames, width, height, duration,
                         pix_fmt, color_range, color_primaries, color_transfer
  ctx.declared   dict|None  the composition's own data-* attributes:
                         {"duration","fps","width","height"}; C23D is the gate
                         on the first of those and goes N/A without it

  ctx.px         the PIXEL channel, a grade-mg.py Pixel. Used here:
                   .n .fps .width .height .path
                   .grey        (n, 360, 640) uint8 luma at the decode size
                   .ground      (n,) per-frame median luma
                   .mask .core  (n, 360, 640) bool ink and type-core masks
                   .ink_frac    (n,) ink share, for blank and cut work
                   .frame_delta (n,) mean absolute luma step at the decode size
                   .changed_frac(n,) share of pixels that moved at all
                   .tracks      tracked components, for the strobe scan
                   .duplicates()-> (dup, meanLevels, changedFrac) at FULL
                                 resolution on luma. Only the two statistics
                                 are read; this module re-thresholds them from
                                 its own constants.

  ctx.src        the SOURCE channel, a grade-mg.py Source, or None. Used here:
                   .frames .fps .W .H .diag .register .manifest
                   .elements .clips .moves .num .prop() .style_at()
                   .is_named() .still_delta() .box_at()
                 Without it C4 falls back to the pixel stillness test, C17 to
                 the pixel handoff signature, C19's reveal half goes N/A and
                 every affected row says so in `note`.

  ctx.audio      a grade-mg.py Audio, or None. Used here:
                   .present .stream .onsets .hits .lufs .true_peak
                   .sample_peak .rate .channels .grid .sig
                   .bar_lines(fps, n_frames)

OPTIONAL, used when present and recomputed here when not

  ctx.strobe     (travel, strobe, moving, thr[, fast]) from grade-mg.py's
                 strobe_scan. C11 and C19 must read the SAME scan or the two
                 rows can disagree about which frames are fast. `strobe` has
                 declared shutter passes already removed, which is what C11
                 charges; `fast` is the set BEFORE those exclusions, which is
                 what C19 has to measure blur coverage over, because coverage
                 computed over a set the covered frames were removed from
                 reports 0 % by construction. A four-element tuple is read as
                 fast == strobe.
  ctx.heroes     the hero move per beat, from hero_moves(src, beats, px)
  ctx.cache      dict this module may write intermediate results into


WHAT CHANGED, AND WHY
---------------------
C5 is renamed Frame integrity, is no longer a gate, and now measures flash
frames at cuts plus duplicate runs against a DECLARED CADENCE at full
resolution on luma. Four things were wrong with the detector it replaces, and
the first of them scored S on an amateur control built to contain duplicate
frames:

  1. It reported through ffmpeg's `mpdecimate`. That filter compares each
     frame against the last frame it KEPT, not against the previous frame, and
     its hi/lo/frac thresholds are 8x8 block SAD sums tuned for telecine. Its
     output is a decimated stream, so a run of n duplicates and n isolated
     duplicates are indistinguishable and no run boundary survives. On
     _controls/bad the row printed mpdecimateDrops 0 while the file carries a
     deliberate three-frame freeze at f88-f90 that mpdecimate itself drops
     (verified: 240 frames in, 238 out, dropped at pts_time 2.9667 and 3.0).
  2. Its direct-difference fallback wanted a changed-pixel share under 0.0002.
     Measured on the delivery-quality h264 of that same control, BIT-IDENTICAL
     source frames come back at 0.0002 to 0.00033 of pixels over two code
     values and 0.007 to 0.014 mean levels. The threshold sat inside the
     codec's own noise floor on duplicates, so it could only ever fire on a
     lossless render.
  3. It measured at the 640x360 decode. Canon requires full resolution on
     luma: averaging a 1920x1080 render into 3x3 blocks pushes real sub-pixel
     ambient motion under any duplicate threshold and manufactures duplicates
     in the other direction.
  4. Off by one on the run. A duplicate FLAG at frame f means f equals f-1, so
     k consecutive flags are k+1 identical frames. Counting a "run" in
     identical frames while comparing it against a flag-count minimum makes a
     three-frame freeze invisible, which is exactly the control's defect.

C17's gap cadence was the blanket set 1..8 plus whatever the piece used, so no
1-2 frame blank could ever be off cadence and C5's flash test could not fire at
all. The cadence here is the declared list plus the lengths the piece actually
repeats, and nothing else. C17 also read direction off the centroid alone,
which reports a scale-through handoff, where the outgoing card shrinks and the
incoming one settles from oversize, as zero motion on both sides and therefore
as a direction break; and it split one device into several transition types by
gap length, so a card film with one primary dip reported six types and no
primary. Motion is now a translation-and-scale vector, the type census is taken
from the dominant pair on each side, and carrying motion through the cut, which
no role label can see, is a designed handoff in its own right.

C4 asked every beat for 0.30 of its frames as stillness. That contradicts this
criterion's own genre band, which grades a continuous-camera piece correct at a
piece hold of 0.05 to 0.35 and therefore cannot also want 0.30 of every beat;
and it asked it of two-frame beats inside a rapid-fire run, where 0.30 is less
than one frame. The floor is now the genre floor capped at 0.30, runs of cuts
closer than ten frames at 30 fps merge into one unit, and the settle is the
frame where motion becomes imperceptible rather than where the tween ends,
which on a film built from hard eases was charging the whole tail of every
`expo.out` as motion.

Three measurements here are REPORT ONLY and never move a band, because no
reference-free version of them is trustworthy enough to charge: chroma bleed
(nothing separates a thin saturated stroke that bled from a coloured ground,
which is chromatic everywhere and ink nowhere), the raw-onset hit rate where no
tempo grid exists, and runs where the composition's own track moved and the
delivered luma did not.

C18's bias sign was inverted against its own stated convention. The rubric and
both standards it cites define delta as positive when SOUND LEADS; the code
computed nearest_onset - visual_event, which is positive when sound TRAILS,
then applied the asymmetric +40 ms early / -100 ms late limits to it. Here
delta = t_visual - t_audio, the window centre is one frame NEGATIVE (the
editor's trick puts the cut one frame ahead of the hit), and the two limits
land on the sides the standards put them.

C19 counted a blurred frame sitting on a cut and never let it touch the band,
and let a single `echoTrails` entry cover every fast frame in the film. Both
are fixed: a blurred frame on a cut frame cannot score S, and an echo trail
covers only the frames or the named element it declares.


MEASUREMENT CAUTIONS, carried from grade-mg.py because each cost an hour once
  - decoding a RANGE gives (n, H, W, 3); reduce over axis 3, never axis 2
  - clip windows are [start, start + duration); bias both ends inward
  - smooth an ink count before looking for reversals, grain manufactures them
  - never measure motion on a bounding box, use the ink COUNT integral
  - exempt by NAME through the manifest, never by loosening a threshold
  - worstFrames is ranked by SEVERITY, never by frame number
"""

import json
import math
import os
import re
import subprocess

import numpy as np


# =============================================================================
# CONSTANTS.  Every threshold this family uses, named per criterion, and
# nowhere else.  Frame counts are quoted at the authoring rate of 30 fps and
# scaled to the delivered rate by fscale().
# =============================================================================

# ---- shared with grade-mg.py, restated so this module imports nothing -------
DEC_W, DEC_H = 640, 360          # the pixel channel working size
CUT_BLANK_INK = 0.002            # ink fraction below this is a blank frame
CUT_GROUND_FLIP = 20.0           # luma step in the frame's median = ground flip
BAND_ORDER = ["S", "A", "B", "C"]
DEFAULT_GENRE = "mixed"
DEFAULT_REGISTER = "corporate"
DEFAULT_DELIVERY = None          # there is no defensible default; C18D says so
SPATIAL_PROPS = {"x", "y", "xPercent", "yPercent", "scale", "scaleX", "scaleY",
                 "rotation", "rotationX", "rotationY", "rotationZ", "clipPath",
                 "translateX", "translateY", "top", "left", "width", "height"}
TRANSLATE_PROPS = {"x", "y", "xPercent", "yPercent", "translateX", "translateY"}

# ---- C4 hold ratio ---------------------------------------------------------
C4_S_BEAT_HOLD = 0.30            # every beat holds this share of its frames,
                                 # capped below by the genre's own floor. The
                                 # flat 0.30 contradicts this criterion's own
                                 # genre band: a continuous-camera piece is
                                 # graded correct at a piece hold of 0.05 to
                                 # 0.35 and cannot also hold 0.30 of every beat.
                                 # The 0.30 is inference; the genre bands and
                                 # the 100 ms stillness below it are not.
C4_MIN_BEAT_FRAMES = 10          # at 30 fps. Cuts closer together than this are
                                 # a rapid-fire run and are ONE unit for the
                                 # stillness test: 0.30 of a ten-frame beat is
                                 # the 100 ms of stillness the rule descends
                                 # from, and 0.30 of a two-frame beat is
                                 # nothing at all. Canon section 6 already
                                 # treats a rapid-fire run as one event.
C4_S_GAP_MS = 100.0              # LottieFiles "100-200 ms stillness after resolution"
C4_S_LEAD_MIN_MS = 100.0         # measured from FRAME 0 OF THE PIECE, not from
                                 # the first detected cut, and only the lower
                                 # bound is charged. grading-rubric.md is
                                 # explicit that the HyperFrames guardrail
                                 # "don't start at t=0" is "about the
                                 # composition's first frame and its poster
                                 # frame": the tell is that the first thing the
                                 # viewer sees is already in motion. Measured
                                 # from the first CUT it is 0 by construction
                                 # on any film whose opening card arrives on
                                 # its own detected boundary, which is how a
                                 # two-tween control card scored C on a beat
                                 # that holds 82 % of its frames. The old upper
                                 # bound is gone with its own reason: a
                                 # deliberate black lead-in is a structural
                                 # choice the piece hold ratio and C5's
                                 # declared holds already grade, and charging
                                 # it here made a broadcast ad's 37-frame
                                 # lead-in a stillness fault.
C4_LEAD_BLOCKS = "A"             # a lead fault caps the row here. It never
                                 # produces a C: canon's C4 C column is the
                                 # genre band and the per-unit hold share, and
                                 # nothing else.
C4_A_BEATS, C4_B_BEATS = 0.90, 0.75
C4_A_PIECE = (0.25, 0.65)        # The A and B rows band the PIECE hold on a
C4_B_PIECE = (0.15, 0.80)        # wide window, not on the genre band. Canon
                                 # restates C4's S row and its C row and does
                                 # not restate A or B, so the machinery is the
                                 # superseded rubric's, which reads "A: >= 90 %
                                 # of beats meet the per-beat rules; piece
                                 # holdRatio in 0.25 to 0.65" and "B: >= 75 % of
                                 # beats; piece holdRatio in 0.15 to 0.80". The
                                 # genre band belongs to S (inside it) and to C
                                 # (outside it by more than 0.10). Requiring the
                                 # genre band for A as well left no path above B
                                 # for any film four points under a floor canon
                                 # itself gives ten points of slack.
C4_GENRE_PIECE = {               # canon C4: genre parameterised, not universal
    "continuous-camera": (0.05, 0.35),
    "mixed": (0.25, 0.65),
    "card-based": (0.45, 0.85),
}
C4_C_PIECE_SLACK = 0.10          # C is "outside the band by more than 0.10"
# The settle frame is where motion becomes IMPERCEPTIBLE, not where the tween
# ends (canon section 6). For expo.out the element is at 99% of target at 0.66
# of the duration, so the numeric settle marks the whole tail as "moving" and a
# film built on hard eases reports a hold ratio it does not have.
C4_IMPERCEPTIBLE_PX = 1.0        # px per frame ...
C4_IMPERCEPTIBLE_REF_H = 1080.0  # ... at this frame height, scaled linearly
C4_OPACITY_PX_EQUIV = 100.0      # 0.01 of opacity per frame reads about as
                                 # strongly as 1 px of travel per frame
C4_CONTINUATION_FRAMES = 1       # a tween starting this soon after the previous
C4_CONTINUATION_EPS = 0.75       # settle, at the value it ended on, is one
                                 # motion authored in segments, not a re-fire
C4_PIXEL_MOVING_FRAC = 0.0005    # pixel fallback: share of pixels that moved

# ---- C5 frame integrity ----------------------------------------------------
# Measured at FULL resolution on luma at one code value. On delivery-quality
# h264, bit-identical source frames give 0.007 to 0.014 mean levels and 0.0002
# to 0.0003 of pixels over two code values; moving frames give 3 to 7 levels
# and 0.027 or more. Two orders of magnitude separate them, which is why these
# numbers are safe and why the old 0.0002 was not.
C5_DUP_CODE_VALUE = 2            # a pixel moving by more than this really moved
C5_DUP_MEAN_LEVELS = 0.10        # mean absolute luma difference over the frame
C5_DUP_CHANGED_FRAC = 0.005      # share of pixels over C5_DUP_CODE_VALUE
C5_DUP_RUN_MIN_FLAGS = 2         # at 30 fps: 2 flags = 3 identical frames
C5_A_RUN_HELD = 2                # A tolerates one run of at most this many
                                 # IDENTICAL frames, at 30 fps
C5_B_RUNS = 3                    # more undeclared runs than this is C
C5_C_RUN_HELD = 8                # ... and so is a SINGLE run of more than this
                                 # many identical frames, at 30 fps. This is
                                 # the "any run > 8 frames" clause of the C5
                                 # band table, and without it there was no path
                                 # from run LENGTH to the criterion's own worst
                                 # band at all: a 31-frame frozen picture in an
                                 # 8 s film banded B, because both length terms
                                 # in the chain (a run over 1.5 s, and a run
                                 # over the A ceiling) terminated at B. The
                                 # worst single form of the defect this
                                 # criterion exists to catch could not reach C.
                                 # 8 frames is the upper end of the blank-gap
                                 # runs the segment model treats as rhythm.
C5_HOLD_AT_CUT_MAX = 45          # frames at 30 fps: 1.5 s. A run of identical
                                 # frames that ends at a cut is the hold of
                                 # move/hold/cut and is not charged, but only up
                                 # to here. Canon 2.4 puts most brand end cards
                                 # at "static for 1.5-3 s" and asks for the
                                 # cadence to be DECLARED; past 1.5 s the piece
                                 # has to say the freeze is deliberate, which is
                                 # what `holds` is for
C5_HOLD_AT_CUT_TOL = 2           # frames at 30 fps. A run of identical frames
                                 # that ends this close to a cut, or to the end
                                 # of the film, is the HOLD of move / hold /
                                 # cut. Canon section 8 item 8 states the
                                 # duplicate tell as "duplicate frames in a
                                 # segment that SHOULD MOVE", and C4 grades a
                                 # card-based film CORRECT at a hold ratio of
                                 # 0.45 to 0.85: charging every one of those
                                 # holds here made the two criteria pull
                                 # against each other and asked a 26-card film
                                 # for one declaration per card to restate what
                                 # its own timeline already says. A run that
                                 # does NOT end at a cut and runs past
                                 # C5_C_RUN_HELD is the other thing entirely --
                                 # a frozen picture mid-beat, which is the form
                                 # the amateur control carries at f88.
C5_FLASH_MAX_FRAMES = 2          # a 1-2 frame blank or wrong frame at a cut
C5_FLASH_CUT_TOL = 2             # frames either side of a cut, at 30 fps
C5_DEAD_HOLD_S = 1.5             # a declared hold with no ambient, this long
C5_HOLD_EXEMPT_MAX = 0.35        # declared holds may not exempt more of the
                                 # runtime than this, EXCEPT that the cap never
                                 # falls below the genre's own hold ceiling
                                 # (C4_GENRE_PIECE). An exemption list derivable
                                 # from the grader's own failure report is not
                                 # an exemption, which is what the cap is for;
                                 # but a flat 0.35 fires by construction on
                                 # card-based work, where C4 grades a piece
                                 # CORRECT at a hold ratio of 0.45 to 0.85 and
                                 # holding four fifths of the runtime is the
                                 # form. A three-second title card holding 69 of
                                 # its 90 frames lost the exemption for its own
                                 # single declared hold and was charged for
                                 # being a title card.
C5_CADENCE_EDGE_TOL = 1          # a declared segment may miss its own boundary
                                 # by one frame; the settle tail bleeds
C5_CADENCE_MIN_HOLD = 2          # hold 1 is not a cadence, it is every frame
C5_CADENCE_MAX_HOLD = 16         # BUCK's Mailchimp shorts run 1, 2, 4, 8 and
                                 # 16 fps inside one shot; past 16 it is a hold
C5_CADENCE_HONOURED = 0.50       # share of the expected duplicate frames the
                                 # segment must actually deliver, or the
                                 # declaration bought relief it did not earn
C5_A_HOLDS, C5_B_HOLDS = 1, 2    # dead holds tolerated at A and at B
C5_SOURCE_STILL_EPS = 0.05       # px per frame on the source channel; below
                                 # this the composition is frozen too
C5_QUANTISED_VISIBLE_PX = 0.5    # px per frame ...
C5_QUANTISED_REF_H = 1080.0      # ... at this frame height. Between the two
                                 # figures the composition drifts sub-pixel and
                                 # BOTH the codec and the eye read it as still,
                                 # so the delivered file is stalled whatever the
                                 # timeline says: canon grades the delivered
                                 # file. Above the upper figure real motion did
                                 # not survive the encode, which is a different
                                 # finding and is REPORT ONLY, because
                                 # still_delta also jumps when an element is
                                 # re-laid out and cannot carry a band on its
                                 # own

# ---- C17 transition design -------------------------------------------------
C17_SAME_START_FRAMES = 1        # "outgoing and incoming animate AT THE SAME T"
C17_BLANK_GAP_FRAMES = 8         # 1-8 frames of blank is rhythm; past that a
                                 # dip needs the piece's own cadence behind it
C17_GAP_CADENCE_TOL = 1          # a dip within a frame of the cadence
C17_CADENCE_MIN_USES = 2         # a gap length used at two cuts IS the cadence
C17_WINDOW_FRAMES = 12           # how far either side to look for a handoff
C17_VELOCITY_FLOOR = 0.5         # px/frame; below this a side is not moving
C17_SCALE_TO_PX = 0.5            # a scale change of ds moves an element's edge
                                 # about ds * diagonal / 2, so scale and travel
                                 # can be compared in one motion vector. Reading
                                 # direction off the centroid alone reports a
                                 # scale-through handoff, which is the commonest
                                 # card transition there is, as zero motion on
                                 # both sides and therefore as a direction break
C17_S_MIN_SPEED_SHARE = 0.30     # neither side below 30% of its own peak
C17_MIN_CUTS_FOR_S = 4           # canon's S row for this criterion is four
                                 # statistics -- designedShare, primaryShare,
                                 # nTypes and direction continuity -- and on one
                                 # or two cuts every one of them is true by
                                 # construction: one cut is 100 % designed, one
                                 # type and primaryShare 1.00. A weight-2 S
                                 # awarded from a single observation is the same
                                 # defect C10's max/min form had, and it is what
                                 # let a static title card with one boundary
                                 # outscore every finished film in the corpus.
                                 # Under this many cuts the row reports what it
                                 # saw and caps at A: no visible transition
                                 # defect, no demonstrated transition design.
C17_A_VMATCH = 0.5               # REPORTED, NOT BANDED. Canon 1.6 retires the
                                 # velocity-match percentage in as many words:
                                 # "Velocity match at a cut is direction
                                 # continuity, not a percentage. The widely
                                 # quoted ~5 % is not met by its own source's
                                 # worked example (909 px/s against 300 px/s,
                                 # 3:1 out)", and it gives the replacement --
                                 # same sign of travel on both sides, and
                                 # neither side below about 30 % of its own peak
                                 # on the cut frame. Both of those are measured
                                 # here already, as dirBreaks and slowAtCut. The
                                 # number that remains is a MAXIMUM over every
                                 # cut in the film, which is the statistic C10
                                 # abandoned for p90/p10 because one worst
                                 # observation is not a property of the piece:
                                 # all three professional films in the
                                 # calibration corpus carry one hard cut whose
                                 # two sides differ 6:1 in speed, and gating the
                                 # A row on it made A unreachable for a card
                                 # film by construction.
C17_S_PRIMARY_SHARE = 0.60       # "pick ONE primary (60-70%) plus 1-2 accents"
C17_S_NTYPES, C17_A_NTYPES = 3, 4
C17_S_DESIGNED, C17_A_DESIGNED, C17_B_DESIGNED = 1.0, 0.90, 0.75
C17_C_MIN_CUTS_FOR_TYPES = 4     # "a different type at every cut" needs cuts
C17_CROSSFADE_NOTE = 0.60        # report-only: the playlist's 200 finished
                                 # pieces are "graphic, never dissolves"
C17_REPLACE_CENTRE_FRAC = 0.06   # A REPLACE IN PLACE is the one edit whose
C17_REPLACE_BAND_RATIO = 2.0     # correct form is a hard swap. Canon 3.2:
C17_REPLACE_MIN_CARRY = 1        # "NEVER crossfade two states of the same
                                 # type. BINARY ARRIVALS for whips, typewriters
                                 # and visemes; a fade laid over a snap is the
                                 # commonest tell in HTML type animation." And
                                 # canon 3.1 calls the same construction a
                                 # regime of its own, "where the eye never
                                 # moves". So when one type block is re-set at
                                 # the same place and the same size with no gap,
                                 # the hard swap IS the designed device and
                                 # asking it to overlap or dissolve asks for the
                                 # tell. Measured on the delivered pixels: ink
                                 # centroid within 6 % of the frame diagonal
                                 # either side of the cut, and ink extent within
                                 # 2x, so a new card at a new size or in a new
                                 # place is not one. The test is on the VERTICAL
                                 # band only: a replace-in-place stream changes
                                 # its copy, so "that's where" becoming "six" at
                                 # the same size and the same place is 6.7x
                                 # narrower and is exactly the construction this
                                 # is here to recognise. What has to hold still
                                 # is where the eye is, which is the centroid,
                                 # and which type band it is reading.
                                 # Canon 3.3's guard applies -- "a piece
                                 # assembled entirely from independent
                                 # enter-hold-exit cards is a slideshow with
                                 # better easing. ADD AT LEAST ONE CONTINUITY
                                 # MOVE" -- so a film where nothing carries
                                 # across any edit gets none of this relief.
C17_KINDS = ("hard cut", "blank gap", "dip to ground", "crossfade", "push",
             "zoom", "iris", "blur-through", "object hand-off", "shape match",
             "grow-to-fill", "carried motion", "pop", "other")

# ---- C18 audio sync --------------------------------------------------------
C18_ONSET_QUARTILE = 0.75        # the strongest quartile of flux peaks are hits
C18_LOCK_MS = 40.0               # or one frame, whichever is larger
C18_WINDOW_CENTRE_FRAMES = -1.0  # NEGATIVE: delta is t_visual - t_audio, and
                                 # the editor's trick puts the cut one frame
                                 # AHEAD of the hit, so a correctly cut piece
                                 # sits one frame negative and a window centred
                                 # on zero reads it as sound late
C18_S_LOCK, C18_S_MEANABS = 0.80, 20.0
C18_A_LOCK, C18_A_HIT = 0.60, 0.40
C18_B_LOCK = 0.40
C18_C_BIAS_EARLY_MS = 40.0       # sound EARLY, the EBU R37 emission limit
C18_C_BIAS_LATE_MS = -100.0      # sound late, inside ITU-R BT.1359-1
C18_GRID_TOL_FRAMES = 2          # a cut within this of a bar line is on grid
C18_GRID_SHARE = 0.60            # this many cuts on grid and bars are the stat
C18_BEATS_PER_BAR = 4

# ---- C18D audio delivery (GATE) --------------------------------------------
C18D_LOUDNESS = {                # from the delivery enum, never from one film
    "broadcast": (-24.0, -22.0),         # EBU R128 -23 LUFS +/- 1 LU
    "web": (-16.0, -13.0),               # AES TD1008 -16 music, YouTube -14
    "social": (-16.0, -13.0),
}
C18D_TRUE_PEAK = {"broadcast": -1.0, "web": -1.0, "social": -1.0}
# A manifest loudnessTarget is INTERSECTED with the published window, never
# substituted for it: a declaration may hold the piece to a tighter target and
# may never widen the gate. This was the one gate a film could move on its own
# authority, and moving it by one LU was worth two bands.
C18D_LOUD_TOL_LU = 0.5           # EBU R128's own normalisation tolerance, and
                                 # the only slack the loudness gate grants on
                                 # the LOUD side. Replaces a symmetric 2 LU
                                 # slack that had no source and granted B for
                                 # being 2 LU hot
C18D_LOUD_TOL_LU = 0.5           # EBU R128's own normalisation tolerance. The
                                 # gate is ASYMMETRIC because delivery is: a
                                 # programme LOUDER than its target is turned
                                 # down by the platform with its true peak
                                 # already baked in, which is a delivery
                                 # failure, while one quieter than its target is
                                 # turned UP and loses nothing. So over the top
                                 # of the window by more than R128's tolerance
                                 # fails the gate; under the bottom caps the row
                                 # at B and prints the shortfall

# ---- C19 reveal craft and motion blur --------------------------------------
C19_OPACITY_TRAVEL = 0.05        # opacity plus travel under 5% of frame height
C19_SCALE_AMP = 0.10             # ... and a scale ramp under this fraction of
                                 # its own larger end. A card arriving from 0.4,
                                 # 0.82 or 1.46 is a scale reveal whatever its
                                 # centroid does, and the old test saw only
                                 # translation and scale-from-zero
C19_BLUR_AMP_PX = 3.0            # ... and a filter blur ramp under this many px
                                 # at 1080p. Canon 1.3 puts a real depth step at
                                 # 3-6 px, so a ramp at or above it is a
                                 # defocus reveal: not a structural device in
                                 # canon's list, but not a bare fade either
                                 # is still an opacity-only reveal
C19_S_OPACITY, C19_A_OPACITY, C19_B_OPACITY = 0.25, 0.40, 0.60
C19_S_DEVICES, C19_A_DEVICES = 2, 1
C19_SIGNALS_REPORT_ONLY = True    # `medSignalsPerCard` is canon 3.2's
                                  # concurrent-signal count, reported and not
                                  # banded: see the note in c19_reveal_craft
C19_MAX_DECLARED_DEVICES = 1     # a declaration may supply at most one of the
                                 # two devices S wants; you cannot declare your
                                 # way to S with nothing measurable on screen
C19_S_BLUR, C19_A_BLUR, C19_C_BLUR = 1.00, 0.90, 0.60
C19_MIN_FAST_FRAMES = 4          # below this the blur half has nothing to say
C19_ENTRANCE_GROUP_FRAMES = 4    # entrance tweens within this are one reveal
C19_CASCADE_MIN = 3              # siblings needed for a cascade
C19_CASCADE_GAP_FRAMES = 12      # and the largest gap between their onsets
C19_SPLIT_OPPOSED_FRAMES = 4     # two siblings entering from opposite sides
C19_GROW_TO_FILL = 0.70          # a card ending at this share of the frame,
                                 # having grown by at least half, is a reveal

# ---- C23 encode and delivery QC --------------------------------------------
C23_PIX_FMT = "yuv420p"
C23_AUDIO_RATE, C23_AUDIO_CH = 48000, 2
C23_FIRST_FRAME_INK = 0.002      # a poster frame with less ink than this
C23_END_CARD_S = 1.5             # canon 2.4, MEASURED: "Most brand end cards
                                 # are static for 1.5-3 s". The superseded
                                 # rubric's own figure was 2-3 s and it labels
                                 # it "no citable standard; inference"; canon's
                                 # is a measurement over the playlist corpus and
                                 # outranks it. A 1.9 s end card is inside the
                                 # range professionals actually cut.
C23_LOOP_CODE_VALUE = 1
C23_LOOP_VELOCITY_RATIO = 3.0    # the seam step against the median in-piece
                                 # step: a value match with a velocity mismatch
                                 # hitches every cycle
C23_SAMPLE_FRAMES = 6            # full-resolution frames pulled for the chroma
                                 # and banding passes
# Chroma bleed, measured as what the words mean: colour that sits outside the
# ink it is supposed to be inside. A stroke-width test cannot do this, because
# chroma ringing on a hard black-on-white edge is itself one pixel wide, and on
# a monochrome control that reads as "100 % of saturated ink is thin" out of
# 3642 pixels of pure artefact.
C23_CHROMA_UV = 24               # |U-128| or |V-128| for a coloured sample
C23_CHROMA_MIN_PX = 4000         # chroma samples needed before the share means
                                 # anything; below it the row reports None
C23_CHROMA_BLEED_SHARE = 0.25    # share of coloured samples landing outside the
                                 # ink they belong to, dilated by one sample
C23_BANDING_STEP = 3             # code-value jump across a smooth gradient
C23_BANDING_RUN = 6              # with flat runs at least this wide either side
C23_BANDING_EDGES = 12           # this many banded edges on a frame is banding
C23_RANGE_TV = (16, 235)         # limited-range luma
# Ringing on a hard black-on-white edge overshoots 16/235 by ten code values or
# more, so min and max over a frame cannot tell a mis-tagged range from a sharp
# picture. Real full-range content sits AT 0 and 255 with mass; ringing does
# not reach 6 or 249. Measured on _controls/bad, a correctly tagged tv render:
# stored 8 to 244, 1.2 % below 16, and nothing at all past 6 or 249.
C23_RANGE_FULL = (6, 249)        # a tv tag is wrong only past these ...
C23_RANGE_FULL_SHARE = 0.005     # ... with this much mass out there
C23_RANGE_WALL = 1               # code values either side of 16 and 235
C23_RANGE_WALL_SHARE = 0.005     # a pc tag is wrong only with a wall this big
C23_RANGE_OUTSIDE_CLEAN = 0.0005 # and nothing outside 16-235 at all
C23_TAIL_MS = 50.0               # the last of the mix ...
C23_TAIL_REF_MS = 500.0          # ... against the half second before it
C23_TAIL_RATIO = 0.60            # above this the bed stops dead
C23_TAIL_FLOOR = 0.01            # and only when it is audible at all
C23_BITRATE_TOP_DECILE = 0.10    # the fastest tenth of frames should cost more
C23_BITRATE_MIN_RATIO = 1.05     # bits than the median, or the encoder may be
                                 # rate-clipped exactly where it matters. On its
                                 # own that ratio is noise: packet sizes are
                                 # dominated by keyframe placement, so the fault
                                 # also needs the signature of an actual cap.
C23_BITRATE_CEIL_TOL = 0.02      # frames within this of the largest packet ...
C23_BITRATE_CEIL_SHARE = 0.05    # ... at this share of the film is a ceiling

# ---- C23D duration and cadence (GATE) --------------------------------------
C23D_FRAME_TOLERANCE = 0         # exactly as authored. No tolerance, and no
                                 # declaration may add one.


CRITERIA_NAMES = {
    "C4": "hold ratio", "C5": "frame integrity", "C17": "transition design",
    "C18": "audio sync", "C18D": "audio delivery",
    "C19": "reveal craft and blur", "C23": "encode QC",
    "C23D": "duration and cadence",
}

BASIS = {
    "C4": "canon C4 genre bands; LottieFiles 100-200 ms stillness; leadMs on "
          "the first beat only; settle where motion is imperceptible",
    "C5": "canon C5 rewrite: flash frames at cuts, duplicate runs against a "
          "declared per-layer cadence, full resolution on luma",
    "C17": "canon C17 and section 5; HyperFrames transitions overview 1-3; "
           "direction continuity at the cut, one primary plus two accents",
    "C18": "canon C18 and section 6; EBU R37 / ITU-R BT.1359-1; window centred "
           "one frame early, hitRate against bar lines",
    "C18D": "canon gate: EBU R128 / AES TD1008 loudness and TRUE peak against "
            "the declared delivery",
    "C19": "canon C19; quality-checklist CRITICAL opacity-only; 'motion blur "
           "on, always'; no blurred frame touching a cut",
    "C23": "canon C23 encode and delivery QC",
    "C23D": "canon gate: rendered frame count exactly as authored",
}

WEIGHTS = {"C4": 1, "C5": 1, "C17": 2, "C18": 1, "C18D": 0,
           "C19": 2, "C23": 1, "C23D": 0}
GATES = {"C18D", "C23D"}


# =============================================================================
# small helpers, restated so this module imports nothing from grade-mg.py while
# four agents are editing it
# =============================================================================

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def fscale(frames_at_30, fps):
    """Every frame threshold here is quoted at the authoring rate of 30 fps. A
    60 fps render doubles every run length, so an 8-frame gap becomes 16 and
    reads as a stall unless the constants scale with the delivered rate."""
    return max(1, int(round(frames_at_30 * fps / 30.0)))


def band_worse(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return a if BAND_ORDER.index(a) >= BAND_ORDER.index(b) else b


def rank_worst(pairs, n=6):
    """Frames worst-first. `pairs` is [(severity, frame)], higher is worse.
    Sorting the SET of frames returns the numerically earliest, which is not
    the frame the note names and not the frame the reader should open."""
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


def _blank_mask(px):
    return px.ink_frac < CUT_BLANK_INK


def _ink_frame(px, f):
    """Ink centroid (fraction of frame) and extent (fraction of frame) at f."""
    f = int(clamp(f, 0, px.n - 1))
    m = px.mask[f]
    if not m.any():
        return None
    ys, xs = np.nonzero(m)
    h, w = m.shape
    return (float(xs.mean()) / w, float(ys.mean()) / h,
            float(xs.max() - xs.min() + 1) / w,
            float(ys.max() - ys.min() + 1) / h)


def _is_replace_in_place(px, c):
    """One type block re-set at the same place across a hard cut.

    Canon 3.2 makes the binary swap the CORRECT device for two states of the
    same type and forbids the crossfade that would satisfy an overlap test;
    canon 3.1 makes the same construction a reading regime of its own. Measured
    on the delivered frames either side of the cut, so no declaration reaches
    it: the ink centroid has to land within C17_REPLACE_CENTRE_FRAC of the frame
    diagonal of where it was, and the ink extent has to be within
    C17_REPLACE_EXTENT_RATIO in both axes."""
    a = _ink_frame(px, c - 1)
    b = _ink_frame(px, c)
    if a is None or b is None:
        return False
    if math.hypot(a[0] - b[0], a[1] - b[1]) > C17_REPLACE_CENTRE_FRAC:
        return False
    lo, hi = min(a[3], b[3]), max(a[3], b[3])
    if lo <= 1e-6 or hi / lo > C17_REPLACE_BAND_RATIO:
        return False
    return True


def _blank_runs(px):
    blank = _blank_mask(px)
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


def _runs_of(flags, min_len):
    """Contiguous True runs of at least min_len, as inclusive (a, b)."""
    out, f, n = [], 0, len(flags)
    while f < n:
        if flags[f]:
            a = f
            while f < n and flags[f]:
                f += 1
            if f - a >= min_len:
                out.append((a, f - 1))
        else:
            f += 1
    return out


def _cache(ctx, key, build):
    store = getattr(ctx, "cache", None)
    if store is None:
        store = {}
        try:
            ctx.cache = store
        except Exception:
            return build()
    if key not in store:
        store[key] = build()
    return store[key]


def _row(cid, measured, band, worst=None, note="", na=False, na_reason="",
         declarations=None):
    return {
        "id": cid,
        "name": CRITERIA_NAMES[cid],
        "weight": WEIGHTS[cid],
        "gate": cid in GATES,
        "na": bool(na),
        "measured": measured,
        "band": None if na else band,
        # ranked by SEVERITY on the way in and never re-sorted here
        "worstFrames": [int(f) for f in dict.fromkeys(worst or [])][:6],
        "basis": BASIS[cid],
        "note": na_reason if na else note,
        "declarations": list(declarations or []),
    }


def _manifest(ctx):
    return getattr(ctx, "manifest", None) or {}


def _register(ctx):
    src = getattr(ctx, "src", None)
    if src is not None and getattr(src, "register", None):
        return src.register
    return _manifest(ctx).get("register", DEFAULT_REGISTER)


# =============================================================================
# shared structure helpers
# =============================================================================

def _settle_perceptual(ctx, mv):
    """The frame where the move becomes IMPERCEPTIBLE, not where the tween
    ends (canon section 6). For `expo.out` the element sits at 99 % of target
    at 0.66 of the duration; charging the remaining third as motion is what
    made a film built on hard eases report a hold ratio it does not have, and
    it is the same error that puts an audio hit 3 to 6 frames late.

    Measured on the on-screen rect (cx, cy, w, h), which carries scale, plus
    opacity at C4_OPACITY_PX_EQUIV. Never on a bounding box alone as a proxy
    for travel: this IS the box, and it is the thing whose stillness is being
    asked about."""
    src = ctx.src
    a = int(clamp(mv["onsetF"], 0, src.frames - 1))
    b = int(clamp(mv["endF"], 0, src.frames - 1))
    if b <= a:
        return b
    rows = np.asarray(src.num[mv["el"]][a:b + 1, :4], dtype=float)
    if len(rows) < 2:
        return b
    step = np.abs(np.diff(rows, axis=0)).max(axis=1)
    try:
        op = np.asarray(src.prop(mv["el"], "opacity")[a:b + 1], dtype=float)
        step = np.maximum(step, np.abs(np.diff(op)) * C4_OPACITY_PX_EQUIV)
    except Exception:
        pass
    thr = C4_IMPERCEPTIBLE_PX * (float(src.H) / C4_IMPERCEPTIBLE_REF_H)
    over = np.flatnonzero(step > thr)
    if not len(over):
        settle = a
    else:
        settle = a + int(over[-1]) + 1
    # the numeric settle is where the curve reaches its end value; nothing can
    # still be travelling after it, so it is the ceiling on this
    return int(clamp(min(settle, mv["settleF"]), a, b))


def _moving_mask(ctx):
    """Per-frame: is anything that is not ambient, mechanical or looping still
    in motion. Canon C4 excludes declared mechanical and looping elements from
    the stillness test as well as ambient: a scene carrying a progress ring
    never has a frame where nothing non-ambient moves, so holdRatio computes as
    0 for the whole piece and a correct build returns C."""
    px, src = ctx.px, ctx.src
    n = px.n
    if src is None:
        return (px.changed_frac > C4_PIXEL_MOVING_FRAC), "pixel"
    moving = np.zeros(n, dtype=bool)
    for m in src.moves:
        if m["ambient"] or m["mechanical"] or m["repeat"] or m["kind"] == "other":
            continue
        a = int(clamp(m["onsetF"], 0, n - 1))
        b = int(clamp(_settle_perceptual(ctx, m), 0, n - 1))
        if b >= a:
            moving[a:b + 1] = True
    return moving, "source"


def _gap_cadence(ctx):
    """The blank-gap lengths this piece uses as its rhythm, declared or
    repeated, and NOTHING ELSE.

    The set this replaces was `declared + repeated + range(1, 9)`, which
    contains every length a flash frame can have, so C5's flash test could
    never fire and C17 called every short dip designed. Canon's rule is that a
    dip to ground is a standard device and the amateur tell is an unmotivated
    dip of INCONSISTENT length: a length used at two cuts is the cadence, a
    length used once is the defect."""
    man = _manifest(ctx)
    declared = sorted({int(x) for x in (man.get("gapCadence") or [])})
    counts = {}
    for (a, b) in _blank_runs(ctx.px):
        if a == 0 or b == ctx.px.n - 1:
            continue                       # the lead-in and the tail are not dips
        L = b - a + 1
        counts[L] = counts.get(L, 0) + 1
    used = sorted({L for L, c in counts.items() if c >= C17_CADENCE_MIN_USES})
    return sorted(set(declared) | set(used)), counts, declared


def _full_res_deltas(ctx):
    """(meanLevels, changedFrac) per frame at the render's FULL resolution on
    luma, where meanLevels[f] and changedFrac[f] compare frame f with f-1.

    Canon C5 requires full resolution: at 640x360 a scale 1 -> 1.04 Ken Burns
    moves the frame edge 0.1 px and hides under any whole-frame average.
    Decoding 1080p luma for a 26 s film is about 1.6 GB, so the pass is
    streamed and only the two summary numbers per frame are kept."""

    def build():
        px = ctx.px
        if hasattr(px, "duplicates"):
            try:
                _, mean_d, chg = px.duplicates()
                if len(mean_d) == px.n:
                    return np.asarray(mean_d, float), np.asarray(chg, float)
            except Exception:
                pass
        path = getattr(ctx, "render", None) or getattr(px, "path", None)
        n = px.n
        mean_d = np.zeros(n, dtype=np.float64)
        chg = np.zeros(n, dtype=np.float64)
        mean_d[0], chg[0] = 255.0, 1.0
        if not path or not os.path.exists(path):
            return mean_d, chg
        W, H = int(ctx.width), int(ctx.height)
        plane = W * H
        proc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-i", path, "-vf", "format=gray",
             "-vsync", "0", "-f", "rawvideo", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        prev, i = None, 0
        try:
            while i < n:
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
        finally:
            try:
                proc.stdout.close()
                proc.wait(timeout=10)
            except Exception:
                proc.kill()
        return mean_d, chg

    return _cache(ctx, "fullResDeltas", build)


def _strobe(ctx):
    """(travel, strobe, moving, thr, fast) for the fast-frame scan C19 shares
    with C11. Prefer the integrator's scan so the two rows cannot disagree
    about which frames are fast. Tolerant of the four-element form, where
    `fast` and `strobe` are the same set."""
    pre = getattr(ctx, "strobe", None)
    if pre is None:
        fn = getattr(ctx, "strobe_scan", None)
        if callable(fn):
            pre = fn(ctx.px, ctx.src, ctx.cuts, _manifest(ctx), ctx.fps)
        else:
            pre = _cache(ctx, "strobe", lambda: _strobe_scan_local(ctx))
    pre = tuple(pre)
    if len(pre) == 4:
        return pre + (pre[1],)
    return pre[:5]


def _strobe_scan_local(ctx):
    """crit_motion's scan, reached only when this module runs standalone.

    It is IMPORTED, not restated. The restatement that used to live here
    measured tracked-component CENTROID travel, and a centroid moves whenever a
    component grows, merges or splits with nothing on screen translating: it
    reported 218 px per frame on a frame whose real edge displacement was 2.6,
    and its area gate then hid the one frame in the same film that genuinely
    jumped by 341 px. Two copies of a measurement are two measurements, and the
    one the report prints has to be the one that ran."""
    import crit_motion
    man = _manifest(ctx)
    bare = dict(man)
    bare.pop("shutterFrames", None)
    travel, strobe, moving, thr = crit_motion.strobe_scan(
        ctx.px, ctx.cuts, man, ctx.fps, DEC_W)
    fast = crit_motion.strobe_scan(ctx.px, ctx.cuts, bare, ctx.fps, DEC_W)[1]
    return travel, strobe, moving, thr, fast


def _strobe_rank(strobe):
    """Rank fast frames by contiguous-run length first and per-frame travel
    second. The head of a frame-ordered set is not the worst: it names three
    isolated hits in the opening titles and misses the five-frame run that is
    the actual defect."""
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
        worst_f = max(r, key=lambda f: strobe[f])
        out.append((len(r) * 100.0 + strobe[worst_f], worst_f))
    return out


def _heroes(ctx):
    """One hero move per beat: the move on the element with the largest settled
    INK area, or the element the manifest names."""
    pre = getattr(ctx, "heroes", None)
    if pre is not None:
        return pre
    fn = getattr(ctx, "hero_moves", None)
    if callable(fn):
        return fn(ctx.src, ctx.beats, ctx.px)
    src = ctx.src
    if src is None:
        return []

    def build():
        named = _manifest(ctx).get("hero", {}) or {}
        out = []
        for bi, (a, b) in enumerate(ctx.beats):
            cand = [m for m in src.moves
                    if a <= m["onsetF"] <= b and m["kind"] == "spatial"]
            if not cand:
                continue
            want = named.get(str(bi)) or named.get(str(bi + 1))
            if want:
                hit = [m for m in cand
                       if m["key"] == want
                       or src.elements[m["el"]].get("id") == str(want).lstrip("#")]
                if hit:
                    out.append(max(hit, key=lambda m: m["dist"]))
                    continue

            def ink_area(m):
                f = int(clamp(m["settleF"], 0, src.frames - 1))
                x0, y0, x1, y1 = src.box_at(m["el"], f)
                sx, sy = DEC_W / src.W, DEC_H / src.H
                bx0 = int(clamp(x0 * sx, 0, DEC_W - 1))
                bx1 = int(clamp(x1 * sx, 1, DEC_W))
                by0 = int(clamp(y0 * sy, 0, DEC_H - 1))
                by1 = int(clamp(y1 * sy, 1, DEC_H))
                if bx1 <= bx0 or by1 <= by0:
                    return 0.0
                pf = int(clamp(f, 0, ctx.px.n - 1))
                return float(ctx.px.mask[pf, by0:by1, bx0:bx1].sum())
            out.append(max(cand, key=ink_area))
        return out

    return _cache(ctx, "heroes", build)


def _motion_at(src, m, f):
    """The per-frame motion of a move as a three-vector (dx, dy, ds*K), where
    K puts a scale change on the same footing as a translation: an element
    scaling by ds moves its own edges about ds * diagonal / 2.

    Reading direction off the centroid alone reports a scale-through handoff,
    where the outgoing card shrinks and the incoming card settles from
    oversize, as zero motion on both sides and therefore as a direction break.
    That is the commonest card transition in the medium."""
    f = int(clamp(f, 1, src.frames - 1))
    el = m["el"]
    cx, cy = src.prop(el, "cx"), src.prop(el, "cy")
    sc = src.prop(el, "scale")
    k = C17_SCALE_TO_PX * src.diag
    return (float(cx[f] - cx[f - 1]), float(cy[f] - cy[f - 1]),
            float(sc[f] - sc[f - 1]) * k)


def _speed_at(src, m, f):
    v = _motion_at(src, m, f)
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def _dir_at(src, m, f):
    return _motion_at(src, m, f)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _peak_speed(src, m):
    a = int(clamp(m["onsetF"], 0, src.frames - 1))
    b = int(clamp(m["settleF"], 0, src.frames - 1))
    if b <= a:
        return 0.0
    return max(_speed_at(src, m, f) for f in range(a + 1, b + 1))


def _blur_on(src, el, f):
    fl = src.style_at(el, "filter", f) or "none"
    return "blur(" in fl and not fl.startswith("blur(0")


def _blur_active(src, f):
    for e in src.elements:
        if _blur_on(src, e["i"], f):
            return True
    return False


# =============================================================================
# C4  hold ratio
# =============================================================================

def c4_hold_ratio(ctx):
    """Stillness per beat and across the piece, banded by GENRE.

    WHAT IT MEASURES. The share of frames on which nothing non-ambient,
    non-mechanical and non-looping is still PERCEPTIBLY moving, per beat and
    for the whole piece; the gap in ms between one move settling and the next
    firing on the same element; and `leadMs` on the FIRST BEAT ONLY.

    Three definitions do the work, and each replaces one that was measuring the
    wrong thing:

      - the settle is the frame where motion becomes imperceptible, not where
        the tween ends, so the long tail of every `expo.out` stops counting as
        motion (canon section 6);
      - beats closer together than ten frames at 30 fps are a rapid-fire run
        and merge into one unit, because 0.30 of a two-frame beat is nothing;
      - the per-beat floor is the genre floor capped at 0.30, because a flat
        0.30 contradicts this criterion's own continuous-camera band of 0.05
        to 0.35.

    S: every unit holds at least the floor, every gap >= 100 ms, the piece
       sits inside its genre band, and the piece's own first frame is still for
       at least 100 ms. leadMs is measured from FRAME 0 of the composition,
       which is what the guardrail is about, and only its lower bound is
       charged; measured from the first detected cut it is 0 on any film whose
       opening card arrives on its own boundary. A lead fault caps the row at
       A and never bands it C.
    C: the piece is outside its genre band by more than 0.10. That is canon's
       whole C column for this row; the superseded rubric's second clause,
       "fewer than 75 % of beats", was deleted when canon moved the per-beat
       rule into the S row, and carrying it forward scored C on a card film
       whose piece hold sits four points outside a band it is otherwise well
       inside.

    STILL SCORES C ON: a card film declaring genre card-based whose background
    gradient tween runs the whole 30 s and is declared neither ambient nor
    mechanical, so no frame is ever still and the piece holds 0.00 against a
    floor of 0.45.
    """
    px, src, fps = ctx.px, ctx.src, ctx.fps
    man = _manifest(ctx)
    decl = []
    genre = man.get("genre")
    if genre in C4_GENRE_PIECE:
        decl.append("genre=%s" % genre)
    else:
        genre = DEFAULT_GENRE
    lo, hi = C4_GENRE_PIECE[genre]
    if man.get("mechanical"):
        decl.append("mechanical:%d" % len(man["mechanical"]))

    moving, basis = _moving_mask(ctx)
    raw_beats = ctx.beats or [(0, px.n - 1)]
    beats, merged = _hold_units(raw_beats, fps)
    floor = min(C4_S_BEAT_HOLD, lo)

    # canon 3.3, verbatim: "The outgoing element's rest transform becomes the
    # incoming element's from-state, so the cut lands mid-move rather than into
    # a gap -- and a card that hands off does not need to resolve, WHICH
    # RELIEVES THE HOLD MODEL." A unit whose closing edit carries motion across
    # it is exactly that card, and charging it for not being still is the same
    # fact C17 rewards, scored again in the opposite direction. The relief is on
    # CARRIES, not on DESIGNED: a hard cut declared on-beat is designed and does
    # not carry, so no declaration reaches this row.
    carrying = set()
    try:
        carrying = {r["cut"] for r in _cut_census(ctx)["records"] if r.get("carries")}
    except Exception:
        carrying = set()
    if carrying:
        decl.append("handoffRelief:%d" % len(carrying))

    ok_beats, worst, relieved = 0, [], 0
    for (a, b) in beats:
        held = int((~moving[a:b + 1]).sum())
        ratio = held / max(b - a + 1, 1)
        hands_off = any(a <= c <= b + 1 for c in carrying)
        if ratio >= floor:
            ok_beats += 1
        elif hands_off:
            ok_beats += 1
            relieved += 1
        else:
            worst.append((1.0 - ratio, a))

    # leadMs applies to the composition's FIRST FRAME, not to every cut. C17
    # defines a designed handoff as outgoing and incoming animating at the same
    # time T, which is leadMs = 0, so enforcing a lead at every cut made the two
    # criteria contradict each other. It is a separate fault from the hold
    # share, and it caps the row rather than banding it: canon's C column here
    # is the genre band and the hold share, and nothing else.
    lead_bad, lead_ms = [], None
    idx0 = np.flatnonzero(moving)
    if len(idx0):
        lead_ms = float(idx0[0]) / fps * 1000.0
        if lead_ms < C4_S_LEAD_MIN_MS:
            lead_bad.append(int(idx0[0]))

    gap_bad = []
    if src is not None:
        for m in src.moves:
            if m["ambient"] or m["mechanical"] or m["repeat"]:
                continue
            settle = _settle_perceptual(ctx, m)
            nxt = [x for x in src.moves
                   if x["el"] == m["el"] and x["onsetF"] > settle
                   and not x["ambient"] and not x["mechanical"]]
            if not nxt:
                continue
            nx = min(nxt, key=lambda x: x["onsetF"])
            gap = (nx["onsetF"] - settle) / fps * 1000.0
            if gap >= C4_S_GAP_MS or _is_continuation(src, m, nx, settle):
                continue
            gap_bad.append(settle)

    piece = float((~moving).sum()) / max(px.n, 1)
    share = ok_beats / max(len(beats), 1)
    outside = max(0.0, lo - piece, piece - hi)

    # Canon's C column for C4 is ONE term: "outside the genre band by >0.10".
    # The superseded rubric also banded C at "fewer than 75 % of beats", and
    # canon DELETED that clause: the per-beat rule lives in the S row, where it
    # reads "every beat holdRatio >= 0.30". It is not a small difference. A
    # 26-card film that holds 0.41 of its frames against a card-based floor of
    # 0.45 -- four points outside a band it is otherwise inside -- scored C on
    # the beat share while its piece hold was well within canon's own slack.
    # The share still governs S, A and B, so a piece that never holds still
    # cannot reach either.
    if outside > C4_C_PIECE_SLACK:
        band = "C"
    elif share >= 1.0 and not gap_bad and not lead_bad and lo <= piece <= hi:
        band = "S"
    elif share >= C4_A_BEATS and C4_A_PIECE[0] <= piece <= C4_A_PIECE[1]:
        band = "A"
    elif share >= C4_B_BEATS and C4_B_PIECE[0] <= piece <= C4_B_PIECE[1]:
        band = "B"
    else:
        band = "B"
    if lead_bad:
        band = band_worse(band, C4_LEAD_BLOCKS)

    note = ""
    if outside > C4_C_PIECE_SLACK and piece < lo:
        note = ("hold ratio %.2f is under the %s floor of %.2f: it never stops moving"
                % (piece, genre, lo))
    elif outside > C4_C_PIECE_SLACK:
        note = ("hold ratio %.2f is over the %s ceiling of %.2f: a slideshow"
                % (piece, genre, hi))
    elif share < C4_B_BEATS:
        note = ("%d/%d beats hold under %.0f%% of their frames; if one element is "
                "meant to move throughout, declare it `mechanical` and it leaves the "
                "stillness test" % (len(beats) - ok_beats, len(beats), floor * 100))
    elif lead_bad:
        note = ("the piece is already moving %.0f ms in: the poster frame is "
                "mid-motion" % (lead_ms or 0.0))
    elif gap_bad:
        note = ("%d move(s) re-fire under %.0f ms after settling"
                % (len(gap_bad), C4_S_GAP_MS))
    if basis == "pixel":
        note = (note + "; " if note else "") + \
            "reduced confidence: no source channel, stillness read from pixels"

    return _row("C4", {
        "holdRatio": round(piece, 3), "beatsOK": round(share, 3),
        "genre": genre, "band": [lo, hi], "beatFloor": round(floor, 2),
        "gapViolations": len(gap_bad), "beats": len(beats),
        "handoffRelieved": relieved,
        "leadMs": (None if lead_ms is None else round(lead_ms)),
        "rapidFireMerged": merged, "basis": basis,
    }, band, rank_worst(worst + [(0.5, f) for f in gap_bad]
                        + [(0.4, f) for f in lead_bad]), note,
        declarations=decl)


def _hold_units(beats, fps):
    """Beats merged into units long enough for the stillness question to mean
    something. A cut list with five cuts inside fourteen frames is a rapid-fire
    run, and asking a two-frame beat to hold 30 % of its frames charges a
    professional flurry as a fault on every card in it."""
    want = fscale(C4_MIN_BEAT_FRAMES, fps)
    out, merged = [], 0
    for (a, b) in beats:
        if out and (out[-1][1] - out[-1][0] + 1) < want:
            out[-1] = (out[-1][0], b)
            merged += 1
        else:
            out.append((a, b))
    # a trailing short unit has nothing after it to absorb it, so it merges
    # backwards instead of being graded as a two-frame beat
    while len(out) > 1 and (out[-1][1] - out[-1][0] + 1) < want:
        out[-2] = (out[-2][0], out[-1][1])
        out.pop()
        merged += 1
    return out, merged


def _is_continuation(src, prev, nxt, settle):
    """One motion authored in segments, not a re-fire. The second tween starts
    on the frame the first settled and at the value it ended on, so there is no
    stillness to violate; charging it as a re-fire was wrong on every instance
    in the positive control."""
    if nxt["onsetF"] > settle + C4_CONTINUATION_FRAMES:
        return False
    f0 = int(clamp(settle, 0, src.frames - 1))
    f1 = int(clamp(nxt["startF"], 0, src.frames - 1))
    a = np.asarray(src.num[prev["el"]][f0][:4], dtype=float)
    b = np.asarray(src.num[nxt["el"]][f1][:4], dtype=float)
    return float(np.abs(a - b).max()) <= C4_CONTINUATION_EPS


# =============================================================================
# C5  frame integrity
# =============================================================================

def _cadence_segments(ctx):
    """The declared per-layer, per-segment cadence.

    BUCK's Mailchimp shorts run "a mixture of 1 2 4 8 and even 16 frames per
    second in a single shot", and Amigo Total runs two layers at two rates in
    one shot, so a single global `posterize` number cannot express what
    professionals actually do. A segment is:

        {"from": f, "to": f, "hold": n,
         "layers": ["#character", "#bg"],     optional, reported
         "phase": f,                          optional, the first held frame
         "why": "..."}                        optional

    `hold` is how many rendered frames one authored pose occupies: 2 is on
    twos, 4 is on fours. `layers` is recorded and printed but cannot be
    verified from the composite, because a frame only repeats when EVERY
    visible layer repeats: it is there so the report names the claim.

    `posterize: n` is accepted as a whole-film segment for compatibility."""
    man = _manifest(ctx)
    n = ctx.px.n
    segs, decl = [], []
    for i, s in enumerate(man.get("cadence") or []):
        try:
            hold = int(s.get("hold"))
        except (TypeError, ValueError):
            continue
        if not (C5_CADENCE_MIN_HOLD <= hold <= C5_CADENCE_MAX_HOLD):
            continue
        a = int(clamp(s.get("from", 0), 0, n - 1))
        b = int(clamp(s.get("to", n - 1), 0, n - 1))
        if b < a:
            continue
        segs.append({"from": a, "to": b, "hold": hold,
                     "phase": s.get("phase"),
                     "layers": list(s.get("layers") or []),
                     "why": s.get("why", "")})
        decl.append("cadence[%d]=hold %d f%d-f%d" % (i, hold, a, b))
    post = int(man.get("posterize", 0) or 0)
    if C5_CADENCE_MIN_HOLD <= post <= C5_CADENCE_MAX_HOLD:
        segs.append({"from": 0, "to": n - 1, "hold": post, "phase": None,
                     "layers": [], "why": "posterize"})
        decl.append("posterize=%d" % post)
    return segs, decl


def c5_frame_integrity(ctx):
    """Flash frames at cuts, and duplicate runs against a declared cadence, at
    FULL resolution on luma. No longer a gate.

    Measures: (a) 1-2 frame blanks and wrong frames at a cut whose length is
    not one the piece repeats or declares; (b) runs of identical delivered
    frames, each honoured or charged against the declared per-layer,
    per-segment cadence, declared holds and declared freezes; (c) declared
    holds of 1.5 s or more with no ambient element, and declared holds sitting
    on top of an active tween; and, REPORT ONLY, (d) runs where the
    composition's own track moved visibly and the delivered luma did not.

    A duplicate flag at frame f means f is identical to f-1, so a run of k
    flags is k+1 identical frames, and the film's own `cadence` declaration
    says how many of those are legal where. A cadence declared but not
    delivered is charged as a false declaration, so declaring a hold of 8 over
    a film that moves every frame buys nothing.

    S: no undeclared flash frame, and every declared cadence honoured with no
       undeclared stall, dead hold or false declaration.
    C: a 1-2 frame blank at a cut outside the declared cadence; or more than
       three undeclared stalls; or a declared hold or cadence the render does
       not deliver.

    STILL SCORES C ON: a film whose gaps are all 6 frames long except for one
    cut that carries a single blank frame. That length is used once, is not in
    `gapCadence` and sits on a cut, so it is a flash frame and the row is C.
    Also on the amateur control's three-frame freeze at f88, which the detector
    this replaces scored S on.
    """
    px, src, fps = ctx.px, ctx.src, ctx.fps
    man = _manifest(ctx)
    decl = []
    mean_d, chg = _full_res_deltas(ctx)
    dup = (mean_d < C5_DUP_MEAN_LEVELS) & (chg < C5_DUP_CHANGED_FRAC)
    if len(dup):
        dup[0] = False
    blank = _blank_mask(px)
    cadence, _gap_counts, gap_declared = _gap_cadence(ctx)
    if gap_declared:
        decl.append("gapCadence:%s" % gap_declared)
    segs, seg_decl = _cadence_segments(ctx)
    decl += seg_decl
    still = None
    if src is not None:
        try:
            still = src.still_delta()
        except Exception:
            still = None

    # ---- declared holds, capped ------------------------------------------
    holds = [h for h in (man.get("holds") or []) if h.get("why")]
    freezes = list(man.get("freezes") or [])
    if holds:
        decl.append("holds:%d" % len(holds))
    if freezes:
        decl.append("freezes:%d" % len(freezes))
    holds = sorted(holds, key=lambda h: h["to"] - h["from"])
    kept, covered, dropped = [], 0, 0
    genre = man.get("genre") or getattr(ctx, "genre", None)
    cap = max(C5_HOLD_EXEMPT_MAX,
              C4_GENRE_PIECE.get(genre, (0.0, 0.0))[1]) * px.n
    for h in holds:
        span = h["to"] - h["from"] + 1
        if covered + span > cap:
            dropped += 1
            continue
        covered += span
        kept.append(h)
    holds = kept
    exempt_spans = [(h["from"], h["to"], False) for h in holds] + \
                   [(f.get("from", 0), f.get("to", 0), True) for f in freezes]

    def in_hold(a, b):
        """The declared span this run belongs to, or None. Overlap, not the
        run's first frame: a hold declared at f34 and a duplicate run beginning
        at f32, because the last two frames of the settle were already
        sub-threshold, are the same hold."""
        for (lo, hi, _fz) in exempt_spans:
            x0, x1 = max(a, lo), min(b, hi)
            if x1 >= x0 and (x1 - x0 + 1) >= 0.5 * (b - a + 1):
                return (lo, hi)
        return None

    # ---- duplicate runs ---------------------------------------------------
    # A duplicate FLAG at f means f is identical to f-1, so a run of k flags is
    # k+1 identical frames. Getting that off by one is what makes a three-frame
    # freeze invisible.
    min_flags = fscale(C5_DUP_RUN_MIN_FLAGS, fps)
    flag_runs = _runs_of(dup, min_flags)
    runs = [(a - 1, b) for (a, b) in flag_runs]      # inclusive identical span

    def on_cadence(a, b):
        held = b - a + 1
        for s in segs:
            if a < s["from"] - C5_CADENCE_EDGE_TOL or b > s["to"] + C5_CADENCE_EDGE_TOL:
                continue
            if held > s["hold"]:
                return False, s
            ph = s.get("phase")
            if ph is not None and ((a - int(ph)) % s["hold"]) != 0:
                return False, s
            return True, s
        return False, None

    undeclared, quantised, over_run, false_holds, held = [], [], [], [], []
    imperceptible = []
    for (a, b) in runs:
        if blank[a:b + 1].all():
            continue                       # a blank dip is C17's business
        ok, seg = on_cadence(a, b)
        if ok:
            continue
        if seg is not None:
            over_run.append(a)             # inside a cadence segment, too long
            continue
        span = in_hold(a, b)
        if span is not None:
            # a declared hold the render stalled on while the composition says
            # a non-ambient tween was running is a FALSE declaration: the piece
            # intended motion there and the render did not deliver it, which is
            # the defect, not the exemption.
            #
            # The question is asked over the frames the DECLARATION claims are
            # still, which is the run clipped to the declared span. Asking it
            # over the whole run charged a correct hold whose duplicate run
            # bled a frame or two past the declaration into the settle of the
            # next move, where the last sub-threshold frames of a curve are
            # always duplicates.
            qa, qb = max(a, span[0]), min(b, span[1])
            if src is not None and qb >= qa and _hold_overlaps_motion(ctx, qa, qb):
                false_holds.append(qa)
            continue
        if still is not None:
            # still[f] is the step from f-1 into f, so the movement INSIDE an
            # identical span (a..b) is still[a+1 .. b]. Reading still[a] charges
            # the step that ENDED the previous motion and turns every real
            # stall into "the codec ate it".
            lo = int(clamp(a + 1, 0, len(still)))
            hi = int(clamp(b + 1, 0, len(still)))
            moved = float(still[lo:hi].max()) if hi > lo else 0.0
            if moved >= C5_QUANTISED_VISIBLE_PX * (ctx.height / C5_QUANTISED_REF_H):
                # canon: grade the DELIVERED file. Visible motion the encode did
                # not carry is a finding about the deliverable, not an exemption
                # for it, but it is reported and never banded.
                quantised.append((a, b))
                continue
        if src is not None and _any_tween_in_flight(ctx, a + 1, b):
            # A tween is live across the INTERIOR of the run and the motion it
            # asked for is under the visibility floor tested just above. That
            # is not a frame-integrity defect: it is an ambient amplitude below
            # what H.264 will carry, which is canon's own scope note ("breathe
            # at scale 1.012 can be quantised out entirely at social
            # bitrates"). Reported, never banded, and kept apart from the
            # visible-motion-not-carried bucket above, which is the real one.
            imperceptible.append((a, b))
            continue
        if src is not None and not _is_dead_freeze(ctx, a, b):
            # Canon section 8 item 8 states the tell as "duplicate frames in a
            # segment that SHOULD MOVE". A run of identical delivered frames
            # across which no non-ambient, non-mechanical, non-looping tween is
            # in flight is not a stutter, it is a HOLD, and a hold is C4's
            # question -- where a card-based film is asked to hold 45 to 85 %
            # of its frames. Charging both made the two criteria pull against
            # each other and asked a 26-card film for one hold declaration per
            # card to say what its own timeline already says. The test stays
            # live for what it is for: a run inside a move is either a dropped
            # frame or animation on twos, and the second wants a `cadence`.
            held.append((a, b))
            continue
        undeclared.append((a, b))

    # ---- false declarations ----------------------------------------------
    # A declared cadence the render does not deliver is relief the piece did
    # not earn: declaring hold 8 over a film that moves every frame would
    # otherwise buy immunity from every duplicate test in the criterion.
    false_cadence = []
    for i, s in enumerate(segs):
        a, b = s["from"], min(s["to"], px.n - 1)
        if b <= a:
            continue
        want = (s["hold"] - 1) / float(s["hold"])
        got = float(dup[a:b + 1].mean())
        if got < C5_CADENCE_HONOURED * want:
            false_cadence.append((i, a, round(got, 3), round(want, 3)))

    dead_holds = []
    for h in holds:
        if h.get("ambient"):
            if src is not None and not _ambient_moves(ctx, h):
                dead_holds.append(h["from"])
            continue
        if (h["to"] - h["from"] + 1) / fps >= C5_DEAD_HOLD_S:
            dead_holds.append(h["from"])

    # ---- flash frames at cuts --------------------------------------------
    flash = _flash_frames(ctx, cadence)

    longest = max((b - a + 1 for (a, b) in undeclared), default=0)
    a_held = fscale(C5_A_RUN_HELD, fps)
    c_held = fscale(C5_C_RUN_HELD, fps)
    long_stall = longest > c_held

    if flash or len(undeclared) > C5_B_RUNS or false_cadence or false_holds \
            or long_stall or len(dead_holds) > C5_B_HOLDS:
        band = "C"
    elif over_run or len(undeclared) > 1 or longest > a_held \
            or len(dead_holds) > C5_A_HOLDS:
        band = "B"
    elif undeclared or dead_holds:
        band = "A"
    else:
        band = "S"

    worst = [(1000.0, f) for f in flash]
    worst += [(800.0, a) for (_i, a, _g, _w) in false_cadence]
    worst += [(700.0, f) for f in false_holds]
    worst += [((b - a + 1) + 10.0, a) for (a, b) in undeclared]
    worst += [(5.0, a) for (a, b) in quantised]

    note = ""
    if flash:
        note = ("%d flash frame(s) at a cut, off the piece's gap cadence %s"
                % (len(flash), cadence or "(none: no gap length is repeated)"))
    elif false_cadence:
        i, a, got, want = false_cadence[0]
        note = ("declared cadence[%d] holds %.0f%% of its frames, not the %.0f%% a "
                "hold of %d would produce: the declaration is not what rendered"
                % (i, got * 100, want * 100, segs[i]["hold"]))
    elif false_holds:
        note = "%d declared hold(s) sit on top of an active tween" % len(false_holds)
    elif len(dead_holds) > C5_B_HOLDS:
        note = ("%d declared hold(s) of %.1fs or more with no ambient element"
                % (len(dead_holds), C5_DEAD_HOLD_S))
    elif over_run:
        note = ("%d run(s) inside a declared cadence segment hold longer than the "
                "declared cadence" % len(over_run))
    elif undeclared:
        a, b = max(undeclared, key=lambda r: r[1] - r[0])
        note = ("longest undeclared stall f%d-f%d (%d identical frames%s)"
                % (a, b, b - a + 1,
                   (", over the %d-frame ceiling: declare it as a hold with a "
                    "reason, or give it something to move" % c_held)
                   if long_stall else ""))
    elif dead_holds:
        note = "%d declared hold(s) with no ambient element" % len(dead_holds)
    elif quantised:
        a, b = max(quantised, key=lambda r: r[1] - r[0])
        note = ("report only: %d run(s) where the composition's own track moved and "
                "the delivered luma did not, longest f%d-f%d; check whether a "
                "low-amplitude move survived the encode, because a breathe at scale "
                "1.012 can be quantised out entirely at social bitrates"
                % (len(quantised), a, b))
    if dropped:
        note = (note + "; " if note else "") + \
            ("%d declared hold(s) past the %.0f%% runtime cap were not honoured"
             % (dropped, C5_HOLD_EXEMPT_MAX * 100))

    return _row("C5", {
        "flashFrames": len(flash), "undeclaredRuns": len(undeclared),
        "longestRun": longest, "cadenceSegments": len(segs),
        "cadenceOverruns": len(over_run), "falseCadence": len(false_cadence),
        "deadHolds": len(dead_holds), "falseHolds": len(false_holds),
        "quantisedOut": len(quantised), "holdRuns": len(held),
        "underEncodeFloor": len(imperceptible),
        "gapCadence": cadence,
        "basis": "full-res luma" + ("+source" if src is not None else ""),
    }, band, rank_worst(worst), note, declarations=decl)


def _flash_frames(ctx, cadence):
    """1-2 frame blanks and 1-2 frame wrong-ground frames at a cut whose length
    the piece neither repeats nor declares. Canon C5 (a)."""
    px, fps = ctx.px, ctx.fps
    tol = fscale(C5_FLASH_CUT_TOL, fps)
    maxlen = fscale(C5_FLASH_MAX_FRAMES, fps)
    cuts = list(ctx.cuts)
    out = []
    for (a, b) in _blank_runs(px):
        if a == 0 or b == px.n - 1:
            continue
        L = b - a + 1
        if L > maxlen or any(abs(L - c) <= C17_GAP_CADENCE_TOL for c in cadence):
            continue
        if any(abs(a - c) <= tol or abs(b - c) <= tol for c in cuts):
            out.append(a)
    # the wrong frame: a 1-2 frame span whose ground flips away from BOTH
    # neighbours while the neighbours agree with each other
    ground = np.asarray(px.ground, dtype=float)
    f = 1
    while f < px.n - 1:
        L = 0
        while (f + L) < px.n - 1 and abs(ground[f + L] - ground[f - 1]) > CUT_GROUND_FLIP:
            L += 1
            if L > maxlen:
                break
        if 0 < L <= maxlen:
            after = f + L
            if abs(ground[after] - ground[f - 1]) <= CUT_GROUND_FLIP:
                if any(abs(f - c) <= tol for c in cuts) and f not in out:
                    out.append(f)
            f = after
        else:
            f += 1
    return sorted(set(out))


def _any_tween_in_flight(ctx, a, b):
    """Is ANY tween at all live across this span, ambient and mechanical
    included. The question here is not whose motion it is but whether the
    composition intended the picture to change, and a slow idle push whose
    per-frame edge travel is a tenth of a pixel is exactly the amplitude canon
    warns "can be quantised out entirely by H.264"."""
    src = ctx.src
    for m in src.moves:
        if m["kind"] == "other":
            continue
        if m["onsetF"] <= b and a <= int(m["endF"]):
            return True
    return False


def _is_dead_freeze(ctx, a, b):
    """A run of identical frames with nothing tweening across it is the HOLD of
    move / hold / cut when it runs into the next cut or into the end of the
    film. It is a DEAD FREEZE -- the defect this half of C5 exists to catch --
    when the piece picks the picture back up inside the same beat and the run
    is longer than a single run is allowed to be. The amateur control carries
    exactly that: thirteen identical frames at f88 in a film that is otherwise
    moving on 235 of its 240 frames, followed by more motion at f101 and a cut
    only at f120."""
    tol = fscale(C5_HOLD_AT_CUT_TOL, ctx.fps)
    ends = [c - 1 for c in ctx.cuts if c > a] + [ctx.px.n - 1]
    length = b - a + 1
    if any(abs(b - e) <= tol for e in ends):
        # The relief for a run that ends at a cut is BOUNDED like every other
        # run. It was unbounded, which made a still slideshow with hard cuts
        # score S with no declaration at all, and the brief's rule is that an
        # exemption is declared by name and the default is the strict case. A
        # hold longer than C5_HOLD_AT_CUT_MAX is a held card and canon 2.4 asks
        # for it to be declared -- "judge runs against a declared cadence", and
        # `holds` is what says which end card is locked off on purpose.
        return length > fscale(C5_HOLD_AT_CUT_MAX, ctx.fps)
    return length > fscale(C5_C_RUN_HELD, ctx.fps)


def _hold_overlaps_motion(ctx, a, b):
    """Is a non-ambient, non-mechanical, non-looping tween in flight across
    this span. The exclusion set is the one _moving_mask uses, because a hold
    declared over a progress ring is not a false hold: the ring is declared
    mechanical and is out of the stillness question everywhere else."""
    src = ctx.src
    for m in src.moves:
        if m["ambient"] or m["mechanical"] or m["repeat"] or m["kind"] == "other":
            continue
        if m["onsetF"] <= b and a <= _settle_perceptual(ctx, m) - 1:
            return True
    return False


def _ambient_moves(ctx, hold):
    src = ctx.src
    names = {hold.get("ambient")}
    for e in src.elements:
        if not src.is_named(e["i"], names):
            continue
        a = int(clamp(hold["from"], 0, src.frames - 1))
        b = int(clamp(hold["to"] + 1, 1, src.frames))
        seg = src.num[e["i"]][a:b, :4]
        if len(seg) > 1 and float(np.abs(np.diff(seg, axis=0)).max()) > 0:
            return True
    return False


# =============================================================================
# C17  transition design
# =============================================================================

def _declared_handoffs(ctx):
    """`handoffs`: the author naming what a cut is doing.

        {"cut": 130, "kind": "blank gap", "why": "the act break"}

    A declared handoff counts as DESIGNED, which is what canon requires for a
    deliberate dip-to-ground structure. It does not buy an S: the declared
    kind enters the type census, so declaring seven different devices still
    fails `primaryShare` and `nTypes`, and an undesigned hard swap that
    declares nothing still fails."""
    out = {}
    for h in (_manifest(ctx).get("handoffs") or []):
        try:
            c = int(h.get("cut"))
        except (TypeError, ValueError):
            continue
        kind = str(h.get("kind") or "declared")
        out[c] = kind
    return out


def _dominant_motion(src, moves, f):
    """The move carrying the most motion on frame f, translation and scale
    together."""
    best, best_v = None, 0.0
    for m in moves:
        v = _speed_at(src, m, f)
        if v > best_v:
            best, best_v = m, v
    return best


def _dominant(src, moves):
    """The move that IS the transition: the one carrying the most change, with
    translation and scale put on comparable ground. Unioning the props of every
    element near the cut let one incidental scale tween on a label decide the
    type for the whole handoff, which split a card film into six transition
    types and reported it as having no primary."""
    if not moves:
        return None
    return max(moves, key=lambda m: max(m["dist"] / max(src.diag, 1.0),
                                        m["scaleDelta"]))


def _transition_kind(src, outs, ins):
    """One of C17_KINDS, from the dominant outgoing and incoming move only."""
    pair = [m for m in (_dominant(src, outs), _dominant(src, ins)) if m is not None]
    if not pair:
        return "pop"
    props = set()
    for m in pair:
        props.update(m["props"])
    if "clipPath" in props:
        return "iris"
    for m in pair:
        if _blur_on(src, m["el"], m["onsetF"]):
            return "blur-through"
    if props & {"scale", "scaleX", "scaleY"}:
        return "zoom"
    if props & TRANSLATE_PROPS:
        return "push"
    if props & {"opacity", "autoAlpha"}:
        return "crossfade"
    return "other"


CUT_CENSUS_DOC = None


def _cut_census(ctx):
    """Classify every cut once: designed or not, which device, and why.

    C17 bands the census and C4 reads it, because canon 3.3 makes the two
    criteria one question: "the outgoing element's rest transform becomes the
    incoming element's from-state, so the cut lands mid-move rather than into a
    gap -- AND A CARD THAT HANDS OFF DOES NOT NEED TO RESOLVE, WHICH RELIEVES
    THE HOLD MODEL." A film built on continuity moves is rewarded by C17 and was
    charged by C4 for never being still, which is the same fact scored twice in
    opposite directions. The census is computed once and cached."""
    cache = getattr(ctx, "cache", None)
    if isinstance(cache, dict) and "cutCensus" in cache:
        return cache["cutCensus"]
    px, src, fps = ctx.px, ctx.src, ctx.fps
    audio = getattr(ctx, "audio", None)
    man = _manifest(ctx)
    decl = []
    out = {"records": [], "declarations": decl, "vmatches": [], "durations": [],
           "dirBad": 0, "slowAtCut": 0, "badGaps": 0, "replaces": 0}
    replaces = []

    real_cuts = [c for c in ctx.cuts if c > 0]

    cadence, _counts, gap_declared = _gap_cadence(ctx)
    if gap_declared:
        decl.append("gapCadence:%s" % gap_declared)
    declared_h = _declared_handoffs(ctx)
    if declared_h:
        decl.append("handoffs:%d" % len(declared_h))
    on_beat = {int(c) for c in (man.get("onBeatHardCuts") or [])}
    if on_beat:
        decl.append("onBeatHardCuts:%d" % len(on_beat))

    blank = _blank_mask(px)
    win = fscale(C17_WINDOW_FRAMES, fps)
    gap_max = fscale(C17_BLANK_GAP_FRAMES, fps)
    same_tol = fscale(C17_SAME_START_FRAMES, fps)

    for c in real_cuts:
        # the dip that contains or abuts this cut, and where it ends
        gap, f = 0, c - 1
        while f >= 0 and blank[f]:
            gap += 1
            f -= 1
        pre_content = f >= 0
        gap_end, f = c - 1, c
        while f < px.n and blank[f]:
            gap += 1
            gap_end = f
            f += 1
        post_content = f < px.n
        bounded = pre_content and post_content
        on_cad = gap == 0 or any(abs(gap - L) <= C17_GAP_CADENCE_TOL for L in cadence)
        is_declared = c in declared_h
        bad_gap = bounded and gap > gap_max and not on_cad and not is_declared
        if bad_gap:
            out["badGaps"] += 1

        # the incoming entrance is searched from the END of the dip, not from
        # the cut frame: a card that enters two frames after a twelve-frame dip
        # is a designed handoff, and measuring from the cut called it late
        a0 = max(0, c - win)
        a1 = min(px.n - 1, max(c, gap_end) + win)

        ok, kind, carries = False, "hard cut", False
        if src is not None:
            outs = [m for m in src.moves if m["role"] == "exit"
                    and m["onsetF"] <= c <= m["endF"] + win]
            ins = [m for m in src.moves if m["role"] == "entrance"
                   and a0 <= m["onsetF"] <= a1]
            overlap = any(o["startF"] <= i["endF"] and i["startF"] <= o["endF"]
                          for o in outs for i in ins)
            same_start = any(abs(o["startF"] - i["startF"]) <= same_tol
                             for o in outs for i in ins)
            into_entrance = bool(ins) and (not bounded or on_cad or is_declared
                                           or gap <= gap_max)
            # carrying motion through the cut, which the playlist names as one
            # of the four recurring mechanisms and which no role label sees: the
            # outgoing card is still moving on its last frame, the incoming one
            # is moving on its first, and the two agree about direction. Roles
            # cannot express it because neither side changes opacity or scale
            # from zero, so both read as repositions.
            pre = [m for m in src.moves
                   if m["onsetF"] <= c - 1 <= m["settleF"] and m["kind"] != "other"]
            post = [m for m in src.moves
                    if m["onsetF"] <= c + 1 <= m["settleF"] and m["kind"] != "other"]
            po = _dominant_motion(src, pre, c - 1)
            pin = _dominant_motion(src, post, c + 1)
            carried = False
            if po is not None and pin is not None:
                pe, pi = _peak_speed(src, po), _peak_speed(src, pin)
                se, si = _speed_at(src, po, c - 1), _speed_at(src, pin, c + 1)
                if pe > C17_VELOCITY_FLOOR and pi > C17_VELOCITY_FLOOR:
                    out["vmatches"].append(abs(pe - pi) / max(pe, pi))
                    cont = _dot(_dir_at(src, po, c - 1), _dir_at(src, pin, c + 1)) > 0
                    fast_enough = (se >= C17_S_MIN_SPEED_SHARE * pe
                                   and si >= C17_S_MIN_SPEED_SHARE * pi)
                    if not cont:
                        out["dirBad"] += 1
                    if not fast_enough:
                        out["slowAtCut"] += 1
                    carried = bool(cont and fast_enough)
            ok = bool(overlap or same_start or into_entrance or carried)
            # CARRIES is narrower than DESIGNED and is what canon 3.3's hold
            # relief turns on: something is actually in motion across the edit.
            # A hard cut rescued by a declared on-beat landing is designed and
            # does NOT carry -- its card still had to resolve before the cut --
            # so a declaration can never buy the C4 relief.
            carries = bool(overlap or same_start or carried)
            if ins:
                span = (max(i["settleF"] for i in ins)
                        - min([o["onsetF"] for o in outs] + [i["onsetF"] for i in ins]))
                out["durations"].append(max(span, 1) / fps)
            if ins or outs:
                kind = _transition_kind(src, outs, ins)
            elif carried:
                kind = "carried motion"
            else:
                kind = "pop"
        else:
            pre = px.frame_delta[max(1, c - 3):c]
            post = px.frame_delta[c:min(px.n, c + 3)]
            ok = bool(len(pre) and len(post) and pre.mean() > 0.5 and post.mean() > 0.5)
            kind = "crossfade" if ok else "hard cut"

        # one device, not two: a dip to ground is the same transition at six
        # frames and at seventeen, and splitting it by length reported a card
        # film as having no primary transition
        if gap > 0 and (on_cad or is_declared) and kind != "pop":
            kind = "dip to ground"
        # the two vetoes apply to what the piece itself does, so they are
        # settled BEFORE the declared escapes, not after: applying them last
        # silently cancelled every rescue a declaration had just granted
        if bad_gap or kind == "pop":
            ok = False
        # A hard cut is ONE DEVICE. The census asks which transition the piece
        # uses, and "pop" and "hard cut" are the same edit -- a straight change
        # of picture with nothing carrying across it. What separates them here
        # is only whether a declaration or an onset rescued it, which is
        # designedShare's question and is already counted there. Splitting them
        # charged the same fact twice and reported a card film as using five
        # devices when it uses four. Same argument the dip already carries one
        # block above: one device, not two.
        if kind == "pop":
            kind = "hard cut"
        # canon 3.2's binary arrival: one type block re-set at the same place
        # with no gap. It is the correct device, not a missing one -- the
        # overlap this row otherwise looks for is the crossfade canon forbids
        # outright on two states of the same type. Read off the delivered
        # frames, gated on canon 3.3's "add at least ONE continuity move" so a
        # true slideshow gets none of it.
        if gap == 0 and not ok and _is_replace_in_place(px, c):
            replaces.append(c)
        if is_declared:
            kind = declared_h[c]
            ok = True
        # a declared on-beat hard cut is designed when it lands on an audio
        # ONSET inside the sync window, which is what the rubric says and what
        # "on the beat" means. Against the strongest quartile only, and against
        # one literal frame at 60 fps, the declaration could not be honoured by
        # a correctly cut film. A dip of an unmotivated length is not rescued
        # by it: an on-beat hard cut and a dip are different claims.
        if not ok and not bad_gap and c in on_beat \
                and audio is not None and audio.present:
            near_ms = min((abs(t - c / fps) * 1000.0 for t in audio.onsets),
                          default=1e9)
            if near_ms <= max(C18_LOCK_MS, 1000.0 / fps):
                ok = True

        out["records"].append({"cut": c, "ok": bool(ok), "kind": kind,
                               "badGap": bool(bad_gap), "gap": gap,
                               "carries": bool(carries)})

    # canon 3.3: "A piece assembled entirely from independent enter-hold-exit
    # cards is a slideshow with better easing. Add at least ONE continuity
    # move." A film that never carries motion across any edit is that
    # slideshow, and it gets no replace-in-place relief at all.
    if len([r for r in out["records"] if r["carries"]]) >= C17_REPLACE_MIN_CARRY:
        for r in out["records"]:
            if r["cut"] in replaces and not r["ok"]:
                # DESIGNED, and still a hard cut: the binary swap is the device,
                # and splitting it out as a sixth transition type would charge
                # the census for recognising it. Same argument as pop.
                r["ok"] = True
                r["replace"] = True
                out["replaces"] += 1
    if isinstance(cache, dict):
        cache["cutCensus"] = out
    return out


def c17_transition_design(ctx):
    """Designed versus undesigned handoff, direction continuity at the cut, and
    the type census. Weight 2.

    WHAT IT MEASURES, per cut. Whether an outgoing and an incoming move overlap
    or share a start frame; whether an incoming entrance follows a dip whose
    length the piece repeats or declares; whether motion CARRIES THROUGH the
    cut, meaning the dominant move on each side is above 30 % of its own peak
    on the adjacent frame and the two agree about direction; and which
    transition kind it is. Motion is a three-vector of translation and scale,
    so a scale-through handoff, where the outgoing card shrinks and the
    incoming one settles from oversize, is not read as zero motion on both
    sides.

    Two things a declaration can say here, both of which enter the census and
    neither of which buys an S: `handoffs` names what a cut is doing, and
    `gapCadence` names the dip lengths the piece uses on purpose. A declared
    blank-gap or dip-to-ground handoff counts as designed; an undesigned hard
    swap that declares nothing still fails.

    S: 100 % designed, direction continuous, neither side under 30 % of peak,
       primaryShare >= 0.60, nTypes <= 3.
    C: under 75 % designed, or a different type at every cut with four or more
       cuts.

    STILL SCORES C ON: the amateur control, whose one cut has no exit on the
    outgoing clip, whose incoming lines are already at full opacity and merely
    reposition, and whose outgoing tween has finished before the cut frame, so
    nothing overlaps, nothing enters and nothing carries: designedShare 0.00.
    """
    src = ctx.src

    real_cuts = [c for c in ctx.cuts if c > 0]
    if not real_cuts:
        return _row("C17", {"cuts": 0}, None, na=True,
                    na_reason="only one beat, nothing to hand off")
    cen = _cut_census(ctx)
    decl = cen["declarations"]
    vmatches, durations = cen["vmatches"], cen["durations"]
    dir_bad, slow_at_cut, bad_gaps = cen["dirBad"], cen["slowAtCut"], cen["badGaps"]
    types = [r["kind"] for r in cen["records"]]
    designed = sum(1 for r in cen["records"] if r["ok"])
    undesigned = len(cen["records"]) - designed
    worst = [((2.0 if r["badGap"] else 1.0), r["cut"])
             for r in cen["records"] if not r["ok"]]

    n = len(real_cuts)
    share = designed / n
    counts = {}
    for t in types:
        counts[t] = counts.get(t, 0) + 1
    primary = max(counts.values()) / n
    n_types = len(counts)
    vmax = max(vmatches) if vmatches else 0.0
    crossfade = counts.get("crossfade", 0) / n

    if share < C17_B_DESIGNED or (n_types == n and n >= C17_C_MIN_CUTS_FOR_TYPES):
        band = "C"
    elif (share >= C17_S_DESIGNED and dir_bad == 0 and slow_at_cut == 0
            and primary >= C17_S_PRIMARY_SHARE and n_types <= C17_S_NTYPES):
        band = "S"
    elif share >= C17_A_DESIGNED and n_types <= C17_A_NTYPES:
        # canon 1.6: velocity match at a cut IS direction continuity, not a
        # percentage. vmatchMax stays in the measured dict and out of the band.
        band = "A"
    else:
        band = "B"
    if band == "S" and n < C17_MIN_CUTS_FOR_S:
        # every clause of the S row is true by construction on one cut
        band = "A"

    note = ""
    if undesigned:
        note = "%d/%d cuts have no designed handoff" % (undesigned, n)
        if bad_gaps:
            note += ("; %d of them dip to ground for a length used nowhere else"
                     % bad_gaps)
    elif n_types == n and n >= C17_C_MIN_CUTS_FOR_TYPES:
        note = "a different transition type at every cut"
    elif primary < C17_S_PRIMARY_SHARE:
        note = ("no primary transition: the commonest is %.0f%% of cuts, under the "
                "60%% one-primary-plus-accents rule" % (primary * 100))
    elif dir_bad:
        note = "%d handoff(s) reverse direction across the cut" % dir_bad
    elif slow_at_cut:
        note = ("%d handoff(s) drop under 30%% of peak speed on the cut frame"
                % slow_at_cut)
    elif vmax > C17_A_VMATCH:
        note = "velocity mismatch %.0f%% on the worst handoff" % (vmax * 100)
    if primary < C17_S_PRIMARY_SHARE and "primary" not in note:
        note = (note + "; " if note else "") + \
            ("no primary transition: the commonest is %.0f%% of %d cuts across %d "
             "types, under the one-primary-plus-accents rule"
             % (primary * 100, n, n_types))
    if crossfade > C17_CROSSFADE_NOTE:
        note = (note + "; " if note else "") + \
            ("report only: %.0f%% of cuts are dissolves, and across 200 finished "
             "pieces transitions are graphic, never dissolves" % (crossfade * 100))
    if n < C17_MIN_CUTS_FOR_S:
        note = (note + "; " if note else "") + (
            "%d cut(s): designedShare, primaryShare and the type census are all "
            "true by construction below %d, so the row reports what it saw and "
            "caps at A" % (n, C17_MIN_CUTS_FOR_S))
    if src is None:
        note = (note + "; " if note else "") + \
            "reduced confidence: no source channel, handoffs read from pixels"

    return _row("C17", {
        "designedShare": round(share, 3), "nTypes": n_types,
        "primaryShare": round(primary, 3), "vmatchMax": round(vmax, 3),
        "dirBreaks": dir_bad, "slowAtCut": slow_at_cut, "badGaps": bad_gaps,
        "crossfadeShare": round(crossfade, 3), "cuts": n,
        "replaceInPlace": cen["replaces"],
        "meanDurationS": round(float(np.mean(durations)), 3) if durations else None,
    }, band, rank_worst(worst), note, declarations=decl)


# =============================================================================
# C18  audio sync   /   C18D  audio delivery (GATE)
# =============================================================================

def c18_audio_sync(ctx):
    """Onset lock, with the window centred ONE FRAME EARLY, and hitRate against
    bar lines where a tempo exists.

    Sign convention, stated once because the code this replaces had it
    inverted: delta = t_visual - t_audio, so delta is POSITIVE when SOUND
    LEADS, which is what EBU R37 and ITU-R BT.1359-1 both mean by early. The
    editor's one-frame trick puts the cut one frame AHEAD of the musical hit,
    which is delta = -1 frame, so the locked window is centred at MINUS one
    frame and a correctly cut piece does not read as consistently late.

    S: lockRate >= 0.80, meanAbs <= 20 ms, the delivery gate passes.
    C: lockRate < 0.40, or bias above +40 ms (sound early) or below -100 ms
       (sound late).

    STILL SCORES C ON: a 20-cut film cut to a bed by eye, where 6 cuts land within
    a frame of an onset. lockRate 0.30 and the row is C.
    """
    man = _manifest(ctx)
    audio = getattr(ctx, "audio", None)
    silent = bool(man.get("silent"))
    decl = ["silent"] if silent else []

    if audio is None or not audio.present:
        if silent:
            return _row("C18", {"silent": True}, None, na=True,
                        na_reason="manifest declares silent: true",
                        declarations=decl)
        has_stream = bool(audio is not None and audio.stream)
        what = "the audio stream is silent" if has_stream else \
               "the render carries no audio stream"
        return _row("C18", {"audio": "silent stream" if has_stream else "no stream"},
                    "C", [],
                    what + " and the manifest does not declare silent: true. This is "
                    "a missing declaration, not a measurement of a mix")

    px, src, fps = ctx.px, ctx.src, ctx.fps
    window_ms = max(C18_LOCK_MS, 1000.0 / fps)
    centre_ms = C18_WINDOW_CENTRE_FRAMES * 1000.0 / fps

    events = [c / fps for c in ctx.cuts if c > 0]
    if src is not None:
        events += [h["onsetF"] / fps for h in _heroes(ctx)]
        impacts = [m["onsetF"] / fps for m in src.moves if m["impact"]]
        if impacts:
            decl.append("impact:%d" % len({m["el"] for m in src.moves if m["impact"]}))
        events += impacts
    events = sorted(set(round(e, 4) for e in events))
    if not events or not audio.onsets:
        return _row("C18", {"events": len(events), "onsets": len(audio.onsets)},
                    None, na=True,
                    na_reason="no visual events or no detected audio onsets to align",
                    declarations=decl)

    deltas = []
    for e in events:
        near = min(audio.onsets, key=lambda t: abs(t - e))
        deltas.append((e - near) * 1000.0)      # positive = sound leads

    locked = [d for d in deltas if abs(d - centre_ms) <= window_ms]
    lock_rate = len(locked) / len(deltas)
    mean_abs = float(np.mean([abs(d - centre_ms) for d in locked])) if locked else 999.0
    bias = float(np.mean(deltas))

    # hitRate against BAR LINES when a tempo is detected. On a 150 BPM bed over
    # 26 s the strongest quartile is about 30 events, so a 60 % raw hit rate
    # demands a visual change every 0.8 s, which is exhaustion, not craft.
    bars = audio.bar_lines(fps, px.n, C18_BEATS_PER_BAR) if audio.grid else []
    grid_used = False
    hit_rate = None
    if bars:
        tol = fscale(C18_GRID_TOL_FRAMES, fps)
        on_grid = sum(1 for c in ctx.cuts if any(abs(c - b) <= tol for b in bars))
        if on_grid / max(len(ctx.cuts), 1) >= C18_GRID_SHARE:
            grid_used = True
            targets = [b / fps for b in bars]
            hit_ok = sum(1 for t in targets
                         if any(abs(t - e) * 1000.0 <= window_ms for e in events))
            hit_rate = hit_ok / max(len(targets), 1)
    if not grid_used:
        hit_ok = sum(1 for t in audio.hits
                     if any(abs(t - e) * 1000.0 <= window_ms for e in events))
        hit_rate = hit_ok / max(len(audio.hits), 1)

    gate = c18d_audio_delivery(ctx)
    gate_ok = gate["na"] or gate["band"] != "C"

    if lock_rate < C18_B_LOCK or bias > C18_C_BIAS_EARLY_MS or bias < C18_C_BIAS_LATE_MS:
        band = "C"
    elif lock_rate >= C18_S_LOCK and mean_abs <= C18_S_MEANABS and gate_ok:
        band = "S"
    elif lock_rate >= C18_A_LOCK and gate_ok and \
            (not grid_used or hit_rate >= C18_A_HIT):
        # hitRate bands only against a detected grid. Without a tempo the raw
        # onset rate is the wrong statistic and an SFX-only track, which the
        # rubric says is professional, has no bars at all.
        band = "A"
    else:
        band = "B"

    worst = rank_worst([(abs(d - centre_ms), int(events[i] * fps))
                        for i, d in enumerate(deltas)])
    note = ""
    if bias > C18_C_BIAS_EARLY_MS:
        note = ("sound leads picture by %.0f ms on average, past the EBU R37 emission "
                "limit of %.0f ms early" % (bias, C18_C_BIAS_EARLY_MS))
    elif bias < C18_C_BIAS_LATE_MS:
        note = "sound trails picture by %.0f ms on average" % (-bias)
    elif lock_rate < C18_A_LOCK:
        note = ("only %.0f%% of cuts and hero onsets land on an audio onset"
                % (lock_rate * 100))
    elif grid_used and hit_rate < C18_A_HIT:
        note = "only %.0f%% of bar lines carry a visual change" % (hit_rate * 100)
    elif not gate_ok:
        note = "the delivery gate C18D is C, which caps this row at B"
    if not grid_used:
        note = (note + "; " if note else "") + \
            ("no tempo grid: hitRate %.2f against raw onsets is reported, not banded"
             % hit_rate)

    return _row("C18", {
        "lockRate": round(lock_rate, 3), "hitRate": round(hit_rate, 3),
        "meanAbsMs": round(mean_abs, 1), "biasMs": round(bias, 1),
        "events": len(events), "grid": ("bars" if grid_used else "onsets"),
        "windowMs": round(window_ms, 1), "centreMs": round(centre_ms, 1),
    }, band, worst, note, declarations=decl)


def c18d_audio_delivery(ctx):
    """The delivery GATE: integrated loudness AND TRUE peak against the
    DECLARED delivery. Weight 0, because a gate already caps the overall grade
    and weighting it as well double-penalises the same defect.

    S: both inside the declared target.
    C: true peak over the limit, loudness OVER the top of the window by more
       than EBU R128's own tolerance, or no `delivery` declared at all.
       Quieter than the window caps the row at B: a platform lifts it. There is no defensible default: broadcast,
       web and social differ by 8 LU.

    STILL SCORES C ON: a bed mixed at -8 LUFS with a true peak of +0.6 dBTP. Both
    halves fail, the gate is C, and the piece is capped at C however good the
    craft rows are.
    """
    man = _manifest(ctx)
    audio = getattr(ctx, "audio", None)
    silent = bool(man.get("silent"))
    decl = ["silent"] if silent else []

    if silent and (audio is None or not audio.present):
        return _row("C18D", {"silent": True}, None, na=True,
                    na_reason="manifest declares silent: true", declarations=decl)
    if audio is None or not audio.present:
        return _row("C18D", {"audio": "none"}, "C", [],
                    "no audio and no silent declaration: there is no mix to deliver")

    delivery = man.get("delivery")
    if delivery not in C18D_LOUDNESS:
        return _row("C18D", {"delivery": "undeclared", "lufs": audio.lufs,
                             "truePeak": audio.true_peak}, "C", [],
                    "no `delivery` declared: broadcast, web and social have different "
                    "loudness and true-peak targets and there is no sensible default")
    decl.append("delivery=%s" % delivery)

    target = tuple(C18D_LOUDNESS[delivery])
    tp_max = C18D_TRUE_PEAK[delivery]
    declared_target = man.get("loudnessTarget")
    rejected = None
    if declared_target and len(declared_target) == 2:
        cand = (float(declared_target[0]), float(declared_target[1]))
        # INTERSECT, never replace. This is the one gate a manifest could move:
        # a film declaring [-17, -14] against the web standard of [-16, -13]
        # turned a measured -17.0 LUFS from B into S, a two-band self-certified
        # improvement on a gate. A declaration may narrow the window -- an
        # author holding themselves to a tighter target is welcome to -- and it
        # may never widen it, so the delivery standard is always the outer
        # bound and the escape is closed rather than merely budgeted.
        tight = (max(cand[0], target[0]), min(cand[1], target[1]))
        if tight[0] <= tight[1] and tight != target:
            target = tight
            decl.append("loudnessTarget=%s" % list(tight))
        if cand[0] < target[0] or cand[1] > target[1]:
            rejected = cand
    if man.get("truePeakMax") is not None:
        try:
            cand = float(man["truePeakMax"])
            if cand <= C18D_TRUE_PEAK[delivery] + 1.0:
                tp_max = cand
                decl.append("truePeakMax=%s" % cand)
        except (TypeError, ValueError):
            pass

    lufs, tp = audio.lufs, audio.true_peak
    loud_ok = lufs is not None and target[0] <= lufs <= target[1]
    peak_ok = tp is not None and tp <= tp_max
    # ASYMMETRIC, because loudness delivery is. A programme over the top of its
    # window is turned DOWN by every platform that normalises, with whatever
    # true peak it was mastered at already baked in, and that is a delivery
    # failure; one under the bottom is turned UP and loses nothing but headroom.
    # The old symmetric 2 LU slack granted B on either side and was the one
    # number in this file with no source. Over the top now fails past EBU R128's
    # own 0.5 LU normalisation tolerance; under the bottom caps the row at B and
    # prints the shortfall.
    too_loud = lufs is not None and lufs > target[1] + C18D_LOUD_TOL_LU
    too_quiet = lufs is not None and lufs < target[0]

    if loud_ok and peak_ok:
        band = "S"
    elif peak_ok and too_quiet and not too_loud:
        band = "B"
    else:
        band = "C"

    note = ""
    if not peak_ok:
        note = "true peak %s dBTP over the %s dBTP %s limit" % (tp, tp_max, delivery)
    elif not loud_ok:
        note = ("integrated %s LUFS, %s target %s to %s"
                % (lufs, delivery, target[0], target[1]))
    if rejected:
        note = (note + "; " if note else "") + \
            ("declared loudnessTarget %s reaches outside the published %s window "
             "%s and was narrowed to it: a declaration may tighten a delivery "
             "gate and may not widen one"
             % (list(rejected), delivery, list(C18D_LOUDNESS[delivery])))
    return _row("C18D", {"delivery": delivery, "lufs": lufs, "truePeak": tp,
                         "target": list(target), "truePeakMax": tp_max},
                band, [], note, declarations=decl)


# =============================================================================
# C19  reveal craft and motion blur
# =============================================================================

def _echo_cover(ctx):
    """`echoTrails` as declared ranges and declared element names, never as a
    blanket. One entry used to cover every fast frame in the film, which is a
    global threshold change bought with a single declaration."""
    man = _manifest(ctx)
    raw = man.get("echoTrails") or []
    ranges, names = [], []
    for e in raw:
        if isinstance(e, dict) and "from" in e:
            ranges.append((int(e["from"]), int(e.get("to", e["from"]))))
        elif isinstance(e, (list, tuple)) and len(e) == 2:
            ranges.append((int(e[0]), int(e[1])))
        elif isinstance(e, str):
            names.append(e)
    return ranges, names


SIGNAL_KINDS = (
    ("translate", ("x", "y", "xPercent", "yPercent", "left", "top",
                   "translateX", "translateY")),
    ("scale", ("scale", "scaleX", "scaleY", "width", "height")),
    ("rotate", ("rotation", "rotationX", "rotationY", "skewX", "skewY")),
    ("paint", ("opacity", "autoAlpha", "alpha", "color", "backgroundColor",
               "fill", "stroke")),
    ("optical", ("filter", "boxShadow", "textShadow", "backdropFilter")),
    ("mask", ("clipPath", "strokeDashoffset", "maskPosition", "maskSize")),
)


def _signal_kinds(props):
    """How many DISTINCT mechanics an entrance drives, canon 3.2's "concurrent
    signals". Two translate properties are one signal; a rise plus a fade plus a
    defocus is three."""
    out = set()
    for name, members in SIGNAL_KINDS:
        if props & set(members):
            out.add(name)
    return out


def c19_reveal_craft(ctx):
    """(a) the share of entrances that are opacity-only and the count of
    structural reveal devices; (b) motion-blur or shutter coverage of every
    fast frame, with no blurred frame touching a cut. Weight 2.

    An entrance is opacity-only when it changes no spatial property, or when it
    changes opacity and travels less than 5 % of frame height with no clip
    path and no scale from zero. Structural devices are clip-path or mask
    wipes, scale from mask, masked rise, character or line cascade, split
    reveal and grow-to-fill; a manifest may declare at most one more.

    S: opacity-only <= 0.25, at least two structural devices, 100 % of fast
       frames covered, and no blurred frame on a cut frame.
    C: opacity-only > 0.60, or blur coverage under 60 %.

    STILL SCORES C ON: eleven cards that each fade up in place with a 12 px rise.
    Every entrance is opacity-only, the share is 1.00, and the row is C.
    """
    px, src, fps = ctx.px, ctx.src, ctx.fps
    man = _manifest(ctx)
    decl = []
    _travel, _strobe_set, _moving, thr, fast_map = _strobe(ctx)
    shutter = man.get("shutterFrames") or []
    if shutter:
        decl.append("shutterFrames:%d" % len(shutter))
    echo_ranges, echo_names = _echo_cover(ctx)
    if echo_ranges or echo_names:
        decl.append("echoTrails:%d" % (len(echo_ranges) + len(echo_names)))

    # coverage is measured over the fast set BEFORE the shutter exclusion:
    # computing it over a set the covered frames were already removed from
    # reports 0 % by construction
    # canon 5: "Transitions are exempt from the 1/3 travel rule BY CLASS. Whip
    # pans, full-frame wipes, cards flying through frame and infinite zooms
    # cross the whole frame in a straight line at one acceleration, and
    # should." A wipe's leading edge travels fast because that is what a wipe
    # is, and asking for a shutter on it asks the piece to blur its own
    # transition. The class comes from the SOURCE, which is the only channel
    # that can see it: at the pixel level a circle wipe growing over the frame
    # is indistinguishable from the content behind it moving, because what the
    # edge tracker follows is the occlusion boundary.
    transit = _transition_frames(ctx)
    fast_map = {f: v for f, v in fast_map.items() if f not in transit}
    fast = sorted(fast_map)
    cutset = set(ctx.cuts)
    covered, uncovered, blur_at_cut = 0, [], []
    for f in fast:
        ok = any(a <= f <= b for (a, b) in shutter)
        if not ok:
            ok = any(a <= f <= b for (a, b) in echo_ranges)
        if not ok and src is not None and echo_names:
            for e in src.elements:
                if src.is_named(e["i"], set(echo_names)) and _element_fast(ctx, e["i"], f, thr):
                    ok = True
                    break
        if not ok and src is not None and _blur_active(src, f):
            ok = True
        if ok:
            covered += 1
            if f in cutset:
                blur_at_cut.append(f)
        else:
            uncovered.append((fast_map[f], f))
    blur_rate = (covered / len(fast)) if fast else None
    blur_gradeable = blur_rate is not None and len(fast) >= C19_MIN_FAST_FRAMES

    def blur_band(rate):
        if rate >= C19_S_BLUR:
            return "S"
        if rate >= C19_A_BLUR:
            return "A"
        return "C" if rate < C19_C_BLUR else "B"

    if src is None:
        if not blur_gradeable:
            return _row("C19", {"fastFrames": len(fast)}, None, na=True,
                        na_reason="no fast frames and no source channel: neither half "
                                  "of this criterion has anything to measure",
                        declarations=decl)
        band = blur_band(blur_rate)
        if band == "S" and blur_at_cut:
            band = "A"
        return _row("C19", {"blurCoverage": round(blur_rate, 3),
                            "fastFrames": len(fast),
                            "blurAtCut": len(blur_at_cut), "basis": "pixel"},
                    band,
                    rank_worst(_strobe_rank({f: s for s, f in uncovered})),
                    "%d/%d fast frames carry no blur, echo or declared shutter; "
                    "reduced confidence: the reveal half needs the source channel"
                    % (len(uncovered), len(fast)), declarations=decl)

    # ---- (a) reveal craft -------------------------------------------------
    by_el = {}
    for m in src.moves:
        if m["role"] != "entrance" or m["repeat"]:
            continue
        by_el.setdefault(m["el"], []).append(m)
    tol = fscale(C19_ENTRANCE_GROUP_FRAMES, fps)
    entrances = {}
    for el, ms in by_el.items():
        first = min(m["onsetF"] for m in ms)
        # one reveal is every entrance tween that fires with the first; a later
        # re-entrance on the same element is a different event
        entrances[el] = [m for m in ms if m["onsetF"] - first <= tol]

    opacity_only, structural, reveal_worst, signals = 0, set(), [], []
    for el, ms in entrances.items():
        props, travel_max = set(), 0.0
        scale_from_zero, has_clip, grew = False, False, False
        scale_amp, blur_amp, turned = 0.0, 0.0, False
        for m in ms:
            props.update(m["props"])
            travel_max = max(travel_max, m["dist"] / max(src.H, 1.0))
            if m["scaleFrom"] < 0.02:
                scale_from_zero = True
            if "clipPath" in m["props"]:
                has_clip = True
            a, b = float(m["scaleFrom"]), float(m["scaleTo"])
            if a > 0 and b > 0:
                scale_amp = max(scale_amp, abs(b - a) / max(a, b))
            if "rotation" in m["props"] or "rotationX" in m["props"] \
                    or "rotationY" in m["props"]:
                turned = True
            blur_amp = max(blur_amp, _blur_ramp_px(src, m))
            if (m["scaleTo"] >= 1.5 * max(m["scaleFrom"], 1e-6)
                    and m["boxW"] >= C19_GROW_TO_FILL * src.W):
                grew = True
        box_h = max((m.get("boxH", 0.0) for m in ms), default=0.0)
        masked = box_h > 0 and any(abs(m["dist"] - box_h) <= 0.25 * box_h for m in ms)
        if has_clip:
            structural.add("clip-path wipe")
        if scale_from_zero:
            structural.add("scale from mask")
        if masked:
            structural.add("masked rise")
        if grew:
            structural.add("grow-to-fill")
        # The defect canon 8.1 and 8.3 name is "every element enters y: 30,
        # opacity: 0" and "opacity-only entrances": the entrance carries NO
        # mechanic but the fade. Reading it as "no translation over 5 % of
        # frame height" charged three other mechanics that plainly are ones.
        # Canon 3.2 measures the reference's entrances as a stack of signals --
        # "mass on 19 of 23 segments, width on 19, height on 17" -- and a scale
        # ramp changes an element's mass and width, a defocus ramp changes both
        # as well (canon 1.3 puts 3-6 px of blur per depth step), and a rotation
        # changes its axis. A film whose every entrance resolves an 8-11 px blur
        # to zero measured 80 % opacity-only and is not doing the thing.
        bare = not (props & SPATIAL_PROPS) or (
            travel_max < C19_OPACITY_TRAVEL and not has_clip and not scale_from_zero
            and scale_amp < C19_SCALE_AMP and blur_amp < C19_BLUR_AMP_PX
            and not turned)
        if bare:
            opacity_only += 1
            reveal_worst.append((1.0, ms[0]["onsetF"]))
        # CONCURRENT SIGNALS ON THE CARD, canon 3.2: "2-4 concurrent signals on
        # a hero card, driven from one proxy. ONE SIGNAL PER CARD IS THE
        # FLAT-BUT-COMPETENT TELL. The measured reference stacks: mass on 19 of
        # 23 segments, width on 19, height on 17, centroid-x on 14, and almost
        # nothing enters by opacity alone." The device census above counts
        # distinct devices ACROSS THE PIECE, so five identical masked word rises
        # plus one scaling bar satisfy "at least two structural devices" while
        # every card in the piece carries exactly one mechanic. That is canon's
        # named tell and the device count cannot see it.
        signals.append(len(_signal_kinds(props)))

    # a cascade: three or more siblings under one parent with distinct,
    # monotonically increasing entrance onsets
    by_parent = {}
    for el, ms in entrances.items():
        p = src.elements[el].get("parent", -1)
        by_parent.setdefault(p, []).append((ms[0]["onsetF"], el))
    cas_gap = fscale(C19_CASCADE_GAP_FRAMES, fps)
    split_tol = fscale(C19_SPLIT_OPPOSED_FRAMES, fps)
    for p, rows in by_parent.items():
        if p is None or p < 0:
            continue
        ons = sorted(o for o, _e in rows)
        if len(ons) >= C19_CASCADE_MIN:
            gaps = [b - a for a, b in zip(ons, ons[1:])]
            if all(0 < gp <= cas_gap for gp in gaps):
                structural.add("cascade")
        # a split reveal: two siblings entering within a few frames from
        # opposite directions
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                oa, ea = rows[i]
                ob, eb = rows[j]
                if abs(oa - ob) > split_tol:
                    continue
                ma = min(entrances[ea], key=lambda m: m["onsetF"])
                mb = min(entrances[eb], key=lambda m: m["onsetF"])
                if (ma["dx"] * mb["dx"] + ma["dy"] * mb["dy"]) < 0 and \
                        min(ma["dist"], mb["dist"]) > C19_OPACITY_TRAVEL * src.H:
                    structural.add("split reveal")

    declared_devices = [str(d) for d in (man.get("revealDevices") or [])]
    if declared_devices:
        decl.append("revealDevices:%d" % len(declared_devices))
    n_measured = len(structural)
    n_devices = n_measured + min(len(declared_devices), C19_MAX_DECLARED_DEVICES)

    n_ent = max(len(entrances), 1)
    op_share = opacity_only / n_ent
    if op_share > C19_B_OPACITY:
        band_a = "C"
    elif op_share <= C19_S_OPACITY and n_devices >= C19_S_DEVICES:
        band_a = "S"
    elif op_share <= C19_A_OPACITY and n_devices >= C19_A_DEVICES:
        band_a = "A"
    else:
        band_a = "B"
    # REPORTED, NOT BANDED, and the reason is worth keeping. Canon 3.2 says
    # "2-4 concurrent signals on a hero card, driven from one proxy. One signal
    # per card is the flat-but-competent tell", and banding on it was tried:
    # it correctly caught a static title card whose five word rises each drive
    # one property, and it also charged both replicas of aired professional
    # work, which measure 1.0. The tell is real and this is the wrong
    # measurement of it. Canon 3.2's signals are measured ON THE INK -- "mass on
    # 19 of 23 segments, width on 19, height on 17, centroid-x on 14" -- and a
    # masked rise on one CSS property changes mass, height and centroid-y
    # together, so counting authored properties reports 1 for the construction
    # canon measured at 3. The number is printed so a future corpus can fit the
    # right one; it decides nothing.
    med_signals = float(np.median(signals)) if signals else 0.0

    if not blur_gradeable:
        band_b, band = None, band_a
    else:
        band_b = blur_band(blur_rate)
        band = band_worse(band_a, band_b)
    if band == "S" and blur_at_cut:
        # the measured figure for a shutter straddling a cut is a 24.6-unit
        # jump against 1.6 for a clean one: it is a smear across an edit, and
        # canon puts it in the S band's conjunction
        band = "A"

    if band_b is not None and band_b == band and band_b in ("B", "C"):
        note = ("%d/%d frames over %.0f px/frame carry no blur, echo trail or declared "
                "shutter" % (len(uncovered), len(fast), thr * px.width))
        worst = rank_worst(_strobe_rank({f: s for s, f in uncovered}))
    else:
        note = ("%.0f%% of entrances are opacity-only; devices: %s"
                % (op_share * 100,
                   ", ".join(sorted(structural)) if structural else "none"))
        worst = rank_worst(reveal_worst)
    if blur_at_cut:
        note = (note + "; " if note else "") + \
            "%d blurred frame(s) sit on a cut frame" % len(blur_at_cut)
    if declared_devices and n_measured < C19_S_DEVICES:
        note = (note + "; " if note else "") + \
            ("%d device(s) declared, at most %d of which count toward S"
             % (len(declared_devices), C19_MAX_DECLARED_DEVICES))

    return _row("C19", {
        "opacityOnlyShare": round(op_share, 3), "devices": n_devices,
        "devicesMeasured": n_measured, "entrances": len(entrances),
        "medSignalsPerCard": round(med_signals, 1),
        "blurCoverage": (None if blur_rate is None else round(blur_rate, 3)),
        "fastFrames": len(fast), "blurAtCut": len(blur_at_cut),
    }, band, worst, note, declarations=decl)


def _blur_ramp_px(src, m):
    """How many px of `filter: blur()` this entrance resolves, at 1080p."""
    if "filter" not in (m.get("props") or ()):
        return 0.0
    vals = []
    for f in (int(m["startF"]), int(m["endF"])):
        try:
            v = src.style_at(m["el"], "filter", f)
        except Exception:
            v = None
        if not v:
            continue
        mm = re.search(r"blur\(\s*([0-9.]+)px", str(v))
        if mm:
            vals.append(float(mm.group(1)))
    if len(vals) < 2:
        return 0.0
    return abs(vals[0] - vals[1]) * (1080.0 / max(float(src.H), 1.0))


def _transition_frames(ctx):
    """Frames covered by a move that is a transition BY CLASS (canon 5): a
    declared impact, a travel across half the frame, or a scale change of 1.0
    or more. The classification is crit_motion's, read off its compound moves
    so C11 and C19 cannot disagree about what a transition is; the local
    fallback applies the same three tests to the raw move list."""
    src = getattr(ctx, "src", None)
    if src is None:
        return set()
    out = set()
    cms = None
    try:
        import crit_motion
        cms = crit_motion.compound_moves(ctx)
    except Exception:
        cms = None
    if cms:
        for cm in cms:
            if cm.get("transition"):
                for f in range(int(cm["onsetF"]), int(cm["endF"]) + 1):
                    out.add(f)
        return out
    W, H = float(src.W), float(src.H)
    for m in src.moves:
        if m.get("impact") or abs(m.get("dx", 0.0)) >= 0.5 * W                 or abs(m.get("dy", 0.0)) >= 0.5 * H                 or m.get("scaleDelta", 0.0) >= 1.0:
            for f in range(int(m["onsetF"]), int(m["endF"]) + 1):
                out.add(f)
    return out


def _element_fast(ctx, el, f, thr):
    """Is this named element the thing moving fast on frame f. An echo-trail
    declaration by name covers only the frames where the element it names is
    actually the fast one."""
    src = ctx.src
    f = int(clamp(f, 1, src.frames - 1))
    cx, cy = src.prop(el, "cx"), src.prop(el, "cy")
    d = math.hypot(float(cx[f] - cx[f - 1]), float(cy[f] - cy[f - 1]))
    return (d / max(src.W, 1.0)) > thr


# =============================================================================
# C23  encode and delivery QC   /   C23D  duration and cadence (GATE)
# =============================================================================

def c23d_duration(ctx):
    """The GATE: rendered frame count exactly as authored. Weight 0.

    S: the render holds exactly round(declared duration * fps) frames.
    C: anything else. There is no tolerance and no declaration may add one:
       a film that is one frame short is a film whose last authored frame did
       not ship, and every downstream frame index in every note is off.

    STILL SCORES C ON: a composition declaring data-duration 26.0000 at 60 fps,
    which is 1560 frames, whose render holds 1552.
    """
    fps = ctx.fps
    v = getattr(ctx, "video", None) or {}
    frames = int(v.get("frames", ctx.n_frames))
    declared = getattr(ctx, "declared", None) or {}
    man = _manifest(ctx)
    decl = []

    want = None
    if declared.get("duration"):
        want = float(declared["duration"]) * fps
        source = "data-duration=%.4f" % float(declared["duration"])
    elif man.get("durationFrames"):
        want = float(man["durationFrames"])
        source = "manifest durationFrames"
        decl.append("durationFrames=%s" % man["durationFrames"])
    elif man.get("duration"):
        want = float(man["duration"]) * fps
        source = "manifest duration"
        decl.append("duration=%s" % man["duration"])

    if want is None:
        return _row("C23D", {"frames": frames}, None, na=True,
                    na_reason="neither the composition nor the manifest declares a "
                              "duration to check the frame count against",
                    declarations=decl)

    target = int(round(want))
    off = frames - target
    band = "S" if abs(off) <= C23D_FRAME_TOLERANCE else "C"
    note = "" if band == "S" else (
        "%s is %.2f frames at %g fps, which rounds to %d, but the render holds %d "
        "(%+d)" % (source, want, fps, target, frames, off))
    return _row("C23D", {"frames": frames, "declaredFrames": target, "off": off},
                band, [], note, declarations=decl)


def c23_encode_qc(ctx):
    """The deliverable itself: pixel format, colour tags against the actual
    stored range, chroma bleed on thin saturated type, banding after encode,
    audio format, the poster frame, the end-card hold, the loop seam and the
    encoder's bit allocation on the fastest frames.

    Chroma bleed is a note, not a fault, and says so in the row: no
    reference-free measurement of it separates a thin saturated stroke that
    bled from a coloured ground, which is chromatic everywhere and ink nowhere.

    S: no faults. A: one soft fault. B: two or more. C: a hard fault, meaning
    a wrong pixel format, a wrong audio sample rate, or a colour-range tag that
    contradicts what is actually stored in the file. The duration half of C23
    is the gate and lives in c23d_duration.

    STILL SCORES C ON: a web render encoded yuv444p, or one whose audio track is
    44.1 kHz. Either is a hard fault and the row is C.
    """
    px, fps = ctx.px, ctx.fps
    audio = getattr(ctx, "audio", None)
    v = getattr(ctx, "video", None) or {}
    man = _manifest(ctx)
    beats = ctx.beats or []
    decl, notes = [], []
    hard, soft = 0, 0

    if v.get("pix_fmt") and v["pix_fmt"] != C23_PIX_FMT:
        hard += 1
        notes.append("pix_fmt %s, not %s" % (v["pix_fmt"], C23_PIX_FMT))

    if audio is not None and audio.stream:
        if audio.rate and audio.rate != C23_AUDIO_RATE:
            hard += 1
            notes.append("audio at %d Hz, not %d" % (audio.rate, C23_AUDIO_RATE))
        if audio.channels and audio.channels != C23_AUDIO_CH:
            soft += 1
            notes.append("audio is %d channel(s), not stereo" % audio.channels)

    # ---- colour tags against what is actually stored ----------------------
    tag = (v.get("color_range") or "").lower()
    if not tag or not v.get("color_primaries") or v.get("color_primaries") == "unknown":
        soft += 1
        notes.append("colour range or primaries untagged")
    stored = _stored_luma_range(ctx)
    if tag and stored is not None:
        if tag in ("tv", "limited") and stored["fullShare"] > C23_RANGE_FULL_SHARE:
            hard += 1
            notes.append("tagged %s but %.1f%% of stored luma sits past %d/%d: a "
                         "full-range render tagged limited crushes the whole piece"
                         % (tag, stored["fullShare"] * 100,
                            C23_RANGE_FULL[0], C23_RANGE_FULL[1]))
        elif tag in ("pc", "full") \
                and stored["outsideShare"] < C23_RANGE_OUTSIDE_CLEAN \
                and stored["wallShare"] > C23_RANGE_WALL_SHARE:
            hard += 1
            notes.append("tagged %s but the stored luma stops dead at %d and %d with "
                         "%.1f%% of pixels on the wall: a limited-range render tagged "
                         "full washes the whole piece"
                         % (tag, C23_RANGE_TV[0], C23_RANGE_TV[1],
                            stored["wallShare"] * 100))

    # ---- chroma bleed and banding, on a few full-resolution frames --------
    # Chroma bleed is a NOTE in canon C23 and it stays one here, because no
    # reference-free measurement of it separates a thin saturated stroke that
    # bled from a coloured GROUND, which is chromatic everywhere and is ink
    # nowhere. Reported so a reviewer can look; never charged as a fault.
    chroma_bleed, banded = _chroma_and_banding(ctx)
    if chroma_bleed is not None and chroma_bleed > C23_CHROMA_BLEED_SHARE:
        notes.append("report only: %.0f%% of coloured chroma samples sit outside the "
                     "ink they belong to; check thin saturated strokes for 4:2:0 bleed"
                     % (chroma_bleed * 100))
    if banded is not None and banded >= C23_BANDING_EDGES:
        soft += 1
        notes.append("%d banded edges on the sampled grounds after encode" % banded)

    # ---- the poster frame -------------------------------------------------
    declared_open = any(h.get("from", 0) <= 0 <= h.get("to", -1)
                        for h in (man.get("holds") or []) + (man.get("freezes") or []))
    poster = int(man.get("posterFrame", 0) or 0)
    if poster:
        decl.append("posterFrame=%d" % poster)
    if px.ink_frac[int(clamp(poster, 0, px.n - 1))] < C23_FIRST_FRAME_INK \
            and not declared_open:
        # REPORTED, NOT BANDED. Canon 2.4 measures the professional reference at
        # "67 blank frames across 10 runs, of which the 37-frame COLD OPEN is
        # one": opening on black is the medium's own idiom, not a delivery
        # fault. The superseded rubric's line here -- "a usable first frame,
        # because feeds show it as the poster" -- is its own inference against
        # canon's measurement, and which frame a platform posters is a
        # publishing decision taken outside the file. It stays in the note so a
        # reader about to upload knows to pick one.
        notes.append("report only: the poster frame is blank; canon 2.4 measures "
                     "a 37-frame cold open in the reference, so this is the "
                     "medium's idiom -- choose a poster frame at upload")

    # ---- the end card -----------------------------------------------------
    looping = bool(man.get("looping"))
    if looping:
        decl.append("looping")
    end_card = man.get("endCard")
    if end_card is not None:
        decl.append("endCard=%s" % json.dumps(end_card))
    if beats and not looping and end_card is not False:
        end_hold = (px.n - beats[-1][0]) / fps
        if end_hold < C23_END_CARD_S:
            soft += 1
            notes.append("the end card holds %.1fs, under %.0fs"
                         % (end_hold, C23_END_CARD_S))

    # ---- the loop seam, value AND velocity --------------------------------
    if looping and px.n >= 3:
        seam = np.abs(px.grey[0].astype(np.int16) - px.grey[-1].astype(np.int16))
        if float(seam.max()) > C23_LOOP_CODE_VALUE:
            soft += 1
            notes.append("the loop seam differs by %d code values" % int(seam.max()))
        step_in = float(np.abs(px.grey[1].astype(np.int16)
                               - px.grey[0].astype(np.int16)).mean())
        step_seam = float(seam.mean())
        med = float(np.median(px.frame_delta[1:]))
        if med > 0 and step_seam > C23_LOOP_VELOCITY_RATIO * max(step_in, med):
            soft += 1
            notes.append("the loop seam steps %.2f levels against %.2f in the piece: "
                         "a value match with a velocity mismatch hitches every cycle"
                         % (step_seam, med))

    # ---- the bed does not stop dead --------------------------------------
    if audio is not None and audio.present and getattr(audio, "sig", None) is not None:
        tail = _bed_stops_dead(audio)
        if tail:
            soft += 1
            notes.append("the mix is still at %.2f of its own level on the last %.0f ms: "
                         "the bed stops dead rather than ending" % (tail, C23_TAIL_MS))

    # ---- bit allocation on the fastest frames ----------------------------
    ratio, ceiling = _bitrate_on_motion(ctx)
    if ratio is not None and ratio < C23_BITRATE_MIN_RATIO and ceiling:
        soft += 1
        notes.append("the fastest tenth of frames costs %.2fx the median frame and "
                     "%.0f%% of packets sit on one size ceiling: the encoder is "
                     "rate-clipped exactly where the motion is"
                     % (ratio, ceiling * 100))

    band = "C" if hard else ("S" if soft == 0 else "A" if soft == 1 else "B")
    return _row("C23", {
        "pixFmt": v.get("pix_fmt"), "colorRange": v.get("color_range"),
        "colorPrimaries": v.get("color_primaries"),
        "storedLuma": ([stored["lo"], stored["hi"]] if stored else None),
        "storedOutside": (round(stored["outsideShare"], 4) if stored else None),
        "audioRate": (audio.rate if audio else None),
        "audioChannels": (audio.channels if audio else None),
        "chromaBleed": (None if chroma_bleed is None else round(chroma_bleed, 3)),
        "bandedEdges": banded,
        "motionBitrateRatio": (None if ratio is None else round(ratio, 2)),
        "softFaults": soft, "hardFaults": hard,
    }, band, [], "; ".join(notes), declarations=decl)


def _sample_frames(ctx):
    """A handful of settled frames, spread across the piece and never on a cut
    or a blank."""
    px = ctx.px
    blank = _blank_mask(px)
    cuts = set()
    for c in ctx.cuts:
        cuts.update(range(c - 2, c + 3))
    want = []
    for k in range(C23_SAMPLE_FRAMES):
        f = int((k + 0.7) * px.n / C23_SAMPLE_FRAMES)
        for d in range(0, 20):
            for g in (f + d, f - d):
                if 0 <= g < px.n and not blank[g] and g not in cuts and g not in want:
                    want.append(g)
                    break
            else:
                continue
            break
    return sorted(want)


def _raw_yuv(ctx, frames):
    """Pull specific frames at NATIVE resolution as yuv420p, with no scaling
    and no range conversion, so the stored code values survive. Returns
    {frame: (Y, U, V)} with Y at (H, W) and U, V at (H/2, W/2).

    A range decodes to a flat buffer of planes, not to an interleaved array:
    slice the planes out by offset, never reshape the whole thing and reduce
    over the wrong axis."""
    path = getattr(ctx, "render", None) or getattr(ctx.px, "path", None)
    if not path or not frames:
        return {}
    W, H = int(ctx.width), int(ctx.height)
    W2, H2 = W // 2, H // 2
    size = W * H + 2 * W2 * H2
    expr = "+".join("eq(n\\,%d)" % f for f in frames)
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vf", "select='%s'" % expr,
         "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-"],
        capture_output=True).stdout
    arr = np.frombuffer(raw, dtype=np.uint8)
    got = len(arr) // size
    out = {}
    for k in range(min(got, len(frames))):
        base = k * size
        y = arr[base:base + W * H].reshape(H, W)
        u = arr[base + W * H:base + W * H + W2 * H2].reshape(H2, W2)
        v = arr[base + W * H + W2 * H2:base + size].reshape(H2, W2)
        out[frames[k]] = (y, u, v)
    return out


def _stored_luma_range(ctx):
    """What the file actually stores in Y, with no range conversion, over the
    sampled frames. A limited-range render tagged full crushes the piece and a
    full-range one tagged limited washes it, and nothing else in the rubric
    would catch either.

    Ringing on a hard black-on-white edge overshoots 16 and 235 by ten code
    values, so min and max cannot tell a mis-tag from a sharp picture. Returns
    lo, hi and three shares: `outsideShare` past 16/235, `fullShare` past
    6/249, which ringing does not reach and real full-range content does, and
    `wallShare` sitting exactly on 16 or 235."""

    def build():
        frames = _sample_frames(ctx)
        planes = _raw_yuv(ctx, frames)
        if not planes:
            return None
        y = np.concatenate([t[0].reshape(-1) for t in planes.values()]).astype(np.int16)
        lo_tv, hi_tv = C23_RANGE_TV
        lo_f, hi_f = C23_RANGE_FULL
        w = C23_RANGE_WALL
        return {
            "lo": int(y.min()), "hi": int(y.max()),
            "outsideShare": float(((y < lo_tv) | (y > hi_tv)).mean()),
            "fullShare": float(((y < lo_f) | (y > hi_f)).mean()),
            "wallShare": float((np.abs(y - lo_tv) <= w).mean()
                               + (np.abs(y - hi_tv) <= w).mean()),
        }

    try:
        return _cache(ctx, "storedLuma", build)
    except Exception:
        return None


def _dilate(mask, k):
    """Binary dilation by k steps with a plus-shaped element, in numpy. No
    scipy dependency anywhere in this stack."""
    m = mask
    for _ in range(max(int(k), 0)):
        d = m.copy()
        d[1:, :] |= m[:-1, :]
        d[:-1, :] |= m[1:, :]
        d[:, 1:] |= m[:, :-1]
        d[:, :-1] |= m[:, 1:]
        m = d
    return m


def _chroma_and_banding(ctx):
    """(chroma bleed share, count of banded edges) on a few frames at native
    resolution. Both are notes in canon C23, so they cost a soft fault and
    never a hard one.

    Bleed is measured as what the words mean: 4:2:0 stores one chroma sample
    per 2x2 luma block, so colour belonging to a thin saturated stroke spreads
    into blocks the stroke does not occupy. Take the coloured chroma samples,
    take the ink mask at chroma resolution, dilate it by one sample to allow
    the honest half-pixel of siting, and the colour still outside it is bleed.
    On a monochrome film there are no coloured samples and the row reports
    nothing rather than reporting an artefact."""

    def build():
        frames = _sample_frames(ctx)
        planes = _raw_yuv(ctx, frames)
        if not planes:
            return (None, None)
        bleed_num, bleed_den, banded = 0, 0, 0
        for f, (y, u, v) in planes.items():
            yi = y.astype(np.int16)
            ui = u.astype(np.int16)
            vi = v.astype(np.int16)
            ch = np.maximum(np.abs(ui - 128), np.abs(vi - 128))
            coloured = ch > C23_CHROMA_UV
            n = int(coloured.sum())
            if n:
                H2, W2 = ch.shape
                # the 2x2 box mean of Y, which is the luma the chroma sample
                # actually covers
                y2 = (yi[0:2 * H2:2, 0:2 * W2:2].astype(np.int32)
                      + yi[1:2 * H2:2, 0:2 * W2:2]
                      + yi[0:2 * H2:2, 1:2 * W2:2]
                      + yi[1:2 * H2:2, 1:2 * W2:2]) / 4.0
                ground = float(np.median(y2))
                ink = np.abs(y2 - ground) > 28.0
                bleed_den += n
                bleed_num += int((coloured & ~_dilate(ink, 1)).sum())
            # banding: a staircase down the middle column and across the middle
            # row, a small step with flat runs either side of it
            for line in (yi[yi.shape[0] // 2].astype(float),
                         yi[:, yi.shape[1] // 2].astype(float)):
                d = np.diff(line)
                for step in np.flatnonzero(np.abs(d) >= C23_BANDING_STEP):
                    lo = max(0, step - C23_BANDING_RUN)
                    hi = min(len(d), step + C23_BANDING_RUN)
                    left, right = d[lo:step], d[step + 1:hi]
                    if len(left) and len(right) and \
                            np.abs(left).max() <= 1 and np.abs(right).max() <= 1:
                        banded += 1
        share = (bleed_num / bleed_den) if bleed_den >= C23_CHROMA_MIN_PX else None
        return (share, banded)

    try:
        return _cache(ctx, "chromaBanding", build)
    except Exception:
        return (None, None)


def _bed_stops_dead(audio):
    """The level of the last C23_TAIL_MS against the half second before it. A
    mix that ends at full level was cut, not finished."""
    sig = np.asarray(audio.sig, dtype=float)
    sr = 22050
    tail = int(sr * C23_TAIL_MS / 1000.0)
    ref = int(sr * C23_TAIL_REF_MS / 1000.0)
    if len(sig) < tail + ref:
        return None
    a = float(np.sqrt(np.mean(sig[-tail:] ** 2)))
    b = float(np.sqrt(np.mean(sig[-(tail + ref):-tail] ** 2)))
    if b <= 0 or a < C23_TAIL_FLOOR:
        return None
    r = a / b
    return r if r > C23_TAIL_RATIO else None


def _bitrate_on_motion(ctx):
    """(ratio, ceilingShare). `ratio` is the median packet size of the fastest
    tenth of frames over the median packet size of the film: a healthy encode
    spends more bits where the motion is. On its own that ratio is noise,
    because packet sizes are dominated by where the keyframes fell, so the
    fault also wants the signature of an actual cap, which is a pile of packets
    all sitting at one size."""

    def build():
        path = getattr(ctx, "render", None) or getattr(ctx.px, "path", None)
        if not path:
            return (None, None)
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "packet=size", "-of", "csv=p=0", path],
            capture_output=True, text=True).stdout
        sizes = [int(x) for x in out.split() if x.strip().rstrip(",").isdigit()]
        if len(sizes) < ctx.px.n // 2:
            return (None, None)
        sizes = np.asarray(sizes[:ctx.px.n], dtype=float)
        motion = np.asarray(ctx.px.changed_frac[:len(sizes)], dtype=float)
        k = max(4, int(len(sizes) * C23_BITRATE_TOP_DECILE))
        top = np.argsort(motion)[-k:]
        med = float(np.median(sizes))
        if med <= 0:
            return (None, None)
        biggest = float(sizes.max())
        ceiling = float((sizes >= (1.0 - C23_BITRATE_CEIL_TOL) * biggest).mean())
        return (float(np.median(sizes[top])) / med,
                ceiling if ceiling >= C23_BITRATE_CEIL_SHARE else 0.0)

    try:
        return _cache(ctx, "bitrateRatio", build)
    except Exception:
        return (None, None)


# =============================================================================
# the family
# =============================================================================

FAMILY = [
    ("C4", c4_hold_ratio),
    ("C5", c5_frame_integrity),
    ("C17", c17_transition_design),
    ("C18", c18_audio_sync),
    ("C18D", c18d_audio_delivery),
    ("C19", c19_reveal_craft),
    ("C23", c23_encode_qc),
    ("C23D", c23d_duration),
]


def evaluate(ctx):
    """Every row this family owns, in report order."""
    return [fn(ctx) for _cid, fn in FAMILY]


# =============================================================================
# __main__: grade one render with this family alone, so the criteria can be
# exercised without waiting on the integrator. It builds the context out of
# grade-mg.py's own objects by file path, because the module name carries a
# hyphen and because four agents are editing that file concurrently: a failure
# to import is reported, never raised.
# =============================================================================

def _build_ctx_from_grade_mg(render, comp=None, manifest_path=None, probe=None):
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location(
        "grade_mg", os.path.join(here, "grade-mg.py"))
    gm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gm)

    v = gm.ffprobe_video(render)
    fps, n = v["fps"], v["frames"]
    man = {}
    if manifest_path is None and comp:
        cand = os.path.join(comp if os.path.isdir(comp) else os.path.dirname(comp),
                            "grade.json")
        manifest_path = cand if os.path.exists(cand) else None
    if manifest_path and os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as fh:
            man = json.load(fh)
    declared = gm.read_declared(gm.composition_entry(comp)) if comp else None

    px = gm.Pixel(render, fps, n, v["width"], v["height"])
    src = None
    if probe:
        tp = os.path.join(probe, "tracks.json")
        wp = os.path.join(probe, "tweens.json")
        if os.path.exists(tp) and os.path.exists(wp):
            with open(tp, encoding="utf-8") as fh:
                tracks = json.load(fh)
            with open(wp, encoding="utf-8") as fh:
                tweens = json.load(fh)
            src = gm.Source(tracks, tweens, fps, man)
    audio = gm.Audio(render, fps, man)
    cuts, _basis = gm.detect_cuts(px, man, src)
    beats = gm.beats_from_cuts(cuts, px.n, px)

    class Ctx(object):
        pass
    ctx = Ctx()
    ctx.fps, ctx.n_frames = fps, px.n
    ctx.width, ctx.height = v["width"], v["height"]
    ctx.render = render
    ctx.px, ctx.src, ctx.audio = px, src, audio
    ctx.manifest, ctx.cuts, ctx.beats = man, cuts, beats
    ctx.video, ctx.declared = v, declared
    ctx.cache = {}
    ctx.strobe = gm.strobe_scan(px, src, cuts, man, fps)
    ctx.heroes = gm.hero_moves(src, beats, px) if src is not None else []
    return ctx


def _main():
    import argparse
    ap = argparse.ArgumentParser(description="the structure family, alone")
    ap.add_argument("render")
    ap.add_argument("--composition")
    ap.add_argument("--manifest")
    ap.add_argument("--probe", help="dir holding tracks.json and tweens.json")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    ctx = _build_ctx_from_grade_mg(a.render, a.composition, a.manifest, a.probe)
    rows = evaluate(ctx)
    if a.json:
        print(json.dumps(rows, indent=2, default=float))
        return
    print()
    for r in rows:
        band = "N/A" if r["na"] else r["band"]
        meas = ", ".join("%s=%s" % (k, v) for k, v in r["measured"].items())
        print("  %-5s %-24s w%d%s %-4s %s"
              % (r["id"], r["name"], r["weight"], "*" if r["gate"] else " ",
                 band, meas[:120]))
        if r["note"]:
            print("        -> %s" % r["note"])
        if r["declarations"]:
            print("        declarations: %s" % ", ".join(r["declarations"]))
        if r["worstFrames"]:
            print("        worst@ %s" % ",".join(str(f) for f in r["worstFrames"]))
    print()


if __name__ == "__main__":
    _main()
