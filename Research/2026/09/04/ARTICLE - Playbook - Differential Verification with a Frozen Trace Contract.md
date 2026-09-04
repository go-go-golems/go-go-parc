---
title: "Playbook - Differential Verification with a Frozen Trace Contract"
aliases:
  - Frozen Trace Contract Playbook
  - Differential CPU Verification Playbook
tags:
  - article
  - playbook
  - fpga
  - verilog
  - testing
  - differential-testing
  - reference-model
status: active
type: article
created: 2026-09-04
repo: /home/manuel/code/wesen/2026-09-04--gatemate-symbolic
---

# Playbook - Differential Verification with a Frozen Trace Contract

This playbook preserves the verification method used to build a tagged stack evaluator on an FPGA with open-source tools: one authoritative instruction table, one executable reference model, and a *frozen trace line format* printed identically by the model and by the RTL testbenches, compared line by line. The method turned every RTL bug in that project into a one-line diagnosis. It applies to any processor, VM, or state machine with a writable instruction set — CPUs on FPGAs, emulators, bytecode interpreters, protocol engines.

## Why this note exists

The failure modes this method prevents are boring and universal. Hand-copied instruction tables drift apart between the assembler, the model, the RTL, and the docs. Testbenches that eyeball "final state" miss everything about *how* the machine got there — ordering, faults, acceptance edges. And when model and RTL disagree, teams debug the RTL first, when the cheaper question is "which one is *right*?"

The core move is to make the reference model and the RTL produce the same output stream, then diff. Once that exists, adding a test is writing a program, not writing a testbench.

## Core mental model

Three artifacts, in dependency order:

1. **One instruction table** — a single source of truth (in the reference project, `tools/opcodes.py`): opcode values, mnemonic, immediate kind, stack effects, precondition counts, fault behavior. The assembler imports it. The model imports it. The RTL has a mirrored package, and a review step keeps them in sync. Four hand-copied tables is the failure mode; one table with mirrors is the fix.
2. **An executable reference model** — the abstract machine, directly transcribed: `M = <pc, stack, output, fault, halted>`, one `step()` per abstract transition, *all checks before any mutation*. The model is the specification. When model and RTL disagree, first decide which behavior is correct, then fix both sides — never "fix" the diff by editing one side blindly.
3. **A frozen trace line format** — every retired instruction, fault, or output acceptance emits exactly one line:

```text
TRACE <seq> <pc_old> <pc_new> <OP> <depth> <COMMIT|OUTPUT|FAULT> [extras]
TRACE 2 2 3 ADD 1 COMMIT
TRACE 7 7 8 EMIT 0 OUTPUT 1 00000001
TRACE 2 2 2 ADD 2 FAULT TYPE_FAULT 1 0
FINAL <halted> <fault_name> <pc> <depth> <outputs> <rdepth>
```

The model's `trace` list and the testbench's `$display`s print the same lines. "Frozen" means: changing a field is a versioned event that touches every printer at once — model, both testbenches, and every hardcoded expectation in the tests.

Two details that make the contract trustworthy:

- **Freeze the check order.** Capacity/underflow → operand tags → canonicality → branch target. A program failing two checks at once must produce the identical fault record on both sides, or the order leaks into the diff.
- **Put operand context in fault records.** The top-two stack tags (zero when absent) make `BAD_OPCODE` and underflow records meaningful — and force both sides to agree on *guarded* reads (stale cache registers must not leak into records).

## Implementation sequence

1. Table + model unit tests. The model must reproduce the spec's expected trace (a book table, a design doc table, or handwritten) *character for character* before anything else exists.
2. Assembler, round-trip tested against the table.
3. RTL testbench that prints the same lines. Give it a watchdog, a `TB_PASS`/`TB_FAIL` sentinel line, and a plusarg for the program image.
4. Directed differential test: assemble program → run model → run RTL → `assert lines == lines`. Use a real diff (unified, expected vs got) as the failure message.
5. Random program generator: maintain a typed software stack, emit only legal instructions, inject one illegal instruction occasionally (mixed-type operand, underflow, bad opcode). Deterministic per seed.
6. Random backpressure on the output channel: backpressure changes timing, never the trace. If it changes the trace, the commit boundary is wrong.

## Common failure modes the method caught

- Three hand-written test programs were wrong (wrong `JZ` polarity, `INT` fed to a Boolean-only branch, a raw word encoded as value instead of opcode-shifted) — all caught by the model before RTL existed.
- The RTL testbenches' mnemonic table lacked new opcodes, so *correct* execution printed `BAD` as the op name — caught as a one-line trace diff.
- Fault-record operand tags disagreed between model (hardcoded zeros) and RTL (real top-of-stack tags) — caught only by the random suite, on `BAD_OPCODE` records.
- A stale compiled simulator (`.vvp`) produced phantom failures after a source fix. Recompile before you debug.
- Unqualified package references after a portability pass silently elaborated as implicit wires; the case never matched and the machine faulted `BAD_OPCODE` at exactly the new instruction. One test run localized it.

## Working rules

- The model is the specification; the RTL is an implementation. Disagreements are resolved by deciding correct behavior first.
- Never widen or reformat a trace line as a side effect of another change. Plan it, touch every printer, update every expectation.
- Random tests must be seedable and fast enough to run on every commit.
- When adding an instruction, the checklist is mechanical (see the source repo's playbook): table, model, package, cores, both testbench mnemonic tables, assembler comes free, programs, tests.
- Direct state construction in the model is legitimate: some fault cases are unreachable through legal programs (canonicality violations, deep arithmetic overflow) and must be reached by building machine states directly — the RTL must still match them.
