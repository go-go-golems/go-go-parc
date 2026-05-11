---
title: "E-Ink Display Driving"
aliases:
  - eink
  - e-ink
  - epd
  - epaper
  - partial refresh
  - waveform mode
tags: [knowledge-base, on-ramp, e-ink, epd, display, embedded, esp32]
status: active
type: knowledge-base
created: 2026-05-11
---

# E-Ink Display Driving

> [!summary]
> E-ink displays are bistable — they hold an image with zero power — but refreshing them is slow and produces visible artifacts. The key architectural decision is when to use partial refresh (fast, accumulates ghosting) vs. full refresh (slow, clean). This entry covers the waveform modes, the ghosting problem, the four-stage rendering pipeline that minimizes refreshes, and the hardware-specific quirks of the panels we use.

## The idea in one paragraph

An electrophoretic display (e-ink) moves charged pigment particles inside microcapsules. A positive voltage drives white particles to the top; a negative voltage drives black particles. The particles stay where they are when power is removed — this is the bistable property. But moving particles takes time (50–800ms per region), and the movement is imperfect — some particles don't quite reach their destination, leaving a faint ghost of the previous image. Each refresh cycle is a tradeoff between speed and fidelity.

## The two refresh modes

**Full refresh** (also called "full update" or "quality mode"): The display controller drives every pixel through a complete black→white→black→final cycle. This clears residual charge, repositions all particles, and produces a clean image. It takes 300–1000ms and produces a visible flash (the screen goes black, then white, then the final image). Use this for initial display, periodic cleanup, and when switching between unrelated screens.

**Partial refresh** (also called "partial update" or "fast mode"): The display controller drives only the pixels that changed, and only to their final state (no black→white→black cycle). This takes 50–200ms and produces no flash. But residual charge from previous images is not cleared, so ghost images accumulate. Use this for frequent updates to the same screen (a clock, a gauge, a changing value).

The tradeoff is simple: **partial refresh is fast but accumulates ghosting; full refresh is clean but slow and flashing.** The architectural pattern that resolves this tradeoff is:

> Use partial refresh for most updates. Schedule a full refresh every N partial updates (or after a timeout, or when the user requests it). This is the "cheap partial + periodic full clean" pattern.

## The ghosting problem

Ghosting is the visible residue of previous images. It happens because electrophoretic particles don't move perfectly. After a partial refresh, some particles that should be white are still slightly dark, and vice versa. The effect is cumulative — each partial refresh adds more residual charge.

Mitigation strategies:

1. **Periodic full refresh**: After 10–20 partial refreshes, do a full refresh. This is our standard approach (Gnosis, PaperS3).

2. **Dark-to-light is worse than light-to-dark**: A pixel that was black and becomes white shows more ghosting than a pixel that was white and becomes black. If you can design your UI to avoid black→white transitions (use white backgrounds, thin black lines), ghosting is less visible.

3. **Unchanged regions don't ghost**: If a pixel stays the same color between refreshes, it doesn't accumulate residual charge. This is why dirty-rectangle tracking (see [[rendering-pipeline-fundamentals]]) is important — only refresh the regions that changed.

4. **Temperature affects ghosting**: Cold temperatures slow particle movement, making ghosting worse. Some display controllers compensate by adjusting drive voltage based on temperature sensor readings. If your device has a temperature sensor, pass it to the display driver.

## The waveform mode selection

The IT8951 controller (used by PaperS3 and many 6"/7.6" e-ink panels) defines waveform modes in its LUT (Look-Up Table). The ones we use:

| Mode | Name | Speed | Quality | When to use |
|------|------|-------|---------|-------------|
| `epd_text` | Text | ~50ms | Good for new content, ghosts on dark→light | Most partial updates (clocks, gauges, labels) |
| `epd_quality` | Quality | ~800ms | Clean, no ghosting | Periodic cleanup, screen transitions |
| `epd_fast` | Fast | ~30ms | Poor, visible ghosting even on first update | Rarely — only for rapid prototyping |
| `epd_gray4` | 4-level gray | ~200ms | 4 gray levels | Images, gradients (limited use on 1-bit panels) |

Our standard selection strategy: `epd_text` for every partial dirty-rect refresh. `epd_quality` every 10th refresh or when switching screens. Never `epd_fast` in production.

## The four-stage pipeline

For e-ink, the rendering pipeline from [[rendering-pipeline-fundamentals]] takes a specific form:

1. **Layout**: Compute widget positions from the declarative screen description.
2. **Update**: Apply data changes; mark affected widgets as dirty.
3. **Collect + Merge**: Gather dirty rectangles from all dirty widgets. Merge overlapping rectangles into larger regions. The merge reduces the number of separate partial-refresh operations — one large refresh is better than several small ones (fewer display controller commands, fewer visual transitions).
4. **Render + Refresh**: Redraw only the merged dirty regions. Send each region as a partial-refresh command to the display controller. The controller updates only those pixels.

## The hardware we use

| Device | Controller | Resolution | Panel | Notes |
|--------|-----------|------------|-------|-------|
| M5Paper S3 | IT8951 | 960×540 | 4.7" monochrome | Good partial refresh, moderate ghosting |
| reMarkable 2 | custom | 1872×1404 | 10.3" monochrome | Excellent partial refresh, CAN driver |
| K118 | N/A | 384×∞ | 58mm thermal | Not e-ink, but same dirty-rect patterns apply |

## Where to go deeper

- [[Fundamentals/rendering-pipeline-fundamentals]] — The general pipeline that e-ink driving instantiates.
- [[On-Ramp/dithering-and-rasterization]] — How to prepare images for 1-bit e-ink panels.
- **Gnosis project report** in this PARC library — Our implementation of the four-stage pipeline on PaperS3.
- [[PROJ - Gnosis Layout Engine - PaperS3 UI Operating System]] — the complete e-ink render pipeline with dirty-rect tracking and waveform mode selection
