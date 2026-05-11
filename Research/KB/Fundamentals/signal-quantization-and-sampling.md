---
title: "Signal Quantization and Sampling Theory"
aliases:
  - quantization theory
  - sampling theorem
  - Nyquist
  - dithering theory
tags: [knowledge-base, fundamental, signal-processing, quantization, sampling]
status: active
type: knowledge-base
created: 2026-05-11
---

# Signal Quantization and Sampling Theory

> [!summary]
The theory behind why dithering works: when you reduce an image from 256 gray levels to 2, quantization error is inevitable. Properly applied dithering converts that amplitude error into high-frequency noise, which the human visual system barely perceives. This entry covers the key results that affect our thermal printing and e-ink rendering work.

## The core idea

Quantization is the process of mapping a large set of input values to a smaller set. When you convert an 8-bit grayscale image (256 levels) to a 1-bit image (2 levels), every pixel's gray value gets rounded to either 0 or 255. The difference between the original value and the rounded value is the **quantization error**.

If you round naively (threshold at 128), the error is systematic: every pixel in the 100–127 range becomes white when it should be dark gray. This creates visible banding and lost midtones.

The key insight: **adding noise before quantization converts amplitude distortion into noise**. The total error is the same, but its character changes. Instead of large contiguous regions being wrong by the same amount, individual pixels are wrong by random amounts. The eye integrates over local regions and perceives the average — which approximates the original value.

## Why it matters to our work

Three of our KB entries depend on this theory:

- **On-Ramp: Dithering and Rasterization** — The algorithms (Floyd-Steinberg, Atkinson, blue-noise ordered dithering) are all implementations of "structured quantization error distribution." Without understanding the theory, you can't tune them.
- **On-Ramp: ESC/POS Thermal Printer Commands** — The printer is a 1-bit device. Every image must be quantized. The choice of dithering algorithm directly affects print quality.
- **On-Ramp: E-Ink Display Driving** — E-ink panels have even fewer output levels than thermal paper (some only support 2-level or 4-level output). Quantization is the fundamental constraint.

Our projects keep running into the same class of bugs: images that are too dark, too light, or missing detail in shadows. These are all quantization artifacts. Understanding the theory prevents treating dithering as a black box.

## The key result

**Roberts' theorem (1962)**: The optimal way to quantize a signal for perceptual quality is to add dither noise with a specific probability distribution before quantization, then average over multiple samples (or, equivalently, over the local spatial neighborhood in an image).

In plain language: **dithering before quantization is provably better than quantizing without dithering**. The error is the same in total, but it's distributed as noise rather than as structured distortion.

For 1-bit image dithering, the practical consequence is:

- **Ordered dithering** (Bayer, blue-noise) adds a deterministic threshold pattern before quantization. The resulting noise has a specific frequency spectrum (grid pattern for Bayer, high-frequency for blue noise).
- **Error diffusion** (Floyd-Steinberg, Atkinson) quantizes each pixel and distributes the error to neighbors. This is a feedback system — the error propagates and creates correlated textures, but the local average density approximates the original gray level.

## The intuition behind the key result

Imagine you're drawing a grayscale ramp on a 1-bit display. Without dithering, the left half is solid white and the right half is solid black, with a hard step at the 50% gray point.

Now imagine flipping a weighted coin for each pixel: if the gray level is 30%, the coin has a 30% chance of landing black. Over a 10×10 pixel region, roughly 30 pixels will be black. From a distance, the region looks 30% gray. This is random dithering — it works, but the noise is clumpy because random clusters happen by chance.

Now imagine the same thing, but you space the black dots as evenly as possible (like a blue-noise mask). Same 30% density, but the dots are uniformly distributed. This looks smoother because the human eye is less sensitive to high-frequency uniform patterns than to random clumping.

Finally, imagine a smarter system: for each pixel, look at how far off your last few decisions were, and adjust the current decision to compensate. If you've been making too many pixels black recently, lean toward white for the next one. This is error diffusion — it minimizes the running error, producing the most accurate local density at the cost of correlated textures ("worms").

All three approaches produce the same average density. They differ in the spatial distribution of the error. The choice between them is a perceptual tradeoff, not a correctness tradeoff.

## What goes wrong when you don't know this

1. **SToMS3R: photos printing as solid black rectangles** — Using fixed threshold on a dark photo: all pixels below 128 become black, all above become white. No midtones survive. The cause is naive quantization without dithering. (DITHER-001 report documents this in detail.)

2. **Gnosis: e-ink ghosting accumulation** — Repeated partial refreshes without periodic full-quality refresh cause ghost images. This is a quantization artifact specific to e-ink: the display's limited waveform modes can't perfectly represent intermediate states, and the residual error accumulates.

3. **Almanach: dithered photos too dark on thermal paper** — Floyd-Steinberg dithering produces accurate density on screen, but thermal paper has dot gain (each black dot spreads). The result prints darker than it looks on screen. The fix is gamma correction before dithering — pre-compensating for the medium's non-linear response. Without understanding quantization theory, gamma correction seems like an unrelated brightness knob. With it, you understand it as pre-distortion of the input signal to compensate for the medium's transfer function.

## Where we use it

- [[On-Ramp/dithering-and-rasterization]]
- [[On-Ramp/esc-pos-thermal-printer]]
- [[On-Ramp/e-ink-display-driving]]

### Related PARC project reports

- [[PROJ - SToMS3R - AtomS3R Lite Thermal Printer Firmware]] — quantization without dithering produces solid black rectangles
- [[PROJ - Gnosis Layout Engine - PaperS3 UI Operating System]] — e-ink ghosting as quantization artifact accumulation

## Where to go deeper

1. **Ulichney, R. A. (1987)**. "Dithering with Blue Noise." *Proceedings of the IEEE*, 76(1), 56–79. — The foundational paper connecting quantization theory to blue-noise dithering.
2. **Lau, D. L. & Arce, G. R. (2008)**. *Modern Digital Halftoning*. CRC Press. — The standard textbook; Chapters 1–3 cover quantization and sampling theory in depth.
3. **DITHER-001 deep research report** in this PARC library — Our own exhaustive treatment of dithering algorithms for thermal printing, including comparison matrices and hardware evaluation plans.
