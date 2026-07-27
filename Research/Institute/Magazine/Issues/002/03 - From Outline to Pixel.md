# From Outline to Pixel

## Rasterizing TrueType Glyphs

A glyph in a TrueType font is not a picture. It is a set of instructions — a program, in a small stack-based bytecode — that describes the outline of a letter as a collection of straight lines and quadratic Bézier curves. To render a glyph at a given size, a font rasterizer executes that program, converts the resulting outlines into pixels, and produces a bitmap of gray values representing how much of each pixel the glyph covers. That bitmap is what a browser composites onto the page, and what a downstream threshold eventually turns into the one-bit dots a thermal printer burns.

This article is about the rasterizer. The specific subject is a fixed-point scanline rasterizer that compiles TrueType outlines into bytecode, executes them in a virtual machine, and fills the resulting contours with non-zero winding rule and 8× subpixel anti-aliasing, all in 26.6 fixed-point arithmetic with no floating-point on the hot path. The reference renderer it is measured against is stb_truetype, a widely used single-header library that uses float coordinates and a different coverage calculation.

The story of building this rasterizer is a story of five bugs. Each is small. Each is local. Each produces a glyph that looks almost right — a hole filled with gray, a stroke missing its anti-aliasing on one side, a glyph fifteen percent too large — and each is invisible without a systematic comparison against a reference. Taken together, they reduced the pixel difference against stb_truetype from 87 percent to 23 percent. The bugs themselves are not specific to this renderer. Any scanline rasterizer that uses non-zero winding fill, fixed-point coordinates, or subpixel anti-aliasing will encounter variants of the same issues.

---

## The Scale Factor, and Why It Matters

We begin where the investigation began: with every glyph the wrong size.

After the obvious bugs were fixed — a flag-repeat bit read as `0x80` instead of `0x08`, a winding value negated at the wrong moment — the rasterizer produced glyphs that were visually recognizable but clearly wrong. Holes in letters like O and B were filled with gray. Strokes were too thick. Anti-aliasing was banded. A batch comparison against stb_truetype reported that 87.4 percent of body pixels differed by more than 20 gray levels, with a mean absolute difference of 154 levels out of 255.

The vast majority of that difference came from a single root cause. The glyphs were the wrong size.

The rasterizer's scale computation divided the desired pixel size by the font's `unitsPerEm` — the number of font units per em square, a fundamental metric of every TrueType font. For Go-Regular, `unitsPerEm` is 2048. At a requested size of 48 pixels, the scale was `48 / 2048 = 0.02344` font-units-to-pixels.

stb_truetype uses a different divisor. Its `ScaleForPixelHeight` function divides by the font's visible height — the distance from the top of the tallest ascender to the bottom of the lowest descender:

```c
float stbtt_ScaleForPixelHeight(const stbtt_fontinfo *info, float height) {
    return height / (info->ascender - info->descender);
}
```

For Go-Regular, `ascender` is 1935 and `descender` is −432, so the visible height is `1935 − (−432) = 2367`. The stb scale is `48 / 2367 = 0.02028`.

The ratio is `2367 / 2048 = 1.156`. Every glyph was 15.6 percent too large.

The fix is one line:

```cpp
int32_t font_height = font.ascender - font.descender;
if (font_height <= 0) font_height = font.units_per_em;
fixed_t scale = (pixel_size * FIXED_ONE * FIXED_ONE) / font_height;
```

After this change, the pixel diff dropped from 87.4 percent to 62.6 percent. The mean absolute difference fell from 154 to 55 gray levels.

The bug is silent in isolation. There is no visual cue that a glyph is fifteen percent oversized. A capital O that is too large still looks like a capital O. Only a comparison against a reference renderer at the same declared pixel size reveals it. And the error is not confined to size: it corrupts every derived metric — bounding boxes, advance widths, subpixel positions — in the same proportion.

The lesson is a clarification of what "pixel size" means. When a specification or an API says "pixel height," it means the visible line height — ascender to descender — not the em square. FreeType uses the same convention as stb_truetype. The em square is a coordinate space; the visible height is what the user sees.

---

## Non-Zero Winding Fill, and How It Breaks

The scale fix left a second defect visible. Glyphs with holes — O, B, the numeral 8 — had their counters partially filled with gray. Not solid black. Gray. Small positive coverage values, 31 or 63 or 95 out of 255, in regions that should have been zero.

To understand why, we have to look at how the fill rule works.

The non-zero winding rule determines whether a point is inside a glyph by tracking a running count as the outline is scanned. Imagine walking a horizontal line across a glyph at a given vertical position. Each time the line crosses an edge of the outline, the crossing is tagged with a direction: +1 if the edge is going one way, −1 if it is going the other. Between two consecutive crossings, the accumulated count is the winding number. If it is non-zero, the region is inside the glyph. If it is zero, the region is outside.

A glyph like O has two contours: an outer boundary drawn clockwise and an inner boundary (the hole) drawn counter-clockwise. A horizontal scanline through the middle of an O crosses four edges:

1. Outer left edge: winding +1, cumulative 1 — inside the stroke
2. Inner left edge: winding −1, cumulative 0 — inside the hole, outside the glyph
3. Inner right edge: winding +1, cumulative 1 — inside the stroke
4. Outer right edge: winding −1, cumulative 0 — outside the glyph

This produces two fill spans — outer-left to inner-left, and inner-right to outer-right — with a gap between them where the hole is. The hole is correctly unfilled because the winding is zero there.

The defect in our rasterizer was that all four crossings had the same winding sign. The cumulative count never returned to zero between the inner edges, so the fill span continued across the hole. The O became a solid blob with a gray tint in the middle.

The root cause was a pair of transformations that each negated the winding, in a system where only one of them should have.

Edges are emitted by the virtual machine in font space, where the y-axis points up. The winding assignment is straightforward: an edge going up (increasing y) gets +1, an edge going down gets −1. This is correct for a clockwise outer contour and a counter-clockwise inner contour. The crossings come out as +1, −1, +1, −1.

The rasterizer's sort routine normalizes every edge so that `y0 ≤ y1`, swapping endpoints when necessary. The original code also negated the winding on swap, on the reasoning that swapping endpoints reverses the edge's direction and therefore the crossing direction. After normalization, a downward edge with winding −1 becomes an upward edge with winding +1. Every upward edge now has winding +1, regardless of which contour it belongs to. The crossings become +1, +1, +1, +1. The cumulative count rises to 4 and never returns to zero. Everything is filled, including the hole.

The fix: do not negate the winding on swap. The winding encodes the *contour's* direction — which side of the fill boundary the edge is on — not the edge's *geometric* direction. Swapping endpoints changes the geometric direction, but it does not change the contour direction. The sort normalization should leave the winding alone.

After this change, the crossings return to +1, −1, +1, −1, the cumulative count traces 0→1→0→1→0, and the hole is correctly unfilled.

The diagnostic that found this was a tracing tool that reproduced the rasterizer's exact logic for a specific pixel row and sub-row, printing every crossing with its x-position and winding. For glyph O at row 29, sub-row 0, the trace showed:

```
sub 0: 4 crossings: (0.8,+1→1) (7.8,-2→-1) (37.2,+1→0) (44.2,-1→-1)
```

The second crossing had winding −2. Two edges with winding −1 had been merged into one crossing, and the merge had summed the windings, producing a net value that overshot past zero. That overshoot is the third bug.

---

## When Crossings Merge

Rasterizers have a merge step that combines crossings closer than some threshold — typically a fraction of a pixel — into a single crossing. The step exists to eliminate thin fill slivers from Bézier flattening, where two edges from the same curve produce crossings that are nearly but not exactly coincident.

The original merge summed the winding values of all near-coincident crossings, regardless of sign. This is correct for opposite-sign pairs: a +1 and a −1 that are 0.05 pixels apart produce a net winding of 0, which is geometrically correct — the thin sliver between them contributes negligible coverage. But for same-sign pairs, two −1 crossings, the sum is −2. The fill algorithm overshoots past zero, and regions that should be outside the glyph fill in.

Same-sign near-coincident crossings arise when two edges from the same contour meet at a sub-row boundary. One edge ends at the boundary (its y1 equals the sub-row start), and the next edge starts there (its y0 equals the sub-row start). Both edges belong to the same side of the same contour, so they have the same winding sign. The thin sliver between their crossing positions is an artifact of discrete sub-row sampling, not real geometry.

The fix distinguishes the two cases:

- **Same winding sign**: keep one crossing with the original winding. The sliver is a sampling artifact; dropping it does not change the fill.
- **Opposite winding sign**: drop the current crossing. The pair represents a Bézier artifact; dropping the second effectively cancels the sliver.

A second, related fix changed the x-intersection computation from `y_sample = y_sub` to `y_sample = max(y_sub, e.y0)`. When an edge begins within a sub-row, using the sub-row's y extrapolates the x-position backward before the edge's start, and two adjacent contour edges that meet at the boundary produce x-positions on opposite sides of the meeting point — creating the sliver. Clamping to the edge's own start eliminates the extrapolation.

---

## The Missing Pixel at the End of a Span

The fill loop walks sorted crossings from left to right. When the winding is non-zero between two consecutive crossings at x-positions `prev_x` and `crossing_x`, it fills the pixels from `prev_x` to `crossing_x`.

The original loop bound was:

```cpp
int px0 = prev_x >> FRAC_BITS;
int px1 = crossing_x >> FRAC_BITS;

for (int px = px0; px < px1; px++) {
    // compute coverage for pixel px
}
```

The right-shift by six bits truncates the fractional part. If `crossing_x` is 8.344 in 26.6 fixed point, then `px1 = 8.344 >> 6 = 8`. The loop runs for pixels 4 through 7. It never visits pixel 8.

But pixel 8 contains the fractional part of the crossing endpoint. From x=8.0 to x=8.344 is 0.344 pixels of coverage. For the stem of a capital I at 48 pixels, that is `0.344 × 8 sub-rows × 255 / 512 ≈ 87` gray levels — a significant anti-aliasing contribution that was simply missing.

The fix:

```cpp
int px1 = (crossing_x >> FRAC_BITS) + 1;
```

The +1 ensures the loop visits the pixel containing the crossing endpoint. The coverage computation inside the loop already clamps the fill end to `min(crossing_x, pixel_end)`, so visiting an extra pixel does not produce over-coverage when the crossing falls exactly on a pixel boundary.

This bug was invisible for crossings that fell on integer pixel boundaries — common for the horizontal and vertical stems that benefit from a lucky subpixel offset. It manifested as missing anti-aliasing on one side of a stroke: the left edge of a fill span was anti-aliased, the right edge was not. The stroke appeared thinner on one side, and the glyph looked slightly off in a way that was hard to name.

---

## The Half-Pixel Offset

The final bug was the most subtle, and it reversed a decision that had seemed obviously correct.

To position a glyph in the coverage mask, the rasterizer shifts its edges by a pen offset. The original code used:

```cpp
fixed_t pen_offset_x = -(fx_min) + (FIXED_HALF);  // +0.5 pixels
```

This shifts the left edge of the glyph's bounding box to position 0.5 within the mask, adding a half-pixel offset. The intent was to avoid edges at exact pixel boundaries, which produce aliased output. A fixed 0.5-pixel offset seemed like a clean way to push every edge off the boundary.

It does not match what float-precision reference renderers produce. stb_truetype places the left edge of a capital I's stem at fractional position 0.5146 — not 0.5, but a specific value derived from the font's own coordinates. The difference of 0.0146 pixels is tiny, but it shifts the anti-aliasing distribution across all eight sub-rows, producing systematically different gray values at the stroke edges.

The fix preserves the natural fractional position of the font's coordinates:

```cpp
fixed_t pen_offset_x = -(fx_min & ~63);
```

The expression `fx_min & ~63` masks off the fractional bits (the lower six bits of a 26.6 number), leaving only the integer part. After subtracting, the left edge of the bounding box sits at its natural fractional position within pixel 0 — exactly where the font's coordinates placed it.

After this change, the pixel diff dropped from 25.4 percent to 23.3 percent. More tellingly, the near-match rate — the fraction of pixels within 10 gray levels of the reference — rose from 9.6 percent to 13.4 percent. The remaining differences are small anti-aliasing variations, not systematic positioning errors.

---

## The Diagnostic Pipeline

Each of these bugs was found through the same pipeline, and the pipeline is worth recording as a method.

The first stage is a batch pixel comparison. A harness renders 88 representative glyphs — A through Z, a through z, 0 through 9, punctuation — and compares every pixel against stb_truetype. The output is a per-glyph body-diff percentage, a mean absolute difference, and a total across all glyphs. This provides the where-to-look signal. A glyph with 90 percent body diff is clearly wrong; one with 30 percent is close but systematic.

The second stage is a per-glyph row-by-row diff. A detail tool renders one glyph and prints a grid in which each cell shows the difference between our coverage and stb's: `=` for an exact match, `+XX` where ours is darker, `−XX` where ours is lighter, `.` for zero in both. A constant +6 across an entire stem indicates a positioning offset. A +192 on one edge and 0 on the other indicates a missing anti-aliasing pixel. Alternating signs at curve edges indicate subpixel positioning differences.

The third stage is a per-sub-row crossing trace. This is the most precise tool. It reproduces the rasterizer's exact logic for a specific pixel row and sub-row, printing every crossing with its x-position, winding, and cumulative count. The expected pattern for a correctly-filled hole is four crossings with windings +1, −1, +1, −1, tracing 0→1→0→1→0. Any deviation is a bug.

The fourth stage, used after the quantitative issues were resolved, was a vision-language model assessing qualitative differences that are hard to measure numerically — stroke weight evenness, anti-aliasing smoothness, curve quality. Used without context, the model's feedback was vague. Used with extensive context about the project, the rendering approach, the recent fixes, and the specific criteria to evaluate, it provided specific per-glyph assessments: "B shows faint horizontal gray bands in both bowls; O counters are clean white."

The pipeline is general. Any rasterizer measured against a reference can be debugged this way, and the failure modes it surfaces are the failure modes every scanline rasterizer shares.

---

## What Remains

After all five fixes, the pixel diff against stb_truetype is 23.3 percent of total pixels. The remaining differences are inherent to the approach, and they represent a deliberate trade.

The rasterizer uses 26.6 fixed-point coordinates; stb_truetype uses float. At stroke edges, the fixed-point quantization produces anti-aliasing values that differ from the float reference by 5 to 20 gray levels.

The coverage calculation uses 8× supersampling — the average of eight discrete sub-row samples. stb_truetype computes the exact area of the pixel covered by the fill region. Both methods produce correct anti-aliasing, but the exact gray values differ at edge pixels.

The Bézier flattening uses adaptive subdivision with a threshold of one-eighth of a pixel, which produces slightly different line segment positions than stb_truetype's subdivision, leading to slightly different edge crossings near curve inflection points.

These differences are the cost of deterministic, FPU-free rendering. The rasterizer can run on a microcontroller with no floating-point unit, producing identical output every time. The price is a small anti-aliasing variation from a float-based reference — a price that is acceptable for the embedded targets this kind of rasterizer is built for.

---

## Performance, and the Lever That Actually Matters

After correctness, the question was speed, and the expected optimization barely helped.

The obvious target was the per-sub-row scan loop, which iterated over a range of edges for every sub-row. Many of those edges were exhausted — their y1 was below the current scan position — and contributed no crossings. An active-edge list that visited only truly active edges seemed like an obvious win.

It was implemented, producing pixel-exact output identical to the original. The speedup was one percent on Latin glyphs, eight to eleven percent on CJK. The reason is structural. Most edges in a Latin glyph span the full height of the glyph — the left and right sides of each contour are active at every scanline. A glyph like O has two contours, each contributing one left and one right edge at any given scanline, for a total of about four active edges. The other forty-odd edges are short Bézier segments active only near the top and bottom curves, and the original cursor already skipped most of them.

The active-edge list removes the remaining dead edges — the "dead zone" between the cursor and the break point — and that dead zone is small for Latin. For CJK, with many short Bézier segments entering and exiting within a few pixel rows, the dead zone is larger and the speedup is measurable.

The performance lever that actually matters is the anti-aliasing level. Dropping from 8× to 4× subpixel anti-aliasing halves the number of sub-rows and halves the total per-edge work. The quality loss is invisible at 48 pixels and above — the eye cannot distinguish 4× from 8× at normal reading distances. At 24 pixels, 4× shows slightly more stairstepping on curves, which is an acceptable trade for embedded displays with limited frame budgets.

| Font | Size | 8× AA | 4× AA | Speedup |
|------|------|-------|-------|---------|
| Go-Regular | 48 px | 30 µs | 20 µs | 1.50× |
| IPA-Gothic | 48 px | 56 µs | 33 µs | 1.69× |
| IPA-Gothic | 96 px | 84 µs | 49 µs | 1.71× |

The lesson generalizes. The hot path of a scanline rasterizer is the per-edge, per-sub-row x-intercept computation — a multiply and a divide per active edge per sub-row. Optimizations that reduce the number of edges visited are second-order. Optimizations that reduce the number of sub-rows are first-order. For embedded use, the right answer is to drop the anti-aliasing level, not to chase a faster inner loop.

---

## Where This Meets the Printer

The rasterizer described here produces antialiased grayscale pixels — exactly the representation that the dithering algorithms of the previous article consume. A correctly rendered glyph, with its holes unfilled, its strokes the right size, and its anti-aliasing present on both edges, is the input that a threshold or a ditherer can do something with.

But "correctly rendered" at a large size is not "correctly rendered" at a small size, and a thermal printer asks for small text. A glyph rendered at eight or nine pixels tall produces strokes thinner than one pixel, and the font rasterizer represents those strokes with anti-aliasing — light-gray pixels rather than solid black. The downstream threshold discards those pixels, and the strokes vanish before the bitmap reaches the printer.

This is the failure the final article addresses. It is a failure that no dithering algorithm can repair, because the information was lost in the rasterizer, before any dot decision was made. The investigation that follows reverses its own conclusion twice — from a bitmap font, to supersampling, to the simple act of disabling anti-aliasing — and arrives at a principle that reframes the entire problem of small text on a one-bit device.
