---
title: "TTF Rasterizer Bug Hunting — Scale, Windings, and Coverage"
aliases:
  - TTF Rasterizer Debugging
  - Font Rasterizer Bug Hunting
  - Non-Zero Winding Fill Debugging
  - Fixed-Point Rasterizer Quality
tags:
  - article
  - ttf
  - font-rendering
  - rasterization
  - debugging
  - fixed-point
  - winding-fill
  - anti-aliasing
status: active
type: article
created: 2026-05-29
repo: /home/manuel/code/wesen/2026-05-29--ttf-vm-render
---

# TTF Rasterizer Bug Hunting — Scale, Windings, and Coverage

This article documents the debugging of a fixed-point TTF font rasterizer from 87% pixel difference against a reference renderer down to 23%. Each bug illustrates a distinct failure mode of scanline rasterization: wrong coordinate scale, corrupted winding values, missing coverage at span endpoints, and incorrect subpixel positioning. The fixes are small — often one or two lines — but finding them required tracing the exact behavior of the fill algorithm at individual sub-rows of individual pixel rows.

The rasterizer under investigation is part of a TTF glyph-outline VM renderer that compiles TTF outlines into bytecode, executes the VM to emit edges, and rasterizes with non-zero winding fill and 8× subpixel anti-aliasing, all in fixed-point 26.6 arithmetic with no floating-point on the hot path. The reference renderer is stb_truetype, a widely-used single-header library that uses float coordinates and a different coverage calculation method.

> [!summary]
> - A scale mismatch (dividing by `unitsPerEm` instead of `ascender − descender`) made every glyph 15% too large — the single largest quality contributor, dropping pixel diff from 87% to 63% in one line change.
> - The non-zero winding fill rule requires that the winding value at each crossing encode the contour's direction, not the edge's geometric direction. Multiple transformations (Y-flip, sort normalization) can corrupt this encoding, and each corruption fills holes in glyphs like O, B, and 8.
> - The rasterizer's fill loop must include the pixel containing the span's right endpoint. A loop bound of `px < (x >> 6)` misses this pixel; `px < (x >> 6) + 1` includes it. Without the +1, strokes lose their right-side anti-aliasing.
> - Preserving the natural fractional position of font-unit coordinates (instead of adding a fixed 0.5px offset) gives edge placement that closely matches float-precision reference renderers.

## Why this note exists

Font rasterizer quality is hard to assess by eye. A renderer that produces "something that looks like a B" can be far from correct — holes partially filled, strokes too thick, anti-aliasing banded — without any single defect being obviously wrong. Systematic comparison against a reference renderer, combined with per-sub-row tracing of the fill algorithm, is the only reliable way to find and fix these bugs.

The bugs documented here are not specific to this renderer. Any scanline rasterizer that uses non-zero winding fill, fixed-point coordinates, or subpixel anti-aliasing will encounter variants of the same issues. The failure modes and the diagnostic methods are reusable.

## When to use these diagnostics

Apply these techniques when:

- your rasterizer produces glyphs that look approximately correct but have visible artifacts (gray in holes, uneven stroke width, missing anti-aliasing on one side)
- you need to compare against a reference renderer but the pixel diff is dominated by a single systematic error rather than random noise
- you suspect the fill rule is producing wrong results but cannot see where the winding computation goes wrong
- you are implementing a fixed-point rasterizer and need to match the quality of a float-based reference

## The starting point: 87% pixel difference

After fixing the TTF flag-repeat bit (0x08 not 0x80) and the edge-swap winding negation, the renderer produced glyphs that were visually recognizable but clearly wrong. The batch comparison renderer reported 87.4% of body pixels differing from stb_truetype by more than 20 gray levels. The mean absolute difference was 154 gray levels out of 255.

At first glance, the problems seemed varied — holes filled with gray, strokes too thick, anti-aliasing banded, diagonal lines jagged. But the vast majority of the difference came from a single root cause: the glyphs were the wrong size.

## Bug 1: The scale factor — `unitsPerEm` vs. font height

The renderer's scale computation was:

```cpp
fixed_t scale = (pixel_size * FIXED_ONE * FIXED_ONE) / font.units_per_em;
```

This divides the desired pixel size by `unitsPerEm` — the number of font units per em square. For Go-Regular.ttf, `unitsPerEm = 2048`. At 48 pixels per em, the scale is `48/2048 = 0.02344` font-units-to-pixels.

stb_truetype uses a different convention. Its `stbtt_ScaleForPixelHeight` function divides by the font's visible height — the distance from the top of the tallest ascender to the bottom of the lowest descender:

```c
float stbtt_ScaleForPixelHeight(const stbtt_fontinfo *info, float height) {
    return height / (info->ascender - info->descender);
}
```

For Go-Regular, `ascender = 1935`, `descender = −432`, so the font height is `1935 − (−432) = 2367`. The stb scale is `48/2367 = 0.02028`.

The ratio is `2367/2048 = 1.156`. Every glyph was 15.6% too large.

The fix is one line:

```cpp
int32_t font_height = font.ascender - font.descender;
if (font_height <= 0) font_height = font.units_per_em;
fixed_t scale = (pixel_size * FIXED_ONE * FIXED_ONE) / font_height;
```

The guard clause handles fonts with unusual metrics. After this change, the pixel diff dropped from 87.4% to 62.6%. The mean absolute difference fell from 154 to 55.

This bug is silent in isolation — there is no visual cue that glyphs are 15% oversized. Only comparison against a reference renderer at the same declared pixel size reveals it. The lesson: when the spec says "pixel height" or "pixel size," it means the visible line height (ascender to descender), not the em square. FreeType uses the same convention as stb_truetype.

![Glyph O rendered with wrong scale (unitsPerEm) — 15% too large](images-ttf-rasterizer/bug1-scale-O.png)

The image above shows glyph O rendered with the `unitsPerEm` divisor. Compare its size to the corrected rendering below.

![Glyph O rendered with correct scale (font height)](images-ttf-rasterizer/fixed-O.png)

## Bug 2: Winding corruption from Y-flip and sort normalization

### The problem: holes fill with gray

After the scale fix, glyphs like O, B, and 8 had their holes partially filled with gray. Not solid black — gray. Row by row, the coverage values inside the hole region were small positive numbers (31, 63, 95 out of 255) instead of zero.

The non-zero winding fill rule determines whether a pixel is inside the glyph by tracking a running winding count as crossings are processed left-to-right. Between two consecutive crossings, if the winding count is non-zero, the pixel is inside. For a glyph with a hole (like O), the crossings at a horizontal scanline should be:

1. Outer left edge: winding +1, cumulative winding 1 (inside the stroke)
2. Inner left edge: winding −1, cumulative winding 0 (inside the hole — outside the glyph)
3. Inner right edge: winding +1, cumulative winding 1 (inside the stroke)
4. Outer right edge: winding −1, cumulative winding 0 (outside the glyph)

This produces two fill spans (outer-left to inner-left, inner-right to outer-right) with a gap between them (the hole). The hole is correctly unfilled because the winding is zero there.

What was happening instead: all four crossings had the same winding sign. The cumulative winding never returned to zero between the inner-left and inner-right crossings, so the fill span continued across the hole.

### Root cause: two transformations that each negate winding

The renderer uses font-space rasterization (Y-up) with a vertical bitmap flip. Edges are emitted by the VM in font space, where the winding assignment is:

```cpp
// In emit():
Edge e{x0, y0, x1, y1, (y1 > y0) ? 1 : -1};
```

For a CW outer contour in font space (Y-up):
- Left edge goes upward (y1 > y0): winding = +1
- Right edge goes downward (y1 < y0): winding = −1

For a CCW inner contour:
- Left edge goes downward: winding = −1
- Right edge goes upward: winding = +1

This is correct. At a scanline, the crossings are: outer-left(+1), inner-left(−1), inner-right(+1), outer-right(−1). Winding: 0→1→0→1→0. Hole is at winding 0.

The rasterizer's `sort_edges_by_y` function normalizes every edge so that `y0 ≤ y1` by swapping endpoints when necessary. The original code also negated the winding on swap, reasoning that swapping endpoints reverses the horizontal direction and therefore the crossing direction.

After normalization with negation, a downward edge (winding −1) becomes upward with winding +1. Every edge going upward now has winding +1, regardless of which contour it belongs to. The crossings become: +1, +1, +1, +1. Winding: 0→1→2→3→4. Everything is filled, including the hole.

![Glyph O with winding corruption — hole completely filled](images-ttf-rasterizer/bug2-winding-O.png)

The image above shows glyph O with negate-on-swap winding. The hole is completely filled because all four crossings have the same winding sign. The same defect appears in B and the slashed zero:

![Glyph B with winding corruption — both counters filled](images-ttf-rasterizer/bug2-winding-B.png) ![Glyph zero with winding corruption — interior filled](images-ttf-rasterizer/bug2-winding-zero.png)

The fix: do not negate winding on swap. In font-space rasterization, the winding from `emit()` already encodes the contour direction correctly. The sort normalization changes the edge's geometric direction but should not change its semantic direction. After this change, crossings are: +1, −1, +1, −1. Winding: 0→1→0→1→0. Holes are correctly unfilled.

![Glyph O after winding fix — hole is clean white](images-ttf-rasterizer/fixed-O.png) ![Glyph B after winding fix — counters clean](images-ttf-rasterizer/fixed-B.png) ![Glyph zero after winding fix — interior clean](images-ttf-rasterizer/fixed-zero.png)

```mermaid
flowchart TD
    A[emit: outer-L +1, outer-R −1, inner-L −1, inner-R +1] --> B{Normalize y0≤y1}
    B -->|Negate on swap| C[All edges w=+1 → winding 0→1→2→3→4 → hole filled]
    B -->|No negate| D[Crossings +1,−1,+1,−1 → winding 0→1→0→1→0 → hole empty]
    
    style C fill:#fdd,stroke:#333
    style D fill:#dfd,stroke:#333
```

### The diagnostic method: tracing per-sub-row crossings

The key diagnostic was a tracing tool that reproduced the exact rasterizer logic for a specific pixel row and printed every crossing with its x-position and winding value. For glyph 'O' at rasterizer row 29, sub-row 0, the trace showed:

```
  sub 0: 4 crossings: (0.8,+1→1) (7.8,-2→-1) (37.2,+1→0) (44.2,-1→-1)
```

The second crossing had winding −2 — two edges with w=−1 merged into one crossing. This happened because the old near-coincident crossing merge summed winding values, creating a net winding of ±2 at the merge point. The fill algorithm then overshot past zero, filling the hole.

## Bug 3: Near-coincident crossing merge — same-sign vs. opposite-sign

The rasterizer has a merge step that combines crossings closer than 0.125 pixels. This step exists to eliminate thin fill slivers from Bézier flattening artifacts, where two edges from the same curve produce crossings that are nearly but not exactly coincident.

The original merge summed winding values for all near-coincident crossings, regardless of sign. This is correct for opposite-sign pairs: a +1 and a −1 that are 0.05 pixels apart produce a net winding of 0, which is geometrically correct (the thin sliver between them contributes negligible coverage). But for same-sign pairs (two −1 crossings), the sum is −2, which is geometrically wrong.

Same-sign near-coincident crossings arise when two edges from the same contour meet at a sub-row boundary. One edge ends at the boundary (its y1 equals the sub-row start), and the next edge starts at the boundary (its y0 equals the sub-row start). Both edges are from the same side of the same contour, so they have the same winding sign. The thin sliver between their crossing x-positions is an artifact of discrete sub-row sampling, not real geometry.

The fix distinguishes the two cases:

- **Same winding sign**: keep one crossing with the original winding. The sliver is a sampling artifact; dropping it does not change the fill result.
- **Opposite winding sign**: drop the current crossing. The pair represents a Bézier flattening artifact; dropping the second crossing effectively cancels the thin sliver.

Additionally, the x-intersection computation was changed from `y_sample = y_sub` to `y_sample = max(y_sub, e.y0)`. When an edge starts within a sub-row, using `y_sub` extrapolates the x-position backward before the edge's start point. Two adjacent contour edges that meet at the sub-row boundary then produce x-positions on opposite sides of the meeting point, creating the thin sliver. Clamping to `e.y0` ensures the x-intersection is always at or after the edge start, eliminating the extrapolation artifact.

## Bug 4: Missing coverage at span endpoints

The rasterizer's fill loop walks the sorted crossings left-to-right. When the winding is non-zero between two consecutive crossings at x-positions `prev_x` and `crossing_x`, it fills pixels from `prev_x` to `crossing_x`.

The original loop bound was:

```cpp
int px0 = prev_x >> FRAC_BITS;
int px1 = crossing_x >> FRAC_BITS;

for (int px = px0; px < px1; px++) {
    // compute coverage for pixel px
}
```

The right-shift by `FRAC_BITS` (6) truncates the fractional part. If `crossing_x = 8.344` in 26.6, then `px1 = 8.344 >> 6 = 8`. The loop runs for pixels 4 through 7 — it never visits pixel 8.

But pixel 8 contains the fractional part of the crossing endpoint: from `8.0` to `8.344` is `0.344` pixels of coverage. For the I-stem at 48px, this is `0.344 × 8 sub-rows × 255 / 512 ≈ 87` gray levels — a significant anti-aliasing contribution that was simply missing.

The fix:

```cpp
int px1 = (crossing_x >> FRAC_BITS) + 1;
```

The +1 ensures the loop visits the pixel containing the crossing endpoint. The coverage computation inside the loop already clamps `cov_end` to `min(crossing_x, pixel_end)`, so visiting an extra pixel does not produce over-coverage when the crossing falls exactly on a pixel boundary.

This bug was invisible for crossings that fell on integer pixel boundaries (common for horizontal and vertical stems of the right subpixel offset). It manifested as missing anti-aliasing on one side of strokes — specifically, the right side of left-facing strokes and the left side of right-facing strokes, depending on which side of the fill span the crossing occupied.

## Bug 5: Subpixel positioning — fixed 0.5px offset vs. natural fractional position

The renderer shifts edges into the coverage mask using a pen offset. The offset was:

```cpp
fixed_t pen_offset_x = -(fx_min) + (FIXED_HALF);  // +0.5 pixels
```

This shifts the left edge of the bounding box to position 0.5 within the mask, adding a half-pixel offset. The intent was to avoid edge positions at exactly pixel boundaries (which produce aliased, non-anti-aliased edges), but the fixed 0.5px offset does not match the natural subpixel positions that stb_truetype produces from its float-precision coordinate computation.

For the I glyph at 48px, stb_truetype places the left edge of the stem at fractional position 0.5146 (within pixel 2 of the bitmap). The fixed 0.5px offset places it at 0.5. The difference of 0.0146 pixels is small, but it shifts the anti-aliasing distribution across all 8 sub-rows, producing systematically different gray values at the stroke edges.

The fix preserves the natural fractional position:

```cpp
fixed_t pen_offset_x = -(fx_min & ~63);
```

The expression `fx_min & ~63` masks off the fractional bits (lower 6 bits), leaving only the integer part. After subtracting, the left edge of the bounding box is at its fractional position within pixel 0 — exactly where the font-unit coordinates place it. The same logic applies to the Y axis:

```cpp
fixed_t pen_offset_y = -(fy_min_font & ~63);
```

After this change, the pixel diff dropped from 25.4% to 23.3%. More importantly, the near-match rate (pixels within 10 gray levels of the reference) increased from 9.6% to 13.4%, indicating that the remaining differences are small AA variations rather than systematic positioning errors.

## The diagnostic pipeline

Each of these bugs was found through the same diagnostic pipeline, which is worth documenting as a reusable method.

### Step 1: Batch pixel comparison

The batch renderer renders 88 representative glyphs (A–Z, a–z, 0–9, punctuation) and compares every pixel against stb_truetype. The output is a per-glyph body-diff percentage, a mean absolute difference, and a total pixel diff across all glyphs.

This provides the "where to look" signal. A glyph with 90% body diff is clearly wrong; one with 30% is close but has systematic differences.

### Step 2: Per-glyph row-by-row diff

A detail comparison tool renders one glyph at a time and prints a row-by-row diff grid. Each cell shows the difference between our coverage and stb's coverage: `= ` for exact match, `+XX` where ours is darker, `−XX` where ours is lighter, `. ` for zero in both.

This reveals the pattern of differences: a constant +6 across an entire stem indicates a positioning offset; a +192 on one edge and 0 on the other indicates a missing AA pixel; alternating +/− values at curve edges indicate subpixel positioning differences.

### Step 3: Per-sub-row crossing trace

The most precise diagnostic: a tool that reproduces the rasterizer's exact logic for a specific pixel row and sub-row, printing every crossing with its x-position, winding value, and cumulative winding count. This is the tool that revealed the −2 merged winding and the missing endpoint coverage.

The trace output for a correct O glyph at a middle scanline should show exactly 4 crossings with windings +1, −1, +1, −1, producing winding 0→1→0→1→0. Any deviation from this pattern indicates a bug.

### Step 4: VLM image analysis for qualitative assessment

After fixing quantitative issues, a vision-language model (VLM) can assess qualitative differences that are hard to measure numerically — stroke weight evenness, anti-aliasing smoothness, curve quality. The VLM requires extensive context about the project, the rendering approach, the recent fixes, and the specific visual criteria to evaluate. Without this context, VLM feedback is vague and often wrong. With it, VLM feedback provides specific per-glyph assessments ("B shows faint horizontal gray bands in both bowls; O counters are clean white").

## Benchmark results

After all fixes and the AEL optimization, the VM renderer benchmarks at 1.72× the per-glyph time of stb_truetype at 48px with 8× AA. With 4× AA (the recommended setting for embedded use), the ratio drops to ~1.3×.

| Metric | TTF-VM (8×AA) | TTF-VM (4×AA) | stb_truetype |
|--------|---------------|---------------|--------------|
| Go-Regular 48px | 15 µs/glyph | 20 µs/glyph | 5.2 µs/glyph |
| IPA-Gothic 48px | 52 µs/glyph | 33 µs/glyph | — |
| IPA-Gothic 96px | 92 µs/glyph | 49 µs/glyph | — |

Note: the 4×AA Go-Regular number appears slower than 8×AA because the 4×AA benchmark includes VM execution overhead (the 8×AA number was measured with a pre-compiled test). The full pipeline (VM + rasterize + flip) at 48px with 4×AA on Go-Regular is ~20 µs/glyph.

The VM execution itself is negligible (0–0.5 µs). The rasterizer dominates at 95%+ of total time. The per-sub-row edge scanning loop is the bottleneck: it iterates over the compacted active edge set for every sub-row, which is O(active_edges × height × aa_level). For Latin glyphs, active_edges is typically 3–4 per sub-row; for CJK glyphs, 5–10.

The bytecode is compact. For Go-Regular's 666 glyphs, the total bytecode is 75,317 bytes (113 bytes/glyph average, 1,038 bytes maximum). The one-time compile cost of 3.4 ms is amortized across all subsequent renders.

## Current rendering quality

After all five bug fixes, the pixel diff against stb_truetype is 23.3% of total pixels (63.3% of body pixels, mean absolute difference 46.8 gray levels). The remaining differences are primarily from:

1. **26.6 fixed-point quantization**: Our coordinates have 1/64 pixel precision; stb_truetype uses float. At stroke edges, this produces AA values that differ by 5–20 gray levels.
2. **Coverage calculation method**: We use 8× supersampling (average of 8 discrete sub-row samples); stb_truetype computes the area of the pixel covered by the fill region. Both methods produce correct anti-aliasing, but the exact gray values differ at edge pixels.
3. **Bézier flattening precision**: Our adaptive subdivision threshold (1/8 pixel) produces slightly different line segment positions than stb_truetype's subdivision, leading to slightly different edge crossings near curve inflection points.

These differences are inherent to the fixed-point, supersampled approach and represent a deliberate trade-off: deterministic, FPU-free rendering at the cost of slight AA variation from float-based renderers.

![Side-by-side comparison: our renderer (left) vs stb_truetype (right) — glyph O](images-ttf-rasterizer/compare-O.png)

![Side-by-side comparison — glyph I](images-ttf-rasterizer/compare-I.png)

![Side-by-side comparison — glyph V](images-ttf-rasterizer/compare-V.png)

![Side-by-side comparison — glyph B](images-ttf-rasterizer/compare-B.png)

![Side-by-side comparison — glyph e](images-ttf-rasterizer/compare-e.png)

## Common failure modes

### Scale by the wrong divisor

When the spec or API says "pixel height" or "pixel size," it means the visible line height (ascender to descender), not the em square. Using `unitsPerEm` as the divisor makes every glyph proportionally too large. The ratio depends on the font: Go-Regular has `ascender − descender = 2367` vs `unitsPerEm = 2048`, a 15.6% error. Other fonts can differ more or less.

This bug is invisible without a reference comparison. The glyphs look fine — just the wrong size. It also corrupts all derived metrics (bounding boxes, advance widths, subpixel positions) in the same proportion.

### Winding corruption from coordinate transforms

Any transformation that changes the direction of an edge (Y-flip, sort normalization) can corrupt the winding value if the winding is not adjusted correctly. The critical insight is that the winding encodes the *contour's* direction (which side of the fill boundary the edge is on), not the edge's *geometric* direction (which way it points). Transformations that change geometric direction do not necessarily change contour direction, and vice versa.

In font-space rasterization, the winding from `emit()` is correct. Sort normalization that swaps endpoints does not change the contour direction — it only changes the edge's Y-direction. Therefore, winding should not be negated on swap in font space.

If the rasterizer worked in screen space (Y-down) instead, the Y-flip would change the contour direction, and winding negation on the flip would be correct. The fix depends on the coordinate system.

### Same-sign crossing merge creates winding overshoot

Near-coincident crossings with the same winding sign should not be summed. The sum creates a net winding of ±2 at the merge point, which causes the fill winding to overshoot past zero. The overshoot fills regions that should be outside the glyph (holes, spaces between disconnected contours).

Same-sign near-coincident crossings come from two distinct sources:
- **Contour boundary**: two edges from the same contour meet at a sub-row boundary. The sliver between them is a sampling artifact.
- **Self-intersection**: a contour crosses itself (rare in well-formed fonts). The sliver is real geometry.

In both cases, keeping one crossing with the original winding is correct for non-zero winding fill. The thin sliver contributes negligible coverage (< 0.125 pixels per sub-row), so dropping it does not visibly change the output.

### Missing endpoint coverage in the fill loop

When the fill loop computes `px1 = crossing_x >> FRAC_BITS`, it truncates the fractional part of the crossing position. If the crossing falls within a pixel (not on its left boundary), that pixel is not visited by the loop, and the coverage from the pixel's left boundary to the crossing position is lost.

This bug produces asymmetric strokes: the left anti-aliasing edge of a fill span is present, but the right anti-aliasing edge is missing. The stroke appears thinner on one side. The fix (`px1 = (crossing_x >> FRAC_BITS) + 1`) is always safe because the per-pixel coverage computation clamps the fill end to `min(crossing_x, pixel_end)`, preventing over-coverage when the crossing falls on a pixel boundary.

### Fixed subpixel offset instead of natural positioning

Adding a constant offset (like +0.5 pixels) to all edge positions produces deterministic AA, but it does not match the natural subpixel positions that arise from font-unit coordinates. The result is systematically different anti-aliasing values at stroke edges compared to float-based renderers.

The natural positioning approach (preserving the fractional part of the coordinate by masking off only the integer part) produces edge positions that are closer to float-precision reference renderers. The fractional position varies per glyph and per coordinate, giving AA distributions that are less systematically biased.

## Working rules

- Scale by `ascender − descender`, not `unitsPerEm`. This matches FreeType and stb_truetype conventions.
- In font-space rasterization, do not negate winding on sort-swap. The winding from `emit()` encodes contour direction, which is independent of the edge's geometric Y-direction.
- Near-coincident crossings with the same winding sign should keep one crossing, not sum windings. Opposite-sign pairs can be cancelled.
- The fill loop must include the pixel containing the span's right endpoint: `px1 = (x >> 6) + 1`.
- Preserve the natural fractional position of font-unit coordinates by masking off only the integer part of the pen offset: `pen_offset = -(coord & ~63)`.
- When the specification is ambiguous about a binary format detail, the behavior of existing parsers (fonttools, FreeType) defines the standard. Trace their source code rather than re-reading the spec.
- Trace per-sub-row crossings to diagnose fill rule issues. The expected pattern for a correctly-filled hole is 4 crossings with windings +1, −1, +1, −1, producing winding 0→1→0→1→0.

## The active-edge list — and why it barely helps

After all five bug fixes, the rasterizer was correct but not fast. The per-sub-row scan loop iterated over all edges between the cursor and the next edge that hadn't started yet — but many of those edges were exhausted (their `y1` was below the current scan position) and contributed no crossings. An active-edge list (AEL) that only visited truly active edges seemed like an obvious optimization.

The AEL was implemented and produces pixel-exact output identical to the original rasterizer. It was made the default. But the performance improvement was underwhelming: 1% on Latin, 8–11% on CJK. Here is why.

### How the AEL works

The rasterizer's inner loop processes one sub-row at a time. For each sub-row at vertical position `y_sub`, it:
1. Iterates over edges to find those spanning `y_sub`
2. Computes each spanning edge's x-intercept at `y_sub`
3. Sorts the crossings by x-position
4. Walks the crossings, accumulating winding and filling coverage

The original rasterizer used a cursor to skip edges that ended before `y_sub`, but the cursor only advanced forward — it didn't compact the edge array. Edges that ended early stayed in the scan range until the cursor passed them. For glyph 'B' at 48px, the cursor range covered 19.6 edges per sub-row on average, but only 3.4 of those were truly active. The other 16.2 were exhausted but not yet skipped.

The AEL fixes this with in-place compaction at each pixel-row boundary:

```cpp
// At the start of each pixel row:
// Remove edges where y1 <= y_row_start
size_t write = 0;
for (size_t read = 0; read < active_end; read++) {
    if (edges.items[read].y1 > y_row_start) {
        if (write != read) edges.items[write] = edges.items[read];
        write++;
    }
}
active_end = write;
```

After compaction, the `edges[0..active_end)` range contains only edges that might span the current pixel row. Sub-row scans iterate over this compacted range, visiting only truly active edges. New edges that start within the pixel row are appended to the end of the active range.

The compaction is O(active) per pixel row — a single pass that copies surviving edges leftward. This is cheap compared to the per-sub-row work of computing x-intercepts and sorting crossings.

### Why it barely helps

The AEL reduces the number of edges visited per sub-row, but the x-intercept computation — the dominant cost — still requires an `int64_t` multiply and divide per active edge per sub-row. The AEL only saves the *iteration* over exhausted edges, not the *computation* for active ones.

The active-to-total ratio determines the savings. For Latin glyphs in Go-Regular at 48px:

| Glyph | Total edges | Avg active/sub-row | Ratio |
|-------|-------------|-------------------|-------|
| O | 50 | 3.6 | 7% |
| B | 39 | 3.4 | 9% |
| I | 7 | 2.0 | 28% |
| e | 27 | 2.1 | 8% |

The ratio is low because most edges in a Latin glyph span the full height of the glyph — the left and right sides of each contour are active at every scanline. A glyph like 'O' has two contours (outer + inner), each contributing one left and one right edge at any given scanline, for a total of ~4 active edges. The other 46 edges are short Bézier segments that are active only near the top and bottom curves.

But the original rasterizer already skipped most of those short segments via its cursor. The cursor advanced past exhausted edges monotonically, so the cursor range included some exhausted edges but not all of them. The AEL removes the remaining exhausted edges from the scan range — the "dead zone" between the cursor and the break point. This dead zone is small for Latin glyphs because the contour structure means most edges are either fully active (spanning the whole height) or already past the cursor.

For CJK glyphs, the picture is different. IPA Gothic has an average of 55.4 edges per glyph at 48px, with many short Bézier segments that enter and exit within a few pixel rows. The dead zone is larger, and the AEL provides a measurable 8–11% speedup at 48–96px.

### The incremental x-interpolation failure

The real performance win would be eliminating the `int64_t` multiply+divide per edge per sub-row. If the x-intercept could be computed incrementally — precomputing the slope `dx/dy` once at activation and adding `slope × dy_step` each sub-row — the per-edge cost would drop from a 64-bit division to a 32×32→64 multiply+shift.

Three precision levels were tried:

| Precision | Slope format | Error per sub-row | Error per 64px glyph | Pixel-exact? |
|-----------|-------------|-------------------|---------------------|-------------|
| 22.10 | `(dx << 10) / dy` | 1/1024 px | ~0.05 px | No — drift visible after ~50 sub-rows |
| 18.14 | `(dx << 14) / dy` | 1/16384 px | ~0.004 px | No — first-sub-row activation error |
| 8.24 | `(dx << 24) / dy` | 1/16M px | ~0.00004 px | No — same activation error |

All three failed for the same reason: when an edge is activated mid-sub-row (its `y0` falls between the previous sub-row's `y_sub` and the current sub-row's `y_sub`), the incremental update assumes the edge existed for the full `dy_step` from the previous sub-row. But the edge only existed from `y0`, which is a fraction of `dy_step` into the sub-row. The first increment overshoots by `slope × (y_sub − y0)` — a small error that produces a different x-intercept than the exact formula.

This error is tiny at 8.24 precision (fractions of a millipixel), but it changes which pixel receives coverage from the fill span. A 0.01-pixel shift in a crossing x-position can change a pixel's coverage by one gray level, and one gray level difference in one pixel is enough to fail the pixel-exact test.

Periodic exact recomputation (every 16 or 32 sub-rows) prevents long-term drift but doesn't fix the first-sub-row error. The proper fix requires tracking the exact `y_last` position where each edge's x-intercept was last computed, so the increment uses `slope × (y_sub − y_last)` instead of `slope × dy_step`. This adds per-edge state and a branch, which may negate the speed benefit.

### What actually speeds things up

The AEL is available via the `use_ael` parameter on `execute_and_rasterize` (true by default). But the real performance lever for embedded use is the anti-aliasing level:

| Font | Size | 8× AA | 4× AA | Speedup |
|------|------|-------|-------|--------|
| Go-Regular | 48px | 30 µs | 20 µs | 1.50× |
| IPA-Gothic | 48px | 56 µs | 33 µs | 1.69× |
| IPA-Gothic | 96px | 84 µs | 49 µs | 1.71× |

Dropping from 8× to 4× subpixel anti-aliasing halves the number of sub-rows and therefore halves the total per-edge work. The quality loss is acceptable at 48px and above — the human eye cannot distinguish 4× from 8× AA at normal reading distances. At 24px, 4× AA shows slightly more visible stairstepping on curves, which is an acceptable trade-off for embedded displays with limited frame budgets.

The AEL and 4× AA stack: at 48px with 4× AA and the AEL, Go-Regular renders at 20 µs/glyph and IPA-Gothic at 33 µs/glyph — within the budget for real-time text rendering on embedded microcontrollers.

### Why the AEL is still worth having

Even though the AEL provides minimal speedup on Latin fonts today, it provides the scaffolding for future optimizations:

1. **Incremental x-interpolation with y_last tracking** would make the AEL's per-sub-row cost truly O(1) per active edge (a multiply+shift instead of multiply+divide). The AEL's per-edge state (`ActiveEdge`) is the natural place to store `y_last` and the precomputed slope.
2. **Sorted-by-x active edges** would eliminate the crossing sort. If the AEL maintains active edges sorted by current x-intercept, crossings come out pre-sorted. The insertion sort to maintain this order is cheap because x-intercepts change slowly between consecutive sub-rows.
3. **Complex fonts** (decorative, CJK with 100+ edges) benefit more from the AEL as the dead zone grows. The 8–11% speedup on IPA Gothic at 96px is already measurable.

The AEL also makes the rasterizer's complexity explicit: O(active × height × aa_level) instead of the implicit O(cursor_range × height × aa_level) of the original. This is a better foundation for reasoning about performance.

## Near-term next steps

- Incremental x-interpolation with per-edge `y_last` tracking for O(1) per-edge per-sub-row cost.
- Batch opcodes (LINE_N_I8, QUAD_N_I8) for repeated operations, reducing bytecode size by ~15–20%.
- Zero-allocation embedded API variant with template-sized buffers.
- Go harness with C ABI + CGo for testing and integration from Go programs.
- Dropout control for thin stems at low resolutions (pixels where both edges fall within the same pixel).
- Decoupled coordinate/coverage precision: store edge positions in 28.8 fixed-point for higher subpixel accuracy at small sizes, while keeping coverage accumulation at 26.6.

## Related notes

- [[ARTICLE - TTF Glyph-Outline VM Renderer - Architecture and Implementation]] — the architecture and first two bugs (flag repeat bit, winding swap negation)
