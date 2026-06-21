---
title: "Playbook: Browser Microbenchmarking for Text-Layout and Reflow Libraries"
aliases:
  - Browser Microbenchmarking Playbook
  - Pretext Perf Measurement Playbook
  - Batched Iteration Benchmarking
  - jsdom Cannot Measure Canvas
tags:
  - article
  - playbook
  - performance
  - benchmarking
  - browser
  - canvas
  - pretext
  - typography
  - measurement
status: active
type: article
created: 2026-06-20
repo: /home/manuel/code/wesen/2026-06-20--typo-reflow-foldout
---

# Playbook: Browser Microbenchmarking for Text-Layout and Reflow Libraries

This playbook describes how to measure the performance of a JavaScript text-layout or reflow library accurately in a browser. It is written for the engineer who has built or adopted a DOM-free measurement library such as `@chenglou/pretext`, needs to know whether dragging a callout or resizing a column will stay smooth, and discovers that the obvious measurement approach returns zero for every operation.

The reference implementation is the perf harness at `/home/manuel/code/wesen/2026-06-20--typo-reflow-foldout/src/perf/main.ts`, served by Vite at `/perf.html`, and the standalone report generator at `.../scripts/01-gen-perf-report.py`. Every technique below was developed to fix a concrete failure in that harness, and each section names the failure it addresses.

> [!summary]
> - A text-layout library that measures text via the canvas API cannot be benchmarked in jsdom or Node, because neither implements the canvas 2D context. Run measurements in a real browser via Playwright.
> - Timing a single sub-millisecond operation with `performance.now()` returns a number dominated by timer quantization and scheduling noise, and the median rounds to zero. Batch many iterations per timed sample and divide, so each sample's total time is large relative to the noise floor.
> - Measuring only the layout algorithm hides the dominant cost. In an interactive editor the renderer — DOM reconciliation or canvas repaint — is usually the bottleneck, and it scales with element count, not with algorithmic complexity. Measure the renderer separately and compare renderers on the same input.
> - A benchmark that uses a mock of the library proves nothing about the library. Import the real library and the project's own modules so the measurements reflect the production path.

## When to use this pattern

Apply this playbook when you need to answer any of these questions with numbers rather than assertion:

- Is the layout computation fast enough to run on every animation frame during drag?
- At what document size does the renderer become the bottleneck?
- Which renderer — DOM elements or canvas — should be the default for interaction?
- Does a claimed two-stage memoization (a slow one-time prepare stage and a fast repeatable layout stage) actually hold, and by what factor?

Do not apply this playbook for coarse, wall-clock comparisons between unrelated libraries, for load-testing a server, or for measuring anything that does not run in a browser. Those have different tooling and different failure modes.

## Why a real browser is required

A DOM-free text-layout library is called DOM-free because it does not put text in the DOM. It still has to read glyph widths from somewhere, and in a browser that somewhere is the canvas 2D context's `measureText`. The library segments the input text, then asks the canvas how wide each segment is, and uses those widths to decide where lines break.

The consequence for benchmarking is direct. `jsdom`, the DOM implementation used by Vitest and Jest in Node, does not implement the canvas 2D context. A call to `canvas.getContext('2d')` returns `null`. Node itself has no canvas at all. A measurement that runs in these environments is not measuring the library; it is measuring a mock you wrote, or it is failing in a way the test runner may not surface. The numbers have no relationship to production performance.

This constraint applies to any library that reads glyph metrics, image intrinsic dimensions, or any other value that only a full rendering engine can produce. The first check before writing a benchmark is to confirm the environment can actually execute the code under test. The check is simple.

```ts
const ctx = document.createElement('canvas').getContext('2d')
if (!ctx) throw new Error('no canvas 2D context — run in a real browser')
```

The reliable way to run the benchmark in a real browser without manual steps is Playwright. A dedicated harness page is served by the same dev server as the application, Playwright navigates to it, the harness runs the benchmarks, and Playwright reads the results from a property on `window` that the harness populates. The harness does the measurement; Playwright does the driving and the data extraction.

## The standalone harness shape

The harness is a single HTML entry plus one module. The HTML is minimal.

```html
<!-- perf.html -->
<div id="root"></div>
<script type="module" src="/src/perf/main.ts"></script>
```

The module imports the real library, the project's own modules under measurement, and a CSS file. It runs a sequence of benchmarks, accumulates results on `window.__PERF__`, and renders a live summary into `#root` so the page can be screenshotted.

```ts
import { prepareWithSegments, layoutNextLineRange } from '@chenglou/pretext'
import { reflow2 } from '../lib/reflow2'        // the project's own pipeline
import { sizeCallouts } from '../lib/calloutSizing'

const results = { env: {}, samples: [] }
// ... run benchmarks, push samples ...
;(window as any).__PERF__ = results
renderSummary()
```

Three properties of this shape matter. First, because the harness is served by the application's dev server (Vite in this case), the bare import `@chenglou/pretext` resolves to the same optimized dependency the application uses. There is no separate build or bundle step for the benchmark. Second, because the harness imports the project's own `lib/` modules, the pipeline timings reflect the real code path including all of its overhead, not a simplified copy. Third, exposing results on `window.__PERF__` as structured data means Playwright can extract them with a single `page.evaluate(() => window.__PERF__)` and the same data can be saved to JSON for offline report generation.

## The failure that motivates batched iteration

The first version of the harness timed each operation once per sample.

```ts
// BROKEN: single-shot timing
for (let i = 0; i < runs; i++) {
  const t0 = performance.now()
  fn()
  samples.push(performance.now() - t0)
}
const medianMs = median(samples)
```

For a layout operation that takes roughly twenty microseconds, this produced a median of `0.00` ms for nearly every measurement. The operation was real and was running; the number was wrong.

The cause is that `performance.now()` has a resolution on the order of a few microseconds, and a single call to a fast operation is shorter than the noise around that measurement. The timer quantization, the overhead of the timing calls themselves, and brief scheduler interruptions together produce a floor below which a single measurement is meaningless. The median of many meaningless single measurements is still meaningless.

The fix is to run the operation many times inside one timed sample, then divide the elapsed time by the iteration count. This lifts the signal above the noise floor.

```ts
function bench(name, params, runs, fn, iterations = 1, warmupRuns = 2) {
  // Warm up so JIT compilation and cache population are not counted.
  for (let i = 0; i < warmupRuns; i++) for (let j = 0; j < iterations; j++) fn()

  const perOpNs = []
  for (let i = 0; i < runs; i++) {
    const t0 = performance.now()
    for (let j = 0; j < iterations; j++) fn()
    // performance.now() returns ms; convert to ns, then divide by iterations.
    const elapsedNs = (performance.now() - t0) * 1e6
    perOpNs.push(elapsedNs / iterations)
  }
  return { name, params, runs, iterations,
           nsPerOp: median(perOpNs),
           minNsPerOp: Math.min(...perOpNs),
           maxNsPerOp: Math.max(...perOpNs) }
}
```

Choosing the iteration count is the part that takes judgment. The goal is for each timed sample to total at least a few milliseconds, so that the timer noise is a small fraction of the measurement. A twenty-microsecond operation needs on the order of two hundred fifty iterations per sample to reach five milliseconds. A five-millisecond operation needs only one. The harness picks the count per benchmark with that target in mind.

```ts
// Fast pipeline op: batch 200× so each sample is ~5 ms.
bench('pipeline.reflow2', { callouts: 8 }, 15, () => reflow2(...), 200)

// Already-slow render op: no batching needed.
bench('render.DOM', { lines: 2000 }, 12, () => rebuildDivs(...), 1)
```

Reporting in nanoseconds and choosing the display unit (ns, µs, ms) from the magnitude, rather than printing everything in milliseconds, is what makes the results readable once they are no longer rounding to zero.

## What to measure: the algorithm, the pipeline, and the renderer

A common mistake is to measure only the layout library and conclude the editor is fast. The layout library is one of three costs that together decide whether interaction is smooth, and it is usually not the largest.

**The library stage cost.** Measure the library's own functions across the dimensions that vary in production. For a text-layout library those dimensions are body-text length, column width, and the number of distinct fonts. This establishes the library's scaling behavior and confirms or refutes any two-stage memoization claim. For pretext, the slow `prepare` stage grows roughly linearly with text length, and the fast per-line layout stage is one to two orders of magnitude cheaper at every length.

**The project pipeline cost.** Measure the project's own code that wraps the library — sizing the callouts, computing the free regions, threading the cursor. This is the code that runs on every interaction frame, and its cost depends on the project's data, not on the library in isolation. Group these measurements by the parameters that vary in the project: callout count, placement mode, column count. The whole pipeline should be measured end-to-end as well, because that is what runs per frame.

**The renderer cost.** This is the cost the browser charges to actually put pixels on screen, and in an interactive editor it is frequently the dominant term. Measure it separately for each renderer, on identical computed input, and across the dimension that drives it — element count. For DOM rendering, the realistic measurement rebuilds the element tree, sets style and text content, and forces layout so the paint cost is included; omitting the forced layout measures only node creation and understates the true cost. For canvas rendering, the measurement clears the canvas and issues one fill call per element.

```ts
// DOM: rebuild N divs, set content + style, force layout.
domHost.replaceChildren()
for (const l of lines) {
  const d = document.createElement('div')
  d.textContent = l.text
  d.style.cssText = `position:absolute;left:${l.x}px;top:${l.y}px;width:${l.width}px`
  domHost.appendChild(d)
}
void domHost.offsetHeight   // force layout; otherwise paint cost is not counted

// Canvas: clear once, fill N times.
ctx.clearRect(0, 0, w, h)
for (const l of lines) ctx.fillText(l.text, l.x, l.y)
```

Comparing the renderer curves against the layout-pipeline cost on the same axis is what reveals the bottleneck. In the reference project, the layout pipeline measures in tens of microseconds regardless of document size, while DOM rendering crosses the sixteen-millisecond frame budget around seven hundred lines. The conclusion — that the renderer, not the layout library, decides interaction smoothness — is visible only because both were measured.

## Warmup, median, and the min–max spread

Three reporting choices protect against misleading numbers.

Run a warmup before recording samples. The first executions of a function compile it, populate caches, and trigger any lazy initialization in the library. Those costs are real but they are not representative of steady-state per-frame cost. A small number of warmup runs (two or three) is enough to move past them.

Report the median, not the mean. A single garbage-collection pause or background task can produce a sample ten times larger than the rest. The mean is pulled toward those outliers; the median is not. For per-frame cost, the median is the number that describes what a typical frame looks like.

Report the min–max spread alongside the median. A tight spread (the min and max within a small factor of the median) means the measurement is stable and the operation's cost is predictable. A wide spread means the operation is subject to interference — usually garbage collection or cache effects — and the median alone would hide that. When comparing two renderers, the spread explains whether the faster one is reliably faster or only faster on average.

## Capturing data and producing a standalone report

Measurements are useful only if they can be read, compared, and shared. The harness exposes its results as structured data on `window.__PERF__`, which Playwright reads and writes to a JSON file. A separate generator script reads that JSON and produces a self-contained HTML report with no external dependencies.

```ts
// In the harness, after all benchmarks:
;(window as any).__PERF__ = results
```

```python
# scripts/01-gen-perf-report.py
data = json.loads(json.loads(open('perf-raw.json').read()))  # Playwright stringifies once
# ... build headline cards, inline-SVG charts, per-benchmark tables ...
open('perf-report.html', 'w').write(html)
```

The generator produces inline SVG charts directly from the data, without a charting library. Two charts carry most of the explanatory weight: one showing the two-stage cost across text lengths (a grouped bar chart with the slow stage and the fast stage on different scales), and one showing the renderer cost across line counts (a line chart with a dashed horizontal line at the frame budget). The dashed budget line is the visual element that makes the renderer comparison legible at a glance — it shows exactly where each renderer crosses from smooth to janky.

The report is regenerated from the JSON whenever a new measurement run is taken, so the report and the raw data never drift apart, and the report can be opened in any browser because it carries its own styles and scripts inline.

## Working rules

- Confirm the measurement environment can execute the code under test before measuring it. A canvas-based library returns nothing useful in jsdom. The presence of the 2D context is the first thing to assert.
- Import the real library and the project's own modules into the harness. A benchmark against a mock measures the mock.
- Batch iterations so every timed sample is several milliseconds, then divide for per-operation cost. A single-shot timing of a sub-millisecond operation is noise.
- Warm up before recording, report the median, and report the min–max spread. The mean is misleading in the presence of garbage-collection pauses.
- Measure the renderer separately from the layout library, and compare renderers on identical input. In an interactive editor the renderer is usually the dominant cost and the library is not.
- Force layout when measuring DOM rendering. Without it, the measurement covers node creation but not paint, and understates the true per-frame cost.
- Report in nanoseconds and choose the display unit from the magnitude. Reporting sub-millisecond operations in milliseconds is what produced the original all-zero output.
- Expose structured results on `window` for Playwright to extract, and generate the human-readable report from the captured JSON so the two cannot drift.

## Common failure modes

**All measurements read zero.** The operation is faster than the timer's effective resolution measured once. Fix: batch iterations. This is the failure that prompted this playbook.

**Measurements pass in jsdom but the production app is slow.** The library is mocked in the test environment, so the test is not exercising the real code path. Fix: run the harness in a real browser via Playwright, importing the real library.

**The layout library measures as fast, but dragging is janky.** The renderer was not measured, or was measured without forcing layout. Fix: measure the renderer separately, force layout for the DOM path, and compare against the frame budget on the same axis as the library cost.

**The median is stable but the max is ten times larger.** Garbage collection or a background task is interfering with some samples. Fix: report the spread, increase the warmup, and treat the median as the per-frame cost rather than the max.

**The report and the raw data disagree.** The report was hand-edited or copied from a different run. Fix: generate the report from the captured JSON every time, and never edit the report by hand.

## Pseudocode: the minimal harness

The complete measurement loop, stripped to its essentials:

```pseudo
function bench(name, params, runs, fn, iterations, warmupRuns):
    for w in 1..warmupRuns:
        for j in 1..iterations: fn()
    perOpNs = []
    for i in 1..runs:
        t0 = performance.now()
        for j in 1..iterations: fn()
        elapsedNs = (performance.now() - t0) * 1_000_000
        perOpNs.push(elapsedNs / iterations)
    return {
        name, params, runs, iterations,
        nsPerOp:   median(perOpNs),
        minNsPerOp: min(perOpNs),
        maxNsPerOp: max(perOpNs),
    }
```

The full harness repeats this loop across the dimensions that matter (text length, callout count, placement, column count, line count), groups the results by benchmark name, exposes them on `window.__PERF__`, and renders a live summary. The generator script turns the captured JSON into a standalone report with charts. Each of those layers is small; the batched-iteration `bench` function is the part that determines whether the numbers are real.

## Related notes

- [[PROJECT REPORT - typo-reflow-foldout - Pretext-Driven Text Reflow Architecture]] — the project whose perf work produced this playbook, including the measured findings and the standalone report.
- The harness source: `/home/manuel/code/wesen/2026-06-20--typo-reflow-foldout/src/perf/main.ts`
- The report generator: `/home/manuel/code/wesen/2026-06-20--typo-reflow-foldout/ttmp/2026/06/20/TYPO-001--typographic-reflow-playground-vite-react-pretext/scripts/01-gen-perf-report.py`
- The generated report: `/home/manuel/code/wesen/2026-06-20--typo-reflow-foldout/perf-report.html`
