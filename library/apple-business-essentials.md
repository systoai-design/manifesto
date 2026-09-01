# apple-business-essentials

**Callable as: Apple Business Essentials** (aliases: ABE ad, the Apple ad, abe-ad, the 26s skeleton)

Product ad in the Apple house style: fast kinetic-typography cards on flat black,
punctuated by four white cards, cut to a driving music bed. The skeleton behind
three separate Systo films. Measured 2026-08-29, re-read into this entry 2026-09-01.
Source: 1280x720 @ 30fps, 776 frames, 25.867s. Analysed at 640x360.

## Fidelity — skeleton

Cut frames, per-segment durations, mechanics, blank gaps and the music grid are
all recorded below, from `segment.mjs` and `audio-beats.mjs` output preserved in
`.analysis/ref/`. This licenses deriving a new film without re-measuring.

It does **not** carry per-card layout numbers — those were fitted to the original's
words in the original's typeface and must be re-fitted per card, as SKILL.md says.

## Skeleton

**Cut frames:** `48 78 95 98 105 113 125 147 168 203 255 298 335 407 463 485 517 531 564 615 647 700 756`

23 segments. Duration min 0.067s, median 2.833s, max 1.100s — note the median sits
*above* the max of the fast run, because the film is bimodal: a burst of very short
cards (the 95 / 98 / 105 / 113 cluster is three cuts inside 18 frames) against long
held ones. That contrast is the pacing signature; averaging it away produces a film
that feels nothing like the reference.

**Blank gaps:** 10 non-zero runs, 67 frames total, longest 37 frames — the cold
open before the first card. The gaps are load-bearing. When deriving, verifying
that the gap runs line up is the structural check that replaces grading.

**Backgrounds:** 19 segments on black, 4 on white. The white cards are the
punctuation.

## Music grid

**149.9 BPM, offset 0.0, 12.008 frames per beat** at 30fps.

Cuts sit close to the grid but are not quantised to it. Do not snap a derived
film's cuts to the beat: the reference's slight anticipation is part of why it
feels driven rather than mechanical.

## Mechanics

The movement vocabulary, counted across all segments. Most cards run several
signals at once, which is why the counts exceed the segment count.

| Mechanic | Segments |
|---|---|
| mass (reveal / wipe / type-on) | 19 |
| width (typing / zoom / scale) | 19 |
| height (grow / zoom) | 17 |
| centroid x (pan / recenter) | 14 |
| top edge (rise / drop) | 11 |
| centroid y (vertical move) | 8 |
| bottom edge (rise / drop) | 5 |

Read together: nearly every card both *reveals* and *scales*, most also drift
horizontally. Almost nothing enters by simple opacity alone.

## Typography

Apple house sans. Identified by glyph IoU, not column profile — SKILL.md is
emphatic about this and it is the right call. Substituted face and its measured
ceiling are recorded in `.analysis/fonttest/`; the font ceiling was measured
*before* a convergence number was promised, which is what makes the 99 target
honest rather than aspirational.

## Blur and shutter

Motion blur present and tested, not assumed — see `.analysis/blur/`. Cards that
strobe without it are the ones with fast horizontal travel.

## Audio

Onsets and cuts both recorded in `.analysis/ref/audio.json`. The audio is the
second clock: where visual segmentation is ambiguous on a soft dissolve, the
onset disambiguates the frame.

## Convergence

The `abe-ad` clone graded **99.35% of the achievable ceiling** (grade A), 776
frames compared, frame count matching exactly. **22 of 23 cards reached 99-100%.**

That gap is the honest state of this reference, not a finished number. The cards
that resisted are the fast cluster around frames 95-125, where a one-frame
boundary error costs several points and the frame-boundary trap in SKILL.md §7
applies directly.

## Derived works

Two films on one skeleton. Every row is a measurement pass that did not have to
happen twice — and the reason this entry exists.

| Build | Date | What changed | Structure held? |
|---|---|---|---|
| `abe-ad` | 2026-08-29 | Direct replication, the convergence target | n/a — this is the clone |
| `systo-26s` | 2026-08-30 | Systo copy, brand and voice; rendered 16:9 and 9:16 | Yes — both cuts run 25.8667s, identical to the reference |

The `systo-26s` pair is the one that shipped: both the 1920x1080 and 1080x1920
renders carry the reference's exact 25.8667s runtime, which is the structural
check passing.

## Licence and provenance

Apple's ad, sourced from a third-party Alight Motion showcase upload. **The
skeleton is fair to study; none of its assets are reusable.** Do not carry over its
footage, audio bed, typeface licence, copy or marks. A derived film must replace
all of them — which all three derivations above did.
