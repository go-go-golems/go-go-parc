---
title: "Playbook - The yosys and iverilog SystemVerilog Subset"
aliases:
  - yosys iverilog Subset Playbook
  - OSS CAD Suite SV Portability Rules
tags:
  - article
  - playbook
  - fpga
  - verilog
  - yosys
  - iverilog
  - toolchain
status: active
type: article
created: 2026-09-04
repo: /home/manuel/code/wesen/2026-09-04--gatemate-symbolic
---

# Playbook - The yosys and iverilog SystemVerilog Subset

Projects using the OSS CAD Suite need iverilog for simulation and yosys for synthesis. Their SystemVerilog acceptance is not identical, and neither warns helpfully when it disagrees: yosys fails at parse or elaboration with terse errors, and iverilog accepts constructs yosys rejects — or vice versa — with only a note. The fix is a project rule: **write in the intersection only.** This playbook lists the exclusions found in practice and the portable replacement for each, so the next project pays the cost once.

## The subset, as rules

| Rejected construct | Rejected by | Portable replacement |
|---|---|---|
| `return` in functions | yosys | Classic function-name assignment: `mk_int = v;` |
| `import pkg::*;` (file-scope or module-header form) | yosys | Fully-qualified references everywhere: `pkg::TAG_INT` |
| Multiple declarators of a typedef'd type (`value40_t a, b;`) | yosys | One declaration per line |
| `parameter string` | yosys | Plain parameters; strings via macro files |
| `-DNAME='"file"'` string defines on the command line | yosys (mangles) | A `.ys` script file; yosys's own tokenizer handles the quoted filename |
| Enum-typed struct fields used in package functions | yosys (width inference fails) | Plain `logic [3:0]` field; keep the enum as documentation |
| String-typed ternary in `$display` | iverilog | Assign to a local `string` with `if`/`else` |
| Enum values in ternary state assignments | iverilog | `if`/`else` state assignment |

Notes on two of these:

- The qualification pass (rewriting bare package identifiers into `pkg::name`) is a mechanical, word-boundary regex over a fixed name list. It is safe because the names are uppercase constants and typedefs that do not collide with port names — but run the full test suite immediately after it.
- `iverilog` prints `sorry: constant selects in always_* processes...` notes for part-selects in `always_comb`. These are informational sensitivity-list approximations, not errors. Filter them; do not "fix" working code because of them.

## The process rule that matters more than the table

When applying scripted edits to RTL (regex replacements, sed patches), **every patch must assert its match count and be verified by grep before the work counts as done.** In the source project, three patches silently no-oped — comments had been rewritten by an earlier pass, whitespace differed — while printing success. The symptom was precise: the machine executed one instruction and then faulted `BAD_OPCODE` at the new opcode, because an unqualified `OP_CALL:` case label elaborates as an implicit wire that never matches. The differential suite caught all three in a single run; the rule exists so the next project does not need the suite to find a text-editing failure.

A symptom → cause quick table for this class:

| Symptom | Likely cause |
|---|---|
| `BAD_OPCODE` at exactly the newly added instruction | Unqualified case label, or the case insert never applied |
| All trace fields print `x` | Declared but never-assigned snapshot registers (registered the pulse, forgot the payload) |
| Parse error `unexpected TOK_IMPORT` | `import` left inside or before a module |
| `This assignment requires an explicit cast` | Enum-typed ternary |
| Works in simulation, wrong in synthesis | Combinational read of a behavioral array standing in for sync RAM |
| Correct execution, wrong mnemonic in traces | Testbench opcode-name table not extended |

## Working rules

- Compile with both tools in CI from the first day; the intersection only shrinks if you discover drift late.
- Prefer flat vectors at module ports; convert to packed structs inside the module body.
- Keep one file that lists every package-defined name; any tooling that rewrites references uses that list, never a broad regex.
- After any scripted edit: recompile, rerun the suite, and grep the edited region before believing the edit happened.
