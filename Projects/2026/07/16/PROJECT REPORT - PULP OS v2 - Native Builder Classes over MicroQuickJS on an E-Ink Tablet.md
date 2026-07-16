---
title: "PULP OS v2: Native Builder Classes over MicroQuickJS on an E-Ink Tablet"
aliases:
  - PULP OS v2 report
  - ESP-51 pulp os v2
  - s3paper component extraction report
tags: [project-report, esp32s3, papers3, eink, microquickjs, javascript, embedded, firmware, widgets]
status: active
type: project-report
created: 2026-07-16
repo: /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5
ticket: ESP-51-PULP-OS-V2
---

# PULP OS v2: Native Builder Classes over MicroQuickJS on an E-Ink Tablet

This report documents the construction of `0114-papers3-pulp-os`, a firmware for the M5Stack PaperS3 (ESP32-S3, 540×960 e-ink panel) whose entire user interface is a set of JavaScript applications compiled to bytecode and executed by an embedded MicroQuickJS engine against a fluent builder API implemented as native C++ classes. The work is tracked as ticket `ESP-51-PULP-OS-V2` and builds directly on the reader-primitives firmware `0112-papers3-reader-primitives` (ticket `ESP-50`), whose subsystems were promoted into four shared ESP-IDF components in the course of this project. Everything described here was validated on hardware; the transcripts referenced throughout live in the ticket's `scripts/output/` directory.

> [!summary]
> - Four components were extracted from the 0112 firmware — `s3paper_core` (pure C++ rendering/layout/widget kernel, 38,007 host-test checks), `s3paper_m5` (EPD transaction shell), `s3paper_storage` (crash-safe persistence with fault-injection hooks), and `s3paper_runtime` (the present pipeline) — with the 0112 firmware re-pointed at each extraction stage and regression-checked on the device.
> - The v2 JavaScript API replaces the v1 flat-function ABI plus evaluated JS facade with native `Widget` and `Page` classes: the class instance's opaque value is a packed generation-checked handle, the fluent methods are C functions in ROM prototype tables, and the remaining JS kernel is two lines.
> - Closures never cross into native storage. A kernel-owned `__cbs` array roots every callback against the compacting garbage collector; native code stores integer callback identifiers and invokes them with direct `JS_Call` frames.
> - Dynamic text values — `text(function () { ... })` — are re-evaluated by an owner-loop tick; combined with a no-op-on-equal `SetText` and render-state diffing, a ticking chess clock costs one 460×86 pixel blit per second and an idle screen costs zero panel work.
> - A latent core defect was found and fixed: `MeasureText` and `BreakLines` validated font identifiers against the bitmap-fallback table, which only knows two faces, so text set in a TTF-only display face measured as invalid and vanished when placed in a row. The identical defect pattern had been fixed once before in the display backend.
> - The product — a launcher and eight applications (reader, library, dice, chess clock, 2048, tea timer, journal, random-page browser) — ships as one 26 KB bytecode image, boots directly into the launcher, sleeps behind a JS-composed sleep image, and survives deep-sleep and RTC-power-off wake cycles.

## 1. Starting position and goals

The predecessor project (ESP-50) produced a hardware-validated e-reader firmware with an unusual internal structure: a single owner task exclusively holds all application and display state; every other execution context communicates through bounded plain-old-data event queues; rendering is a retained widget tree compiled to a flat draw-op list, diffed against the previous frame, and pushed through a refresh planner that owns all e-ink waveform policy. That project ended with a proof of concept: a v1 JavaScript API in which approximately forty flat C functions (`s3Text`, `s3Config(handle, prop, a..d)`, `s3Present(...)`) were wrapped by an ES5 facade evaluated at boot, and a six-application demo OS ran from one bytecode image.

The v1 design had four measurable costs. First, the facade's wrapper prototype and closure table lived in the JavaScript heap arena, competing with application data for the fixed 160 KB allocation. Second, every gesture dispatch was serialized to an eval string (`s3Dispatch(0,270,480,3)`) and re-parsed by the engine. Third, argument validation was split between the facade and the native functions, so an incorrect call could produce either a JavaScript `TypeError` or a silent no-op depending on which layer noticed. Fourth, the facade needed a successful evaluation before any application could run, adding a boot dependency that bytecode alone would not have.

The v2 goal, fixed in the ticket's design document before implementation began, was to invert the ownership: builder objects become native class instances registered in the engine's read-only stdlib, the fluent method set moves into ROM prototype tables generated at build time, and the JavaScript side keeps only what genuinely must be JavaScript — the closures. A secondary goal, prerequisite to the first, was to stop the two firmwares from sharing code by copy: the proven subsystems had to become ESP-IDF components consumable by both.

## 2. Component extraction with a live regression guard

The extraction proceeded in three phases, each ending with the 0112 firmware rebuilt against the new layout and exercised on the device. The ordering principle was that 0112, being hardware-proven, acts as the regression suite for the components; a component that passes 0112's console evidence (trace equivalence, region ticking, page turns, catalog scans) is safe for 0114 to consume.

### 2.1 Layout and build-system mechanics

`s3paper_core` and `s3paper_m5` moved verbatim (`git mv`, history preserved) from `0112/components/` to the repository-level `components/` directory. The firmware's top-level CMake gained two decisions worth recording. `EXTRA_COMPONENT_DIRS` points at the specific component directories rather than the shared `components/` root, because the root contains unrelated components whose dependencies would otherwise enter the build graph — a failure mode observed earlier when a spike project pulled in an unresolved display library. Second, the component list is trimmed with `set(COMPONENTS main esp_psram)`; the PSRAM component must be named explicitly because a trimmed component list prunes Kconfig-only components silently, and the symptom — `CONFIG_SPIRAM` vanishing — appears only as a configure-time note.

### 2.2 s3paper_storage: inverting two couplings

The storage module (`app_storage.cpp`, 940 lines) had exactly two dependencies on its host firmware, and the extraction consisted of inverting both. The requirement that the display driver initialize before the SD card mounts — the two share an SPI bus, and mounting first once tore down the live bus — became an injected `pre_mount` callback in a `StorageConfig` structure. The embedded demo book became a configured seed (`seed_path`, `seed_text`, `seed_len`). Everything else — the five versioned, checksummed, atomically-written state files; the serialized library catalog validated by path, size, and modification time; the coalesced dirty-flag flush — moved unchanged, including a deliberately static 5 KiB scratch buffer whose earlier life as a stack local had crash-looped an 8 KiB task.

The component also gained a debug surface it did not have before: `DebugCorruptStateFile(kind, mode)` flips a byte, truncates, or deletes any state file, and `DebugReloadState()` re-runs every loader. Exposed as console commands, these closed a long-open validation gap. The recovery battery on hardware demonstrated all three designed behaviors: a corrupt primary is detected by CRC and ignored (fresh state, no crash); a truncated catalog degrades the next scan to full re-hashing, which then rewrites the catalog; a deleted primary falls back to the `.bak` generation. A subtlety worth stating precisely: `.bak` fallback triggers only when the primary is missing, not when it is corrupt, because the atomic write sequence renames the previous good file to `.bak` before renaming the temporary file into place — a corrupt primary therefore implies the `.bak` is not newer than the corruption event.

### 2.3 s3paper_runtime: the present pipeline as a service

The runtime component merges what were two firmware modules: frame storage and backend management (`app_display.cpp`) and the retained-tree present pipeline (`app_ui.cpp`). Its public surface is small: `RuntimeInit(config)` allocates draw-op, text-arena, trace, and widget-arena storage in PSRAM and registers fonts; `PresentPage(slots, intent, screen_change, hits, cap, extra_ops)` performs the full layout–compile–plan–present sequence; `PresentPageUpdate(...)` performs the diff-driven variant; `PresentCount()` exposes a monotonic counter that transient screen owners use to detect displacement.

Two invariants moved as code comments because each has a concrete failure behind it. The update path never propagates hit regions to the caller: hit regions compiled under a damage clip shrink to the clip rectangle, and propagating them once made every tap target on a chess clock die after the first second. And the tree compiler must always receive a hit-region output array even when the caller will discard it, because a node carrying a hit identifier with no output array is a hard capacity error by design.

The extraction changed one coupling for the better. The 0112 status fixture — a live clock region — previously reached directly into pipeline internals to deactivate itself when another screen presented. It now compares `PresentCount()` against the value recorded at its own last present, which is the same contract the JavaScript layer uses. The fixture's re-expression against the public API served as an early proof that the API was sufficient.

### 2.4 What deliberately did not move

The MicroQuickJS engine copy stays inside each firmware. The engine's atom table — the interned-name table both the stdlib and all compiled bytecode reference by index — is generated from that firmware's stdlib definition. Two firmwares with different stdlibs therefore have incompatible atom tables, and sharing the engine component would couple their JavaScript ABIs. Each firmware carries `components/mquickjs` with a provenance README and regenerates its own atom header.

## 3. The v2 builder API

### 3.1 Class mechanics in a ROM-table engine

MicroQuickJS differs from mainstream engines in that the standard library, including class definitions, prototype tables, and all interned strings, is generated at build time into a single constant array placed in flash. A host-side generator (`pulp_stdlib.c` compiled with `mquickjs_build.c`) consumes declarative macro tables and emits two artifacts: a 32-bit stdlib table included by the device build, and the matching atom header included by the engine. User classes are declared in the same tables:

```c
static const JSPropDef js_widget_proto[] = {
    JS_CFUNC_DEF("pad", 4, js_w_pad),
    JS_CFUNC_DEF("size", 1, js_w_size),
    JS_CFUNC_DEF("onTap", 1, js_w_on_tap),
    /* ... nineteen more ... */
    JS_PROP_END,
};
static const JSClassDef js_widget_class =
    JS_CLASS_DEF("Widget", 0, js_widget_ctor, JS_CLASS_WIDGET,
                 NULL, js_widget_proto, NULL, js_widget_finalizer);
```

The function names are stringified references resolved when the generated header is included by a device translation unit that has the prototypes in scope. The device defines `JS_CLASS_WIDGET` as `JS_CLASS_USER + 0` and — a detail that cost one build failure on the device and one on the host tool — must define `JS_CLASS_COUNT` to cover the user classes, because that macro sizes the generated finalizer table.

An instance of such a class is an ordinary heap object carrying one pointer-sized opaque value. The v2 design stores a packed widget handle there: `(generation << 16 | index) + 1`, biased so a valid handle is never the null opaque. Every prototype method resolves `this` through the same helper: verify the class identifier, unpack the opaque, and look the handle up in the widget arena, which checks both index bounds and generation equality. A stale wrapper — one whose node was destroyed or whose tree was reset — produces `TypeError: stale widget handle` at the exact call site. The finalizer is deliberately a no-op: the retained tree owns node lifetime; wrappers are views. This is the inverse of the conventional binding pattern in which the wrapper owns the native object, and it is what makes `resetTree()` safe: bumping generations invalidates every outstanding wrapper without any bookkeeping on the JavaScript side.

Fluent chaining is `return *this_val;`. The engine's compacting garbage collector may move objects during any allocating call, but `this_val` points into the interpreter frame, which the collector updates; returning its current value after intermediate allocations is therefore correct where returning a copy captured before them would not be.

### 3.2 Closures stay on their side of the boundary

The single most consequential rule in the design is that native code never stores a `JSValue`. The engine's collector compacts; a `JSValue` held in a C static across an allocation is a dangling reference waiting for the next collection. The v1 design obeyed this rule by keeping callbacks in a facade-owned JavaScript object and dispatching through eval strings. The v2 design keeps the rule but removes both the facade and the parser from the path:

- A two-line kernel, evaluated once at context creation, defines `var __cbs = [null];` and the gesture-constant table `G`.
- `RegisterCb(ctx, fn)` assigns the next integer identifier and stores the function with `JS_SetPropertyUint32(cbs, id, fn)`. The array is reachable from the global object, so the collector treats the closure as live and updates the array slot when the closure moves.
- `onTap(fn)` writes the callback identifier into the widget node's hit-identifier field. The identifier that the hit-test returns for a tapped point *is* the callback index — there is no translation table.
- Dispatch pushes a direct call frame: `JS_PushArg` for the arguments in reverse order, the function, and the `this` value, then `JS_Call(ctx, argc)` under a one-second interrupt deadline. No source text is constructed or parsed.

One engine-specific sharp edge surfaced immediately: the dialect treats array holes as errors, so re-creating `__cbs` as an empty array and then writing index 1 threw `TypeError: invalid array subscript`. The reset path now seeds slot 0 with `null` before callback registration resumes.

### 3.3 Pages, ticks, and dynamic values

`Page` instances are views over a fixed native table of twelve entries, keyed by name so `page('blitz')` retrieves the same retained entry across calls. A page holds the four widget-tree slots (header, content, footer, overlay), one callback identifier per gesture kind, an optional tick callback, and a tick interval. `show(full)` presents through the runtime (clean-full or partial); `update()` presents through the diff path.

Dynamic values are the piece that makes application code shrink. `text(fn)` detects a function argument, registers it in `__cbs`, records `{widget handle, callback id}` in a native table, and evaluates the function once for the initial text. The owner loop's timer tick then does, in order: invoke the page's tick callback if present, re-evaluate every live dynamic value and `SetText` the result, and issue exactly one diff-update present. Three properties compose here. `SetText` returns without bumping the content version when the new string equals the old one; the render-state diff maps version changes to exact damage rectangles; and the planner merges and aligns those rectangles before the panel sees them. The chess clock's entire per-second cost is consequently one 460×86 rectangle (about 15 ms of render time), and when the clock is paused the tick performs no panel work at all — the transcripts show the per-second present log line with no accompanying backend line.

The chess clock application, complete, for comparison against its v1 form that manually managed label updates:

```js
ui.bt = text(function () { return fmtClock(z.b); }).size('xl').center();
ui.mid = text(function () {
  if (z.w <= 0) { return 'WHITE FLAGS'; }
  if (z.b <= 0) { return 'BLACK FLAGS'; }
  return 'MOVES ' + z.moves;
}).size('lg').center();
p.on(G.LONG, function () { settle(); z.run = 0; p.update(); });
p.on(G.TICK, function () { settle(); });
p.every(1000);
p.show(true);
```

### 3.4 Navigation grammar as a dispatch order

Gesture routing is a fixed native sequence: a tap first consults the hit-test over the last present's regions and calls the topmost hit's callback; any gesture then consults the current page's per-kind handler; an unhandled swipe-down finally falls through to the `paper.home` callback. Applications trap swipe-down simply by registering a handler for it — 2048 binds all four swipes to moves and exposes home as a button — and every other screen inherits swipe-down-goes-home without writing anything. The dispatch order is the navigation policy.

## 4. A case study: the glyph that vanished

One defect consumed the largest single debugging block of the project and is worth recording as a pattern. The tap-probe screen built `text('taps: 0').size('lg')` inside a padded row; on hardware, the counter simply did not render — the full-screen present contained one glyph run instead of two — while the identical tree built directly against the C++ API on the host rendered both texts.

The localization sequence was: a variant matrix probe (five texts in differing row/column/padding configurations, all in the default font) rendered completely, which exonerated the row layout, the variadic `add`, and the wrapper plumbing; a fake-backend trace probe showed the missing op precisely; a host reproduction with the production font file then showed `MeasureText` returning `InvalidArgument` for every string in the display face while line metrics for the same face succeeded. The cause: `MeasureText` and `BreakLines` guarded their font argument with `GetFont(font_id) == nullptr`, where `GetFont` is the *bitmap-fallback* lookup that knows only the two original faces. The display faces registered later are TTF-only; measurement rejected them, a row lays its children out at intrinsic (measured) width, the text got zero width, and the fully-clipped glyph op was dropped — silently, because dropping fully-clipped ops is correct behavior.

Two texts in the same face behaved differently because a column stretches its children on the cross axis: the title needed only line metrics (which worked), while the row child needed width measurement (which failed). And the defect had a sibling: the display backend's glyph-run guard had the exact same two-face assumption, found and fixed weeks earlier. The correct response to finding a legacy-assumption bug once is to search for the assumption pattern, not the symptom; the fix this time patched both remaining call sites and added a host regression test that registers a TTF-only face and asserts measurement succeeds.

## 5. The product, and what live operation added

The application image contains a launcher and eight applications in roughly 600 lines of ES5: Library (scans the card, serif titles), Reader (native pagination through the book service, JavaScript chrome and gestures — and because the layout key matches 0112's, a book left open in the old firmware resumes at the same page in the new one), Dice Tray, Blitz Ink, 2048 INK, Tea Timer, Postcard (a 30-key tap keyboard appending one line per day to a journal file that the library scan then lists as a book), and Daily Pulp (a random page from a random book). Boot mounts the card, seeds a Ukrainian-language sample book (the font subsets carry Latin and Ukrainian Cyrillic; the seed proves the whole path), loads persistence, creates the JavaScript context, loads the bytecode image before any evaluation — the loader requires an atom-table state with no RAM atoms — and runs the launcher with a clean full refresh.

The operator used the physical device during validation, which produced three findings no console transcript would have: tap targets the size of a rendered word are too small for fingers (the dice buttons became 108×72 boxes; every text button in the OS gained explicit dimensions); separator rules read as sloppy when their margins differ from the header rule's (launcher and shelf separators now share the 40-pixel margin); and repeated partial updates in 2048 accumulate visible ghosting (the application now issues a clean-full re-blank every twelfth present — application-level policy, chosen over tightening the global planner budget because only this screen has the problem). A fourth request added a fifth registered face, `kFontTitle` (the serif at display size), for shelf typography.

Power completes the product loop. The sleep sequence quiesces input, flushes persistence, presents a sleep image — now built by a JavaScript lambda registered through `paper.sleepImage(fn)`, evaluated by the power module through the same callback machinery as everything else — unmounts the card, and enters the requested state. Both timed wake paths were exercised: deep sleep (timer wake, boot cause 8/4) and BM8563 RTC power-off (relatch, boot cause 1), each resuming into the launcher.

## 6. Numbers

| Measure | Value |
|---|---|
| Host test suite (s3paper_core) | 38,007 checks, ASan/UBSan, < 1 min |
| Bytecode image (launcher + 8 apps) | 26,020 bytes |
| JS heap arena | 160 KB, PSRAM |
| Remaining JS facade (v2 kernel) | 2 lines |
| Chess-clock tick cost | 1 rect, 460×86 px, ~15 ms render |
| Tap-callback response (probe 3) | 1 rect, 127×45 px |
| 0114 binary | 998 KB (vs 0112's 1,002 KB with the native reader) |
| Firmware-specific JS platform code | ~1,760 lines across 6 files |
| ESP-51 commits this session | 16 (Phases 0–8) |

## 7. Assessment

The v2 API achieved its structural goals: prototypes and dispatch live in flash, the parser is out of the interaction path, validation happens exactly once at the native boundary, and application source shrank where the new primitives apply (the blitz clock lost its manual label-update function entirely). The extraction discipline — never letting 0112 stay broken longer than one phase — caught nothing this time, which is itself the result: four subsystems moved without a regression reaching the old firmware.

The engineering lesson worth keeping is the pairing of probes with introspection. The validation probes (deterministic screens with announced names and countable draw ops) found the vanished glyph; but localizing it took a trace dump and a hit-region dump that did not exist yet and had to be built mid-hunt. Both are now permanent console commands (`js probe N`, `js hits`), and the next coordinate-dependent bug will not require guessing tap positions from typography estimates.

Remaining work under the ticket is Phase 9: capacity saturation (arena-full from JavaScript, callback-registry growth, event-queue flood), a scripted mixed soak with heap watermarks, the trace-equivalence harness port, and the license inventory. None of it blocks daily use of the device, which as of this report boots into PULP, plays a chess game, brews tea, and goes to sleep showing its own name in 84-pixel serif-free Swiss bold.
