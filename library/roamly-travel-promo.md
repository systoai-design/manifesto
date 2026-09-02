# roamly-travel-promo

**Callable as: Roamly** (aliases: the travel app promo, the white product film,
the isometric map film)

A 37.5-second promo for a travel-planning app: kinetic type typed by a caret, a
UI card assembling, a 3D-tilted isometric map with drawn routes and city labels,
photo cards, recommendation rows, gradient type, and a logo lockup. Measured
2026-09-02. Source: 1280x720 @ 30fps, 1124 frames, 37.467s. A third party's
commercial work, supplied as a reference to replicate.

**Study only.** This is a Match of somebody's shipped advertising. The entry
records measurements; the build stays local and is not published. Nothing in
this file reproduces the reference's media.

## Fidelity — skeleton

Cut frames, per-segment durations, per-signal easing fits, the palette census,
the typeface identification and its ceiling, and the map camera curve are all
recorded. The audio was not analysed.

## Structure

26 segments from the blank-run and column-profile model, total 1031 of 1124
frames inside segments. Frame ranges, and what each shows:

| # | frames | dur | shows |
| --- | --- | --- | --- |
| 0 | 0-100 | 3.37s | headline typed on, two lines, caret |
| 1-4 | 101-122 | 0.73s | type dissolves to streaks and dust |
| 5 | 140-220 | 2.70s | UI card assembles over lavender skeleton bars |
| 6 | 221 | 0.03s | flash |
| 7 | 268-275 | 0.27s | the card tilts away as a plane |
| 8 | 276 | 0.03s | flash |
| 9 | 287-440 | 5.13s | the map. The longest beat. |
| 10 | 441-485 | 1.50s | search field |
| 11 | 489-594 | 3.53s | "One place to plan every trip." + six pictograms |
| 12-13 | 607-614 | 0.26s | flash |
| 14 | 615-651 | 1.23s | the CTA, with a bloom |
| 15-18 | 652-709 | 1.93s | photo cards with a chromatic swell |
| 19 | 710-771 | 2.07s | booking row |
| 20 | 772 | 0.03s | flash |
| 21 | 774-812 | 1.30s | "Plan smarter." |
| 22 | 813-863 | 1.70s | "Travel better.", gradient swept through the glyphs |
| 23 | 864-933 | 2.33s | two recommendation rows |
| 24 | 934-1021 | 2.93s | "One app. Every route.", rotated, over dashed routes |
| 25 | 1022-1123 | 3.40s | the lockup, held |

Per-segment easing fits with residuals and runners-up are in the source's
`segments.json`; the recurring shapes are `power4.inOut` on the fast card moves,
`back.out(3)` on pill arrivals, `expo.in` on exits and `sine.out` on the long
map settles.

## Palette, by quantised pixel census over every 8th frame

| hex | share | job |
| --- | --- | --- |
| `#FCFCFC` | 79.5% | the page. Near-white, never pure white. |
| `#F0F0F0` | 5.7% | cards and placeholder fills |
| `#F0F0FC` | 2.6% | the lavender wash under UI |
| `#0C00FC` | 0.13% | the CTA and the wordmark |
| `#6C60F0` | 0.07% | secondary UI and icon grounds |
| `#CCC0F0`, `#D8CCFC` | 0.31% | skeleton bars |
| `#90CCF0` | 0.25% | the first drawn route |

**Only 0.9% of sampled pixels are chromatic at all** (max-min > 40). This is the
governing fact of the film: a white piece that spends saturated colour as
punctuation. Any rebuild that lands above about 2% chroma has missed it.

## Typeface — substitution, with a measured ceiling

| candidate | best weight | glyph IoU | rendered aspect |
| --- | --- | --- | --- |
| **Inter Tight** | **550** | **75.7%** | 8.92 |
| Archivo | 650 | 69.5% | 9.81 |
| Inter | 700 | 26.0% | 6.86 |
| Geist, Satoshi | - | below Archivo | - |

Reference aspect for "beautifully planned." is 8.49.

Inter Tight is a **near relative, not the face** — expect a real ceiling on every
type card and do not spend iterations chasing it. The reference is most likely
Inter Display or a licensed grotesque of that family.

Fitting Archivo's variable axes was tried and **rejected on the evidence**:
setting `wdth` 85 matched the reference aspect almost exactly (8.59 against 8.49)
and *lowered* IoU to 66.1% from 69.5%. The proportions were never the problem,
the letterforms were, and that measurement is what justified fetching other faces
instead of tuning this one.

## Type sizes, fitted to measured ink widths

Sizes were fitted by binary search so the rendered string width matches the
reference's measured ink box, which is more reliable than reading a cap height
off an antialiased frame.

| string | measured width | fitted size |
| --- | --- | --- |
| "beautifully planned." | 620px | 81px |
| "One place to plan every trip." | 621px | 56px |
| "Plan smarter." | 505px | 95px |
| "Philadelphia, PA" | 574px | 86px |
| "Find trips" | 420px | 106px |
| "Chelsea" | 340px | 101px |

## The map camera — the one measurement that matters most here

The map beat is **not a static perspective**. The plane starts zoomed and
rotated in plane, unwinds to axis-aligned, then pushes back in.

Scale was recovered by autocorrelating the centre scanline's edges to get the
grid pitch, and dividing by the settled pitch of 70px:

| frame | grid pitch | scale |
| --- | --- | --- |
| 300 | 180px | 2.57 |
| 320 | 144px | 2.06 |
| 360 | 70px | 1.00 |
| 400 | 111px | 1.59 |

Both legs are close to linear, so the eases are `none`. A `power3.out` pull-back
reaches scale 1.0 by f320 and leaves the middle of the beat flat, which is the
first thing a rebuild gets wrong. Opening rotation is about -16 degrees,
resolved to 0 by the flat hold.

**A measurement caution that cost real time here.** The obvious way to recover
the rotation is an edge-gradient orientation histogram. On this material it is
unreliable — it reported 0 degrees on reference frames that are visibly tilted,
because a pale one-pixel grid on near-white gives too few gradient pixels to
outvote the type and the pills. Grid *pitch* is stable and rotation is better
taken off a visual check or a Hough fit. Do not trust the histogram here.

## Elements worth recording

- Routes are drawn as a **wide pale corridor under a sharp line** with a round
  cap head, not a single stroke: the halo is the road, the line is the trip.
  Corners are quadratic, not right angles.
- The two routes never share a frame. The first draws and clears before the
  second begins.
- Six place pills: Princeton NJ, Beacon NY, Boston MA, SoHo New York, Newport RI,
  New London CT. White, fully rounded, on a two-layer shadow.
- Six single-stroke pictograms around the "One place" line — parasol, museum,
  flag, fan, pin, ticket — each a different hue at a small authored rotation.
- "One app. Every route." is rotated **-8.5 degrees**, recovered by fitting a
  line through its ink centroid.
- The CTA's solid core is 874x132 with roughly a 19px bloom halo around it.

## What cannot be reproduced

The photo cards at segments 15-18 are photography with a chromatic mesh
distortion. A study build has no rights to the plates and no way to reproduce
them; a stand-in gradient of the measured hues is the honest substitute and it
must be stated. The app-card interior and the drawn pictograms are approximations
by construction.

## Derived

None yet. The skeleton is recorded and licenses deriving a new film without
re-measuring: 26 segments, their frames, the palette, the type scale and the map
camera curve are all here.
