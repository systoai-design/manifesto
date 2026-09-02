# The motion canon

The consolidated reference for authoring motion graphics under the HyperFrames contract.
Read this first. Every rule states its measurable form; where a rule needs depth, it links
to one of the six research documents in this directory.

**The contract, once.** One paused GSAP timeline registered on `window.__timelines`, keyed
by the composition id. Every tween is a `fromTo` with an explicit from-state, and
`immediateRender: false` on any tween that re-owns a property already written on the same
element. Transforms and paint-only properties (`x`, `y`, `scale`, `rotation`, `opacity`,
`filter`, `clip-path`, `color`, `mask`), never `width` / `height` / `top` / `left` /
`fontSize` / `letterSpacing`. No `Math.random`, no `Date.now`. Finite repeats. State is a
pure function of timeline time, so seeking is exact.

`CustomEase` and `CustomWiggle` are legal: both are pure functions of progress and both have
been free since GSAP 3.13. Two-bone IK is legal: it is the law of cosines, not a simulation.
A baked table sampled by time is legal. A stateful integrator is not.

**How to read a number here.** `[source]` means a named document states it. `[measured]`
means it was measured on a real reference in this repo. `[inference]` means it is reasoning
from cited material, and an inference is a starting value to fit against reference footage,
never a canonical figure. **A threshold marked `[tuning]` is a knob a grader exposes, not a
law.** About a third of the numbers below are inference; they are labelled, and the labels
are the point.

**Frame grid.** Author at the delivery frame rate. `const F = 1/FPS; const f = n => n * F;`
Every start time and every duration goes through `f()`. A duration typed in raw seconds ends
between frames, so the settled pose is never rendered and an editor cannot cut on it. Frame
rate is a decision with consequences: it scales every per-frame threshold below, and 24
reads as film, 30 is the broadcast and social default, 60 flattens the sense of weight.

---

## 1. Physics of motion (the twelve principles, for graphics)

Depth: [`twelve-principles.md`](twelve-principles.md).

### 1.1 Squash and stretch

Travel on a parent, deformation on a child, so the two transform sets never fight.

- **The contact frame IS the squash frame.** Start the squash one frame before the parent
  reaches rest so the peak lands on the stop. *Measurable:* the peak of the `sx/sy`
  excursion sits on the frame where the travel-axis step series goes to zero. A squash
  peaking two or more frames after the stop reads as a wobble, not an impact. `[inference]`
- **Impact 2-4 frames, recovery 4-8 frames, carried as FRAME COUNTS across frame rates.**
  Converting LottieFiles' 60 fps counts by milliseconds gives 1-2 frames at 30, and a
  one-frame deformation is a flicker. `[source: LottieFiles frame counts; carry-the-count is inference]`
- **Amplitude scales with velocity.** 6 % elongation is invisible on a body travelling
  29 px per frame; classical practice on a fast fall is 20-50 %. The UI figures
  (0.85 / 1.15) are micro-feedback on a phone. `[inference]`
- **The stretch axis follows the velocity vector**, not the world Y. `rotation = atan2(vy, vx) + 90`,
  then stretch along local Y. Stretching vertically while travelling diagonally reads as the
  object inflating. `[inference; this is what AE auto-orient-along-path exists for]`
- **On display type, `scaleX <= 1.06-1.10`.** Beyond that letterforms read as broken glyphs.
  Text is never non-uniformly scaled except as a measured per-glyph fit. `[inference]`
- **Premium means 1-3 % with zero oscillation, not zero deformation.** "Skip for premium
  brands" is about *visible cartoon deformation*; a premium film still carries weight cues in
  the scale settle, the shadow spread and the landing frame. Following it literally produces
  the "weightless" defect. `[inference, reconciling LottieFiles against its own defect list]`
- *Measurable:* volume conservation — `sx * sy` (or ink count) stays within about 5 % of
  settled through the excursion `[tuning]`. Compressed axis is the travel axis.

### 1.2 Anticipation

- **One curve, not two tweens.** Chaining `power2.inOut` into `power3.out` puts a velocity
  step at the junction: on a 420 px move the first frame of tween 2 carries about 24 % of the
  travel. Use a `CustomEase` whose y goes negative, over the whole travel. `[computed]`
- **Magnitude: 10-20 % of travel for moves under about 300 px, capped at 20-40 px at 1080p**
  (or 5-12 % of the element's own dimension), whichever is smaller. Anticipation scales with
  the object and the force, not with distance: 12 % of a 1200 px slide is a separate move in
  the opposite direction. `[LottieFiles for the fraction; the cap is inference]`
- **Below about 12-15 px of counter-travel, percentage rules stop working.** Either scale the
  prep up disproportionately or omit it. 15 % of a 34 px head turn is 1.3 px per frame,
  against "subtle reads as static at 30 fps". `[inference]`
- **Duration 100-200 ms (3-6 frames at 30 fps).** The 1:3 anticipation-to-action ratio is a
  **UI figure only**; in character work the anticipation is the slower part. `[inference]`
- **An off-frame element cannot wind up, but the scene can**: the container dims, the camera
  pulls back, or a held blank gap precedes the hit. `[inference]`
- *Measurable:* a run of 2-6 frames whose centroid step is opposite to the main travel,
  immediately before the main run; net opposite displacement / total travel in 0.08-0.20. A
  near-zero step at the wound-up extreme is a **cartoon** signal, not a required condition —
  a product-grade pull-back-then-push is one continuous curve. `[inference]`

### 1.3 Staging

- **One thing moves, or one thing moves most.** *Measurable:* one region carries most of the
  summed step magnitude at any moment `[tuning: "more than 2/3" is a starting value]`.
- **The 1/3 rules are UI rules.** "At most 1/3 of 3+ elements active" is about a user tracking
  state. Video routinely violates it and should: a six-item stagger has all six active, a
  lockup resolves as one unit, a grid lands together on the downbeat. Grade **unmotivated**
  simultaneity only: count one declared group or lockup as one element, and exempt same-frame
  starts on a declared audio hit. `[LottieFiles for the rule; scoping is inference]`
- **Dim and defocus the rest**: 40-60 % opacity, plus 3-6 px of blur per depth step with a cap
  of 8 soft / 16 default / 24 heavy at 1080p. Lean on the dim; dim plus modest blur reads more
  like real depth of field than blur cranked up. `[source: HF depth-of-field-blur]`
- **Order:** the element the hero lands *on* moves first; the hero is the first *content*
  mover. This reconciles LottieFiles ("hero enters after supports") with HyperFrames ("hero
  moves first"). `[inference]`
- **Every beat must contain at least one frame that works as a still.** That is what staging
  means to a client, and it is checkable against the settled window. `[inference]`

### 1.4 Straight-ahead and pose-to-pose

- **Pose-to-pose is every `fromTo`.** The from and to states are the key poses, the ease is the
  in-between rule.
- **Straight-ahead is one `ease: "none"` driver with an `onUpdate`** that computes state as a
  pure function of time, with an index-seeded hash for variation.
- **Seed frame 0** by calling the pose function once at setup. The driver has not rendered
  before the first seek, so an unseeded field shows its unstyled CSS position on frame 0.
- **Cap every driver to its beat and give it a rest state.** *Measurable:* the ambient step
  series reaches zero before the cut. `[inference]`
- Past about 30 elements, per-element `gsap.set` is the slow path: write transform strings, or
  move the field to canvas.

### 1.5 Follow-through and overlapping action

- **Child lag 50-150 ms behind parent; sibling GROUPS offset by about 3 frames, not per
  element.** `[source: LottieFiles; manifesto]`
- **Overshoot by register, one rule, three cases** — this replaces two contradictory rows that
  used to sit adjacent:

  | Register | Amplitude (fraction of TRAVEL) | Reversals |
  | --- | --- | --- |
  | premium, product | 0-2 % | <= 1 |
  | editorial, brand | 1-5 % | <= 1 |
  | playful | 15-25 % | <= 2, second under 5 % |
  | energetic | 15-30 % | <= 1 |
  | celebration only | 15-25 % | <= 1 |

  **Define the denominator explicitly: overshoot % = (peak − target) / (target − start).** For
  a scale tween 0.9 → 1.0, 10 % of travel is scale 1.01 (felt) and 10 % of target is 1.10
  (cartoon). Premium is 0-2 % rather than a flat 0 because LottieFiles' own cited Apple Spring
  (stiffness 300, damping 20) is ζ 0.577, whose first overshoot is about 11 %. `[computed]`
- **Overshoot goes on transforms only, never on opacity or colour.** Paint has no momentum.
- **A drop shadow shares its caster's Y exactly.** Only the *spread* lags — opacity, scale,
  softness, 2-3 frames behind. A shadow that lags in position visibly detaches. `[inference;
  the "shadow arrives 50 ms after card" source describes growth, not travel]`
- **Opacity gets its own envelope, always**, finishing in the first 40-60 % of the move so the
  element is opaque while it decelerates and the settle is visible. `[inference]`
- **Moving hold:** creep in one direction + breath + blink, at the low end of the ambient
  amplitudes. One ambient motion, not three; three columns at ±6 px compound to ±18 px of
  competing motion. `[source: HF sine-wave-loop]`

### 1.6 Slow in and slow out

- `.out` on arrivals, `.in` on departures, `.inOut` between positions.
- **Linear is correct for anything CONTINUOUS**: loops, tickers, conveyors, a pan already
  moving when you cut into it, the constant-velocity plateau inside a compound move. If a move
  is cut into or out of mid-flight, any easing at the boundary reads as a hitch. Linear is
  wrong only for an *isolated* move that starts and stops on screen. `[inference; the
  nudge-curve recipe's linear plateau is the proof]`
- **Below about 5 frames, ease is noise.** A 3-frame tween has two in-between positions;
  swapping the cubic moves them by a few percent. Short accents are keyed by **spacing**, not
  by curve type. `[inference]`
- **Delete ease-variety quotas.** "At least 3 easings per composition" and "no more than 2
  tweens sharing an ease" contradict "same ease family across a stagger" and "reuse the ease
  family". A house style *is* a consistent curve; variety belongs in duration and distance.
  Expect two to four distinct curves per piece as a consequence of having distinct registers;
  more than about five is unresolved, not varied. `[inference]`
- *Measurable, per family (computed):* fraction of travel at 25 % of duration — `sine.out`
  38 %, `power1.out` 44 %, `power2.out` 58 %, `power3.out` 68 %, `power4.out` 76 %,
  `expo.out` 82 %. Peak/mean step — 1.57, 2.0, 3.0, 4.0, 5.0, 6.9. Linear ends on a 6.7 px
  final step where every eased family ends below 0.5 px: that is the abrupt stop.
- **Velocity match at a cut is direction continuity, not a percentage.** The widely quoted
  "~5 %" is not met by its own source's worked example (909 px/s against 300 px/s, 3:1 out).
  *Measurable:* same sign of travel on both sides, and neither side below about 30 % of its own
  peak speed on the cut frame. `[computed]`
- **The two correct handoff forms.** (a) *Push*: both scenes share one ease and one duration
  and move as one surface — the match is true by construction. (b) *Cut with matched
  velocity*: the exit ENDS at the cut and the entry STARTS at it, with durations solved so
  `(n+1)·D_exit / T_exit = (m+1)·D_entry / T_entry`. For equal distances and the same exponent
  that means **equal durations**.

### 1.7 Arcs

- **Arcs are for organic elements.** Type, cards, panels and UI travel **straight** in
  professional motion graphics; the principle's own source concedes it. An 80 %-arc-rate
  target is how you get the swoop. Report an arc on a text or card element as *unmotivated*,
  not as a credit. `[inference, inverting the earlier default]`
- **Arc depth is a fraction of the chord, not a pixel count**: 3-8 % for corporate, 10-25 % for
  organic or playful. 15 px of sagitta is a deliberate arc on a 200 px move and invisible on a
  1600 px move. This is also how the AE control behaves. `[inference]`
- **Two tweens on one element are safe only when they name disjoint properties.** Two tweens
  that both write `y` are a bug however they are flagged; `immediateRender: false` does not
  make it safe.
- *Measurable:* max perpendicular deviation from the chord / chord length, roughly 3-15 %
  `[tuning]`, with one-sided curvature. Note the corporate end is not measurable at low decode
  resolutions: 0.4 % is 1.4 px at 640×360, inside antialiasing noise.

### 1.8 Secondary action

- Amplitude 30-50 % of primary; 1-3 frames later; a different ease family; may move in a
  different direction or on a different property. `[source: LottieFiles]`
- **Distinguish it from follow-through:** follow-through is the same direction, caused by the
  primary, decaying. Secondary action is not caused by the primary.
- **Grade only declared pairs.** Most hero moves in graphic motion (a headline slide, a
  counter, a card push) have no natural child, and requiring a reaction on every one produces
  bolted-on glows and shadows — the agent-made look. **Rigid parenting is correct for
  lockups**: a wordmark and its symbol move as one because they are one object. `[inference]`
- **The environment reacts on the SCENE WRAPPER, not the background layer.** Scaling `#bg`
  alone reads as the wallpaper twitching.
- **Camera shake**, the commonest secondary reaction and previously absent: a hash-seeded sum
  of decaying sines on the scene wrapper, or `CustomWiggle` (never `type: "random"`). At 1080p,
  6-14 px decaying over 8-12 frames, rotation under 0.5 degrees, decaying to exactly zero
  before the next beat's first motion. `[inference for amplitudes]`

### 1.9 Timing

- **Budget peak velocity, then let distance set duration.** The distance-to-duration
  multiplier table (50 px 0.8×, 100 px 1.0×, full screen 1.8-2.0×) is a **UI table**: it exists
  because an interface has a 400 ms ceiling, and it makes a 20× distance take 2× the time,
  which is 10× the speed. Applied to film at the house 0.6 s default, a full-screen 1920 px
  move takes 53 px per frame — five times the strobe budget. Keep the table for depicted UI
  only. `[computed]`
- **Strobe threshold as a fraction of frame width: about 0.5 % per frame** for hard
  high-contrast edges, up to 1 % with a shutter. 10 px at 1920, 5 px at 960, 20 px at 3840.
  Halve at 24 fps, roughly double at 60. Contrast, edge hardness and whether the element is
  still fading in all move it; so does whether the eye is *tracking* the object, which is why
  fast pans judder while a tracked hero does not. `[inference from one measured case at 31 px]`
- **Exit ≈ 0.65-0.70 × entrance, `.in` ease — for cards that exit by animating in place
  only.** The dominant exit in this medium is a hard cut (ratio 0), and a transitional
  handoff is legitimately *longer* than its entrance. `[arithmetic on five cited ranges]`
- **Hold a settled pose at least 6-8 frames before any cut**, or the settle is never seen.
  `[inference]`
- Blank gaps 1-8 frames between cards. Beat-length CV >= 0.18, slowest scene >= 3× the fastest.
  Dwell >= 1 s after a climax. Clip boundaries biased inward: `start − 0.0002`,
  `duration − 0.0011`. `[measured]`
- **One physics per film**: one gravity (the same `.in` exponent and fall time per pixel for
  every drop) and one light direction. Inconsistent fall acceleration between two drops is the
  commonest solid-drawing failure in generated pieces. `[inference]`

### 1.10 Exaggeration, solid drawing, appeal

- **Exaggeration is a register knob applied once**, not a per-element garnish. Playful 15-25 %,
  energetic 20-30 %, corporate 0-5 %, premium 0 %. Clamp derived values into the stated bands.
- **One projection.** `perspective` on the parent OR `transformPerspective` on the element,
  never both — two projections mean the card's foreshortening matches nothing else in frame.
- **A `filter` on a child flattens its 3D context.** Keep a blurred shadow outside the
  `preserve-3d` group and drive it from the same pose object.
- **Promote layers deliberately and never promote type you are about to scale.** Text on a
  promoted layer is rasterised once at the promotion scale and stretched, so a scale tween
  softens the glyphs and they re-sharpen on de-promotion — a weight pop on the settle frame,
  which is the frame the grader samples. This is the browser's version of forgetting
  Continuously Rasterize. Set `gsap.config({ force3D: true })` and keep `will-change` static
  so promotion state never changes mid-piece.
- **Scale type DOWN into place** (1.06-1.12 → 1 premium, 0.85-0.92 → 1 for a pop). `scale: 0 → 1`
  on type reads as inflation and rasterises glyphs at tiny sizes. `[inference]`
- **Settle to whole pixels.** A headline resting at x = 40.37 sits on a different antialiasing
  phase than one at 40, and sub-pixel ambient motion makes letter edges crawl. It looks worse
  in the render than in the preview, so it survives review and ships. `[inference]`
- **Scale reads non-linearly**: a linear ramp from 0.2 to 1.0 appears to accelerate. Ramp scale
  on a curve, never from exactly 0. And a camera push scales stroke weights: a 1.5× push turns
  a 2 px rule into 3 px. `[inference]`
- *Measurable:* settled aspect drift <= 1 % `[tuning]`; no `0,0,1,0,0,1` px step patterns (that
  is a layout-property tween snapping, not an ease); one implied light direction across the
  film; duration palette of 3-4 modes, not a smear.

### 1.11 Four things the twelve principles do not name

- **The masked reveal**, the default gesture of professional kinetic type, lower thirds and
  lockups: `overflow: hidden` wrapper with the inner travelling `yPercent 112 → 0` (over-travel
  8-12 % so the type is still moving when it clears), or a `clip-path: inset()` tween. Its point
  is that the element has **no visible leading edge**, which is what separates a reveal from a
  slide. Mask padding is a **per-face metric** — measure descender depth and overshoot, do not
  use a constant. And distinguish a mask that travels with the type from one that stays fixed
  while the type moves through it; the second is the standard reveal. `[inference]`
- **Per-layer motion blur**, derived from each layer's own velocity. With `x(t) = D·e(p)`,
  per-frame travel is `D·e'(p) / (T·fps)` and a 180-degree shutter is half of that;
  `e'(p) = (n+1)(1−p)^n` for the power family. Write it into an SVG `feGaussianBlur` with an
  **axis-weighted** `stdDeviation` from the same `onUpdate` as the transform. **CSS
  `filter: blur()` is isotropic and is not a substitute.** A whole-frame render shutter blurs
  the static background too, so you use both. `[computed]`
- **Shutter angle, corrected.** `tmix=frames=4` on a 240 fps stream integrates 16.67 ms, the
  entire 60 fps frame interval — a **360-degree** shutter, twice any camera, and it reads soft
  and drunk. **Use `tmix=frames=2` then `framestep=4`** for the 180-degree film look. Never
  straddle a cut with a shutter window. `[computed]`
- **Luminance is a motion channel.** A 2-frame luminance pop is legible where a 2-frame move is
  invisible, and it is paint-only so it is already legal. It comes with a hard safety limit:
  **no more than three full-frame flashes or luminance reversals per second** (WCAG 2.3.1,
  ITU-R BT.1702). This is not hypothetical: three cuts inside 18 frames is about 5 per second.

---

## 2. Choreography

Depth: [`motion-rules.md`](motion-rules.md).

### 2.1 Offset and delay

- **Offset related-but-separate elements by 15-30 % of the offset element's own duration**,
  with 2-4 frames as a floor for short snaps. A fixed frame count is inconsistent across
  durations: 3 frames against a 6-frame snap is a cascade, against a 40-frame settle it is
  simultaneous. `[inference]`
- **Elements that are one physical thing share a start** (a cursor and the button it presses,
  a card and its shadow). One `fromTo` with an array of targets.
- **First motion 0.1-0.3 s after the composition's first frame** — the *first beat only*, not
  every beat. Later beats' lead is set by the transition: 0 for hard cuts and velocity-matched
  handoffs, one transition duration for dissolves. Requiring 100-300 ms of dead air after
  every cut produces a piece that stalls at every edit point. `[inference]`
- *Measurable:* for tweens on distinct targets starting inside one 0.5 s window, the start
  delta is either 0 (deliberately grouped) or >= 1 frame.

### 2.2 Stagger

- **Cap by register.** UI-scale groups (cards, chips, rows): total stagger under 500 ms.
  **Per-character or per-word kinetic type: 1.5-2.5 s for a full line.** A 40-character
  headline at 2 frames per character is an 80-frame sweep, 2.67 s, and is completely standard.
  `[LottieFiles/HF for the UI cap; the type figure is inference]`
- **Switch to a wipe when the step drops below one frame, not at a fixed item count.**
  `min(0.06, 0.5/n)` gives 0.031 s at 16 items = 0.94 frames at 30 fps, at which point
  consecutive items land on the same rendered frame and the stagger stops existing. The
  commonly quoted 9-item cutoff is neither that nor anything else. `[computed]`
- **One easing family across a stagger; vary start time only.** Optional overshoot on the last
  element as punctuation.
- **A Range Selector with Ease High/Low set is a NON-UNIFORM distribution of start times.**
  A uniform `each` cannot reproduce it; use `stagger: { each, ease }` or a function-based
  stagger, and fit that distribution ease separately from the per-unit ease. This is the
  control that makes an AE type reveal *sweep* rather than tick. `[source: GSAP Staggers]`
- **Cascade math:** for total time `T` and overlap ratio `R` (per-unit duration : stagger
  sweep = R : 1), per-unit duration = `T·R/(1+R)` and stagger = `T/((1+R)(n−1))`, so the last
  unit settles at exactly `at + T`. At the measured `R ≈ 0.7`, per-unit duration is **0.41 of
  the total, not 0.7** — the 0.7 is the ratio, not the share. The stagger budget is **not**
  satisfied automatically: check it. `[measured; the share correction is arithmetic]`

### 2.3 Hierarchy

- **Whatever moves first is the subject.** If a supporting layer moves first it must be
  low-amplitude, low-contrast preparation.
- **Rank hierarchy by change in VISUAL WEIGHT (roughly area × contrast change), not by peak
  displacement.** A logo that fades up on zero displacement is the hero of its beat; a large
  headline settling 12 px outweighs a small chip travelling 200 px — which is exactly the
  effect the sources describe when they say a small word animating aggressively can dominate
  a frame. A displacement-ranked test fails a correctly hierarchical build. `[inference]`
- Amplitude tiers: primary 100, secondary 30-50, ambient 10-20 %.
- Two focal points and three layers minimum per scene, so there is something to be a
  hierarchy of.

### 2.4 Rhythm and holds

- **Bimodal pacing.** Beat-length CV >= 0.18, slowest/fastest >= 3. Averaging the contrast away
  produces a film that feels nothing like the reference. **But when a piece is cut to a music
  grid, CV is the wrong statistic**: cards cluster at 1, 2 and 4 bar multiples and CV falls
  legitimately. If a tempo is detected and >= 60 % of cuts land within 2 frames of a bar line,
  grade the **range of bar multiples used** instead. `[measured; the alternative is inference]`
- **Gaps are placed, not distributed.** The measured reference spends 67 blank frames across
  10 runs, of which the 37-frame cold open is one, leaving about 30 frames across 9 interior
  gaps in a 22-cut edit: roughly 60 % of its cuts are hard cuts with **no gap at all**. A
  default gap after every card is a metronome one level up. `[measured]`
- **Reading rates: use the right one.** 13 cps (~137 wpm) is a **subtitle** standard for small
  type read while watching something else. Display type is read as a shape: budget about
  2.5-3 words per second with a floor of roughly 0.8 s of settled time for any text element,
  and add time for a second line rather than for characters. The two rates differ by ~6× for
  the same text and cannot both drive a grader. `[legibility.info for the subtitle rate; the
  display figure is inference]`
- **Exempt deliberate freezes from the no-duplicate-frames rule.** Most brand end cards are
  static for 1.5-3 s; animation on twos and posterised time duplicate every second frame on
  purpose. A blanket rule bans the commonest closing shot in the medium and invites the
  failure it is trying to catch, because an agent will add a breathe to a lock-up that should
  be locked off. Judge runs against a **declared cadence**. `[inference]`

---

## 3. Type

Depth: [`kinetic-type.md`](kinetic-type.md).

### 3.1 Hold time

- Card life: entrance → **settle** → hold → exit → gap. **Only the hold counts as reading
  time**, and the hold is measured from the settle, not from the card start. This is the single
  most useful idea in the type document and most designers do it by feel without stating it.
- `hold_read(words) = 0.33·words + 0.40 s`, minimum 0.83 s — **a FLOOR to check against, not a
  design target.** These are caption accessibility minima and as targets they run about twice
  too slow for professional work: a 3-word read card computes to 1.39 s of hold, which with a
  0.45 s entrance and 0.27 s exit is a 2.11 s card, longer than 21 of the 22 interior segments
  of the measured reference (median 1.067 s, max 2.4 s). **Fix the beat grid first, then cut
  the copy to fit the beat.** Copy is the free variable; timing is fixed. A centred 3-word hero
  card at 150 px is one or two fixations, roughly 0.6-0.9 s. `[measured; the target is inference]`
- **Beat regime splits in two.** 0.17 s (350 wpm RSVP) is the floor for a strict
  **replace-in-place** stream, where the eye never moves. A stream where each word **joins**
  the last is spatial accumulation and costs a saccade plus a fixation per word: 0.30-0.35 s.
  `[PLOS ONE 2016 for the 200 ms fixation; the split is inference]`
- **Flash regime, 2-8 frames**, only for words already established earlier in the piece.
- **Derive the regime, do not declare it.** A card is a *read* card if it introduces a word not
  shown earlier in the piece; everything else is beat or flash. As an author-declared enum the
  check is an attestation, not a measurement, and a builder whose card fails simply relabels it.

### 3.2 Mechanics

- **2-4 concurrent signals on a hero card, driven from one proxy.** One signal per card is the
  flat-but-competent tell. The measured reference stacks: mass on 19 of 23 segments, width on
  19, height on 17, centroid-x on 14, and almost nothing enters by opacity alone. `[measured]`
- **One dominant mechanic per piece for short form**, at most two accent mechanics reserved for
  structural cards, and ease variation within one family. "At least three mechanisms and three
  eases" is a floor for a two-minute explainer and backwards for a 15-30 second piece, which
  reads as authored with one mechanic varied in amplitude and reads as a demo reel with five.
  The reference is one compound mechanic across 23 cards. `[measured; restatement is inference]`
- **The full-frame ground inversion is a device and belongs in the vocabulary.** The reference
  carries its punctuation in the ground: 19 segments on black, 4 on white. It costs one
  paint-only property, is perfectly seek-safe, and gives structural read that no amount of
  entrance variety will. Roughly one card in five; hold the type mechanic constant across the
  flip. `[measured]`
- **Never crossfade two states of the same type.** Binary arrivals for whips, typewriters and
  visemes; a fade laid over a snap is the commonest tell in HTML type animation.
- **Never tween `letter-spacing`.** Per-letter `x` transforms converging from an index-derived
  spread symmetric about the centre, so the word's centroid does not move.
- **Never request a weight the face does not ship.** Archivo Black is one style at CSS weight
  400; requesting 900 triggers synthetic emboldening, which smears the outline at display size
  and is itself a classic tell. If weight is the mechanic, use a family with a real axis.
- **Reserve the box at the widest state** with a hidden ghost twin and centre the live copy in
  it, for any variable-weight or reflowing move.
- **Blur in `em`, not px**: 0.04-0.08 em reads as defocus, above 0.15 em as a rendering fault.
  A fixed 10 px is a whisper at 340 px type and erases a 30 px eyebrow. And **any non-`none`
  `filter` value, `blur(0px)` included, switches Chromium text off subpixel antialiasing**, so
  apply `filter: blur(0px)` to every type element in the piece or to none.
- **Gate every build-time measurement on `await document.fonts.ready`**, and set
  `font-display: block` on every face. A timeline built before the woff2 decodes measures
  fallback metrics and bakes them in — silently, intermittently, on some renders only.
- **Do not scale type through a big zoom.** A promoted layer rasterises once and stretches;
  340 px of type at 36× is about 12,000 px, near Chromium's texture limits. Scale the ground
  and the mask instead, or swap the glyph for an SVG path.
- **Knockout: prefer `mask` over `mix-blend-mode: multiply`.** White text's antialiased edge
  pixels are mid-grey, and mid-grey multiplied against bright footage darkens it, so every
  glyph carries a 1-2 px dark halo. And `autoAlpha` on a multiply layer does not fade type in;
  it turns white to grey.

### 3.3 Craft the rules do not cover

- **Set every line break by hand, per card.** The break determines the stagger structure, so an
  accidental break is an accidental rhythm. Break on syntactic units; never between an article
  and its noun, never after a preposition, never orphan a one-word last line unless that orphan
  is the payoff.
- **Choose the face before the motion**, on: even fitting (so per-glyph splitting does not open
  gaps), large closed counters if a zoom-through is planned, a real variable axis if weight is
  the mechanic, generous round-glyph overshoot so masked reveals are not flat-topped, and an
  embedding licence covering rendered video. Record cap height and descender depth in the
  storyboard: the mask geometry depends on both.
- **Ambient drift on read type is a velocity question, not a ban.** Under about 0.3 % of frame
  width per frame (≈6 px at 1920) a push reads as camera and keeps a long hold alive — that
  slow push is the Apple idiom. Above it, it is type in motion and cannot be read. The measured
  reference moves horizontal centroid on 14 of 23 segments. `[measured; threshold inference]`
- **Spec the silent cut.** Most feed viewing is muted, and a card comfortable at 0.8 s with
  narration needs closer to 1.4 s without. Spec both, or make the silent cut the master.
- **Add at least one continuity move.** A piece assembled entirely from independent
  enter-hold-exit cards is a slideshow with better easing. The outgoing element's rest
  transform becomes the incoming element's from-state, so the cut lands mid-move rather than
  into a gap — and a card that hands off does not need to resolve, which relieves the hold model.
- **Safe area: 4-5 % for web and streaming**, which the grader's existing 4 % edge check already
  enforces. Ninety-percent title-safe exists because CRT overscan cropped the frame; there is no
  overscan in any delivery path here, and applying it discards 10 % of the frame and fights the
  rule to anchor to edges. Use asymmetric platform UI bands for vertical (Reels ≈220 px top /
  420-500 px bottom; TikTok ≈180 / 320). Reserve 10 % for a named broadcast deliverable.
- **Hierarchy: grade the type SCALE, not the size count.** Single-size single-weight systems
  (Swiss, a Saul Bass title, one word per card) are canonical professional work. What is
  gradeable: every settled size within 10 % of a step in a declared ratio series, and
  `minSize >= 18 px` at 1080p (32 px body / 90 px headline in-feed).

---

## 4. Character

Depth: [`character-motion.md`](character-motion.md).

### 4.1 Rig

- **Nested translate group per joint; geometry drawn from (0,0) downward; rotation written as
  an explicit `rotate()` attribute.** No `transform-box`, no bounding boxes — a `<g>`'s bbox
  includes its children and changes as the forearm swings.
- **Two joints in the foot, not one.** Heel-strike rotates about the **heel**, toe-off about
  the **ball**. One ankle pivot swings a rigid plank and cannot produce foot roll, which is
  what makes a walk read as weighted and where its propulsion comes from. `[inference]`
- **One element, one writer.** Either one driver whose pose function owns the element for its
  whole life, or every driver's from-state is a no-op relative to the seeded rest pose. A
  driver tween renders its from-state whenever the playhead is before its start.
- `tl.seek(t, false)` when probing: the default suppresses `onUpdate` and every pose-driver
  shows its frame-0 pose.
- **Drop `will-change` from rig parts** (nothing to optimise in a seek-and-screenshot renderer,
  and layer promotion changes edge antialiasing on rotated shapes) and **replace
  `filter: brightness()` on far-side limbs with explicit darker tints** (a filter establishes a
  containing block and forces a separate compositing pass, shifting the far side sub-pixel).

### 4.2 Walk

- **Author the ANKLE trajectory in world space and derive thigh and shin with closed-form
  two-bone IK.** Authoring joint angles as four independent curves produces a foot that neither
  stays on the ground nor stays still: measured on the FK rig here, the planted foot's world
  height swings 29.5 px on a ~300 px character (19 px through the ground plane at DOWN, 13 px
  above it near the back contact) and slides ±7 px per frame within one step. A constant root
  translation cannot fix either; it is the wrong shape of correction. Two-bone IK is stateless
  and closed-form, so it satisfies the contract exactly as well as a pose table does. `[measured]`
- **Interpolate cyclic key tables with a wrapped Catmull-Rom, not smoothstep.** `ss'(u) = 6u(1−u)`
  is zero at both ends of every segment, so smoothstep stops every joint dead at **every key** —
  at 15 frames per step that is a velocity zero every 3.75 frames, an 8 Hz pulse, and it is the
  "jerky motion, abrupt stops" on the appeal-killer list. Slow-in/out belongs at the extremes;
  limbs move fastest through passing. `[computed]`
- **Quantise the CYCLE, not the step.** 7.5 frames per step is 15 frames per cycle, exactly on
  the grid, with the second leg's contact falling mid-frame where it is invisible because the
  legs are symmetric. Rounding 7.5 up to 8 slows the run by 6.7 %. In a pose-function rig the
  pose is continuous and the renderer samples it, so a key at frame 7.5 is not lost. `[inference]`
- **Add per-side asymmetry and an additive per-joint bias layer.** Perfect left/right symmetry
  is twinning, the first note any lead animator gives; 2-4 degrees on thigh and arm and 1-2 px
  on hipY fixes it. And an amplitude scalar is **not** a personality control: a tired walk has
  shorter stride AND lower hips AND more forward head AND less arm swing AND longer contact
  dwell — per-channel offsets in different directions. `[inference]`
- **Arm-swing extremes are a CHOICE between two things Williams says**, not a settled fact: he
  describes widest-at-down as the real-life mechanic but prefers contact in animation. Choose,
  and say which.
- **In a strict side view, the Williams hip/shoulder opposition is in the transverse plane and
  is invisible.** A picture-plane hip rotation reads as the pelvis tipping. The side-view cheat
  is a small `scaleX` on the shoulder and hip groups plus an x offset of the far limb.
- **Tempo table (per step, at 24 fps, from Williams via the Monmouth adaptation):** very fast
  run 4, run/very fast walk 6, slow run or cartoon walk 8, natural walk 12, strolling 16, tired
  20, slow step 24, slowest 32. ×1.25 for 30 fps. Pick the row from the brief's **verb**, then
  fit the amplitude; do not scale a natural walk's timing to make it feel tired. `[source, but
  note the source table has four shifted parentheticals and the per-step reading has no
  independent corroboration]`
- **Verify a walk by tracing the ankle and by playback at speed.** Silhouettes at five key
  frames are blind to spacing, foot plant and slide — which is where every cycle defect lives.

### 4.3 Face and acting

- **Blink: close faster than open**, lids one frame apart, brows moving with them. 3/1/4 frames
  at 30 fps for a regular blink. **The close eases OUT (fast from frame one), not IN** — though
  at 3 frames the curve is noise and you are really authoring positions.
- **The lid edge is an arc, and the lid rides the eyeball.** A rectangular lid scaled in Y
  closes with a straight edge across a round eye: a roller shutter. When the pupil looks down
  the upper lid drops with it, roughly 30-40 % of the pupil's travel; a lid that stays put while
  the eye moves is the commonest tell in cheap 2D character work.
- **Blinks are placed by MEANING, never by hash.** On a phrase end, a thought change, a change
  of eye direction, before or after a head turn as anticipation. Hashing produces the nervous
  android. Use `prand` to jitter durations by a frame, and reserve hashing for **texture**
  (particles, foliage, crowds), not for acting.
- **The head-turn cheat needs three things a rigid slide does not have:** the face group
  compresses in X to about 0.85 at full turn; the far eye travels further and narrows more than
  the near eye (so the eyes cannot live in one rigid group); the features arc on the head's
  curve, so there is a small Y offset through the middle.
- **Percentage rules for anticipation and overshoot break down below ~12-15 px of counter-travel.**
  A 15 % anticipation on a 34 px head turn is 1.3 px per frame; `back.out(2.5)` on a 5-degree
  hair tween is a 0.94-degree overshoot. For hair follow-through to read against a 6-degree
  head turn, the overshoot needs to be 8-12 degrees — larger than the parent's travel.

### 4.4 Jumps, smears, lip-sync

- **Author the jump by choosing hang time and apex, then derive gravity**: `g = 8H/AIR²`,
  `v0 = g·AIR/2`. Gravity is a design parameter, not 9.81, and the Odd Rule falls out free.
- **A 15-frame hang time is a ONE-FOOT HOP, not a body-height jump.** `hang = 2·√(2H/g)`, so
  0.5 s of total flight is a 0.31 m apex; a body-height leap (1.75 m) needs about 1.2 s, i.e.
  **30-36 frames**. `[computed]`
- **Either compute the partner scale (`sx = 1/sy`) everywhere or drop the volume claim.** Four
  of five phases in the standard jump recipe break volume by 5-9 %. In practice drop the claim:
  a landing squash that widens *less* than reciprocal reads heavier, because a real body loses
  height into bent knees. But say which you are doing.
- **Smear trigger: about 1.5 % of frame width per frame, or half the object's own width per
  frame.** An absolute pixel figure does not travel across resolutions.
- **Size the smear so it CLOSES the gap:** `width · sx >= per-frame travel + width` on the
  fastest **rendered** frame. A 60 px puck travelling 205 px in its first frame needs 4.4×; the
  common `K = 1.6` gives 2.02× and leaves an 83 px hole, so the object still strobes — as an
  ellipse. `[computed]`
- **Ghost spacing decides the read.** One-frame spacing on a 40 px/frame move gives four
  discrete silhouettes: a **multiples** read (a 1940s cartoon effect), not a blur. For blur, use
  sub-frame spacing and 6-8 low-opacity copies, which strobes *less* because they overlap. For
  multiples, hold each 1-2 frames and **deform each copy progressively** — undeformed
  duplicates are the giveaway.
- **Lip-sync: shapes lead the sound by 3 frames** (round the source's "at least two frames at
  24 fps" **up**, not down; rounding down gives less lead than the stated minimum in the exact
  direction the source warns about). Closed consonants (M/B/P) earliest. Ten Preston Blair
  shapes in the DOM from frame 0, exactly one visible, visibility **snaps** — never crossfade
  two visemes.
- **2-4 shapes per WORD, not one per phoneme**; no viseme under 2 frames; rest at phrase ends
  only, never mid-sentence. A cue every 5 frames is a chattering mouth. **And the jaw is
  mandatory**: jaw-open amount is the primary volume signal and the viseme is decoration on top
  of it. A shape-only mouth reads flat however correct the visemes are.
- **What genuinely needs a simulation:** weight-correct balance (a constrained whole-body
  solve), collision response, coupled cloth/hair/fluid. **IK is not on that list.** Substitutes:
  delayed-copy follow-through `child(t) = gain · parent(t − lag)`, a closed-form damped
  oscillator `θ = A·cos(ωt)·e^(−kt)`, or a pre-baked table sampled by frame.

---

## 5. Camera and transitions

Depth: [`motion-rules.md`](motion-rules.md) Rules 7-8.

- **CSS has a lens.** `perspective` **is** the focal length and `translateZ` is the dolly.
  Animate `translateZ` with `perspective` fixed for a **true push** (per-layer parallax falls
  out free); animate `perspective` with `translateZ` fixed for a **zoom**; animate both in
  opposition for a **dolly zoom**. Scale on a wrapper is a third thing, a crop-and-blow-up, and
  it is what most "push" recipes actually produce — which is why HTML camera moves so often read
  as a zoom on a photograph. `[CSS 3D transform specification]`
- **The counter-translate formula depends on which move you are making.** `T = −offset·S`
  recentres the target; **holding** a point where it already sits under scale `S` needs
  `T = −offset·(S−1)`. And the offset is **measured** with `getBoundingClientRect` after
  `document.fonts.ready`, never typed: a hand-typed offset is wrong the moment the copy changes
  length.
- **Fixed parallax ratios (1.0 / 0.5 / 0.2) are correct only for a LATERAL move.** For a push, a
  layer's apparent displacement and scale both follow `d/(d−t)`, so the ratio between layers
  changes continuously and cannot be a constant; substituting the lateral constants gives layers
  that separate linearly when they should separate hyperbolically, which is precisely what makes
  a fake push read as sliding planes. **Counter-scale each layer by its own `d/(d−t)` at rest**
  or every element pushed back on Z arrives smaller than the layout intended and the type sizes
  in the spec no longer hold. `[inference from the projection arithmetic]`
- **Camera drift is a REGISTER, not a law.** Locked-off is deliberate and common: product hero
  shots, Swiss graphics, most title cards. Perpetual low-amplitude drift is the signature of one
  contemporary style and is a large part of why current explainer work looks interchangeable; it
  also fights legibility, because drifting text is text you are still tracking. When used:
  2-8 px X, 1-4 px Y, X:Y frequency ratio 1.2-1.5.
- Camera eases: `power2.out`, `power3.out`, `power2.inOut`. Never spring or back on a camera.
  Zoom duration 1.0-2.0 s (under 0.8 teleports, over 2.5 drags), dwell >= 1.0 s after settling.
- **Transitions: pick ONE primary (60-70 % of scene changes) plus one or two accents.** A
  different transition at every cut is the tell.
- **A dip to black or white is a standard device, not a defect.** Chapter breaks, emphasis, the
  outro. The amateur tell is an **unmotivated dip of inconsistent length**: designed = a dip
  whose length matches the piece's declared gap cadence within one frame; undesigned = a length
  used nowhere else, or over 8 frames with no reason.
- **Exits are mandatory wherever the frame goes empty.** "Exit animations are banned except on
  the final scene" contradicts the measured reference, which has 10 blank runs — you cannot
  produce an empty frame without something exiting. The real rule is: never stack an exit tween
  and a cross-transition on the same element at the same `T`.
- **Eye-trace across the cut**, which no other rule here covers and which is the primary tool an
  editor uses to make a cut invisible: put the incoming subject within roughly 15-20 % of frame
  diagonal of where attention sat on the outgoing frame, or displace it deliberately and give
  6-8 frames to find it. Two shots can match on graphics and velocity and still cut badly.
- **Transitions are exempt from the 1/3 travel rule by class.** Whip pans, full-frame wipes,
  cards flying through frame and infinite zooms cross the whole frame in a straight line at one
  acceleration, and should.
- **Loops need velocity continuity, not just value continuity.** A value match with a velocity
  mismatch hitches every cycle. Use a full-period sine or an exact 360-degree rotation rather
  than an eased tween returning to its start, and put the wrap where velocity is **highest**.
  `yoyo` is exactly the case where value matches and velocity reverses, which is why long yoyo
  drifts read as a pendulum.

---

## 6. Sound

Depth: [`sound-design.md`](sound-design.md).

- **Every class has one anchor sample that lands on one frame.** Impact/tick: the transient
  onset. Whoosh: the loudest sample. Riser/reverse swell: the **last** sample. Sub-drop: the
  onset of the pitch fall.
- **The settle frame is where motion becomes IMPERCEPTIBLE, not where the tween ends.** For
  `expo.out` the position is at 99 % of target at t = 0.66 of the duration; anchoring on the
  tween end puts the hit 3-6 frames late on every hard ease. Define it as the first frame where
  the fitted speed drops below about 1 px/frame at 1080p — roughly 55-70 % of the tween for
  `power4.out` and `expo.out`. `[inference]`
- **Placement: 0 to +1 frame LATE for a hard click, never early.** The point of subjective
  simultaneity sits at or after zero audio lag. Two frames late is the practical ceiling; three
  is technically inside detection and reads as a mistake to any editor in the room. State rules
  in milliseconds first, frames second, because 30 and 60 fps differ.
- **The whoosh is the only legitimate early start, and it is early in FILE start, not in
  perceptual onset.** Every whoosh gets a 60-150 ms swell before its peak regardless of ease:
  build the envelope as `swell(t) · speed(t)`, peak on the peak-velocity frame, file starting
  2-4 frames earlier. A whoosh with an instantaneous attack is a burst of static. **And the
  whoosh alone never marks the settle** — it decays with the ease and the settle gets a tick.
- **Three synthesis fixes that decide whether the stem passes a review:** carry the filter state
  across blocks (`sosfilt(..., zi=zi)`) or every whoosh carries a 94 Hz buzz and every riser a
  47 Hz one; use **pink** noise, not white, as the source; and build an impact as **four
  layers** — transient (1.5-9 kHz click, 5-15 ms), body (120-250 Hz with a short pitch drop,
  the layer phones actually reproduce), sub (50-90 Hz, high-passed at 30 Hz), tail (200-600 ms).
  `[measured by running the code]`
- **Tune tonal SFX to the bed's key.** Sub-drop landing pitch, shimmer partials, riser top note.
  Use genuinely inharmonic partial ratios for a glint (1, 2.76, 5.40, 8.93), not equal spacing:
  equal 3.5-semitone steps are a diminished-seventh cluster in no key.
- **Do dip the bed under a structural hit** — 50-200 ms, 3-6 dB, fast release, as a hand-placed
  `data-automation` volume lane. The tooling's refusal to *auto*-carve a bed under an SFX group
  is correct (it would pump on every whoosh) and is not a mixing rule. The bed being loud at the
  hit is why a hit reads small.
- **The pre-hit drop**, the most-used device in trailer and motion-graphics sound and previously
  unnamed here: cut bed and stem to silence 2-6 frames before a structural hit, then the hit.
- **Thin the cue list.** One transient per card start is a drum part: a professional pass sounds
  perhaps half to two thirds of the cuts, always the structural ones, and lets the rest ride on
  the bed's grid. Cards inside a rapid-fire run get **one** sound for the run. Word ticks off by
  default.
- **Vary per instance** from the cue index: ±1-2 semitones, ±10 % decay, ±1.5 dB. Identical
  repeated transients are a fast tell for a synthetic pass.
- **Pan from `cx`.** `pan = (cx/width − 0.5) · 0.6`, constant-power, with the impact body and
  sub-drop centred and mono below about 120 Hz.
- **Master chain:** high-pass the bed at 30-40 Hz under a sub-drop, a gentle 2:1 bus compressor,
  and a **true-peak limiter at −1 dBTP as the last stage**. Two hits within a bar plus the bed's
  own boom will exceed −1 dBTP at a −15 LUFS gain.
- **Loudness from the delivery spec, not from one film**: AES TD1008 −16 LUFS music / −18 speech
  at −1 dBTP for streaming; EBU R128 −23 LUFS / −1 dBTP European broadcast; ATSC A/85 −24 LKFS
  / −2 dBTP US broadcast; Netflix −27 LKFS dialogue-gated / −2 dBTP; social normalises to about
  −14 and never boosts, so −15 LUFS / −1 dBTP is a defensible web target. **Deliver 48 kHz.**
- **Gate on TRUE peak** from `ebur128=peak=true`, not sample peak from `volumedetect`.
- **Verify on the muxed MP4 in the target player**, not on the WAV: AAC priming (1024-2112
  samples, 21-44 ms) shifts audio in players that ignore edit lists.
- **Picture-side consequence: a hit needs runway.** Leave 4-6 frames clear before an impact for
  a whoosh or riser, land the impact on the hit frame, let the visual tail carry 8-12 frames
  after it. A cut with no runway cannot be scored convincingly however well it is timed.

---

## 7. The grading rubric

Depth: [`grading-rubric.md`](grading-rubric.md).

**Bands.** S exemplary, A professional, B competent with visible faults, C amateur tell present.
Band points S 100 / A 85 / B 65 / C 30. `W = Σ(points·weight) / Σ(weight)` over applicable
criteria. **S = every applicable criterion at S or N/A. A = W >= 90 and no C. B = W >= 75 and
at most two Cs, none of them gates. C = anything else, or any gate at C.**

**A means no visible defect. It does not mean good.** Concept, script, art direction, brand fit
and originality are unmeasured. Print the worst-first table before the aggregate: a studio reads
only the table.

**Gates** (a C caps the overall grade at C; gates carry weight 0 in `W` so one legibility
problem does not also destroy the craft score):

| Gate | Threshold |
| --- | --- |
| Contrast (C13) | worst settled contrast >= 3:1 at the large-text threshold, worst-tile 10th percentile |
| Photosensitive flash (C20) | <= 3 full-frame luminance reversals in any one-second window |
| Audio delivery (C18) | integrated loudness inside the **declared delivery** target; **true** peak inside it |
| Duration and cadence (C23) | rendered frame count exactly as authored |

Two gates were **removed**: dead frames (it gates out animation on twos, deliberate freezes and
end cards, and the cheapest way to pass it was per-frame grain) and safe margins (it gates out
every web-only deliverable and every deliberately cropped full-bleed treatment).

**The criteria, in measurable form:**

| # | Criterion | Measured | S | C |
| --- | --- | --- | --- | --- |
| C1 | Ease discipline | classify from **measured geometry**, not the parsed ease (nesting composes curves); test `overshoot` **first** or every `back.out` files as `out` | 0 linear on non-mechanical spatial moves, 0 direction violations | any linear spatial move, or >15 % direction violations. Exempt: small recedes (<5 % scale, <3 % frame height) and auto-classified ambient (>=2 s, <5 % travel) |
| C2 | Ease vocabulary | cluster sampled **shape** at radius 0.06, per **role** | one shape per role, distinct across roles, >=3 clusters | 1 cluster, or the same ease on hero + secondary + ambient, or overshoot on opacity/colour |
| C3 | Simultaneity | onset clusters and concurrency, counting a declared group or lockup as **one** element and exempting declared audio hits | SI <= 0.34, conc <= 0.34 | undeclared same-frame start of unrelated elements |
| C4 | Hold ratio | stillness per beat; `leadMs` on the **first beat only**; mechanical and looping elements excluded | every beat holdRatio >= 0.30, gaps >= 100 ms | outside the genre band by >0.10 (continuous-camera 0.05-0.35, mixed 0.25-0.65, card-based 0.45-0.85) |
| C5 | Frame integrity | flash frames at cuts; duplicate runs against a **declared cadence**, at full resolution on luma | 0 undeclared flash frames, cadence honoured | a 1-2 frame blank at a cut outside the declared cadence, **or a single undeclared run of more than 8 identical frames** |
| C6 | Settle quality | reversals and amplitude as a fraction of **travel**, centroid-tracked for positional overshoot | inside the register budget (§1.5), no settle with >=2 reversals | outside budget on >15 %, or >=3 reversals, or overshoot on paint |
| C7 | Arcs | N/A unless organic elements are declared; report unmotivated arcs on type and cards | arcs on declared organic moves, one-sided | jitter faults |
| C8 | Secondary motion | **declared pairs only**; `lockedRate` reported, not banded; N/A with no pairs | conforming reaction on every declared pair | <50 % of declared pairs conform |
| C9 | Anticipation | register-gated: playful/energetic graded on declared impact verbs; corporate/premium N/A with a **ceiling** (>30 % of hero moves = over-animated) | anticRate >= 0.80 in a playful register | anticRate 0 with >=3 declared impact verbs |
| C10 | Timing contrast | CV and ratios; on a detected grid, **range of bar multiples** instead | R_beat >= 3, cv >= 0.30, R_move >= 3 (ambient and transitions excluded) | cv < 0.10, or R_move < 1.5 |
| C11 | Distance-duration | `rho` within **entrance** moves only; 1/3 rule for in-scene repositions only, transitions exempt by class; strobe at 0.5 % frame width/frame | rho >= 0.40 within class, 0 violations, 0 strobe frames | rho < 0 within class, or >3 violations |
| C12 | Type hierarchy | sizes drawn from a declared scale (±10 %); `minSize` | every size on the scale, minSize >= 18 px (32/90 in-feed) | minSize < 18 px at 1080p |
| C13 | Contrast | settled window only, local ground, **tiled**, 10th percentile; APCA Lc reported as advisory | worst >= 4.5:1 | worst < 2.5:1, or <95 % of settled frames >= 3:1 |
| C14 | Safe margins | broadcast: 93 % action / 90 % title. web: 4-5 %. social: platform rectangles. Ink test restricted to tracked components | 0 breaches for the declared delivery | breaches beyond the B band; cropped type declared by element is exempt |
| C15 | Readability dwell | two models by role | body: cps <= 13 and >= 833 ms. display: >= 300 ms per word | display < 130 ms per word or under **8 frames** absolute |
| C16 | Palette adherence | share of chromatic pixels within ΔE2000 8 of a declared palette entry; dominant ground is a palette entry; banding after encode | >= 0.95 adherence | < 0.80 adherence |
| C17 | Transition design | designed vs undesigned handoff; direction continuity at the cut; type census | 100 % designed, direction continuous and neither side below 30 % of peak, primaryShare >= 0.60, nTypes <= 3 | <75 % designed, or a different type at every cut |
| C18 | Audio sync and delivery | onset lock, window centred **one frame early**; `hitRate` against **bar lines** where a tempo exists; true peak and loudness from the declared delivery | lockRate >= 0.80, meanAbs <= 20 ms, gates pass | lockRate < 0.40, or bias > +40 ms (early) or < −100 ms (late), or delivery gate fails |
| C19 | Reveal craft and motion blur | share of opacity-only entrances; structural reveal devices used; blur/shutter coverage of fast frames | opacity-only <= 0.25, >=2 structural devices, 100 % of fast frames covered, no blurred frame touching a cut | opacity-only > 0.60, or <60 % blur coverage |
| C20 | Photosensitive flash | full-frame luminance reversals per rolling second | <= 3 | > 3 (**gate**) |
| C21 | Restraint | concurrent ambient motions; hero moves in flight; onsets per 10 frames | exactly one ambient during breathe, one hero move in flight | >=3 concurrent ambient tweens, or >1 onset per 10 frames sustained |
| C22 | Framing | distinct alignment positions; margin consistency; focal-point count; optical vs geometric centring | two or three alignment positions, one focal point per settled frame | one alignment position per element |
| C23 | Encode and delivery QC | frame count, `pix_fmt`, `color_range`, chroma bleed, banding, poster frame, end-card hold, loop seam | all pass | frame count wrong (**gate**) |
| C24 | Eye-trace and screen direction | hero centroid jump across cuts as a fraction of frame diagonal; parallax ratios; transition direction sequence | report-only | report-only |

**Weights.** 2: C1, C3, C17, C19. 1: everything else except the gates. 0: C13, C20, C23-duration,
C18-delivery (gates).

**Declaration budget.** Every hard criterion has an escape hatch and the author writes the
manifest, so the report prints the number of declarations and the number of criteria whose band
improved because of one. Flag any pass that depends on more than a few. A declaration is a claim
about intent and should be visible as one.

**Two things to grade differently.** A **blocking pass** (linear tweens and holds, timing judged
alone before curves are applied) is supposed to fail every ease rule here; that is the step a
professional does first. And grade the **delivered file**, not only the frame dump: motions at
the amplitudes prescribed here (breathe at scale 1.012, decorative opacity 12-25 %) can be
quantised out entirely by H.264 at social bitrates.

**Scope limit.** Every pixel metric here is calibrated to a high-contrast graphic register
(ink = `|luma − ground| > 28`). A tonal or photographic piece registers almost no ink and several
criteria then mis-measure rather than fail loudly. Raise a confidence flag below an ink-coverage
floor, or declare the rubric out of scope for footage-led work.

---

## 8. The twelve fastest ways to make it look amateur

Each with the principle it violates and the detector that catches it. Full vocabulary in
[`twelve-principles.md`](twelve-principles.md) §13.

1. **PowerPoint** — every element enters `y: 30, opacity: 0`, same ease, same duration, all at
   once. *Detector:* one ease shape for the whole film; identical entrance directions; beat CV
   < 0.18; first significant step on frame 0.
2. **Floaty** — `sine`/`power1` on everything, durations at the slow end regardless of distance.
   *Detector:* peak/avg velocity below ~2 on entrances **in a register that is not declared
   calm** — `sine.out` and `power1.out` are the correct choice on a slow premium reveal.
3. **Weightless** — nothing winds up, nothing trails, things stop dead, opacity-only entrances.
   *Detector:* `sx/sy` constant through every impact; zero anticipation runs; opacity-only
   entrance share above 0.6.
4. **Robotic** — linear spatial tweens, dead-straight paths, uniform stagger. *Detector:*
   step-series CV < 0.15, **plus** uniform duration, uniform distance and a single ease. Uniform
   lag alone is not the defect: every correct stagger produces it.
5. **Cheap / bouncy** — `back.out` on everything, elastic on type, overshoot as spice. *Detector:*
   reversals >= 1 on most settles in a non-playful register; overshoot > 13 % of travel.
6. **Flat** — pure black ground, one centred text block, web-sized type, decorative opacity under
   10 %. *Detector:* one moving region and no luma change elsewhere; centroid always in the middle
   third; fewer than 3 type sizes.
7. **Jump cut** — scenes pop fully formed, exits fade then the next entrance runs, first motion at
   t = 0, cuts ignore the onsets. *Detector:* no overlap at the cut; direction discontinuity;
   clip boundary drift.
8. **Stutter** — layout-property tweens snapping to whole pixels on slow tails, duplicate frames
   in a segment that should move, strobing without a shutter. *Detector:* `0,0,1` step patterns;
   per-frame edge travel over 0.5 % of frame width.
9. **Flashed and gone** — the reveal lands at `DURATION − 0.2 s`, the climax has no hold.
   *Detector:* stillness after the last climax step < 1 s.
10. **Swoopy** — arcs bent onto type and cards to satisfy an arc-rate target. *Detector:* one-sided
    perpendicular deviation above ~3 % of chord on a text or card element.
11. **Over-animated** — a wind-up, a trailing shadow and a different ease on every element.
    *Detector:* anticipation on more than 30 % of hero moves; three or more concurrent ambient
    tweens; more than one onset per 10 frames sustained across a beat.
12. **Synthetic sound** — a transient on every cut, identical impacts, no space, no pre-hit drop.
    *Detector:* cue onsets per rolling second above 4; zero variation in transient spectra; no
    volume automation on the bed at any structural hit.

---

## Attributions

**LottieFiles `motion-design` skill** (MIT, © LottieFiles) — `director/disney-principles.md`,
`director/choreography.md`, `director/core-philosophy.md`, `director/narrative-structure.md`,
`director/motion-personality.md`, `director/context-adaptation.md`, `director/emotion-mapping.md`,
`director/decision-framework.md`, `reference/timing-easing-tables.md`,
`reference/quality-checklist.md`, `reference/troubleshooting.md`,
`reference/property-selection.md`, `SKILL.md`. Source of the squash and stretch ratios,
anticipation duration and magnitude, follow-through child delay, overshoot budgets, exaggeration
by personality, the duration and stagger tables, the counter-motion table, the 1/3 rules and the
severity tiers. The MIT licence and the LottieFiles attribution are stated in the skill's own
frontmatter and are verified.

**The HyperFrames skills** (HeyGen, **Apache-2.0, verified**: the locally installed skill folders
carry no licence file and no licence field in their frontmatter, which is why a local-only check
reads as unverified, but the upstream project the skills document is `github.com/heygen-com/hyperframes`,
whose GitHub licence metadata reports `Apache-2.0` / "Apache License 2.0". The composition contract,
the CLI and the runtime the skills describe are that project's) — `hyperframes-animation`
(`rules-index.md`, `techniques.md`, `transitions/overview.md`, the `adapters/` and the named
rules: `spring-pop-entrance`, `press-release-spring`, `physics-press-reaction`,
`reactive-displacement`, `nudge-curve`, `waterfall-entry`, `motion-blur-streak`,
`depth-of-field-blur`, `viewport-change`, `multi-phase-camera`, `3d-camera-flight`,
`kinetic-beat-slam`, `gradient-text-sweep`, `hacker-flip-3d`, `chromatic-glitch`,
`discrete-text-sequence`, `asr-keyword-glow`, `sine-wave-loop`, `particle-burst`,
`svg-icon-enrichment`, `gsap-effects`); `hyperframes-creative`
(`references/motion-principles.md`, `beat-direction.md`, `video-composition.md`,
`typography.md`); `hyperframes-core` (`determinism-rules.md`); `hyperframes-audio`
(`references/attributes.md`, `diagnosis.md`). Source of the contract itself, the load-bearing
GSAP rules, the spring closed form and damping table, the ease-direction rules, the transition
catalogue, the composition and typography figures, and the audio group model.

**The `manifesto` skill** — `SKILL.md`, `scripts/grade-original.py`, `scripts/segment.mjs`,
`scripts/track.mjs`, `scripts/measure.mjs`, `scripts/audio-beats.mjs`,
`scripts/bed-tempo-fit.py`, `scripts/bed-compose.py`, `scripts/vo-transcribe.py`,
`scripts/vo-verify.py`, `library/INDEX.md`, `library/apple-business-essentials.md`. Source of
every `[measured]` figure here: the frame-boundary bias constants, the cut and blank-gap model,
the Range Selector translation, the strobe case, the shutter pipeline, and the grader's own
checks.

**Frank Thomas and Ollie Johnston**, *The Illusion of Life: Disney Animation* (1981). The twelve
principles. **The book's text was not obtained.** Definitions and page numbers are quoted through
two secondary summaries that cite it directly:
https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation and
https://handwiki.org/wiki/Twelve_basic_principles_of_animation (squash p. 49, slow in and slow
out **p. 47**, anticipation pp. 51-52, follow-through pp. 59-62, moving hold pp. 61-62, appeal
p. 68). Also https://en.wikipedia.org/wiki/Squash_and_stretch .

**Richard Williams**, *The Animator's Survival Kit*. **The book was not obtained** (the
archive.org text was truncated before the walks chapter; a CMU handout PDF of that chapter is 76
pages of image-only scans with zero extractable text). The walk vocabulary, the four key poses,
the arm opposition and the tempo ladder are quoted from student notes on the book and from an
instructional adaptation, all of which are secondary:
https://animation.monmouth.edu/instruct/animation/walk-cycle/ (the tempo table, "adapted from The
Animator's Survival Kit", stated at 24 fps; **four of its eight rows carry shifted
parentheticals** and the per-step reading has no independent corroboration),
https://cloytoons.wordpress.com/2015/12/01/animation-research-walk-cycle/ and
https://cloytoons.wordpress.com/2015/12/06/animation-research-run-cycle/,
https://www.tumblr.com/zak-graphicarts/174088404863/richard-williams-the-traditional-walk,
https://edwardboyleanimation.wordpress.com/2016/01/04/walk-cycle-research-3-animators-survival-kit/,
https://mister-chad.com/animation/walk+cycle,
https://blogs.ulster.ac.uk/scottmoore/2024/10/21/animation-strategies-animation-walk-and-runs-regular-run-cycle/.

**Preston Blair**. The ten mouth shapes and the walk chart, quoted through
https://www.garycmartin.com/mouth_shapes.html and https://garycmartin.com/phoneme_examples.html
(Gary C. Martin's rendering and extension of the Blair series),
http://johnkstuff.blogspot.com/2010/02/preston-blair-simple-walk.html (John Kricfalusi's
annotation) and https://angryanimator.com/word/2018/03/20/preston-blair-deciphered/ (Angry
Animator, "Preston Blair Deciphered").

**Web sources, by area.**

*Animation principles and physics* — Bloop Animation
(https://www.bloopanimation.com/the-12-principles-of-animation/,
https://www.bloopanimation.com/blinking-animation/,
https://www.bloopanimation.com/the-art-of-smear-frames/); Interaction Design Foundation, Laia
Tremosa (https://ixdf.org/literature/article/ui-animation-how-to-apply-disney-s-12-principles-of-animation-to-ui-design);
Alejandro Garcia, "Physics in Animation" (https://www.animatorisland.com/physics-in-animation-how-important-is-it/,
written by Garcia himself, a primary source in this chain); Animation Apprentice
(https://animationapprentice.blogspot.com/2020/09/do-animated-characters-need-to-blink.html);
Envato Tuts+ (https://design.tutsplus.com/tutorials/animation-for-beginners-how-to-animate-a-head-turn--cms-26487);
SunStrike Studios (https://sunstrikestudios.com/en/blog/timing_in_animation/); NYU FRL
(https://frl.nyu.edu/keyframing-the-basics/); School of Motion (graph editor, follow-through,
eases, six transitions, common 2D mistakes); Ben Marriott
(https://elements.envato.com/learn/ben-marriott, https://www.benmarriott.com/motion-foundation);
smear-frame sources (https://www.traditionalanimation.com/2017/smear-speed-motion-blur-effects-in-animation/,
https://en.wikipedia.org/wiki/Smear_frame, https://idearocketanimation.com/8857-animation-techniques-smear/);
Adobe on Posterize Time (https://helpx.adobe.com/after-effects/using/time-effects.html); Creative
COW on animating in 2s; ProVideo Coalition and Spotlight FX on the 180-degree shutter.

*Tooling* — GSAP docs (https://gsap.com/docs/v3/Eases/, `.../Eases/CustomEase/`,
`.../Eases/CustomWiggle/`, `.../Eases/SteppedEase/`, `.../GSAP/Tween/`, `.../GSAP/Timeline/`,
`.../Plugins/Physics2DPlugin/`, `https://gsap.com/resources/svg/`,
`https://gsap.com/resources/getting-started/Easing/`,
`https://gsap.com/resources/getting-started/Staggers/`, the 3.13 all-plugins-free release
https://gsap.com/blog/3-13/, and the 3.14.2 source for the ease formulas); MDN `transform-box`;
https://svg-tutorial.com/svg/transform/; https://dockyard.com/blog/2019/11/29/an-animated-tale-of-svg-transforms;
CSS-Tricks on knockout text.

*Design systems* — Material Design 1 (https://m1.material.io/motion/duration-easing.html,
`.../movement.html`); Material Design 3 tokens, **second-hand** via
https://www.mdui.org/en/docs/2/styles/design-tokens because the canonical page renders
client-side; IBM Carbon (https://v10.carbondesignsystem.com/guidelines/motion/overview/); Apple
WWDC23 "Animate with springs" (https://developer.apple.com/videos/play/wwdc2023/10158/) and the
older iOS HIG animation text via mirror (the current HIG Motion page renders client-side);
NN/g (https://www.nngroup.com/articles/animation-duration/); Val Head; Issara Willenskomer's UX
in Motion Manifesto (cited **for its taxonomy only, never for a number**); Wojciech A. Hoffmann
(https://www.motiondesignprinciples.com/).

*Type, reading and captions* — Netflix Timed Text Style Guides (General Requirements, English
(USA), Subtitle Timing Guidelines); BBC Subtitle Guidelines **through two secondaries**
(https://www.clevercast.com/bbc-subtitling-guidelines/,
https://broadcastwriter.com/2024/12/12/bbc-subtitle-style-guide-2024/) because the BBC hosts were
unreachable; Closed Caption Creator; https://legibility.info/rules-for-text-in-videos;
https://www.rocketshiphq.com/text-overlays-video-ads-mobile/; Virtual Speech on speaking rate;
**Di Nocera, Ricciardi and Juola** (2018), IJHFE 5(4):293, RSVP comprehension by speed (*not*
Benedetto et al., a misattribution corrected in this revision); **Primativo et al.** (2016), PLOS
ONE, RSVP speed limits (https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0153786);
Lee, Forlizzi, Hudson, "The Kinetic Typography Engine", UIST 2002; Lee, Jun, Forlizzi, Hudson,
DIS 2006; Ford, Forlizzi, Ishizaki, CHI 97 Extended Abstracts pp. 269-270 (**cited through the
2002 paper's summary**; the abstract page returned 429/403); SVGator's kinetic-typography guide.

*Editing, framing and delivery* — https://en.wikipedia.org/wiki/Match_cut,
https://en.wikipedia.org/wiki/180-degree_rule; StudioBinder on match cuts and the push-in shot;
Beverly Boy on camera movements; Bitcut and Beat2Cut on beat-sync editing; FilmmakerIQ, "Editing
to the Beat, the One Frame Trick"; Film Editing Pro on cutting music cues; NAB "Television Safe
Areas Redefined" reproducing SMPTE EG 2046-3, and SMPTE ST 2046-1 for the 93 %/90 % figures;
PremiumBeat, "Default Title Safe Guides Are a Sham"; Kreatli's safe-zone hub and Ignite Social
Media on TikTok and Reels bands; artofstyleframe.com on visual hierarchy; story-boards.ai on
timing and transitions; lumitree.art on parallax ratios; W3C Understanding SC 2.3.1 (three
flashes); APCA in a Nutshell; WCAG 2.2 SC 1.4.3.

*Audio* — Selfridge, Moffat and Reiss, "Sound Synthesis of Objects Swinging through Air Using
Physical Models", *Applied Sciences* 2017 7(11):1177; Andy Farnell, *Designing Sound* (MIT Press
2010); Karplus-Strong via CCRMA; perfectcircuit.com and modeaudio.com on kick synthesis; BOOM
Library, Krotos and Native Instruments on trailer impact layering; Pixflow on transition sounds
and whoosh placement; Videomaker on SFX with motion graphics; Point Blank on reverse transitions;
pitchdrift and sfxengine on common mistakes; ITU-R BS.1770-4 (K-weighting), ITU-R BT.1359-1
(sync detectability), EBU R128 and R37, ATSC A/85, AES TD1008, Netflix sound mix specifications,
YouTube normalisation; Apple TN2258 and Firefox bug 1321249 on AAC priming; Justin London,
*Hearing in Time* (the 100 ms inter-onset figure, **which is about judging rhythmic quantity, not
about two clicks fusing**); Vatakis and Spence 2007 via Takehana, Uehara and Sakaguchi 2019, PLOS
ONE; https://en.wikipedia.org/wiki/Point_of_subjective_simultaneity.

*Shape language and studios* — https://blog.cg-wire.com/character-shape-language/ and
https://pixune.com/blog/shape-language-technique/; Communication Arts on Buck and Giant Ant;
Cartoon Brew on Metamorphosis and the Duolingo acquisition; Motion Hatch 098 with Jay Grandin;
School of Motion's Ordinary Folk interview and https://www.ordinaryfolk.co/about; Mattrunks;
STASH; the Gunner legacy site and Gunner School; designyourway's studio list; Motionographer's
Metamorphosis interview (**search summary only**).

**Sources cited in earlier revisions and withdrawn**, listed so nobody re-adds them: a Williams
blocking-order quote attributed to Edward Boyle (not on that page); a corroborating tempo ladder
attributed to "Altea Claveras" (no URL, untraceable); per-consonant lip-sync lead times
attributed to High On Films (the page fetches and contains no such breakdown); a "baby schema"
quote attributed to the shape-language sources (in neither page); a Behance page for Gunner's
Google Home claims (no URL); a "Studio Ahremark case study" for Ordinary Folk's identity (no
URL); a forced-alignment tolerance "above 200 ms" attributed to arXiv 2406.19363 (not in the
abstract, and conventional evaluation is far tighter); and Made Good Designs, read only via
search summary and therefore no longer a basis for any figure.

---

Every claim in this document that could not be traced to a source has been rewritten as an
explicit inference with lowered confidence. The full list of corrections applied and claims
downgraded is in [`corrections.md`](corrections.md).
