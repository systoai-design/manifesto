# Library entry template

Every `<slug>.md` follows this shape. Uniformity is the point: entries are read by
agents that have never seen the reference and may no longer have the file. Every
value is **measured, not estimated** — it comes out of `segment.mjs`,
`measure.mjs`, `audio-beats.mjs`, `font-identify.mjs`, `grade.mjs`, never off a
viewing.

**What belongs here:** the measured skeleton. Cut frames, durations, easing,
mechanics, blank gaps, the music grid, the audio cadence, the typeface finding,
the shutter, the convergence achieved and where it stalled.

**What does not:** the reference video, its frames, its audio, its copy, or any
still lifted from it. The library is measurements, not media. An entry that needs
the source file attached to be useful is a wrong entry.

This exists because of one line in SKILL.md: *"Once you have its cut frames,
easing curves and mechanics, you can hang different copy, palette and typography
on that skeleton."* Without a library, every new film from the same reference
re-runs the entire measurement pipeline — decode, segment, fit, identify, grade —
to rediscover numbers that were already known.

Omit a section only when it genuinely does not apply, and say why in one line.
An empty heading beats an invented value.

---

```markdown
# <slug>

**Callable as: <Name>** (aliases: <what someone would actually say>)

<One line: what the film is and what it does.> Measured <date>.
Source: <w>x<h> @ <fps>fps, <frames> frames, <duration>s. <Where it came from.>

## Fidelity — <skeleton | partial | signature-only | none>

- `skeleton` — cut frames, per-segment durations, mechanics, gaps and the music
  grid are all recorded. **Only this value licenses deriving a new film from the
  entry without re-measuring the source.**
- `partial` — some stages measured. Saves part of a re-measure, replaces none.
- `signature-only` — pacing character and a mechanic vocabulary. No frame numbers.
- `none` — seen, not measured.

Never promote this line without re-running the measurement. Under-claiming costs
one decode pass; over-claiming silently ships a film cut on invented frames.

## Skeleton

**Cut frames:** `<the frames.txt line, verbatim>`

<Segment count. Duration min / median / max. How many blank-gap runs and their
total, since those are load-bearing for pacing and are the thing to verify when
deriving. Anything irregular about the cut rhythm.>

## Music grid

<BPM, offset, frames-per-beat. Whether cuts sit on the grid or deliberately
against it. If there is no music bed, say so.>

## Mechanics

<Which motion mechanics appear and how often, from the per-segment signals. This
is the film's movement vocabulary, and it is what actually transfers to a derived
work.>

| Mechanic | Segments |
|---|---|
| <mass (reveal / wipe / type-on)> | <n> |

## Typography

<The identified face and the method (glyph IoU, never column profile). The
substitution used, and its score. The font ceiling measured before promising a
convergence number.>

## Blur and shutter

<Whether motion blur is present, tested not assumed, and the shutter that matched.>

## Audio

<Onset count, whether cuts align to onsets or to the visual clock, voiceover
presence and word-level cadence if measured.>

## Convergence

<The grade achieved on the clone, the measured ceiling, and how many cards stayed
below target. Name the cards that resisted and why - that is the expensive
knowledge.>

## Derived works

<Films built on this skeleton, and what each changed. This is the entry paying for
itself: every row here is a measurement pass that did not have to happen twice.>

| Build | Date | What changed | Structure held? |
|---|---|---|---|

## Licence and provenance

<Whose film it is. What may be learned from it (structure, pacing, mechanics) and
what may not be reused (footage, audio, type, copy, marks). If the reference is a
third party's ad, the skeleton is fair to study and its assets are not yours.>
```
