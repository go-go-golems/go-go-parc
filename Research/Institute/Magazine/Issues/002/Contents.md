# One Bit at a Time

## The Engineering of Thermal Printing

*Issue 002 — The Golem Review*

---

A thermal receipt printer can do two things. It can heat a spot on the paper, or it can leave the spot alone. Everything it produces — a line of text, a photograph, a barcode — is built from the accumulated record of those binary decisions. There is no ink, no pen that traverses the page, no shade of gray. A dot is either burned or it is not.

The simplicity is misleading. Behind the binary interface stands a coupled physical system: a line of resistive heaters that must be energized in patterns, a motor that must advance paper with micron-scale repeatability, a power rail that sags under load, a chemical paper that responds non-linearly to heat, and a host computer that must decide, for every dot on every line, whether to burn or to refrain. A page rendered on a conventional display carries two hundred fifty-six levels of gray per channel. The entire problem of thermal image quality is the problem of collapsing that representation into one bit per dot without losing what the eye cares about.

This issue addresses that collapse in four stages, following the data from the heater to the glyph.

---

## In This Issue

**1. The Thermal Print Head: Heat, Paper, and the Physics of a Single Dot**

A one-bit output device is, physically, an array of heaters. The first article opens with the mechanism — the 384-dot head at 203 dots per inch, the stepper-driven platen, the thermal paper that records energy as density. It develops the energy equation that governs every dot, derives why a ten-percent voltage sag costs roughly twenty percent of the delivered energy, and traces the command path from the host to the heater. The `GS v 0` raster command and the byte arithmetic that predicts when a serial link will starve a moving head are developed from the framing invariant upward.

**2. Dithering: Simulating Continuous Tone with Black and White**

Given a device that can only burn or refrain, dithering is the arrangement of dots that makes a region read as gray. The second article develops the three algorithmic families — thresholding, ordered dithering, and error diffusion — from the quantization of a single pixel. It then confronts the medium: thermal paper exhibits dot gain, in which each burned dot spreads, so an algorithm that is tonally accurate on a screen prints too dark on paper. The resolution is a calibrated trade between the tone curve, the diffusion kernel, and the printer's heat, settled by physical test.

**3. From Outline to Pixel: Rasterizing TrueType Glyphs**

Before any dot can be burned, the glyphs of a page must be rendered into pixels. The third article descends into the scanline rasterizer that converts TrueType outlines into antialiased coverage, and treats the four failure modes that silently degrade glyph quality — a scale divisor chosen from the wrong font metric, a winding value corrupted by a coordinate transform, a span endpoint whose coverage is truncated, and a subpixel position forced to an arbitrary offset. Each is a small, localized defect whose global effect is a glyph that looks almost right.

**4. Crisp Text on a One-Bit Device: Hinting, Heat, and the Limits of Algorithms**

The final article synthesizes the preceding three in the hardest case: small text. It begins with a paradox — heat cannot repair strokes that vanished before the bitmap reached the printer — and follows an investigation that reverses its own conclusion twice, from a bitmap web font to supersampling to the act of disabling anti-aliasing. The principle that emerges is that on a one-bit device, legibility is governed more by a font's hinting and its size than by any conversion algorithm layered on top. The article closes with the per-segment heat scheme that lets a single page burn its text hot and its photographs cool.

---

## A Note on Evidence

The technical content of this issue is grounded in a working thermal-printing pipeline: an ESP32 host driving an M5Stack K118 class mechanism over UART, rendering pages with headless Chrome, and converting the result to a packed one-bit bitmap in Go. Values cited for density, speed, gamma, and dithering kernels were confirmed by printing on physical paper and reading the results, not by inspecting screen previews. Where a decision could only be made empirically, the article says so. Where a decision follows from arithmetic or from the structure of the algorithm, the derivation is given in full.

---

*The Golem Review · Issue 002 · Research/Institute/Magazine*
