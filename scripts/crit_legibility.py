#!/usr/bin/env python3
"""crit_legibility.py -- the legibility family of the corrected grading rubric.

Specification: references/canon.md section 7, with
section 3 (type), section 3.3 (safe area) and section 8 (the amateur tells) as
the supporting definitions.  Where canon and the superseded
_research/grading-rubric.md disagree, canon wins; grading-rubric.md is used only
for measurement machinery canon does not restate (the two channels, the shared
definitions of move / onset / settle, the manifest shape).

Six criteria live here, each an independent function of one context object:

    C12  type hierarchy         weight 1
    C13  contrast               weight 0, GATE
    C14  safe margins           weight 1, NO LONGER A GATE
    C15  readability dwell      weight 1
    C16  palette adherence      weight 1
    C20  photosensitive flash   weight 0, GATE

Every function has the same signature and returns the same dict:

    def c13_contrast(ctx) -> dict:
        {"id": "C13", "name": "contrast", "band": "S"|"A"|"B"|"C"|None,
         "weight": int, "gate": bool, "na": bool, "measured": {...},
         "worstFrames": [int], "basis": str, "note": str,
         "declarations": [str]}

`band` is None exactly when `na` is True.  `worstFrames` is ranked WORST FIRST
by severity and is never re-sorted by frame number: the frame the note names has
to be the first frame the reader opens.  `declarations` lists the manifest keys
this criterion actually consumed on this piece, so the integrator can add them
up for the declaration budget.

-----------------------------------------------------------------------------
THE CONTEXT OBJECT
-----------------------------------------------------------------------------
`ctx` may be any object with the attributes below, or a plain dict with the same
keys.  Everything is read through `_get`, so an integrator can hand over the
grader's own locals wrapped in a `types.SimpleNamespace` and be done.

REQUIRED

  ctx.px          a grade-mg.py `Pixel`.  Used members:
                    .n                 int, decoded frame count
                    .fps               float
                    .width, .height    float, DELIVERED pixel dimensions
                    .path              str, the mp4 (only for the C20 fallback)
                    .grey              (n, H, W) uint8, decode-size luma
                    .mask              (n, H, W) bool, |luma - ground| > 28
                    .core              (n, H, W) bool, |luma - ground| > 70
                    .ground            (n,) float, per-frame median luma
                    .ink_frac          (n,) float
                    .comps             list per frame of
                                       (area, cx, cy, x0, y0, x1, y1)
                    .tracks            [{frames, cx, cy, area, box}]
                    .rgb(frames)       {frame: (H, W, 3) uint8}
                    .flash_transitions() -> (frames, signs)   [optional]
                  The decode size is read off px.mask.shape, never assumed, so
                  a vertical deliverable decoded at its own aspect works.

  ctx.manifest    dict, grade.json.  Keys read by this family, all optional:
                    delivery       "broadcast" | "web" | "social"    C12 C14
                    typeScale      [float, ...] sizes in COMPOSITION px    C12
                    croppedType    [element name, ...] cropped on purpose  C14
                    decorativeType [element name, ...] accent or incidental
                                   type not carrying required information; the
                                   WCAG 1.4.3 carve-out, capped at 25 % of the
                                   settled text elements                   C13
                    fullBleed      [{from, to, box?, why}] frame windows
                                   where the frame is covered on purpose C13 C14
                    socialSafe     ["tiktok" | "reels", ...]              C14
                    palette        ["#RRGGBB", ...]                       C16
                    footageRegions [{box: [x0, y0, x1, y1] in decode px}]  C16
                    themeChanges   truthy: the piece flips ground on purpose C16
                  `delivery` DESCRIBES the piece rather than relieving it:
                  declaring broadcast makes C14 stricter, not looser, which is
                  why it is not on the exemption list.  `croppedType` and
                  `decorativeType` are exemptions and are counted as such.
                  Nothing in this family reads `register`.  Legibility is not a
                  register-dependent property: a premium film and a playful one
                  both have to be readable.  C20 has no key at all: it is the
                  one defect in scope that can harm a viewer, and a statement
                  of intent does not move a seizure threshold.

OPTIONAL

  ctx.src         a grade-mg.py `Source`, or None.  Used members:
                    .W, .H, .fps, .frames
                    .elements                 [{i, key, id, text, ...}]
                    .text_elements()          [el index]
                    .settled_window(el, cuts) (a, b) or None
                    .font_px(el, f)           float, CSS font-size in px
                    .box_at(el, f)            (x0, y0, x1, y1) in stage px
                    .chars_at(el, f, own)     int
                    .prop(el, name)           (frames,) float
                    .style_at(el, name, f)    str or None
                    .style_runs               per element {prop: [(f, value)]}
                    .is_named(el, names)      bool
                  Without it C13, C14 and C16 fall back to the pixel channel at
                  reduced confidence and say so, C12 falls back to component
                  cap heights and caps at B, and C15 can only measure the
                  absolute-dwell half.

  ctx.cuts        [int] frame indices of cut boundaries.  Default [].
  ctx.beats       [(a, b)] content runs between cuts.  Default: derived from
                  ctx.cuts, or one beat over the whole film.
  ctx.fps         float.  Default ctx.px.fps.
  ctx.width       float delivered width.   Default ctx.px.width.
  ctx.height      float delivered height.  Default ctx.px.height.
  ctx.delivery    str.  Default ctx.manifest["delivery"], then DEFAULT_DELIVERY.

Nothing here mutates ctx, and no function depends on another having run.

-----------------------------------------------------------------------------
MEASUREMENT CAUTIONS CARRIED FROM THE SKILL
-----------------------------------------------------------------------------
  - decoding a RANGE gives (n, H, W, 3); reduce over the LAST axis, never axis 2
  - clip windows are [start, start + duration); bias both ends inward
  - smooth an ink count before looking for reversals, grain manufactures them
  - never measure motion on a bounding box, use the ink COUNT integral
  - exempt by NAME through the manifest, never by loosening a threshold
  - worstFrames is ranked by SEVERITY, never by frame number

-----------------------------------------------------------------------------
WHAT CHANGED FROM THE EIGHTEEN-CRITERION CODE, AND WHY
-----------------------------------------------------------------------------
C12  Bands on scale ADHERENCE plus minSize, not on a size count and a weight
     span.  Single-size single-weight systems (Swiss, a Saul Bass title, one
     word per card) are canonical professional work and scored C under
     "weightSpan 0, video needs 300+"; half the bundled faces cannot reach a
     300 span at all, so that test graded the font menu.

C13  Rebuilt as a measurement.  The C band is canon's verbatim -- worst below
     2.5:1, or fewer than 95 % of settled frames at or above 3:1 -- and every
     change below is to what the measurement SEES, never to that number:

       - the ground is LOCAL, the median of the element's own expanded box
       - the foreground is the glyph BODY, defined as everything at least half
         as far from the ground as the 95th percentile of ink deviation, so it
         works at any contrast and does not pick the antialiased seam
       - the background excludes a dilated ink mask, so the halo, which is
         neither ground nor glyph, stops being averaged into the ground
       - the tiles vary only the BACKGROUND: the type has one colour, and
         finding the patch where the ground is worst is the whole point of
         canon's 10th percentile
       - the window is the CARD's settled window, and inside it only the frames
         whose rendered ink strength sits at the element's own plateau, so a
         fade driven from a parent is not graded as settled type
       - a box straddling two planes (a label on a chip) has the page dropped
         before the label is measured
       - a box with no ink, a box covered by a solid, and a box under eight
         decode pixels are NOT MEASURABLE and are excluded and counted, rather
         than scored 1.00:1

     Between them these moved a finished film's worst settled contrast from
     1.34:1 to 2.63:1 and its share above 3:1 from 0.83 to 0.96, without moving
     a band boundary.  The WCAG small-text 4.5:1 rule can no longer fire the
     gate on its own; it caps the band at B, because 4.42 against 4.5 is
     decoder noise and this is a gate.  Weight 0: one legibility problem should
     not also destroy the craft score.

C14  No longer a gate.  Delivery-aware: broadcast gets 93 % action and 90 %
     title, web gets the 4 % edge check canon section 3.3 endorses, social gets
     the platform rectangles.  The ink test is restricted to TRACKED
     components, so a full-bleed panel or an edge-anchored band no longer
     breaches on every frame of the piece, and cropped type is exempt by
     declared element name.  Declaring broadcast delivery makes C14 STRICTER,
     which is why delivery is a description and not an exemption.

C15  Two models by role.  Body text keeps the Netflix subtitle rates; display
     type is read as a shape and is graded per WORD, failing under 130 ms per
     word or under 8 frames absolute.  The two rates differ by about six times
     for the same text and cannot both drive one number.  The unit graded is a
     CARD, not a DOM element: a per-letter cascade scored 17 ms per word on a
     finished film because a single letter is not a thing anybody reads.  Two
     regimes are DERIVED rather than declared, exactly as canon 3.1 requires:
     joining against replace-in-place, from whether the windows overlap; and
     read against flash, from whether the card introduces a word not already
     shown, which is what exempts a rapid-fire reprise of established copy.

C16  Bands on palette adherence at CIEDE2000 8 against a DECLARED palette, with
     the dominant ground required to be a palette entry and banding measured
     after encode.  A legitimately monochrome or one-bit piece is graded on
     neutral adherence instead of chromatic adherence: the old code divided a
     zero chromatic count by one and reported adherence 0, which scored a whole
     professional style family C.  The hue census survives as a report line
     only; nothing in the cited 60-30-10 sources licenses nHues <= 3 as a pass.

C20  New, and a gate.  At most three full-frame luminance reversals in any
     rolling one-second window (WCAG 2.3.1, ITU-R BT.1702).  There is no
     declaration that relieves it: it is the one defect in scope that can harm
     a viewer.  The red-flash half of SC 2.3.1 is NOT measured here and the
     measured dict says so.
"""

import json
import math
import os
import re
import subprocess
import sys

import numpy as np

# =============================================================================
# CONSTANTS.  Every threshold this family owns lives here and nowhere else,
# named C<criterion>_*, because all of them will be re-tuned.
# =============================================================================

# ---- shared ----------------------------------------------------------------
INK_DELTA = 28                   # |luma - local ground| for the ink mask
CORE_DELTA = 70                  # |luma - local ground| for the type core mask
COMPONENT_MIN_PX = 40            # smaller than this is noise at 640 wide
REF_HEIGHT_1080 = 1080.0         # every type size is quoted at this height
DEFAULT_DELIVERY = "web"         # canon 3.3: broadcast overscan does not exist
                                 # in any delivery path here, so web is the
                                 # medium's default and broadcast is DECLARED.
                                 # Declaring broadcast tightens C14, never
                                 # loosens it, so this default cannot be gamed.
DELIVERIES = ("broadcast", "web", "social")

# ---- C12 type hierarchy ----------------------------------------------------
C12_SIZE_CLUSTER = 0.10          # settled sizes within 10 % are one size
C12_SCALE_TOL = 0.10             # canon C12: on the declared scale within 10 %
C12_SCALE_RATIOS = [1.125, 1.2, 1.25, 1.333, 1.414, 1.5, 1.618, 2.0]
C12_A_EXCEPTIONS = 1             # A allows one settled size off the scale
C12_MIN_PX = 18.0                # canon 3.3 floor at 1080p
C12_SOCIAL_BODY_PX = 32.0        # canon 3.3 in-feed body floor
C12_SOCIAL_HEAD_PX = 90.0        # canon 3.3 in-feed headline floor
C12_CAP_TO_EM_MIN = 0.66         # pixel channel: cap height / em, the LOW end.
                                 # Dividing by the low end gives the LARGEST
                                 # plausible font size, so a pixel-only C is a
                                 # size that fails even on the generous read.
C12_PIXEL_MIN_ASPECT = 3.0       # a word is at least this many times as wide as
                                 # it is tall; below it the component is a glyph,
                                 # a bullet or a period, not a size sample
C12_PIXEL_MIN_H = 6              # decode px; below this the height is noise

# ---- C13 contrast (GATE, weight 0) ----------------------------------------
C13_S_RATIO = 4.5                # canon C13 S: worst >= 4.5:1
C13_A_RATIO = 3.0                # WCAG 2.2 SC 1.4.3 large text
C13_C_RATIO = 2.5                # canon C13 C: worst < 2.5:1
C13_SHARE_FLOOR = 0.95           # canon C13 C: < 95 % of settled frames >= 3:1
C13_SMALL_TEXT_PX = 24.0         # 1080p-equivalent; below this WCAG wants 4.5
C13_SMALL_TEXT_RATIO = 4.5
C13_BOX_EXPAND = 0.10            # the box is expanded by this before measuring
C13_RING_MIN_PX = 3              # ... by at least this many decode px
C13_MIN_RING_PX = 24             # ring pixels needed before the ring is trusted
C13_GROUND_INK_MAX = 0.50        # the local ground is the MEDIAN of the expanded
                                 # box, because ground is the majority of any
                                 # type box.  A ring median is what the earlier
                                 # version used and it fails on packed inline
                                 # spans, where the ring sits inside the
                                 # neighbouring letters: per-letter spans in a
                                 # cascade measured 1.34:1 on white-on-cream
                                 # type.  If the median leaves more than this
                                 # share as ink it picked the glyph, and the
                                 # ring median is used instead.
C13_SETTLE_FRAC = 0.90           # a sampled frame counts as SETTLED only when
                                 # the box's own ink strength is at least this
                                 # much of the window's TYPICAL level.
                                 # settled_window tests the element's OWN
                                 # opacity, so a fade applied to a parent leaves
                                 # half a fade inside the "settled" window and
                                 # the criterion grades frames the type was
                                 # still arriving on.  The reference level is
                                 # the MEDIAN of the series, never its peak: a
                                 # peak is set by a single frame, and one frame
                                 # of a wipe crossing the box trimmed away every
                                 # genuinely settled frame of a whole card.
C13_SETTLE_REF_PCTL = 75.0       # ... and the median is wrong the other way on a
                                 # short window that is half arrival, where the
                                 # median IS an arrival value.  The upper
                                 # quartile lands on the plateau in both cases.
C13_SETTLE_MAX_MULT = 1.6        # ... and a frame whose box deviates this much
                                 # MORE than its own settled level is showing
                                 # something that is not its type: a wipe or a
                                 # panel crossing it.  Without the upper bound
                                 # the trim keeps exactly the occlusion frames.
C13_PLANE_SEP = 20.0             # luma between the ring plane and the box
                                 # ground.  Past it the element's box straddles
                                 # two planes: a pill, a chip or a badge whose
                                 # bounding box shows the page through its
                                 # corners.  The page and the antialiased seam
                                 # around it are then brighter than the label
                                 # is dark, so they were read as the foreground
                                 # and the row reported the BADGE against the
                                 # page instead of the label against the badge:
                                 # a black label on a chartreuse chip on white
                                 # measured 1.26:1.
C13_PLANE_TOL = 24.0             # ... and everything within this of the page
                                 # plane, dilated twice to take the seam with
                                 # it, is dropped before the type is measured
C13_MAX_INK_FILL = 0.85          # a box this full of ink is covered by a solid,
                                 # not carrying glyphs.  Type covers 20-50 % of
                                 # its own tight box; a wipe or a panel passing
                                 # over it covers all of it, and measuring that
                                 # measures the wipe.
C13_HOLD_FLOOR_FRAMES = 8        # frames at 30 fps. Canon 1.9: "Hold a settled
                                 # pose at least 6-8 frames before any cut, or
                                 # the settle is never seen." An element whose
                                 # own settled window is shorter than that is a
                                 # flash, its legibility is C15's dwell row, and
                                 # gating a whole film on the colour of
                                 # something nobody has time to read is the
                                 # wrong criterion. It is REPORTED here, and the
                                 # hatch is closed by C15, which fails any
                                 # display card under the same floor.
C13_FRAME_PERCENTILE = 10.0      # the element's ratio across its own settled
                                 # frames is the 10th percentile, not the
                                 # minimum. Canon asks for a 10th percentile
                                 # across TILES for exactly this reason and the
                                 # frame axis has the same problem: one sampled
                                 # frame of a 22-frame element whose median is
                                 # 13.3:1 read 2.01:1 and would have failed the
                                 # gate on an encode transient.
C13_DECORATIVE_MAX_SHARE = 0.25  # at most this share of settled text CARDS
                                 # may be declared decorative.  Past it the
                                 # declaration is ignored: an exemption list
                                 # covering most of the type is not an
                                 # exemption, it is a rewrite of the criterion.
C13_CORE_TOP_PCTL = 95.0         # the glyph BODY is defined by how far the type
C13_CORE_OF_MAX = 0.50           # actually sits from its ground -- everything at
                                 # least half as far as the 95th percentile of
                                 # ink deviation -- not by a fixed number of
                                 # levels and not by a fixed share of the ink
                                 # pixels.  A fixed 70-level core cannot see
                                 # low-contrast type at all, so the criterion
                                 # went N/A on exactly the input it exists to
                                 # fail; and a fixed percentile of the ink
                                 # POPULATION picks whichever mode has more
                                 # pixels, which on a dollar sign inside a
                                 # coloured chip is the antialiased seam around
                                 # the chip, and reported 1.08:1 for black on
                                 # chartreuse.
C13_MIN_BOX_PX = 8               # an element box smaller than this in either
                                 # axis at decode resolution cannot carry a
                                 # local ground AND a glyph body.  A pill
                                 # clipped to three pixels at the top edge of
                                 # the frame reported 2.19:1 and was the worst
                                 # sample in a whole film.
C13_MIN_TILE_PX = 6              # a tile smaller than this in either axis is
                                 # not a sample of anything.  A single letter of
                                 # a 96 px cascade is nine decode pixels wide,
                                 # and cutting it into eight columns produced
                                 # eight one-pixel strips: the tile count is
                                 # reduced until the tiles are real.
C13_TILES_X, C13_TILES_Y = 8, 2  # tile the element box: one mean over a
                                 # gradient hides the one region where the type
                                 # crosses a light patch
C13_FRAME_TILES_X, C13_FRAME_TILES_Y = 8, 8   # ... and the whole frame, on the
                                 # pixel-only path, where 8x2 is far too coarse
C13_SOLID_INK_FRAC = 0.75        # a text box whose ink fraction is over this
                                 # is a solid plane drawn over the type, not
                                 # glyphs: measured, settled word boxes read
                                 # 0.30-0.42 and the same boxes under a wipe
                                 # read 0.87-1.00. Not measurable, so excluded
                                 # from the worst and from the share exactly as
                                 # a box below the ink floor already is.
C13_TILE_PERCENTILE = 10.0       # canon C13: the 10th percentile tile
C13_MIN_CORE_PX = 40             # core pixels needed before a frame is measured
C13_MIN_TILE_CORE_PX = 6
C13_MIN_TILE_BG_PX = 6
C13_MAX_SAMPLE_FRAMES = 400      # cap the RGB pull
C13_MIN_SAMPLES_PER_EL = 2       # ... but never stride a short card out
C13_APCA_LARGE_LC = 45.0         # advisory only; APCA is a WCAG 3 draft

# ---- C14 safe margins (weight 1, NOT a gate) ------------------------------
C14_TITLE_SAFE = 0.05            # SMPTE ST 2046-1 safe title area, 90 %
C14_ACTION_SAFE = 0.035          # SMPTE ST 2046-1 safe action area, 93 %
C14_WEB_SAFE = 0.04              # canon 3.3 "4-5 % for web and streaming"
C14_ACTION_DELIVERY = ("broadcast",)   # there is no overscan on web or social
C14_BREACH_PX = 40               # mask pixels at 640x360
C14_GROUND_PLANE_FRAC = 0.25     # a component this big is the ground plane
C14_MAX_FILL = 0.60              # a filled rectangle is a panel, not readable
C14_MIN_TRACK_FRAMES = 3         # canon C14: TRACKED components only.  A blob
                                 # that lives for one frame is grain or a
                                 # transition artefact, not an element sitting
                                 # in the margin
C14_A_TITLE_SHARE = 0.005
C14_B_TITLE_SHARE = 0.02
C14_B_ACTION_SHARE = 0.005
C14_B_OVERLAY_SHARE = 0.005
C14_SOCIAL_SAFE = {              # [x0, y0, x1, y1] as fractions of a 9:16 frame
    "tiktok": [0.0, 0.094, 1.0, 0.833],    # about 180 px top / 320 px bottom
    "reels": [0.0, 0.115, 1.0, 0.760],     # about 220 px top / 460 px bottom
}

# ---- C15 readability dwell -------------------------------------------------
C15_DISPLAY_MAX_WORDS = 5        # more words than this is body or caption text
# C15_LINE_HEIGHT_FACTOR is gone. Wrapping is counted from the probe line
# boxes (_is_wrapped); a box-height multiple of the font size fires on every
# masked word rise, which is the dominant construction in the medium.
C15_SLAM_CHARS = 12              # one or two words is a slam word
C15_SLAM_MIN_FRAMES = 8          # canon C15 C: under 8 frames absolute
C15_S_CPS, C15_A_CPS, C15_B_CPS = 13.0, 17.0, 20.0        # body model
C15_MIN_SETTLED_MS = 833.0       # Netflix 5/6 s minimum event duration
C15_C_SETTLED_MS = 500.0
C15_S_MSWORD = 300.0             # canon C15 S: display >= 300 ms per word
C15_A_MSWORD = 200.0
C15_B_MSWORD = 160.0
C15_C_MSWORD = 130.0             # canon C15 C: display < 130 ms per word
C15_RUN_GAP_FRAMES = 3           # frames at 30 fps. Two display cards this
                                 # close, in the same place on screen, are one
                                 # READING RUN: canon 3.1's replace-in-place
                                 # regime, "where the eye never moves". The
                                 # reading rate of a stream is the stream's, not
                                 # each fragment's, and pricing "can be a" alone
                                 # asks a sentence fragment to stand as a card
C15_RUN_CENTRE_FRAC = 0.25       # ... and "in the same place" is centres within
                                 # this fraction of the frame diagonal, so a
                                 # caption and a headline are never one run
C15_RUN_MIN_CARDS = 2            # a run is at least this many cards
C15_REPLACE_FLOOR_MS = 170.0     # canon 3.1's OTHER floor, and the one that
                                 # applies inside a run: "0.17 s (350 wpm RSVP)
                                 # is the floor for a strict REPLACE-IN-PLACE
                                 # stream, where the eye never moves." Canon
                                 # splits the beat regime in two and says to
                                 # DERIVE which one a card is in; the derivation
                                 # is the run this file already detects -- same
                                 # place, no gap, consecutive. The generic
                                 # 8-frame floor is the flash boundary for a
                                 # card that has to stand on its own, and a
                                 # fragment of a sentence the eye is already
                                 # fixated on is not that card. Applying the
                                 # 8-frame floor to it charged the middle word
                                 # of a three-card sentence, at one screen
                                 # position with no gap either side, as a card
                                 # too short to read.
C15_TEXTURE_MIN_WORDS = 6        # a card carrying at least this many words,
C15_TEXTURE_DISTINCT = 0.34      # of which this share or fewer are DISTINCT,
                                 # is a repeated-word texture rather than copy.
                                 # A full-bleed wall that tiles one word
                                 # twenty-nine times is read once and then
                                 # seen, and pricing it at twenty-nine words
                                 # made it the worst card in a finished film at
                                 # 9 ms per word. The reading unit is the
                                 # distinct set.
C15_SPLIT_CHARS = 1              # elements this short are LETTERS of one split
                                 # word, not words: an eleven-letter end card
                                 # built from eleven spans counted eleven words
                                 # and reported 42 ms per word on two finished
                                 # films.  Adjacent one-character elements are
                                 # concatenated before the card is tokenised.
C15_FLASH_EXEMPT = True          # canon 3.1: a card is a READ card if it
                                 # introduces a word not shown earlier in the
                                 # piece; everything else is beat or flash and
                                 # the reading floors do not apply to it.  The
                                 # regime is DERIVED from the copy, never
                                 # declared, because as a declaration it is an
                                 # attestation and a builder whose card fails
                                 # would relabel it.
C15_PIXEL_MAX_CONCURRENT = 1     # the pixel fallback only fires on a card that
                                 # is ALONE in frame, so a per-word stagger is
                                 # never read as a string of flashed cards

# ---- C16 palette adherence -------------------------------------------------
C16_BEAT_SAMPLE = 0.70           # one settled frame per beat, 70 % through
C16_MIN_SAMPLES = 12             # ... or this many even samples with no beats
C16_SAT_MIN = 0.25               # below this a pixel is neutral, not chromatic
C16_VAL_RANGE = (0.15, 1.00)     # the old 0.95 ceiling threw away every fully
                                 # bright brand accent, which is the commonest
                                 # thing a palette declares
C16_PALETTE_DE = 8.0             # canon C16: CIEDE2000 8 of a palette entry
C16_GROUND_DE = 10.0             # a beat ground further than this is off-palette
C16_S_ADHERENCE = 0.95           # canon C16 S
C16_A_ADHERENCE = 0.90
C16_C_ADHERENCE = 0.80           # canon C16 C
C16_MONO_CHROMA_FLOOR = 0.02     # below this share of chromatic pixels the piece
                                 # is monochrome, duotone-neutral or one-bit, and
                                 # chromatic adherence is measuring nothing.  It
                                 # is graded on NEUTRAL adherence instead: that
                                 # is a whole professional style family and the
                                 # old code scored all of it C by dividing zero
                                 # chromatic pixels by one.
C16_HUE_BINS = 24                # 15 degrees each, report line only
C16_BIN_COVERAGE = 0.01          # a hue bin counts at 1 % of the frame
C16_HUE_ROTATION = 60.0          # one element rotating its own hue this far is
                                 # rainbow cycling
C16_BANDING_MIN_STEP = 3         # code-value jump across a smooth gradient
C16_BANDING_MAX_STEP = 12        # above this it is an edge, not banding
C16_BANDING_RATE_MAX = 0.02      # share of sampled gradient steps that may band
C16_MAX_PIXELS_PER_FRAME = 20000 # subsample before the CIEDE2000 pass

# ---- C20 photosensitive flash (GATE, weight 0) ----------------------------
C20_LUM_STEP = 0.10              # WCAG general flash threshold
C20_DARK_MAX = 0.80              # ... where the darker of the pair is below this
C20_AREA_SHARE = 0.25            # over a significant portion of the central field
C20_CENTRE_FRAC = 0.50           # the central 10 degrees, as half width and height
C20_MAX_PER_SECOND = 3           # canon C20: <= 3 is S, > 3 is C and gates
C20_DISSOLVE_FRAMES = 4          # consecutive same-sign transitions no further
                                 # apart than this are one luminance CHANGE: a
                                 # dip to black spread over three frames is one
                                 # change, not three. The gap is measured to
                                 # the previous TRANSITION, not to the last
                                 # change kept, because measuring it to the
                                 # last kept change re-opens a new change every
                                 # five frames and turns one slow dissolve back
                                 # into a burst
C20_CHANGES_PER_FLASH = 2        # a flash is a PAIR of opposing changes (W3C SC
                                 # 2.3.1), so the standard's own calibration
                                 # point, a 3 Hz square wave, is six luminance
                                 # changes per second and exactly three flashes.
                                 # Counting each change as a flash makes the
                                 # gate fire at 1.5 Hz, twice as strict as the
                                 # standard, and it failed a real product film
                                 # on two hard cuts and a dissolve.
C20_FLASH_W, C20_FLASH_H = 320, 180

# ---- report plumbing -------------------------------------------------------
BAND_ORDER = ["S", "A", "B", "C"]
WEIGHTS = {"C12": 1, "C13": 0, "C14": 1, "C15": 1, "C16": 1, "C20": 0}
GATES = {"C13", "C20"}
CRITERIA_NAMES = {
    "C12": "type hierarchy", "C13": "contrast", "C14": "safe margins",
    "C15": "readability", "C16": "palette", "C20": "photosensitive flash",
}
BASIS = {
    "C12": "canon C12 and 3.3: declared type scale within 10 %, minSize 18 px "
           "at 1080p (32 body / 90 headline in-feed)",
    "C13": "canon C13 gate: settled window, local ground, 8x2 tiles, 10th "
           "percentile; WCAG 2.2 SC 1.4.3; APCA Lc advisory",
    "C14": "canon C14 and 3.3: SMPTE ST 2046-1 on broadcast only, 4 % edge on "
           "web, platform rectangles on social, tracked components only",
    "C15": "canon C15: Netflix timed text 5/6 s and 17-20 cps for body; RSVP "
           "200-300 ms per word for display",
    "C16": "canon C16: CIEDE2000 8 adherence to a declared palette, ground on "
           "palette, banding after encode; hue census is a report line",
    "C20": "canon C20 gate: W3C SC 2.3.1 general flash, three per second. The "
           "red-flash half of SC 2.3.1 is not measured",
}


# =============================================================================
# shared pure helpers.  Identical in behaviour to the ones in grade-mg.py; they
# are duplicated so this module imports with no dependency on a file four
# agents are editing concurrently.  The integrator may replace this block with
# imports once the modules are merged.
# =============================================================================

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def fscale(frames_at_30, fps):
    """Frame-count thresholds are quoted at the rubric's authoring rate of 30.
    A 60 fps render doubles every run length, so an 8-frame floor becomes 16."""
    return max(1, int(round(frames_at_30 * fps / 30.0)))


def band_worse(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return a if BAND_ORDER.index(a) >= BAND_ORDER.index(b) else b


def rank_worst(pairs, n=6):
    """Frames worst-first.  `pairs` is [(severity, frame)], higher is worse."""
    out, seen = [], set()
    for sev, f in sorted(pairs, key=lambda p: -float(p[0])):
        f = int(f)
        if f in seen:
            continue
        seen.add(f)
        out.append(f)
        if len(out) >= n:
            break
    return out


def rel_lum_rgb(c):
    s = np.asarray(c, dtype=float) / 255.0
    lin = np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)
    return float(lin @ np.array([0.2126, 0.7152, 0.0722]))


def wcag_ratio(rgb_a, rgb_b):
    la, lb = rel_lum_rgb(rgb_a), rel_lum_rgb(rgb_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def apca_lc(text_rgb, bg_rgb):
    """APCA-W3 lightness contrast, advisory only (WCAG 3 is a draft).  WCAG 2
    misjudges hue pairs -- orange on cream computes near 3:1 by construction --
    so the number is printed beside the ratio and never bands anything."""
    def ys(c):
        s = np.asarray(c, dtype=float) / 255.0
        y = float(np.array([0.2126729, 0.7151522, 0.0721750]) @ (s ** 2.4))
        return y + (0.022 - y) ** 1.414 if y < 0.022 else y
    yt, yb = ys(text_rgb), ys(bg_rgb)
    if yb > yt:
        sapc = (yb ** 0.56 - yt ** 0.57) * 1.14
        return 0.0 if sapc < 0.1 else (sapc - 0.027) * 100.0
    sapc = (yb ** 0.65 - yt ** 0.62) * 1.14
    return 0.0 if sapc > -0.1 else (sapc + 0.027) * 100.0


def rgb_to_hsv(arr):
    """arr is (..., 3) uint8 or float.  Returns h in degrees, s and v in 0..1."""
    a = np.asarray(arr, dtype=np.float32) / 255.0
    # a range decodes to (n, H, W, 3): reduce over the LAST axis, never axis 2
    mx = a.max(axis=-1)
    mn = a.min(axis=-1)
    d = mx - mn
    h = np.zeros_like(mx)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    nz = d > 1e-6
    m = nz & (mx == r)
    h[m] = ((g[m] - b[m]) / d[m]) % 6
    m = nz & (mx == g)
    h[m] = ((b[m] - r[m]) / d[m]) + 2
    m = nz & (mx == b)
    h[m] = ((r[m] - g[m]) / d[m]) + 4
    h = h * 60.0
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0.0)
    return h, s, mx


def srgb_to_lab(rgb):
    """rgb is (..., 3) 0..255.  Returns (..., 3) CIE Lab under D65."""
    s = np.asarray(rgb, dtype=np.float64) / 255.0
    lin = np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = lin @ m.T
    white = np.array([0.95047, 1.0, 1.08883])
    t = xyz / white
    d = 6.0 / 29.0
    ft = np.where(t > d ** 3, np.cbrt(np.maximum(t, 1e-12)),
                  t / (3 * d * d) + 4.0 / 29.0)
    L = 116.0 * ft[..., 1] - 16.0
    a = 500.0 * (ft[..., 0] - ft[..., 1])
    b = 200.0 * (ft[..., 1] - ft[..., 2])
    return np.stack([L, a, b], axis=-1)


def ciede2000(lab1, lab2):
    """lab1 is (..., 3), lab2 is (k, 3).  Returns (..., k) distances."""
    L1 = lab1[..., 0][..., None]
    a1 = lab1[..., 1][..., None]
    b1 = lab1[..., 2][..., None]
    L2, a2, b2 = lab2[:, 0], lab2[:, 1], lab2[:, 2]
    C1 = np.hypot(a1, b1)
    C2 = np.hypot(a2, b2)
    Cb = (C1 + C2) / 2.0
    G = 0.5 * (1 - np.sqrt(Cb ** 7 / (Cb ** 7 + 25.0 ** 7 + 1e-30)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360.0
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360.0
    dLp = L2 - L1
    dCp = C2p - C1p
    dh = h2p - h1p
    dh = np.where(dh > 180, dh - 360, np.where(dh < -180, dh + 360, dh))
    dHp = 2 * np.sqrt(np.maximum(C1p * C2p, 0.0)) * np.sin(np.radians(dh) / 2)
    Lbp = (L1 + L2) / 2.0
    Cbp = (C1p + C2p) / 2.0
    hsum = h1p + h2p
    hdiff = np.abs(h1p - h2p)
    hbp = np.where(hdiff > 180,
                   np.where(hsum < 360, (hsum + 360) / 2, (hsum - 360) / 2),
                   hsum / 2.0)
    T = (1 - 0.17 * np.cos(np.radians(hbp - 30))
         + 0.24 * np.cos(np.radians(2 * hbp))
         + 0.32 * np.cos(np.radians(3 * hbp + 6))
         - 0.20 * np.cos(np.radians(4 * hbp - 63)))
    dTh = 30 * np.exp(-(((hbp - 275) / 25.0) ** 2))
    Rc = 2 * np.sqrt(Cbp ** 7 / (Cbp ** 7 + 25.0 ** 7 + 1e-30))
    Sl = 1 + (0.015 * (Lbp - 50) ** 2) / np.sqrt(20 + (Lbp - 50) ** 2)
    Sc = 1 + 0.045 * Cbp
    Sh = 1 + 0.015 * Cbp * T
    Rt = -np.sin(np.radians(2 * dTh)) * Rc
    return np.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2
                   + Rt * (dCp / Sc) * (dHp / Sh))


def hex_to_rgb(h):
    h = str(h).strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return None
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except ValueError:
        return None


def _dilate3(m):
    """One-pixel 4-neighbour dilation.  Used to push the antialiased halo out of
    the background sample: a halo pixel is neither ground nor glyph, and
    averaging it into the ground pulls the ground toward the glyph and
    understates every contrast ratio on thin type."""
    out = m.copy()
    out[:-1, :] |= m[1:, :]
    out[1:, :] |= m[:-1, :]
    out[:, :-1] |= m[:, 1:]
    out[:, 1:] |= m[:, :-1]
    return out


# =============================================================================
# ctx plumbing
# =============================================================================

def _get(ctx, name, default=None):
    if isinstance(ctx, dict):
        return ctx.get(name, default)
    return getattr(ctx, name, default)


class _Env(object):
    """Everything the family reads, resolved once, with the defaults applied."""

    __slots__ = ("px", "src", "manifest", "cuts", "beats", "fps", "width",
                 "height", "delivery", "dec_w", "dec_h", "s1080")

    def __init__(self, ctx):
        self.px = _get(ctx, "px")
        if self.px is None:
            raise ValueError("crit_legibility: ctx.px is required")
        self.src = _get(ctx, "src")
        self.manifest = _get(ctx, "manifest") or {}
        self.cuts = sorted(int(c) for c in (_get(ctx, "cuts") or []))
        self.fps = float(_get(ctx, "fps") or getattr(self.px, "fps", 30.0))
        self.width = float(_get(ctx, "width") or getattr(self.px, "width", 1920))
        self.height = float(_get(ctx, "height") or getattr(self.px, "height", 1080))
        self.dec_h, self.dec_w = self.px.mask.shape[1], self.px.mask.shape[2]
        d = _get(ctx, "delivery") or self.manifest.get("delivery") or DEFAULT_DELIVERY
        self.delivery = d if d in DELIVERIES else DEFAULT_DELIVERY
        beats = _get(ctx, "beats")
        self.beats = list(beats) if beats else self._beats_from_cuts()
        # every type size in this family is quoted at 1080p, so the conversion
        # is computed once and never re-derived per criterion
        self.s1080 = REF_HEIGHT_1080 / (self.src.H if self.src is not None
                                        else self.height)

    def _beats_from_cuts(self):
        n = self.px.n
        if not self.cuts:
            return [(0, n - 1)] if n > 1 else []
        out = []
        for i, c in enumerate(self.cuts):
            e = self.cuts[i + 1] - 1 if i + 1 < len(self.cuts) else n - 1
            if e > c:
                out.append((int(c), int(min(e, n - 1))))
        return out


def _env(ctx):
    return _Env(ctx)


def _row(cid, measured, band, worst=None, note="", na=False, na_reason="",
         declarations=None):
    return {
        "id": cid,
        "name": CRITERIA_NAMES[cid],
        "band": None if na else band,
        "weight": WEIGHTS[cid],
        "gate": cid in GATES,
        "na": bool(na),
        "measured": measured,
        # arrives RANKED BY SEVERITY and is never re-sorted
        "worstFrames": [int(f) for f in dict.fromkeys(worst or []) if f is not None][:6],
        "basis": BASIS[cid],
        "note": (na_reason if na else note),
        "declarations": sorted(set(declarations or [])),
    }


def _declared(env, keys):
    """Which of `keys` the manifest actually carries, for the declaration
    budget.  A declaration is a claim about intent and has to be visible."""
    out = []
    for k in keys:
        v = env.manifest.get(k)
        if v is None or v is False or (isinstance(v, (list, dict, str)) and not v):
            continue
        out.append(k)
    return out


def _text_like_components(px, f, min_px=COMPONENT_MIN_PX, max_fill=C14_MAX_FILL,
                          max_h_frac=0.6):
    """Components on frame f that could be type: big enough to see, not a
    filled rectangle, not the ground plane.  A solid bar or a colour field
    fills its own box; a word does not.

    `max_fill=1.01, max_h_frac=1.0` turns it into "any non-ground content",
    which is what the action-safe test wants: action safe is about anything in
    the picture, not only about readable type."""
    out = []
    dec_h, dec_w = px.mask.shape[1], px.mask.shape[2]
    for c in px.comps[int(f)]:
        area, cx, cy, x0, y0, x1, y1 = c
        if area < min_px:
            continue
        w, h = (x1 - x0 + 1), (y1 - y0 + 1)
        if h < C12_PIXEL_MIN_H or h > dec_h * max_h_frac:
            continue
        if area >= C14_GROUND_PLANE_FRAC * dec_w * dec_h:
            continue
        if area / max(w * h, 1) > max_fill:
            continue
        out.append(c)
    return out


def _tracked_keys(px, min_frames=C14_MIN_TRACK_FRAMES):
    """frame -> set of component centroids that belong to a track living at
    least `min_frames` frames.  The centroids come straight out of px.comps
    and back out of px.tracks unchanged, so identity by value is exact."""
    keys = {}
    for tr in px.tracks:
        if len(tr["frames"]) < min_frames:
            continue
        for k, f in enumerate(tr["frames"]):
            keys.setdefault(int(f), set()).add((round(float(tr["cx"][k]), 4),
                                                round(float(tr["cy"][k]), 4)))
    return keys


# =============================================================================
# C12  type hierarchy
# =============================================================================
#
# WHAT IT MEASURES NOW
#   Every settled type size, clustered at 10 %, against a DECLARED type scale
#   (manifest `typeScale`, in composition px) to within 10 %; plus `minSize`
#   normalised to 1080p against the delivery's floor.
#
#   S  every settled size sits on the declared scale, and minSize is at or
#      above the floor (18 px at 1080p, or 32 px body with a 90 px headline for
#      social in-feed).
#   C  minSize below the floor.
#
#   Without a declared scale the best-fitting common ratio is reported as
#   ADVISORY and the band is capped at A: a ratio found by search is not the
#   author's scale, and S is a claim that every size sits where it was meant to.
#
# WHAT STILL SCORES C
#   A 1080p piece whose smallest settled text element sets 14 px, or a social
#   in-feed piece with 28 px body copy.  Both are below the floor, both are
#   unreadable in a feed, and no declaration relieves either: `typeScale` moves
#   the adherence half only.

def c12_type_hierarchy(ctx):
    env = _env(ctx)
    decl = _declared(env, ["typeScale", "delivery"])
    declared_scale = [float(x) for x in (env.manifest.get("typeScale") or [])]
    floor_body = C12_SOCIAL_BODY_PX if env.delivery == "social" else C12_MIN_PX
    floor_head = C12_SOCIAL_HEAD_PX if env.delivery == "social" else None

    if env.src is None:
        return _c12_pixel(env, floor_body, decl)

    src = env.src
    sizes = []            # (size in composition px, frame, key)
    for el in src.text_elements():
        win = src.settled_window(el, env.cuts)
        if not win:
            continue
        a, _b = win
        s = src.font_px(el, a)
        if s <= 0:
            continue
        sizes.append((float(s), int(a), src.elements[el]["key"]))
    if not sizes:
        return _row("C12", {"delivery": env.delivery}, None, na=True,
                    na_reason="no settled text elements", declarations=decl)

    uniq = []
    for s in sorted(x[0] for x in sizes):
        if not uniq or s > uniq[-1] * (1 + C12_SIZE_CLUSTER):
            uniq.append(s)
    exceptions, fitted = _scale_exceptions(uniq, declared_scale)

    fails = []
    for (s, f, key) in sizes:
        s1080 = s * env.s1080
        if s1080 < floor_body:
            fails.append((floor_body - s1080, f, key, s1080))
    biggest = max(x[0] for x in sizes) * env.s1080
    head_ok = floor_head is None or biggest >= floor_head

    if fails:
        band = "C"
    else:
        if exceptions == 0:
            band = "S" if declared_scale else "A"
        elif exceptions <= C12_A_EXCEPTIONS:
            band = "A"
        else:
            band = "B"
        if not head_ok:
            band = band_worse(band, "A")

    note = ""
    if fails:
        fails.sort(key=lambda t: -t[0])
        note = (f"{fails[0][2]} sets {fails[0][3]:.0f} px at 1080p, under the "
                f"{floor_body:.0f} px floor for {env.delivery} delivery")
    elif not head_ok:
        note = (f"largest settled type is {biggest:.0f} px at 1080p; in-feed "
                f"headline type wants {floor_head:.0f} px")
    elif exceptions and declared_scale:
        note = f"{exceptions} settled size(s) sit off the declared type scale"
    elif exceptions:
        note = (f"{exceptions} settled size(s) sit off the best-fitting "
                f"{fitted:.3g} ratio; declare typeScale to grade adherence")
    elif not declared_scale:
        note = ("no typeScale declared: sizes fit a "
                + (f"{fitted:.3g}" if fitted else "single-size")
                + " series, reported as advisory, so the band is capped at A")

    return _row("C12", {
        "nSizes": len(uniq),
        "minSize1080": round(min(x[0] for x in sizes) * env.s1080, 1),
        "maxSize1080": round(biggest, 1),
        "offScale": exceptions,
        "scaleRatio": (None if fitted is None else round(fitted, 3)),
        "scaleDeclared": bool(declared_scale),
        "delivery": env.delivery,
    }, band, rank_worst([(t[0], t[1]) for t in fails]), note, declarations=decl)


def _c12_pixel(env, floor_body, decl):
    """No source channel: measure CAP HEIGHT off tracked word-shaped components
    and convert with the low end of the cap/em range, so the reported size is
    the largest plausible one and a C is a size that fails even on the generous
    read.  Scale adherence is not measurable this way, so the band is capped
    at B."""
    px = env.px
    caps = []
    probe = [int(clamp(a + 0.5 * (b - a), 0, px.n - 1)) for (a, b) in env.beats]
    if not probe:
        probe = list(range(0, px.n, max(1, px.n // 20)))
    for f in probe:
        for (area, cx, cy, x0, y0, x1, y1) in _text_like_components(px, f):
            w, h = (x1 - x0 + 1), (y1 - y0 + 1)
            if w < C12_PIXEL_MIN_ASPECT * h:
                continue                  # a glyph or a bullet, not a word
            caps.append((h, f))
    if not caps:
        return _row("C12", {"delivery": env.delivery, "basis": "pixel"}, None,
                    na=True,
                    na_reason="no word-shaped components on the pixel channel: "
                              "there is no type here to hold to a size floor",
                    declarations=decl)
    scale = REF_HEIGHT_1080 / env.dec_h
    cap_h, cap_f = min(caps, key=lambda t: t[0])
    est = cap_h * scale / C12_CAP_TO_EM_MIN
    band = "C" if est < floor_body else "B"
    note = ("reduced confidence: sizes estimated from component cap heights, so "
            "scale adherence is not measurable and the band is capped at B")
    if band == "C":
        note = (f"smallest word-shaped component is {cap_h * scale:.0f} px of cap "
                f"height at 1080p, at most {est:.0f} px of type, under the "
                f"{floor_body:.0f} px floor; " + note)
    return _row("C12", {"minCap1080": round(cap_h * scale, 1),
                        "minSizeEst1080": round(est, 1),
                        "delivery": env.delivery, "basis": "pixel"},
                band, [cap_f], note, declarations=decl)


def _scale_exceptions(uniq, declared):
    """How many settled sizes sit off a ratio series.  A declared scale wins;
    otherwise the best-fitting common ratio is found and returned so it can be
    reported as advisory."""
    if declared:
        bad = sum(1 for s in uniq
                  if not any(abs(s - d) <= C12_SCALE_TOL * d for d in declared))
        return bad, None
    if len(uniq) <= 1:
        return 0, None
    best = (len(uniq), None)
    for r in C12_SCALE_RATIOS:
        for base in uniq:
            steps = [base * (r ** k) for k in range(-8, 9)]
            bad = sum(1 for s in uniq
                      if not any(abs(s - t) <= C12_SCALE_TOL * t for t in steps))
            if bad < best[0]:
                best = (bad, r)
    return best


# =============================================================================
# C13  contrast   (GATE, weight 0)
# =============================================================================
#
# WHAT IT MEASURES NOW
#   The CARD's settled window only, and inside it only the frames whose
#   rendered ink strength sits at the element's own plateau.  For every sampled
#   frame: a LOCAL ground (the median of the element's expanded box, the ring
#   when the glyph fills it), a foreground of the glyph BODY (everything at
#   least half as far from the ground as the 95th percentile of ink deviation),
#   and a background of everything outside a DILATED ink mask so the
#   antialiased halo is in neither sample.  The box is TILED 8 x 2 and the
#   tiles vary only the BACKGROUND, because the type has one colour and what
#   canon's 10th percentile is looking for is the patch where the GROUND is
#   worst.  APCA Lc is computed on the same pair and reported as advisory; it
#   bands nothing, because WCAG 3 is a draft, but the note says when the two
#   models disagree about a hue pair, which is the case canon warns about.
#
#   Three kinds of sample are NOT MEASURABLE and are excluded from both the
#   worst and the share, and counted in the row: a box with no ink against its
#   own local ground, a box covered by a solid (a wipe or a panel on top of it),
#   and a box under eight decode pixels in either visible dimension.  Scoring
#   those 1.00:1 fired the gate on three finished films.  What IS separable and
#   is reported: an element carrying no ink across its ENTIRE window never
#   rendered, which caps the band at B.
#
#   The ink floor is |luma - local ground| > 28, which reaches down to about
#   1.2:1, so type low enough in contrast to fail this criterion still
#   registers as ink and is still measured.  Below 1.2:1 the row says so.
#
#   `decorativeType` names accent or incidental type not carrying required
#   information (the WCAG 1.4.3 carve-out), excluded and counted.  It is capped
#   at a quarter of the settled text elements: past that the declaration is
#   ignored, because an exemption list covering most of the type is not an
#   exemption, it is a rewrite of the criterion.
#
#   S  worst >= 4.5:1, and no small type below 4.5:1
#   A  worst >= 3.0:1, and no small type below 4.5:1
#   B  neither, but not C
#   C  worst < 2.5:1, OR fewer than 95 % of settled frames at or above 3:1
#
#   The share test is what stops one dissolve frame failing a whole film, and
#   the WCAG small-text rule deliberately cannot fire the gate on its own:
#   4.42 against a 4.5 floor is decoder noise, and this criterion caps the
#   whole grade at C.
#
#   Weight 0.  A legibility problem already caps the overall grade; weighting
#   it as well would double-penalise the same defect and destroy W as a craft
#   signal.
#
# WHAT STILL SCORES C
#   White #FFFFFF type settled on a #BFBFBF panel is 1.67:1 on every tile of
#   every settled frame: worst below 2.5, share zero, gate failed.  So is a
#   film that is fine everywhere except one card where the headline sits on a
#   photograph and 8 % of its settled frames fall under 3:1.  Measured on the
#   real samples: a gold #D39745 end-card headline on white lands at 2.45:1 and
#   fails the gate, and a product film whose chip labels sit at 2.6 to 3.0:1
#   fails the 95 % share test at 0.92.  `decorativeType` is the only relief and
#   it is capped and counted.

def c13_contrast(ctx):
    env = _env(ctx)
    px, src = env.px, env.src
    decl = _declared(env, ["delivery", "decorativeType"])
    # `fullBleed` is a SAFE-MARGIN declaration and no longer relieves anything
    # here. A margin claim was buying a legibility gate: one boxless window
    # over a card whose type is fully legible on black exempted every settled
    # element behind it, and deleting that single entry moved a finished film
    # from B to C with the gate failed. The occlusion case it was written for
    # is real, and it is measured rather than declared -- _tiles already returns
    # "covered" for a box a solid sits on top of -- while the decorative tile
    # field it was actually being used for is what `decorativeType` is, which is
    # per element and capped.
    exempt = set()

    windows = []           # (el or None, [eligible frames], size1080)
    n_text = n_decorative = 0
    if src is not None:
        decorative = set(env.manifest.get("decorativeType") or [])
        all_text = src.text_elements()
        n_text = len(all_text)
        named = [el for el in all_text
                 if decorative and _named_subtree(src, el, decorative)]
        card_win = _card_windows(src, env)
        # The cap is on CARDS, not on elements. A texture field is made of many
        # small spans by construction -- a word wall of 28 tiles at three glyph
        # spans each is 84 of a film's 150 text elements and blew a 25 %
        # element cap on its own -- while it is ONE card of that film's
        # twenty-seven. Counting cards is what the share was reaching for, and
        # it is the unit C13 and C15 already agree on.
        cards_all = {_group_key(src, env, el, card_win.get(el, (0, 0))[0])
                     for el in all_text}
        cards_dec = {_group_key(src, env, el, card_win.get(el, (0, 0))[0])
                     for el in named}
        if len(cards_dec) > C13_DECORATIVE_MAX_SHARE * max(len(cards_all), 1):
            named = []
        # ... and a card whose type is ALL decorative has nothing left to read,
        # so the claim is false there and is refused card by card. This is the
        # WCAG 1.4.3 incidental carve-out read literally: text is incidental
        # when it is not the information, which means there has to be some
        # information beside it.
        by_card = {}
        for el in all_text:
            by_card.setdefault(
                _group_key(src, env, el, card_win.get(el, (0, 0))[0]), []).append(el)
        skip = set()
        for el in named:
            k = _group_key(src, env, el, card_win.get(el, (0, 0))[0])
            if any(e not in named for e in by_card.get(k, [])):
                skip.add(el)
        n_decorative = len(skip)
        for el in all_text:
            if el in skip or el not in card_win:
                continue
            a, b = card_win[el]
            frames = _c13_settled_frames(px, src, env, el, a, b, exempt)
            if not frames:
                continue
            windows.append((el, frames, src.font_px(el, a) * env.s1080))
    else:
        probe = [int(clamp(a + 0.5 * (b - a), 0, px.n - 1)) for (a, b) in env.beats]
        if not probe:
            probe = list(range(0, px.n, max(1, px.n // 20)))
        if sum(1 for f in probe if _text_like_components(px, f)) < max(1, len(probe) // 5):
            return _row("C13", {"basis": "pixel"}, None, na=True,
                        na_reason="no text-like components on the pixel channel: "
                                  "there is nothing here held to a type-contrast "
                                  "standard", declarations=decl)
        for (a, b) in env.beats:
            # the middle of a content run is the settled part of it
            lo = int(a + 0.35 * (b - a))
            hi = int(a + 0.70 * (b - a))
            frames = [f for f in range(lo, hi + 1) if f not in exempt]
            if frames:
                windows.append((None, frames, 999.0))
    if not windows:
        return _row("C13", {}, None, na=True,
                    na_reason="no settled text windows", declarations=decl)

    samples = _allocate_samples(windows, C13_MAX_SAMPLE_FRAMES,
                                C13_MIN_SAMPLES_PER_EL)
    rgb = px.rgb([s[0] for s in samples])

    worst, worst_f, worst_lc = 1e9, None, None
    small_fail = None
    ok_w, tot_w = 0.0, 0.0
    per_frame = []
    measured_frames = 0
    no_ink = 0
    seen_el, inked_el = {}, {}
    by_el = {}
    hold_floor = fscale(C13_HOLD_FLOOR_FRAMES, env.fps)
    held = {el: len(frames) >= hold_floor for (el, frames, _s) in windows}
    for (f, el, size1080, weight) in samples:
        img = rgb.get(int(f))
        if img is None:
            continue
        ratio, lc, how = (_tile_ratio_box(px, src, env, img, f, el)
                          if (src is not None and el is not None)
                          else _tile_ratio_frame(px, img, f))
        seen_el[el] = seen_el.get(el, 0) + 1
        if ratio is None:
            # occluded, or below the ink floor: not measurable, and excluded
            # from both the worst and the share rather than scored as 1.00:1
            no_ink += 1
            continue
        inked_el[el] = inked_el.get(el, 0) + 1
        measured_frames += 1
        by_el.setdefault(el, []).append((ratio, lc, int(f), size1080))
        if not held.get(el, True):
            continue
        tot_w += weight
        if ratio >= C13_A_RATIO:
            ok_w += weight
        per_frame.append((ratio, int(f)))
    # The element, not the sampled frame, is the unit that carries a contrast:
    # its ratio is the C13_FRAME_PERCENTILE of its own settled frames, so one
    # encode transient on one frame cannot fail a gate, and an element that is
    # low-contrast for its whole life still reports exactly what it is.
    flash_worst = None
    for el, rows in by_el.items():
        vals = [r[0] for r in rows]
        v = float(np.percentile(vals, C13_FRAME_PERCENTILE))
        k = min(range(len(rows)), key=lambda i: abs(rows[i][0] - v))
        ratio, lc, f, size1080 = rows[k]
        ratio = v
        if not held.get(el, True):
            if flash_worst is None or ratio < flash_worst[0]:
                flash_worst = (ratio, f, el)
            continue
        if size1080 < C13_SMALL_TEXT_PX and ratio < C13_SMALL_TEXT_RATIO:
            if small_fail is None or ratio < small_fail[1]:
                small_fail = (int(f), ratio, size1080)
        if ratio < worst:
            worst, worst_f, worst_lc = ratio, int(f), lc
    n_flash = sum(1 for el in by_el if not held.get(el, True))
    if worst >= 1e9 and flash_worst is not None:
        # nothing is held long enough to be graded: fall back to grading them
        # all rather than reporting no contrast at all
        for el, rows in by_el.items():
            vals = [r[0] for r in rows]
            v = float(np.percentile(vals, C13_FRAME_PERCENTILE))
            if v < worst:
                k = min(range(len(rows)), key=lambda i: abs(rows[i][0] - v))
                worst, worst_lc, worst_f = v, rows[k][1], rows[k][2]
            tot_w += len(rows)
            ok_w += sum(1 for x in vals if x >= C13_A_RATIO)
            per_frame.extend((x, rows[i][2]) for i, x in enumerate(vals))
        n_flash = 0
    unrendered = sum(1 for el, n in seen_el.items()
                     if n >= C13_MIN_SAMPLES_PER_EL and inked_el.get(el, 0) == 0)
    if measured_frames == 0:
        return _row("C13", {"noInkFrames": no_ink}, None, na=True,
                    na_reason="no settled text box carried ink against its own local "
                              "ground: the type is occluded, or below the "
                              "|luma - ground| > 28 ink floor everywhere",
                    declarations=decl)

    share = ok_w / max(tot_w, 1e-9)
    small_ok = small_fail is None
    if worst < C13_C_RATIO or share < C13_SHARE_FLOOR:
        band = "C"
    elif worst >= C13_S_RATIO and small_ok:
        band = "S"
    elif worst >= C13_A_RATIO and small_ok:
        band = "A"
    else:
        band = "B"
    if unrendered:
        band = band_worse(band, "B")

    note = ""
    worst_pairs = [(-r, f) for (r, f) in per_frame]
    if worst < C13_C_RATIO:
        note = (f"worst settled tile {worst:.2f}:1 at f{worst_f}, under the "
                f"{C13_C_RATIO:.1f}:1 gate (APCA Lc {worst_lc:.0f}, advisory)")
    elif share < C13_SHARE_FLOOR:
        note = (f"only {share:.0%} of settled frames reach {C13_A_RATIO:.0f}:1, "
                f"under the {C13_SHARE_FLOOR:.0%} gate")
    elif small_fail:
        note = (f"small type ({small_fail[2]:.0f} px at 1080p) at "
                f"{small_fail[1]:.2f}:1 on f{small_fail[0]}, WCAG wants "
                f"{C13_SMALL_TEXT_RATIO}; a gate is not fired on this alone")
        worst_pairs = [(1e9, small_fail[0])] + worst_pairs
    elif worst < C13_S_RATIO:
        note = (f"worst settled tile {worst:.2f}:1 at f{worst_f} "
                f"(APCA Lc {worst_lc:.0f}, advisory)")
    if worst_lc is not None and worst < C13_A_RATIO and worst_lc >= C13_APCA_LARGE_LC:
        # canon: WCAG 2 misjudges hue pairs, and APCA is where that shows.
        # Advisory in both directions: it never changes the band, it tells the
        # reader the two models disagree about this particular colour pair.
        note = (note + "; " if note else "") + \
            (f"APCA puts the same pair at Lc {worst_lc:.0f}, over its "
             f"{C13_APCA_LARGE_LC:.0f} large-text floor: the two models "
             f"disagree on this hue pair")
    if unrendered:
        note = (note + "; " if note else "") + \
            (f"{unrendered} settled text element(s) carry no ink anywhere in their "
             f"own window: occluded, or never rendered")
    elif no_ink:
        note = (note + "; " if note else "") + \
            (f"{no_ink} sampled frames excluded as not measurable: the box carries "
             f"no ink against its own local ground")
    if n_decorative:
        note = (note + "; " if note else "") + \
            (f"{n_decorative} of {n_text} text element(s) declared decorative and "
             f"excluded")
    if n_flash:
        note = (note + "; " if note else "") + \
            (f"report only: {n_flash} element(s) settle for under {hold_floor} "
             f"frames and are not gated on colour"
             + (f", worst {flash_worst[0]:.2f}:1 at f{flash_worst[1]}"
                if flash_worst else ""))
    if src is None:
        note = (note + "; " if note else "") + \
            ("reduced confidence: measured whole-frame on an 8x8 grid, so one "
             "low-contrast word is averaged in with the type around it")

    return _row("C13", {
        "worstRatio": round(worst, 2),
        "shareAbove3": round(share, 3),
        "apcaLc": (None if worst_lc is None else round(worst_lc)),
        "framesMeasured": measured_frames,
        "noInkFrames": no_ink,
        "unrenderedElements": unrendered,
        "decorativeExempt": n_decorative,
        "flashElements": n_flash,
        "basis": ("pixel whole-frame" if src is None
                  else f"source, {C13_TILES_X}x{C13_TILES_Y} tiles, p10"),
    }, band, rank_worst(worst_pairs), note, declarations=decl)


def _allocate_samples(windows, budget, floor):
    """Spread a fixed RGB-decode budget over the settled windows so every text
    element is probed, while the share statistic stays FRAMES-weighted.  A flat
    stride over the concatenated frame list gave all of its samples to whichever
    card sat on screen longest, and a two-second card with a legibility fault
    could be strided out entirely.

    `windows` is [(el, [eligible frames], size1080)]."""
    total = sum(max(1, len(fr)) for (_e, fr, _s) in windows)
    out = []
    for (el, frames, size1080) in windows:
        length = max(1, len(frames))
        k = int(round(budget * length / max(total, 1)))
        k = int(clamp(k, min(floor, length), length))
        if k <= 0:
            continue
        idx = np.unique(np.linspace(0, length - 1, k).round().astype(int))
        weight = length / float(len(idx))
        for i in idx:
            out.append((int(frames[int(i)]), el, size1080, weight))
    return out


def _group_key(src, env, el, a):
    """Which CARD an element belongs to: its clip when the composition has
    clips, otherwise the cut interval its settle frame lands in.  C13 and C15
    both need it, and they must agree, or the two rows describe different
    films."""
    clip_of = getattr(src, "clip_of", None)
    if callable(clip_of):
        c = clip_of(el)
        if isinstance(c, dict):
            return ("clip", c.get("id"))
    prior = [x for x in env.cuts if x <= a]
    return ("cut", prior[-1] if prior else 0)


def _card_windows(src, env):
    """{el: (a, b)} narrowed to the window in which the whole CARD is settled.

    A per-letter cascade gives every letter its own settled window, and the
    early letters' windows open while the rest of the line is still arriving.
    Measuring contrast there measures a letter mid-reveal: two finished films
    reported their worst settled contrast on the first letter of an end card,
    at 2.48:1 and 1.93:1, on frames where that letter was still fading up.
    Legibility is a property of the card, so the window is the card's."""
    own, groups = {}, {}
    for el in src.text_elements():
        win = src.settled_window(el, env.cuts)
        if not win:
            continue
        a, b = int(win[0]), int(win[1])
        own[el] = (a, b)
        groups.setdefault(_group_key(src, env, el, a), []).append(el)
    out = {}
    for _k, els in groups.items():
        a_int = max(own[e][0] for e in els)
        b_int = min(own[e][1] for e in els)
        for e in els:
            a, b = own[e]
            if len(els) > 1 and b_int >= a_int and b_int >= a and a_int <= b:
                out[e] = (max(a, a_int), min(b, b_int))
            else:
                # the card's elements never coexist: a replace-in-place stream,
                # where each element IS its own card
                out[e] = (a, b)
    return out


def _named_subtree(src, el, names):
    """Does a declaration name this element, an ANCESTOR of it, or its class.

    A declaration is a claim about intent and an author writes it about the
    thing they authored. A decorative tile field is authored as one container
    with a generated subtree: naming `#big-wall` has to reach the 84 glyph
    spans inside it or the declaration cannot be written at all, and naming
    eighty-four generated spans one at a time is not a claim anybody can check.

    Containment is read off the probe's own selector key -- a tile glyph's key
    is `#big-wall>span:nth-of-type(1)>span:nth-of-type(1)` -- rather than off
    the parent index, which points at the nearest TRACKED ancestor and skips
    untweened containers. Classes are accepted in the same spirit (`.bhl`), and
    both are still names.
    """
    if not names:
        return False
    if src.is_named(el, names):
        return True
    e = src.elements[el]
    key = str(e.get("key") or "")
    cls = set((e.get("cls") or "").split())
    for raw in names:
        n = str(raw)
        if n.startswith("."):
            if n[1:] in cls:
                return True
            continue
        if not n.startswith("#"):
            n = "#" + n
        if key == n or key.startswith(n + ">") or key.startswith(n + " "):
            return True
    return False


def _bleed_frames(env):
    """Frames a declared whole-frame fullBleed window covers.  A wipe that
    fills the frame edge to edge sits ON TOP of every settled text element
    behind it, so measuring those elements measures the wipe.  The same
    declaration C14 uses for the same reason, read the same way."""
    out = set()
    for w in (env.manifest.get("fullBleed") or []):
        if w.get("box"):
            continue
        a = int(w.get("from", 0))
        b = int(w.get("to", env.px.n - 1))
        out.update(range(max(a, 0), min(b, env.px.n - 1) + 1))
    return out


def _c13_settled_frames(px, src, env, el, a, b, exempt):
    """The frames inside an element's settled window on which its type is
    actually FULLY RENDERED, measured on the channel that renders it.

    `settled_window` tests the element's OWN opacity, so a fade applied to a
    parent or a per-letter cascade driven from a container leaves the arrival
    inside the window: three finished films had letters measured at 1.3:1
    partway through their own fade-in.  The box's mean deviation from the
    frame ground rises through an arrival and falls through an exit, so the
    plateau of that series is the part that is settled."""
    a = int(clamp(a, 0, px.n - 1))
    b = int(clamp(b, a, px.n - 1))
    sx, sy = env.dec_w / src.W, env.dec_h / src.H
    # exempt frames are dropped BEFORE the peak is taken: a full-frame wipe
    # covering the box reads as maximum deviation from ground, and using that
    # as the peak trimmed away every genuinely settled frame behind it
    live = [f for f in range(a, b + 1) if f not in exempt]
    if not live:
        return []
    strength = []
    for f in live:
        x0, y0, x1, y1 = src.box_at(el, f)
        bx0 = int(clamp(math.floor(x0 * sx), 0, env.dec_w - 1))
        bx1 = int(clamp(math.ceil(x1 * sx), bx0 + 1, env.dec_w))
        by0 = int(clamp(math.floor(y0 * sy), 0, env.dec_h - 1))
        by1 = int(clamp(math.ceil(y1 * sy), by0 + 1, env.dec_h))
        g = px.grey[f, by0:by1, bx0:bx1].astype(np.float32)
        strength.append(float(np.abs(g - float(px.ground[f])).mean()))
    if not strength:
        return []
    ref = float(np.percentile(strength, C13_SETTLE_REF_PCTL))
    if ref <= 0:
        return []
    lo, hi = C13_SETTLE_FRAC * ref, C13_SETTLE_MAX_MULT * ref
    return [live[i] for i, s in enumerate(strength) if lo <= s <= hi]


def _tile_ratio_box(px, src, env, img, f, el):
    """The tiled 10th-percentile ratio for one element on one frame, against a
    LOCAL ground taken from the ring around its box."""
    x0, y0, x1, y1 = src.box_at(el, f)
    sx, sy = env.dec_w / src.W, env.dec_h / src.H
    bx0, by0 = x0 * sx, y0 * sy
    bx1, by1 = x1 * sx, y1 * sy
    ex = max(C13_RING_MIN_PX, C13_BOX_EXPAND * (bx1 - bx0))
    ey = max(C13_RING_MIN_PX, C13_BOX_EXPAND * (by1 - by0))
    X0 = int(clamp(math.floor(bx0 - ex), 0, env.dec_w - 2))
    X1 = int(clamp(math.ceil(bx1 + ex), X0 + 2, env.dec_w))
    Y0 = int(clamp(math.floor(by0 - ey), 0, env.dec_h - 2))
    Y1 = int(clamp(math.ceil(by1 + ey), Y0 + 2, env.dec_h))
    # the guard is on the VISIBLE extent: an element half off the top of the
    # frame has a tall box and three rows of pixels on screen
    vw = clamp(bx1, 0.0, float(env.dec_w)) - clamp(bx0, 0.0, float(env.dec_w))
    vh = clamp(by1, 0.0, float(env.dec_h)) - clamp(by0, 0.0, float(env.dec_h))
    if vw < C13_MIN_BOX_PX or vh < C13_MIN_BOX_PX:
        return None, None, "toosmall"
    # OCCLUDED. Type has counters, sidebearings and leading, so a text box is
    # never ink from edge to edge: measured across the corpus a settled word
    # box reads 0.30 to 0.42 ink and the same box under a full-frame wipe reads
    # 0.87 to 1.00. A box that is solid ink is a plane drawn OVER the type, and
    # the ratio computed there is the wipe's own colour against itself -- APCA
    # Lc 0 -- attributed to a headline that is not on screen. Two frames of a
    # 95x wipe dot decided the contrast gate on two finished films.
    ibx0 = int(clamp(math.floor(bx0), 0, env.dec_w - 1))
    ibx1 = int(clamp(math.ceil(bx1), ibx0 + 1, env.dec_w))
    iby0 = int(clamp(math.floor(by0), 0, env.dec_h - 1))
    iby1 = int(clamp(math.ceil(by1), iby0 + 1, env.dec_h))
    if float(px.mask[int(f), iby0:iby1, ibx0:ibx1].mean()) > C13_SOLID_INK_FRAC:
        return None, None, "occluded"
    g = px.grey[int(f), Y0:Y1, X0:X1].astype(np.float32)
    sub = img[Y0:Y1, X0:X1]

    ring = np.ones(g.shape, dtype=bool)
    ix0 = int(clamp(math.floor(bx0) - X0, 0, g.shape[1]))
    ix1 = int(clamp(math.ceil(bx1) - X0, 0, g.shape[1]))
    iy0 = int(clamp(math.floor(by0) - Y0, 0, g.shape[0]))
    iy1 = int(clamp(math.ceil(by1) - Y0, 0, g.shape[0]))
    ring[iy0:iy1, ix0:ix1] = False
    have_ring = int(ring.sum()) >= C13_MIN_RING_PX

    # The local ground is the MEDIAN of the expanded box: ground is the
    # majority of any type box, which is the same reasoning that makes the
    # frame median the global ground.  The ring is the fallback for the one
    # case the median gets wrong, a box the glyph fills more than half of.
    ground = float(np.median(g))
    d = np.abs(g - ground)
    if float((d > INK_DELTA).mean()) > C13_GROUND_INK_MAX and have_ring:
        ground = float(np.median(g[ring]))
        d = np.abs(g - ground)

    # A pill, badge or chip has a plane of its own, and the corners of its
    # bounding box show the page THROUGH it.  Those corners are further from
    # the local ground than the glyphs are, so they were being read as the
    # foreground and the row reported the badge's contrast against the page
    # instead of the label's contrast against the badge.  Drop whatever matches
    # the surrounding page when the page is a different plane from the ground.
    keep = None
    if have_ring:
        page = float(np.median(g[ring]))
        page_mask = np.abs(g - page) <= C13_PLANE_TOL
        # Only when the page shows through the CORNERS, which is the case this
        # exists for.  If the page plane is most of the box then the box median
        # picked the element itself as its ground, and dropping the page would
        # drop the actual ground and leave nothing.
        if abs(page - ground) >= C13_PLANE_SEP \
                and float(page_mask.mean()) < C13_GROUND_INK_MAX:
            keep = ~_dilate3(_dilate3(page_mask))
            if int(keep.sum()) < C13_MIN_CORE_PX * 2:
                keep = None
    return _tiles(sub, d, C13_TILES_X, C13_TILES_Y, keep)


def _tile_ratio_frame(px, img, f):
    """The pixel-only path: the whole frame on a finer grid, against the frame's
    own median ground."""
    f = int(f)
    d = np.abs(px.grey[f].astype(np.float32) - float(px.ground[f]))
    return _tiles(img, d, C13_FRAME_TILES_X, C13_FRAME_TILES_Y)


def _tiles(img, d, nx, ny, keep=None):
    """(ratio, apcaLc, basis) for one region.  `d` is |luma - local ground|,
    and `keep` optionally masks the region down to the plane the type sits on.

    The foreground is the glyph BODY, taken as the top slice of ink deviation
    rather than as a fixed number of levels from the ground: a fixed core
    threshold cannot see low-contrast type at all, so the criterion went N/A on
    exactly the input it exists to fail.  The background excludes a dilated ink
    mask, because an antialiased halo pixel is neither ground nor glyph and
    averaging it into the ground understates every ratio on thin type."""
    ink = d > INK_DELTA
    if keep is not None:
        ink = ink & keep
    n_ink = int(ink.sum())
    n_region = int(keep.sum()) if keep is not None else int(ink.size)
    if n_ink < C13_MIN_CORE_PX:
        return None, None, "noink"
    if n_ink > C13_MAX_INK_FILL * max(n_region, 1):
        # the box is covered by a solid: a wipe, a panel or a card on top of it
        return None, None, "covered"
    far = float(np.percentile(d[ink], C13_CORE_TOP_PCTL))
    core = (d >= max(C13_CORE_OF_MAX * far, float(INK_DELTA)))
    if keep is not None:
        core = core & keep
    if int(core.sum()) < C13_MIN_TILE_CORE_PX:
        core = ink
    bg_ok = ~_dilate3(ink)
    if keep is not None:
        bg_ok = bg_ok & keep
    if int(bg_ok.sum()) < C13_MIN_TILE_BG_PX:
        return None, None, "noink"

    # The FOREGROUND is measured once over the whole glyph body.  The type has
    # one colour; what varies across an element's box is the GROUND, and
    # finding the patch where the ground is worst is the entire reason canon
    # asks for tiles and a 10th percentile.  Measuring both ends per tile makes
    # each tile a different, tiny, two-mode sample, and the resulting number
    # moved by half a stop on unrelated changes.
    fg = img[core].mean(axis=0)
    H, W = core.shape
    nx = int(clamp(W // C13_MIN_TILE_PX, 1, nx))
    ny = int(clamp(H // C13_MIN_TILE_PX, 1, ny))
    ratios, lcs = [], []
    for ty in range(ny):
        y0, y1 = ty * H // ny, (ty + 1) * H // ny
        for tx in range(nx):
            x0, x1 = tx * W // nx, (tx + 1) * W // nx
            tb = bg_ok[y0:y1, x0:x1]
            if int(tb.sum()) < C13_MIN_TILE_BG_PX:
                continue
            bg = img[y0:y1, x0:x1][tb].mean(axis=0)
            ratios.append(wcag_ratio(fg, bg))
            lcs.append(abs(apca_lc(fg, bg)))
    if not ratios:
        bg = img[bg_ok].mean(axis=0)
        return float(wcag_ratio(fg, bg)), float(abs(apca_lc(fg, bg))), "whole"
    return (float(np.percentile(ratios, C13_TILE_PERCENTILE)),
            float(np.percentile(lcs, C13_TILE_PERCENTILE)), "tiled")


# =============================================================================
# C14  safe margins   (weight 1, NOT a gate)
# =============================================================================
#
# WHAT IT MEASURES NOW
#   Delivery-aware, and no longer a gate.  Canon removed the gate because it
#   gated out every web-only deliverable and every deliberately cropped
#   full-bleed treatment.
#
#     broadcast  93 % action safe on non-ground TRACKED components, and 90 %
#                title safe on settled type
#     web        the 4 % edge check canon section 3.3 endorses, on settled type
#     social     the same 4 % edge, plus the declared platform rectangles
#                (Reels about 220 px top / 460 px bottom, TikTok about 180/320)
#
#   The ink test is restricted to TRACKED components: a component that lives
#   fewer than three frames is grain or a transition artefact, and a
#   ground-plane-sized or box-filling component is a panel, not readable
#   content.  `croppedType` exempts display type cropped on purpose, by element
#   name.  `fullBleed` exempts a frame window, or a box inside it.
#
#   S  no breach of any kind for the declared delivery
#   C  breaches past the B band
#
# WHAT STILL SCORES C
#   A 1080p web piece whose headline sits 20 px from the frame edge for three
#   seconds: at 30 fps that is 90 frames of a 780-frame film, a title-safe
#   share of 0.115 against the 0.02 B ceiling.  Declaring `delivery:
#   "broadcast"` makes it worse, not better, because action safe then applies
#   as well.

def c14_safe_margins(ctx):
    env = _env(ctx)
    px, src = env.px, env.src
    decl = _declared(env, ["delivery", "croppedType", "fullBleed", "socialSafe"])

    full_bleed = env.manifest.get("fullBleed") or []
    cropped = set(env.manifest.get("croppedType") or [])
    action_on = env.delivery in C14_ACTION_DELIVERY
    edge = C14_TITLE_SAFE if env.delivery == "broadcast" else C14_WEB_SAFE
    social_rects = []
    if env.delivery == "social":
        for name in (env.manifest.get("socialSafe") or []):
            r = C14_SOCIAL_SAFE.get(str(name).lower())
            if r:
                social_rects.append(r)

    def frame_exempt(f):
        """A fullBleed entry with no box exempts the whole frame for its
        window.  With a box it exempts only that region, which is what a
        full-bleed design ELEMENT needs."""
        return any(w.get("from", 0) <= f <= w.get("to", 10 ** 9) and not w.get("box")
                   for w in full_bleed)

    def bleed_mask(f):
        m = None
        for w in full_bleed:
            if not w.get("box"):
                continue
            if not (w.get("from", 0) <= f <= w.get("to", 10 ** 9)):
                continue
            bx0, by0, bx1, by1 = w["box"]
            if m is None:
                m = np.zeros((env.dec_h, env.dec_w), dtype=bool)
            m[int(by0 * env.dec_h):int(math.ceil(by1 * env.dec_h)),
              int(bx0 * env.dec_w):int(math.ceil(bx1 * env.dec_w))] = True
        return m

    mx_t, my_t = int(env.dec_w * edge), int(env.dec_h * edge)
    mx_a, my_a = int(env.dec_w * C14_ACTION_SAFE), int(env.dec_h * C14_ACTION_SAFE)
    title_band = np.ones((env.dec_h, env.dec_w), dtype=bool)
    title_band[my_t:env.dec_h - my_t, mx_t:env.dec_w - mx_t] = False
    action_band = np.ones((env.dec_h, env.dec_w), dtype=bool)
    action_band[my_a:env.dec_h - my_a, mx_a:env.dec_w - mx_a] = False
    overlay_band = None
    if social_rects:
        overlay_band = np.zeros((env.dec_h, env.dec_w), dtype=bool)
        for (_x0, oy0, _x1, oy1) in social_rects:
            overlay_band[:int(oy0 * env.dec_h), :] = True
            overlay_band[int(oy1 * env.dec_h):, :] = True

    settled_boxes = {}
    if src is not None:
        for el in src.text_elements():
            if cropped and src.is_named(el, cropped):
                continue          # deliberately cropped display type, by name
            win = src.settled_window(el, env.cuts)
            if not win:
                continue
            for f in range(win[0], win[1] + 1):
                settled_boxes.setdefault(int(f), []).append(el)
        frames = sorted(settled_boxes)
        if not frames:
            return _row("C14", {"delivery": env.delivery}, None, na=True,
                        na_reason="no settled text elements to hold to a safe area",
                        declarations=decl)
    else:
        probe = [int(clamp(a + 0.5 * (b - a), 0, px.n - 1)) for (a, b) in env.beats]
        if not probe:
            probe = list(range(0, px.n, max(1, px.n // 20)))
        if sum(1 for f in probe if _text_like_components(px, f)) < max(1, len(probe) // 5):
            return _row("C14", {"delivery": env.delivery, "basis": "pixel"}, None,
                        na=True,
                        na_reason="no text-like components on the pixel channel: a "
                                  "safe area applies to readable content and there "
                                  "is none to measure", declarations=decl)
        frames = list(range(px.n))

    tracked = _tracked_keys(px) if (src is None or action_on) else {}
    title_breach, action_breach, overlay_breach = [], [], []
    # Each share is over the frames on which its own test APPLIED, not over the
    # film: with px.n as the denominator the same breaching card scores B in a
    # 30 s film and C in a 4 s one, which is the same defect banded twice.
    tested_t = tested_a = 0
    # A render SHORTER than the composition -- which is exactly what C23's
    # duration gate exists to catch -- has fewer pixel frames than the source
    # has authored ones, and indexing the decoded mask with an authored frame
    # number raised IndexError before any row printed. The gate that reports the
    # short render must not be the thing the short render crashes.
    frames = [f for f in frames if 0 <= int(f) < px.n]
    if not frames:
        return _row("C14", {"delivery": env.delivery, "framesTested": 0}, None,
                    na=True,
                    na_reason="no settled text frame falls inside the delivered "
                              "render: the render is shorter than the composition, "
                              "which C23 reports as the duration gate",
                    declarations=decl)
    for f in frames:
        if frame_exempt(f):
            continue
        m = px.mask[f]
        bm = bleed_mask(f)
        if bm is not None:
            m = m & ~bm

        if src is not None:
            tested_t += 1
            sx, sy = env.dec_w / src.W, env.dec_h / src.H
            # The ink test is restricted to TEXT-LIKE components on BOTH
            # channels, not only on the pixel one. A block-level text element
            # is as wide as its container: a centred headline inside a
            # full-width div has the box [0, y0, W, y1], and intersecting the
            # raw frame ink with that box asks "is there any ink at all in this
            # horizontal band", which a full-bleed panel or an edge graphic
            # answers yes to on every frame. On one product film that reported
            # 108 breach frames on six wrappers whose type is centred and
            # nowhere near an edge.
            tmask = None
            for (_area, _cx, _cy, tx0, ty0, tx1, ty1) in _text_like_components(px, f):
                if tmask is None:
                    tmask = np.zeros((env.dec_h, env.dec_w), dtype=bool)
                tmask[int(ty0):int(ty1) + 1, int(tx0):int(tx1) + 1] = True
            if tmask is None:
                continue
            m = m & tmask
            hit_t = hit_o = False
            for el in settled_boxes[f]:
                x0, y0, x1, y1 = src.box_at(el, f)
                bx0 = int(clamp(math.floor(x0 * sx), 0, env.dec_w))
                bx1 = int(clamp(math.ceil(x1 * sx), 0, env.dec_w))
                by0 = int(clamp(math.floor(y0 * sy), 0, env.dec_h))
                by1 = int(clamp(math.ceil(y1 * sy), 0, env.dec_h))
                if bx1 <= bx0 or by1 <= by0:
                    continue
                sub = m[by0:by1, bx0:bx1]
                if int((sub & title_band[by0:by1, bx0:bx1]).sum()) > C14_BREACH_PX:
                    hit_t = True
                if overlay_band is not None and \
                        int((sub & overlay_band[by0:by1, bx0:bx1]).sum()) > C14_BREACH_PX:
                    hit_o = True
            if hit_t:
                title_breach.append(f)
            if hit_o:
                overlay_breach.append(f)
        else:
            keys = tracked.get(f, ())
            tm = None
            for (area, cx, cy, x0, y0, x1, y1) in _text_like_components(px, f):
                if (round(float(cx), 4), round(float(cy), 4)) not in keys:
                    continue          # not a tracked component
                if tm is None:
                    tm = np.zeros((env.dec_h, env.dec_w), dtype=bool)
                tm[int(y0):int(y1) + 1, int(x0):int(x1) + 1] = True
            if tm is None:
                continue
            tested_t += 1
            mm = m & tm
            if int((mm & title_band).sum()) > C14_BREACH_PX:
                title_breach.append(f)
            if overlay_band is not None and int((mm & overlay_band).sum()) > C14_BREACH_PX:
                overlay_breach.append(f)

        if action_on:
            # Action safe is about ANY non-ground content, not only type, so it
            # runs off tracked components on both channels.  Ink is
            # |luma - ground| > 28, so without the ground-plane and fill filters
            # every full-bleed panel and edge-anchored band breaches on every
            # frame of the piece.
            keys = tracked.get(f, ())
            am = None
            for (area, cx, cy, x0, y0, x1, y1) in _text_like_components(
                    px, f, max_fill=1.01, max_h_frac=1.0):
                if (round(float(cx), 4), round(float(cy), 4)) not in keys:
                    continue
                if am is None:
                    am = np.zeros((env.dec_h, env.dec_w), dtype=bool)
                am[int(y0):int(y1) + 1, int(x0):int(x1) + 1] = True
            if am is not None:
                tested_a += 1
                if int((m & am & action_band).sum()) > C14_BREACH_PX:
                    action_breach.append(f)

    ts = len(title_breach) / max(tested_t, 1)
    as_ = len(action_breach) / max(tested_a, 1)
    os_ = len(overlay_breach) / max(tested_t, 1)
    if not title_breach and not action_breach and not overlay_breach:
        band = "S"
    elif ts <= C14_A_TITLE_SHARE and not action_breach and not overlay_breach:
        band = "A"
    elif ts <= C14_B_TITLE_SHARE and as_ <= C14_B_ACTION_SHARE \
            and os_ <= C14_B_OVERLAY_SHARE:
        band = "B"
    else:
        band = "C"

    note = ""
    if ts > C14_B_TITLE_SHARE:
        note = (f"readable content inside the {edge:.0%} edge on "
                f"{len(title_breach)} frames")
    elif os_ > C14_B_OVERLAY_SHARE:
        note = f"settled type under a platform overlay on {len(overlay_breach)} frames"
    elif as_ > C14_B_ACTION_SHARE:
        note = (f"non-ground content inside the {C14_ACTION_SAFE:.1%} action-safe "
                f"band on {len(action_breach)} frames")
    elif title_breach or action_breach or overlay_breach:
        note = (f"{len(title_breach)} title, {len(action_breach)} action and "
                f"{len(overlay_breach)} overlay breach frames")
    if not action_on:
        note = (note + "; " if note else "") + \
            f"action safe not applied: there is no overscan on {env.delivery} delivery"
    if env.delivery == "social" and not social_rects:
        note = (note + "; " if note else "") + \
            "no socialSafe platform declared, so the UI bands are not tested"

    worst = rank_worst([(3.0, f) for f in title_breach]
                       + [(2.0, f) for f in overlay_breach]
                       + [(1.0, f) for f in action_breach])
    return _row("C14", {"titleSafeShare": round(ts, 4),
                        "actionSafeShare": round(as_, 4),
                        "overlayShare": round(os_, 4),
                        "edge": edge,
                        "framesTested": tested_t,
                        "delivery": env.delivery,
                        "basis": "source" if src is not None else "pixel"},
                band, worst, note, declarations=decl)


# =============================================================================
# C15  readability dwell
# =============================================================================
#
# WHAT IT MEASURES NOW
#   The unit of reading is a CARD, never a DOM element.  Text elements are
#   grouped by their clip (or, with no clips, by the cut interval their settle
#   lands in), and the card's readable window is derived from the group:
#
#     joining   every element's settled window overlaps every other's, so the
#               card is readable only once the LAST of them has settled: the
#               window is the intersection.  Canon 3.1: the hold is measured
#               from the settle, not from the card start.
#     replace   the windows do not all overlap, so the words stream through one
#               position: the window is the union and the words are the whole
#               stream.  That is RSVP, and canon 3.1 says to DERIVE the regime
#               rather than let it be declared, which is why it is read off the
#               overlap and not off the manifest.
#
#   Grading each element separately instead is the same category error as
#   bending an arc onto every headline: a per-letter cascade scored 17 ms per
#   word on a finished film, because a single letter is not a thing anybody
#   reads.
#
#   Two models by card ROLE, because the two reading rates differ by about six
#   times for the same text and cannot both drive one number.  A card is BODY
#   if any of its elements has wrapped, or it carries more than five words, or
#   more than 24 characters; otherwise it is DISPLAY.
#
#     body     characters per second, and the readable duration in ms
#     display  ms per WORD, and the readable duration in frames
#
#   S  body at or under 13 cps and at or over 833 ms; display at or over
#      300 ms per word
#   C  display under 130 ms per word, or under 8 frames absolute (scaled by
#      the delivered frame rate); or body over 20 cps or under 500 ms
#
#   The 8-frame absolute floor lands on the CARD, which is what resolves it
#   against canon 3.1's blessing of a 0.17 s replace-in-place stream: the
#   stream is one card, its window is the whole stream, and only its per-word
#   rate is 0.17 s.
#
# WHAT STILL SCORES C
#   A three-word display card held for 6 frames at 30 fps: 200 ms total, 67 ms
#   per word, and under the 8-frame floor twice over.  Or a 32-character
#   caption on screen for 1.0 s, which is 32 cps against a 20 cps ceiling.
#   Neither is relieved by any manifest key.

def c15_readability(ctx):
    env = _env(ctx)
    src = env.src
    decl = _declared(env, [])
    slam_min = fscale(C15_SLAM_MIN_FRAMES, env.fps)

    if src is None:
        return _c15_pixel(env, slam_min, decl)

    cards = _c15_cards(src, env)
    if not cards:
        return _row("C15", {}, None, na=True,
                    na_reason="no settled text elements", declarations=decl)

    worst_cps, worst_cps_el, worst_cps_f = 0.0, None, None
    worst_word, worst_word_el, worst_word_f = None, None, None
    body_fail, display_fail = [], []
    body_min_ms = float("inf")
    n_body = n_display = 0
    n_replace = n_flash = n_runcards = 0
    for card in cards:
        a, b = card["window"]
        frames = b - a + 1
        la, lb = card.get("life", card["window"])
        life_frames = lb - la + 1
        ms = frames / env.fps * 1000.0
        chars, words = card["chars"], card["words"]
        if card["regime"] == "replace":
            n_replace += 1
        if card.get("established"):
            # canon 3.1: a card that introduces no new word is beat or flash,
            # and the reading floors are about READING
            n_flash += 1
            continue
        if card["kind"] == "body":
            n_body += 1
            cps = chars / max(ms / 1000.0, 1e-6)
            if cps > worst_cps:
                worst_cps, worst_cps_el, worst_cps_f = cps, card["key"], a
            body_min_ms = min(body_min_ms, ms)
            if cps > C15_B_CPS or ms < C15_C_SETTLED_MS:
                body_fail.append((max(cps - C15_B_CPS, 0.0)
                                  + max(C15_C_SETTLED_MS - ms, 0.0) / 100.0, a))
        else:
            n_display += 1
            # Canon 3.1 prices display type per word: a replace-in-place stream
            # at 0.17 s and a joining stream at 0.30-0.35 s, "a saccade plus a
            # fixation per word". Both are rates over the card's LIFE, because
            # in both regimes the words arrive in turn and each one's budget is
            # the interval it gets. Dividing the INTERSECTION -- the frames on
            # which the finished line stands complete -- by the word count
            # prices a five-word line that accumulates over 1.8 s at 83 ms per
            # word, when its actual accumulation rate is 357 ms and is exactly
            # canon's joining figure. The reading WINDOW still drives the body
            # model, where the block really is read whole.
            per_word = (life_frames / env.fps * 1000.0) / max(words, 1)
            # In a replace-in-place stream the reading unit is the RUN, so the
            # card is priced at whichever of the two rates is the one the eye
            # actually gets. The absolute frame floor is unaffected.
            run_rate = card.get("runMsPerWord")
            if run_rate is not None and run_rate > per_word:
                per_word = run_rate
                n_runcards += 1
            if worst_word is None or per_word < worst_word:
                worst_word = per_word
                worst_word_el, worst_word_f = card["key"], a
            # The absolute floor is the flash boundary for a card that has to
            # stand alone. Canon 3.1 gives a strict replace-in-place stream its
            # own floor, 0.17 s, "where the eye never moves", so a fragment
            # inside a derived run is held to that instead. It is still a floor
            # and it is still absolute: a 5-frame card at 30 fps fails it
            # wherever it sits.
            in_run = card.get("runCards") is not None
            floor_f = (fscale(C15_REPLACE_FLOOR_MS / 1000.0 * 30.0, env.fps)
                       if in_run else slam_min)
            if per_word < C15_C_MSWORD or life_frames < floor_f:
                display_fail.append((max(C15_C_MSWORD - per_word, 0.0) / 10.0
                                     + max(floor_f - life_frames, 0.0), a))

    body_s = worst_cps <= C15_S_CPS and (n_body == 0 or body_min_ms >= C15_MIN_SETTLED_MS)
    body_a = worst_cps <= C15_A_CPS and (n_body == 0 or body_min_ms >= C15_MIN_SETTLED_MS)
    disp_s = worst_word is None or worst_word >= C15_S_MSWORD
    disp_a = worst_word is None or worst_word >= C15_A_MSWORD
    disp_b = worst_word is None or worst_word >= C15_B_MSWORD
    # Canon's C column for C15 is ONE clause and it is the display one:
    # "display < 130 ms per word or under 8 frames absolute". The body model
    # supplies canon's S row -- "body: cps <= 13 and >= 833 ms" -- and a card
    # outside it caps the row rather than failing it. The porter's 20 cps /
    # 500 ms C band is not in canon and it scored a product film C on a
    # depicted YouTube description nobody is meant to read.
    clean = not display_fail
    if body_s and disp_s and clean:
        band = "S"
    elif body_a and disp_a and clean:
        band = "A"
    elif disp_b and clean:
        band = "B"
    else:
        band = "C"
    if body_fail and band != "C":
        band = band_worse(band, "B")

    note = ""
    if display_fail:
        note = (f"{len(display_fail)} display card(s) under {slam_min} frames "
                f"or {C15_C_MSWORD:.0f} ms per word, worst {worst_word_el}")
    elif body_fail:
        note = (f"{len(body_fail)} body card(s) over {C15_B_CPS:.0f} cps or under "
                f"{C15_C_SETTLED_MS:.0f} ms, worst {worst_cps_el}: canon's C row "
                f"is the display clause, so this caps the row at B")
    elif body_fail:
        note = (f"{len(body_fail)} body card(s) over {C15_B_CPS:.0f} cps or "
                f"under {C15_C_SETTLED_MS:.0f} ms, worst {worst_cps_el}")
    elif worst_cps > C15_A_CPS:
        note = f"{worst_cps_el} runs at {worst_cps:.1f} cps"
    elif worst_word is not None and worst_word < C15_A_MSWORD:
        note = f"{worst_word_el} holds {worst_word:.0f} ms per word"

    worst = rank_worst(display_fail + body_fail
                       + ([(0.5, worst_cps_f)] if worst_cps_f is not None else [])
                       + ([(0.4, worst_word_f)] if worst_word_f is not None else []))
    return _row("C15", {
        "worstCps": round(worst_cps, 1),
        "minBodyMs": (None if math.isinf(body_min_ms) else round(body_min_ms)),
        "minMsPerWord": (None if worst_word is None else round(worst_word)),
        "cards": len(cards), "bodyCards": n_body, "displayCards": n_display,
        "replaceCards": n_replace, "flashCards": n_flash,
        "runPricedCards": n_runcards,
        "slamMinFrames": slam_min,
    }, band, worst, note, declarations=decl)


def _reading_window(src, el, env):
    """The frames in which this element can be READ.

    Canon 3.1 says the hold is measured from the settle, and the case it has in
    mind is a REVEAL -- a masked rise, a type-on, a clip-path wipe -- where the
    word is not fully present until the entrance finishes. A word that SLIDES
    in fully formed is legible the whole way; measuring only its post-settle
    frames reported 67 ms of reading time for a card that is on screen for
    400 ms and readable for 300 of them, and it did that on four cards of one
    broadcast ad. The shared Source already carries the corrected window and
    names the same failure in its own docstring: it opens at
    C15_READABLE_PROGRESS of arrival (80 %, or full opacity for a fade) and
    never later than the numeric settle, so a mask reveal still gets almost
    nothing for its entrance and a slide gets its travel back.

    The window still CLOSES at the exit or the cut, so a card cannot buy dwell
    at the end, and a card whose reading window is short is still short: the
    systo-26s "can be" card holds 9 frames at 60 fps either way and stays a C.
    """
    fn = getattr(src, "readable_window", None)
    if callable(fn):
        try:
            win = fn(el, env.cuts)
            if win:
                return win
        except Exception:
            pass
    return src.settled_window(el, env.cuts)


def _is_wrapped(src, el, f):
    """Does this element's own text occupy more than one LINE BOX?

    Counted from the line boxes the probe records, which is the only test that
    means what it says. The box-height rule this replaces -- box taller than
    1.6 x the font size is wrapped -- misrouted seventeen of eighteen reading
    units on a finished film into the body-copy model, because every card in it
    is a masked word rise whose mask wrapper is 1.8 to 2.1 times the font size:
    a single word, and even a single digit, tested as wrapped body copy and was
    then priced as a Netflix subtitle at characters per second. Under the
    display model the same film's real fault is a card at 117 ms per word,
    which is a different diagnosis pointing at a different fix.

    When the probe predates the line-box record there is no substitute that is
    not the same mistake, so the element is treated as unwrapped and the word
    and character counts alone decide the model."""
    lines = None
    fn = getattr(src, "lines_at", None)
    if callable(fn):
        lines = fn(el, f)
    if lines is None:
        return False
    return lines > 1


def _c15_cards(src, env):
    """Group settled text elements into the units a viewer actually reads.

    Grouping key: the element's clip when the composition has clips, otherwise
    the cut interval its settle frame lands in.  Within a group the regime is
    DERIVED, never declared, because an author-declared regime is an
    attestation and a builder whose card fails would simply relabel it
    (canon 3.1).  Two things are derived:

      joining / replace   whether the elements' settled windows really overlap
      read / flash        whether the card introduces a word not shown earlier
                          in the piece.  Canon 3.1: everything else is beat or
                          flash, and the reading floors do not apply to it.
    """
    groups = {}
    singles = []
    slam_min = fscale(C15_SLAM_MIN_FRAMES, env.fps)
    for el in src.text_elements():
        settled = src.settled_window(el, env.cuts)
        if not settled:
            continue
        win = _reading_window(src, el, env) or settled
        a, b = int(win[0]), int(win[1])
        # The WINDOW is the reading window; every metric that DESCRIBES the
        # element -- its copy, whether it wraps, which card it belongs to -- is
        # read at the SETTLED frame. Reading them at the reading-window start
        # reads a masked word mid-rise, where the wrapper box is still taller
        # than the type, and that re-labelled forty display cards as body copy.
        m = int(clamp(settled[0], 0, src.frames - 1))
        # The card's LIFE: from the first frame it starts arriving to the frame
        # the cut or its exit takes it away. Canon's "under 8 frames absolute"
        # is the flash-regime floor of canon 3.1 and it is about how long the
        # card is on screen; the per-word rate is the reading measure and stays
        # on the reading window.
        life_a, life_b = a, b
        # getattr, not a bare call: the module's own self-test builds a stub
        # source with no clip table, and an unguarded call aborted the whole
        # self-test before it reached a single assertion.
        clip = getattr(src, "clip_of", lambda _e: None)(el)
        if clip:
            life_a = min(life_a, int(math.ceil(clip["start"] * env.fps - 0.05)))
            # The card is on screen until the NEXT card starts. A composition
            # that pulls every clip end back a third of a frame so it cannot
            # bleed into the next one renders an eight-frame card as fifteen
            # delivered frames at 60 fps, and the frame it gives up belongs to
            # the transition, not to the card after it. Measuring to the clip's
            # own end lost one frame on every card and put three of them under
            # an absolute floor they are authored exactly on.
            nxt = [c for c in (env.cuts or []) if c > life_a]
            life_b = max(life_b,
                         (min(nxt) - 1) if nxt else (src.frames - 1),
                         int(math.floor((clip["start"] + clip["duration"])
                                        * env.fps + 0.05)) - 1)
        for mv in (getattr(src, "moves", None) or []):
            if mv["el"] == el and mv.get("role") == "entrance":
                life_a = min(life_a, int(mv["onsetF"]))
        chars = src.chars_at(el, m, own=True)
        if chars <= 0:
            continue
        text = (src.elements[el].get("text") or "").strip()
        words = max(1, len(text.split()))
        wrapped = _is_wrapped(src, el, m)
        # Body or display. Canon's two models are a CAPTION or paragraph, read
        # line by line at a characters-per-second rate, and DISPLAY type, read
        # as a shape. What separates them is whether the block runs to more
        # than one line and how many words it asks for -- not its character
        # count. A five-word all-caps label reading "MONTHS OF RECURRING
        # COMMISSIONS PAID" is display type at thirty-four characters, and
        # pricing it at the Netflix subtitle rate scored a product-UI label
        # that stands for 1.1 s as a legibility failure at 28 cps. A real
        # caption still lands here: it either wraps or runs past five words.
        if wrapped or words > C15_DISPLAY_MAX_WORDS:
            # A block of body copy is read as a block, on its own.  Only DISPLAY
            # type is split across elements as a technique (per word, per
            # letter, per line), so only display type has to be regrouped;
            # summing a heading, a paragraph and a caption into one character
            # count and dividing by their overlap invented a 43 cps card on a
            # product film that shows them one at a time.
            singles.append({"window": (a, b), "life": (life_a, life_b),
                            "regime": "single", "kind": "body",
                            "chars": chars, "words": words, "text": text,
                            "key": src.elements[el]["key"]})
            continue
        key = _group_key(src, env, el, m)
        g = groups.setdefault(key, {"a": [], "b": [], "chars": 0, "texts": [],
                                    "n": 0, "key": None, "life": [],
                                    "lifeB": []})
        g["a"].append(a)
        g["b"].append(b)
        g["life"].append(life_a)
        g["lifeB"].append(life_b)
        g["chars"] += chars
        g["texts"].append(text)
        g["n"] += 1
        try:
            x0, y0, x1, y1 = src.box_at(el, m)
            cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            prev = g.get("centre")
            g["centre"] = (cx, cy) if prev is None else \
                ((prev[0] + cx) / 2.0, (prev[1] + cy) / 2.0)
        except Exception:
            pass
        if g["key"] is None:
            g["key"] = src.elements[el]["key"]

    cards = list(singles)
    for _k, g in groups.items():
        a_int, b_int = max(g["a"]), min(g["b"])
        # "Joining" needs a real overlap.  Two words whose windows meet on one
        # frame are a stream, not a line held together: taking the intersection
        # there gave a 1-frame window and 17 ms per word on a finished film.
        if g["n"] == 1 or (b_int - a_int + 1) >= slam_min:
            window, regime = (a_int, b_int), "joining"
        else:
            window, regime = (min(g["a"]), max(g["b"])), "replace"
        text = _join_split_text(g["texts"])
        words = max(1, len(text.split()))
        distinct = len(_tokens(text))
        if words >= C15_TEXTURE_MIN_WORDS and distinct <= C15_TEXTURE_DISTINCT * words:
            # a repeated-word texture: the viewer reads the word, not the wall
            words = max(1, distinct)
        cards.append({"window": window,
                      "life": (min(g["life"]), max(g["lifeB"])),
                      "regime": regime, "kind": "display",
                      "chars": g["chars"], "words": words,
                      "centre": g.get("centre"),
                      "text": text, "key": g["key"]})
    cards.sort(key=lambda c: c["window"][0])

    # ---- reading runs: canon 3.1's replace-in-place stream -----------------
    # "0.17 s (350 wpm RSVP) is the floor for a strict replace-in-place stream,
    # WHERE THE EYE NEVER MOVES." In that regime the viewer reads continuously
    # across the cards and the rate that decides legibility is the stream's.
    # Charging each fragment separately asks a three-word piece of one sentence,
    # on screen for 267 ms between two other fragments of the same sentence, to
    # stand on its own as a card. Both replicas of aired broadcast work here
    # carry the identical card at the identical 267 ms; the reference is what
    # canon says an inference must be fitted against.
    #
    # The run also decides the REGIME, which canon 3.1 says to derive: a card
    # inside one is replace-in-place, "where the eye never moves", and canon
    # gives that regime a floor of its own at 0.17 s. Outside a run a display
    # card stands alone and keeps the 8-frame flash boundary. A film cannot buy
    # dwell either way: the per-word rate still applies to every card, and
    # 0.17 s is still an absolute floor.
    gap = fscale(C15_RUN_GAP_FRAMES, env.fps)
    diag = math.hypot(float(src.W), float(src.H))
    disp = [c for c in cards if c["kind"] == "display"]
    run, runs = [], []
    for c in disp:
        if run:
            prev = run[-1]
            near_time = c["life"][0] - prev["life"][1] <= gap
            pc, cc = prev.get("centre"), c.get("centre")
            near_place = (pc is None or cc is None
                          or math.hypot(pc[0] - cc[0], pc[1] - cc[1])
                          <= C15_RUN_CENTRE_FRAC * diag)
            if near_time and near_place:
                run.append(c)
                continue
            runs.append(run)
        run = [c]
    if run:
        runs.append(run)
    for r in runs:
        if len(r) < C15_RUN_MIN_CARDS:
            continue
        span = max(x["life"][1] for x in r) - min(x["life"][0] for x in r) + 1
        words = sum(x["words"] for x in r)
        rate = (span / env.fps * 1000.0) / max(words, 1)
        for c in r:
            c["runMsPerWord"] = rate
            c["runCards"] = len(r)

    # read vs flash, in play order
    seen = set()
    for c in cards:
        toks = _tokens(c["text"])
        c["established"] = bool(C15_FLASH_EXEMPT and toks and toks <= seen)
        seen |= toks
    return cards


def _join_split_text(texts):
    """Rebuild a card's copy from its elements.  Two adjacent one-character
    elements are LETTERS of one split word and are joined with nothing;
    anything else is joined with a space.  Without this an eleven-letter end
    card built from eleven spans counts as eleven words."""
    out = ""
    prev = None
    for t in texts:
        t = (t or "").strip()
        if not t:
            continue
        if prev is not None and len(t) <= C15_SPLIT_CHARS and len(prev) <= C15_SPLIT_CHARS:
            out += t
        elif out:
            out += " " + t
        else:
            out = t
        prev = t
    return out


def _tokens(text):
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower()) if w}


def _c15_pixel(env, slam_min, decl):
    """No source channel: per-word timing is not measurable, but the absolute
    dwell floor is.  A text-like component whose WHOLE life is shorter than the
    floor, while it is the only readable thing in frame, is a flashed card and
    that is a real C.  The guard on concurrency is what stops a per-word stagger
    reading as a string of flashed cards."""
    px = env.px
    flashes = []
    shortest = None
    for tr in px.tracks:
        fr = tr["frames"]
        if not fr or fr[0] <= 0 or fr[-1] >= px.n - 1:
            continue                       # a life clipped by the film's ends
        life = len(fr)
        boxes = tr["box"]
        mid = life // 2
        x0, y0, x1, y1 = boxes[mid]
        w, h = (x1 - x0 + 1), (y1 - y0 + 1)
        fill = tr["area"][mid] / max(w * h, 1)
        if h < C12_PIXEL_MIN_H or fill > C14_MAX_FILL:
            continue
        if w < C12_PIXEL_MIN_ASPECT * h:
            continue
        if shortest is None or life < shortest[0]:
            shortest = (life, fr[mid])
        if life >= slam_min:
            continue
        if len(_text_like_components(px, fr[mid])) > C15_PIXEL_MAX_CONCURRENT:
            continue                       # part of a stagger, not a lone card
        flashes.append((slam_min - life, fr[mid]))
    measured = {"minTextComponentFrames": (None if shortest is None else shortest[0]),
                "slamMinFrames": slam_min, "basis": "pixel"}
    if not flashes:
        return _row("C15", measured, None, na=True,
                    na_reason="per-word dwell needs the source channel; the "
                              "absolute-dwell half was measured on tracked text "
                              "components and found nothing under the floor",
                    declarations=decl)
    return _row("C15", dict(measured, flashedCards=len(flashes)), "C",
                rank_worst(flashes),
                f"{len(flashes)} lone text component(s) live fewer than "
                f"{slam_min} frames; reduced confidence, measured on the pixel "
                f"channel, and ms per word is not measurable without the source",
                declarations=decl)


# =============================================================================
# C16  palette adherence
# =============================================================================
#
# WHAT IT MEASURES NOW
#   The share of CHROMATIC pixels within CIEDE2000 8 of a declared palette
#   entry, on one settled frame per beat; the dominant GROUND of each beat
#   required to be a palette entry within CIEDE2000 10; and gradient banding
#   measured after encode.
#
#   A piece whose chromatic share is under 2 % is monochrome, duotone-neutral
#   or one-bit.  That is a whole professional style family in the playlist, and
#   the chromatic test measures nothing on it, so it is graded on NEUTRAL
#   adherence instead: the share of ALL sampled pixels within the same
#   CIEDE2000 8 of a palette entry.  A one-bit piece declaring
#   ["#000000", "#FFFFFF"] scores S.
#
#   S  adherence >= 0.95 and every beat ground on palette and no banding
#   C  adherence < 0.80, or one element rotating its own hue past 60 degrees
#
#   With no `palette` declared there is nothing to adhere to: the hue census is
#   printed as a report line and the row is N/A.  Hue-bin counting mis-scores
#   gradients, duotones and muted premium schemes, and nothing in the cited
#   60-30-10 sources licenses nHues <= 3 as a pass condition.
#
# WHAT STILL SCORES C
#   A film declaring ["#0A0A0A", "#FF6A3D"] that spends four of its six beats
#   on a teal ground: teal is about CIEDE2000 60 from both entries, so
#   adherence lands near 0.3 against the 0.80 floor.  Declaring the palette is
#   what makes the criterion gradeable, so the declaration cannot buy a pass.

def c16_palette(ctx):
    env = _env(ctx)
    px, src = env.px, env.src
    decl = _declared(env, ["palette", "footageRegions", "themeChanges"])

    palette = [hex_to_rgb(c) for c in (env.manifest.get("palette") or [])]
    palette = [c for c in palette if c]
    footage = env.manifest.get("footageRegions") or []
    theme_change = bool(env.manifest.get("themeChanges"))

    frames = [int(clamp(a + C16_BEAT_SAMPLE * (b - a), 0, px.n - 1))
              for (a, b) in env.beats]
    if not frames:
        step = max(1, px.n // C16_MIN_SAMPLES)
        frames = list(range(0, px.n, step))
    frames = sorted(set(frames))
    if not frames:
        return _row("C16", {}, None, na=True, na_reason="no frames to sample",
                    declarations=decl)
    rgb = px.rgb(frames)

    rotator, rotation = None, 0.0
    # The hue-velocity test reads per-element computed style, which only the
    # source channel carries. A PixelSource has no style runs at all and the
    # unguarded call crashed the whole run on any pixel-only grade.
    if src is not None and not theme_change and getattr(src, "style_runs", None):
        rotator, rotation = _hue_rotation(src)

    lab_pal = srgb_to_lab(np.array(palette, dtype=np.float64)) if palette else None
    hue_union = set()
    dominants = []
    chroma_px = mono_px = 0.0
    kept_px = 0.0
    adherent_chroma = adherent_all = 0.0
    sampled_chroma = sampled_all = 0.0
    ground_ok = ground_tot = 0
    band_hits = band_steps = 0
    worst_ground = []
    for f in frames:
        img = rgb.get(f)
        if img is None:
            continue
        keep = np.ones(img.shape[:2], dtype=bool)
        for r in footage:
            x0, y0, x1, y1 = [int(v) for v in r["box"]]
            keep[y0:y1, x0:x1] = False
        total = float(keep.sum())
        if total <= 0:
            continue
        h, s, v = rgb_to_hsv(img)      # reduce over the LAST axis, never axis 2
        chroma = keep & (s >= C16_SAT_MIN) & (v >= C16_VAL_RANGE[0]) \
            & (v <= C16_VAL_RANGE[1])
        kept_px += total
        chroma_px += float(chroma.sum())
        mono_px += float((keep & ~chroma).sum())

        bins = np.floor(h[chroma] / (360.0 / C16_HUE_BINS)).astype(int) % C16_HUE_BINS
        counts = np.bincount(bins, minlength=C16_HUE_BINS) / total
        hue_union.update(i for i in range(C16_HUE_BINS) if counts[i] >= C16_BIN_COVERAGE)
        dominants.append(max(float((keep & ~chroma).sum()) / total,
                             float(counts.max()) if len(counts) else 0.0))

        if lab_pal is not None:
            for mask, acc_name in ((chroma, "chroma"), (keep, "all")):
                pix = img[mask]
                if not len(pix):
                    continue
                step = max(1, len(pix) // C16_MAX_PIXELS_PER_FRAME)
                pix = pix[::step]
                d = ciede2000(srgb_to_lab(pix.astype(np.float64)), lab_pal).min(axis=-1)
                if acc_name == "chroma":
                    adherent_chroma += float((d <= C16_PALETTE_DE).sum())
                    sampled_chroma += float(len(pix))
                else:
                    adherent_all += float((d <= C16_PALETTE_DE).sum())
                    sampled_all += float(len(pix))
            # the dominant GROUND is the non-ink plane, not the frame median:
            # a per-channel median of a busy frame is a colour that is not in it
            not_ink = keep & ~px.mask[f]
            src_px = img[not_ink] if int(not_ink.sum()) > 64 else img[keep]
            gnd = np.median(src_px, axis=0)
            dg = float(ciede2000(srgb_to_lab(gnd[None, :]), lab_pal).min())
            ground_tot += 1
            if dg <= C16_GROUND_DE:
                ground_ok += 1
            else:
                worst_ground.append((dg, f))

        # banding after H.264: a step of 3 or more code values inside a region
        # that is otherwise smooth
        gy = img[::4, ::4, 1].astype(np.int16)
        dx = np.abs(np.diff(gy, axis=1))
        if dx.size and (dx <= 1).mean() > 0.5:
            band_steps += int(dx.size)
            band_hits += int(((dx >= C16_BANDING_MIN_STEP)
                              & (dx < C16_BANDING_MAX_STEP)).sum())

    if not dominants:
        return _row("C16", {}, None, na=True, na_reason="no beat frame decoded",
                    declarations=decl)

    chroma_share = chroma_px / max(kept_px, 1.0)
    mono = chroma_share < C16_MONO_CHROMA_FLOOR
    banding_rate = band_hits / max(band_steps, 1)
    census = {"nHues": len(hue_union),
              "chromaShare": round(chroma_share, 4),
              "dominantMin": round(min(dominants), 3),
              "hueRotation": round(rotation),
              "bandingRate": round(banding_rate, 4)}

    if lab_pal is None:
        if rotation > C16_HUE_ROTATION:
            return _row("C16", census, "C", [frames[0]],
                        f"{rotator} rotates its own hue {rotation:.0f} degrees "
                        f"(rainbow cycling)", declarations=decl)
        return _row("C16", census, None, na=True,
                    na_reason="no palette declared: hue census reported, adherence "
                              "not measurable", declarations=decl)

    if mono:
        adherence = adherent_all / max(sampled_all, 1.0)
        model = "neutral"
    else:
        adherence = adherent_chroma / max(sampled_chroma, 1.0)
        model = "chromatic"
    ground_share = ground_ok / max(ground_tot, 1)

    if adherence >= C16_S_ADHERENCE and ground_share >= 1.0 \
            and banding_rate <= C16_BANDING_RATE_MAX:
        band = "S"
    elif adherence >= C16_A_ADHERENCE and ground_share >= 0.9:
        band = "A"
    elif adherence >= C16_C_ADHERENCE:
        band = "B"
    else:
        band = "C"
    if rotation > C16_HUE_ROTATION:
        band = "C"

    note = ""
    if rotation > C16_HUE_ROTATION:
        note = (f"{rotator} rotates its own hue {rotation:.0f} degrees "
                f"(rainbow cycling)")
    elif adherence < C16_C_ADHERENCE:
        note = (f"only {adherence:.0%} of {model} pixels sit within CIEDE2000 "
                f"{C16_PALETTE_DE:.0f} of the declared palette")
    elif ground_share < 1.0:
        note = f"{ground_tot - ground_ok} beat ground(s) are not a palette entry"
    if mono:
        note = (note + "; " if note else "") + \
            (f"monochrome register: chromatic pixels are {chroma_share:.1%} of the "
             f"frame, so adherence is measured on all sampled pixels")
    if banding_rate > C16_BANDING_RATE_MAX:
        note = (note + "; " if note else "") + \
            f"gradient banding on {banding_rate:.1%} of sampled smooth steps"

    worst = rank_worst(worst_ground) or [frames[int(np.argmin(dominants))]]
    return _row("C16", dict(census, adherence=round(adherence, 3),
                            adherenceModel=model,
                            groundShare=round(ground_share, 3)),
                band, worst, note, declarations=decl)


def _hue_rotation(src):
    """The largest hue swing any single element applies to its own colour or
    background.  Kept as a hue-VELOCITY test on one element rather than on the
    frame's dominant colour: a per-scene ground flip is a standard brand-reel
    pattern and tripped the old whole-frame 60-degree rule."""
    rotator, rotation = None, 0.0
    for e in src.elements:
        for prop in ("color", "backgroundColor"):
            runs = src.style_runs[e["i"]].get(prop) or []
            hs = []
            for (_f, v) in runs:
                m = re.findall(r"[\d.]+", v or "")
                if len(m) < 3:
                    continue
                h, s, _v = rgb_to_hsv(np.array([[float(m[0]), float(m[1]),
                                                 float(m[2])]], dtype=np.float32))
                if float(s[0]) >= C16_SAT_MIN:
                    hs.append(float(h[0]))
            for i in range(1, len(hs)):
                d = abs(hs[i] - hs[0])
                d = min(d, 360 - d)
                if d > rotation:
                    rotation, rotator = d, e["key"]
    return rotator, rotation


# =============================================================================
# C20  photosensitive flash   (GATE, weight 0)
# =============================================================================
#
# WHAT IT MEASURES NOW
#   Full-frame luminance FLASHES inside the central field, per rolling
#   one-second window.  A transition is a frame pair whose relative luminance
#   steps by 0.10 or more with the darker of the pair under 0.80, over at least
#   25 % of the central half of the frame.  Consecutive same-sign transitions
#   are one CHANGE (a two-frame dissolve is not two flashes), and a FLASH is a
#   pair of opposing changes, exactly as W3C SC 2.3.1 defines it: the
#   standard's calibration point of 3 Hz is six changes and three flashes in a
#   second.
#
#   S  at most 3 flashes in any one second
#   C  more than 3          (GATE: caps the overall grade at C)
#
#   Weight 0, like every gate: it already caps the grade, and weighting it as
#   well would double-penalise the same defect.
#
#   There is NO manifest key that relieves this.  Every other hard criterion in
#   the rubric has a declaration escape; this one is the single defect in scope
#   that can physically harm a viewer, and an author's statement of intent does
#   not change what a seizure threshold is.
#
#   NOT measured here: the red-flash half of SC 2.3.1 (a pair of opposing
#   transitions involving a saturated red).  The measured dict says so rather
#   than letting a passing row imply a full 2.3.1 check.
#
# WHAT STILL SCORES C
#   Four hard cuts between a near-black card and a near-white card inside 24
#   frames at 30 fps.  Canon states the case directly: three cuts inside 18
#   frames is about five per second.  A strobe transition, a camera-flash
#   effect and an inverted-ground stinger cut on eighths all land here.

def c20_flash(ctx):
    env = _env(ctx)
    px = env.px
    frames, signs = _flash_transitions(env)
    # collapse consecutive same-sign transitions into one CHANGE: a dissolve
    # spread over three frames is one luminance change, not three
    changes = []
    prev_f, prev_sign = None, 0
    for i, f in enumerate(frames):
        if signs[i] == 0:
            continue
        f = int(f)
        same_run = (signs[i] == prev_sign and prev_f is not None
                    and f - prev_f <= C20_DISSOLVE_FRAMES)
        if not same_run:
            changes.append((f, signs[i]))
        prev_f, prev_sign = f, signs[i]
    window = max(1.0, float(env.fps))
    worst, worst_at = 0.0, None
    for (f, _s) in changes:
        c = sum(1 for (x, _t) in changes if f <= x < f + window)
        flashes = c / float(C20_CHANGES_PER_FLASH)
        if flashes > worst:
            worst, worst_at = flashes, f
    band = "C" if worst > C20_MAX_PER_SECOND else "S"
    note = ""
    if band == "C":
        note = (f"{worst:.1f} full-frame luminance flashes inside one second from "
                f"f{worst_at}, over the WCAG general flash threshold of "
                f"{C20_MAX_PER_SECOND} per second")
    return _row("C20", {"maxFlashesPerSecond": round(worst, 1),
                        "changes": len(changes),
                        "transitions": len(frames),
                        "redFlashTest": "not run"},
                band, [worst_at] if worst_at is not None else [], note,
                declarations=[])


def _flash_transitions(env):
    """(frames, signs) of full-frame luminance transitions over the WCAG general
    flash threshold inside the central field.  Uses the Pixel's own cached
    implementation when it has one, so C19 and C20 share a decode; otherwise it
    decodes for itself."""
    px = env.px
    fn = getattr(px, "flash_transitions", None)
    if callable(fn):
        try:
            return fn()
        except Exception:
            pass
    W, H = C20_FLASH_W, C20_FLASH_H
    path = getattr(px, "path", None)
    if not path or not os.path.exists(path):
        return [], []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf",
                          f"scale={W}:{H}", "-vsync", "0", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.uint8)
    n = len(a) // (W * H * 3)
    if n < 2:
        return [], []
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
    return frames, signs


# =============================================================================
# registry
# =============================================================================

CRITERIA = {
    "C12": c12_type_hierarchy,
    "C13": c13_contrast,
    "C14": c14_safe_margins,
    "C15": c15_readability,
    "C16": c16_palette,
    "C20": c20_flash,
}
ORDER = ["C12", "C13", "C14", "C15", "C16", "C20"]


def evaluate(ctx):
    """Run the whole family.  Returns rows in report order."""
    return [CRITERIA[cid](ctx) for cid in ORDER]


# =============================================================================
# self test
# =============================================================================
#
# `python crit_legibility.py` builds synthetic pixel and source channels and
# runs the family twice: once on a clean piece and once on the failing input
# named in each criterion's header comment.  It proves the module imports, that
# every function returns the documented shape, and that every criterion can
# still reach C.  `--ctx <pickle>` runs a real dumped context instead.

def _selftest():
    import types

    DW, DH = 640, 360
    FPS = 30.0
    N = 120

    class FakePixel(object):
        def __init__(self, grey, colour, flash=None):
            self.path = ""
            self.fps = FPS
            self.width, self.height = 1920.0, 1080.0
            self.grey = grey
            self.n = grey.shape[0]
            gf = grey.astype(np.float32)
            self.ground = np.median(gf.reshape(self.n, -1), axis=1)
            self.mask = np.abs(gf - self.ground[:, None, None]) > INK_DELTA
            self.core = np.abs(gf - self.ground[:, None, None]) > CORE_DELTA
            self.ink_frac = self.mask.reshape(self.n, -1).mean(axis=1)
            self._colour = colour
            self._flash = flash or ([], [])
            self._comps = None
            self._tracks = None

        @property
        def comps(self):
            if self._comps is None:
                self._comps = [_simple_components(self.mask[i])
                               for i in range(self.n)]
            return self._comps

        @property
        def tracks(self):
            if self._tracks is None:
                self._tracks = _simple_tracks(self.comps)
            return self._tracks

        def rgb(self, fl):
            return {int(f): self._colour[int(f)] for f in fl
                    if 0 <= int(f) < self.n}

        def flash_transitions(self):
            return self._flash

    class FakeSource(object):
        """Two text elements on a 1920x1080 stage."""

        def __init__(self, specs, fps=FPS, frames=N):
            self.W, self.H, self.fps, self.frames = 1920.0, 1080.0, fps, frames
            self.elements = []
            self._spec = specs
            self.style_runs = []
            for i, sp in enumerate(specs):
                self.elements.append({"i": i, "key": sp["key"], "id": sp["key"],
                                      "text": sp["text"]})
                self.style_runs.append({})

        def text_elements(self):
            return list(range(len(self._spec)))

        def settled_window(self, el, cuts):
            return self._spec[el]["window"]

        def font_px(self, el, f):
            return self._spec[el]["size"]

        def box_at(self, el, f):
            return self._spec[el]["box"]

        def chars_at(self, el, f, own=True):
            return len(self._spec[el]["text"])

        def prop(self, el, name):
            if name == "h":
                b = self._spec[el]["box"]
                return np.full(self.frames, b[3] - b[1], dtype=np.float32)
            return np.zeros(self.frames, dtype=np.float32)

        def style_at(self, el, name, f):
            return None

        def is_named(self, el, names):
            return self._spec[el]["key"] in (names or ())

    def _simple_components(mask, min_px=COMPONENT_MIN_PX):
        """A deliberately naive labeller: good enough for rectangles."""
        h, w = mask.shape
        seen = np.zeros_like(mask)
        out = []
        ys, xs = np.nonzero(mask)
        for (y, x) in zip(ys, xs):
            if seen[y, x]:
                continue
            stack = [(y, x)]
            seen[y, x] = True
            pts = []
            while stack:
                cy, cx = stack.pop()
                pts.append((cy, cx))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            if len(pts) < min_px:
                continue
            ay = [p[0] for p in pts]
            ax = [p[1] for p in pts]
            out.append((len(pts), float(np.mean(ax)), float(np.mean(ay)),
                        min(ax), min(ay), max(ax), max(ay)))
        out.sort(key=lambda c: -c[0])
        return out

    def _simple_tracks(per_frame):
        tracks = []
        live = {}
        for f, comps in enumerate(per_frame):
            used = set()
            prev = [(ti, tracks[ti]) for ti, lf in live.items() if lf == f - 1]
            for (area, cx, cy, x0, y0, x1, y1) in comps:
                best, bd = None, 1e18
                for ti, tr in prev:
                    if ti in used:
                        continue
                    r = area / max(tr["area"][-1], 1e-6)
                    if r < 0.5 or r > 2.0:
                        continue
                    d = (cx - tr["cx"][-1]) ** 2 + (cy - tr["cy"][-1]) ** 2
                    if d < bd:
                        best, bd = ti, d
                if best is None:
                    tracks.append({"frames": [f], "cx": [cx], "cy": [cy],
                                   "area": [area], "box": [(x0, y0, x1, y1)]})
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

    def build(ink_rgb, ground_rgb, boxes, flash=None):
        """boxes are (x0, y0, x1, y1) in decode px, painted on every frame as
        glyph-like vertical strokes rather than a solid bar: real type is
        SPARSE inside its own box, every criterion here assumes it, and a
        synthetic that paints a filled rectangle tests the wrong thing."""
        colour = np.zeros((N, DH, DW, 3), dtype=np.uint8)
        colour[:, :, :] = np.array(ground_rgb, dtype=np.uint8)
        for (x0, y0, x1, y1) in boxes:
            for x in range(x0, x1, 4):      # 2 px of stroke, 2 px of counter
                colour[:, y0:y1, x:min(x + 2, x1)] = np.array(ink_rgb, dtype=np.uint8)
        lin = colour.astype(np.float32) / 255.0
        grey = (lin @ np.array([0.299, 0.587, 0.114], dtype=np.float32) * 255.0)
        return FakePixel(grey.astype(np.uint8), colour, flash)

    print("\n  crit_legibility self test\n  " + "-" * 74)

    # ---- clean: white type on near-black, well inside the frame ------------
    boxes = [(200, 150, 440, 175)]
    px_ok = build((255, 255, 255), (10, 10, 10), boxes)
    src_ok = FakeSource([{"key": "#head", "text": "one tool", "size": 96.0,
                          "window": (10, 100),
                          "box": (600.0, 450.0, 1320.0, 525.0)}])
    ctx_ok = types.SimpleNamespace(px=px_ok, src=src_ok, manifest={
        "delivery": "web", "typeScale": [96.0], "palette": ["#0A0A0A", "#FFFFFF"]},
        cuts=[0], beats=[(0, N - 1)], fps=FPS, width=1920, height=1080)

    # ---- failing: light grey type on white, in the corner, flashing --------
    bad_boxes = [(4, 4, 120, 14)]
    flash_frames = list(range(10, 34, 3))
    flash_signs = [1 if i % 2 == 0 else -1 for i in range(len(flash_frames))]
    px_bad = build((200, 200, 200), (255, 255, 255), bad_boxes,
                   (flash_frames, flash_signs))
    src_bad = FakeSource([{"key": "#tiny", "text": "a b c", "size": 14.0,
                           "window": (10, 14),
                           "box": (12.0, 12.0, 360.0, 42.0)}])
    ctx_bad = types.SimpleNamespace(px=px_bad, src=src_bad, manifest={
        "delivery": "web", "typeScale": [14.0], "palette": ["#0A0A0A", "#FF6A3D"]},
        cuts=[0], beats=[(0, N - 1)], fps=FPS, width=1920, height=1080)

    for label, ctx in (("clean", ctx_ok), ("failing", ctx_bad)):
        print(f"\n  {label}")
        for row in evaluate(ctx):
            assert set(row) >= {"id", "name", "band", "weight", "na", "measured",
                                "worstFrames", "basis", "note", "declarations"}
            assert (row["band"] is None) == row["na"]
            assert row["band"] in (None, "S", "A", "B", "C")
            b = "N/A" if row["na"] else row["band"]
            meas = ", ".join(f"{k}={v}" for k, v in list(row["measured"].items())[:4])
            print(f"    {row['id']:<4s} w{row['weight']}"
                  f"{'*' if row['gate'] else ' '} {b:<4s} {meas[:70]}")
            if row["note"]:
                print(f"         -> {row['note'][:110]}")
    print("\n  shape assertions passed\n")
    return 0


def _run_pickle(path):
    import pickle
    with open(path, "rb") as fh:
        ctx = pickle.load(fh)
    rows = evaluate(ctx)
    print(json.dumps(rows, indent=1, default=str))
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--ctx":
        sys.exit(_run_pickle(sys.argv[2]))
    sys.exit(_selftest())
