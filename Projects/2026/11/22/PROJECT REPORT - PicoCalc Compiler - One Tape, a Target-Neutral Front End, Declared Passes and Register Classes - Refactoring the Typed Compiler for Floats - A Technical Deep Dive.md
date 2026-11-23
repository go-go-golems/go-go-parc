---
title: "Refactoring the Typed compiler for floats: one tape, a target-neutral front end, declared passes and register classes"
aliases:
  - PicoCalc Typed-first, milestone 1
  - The Typed compiler's new architecture
tags: [project, compiler, picocalc, riscv, refactoring, measurement]
type: project
status: active
created: 2026-11-22
repo: /home/manuel/code/wesen/2026-10-20--ds-js-os
ticket: PICOCALC-TYPED-FIRST
source_revision: 5784a35
---

# Refactoring the Typed compiler for floats

The PicoCalc's operating system compiles its own applications. A compiler written in JavaScript, the *Typed compiler*, runs inside QuickJS on the handheld's ESP32-P4 and turns Typed, a typed subset of JavaScript, into RV32 machine code at boot. On 22 November the project's goal was written down in its `AGENTS.md`: the operating system's code should be Typed, with QuickJS only as a fallback and C only where it cannot be avoided or as a benchmark. The first large workload that goal implies is Candela, a physically based path tracer whose kernel is single-precision floating point throughout. Typed had no floating-point type.

Adding one touches every layer of the compiler. Before doing that, the program PICOCALC-TYPED-FIRST restructured the compiler so that a new value type would be one addition in each place rather than a search through scattered conventions. This report describes that restructuring: six tickets, each built by a separate agent in its own git worktree, each gated on byte-identical output, merged in about one working day. It explains what each change is, why it was needed, how it was verified, and what the measurements showed, including two results that went against the plan.

> [!summary]
> - **One tape definition.** The compiler's intermediate representation, a flat array of numbers per function, is now defined once in `compiler/typed/tape.js` with names, operand cells, value types and effect bits. Before, its opcodes were raw hex in at least six places.
> - **A target-neutral front end.** The parser emits only the tape. WebAssembly became a backend that serializes it, so the WebAssembly oracle now checks the same representation the RV32 backend consumes.
> - **A declared pass pipeline.** RV32 passes are registered objects, policies are lists of pass names, every pass is timed, and two pass groups load only when a policy needs them. Boot compiles use 122–157 KB less heap and take 15–96 ms longer on the P4, for a reason not yet found.
> - **Register classes and one instruction table.** Integer and float registers are two classes the planner allocates separately, and 85 instruction encodings live in one table checked against GNU `as`.
> - Every one of these changes left all compiled images byte-identical. The one ticket whose idea did not survive its own study (lowering `async` on the tape) is reported as such.

## 1. What the compiler looked like

The compiler has two targets. WebAssembly runs in WAMR, an isolated interpreter, and serves as an independent reference. RV32 is native code that the firmware's ELF loader relocates into a world. A review of the source at the start of the program found the structure below.

```
Typed source
  ├─ typed-async.js (1,182 lines)  only if async/await appears: its own scanner, parser and liveness;
  │                                rewrites async functions into ordinary Typed source text
  ▼
typed-wasm.js (1,667)              lexer → signatures → FunctionEmitter: parser, type checker and emitter
  │                                in one class; no syntax tree; one function at a time
  ├─ Wasm mode     → Wasm bytes
  └─ numeric mode  → the tape
  ▼  streamed: each function is lowered as soon as it is parsed
typed-rv32.js (2,992, built from 13 files): tape passes, location planning, emission, linking
```

Two properties of this design are deliberate and were kept. Compilation streams one function at a time and frees each function's tape after lowering it, which bounds memory on a device whose compiler runs under a 2–4 MiB cap. And there is no syntax tree: the parser checks types while it parses and writes operations directly, so compile cost is proportional to source length.

The problems were in how the pieces knew about each other.

| | Finding | Consequence |
|---|---|---|
| A | The tape had no definition. Opcodes were raw hex in the front end, the RV32 passes, the PIE pass, the inspector and the tests. | A new operation meant finding every place that matched opcodes by number. |
| B | The two targets were two emission modes of one 700-line class. | The WebAssembly oracle exercised a different emission path from the one RV32 consumed. |
| C | `async` had a second parser that produced text, which was lexed again; errors were located by compiling the text a second time. | Two parsers of one language and a fragile error path. |
| D | The RV32 passes ran inside one closure gated by about fifteen flags. | No per-pass timing; every policy loaded every pass. |
| F | Registers were integers 0–31 everywhere. | Floats need a second register file. |

## 2. The tape, defined once

The *tape* is the compiler's intermediate representation. Each operation is a WebAssembly opcode followed by its operands as plain numbers rather than LEB128 bytes, plus three pseudo-operations for UTF-16 text buffers: `0xf1` (a checked address), `0xf2` (checked literal stores) and `0xf3` (an unchecked address that loop versioning writes after proving bounds).

A concrete example. This function:

```js
function clampAdd(a: i32, b: i32, limit: i32): i32 {
    const s = a + b;
    if (s > limit) { return limit; }
    return s & 0xff;
}
```

has this tape (cells, then their meaning):

```
32 0        local.get a
32 1        local.get b
106         i32.add
33 3        local.set s        (local 3: parameters are 0–2)
32 3        local.get s
32 2        local.get limit
74          i32.gt_s
4 64        if (no result)
32 2          local.get limit
15            return
11          end
32 3        local.get s
65 255      i32.const 255
113         i32.and
11          end
```

The RV32 backend under the `interactive` policy turns it into 18 instructions.

`compiler/typed/tape.js` now holds one row per opcode: a constant name, an operation name, operand formats, the value types it pops and pushes, and a set of effect bits (`STORES`, `LOADS`, `CALLS`, `BRANCHES`, `TRAPS`, `CONTROL`). The passes test effects instead of opcode lists. For example, the analysis that decides whether a function stores to memory became `EFFECTS[op] & STORES`. The passes still walk raw cells rather than decoding the tape into objects, because decoding allocated several objects per operation and cost a quarter of a compile in bare QuickJS. `decode` exists for tools and tests only.

The ticket's agent found one bug the design would have introduced. The design named the effect bits in the singular, so `CALL = 4` (an effect) and `CALL = 0x10` (the opcode) shared a name. When both were destructured into the same scope, the later definition won, and every function call compiled as an `if`. The table now refuses any name defined twice. A test walks the 4,184 tapes produced by compiling all Typed applications under two policies, with a typed operand-stack check against the table's pop and push columns.

## 3. A target-neutral front end

With the tape defined, the WebAssembly target could become a consumer of it. The parser now always writes the tape. A new backend, `wasm/encode.js`, serializes each function's tape: operand cells become LEB128 (signed only for `i32.const`), and the pseudo-operations expand to exactly the bounds-check and store sequences the old WebAssembly mode wrote.

`typed-wasm.js` was split into ten modules under `frontend/` (lexer, declarations, expressions, statements, compile, inspection) and `wasm/` (encode, module, inspection, link). The longest is 409 lines. The firmware and every other loader still read one script: `frontend/build.mjs` concatenates the modules, and `make test-generated` checks that the bundle is current.

The gate was byte identity: 123 digests covering RV32 images and observed tapes under six policies, the standalone WebAssembly modules, the five linked WebAssembly worlds, and every inspection event stream. All 123 matched. A deliberate one-constant change to the serializer changed 8 digests, which shows that the harness detects differences.

The memory measurement carried a lesson of its own. A single deterministic run showed the RV32 compile's peak heap 1.6 % higher after the change. Adding one comment line to the *old* compiler moved its peak by 0.5 %. The difference was where QuickJS's cycle collector happened to run, not more live data. The harness was changed to count requested bytes and to sweep the collector's phase. Measured that way, the Editor's RV32 compile was 0.7 % faster with 0.2 % less peak.

## 4. Async: a study that came back negative

The design proposed lowering `async`/`await` inside the front end and as a tape transformation, removing the second parser. The ticket was told to study that first and implement it only if it was sound and not slower. The study concluded it was not worth doing, for four reasons:

- **The layout cannot improve.** Editor's async state is already minimal: 57 declared fields plus 13 lowered ones, each saved scalar read after its wait. Since compiled images could change only if the layout improved, a tape pass would have had to reproduce today's output exactly.
- **A tape pass would not be simpler.** The tape is structured like WebAssembly, so resuming in the middle of a loop means rebuilding the control tree and emitting a dispatch loop. That is the statement skeleton the current code already builds. It would also need variable names, which error messages and the layout require and the tape does not carry.
- **Streaming still needs a pre-pass.** Which generated functions exist and their indices depend on async bodies that may appear later in the source.
- **Text generation is cheap.** It was 57.1 of 906.8 ms in earlier on-device measurements.

The ticket delivered what remained useful. `typed-async.js` is now built from eight modules under `compiler/typed/async/`. Errors inside rewritten code are mapped to source positions by a `catch` around each lowered function, so the second compile is gone. A new test checks 18 diagnostics exactly on both targets.

## 5. A declared pass pipeline

The RV32 backend's passes became registered objects, `{name, run, enabled}`. A policy is now a list of pass names plus the parameters of the stages that are not passes (the location planner and instruction selection):

```js
const DEFAULT_POLICY = {
    passes: ["inline", "commute", "rotate", "version", "split"],
    inlineGuardedReturns: true,
    operandLocations: DEFAULT_LOCATIONS,
    select: DEFAULT_SELECT,
};
// interactive: passes: []     balanced: ["inline", "commute", "rotate"]
```

The pipeline wraps every pass with the same observation hook and timer. The first use of the timers was to see where a compile's time goes. Times are in milliseconds, median of 7 compiles, in bare QuickJS on the workstation.

| Workload, policy | front end | inline | commute | rotate | version | split | plan | emit | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Agenda, interactive | 6.3 | | | | | | 1.5 | 4.5 | 12.5 |
| Editor, interactive | 35.3 | | | | | | 6.5 | 18.3 | 60.4 |
| Files, default | 1.2 | 0.3 | 0.3 | 0.2 | 0.9 | 0.4 | 1.1 | 1.7 | 6.3 |
| Chess, balanced | 20.3 | 8.2 | 3.3 | 2.4 | | | 12.3 | 20.5 | 69.4 |
| Ray tracer, kernel | 4.5 | 1.4 | 0.9 | 0.7 | 7.7 | 1.9 | 7.2 | 5.9 | 36.3 |

At boot, the front end, location planning and emission dominate every compile. The `interactive` policy, which Agenda and Editor use, runs no tape pass at all. Optimization work on boot compiles should therefore target the front end and the planner, not the passes.

The thirteen backend files became ES modules in directories (`encoding/`, `emit/`, `passes/`, `analysis/`, `plan/`). `build.mjs` bundles them into three scripts: a core, an inline group and a loop group. The P4 loads a group only when the policy of the app being compiled needs it, through a loader the firmware defines over its compiler bytecode cache.

The board measured the effect in a paired study (three blocks, alternating order):

| App, policy | Compile, control → candidate | Peak heap |
|---|---|---|
| Agenda, interactive | 0.700 → 0.715 s | −149 KB |
| Editor, interactive | 3.219 → 3.237 s | −157 KB |
| Files, default | 0.447 → 0.471 s | +34 KB |
| Chess, balanced | 3.920 → 4.016 s | −122 KB |

Memory went down as intended for the apps that do not need the groups. Files needs only two loop-group passes but pays for loading the group; moving the 2.5 KB `split` pass to the core would fix that. Compile time went *up* on the device by 15–96 ms. Instruction counts under callgrind on the workstation are unchanged (Agenda 132.35 M against 132.4 M). So the cost is specific to the P4, possibly memory placement or evaluating the group's bundle inside the compile; the cause has not been found. The change was merged because every app stays within 75 % of its compile deadline, and memory is the scarcer resource on the device. Chess's margin is now 0.48 s.

A packaging detail mattered too. The first bundles gave each module its own function scope, and the QuickJS bytecode grew 48 % (701 KB against 474 KB). Compiling each bundle as one scope brought it to 261 + 45 + 196 KB.

## 6. Register classes and one instruction table

Floats live in a separate register file, `f0`–`f31`, with their own loads and stores (`flw`, `fsw`), moves between files (`fmv.x.w`, `fmv.w.x`) and calling convention. Under `ilp32f`, floats are passed in `fa0`–`fa7` and `fs0`–`fs11` are callee-saved.

The ticket kept a register a plain number with a class bit: `x_n` is `n` and `f_n` is `32 + n`, so `reg >> 5` gives the class. This choice was made for the device. The planner and emitter run at boot inside QuickJS, and objects would add allocation to the hottest paths. The integer path gained only a `reg < 32` test in `load`, `store` and `move`. `REGISTER_CLASSES` gives each class its argument, callee-saved, home and scratch registers. The planner allocates homes per class, and the float class takes part only when a function has an `f32` parameter or local, so integer-only functions plan exactly as before.

`encoding/instructions.js` holds 85 encodings: 40 RV32I, 8 M, 6 Zicsr, 26 RV32F and the 5 PIE instructions the SIMD pass uses. Each row is a mnemonic, its fixed bits and its operand syntax (`"fd, f1, f2, rm"`). The operand fields determine both the bits and the encoder's argument order, and an encoder refuses a register of the wrong class. A test assembles 2,566 instruction words over all 85 rows with the ESP toolchain's GNU `as` and compares them bit for bit. The PIE pass, which used hand-written 32-bit constants, now builds every word through the table.

Encoders are created on first use: creating all 85 at load cost the QuickJS realm 35 KB. Even so, the compiler realm is about 45 KB larger after loading. The cause is not the table's size. QuickJS keeps each function's source text unless `JS_STRIP_SOURCE` is set, and the firmware does not set it, so every comment in the compiler bundles stays resident on the device. Setting it would free more than this ticket added.

## 7. Bitwise operators

Candela's random-number generator, a PCG hash, uses variable shifts, exclusive-or and unsigned multiplication. Typed had only `>>`. The BITWISE ticket added `&`, `|`, `^`, `<<`, `>>>`, prefix `~` and hex literals, with JavaScript's precedence. Operands must be `i32`, so JavaScript's precedence pitfall `a & 1 === 1` is a type error rather than a silent bug. RV32 gets register forms and immediate forms (`andi`, `ori`, `xori`, `slli`, `srai`, `srli`). The range analysis gained a general rule: `x & y` lies in `[0, max]` when either operand is non-negative. That rule shortens `(a & 1023) / 8` plus `% 8` from 17 to 11 instructions under the `kernel` policy.

The ticket found a second tokenizer that the design had missed. On the device, the lexer reads tokens from a lexical index computed in C (`typed_lex_index.c`) rather than running its regular expression. Unchanged, that C code would have split `0x1f` into `0` and `x1f`, and `>>>` into `>>` and `>`, silently. It was updated and checked against the JavaScript lexer on a host QuickJS. The firmware installed afterwards compiled every boot app through it. A Typed version of `pcgH` matches the C on 10,000 inputs, both through a JavaScript transcription of the C and through the real C compiled with g++.

## 8. How the changes were verified

All six tickets used the same discipline:

- **Byte identity as the refactoring gate.** A refactor that claims to change no output must leave every compiled image and every observed tape unchanged. The harness grew from 84 to 125 digests as tickets added coverage, and each ticket showed that a deliberate error changes some digests.
- **Host gates after every merge.** These are `make test`, the ray-tracer frame digest (`430f0d50…`), the Chess oracle (6,981 words compared between WebAssembly and RV32), and 24 historical replays under the default and `kernel` policies. They passed after every one of the nine merges into `main`.
- **The board for timing claims.** The pipeline's heap and time trade-off was measured on the P4 in paired blocks, and its device-only slowdown is reported as found, not explained away.
- **A second pair of eyes from structure.** Each ticket kept its own diary with exact errors. The coordinator merged branches in dependency order and resolved conflicts. One example is a source list that a parallel ticket replaced with per-app manifests, which broke the tape test until it read the manifests.

## 9. What this taught

- **Defining the representation once removes a class of bugs, and finding the definitions finds bugs.** The effect-name collision and the second tokenizer both surfaced because a ticket had to enumerate every place that knew the tape or the token set.
- **Byte identity makes large refactors cheap to trust.** Nine merges restructured most of the compiler, and the gate stayed a single comparison.
- **Measure memory in requested bytes, not peak heap.** QuickJS's collector phase moves peak readings by more than many of the effects being measured.
- **Host instruction counts do not predict P4 time.** The pipeline's slowdown appears only on the device.
- **A design study can conclude "no".** The async ticket's main idea was not built, and the reasons are recorded where the next person will look.
- **Agents in worktrees inherit stale state.** One agent restored the firmware recorded in its branch's copy of `PLAYABLE.json` and overwrote a newer install. Restores now run from the main checkout.

## 10. What comes next

- **PICOCALC-TYPED-F32** (running) adds `f32` to the language, the tape, WebAssembly and RV32F through the new register classes. It fixes the semantics where WebAssembly and RISC-V disagree: NaN handling in `min`/`max`, float-to-integer conversion, and never contracting into fused multiply-add. It also writes a math library in Typed. The RV32 executors already run RV32F bit-exact against 15,454 instruction vectors captured on the P4 (PICOCALC-RV32-CONFORMANCE, the subject of the next report).
- **PICOCALC-CANDELA-TYPED** then generates Candela's kernel and scene code in Typed, with the C++ kernel kept as the benchmark.
- **Open:** the P4-only compile slowdown; `JS_STRIP_SOURCE` in the firmware; moving `split` to the core; one shared bundler for the three build scripts.

## Related notes

- [[PROJECT REPORT - PicoCalc - An Operating System That Compiles Its Own Applications - The Whole Project, Its Repository and What It Taught - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc Compiler - Under 1.5x C - Removing the Work a Register Allocator Could Not Save - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc Compiler - When Faster Code Broke the Boot - Measuring and Restoring On-Device Compile Budgets - A Technical Deep Dive]]
- Tickets: `ttmp/2026/11/22/PICOCALC-TYPED-FIRST--*` (program design and diary), `PICOCALC-TYPED-TAPE`, `PICOCALC-TYPED-FRONTEND`, `PICOCALC-TYPED-ASYNC-TAPE`, `PICOCALC-TYPED-PIPELINE`, `PICOCALC-RV32-REGISTERS`, `PICOCALC-TYPED-BITWISE`; the guide `docs/typed-compiler.md`.
