---
title: "Measuring Before Optimizing: An X11 Window Manager Resize Path"
aliases:
  - GGWM-012 Performance Analysis
  - X11 Resize Performance Measurement
  - Measuring Before Optimizing
tags:
  - article
  - performance
  - x11
  - window-manager
  - go
  - profiling
  - measurement
status: active
type: article
created: 2026-07-22
repo: /home/manuel/workspaces/2026-07-21/go-go-wm-goja/go-go-wm
---

# Measuring Before Optimizing: An X11 Window Manager Resize Path

This note records what happened when a carefully reasoned performance analysis met a measurement. Three external review documents, roughly 8,700 lines between them, agreed on why dragging a divider in the `go-go-wm` window manager felt slow. A verification pass against the live code produced a fourth diagnosis that contradicted all three and looked better than any of them. Ninety seconds of running the actual system refuted the fourth diagnosis as well.

The engineering content is specific to X11 and to one Go window manager. The transferable content is a failure mode: reading code produces hypotheses that are mechanically correct and causally wrong, and no amount of additional reading distinguishes the two.

> [!summary]
> - Code reading identified a real mechanism — 1,024 synchronous X round trips per drag — that measurement showed was **not** the bottleneck. Removing every one of those round trips made the system 15% *slower*.
> - Reconciliation (layout, tree indexing, geometry diffing, request construction) is **1.8%** of a relayout. Painting is the other 98.2%. All the algorithmic optimization work targeted the 1.8%.
> - The largest single win, a 7.2× speedup, was not in any plan. It surfaced within an hour of the repository having its first benchmark.
> - A nested `Xephyr` server turns "needs a spare console and a human" into a tool call that runs in ninety seconds.

## Why this note exists

The `go-go-wm` project had accumulated three long-form architecture reviews recommending substantial work: a preview/commit split for interactive resize, a latest-wins pointer mailbox, separation of window chrome from window content, capacity-based buffer allocation, and a retained widget tree. Each recommendation was argued from the source code. None of them had a benchmark behind it, because the repository contained no benchmarks at all and exactly two debug-level timing probes.

That is a common state for a project that has already done one round of successful optimization. Earlier work had produced measurable CPU reductions through row-major pixel fills, cached image objects, and MIT-SHM shared pixmaps. Those wins were real. What they left behind was a system where everyone's remaining model of the cost structure came from reading the code, and where the reading was plausible enough that nobody questioned it.

## The system under analysis

`go-go-wm` is a reparenting X11 window manager written in Go, about 21,600 lines. The relevant structure:

```mermaid
graph TD
    subgraph "single goroutine owns all X-facing state"
        LOOP[WM run loop]
        RECON[relayoutPaint: the sole reconciler]
        PAINT[paintFrame: compose + upload]
    end
    subgraph "pure, display-free"
        CORE[wmcore: tree, ops, layout]
    end
    subgraph "rendering"
        DRAW[draw: fill, text, widgets]
        SHM[xshm: MIT-SHM shared pixmap]
    end
    X[X server]

    LOOP --> RECON
    RECON --> CORE
    RECON --> PAINT
    PAINT --> DRAW
    PAINT --> SHM
    SHM --> X
    RECON --> X

    style PAINT fill:#c33,color:#fff
    style X fill:#333,color:#fff
```

Two structural properties matter for everything that follows.

The window manager is **single-threaded by construction**. X event callbacks and posted closures are mutually exclusive, because `xgbutil`'s event loop sends on an unbuffered channel before dequeuing each event. There is not one mutex in the entire X11 package. Any work on this loop is work the user feels as input latency, and there is no render thread to hide it in.

The **paint path is immediate-mode**. Every repaint rebuilds a full pane-sized `image.RGBA` from the model, converts it from RGBA to the server's BGRA byte order, and uploads it. There is no retained surface and no damage tracking. A window's title strip is drawn *into* that full-pane buffer rather than into its own child window, so changing which window has focus repaints two entire panes to update a 22-pixel-high strip.

## The hypothesis that reading produced

Tracing one accepted pointer sample during a divider drag through the source gives this chain:

```
MotionNotify
  ├─ 16 ms time gate                                 admission control
  ├─ wmcore.Layout(...)          full tree + fresh map     ← layout #1
  ├─ wmcore.Apply(OpSetRatio)    durable tree mutation
  └─ relayoutResized()
       ├─ wmcore.Layout(...)     full tree + fresh map     ← layout #2
       ├─ syncDividers()         repaints EVERY divider, uncached blit path
       ├─ per item: Root.Find()  O(n) DFS inside an O(n) loop
       ├─ per changed frame: MoveResize + client ConfigureWindow
       ├─ per changed frame: paintFrame()
       │    ├─ full-pane Fill
       │    ├─ TitleStrip.Render()
       │    └─ if size changed:  surf.Destroy(); xshm.New(...)
       └─ Map()/Unmap() for EVERY frame in the process
```

The item that stands out is `xshm.New`. It issues `shm.AttachChecked(...).Check()` and `shm.CreatePixmapChecked(...).Check()`. In XCB, a *checked* request is one whose errors are collected synchronously — which means it is a round trip, a serial dependency on the server that drains request pipelining.

`paintFrame` destroys and recreates the shared pixmap whenever the pane's dimensions change, and a divider drag changes dimensions on every tick. Two panes change per tick. That is four round trips per tick, and over a full drag it multiplies out to over a thousand.

This explains something the earlier optimization work had left unexplained. Prior tickets had made the pixel work measurably faster and the drag still felt slow. Latency that comes from serial round trips does not improve when you make CPU work faster. The hypothesis accounted for the symptom, identified a real mechanism in the source, and explained why the previous fix had underdelivered.

All three review documents had missed it, and the reason they missed it is instructive: the natural audit is `grep '\.Reply()'`, which finds reply-waiting requests. `.Check()` does not match that pattern.

The hypothesis was wrong.

## The measurement

The obstacle was that a window manager cannot be benchmarked in a unit test. It needs an X server, real client windows, and pointer input. The first two attempts used a spare virtual console — which required a human at a physical console, failed twice for reasons unrelated to the experiment, and on one occasion tore down the display server because the harness script was `xinit`'s client and its death ended the session.

The approach that worked is a **nested server**:

```bash
DISPLAY=:0 Xephyr :7 -screen 1280x800 -ac -noreset &
go-go-wm wm --display :7 --log-level debug --log-format json --log-file run.jsonl &
# create two panes over the IPC socket, then drive the drag
DISPLAY=:7 xdotool mousedown 1
for x in $(seq 320 6 960); do DISPLAY=:7 xdotool mousemove $x 400; sleep 0.004; done
DISPLAY=:7 xdotool mouseup 1
echo '{"q":"perf"}' | socat - UNIX-CONNECT:$SOCK
```

`Xephyr` runs a real X server as a window on an existing display. It has real X semantics, it is disposable, it cannot take down a live session, and it needs no console access. The entire three-condition experiment runs in about ninety seconds and is driven from a script. Three failed attempts at console-based testing were solving a problem that did not need solving.

Instrumentation was added first: counters for reconciliation work, upload-path resource churn, motion admission, and wall clock, exposed as bounded aggregates over the existing IPC socket. Plus one deliberate measurement affordance — an environment variable that suppresses decoration paint during a drag while still committing geometry, which isolates paint cost from everything else without restructuring any code.

## What the numbers said

Three conditions, one scripted drag each, 644 motion events per run.

**The mechanism was confirmed exactly.** `shm_creates = shm_destroys = frames_resized = 512`. One shared-pixmap teardown and rebuild per resized pane per tick, 1,024 checked round trips for a single drag. The source reading was correct in every particular.

**The conclusion drawn from it was not:**

| Condition | shm creates | ximg creates | ms/paint | p50 | p95 |
|---|---:|---:|---:|---:|---:|
| default (MIT-SHM) | 512 | 0 | **4.98** | 4.82 | 8.29 |
| `GO_GO_WM_NO_SHM=1` | 0 | 510 | **5.85** | 5.47 | 9.44 |

Disabling MIT-SHM removes every one of the 1,024 round trips and makes each paint **15% slower**. If the round trips dominated, the opposite would happen. Shared memory earns its cost several times over even while paying two synchronous round trips per frame.

The second measurement is more decisive. Suppressing decoration paint during the drag, while still committing all geometry:

```
relayout_ms_total    2595 ms  ->  13.8 ms       188x
ms per relayout      7.416    ->  0.040
```

Everything that is not painting — computing the layout, building the node index, diffing applied geometry, constructing and batching X requests, synchronizing dividers — is **0.13 ms of a 7.4 ms relayout**. Under two percent.

Combining that with the microbenchmarks gives a complete accounting of one paint:

| Component | Time | Share |
|---|---:|---:|
| `draw.Fill` (full pane) | ~0.06 ms | ~1% |
| `TitleStrip.Render` | ~0.04 ms | ~1% |
| RGBA→BGRA conversion + upload + X | **~4.9 ms** | **~98%** |
| **Total `paintFrame`** | **4.98 ms** | |

`draw.Fill` runs at 32 GB/s. It is memory-bandwidth bound and there is nothing left to win there. The 98% is pixel volume moving through conversion and into the server.

## The consequence for the plan

The plan had ordered capacity-based buffer allocation (which eliminates per-tick surface recreation, and therefore the round trips) ahead of separating window chrome from window content. The measurement inverts that.

If the cost is pixel volume rather than round trips, then the change that matters is the one that reduces pixels. Separating chrome from content means a window's decoration lives in a title child window sized 1272×22 instead of being composited into a 1272×664 pane buffer. For the decoration repaints that dominate focus changes and drags, that is roughly a 30× reduction in pixels touched. Capacity buffers remain worth doing for allocation pressure, but they are no longer the headline.

```mermaid
flowchart LR
    A["hypothesis from reading:<br/>round trips dominate"] --> B["fix: capacity buffers<br/>(Phase 2 first)"]
    C["hypothesis from measuring:<br/>pixel volume dominates"] --> D["fix: chrome/content split<br/>(Phase 4 first)"]
    style A fill:#c33,color:#fff
    style B fill:#c33,color:#fff
    style C fill:#282,color:#fff
    style D fill:#282,color:#fff
```

## The win that was not on any plan

The repository's first benchmarks were written as instrumentation groundwork, with no expectation that they would change direction. They immediately showed that `draw.Text` was **72%** of a title-strip render — 52.8 µs of 73.7 µs.

A window's title does not change while its pane is being resized. Only the width does. The glyph rasterization was being repeated on every repaint for a string that was identical every time.

The fix caches each rendered run as an **alpha mask** rather than as coloured pixels:

```go
type textKey struct { s string; bold bool; size float64 }

type textMask struct {
    mask    *image.Alpha // coverage only; colour applied at blit time
    originY int          // baseline offset within the mask
    advance int          // pen advance, must equal TextWidth
}
```

Storing coverage rather than colour is the load-bearing decision. Caching rendered RGBA would key on colour, so a focus change or theme swap would miss and re-rasterize — and focus changes recolour the same title constantly. With a mask, the expensive geometry work happens once per `(string, bold, size)` and colour is applied at composite time.

| Benchmark | Before | After | Change |
|---|---:|---:|---|
| `draw.Text` (24-char title) | 53.9 µs | 7.46 µs | **7.2×** |
| `TitleStrip.Render` w=1272 | 73.7 µs | 38.8 µs | 1.9× |

This is the largest single improvement produced by the entire effort, and it appeared within an hour of the project having any benchmark at all. It was not in any of the three review documents, and it was not in the plan derived from them.

### The cost, and how it was bounded

The cache is not bit-exact. `font.Drawer` blends each glyph onto the destination in turn; the cache blends glyphs into one mask and applies it once:

```
direct:  dst = over(over(dst, g₁), g₂)
cached:  dst = over(dst, over(g₁, g₂))
```

These are identical for non-overlapping glyphs and differ by one least-significant bit where antialiased glyphs overlap, because the alpha arithmetic rounds at a different point. Measured across the golden-image corpus: **14 differing pixels out of 179,200 (0.0078%), maximum channel delta 1/255**, on two of nine images.

A first check against five hand-picked strings had reported zero difference. That check was worthless — it simply had not hit a kerned pair that overlaps. When a change *can* alter output, measure the corpus, not a sample.

Two golden images were regenerated. What made that acceptable rather than corrosive was making the tolerance explicit and enforced: a test retains the original implementation as a reference and fails if any channel drifts by more than 1. The trade is no longer "a rendering change was accepted once" but "a bounded rendering change was accepted, and the bound is a test."

## Common failure modes

**Reasoning from mechanism to magnitude.** The round-trip hypothesis identified a real mechanism, quantified it correctly, and explained the observed symptom. Every step was sound except the unstated one: that a real cost is a dominant cost. Code reading can establish that something happens. It cannot establish how much it matters relative to everything else that also happens.

**Optimizing what is legible.** Layout algorithms, tree traversals, and redundant requests are visible in source and satisfying to fix. Pixel volume moving through a colour-conversion loop is not visible in the same way. The work that got done first was the work that was easiest to *see*, not the work that was largest — and it addressed 1.8% of the cost.

**The plausible algorithmic win that is a regression.** Reconciliation performed an O(n) tree search inside an O(n) loop. Replacing it with a node index is textbook. Benchmarked:

| leaves | `Find` (O(n²)) | index (allocating) | index (scratch-reused) |
|---:|---:|---:|---:|
| 2 | 92 ns | 531 ns | 179 ns |
| 8 | 710 ns | 1179 ns | 800 ns |
| 32 | 11213 ns | 8014 ns | **3309 ns** |

Allocating a fresh map costs more than the depth-first scans it replaces until roughly 24 leaves. A real workspace holds two to eight tiles. The obvious improvement was a **regression across the entire realistic input range**. Reusing one scratch map moves the crossover to about 10 leaves and reduces the small-tree penalty to ~70 ns — noise against a 5 ms paint. It was kept as protection against pathological trees, not as a speedup, and it is documented that way so nobody cites it as one.

**Measurement tools that look like design directions.** The paint-suppression flag produced the decisive 188× number. It is also not implementable as a feature: with paint suppressed, `frames_painted` stayed at 506 and total paint time did not move, because skipping the paint leaves the window's background pixmap stale at the new size, the server generates an `Expose`, and the frame repaints anyway. "Do not paint during the drag" requires retained content or a preview representation that stays valid while geometry changes. A flag that isolates a cost is not a proposal for removing it.

## Anti-patterns

- **Auditing for one spelling of a concept.** Three independent reviews concluded the drag loop was free of synchronous round trips because they searched for `.Reply()`. The round trips were spelled `.Check()`. Audit for the property, not for the token.
- **Trusting a spot check over a corpus.** Five strings showed zero pixel difference while the real corpus showed 18 differing pixels. Sampling proves nothing about a change that alters output.
- **Assuming the optimized path is the executing path.** On the development machine's Xorg with the `modesetting` driver, `shared_pixmaps` is reported as **false**, so the MIT-SHM path never runs and an entire prior optimization ticket is inert in that configuration. Nothing logged this above `Info` level and nobody had looked. Verify that the fast path is the one being taken before analysing it.
- **Deferring measurement until after the plan is written.** The plan was written from source and was wrong about ordering. Measurement was scheduled as its first phase, which was correct — but the plan's later phases were already committed to a priority derived from unmeasured reasoning.

## Working rules

1. **A mechanism is not a magnitude.** Reading source establishes that something happens, never how much it costs relative to everything else.
2. **The first benchmark is worth more than the tenth optimization.** The largest win here appeared within an hour of the repository having any benchmark, and it was on nobody's list.
3. **Prefer subtraction experiments.** Disabling a code path (`NO_SHM`, `NO_RESIZE_PAINT`) isolates its cost with far less effort than instrumenting it, and the result is unambiguous.
4. **Confirm the fast path is the live path.** Log capability decisions at a level someone will actually see.
5. **Use a nested server for anything needing a real display.** `Xephyr` on an existing display is disposable, scriptable, needs no console, and turns a human-in-the-loop experiment into a ninety-second command.
6. **Bound accepted regressions with a test.** If a change trades exactness for speed, encode the tolerance so the drift cannot grow later without failing.
7. **Record refuted hypotheses next to the code they explain.** The refutation is more valuable than the conclusion, because the next reader will otherwise re-derive the same plausible wrong answer from the same source.

## Where this leaves the project

Instrumentation is in place: reconciliation counters, upload-path churn counters, motion admission counters, and a paint breakdown split into compose and upload, all readable over IPC. The measurement harness runs in ninety seconds and produces directly comparable counters across code changes.

The confirmed optimizations, all verified at runtime rather than only by unit test: 700 redundant Map/Unmap requests suppressed per drag, 66% of divider repaints eliminated, 46% of motion events coalesced, one layout pass per tick instead of two, a synthetic `ConfigureNotify` replacing a whole-workspace relayout on a client-driven path, and the 7.2× glyph cache.

The open work, in the order the measurement supports: split the remaining ~98% into colour conversion versus X upload — instrumentation for this is committed but not yet run — then separate window chrome from window content, which is the change that reduces pixel volume.

Full analysis, investigation diary, and measurement harnesses live in the repository under `ttmp/2026/07/21/GGWM-012-GUIDES--import-go-go-wm-engineering-guides-and-handbook/`.

## Related notes

- Source repository: `/home/manuel/workspaces/2026-07-21/go-go-wm-goja/go-go-wm`
- Design document: `ttmp/2026/07/21/GGWM-012-GUIDES--.../design-doc/01-go-go-wm-performance-engineering-an-intern-s-guide-to-the-resize-and-render-path.md`
- Measurement harness: `ttmp/2026/07/21/GGWM-012-GUIDES--.../scripts/ggwm-xephyr-validate.sh`
