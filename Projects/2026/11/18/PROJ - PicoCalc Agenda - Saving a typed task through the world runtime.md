---
title: "PicoCalc Agenda — Saving a typed task through the world runtime"
tags: [project, picocalc, wasm, riscv, compilers]
status: active
type: project
created: 2026-11-18
---

# PicoCalc Agenda — Saving a typed task through the world runtime

The first typed Agenda read saved reminder lines. It now accepts a keyboard prompt, normalizes the entry, writes it through the notes capability, and refreshes the view after the write succeeds. This moves the verified boundary from a pure parsing operation to a state change in the real simulator filesystem.

## One edit and two asynchronous results

The compositor forwards F2 and the subsequent keys to the focused Agenda world. Enter calls the generated `normalizeEntry` function with the prompt and the local civil date. The SDK resolves that date from the configured wall clock. A diagnostic leaves the prompt open. A valid result becomes a pending edit, and the reactor requests a fresh read of `notes/todo.txt`.

The matching read settlement contains the file text. The reactor preserves those bytes, adds a newline separator when the previous last line lacks one, and appends the normalized checkbox line. The SDK checks that the world holds write access to the file through its existing notes capability. Only the matching successful write settlement closes the prompt and schedules a fresh read. Earlier read tokens are discarded so an older snapshot cannot publish after the edit.

```text
F2 and keyboard text
    -> normalize the prompt
    -> read the latest notes
    -> write the updated notes through the capability
    -> reload the file and publish
```

## Retaining direct calls on both targets

The reactor has two call sites for generated code. The Wasm linker appends the typed functions once and rewrites separate bridge bodies for `parseTask` and `normalizeEntry`. The RV32 template has two entry jumps and declares its reserved executable size in a header. The linker writes the compiled code once and patches both jumps to the corresponding entry addresses. Both compile routes check source-level signatures and the parser's task-record layout before returning a module. The updated RV32 template reserves 48 KiB, of which the current typed instructions need 30,388 bytes.

## What has been validated

The Wasm simulator test typed a relative date, a time and a reminder lead, then checked the exact bytes in a real temporary notes directory. It also checked that an invalid prompt leaves the file unchanged and that the first task creates a missing file. The native ELF test executed the generated RV32 instructions and checked the exact write request and refreshed state, using deterministic filesystem and clock stubs.

On the powered PicoCalc, the new native module measured 59,528 bytes. A single full boot published in 3.277 seconds. An editable rebuild in that same session published in 2.158 seconds. The compiler allocator peaked at about 695 KB, and Agenda's world counter was 160,328 bytes. These are startup and rebuild measurements using the existing device notes. The task write was exercised in simulation and emulation. The timings still leave a two-second performance gap on the assembled firmware, and physical keypress-to-LCD latency requires its own capture.

Commit `00f27ba` contains the implementation and both integration receipts. The parity ticket records the remaining task editing, grouping, and Editor handoff requirements.
