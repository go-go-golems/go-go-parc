---
title: "A Canvas for E-Ink: Adding Freehand Primitives to a POD Widget Tree"
aliases:
  - esp-52 canvas case study
  - eink canvas primitives report
  - s3paper canvas widget deep dive
tags: [project-report, eink, esp32s3, papers3, rendering, widgets, fuzzing, javascript, embedded]
status: active
type: project-report
created: 2026-07-16
repo: /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5
ticket: ESP-52-EINK-CANVAS
---

# A Canvas for E-Ink: Adding Freehand Primitives to a POD Widget Tree

This report is a case study in extending a finished rendering stack by one capability, end to end, in a single working day. The capability is freehand drawing — line segments at arbitrary angles, filled and stroked circles, rectangles, and area fills — added to the s3paper stack that drives the M5Stack PaperS3's 540×960 e-ink panel, exposed to JavaScript as a `Canvas` widget in the PULP OS builder API, and demonstrated by a three-scene showcase application. The work is ticket `ESP-52-EINK-CANVAS`; it landed in five commits on top of the ESP-51 platform described in the two companion reports ([[PROJECT REPORT - PULP OS v2 - Native Builder Classes over MicroQuickJS on an E-Ink Tablet]], [[PROJECT REPORT - Binding MicroQuickJS - Handles, Atoms, and the Compacting GC in the PULP OS Builder Layer]]).

The interest of the case is not the primitives themselves — a line and a circle are not research — but the constraint field they had to be threaded through: a draw-op vocabulary designed around damage rectangles, a widget tree whose nodes are fixed-size plain-old-data structures that cannot hold a variable-length anything, a render-state differ that only understands version counters and frames, two backends that must agree byte-for-byte on semantics, and a JavaScript boundary with strict garbage-collection rules. Every design decision below is the resolution of one of those constraints, and the section on the fuzzer is a reminder of why the stack's test discipline pays for itself: the first run of the extended fuzzer found a lifetime bug that had been latent in the tree code through two shipped tickets.

> [!summary]
> - Two new draw-op kinds (`Line`, `Circle`) follow the established GlyphRun pattern: true pre-clip geometry in the payload, the clipped bounding box in `bounds` for damage accounting, and per-pixel clipping delegated to the backend via the op's `clip` rectangle.
> - Canvas content lives in arena-owned command slabs (8 slots × 96 commands × 12 bytes), not in the widget node; the node stores only a slot index. Commands are canvas-relative, so a moved canvas needs no command rewrite, and appends bump the node's content version so the existing differ produces damage with no new mechanism.
> - The M5GFX backend renders thickness by parallel-line offsetting along the minor axis and rings by concentric outlines — never by filling and re-erasing, which would destroy underlying content.
> - Extending the widget fuzzer with canvas operations immediately exposed a pre-existing defect: destroying a still-linked child left a dangling child index in the parent, and slot reuse could then create link cycles that made every tree walk recurse forever. `Destroy` now unlinks first.
> - The showcase application ("Ink") demonstrates the panel's economics deliberately: an analog clock that costs exactly one canvas blit per minute (36 blits in a 36-minute soak, silence between), and two compositions that arrive on intentional clean-full flashes.

## 1. Starting constraints

The stack the canvas had to join was complete and hardware-proven, which cuts both ways: every layer offered a pattern to copy, and every layer imposed an invariant that could not be relaxed. The relevant ones:

1. **Draw ops are POD and self-describing.** A `DrawOp` carries its kind, gray level, a `bounds` rectangle, the `clip` rectangle in force when it was emitted, and a payload union. `bounds` is consumed by the damage machinery (frame damage is the union of op bounds); `clip` is consumed by backends whose rasterization can exceed `bounds` (glyphs already did; circles and thick lines would too). Ops never carry pointers into transient storage.
2. **Fully-clipped ops are dropped and counted** by the `FrameBuilder`, never emitted. Damage exactness depends on this.
3. **Widget nodes are fixed-size POD** in a 128-slot arena with generation-checked handles. A node is ~136 bytes with a props union; there is no place for a growable list, and adding heap pointers to nodes would break the arena's reset-by-generation lifetime model and its host-testability.
4. **Change detection is `content_version`.** Mutators bump the counter; `RenderStateDiff` compares captured versions and frames per slot and emits damage rectangles. Anything the canvas does to the screen must be expressible as "this node's version changed within this frame."
5. **Two backends, one truth.** The fake backend renders to a normalized text trace (golden-tested, and the substrate of the trace-equivalence harness); the M5 backend renders to the panel. A primitive exists only when both agree on its semantics.
6. **JavaScript sees native classes.** Whatever surface the canvas exposes must obey the binding layer's rules: no `JSValue` retained natively, all arguments copied out before allocating calls, staleness by generation, errors as `TypeError` at the call site.

## 2. Phase 1: the op vocabulary

### 2.1 Payload design

The existing vocabulary (`FillRect`, `StrokeRect`, `HLine`, `VLine`, `GlyphRun`, `Bitmap`) is rectilinear; its geometry is fully described by `bounds`. A diagonal line or a circle is not: clipping its bounding box loses the actual shape. The GlyphRun op had already solved this problem — the payload carries the baseline and text while `bounds` carries the clipped box — so the new payloads copy the split exactly:

```cpp
struct LinePayload  { int32_t x0, y0, x1, y1; int32_t thickness; };
struct CirclePayload{ int32_t cx, cy, r;      int32_t thickness; };  // 0 = disc
```

Endpoints and centers are *true pre-clip geometry*. The rasterizer draws the true shape and lets the panel clip (`M5.Display.setClipRect(op.clip...)` is already applied per-op by the backend loop, so the new ops inherited clipping without writing any). One op kind serves both filled and stroked circles, discriminated by `thickness`: zero means disc, positive means a ring of that width measured inward from `r`. This halves the switch cases everywhere downstream at the cost of one convention to document.

### 2.2 Bounding-box arithmetic

The emitters compute conservative clipped boxes:

```
Line:   bbox = { min(x0,x1) - t/2, min(y0,y1) - t/2,
                 |x1-x0| + t + 1,  |y1-y0| + t + 1 }
Circle: bbox = { cx - r, cy - r, 2r + 1, 2r + 1 }
```

The `+1` terms make the boxes closed over the endpoint pixels in the stack's half-open rectangle convention; the `t/2` inflation covers thickness emulation on either side of the ideal segment. The emitter intersects the box with the current clip, drops-and-counts when empty, and otherwise emits with `bounds = clipped box`. Damage therefore never under-reports (the diff would leave stale pixels) and over-reports by at most the difference between a diagonal's box and its coverage — acceptable, because the refresh planner merges and aligns damage anyway. Argument validation rejects non-positive line thickness and negative radii, and clamps a ring thicker than its radius into a disc (the geometrically equivalent object) rather than erroring, a choice recorded in the host test.

### 2.3 Two backends

The fake backend appends one line per op in the established format, e.g. `op kind=Line gray=0 bounds=39,39,163,83 clip=... from=40,40 to=200,120 t=2` — the payload fields printed after the common prefix, byte-stable for goldens.

The M5GFX backend required two rendering decisions:

- **Thick lines.** M5GFX has no thick-line primitive. The backend draws `t` parallel one-pixel lines offset along the *minor* axis of the segment (vertical offsets for shallow lines, horizontal for steep ones), centered by offsetting from `-t/2`. This is the standard fallback; its known artifact — slight ropiness on thick near-diagonal lines — is documented and irrelevant at the thicknesses the OS uses (≤ 6).
- **Rings.** The tempting implementation — fill a disc of radius `r`, then fill radius `r − t` in white — is wrong on this stack: the interior fill would erase whatever the scene had already painted underneath, and e-ink scenes compose incrementally. Rings are therefore `t` concentric `drawCircle` outlines stepping inward. Slower, correct.

### 2.4 What the host tests pinned

`TestLineCircleOps` (34 checks) asserts the bbox arithmetic for in-view, partially-clipped, and fully-clipped (dropped and counted) cases; payload round-trips through clipping untouched; the thickness clamp and the invalid-argument rejections; and the exact fake-backend trace substrings for one op of each new kind. The suite ran green at 38,041 checks before any widget work began — the vocabulary was proven in isolation first.

## 3. Phase 2: the Canvas widget and the command store

### 3.1 Where a command list can live

The central design decision of the ticket. A canvas is, semantically, a variable-length list of drawing commands, and constraint 3 forbids putting one in a node. Three placements were considered:

- *Heap allocations referenced from the node.* Rejected: nodes gain owning pointers, `Reset()` gains a traversal-and-free obligation, host tests gain allocator behavior, and the generation-invalidation lifetime model gains an exception.
- *A store owned by the runtime component.* Rejected: `CompileTree` lives in `s3paper_core` and must read the commands; core cannot depend on the runtime above it, and passing a store parameter through `CompileTree` would ripple through every caller including 0112.
- *A store owned by the `WidgetArena` itself.* Chosen. The arena already owns node lifetime and is visible to layout, render, and diff; canvases are node content, so their storage belongs with the nodes.

The store is compile-time sized: `CanvasCmd canvas_[8][96]` plus per-slot counts and in-use flags — 8 canvases × 96 commands × 12 bytes = 12 KiB, growing the arena from ~17 KiB to ~29 KiB of PSRAM (confirmed against the boot log's `runtime ready` line). The command itself is a 12-byte POD:

```cpp
struct CanvasCmd {
    enum Kind : uint8_t { kFill, kBox, kLine, kDisc, kRing };
    uint8_t kind; Gray8 gray; uint8_t thickness; uint8_t _pad;
    int16_t a, b, c, d;   // rect: x,y,w,h | line: x0,y0,x1,y1 | circle: cx,cy,r,-
};
```

`int16_t` coordinates bound the command size; the panel is 540×960, and canvas-relative coordinates (see below) keep every legitimate value far inside the range. The JS binding clamps rather than errors on overflow.

The node side is two half-words: `CanvasProps { uint16_t store; }` in the props union, plus the count living in the arena's per-slot array. `NewCanvas(arena)` finds a free slot, creates a `WidgetKind::Canvas` node, and links the two; `Destroy` and `Reset` release the slot (found by the fuzzer to need care — §5). Exhaustion of the eight slots is an explicit `CapacityExceeded`, surfaced in JavaScript as `TypeError`.

### 3.2 Canvas-relative coordinates

Commands are stored relative to the canvas's own origin; the emitter adds the laid-out frame's origin at compile time. Two properties fall out. A canvas that moves — because layout reflowed around it — needs no command rewrite, and the differ handles the move as ordinary frame damage. And command emission composes with the tree's clipping naturally:

```
case WidgetKind::Canvas:
    if (!fb.PushClip(frame).ok()) return Ok      // disjoint: nothing to draw
    for cmd in arena.CanvasCmds(node):
        emit at (frame.x + cmd.a, frame.y + cmd.b, ...)
    fb.PopClip()
```

`PushClip` intersects with the ambient clip (the ancestor-frame intersection `CompileTree` already maintains), so a command whose geometry exceeds the canvas box is clipped to the box — freehand drawing cannot escape its widget, an invariant the host test proves with a line aimed well past the frame. One mechanical consequence: `EmitNode` needed the arena to reach the store, so its signature grew a parameter; the single call site made this a two-line change.

### 3.3 Change detection for free

`CanvasAppend` and a non-empty `CanvasClear` bump `content_version`; the differ needs nothing new. The granularity is deliberately coarse: any change burst damages the whole canvas frame, not the changed command's box. The trade was examined and accepted — computing per-command damage would require diffing command lists inside the differ (a new mechanism, contradicting constraint 4), and the two consumers in sight redraw wholesale anyway (the clock wipes and rebuilds per minute; compositions present clean-full). The report's obligations: the coarseness is documented at the API, and the measured cost at the showcase's rates is one 460×790 blit per minute.

Layout was the last core touch: a canvas reports no intrinsic size (like the Book widget), so it is sized by `fixed_w`/`fixed_h` or flex, and an unsized canvas collapses — the `-Werror=switch` build flag is what forced this decision to be made explicitly rather than by omission, flagging the one measurement switch the new enum value had not covered.

## 4. Phase 3: the JavaScript surface

The binding adds a factory and six prototype methods, declared in the stdlib tables (with the full regeneration protocol from the companion report — both headers, then bytecode, then firmware) and implemented over one shared parser:

```
canvas()                              -> Widget (Canvas kind)
.line(x0,y0,x1,y1, gray, t?)   .disc(cx,cy,r, gray)
.ring(cx,cy,r, gray, t?)       .box(x,y,w,h, gray, t?)
.paint(x,y,w,h, gray)          .wipe()
```

`CanvasMethod(ctx, this_val, argc, argv, kind, n_coords, has_thickness, usage)` resolves `this` through the standard generation-checked helper, rejects non-Canvas nodes (`TypeError: line: not a Canvas` — kind errors carry the usage string), parses `n_coords` integers plus gray plus optional thickness with `JS_ToInt32` (propagating conversion exceptions), clamps coordinates to `int16` and thickness to `uint8`, and converts a store `CapacityExceeded` into `TypeError: canvas append failed`. Naming avoided `fill` and `clear`, both already meaningful elsewhere in the stack (`FillRect`, `CanvasClear` vs. text-clearing idioms); `paint` and `wipe` collide with nothing.

Validation reused the two-probe pattern: `js probe 11` renders one of every primitive on the panel (10 ops, clean full) and then proves containment inline — a `line` call on a text widget throws the kind error, and a 200-iteration append loop throws capacity. `js probe 12` is the same program through the fake backend with the op list printed; its transcript shows the frame-relative arithmetic exactly (a line stored as `(20,20)→(480,680)` in a canvas laid out at `(40,91)` emits `from=60,111 to=520,771`) and the clip pinned to the canvas frame `40,91,460,700`. The phase worked on its first flash — the value of the ESP-51 helpers (`ThisNode`, `MakeWidget`, the error conventions) is that a new class surface is mostly declarative.

## 5. What the fuzzer found: Destroy-while-linked

The plan required extending the deterministic widget fuzzer with canvas operations — random `NewCanvas`, bursts of appends with random command fields, occasional clears — on the theory that slot allocation was new lifetime machinery and lifetime machinery is where fuzzers earn their keep. The very first run died with an AddressSanitizer stack overflow in `WidgetArena::DestroyIndex`.

The defect was not in the canvas code. The fuzzer's op mix had shifted (canvas creation consumed different pseudo-random draws), steering it into a sequence the old mix had never produced: **destroy a node that is still linked as some parent's child, then reuse its slot.** `Destroy` cascaded through the subtree and freed the slot but did not unlink it from the parent, whose child index now dangled. When a later `Create` reused the slot, the stale parent silently adopted the new node — and once a node is reachable as a child of two parents, sibling chains can close into cycles, at which point every recursive tree walk (destroy, layout, measure) recurses until the stack ends. The contract comment on `Destroy` ("the node must not still be linked") had made this the caller's problem; the fuzzer, legitimately, does not read contract comments.

The fix makes the operation total instead of contractual: `Destroy` now unlinks from a live parent (via the existing `RemoveChild`, using the parent links added during the ESP-50 cycle-bug fix) before cascading. Thirteen lines, one comment explaining the history, suite green at 38,174 checks.

Two observations for the pattern file. First, this is the second time in this codebase that a *change in fuzz op mix* — not a new fuzzer, not more iterations — surfaced a real latent bug within seconds (the first was the AddChild diamond/cycle defect in ESP-50). The lesson is that a fuzzer's coverage is a function of its operation distribution, and every new API is a reason to redraw that distribution. Second, the bug had survived two tickets of heavy tree usage because application code happens to detach before destroying; "the code that exists never does X" is exactly the property fuzzing exists to falsify.

## 6. Phase 4: Ink, and the economics of the panel

The showcase application had a design brief beyond "draw things": demonstrate what e-ink is *for*, using the refresh vocabulary the stack already owns. Ink is one retained page, one canvas, three scenes rotated by tap, with swipe-down inheriting the OS-wide go-home grammar:

- **Clock.** A ring face (r = 190), twelve tick marks with heavier cardinals, hour and minute hands as thick lines, a disc-and-ring hub — seventeen commands. A one-second page tick compares the minute; on change it `wipe()`s, re-appends, and issues a diff update. The measured behavior over a 36-minute soak: 36 update presents at 60.26-second spacing, each a single 460×790 rectangle at ~15 ms render time, and *no panel activity whatsoever between them* — the per-second ticks run layout and diff, find zero damage, and stop. Heap minimum-free stayed within 2.7 KB of resting over 1,944 ticks with zero exceptions. One screen, then, states the platform's whole argument: persistent image, exact damage, silence as the default.
- **Field.** A generated composition — thirty discs and rings across the gray range with three-weight variation, four full-height hairlines — presented with a deliberate clean full. On this panel the full-refresh flash is usually treated as a cost; a gallery reveal is the one context where it reads as intent.
- **Ladder.** Sixteen concentric rings stepping through the sixteen gray levels plus a labeled strip along the bottom — the palette as a composition, doubling as a panel diagnostic.

The clock's honest limitation is recorded rather than hidden: the firmware exposes no wall-clock to JavaScript (the BM8563 RTC has no binding yet), so it displays minutes since boot and its caption says so. A future `rtcNow()` binding changes one line of the scene.

## 7. Numbers

| Measure | Value |
|---|---|
| New op kinds / payload bytes | 2 kinds; 20 B (line), 16 B (circle) payloads |
| Command store | 8 slots × 96 cmds × 12 B = 12 KiB; arena 17 → 29 KiB PSRAM |
| Host suite growth | 38,007 → 38,174 checks (ops, widget, fuzz extension) |
| Scene command counts | clock 17, field 34, ladder 34 (cap 96) |
| Clock steady-state cost | 1 blit/min, 460×790, ~15 ms render; 36/36 minutes in soak |
| Fault surfaces proven in JS | kind mismatch, store capacity, stale handle (inherited) |
| Latent bugs found by the fuzz extension | 1 (Destroy-while-linked), fixed |
| Commits | 5 (P1 ops, P2 widget+fix, P3 binding, P4 app, P5 closure) |
| Ticket state | closed, all 16 tasks complete, doctor clean |

## 8. Assessment

The ticket's real subject is extensibility. The canvas touched every layer of the stack and yet required no new *mechanisms* — no new damage model, no new lifetime model, no new binding pattern, no new validation technique. Each layer had one extension point shaped in advance by an invariant: payloads for non-rectilinear geometry, the arena for node-adjacent storage, `content_version` for change detection, the shared method parser for the JS surface, probes and traces for proof. Where a decision was genuinely open (command granularity in the differ, ring rendering, coordinate frames), the constraint field made one option clearly cheaper, and the report of record documents why.

The counterweight to that tidiness is the fuzzer's find: a stack this disciplined still carried a two-ticket-old lifetime bug in its most-used data structure, discoverable only when a new feature perturbed the test distribution. The closing recommendation is therefore procedural rather than architectural — treat every API addition as an obligation to extend the fuzz op mix in the same commit, because that is where this codebase's two worst latent defects were found, both within seconds of the mix changing.
