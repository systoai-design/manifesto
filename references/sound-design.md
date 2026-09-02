# Sound design for motion graphics, synthesised deterministically

Research note for the `manifesto` skill. Everything here is written to be built under the
HyperFrames contract the skill already uses for picture: one paused timeline, state a pure
function of time, no randomness that is not seeded, finite everything. The audio side has the
same shape: one stem rendered offline by a script whose output is a pure function of the cut
list and a seed, muxed under the render.

Every number below carries a basis. "Source" means a named document you can open. "Inference"
means my own reasoning from those sources, and should be tested on the film before it is
treated as a rule.

Local material this note builds on and does not repeat:

- `<skill>/SKILL.md`, in particular the closing "Sound" section
  (the one principle it already states: match the sound's character to the motion's, and a
  film whose cuts are silent reads unfinished), the "Composing a replacement bed" section,
  and "Placing a music bed under a voice".
- `<skill>/scripts/segment.mjs` (the cut list), `audio-beats.mjs`
  (onsets and cut-to-onset lock), `bed-compose.py` (the synthesised bed), `vo-mix.py` and
  `vo-verify.py` (sample placement and energy-onset verification), `grade-original.py`
  (the audio checks a finished film must pass).
- `<skills>/motion-design/director/disney-principles.md`, `director/choreography.md`,
  `reference/timing-easing-tables.md`, `reference/quality-checklist.md` (LottieFiles, MIT).
- `<skills>/hyperframes-animation/rules-index.md` (the contract),
  `rules/kinetic-beat-slam.md`, `techniques.md` (velocity-matched transitions, audio-reactive),
  `transitions/overview.md`; `<skills>/hyperframes-creative/references/
  beat-direction.md` (the motion-verb vocabulary and its "SFX cues" heading),
  `motion-principles.md`, `video-composition.md`, `typography.md` (HeyGen, Apache-2.0).
- `<skills>/media-use/audio/references/sfx.md` and
  `assets/sfx/manifest.json` (the bundled 21-file library and its placement hints),
  `<skills>/hyperframes-audio/` (carve groups, `ebur128` recipe).

---

**Revision 2 (2026-09-02).** Corrected against a practitioner review that ran this
document's own code. Four of the seven synthesis recipes would not pass a client review as
written: the whoosh had an instantaneous attack on white noise with a 94 Hz block buzz, the
impact had no body and no tail, the shimmer was a diminished chord, the riser flutters. The
document also contradicted itself on whoosh placement, and five figures that read as rules
were inferences. Six things a professional reaches for first were absent entirely: panning,
space, the pre-hit drop, key-tuning, per-instance variation and a master limiter. Every
change is in `corrections.md` in this directory.

## 1. Why a mix with no SFX reads unfinished

State the failure first, because it is the reason this note exists.

A motion-graphics film with a music bed and no designed sound has two streams that do not
touch. The picture cuts on frames the edit chose; the music is continuous and carries its own
grid. Nothing in the audio acknowledges that a card just landed, that a word just rose, that
the ground just flipped. The viewer hears music playing *near* a video rather than *with* it.

Three things are known about why this fails:

1. **Sound and picture weld when they coincide, and the weld is involuntary.** Chion calls it
   synchresis, "the spontaneous and irresistible weld produced between a particular auditory
   phenomenon and visual phenomenon when they occur at the same time" (Chion, *Audio-Vision*,
   1994, as quoted at https://blog.animationstudies.org/?p=3216 and
   https://www.shapingwaves.com/13016/). It is why any of a hundred sounds will do for a
   hammer shot. The converse is the problem: when nothing coincides, nothing welds, and the
   picture is experienced as mute. The bed does not count, because it does not coincide with
   anything in particular.
2. **Motion without sound is read as an absence, not as neutral.** "Our brains are used to
   hearing, and it's therefore unnatural not to associate sound with movement"
   (https://mowe.studio/animation-sound-design-effects-music-motion-graphics/). Titeux makes
   the same point from the other direction: the identical moving white disc becomes a
   basketball or a tennis ball depending only on the sound put under it
   (https://www.nicolastiteux.com/en/blog/sound-design-for-motion-design/). Silent motion has
   no material; it reads as a template.
3. **The skill's own finding.** `manifesto/SKILL.md` closing section: "A film whose cuts are
   silent reads unfinished even when the picture is right, and this is usually the cheapest
   remaining improvement once the visuals converge." The Apple-cascade section says the same
   for smooth motion: "A cascade with a soft transient per line reads far more finished than a
   silent one."

What it actually sounds like to a viewer (inference from the above, stated so a builder can
recognise it in a review): the piece feels like a slideshow with a soundtrack. Cuts feel
abrupt because nothing cushions or announces them. Big reveals feel small because the ear got
no weight. Fast moves feel weightless. Stagger and typing reveals feel like a rendering
artefact rather than a performance. And, because the bed is doing all the work, any point where
the bed is quiet exposes total silence, which on a phone speaker reads as "the audio dropped
out". The fix is not more music. It is a small number of transients placed on the frames the
edit already chose.

A companion failure exists and is worth naming so the fix does not overshoot: sounding every
movement. Connor (same animationstudies post) calls it mickey-mousing, notes Chuck Jones
complained about it in 1946, and describes the effect as a comfort dip similar to an uncanny
valley. Selective synchrony, sound meeting picture at the moments that matter, is the target.

---

## 2. The sound-to-motion mapping

The mapping below is the practitioner consensus, cross-referenced to the motion vocabulary the
build side already uses. Where a source gives the pairing it is cited; where the pairing is
common practice restated in this note's terms, it is marked as such.

### 2.1 Anchor point first

Before the table: every sound class has one sample that must land on one frame. Call it the
anchor. Get this wrong and the class is wrong regardless of timbre.

| Class | Anchor sample | Lands on |
| --- | --- | --- |
| Impact, thud, boom, click, tick, pop | the transient onset (first sample of the click) | the frame the motion becomes **imperceptible**, not the frame the tween ends, or the cut frame. See the note below |
| Whoosh | the loudest sample (peak of the amplitude envelope) | the frame of **peak velocity**. The file starts 2-4 frames earlier, because a whoosh has a swell; see 4.2 |
| Riser, reverse swell | the **last** sample | the cut or reveal frame; the sound stops dead there |
| Sub-drop | the onset of the pitch fall | the reveal frame |
| Shimmer, glint | the onset | the frame the highlight crosses the glyph (or the first frame of the sweep) |

**"Velocity reaches zero" is the wrong settle frame for every hard `.out` ease.** For
`expo.out` the position is at 99% of target when t = 0.66 of the tween duration; the last
third is sub-pixel drift, which on a 0.5 s slide is 5 frames at 30 fps of motion nobody can
see. Anchoring on the tween's end frame puts the hit 3 to 6 frames late on every hard ease,
which is exactly the "reaction rather than coincidence" this document warns about in 3.2.
**Define the settle frame as the first frame where the fitted speed curve drops below a
visibility threshold** (1 px/frame at 1080p is a reasonable default; scale with resolution),
computed from the derivative table in 4.1. For `power4.out` and `expo.out` that lands at
roughly 55-70% of the tween duration. This matters most on the original-film path (6.1),
where cues come from `data-start` / `data-duration` and there is no pixel measurement to
save you; on the reference path, confirm whether `segment.mjs`'s `toFrame` already stops at
the sub-pixel floor. (Inference; the derivative table is this document's own.)

Basis: the bundled library's own placement hints say the same in words ("Trigger on the visual
landing", "Align so the swell peaks on the cut", "Trigger at (climax_time - 10.03s) so it crests
exactly on the reveal", `media-use/audio/assets/sfx/manifest.json`). The velocity rule for the
whoosh is inference from the Selfridge/Moffat/Reiss aeroacoustic model in section 4.2, where
level and centre frequency are both functions of speed.

### 2.2 The table

Motion signatures are given in the terms `segment.mjs` and `track.mjs` report, so a cue list
can be derived from measurements rather than from watching.

| Motion (what the picture does) | Signature in the measurement | Sound class | Notes and basis |
| --- | --- | --- | --- |
| Fast travel: a card or word slides, a whip pan, a push transition | `cx`/`cy` centroid run over >= 4 frames with a fitted ease; a velocity-matched transition (`techniques.md` section 10) | **whoosh**, band-passed noise whose level and pitch follow speed | Speed to pitch is the physics: Strouhal, f = St u / d (Selfridge, Moffat, Reiss 2017, *Appl. Sci.* 7(11):1177). "Match the whoosh speed to the transition timing" (https://pixflow.net/blog/cinematic-whoosh-sound-effects/). Manifest: `whoosh-short` 0.57 s "quick swipe/slide accent, fast element move". |
| Settle after travel; a slam; a hard cut onto a card; a ground flip | end of a centroid run; `bg` flips between segments; a `SLAMS / STAMPS / DROPS` verb in `beat-direction.md` | **impact** (thud): 50-90 Hz decaying sine with a short noise click on top | Disney principle 1: impact 2-4 frames, recovery 4-8 (`disney-principles.md`). Manifest `impact-bass-1`: "logo/hero snap, headline slam. Trigger on the visual landing". The click carries the frame; the sine carries the weight (inference, section 4.3). |
| Steps: typing, a counter incrementing, a stagger of items, a metronome chrome, a toggle | `words[]` reveal frames from column blocks; per-char `autoAlpha` at 0.02 s (`SKILL.md` technique map); `CLICKS / LOCKS IN / SNAPS / STEPS / TYPES ON` verbs | **tick / click**: 2-5 ms click with a short resonant tail | Manifest `click`: "Short accent, sync exactly to the on-screen action"; `key-press`: "sync to the typed character". Kinetic-beat-slam's metronome ticks flash on the same `PULSE` grid; the audio tick reads that grid too. |
| A build: elements assembling, a zoom pushing in, a scale ramp, the beat before the hero | a long monotonic `bboxW`/`bboxH` growth; the arc into a peak in `bed-compose.py`'s `ARC` | **riser**: noise with a rising filter over N seconds, ending exactly on the payoff | Manifest `riser`: 10.03 s, "peak at the end. Trigger at (climax_time - 10.03s)". `bed-compose.py` already places 30-44 frame risers into its three structural hits (`riser(108, 30, ...)`), so the bed and the SFX must not both do it (section 5.5). |
| A reveal: the logo lockup, the hero word, a full-frame wipe landing | first frame of the segment with the largest `gapBefore`; the `titlecard-reveal` / `logo-assemble-lockup` blueprints | **sub-drop / boom**: pitch-falling sine, 100-140 Hz down to 30-40 Hz | Kick-drum synthesis is the same object: pitch envelope on a sine settling to 40-60 Hz (https://www.perfectcircuit.com/signal/kick-drum-synthesis, https://modeaudio.com/magazine/drum-synth-sound-design-kick-snare). Manifest `impact-bass-2`: "brief anticipation then a deep hit. Place so the peak lands on the reveal". |
| A glint: a light sweep across a glyph, a gradient sweep, the liquid-glass rim glint, a sparkle | `gradient-text-sweep` rule; the rotating conic glint in `SKILL.md` liquid glass; a short spike in `edge` energy on one card | **shimmer**: a cluster of high detuned sines, fast attack, long decay | Manifest `sparkle`: "Bright sparkle / shimmer, magical reveal or 'shine' highlight on a hero element. Sync to the highlight." Synthesis is inference (section 4.7). |
| Into a cut: the last beats before a hard cut, a blackout, a section change | the 1-8 frame blank runs `segment.mjs` reports between cards; a `gapBefore` >= 6 | **reverse swell**: a reversed-cymbal shape, exponential rise, dead stop on the cut | Reverse-cymbal placement "1 or 2 bars ahead" of the section it leads into (https://www.pointblankmusicschool.com/blog/using-reversals-to-create-unique-transitions-in-your-tracks/). For a 26 s ad that is far too long; scale it to the gap plus the previous card's tail (inference, 0.4-1.0 s). Better: **scale it to a bar of the bed's own meter** rather than to an arbitrary window. At 150 BPM one bar is 1.6 s, so a one-bar swell into the two largest gaps is in range and lands on the grid, which an arbitrary 0.4-1.0 s does not. |
| A pop: scale 0 to 1 with `back.out`, a chip or badge appearing | `bboxW` and `bboxH` expand from centre (track.mjs decision table); `spring-pop-entrance` rule | **pop**: a tick whose resonator pitch rises over 20-40 ms | Manifest `pop` 0.72 s: "element appear/spawn, chip/tag/badge in. Small precise accent". Pitch-rise detail is inference. |
| Squash and stretch, a rubbery overshoot | a settle with a direction reversal (the thing `grade-original.py` flags as overshoot) | pitched, bending tone (rubber) | "bubbly sounds and rubbery stretches that ascend and descend in pitch" (https://www.krotosaudio.com/sound-effects-motion-graphics-tips/). Note the film that produced `grade-original.py` bans overshoot; if the motion law forbids it, so does the sound. |
| A cross-dissolve, a fade, a blur-through | corner luma ramps between two values across a boundary (`SKILL.md` product-UI section) | **nothing**, or air only | A dissolve has no instant; a transient on it invents one the picture does not show. Inference. |
| A blank gap between cards | `inkFrac ~ 0` run | **silence in the SFX stem** | The gaps are "why the reference breathes" (`SKILL.md` section 3.2). Sound placed inside a gap is a new event; the gap stops being a gap. Inference. |
| Ambient loop, breathing hold, slow Ken Burns | finite `yoyo` repeats, `sine.inOut` | **nothing** from the SFX stem; the bed carries it | Ambient motion sits under the 1/3 density rule (`choreography.md`); sounding it is mickey-mousing. Inference. |

### 2.3 Hierarchy: which motions get a sound

The choreography rules on the picture side transfer directly:

- **Lead with the hero.** "Hero gets largest displacement and most attention-grabbing easing;
  supporting elements are subtler in every dimension" (`choreography.md`). The hero move gets
  the transient; supporting elements get nothing or a quieter, shorter, higher one.
- **One primary action per timing beat** (`disney-principles.md`, Staging). One transient per
  beat is the audio equivalent. Two transients within a beat compete unless one is
  clearly subordinate (a soft tick under a whoosh is fine; two impacts are not).
- **Secondary action is 30-50 % of primary amplitude, 50-100 ms after it**
  (`disney-principles.md`, principle 8). The audio parallel: a secondary sound (a shadow
  growing, a ripple) sits 6-10 dB under the primary transient and 2-3 frames behind it
  (the dB figure is inference; the delay is the source's).
- **Shared motion events start within 50 ms** (`choreography.md`). When several elements react
  to one trigger they get **one** sound at the trigger, not one each.
- **Missing from this hierarchy, and the single most-used trailer and motion-graphics
  device: the pre-hit drop.** Cut the bed (and the stem) to silence 2 to 6 frames before a
  structural hit, then the hit. This document's own reference material contains it
  (`beat-direction.md` SFX cues: "On fold: drone cuts. Silence. Then a single clean chime.")
  and the section 3.2 gap analysis is almost there ("the gap is the edit breathing"), but
  the technique was never named or given a recipe. In HyperFrames it is a `data-automation`
  volume lane on the bed, or a hard-edited bed WAV; both are seek-safe. (Inference;
  universal trailer practice.)
- **Do not stack.** "Do not mindlessly stack! Always check if your addition provides value"
  (https://pitchdrift-productions.com/sound-design-tips-for-motion-graphics/). "Excessive Sound
  Layering and Audio Clutter" is one of eight named mistakes at
  https://sfxengine.com/blog/common-sound-design-mistakes-in-video-editing.

### 2.4 Match the sound's envelope to the ease

`SKILL.md`: "Smooth animation wants soft, low-transient sound; hard cuts want sharp ones." Make
it concrete. The GSAP ease that `segment.mjs` fits for a move is a position curve; its
derivative is the speed curve, and the speed curve is the whoosh's amplitude envelope. The
attack of a transient should match the attack of the settle:

| Fitted ease (from `beats.json`) | Picture character | Transient attack | Whoosh shape |
| --- | --- | --- | --- |
| `expo.out`, `power4.out` | snaps in, all the speed in the first 2-3 frames | hard: click 1-2 ms, resonator Q high | front-loaded, most energy in the first 20 % |
| `power2.out`, `power3.out` | confident deceleration | medium: click 3 ms | front-loaded, gentler tail |
| `back.out(n)` | overshoots and returns | click on the first arrival, softer second tick on the return if n >= 1.7 | front-loaded plus a small second bump at the reversal |
| `sine.inOut`, `power1.inOut` | glides | no transient; whoosh only | symmetric, peak at the midpoint |
| `power2.in`, `expo.in` (exits) | accelerates away | none on the exit; the cut it leads into gets the hit | back-loaded, ends at the cut |

Basis: the ease family list and its character descriptions are from
`hyperframes-animation/adapters/gsap-easing-and-stagger.md` via `kinetic-beat-slam.md`
("`power4.out` hard slam, `expo.out` hardest snap, `back.out(2)` overshoot pop, `circ.out`
heavy rise with momentum") and `motion-principles.md` ("`expo.out` = confident, `sine.inOut` =
dreamy, `elastic.out` = playful"). The mapping to click length and Q is inference.

---

## 3. Sync tolerances

### 3.1 What the research says

All figures use the ITU sign convention: **positive = sound leads (arrives before) picture,
negative = sound lags**.

| Source | Stimulus | Detectable | Acceptable | Note |
| --- | --- | --- | --- | --- |
| ITU-R BT.1359-1 (1998), text extracted from https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1359-1-199811-I!!PDF-E.pdf | female newsreader | +45 ms / -125 ms | +90 ms / -185 ms | "The range of timing between the 'just detectable' limits of sound leading and sound delayed is about 170 ms." Producer control zone +25 / -100 ms. Appendix 1 cites ITU-R BR.265: film sync accuracy within half a frame, "about +/- 22 ms" at 24 fps. |
| EBU R37 (2007), https://tech.ebu.ch/docs/r/r037.pdf | broadcast chain | | +40 ms / -60 ms end-to-end | Each stage: "Audio 5 ms early (sound before picture) to 15 ms late". |
| Dixon and Spitz 1980, *Perception* 9:719-721, https://journals.sagepub.com/doi/10.1068/p090719 (as summarised at https://pmc.ncbi.nlm.nih.gov/articles/PMC4451240/) | hammer hitting a peg | +75 ms / -188 ms | | Speech: +131 / -258 ms. "Asynchrony is more easily detected when sound precedes picture, and for a hammer hitting a peg than for someone speaking." |
| Vatakis and Spence 2006, *Brain Research* (summarised in the same PMC review) | action vs speech vs music | tighter for actions | | Temporal binding window "approximately 50-80 ms when audition leads to 150-250 ms when vision leads, depending on the complexity of the stimulus" (https://pmc.ncbi.nlm.nih.gov/articles/PMC4451240/). |
| Steinmetz 1996, *IEEE JSAC* 14(1):61-72, https://ieeexplore.ieee.org/document/481694 (figures as reported at https://link.springer.com/chapter/10.1007/978-3-319-65840-7_1) | lip sync | | +/-80 ms "acceptable"; -160 to +240 "noticeable but not annoying" | Reported second-hand; the primary was not fetched. |
| Ebenezer 2022, https://arxiv.org/abs/2212.01686 | sports broadcast | | | "humans are more sensitive to audio-video offset errors for speech stimuli, and the complex events that occur in sports broadcasts have higher thresholds of acceptability". |
| London 2004, *Hearing in Time*, lecture text at https://web.uvic.ca/~aschloss/course_mat/MUS%20511/ARTICLES%20AND%20REFS%20FOR%20320/Musical%20Meter.pdf | tapping to a metronome | | | "when you steadily keep time you are actually a bit ahead of the beat (20-40ms)", the negative asynchrony. |

Two things fall out of the table that matter for motion graphics specifically:

1. **The asymmetry is consistent and large.** Sound early is detected at roughly 40-60 % of the
   lag that sound late is detected at (45 vs 125, 75 vs 188, 131 vs 258, 40 vs 60). The usual
   explanation is that we are used to light arriving before sound
   (https://resi.io/glossary/audio-video-synchronization/). So if a placement error is
   unavoidable, err **late**, never early.
2. **Impulsive events are the tightest case.** BT.1359-1 says its figures come from a
   newsreader and "narrower limits may apply to the case of impulsive sounds" (search
   excerpt of the recommendation text; the extracted PDF confirms the newsreader test material).
   Dixon and Spitz measured the hammer at 75/188 against speech at 131/258. A motion-graphics
   hit is a hammer, not a newsreader.

### 3.2 The window where a hit reads as "on"

Combining the sources (this paragraph is inference from them, not a figure any one source
states):

- **Detection floor for an impulsive event: about +45 ms early, about -125 ms late** (the
  tightest published pair, BT.1359-1). The hammer study is looser (+75 / -188) but its
  method drifted the offset continuously and asked for a response, which raises thresholds.
- **A hit reads as "on" when its transient onset is within one frame of the picture event at
  30 fps** (33 ms), which sits inside every detection threshold in the table with margin on the
  late side and almost none on the early side. At 60 fps the same rule gives 17 ms.
- **State the rules in milliseconds first and frames second**, because this skill delivers
  at 60 fps as well as 30: one frame is 33 ms at 30 fps, 17 ms at 60, 42 ms at 24.
- **For a hard click, place the onset 0 to +1 frame LATE, never early.** The point of
  subjective simultaneity for audiovisual events sits at or after zero audio lag in most
  studies (visual leading by a few tens of ms is perceived as most synchronous:
  https://en.wikipedia.org/wiki/Point_of_subjective_simultaneity ,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4451240/ ). The whoosh and riser pre-roll (4.2)
  is the only legitimate early start, and it is early only in file start, not in perceptual
  onset.
- **A caveat on the +45 ms figure this document leans on.** BT.1359-1's +45 ms is the
  detection threshold for a **newsreader** under laboratory conditions. This document noted
  that impulsive sounds are tighter, gave no impulsive figure, and then applied the speech
  figure as though it were one, to three significant figures. Treat "74% of the way to
  threshold" as an inference about a number that does not describe this case.
- **Two frames late is the practical ceiling, not three.** 100 ms against a 125 ms
  detection threshold is technically inside detection, but a click 100 ms after a hard cut
  reads as a mistake to any editor in the room. Use the extra frame only when the picture
  event is itself soft (a dissolve landing, a slow settle). (Inference from studio practice;
  the document's own hammer figures, Dixon and Spitz +75/-188, are for a continuously
  drifting offset, which as it notes inflates thresholds.)

The "start it slightly early" advice that circulates among practitioners (pitchdrift: "starting
a sound ... a little earlier can ease the viewer into the scenery change") is about
**perceptual onset, not file start**. A whoosh or a swell has a slow attack; its perceptual
onset is where the envelope crosses roughly -20 dB relative to its peak, tens of milliseconds
into the file. Starting the file early puts the perceptual onset on the frame. A click with an
instant attack has no such lag and gets no lead. That reconciles the advice with the asymmetry
data. Inference.

The tapping literature adds a nuance for rhythmic ticks specifically: humans tap 20-40 ms ahead
of a metronome and do not notice (London, above). A tick that lands 0-1 frame early on a
regular grid will still read as on the grid; an impact on a single reveal will not get the
same forgiveness because there is no grid to anticipate. Inference from the two sources.

### 3.3 Frames, samples and where the error actually comes from

- Frame period: 33.33 ms at 30 fps, 16.67 ms at 60 fps, 41.67 ms at 24 fps.
- Place by sample, as `vo-mix.py` does: `start = round(frame / fps * sr)`. Do not place by
  seconds rounded to milliseconds and do not place by a media player's seek; both accumulate.
- Verify with energy onsets, not ASR and not by ear: `vo-verify.py`'s approach (find the
  actual energy onset of each cue in the rendered file and report the drift) applies
  unchanged to SFX. `SKILL.md`: "Whisper's boundaries lag soft attacks by a third of a second".
- `audio-beats.mjs` counts a cut as onset-locked when it is within 3 frames. That is an
  **analysis** window for asking whether a reference was cut to music. It is not a placement
  tolerance; placement is one frame.
- **The AAC priming trap, which bites more often than the frame-origin one.** Every AAC
  encoder inserts 1024 to 2112 samples of priming (21 to 44 ms at 48 kHz); the muxer records
  it in an edit list, and players that ignore edit lists play the audio that much late.
  ffmpeg's native encoder primes 1024 samples. **Verify sync on the muxed MP4 in the target
  player, not on the WAV**, and say which container and which player in the verification
  step (6.5). (Apple TN2258,
  https://developer.apple.com/library/archive/technotes/tn2258/_index.html ; Firefox bug
  1321249, https://bugzilla.mozilla.org/show_bug.cgi?id=1321249 .)
- The frame-boundary trap in `SKILL.md` section 7 (clip starts rounded up miss their own first
  frame) has an audio twin: a transient placed at `frame / fps` exactly, with the picture clip
  starting at `frame / fps - 0.0002`, is fine; a transient placed at `(frame + 1) / fps` because
  someone counted from 1 is a full frame late everywhere. Check the frame origin once.
- A shutter (`SKILL.md`, "The shutter") does not move the picture event; a 360 degree shutter
  at 60 fps spreads the settle over the frames either side, which softens the visual attack.
  When a card is shuttered, soften the transient attack to match (inference).

---

## 4. Synthesising each class in numpy

### 4.1 Contract

Same contract as the picture side, restated for audio:

- **Deterministic.** Every function takes a `seed` and builds its own
  `np.random.default_rng(seed)`. No module-level RNG, no `np.random.seed`, no `time`. Two calls
  with the same arguments return identical arrays. The placement script derives each cue's
  seed from its index, so a re-render is bit-identical.
- **Sample-accurate.** 48 kHz (matches most delivery; `bed-compose.py` uses 44.1 kHz, either
  is fine but the stem and the bed must agree before mixing). Every function returns a float
  array normalised to peak 1.0 with a 3 ms edge ramp so a cue can be truncated without a
  click.
- **No third-party samples.** Oscillators, noise, filters. `scipy.signal.butter` +
  `sosfilt` for the filters, as `bed-compose.py` already does.
- **Parameterised by the motion, not by taste.** Duration from the fitted move duration,
  envelope from the fitted ease, brightness from the ease family, level from hierarchy.

Shared helpers (verified running; the smoke test is at the end of this section):

```python
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000

def _rng(seed):
    return np.random.default_rng(seed)

def _bp(x, lo, hi, order=2):
    lo = max(20.0, lo); hi = min(hi, SR * 0.49)
    if hi <= lo * 1.05:
        hi = lo * 1.05
    return sosfilt(butter(order, [lo / (SR / 2), hi / (SR / 2)], "band", output="sos"), x)

def _lp(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR * 0.49) / (SR / 2), "low", output="sos"), x)

def _hp(x, fc, order=2):
    return sosfilt(butter(order, max(20.0, fc) / (SR / 2), "high", output="sos"), x)

def _edge(x, ms=3.0):
    n = min(len(x), int(SR * ms / 1000))
    if n > 1:
        r = np.linspace(0, 1, n)
        x[:n] *= r; x[-n:] *= r[::-1]
    return x

def _ease_speed(kind, n):
    """Normalised speed curve (derivative of the GSAP position ease), peak 1."""
    t = np.linspace(0, 1, n)
    if kind == "power2.out":        # position 1-(1-t)^3, speed 3(1-t)^2
        v = 3 * (1 - t) ** 2
    elif kind == "power2.inOut":
        v = np.where(t < .5, 12 * t ** 2, 12 * (1 - t) ** 2)
    elif kind == "expo.out":
        v = 10 * np.log(2) * 2 ** (-10 * t)
    else:                           # "none" / linear
        v = np.ones(n)
    return v / v.max()
```

Extend `_ease_speed` with the derivatives of whatever `segment.mjs` fits. The ease library in
`segment.mjs` gives the position curves; the derivatives are:

| GSAP ease | position p(t) | speed p'(t) |
| --- | --- | --- |
| `powerN.out` (N = 1..4) | 1 - (1-t)^(N+1) | (N+1)(1-t)^N |
| `powerN.in` | t^(N+1) | (N+1) t^N |
| `powerN.inOut` | piecewise, see `segment.mjs` | 2^N (N+1) t^N for t < 0.5, mirrored after |
| `sine.out` | sin(pi t / 2) | (pi/2) cos(pi t / 2) |
| `sine.inOut` | -(cos(pi t) - 1)/2 | (pi/2) sin(pi t) |
| `expo.out` | 1 - 2^(-10t) | 10 ln2 2^(-10t) |
| `circ.out` | sqrt(1 - (t-1)^2) | (1-t)/sqrt(1-(t-1)^2) (infinite at t=0; clip) |
| `back.out(s)` | 1 + (s+1)(t-1)^3 + s(t-1)^2 | 3(s+1)(t-1)^2 + 2s(t-1), negative during the overshoot return; take abs for level |

Basis: differentiation of the formulas in `segment.mjs`'s `EASES` table.

**Sample rate: deliver 48 kHz.** Video delivery is 48 kHz in every platform and broadcast
spec this document cites (EBU R128, ATSC A/85). `bed-compose.py` works at 44.1 kHz, so
resample it with `scipy.signal.resample_poly` or ffmpeg's `soxr`, never `np.interp`. The
stem and the bed must agree, and they must agree at 48 kHz rather than at whichever one you
started with.

### 4.2 Whoosh

**Model.** Band-passed noise with amplitude and centre frequency both driven by the motion's
speed curve. The physics: for an object moving through air the aeolian tone frequency is
f = St u / d (Strouhal), and the lift-dipole intensity scales with u^6 while the turbulent wake
adds broadband noise scaling with u^8, with "very little noise content below the lift dipole
fundamental" and a 1/f^2 roll-off above it (Selfridge, Moffat, Reiss, "Sound Synthesis of
Objects Swinging through Air Using Physical Models", *Applied Sciences* 2017, 7(11):1177, text
extracted from https://pdfs.semanticscholar.org/672b/abb90070bf03226c298fc4aea6d115f4c273.pdf).
The same paper's survey lists the simpler signal model this note uses: "noise shaping with a
bandpass filter with centre frequency proportional to the speed of the swing". Farnell's
*Designing Sound* (MIT Press 2010) treats the same family procedurally in Pure Data
(https://books.google.com/books/about/Designing_Sound.html?id=eMPxCwAAQBAJ).

**Parameters** (ranges are inference from the physics and the manifest durations; the exponents
are chosen to be steeper than linear because level goes as u^6):

| parameter | range | drive it from |
| --- | --- | --- |
| `dur` | 0.15-0.6 s for a card move; up to 1.5 s for a full-frame push | the fitted `durS` of the centroid run, plus 20-40 % tail |
| `ease` | any fitted ease | `beats.json` `motions[].ease` |
| `f_lo`, `f_hi` | 200-600 Hz to 2.5-8 kHz | larger elements lower (Strouhal: bigger d, lower f); a hero word 300-4000, a small chip 800-8000 |
| `q` | 1.5-4 | lower Q = airier, higher Q = whistling |
| speed-to-frequency exponent | 1.5 | inference; linear reads flat |
| speed-to-level exponent | 2 | inference; u^6 in the physics is too steep for a 10-frame move |

```python
def whoosh(dur=0.35, ease="power2.out", f_lo=300.0, f_hi=4000.0, q=2.5, seed=1):
    # PRE-ROLL. Every whoosh gets a swell of 60-150 ms before its peak REGARDLESS OF EASE.
    # The version this document previously shipped multiplied white noise by v**2 with v = 1
    # at sample 0, then applied a 3 ms edge ramp. Measured on its own defaults, the envelope
    # reached -20 dB relative to its peak 0.2 ms into the file for power2.out and 0.1 ms for
    # expo.out, and 92% (power2.out) / 100% (expo.out) of the energy sat in the first 20% of
    # the file. That is a gated burst of hiss with an instantaneous attack: on a review it
    # reads as a click of static, not as a whoosh. It also contradicted section 3.2 of this
    # same document, which says a whoosh has a slow attack and that starting the file early
    # is what puts the PERCEPTUAL onset on the frame.
    pre = int(SR * pre_roll)                  # 0.06-0.15 s, 2-4 frames at 30 fps
    n = int(SR * dur) + pre
    v = np.concatenate([np.zeros(pre), _ease_speed(ease, int(SR * dur))])
    swell = np.minimum(1.0, np.arange(n) / max(1, pre)) ** 2      # raised ramp into the peak
    # PINK, NOT WHITE. The cited aeroacoustic model gives a 1/f^2 roll-off above the lift
    # dipole fundamental; feeding white noise into a band-pass gives a hissy, thin result.
    # Every studio whoosh library is built on pink or brown noise, low-passed, with the high
    # band added as a separate quieter layer. Cheap deterministic pink: Paul Kellet's
    # three-pole filter, or cumulative-sum brown noise high-passed at 20 Hz.
    x = _pink(_rng(seed).standard_normal(n))
    out = np.zeros(n)
    hop = 512                                 # ~10 ms filter update
    # CARRY THE FILTER STATE. sosfilt starts from zero state on every call, so fresh state
    # per block modulates the amplitude at the block rate: measured with a stationary speed
    # curve, the RMS of the first 64 samples of each block was 0.903 of the mid-block RMS
    # and the amplitude envelope had a spectral line at 48000/512 = 93.75 Hz at 3.5x the
    # median of the surrounding band. That is a 94 Hz buzz riding on every whoosh (and a
    # 47 Hz buzz on every riser at hop 1024, and 21.5 Hz on bed-compose.py's riser at 2048).
    # With zi carried the ratio is 0.996 and the line drops to 2.0x.
    zi = None
    for i in range(0, n, hop):
        sp = v[min(i + hop // 2, n - 1)]
        fc = f_lo + (f_hi - f_lo) * sp ** 1.5  # speed -> centre frequency
        bw = fc / q
        sos = _bp_sos(fc - bw / 2, fc + bw / 2)
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        seg = x[i:i + hop]
        y, zi = sosfilt(sos, seg, zi=zi)
        out[i:i + len(seg)] = y
    out *= (v ** 2) * swell                   # level rises steeply with speed, under the swell
    return _edge(out / (np.abs(out).max() + 1e-9))
```

Better still for a time-varying band-pass: a **state-variable filter updated per sample**,
which is the standard way to sweep a filter in synthesis (Farnell, *Designing Sound*, already
cited here, does exactly this), because coefficient jumps in a biquad every 512 samples also
produce small steps even with the state carried.

**Anchor: the PEAK lands on the peak-velocity frame; the FILE starts 2-4 frames earlier.**
For an `.out` ease the peak velocity is the move's first frame, so the file starts 2-4 frames
before the move begins and the swell carries into it. For `.inOut` the peak is at the
midpoint. For an exit (`.in`) the peak is the last sample and the file ends on the cut. The
early file start is legitimate precisely because it is the perceptual onset that sits on the
frame, not the file start (section 3.2). Pixflow describes the same placement: a short whoosh
placed just ahead of an impact gives the moment a sense of arrival, the sound travels, then
lands (https://pixflow.net/blog/enhancing-motion-graphics-with-cinematic-transition-sounds/).
**The whoosh alone never marks the settle**: for a hard `expo.out` slide it swells into the
move, peaks on the first 1-2 frames, decays with the ease, and the settle frame gets a soft
tick or impact.

**Panning.** The stem should not be mono. A card sliding left to right pans with it; a
full-frame push widens; the impact body and the sub-drop stay centred and mono below about
120 Hz. `segment.mjs` reports `cx`, so the pan law is one line with constant-power panning:
`pan = (cx / width - 0.5) * 0.6`. `bed-compose.py` already pans its ticks (-0.4 / 0.4). This
is the cheapest single improvement in realism this document was missing. (Inference; standard
practice.)

### 4.3 Impact / thud

**Model.** A sine whose pitch falls quickly from about twice the resting frequency down to
50-90 Hz, with an exponential amplitude decay, plus a 5-15 ms band-passed noise transient on
the first samples, then soft saturation. This is kick-drum synthesis: "One envelope modulates
the pitch of the oscillator, causing it to jump from its bass frequency to a higher pitch and
then quickly come back", pitch settling "usually between 40 and 60Hz", with a "very quick
attack (around 1 ms) and slower decay, say around 50 ms" on the pitch envelope
(https://www.perfectcircuit.com/signal/kick-drum-synthesis,
https://modeaudio.com/magazine/drum-synth-sound-design-kick-snare). The noise click is what
makes the frame readable: low sines have slow perceptual onsets; the click pins the transient
to the frame (inference, consistent with the asymmetry data in section 3).

`bed-compose.py`'s own `impact()` is the same object at a longer scale: `boom = sin(cumsum(38 +
30 exp(-22 t)))`, decay 3.4/s, plus an `air` band 1.8-11 kHz decaying at 7.5/s, low-passed at
200 Hz. That one is a 1.5 s musical boom for structural beats; the SFX thud below is 0.3-0.5 s
and drier, so it reads as a settle rather than a downbeat.

| parameter | range | drive it from |
| --- | --- | --- |
| `f0` (rest) | 50-90 Hz | heavier element lower; a full-frame slam 50-60, a card 70-90 |
| `f_start` | 1.6-3x `f0` | harder ease higher (expo.out 3x, power2.out 2x) |
| pitch fall rate | 30-60 /s (25-50 ms) | **the kick-synthesis sources cited above give this envelope directly** (perfectcircuit, modeaudio). The earlier basis line here cross-referenced `disney-principles.md`'s 2-4 frame UI **squash duration at 60 fps**, which is a category error: a picture-deformation window is not a basis for an oscillator pitch envelope, and it weakened an otherwise correctly sourced number |
| `decay` | 6-14 /s (0.5 s to 0.2 s tails) | hold length: a card that cuts within 10 frames wants 14 |
| `click` | 0.2-0.5 | harder ease more click; a shuttered card less |
| `dur` | 0.3-0.6 s | inference |

**A professional impact is four layers, not two, and `bed-compose.py`'s own `impact()`
already has three of them.** Played dry on a laptop or a phone, where 65 Hz does not exist,
a pitched sine plus a 12 ms click is a click and nothing. The trailer-SFX literature is
unanimous that an impact is built as **transient + body + sub + tail**, spread across bands
so the layers do not crowd each other (BOOM Library, "think in layers (frequency, sustain,
tail, transient)", https://www.boomlibrary.com/blog/top-tips-for-trailer-sound-design/ ;
Krotos, build-up / hit / tail, https://www.krotosaudio.com/trailer-sound-design-tips-tricks/ ;
Native Instruments,
https://blog.native-instruments.com/5-quick-tips-for-epic-movie-trailer-impacts/ ):

- **transient**: the existing 1.5-9 kHz click, 5-15 ms
- **body**: a second pitched layer at 120-250 Hz with a short pitch drop and 80-150 ms decay.
  This is what phone speakers and laptops actually reproduce, and it is the "punch"
- **sub**: the existing 50-90 Hz sine, gained to taste, high-passed at 30 Hz
- **tail**: 200-600 ms of band-limited noise, or a short convolution with an exponentially
  decaying noise impulse (`bed-compose.py`'s `reverb()` is fine and is deterministic with a
  seed)

Ratios between the layers are taste and are set per film; the presence of all four is not.
**Space generally:** there is no reverb or tail treatment anywhere in the SFX chain below,
while the bed has a `reverb()` and a chord hold, so dry synthetic transients over a
reverberant bed read as pasted on. One shared, seeded, deterministic impulse (exponentially
decaying noise, 0.4-1.2 s) convolved into the impact, sub-drop and shimmer tails at 10-20%
wet is enough. Reverb on ticks and whooshes is optional and usually wrong.

**Variation.** Every impact below shares a synthesis and differs only by the seed of the
12 ms click, so every settle in the film sounds identical, which is a fast tell for a
synthetic pass. Round-robin deterministically from the cue index: +/-1 to 2 semitones on
`f0`, +/-10% on decay, +/-1.5 dB level. The seed scheme already supports it.

```python
def impact(f0=65.0, f_start=140.0, dur=0.45, decay=9.0, click=0.35, seed=2):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = f0 + (f_start - f0) * np.exp(-t * 40)      # pitch falls in ~25-50 ms
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * decay)
    nt = int(SR * 0.012)
    trans = _bp(_rng(seed).standard_normal(nt), 1500, 9000) * np.exp(-np.arange(nt) / SR * 350)
    out = body
    out[:nt] += click * trans
    out = np.tanh(out * 1.3)
    return _edge(out / (np.abs(out).max() + 1e-9))
```

**Anchor:** sample 0 on the settle frame (velocity zero). With a `back.out` ease the first
arrival at the target is the settle, not the end of the overshoot; `segment.mjs` reports
`toFrame` as the end of the monotonic run, which for a `back` fit is the first arrival, so use
`toFrame` directly.

### 4.4 Tick / click

**Model.** A 2-5 ms noise burst exciting one damped resonator (a two-pole filter), which is the
minimal version of a plucked-string model. Karplus-Strong (1983) does the same thing with a
delay line and a loop filter, "noise fed into a feedback delay line, with lowpass filtering of
the feedback" (https://ccrma.stanford.edu/~jos/pasp/Karplus_Strong_Algorithm.html); use it
instead of the two-pole when the tick needs harmonics (a wooden or metallic click). The
two-pole is enough for UI ticks and keeps the cue under 50 ms.

The 100 ms floor in section 5.4 sets the maximum tick density; the tick's own length sets how
many can overlap. At 45 ms two ticks 3 frames apart at 30 fps (100 ms) do not touch.

| parameter | range | drive it from |
| --- | --- | --- |
| `click_ms` | 2-5 ms | the ease: 2 for expo, 5 for sine |
| `f_res` | 1.5-5 kHz UI tick; 600-1200 Hz wooden; 6-9 kHz glassy | element size (small = high); when a voice is present keep it above 4 kHz, out of the 300-3400 Hz speech band (`SKILL.md`, "Replacing the voiceover") |
| `q` | 8-30 | dry step 8-12; a "lock in" 20-30 |
| `dur` | 30-80 ms | inference |
| pop variant | `f_res` rising 1.5x over 20-40 ms | for `back.out` / `spring-pop-entrance` |

```python
def tick(f_res=3200.0, dur=0.045, click_ms=3.0, q=18.0, seed=3):
    n = int(SR * dur)
    nc = int(SR * click_ms / 1000)
    exc = np.zeros(n)
    exc[:nc] = _rng(seed).standard_normal(nc) * np.linspace(1, 0, nc)
    w = 2 * np.pi * f_res / SR
    r = np.exp(-np.pi * f_res / (q * SR))         # pole radius from Q (bandwidth = f/Q)
    a1, a2 = 2 * r * np.cos(w), -r * r
    y = np.zeros(n)
    for i in range(n):                            # y = x + a1 y[-1] + a2 y[-2]
        y[i] = exc[i] + a1 * (y[i - 1] if i > 0 else 0) + a2 * (y[i - 2] if i > 1 else 0)
    out = 0.6 * exc + y
    return _edge(out / (np.abs(out).max() + 1e-9))
```

The Python loop is fine at 2,160 samples; for thousands of ticks vectorise with
`scipy.signal.lfilter([1], [1, -a1, -a2], exc)`, which is the same filter.

**Anchor:** sample 0 on the step frame. For per-character typing use the `words[].frame` list
from `segment.mjs` (word level) or the per-char cue times from the composition itself
(`autoAlpha` at 0.02 s per char in `SKILL.md`'s technique map); one tick per character at
0.02 s spacing is 50 ticks/s and is far past the density floor, so tick every second or third
character, or per word, and let the bed's shaker carry the texture (inference).

**With a voice present, do NOT park ticks at 4-6 kHz.** The 300-3400 Hz "speech band" is
the telephone band; sibilants and the presence region occupy 4-8 kHz, so ticks at 4-6 kHz
collide with every "s" in the read and are fatiguing. A 30-80 ms tick at 2-3 kHz masks less
than a phoneme and is the standard UI-tick region. With a voice, either keep ticks at
2-3 kHz and drop them 3 dB, or go to 8-10 kHz (glassy) where the read has little energy.
(Inference; this corrects the "keep ticks above 4 kHz when a voice is present" line in 5.3.)

### 4.5 Riser

**The riser needs the same two fixes as the whoosh, plus a low layer.** Carry the filter
state across blocks or it flutters at 48000/1024 = 47 Hz (measured; `bed-compose.py`'s own
riser at 2048 flutters at 21.5 Hz, below pitch but audible on a quiet passage). Use pink
rather than white noise as the source. And a 200 Hz to 8 kHz noise sweep with nothing under
it sounds like a filter demo: add a slowly rising sub or pad layer under the noise so the
build has weight, which is how `bed-compose.py` stacks its own riser under the pad.
(Inference.)

**Model.** Noise with a band-pass whose centre rises exponentially over N seconds (an
exponential sweep reads as a linear pitch rise), with an amplitude ramp, ending on the last
sample. `bed-compose.py` already has one (`fc = 380 + 7200 (i/n)^1.7`, level `t^2.2`, 30-44
frames) and places three, so a film with that bed either uses the bed's risers or replaces
them, never both on the same frame.

| parameter | range | drive it from |
| --- | --- | --- |
| `dur` | 0.5-2.0 s in a 20-30 s ad; the bundled `riser.mp3` is 10.03 s and is for long-form | the length of the build the picture shows, capped by the previous cut (a riser must not start before the card it belongs to) |
| `f_lo` to `f_hi` | 150-300 Hz to 6-10 kHz | inference |
| `curve` | 1.5-2.5 | higher = more of the rise in the last 20 % |
| level curve | `t^2.2` (from `bed-compose.py`) | |
| final 5 ms | linear to zero | the stop must be dead on the hit; a riser that rings past the cut smears the hit (inference) |

```python
def riser(dur=2.0, f_lo=200.0, f_hi=8000.0, curve=1.8, seed=4):
    n = int(SR * dur)
    x = _rng(seed).standard_normal(n)
    out = np.zeros(n)
    hop = 1024
    for i in range(0, n, hop):
        p = (i / n) ** curve
        fc = f_lo * (f_hi / f_lo) ** p            # exponential sweep
        seg = x[i:i + hop]
        out[i:i + len(seg)] = _bp(seg, fc * 0.6, fc * 1.7)
    out *= np.linspace(0, 1, n) ** 2.2
    k = int(SR * 0.005)
    out[-k:] *= np.linspace(1, 0, k)
    return out / (np.abs(out).max() + 1e-9)
```

**Anchor:** last sample on the payoff frame. Start = payoff - `dur`.

### 4.6 Sub-drop / boom

**Model.** A sine falling from 100-140 Hz to 30-40 Hz with a time constant of 0.2-0.5 s, soft
attack (8 ms), slow decay, soft saturation. It is the impact of section 4.3 with the click
removed and the pitch envelope stretched ten-fold: "lower bend amounts will make mellow and
droning kicks" (https://www.perfectcircuit.com/signal/kick-drum-synthesis). No noise, so no
seed; it is fully deterministic by construction.

**Tune the landing pitch to the bed's key.** The sub-drop's `f_end`, the shimmer partials,
the pop resonator and the riser's top note are all tonal and are all currently in no key.
`bed-analyse.py` reports the bed's pitch classes; a sub-drop that lands on the root of the
bed's chord at that bar is what makes a synthesised hit feel composed rather than dropped
in. (Inference; universal trailer practice.)

One correction to what follows: its true peak is **not** especially high. Measured, the
sub-drop's inter-sample overshoot is +0.01 dBTP at a sample peak of 0 dBFS, because a smooth
low sine has essentially no inter-sample peak problem. The true-peak risk in this recipe is
the `tanh`-saturated impact click and the summed coincidence of an impact with the bed's own
boom. Keep the true-peak warning; aim it at the right object. Phone speakers do not
reproduce it, so on mobile the sub-drop is felt
only through its harmonics from the `tanh` stage. If the film is phone-first, raise `f_end` to
45-55 Hz and the saturation to 1.5 (inference).

```python
def sub_drop(f_start=120.0, f_end=35.0, dur=1.2, tau=0.35):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = f_end + (f_start - f_end) * np.exp(-t / tau)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.minimum(1.0, t / 0.008) * np.exp(-t * 2.2)
    out = np.tanh(x * env * 1.2)
    return _edge(out / (np.abs(out).max() + 1e-9))
```

**Anchor:** sample 0 on the reveal frame. Pair it with a `tick` or `impact` click on the same
frame if the reveal is hard-edged, because the sub alone has no readable onset (inference from
the asymmetry data: a slow onset reads late).

### 4.7 Shimmer / glint

**Model.** A cluster of 4-8 high sines, each slightly detuned. **The ratio in the code below
produces exactly the chord it claims to avoid**: `1.5 ** 0.5` is 1.2247, which is 3.51
semitones, so six partials at equal 3.5-semitone spacing is a stack of near-minor-thirds, a
diminished-seventh-like cluster that reads as an unmistakable and slightly sour chord and
will clash with whatever key the bed is in (`bed-compose.py` is in A minor resolving to C).
Use **genuinely inharmonic ratios** (a bell-like set such as 1, 2.76, 5.40, 8.93, or a seeded
uniform draw in [1.1, 1.4] per step), or better for a motion-graphics film, **tune the
partials to the bed's key** using the pitch classes `bed-analyse.py` already reports. A glint
that rings the bed's fifth or octave sounds designed; one that rings a random diminished
cluster sounds like a preset. (Inference from standard bell/glass synthesis practice.) Fast
attack (15 ms), decays getting shorter for higher partials. fast attack (15 ms), decays getting shorter for higher partials.
Synthesis recipe is inference; the pairing to a glint is from the manifest (`sparkle`).

```python
def shimmer(dur=0.9, base=2400.0, n_partials=6, seed=5):
    n = int(SR * dur)
    t = np.arange(n) / SR
    g = _rng(seed)
    out = np.zeros(n)
    for k in range(n_partials):
        # WAS: base * (1.5 ** (k * 0.5)) -- equal 3.51-semitone spacing, a diminished chord.
        RATIOS = [1.0, 2.76, 5.40, 8.93, 13.34, 18.64]          # bell-like, inharmonic
        f = base * RATIOS[k % len(RATIOS)] * (1 + g.uniform(-0.004, 0.004))
        if f > SR * 0.45:
            break
        out += np.sin(2 * np.pi * f * t + g.uniform(0, 2 * np.pi)) * np.exp(-t * (3.5 + k)) / (k + 1)
    out *= np.minimum(1.0, t / 0.015)
    return _edge(out / (np.abs(out).max() + 1e-9))
```

**Anchor:** sample 0 where the highlight crosses the element. For the liquid-glass rim glint in
`SKILL.md` (a conic gradient spun 0 to 360 with a linear ease) the audible moment is when the
bright spot passes the top edge; compute that frame from the rotation, do not sound the whole
revolution.

### 4.8 Reverse swell

**Model.** The reversed-cymbal shape: band-passed noise under an exponential rise (`t^3`),
stopping dead on the cut. The technique is standard in music production ("reverse cymbals
before a chorus create transitions that swell into the drop",
https://www.pointblankmusicschool.com/blog/using-reversals-to-create-unique-transitions-in-your-tracks/).
The difference from a riser is that a swell has no pitch movement, so it says "something is
about to change" without saying "something is building".

```python
def reverse_swell(dur=0.8, f_lo=400.0, f_hi=6000.0, seed=6):
    n = int(SR * dur)
    out = _bp(_rng(seed).standard_normal(n), f_lo, f_hi)
    out *= np.linspace(0, 1, n) ** 3.0
    k = int(SR * 0.004)
    out[-k:] *= np.linspace(1, 0, k)
    return out / (np.abs(out).max() + 1e-9)
```

**Anchor:** last sample on the cut frame. If the cut is followed by a blank gap (the usual case
in the measured references), the swell ends on the first blank frame and the gap is silent;
the next card's transient then lands on the card's first frame. The silence between is the
edit breathing.

### 4.9 Smoke test results

All seven functions were run from a scratch script (`sfx_test.py`, session scratchpad, not
shipped; the code is exactly what is printed in this section plus the placement code in 6.3)
with the defaults above, at 48 kHz, on 2026-09-02. Each was called twice and the two arrays
compared with `np.array_equal`: identical in every case. Measured on the normalised output:

| class | length | RMS (dBFS) | crest factor |
| --- | --- | --- | --- |
| whoosh | 0.350 s | -18.1 | 18.1 dB |
| impact | 0.450 s | -10.7 | 10.0 dB |
| tick | 0.045 s | -24.6 | 17.6 dB |
| riser | 2.000 s | -21.4 | 21.4 dB |
| sub_drop | 1.200 s | -8.3 | 8.3 dB |
| shimmer | 0.900 s | -15.6 | 15.6 dB |
| reverse_swell | 0.800 s | -20.0 | 20.0 dB |

The crest factors matter for section 5: the impact and sub-drop are dense (low crest), so at a
given peak they contribute far more loudness than a tick or a whoosh. Gain them by ear against
the bed's short-term loudness, not by peak.

---

## 5. Mixing SFX under music

### 5.1 Delivery loudness targets (platform specs)

| Destination | Integrated loudness | True peak | Source |
| --- | --- | --- | --- |
| AES TD1008 (2021), streaming and on-demand | -16 LUFS music (track-normalised), -18 LUFS speech and "assorted" | max -1 dBTP at the codec input | https://aes.org/technical-council/technical-document-aestd1008/ and https://productionadvice.co.uk/td1008/ |
| YouTube | normalises playback to about -14 LUFS; louder content is turned down, quieter is not turned up | | https://productionadvice.co.uk/stats-for-nerds/ ("content loudness" readout), https://www.criticallisteninglab.com/en/learn/loudness/youtube |
| Spotify, Tidal, Amazon | -14 LUFS (Amazon -2 dBTP) | -1 to -2 dBTP | https://www.forasoft.com/learn/audio-for-video/articles-audio/lufs-targets-per-platform-2026 |
| Apple Music (Sound Check) | -16 LUFS | | same |
| TikTok, Instagram, Facebook, X | no published target; informal tests put normalised playback near -14 to -15 LUFS | | same, and https://clickyapps.com/creator/video/guides/lufs-targets-2025 (both secondary; no first-party spec exists) |
| EBU R128 (broadcast, Europe) | -23 LUFS | -1 dBTP | https://tech.ebu.ch/docs/r/r128.pdf |
| **ATSC A/85 (broadcast, US)** | **-24 LKFS +/- 2, dialogue-anchored** | **-2 dBTP** | https://www.atsc.org/wp-content/uploads/2015/03/Techniques-for-establishing-and-maintaining-audio-loudness.pdf , https://www.criticallisteninglab.com/en/learn/loudness/atsc-a85 . This is the target a US client will ask for and it was missing from this table |
| Netflix | -27 LKFS +/- 2 LU, dialogue-gated | -2 dBTP | https://www.izotope.com/en/learn/izotope-insight-2-now-updated-for-netflix-loudness-requirements.html (secondary; the partner-help page redirected and was not fetched) |
| `grade-original.py` (the skill's own gate for a VO film) | -17.0 to -15.0 LUFS | reads `max_volume` from `volumedetect`, which is **sample peak, not true peak** | `<skill>/scripts/grade-original.py`, AUDIO checks. **The gate should read the `Peak:` value from the `ebur128=peak=true` pass the script already runs**, because inter-sample peaks after lossy encoding routinely exceed sample peak, which is why every standard in this table specifies dBTP |

**Recommendation for a web/social motion-graphics film** (inference from the table): mix to
**-15 LUFS integrated, -1.0 dBTP**, measured with `ffmpeg -af ebur128=peak=true` the way
`grade-original.py` and `hyperframes-audio/references/diagnosis.md` both do. Reasoning: every
social platform normalises down to about -14 and none boosts, so -14 to -16 loses nothing on
any of them; -15 leaves 1 LU of slack for measurement differences; -1 dBTP survives the lossy
transcode. A film going to broadcast gets a separate -23 LUFS pass; do not try to serve both
with one file.

Measure the K-weighted loudness and the true peak separately. **But the reason previously
given here for doing so is wrong at the frequencies these recipes use.** Measured with the
BS.1770-4 filter coefficients at 48 kHz, K-weighting gain is -0.8 dB at 120 Hz, -1.4 dB at
90 Hz, -2.5 dB at 65 Hz, -3.9 dB at 50 Hz, -6.7 dB at 35 Hz and -8.3 dB at 30 Hz. The
sub-drop starts at 120 Hz and the impact body sits at 50-90 Hz, so **both count almost fully
toward integrated loudness**; only the last 30-40 Hz of the sub-drop's tail is discounted
meaningfully, and a film with five structural hits will move its integrated reading visibly
when they are added. The advice to gain hits by ear against the bed's short-term loudness
rather than by peak is right; the justification was not. True-peak meters
oversample 4x to catch inter-sample peaks that a sample-peak meter misses
(https://nugenaudio.com/loudness-true-peak/, https://www.forasoft.com/learn/audio-for-video/articles-audio/loudness-normalization-ebu-r128-bs1770-atsc-a85).
The sub-drop is where a mix that reads -15 LUFS clips.

### 5.2 Voice, bed, SFX: the hierarchy

- Voice first. `grade-original.py`: music 6.0 to 14.0 dB below voice, duck depth <= 6 dB (a bed
  that pumps more than that "audibly pumps under the read"), per-line level spread <= 3 dB.
- WCAG technique G56 for accessibility: non-speech at least 20 dB below speech
  (https://www.w3.org/WAI/WCAG20/Techniques/general/G56). That is stricter than the film gate;
  it is the figure to use if the deliverable has an accessibility requirement.
- Bed under a voice: "about -31 LUFS, never masking the voice"
  (`media-use/audio/references/tts.md`, for a -16 to -18 LUFS voice, so the same 13-15 dB gap).
- Film/TV stem practice as reported by Krotos Studio: music -14 LUFS as mastered, TV -23, film
  -27 overall; SFX "between -20dB (footsteps, environmental sounds) and -10dB (hits, cracks and
  louder sounds)" with music near -20 dB
  (https://krotos.studio/blog/how-to-balance-music-and-sound-effects). A stem set quoted in
  search excerpts attributed to the same article (speech -17, SFX foreground -21, music -24,
  SFX background -29 LUFS) was not visible in the page text retrieved and is listed here as
  unverified.
- The bundled SFX engine's default: `volume: 0.35` on every cue, "SFX sit UNDER voice + BGM"
  (`media-use/audio/references/sfx.md`). 0.35 linear is -9.1 dB. That is a safe default for
  library files of unknown level, not a target for synthesised cues whose level you control.

### 5.3 SFX peak relative to the bed (inference, to be tested per film)

Levels below are for a film with no voice. With a voice, drop every row 3 dB and move ticks
above 4 kHz.

| class | relation to the bed at the moment of the cue | why |
| --- | --- | --- |
| impact, sub-drop (the film's 2-5 structural hits) | short-term peak 3-6 dB **above** the bed's short-term loudness at that frame | it is the loudest thing in the film for 100 ms; that is the point |
| impact on an ordinary card settle | level with the bed, 0 to +2 dB | punctuation, not an event |
| tick / click | 8-14 dB below the bed | it is heard by its spectrum (2-5 kHz, where the bed has a hole), not by its level |
| whoosh | peak 4-8 dB below the bed | a whoosh above the bed reads as wind, not as motion |
| riser, reverse swell | start inaudible, arrive 2-4 dB below the bed at the last 100 ms | the arrival is the hit's job |
| shimmer | 10-16 dB below the bed | decoration |

Two constraints from the skill's own audio work apply regardless of the numbers:

- **Spectral placement beats level.** `bed-compose.py` low-passes the pad below 980 Hz and keeps
  percussive air above 6 kHz to leave a hole at 1.5-4 kHz for the voice; `SKILL.md` says to
  confirm "1.5-4 kHz is well down". Ticks at 2-5 kHz sit in that hole and are audible at low
  level. When there is a voice the hole is the voice's -- but **do not move the ticks to
  4-6 kHz**, which is the sibilance and presence region, where they collide with every "s" in
  the read and are fatiguing (see 4.4). Keep them at 2-3 kHz and drop them 3 dB, or move them
  to 8-10 kHz where the read has little energy.
- **Do not put SFX in a carve group; DO dip the bed by hand under a structural hit.** These
  are two different things and the earlier revision collapsed them into one rule.
  `hyperframes-audio` refuses to carve a bed when an SFX clip shares the voice group, because
  "the bed starts ducking under a whoosh" (`hyperframes-audio/SKILL.md`, "Keep the carve group
  a voice group"), and that is a **tooling constraint about automatic ducking**: an automatic
  carve keyed to SFX would pump on every whoosh, which is correct to refuse. It is not a
  mixing rule. In trailer and motion-graphics mixing a brief dip of the bed under a structural
  hit -- 50 to 200 ms, 3 to 6 dB, fast release -- is normal and is what gives the hit room;
  the bed being loud at the hit is why a hit reads small. The right tool is a hand-placed
  `data-automation` volume lane on the bed at the 2 to 5 structural frames, which is fully
  seek-safe and exists in `hyperframes-audio/references/attributes.md`. The claim that "a
  transient that needs the bed out of the way is too quiet" does not survive contact with how
  trailers are mixed.

### 5.4 Density: how many SFX per second before it reads as noise

**Keep the 100 ms rule as practice; drop the justification, which the source does not
support.** London's figure is about the limit for **judging rhythmic quantity and duration**,
not about two clicks fusing into one event: two transients 30 to 60 ms apart are heard as a
distinct flam, which drummers play on purpose and which is a legitimate device on a two-stage
settle (first arrival, then the overshoot return). So "never two transients closer than
100 ms unless one is a flam" is a fine working rule, and "they fuse into one smeared event"
is not what the source says. The quoted text: "we are able to make judgements of quantity and
duration only when the IOIs are longer than 100ms (i.e., slower than 10 per second)"; above
1.5-2.0 s "the rhythm falls apart"; a spontaneous comfortable beat is 500-700 ms (London,
*Hearing in Time*, lecture text at the UVic URL above, citing Hirsh et al. 1990, Friberg and
Sundstrom 2002, Repp 2002, Fraisse 1982). Auditory forward masking extends 50-200 ms after a
sound (https://link.springer.com/chapter/10.1007/978-3-540-73009-5_18), so a quiet tick within
that window after an impact is inaudible anyway.

Practical ceilings (inference from those figures and the choreography rules):

- **Never two transients closer than 100 ms** (3 frames at 30 fps) unless one is deliberately
  a flam or a grace note on the other. Below that they fuse into one smeared event.
- **Sustained rate above about 4 transients per second reads as texture, not as events.** At
  that rate the ear hears a rhythm (it is inside the rhythmic range) and the picture cuts
  stop being individually marked. Typing ticks are the exception because they are *meant* to
  be texture; keep them 10-14 dB down so they sit with the bed's shaker.
- **The comfortable event rate is one transient per 0.5-1.5 s.** That is the spontaneous
  tempo range and it is also the `kinetic-beat-slam` `BEATS` spacing ("1.2-1.8s; <0.8s frantic,
  >2.5s loses the pulse"). The measured 26 s reference had 23 cards in 776 frames, about one
  cut per 1.1 s, which sits in this range; one transient per cut is not too many.
- **Apply the 1/3 rule.** `choreography.md`: with 3+ animated elements at most a third are
  active at once. If a card has a hero move plus two supporting moves, sound the hero only.
  Sound count per card: one primary transient, at most one secondary, plus texture ticks if
  the card types.

A useful test: mute the picture and listen to the stem alone. If it sounds like a drum part it
is too dense; if it sounds like someone knocking now and then, it is about right (inference).

### 5.5 Where the bed and the SFX overlap

`bed-compose.py` already synthesises `impact()` on five structural frames (108, 347, 534, 576,
661) and `riser()` into three of them, on a 150 BPM grid fitted to the cut list with
`bed-tempo-fit.py`. Those are musical events on the grid. SFX are picture events on frames.
When the two coincide, which they will on structural cuts because the grid was fitted to
them, decide per frame:

- On a structural cut, let the **bed's** impact carry the weight (it is longer and reverberant,
  1.5 s) and add only the **SFX click** component (the 12 ms transient) so the frame is pinned.
  Two booms on one frame double the low end and push true peak over.
- On ordinary card cuts the bed has nothing; the SFX stem carries them.
- Ticks and shaker: the bed's `tick + shaker` layer runs on eighth and sixteenth notes; picture
  ticks land on word frames. When a word frame is within 1 frame of a grid tick, drop the
  picture tick; the grid one already reads as the word (inference, and only true because the
  grid was fitted to the cuts).

`bed-verify.py` (cross-correlation of the render's audio against each candidate bed) still
works with an SFX stem added, because the stem is sparse; expect the correlation against the
bed to drop slightly from the 0.99 the skill reports for the bed alone. Record the number.

---

## 6. Placing cues automatically from the cut list

### 6.1 Inputs the skill already produces

`segment.mjs` writes `.analysis/ref/beats.json`:

```
{ meta: { fps, ... },
  segments: [ { index, startFrame, endFrame, frames, start, end, duration,
                gapBefore,          // blank frames before this card
                bg: "white"|"black",
                peakInk, edgeMin, edgeMax, blurDrop,
                motions: [ { signal: "inkFrac"|"bboxTop"|"bboxBot"|"bboxW"|"bboxH"|"cx"|"cy",
                             mechanic, fromFrame, toFrame, from, to, startS, durS,
                             ease, rmse, alt } ],
                words: [ { xFrom, xTo, frame, t } ] } ] }
```

`audio-beats.mjs` writes `.analysis/ref/audio.json` with `onsets` (frame numbers, 94th
percentile threshold, min 4 frames apart) and per-cut `nearestOnsetDelta`.

For an original film there is no reference to segment; the composition's own `data-start` /
`data-duration` attributes, converted to frames as `SKILL.md`'s "Audit clip boundaries" section
describes, give the same list. `beats-from-read.py` gives the VO line frames.

### 6.2 Rules, in order

1. **Build a candidate list of card starts, then THIN it.** Rule 1 as previously written
   ("every card start gets exactly one transient") sounds all 23 cards of a 26 s reference,
   plus a whoosh on every measured slide, plus a tick on every word after the first, plus
   risers, and the generator produces the drum part that 2.3 and 5.4 of this same document
   warn against. A professional pass on a 23-card piece sounds perhaps half to two thirds of
   the cuts, always the structural ones, and lets the rest ride on the bed's grid, which was
   fitted to the cuts and therefore already marks them. Concretely: cards inside a
   rapid-fire run (gap 0-2 frames, duration under 12 frames) get **one** sound for the run,
   on its first card, plus the bed's ticks. Word ticks are **off by default** and on only
   for a card whose motion is a step reveal. (Inference.) Class the survivors by context: the first card and the
   card after the longest gap get a `sub_drop` (plus a click); a card after a gap >= 4 frames or
   after a background flip gets an `impact`; a card that follows within 3 frames gets a `tick`.
   Basis: the blank-gap cut model in `segment.mjs` and `SKILL.md` section 3.2; the class
   choice is inference.
2. **A monotonic run of `cx`, `cy` or `bboxTop` lasting >= 4 frames gets a whoosh** with
   `dur = durS * 1.3`, `ease` from the fit, anchored so its peak sits on `fromFrame` for `.out`
   eases. Skip if the same card already has an impact within 3 frames of the whoosh's end (the
   impact is the settle; the whoosh into it is the standard pairing, but a whoosh shorter than
   6 frames under an impact is masked and wasted).
3. **Word reveals after the first in a card get a soft tick** (`f_res` 2200, `q` 10, 12 dB
   down) -- **off by default**, on only for a step-reveal card. Typing cards: every second
   character at most.
4. **Risers into the two largest gaps**, `dur` = min(1.5 s, previous card's duration), ending
   on the card's first frame. Skip if the bed already has one there (section 5.5).
5. **Reverse swell into any blackout or ground flip that has no riser.**
6. **One transient per frame.** Dedupe by `(class, frame)`; if two different classes land on
   one frame keep the heavier (sub_drop > impact > tick) plus the click component only of the
   other.
7. **Lead offset.** `lead_ms` defaults to 0 for clicks and impacts. For whoosh, riser and swell
   the anchor is the peak or the end, so no separate lead is needed. Never set a positive lead
   on a transient (section 3.2).
8. **Gain per class** from section 5.3, with per-instance variation from the cue index
   (+/-1.5 dB, +/-1-2 semitones, +/-10% decay), then a single stem normalisation, then
   measure.
9. **Master chain, which this document was missing entirely.** High-pass the bed at 30-40 Hz
   under a sub-drop so the two do not stack; a gentle bus compressor (2:1, slow) to glue; and
   a **true-peak limiter at -1 dBTP as the last stage**. Section 5.5 warns about the double
   boom and then does nothing about it: two structural hits within a bar plus the bed's own
   boom will exceed -1 dBTP at the -15 LUFS gain. `hyperframes-audio`'s fx registry has a
   `limiter`, or a simple look-ahead in numpy will do. (Inference; standard.)
10. **Do not truncate the tail.** `render_stem` clamps the last cue at `N`
   (`b = min(N, ...)`) with no fade, so an impact or sub-drop on the final card with a 1 s
   decay ends in a hard cut on the last frame. Extend the stem by the longest tail and let the
   composition's audio run past the last picture frame, or fade the final 100 ms.
11. **Exit sounds.** The table gives exits "none on the exit; the cut it leads into gets the
   hit", which is right for a hard cut and wrong for a push: the **reverse whoosh** (a
   "whoosh out") is the pair of the entrance whoosh and is what makes a push feel like one
   move rather than two cards.
12. **Silence is a deliverable choice.** Decide, and write down, whether the piece opens
   silent (first 6-12 frames with no bed, so the first hit has contrast) and whether the bed
   ends on the last frame or rings 0.5 s past it -- and whether the container length follows.
   A client will ask about both.

### 6.3 Code (verified on a synthetic `beats.json`)

```python
SFX_FUNCS = {"whoosh": whoosh, "impact": impact, "tick": tick, "riser": riser,
             "sub_drop": sub_drop, "shimmer": shimmer, "reverse_swell": reverse_swell}

GAIN_DB = {"whoosh": -14, "impact": -8, "tick": -18, "riser": -16,
           "sub_drop": -6, "shimmer": -20, "reverse_swell": -16}   # section 5.3, pre-mix

def cues_from_beats(beats):
    segs = beats["segments"]
    cues = []
    for i, s in enumerate(segs):
        f, gap = s["startFrame"], s.get("gapBefore", 0)
        motions = {m["signal"]: m for m in s.get("motions", [])}
        if i == 0:
            cues.append(("sub_drop", f, {}))
        elif gap >= 4 or s["bg"] != segs[i - 1]["bg"]:
            cues.append(("impact", f, {}))
        else:
            cues.append(("tick", f, {}))
        for sig in ("bboxTop", "cx", "cy"):
            m = motions.get(sig)
            if m and m["durS"] >= 0.12:
                cues.append(("whoosh", m["fromFrame"], {"dur": m["durS"] * 1.3, "ease": m["ease"]}))
                break
        words = [w for w in s.get("words", []) if w.get("frame") is not None]
        for w in words[1:]:
            cues.append(("tick", w["frame"], {"f_res": 2200.0, "q": 10.0}))
    for s in sorted(segs, key=lambda s: -s.get("gapBefore", 0))[:2]:
        if s.get("gapBefore", 0) >= 6:
            cues.append(("riser", s["startFrame"], {"dur": 1.5, "end_on": True}))
    seen, keep = set(), []
    for k, f, kw in sorted(cues, key=lambda c: c[1]):
        if (k, f) in seen:
            continue
        seen.add((k, f)); keep.append((k, f, kw))
    return keep

def render_stem(cues, fps, total_frames, lead_ms=0.0):
    N = int(round(total_frames / fps * SR))
    stem = np.zeros(N)
    for idx, (kind, frame, kw) in enumerate(cues):
        kw = dict(kw)
        end_on = kw.pop("end_on", kind in ("riser", "reverse_swell"))
        fn = SFX_FUNCS[kind]
        if "seed" in fn.__code__.co_varnames:
            kw["seed"] = 100 + idx                      # index-derived, so re-renders match
        sig = fn(**kw) * 10 ** (GAIN_DB[kind] / 20)
        t_hit = frame / fps - lead_ms / 1000
        start = int(round((t_hit - (len(sig) / SR if end_on else 0)) * SR))
        a, b = max(0, start), min(N, start + len(sig))
        if b > a:
            stem[a:b] += sig[a - start:b - start]
    return stem
```

Run against a three-segment synthetic `beats.json` (30 fps, 160 frames) this produced:
`sub_drop@6, riser->6, tick@44, tick@50, whoosh@44, tick@56, impact@100, riser->100`, stem
peak 0.50 before normalisation. (The scratch version anchored the whoosh on `toFrame`; the
listing above uses `fromFrame` per section 4.2, which is the correct anchor for `.out` eases.)

Write the stem with `soundfile.write(".analysis/sfx-stem.wav", stem, SR)` as `bed-compose.py`
does, then mix: `mix = bed + stem`, `ebur128` measure, one gain to hit -15 LUFS, check
true peak, and re-measure. Never normalise the stem and the bed independently after mixing
decisions have been made, because the class gains in `GAIN_DB` are relative to the bed.

### 6.4 Into the HyperFrames composition

Two ways to attach the result, both seek-safe:

- **One stem.** A single `<audio id="sfx" src="media/sfx-stem.wav" data-start="0">` alongside
  the bed. Simplest, and `bed-verify.py` style checks work on the render. Every `<audio>` needs
  an `id` (`SKILL.md` lint traps).
- **Per cue.** One `<audio>` per cue with `data-start` at `frame / fps - 0.0002` (the same
  inward bias the picture clips use, `SKILL.md` section 7). Useful when cues must move with
  clips in `general-video`. Put them in an `sfx` group, never in the voice group
  (`hyperframes-audio`).

The composition's own audio-reactive path (`techniques.md` section 11: pre-extracted bands
sampled per frame via `tl.call`) can run on the *mixed* track so a logo pulses on the sub-drop.
Keep it under 5 % scale on text per that section.

### 6.5 Verify

- **Placement:** energy-onset detection on **the muxed MP4, played in the target player**,
  not on the WAV, because AAC priming (3.3) shifts audio by 21-44 ms in players that ignore
  edit lists. Use the `vo-verify.py` method against the cue list and report drift in frames.
  Target: every impulsive cue within +1 frame late to 0 early.
- **Mono and small-speaker check.** Render a mono, band-limited (200 Hz to 8 kHz) fold-down
  and listen for what disappears. The impact body layer (4.3) exists for exactly this check;
  if the hits vanish in the fold-down, the body layer is missing or too quiet.
- **True peak on the master**, from `ebur128=peak=true`, after the limiter. Sample peak from
  `volumedetect` is not the same measurement.
- **Density:** count cue onsets per rolling second; flag any second with more than 4 and any
  pair closer than 3 frames that was not intended as one event.
- **Loudness:** `ffmpeg -af ebur128=peak=true`, integrated and true peak, against section 5.1.
- **Bed integrity:** `bed-verify.py` correlation against the composed bed; record the value.
- **The silent-gap check:** for every blank run in `beats.json`, the stem must be at or below
  -60 dBFS across the run except for a riser or swell that ends on the run's first frame
  (extend `grade-original.py`'s "music floor inside the blackout" check to the stem).
- **The mickey-mousing check:** cues per card <= 2 primary. Anything above is a review item,
  not a lint failure.

---

## 7. Quick reference

| motion | sound | anchor | dur | level vs bed | spectrum |
| --- | --- | --- | --- | --- | --- |
| fast move | whoosh | peak on peak-velocity frame | 1.3x move | -4 to -8 dB | 300 Hz-4 kHz, follows speed |
| settle / slam / cut | impact | onset on settle frame | 0.3-0.5 s | 0 to +2 dB (structural +3 to +6) | 50-90 Hz + 1.5-9 kHz click |
| step / type / toggle | tick | onset on step frame | 30-80 ms | -8 to -14 dB | 1.5-5 kHz (>4 kHz with VO) |
| build | riser | end on payoff | 0.5-2 s | arrives -2 to -4 dB | 200 Hz to 8 kHz sweep |
| reveal | sub-drop + click | onset on reveal | 0.8-1.5 s | +3 to +6 dB | 120 to 35 Hz |
| glint | shimmer | onset on crossing | 0.6-1 s | -10 to -16 dB | > 2 kHz |
| into a cut | reverse swell | end on cut | 0.4-1 s | arrives -2 to -4 dB | 400 Hz-6 kHz |
| dissolve, gap, ambient | nothing | | | | |

Sync: onset within +/-1 frame; never > 1 frame early; late is more forgivable than early by a
factor of about 2.5 (ITU-R BT.1359-1: +45 / -125 ms). Density: >= 100 ms between events, about
one per 0.5-1.5 s, never > 4/s sustained. Delivery: -15 LUFS integrated, -1 dBTP, for web and
social; -23 LUFS / -1 dBTP for European broadcast; measure with `ebur128`.

---

## 7b. What this document still does not cover

Named here so the gap is visible rather than implied.

- **Bed hit points and music editing.** This document treats the bed as fixed and the stem as
  additive. In practice half of "sound design" on a motion piece is editing the music: a hit
  point on a downbeat, an early cut of a phrase so the reveal lands on bar one, the pad
  dropping out under a whisper card. `bed-tempo-fit.py` gets the grid; nothing here says how
  to move the bed to the picture when the grid fit is off by a beat.
- **Practitioner citations for the mapping itself.** Section 2.2 cites a manifest and physics
  papers and not a single working sound designer's account of a motion piece. The Krotos, BOOM
  Library and Native Instruments posts cited in 4.3, and the Videomaker piece
  (https://www.videomaker.com/how-to-combine-sound-effects-with-motion-graphics/), would
  ground the table in practice rather than in a bundled library's asset descriptions.
- **The smoke-test table in 4.9 proves the functions run and are seeded. It does not prove
  they sound right, and this document should not imply that it does.**

## 8. Open questions

- The impulsive-sound sync thresholds in the standards are all derived from newsreaders or a
  filmed hammer. Nobody has published a threshold for a synthetic click against a rendered
  card cut. The +/-1 frame rule is inferred; a quick ABX on a rendered card at 0, +1, -1, +2
  frames would settle whether the early side can be relaxed at 60 fps.
- The per-class gain table (5.3) is inference. One graded film with those values, measured
  against a listening pass, would turn it into data.
- TikTok and Instagram loudness behaviour is only known from third-party measurement. If a
  film is TikTok-first, measure the platform's playback of a -15 and a -12 LUFS upload of the
  same film once and record what it did.
- Whether `segment.mjs`'s `toFrame` for a `back.out` fit is the first arrival or the end of
  the overshoot return depends on `mainRun`'s break tolerance (6 % reversal); confirm on a
  measured `back` card before anchoring impacts to it.
- The block-wise band-pass in `whoosh()` and `riser()` is called per block with fresh filter
  state; no click was audible on the test renders but it has not been measured. If a click is
  ever heard, switch to `sosfilt` with carried `zi` or overlap-add.
