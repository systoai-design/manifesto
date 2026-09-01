# Measured reference library: index

One line per reference measured. Newest last. Read this before ingesting anything;
append to it after. Full entries live beside this file as `<slug>.md`.

**Every entry is callable by name.** "Build me a 30-second film on the Apple
Business Essentials skeleton" resolves through the *Call it* column below — match
case-insensitively against the name, the slug, or any alias in the entry — then
runs *Deriving a NEW film from a measured reference* (SKILL.md) from the recorded
skeleton instead of re-measuring the source.

**Why this exists.** SKILL.md already says a measured reference is not only
something to clone: once you have its cut frames, easing curves and mechanics you
can hang different copy on that skeleton. Until this library, none of that
survived the job. Every new film from the same reference re-ran the whole
pipeline — decode, segment, fit, identify the face, detect blur, analyse audio —
to rediscover numbers that had already been measured once.

**What belongs here:** cut frames, per-segment durations, mechanics, blank-gap
runs, the music grid, the audio cadence, the typeface finding and its ceiling, the
shutter, the convergence achieved and where it stalled.

**What does not:** the reference video, its frames, its audio, its copy, or any
still lifted from it. Measurements, not media.

**Fidelity** is declared per entry and never promoted without re-measuring.
`skeleton` licenses deriving without re-measuring; `partial` saves part of a pass;
`signature-only` is a pacing vocabulary; `none` is a placeholder.

| Call it | Reference | Measured | Native | Fidelity | Derived | Notable |
|---|---|---|---|---|---|---|
| **Apple Business Essentials** | [apple-business-essentials](apple-business-essentials.md) | 2026-08-29 | 1280x720 @30fps, 776f, 25.867s | **skeleton** | 2 | Bimodal pacing — a three-cut burst inside 18 frames against long held cards; 149.9 BPM grid that the cuts deliberately anticipate rather than sit on; 10 blank-gap runs are load-bearing; clone graded 99.35% of ceiling, grade A, with 22 of 23 cards at 99-100% |

---

## Reading a row

*Native* is what the reference actually is, not what you rendered. A derived film
inherits the frame count and duration, so this column is the contract.

*Fidelity* tells you whether you can work from the entry alone. Only `skeleton`
means yes — and even then the entry supplies numbers, never media.

*Derived* counts the films already built on this skeleton. A high number is the
entry earning its keep.

*Notable* is the thing that would have cost an hour if nobody had written it down.
