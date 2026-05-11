---
title: "1-Bit Image Dithering and Rasterization"
aliases:
  - dithering
  - halftoning
  - floyd-steinberg
  - atkinson dithering
  - ordered dithering
  - 1-bit image
tags: [knowledge-base, on-ramp, dithering, halftoning, image-processing, thermal-printer, e-ink]
status: active
type: knowledge-base
created: 2026-05-11
---

# 1-Bit Image Dithering and Rasterization

> [!summary]
> When a display or printer can only produce black and white — no gray — you need dithering to approximate continuous tones. This entry covers the three families of dithering algorithms we use (ordered, error diffusion, blue-noise), the one we recommend for thermal printing (Atkinson), and the gamma correction that makes it work on physical media. For the full mathematical treatment, see [[signal-quantization-and-sampling]].

## The idea in one paragraph

A grayscale image has 256 levels per pixel. A 1-bit device has 2. Dithering is the process of converting the former into the latter while preserving the appearance of continuous tone. It works by exploiting the human visual system's tendency to average over local regions: a 10×10 patch where 30% of pixels are black looks gray, not like 30 black pixels and 70 white ones. The choice of *which* 30 pixels to make black determines the quality of the result.

## The three families

### Ordered dithering (Bayer, clustered-dot)

A fixed threshold matrix is tiled across the image. Each pixel is compared against the threshold at its position. The Bayer matrix produces a characteristic cross-hatch pattern. Clustered-dot dithering groups dots together to simulate ink spreading on paper.

```
2×2 Bayer matrix:
  0  2
  3  1

Scaled to 0–255:
   0  128
 192  64
```

**Strengths**: No error propagation — each pixel is independent. Fast. Deterministic. No "worm" artifacts.
**Weaknesses**: Visible cross-hatch pattern at low resolutions. The pattern competes with image detail.
**When to use**: When speed matters more than quality, or when the output device has strong dot gain (clustered-dot groups dots to counteract spreading).

### Error diffusion (Floyd-Steinberg, Atkinson, Stucki)

Each pixel is quantized individually. The quantization error (the difference between the original gray and the output black/white) is distributed to neighboring pixels that haven't been processed yet. Different algorithms distribute the error differently:

```
Floyd-Steinberg error diffusion:      Atkinson error diffusion:
            X   7/16                           X   1/8  1/8
    3/16  5/16  1/16                     1/8  1/8  1/8
    1/16                             1/8
```

Atkinson distributes only 6/8 of the error (75%), dispersing it over a wider area. This produces lighter output — crucial for thermal paper, where each black dot spreads (dot gain), making the image darker than it appears on screen.

**Strengths**: No visible pattern. Preserves detail better than ordered dithering. Adjustable error distribution.
**Weaknesses**: Processing is sequential (can't parallelize). Error propagation creates correlated textures ("worms" in Floyd-Steinberg). Sensitive to the processing order.
**When to use**: When quality matters more than speed. For thermal printing, use Atkinson over Floyd-Steinberg.

### Blue-noise dithering

A pre-computed threshold map with blue-noise spectral properties (high-frequency energy, minimal low-frequency clustering) is tiled across the image. The result looks like random dithering but with uniform dot distribution — no clumping, no cross-hatch.

**Strengths**: Best visual quality at high resolutions (300+ DPI). No visible pattern. Each pixel is independent (parallelizable).
**Weaknesses**: Requires a pre-computed blue-noise map (typically 64×64 or 128×128). Quality degrades at low resolutions. The map is resolution-dependent.
**When to use**: When you have high DPI output and want the best possible quality without error diffusion's sequential processing.

## Our recommendation for thermal printing

**Atkinson dithering with gamma 1.8 pre-correction.** This is what we implement first for any thermal printer project. The reasoning:

1. **Atkinson's 75% error diffusion produces lighter output**, which compensates for thermal paper's dot gain. Floyd-Steinberg's 100% diffusion produces accurate density on screen, but each black dot on thermal paper spreads ~1.2×, making the overall image too dark.

2. **Gamma 1.8 before dithering** compensates for the medium's non-linear transfer function. On a screen, gray 128 looks 50% bright. On thermal paper, a 50% duty cycle looks ~65% dark because of dot gain. Applying gamma 1.8 (`gray = 255 * (gray/255)^1.8`) makes midtones lighter before dithering, so the dot-gain-darkened result lands closer to the intended brightness.

3. **Both must be calibrated on real hardware.** The gamma value (1.8) is a starting point, not a constant. It depends on the specific paper, printhead temperature, and printing speed. Print a grayscale ramp, measure the density at each step, and fit a curve. The gamma that makes the measured density match the input gray level is the correct gamma for that hardware.

## Rasterization: from dithered image to printer bytes

After dithering, the image is a 2D array of 0s and 1s. The printer expects this as packed bytes, one bit per pixel, MSB-first:

```go
bytesPerRow := (width + 7) / 8
data := make([]byte, bytesPerRow*height)
for y := 0; y < height; y++ {
    for x := 0; x < width; x++ {
        if dithered[y][x] == 1 { // black pixel
            data[y*bytesPerRow+x/8] |= byte(0x80) >> (x % 8)
        }
    }
}
```

The packed bytes are wrapped in the ESC/POS `GS v 0` raster command (see [[esc-pos-thermal-printer]]) and sent to the printer as one continuous stream (see [[encoding-and-framing]]).

## Where to go deeper

- [[Fundamentals/signal-quantization-and-sampling]] — The theory behind why dithering works.
- [[On-Ramp/esc-pos-thermal-printer]] — How to send the dithered image to the printer.
- **DITHER-001 deep research report** in this PARC library — Exhaustive treatment of 6 algorithm families, comparison matrices, hardware evaluation plans, and a 6-phase implementation roadmap.
- [[PROJ - SToMS3R - AtomS3R Lite Thermal Printer Firmware]] — Atkinson dithering + gamma 1.8 in the browser, 1-bit bitmap to K118 printer
