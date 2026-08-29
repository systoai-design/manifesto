---
name: motion-replicate
description: >
  Replicate a motion-graphics video (ad, kinetic typography, logo sting, title
  sequence, UI animation) from a video file or URL into a rendered HyperFrames
  composition that matches it frame-for-frame. Use whenever the user shares a
  video and asks to replicate, recreate, clone, copy, or "make this exact
  animation" — including Alight Motion / After Effects showcase videos, ad
  recreations, or any motion reference where the deliverable is a matching
  video (not a website — that's swipefile). Measures the reference numerically
  (per-frame pixel analysis, fitted easing curves, audio-onset cut detection)
  rather than eyeballing sampled frames, and scores convergence with SSIM.
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
colour that was off-white where the reference is pure white. Working project
with every technique: `D:\New Claude\motion-replicate\abe-ad` (read its
`index.html`, `FINDINGS.md`, and `STORYBOARD.md`).

## 0. Ground rules

- **Clone what you can't copy.** Unavailable font → nearest metric match
  (Helvetica → Arial on Windows; verify with §3.5, don't assume). Trademarked
  glyph → hand-drawn SVG. Soundtrack → extract the reference's own audio and
  mux it, and say plainly that this makes the result private/study-only.
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
plus any residual deltas honestly. State that the muxed reference audio makes
the artefact private/study-only.

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
Say so plainly in the findings: a kept bed is fine for an animatic or a pitch
and is not clearable for a paid run.
