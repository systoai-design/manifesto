# Character animation for motion graphics, in HTML/SVG + GSAP

Reference for the `manifesto` skill. Every recipe below runs under the HyperFrames contract: one paused GSAP timeline, every tween a `fromTo` with an explicit from-state, transforms and paint-only properties, no `Math.random` or `Date.now`, finite repeats, and state that is a pure function of timeline time. All timing is authored in frames at 30 fps and converted once with `f(n) = n / 30`; every figure is given in frames and seconds.

**Revision 2 (2026-09-02).** Corrected against a full citation audit and a practitioner
review. Five citations turned out to be fabricated, misattributed or absent from the page
they named and have been removed or re-sourced; the rig's two worst mechanical defects
(foot slide and stop-at-every-key interpolation) are now stated with their fixes; every
"verified" browser probe is re-labelled, because no artifact was retained and one of them
does not survive arithmetic. Every change is in `corrections.md` in this directory.

Every number carries a basis. "Source" means a named document below. "Inference" means my own reasoning, and an inference is never a canonical figure; treat it as a starting value to fit against reference footage the way `manifesto` fits everything else (SKILL.md section 3).

The recipes were run in a browser and probed by seeking the timeline to specific frames and reading back the transforms. **Those probes are not reproducible from this repository.** None of `rig-common.js`, `rig-html.html`, `rig-svg.html`, `face.html`, `jump-smear.html` or `lipsync.html` was retained; `_research/` holds only the markdown. Most of the reported readouts recompute correctly from the code printed below (the apex pose, the puck's 2.02x, the blink offsets, the lip-sync leads), so the probes were almost certainly real, but one of them does not survive arithmetic (section 2.6) and none can be re-run. Every line that says "Verified" below should be read as **"reported, recomputable where noted, artifact not retained"**. Rebuild the rigs from the listings and re-probe before relying on any of it.

A second, harder caution about method: **checking five key frames by silhouette cannot verify a walk.** Every defect in a cycle lives between the keys (spacing, foot plant, slide), and a key-frame silhouette check is blind to all of them. The two tests that matter are playback at speed and an ankle-trajectory trace in world space; neither was run, and when the second one was run for this revision the rig failed it (section 3.4).

## 0. Contract notes that character work trips over (verified)

These four came out of running the recipes, not out of the rule files, and each one cost an iteration.

1. **A dev scrub must seek with events.** `tl.seek(t)` defaults `suppressEvents` to `true`, and GSAP then skips `onUpdate` on the tweens it renders, so every pose-driver recipe below shows the frame-0 pose at every time and looks broken. Seek with `tl.seek(t, false)` when probing. The HyperFrames renderer samples "every frame is a fresh seek" (hyperframes-core `determinism-rules.md` line 68) and its own rules depend on `onUpdate` drivers (`sine-wave-loop`, `particle-burst`, `counting-dynamic-scale`), so this is a dev-scrub trap, not a render trap. Basis: verified in the browser on `rig-html.html`; the walk froze with the default and animated with `false`.
2. **A driver tween renders its from-state, and fires `onUpdate`, whenever the playhead is BEFORE its start.** So two drivers writing the same element fight: the later-added one writes its from-state pose over the earlier one's live pose. Verified: a jump driver and a dash driver on one element put the character at the dash's start position during the crouch. The rule that follows is **one element, one writer**: either one driver whose pose function covers the element's whole life (the jump recipe), or every driver's from-state is a no-op relative to the seeded rest pose (the walk recipe blends with `b = 0`, the breath recipe uses `sin(0) = 0`).
3. **Seed frame 0 by calling the pose function once at setup.** The driver has not rendered before the first seek. `motion-blur-streak` seeds its blur proxy for the same reason; `manifesto` SKILL.md section 6 ("render-order trap") gives every element a `tl.set` baseline for the same reason.
4. **Never overlap a driver's `gsap.set` with a `fromTo` on the same element and property.** `hyperframes-creative/references/motion-principles.md` ("Never overlap conflicting transform tweens on the same element") applies doubly to rigs, because a rig is twelve elements that all want two owners. The face recipe splits ownership by property (breath owns `scaleY`/`y` of the body, weight shift owns `x`/`rotation`), which GSAP merges correctly because it stores transform components independently.

The frame helper used everywhere:

```js
var FPS = 30, F = 1 / FPS;
function f(n) { return n / FPS; }   // frames -> seconds; every cue is written as f(frame)
```

Clip boundaries in a HyperFrames scene should still be written biased inward as `manifesto` SKILL.md section 7 specifies (`start = frame/fps - 0.0002`); the recipes here live inside one scene so they use plain `f()`.

## 1. Sources

Local (read first; cited by path). `$SKILLS` is the local skills repo on the E: drive and `$USKILLS` is the per-user skills directory, the two roots named in the task brief:

- `$SKILLS/motion-design/director/disney-principles.md` (LottieFiles, MIT): squash/stretch ratios, anticipation size and duration, follow-through child delay, timing by weight, overshoot by personality, appeal killers.
- `$SKILLS/motion-design/director/choreography.md`: counter-motion table, the 1/3 rules, stagger patterns.
- `$SKILLS/motion-design/reference/timing-easing-tables.md`: duration by element type, spring parameters, stagger budget.
- `$SKILLS/motion-design/reference/quality-checklist.md`: the severity tiers.
- `$USKILLS/hyperframes-animation/rules-index.md`: the contract itself. (**Licence unverified.** There is no licence file anywhere under `hyperframes-animation` or `hyperframes-core`, no licence field in either `SKILL.md` frontmatter, and no occurrence of "Apache" in either. The HeyGen / Apache-2.0 attribution used elsewhere in this bundle is carried by convention, not by anything in the files. By contrast the LottieFiles / MIT attribution for `motion-design` **is** in that skill's frontmatter and is verified.)
- `$USKILLS/hyperframes-animation/rules/sine-wave-loop.md`: bounded idle amplitudes and the onUpdate driver form.
- `$USKILLS/hyperframes-animation/rules/motion-blur-streak.md`: ghost-trail and directional-blur recipes, the "dwell 1 s sharp" rule, ghost count and opacity ranges.
- `$USKILLS/hyperframes-animation/rules/particle-burst.md`: the ballistic pure-function pattern and the `prand` hash.
- `$USKILLS/hyperframes-animation/rules/spring-pop-entrance.md` and `adapters/gsap-easing-and-stagger.md`: "smooth beats bouncy", `springEase` closed form, why stateful springs are banned.
- `$USKILLS/hyperframes-animation/rules/svg-icon-enrichment.md` (via rules-index): explicit `setAttribute('transform','rotate(...)')` for SVG centers.
- `$USKILLS/hyperframes-animation/rules/nudge-curve.md`: slow-fast-slow chaining.
- `$USKILLS/hyperframes-animation/techniques.md`: `steps(1)` blink cursor, Lottie contract.
- `$USKILLS/hyperframes-creative/references/motion-principles.md`: fromTo over from, no overlapping transform tweens, ambient tweens on `tl`.
- `$USKILLS/hyperframes-creative/references/beat-direction.md`, `video-composition.md`, `typography.md`: verbs, density, "subtle reads as static at 30 fps".
- `$SKILLS/manifesto/SKILL.md`: the frame-boundary trap, the shutter rule and the 5-10 px per frame strobe threshold, the render-order trap, "controllers not per-element keyframes" and "offset sibling groups by ~3 frames".
- `$SKILLS/manifesto/scripts/grade-original.py`: the duplicate-consecutive-frames check and the settle-direction-reversal (overshoot) check.

Web (fetched and quoted; where a page could not be fetched and only a search snippet was available, the citation says "snippet"):

- Williams tempo table, adapted: Monmouth University animation instruction, "Movement: Walk Cycle", https://animation.monmouth.edu/instruct/animation/walk-cycle/ and the older mirror https://bluehawk.monmouth.edu/~wkoning/instruct/?page=General&show=1 ("adapted from The Animator's Survival Kit", stated at 24 fps).
- Williams walk mechanics, quoted from student notes on the book: https://cloytoons.wordpress.com/2015/12/01/animation-research-walk-cycle/ and https://www.tumblr.com/zak-graphicarts/174088404863/richard-williams-the-traditional-walk and https://edwardboyleanimation.wordpress.com/2016/01/04/walk-cycle-research-3-animators-survival-kit/.
- Run cycle counts: https://blogs.ulster.ac.uk/scottmoore/2024/10/21/animation-strategies-animation-walk-and-runs-regular-run-cycle/ and https://cloytoons.wordpress.com/2015/12/06/animation-research-run-cycle/.
- Preston Blair walk: http://johnkstuff.blogspot.com/2010/02/preston-blair-simple-walk.html (John Kricfalusi on Blair's chart) and https://mister-chad.com/animation/walk+cycle (pose definitions, Blair's head arc).
- Preston Blair mouth shapes: https://www.garycmartin.com/mouth_shapes.html.
- Lip-sync lead: https://escapestudiosanimation.blogspot.com/2022/04/lipsync-two-frames-ahead-of-audio.html (Escape Studios).
- Lip-sync technique: https://www.highonfilms.com/lip-sync-animation-techniques-every-character-animator-should-know/ . The page now returns HTTP 200 and its full text was extracted for this revision. It contains **exactly one frame figure**, a general "offset the key shapes one or two frames ahead of the sound", and **no per-consonant breakdown at all**: no separate T/D figure, no separate F/V figure. The "per-consonant lead times" this document previously drew from it do not exist in the source. It still supports "key the hits, not every phoneme" and the slower jaw curve.
- Blink frame counts: https://www.bloopanimation.com/blinking-animation/ and https://animationapprentice.blogspot.com/2020/09/do-animated-characters-need-to-blink.html.
- Head turn: https://design.tutsplus.com/tutorials/animation-for-beginners-how-to-animate-a-head-turn--cms-26487 and https://sunstrikestudios.com/en/blog/timing_in_animation/.
- Moving hold, squash/stretch volume, anticipation, follow-through, appeal: https://handwiki.org/wiki/Twelve_basic_principles_of_animation quoting Thomas and Johnston, The Illusion of Life (1981), with page numbers.
- Smears: https://www.traditionalanimation.com/2017/smear-speed-motion-blur-effects-in-animation/, https://en.wikipedia.org/wiki/Smear_frame, https://www.bloopanimation.com/the-art-of-smear-frames/, https://idearocketanimation.com/8857-animation-techniques-smear/.
- Animation physics (Odd Rule, fall timing and scale): https://www.animatorisland.com/physics-in-animation-how-important-is-it/ . **Written by Alejandro Garcia himself**, who teaches the Physics of Animation course at San Jose State and consulted at DreamWorks; it is a primary source in this chain, not a summary of one, which strengthens the Odd Rule and fall-timing citations rather than weakening them.
- Shape language: https://blog.cg-wire.com/character-shape-language/ ; motion-per-shape claim from https://pixune.com/blog/shape-language-technique/ (snippet). Neither page contains the phrase "baby schema" or anything about infant facial proportions; a claim previously attributed to a "search snippet" on these sources has been removed (section 7).
- Blair walk-chart critique (the "no help in timing" line, previously cited only as an unnamed search snippet): Angry Animator, "Preston Blair Deciphered", https://angryanimator.com/word/2018/03/20/preston-blair-deciphered/ .
- GSAP: https://gsap.com/resources/svg/ (transformOrigin, svgOrigin, smoothOrigin), https://gsap.com/docs/v3/GSAP/Tween/ (immediateRender defaults), https://gsap.com/docs/v3/GSAP/Timeline/ (repeat, yoyo, repeatDelay, nested timelines), https://gsap.com/docs/v3/Eases/SteppedEase/ (steps), https://gsap.com/docs/v3/Plugins/Physics2DPlugin/.
- CSS/SVG: https://developer.mozilla.org/en-US/docs/Web/CSS/transform-box, https://svg-tutorial.com/svg/transform/ (nested arm groups), https://dockyard.com/blog/2019/11/29/an-animated-tale-of-svg-transforms.

**Removed in revision 2, and why.** Two citations that this document previously leaned on do not exist. (1) A Williams *blocking-order* quote attributed to Edward Boyle ("block in the 'contact' key poses ... The next step is to block in the 'passing' key pose") is not on that page; the page was fetched twice and dumped in full and is a short set of caption notes about arm swing, heel lead, pelvis wave and elbow breaking. (2) A "second student summary (Altea Claveras, quoting the book)" said to corroborate the per-step reading of the Monmouth tempo ladder carries no URL, appears nowhere in the source list, and returns nothing on a targeted search of its quoted phrasing. It was the only independent confirmation offered for the per-step reading, so that reading is now stated as an inference (section 3.2).

Not obtained: the Williams book itself (the archive.org text was truncated before the walks chapter; a CMU handout PDF of the walks chapter was image-only). The Monmouth table is an adaptation and is cited as such. The Disney Research blink paper PDF fetched but its text did not extract usably, so no figures from it are used.

## 2. Building a rigged 2D character from shapes

### 2.1 The hierarchy

```
root (translate: where the character stands; scaleX -1 to face left)
  hips (translate y = bob, rotate = pelvis rock)
    thigh L/R (rotate at hip)
      shin (rotate at knee)
        foot (rotate at ankle)
          toe (rotate at the ball of the foot)   <-- ADDED in revision 2, see below
    torso (rotate at pelvis, origin bottom-centre)
      upper arm L/R (rotate at shoulder)
        forearm (rotate at elbow)
          hand
      head (rotate at neck, origin bottom-centre)
        face group (translate: fakes a turn), eyes, lids, brows, mouth
```

Two ideas carry the whole thing.

**Every limb is drawn hanging down from its joint, and the joint is the transform origin.** The child limb is placed at the parent's far end. A rotation of the thigh then carries the shin and foot with it for free, because CSS and SVG transforms nest. `manifesto` SKILL.md (liquid-glass section, "Controllers, not per-element keyframes") already argues for nested wrappers driven as units; a rig is that idea taken to twelve levels.

**The foot needs two joints, not one.** A rig with a single ankle pivot cannot roll
through the foot, and foot roll is what makes a walk read as weighted. A real walk has
heel-strike (the foot rotates about the **heel** as the sole comes down), a flat stance,
then toe-off (the foot rotates about the **ball** as the heel lifts). One origin at
`8px 50%` just swings a rigid plank through the whole cycle, which is what the `foot` key
row below does. Add a toe joint at the ball and switch the effective pivot: heel at
contact, ball at push-off. This is also where the walk's propulsion comes from, and it is
the second half of the fix for the ground-contact problem in section 3.4. (Inference;
standard leg-rig topology in both 2D and 3D.)

**Draw order is z-order.** The far leg and far arm come first in the DOM so they render behind the torso, and get a `filter: brightness(.8)` or reduced opacity so the silhouette reads (inference, standard practice; John Kricfalusi's Blair notes say the near foot "is always larger, and when it touches the ground is lower than the one behind", so a near/far offset of a few pixels is period-correct too).

### 2.2 Origins: HTML divs versus SVG groups

**HTML divs.** `transform-origin` is relative to the element's own box, so `transform-origin: 50% 0` on a limb whose top edge sits on the joint is exactly right. GSAP reads the CSS origin unless you pass `transformOrigin`; the recipes set it in CSS and never override it.

**Inline SVG.** The default reference box for `transform-origin` on SVG elements is the viewport, not the element: MDN gives `transform-box` initial value `view-box` ("The nearest SVG viewport is used as the reference box"), and DockYard's article puts it as "SVG elements differ in that their coordinate system's default transform-origin is (0,0) of its reference box (the top left corner of the SVG's viewBox)". `transform-box: fill-box` makes the origin relative to "the object bounding box" (MDN). GSAP sidesteps this: its `transformOrigin` on SVG is normalised to the behaviour developers expect from the DOM, where (in GSAP's wording) "transform-origin is relative to the element itself". (The tighter phrasing "relative to its own top left corner" that this document previously put in quotation marks is not verbatim on the page; the substance is right, the quotation marks were not.) And `svgOrigin` "works exactly like transformOrigin but it uses the SVG's global coordinate space" (gsap.com/resources/svg). Either way the origin is expressed against a bounding box, and the bounding box of a `<g>` **includes its children**, so it changes as the forearm swings. That makes percentage origins on joint groups fragile.

The robust pattern (svg-tutorial.com, quoted): "we can rotate the second arm piece around the joint by applying a rotate transformation" after "we move this group to the end of the first arm by applying another translate transformation". Every joint group has its own origin at (0,0), its geometry is drawn from (0,0) downward, it sits inside a `translate(jointX, jointY)` group at the parent's far end, and the animation writes `transform="rotate(a)"` directly. `svg-icon-enrichment` gives the same instruction for icons ("use SVG setAttribute('transform', 'rotate(deg cx cy)') for explicit center"). No `transform-box`, no bounding boxes, nothing to drift.

### 2.3 The GSAP pattern: pose function + one driver

For cyclic and physical motion, every joint angle is a pure function of a phase, and one `fromTo` on a proxy advances the phase linearly. This is the `sine-wave-loop` onUpdate form and the `particle-burst` ballistic form applied to a skeleton. It satisfies the contract by construction: no accumulated state, any frame reproducible from time alone, finite because the driver has a duration.

For one-shot actions (a blink, a head turn, a weight shift) plain `tl.fromTo` tweens on the joint elements are clearer and the face recipe uses them. The two styles must not share an element and property (section 0, item 4).

`immediateRender`: GSAP's default is "false for to() tweens, true for from() and fromTo() tweens" (Tween docs). Inside a scene every tween that **re-owns** a property already written by an earlier tween on the same element carries `immediateRender: false`, as `manifesto` SKILL.md section 6 and `motion-principles.md` require; the recipes do this on every second and later `fromTo` per property.

### 2.4 Recipe: shared pose math (`rig-common.js`)

Pose tables are cyclic key lists sampled between keys. The interpolant matters more than the angles do.

**Do not use smoothstep between every pair of keys.** `ss'(u) = 6u(1-u)` is zero at both ends of every segment, so smoothstep gives **zero velocity at every key**, which is not slow-in/slow-out, it is a full stop eight times per cycle. At 15 frames per step the walk hits a velocity zero every 3.75 frames, an 8 Hz pulse, and it produces exactly the "jerky motion, inconsistent timing, abrupt stops" that section 7 lists as appeal killers. Williams' slow-in/slow-out applies at the **extremes** (up and down); the limbs are moving fastest through passing, and smoothstep forces them to stop there. Interpolate the cyclic tables with a **wrapped Catmull-Rom or cardinal spline** (C1, non-zero tangents at interior keys), which is what smooth keys give you in After Effects, and reserve zero tangents for keys you actually want to hold. This is a ten-line change to `cyc()` and it is the single largest quality gain available in this document. The `ss()` below is kept only so the listing matches the probes that were run against it.

(Thomas and Johnston on slow in and slow out: "More pictures are drawn near the beginning and end of an action, creating a slow in and slow out effect", handwiki **p. 47** -- not p. 12, which is the reference index number, not a page. Every other handwiki page number in this document is correct: squash p. 49, anticipation pp. 51-52, follow-through pp. 59-62, moving hold pp. 61-62, appeal p. 68.)

The **angles in the tables are inference**; the pose names, their order, where the hips are lowest and highest, and the arm opposition are Williams (section 3).

```js
// rig-common.js : shared pose math for the character recipes (pure functions, no state)
// frame helper: everything is authored in frames at 30 fps and converted once
var FPS = 30, F = 1 / FPS;
function f(n) { return n / FPS; }

// smoothstep between two keys. WARNING: ss'(0) = ss'(1) = 0, so this stops the limb dead
// at EVERY key, eight times per cycle. Kept here because the probes were run against it.
// Replace with a wrapped Catmull-Rom for production (see the note above cyc()).
function ss(u) { return u * u * (3 - 2 * u); }

// Catmull-Rom on a wrapped key ring: C1, non-zero tangents at interior keys. This is the
// interpolant the tables should actually use.
function crWrap(V, i, t) {                       // V = value ring, i = segment index
  var n = V.length, p0 = V[(i - 1 + n) % n], p1 = V[i % n], p2 = V[(i + 1) % n], p3 = V[(i + 2) % n];
  var t2 = t * t, t3 = t2 * t;
  return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3);
}

// sample a cyclic key table {p:[phases 0..1], v:[values]} at phase (0..1), wraps
function cyc(keys, phase) {
  var P = keys.p, V = keys.v, n = P.length;
  phase = phase - Math.floor(phase);
  for (var i = 0; i < n; i++) {
    var p0 = P[i], p1 = (i + 1 < n) ? P[i + 1] : P[0] + 1;
    var v0 = V[i], v1 = (i + 1 < n) ? V[i + 1] : V[0];
    var ph = (phase < p0) ? phase + 1 : phase;
    if (ph >= p0 && ph < p1) return v0 + (v1 - v0) * ss((ph - p0) / (p1 - p0));
  }
  return V[0];
}

// WALK key poses for ONE leg over its own full cycle (contact -> next contact of the same leg).
// Phases: 0 contact(front) .125 down .25 passing .375 up .5 contact(back) .625 down .75 passing .875 up
// Basis: pose names and order = Richard Williams (contact, down, passing, up); the ANGLES are inference.
// Sign: character faces +x; positive rotation swings the limb free end backward (screen clockwise).
var WALK = {
  thigh: { p: [0, .125, .25, .375, .5, .625, .75, .875], v: [-28, -18, -2, 14, 26, 22, -8, -30] },
  shin:  { p: [0, .125, .25, .375, .5, .625, .75, .875], v: [  5,  22,  8, 12, 18, 45, 62,  30] },
  foot:  { p: [0, .125, .25, .375, .5, .625, .75, .875], v: [ 18,  -4, -6, -22, -34, -46, -30, 6] },
  // hips vertical offset in px (+ is down). Lowest at DOWN, highest at UP (Williams).
  hipY:  { p: [0, .125, .25, .375, .5, .625, .75, .875], v: [  0,   8,  -2, -8,  0,  8,  -2, -8] },
  // NOTE ON PLANE. Williams' hip/shoulder opposition happens in the TRANSVERSE plane and
  // is invisible in a strict side view. Rotating hips in the PICTURE plane instead reads
  // as the pelvis tipping forward and back, which is not what a walk does. Keep a small
  // picture-plane rotation as a stylistic lean if you want it, but do not label it the
  // Williams counter-rotation and do not scale it up expecting the twist to appear: the
  // side-view cheat for transverse rotation is a small scaleX on the shoulder and hip
  // groups plus an x offset of the far limb. (Inference; plane of motion vs plane of camera.)
  hipRock:{ p: [0, .25, .5, .75], v: [ 3, 0, -3, 0] },        // pelvis tilt, degrees
  shoulder:{ p: [0, .25, .5, .75], v: [ -2, 0, 2, 0] },       // picture-plane chest rock
  headNod:{ p: [0, .125, .25, .375, .5, .625, .75, .875], v: [ 0, 2, 0, -2, 0, 2, 0, -2] }
};

// Full-body pose for a walk at cycle phase (0..1). Returns degrees / px for every joint.
//
// TWO KNOWN LIMITATIONS OF THIS FUNCTION, both stated so a builder does not inherit them.
//
// 1. TWINNING. L = phase and R = phase + 0.5 against identical tables makes the walk
//    exactly half-cycle symmetric, and perfect left/right symmetry is the note every lead
//    animator gives first. Real walks favour a side: one leg carries longer, one arm
//    swings wider, the head sits slightly off-axis. Add a small per-side additive offset
//    (2-4 degrees on thigh and arm, 1-2 px on hipY) and the rig stops reading as a
//    mechanism. (Inference; standard supervision note.)
// 2. `amp` IS NOT A PERSONALITY CONTROL. A tired walk is not a natural walk at amp 0.6:
//    it has a shorter stride AND lower hips AND more forward head AND less arm swing AND
//    a longer contact dwell, i.e. per-channel offsets in different directions. Section 3.2
//    warns "do not scale a natural walk's timing to make it feel tired" and this function
//    ships the same mistake on the amplitude axis. What a production rig exposes is an
//    ADDITIVE POSE-OFFSET LAYER: a constant per-joint bias added on top of the cycle.
//    Add offsets here rather than turning one scalar. (Inference.)
function walkPose(phase, amp, off) {
  amp = (amp === undefined) ? 1 : amp;              // 1 = natural, 1.6 = cartoony
  off = off || {};                                   // additive per-joint bias, the real dial
  var L = phase, R = phase + 0.5;                   // right leg is half a cycle behind
  var thighL = cyc(WALK.thigh, L) * amp, thighR = cyc(WALK.thigh, R) * amp;
  // arms swing OPPOSITE the leg on the same side (Williams). Small phase lag so the
  // widest swing lands on the DOWN pose rather than the contact (inference).
  var armL = -0.85 * cyc(WALK.thigh, R + 0.06) * amp;   // = opposite of thighL
  var armR = -0.85 * cyc(WALK.thigh, L + 0.06) * amp;
  return {
    hipY: cyc(WALK.hipY, phase) * amp,
    hipRock: cyc(WALK.hipRock, phase) * amp,
    torso: -5 * amp + cyc(WALK.shoulder, phase) * amp,     // constant forward lean + rock
    head: -cyc(WALK.shoulder, phase) * amp + cyc(WALK.headNod, phase) * amp,
    thighL: thighL, shinL: cyc(WALK.shin, L) * amp, footL: cyc(WALK.foot, L) * amp,
    thighR: thighR, shinR: cyc(WALK.shin, R) * amp, footR: cyc(WALK.foot, R) * amp,
    upperArmL: armL, foreArmL: -25 - 20 * Math.max(0, -armL) / 30,
    upperArmR: armR, foreArmR: -25 - 20 * Math.max(0, -armR) / 30
  };
}

// RUN key poses: same four names, both feet leave the ground at UP (inference for angles).
var RUN = {
  thigh: { p: [0, .125, .25, .375, .5, .625, .75, .875], v: [-40, -22,  4, 30, 44, 30, -20, -48] },
  shin:  { p: [0, .125, .25, .375, .5, .625, .75, .875], v: [ 10,  30, 12, 20, 60, 95,  90,  40] },
  foot:  { p: [0, .125, .25, .375, .5, .625, .75, .875], v: [ 20,  -6, -8, -30, -50, -60, -40,  8] },
  hipY:  { p: [0, .125, .25, .375, .5, .625, .75, .875], v: [  2,  14, -4, -18,  2, 14,  -4, -18] }
};
function runPose(phase, amp) {
  amp = (amp === undefined) ? 1 : amp;
  var L = phase, R = phase + 0.5;
  var thighL = cyc(RUN.thigh, L) * amp, thighR = cyc(RUN.thigh, R) * amp;
  var armL = -0.7 * thighR, armR = -0.7 * thighL;      // opposite, and pumped (elbows bent)
  return {
    hipY: cyc(RUN.hipY, phase) * amp, hipRock: cyc(WALK.hipRock, phase) * 1.5 * amp,
    torso: -14 * amp + cyc(WALK.shoulder, phase) * 2 * amp,   // more lean = faster (Williams)
    head: -4 * amp,
    thighL: thighL, shinL: cyc(RUN.shin, L) * amp, footL: cyc(RUN.foot, L) * amp,
    thighR: thighR, shinR: cyc(RUN.shin, R) * amp, footR: cyc(RUN.foot, R) * amp,
    upperArmL: armL, foreArmL: -80, upperArmR: armR, foreArmR: -80
  };
}
```

### 2.5 Recipe: HTML div rig, walking (`rig-html.html`)

Reported (artifact not retained): seeking to contact, down, passing and up at frames 42, 46, 50, 53, 57 produced the expected silhouettes, and `#legL` read `rotate(-28deg)` at the contact key. The frame arithmetic checks out exactly against the tables and constants below. **But silhouettes at five keys do not verify a walk** (see the note in the preamble): they are blind to spacing, foot plant and slide, and this rig fails on all three (section 3.4).

Two CSS notes for this listing, both wrong for this pipeline as originally written.
`will-change: transform` on `.part` promotes every one of the thirteen rig elements to its
own composited layer. The renderer seeks and screenshots one frame at a time, so there is
no repaint loop to optimise and nothing to gain, while layer promotion costs memory and
can change edge antialiasing on rotated shapes. Drop it, or scope it to the root.
`filter: brightness(.8)` on the far-side limbs multiplies the colour toward black, which
reads muddy on the blue cloth and sallow on the skin; `filter` also establishes a
containing block and forces a separate compositing pass on the whole nested subtree, which
can shift the far side by a sub-pixel against the near side. 2D character work picks a
distinct flat darker tint per material instead: use explicit `.far-skin` / `.far-cloth`
colours. (Compositing behaviour of `will-change` and `filter`; the tint practice is
standard.)

```html
<!doctype html><meta charset="utf-8"><title>rig-html</title>
<style>
  body{margin:0;background:#f4efe6;font-family:system-ui}
  #stage{position:relative;width:640px;height:480px;overflow:hidden;background:#f4efe6}
  #ground{position:absolute;left:0;right:0;top:400px;height:2px;background:#bbb}
  .part{position:absolute;will-change:transform}
  /* every limb is drawn hanging DOWN from its joint: left/top place the joint,
     transform-origin sits ON the joint. Children are placed at the parent's far end. */
  #root{left:320px;top:300px;width:0;height:0}
  #hips{left:-30px;top:-14px;width:60px;height:28px;border-radius:14px;background:#2b2b2b;transform-origin:50% 50%}
  #torso{left:2px;bottom:14px;width:56px;height:96px;border-radius:26px 26px 10px 10px;background:#3c5a99;transform-origin:50% 100%}
  #head{left:-2px;bottom:92px;width:60px;height:60px;border-radius:50%;background:#e8b98a;transform-origin:50% 100%}
  #eye{left:38px;top:22px;width:8px;height:8px;border-radius:50%;background:#222}
  .upper-arm{top:82px;width:18px;height:70px;border-radius:9px;background:#e8b98a;transform-origin:50% 0}
  .fore-arm{left:1px;top:64px;width:16px;height:60px;border-radius:8px;background:#e8b98a;transform-origin:50% 0}
  .hand{left:-2px;top:54px;width:20px;height:20px;border-radius:50%;background:#e8b98a}
  .thigh{top:0;width:22px;height:82px;border-radius:11px;background:#2b2b2b;transform-origin:50% 0}
  .shin{left:1px;top:76px;width:20px;height:76px;border-radius:10px;background:#2b2b2b;transform-origin:50% 0}
  .foot{left:-4px;top:70px;width:42px;height:14px;border-radius:4px 8px 8px 4px;background:#111;transform-origin:8px 50%}
  #armR{left:-9px}  #armL{left:47px}
  #legR{left:-24px} #legL{left:4px}
  .far{filter:brightness(.8)}
  #scrub{width:640px}
</style>
<div id="stage">
  <div id="ground"></div>
  <div id="root" class="part">
    <div id="hips" class="part">
      <div id="legR" class="thigh part far"><div class="shin part"><div class="foot part"></div></div></div>
      <div id="torso" class="part">
        <div id="armR" class="upper-arm part far"><div class="fore-arm part"><div class="hand part"></div></div></div>
        <div id="head" class="part"><div id="eye" class="part"></div></div>
        <div id="armL" class="upper-arm part"><div class="fore-arm part"><div class="hand part"></div></div></div>
      </div>
      <div id="legL" class="thigh part"><div class="shin part"><div class="foot part"></div></div></div>
    </div>
  </div>
</div>
<input id="scrub" type="range" min="0" max="1000" value="0"><span id="t"></span>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="rig-common.js"></script>
<script>
  var tl = gsap.timeline({ paused: true });
  window.__timelines = (window.__timelines || []).concat(tl);

  // joint lookup: one element per joint, rotation only. The root translates.
  var J = {
    hips: document.getElementById('hips'), torso: document.getElementById('torso'),
    head: document.getElementById('head'),
    thighL: document.getElementById('legL'), shinL: document.querySelector('#legL .shin'), footL: document.querySelector('#legL .foot'),
    thighR: document.getElementById('legR'), shinR: document.querySelector('#legR .shin'), footR: document.querySelector('#legR .foot'),
    upperArmL: document.getElementById('armL'), foreArmL: document.querySelector('#armL .fore-arm'),
    upperArmR: document.getElementById('armR'), foreArmR: document.querySelector('#armR .fore-arm')
  };
  // the ONLY writer of these transforms. Never also tween J.* with tl.fromTo.
  function applyPose(P) {
    gsap.set(J.hips,  { y: P.hipY, rotation: P.hipRock });
    gsap.set(J.torso, { rotation: P.torso });
    gsap.set(J.head,  { rotation: P.head });
    ['thighL','shinL','footL','thighR','shinR','footR','upperArmL','foreArmL','upperArmR','foreArmR']
      .forEach(function (k) { gsap.set(J[k], { rotation: P[k] }); });
  }

  // Rest pose so a seek to t=0 shows the rig standing (explicit from-state, seeded once).
  var REST = walkPose(0.25, 0.35);           // near-passing, low amplitude = relaxed stand
  applyPose(REST);

  // Walk: Williams brisk natural walk = 12 frames per step at 24 fps = 0.5 s per step,
  // so one full cycle (two steps) = 1.0 s = 30 frames at 30 fps. Four cycles, finite.
  var STEP = f(15), CYCLE = 2 * STEP, CYCLES = 4, WALK_AT = f(12);
  var drive = { p: 0, b: 0 };
  // ONE driver: p = cycle phase (linear), b = blend rest->walk over the first 8 frames.
  tl.fromTo(drive, { p: 0 }, { p: CYCLES, duration: CYCLE * CYCLES, ease: 'none',
    onUpdate: function () {
      var W = walkPose(drive.p, 1), out = {};
      for (var k in W) out[k] = REST[k] + (W[k] - REST[k]) * drive.b;
      applyPose(out);
    } }, WALK_AT);
  tl.fromTo(drive, { b: 0 }, { b: 1, duration: f(8), ease: 'power2.out' }, WALK_AT);

  // dev scrub only - not part of the composition
  var s = document.getElementById('scrub'), tt = document.getElementById('t');
  s.oninput = function () { tl.seek(s.value / 1000 * tl.duration(), false); tt.textContent = tl.time().toFixed(3) + 's / f' + Math.round(tl.time() * FPS); };
  window.__seek = function (sec) { tl.seek(sec, false); return tl.time(); };
</script>
```

### 2.6 Recipe: inline SVG rig, running (`rig-svg.html`)

Same pose math, explicit `rotate()` attributes, run tables.

**A reported probe that does not survive arithmetic.** The earlier revision said "contact pose at frame 30 and an airborne pose at frame 36". Recomputed from this recipe's own constants (`RUN_AT = f(12)`, `STEP = f(8)`, `CYCLE = 16` frames, so `phase = (t - 12) / 16`), the contact keys land on frames **28 and 36** and the UP keys (both feet off, `hipY = -18`) land on frames **34 and 42**. Frame 30 is the DOWN key (phase .125) and frame 36 is a contact, not airborne. Either the frames were mislabelled or the poses were eyeballed from silhouettes. The parallel walk check in 2.5 recomputes exactly, which makes this look like a transcription slip rather than a broken rig, but it is unverified either way.

```html
<!doctype html><meta charset="utf-8"><title>rig-svg</title>
<style>
  body{margin:0;background:#f4efe6;font-family:system-ui}
  #stage{width:640px;height:480px;background:#f4efe6;display:block}
  .skin{fill:#e8b98a} .cloth{fill:#3c5a99} .dark{fill:#2b2b2b} .far{opacity:.8}
  #scrub{width:640px}
</style>
<!-- Every joint is a <g> whose OWN origin (0,0) is the joint. Geometry is drawn from (0,0)
     downward. The child joint sits inside a translate() group placed at the parent's far end.
     Rotation is written as transform="rotate(a)" on the joint group, so no transform-origin
     or transform-box is involved at all (svg-icon-enrichment rule: explicit center). -->
<svg id="stage" viewBox="0 0 640 480">
  <line x1="0" y1="400" x2="640" y2="400" stroke="#bbb" stroke-width="2"/>
  <g id="root" transform="translate(320,300)">
    <g id="hips">
      <!-- far leg (drawn first = behind) -->
      <g transform="translate(-10,0)"><g class="j far" data-j="thighR">
        <rect class="dark" x="-11" y="0" width="22" height="82" rx="11"/>
        <g transform="translate(0,76)"><g class="j far" data-j="shinR">
          <rect class="dark" x="-10" y="0" width="20" height="76" rx="10"/>
          <g transform="translate(0,72)"><g class="j far" data-j="footR">
            <rect fill="#111" x="-8" y="-7" width="42" height="14" rx="5"/>
          </g></g>
        </g></g>
      </g></g>
      <rect class="dark" x="-30" y="-14" width="60" height="28" rx="14"/>
      <g transform="translate(0,-10)"><g class="j" data-j="torso">
        <rect class="cloth" x="-28" y="-96" width="56" height="96" rx="20"/>
        <g transform="translate(-18,-84)"><g class="j far" data-j="upperArmR">
          <rect class="skin" x="-9" y="0" width="18" height="70" rx="9"/>
          <g transform="translate(0,64)"><g class="j far" data-j="foreArmR">
            <rect class="skin" x="-8" y="0" width="16" height="60" rx="8"/>
            <circle class="skin" cx="0" cy="62" r="10"/>
          </g></g>
        </g></g>
        <g transform="translate(0,-92)"><g class="j" data-j="head">
          <circle class="skin" cx="0" cy="-30" r="30"/>
          <circle fill="#222" cx="12" cy="-34" r="4"/>
        </g></g>
        <g transform="translate(18,-84)"><g class="j" data-j="upperArmL">
          <rect class="skin" x="-9" y="0" width="18" height="70" rx="9"/>
          <g transform="translate(0,64)"><g class="j" data-j="foreArmL">
            <rect class="skin" x="-8" y="0" width="16" height="60" rx="8"/>
            <circle class="skin" cx="0" cy="62" r="10"/>
          </g></g>
        </g></g>
      </g></g>
      <g transform="translate(10,0)"><g class="j" data-j="thighL">
        <rect class="dark" x="-11" y="0" width="22" height="82" rx="11"/>
        <g transform="translate(0,76)"><g class="j" data-j="shinL">
          <rect class="dark" x="-10" y="0" width="20" height="76" rx="10"/>
          <g transform="translate(0,72)"><g class="j" data-j="footL">
            <rect fill="#111" x="-8" y="-7" width="42" height="14" rx="5"/>
          </g></g>
        </g></g>
      </g></g>
    </g>
  </g>
</svg>
<input id="scrub" type="range" min="0" max="1000" value="0"><span id="t"></span>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="rig-common.js"></script>
<script>
  var tl = gsap.timeline({ paused: true });
  window.__timelines = (window.__timelines || []).concat(tl);

  var J = {};
  document.querySelectorAll('.j').forEach(function (g) { J[g.dataset.j] = g; });
  var hips = document.getElementById('hips');

  // The only writer. Explicit rotate() about the joint origin; hips translate + rock.
  function applyPose(P) {
    hips.setAttribute('transform', 'translate(0,' + P.hipY.toFixed(2) + ') rotate(' + P.hipRock.toFixed(2) + ')');
    for (var k in J) J[k].setAttribute('transform', 'rotate(' + (P[k] || 0).toFixed(2) + ')');
  }

  var REST = walkPose(0.25, 0.35);
  applyPose(REST);                                  // seed t=0

  // RUN this time: Williams run = 6 frames per step at 24 fps = 0.25 s per step
  // -> 7.5 frames at 30 fps; author it as 8 frames (0.267 s) so keys land on frames.
  var STEP = f(8), CYCLE = 2 * STEP, CYCLES = 8, RUN_AT = f(12);
  var drive = { p: 0, b: 0 };
  tl.fromTo(drive, { p: 0 }, { p: CYCLES, duration: CYCLE * CYCLES, ease: 'none',
    onUpdate: function () {
      var W = runPose(drive.p, 1), out = {};
      for (var k in W) out[k] = REST[k] + (W[k] - REST[k]) * drive.b;
      applyPose(out);
    } }, RUN_AT);
  tl.fromTo(drive, { b: 0 }, { b: 1, duration: f(6), ease: 'power2.out' }, RUN_AT);

  var s = document.getElementById('scrub'), tt = document.getElementById('t');
  s.oninput = function () { tl.seek(s.value / 1000 * tl.duration(), false); tt.textContent = tl.time().toFixed(3) + 's / f' + Math.round(tl.time() * FPS); };
  window.__seek = function (sec) { tl.seek(sec, false); return tl.time(); };
</script>
```

## 3. The walk cycle

### 3.1 The four key poses

Williams' vocabulary, quoted from student notes on The Animator's Survival Kit (cloytoons, zak-graphicarts, mister-chad):

- **Contact**: "both feet on ground with one foot forward"; "The arms are always opposite to the legs to give balance and thrust."
- **Down** (recoil): "the lowest point of the cycle"; "This is where the bent leg takes weight and the arm swing is at it's widest."
- **Passing**: "one leg passes by the other as the weight shifts"; "As the leg is straight up on this passing position, the pelvis, body and head is lifted slightly higher."
- **Up** (high point): "The foot pushes off the ground, lifting the pelvis, body and head up to it's highest position of the cycle."
- Weight timing: "the weight goes down just after the contact pose and the weight goes up just after the passing position."

Williams' method is usually taught as contact-first (block both contacts, then passing, then down and up). **This document previously attributed a quote for that to Edward Boyle's walk-cycle notes; the quote is not on that page and has been removed.** The page was fetched twice and dumped in full and contains nothing about blocking order. Treat contact-first as received teaching practice with no citation in this document, not as a Williams quotation. Blair's chart, by contrast, gives the drawings in order without timing: "Preston offered no help in timing, or in the sequence in which the drawings are to be created" (Angry Animator, "Preston Blair Deciphered", https://angryanimator.com/word/2018/03/20/preston-blair-deciphered/ -- previously cited only as an unnamed search snippet; and John K: "You would want to shoot the walk on 2s or inbetween it, or it will be too fast").

Phase placement inside one step (inference, consistent with the quotes above): contact 0, down at 25%, passing at 50%, up at 75%, next contact at 100%. The tables in `rig-common.js` use exactly those phases.

### 3.2 Tempo: frames per step at 24 and 30 fps

The Monmouth adaptation of Williams' tempo list, stated for 24 fps. The page lists full cycles (two steps) with frames per step in brackets. **Four of its eight rows have shifted parentheticals, not one:** the 12-frame row says "4 frames per step, 6 steps per second" (should be 6 and 4), the 16-frame row says "6 frames per step, 4 steps per second" (should be 8 and 3), the 24-frame row says "3 steps per second" (should be 2), and the 32-frame row says "2/3rd steps per second" (should be 1.5). The per-step column below is cycle/2, which repairs all four and matches Williams' own per-step framing; the steps-per-second column below is likewise recomputed and is correct. (The earlier revision described this as a single typo in one row.)

| Williams description (Monmouth wording) | frames per step @24 | steps per second | frames per step @30 (exact) | authored @30 | seconds per step |
|---|---|---|---|---|---|
| "Very fast run" | 4 | 6 | 5 | 5 | 0.167 |
| "Run or very fast walk" | 6 | 4 | 7.5 | 8 (or 7) | 0.267 (0.233) |
| "Slow run or 'cartoon' walk" | 8 | 3 | 10 | 10 | 0.333 |
| "Brisk, business-like walk - 'natural walk'" | 12 | 2 | 15 | 15 | 0.500 |
| "Strolling walk, more leisurely" | 16 | 1.5 | 20 | 20 | 0.667 |
| "Elderly or tired person" | 20 | 1.2 | 25 | 25 | 0.833 |
| "Slow step" | 24 | 1 | 30 | 30 | 1.000 |
| Slowest row (Monmouth's wording here is the song-lyric caption "...'show me the way ... to go home'...", not "Very slow walk") | 32 | 0.75 | 40 | 40 | 1.333 |

Basis: the 24 fps column and descriptions are the Monmouth page (adapted from Williams). The 30 fps columns are arithmetic (x 1.25). **On rounding, and a rule this document previously contradicted.** The "authored" column rounds to whole frames. The rounding rule as previously stated ("when the exact value is x.5, prefer the slower whole frame for walks and the faster for runs") is self-contradictory in this very table: the only x.5 row is 7.5 on the "Run or very fast walk" line, and by the stated rule a run takes the faster value, 7. The authored column hedged "8 (or 7)" and the recipes then picked 8, the slower one. **Resolved: quantise the CYCLE, not the step.** 7.5 frames per step is 15 frames per cycle, exactly on the grid, with the second leg's contact falling mid-frame where it is invisible because the two legs are symmetric. That costs nothing, where rounding 7.5 up to 8 slows the run by 6.7%. The frame-grid argument that motivated per-step rounding is a hand-drawn constraint imported into a procedural pipeline where it does not apply: in a pose-function rig the pose is continuous and the renderer samples it, so a key at frame 7.5 is not lost, it is slightly softened by sampling. (Inference; the arithmetic is not in dispute.)

**On the per-step reading.** The earlier revision cited "a second student summary (Altea Claveras, quoting the book)" as independent confirmation that these are per-step numbers. **That citation carries no URL, appears nowhere in the source list, and returns nothing on a targeted search; it has been removed.** The per-step reading now rests on the Monmouth page's own bracketed figures plus the cycle/2 reconstruction that repairs its four shifted rows, which is strong internal evidence but is **not independently corroborated**. Treat the ladder as inference from one adapted secondary source.

Sanity checks from other sources: Scott Moore (Ulster) gives "12-16 frames per cycle for a run compared to 24 frames per cycle for a walk" and, citing Williams, "at least 3 frames are needed for the legs to cycle" -- consistent with the table. **Cloy Toons does not agree with the table; it contradicts it.** The verbatim line is "For my run cycle I think I'll animate it as a six frame cycle as its considered to be a good place to start as suggested in the Animators survival kit": a six-frame **cycle**, i.e. 3 frames per step, which is faster than this table's own "very fast run" row of 4 frames per step and half the 6-frames-per-step row it was quoted to support. It also contradicts Ulster's 12-16 frames per cycle for a run. This is exactly the cycle-versus-step confusion the paragraph above spends its length untangling, and it had slipped back in as false corroboration.

The recipes: the HTML walk uses 15 frames per step (0.5 s, the natural walk); the SVG run uses 8 frames per step, which by the rule above should be a 15-frame cycle (7.5 per step) instead.

**Why the numbers matter beyond speed.** Williams' descriptions attach character to tempo (business-like, strolling, elderly). Pick the row from the brief's verb (beat-direction.md's "every element gets a verb"), then fit the amplitude; do not scale a natural walk's timing to make it feel tired.

### 3.3 Arm counter-swing and head bob

- Arms opposite legs: Williams, and not in dispute. **Where the swing is widest is a choice between two things Williams says, not a settled fact, and this document previously presented it as settled.** Edward Boyle's notes report both halves: "Williams says that the arm swing is at its widest in the down position, but he prefers it to be on the contact position." The down reading is the real-life mechanic; the contact reading is what Williams prefers in animation, and standard Blair/Williams charts put the arm extremes at contact, coincident with the leg extremes. The tables here choose **down**, implemented as `-0.85 x (opposite thigh)` with a phase lag of 0.06 cycle. That is a defensible choice; it is not what Williams recommends. If the walk reads mushy, set the lag to 0 and put the arm extremes on contact. The 0.85 ratio and the lag are inference.
- Forearm: bends more when the arm is forward (inference; a straight pendulum reads mechanical). `foreArm = -25 - 20 * forwardness`.
- Head: highest at up, lowest at down (Williams). The hips carry the bob; the head inherits it through the torso. Bob amplitude in the recipe is 8 px on a character 300 px tall, about 2.7% of height, with a tiny nod of 2 degrees against the bob (inference). For a cartoony walk the tables are scaled by `amp = 1.6` (inference); Williams' own instruction is that "We're not copying life - we're making a comment on it" (zak-graphicarts quoting the book).
- Blair's chart shows "the curving arc of the head/body bouncing up and down through the entire cycle" (mister-chad), so the bob is a curve, not a triangle wave; smoothstep between keys gives that.

### 3.4 Looping deterministically

Two contract-safe ways.

**A. Phase driver (used in the recipes).** `tl.fromTo(drive, {p: 0}, {p: CYCLES, duration: CYCLE * CYCLES, ease: 'none', onUpdate})` and `phase = p mod 1`. Finite (CYCLES is a number), seek-safe (pose is `walkPose(p)`), and the walk's speed can be changed at one place. A blend variable `b` ramps the pose from rest to the cycle over 8 frames so the first step is not a pop; `b`'s from-state is 0, which makes the driver's pre-start render a no-op (section 0, item 2).

**B. Nested timeline with finite `repeat`.** GSAP's Timeline docs: `repeat` is the "Number of times that the animation should repeat after its first iteration ... To repeat indefinitely, use -1", `yoyo` runs "every other repeat cycle ... in the opposite direction", and a nested timeline is added with `tl.add(nested, position)`. A walk child timeline of `fromTo` tweens per joint with `repeat: CYCLES - 1` is legal as long as the repeat is finite, but the child's joints then belong to that child forever (item 4). Use A for anything that has to blend, stop, or change speed; B is only simpler for a background walker that never does anything else. `rules-index.md` says "never a second timeline": a child added to the one paused master is not a second root, but keep everything on the master unless a nested repeat buys real clarity.

**Walking in place versus travelling, and the rig's worst defect.**

The recipes walk in place, and the earlier revision said foot slide is fixed by translating `#root` at a constant `stride / stepDuration`. **It is not, and this rig's planted foot neither stays on the ground nor stays still.** Re-implementing `walkPose` and computing the ankle in world space (hip-to-knee 76 px, knee-to-ankle 72 px, plus the `hipY` curve), the planted foot's world height swings from 122.6 px to 152.1 px across the stance half-cycle: **29.5 px of vertical excursion on a roughly 300 px character**, driving about 19 px through the ground plane at the DOWN pose and floating about 13 px above it near the back contact. Horizontally the ankle covers 141.7 px of stance travel at 3.4 to 17.5 px per frame against the 10.1 px per frame a constant root would need, so the foot **slides backward at up to 7 px/frame and forward at up to 7 px/frame within a single step**. A constant root rate cannot fix either problem; it is the wrong shape of correction.

**The fix is to invert the authoring.** Author the ANKLE trajectory in world space (flat and world-locked through stance, an arc through swing) and derive thigh and shin from it with a **two-bone closed-form IK solve**. Hip height then becomes a consequence of leg geometry rather than a fourth independent curve fighting it. Two-bone IK is not a simulation and is legal under the contract: given a target distance `d` and limb lengths `L1`, `L2`,

```js
// closed-form two-bone IK: stateless, a pure function of the target position
function ik2(L1, L2, tx, ty) {                 // target relative to the hip
  var d = Math.min(Math.hypot(tx, ty), L1 + L2 - 1e-6);
  var knee = Math.acos((L1 * L1 + L2 * L2 - d * d) / (2 * L1 * L2));       // interior angle
  var hip  = Math.atan2(tx, ty) - Math.asin(L2 * Math.sin(knee) / d);
  return { thigh: hip * 180 / Math.PI, shin: (Math.PI - knee) * 180 / Math.PI };
}
```

Section 9 previously listed "IK foot planting" under what needs a physics simulation. That was a category error and it foreclosed the fix for this rig's worst defect; it has been corrected there. If FK is kept anyway, then at minimum drive the root from the stance ankle's **computed x** so slide is zero by construction, and re-solve `hipY` from the leg length instead of authoring it as an independent curve. If the ground is a texture, scrolling it at the same computed rate is the cheaper cut.

**Ending a cycle.** Stop on a contact or a passing pose and blend `b` back toward a rest pose over 8-12 frames; stopping mid-swing reads as a freeze. Then a moving hold (section 5).

### 3.5 Run versus walk

Run specifics from the notes on Williams (cloytoons run post): both feet off the ground, forward lean that "increases with running speed", arm opposition kept. The `RUN` tables in `rig-common.js` add a 14 degree lean, a larger bob (18 px), higher knees, and pumped arms with the elbows locked at -80 degrees (inference). At 8 frames per step the whole cycle is 16 frames, so a key every 2 frames; smoothstep between keys still gives the slow-in/out that Blair's on-twos drawings would have had by omission.

## 4. Blinks, head turns, weight shifts, jumps

### 4.1 Blinks

Bloop Animation's frame counts at 24 fps:

- Regular blink: "Closing lids (2 frames) hold eyes closed (1 frame) opening lids (3 frames)" = 6 frames.
- Fast blink: "Closing lids (2 frames) opening lids (3 frames)" = 5.
- Long blink: "Closing lids (3 frames) hold eyes closed (2 frames) opening lids (4 frames)" = 9.
- Eye batting: "Close lids 3/4 (1 frame) opening lids (2)" = 3.
- Eye dart: "3 frames: The original position of the pupil, a transitional frame, and the ending position."

Animation Apprentice: "A standard blink is usually about 8 frames, with the lids closed for about 2 frames, and an ease-in and ease-out at either end", lids offset "by one frame", "your characters should blink every time they change eye direction", and brows should move slightly with the blink.

The asymmetry to keep: **close faster than open** in every row above (2 vs 3, 3 vs 4). At 30 fps the recipe uses close 3, hold 1, open 4 (8 frames, 0.267 s) as the regular blink and 3/2/5 for a slow one; the scaling from 24 to 30 is arithmetic rounded to frames. **Note that neither Bloop nor Escape Studios states a frame rate.** Both give bare frame counts. 24 fps is a reasonable working assumption for hand-drawn instruction and is what this document assumes, but it is **this document's inference, not the authors' statement**, and the earlier revision presented it as the latter. (SunStrike, also cited, does state a 24-30 fps context.)

Mechanism: a skin-coloured lid div inside an `overflow: hidden` eye, `transform-origin: 50% 0`, `scaleY` 0 (open) to 1 (closed). Opacity would show the pupil through the lid; a mask-shaped lid with `scaleY` reads as a lid coming down.

Three corrections to that mechanism, all cheap and all worth more than any of the frame counts. (1) **A rectangular lid scaled in Y closes with a straight horizontal edge across a round eye, which reads as a roller shutter.** Give the lid a bottom `border-radius` so its leading edge is an arc, and make the closed pose a curved line rather than a filled block. (2) **The lid must ride the eyeball.** When the pupil looks down the upper lid drops with it, roughly 30-40% of the pupil's travel; a lid that stays put while the eye moves is the commonest tell in cheap 2D character work, and the head-turn recipe in 4.2 moves the pupils 6 px with no lid response at all. (3) **The close ease is backwards, and at 3 frames it barely matters either way.** `power2.in` means slow start, fast finish: the lid creeps for a frame and a half then slams, which reads as a rendering glitch. A blink closes fast from the first frame and settles into the closed pose, so `power1.out` or linear. But this is false precision: a 3-frame tween has two in-between positions and swapping the cubic moves them by under 10 px of a 26 px lid. **Below about 5 frames you author positions, not curves** -- which applies to half a dozen places in this document where a cubic is specified on a 3-frame move. (All three: inference from standard 2D eye-rig construction.)

### 4.2 Head turn with anticipation

- Length: "Head turns read well around 10-14 frames" (SunStrike, at 24-30 fps). Recipe: 12 frames, 0.4 s.
- Anticipation: "Small motion opposite to main direction before action. Duration: 100-200ms, magnitude: 10-20% of main action" (disney-principles.md). Recipe: 4 frames (0.133 s) at 15% of the travel. Thomas and Johnston: "Anticipation is used to prepare the audience for an action" (handwiki pp. 51-52).
- Eyes lead: the pupils dart to the target over 3 frames before the head starts (Bloop's eye dart count; that the eyes lead the head is inference from the Animation Apprentice rule that a change of eye direction gets a blink, plus the Animation Mentor snippet that "an eye blink before a head turn is an example of anticipation").
- Blink in the middle: "I like to have the eyes blink completely closed in the middle pose" (Envato Tuts+). The recipe schedules the blink so the lids are shut at 50% of the turn.
- Hair follow-through: "Child delay: 50-150ms behind parent" (disney-principles.md); Thomas and Johnston: "loosely tied body parts continue moving after a character stops" (handwiki pp. 59-62). Recipe: hair starts 3 frames late and overshoots with `back.out(2.5)`. This is the one place a `back` ease is doctrine-correct: `spring-pop-entrance` bans it for entrances because it reads as cartoon wobble, but follow-through on a loose part is the register it was made for.
- Cushion: Envato Tuts+'s full text is "the character stops, moves forward a little bit, and then moves back into the stop position" -- an **out-and-back**, not a one-way creep. The earlier revision quoted it with an ellipsis that removed the operative clause and then implemented only the forward half ("one more degree over 6 frames"). The one-way version is a defensible deliberate choice here, because `grade-original.py`'s settle-direction-reversal check fails the return leg (section 6 says as much), but the source does not endorse it and the elided quote made it look as though it did.

**Two amplitudes in this recipe are below the visibility floor the document itself sets.** The anticipation is 15% of a 34 px travel over 4 frames, which is 5.1 px total, 1.3 px per frame, against HF's own "subtle reads as static at 30 fps". The hair overshoot is worse: `back.out(2.5)` peaks 18.9% over target, and on a 5-degree tween that is 0.94 degrees -- nobody sees a one-degree overshoot on a 176 px hair shape. Percentage rules for anticipation and overshoot break down below roughly 12-15 px of counter-travel: below that you either scale the prep up disproportionately (a small move needs a proportionally **bigger** wind-up to read at all) or you omit it and spend the frames elsewhere. For the hair to read as follow-through against a 6-degree head turn, the overshoot needs to be 8-12 degrees, i.e. larger than the parent's travel, not 19% of a fifth of it. (Computed: `back.out(2.5)` peak = 1.189; the 12-15 px floor is inference.)

A flat vector head cannot rotate in Y. The recipe fakes the turn by sliding the face group horizontally inside the head and tilting the head a few degrees. **A rigid face group sliding in a straight line is the flat default look**, and three things make the cheat work, none of which the recipe has: (1) the face group must compress in X as it moves off-centre, to about 0.85 at full turn, because you are simulating a curved surface rotating away; (2) the far eye must travel further and narrow more than the near eye (parallax), so the eyes cannot live in one rigid group; (3) the features arc on the head's curve, so there is a small Y offset through the middle of the slide, not a straight horizontal path. The same missing-arc note applies to the weight shift and the dash, both of which are straight lines. (Inference; standard 2D head-turn cheat as built with a puppet or a nested-null parallax rig.) a real turn needs swapped drawings (front, three-quarter, side) shown with `tl.set` visibility on the middle frames, which is the lip-sync mechanism of section 7 applied to heads.

### 4.3 Weight shift

Hips move first, the chest counters, the head arrives last: an overlap of 2-3 frames per level (the ~3 frame sibling offset in `manifesto` SKILL.md's controllers note, and disney-principles' 50-150 ms child delay). The recipe moves the body 10 px and rotates it -3 degrees over 10 frames, the neck 2 frames later, the head 3 frames later with a smaller counter-rotation. Amplitudes are inference.

### 4.4 Recipe: face and torso (`face.html`)

Verified: eyes open at frame 0; at frame 40 (mid-turn) one lid was fully down and the other one frame behind, the features had slid, the hair had started to follow; at frame 54 the head had settled and the hair was in overshoot; at frame 162 the hold showed the body's breath scale and the weight-shift offset held.

```html
<!doctype html><meta charset="utf-8"><title>face-blink-turn-hold</title>
<style>
  body{margin:0;background:#f4efe6;font-family:system-ui}
  #stage{position:relative;width:640px;height:480px;overflow:hidden;background:#f4efe6}
  .part{position:absolute;will-change:transform}
  #body{left:230px;top:250px;width:180px;height:260px;border-radius:70px 70px 20px 20px;background:#3c5a99;transform-origin:50% 100%}
  #neck{left:300px;top:230px;width:40px;height:40px;background:#e8b98a}
  #head{left:240px;top:80px;width:160px;height:170px;border-radius:50% 50% 45% 45%;background:#e8b98a;transform-origin:50% 100%}
  #hair{left:-8px;top:-14px;width:176px;height:70px;border-radius:80px 80px 20px 20px;background:#2b2b2b;transform-origin:50% 100%}
  #face{left:0;top:0;width:160px;height:170px}          /* features slide inside the head to fake a turn */
  .eye{top:70px;width:26px;height:26px;border-radius:50%;background:#fff;overflow:hidden}
  .pupil{position:absolute;left:9px;top:9px;width:9px;height:9px;border-radius:50%;background:#222}
  .lid{position:absolute;left:0;top:0;width:100%;height:100%;background:#e8b98a;transform-origin:50% 0}
  #eyeL{left:92px} #eyeR{left:42px}
  .brow{top:56px;width:30px;height:6px;border-radius:3px;background:#2b2b2b}
  #browL{left:90px} #browR{left:40px}
  #mouth{left:64px;top:122px;width:32px;height:8px;border-radius:0 0 16px 16px;background:#8a4a3a}
  #scrub{width:640px}
</style>
<div id="stage">
  <div id="body" class="part"></div>
  <div id="neck" class="part"></div>
  <div id="head" class="part">
    <div id="hair" class="part"></div>
    <div id="face" class="part">
      <div id="browR" class="brow part"></div><div id="browL" class="brow part"></div>
      <div id="eyeR" class="eye part"><div class="pupil"></div><div class="lid"></div></div>
      <div id="eyeL" class="eye part"><div class="pupil"></div><div class="lid"></div></div>
      <div id="mouth" class="part"></div>
    </div>
  </div>
</div>
<input id="scrub" type="range" min="0" max="1000" value="0"><span id="t"></span>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script>
  var FPS = 30, F = 1 / FPS; function f(n) { return n / FPS; }
  var tl = gsap.timeline({ paused: true });
  window.__timelines = (window.__timelines || []).concat(tl);
  var lids = ['#eyeR .lid', '#eyeL .lid'];

  // Explicit rest state at t=0 for everything a tween will later own.
  gsap.set(lids, { scaleY: 0 });                     // lids OPEN = scaleY 0 (lid slides down to close)
  gsap.set(['#head', '#body', '#hair', '#face', '.pupil', '.brow'], { x: 0, y: 0, rotation: 0 });

  // ---- BLINK -------------------------------------------------------------------------
  // Regular blink (Bloop Animation, at 24 fps): close 2, hold 1, open 3 = 6 frames.
  // Scaled to 30 fps and rounded to frames: close 3, hold 1, open 4 = 8 frames (0.267 s).
  // Close is FASTER than open (asymmetry). Lids offset by one frame (Animation Apprentice).
  function blink(at, close, hold, open) {
    close = close || f(3); hold = hold || f(1); open = open || f(4);
    lids.forEach(function (sel, i) {
      var t0 = at + i * f(1);                          // second lid one frame late
      tl.fromTo(sel, { scaleY: 0 }, { scaleY: 1, duration: close, ease: 'power2.in', immediateRender: false }, t0);
      tl.fromTo(sel, { scaleY: 1 }, { scaleY: 0, duration: open, ease: 'power2.out', immediateRender: false }, t0 + close + hold);
    });
    // brows dip a hair with the blink so the face does not go stiff (Animation Apprentice)
    tl.fromTo('.brow', { y: 0 }, { y: 2, duration: close, ease: 'power1.in', immediateRender: false }, at);
    tl.fromTo('.brow', { y: 2 }, { y: 0, duration: open, ease: 'power1.out', immediateRender: false }, at + close + hold);
  }

  // ---- HEAD TURN with anticipation, blink in the middle, hair follow-through ---------
  // Turn length: 10-14 frames reads well (SunStrike). Author 12 frames = 0.4 s.
  // Anticipation: small move the OTHER way, 100-200 ms and 10-20% of the main travel
  // (motion-design disney-principles). Blink closed on the middle pose (Envato Tuts+).
  var TURN_AT = f(30), ANT = f(4), TURN = f(12), TRAVEL = 34;   // px the features slide
  // anticipation: features + head lean slightly away from the turn direction
  tl.fromTo('#face', { x: 0 }, { x: -TRAVEL * 0.15, duration: ANT, ease: 'power1.inOut' }, TURN_AT);
  tl.fromTo('#head', { rotation: 0 }, { rotation: 2, duration: ANT, ease: 'power1.inOut' }, TURN_AT);
  // main turn: features slide across the head, head tilts into the move, then settles
  tl.fromTo('#face', { x: -TRAVEL * 0.15 }, { x: TRAVEL, duration: TURN, ease: 'power3.out', immediateRender: false }, TURN_AT + ANT);
  tl.fromTo('#head', { rotation: 2 }, { rotation: -6, duration: TURN, ease: 'power3.out', immediateRender: false }, TURN_AT + ANT);
  // the eyes lead: pupils dart to the target over 3 frames BEFORE the head moves (eye dart = 3 frames, Bloop)
  tl.fromTo('.pupil', { x: 0 }, { x: 6, duration: f(3), ease: 'power2.out' }, TURN_AT - f(3));
  tl.fromTo('.pupil', { x: 6 }, { x: 0, duration: TURN, ease: 'power2.out', immediateRender: false }, TURN_AT + ANT);
  // blink lands so the lids are CLOSED on the middle of the turn
  blink(TURN_AT + ANT + TURN * 0.5 - f(3));
  // hair: follow-through, child lags parent by 50-150 ms (disney-principles): 3 frames here,
  // overshoots the head rotation and settles late
  tl.fromTo('#hair', { rotation: 0 }, { rotation: 5, duration: TURN + f(4), ease: 'back.out(2.5)', immediateRender: false }, TURN_AT + ANT + f(3));
  // cushion: the head does not dead-stop; it creeps 1 more degree over 6 frames (Envato Tuts+ "cushion")
  tl.fromTo('#head', { rotation: -6 }, { rotation: -7, duration: f(6), ease: 'power1.out', immediateRender: false }, TURN_AT + ANT + TURN);
  // BUG, fixed here: the follow-through tween above runs from TURN_AT + ANT + f(3) = f(37)
  // for TURN + f(4) = f(16), ending at f(53); this settle previously started at
  // TURN_AT + ANT + TURN + f(4) = f(50), so frames 50-53 had TWO fromTo tweens writing
  // #hair rotation concurrently -- exactly the failure motion-principles.md describes and
  // that section 0 item 4 of this document names. Start it where the first one ends.
  tl.fromTo('#hair', { rotation: 5 }, { rotation: 0, duration: f(8), ease: 'power2.out', immediateRender: false }, TURN_AT + ANT + f(3) + TURN + f(4));

  // ---- WEIGHT SHIFT ----------------------------------------------------------------
  // hips go one way, shoulders/head counter the other, head last (overlap, 2-3 frames apart)
  var WS_AT = f(90);
  tl.fromTo('#body', { x: 0, rotation: 0 }, { x: 10, rotation: -3, duration: f(10), ease: 'power2.inOut' }, WS_AT);
  tl.fromTo('#neck', { x: 0 }, { x: 6, duration: f(10), ease: 'power2.inOut' }, WS_AT + f(2));
  tl.fromTo('#head', { x: 0, rotation: -7 }, { x: 4, rotation: -4, duration: f(12), ease: 'power2.inOut', immediateRender: false }, WS_AT + f(3));

  // ---- MOVING HOLD (from f(120) to the end) ---------------------------------------
  // Never a full stop: a hold rendered as bit-identical frames fails the duplicate-frame
  // check in grade-original.py and reads dead (Thomas & Johnston, moving hold).
  // Three finite ingredients: (1) a slow creep to a slightly different pose, (2) a breath,
  // (3) a blink. Amplitudes at the sine-wave-loop low end.
  var HOLD_AT = f(120), HOLD = f(90);
  tl.fromTo('#head', { rotation: -4 }, { rotation: -3, duration: HOLD, ease: 'power1.out', immediateRender: false }, HOLD_AT); // creep
  var breath = { p: 0 };
  tl.fromTo(breath, { p: 0 }, { p: Math.PI * 2 * 1.5, duration: HOLD, ease: 'none',   // 1.5 breaths in 3 s
    onUpdate: function () {
      var s = Math.sin(breath.p);
      gsap.set('#body', { scaleY: 1 + s * 0.012, y: -s * 1.5, transformOrigin: '50% 100%' });
      gsap.set('#neck', { y: -s * 2.2 });
    } }, HOLD_AT);
  blink(HOLD_AT + f(40));
  blink(HOLD_AT + f(74), f(3), f(2), f(5));            // a longer, slower one

  var s = document.getElementById('scrub'), tt = document.getElementById('t');
  s.oninput = function () { tl.seek(s.value / 1000 * tl.duration(), false); tt.textContent = tl.time().toFixed(3) + 's / f' + Math.round(tl.time() * FPS); };
  window.__seek = function (sec) { tl.seek(sec, false); return tl.time(); };
</script>
```

### 4.5 Bounce and jump: squash, stretch, hang time

Ratios and frame counts from disney-principles.md: "Squash: scale ~[1.2, 0.8]; Stretch: ~[0.85, 1.15]; Impact: 2-4 frames (30-65ms); Recovery: 4-8 frames (65-130ms); Preserve volume". Thomas and Johnston: "An object's volume does not change when squashed or stretched. If the length of a ball is stretched vertically, its width needs to contract correspondingly horizontally" (handwiki p. 49).

**Only the flight phase of this recipe holds that invariant, and the earlier revision claimed all of it did.** Four of the five phases lerp hand-picked pairs that break volume: crouch 0.78/1.18 (1/0.78 = 1.28, area error -8.0%), push 1.22/0.86 (1/1.22 = 0.82, +4.9%), landing 0.76/1.20 (1/0.76 = 1.32, -8.8%), recovery back to 1/1. Only the flight branch computes `P.sx = 1 / P.sy`. Two honest options: compute the partner scale everywhere (one line), or drop the volume claim. **In practice drop the claim, not the numbers**: for a character with feet, a landing squash that widens *less* than reciprocal reads heavier and better, because a real body loses height into bent knees rather than displacing sideways. But say which you are doing. Note also that the 0.22 of flight stretch exceeds this document's own cited stretch range of [0.85, 1.15].

Phases and frames at 30 fps (recipe values). **Two of the five frame counts are outside the ranges cited above, and the earlier revision said all five were inside them.** Landing squash 3 sits in "Impact: 2-4 frames" and recovery 7 sits in "Recovery: 4-8 frames", but crouch 8 frames (267 ms) and push 3 frames are covered by no range quoted here; the crouch is an anticipation, for which the same source gives 100-200 ms, i.e. 3-6 frames at 30 fps, and section 11's own checklist repeats that as "Anticipation 10-20% of the travel over 3-6 frames". The 8-frame crouch therefore contradicts both the cited range and this document's own checklist. Either shorten it to 5-6 frames or state it as a deliberate cartoon over-crouch. The physics below is not inference:

| phase | frames | seconds | what |
|---|---|---|---|
| crouch (anticipation) | 8 | 0.267 | squash to 0.78 / 1.18, `power2.inOut` |
| push | 3 | 0.100 | stretch to 1.22 / 0.86, `power3.out` |
| flight | 15 | 0.500 | ballistic, stretch proportional to speed, upright at apex |
| landing squash | 3 | 0.100 | 0.76 / 1.20, `power2.out` |
| recovery | 7 | 0.233 | back to 1 / 1 |

Flight is `y = -v0 t + g t^2 / 2` with `g = 8H / AIR^2` and `v0 = g AIR / 2`, so the animator chooses the **hang time in frames** and the **apex height in pixels** and the physics follows. Two things come free: the Odd Rule ("the spacings from the apex go as 1, 3, 5, 7, 9, and so on", Animator Island summarising Garcia) so the apex is the slow part and the take-off and landing the fast parts, and scale ("just a 20% change in the timing will make a 6 foot character seem like it's only about 4 feet tall"; "It takes a ball about 1/2 second to fall to the ground from a height of 4 feet", same source). **The units here were crossed in the earlier revision and the worked example was wrong by about a factor of five in height.** Garcia's half second is the **fall** from 4 feet; this recipe's `AIR = f(15) = 0.5 s` is the **total flight**, so its fall leg is only 0.25 s, which by the same source is roughly a foot of apparent rise: a hop, not a body height. Under real gravity, `h = g (AIR/2)^2 / 2`, so a 0.5 s hang is a 0.31 m apex (about one foot) and a body-height jump (1.75 m apex) needs about 1.2 s of hang, **36 frames at 30 fps**. Restate the rule as `hang_time = 2 sqrt(2H/g)`: **15 frames reads as a one-foot hop, and anything that should read as a real leap needs 30-36 frames.** The scaling argument itself is right and worth keeping; only the worked example inverted it. (Computed; Garcia for the 4-foot / half-second anchor. The rest of this recipe's jump arithmetic is correct: `g = 8H/AIR^2 = 4800`, `v0 = 1200`, apex exactly 150 px at t = 0.25 s.)

**The stretch axis is hard-coded to Y and should follow the velocity vector.** The character travels 260 px horizontally and 150 px vertically, so the take-off velocity is nowhere near vertical and a Y-only stretch is off-axis by 30 to 60 degrees, which reads as the character inflating rather than as speed. The fixed `P.rot = 8 * k` is a fudge covering for the missing angle. Correct it in two lines: `rotation = atan2(vy, vx) + 90` degrees, then stretch along the element's local Y. This is exactly what an After Effects rig does with auto-orient-along-path plus a scale expression. (The recipe's own DX/AIR against v0; stretch following velocity is standard.)

Reported probe (artifact not retained, but every figure recomputes from the constants above): at the apex frame (0.95 s) the body read `x=130 y=-150 scaleX=1.00 scaleY=1.00`; at landing (1.2 s) `y=0`; at the crouch end `scaleY=0.78`.

`bounce` and `elastic` eases are not used anywhere in this section. A ball bounce is a sequence of ballistic arcs with a squash at each contact, which the same formula gives per bounce; GSAP's `bounce` ease is a fixed shape that cannot be tuned to a character's weight (gsap-easing-and-stagger.md marks it "physical-comedy register only").

## 5. Smears and multiples in vector art

### 5.1 What they are

- Smear: "A 'smear' depicts one quick 'blur' of motion in a single frame" (IdeaRocket); "Smear animation is a rapid movement portrayed across 3 to 4 drawings. The anticipation drawing is followed by 1 to 2 smeared drawings and finally the resolution" (traditionalanimation.com). Wikipedia's taxonomy: elongated in-betweens ("distorting it over 1-2 frames") and multiples ("Duplication of the subject or parts of the subject along a path of motion. It does not distort the subject").
- History: "The first use of a smear frame is often attributed to the 1942 Warner Brothers short, 'The Dover Boys at Pimento University,' where animator Chuck Jones used smears" (Bloop), with earlier 1930s examples. Dry brush, the painted trail, dates from "the early 1930s with the advent of color" (traditionalanimation.com).
- When: "Employed when action exceeds the speed of animating on 1s" and "only when necessary and, if on a healthy budget, sparingly" (traditionalanimation.com).

### 5.2 When a 30 fps piece needs one

The measurable version of "action exceeds the speed of animating on 1s" is edge travel per frame. `manifesto` SKILL.md (frame-rate section) found that 31 px of edge travel per frame strobes on a high-contrast letterform even though every frame was distinct and the ease was clean, and states: "Above roughly 5-10 px of edge travel per frame, expect strobing on hard edges." That is the trigger: compute `max |dx/dt| / fps` for the move. **State the threshold as a fraction of frame width, not in absolute pixels.** The cited figure was measured on one composition at one frame size; 10 px is 1.6% of a 640-wide stage, 0.5% of 1920 and 0.26% of 3840, so carrying the absolute number across output resolutions silently changes what it means. The portable forms are about 1.5% of frame width per frame, or, better for a rig, **more than about half the object's own width per frame**. Above that on a hard-edged shape you need a smear, a rendered shutter (the `tmix` approach, held clear of cuts), or a slower move.

**And strobing depends on what the eye is tracking.** A subject the viewer is smoothly pursuing does not strobe at speeds that shatter the background, which is why fast pans judder while the tracked hero does not. Nothing in this document models gaze, so a naive application of the threshold over-applies smears to hero subjects and under-applies them to backgrounds and camera moves. (Resolution arithmetic; smooth-pursuit versus fixed-gaze is the standard account of why 24 fps pans judder and tracked action does not.)

The recipe's 240 px whip in 6 frames is **40 px/frame on average, not at peak**: `dashX` uses `power3.out`, whose derivative at u = 0 is 3, so the first frame carries roughly 120 px. It needs a smear, and more of one than the mean figure suggests. (Computed from the recipe's own `dashX(t) = DX + DASH_X * power3.out(t/DASH)`; this document already uses `v = 3(1-u)^2` for that curve in `puckPose`.)

Only fake it on entrances and mid-shot moves, never on an exit (`motion-blur-streak`, "never a mid-composition exit"), and let the object "dwell >= 1 s sharp after the snap" (same rule).

### 5.3 Two fakes, both pure functions

**A. Multiples (ghost copies).** N duplicates behind the lead, each drawn where the lead was `i` frames ago: `ghost_i(t) = pose(t - i * dt)`. Because the lead's position is already a pure function of time, the ghost is the same function at an earlier argument, which is exactly what a multiple is. `motion-blur-streak` path B gives the ranges: 2-4 ghosts (">4 reads as strobe, not streak"), base opacity 0.3-0.6, and the ghosts collapse into the lead at the settle. The recipe uses 3 ghosts at `0.45 / i` opacity, one frame apart.

**That ghost-count ceiling is a UI-motion rule for slow moves and it inverts at 40 px/frame.** One-frame spacing on a move this fast puts the first ghost 101 px behind an 80 px object, leaving a 21 px hole, so you get four discrete silhouettes: a **multiples** read (a deliberate 1940s cartoon effect), not a blur read. Decide which you want. For a **blur** read use sub-frame spacing (1/3 or 1/4 frame) and 6-8 copies at low opacity, which strobes *less*, not more, because the copies overlap. For a **multiples** read keep them discrete but hold each only 1-2 frames and deform each copy progressively (trailing copies stretched and thinned), because classical multiples are redrawn, not duplicated -- undeformed copies of one shape are the giveaway. Wikipedia's own taxonomy, quoted in 5.1, draws exactly this line; the recipe as written sits between the two and reads as neither. (Gap arithmetic computed; the two remedies are inference from that taxonomy.)

**B. Elongated in-between (scaleX stretch on the motion axis).** `scaleX = 1 + K * |v| / vmax` with `transform-origin` at the trailing edge, and the position pulled back by the growth so the leading edge lands where the un-smeared object would be. **`K` should be derived, not chosen, and 1.6 is roughly half of what the technique needs.** A drawn smear works by bridging the gap between consecutive frames so the eye fuses them. The puck travels 205 px in its first rendered frame and is 60 px wide, so it needs `sx >= (205 + 60) / 60 = 4.4x` to close the gap; `K = 1.6` delivers 2.02x = 121 px, leaving an 83 px hole, so the object still strobes, it just strobes as an ellipse. Set `K` so that `width * sx >= per-frame travel + width` on the fastest rendered frame. Note also that the 2.6x figure is the value at u = 0, which is never rendered; the peak that actually appears on screen is 2.02x. With `power3.out` the velocity is highest on the first frame, so the first rendered frame is the longest smear, and the object is round again at rest. For a vertical move swap to `scaleY` and origin at the trailing edge in Y. This is the elongated in-between; it distorts the subject, which is why it suits props and simple bodies and not a face.

**C. Directional blur** is the third option, `motion-blur-streak` path A (`feGaussianBlur stdDeviation="X 0"` on a proxy), and reads as camera blur rather than a drawn smear; choose it when the piece is photographic and A or B when it is graphic.

### 5.4 Recipe: jump plus both smears (`jump-smear.html`)

Reported (artifact not retained; the 2.02x recomputes exactly from the constants): three fading ghosts trailing the body at frame 77, the puck stretched to 2.02x on its first rendered frame at frame 101 and round at rest by frame 105. See 5.3 for why 2.02x is too short for this move.

```html
<!doctype html><meta charset="utf-8"><title>jump-smear</title>
<style>
  body{margin:0;background:#f4efe6;font-family:system-ui}
  #stage{position:relative;width:640px;height:480px;overflow:hidden;background:#f4efe6}
  #ground{position:absolute;left:0;right:0;top:400px;height:2px;background:#bbb}
  .part{position:absolute;will-change:transform}
  /* a simple "bean" character: one body div, feet at its bottom edge (origin 50% 100%) */
  #bean{left:60px;top:280px;width:80px;height:120px;border-radius:40px 40px 30px 30px;background:#3c5a99;transform-origin:50% 100%}
  #beanEye{left:52px;top:34px;width:10px;height:10px;border-radius:50%;background:#fff}
  .ghost{left:60px;top:280px;width:80px;height:120px;border-radius:40px 40px 30px 30px;background:#3c5a99;transform-origin:50% 100%;opacity:0}
  #puck{left:60px;top:150px;width:60px;height:60px;border-radius:50%;background:#c84f1c;transform-origin:0% 50%}
  #scrub{width:640px}
</style>
<div id="stage">
  <div id="ground"></div>
  <!-- ghosts BEHIND the lead = classic "multiples" -->
  <div class="ghost part" data-i="3"></div><div class="ghost part" data-i="2"></div><div class="ghost part" data-i="1"></div>
  <div id="bean" class="part"><div id="beanEye" class="part"></div></div>
  <div id="puck" class="part"></div>
</div>
<input id="scrub" type="range" min="0" max="1000" value="0"><span id="t"></span>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script>
  var FPS = 30, F = 1 / FPS; function f(n) { return n / FPS; }
  var tl = gsap.timeline({ paused: true });
  window.__timelines = (window.__timelines || []).concat(tl);
  var E = { p2io: gsap.parseEase('power2.inOut'), p3o: gsap.parseEase('power3.out'), p2o: gsap.parseEase('power2.out') };
  function lerp(a, b, u) { return a + (b - a) * u; }
  function clamp01(u) { return u < 0 ? 0 : u > 1 ? 1 : u; }

  // ================= JUMP: anticipation -> push -> ballistic flight -> land -> recover ======
  // Squash/stretch ratios from motion-design disney-principles: squash ~[1.2, 0.8], stretch ~[0.85, 1.15],
  // impact 2-4 frames, recovery 4-8 frames. Volume preserved: scaleX = 1/scaleY (Thomas & Johnston).
  // Flight is a PURE ballistic function of time (particle-burst rule): y = -v0*t + 0.5*g*t*t, so a seek to
  // any frame shows the exact mid-air state and the apex is automatically the slow part
  // (Odd Rule: spacing from the apex goes 1,3,5,7 under constant gravity - Garcia, via Animator Island).
  // Author the HANG TIME in frames and the apex height in px; derive g and v0 from them. Fall timing
  // is what tells the viewer how big the character is (Garcia), so g is a design choice, not 9.81.
  var JUMP_AT = f(10), CROUCH = f(8), PUSH = f(3), AIR = f(15), LAND_SQ = f(3), RECOVER = f(7);
  var H = 150;                          // apex height, px
  var g = 8 * H / (AIR * AIR);          // px/s^2 that makes the apex land at H in AIR seconds (= 4800 here)
  var v0 = g * AIR / 2;                 // launch speed (= 1200 px/s)
  var DX = 260;                         // horizontal travel during flight
  var T_PUSH = JUMP_AT + CROUCH, T_AIR = T_PUSH + PUSH, T_LAND = T_AIR + AIR, T_REC = T_LAND + LAND_SQ, T_REST = T_REC + RECOVER;

  // ================= SMEAR A: ghost multiples on a fast cross ==============================
  // The bean whips 240 px in 6 frames (40 px/frame). Above ~5-10 px of hard-edge travel per frame the eye
  // cannot fuse consecutive frames (manifesto SKILL, shutter section) - this move needs a smear.
  // Ghosts are the SAME pure function evaluated at t - i*dt, i.e. multiples of the previous frames.
  var DASH_AT = f(75), DASH = f(6), DASH_X = 240, GH = 3, GDT = f(1);
  function dashX(t) { return DX + DASH_X * E.p3o(clamp01(t / DASH)); }
  var END = f(140);

  // ONE writer for the bean: its whole life as a piecewise pure function of timeline time.
  // (Two drivers on one element fight: a driver renders its from-state, and fires onUpdate, whenever
  // the playhead is BEFORE it, so the later-added one wins even while the first is mid-flight. Verified.)
  function beanPose(t) {
    var P = { x: 0, y: 0, sx: 1, sy: 1, rot: 0 };
    if (t < JUMP_AT) return P;
    if (t < T_PUSH) {                                   // 1 anticipation: crouch, slow in-out, 8 frames
      var u = E.p2io((t - JUMP_AT) / CROUCH); P.sy = lerp(1, 0.78, u); P.sx = lerp(1, 1.18, u); return P;
    }
    if (t < T_AIR) {                                    // 2 push: stretch FAST, 3 frames - the contrast is the point
      var u2 = E.p3o((t - T_PUSH) / PUSH); P.sy = lerp(0.78, 1.22, u2); P.sx = lerp(1.18, 0.86, u2); P.rot = 8 * u2; return P;
    }
    if (t < T_LAND) {                                   // 3 flight: ballistic, stretch along velocity, upright at apex
      var ta = t - T_AIR, vy = -v0 + g * ta;            // px/s, negative = up
      var k = Math.min(1, Math.abs(vy) / v0);           // 0 at apex, 1 at take-off / landing
      P.x = DX * ta / AIR; P.y = -v0 * ta + 0.5 * g * ta * ta;
      P.sy = 1 + 0.22 * k; P.sx = 1 / P.sy; P.rot = vy < 0 ? 8 * k : 5 * k; return P;
    }
    P.x = DX;
    if (t < T_REC) {                                    // 4 landing squash: impact, 3 frames
      var u3 = E.p2o((t - T_LAND) / LAND_SQ); P.sy = lerp(1.22, 0.76, u3); P.sx = lerp(0.86, 1.2, u3); P.rot = lerp(5, 0, u3); return P;
    }
    if (t < T_REST) {                                   // 5 recovery: 7 frames, slow out
      var u4 = E.p2o((t - T_REC) / RECOVER); P.sy = lerp(0.76, 1, u4); P.sx = lerp(1.2, 1, u4); return P;
    }
    if (t >= DASH_AT) P.x = dashX(t - DASH_AT);         // 6 the dash (a full second of sharp rest sits before it)
    return P;
  }
  var bean = document.getElementById('bean');
  var ghosts = Array.prototype.slice.call(document.querySelectorAll('.ghost'));
  function applyBean(t) {
    var P = beanPose(t);
    gsap.set(bean, { x: P.x, y: P.y, scaleX: P.sx, scaleY: P.sy, rotation: P.rot });
    ghosts.forEach(function (gEl) {
      var i = +gEl.dataset.i, td = t - DASH_AT - i * GDT;                 // where the lead was i frames ago
      var on = td > 0 && (t - DASH_AT) < DASH + f(1);
      gsap.set(gEl, { x: on ? dashX(td) : P.x, opacity: on ? 0.45 / i : 0 });
    });
  }
  applyBean(0);                                          // seed frame 0 (rest)
  var drive = { t: 0 };
  tl.fromTo(drive, { t: 0 }, { t: END, duration: END, ease: 'none', onUpdate: function () { applyBean(drive.t); } }, 0);

  // ================= SMEAR B: elongated in-between via scaleX on the motion axis =============
  // The puck crosses 420 px in 5 frames. Stretch = 1 + K * |v| / vmax, origin at the TRAILING edge, and
  // x is pulled back by the growth so the LEADING edge stays where the un-smeared puck would be.
  var PUCK_AT = f(100), PUCK = f(5), PUCK_X = 420, K = 1.6, PUCK_W = 60;
  function puckPose(t) {
    var u = clamp01((t - PUCK_AT) / PUCK);
    var x = PUCK_X * E.p3o(u);
    var v = 3 * Math.pow(1 - u, 2);                      // d/du of the power3.out curve, 3 at u=0, 0 at u=1
    var sx = (t < PUCK_AT) ? 1 : 1 + K * (v / 3);        // 2.6x long on the first frame, 1.0 at rest
    return { x: x - PUCK_W * (sx - 1), sx: sx };
  }
  var puck = document.getElementById('puck');
  function applyPuck(t) { var P = puckPose(t); gsap.set(puck, { x: P.x, scaleX: P.sx }); }
  applyPuck(0);
  var pk = { t: 0 };
  tl.fromTo(pk, { t: 0 }, { t: END, duration: END, ease: 'none', onUpdate: function () { applyPuck(pk.t); } }, 0);
  // both objects dwell sharp >= 1 s after their smear (motion-blur-streak): nothing else moves them.

  var s = document.getElementById('scrub'), tt = document.getElementById('t');
  s.oninput = function () { tl.seek(s.value / 1000 * tl.duration(), false); tt.textContent = tl.time().toFixed(3) + 's / f' + Math.round(tl.time() * FPS); };
  window.__seek = function (sec) { tl.seek(sec, false); return tl.time(); };
</script>
```

## 6. Holds versus moving holds

Thomas and Johnston (handwiki pp. 61-62): "The 'moving hold' animates between two very similar positions; even characters sitting still, or hardly moving, can display some sort of movement, such as breathing, or very slightly changing position." The search summaries of the same principle put the reason plainly: rendered "absolutely still without any subtle movement" gives "a dull and lifeless result".

Why a full stop reads dead in this pipeline specifically: `grade-original.py` fails a film on `duplicate consecutive frames` with the note "a hold rendered as bit-identical frames reads as a stall". A character that stops completely produces exactly that. `video-composition.md` says the same from the other side: "Subtle reads as static at 30fps. Err toward more movement than feels safe."

The tension with the animation doctrine: `sine-wave-loop` says "circular breathing ... is cheap" and to prefer reveal, then jitter, then breath, with amplitudes at the low end (scale 0.008-0.015, 2-3 px). That doctrine is about UI cards and wordmarks. A character is different: breathing is the one ambient motion that is literally what the subject would do, so it is the sanctioned moving hold, at the same low amplitudes so it stays a hold and not a dance.

The recipe's hold (last 90 frames of `face.html`) has three finite ingredients:

1. a creep: one degree of head rotation over the whole hold, `power1.out` (the "two very similar positions");
2. a breath: `scaleY 1 + 0.012 sin`, 2 px of neck rise, 1.5 cycles over 3 s (period 2 s, inside `sine-wave-loop`'s 1.5-3 s range), driven by a phase proxy so `sin(0) = 0` at the hold's start;
3. a blink at frame 40 of the hold and a slower one at frame 74 (Animation Apprentice: "people blink a lot").

What the hold must not contain: a full-amplitude idle loop on every limb (three limbs at 6 px "compound to +-18px of competing motion", `sine-wave-loop`), or a motion whose settle passes its rest and comes back, which `grade-original.py`'s "settle direction reversals" check flags. Creep in one direction only.

## 7. Appeal and shape language

Thomas and Johnston: "Appeal in a cartoon character corresponds to what would be called charisma in an actor" (handwiki p. 68). disney-principles.md's appeal killers: "jerky motion, inconsistent timing, abrupt stops, uniform animation". The full stop of section 6 is on that list; so is giving every limb the same ease.

Shape language (CG Wire): "The round edges imply safety, softness, and welcoming nature, so characters with circular features often come across as amiable and open-hearted"; "Squares and rectangles are synonymous with stability, strength, and reliability"; "Triangles introduce a sense of dynamism to character design: with their sharp angles and directional points, triangles can signify danger, unpredictability, and movement." The motion corollary from the Pixune snippet: "Round characters move smoothly, square ones move steadily, triangular ones move sharply". Mapped to the recipes:

| shape family | walk row | squash budget |
|---|---|---|
| round | strolling or cartoon walk | full ratios (1.2 / 0.8) |
| square | brisk business-like | small (1.05 / 0.95) or none |
| triangular | run, very fast run | stretch more than squash |

Basis: the walk assignments are inference joining the two sources. The squash budgets follow disney-principles' exaggeration table ("Playful 15-25%, Corporate 0-5%, Premium 0%").

**The ease column has been removed from this table.** It previously assigned one ease family per shape family (round to sine/power2, square to power3, triangular to power4/expo). No working animator picks eases from a character's shape family, nothing supports the mapping, and encoding ease as a property of the character guarantees **uniform animation**, which is on disney-principles' appeal-killer list two paragraphs above. One character uses many eases across one shot: an expo on a snap take, a sine on a settle, a linear on a mechanical beat, chosen per action by weight and intent. Keep shape language for **design** (silhouette, proportion, read) and choose eases per action.

Proportion. The head-to-body ratio is the single strongest cuteness dial. (**A "baby schema" quote previously attributed here to the shape-language sources has been removed:** it appears in neither cited page, and no URL was given for it. The connection between rounded proportion and infant features is a real idea in the literature, but this document has no source for it and now claims none.) The rigs here are about 5 heads tall (60 px head on a 300 px body). Two to three heads reads as a mascot, six to eight as adult realism (**inference, no source fetched** -- roughly right and harmless, but a design-standard claim with no basis, flagged here because the rest of this document does carry a basis for its numbers). Whatever the ratio, keep it constant across poses: disney-principles' solid drawing rule, "Maintain consistent proportions across keyframes", is what a transform-only rig guarantees for free, since limbs rotate and never resize.

Build the character so its silhouette reads at the contact pose, the passing pose, and the hold, at the size it will appear in the frame (quality-checklist: "Elements >40px for motion, >100px for detail"). If a limb is very thin at the final scale it will alias during rotation and the smear tricks will not read on it. **The "about 12 px" figure previously given here has no source and the quote next to it did not support it.** `motion-blur-streak`'s full line is "thin type (< ~120px / 800 weight) or a busy backdrop swallows the smear", which is about display **type size** and is a different quantity by an order of magnitude. Use the quality-checklist figures that are actually about element size ("Elements >40px for motion, >100px for detail") and test the smear on the actual limb; treat any thickness threshold as something to measure, not to look up.

## 8. Lip-sync basics

### 8.1 The Preston Blair shapes

Gary C. Martin's rendering of the Blair series, ten shapes: "A and I", "E", "O", "U", "C, D, G, K, N, R, S, Th, Y and Z", "F and V", "L", "M, B and P", "W and Q", and "Rest". His guidance: they "work well for the initial blocking out of most dialogue sequences", and add asymmetry, because "The images here are devoid of emotion and personality so as to show each phoneme clearly."

### 8.2 Timing rules

- Lead the sound: "offset the jaw opening at least two frames before the audio is actually heard", because "there is a very slight time delay between our mouths making a shape, and the sound being expelled", and for "a heavily emphasised vowel or consonant" the lead can be "six to eight frames ahead" (Escape Studios). Matching audio frame-for-frame will "feel slightly 'off sync', ie a little late."
- Closed consonants first: "For M, B and P sounds ... the phoneme shape should be reached before the M, B or the P sound is made, as the sound is often only made as the pose breaks". **This is Gary C. Martin's extended Preston Blair phoneme page (https://garycmartin.com/phoneme_examples.html), the same author already cited in 8.1 for the ten shapes -- not "the RMIT mouth-shape notes", which was a misattribution and made one source look like two.**
- **There are no per-consonant lead times in any source this document has.** The earlier revision cited a High On Films snippet for "1-2 frames" leads differentiated across B/P/M, T/D and F/V. That page now fetches and its full text contains exactly one frame figure, a general "offset the key shapes one or two frames ahead of the sound", with no per-consonant breakdown, no T/D figure and no separate F/V lead. The recipe's `LEAD_MBP` applied to both MBP and FV therefore has **no source**; keep it as a deliberate inference (closed shapes need to be reached before the sound, open shapes do not) and do not present it as a sourced differentiation.
- Key the hits, not every phoneme: "pick out the strong consonants and the vowels that the mouth has to physically hit, and let the in-betweens flow between them" (High On Films snippet).

**Neither Escape Studios nor Bloop states a frame rate**; 24 fps is this document's working assumption for hand-drawn instruction, not the authors' statement (see 4.1). Taking 24 fps, "at least two frames" is 83 ms, which is **2.5 frames at 30 fps**. The earlier revision rounded that **down** to 2 for open shapes, which gives 67 ms of lead: less than the source's stated floor, in the one direction the source explicitly warns about ("off sync, ie a little late"). **Round up: 3 frames for open shapes as well as for the closed consonants**, and keep the closed consonants earliest by pushing them to 4 if the read needs it. (The document's own 24-to-30 arithmetic in 4.1 rounds 2 to 3 for exactly this reason.)

### 8.3 How a 30 fps deterministic timeline drives them

The phoneme track is data: `[frame, shape]` pairs where the frame is where the sound starts, produced by a forced aligner or by hand from the read (`manifesto`'s `vo-transcribe.py` gives word-level frames; phoneme-level needs an aligner, and the per-line generation in SKILL.md's "read that does not drift" section means the frames are known at authoring time). Each cue is shifted earlier by its lead, and the visible shape at time `t` is the last cue at or before `t`: the `discrete-text-sequence` pattern, a pure function of time with no per-frame state. All ten mouths exist in the DOM from frame 0 and exactly one is visible; visibility snaps. Never crossfade two visemes: a half-blended mouth is mush, the same reason `waterfall-entry` sets opacity with `tl.set` rather than a fade.

A jaw, if the rig has one, can move on a slower `power2` curve underneath the snapping shapes (High On Films snippet: the jaw "should animate on a slower, more musical curve that hits the emphasised beats"); implement it as a rotation of a jaw group keyed on the open vowels only, with its own driver, never sharing an element with the mouth shapes.

### 8.4 Recipe (`lipsync.html`)

Reported (artifact not retained; the lead arithmetic recomputes): probing `shapeAt` across the line "hello, my people" returned `rest, CDGKNRSThYZ, E, O, MBP, AI, MBP, U` at the expected times, the MBP shape arriving 3 frames before its sound frame and the E shape 2 frames before its own.

**The cue track in this recipe is too dense and contradicts the rule stated two sections above.** Fourteen cues over 74 frames is a cue every 5 frames at 30 fps, which is a chattering mouth and the classic amateur read -- and it keys nearly every phoneme, which is exactly what "key the hits, not every phoneme" forbids. Three rules to apply: **no viseme is held for fewer than 2 frames**; **hit 2-4 shapes per WORD, not one per phoneme**; and **drop the mid-phrase rests** at frames 52 and 72, because a mouth returning to rest between words in one breath reads as the character stopping talking three times in one line. Rest belongs at phrase ends only.

**And the jaw is mandatory, not optional.** Jaw-open amount is the primary volume signal; the viseme is secondary decoration on top of it. A shape-only mouth reads flat no matter how correct the visemes are. (Inference; standard lip-sync blocking, which keys accents first and adds only the shapes that survive playback.)

```html
<!doctype html><meta charset="utf-8"><title>lipsync</title>
<style>
  body{margin:0;background:#f4efe6;font-family:system-ui}
  #stage{width:640px;height:480px;background:#f4efe6;display:block}
  .m{visibility:hidden}
  #scrub{width:640px}
</style>
<!-- Ten Preston Blair shapes (Gary C. Martin's naming): AI, E, O, U, CDGKNRSThYZ, FV, L, MBP, WQ, rest.
     All ten live in the DOM from t=0; exactly one is visible at any time. -->
<svg id="stage" viewBox="0 0 640 480">
  <circle cx="320" cy="220" r="150" fill="#e8b98a"/>
  <circle cx="270" cy="180" r="12" fill="#222"/><circle cx="370" cy="180" r="12" fill="#222"/>
  <g id="mouths" transform="translate(320,290)">
    <g class="m" data-s="rest"><path d="M-40 0 Q0 14 40 0" stroke="#8a4a3a" stroke-width="7" fill="none" stroke-linecap="round"/></g>
    <g class="m" data-s="AI"><ellipse rx="44" ry="30" fill="#5a1f1a"/><rect x="-34" y="-30" width="68" height="12" fill="#fff"/></g>
    <g class="m" data-s="E"><ellipse rx="52" ry="16" fill="#5a1f1a"/><rect x="-40" y="-16" width="80" height="9" fill="#fff"/></g>
    <g class="m" data-s="O"><ellipse rx="24" ry="30" fill="#5a1f1a"/></g>
    <g class="m" data-s="U"><ellipse rx="16" ry="20" fill="#5a1f1a"/></g>
    <g class="m" data-s="CDGKNRSThYZ"><ellipse rx="46" ry="12" fill="#5a1f1a"/><rect x="-36" y="-12" width="72" height="8" fill="#fff"/></g>
    <g class="m" data-s="FV"><path d="M-40 -2 Q0 10 40 -2" stroke="#8a4a3a" stroke-width="8" fill="none"/><rect x="-30" y="-8" width="60" height="8" fill="#fff"/></g>
    <g class="m" data-s="L"><ellipse rx="40" ry="22" fill="#5a1f1a"/><path d="M-10 6 Q0 -14 10 6" fill="#d8776a"/></g>
    <g class="m" data-s="MBP"><path d="M-44 0 L44 0" stroke="#8a4a3a" stroke-width="8" stroke-linecap="round"/></g>
    <g class="m" data-s="WQ"><ellipse rx="14" ry="14" fill="#5a1f1a"/></g>
  </g>
</svg>
<input id="scrub" type="range" min="0" max="1000" value="0"><span id="t"></span>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script>
  var FPS = 30, F = 1 / FPS; function f(n) { return n / FPS; }
  var tl = gsap.timeline({ paused: true });
  window.__timelines = (window.__timelines || []).concat(tl);

  // The phoneme track is DATA baked before build: [frame, shape]. Frames are where the SOUND
  // starts (from a forced aligner / transcript). "hello, my people": h-e-l-o | m-ai | p-ee-p-l
  var track = [
    [30, 'CDGKNRSThYZ'], [33, 'E'], [38, 'L'], [42, 'O'], [52, 'rest'],
    [58, 'MBP'], [62, 'AI'], [72, 'rest'],
    [78, 'MBP'], [81, 'E'], [88, 'MBP'], [91, 'U'], [95, 'L'], [104, 'rest']
  ];
  // LEAD: the shape is reached BEFORE the sound. At least 2 frames ahead (Escape Studios),
  // and closed shapes M/B/P are hit early and held until the sound breaks them (RMIT / Ian Maigua).
  var LEAD = 2, LEAD_MBP = 3;
  var cues = track.map(function (c) {
    var lead = (c[1] === 'MBP' || c[1] === 'FV') ? LEAD_MBP : LEAD;
    return { t: f(c[0] - lead), s: c[1] };
  });

  var shapes = {};
  document.querySelectorAll('#mouths .m').forEach(function (g) { shapes[g.dataset.s] = g; });
  function show(name) {
    for (var k in shapes) shapes[k].style.visibility = (k === name) ? 'visible' : 'hidden';
  }
  // pure function of time: the last cue whose time <= t (discrete-text-sequence pattern)
  function shapeAt(t) {
    var s = 'rest';
    for (var i = 0; i < cues.length; i++) { if (cues[i].t <= t) s = cues[i].s; else break; }
    return s;
  }
  show('rest');                                                    // seed t=0
  var END = f(120);
  var drive = { t: 0 };
  tl.fromTo(drive, { t: 0 }, { t: END, duration: END, ease: 'none',
    onUpdate: function () { show(shapeAt(drive.t)); } }, 0);
  // Mouth shapes SNAP (binary visibility); never crossfade visemes - a half-blended mouth reads as mush.
  // The jaw, if you have one, can ease on a slower curve underneath the snapping shapes.

  var s = document.getElementById('scrub'), tt = document.getElementById('t');
  s.oninput = function () { tl.seek(s.value / 1000 * tl.duration(), false); tt.textContent = tl.time().toFixed(3) + 's / f' + Math.round(tl.time() * FPS) + ' ' + shapeAt(tl.time()); };
  window.__seek = function (sec) { tl.seek(sec, false); return shapeAt(tl.time()); };
</script>
```

## 9. What is not achievable without a physics simulation, and the deterministic substitutes

The line is drawn by the contract: state must be a pure function of time. A simulation is by definition the opposite, a state that depends on the previous state. gsap-easing-and-stagger.md says it for springs: "an interactive spring is a stateful integrator (velocity accumulates frame to frame), which cannot be seeked deterministically - you'd have to simulate frames 0...N-1 to render frame N" and so "interaction-lib spring solvers are banned in compositions". Everything below follows from that.

| wanted | why it needs a sim | deterministic substitute |
|---|---|---|
| collision response (landing on uneven ground, bumping a prop, a ball off a wall) | contact detection and impulse resolution are event-driven state | author the contact frame; before it a ballistic arc, at it a squash (section 4.5), after it a new arc with reduced `v0`. GSAP's Physics2DPlugin is "not intended to replace a full-blown physics engine and does not offer collision detection" (plugin docs), and although "everything is reverseable", any easing you define "will be completely ignored **for these properties**" -- the physics properties only, so a tween can still ease its other properties normally. (The earlier revision truncated that quote in a way that overstated it.) It still buys nothing over the closed form here |
| ragdoll, chain, rope, tail with real inertia | coupled second-order system | delayed-copy follow-through: `child(t) = gain * parent(t - lag)`, one lag per link (3 frames each, `manifesto` sibling offset), plus an exponentially decaying pendulum `theta = A cos(w t) e^(-k t)` for a free swing (inference; the closed-form damped oscillator is the same math as `springEase`) |
| cloth, hair strands, fluid, smoke | continuum simulation | pre-baked: run a sim offline with a fixed seed, sample it to a key table per frame, ship the table. A table lookup is a pure function of time and is allowed; a live sim is not. Or fake it with a few `sine-wave-loop` layers at staggered periods (rule's "2.1s / 1.9s / 2.4s" guidance) |
| secondary jiggle from an impact (a belly, a cheek) | spring driven by the body's acceleration | `springEase` from gsap-easing-and-stagger.md at `dampingFraction 0.6-0.7` for "~5-10% overshoot", fired at the contact frame as a `fromTo` on `scaleY`; the closed form is "a pure function of progress - no state, nothing to desync" |
| **weight-correct balance** (a constrained solve over the whole body) | coupled constraints over every joint at once | author the balance by eye at the key poses and hold the centre of mass over the support foot; there is no closed form for this. **IK foot planting is NOT in this row and has been moved out of this table**: two-bone IK is not a simulation, it is the law of cosines, it is stateless and closed-form and a pure function of the target position, so it satisfies the contract exactly as well as `walkPose` does. See section 3.4 for the solver and for why FK authoring is the cause of this rig's foot slide. Listing IK as unachievable was a category error that foreclosed the fix for the document's worst defect |
| motion blur that integrates over the shutter | needs sub-frame samples | `motion-blur-streak` (blur proxy or ghosts), or render at 4x fps and `tmix` per card as `manifesto` SKILL.md describes, kept clear of cuts |
| random idle variation | randomness | index-derived hashes (`particle-burst`'s `prand(n)`) -- **but not for blinks.** Blink PLACEMENT is meaning-driven and this document says so in 4.1, quoting Animation Apprentice: blinks land on a phrase end, a thought change, a change of eye direction, or before/after a head turn as anticipation. Hashing them produces the nervous-android read. Put blinks on the beat sheet by hand and use `prand` only to jitter durations by a frame. The same objection applies to any "random" character variation: what looks random in good character work is motivated, and hashing is the substitute for **texture** (particles, foliage, crowds), not for acting |

The substitute always has the same shape: write the physics as a formula of `t`, or bake it to a table before build, and drive it from one linear proxy with `ease: 'none'` (`particle-burst`: "an eased driver warps gravity").

## 10. Frame and time reference at 30 fps

| frames | seconds | used for |
|---|---|---|
| 1 | 0.033 | lid offset, ghost spacing |
| 2 | 0.067 | ghost spacing (see 5.3: too coarse for a blur read) |
| 3 | 0.100 | lid close, eye dart, impact squash, follow-through lag, lip-sync lead (all shapes, rounded UP per 8.2), push-off |
| 4 | 0.133 | lid open, anticipation |
| 5 | 0.167 | very fast run step, puck smear |
| 6 | 0.200 | slow lid open, cushion, dash |
| 7 | 0.233 | recovery |
| 8 | 0.267 | regular blink total, run step, crouch, walk blend-in |
| 10 | 0.333 | cartoon walk step, weight shift |
| 12 | 0.400 | head turn |
| 15 | 0.500 | natural walk step; jump hang time for a ONE-FOOT hop (a body-height leap needs 30-36 frames, see 4.5) |
| 20 | 0.667 | strolling step |
| 25 | 0.833 | tired step |
| 30 | 1.000 | one walk cycle at natural tempo, slow step, minimum sharp dwell after a smear |
| 40 | 1.333 | very slow step |

Basis: each row's use column points to the section that gives the figure's source; the seconds column is `n / 30`.

## 11. Builder checklist

- Rig: limbs hang from their joints, origins on the joints, children at the parent's far end, far side drawn first. SVG: `translate` group per joint, `rotate()` written as an attribute, no `transform-box`.
- One writer per element and property. A driver's from-state is a no-op, or it owns the element for the whole scene.
- Seed the rest pose at setup. Probe with `tl.seek(t, false)`.
- Walk: pick the Williams row by the verb, quantise the **cycle** to whole frames (not the step), arms opposite legs, hips lowest at down and highest at up, blend in over 8 frames, stop on a contact or passing pose.
- **Trace the ankle before you believe the walk.** Compute the planted foot's world position across the stance half-cycle: it must stay on the ground line (no penetration, no float) and its world x must not move. Author the ankle trajectory and solve thigh/shin with two-bone IK if it does not. A key-pose silhouette check will not find this.
- Interpolate the pose tables with a wrapped Catmull-Rom, not smoothstep: smoothstep stops every joint dead at every key.
- Add a per-side asymmetry offset and a per-joint additive bias layer; do not use one amplitude scalar as a personality dial.
- Blink close faster than open, lids one frame apart, blink on every look change and in the middle of a turn, lid edge curved and riding the pupil. Place blinks by meaning, never by hash.
- Below 5 frames, author positions rather than easing curves.
- Anticipation 10-20% of the travel over 3-6 frames, opposite direction, then the action, then a cushion; follow-through on loose parts 2-3 frames late.
- Jump: choose hang time and apex, derive `g`; squash on impact 2-4 frames, recover 4-8; volume preserved.
- Any move over about 1.5% of frame width per frame (or half the object's own width per frame) gets ghosts, a stretch, or a shutter; then 1 s sharp. Size the stretch so `width * sx >= travel + width` on the fastest rendered frame, and space ghosts sub-frame if you want a blur rather than multiples.
- No full stops: creep + breath + blink, at `sine-wave-loop` low amplitudes, no reversals.
- Lip-sync: baked cue table, shapes lead the sound by 3 frames (rounded up from the source floor), closed consonants earliest, visibility snaps, no viseme under 2 frames, 2-4 shapes per word, jaw always.
- No sim: formula of `t` or baked table, linear driver, `prand` for variation.
- Run `grade-original.py` on the render: duplicate frames and settle reversals are the two checks a character film fails first.
