---
title: "Rendering Pipeline Fundamentals: Retained Mode, Dirty Rects, and Compositing"
aliases:
  - rendering pipeline
  - retained mode rendering
  - dirty rectangle
  - partial refresh
  - display compositing
tags: [knowledge-base, fundamental, rendering, graphics, display, e-ink, lcd]
status: active
type: knowledge-base
created: 2026-05-11
---

# Rendering Pipeline Fundamentals: Retained Mode, Dirty Rects, and Compositing

> [!summary]
The architectural pattern behind every display system we build: maintain a tree of visual elements, compute layout, track which regions changed (dirty rectangles), merge those regions to minimize display updates, and render only what changed. This entry covers the theory that makes our e-ink, LCD, and thermal rendering work.

## The core idea

A **rendering pipeline** transforms application state (data, time, user input) into pixels on a display. For constrained displays (e-ink, small LCDs, thermal printers), the pipeline must minimize the number of pixels written because each write is expensive — e-ink partial refresh takes 50–200ms per region, serial LCDs are bandwidth-limited, and thermal printheads heat one row at a time.

The pipeline has four stages that appear in every one of our display projects:

1. **Layout**: Compute the position and size of every visual element.
2. **Update**: Apply data changes, mark affected elements as dirty.
3. **Collect + Merge**: Gather dirty rectangles and merge overlapping/adjacent ones.
4. **Render + Refresh**: Redraw only the merged dirty regions and send them to the display.

## Why it matters to our work

Two of our KB entries depend on this theory:

- **On-Ramp: E-Ink Display Driving** — E-ink partial refresh is the canonical use case for dirty-rect optimization. Full refresh is slow (300ms–1s) and causes visible flashing. Partial refresh is fast (50–200ms) but accumulates ghosting. The pipeline must choose between them.
- **Tribal: ESP-IDF Firmware Patterns** — Our firmware rendering follows this four-stage pattern. Gnosis uses it explicitly; SToMS3R uses it implicitly (the browser does layout, the ESP32 does the "render" stage).

Every display project we build reinvents this pipeline unless we document it as a reusable pattern.

## The key result

**Retained-mode rendering with dirty-rectangle tracking is the optimal architecture for constrained displays.** The key property: the system maintains a persistent model of the visual tree (the "retained" mode), so it can compute the minimal set of pixels that changed between frames.

This is distinct from **immediate-mode rendering** (used by many game UIs and terminal emulators), where the entire frame is redrawn from scratch each cycle. Immediate mode is simpler to implement but sends every pixel every frame — acceptable for 60Hz LCDs, unacceptable for e-ink and thermal printers.

## The intuition behind the key result

Think of a whiteboard where you're drawing a dashboard with a clock, a gauge, and a label. Every second, the clock changes and the gauge needle moves.

**Immediate mode**: Erase the entire whiteboard and redraw everything. Simple, but you erase and redraw 95% unchanged content.

**Retained mode with dirty rects**: Only erase and redraw the clock digits and the gauge needle. Everything else stays. Faster, but you need to know exactly which pixels the clock and gauge occupy.

The dirty-rect system is the "knowing exactly which pixels changed" part. In a tree-based layout:
- Each node has a bounding rectangle (computed by the layout pass).
- When a node's value changes, its bounding rectangle is marked dirty.
- Adjacent dirty rectangles are merged (two overlapping 10×10 rects become one 15×15 rect — fewer display updates than two separate ones).
- Only the merged dirty regions are redrawn and refreshed.

The Gnosis engine on PaperS3 uses exactly this approach. The Loupedeck driver uses it for its 60×360 LCD. The reMarkable pipeline uses it for document rendering.

## What goes wrong when you don't know this

1. **Gnosis predecessor (firmware 0075–0077)**: Used ad-hoc dirty tracking — specific methods knew their own screen regions. Adding a button meant changing coordinates in four places. Moving a panel meant cascading arithmetic. The layout engine replaced this with tree-based positions and automatic dirty tracking.

2. **Full-screen refresh on e-ink when only a clock changed**: Without dirty-rect tracking, the only safe option is to refresh the entire screen. This takes 800ms+ and causes a visible flash. With dirty-rect tracking, only the clock region is refreshed in 80ms with no flash.

3. **Thermal printer banding from mid-raster pauses**: The "dirty region" concept applies at the printer level too. If you split a bitmap into multiple raster commands (banding), the seam between bands is a visible artifact — the paper feed between bands is not perfectly aligned with the dot grid. The fix: send the entire bitmap as one continuous raster command (the "full-body buffer" pattern).

## Where we use it

- [[On-Ramp/e-ink-display-driving]]
- [[Tribal/esp-idf-firmware-patterns]]

### Related PARC project reports

- [[PROJ - Gnosis Layout Engine - PaperS3 UI Operating System]] — four-stage pipeline on e-ink with dirty-rect optimization
- [[PROJ - Loupedeck Live Hello World - Serial Go Driver]] — render scheduler with region coalescing on 60×360 LCD

## Where to go deeper

1. **Skala, A. (2019)**. *Rendering and Compositing*. — Practical coverage of retained-mode rendering, dirty rectangles, and compositing for UI frameworks.
2. **Gnome/GTK documentation** — GTK's rendering model is retained-mode with dirty-region tracking. The architecture documents explain the four-stage pipeline in detail.
3. **Gnosis Layout Engine project report** in this PARC library — Our implementation of the four-stage pipeline on an ESP32-S3 e-ink display.
