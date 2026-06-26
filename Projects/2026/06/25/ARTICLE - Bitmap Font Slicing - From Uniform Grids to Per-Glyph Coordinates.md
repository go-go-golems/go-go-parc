---
title: "Bitmap Font Slicing: From Uniform Grids to Per-Glyph Coordinates"
aliases:
  - Bitmap Font Slicer v2 Deep Dive
  - Coordinate-Based Glyph Model
tags:
  - article
  - bitmap-fonts
  - rendering
  - computer-vision
  - go
  - react
  - redux
  - firmware
  - cli
  - parity
status: active
type: article
created: 2026-06-25
repo: /home/manuel/code/wesen/2026-06-24--bitmap-font-browser
---

# Bitmap Font Slicing: From Uniform Grids to Per-Glyph Coordinates

This is a deep-dive technical analysis of a second-generation bitmap font slicer. The first generation assumed every glyph in a font sprite sheet sat on a single uniform grid. That assumption covers most of a collection of 817 retro bitmap fonts, but it breaks for the fonts that matter most: variable-width block fonts, sparse irregular grids, and sheets that pack two distinct typefaces into one image. The second generation replaces the uniform grid with a per-glyph coordinate model and recovers those coordinates automatically with connected-component analysis. It then labels each glyph by character using a technique that needs no optical character recognition and no machine-vision model: it renders text itself and compares the result to the source sheet, pixel for pixel.

The article explains why the uniform-grid model fails, how connected-component analysis recovers glyph structure, why credit-text bands must be separated before clustering, and how a self-rendering oracle labels glyphs without recognition. It covers the renderer's adjustable line height and letter spacing, the firmware-portability contract, and the visual design system for the editing tool. The reference implementation is the PicoCalc Bitmap Font Browser. Its rendering core was written first in framework-free TypeScript as the portable reference; that core has since been transliterated to Go and is now the primary command-line renderer and batch analyzer, with a third in-browser JavaScript port driving an interactive gallery. The three implementations are kept in lockstep because they are all transliteration targets for the same future C firmware.

> [!summary]
> 1. A uniform `cellW × cellH` grid cannot represent variable-width or multi-region fonts; a per-glyph `(x, y, w, h)` coordinate list is the general model, and a uniform grid is its degenerate case.
> 2. Connected-component analysis with row/column clustering recovers glyph structure that projection-autocorrelation cannot, because it keys off where glyphs sit rather than the periodicity of ink density.
> 3. Credit and version text often dominate a sheet's component count; it must be classified into a separate band and dropped before clustering, or the detector invents roughly twice as many glyphs as exist.
> 4. The self-rendering oracle is a sound *idea* — verify a charset hypothesis by rendering it and diffing against the sheet — but the shipped implementation compares each box to its own source glyph, so its coverage metric collapses to "fraction of boxes that captured ink" (a layout-alignment signal), not charset correctness. Labels remain a hypothesis until a human confirms them.
> 5. The algorithm now exists in three languages (TypeScript, Go, JavaScript) that must agree pixel-for-pixel. That three-way parity is the firmware-portability contract: any of the three can be the reference for the C port, and divergence between them is a bug.

## Why this note exists

This note preserves the reusable engineering knowledge from redesigning a bitmap font slicer. The triggering project is a font-preview tool for a text-oriented operating system running on a PicoCalc handheld (a 320×320-pixel display). But the patterns generalize: any system that ingests inconsistently-structured raster sprite sheets, any system that must label glyphs at scale without OCR, and any renderer meant to be ported from a managed language to firmware will hit the same decisions. The note is written so a future reader can rebuild the system from the reasoning alone.

## The input: what a bitmap font sheet actually is

A bitmap font is not stored as outlines. It is stored as a raster image — a PNG — containing many glyphs arranged in a grid. The collection in question comes from the `ianhan/BitmapFonts` repository: 817 PNG sheets. Most are 320 pixels wide. Each pixel is either ink or paper after binarization, and the firmware stores each glyph as a packed one-bit-per-pixel bitmap. There is no outline, no hinting, no anti-aliasing in the stored representation. This simplicity is the whole reason a firmware text driver can use them: a glyph is a block of bits, and rendering is a bit-block transfer.

The dominant layout is a uniform grid. A sheet is divided into `cols × rows` identical cells of size `cellW × cellH`, filled row-major with glyphs in ASCII order starting at the space character (`0x20`). Unsupported characters are simply left blank. This is the layout of a classic BIOS codepage, and it is what the first-generation slicer assumed.

```text
16X16-F1.png  →  320 × 48 px,  cell 16×16  →  20 cols × 3 rows = 60 glyphs

         col0   col1   col2   col3  ...        col19
        +------+------+------+------+   ...   +------+
 row0   | 0x20 | 0x21 | 0x22 | 0x23 |   ...   | 0x33 |   space ! " # ... 3
 row1   | 0x34 | ...                                 |   4 5 6 7 8 9 : ; ...
 row2   | 0x48 | ...                                 |   H I J K ...

codepoint(col, row) = firstCodepoint + row*columns + col
```

## Where the uniform grid assumption breaks

The uniform-grid model works when three conditions hold simultaneously: every glyph occupies the same cell width, every glyph occupies the same cell height, and the cells tile the sheet on a single row-and-column pitch with no overlap. The first-generation heuristic guessed the cell size from the filename (a token like `16x16`) or from the largest common divisor of the image dimensions, and it covered roughly 85 percent of the collection. The remaining 15 percent need manual correction, which is tolerable. But three specific fonts cannot be represented by the model at all, no matter what cell size is chosen, because the three conditions do not hold.

The clearest failure is visible rather than statistical. When the heuristic's 8×8 grid is overlaid on `HOMEBOY`, the cells slice through the middle of large block letters:

![The first-generation uniform 8x8 grid overlaid on HOMEBOY. The cells are far too small and cut through large variable-width block letters, demonstrating that a single cell size cannot tile this sheet.](v1-grid-homeboy.png)

The same heuristic applied to a clean uniform font lands every cell boundary exactly on a glyph boundary:

![The first-generation uniform 16x16 grid overlaid on 16X16-F1. Every cell aligns cleanly with a glyph. This is the case the model was designed for.](v1-grid-clean.png)

The difference between the two images is the entire motivation for a new model. `HOMEBOY` has variable-width glyphs with no inter-column gutter and with strokes that fragment into multiple disconnected blobs. `16X16-F1` has uniform glyphs on a clean grid. Any single cell size chosen for `HOMEBOY` either clips the wide letters or merges two adjacent letters into one cell. The problem is structural, not a matter of tuning the heuristic.

The measured component data confirms this across the three target fonts. All three are 320×200, 8-bit palette, black background. Connected-component analysis (eight-connectivity) on the binarized ink mask produces these counts:

| Font | Total components | Glyph-band components | Credit-band components | Glyph-band median size |
|------|-----------------:|----------------------:|-----------------------:|-----------------------:|
| HOMEBOY | 104 | 46 | 58 | 29×22 |
| LIGHT | 49 | 31 | 18 | 15×13 |
| M_TWINS | 89 | ~19 | ~70 | 13×13 |

Two facts jump out of this table, and each drives a part of the design. First, the total component count is not the glyph count: `HOMEBOY` has 104 components but roughly 40 glyphs. Second, the majority of components are not glyphs at all — they are credit text, addressed in the next section.

## The per-glyph coordinate model

The replacement for the uniform grid is a list of independent glyph records. Each record carries a bounding box in source-sheet pixels — `x, y, w, h` — plus the cropped one-bit bitmap for that box, plus the character label once it has been determined. There is no global cell size. A uniform grid is the special case in which every box shares the same width and height and is placed at `(col * (w + gap), row * (h + gap))`.

```go
type Glyph struct {
    X, Y, W, H int
    Bits       []byte  // packed 1-bit bitmap, w*h bits, row-major; byte i>>3, bit i&7
    Char       string  // label; "" until the oracle fills it
}

type GlyphSet struct {
    Name       string
    SrcW, SrcH int
    Glyphs     []Glyph
    LineHeight int  // render-time row pitch (source px)
    Advance    int  // default horizontal advance (source px)
}
```

The choice to store a `bits` array per glyph rather than one concatenated atlas is forced by variable sizes. The first generation packed all glyphs into a single array indexed by `index * cellW * cellH`, an index that only works when every glyph is the same size. Variable sizes break that index, so each glyph owns its own bits. The packing within a single glyph is unchanged from the first generation: one bit per pixel, row-major, byte `i >> 3`, bit `i & 7`. This matters because it keeps the firmware port mechanical — the asset baker emits one C struct plus one bitblob per glyph, the same layout as the BDF and PCF bitmap font formats.

This representation is deliberately a superset of the first generation's. It does not preserve a separate uniform-grid code path with a compatibility shim. A uniform grid is constructed by listing boxes at grid positions. Collapsing two old configuration concepts (a slicing config and an overrides file) into one layout document is a consequence of the same generality.

## Binarization: detecting ink without luminance thresholds

Every analysis stage operates on a binary ink mask. The binarization rule is reused unchanged from the first generation because it solved a real bug there, and the bug is instructive.

The obvious way to binarize a grayscale image is a luminance threshold: a pixel is ink if its perceived brightness is below some value. This fails on the collection because ink can be a saturated, low-luminance color. The font `08X08-F1` draws every glyph in pure red, `(240, 0, 0)`. The Rec. 601 luma of that color is approximately 72. A threshold of 128 classifies every red pixel as paper, and the entire font renders blank. The first-generation diary records this as the bug that forced a redesign of binarization.

The fix is to define ink by distance from the background rather than by absolute brightness. The background is the most common opaque color in the sheet. A pixel is ink when the maximum per-channel difference between it and the background exceeds a threshold. This single rule handles white-on-black, black-on-white, and colored ink uniformly:

```text
backgroundColor(img)  = the most common opaque RGB color in the sheet
inkDistance(img, x, y, bg) = max(|r - bg.r|, |g - bg.g|, |b - bg.b|)
isInk(x, y) = (inkDistance >= threshold) XOR invert
```

The `invert` flag XORs the result, which absorbs the polarity question (whether ink is darker or lighter than the background) into the same threshold. This is the foundation of every later stage; reverting to a luminance threshold would silently drop colored fonts. The Go port carries the same rule, and the same red-ink regression test (`08X08-F1` renders ink, not blank) guards it in both language implementations.

## Finding glyphs with connected components

Connected-component analysis is the technique that answers the question "where are the letters?" without assuming a grid. It labels every maximal set of ink pixels reachable from one another by eight-neighbor moves. Each labeled component has a bounding box and a pixel count. The output is a set of independent blobs with no assumption about how they relate to one another.

The reason this is necessary, rather than the projection-autocorrelation detector the first generation tried, is that projection autocorrelation is dominated by intra-glyph structure. The first generation projected ink counts onto the X and Y axes and searched for the dominant period, expecting it to be the cell size. On `16X16-F1` the true cell height of 16 produced an autocorrelation score of roughly 0.03, while a spurious period of 4 — an artifact of horizontal stroke spacing within each letter — scored 0.53. The detector latched onto the harmonic and was unusable. The first-generation diary shipped it marked "beta only" for exactly this reason.

Connected components sidesteps the problem because it does not ask "what is the period of the ink signal." It asks "where are the blobs." The relationship between blobs is then recovered by a separate clustering step that keys off blob centers, which are robust to intra-glyph stroke structure.

The bounding boxes of the components on `HOMEBOY` make the structure of the problem visible:

![Connected-component bounding boxes on HOMEBOY. Red boxes mark components larger than 8x8; green boxes mark small fragments. A single block letter fragments into many components — the counter of an O, detached serifs — so component count is not glyph count.](diag-v2-HOMEBOY-ccboxes.png)

`LIGHT`, by contrast, is close to a uniform grid and is largely recoverable by clustering:

![Connected-component bounding boxes on LIGHT. One red box per letter with a few green punctuation fragments. The layout is near-uniform.](diag-v2-LIGHT-ccboxes.png)

`M_TWINS` is the hardest case: two distinct typeface styles packed into one sheet, occupying different column regions:

![Connected-component bounding boxes on M_TWINS. Two typeface styles occupy different horizontal regions. One uniform grid cannot describe both.](diag-v2-M_TWINS-ccboxes.png)

## One glyph is not one component

The `HOMEBOY` image above exposes a problem that component counting alone cannot solve. The font has roughly 40 glyphs but produces 104 components. A single block letter fragments into many eight-connected blobs: the enclosed counter of an `O` is a separate component from its outline, detached serifs are separate components, and dot-like punctuation marks are their own components. Naive component counting would report more than twice the real glyph count.

The solution is to cluster components into rows and columns and to treat the set of components in one row-column cell as one glyph. The clustering is one-dimensional along each axis. Each component has a center point. Components are sorted by their Y center and split into groups wherever the gap between consecutive centers exceeds a tolerance. The same is done along X. A glyph is then the union of the components whose centers fall in the same row group and the same column group.

```text
clusterByAxis(centers, tol):
    sort centers
    groups = [[centers[0]]]
    for each subsequent center c:
        if c - last(groups) <= tol: append c to last group
        else:                        start a new group with c
    return groups

detectRowsCols(components, rowTol, colTol):
    rows = clusterByAxis([c.centerY for c in components], rowTol)
    cols = clusterByAxis([c.centerX for c in components], colTol)
    glyphs = []
    for each (row, col):
        members = components whose center is in row and in col
        if members: emit boundingBox(union of members)
    return glyphs
```

This recovers a grid even when glyphs have no inter-cell gutter, because it keys off where glyphs sit rather than where gutters are. On `LIGHT` it recovers approximately 16 columns by 3 rows. On `HOMEBOY` it recovers 7 rows even though the columns have no gutter at all.

After clustering, a refinement stage cleans up the cells. Adjacent components within a row cell whose gap is small relative to the median glyph width are merged, reassembling the fragmented strokes of a block letter into one glyph. Components whose area is below a minimum are dropped as speckle. Cells that are suspiciously wide relative to the row's median glyph width likely contain two glyphs whose centers fell in one column band; the design reserves a split-at-valley pass for these, though the shipped refinement merges and drops but does not yet split.

## Most components are not glyphs: the credit-text problem

A second structural fact about these sheets is easy to miss and corrupts the detector if ignored. Most sheets carry credit and version text that is not part of the glyph set: author names, font names, year strings, sometimes a one-line description. This text is small and dense and sits in a distinct band of the sheet. The measured data makes the scale of the problem precise.

For `HOMEBOY`, 58 of the 104 components are credit text. The credit components have a median size of 5×5 pixels; the glyph components have a median size of 29×22. The credit band sits below a 49-pixel vertical gap from the evenly-spaced glyph rows. For `LIGHT`, 18 of 49 components are credit text below a 146-pixel gap. For `M_TWINS`, roughly 70 of 89 components are credit text, though its multi-region layout makes a single horizontal cut insufficient.

A detector that does not separate the credit band before clustering will report roughly twice the real glyph count and will treat credit strings as if they were additional letter rows. The region-classification stage exists to prevent this. It uses two corroborating signals. The first is a row-spacing signature: glyph rows are approximately evenly spaced, so the credit band appears as one inter-row gap much larger than the median gap. The second is a size signature: credit components cluster well below the glyph band's median area. A component below the detected cut, or whose area is below 35 percent of the glyph median, is classified as credit and dropped before clustering.

```text
classifyRegions(components, rowClusters):
    gaps = adjacent row-cluster center differences
    medianGap = median(gaps)
    cut = the y just above the largest gap, if largestGap > 2 * medianGap
    glyphMedianArea = median area of components above the cut
    for each component c:
        if c.y0 >= cut:                      classify c as CREDIT
        elif c.area < 0.35 * glyphMedianArea: classify c as FRAGMENT  (keep, merge later)
        else:                                 classify c as GLYPH
    cluster only the GLYPH components
```

The band-separation diagnostic shows this working on `HOMEBOY` and `LIGHT`. Green boxes mark glyph-band components, red boxes mark the credit band, blue marks small fragments kept for merging, and a yellow line marks the detected cut:

![HOMEBOY with components classified by region: green glyphs, red credit text, blue fragments, yellow boundary. The cut lands cleanly above the dense credit band.](diag-v2-HOMEBOY-bands.png)

![LIGHT with the same region classification. The credits sit at the bottom under the detected cut.](diag-v2-LIGHT-bands.png)

The diagnostic is also where the single-cut approach honestly fails. On `M_TWINS`, the two typeface regions and the credit band interleave, so a horizontal cut lands inside the glyph region and misclassifies real glyphs as credit:

![M_TWINS region classification. The simple horizontal cut fails here: the two typeface regions and the credits interleave, so red boxes cover real glyphs. This font needs column-region grouping, not a single band cut.](diag-v2-M_TWINS-bands.png)

`M_TWINS` is the case that forces a more general region model. When column clustering yields two well-separated column groups with a large gap between them, the detector treats them as two sub-sheets and runs row and column detection within each. The single horizontal cut is the common-case fast path; column-region grouping is the fallback when the row-spacing and size signatures disagree.

## Labeling glyphs without recognition: the rendering oracle

Detecting glyph boxes solves only half the problem. The boxes are unlabeled. To render arbitrary text, each box must be associated with the character it depicts. The obvious approach is optical character recognition: read each glyph and identify the letter. The first generation tried the modern variant of this — a vision language model — and it failed in a specific, instructive way.

Asked to transcribe the glyphs of `16X16-F1` (a ground-truth sheet whose layout was already known by inspection), the vision model hallucinated a canonical codepage. It invented lowercase letters that do not exist in the font. On a high-resolution crop of the row containing `H I J K L M N O P Q R S T U V W X Y Z [`, it reported `A B C D E F G H I J K L M N O P Q R S T`, imposing the prior that capital letters start at `A` rather than reading the actual pixels. Open-ended transcription of bitmap glyphs is unreliable because the model pattern-matches to a canonical codepage instead of reading pixels.

The second generation replaces recognition with verification, and it needs no model at all. The key realization is that the tool can render text itself. The font is a bitmap font. Given a hypothesis about which characters the sheet contains and in what order, the tool can render that hypothesis string using the detected glyph boxes and compare the result to the source sheet, pixel for pixel. A correct hypothesis reproduces the sheet exactly, because the rendered output is built from the sheet's own bitmaps. Labeling reduces to a self-consistency check. The intended design is:

```text
oracleLabel(sheet, layout, hypothesisCharset):
    expected = renderHypothesis(layout, hypothesisCharset)   # same dimensions as sheet
    for each (box, i):
        glyphSource     = crop(binarized sheet, box)          # what the sheet shows here
        glyphHypothesis = crop(expected, box)                # what the hypothesis predicts here
        score = IoU(glyphSource, glyphHypothesis)
        if score >= 0.85:  accept hypothesisCharset[i] as the label for box
        elif score >= 0.5: flag box as needs-review
        else:              reject the hypothesis at this box
```

In this design the oracle never guesses a glyph. It renders the hypothesis character for each box and compares that rendered character to the sheet pixels at the box. A wrong hypothesis is rejected by pixel disagreement, not by a model's priors. This is strictly better than vision transcription, which hallucinates.

### The shipped oracle, and the tautology it contains

The implementation that shipped — first in TypeScript, then transliterated to Go — does not quite do what the pseudocode above describes, and the difference matters enough to state plainly. The shipped `verifyHypothesis` does not render the hypothesis character for box `i`. It renders box `i`'s own source glyph and compares that to box `i`'s source crop. The glyph it renders is `glyphs.glyphs[i]`, the bitmap that `expandLayout` cropped from box `i` in the first place. The hypothesis charset only supplies the label string; it does not select which glyph is rendered.

```text
# what the shipped oracle actually computes, per box i:
src = crop(binarized sheet, box i)              # the sheet at box i
hyp = renderCharBits(glyphs.glyphs[i], box i)   # box i's OWN glyph, re-rendered into box i
score = IoU(src, hyp)                            # ~1.0 whenever box i has any ink
```

Because the hypothesis glyph and the source crop come from the same box, the comparison is self-referential. Whenever a box contains ink, the rendered glyph reproduces that ink and the IoU is near 1.0, regardless of which character the hypothesis says the box depicts. The coverage metric — the fraction of boxes scored "ok" — therefore collapses to the fraction of boxes that captured any ink at all. The Go port confirms this directly: on `HOMEBOY`, `oracleCov` and `yield` (the non-blank-box fraction) are equal to three decimal places. Coverage is a layout-alignment signal, not a charset-correctness proof.

This is a genuine flaw, not a feature, and it changes what the oracle can honestly claim. It can tell you that the detected boxes land on ink rather than on gutters — useful, because a layout whose boxes are mostly blank is a bad layout. It cannot tell you that the labels are correct. A font whose boxes all capture ink but whose ASCII-from-space labels are shifted by one position scores full coverage with entirely wrong labels. The batch analyzer's triage report states this explicitly: a layout marked `auto` has generated boxes and a charset hypothesis, and the labels are a hypothesis that a human must confirm before the layout is used.

The honest metric the Go port adds is `Yield`: the fraction of glyph boxes that contain at least one ink pixel. It is computed without any self-referential rendering, and it equals the oracle's coverage by construction. The intended oracle — render each hypothesis character and compare to the sheet — is documented as future work. Until it exists, the labels are not verified, and the editing tool's manual label step is not optional.

## The renderer: adjustable line height, letter spacing, and color mode

Once glyphs are detected and labeled, rendering is a bit-block transfer. The renderer is the firmware-portable core of the project. It is integer-only, allocation-light, and uses a single platform-specific call — `setPixel` — to write to the framebuffer. In the browser the framebuffer is a canvas `ImageData` (RGBA, four bytes per pixel). In the Go CLI it is a `[]byte` RGBA slice. On the device it is the LCD buffer (RGB565). The algorithm is identical between the three; only `setPixel` changes.

The renderer draws one glyph by walking its bitmap and writing each ink pixel scaled by an integer zoom factor. It lays out text by maintaining a pen position, advancing horizontally after each glyph and vertically after each line break or wrap. The extension over the first generation is that the horizontal advance is per-glyph — each glyph's own width plus a configurable letter spacing — and the vertical advance is a configurable line height. The first generation used a single global cell size for both, which is correct only for uniform fonts.

```text
renderText(glyphSet, text, canvas, lineHeight, letterSpacing, zoom, fg, bg, colorMode, source):
    fill framebuffer with bg
    lineH = lineHeight * zoom
    gap   = letterSpacing * zoom
    penX = 0; penY = 0
    for each character ch in text:
        if ch == newline: penX = 0; penY += lineH; continue
        if wrap and col >= cols: penX = 0; penY += lineH
        glyph = resolveGlyph(glyphSet, ch)
        if glyph:
            blitGlyph(framebuffer, glyph, penX, penY, zoom, fg, bg, colorMode, source)
            penX += glyph.w * zoom + gap
        else:
            penX += defaultAdvance * zoom + gap
```

The adjustable line height exists for block fonts. `HOMEBOY` glyphs are 22 pixels tall and, at the default line height equal to the cell height, the rows touch. Increasing the line height to the cell height plus a few pixels inserts a gap so the block letters do not collide. Letter spacing does the same horizontally. Both are render-time overrides, not baked into the glyph boxes, because the boxes describe the source while spacing is a render concern. A terminal render of the same font wants tight spacing; a title render wants loose spacing. Keeping them separate lets one layout serve both.

### Color mode: flat mask versus original sheet colors

The renderer has two color modes. Mask mode paints every ink pixel a single flat foreground color — the PicoCalc green-on-dark look — and every background pixel the background color. Source mode paints each ink pixel its original color from the sheet, reading the source `ImageData` at the glyph's sheet position. Source mode exists because many fonts in the collection use colored ink that carries information the flat mask discards: `08X08-F1` is pure red, `16X16-F1` is light gray, and several sheets use multiple ink colors within one typeface. In source mode the rendered text shows the font as its author drew it; in mask mode it shows how the font will look on a monochrome device. The Go CLI exposes this as `--color-mode mask|source`, and the gallery exposes it as a toggle. The blit changes by exactly one line: when `source` is non-nil, the on-bit color comes from `sourcePixel(img, glyph.x + gx, glyph.y + gy)` instead of the flat `fg`.

### Case fallback: rendering text on incomplete fonts

Most fonts in the collection ship only one ASCII case. `16X16-F1` has uppercase `A`–`Z` but no lowercase; a few fonts are the reverse. A renderer that resolved each character to exactly one labeled glyph would render blanks for every missing-case character, which makes previewing normal prose on an uppercase-only font useless. The resolver falls back to the opposite ASCII case: a lowercase input character whose glyph is absent resolves to its uppercase counterpart, and vice versa. The fallback is symmetric and applies only when the exact label is missing, so a font that genuinely has both cases renders each correctly. The effect is that `"Hello World"` renders as `"HELLO WORLD"` on an uppercase-only font — legible, if inaccurate — which is the right behavior for a browsing and triage tool.

## From TypeScript core to Go CLI

The algorithm was written first in framework-free TypeScript under `web/src/core/`, deliberately isolated from React and Redux so it could be transliterated. That transliteration is now done. The Go package `internal/core` mirrors the TypeScript files one for one, and a `bfb` command-line tool exposes the core as a renderer, a batch analyzer, and an interactive gallery. The Go port was a transliteration, not a redesign: the same per-stage invariants, the same packed-1bpp indexing, the same connected-component and clustering logic, ported file for file so that a passing Go test suite and a passing TypeScript test suite together prove the two agree.

| TypeScript (port source) | Go (transliteration) | Role |
|---------------------------|----------------------|------|
| `core/types.ts` | `internal/core/types.go` | `Glyph`, `GlyphSet`, `FontLayout`, `RenderRequest` |
| `core/bits.ts` | `internal/core/bits.go` | packed 1-bpp `GetBit`/`SetBit`/`PackMask` |
| `core/binarize.ts` | `internal/core/binarize.go` | background-distance binarization |
| `core/detect.ts` | `internal/core/detect.go` | connected components, region classification, clustering |
| `core/oracle.ts` | `internal/core/oracle.go` | IoU, `VerifyHypothesis`, `LabelLayout`, `Yield` |
| `core/layout.ts` | `internal/core/layout.go` | `ExpandLayout` (layout → glyph set) |
| `core/render.ts` | `internal/core/render.go` | integer-only blit, `RenderText`, case fallback |
| `core/heuristics.ts` | `internal/core/heuristics.go` | filename/divisor cell-size guess |

The Go tests mirror the TypeScript tests case for case. The same synthetic ASCII-art fixtures, the same expected pixel colors, the same component counts. Where the TypeScript suite asserts `getPixelColor(fb, 2, 0) === [10, 20, 30]`, the Go suite asserts the same pixel equals `RGB{10, 20, 30}`. The most important parity check runs against real sheets rather than synthetic art: the Go detector on `HOMEBOY` produces a credit-band cut at exactly `y = 117`, with 41 glyph-band and 58 credit-band components — the same numbers the TypeScript offline verifier produced. Drift in that number means the port diverged.

The CLI is built on the Glazed command framework, which gives each subcommand structured output (`--output json`, `--output csv`), a help system, and logging for free. Three subcommands ship today.

`bfb render` takes a font sheet, an optional layout JSON, a text string, and render parameters, and writes a PNG. Without a layout it seeds one from the filename heuristic, so a clean uniform font renders with no curated configuration. It is the headless rendering path the firmware build pipeline can call, and it removes the indirection of a Node script for offline rendering.

`bfb analyze` runs the connected-component detector, the region classifier, and the self-consistency oracle across the whole collection. For each font it picks the better of two layouts — the detected-box layout or the heuristic uniform grid — by yield, writes a `FontLayout` JSON, and appends a row to a triage report. The full collection (487 sheets present locally of 817 catalogued) analyzes in about five seconds. The triage report sorts fonts into `auto` (a layout was generated; labels are an unverified hypothesis), `needs-review` (detection was weak), and `missing` (the sheet is not downloaded), so a human can work the queue rather than click through fonts one at a time.

`bfb gallery` generates a standalone HTML gallery for browsing and marking fonts. Demos render on demand in the browser through a third port of the core — a vanilla-JavaScript implementation inlined into the page — so any text preset, color mode, and zoom can be tried live without re-running Go. A small Redux-like store holds the gallery state: the current font, the text preset, the color mode, the zoom, and two kinds of per-font marks. The operator marks a font liked or marks its slicing bad, adds free-form tags, and filters the list by mark or tag to jump straight to the fonts that need attention. Marks and tags persist to `localStorage`, and the liked set exports to a JSON bundle (name, layout, tags) that round-trips through `bfb render --layout`.

The three implementations are not redundant. The TypeScript core is the browser and portable reference. The Go CLI is the authoritative renderer for the build pipeline and the only one that runs the batch analyzer at scale. The JavaScript gallery port exists so the operator can switch presets and color modes interactively, which pre-rendered PNGs cannot support. All three must agree, because any of them can be the reference for the C firmware port.

## The firmware-portability contract, as a three-way parity

The renderer and the glyph representation are written so that a C port is mechanical, and the constraints that make that true are worth stating explicitly because they govern many small decisions. The contract is now a three-way parity rather than a two-way one: the TypeScript core, the Go CLI, and the JavaScript gallery port must all produce the same framebuffer for the same glyph set, text, and parameters, because the C firmware will be transliterated from whichever is most convenient and must match all three.

A glyph is a C struct: signed integer coordinates and dimensions, a pointer to a packed one-bit bitmap, and a one-byte code. The bitmap packing within a glyph is one bit per pixel, row-major, byte `i >> 3`, bit `i & 7`, identical across all three implementations. The asset baker emits one such struct and one bitblob per glyph per font.

The blit and the text layout use only integer arithmetic. There is no floating point, no anti-aliasing, no alpha blending. The only platform-specific operation is `setPixel`, which writes RGBA to an `ImageData` in the browser, RGBA to a `[]byte` in Go, and RGB565 to the LCD buffer on the device. The line height, letter spacing, and per-glyph width are plain integers.

The detection stage and the oracle are host-only tools. They run at build time to produce the layout JSON. They do not run on the device. The device consumes only the resulting coordinate layout. Keeping detection and oracle out of the firmware port is part of the contract: the device does a fixed blit from a known layout, nothing more.

The lock-step guarantee between the implementations is maintained by mirrored unit tests today: each Go test asserts the same value the TypeScript test asserts on the same input, and the gallery's source-color render of `08X08-F1` produces the same red ink shades the Go CLI produces. The remaining gate is an automated cross-implementation pixel diff — render the same `(sheet, layout, text, params)` in TypeScript, Go, and JavaScript and assert byte-identical RGBA. The gallery's planned Go-backend render mode, which fetches a Go-rendered PNG and displays it next to the in-browser JavaScript render with a pixel diff, is the interactive form of that gate.

## The editing tool's visual design system

The tool that an operator uses to correct detection failures and label glyphs has a deliberate visual identity, and the identity is itself a design decision worth recording because it governs the component architecture.

The interface is retro monochrome, modeled on classic Macintosh System 1, but stripped of all window chrome. There is no title bar, no menu bar, no window frame. The application fills its viewport as a flat, gridded work surface. The aesthetic is two one-bit colors — black ink on white paper — with structure expressed entirely by hairline borders and recessed wells rather than by shadows, gradients, or rounded corners. The grid is the structure; the strokes define the regions.

Color is reserved for meaning, never for decoration. The single non-monochrome hue in the chrome is one accent blue, used only for focus rings and the currently selected item. Semantic states — auto-detected, needs-review, error, region — are expressed as font color through a small set of tones (`ok`, `warn`, `info`, `crit`) applied to text and to twelve-pixel swatches beside the text. The rule is strict: if removing the color loses no information, the color is decoration and must be removed. Status is never conveyed by color alone; every colored badge carries a text label, so the interface remains legible if color is removed entirely.

The component architecture follows a strict atomic layering borrowed from design-system practice, enforced as a dependency rule. There are four layers: primitives, atoms, molecules, organisms. A component may import only from its own layer or a layer below it.

```text
ui/
  primitives/   tokens only — tokens.css, reset.css; no components
  atoms/        smallest units: Text, Label, Number, Rule, Field, IconButton, Swatch
  molecules/    2–4 atoms composed: Toolbar, SliderRow, Badge, SearchField, StatusLine
  organisms/    full regions: FontList, GlyphEditor, PreviewCanvas, Controls
```

The dependency rule is the backbone of the system. Changing a token changes the whole application. Changing an atom changes every molecule that uses it. No organism ever hardcodes a color or a spacing value, because it can only reach those through the layers below it. This makes the monochrome field and the color-as-signal rules enforceable by construction rather than by convention. A component literally cannot introduce a decorative color because it has no access to raw color values.

The typographic discipline is Swiss: one grid, two typefaces, strong contrast through size and weight. A monospace face drives the interface labels and numbers. A sans-serif face is reserved for the content the user types into the preview, so the neutral interface never competes with the bitmap font being judged. Generous whitespace, a four-pixel base grid to which every dimension snaps, and sharp corners complete the system. The bitmap preview is the visual center of the tool; everything else is calibrated to recede.

## Common failure modes

Several failure modes recur across this kind of system, and naming them helps avoid them.

**Luminance-threshold binarization** silently drops colored fonts. The red-glyph case is the canonical example. The fix is distance-from-background binarization, and the regression test that encodes it should never be removed.

**Naive connected-component counting** over-reports glyphs for any font whose letters fragment. Block fonts with enclosed counters and detached strokes produce many components per letter. The fix is row-column clustering with a merge refinement, never raw component count.

**Ignoring the credit band** roughly doubles the reported glyph count and introduces spurious letter rows. The fix is region classification before clustering, using the row-spacing and size signatures. The single-cut fast path fails on multi-region sheets and must fall back to column-region grouping.

**Vision transcription for labeling** hallucinates a canonical codepage. This is not a tunable problem; it is a category error about what vision models do with unfamiliar pixel layouts. The fix is the rendering oracle, which verifies rather than recognizes.

**A self-referential oracle** is a subtler failure than a hallucinating one. The shipped oracle renders each box's own source glyph, so its coverage metric reports layout alignment rather than charset correctness. It looks like it works — coverage is high — while proving nothing about the labels. The fix is to render the hypothesis character for each box and compare to the sheet, the intended design the pseudocode describes; until that exists, use `Yield` (non-blank-box fraction) as the honest metric and treat labels as unverified.

**Baking spacing into glyph boxes** couples the source representation to one render context and prevents tight versus loose renders of the same font. The fix is render-time line height and letter spacing overrides.

**Mixing the detection or oracle into the firmware port** violates the portability contract and bloats the device binary. The fix is the strict boundary: detection and oracle are host build tools; the device consumes only the resulting layout.

**Letting three implementations drift** silently breaks the parity contract. The fix is mirrored tests that assert the same values across TypeScript and Go, plus a cross-implementation pixel diff for the gallery's JavaScript port.

## Working rules

The decisions above distill into a small set of rules that govern the system.

- Store glyphs as per-glyph coordinates. A uniform grid is the degenerate case. Never add a parallel uniform-grid code path with a compatibility shim.
- Detect structure with connected components plus row-column clustering, never with projection autocorrelation. Classify and drop the credit band before clustering.
- Label glyphs with the rendering oracle, never with OCR or vision transcription. Verify hypotheses; do not recognize pixels. Until the oracle renders the hypothesis character per box, treat its coverage as a layout-alignment signal (`Yield`) and the labels as an unverified hypothesis.
- Keep the renderer integer-only and single-`setPixel`. Line height and letter spacing are render-time overrides in source pixels, not properties of the boxes. Offer mask and source color modes; the blit differs by one line.
- Resolve glyphs with a symmetric ASCII case fallback so incomplete-case fonts still render legible text.
- Keep detection and the oracle off the device. The firmware consumes the layout; it does not compute it.
- Keep the TypeScript, Go, and JavaScript implementations in lockstep. Mirror the tests across languages; add a cross-implementation pixel diff before trusting any one as the firmware reference.
- Express the visual identity in tokens and enforce the atomic layering as a dependency rule. Reserve color for state; never convey state by color alone.

## Implementation references

The reference implementation is the PicoCalc Bitmap Font Browser. The TypeScript core and its design live in one docmgr ticket; the Go port and CLI live in a second.

- Repository: `/home/manuel/code/wesen/2026-06-24--bitmap-font-browser`
- TypeScript core (port source): `web/src/core/{types,bits,binarize,detect,oracle,layout,render,heuristics}.ts` and `*.test.ts`
- Go core (transliteration): `internal/core/{types,bits,binarize,detect,oracle,layout,render,heuristics}.go` and `*_test.go`
- PNG codec bridge (the only image-library import): `internal/pngx/png.go`
- CLI: `cmd/bfb/{main,render,analyze,gallery}.go`
- v2 design guide: `ttmp/2026/06/25/BITMAP-FONT-SLICER-V2--*/design-doc/01-bitmap-font-slicer-v2-intern-design-implementation-guide.md`
- v2 investigation diary: `ttmp/2026/06/25/BITMAP-FONT-SLICER-V2--*/reference/01-investigation-diary.md`
- Go-port design guide: `ttmp/2026/06/25/BITMAP-FONT-RENDER-GO--*/design-doc/01-go-renderer-cli-and-batch-heuristics-oracle-intern-design-implementation-guide.md`
- Go-port investigation diary: `ttmp/2026/06/25/BITMAP-FONT-RENDER-GO--*/reference/01-investigation-diary.md`
- First-generation binarization and renderer (reused): `v1/web/src/core/fontLoader.ts`, `v1/web/src/core/renderer.ts`, `v1/web/src/core/bits.ts`
- First-generation detector (the approach replaced): `v1/web/src/core/detect.ts`
- Analysis scripts (connected components, clustering, band separation): `ttmp/2026/06/25/BITMAP-FONT-SLICER-V2--*/scripts/01-…` through `07-…`
- Diagnostic images: `ttmp/2026/06/25/BITMAP-FONT-SLICER-V2--*/various/`
- Font collection: `https://github.com/ianhan/BitmapFonts`

## Open questions

The design leaves several questions for implementation to resolve empirically.

- The merge tolerance in the clustering refinement over-joins `HOMEBOY`'s first row into a single 285×22 box. The Go port reproduces this faithfully (parity before tuning), and tuning the merge-gap threshold — or adding the reserved split-at-valley pass — is a separate ticket. The fix must not break the `HOMEBOY` cut-`y=117` parity anchor.
- The multi-region detection rule for sheets like `M_TWINS` needs a confidence signal so it does not fire on legitimately wide single-style sheets.
- The oracle's tautology is the largest open item. The intended probe-render oracle — render each hypothesis character into its box and compare to the sheet — is documented but not shipped. Until it exists, labels are unverified, and the manual editor is the only charset authority.
- The three-way parity is enforced by mirrored unit tests today, not by an automated cross-implementation pixel diff. The gallery's planned Go-backend render plus diff mode is the interactive version of that gate; a headless version belongs in CI.
- The persistence model for curated layouts is resolved in principle (JSON files under `assets/fonts/layouts/`, one per font, shareable and committable) but the gallery's session state — marks, tags, current text and preset — is currently `localStorage` plus a downloaded JSON. Server-side persistence and a Go `bfb serve` command that hosts the gallery alongside a render endpoint are the next step.

## Related notes

- [[ARTICLE - Bitmap Font Browser - The Portable Core and the Firmware Contract]] — the companion article on the portable core and the device contract.
- [[PROJ - ZK Tool]] — another Go + tooling project in the vault; shares the "framework-free core, thin shell" pattern.
- [[ARTICLE - Playbook - Self-Contained Go Wasm and JavaScript Browser Applications]] — the Go-plus-browser frontend pattern this project's stack descends from.
