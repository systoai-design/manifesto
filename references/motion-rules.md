# The studio rulebook for motion design

Working rules professionals apply when authoring motion graphics, assembled for the
`manifesto` skill. Every rule has four parts: the name, the reason it exists, a
measurable form a grader can check, and the code-level implication under the
HyperFrames contract (one paused GSAP timeline, every tween `fromTo` with an explicit
from-state, transforms and paint-only properties, deterministic, state a pure function
of timeline time).

This document extends the local references rather than repeating them. Where a
number already lives in `motion-principles.md`, `choreography.md`,
`disney-principles.md` or `timing-easing-tables.md`, it is cited, not re-derived.

**Revision 2 (2026-09-02).** Corrected against a practitioner review. The most
consequential fix is the shutter recipe (the published one produced a 360-degree shutter,
twice any camera); the most structural are the ones that stop UI thresholds being applied
to film (the distance-duration table, the stagger cap, the 1/3 rules, the ease quotas).
Seven rules the document was missing have been added, including the only genuinely unsafe
gap, a photosensitivity limit. Every change is in `corrections.md` in this directory.

## How to read the numbers

Every figure carries a basis in square brackets:

- `[source: <path or URL>]` means the number is stated by that source.
- `[measured: <path>]` means it was measured on a real reference in this repo.
- `[inference]` means it is this document's own reasoning from the cited material.
  An inference is never a canonical figure. Treat it as a starting value to be fitted
  against the reference, which is what the manifesto skill does anyway (SKILL.md:
  "Do not replicate what you saw. Replicate what you measured.").

Frame-to-time conversion used throughout `[arithmetic]`:

| Frames | 24 fps | 30 fps | 60 fps |
| --- | --- | --- | --- |
| 1 | 41.7 ms | 33.3 ms | 16.7 ms |
| 2 | 83 ms | 67 ms | 33 ms |
| 3 | 125 ms | 100 ms | 50 ms |
| 4 | 167 ms | 133 ms | 67 ms |
| 6 | 250 ms | 200 ms | 100 ms |
| 12 | 500 ms | 400 ms | 200 ms |

When a source states an offset in frames without naming a frame rate, it is an After
Effects habit and almost always means a 24 or 30 fps comp. The manifesto skill authors
in seconds on the reference's frame grid (`var F = 1/30; f(frameNumber)`), so convert
once and keep the grid (SKILL.md, "Raising the frame rate needs no retiming").

## Sources consulted

Local (read in full, cited by path):

- LottieFiles `motion-design` skill (MIT): `<skills>/motion-design/director/disney-principles.md`, `director/choreography.md`, `director/core-philosophy.md`, `director/narrative-structure.md`, `director/motion-personality.md`, `director/context-adaptation.md`, `director/emotion-mapping.md`, `director/decision-framework.md`, `reference/timing-easing-tables.md`, `reference/quality-checklist.md`.
- HyperFrames animation skill (Apache-2.0): `<skills>/hyperframes-animation/rules-index.md`, `techniques.md`, `transitions/overview.md`, `adapters/gsap-easing-and-stagger.md`, `rules/waterfall-entry.md`, `rules/nudge-curve.md`, `rules/spring-pop-entrance.md`, `rules/multi-phase-camera.md`, `rules/viewport-change.md`, `rules/depth-of-field-blur.md`, `rules/motion-blur-streak.md`, `rules/kinetic-beat-slam.md`, `rules/3d-camera-flight.md`, `blueprints/camera-journey.md`.
- HyperFrames creative skill: `<skills>/hyperframes-creative/references/motion-principles.md`, `beat-direction.md`, `video-composition.md`, `typography.md`.
- Manifesto skill: `<skill>/SKILL.md`, `scripts/grade-original.py`, `library/INDEX.md`, `library/apple-business-essentials.md`; project findings `<builds>/abe-ad/FINDINGS.md`, `<builds>/systo-26s/FINDINGS.md`.

Web (fetched; a few pages were not fetchable and are marked as such):

- Issara Willenskomer, "Creating Usability with Motion: The UX in Motion Manifesto", https://uxmag.com/articles/creating-usability-with-motion-the-ux-in-motion-manifesto
- Wojciech A. Hoffmann's principle list at https://www.motiondesignprinciples.com/ (names Offset and Delay, Parenting, Parallax, Dolly and Zoom)
- Thomas and Johnston's twelve principles, summarised at https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation
- Ben Marriott interview at https://elements.envato.com/learn/ben-marriott and his course outline at https://www.benmarriott.com/motion-foundation
- School of Motion: graph editor primer https://www.schoolofmotion.com/blog/graph-editor-after-effects, follow-through https://www.schoolofmotion.com/blog/follow-through-tutorial, eases https://schoolofmotion.com/blog/photoshop-animation-eases, six transitions https://schoolofmotion.com/blog/six-essential-motion-design-transitions-tutorial
- Graph editor guides: https://designkkashi.com/en/after-effects-graph-editor-speed-value-influence-guide/ , https://www.kelp.agency/blog/using-the-graph-editor-in-adobe-after-effects/ , https://olafmotion.com/tutorials/how-to-use-graph-editor/ , https://mtmograph.com/blogs/tools/how-to-use-the-graph-editor-in-after-effects , https://motion.mtmograph.com/m-screens/easing/speed-graph , https://motion.mtmograph.com/m-screens/easing/value-graph , https://vdci.edu/learn/after-effects/mastering-motion-animations (Jerron Smith)
- Character offset frames: https://frl.nyu.edu/keyframing-the-basics/
- Staggering in AE: https://docs.nosleepcreative.com/after-effects/cookbook/staggering , https://blog.frame.io/2023/12/13/insider-tips-how-to-create-a-staggered-layer-sequence-in-after-effects/
- Material Design 1 motion: https://m1.material.io/motion/duration-easing.html , https://m1.material.io/motion/movement.html
- Material Design 3 tokens (mirrors of the M3 spec, the m3.material.io page itself renders client-side and returned no body): https://www.mdui.org/en/docs/2/styles/design-tokens , https://raw.githubusercontent.com/anzy-renlab-ai/vocut/main/docs/research/methodology/material-motion.md ; canonical page https://m3.material.io/styles/motion/easing-and-duration/tokens-specs
- Apple HIG Motion (current page https://developer.apple.com/design/human-interface-guidelines/motion renders client-side and returned no body; the older iOS HIG animation text was read from the mirror https://codershigh.github.io/guidelines/ios/human-interface-guidelines/visual-design/animation/index.html); WWDC23 "Animate with springs" notes https://wwdcnotes.com/documentation/wwdc23-10158-animate-with-springs/
- IBM Carbon motion: https://v10.carbondesignsystem.com/guidelines/motion/overview/
- NN/g animation duration: https://www.nngroup.com/articles/animation-duration/
- Val Head: https://valhead.com/2016/05/05/how-fast-should-your-ui-animations-be/
- GSAP: https://gsap.com/resources/getting-started/Easing/ , https://gsap.com/resources/getting-started/Staggers/
- Parallax ratios: https://lumitree.art/blog/parallax-effect
- Reading time: https://legibility.info/rules-for-text-in-videos , https://www.rocketshiphq.com/text-overlays-video-ads-mobile/
- Hierarchy: https://artofstyleframe.com/blog/visual-hierarchy-motion-graphics/
- Pauses and contrast: https://www.story-boards.ai/content-hub/blog/understanding-timing-and-transitions-in-motion-graphics-storyboarding
- Cuts and continuity: https://en.wikipedia.org/wiki/Match_cut , https://en.wikipedia.org/wiki/180-degree_rule , https://www.studiobinder.com/blog/match-cuts-creative-transitions-examples/ , https://www.studiobinder.com/camera-shots/camera-movements/push-in-shot/ , https://beverlyboy.com/cinematography/camera-movements-explained-with-examples/

Not fetchable in this session (403 or client-rendered): the VANTIQ Studio Medium
article on speed vs value graphs, the VDODNA overshoot article, the Hui Wang iOS 26
motion guide. Nothing in this document depends on them.

---

## Rule 1. Nothing starts on the same frame (offset and delay)

**Why.** Two objects that begin moving on the same frame read as one object. The
viewer's visual system groups by common onset before it reads what the objects are.
Willenskomer states the principle as "Defines object relationships and hierarchies
when introducing new elements and scenes" and adds that "Even before the user
registers what these objects are, the designer has already communicated to her,
through motion, that the objects are somehow 'separate'" [source:
https://uxmag.com/articles/creating-usability-with-motion-the-ux-in-motion-manifesto].
Hoffmann lists it first among his UX principles under the same name, "Offset and
Delay" [source: https://www.motiondesignprinciples.com/]. LottieFiles puts it as
"Nothing starts and stops all at once" [source:
`motion-design/director/core-philosophy.md`, Pillar 3]. HyperFrames adds the
scene-level version: "Don't start at t=0. Offset the first animation 0.1-0.3s.
Zero-delay feels like a jump cut" [source:
`hyperframes-creative/references/motion-principles.md`, Guardrails].

The exception that proves the rule: elements that are one physical thing (a cursor
and the button it depresses; a card and its shadow) should share a start so they read
as one. HyperFrames does exactly this by passing a single targets array to one tween
[source: `hyperframes-animation/rules-index.md`, `physics-press-reaction`].

**Measurable form.**

- Related but separate elements: **offset by 15 to 30% of the offset element's own
  duration**, with 2 to 4 frames as a floor for short snaps [inference; no source states
  either figure verbatim]. Express it as a fraction, not a constant frame count: a
  3-frame offset against a 6-frame snap is 50% overlap and reads as a cascade, while the
  same 3 frames against a 40-frame settle is 7.5% and reads as simultaneous, which is
  exactly the failure this rule exists to prevent. Rule 2 already defines the same
  relationship correctly as an overlap fraction, so the frame-count form made this
  document inconsistent with itself between adjacent rules; a fraction also survives a
  change of register and of frame rate. The supporting figures:
  - character animation: "move all the keys for the arms a few frames ahead of the
    legs, around 3 frames should be fine" [source: https://frl.nyu.edu/keyframing-the-basics/]
  - product-UI comps: "Offset sibling groups by ~3 frames. Not per element, per
    group" [source: `manifesto/SKILL.md`, Liquid glass, Structure]
  - LottieFiles: child delay 50-150 ms behind parent [source:
    `motion-design/director/disney-principles.md` §5], which is 1.5 to 4.5 frames at
    30 fps [arithmetic]
  - LottieFiles: when many elements react to one trigger, "All start within 50ms of
    each other" but "Can arrive at different times" [source:
    `motion-design/director/choreography.md`, Shared Motion Events]
  - HyperFrames waterfall: the next element starts "within ±2 frames of the previous
    settling" [source: `hyperframes-animation/rules/waterfall-entry.md`]
- First motion in a scene: 0.1 to 0.3 s after the scene's first frame [source:
  `hyperframes-creative/references/motion-principles.md`]. The manifesto grader's
  companion rule for a spoken beat is that something must be on screen within 6 sampled
  frames of the line start (`SYNC` check) [source: `manifesto/scripts/grade-original.py`].
- Grader test: for every pair of tweens on distinct targets starting inside the same
  0.5 s window, the difference of their start times is either 0 (deliberately grouped
  as one object) or at least 1 frame. Count zero-offset pairs on unrelated targets;
  target is 0 [inference].

**Code-level implication.**

- Author onsets on the frame grid: `var F = 1/30; tl.fromTo(a, ..., f(120)); tl.fromTo(b, ..., f(123));` [source: `manifesto/SKILL.md` §4 and `waterfall-entry.md`].
- For a group, prefer GSAP `stagger: { each }` over N hand-typed delays so the offset
  survives a change of count [source: `hyperframes-animation/adapters/gsap-easing-and-stagger.md`, Stagger].
- Elements that must read as one object go in one `fromTo` with an array of targets.
- Never emulate offset with CSS `transition-delay`; CSS transitions run on wall-clock
  and break seek [source: `hyperframes-animation/rules-index.md`, contract].

---

## Rule 2. Overlapping action in graphics

**Why.** Disney's fifth principle: "loosely tied parts of a body should continue
moving after the character has stopped" and parts have different timing [source:
https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation , after Thomas and
Johnston, *The Illusion of Life*]. School of Motion's graphics version: "Something
moves in your scene, and as it moves something else follows, only slightly delayed"
[source: https://www.schoolofmotion.com/blog/follow-through-tutorial]. In graphics
there is no skeleton, so the "parts" are the layers of a lockup: word, underline,
icon, shadow, background panel. The rule keeps a build from reading as a spreadsheet
filling in, and it is the difference between a queue and a wave.

**Measurable form.**

- A chain of N related elements should overlap, not queue: element k+1 starts before
  element k settles. HyperFrames: "Overlap, don't queue: next element starts within ±2
  frames of the previous settling; gaps SHRINK across the cascade; the last element
  snaps" [source: `hyperframes-animation/rules/waterfall-entry.md`].
- Heavier elements travel further and longer than light ones. Waterfall table [source:
  same file]: anchor/heavy 60-80 px over 0.16-0.20 s; normal word 40-50 px over
  0.13-0.16 s; punctuation 30-48 px over 0.10-0.13 s.
- The Apple cascade quantifies overlap as the ratio R of per-unit duration to the
  first-to-last sweep. Measured on a real 11-character line at 60 fps: sweep about 20
  frames, per-unit about 14 frames, so R is about 0.7 [measured: `manifesto/SKILL.md`,
  Translating the Range Selector]. R near 1 is a wash; small R is discrete pops.
- Trailing elements stop at different times: "Trailing elements: offset stop times by
  100-200ms" [source: `motion-design/director/disney-principles.md` §5].
- Grader test: for a cascade, compute overlap fraction = (end_k - start_{k+1}) /
  duration_k for each adjacent pair. A queue has overlap ≤ 0; a wave has 0 < overlap <
  1 and the sequence of gaps is non-increasing [inference from the waterfall rule].

**Code-level implication.**

- Compute each start from the previous: `nextStart = prevStart + prevDuration - overlapFrames * F` [source: `waterfall-entry.md`].
- The Range Selector translation for a wash [source: `manifesto/SKILL.md`]:

```js
// T = total, R = overlap ratio (about 0.7 measured), n = units
gsap.fromTo(units,
  { yPercent: 100, autoAlpha: 0, filter: "blur(10px)" },
  { yPercent: 0, autoAlpha: 1, filter: "blur(0px)",
    duration: T * R / (1 + R),
    stagger:  T / ((1 + R) * (units.length - 1)),
    ease: "power3.out" });
```

- Arrival opacity in a snap cascade is binary via `tl.set`, never a fade [source:
  `waterfall-entry.md`]; the blur-and-fade wash is the other register (Apple cascade)
  and must not be mixed with a mask reveal [source: `manifesto/SKILL.md`, Do not
  confuse it with a mask reveal].

---

## Rule 3. Follow-through and secondary motion

**Why.** Follow-through is the part of the body that keeps going after the main mass
stops; secondary action is a supporting movement that "enhance[s] the main action
without stealing focus" [source:
https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation]. In graphics the
follow-through is the shadow, glow, underline or sibling that reacts a beat late, and
the secondary action is the ripple, the counter-motion of the background, the shadow
that spreads when a card lifts. School of Motion: the amount of follow-through
"communicates information about the scene (speed, force, environment)" [source:
https://www.schoolofmotion.com/blog/follow-through-tutorial].

**Measurable form.**

- Secondary amplitude 30-50% of primary, starting 50-100 ms after primary, on a
  different easing [source: `motion-design/director/disney-principles.md` §8].
- Three-layer amplitude budget: primary 100%, secondary 30-50%, ambient 10-20%
  [source: `motion-design/director/core-philosophy.md`, Three Motion Layers].
- Reaction timing in the four-act model: shadows 50-100 ms after primary, siblings
  50-150 ms, environment 100-200 ms; counter-motion simultaneous [source:
  `motion-design/director/narrative-structure.md`, Act 3].
- Counter-motion speed ratios: background shifts opposite the hero at 20-30% of hero
  speed; shadow scales down 10-20% when hero scales up; ambient drifts opposite a
  rotation at 15-25% [source: `motion-design/director/choreography.md`, Counter-Motion].
- Overshoot as follow-through is a register, not a garnish: `back.out` and `elastic`
  are "RARE, explicitly-playful register only, never a default" and the baked spring at
  damping 0.6-0.7 gives 5-10% overshoot where `back` reads cartoon [source:
  `hyperframes-animation/adapters/gsap-easing-and-stagger.md`, Spring Eases].
- Grader test (from the shipped grader): within a settled window, ink count must show
  no direction reversal when the film's law is "no overshoot"; a re-trigger is a sharp
  positive jump and starts a new segment [source: `manifesto/scripts/grade-original.py`,
  MOTION check].

**Code-level implication.**

- Shadow/glow follow-through is a second `fromTo` on a different target at
  `t + 0.05..0.10`, amplitude scaled by 0.3-0.5, with a softer ease than the primary
  (`power2.out` against a `power4.out` primary) [inference from the amplitude and
  timing figures above].
- Under the contract, a shadow must be a paint-only property (`boxShadow`,
  `filter: drop-shadow`, opacity of a shadow layer) or a transform on a separate shadow
  element; never animate `width`/`height`/`top`/`left` [source: `hyperframes-animation/rules-index.md`].
- Overshoot only on transforms, never on opacity or color; split opacity onto its own
  `power2.out` tween at the same position [source: `gsap-easing-and-stagger.md`, Spring Eases, craft notes].
- Never overlap two transform tweens on one element; put the follow-through on a child
  or wrapper [source: `hyperframes-creative/references/motion-principles.md`, Load-Bearing GSAP Rules].

---

## Rule 4. The speed graph and the value graph, and what ease shapes look like on each

**Why.** Ben Marriott credits the graph editor as the single largest step in his
work: with plugins "my work plateaued, I could combine scenes and make it look pretty
good, but nothing flowed smoothly", so he went on "a plugin diet" and "did everything
inside the graph editor", learning both the speed graph and the value graph, which
produced the "bespoke smooth, snapping motion" that separates professional from
beginner work [source: https://elements.envato.com/learn/ben-marriott]. His Motion
Foundation course sequences it the same way: week 2 "easing with the speed graph",
week 3 the "value graph editor" [source: https://www.benmarriott.com/motion-foundation].
School of Motion's primer defines the two: the Speed Graph is "a visual representation
of the speed of your movements (out of a possible 100)" and the Value Graph "a visual
representation of the actual value of the property" [source:
https://www.schoolofmotion.com/blog/graph-editor-after-effects].

Builders working in GSAP never see either graph, so they need to know what each named
ease looks like on both, and how to go from an After Effects influence percentage or a
fitted bezier to a GSAP ease.

**What the shapes look like.**

| Motion | Value graph (value vs time) | Speed graph (velocity vs time) |
| --- | --- | --- |
| Linear | straight diagonal ("robotic constant-speed") | flat horizontal line |
| Ease out (arrive) | steep at the start, flattening into the target | starts at a peak on the left, descends to zero on the right |
| Ease in (depart) | flat at the start, steepening | starts at zero, rises to a peak at the right |
| Ease in-out | S-curve | dome, peak in the middle |
| Overshoot | curve passes the final value and comes back | curve dips below zero before settling |
| Hold | flat | zero |

Sources for the table: olafmotion (flat line, straight diagonal, S-curve, sharp spike
mapping) [https://olafmotion.com/tutorials/how-to-use-graph-editor/]; designkkashi
("Easy Ease: perfect dome", "Ease Out: upward slope from zero", "Ease In: downward
slope to zero") [https://designkkashi.com/en/after-effects-graph-editor-speed-value-influence-guide/];
Mt. Mograph on overshoot ("In the speed graph, the curve dips below zero"; on the value
graph "the curve extends beyond the final keyframe value then curves back")
[https://mtmograph.com/blogs/tools/how-to-use-the-graph-editor-in-after-effects and
https://motion.mtmograph.com/m-screens/easing/speed-graph].

Naming trap: After Effects calls "Ease Out" the keyframe you leave and "Ease In" the
keyframe you arrive at, so its "Ease In" is GSAP's `.out`. School of Motion's
frame-by-frame lesson uses the animator's older vocabulary the other way round again
("Ease In (cushioning in): you start out really fast and you kind of slow into the
motion") [source: https://schoolofmotion.com/blog/photoshop-animation-eases]. GSAP's
own definitions settle it for this contract: `.in` "start slow and end faster", `.out`
"start fast and end slower", `.inOut` "start slow and end slow" [source:
https://gsap.com/resources/getting-started/Easing/]. Always write the GSAP name, never
"ease in/out" in a spec.

**Which graph for what.** Speed graph "for timing and feel", value graph "for spatial
control and avoiding unwanted overshoot" [source: https://olafmotion.com/tutorials/how-to-use-graph-editor/].
Speed graph for "snappy UI animations", value graph required for "bounces, overshoots,
complex arc trajectories" [source: designkkashi]. The reason is that the value graph
shows where a curve crosses the target and lets you see the overshoot peak ("we will
also show at what value the overshoot peaks") [source:
https://motion.mtmograph.com/m-screens/easing/value-graph].

**Influence percentages and their GSAP equivalents.**

| AE influence on the arriving key | Feel (source) | Nearest GSAP `.out` [inference] |
| --- | --- | --- |
| 33% | "Casual smoothness, background elements" | `power1.out` to `power2.out` |
| 60-75% | "Polished deceleration, corporate/UI" | `power2.out` to `power3.out` |
| 75% both sides | symmetric, "highest speed point is actually in the middle" | `power2.inOut` to `power3.inOut` |
| 85-100% | "High-energy drama, kinetic typography" | `power4.out` to `expo.out` |

Sources: tiers and the warning that above 95% on both sides objects "teleport"
mid-curve, "Keep it at 90% or below" [https://designkkashi.com/en/after-effects-graph-editor-speed-value-influence-guide/];
75% as the general smooth setting [https://www.kelp.agency/blog/using-the-graph-editor-in-adobe-after-effects/];
75 on both sides for a symmetric curve with the peak in the middle (Jerron Smith)
[https://vdci.edu/learn/after-effects/mastering-motion-animations]. The GSAP column is
an inference: AE influence controls handle length, GSAP `powerN` controls the exponent,
and the two families are not the same curve; the fit tool decides.

**Measurable form.**

- A named ease is a hypothesis, not a fact. `segment.mjs` returns "a least-squares
  best-fit GSAP ease for every monotonic motion it finds, with runners-up and RMSE"
  [source: `manifesto/SKILL.md` §3.2]. The measured lockup in the ABE clone needed
  fitted cubic-beziers, x `(0.31,0.15,0.07,1)` over 53 frames and scale
  `(0.68,0.30,0.06,0.93)` over 40 frames, 0.85 px RMSE against 3.83 px for the best
  named ease; `expo.out` could not fit because "it is fastest on frame 1, the reference
  is slowest" [measured: `<builds>/abe-ad/FINDINGS.md`].
- Per-frame step profile of a moving edge should be monotone for a single ease
  (example: -2, -6, -10, -14, -18, -23, -26, -30, -31, -27, -22, -19, -14, -10, -6 px is
  "a clean ease with no snapping") [measured: `manifesto/SKILL.md`, "Choppy" is
  usually not a frame-rate problem].
- Peak speed location: an `out` ease peaks on its first frame, an `in` ease on its
  last, `inOut` at the midpoint. For a velocity-matched cut the peaks of exit and entry
  must meet at the cut within about 5% [source:
  `hyperframes-creative/references/beat-direction.md`, Velocity-Matched Transitions].
- Ease variety: **delete both quotas.** "No more than 2 independent tweens with the same
  ease in a scene" [source: `hyperframes-creative/references/motion-principles.md`] and
  "at least 3 different easings" per composition [source:
  `hyperframes-animation/techniques.md`] both contradict two other rules in this document
  -- Rule 9's "same easing family across a stagger, vary start time only" and Rule 11's
  "reuse the ease family" -- and a quota encourages the specific failure this document
  warns about elsewhere, a different curve on every element, which is the agent-made look.
  A house style *is* a consistent curve; variety belongs in duration and distance. Expect
  two to four distinct curves per piece as a consequence of having distinct registers
  (entrances, camera, ambient, exits), and treat a piece using more than about five as
  unresolved rather than varied [inference; studio practice is to build a piece on one or
  two custom curves].

**Code-level implication.**

- Map: AE speed-graph ease on the arrival key → GSAP `.out`; on the departure key →
  `.in`; both keys → `.inOut`. Overshoot that shows as a negative dip on the speed graph →
  `back.out(n)` with n from the fit, or the baked spring at damping 0.6-0.7 [source:
  `gsap-easing-and-stagger.md`].
- When the fit returns a cubic-bezier, **write it as SVG path data**, which is
  CustomEase's documented input:
  `CustomEase.create("name", "M0,0 C0.31,0.15 0.07,1 1,1")`. The four-bare-numbers form
  `CustomEase.create("name", "0.31,0.15,0.07,1")` that this document previously showed is
  not the documented syntax and will fail at runtime or silently produce the wrong curve,
  which is a build-breaker in an otherwise correct recipe. Verify the string parses before
  shipping. Related and worth stating in the same place: cubic-bezier control points live
  in (time, progress) space, so a curve fitted against measured pixel positions is only
  interchangeable with a CSS `cubic-bezier` if the fit was performed in that same
  normalised space. CustomEase has been free since GSAP 3.13 [source:
  https://gsap.com/docs/v3/Eases/CustomEase/ ; https://gsap.com/blog/3-13/].
  If the plugin cannot be loaded, a bezier can be evaluated as a function ease, which
  the contract permits because it is a pure function of progress [inference from the
  Spring Eases section of `gsap-easing-and-stagger.md`, which does exactly this].
- Where the reference shows a slow-fast-slow group slide that no single ease fits,
  chain three tweens on one property: `power3.in` for about 10% of distance over about
  20% of time, `none` for about 65% over about 18%, `power4.out` for about 25% over
  about 62%, tail at least 3x the ramp-in in time [source: `hyperframes-animation/rules/nudge-curve.md`].
- Do not model an AE speed graph with a real-time spring; a stateful integrator cannot
  be seeked. Bake the closed form [source: `gsap-easing-and-stagger.md`, Spring Eases].

---

## Rule 5. Easing direction and the velocity-matched cut

Covered in the local references; stated here only as the checkable form so the grader
has one place to look.

- `.out` for entering, `.in` for leaving, `.inOut` for moving between positions; "You
  get this backwards constantly" [source: `hyperframes-creative/references/motion-principles.md`].
  Same rule in Material ("deceleration" for entering, "acceleration" for permanently
  exiting) [source: https://m1.material.io/motion/movement.html] and NN/g ("Ease-out for
  elements entering the screen; Ease-in for elements leaving") [source:
  https://www.nngroup.com/articles/animation-duration/].
- Never linear for an **isolated** spatial move that starts and stops on screen. Linear
  is correct, and often the only correct choice, for anything **continuous**: loops,
  tickers, conveyors, endless backgrounds, a pan that is already moving when you cut into
  it and still moving when you cut out, and the constant-velocity plateau inside a
  compound move. If a move must be cut into or out of mid-flight, any easing at the
  boundary reads as a hitch at the cut, so the boundary segment has to be linear. This
  document contradicts itself one rule earlier otherwise: the nudge-curve recipe in Rule 4
  puts `none` on the middle 65% of the distance, which is linear spatial movement, and
  that recipe is correct. A grader that fails all linear spatial tweens will fail a
  correctly built through-move and a correctly built loop [source:
  `motion-design/director/disney-principles.md` §6; `gsap-easing-and-stagger.md` ease
  table, for the isolated case; the continuous exemption is inference].
- Velocity match: exit `y:-150, blur 30px, 0.33s power2.in`; entry `y:150→0, blur
  30px→0, 1.0s power2.out` so "The fastest point of both curves meets at the cut"
  [source: `hyperframes-animation/techniques.md` §10]. Grader: peak velocities of the
  outgoing and incoming tweens at the cut frame within ~5% [source: `beat-direction.md`].
- Do not author an exit that **duplicates work a transition is already doing**: "The
  transition IS the exit", and the outgoing and incoming tweens sit at the same T
  [source: `hyperframes-animation/transitions/overview.md`, Animation Rules]. The blanket
  form of this rule ("exit animations are banned except on the final scene") is too
  strong and contradicts this document's own measurements: exits are **mandatory**
  wherever the frame goes empty between beats, and the ABE reference has 10 blank runs
  totalling 67 frames with interior gaps of 2, 1, 4, 5, 2, 2, 4, 2 and 8 frames. You
  cannot produce an empty frame without something exiting. The underlying engineering
  point is valid and is what to state: never stack an exit tween and a cross-transition
  on the same element at the same T [measured: `library/apple-business-essentials.md`;
  the restatement is inference].

---

## Rule 6. Arcs

**Why.** "Most natural action tends to follow an arched trajectory", straight lines
read as mechanical, and "Faster movement flattens arcs" [source:
https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation]. Material's product
version limits it: elements moving along a single axis do not arc, and elements
entering or leaving the screen move straight because "Arcing off-screen complicates the
entry point"; for diagonal moves "begin with a shallow ascent and end with a steep
ascent" when going up, the reverse going down [source: https://m1.material.io/motion/movement.html].

**Measurable form.**

- Perpendicular offset at the path midpoint, as a **fraction of the chord**: roughly 3-8%
  of the travel distance for corporate, 10-25% for organic or playful. Absolute pixels
  only mean something at a stated frame size: 15 px of sagitta on a 200 px move is a
  deliberate arc, the same 15 px on a 1600 px move is invisible, and on a 4K frame it is
  invisible on both. This is also how the control works in After Effects, where you drag a
  spatial bezier handle relative to the move and the bow scales with it [source:
  `motion-design/director/disney-principles.md` §7 gives the absolute figures (10-20 px,
  5 px corporate, 20 px+ playful) at UI scale; the fractional restatement is inference].
- Arcs only for two-axis moves in-frame; no arc on single-axis moves or on enter/exit
  [source: Material movement, above].
- No **sustained hero move that the viewer is meant to read and follow** travels more
  than 1/3 of the frame without a direction change, speed change or arc adjustment
  [source: `motion-design/director/choreography.md`, The 1/3 Rules -- which is a UI
  staging rule about not letting an element wander across a screen the user is trying to
  use]. **Transitions are exempt by class**: whip pans, full-frame wipes, cards flying
  through frame and infinite-zoom transitions all cross the entire frame in a straight
  line at a single acceleration, and should. Applied without that exemption the rule
  forbids most of the transition vocabulary Rule 8 enumerates [inference].
- Grader test: trace the centroid of a moving element (`card-motion.mjs` reports
  centroid per frame [source: `manifesto/SKILL.md`, product-UI vocabulary]); fit a line
  between start and end; the max perpendicular deviation is the arc depth. Compare to
  the register table above [inference].

**Code-level implication.**

- Two ways to arc under the contract, both pure functions of time: (a) MotionPath
  along an SVG path, `motionPath: { path: "M ... C ..." }` [source:
  `hyperframes-animation/techniques.md` §9]; (b) two tweens on `x` and `y` with
  different eases at the same position (Material's "shallow then steep" is `x` on
  `power2.out` against `y` on `power2.in` for a rising diagonal) [inference].
- Because the two-tween form puts two transform tweens on one element, it is allowed
  only when they animate different transform components; GSAP composes `x` and `y`
  into one transform, so it is not the "overlapping conflicting transform tweens"
  failure, which is about two tweens fighting over the same property [inference from
  `motion-principles.md`, Load-Bearing GSAP Rules]. If in doubt, put `x` on a wrapper
  and `y` on the child.

---

## Rule 7. Camera moves: push, pull, parallax with depth ratios, drift, focus

**Why.** A push-in "can reveal the character's state of mind", builds "dramatic
tension" and signals that a detail "matters to the story"; a push-in moves the camera,
a zoom changes focal length, and "only the push-in creates parallax and spatial depth
changes" [source: https://www.studiobinder.com/camera-shots/camera-movements/push-in-shot/].
A pull-out creates "distance, isolation, or loneliness" and is used to "unveil a
setting or conclude a scene by detaching the audience" [source:
https://beverlyboy.com/cinematography/camera-movements-explained-with-examples/].
Willenskomer's UI framing is the same: dolly moves the camera, zoom scales the object,
and zoom "communicat[es] that objects are 'inside' other objects or scenes" [source:
UX in Motion Manifesto]. **CSS has a lens.** The `perspective` property *is* the focal length and `translateZ` is
the dolly, which is not a workaround but how the CSS 3D transform pipeline is specified:
the perspective value is the distance from the viewer to the z = 0 plane. So the three
moves are distinguishable and each has its own construction. Animate **`translateZ` with
`perspective` fixed** for a true push, and correct per-layer parallax falls out for free.
Animate **`perspective` with `translateZ` fixed** for a zoom. Animate **both in
opposition** for a dolly zoom, which this document previously listed as unachievable.
Scale on a wrapper is a third thing, a crop-and-blow-up, and it is what most "push"
recipes actually produce -- which is why HTML camera moves so often read as a zoom on a
photograph rather than a move through space. The machinery is already in this stack: the
3D-flight rule below puts props at `translateZ` 80-300 px [CSS 3D transform
specification; the consequence is inference].

**Measurable form.**

Push/pull amounts (scale factor on the world wrapper):

| Effect | Scale | Read |
| --- | --- | --- |
| Subtle | 1.02-1.05 | "Barely perceptible, professional" |
| Medium | 1.05-1.15 | "Ta-da" emphasis |
| Noticeable | 1.15-1.30 | focus on region |
| Dramatic | 1.5-2.5 | element fills screen |
| Full-screen | 3.0+ | element covers viewport |

[source: `hyperframes-animation/rules/viewport-change.md`, Values]. Ken Burns on a
still is scale 1 → 1.04 over the beat [source: `hyperframes-creative/references/motion-principles.md`,
Image Motion Treatment]. A three-phase camera runs 0.88-0.96 → 0.98-1.02 → 1.04-1.15
[source: `hyperframes-animation/rules/multi-phase-camera.md`].

Push/pull timing: a targeted zoom starts after "content landed + ~0.5s scan time",
takes 1.0-2.0 s ("under 0.8s teleports, over 2.5s drags"), and dwells at least 1.0 s
after settling [source: `viewport-change.md`, Values]. Phase settles of 1.0-1.8 s and
1.0-2.0 s in the multi-phase rule [source: `multi-phase-camera.md`]. Camera eases are
`power2.out`, `power3.out`, `power2.inOut`; "spring/back easing on a camera feels
uncomfortable" [source: same]. 3D flight landings `power4.out`, repositioning
`power2.inOut` [source: `hyperframes-animation/rules-index.md`, `3d-camera-flight`].

Parallax depth ratios (displacement of a layer relative to the reference layer):

| Layer | LottieFiles | Lumitree | Implied depth (Lumitree) |
| --- | --- | --- | --- |
| Foreground | 1.0x | 1.0-1.8x | 1x |
| Midground | 0.5x | 0.5-0.8x | 1.8x to 3.6x |
| Background | 0.2x | 0.15-0.3x | 9x |

[source: `motion-design/director/choreography.md`, Depth Through Speed; source:
https://lumitree.art/blog/parallax-effect , which states "apparent angular velocity is
inversely proportional to distance" and that its 0.2x / 0.5x / 1.0x / 1.8x speeds
"roughly correspond to depth ratios (9x, 3.6x, 1.8x, 1x)", recommending three to four
layers and noting four to six layers as the point of diminishing returns]. **Fixed ratios are correct only for a LATERAL move.** The Lumitree statement ("apparent
angular velocity is inversely proportional to distance") is the lateral case. For a
**push**, a layer's apparent displacement and scale both follow `d / (d - t)` as the
camera travels distance `t` toward a layer at depth `d`, so the ratio between layers
changes continuously through the move and cannot be a constant. Substituting the lateral
constants into a push gives layers that separate linearly when they should separate
hyperbolically, which is exactly what makes a fake push read as a set of sliding planes.
Author the push in `translateZ` and let the transform derive it. **Then counter-scale
each layer by its own `d / (d - t)` at rest** so it holds its designed size in the frame:
any element pushed back on Z arrives smaller than the layout intended, and if that is not
compensated the type sizes in the design spec no longer hold. That counter-scale step is
the standard production trap here [inference from the Lumitree statement and the
projection arithmetic]. Willenskomer: objects that move quicker "appear
to the user as 'closer'" [source: UX in Motion Manifesto, Parallax]. In HyperFrames 3D
flight, props sit at `translateZ` 80-300 px: "higher = stronger parallax, earlier
fly-past" [source: `3d-camera-flight.md`, Values].

Drift on holds. **This is a register, not a law**, and the earlier phrasing ("the camera
never fully stops") stated one contemporary style as universal. Locked-off is a deliberate
and common choice: product hero shots, Swiss-influenced graphics and most title cards lock
off completely, and perpetual low-amplitude drift is a large part of why so much current
explainer work looks interchangeable. It also fights Rule 10's legibility requirement,
because drifting text is text you are still tracking. Attach drift to handheld,
documentary and organic registers, and to the case where a hold is long enough to feel
dead. Amplitude when used: 2-8 px X and 1-4 px Y, 1-3
cycles over the whole composition, X and Y frequencies in ratio 1.2-1.5 ("1.0 = perfect
diagonal (mechanical); ~1.3 = organic Lissajous") [source: `multi-phase-camera.md`, Values].

Focus as a camera tool: rack or pull over 0.5-1.2 s; 3-6 px blur per depth step; terminal
blur 8 soft, 16 default, 24 heavy; dim off-focus layers to 0.4-0.7 opacity, rarely below
0.35 because "fully dark reads as 'removed'"; focal layer stays at 0 px [source:
`hyperframes-animation/rules/depth-of-field-blur.md`, Values]. Style-frame hierarchy
says the same from the design side: "A blurred background pushes the sharp foreground
forward" [source: https://artofstyleframe.com/blog/visual-hierarchy-motion-graphics/].

Grader tests: on a push, bounding box width and height grow together (`w` and `h`
rising in `card-motion.mjs` is "a push-in") and the ratio of a small element's width at
two frames gives the exact factor (a 69 px link becoming 375 px is a 5.4x push)
[measured: `manifesto/SKILL.md`, product-UI vocabulary]. On a parallax pan, track one
element per layer; displacement ratios should sit on the depth table above [inference].

**Code-level implication.**

- One `.world` wrapper, one writer of its transform; counter-translate math is
  `T = -offset × S` when scale and translate compose on the same element, and
  `T = -offset` when the inner wrapper translates and the outer scales; the two rules
  are different and mixing them lands the target off-center [source:
  `hyperframes-animation/rules-index.md`, `viewport-change` and `coordinate-target-zoom`].
- Author the world at 1x and open scaled-in for a workspace reveal; scaling the world
  down for the wide frame "drops every label below legible pixel size" [source:
  `viewport-change.md`, Extreme range].
- Parallax layers are separate children of the world, each with its own `x` tween at
  `ratio × cameraTravel`, all at the same position and with the same ease so they share
  a velocity profile [inference; the LottieFiles rule "same easing family, vary only
  start time" for staggers applies by analogy].
- Blur via a `--dof` custom property tweened on the timeline so it stays on the seek
  clock; never bare `gsap.to` [source: `depth-of-field-blur.md`; `motion-principles.md`,
  Ambient pulses must attach to the seekable `tl`].
- A camera is the one place a linear ease is legitimate ("Camera moves with timed
  counterpoint") [source: `gsap-easing-and-stagger.md` ease table].

---

## Rule 8. Object cuts, match cuts, and continuity across cuts

**Why.** A match cut is a transition where "the composition of the two shots are
matched by the action or subject and subject matter"; a graphic match is when "the
shapes, colors and/or overall movement of two shots match in composition"; both belong
to continuity editing, which "smooths over the inherent discontinuity of shot changes"
[source: https://en.wikipedia.org/wiki/Match_cut]. StudioBinder groups the types as
graphic match, match on action, and sound bridge, with the graphic family split into
symbolic, color and temporal matches [source:
https://www.studiobinder.com/blog/match-cuts-creative-transitions-examples/]. School
of Motion's six essential transitions are hard cut, dissolve, cut on action, match cut,
dynamic/infinite zoom and morph, with hard cuts suited to "fast-paced action" and to
"re-time clips to an audio beat" [source:
https://schoolofmotion.com/blog/six-essential-motion-design-transitions-tutorial].
Screen direction obeys the 180-degree rule: crossing the axis "can be disorienting"
because "spatial relationships become reversed" [source:
https://en.wikipedia.org/wiki/180-degree_rule]. HyperFrames' "Transitions are meaning"
framing: crossfade says "this continues", hard cut says "wake up", slow dissolve says
"drift with me" [source: `hyperframes-creative/references/motion-principles.md`].

**Measurable form.**

- Object persistence: an element that survives a cut keeps position, scale and travel
  direction across the cut frame; in the manifesto's morph card, "shared letters
  persist; outgoing letters fade on measured frames; new text absolutely positioned at
  a `measureText` offset" [source: `manifesto/SKILL.md` §6 technique map].
- Direction continuity: all elements of one scene enter from the same direction or
  origin, "Mixed directions = chaos" [source: `motion-design/director/choreography.md`,
  Spatial Origin Consistency]; across a cut, travel direction should not reverse
  unless the reversal is the point [inference from the 180-degree rule].
- Velocity continuity: peak velocity of exit and entry within ~5% at the cut [source:
  `beat-direction.md`]; ease families paired `.in` then `.out` [source: `techniques.md` §10].
- Transition budget: one primary transition for 60-70% of scene changes plus 1-2
  accents; "Never use a different transition for every scene" [source:
  `hyperframes-animation/transitions/overview.md`]. Durations by energy: calm 0.5-0.8 s,
  medium 0.3-0.5 s, high 0.15-0.3 s; opening 0.4-0.6 s, between related points 0.3 s,
  wind-down 0.5-0.7 s, outro 0.6-1.0 s [source: same file, Energy and Narrative
  Position tables].
- Blank frames as cuts: kinetic pieces "cut through blank frames. A card ends, the
  frame goes empty for 1-8 frames, the next card begins"; the measured ABE reference has
  10 non-zero blank runs totalling 67 frames, longest 37 (the cold open), and the
  individual gaps are 2, 1, 4, 5, 2, 2, 4, 2, 8 frames [source: `manifesto/SKILL.md` §3.2;
  measured: `library/apple-business-essentials.md` and `abe-ad/FINDINGS.md`].
- Audio lock: 12 of 23 cuts landed within 0-2 frames of an audio onset [measured:
  `abe-ad/FINDINGS.md`]. The cuts sit close to a 149.9 BPM grid (12.008 frames per beat
  at 30 fps) "but are not quantised to it", and the slight anticipation "is part of why
  it feels driven rather than mechanical" [measured: `library/apple-business-essentials.md`].
- Grader tests: (a) run `segment.mjs` on the render and compare cut frames one-for-one
  with the plan [source: `manifesto/SKILL.md` §7]; (b) `card-motion.mjs --cmp` on the
  frames either side of each cut, checking the persisted element's centroid and box are
  continuous [inference]; (c) `audio-beats.mjs` reports how many cuts land within 3
  frames of an onset [source: `manifesto/SKILL.md` §3.6].

**Code-level implication.**

- Write every clip boundary from its frame number, biased inward:
  `start = frame/fps - 0.0002; duration = (endFrame + 1 - frame)/fps - 0.0011`; the
  inclusive-end and rounded-up-start traps put 11 of 29 clips a frame late [measured:
  `manifesto/SKILL.md` §7, frame-boundary trap].
- Outgoing and incoming tweens at the same `T`; the outgoing scene is fully visible when
  the transition starts [source: `transitions/overview.md`].
- For a match cut on a persisted object, the object exists once in the DOM across both
  scenes or is duplicated at identical geometry; give it a `tl.set` baseline at its
  card's first frame so a render worker that seeks past a fade-out does not latch it
  hidden (the render-order trap that blanked 13 frames) [source: `manifesto/SKILL.md` §6].
- Never straddle a cut with a shutter window: motion blur is applied per card, held one
  frame clear of every cut [source: `manifesto/SKILL.md`, The shutter].

---

## Rule 9. The "everything moves at once" failure and the stagger cap

**Why.** Staging is "the presentation of any idea so that it is completely and
unmistakably clear" [source: Twelve principles, Wikipedia]. If every element is in
motion the viewer has nothing to follow; the style-frame article's rule is "Trust the
viewer to read a single dominant signal" and that crowding "causes the eye to stall"
[source: https://artofstyleframe.com/blog/visual-hierarchy-motion-graphics/]. The
opposite failure is a stagger so long that the group never reads as one arrival. Both
have hard numbers.

**Measurable form.**

- Density: with 3 or more animated elements, at most 1/3 active simultaneously
  [source: `motion-design/director/choreography.md`, The 1/3 Rules]; attention budget
  "Max 2-3 elements in active motion simultaneously", ambient excluded [source:
  `motion-design/director/core-philosophy.md`].
- Stagger cap, **UI-scale groups only** (cards, chips, list rows): total stagger under
  500 ms regardless of item count [source:
  `motion-design/reference/timing-easing-tables.md`; `hyperframes-creative/references/motion-principles.md`;
  `hyperframes-animation/rules-index.md` contract: `items × stagger ≤ ~0.5s`].
- **For per-character or per-word kinetic type the cap is 1.5 to 2.5 s for a full line**,
  and the real constraint is that the step must be at least 1 frame, preferably 2. A
  40-character headline revealed at 2 frames per character at 30 fps is an 80-frame sweep,
  2.67 s, which is a completely standard reveal that the 0.5 s cap forbids [inference;
  note that the manifesto's own measured Apple cascade is 11 units over about 20 frames of
  sweep at 60 fps, which passes only because the reference happened to be short].
- Self-capping step: `STAGGER = min(0.06, 0.5 / ITEM_COUNT)`. **Switch to a wipe when the
  step drops below one frame, not at a fixed item count.** The formula gives 0.031 s at 16
  items, which is 0.94 frames at 30 fps: consecutive items land on the same rendered frame
  and the stagger stops existing. So it fails silently above 16 items at 30 fps and above
  31 at 60, while the stated cutoff of 9 is neither of those [source:
  `hyperframes-animation/rules/spring-pop-entrance.md`, Values, for the formula and the
  9-item note; the failure analysis is arithmetic].
- Stagger step by pattern: micro cascade 20-40 ms (budget under 200 ms), standard
  50-100 ms (under 400 ms), dramatic 100-200 ms (under 600 ms), wave 30-60 ms (under
  500 ms) [source: `timing-easing-tables.md`, Stagger Patterns]. Card streak-in
  0.05-0.12 s per card, "one assembling wave, not separate arrivals" [source:
  `hyperframes-animation/rules/motion-blur-streak.md`].
- Same easing family across a stagger; vary start time only; optional overshoot on the
  last element as punctuation [source: `choreography.md`, Stagger Patterns].
- Performance ceiling: under 20 animated elements per viewport [source:
  `motion-design/reference/quality-checklist.md`].
- Grader test: sample the timeline every frame and count targets with a non-zero
  tween velocity; flag any frame where the count exceeds max(3, N/3) for non-ambient
  targets, and any group whose last start minus first start exceeds 0.5 s [inference
  from the figures above].

**Code-level implication.**

- `stagger: { each: Math.min(0.06, 0.5 / n), from: "start" | "center" | "edges" }`
  [source: `gsap-easing-and-stagger.md`; `spring-pop-entrance.md`].
- `from: "random"` is not documented as deterministic [source:
  https://gsap.com/resources/getting-started/Staggers/ , which does not specify] and
  GSAP's contract here forbids `Math.random` outright, so a "random" order must be an
  index-derived hash baked into a `from` index array or a function-based delay
  [source: `hyperframes-animation/rules-index.md`, deterministic clause; the hash
  pattern is in `techniques.md` §2].
- Ambient motion on held elements is one tween per scene ("alive with ONE ambient
  motion") [source: `motion-principles.md`, Scene structure], finite repeats, on the
  timeline.

---

## Rule 10. Hold and breath: how much of a beat is motion versus stillness

**Why.** "A common mistake beginners make is packing every second with movement"; the
pauses "make the fast moments feel faster and the big moments feel bigger" [source:
https://www.story-boards.ai/content-hub/blog/understanding-timing-and-transitions-in-motion-graphics-storyboarding].
HyperFrames: "Stillness after motion is powerful" [source: `motion-principles.md`,
Guardrails]. The ABE reference's blank gaps "are load-bearing for pacing" [source:
`manifesto/SKILL.md` §9]. And text that is still moving cannot be read: the legibility
standard requires animated text to "remain motionless for a minimum of 1 second per 13
characters" [source: https://legibility.info/rules-for-text-in-videos].

**Measurable form.**

Scene phase shares (three published models, all within a band):

| Model | Build / setup | Hold / breathe / action | Resolve |
| --- | --- | --- | --- |
| HyperFrames build/breathe/resolve | 0-30% | 30-70% | 70-100% |
| LottieFiles setup/action/resolution | 20-30% | 30-40% | 30-40% |
| LottieFiles four-act, 800 ms+ | 20% anticipation | 30-35% action, 15-20% reaction | 25-30% |

[source: `hyperframes-creative/references/motion-principles.md`; `motion-design/director/choreography.md`,
Sequence Structure; `motion-design/director/narrative-structure.md`, Scaling to Duration].
The HyperFrames model is the one written for video beats; the LottieFiles models are
UI-scale (their 800 ms+ row is their longest tier). Read across them: motion occupies
roughly 30-40% of a beat at the front, a hold occupies roughly 40%, and the resolve is
the rest [inference].

Hold minimums for text:

**Two reading rates appear in this rule and they differ by about 6x for the same text.
Reconcile before using either.** 13 characters per second (roughly 137 wpm) is a
**subtitle** standard, built for small type read while the viewer is simultaneously
watching action, and it prices a long word the same as several short ones. The 4 words per
second (roughly 20 cps) in the ad-overlay row below is a **display-type** figure: display
typography is read as a shape, not scanned character by character. They cannot both drive
a grader, and the appendix silently adopted the stricter one, which fails a great many
professionally paced cards. **Use character count only for subtitle-scale text; for
display type budget about 2.5-3 words per second with a floor of roughly 0.8 s of settled
time for any text element however short, and add time for a second line rather than for
characters.** Note also that the rule says *motionless* while the practical requirement is
*settled*: a slow settle or an ambient drift under 1 px per frame does not impair reading.

- 13 characters per second, so a 30-character line needs at least 2.3 s; at most 30
  characters per line and 3 lines at once [source: https://legibility.info/rules-for-text-in-videos ,
  citing FFA and ARD/ORF/SRF/ZDF subtitle standards -- **subtitle scale**].
- Ad overlays: 1.5-3 s per text card, 5-8 words per card, at most 2 lines, entrance
  animation 150-250 ms, no more than 200 ms between cards, text appearing 0.1-0.3 s
  before the spoken word, on the premise that "the average adult reads roughly 4 words
  per second" [source: https://www.rocketshiphq.com/text-overlays-video-ads-mobile/].
- HyperFrames: "3 seconds on screen = must be readable in 2. Fewer words, larger type"
  [source: `hyperframes-creative/references/typography.md`].
- After a resolution, 100-200 ms of stillness before new motion [source:
  `choreography.md`, Sequence Structure; `narrative-structure.md`, Act 4].
- Climax dwell after a camera zoom: at least 1.0 s [source: `viewport-change.md`].
- Measured skeleton: recomputed from the ABE reference's own cut list, **median segment
  1.067 s, mean 1.073 s, max 2.4 s, min 0.1 s (3 frames)**, while its fast cluster puts
  three cuts inside 18 frames. (The "median 2.833 s" figure carried by the library entry
  and repeated here is arithmetically impossible: 25.867 s over 23 segments is a mean of
  1.12 s, so a median of 2.833 s would need twelve segments totalling over 34 s.) Its 67
  blank frames are 8.6% of 776 [measured: `library/apple-business-essentials.md`;
  recomputation is arithmetic].

Grader tests: (a) the shipped `LEGIBILITY` check samples contrast only in the settled
window `[start + 0.35 s, start + 0.62 × duration]`, which is the operational definition
of "hold" used in this repo [source: `manifesto/scripts/grade-original.py`]; (b) per
beat, motion fraction = frames where the hero's ink count or centroid changes above the
grain floor / beat frames; flag beats with motion fraction above ~0.7 (no hold) or below
~0.1 with no ambient (dead). **Both bounds are pure inference, read across three phase
models from two different disciplines; expose them as tuning parameters rather than
printing them in the grader appendix next to measured values** [inference]; (c) reading
check: settled seconds ≥ characters / 13 for subtitle-scale text only, and words / 2.75
with a 0.8 s floor for display type [source: legibility.info; the split is inference].

**Code-level implication.**

- Author a hold as an explicit `tl.set` or as the gap between the entrance tween's end
  and the exit's start; the grader cannot distinguish a hold from a broken tween unless
  the frames are bit-identical, and bit-identical frames are themselves a failure
  ("duplicate consecutive frames ... 0") [source: `grade-original.py`, FRAME check].
  So a hold usually carries one bounded ambient motion: sine breathe at 0.6 px focus or a
  1.4% idle push, finite `repeat`, `yoyo: true` [source: `depth-of-field-blur.md`,
  FOCAL_BREATH_PX; `grade-original.py` comment on the linear idle push]. **Exempt
  deliberate freezes**, in particular the final logo or end card, and any hard hold used
  as a device: most brand end cards are literally static for 1.5-3 s, a freeze frame is a
  standard device, and a rule that bans duplicate frames everywhere bans the most common
  closing shot in the medium. Worse, it invites the failure it is trying to catch, because
  an agent under a no-duplicate-frames rule will add a breathing scale to a lock-up that
  should be locked off, and a logo that breathes is a brand-guidelines violation on most
  accounts. Check instead for **unintended** duplicate frames inside a segment that is
  supposed to be moving, and judge runs against a declared cadence so animation on twos
  and posterised time pass [inference].
- Reproduce blank gaps as authored empty frames between clips, not as a fade to black
  [source: `manifesto/SKILL.md` §3.2].
- The grader-friendly form of "readable in 2 s": entrance done by 0.35 s into the beat
  and exit not before 62% of the beat, which is the settled window above [inference from
  the grader constants].

---

## Rule 11. Beat and rhythm: contrast between fast and slow inside one piece

**Why.** Timing conveys weight and mood: a 2-frame move is "light, energetic, and
frantic", a 20-frame move "heavy, significant, and serious" [source:
https://www.story-boards.ai/content-hub/blog/understanding-timing-and-transitions-in-motion-graphics-storyboarding].
A piece with one speed has no rhythm. HyperFrames: "Don't use the same speed on
everything ... The slowest scene should be 3x slower than the fastest" [source:
`motion-principles.md`, Guardrails], and "Name the pattern, fast-fast-SLOW-fast-SHADER-hold,
before implementing" [source: `beat-direction.md`, Rhythm Planning]. The measured
reference is bimodal: "a burst of very short cards ... against long held ones. That
contrast is the pacing signature; averaging it away produces a film that feels nothing
like the reference" [measured: `library/apple-business-essentials.md`].

**Measurable form.**

- Slowest scene / fastest scene duration ratio ≥ 3 [source: `motion-principles.md`].
  The ABE skeleton runs 0.067 s minimum to 2.833 s median, a ratio above 40 across the
  whole film and about 16 between the median hold and the fast cluster [measured:
  `library/apple-business-essentials.md`; arithmetic].
- Coefficient of variation of spoken-beat lengths ≥ 0.18, because "A run of identical
  beat lengths reads as a metronome; the graded reference's cards vary by a factor of
  four" [source: `manifesto/scripts/grade-original.py`, MOTION pacing check].
- Speed tiers as weight: fast 0.15-0.3 s (energy, urgency), medium 0.3-0.5 s, slow
  0.5-0.8 s (gravity, luxury), very slow 0.8-2.0 s (cinematic) [source:
  `motion-principles.md`, Speed communicates weight].
- Percussive pieces: beat spacing 1.2-1.8 s ("<0.8s frantic, >2.5s loses the pulse"),
  entrance attack 0.35-0.6 s, exits ≤ 0.25 s [source: `hyperframes-animation/rules/kinetic-beat-slam.md`, Values].
- One beat array drives everything: "every element times off `BEATS[]` / `PULSE`; this
  is the single biggest lever for 'rhythmic'" [source: same file].
- Music grid: fit a tempo to your own cut list rather than the reference's music; the
  Systo derivation landed on 150 BPM, 12 frames per beat at 30 fps, structural cuts
  within 0.1-2.5 frames of a beat [measured: `<builds>/systo-26s/FINDINGS.md`].
- Cuts may anticipate the beat by a frame or two rather than sit on it [measured:
  `library/apple-business-essentials.md`, Music grid].
- Grader tests: (a) beat-length CV ≥ 0.18 [source: grader]; (b) max/min scene duration
  ≥ 3 [source: HyperFrames]; (c) fraction of cuts within 3 frames of an audio onset,
  reported, not thresholded, because the reference itself was 12 of 23 [measured].

**Code-level implication.**

- Declare the grid once: `var PULSE = 60 / BPM; var BEATS = [...]` and position every
  tween at `BEATS[i] + offset` [source: `kinetic-beat-slam.md`].
- Vary the entrance per beat but reuse the ease family; vary duration deliberately
  across scenes; give each scene its own stagger [source: `motion-principles.md`, Guardrails].
- Hard cuts for rapid-fire runs of 3 or more tempo-matched switches; shader or CSS
  transitions for centerpiece beats; "Anytime a 0.3-0.8s transition would feel too slow"
  use a cut [source: `beat-direction.md`, Transition table].

---

## Rule 12. Motion hierarchy: what moves first is most important

**Why.** "The element that moves first is perceived as most important. Stagger in
order of importance, not DOM order" [source: `motion-principles.md`, Choreography is
hierarchy]. "Time is hierarchy. The first element to appear is the most important. In
video, sequence replaces position" [source: `hyperframes-creative/references/typography.md`].
Style-frame practice names it "Temporal Entry: the choreography of what arrives first
establishes hierarchy", with "One element wins" and "Only one element should punch at
maximum brand saturation" [source: https://artofstyleframe.com/blog/visual-hierarchy-motion-graphics/].
Movement itself is attention: "A small word animating aggressively while a large
headline sits still can dominate a frame, because movement equals attention" [**source not read**: https://madegooddesigns.com/motion-design-principles/ was seen only
as a search summary. A summary is not a source, so this is quoted as a general observation
with no citation and nothing in this document depends on it].

A contradiction in the local material to resolve: LottieFiles' Staging entry says "Hero
enters 100-200ms after supporting elements" [source: `disney-principles.md` §3], while
its Choreography file says "Lead with the Hero" [source: `choreography.md` §1] and
HyperFrames says the first mover is the most important. Both patterns exist in
practice: a UI modal dims the backdrop before the dialog lands (context first), a title
card lands the hero word first (hero first). The rule that reconciles them: whatever
moves first is what the viewer will treat as the subject, so if the supporting layer
moves first it must be a low-amplitude, low-contrast preparation (a dim, a panel) and
the hero must still own the largest displacement and the most emphatic ease
[inference].

**Measurable form.**

- Hero has the largest displacement and the most attention-grabbing ease; supporting
  elements are "subtler in every dimension" [source: `choreography.md` §1].
- One hero motion per scene moment [source: `core-philosophy.md`, Attention Budget].
- Hero visible by t ≤ 0.5 s of its beat [source: `spring-pop-entrance.md`, POP_DUR note].
- Amplitude tiers primary 100 / secondary 30-50 / ambient 10-20% [source: `core-philosophy.md`].
- Two focal points minimum per scene and three layers minimum, so the hierarchy has
  something to be a hierarchy of [source: `motion-principles.md`, Visual Composition].
- Grader test: rank elements by onset within the beat and by **change in visual weight**
  (roughly area x contrast change), not by peak displacement. Displacement is not what
  makes an element the hero: a logo that fades up on zero displacement is the hero of its
  beat, and a large headline that settles 12 px outweighs a small chip that travels 200 px
  -- which is precisely the effect the quotation in this rule describes ("a small word
  animating aggressively while a large headline sits still can dominate a frame"). A
  displacement-ranked test would fail a correctly hierarchical build and reward the failure
  the quotation warns about. If a robust visual-weight metric is not available, make this a
  review note rather than an automated check [inference; this replaces a displacement-based
  test that contradicted Rules 15 and 17 of this document].

**Code-level implication.**

- Order tweens by importance in the source, and let the position argument carry it;
  do not let `querySelectorAll` order become the stagger order.
- Per-word decay of travel (80 → 60 → 50 → 25 → 12 px) "mimics a camera settling" and
  puts the largest move on the first word [source: `techniques.md` §4].

---

## Rule 13. Scale of movement versus size of element (and distance)

**Why.** "Correct timing makes objects appear to obey the laws of physics" [source:
Twelve principles, Wikipedia]. Carbon: "the larger the change in distance (traveled)
or size (scaling) of the element, the longer the animation takes", on a non-linear
scale [source: https://v10.carbondesignsystem.com/guidelines/motion/overview/].
Material 1: longer durations when objects "travel large distances or have dramatic
changes in surface area", and larger screens need longer durations "so that movements
aren't too fast" [source: https://m1.material.io/motion/duration-easing.html]. Big
things are heavy; heavy things move slowly and travel with authority. Small things snap.

**Measurable form.**

- **Budget PEAK VELOCITY, not a distance multiplier.** Pick the speed the register
  allows, then let distance set duration. The distance-to-duration table (50 px 0.8x,
  100 px 1.0x, 200 px 1.3x, 300 px 1.5x, 400 px 1.6x, full screen 1.8-2.0x) is a **UI
  table**: it exists because an interface has a 400 ms ceiling and must compress long
  moves, and it makes a 20x distance take 2x the time, which is 10x the speed. Run it on
  film and it forces a violation of this document's own strobe rule by a factor of five:
  at the house 0.6 s default, a full-screen 1920 px move at the 2.0x cap is 1.2 s, 36
  frames at 30 fps, 53 px per frame of leading-edge travel against a stated ceiling of
  10 px. Keep the table only for depicted UI inside a product film [source:
  `timing-easing-tables.md`, Distance-Duration Scaling; the arithmetic and the
  replacement are inference].
- Weight tiers in a cascade: heavy 60-80 px over 0.16-0.20 s, light 30-48 px over
  0.10-0.13 s [source: `waterfall-entry.md`].
- Travel as a fraction of the element's own size: streak entrances start 40-120% of
  the element's own dimension away [source: `motion-blur-streak.md`, ENTER_FROM]; a
  pop's `Y_RISE` is 0-32 px, "never large enough to read as a slide-up" [source:
  `spring-pop-entrance.md`].
- Travel ceiling: no unbroken motion over 1/3 of the container [source:
  `choreography.md`]; max displacement 15-25% of container width depending on width
  [source: `motion-design/director/context-adaptation.md`, Responsive Motion].
- Element minimums: over 40 px to carry motion, over 100 px to carry detail [source:
  `quality-checklist.md`].
- Material's material-based scaling for feel: rigid 1.2x duration and 0% overshoot,
  paper 1.0x and 3-5%, fluid 1.5x and 5%, gas 2.0x and 0% [source: `timing-easing-tables.md`, Material-Based Easing].
- Strobe threshold, **as a fraction of frame width**: roughly **0.5% of frame width per
  frame** for hard high-contrast edges, up to about 1% with a shutter. Halve the tolerance
  at 24 fps and roughly double it at 60. An absolute pixel figure silently changes meaning
  across output resolutions (10 px is 0.52% of a 1920 frame, 0.26% at 3840, 1.04% at 960),
  and the classic camera-department form of the same limit -- roughly 5 to 7 seconds
  minimum for a pan to cross one frame width at 24 fps -- converts to about 0.6-0.8% of
  frame width per frame, which is where the number comes from. Contrast and edge hardness
  move it too: a blurred or soft-edged element travels two to three times faster before it
  steps [measured anchor: `manifesto/SKILL.md`, a measured 31 px per frame strobed with a
  perfect ease; the fractional restatement is inference].
- **The shutter recipe, corrected.** `tmix=frames=4` on a 240 fps stream integrates
  4 x 4.17 = 16.67 ms, which is the entire 60 fps frame interval: a **360-degree shutter**,
  twice the blur any camera produces, and it reads soft and slightly drunk. Every viewer's
  calibration for what motion blur looks like is set by the 180-degree cinema shutter,
  which exposes half the frame interval. **Use `tmix=frames=2` on the 240 fps stream, then
  `framestep=4` to land on 60 fps.** Reserve the 4-frame average for a deliberately dreamy
  or heavily smeared register, and consider `tmix=frames=1` (90 degrees, no averaging) for
  hard crisp action. Applied per card and held clear of every cut [the 240/tmix pipeline is
  `manifesto/SKILL.md`; the shutter-angle arithmetic and the correction are computed].
- Grader test: per moving element, peak px per frame of its leading edge; report
  elements above 10 px/frame on high-contrast edges as shutter candidates [source:
  threshold above; test is the `track.mjs` edge profile].

**Two consequences of scale that this rule previously omitted.**

- **Scale reads non-linearly.** Perceived size follows area, not linear dimension, so a
  linear value ramp from 0.2 to 1.0 appears to accelerate. Ramp scale on a curve, and never
  start a growth tween at exactly 0. This is why designers key scale in AE with an ease even
  when the timing is meant to be even [inference].
- **A camera push scales stroke weights with everything else.** A 1.5x push turns a 2 px
  rule into 3 px and can push type past its designed optical weight. It is the dynamic
  version of the static border-scaling note this document already carries, and it is caught
  in client review rather than in the build because it only shows at the end of the push
  [inference].

**Code-level implication.**

- Compute duration from travel: `dur = base * distanceFactor(px)` using the table
  above **for depicted UI only**, and from weight: anchors get the longer end of the range
  [inference; tables are sourced but UI-scoped].
- Large elements (a full-frame background, a hero wordmark) get the slow tier and no
  overshoot; small chips get the tight snap (`response 0.25-0.35`, duration 0.37-0.51 s
  on the baked spring) [source: `gsap-easing-and-stagger.md`, response table].
- Under the contract size change is `scale`, never `width`/`height`; a container that
  must grow uses a proxy-driven `scaleY` with inverse counter-scale on the content or a
  mask plus sheet slide [source: `rules-index.md`, `anchored-layout-expand`].

---

## Rule 14. UI motion numbers are not motion-graphics numbers

**Why.** The published design-system figures are tuned for interfaces a person uses
hundreds of times a day, where "the ideal animation duration is between 100ms and
500ms" and anything longer is a cost the user pays on every interaction. Apple's HIG:
"Use animation and motion effects judiciously. Don't use animation for the sake of
using animation" and "In general, avoid adding motion to interactions that occur
frequently" [source: iOS HIG animation text via https://codershigh.github.io/guidelines/ios/human-interface-guidelines/visual-design/animation/index.html ;
current page https://developer.apple.com/design/human-interface-guidelines/motion].
NN/g: "At 500ms, animations start to feel like a real drag for users" [source:
https://www.nngroup.com/articles/animation-duration/]. Val Head: "getting UI animations
to feel right is more important than the exact numbers behind them", and the 200-500 ms
range rests on 100 ms feeling instant and about 230 ms being needed to perceive a
change at all [source: https://valhead.com/2016/05/05/how-fast-should-your-ui-animations-be/].

A film is watched once, has no user waiting on it, and has to be legible at 30 fps
after H.264 compression. HyperFrames warns that "Subtle reads as static at 30fps. Err
toward more movement than feels safe" [source: `hyperframes-creative/references/video-composition.md`,
Motion Intensity] and that the design spec's web-scale decoration is invisible on video
(borders 1 px → 2-4 px, decorative opacity 3-8% → 12-25%) [source: same, Scale table].
The same logic applies to time: a UI's 200 ms modal is a film's chip.

**The UI numbers, for reference (so they are not copied by accident).**

| System | Durations | Easing |
| --- | --- | --- |
| Material 3 | short1-4: 50, 100, 150, 200 ms; medium1-4: 250, 300, 350, 400; long1-4: 450, 500, 550, 600; extra-long1-4: 700, 800, 900, 1000 | standard (0.2, 0, 0, 1); standard decelerate (0, 0, 0, 1); standard accelerate (0.3, 0, 1, 1); emphasized decelerate (0.05, 0.7, 0.1, 1); emphasized accelerate (0.3, 0, 0.8, 0.15) |
| Material 1 (mobile) | standard 300 ms; full-screen 375; entering 225; leaving 195; ceiling 400 ("feels too slow if exceeded"); tablet +30%; wearable -30%; desktop 150-200 | standard (0.4, 0, 0.2, 1); decel (0, 0, 0.2, 1); accel (0.4, 0, 1, 1); sharp (0.4, 0, 0.6, 1) |
| IBM Carbon | fast-01 70; fast-02 110; moderate-01 150; moderate-02 240; slow-01 400; slow-02 700 ms | productive standard (0.2, 0, 0.38, 0.9); expressive standard (0.4, 0.14, 0.3, 1); entrance productive (0, 0, 0.38, 0.9); exit productive (0.2, 0, 1, 0.9) |
| Apple (WWDC23 springs) | perceptual duration, default 0.5 s implied by the API; bounce 0 default, about 0.15 subtle, 0.30 noticeable, above 0.4 "may feel too exaggerated for a UI element" | spring, not bezier; HIG default bezier often quoted as (0.25, 0.1, 0.25, 1) |
| NN/g | feedback about 100 ms; modals 200-300; overall 100-500; 500 is a drag; disappear shorter than appear (300 in, 200-250 out) | ease-out most of the time |
| Val Head | 200-500 overall; small 200-300; large or complex easing 400-500 | not specified |

[sources: M3 values via https://www.mdui.org/en/docs/2/styles/design-tokens and the
vocut mirror, canonical https://m3.material.io/styles/motion/easing-and-duration/tokens-specs ;
M1 https://m1.material.io/motion/duration-easing.html ; Carbon
https://v10.carbondesignsystem.com/guidelines/motion/overview/ ; Apple springs
https://wwdcnotes.com/documentation/wwdc23-10158-animate-with-springs/ ; the (0.25, 0.1,
0.25, 1) curve as "Apple HIG" is from `timing-easing-tables.md` and is the CSS `ease`
keyword, not an Apple publication, so treat that attribution as [inference]; NN/g and
Val Head as above]. The LottieFiles skill, which is a UI skill, mirrors these: tooltip
80-120 ms, button 120-180, card 200-350, modal 300-400, page 400-600, dramatic reveal
600-1200, ambient 2000-20000 ms [source: `timing-easing-tables.md`].

**The motion-graphics numbers.**

| Thing | Film figure | Source |
| --- | --- | --- |
| Entrance on a beat | 0.35-0.6 s attack; hero visible by 0.5 s | `kinetic-beat-slam.md`; `spring-pop-entrance.md` |
| Entrance pop | 0.4-0.7 s | `spring-pop-entrance.md` |
| Standard settle (baked spring) | 0.51-0.74 s; weighted hero 0.74-1.03 s | `gsap-easing-and-stagger.md` |
| House default tween | 0.6 s `power3.out` | `gsap-easing-and-stagger.md`, Defaults |
| Exit | ≤ 0.25 s; entrance 0.4 s vs exit 0.25 s | `kinetic-beat-slam.md`; `motion-principles.md` |
| Scene transition | 0.15-0.3 s high energy to 0.5-0.8 s calm; outro up to 1.0 s | `transitions/overview.md` |
| Camera push | 1.0-2.0 s plus ≥ 1.0 s dwell | `viewport-change.md` |
| Rack focus | 0.5-1.2 s | `depth-of-field-blur.md` |
| Group slide | 0.57 s for 270 px in three phases | `nudge-curve.md` |
| Held card | median 2.83 s on the measured ad | `library/apple-business-essentials.md` |
| Fast card | as short as 0.067 s (2 frames) on the measured ad | same |
| Text hold | ≥ characters / 13 seconds; 1.5-3 s per overlay | legibility.info; rocketshiphq |

The two tables overlap only at the fast end. A film entrance of 0.6 s is a UI's
"extra-long" tier; a film hold of 2.8 s has no UI equivalent at all. The mistake to
avoid is importing M3 `medium2` (300 ms) as "the standard duration" for a title card.

**Measurable form.** A film composition whose tween durations all sit inside 100-500 ms
is almost certainly built on UI numbers; the grader can flag a composition whose 90th
percentile tween duration is under 0.5 s and whose longest hold is under 1.5 s
[inference]. The reverse error also exists: UI-scale figures are correct for a
product-UI film that is imitating a real interface (cursor click 0.9 → 1.0 scale over
two short tweens; typing at per-character `tl.set`), because there the subject is a UI
[source: `rules-index.md`, `physics-press-reaction`, `cursor-click-ripple`].

**Code-level implication.**

- Set the timeline default to the film scale, not the UI scale:
  `gsap.timeline({ paused: true, defaults: { duration: 0.6, ease: "power3.out" } })`
  [source: `gsap-easing-and-stagger.md`, Defaults].
- When the film depicts a UI, use the UI table for the depicted interactions and the
  film table for the camera, the cards and the type around them [inference].
- Reduced-motion variants are a UI requirement (Apple: "Make animations optional";
  LottieFiles context-adaptation table) and do not apply to a rendered video; a video
  has one rendered state [source: iOS HIG mirror; `context-adaptation.md`; inference for
  the last clause].

---

## Rule 15. Overshoot is a register, not a spice

**Why.** "Bouncy `back.out` is the #1 instant turn-off in agent-made videos and is
almost never executed well" [source: `spring-pop-entrance.md`]. Real system animations
"are critically damped or close to it, they barely overshoot, or don't at all" [source:
`gsap-easing-and-stagger.md`, Spring Eases]. Apple's own spring API defaults to bounce 0
[source: WWDC23 notes]. Overshoot is also what a value graph is for: "find where curves
cross the final value unintentionally, and pull Bezier handles inward" [source: olafmotion].

**Measurable form.**

- Overshoot budget by context: success 5-10%, error 0%, feedback 2-5%, celebration
  15-25%, premium 0% [source: `timing-easing-tables.md`, Overshoot Budget]; by
  personality: playful 10-20%, energetic 15-30%, corporate 0-3%, premium 0 [source:
  `motion-design/director/motion-personality.md`].
- Spring damping map: 1.0 no overshoot (house default); 0.80-0.85 about 1-1.5% ("felt,
  not seen"); 0.60-0.70 about 5-10% (explicitly playful); below 0.55 over 12% ("Don't")
  [source: `gsap-easing-and-stagger.md`]. `back.out(n)` with n ≤ 2 [source:
  `spring-pop-entrance.md`].
- Apple UI bounce: 0.15 subtle, 0.30 noticeable, above 0.4 exaggerated [source: WWDC23 notes].
- Grader: "Overshoot is a DIRECTION REVERSAL, not movement"; measure on ink count, not
  bounding box; segment on raw series at re-trigger jumps (> 1.15x), smooth within a
  segment with a 3-tap mean, flag any sign change of significant diffs (> 2% of mean)
  [source: `manifesto/scripts/grade-original.py`, MOTION check].

**Code-level implication.**

- Never hand-key a `scale: 1.1` mid-state; "it double-bounces against the curve"
  [source: `spring-pop-entrance.md`].
- If the fitted ease from the reference shows a negative dip on the speed graph, use
  the baked spring with `dampingFraction` chosen to match the measured overshoot
  percentage; take duration from the helper, tune speed through `response` [source:
  `gsap-easing-and-stagger.md`].

---

## Rule 16. Anticipation in graphics

**Why.** Anticipation "prepares viewers for upcoming action" [source: Twelve
principles, Wikipedia]. On a graph it is the first keyframe's handle dragged "opposite
the travel direction to create a wind-up effect" [source: designkkashi]. In graphics it
is a small counter-move, a dim, or a compression before the hit.

**Measurable form.**

- 100-200 ms, 10-20% of the main action's magnitude; skip below 150 ms interactions
  [source: `disney-principles.md` §2]. Four-act share 10-20% of a beat; hold compressed
  about 50 ms; "Skip for <150ms interactions" [source: `narrative-structure.md`, Act 1].
- Corporate: minimal or none; playful: exaggerated wind-up [source: `narrative-structure.md`, By Personality].
- Grader: a wind-up shows as a short opposite-sign displacement immediately before the
  main move; it is legitimate only when the main move follows within 200 ms and is at
  least 5x its magnitude [inference from the 10-20% figure].

**Code-level implication.**

- Two adjacent `fromTo`s on the same property, wind-up first (`power2.in`, short), then
  the move; or a single `back.in`-style departure, which produces the wind-up
  implicitly; the manifesto's press recipe uses "linear compression then spring
  recovery via two adjacent GSAP tweens on the same property" [source: `rules-index.md`,
  `press-release-spring`]. Later tweens re-owning a property carry `immediateRender: false`
  [source: `manifesto/SKILL.md` §5 lint traps].

---

## Rule 17. Ambient life on holds

**Why.** A held frame with no motion reads as a stall; a held frame with too much
reads as jitter. "Every decorative element should have ambient motion: breathe, drift,
pulse, orbit" [source: `video-composition.md`], but "alive with ONE ambient motion"
[source: `motion-principles.md`].

**Measurable form.**

- Amplitude 10-20% of primary, continuous and slow, never demanding attention [source:
  `core-philosophy.md`].
- Camera drift 2-8 px; focus breathing ≤ 0.6 px with a 2-3 s period; glow bloom peak
  opacity ≤ 0.45 [source: `multi-phase-camera.md`; `depth-of-field-blur.md`;
  `rules-index.md`, `ambient-glow-bloom`].
- Audio-reactive intensity on type or logo ≤ 5% scale and ≤ 30% glow; backgrounds may
  push to 10-30% [source: `techniques.md` §11].
- Ambient period 2-20 s [source: `timing-easing-tables.md`].
- Different ambient per scene; "or nothing" is a valid choice [source: `motion-principles.md`, Guardrails].
- Grader: duplicate consecutive frames = 0 (the FRAME check) and no direction reversal
  on the settled hero (the MOTION check) together define the window: something must
  change every frame, and the hero must not visibly oscillate [source: `grade-original.py`].

**Code-level implication.**

- `tl.to(el, { scale: 1.02, yoyo: true, repeat: N, duration: 1.2, ease: "sine.inOut" }, t)`
  on the timeline, with `repeat = Math.max(0, Math.floor(dur / cycle) - 1)` so the
  finite repeat never overshoots `data-duration` [source: `kinetic-beat-slam.md`, Finale repeat math].
- Ambient lives on a separate element or a separate transform channel from the
  entrance (parent/child split) [source: `motion-principles.md`, Load-Bearing rules].

---

## Appendix A. A working conversion sheet from After Effects habits to the contract

| AE habit | Under the contract |
| --- | --- |
| Easy Ease (F9), any influence | **There is no monotone mapping from influence to `powerN`; use the fitter.** Influence sets handle length, which controls how much of the duration the ease occupies; the GSAP exponent controls the curve's shape over the whole duration. You can reach 85% influence with a soft-shaped curve. If one line is needed: AE's Easy Ease is closest to the CSS `ease-in-out` shape, near `power1.inOut`, and `power2.inOut` is already noticeably snappier and not in the same range. The influence-to-`powerN` table this appendix used to print has been removed, because a table that will be copied is worse than no table when the document already ships a least-squares fitter that does the job correctly [inference] |
| "Both keys 75% puts the highest speed point in the middle" | true of **every** symmetric `inOut` curve; it is not a property of 75% [source: vdci, Jerron Smith, for the observation; the correction is arithmetic] |
| Speed graph dipping below zero | `back.out(n)` or baked spring ζ 0.6-0.7 [source: mtmograph; gsap adapter] |
| Value graph crossing the target then returning | same as above; measure the peak, not the handle |
| Hold keyframe | `tl.set` or a gap between tweens |
| Text Animator with Range Selector, Ramp Up, Ease Low 100 | per-unit `fromTo` with `duration = T·R/(1+R)` and `stagger = T/((1+R)(n-1))`, `power3.out` [source: `manifesto/SKILL.md`]. **A Range Selector with Ease High or Ease Low set is a NON-UNIFORM distribution of start times, and a uniform `each` cannot reproduce it.** The Ease High / Ease Low controls are what make an AE type reveal sweep rather than tick. Use GSAP's stagger `ease`: `stagger: { each: s, ease: "power2.inOut" }`, or a function-based stagger, and fit that distribution ease separately from the per-unit ease. The per-unit arithmetic above is correct (`D + S(n-1) = T`); the distribution is the part that was missing, so the one AE-to-GSAP translation this document gave in full was the wrong shape whenever the reference used the ease controls, which is most of the time [source: GSAP Staggers, https://gsap.com/resources/getting-started/Staggers/ , which the document already cites] |
| Sequence Layers by N frames | `stagger: { each: N * F }` [source: frame.io article for the AE side; GSAP docs] |
| Parented null driving a group | wrapper div; one tween on the wrapper [source: `manifesto/SKILL.md`, Controllers] |
| Camera layer | `.world` wrapper, one writer of its transform [source: `viewport-change.md`] |
| Motion blur switch | **Two separate things, and you use both.** (a) **Shutter angle as a style control**, decided at the top of a job: 180 degrees default, 90 for hard crisp action, 270-360 for smeared or dreamy; applied render-side per card with the corrected `tmix` recipe in Rule 13. (b) **Per-layer directional blur** as an authored effect, with the amount tied to that layer's own velocity rather than set by hand. In AE the motion-blur switch derives blur per layer, so fast layers smear and slow ones do not within a single frame; a whole-frame render shutter cannot do that, it blurs the static background's grain along with the moving card. Under the contract the per-layer form is an SVG `feGaussianBlur` with an axis-weighted `stdDeviation` written by an `onUpdate` from the same proxy as the transform: with `x(t) = D e(p)`, per-frame travel is `D e'(p) / (T fps)` and a 180-degree shutter is half of that; `e'(p)` for the power family is `(n+1)(1-p)^n`. CSS `filter: blur()` is isotropic and is not a substitute [source: `manifesto/SKILL.md` and `motion-blur-streak` for the two halves; the connection and the derivative are inference/computed] |
| Wiggle expression | index-seeded hash of quantized time, never `Math.random` [source: `rules-index.md`, `chromatic-glitch`; `techniques.md` §2] |
| Loop out expression | finite `repeat` computed from the clip length [source: `kinetic-beat-slam.md`] |

## Appendix B. Threshold summary for a grader

Each line names the rule, the metric, the threshold and where the number came from.

| Rule | Metric | Threshold | Basis |
| --- | --- | --- | --- |
| 1 | onset delta between unrelated targets in one 0.5 s window | ≥ 1 frame; typical 2-4 | inference from NYU 3 frames, manifesto ~3 frames, LottieFiles 50-150 ms |
| 1 | first tween in a scene | ≥ 0.1 s after scene start | HyperFrames motion-principles |
| 2 | cascade overlap | 0 < overlap < 1, gaps non-increasing | waterfall-entry |
| 3 | secondary amplitude, delay | 30-50%, 50-100 ms | LottieFiles disney-principles |
| 4 | fitted ease RMSE | report; prefer fitted bezier when named ease RMSE > 3 px at analysis scale | measured abe-ad |
| 5 | exit/entry continuity at a cut | same direction of travel, and neither side below 30% of its own peak speed on the cut frame | HyperFrames beat-direction states ~5%, but its own worked example (exit `y:-150` 0.33 s `power2.in` = 909 px/s; entry `y:150→0` 1.0 s `power2.out` = 300 px/s) misses that by 3:1, so 5% is aspirational prose, not a demonstrated tolerance [computed] |
| 6 | arc depth | 3-8% of chord corporate, 10-25% organic/playful | LottieFiles disney-principles (absolute px, UI scale) + inference |
| 7 | parallax speed ratios bg/mid/fg | about 0.2 / 0.5 / 1.0 | LottieFiles choreography; Lumitree |
| 7 | camera zoom duration, dwell | 1.0-2.0 s, ≥ 1.0 s | viewport-change |
| 8 | render cut frames vs plan | one-for-one | manifesto SKILL §7 |
| 9 | simultaneous active non-ambient elements | ≤ max(3, N/3) | LottieFiles core-philosophy, choreography |
| 9 | group stagger span | ≤ 0.5 s for UI-scale groups; 1.5-2.5 s for per-character kinetic type; step ≥ 1 frame always | LottieFiles, HyperFrames for the UI cap; type figures inference |
| 10 | settled window | [start + 0.35 s, start + 0.62·dur] | grade-original.py |
| 10 | text settled time | subtitle-scale: ≥ chars / 13 s. Display type: ≥ words / 2.75 s with a 0.8 s floor | legibility.info (subtitle); the display figure is inference reconciling the two rates in Rule 10 |
| 11 | beat-length CV | ≥ 0.18 | grade-original.py |
| 11 | slowest/fastest scene | ≥ 3 | HyperFrames motion-principles |
| 12 | hero visible | ≤ 0.5 s into its beat | spring-pop-entrance |
| 13 | leading-edge travel per frame on hard edges | flag above ~0.5% of frame width per frame (halve at 24 fps, double at 60) | manifesto SKILL measured anchor + inference |
| 13 | unbroken travel | ≤ 1/3 frame **for sustained hero moves only**; transitions exempt by class | LottieFiles choreography (UI) + inference |
| 14 | 90th-percentile tween duration in a film | should exceed 0.5 s | inference |
| 15 | settle direction reversals | premium/product 0; editorial/brand ≤ 1 reversal of 1-5% of **travel**; celebration 15-25%. State the denominator: overshoot % = (peak − target) / (target − start) | grade-original.py for the zero-reversal law; the register split and the denominator definition are inference |
| 17 | duplicate consecutive frames | 0 **inside a segment that is supposed to be moving**; declared freezes and declared on-twos cadence exempt | grade-original.py + inference |
| 18 (new) | full-frame luminance reversals | ≤ 3 per second | WCAG 2.3.1 / ITU-R BT.1702 |
| 19 (new) | settled translate values on text and hairlines | whole pixels | inference |
| 20 (new) | explicit `transformOrigin` on every element that scales or rotates | present, and not the default 50% 50% unless intended | inference |
| 21 (new) | loop seam | position, scale, rotation **and velocity** continuous across the wrap | inference |
| 22 (new) | delivery | action safe 93%, title safe 90% (broadcast only); min type ≈ 4% of frame height; no 1 px strokes | SMPTE ST 2046-1 + inference |

## Appendix C1. Rules this document was missing, added in revision 2

Each of these is a rule a professional applies and that nothing in Rules 1-17 covered.
Where a figure is given it is inference unless a source is named.

**C1.1 Transform origin.** Every element that scales or rotates needs an explicit
`transformOrigin`, chosen from the design intent: a card that grows from its top edge,
type that scales from its baseline and optical left rather than its bounding-box centre, a
panel that pivots from the corner it is hinged on. Never leave it at the default
`50% 50%` for anything that should pivot. This is the commonest single failure in junior
AE work and it transfers directly to CSS transforms, where the default centre origin is
even easier to inherit by accident; it changes the read of a move completely at identical
timing and easing, so no amount of curve fitting recovers it. Type is the sharpest case: a
bounding-box centre includes ascender and descender space that the eye does not, so
centre-origin scaling on a headline visibly drifts.

**C1.2 Masks, mattes and wipe reveals.** Masked reveals are the core mechanism of kinetic
typography and of most professional lower thirds and lockup builds, and this document
mentioned masks once, as something a cascade must not be confused with. Cover: `clip-path`
and `mask-position` reveals; the moving-cover-shape reveal; **the difference between a mask
that travels with the type and one that stays fixed while the type moves through it** (the
second is the standard kinetic-type reveal and reads completely differently); matte edge
softness; and the fact that a mask reveal is paint-only under the contract and so is legal
where `width`/`height` animation is not, which makes it the sanctioned way to do the things
that ban forbids.

**C1.3 Delivery.** Action safe 93% and title safe 90% of the frame **for broadcast
deliverables**; for web and social use 4-5% margins plus the platform's own asymmetric UI
bands. Minimum type roughly 4% of frame height for anything that must be read on a phone,
about 43 px at 1080. Avoid 1 px strokes and hairline weights, which disappear or crawl
after compression. If the piece will be delivered 16:9, 1:1 and 9:16, keep the load-bearing
content inside a centre column that survives all three. (SMPTE ST 2046-1 for the broadcast
figures; the rest is inference. This document already carries the closely related
observation that web-scale decoration is invisible on video, so the ground was prepared.)

**C1.4 Photosensitivity. This is the one genuinely unsafe gap the document had.** No more
than three flashes or luminance reversals per second over a significant portion of the
frame, and no high-contrast regular striped patterns that scroll. ITU-R BT.1702 and the
equivalent broadcast guidance set this as a safety requirement, not a preference, and it is
enforceable. It is not hypothetical here: Rule 11's percussive register runs beat spacing of
1.2-1.8 s but its cited kinetic-beat work and the ABE measurement include a cluster of three
cuts inside 18 frames, which is 5 cuts per second, and a full-frame luminance change on each
of those is a violation. Related: `prefers-reduced-motion` does not apply to a rendered
video, but a reduced-motion alternate cut is a real deliverable on accessibility-sensitive
accounts, and the flash limit binds the render itself.

**C1.5 Frame rate is a decision with consequences.** It scales every per-frame threshold in
this document (strobe cap, minimum stagger step, offset floor, blank-gap lengths) and it
carries a look: 24 halves the strobe tolerance and reads as film, 30 is the broadcast and
social default, 60 reads as demo or interface capture and flattens the sense of weight. The
same tween at the same seconds reads noticeably lighter at 60 than at 24, which is why most
brand film is still finished at 24 or 25. State the delivery rate before authoring, because
every cut and gap here is a frame count.

**C1.6 Eye-trace across a cut.** Note where the viewer's attention sits on the outgoing
frame and put the incoming subject near it, within roughly 15-20% of frame diagonal, or
displace it deliberately and give the viewer 6-8 frames to find it before it does anything
meaningful. Eye-trace is the primary tool an editor uses to make a cut invisible and it
operates before and independently of graphic matching or velocity matching: two shots can
match on graphics and velocity and still cut badly because the eye has to travel across the
frame during the change. It matters more in motion graphics than in live action, not less,
because the frames are sparser and there is less to anchor the eye.

**C1.7 Seamless loops.** A loop needs **position, scale, rotation and velocity** continuity
at the wrap, not just matching first and last values; a value match with a velocity mismatch
produces a visible hitch every cycle. In practice: use a full-period sine or a rotation of
exactly 360 degrees rather than an eased tween returning to its start, and place the wrap
point where velocity is highest, not where the element is at rest. Directly relevant here:
Rule 17 recommends `yoyo` repeats for ambient life, and `yoyo` is exactly the case where
value continuity holds but velocity reverses, which is why long yoyo drifts often read as a
pendulum rather than a drift.

**C1.8 The blocking pass, and grading it differently.** Time the piece first with linear
tweens and holds, judge the timing alone, then apply curves. This is how the work is done
and it is how you catch a pacing problem before spending effort on curves that get thrown
away. It matters more here than in AE because the grader as specified rejects a blocking
pass as a linear-ease violation, which means an agent cannot do the step a professional
does first.

**C1.9 A hit needs runway (the picture-side consequence of sound design).** Leave 4-6 frames
clear before an impact for a whoosh or riser to occupy, land the impact on the hit frame,
and let the visual tail carry 8-12 frames after it. A cut placed with no runway cannot be
scored convincingly no matter how well it is timed. This is a picture-editing constraint,
not a mixing note, which is why it belongs here even though a separate sound document
exists; it also explains the anticipation observed in the reference (cuts landing a frame or
two ahead of the beat) better than a statistical claim with no null model.

**C1.10 Sub-pixel settle.** Text and hairline elements must settle to whole-pixel translate
values. A headline resting at x = 40.37 px sits on a different antialiasing phase than one
at 40, and any residual ambient motion under a pixel makes the letter edges crawl. It is one
of the few defects that looks worse in the render than in the browser preview, so it
survives review and ships. Rule 17's ambient-life requirement and Rule 10's
no-duplicate-frames rule both push builds directly into this failure.

**C1.11 Spatial interpolation is not temporal easing.** In After Effects the motion-path
shape (spatial interpolation, including roving keyframes) is a separate control from the
speed curve, and roving is what produces a constant-speed traverse along a curved path.
Under this contract the equivalent is a **single MotionPath tween carrying one ease along
the whole path**, never a chain of per-point tweens, which is what reintroduces the stutter
that roving exists to remove. This document's own headline source (Marriott's Motion
Foundation sequencing) separates the two.

**C1.12 Luminance is a motion channel.** A brightness or exposure change reads faster than a
positional one, so a 2-frame luminance pop is a legible accent where a 2-frame move is
invisible. Flash frames, exposure bumps on a hit and a hold-then-dim on a resolve are
standard accents and are paint-only, so they are already legal under the contract. This
gives Rule 11's percussive register a tool it otherwise has none for. It must be read
together with C1.4, since the same mechanism is what makes it a safety issue.

**C1.13 Compression.** Full-frame fast motion, fine grain, and heavy blur ramps are the
three things that blow a bitrate budget and macroblock. A sharp whip pan across a detailed
frame is close to the worst case for inter-frame prediction and visibly blocks up at
platform bitrates. Keep whole-frame motion short, and make it either high-contrast and
simple or deliberately blurred, which costs fewer bits than a sharp fast pan. This
interacts conveniently with Rule 13: the shutter that fixes the strobe also lowers the
bitrate cost, so state the two together.

## Appendix C. Open questions

- The offset figure is a synthesis; no single professional source publishes either the
  "2-4 frame" form or the 15-30%-of-duration form as a rule. The nearest published numbers are 3 frames (NYU FRL,
  character limbs), "~3 frames" per sibling group (manifesto, from an AE liquid-glass
  tutorial), and 50-150 ms (LottieFiles). It should be fitted per reference, and
  `segment.mjs` per-word reveal frames are the instrument.
- Ben Marriott's and School of Motion's published web pages describe the graph editor
  qualitatively; the influence-percentage tiers here come from third-party AE guides
  (designkkashi, kelp, vdci). If a Marriott video transcript with specific influence
  numbers is needed, it must be sourced from the video itself.
- **The "12 of 23 cuts landed within 0-2 frames of an audio onset" finding has no null
  model, and recomputation against the reference's own 149.9 BPM grid gives 11 of 23, not
  12.** With a 5-frame window on a dense music bed that hit rate is close to what chance
  produces, so the authoring instruction Rule 11 builds on it should be treated as a
  qualitative observation (the cuts sit near the grid and tend to anticipate it), not as
  evidence of deliberate frame-accurate anticipation.
- The hold/motion ratio for a beat is inferred by reading across three phase models
  and one measured skeleton. A direct measurement across several references (motion
  frames / total frames per card via `card-motion.mjs`) would replace the inference.
- Material 3 token values were confirmed from two mirrors of the spec because the
  canonical page renders client-side; the values match the mirrors exactly but the
  canonical page should be checked once from a browser.
- Apple's current HIG Motion page could not be fetched as text; the bullets quoted are
  from the older iOS HIG animation section, which carries the same principles but not
  the current wording.
- Whether GSAP's `stagger.from: "random"` is seeded is undocumented; under this contract
  it is irrelevant because `Math.random` is banned, but a builder porting an existing
  composition should know the order will change between renders if it was used.
