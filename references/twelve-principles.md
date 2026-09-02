# The Twelve Principles of Animation, for Motion Graphics

Reference for the `manifesto` skill. Every recipe below is written for the HyperFrames
contract: one paused GSAP timeline, every tween a `fromTo` with an explicit from-state,
transforms and paint-only properties (`x`, `y`, `scale`, `rotation`, `opacity`, `filter`,
`clip-path`, `color`), never `width`/`height`/`top`/`left`, no `Math.random` or `Date.now`,
finite repeats, and state that is a pure function of timeline time.

**Revision 2 (2026-09-02).** This document has been corrected against a full source
audit and a practitioner review. Numbers that could not be traced to a source are now
labelled inference and carry lowered confidence; recipes that contradicted the
document's own detectors have been rewritten; four contract violations have been fixed.
Every change is listed in `corrections.md` in this directory. Where a threshold is a
tuning parameter rather than a measured or sourced figure it now says so explicitly, and
a grader should expose it as a knob, not a law.

Every number carries a basis. `<skills>` is the local skills root (the directory that
holds the `motion-design`, `manifesto`, `hyperframes-animation` and `hyperframes-creative`
skills; the HyperFrames pair is installed in the user-level skills directory, the other
two under the `E:` skills tree). "LottieFiles" means the LottieFiles `motion-design` skill
(MIT) at `<skills>/motion-design/`. "HF" means the HyperFrames skills bundle (Apache-2.0,
HeyGen); paths are given as `hyperframes-animation/...` and `hyperframes-creative/...`.
"Manifesto" means `<skills>/manifesto/SKILL.md` and
`<skills>/manifesto/scripts/grade-original.py`. "Computed" means a value
derived in this document from a stated formula (the script and its output are reproduced
in Appendix A). "Inference" means this document's own reasoning, not a canonical figure.

## Contents

- 0. Scope, sources, and the measurement primitives every signature uses
- 1. Squash and stretch
- 2. Anticipation
- 3. Staging
- 4. Straight-ahead action and pose-to-pose
- 5. Follow-through and overlapping action
- 6. Slow in and slow out
- 7. Arcs
- 8. Secondary action
- 9. Timing
- 10. Exaggeration
- 11. Solid drawing
- 12. Appeal
- 13. Which principles generated motion graphics miss, and how it reads
- 14. Four things the twelve principles do not name (masked reveal, per-layer motion blur, luminance, the blocking pass)
- Appendix A. Computed ease and overshoot tables
- Appendix B. Sources

---

## 0. Scope, sources, and measurement primitives

### 0.1 Where the canonical definitions come from

The twelve principles were set out by Frank Thomas and Ollie Johnston in *The Illusion of
Life: Disney Animation* (1981). This document does not have the book's text; the canonical
definitions are taken from the Wikipedia summary of the book, which cites it directly
(https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation), and from the
LottieFiles UI adaptation (`<skills>/motion-design/director/disney-principles.md`).
Where a Thomas and Johnston phrase is quoted, it is quoted from the Wikipedia page's
attribution, not from a page number.

Two things the reader should hold in mind throughout:

1. The LottieFiles numbers are written for **UI** (buttons, cards, tooltips) and mostly
   assume 60fps: its "2-4 frames (30-65ms)" for squash impact only works at 60fps. At the
   30fps authoring grid manifesto uses, 30-65ms is 1-2 frames. This document gives both
   the millisecond figure and the frame count at 30fps and 60fps.
2. HyperFrames' own creative references state that video is not UI: "Subtle reads as
   static at 30fps. Err toward more movement than feels safe" and web-sized amplitudes
   are invisible (`hyperframes-creative/references/video-composition.md`, "Motion
   Intensity" and "Scale"). So the LottieFiles pixel amplitudes (a 5-10px card shift, a
   10-20px arc) are lower bounds for a 1080p frame. Where this document scales them up it
   says so and marks the scaled figure as inference.

### 0.2 The contract, restated once

From `hyperframes-animation/rules-index.md` ("The contract, every rule assumes this"):
one paused timeline registered on `window.__timelines`; `fromTo` with explicit
from-states, `immediateRender: false` when re-owning a property on the same element;
absolute values, never relative `+=`; no `Math.random` or `Date.now`; finite repeats;
transforms and paint-only properties; group staggers capped so items x stagger <= ~0.5s;
no CSS `transition` on animated elements; layout measured only at build time.

**Permitted primitives beyond the plain eases.** `CustomEase` and `CustomWiggle` are
pure functions of progress, carry no state, and have been free in GSAP since 3.13
(2025-04-29, https://gsap.com/blog/3-13/; https://gsap.com/docs/v3/Eases/CustomEase/).
They are legal under the contract and are the correct tool wherever this document would
otherwise chain two or three tweens to fake one curve (anticipation, the nudge curve, a
decaying shake). A `CustomEase` whose output leaves [0,1] must drive transforms only,
never opacity or colour, which is the same rule as spring overshoot. `CustomWiggle` must
not use `type: "random"`, which is seeded at creation and is not reproducible across
builds; use a hash-seeded sum of decaying sines (section 4(c)) when a specific wiggle
must survive a rebuild.

**Everything goes on the frame grid.** `f(n)` exists so that starts, durations and
settles land on rendered frames. A duration typed in raw seconds (0.55, 0.45, 0.32) ends
between frames at 30 fps, so the settled pose is never rendered and an editor cannot cut
on it. Every start time and every duration in a recipe should be written `f(n)`; the
(e) tables give frame counts as the primary unit with milliseconds parenthetical. Where
a recipe below still shows raw seconds it is legacy and should be quantised on use.

Two HF rules that shape several recipes below:

- "Never overlap conflicting transform tweens on the same element" and the wrapper
  pattern that fixes it: entrance on the parent, secondary transform on the child
  (`hyperframes-creative/references/motion-principles.md`, "Load-Bearing GSAP Rules").
  Squash and stretch, follow-through and arcs all use this parent/child split.
- State continuity by adjacency: when two tweens on the same property must chain, the
  second starts exactly where the first ends, `RELEASE_START = PRESS_START + PRESS_DUR`
  (`hyperframes-animation/rules/press-release-spring.md`). Anticipation and squash both
  chain tweens this way.

The shared preamble every recipe assumes:

```js
const FPS = 30;
const F = 1 / FPS;                        // one frame, the authoring grid
const f = (n) => n * F;                   // frame number to seconds
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true, defaults: { ease: "power3.out" } });
// ... recipes add tweens to tl at absolute times ...
window.__timelines["main"] = tl;          // key must equal data-composition-id
```

### 0.3 Measurement primitives used by every "measurable signature"

These are the quantities a script computes per frame. They are the ones manifesto's
`measure.mjs` and `grade-original.py` already compute, so the signatures below are
written in their terms.

| id | primitive | definition | basis |
| --- | --- | --- | --- |
| M1 | ink mask | pixels whose luma differs from the frame's ground by more than a per-frame threshold. `grade-original.py` uses a fixed 28 levels (of 255) against the frame median; that constant is calibrated to a high-contrast graphic register and breaks twice: a tone-on-tone or photographic frame registers almost no ink, and a full-bleed design covering more than half the frame inverts the median so the background becomes the ink. Derive the split per frame (a percentile or Otsu split), and assert a plausible ink fraction (roughly 0.02-0.60) before trusting any measurement built on it | `grade-original.py` (`mask = abs(gr - ground) > 28`); the per-frame derivation and the fraction assert are inference, prompted by the script's own comment that the ground can flip |
| M2 | ink count | number of pixels in M1, an integral over the frame | manifesto: "Never measure motion on a bounding box ... Use ink COUNT" |
| M3 | centroid | mean x and mean y of M1 pixels, per element region | `grade-original.py` composition block; `measure.mjs` |
| M4 | second moments | standard deviation of x and of y over M1 pixels (call them `sx`, `sy`); a width and height proxy that does not flip by a pixel when one antialiased row crosses the threshold | inference, motivated by manifesto's bbox warning ("at 360p one row of antialiasing crossing the mask threshold flips the height by a pixel and swings the area 4%") |
| M5 | region edges | top, bottom, left, right of ink inside a fixed region, per frame | manifesto `track.mjs` |
| M6 | step series | `d[t] = p[t] - p[t-1]` for any per-frame scalar `p` (centroid, edge, `sx`); its sign is the direction of motion, its magnitude the speed | inference |
| M7 | significance and smoothing | segment the RAW series on re-trigger jumps, smooth within a segment with a 3-frame mean, ignore steps smaller than 2% of the segment mean. The re-trigger test must be a ratio **and** an absolute floor: a jump counts only if it exceeds 1.15x its predecessor *and* some fraction (about 0.1) of the running segment mean. The bare ratio is unstable near zero, and the anticipation detector in section 2(d) deliberately drives the series through zero at the wound-up extreme, where 0.01 followed by 0.02 is a 2x jump and splits the very motion the detector is trying to read as one | `grade-original.py` motion block (1.15, 3-frame convolve, 0.020); the absolute floor is inference |
| M8 | sharpness | mean gradient magnitude over the element region | manifesto "Defocus entry" (mean gradient series 0.064 ... 2.401) |
| M9 | duplicate frames | consecutive bit-identical frames. The zero-duplicates rule is correct for a beat that is supposed to be moving and wrong as a universal: animation on twos, posterised time (`steps()` eases, a stop-motion or retro register) and a deliberate freeze on an end card all produce duplicates on purpose. Judge duplicate runs against a declared cadence (`posterize: 2` makes every 2-frame duplicate correct) and exempt any declared freeze | `grade-original.py` (`mpdecimate` count must be 0); the cadence and freeze exemptions are inference, prompted by Adobe's Posterize Time (https://helpx.adobe.com/after-effects/using/time-effects.html) |
| M10 | settled window | for a beat starting at `a` with duration `d`, measure state between `a + min(0.35, 0.25 d)` and `a + 0.62 d`. `grade-original.py` uses a flat `a + 0.35s` for the start, which produces an **empty window** whenever `0.62 d < 0.35`, that is for any beat shorter than 0.565 s (17 frames at 30 fps). Short beats are common in cut-to-music work (section 9(c) authors beats of 14 and 18 frames), and on those every check keyed to the settled window silently measures nothing and passes | `grade-original.py` (`settled.append((a + 0.35, a + d * 0.62))`); the `min(0.35, 0.25 d)` repair is computed from `0.35 / 0.62 = 0.5645` |

A note on frame rate: every frame count below is given at 30fps unless stated; at 60fps
double it. Manifesto authors on the reference's grid and lets the renderer sample it
(`hyperframes render -f 60` "needs no edit at all", manifesto "Raising the frame rate").

Frame rate is a stated decision, not a conversion detail, because every per-frame
threshold in this document (strobe tolerance, minimum stagger step, offset floor, blank
gap length) scales with it and because it carries a look. Delivery rates in real use are
23.976, 24, 25, 29.97, 30 and 60; 24 halves the strobe tolerance and reads as film, 30 is
the broadcast and social default, 60 flattens the sense of weight and reads as interface
capture. Author on the delivery grid: every cut and gap in this system is a frame count,
so a 30 fps author grid conformed to 23.976 shifts all of them. (Inference; the look
consequence is studio practice, the arithmetic is not in dispute.)

---

## 1. Squash and stretch

### (a) Canonical definition

Thomas and Johnston call this "by far the most important" of the twelve
(https://en.wikipedia.org/wiki/Squash_and_stretch, citing *The Illusion of Life*). It gives
weight and flexibility to an object by deforming it in the direction of force. The
load-bearing constraint: an object's volume does not change when squashed or stretched;
if it stretches vertically it must narrow horizontally
(https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation). The 1930s Disney
artists "had to maintain the overall volume of an object" or it read as growing and
shrinking rather than deforming (Squash and stretch, Wikipedia).

LottieFiles UI adaptation: squash scale about `[1.2, 0.8]`, stretch about `[0.85, 1.15]`;
impact 2-4 frames (30-65ms), recovery 4-8 frames (65-130ms); preserve volume; "skip for
premium/luxury brands" (`director/disney-principles.md`, section 1).

### (b) What it looks like in motion graphics

Motion graphics rarely has a body to deform, so squash and stretch shows up as:

- A **landing** compression. A card, badge, logo or word drops or slams into place and
  compresses along the axis of travel on the impact frame, then recovers. Manifesto's
  product-UI section lists "slam zoom" and stamping treatments; the Hammer treatment in
  `grade-original.py` "stamps its word three times inside one beat".
- A **stretch during fast travel**. A pill or shape flying in elongates along its
  velocity, then relaxes on arrival. This is the same visual job as HF's
  `motion-blur-streak` (a fake velocity smear that peaks at peak speed and resolves to 0
  at the settle); stretch is the shape version, blur is the pixel version.
- A **press** on UI: `press-release-spring` compresses a button to `PRESS_SCALE`
  0.88-0.96 on center and springs back (HF rule). That is a uniform squash without the
  volume swap, which is acceptable for a pressed control because the "force" is into the
  screen, not along it.
- A **counter** that fattens as its value grows (`counting-dynamic-scale`, HF).
- Type: a headline that lands with 2 frames of vertical compression. Keep it small on
  type; letterforms distorted more than about 10% read as broken glyphs rather than
  weight (inference).

What it does not look like: a bouncing ball. LottieFiles says "Skip for premium/luxury
brands" and HF says "Smooth beats bouncy", and both are right about *visible deformation*
(a cartoon squash). They are not a licence to build a weightless film: section 13 names
exactly that failure ("things stop dead with no settle and no deformation"). Premium work
is full of weight cues and empty of cartoon deformation. The working rule: premium takes
squash down to **1-3% with zero oscillation**, not to zero deformation, and spends its
weight budget on the scale settle, the shadow spread and the landing frame instead
(inference, reconciling the two sources against this document's own section 13).

### (c) Recipe

Travel lives on a parent, deformation on a child, so the two transform sets never fight
(HF motion-principles, "split across parent + child"). Volume is preserved by setting
`scaleY = 1 / scaleX`. Transform origin is the contact edge so the squash compresses
toward the ground rather than around the center.

```html
<div class="drop" id="drop">              <!-- parent: travel -->
  <div class="body" id="body">Ship</div>   <!-- child: deformation -->
</div>
<style>
  #drop { position: absolute; left: 860px; top: 380px; will-change: transform; }
  #body { transform-origin: 50% 100%; will-change: transform; }
</style>
```

```js
const T0 = f(6);                 // first motion at frame 6, not t=0 (HF: "Don't start at t=0")
const FALL = f(9);               // 9 frames of fall
const IMPACT = T0 + FALL;
const SQ_X = 1.18, SQ_Y = 1 / SQ_X;   // volume-preserving squash (SQ_X * SQ_Y = 1)
const ST_X = 0.80, ST_Y = 1 / ST_X;   // volume-preserving stretch: 25% elongation on a fast fall

// travel: accelerating fall (ease-in reads as gravity).
// The element starts ABOVE the frame edge, not inside it. Nothing materialises in mid-air
// in professional work, so there is no opacity tween here at all: y is far enough negative
// that the shape is off-frame on frame 0. (#drop sits at top: 380px, height 180px, so
// -600 clears the top of a 1080 frame.)
tl.fromTo("#drop", { y: -600 }, { y: 0, duration: FALL, ease: "power2.in" }, T0);

// stretch along velocity while falling. 6% is invisible at 29px of travel per frame;
// classical practice on a fast fall is 20-50% elongation.
tl.fromTo("#body", { scaleX: 1, scaleY: 1 }, { scaleX: ST_X, scaleY: ST_Y, duration: FALL, ease: "power1.in" }, T0);

// impact: the CONTACT frame IS the squash frame. The squash starts one frame before the
// parent reaches y: 0 and peaks on it, so the deformation is caused by the arrival rather
// than following it. (Section 1(d): "a squash that peaks two or more frames after the
// stop reads as a wobble, not an impact" -- the earlier version of this recipe failed
// its own detector.)
tl.fromTo("#body", { scaleX: ST_X, scaleY: ST_Y },
  { scaleX: SQ_X, scaleY: SQ_Y, duration: f(2), ease: "power1.out", immediateRender: false }, IMPACT - f(1));

// recovery: 6 frames back to rest, decelerating; no overshoot on the shape
tl.fromTo("#body", { scaleX: SQ_X, scaleY: SQ_Y },
  { scaleX: 1, scaleY: 1, duration: f(6), ease: "power2.out", immediateRender: false }, IMPACT + f(1));
```

Text variant for a slam (smaller, and only on display type):

```js
// 1.06 not 1.18: the (e) table caps display type at scaleX <= 1.06-1.10 for glyph
// legibility, and section 11(b) forbids non-uniform scaling of text outright except as a
// measured per-glyph fit. The shape demo above may squash to 1.18; a word may not.
tl.fromTo("#word", { scale: 2.2 }, { scale: 1, duration: f(7), ease: "expo.out" }, T0);
tl.fromTo("#word", { opacity: 0 }, { opacity: 1, duration: f(3), ease: "power2.out" }, T0);  // own envelope, finishes early
tl.fromTo("#word-body", { scaleX: 1, scaleY: 1 }, { scaleX: 1.06, scaleY: 1 / 1.06, duration: f(2), ease: "power1.out" }, T0 + f(5));
tl.fromTo("#word-body", { scaleX: 1.06, scaleY: 1 / 1.06 }, { scaleX: 1, scaleY: 1, duration: f(5), ease: "power2.out", immediateRender: false }, T0 + f(7));
```

**Opacity has its own envelope, always.** Every other recipe in this document puts
`opacity` on the same tween, duration and ease as the position, which leaves the element
translucent through the part of the curve that carries its character. Give the fade its
own shorter tween finishing in the first 40-60% of the move, so the element is fully
opaque while it decelerates and the settle is visible. HF requires the split whenever the
transform overshoots (`gsap-easing-and-stagger`, Spring Eases craft note); the
professional habit is to split it always. (Source for the requirement: HF; the
40-60% figure is inference.)

Under seek: every tween states both ends, later tweens on the same property carry
`immediateRender: false`, and the three tweens on `#body` are adjacent in time so GSAP
threads the values (HF press-release-spring, "State continuity").

### (d) Measurable signature on rendered frames

Using M4 on the element region: the ratio `r[t] = sx[t] / sy[t]` normalized to its settled
value `r_rest`.

- **Squash**: `r[t] / r_rest` rises above 1.0 (wider than tall) for a short run of frames
  around the impact frame, then returns. A stretch on the same axis of travel is the
  inverse excursion (below 1.0) during the frames of fastest travel, immediately before
  the impact.
- **Duration of the excursion**: 1-2 frames at 30fps (2-4 at 60fps) for the impact, 2-4
  frames at 30fps (4-8 at 60fps) for the recovery (LottieFiles 30-65ms and 65-130ms).
- **Volume conservation**: the product `sx[t] * sy[t]` (or M2 ink count, which is more
  robust) stays within about 5% of its settled value through the excursion. If ink count
  swells with the squash the element is scaling, not squashing (threshold 5%: inference;
  the conservation itself: Thomas and Johnston via Wikipedia).
- **Alignment with impact**: the excursion's peak sits on the frame where the M6 step
  series of the travel axis goes to zero (the frame the object stops). A squash that
  peaks two or more frames after the stop reads as a wobble, not an impact (inference).
- **Direction**: the compressed axis is the travel axis. A horizontal slide that
  compresses vertically is wrong (inference from the definition: deformation is in the
  direction of force).

The task statement's phrasing, "the ink bbox aspect ratio dips below 1.0 for 2-4 frames at
impact with area roughly conserved", is the same signature expressed on a bbox; prefer
`sx/sy` and ink count over min/max bbox for the reason in M4.

### (e) Parameter ranges with basis

| parameter | range | basis |
| --- | --- | --- |
| squash ratio (scaleX : scaleY) | 1.2 : 0.8 UI; this document uses 1.18 : 0.847 to hold volume exactly | LottieFiles (`[1.2, 0.8]`); volume-exact pair: computed as 1/1.18 |
| stretch ratio | 0.85 : 1.15 is the UI figure and is invisible at video travel speeds; on a fast fall use 20-50% elongation (0.80 : 1.25 to 0.67 : 1.50), volume-exact | LottieFiles (`[0.85, 1.15]`, UI micro-feedback); the video amplitude is inference from classical practice, calibrated against per-frame travel |
| impact duration | **2-4 frames**, held as a frame count across frame rates (not 30-65ms). Converting LottieFiles' 60fps frame counts by milliseconds gives 1-2 frames at 30fps, and a one-frame deformation at 30fps is a flicker, not a squash | LottieFiles frame counts; the carry-the-count rule is inference |
| recovery duration | **4-8 frames**, likewise carried as a count | LottieFiles frame counts; inference |
| on display type | scaleX <= 1.06-1.10 | inference (glyph legibility) |
| press (uniform) | scale 0.88 dramatic, 0.92 default, 0.96 subtle; never below 0.85 or above 0.98 | HF `press-release-spring` Values |
| press duration vs release | press 0.10-0.30s, release 0.40-0.90s, press shorter than release | HF `press-release-spring` |
| when to use zero | premium/luxury brands | LottieFiles; HF "Smooth beats bouncy" |

---

## 2. Anticipation

### (a) Canonical definition

"Used to prepare the audience for an action, and to make the action appear more
realistic": a small motion in the opposite direction before the main action, the golfer's
backswing, the knees bending before a jump (Twelve basic principles, Wikipedia, citing
Thomas and Johnston). Bloop Animation's summary adds the rule of proportion: faster
movement wants stronger anticipation
(https://www.bloopanimation.com/the-12-principles-of-animation/).

LottieFiles UI adaptation: duration 100-200ms, magnitude 10-20% of the main action;
button scales down 3% before expanding; card shifts 5-10px away first; skip for
micro-feedback under 150ms (`director/disney-principles.md`, section 2).

### (b) What it looks like in motion graphics

- **A pull-back before a push.** A camera wrapper eases back 2-4% before a push-in; a
  logo dips 3% before popping; a card nudges left before sliding right.
- **A wind-up on type.** A word about to slam scales down slightly, or a line that will
  exit upward first drops a few pixels.
- **A held breath.** In editing terms anticipation can be a beat of stillness: HF
  motion-principles says offsetting the first animation by 0.1-0.3s avoids the jump-cut
  feel, and manifesto's cut model preserves 1-8 blank frames between cards because "they
  are why the reference breathes". The blank gap before a card is anticipation at the
  cut level (inference: the gap functions as a wind-up).
- **Not on arrivals from off-frame.** An element that is not on screen yet cannot
  visibly wind up; anticipation applies to elements already resting on screen, to the
  camera, or to the whole group (inference).
- Cursor pieces: the cursor arrives and rests over the target "BEFORE the press starts",
  "or the press is unattributed" (HF `physics-press-reaction`). That arrival-then-rest
  is anticipation for the click.

### (c) Recipe

Two adjacent tweens on the same property; the second re-owns it with
`immediateRender: false` and starts exactly where the first ends.

```js
const D = 420;                                  // main travel, px
const ANT = 0.12 * D;                           // 12% counter-move
const T0 = f(8);
const ANT_DUR = 0.15, MOVE_DUR = 0.45;

// 1. wind-up: opposite direction, symmetrical ease so it reads as a settle, not a launch
tl.fromTo("#card", { x: 0 }, { x: -ANT, duration: ANT_DUR, ease: "power2.inOut" }, T0);
// 2. main move: from the wound-up position. NOTE the ease. power3.out starts at peak
//    velocity (peak/avg 4.0, Appendix A) while tween 1 ends at zero velocity, so chaining
//    inOut into .out puts a velocity STEP at the junction: on a 420px move the first frame
//    of tween 2 carries ~24% of the travel, about 100px, which reads as a jerk, not a
//    launch. Use an .inOut here so the action accelerates out of the wound-up pose.
tl.fromTo("#card", { x: -ANT }, { x: D, duration: MOVE_DUR, ease: "power2.inOut", immediateRender: false }, T0 + ANT_DUR);
```

**The professional form is one curve, not two tweens.** In After Effects this whole gesture
is a single keyframe pair with a graph-editor curve that dips below zero and rises. Under
the contract that is `CustomEase` with an SVG path whose y goes negative, registered once
at build time and applied to one `fromTo` over the full travel:

```js
CustomEase.create("antic", "M0,0 C0.10,-0.14 0.30,0.02 0.42,0.30 0.60,0.72 0.80,1 1,1");
tl.fromTo("#card", { x: 0 }, { x: D, duration: ANT_DUR + MOVE_DUR, ease: "antic" }, T0);
```

One tween, no junction, no velocity step, and still a pure function of progress.
(https://gsap.com/docs/v3/Eases/CustomEase/ ; free since GSAP 3.13.)

Scale anticipation for a pop (already-visible element):

```js
tl.fromTo("#badge", { scale: 1 }, { scale: 0.96, duration: 0.12, ease: "power2.inOut" }, T0);
tl.fromTo("#badge", { scale: 0.96 }, { scale: 1.12, duration: 0.18, ease: "power3.out", immediateRender: false }, T0 + 0.12);
tl.fromTo("#badge", { scale: 1.12 }, { scale: 1, duration: 0.30, ease: "power2.out", immediateRender: false }, T0 + 0.30);
```

Camera anticipation (pull back, then push):

```js
tl.fromTo("#world", { scale: 1 }, { scale: 0.97, duration: 0.2, ease: "sine.inOut" }, T0);
tl.fromTo("#world", { scale: 0.97 }, { scale: 1.35, duration: 0.7, ease: "power3.inOut", immediateRender: false }, T0 + 0.2);
```

### (d) Measurable signature on rendered frames

On the M6 step series of the element's centroid (M3) projected onto the main travel axis:

- A run of 2-6 frames at 30fps (100-200ms) where the sign of the step is **opposite** to
  the main travel, immediately followed by the main run in the positive direction.
- The **net displacement of the opposite run**, divided by the total main travel, is the
  anticipation fraction: 0.08-0.20 (task statement 8-20%; LottieFiles 10-20%).
- The opposite run is **smooth** (its own step series has a single peak, no reversal
  inside it). Whether there is a near-zero step at the wound-up extreme is
  register-dependent, not a law: a cartoon wind-up holds the pose, and a product-grade
  pull-back-then-push (camera, wordmark, the `CustomEase` form above) is one continuous
  velocity curve with no hold at all. A detector keyed on the hold fails the second, which
  is the more common one in this skill's output. Use the hold as a positive signal for a
  cartoon register and never as a required condition (inference; this corrects an earlier
  version that required the pause).
- Order matters: the reversal precedes the large steps. Overshoot (principle 5) is the
  same shape at the **end** of the move; anticipation is at the **start**. A detector
  must key on where the reversal sits relative to the frame of peak speed: before it is
  anticipation, after it is overshoot (inference; grade-original's reversal detector
  does not distinguish the two, so add the ordering test).
- Zero anticipation is the correct measurement on most entrances from off-frame and on
  micro-feedback under 150ms (LottieFiles "Skip for micro-feedback").

### (e) Parameter ranges with basis

| parameter | range | basis |
| --- | --- | --- |
| magnitude, fraction of main travel | 10-20% **for moves under about 300px**, with an absolute cap of 20-40px at 1080p (or 5-12% of the element's own dimension), whichever is smaller. Anticipation scales with the object and the force, not with the distance travelled: 12% of a 1200px cross-frame slide is a 144px counter-move, which stops being a wind-up and becomes a separate move in the opposite direction | LottieFiles for the fraction; the cap and the reductio are inference |
| magnitude, visibility floor | below about 12-15px of counter-travel a percentage rule stops working: 15% of a 34px head-turn is 5px over 4 frames, which is 1.3px per frame against HF's own "subtle reads as static at 30fps". Below that floor either scale the anticipation up disproportionately or omit it and spend the frames elsewhere | inference; HF video-composition for the "reads as static" line |
| duration | 100-200ms; 3-6 frames at 30fps | LottieFiles |
| scale dip before a pop | 3% (0.97) | LottieFiles ("Button: scale down 3%"); LottieFiles button pattern uses 0.97 over 50ms |
| card shift | 5-10px in UI; at 1080p video scale to ~1-2% of frame width | LottieFiles; scaling: inference |
| ratio of anticipation to action duration | roughly 1 : 3 **in the UI case only**. In character work the anticipation is usually the slower, longer part and the action is a few fast frames, so the ratio inverts. Do not carry 1:3 into an impact verb | inference from the 100-200ms and 300-600ms UI tables; explicitly *not* a sourced figure and not general |
| stronger for faster main actions | qualitative | Bloop Animation summary |
| skip when | main action under 150ms; the element is off-frame **and** nothing else can carry the wind-up. An off-frame element cannot visibly wind up, but the *scene* can: the container dims, the camera pulls back, or a held blank frame precedes the hit, all of which are anticipation at the beat level. Section 2(b) already says this, so "element not yet visible" is not on its own a reason to skip | LottieFiles for the 150ms; the scene-level qualification is inference and corrects an over-absolute earlier statement |
| beat-level equivalent | 1-8 blank frames between cards; first motion at 0.1-0.3s | manifesto section 3.2; HF motion-principles |

---

## 3. Staging

### (a) Canonical definition

Thomas and Johnston: "the presentation of any idea so that it is completely and
unmistakably clear", achieved through placement, lighting, camera angle, and by keeping
the audience's focus on what matters while avoiding unnecessary detail (Twelve basic
principles, Wikipedia). Bloop adds the silhouette rule and blocking as sub-concepts.

LottieFiles UI adaptation: dim non-hero elements to 40-60% opacity, optional 2-4px blur;
hero enters 100-200ms after supporting elements; one primary action per timing beat
(`director/disney-principles.md`, section 3). Choreography: "Lead with the hero", spatial
origin consistency, and the 1/3 rules (no motion travels more than 1/3 of the screen
without a keyframe; with 3+ elements, at most 1/3 active at once)
(`director/choreography.md`).

### (b) What it looks like in motion graphics

- **One thing moves at a time, or one thing moves most.** "The element that moves first
  is perceived as most important. Stagger in order of importance, not DOM order" (HF
  motion-principles, "Choreography is hierarchy"). "Time is hierarchy" (HF typography).
- **Dim and defocus the rest.** HF `depth-of-field-blur` tweens `filter: blur()` plus a
  slight opacity dim on off-focus layers while the focal element stays sharp. Manifesto's
  product-UI vocabulary: cards "enter defocused and resolve" over 10-15 frames.
- **Camera as staging.** `viewport-change`, `coordinate-target-zoom` and
  `multi-phase-camera` (HF) push the frame toward the subject; a push-in is a staging
  decision, not decoration.
- **Composition rules that are staging in disguise**: two focal points minimum, hero text
  60-80% of frame width, anchor to edges, three layers (background treatment, midground
  content, foreground accents) (HF video-composition).
- **Legibility is staging**: type must clear 3:1 contrast against its ground while it is
  settled (grade-original, "worst type/ground contrast >= 3.00:1 (large)"), and nothing
  sits inside the 4% title-safe margin (grade-original "frames with ink in the safe
  margin").

Note a real disagreement between the two local sources on order: LottieFiles says the
hero enters 100-200ms **after** its supporting elements (context first, then subject),
HF says the hero moves **first** (subject first, then context). LottieFiles is writing for
UI where the container is the context; HF is writing for video where the first mover
takes the eye. For a motion-graphics card the HF order is the safer default; use the
LottieFiles order when the supports are literally the frame the hero lands in
(inference).

### (c) Recipe

Supports establish, then dim and soften as the hero lands with the biggest displacement
and the strongest ease. The dim is a `filter` and `opacity` tween, both paint-only.

```html
<div class="stage" id="stage">
  <div class="support" id="s1">Q3 revenue</div>
  <div class="support" id="s2">vs last year</div>
  <div class="hero" id="hero">+38%</div>
</div>
<style>
  .support, .hero { will-change: transform, opacity, filter; }
</style>
```

```js
const T0 = f(6);
const S_DUR = f(12);            // 0.40s
const S_LAG = f(2);             // 0.067s between the two supports
const H_DUR = f(18);            // 0.60s

// supports settle first, small travel, gentle ease
["#s1", "#s2"].forEach((sel, i) => {
  tl.fromTo(sel, { y: 24 }, { y: 0, duration: S_DUR, ease: "power2.out" }, T0 + i * S_LAG);
  tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: f(5), ease: "power2.out" }, T0 + i * S_LAG);
});
// hero lands last, largest travel, strongest ease
tl.fromTo("#hero", { y: 120, scale: 0.9 }, { y: 0, scale: 1, duration: H_DUR, ease: "power4.out" }, T0 + f(6));
tl.fromTo("#hero", { opacity: 0 }, { opacity: 1, duration: f(7), ease: "power2.out" }, T0 + f(6));

// supports step back AFTER their own entrances have finished. The earlier version started
// this dim at T0 + 0.25 while the entrance tweens ran to T0 + 0.40 and T0 + 0.46, so for
// 150-210ms two fromTo tweens owned opacity on the same elements and, because the dim
// carries immediateRender: false, it snapped opacity to 1 mid-entrance. Under seek the
// result depended on GSAP's overwrite resolution, which is exactly the non-determinism
// the contract exists to prevent. Start it at or after the last entrance ends.
const DIM_AT = T0 + S_LAG + S_DUR;                    // = end of #s2's entrance
tl.fromTo(["#s1", "#s2"], { opacity: 1, filter: "blur(0px)" },
  { opacity: 0.55, filter: "blur(8px)", duration: f(10), ease: "sine.inOut", immediateRender: false }, DIM_AT);

// camera confirms the subject: gentle push. The offsets are MEASURED, never typed.
const stage = document.getElementById("stage").getBoundingClientRect();
const hero  = document.getElementById("hero").getBoundingClientRect();
const S = 1.06;
// Two different moves, two different formulas. Choose deliberately:
//   bring the hero TO the centre of frame:  T = -offset * S
//   HOLD the hero where it already sits:    T = -offset * (S - 1)
// offset is the hero's centre relative to the stage's centre.
const ox = (hero.left + hero.width / 2) - (stage.left + stage.width / 2);
const oy = (hero.top + hero.height / 2) - (stage.top + stage.height / 2);
const HOLD = true;                                     // this recipe holds, it does not recentre
const k = HOLD ? (S - 1) : S;
tl.fromTo("#stage", { scale: 1, x: 0, y: 0 },
  { scale: S, x: -ox * k, y: -oy * k, duration: f(36), ease: "power2.inOut" }, DIM_AT);
```

Two things the earlier version of this recipe got wrong and that are worth stating as
rules. **The counter-translate formula depends on which move you are making.**
`T = -offset x S` recentres the target; holding a point where it already sits under a
scale of `S` needs `T = -offset x (S - 1)`. Typed constants matched neither: at `S = 1.06`
an `x` of -40 implies a hero offset of 37.7px under the recentring form and 667px under
the hold form. **And the offset is measured with `getBoundingClientRect` after
`document.fonts.ready`, never typed** (HF `viewport-change`), because a hand-typed offset
is wrong the moment the copy changes length.

### (d) Measurable signature on rendered frames

- **Motion concentration.** Per frame, compute M6 step magnitude per element region, and
  the share of total motion energy belonging to the largest mover. In a staged beat one
  region carries most of the energy at any moment. The "more than 2/3 of the summed step
  magnitude across regions" figure is a **tuning parameter**, not a measured or sourced
  threshold: it is a plausible starting value and a grader should expose it as a knob.
  (Inference; LottieFiles' 1/3 active-elements rule is the design-side statement of the
  same idea, at UI scale.)
- **Active count.** Number of regions whose step exceeds the M7 significance threshold,
  per frame. **UI register only.** LottieFiles' "at most 1/3 of 3+ elements active at
  once" is an interface-transition rule about not overloading a user who has to track
  state. Video routinely violates it: a six-item stagger over 0.3s has all six active, a
  logo lockup resolves as one unit, and a grid landing together on the downbeat is the
  point of cutting to music. What is actually a defect is *unmotivated* simultaneity, so
  count elements inside one declared group or lockup as one element and exempt same-frame
  starts that land on a declared audio hit. Report the raw share; grade only the
  undeclared case (LottieFiles for the rule; the scoping is inference).
- **Dim ratio.** Mean luma contrast of non-hero regions relative to the hero region
  during the hero's settled window (M10). Staged beats show the supports at 40-60% of
  their own pre-dim contrast, or a measurable M8 sharpness drop (2-4px blur at UI scale)
  (LottieFiles). If everything is equally sharp and equally bright the beat has no
  staging.
- **Displacement hierarchy.** The hero's total travel is the largest, and its ease fit is
  the most front-loaded (highest peak/avg velocity, see Appendix A). If the supports
  travel further or faster than the hero, the hierarchy is inverted (LottieFiles "Hero
  gets largest displacement").
- **Order.** The hero's first significant step is either first (HF) or 100-200ms after
  the supports (LottieFiles); either is staged. A hero that starts mid-pack is not.
- **Position and legibility** (grade-original): worst settled contrast >= 3:1, no ink in
  the 4% edge margin except named full-bleed gestures, vertical centroid spread across
  the film >= 0.09 (sd of normalized cy) and no more than 85% of frames with the
  centroid in the middle third.

### (e) Parameter ranges with basis

| parameter | range | basis |
| --- | --- | --- |
| non-hero dim | 40-60% opacity | LottieFiles |
| non-hero blur | 2-4px UI; for 1080p video 3-6px per depth step with a cap of 8 soft / 16 default / 24 heavy, and lean on the opacity dim to do the push-back work | LottieFiles for the UI figure; the video figures are HF `rules/depth-of-field-blur.md` `BLUR_PER_DEPTH` and `MAX_BLUR`, which is the applicable rule. (The earlier citation to HF transitions "Blur Intensity by Energy" was wrong: that table governs blur-through *cuts*, not dimming supports behind a hero.) |
| hero delay after supports (UI) | 100-200ms | LottieFiles |
| hero first, supports overlapping | stagger sequence < 500ms total | HF motion-principles |
| active elements | at most 1/3 of 3+ elements at once | LottieFiles choreography |
| max unbroken travel | 1/3 of screen | LottieFiles choreography |
| hero text width | 60-80% of frame width | HF video-composition |
| settled contrast | >= 3:1 for display type | grade-original |
| safe margin | 4% of frame on every edge | grade-original |
| camera push | scale 1.04-1.06 ambient; a push-through is a `viewport-change` (single wrapper) or `coordinate-target-zoom` (nested) move with its own counter-translate, sized from the measured target, not from a fixed multiplier | HF motion-principles (Ken Burns 1 to 1.04); HF `viewport-change` / `coordinate-target-zoom`. (The earlier "1.3-2.5 for a push-through" cited `motion-blur-streak` `SCALE_FROM`, which is an element's entrance scale and not a camera parameter at all.) |
| a real push versus a zoom | CSS `perspective` **is** the focal length and `translateZ` is the dolly: animate `translateZ` with `perspective` fixed for a true push (per-layer parallax falls out for free), animate `perspective` with `translateZ` fixed for a zoom, and animate both in opposition for a dolly zoom. Scale on a wrapper is a third thing, a crop-and-blow-up, and is what most "push" recipes actually produce | CSS 3D transform specification (the `perspective` value is the viewer distance to the z=0 plane); inference for the consequence |

---

## 4. Straight-ahead action and pose-to-pose

### (a) Canonical definition

Two working methods. Straight-ahead: draw frame by frame from the start; fluid, dynamic,
good for unpredictable action, hard to keep proportions and timing under control.
Pose-to-pose: draw the key poses first, then fill the in-betweens; better control of
timing and composition, better for dramatic and emotional scenes. Wikipedia notes that
computers can fill the in-betweens automatically while keeping the advantages of
pose-to-pose (Twelve basic principles, Wikipedia). Bloop's sub-concepts: key poses,
breakdowns, in-betweens.

LottieFiles UI adaptation: straight-ahead for particles, ambient, generative art;
pose-to-pose for UI transitions and state changes (`director/disney-principles.md`,
section 4).

### (b) What it looks like in motion graphics

Under the HyperFrames contract this principle becomes a question of **who computes the
in-betweens**:

- **Pose-to-pose is every `fromTo`.** The from and to states are the key poses, the ease
  is the in-between rule. The whole timeline is a pose sheet with timestamps; manifesto's
  beat map (`startFrame | t | card | gapBefore | mechanic | fitted ease`) is literally a
  pose-to-pose exposure sheet.
- **Straight-ahead is a driver with `onUpdate`.** A proxy tween with `ease: "none"` and
  an `onUpdate` that computes every element's state as a pure function of time:
  `particle-burst` ("one `ease: 'none'` driver whose onUpdate computes each particle as a
  pure ballistic function of time, scrub-safe mid-flight"), the Canvas 2D and shader
  patterns in HF techniques, `reactive-displacement` (one driver feeds three motions),
  `sine-wave-loop`'s `tl.time()` form. The determinism rule makes this straight-ahead in
  look but pose-to-pose in nature: because state must be a pure function of time, there
  is no accumulating simulation. HF says so explicitly about springs: "an interactive
  spring is a stateful integrator ... which cannot be seeked deterministically"
  (`hyperframes-animation/adapters/gsap-easing-and-stagger.md`, Spring Eases).
- **Hybrid** is the norm: pose-to-pose for the hero and type, straight-ahead drivers
  for ambient fields, particles and procedural backgrounds.

The straight-ahead failure mode in film (drifting proportions, losing the timing) shows
up here as drivers whose duration is not tied to the beat, so the ambient layer never
resolves with the content. Cap every driver to its beat and give it a rest state.

### (c) Recipe

Pose-to-pose with labels (the timeline is the exposure sheet):

```js
tl.addLabel("pose-a", f(6));
tl.addLabel("pose-b", f(24));
tl.addLabel("pose-c", f(42));
tl.fromTo("#card", { x: -300, rotation: -6, opacity: 0 }, { x: 0, rotation: 0, opacity: 1, duration: 0.5, ease: "power3.out" }, "pose-a");
tl.fromTo("#card", { x: 0, rotation: 0 }, { x: 180, rotation: 2, duration: 0.45, ease: "power2.inOut", immediateRender: false }, "pose-b");
tl.fromTo("#card", { x: 180, rotation: 2 }, { x: 180, rotation: 0, scale: 1.04, duration: 0.4, ease: "power2.out", immediateRender: false }, "pose-c");
```

Straight-ahead driver, deterministic, seek-safe: an ambient field of N dots, each a pure
function of `t` and its index. No state, no `Math.random`.

```js
const dots = gsap.utils.toArray(".dot");           // N elements, positioned by CSS
function hash(i, k) {                              // index-seeded pseudo-random in [0,1)
  let n = (i * 374761393 + k * 668265263) | 0;
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  return ((n ^ (n >>> 16)) >>> 0) / 4294967296;
}
const BEAT = 6.0;
const drive = { t: 0 };
function writeField() {
  const t = drive.t;
  dots.forEach((el, i) => {
    const ax = 18 + 22 * hash(i, 1), ay = 12 + 20 * hash(i, 2);
    const wx = 0.35 + 0.4 * hash(i, 3), wy = 0.3 + 0.5 * hash(i, 4);
    const px = 6.283 * hash(i, 5), py = 6.283 * hash(i, 6);
    const env = t < BEAT * 0.8 ? 1 : 1 - (t - BEAT * 0.8) / (BEAT * 0.2);
    gsap.set(el, { x: env * ax * Math.sin(wx * t + px), y: env * ay * Math.sin(wy * t + py) });
  });
}
writeField();   // SEED FRAME 0. Without this the field shows its unstyled CSS position on
                // frame 0 and through any pre-roll, so the render's first frames differ
                // from the preview's. Sections 10(c) and 11(c) already seed their drivers;
                // this one did not.
tl.fromTo(drive, { t: 0 }, {
  t: BEAT, duration: BEAT, ease: "none", onUpdate: writeField,
}, f(6));
// Past about 30 elements, N gsap.set calls per frame is the slow path: write the transform
// strings directly, or move the field to a canvas, which is what the HF canvas pattern is
// for. (Inference; HF techniques Canvas 2D.)
```

The `hash` is the HF techniques Canvas 2D pattern ("The hash() function is deterministic,
same frame renders identically every time"). `gsap.set` inside `onUpdate` is fine because
the set is recomputed on every seek from `drive.t` alone.

### (d) Measurable signature on rendered frames

- **Pose-to-pose** elements show piecewise motion on M6: runs of significant steps
  separated by rests (near-zero steps for several frames), and within each run the step
  profile fits a single ease family with low RMSE (manifesto `segment.mjs` fits "a
  least-squares best-fit GSAP ease for every monotonic motion it finds, with runners-up
  and RMSE"). The rests are the poses.
- **Straight-ahead** elements show continuous, non-repeating motion with no rests for the
  whole beat and a poor single-ease fit (high RMSE, no dominant family). Multiple such
  elements show low pairwise correlation of their step series (they are independent
  functions of index).
- **Scrub safety** (a straight-ahead driver that is actually a stateful integrator):
  render the same frame by seeking directly and by seeking through the frames before it;
  a pure function gives identical pixels, an integrator does not. Manifesto's
  render-order trap is the same class of bug detected the same way (grade against the
  render, not the preview).
- **Rest at beat end**: the ambient layer's step series goes to zero before the cut
  (inference; a driver that is still moving on the cut frame is straight-ahead action
  that lost its timing).

### (e) Parameter ranges with basis

| parameter | range | basis |
| --- | --- | --- |
| pose count per beat | 2-4 key states per hero element (entrance, optional reposition, hold, exit or cut) | inference from HF "build / breathe / resolve" (motion-principles) |
| driver elements | <= ~40 particles per burst | HF `particle-burst` |
| animated elements per viewport | < 20 | LottieFiles quality-checklist |
| ambient amplitude | 10-20% of element size, slow | LottieFiles troubleshooting ("Ambient too prominent: 10-20% amplitude, slower") |
| ambient period | 2-20s | LottieFiles duration table ("Ambient 2000-20000ms") |
| audio-reactive amplitude on text/logo | <= 5% scale, <= 30% glow | HF techniques section 11 |

---

## 5. Follow-through and overlapping action

### (a) Canonical definition

Follow-through: loosely attached parts keep moving after the body stops, then are pulled
back toward the center of mass, possibly oscillating. Overlapping action: parts of the
body move at different rates. "Drag": a part takes a few frames to catch up when
movement starts. The related "moving hold": even a still character keeps a little motion
(breathing) because a frozen drawing reads as dead (Twelve basic principles, Wikipedia,
citing Thomas and Johnston).

LottieFiles UI adaptation: child delay 50-150ms behind parent; trailing elements' stop
times offset by 100-200ms; spring easing on trailing parts, lower stiffness for more
trail (`director/disney-principles.md`, section 5). Overshoot budget: success 5-10%,
error 0%, feedback 2-5%, celebration 15-25%, premium 0% (`reference/timing-easing-tables.md`).

### (b) What it looks like in motion graphics

- **A card lands, its contents land a beat later.** Image first, then title, then
  description, "at slight delays" (Interaction Design Foundation article, principle 5).
  The After Effects habit manifesto records: "Offset sibling groups by ~3 frames. Not per
  element, per group. It is what stops a UI assembling like a spreadsheet."
- **Overshoot is the settle.** In UI motion elements commonly overshoot slightly on
  arrival and then settle (a claim previously attributed to a Made Good Designs search
  summary; the page was never read, so treat this as a general observation with no
  citation). HF makes it a register, not a default:
  "Bouncy `back.out` is the #1 instant turn-off in agent-made videos" and the house
  settle is `power3.out` or a critically damped spring with no overshoot
  (`spring-pop-entrance`, `gsap-easing-and-stagger`). When overshoot is used, it goes on
  transforms only, never opacity (Spring Eases craft notes).
- **Drag on type**: a per-character cascade where each unit is still in motion while the
  next starts, the Apple cascade with `R` about 0.7 (manifesto), or `waterfall-entry`
  where "next element starts within +/-2 frames of the previous settling".
- **Trailing shadow**: LottieFiles' card pattern says "shadow arrives 50ms after card",
  and that describes the shadow **growing in**, not travelling separately. What lags in a
  professional shadow is the *spread* (blur radius, scale, opacity); the position does
  not, because a drop shadow is attached to its caster and cannot lag in position without
  the card visibly floating off its own shadow. Section 11's own "one implied light" rule
  forbids the positional lag (LottieFiles for the timing; the spread-not-position
  distinction is inference and corrects an earlier misreading of the source).
- **Moving hold**: HF's "breathe" phase, ONE ambient motion on held content
  (motion-principles, "Breathe (30-70%)"), `sine-wave-loop`. Grade-original's duplicate
  frame check ("a hold rendered as bit-identical frames reads as a stall") is the moving
  hold enforced as a rule.
- **Impact aftermath**: `reactive-displacement`'s "wobble after settle", a damped sine
  rotation decaying linearly over `WOBBLE_DUR`.

### (c) Recipe

A card lands on `power3.out`; its children start 3, 6 and 9 frames later on the same axis;
a light tag at the end of the chain is the only element allowed a physical overshoot,
using the baked spring (seek-safe closed form) from HF.

```js
// springEase from hyperframes-animation/adapters/gsap-easing-and-stagger.md
function springEase({ response = 0.5, dampingFraction = 1 } = {}) {
  const w = (2 * Math.PI) / response, z = dampingFraction;
  let pos;
  if (z < 1) { const wd = w * Math.sqrt(1 - z * z);
    pos = (t) => 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + ((z * w) / wd) * Math.sin(wd * t)); }
  else if (z > 1) { const wo = w * Math.sqrt(z * z - 1);
    pos = (t) => 1 - Math.exp(-z * w * t) * (Math.cosh(wo * t) + ((z * w) / wo) * Math.sinh(wo * t)); }
  else { pos = (t) => 1 - Math.exp(-w * t) * (1 + w * t); }
  const EPS = 0.001, rate = z <= 1 ? z * w : (z - Math.sqrt(z * z - 1)) * w, SCAN = 12 / rate, N = 4800;
  let T = SCAN;
  for (let i = N; i >= 0; i--) { const t = (i / N) * SCAN; if (Math.abs(1 - pos(t)) > EPS) { T = ((i + 1) / N) * SCAN; break; } }
  const xT = pos(T);
  return { duration: T, ease: (p) => pos(p * T) + p * (1 - xT) };
}

const T0 = f(8);
const LAG = f(3);                                   // ~3 frames per sibling group

// parent: the body of the move
tl.fromTo("#card", { y: 140, opacity: 0 }, { y: 0, opacity: 1, duration: 0.55, ease: "power3.out" }, T0);

// children drag behind, same direction, shorter travel, later start, same ease family
[["#card-img", 0], ["#card-title", 1], ["#card-body", 2]].forEach(([sel, k]) => {
  tl.fromTo(sel, { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "power3.out" }, T0 + (k + 1) * LAG);
});

// the loose part: a small tag that overshoots physically (zeta 0.7 -> ~4.6% overshoot)
const tag = springEase({ response: 0.45, dampingFraction: 0.7 });
tl.fromTo("#card-tag", { y: 60 }, { y: 0, duration: tag.duration, ease: tag.ease }, T0 + 4 * LAG);
tl.fromTo("#card-tag", { opacity: 0 }, { opacity: 1, duration: 0.2, ease: "power2.out" }, T0 + 4 * LAG); // opacity on its own monotone tween

// moving hold: one ambient breath on the card while it is read (finite repeats)
tl.fromTo("#card", { scale: 1 }, { scale: 1.012, duration: 1.4, ease: "sine.inOut", yoyo: true, repeat: 3, immediateRender: false }, T0 + 0.9);
```

If a `back.out` is wanted instead of the spring: `back.out(1.2)` is 5.3% overshoot,
`back.out(1.7)` is 10% (computed, Appendix A); HF caps it at about 2 (13% overshoot).

### (d) Measurable signature on rendered frames

- **Lag**: the frame of first significant step (M7) for each child region minus the
  parent's. Follow-through shows 1-5 frames at 30fps (50-150ms) per link, monotonically
  increasing down the chain (LottieFiles child delay). The cross-correlation of parent and
  child step series peaks at a positive lag of the same size (inference).
- **Stop-time offset**: the frame where each region's step falls below significance;
  trailing parts stop 3-6 frames at 30fps (100-200ms) after the parent (LottieFiles).
- **Overshoot = exactly one direction reversal at the settle.** On a region's M6 series
  along the travel axis, after segmenting on re-triggers and smoothing (M7): count sign
  changes among significant steps. Zero reversals is the HF house settle (and the law
  grade-original enforces: "settle direction reversals" must be 0). Exactly one reversal,
  located after the frame of peak speed, is a single overshoot (task statement). Two or
  more reversals is elastic or under-damped wobble.
  Magnitude: the overshoot distance past rest divided by total travel, 2-10% for the
  registers HF permits, 15-25% only for celebration (LottieFiles overshoot budget;
  HF spring table).
  Timing: for `back.out(s)` the reversal sits at 47-67% of the tween's duration depending
  on `s` (58% for 1.7), so the return from overshoot occupies the last third to half of
  the tween (computed, Appendix A).
  Second reversal visibility: for a spring, each successive excursion is the previous one
  multiplied by the overshoot ratio, so at zeta 0.6 (9.5%) the second excursion is 0.9%,
  below the 2% significance floor and invisible; at zeta 0.5 (16.3%) the second is 2.7%
  and shows as a second reversal (computed from the standard second-order step
  response; the 2% floor is grade-original's).
- **Moving hold**: M9 duplicate frames = 0 through a held beat; M2 ink count or M4 second
  moments show a low-amplitude periodic variation (1-2% for a breathe: HF motion-principles
  Ken Burns 1 to 1.04, LottieFiles ambient 10-20% of element for decorative elements,
  <= 5% on text per HF techniques audio-reactive note).
- **Overshoot on the wrong property**: opacity that exceeds 1 clamps, which shows on M2
  as a plateau reached early followed by no change, while transforms are still moving;
  a glow that pulses past its peak and back. The rule is "overshooting curves go on
  transforms only, never on opacity or color" (HF Spring Eases craft notes).

### (e) Parameter ranges with basis

| parameter | range | basis |
| --- | --- | --- |
| child lag behind parent | 50-150ms (1.5-4.5 frames at 30fps, 3-9 at 60fps) | LottieFiles |
| per sibling group offset | ~3 frames | manifesto (AE liquid-glass build habit) |
| trailing stop offset | 100-200ms | LottieFiles |
| cascade overlap | next unit starts within +/-2 frames of previous settling; gaps shrink | HF `waterfall-entry` |
| Apple cascade ratio | stagger-spread : per-unit duration = 1 : R, R about 0.7 measured | manifesto "Translating the Range Selector to GSAP" |
| overshoot, **by register** (one row, three cases: read this instead of the pair of contradictory rows that used to sit here) | premium and product: 0-2%, at most one reversal. Editorial and brand: at most one reversal of 1-5%. Celebration only: 15-25% | HF `spring-pop-entrance` and grade-original's zero-reversal law for the product case; LottieFiles material table (paper 3-5%, feedback 2-5%) for the editorial case; LottieFiles for celebration. The premium 0-2% rather than a flat 0 is because LottieFiles' own "Apple Spring: stiffness 300, damping 20" is zeta 0.577, whose first overshoot is about 11% (computed), so even the cited premium reference is near-critically damped rather than zero-overshoot |
| overshoot, house default | 0% (`power3.out` or spring zeta 1.0) | HF `spring-pop-entrance`, `gsap-easing-and-stagger` |
| overshoot, "alive not bouncy" | ~1-1.5% (zeta 0.80-0.85) | HF Spring Eases table; computed 1.5% at 0.80, 0.6% at 0.85 |
| overshoot, explicitly playful | ~5-10% (zeta 0.60-0.70); `back.out(1.2-1.7)` = 5.3-10% | HF Spring Eases table; computed |
| overshoot, do not | > 12% (zeta < 0.55); `back.out` > 2 (> 13%) | HF Spring Eases table; HF `spring-pop-entrance` ("keep OVERSHOOT <= ~2") |
| overshoot by context (UI) | success 5-10%, feedback 2-5%, celebration 15-25%, error 0%, premium 0% | LottieFiles timing-easing-tables |
| press release bounce factor | 1.4 soft, 2.0 firm, 2.8 cartoony (7.1%, 13.2%, 22.5%) | HF `press-release-spring`; overshoot %: computed |
| spring response (period) | 0.25-0.35 tight, 0.35-0.50 standard, 0.50-0.70 weighted hero | HF Spring Eases table |
| moving hold amplitude | scale 1.00 to 1.04 over the beat (Ken Burns); text <= 5% | HF motion-principles; HF techniques |
| wobble after settle | +/- WOBBLE_AMP_DEG rotation, linear decay | HF `reactive-displacement` |

---

## 6. Slow in and slow out

### (a) Canonical definition

More drawings near the beginning and end of an action, fewer in the middle, so the
object accelerates out of a pose and decelerates into the next; this emphasizes the
extreme poses (Twelve basic principles, Wikipedia). Bloop's sub-concepts: "spacing" (the
change between frames) as distinct from "timing" (the number of frames), the easing
graph, the spline curve.

LottieFiles UI adaptation: entrance ease-out, exit ease-in, on-screen ease-in-out,
ambient loop sine ease-in-out; "NEVER linear for spatial movement", linear only for
rotation, progress bars, timers (`director/disney-principles.md`, section 6; the same
rules in `reference/timing-easing-tables.md`).

### (b) What it looks like in motion graphics

- **Ease-out on every arrival, ease-in on every departure, inOut between positions.**
  "You get this backwards constantly. Ease-in for entrances feels sluggish. Ease-out for
  exits feels reluctant" (HF motion-principles, "Direction rules").
- **The house curve is `power3.out`**, `power2` for gentle secondary motion, `power4` or
  `expo` for punch, `sine` for ambient (HF `gsap-easing-and-stagger`).
- **The ease is the character.** "A slide-in with `expo.out` = confident. With
  `sine.inOut` = dreamy. With `elastic.out` = playful" (HF motion-principles). Manifesto:
  "the ease is the whole character of the move", fit it from the reference with
  `segment.mjs` rather than guess.
- **Velocity-matched cuts**: exit on `power2.in` or `power3.in` with a blur ramp, enter on
  `.out` with the blur clearing; "The fastest point of both curves meets at the cut";
  match exit and entry velocity within ~5% (HF beat-direction, HF techniques section 10).
- **Slow-fast-slow group slides** are not a single ease: `nudge-curve` chains
  `power3.in` (10% distance, 20% time), linear (65%, 18%), `power4.out` (25%, 62%), with
  the tail at least 3x the ramp-in in time (HF).
- **Linear is deliberate**: camera moves with timed counterpoint, mechanical motion,
  rotation, progress (HF `gsap-easing-and-stagger`; LottieFiles).

### (c) Recipe

```js
const T0 = f(6);
// arrival: decelerating
tl.fromTo("#line1", { x: -220, opacity: 0 }, { x: 0, opacity: 1, duration: 0.5, ease: "power3.out" }, T0);
// reposition on screen: symmetric
tl.fromTo("#line1", { x: 0 }, { x: -160, duration: 0.45, ease: "power2.inOut", immediateRender: false }, T0 + 1.6);
// departure on the final scene only: accelerating, shorter than the arrival
tl.fromTo("#line1", { x: -160, opacity: 1 }, { x: -520, opacity: 0, duration: 0.32, ease: "power3.in", immediateRender: false }, T0 + 3.2);

// Handoff between two scene wrappers. The version that used to sit here started a
// power3.in exit and a power3.out entry at the same time T and claimed "the fastest point
// of both curves meets at the cut". It does not: #s1 is fastest at T + 0.5 and #s2 is
// fastest at T, half a second apart, so the two planes visibly drift apart mid-move.
// There are exactly two correct forms.

// FORM A -- the push (one plane). Both scenes share one ease and one duration and move as
// one surface, so the velocity match is true by construction. This is the default.
const T = f(120);
tl.fromTo("#s1", { yPercent: 0 },   { yPercent: -100, duration: f(15), ease: "power2.inOut" }, T);
tl.fromTo("#s2", { yPercent: 100 }, { yPercent: 0,    duration: f(15), ease: "power2.inOut" }, T);

// FORM B -- the cut with matched velocity. The exit ENDS at the cut and the entry STARTS
// at it, and the durations are solved so the end velocity of the .in equals the start
// velocity of the .out: (n+1) D_exit / T_exit = (m+1) D_entry / T_entry for power(n).in
// and power(m).out. For equal distances and the same exponent both sides, that means
// EQUAL durations -- not the 0.33 vs 1.0 that HF's own quick-pick uses, which misses its
// own stated ~5% tolerance by 3:1.
const CUT = f(150), D = 150, DUR = f(10);
tl.fromTo("#s1", { y: 0 }, { y: -D, duration: DUR, ease: "power2.in" }, CUT - DUR);
tl.fromTo("#s2", { y: D }, { y: 0,  duration: DUR, ease: "power2.out" }, CUT);

// slow-fast-slow group slide (nudge-curve): 270px total, time ratios 20/18/62.
// WARNING: the three-tween form has velocity steps at both joins. In normalized units the
// ramp-in ends at 4 * 0.10 / 0.20 = 2.0, the linear burst runs at 0.65 / 0.18 = 3.6, and
// the tail starts at 5 * 0.25 / 0.62 = 2.0, so the burst is 1.8x the phases either side of
// it (1000, then 1800, then 857 px/s on the 270px version). Section 12(d)'s own no-jerk
// detector would flag it. Prefer one CustomEase drawn to the same 10/65/25 spacing with
// continuous velocity; keep the chain only if you solve the phases for matching end
// velocities, which forces a different time split than 20/18/62.
const N0 = T0 + f(72);
CustomEase.create("nudge", "M0,0 C0.09,0.02 0.14,0.10 0.20,0.10 0.30,0.55 0.38,0.75 0.48,0.79 0.70,0.96 0.85,1 1,1");
tl.fromTo(".row", { x: 0 }, { x: -270, duration: f(17), ease: "nudge" }, N0);

// linear where linear is right: a progress ring and a continuous rotation
tl.fromTo("#ring", { strokeDashoffset: RING_LEN }, { strokeDashoffset: 0, duration: 2.0, ease: "none" }, T0);
tl.fromTo("#spinner", { rotation: 0 }, { rotation: 720, duration: 4.0, ease: "none" }, T0);
```

### (d) Measurable signature on rendered frames

On the M6 step series of an element's centroid along its travel axis, over one motion
segment:

- **Linear** (the defect): steps of constant magnitude, coefficient of variation of the
  step series near 0, and a hard stop (the last significant step is as large as the
  first). Detect: `std(steps) / mean(steps) < 0.15` over a run of 6+ frames (threshold:
  inference; flat step series: computed, Appendix A shows linear at 6.7px every frame for
  a 100px, 15-frame tween).
- **Ease-out** (arrival): the largest step is the first or second frame of the run, steps
  decay monotonically, the last several steps are below 1% of the travel. The
  front-loading distinguishes families: fraction of travel completed at 25% of the
  duration is 44% for `power1.out`, 58% for `power2.out`, 68% for `power3.out`, 76% for
  `power4.out`, 82% for `expo.out` (computed). Peak step divided by mean step is 2.0,
  3.0, 4.0, 5.0 and 6.9 for the same families (computed). `segment.mjs` returns the
  best-fit family and RMSE directly.
- **Ease-in** (departure): the mirror, largest step last, and the element leaves the
  frame or reaches full transparency on its fastest frame.
- **inOut** (reposition): steps small at both ends, peak in the middle, symmetric.
- **Wrong direction** (the common defect): an entrance whose peak step is at the end
  (ease-in on an arrival) or an exit whose peak step is at the start.
- **Velocity match at a cut**: the outgoing and incoming steps have the same sign and
  neither side is below about 30% of its own peak speed on the cut frame. The "~5% of each
  other" figure that used to sit here is HF's stated tolerance and is not met by HF's own
  worked example (3:1 out), so it is not a usable gate (HF beat-direction for the claim;
  the replacement is inference).
- **Slow-fast-slow**: three distinct regimes in the step series: a short rising ramp, a
  plateau at about 2x the average step, a long decaying tail whose length is at least 3x
  the ramp (HF `nudge-curve`).
- **Layout snapping** masquerading as easing: a slow tail whose steps are exactly 0, 0,
  1, 0, 0, 1 px is a `left`/`top`/`fontSize`/`letterSpacing` tween snapping to whole
  pixels, not an ease (HF `gsap-transforms-and-perf`, "holds the same pixel for several
  frames, then jumps a whole one"). Transforms give sub-pixel steps.

### (e) Parameter ranges with basis

| parameter | range | basis |
| --- | --- | --- |
| entrance ease | `.out` family; `power3.out` house default; `expo.out` punchier | LottieFiles; HF `gsap-easing-and-stagger` |
| exit ease | `.in` family, `power2.in` / `power3.in` | LottieFiles; HF beat-direction |
| between positions | `.inOut` | LottieFiles; HF motion-principles |
| ambient loop | `sine.inOut`, yoyo, finite repeats | LottieFiles; HF `sine-wave-loop` |
| linear allowed for | rotation, progress, timers, camera counterpoint, mechanical | LottieFiles; HF |
| distinct eases per scene | at least 3 characters; no more than 2 independent tweens sharing one ease per scene | HF techniques ("at least 3 different easings"); HF motion-principles |
| MD3 tokens | standard (0.2, 0, 0, 1); decelerate (0, 0, 0, 1); accelerate (0.3, 0, 1, 1); emphasized-decelerate (0.05, 0.7, 0.1, 1); emphasized-accelerate (0.3, 0, 0.8, 0.15) | **Second-hand citation.** Material Design 3 easing tokens as mirrored at https://www.mdui.org/en/docs/2/styles/design-tokens; the m3.material.io token page did not fetch, so the primary source is unverified. The values are standard and LottieFiles' timing tables list the same ones, which is corroboration but not verification |
| ~~Apple HIG default~~ CSS `ease` keyword | (0.25, 0.1, 0.25, 1) | This is the CSS specification's `ease` keyword, not an Apple motion token. It reached the LottieFiles table under an Apple label and this document repeated the attribution; Apple's own motion page did not fetch and nothing verifies the association. Relabelled, and it should not be cited as a platform default |
| velocity match tolerance at a cut | HF *states* ~5%; treat that as aspirational, not demonstrated. HF's own velocity-matched quick-pick (exit `y:-150` over 0.33s `power2.in`, entry `y:150->0` over 1.0s `power2.out`) computes to 909 px/s against 300 px/s, a 3:1 mismatch. What is actually perceived as continuous is that the direction matches and neither side has stopped: same sign of travel, and both sides above about 30% of their own peak speed on the cut frame | HF beat-direction for the 5% claim; the arithmetic and the replacement criterion are computed and inference respectively |
| nudge curve | 10/65/25 distance, ~20/18/62 time, tail >= 3x ramp-in | HF `nudge-curve` |

---

## 7. Arcs

### (a) Canonical definition

Most natural action follows an arched trajectory, and animation should follow implied
arcs for realism. Mechanical movement is the exception and typically moves in straight
lines. As speed increases the arc flattens (Twelve basic principles, Wikipedia). Bloop:
"Living things do not move in straight lines but in curved motions."

LottieFiles UI adaptation: add a 10-20px perpendicular offset at the path midpoint;
subtle (5px) for corporate, pronounced (20px+) for playful; mechanical UIs can use
straight paths intentionally (`director/disney-principles.md`, section 7). Emotion map:
joy = curved upward, calm = gentle curves, urgency = straight lines, elegance = long arcs
(`SKILL.md`, Emotion-to-Motion Map). "Path as language: Angular = tense. Curved =
friendly. Spiral = whimsical."

### (b) What it looks like in motion graphics

- **A card that enters on a slight curve** rather than a rail: LottieFiles' card
  entrance, "Path: slight curve (10px X offset at midpoint)". At 1080p this is a small
  cross-axis component on the entrance, or a slight rotation that settles to 0 (which
  makes the corners trace arcs even if the centroid does not).
- **Rotation settles** are arcs by construction: `reactive-displacement`'s intruder
  "enters tilted, settles flat"; `spring-pop-entrance`'s playful variant settles
  `rotation: ROT_FROM -> 0`; per-letter `y_i`/`rot_i` on "letter wave on an arc"
  (manifesto technique map).
- **Orbits and paths**: `orbit-3d-entry`, `avatar-cloud-network` (elliptical ring),
  MotionPathPlugin (HF techniques section 9, a cubic path for a slider or particle),
  `ai-tracking-box` (target follows a sine arc).
- **Thrown objects**: `particle-burst` computes ballistic parabolas per particle.
- **Straight is a choice**: type usually travels straight (a mask reveal rises on a
  line, a push slide is a line) and it reads as editorial precision, "Mechanical /
  precise: TYPES ON, CLICKS, LOCKS IN, SNAPS, STEPS" (HF beat-direction verbs). Do not
  bend a slam.

### (c) Recipe

Three ways to get an arc without a plugin. (a) Different eases on `x` and `y` over the same
window: the path is curved because the two axes cover their distance at different rates.
(b) A cross-axis "lift" tween on the child while the parent travels straight. (c) Rotation
about an offset origin.

```js
const T0 = f(6);

// (a) x and y on different eases -> curved path (concave toward the slower axis).
// The first tween carries ONLY x and opacity. The version that used to sit here animated
// x, y and opacity in tween 1 and then re-owned y in tween 2, so two concurrent fromTo
// tweens owned y on the same element and the result depended on GSAP's overwrite
// resolution on first render. That is the exact thing section 0.2 quotes as load-bearing
// ("Never overlap conflicting transform tweens on the same element"). Split cleanly and
// the aliases really are independent.
tl.fromTo("#chip", { x: -420 }, { x: 0, duration: f(18), ease: "power3.out" }, T0);
tl.fromTo("#chip", { y: 160 },  { y: 0, duration: f(18), ease: "power2.out" }, T0);
tl.fromTo("#chip", { opacity: 0 }, { opacity: 1, duration: f(7), ease: "power2.out" }, T0);
// Note the cross-axis ease: power3.out on x with sine.inOut on y produces a path that
// starts nearly horizontal and hooks upward at the end, which reads as a swoop into place
// rather than an arc. For a settle, spend the cross-axis motion early: both axes .out
// with different exponents. (Inference.)

// (b) parent goes straight, child lifts and lands: a symmetric bump perpendicular to travel
tl.fromTo("#card", { x: -480 }, { x: 0, duration: 0.55, ease: "power3.out" }, T0);
tl.fromTo("#card-inner", { y: 0 }, { y: -34, duration: 0.22, ease: "power2.out" }, T0);
tl.fromTo("#card-inner", { y: -34 }, { y: 0, duration: 0.33, ease: "power2.in", immediateRender: false }, T0 + 0.22);

// (c) rotation about an offset origin: an element swings in on a true arc
// CSS: #pendant { transform-origin: 50% -600px; }
tl.fromTo("#pendant", { rotation: -14, opacity: 0 }, { rotation: 0, opacity: 1, duration: 0.7, ease: "power3.out" }, T0);

// rotation settle so corners trace arcs even on a straight centroid path
tl.fromTo("#poster", { x: 380, rotation: 5 }, { x: 0, rotation: 0, duration: 0.6, ease: "power3.out" }, T0);
```

Recipe (a) puts three tweens on `#chip` at the same time, one per property. That is safe
because `x`, `y` and `opacity` are separate aliases (HF `gsap-transforms-and-perf`:
aliases "prevent accidental overwrites between separate tweens on the same element") and
**no two of them name the same property**. The safety comes from the disjointness, not
from `immediateRender: false`; two tweens that both write `y` are a bug however they are
flagged. If in doubt, use the parent/child form (b).

### (d) Measurable signature on rendered frames

- Take the M3 centroid path `(cx[t], cy[t])` over the motion segment. Fit the chord from
  first to last significant frame. The **maximum perpendicular distance** from any point
  on the path to the chord, divided by the chord length, is the arc ratio. A straight rail
  gives ~0 (below 1% after M7 smoothing); an arc gives roughly 3-15%. **These ratio bounds are tuning parameters, not measured
  thresholds** (LottieFiles' 10-20px on a UI-scale travel of 100-300px is 3-20%; the
  narrowing to 3-15% is inference). Note also that the corporate end of the band is not
  measurable at low decode resolutions: a 0.4% residual is 4.3px on a 1080 frame and
  1.4px at a 640x360 decode, inside centroid noise from antialiasing.
- **Curvature sign** is consistent along the path (one bow, not a wobble). A path whose
  perpendicular deviation changes sign is a wiggle or an overshoot in the cross axis, not
  an arc (inference).
- **Rotation arcs**: the element's principal axis angle (from the M4 second-moment
  covariance) changes monotonically and settles to its rest angle on the same frame the
  centroid settles.
- **Straight by design**: type entrances measured by `track.mjs` with "top and bottom
  rise together" and a constant left/right edge are straight translations, which is the
  expected reading for kinetic type; an arc detector should not flag them.
- Arc flattening with speed: on a fast move the arc ratio is lower than on a slow move
  of the same element (Thomas and Johnston via Wikipedia); a detector can only use this
  comparatively.

### (e) Parameter ranges with basis

| parameter | range | basis |
| --- | --- | --- |
| midpoint perpendicular offset | express as a **fraction of the chord**, not in pixels: 3-8% of the travel distance for corporate, 10-25% for organic or playful. 15px of sagitta on a 200px move is a deliberate arc; the same 15px on a 1600px move is invisible, and on a 4K frame it is invisible on both. This is also how the control works in After Effects, where the bow scales with the move | LottieFiles gives the absolute px (10-20px, 5px corporate, 20px+ playful) at UI scale; the fractional restatement is inference |
| when arcs apply at all | organic elements (characters, particles, physical props). Type, cards, panels and UI travel **straight** in professional motion graphics, and LottieFiles' own note concedes "Mechanical UIs can use straight paths intentionally". An 80%-arc-rate target is how you get the swoop, which is a recognised amateur tell. Report an arc on a text or card element as an unmotivated arc, not as a credit | LottieFiles' own caveat; the inversion of the default is inference from studio practice |
| entry tilt that settles to 0 | 5-15 degrees, typically ~10 | HF `reactive-displacement` INTRUDER_TILT |
| playful pop rotation | -10 to +10 degrees, alternate sign by index | HF `spring-pop-entrance` ROT_FROM |
| straight paths | type slams, mask reveals, push slides, mechanical UI | HF beat-direction; LottieFiles "Mechanical UIs can use straight paths" |
| orbit / path | MotionPathPlugin cubic; elliptical ring | HF techniques 9; HF `avatar-cloud-network` |

---

## 8. Secondary action

### (a) Canonical definition

Actions added to the main action to give the scene more life and support the main
action; they must emphasize rather than distract from the primary movement. Thomas and
Johnston's example: during a dramatic movement, facial expressions are better placed at
the beginning or end of the movement, not during it (Twelve basic principles,
Wikipedia). Bloop: a secondary action is subordinate to the primary and "not directly
caused by it" (which is what distinguishes it from follow-through, which is caused by
it).

LottieFiles UI adaptation: amplitude 30-50% of primary; timing 50-100ms after primary;
different easing than primary; examples: card enters, shadow grows; button presses, ripple
expands (`director/disney-principles.md`, section 8). The three-layer rule: primary,
secondary, ambient, "flat animation = missing layers" (`SKILL.md`, Three Pillars).

### (b) What it looks like in motion graphics

- **Shadow and glow**: the card lands, its drop shadow spreads and softens (LottieFiles
  counter-motion table: "Lifts (Y up): Shadow spreads + softens, 20-30%"); a glow blooms
  behind the hero (`ambient-glow-bloom`, peak opacity <= ~0.45); a burst behind a pressed
  button (`press-release-spring` phase 3, `BURST_PEAK_SCALE` 3-8).
- **Counter-motion**: hero enters left, background shifts right at 20-30% speed; hero
  scales up, shadow scales down 10-20%; hero rotates CW, ambient drifts CCW at 15-25%
  (LottieFiles choreography, Counter-Motion table).
- **Reaction of the environment**: HF beat-direction's example, a number "SLAMS into
  existence with such force the wave ripples in response". `reactive-displacement`
  formalizes it: the victim's displacement is derived from the intruder's driver.
- **Accents**: a divider draws (`scaleX` 0 to 1), a label ticks in, a data bar fills
  behind a stat (`stat-bars-and-fills`), a checkmark pops after the button
  (`press-release-spring`, "State change at release").
- **Depth through speed**: foreground 1.0x, midground 0.5x, background 0.2x
  displacement (LottieFiles choreography).
- **Sound** is secondary action in the audio channel: "a transient per cut, a whoosh
  under a fast move, a click on a UI state change ... A film whose cuts are silent reads
  unfinished" (manifesto, Sound).

### (c) Recipe

Primary: the card. Secondary: its shadow (separate element so `boxShadow` and `filter`
never tween on the same node, an HF constraint), a glow behind it, and the background
counter-shifting. Each secondary starts 2-3 frames after the primary, at 30-50% of its
amplitude, on a different ease.

```html
<div id="bg"></div>
<div id="glow"></div>
<div id="shadow"></div>
<div id="card">...</div>
```

```js
const T0 = f(6);
const PRIMARY_Y = 120;

// primary
tl.fromTo("#card", { y: PRIMARY_Y, opacity: 0 }, { y: 0, opacity: 1, duration: 0.55, ease: "power3.out" }, T0);

// secondary 1: the shadow. It shares the card's Y EXACTLY -- same target, same tween --
// because a drop shadow is attached to its caster. Only the SPREAD lags: opacity, scale
// and softness come in two frames later on a gentler ease. The earlier version tweened the
// shadow's y separately from the card's, so during the entrance the card visibly floated
// off its own shadow.
tl.fromTo(["#card", "#shadow"], { y: PRIMARY_Y }, { y: 0, duration: f(17), ease: "power3.out" }, T0);
tl.fromTo("#shadow", { opacity: 0, scale: 0.9 },
  { opacity: 0.35, scale: 1.05, duration: f(18), ease: "power2.out" }, T0 + f(2));
// Softness: prefer swapping between two pre-blurred shadow assets (or a static filter) over
// tweening a blur radius every frame. filter: blur() costs radius x area per frame, and a
// card-sized element at 28px is a real per-frame cost (HF depth-of-field-blur).

// secondary 2: glow blooms behind, later still, opacity capped
tl.fromTo("#glow", { opacity: 0, scale: 0.8 }, { opacity: 0.4, scale: 1.2, duration: 0.8, ease: "sine.out" }, T0 + f(3));

// secondary 3: background counter-shifts opposite to the card at ~25% of its speed
tl.fromTo("#bg", { y: -PRIMARY_Y * 0.25 }, { y: 0, duration: 0.7, ease: "power1.out" }, T0);

// accent: a rule draws under the headline once the card has landed
tl.fromTo("#rule", { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.4, ease: "power2.inOut" }, T0 + 0.45);
```

### (d) Measurable signature on rendered frames

- **Two or more regions move in the same beat with a hierarchy of amplitude**: the
  secondary region's total travel (M3) or intensity change (mean luma of the region, for
  a glow) is 30-50% of the primary's (LottieFiles).
- **Lag**: the secondary's first significant step is 1-3 frames at 30fps (50-100ms) after
  the primary's (LottieFiles). Follow-through (principle 5) has the same lag but the same
  direction and a decaying chain; secondary action may move in a different direction
  (counter-motion) or a different property (blur, luma).
- **Different ease family**: `segment.mjs` fits a different best family (or the same
  family with a clearly different exponent) on the secondary than on the primary
  (LottieFiles "Different easing than primary").
- **Counter-motion**: the background region's step series has the opposite sign to the
  hero's and 20-30% of its magnitude (LottieFiles).
- **Glow or shadow**: in the region behind the hero, mean luma rises (glow) or falls
  (shadow) with a soft M8 sharpness (blurred edge) and peaks after the hero settles; peak
  opacity of a glow stays under ~0.45 of full (HF `ambient-glow-bloom`).
- **Missing secondary** reads on the measurements as exactly one moving region per beat
  with the rest of the frame static and unchanged in luma (LottieFiles: "Feels cheap/flat:
  Only primary motion").
- Secondary must not out-move the primary: if the largest mover in the beat is not the
  hero, staging (principle 3) has failed, not secondary action.

### (e) Parameter ranges with basis

| parameter | range | basis |
| --- | --- | --- |
| amplitude vs primary | 30-50% | LottieFiles |
| delay after primary | 50-100ms (1.5-3 frames at 30fps) | LottieFiles |
| counter-motion speed ratio | 20-30% (position), 10-20% (shadow scale), 15-25% (rotation) | LottieFiles choreography |
| parallax layers | 1.0x / 0.5x / 0.2x | LottieFiles choreography |
| glow peak opacity | <= ~0.45 | HF `ambient-glow-bloom` |
| burst behind a press | scale 3-8, opacity 0.4-1.0, grow ~= fade 0.4-0.7s, blur 40-100px | HF `press-release-spring` |
| environmental glow | opacity 0.1 subtle, 0.25 default, 0.45 max; fade-in 0.6-1.0s | HF `press-release-spring` |
| decorative opacity on video | 12-25% (web 3-8% is invisible) | HF video-composition |
| accent line | `scaleX` 0 to 1, `transformOrigin` at the start end | HF video-composition ("animate well (`scaleX: 0` to `1`)") |

---

## 9. Timing

### (a) Canonical definition

"Timing refers to the number of drawings or frames for a given action, which translates
to the speed." Correct timing makes objects appear to obey physics (weight determines how
fast something reacts), and it establishes mood, emotion and personality (Twelve basic
principles, Wikipedia). Bloop: hand-drawn work "on twos" uses 12 drawings per second
rather than 24; timing (how many frames) is distinct from spacing (how far per frame).

LottieFiles UI adaptation: heavy (modals, pages) 400-800ms; light (tooltips, toggles)
100-250ms; sad/serious 600ms+; happy/light 200-400ms; urgent 100-200ms; entrances 30-50%
longer than exits (`director/disney-principles.md`, section 9). Duration by element type:
tooltip 80-120ms, button 120-180ms, icon 150-250ms, card 200-350ms, modal 300-400ms, page
400-600ms, dramatic reveal 600-1200ms, ambient 2-20s; distance scaling 50px = 0.8x, 100px
= 1.0x, 200px = 1.3x, 400px = 1.6x, full screen 1.8-2.0x; exit = 65-75% of entrance;
stagger total < 500ms (`reference/timing-easing-tables.md`).

### (b) What it looks like in motion graphics

- **Speed is weight.** Fast 0.15-0.3s = energy; medium 0.3-0.5s = professional; slow
  0.5-0.8s = gravity, luxury; very slow 0.8-2.0s = cinematic (HF motion-principles).
  LottieFiles material table: rigid 1.2x duration, elastic 0.8x, fluid 1.5x, gas 2.0x.
- **The cut is timing.** Manifesto: cuts land through blank runs of 1-8 frames; 12 of 23
  cuts in the proven build were locked to audio onsets within 0-2 frames; the music grid
  in the derived film was 150 BPM = 12 frames per beat at 30fps.
- **Beat lengths vary.** "A run of identical beat lengths reads as a metronome; the
  graded reference's cards vary by a factor of four"; grade-original requires a
  coefficient of variation >= 0.18 across spoken beats. HF: "The slowest scene should be
  3x slower than the fastest."
- **Enter longer than exit.** "A card takes 0.4s to appear but 0.25s to disappear" (HF
  motion-principles); exit = 65-75% of entrance (LottieFiles).
- **Reading time is timing.** "3 seconds on screen = must be readable in 2. Fewer words,
  larger type" (HF typography). Word reveals synced to the transcript, and the Apple
  cascade's duration "comes from the read, not from a number", roughly 2s for three
  words (manifesto).
- **Dwell.** After a climax the composition runs >= 1s (>= 2s for dramatic) or the reveal
  reads as "flashed and gone" (HF `press-release-spring`, `motion-blur-streak`,
  `reactive-displacement` DWELL_MIN).
- **Strobing is a spacing problem before it is a frame-rate problem.** State the
  threshold as a **fraction of frame width per frame**, not in absolute pixels: roughly
  0.5% of frame width per frame for hard high-contrast edges, up to about 1% with a
  shutter. At 1920 that is 10-19px; at 3840 it is 20-38px; at 960 it is 5-10px, which is
  where the often-quoted "5-10px" number came from. Halve the tolerance at 24 fps and
  roughly double it at 60. Contrast and edge hardness move it too: a blurred or fading
  element travels two to three times faster before it steps, and most of an entrance's
  fast frames happen while the element is still fading in. The fix is a shutter (or a
  per-layer directional blur) held a frame clear of every cut; raising the render rate
  does halve the per-frame travel of the same tween, so it is not nothing, but it does not
  substitute for a shutter. **Basis: the underlying "5-10px" is one measured case at 31px
  on a high-contrast letterform (manifesto); everything else here is inference, including
  the fractional restatement.**

### (c) Recipe

Durations derived from distance and weight, not typed by hand; exits shorter than
entrances; beat lengths deliberately uneven; frame-exact boundaries.

```js
// distance-duration scaling. THIS IS A UI TABLE AND A UI FUNCTION, marked inference, kept
// only for depicted UI inside a product film. For film work, budget PEAK VELOCITY instead:
// pick the speed the register allows, then let distance set duration. Following the table
// at the house 0.6s default, a full-screen 1920px move at the 2.0x cap takes 1.2s = 36
// frames = 53px per frame of leading-edge travel, which is five times the strobe budget
// stated two sections above. The table exists because a UI has a 400ms ceiling and must
// compress long moves; film has no such ceiling.
// (LottieFiles table, interpolated; the interpolation and WEIGHT are inference.)
function distScale(px) {
  if (px <= 50) return 0.8;
  if (px <= 100) return 1.0;
  if (px <= 200) return 1.0 + 0.3 * (px - 100) / 100;
  if (px <= 400) return 1.3 + 0.3 * (px - 200) / 200;
  return 1.6 + 0.3 * Math.min(1, (px - 400) / 700);      // ~1.9 at full 1080p width
}
const WEIGHT = { light: 0.18, medium: 0.32, heavy: 0.55, cinematic: 0.9 };   // base seconds at 100px
const enterDur = (px, w) => WEIGHT[w] * distScale(px);
const exitDur  = (px, w) => 0.7 * enterDur(px, w);       // exit = 65-75% of entrance (UI)
// In motion graphics most elements have NO exit tween: the outgoing element is removed by
// the next scene's entrance (push, cover, cut) or by a blank-frame cut. Treat the ratio as
// governing only the case where a card exits by animating in place, and exempt hard cuts
// and transitional handoffs by name. (Inference; manifesto's cut model.)

// beats authored on frames, uneven on purpose: 26, 14, 38, 18 frames
const beats = [0, 26, 40, 78, 96].map(f);
const cardY = 140;
tl.fromTo("#h1", { y: cardY, opacity: 0 }, { y: 0, opacity: 1, duration: enterDur(cardY, "heavy"), ease: "power3.out" }, beats[0] + f(4));
tl.fromTo("#h2", { x: -60, opacity: 0 },   { x: 0, opacity: 1, duration: enterDur(60, "light"),    ease: "power2.out" }, beats[1]);
tl.fromTo("#h3", { scale: 0.85, opacity: 0 }, { scale: 1, opacity: 1, duration: enterDur(200, "medium"), ease: "expo.out" }, beats[2] + f(2));
// final-scene exit only, accelerating and shorter
tl.fromTo("#h3", { y: 0, opacity: 1 }, { y: -cardY, opacity: 0, duration: exitDur(cardY, "medium"), ease: "power3.in", immediateRender: false }, beats[4] - f(8));

// group stagger capped so items x stagger <= 0.5s
const items = gsap.utils.toArray(".item");
const STAG = Math.min(0.06, 0.5 / items.length);
items.forEach((el, i) => tl.fromTo(el, { y: 32, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "power3.out" }, beats[2] + i * STAG));
```

Clip boundaries when the piece is multi-clip: write `start = frame / fps - 0.0002` and
`duration = (endFrame + 1 - frame) / fps - 0.0011` so a card neither misses its first frame
nor bleeds one frame long (manifesto, "The frame-boundary trap").

### (d) Measurable signature on rendered frames

- **Motion duration** per element: frames from first to last significant step (M7). Check
  against the element-type table (LottieFiles) and against distance: a 400px travel that
  takes the same frames as a 50px travel has no distance scaling (LottieFiles).
- **Enter versus exit**: exit frame count / entrance frame count for the same element,
  0.65-0.75 (LottieFiles), about 0.6 in the HF example (0.25/0.4).
- **Beat-length variation**: coefficient of variation of beat durations >= 0.18
  (grade-original); max/min beat ratio around 3-4 (HF "3x"; manifesto "factor of four").
- **Cut structure**: blank runs (M2 ink count ~0) of 1-8 frames between cards
  (manifesto); cuts within 0-3 frames of an audio onset when the piece is cut to music
  (manifesto `audio-beats.mjs`).
- **Dwell**: frames of stillness (all regions below significance) after the last
  significant motion and before the cut, >= 1s (HF DWELL_MIN); 100-200ms minimum between
  beats (LottieFiles choreography, "Leave 100-200ms stillness after resolution").
- **Stagger window**: last item's start minus first item's start <= 0.5s (LottieFiles;
  HF).
- **Strobing**: per-frame edge travel (M5) on a high-contrast edge above about 0.5% of
  frame width per frame without a shutter or per-layer blur, or a hard cut straddled by a
  shutter window (a ghost frame: the first frame after the cut shows a large blended
  change). The measured anchor is one case at 31px per frame on a high-contrast
  letterform (manifesto); the fractional threshold is inference.
- **Stall**: M9 duplicate frames > 0 inside a beat.

### (e) Parameter ranges with basis

| parameter | range | basis |
| --- | --- | --- |
| element-type durations | tooltip 80-120ms; button 120-180; icon 150-250; card 200-350; modal 300-400; page 400-600; dramatic reveal 600-1200; ambient 2000-20000 | LottieFiles timing tables |
| video speed bands | fast 0.15-0.3s; medium 0.3-0.5; slow 0.5-0.8; very slow 0.8-2.0 | HF motion-principles |
| MD3 duration tokens | short 50-200ms, medium 250-400, long 450-600, extra-long 700-1000 | Material Design 3 tokens via mdui mirror |
| distance scaling | 50px 0.8x; 100 1.0x; 200 1.3x; 300 1.5x; 400 1.6x; full screen 1.8-2.0x | LottieFiles |
| exit / entrance | 0.65-0.75 | LottieFiles; HF (0.25s vs 0.4s) |
| material scaling | rigid 1.2x, elastic 0.8x, fluid 1.5x, paper 1.0x, gas 2.0x, glass 0.9x | LottieFiles |
| personality durations | playful 150/250/400ms; premium 350/500/800; corporate 200/300/450; energetic 100/180/300 | LottieFiles |
| stagger | micro 20-40ms (< 200ms total); standard 50-100 (< 400); dramatic 100-200 (< 600); wave 30-60 (< 500); hard cap 500ms | LottieFiles; HF |
| first motion offset | 0.1-0.3s after the cut | HF motion-principles |
| beat CV | >= 0.18 | grade-original |
| slowest : fastest scene | >= 3 : 1 | HF motion-principles |
| blank gap between cards | 1-8 frames | manifesto |
| audio-onset lock tolerance | 0-3 frames | manifesto |
| dwell after climax | >= 1s; >= 2s dramatic | HF rules |
| strobe threshold | about 0.5% of frame width per frame on a hard high-contrast edge (10px at 1920, 5px at 960, 20px at 3840); halve at 24fps, roughly double at 60fps | **inference**, generalised from a single measured case (31px per frame strobed on a high-contrast letterform, manifesto). Not a law; expose it as a knob |
| hold before a cut | a settled pose is held at least 6-8 frames at 30fps before any cut, or the settle is never seen | inference; consistent with, but not stated in, manifesto's cut model |
| one physics per film | one gravity (the same `.in` exponent and fall time per pixel for every drop) and one light direction across all beats | inference; inconsistent fall acceleration between two drops is the commonest solid-drawing failure in generated pieces |
| clip boundary bias | start - 0.0002s; duration - 0.0011s | manifesto |

---

## 10. Exaggeration

### (a) Canonical definition

"Animated motions that strive for perfect imitation of reality can look static and
dull." Disney's exaggeration stayed true to reality but in a wilder, more extreme form;
when several elements are exaggerated they must be balanced so the viewer is not confused
(Twelve basic principles, Wikipedia). Bloop: exaggeration applies to pose clarity,
silhouette, and design intensity, and "you can exaggerate without physical limitations".

LottieFiles UI adaptation: playful 15-25%, energetic 20-30%, corporate 0-5%, premium 0%;
scale overshoot 10-30% beyond target; rotation +/- 5-15 degrees
(`director/disney-principles.md`, section 10).

### (b) What it looks like in motion graphics

- **Amplitude.** The slam that scales from 2.2 to 1 instead of 1.1 to 1; the `waterfall`
  anchor word that travels 60-80px where a light word travels 30-48px; a push-through
  from `SCALE_FROM` 1.3-2.5; grade-original exempts "the Through treatment (which scales
  its line to 7x so it passes the camera)".
- **Speed.** `expo.out` instead of `power2.out` on the same move; "SLAMS, CRASHES,
  PUNCHES, STAMPS, SHATTERS" versus "SLIDES, PUSHES" (HF beat-direction verbs).
- **Blur as exaggerated velocity**: `motion-blur-streak` PEAK_BLUR 8-30, capped ~18-20 at
  wrapper level; the defocus entry resolving over 10-15 frames (manifesto).
- **Overshoot as exaggerated settle**: see principle 5. HF's doctrine matters here:
  overshoot "is a register, not a spice", and "bounce everywhere reads cheap, the second
  failure is worse" than one ease everywhere (`gsap-easing-and-stagger`).
- **Type scale**: headlines 64-120px on video versus 32-48 on web; hero text at 60-80% of
  frame width (HF video-composition, typography). Exaggeration of the design, not only the
  motion.
- **Restraint is the premium form.** Apple's style: "Subtle, smooth, quick. Nothing flashy
  or dramatic" (manifesto, Apple cascade). "Personality Mistakes: Premium: too subtle =
  invisible; too slow = waiting; zero = broken" (LottieFiles troubleshooting).

### (c) Recipe

A slam with exaggerated scale and a coupled blur envelope that resolves exactly at the
settle, and the personality knob applied as one number.

```js
const P = { corporate: 0.03, playful: 0.20, energetic: 0.28, premium: 0.0 }["energetic"];   // exaggeration fraction
// Clamp the derived start scale into the table's own band. 1 + 6 * 0.28 = 2.68, which is
// outside the (e) table's "slam start scale 1.3-2.5".
const SLAM_FROM = Math.min(2.5, Math.max(1.3, 1 + 6 * P));
const T0 = f(8);

// exaggerated arrival: scale from far larger than rest, expo.out, blur peaks at peak speed
const blurNode = document.getElementById("streak-blur");            // <feGaussianBlur>
const bp = { v: 22 };
// DIRECTIONAL. stdDeviation takes separate x and y; an equal-on-both-axes Gaussian is a
// DEFOCUS, not a motion smear, and produces from frame one exactly the read that section
// 10(d) tells you to avoid ("a blur that lingers after the stop reads as a focus pull").
// Write "v 0" for lateral travel, "0 v" for vertical, and rotate the filtered group to the
// travel vector for anything diagonal.
const writeBlur = () => blurNode.setAttribute("stdDeviation", `${bp.v} 0`);
writeBlur();                                                         // seed frame 0
tl.fromTo("#slam", { scale: SLAM_FROM }, { scale: 1, duration: f(8), ease: "expo.out" }, T0);
tl.fromTo("#slam", { opacity: 0 }, { opacity: 1, duration: f(3), ease: "power2.out" }, T0);
tl.fromTo(bp, { v: 22 }, { v: 0, duration: f(8), ease: "expo.out", onUpdate: writeBlur }, T0);

// exaggerated settle, only in the playful/energetic registers; transforms only
if (P >= 0.15) {
  const s = springEase({ response: 0.4, dampingFraction: 0.65 });   // ~6.8% overshoot
  tl.fromTo("#slam-inner", { scale: 0.92 }, { scale: 1, duration: s.duration, ease: s.ease }, T0 + 0.1);
}

// exaggerated tilt that settles to flat (arc + exaggeration together)
tl.fromTo("#slam", { rotation: -12 * P / 0.2 }, { rotation: 0, duration: 0.5, ease: "power3.out", immediateRender: false }, T0);

// environment reacts: the CAMERA takes the hit, not the wallpaper. Scaling #bg alone
// decouples the background from the foreground and the frame reads as the wallpaper
// twitching; put the reaction on the scene wrapper so everything moves together.
const SCENE = "#scene";
tl.fromTo(SCENE, { scale: 1 }, { scale: 1 + 0.06 * P / 0.2, duration: f(4), ease: "power1.out" }, T0 + f(2));
tl.fromTo(SCENE, { scale: 1 + 0.06 * P / 0.2 }, { scale: 1, duration: f(18), ease: "power2.out", immediateRender: false }, T0 + f(6));
```

**Camera shake.** The decaying shake that accompanies a slam, a hit or a hard cut is the
single most common secondary reaction in motion graphics (the AE habit is `wiggle()` on a
camera null) and this document had no recipe for it. Two legal forms under the contract.
`CustomWiggle` (a pure function of progress; never `type: "random"`, which is seeded at
creation and not reproducible), or a hash-seeded sum of decaying sines driven from
timeline time, which is the section 4(c) pattern:

```js
const shake = { t: 0 };
const AMP = 10, DECAY = f(10);          // 1080p: 6-14px, decaying over 8-12 frames
function writeShake() {
  const k = Math.max(0, 1 - shake.t / DECAY);          // linear decay to exactly zero
  const e = k * k;                                      // quadratic envelope reads heavier
  gsap.set("#scene", {
    x: e * AMP * Math.sin(58 * shake.t) * 0.9,
    y: e * AMP * Math.sin(71 * shake.t + 1.7) * 0.6,
    rotation: e * 0.4 * Math.sin(63 * shake.t + 0.4),   // keep rotation under ~0.5 degrees
  });
}
writeShake();
tl.fromTo(shake, { t: 0 }, { t: DECAY, duration: DECAY, ease: "none", onUpdate: writeShake }, IMPACT_FRAME);
```

The shake must decay to exactly zero before the next beat's first motion. Amplitudes are
inference at 1080p; the two legal forms are from the contract and
https://gsap.com/docs/v3/Eases/CustomWiggle/ .

### (d) Measurable signature on rendered frames

- **Extent beyond rest.** Max of `sx[t]` (M4) over the entrance divided by settled
  `sx_rest`: an exaggerated slam starts at 2-7x and resolves; a plain entrance starts near
  1.0. Peak-over-rest ratio on any property (scale, rotation, blur) minus 1 is the
  exaggeration amount.
- **Overshoot fraction** (principle 5): 10-30% scale beyond target for a playful pop;
  0-5% corporate; 0 premium (LottieFiles).
- **Rotation extent**: peak principal-axis angle deviation of 5-15 degrees settling to 0
  (LottieFiles).
- **Blur envelope**: M8 sharpness minimum coincides with the frame of maximum step and
  sharpness is back to its settled value on the frame the element stops (HF
  `motion-blur-streak`: "A blur that lingers after the stop reads as a focus pull").
- **Balance**: only one element per beat carries the exaggerated extent. The
  peak-over-rest > 1.5 figure used to flag "unbalanced" is a **tuning parameter**, not a
  measured threshold (Thomas and Johnston via Wikipedia state the principle; the number is
  inference and a grader should expose it as a knob).
- **Consistency of register**: across the film, the distribution of overshoot fractions
  and peak-over-rest ratios should cluster (one personality). A film with 0% overshoot on
  ten elements and 20% on one reads as a mistake, not a choice (LottieFiles "Mixed
  archetypes: pick one for 90%+").

### (e) Parameter ranges with basis

| parameter | range | basis |
| --- | --- | --- |
| exaggeration by personality | playful 15-25%, energetic 20-30%, corporate 0-5%, premium 0% | LottieFiles |
| scale overshoot beyond target | 10-30% (playful UI); <= ~13% (`back.out` <= 2) in HF | LottieFiles; HF `spring-pop-entrance` |
| rotation | +/- 5-15 degrees | LottieFiles |
| slam start scale | 1.3-2.5 push-through; 2.2 measured on a word slam in this doc's recipe | HF `motion-blur-streak` SCALE_FROM; recipe value: inference |
| entrance blur peak | 8-30 (default 18), ~18-20 cap at wrapper level, > 30 erases the glyph | HF `motion-blur-streak` |
| defocus entry resolve | 10-15 frames | manifesto product-UI vocabulary |
| waterfall travel by weight | anchor 60-80px, normal 40-50, light 30-48 | HF `waterfall-entry` |
| headline size on video | 64-120px; in-feed >= 90px | HF video-composition; HF typography |
| audio-reactive pulse | <= 5% scale on text/logo; 10-30% on backgrounds | HF techniques |
| overshoot as register | rare, explicitly playful; never product/enterprise | HF `spring-pop-entrance` |

---

## 11. Solid drawing

### (a) Canonical definition

Taking into account three-dimensional form, giving it volume and weight; the animator
must understand 3D shapes, anatomy, weight, balance, light and shadow. Thomas and
Johnston warned against "twins", mirrored symmetrical poses that look lifeless (Twelve
basic principles, Wikipedia). Bloop: twinning, weight distribution, center of mass.

LottieFiles UI adaptation: maintain consistent proportions across keyframes; use scale
and rotation together for depth; shadow behavior matches the implied light source
(`director/disney-principles.md`, section 11). Interaction Design Foundation:
"Inconsistent shadows or perspectives signal something is wrong."

### (b) What it looks like in motion graphics

In an HTML composition solid drawing is the correctness of the geometry and the
rendering, not draftsmanship:

- **Proportions hold.** Non-uniform scale is only ever a deliberate squash; a card that
  arrives at `scaleX: 1.0, scaleY: 0.96` by accident is a broken drawing. Text is never
  non-uniformly scaled except as a measured per-glyph fit (manifesto: `scaleX` plus a
  margin, in `em` units).
- **Depth is built correctly.** `perspective` on the parent, `preserve-3d` on the
  animated element (HF techniques section 3); `transformPerspective` via GSAP, not a CSS
  `perspective()` in the transform string that GSAP will overwrite (HF motion-principles,
  Image Motion Treatment); never a `filter` on a `preserve-3d` element because it flattens
  the 3D context (HF `motion-blur-streak`, Filter placement).
- **Pivot is right.** `transform-origin` at the contact edge for a squash, at the cursor
  tip for a cursor (`physics-press-reaction`), at the anchor corner for a resize
  (`cursor-drag`), at 12 o'clock for a progress ring (`svg-path-draw`); SVG icons use
  `setAttribute('transform', 'rotate(deg cx cy)')` because CSS `transform-box` puts the
  origin off-center on thin lines (`svg-icon-enrichment`).
- **Light is consistent.** The shadow's offset follows the implied light; when a card
  tilts, its shadow and rim highlight move with it, driven from one source. Manifesto's
  liquid-glass rim: "four separate inset shadows, not a border. Real glass catches light
  hardest on one edge".
- **Sub-pixel rendering.** Transforms interpolate sub-pixel; layout properties snap to
  whole pixels and stutter on slow tails (HF `gsap-transforms-and-perf`). This is the
  motion-graphics version of "the drawing wobbles between frames".
- **Controllers, not per-element keyframes**: nested wrappers so one scale keyframe
  drives a whole group (manifesto, Structure), which keeps the group's internal
  proportions rigid.
- **No twins**: two identical cards entering with mirrored, simultaneous motion read as
  dead; `split-tilt-cards` runs their float "in phase opposition" (HF).

### (c) Recipe

A tilted card whose shadow and rim highlight are derived from the same tilt value, so light
stays consistent through the move; correct perspective setup; group controller wrapper.

```html
<div class="scene" id="scene">                      <!-- perspective lives here -->
  <div class="shadow" id="shadow"></div>            <!-- sibling: never inside preserve-3d -->
  <div class="group" id="group">                    <!-- controller: one transform for the whole cluster -->
    <div class="card" id="card"><div class="rim" id="rim"></div>...</div>
  </div>
</div>
<style>
  #shadow{ position: absolute; inset: 0; border-radius: inherit; background: rgba(0,0,0,0.45); filter: blur(28px); }
</style>
<style>
  /* ONE projection. perspective lives on the parent OR transformPerspective lives on the
     element -- never both. Applying both composes two projections, so this card's
     foreshortening matches nothing else in the scene. HF gives both patterns; pick one. */
  #scene { perspective: 1200px; }
  #group { transform-style: preserve-3d; will-change: transform; }
  #card  { transform-origin: 50% 50%; will-change: transform; }
  /* The shadow sits OUTSIDE #group. A filter on a child of a preserve-3d group flattens
     that child's 3D context, so a blurred shadow inside the group renders flat while the
     card tilts. Keep it a sibling and drive it from the same pose object. */
  #rim   { position: absolute; inset: 0; border-radius: inherit; pointer-events: none;
           box-shadow: inset 0 1.5px 0 rgba(255,255,255,0.62), inset 0 -1.2px 0 rgba(255,255,255,0.20); }
</style>
```

```js
// NO transformPerspective here: #scene already carries `perspective: 1200px`. The earlier
// version set both and doubled the projection.
const T0 = f(6);
const LIGHT = { x: -0.6, y: -0.8 };                   // implied light direction, fixed for the whole film

// one pose object drives card tilt, shadow offset and rim brightness: consistent light by construction
const pose = { ry: -18, rx: 6, lift: 0 };
function applyPose() {
  gsap.set("#card", { rotationY: pose.ry, rotationX: pose.rx, y: -pose.lift * 10 });
  // shadow slides away from the light and softens as the card lifts
  gsap.set("#shadow", {
    x: -LIGHT.x * (14 + pose.lift * 18) + pose.ry * 0.6,
    y: -LIGHT.y * (14 + pose.lift * 18),
    scale: 1 + pose.lift * 0.06,
    opacity: 0.45 - pose.lift * 0.15,
  });
  // rim catches more light as the lit edge turns toward it
  gsap.set("#rim", { opacity: 0.55 + 0.45 * Math.max(0, Math.cos((pose.ry - 20) * Math.PI / 180)) });
}
applyPose();                                            // seed t=0
tl.fromTo(pose, { ry: -18, rx: 6, lift: 0 }, { ry: -6, rx: 2, lift: 1, duration: 0.9, ease: "power3.out", onUpdate: applyPose }, T0);
tl.fromTo("#group", { x: -120, opacity: 0 }, { x: 0, opacity: 1, duration: 0.6, ease: "power3.out" }, T0);   // controller entrance
```

`applyPose` is a pure function of `pose`, and `pose` is a pure function of timeline time
through its `fromTo`, so the whole rig is seek-safe.

### (d) Measurable signature on rendered frames

- **Aspect stability.** `sx/sy` (M4) of a settled element is constant across the settled
  window (M10); a drift means an accidental non-uniform scale or a reflow. The 1% figure
  is a **tuning parameter** (inference; chosen below the 4% bbox flicker manifesto warns
  about, not measured).
- **Whole-pixel rest.** Text and hairline elements settle to whole-pixel translate values.
  A headline resting at x = 40.37px sits on a different antialiasing phase than one at 40,
  and any residual ambient motion under a pixel makes the letter edges crawl. It is one of
  the few defects that looks worse in the render than in the browser preview, so it
  survives review and ships. Round the final position rather than letting an eased tween
  asymptote to a fraction. (Inference; note that the moving-hold requirement and the
  no-duplicate-frames rule both push builds directly into this failure.)
- **No pixel snapping.** On a slow tail, the M6 step series of a transform is a smooth
  decay of fractional values (sub-pixel edges show as antialiasing changes); a series of
  exact zeros punctuated by single 1px steps is a layout property tween (HF
  `gsap-transforms-and-perf`).
- **No stalls.** M9 duplicate consecutive frames = 0 (grade-original).
- **Shadow consistency.** The vector from the element's centroid to its shadow's centroid
  has a stable direction across the film (same implied light); its length grows with lift
  (LottieFiles "Lifts (Y up): Shadow spreads + softens"). A shadow whose direction flips
  between beats is inconsistent light (Interaction Design Foundation).
- **Perspective consistency.** Elements in 3D show vanishing behaviour consistent with one
  `perspective` value: the far edge of a rotated card is shorter than the near edge by a
  ratio that is the same for every card in the beat (inference).
- **Glyph integrity.** On type, per-letter ink-width ratios relative to the reference are
  uniform; a single glyph with a different ratio is a broken fit (manifesto, per-glyph
  fit and glyph IoU).
- **Twins.** Two regions with identical step series (correlation ~1, zero lag) and
  mirrored positions in the same beat.

### (e) Parameter ranges with basis

| parameter | range | basis |
| --- | --- | --- |
| perspective | 900-1200px on the parent | HF techniques 3 (900px); HF motion-principles (`transformPerspective: 1200`) |
| image tilt | `rotationY: -8` plus box-shadow | HF motion-principles |
| card tilt pair | +/- baseTilt on split cards, float in phase opposition | HF `split-tilt-cards` |
| settled aspect drift | <= 1% | inference (**tuning parameter**, not measured) |
| layer promotion | promote deliberately and for the whole composition, never toggling, and **never promote type you are about to scale**. Text on a promoted layer is rasterised once at the promotion scale and stretched, so a scale tween softens the glyphs and they visibly re-sharpen when the layer is de-promoted, which reads as a weight pop on the settle frame. This is the browser's version of forgetting Continuously Rasterize in After Effects, and `will-change: transform` sprinkled per element is how you get it | browser compositor rasterisation behaviour; inference for the rule |
| entrance scale on type | scale down into place (1.06-1.12 -> 1 premium, 0.85-0.92 -> 1 for a pop), not up from zero. `scale: 0 -> 1` on type reads as inflation and rasterises glyphs at tiny sizes on the first frames, which is the PowerPoint zoom section 13 warns about | HF `spring-pop-entrance` uses 0 -> 1; the idioms and the raster note are inference |
| shadow direction | one implied light per film | LottieFiles; Interaction Design Foundation |
| rim highlight | bright top inset (0.62 alpha), dim sides (0.20) | manifesto liquid glass |
| SVG pivots | explicit `rotate(deg cx cy)` attribute | HF `svg-icon-enrichment` |
| forbidden geometry tweens | width, height, top, left, margin, padding, fontSize, letterSpacing, roundProps | HF `gsap-transforms-and-perf` |

---

## 12. Appeal

### (a) Canonical definition

The equivalent of charisma in an actor: an appealing character feels real and
interesting, villains included. Symmetrical or baby-like faces tend to be effective;
complicated or hard-to-read designs lack appeal (Twelve basic principles, Wikipedia).
Bloop: consistency of design, silhouette recognition, shape variation.

LottieFiles UI adaptation: smooth curves over sharp angles; satisfying timing;
personality consistency across all elements; "Appeal killers: jerky motion, inconsistent
timing, abrupt stops, uniform animation" (`director/disney-principles.md`, section 12).
"Appropriate on 100th viewing" (`reference/quality-checklist.md`).

### (b) What it looks like in motion graphics

Appeal is the meta-principle: it is what a piece has when the other eleven are present in
the right proportion and consistent with one another.

- **One personality.** Signature easing, a three-value duration palette, one entrance
  pattern (LottieFiles Brand Motion Identity); "Consistent: same interaction = same
  motion" (LottieFiles checklist).
- **Variety inside the personality.** At least 3 ease characters per scene, 3+ entrance
  directions, no two scenes with the same stagger or the same ambient (HF motion-principles
  guardrails, HF techniques). Both at once: consistency of register, variety of gesture.
- **Type is appeal.** Banned monoculture fonts, extreme weight contrast (300 vs 900),
  tracking -0.03 to -0.05em on display sizes, one expressive font per scene (HF
  typography). "Motion is typography. How a word enters carries as much meaning as the
  font."
- **The frame is designed, not generated.** Two focal points, three layers, background
  not empty, anchored to edges, tinted neutrals, no full-screen linear gradients on dark
  (HF video-composition).
- **Smooth beats bouncy.** Bounce is "the #1 instant turn-off in agent-made videos" (HF
  `spring-pop-entrance`).
- **It resolves.** Build / breathe / resolve; stillness after motion; a dwell after the
  climax (HF motion-principles; HF rules).
- **Sound matches motion.** Smooth motion wants soft transients; hard cuts want sharp
  ones (manifesto, Sound).

### (c) Recipe

Appeal is not one tween, so the recipe is a motion-language block plus a build-time audit
that walks the timeline and reports the appeal killers before render. The audit is
deterministic (it reads tween metadata, not time) and runs once at setup.

```js
// 1. the motion language, declared once
const LANG = {
  personality: "corporate",                        // one per film
  ease: { enter: "power3.out", exit: "power3.in", move: "power2.inOut", ambient: "sine.inOut", punch: "expo.out" },
  dur:  { quick: f(6), standard: f(10), slow: f(15) },   // three values only, on the frame grid
  overshoot: 0,                                    // corporate: 0-3%
};
const tl = gsap.timeline({ paused: true, defaults: { ease: LANG.ease.enter, duration: LANG.dur.standard } });

// 2. every tween uses the language
tl.fromTo("#title", { y: 90, opacity: 0 }, { y: 0, opacity: 1, duration: LANG.dur.slow, ease: LANG.ease.enter }, f(6));
tl.fromTo("#sub",   { x: -60, opacity: 0 }, { x: 0, opacity: 1, duration: LANG.dur.standard, ease: LANG.ease.punch }, f(12));
tl.fromTo("#rule",  { scaleX: 0 }, { scaleX: 1, duration: LANG.dur.quick, ease: LANG.ease.move }, f(16));
tl.fromTo("#glow",  { opacity: 0 }, { opacity: 0.3, duration: 1.6, ease: LANG.ease.ambient }, f(8));

// 3. build-time audit of the appeal killers (deterministic; reads tween vars only)
function auditAppeal(tl) {
  const tweens = tl.getChildren(true, true, false);
  // startTime() on a tween inside a NESTED timeline is relative to that nested parent, so
  // "first motion at" is wrong whenever scenes are sub-timelines. Walk to the root.
  const globalStart = (t) => { let s = t.startTime(), p = t.parent;
    while (p && p !== tl) { s += p.startTime(); p = p.parent; } return s; };
  const eases = new Set(), durs = new Set(), starts = tweens.map(globalStart).sort((a, b) => a - b);
  let linearSpatial = 0, bouncy = 0;
  tweens.forEach((t) => {
    const v = t.vars;
    // A FUNCTION ease (springEase, CustomEase) stringifies to its source text, so naming
    // is useless for it: every spring would count as its own "family" and the >= 3 check
    // would pass for the wrong reason. Classify by sampled SHAPE instead, and cluster:
    // power2.out and power3.out differ by two or three frames of settle and do not read as
    // two characters. (Cluster radius 0.06 on the (s(.25), s(.5), s(.75)) triple:
    // inference.)
    const fn = typeof v.ease === "function" ? v.ease : gsap.parseEase(v.ease || "power1.out");
    const shape = [0.25, 0.5, 0.75].map((p) => Math.round(fn(p) / 0.06)).join(":");
    eases.add(shape);
    durs.add(Math.round(t.duration() * 100) / 100);
    const spatial = ["x", "y", "scale", "scaleX", "scaleY", "xPercent", "yPercent"].some((k) => k in v);
    if (spatial && ease === "none" && !("rotation" in v)) linearSpatial++;
    if (/^(back|elastic|bounce)/.test(ease)) bouncy++;
  });
  const warn = [];
  if (eases.size < 3) warn.push(`only ${eases.size} ease characters (want >= 3)`);
  if (starts[0] < 0.1) warn.push(`first motion at ${starts[0].toFixed(2)}s (offset 0.1-0.3s)`);
  if (linearSpatial) warn.push(`${linearSpatial} linear spatial tweens`);
  if (bouncy && LANG.personality !== "playful") warn.push(`${bouncy} overshoot eases in a ${LANG.personality} film`);
  if (durs.size > 4) warn.push(`${durs.size} distinct durations (a palette is 3-4)`);
  return warn;
}
console.log(auditAppeal(tl));
```

### (d) Measurable signature on rendered frames

Appeal has no single measurement; it is the conjunction of the others plus consistency
statistics across the film:

- **Ease variety and consistency.** Fit every motion segment (`segment.mjs`). Across a
  scene: at least 3 distinct families (HF). Across the film: the entrance segments cluster
  on one family (personality), exits on its `.in` mirror. All-one-family reads flat; a
  scatter of every family reads like no one chose.
- **Duration palette.** Histogram of segment durations shows 3-4 modes, not a smear
  (LottieFiles palette; inference for "modes").
- **No abrupt stops.** For every ease-out segment the last significant step is below 1%
  of the travel (computed: `power2.out` and above reach this; `sine.out` and `power1.out`
  end with steps of 0.4-0.5% per frame of a 100px move at 15 frames, still smooth;
  linear ends at 6.7%: that is the abrupt stop).
- **Below about 5 frames, ease is noise.** A 3-frame tween has two in-between positions;
  swapping `power2.in` for `power2.out` moves them by a few percent of the travel. Short
  accents are keyed by *spacing* (how many distinct positions you give them), not by
  curve type. Specify positions, not cubics, under 5 frames (inference).
- **No jerk.** Second difference of the step series (acceleration) has no spikes inside a
  segment except at the segment boundaries (a re-trigger). A spike mid-segment is a
  tween fighting another tween on the same property (HF "Never overlap conflicting
  transform tweens").
- **Not uniform.** Entrance directions across the film: at least 3 distinct (up, down,
  left, right, scale, opacity-only) (HF video-composition). Stagger values across scenes:
  not all equal (HF).
- **Type**: distinct type sizes in the timeline >= 3 (grade-original); vertical centroid
  spread sd >= 0.09 and middle-third occupancy <= 85% (grade-original).
- **Settle law honoured**: 0 reversals in a no-overshoot film (grade-original), or one
  reversal of consistent magnitude in a playful one.
- **Dwell and breathe**: every beat ends with >= 1s of near-stillness after its climax and
  no duplicate frames inside it.
- **Legibility**: settled contrast >= 3:1, no ink in the 4% margin (grade-original).
- **Sound**: transients coincide with cuts (audio onsets within 0-3 frames of cut frames,
  manifesto `audio-beats.mjs` run on your own render).

### (e) Parameter ranges with basis

| parameter | range | basis |
| --- | --- | --- |
| personality archetypes | playful 150-300ms, ease-out-back, 10-20%; premium 350-600ms, (0.4,0,0.2,1), 0%; corporate 200-400ms, (0.2,0,0,1), 0-3%; energetic 100-250ms, ease-out-expo, 15-30% | LottieFiles `SKILL.md` Motion Personality |
| brand identity constants | one signature ease for 80% of tweens; 3 durations; one entrance pattern | LottieFiles |
| ease characters | **three distinct gestures per scene** (direction, amplitude and duration all count toward the variety) and three ease families across the *film*, not inside every scene. The earlier version of this table printed ">= 3 ease characters per scene" directly above "one signature ease for 80% of tweens", which pull in opposite directions and cannot both be enforced. Studio practice is a house curve carrying most of the piece plus a small number of deliberate exceptions (the punch on the hero, the ambient sine, the exit mirror); a per-scene quota pushes a builder to add character it does not need, which is the "scatter of every family reads like no one chose" failure named three paragraphs below | HF techniques states ">= 3 different easings"; LottieFiles Brand Motion Identity states the signature ease. The reconciliation is inference |
| entrance directions per scene | >= 3 | HF video-composition |
| type sizes | >= 3 distinct | grade-original |
| weight contrast | 300 vs 900 | HF typography |
| display tracking | -0.03 to -0.05em | HF typography |
| overshoot register | none by default; playful only | HF |
| focal points | >= 2 per scene | HF motion-principles, video-composition |
| layers | >= 3 per scene | HF |

---

## 13. Which principles generated motion graphics miss, and how it reads

The sources that say this most directly are HF motion-principles ("You know these rules
but you violate them. Stop."), `spring-pop-entrance` ("the #1 instant turn-off in
agent-made videos"), LottieFiles troubleshooting, and the harness in `grade-original.py`,
each check of which "is written to actually catch the specific defect that produced it".
The viewer's words for each defect, mapped to the missing principle and the detector.

### "PowerPoint" / "slide deck"

What is missing: **staging, follow-through, secondary action, timing variety**.
The shape of it: every element enters with `y: 30, opacity: 0`, the same ease, the same
0.4-0.5s, all at once or in DOM order; nothing reacts to anything; each beat is the same
length; the first tween starts at t=0 (HF motion-principles guardrails, all six).
Detectors: one ease family for the whole film; all entrance directions identical; active
regions per frame equal to the total (no 1/3 rule); zero counter-motion (background step
series flat while the hero moves); beat CV < 0.18 (grade-original); first significant
step at frame 0.

### "Floaty"

What is missing: **slow in/slow out in the right direction, timing, weight**.
The shape of it: `sine.inOut` or `power1` on everything; entrances on ease-in (they
start slow and arrive without conviction); durations at the slow end of every table
regardless of distance; no ease-in on exits so elements drift off instead of leaving.
`reactive-displacement` names the same read: "higher bounce on long durations reads as
floaty". Detectors: peak/avg velocity below ~2 on entrances (computed: `sine.out` 1.57,
`power1.out` 2.0); entrance duration not scaling with distance; exits whose largest step
is at the start. **Register caveat:** `sine.out` and `power1.out` are the *correct*
choices on a slow reveal in a calm, premium or documentary register, so this detector
needs the register as an input and must not fire on a declared calm piece
(HF `gsap-easing-and-stagger` mood mapping: "sine, power1 feel contemplative").

### "Weightless"

What is missing: **squash and stretch, anticipation, follow-through, secondary action**.
The shape of it: things stop dead with no settle and no deformation, nothing winds up,
nothing trails, the environment never reacts. Opacity-only entrances (LottieFiles
CRITICAL: "Opacity-only for important states"). Detectors: `sx/sy` constant through every
impact; zero anticipation runs; every region's last significant step is as large as the
mean (abrupt stop); only one moving region per beat.

### "Robotic" / "mechanical"

What is missing: **slow in/slow out, arcs**.
The shape of it: linear spatial tweens and dead-straight paths, uniform stagger, everything
synced to the frame. LottieFiles: "Looks Robotic: Linear easing or no arcs". Detectors: step series with CV < 0.15; arc ratio ~0 on every path where an arc is
motivated; and uniform lag **combined with** uniform duration, uniform distance and a
single ease. Uniform lag on its own is not the defect: every stagger recipe in this
document produces exactly identical lag (`T0 + i * 0.06`, `beats[2] + i * STAG`), so a
detector keyed on it flags correct output. Note also that GSAP's advanced stagger object
(`{ each, from, ease, grid }`) is the direct analogue of the After Effects Range Selector's
Ease High / Ease Low and is never used anywhere in this document; a hand-rolled `forEach`
throws away the one control that makes a cascade read hand-animated. (Inference; the
Range Selector translation is in manifesto's own AE section.)

### "Cheap" / "bouncy" / "cartoon"

What is missing: **exaggeration under control, appeal**. This is the inverse failure and
HF calls it the worse one: `back.out` on everything, `elastic` on type, overshoot as
spice. Detectors: reversal count >= 1 on most settles in a non-playful film; overshoot
fraction > 13%; multiple reversals (elastic wobble); `bounce` fits on anything that is not
literally dropping.

### "Flat" / "nothing loaded"

What is missing: **staging (composition side), secondary and ambient layers, solid drawing
of the frame**. Pure `#000` ground, one centered text block, web-sized type, decorative
opacity under 10%, no glow, no structure (HF video-composition). Detectors: one moving
region and no luma change anywhere else; centroid always in the middle third
(grade-original); type sizes < 3 distinct; contrast either failing 3:1 or every element
at the same contrast.

### "Jump cut" / "jarring"

What is missing: **timing (the cut) and anticipation (the gap)**. Scenes that pop fully
formed, exits that fade the outgoing scene and then run the next entrance (a "jump cut
with a dip"), first motion at t=0, no blank frame, cuts that ignore the audio onsets,
clips that start a frame late or end a frame long. Detectors: outgoing and incoming
motion not overlapping at the cut; velocity mismatch at the cut > 5%; cut frames off the
onset grid; clip boundary drift (manifesto's `segment.mjs` on your own render should find
the cuts on the same frames).

### "Stutter" / "choppy"

What is missing: **solid drawing (rendering)**. Layout-property tweens snapping to
whole pixels on slow tails, `roundProps`, duplicate frames on holds, strobing from
hard-edge travel above about 0.5% of frame width per frame without a shutter. Detectors:
M9 > 0 against the declared cadence; 0,0,1 step patterns; per-frame edge travel over the
strobe threshold.

### "Flashed and gone"

What is missing: **timing (dwell)**. The reveal lands at `DURATION - 0.2s`, the climax
has no hold, the ambient driver is still moving on the cut. Detector: stillness after
the last climax step < 1s.

### Priority when fixing

The LottieFiles severity tiers order the same list: CRITICAL is linear spatial easing,
opacity-only states, exceeding 1/3 screen, a missing primary layer, stagger over 500ms,
layout-property jank; HIGH is a missing secondary layer, wrong duration for the element
type, wrong directional easing, inconsistent personality, no follow-through; MEDIUM is a
missing ambient layer, no anticipation, overshoot mismatch, weak arcs, missing
counter-motion (`reference/quality-checklist.md`). Manifesto's fix order for a replica
puts structure first (frame count, clip boundaries, flat colours, cut times, gaps) and
eases last; for an original film grade-original's checks are the gate.

---

## 14. Four things the twelve principles do not name, and that this document was missing

These are additions from the practitioner review, not principles. Each is a gesture or a
constraint that professional motion graphics depends on and that nothing in sections 1-13
covered.

### 14.1 The masked reveal (the default gesture, and it was absent)

In the earlier revision `clip-path` appeared exactly once, in the contract sentence,
`overflow` appeared nowhere, and there was no split-text, wrapper or `inset()` recipe. The
masked reveal is the single most-used device in professional kinetic type, lower thirds,
stat cards and logo builds. Its whole point is that the element has **no visible leading
edge entering the frame**, which is what separates a reveal from a slide. It is
paint-and-transform only, so it is legal under the contract, and it is the sanctioned way
to do the things the `width`/`height` ban forbids.

Two forms. The wrapper form is the workhorse:

```html
<span class="mask"><span class="inner">Revenue</span></span>
<style>
  .mask  { display: inline-block; overflow: hidden; vertical-align: bottom;
           /* room for descenders and ascender overshoot: measure the face, do not guess.
              A constant like 0.18em clips a face with a deep descender and wastes mask
              height on one without. */
           padding: 0.06em 0.05em 0.18em; }
  .inner { display: inline-block; will-change: transform; }
</style>
```

```js
// The inner travels slightly FURTHER than the mask height, so the type is still moving
// when it clears: a counter-move of about 8-12% reads as momentum rather than a lid
// lifting. (Inference.)
tl.fromTo(".inner", { yPercent: 112 }, { yPercent: 0, duration: f(14), ease: "power3.out" }, T0);
```

The clip-path form is used where there is no room for a wrapper, or where the reveal must
run diagonally:

```js
tl.fromTo("#panel", { clipPath: "inset(0 100% 0 0)" },
                    { clipPath: "inset(0 0% 0 0)", duration: f(12), ease: "power3.inOut" }, T0);
```

The distinction that matters and that no rule in this document previously drew: a mask that
**travels with the type** and a mask that **stays fixed while the type moves through it**
read completely differently. The second is the standard kinetic-type reveal. Splits (per
word, per line, per character) must be built before layout is measured, and every
build-time measurement must be gated on `await document.fonts.ready` or it measures
fallback metrics and bakes them in, silently and intermittently.

### 14.2 Per-layer motion blur, as a first-class effect

This document previously treated blur twice, as exaggeration (`motion-blur-streak`) and as
a post-render whole-frame shutter, and connected them nowhere. In After Effects motion blur
is a **per-layer switch** whose amount is derived from each layer's own velocity, so fast
layers smear within a frame and slow ones do not. A whole-frame render shutter cannot do
that: it blurs the static background along with the moving card. Professionally you use
both, and the shutter angle is a look decision made at the top of a job (180 degrees
default, 90 for hard crisp action, 270-360 for smeared or dreamy).

Under the contract, per-layer blur is a directional blur whose radius is a pure function of
progress. With position `x(t) = D e(p)`, the per-frame travel is `D e'(p) / (T fps)` and a
180-degree shutter is half of that, so one `onUpdate` on the position tween can write both:

```js
// e'(p) for the power family is (n+1)(1-p)^n. power3.out -> 4(1-p)^3.
const K = 0.5;                                   // 180-degree shutter: half the frame travel
const st = { p: 0 };
const node = document.getElementById("vel-blur");  // <feGaussianBlur>
const write = () => {
  const v = D * 4 * Math.pow(1 - st.p, 3) / (DUR * FPS);
  node.setAttribute("stdDeviation", (K * v).toFixed(2) + " 0");   // directional, x only
  gsap.set("#el", { x: -D * (1 - (1 - Math.pow(1 - st.p, 4))) });
};
write();                                          // seed frame 0
tl.fromTo(st, { p: 0 }, { p: 1, duration: DUR, ease: "none", onUpdate: write }, T0);
```

Note the substitution rule: **CSS `filter: blur()` is isotropic** and is therefore not a
motion-blur substitute. The two forms that work are an SVG `feGaussianBlur` with an
axis-weighted `stdDeviation` (above), and stacked ghost copies offset along the travel axis
at decaying opacity. Whichever is used, the blurred window must never straddle a cut.

Basis: After Effects per-layer blur defaults (shutter 180, phase -90) via
https://www.provideocoalition.com/tip_create_cinematic_motion_blur_in_after_effects_and_in_life/ ;
HF `motion-blur-streak` for the proxy pattern; the derivative is computed; `K` is inference.

One arithmetic note on the post-render shutter that this document previously got wrong by
omission. `tmix=frames=4` on a 240 fps stream averages 16.67 ms, which is the entire 60 fps
frame interval: a **360-degree** shutter, twice what any camera produces, and it reads soft
and slightly drunk. For the standard film look use `tmix=frames=2` then `framestep=4`.
Reserve the 4-frame average for a deliberately dreamy register.

### 14.3 Luminance is a motion channel

The visual system responds to luminance change well below the temporal resolution at which
it can track a displacement, which is why a single-frame flash lands and a single-frame
move does not. A 2-frame luminance pop is a legible accent where a 2-frame move is
invisible, and flash frames, exposure bumps on a hit and a hold-then-dim on a resolve are
standard accents. All of them are paint-only and therefore already legal here. This gives a
percussive register a tool it otherwise has none for.

It comes with a hard safety limit, which is the only genuinely unsafe gap this document
had: **no more than three full-frame flashes or luminance reversals in any one-second
period**, and no scrolling high-contrast striped patterns. This is WCAG 2.3.1 for web and
the equivalent broadcast guidance (ITU-R BT.1702, Ofcom) for television, and it is
enforceable rather than advisory. It is not hypothetical here: a cluster of three cuts
inside 18 frames is about 5 cuts per second, and a full-frame ground flip on each of those
is a violation. Test any strobing, flashing or hard-cut sequence against it.
Basis: https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html .

### 14.4 The blocking pass, the poster frame, and the review at 1:1

Three habits, none of which the earlier revision stated, and each of which the document's
own detectors would penalise if run at the wrong moment.

**Block first, curve later.** Time the piece with linear tweens and holds, judge the timing
alone, then apply curves. This is how the work is actually done and it is how you catch a
pacing problem before you spend effort on curves you will throw away. It matters more here
than in AE because a grader that fails linear spatial tweens rejects a blocking pass, which
means an agent cannot do the step a professional does first. Grade the two passes
differently.

**Every beat must contain at least one frame that works as a still.** That is what staging
means to a client, and it is trivially checkable against the settled window (M10) the
harness already computes.

**Review at full speed, then half speed, then frame by frame, on the render at 1:1.** The
four things the numbers do not catch, all four of which were present in this document's own
recipes before this revision: text softening under scale (layer promotion), edge shimmer on
slow tails (sub-pixel rest), shadow detachment, and doubled perspective.

**And grade the delivered file, not only the frame dump.** The low-amplitude motions this
document prescribes (a moving hold at scale 1.00 to 1.012, decorative opacity 12-25%,
ambient at 10-20% of element size) sit at or below what H.264 preserves on a flat surface
at typical social bitrates: a breathe that grades clean on PNGs can be quantised out of the
delivered file entirely. The standard fix for the banding that section 12(b) bans by
prohibition is 1-2% grain or dither, which also gives the encoder something to hold onto.
Check `pix_fmt`, `color_range` and `color_primaries` on the muxed file as well: a
limited-range render tagged full crushes the whole piece. (Inference; standard delivery
practice.)

---

## Appendix A. Computed ease and overshoot tables

Script: `ease_tables.py` (this session). Formulas: GSAP's back ease from the 3.14.2 source,
`easeOut(p) = (p-1)^2 * ((s+1)(p-1) + s) + 1`, default `s = 1.70158`
(https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.js, `_configBack`); power eases
`1 - (1-p)^(n+1)`; `expo.out` `1 - 2^(-10p)`; damped-spring step-response overshoot
`exp(-z pi / sqrt(1 - z^2))` (standard second-order result). These are computed, not
sourced from a design guide.

### back.out(s): overshoot and where the reversal sits

| s | overshoot | reversal at (fraction of duration) |
| --- | --- | --- |
| 0.5 | 0.8% | 0.78 |
| 1.0 | 3.7% | 0.67 |
| 1.2 | 5.3% | 0.64 |
| 1.4 | 7.1% | 0.61 |
| 1.7 (default 1.70158) | 10.0% | 0.58 |
| 2.0 | 13.2% | 0.56 |
| 2.5 | 18.9% | 0.52 |
| 3.0 | 25.0% | 0.50 |
| 4.0 | 37.9% | 0.47 |

### Damped spring: overshoot by damping fraction

| zeta | first overshoot | second excursion (overshoot squared) |
| --- | --- | --- |
| 0.50 | 16.3% | 2.7% (visible as a second reversal above a 2% floor) |
| 0.55 | 12.6% | 1.6% |
| 0.60 | 9.5% | 0.9% |
| 0.65 | 6.8% | 0.5% |
| 0.70 | 4.6% | 0.2% |
| 0.75 | 2.8% | 0.1% |
| 0.80 | 1.5% | ~0 |
| 0.85 | 0.6% | ~0 |
| 0.90 | 0.15% | ~0 |
| 1.00 | 0 | 0 |

These agree with HF's Spring Eases table (0.80-0.85 "~1-1.5%", 0.60-0.70 "~5-10%",
< 0.55 "> 12%").

### Ease-out families: front-loading and peak velocity

Fraction of travel complete at 25%, 50%, 75% of duration; peak step / mean step; frames
still more than 1% from rest in a 16-frame tween.

| ease | @25% | @50% | @75% | peak/avg velocity | frames moving of 16 |
| --- | --- | --- | --- | --- | --- |
| linear | 25.0% | 50.0% | 75.0% | 1.00 | 15 |
| sine.out | 38.3% | 70.7% | 92.4% | 1.57 | 14 |
| power1.out | 43.8% | 75.0% | 93.8% | 2.00 | 14 |
| power2.out | 57.8% | 87.5% | 98.4% | 3.00 | 12 |
| power3.out | 68.4% | 93.8% | 99.6% | 4.00 | 11 |
| power4.out | 76.3% | 96.9% | 99.9% | 5.00 | 10 |
| expo.out | 82.3% | 96.9% | 99.4% | 6.92 | 10 |
| power2.inOut | 6.2% | 50.0% | 93.8% | 3.00 | 13 |

Per-frame steps for a 100px, 15-frame (0.5s at 30fps) tween, first four and last four
frames:

| ease | first four steps (px) | last four steps (px) |
| --- | --- | --- |
| linear | 6.7, 6.7, 6.7, 6.7 | 6.7, 6.7, 6.7, 6.7 |
| sine.out | 10.5, 10.3, 10.1, 9.8 | 3.8, 2.7, 1.6, 0.5 |
| power1.out | 12.9, 12.0, 11.1, 10.2 | 3.1, 2.2, 1.3, 0.4 |
| power2.out | 18.7, 16.2, 13.9, 11.8 | 1.1, 0.6, 0.2, 0.0 |
| power3.out | 24.1, 19.5, 15.5, 12.0 | 0.3, 0.1, 0.0, 0.0 |
| power4.out | 29.2, 21.9, 16.1, 11.6 | 0.1, 0.0, 0.0, 0.0 |
| expo.out | 37.0, 23.3, 14.7, 9.3 | 0.2, 0.1, 0.1, 0.1 |
| power2.inOut | 0.1, 0.8, 2.3, 4.4 | 4.4, 2.3, 0.8, 0.1 |

Two things to read off this. First, the "abrupt stop" of a linear tween is a 6.7px final
step where every eased family ends below 0.5px; that is the whole content of "slow out".
Second, on **first-frame travel**: `expo.out` and `power4.out` on a 100px move at 30fps
step 29-37px on frame one. Whether that strobes depends on frame width, contrast and
whether the element is still fading in. At 1920 wide it is 1.5-1.9% of frame width, above
the ~0.5% guideline, so a fast slam on high-contrast type at 1080p wants a shutter or a
directional blur. At 3840 the same tween is under 1% and usually will not. The earlier
version of this paragraph applied an absolute 5-10px threshold and concluded that nearly
every eased entrance at 1080p needs a shutter, which is not how anything is delivered.

## Appendix B. Sources

Local (read in full):

- `<skills>/motion-design/director/disney-principles.md` (LottieFiles, MIT)
- `<skills>/motion-design/director/choreography.md`
- `<skills>/motion-design/reference/timing-easing-tables.md`
- `<skills>/motion-design/reference/quality-checklist.md`
- `<skills>/motion-design/reference/troubleshooting.md`
- `<skills>/motion-design/reference/property-selection.md`
- `<skills>/motion-design/SKILL.md`
- HyperFrames skills bundle (Apache-2.0, HeyGen): `hyperframes-animation/SKILL.md`,
  `rules-index.md`, `techniques.md`, `transitions/overview.md`,
  `adapters/gsap.md`, `adapters/gsap-easing-and-stagger.md`,
  `adapters/gsap-timeline-and-labels.md`, `adapters/gsap-transforms-and-perf.md`,
  `rules/spring-pop-entrance.md`, `rules/press-release-spring.md`,
  `rules/physics-press-reaction.md`, `rules/reactive-displacement.md`,
  `rules/nudge-curve.md`, `rules/waterfall-entry.md`, `rules/motion-blur-streak.md`;
  `hyperframes-creative/references/motion-principles.md`, `beat-direction.md`,
  `video-composition.md`, `typography.md`
- `<skills>/manifesto/SKILL.md`
- `<skills>/manifesto/scripts/grade-original.py`

Web:

- Twelve basic principles of animation, Wikipedia (summarizing Thomas and Johnston, *The
  Illusion of Life*, 1981): https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation
- Squash and stretch, Wikipedia: https://en.wikipedia.org/wiki/Squash_and_stretch
- Bloop Animation, The 12 Principles of Animation: https://www.bloopanimation.com/the-12-principles-of-animation/
- Interaction Design Foundation, Laia Tremosa, UI Animation: How to Apply Disney's 12
  Principles of Animation to UI Design:
  https://ixdf.org/literature/article/ui-animation-how-to-apply-disney-s-12-principles-of-animation-to-ui-design
- GSAP 3.14.2 source (ease formulas and defaults): https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.js
- GSAP ease documentation: https://gsap.com/docs/v3/Eases/
- Material Design 3 motion tokens, as mirrored by mdui (the m3.material.io token page did
  not return content when fetched): https://www.mdui.org/en/docs/2/styles/design-tokens
- Made Good Designs, Motion Design Principles Explained. **Read via search summary only,
  and therefore NOT cited for any number in this document.** The "200-500ms interface
  transition band" and the "elements overshoot slightly on arrival" line that were
  previously attributed to it have been dropped: a search summary is not a source for a
  figure. https://madegooddesigns.com/motion-design-principles/
- Issara Willenskomer, Creating Usability with Motion: The UX in Motion Manifesto (12
  UX-in-motion principles: easing, offset and delay, parenting, transformation, value
  change, masking, overlay, cloning, obscuration, parallax, dimensionality, dolly and
  zoom; the article itself returned 403 and was read via search summaries). **Cited for
  the taxonomy of its twelve UX-in-motion principles only, never for a number.**
  https://medium.com/ux-in-motion/creating-usability-with-motion-the-ux-in-motion-manifesto-a87a4584ddc

Not obtained, and therefore not cited for numbers: the text of *The Illusion of Life*
itself; Richard Williams, *The Animator's Survival Kit* (its timing charts would give
canonical frame counts for anticipation and squash; searches returned only summaries);
Apple Human Interface Guidelines, Motion (403 on fetch).
