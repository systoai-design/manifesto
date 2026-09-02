# Corrections applied

Every correction made to the six research documents in this directory, and every claim
downgraded from source to inference. Applied 2026-09-02 against a full citation audit and a
set of practitioner reviews.

Two kinds of entry:

- **CORRECTION** — a claim that was wrong (arithmetic, attribution, recipe, or contract
  violation) and has been fixed in place.
- **DOWNGRADE** — a claim that was not wrong but was not supported either. It has been
  rewritten as an explicit inference, marked as a tuning parameter, or removed.

Counts: **231 items** across six documents. 148 corrections, 83 downgrades.

---

## `twelve-principles.md` — 52 items (34 corrections, 18 downgrades)

### Contract and measurement primitives

1. **CORRECTION** — `CustomEase` and `CustomWiggle` added to the permitted primitives in §0.2.
   Both are pure functions of progress and free since GSAP 3.13; they are the correct tool
   wherever the document chained tweens to fake one curve.
2. **CORRECTION** — §0.2: the frame grid was established and then abandoned. Sections 2, 3, 5,
   6, 9, 10 and 12 authored in raw seconds (0.55, 0.45, 0.32), which at 30 fps ends between
   frames so the settled pose is never rendered. Rule added: every start and duration goes
   through `f()`.
3. **CORRECTION** — M1 ink mask: the fixed 28-level threshold against the frame median breaks
   twice (low-contrast design registers no ink; full-bleed design inverts the median so the
   background becomes the ink). Now derived per frame with an ink-fraction assert.
4. **CORRECTION** — M7 re-trigger test: a bare 1.15× ratio is unstable near zero, and the
   anticipation detector deliberately drives the series through zero. Absolute floor added.
5. **CORRECTION** — M9: the zero-duplicate-frames rule now exempts declared on-twos cadence
   and declared freezes. As written it banned the commonest closing shot in the medium.
6. **CORRECTION** — M10 settled window: `a + 0.35 s` produces an **empty window** for any beat
   under 0.565 s (17 frames), so every settled-window check silently passed on short beats.
   Changed to `a + min(0.35, 0.25·d)`.
7. **DOWNGRADE** — frame-rate note: delivery rates (23.976, 24, 25, 29.97) were absent; frame
   rate is now stated as a decision that scales every per-frame threshold.

### 1. Squash and stretch

8. **CORRECTION** — the recipe's squash peaked two frames after the stop, which the document's
   own §1(d) detector calls a wobble. Squash now starts at `IMPACT − f(1)`.
9. **CORRECTION** — the object materialised in mid-air (`y: -260` with the element at
   `top: 380px`, plus a 2-frame fade). Now starts off-frame with no opacity tween.
10. **CORRECTION** — 6 % stretch is invisible at 29 px of travel per frame. Raised to 20-50 %
    elongation for a fast fall, with the UI figure labelled as UI micro-feedback.
11. **CORRECTION** — the text variant squashed a word to `scaleX 1.18`, breaking the
    document's own `<= 1.06-1.10` rule and §11(b)'s outright ban. Reduced to 1.06.
12. **CORRECTION** — impact and recovery converted 60 fps counts by **milliseconds**, giving
    1-2 frames at 30 fps. A one-frame deformation is a flicker. Frame counts now carried.
13. **CORRECTION** — "premium = zero squash" instructs a weightless film, which §13 then names
    as a defect. Restated: 1-3 % with zero oscillation.
14. **CORRECTION** — opacity was on the same tween as position everywhere. Separate envelope
    rule added, finishing in the first 40-60 % of the move.

### 2. Anticipation

15. **CORRECTION** — chaining `power2.inOut` into `power3.out` puts a velocity step at the
    junction (about 24 % of a 420 px travel in one frame). Ease changed and a one-curve
    `CustomEase` form added.
16. **CORRECTION** — anticipation magnitude as a pure fraction of travel breaks at video scale
    (12 % of 1200 px is a 144 px counter-move). Absolute cap added.
17. **CORRECTION** — visibility floor added: below 12-15 px of counter-travel a percentage
    rule stops working.
18. **DOWNGRADE** — the 1:3 anticipation-to-action ratio sat in a table of sourced rows.
    Labelled UI-only inference; explicitly not general.
19. **CORRECTION** — "skip when the element is not yet visible" contradicted §2(b)'s own
    scene-level anticipation. Qualified.
20. **DOWNGRADE** — the detector required a near-zero step at the wound-up extreme. That is a
    cartoon signal, not a law; a product-grade pull-back-then-push has no hold.

### 3. Staging

21. **CORRECTION** — contract violation: the dim tween re-owned `opacity` on `#s1`/`#s2` for
    150-210 ms while their entrance tweens were still running, and carried
    `immediateRender: false` so it snapped opacity to 1 mid-entrance. Start moved past the
    last entrance.
22. **CORRECTION** — the camera push cited `T = −offset·S` (recentring) while describing a
    hold-in-place move, which needs `T = −offset·(S−1)`. The typed constants matched neither.
    Both formulas now stated with the choice made explicit.
23. **CORRECTION** — offsets were typed constants; the HF rule requires them measured with
    `getBoundingClientRect` after `fonts.ready`.
24. **CORRECTION** — the staging blur of 3 px contradicted the document's own table.
25. **CORRECTION** — the blur table cited HF's transitions "Blur Intensity by Energy", which
    governs blur-through **cuts**. Re-sourced to `depth-of-field-blur` (3-6 px per depth step,
    cap 8/16/24).
26. **CORRECTION** — "camera push 1.3-2.5" cited `motion-blur-streak` `SCALE_FROM`, which is
    an element's entrance scale, not a camera parameter. Replaced.
27. **CORRECTION** — added the CSS `perspective`-is-focal-length row: a real push is
    `translateZ`, a zoom is `perspective`, wrapper scale is a crop-and-blow-up.
28. **DOWNGRADE** — the 1/3 concurrency rule is a UI rule; now scoped, with declared groups
    counting as one element and declared audio hits exempt.
29. **DOWNGRADE** — "more than 2/3 of summed step magnitude" marked as a tuning parameter.

### 4-6. Straight-ahead, follow-through, slow in/out

30. **CORRECTION** — the straight-ahead driver had no build-time seed, so frame 0 showed the
    unstyled CSS field. Seed call added (§§10 and 11 already seeded theirs).
31. **CORRECTION** — the overshoot table printed "house default 0 %" directly above
    "explicitly playful 5-10 %" with no way to tell which applied. Replaced with one
    register-cased row, and premium raised to 0-2 % because the cited Apple Spring is ζ 0.577
    (≈11 % overshoot).
32. **CORRECTION** — the "velocity-matched handoff" started a `power3.in` exit and a
    `power3.out` entry at the same `T`, so the two fastest points were half a second apart.
    Replaced with the two forms that actually match (shared-ease push; equal-duration cut).
33. **CORRECTION** — the nudge-curve chain has velocity steps at both joins (1000 → 1800 →
    857 px/s), which the document's own §12(d) jerk detector would flag. `CustomEase` form
    given.
34. **CORRECTION** — "Apple HIG default (0.25, 0.1, 0.25, 1)" is the CSS `ease` keyword, not
    an Apple token. Relabelled.
35. **DOWNGRADE** — the "~5 %" velocity-match tolerance is HF's stated figure and is missed by
    HF's own worked example by 3:1. Marked aspirational, with a usable replacement criterion.
36. **DOWNGRADE** — MD3 tokens marked as a second-hand citation (the canonical page never
    fetched).
37. **CORRECTION** — added the sub-5-frame rule: below 5 frames ease is noise, author
    positions.

### 7-9. Arcs, secondary action, timing

38. **CORRECTION** — contract violation: arc recipe (a) ran two concurrent `fromTo` tweens
    both owning `y` on `#chip` and claimed it was safe because "x and y are separate
    aliases". Split into disjoint properties.
39. **CORRECTION** — arc depth restated as a fraction of the chord; the pixel figure is UI
    scale and makes the arc's register depend on how far the element happens to travel.
40. **CORRECTION** — arcs inverted from default-on to declared-organic-only. Type, cards and
    panels travel straight; an 80 % arc target produces the swoop.
41. **DOWNGRADE** — the 3-15 % arc-ratio band marked as a tuning parameter, with a note that
    the corporate end is inside antialiasing noise at low decode resolutions.
42. **CORRECTION** — the shadow tweened its own `y` separately from the card's, so the card
    visibly floated off its shadow during the entrance. Shadow now shares the card's `y`;
    only the spread lags.
43. **CORRECTION** — "shadow arrives 50 ms after card" describes the shadow **growing in**,
    not travelling separately; the document used it to justify a positional lag.
44. **DOWNGRADE** — the strobe threshold ("5-10 px per frame") is one measured case at 31 px,
    generalised. Restated as ~0.5 % of frame width per frame, marked inference, in three
    places plus Appendix A's conclusion.
45. **DOWNGRADE** — `distScale`/`WEIGHT` labelled as a UI function, with the arithmetic
    showing it forces a violation of the document's own strobe rule by 5×.
46. **DOWNGRADE** — the exit/entrance ratio scoped to cards that exit by animating in place.

### 10-13. Exaggeration, solid drawing, appeal, defects

47. **CORRECTION** — `stdDeviation` was written equal on both axes, which is a defocus, not a
    motion smear, and produces from frame one the read §10(d) warns against. Made directional.
48. **CORRECTION** — the energetic register's derived start scale (2.68) fell outside the
    document's own 1.3-2.5 band. Clamped.
49. **CORRECTION** — the impact reaction scaled `#bg` alone, which reads as the wallpaper
    twitching. Moved to the scene wrapper, and a camera-shake recipe added (previously absent).
50. **CORRECTION** — contract violations in §11: `perspective` on the parent **and**
    `transformPerspective` on the element (doubled projection); `filter: blur(28px)` on a
    child inside `preserve-3d` (flattens the 3D context). Both fixed.
51. **CORRECTION** — appeal-audit bugs: `String(v.ease).split("(")` makes every function ease
    its own family; `t.startTime()` is relative to a nested parent; the duration warning
    threshold contradicted the recipe. All three fixed.
52. **CORRECTION** — §12(e) printed ">= 3 ease characters per scene" directly above "one
    signature ease for 80 % of tweens". Reconciled.

*Also added as new §14 (four missing gestures):* the masked reveal (`clip-path` appeared once
in 1787 lines, `overflow` never, no split-text recipe); per-layer motion blur with the
derivative form and the isotropy caveat; the corrected `tmix` shutter arithmetic
(`frames=4` on 240 fps is a 360-degree shutter); luminance as a motion channel with the WCAG
2.3.1 flash limit; and the blocking pass, poster-frame test, 1:1 review and delivered-file
grading. Section 13's "floaty" detector gained a register caveat and "robotic" gained the
uniform-lag caveat (every stagger recipe in the document produces identical lag). Appendix B
downgraded Made Good Designs and Willenskomer to non-numeric citations.

---

## `character-motion.md` — 44 items (30 corrections, 14 downgrades)

### Citations

53. **DOWNGRADE** — a Williams blocking-order quote attributed to Edward Boyle
    ("block in the 'contact' key poses...") is **not on that page**. The page was fetched
    twice and dumped in full. Removed; contact-first is now received teaching practice with
    no citation.
54. **DOWNGRADE** — a corroborating tempo ladder attributed to "Altea Claveras, quoting the
    book" has no URL, appears in no source list, and returns nothing on a targeted search. It
    was the only independent confirmation that the Monmouth figures are per-step, so that
    reading is now explicitly an inference from one adapted secondary source.
55. **DOWNGRADE** — per-consonant lip-sync leads attributed to a High On Films snippet. The
    page now returns 200 and contains exactly one frame figure and no per-consonant
    breakdown. `LEAD_MBP` is now a deliberate inference, not a sourced differentiation.
56. **DOWNGRADE** — a "baby schema" quote attributed to the shape-language sources is in
    neither page and carried no URL. Removed.
57. **DOWNGRADE** — the "about 12 px" limb-thickness threshold had no source, and the
    `motion-blur-streak` quote beside it is about display **type size** (<~120 px), a
    different quantity by an order of magnitude. Removed.
58. **DOWNGRADE** — the HeyGen/Apache-2.0 attribution for `hyperframes-animation` is
    unverifiable: no licence file, no frontmatter field, no occurrence of "Apache". Flagged.
59. **CORRECTION** — the slow-in/slow-out page number is **47**, not 12 (12 is the reference
    index). Every other handwiki page number in the document is right.
60. **CORRECTION** — `animatorisland` is written by Alejandro Garcia himself, not
    "summarising" him. A primary source in this chain.
61. **CORRECTION** — the M/B/P closed-consonant rule is Gary C. Martin's phoneme page, the
    same author already cited for the ten shapes — not "the RMIT mouth-shape notes", which
    made one source look like two.
62. **CORRECTION** — the "Preston offered no help in timing" line is Angry Animator, "Preston
    Blair Deciphered", not an unnamed search snippet.
63. **CORRECTION** — the GSAP `transformOrigin` quote was not verbatim; the page says
    "relative to the element itself". Quotation marks removed.
64. **CORRECTION** — the Physics2DPlugin quote was truncated: easing is ignored "for these
    properties", the physics properties only.
65. **CORRECTION** — Cloy Toons was cited as agreeing with the tempo table. It **contradicts**
    it: a six-frame **cycle** is 3 frames per step, faster than the table's own "very fast
    run" row. This is the exact cycle-versus-step confusion the section spends a paragraph
    untangling, readmitted as false corroboration.
66. **CORRECTION** — the Monmouth table has **four** shifted parentheticals, not one typo; and
    the last row's caption is a song lyric, not "Very slow walk".
67. **CORRECTION** — Williams's arm-swing position is a choice between two things he says
    (widest at down as the real-life mechanic, contact as his animation preference), not the
    settled fact the document presented.
68. **CORRECTION** — the Envato cushion quote's ellipsis removed the operative clause: the
    full text is an out-and-back ("stops, moves forward a little, and then moves back"), not
    a one-way creep.
69. **DOWNGRADE** — neither Bloop nor Escape Studios states a frame rate. The 24 fps
    assumption is the document's inference and was presented as the authors' statement.

### Verification claims

70. **DOWNGRADE** — every "Verified" browser probe is unreproducible: none of the six HTML/JS
    artifacts was retained. All relabelled "reported, recomputable where noted, artifact not
    retained".
71. **CORRECTION** — the run verification does not survive arithmetic. With `RUN_AT = f(12)`,
    `STEP = f(8)`, `CYCLE = 16`, contacts land on frames 28 and 36 and UP on 34 and 42; frame
    30 is DOWN and frame 36 is a contact, not airborne.
72. **DOWNGRADE** — a key-pose silhouette check cannot verify a walk; every cycle defect lives
    between the keys. Stated in the preamble and the checklist.

### Rig and walk mechanics

73. **CORRECTION** — the rig's planted foot neither stays on the ground nor stays still:
    29.5 px of vertical excursion on a ~300 px character (19 px through the ground plane at
    DOWN, 13 px above it near the back contact) and ±7 px/frame of slide within one step. A
    constant root rate cannot fix either. Ankle-first authoring with closed-form two-bone IK
    now given, with code.
74. **CORRECTION** — IK moved out of the "needs a physics simulation" table. It is the law of
    cosines: stateless, closed-form, a pure function of the target. Listing it there
    foreclosed the fix for the document's worst defect.
75. **CORRECTION** — smoothstep between every pair of keys gives **zero velocity at every
    key**, an 8 Hz pulse at 15 frames per step, which is the "jerky motion, abrupt stops" on
    the document's own appeal-killer list. Wrapped Catmull-Rom given, with code.
76. **CORRECTION** — the rounding rule was self-contradictory (the only x.5 row is a run, and
    the stated rule takes the faster value 7, while the table and recipes chose 8). Resolved
    by quantising the **cycle**, not the step.
77. **CORRECTION** — perfect L/R symmetry is twinning. Per-side offset layer added.
78. **CORRECTION** — an amplitude scalar is not a personality control; the document warns
    against exactly this on the timing axis and ships it on the amplitude axis. Additive
    pose-offset layer added.
79. **CORRECTION** — no toe joint, so the rig cannot roll through the foot. Heel-strike and
    toe-off added to the hierarchy.
80. **DOWNGRADE** — the hip/shoulder counter-rotation is transverse-plane and invisible in a
    strict side view; a picture-plane rotation reads as the pelvis tipping. Relabelled as a
    stylistic lean with the correct side-view cheat given.
81. **CORRECTION** — `will-change` on all 13 rig parts is pointless in a seek-and-screenshot
    renderer and can change edge antialiasing; `filter: brightness(.8)` multiplies toward
    black and forces a separate compositing pass on the nested subtree. Both replaced.

### Face, jump, smears, lip-sync

82. **CORRECTION** — contract violation: `#hair`'s follow-through tween runs to f(53) and the
    settle started at f(50), so frames 50-53 had two `fromTo` tweens writing `#hair` rotation
    concurrently. Start moved.
83. **CORRECTION** — the blink close ease is backwards (`power2.in` creeps then slams).
84. **CORRECTION** — a rectangular lid scaled in Y closes with a straight edge across a round
    eye (a roller shutter), and the lid does not ride the eyeball. Both fixed.
85. **CORRECTION** — the head-turn anticipation (1.3 px/frame) and hair overshoot
    (0.94 degrees) are both below the document's own visibility floor.
86. **CORRECTION** — the head-turn cheat is missing X compression, eye parallax and the
    feature arc, which is what separates it from the Character Animator look.
87. **CORRECTION** — the hang-time units are crossed. Garcia's half second is the **fall**;
    `AIR = 0.5 s` is total flight, so its fall leg is 0.25 s ≈ one foot. A body-height leap
    needs about 36 frames, not 15.
88. **CORRECTION** — `scaleX = 1/scaleY` holds only in the flight phase; four of five phases
    break volume by 5-9 %. The prose claimed an invariant the code does not hold.
89. **CORRECTION** — the flight stretch axis is hard-coded to Y while the character travels
    260 px horizontally, so it is off-axis by 30-60 degrees and reads as inflation.
    `atan2(vy, vx)` given.
90. **CORRECTION** — two of five jump phase counts are outside the ranges the document says
    they are inside (the 8-frame crouch contradicts both the cited 100-200 ms anticipation
    range and the document's own checklist).
91. **CORRECTION** — "40 px/frame at peak" is the **mean**; `power3.out`'s derivative at u=0
    is 3, so the first frame carries about 120 px.
92. **CORRECTION** — the smear elongation is about half what the technique needs: the puck
    needs 4.4× to close the inter-frame gap and `K = 1.6` delivers 2.02×, leaving an 83 px
    hole. `K` should be derived. Also, the quoted 2.6× is at u = 0, which is never rendered.
93. **CORRECTION** — one-frame ghost spacing at 40 px/frame produces four discrete
    silhouettes: a multiples read, not a blur read. Both remedies given.
94. **DOWNGRADE** — the strobe threshold restated as a fraction of frame width (or of object
    width), with the smooth-pursuit caveat: a tracked hero does not strobe at speeds that
    shatter the background.
95. **CORRECTION** — the open-shape lip-sync lead rounds **down** to 2 frames (67 ms), below
    the source's stated floor, in the one direction the source warns about. Rounded up to 3.
96. **CORRECTION** — 14 cues over 74 frames keys nearly every phoneme, which the document's
    own cited rule forbids; mid-phrase rests read as the character stopping talking three
    times in one line; and the jaw is the primary volume signal, not optional.

---

## `kinetic-type.md` — 38 items (26 corrections, 12 downgrades)

97. **CORRECTION** — the RSVP comprehension paper is **Di Nocera, Ricciardi and Juola** (2018),
    not Benedetto et al. Corrected in three places; the findings themselves are right.
98. **CORRECTION** — the PLOS ONE 2016 paper is Primativo et al., which reports its own
    experiments; Rubin and Turano is one of the works it cites and partially disputes.
99. **CORRECTION** — "23 segments in 25.867 s with a median of 2.833 s and a minimum of
    0.067 s" is arithmetically impossible (the mean is 1.12 s). Recomputed from the cut list:
    median 1.067 s, mean 1.073 s, max 2.4 s, min 0.1 s.
100. **CORRECTION** — "12 of 23 cuts locked to onsets within 0-2 frames" recomputes to **11 of
     23**, 9 of them early, with twelve cuts 3-6 frames off the grid.
101. **CORRECTION** — the cascade row said per-unit duration is "about 0.7 of the total". R is
     the ratio of per-unit to sweep; the share is `R/(1+R)` = 0.41, which is what R3's own
     algebra computes. A builder copying the table value would author a per-unit tween ~70 %
     too long.
102. **CORRECTION** — "exit = 0.6 × entrance (the midpoint of the ranges above)" is not the
     midpoint; the five cited ranges give 0.70, 0.67-0.77, 0.625 and 1.0. Raised to 0.65-0.70,
     and scoped to cards that exit by animating in place.
103. **CORRECTION** — "overshoot budget 0-5 % corporate" cited a table with **no Corporate
     row**. Relabelled inference.
104. **CORRECTION** — the Netflix 3-11 frame gap rule is stated for **24 fps content**; the
     qualifier was dropped, silently changing the rule at the 30 fps the document works at.
105. **CORRECTION** — a Beat2Cut sentence in quotation marks is not on the page. Replaced with
     the actual wording; the substance is supported.
106. **DOWNGRADE** — the forced-alignment "tolerance above 200 ms" is in neither cited source
     and is probably wrong (evaluation is conventionally 10-100 ms). Removed.
107. **DOWNGRADE** — "WhisperX degrades on noisy audio" is uncited. Removed.
108. **DOWNGRADE** — the Gunner Google Home quote and Motion Award were attributed to a Behance
     page with no URL anywhere in the source list. Untraceable; claim softened.
109. **DOWNGRADE** — the Ordinary Folk identity claim was attributed to a "Studio Ahremark case
     study" with no URL. Removed.
110. **DOWNGRADE** — eight further studio sources listed explicitly as unverified in this pass.
111. **CORRECTION** — the hold model is a set of caption **floors** presented as design
     targets. A 3-word read card computes to a 2.11 s card, longer than 21 of the 22 interior
     segments of the reference. Causality restated: fix the beat grid, then cut the copy.
112. **DOWNGRADE** — the 0.40 s per-card reserve is an untested guess that propagates into
     `holdFor()`, `schedule()`, R1 and a proposed grader check. Flagged where it enters.
113. **CORRECTION** — the beat regime conflates replace-in-place (true RSVP, no eye movement,
     0.17 s floor) with accumulation (a saccade plus a fixation per word, 0.30-0.35 s). Split.
114. **DOWNGRADE** — "3-4 words maximum" comes from a consolidation of tutorials, which is not
     a source. Relabelled.
115. **CORRECTION** — `schedule()`'s default 3-frame gap after every card is a metronome one
     level up: the reference is roughly 60 % hard cuts with no gap. Default changed to 0.
116. **CORRECTION** — regime was author-declared, making the central deliverable
     unfalsifiable. `regimeOf()` added: a read card is one that introduces a new word.
117. **CORRECTION** — the entrance table offered one mechanic per card, which is the
     flat-but-competent tell the document names. The reference stacks 2-4 signals; rule added.
118. **CORRECTION** — "at least three mechanisms and three eases" is backwards for short form.
     Restated as one dominant mechanic plus at most two accents.
119. **CORRECTION** — the full-frame ground inversion, the reference's actual punctuation
     device (19 black, 4 white), had no row. Added.
120. **CORRECTION** — motion blur appeared once, as a prohibition. Positive rule added
     (1.5 % of frame width per frame) with the isotropy caveat on CSS `filter: blur()`.
121. **CORRECTION** — "anticipate by 1-2 frames": 2 frames at 30 fps is 67 ms of video lead,
     past the detectability threshold. Reduced to 1 frame at 30 and 24 fps.
122. **CORRECTION** — the proposed grader check "every structural cut 0-2 frames early" is
     failed by the reference on twelve of twenty-three cuts. Rewritten as a proportion.
123. **DOWNGRADE** — "a per-word entrance longer than twice the gap reads as a queue" has no
     source and no measurement, and the clamp it produced reassigns emphasis at random.
124. **CORRECTION** — R8's clamp moved from duration to start time; on its own onsets the old
     clamp produced 0.35, 0.35, 0.12, 0.35, 0.30.
125. **CORRECTION** — R8's `lineSettle` used the unclamped constant and dropped the `LEAD`
     term, so it was not the settle of any tween in the loop.
126. **CORRECTION** — blur specified in absolute pixels at 140, 150 and 340 px type. Restated
     in `em`, with the Chromium antialiasing-mode note (any non-`none` filter switches text
     off subpixel AA, so apply `blur(0px)` to all type or none).
127. **CORRECTION** — R2 and R11 set Archivo Black at weight 900. It ships one style at 400, so
     this triggers synthetic emboldening — and R11's hero/sub weight contrast does not exist.
128. **DOWNGRADE** — R2's mask padding constants are per-face metrics, not constants.
129. **CORRECTION** — R3's "the stagger budget is satisfied automatically for any R near 1" is
     false at the T its own comment recommends (T = 2 s gives a 1.18 s sweep against a 0.5 s
     cap).
130. **CORRECTION** — R5's breathe repeat evaluates to **0** with its own inputs, and a yoyo
     with repeat 0 never returns, so the word ends at weight 820. Guarded.
131. **CORRECTION** — R7 scales the type to 36×, which on a promoted layer is a blurred
     texture enlargement near Chromium's limits. Scale the ground and mask instead.
132. **CORRECTION** — R7's transform origin is a hard-coded pixel pair measured against a
     shaped run; it breaks silently on any copy or font change. Derived from a Range rect.
133. **CORRECTION** — R7's multiply knockout puts a 1-2 px dark halo on every glyph (mid-grey
     antialiased edges multiplied against bright footage), and `autoAlpha` on a multiply layer
     does not fade type in — it turns white to grey. Mask form preferred.
134. **CORRECTION** — no recipe waited for fonts before measuring, and `font-display: block`
     was set on one face only. `document.fonts.ready` gating and `force3D: true` added as R11b.

---

## `motion-rules.md` — 33 items (21 corrections, 12 downgrades)

135. **CORRECTION** — the shutter recipe. `tmix=frames=4` on a 240 fps stream integrates
     16.67 ms, the entire 60 fps frame interval: a **360-degree shutter**, twice any camera.
     Use `tmix=frames=2` then `framestep=4`. This is the most consequential single error in
     the document because it is the recipe most likely to be run verbatim.
136. **CORRECTION** — Rule 1's offset restated as 15-30 % of the offset element's own duration.
     A constant frame count is a cascade against a 6-frame snap and simultaneous against a
     40-frame settle, and Rule 2 already defines the same relationship as a fraction.
137. **CORRECTION** — Rule 13's distance-duration table forces a violation of Rule 13's own
     strobe rule by 5× (a full-screen move at the 2.0× cap is 53 px/frame). Scoped to UI;
     peak-velocity budgeting substituted.
138. **DOWNGRADE** — the strobe threshold restated as ~0.5 % of frame width per frame, with the
     camera-department cross-check (a pan crossing frame width in 5-7 s at 24 fps).
139. **CORRECTION** — Rule 9's stagger cap. The 0.5 s cap is UI-scale; per-character kinetic
     type runs 1.5-2.5 s. And `min(0.06, 0.5/n)` fails silently above 16 items at 30 fps
     (step 0.94 frames), while the stated cutoff of 9 is neither that nor anything else.
140. **CORRECTION** — Appendix A's Range Selector translation gives a uniform `each`, but a
     Range Selector with Ease High/Low set is a non-uniform distribution of start times. GSAP's
     stagger `ease` is the direct analogue and was never mentioned.
141. **CORRECTION** — Appendix A's influence-to-`powerN` mapping table removed. Influence sets
     handle length; the exponent sets curve shape; there is no monotone mapping, and the
     document ships a fitter that does the job.
142. **CORRECTION** — "75 % both sides puts the highest speed point in the middle" is true of
     every symmetric `inOut` curve and is not a property of 75 %.
143. **CORRECTION** — Rule 4's `CustomEase.create("name", "0.31,0.15,0.07,1")` is not the
     documented syntax. SVG path data form given, plus the (time, progress) space caveat.
144. **CORRECTION** — Rule 5's "never linear for spatial movement" contradicts Rule 4's own
     nudge-curve recipe, whose middle 65 % is linear. Continuous motion exempted.
145. **CORRECTION** — Rule 5's exit ban contradicts the document's own measurement: the
     reference has 10 blank runs, and you cannot produce an empty frame without an exit.
146. **DOWNGRADE** — the ease-variety quotas ("3 different easings", "no more than 2 tweens
     sharing an ease") deleted: they contradict Rules 9 and 11 of the same document and
     encourage the agent-made look.
147. **CORRECTION** — Rule 7: CSS `perspective` **is** the focal length; `translateZ` is the
     dolly. The document said there is no lens, so every camera move authored from it is a
     wrapper scale, which is a crop-and-blow-up.
148. **CORRECTION** — parallax ratios are constant only for a lateral move; under a push,
     displacement and scale follow `d/(d−t)`. Plus the counter-scale trap: any layer pushed
     back on Z arrives smaller than the layout intended.
149. **DOWNGRADE** — camera drift restated as a register, not a law. Locked-off is deliberate
     and common, and perpetual drift fights the document's own legibility rule.
150. **CORRECTION** — Rule 6's arc depth restated as a fraction of the chord.
151. **CORRECTION** — Rule 6/13's 1/3 travel rule exempts transitions by class; as written it
     forbids most of the transition vocabulary Rule 8 enumerates.
152. **CORRECTION** — Rule 12's hierarchy test ranked by peak displacement, which would fail a
     correctly hierarchical build and reward the failure its own quotation warns about.
     Changed to visual weight.
153. **DOWNGRADE** — madegooddesigns was read only via search summary; nothing now depends on
     it.
154. **CORRECTION** — Rule 10's median-segment figure corrected from 2.833 s to 1.067 s.
155. **CORRECTION** — Rule 10 carries two reading rates differing by 6× (13 cps subtitle,
     4 words/s display) and the appendix silently adopted the stricter one. Reconciled by
     scale of type.
156. **DOWNGRADE** — Rule 10's motion-fraction band (0.7 / 0.1) marked as a tuning parameter.
157. **CORRECTION** — the duplicate-frames rule exempts deliberate freezes and declared
     cadence, with the note that it otherwise invites a breathing lock-up.
158. **CORRECTION** — Rule 15's overshoot denominator defined explicitly, and the register
     split stated.
159. **CORRECTION** — Appendix B's velocity-match row rewritten (HF's own preset computes to
     `vmatch = 0.67`, missing its own stated 5 % by 13×).
160. **DOWNGRADE** — Appendix C now records that the "12 of 23 cuts" finding has no null model
     and recomputes to 11 of 23; with a 5-frame window on a dense bed that is near chance.

*Seven rules added as Appendix C1, each of which the document was missing:* transform origin
(the commonest single failure in junior AE work, absent from a document this detailed about
easing); masks, mattes and wipe reveals (mentioned once, as something a cascade must not be
confused with, while being the sanctioned way to do what the width/height ban forbids);
delivery (title/action safe, minimum type size, hairline strokes, multi-aspect); **photosensitivity**
(the only genuinely unsafe gap: three cuts in 18 frames is 5 per second, and a full-frame
luminance change on each is a WCAG 2.3.1 violation); frame rate as a stated decision; eye-trace
across the cut; seamless loops (velocity continuity, and the `yoyo` pendulum trap); the blocking
pass; audio runway; sub-pixel settle; spatial versus temporal interpolation (roving keyframes);
luminance as a motion channel; and H.264 compression. Rule 13 also gained the non-linear scale
perception and stroke-weight-scaling consequences.

---

## `sound-design.md` — 27 items (19 corrections, 8 downgrades)

161. **CORRECTION** — §4.2's whoosh contradicts §3.2 of the same document and produces a click
     of static, not a whoosh. Measured on its own defaults: the envelope reaches −20 dB
     0.1-0.2 ms into the file and 92-100 % of the energy sits in the first 20 %. A 60-150 ms
     pre-roll swell is now built regardless of ease, with the peak on the peak-velocity frame.
162. **CORRECTION** — the block-wise filter does **not** carry state: `sosfilt` starts from zero
     on every call. Measured, that puts a 93.75 Hz spectral line at 3.5× the surrounding median
     on every whoosh (47 Hz on risers, 21.5 Hz on `bed-compose.py`'s). `zi` now carried, with
     a state-variable filter recommended for a swept band-pass.
163. **CORRECTION** — white noise is the wrong source: the cited aeroacoustic model gives a
     1/f² roll-off. Pink source now specified.
164. **CORRECTION** — the impact is two layers where a professional impact is four (transient,
     body, sub, tail). Without the 120-250 Hz body layer it is inaudible on phones except as a
     click. `bed-compose.py`'s own `impact()` already has three of the four.
165. **CORRECTION** — "K-weighting rolls off low frequencies, so a sub-drop adds little to
     LUFS" is wrong at these frequencies. Measured from the BS.1770-4 coefficients: −0.8 dB at
     120 Hz, −2.5 dB at 65 Hz, −3.9 dB at 50 Hz. Both the sub-drop and the impact body count
     almost fully.
166. **CORRECTION** — the sub-drop's inter-sample overshoot is +0.01 dBTP at 0 dBFS sample
     peak. The true-peak risk is the `tanh`-saturated click and the coincidence with the bed's
     boom. Warning re-aimed.
167. **CORRECTION** — the shimmer's `1.5 ** (k*0.5)` ratio is 3.51 semitones, so six partials
     are a diminished-seventh cluster: exactly the chord the comment says it avoids. Inharmonic
     ratios given, plus key-tuning from `bed-analyse.py`.
168. **CORRECTION** — the impact anchor ("velocity reaches zero") is 3-6 frames late on every
     hard `.out` ease; `expo.out` is at 99 % of target at t = 0.66. Redefined as the first
     frame below a visibility threshold.
169. **CORRECTION** — §6.2 rule 1 ("every card start gets exactly one transient") contradicts
     §2.3 and §5.4 of the same document and produces the drum part they warn against. Rewritten
     as a candidate list plus thinning.
170. **DOWNGRADE** — BT.1359-1's +45 ms is a newsreader speech threshold applied as if it were
     an impulsive figure, to three significant figures. Flagged.
171. **CORRECTION** — "up to three frames late is inside detection" is dangerous advice: a
     click 100 ms after a hard cut reads as a mistake. Ceiling reduced to two frames, and the
     placement rule stated as 0 to +1 frame late, never early.
172. **CORRECTION** — London's 100 ms figure is about judging rhythmic quantity, not about two
     clicks fusing; two transients 30-60 ms apart are a flam, played on purpose. Rule kept,
     justification corrected.
173. **CORRECTION** — the kick pitch envelope was cross-referenced to `disney-principles.md`'s
     2-4 frame UI squash window, a category error. Re-sourced to the kick-synthesis pages the
     document already cites.
174. **CORRECTION** — "do not duck the bed for SFX" elevated a tooling constraint about
     *automatic* carving into a mixing rule. A hand-placed `data-automation` dip of 50-200 ms
     at 3-6 dB under a structural hit is normal and is what gives a hit room.
175. **CORRECTION** — "keep ticks above 4 kHz when a voice is present" moves them into the
     sibilance band, where they collide with every "s". 2-3 kHz at −3 dB, or 8-10 kHz.
176. **CORRECTION** — deliver 48 kHz (every platform and broadcast spec), resampling the
     44.1 kHz bed with `resample_poly` or `soxr`, never `np.interp`.
177. **CORRECTION** — ATSC A/85 (−24 LKFS, −2 dBTP) added to the loudness table; it is the
     target a US client asks for.
178. **CORRECTION** — the `grade-original.py` peak gate reads `max_volume` (sample peak) while
     the document recommends dBTP; the script already runs `ebur128=peak=true`.
179. **CORRECTION** — `render_stem` truncates the last cue with no fade, so a 1 s decay on the
     final card ends in a hard cut on the last frame.
180. **CORRECTION** — no true-peak limiter anywhere: two hits within a bar plus the bed's own
     boom exceed −1 dBTP at the −15 LUFS gain, which §5.5 warns about and then does nothing
     about. Master chain added.
181. **CORRECTION** — the AAC priming trap (1024-2112 samples, 21-44 ms, in players that ignore
     edit lists) was unmentioned and bites more often than the frame-origin trap. Verification
     moved to the muxed MP4 in the target player.
182. **CORRECTION** — the reverse-swell length scaled to an arbitrary 0.4-1.0 s rather than to a
     bar of the bed's own meter (1.6 s at 150 BPM).
183-187. **CORRECTIONS, previously absent entirely** — stereo panning from `cx` (the cheapest
     realism gain available and the bed already pans its ticks); shared seeded reverb on
     impact/sub-drop/shimmer tails (dry synthetic transients over a reverberant bed read as
     pasted on); the **pre-hit drop**, the single most-used trailer device, present in the
     document's own reference material and never named; per-instance variation from the cue
     index; and the mono/small-speaker fold-down check.

*Also added:* exit sounds (the reverse whoosh that pairs with a push), silence as a
deliverable decision (the silent open, the ringing tail, whether container length follows),
frame-rate-specific placement stated in ms first, a §7b naming what the document still does
not cover (bed hit points and music editing; practitioner citations for the mapping itself),
and an explicit note that the §4.9 smoke test proves the functions run and are seeded, not
that they sound right.

---

## `grading-rubric.md` — 37 items (18 corrections, 19 downgrades)

188. **CORRECTION** — C6's energetic overshoot is quoted as 0-10 % where its own cited source
     says 20-30 %. Raised to 15-30 %.
189. **CORRECTION** — C6's "premium = 0 % and 0 reversals" fails the LottieFiles table's own
     Apple Spring (ζ 0.577, ≈11 % overshoot). Raised to 0-2 % with one reversal.
190. **CORRECTION** — C6's playful budget of one reversal fails the source's own "Bouncy"
     preset (ζ ≈ 0.44, overshoots of 21 % then 4.6 %). Raised to two.
191. **CORRECTION** — the overshoot denominator was undefined; 10 % of travel and 10 % of
     target are the two registers the table is trying to separate. Defined.
192. **CORRECTION** — C6's P-channel fallback (ink count) is blind to positional overshoot,
     which is the most common amateur overshoot. Centroid tracking added.
193. **CORRECTION** — C4's `leadMs` (100-300 ms after every cut) contradicts C17's definition
     of a designed handoff, so a piece could not score S on both. Scoped to the first beat.
194. **CORRECTION** — C18 penalises late sound and never early sound, the opposite of the ITU
     figures it quotes. C band now fires on both sides, asymmetrically.
195. **CORRECTION** — C17's 5 % velocity tolerance fails the HyperFrames preset it came from by
     13× (909 px/s against 300 px/s). Replaced with direction continuity plus a 30 %-of-peak
     floor.
196. **CORRECTION** — the band-point claim "one C costs more than two Bs" is arithmetically
     false: from S, one C costs 70 and two Bs cost 70, exactly equal.
197. **DOWNGRADE** — C11's "1/3 screen rule" promoted a **container**-scoped UI rule to a
     frame-scoped one and then tagged it CRITICAL at weight 2. Scoped to in-scene repositions,
     transitions exempt by class, weight dropped to 1.
198. **DOWNGRADE** — the whole timing/distance/concurrency/lag/arc apparatus is from a skill
     whose own `SKILL.md` scopes it to "buttons, cards, modals, page transitions". Scoped
     criterion by criterion.
199. **DOWNGRADE** — C16's hue-bin count rests on the 60-30-10 rule, an interior-decorating
     proportion heuristic. Replaced with palette adherence (ΔE2000 within 8 of a declared entry).
200. **DOWNGRADE** — C15 applies Netflix subtitle limits to kinetic display type, which is RSVP
     reading at the point of gaze. Split into two models by role.
201. **DOWNGRADE** — C10's `cv_beat >= 0.18` is generalised from one film and fails a piece cut
     to a bar grid. Bar-multiple alternative added.
202. **DOWNGRADE** — six detector gates marked as tuning parameters rather than thresholds.
203. **DOWNGRADE** — the "stagger over 500 ms" entry removed from the quoted CRITICAL list: it
     is a UI figure the rubric enforces nowhere, and the manifesto's own Apple cascade runs
     about 2 s for three words.
204. **CORRECTION** — C1 classified from the **parsed ease**, which under a nesting contract is
     not the curve the viewer sees. Changed to measured geometry, which section 4.1 already
     dumps.
205. **CORRECTION** — C1's class table has no evaluation order, and `back.out(1.7)` satisfies
     the `out` rule, so every overshoot files as `out` and `overshootShare` reads zero.
     Overshoot now tested first.
206. **CORRECTION** — C1 fails small-amplitude recede exits and undeclared ambient (an 8 s
     `scale 1 → 1.04` with `ease: "none"` was a CRITICAL fail). Both exempted.
207. **CORRECTION** — C2 counted `power1..4` as four families and every function ease or
     CustomEase as one, so a piece built the way the rubric's own Marriott citation recommends
     scores band C. Changed to shape clustering.
208. **CORRECTION** — C2's piece-wide `topShare` ceiling rewards ease salad while the rubric's
     own `troubleshooting.md` prescribes standardising per motion type. Changed to per-role.
209. **CORRECTION** — C2 required `overshootShare = 0` for S while C6 allowed corporate 0-5 %.
     Delegated to C6.
210. **DOWNGRADE** — C3's ambient exclusion sat exactly on the boundary of the commonest correct
     case (a `scale 1.04` Ken Burns is 2.0 % of frame width). Replaced with the class-based
     definition.
211. **CORRECTION** — C3 now grades only unmotivated simultaneity: declared groups count as one
     element, declared audio hits are exempt.
212. **CORRECTION** — C4's `holdRatio` fences fail continuous-camera pieces at one end and
     hard-cut kinetic typography at the other. Made genre-parameterised, with mechanical and
     looping elements excluded from the stillness test.
213. **CORRECTION** — C5 removed as a gate and rewritten as frame integrity. As written it
     gated out animation on twos, posterised time, deliberate freezes and end cards; flagged
     correct ambient drift as dead (0.1 px/frame at the 640×360 decode); and its cheapest
     defeat was per-frame grain.
214. **CORRECTION** — C7 inverted to N/A-unless-organic. An 80 % arc rate on type produces the
     swoop, and the corporate residual band is inside antialiasing noise at 640×360.
215. **CORRECTION** — C8 now grades declared pairs only; `lockedRate` reported, not banded.
     Rigid parenting is the null-and-parent workflow, and `reactRate = 1.0` forces decoration.
216. **CORRECTION** — C9 register-gated: `narrative-structure.md` gives corporate anticipation
     as "Minimal/none", so a corporate piece following the source scored C. The context-dim
     detector removed (it is staging, and admitting it made the criterion measure nothing).
217. **CORRECTION** — the C9/C11 contradiction named and resolved: the same 1/3-frame move was
     simultaneously the class that must be wound up and the class that must not exist.
218. **CORRECTION** — C11's Spearman `rho` is negative by design across a professional piece
     (big moves are fast, small moves are slow). Scoped to entrance moves.
219. **CORRECTION** — C12 is as brand-dependent as the centroid checks the rubric demoted:
     `nSizes = 1` is canonical Swiss/Bass work, `weightSpan >= 300` is unreachable in half the
     bundled faces, and its A band (24 px) contradicts its C band (18 px) and its own cited
     source (18-24 px labels). Changed to type-scale adherence plus a size floor.
220. **CORRECTION** — C13's mean-ground-over-bbox over-reports contrast on gradients and
     footage. Tiled, 10th percentile, with APCA reported as advisory.
221. **CORRECTION** — C14 removed as a gate for non-broadcast delivery, and its ink definition
     fixed: `|luma − frame median| > 28` makes any full-bleed panel or edge band fail
     action-safe on every frame. Cropped hero type declared by element.
222. **CORRECTION** — C15's 4-frame slam floor raised to 8 frames; 133 ms is recognition, not
     reading, and sits near flash territory.
223. **CORRECTION** — C17's "fade-out, gap, fade-in = undesigned" bans a standard device that
     the rubric's own transition source lists and that the measured reference uses as its
     rhythm. Redefined as cadence-consistency.
224. **CORRECTION** — C18's loudness target came from one film. Now filled from a `delivery`
     enum with published targets, and an undeclared delivery fails the gate.
225. **CORRECTION** — C18 gated on sample peak (`volumedetect`) while every cited standard
     specifies dBTP, and the script already runs `ebur128=peak=true`.
226. **CORRECTION** — C18's locked window centred on zero reads a professionally cut piece as
     systematically one frame late, and `hitRate` against every strong onset demands a cut
     every 0.8 s. Both fixed.
227-230. **CORRECTIONS, new criteria** — C19 reveal craft and motion blur (opacity-only entrances
     are CRITICAL in the rubric's own source and were measured nowhere, because section 4.2
     excludes paint moves from every test; motion blur was a sub-metric buried in C11); C20
     photosensitive flash, **added as a gate**; C21 restraint and motion density (nothing capped
     technique presence, so an over-animated piece outscored a restrained one); C22 framing and
     layout (18 criteria and none of layout, though the rect track is already dumped); C23
     encode and delivery QC; C24 eye-trace and screen direction.
231. **CORRECTION** — gates and weights reworked: gates carry weight 0 (a gate already caps the
     grade, so double-counting destroys `W` as a craft signal), C5 and C14 removed as gates,
     C20 and the C23 duration half added; S redefined as "every **applicable** criterion at S
     or N/A"; the Motion Awards percentage comparison removed; the declaration budget added to
     the report; and the scope limit for tonal and footage-led pieces stated.

---

## Claims that were checked and survived

Not exhaustive, but worth recording so they are not re-litigated. All local skill citations in
all six documents resolve to real files that say what is claimed. Every GSAP documentation
quote is verbatim correct. The MDN `transform-box` values, the DockYard and svg-tutorial SVG
transform quotes, the Netflix and BBC caption figures, the CMU UIST 2002 and DIS 2006 quotes
and statistics (to the decimal), the SMPTE 93 %/90 % figures, the Kreatli platform bands, the
Bloop blink counts, the Animation Apprentice blink rules, the handwiki Thomas and Johnston page
numbers (bar one), the Animator Island physics figures, the Williams walk quotes across three
student pages, the smear-frame taxonomy, the cg-wire shape-language quotes, and the manifesto
library entry's frame counts, BPM, gap runs and mechanics table are all accurate as quoted.

The arithmetic that could be recomputed is almost entirely correct: the `back.out(s)` overshoot
and reversal formulas, the damped-spring overshoot table, the power-family front-loading and
peak/average velocity figures, the jump recipe's `g` and `v0`, the walk verification frames, the
t90 fractions, the cascade algebra, and every row of the frames-to-seconds tables.

And the epistemic apparatus in all six documents — the `[source]` / `[measured]` / `[inference]`
convention, the refusal to promote an inference to a canonical figure, the explicit lists of
sources that could not be fetched — is what made this audit possible at all. The corrections
above are almost all cases where that discipline slipped in one place, not cases where it was
absent.
