---
title: "Compilation strategies as checked data: searching pass orderings, specializing on outer facts, and the workbench in the browser"
aliases:
  - IR Workbench, report 2
  - IRWB-001 strategies and workbench milestone
tags: [project, compiler, ir, typescript, riscv, search, specialization]
type: project
status: active
created: 2026-11-24
repo: /home/manuel/code/wesen/2026-11-24--compiler-workbench
ticket: IRWB-001
source_revision: fcb155f
---

# Compilation strategies as checked data

The first report on this project ended at parity. The Typed compiler, defined on the IR Workbench v6 framework, produced the same revisions, the same provenance trees and the same RV32 images as the Compiler Workbench prototype, down to the byte and the instruction count. Parity is the evidence that the port is faithful. It also means that the compiler, at that point, was no better than the prototype.

This report covers the next milestone. It asks what the framework makes possible that the prototype could not easily do, and answers with measurements. Four pieces of work are described:
- **Strategies:** compilation as a plan that forks, measures and chooses.
- **Per-function search:** each function gets its own choice.
- **Specialization:** a pass that uses facts from the program above Typed, under a contract restricted to those facts.
- **The browser workbench:** the prototype's interface, running on the new kernel, where all of this can be tried per project.

The report also covers the audit that checks every preservation claim, and the reference compiler cross-check.

> [!summary]
> - **A strategy is data.** It is a v6 Strategy IR plan over versioned pass algorithms. Every candidate pass application in a plan is checked against the original program. `chooseBest` records the objective, every alternative's metrics or rejection, the winner and the tie-break rule. Only the winner's chain becomes revisions, and `why` still answers through them.
> - **Choosing among four pass orderings beats the fixed O2 pipeline on 12 of 44 projects**, and lowers total emulator instructions over the corpus by 2.2 %. No new pass was written. Eleven of the twelve gains come from one extra `subst` after O2's final cleanup, which removes, in those eleven programs, a loop copy that the prototype's book attributed to a missing pass. Searching per function found nothing beyond per-program choice, for a reason section 5 explains.
> - **Specialization on an outer fact is a checked transformation.** Binding `s = Square` in `area(s, k)` reduces the function to `return (k * k)`. The meaning contract is restricted to inputs with `s = Square`, and every resolved branch's `because` chain reaches the outer fact.
> - **The workbench runs in the browser on the new kernel.** The kernel's passes are asynchronous; the prototype's scripts are synchronous. A replay context reconciles the two without rewriting the scripts: 45 of the corpus's 46 scripts run unchanged. Every tile reads at 60–80 columns.

## 1. Why a fixed pipeline leaves performance on the table

A compiler's optimization level is a fixed sequence of passes. Compiler Workbench's O2 is sixteen passes, `cfg, fold, simplify, constprop, fold, simplify, dce, cfg, licm, lvn, strength, bce, subst, subst, dce, cfg`, the same list for every program. The list is a compromise. Each pass creates opportunities for others: constant propagation exposes folds, folding exposes dead code, removing dead code merges blocks, merged blocks expose further propagation. A fixed list runs each pass at the positions where it helps on average.

Two observations make a fixed list suboptimal for a particular program. First, a pass can become applicable only after passes that run later in the list. Section 5 shows a case: a copy that `subst` cannot remove until `dce` and `cfg` have run, and O2 runs `subst` before them. Second, the number of rounds that matters varies. A program whose constants cascade through several levels of folding needs more rounds than O2 gives it; a program with no constants needs none.

The prototype could run any pipeline, but it had no way to compare pipelines as part of compilation. Its pipeline runner applied passes in order and reported what changed. Choosing between two pipelines meant running both by hand and reading the numbers. On the new kernel, choosing is part of the compiler itself.

## 2. A strategy is a plan, not a script

The v6 framework has a small language for describing computations over artifacts, the **Strategy IR**. A plan is a tree of nodes, each of a fixed kind:

| node kind | meaning |
|---|---|
| `apply` | run one registered algorithm (here: a pass) on the current artifact |
| `sequence` | run children in order, each on the previous output |
| `fork` | run each named branch on the same input; produce a candidate set |
| `chooseBest` | measure every candidate with a metrics algorithm, drop those that violate constraints, pick the best by an objective |
| `attempt` | run a body; on failure with given codes, run a fallback |
| `repeatUntilStable` | run a body until its output revision stops changing, up to a limit |
| `forEach`, `conditional`, `verify`, `checkpoint`, … | iteration, branching on a condition, explicit checks, named intermediate results |

An algorithm is referenced by id and version, for example `typed.constprop@1`. The plan never contains code. This matters for three reasons. A plan can be serialized, stored in a project's `strategies/` folder, and diffed. The interpreter can record what every node did, so a decision can be explained after the fact. And the registry that maps algorithm references to code is the single place where the compiler decides what a plan is allowed to call.

The workbench writes strategies in a short form that compiles to a plan. The preset that picks the fastest of the standard pipelines is:

```json
{
  "about": [
    "The standard pipeline that runs the fewest instructions",
    "on the project's own cases."
  ],
  "choose": { "O0": "O0", "O1": "O1", "O2": "O2", "loops": "loops" },
  "by": "instructions"
}
```

`planFromSpec` turns it into a `chooseBest` node over a `fork` with four branches. Each branch is a `sequence` of `apply` nodes, one per pass, and O0's branch is a single `apply` of `typed.keep`, the identity. The compiled plan has 37 nodes. The short form exists because the compiled plan, printed at the 72-column width the workbench's tiles use, is 214 lines long, while the short form is 9.

## 3. Every candidate is checked

A pass becomes a strategy algorithm through `passAlgorithm`, one of the framework extensions from the first milestone. The algorithm applies the pass with `applyPass`, which does the following:
- runs the pass;
- verifies that it wrote only the entity kinds it declared;
- verifies every analysis it claims to preserve;
- checks the output against the transformation contract.

The contract for every optimization is the same differential invariant, `typed.meaning-kept`: evaluate the original program (r0) and the candidate on seeded cases drawn from the project's input specifications, and compare results, traps and final memory. When the contract rejects an output, the algorithm reports `contract-rejected` instead of returning the artifact, and the strategy interpreter treats that branch as failed.

The consequence is that a strategy cannot choose a wrong program, however it is written. The `wrong-shift` project contains a division by a power of two applied to a signed value, which `div-to-shift` rewrites into an arithmetic shift. That rewrite rounds negative values the wrong way. A strategy that offers O2 with and without `div-to-shift` produces this alternative list:

```json
[
  { "name": "plain", "status": "feasible", "m": 1650 },
  {
    "name": "shift",
    "status": "rejected",
    "reason": "contract-rejected: [contractRejected] Pass typed.div-to-shift
      output rejected: typed.meaning-kept: 27/80 sampled cases disagree"
  }
]
```

The faster program is never measured, because it never becomes a candidate. In the prototype, the equivalent check was a separate step the user ran after the pipeline; a pipeline that included the wrong pass produced a wrong program and reported success.

## 4. Choosing, and what the decision records

`chooseBest` needs a number per candidate. The metrics algorithm `typed.metrics@1` computes four:
- statements;
- blocks;
- image bytes, by lowering the candidate to RV32 with the backend;
- emulator instructions, the sum of retired instructions over 10 seeded cases per function, run on the vendored RV32IMF interpreter.

On Blend, the decision record for the preset above reads:

| candidate | status | instructions | bytes | statements | blocks |
|---|---|---:|---:|---:|---:|
| O0 | feasible | 2,255 | 96 | 13 | 7 |
| O1 | feasible | 2,235 | 88 | 11 | 6 |
| **O2** (winner) | feasible | **1,925** | 88 | 12 | 6 |
| loops | feasible | 1,945 | 96 | 12 | 6 |

The record also states the objective (`min instructions`), the constraints (none here) and the tie-break rule (`lexicographic candidate name (code unit order)`). The tie-break is part of v6's decision evidence because ties are common. Minimizing bytes on Blend ties O1 and O2 at 88, and the record says O1 won because its name sorts first. A user reading the decision does not have to guess why.

One detail of the metric turned into a bug. The interpreter reports a run that reaches its step limit with a step count of `NaN`, because the true count is unknown. One project in the corpus, `my-analysis`, has an input that loops forever. Its instruction sum became `NaN`, and the strategy interpreter refused the metric with `IR data must contain only finite numbers`. The framework was right to refuse: a `NaN` compares false with everything, so a minimization over it would have chosen arbitrarily. A limited run now costs the limit, 200,000 steps, and a fifth metric, `limited`, counts how many runs hit it. A constraint `limited == 0` can then exclude candidates that make more cases run out of steps.

### Publishing the winner

The losing branches of a `chooseBest` exist only inside the strategy's execution. `runStrategy` walks back from the winning artifact through the pass results that produced it, and publishes that chain into the program's revision timeline. On Blend, the six published revisions are `cfg, fold, simplify, constprop, dce, licm`, exactly the revisions O2 produces directly. Because the published revisions are the same artifacts the pass results recorded, provenance is unaffected: `why('s:blend.15')` reaches `licm@r6 ← constprop@r4 ← op:blend#35`, because of the loop fact, as it does after a direct pipeline run.

## 5. Searching orderings over the corpus

The experiment behind this section's numbers is `tools/search-experiment.mjs`. For each of the 44 projects it compiles three ways and measures the result with the same metric:
- **O2**, the fixed pipeline;
- **per program:** `chooseBest` over four candidates, by instructions;
- **per function:** the same four candidates, chosen separately for each function.

The four candidates are:

| candidate | passes |
|---|---|
| `O2` | O2 |
| `O2x2` | O2, then O2 again |
| `loops+O2` | the `loops` pipeline, then O2 |
| `O2+more` | O2, then `lvn, subst, subst, dce, cfg, licm, subst, dce, cfg` |

Every candidate on every project was checked against r0 after every pass, and each final program was checked again on 40 cases.

Twelve of the 44 projects get faster:

| project | O2 | best ordering | gain | winner |
|---|---:|---:|---:|---|
| constants | 70 | 40 | 42.9 % | `O2x2` |
| checksum | 1,410 | 1,260 | 10.6 % | `O2+more` |
| early-exit | 631 | 566 | 10.3 % | `O2+more` |
| wrong-shift | 1,650 | 1,500 | 9.1 % | `O2+more` |
| strength | 1,938 | 1,802 | 7.0 % | `O2+more` |
| ramp | 1,040 | 970 | 6.7 % | `O2+more` |
| bounds-two | 810 | 760 | 6.2 % | `O2+more` |
| bounds-lab | 5,333 | 5,038 | 5.5 % | `O2+more` |
| strings | 10,833 | 10,302 | 4.9 % | `O2+more` |
| start-here | 3,871 | 3,750 | 3.1 % | `O2+more` |
| histogram | 2,292 | 2,230 | 2.7 % | `O2+more` |
| across-calls | 640 | 630 | 1.6 % | `O2+more` |

Over the corpus, instructions fall from 77,321 to 75,651 (2.2 %). This total leaves out `my-analysis`, whose non-terminating case is costed at the 200,000-step limit in every column, which would hide the differences. In every project that got faster, the image also got smaller, and the corpus total falls from 5,160 to 5,092 bytes. None of the 132 final programs (44 projects, three ways each) disagrees with r0 on 40 cases per function.

The winners say something about O2 itself, and following one of them up shows what. After O2, Checksum's loop body still begins with a copy:

```
bb:total.3  -> [.1]
    s:total.4    t3 = i
    s:total.9    s = (s + load16[(work + (t3 << 1))+4])
    s:total.10   i = (i + 1)
    s:total.11   goto .1
```

Applying the nine extra passes of `O2+more` one at a time, only the first `subst` changes anything. It replaces `t3` by `i` and deletes the copy, and instructions fall from 1,410 to 1,260. O2 itself runs `subst` twice, but before its final `dce` and `cfg`, and the copy becomes substitutable only after those two passes. For each of the eleven `O2+more` winners, O2 followed by a single `subst` gives exactly the winning instruction count. `constants` is different: its constants cascade through more levels of folding than one O2 reaches, and running O2 twice finishes the job.

This copy has the shape of the `t7 = i` that the book names as one of two reasons the reference compiler is faster: a copy that survives in bounds-checked loops. That copy was read as a missing pass, copy coalescing. In Checksum, `bce` has removed the bounds check, so the copy has a single reader and the existing `subst` removes it when it runs at the end. In Blend the check survives, `t7` has two readers (the check and the load), and an extra `subst` does not touch it. Blend is not among the twelve winners. So the search split the book's gap in two. Where the check is gone, the gap is a pass-ordering problem that one run of the search found. Where the check stays, it still needs coalescing. Changing O2 would break parity with the book, so the ordering finding becomes a new pipeline rather than an edit to O2.

The search is not free. The whole experiment took 21 minutes of compile time for 44 small projects, because each candidate is a full pipeline with a meaning check after every pass.

### Per-function search

Per-function search registers each pass a second time per function, as `typed.<pass>@<fn>`. The second registration has the same body, but it edits only the named function. `searchPlan` builds one `chooseBest` per function, in source order, and passes `{ fn }` to the metrics algorithm, so each choice is measured on that function's own cases. The choices chain: the second function is optimized on top of the first function's winner.

On this corpus, per-function search never beat per-program choice. The result follows from the candidates and the corpus. Every candidate starts with O2 and only adds passes after it. An added pass rarely makes any function slower, so the candidate that is best for the program as a whole is usually best for each function in it. Per-function search can only win when a candidate helps one function and hurts another. In addition, 25 of the 44 projects have a single function, where the two methods are the same by construction.

A second experiment tested whether candidates that disagree change this. On the 19 projects with more than one function, the candidates were O1, O2, `loops` and O2 without `licm`. `licm` raises register pressure, so removing it can make a loop body cheaper. Per-function search now chose different pipelines for different functions in several projects. In `div-magic`, `digitsum` kept O1 and `sevenths` took `loops`. In `wrong-shift`, `eighth` took O1 and `bucket` took O2. The totals were still identical: 33,354 instructions both ways.

The per-function choices differ only where the alternatives tie. When O1 and O2 give `eighth` the same instruction count, the tie-break picks O1 by name, while the per-program winner, O2, is just as good for that function. Per-function search can only win when two functions strictly prefer different candidates. With these candidate sets, no project in this corpus has two such functions.

The negative result is still useful. It shows that, on programs of this size, a single choice per program loses nothing, and per-function search costs one full candidate set per function. The case for per-function search rests on larger programs with many independent hot functions. Candela's gallery has 332 functions.

## 6. Checking what passes claim

Every pass declares which analyses its edit leaves intact. Value numbering, for example, claims that the control-flow graph and the dominator tree survive it. A declared preservation lets the analysis manager carry the fact forward to the new revision instead of recomputing it. A false claim is therefore a silent error: later passes read a stale fact.

The framework verifies each claim, either by checking a transfer function or by recomputing the analysis and comparing. Verification only happens, though, when the fact exists for the input revision. A claim about an analysis nobody computed was never checked. **Audit mode** closes that gap: `applyPass` with `auditPreservation` computes every claimed fact before the pass runs, so every claim is checked.

`tools/audit-preservation.mjs` applies every pass that makes claims to every revision of every corpus pipeline: 1,376 applications. With the corrected declarations, no claim fails. With the prototype's declarations restored, three claims fail on real revisions:

```
subst -> typed.loops   10 revisions, e.g. bounds-lab@r4 bounds-two@r4 checksum@r4 early-exit@r5
lvn   -> typed.loops    9 revisions, e.g. orders@r0 orders@r1 orders@r2 orders@r3
dce   -> typed.loops    2 revisions, e.g. ramp@r3 strength@r3
```

The first report described the `lvn` failure, which the framework caught on the first full run. The `subst` and `dce` failures had survived that run, because on those revisions nothing had computed the loop analysis before the pass ran.

### The reference compiler

The repository that hosts the PicoCalc toolchain has its own Typed-to-RV32 compiler, with a default policy that inlines calls, rotates loops and unrolls kernels. Vendoring its pass groups (unchanged, digest-checked) makes the book's chapters 13 and 14 reproducible as tests. Chapter 13 compares the evaluator with the reference compiler's images on all 70 functions: 6,986 decided cases agree, and so do our O2 images. Chapter 14 compares speed and size:

| benchmark | r0 | ours, O2 | reference |
|---|---:|---:|---:|
| Blend | 531 | 451 | 383 |
| Checksum | 446 | 366 | 292 |
| insertion sort | 2,022 | 2,022 | 1,533 |
| Collatz | 1,590 | 1,590 | 1,486 |
| value numbering | 690 | 570 | 695 |

Over the corpus, our O2 images total 5,160 bytes against the reference's 7,628. Our compiler produces smaller code that mostly runs slower. The book attributes the gap to two missing transformations: copy coalescing (a copy `t7 = i` survives in bounds-checked loops) and loop rotation (the loop exit sits between the test and the body, so every iteration takes a jump back). Section 5 showed that where `bce` has removed the check, the copy is an ordering problem rather than a missing pass.

## 7. Specialization on outer facts

A Typed program carries only the facts its source states. The programs that generate Typed often know more. Candela, the renderer that compiles to Typed, knows which scene is being rendered, how its rows are laid out, and which values are colours in [0, 1]. Those facts exist as Candela artifacts, not as Typed code. Specialization is the mechanism that brings such a fact into the Typed compiler without trusting it blindly.

A fact enters as an artifact of the framework IR `typed.bindings`:

```js
createArtifact(BindingsIR, 'shapes', {
  formatVersion: 1, source: 'demo',
  bindings: [{ fn: 'area', param: 's', value: 4, entity: 'shape/Square' }],
});
```

The `specialize` pass substitutes the bound value for the parameter's reads. Its `because` field names the fact by a stable reference, `fact:typed.bindings:shapes@<revision>#shape/Square`. The existing passes do the rest. In the `match-enum` project,

```
function area(s: Shape, k: i32): i32 {
    let r = 0;
    match (s) {
        Circle: { r = 3 * k * k; }
        Square: { r = k * k; }
        Tri: { r = k * k / 2; }
    }
    return r;
}
```

becomes, after `specialize` and O2,

```
bb:area.0 -> []
  s:area.15  return (k * k)
```

The substituted constant makes each comparison of the `match` foldable. `cfg` resolves the three branches, `dce` removes the dead cases, and `cfg` merges what is left.

The difficult part is the contract. The specialized program does not mean what r0 means: for `s = Circle` it returns `k * k` instead of `3 * k * k`. If the contract stayed unrestricted, the meaning check would reject the first pass after specialization, and every pass after that. If the check were dropped, the pipeline would be unchecked. The program therefore records the assumption `{ area: { s: 4 } }`, and from that revision on, the meaning contract compares with r0 only on cases that satisfy it. Under the assumption, each revision agrees on 80 of 80 cases. Without it, the same final program fails, which the test asserts: the restriction is what makes the passes valid, and the evidence says so.

Assumptions belong to revisions. Undoing or checking out a revision before the specialization drops the assumption, so a later check cannot silently run under a restriction that no revision justifies.

Provenance crosses the boundary. Each of the three branch resolutions records the folded comparison as its reason, and `why` on that comparison reaches the fact reference. The new branch statements that `cfg` created were pruned in the same revision, which is a divergence from the prototype; section 9 returns to it.

## 8. The workbench in the browser

The prototype is a browser application. A page shows the project's files, the program at the current revision, its control-flow graph, facts, provenance, checks, the RV32 image, a console, the book, and tiles that a project's own UI scripts add. The milestone ports that interface onto the new kernel. A subagent did the port, and kept its own diary of the work.

### Synchronous scripts over an asynchronous kernel

The corpus has 46 workbench scripts and 11 UI scripts, written against a synchronous API:

```js
const before = p.image().bytes;
p.pipeline('O2');
return { bytes: [before, p.image().bytes] };
```

The kernel's passes are asynchronous, because v6's contract checks and strategy interpreter are. A synchronous `p.pipeline('O2')` cannot wait for them. Rewriting every script with `await` would fork the corpus from the book, whose walk-throughs quote the scripts.

The port uses a **replay context** instead (`src/workbench/sync.ts`). Script code runs in attempts. Each asynchronous call inside an attempt does one of two things:
- **replays** its recorded outcome, if one exists for its key;
- **suspends**, otherwise, by throwing a `Suspend` value.

On a suspension, the runner performs the call on a scratch copy of the program, records the outcome under the call's key, restores whatever state the attempt touched, and runs the script again from the top:

```
run(script):
  loop:
    try:   return script()            # every async call replays or suspends
    catch Suspend(op, key):
      outcome[key] = await op()       # on a scratch copy of the program
      restore(touched)                # undo what the attempt changed
```

A script with k new asynchronous calls runs k + 1 times. The cost is small next to the passes: O2 on the `start-here` project takes about 3 seconds checked, while re-running script code takes milliseconds. Two requirements follow from the design:
- **Scripts must be deterministic.** An attempt must make the same calls in the same order every time.
- **Keys must capture everything an outcome depends on:** the operation, the program, the revision chain and the arguments. For a strategy that names a user-written pass, the key also includes a hash of that pass's body, so that editing the pass invalidates its recorded outcomes even when the plan text is unchanged.

With the replay context, 45 of the 46 corpus scripts run unchanged. Blend's walk-through returns `{bytes: [96, 88], steps: [115, 99]}`, as in the book. The one that does not, `wrong-shift/explore`, applies `div-to-shift` and expects to see the wrong result. The new kernel gates every pass with the meaning contract, so the pass is refused. The script can opt out with `{ check: false }`, which restores the prototype's behaviour. The port records this, and nine other deliberate divergences from the prototype, in `src/workbench/DIVERGENCES.md`, which is bundled into the in-page reference.

### Keeping the page responsive

A promise chain that never waits for I/O yields only to the microtask queue, so the browser cannot repaint until it finishes. The first version of the prototype's "pass orders" task, which compiles a project 24 ways, froze the page for 34 seconds. The port yields to the browser's task queue between replay attempts and between strategy nodes. That uses a `MessageChannel` message, which schedules a macrotask, and an optional `pause` hook that `runStrategy` awaits before each algorithm. The same task now takes 18 seconds, renders 86 frames and shows progress. The longest frame is about one second, the duration of a single pass.

### Strategies and the compiler in the interface

Two views are new relative to the prototype:
- **Compiler** lists the passes, analyses, pipelines and strategies as data, with where each is defined. Built-in passes are read-only. A project can define passes with the prototype's builder API, and those are held to the built-in passes' rules: declared writes, checked preservation claims and the meaning contract.
- **Strategies** edits strategies in the short form, runs them, and shows the decision: the winner, each alternative with its metrics or rejection reason, the published revisions, and the execution trace.

A user pass written in the Compiler view can be applied, and it can win a strategy candidate. In the port's test, a pass that rewrote one multiplication won by instructions, 50 against 60.

### Narrow tiles

The workbench is a grid of tiles, and a tile is typically 60 to 80 columns wide. Everything the workbench shows as text was formatted for that width, 72 columns:
- `project.json` files: prose fields became arrays of lines, which the project loader joins;
- notes and book prose: wrapped by a Markdown-aware wrapper;
- strategy files: printed by a width-aware JSON printer that keeps an object on one line when it fits.

The formatter verified each file before writing it. A project's meaning had to be deep-equal before and after, and its Markdown had to produce the same block structure. 88 files changed. Typed sources were left as written, because their line numbers are part of provenance: Blend's line 5 accounts for 322 of its 451 instructions, and a figure in the book says so. The views wrap long lines with a hanging indent and give code editors a ruler at 72 columns. At a 63-column tile, no view scrolls sideways.

## 9. What did not go as planned

- **The `NaN` metric** (section 4) cost a failed corpus run before it was understood. The framework's refusal of non-finite data was the correct behaviour, and the fix belonged in the metric, not in the interpreter.
- **Scripted edits to formatted source failed silently.** Two replacements written as text substitutions matched nothing, because the code formatter had broken the target lines differently. The project normalization never ran, and the corpus formatter's meaning check stopped before writing anything. After that, every scripted edit was followed by a check that it had applied.
- **Entities created and removed within one revision cannot be resolved.** The prototype's store keeps every entity it ever made. The new kernel's native value keeps only live entities, so the three branch statements that `cfg` creates during specialization, and prunes in the same pass application, appear in no revision. Provenance is intact through the edit log, whose `because` fields name the folded comparisons. But `why` on the pruned statements reports them as absent, where the prototype would answer. Keeping such entities in the revision's report would restore the prototype's behaviour.
- **The per-program experiment was first run with each project's own pipeline as the baseline**, as the chapter 14 corpus total once was. The book's statements are about O2 everywhere, and the comparison in section 5 uses O2 everywhere.

## 10. Where this leads

The next milestone brings Candela's gallery program, 332 functions and about 13,000 single-precision float operations, onto the kernel. A subagent is lifting floats and Candela's addressing operations into the Typed representation and making the evaluator and passes float-safe. Once it lands, three experiments from the ideas document (design-doc 04 in the ticket) become runnable:
- **Per-scene kernels:** specialize the renderer on the scene index with the mechanism of section 7, checked on that scene's inputs.
- **Guarded specialization:** clone the kernel per scene and dispatch once, with a byte constraint deciding how many clones are worth their size.
- **Tolerance contracts for fused multiply-add:** a differential invariant whose comparison accepts a bounded error, so that a rewrite changing the last bit of a result is a checked, recorded trade rather than an unchecked flag.

Section 6's table also gives a concrete target for new passes. The gap to the reference compiler's 383, 292, 1,533 and 1,486 instructions can be closed with three changes, measured on the same five benchmarks:
- loop rotation;
- copy coalescing for copies with several readers;
- the end-of-pipeline `subst` that section 5 found.

## Related notes

- [[PROJECT REPORT - IR Workbench - A Compiler Defined on Its Own IR Framework - Typed to RV32 on v6, With the Prototype's Numbers Reproduced - A Technical Deep Dive]], the first report (framework, passes, parity).
- Ticket workspace: `/home/manuel/code/wesen/2026-11-24--compiler-workbench/ttmp/2026/11/24/IRWB-001--ir-workbench/`
  - `design-doc/04-optimization-ideas-…md`: the sixteen ideas and their order.
  - `log/02-implementation-diary.md`: steps 6–9.
  - `log/05-ui-agent-diary.md`: the browser port.
- Code:
  - `src/typed/strategies.ts`: metrics, the registry, plan shapes, the per-function search, `runStrategy`, and the short form and presets.
  - `src/typed/specialize.ts`.
  - `src/workbench/sync.ts`: the replay context.
  - `tools/search-experiment.mjs`.
  - `tools/audit-preservation.mjs`.
