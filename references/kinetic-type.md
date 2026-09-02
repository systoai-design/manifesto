# Kinetic typography craft, for the manifesto skill

Reference document for building kinetic-type pieces as HTML + GSAP under the HyperFrames contract: one paused timeline, every tween a `fromTo` with an explicit from-state, transforms and paint-only properties, deterministic, seek-safe. It builds on the local skills it cites rather than restating them, and every number carries a basis line. A basis of "inference" means the figure is this document's own reasoning and has not been measured or published anywhere; treat it as a starting value to fit, not a standard.

Written 2026-09-02. Where a web source could not be fetched directly (403, 429, blocked host) the citation says so and names the secondary source that was used instead.

## Contents

1. Sources consulted
2. Reading speed and hold time
3. Unit of animation: letter, word, line, block
4. Entrance vocabulary and its emotional register
5. Exits, and why they are faster
6. Hierarchy: scale, weight, one typeface
7. Text as mask and text as container
8. Sync: voiceover word timestamps and music beats
9. Amateur tells and the fix for each
10. Studio patterns: Buck, Ordinary Folk, Giant Ant, Gunner
11. What the existing HyperFrames text rules do not cover
12. Recipes for the gaps, under the contract
13. Verification checklist
14. Open questions

---

**Revision 2 (2026-09-02).** Corrected against a citation audit and a practitioner review.
One headline statistic about the measured reference was arithmetically impossible and is
recomputed; an author misattribution runs through three sections and is fixed; the cascade
overlap ratio was defined two incompatible ways; four recipes contained bugs that ship
visibly wrong (a yoyo that never returns, a synthetic-bold request, a knockout that cannot
fade, a clamp that reassigns emphasis at random). Every change is in `corrections.md` in
this directory.

## 1. Sources consulted

Local (read in full unless noted):

- `<skill>/SKILL.md` and `scripts/grade-original.py` (the measurement pipeline, the Apple cascade translation, the graded checks)
- `<skill>/library/INDEX.md` and `library/apple-business-essentials.md` (the one measured reference: 776 frames at 30 fps, 23 segments, 149.9 BPM)
- `<skills>/motion-design/director/disney-principles.md`, `director/choreography.md`, `reference/timing-easing-tables.md`, `reference/quality-checklist.md` (LottieFiles, MIT)
- `<skills>/hyperframes-animation/rules-index.md`, `techniques.md` (sections 4, 7, 8, 10, 12), `transitions/overview.md`, `adapters/animate-text.md`, `adapters/gsap-easing-and-stagger.md`, `blueprints-index.md`, and the rules `kinetic-beat-slam.md`, `waterfall-entry.md`, `gradient-text-sweep.md`, `hacker-flip-3d.md`, `chromatic-glitch.md`, `discrete-text-sequence.md`, `asr-keyword-glow.md`, `gsap-effects.md` (HeyGen, Apache-2.0)
- `<skills>/hyperframes-creative/references/motion-principles.md`, `beat-direction.md`, `video-composition.md`, `typography.md`

Web (fetched and read, unless marked):

- Netflix, English (USA) Timed Text Style Guide: https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-USA-Timed-Text-Style-Guide
- Netflix, Timed Text Style Guide: Subtitle Timing Guidelines: https://partnerhelp.netflixstudios.com/hc/en-us/articles/360051554394-Timed-Text-Style-Guide-Subtitle-Timing-Guidelines
- BBC Subtitle Guidelines. The primary host (bbc.co.uk and bbc.github.io) could not be fetched from this session; the figures below are taken from two secondary write-ups that quote the guideline text: https://www.clevercast.com/bbc-subtitling-guidelines/ and https://broadcastwriter.com/2024/12/12/bbc-subtitle-style-guide-2024/
- Closed Caption Creator, "Subtitle Reading Speed: CPS & WPM Limits Explained": https://www.closedcaptioncreator.com/blog/articles/subtitle-reading-speed.html
- legibility.info, "Rules for text in videos": https://legibility.info/rules-for-text-in-videos
- **Di Nocera, Ricciardi and Juola**, "Rapid serial visual presentation: degradation of inferential reading comprehension as a function of speed", Int. J. Human Factors and Ergonomics 5(4), 293, 2018. Abstract via search results and https://www.inderscienceonline.com/doi/abs/10.1504/IJHFE.2018.096118 (full text not fetched). **This document previously attributed the paper to "Benedetto et al." in three places; that is a different, earlier RSVP/Spritz study. The findings quoted (209 participants across six groups, no comprehension difference at 250, 300 and 350 wpm, significant decline at 400 and 450) are correct and belong to Di Nocera, Ricciardi and Juola.**
- **Primativo et al.**, "Perceptual and Cognitive Factors Imposing Speed Limits on Reading Rate: A Study with the Rapid Serial Visual Presentation", PLOS ONE 2016: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0153786 . (The earlier description of this as "Rubin and Turano region of work summarised in ..." was loose: Rubin and Turano 1992 is one of the works this paper cites and partially disputes, not its subject. Every figure drawn from it here is correct.)
- Virtual Speech, "Average Speaking Rate and Words per Minute" (quotes the National Center for Voice and Speech figure): https://virtualspeech.com/blog/average-speaking-rate-words-per-minute
- Lee, Jun, Forlizzi, Hudson, "Using Kinetic Typography to Convey Emotion in Text-Based Interpersonal Communication", DIS 2006: http://www.cs.cmu.edu/~joonhwan/documents/p41-lee.pdf (PDF fetched and text-extracted)
- Lee, Forlizzi, Hudson, "The Kinetic Typography Engine: An Extensible System for Animating Expressive Text", UIST 2002: https://www.cs.cmu.edu/~johnny/kt/dist/files/Kinetic_Typography.pdf (PDF fetched and text-extracted)
- Ford, Forlizzi, Ishizaki, "Kinetic Typography: Issues in Time-Based Presentation of Text", CHI 97 Extended Abstracts, pp. 269-270. Abstract page returned 429/403; cited here through the UIST 2002 paper's summary of it and the search-result abstract at https://www.semanticscholar.org/paper/Kinetic-typography:-issues-in-time-based-of-text-Ford-Forlizzi/2ad39695702e9885d04afcc5a9ec84b9482d05db
- NAB, "Television Safe Areas Redefined" (reproduces SMPTE EG 2046-3 extracts): https://www.nab.org/xert/scitech/pdfs/tv031510.pdf (PDF fetched and text-extracted)
- PremiumBeat, "Default Title Safe Guides Are a Sham": https://www.premiumbeat.com/blog/default-title-safe-guides-are-a-sham/
- Kreatli, "Safe Zone Hub 2026": https://kreatli.com/guides/safe-zone-guide
- Bitcut, "Beat Sync Video Editing": https://bitcut.app/blog/beat-sync-video-editing
- Beat2Cut, "Beat-Sync Video Editing: Complete Guide": https://beat2cut.com/blog/beat-sync-video-editing-complete-guide/
- WhisperX (Bain et al., INTERSPEECH 2023) via https://github.com/m-bain/whisperX . Rousso, Cohen, Keshet and Chodroff, "Tradition or Innovation: A Comparison of Modern ASR Methods for Forced Alignment", https://arxiv.org/pdf/2406.19363 (abstract only; **full text not read, and no tolerance figure from it is used in this document any more** -- see 8.2).
- CSS-Tricks, "CSS Techniques and Effects for Knockout Text": https://css-tricks.com/css-techniques-and-effects-for-knockout-text/
- SVGator, "What is kinetic typography? A guide to text in motion": https://www.svgator.com/blog/kinetic-typography-a-guide-to-text-in-motion/
- **Sources in the studio section that could not be traced, and are therefore no longer cited for a claim:** a Behance project page said to support Gunner's Google Home "modular visual system ... scaled across hundreds of devices" line and its Motion Award (no URL was ever given, so the claim is untraceable from this document); and a "Studio Ahremark case study" said to support Ordinary Folk's circle-and-geometric-shape identity (likewise no URL). Both claims have been softened in section 10.
- **Not checked in this revision, and therefore unverified rather than disproven:** the SVGator kinetic-typography guide; both Communication Arts features; the Mattrunks Giant Ant piece; STASH on the Dropbox logo system and the Gunner archive; the Gunner legacy site and Gunner School; the designyourway studio list; the Motionographer Metamorphosis interview (already flagged as search summary only). Four adjacent studio sources that were checked (Cartoon Brew on Metamorphosis, Motion Hatch 098, the Ordinary Folk about page, the School of Motion interview) all came back accurate.
- Studio profiles: Communication Arts on Buck (https://www.commarts.com/features/buck) and on Giant Ant (https://www.commarts.com/features/giant-ant); School of Motion podcast with Ordinary Folk (https://www.schoolofmotion.com/blog/ordinary-folk-interview); Ordinary Folk about page (https://www.ordinaryfolk.co/about); Mattrunks on Giant Ant (https://mattrunks.com/en/blog/studios/giant-ant-media-originality-fashions-and-customers); Motion Hatch podcast with Jay Grandin (https://motionhatch.com/098-how-giant-ant-became-a-leading-motion-design-studio-jay-grandin); Gunner legacy site (https://legacy.gunner.work/), Gunner School (https://www.gunner.school/our-story), STASH on Gunner's Dropbox system (https://www.stashmedia.tv/dropbox-logo-animation-system-by-gunner/) and Gunner archive (https://www.stashmedia.tv/tag/gunner/); Cartoon Brew on Metamorphosis (https://www.cartoonbrew.com/advertising/good-books-metamorphosis-by-buck-58953.html) and on the Duolingo acquisition (https://www.cartoonbrew.com/studios/duolingo-acquires-gunner-animation-studio-221889.html); Motionographer interview on Metamorphosis (https://motionographer.com/2012/03/26/interview-buck-good-books-metamorphosis/, search summary only); designyourway studio list (https://www.designyourway.net/blog/34-of-the-best-motion-graphics-studios-and-their-work/)

---

## 2. Reading speed and hold time

### 2.1 The published rates

These are the numbers a builder can defend. They come from caption and subtitle practice, from reading research, and from speech rate. None of them was written for kinetic type; section 2.3 says how to adapt them.

| Figure | Value | Source (basis) |
| --- | --- | --- |
| Conversational English speech | about 150 wpm (0.40 s per word) | National Center for Voice and Speech, quoted by Virtual Speech |
| Audiobook narration | 150-160 wpm | Virtual Speech and search summary of narration-rate articles |
| BBC recommended subtitle rate | 160-180 wpm, "0.33 to 0.375 second per word" | BBC guideline text as quoted by Clevercast and Broadcast Writer |
| BBC minimum display | "around 0.3 seconds per word (e.g. 1.2 seconds for a 4-word subtitle)" | same |
| BBC gap between subtitles when speech pauses | minimum 1 s, preferably 1.5 s | Broadcast Writer quoting the BBC text |
| BBC lag tolerance | subtitles should not anticipate speech by more than 1.5 s, nor hang more than 1.5 s after; never appear more than 2 s after the words | same |
| BBC broadcast line length | 37 fixed-width characters; online, 68% of frame width for 16:9, 90% for 9:16 | same |
| BBC subtitle size | line height 8% of active video height (16:9, 4:3, 1:1); 4.5% for 9:16 | same |
| Netflix reading speed | up to 20 characters per second (adult), 17 cps (children) | Netflix English (USA) TTSG |
| Netflix line limits | 42 characters per line, two lines, bottom-heavy pyramid when breaking | same |
| Netflix minimum duration | 20 frames (0.83 s), reserved for one- or two-word subtitles | Netflix Subtitle Timing Guidelines |
| Netflix maximum duration | 7 s | Closed Caption Creator summarising Netflix |
| Netflix frame gap | 2 frames minimum between subtitles **at every frame rate**; **in 24 fps content** a gap of 3-11 frames inclusive is closed to 2; otherwise 0.5 s or more | Netflix Subtitle Timing Guidelines. The 24 fps qualifier is in the source and was previously dropped here, which silently changed the rule's meaning: 3-11 frames is 125-458 ms at 24 fps but 100-367 ms at the 30 fps this document works at |
| Netflix audio sync | in-time within 1-2 frames of the first frame of audio; out-time at least 0.5 s past the audio end when nothing follows | same |
| Netflix shot changes | keep a 2-frame gap before a cut; snap in-time to the cut if dialogue starts within 0.5 s after it | same |
| Text in video, conservative | 13 characters per second minimum; a 30-character line needs 2.3 s; animated text must sit stationary "1 second for every 13 characters" | legibility.info |
| Text in video, size | 40-60 px body text at 1920x1080; titles at least 50% larger; 30 characters per line, 3 lines maximum | legibility.info |
| RSVP comprehension threshold | no comprehension loss at 250, 300, 350 wpm; significant decline at 400 and 450 wpm (209 participants) | Di Nocera, Ricciardi and Juola 2018, abstract |
| RSVP perceptual limits | eye-movement execution caps ordinary reading near 300 wpm (about 200 ms per word); unmasked decoding runs to about 1200 wpm; masking and memory bring it to 250-500 wpm | PLOS ONE 2016 |
| HyperFrames house rule | "3 seconds on screen = must be readable in 2. Fewer words, larger type." | `hyperframes-creative/references/typography.md` |
| Entrance to settle window used by the grader | settled window starts 0.35 s after the beat and ends at 62% of the beat's duration | `manifesto/scripts/grade-original.py`, the `settled` list |

Two conversions worth having in your head (basis: arithmetic on the rows above, assuming an average English word of about 5.7 characters including its trailing space; that average is an inference):

- Netflix 20 cps is roughly 3.5 words per second, about 210 wpm. It is the loosest professional caption rate.
- legibility.info 13 cps is roughly 2.3 words per second, about 137 wpm. It is the tightest, and it is written for on-screen graphics rather than dialogue captions.

### 2.2 What the measured reference does

The one reference measured to skeleton fidelity (Apple Business Essentials, `library/apple-business-essentials.md`) has 23 segments in 25.867 s. **Recomputed from the entry's own cut list: median 1.067 s, mean 1.073 s, max 2.4 s, min 0.1 s (3 frames).** The figures this document previously carried ("median 2.833 s, minimum 0.067 s") are arithmetically impossible: 25.867 s over 23 segments is a mean of 1.12 s, so a median of 2.833 s would require twelve segments totalling over 34 s inside a 25.9 s film. The library entry carries the same bad numbers and should be corrected there too. The cluster at frames 95, 98, 105, 113 is three cuts inside 18 frames. Those sub-reading cards are not reads; at 3-8 frames nothing can be read (basis: BBC 0.3 s per word minimum is 9 frames at 30 fps for one word). They function as rhythm, and the entry notes that "averaging it away produces a film that feels nothing like the reference". The lesson for hold time is that a professional piece runs two regimes, long readable holds and flash cards, and the grader enforces the contrast: `grade-original.py` fails a film whose beat lengths have a coefficient of variation below 0.18, on the stated grounds that "every beat is the same length: the cut reads as a metronome".

The reference also spends 67 of 776 frames on blank gaps across 10 runs, and the manifesto skill calls those gaps load-bearing. A hold model that fills every frame with type is wrong before it starts.

### 2.3 The hold model

Definitions. A card's on-screen life is: entrance (type in motion, not readable), settle (first frame where every glyph is at rest and at full contrast), hold (readable), exit (type in motion again), gap (blank frames before the next card). Only the hold counts toward reading time. legibility.info states this directly for animated text ("must remain stationary"), and `grade-original.py` measures contrast only inside the settled window for the same reason.

Three regimes, chosen per card (basis for the regime split: inference from the bimodal reference and from the difference between RSVP single-word reading and phrase reading):

**Read regime.** The viewer must take in the whole card as a phrase. Use the caption rates.

```
hold_read(words) = 0.33 s * words + 0.40 s        minimum 0.83 s
```

**Read this as a FLOOR to check against, not as a design target.** These are caption
accessibility minima, and used as targets they run roughly twice too slow for the one
piece this document holds up as professional: a 3-word read card needs 1.39 s of hold
under the model, and with a 0.45 s entrance and a 0.27 s exit the card is 2.11 s, longer
than 21 of the reference's 22 interior segments (recomputed: median 1.067 s, max 2.4 s).
In studio practice the causality runs the other way round: fix the beat grid and the board
first, then **cut the copy to fit the beat**. Copy is the free variable; timing is fixed.
A centred 3-word hero card at 150 px is one or two fixations, roughly 0.6-0.9 s of hold
(the fixation figure is this document's own PLOS ONE row, about 200 ms per fixation; the
0.6-0.9 s is inference).

Basis for the coefficients: 0.33 s per word is the BBC's own lower figure for 180 wpm; the
0.40 s reserve is **an untested inference** covering fixation onto the card, and it is
worth naming that it then propagates into `holdFor()`, into `schedule()`, into R1's VO
variant and into a proposed pass/fail grader check, which gives a guess the authority of
machinery; the 0.83 s floor is Netflix's minimum for a one- or two-word subtitle. Examples: 1 word 0.83 s, 3 words 1.39 s, 5 words 2.05 s, 8 words 3.04 s. The HyperFrames house rule ("readable in two-thirds of its screen time") is stricter than this for long lines; if the copy is above 6 words, apply it instead: on-screen total of 1.5 x hold_read.

**Beat regime.** One word at a time, each replacing or joining the last, driven by voice or music. The reader is not scanning, so RSVP rates apply.

**Split this regime in two, because the two halves have different floors.**

```
hold_beat_replace(word) >= 0.17 s   -- strict replace-in-place stream (true RSVP)
hold_beat_accumulate(word) >= 0.30-0.35 s  -- each word JOINS the last on screen
```

350 wpm is an RSVP figure and RSVP presents every word at one fixed point, so the eye never
moves. The beat regime as defined here also covers words that *join* the last, which is
spatial accumulation and costs a saccade plus a fixation per word; this document's own
PLOS ONE row already carries the right number for that case ("eye-movement execution caps
ordinary reading near 300 wpm, about 200 ms per word"), and 0.30-0.35 s allows for the
saccade on top. The earlier revision applied the 0.17 s RSVP floor to both. Target
0.25-0.33 s for the replace case.

Basis: 350 wpm is where Di Nocera, Ricciardi and Juola found comprehension still intact; 0.25-0.33 s is an inference sitting between the RSVP ceiling and the caption rate, and it is where the measured reference's per-word reveals live (the manifesto skill records per-word reveal frames per card; a 7-10 frame reveal at 30 fps is 0.23-0.33 s). The whole line must then be held, or re-shown, for hold_read at the end; a beat stream that cuts away on its last word is not readable as a sentence (inference).

**Flash regime.** 2-8 frames. Only for words already established earlier in the piece, or for pure rhythm hits (a colour flip, a single glyph). Never for new information. Basis: the reference's three-cuts-in-18-frames cluster; the "already established" restriction is an inference.

Adjustments:

- **Voice says the line.** Do not shorten the hold on the theory that the ear is doing the reading; instead end the hold no earlier than the last spoken word's end plus 0.5 s, which is Netflix's out-time rule. If the line is on screen before the voice reaches it, the hold is `max(hold_read, VO_end + 0.5 s) - settle`.
- **Words per line.** Cascading lines of 3-4 words at most. The "3-4 words maximum" figure comes from the AE tutorials the manifesto consolidates; **a consolidation of tutorials is not a source**, so treat it as received practice with no citation, not as a measured limit. Netflix does cap a caption line at 42 characters, and that part is sourced. Longer copy is split into lines and revealed per line (section 3).
- **Dense copy exception.** If a card carries more than about 30 characters on one line, use legibility.info's 13 cps as the hold instead of the word count, because character density, not word count, is what slows a reader on a long line (the 13 cps figure is theirs; using it as the switch-over is an inference).
- **Contrast and size below the floor.** Every rate above assumes legible type. A card under the size floor (section 9) or under 3:1 contrast (`grade-original.py` grades display type at the WCAG large-text ratio) needs longer, and the right fix is the size, not the hold.

### 2.4 Turning the model into a schedule

Frame-exact, authored in seconds, biased inward at clip boundaries as the manifesto skill requires:

```js
// Basis: hold model above; boundary bias from manifesto SKILL.md, "The frame-boundary trap".
const FPS = 30, F = 1 / FPS;
const wordsIn = s => s.trim().split(/\s+/).filter(Boolean).length;

// REGIME MUST BE DERIVED, NOT DECLARED. As an author-declared enum this is an attestation,
// not a measurement: a builder whose card fails simply relabels it and passes, which makes
// the central deliverable unfalsifiable. Derive it from the card list instead: a card is a
// READ card if it introduces a word not already shown anywhere earlier in the piece;
// everything else is beat or flash. Then the flash restriction ("only for words already
// established") becomes enforceable rather than honour-system.
function regimeOf(text, shownWords) {
  return text.toLowerCase().split(/\s+/).some(w => w && !shownWords.has(w)) ? "read" : "beat";
}

function holdFor(text, regime) {
  const w = wordsIn(text), c = text.replace(/\s+/g, "").length;
  if (regime === "flash") return 4 * F;                       // 2-8 frames, caller chooses
  if (regime === "beat")  return 0.28;                        // replace-in-place; 0.32+ if words accumulate
  let h = 0.33 * w + 0.40;                                   // read regime
  if (c > 30) h = Math.max(h, c / 13);                       // legibility.info density rule
  return Math.max(0.83, h);
}

// cards: [{ text, regime, enter, exit, gapAfter }] with enter/exit/gap in seconds
// returns absolute times on the frame grid; the settle is where the hold starts
function schedule(cards, t0 = 0) {
  let t = t0;
  return cards.map(card => {
    const start   = Math.round(t / F) * F;
    const settle  = start + card.enter;
    const hold    = holdFor(card.text, card.regime);
    const exitAt  = Math.round((settle + hold) / F) * F;
    const end     = exitAt + card.exit;
    // DEFAULT 0, NOT 3. The reference spends 67 blank frames in 10 runs, of which the
    // 37-frame cold open is one, leaving about 30 frames across 9 interior gaps in a
    // 22-cut edit: roughly 60% of its cuts are HARD CUTS with no gap at all, and the gaps
    // that exist are placed, not distributed. A gap after every card is exactly the
    // metronome the CV check is trying to catch, one level up. Place gaps deliberately at
    // structural boundaries. (Measured from the library entry's gap counts.)
    t = end + (card.gapAfter ?? 0);
    return { ...card, start, settle, hold, exitAt, end,
             clipStart: start - 0.0002,
             clipDur: (Math.round((end - start) / F) / FPS) - 0.0011 };
  });
}
```

Use `clipStart` and `clipDur` for the `.clip` `data-start` / `data-duration` attributes and the plain values for tween positions. The two bias constants are the manifesto's, from a build where 11 of 29 clips started a frame late.

---

## 3. Unit of animation: letter, word, line, block

The unit that moves should be the unit of meaning being emphasised. That is the one-line rule; everything below is consequences. (Basis: inference, but it agrees with the UIST 2002 paper's observation that RSVP-style presentation "allow[s] words to be treated independently without regard to effects on adjacent text elements", and with the manifesto's note that "Words vs characters is the biggest look decision.")

| Unit | Reads as | Right for | Wrong for | Budget constraint |
| --- | --- | --- | --- | --- |
| Whole block | one gesture; calm, premium, or a stamp | statements the viewer already expects; end cards; anything under 3 words that must land as one | copy over ~8 words (a block that long reads as a slide) | none beyond the entrance duration |
| Per line | reading order made visible; editorial | copy of 2-4 lines; quotes; lists | single-line hero words | line stagger x lines <= 0.5 s (rules-index contract) |
| Per word | speech rhythm; the voice's cadence | spoken lines; taglines; anything synced to VO timestamps | long paragraphs (per-word on 20 words is 20 events, which is noise) | word stagger x words <= 0.5 s unless timed to VO, where the transcript is the schedule |
| Per character | mechanical, granular, typed, decoded, or "wash" when heavily overlapped | one hero word up to about 12 characters; typewriter; decode; the Apple cascade | body copy; any line the viewer must read as a phrase, because the word shape is assembled last | character stagger x characters <= 0.5 s; use the cascade overlap ratio (section 12, R3) to stay inside it on longer words |

Why per-character reading costs more: a word is recognised by its shape and its first and last letters as much as by its middle, and a per-character build withholds the shape until the last unit lands (basis: inference from the RSVP literature's emphasis on whole-word decoding; not measured here). The hold clock therefore starts at the last character's settle, not the first.

The stagger budget is the contract's, stated in `hyperframes-animation/rules-index.md` ("items x stagger <= ~0.5s") and in the LottieFiles timing tables ("Total stagger MUST stay <500ms"). It is a budget for one arrival to read as one beat; a VO-timed line is not one arrival, it is a sequence of arrivals, and the transcript overrides it.

The external `animate-text` catalogue (see `adapters/animate-text.md`) sorts its 24 effects into exactly these four buckets: 7 per-character, 8 per-word, 2 per-line, 7 whole-element. Its implementation files are not vendored into HyperFrames for licensing reasons; use its IDs as vocabulary in a storyboard and implement from the recipes here.

Mixing units inside one card is the usual professional move, not an exception: the hero word per-character or as a block, the supporting line per-word or per-line, arriving later and smaller (section 6).

---

## 4. Entrance vocabulary and its emotional register

### 4.1 What the research says motion means

The CMU line of work is the only published mapping from kinetic-type properties to perceived meaning, so it anchors the register column below.

- Ford, Forlizzi and Ishizaki (CHI 97) identified three things kinetic typography does well: expression of emotional content, creation of characters, and capture or direction of attention (as summarised in Lee, Forlizzi, Hudson, UIST 2002).
- The UIST 2002 paper maps tone of voice to motion: "large upward or downward motions can convey rising or falling pitch"; loudness "can be mimicked by changing the size of text, as well as its weight, and occasionally contrast or color"; "for high volumes, motions mimicking vibration can be used", and persistence after the utterance mimics reverberation; tempo maps directly to timing and pacing; a temporally stretched word can be shown by spatial stretching. It also names analogous motion: small vibrations read as trembling (high arousal: anticipation, excitement, anger); a shrinking, decelerating motion reads as slumped shoulders (disappointment); slow rhythmic motion reads as breathing and induces empathy.
- The same paper's caution: kinetic typography "cannot normally replace or override strong emotive content intrinsic to the meaning of the text"; it reinforces or tempers. Do not expect a slam to make a soft line hard.
- It also states the attention rule: "perceptual phenomena that have sudden onset tend to induce attentional capture", moving objects draw the eye, and motion along a path pulls the eye to the end point. And the pitfall: kinetic type can "demand too much attention", so avoid sudden onsets where capture is not wanted.
- Lee, Jun, Forlizzi and Hudson (DIS 2006) had three designers build 24 effects for happy, joyous, angry and sad on the neutral sentence "I am fine", then had 66 people rate them on mood and energy. Ratings were consistent across designers (F(3,195)=125.8 for mood, 322.1 for energy, p<0.0001). Angry rated highest energy (5.45 of 7), sad lowest (2.58); angry and sad rated lowest mood (3.22, 2.59), happy and joyous highest (4.85, 5.03). The takeaway for a builder: energy is the most reliably communicated axis, and it is carried by speed, amplitude and vibration; mood is carried by direction, ease and settle.

The HyperFrames easing adapter puts the same idea in tool terms: "Easings are tone of voice", `.out` for entrances, `.in` for exits, `power3.out` as the house settle, overshoot as a rare playful register. And `motion-principles.md`: "The transition is the verb. The easing is the adverb."

### 4.2 The vocabulary

Each row: mechanic, what it says, the ease family that fits, where it already exists in the local skills, and the tell that gives an amateur version away. Durations are the entrance only, settle excluded, and every one is a range to fit against the piece's tempo. Where a duration has a named source it is given; otherwise it is an inference calibrated to the LottieFiles tables (dramatic reveal 600-1200 ms, card enter 200-350 ms) and to the beat-slam rule (0.35-0.6 s on the hit).

| Entrance | Mechanic | Register | Ease | Duration | Exists in | Tell |
| --- | --- | --- | --- | --- | --- | --- |
| Mask reveal (rise through a clip) | wrapper `overflow:hidden`, inner `yPercent` 60-110 to 0 | editorial, assured, "typeset"; the straight clip edge reads as print | `power3.out`, `expo.out` | 0.35-0.6 s per unit (inference) | manifesto §6 technique map; `animate-text` `mask-reveal-up` (external) | descenders clipped by a tight mask; a fade added on top, which kills the print read |
| Rise (free translate + fade) | `y` 30-80 px to 0 with `autoAlpha` 0 to 1 | soft, calm, conversational; the web default | `power2.out` to `power3.out` | 0.3-0.5 s | `techniques.md` §4 (uses `tl.from`; use `fromTo`) | used on every element (`motion-principles.md` names `y: 30, opacity: 0` as the default to stop reaching for) |
| Slam / stamp | `scale` 1.3-1.6 to 1, `filter: blur(16px)` to 0, `autoAlpha` 0 to 1 | loud, percussive, assertive; size is loudness (UIST 2002) | `power4.out` | 0.35-0.6 s (`kinetic-beat-slam.md`) | `kinetic-beat-slam.md` p1 | one slam per line for the whole piece; `back.out` on a slam, which turns a stamp into a cartoon |
| Side snap | `x` -320 to 0 (or +) with `autoAlpha` | urgent, whip, "next" | `expo.out` | 0.3-0.45 s (`kinetic-beat-slam.md` p2) | `kinetic-beat-slam.md` p2 | entering from a different side each line with no reason; `choreography.md` calls mixed directions chaos |
| Waterfall (binary whip from below) | `tl.set` opacity 1 + `y` offset, then whip to 0; overlapping | energetic, headline, sports/promo | `power4.out` | 0.10-0.20 s per word, weighted by size | `waterfall-entry.md` | fading the arrival (the rule bans it), or queuing instead of overlapping |
| Tracking-in (letters converge) | per-letter `x` from an index-derived spread to 0, plus fade | luxury, cinematic, title-sequence; slow inhale | `expo.out` for arrival, `power1.out` for the fade | 0.8-1.4 s (inference; LottieFiles "dramatic reveal" 600-1200 ms) | none under the contract (`letter-spacing` tweens reflow); recipe R4 | tweening `letter-spacing` and letting the line re-centre every frame; kerning pairs lost when glyphs are split without compensation |
| Tracking-out exit | reverse of the above | dissolve of attention, "let go" | `power2.in` | 0.4-0.7 s | recipe R4 | same as above |
| Weight / variable-axis | `--wght` 200 to 900 via `font-variation-settings` | growing loudness, conviction; a whisper becoming a statement | `power2.out` or `sine.inOut` for a breathe | 0.4-0.8 s (inference) | `techniques.md` §8 (no reflow guard) | the line reflowing as the word widens; requesting a weight the embedded font does not have (`typography.md`: only listed weights exist) |
| Blur-resolve | `filter: blur(10-30px)` to 0, `autoAlpha` 0 to 1, small `scale` 1.04 to 1 or none | dreamy, memory, arrival from depth; the Apple register when combined with rise | `power3.out` | 0.4-0.7 s; the manifesto's product-UI measurement shows the blur resolving faster than the move, so give blur its own shorter tween | `techniques.md` §10 exit/entry pair; `depth-of-field-blur.md`; manifesto Apple cascade | blur specified in absolute pixels. **Express it as a fraction of type size**: about 0.04-0.08 em reads as defocus and above roughly 0.15 em reads as a rendering fault. Ten pixels against 340 px type is a whisper; ten pixels against a 30 px eyebrow erases it, and this document quotes the same "10 not 40" figure at 140 px, 150 px and 340 px. Second, unmentioned and real: any non-`none` `filter` value, `blur(0px)` included, forces the element off the subpixel-antialiasing path in Chromium, so a piece where some cards blur-resolve and others do not renders its type at two visibly different apparent weights. Apply `filter: blur(0px)` to every type element in the piece, or to none |
| Typewriter | per-character `autoAlpha` set, binary, 0.02 s | mechanical, human-typed, terminal; suspense at low cps | `steps(1)` / `tl.set` | 3-5 cps dramatic, 8-12 natural, 15-20 tech (`gsap-effects.md` timing guide) | `techniques.md` §7; `discrete-text-sequence.md`; `gsap-effects.md` | per-character fades instead of binary; a CSS `@keyframes` cursor blink, which desyncs from seek |
| Cascade (Apple) | per-unit `yPercent` 100 to 0, `autoAlpha` 0 to 1, `blur(10px)` to 0, heavily overlapped | premium, quiet confidence, one smooth wash | `power3.out` / `expo.out` (Ease Low 100 in AE terms) | about 0.57 s total for 11 characters. **R = 0.7 is the ratio of per-unit duration to stagger sweep, NOT the per-unit share of the total**: with R = 0.7 the per-unit duration is R/(1+R) = about 0.41 of the total, which is the 14 frames of the measured 34. (manifesto, measured at 60 fps; the earlier wording here contradicted R3's own algebra two sections later, and a builder copying it would author a per-unit tween roughly 70% too long) | manifesto "The Apple-style cascade" (math, no rule) | a discrete stagger that reads as a choppy queue: overlap ratio R too small |
| Pop (spring) | `scale` 0 to 1 | playful, friendly, UI-ish | `back.out(1.7)` or a baked spring at damping 0.6-0.7 | 0.4-0.6 s | `spring-pop-entrance.md`, `gsap-easing-and-stagger.md` spring section | used in a serious register; the adapter calls overshoot "a rare, explicitly-playful register, never the house style" |
| Flip / decode | per-character `rotateX` 90 to 0 with glyph substitution | tech, decrypt, flap display | `power3.out` | 0.4-1.0 s per character with 0.03-0.08 s stagger | `hacker-flip-3d.md` | no `perspective` on the ancestor (renders as a 2D squash) |
| Glitch stretch | `scaleX` 1.3-1.8 to 1 with RGB-split copies jittering on quantised time | tense, digital, disruptive | `power4.out` | 0.25-0.6 s | `chromatic-glitch.md` | interpolated (not quantised) jitter that reads as jelly; a glitch that outlives the hold |
| Wipe / clip window | `clip-path: inset(...)` tween on the wrapper, or content sliding through a static clip | editorial, precise, "revealed by a rule" | `power3.inOut` for a moving edge | 0.4-0.7 s | `techniques.md` §12 | wiping every card the same direction |
| Gradient sweep on a held line | `backgroundPosition` through `background-clip:text` | light passing over type; a hold that stays alive | `none` | 1.2-3 s | `gradient-text-sweep.md` | an eased sweep, which reads as an object rather than light (the rule's own constraint) |
| Counter / roll | numeric proxy with `Math.round`, `tabular-nums` | data, proof | `power2.out`, overshoot and settle if measured | 0.6-1.5 s | `counting-dynamic-scale.md`; manifesto product-UI notes | a single linear ramp where the reference overshoots |

**Read this table as a set of ingredients, not a set of choices.** One signal per card is
precisely the flat-but-competent tell section 9 names and the earlier revision then built:
every recipe applied exactly one mechanic per card. The measured reference **stacks**
signals -- mass (reveal, wipe, type-on) on 19 of 23 segments, width on 19, height on 17,
centroid x on 14, with the entry stating outright that nearly every card both reveals and
scales, most also drift horizontally, and almost nothing enters by opacity alone. Use
**2-4 concurrent signals on a hero card**, all driven from one proxy so they cannot drift
apart. (Library entry mechanics table.)

**On variety, the summary line this document used to carry was backwards for short-form.**
"At least three distinct entrance mechanisms and at least three distinct eases across a
piece" is a reasonable floor for a two-minute explainer and wrong for a 15-30 second piece,
which reads as authored when it has **one dominant mechanic varied in amplitude and
timing** and reads as a demo reel when it has five. The measured reference is one compound
mechanic reused across 23 cards. Restate: one dominant mechanic per piece, at most two
accent mechanics reserved for the cards that carry structure, and ease variation within one
family rather than across three. The beat-slam rule's own phrasing that this document
quotes approvingly -- reuse the ease family, vary the axis -- already says exactly this.
(`kinetic-beat-slam.md`; `video-composition.md`; library entry mechanics table; the
short-form restatement is inference.)

**A device this table has no row for, and should:** the **full-frame ground inversion**.
The reference carries its punctuation in the ground, not in the type: 19 segments on black,
4 on white, and the entry names the white cards as the punctuation. A ground flip costs one
paint-only property, is perfectly seek-safe, and gives a piece a structural read that no
amount of entrance variety will. Pick two grounds, put the inversion on the structural
beats (roughly one card in five), and hold the type mechanic constant across the flip so
the ground carries the change. (Library entry background counts.)

**And no row here mentions motion blur, which is the loudest single difference between an
AE render and a browser capture.** The fastest mechanics in this table are exactly the ones
that need it: the waterfall at 0.10-0.20 s per word, the slam's opening frames, R4's
tracking-in where the outer glyph of a 7-letter word covers about 300 px, and R7's push.
Positive rule: **any element whose per-frame travel exceeds about 1.5% of frame width
(roughly 29 px at 1920) needs a shutter pass or a directional-blur substitute.** Note that
CSS `filter: blur()` is isotropic and is therefore NOT the substitute; the two forms that
work under the contract are stacked ghost copies offset along the travel axis at decaying
opacity, and an SVG `feGaussianBlur` with an axis-weighted `stdDeviation` driven from the
same proxy as the transform. (The library entry for this reference records "Motion blur
present and tested, not assumed"; the 1.5% threshold is inference.)

### 4.3 Matching entrance to the word

The word itself picks the mechanic when the line is short. `beat-direction.md` lists the verbs: impact (slams, stamps, drops), directional (slides, wipes, cuts), reveals (draws, fills, grows), organic (floats, breathes), mechanical (types, clicks, locks in). A line about speed snaps; a line about patience rises through a mask over a full second. A line about breaking something glitches. Naming the verb before choosing the tween is the practice, and `beat-direction.md` is explicit that "if you can't name the verb, the element is not yet designed".

---

## 5. Exits, and why they are faster

### 5.1 The ratio

Every timing source agrees exits are shorter than entrances, and they agree on roughly how much:

| Source | Statement |
| --- | --- |
| LottieFiles `timing-easing-tables.md` | "Entrance = base (100%). Exit = 65-75% of entrance." |
| LottieFiles `disney-principles.md` | "Enter-exit asymmetry: entrances 30-50% longer than exits." |
| `motion-principles.md` | "A card takes 0.4s to appear but 0.25s to disappear." |
| `kinetic-beat-slam.md` | "exits <= 0.25s" against 0.35-0.6 s entrances |
| `transitions/overview.md` | exits at 0.5 s with `power3.in` paired with 0.5 s `power3.out` entries in the seam example |

Working value: **exit = 0.65-0.70 x entrance**, ease `.in`. (The earlier revision said 0.6 and called it "the midpoint of the ranges above". It is not: the five cited ranges give 0.70, 0.67-0.77, 0.625 and 1.0, whose midpoint is about 0.70, and 0.6 is below every LottieFiles figure -- it is only reachable by averaging in the beat-slam rule's 0.25 s exit against a 0.6 s entrance. The ease direction is stated in all of them and in the easing adapter.)

**And this ratio should not be a pass/fail check at all.** The dominant exit in this medium
is a hard cut, which is ratio zero, and the Buck transitional-continuity pattern section 10
praises is a morph out that carries into the next card and is legitimately *longer* than
the entrance. A ratio gate rejects both. Scope it: "a card that exits by **animating in
place** uses about 0.7 x its entrance on a `.in` ease", with cuts and transitional exits
exempted by name in the storyboard. (Arithmetic on the five cited ranges; the exemption
argument is from this document's own sections 5.3 and 10.)

### 5.2 Why

Three reasons, the first two from the sources, the third an inference:

1. **The reading is done.** Once the hold has elapsed the type carries no more information; every frame it lingers is a frame the next idea is not on screen. The BBC's rule that a subtitle must not "hang up on the screen for more than 1.5 seconds after speech has stopped" is the caption-world form of this.
2. **Attention is captured on onset, not on departure.** The UIST 2002 paper's attention rule is about sudden onsets. An exit does not need to be noticed, only cleared; an ease-in leaves slowly and accelerates away so most of its motion is over in its last few frames, which is what makes a short exit still read as a motion rather than a cut.
3. **The gap is part of the exit.** The measured reference cuts through 1-8 blank frames between cards. A fast exit plus a short gap is how a piece breathes without slowing; a slow exit plus no gap is how it drags.

### 5.3 Exit vocabulary

| Exit | Mechanic | Pairs with | Notes |
| --- | --- | --- | --- |
| Hard cut into a blank gap | `tl.set(autoAlpha: 0)` on the exit frame, 1-8 blank frames, next card | any percussive entrance | The dominant exit in the measured reference; the manifesto's cut model is "cards cut through blank frames". Zero cost, and it is the one people forget exists. |
| Drop through the mask | reverse of the mask reveal, `yPercent` 0 to -110 (up) or +110 (down) | mask reveal | Up if the next line rises, so the motion reads as one column passing a window. |
| Blur-out-up | `y` 0 to -150, `blur` 0 to 30 px, `autoAlpha` to 0, 0.33 s `power2.in` | any; the velocity-matched seam | Exact values from `techniques.md` §10 and `beat-direction.md`. |
| Scale-down fade | `scale` 1 to 0.92, `autoAlpha` to 0, 0.2-0.3 s | slam, pop | `scale-swap-transition.md` shrinks and fades the outgoing cluster. |
| Tracking-out | letters diverge, fade | tracking-in | The letters leave the way they came; R4. |
| Glitch tear | one burst envelope 0.12-0.2 s then `tl.set` hidden | glitch, tech register | `chromatic-glitch.md` emphasis burst, ending in a kill. |
| Zoom-through | wrapper `scale` 1 to 30-40 on `expo.in`, hard cut at the frame the interior fills the frame | text as container | Manifesto technique map: "slam zoom: wrapper scale, origin at the measured target glyph, hard cut at peak". |
| Slide-aside | `x` to a new rest position while the next element enters the vacated centre | a hero that must stay visible | `nudge-curve.md` and the `video-text-pivot` blueprint. |

Two contract notes that every exit needs:

- **Hard-kill after the fade.** `motion-principles.md`: a faded inner element "may need a deterministic zero-duration `tl.set()` kill after its fade, because a later tween or sibling `immediateRender` can resurrect it." Pair every exit tween with `tl.set(el, { autoAlpha: 0 }, exitEnd)`.
- **Give fade-out-only elements a baseline.** Manifesto §6, the render-order trap: an element whose only tweens are fade-outs with `immediateRender: false` can render blank when the worker seeks past and back. `tl.set(el, { autoAlpha: 1 }, cardStart)` first.

And a scope note. `transitions/overview.md` bans exit animations in multi-scene montages ("The transition IS the exit") except on the final scene. That rule governs seams between HyperFrames scenes. A continuous typography piece built the way the manifesto prescribes (one monolithic composition, one `.clip` per card, one timeline with absolute-time `fromTo`s) owns its exits inside the monolith; the ban does not apply there, and the blank-gap cut is not a transition in the montage sense. State which model the composition uses in `STORYBOARD.md` so a reviewer does not flag the exits as violations.

---

## 6. Hierarchy: scale, weight, one typeface

### 6.1 The rules the skills already state

- One expressive face per scene; "one performs, one recedes" (`typography.md`).
- Weight contrast must be extreme: "Video needs 300 vs 900" (`typography.md`).
- Sizes for video, not web: headlines 64-120 px full-screen, body 28-42 px, labels 18-24 px (`video-composition.md`); in-feed, headlines 90 px and up, body 32 px and up (`typography.md`).
- Hero text fills 60-80% of frame width (`video-composition.md`, `motion-principles.md`).
- Tracking tighter than web, -0.03 to -0.05 em at display sizes, because encoding compresses letter detail (`typography.md`); the beat-slam rule uses -0.03 em at 150 px.
- On dark grounds light type reads heavier and tighter; use 350 instead of 400 for body and add 0.01 em tracking at display sizes (`typography.md`).
- Time is hierarchy: "The first element to appear is the most important" (`typography.md`), "The element that moves first is perceived as most important" (`motion-principles.md`).
- The grader requires at least three distinct sizes in the timeline (`grade-original.py`, TYPE check).

### 6.2 Ratios (inference, calibrated to the size tables)

Adjacent levels need a visible jump in motion, at feed size, after compression. A 1.25 ratio that works on a page disappears in a 6-second card. Working ratios:

| Level | Size relative to hero | Weight | Enters |
| --- | --- | --- | --- |
| Hero word or line | 1.0 (fills 60-80% width) | 800-900 | first |
| Supporting line | 0.40-0.55 | 400-500 | 100-200 ms after the hero settles |
| Label / eyebrow / metadata | 0.18-0.25, tracked +0.08 to +0.14 em, caps | 500-700 | with the support, or last |

Basis: the video-composition table gives headline 64-120 against body 28-42 (ratio 0.35-0.44) and labels 18-24 (0.19-0.28); the ratios above are those ranges widened slightly for a hero that is deliberately oversized. The 100-200 ms lag is the LottieFiles secondary-action figure ("timing: 50-100ms after primary") and follow-through figure ("Child delay: 50-150ms") stretched for video.

A disagreement to be aware of: `disney-principles.md` (a UI adaptation) says "Hero enters 100-200ms after supporting elements", while `typography.md` and `motion-principles.md` say the hero moves first. For UI the context lands then the hero arrives into it; for kinetic type the hero is the context. Follow the typography rule for type.

### 6.3 Contrast inside one face

`typography.md` lists the ways to get contrast without a second face: one variable changed (weight, optical size, width), proportional against monospaced, one font at two weights. For kinetic type add the temporal axis: the hero arrives with the piece's loudest mechanic and the support with its quietest. The same line said twice with the same face and the same size, once slammed and once faded, is two different sentences (the paper's tone-of-voice mapping and `typography.md`'s "Motion is typography" both say so).

Legibility floor for the smallest level (basis: legibility.info's 40-60 px body at 1080p, the BBC's 8% of frame height for subtitle line height, and `typography.md`'s 20 px minimum full-screen / 32 px in-feed): nothing under 32 px at 1080p in a piece that will be seen in a feed, nothing under 24 px anywhere, and justify anything under 40 px in writing.

---

## 7. Text as mask and text as container

Two distinct moves that share a mechanism:

- **Type revealing footage.** The letters are a window; footage plays inside them; the ground around them is solid. Often the letters then grow until one letter's interior fills the frame and the footage is simply there.
- **Type as container.** The letters are a window; other type or graphics scroll, slide or count inside them; the letters themselves stay still.

### 7.1 Mechanisms

CSS-Tricks lists three: `background-clip: text` (a gradient or image inside glyphs, but it cannot take a video and leaves "little space for other effects like blur, or moving text"), `mix-blend-mode` knockouts (four modes work: multiply, screen, darken, lighten), and an SVG `<mask>` with a `<text>` element (masks by luminance; the article notes historical browser gaps and that transforms cannot be applied to the mask itself, only to the masked element). The HyperFrames gradient-sweep rule already uses the first for gradients. For footage the other two are the tools.

**Blend knockout** (simplest, works today in the capture browser because it is ordinary compositing):

- A full-frame layer painted solid black with white text, set to `mix-blend-mode: multiply`, over a `<video>`. Black times anything is black; white times the video is the video. Footage shows only through the letters.
- Invert for a white ground: white layer, black text, `mix-blend-mode: screen`.
- The blend layer's ancestor needs `isolation: isolate` so the blend does not reach through to the composition background.
- The text is ordinary DOM, so it can be scaled, translated and staggered per word with transforms, and each of those is a paint-only or transform change under the contract. The video is framework-owned (`techniques.md` §6: muted, playsinline, never call `play()`).
- Limitation: the ground must be pure black or pure white. A brand-coloured ground needs the SVG mask.

**SVG mask** (any ground colour, any shape):

- `<mask maskUnits="userSpaceOnUse">` containing a black rect and white `<text>`, applied to the footage wrapper via `mask: url(#id)` (with `-webkit-mask`). The wrapper sits over a coloured ground.
- Scaling the masked wrapper scales the letters and the footage together: the camera pushes into the letter. To keep the footage still while the letters grow, put the video in a child and counter-scale it, `child.scale = 1 / wrapper.scale`, both driven from one proxy so they cannot drift (the counter-transform pattern from `anchored-layout-expand.md` and `viewport-change.md`).
- The text inside an SVG mask is an SVG `<text>`, not HTML; it uses the same embedded `@font-face` but wraps and kerns as SVG text does. Measure the settled bbox, do not assume it matches the HTML twin.

### 7.2 The signature moves

**Reveal by zoom-through.** The footage sits in the word; the word scales toward the camera with `expo.in` until one counter or bowl fills the frame; hard cut to the bare footage at the frame the interior first fills the frame. Manifesto technique map: "slam zoom: wrapper scale, origin at the measured target glyph, hard cut at peak". Choose the origin on a glyph with a large interior (O, D, a bowl), and set `transform-origin` there in pixels, not percentages, so it is stable across sizes. Do not blur it: hard-masked fast moves look blurred in a sampled frame while being crisp (manifesto §3.4), and adding blur makes the replica less accurate; if the fast move strobes, use the per-card shutter from the manifesto's frame-rate section instead.

**Container scroll.** Hold the letters; slide the content inside them (a wall of words, a colour, a number) with `y` or `x` on the masked child. The window is the constant, the content is the variable; this is the `fixed-anchor-cycle` blueprint's logic applied inside glyphs.

**Type over footage without a mask.** Sometimes the right move is not a knockout but contrast: solid type over darkened footage. `video-composition.md`'s three-layer rule and the grader's 3:1 large-text contrast check apply; darken the footage with a paint-only overlay rather than a filter on the video.

Cost warning: a `<video>` under a blend or mask is the heaviest thing a composition can do in the capture browser. `techniques.md` reserves GPU-captured HTML for "1-3 hero beats per video"; the same restraint applies here, and the render must be verified frame by frame (the `hyperframes-render-discipline` skill's capture-through-a-sink habit), never the preview.

---

## 8. Sync: voiceover word timestamps and music beats

### 8.1 Two clocks

A kinetic piece with a voice and a bed has two clocks. Voice timestamps say when a word is said; the music grid says where the pulse is. They do not agree, and the manifesto's finding is that a professional piece keeps them separate: on the measured reference the manifesto skill reports "12 of 23 cuts were locked to onsets within 0-2 frames". **Recomputed against the entry's own 149.9 BPM and 12.008 frames per beat, the figure is 11 of 23 within 2 frames, 9 of them early**; twelve cuts sit 3-6 frames off the grid. The anticipation finding survives and is the useful part; the count and the implied degree of lock do not. The entry's own note is that the cuts "sit close to the grid but are not quantised to it", with slight anticipation that is "part of why it feels driven rather than mechanical".

Working rule (basis: inference from the above and from the two beat-sync guides): cuts and structural hits belong to the music; word arrivals belong to the voice; when a word must hit both, move the voice, not the beat. The manifesto's per-line generation pipeline exists for exactly this: "render each line at nine speeds, keep the take that fits its window".

### 8.2 Word timestamps

Getting them:

- `hyperframes transcribe` produces word-level `{ word, start, end }` (referenced by `asr-keyword-glow.md` and the `hyperframes-cli` skill).
- The manifesto's `vo-transcribe.py` runs faster-whisper at word resolution over the isolated vocal stem and prints a frame number per word.
- WhisperX refines Whisper's utterance-level timestamps with a wav2vec2 phoneme-alignment pass (Bain et al., INTERSPEECH 2023). What is actually supported: **wav2vec2 cannot timestamp digits or spoken symbols** -- words with no characters in the alignment model's dictionary, for example "2014." or "£13.60", get no timing at all (WhisperX README, verified). Two other claims this document previously made here have been withdrawn. (1) "The alignment literature commonly evaluates at a tolerance above 200 ms" is in neither the WhisperX README nor the arXiv 2406.19363 abstract, and forced-alignment evaluation is conventionally reported at much tighter thresholds (10/25/50/100 ms), so the figure is probably wrong as well as unsourced. (2) "WhisperX degrades on noisy audio" is plausible and uncited. **Unsupported, and removed as a basis for anything below.** The practical conclusion still holds on other grounds (see the manifesto's own finding that Whisper's boundaries lag soft attacks by a third of a second): a transcript timestamp is a hint good to a few frames on clean speech, not a frame-exact truth.

Verifying them: the manifesto is blunt that Whisper's "boundaries lag soft attacks by a third of a second", and its `vo-verify.py` finds each line's actual energy onset in the assembled track. Use the energy onset as the word's time when the two disagree.

Placing type against them (basis: Netflix in-time rule of 1-2 frames from the audio, out-time of 0.5 s past the audio; BBC anticipation limit of 1.5 s; the settle-locked reasoning is an inference from the UIST 2002 attention rule):

- **The settle lands on the onset, not the start of the tween.** A word that starts moving as it is spoken is still moving when the ear has finished it. Start the entrance early by the time the ease takes to reach 90% of its travel (table in R9). For binary arrivals (waterfall, typewriter, hard cut) the start is the onset.
- **Never later than the word.** Reading a word after hearing it reads as a caption; reading it as it is heard reads as the voice made visible. Netflix's 1-2 frame in-time tolerance is the right target.
- **Lead by no more than a beat.** Words arriving well before they are spoken split attention. The BBC's 1.5 s anticipation ceiling is far too loose for kinetic type; keep the lead under the entrance duration (inference).
- **Hold after the last word.** The line stays at least 0.5 s after the last word's end (Netflix out-time), and at least the read-regime hold measured from the line's completion if the line is new information.
- **Faster than the entrance.** When two words are closer together than the entrance duration, shorten the entrance to fit rather than letting words pile up mid-travel; **a per-word entrance longer than twice the gap to the previous word reads as a queue -- an unsupported rule, and the clamp it produced is worse than the problem.** There is no source and no measurement behind the 2x figure, and R8 implemented it as a hard clamp on DURATION, which changes the mechanic mid-line: on R8's own onsets it yields 0.35, 0.35, 0.12, 0.35, 0.30, so two words arrive with a visibly different entrance from their neighbours purely because the speaker ran them together, and section 4.1 says duration and amplitude carry energy, so a transcript accident is now assigning emphasis at random. **Clamp the start times, not the durations**: hold the entrance constant and let closely spaced words overlap in flight, which is what a waterfall does by design and what this document already endorses. (R8 has been corrected.)

### 8.3 Music beats

Getting the grid: the manifesto's `audio-beats.mjs` reports onsets and how many cuts land within 3 frames of one; `bed-tempo-fit.py` least-squares fits BPM and phase to a cut list; the measured reference gave "149.9 BPM, offset 0.0, 12.008 frames per beat at 30fps".

Placing against it:

- **Anticipate by 1 frame at 30 fps, not 2.** Both beat-sync guides say 1-2 frames and give the same reason. Bitcut: "place your cut 1-2 frames before the beat. This creates a sense of anticipation: the viewer sees the new shot and then hears the beat". Beat2Cut: "Visual processing takes time. Cutting 1-2 frames early feels more 'on the beat'." But 2 frames at 30 fps is 67 ms of video lead, past the detectability threshold for video ahead of audio (ITU-R BT.1359 relative-timing tolerances put video-ahead detection at about 45 ms); 1 frame is 33 ms and sits inside it. Use 1 frame at 30 fps and 1 frame at 24 fps (42 ms, already at the limit), and reserve 2 frames for 48 or 60 fps timelines. The measured reference's slight anticipation is the same finding in data.
- **Not every beat.** Bitcut: "Not every beat needs a cut". Beat2Cut makes the same point in its own words -- "Not every beat needs a cut. Too many cuts... feel amateur despite effort" and "Cut on downbeats, let other beats pass". (The sentence this document previously put in quotation marks and attributed to Beat2Cut, "Cutting on every beat feels frantic. Choose downbeats for major cuts", is not on the page; the substance is fully supported, the quotation marks were not.) The grader's beat-length variation check is the enforcement.
- **Impact frame per mechanic.** A slam's impact is its first frame (sudden onset); a rise's impact is its settle. Lock the impact frame to the anticipated beat, and back-compute the start (R9).
- **Chrome that keeps the beat** is optional and cheap: `kinetic-beat-slam.md`'s metronome ticks read the same `BEATS` array as the phrases.

### 8.4 Sound design

A cut with no sound reads unfinished. Manifesto, Sound section: "match the sound's character to the motion's. Smooth animation wants soft, low-transient sound; hard cuts want sharp ones", and the cut list from `segment.mjs` "is already the edit decision list to place them against". Every mask rise, slam and glitch in this document has a natural transient; budget for them.

---

## 9. Amateur tells and the fix for each

| Tell | Why it reads amateur | Fix | Basis |
| --- | --- | --- | --- |
| Every word has the same entrance | "the flat-but-competent tell"; no hierarchy, no tone of voice | vary the axis per phrase, reuse the ease family; 3+ mechanics and 3+ eases per piece | `kinetic-beat-slam.md`, `video-composition.md`, `motion-principles.md` guardrails |
| No hold; the next word arrives while the last is still being read | nothing is readable; the piece is motion, not typography | hold model in section 2.3; hold only counts settled frames | BBC 0.3 s/word, Netflix 0.83 s minimum, legibility.info stationary rule |
| Every card the same length | "the cut reads as a metronome" | vary by content; flash cards against held cards; CV of beat lengths >= 0.18 | `grade-original.py`; measured reference's bimodal pacing |
| Centred and floating | a web layout pattern; one focal point; nothing for the eye to travel to | anchor to edges, two focal points, three layers; vertical spread sd >= 0.09 and <= 85% of frames in the middle third | `video-composition.md`, `motion-principles.md`, `grade-original.py` COMPOSITION checks |
| Ease-in entrances | "sluggish"; the type arrives reluctantly and settles nowhere | `.out` for entrances, `.in` for exits, `.inOut` for moves | `motion-principles.md`, `disney-principles.md` #6, `timing-easing-tables.md` |
| Linear motion on type | no weight, no settle | never linear for spatial movement; linear only for gradient sweeps, rotation, progress | `disney-principles.md` #6 ("NEVER linear for spatial movement"), `gradient-text-sweep.md` |
| PowerPoint bounce | overshoot as emphasis; reads cheap in any serious register | overshoot budget 0% premium (sourced); **0-5% corporate is this document's own inference, not a source row** -- `timing-easing-tables.md`'s overshoot table has Success 5-10%, Error 0%, Feedback 2-5%, Celebration 15-25%, Premium 0%, and no Corporate row at all ("Corporate" appears only in a separate duration-by-personality table). `back`/`elastic` only in an explicitly playful piece; prefer a critically damped spring | `timing-easing-tables.md` overshoot budget (Premium row), `disney-principles.md` #10, `gsap-easing-and-stagger.md`; corporate figure: inference |
| Text too small for video | web sizes vanish at feed scale and after compression | headlines 64-120 px (90+ in-feed), body 28-42 (32+ in-feed), nothing under 24 px; hero fills 60-80% width; BBC line height 8% of frame height as a caption floor | `video-composition.md`, `typography.md`, legibility.info, BBC |
| Type in the unsafe margin | covered by platform UI (there is no overscan in any delivery path this document targets) | **4-5% margins for web and streaming, which is what the grader's existing 4% edge check already enforces**; 10% title-safe only when the brief names a broadcast deliverable. Ninety-percent title-safe exists because CRT overscan cropped the frame; applied to a web or social piece it discards 10% of the frame and fights this document's own rule to anchor to edges rather than centre. (This document cites PremiumBeat's "Default Title Safe Guides Are a Sham" and then followed the default anyway.) For vertical social, use the asymmetric platform bands rather than any symmetric box: Kreatli's conservative margins: Reels 108 px top, 320 px bottom, 60 px sides; TikTok 130/250/60; Shorts central 4:5; the grader flags any ink inside 4% of an edge | NAB summary of SMPTE ST 2046-1; PremiumBeat; Kreatli; `grade-original.py` |
| Fading arrivals on a whip | the fade fights the snap | binary 0 to 1 via `tl.set` on a waterfall; fades belong to soft entrances only | `waterfall-entry.md` |
| Everything starts at t=0 | "feels like a jump cut" | offset the first tween 0.1-0.3 s; the measured reference opens on a 37-frame blank | `motion-principles.md`; `library/apple-business-essentials.md` |
| Mixed entry directions inside one cascade | "Mixed directions = chaos" | one direction per cascade; change direction between sentences, not inside one | `choreography.md`, `waterfall-entry.md`, manifesto "Vary the entry direction between lines" |
| Text moving **fast** while it is being read | a word with angular velocity cannot be read; reading time starts at settle | separate entrance from hold. **The blanket ban on ambient drift is too absolute and is contradicted by this document's own reference**, which measures horizontal centroid movement on 14 of 23 segments and vertical on 8. What breaks reading is angular velocity, not motion as such: a push or drift under roughly 0.3% of frame width per frame (about 6 px per frame at 1920) reads as camera rather than as type in motion and keeps a long hold alive, and that slow push is the Apple idiom this document is otherwise trying to reproduce. Ban anything above it | legibility.info stationary rule; `grade-original.py` settled window; library entry centroid counts; the velocity threshold is inference |
| Too many moving elements | the eye is pulled in several directions | max one third of elements active at once; no unbroken travel over one third of the frame | `choreography.md` 1/3 rules; SVGator legibility notes |
| Stagger that never ends | an arrival of 20 letters at 50 ms is a second of nothing landing | items x stagger <= 0.5 s; on long words use the cascade's overlap ratio, not a longer stagger | rules-index contract; `timing-easing-tables.md`; manifesto cascade math |
| Descenders clipped by a mask | the "y" loses its tail on the way in | pad the mask box and pull it back with negative margin (R2) | inference; standard fix |
| Kerning lost when letters are split into spans | display type at negative tracking shows gaps at pairs like "AV", "To" | split words when kerning pairs are visible; when splitting letters, keep the tracking-in move short or accept the loss on a face with even fitting | inference; `typography.md` tracking note |
| `letter-spacing` tweened for tracking-in | layout reflows every frame; the line re-centres | per-letter `x` transforms converging (R4) | rules-index contract (transforms and paint-only) |
| Variable weight tweened on a flowing line | the whole line reflows as the word widens | ghost twin at the heaviest weight reserves the box; live copy centred in it (R5) | `hacker-flip-3d.md` ghost pattern; inference |
| CSS `transition` or `@keyframes` on type | interpolates on the wall clock; flickers and desyncs under seek | every motion on the timeline; blink via `steps(1)` yoyo or a sin square wave | rules-index contract; `chromatic-glitch.md`; `discrete-text-sequence.md` |
| `gsap.from()` inside a clip | writes the from-state at construction; elements flash or skip entrances under non-linear seek | `fromTo` with explicit from-state; `immediateRender: false` when re-owning a property | `motion-principles.md` load-bearing rules; manifesto lint traps |
| Blur out of scale with the type | reads as a rendering fault, not depth | 0.04-0.08 em (about 10 px at 150 px type, about 24 px at 340 px type); blur resolves on its own faster tween; and apply `filter: blur(0px)` to every type element or to none, so antialiasing mode is uniform across the piece | manifesto Apple cascade (AE sources) and product-UI defocus measurement; the em restatement and the antialiasing note are inference |
| One card, one signal | the flat-but-competent tell: the piece is a slideshow with better easing | 2-4 concurrent signals on a hero card, all from one proxy; and a ground inversion on the structural beats | library entry mechanics and background counts (section 4.2) |
| No motion blur on the fast frames | the single loudest difference between an AE render and a browser capture | shutter pass or ghost/feGaussianBlur substitute on any element travelling more than about 1.5% of frame width per frame | manifesto frame-rate section; library entry ("Motion blur present and tested, not assumed") |
| A break that falls where the box wraps it | the break sets the stagger structure, so an accidental break is an accidental rhythm | set every line break by hand per card. Break on syntactic units; never between an article and its noun, never after a preposition, never orphan a one-word last line unless that orphan is the payoff | Netflix TTSG bottom-heavy-pyramid rule (quoted in 2.1 and previously never applied); standard typesetting practice |
| A face chosen after the motion | kinetic type needs specific things from a face and most faces do not have them | choose the face first, on: even fitting (so per-glyph splitting does not open visible gaps), large closed counters if a zoom-through is planned, a real variable weight axis if weight is the mechanic, generous round-glyph overshoot so masked reveals are not flat-topped, and an embedding licence covering rendered video. Record the chosen face's cap height and descender depth in the storyboard, because R2's mask geometry depends on both | inference; two of this document's own recipes fail on the first and third criteria |
| Only a sound-on cut exists | most feed viewing is muted, and a muted piece carries the whole message in the type | spec both cuts, or spec the silent cut as the master and let the voice ride under timing that already works without it. A card comfortable at 0.8 s with narration needs closer to 1.4 s without | inference, consistent with the in-feed delivery targets this document assumes elsewhere |
| Every card enters, holds and exits alone | a piece assembled from independent enter-hold-exit cards is a slideshow with better easing, which is the structural version of the flat tell | add at least one continuity move: the outgoing element's rest transform becomes the incoming element's from-state, so motion is continuous across the boundary and the cut lands mid-move rather than into a gap. That also relieves the hold model, since a card that hands off does not need to resolve | this document's own section 10 (Buck: transitional continuity) and its own `schedule()` structure |
| Decorative chrome around the hero word | "the flip is the beat"; timestamp lines and status dots dilute it | none, or one big secondary label in the same stack | `hacker-flip-3d.md` critical constraints |
| Silent cuts | "reads unfinished even when the picture is right" | a transient per cut, matched to the motion's character | manifesto Sound section |
| Exit as slow as the entrance | drags; the next idea is late | exit about 0.6 x entrance, `.in`, then a 1-8 frame gap | section 5 |

---

## 10. Studio patterns: Buck, Ordinary Folk, Giant Ant, Gunner

A caution first, and it applies to every line below. None of these studios has been measured with the manifesto pipeline, and none publishes timing numbers. What follows is drawn from interviews, profiles and project write-ups, so it describes tendencies a viewer can recognise, not values a builder can copy. **Every "borrow" line is an inference and is written in the imperative only for readability; none of them is a prescription and none should be read as one, because they sit next to sourced rules elsewhere in this document and will otherwise be mistaken for them.** When a specific piece is the reference, measure it (manifesto §3) and record it in the library; that is the only way a studio pattern becomes a number.

### Buck

What the sources say: "style-agnostic", building a coherent visual world per brief rather than imposing one look (designyourway; Communication Arts). Communication Arts describes warmth and humanity in work for tech clients, "a wink of humor", cross-functional "unicorns" who flex across roles, and practical lo-fi set building; Ryan Honey: "We take our work seriously, but we don't take ourselves too seriously." On the typographic side, Good Books "Metamorphosis" (String Theory, 2012, D&AD 2013) is described by Cartoon Brew as "a relentless visual onslaught" of "transitional animation" mixing cel, 2D, 3D and stop-motion, where the aim was that the piece "would, like Thompson's prose, somehow seamlessly hold together". Search summaries also attribute "The Girl Effect" and Childline "First Steps" (with YCN) to Buck as typography-led pieces.

Recognisable pattern: transitional continuity. One thing becomes the next; there is rarely a plain cut. Type is an object in a world with physical rules, not a caption over one. Restraint is in the pacing and the design system, not in the amount of motion.

Borrow (inference): a morph chain between cards (the manifesto's "phrase morph" technique and the `logo-assemble-lockup` blueprint's "morphed in one unbroken chain out of the preceding phrase"); one consistent physical logic for how type moves in the piece; humour in the timing (a held beat, a late arrival) rather than in the graphics.

### Ordinary Folk

What the sources say: founded 2019 in Vancouver by Jorge R. Canedo Estrada after Buck (animator) and Giant Ant (animator, then associate creative director); ten people across six countries (about page). The School of Motion interview describes "complex, polished animation with meticulous attention to detail", intricate gradients, masking and layered elements, deliberate stylistic flexibility through outside designers, camera mockups first "to understand timing", building "from the biggest to the most important elements", frame-by-frame quality through transitions rather than only at key poses, and a 10-15 s shot taking about a week. The about page speaks of care "from everyday communications to nuanced animation curves". Search-result summaries describe the work as geometric, cinematic, refined and restrained, "closer to short film than marketing asset", with personal projects "where the music drives the design and animation". **(A claim about their own site identity being built on circles and geometric shapes was previously attributed to a "Studio Ahremark case study, via search"; that source is absent from the source list and carries no URL, so the claim has been removed.)**

Recognisable pattern: audio-driven, camera-first, geometry-led. Motion is composed to the track, the virtual camera is planned before the elements are, and the easing curves are the craft.

Borrow (inference): fit the tempo grid before any tween exists (manifesto `bed-tempo-fit.py`; R9); treat the camera as the first element (the `viewport-change` and `multi-phase-camera` rules); spend the budget on the curve of the hero move and on the in-between frames of every transition, not on the number of elements.

### Giant Ant

What the sources say: Vancouver, founded by Jay Grandin and Leah Nelson; "elegant styling, crisp visuals and imaginative storytelling" (Communication Arts); "lineless" flat-shape animation, "quirky perspectives, and smart writing", and "the ability to do so much with so little" (Motion Array, via search); Mattrunks singles out their typography with voice: "the text/voice combo remains one of the most effective ways to visually reinforce a message". Grandin: "if there is no real story, there's no soul" (Communication Arts), "everything is a statement of our taste", and "it doesn't take any more time to do a great job than a mediocre job" (Motion Hatch). Nelson: "the best idea always wins".

Recognisable pattern: writing first, voice-led type, sparse frames that do a lot, warmth without noise. The type serves the read; it does not compete with it.

Borrow (inference): write the line before designing it; sync per-word to the read (R8) and keep the mechanic quiet enough that the words, not the moves, are what the viewer remembers; use the hold model generously; one accent colour.

### Gunner

What the sources say: Detroit, "an illustration and animation studio" whose artists "obsess over creating imagery that hypnotizes and stirs a little feeling in our guts" (legacy site); clients Google, Dropbox, Spotify, Lyft, Amazon, Herman Miller, Fender; acquired by Duolingo in 2021, the name continuing as a tuition-free school (Cartoon Brew, Gunner School). The Google Home onboarding animations are described as a modular visual system scaled across many devices and shipped in code with Lottie. **(The earlier revision quoted a specific "scaled across hundreds of devices" line and a Motion Award and attributed both to "the Behance project page, via fetch"; no Behance URL appears anywhere in this document's source list, so the claim is untraceable and is now stated without quotation or award.)** The Dropbox logo system's stated aim: "each animation be unique to the product's function but as a whole feel familial within Dropbox's ecosystem" (STASH). STASH's archive shows character-driven narrative films (Squarespace "Clyde" Frazier, Duolingo World) and cel credits on several projects.

Recognisable pattern: illustration-first, character-led, motion designed as a system that ships in product. Typography in Gunner's work is generally a supporting element to illustration rather than the subject, on the evidence available here.

Borrow (inference): systems thinking. Define the piece's few motion primitives once, name them, and reuse them so that every card feels familial while doing a different job (the beat-slam rule's "reuse the ease family, vary the axis" is the same idea); give type a physical character (weight, bounce budget, squash) that matches the illustration language it sits with.

---

## 11. What the existing HyperFrames text rules do not cover

Read against the six named text rules (`kinetic-beat-slam`, `waterfall-entry`, `gradient-text-sweep`, `hacker-flip-3d`, `chromatic-glitch`, `discrete-text-sequence`) and `techniques.md` sections 4, 7 and 8, a professional kinetic-type piece still needs the following. Each gap names the recipe in section 12 that fills it.

1. **A hold-time model.** No rule derives dwell from word count or character count. `kinetic-beat-slam` fixes BEATS spacing at 1.2-1.8 s independent of what the phrases say; `discrete-text-sequence` and `asr-keyword-glow` ask for a 1 s climax dwell, which is a floor, not a model. Recipe R1.
2. **A mask reveal for words and lines.** `techniques.md` §12 slides a whole block through a static clip window; `waterfall-entry` is a free whip, not a masked rise; the masked per-word rise lives only in the manifesto's technique map and in the external `animate-text` catalogue, which is not vendored. Recipe R2.
3. **The heavily overlapped cascade.** The manifesto has the Range Selector translation and the measured R of about 0.7, but no HyperFrames rule expresses "stagger-spread to per-unit duration is 1 : R", and the contract's 0.5 s stagger cap is easy to trip on a per-character wash without it. Recipe R3.
4. **Tracking-in and tracking-out that respect the no-layout-tween contract.** `motion-principles.md` suggests letter-spacing as a variation but a `letter-spacing` tween reflows the line every frame. Recipe R4.
5. **Variable-weight entrances with a reflow guard.** `techniques.md` §8 tweens `--wght` and `--opsz` on a wordmark, which is fine alone on a line; on a flowing line the advance widths change and neighbours move. No weight-as-loudness guidance either. Recipe R5.
6. **Impact-frame timing.** `kinetic-beat-slam` starts its tweens on the beat. For a rise or a cascade the perceived landing is the settle, which arrives 0.3-0.7 of the duration later; nothing computes that back-offset, and nothing applies the 1-2 frame anticipation both beat-sync sources describe. Recipe R9.
7. **A VO-word-onset arrival rule.** `asr-keyword-glow` highlights words already on screen; `techniques.md` §4 makes words arrive on transcript times but uses `tl.from` (a contract violation inside a clip, per `motion-principles.md`), a fixed 0.35 s duration regardless of word spacing, no clamp when words are closer than the entrance, and no hold after the last word. Recipe R8.
8. **An exit vocabulary for type.** `transitions/overview.md` bans in-scene exits in montages, `kinetic-beat-slam` says "exits <= 0.25s" and shows none, and `waterfall-entry` is arrival only. A continuous type piece owns its exits and needs them written. Recipe R10.
9. **Text as mask over footage and the zoom-through.** `gradient-text-sweep` clips gradients into glyphs; nothing clips video, and the manifesto's "slam zoom, hard cut at peak" has no rule. Recipe R7.
10. **Hierarchy stacks.** The typography reference gives sizes and weight contrast but no rule composes a hero line with a supporting line that arrives later and smaller with a staged entrance. Recipe R11.
11. **Blank-gap rhythm.** The measured reference spends 67 frames in 10 blank runs and the manifesto calls them load-bearing; no rule schedules gaps. R1's `schedule()` carries `gapAfter`.
12. **A contract-clean typewriter.** `techniques.md` §7 is fine (finite yoyo cursor, `tl.call` per character); `gsap-effects.md`'s cursor uses a CSS `@keyframes` blink, which `chromatic-glitch` and `gradient-text-sweep` both identify as a seek-safety violation. R12 states the clean form briefly and defers to `discrete-text-sequence`.
13. **Size and safe-zone checks for type.** `typography.md` has the sizes and `grade-original.py` has a 4% edge check; no rule ties platform safe zones (9:16 top and bottom bands) to type placement. Covered in section 9 and the checklist.

---

## 12. Recipes for the gaps, under the contract

All recipes assume: `tl` is the single paused timeline registered on `window.__timelines`; `F = 1/FPS`; every tween is `fromTo`; `immediateRender: false` on any tween that re-owns a property already tweened earlier on the same element; no CSS `transition` on animated elements; index-derived values only; finite repeats. DOM measurement, where used, happens at build time and only in a single-scene composition (rules-index contract).

### R1. Hold-time calculator and card schedule

Given in section 2.4 (`holdFor`, `schedule`). Two additions:

```js
// VO-aware hold: never cut before the line has been heard plus Netflix's 0.5 s out-time.
function holdWithVO(text, regime, settleAt, voEndAt) {
  const h = holdFor(text, regime);
  return Math.max(h, (voEndAt + 0.5) - settleAt);
}

// House rule check (typography.md): a card must be readable in two-thirds of its screen time.
function readableInTwoThirds(card) {
  return card.hold >= (2 / 3) * (card.end - card.start);
}
```

Basis: section 2.3. `readableInTwoThirds` is a check, not a target; short percussive cards fail it by design and are declared as beat or flash regime instead.

### R2. Mask reveal, per word or per line, with its exit

```html
<p class="line" id="l1">
  <span class="m"><span class="w">Notice</span></span>
  <span class="m"><span class="w">more.</span></span>
</p>
```

```css
/* Archivo Black ships as a SINGLE STYLE at CSS weight 400. Requesting 900 triggers
   synthetic emboldening, which at 140 px smears the outline and thickens strokes unevenly,
   and synthetic bold is itself a classic amateur tell. Either set it at 400 and take
   contrast from size and colour, or use a family that actually ships the axis. This is the
   failure typography.md warns about: only listed weights exist. */
.line { font: 400 140px/1.05 "Archivo Black", sans-serif; letter-spacing: -0.03em; color: #f5f5f5; }
.m {                       /* the window */
  display: inline-block; overflow: hidden; vertical-align: bottom;
  /* Room for descenders and ascender overshoot. THESE ARE NOT CONSTANTS: descender depth
     and overshoot are per-face metrics, so 0.18em clips a face with a deep descender and
     wastes mask height on one without. Measure the chosen face's metrics and set them per
     project (see the face-selection row in section 9). */
  padding: 0.06em 0.05em 0.18em; margin: -0.06em -0.05em -0.18em;
}
.w { display: inline-block; will-change: transform; }
```

```js
// Basis: manifesto technique map ("mask span + inner yPercent -> 0; measure the true start offset,
// often ~60% not 110%"); stagger cap from rules-index; exit ratio from section 5.
const FROM = 110;                 // fit to the reference: 60-110
const words = gsap.utils.toArray("#l1 .w");
const n = words.length;
const enterDur = 0.45, step = Math.min(0.09, 0.5 / Math.max(1, n - 1));   // items x stagger <= 0.5 s
const t0 = 0.2;
words.forEach((w, i) => {
  tl.fromTo(w, { yPercent: FROM }, { yPercent: 0, duration: enterDur, ease: "power3.out" }, t0 + i * step);
});
const settle = t0 + (n - 1) * step + enterDur;
const hold   = holdFor("Notice more.", "read");
const exitAt = Math.round((settle + hold) / F) * F;
const exitDur = 0.6 * enterDur, exitStep = step * 0.5;
words.forEach((w, i) => {
  tl.fromTo(w, { yPercent: 0 }, { yPercent: -FROM, duration: exitDur, ease: "power3.in", immediateRender: false }, exitAt + i * exitStep);
});
tl.set(words, { autoAlpha: 0 }, exitAt + (n - 1) * exitStep + exitDur);   // hard-kill after the fade
```

Per-line variant: one `.m` per line, `.w` is the whole line, `step` 0.12-0.18 s. Direction: rise for arrivals, drop up through the mask for exits when the next line also rises, so the two read as one column passing the window. Do not add opacity to the entrance; the straight clip edge is the point (section 4.2). Verify with the manifesto's `track.mjs`: a masked glyph shows "bottom fixed, top rising".

### R3. The Apple cascade (heavy overlap)

```js
// Basis: manifesto "Translating the Range Selector to GSAP". R = 0.7 measured on an 11-character line
// at 60 fps (sweep ~20 frames, per-unit ~14 frames). T comes from the read: ~2 s for three words.
function cascade(units, T, R, at, opts = {}) {
  const n = units.length;
  const per = T * R / (1 + R);
  const stagger = n > 1 ? T / ((1 + R) * (n - 1)) : 0;
  tl.fromTo(units,
    { yPercent: opts.from ?? 100, autoAlpha: 0, filter: "blur(10px)" },
    { yPercent: 0, autoAlpha: 1, filter: "blur(0px)", duration: per, stagger, ease: opts.ease ?? "power3.out" },
    at);
  return { settle: at + T };      // the last unit settles at at + T by construction
}
```

Units are `display:inline-block` spans per character (mechanical, granular) or per word (calmer, spoken lines); the manifesto calls this "the biggest look decision". Keep 3-4 words per line. **The stagger budget is NOT satisfied automatically**, contrary to what this document previously claimed: the sweep is `T / (1 + R)`, which at the `T = 2 s for three words` this document's own comment recommends gives 1.18 s, well past the 0.5 s cap. It only fits at short T (T = 0.6 s and R = 0.7 gives 0.35 s). Check it explicitly. Blur at 0.04-0.08 em of the type size, not a fixed pixel figure. The glyph must never be cut by a straight line; if it is, you built R2, not this (the manifesto's distinguishing test).

### R4. Tracking-in and tracking-out, transform-only

```html
<h1 class="track" id="t1" aria-label="ARRIVAL">
  <span>A</span><span>R</span><span>R</span><span>I</span><span>V</span><span>A</span><span>L</span>
</h1>
```

```css
.track { font: 700 180px/1 "Oswald", sans-serif; letter-spacing: 0.04em; color: #fff; white-space: nowrap; }
.track span { display: inline-block; will-change: transform, opacity; }
```

```js
// Basis: contract (transforms and paint only; letter-spacing reflows). Spread is index-derived and
// symmetric about the centre so the word's centroid does not move. Duration from LottieFiles
// "dramatic reveal" 600-1200 ms; ease pairing from the easing adapter.
const letters = gsap.utils.toArray("#t1 span");
const n = letters.length, mid = (n - 1) / 2;
const em = parseFloat(getComputedStyle(letters[0]).fontSize);   // build-time measurement, single-scene only
const SPREAD = 0.55 * em;                                       // px of extra advance per letter at the start
const at = 0.3, dur = 1.1;
letters.forEach((el, i) => {
  tl.fromTo(el, { x: (i - mid) * SPREAD, autoAlpha: 0 },
                { x: 0, autoAlpha: 1, duration: dur, ease: "expo.out" }, at);
});
// exit: letters part and thin out, faster, ease-in
const exitAt = at + dur + holdFor("ARRIVAL", "read");
letters.forEach((el, i) => {
  tl.fromTo(el, { x: 0, autoAlpha: 1 },
                { x: (i - mid) * SPREAD * 0.6, autoAlpha: 0, duration: 0.5, ease: "power2.in", immediateRender: false }, exitAt);
});
tl.set(letters, { autoAlpha: 0 }, exitAt + 0.5);
```

Opacity and position on one tween is acceptable here because neither overshoots; if you switch to a spring with damping under 1, split opacity onto its own `power2.out` tween at the same position (easing adapter). Kerning: splitting into spans drops pair kerning; on a face with visible pairs, apply a per-pair correction as `margin-left` in em on the second span at build time, or use words as units.

### R5. Weight-axis entrance with a reflow guard

```html
<span class="wslot">
  <span class="wghost" aria-hidden="true">LOUDER</span>
  <span class="wlive" id="w1">LOUDER</span>
</span>
```

```css
@font-face { font-family: "BrandVar"; src: url("../capture/assets/fonts/Brand-Variable.woff2") format("woff2"); font-weight: 100 900; font-display: block; }
.wslot  { display: inline-grid; font-family: "BrandVar", sans-serif; font-size: 160px; line-height: 1; }
.wghost, .wlive { grid-area: 1 / 1; justify-self: center; white-space: nowrap; }
.wghost { visibility: hidden; font-variation-settings: "wght" 900; }        /* widest state reserves the box */
.wlive  { --wght: 200; font-variation-settings: "wght" var(--wght); }
```

```js
// Basis: techniques.md §8 (custom-property tween); ghost-reserves-width from hacker-flip-3d;
// weight-as-loudness from Lee, Forlizzi, Hudson 2002. Embed the variable font yourself: the bundled
// families ship fixed weights only (typography.md).
tl.fromTo("#w1", { "--wght": 200, autoAlpha: 0 }, { "--wght": 900, autoAlpha: 1, duration: 0.6, ease: "power2.out" }, 0.4);
// optional breathe on the hold, finite: weight 900 -> 820 -> 900, one cycle per 1.6 s
const holdDur = holdFor("LOUDER", "read"), cycle = 1.6;
// BUG, guarded here. With this recipe's own inputs the old expression evaluated to ZERO:
// holdFor("LOUDER","read") is 0.83 s, floor(0.83 / 1.6) is 0, and 0 * 2 - 1 clamps to 0.
// A yoyo tween with repeat 0 NEVER RETURNS, so the word would end the piece at weight 820
// and any later tween assuming 900 starts from the wrong state. A 1.6 s cycle also cannot
// fit inside a 0.83 s hold at all. Skip the breathe when no whole cycle fits.
const cycles = Math.floor(holdDur / cycle);
if (cycles >= 1) {
  tl.fromTo("#w1", { "--wght": 900 }, { "--wght": 820, duration: cycle / 2, ease: "sine.inOut", yoyo: true,
    repeat: cycles * 2 - 1, immediateRender: false }, 1.0);   // odd count lands back on the from-value
}
```

The ghost is at the heaviest weight so the slot never grows; the live copy is centred in it, so only its own ink changes. Register: rising weight is rising loudness or conviction; falling weight is the "slumped shoulders" register the 2002 paper describes. The repeat arithmetic uses `Math.floor` so the yoyo never runs past the hold (`kinetic-beat-slam.md`'s repeat-ceil rule).

### R6. Slam with a blur that resolves first

```js
// Basis: kinetic-beat-slam p1 values; the manifesto's product-UI measurement that blur resolves faster
// than position on a defocus entry; impact = first frame, so this is onset-locked (R9).
function slam(sel, at) {
  tl.fromTo(sel, { scale: 1.5, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 0.5, ease: "power4.out" }, at);
  tl.fromTo(sel, { filter: "blur(16px)" }, { filter: "blur(0px)", duration: 0.32, ease: "power3.out" }, at);
}
```

Two tweens on one element are fine when they own different properties (`motion-principles.md` warns only about conflicting transforms). No overshoot on a slam.

### R7. Text as mask over footage, and the zoom-through

Blend knockout (black ground):

```html
<div class="stage" id="s7">
  <video id="bg" src="../capture/assets/videos/clip.mp4" muted playsinline></video>
  <div class="knock"><span class="kt" id="kt">SUMMER</span></div>
</div>
```

```css
#s7 { position: absolute; inset: 0; isolation: isolate; background: #000; overflow: hidden; }
#bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
/* PREFER THE MASK FORM BELOW over this multiply knockout. The antialiased edge pixels of
   white text are mid-grey, and mid-grey multiplied against bright footage darkens it, so
   every glyph carries a one-to-two-pixel dark halo -- the giveaway that the knockout was
   faked with a blend mode. `mask` / `-webkit-mask` with an alpha or luminance mask
   composites the antialiased edge as coverage rather than as a colour multiply. */
.knock { position: absolute; inset: 0; background: #000; color: #fff; mix-blend-mode: multiply;
         display: grid; place-items: center; }
.kt { font: 900 340px/1 "Archivo Black", sans-serif; letter-spacing: -0.04em; will-change: transform; }
```

```js
// Basis: CSS-Tricks knockout modes (multiply keeps dark dark, lets the video through white);
// zoom-through from the manifesto technique map ("wrapper scale, origin at the measured target glyph,
// hard cut at peak"). Video is framework-owned (techniques.md §6): never call play().
// ORIGIN: derive it, do not type it. A pixel origin is measured against a text box whose
// position depends on the shaped run, so it breaks silently on any copy or font change.
// Gate on fonts, then measure the target glyph with a Range rect.
await document.fonts.ready;
const r = document.createRange(); r.setStart(kt.firstChild, 1); r.setEnd(kt.firstChild, 2);  // the "U"
const g = r.getBoundingClientRect(), st = document.getElementById("s7").getBoundingClientRect();
gsap.set("#kt", { transformOrigin: (g.left + g.width / 2 - st.left) + "px " + (g.top + g.height / 2 - st.top) + "px" });

// ARRIVAL: do NOT animate autoAlpha on a multiply layer. White text at half opacity is
// grey, and grey multiplied against footage DIMS the footage showing through the glyph
// while the letterforms are fully present from frame one -- it does not fade the type in.
// Animate a transform or a clip-path on the knockout layer instead. (Animating the
// knockout layer's own opacity is not an option either: a half-opacity multiply layer
// half-reveals the footage across the whole frame.)
tl.fromTo("#kt", { yPercent: 8 }, { yPercent: 0, duration: 0.35, ease: "power3.out" }, 0.3);
const hold = holdFor("SUMMER", "read");
const zoomAt = 0.3 + hold, zoomDur = 0.7;
// PUSH: do not scale the TYPE. A promoted layer is rasterised once at its layout size and
// then stretched as a texture, so at 36x the glyph edge is a blurred enlargement rather
// than a crisp vector edge, and 340 px of type at 36x is about 12,000 px, near Chromium's
// texture limits. This is why browser zoom-throughs do not look like the AE version, and
// no easing fixes it. Scale the GROUND and the mask instead (hold the knockout at a fixed
// size and move a wrapper carrying the frame), or swap the glyph for an SVG path, which
// re-rasterises at every composited scale. Drop will-change from anything whose scale
// range exceeds about 3x.
tl.fromTo("#s7-camera", { scale: 1 }, { scale: 36, duration: zoomDur, ease: "expo.in", immediateRender: false }, zoomAt);
// hard cut to bare footage at the frame the counter fills the frame; find it by rendering and reading edges
const cutAt = Math.round((zoomAt + zoomDur - 2 * F) / F) * F;
tl.set(".knock", { autoAlpha: 0 }, cutAt);
```

SVG mask (any ground colour, letters still, footage still, camera pushes in):

```html
<svg width="0" height="0" aria-hidden="true">
  <defs>
    <mask id="tm" maskUnits="userSpaceOnUse" x="0" y="0" width="1920" height="1080">
      <rect width="1920" height="1080" fill="#000"/>
      <text x="960" y="640" text-anchor="middle" fill="#fff"
            font-family="Archivo Black" font-size="340" letter-spacing="-13">SUMMER</text>
    </mask>
  </defs>
</svg>
<div class="ground"><div class="masked" id="mk"><div class="inner" id="mi"><video ... muted playsinline></video></div></div></div>
```

```css
.ground { position: absolute; inset: 0; background: #1b3a2f; }
.masked { position: absolute; inset: 0; mask: url(#tm); -webkit-mask: url(#tm); will-change: transform; }
.inner  { position: absolute; inset: 0; will-change: transform; }
```

```js
// One proxy drives wrapper scale S and child scale 1/S so the footage stays still while the letters grow.
const cam = { s: 1 };
tl.fromTo(cam, { s: 1 }, { s: 6, duration: 1.2, ease: "power2.inOut", onUpdate() {
  gsap.set("#mk", { scale: cam.s, transformOrigin: "960px 540px" });
  gsap.set("#mi", { scale: 1 / cam.s, transformOrigin: "960px 540px" });
} }, 2.0);
```

Both forms: one or two hero beats per piece, render and inspect frames (the preview will not show a capture problem). The SVG-mask form's text is SVG text; measure its settled bbox with `track.mjs` rather than assuming it matches an HTML twin.

### R8. VO-word-onset arrival

```html
<p class="vo" id="vo1">
  <span class="w">Anything</span> <span class="w">a</span> <span class="w">browser</span>
  <span class="w">can</span> <span class="w">render</span>
</p>
```

```js
// Basis: techniques.md §4 (decaying slide, transcript timings), rewritten as fromTo; settle-on-onset,
// clamp, and post-line hold from section 8.2 (Netflix in-time 1-2 frames, out-time +0.5 s).
// ONSETS: seconds, scene-local, from `hyperframes transcribe` or vo-transcribe.py, verified by energy onset.
const ONSETS = [0.00, 0.23, 0.28, 0.63, 0.78];
const VO_END = 1.10;                                   // end of the last word's audio
const ENTER  = 0.35, EASE = "power2.out", T90 = 0.536; // fraction of duration at 90% travel for power2.out (R9 table)
const LEAD   = 1 * F;                                   // land one frame before the ear hears it
const els = gsap.utils.toArray("#vo1 .w");
els.forEach((el, i) => {
  // DURATION IS CONSTANT. The earlier version clamped duration to twice the gap to the
  // previous word, which on these onsets gives 0.35, 0.35, 0.12, 0.35, 0.30 -- two words
  // arriving with a different mechanic purely because the speaker ran them together, so a
  // transcript accident assigns emphasis at random (section 4.1: duration carries energy).
  // Hold the entrance constant and let closely spaced words overlap in flight, which is
  // what a waterfall does by design.
  const dur = ENTER;
  const start = ONSETS[i] - LEAD - dur * T90;                  // 90% of travel lands on the onset
  const slide = Math.max(12, 80 - i * 17);                     // decaying slide, techniques.md §4
  tl.fromTo(el, { x: slide, y: 14, autoAlpha: 0 }, { x: 0, y: 0, autoAlpha: 1, duration: dur, ease: EASE }, Math.max(0, start));
});
// The settle of the LAST WORD'S ACTUAL TWEEN. The earlier expression used the constant
// ENTER and dropped the LEAD term, so it was not the settle of any tween in this loop.
// settle = start + dur = (onset - LEAD - dur*T90) + dur = onset - LEAD + dur*(1 - T90).
const lineSettle = ONSETS[ONSETS.length - 1] - LEAD + ENTER * (1 - T90);
const exitAt = Math.round(Math.max(lineSettle + holdFor("Anything a browser can render", "read"), VO_END + 0.5) / F) * F;
tl.fromTo(els, { autoAlpha: 1 }, { autoAlpha: 0, duration: 0.22, ease: "power2.in", stagger: 0.02, immediateRender: false }, exitAt);
tl.set(els, { autoAlpha: 0 }, exitAt + 0.22 + 0.02 * (els.length - 1));
```

If a word's computed `start` would fall before the scene begins, either give the first word a shorter entrance or shift the line; never clamp silently in a way that lets it land late. Emphasis on top of arrival (the spoken word glowing or scaling) is `asr-keyword-glow.md`, added on its own driver.

### R9. Beat grid with anticipation and impact-frame offsets

```js
// Basis: 149.9 BPM / 12.008 frames per beat measured on the reference (library entry); 1-2 frame
// anticipation from Bitcut and Beat2Cut and from the reference's own behaviour; t90 fractions computed
// from GSAP's ease definitions: powerN.out(p) = 1 - (1 - p)^(N+1), expo.out(p) = 1 - 2^(-10p).
// Verify one: gsap.parseEase("power3.out")(0.438) is about 0.90.
const BPM = 149.9, OFFSET = 0.0;
const beat = n => OFFSET + n * 60 / BPM;
const ANTICIPATE = 1 * F;                                  // 1-2 frames
const T90 = { "power1.out": 0.684, "power2.out": 0.536, "power3.out": 0.438, "power4.out": 0.369, "expo.out": 0.332 };
const onFrame = t => Math.round(t / F) * F;

// onset-locked mechanics (slam, snap, cut, waterfall, typewriter, glitch): the START is the impact
function onsetAt(n) { return onFrame(beat(n) - ANTICIPATE); }
// settle-locked mechanics (mask rise, cascade, blur-resolve, weight, tracking): the 90% frame is the impact
function settleStart(n, dur, ease) { return onFrame(beat(n) - ANTICIPATE - dur * T90[ease]); }

// Example: a phrase rises through a mask (R2) and lands on beat 8; the next slams on beat 12; hold across 9-11.
const riseAt  = settleStart(8, 0.45, "power3.out");
const slamAt  = onsetAt(12);
```

Do not put a hit on every beat; hold across bars and cut on downbeats (both beat-sync sources; the grader's CV check). For a derived film, do not quantise the reference's cuts onto the grid if the reference anticipates it; carry the measured frames (library entry note).

### R10. Exit set with kills

```js
// Basis: section 5. Every exit is fromTo from the rest state, .in ease, ~0.6 x its entrance, then a kill.
function exitDrop(sel, at, dur = 0.27)  { tl.fromTo(sel, { yPercent: 0 }, { yPercent: -110, duration: dur, ease: "power3.in", immediateRender: false }, at); tl.set(sel, { autoAlpha: 0 }, at + dur); }
function exitBlurUp(sel, at, dur = 0.33){ tl.fromTo(sel, { y: 0, filter: "blur(0px)", autoAlpha: 1 }, { y: -150, filter: "blur(30px)", autoAlpha: 0, duration: dur, ease: "power2.in", immediateRender: false }, at); tl.set(sel, { autoAlpha: 0 }, at + dur); }
function exitShrink(sel, at, dur = 0.25){ tl.fromTo(sel, { scale: 1, autoAlpha: 1 }, { scale: 0.92, autoAlpha: 0, duration: dur, ease: "power2.in", immediateRender: false }, at); tl.set(sel, { autoAlpha: 0 }, at + dur); }
function exitCut(sel, at)                { tl.set(sel, { autoAlpha: 0 }, at); }          // then 1-8 blank frames
```

`exitBlurUp` values are the velocity-matched pair from `techniques.md` §10; its entry twin is `y: 150 -> 0, blur 30 -> 0, 1.0 s power2.out`.

### R11. Hierarchy stack

```html
<div class="stack" id="k1">
  <div class="hero" id="k1h">Decide faster.</div>
  <div class="sub"  id="k1s">Every signal, one screen, no waiting.</div>
  <div class="eyebrow" id="k1e">SYSTO / 02</div>
</div>
```

```css
.stack { position: absolute; left: 140px; bottom: 140px; }             /* anchored, not centred */
.hero    { font: 900 150px/0.96 "Archivo Black", sans-serif; letter-spacing: -0.03em; }
.sub     { font: 400 66px/1.15 "Archivo Black", sans-serif; opacity: 0.9; margin-top: 0.25em; }   /* 0.44 of hero */
.eyebrow { font: 700 30px/1 "Space Mono", monospace; letter-spacing: 0.12em; margin-bottom: 0.6em; }  /* 0.20 of hero */
```

```js
// Basis: section 6.2 ratios; hero first (typography.md); support 100-200 ms after the hero settles
// (LottieFiles secondary-action and follow-through figures, stretched for video); staging dim from disney #3.
const at = 0.3;
slam("#k1h", at);                                                        // R6, onset-locked
const heroSettle = at + 0.5;
tl.fromTo("#k1s", { y: 40, autoAlpha: 0 }, { y: 0, autoAlpha: 0.9, duration: 0.45, ease: "power3.out" }, heroSettle + 0.15);
tl.fromTo("#k1e", { x: -24, autoAlpha: 0 }, { x: 0, autoAlpha: 1, duration: 0.35, ease: "power2.out" }, heroSettle + 0.25);
```

Three sizes, three eases, three axes (scale, y, x), one face plus a mono for the eyebrow; the composition check for distinct sizes passes by construction.

### R11b. Two build-time rules every recipe above depends on

**Gate every build-time measurement on fonts.** R4 reads `getComputedStyle(letters[0]).fontSize`
at build time and R7 measures a glyph rect. If the capture worker constructs the timeline
before the woff2 has decoded, both measure fallback metrics and bake them in, and the
failure is silent, intermittent and only visible on some renders. `await document.fonts.ready`
before any measurement and before timeline construction, and set `font-display: block` on
**every** face, not only the variable one. (CSS Font Loading API; the recipes' own use of
build-time measurement.)

**Pin the transform pipeline so antialiasing does not flip mid-piece.** GSAP's default
`force3D: "auto"` adds a 3D transform for the duration of a tween and removes it at the
end, promoting then demoting the layer and flipping the text between greyscale and subpixel
antialiasing at the tween boundary. On 140 px type that reads as a small weight pop on the
settle frame -- the exact frame this document cares about and the exact frame the grader
samples. Set `gsap.config({ force3D: true })` for the composition and keep `will-change`
static so promotion state never changes. (GSAP CSSPlugin `force3D` behaviour; Chromium
changes text antialiasing mode with layer promotion.)

### R12. Typewriter, contract-clean

Use `discrete-text-sequence.md` (sparse state array, reverse search, sin square-wave cursor) for anything with edits or pauses; for a plain type-on use per-character spans with `tl.set(span, { autoAlpha: 1 }, t_i)` at the character times (manifesto: "per-char spans, fromTo autoAlpha dur 0.02 (binary, never fade)"). Cursor: `tl.fromTo(cursor, { opacity: 1 }, { opacity: 0, duration: 0.4, ease: "steps(1)", yoyo: true, repeat: Math.max(0, Math.floor(span / 0.8) * 2 - 1) }, t0)`. Never a CSS `@keyframes` blink. If the line re-centres while typing, the manifesto's rule applies: hidden words keep layout width, and the group's `x` shift is stepped per word from `measureText` widths, never from DOM rects.

---

## 13. Verification checklist

Run against the render, not the preview. Existing checks are in `grade-original.py`; the added ones are proposals in the same pass/fail style.

Existing (grade-original.py):

- No duplicate consecutive frames (a hold rendered as bit-identical frames reads as a stall).
- No ink inside the 4% edge margin except named full-bleed gestures.
- Worst settled contrast >= 3:1 (WCAG large text), sampled only inside the settled window.
- Vertical spread of content centroid sd >= 0.09; <= 85% of frames with content in the middle third.
- >= 3 distinct type sizes in the timeline.
- No spoken beat renders an empty frame mid-beat.
- No settle direction reversal on ink count (overshoot), segmented on re-triggers.
- Beat-length CV >= 0.18.
- Audio: -17 to -15 LUFS integrated, peak <= -1 dBFS, duck depth <= 6 dB, music 6-14 dB below voice, per-line read spread <= 3 dB.
- Every spoken line has something on screen within 6 samples of its onset.

Proposed additions (basis: this document):

- Per card, settled hold >= `holdFor(text, regime)` where **regime is derived, not declared** (`regimeOf()` in 2.4): a card is a read card if it introduces a word not shown earlier. As an author-declared enum the check is an attestation, not a measurement.
- Per card that **exits by animating in place**, exit duration <= 0.75 x entrance duration (LottieFiles upper bound). Hard cuts (ratio 0) and declared transitional handoffs are exempt by name.
- Per VO word, first settled frame within 2 frames of the energy onset and never after it.
- **At least a third of structural cuts within 2 frames of a beat and, of those, a majority early**, with the anticipation itself 1 frame at 30 fps. The earlier version of this check ("every structural cut 0-2 frames early") is failed by the measured reference on twelve of its twenty-three cuts, so it cannot be a gate. Count of cuts per bar <= 1 on average.
- Smallest type on screen >= 24 px at 1080p (>= 32 px for feed delivery); hero >= 60% of frame width on hero cards.
- For 9:16 delivery, no type inside the platform bands (Kreatli's conservative margins) on the frames that matter.
- Every `fromTo` that re-owns a property carries `immediateRender: false`; every fade-out has a `tl.set` kill; every element whose first tween is a fade-out has a baseline `tl.set` (grep the timeline).
- No `letter-spacing`, `width`, `height`, `top`, `left`, `font-size` in any tween target list.
- No synthetic bold: every `font-weight` requested is a weight the embedded face actually ships.
- `await document.fonts.ready` precedes every build-time measurement and the timeline construction.
- Every element travelling more than about 1.5% of frame width per frame has a shutter pass or a directional-blur substitute, and no blurred frame touches a cut frame.
- Line breaks are authored per card, not left to box wrapping.
- No full-frame flash sequence exceeding three luminance reversals per second (WCAG 2.3.1); ground inversions counted.
- The silent cut is watchable: play the render muted and check every card is still readable at its authored hold.
- Blank-gap runs present and, for a derived film, matching the skeleton's runs within 1 frame.

---

## 14. Open questions

- The hold model's coefficients (0.33 s per word plus 0.40 s, and the beat-regime targets) have not been tested on viewers of kinetic type; they are caption rates plus reasoning, and section 2.3 now says outright that they are floors rather than design targets, because taken as targets they are roughly twice as slow as the measured reference. A small A/B on comprehension of 3-6 word cards at 0.25, 0.33 and 0.40 s per word would settle the read regime.
- The Ford, Forlizzi, Ishizaki 1997 abstract could not be retrieved directly (429 and 403 on the two hosts tried); its content is cited through the 2002 paper's summary. The 2002 and 2006 papers were read in full.
- The BBC guideline text is cited through two secondary pages; the bbc.co.uk and bbc.github.io hosts were unreachable from this session. The two secondaries agree with each other on every figure used.
- Studio patterns are drawn from interviews and profiles, not from measured pieces. Each "borrow" is an inference. A measured library entry per studio would replace this section.
- The SVG `<mask>` with `<text>` over a `<video>` and the `mix-blend-mode` knockout over a `<video>` have not been rendered through the HyperFrames capture worker in this session; the mechanisms are standard CSS compositing, but the cost and determinism under seek need a test render before either is used on a hero beat.
- Tweening a CSS custom property that feeds `font-variation-settings` (R5) follows `techniques.md` §8, which is an existing pattern, but seek-safety of that specific property in the render worker was not verified here.
- Whether a `letter-spacing` tween is forbidden by the contract or merely discouraged is a reading of the rules-index wording ("transforms and paint-only properties"); R4 avoids the question by not using it.
- The t90 fractions assume GSAP's documented ease formulas; confirm with `gsap.parseEase` in the build before locking a beat to them.
