---
title: "PicoCalc Agenda — Normalizing typed task entry"
tags: [project, picocalc, compilers, wasm, riscv]
status: active
type: project
created: 2026-11-18
---

# PicoCalc Agenda — Normalizing typed task entry

The original Agenda accepts `dentist @tue 2pm !15m` and resolves the date against the device's local calendar before saving the task. The typed reminder viewer could already read the saved line. The new typed task-entry operation performs the earlier normalization step, giving the full port the same text to store.

## Separate the prompt from its I/O

The normalizer takes the prompt as a UTF-16 string, the local civil date as an integer, and a writable output buffer. The current date enters as data, so tests can reproduce a weekday calculation without changing the hardware clock. One scan obtains word boundaries using Agenda's existing whitespace rule. Date and time helpers read spans of that input. They can distinguish an ordinary word following a date from a time-shaped word that is numerically invalid. The original app leaves the former in the title and reports the latter as an error.

The operation copies ordinary words and formats accepted dates and times in the stored form. It also preserves lead tokens and the original content check, which removes the first date and lead when deciding whether a title remains. The return value is either the output length or a diagnostic category. Each write checks the caller's capacity. The runtime can ignore the output on failure and keep the edit prompt open.

```text
prompt and civil today
    scan words and resolve date and time
    format the normalized text and validate required title
    return a length or a diagnostic category
```

## Verify the same decisions on both targets

The test loads the original JavaScript implementation as its oracle. The emitted Wasm functions run in a host WebAssembly instance, and the emitted machine words run in the repository's RV32 instruction emulator. Both agree across 3,924 isolated token cases and 292 complete prompts, including unset clocks, leap dates, malformed tokens, Unicode whitespace, duplicate dates, and output capacity boundaries. The fixture compares every successful output code unit and checks the error class on invalid inputs.

This checkpoint exercises a pure typed operation. Wiring that operation into Agenda requires the reactor interface, the keyboard edit state, and capability-scoped file writes. The compiled reminder and entry functions together emit 30,388 bytes of RV32 instructions. That exceeds the current native reactor's 16 KiB reserved region. The feature-parity design records the packaging step separately from the typed language rules, the compiler heap and the world memory limit.

The design is in project commit `8da5247`, and commit `68f91fa` contains the operation and its reproducible cross-target tests. The next comparison at the whole-app boundary will need to cover file bytes, view state, clock-driven notifications and Editor capability transfer through the real kernel.
