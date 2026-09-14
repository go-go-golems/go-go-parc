---
title: Makera Z1 Control — G-code Inspector from Dictionary to Firmware Trace to Page
aliases:
  - dropcut G-code Inspector technical report
  - MZ1-017 opcode dictionary and Inspector implementation
tags:
  - project
  - cnc
  - gcode
  - react
  - codemirror
  - evidence
status: active
type: project
created: 2026-09-14
project_started: 2026-08-11
repo: /home/manuel/workspaces/2026-08-11/cnc-control-dropcut/dropcut-studio
branch: task/cnc-control-dropcut
implementation_commit: acb55f0
source_tickets: MZ1-017
scope: the opcode dictionary package, the dropcut decode CLI, the source-grounded firmware opcode trace, and the Inspector web page with live browser validation
implementation_status: complete and live-validated; ticket closed (recorded future work: per-entry firmwareStatus property, M2/M22 handler locations, control-page preview)
---

# Makera Z1 Control — G-code Inspector from Dictionary to Firmware Trace to Page

A CAM application that compiles JavaScript into verified G-code has an obvious blind spot: files it did not produce. Any real shop receives `.nc` files from other exporters, from vendors, and from three years ago. This report covers the construction of the tool that closes that gap — the G-code Inspector — and the three layers built beneath it in the correct dependency order: an opcode dictionary with provenance, a headless decoder that proves the pipeline outside any browser, and a source-grounded trace into the machine's firmware that determines what the words on a line actually do on this specific machine. The Inspector page is the fourth layer and the only one that needs a browser; everything under it is testable without one.

The report's engineering content is concentrated in two places. First, the design decision that gives per-line answers without a second interpreter: the parser records its own modal state per line, so "what does this bare `X14.81` mean" is answered by the state machine that owns the answer. Second, the six defects that live browser validation found after the static validation (typecheck, 294 tests, production build) had all passed. None of the six was caught by the test suite, and each is a named failure class worth recording: the test suite covers the pure pipeline; the browser covers the wiring between the pipeline and the human.

## 1. The problem, stated precisely

Three questions a reviewer asks of an unfamiliar file, and what answering each requires:

1. **What does this file contain?** — structure: headers, motion count, tool changes, time estimate, bounds. Requires a full modal parse, not a line scan: feed rates, units, and distance mode carry across lines.
2. **What does this line mean?** — semantics: the dictionary meaning of each code, the resolution of each parameter word against the units in force, and what the interpreter made of the line (segment geometry, duration).
3. **What does the machine actually do with this code?** — ground truth: which firmware handler receives it, and which codes are inert despite being standard G-code.

Question 3 is where this project departs from generic G-code viewers. The Makera Z1's firmware is Marlin-derived with machine-specific additions, and its behavior deviates from RS-274 in load-bearing ways — most notably, `M30` does not end a program on this firmware; it deletes a file from the SD card. A decoder that answers from the standard alone would be confidently wrong exactly where a user needs it to be right.

## 2. Layer 1 — the dictionary as a package with a drift test

`@cam/gcode-codes` is deliberately a workspace package, not page-local data, for one reason: the "supported on this machine?" flag must agree with the machine profiles the compiler and parser already consume, or the UI lies. Each entry carries `letter`, `number`, `group`, `modality`, a one-sentence `summary`, optional `parameters`, `aliases` (M5/M05 are one entry), `notes`, and — the part that makes it maintainable — `sources`: `RS-274` for standard semantics, `MZ1-001/006/016` for this repository's own hardware evidence, and `vendored <file>:<line>` for semantics read directly from the firmware source.

The conformance test is the package's enforcement mechanism: every G/M code claimed by any registered machine profile must have a dictionary entry. The profiles describe the *compiler's emission dialect*; the dictionary describes *firmware behavior*. These two sets can drift apart in both directions — a profile claiming a code the firmware ignores (eight such codes exist: G40/41/42, G43/49, G80, G93/94), and firmware implementing behavior no profile models (the entire ATC block M480–M499). The drift test turns silent drift into a failing test instead of a lying UI.

## 3. Layer 2 — the CLI decoder, or the pipeline proven outside the browser

`dropcut decode <file.nc> [-m machine] [--line N]` and `dropcut codes [-m machine]` run the identical pipeline the page later uses: `parseGcode` with the selected machine's `supportedG`/`supportedM` sets (dialect warnings fall out for free), plus summary, structured `;@MKR|` headers, a codes-used census with meanings and support flags, and per-line word decode. Tokenization comes from the parser's exported `wordsOf` — one tokenizer owner, so the CLI and the UI can never diverge from the interpreter.

The CLI's second role is evidence discipline. The real operator-provided file — `MakeraBadge.nc`, 18,532 lines, 328 KB, a Makera Studio export with a full `;@MKR|` header block — is committed as a parser fixture with its decode numbers pinned: 18,231 moves (17,439 cut, 792 rapid), 18 headers, tool changes T2@22 and T1@17,460, a monotonic cumulative-time property, and a sub-second parse budget. Every layer built afterward asserts against the same numbers; the one set of facts is checked at each boundary.

## 4. Layer 3 — the firmware trace: what "supported" actually means

The trace document maps every opcode to its handler in the vendored firmware with fifty links into the source tree, and its census method matters as much as its results. The firmware has no central opcode table: a serial line becomes a `Gcode` object broadcast to every module, and "the supported set" is the union of what modules happen to handle. Three structural consequences:

- **Halt gating** is dispatcher-level: while halted, everything is ignored except M999 plus a short query allow-list — the mechanism behind the controller's evidence-gated unlock.
- **G53 is not a module code**: the dispatcher rewrites the same line's movement to machine coordinates, and refuses if the modal motion group exceeds 3.
- **The accessory outputs are config-born**: M7/M9 (air), M811/M812 (spindle fan), M821/M822 (light), M801/M802 (aux), and the probe/tool-sensor family have no hardcoded dispatch at all — the Switch module binds them from `switch.*` config sections at boot. This is also why the two stock config defaults genuinely disagree about what M801 drives, and why its `S` word is a raw sigma-delta byte (1–255), not a percentage.

The findings that corrected earlier assumptions are now in the dictionary with their handler references: M30 removes SD files (SimpleShell.cpp:221); M331/M332 are vacuum/CNC *mode* switches, not output toggles; M0/M1/M4 have no handlers; eight profile-claimed codes are inert; arcs exist in firmware motion modes even though the exporter never emits them (the profile's "cannot arc" is an exporter fact); M3 is dual-purpose — spindle normally, laser when laser mode is enabled.

## 5. Layer 4 — the page: architecture in one paragraph

The Inspector is a page in the existing studio app, not a fourth app — the reuse targets (store patterns, viewport, CodeMirror setup) live there, and it shares no state with the project page. It is loaded with `React.lazy` and code-splits into its own 28.9 kB chunk. Redux follows the project's established tiering exactly: the store holds the file name, text, and small serializable summaries; the `ParseResult` (which contains `Set`s), the 18k-motion array, the `Float32Array` render buffers, and the line→segment index live in a tier-2 cache behind an id. The serializability middleware that the tiering exists to protect stays on. The viewport is a second `createViewport` instance — created on mount, disposed on unmount — so the project page's singleton keeps its own lifecycle and the pages never swap buffers behind each other.

## 6. Modal snapshots: answering "what does this line mean" without a second interpreter

The interesting question on a G-code line is never the line alone. `X14.81` on line 23 of the badge is a rapid target in absolute millimetres; the same word two hundred lines later might be a cutting move in incremental mode. A UI could re-implement a light modal interpreter to resolve this — and that copy would drift from the real one, which is the exact failure mode this project refuses everywhere else. Instead, the parser gained an opt-in `recordModalState`: after every word-bearing line it records a `ModalSnapshot` (motion mode, distance mode, units, position, feed, spindle, tool, plane), plus a power-on snapshot at line 0. The snapshot *after* line N is the state carried *into* line N+1; a binary search (`modalStateAt`) resolves any line.

Two design details are worth naming. First, snapshots must record on **all** interpreter exit paths — dwell lines, modal-only lines like `G90 G21` or `T2 M6`, and motion lines; the first implementation recorded only the motion path and silently lost every mode-setting line. Second, the decode panel uses the before-line snapshot to resolve bare parameter words (units-aware) while the line's own words supply their explicit codes — so the panel never re-derives modal state, it reads the interpreter's.

## 7. The linking contracts, stated per direction

The page is two views of one artifact plus a dictionary, and each link has exactly one owner:

- **Playback → listing**: the viewport's throttled tick (12 Hz, never per animation frame) carries `gcodeLine`; the listing highlight goes through a CodeMirror `StateField` via a module handle — no React re-render on the hot path.
- **Listing click → 3D**: the click maps to a line number; the artifact's line→segment index (built once per decode) finds the segment; the viewport seeks to `segment.t0`.
- **Segment click / diagnostics click → both**: seek plus focus plus scroll-to-center.
- **Slider seek → focus**: the seek resolves its landing line with the same `sampleAt` the renderer uses, and dispatches focus itself.

The single-owner-per-direction rule is what made the sixth defect diagnosable (§8): when two paths both write `focusedLine`, clobbering has a name.

## 8. What live validation found that the test suite could not

Static validation passed first: typecheck clean, 294 tests green, production build with the chunk split as designed. The browser then found six defects, each now a recorded failure class with a receipt:

1. **A render-time handle capture is dead on first render.** The transport captured `getInspectorViewport()` during render; the instance is created in the mount *effect*, so the closure held `null` until an unrelated re-render — and none came. The play button did nothing while the UI looked correct. Fix: read the handle at event time.
2. **Child effects run before parent effects.** The DRO and the page's tick subscription are children of the viewport owner; their `[]`-keyed subscription effects ran before the instance existed. Fix: key subscription effects on `artifactId` — the commit that mounts the viewport child also re-runs them, after the child's own effects.
3. **A module handle plus lazy loading hides missing DOM.** The file input lived only in the decoded layout; the drop-zone hero's click went to a null ref. Found only because an automated `setInputFiles` timed out waiting for an element a human would assume was there.
4. **A duplicate import 500s a lazy chunk silently.** The page hung on the Suspense fallback; the only evidence was a console 500 and a vite log line. Lazy-loaded routes need their chunk errors visible.
5. **"The decoration exists" and "the user can see it" are different facts.** CodeMirror renders only the visible viewport. The playback highlight was applied correctly to a line 300 rendered rows below the fold and appeared broken. Fix: during playback the listing follows the active line (scroll-to-center); when paused it does not — a paused view must not steal the scroll position.
6. **A paused clock is not a quiescent system.** The viewport ticks its current line at ~12 Hz even when paused, and the slice let every tick overwrite `focusedLine` — so clicking line 23 to inspect it was clobbered back to line 342 within 80 ms. The root cause was conflation: one field carried two meanings ("where playback is" and "what the user is inspecting"). Fix: playing ticks own the field; every seek path sets it explicitly via `sampleAt`.

Two of these (1, 2) are the same lesson twice — module-level handles have an ordering contract with React's effect ordering, and `[]` is only correct for subscriptions whose subject already exists. That is now written into both handle modules' doc comments.

A seventh finding adjusted the test suite itself: the decode performance budget (`< 100 ms` warm) was set from browser measurements (34–62 ms) but the full-suite run contends for CPU with 24 other files and tripled the number. Timing assertions under contention are regression guards, not benchmarks; the budget now reflects that (1 s cold, 250 ms warm), with the browser receipts recorded alongside.

## 9. Status and recorded future work

Complete and live-validated on the badge: drop zone → decode (34–62 ms) → summary with the pinned numbers → play with tracking highlight, live DRO, and following listing → pause → click line 23 and have it stick → slider-seek to 50 % landing on the sampled line → G28 entry card showing the machine-specific homing notes with their sources. The ticket is closed. Recorded as future work, not scope creep: a `firmwareStatus` property per dictionary entry (live/source/dead/unhandled) so the UI can render "inert on this machine" explicitly; the two open firmware questions (M2/M02 handler location; M490 subcode mapping); and the deferred control-page preview (decode a file from the machine's SD client-side), which touches the machine-facing server and deserves its own ticket.

The pattern this report adds to the series: **evidence discipline does not end at the test suite.** The pipeline was provably correct before the browser opened, and the browser still found six wiring defects — because tests cover what components compute, and only live use covers what components are connected to.

> [!summary]
> - Build shared semantics as a package with a drift test against its consumers; page-local data guarantees eventual disagreement.
> - Prove the pipeline headlessly (CLI) before wiring it into a UI; the CLI and the page then assert against the same pinned fixture numbers.
> - "What the machine does" comes from the firmware dispatch, not the standard; on this firmware M30 deletes files, eight standard codes are inert, and accessory outputs are config-born.
> - Modal questions belong to the interpreter: record per-line snapshots from the state machine that owns the answer, never a UI-side reimplementation.
> - Module-level handles have an ordering contract with React: children's effects run first, so subscriptions to a parent-created handle must be keyed on the state that mounts it.
> - Virtualized renderers separate existence from visibility: a highlight feature needs a follow feature, or it only works when it happens to be on screen.
> - A paused animation clock still emits state; any field it feeds needs an explicit owner rule or it clobbers user intent at tick rate.
> - Timing budgets under test-suite contention are regression guards, not benchmarks; record the measured numbers separately from the assertion ceiling.

## Related notes

- [[Projects/2026/09/14/PROJ - Makera Z1 Control - P5 Qualification, Firmware Job Semantics and the G-code Decoder|PROJ — Makera Z1 Control: P5 Qualification, Firmware Job Semantics and the G-code Decoder]]
- [[Projects/2026/09/14/PROJ - Makera Z1 Control - Controller Ownership, Adapter Cutover and Hardware Qualification|PROJ — Makera Z1 Control: Controller Ownership, Adapter Cutover and Hardware Qualification]]
- [[Projects/2026/09/13/PROJ - Makera Z1 Control - P1 and P2 Protocol Ownership and Hardware Evidence|PROJ — Makera Z1 Control: P1 and P2 Protocol Ownership and Hardware Evidence]]
- [[Projects/2026/09/12/ARTICLE - Makera Z1 Stock Firmware - Source-Grounded Command and Telemetry Reference|ARTICLE — Makera Z1 Stock Firmware: Source-Grounded Command and Telemetry Reference]]
- [[Research/Software Architecture Garden/dropcut-studio/designs/09 - Single-Owner CNC Controller - Worker Ownership Separate from Operation Evidence|Garden 09 — Single-Owner CNC Controller]]
