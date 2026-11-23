---
title: "Restructuring the PicoCalc OS around Typed applications: app manifests, one Typed-world path and no app-specific C"
aliases:
  - PicoCalc Typed-first, milestone 4
  - PicoCalc app manifests and Typed Agenda and Files
tags: [project, picocalc, operating-system, esp32-p4, refactoring, typed]
type: project
status: active
created: 2026-11-22
repo: /home/manuel/code/wesen/2026-10-20--ds-js-os
ticket: PICOCALC-TYPED-FIRST
source_revision: 06e8d55
---

# Restructuring the PicoCalc OS around Typed applications

The PicoCalc's operating system runs every driver, service and application as a *world*: an isolated QuickJS runtime with its own heap limit, turn budget and authority. Since mid-November some worlds have instead been *Typed worlds*. Their source is Typed, a typed subset of JavaScript, which the handheld's ESP32-P4 compiles to RV32 machine code at boot and loads as a native world. The project's goal, stated in `AGENTS.md` on 22 November, is an operating system whose code is Typed, with QuickJS as a fallback and C only where it cannot be avoided.

At the start of the day the firmware fell short of that goal in three ways. The P4 port contained a C file per Typed app. Two of the four boot apps kept their logic in app-specific C. And the repository had long files nobody wanted to touch. This report describes three tickets of the PICOCALC-TYPED-FIRST program that removed those problems — PICOCALC-TYPED-APP-MANIFEST, PICOCALC-AGENDA-TYPED-WORLD and PICOCALC-SPLIT-FILES — and the price the second one paid in boot time.

> [!summary]
> - **One compile path driven by data.** Each Typed app is described by `apps/typed/NAME/app.json`. A build-time generator turns the manifests into a C table, and one function in the port compiles every app. The per-app C files are gone, the P4 `CMakeLists.txt` went from 611 to 96 lines, and a failed compile now falls back to the app's JavaScript version instead of stopping the boot.
> - **No app-specific C.** Agenda (869 lines of C) and Files (334 lines) are now complete Typed worlds on the same generic world module as Editor and Chess. They are checked frame by frame and edit by edit against the JavaScript apps, and their RV32 and WebAssembly builds must produce identical system-call transcripts.
> - **The price is boot time.** Agenda's boot compile went from 0.71 s to 2.52 s and Files' from 0.47 s to 1.39 s. Because every app's first frame waits for all boot compiles, the whole boot got about 2.8 s slower. This is now the program's leading open problem.
> - **Smaller files, checked.** The nucleus, the trace REPL and Candela's translator were split by checked scripts. `make test` now fails on any new source file over 500 lines unless it is on a reasoned exception list.

## 1. How a Typed app reaches the screen

A Typed app is compiled on the handheld every boot. The world manifest (`system.json`) names a file such as `editor/compiled.bin`. When the kernel reads that file, the port intercepts the read, compiles the app's Typed sources against a prebuilt *reactor* (a C module implementing the world interface), and returns an ELF that the firmware's loader relocates into a native world. If the compile fails or misses its deadline, the system runs a JavaScript version of the app instead.

Before APP-MANIFEST, each app's part in that process was C in the port. Here is a real example of the duplication, from two of those files:

```c
// chess_p4.c
static const p4_compile_limits limits = {.heap_bytes = 4 * 1024 * 1024, .duration_us = 6000000, .policy = "balanced"};
// editor_p4.c
static const p4_compile_limits limits = {.heap_bytes = 4 * 1024 * 1024, .duration_us = 6000000, .policy = "interactive"};
```

Around them were per-app source lists, per-app CMake blocks and 74 `PICOCALC_` build flags. A firmware profile was a list of those flags. Adding a Typed app meant writing C in four places.

## 2. App manifests

Each Typed app is now described by a manifest. Editor's, in full:

```json
{
  "name": "editor",
  "kind": "world",
  "sources": ["state.typed", "layout.typed", "empty.typed", "markdown.typed", "view.typed", "find.typed",
              "preview.typed", "document-view.typed", "positions.typed", "edit.typed", "editor.typed"],
  "link": "compiler/typed/typed-world.js",
  "entry": "compileTypedWorldRv32",
  "compiler": ["typed/async.js"],
  "reactor": {"sources": ["firmware/sdk/typed/world.c", "firmware/sdk/typed/chess-psix.c",
                          "firmware/sdk/typed/rv32-slot.S", "firmware/third_party/quickjs/libunicode.c",
                          "firmware/sdk/nw_elf.c"]},
  "policy": "interactive",
  "heapBytes": 4194304,
  "deadlineMs": 6000,
  "world": {"replaces": "editor", "budget_ms": 200, "mem_kb": 768},
  "fallback": true
}
```

The fields say, in order:
- which sources are concatenated in which order;
- which linker assembles the world;
- which extra compiler modules it needs (Editor uses `async`/`await`);
- which C files build its reactor ELF;
- the code-generation policy, heap cap and deadline for its boot compile;
- which `system.json` entry it replaces;
- whether a JavaScript fallback exists.

Two design decisions follow from the device:

- **The manifests are not parsed on the handheld.** `firmware/port/esp32p4/typed_apps.py` reads them at configure time and writes four things: the assembled sources, a C table (`typed_apps.c`), the boot manifest `system.typed.json`, and a CMake fragment. The port compiles from the table. JSON parsing at boot would cost time and memory for information that is fixed when the firmware is built.
- **Profiles list apps, not flags.** The playable profile is now:

  ```sh
  APPS=(chess agenda editor files candela raytrace)
  OPTIONS=(PICOCALC_DEVICE_COMPILER=ON PICOCALC_CANDELA_GALLERY=ON)
  ```

One function, `p4_typed_app_compile`, serves every app. The painter that Chess delivers to the compositor, the Candela scene and the Typed ray tracer compile through the same call. The console gained `typed`, which lists the apps, and `typed WORLD baseline|build`. Benchmarks that only studies use moved out of the shipping firmware into `bench/board/firmware/`, built only by a `bench` profile.

**The fallback moved into the kernel.** A manifest entry may now carry `"fallback": "apps/x.js"`. When a world's compiled file cannot be produced, the kernel runs that JavaScript world instead:

```c
if (!W->source && mw->fallback[0]) {
    // A compiled world whose compile failed (the P4's Typed apps): its JavaScript version runs instead.
    klog("%s: %s is unavailable; running %s", W->name, W->file, mw->fallback);
    snprintf(W->file, sizeof W->file, "%s", mw->fallback);
    W->engine = ENG_JS;
    ...
}
```

Before this, a failed Editor, Files or Chess compile stopped the whole boot. Chess still has no JavaScript version, so it still has no fallback.

**Verification.** Every bundled source and reactor ELF was byte-identical to the previous playable build under its new name: 51 files the same, 14 renamed, none changed. On the board, every boot compile stayed within 75 % of its deadline with identical module bytes. The ray tracer's four scenes gave identical screen-capture checksums, and the gallery's 18 path-traced scenes matched their reference digests.

## 3. Agenda and Files without app-specific C

Editor and Chess were already complete Typed worlds. Their whole logic is Typed, linked against the generic world module (`firmware/sdk/typed/world.c`) through `compiler/typed/typed-world.js`, which declares two entry points and the platform calls a world may make. Agenda and Files were not: only their compute functions were Typed, and their event handling, screens and file logic lived in app-specific C reactors.

PICOCALC-AGENDA-TYPED-WORLD moved all of it:

| App | Was C | Now Typed |
|---|---|---|
| Agenda | `wasm-world.c`, 869 lines: reading and indexing the task file, grouping, the 25-row window, prompts and diagnostics, add/edit/toggle/delete, reminders and their persisted "fired" store, handing the file to Editor | nine sources, 71 KB |
| Files | `world.c`, 334 lines: listing (including a JSON scanner), sorting, sizes, prompts, mkdir/rename/remove, opening a file in Editor | five sources, 38 KB |

A checked script deleted ten files: both apps' reactors, slot files and adapters. What remains in C is the platform: nine new calls in the generic world module that any Typed world may use (opening and walking a directory handle, file operations, asking another world to take a file, revoking a handle, the wall clock and time zone), and a timer a world declares in its metadata.

Typed's limits shaped the port. Typed has no local records, so the task parser writes its fields into the world's state record rather than returning a structure. Agenda now handles at most 12,000 tasks and files up to 65,536 UTF-16 units. These limits are recorded in the ticket, with "local records" and "sources shared between apps" filed as compiler requests.

**Three kinds of oracle check the port:**

1. **The JavaScript apps.** `agenda-wasm-world.mjs` compares the Typed Agenda with the JavaScript Agenda: 14 grouped frames and 4 done-only frames identical, 6 file edits byte-exact, 6 diagnostics exact, plus the midnight regroup, the editor capability rules, reminders with persistence and a daylight-saving transition. Files matches the JavaScript Files on 26 frames.
2. **The two targets.** `agenda-rv32.mjs` and `files-rv32.mjs` run the RV32 ELF on an emulator and the WebAssembly build against one scripted kernel. They require byte-identical system-call transcripts: 137 calls for Agenda, 57 for Files.
3. **The device.** Driven by console key injection on the P4:
   - adding a task, editing its time from 09:00 to 11:30, ticking it, and handing `notes/todo.txt` to Editor worked;
   - browsing to `/notes` in Files and opening the file in Editor worked;
   - a reminder could not ring because the device's wall clock was unset, so reminders are covered on the host only.

The host replay count went from 24 to 25.

## 4. The price: boot time

Moving the logic into Typed moved its cost into the boot compile. A paired board comparison (three boots each):

| App | Compile before | Compile after | New deadline | Share of deadline |
|---|---:|---:|---:|---:|
| Agenda | 0.709 s | 2.516 s | 4.0 s | 63 % |
| Files | 0.472 s | 1.391 s | 3.0 s | 46 % |
| Editor | 3.247 s | 3.239 s | 6.0 s | 54 % |
| Chess | 3.987 s | 3.968 s | 6.0 s | 66 % |

The deadlines for Agenda and Files were raised from 1.7 s to 4.0 s and 3.0 s. All four apps run natively, with no fallback.

The effect on the user is larger than the compile times suggest. Every app's first frame waits for all boot compiles, so Agenda's first frame arrived about 2.8 s later than before. The measurement used the kernel's trace of the first `frames` post from Agenda: median 16.26 s before, 19.07 s after. The trace itself slows the boot, so these are paired values, not absolute latencies. The earlier target of 1.897 s from cold boot to Agenda's first frame came from an image with an early-boot priority for Agenda, which APP-MANIFEST removed because it was a measurement aid. No current image could meet it.

The decision was to accept the cost and make it the next problem to solve. The goal says Typed first, and the per-pass timings from the compiler work show where boot compiles spend their time: in the front end, the location planner and the emitter, not in optimization passes. The obvious remedies are:
- **A module cache.** Compile once, keep the image in flash keyed by its source digest and policy, and reuse it at the next boot. This is NATIVE-NEXT's scope B.
- **Not blocking first frames on all compiles.**

## 5. Long files, split and checked

PICOCALC-SPLIT-FILES split the long files that no other ticket was rewriting. Each split was a checked script: it asserted that every line landed exactly once, applied edits with asserted counts, and had dry-run and revert modes.

| File | Lines | Became |
|---|---:|---|
| trace REPL `query.js` | 2,545 | nine files sharing one scope, joined by the Go embed |
| `nucleus/vm.c` | 1,266 | `vm.c`, `vm_ops.c`, `vm_sys.c`, a private header |
| `nucleus/kernel.c` | 1,117 | scheduling, channels, supervision, reports, a private header |
| `nucleus/vm_mqjs.c` | 1,039 | runtime, operations, graphics |
| `nucleus/native.c` | 836 | engine core, JSON, device calls |
| Candela translator `lower.js` | 914 | state, expressions, statements as a chain of classes |
| trace REPL `main.go` and three packages | 511–701 | one file per command or responsibility |

The leftover moves of the earlier repository reorganization also landed:
- the trace REPL moved to `tools/trace-repl/`;
- the firmware's tests moved to `tests/apps/` and `tests/native/`;
- the device scripts moved to `tools/device/`.

The tour screenshots stayed byte-identical through every split. The one exception was a Settings help line that names the moved provisioning script.

Two files were deliberately not split. A QuickJS world loads one file, so the two `compositor.js` files and `agent.js` stayed whole. Splitting them would need either a bundler, whose output is an equally long file, or a manifest entry that names several files.

**The check keeps files short.** `tools/check-file-length.mjs`, run by `make test`, fails on any tracked source file over 500 lines unless `tools/file-length-exceptions.txt` lists it with a reason: vendored, generated, the book compiler cji, or the ticket that will split it. It also fails on an exception that is no longer needed, so entries come off when their ticket lands. During the program, the entries for `emu.c`, the P4 `CMakeLists.txt`, Agenda's `wasm-world.c` and the split RV32 sources came off this way as their tickets landed.

## 6. What coordinating this showed

These three tickets ran in parallel with the compiler tickets, each built by an agent in its own git worktree and merged by a coordinator. Three coordination problems are worth recording.

- **Merges across a moving tree.** APP-MANIFEST's merge had six conflicts, mostly with SPLIT-FILES, which had moved the kernel's boot section into `kernel_supervision.c`. APP-MANIFEST's fallback had to be carried into the new file by hand. A test from the tape ticket read per-app `source.list` files that APP-MANIFEST had replaced with manifests. The gate (`make test` and the host gates after every merge) found both.
- **Stale state in worktrees.** One agent finished its board session by restoring "the playable firmware". Its branch's copy of `firmware/PLAYABLE.json` named an older image, so it overwrote a newer install. A probe that compares the board with the record found the mismatch, and restores now run from the main checkout.
- **The device has moods.** Midway through the day the keyboard controller stopped answering on I2C, on old images too. The cause was the known hang after resets of only the ESP32, not a firmware bug; a person cleared it by resetting the keyboard. Later the screen appeared black. That was a power-key press during testing, which turns off the backlight; the firmware has no screen-off timer. In both cases the right first step was to read the bus statistics (I2C errors, SPI transfer counts) before suspecting the software.

## 7. Open problems

- **Boot latency.** Agenda's and Files' larger compiles delay every first frame. Candidate fixes are a flash module cache keyed by source digest and policy, and first frames that do not wait for every compile.
- **Typed language gaps the port exposed:** local records, or a record view of a buffer, and Typed sources shared between apps.
- **Chess has no JavaScript fallback.**
- **QuickJS worlds are single files,** which blocks splitting the compositor and the agent world.
- **The PaperS3 builds** still fail to link, as they did before this work.

## Related notes

- [[PROJECT REPORT - PicoCalc Compiler - One Tape, a Target-Neutral Front End, Declared Passes and Register Classes - Refactoring the Typed Compiler for Floats - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc - An Operating System That Compiles Its Own Applications - The Whole Project, Its Repository and What It Taught - A Technical Deep Dive]]
- [[PROJECT REPORT - picocalc-os - Worlds, Turns, Handles and Frames - A Technical Deep Dive]]
- Tickets: `ttmp/2026/11/22/PICOCALC-TYPED-APP-MANIFEST--*`, `ttmp/2026/11/19/PICOCALC-AGENDA-TYPED-WORLD--*` (design-doc 02 and diary 02), `ttmp/2026/11/22/PICOCALC-SPLIT-FILES--*`, and the program diary in `ttmp/2026/11/22/PICOCALC-TYPED-FIRST--*`.
