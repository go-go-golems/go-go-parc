---
title: "Candela on the kernel: float semantics, lifting from the tape, and a checked O2 on a 332-function renderer"
aliases:
  - IR Workbench, report 3
  - IRWB-001 Candela milestone
tags: [project, compiler, ir, floating-point, riscv, candela, verification]
type: project
status: active
created: 2026-11-24
repo: /home/manuel/code/wesen/2026-11-24--compiler-workbench
ticket: IRWB-001
source_revision: fcb155f
---

# Candela on the kernel

The Compiler Workbench corpus is small by design. Its 44 projects have 70 functions, and its largest program has a few hundred entities. Every value is a 32-bit integer. Candela is different on every axis. It is the path-tracing renderer of the PicoCalc gallery, written in a scene language that compiles to Typed. Its gallery program has:
- 332 functions;
- about 12,000 statements and 13,000 single-precision float operations;
- value records returned as up to 26 separate values;
- checked text addresses and stack-allocated arrays.

This report covers the milestone at which the whole of Candela lifts into the kernel's representation, evaluates exactly as the reference compiler's RV32 image runs, and passes through the O2 pipeline with every pass checked against the original. The work was done by a subagent, which kept its own diary (`log/04-f32-candela-agent-diary.md`). This report explains the design decisions and the results.

> [!summary]
> - **Floats are carried as their IEEE bits.** Constants, locals, memory and results all hold an f32 as a signed 32-bit integer. That keeps NaN payloads and −0 exact, and keeps every artifact finite JSON. Every float operation has its own operator name, so no integer rule can match a float by accident.
> - **The evaluator agrees with the reference compiler's image on all 332 functions.** On 33,200 cases, 32,985 agree and none disagrees. The 215 inconclusive cases are step-limit hits in five deep functions, which agree on 50 of 50 cases at a higher limit.
> - **O2 keeps Candela's meaning.** Sixteen passes make 13 revisions and reject nothing; each pass is checked against r0 on 13,280 cases. Statements drop from 12,358 to 9,479 (−23 %). The final check agrees on all 33,142 decided cases.
> - **The framework's generic machinery dominates the cost at this size.** A pass costs about two minutes, whatever it changes. The time goes to canonical encoding, hashing and deep freezing in the framework core, not to the compiler's own code.

## 1. What changes when the program has floats

The first milestone's representation, `typed.blocks`, had one kind of value: a 32-bit integer. Adding single-precision floats raises three questions, and the answers determine everything else:
1. How a float value is stored in an artifact.
2. How the evaluator computes float operations, so that it agrees with the RV32F hardware bit for bit.
3. Which optimizations stay valid.

### Storing a float

An artifact in the v6 framework is canonical JSON, hashed for its revision. JSON numbers cannot represent NaN, infinity or the sign of zero, and the framework refuses non-finite data outright. Storing an f32 as a JavaScript number would therefore lose exactly the values on which float semantics differ from real arithmetic.

The kernel stores every f32 as its IEEE-754 bit pattern, interpreted as a signed 32-bit integer. `1.0f` is `1065353216`, the canonical NaN is `0x7fc00000`, and −0 is `-2147483648`. The front end's tape already uses this encoding for float constants, so constants arrive in it. A value record gains an optional `type: 'f32'`. Its absence means i32, so every existing artifact of the integer corpus keeps its hash.

Float operators get their own names: `fadd`, `fmul`, `flt`, `f2i`, `fsqrt` and so on. Under the bit encoding, an f32 addition and an i32 addition both take two integers and return one. If they shared an operator name, an integer rule such as `x + 0 → x` would match a float addition. With separate names it cannot.

### Computing a float

The evaluator implements each operator the way the reference compiler and the RV32F interpreter do. The subagent took each rule from a specific line of the vendored sources:

| operator | rule | source |
|---|---|---|
| `fadd`, `fsub`, `fmul`, `fdiv`, `fsqrt` | compute in double precision, round with `Math.fround`; a NaN result becomes `0x7fc00000` | typed-rv32.js:839–841 (static round-to-nearest-even, never fused); rv32-interp.js:30 |
| `fneg`, `fabs`, `fcopysign` | change the sign bit only; payloads survive | tape.js:89 (`fsgnjn`/`fsgnjx`/`fsgnj`) |
| `fmin`, `fmax` | the other operand when one is NaN; canonical NaN when both are; −0 < +0 | tape.js:117–122; rv32-interp.js:149 |
| comparisons | false when either operand is NaN, except `fne` | tape.js:68; rv32-interp.js:158 |
| `f2i`, `f2u` | round toward zero and saturate; NaN gives 2³¹−1 or 2³²−1; negatives give 0 for unsigned | typed-rv32.js:937; rv32-interp.js:175 |
| `floor`, `ceil`, `trunc` | x itself when \|x\| ≥ 2²³, ∞ or NaN; otherwise the integer in that direction with x's sign, so `ceil(−0.5)` is −0 | typed-rv32.js:954 |

The point of the table is that "IEEE semantics" is not specific enough. The comparison rule, the min/max treatment of −0 and the saturation of conversions are choices the target makes, and the evaluator is the specification every optimization is checked against. If it differs from the target in one of these choices, every check after it is wrong in that case.

### Which optimizations stay valid

Each pass was restricted by value type:
- **`fold`** evaluates float operators only through the same bit functions the evaluator uses. It does not fold `floor`, `ceil`, `trunc` or the float-to-integer conversions. These are exact functions of their bits, so folding them would be sound, but that decision was deferred.
- **`simplify`** applies its algebraic identities to integers only.
- **`constprop`, `licm`, `lvn` and `subst`** move, share or substitute values without changing any operation's operands. Float operations are pure and deterministic, because the rounding mode is static, so these passes stay valid for floats. Value numbering's keys include the type, so `#f1065353216` (the float 1.0) is never merged with the integer `1065353216`.
- **`strength` and `bce`** only ever matched integer operators.

The identities that are unsound for floats are exactly the ones that hold over the reals and fail for −0, NaN or infinity:

| rewrite | counterexample |
|---|---|
| `x + 0 → x` | x = −0: −0 + 0 = +0 |
| `x · 0 → 0` | x = NaN or ∞ |
| `x − x → 0` | x = NaN or ∞ |
| `!(a < b) → a ≥ b` | either operand NaN |

The subagent wrote each as a deliberately unsound pass, to test whether the meaning check rejects them. All four are rejected, but the first measurement showed a weakness in the evidence:

```
subSelf 40  ACCEPTED
subSelf 400 contractRejected … 1/11200 sampled cases disagree
notLess 40  ACCEPTED
notLess 400 contractRejected … 3/11200 sampled cases disagree
```

With purely random cases, NaN almost never occurs, so two of the four unsound rewrites passed the default check of 40 cases per function. A sampled check is only as good as its distribution, and the counterexamples of float rewrites sit at a handful of special values. The fix is in case generation. In a function with f32 parameters, the first quarter of the cases sweeps 15 edge values: NaN, ±∞, ±0, 1, −1, the smallest subnormal, the largest finite value, the smallest normal, 0.5, 2²⁴ and ±2³¹. After the sweep, all four rewrites are rejected at 40 cases. Functions without float parameters generate exactly the same cases as before, so the integer corpus's checks are unchanged.

## 2. Lifting from the tape

The Typed front end compiles source to a **tape**, a compact stack-machine encoding, and from the tape to WebAssembly. The first milestone's lifter read the front end's inspection events, which describe each function as a sequence of operations with source spans. On Candela, inspection failed with `unknown tape opcode 151 at 12`.

The subagent traced the failure to the Wasm backend. `typedWasm.compile(…, { inspect })` re-describes each function by decoding the Wasm bytes it has just emitted, using the tape's opcode table. Four tape operations, `min_num`, `max_num`, `to_i32` and `to_u32`, expand in Wasm into instructions that have no tape row, such as `f32.max` (0x97 = 151) and `select`. The finding has a consequence beyond Candela. The original lifter had always lifted Wasm operations, with the tape's higher-level operations already expanded. A checked text address, for example, arrived as a capacity load, a branch over `unreachable`, a shift and an add.

The new path lifts from the tape itself. `compileFunctions(…, { inspect })` produces tape-level events with spans and local names for all 332 functions, identical to a raw `typedTape.decode`. `ingest(name, source, { tape: true })` uses those events. The default path is unchanged, so the integer corpus lifts exactly as before.

Lifting from the tape required three new constructs:
- **Checked addresses** become one value, `caddr(r, p)`. It traps unless `p <u load32[r]` (the text's capacity word), and otherwise yields `r + (p << 1)`. It is impure, because it reads memory and can trap, so the lifter materializes it before stores and calls, as it does for loads.
- **Multi-value results.** 180 of the 332 functions return a value record as several values, up to 26 leaves. A call to such a function becomes an `eval call f(…)` statement followed by `result#k` leaves; a return becomes `return tuple(…)`. The validator allows these constructs only in those positions.
- **Frame arrays.** `array.address off` becomes `aaddr`, the frame's array base plus an offset, and `array.zero` becomes a `zero` statement. The evaluator gives each call with frame arrays a 16-byte-aligned area in a 64 KiB stack above guest memory.

Local types needed inference. The front end marks f32 locals only when they are declared through two specific helpers, and temporaries allocated with `nextLocal++` are unmarked. The lifter therefore infers each local's class by simulating the tape's operand stack until no local changes. Code after a `br`, `return` or `unreachable` is skipped until the enclosing `else` or `end`, because the stack there is polymorphic and simulating it would assign wrong types. On Candela, the inferred types agree with every type the front end does record.

The result: 332 functions, 2,409 blocks, 12,358 statements, 37,220 values and 40,916 front-end operations. The tables validate, and both round trips, through the store and through the v6 projection, are exact.

## 3. The oracle: agreeing with the reference image

The evaluator is checked against an independent implementation: the reference compiler's RV32 image of the same program, run on the vendored RV32IMF interpreter. Calling an RV32 function from the host requires the ilp32f calling convention, which `src/typed/reference.ts` implements:
- f32 arguments go in `fa0`–`fa7`, then in the next free integer register, then in stack words;
- integer arguments go in `a0`–`a7`, then in stack words;
- results follow the same rules, which matters for a function returning 26 leaves.

The interpreter's `run` accepts integer arguments only. Floats and stack words are passed through its `registers` and `fregisters` options, with guest memory laid out first, then 64 KiB of stack, then the caller's stack words.

At r0, with 100 cases per function and constructed inputs for the kernel record `K`:

| | cases |
|---|---:|
| total | 33,200 |
| agree, value results | 31,617 |
| agree, both trap | 1,368 |
| disagree | **0** |
| inconclusive (step limit) | 215 |

The inconclusive cases come from five functions: `skyBuild`, `cdlSky`, `cdlRenderSpan`, `fbm3` and `traceAOV`. At a step limit of 5·10⁶ they agree on 50 of 50 cases. Every function therefore has value results that match the reference, including `renderPixel`, which traces one complete pixel. The harness detects errors: flipping one `fmul` to `fadd` makes 20 of 20 cases disagree.

The oracle uses the reference compiler's `stock` policy, because the subagent's base revision lacked the reference pass groups. Those groups (inline, loops, kernel) are now vendored, and running the oracle against the gallery's own `kernel` policy, the image the device runs, is the next check.

## 4. O2 on Candela

`tools/candela-o2.mjs` runs O2 one pass at a time. Each pass is checked against r0 with the optimization contract: 332 functions × 40 cases = 13,280 cases per pass.

| pass | rev | edits | statements |
|---|---|---|---|
| cfg | r1 | 974 (488 retarget, 438 unreachable, …) in 110 fns | 12,358 → 11,918 |
| fold | r2 | 676 replace in 103 fns | — |
| simplify | r3 | 48 replace in 19 fns | — |
| constprop | r4 | 925 replace in 124 fns | — |
| fold | r5 | 114 replace in 53 fns | — |
| simplify | no change | | |
| dce | r6 | 2,164 remove in 144 fns | → 9,754 |
| cfg | r7 | 18 in 3 fns | → 9,751 |
| licm | r8 | 87 in 8 fns | → 9,778 |
| lvn | r9 | 256 in 38 fns | → 9,842 |
| strength | no change | | |
| bce | no change | | |
| subst | r10 | 430 in 160 fns | → 9,627 |
| subst | r11 | 280 in 132 fns | → 9,487 |
| dce | r12 | 2 | → 9,485 |
| cfg | r13 | 20 in 2 fns | → 9,479 |

No pass was rejected. The final check, at 100 cases per function, agrees on all 33,142 decided cases; 58 reach the step limit and none disagrees.

Most of the gain comes from Candela's code generator. It assigns constants to locals, and it emits `if` arms after returns. `constprop` and `fold` turn the constant locals into constants, which leaves 2,164 assignments dead, and `cfg` removes 438 unreachable blocks. `subst` merges 355 temporaries into their only readers. `licm` and `lvn` add statements: they trade a copy into a local for fewer evaluations. Statement count is therefore not the measure of success here. Instructions in an RV32 image are, and Candela's images need the float backend, which is the next step.

Two passes found nothing. `strength` finds no division by a power of two with a non-negative operand. `bce` finds nothing because, on the tape, a checked address is a single `caddr` value, not the branch pattern `bce` recognizes. A bounds-check elimination for `caddr`, which proves `p <u capacity` and replaces the value by an unchecked `r + 2·p`, is the obvious next pass. The Candela inventory counts 559 checked addresses.

## 5. Where the time goes

The O2 run took 36 minutes and held 4–6 GB. A pass that changes nothing still costs 56–79 seconds. A profile of the analyses on Candela r0 shows why:

| function | self time |
|---|---:|
| `encode` (core/data, canonical encoding) | 38.0 s |
| its helper | 17.6 s |
| `sha256` | 11.9 s |
| `immutable` | 5.9 s |
| garbage collector | 5.8 s |
| `deepFreeze` | 3.3 s |
| `defLocal`, the hottest compiler function | 0.6 s |

The framework canonically encodes, hashes and deep-freezes every artifact and analysis record, and `applyPass` projects both the input and the output into entities, about 15 seconds each. These operations are what give artifacts their content-derived revisions and make cached facts exact. At 100,000 entities they dominate everything else.

Two of the costs were in the compiler's own adapter, and they are fixed. `resolve` scanned every entity on each call, and v6's projection calls `resolve` once per entity: about 10¹⁰ steps on 103,618 entities. The projection did not finish in 60 seconds. `rebuildBlocks` had the same shape. With both indexed, the projection takes 14–18 seconds. The corpus never exposed the problem, because its programs have a few hundred entities.

The rest needs framework changes, which this milestone did not make:
- cache projections per artifact;
- skip re-encoding and re-freezing values that an adapter has just produced and validated;
- hash incrementally: a pass that changes 18 statements in 3 functions should not re-encode 329 unchanged functions.

## 6. What this milestone enables

The per-scene specialization planned in design-doc 03 starts from this head. The scene index is an i32 derived from a parameter, and `constprop` cannot see it without the Candela fact. The specialization mechanism of report 2 supplies that fact under a restricted contract. The next three steps are:
1. **The f32 backend:** RV32F instruction selection, register allocation for `fa` registers, and the ilp32f convention. This makes Candela's images measurable in instructions.
2. **`caddr`-aware bounds-check elimination**, using row-layout facts from Candela where ranges alone are not enough.
3. **Per-scene kernels** and their guarded variant, measured in bytes and instructions per sample against the reference compiler's `kernel` policy.

## Related notes

- [[PROJECT REPORT - IR Workbench - A Compiler Defined on Its Own IR Framework - Typed to RV32 on v6, With the Prototype's Numbers Reproduced - A Technical Deep Dive]], report 1.
- [[PROJECT REPORT - IR Workbench - Compilation Strategies as Checked Data - Searching Pass Orderings, Specializing on Outer Facts, and the Workbench in the Browser - A Technical Deep Dive]], report 2.
- In the ticket workspace (`ttmp/2026/11/24/IRWB-001--ir-workbench/`):
  - `log/04-f32-candela-agent-diary.md`: the subagent's diary, 9 steps.
  - `analysis/03-candela-inventory-…md`: the inventory this work followed.
- In the code:
  - `src/typed/f32.ts` and `src/typed/reference.ts`;
  - `tools/candela-oracle.mjs` and `tools/candela-o2.mjs`;
  - `corpus/candela-gallery/`.
