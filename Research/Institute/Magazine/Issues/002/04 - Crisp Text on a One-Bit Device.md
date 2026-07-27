# Crisp Text on a One-Bit Device

## Hinting, Heat, and the Limits of Algorithms

A thermal printer asked to render small text fails in a way that resists every obvious fix. The glyphs are missing pieces. Strokes thin to nothing. Counters — the enclosed holes in letters like e, a, g — close up and fill in. An eight-pixel-tall lowercase e may print as an undifferentiated blob. Heat does not help. A different dithering algorithm does not help. A sharper threshold does not help. The failure has a specific cause, and the cause is upstream of every lever we have examined so far.

This article traces that cause to its origin and follows the investigation that resolved it. The investigation reversed its own conclusion twice, and each reversal was forced by a printed page rather than by an argument about rasterizers. The result is a principle that reframes the problem of small text on a one-bit device: legibility is governed more by the font's hinting and its size than by any conversion algorithm layered on top. Techniques matter at the margin. The font and the size set the ceiling.

---

## The Failure That Heat Cannot Fix

Begin with the observation that did not fit the model.

The model so far has three levers: a tone curve applied before dithering, the dithering algorithm itself, and the printer's heat. Text, the model says, should be thresholded, and its quality should respond to the density register. A density ladder printed this way — the same paragraph at sizes from sixteen pixels down to eight, across densities 16, 24, 32, and 39 — confirmed the model for the larger sizes. At density 24 the text was crisp and dark down to about eleven pixels. At density 32 the punch was best. At density 39 the large text was bold but the smallest sizes began to bleed.

At eight and nine pixels, something different happened. Parts of letters were simply missing, and no density fixed it. Raising the density made the surviving strokes darker, but it did not bring the missing strokes back. The failure was not a darkness problem. It was a presence problem. The strokes were gone.

The cause is in the font rasterizer, not the printer. A vector font rendered at a small size produces strokes thinner than one pixel. The rasterizer represents those strokes with anti-aliasing — light-gray pixels rather than solid black — because a sub-pixel-wide stroke cannot fill a pixel completely. The downstream threshold, applied after the screenshot is taken, compares each pixel's luminance to a cutoff. A light-gray stroke at luminance 180 sits above a cutoff of 128 and is discarded. The stroke was present in the rendered page. It is absent in the bitmap. The printer never had a chance to render it, because the bitmap it received no longer contained it.

This is a continuous-tone problem disguised as a text problem. The anti-aliasing produced intermediate gray values, and the binary conversion threw them away. No amount of heat recovers information that was lost before the bitmap reached the printer.

There are two host-side responses, and the rest of this article is the story of trying both.

---

## First Attempt: A Bitmap Web Font

The direct response to "anti-aliasing produces gray strokes that the threshold discards" is to remove the anti-aliasing at its source. A bitmap font — a font whose glyphs are authored at an exact pixel size, every stroke a solid one-bit pixel, every counter open by design — has nothing for the threshold to discard. There is no gray. There is only ink and paper.

A comparison card made the case unambiguously. The same text rendered three ways — anti-aliased vector under threshold, vector with anti-aliasing disabled, and classic X11 PCF bitmap fonts at their native sizes — produced three clearly different results. The anti-aliased section broke up badly by eight pixels. Disabling anti-aliasing helped, but the glyphs were blocky and still crumbled at the smallest size. The bitmap section was crisp all the way down: a 6×9 bitmap font was more legible than the eleven-pixel anti-aliased line above it, counters stayed open at 5×7, and even 4×6 was readable.

The conclusion seemed clear. Ship a bitmap font.

The production renderer draws through headless Chrome, not a direct rasterizer, and the obvious translation of "use a bitmap font" into that pipeline is to serve the browser a web font that carries the pixel design as embedded monochrome bitmap strikes — the OpenType `EBDT` and `EBLC` tables — applied to small-text elements at the strike's native pixel size. The render browser captures at device-pixel-ratio 1, so a `font-size: 9px` element occupies exactly nine device pixels, which is where a nine-pixel strike should land verbatim.

It failed. A classic X11 PCF font was converted to an OpenType font carrying its bitmap strike, embedded via `@font-face`, and rendered at 384 pixels. Chrome did not use the strike. Blink, Chrome's rendering engine, rasterizes text through FreeType, and FreeType on Linux draws the font's vector outlines and ignores embedded monochrome bitmaps for normal text. The outlines that the conversion tool auto-traced from the bitmap were crude. The custom font rendered *worse* than the stock font it was meant to improve.

The first conclusion was wrong, and a printed page showed it. The browser will not use a web font's embedded bitmap strike. The bitmap-font result, achieved with a direct rasterizer, does not survive the trip through Chrome.

---

## Second Attempt: Supersampling

With the bitmap-font path closed, the question became how to make a vector font's anti-aliasing survive the threshold. The strokes vanish because they are rendered as light-gray pixels that the threshold discards. If the strokes were wider — if the same sub-pixel stroke were spread across more pixels — the threshold would keep them.

Supersampling does this without touching the font. The page is rendered at three times the device resolution with anti-aliasing on. A stroke one target-pixel wide is captured across three source pixels, each at a different gray level. The screenshot is then box-averaged back down to the target resolution and thresholded. A stroke that would have vanished at 1× survives as a run of gray that the threshold keeps.

The implementation has two sharp edges. The first is that the scale must actually take. The browser automation library defaults the device scale factor to 1, and a launch flag setting the scale is silently overridden unless the scale is set through the correct API call. Verify by checking that the screenshot comes out three times as wide.

The second is that the downscale must be fast. A naive pixel-by-pixel box average — calling the image library's `At(x, y)` for every pixel of a full page — took seventeen seconds. The fix is to decode the screenshot once into a packed RGBA buffer and index the pixel bytes directly in the inner loop, using fixed-point luminance weights. The same 3× render then completes in about two and a half seconds.

Supersampling works. The small serif italic that was broken at 1× becomes complete, and it still looks like a serif. It shipped as the default. The conclusion, again, seemed clear: supersample.

---

## Third Attempt: Turn Off the Anti-Aliasing

Then the question was posed properly. Rather than argue about techniques, a harness rendered the same small text across six fonts, sizes eight through sixteen, five techniques — 1× with anti-aliasing off, 2×, 3×, and 4× supersampling, and a darker-threshold variant — and a grid of printer densities and speeds. Every sheet was downsampled to the 384-pixel target exactly as the production pipeline would, self-labeled with its settings, printed, and read on paper.

The matrix overturned the supersampling decision. Four findings came out of it, and the first two reversed earlier conclusions.

The font's hinting quality dominates. A well-hinted font — DejaVu Serif, DejaVu Sans — stays crisp to eight or nine pixels regardless of technique. A lightly-hinted font — EB Garamond, DM Sans, Noto Sans — is rough at small sizes in every technique. No amount of supersampling rescues a font whose hinting does not snap its stems to pixels.

For a well-hinted font, 1× with anti-aliasing off is as crisp as supersampling — usually crisper — and about three times faster. Bytecode hinting is designed to snap stems to exact pixel boundaries. Supersampling bypasses hinting entirely by rendering large and shrinking, which produces a softer result than hinting would have. The technique that seemed obviously inferior turned out to be sharper, and faster, for the fonts that matter.

Effective size is set by x-height, not nominal size. EB Garamond has a small x-height and renders two to three pixels smaller than DejaVu at the same `font-size`. A Garamond set at 16 or 17 pixels reads like a DejaVu set at 11 or 12. A delicate face must simply be set larger.

Weight is the biggest remaining lever. Heavier strokes survive the threshold far better than light ones, and bold italic is legible where normal italic is not. For the smallest sizes and for italic text, weight matters more than any rasterization technique.

The default render technique is now 1× with anti-aliasing off. Supersampling remains available as an opt-in, for the case of a delicate display font the designer refuses to change. The byte-compatible packed-bitmap contract is unchanged throughout.

---

## The Mechanism: Moving the One-Bit Decision

Why does disabling anti-aliasing work, when supersampling seemed to? The answer is a shift in where the one-bit decision is made.

With anti-aliasing on, the decision is made by a dumb luminance threshold applied after the fact. The font rasterizer produces gray pixels — some dark, some light, some barely present — and the threshold, seeing only luminance, discards the light ones. The decision is blind to the structure of the glyph. A light-gray pixel at the edge of a stem and a light-gray pixel in the middle of a counter are treated identically, and both are discarded, even though one is part of the stroke and the other is not.

With anti-aliasing off, the decision is made by FreeType's hint-aware rasterizer at draw time. FreeType, asked to render a glyph without anti-aliasing, applies the font's bytecode hinting — instructions in the font itself that snap stems to pixel boundaries, align counters to the pixel grid, and adjust stem widths to the nearest whole pixel — and then makes the black-or-white decision per pixel with that hinting applied. A stem that the font's hinting places at a pixel boundary becomes a solid black column. A counter that the hinting keeps open stays open. The decision is structurally aware, because it is made by the same code that understands the glyph's shape.

This is the conceptual shift, and it is more important than any specific technique. On a one-bit device, the goal is not to recover gray information that was lost. The goal is to never produce gray information in the first place — to let the font's hinting make the one-bit decision at the moment of rendering, rather than asking a downstream threshold to reconstruct it from gray pixels that no longer carry the structural information.

Anti-aliasing is a technique for displays that can show gray. A thermal printer cannot. Feeding it gray pixels and then thresholding them is asking the printer to reconstruct a structure that was deliberately blurred. Disabling anti-aliasing and letting hinting do the work is the natural fit between the device and the rendering.

The mechanism by which anti-aliasing is disabled is itself a subtlety worth recording. On Linux, Chrome rasterizes text through FreeType, and whether FreeType anti-aliases is a fontconfig decision, not a CSS one. The `-webkit-font-smoothing` CSS property is a no-op in Chrome on Linux. Supplying the render browser a fontconfig file with `antialias=false` — set through the `FONTCONFIG_FILE` environment variable on the browser process — switches FreeType to its monochrome rasterizer. The effect is measurable: the render screenshot goes from a few percent gray pixels to zero. There is no longer any light-gray fringe for the downstream threshold to discard, so nothing drops.

---

## The Recipe, and What Actually Governs It

The production recipe for small text on a thermal printer, confirmed on paper, is now a set of typographic choices rather than pipeline code:

Pick a well-hinted font. DejaVu Serif for a serif look, DejaVu Sans for maximum crispness. A delicate face like EB Garamond must be set about three points larger to reach the same effective size.

Disable anti-aliasing in the render browser, via fontconfig. This is the single most effective change, and it costs nothing.

Use bold or medium weight for the smallest sizes and for italic text. Normal italic loses strokes at one bit; bold italic survives.

Keep text from getting too small in the first place. No technique rescues a six-pixel glyph set in a lightly-hinted font.

Print text at a density around 38, which read best across the heat sweep. Density matters more than speed for text; the two speeds tested (37 and 80) were not visibly distinguishable.

The recipe is not a triumph of algorithm. It is an admission that the font and the size set the ceiling, and that the techniques available to the rasterizer can only approach that ceiling, not raise it. The matrix showed this directly: a well-hinted font at 1× with anti-aliasing off was sharper than the same font at 4× supersampling. The technique that did the least work on the pixels did the most for legibility, because the font's hinting was already doing the work the techniques were trying to replicate.

---

## The Tension, and Its Resolution

We now have two locked findings in tension, and the tension is the final engineering problem.

Photographs want a cool, light setting: Atkinson dithering, gamma 0.8, density around 20. If the dots are burned hot, the photograph's midtones merge into mud.

Text wants a hot setting: density around 38, with the anti-aliasing off and a well-hinted font. If the dots are burned cool, the text is faint and the strokes break up.

A single global density cannot serve both. A page that contains a photograph and text, printed at one density, will print one of them badly. The complaint that opened this entire investigation — "hard to read" — was the signature of exactly this mismatch.

The resolution costs nothing in firmware, because the print path already sends a tall page as multiple segment commands. The ESP32's receive buffer is limited, and a long bitmap is split into segments that are sent as sequential print commands, with only the final segment carrying the paper feed. Density and speed are printer state: setting them between segment commands makes each segment print at its own heat.

A page can therefore print its text segments hot and its photograph segment cool in a single job. The text bands set density 38 before they print; the photograph band sets density 20 before it prints; the text bands after the photograph set density 38 again. The printer receives several commands, each at its own heat, and the paper records them as one continuous page.

```
Compose page
  → Segment A: header + body, bitmap font         → set density 38, print
  → Segment B: photograph, Atkinson, gamma 0.8    → set density 20, print
  → Segment C: caption + body, bitmap font         → set density 38, print
  → One continuous page
```

The implementation maps per-block render options, carried in the layout, onto per-block bounding boxes measured in the browser. Each block that sets a `printerDensity` override produces a heat region. The regions are turned into a top-to-bottom cover of every row — regions at their density, gaps at the page default — and the bitmap is sliced into those bands. Each band is sent as a separate print command after its density has been set. The firmware needs no change. It receives the same packed one-bit bytes it always has, at whatever density the host chose.

A mixed test page printed this way — text bands at 38, a photograph band at 20, text again at 38 — produces crisp dark text and a light, detailed photograph, in the same job, with no firmware modification. This is the complete answer to the original complaint.

---

## What the Four Articles Say, Together

The four articles of this issue trace a single thread from the physics of a heated dot to the typography of a small glyph, and the thread is the binary decision.

The first article established the device. A thermal printer is a line of heaters and a motor, fed by a serial link too slow at default settings to keep up with the mechanism. The energy delivered to a dot is quadratic in voltage, which makes the device sensitive to power integrity and to its own thermal history. Text loads the system lightly and prints well; photographs load it heavily and expose every weakness.

The second article established the algorithm. A one-bit device cannot show gray, so continuous tone must be simulated by arranging black and white dots whose local average approximates the original. The families differ in how they choose the dots, and the right choice on thermal paper is not the most tonally accurate algorithm but the one that compensates for the medium's dot gain. Atkinson dithering, which discards a quarter of the quantization error, prints lighter than Floyd–Steinberg, and on a medium where each dot spreads, lighter is more accurate.

The third article descended into the rasterizer that produces the pixels the ditherer consumes. The failure modes of a scanline rasterizer are local and subtle — a scale divisor from the wrong metric, a winding corrupted by a transform, a span endpoint whose coverage is truncated, a subpixel position forced to an arbitrary offset — and each produces a glyph that looks almost right. Systematic comparison against a reference renderer is the only reliable way to find them.

This fourth article closed the loop. Small text fails on a thermal printer not because of the printer, and not because of the dithering, but because anti-aliasing produces gray strokes that a downstream threshold discards. The fix is to move the one-bit decision from a dumb luminance threshold applied after the fact to FreeType's hint-aware rasterizer applied at draw time — to disable anti-aliasing and let the font's hinting make the decision. The font and the size set the ceiling. The techniques approach it.

The unifying principle is that a one-bit device is not a low-resolution gray display. It is a binary decision-maker, and the quality of its output depends on which decisions are made, where they are made, and how much structural information survives to the moment of decision. A photograph's gray survives best when dithering distributes the error in a way that compensates for the medium. A glyph's strokes survive best when the font's hinting snaps them to pixels before any threshold is applied. A mixed page survives best when the printer's heat is set per segment, so that the text burns hot and the photograph burns cool.

The thermal printer is easy to demo and hard to drive well. The demo path is one line: send text over a serial port. The robust path is a control problem — feed the printer at a rate it can accept, deliver enough energy without sagging or overheating, keep the paper moving predictably, and use the command language in a way that respects buffer and scheduler boundaries. Once the printer is understood as a coupled physical system whose output is the record of binary decisions made under constraints, the artifacts that confound a beginner — the banded photograph, the faded dense region, the missing strokes in small text — stop being mysterious. They become the legible signature of a specific constraint, and addressing them is a matter of identifying which constraint is speaking and moving the decision that governs it.
