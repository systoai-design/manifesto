# A measurable grading rubric for an original motion graphic

Status: research reference for the `manifesto` skill. Every number below carries a
stated basis. "Inference" means the figure is this document's own reasoning and must
not be quoted as a canonical industry value.

Scope: a rendered MP4 plus its HyperFrames composition source (one paused GSAP
timeline, `fromTo` tweens with explicit from-states, transform and paint-only
properties, deterministic, seek-safe). The rubric assumes both are available. Where
only the render exists, each criterion says what degrades.

Contents

1. How professionals judge motion graphics
2. The recognised amateur tells, and which criterion catches each
3. What `grade-original.py` already checks, and what survives without a voiceover
4. Measurement channels and shared definitions
5. The rubric: 18 criteria with S / A / B / C bands
6. Overall scoring
7. Script outline (inputs, pipeline, output schema)
8. Sources

---

**Revision 2 (2026-09-02).** Corrected against a practitioner review. Five problems ran
through the whole rubric and are fixed criterion by criterion below: UI micro-interaction
figures were applied as motion-graphics standards; technique *presence* was scored and
restraint never was; several criteria were register-blind where the sources are
register-aware; four thresholds contradicted the sources they cite or each other; and two
of the four gates would gate out professional choices. Three new criteria have been added
(motion blur, restraint, photosensitivity as a gate) and two gates removed. Every change is
in `corrections.md` in this directory.

**One thing to state before the criteria.** An A on this rubric means **no visible defect**.
It does not mean good. Concept, script, art direction, brand fit and originality are
unmeasured here, and a piece can pass every criterion and still be the wrong film. Section 1
says clarity and originality are editorial and outside the rubric; that sentence is
load-bearing and should be read before the word "shippable" below.

## 1. How professionals judge motion graphics

### Motion Awards (Motionographer)

Judges score each entry 1 to 10 on three criteria, "the three C's" (2024 FAQ,
https://2024.motionawards.com/faq/ ; current FAQ https://motionawards.com/faq.html):

- Craftsmanship: "Is the project immaculately crafted? Does the project have a
  distinctive point of view? Does the project use novel techniques or push existing
  techniques in a new direction?"
- Clarity of messaging / impact: does it "achieve its intended goal and/or
  communicate its message clearly"; does it "elicit a strong emotional or
  intellectual response".
- Creativeness / originality: "How original is the piece? Does it stand apart?"

The FAQ states plainly: "Above all else, The Motion Awards is a celebration of
craft." Entries advance from the shortlist with "an average score of 7.0 or higher"
and a top-N placing in category (top 10 in the 2024 rules; the 2025 FAQ as indexed
by search says top 5). Only Craftsmanship is measurable from frames; clarity and
originality are editorial and stay outside this rubric.

### Vimeo Staff Picks

Four tenets, from the curators' own post
(https://vimeo.com/blog/post/how-to-get-a-vimeo-staff-pick):

- Originality: "How unique is the style and story?"
- Exceptional craft: "Does it look and sound amazing? Does it innovate and push the
  medium?"
- Engaging storytelling: "Does the film pull us in?"
- Diverse perspectives.

Selection is by human majority vote, never algorithmic. The craft tenet explicitly
pairs picture with sound, which is why audio sync is a criterion here and not an
optional extra.

### D&AD, Animation category

"Judges will prioritise craft over idea in this category."
(https://www.dandad.org/awards/d-ad-awards/categories-2025/animation). The general
D&AD craft questions as reported by LBBOnline for the 2019 criteria: is it
brilliantly crafted, does the craft elevate the idea, is it fit for purpose
(https://lbbonline.com/news/dad-awards-2019-judging-criteria-announced).

### Reviewer checklists

School of Motion, "Common 2D Character Animation Mistakes to Avoid"
(https://schoolofmotion.com/blog/new-to-2d-character-animation-here-are-the-most-common-mistakes-and-how-to-avoid-them)
names seven: ignoring the principles of animation; stiff, symmetrical poses;
letting characters float instead of move; over-relying on auto-keyframe and linear
interpolation; animating everything all at once; neglecting secondary motion and
follow-through; bad or no reference. Six of the seven translate directly to abstract motion
graphics. **"Bad or no reference" translates too, and it is the highest-leverage item on
the list**: a studio does not grade a render in a vacuum, it grades it against an approved
style frame and animatic, which is why the stage model exists. The manifest should carry
the approved style frame and the grader should report a frame-to-styleframe delta on the
key frame (palette distance, type scale, layout alignment, weight distribution). Without
it this rubric can certify a piece as defect-free while it is nothing like what was
approved, which is the failure mode that actually costs money.

Ben Marriott, on the biggest skill jump in his own work: going on "a plugin diet",
uninstalling easing plugins and learning "the speed graph and the value graph"
directly (https://elements.envato.com/learn/ben-marriott). The point for a rubric:
professionals treat the shape of the ease curve, not the presence of "easy ease", as
the craft.

The LottieFiles motion-design skill (MIT, (c) LottieFiles) supplies severity tiers
that this rubric reuses for weighting
(`<skills>/motion-design/reference/quality-checklist.md`):

- CRITICAL: linear easing on spatial movement; opacity-only for important states;
  exceeds the 1/3 screen rule; missing primary layer; layout property animation.
  (**The "stagger over 500 ms" entry has been dropped from this quote.** It is a UI figure
  and the rubric does not enforce it in any criterion; leaving it in the CRITICAL list
  invited a builder to apply it to a title cascade that legitimately runs one to three
  seconds. The manifesto skill's own Apple cascade recipe runs about 2 s for three words.
  Note also that **"opacity-only for important states" is CRITICAL in the source and is
  measured by no criterion in this rubric** -- see C19 below, which fixes that.)
- HIGH: missing secondary layer; duration mismatch with element type; wrong
  directional easing; inconsistent personality; no follow-through.
- MEDIUM: missing ambient layer; no anticipation phase; overshoot mismatch; could
  use better arcs; missing counter-motion.

The HyperFrames creative references (Apache-2.0, (c) HeyGen) add the guardrails an
author most often violates
(`<skills>/hyperframes-creative/references/motion-principles.md`):
same ease on every tween; same speed on everything ("the slowest scene should be 3x
slower than the fastest"); everything entering from the same direction; same stagger
every scene; ambient zoom on every scene; starting at t=0. And from
`gsap-easing-and-stagger.md` in the animation skill: "One ease everywhere reads flat;
bounce everywhere reads cheap; the second failure is worse." From
`rules/spring-pop-entrance.md`: bouncy `back.out` "is the #1 instant turn-off in
agent-made videos".

---

## 2. The recognised amateur tells

| Tell | Named by | Criterion below |
| --- | --- | --- |
| Linear easing on spatial moves | School of Motion mistake 4; LottieFiles CRITICAL; Disney principle 6 | C1 |
| Mismatched or backwards eases (ease-in entrances, ease-out exits) | LottieFiles HIGH "wrong directional easing"; HyperFrames motion-principles | C1 |
| One ease everywhere / bounce everywhere | HyperFrames guardrails; gsap-easing adapter | C2 |
| Everything moving at once | School of Motion mistake 5; LottieFiles 1/3 rule | C3 |
| No holds, nothing breathes | LottieFiles choreography "100-200 ms stillness"; HyperFrames build/breathe/resolve | C4 |
| Dead frames, static holds that read as a stall | `grade-original.py` check 1; moving-hold principle (Pluralsight 12 principles) | C5 |
| Floaty, weightless motion; overshoot on everything or double bounces | School of Motion mistake 3; LottieFiles overshoot budget; spring-pop rule | C6, C11 |
| Straight, mechanical paths where the register is organic | Disney principle 7 (arcs); LottieFiles MEDIUM | C7 |
| No secondary motion, no follow-through | School of Motion mistake 6; LottieFiles HIGH | C8 |
| No anticipation | Disney principle 2; LottieFiles MEDIUM | C9 |
| No rhythm contrast, metronome cutting | `grade-original.py` check 9; HyperFrames "3x" rule | C10 |
| Duration unrelated to distance; strobing edges | LottieFiles distance-duration table; manifesto shutter section | C11 |
| No type hierarchy | `grade-original.py` check 6; HyperFrames typography | C12 |
| Text unreadable (contrast) | WCAG 1.4.3; `grade-original.py` check 3 | C13 |
| Type running off frame | SMPTE ST 2046-1; `grade-original.py` check 2 | C14 |
| Text on screen too briefly | Netflix timed-text limits; HyperFrames "3 s on screen = readable in 2" | C15 |
| Muddy or rainbow palette, flat frames | 60-30-10 rule; HyperFrames video-composition | C16 |
| Cuts that are not designed (fade out, black, fade in) | HyperFrames transitions overview rule 3 | C17 |
| Silent cuts, hits off the beat | Vimeo "sound amazing"; EBU R37; ITU-R BT.1359 | C18 |

---

## 3. What `grade-original.py` already checks

Source: `<skill>/scripts/grade-original.py`. Sixteen pass/fail
checks, reported as a percentage and a letter (A = 100 %, B >= 90 %, C >= 80 %, else
D). Frames are sampled every third frame at 640x360 grey and RGB.

| # | Group | Check | Threshold | Needs VO? | Notes for a no-VO piece |
| --- | --- | --- | --- | --- | --- |
| 1 | FRAME | duplicate consecutive frames (`mpdecimate hi=lo=1 frac=1`) | 0 | no | keep; see C5 |
| 2 | LEGIBILITY | frames with ink inside a 4 % edge margin, exempt by name | 0 | no | keep; C14 moves to SMPTE 5 % / 3.5 % |
| 3 | LEGIBILITY | worst type/ground WCAG contrast on settled frames (core mask delta > 70) | >= 3.0:1 | no (settled windows come from `beats.ts`) | keep; C13 |
| 4 | COMPOSITION | vertical centroid spread (sd) | >= 0.090 | no | keep as a composition probe (not in this rubric's 18; see note) |
| 5 | COMPOSITION | frames with centroid in the middle vertical third | <= 85 % | no | same |
| 6 | TYPE | distinct font sizes in the timeline | >= 3 | no | keep; C12 |
| 7 | CONTINUITY | spoken beats whose middle renders an empty frame | 0 | yes (`vo-timing.json`) | re-base on composition beats: any worded beat with `occ < 0.30` mid-beat |
| 8 | MOTION | settle direction reversals (ink count, segmented on re-triggers, smoothed) | 0 | no | keep; C6 generalises it to a register budget |
| 9 | MOTION | beat-length variation (cv) over worded beats | >= 0.18 | no | keep; C10 |
| 10 | AUDIO | integrated loudness | -17.0 to -15.0 LUFS | no | applies to any audio track; C18 gate |
| 11 | AUDIO | peak | <= -1.0 dBFS | no | applies to any audio track; C18 gate |
| 12 | AUDIO | sidechain duck depth | <= 6.0 dB | yes | not applicable |
| 13 | AUDIO | music below voice | 6.0 to 14.0 dB | yes | not applicable |
| 14 | AUDIO | per-line read level spread | <= 3.0 dB | yes | not applicable |
| 15 | AUDIO | music floor inside the blackout | <= -60 dB | no, film-specific | only if the piece declares a silence window |
| 16 | SYNC | lines with nothing on screen 6 samples after line start | 0 | yes | not applicable; C18 replaces it with onset alignment |

Eleven checks survive with no voiceover (1 to 6, 8 to 11, and 15 when a silence
window is declared). Four are voice-only (12, 13, 14, 16). Check 7 survives if its
beat list is taken from the composition instead of the VO timing file.

Four method lessons from that script carry into every criterion below, verbatim in
spirit (SKILL.md, "Grading an ORIGINAL film"): grade contrast at the large-text
threshold; measure legibility only while type is settled; overshoot is a direction
reversal, not movement; never measure motion on a bounding box, use an integral (ink
count) and smooth it because per-frame grain manufactures reversals.

Note on checks 4 and 5: they encode one film's composition rule (do not sit
everything at the same height). They are worth keeping as a report line but are not
promoted to a graded criterion here because the right value is brand-dependent.

---

## 4. Measurement channels and shared definitions

### 4.1 Two channels

**Source channel (S).** Because the HyperFrames contract makes state a pure function
of timeline time (`rules-index.md`, "The contract"), the composition can be probed
exactly. Load the composition in a headless browser, wait for `document.fonts.ready`,
take `tl = window.__timelines[0]`, and for every frame `f` call `tl.pause();
tl.seek(f / fps)`. For every element that is a target of any tween, record:

- centre `(cx, cy)`, width, height from `getBoundingClientRect()` (includes transforms)
- `gsap.getProperty(el, p)` for `x, y, xPercent, yPercent, scale, scaleX, scaleY,
  rotation, opacity`
- computed `filter`, `clip-path`, `color`, `background-color`, `font-size`,
  `font-weight`, `visibility`
- text content length (characters, excluding whitespace)

Also dump the tween table once: `tl.getChildren(true, true, false)` and for each
tween its absolute start (walk `parent` and sum `startTime()`), `duration()`,
`vars.ease` (string) or a 101-point sample of the parsed ease (`tw._ease(p)` for `p`
in 0..1) when it is a function, `targets()`, the property keys in `vars`, and
`vars.startAt` (the `fromTo` from-state). A staggered call yields one tween per
target, so onsets are already per element.

**Pixel channel (P).** Decode the render at full frame rate (not every third frame;
onset and dead-frame tests need every frame) at 640x360 grey plus RGB, exactly as
`grade-original.py` does but with `every = 1`. Per frame: ground luma (median), ink
mask (`|luma - ground| > 28`), core mask (`> 70`), ink count, centroid, edge band,
column and row ink profiles, plus connected components with area >= 40 px (at 640
wide). Elements are tracked across frames by nearest-centroid matching with an area
ratio gate of 0.5 to 2.0 (inference: a component that doubles in one frame is a
different component).

Every criterion states which channel it prefers. When only P exists, criteria C8 and
C9 report at reduced confidence and C2 falls back to curve fitting.

### 4.2 Shared definitions

- **fps**: from `ffprobe` `avg_frame_rate`. One frame = 1000 / fps ms. At 30 fps,
  "within 1 frame" = 33 ms; at 60 fps, 17 ms.
- **Move**: one tween on a spatial property (`x, y, xPercent, yPercent, scale*,
  rotation, clip-path`) with duration >= 2 frames. Opacity-only and filter-only
  tweens are **paint moves** and are excluded from ease-direction, arc and
  distance tests but included in onset tests.
- **Beat**: the interval between consecutive cuts. Cuts come from the manifest when
  declared, otherwise from the blank-run and column-profile model in
  `segment.mjs` (SKILL.md section 3.2).
- **Onset** of a move: the first frame where normalised progress `s(t) >= 0.02`
  (S channel: from the tween start; P channel: from the tracked centroid or ink
  count). **Settle**: the first frame after which `|s - 1| < 0.005` for the rest of
  the tween.
- **Progress curve** `s(t)`: displacement from the from-state divided by total
  travel, sampled per frame, for the dominant property of the move (the one with the
  largest normalised travel).
- **Hero move**: in each beat, the move on the element with the largest ink area
  at settle, or the element named `hero` in the manifest.
- **Settled window** of a text element: from its entrance settle to the onset of its
  exit tween (or the cut). Legibility is measured only inside this window
  (`grade-original.py`, check 3 comment).
- **Register**: one of `premium | corporate | playful | energetic`, declared in the
  manifest. It parameterises C6, C7 and C9 the way the LottieFiles personality tables
  do. Undeclared register defaults to `corporate` (inference: the middle of the
  tables). **Better than an archetype, where the brief supports it: a declared MOTION
  SYSTEM** -- signature ease, duration scale, primary transition, stagger step, ambient
  device -- graded for adherence to itself rather than conformance to a generic
  personality. That is the actual professional QC question ("is this consistent with
  itself and with the brand's motion language", not "is this playful enough"), and it is
  measurable: cluster moves by role and element class and check duration cv and ease
  identity within each cluster. Nothing in this rubric currently checks that all card
  entrances in a piece share a duration, an ease and a direction, which is the first note
  a lead animator writes on any reel.
- **Ambient**, defined once here because three criteria previously defined it three
  different ways: any tween with duration >= 2 s **and** travel < 5 % of frame. C3 used an
  amplitude test, C4 used the word without defining it, and C5 recognised ambient only
  inside a declared hold, which guaranteed that the same tween was ambient for one
  criterion and primary for another and made the aggregate non-reproducible. (Inference;
  consistent with the LottieFiles ambient band of 2000-20000 ms and "10-20 % amplitude".)
- **Delivery**: one of `broadcast | web | social`, declared in the manifest. It
  parameterises C14 and C18. There is no sensible default; an undeclared delivery fails
  the C18 delivery gate rather than inheriting one film's window.
- **Scope limit, stated once.** Every P-channel metric here is calibrated to a
  high-contrast graphic register: ink is `|luma - ground| > 28` and core is `> 70`. A
  tonal or photographic piece (charcoal on black, layered greys, footage-led work)
  registers almost no ink, and C3 concurrency, C5, C14 and C16 then quietly mis-measure
  rather than fail loudly. Raise a confidence flag when frame-wide ink coverage is below a
  floor, or declare the rubric out of scope for footage-led pieces.

### 4.3 The manifest (`grade.json`)

Exemptions are declared by name, never by loosening a threshold, following the
pattern in `grade-original.py` (flips, `through`, `s1-split` exempted by beat name):

```json
{
  "fps": 30,
  "register": "premium",
  "silent": false,
  "cuts": [0, 42, 97, 140],
  "holds": [{ "from": 60, "to": 96, "ambient": "#glow" }],
  "fullBleed": [{ "from": 40, "to": 46, "why": "iris wipe" }],
  "mechanical": ["#progress-ring", "#counter"],
  "hero": { "1": "#h1", "2": "#h2" },
  "secondaryPairs": [{ "parent": "#card", "child": "#shadow" }],
  "onBeatHardCuts": [97],
  "footageRegions": [],
  "loudnessTarget": [-17, -15]
}
```

Frame numbers are integers at the authoring fps. Anything not declared is measured
at full strictness.

**Declaration budget.** Exemption-by-name is the right discipline, but every hard criterion
here has a declaration escape (`mechanical`, `fullBleed`, `holds`, `onBeatHardCuts`,
`silent`, `footageRegions`, `secondaryPairs`, `hero`, `delivery`) and the author of the
piece writes the manifest, so an agent optimising for the grade can declare its way to A at
zero cost. The report must therefore print, at the top: **the number of declarations, and
the number of criteria whose band improved because of one.** Flag any piece whose pass
depends on more than a small number. A declaration is a claim about intent and should be
visible as one. (This is why broadcast QC separates the operator from the deliverable.)

---

## 5. The rubric

Each criterion gives: what is measured, how, the bands, and the basis. Bands are
S (exemplary), A (professional), B (competent with visible faults), C (amateur tell
present). Where a criterion cannot apply (for example C7 on a declared mechanical
piece), it is marked N/A and removed from the weighted total.

### C1. Ease discipline (no linear on spatial moves; correct direction)

**Measure.** For every move, classify its progress curve and its role.

**Classify from the measured per-frame geometry, not from the ease attached to the tween.**
Use the rect and `getProperty` track section 4.1 already dumps, build `s(t)` from on-screen
displacement, and keep the ease string only as a report label. Under the HyperFrames
contract a clip wrapper, a parent group and a child can each carry a tween, and the curve
the viewer sees is the composition of all of them plus any `timeScale` on the parent
timeline. A child with `ease: "none"` inside a parent with `power2.out` is not linear on
screen; a child with `power2.out` inside a linearly moving parent is not an ease-out on
screen. Classifying from the parsed ease fails the first (CRITICAL, band C) and passes the
second. The correct measurement is already available and is cheaper than parsing eases.

**Evaluate `overshoot` FIRST.** `back.out(1.7)` has `s(0.5) = 1.0875` and `s(0.25) = 0.406`,
which satisfies the `out` rule, so a top-to-bottom table walk files every `back.out` under
`out`, `overshootShare` in C2 reads zero, and the single tell the sources call "the #1
instant turn-off in agent-made videos" is invisible to the criterion built to catch it.

Classification from `s(t)` at quarter points:

| Class | Rule | Reference values |
| --- | --- | --- |
| linear | `|s(0.25)-0.25| < 0.05` and `|s(0.5)-0.5| < 0.05` and `|s(0.75)-0.75| < 0.05` | `none`: exactly 0.25 / 0.5 / 0.75 |
| out | `s(0.5) >= 0.60` and `s(0.25) >= 0.35` | `power1.out` 0.75; `power2.out` 0.875; `sine.out` 0.707 at `s(0.5)` |
| in | `s(0.5) <= 0.40` | `power1.in` 0.25; `sine.in` 0.293 |
| inOut | `|s(0.5)-0.5| <= 0.10` and `s(0.25) <= 0.20` and `s(0.75) >= 0.80` | `power1.inOut` 0.125 / 0.875; `sine.inOut` 0.146 / 0.854 |
| overshoot | `max s(t) > 1.005` or any sign change in the smoothed derivative before settle | `back.out(1.7)` peaks near 1.10 |
| custom | anything else | report, do not fail |

Reference values are computed from the GSAP definitions (`power N.out = 1 - (1-p)^(N+1)`,
`powerN.in = p^(N+1)`, sine variants from `sin`/`cos` of `p * pi/2`). Family list
from `<skills>/hyperframes-animation/adapters/gsap-easing-and-stagger.md`.
The 0.05 / 0.10 tolerances are inference, chosen so `sine` and `power1` land on the
right side of every boundary.

Role: **entrance** if the element's opacity rises from 0 or its from-state centre is
outside the frame or its from-state scale is 0; **exit** if the reverse; **reposition**
otherwise. Rule: entrance must be `out` (or `overshoot` where C6 allows it); exit must
be `in`; reposition must be `inOut` or `out`.

**Two exemptions from the direction test, both of which the earlier revision failed.**
(a) **Small-amplitude recedes.** A premium exit is commonly `scale 1 -> 0.96` plus fade plus
blur on an `out` or `inOut` ease, which reads as sinking away rather than being thrown; the
ease-in rule is right for exits that *leave the frame* and wrong for these. Exempt exits
whose spatial travel is under 5 % of scale or 3 % of frame height (inference).
(b) **Ambient auto-classification.** Any tween meeting the ambient definition in 4.2
(duration >= 2 s, travel < 5 % of frame) is ambient and exempt **without a declaration**.
As written, an undeclared 8 s `scale 1 -> 1.04` Ken Burns with `ease: "none"` is a CRITICAL
fail, and that is the single most common correct thing in the medium.

**A source conflict worth flagging to the builder.** `motion-principles.md`'s "GOOD option
A" combines a `y: 50, opacity: 0` entrance with a Ken Burns in one tween at `ease: "none"`.
Under C1 that entrance is linear on a spatial move, band C. C1 is right and the snippet is
not: option B (parent entrance, child Ken Burns) is the professional build. Say so here,
because a builder following the HyperFrames reference will otherwise write option A and
fail.

Linear is allowed on elements listed under `mechanical` (rotation loops, progress, counters, camera drift with
counterpoint), which matches the LottieFiles rule "Linear only for: rotation,
progress bars, timers" and the GSAP adapter's "camera moves with timed counterpoint,
mechanical motion".

Metrics: `L` = linear moves on non-mechanical elements; `D` = direction violations;
`M` = total moves; `dRate = D / M`.

| Band | Threshold |
| --- | --- |
| S | `L = 0` and `D = 0` |
| A | `L = 0` and `dRate <= 0.05` |
| B | `L = 0` and `dRate <= 0.15` |
| C | `L >= 1`, or `dRate > 0.15`, or a direction violation on any hero entrance |

Basis: LottieFiles quality-checklist (linear on spatial = CRITICAL, hence any
occurrence is C; wrong directional easing = HIGH, hence rate-based);
`disney-principles.md` principle 6 ("NEVER linear for spatial movement");
`motion-principles.md` direction rules. The 5 % / 15 % rates are inference.

### C2. Ease vocabulary (variety without bounce spam)

**Measure ease diversity PER ROLE, and count by curve SHAPE, not by ease name.**

Two changes from the earlier revision, both of which inverted what the criterion rewarded.

**(a) Count clusters of sampled shape on both channels**, not distinct ease strings.
Cluster the `(s(0.25), s(0.5), s(0.75))` triple plus peak overshoot at radius 0.06
(inference, deliberately wider than the 0.04 used on the P channel so adjacent power grades
merge). On screen `power2.out` and `power3.out` differ by two or three frames of settle and
do not read as two characters, so a name-based count is inflatable by an author who does
nothing; worse, a piece built the way this rubric's own Ben Marriott citation recommends
(hand-shaped speed graphs, no named presets) reports `families = 1` and scores band C,
which punishes exactly the practice section 1 holds up as the craft.

**(b) Grade consistency within a role and variety across roles.** `troubleshooting.md`,
cited elsewhere in this rubric, prescribes "Mixed archetypes -> pick one for 90 %+" for "No
personality" and "Different easing same-type -> standardize per motion type" for
"Inconsistent feel". A brand motion system is a signature ease on most tweens plus one or
two role variants, so a piece-wide `topShare` ceiling rewards ease salad and the source
rewards consistency. **S = one ease consistently within each role (hero, support, ambient,
exit) and distinct eases across roles; C = the same ease on hero, secondary and ambient at
once. Report `topShare` as a line; do not band it.**

`overshootShare` = share of moves classified `overshoot` in C1 (evaluated first, per the
note there).

| Band | Threshold |
| --- | --- |
| S | one ease shape per role, distinct across roles; shape clusters >= 3 across the piece; overshoot within the C6 register budget |
| A | shape clusters >= 3; at most one role using two shapes; overshoot within the C6 budget |
| B | shape clusters = 2 |
| C | shape clusters = 1, or the same ease on hero, secondary and ambient simultaneously, or **overshoot on any opacity or colour tween** |

The overshoot condition is delegated to C6 rather than duplicated here: the earlier revision
required `overshootShare = 0` for S in non-playful registers while C6 allowed corporate
0-5 %, so the two criteria contradicted each other and a standard 3 % `back.out(1.2)` settle
on a corporate CTA could not reach S. The only overshoot test that stays in C2 is the
paint-property one, which is absolute.

Basis: `techniques.md` "Every composition should use at least 3 different easings";
`gsap-easing-and-stagger.md` "a composition should draw on ~3 easing characters",
"bounce everywhere reads cheap", and "at zeta < 1, overshooting curves go on
transforms only, never on opacity"; `motion-principles.md` "no more than 2
independent tweens with the same ease in a scene". Share percentages are inference.

### C3. Simultaneity index and concurrency

**Measure.** Per beat with >= 3 animated elements (the LottieFiles rule applies
"with 3+ animated elements"):

- Onset clusters: group move onsets that fall within +/- 1 frame of each other.
  `SI` = (size of the largest cluster) / (onsets in the beat). Onsets belonging to a
  single stagger call are already distinct, so a `stagger: 0.08` group does not
  trip this; a group that starts on the same frame does.
- Concurrency: per frame, `active` = elements whose progress `0.02 < s < 0.98`;
  `conc` = max over the beat of `active / animatedElementsInBeat`. **Exclude any tween
  classified ambient by the 4.2 definition (duration >= 2 s, travel < 5 % of frame),
  regardless of amplitude.** The earlier 2 %-of-frame-height amplitude test sat exactly on
  the boundary of the commonest correct case: a `scale 1 -> 1.04` Ken Burns on a 1920 frame
  moves the edge 38 px, which is 2.0 % of width, so the exclusion fired or did not depending
  on rounding.
- **Grade only UNMOTIVATED simultaneity.** Elements inside one `.clip` sub-group or one
  declared lockup count as **one** element for the onset census, and same-frame starts that
  land on a declared audio hit are exempt. A logo lockup resolving as one unit, a grid
  landing together on the downbeat and a slam on a hit are professional, and the last of
  those is the point of cutting to music, which C18 separately rewards. The LottieFiles
  1/3 rule is a UI density rule for 3+ interactive elements and its own `SKILL.md` scopes
  the skill to "buttons, cards, modals, page transitions". (Inference for the scoping.)
- Shared-event allowance: a declared trigger group (elements reacting to one event)
  may start "within 50 ms of each other" and count as one onset.

Piece scores: `SI_max`, `conc_max` over beats, and `nBad` = beats with `SI = 1`.

| Band | Threshold |
| --- | --- |
| S | `SI_max <= 0.34` and `conc_max <= 0.34` |
| A | `SI_max <= 0.50` and `conc_max <= 0.50` |
| B | `SI_max <= 0.75` |
| C | any beat with `SI = 1` (everything starts on the same frame), or `conc_max > 0.75` |

Basis: LottieFiles `choreography.md` "With 3+ animated elements, max 1/3 active
simultaneously" and "All start within 50 ms of each other" for shared events;
`quality-checklist.md` "1/3 rule (density)"; School of Motion mistake 5. The 0.50 /
0.75 intermediate bands are inference.

### C4. Hold ratio and breathing room

**Measure.**

- `stillness(b)` per beat: frames between the settle of the last entrance move and
  the earliest exit onset (or cut), during which no non-ambient element is moving.
- `holdRatio(b) = stillness(b) / beatFrames(b)`; piece `holdRatio` = held frames /
  total frames.
- `gapMs`: for every pair (settle of move k, onset of the next non-secondary move on
  the same element or its group), the gap in ms.
- First onset after each cut: `leadMs` = ms from the cut to the first onset in the
  new beat.

| Band | Threshold |
| --- | --- |
| S | every beat `holdRatio(b) >= 0.30`; every `gapMs >= 100`; piece `holdRatio` inside the register/genre band below; `leadMs` in 100 to 300 **on the first beat of the piece only** |
| A | >= 90 % of beats meet the per-beat rules; piece `holdRatio` in 0.25 to 0.65 |
| B | >= 75 % of beats; piece `holdRatio` in 0.15 to 0.80 |
| C | < 75 % of beats, or piece `holdRatio` outside the register/genre band by more than 0.10 |

**Three corrections to this criterion, each of which made it fail correct work.**

**`leadMs` applies to the first beat only.** C17 defines a designed handoff as outgoing and
incoming animating at the same time `T`, which is `leadMs = 0`, so a piece could not score S
on both criteria. The HyperFrames guardrail "Don't start at t=0. Offset the first animation
0.1-0.3s" is about the composition's first frame and its poster frame, not every beat. For
later beats the lead is set by the transition: 0 for hard cuts and velocity-matched
handoffs, one transition duration for dissolves. Optimising for the old rule produces a
piece that stalls for a tenth of a second at every edit point, which is the most visible
amateur cutting fault there is.

**Exclude declared `mechanical` and looping elements from the stillness test, not just
ambient.** A scene carrying a progress ring or a counter never has a frame where nothing
non-ambient moves, so `holdRatio` computes as 0 for the whole piece and the criterion
returns C for a correct build.

**The piece-level fences are register and genre parameterised, not universal.**
`holdRatio < 0.15` is *correct* for a continuous-camera piece (a 3D flight, a sports promo)
and `> 0.80` is *correct* for a hard-cut kinetic typography film, which is the reference the
manifesto skill was proven on. Declare the genre and set the band: continuous-camera 0.05 to
0.35, mixed 0.25 to 0.65, card-based 0.45 to 0.85 (all inference). Count ambient-only frames
as held: they are the moving hold. The 100-200 ms gap rule and the per-beat resolution phase
are sound and stay. Do not grade the 30/40/30 build/breathe/resolve split at all: it is a
HyperFrames default for explainer scenes, and a one-word slam card is 5/90/5 and correct.

Basis: LottieFiles `choreography.md` sequence structure (setup 20-30 %, action
30-40 %, resolution 30-40 %; "Leave 100-200 ms stillness after resolution before new
motion"); HyperFrames `motion-principles.md` build / breathe / resolve (breathe 30-70 %
of the scene, so about 40 %) and "Don't start at t=0. Offset the first animation
0.1-0.3s. Zero-delay feels like a jump cut". The piece-level 0.15 / 0.80 fences and
the percent-of-beats bands are inference.

### C5. Frame integrity (was "dead frames and dead holds"; **no longer a gate**)

**This criterion was the one to dispute hardest as a gate, and it has been rewritten.**
Four reasons the old form was wrong.

**Animation on twos and posterised time are a style, not a defect.** Locking motion to
12 fps inside a 24 fps comp is standard for a hand-drawn or stop-motion look (Adobe, "Using
time effects", https://helpx.adobe.com/after-effects/using/time-effects.html ; Creative COW,
"Animating in 2s"). `mpdecimate` flags every second frame of such a piece.

**Dead-still holds are used deliberately.** A white card with black type held for 1.5 s with
nothing moving is the Apple register, and `motion-principles.md` itself says "Stillness
after motion is powerful". The moving hold is a *character-animation* principle about a held
pose; a graphic card is not a character. Most brand end cards are static for 1.5-3 s.

**The measurement flags correct ambient motion as dead.** Frames are compared at 640x360; a
`scale 1 -> 1.04` over 4 s at 1920 wide moves the frame edge 0.32 px per frame at full size
and 0.1 px at 640 wide, under the 0.25-level threshold. Conversely per-frame grain defeats
the test completely while fixing nothing, and the cheapest way to pass the old gate was to
seed grain per frame, which the rubric rewarded and learned nothing from.

**The real editing defects were not measured.** The classic errors are the 1-frame **flash
frame** (an accidental blank or wrong frame at a cut) and an *inconsistent* gap length
between cards; the old form treated gaps up to 8 frames as rhythm without checking they were
consistent.

**Rewritten measure.** (a) Any 1-2 frame blank or off-palette frame at a cut that is not
part of the piece's declared gap cadence = C. (b) Duplicate runs are judged against a
declared cadence (`posterize: 2` in the manifest makes every 2-frame duplicate correct) and
measured **at full resolution on luma at one code value**, not at 640x360. (c) Declared
freezes (end card, freeze-frame device) are exempt by name. (d) A duplicate run is only an
undeclared stall when the S channel confirms nothing moved either, including ambient, where a
0.1 px drift is visible: a run the composition moved through is the encode quantising a
low-amplitude move out, which is a finding about the deliverable and is reported, not banded.
A stall that survives that test is banded by LENGTH on the table below, where a single run
over 8 frames is C.

An earlier revision of clause (d) read "an undeclared stall longer than 1.5 s ... = B, not C",
which contradicts the C row of the table below and left the criterion with no path at all from
run length to its own worst band: both length terms in the implementation terminated at B, and
a 31-frame frozen picture in an 8 s film graded B. The table wins, the 1.5 s figure is retired,
and 8 frames is the figure that stands (the upper end of the blank-gap runs SKILL.md section
3.2 treats as rhythm).

**Removed from the gates.** What a studio actually treats as a hard fail, and what now
gates instead: photosensitive flash (C20), contrast (C13), true-peak and loudness delivery
(C18), and wrong duration or cadence.

### C5 (original text, retained for the measurement plumbing)

**Measure.** P channel at full rate.

- Duplicate run: `n >= 2` consecutive frames with `mpdecimate=hi=1:lo=1:frac=1`
  reporting a drop, or mean absolute grey difference `< 0.25` levels (inference: a
  single level of dither over 0.25 of the frame would exceed this). Runs inside a
  declared hold whose `ambient` element is present are not dead frames; runs inside
  a declared hold with no ambient are **dead holds** if they last longer than 1.5 s.
- Any duplicate run outside a declared hold is an undeclared stall.

| Band | Threshold |
| --- | --- |
| S | 0 undeclared duplicate runs; 0 dead holds |
| A | <= 1 undeclared run of <= 2 frames; <= 1 dead hold |
| B | <= 3 undeclared runs; <= 2 dead holds |
| C | > 3 undeclared runs, or any run > 8 frames, or > 2 dead holds |

Basis: `grade-original.py` check 1 ("a hold rendered as bit-identical frames reads as
a stall"); the moving-hold principle (Pluralsight, "Understanding 12 Principles of
Animation": a held pose "needs to display some sort of movement ... to prevent the
animation from becoming dead"); HyperFrames `video-composition.md` "Static
decoratives feel dead". The 1.5 s and 8-frame figures are inference; 8 frames is the
upper end of the blank-gap runs `segment.mjs` treats as rhythm (SKILL.md section 3.2).

### C6. Settle quality: overshoot count and amplitude against register

**Measure.** For every move, on the smoothed progress curve (3-frame box on the
S-channel value, or on ink count per `grade-original.py` on the P channel):

- `reversals` = sign changes of the derivative after the first frame where
  `s >= 0.95`, counting only steps larger than 0.5 % of travel (inference; the
  original script uses 2 % of ink count against grain). **On the P channel, track the
  component CENTROID along the move axis for positional overshoot** and keep ink count for
  scale and opacity. Ink count is invariant to translation, so an ink-count fallback is
  blind to `back.out` on a slide, which is the most common amateur overshoot of all;
  `grade-original.py` used ink count because that film's overshoot risk was a squash, which
  is a property of that film and not a method.
- `amplitude` = `max s - 1`, as a percentage of travel.
- Re-triggers (a jump of `> 15 %` upward within a settle window) start a new
  segment, exactly as `grade-original.py` does for the hammer treatment.

Register budget for `amplitude` on transforms:

| Register | Allowed amplitude | Allowed reversals |
| --- | --- | --- |
| premium | 0 to 2 % | <= 1 |
| corporate | 0 to 5 % | <= 1 |
| playful | 15 to 25 % | <= 2 (the second under 5 % of travel) |
| energetic | 15 to 30 % | <= 1 |

**Three corrections to this table.** (a) **Energetic was quoted as 0-10 % against its own
cited source.** `disney-principles.md`'s exaggeration-by-personality table says Energetic
20-30 %, Playful 15-25 %, Corporate 0-5 %, Premium 0 %; the rubric's own basis line
contradicted its own number. Set 15-30 % (inference: the source's 20-30 with the lower edge
relaxed to meet playful). (b) **"Premium = 0 % and 0 reversals" fails Apple's own spring.**
The LottieFiles table lists "Apple Spring: stiffness 300, damping 20" as the iOS interactive
default, which at unit mass is damping ratio 20 / (2 sqrt(300)) = 0.577 and a first
overshoot of exp(-pi 0.577 / sqrt(1 - 0.577^2)) = about 11 % (computed). Premium system
motion is *near*-critically damped, not zero-overshoot; `gsap-easing-and-stagger.md` says
the same ("they barely overshoot, or don't at all"). 0-2 % with at most one reversal.
(c) **The `<= 1` playful budget fails the source's own "bouncy" preset.** LottieFiles
"Bouncy: stiffness 150-250, damping 10-15" is damping ratio about 0.44 at the midpoints,
giving overshoots of about 21 % then 4.6 % (computed): a visible second reversal, played on
purpose. Three or more remains a wobble.

**And define the denominator explicitly**, because the two readings are the two registers
this table is trying to separate: **overshoot % = (peak - target) / (target - start)**, that
is, as a fraction of *travel*. For a scale tween from 0.9 to 1.0, 10 % of travel is scale
1.01 (felt, not seen) and 10 % of the target value is scale 1.10 (cartoon).

Note also that `back.out(n)` and a damped spring are **not interchangeable at matched
overshoot percentages**: `back` has one smooth excursion, a spring has decaying oscillation,
and swapping them changes the read even when the peak matches.

`offRegister` = share of settles outside the budget. Opacity or colour overshoot is
always a violation.

| Band | Threshold |
| --- | --- |
| S | `offRegister = 0`; no settle with `reversals >= 2` |
| A | `offRegister <= 0.05`; no settle with `reversals >= 3` |
| B | `offRegister <= 0.15` |
| C | `offRegister > 0.15`, or any amplitude `> 25 %`, or any `reversals >= 3` (a wobble), or overshoot on opacity |

Basis: LottieFiles `timing-easing-tables.md` overshoot budget (Premium 0 %, Feedback
2-5 %, Success 5-10 %, Celebration 15-25 %) and `disney-principles.md` exaggeration
by personality (Corporate 0-5 %, Playful 15-25 %); `troubleshooting.md` "Playful:
overshoot > 25 % = broken"; `gsap-easing-and-stagger.md` damping table (zeta < 0.55 =
"> 12 %, don't"); `grade-original.py` check 8. The 5 % / 15 % off-register bands are
inference.

### C7. Arc versus line

**N/A unless the manifest declares organic elements** (characters, particles, physical
props), and then it applies only to those. **The default is inverted from the earlier
revision**, which required an 80 % arc rate for S in every register except a declared
mechanical piece. Type, panels, cards, UI and wipes travel in **straight lines** in
professional motion graphics, `disney-principles.md` itself concedes "Mechanical UIs can use
straight paths intentionally", and pushing a builder to bend every headline's path produces
the swoop, a recognisable amateur tell. **Report any arc on a text or card element as a note
("unmotivated arc"), not as a credit.** Weight stays 1.

The measurement is also infeasible at the corporate end as specified: a 0.4 % residual is
4.3 px on a 1080 frame and 1.4 px at a 640x360 decode, inside centroid noise from
antialiasing (the manifesto skill's own note on bounding boxes at 360p applies).

**Measure (for declared organic elements).** For every translation move whose 2D path length
`>= 10 %` of the frame diagonal (inference: shorter moves cannot show an arc at video
resolution): fit a
straight line to the centroid track by least squares; `residual` = maximum
perpendicular deviation as a fraction of frame height. Also compute the arc
direction consistency (all deviations on one side of the chord) to separate a
designed arc from jitter.

Register targets (from Disney principle 7: "Add 10-20 px perpendicular offset at
path midpoint. Subtle (5 px) for corporate, pronounced (20 px+) for playful";
expressed as a fraction of a 1080-high frame, so 5 px = 0.46 %, 20 px = 1.85 %):

| Register | Target residual | Straight paths |
| --- | --- | --- |
| premium, corporate | 0.4 to 1.5 % | acceptable if declared mechanical |
| playful, energetic | 1.5 to 5 % | not expected |
| declared mechanical piece (kinetic type, UI) | N/A | criterion is N/A |

`arcRate` = share of qualifying moves whose residual sits in the register band and
whose deviations are one-sided. Jitter (`residual > 15 %` with mixed sides) counts
as a fault.

| Band | Threshold |
| --- | --- |
| S | `arcRate >= 0.80`; no jitter faults |
| A | `arcRate >= 0.60` |
| B | `arcRate >= 0.40` |
| C | `arcRate < 0.40` with >= 3 qualifying moves, or any jitter fault |

Basis: `disney-principles.md` principle 7 (numbers as quoted, with the note
"Mechanical UIs can use straight paths intentionally"); LottieFiles severity MEDIUM
("Could use better arcs"), which is why this criterion carries weight 1 and its C
requires three qualifying moves. Band rates are inference.

### C8. Secondary motion and follow-through lag

**Grade only declared `secondaryPairs`. A piece with no declared pairs is N/A, not C.**
Three reasons the earlier form was wrong. **Rigid parenting is correct for lockups**: a
wordmark and its symbol, a card and its shadow at fixed offset, a label and its rule move as
one unit because they are one object, and penalising `lockedRate` penalises the
null-and-parent workflow every AE artist uses. **`reactRate = 1.0` forces decoration**: most
hero moves in graphic motion (a headline slide, a counter, a card push) have no natural
child, so satisfying it means bolting glows and trailing shadows onto everything, which is
the agent-made look. **The DOM heuristic is wrong for text**: "any DOM descendant or sibling
within the clip" makes every word span inside a headline a secondary candidate of that
headline.

So: `reactRate` over declared pairs only; `lockedRate` **reported, not banded**; keep the
50-150 ms lag window for declared organic pairs. Note also that `disney-principles.md`
principle 8 gives secondary amplitude as **30-50 %** of primary while the `ampRatio` band
below starts at 0.10; the lower bound was taken from the counter-motion table, which is a
different technique.

**Measure.** S channel preferred. For each declared pair, look for a **secondary
reaction**: a move on a paired element (from `secondaryPairs`, or any element that
is a DOM descendant or sibling of the hero within the same clip) that starts after
the hero's onset. Record `lagMs` = secondary onset minus hero onset, `stopLagMs` =
secondary settle minus hero settle, and `ampRatio` = secondary travel / hero
travel (or, for a shadow or glow, its opacity or blur delta relative to 1).

Conforming reaction: `lagMs` in 50 to 150, `stopLagMs` in 50 to 200, `ampRatio` in
0.10 to 0.50, and the secondary uses a different ease string than the hero.
`reactRate` = hero moves with at least one conforming reaction / hero moves.
`lockedRate` = secondaries with `lagMs = 0` and identical ease (rigid parenting).

P channel: only pairs of tracked components with overlapping bounding boxes can be
tested; report `reactRate` with a "reduced confidence" flag.

| Band | Threshold |
| --- | --- |
| S | `reactRate = 1.0`; `lockedRate = 0` |
| A | `reactRate >= 0.75`; `lockedRate <= 0.10` |
| B | `reactRate >= 0.50` |
| C | `reactRate < 0.50`, or `lockedRate > 0.50` |

Basis: `disney-principles.md` principle 5 ("Child delay: 50-150 ms behind parent",
"Trailing elements: offset stop times by 100-200 ms") and principle 8 ("Amplitude:
30-50 % of primary; timing: 50-100 ms after primary; different easing than
primary"); `choreography.md` counter-motion table (10-30 % speed ratio, which sets
the 0.10 lower bound); LottieFiles severity HIGH for both "no follow-through" and
"missing secondary layer"; School of Motion mistake 6. Band rates are inference.

### C9. Anticipation presence

**Register-gated.** `narrative-structure.md`, this rubric's own source, gives anticipation
by personality as Corporate "Minimal/none" and Premium "Subtle tension", so a corporate piece
with `anticRate = 0` is *following the source* and scored C under the earlier form.
**Playful and energetic: graded, on declared impact verbs only. Corporate and premium: N/A,
with a CEILING** -- more than 30 % of hero moves carrying a wind-up is reported as
over-animated (inference). In studio work anticipation is spent on the two or three impacts
that matter; on 80 % of big moves it is wind-up spam.

**And note the contradiction with C11 that the qualifying gate creates.** C9 makes
translation of 1/3 of the frame a move that must carry anticipation; C11 makes travel over
1/3 of the frame a CRITICAL violation. The same move is simultaneously the class that must be
wound up and the class that must not exist, and the only build satisfying both is an
intermediate keyframe on every large move, which no studio has. Resolved in favour of C11's
correction below: large travel is normal in video and the 1/3 rule applies only to element
repositions inside a scene.

**Measure.** Qualifying hero moves: any move the manifest tags with an impact verb (plus,
in playful/energetic registers, translation `>= 1/3` of the frame dimension on its axis or a
scale change by a factor `>= 2`). Skip moves shorter than 150 ms. For each, search the
300 ms before onset for one of:

- a counter-move on the same element in the opposite direction with magnitude 10-20 %
  of the main travel and duration 100-200 ms;
- a scale dip `>= 3 %` on the same element.

**The context-dim detector has been removed from C9.** Dimming other elements to 40-60 % is
principle 3 *staging* in the same source file, not anticipation, and admitting it lets a
piece pass C9 with no wind-up anywhere, which makes the criterion measure nothing.

`anticRate` = qualifying moves with a detected anticipation / qualifying moves.
If fewer than 3 moves qualify the criterion is N/A.

| Band | Threshold |
| --- | --- |
| S | `anticRate >= 0.80` |
| A | `anticRate >= 0.50` |
| B | `anticRate >= 0.25` |
| C | `anticRate = 0` with >= 3 qualifying moves |

Basis: `disney-principles.md` principle 2 ("Duration: 100-200 ms, magnitude: 10-20 %
of main action", "Button: scale down 3 % before expanding", "Skip for micro-feedback
(< 150 ms)") and principle 3 staging ("Dim non-hero elements to 40-60 % opacity;
optional 2-4 px blur"); `narrative-structure.md` act 1; LottieFiles severity MEDIUM.
The 1/3 and 2x qualifying gates and the band rates are inference.

### C10. Timing contrast

**Measure.**

- Beat durations `B_i` (cut to cut, in frames). `R_beat = max / min`,
  `cv_beat = sd / mean`.
- Primary move durations `M_i` (one hero move per beat). `R_move = max / min`.
- Distinct duration classes: bucket every move duration into the LottieFiles speed
  classes (fast 0.15-0.3 s, medium 0.3-0.5, slow 0.5-0.8, very slow 0.8-2.0) and
  count non-empty buckets.

| Band | Threshold |
| --- | --- |
| S | `R_beat >= 3.0`; `cv_beat >= 0.30`; `R_move >= 3.0`; >= 3 duration classes |
| A | `R_beat >= 2.0`; `cv_beat >= 0.18`; `R_move >= 2.0` |
| B | `cv_beat >= 0.10` and `R_move >= 1.5` |
| C | `cv_beat < 0.10` (metronome), or `R_move < 1.5` (everything at one speed) |

**When the piece is cut to a grid, `cv` is the wrong statistic.** Beat-synced kinetic
typography cuts on bars, and the manifesto skill's own derived film sits on a 150 BPM grid at
12 frames per beat, so cards cluster at 1, 2 and 4 bar multiples and `cv_beat` can fall under
0.18 while the piece is professionally paced. The 0.18 threshold came from one film.
**Correction:** if `audio-beats.mjs` finds a tempo and >= 60 % of cuts land within 2 frames
of a bar line (inference, consistent with the skill's own 3-frame lock), grade timing
contrast as the **range of bar multiples used** (S: three distinct multiples, e.g. 1, 2, 4;
C: one) instead of `cv`. Otherwise keep the `cv` bands. `R_move >= 3.0` is fine as a
piece-level statistic but must **exclude ambient and transition tweens**, or every piece with
a Ken Burns passes trivially.

Basis: HyperFrames `motion-principles.md` "The slowest scene should be 3x slower than
the fastest" and its speed classes; `grade-original.py` check 9 (cv >= 0.18, "the
graded reference's cards vary by a factor of four"). The 0.30 / 0.10 cv bands, the
three-class rule and the bar-multiple alternative are inference.

### C11. Distance-duration consistency and the 1/3 distance rule

**Measure.** For translation moves, `dist` (px at authored size) and `dur` (ms).

**The correlation sign is wrong for video across a whole piece, and the 1/3 rule cannot be
CRITICAL.** In professional pieces the largest travels are the **fastest** (whip pans, slams,
pushes: full frame in 0.2-0.4 s per `beat-direction.md`'s own quick-picks) and the smallest
are the **slowest** (drift, breathe, Ken Burns over 4-10 s), so Spearman `rho` across all
translation moves is negative in a good piece, which the earlier bands scored C. The
LottieFiles table describes scaling **within a class** (two comparable card entrances, the
bigger one slightly longer), not a global law. And whip pans, pushes, full-frame wipes and
slam zooms all cross more than a third of the frame in one keyframe pair by design; the
HyperFrames transition catalogue is largely made of such moves. **Corrections: compute `rho`
and `outlierRate` within ENTRANCE moves only, excluding ambient, transitions and declared
impact verbs, and require at least 5 in the class; apply the 1/3 rule only to element
repositions inside a scene, with transitions and camera moves exempt BY CLASS rather than by
declaration; and drop this criterion's weight from 2 to 1, since its CRITICAL label rested on
the UI reading of the 1/3 rule.**

- `rho` = Spearman correlation between `dist` and `dur` across **entrance** translation moves
  (N/A if fewer than 5).
- Distance-scaling residual: expected `dur = base * k(dist)` with `k` from the
  LottieFiles table (50 px 0.8x, 100 px 1.0x, 200 px 1.3x, 300 px 1.5x, 400 px 1.6x,
  full screen 1.8-2.0x, interpolated); `base` = the median of `dur / k(dist)`.
  `outlierRate` = share of moves with `dur` outside 0.5x to 2x of expected.
- 1/3 violations: moves whose travel exceeds 1/3 of the frame on its axis with no
  intermediate keyframe (no direction change, no second tween on the element within
  the move, no ease change).
- Strobe frames: frames where a high-contrast edge (core mask) travels more than about
  **0.5 % of frame width per frame** (10 px at 1920, 5 px at 960, 20 px at 3840; halve at
  24 fps, roughly double at 60) with no blur filter active on the element and no declared
  shutter pass. The manifesto's "5-10 px" was measured on one composition at one frame size
  on high-contrast type, so an absolute figure silently changes meaning across resolutions.
  The criterion already credits a blur filter and a declared shutter; see **C19** for the
  more useful measurement, which is the *absence* of blur on fast moves.

| Band | Threshold |
| --- | --- |
| S | `rho >= 0.40`; `outlierRate <= 0.10`; 0 undeclared 1/3 violations; 0 strobe frames |
| A | `rho >= 0.20`; `outlierRate <= 0.25`; <= 1 violation; strobe frames <= 2 % of moving frames |
| B | `outlierRate <= 0.40`; <= 3 violations |
| C | `rho < 0` (longer moves take less time), or `> 3` violations, or strobe frames > 10 % of moving frames |

Basis: `timing-easing-tables.md` distance-duration scaling; `quality-checklist.md`
"Duration proportional to distance" and "1/3 rule (distance)" (CRITICAL); manifesto
SKILL.md "Above roughly 5-10 px of edge travel per frame, expect strobing on hard
edges" and the measured 31 px/frame strobe. Correlation and outlier bands are
inference.

### C12. Type hierarchy

**Measure.** S channel: computed `font-size` and `font-weight` of every text element
during its settled window; hero width = settled bounding-box width of the largest
text element per beat as a fraction of frame width. P channel: row-profile band
heights of text components, clustered at 10 % tolerance, as a proxy for size.

- `nSizes` = distinct settled sizes (cluster at 10 %).
- `sizeRatio` = largest / smallest settled size.
- `weightSpan` = max weight minus min weight among text elements.
- `minSize` = smallest settled size, scaled to a 1080-high frame.
- `heroFill` = max over beats of hero width fraction.

| Band | Threshold |
| --- | --- |
**Report `nSizes`, `sizeRatio` and `weightSpan`; grade only two things.** The hierarchy
*count* is exactly as brand-dependent as centroid checks 4 and 5, which this rubric demoted
for that reason: single-size, single-weight typographic systems (Swiss/International style, a
Saul Bass title, a one-word-per-card kinetic piece) are canonical professional work and score
`nSizes = 1`. `weightSpan >= 300` is unreachable in half the bundled faces --
`typography.md` lists League Gothic and Archivo Black as weight 400 only -- so a piece set in
one of them cannot reach A regardless of quality. And the A band's `minSize >= 24 px`
contradicts the C band's 18 px **and** `video-composition.md`'s own recommendation of 18-24 px
monospace labels.

| Band | Threshold |
| --- | --- |
| S | every settled size within 10 % of a step in a declared ratio series (a real type scale), **and** `minSize >= 18 px` at 1080p (>= 32 px body / >= 90 px headline when `delivery: social`) |
| A | sizes drawn from a scale with at most one exception; `minSize >= 18 px` |
| B | sizes not from a declared scale but `minSize >= 18 px` |
| C | `minSize < 18 px` at 1080p for anything meant to be read, or below the in-feed floor when `delivery: social` |

The 10 % scale tolerance is inference.

Basis: `grade-original.py` check 6 (>= 3 sizes); HyperFrames `typography.md` "Weight
contrast must be extreme ... Video needs 300 vs 900" (a span of 600, relaxed here to
300 because many bundled families ship only 400 and 700) and "headlines 60px+, body
20px minimum"; `video-composition.md` scale table (headlines 64-120 px, body 28-42 px,
which gives ratios of roughly 2.3 to 3; "If you're writing a font-size under 24 px in
a video composition, justify it"; "Hero text: 60-80 % of width"). The 2.5 / 2.0 / 1.5
ratio cut-offs are inference from that table.

### C13. Contrast at the large-text threshold

**Measure.** The `grade-original.py` method with two refinements. **(a) Tile the box.**
Averaging a photo, a radial glow or a gradient to one ground colour hides the one region
where the type crosses a light patch, which is the only region that matters: tile the bbox
(8x2 is enough), compute per-tile contrast, and take the **10th percentile** as the worst
case (inference). **(b) Report APCA Lc alongside the WCAG 2 ratio as an advisory line**,
keeping WCAG 2 as the gate. The manifesto skill already found that WCAG 2 misjudges hue
pairs (orange on cream "computes near 3:1 by construction"), and APCA's Lc 45 large-text
floor catches those; APCA is still a WCAG 3 draft, hence advisory
(https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html).

On settled frames only, core mask = `|luma - ground| > 70`; foreground colour = mean RGB
under the core mask; ground = per-tile mean RGB outside it, within the text element's
bounding box expanded by 10 %
(inference: local ground, not whole-frame, so a dark panel behind light type is
measured correctly). Contrast ratio `(L1 + 0.05) / (L2 + 0.05)` with WCAG relative
luminance. Record the worst ratio and the share of settled frames `>= 3.0`. Text
under 24 px (1080p-equivalent) is held to 4.5:1.

| Band | Threshold |
| --- | --- |
| S | worst `>= 4.5:1` |
| A | worst `>= 3.0:1` |
| B | `>= 95 %` of settled frames `>= 3.0:1` and worst `>= 2.5:1` |
| C | worst `< 2.5:1`, or `< 95 %` of settled frames `>= 3.0:1`, or any small text `< 4.5:1` |

Basis: WCAG 2.2 SC 1.4.3, Understanding document
(https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html): "at least
4.5:1" for normal text, "at least 3:1" for large text, large = "at least 18 point or
14 point bold" (about 24 px and 18.5 px); `grade-original.py` check 3 and SKILL.md
"Grade contrast at the LARGE-text threshold (3:1), not 4.5:1 ... Display type is
large text by definition". The 2.5:1 and 95 % B-band fences are inference.

### C14. Safe-margin violations (**no longer a gate for non-broadcast delivery**)

**Three corrections before the measurement.**

**SMPTE ST 2046-1 is a broadcast standard for a 16:9 television raster**, and the 90 %
title-safe box exists because CRT overscan cropped the frame. There is no overscan in any
web or social delivery path, and applied there it discards 10 % of the frame and fights
`motion-principles.md`'s own "Anchor to edges". So: **action-safe only when
`delivery: broadcast`; title-safe applied to *readable* text only (elements with a settled
window and a reading role); platform overlay rectangles when `delivery: social`.**
First-pass figures for 1080x1920 from current guides, all secondary and all subject to
change: TikTok about 180 px top and 320 px bottom; Instagram Reels about 220 px top and
420-500 px bottom; a common intersection of roughly 900x1400 centred (Kreatli safe-zone hub,
https://kreatli.com/guides/safe-zone-guide ; Ignite Social Media,
https://www.ignitesocialmedia.com/content-creation/what-are-the-safe-zones-for-tiktoks-and-instagram-reels/).
Put a versioned per-platform rectangle table in the manifest schema.

**The ink definition breaks the action-safe test outright.** Ink is `|luma - frame median| >
28`, so any full-bleed coloured panel, split screen or edge-anchored band becomes ink across
the entire edge band and fails action-safe on every frame of the piece. Restrict the
action-safe test to tracked components that are not the ground plane. The same threshold
makes the criterion behave randomly on the treatment `video-composition.md` actively
recommends, oversized faded type bleeding off-frame at 12-25 % opacity.

**"Any settled text element touching the frame edge = C" bans deliberately cropped display
type**, which is an editorial style and a declaration, not a fault. Declare cropped hero type
by element, the way `mechanical` is declared.

### C14 (measurement)

**Measure.** P channel, every frame. Ink mask restricted to an edge band. Two bands:

- Title-safe band: outer 5 % of width and height (SMPTE ST 2046-1 safe title area =
  90 % of the production aperture).
- Action-safe band: outer 3.5 % (safe action area = 93 %).

A frame **breaches title-safe** if a settled text element has `> 40` mask pixels (at
640x360, the `grade-original.py` count) inside the 5 % band. A frame **breaches
action-safe** if any undeclared ink has `> 40` pixels inside the 3.5 % band.
Declared `fullBleed` windows are exempt by name. Moving type in transit is judged
against action-safe only. For 9:16 social deliverables, the manifest may add
platform overlay rectangles that are treated as additional edge bands (their sizes
change per platform and are not fixed here).

| Band | Threshold |
| --- | --- |
| S | 0 title-safe breaches; 0 action-safe breaches |
| A | title-safe breaches `<= 0.5 %` of frames; 0 action-safe breaches |
| B | title-safe breaches `<= 2 %` of frames; action-safe breaches `<= 0.5 %` |
| C | more than that, or any settled text element touching the frame edge |

Basis: SMPTE ST 2046-1 (2009) as quoted by Extreme Reach
(https://helpcenter.xr.global/hc/en-us/articles/23817307323028-Safe-Title-Area):
"Safe Action Area: 93 % of the width and 93 % of the height of the Production
Aperture", "Safe Title Area: 90 % of the width and 90 % of the height"; standard
text at https://pub.smpte.org/pub/st2046-1/st2046-1-2009.pdf (fetched, not
machine-readable here). `grade-original.py` check 2 used 4 %; this rubric aligns to
the published 5 % / 3.5 %. Percent-of-frames bands are inference.

### C15. Readability dwell time

**Measure.** S channel: for each text element, `chars` (non-whitespace characters
visible at settle) and `settledMs` (settled window). `cps = chars / (settledMs /
1000)`. Elements with `chars <= 12` (one or two words) are **slam words** and are
held only to a minimum on-screen time of 4 frames (inference).

| Band | Threshold |
| --- | --- |
**Two models by element role.** Netflix's 20 cps and 5/6 s minimum are for **subtitles read
while watching something else**; kinetic typography presents one word or phrase at a time at
the point of gaze, which is RSVP reading, and RSVP puts comfortable comprehension around
300 wpm (about 200 ms per word) with no measured loss up to about 350 wpm. The old
`settledMs >= 833` for A fails a professional rapid kinetic piece whose cards average around
a second but include many at 15-20 frames.

| Band | Multi-line body / caption text | Single-line display text |
| --- | --- | --- |
| S | `cps <= 13` and `settledMs >= 833` | `>= 300 ms` per word (200 wpm) |
| A | `cps <= 17` and `settledMs >= 833` | `>= 200 ms` per word (300 wpm) |
| B | `cps <= 20` | `>= 160 ms` per word |
| C | `cps > 20`, or `chars > 12` settled `< 500 ms` | `< 130 ms` per word, or under **8 frames** absolute |

**The slam-word floor rises from 4 frames to 8.** 133 ms at 30 fps is recognition, not
reading, and it also sits in the territory the photosensitivity gate (C20) should be
watching. 8 frames is 267 ms, in line with the 200 ms per-word RSVP figure plus a frame of
settle (inference). The per-word figures are derived from the RSVP rates (PLOS ONE 2016,
https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0153786 ); the band split
is inference.

Basis: Netflix Timed Text Style Guide, General Requirements
(https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617-Timed-Text-Style-Guide-General-Requirements):
minimum duration "5/6 (five-sixths) second per subtitle event (e.g. 20 frames for
24fps)"; English (USA) guide
(https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-USA-Timed-Text-Style-Guide):
"Adult programs: Up to 20 characters per second", "Children's programs: Up to 17
characters per second". HyperFrames `typography.md`: "3 seconds on screen = must be
readable in 2. Fewer words, larger type", which is a 1.5x safety factor over the
reading rate and gives `20 / 1.5 = 13.3` cps for the S band. The 500 ms and 4-frame
fences are inference.

### C16. Palette discipline (rewritten: adherence, not hue counting)

**Hue-bin counting mis-scores professional palettes and "flat" was mis-defined.** Gradients
(which HyperFrames recommends), duotones and brand systems with five or more colours exceed
3-4 hue bins by construction; a per-scene background colour flip is a standard brand-reel
pattern and trips the 60-degree rotation rule; a muted premium scheme (a cream at about
S = 0.12, a sand, a warm grey) registers as entirely neutral, so no chromatic accent reaches
2 % and the piece scores C for being "flat" while being correct in its register. And the
basis, the 60-30-10 rule, is an interior-decorating proportion heuristic carried into graphic
design; nothing in either cited page licenses `nHues <= 3` as a pass condition.

**What professionals actually check is palette discipline.** Measure: (a) the share of
chromatic pixels within CIEDE2000 distance 8 of a declared palette entry (inference for the
radius), S >= 0.95, C < 0.80; (b) whether each beat's dominant ground is a palette entry;
(c) banding across large gradient regions after H.264. Keep the rainbow rule as a
**hue-velocity test on a single element**, not on the frame's dominant colour.

### C16 (original hue-census measurement, retained as a report line)

**Measure.** P channel on one settled frame per beat (70 % through the beat, as the
manifesto contact-sheet convention). Convert to HSV. Chromatic pixels: `S >= 0.25`
and `V` in 0.15 to 0.95. Bin hue into 24 bins of 15 degrees; merge adjacent bins whose
combined coverage is under 1 % of the frame. `nHues` = bins with `>= 1 %` coverage on
any beat frame, unioned across the piece. Neutrals (everything else) count as one.
`dominant` = coverage of the largest colour (chromatic or neutral) on each frame;
`accent` = largest chromatic bin that is not the dominant. Declared `footageRegions`
are masked out.

| Band | Threshold |
| --- | --- |
| S | `nHues <= 3`; `dominant >= 0.50` on every beat frame; `accent >= 0.02` on at least one frame |
| A | `nHues <= 4`; `dominant >= 0.50` on >= 80 % of beat frames; accent present |
| B | `nHues <= 6` |
| C | `nHues > 6`, or no chromatic accent reaches 2 % on any frame (flat), or hue of the dominant colour rotates more than 60 degrees across the piece outside a declared theme change (rainbow cycling) |

Basis: the 60-30-10 rule as applied to motion design (LottieFiles blog, "A Guide to
Color Theory for Motion Design",
https://lottiefiles.com/blog/tips-and-tutorials/color-theory-for-motion-design;
Wix, https://www.wix.com/wixel/resources/60-30-10-color-rule); HyperFrames
`video-composition.md` "Muted is fine. Flat is not. Every scene should have at least
one color that pulls the eye" and "Brand accent should be VISIBLE, not a 5 % opacity
glow"; `techniques.md` "Never do ... rainbow color cycling". Hue-bin counts and the
2 % accent floor are inference.

### C17. Transition design

**Measure.** For every cut (declared or detected), classify the handoff from the
tween table (S) or the pixel signature (P):

- **designed handoff**: an outgoing move and an incoming move overlap in time, or
  share the same start `T` (transitions overview: "outgoing and incoming animate AT
  THE SAME TIME T"), or the cut is listed in `onBeatHardCuts` and lands within 1
  frame of an audio onset.
- **undesigned**: elements pop fully formed with no entrance tween; **or a dip whose length
  is used nowhere else in the piece; or a dip longer than 8 frames with no declared reason.**
  A dip to black or white is **not** undesigned per se: it is a standard device for chapter
  breaks and emphasis, `transitions/overview.md` itself lists colour dip as a dissolve
  pattern and colour dip to black for the outro, and the manifesto skill's reference film
  cuts *through* blank frames of 1-8 frames and treats the gaps as the rhythm. The amateur
  tell is an unmotivated dip of inconsistent length, so **"designed" includes a dip whose
  length matches the piece's declared gap cadence within 1 frame.**
- Velocity match, for handoffs where both sides translate or blur: peak speed of the
  exit (px/frame) versus peak speed of the entry; `vmatch = |exit - entry| / max`.
- Type census: classify each transition (hard cut, crossfade, push, blur-through,
  iris, zoom, other). `primaryShare` = share of the most common type; `nTypes`.
- Duration of each transition against the energy table (calm 0.5-0.8 s, medium
  0.3-0.5 s, high 0.15-0.3 s) using the manifest register mapped premium/corporate
  to medium and playful/energetic to high (inference).

| Band | Threshold |
| --- | --- |
| S | 100 % designed; on every velocity-matched pair, **same direction of travel and neither side below 30 % of its own peak speed at the cut frame**; `primaryShare >= 0.60`; `nTypes <= 3`; durations inside the energy band, checked against the music grid where one exists |
| A | `>= 90 %` designed; `vmatch <= 0.5`; `nTypes <= 4` |
| B | `>= 75 %` designed |
| C | `< 75 %` designed, or the fade-out / gap / fade-in pattern at 2 or more cuts, or a different transition type at every cut (`nTypes = cuts` with `cuts >= 4`) |

Basis: HyperFrames `transitions/overview.md` rules 1 to 3 ("Every composition uses
transitions", "Every scene uses entrance animations", the banned fade-then-entrance
example), "Pick ONE primary (60-70 % of scene changes) + 1-2 accents. Never use a
different transition for every scene", and the energy duration table;
`beat-direction.md` states "Match exit velocity to entry velocity within ~5 % tolerance",
**but that tolerance fails the preset it came from**: the "Velocity-matched upward"
quick-pick is exit `y: -150, 0.33 s, power2.in` and entry `y: 150 -> 0, 1.0 s, power2.out`,
whose peak velocities are 2 x 150 / 0.33 = 909 px/s and 2 x 150 / 1.0 = 300 px/s, so
`vmatch = 0.67` (computed). The 5 % is aspirational prose. What is actually perceived as
continuous is direction continuity and no zero-velocity frame at the cut, which is what the
S band now measures. Note also that the energy-duration table maps register to duration, and
a "calm" 0.5-0.8 s transition in a premium piece cut to a 150 BPM track is a bar and a half
long, so check duration against the music grid when one exists (inference).
manifesto SKILL.md blank-run model (1-8 frames is rhythm). The 0.25 velocity
tolerance for A and the 75 % floor are inference.

### C18. Audio sync and audio delivery

**Measure.** Skip only if the manifest declares `silent: true`; a piece with no
audio and no such declaration scores C ("A film whose cuts are silent reads
unfinished", manifesto SKILL.md, Sound).

- Audio onsets: spectral-flux onset detection on the mixed track (the `audio-beats.mjs`
  method in the manifesto skill). Keep the strongest quartile as **hits**.
- Visual events: every cut, every hero-move onset, every declared impact verb.
- Alignment: for each visual event, `delta` = nearest audio onset minus the visual
  event, in ms, positive when sound leads. `locked` if `|delta| <= max(40, 1000/fps)`.
- `lockRate` = locked visual events / visual events; `hitRate` = audio hits with a
  visual event within the window / audio hits; `meanAbs` = mean `|delta|` over
  locked events; `bias` = mean signed `delta`.
- Delivery gates. **`loudnessTarget` is filled from the `delivery` enum, not from one
  film's window.** Published targets: EBU R128 -23 LUFS +/-1 LU and -1 dBTP for European
  broadcast (https://tech.ebu.ch/docs/r/r128.pdf); ATSC A/85 -24 LKFS +/-2 for US broadcast;
  YouTube normalises to -14 LUFS and only attenuates; AES TD1008 recommends -16 LUFS music
  and -18 LUFS speech at -1 dBTP for streaming
  (https://aes2.org/wp-content/uploads/2024/01/20210924_TD1008_v3.13.pdf); Netflix requires
  -27 LKFS +/-2 dialogue-gated at -2 dBTP
  (https://partnerhelp.netflixstudios.com/hc/en-us/articles/360001794307). **A manifest with
  no `delivery` fails this gate** rather than inheriting the -17 to -15 LUFS window of the
  one film that produced `grade-original.py`.
- **Gate on TRUE peak, not sample peak.** `grade-original.py` reads `max_volume` from
  `volumedetect`, which is sample peak; the `ebur128=peak=true` pass it already runs reports
  true peak. Inter-sample peaks after lossy encoding can exceed sample peak by more than
  1 dB, which is why every standard above specifies dBTP. Default -1 dBTP, -2 dBTP for
  Netflix delivery.
- **Centre the locked window one frame EARLY, not on zero.** Editors habitually place the cut
  one frame ahead of the musical hit so the eye registers the change with the sound
  (FilmmakerIQ, "Editing to the Beat, the One Frame Trick",
  https://filmmakeriq.com/editing-to-the-beat-the-one-frame-trick/), so a `bias` measured as
  visual-minus-audio reads a professionally cut piece as consistently "sound late by one
  frame".
- **Measure `hitRate` against bar lines and declared accents when a tempo is detected**, and
  keep the raw-onset version only for gridless pieces. On a 150 BPM track over 26 s the
  strongest quartile of onsets is roughly 30 events, so a 60 % hit rate demands a visual
  change every 0.8 seconds for the whole run, which is not craft, it is exhaustion. Pros cut
  on downbeats and phrase boundaries.
- `lockRate`'s music-bed condition should also accept an **SFX-only** track: a piece with
  designed SFX and no music bed is professional.

| Band | Threshold |
| --- | --- |
| S | `lockRate >= 0.80`; `hitRate >= 0.60`; `meanAbs <= 20 ms`; both delivery gates pass |
| A | `lockRate >= 0.60`; `hitRate >= 0.40`; both gates pass |
| B | `lockRate >= 0.40`; loudness within 2 LU of target |
| C | `lockRate < 0.40` with a music bed or SFX track present, or `bias > +40 ms` (**sound early**, the EBU R37 emission limit) or `bias < -100 ms` (sound late, inside the ITU detectability figure), or true peak above the delivery target, or no audio without a `silent` declaration |

**The sync-bias test previously penalised the wrong direction.** This criterion quotes
ITU-R BT.1359-1's detectability figures (+45 ms sound early to -125 ms sound late) and then
fired only on late sound. **Sound early is the more detectable fault** -- nature delivers
light first -- so the C band now fires on both sides, asymmetrically, as the sources
require.

Basis: EBU R37 (2007) as quoted by secondary sources: overall range
"<= 40 ms early to <= 60 ms late" for emission, "5 ms early to 15 ms late" per stage
(https://tech.ebu.ch/docs/r/r037.pdf, fetched as PDF, text not machine-readable
here; the 40/60 figures are widely quoted, for example in the arXiv sports-video
desync study https://arxiv.org/pdf/2212.01686). ITU-R BT.1359-1: "thresholds of
detectability are about +45 ms to -125 ms and thresholds of acceptability are about
+90 ms to -185 ms", positive = sound leads
(https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1359-1-199811-I!!PDF-E.pdf).
Music-to-motion perception: JND about 60 ms, point of subjective simultaneity -50 to
+50 ms (Vatakis and Spence 2007, as cited in Takehana, Uehara and Sakaguchi 2019,
PLOS ONE, https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0221584).
The +/- 40 ms window is therefore inside every detectability figure; the manifesto
skill's own `audio-beats.mjs` counts a cut as locked within 3 frames, and its proven
build had "12 of 23 cuts ... locked to onsets within 0-2 frames" (SKILL.md 3.6),
which is the origin of the 0.60 A-band lock rate. The 0.80 S rate, the 20 ms mean,
and the hit-rate figures are inference.

### C19. Reveal craft, and motion blur on fast moves (new, weight 2)

**Two things the earlier rubric measured nowhere, both of which are among the loudest
professional-versus-amateur signals in this medium.**

**(a) Opacity-only reveals.** `quality-checklist.md`'s CRITICAL tier includes "opacity-only
for important states", and no criterion measured it: section 4.2 explicitly reclassifies
opacity-only and filter-only tweens as *paint moves* and excludes them from every ease, arc
and distance test, so the single most recognisable agent-made tell -- every element fading in
with a 20 px rise -- passed the whole rubric cleanly. Measure the **share of entrances that
are opacity-only, or opacity plus travel under 5 % of frame height**, and the count of
distinct structural reveal devices used (clip-path or mask wipe, scale-from-mask, split
reveal, character or line cascade).

| Band | Threshold |
| --- | --- |
| S | opacity-only share `<= 0.25` and at least two structural reveal devices |
| A | share `<= 0.40` and at least one structural device |
| B | share `<= 0.60` |
| C | share `> 0.60` |

All figures inference. `clip-path` is an allowed property under the HyperFrames contract, so
the correction is buildable.

**(b) Motion blur coverage.** The manifesto skill says it outright -- "Motion blur on,
always. It is the difference between clean and cheap" -- and documents why: 31 px of
hard-edge travel per frame strobes and "more frames do not fix that. A shutter does". The
earlier rubric touched blur only as a sub-metric buried in C11. **For every frame where a
high-contrast edge travels more than about 0.5 % of frame width per frame, require one of: a
blur filter on the element with `stdDeviation` scaling with speed, an echo trail, or a
declared shutter pass covering that frame.** S = 100 % of fast frames covered, A >= 90 %,
C < 60 %. The coverage test must also assert that **no blurred frame touches a cut frame**,
since the manifesto's measured figure for a shutter straddling a cut is a 24.6-unit jump
against 1.6 for a clean one.

### C20. Photosensitive flash (new, weight 2, **a GATE**)

**Measure.** Full-frame relative-luminance reversals per rolling one-second window, computed
on the P channel, which is already decoded at full rate. A **flash** is a luminance change
above the general flash threshold over a significant portion of the frame; also flag
high-contrast regular striped patterns that scroll.

| Band | Threshold |
| --- | --- |
| S / A | `<= 3` flashes in any one-second window |
| C (gate) | more than 3 in any one-second window |

Basis: W3C, Understanding SC 2.3.1 Three Flashes or Below Threshold
(https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html); Ofcom's
broadcast guidance is the stricter form and is what a UK deliverable is tested against.
**This is the one defect in the rubric's scope that can genuinely harm a viewer, and it is a
hard fail in every broadcast QC department.** It is a live risk here rather than a theoretical
one: this rubric's own vocabulary of ground flips, white dips, slams and strobe describes
exactly the sequences that trip it, and a cluster of three cuts inside 18 frames is about
5 cuts per second.

### C21. Restraint and motion density (new, weight 1)

**A ceiling to balance the presence criteria.** C7, C8 and C9 award S at 80-100 % technique
presence and nothing anywhere caps motion density, so a piece that gives every headline a
wind-up, a trailing shadow and its own ease outscores a restrained Apple-style card, and the
first is the look the sources warn about. A senior reviewer's first note on most junior work
is "take half of it out".

**Measure.** Concurrent ambient motions (`motion-principles.md`: a scene is "alive with ONE
ambient motion"); hero moves in flight at once; move onsets per 10 frames sustained across a
beat.

| Band | Threshold |
| --- | --- |
| S | exactly one ambient motion running during breathe; at most one hero move in flight at a time |
| A | at most two concurrent ambient motions |
| C | three or more concurrent ambient tweens, or more than one move onset per 10 frames sustained for a whole beat |

All figures inference except the one-ambient rule.

### C22. Framing and layout (new, weight 1)

The rubric measured 18 aspects of motion and none of layout, having demoted centroid checks 4
and 5 for brand dependence without replacing them, so a piece can score A with every element
optically wrong in the frame. This is the first thing a studio reviewer looks at.

**Measure**, all from the rect track section 4.1 already dumps, so it is free: the count of
distinct x and y alignment positions across settled elements (professional frames resolve to
two or three, amateur frames to one per element); consistency of the outer margin across
beats; count of high-salience clusters per settled frame (one focal point, not three); and
optical versus geometric centring on title cards. All thresholds inference; report first,
band once calibrated.

### C23. Encode and delivery QC (new, weight 1, **the duration half is a GATE**)

Nothing in the earlier rubric looked at the file as a deliverable, and these fail silently in
web renders.

- **Duration and frame count exactly as authored** (the script outline has this; it is now a
  gate).
- `pix_fmt yuv420p`, correct `color_range` and `color_primaries` tags. A limited-range render
  tagged full crushes or washes the entire piece. Measurable with `ffprobe`.
- Chroma bleed on thin saturated type: 4:2:0 halves colour resolution, so flag strokes under
  3 px at 1080 in high-saturation colours as a note.
- Gradient banding after encode (see C16).
- Per-frame encoded size against motion energy: a rate-limited encoder shows blockiness at
  the fastest frames.
- Audio 48 kHz stereo, and the bed does not stop dead on the last frame.
- A usable first frame (not black, not mid-transition), because feeds show it as the poster.
- End-card hold long enough to read: commonly 2-3 s on a 15-30 s spot (no citable standard;
  inference).
- For looping deliverables, last frame within one code value of the first **and velocity
  continuous** across the seam.

### C24. Eye-trace and screen direction (new, weight 1, report-only)

Editors check where the eye is at the cut and where the next hero lands; a cut that moves the
point of interest across the whole frame reads as a jump. Measurable on both channels:
distance between the settled hero centroid before the cut and the hero onset position after
it, as a fraction of frame diagonal; report the distribution and flag consistent jumps over
0.5 (inference). Also report the parallax ratio of background travel to hero travel during a
camera move (`choreography.md`'s 1.0x / 0.5x / 0.2x convention is measured nowhere), and the
direction sequence of transitions, flagging alternating directions with no declared reason.

---

## 6. Overall scoring

### Band points and weights

Band points: S = 100, A = 85, B = 65, C = 30 (inference). **The earlier claim that "the
spacing makes one C cost more than two Bs" is arithmetically wrong**: measured from S, one C
costs 70 points and two Bs cost 2 x 35 = 70, exactly equal. The claim holds only if A is the
baseline, which was not stated. The spacing is still defensible on the severity logic that a
single amateur tell is what reviewers notice first; it just does not do what was claimed.

Weights follow the LottieFiles severity tiers: CRITICAL-tier criteria weigh 2, the
rest weigh 1.

| Weight 2 | Weight 1 | Weight 0 (gates only) |
| --- | --- | --- |
| C1 ease discipline | C2 ease vocabulary | C13 contrast |
| C3 simultaneity | C4 hold ratio | C18 delivery half |
| C17 transition design | C5 frame integrity | C20 photosensitive flash |
| C19 reveal craft and motion blur | C6 settle quality | C23 duration/cadence half |
| | C7 arcs (register-gated) | |
| | C8 secondary motion (declared pairs) | |
| | C9 anticipation (register-gated) | |
| | C10 timing contrast | |
| | C11 distance-duration and 1/3 | |
| | C12 type hierarchy | |
| | C14 safe margins | |
| | C15 readability | |
| | C16 palette | |
| | C18 sync half | |
| | C21 restraint | |
| | C22 framing | |
| | C23 encode QC | |
| | C24 eye-trace (report-only) | |

Two changes from the earlier revision. **C11 drops from weight 2 to 1**, because its CRITICAL
label rested on the UI reading of the 1/3 rule. **Gate criteria carry weight 0 in `W`**: a
gate already caps the overall grade at C, so also weighting it double-penalises the same
defect and drags `W` down for a piece with a single legibility problem and otherwise
excellent choreography, which destroys `W` as a craft signal and as a diff between builds.
Let the gates be binary and let `W` measure only craft.

Weighted score `W = sum(points_i * w_i) / sum(w_i)` over criteria that are not N/A.

### Gates

Four criteria are **gates**: **C13 contrast, C20 photosensitive flash, the delivery half of
C18 (loudness and true peak), and the duration/cadence half of C23.** A C on any gate caps
the overall grade at C regardless of `W`.

**Two gates from the earlier revision have been removed.** C5 (dead frames) would gate out
animation on twos, deliberate dead-still holds and freeze-frame end cards, and the cheapest
way to pass it was per-frame grain, which the rubric rewarded and learned nothing from. C14
(safe margins) would gate out any web-only deliverable and any deliberately cropped
full-bleed type. What a studio actually treats as a hard fail is what now gates: a
photosensitivity risk, unreadable text, a broken encode or wrong duration, and clipping.

### Overall bands

| Overall | Rule |
| --- | --- |
| S | every **applicable** criterion at S or N/A |
| A | `W >= 90` and no criterion at C |
| B | `W >= 75` and at most 2 criteria at C, none of them gates |
| C | anything else, or any gate at C |

This rubric's A band sits at 90 % deliberately: it is a build gate whose job is to stop a
defect shipping. Treat B as "iterate", A as "**no visible defect**", S as "portfolio". **A
does not mean good**: concept, script, art direction and brand fit are unmeasured here.

(The earlier revision printed the Motion Awards nominee floor of 7.0 on a 10-point scale
beside this rubric's 90 % and then disclaimed the comparison in the next sentence. A juried
relative ranking converted to a percentage is not commensurable with a defect-count score,
and printing the two numbers side by side invited exactly the comparison the disclaimer
forbade, so the figures have been removed and only the distinction kept.)

**Several S bands were unreachable by construction** and have been simplified above: C12 and
C17 required five-way conjunctions, so the joint probability across 20-plus criteria was
effectively zero and S was decorative. That matters, because the rubric then cannot
distinguish good from great, which is the distinction section 1 opens by discussing.

### Reporting

**Print the worst-first table FIRST and treat the aggregate as secondary**; a studio would
not read the aggregate at all. Print the declaration budget (4.3) at the top: the number of
declarations, and the number of criteria whose band improved because of one.

Report every criterion with its measured values, band, weight, basis line, and the
frame numbers of the worst offender (the `worst@` convention from `grade.mjs`), so
the table doubles as the fix queue. Sort the report worst-first. Print N/A criteria
with the reason (register, manifest declaration, missing channel).

---

## 7. Script outline

Inputs: `render.mp4`, `index.html` (composition), `grade.json` (manifest, section
4.3), optional `audio.wav` if the render is muxed with a different mix.

Pipeline:

1. `ffprobe` for fps, frame count, dimensions. Fail if the composition's declared
   duration times fps does not equal `nb_read_frames` (SKILL.md section 1).
2. Source probe (section 4.1): headless browser, seek every frame, dump
   `tracks.json` (per element per frame) and `tweens.json` (tween table).
3. Pixel decode (section 4.1): full-rate grey and RGB planes; per-frame stats;
   `mpdecimate` duplicate list; connected components with tracking.
4. Cut list: manifest cuts if present, else `segment.mjs` blank-run model; reconcile
   against the tween table's clip boundaries and report any mismatch.
5. Audio: onset list via spectral flux; `ebur128` and `volumedetect` via ffmpeg.
6. Derive moves, onsets, settles, progress curves, roles, hero per beat.
7. Evaluate C1 to C18, each returning `{measured, band, weight, worstFrames,
   basis, na}`.
8. Aggregate (section 6), print the sorted table, write `grade-report.json`, exit
   non-zero below the target band (default A) so a bad render cannot ship quietly.

Output schema:

```json
{
  "overall": { "band": "A", "weighted": 91.4, "gatesFailed": [] },
  "criteria": [
    {
      "id": "C1", "name": "ease discipline", "weight": 2, "na": false,
      "measured": { "linearSpatial": 0, "directionViolations": 1, "moves": 38 },
      "band": "A", "worstFrames": [212], "note": "#sub exits with power2.out"
    }
  ],
  "inputs": { "fps": 30, "frames": 1050, "channels": ["source", "pixel", "audio"] }
}
```

Implementation cautions carried from the manifesto skill: decode a range as
`(n, H, W, 3)` and reduce over axis 3, not 2 (SKILL.md, "A measurement bug that will
cost you an hour"); bias clip boundaries inward when converting frames to seconds
(SKILL.md, "The frame-boundary trap"); smooth ink counts before looking for
reversals; exempt by name, never by loosening a threshold.

---

## 8. Sources

Local files (read in full):

- `<skill>/SKILL.md`
- `<skill>/scripts/grade-original.py`
- `<skills>/motion-design/director/disney-principles.md` (MIT, (c) LottieFiles)
- `<skills>/motion-design/director/choreography.md`
- `<skills>/motion-design/director/narrative-structure.md`
- `<skills>/motion-design/reference/timing-easing-tables.md`
- `<skills>/motion-design/reference/quality-checklist.md`
- `<skills>/motion-design/reference/troubleshooting.md`
- `<skills>/hyperframes-animation/rules-index.md` (Apache-2.0, (c) HeyGen)
- `<skills>/hyperframes-animation/techniques.md`
- `<skills>/hyperframes-animation/transitions/overview.md`
- `<skills>/hyperframes-animation/adapters/gsap-easing-and-stagger.md`
- `<skills>/hyperframes-animation/rules/spring-pop-entrance.md`
- `<skills>/hyperframes-creative/references/motion-principles.md`
- `<skills>/hyperframes-creative/references/beat-direction.md`
- `<skills>/hyperframes-creative/references/video-composition.md`
- `<skills>/hyperframes-creative/references/typography.md`

Web:

- Motion Awards FAQ 2024: https://2024.motionawards.com/faq/
- Motion Awards FAQ (current): https://motionawards.com/faq.html
- Vimeo, "How to get a Vimeo Staff Pick": https://vimeo.com/blog/post/how-to-get-a-vimeo-staff-pick
- D&AD Awards, Animation category: https://www.dandad.org/awards/d-ad-awards/categories-2025/animation
- LBBOnline, D&AD 2019 judging criteria: https://lbbonline.com/news/dad-awards-2019-judging-criteria-announced
- School of Motion, common 2D character animation mistakes: https://schoolofmotion.com/blog/new-to-2d-character-animation-here-are-the-most-common-mistakes-and-how-to-avoid-them
- Envato, Ben Marriott interview: https://elements.envato.com/learn/ben-marriott
- Pluralsight, 12 principles of animation (moving hold): https://www.pluralsight.com/resources/blog/software-development/understanding-12-principles-animation
- W3C, Understanding SC 1.4.3 Contrast (Minimum): https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- SMPTE ST 2046-1 (2009): https://pub.smpte.org/pub/st2046-1/st2046-1-2009.pdf ; percentages as quoted by Extreme Reach: https://helpcenter.xr.global/hc/en-us/articles/23817307323028-Safe-Title-Area
- Netflix Timed Text Style Guide, General Requirements: https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617-Timed-Text-Style-Guide-General-Requirements
- Netflix English (USA) Timed Text Style Guide: https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-USA-Timed-Text-Style-Guide
- EBU R37 (2007): https://tech.ebu.ch/docs/r/r037.pdf
- ITU-R BT.1359-1: https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1359-1-199811-I!!PDF-E.pdf
- Takehana, Uehara, Sakaguchi (2019), PLOS ONE, audiovisual synchrony for human motion to music: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0221584
- arXiv 2212.01686, perceptual acceptability of A/V desync in sports video: https://arxiv.org/pdf/2212.01686
- LottieFiles blog, colour theory for motion design: https://lottiefiles.com/blog/tips-and-tutorials/color-theory-for-motion-design
- Wix, the 60-30-10 rule: https://www.wix.com/wixel/resources/60-30-10-color-rule

Not verified (fetch returned no readable text; not relied on for any number): the
YouTube videos "Why Your Motion Design Still Looks Amateur" and "Why Your Animation
Looks Bad (3 Fixes)", and the EBU / SMPTE / ITU PDFs themselves, whose figures are
taken from the secondary sources listed against them.
