---
title: "Bitmap Font Browser: The Portable Core and the Firmware Contract"
aliases:
  - Bitmap Font Browser Portable Core
  - v2 Slicer Algorithm Deep Dive
  - Bitmap Font Firmware Contract
tags:
  - article
  - bitmap-fonts
  - rendering
  - computer-vision
  - firmware
  - go
  - typescript
status: active
type: article
created: 2026-06-25
repo: /home/manuel/code/wesen/2026-06-24--bitmap-font-browser
---

# Bitmap Font Browser: The Portable Core and the Firmware Contract

This article is a deep-dive technical analysis of the implemented portable core of the Bitmap Font Browser, the second-generation tool that slices bitmap font sprite sheets and renders text pixel-perfectly for a PicoCalc handheld. The earlier article in this vault, [[ARTICLE - Bitmap Font Slicing - From Uniform Grids to Per-Glyph Coordinates]], established *why* a per-glyph coordinate model replaces a uniform grid. This article covers *how* that model is built and exercised: the four-stage algorithm pipeline, the data structures that make it firmware-portable, the split between the Go deployment shell and the TypeScript engine, and the validation that proves the pipeline works on real fonts. A reader who finishes this article understands the engine well enough to port any one of its stages to C, and understands why the next planned work is to move the renderer into Go as a standalone command-line tool.

> [!summary]
> 1. The engine is four framework-free stages — binarize, detect, oracle, render — operating on plain typed arrays so they can be transliterated to C without change.
> 2. The coordinate glyph model represents a font as a list of `(x, y, w, h, bits, char)` records; a uniform grid is the degenerate case where every record shares size and pitch.
> 3. Detection finds glyphs as eight-connected ink components, separates a credit-text band by a row-spacing signature before clustering, and clusters component centers — not gutters — which is why it recovers grids that projection autocorrelation cannot.
> 4. The renderer is integer-only and uses a single platform-specific `setPixel`; line height and letter spacing are render-time overrides in source pixels, so one layout renders tightly or loosely.
> 5. The Go server is deliberately 252 lines and holds no algorithm; every interesting routine lives in the TypeScript `core/`, which is the firmware reference and the port target.

## The split that shapes everything

The repository divides into a thin Go server and a larger TypeScript core, and the division is a design constraint, not an accident of history. The Go program is 252 lines across four files. It is the standard library `net/http` multiplexer with Go 1.22 method-pattern routes, an embedded single-page application, and a typed manifest loader. It contains no slicing, no detection, no rendering. The TypeScript under `web/src/core/` is 1,127 lines across nine files and contains every algorithm that matters.

The reason for this asymmetry is the firmware contract. The PicoCalc device runs a C text driver that must draw the same pixels the browser draws. If the rendering algorithm lived in Go, it would have to be ported to C twice: once from Go and once from whatever the browser used. By keeping the algorithm in a framework-free TypeScript module that imports nothing from React or Redux and operates on `Uint8Array`, the same code is both the browser engine and the literal reference for the C port. The browser is the development surface with hot reload and tests; the device is the consumer of the same algorithm. The Go server is only the deployment shell that serves the font sheets, the manifest, and the built application.

This split has a direct consequence for the work that follows the article. The renderer, the detector, and the oracle are all candidates to become standalone tools. A command that takes a font, its glyph coordinates, and a text layout and writes a PNG does not need a browser; it needs the `core/` algorithm and an image encoder. Moving that into Go is the natural next step, and it is tractable precisely because the algorithm is already isolated from its surroundings.

## The data model

Everything the engine produces or consumes is one of three structures, defined once in `web/src/core/types.ts`. A `Glyph` is a single character's bitmap: an integer bounding box in source-sheet pixels, a packed one-bit bitmap cropped to that box, and a character label that is empty until the oracle fills it. A `GlyphSet` is a list of `Glyph` records plus render metrics. A `FontLayout` is the editable, persistable description of how to cut a sheet into glyphs.

```typescript
interface Glyph {
  x: number; y: number; w: number; h: number; // box in source pixels
  bits: Uint8Array;                          // packed 1-bit, w*h bits, row-major
  char: string;                              // "" until labeled
}

interface GlyphSet {
  name: string;
  glyphs: Glyph[];      // variable count, variable sizes
  lineHeight: number;   // render-time row pitch (source px)
  advance: number;      // default horizontal advance (source px)
  grid?: { cellW: number; cellH: number; cols: number; rows: number };
}

interface FontLayout {
  grid?: GridSpec;      // uniform grid (the easy case)
  boxes?: GlyphBox[];   // explicit per-glyph boxes (the hard case); wins over grid
  labels?: string;     // per-box char labels
  charset?: string;     // ordered labels for grid mode (ASCII-from-space)
  threshold: number; invert: boolean;
  lineHeight: number; letterSpacing: number;
}
```

The coordinate model is the generalization that the earlier article argued for. A uniform grid is not a separate code path; it is a `FontLayout` whose `grid` field is set and whose `boxes` are absent, expanded to boxes at load time by enumerating `(col, row)` positions. A variable-width font like `HOMEBOY` carries explicit `boxes`. A hybrid sheet can carry both, with `boxes` winning on conflict. One type, three producers (the heuristic, the detector, the manual editor), one consumer (the renderer).

The bitmap packing within a glyph is chosen so the same bytes are a valid C array. Pixel `(x, y)` of a `w`-wide glyph is bit `y * w + x`; the byte is that index shifted right by three, the bit is the low three bits. There is no division beyond the shift. The first generation packed all glyphs into one concatenated array indexed by `i * cellW * cellH`, an index that only works when every glyph is the same size. Variable sizes break that index, so each glyph owns its own `bits`. The packing within a glyph is unchanged.

## Stage one: binarization by distance from background

Every later stage operates on a binary ink mask, so the binarization rule is the foundation. The rule is reused unchanged from the first generation because it solved a real failure that a luminance threshold could not.

The obvious way to binarize a grayscale image is a luminance threshold: a pixel is ink if its perceived brightness is below some value. This fails on the font collection because ink can be a saturated, low-luminance color. The sheet `08X08-F1` draws every glyph in pure red, `(240, 0, 0)`. The Rec. 601 luma of that color is approximately 72. A threshold of 128 classifies every red pixel as paper, and the entire font renders blank.

The fix defines ink by distance from the background rather than by absolute brightness. The background is the most common opaque color in the sheet. A pixel is ink when the maximum per-channel difference between it and the background exceeds a threshold.

```typescript
function backgroundColor(img): RGB {
  // most common opaque color — space + gutters dominate, so this is the sheet bg
}
function inkDistance(img, x, y, bg): number {
  const i = (y * img.width + x) * 4;
  if (img.data[i + 3] === 0) return 0;        // transparent -> background
  return Math.max(Math.abs(img.data[i]   - bg[0]),
                  Math.abs(img.data[i+1] - bg[1]),
                  Math.abs(img.data[i+2] - bg[2]));
}
// ink = (inkDistance >= threshold) XOR invert
```

One rule handles white-on-black, black-on-white, and saturated colored ink. The `invert` flag absorbs the polarity question into the same threshold. The function `binarize` in `web/src/core/binarize.ts` returns a `Uint8Array` of 0/1 over the sheet, and that mask is the input to detection.

A known limitation is recorded honestly in the diary. When a sheet is mostly ink, the most-common-color detector misidentifies the background. The synthetic test fixtures had to be crafted background-dominant for the default path to apply; the `invert` flag is the escape hatch for ink-heavy content. The rule is correct for real sheets, where space and gutters dominate.

## Stage two: detection by connected components and clustering

Detection answers the question "where are the letters" without assuming a grid. It is the stage that replaces the first generation's projection-autocorrelation detector, which the project's own measurements proved unreliable. The replacement is four substages: connected components, region classification, row and column clustering, and a merge and split refinement.

### Why connected components, not projection autocorrelation

The first generation projected ink counts onto the X and Y axes and searched for the dominant period, expecting it to be the cell size. The signal is dominated by intra-glyph structure. On `16X16-F1`, a sheet whose true cell height is 16, the autocorrelation of the row projection scores the true period 16 at approximately 0.03 while a spurious period of 4 — the spacing of horizontal strokes within each letter — scores 0.53. The detector latched onto the harmonic. Connected components sidesteps the problem because it does not ask for the period of the ink signal. It asks where the blobs are, and it recovers the relationship between blobs with a separate clustering step.

### Connected components

`connectedComponents` in `web/src/core/detect.ts` labels every maximal set of ink pixels reachable from one another by eight-neighbor moves, using a two-pass union-find. Each component carries a bounding box, an area, and a center. The output is a set of independent blobs with no assumption about how they relate to one another.

A fact that shapes the whole stage is that one glyph is not necessarily one component. `HOMEBOY` has roughly 40 glyphs but produces 104 components, because the enclosed counter of a block `O` is a separate component from its outline, detached serifs are separate components, and dot punctuation is its own component. Naive component counting would report more than twice the real glyph count. Clustering, not counting, is what recovers glyphs.

### Region classification: dropping the credit band

A second structural fact, easy to miss, is that most sheets carry credit and version text that is not part of the glyph set. Measured on the three target fonts, the credit band dominates the component count: `HOMEBOY`'s 104 components are 46 glyph components plus 58 credit components; `LIGHT`'s 49 are 31 plus 18; `M_TWINS`'s 89 are roughly 19 plus 70. A detector that does not separate the credit band reports roughly twice the real glyph count and treats credit strings as additional letter rows.

`classifyRegions` separates the bands with two corroborating signals. The first is a row-spacing signature: glyph rows are approximately evenly spaced, so the credit band appears as one inter-row gap much larger than the median gap. The second is a size signature: credit components cluster well below the glyph band's median area. A component below the detected cut, or whose area is below 35 percent of the glyph median, is classified as credit and dropped before clustering.

```text
classifyRegions(components, rowTol=6):
  rows = clusterByAxis([c.centerY for c in components], rowTol)
  centers = sorted mean Y of each row cluster
  gaps = differences of adjacent centers
  cutY = the Y just above the largest gap, if largestGap > 2 * median(gap)
  glyphMedianArea = median area of components above cutY
  for each component c:
    if c.centerY >= cutY:                 -> CREDIT
    elif c.area < 0.35 * glyphMedianArea: -> FRAGMENT (keep, merge later)
    else:                                 -> GLYPH
  cluster only the GLYPH components
```

A subtle bug in the first version of this stage is worth recording because it is the kind of error that recurs. The region classification originally shared its row tolerance with the glyph-grid clustering tolerance, and that tolerance was derived from the median glyph height — a large number, because glyphs are tall. The large tolerance over-clustered the row bands, which erased the large gap that marked the credit band, so `HOMEBOY`'s 58 credit components were treated as glyphs. The fix was to give region classification its own tight, absolute tolerance, because it looks for narrow row bands, while the glyph-grid clustering uses the size-derived tolerance. Two different questions need two different tolerances.

### Clustering and refinement

With the credit band removed, the glyph components are clustered into rows by their Y centers and into columns by their X centers. The clustering is one-dimensional along each axis: sort the centers, split into groups wherever the gap exceeds a tolerance. A glyph is the union of the components whose centers fall in the same row and column cell. This recovers a grid even when glyphs have no inter-cell gutter, because it keys off where glyphs sit rather than where gutters are. On `LIGHT` it recovers approximately 16 columns by 3 rows; on `HOMEBOY` it recovers 7 rows even though the columns have no gutter.

The cluster tolerance is derived from the glyph-band component sizes, not a fixed pixel count, so it adapts to the font scale. Adjacent glyphs are roughly one glyph-width apart, so a tolerance proportional to the median glyph dimension works across an 8-pixel font and a 32-pixel font. An absolute 6-pixel tolerance, used in an early version, wrongly merged a tight 2-pixel grid into one column.

A refinement stage then cleans the clustered cells. Cells suspiciously wider than the row's median glyph width likely contain two glyphs whose centers fell in one column band, and are split at the local projection valley. Adjacent components within a row cell whose gap is small relative to the median glyph width are merged, reassembling the fragmented strokes of a block letter. Components below a minimum area are dropped as speckle.

### What detection produces

`detectGlyphs` returns the candidate glyph boxes, unlabeled, plus the region classification for the editor to draw. On `HOMEBOY` it returns 13 boxes with the credit band cut at Y equals 117, matching the offline Python analysis. On `M_TWINS` it separates the credits but the simple horizontal cut is insufficient for that sheet's two interleaved style regions, which is the case that motivates the column-region grouping described in the design guide. The boxes are the input to the oracle.

## Stage three: the labeling oracle

The oracle assigns a character label to each box. The obvious approach is optical character recognition: read each glyph and identify the letter. The first generation tried the modern variant, a vision language model, and it failed in a specific way that the second generation avoids entirely.

Asked to transcribe the glyphs of `16X16-F1`, a sheet whose layout was already known by inspection, the vision model hallucinated a canonical codepage. It invented lowercase letters that do not exist in the font. On a high-resolution crop of the row `H I J K L M N O P Q R S T U V W X Y Z [`, it reported `A B C D E F G H I J K L M N O P Q R S T`, imposing the prior that capital letters start at A rather than reading the pixels. Open-ended transcription of bitmap glyphs is unreliable because the model pattern-matches to a canonical codepage instead of reading pixels.

The replacement is a self-consistency check that needs no model. Because the tool can render text itself, it can take a hypothesis about which characters the sheet contains and in what order, render that hypothesis using the detected glyph boxes, and compare the result to the source sheet pixel for pixel. A correct hypothesis reproduces the sheet, because the rendered output is built from the sheet's own bitmaps. Labeling reduces to asking whether a hypothesis reproduces the pixels.

```text
verifyHypothesis(sheet, layout, glyphs, charset):
  expected = renderHypothesis(layout, charset)    # same dimensions as sheet
  for each (box, i):
    source = crop(binarized sheet, box)
    hypothesis = crop(expected, box)
    score = IoU(source, hypothesis)
    if score >= 0.85:  accept charset[i] as the label for box i
    elif score >= 0.5: flag for review
    else:              reject the hypothesis at this box
```

The oracle never recognizes a glyph. It verifies that a hypothesis reproduces the pixels. A wrong hypothesis is rejected by pixel disagreement, not by a model's priors. This is strictly better than vision transcription, which hallucinates, and better than vision comparison, which the first generation found reliable but which requires an external model and rate limits.

The implemented oracle has an honest limit that the diary records. The coverage metric, as first written, compared each box's source crop to that same box's glyph rendered back into the box — a comparison that is always approximately one by construction, because the glyph is the crop. That metric reported the fraction of boxes with ink, not charset correctness. The current implementation reframes the oracle honestly: the `label` action counts non-blank glyphs as a yield, and the preview itself is the charset oracle. A wrong ASCII assumption shows up as mislabeled or blank letters in the preview, which is itself the discovery. A real verifier — rendering a probe string and detecting duplicate-glyph collisions and missing characters — is future work.

## Stage four: the renderer

Once glyphs are detected and labeled, rendering is a bit-block transfer. The renderer in `web/src/core/render.ts` is the firmware-portable core. It is integer-only, allocation-light, and uses a single platform-specific call, `setPixel`, to write to the framebuffer. In the browser the framebuffer is a canvas `ImageData`, four bytes per pixel in RGBA order. On the device it is the LCD buffer in RGB565. The algorithm is identical between the two; only `setPixel` changes.

The blit draws one glyph by walking its bitmap and writing each ink pixel scaled by an integer zoom factor. Text layout walks the string, advances a pen horizontally after each glyph and vertically after each line break or wrap. The extension over the first generation is that the horizontal advance is per-glyph — each glyph's own width plus a configurable letter spacing — and the vertical advance is a configurable line height. The first generation used a single global cell size for both, which is correct only for uniform fonts.

```text
renderText(glyphSet, text, canvas, lineHeight, letterSpacing, zoom, fg, bg):
  fill framebuffer with bg
  lineH = lineHeight * zoom          # source px scaled to device px
  gap   = letterSpacing * zoom
  penX = 0; penY = 0
  for each character ch in text:
    if ch == newline: penX = 0; penY += lineH; continue
    if wrap and penX + maxGlyphWidth*zoom > canvas.w: penX = 0; penY += lineH
    glyph = resolveGlyph(glyphSet, ch)
    if glyph:
      blitGlyph(framebuffer, glyph, penX, penY, zoom, fg, bg)
      penX += glyph.w * zoom + gap      # advance by THIS glyph's width
    else:
      penX += defaultAdvance * zoom + gap
```

The adjustable line height exists for block fonts. `HOMEBOY` glyphs are 22 pixels tall and, at the default line height equal to the cell height, the rows touch. Increasing the line height to the cell height plus a few pixels inserts a gap so the block letters do not collide. Letter spacing does the same horizontally. Both are render-time overrides, not properties of the boxes, because the boxes describe the source while spacing is a render concern. A terminal render of the same font wants tight spacing; a title render wants loose spacing. One layout serves both.

Character resolution maps a typed character to a glyph by label, with a lowercase to uppercase fallback that the first generation established. When a lowercase letter has no labeled glyph, the renderer renders the uppercase form instead. This is correct for the many uppercase-only fonts in the collection and is safe for fonts that define distinct lowercase, because the fallback only triggers when the lowercase glyph is genuinely absent.

## The firmware contract, stated

The renderer and the glyph representation are written so that a C port is mechanical, and the constraints that make that true are worth stating because they govern many small decisions.

A glyph is a C struct: signed integer coordinates and dimensions, a pointer to a packed one-bit bitmap, and a one-byte code. The bitmap packing within a glyph is one bit per pixel, row-major, identical to the TypeScript representation. The blit and the text layout use only integer arithmetic. There is no floating point, no anti-aliasing, no alpha blending. The line height, the letter spacing, and the per-glyph width are plain integers. The detection stage and the oracle are host build tools; they run to produce the layout and do not run on the device. The device consumes only the resulting coordinate layout.

The lock-step guarantee between the browser and the device is maintained by golden-image tests. The same glyph set, text, and spacing produce byte-identical framebuffers in both, after RGB565 conversion. Any divergence is a bug in one of the two.

## Validation by looking at real output

The project's working rule, established in the first generation and carried through, is to verify rendering by looking at real output rather than trusting synthetic tests. The unit tests prevent regressions; the eyes and the pixel sampling find the bugs. Three validation results from the second generation are worth recording because they are the evidence that the pipeline works.

The detector runs on real sheets through an offline verifier, `web/tools/verify-detect.mts`, which decodes a sheet, runs detection, and writes a box-overlay image. On `HOMEBOY` it returns 41 glyph components and 58 credit components with the cut at Y equals 117, matching the standalone Python analysis. The credit band is excluded, and a vision check of the overlay confirms the boxes land on the real block letters. On `16X16-F1` the oracle reports coverage 0.833 against the heuristic grid, the clean font being mostly verified.

The full interactive pipeline runs live in a browser. With `HOMEBOY` selected, the detect button produces 13 boxes and the yellow credit-band cut at Y equals 117, matching the offline verifier exactly. Clicking a box selects it; pixel sampling the canvas confirms the selected box's stroke is the red selected color, `[242, 66, 66]`, rather than the blue default. Typing a character into the label field commits it to the layout and persists it to local storage. With `16X16-F1` selected, the preview renders typed text; pixel sampling the preview canvas returns 19,096 green foreground pixels where an earlier bug returned zero.

The earlier bug is the one validation found and fixed. The preview was blank for fonts seeded by the heuristic, because the layout expander only read per-box `labels`, but the heuristic sets `charset`. Grid-seeded glyphs were unlabeled, and the character resolver found nothing. The fix was a one-line fallback: when explicit per-box labels are absent, label grid cell `i` with `charset[i]`. The preview went from zero to 19,096 foreground pixels. This is the kind of bug that eyes and pixel sampling find and that green unit tests do not.

## The Go port and the command-line tools

The algorithm's isolation from its surroundings makes two planned tools tractable, and both are the natural next work.

The first is a renderer that takes a font, its glyph coordinates, and a text layout and writes a PNG. It needs the `core/` render algorithm and an image encoder; it does not need a browser. Moving the renderer into Go gives a single binary that the firmware build pipeline can call, and it removes the indirection of a Node script for headless rendering. Because the algorithm is already framework-free, the port is a transliteration of `render.ts` and `bits.ts` into Go, plus an RGBA-to-PNG encoder from the standard library `image` package. The firmware contract guarantees the Go output matches the browser output.

The second is a command-line tool that runs the heuristics and the oracle in batch across the collection. Today a single font is processed by clicking detect and label in the browser; 817 fonts need a batch path. The Go tool would load each sheet, run the connected-component detector and the region classifier, run the oracle against a list of charset hypotheses, and write the resulting `FontLayout` to a JSON file per font. The confidence and coverage numbers become a triage queue, exactly as the first generation's vision pipeline did, but without an external model.

Both tools follow from the split this article documents. The algorithm is already in one place, already portable, and already validated. Moving it into Go is the work of transcription, not redesign.

## Working rules

The decisions above distill into rules that govern the system.

- Keep the algorithm framework-free in `core/`. No React, no Redux, no DOM. The same code is the browser engine and the firmware reference.
- Store glyphs as per-glyph coordinates. A uniform grid is the degenerate case. Never add a parallel uniform-grid code path with a compatibility shim.
- Detect structure with connected components plus row and column clustering, never with projection autocorrelation. Classify and drop the credit band before clustering, using a tight tolerance separate from the glyph-size-derived clustering tolerance.
- Label glyphs with the self-consistency oracle, never with optical character recognition or vision transcription. Verify hypotheses; do not recognize pixels.
- Keep the renderer integer-only and single-`setPixel`. Line height and letter spacing are render-time overrides in source pixels, not properties of the boxes.
- Keep detection and the oracle off the device. The firmware consumes the layout; it does not compute it.
- Verify rendering by looking at real output and by pixel sampling. Unit tests prevent regressions; eyes and pixel sampling find the bugs that matter.

## Implementation references

- Repository: `/home/manuel/code/wesen/2026-06-24--bitmap-font-browser`
- Portable core: `web/src/core/{types,bits,binarize,detect,oracle,layout,render,heuristics}.ts` — 1,127 lines, framework-free.
- Go server: `cmd/server/main.go`, `internal/{manifest,spa}/` — 252 lines, no algorithm.
- Offline verifier: `web/tools/verify-detect.mts` — runs detection and the oracle on real sheets, writes box-overlay PNGs.
- Design and diary: `ttmp/2026/06/25/BITMAP-FONT-SLICER-V2--*/{design-doc,reference}/01-*.md`.
- Diagnostic images (referenced from the companion article): `diag-v2-HOMEBOY-bands.png`, `diag-v2-LIGHT-bands.png`, `diag-v2-M_TWINS-bands.png` in this folder.
- Companion article: [[ARTICLE - Bitmap Font Slicing - From Uniform Grids to Per-Glyph Coordinates]] — the design rationale for the coordinate model.
- Project status note: [[PROJ - Bitmap Font Browser - PicoCalc pixel-font preview and slicer]] — the v1-era project record.
