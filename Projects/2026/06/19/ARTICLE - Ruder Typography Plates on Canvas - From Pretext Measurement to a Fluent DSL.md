---
title: "Ruder Typography Plates on Canvas — From Pretext Measurement to a Fluent DSL"
aliases:
  - Ruder Typography Plates
  - Ruder Canvas Composition Deep Dive
  - Ink-Bounds Canvas Alignment
  - Canvas Typography DSL
tags:
  - article
  - typography
  - canvas
  - pretext
  - ink-bounds
  - measurement
  - swiss-typography
  - dsl
  - vite
status: active
type: article
created: 2026-06-19
repo: /home/manuel/code/wesen/2026-06-16--learn-grids-2
---

# Ruder Typography Plates on Canvas — From Pretext Measurement to a Fluent DSL

This article is a deep technical analysis of a single-page typographic composition system built on HTML5 Canvas: seven "Ruder plates" on one beige card, each exercising a different sub-domain of typography, plus a design for a fluent domain-driven DSL that the implementation *should* have been. The reference implementation lives in `/home/manuel/code/wesen/2026-06-16--learn-grids-2/ruder/` — a Vite + TypeScript project that renders seven compositions on seven DPR-scaled canvases, drives three of them with live slider controls, and ships an interactive typeface selector on four of them.

The thread that connects the seven plates is a single discipline: **measurement and drawing must share the same font, the same shaping, and the same coordinate system.** Once that holds, alignment stops being a matter of manual offsets and becomes a matter of reading measured quantities. The article builds each plate from that discipline, shows the failure modes that broke it, and ends with the DSL that inverts the implementation's leakage of canvas internals into the typography domain.

The work sits downstream of two earlier Pretext articles in this vault — [[ARTICLE - Pretext Print Layout - Building a Swiss Typography Rendering System for Dense Programming Reports|the Pretext Print Layout system]] and [[ARTICLE - Constraint-Based Layout on Canvas - Cassowary + Pretext + React|the Cassowary canvas layout system]]. Those articles established Pretext as a fast, DOM-free text-measurement library and constraint-based positioning on canvas. This article is narrower and deeper: it is about what happens when you commit fully to measuring glyphs with the browser's own shaping engine and then drawing the same glyphs on the same canvas, so that the measured advance widths and the drawn glyph origins are guaranteed to coincide.

> [!summary]
> 1. **Measurement-drawing parity is the only foundation that holds.** When `ctx.measureText` and `ctx.fillText` run against the same font shorthand on the same DPR-scaled canvas, measured advance widths and drawn glyph advance origins coincide exactly. Any cross-target pair (DOM measure + canvas draw, or two canvases with different fonts) introduces drift that no amount of manual correction can fully remove.
> 2. **Ink-bounds alignment and advance-box alignment are different problems.** `textAlign='left'|'right'|'center'` anchors the advance box, not the visible ink. For glyphs with side bearings (u, s, i, l, g), advance-box alignment produces visibly ragged columns. The fix is to offset the draw position by `actualBoundingBoxLeft` and `actualBoundingBoxRight`, which the browser exposes as non-standard but widely supported `TextMetrics` fields.
> 3. **Construction guides are weight-invariant; ink area is not.** A type specimen's cap-height, x-height, and descender guides drawn from the regular weight (400) describe the typeface's construction and apply to every weight. The ink-area block behind a glyph, by contrast, grows with weight because the stem thickens. Teaching the eye to see the difference between invariant construction and growing ink is the whole point of a weight-ramp specimen.
> 4. **The canvas implementation leaks.** The actual code expresses typography as `TitleSize = 24`, `ctx.font = fontShorthand()`, `x = -actualBoundingBoxLeft`, `InnerH = InnerW`. The DSL the project *should* have had expresses the same ideas as `.size(24).weight(400)`, `.alignInk('left','center','right')`, `.card({ square: true })`. The gap between the two is the cost of speaking the canvas vocabulary instead of the typography vocabulary.

## Why this note exists

The Ruder plates were built across one extended session, one composition at a time, each one revealing a distinct typography concept that the previous one had not needed. The first plate needed Pretext advance-width measurement. The second needed ink-bounds alignment. The third needed construction guides drawn from weight-invariant metrics. The fourth needed a closed-form enumeration of a two-color arrangement space. The fifth and sixth needed palette uniformity and optical centering. The seventh needed geometric composition (tangent circles, modular grids, palette mapping) layered on top of typography.

By the time the seventh plate was built, the implementation had accumulated a large amount of duplicated boilerplate — `newCanvas(cssW, cssH)`, `drawCard`, `drawHairline`, the `mountControls(state, schema, onChange)` pattern, the mutable `state` object, the `reRender` loop — and a correspondingly large amount of leakage: typography concepts had to be expressed as canvas coordinates and font shorthand strings. The natural next step was to design the API surface the project should have had from the start, and to write it down before the lessons of the seven plates were forgotten.

This note is that write-down. It is written for someone who wants to build typographic compositions on canvas and who wants to understand, in implementation terms, why each design decision was made. It is not a tutorial; it assumes familiarity with the canvas 2D API, with `document.fonts`, and with the basic idea of glyph metrics. The two earlier Pretext articles cover the measurement library and the constraint-layout system this project builds on.

## The shared foundation: DPR-scaled canvas and measurement-drawing parity

Every plate in the project is rendered by the same helper, which scales the canvas backing store to the device pixel ratio and leaves the rest of the drawing in CSS pixels:

```ts
function newCanvas(cssW: number, cssH: number) {
  const dpr = Math.max(1, window.devicePixelRatio || 1)
  const canvas = document.createElement('canvas')
  canvas.width = Math.ceil(cssW * dpr)
  canvas.height = Math.ceil(cssH * dpr)
  canvas.style.width = `${cssW}px`
  canvas.style.height = `${cssH}px`
  const ctx = canvas.getContext('2d')!
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  return { canvas, ctx, dpr }
}
```

Two properties of this helper matter for everything that follows.

The first is that the transform `(dpr, 0, 0, dpr, 0, 0)` means every subsequent draw call is expressed in CSS pixels, and the backing store is sharp on hidpi screens. Glyphs drawn at integer CSS coordinates land on device pixels at `dpr × coordinate`, so there is no half-pixel anti-aliasing across the whole stroke at `dpr = 2`. The cost is that `ctx.getImageData` reads device pixels, so any pixel-scan verification has to multiply the sample coordinates by `dpr`. Forgetting that multiplier is the single most common bug when verifying a plate.

The second property is the foundation of the whole project. When the same font shorthand string is passed to `ctx.font` for both measurement and drawing, the browser shapes the glyphs identically in both passes. The advance width returned by `ctx.measureText(token).width` is exactly the distance the drawing cursor advances when `ctx.fillText(token, 0, y)` draws the same token. There is no DOM-vs-canvas drift, no font-fallback discrepancy, no kerning surprise, because the measurement and the drawing go through the same shaping engine.

This is the reason the project draws on canvas rather than positioning DOM nodes. The earlier Pretext Print Layout article documented that measured heights diverge from CSS-rendered heights and that the fix was to use Pretext only for page-break decisions. That lesson holds for the DOM. On a single canvas, with a single font shorthand, the divergence disappears. The cost is that you give up CSS layout and re-implement alignment yourself, but the gain is that alignment becomes a pure function of measured quantities.

Font readiness is part of the contract. The project waits for `document.fonts.ready` and then loads the specific weight and size before any measurement or drawing:

```ts
async function applyPreset(id: string): Promise<void> {
  state = presetById(id)
  const fontsApi = (document as { fonts: { load: (f: string, t?: string) => Promise<unknown> } }).fonts
  try {
    await fontsApi.load(fontShorthand(), 'a')
  } catch { /* will fall back; measurement may be off */ }
  const { positions } = renderComposition()
  renderDebug(positions)
}
```

Measuring before the font is loaded measures the fallback. The fallback has different metrics. The measurement-drawing parity contract is only satisfied once `document.fonts.load` has resolved for the exact font shorthand being measured. This is why every `applyPreset` path awaits the load before re-rendering.

## Plate 1 — Pretext vowel measurement (the canonical case)

The first plate, and the one the rest of the project refers back to, is a single canvas holding two lines. The upper line is the display string `abcedfghijklmnopqrstu` (the alphabet a through u, with d and e swapped, 21 characters). The lower line is the five vowels `a e i o u`, each drawn one line-box below the upper line, each colored differently, and each horizontally aligned with its counterpart in the upper line.

The alignment target is the **advance origin** of the vowel in the upper line — the position where the drawing cursor would be if it were about to draw that vowel. The advance origin of `a` is 0, because `a` is the first character. The advance origin of `e` is the measured advance width of the prefix `abc` (the three characters before `e`). The advance origin of `i` is the measured advance width of the prefix `abcedfgh` (the eight characters before `i`).

The measurement is done with Pretext's `prepareWithSegments` and `measureNaturalWidth`:

```ts
function measureVowelPositions() {
  const out = []
  for (const v of VOWELS) {
    const idx = DISPLAY_TEXT.indexOf(v)
    if (idx < 0) continue
    const prefix = DISPLAY_TEXT.slice(0, idx)
    const prepared = prefix === ''
      ? prepareWithSegments('', fontShorthand())
      : prepareWithSegments(prefix, fontShorthand())
    const x = prefix === '' ? 0 : measureNaturalWidth(prepared)
    out.push({ vowel: v, x, index: idx })
  }
  return out
}
```

`measureNaturalWidth` returns the widest forced line of a prepared text. For a single-line prefix with no wrap point, that is the full advance width of the prefix. The lower vowel is then drawn at exactly that x, one line-box below the upper line, with the same font shorthand. Because the measurement and the drawing share the font shorthand on the same canvas, the lower vowel's advance origin coincides with the upper vowel's advance origin to the pixel.

```ts
ctx.font = fontShorthand()
ctx.textBaseline = 'top'
ctx.fillText(DISPLAY_TEXT, 0, 0)              // upper line
const lowerY = lineBoxPx
for (const { vowel, x } of positions) {
  ctx.fillStyle = VOWEL_COLORS[vowel]
  ctx.fillText(vowel, x, lowerY)             // lower vowel at measured advance origin
}
```

The subtlety worth naming is that the advance origin is not the left edge of the ink. Most glyphs have a left side bearing: the glyph's ink starts a few pixels to the right of the advance origin, and a few glyphs (`u`, `o`) overhang the origin to the left. A pixel scan of the lower vowel's ink will therefore show the ink starting a few pixels right of the measured x. That is not drift; it is the side bearing, and it is the same side bearing in the upper line. The composition is aligned at the advance origin, which is the typographic definition of the left edge of a glyph slot.

This plate is the canonical case because it reduces typography to its smallest non-trivial problem: position one glyph under another glyph, using only measurement. Every later plate generalizes this in some direction — multiple weights, multiple columns, multiple arrangements, geometric tangency — but the discipline is the same.

## Plate 2 — Three-line light→bold with ink-bounds alignment

The second plate is three lines of three tokens each, with a weight ramp across the lines (light 400, regular 700, bold 900):

```
a    u     s       (light)
b    il    d       (regular)
u    n     g       (bold)
```

The left column (`a`, `b`, `u`) is left-aligned at the canvas left edge. The right column (`s`, `d`, `g`) is right-aligned at the canvas right edge. The middle column (`u`, `il`, `n`) is centered. The first implementation used the obvious canvas primitives:

```ts
ctx.textAlign = 'left';   ctx.fillText(tokens[0], 0, y)
ctx.textAlign = 'center'; ctx.fillText(tokens[1], canvasW / 2, y)
ctx.textAlign = 'right';  ctx.fillText(tokens[2], canvasW, y)
```

This is advance-box alignment, and it is wrong for this composition. The reason is visible in the metrics of `a` at Playfair Display 900, 140px: `actualBoundingBoxLeft = -5`, `actualBoundingBoxRight = 74`. The glyph's ink extends five pixels to the left of the advance origin. With `textAlign='left'` at `x = 0`, the advance origin is at 0, so the ink starts at `0 + (-5) = -5` — five pixels off the canvas. For `s` at the same weight, `actualBoundingBoxLeft = -7`, so the right-aligned `s` ends with its ink seven pixels inside the right edge. The three left-column letters end up with their visible ink at -5, 0, -1: a visibly ragged left edge. The three right-column letters end up with their visible ink at -7, -5, 0: a visibly ragged right edge.

The fix is to align the ink, not the advance box. Each token's ink bounds are read from `TextMetrics`, and the draw position is offset so the ink lands where the advance box would have landed under a hypothetical glyph with no side bearings:

```ts
interface TokenMetrics {
  advanceW: number
  inkLeft: number    // actualBoundingBoxLeft, ≤ 0 for overhang-left glyphs
  inkRight: number   // actualBoundingBoxRight, ≤ advanceW
  inkW: number       // inkRight - inkLeft
}

function measureToken(token, font): TokenMetrics {
  measureCtx.font = font
  const m = measureCtx.measureText(token)
  const il = typeof m.actualBoundingBoxLeft  === 'number' ? m.actualBoundingBoxLeft  : 0
  const ir = typeof m.actualBoundingBoxRight === 'number' ? m.actualBoundingBoxRight : m.width
  return { advanceW: m.width, inkLeft: il, inkRight: ir, inkW: ir - il }
}
```

The three columns are then drawn with `textAlign='left'` and computed offsets:

```ts
// left column: ink-left at 0        → x = -inkLeft
// middle column: ink-center at W/2  → x = W/2 - (inkLeft + inkRight)/2
// right column: ink-right at W      → x = W - inkRight
ctx.textAlign = 'left'
ctx.fillText(left,  -leftMetrics.inkLeft,                            y)
ctx.fillText(mid,   W/2 - (midMetrics.inkLeft + midMetrics.inkRight)/2, y)
ctx.fillText(right, W - rightMetrics.inkRight,                       y)
```

The invariant this produces is exact. The left column's `inkLeft + x = -inkLeft + inkLeft = 0` for all three lines. The right column's `inkRight + x = inkRight + (W - inkRight) = W` for all three lines. The middle column's `inkCenter + x = (inkLeft + inkRight)/2 + W/2 - (inkLeft + inkRight)/2 = W/2` for all three lines. A numeric readout printed under the canvas lets the user read these values directly, which is how the alignment was verified without trusting a screenshot.

`actualBoundingBoxLeft` and `actualBoundingBoxRight` are non-standard fields on `TextMetrics`. They are supported in Chromium and Firefox. The code falls back to the advance box (`inkLeft = 0`, `inkRight = advanceW`) when the fields are absent, which collapses the offsets to the original advance-box alignment. The composition therefore degrades gracefully on a browser without ink bounds, and the degradation is honest rather than silent: the numeric readout shows `inkLeft = 0` for every token, which signals that the fallback is in effect.

This plate is where the project learned that "alignment" is ambiguous until you specify whether you mean the advance box or the ink box, and that the two only coincide for glyphs with zero side bearings. The specimen, the prose, and the stacked headline all inherit this distinction.

## Plate 3 — Type specimen: construction guides and growing ink

The third plate is a type specimen. Five columns, a weight ramp from light 300 to black 900, and two horizontal bands per column. The upper band holds the word `Hamburgefons` set vertically (rotated 90° counter-clockwise, so it reads bottom-to-top with the baseline at the bottom of the column). The lower band holds the two-letter construction study `Hg` — the cap `H` and the lowercase `g` — at large size, with construction guides drawn behind the glyphs.

The construction guides are the point of the plate. There are four horizontal hairlines: the baseline, the cap-height line, the x-height line, and the descender line. They are drawn once across the full lower band, and they are computed from the regular-weight (400) metrics of the family:

```ts
function computeGuides(): Guides {
  const f = regularFont()  // 400 weight, HgSize
  const H = measureToken('H', f)
  const x = measureToken('x', f)
  const g = measureToken('g', f)
  const capH = H.ascent          // cap-height
  const xH   = x.ascent          // x-height
  const desc = g.descent         // descender depth
  const breathing = (LowerH - (capH + desc)) / 2
  const baseY = InnerY + UpperH + breathing + capH
  return { baseY, capY: baseY - capH, xHtY: baseY - xH, descY: baseY + desc, capH, xH, desc }
}
```

The reason the guides are drawn from the 400 weight is that the construction — the cap-height, the x-height, the descender depth — is a property of the typeface, not of any individual weight. The em box is the same for every weight of a family. What changes with weight is the stem thickness, which shows up as the ink area, not as the construction. Drawing the guides from one weight and then drawing every weight's glyphs against those guides makes this visible: the cap-height line sits at the same y for the light `H` and the black `H`, but the black `H`'s ink is visibly wider.

That visibility is amplified by the ink-area block. Behind each `g` glyph, a translucent black rectangle is drawn, sized to the glyph's ink bounding box:

```ts
const BlockAlpha = 0.25
function drawInkBlock(ctx, x, y, w, h, alpha) {
  ctx.save()
  ctx.fillStyle = INK
  ctx.globalAlpha = alpha
  ctx.fillRect(x, y, w, h)
  ctx.restore()
}
// per column, behind the g glyph:
drawInkBlock(ctx, gx + g.inkLeft, baseY - g.ascent, g.inkW, g.ascent + g.descent, BlockAlpha)
```

The block's width is `g.inkW`, which is the horizontal extent of the `g`'s ink. At Inter 300 the block is 41px wide. At Inter 900 the block is 46px wide. The block is drawn at a constant 0.25 alpha, so the eye sees the area grow rather than the darkness grow. This is the teaching move: the construction is invariant (the guides do not move), and the ink grows. A reader looking across the five columns sees the same skeleton with progressively thicker flesh.

The rotated word in the upper band is drawn with the canvas transform. The rotation is `-π/2`, which in canvas coordinates (y-down) makes the rotated x-axis point up and the rotated y-axis point right. With `textAlign='left'` and `textBaseline='alphabetic'`, `fillText(word, 0, 0)` then extends the word upward from the translation point, with the baseline at the translation point:

```ts
ctx.translate(colCenterX, baseLineY)   // column center, bottom of upper band
ctx.rotate(-Math.PI / 2)
ctx.textAlign = 'left'
ctx.textBaseline = 'alphabetic'
ctx.translate(0, (m.ascent - m.descent) / 2)  // center the word's ink on colCenterX
ctx.fillText(WORD, 0, 0)
```

The final `translate(0, (ascent - descent) / 2)` is the ink-centering trick again: after rotation, the canvas's local y-axis is horizontal, so a y-translate in the rotated frame shifts the word horizontally in the unrotated frame. The offset `(ascent - descent) / 2` centers the word's ink vertically (in the rotated frame) on the column center.

This plate is where the project learned to separate construction from ink, and to use that separation as a teaching device. It is also where the project learned that the rotated-word orientation has to be verified by pixel scan rather than by reading the rotation code, because the canvas rotation conventions are easy to get backwards.

## Plate 4 — The 21-arrangement 6×6 gallery

The fourth plate leaves typography for geometry. It is a gallery of 21 arrangements of two colors (ink-black and brick-orange) on a 6×6 grid of circles, rendered as a 3×7 array of mini-panels. Each arrangement is a pure function from cell coordinates to a color:

```ts
type Arr = { id: number; name: string; fn: (i: number, j: number) => 0 | 1 }
```

The 21 functions enumerate the standard two-color arrangement space: solids, checkerboards at 1×1 and macro-quadrant scales, vertical and horizontal stripes and halves, outer ring and its inverse, cross and its inverse, thin X and its inverse, two Sierpinski halves, concentric squares, filled diamond, and a thick X. The interesting ones are the Sierpinski arrangements, which use a closed-form identity from number theory.

The Sierpinski sieve is Pascal's triangle modulo 2. A cell `(i, j)` is colored according to the parity of the binomial coefficient `C(i + j, i)`. Computing binomial coefficients modulo 2 directly is possible but clumsy. The Lucas theorem gives a much cleaner test: `C(i + j, i)` is odd if and only if `(i & j) === 0`, where `&` is bitwise AND. The proof is that Lucas's theorem reduces `C(n, k) mod 2` to the bitwise condition `(k & (n - k)) === 0`, and here `n = i + j`, `k = i`, `n - k = j`.

The arrangement is therefore:

```ts
const SIERP_UP = (i, j) => (i + j <= 5 && (i & j) === 0) ? 1 : 0
```

The `i + j <= 5` restricts the pattern to the upper anti-triangle of the 6×6 grid, which is where Pascal's triangle lives. The lower anti-triangle is the mirror, reflected across the anti-diagonal by transforming `(i, j) → (5 - i, 5 - j)` before applying the same Lucas test:

```ts
const SIERP_LO = (i, j) => {
  if (i + j < 5) return 0
  const ii = 5 - i, jj = 5 - j
  return ((ii & jj) === 0) ? 1 : 0
}
```

The circle packing is "tightly packed and fully touching". The first implementation used `radius = cell * 0.42`, which left a visible gap between adjacent circles. The user asked for the circles to touch. The fix is `radius = cell / 2`, which makes the diameter equal to the cell size, so adjacent circles are tangent at the shared cell edge:

```ts
const cell = 20
const r = cell / 2   // tightly packed: diameter = cell → adjacent circles touch
```

This plate is geometrically unrelated to the others, but it shares the project's discipline: the arrangement is a pure function of cell coordinates, the rendering is a pure function of the arrangement, and the verification is a pixel scan that classifies each sampled cell as black, orange, or background. Twenty-six cells were sampled across eleven arrangements; all matched the formula's prediction.

## Plate 5 and 6 — German prose and stacked headline

The fifth and sixth plates are typographically simpler than the first four, but they are the ones that were matched against two external reference images across nine comparison passes. They are worth treating together because the matching process produced most of the cross-cutting lessons.

The prose plate is a title (`Pythia und Konstruktion`) followed by a sixteen-line Paul Valéry quotation, set in a single uniform typeface — same family, same weight, same size for the title and the body. The title hugs the body with no paragraph break. The rag is left-aligned (the right edge is ragged, not justified). There is no first-line indent. The text contains German diacritics (ü, ä, ö, ß, é) and German typographic quotes (`„…"`), which are preserved verbatim from the reference.

The stacked-headline plate is five German-ish vocabulary words (`1Wort`, `fallen lassen`, `verlieren`, `aufgreifen`, `verpfänden`) set as five large centered lines. All five lines share one family, one weight, and one size. The line-height equals the size (`leading = 1.0`), so each line occupies a square line-box. The `1Wort` line is a fusion motif: no space between the digit and the word.

Both plates sit inside a square inner keyline border. The inner border is forced to 1:1 aspect by setting `InnerH = InnerW`. The whole composition is rendered on a beige card (`#fffdf6`) with a thin inner keyline at 0.5 alpha. There are no construction guides, no ink blocks, no sidebearing boxes. The plates are minimalist reading specimens.

The reason these two plates took nine passes to match is that the reference images used a paid neo-grotesk typeface (Univers or Helvetica), and the project could only load Inter from Google Fonts. Inter is a reasonable approximation of a neo-grotesk, but its diacritic shapes are rounder than Univers's flat shapes, and its stem thickness at a given nominal weight is slightly different. The matching process therefore had to converge on the parameters that made Inter look as close as possible to the reference, knowing that the diacritic-shape gap was irreducible.

The parameters that converged were: weight 400 (regular), size 24px for the prose and 100px for the headline, leading 1.15 for the prose and 1.0 for the headline (true squares), tracking +4px on the headline, ten-pixel margins, and a 0.5-alpha border. The numeric readout under each canvas showed the live values, so each pass could be verified by reading the numbers rather than eyeballing the screenshot. The final pass, compared by a fresh vision-language-model call with the full context re-established (because the VLM has no memory between calls), found that the only remaining differences were the font family and the diacritic shape — both unavoidable.

The `1Wort` fusion is implemented as a per-line toggle rather than a string substitution at definition time, so the live control can switch between `1Wort` and `1 Wort` and the canvas re-renders:

```ts
const lines = STACK_LINES.map((l, i) => (i === 0 && !state.fusion1Wort) ? '1 Wort' : l)
```

This is a small thing, but it captures a principle that recurs throughout the project: every typographic decision that the user might want to inspect should be a live knob, not a baked-in constant. The fusion is a knob. The square inner border is a knob. The leading is a knob. The principle pays off in the DSL design at the end.

## Plate 7 — The Swiss / NASA balloon plate

The seventh plate layers geometric composition on top of typography. It is a 5:7 portrait beige card with a Swiss modular grid: ten horizontal warm-gray hairline rules at 0.45 alpha, plus a central vertical axis. Two large circles are tangent to a shared horizontal rule — a brick-orange "balloon" disk above the rule and a near-black "payload" disk below it. A small brick-orange square (the "gondola") sits at the tangent line with a four-pane window, and five radial lines fan from the gondola to five points on the balloon's lower arc. A Swiss-style title sits at the top-left with a tonal step, and smaller labels anchor to lower grid rules.

The reference image is a dark-background Swiss poster with coral and near-black circles and white text. The project maps that palette to the Ruder beige card:

| Swiss poster | Ruder plate |
|---|---|
| dark gray-violet background | beige `#fffdf6` card surface |
| coral disk, gondola, strings | brick-orange `#c4621d` |
| near-black payload disk | ink-black `#1a1410` |
| white / very-light-warm-gray rules | warm-gray `#bfb7a5` at 0.45 alpha |
| white text | ink-black `#1a1410` |

The mapping is a first-class decision, not an afterthought. The plate is recognizable as the Swiss poster because the geometry and the tonal relationships survive the palette translation. The accent color moves from coral to brick-orange; the dark mass moves from the background to the payload disk; the white rules become warm-gray hairlines on beige. None of these changes breaks the composition because the composition is carried by the geometry and the tonal hierarchy, not by the specific hues.

The tangent between the two circles is the geometric heart of the plate. Both circles are tangent to the same horizontal grid rule: the balloon's bottom edge touches the rule from above, the payload's top edge touches the rule from below. The implementation places the tangent at a chosen grid rule index and computes each circle's center from its radius:

```ts
const tangentYabs = ruleY(state.tangentRuleIdx)
const coralCy = tangentYabs - coralR   // coral bottom = tangent
const blackCy = tangentYabs + blackR   // black top = tangent
```

The first implementation placed the tangent at the third rule from the top (index 2) and made the coral disk 380px in diameter. The coral's top edge landed at `tangentY - coralDiam = 166 - 380 = -214`, which is off the canvas. The disk was clipped. The fix was both to lower the tangent (from rule 2 to rule 4) and to shrink the coral (from 380 to 340), so that the coral's top edge lands at `362 - 340 = 22`, eight pixels inside the inner keyline. The lesson is that a tangent constraint and a radius constraint interact: moving the tangent down without shrinking the circle does not help, because the circle grows upward proportionally.

The title's tonal step was another lesson. The first implementation split the first line into two runs with different weights (`National` at 400, `Aeronautics and` at 300) on the same baseline. A stateless comparison against the reference flagged this as wrong: the reference's tonal step is between lines, not within a line. The whole first line is light 300; the whole second line is regular 400. The fix was to draw the first line as one run at 300 and the second as one run at 400:

```ts
ctx.font = titleFont(state.titleWeightLight)    // 300
ctx.fillText('National Aeronautics and', textX, y)
y += titleLineH
ctx.font = titleFont(state.titleWeightRegular)  // 400
ctx.fillText('Space Administration', textX, y)
```

The five balloon strings are drawn as radial lines from the gondola's top center to five points on the coral's lower arc, at math angles 235°, 248°, 260°, 292°, 305° measured from the coral center. The conversion from math angles (counter-clockwise from the positive x-axis) to canvas angles (clockwise from the positive x-axis, because y is down) is a sign flip:

```ts
for (const ma of mathAngles) {
  const ca = -ma * Math.PI / 180   // math angle → canvas angle
  const ex = coralCx + coralR * Math.cos(ca)
  const ey = coralCy + coralR * Math.sin(ca)
  ctx.beginPath(); ctx.moveTo(stringsTopX, stringsTopY); ctx.lineTo(ex, ey); ctx.stroke()
}
```

This plate is where the project learned that a palette mapping is a constraint, not a manual color table, and that a tangent is a constraint that interacts with the radii it connects. Both lessons reappear in the DSL.

## Interactive narrowing: state, schema, and re-render

Three of the plates — the prose, the stacked headline, and the NASA balloon — are driven by live slider controls. The control system is a single shared module that takes a mutable state object, a schema describing the controls, and a change callback:

```ts
export function mountControls(
  target: HTMLElement,
  state: Record<string, unknown>,
  schema: Control[],
  onChange: () => void,
): ControlPanel
```

The schema is a list of control descriptors. A range control has a key, a label, a min, a max, a step, and an optional unit and formatter. A select control has a key, a label, and a list of options. A checkbox has a key and a label. A reset button has a label and restores a snapshot of the state taken at mount time:

```ts
export type Control =
  | { kind: 'range'; key: string; label: string; min: number; max: number; step: number; unit?: string; format?: (v: number) => string }
  | { kind: 'select'; key: string; label: string; options: { value: string; label: string }[] }
  | { kind: 'checkbox'; key: string; label: string }
  | { kind: 'reset'; label: string }
```

Each plate declares its own state and schema. The prose plate exposes fourteen knobs: title size, body size, title leading, body leading, weight, indent, title-to-body gap, three margins, inner width, border alpha, the square-inner checkbox, and a typeface select. The stacked-headline plate exposes eleven knobs, including the `1Wort` fusion checkbox. The NASA plate exposes nineteen knobs, including the coral diameter, the black diameter, the tangent row, the gondola size, and the string count.

The render loop is the same for every plate. The state is a plain mutable object. Every control's input handler writes its value into the state and calls `onChange`, which is the plate's `reRender` function. `reRender` reads the state, rebuilds the canvas, and updates the numeric readout. There is no reactivity framework. The simplicity is deliberate: the state is serializable, the schema is declarative, and the render is a pure function of the state. A reset restores the snapshot and calls `reRender` once.

The typeface select is the one control that needs special handling, because changing the family requires loading the new font before re-rendering. The select's change handler is attached after `mountControls` returns, and it awaits `document.fonts.load` for the new family and the relevant weights and sizes before calling `reRender`:

```ts
familySelect.addEventListener('change', async () => {
  const preset = FONT_PRESETS.find((p) => p.id === familySelect.value) ?? FONT_PRESETS[0]
  state.familyPreset = preset.id
  state.family = preset.family
  try {
    const fontsApi = document.fonts
    await fontsApi.load(fontShorthandOf({ family: state.family, weight: state.weight, sizePx: state.size }), '1')
  } catch { /* fallback */ }
  reRender()
})
```

If the handler called `reRender` synchronously, the canvas would redraw with the fallback font for one frame, and the measurement would be wrong for that frame. The async load eliminates the flash and the wrong measurement.

## Failure modes

Three failure modes in this project are worth recording because they are not specific to typography and will recur in any canvas-heavy front-end work.

### Firefox closes the `<select>` popup when an ancestor has a positioned pseudo-element

After the interactive controls were added, the user reported that the typeface `<select>` dropdown no longer opened in Firefox. It opened in Chromium. The cause was the card's `::before` pseudo-element, which drew a decorative second border offset from the card:

```css
.card::before {
  content: "";
  position: absolute;
  inset: 0;
  border: 1px solid var(--frame);
  pointer-events: none;
  transform: translate(8px, 8px);
  opacity: 0.5;
}
```

The Mozilla bug (bugzilla 1440506, 1756514) is that a positioned pseudo-element on an ancestor of a `<select>` causes the native dropdown to close immediately when clicked. The `pointer-events: none` on the pseudo-element does not fix it. The fix that landed in Firefox 99 is not present in older versions, and the user's Firefox exhibited the bug. The workaround is to remove the positioned pseudo-element and express the decorative frame as a second `box-shadow` on the card itself:

```css
.card {
  box-shadow: 0 8px 32px rgba(120, 90, 40, 0.18), 8px 8px 0 0 rgba(214, 199, 164, 0.45);
}
```

A `box-shadow` is not a positioned pseudo-element and does not trigger the bug. The visual result is indistinguishable from the `::before` overlay. The lesson is that the canvas and the DOM share a page, and a CSS decision made for the card frame can break a DOM control that the canvas modules know nothing about.

### esbuild lowercases an uppercase constant at its usage site but not at its declaration

The prose module declared a constant `PROSE_LINES` and referenced it later as `PROSE_LINES.length`. The build succeeded. At runtime, the browser threw `ReferenceError: ProseLines is not defined`. The transpiled output declared `const PROSE_LINES = [...]` but referenced `ProseLines.length` — esbuild's token scanner had lowercased the identifier at the usage site but not at the declaration, producing a name that did not resolve.

The trigger appears to be the all-caps prefix. Renaming the constant to lowercase-first (`proseLines`) made the declaration and the usage both resolve to the same token, and the error disappeared. The same class of bug reappeared when an `import { FONT_PRESETS }` line was lost during an edit and the usage site threw `ReferenceError: FONT_PRESETS is not defined`; re-adding the import fixed it. The lesson is to prefer lowercase-first identifiers for module-level constants in this toolchain, and to verify imports survived every edit by reading the transpiled output, not just the source.

### A vision-language model has no memory and is unreliable at absolute pixel measurements

The nine-pass matching of the prose and headline plates was driven by a vision-language model comparing tight crops of the rendered canvas against the reference images. The model is good at relative judgments ("yours is heavier", "yours is looser") and bad at absolute pixel estimates ("the title is about 20px"). It also has no memory between calls: each comparison starts a fresh session with no knowledge of the previous passes, the fixes applied, or the project's goals.

The methodology that worked was to re-establish the full context in every call: what each image shows, what the prior passes fixed, what the only remaining gap is expected to be, the exact image ordering, and the specific axes to compare. With full context, the model's relative judgments were reliable enough to drive the convergence. Without context, the model invented mismatches (for example, misreading `aufgreifen` as `upgreifen` in one pass and then confirming the opposite in the next). The lesson is that a stateless comparison agent is a useful tool for narrowing typography, but only if every call is self-contained and the absolute measurements come from the code's numeric readout, not from the model.

## The ideal fluent DSL

By the time the seventh plate was built, the implementation had accumulated a recognizable shape: a mutable `state` object, a `schema` array, a `reRender` function, a `newCanvas` helper, a `drawCard` helper, a `drawHairline` helper, a `mountControls` call, and a typeface select with an async font-load handler. Every plate expressed its typography as canvas coordinates and font shorthand strings. The gap between the typography the user was trying to learn and the canvas the code was written in had become the project's main source of friction.

The natural design exercise, recorded in the repo as a design doc, is to invert the implementation. The DSL the project should have had speaks the typography domain directly. The same compositions expressed in the ideal DSL read as chains of typography concepts:

```js
// The three-line light→bold plate, in the ideal DSL
R.typography({ kind: 'weight-ramp', palette: 'ruder' })
  .family('Inter')
  .weightRamp([400, 700, 900])
  .size(140).leading(1.2)
  .tokens([['a','u','s'], ['b','il','d'], ['u','n','g']])
  .alignInk('left', 'center', 'right')
  .gap({ breath: 1.5 })
  .measure('ink-bounds', { via: 'canvas', fallback: { via: 'advance' } })
  .card({ border: true, borderAlpha: 0.5, margin: 10 })
  .render('#lines-weights')
```

The contrast with the implementation is the point. The implementation expresses the ink-bounds alignment as `x = -actualBoundingBoxLeft`, which leaks the `TextMetrics` field name and the offset arithmetic into the typography spec. The DSL expresses it as `.alignInk('left', 'center', 'right')`, which names the alignment intent and hides the measurement. The implementation expresses the weight ramp as `state.weights[lineIdx]`, which leaks the array indexing. The DSL expresses it as `.weightRamp([400, 700, 900])`, which names the ramp.

The DSL has eight design principles, each derived from a lesson in the implementation:

1. **One entry point, fluent builder, render terminator.** The pipeline is `R.typography(spec).<constraints>.render(target)`. Every constraint returns the builder. Only `.render()` does not chain.
2. **Domain vocabulary, not CSS vocabulary.** Methods are `.family`, `.weightRamp`, `.alignInk`, `.construction`, `.modularGrid`, `.tangent`, `.mapPalette`. There is no `.setTransform` or `.fillText` in the surface.
3. **Measurement-first, drawing-last.** `.measure('natural-width', { via: 'pretext' })` runs before the geometry is computed, so constraints can consume measured widths. Drawing is the single terminal `.render()` call.
4. **Constraints are live knobs.** Every constraint accepts a value or a bound and mounts a slider automatically via `.controls()`. This makes the "narrow the typography by dragging" intent first-class.
5. **Composition is declarative.** Each constraint is a pure specification of a typography axis. The renderer resolves it. There are no `if (squareInner) InnerH = InnerW` branches in the surface.
6. **Palette and palette mapping are first-class.** `.palette('swiss')` declares the source; `.mapPalette({ swissToRuder: { ... } })` maps it to the target card. The Swiss→Ruder mapping is a method, not a manual table.
7. **Construction guides, modular grids, and tangencies are geometry constraints.** `.construction({ cap, xHeight, descender, baseline })`, `.modularGrid({ rows, axis })`, `.tangent({ at: 'row 5', between: [disk, disk] })`.
8. **Alignment is ink-bounds-aware.** `.alignInk('left', 'right', 'center', 'baseline')` uses the ink bbox. `.alignBox(...)` is the advance-box fallback.

The DSL is a design doc, not an implementation. The runtime that lowers each constraint to canvas and Pretext calls is a future pass. The value of writing it down now is that it records the lessons of the seven plates in the form they should have taken: a typography vocabulary, not a canvas vocabulary.

## Working rules

The rules that fell out of this project, stated so they generalize beyond it:

- **Measure and draw through the same shaping engine.** If the measurement and the drawing can diverge, they will, and the divergence will be a font-fallback or a kerning difference that no manual correction fully removes. A single canvas with a single font shorthand is the simplest target that guarantees parity.
- **Wait for the font before measuring.** `document.fonts.ready` is not enough; load the specific weight and size with `document.fonts.load(shorthand, sample)` and await it. Measuring the fallback measures the wrong font.
- **Prefer ink-bounds alignment over advance-box alignment for visible edges.** `textAlign='left'|'right'|'center'` is fine for running text. It is wrong for columns of large display glyphs, because side bearings are visible at display sizes. Offset by `actualBoundingBoxLeft` and `actualBoundingBoxRight`.
- **Draw construction guides from one weight; draw ink from each weight.** The construction is invariant across weights. The ink is not. A specimen that wants to teach the difference draws the guides once and lets the ink grow.
- **Make every typographic decision a live knob.** If a parameter was worth tuning by hand across nine passes, it is worth exposing as a slider so the next person can tune it without editing code. The state-plus-schema pattern keeps the knobs declarative and the render pure.
- **Re-establish full context for every stateless comparison.** A vision model with no memory will invent mismatches if the context is thin. Put the image ordering, the prior fixes, the expected remaining gap, and the specific axes in every call. Trust relative judgments; distrust absolute pixel estimates.
- **Speak the domain, not the implementation.** When the implementation vocabulary (`ctx.font`, `actualBoundingBoxLeft`, `InnerH = InnerW`) has leaked into the spec, the spec is harder to read and harder to teach than it needs to be. The DSL exercise is the discipline that surfaces the leak.

## Related notes

- [[ARTICLE - Pretext Print Layout - Building a Swiss Typography Rendering System for Dense Programming Reports|Pretext Print Layout]] — the upstream article on Pretext as a fast DOM-free measurement library and the Swiss typography system for dense reports. This article is the canvas-rendering counterpart: where that article measured for pagination and let CSS render, this one measures for alignment and draws on canvas directly.
- [[ARTICLE - Constraint-Based Layout on Canvas - Cassowary + Pretext + React|Constraint-Based Layout on Canvas]] — the upstream article on Cassowary constraint solving with Pretext measurement on canvas. The iterative solve-measure loop in that article is the general case of the measurement-drawing parity discipline in this one.
- The project repository: `/home/manuel/code/wesen/2026-06-16--learn-grids-2/ruder/`
- The ideal DSL design doc and seven worked examples: `/home/manuel/code/wesen/2026-06-16--learn-grids-2/ttmp/2026/06/19/RUDER-TYPOGRAPHY-DSL/ruder-typo-dsl/`
- The docmgr tickets for the project: `/home/manuel/code/wesen/2026-06-16--learn-grids-2/ttmp/2026/06/18/` (`RUDER-PRETEXT-VOWELS` and `RUDER-6X6-ARRANGEMENTS-GALLERY`)

## Open questions

- **Is the DSL worth implementing?** The design doc is comprehensive but the runtime does not exist. The seven plates took roughly one session to build in the canvas vocabulary. Implementing the DSL and migrating the plates to it is a separate project, justified only if more plates are planned or if the plates need to be maintained by someone who does not want to learn the canvas vocabulary.
- **Can the ink-bounds alignment be made robust against browsers without `actualBoundingBox*`?** The current fallback collapses to advance-box alignment, which is visibly wrong for display sizes. A pixel-scan fallback that reads the rendered glyph's ink bbox from an offscreen canvas would restore ink-bounds alignment on those browsers at the cost of one `getImageData` call per token.
- **Does the measurement-drawing parity hold under sub-pixel transforms?** The project uses `setTransform(dpr, 0, 0, dpr, 0, 0)`, which scales by an integer at `dpr = 2` and by a non-integer at fractional DPRs. The pixel scans were done at `dpr = 1`. Whether the parity holds exactly at fractional DPRs, or only approximately, has not been measured.
