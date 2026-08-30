---
name: motion-replicate
description: >
  Replicate a motion-graphics video (ad, kinetic typography, logo sting, title
  sequence, UI animation) from a video file or URL into a rendered HyperFrames
  composition that matches it frame-for-frame — or build a NEW film on that
  measured skeleton, swapping in different copy, brand and voice while keeping
  its cuts and easing. Use whenever the user shares a video and asks to
  replicate, recreate, clone, copy, "make this exact animation", or "do this but
  for us" — including Alight Motion / After Effects showcase videos and ad
  recreations, and for the work that follows: replacing a voiceover, composing
  an original music bed to clear the borrowed one, raising the frame rate,
  adding motion blur to cards that strobe, and reframing to 9:16 or 1080p. Also
  carries the Apple-style per-character cascade (SF Pro, rise + fade + blur) and
  how to translate an After Effects Range Selector into GSAP, and Apple's
  liquid-glass surface in CSS. Not
  for websites — that's swipefile. Measures the reference numerically (per-frame
  pixel analysis, fitted easing curves, audio-onset cut detection) rather than
  eyeballing sampled frames, and scores convergence with SSIM.
---

# Motion Replicate — video reference → matching rendered video

## The core principle

**Do not replicate what you saw. Replicate what you measured.**

Reading sampled frames with vision tells you *what the cards say* and roughly
what happens. It cannot tell you that a cut is at frame 116 not 122, that a
rise is `power2.out` over 7 frames not `power3.out` over 9, or that the piece
is cut to audio onsets. Vision gets you a draft; measurement gets you a
replica. The measurement stage (§3) is not optional polish — it is the skill.

Proven on a 26s kinetic-typography ad. Eyeballed from ~70 sampled frames it
scored **98.26% of ceiling**; measured and graded to convergence it reached
**99.35%, grade A, with 22 of 23 cards at 99-100%**. What measurement found that
sampling never would: a **whole missing card** (a phrase that appears twice),
three cards in the wrong order, a render-order bug blanking 13 frames, **eleven
clips starting a frame late**, clip ends rendering one frame long, and a paper
colour that was off-white where the reference is pure white. Two worked projects, each with a `FINDINGS.md` carrying the full measurement
trail - every correction, its evidence, and every change that scored worse and
was reverted:

- `D:\New Claude\motion-replicate\abe-ad` - the replication itself
- `D:\New Claude\motion-replicate\systo-26s` - a **different film built on that
  measured skeleton**: same 776 frames and cut list, new copy, brand, voice and
  original music bed, delivered at 60fps in 16:9, 1080p and 9:16. Its `build.sh`
  is the whole render pipeline including the per-card shutter.

## 0. Ground rules

- **Clone what you can't copy.** Unavailable font → nearest metric match
  (Helvetica → Arial on Windows; verify with §3.5, don't assume). Trademarked
  glyph → hand-drawn SVG. Soundtrack → mux the reference's own while building,
  and say plainly that this makes the result private/study-only. If it has to
  clear, replace the read and compose a bed — see the audio sections at the end.
- Work dirs: `D:\New Claude\motion-replicate\<slug>\` for the project,
  `<project>\.analysis\` for measurement artifacts. Never C:.
- Scripts live in this skill's `scripts/`. Refer to it as `$S` below.

## 1. Ingest

```bash
ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=nb_read_frames,avg_frame_rate,width,height "<video>"
ffmpeg -v error -y -i "<video>" -vn -acodec copy media/reference-audio.m4a
```

`nb_read_frames` is authoritative. Your composition's duration must be
`frames / fps` exactly — a replica that is 3 frames long is already wrong.

## 2. Watch — for orientation only

Two passes, purely to learn the *content*: what each card says and the rough
order. Do not derive timings here.

```bash
node "C:\Users\Kyle\.claude\skills\watch-video\scripts\watch.mjs" "<video>" --every 0.5 --max 60
ffmpeg -v error -y -ss <t0> -t <len> -i "<video>" -vf "fps=10,scale=426:-1,tile=4x3" "sheets/W_%02d.jpg"
```

A 0.5s grid **misses whole cards** (it missed two in the first build), so run
the 10fps sheets over every transition window. Then stop looking and measure.

## 3. Measure — the core

### 3.1 Decode once, analyse many times

```bash
node "$S/extract.mjs" "<video>" .analysis/ref --w 640 --h 360
node "$S/measure.mjs" .analysis/ref
```

`extract.mjs` writes a raw RGB24 plane file so every later probe is a byte-offset
read — no image-decoding dependency, no re-decoding per query. `measure.mjs`
computes per frame: background luma, ink mask + bbox + centroid, ink mass, edge
energy, saturation, and per-third hue, plus column/row ink profiles.

### 3.2 Segment into frame-exact cards

```bash
node "$S/segment.mjs" .analysis/ref
```

**The cut model that actually works.** Motion-graphics pieces do not cut on
scene-change heuristics; they cut through **blank frames**. A card ends, the
frame goes empty for 1-8 frames, the next card begins. So:

- a *blank run* (`inkFrac` ≈ 0) is a cut boundary **and a rhythm feature** —
  reproduce the gaps, they are why the reference breathes;
- within a content run, split on a large column-profile L1 distance (a hard
  content swap) or a background flip.

Generic scene detection finds only the background flips. In the proven build it
found 5 segments where the truth was 23.

`segment.mjs` also reports, per card: `gapBefore` in frames, per-word reveal
frames (from contiguous column blocks), and a **least-squares best-fit GSAP
ease** for every monotonic motion it finds, with runners-up and RMSE. That is
where `power2.out` vs `back.out(1.4)` stops being a guess.

### 3.3 Identify the mechanic — read the edges, not the picture

```bash
node "$S/track.mjs" .analysis/ref --from <sec> --to <sec> --x0 <px> --x1 <px>
```

Per frame it prints top / bottom / left / right / ink / meanAlpha for a region.
The decision table:

| Signature | Mechanic |
| --- | --- |
| bottom fixed, top rising | translate-through-fixed-mask, or clip reveal |
| top and bottom rise together | free translation, no mask |
| left fixed, right growing in steps | typing — each step is one character |
| both edges expand from centre | scale |
| edges static, ink rising | opacity fade |
| meanAlpha < 0.9 on a settled frame | element is semi-transparent there |

### 3.4 Test for motion blur — do not assume it

Fast moves *look* blurred in a sampled frame when they are actually
hard-masked. Pull the full-res frame and look:

```bash
ffmpeg -v error -y -i "<video>" -vf "select=eq(n\,<FRAME>)" -frames:v 1 -vsync 0 out.png
```

Crisp horizontal shear through glyphs = mask reveal (reproduce with
`overflow:hidden` + a `yPercent` tween). Soft directional smear = real motion
blur (reproduce with `/hyperframes-animation` → `motion-blur-streak`). In the
proven build the "obvious" blur was entirely mask reveals — building blur would
have made it *less* accurate.

### 3.5 Verify the font substitution numerically

Compare a **settled** bbox on a card where both videos show the *same content*:

```bash
node "$S/track.mjs" .analysis/ref  --from <t> --to <t+0.07>
node "$S/track.mjs" .analysis/mine --from <t> --to <t+0.07>
```

Trap that will burn you: if the two sides are showing *different cards* at that
timestamp, the width difference is a timing bug, not a font bug. Confirm the
same text is on screen first. In the proven build Arial matched Helvetica within
4-8px — no global type correction was needed, and the alarming first numbers
were a card that cut 0.7s early.

### 3.6 Find the second clock: audio

```bash
node "$S/audio-beats.mjs" "<video>" --dir .analysis/ref --fps 30
```

Reports audio onsets and how many picture cuts land within 3 frames of one. In
the proven build **12 of 23 cuts were locked to onsets within 0-2 frames** — the
piece was cut to the music. When cuts are onset-locked, snap your cuts to the
onset frames; the sync is felt even when the picture alone looks fine.

### 3.7 Identify the cards frame-exactly BEFORE measuring anything else

Build a labelled contact sheet with one settled frame per segment, then sweep
every boundary two frames at a time:

```bash
# one representative frame per segment (70% through each)
node -e "const b=require('./.analysis/ref/beats.json');console.log(b.segments.map(s=>s.startFrame+Math.floor(0.7*s.frames)).join(' '))"
# then per frame: select=eq(n\,F), scale, drawtext the frame number, and tile
ffmpeg -v error -y -i ".analysis/cards/r_%02d.jpg" -vf "tile=4x6" SHEET.jpg
```

This is not optional and it is not the §2 watch pass. In the proven build the
0.5s pass produced a card list that was **wrong**: it missed that one phrase
appears twice and put three cards in the wrong order. Two segments also merge
several cards each (no blank frame between them), so a per-segment sheet alone
is not enough — sweep the boundaries.

**Never hand a card label derived from eyeballed frames to a downstream step.**
Doing so sent measurement agents looking for the wrong words in the right frames.

## 4. Beat map

Write the table from measured values only: `startFrame | t | card | gapBefore |
mechanic | fitted ease | per-word frames`. This is the build spec. Convert
frames to seconds as `f/fps` so every value lands on a frame boundary.

## 5. Build — HyperFrames route

`/hyperframes` → `/general-video` (multi-scene) or `/motion-graphics` (short
single unit) → `/hyperframes-core` + `/hyperframes-animation`. Scaffold with
`npx hyperframes init . --non-interactive --example=blank`, then write
`BRIEF.md`, `frame.md` (measured palette/type), `STORYBOARD.md` (the beat map).

For a continuous typography piece: **one monolithic standalone composition**,
one `.clip` per card, one paused GSAP timeline with absolute-time `fromTo`s.
Accept the file-too-large lint warning and record why.

## 6. Technique map

Every entry is implemented in the proven build's `index.html`.

| Reference look | Implementation |
| --- | --- |
| word rises from an invisible baseline | mask span (`overflow:hidden`) + inner `yPercent`→0. Measure the true start offset; it is often ~60%, not 110% |
| word pops with overshoot | `fromTo scale`, `back.out(n)` — take `n` from the ease fit |
| typed characters | per-char spans, `fromTo autoAlpha` dur 0.02 (binary, never fade) |
| line re-centres while typing | hidden words keep layout width; group `x = (unrevealed width + gaps)/2`, stepped per word. Widths from canvas `measureText`, never DOM rects |
| phrase morph (word → word) | shared letters persist; outgoing letters fade on measured frames; new text absolutely positioned at a `measureText` offset; group x-shift recentres |
| bar chart behind text | absolute bars, `scaleY` 0→1 origin bottom |
| tilted word wall | JS-generated rows, per-tile colour lerp, one world wrapper. **Check whether it zooms or pans** — measure `bboxW` across the card |
| circle wipe from a word | absolute dot at that word's measured centre, `scale` 0→N |
| typing-indicator dots | staggered alpha in, N bounce cycles, drift-up exit — get N and the period from `track.mjs` |
| gradient text | `background-clip:text` + slow `backgroundPosition` tween |
| slam zoom | wrapper `scale`, origin at the measured target glyph, hard cut at peak |
| letter wave on an arc | per-letter baked `y_i`/`rot_i`, three sequential `fromTo`s (`immediateRender:false` on the later ones) |

Lint traps: explicit from-state on every `fromTo` plus `immediateRender:false`
when re-owning a property; no CSS transform on a tweened element; every
`<audio>` needs an `id`; keep JS measurement constants in sync when CSS font
sizes change.

**The render-order trap (cost 13 blank frames, and `preview` showed nothing
wrong).** If the *only* tweens touching an element are fade-OUTs carrying
`immediateRender:false`, a render worker that seeks past them before seeking
back leaves the element latched hidden — the card renders blank even though a
direct seek to the same time looks correct. Give every such element an explicit
baseline at its card's first frame:

```js
tl.set(['#m-of', '#m-y', '#m-o'], { autoAlpha: 1 }, f(191));
```

Audit for this after authoring: any element whose first tween is a fade-out or
a `scale`-down needs a `tl.set` baseline. Only `compare.mjs` against the
rendered file catches it — never the preview.

## 6b. Reconstructing a scattered background

A tiled/scattered layer (a word wall, a logo field, a confetti scatter) will not
yield to guessing, and it will not yield to a grid fit either if the design is
irregular. Three tools, in order:

```bash
# 1. what distinct elements are in this frame, and what colour is each?
node "$S/components.mjs" wall.bin --w 1280 --h 720 --frame 3 --gap 0.13 --min-px 400
# 2. merge detections from EVERY frame of the move into authored space
node "$S/reconstruct.mjs" wall.bin --frames 8 --scales "1.131,1.128,..."
# 3. find every instance of one repeated element, occlusion and all
node "$S/match-tiles.mjs" scene.bin --frame 7 --template tpl.bin \
     --tpl-box "561,15,859,222" --scale 1.0 --min-sep 300
```

`reconstruct.mjs` is the one that beats occlusion: when the layer scales or pans,
an element hidden behind the subject on one frame is visible on another, so
mapping every frame's detections back through that frame's measured scale and
clustering them recovers elements no single frame shows. Derive the per-frame
scale from something you can measure on all of them (a foreground hero word).

Gotchas that cost real iterations:
- **Seed clustering from the largest blob**, not in reading order, or an `i`-dot
  starts its own group and nothing can join it.
- An accent mark shares no vertical band with its own letters; claim it by
  horizontal containment instead.
- `--min-sep` must be near the real element pitch or an N-tile grid reads as 2N.
- Element gaps are often smaller than intra-word letter gaps look; if adjacent
  elements merge into one blob, lower `--gap` before anything else.

When detection stalls, **optimise instead**:

```bash
node "$S/fit-tiles.mjs" ref.bin --w 640 --h 360 --first 108 --frames 8 \
     --scales "1.131,..." --tpl-frame 7 --tpl-box "263,7,446,111" --rot 2
```

`fit-tiles.mjs` stamps a real glyph template at candidate positions, scores the
whole layer against every frame at once, and hill-climbs the positions —
excluding pixels behind the subject, because the layer is unknowable there.
Layer IoU went 0.19 → 0.56 on the proven build where detection had plateaued.
Two cautions learned the hard way: a **denser fit can score higher on template
IoU yet worse in the render** (the template is the reference's glyph, yours is
not), and **"uncovered ink" peaks are usually edge residue from tiles you
already have**, not missing elements — adding tiles there made it worse.

**Check where the error actually is before iterating.** Split the card's error
between the foreground subject and the background layer:

```js
if (refLuma > 170 || mineLuma > 170) heroErr += d; else wallErr += d;
```

On the proven build this was the single most valuable measurement of the whole
session: eight attempts at the background moved the card 76.9 → 78.0, because
**68% of the error was the foreground hero word** — 10% too narrow, 6% too
short and 36px off centre. Fixing that one element moved the same card 77.4 →
84.3 in a single render. Measure the split first; iterate on the bigger half.

Split it a third way once the subject is aligned — **interior vs outline**:

```js
if (refHero && mineHero) interior += d;        // fill colour
else if (refHero !== mineHero) edgeBand += d;  // glyph OUTLINE
else layer += d;
```

That is what tells you when you have hit the **font substitution wall**. On the
proven build the interior fell to mean 5.2 while the edge band held 319k pixels
at mean 226 — the substituted face's outline, not anything you can tune. Two
things still help before you give up:

- **Fit each glyph individually** when the word is short. Measure each letter's
  box in the reference, then correct with `scaleX` + a margin (transforms do not
  affect flow, so the advance needs its own margin). Use `em` units and the same
  fit serves every instance of that word in the composition. This brought letter
  widths within 1-2px and moved the card 88.2 → 89.5.
- **Check the fill is actually flat.** A big hero glyph that reads as white was
  measured as a brightness *arch* — 220 at each edge, 251 in the middle.

### Identifying the reference's typeface — measure, never assume

If a substitute face is suspected, **test candidates instead of reasoning about
them**. Two numbers settle it, and they can disagree:

1. **Raw ink-width ratios** of 3-4 glyphs against the reference's. Cheap, and it
   ranks candidates.
2. **The outline mismatch band** — pixels where one side has glyph and the other
   does not, with each candidate first fitted to the reference's letter widths.
   This is the one that decides, because it measures the *shape*, not the
   proportions.

On the proven build these disagreed and the second was right. Nimbus Sans
(URW's metrically-exact Helvetica) had the closest ink-width ratios — but a
**51% larger outline mismatch** than Arial-with-a-per-glyph-fit (483,139 px vs
319,500), and it dropped four other cards below target because their sizes were
fitted to Arial's metrics. The reference was neither Helvetica nor Inter.

So: enumerate the installed fonts, download and test the plausible candidates
(Nimbus Sans for Helvetica, Inter or Roboto for a UI grotesque — all freely
licensed), and **keep whichever measures best, even if theory says otherwise**.
Then say plainly what the residual is. Do not swap a face globally late in a
build without re-fitting every card's size — advance widths may match while ink
extents do not.

## 7. Score and converge — objectively

### The grade — the number you drive to 99-100

```bash
npx hyperframes render
node "$S/grade.mjs" "<reference>" "<my render>" \
     --beats .analysis/ref/beats.json --out .grade --diffmaps --target 99
```

`grade.mjs` reports, **per card, never as one blended number for the film**:

| column | meaning |
| --- | --- |
| `sim%` | `100 - mean|delta| / 255 * 100` |
| `ceil%` | the same measure, reference vs a **re-encode of the reference** |
| `%ceil` | `sim / ceiling` — **this is the grade** |
| `within16` | share of pixels whose channels all differ by ≤ 16/255 |
| `worst@` | the single worst frame in that card, to look at directly |

**Why the ceiling matters.** Both files are lossy H.264, so a pixel-perfect
clone still cannot score 100%. Pushing a card past its own ceiling measures the
codec, not the replica. A card sitting at its ceiling is FINISHED. (In the proven
build the ceiling came out at 99.99%, so 99-100% was genuinely reachable — but
measure it, never assume it.)

Sort worst-first and work down; that table is the queue. Re-grade after every
change and state the before/after. Never declare convergence from eyeballed
side-by-sides.

`compare.mjs` remains available for a quick SSIM/PSNR read; `grade.mjs` is the
one to drive the loop.

Fix in this order, because the errors are coupled:
1. **total frame count** (a length mismatch offsets everything downstream),
2. **clip boundaries** — see the frame-boundary trap below; it is worth more
   than any single card's animation,
3. **flat colours** — background, paper and ink. A global colour that is a
   couple of levels off costs more than any easing curve, because it is wrong
   on every pixel of every frame of those cards. Sample them, do not assume,
4. **cut times** (snap to measured frames, and to audio onsets where locked),
5. **blank gaps** between cards,
6. **within-card mechanics** (mask vs translate vs scale — §3.3),
7. **eases and per-word stagger** (from the fit),
8. **geometry** (font size and position from settled-frame bboxes).

### The frame-boundary trap (two bugs, one cause)

Clip windows are `[start, start + duration)` compared against a frame's sample
time. Decimal times land ambiguously on both ends:

- **Ends are inclusive.** `17.8 + 1.4667 = 19.2667` and frame 578's time is
  `19.26666…`, so the card renders one frame too long and bleeds into the next.
- **Starts rounded UP miss their own first frame.** `19.2667 > 578/30`, so the
  card begins at f579 and the frame before it goes black.

Both are invisible in the preview and in eyeballed side-by-sides. On the proven
build **11 of 29 clips started a frame late**; fixing that alone moved the film
0.16 points, and fixing the ends moved it 0.16 more. Write every boundary from
its frame number, biased inward:

```js
start    = (frame / fps) - 0.0002        // just BELOW its own frame
duration = ((endFrame + 1 - frame) / fps) - 0.0011   // just short of the next
```

Audit this before chasing any easing curve.

A useful convergence check: run `segment.mjs` on your own render and compare its
segment count and start frames against the reference's. They should match
one-for-one.

**Score every change; revert the ones that lose.** In the proven build three
successive "improvements" to one card — including one built from measured row
pitch — each scored *worse* than the original guess, and were reverted. Without
the score they would all have shipped as progress. Two other edits regressed a
neighbouring card and were only caught because the per-card table moved.

**Also watch the seams.** Two of the largest single-frame errors were clip
boundaries where one card ended a frame before the next began, leaving a hole
that neither the preview nor a card-level average reveals. Sort by `worst`, not
just `delta`, and check the frames either side of every cut.

## 8. Deliver

Verify the **render**, not the preview: extract frames from the MP4, hstack
against reference frames at the same timestamps, read them, and report the SSIM
plus any residual deltas honestly.

Sweep the whole film before handing anything over, not one frame — see
*Verifying a build before handing it over*. Say plainly what is and is not
cleared: a muxed reference soundtrack makes the artefact private/study-only, and
separating a bed does not license it.

## Scripts

| Script | Purpose |
| --- | --- |
| `extract.mjs` | video → raw RGB24 plane + meta (one decode, random access) |
| `measure.mjs` | raw → per-frame bbox / ink / centroid / edge / hue + profiles |
| `segment.mjs` | frame-exact cuts (blank-run model), per-word reveals, fitted eases |
| `track.mjs` | per-frame edges of one region — the mechanic identifier |
| `audio-beats.mjs` | audio onsets + how many cuts lock to them |
| `compare.mjs` | SSIM + per-card metric delta vs the reference |
| `grade.mjs` | **the graded loop** — per-card % of ceiling, letter grade, diffmaps |
| `components.mjs` | connected components in a frame, grouped into words + colours |
| `reconstruct.mjs` | merge detections across a moving shot into authored coordinates |
| `match-tiles.mjs` | template-match every instance of a repeated element |
| `fit-tiles.mjs` | **optimise** a scattered layer's positions against the reference |
| `reframe.mjs` | generate an aspect-ratio variant with the stage wrapper done right |
| `check-framing.mjs` | sweep a render for centring, clipping and the widest content |
| `vo-transcribe.py` | word-level frame numbers for the reference read - the timing template |
| `vo-profile.py` | the reference read's median f0, pitch spread and words per minute |
| `vo-rank-voices.py` | rank candidate voices by f0 distance from that target |
| `vo-generate.py` | render each line at nine speeds, keep the take that fits its window |
| `vo-mix-ratio.py` | does the original duck? and how far above its bed does the voice sit? |
| `vo-fit-eq.py` | grid-fit the EQ that clears the read, scored on the mud bands only |
| `vo-mix.py` | place each line to the sample, one constant gain on the bed |
| `vo-verify.py` | energy onsets vs plan - never verify placement with ASR |
| `bed-tempo-fit.py` | least-squares fit a tempo grid to your own cut list |
| `bed-compose.py` | synthesise an original bed - worked example |
| `bed-analyse.py` | tempo, pitch classes and energy arc of any bed |

### Measure the font ceiling before promising a number

If the reference's typeface cannot be obtained, find out what that costs
**before** spending days on layout. Take the cheapest pure-text card - a single
line on a flat ground, no motion, no colour - and fit it until its geometry
matches: ink width, ink box, and total ink mass.

On the piece this note comes from, that fit landed within 3 px of width, 1 px
of height and **0.05% of ink mass**. The card scored **97.51%**, and the glyph
IoU was **32.4%**. Only a third of the ink overlapped, and perfecting the
geometry had bought 0.32 points. Everything left was letterform shape.

That single number is the ceiling for every type-heavy card in the piece, and
it is cheap to obtain. Quote it before agreeing a similarity target: a film
that is mostly type cannot beat its font ceiling, however good the layout.

## Stop condition

Stop when a card reaches its own ceiling, or when the numbers stop moving —
not when the frame looks right. Concretely:

- A card at **≥99% of ceiling is done.** Do not keep tuning it.
- A card that survives **three changes without moving more than ~0.5 point** is
  telling you the model is wrong, not the values. Go and measure what fraction
  of that card's error belongs to which element (§6b) before touching it again.
- Some cards have a practical ceiling below the target. A dense irregular
  background reconstructed rather than traced is the usual one: on the proven
  build the word-wall card finished at **89.5% while the other 22 of 23 reached
  99-100%**, and its residual split 35.7% glyph outline / 60.0% layer
  arrangement — both traced to a typeface that could not be identified or
  obtained. Say so plainly in the handoff, with the reason, the measured
  before/after, and what would actually fix it — do not quietly average it away
  into the overall figure.

---

## Replacing the voiceover, keeping the bed

When the reference's soundtrack sells a different product, split it: keep the
music, replace the read. Six scripts in `scripts/` do this, and the principle is
the same as everywhere else in this skill — **measure, don't eyeball.**

**1. Separate.** `demucs htdemucs --two-stems=vocals`. Verify the removal
rather than assuming it: compare the instrumental's 300-3400 Hz speech-band
energy against the vocal stem's. A 14 dB gap is clean. Whisper returns "I'll
see you next time" from almost any non-speech audio — that is its hallucination
on silence, never evidence of residual dialogue.

**2. Transcribe the original read as a clock.** `vo-transcribe.py` runs
faster-whisper at word resolution over the *isolated vocal stem* and prints a
frame number for every word. This is a second clock, independent of the picture,
and it is the timing template: write the new lines to the original's syllable
budgets and split them at the frames where the original speaker took breath.
Card starts tell you where a line may begin; the original read tells you how
long it has.

**3. Cast by measurement.** `vo-profile.py` gives the original read's median f0,
pitch spread and words-per-minute. `vo-rank-voices.py` profiles every candidate
voice by autocorrelation f0 on its preview clip and ranks by distance from that
target. Register is measurable; pick from the shortlist by ear, not the whole
catalogue. Weigh the engine's own quality grade against f0 distance — 17 Hz is
about 1.5 semitones, an ordinary difference between two real VO artists, and
worth trading for a materially better voice.

**4. Never splice engines.** If a hosted service runs out mid-batch, regenerate
every line locally rather than shipping a read half from each — the timbre
change mid-film is far more noticeable than either voice alone. Kokoro
(`kokoro-v1.0.onnx`, CPU, no GPU needed) is a good local fallback; re-run the
same f0 ranking over its voices so the choice stays measured.

**5. Fit by search, not by stretching.** `vo-generate.py` renders each line at
nine speeds and keeps the take closest to its window *without exceeding it*.
Time-stretching a finished take to fit is audible; choosing the take that
already fits is not.

**6. Place by sample, verify by energy.** `vo-mix.py` writes each clip at
`round(start_frame / fps * sr)` with 8 ms edge ramps. `vo-verify.py` then finds
each line's actual energy onset in the assembled track and reports the drift.
Verify with energy onsets, not ASR segment starts — Whisper's boundaries lag
soft attacks by a third of a second and will make a sample-accurate mix look
broken.

**Do not duck the bed until you have checked whether the original does.**
Sidechaining the music under the voice is the reflex, and it pumps. The
reference settles it: `vo-mix-ratio.py` measures the isolated bed's level during
speech against its level during silence, and measures how far the original voice
sits above its own bed. On the piece this skill was built from, the bed moved
+1.40 dB - *upward* - and the voice sat +2.28 dB above it. So: one constant gain
on the bed, voice set to the measured ratio, no dynamics on the bed at all.

Testing for pumping afterwards is harder than it looks, because music has swells
of its own - on that same piece the isolated bed rose 8.4 dB after one line and
fell 10.7 dB after another, which any naive detector flags. The test that
actually separates them is the direction of the whole effect: in an un-ducked
mix, windows under voice are *louder* than windows without, because the voice
adds on top. In a ducked mix the quiet windows are louder, because the bed
springs back.

**"Muffled" usually means mud, not missing highs.** Diagnose it by comparing
long-term average spectra against the original read, normalised to a mid band so
you are comparing tilt and not level. The synthetic read that prompted this note
was already 10-12 dB *brighter* than the reference above 4.5 kHz; the muffle was
+6 dB of excess at 150-300 Hz masking the consonants. `vo-fit-eq.py` grid-fits
the correction, scoring squared error against the reference's tilt **in the mud
bands only** - leave presence out of the objective, or the fit will happily dull
a read that needs to stay bright.

**Licensing is not a technical question.** Separating a bed does not license it.
A kept bed is fine for an animatic or a pitch and is not clearable for a paid
run. When it has to clear, compose one - and note that AI music generators
mostly do not solve this, because their weights carry their own terms
(MusicGen's are CC-BY-NC, which fails for the same reason the borrowed bed did).

## Composing a replacement bed

`bed-compose.py` is a worked example: sub, detuned-saw pad, plucked pulse,
kick, ticks, shaker, impacts, risers and a bell figure, through a
synthetic-IR reverb, all from oscillators and noise. Three things make it fit a
film rather than just play under one.

**Fit the tempo to the picture, not to the reference's music.**
`bed-tempo-fit.py` least-squares fits a BPM and phase against your own cut
list, weighting structural cuts higher. On the piece this was built for it
landed on 150 BPM - a clean 12 frames per beat at 30fps - with the big cuts
within 0.1-2.5 frames of a beat. The edit is yours, so a grid derived from it
is yours too.

**Write the arrangement as an explicit dB arc through the film's sections**,
not as instrument on/off gates. The first attempt here gated instruments and
measured dead flat at -11 dB for the entire film; replacing that with a
breakpoint arc (silent open, verse, build into the peak, step back for the
logo) is what made it feel composed.

**Leave a hole for the voice.** Lowpass the pad below 1 kHz, keep percussive
air above 6 kHz, and check the result: measure the bed's spectrum relative to
its own 500-800 Hz band and confirm 1.5-4 kHz is well down.

Verify the result by pointing `bed-analyse.py` - the same script you used on
the reference bed - at your composition. It should detect the tempo you
composed and pitch classes matching the harmony you wrote. If the detected
pitch classes match the *reference's*, you have transposed rather than
composed.

---

# Deriving a NEW film from a measured reference

A measured reference is not only something to clone. Once you have its cut
frames, easing curves and mechanics, you can hang different copy, palette and
typography on that skeleton and get a film of your own that moves like one that
already works. Same length, same cuts, different argument.

**What transfers:** cut frames, durations, easing curves, mechanics, the blank
gaps, the audio's word-level cadence. **What does not:** copy, colour, type,
harmony, and any layout number fitted to the old words.

**Do not grade it.** Pixel similarity is meaningless once the words differ.
Verify that the *structure* survived instead:

- the frame count and duration match exactly
- `segment.mjs` finds the cuts on the same frames
- the blank-gap runs line up

On the build this came from, 9 of the reference's 11 blank runs landed
identically; the other two differed by a single frame where a mask reveal
crosses the ink threshold, because the substituted face covers less area per
glyph. That is the expected residue, not a fault.

**Per-card sizes must be re-fitted.** Every font size, offset and tile position
in the original was fitted to the original's words in the original's typeface.
Carry them over unchanged and things will be the wrong size, usually too wide.
Re-measure per card.

**Watch for stale selectors.** A tween copied from the source build that targets
a card the new film does not have fails silently. Grep every selector in the
timeline against the markup before rendering.

## Deviating from the reference on purpose

Sometimes a card reads badly and the reference is doing exactly the same thing.
**Check the reference before changing anything.** On the build this came from, a
morph card showed garbled text for eight frames; the reference showed the same
garble on the same frames. The replication was faithful and the *mechanic* was
the problem, made worse here because a heavier typeface turns a thin garble into
a dense blob.

That reframes the decision. It is no longer a bug fix, it is a design change,
and it should be:

- **made deliberately**, because the client's film matters more than fidelity to
  a reference nobody else will see
- **recorded as a deviation**, with the reference's own behaviour noted, so the
  next person does not "fix" it back

The user's eye is the ground truth for whether something reads badly. Your
measurements are the ground truth for *why*, and for whether the fix worked.

---

# Frame rate, and when to reach for a shutter

## Raising the frame rate needs no retiming

If the timeline is authored in seconds (`var F = 1/30`, every cue written as
`f(frameNumber)`) then the frame rate only controls how often that timeline is
sampled. Render at 60 and you get twice the frames, the same duration, every cut
on the same second. `hyperframes render -f 60` needs no edit at all.

Keep the authoring grid at the reference's frame rate. It is the grid everything
was measured on; changing it invalidates every number in the build.

## "Choppy" is usually not a frame-rate problem

Measure before assuming. For the suspect card, decode its frames and report:

- **how many are identical to their predecessor** - duplicates mean the motion
  really is updating at a lower rate
- **the per-frame change** - how much actually moves between frames
- **the per-frame step of the moving element's bbox** - a smooth ease shows a
  smooth progression of steps

On the card that prompted this section every frame was distinct, and the hero's
width stepped -2, -6, -10, -14, -18, -23, -26, -30, -31, -27, -22, -19, -14,
-10, -6 px: a clean ease with no snapping. The motion was perfect. The problem
was that **31 px of edge travel per frame strobes** on a high-contrast
letterform, because the eye cannot fuse consecutive frames. More frames do not
fix that. A shutter does.

Above roughly 5-10 px of edge travel per frame, expect strobing on hard edges.

## The shutter, and the rule that governs it

Render at 240fps and average back down. `tmix=frames=4:weights=1 1 1 1,fps=60`
is a 360 degree shutter at 60fps. Verify it landed by profiling one moving edge:
a single step (57 -> 228) should become a ramp (57, 93, 128, 143, 176, 188, 223).

**Never let the shutter window straddle a cut.** Averaging across a cut blends
two cards into a ghost frame, and on a film built from hard cuts that is far
worse than the strobing you set out to fix. It is measurable as a jump in the
first frame's change after the cut: 1.6 units at a 180 degree shutter, 24.6 at
270 on the same material.

So blur is applied **per card, held a frame clear of every cut**, and
composited over the sharp render:

    ffmpeg -i sharp.mp4 -i blurred.mp4 -filter_complex \
      "[0:v][1:v]overlay=enable='between(n,218,230)+between(n,268,304)'[v]" \
      -map "[v]" -map 0:a ...

Do not reach for a global shutter. Most of a kinetic-type film is static holds
and hard cuts, where blur does nothing (averaging identical frames returns the
same frame) except put the cuts at risk.

**Do not trust a global sharpness metric to tell you whether blur applied.** Mean
gradient energy over a whole frame is dominated by static content and barely
moves. Profile one moving edge instead.

---

# Reframing to another aspect ratio

## The trap

`hyperframes` sizes the composition **root** to `data-width` / `data-height`. So
putting a transform on the root scales a box that is *already the output size*,
from its top-left corner, throwing the content into a corner rather than
reframing it. At 1920x1080 the centre landed at (1440, 810); at 1080x1920 it sat
783 px low.

The measured stage must live in a **wrapper inside** the root, and the wrapper is
what gets transformed. `reframe.mjs` does this:

    node reframe.mjs index.html vertical.html --w 1080 --h 1920 --scale 1.3
    node reframe.mjs index.html wide1080.html --w 1920 --h 1080 --scale 1.5

## Choosing the scale

Run `check-framing.mjs` on the **native** render, the one at the authored stage
size, so the widest figure comes back in stage pixels:

    node check-framing.mjs renders/native.mp4 --w 1280 --h 720 \
      --fullbleed 216-231,854-865

The largest safe scale is `(targetWidth - 2*margin) / widestContent`. On this
build the widest line measured 683 px, which allowed **1.3x into a 1080-wide
frame**, so the vertical type came out *larger* than the 16:9, which is what
mobile wants. Reframing is not necessarily shrinking.

Pass `--fullbleed` for frames meant to fill or overflow: a slam zoom, a wipe
covering frame, a full-bleed texture card. Otherwise they dominate the widest
figure and force the scale down for no reason.

## Rendering larger, and proving it is not an upscale

Scaling the stage rather than the canvas means the browser re-rasterises type at
the new scale, which is a genuine re-render. Prove it: on a static card, measure
the 20-80% rise across glyph edges in the native render against a lanczos
upscale of the smaller one. 1.88 px against 2.75 px is a 1.47x gain, tracking a
1.5x scale. If the two match, something is rasterising at the wrong scale;
suspect `will-change: transform` on an ancestor.

## What a narrower crop breaks that a wider one does not

- **Anything that enters from an offset.** A lockup sliding in from x+285 clears
  a 1280-wide stage and runs off a narrower crop. It took two passes here
  because the first correction was estimated: 285 -> 195 still left the
  wordmark's period **9 px** from the frame edge. Measure the settled element,
  account for its entry scale, then solve for the offset.
- **Solid backgrounds sized to the stage.** A paper card inset to a 1280x720
  stage fills only a band of a 9:16 frame and reads as letterboxing. Extend it
  past the stage (`top: -400px; bottom: -400px`) so it fills. If `check-framing`
  reports many edge-touching frames on solid cards, this is why.
- **Full-bleed texture cards.** A hero word sized for 16:9 can be wider than the
  narrower frame. Resize it and its texture together, and add rows or columns so
  the field still bleeds off the new edges.

---

# Verifying a build before handing it over

**One frame is not a check.** This skill's worst moment was shipping a reframed
build whose content sat in the bottom-right corner, after finding and fixing
that exact bug in the *other* variant minutes earlier and verifying the fix on a
single frame of the one that was already correct.

Before handing over any build, sweep the whole film:

    node check-framing.mjs renders/out.mp4 --w W --h H --fullbleed ...

and read three numbers: mean offset from centre, worst offset, and frames
touching a side edge. A large worst-offset is usually a line mid-reveal and is
fine. Frames touching an edge that are not deliberately full-bleed are faults.

When you fix a class of bug, **check every artefact that could have it**, not
just the one you were looking at.

## A measurement bug that will cost you an hour

Decoding one frame gives `(H, W, 3)`, so `.mean(2)` averages the colour
channels. Decoding a *range* gives `(n, H, W, 3)`, where `.mean(2)` averages over
**width** and returns nonsense: here it reported a 469 px lockup as 3 px wide and
sent a correction off in the wrong direction. Use `.mean(3)`, or index the frame
first.

Any measurement that returns an absurd value is wrong until proven otherwise.
Sanity-check it against something already known before acting on it.

---

# The Apple-style cascade

The look that made this style spread: text that arrives per character or per
word, each unit rising, fading up and un-blurring, with the units overlapping so
heavily that it reads as one smooth wash rather than a stagger.

In After Effects it is a **Text Animator driven by a Range Selector offset**.
There is no equivalent primitive in CSS or GSAP, so it has to be translated -
and the translation is the useful part, because getting it wrong produces a
choppy stagger instead of a wash.

## The After Effects recipe it comes from

Consolidated from three tutorials, which agree on everything except one sign:

    Text layer, centred, 3-4 words maximum
    Font: SF Pro / SF Pro Display, semibold for display, tracking around -30
    Animate -> Position, Y = 100        (or -100 from above, X +/-100 from the side)
    Add -> Opacity = 0
    Add -> Property -> Blur = 10        (40 is far too much; 10 reads as depth)
    Range Selector -> Advanced
        Based On:  Words  or  Characters
        Shape:     Ramp Up
        Ease High: -50                  (one source says +50 - fit it, see below)
        Ease Low:  100
    Offset: keyframe -100 at the start, +100 at the end
    Ease the offset keyframes, and enable layer motion blur

**Words vs characters** is the biggest look decision. Words is calmer and suits
a spoken line; characters is more granular and mechanical.

**Duration comes from the read, not from a number.** Say the line out loud and
let that set the keyframe distance - roughly 2s for three words. Too tight and
it outruns both the voiceover and the eye.

## Translating the Range Selector to GSAP

A Range Selector is a window that sweeps across the text. For a unit at
normalised position `p` (index / count, 0 at the first unit, 1 at the last),
with the range spanning a fraction `R` of the text and offset `o`:

    selector s = clamp((p - start - o) / R, 0, 1)

The animator's values apply at `s = 1` and vanish at `s = 0`, so a unit is
fully hidden at `s = 1` and settled at `s = 0`. As `o` sweeps, each unit
transitions over an interval of width `R` in offset-space, and the sweep must
travel `1 + R` for every unit to finish.

That gives the mapping. For a total animation of duration `T` over `n` units:

    per-unit duration   = T * R / (1 + R)
    stagger, first-to-last = T * 1 / (1 + R)
    stagger between units  = T / ((1 + R) * (n - 1))

**The ratio of stagger-spread to per-unit duration is 1 : R.** That single
number is what separates this from an ordinary stagger: `R` near 1 means every
unit is in motion almost the whole time, which is the wash. A small `R` gives
discrete pops.

Measured off a real instance of the effect (an 11-character line at 60fps): the
sweep took ~20 frames while each unit took ~14, so `R` was about **0.7**, total
~0.57s. Start there and fit to your reference.

In GSAP:

    gsap.fromTo(units,
      { yPercent: 100, autoAlpha: 0, filter: "blur(10px)" },
      { yPercent: 0, autoAlpha: 1, filter: "blur(0px)",
        duration: T * R / (1 + R),
        stagger:  T / ((1 + R) * (units.length - 1)),
        ease: "power3.out" })

`Ease Low: 100` is why the arrival is so soft: it fully eases the approach to
`s = 0`, the settled state. That is a strong ease-out, so `power3.out` or
`expo.out`, not `power1`. Fit the actual curve from the reference with
`segment.mjs` rather than taking any of this on faith - the ease is the whole
character of the move.

## Do not confuse it with a mask reveal

This skill already teaches a masked word-rise (`overflow: hidden` on a wrapper,
`yPercent` on an inner span). The two look similar in thumbnails and are
completely different mechanics:

| | mask reveal | Apple cascade |
| --- | --- | --- |
| edge | hard clip on a straight line | none; the glyph is whole throughout |
| opacity | usually none | fades from 0 |
| blur | none | present, and it is the tell |
| units | usually per word | per character or per word |
| overlap | discrete stagger | heavy - the point of the effect |

Section 3.3 already says to read the edges. Here the specific test is: **does a
glyph ever appear cut by a straight line?** If yes it is masked. If it is whole
but soft and translucent as it moves, it is the cascade. `track.mjs` on a single
glyph settles it - a masked glyph's top edge is pinned to the mask while its
body moves; a cascading glyph's edges move together.

## The rest of the style

The cascade is the signature, but on its own it does not read as Apple. From
the same sources:

- **Palette.** White, black, or a very light grey ground. No loud or
  complementary colour. Accent sparingly.
- **Type.** SF Pro Display; bold for headings, regular or medium for
  subheadings. Tight tracking.
- **Space.** Generous. Nothing cramped, nothing accidental. The layout stays
  centred - off-balance layouts cost attention.
- **Restraint.** Subtle, smooth, quick. Nothing flashy or dramatic.

Polish that carries most of the "premium" feeling:

- **A very subtle vertical gradient on the text**, lighter at the top. It pairs
  with text rising from below, because the glyph darkens as it enters. Keep it
  almost imperceptible - if you can see it as a gradient, it is too strong.
- **Motion blur on**, always. It is the difference between clean and cheap.
- **Vary the entry direction** between lines (up, down, left, right) and swap
  text and background colours between sentences, with a shape layer wiping the
  change. Repeating one identical move for a whole film is what makes long text
  sequences boring.
- **Sound.** Smooth motion wants smooth sound. A cascade with a soft transient
  per line reads far more finished than a silent one.
- **Glass panels**, if the design needs surfaces: a blurred shape used as an
  adjustment layer, plus a duplicate with no fill and a white stroke at low
  opacity for the edge. It only works over something - on a flat ground a blur
  has nothing to blur.

---

# Liquid glass

Apple's post-WWDC-2025 surface: a panel that blurs and bends what is behind it,
with a bright hairline on its lit edges, a soft cast shadow, and a glint that
travels around its rim.

## What After Effects does, and what it maps to

The AE recipe is an adjustment layer carrying **CC Glass**, track-matted to a
rounded shape, with the shape as its bump map (softness 25, height 60,
displacement 100), lit by an **ambient AE light** at 200% - and CC Glass only
responds to AE lights if the shape layer is **3D**. Around it: a duplicate with
no fill and a 2px stroke at **overlay, 50%** for the rim; another duplicate
filled black, blurred ~40, offset down, at ~35% opacity, inverse-matted for the
shadow; and **CC Light Sweep** (shape smooth, width 100, sweep intensity 0, edge
intensity 60, edge thickness 3, light reception cutout) with its Direction
animated one full turn for the glint.

Every part of that has a CSS equivalent except one, and the exception matters.

## The CSS build (verified rendering)

    .glass {
      border-radius: 44px; overflow: hidden;
      /* blur behind, and lift its colour the way real glass does */
      backdrop-filter: blur(14px) saturate(1.55) brightness(1.06);
      /* a faint body tint, so it reads as a surface and not a hole */
      background: linear-gradient(150deg,
        rgba(255,255,255,0.16), rgba(255,255,255,0.05) 46%, rgba(255,255,255,0.11));
      /* the rim: bright hairline on the lit edge, softer elsewhere, plus cast */
      box-shadow:
        inset 0  1.5px 0 rgba(255,255,255,0.62),
        inset 0 -1.2px 0 rgba(255,255,255,0.20),
        inset  1.2px 0 0 rgba(255,255,255,0.20),
        inset -1.2px 0 0 rgba(255,255,255,0.20),
        0 26px 50px rgba(0,0,0,0.42);
    }

The travelling glint is a rotating conic gradient in an inset child at
`mix-blend-mode: overlay`, spun 0 -> 360 with a linear ease. That is CC Light
Sweep's Direction keyframe, exactly.

**The body tint is not optional.** Without it the panel reads as a hole cut in
the frame rather than a pane sitting on it, and no amount of edge work fixes
that.

**The rim is four separate inset shadows, not a border.** Real glass catches
light hardest on one edge. A uniform `border` reads as a sticker; a bright top
inset with dimmer sides is what sells it.

## Refraction: the part that does not map

`backdrop-filter` blurs but does not *bend*. The obvious CSS analogue of CC
Glass is an SVG `feDisplacementMap` fed by the panel's own blurred alpha:

    <feGaussianBlur in="SourceAlpha" stdDeviation="18" result="bump"/>
    <feDisplacementMap in="SourceGraphic" in2="bump" scale="26"
                       xChannelSelector="A" yChannelSelector="A"/>

**This does not work, and it is worth knowing why before you spend an hour on
it.** `feDisplacementMap` displaces by a channel's *value*, not by its gradient.
Feeding the same channel to both X and Y pushes every pixel the same diagonal
distance in proportion to alpha, so the panel slides bodily and grows a ghosted
double edge instead of bending light at its rim. Rendered side by side against a
plain panel, the plain one looks more like glass.

True refraction needs a **normal map**: an image where R encodes horizontal
displacement and G vertical, ramping steeply only near the edges, fed as
`xChannelSelector="R" yChannelSelector="G"`. Build that deliberately - as an
inline SVG gradient pair referenced through `feImage` - or skip refraction
entirely. On a busy background the blur, tint, rim and glint carry the look on
their own.

## Structure, from the same source

Two habits from the AE build that translate directly and are worth stealing:

- **Controllers, not per-element keyframes.** Group each cluster under a null
  (buttons, panel, whole device) and parent the nulls into a chain, so one
  scale keyframe on the outermost drives the entry for everything. In HTML that
  is nested wrapper divs, each animated as a unit - the same reason the
  reframing work in this skill needed a stage wrapper.
- **Offset sibling groups by ~3 frames.** Not per element, per *group*. It is
  what stops a UI assembling like a spreadsheet.
- **Property links.** In AE the stroke and shadow duplicates are pick-whipped to
  the main shape so size and roundness propagate. In CSS use one custom property
  (`--r` for radius, `--w` for width) read by all three layers, so a single
  change moves the panel, its rim and its shadow together.
