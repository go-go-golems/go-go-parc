---
title: "Tensor programs on the v6 framework: Tix, CUDA on a GB10, and four Codex configurations on the same tasks"
aliases:
  - IR Workbench, report 11
  - Tix and the tensor track (IRWB-019)
tags: [project, compiler, tensor, gpu, cuda, agents, codex]
type: project
status: active
created: 2026-11-26
repo: /home/manuel/code/wesen/2026-11-24--compiler-workbench
ticket: IRWB-019
tickets: [IRWB-020, IRWB-021, IRWB-018]
source_revision: 9cfad72
---

# Tensor programs on the v6 framework: Tix, CUDA on a GB10, and four Codex configurations on the same tasks

The IR Workbench's framework layer, `src/framework/`, has carried one domain so far: Typed, a scalar imperative language compiled to 32-bit RISC-V. Every optimization pass in that domain is checked against the original program. The framework comprises artifacts with content hashes, IR definitions, contracts, passes with correspondence, dataflow and strategies, about 11,400 lines in all. It was written to be general, but generality that has been exercised by one client is a claim, not a measurement.

This report follows a second domain built on the same framework: tensor programs written in Tix, a small index-notation language, to be compiled to CUDA and run on an NVIDIA GB10. The domain is chosen because it differs from Typed in every way that should stress the framework. Its values are arrays with shapes rather than scalars. Its optimizations change floating-point results legitimately, so a bit-exact meaning check no longer works. Its fastest engine is a remote GPU reached over ssh. Its cost, GPU time, is noisy.

The stages are designed and implemented by Codex agents. Each task is given to four Codex configurations at once, with identical briefs, so the same work also measures how the configurations compare. This report is written as the work proceeds. The sections below describe the setup, and results are added as each round finishes.

> [!summary]
> - **The question is the framework's generality.** The primary result of each stage is the list of changes the tensor domain forces in `src/framework`, each with its reason.
> - **Tix is index notation with five constructs:** shaped parameters, pointwise expressions, `sum` and `max` reductions over named indices, single-assignment statements, and affine index arithmetic. Its f32 meaning is fixed down to the order of accumulation, so implementations can be compared bit for bit.
> - **Twelve configurations per task:** Codex CLI or Pi, gpt-6.2-sol or gpt-6.2-astra, medium, high or xhigh. Four Claude cells (Opus 5.5 and Fable 5.2, medium and xhigh) also take stage 1. Each configuration writes its own ticket, design, implementation, diary and report. The coordinator reviews the designs, and a blind judge and a hidden test suite score them.
> - **First result (Section 4):** all twelve configurations derived streaming attention correctly, so a design-only question with a known answer produces a ceiling. The small differences favour Pi over Codex, Astra over Sol, and high or xhigh over medium.

## 1. Why tensors, and why this language

A compiler framework is general when a second domain can use it without bending it. Tensor programs are a demanding second domain for this one, for four reasons.

The first reason is the shape of the values. Typed's IR is a control-flow graph of scalar statements. A tensor program's natural IR is a set of statements over iteration domains, where each statement defines a whole array. The framework's IR definitions, adapters and correspondence must accept that form without assuming blocks and branches.

The second reason is the meaning check. In Typed, an optimized program must produce bit-identical results to the original on generated inputs, and any difference is a counterexample. A tensor compiler that fuses two loops or splits a reduction into a tree changes the order of floating-point additions, and with it the low bits of the result. The change is legitimate. The contract must therefore be able to say "within a tolerance of an f64 reference", while still saying "bit-identical" for passes that should not change any bit. Report 10 (Section 6) proposed a contract assembled from a domain, an observation and a relation, and this domain needs one.

The third reason is the engine. The evidence for a GPU pass comes from compiling CUDA with `nvcc` on another machine and running it there. The framework's checks were designed around local, synchronous, cheap evaluators.

The fourth reason is the cost. RV32 instruction counts are deterministic. GPU times vary between runs, and other jobs on the same GPU disturb them.

The input language is Tix, written for this purpose. Each statement defines one tensor by an expression over index names:

```
fn attention(q: f32[N, D], k: f32[N, D], v: f32[N, D]): f32[N, D] {
  s[i, j] = sum(d) q[i, d] * k[j, d] / sqrt(D);
  m[i] = max(j) s[i, j];
  e[i, j] = exp(s[i, j] - m[i]);
  l[i] = sum(j) e[i, j];
  o[i, x] = sum(j) e[i, j] * v[j, x] / l[i];
  return o;
}
```

Index notation was chosen over the two obvious alternatives:
- **PyTorch's operator sets** (Core ATen, about 180 operators, or ONNX). Importing them means reproducing each operator's broadcasting and type-promotion rules. The work would go into PyTorch's semantics rather than into the framework.
- **Typed with tensor types.** Typed is scalar and imperative, so a contraction written in it is a loop nest. Fusion and tiling would have to rediscover the reductions that index notation states directly.

In Tix, `view`, `permute` and `expand`, which make up 26 of the 40 Core ATen nodes of a transformer block, do not exist. They are renamings of indices. Fusion and tiling become questions about which iteration domains two statements share.

The f32 meaning is defined exactly. Every literal, shape value, operation and function result is rounded to f32. A `sum` starts at 0 and a `max` at −∞, and both accumulate in increasing lexicographic order of their indices, rounding after each step. This definition has a cost: it fixes an order of accumulation that a GPU will not follow. It also has a purpose. It makes the f32 evaluator a deterministic function, against which a pass's result is either bit-identical or not, and it makes a hidden test suite possible.

## 2. The machines

The laptop that runs the agents has Intel Iris Xe graphics and no NVIDIA GPU. The GPU machine, `bling`, has an NVIDIA GB10 (compute capability 12.1, 121 GB of unified memory, aarch64) with CUDA 13.0. A probe established the remote path before any brief was written. A 2^24-element axpy, written to a temporary directory over ssh, compiled with `nvcc -O3 -arch=sm_121` in 0.59 s. It ran in 1.37 ms per launch at 147.5 GB/s on managed memory, and returned the expected value.

A second probe established that the Codex sandbox can reach that machine only when asked. A sandboxed agent's `ssh` fails with "Could not resolve hostname bling.local" under the default `sandbox_workspace_write.network_access=false`. With the setting `true`, it prints the host and the GPU's name. The stages that run on the GPU pass that setting. The others do not.

A later probe refined this. The machine is also on the tailnet as `bling`, which resolves wherever the laptop is, while `bling.local` resolves only on the home LAN, so the tools now use `bling`. And the network setting turned out not to be a boundary. With `network_access=false`, a Codex agent asked to run the same `ssh` requested escalation on its first call. An approval-assessor sidecar granted it, and the command ran outside the sandbox. With `true`, the command ran inside the sandbox without escalation. The setting decides whether an agent must ask, not whether it can reach the network. The GPU stages pass `true` so that their runs stay sandboxed.

## 3. The experiment

Each task goes to four Codex configurations: gpt-6.2-sol and gpt-6.2-astra, each at medium and high reasoning effort. This 2×2 design separates the model's effect from the effort's. Each configuration gets one agent per task, its own git worktree, and the same context:
- **The brief,** identical for all four.
- **The design policy as `developer_instructions`:** specify only the valid domain, name the simplest alternative, probe before relying on a feature, list missing work under "Later", propose missing infrastructure instead of working around it. Report 10 measured this policy. It also carries a line asking the agent to stay in its worktree.
- **The base revision,** chosen before this experiment's own ticket exists, so no agent can read what the experiment measures.

Ticket identifiers carry a letter (IRWB-020-A to D), assigned to configurations at random. The judge sees documents without frontmatter, in a shuffled order. The key that maps letters to configurations is kept outside the judge's directory.

Stage 1 (IRWB-020) asks for the Tix front end, its IR as a v6 artifact, f32 and f64 evaluators, a meaning contract with exact and tolerance relations, two checked passes, and a corpus of six programs. The two passes are chosen to exercise both relations:
- `inline` substitutes a single-use pointwise statement into its consumer. It must be bit-identical.
- `split-sum` rewrites a sum into blocks and then within blocks. It reassociates the sum, so it must be rejected by the exact relation and accepted by the tolerance relation.

The brief fixes the language core and a three-function API:
- `compileTix(source)`, which reports errors with `line:col`;
- `runTix(program, fn, inputs, {precision})`;
- `optimizeTix(program, passes)`.

The rest is the agents' to design: the IR's form, the contract, the passes' implementation, the framework changes. The work proceeds in turns of the same session. The agent designs, the coordinator reviews, the agent revises and implements, and the agent writes a report draft.

A hidden acceptance suite scores the implementations. It stays outside the repository until all four are done. It checks:
- f32 bit-exactness and f64 closeness on six programs, against hand-written JavaScript that applies the brief's rounding rules literally;
- the precedence rules;
- the order of a two-index reduction, with magnitudes chosen so that the order changes the result;
- four compile errors;
- both passes.

The research round r1 (IRWB-021) asks a harder question of the same four configurations, as a design only. Can a compiler derive streaming attention, the FlashAttention form, from the plain program above, as a sequence of rewrites each of which is checked? The streaming form keeps a running maximum, normalizer and output per row, rescaled whenever the maximum grows. It never stores the N×N score matrix, and so moves O(N·D) bytes instead of O(N²). The design must settle:
- the rules and their side conditions;
- the construct Tix lacks (a reduction whose state is not a single number);
- how each step is checked;
- which other programs the rules reach;
- a falsifiable experiment on the GB10.

## 4. The research round: every configuration derived streaming attention correctly

The matrix grew before the first results came in. Pi was added as a second harness at the same models and efforts, and xhigh as a third effort. That gives twelve cells per task: Codex CLI or Pi, gpt-6.2-sol or gpt-6.2-astra, medium, high or xhigh.

Pi differs from Codex in what the harness itself says. Its own system-message text is about 2.3K characters (a preamble, four tools, rules and documentation pointers), against Codex's 27,750-character system prompt. Pi has none of the coding and writing rules that report 10 traced the over-engineering to. Both harnesses received the same policy, Pi through `--append-system-prompt`, so the difference between them is the harness's own text and tools.

A blind judge scored the twelve research designs with a rubric that checks the mathematics rule by rule. The judge re-ran every numeric example the documents quote, and each of its 86 quotes was verified against the documents by script.

| Grouping | Overall (0–10) | Over-engineering | Insight (M7) | Words |
|---|---:|---:|---:|---:|
| Codex CLI | 8.17 | 2.50 | 4.17 | 3,096 |
| Pi | 8.67 | 2.83 | 4.67 | 3,218 |
| gpt-6.2-sol | 8.17 | 2.50 | 4.17 | 3,198 |
| gpt-6.2-astra | 8.67 | 2.83 | 4.67 | 3,116 |
| medium | 7.75 | 2.00 | 3.75 | 2,593 |
| high | 8.75 | 2.75 | 4.75 | 3,217 |
| xhigh | 8.75 | 3.25 | 4.75 | 3,660 |

The first four criteria were 5 out of 5 for all twelve documents: mathematical correctness, completeness of the derivation, the new construct's semantics, and the checking plan. Every design represents the empty prefix with a tag rather than with −∞, which avoids the indeterminate form exp(−∞ − (−∞)). Every design applies both rescaling factors when two partial summaries merge. Every design proves the merge associative over the summaries that can actually occur.

The construct all of them added is a reduction whose state is a triple: the running maximum *m*, the normalizer *l*, and the output accumulator *o*. Two such states merge as

```
m = max(m₁, m₂)
l = l₁·exp(m₁ − m) + l₂·exp(m₂ − m)
o = o₁·exp(m₁ − m) + o₂·exp(m₂ − m)
```

and the output is *o / l* once the last block has been merged.

The strongest idea, found in four documents, splits this merge into two smaller lemmas. The first rebases each block's sum to the block's own maximum. The second folds the resulting (maximum, sum) pairs. One document abstracts this into a scale-transport law, r(u, u) = 1 and r(u, v)·r(v, h) = r(u, h). From that law, the rescaling in the merge follows for any reduction whose terms scale multiplicatively, not only for softmax.

The differences between cells are small, and each cell had one run. Pi scored above Codex by half a point, Astra above Sol by half a point, and high and xhigh above medium by a point. Length and over-engineering grew with effort. The lowest cell (Codex, Sol, medium) made the one error the judge found: it claimed that its rules reach softmax followed by a contraction, without an inlining rule that would make that reachable.

The main finding is a ceiling. Streaming attention is well known, its identities are in the literature, and all twelve configurations know them. A design-only question with a known answer measures recall. It does not separate the configurations. The objective version of this research is its implementation (T5 in the repository's `BACKLOG.md`), where the derived kernel's measured GPU time against an unfused and a hand-written kernel would decide.

## 5. Stage 1 designs: the task that separates the configurations

Stage 1 drew sixteen designs. Twelve came from the Codex and Pi cells. Four came from Claude cells, Opus 5.5 and Fable 5.2 at medium and xhigh effort, run as subagents of the coordinating session. The Claude cells are kept few because they share the coordinator's quota. A blind judge scored all sixteen with a rubric of over-engineering counts and five fitness criteria:
- semantic fidelity to the brief;
- the contract;
- the framework analysis;
- the test plan;
- implementability.

All 192 of its quotes were verified against the documents.

| Group | Over-engineering (0–10) | Fitness (0–10) | Excess items | Words |
|---|---:|---:|---:|---:|
| Claude (Opus, Fable) | 2.75 | 8.50 | 12.3 | 4,990 |
| Codex CLI | 2.50 | 7.50 | 6.3 | 2,577 |
| Pi | 4.50 | 6.67 | 12.0 | 2,608 |
| Codex · Astra | 2.00 | 8.00 | 5.7 | 2,627 |
| Codex · Sol | 3.00 | 7.00 | 7.0 | 2,528 |
| Pi · Astra | 4.00 | 7.00 | 11.0 | 2,581 |
| Pi · Sol | 5.00 | 6.33 | 13.0 | 2,635 |

The table supports three readings. Each cell had one run, and each group combines three or four cells.

**The harness matters, in the direction opposite to the one report 10 suggested.** Report 10 traced defensive error contracts to a rule in Codex's system prompt. Here, with the policy present in both harnesses, the Pi cells, whose prompt lacks that rule, specify more error conditions than the Codex cells (4.7 against 3.0 on average) and twice the excess overall. The defensive tendency is partly the model's own. Something in the Codex context restrains it. The most likely candidate is the policy's rank: Codex passes it as a developer message, ranked above anything the user writes, while Pi appends it to its own system prompt.

**Sol is the weakest model in both harnesses.** It is weaker in fitness and stronger in over-engineering than Astra on the same harness. That makes Sol the target of the prompting experiment (Section 6).

**The most common excess was caused by the brief.** Twelve of sixteen designs plan a general solver for symbolic shapes, because the brief's grammar allows an affine expression in a parameter's type, such as `f32[N + 1]`, which no corpus program uses. The policy's "keep the input domain as narrow as the experiment allows" did not prevail over a grammar that explicitly admits more. A brief's specification is read as a requirement, and its generality is implemented.

All sixteen designs agree on the two framework changes the tensor domain needs, and both are in `src/framework/passes/define-pass.ts`:
- **A synchronous entry point.** Checked pass application exists only as an asynchronous function, because the analysis manager is asynchronous, while the fixed API `optimizeTix` is synchronous.
- **A lazy edit.** `applyPass` always opens an IR edit, which throws for an adapter that cannot rebuild a native value, even when the pass returns one and never edits.

Most designs also found that the framework's differential check already carries both relations, exact and tolerance, without change. The first finding of the tensor track is therefore small and specific. Contract checking generalizes, and pass application assumed a rewritable, asynchronous domain.

## 6. Prompting Sol: three policies on the same four cells

The stage-1 scores made Sol the target of the prompting work: it was the weaker model in both harnesses. Two revisions of the developer policy were tried on the four Sol cells that matter most in practice (Codex and Pi, medium and high effort). Each revision redesigned stage 1 from the same base with the same brief.

- **v1** is the policy from report 10: state the input domain, compare with the simplest alternative, prefer the smallest deliverable, describe only what can be built, probe before relying on a feature.
- **v2** adds four rules aimed at what the stage-1 judge counted:
  - support only the subset the corpus uses, and reject the rest with an ordinary error;
  - specify errors only by where they are detected and what their message says;
  - build one path per job;
  - justify every numeric threshold by an error argument or a measurement.
- **v3** replaces v2's first rule. That rule had given as its example "affine expressions in parameter types that no program uses", to be rejected, but those expressions are part of the brief's fixed grammar. v3's version: accept everything the brief fixes; cover it with the simplest method that works; reject only what would need machinery no example uses. v3 also adds a rule to rely on the input assumptions the brief states, such as "inputs are finite".

Judges disagree with each other by up to two fitness points on the same document, so all twelve designs (four cells × three policies) were scored blind in one session:

| Policy | Excess items | Over-engineering | Fitness | Fidelity to the fixed core (A1) |
|---|---:|---:|---:|---:|
| v1 | 7.00 | 3.75 | 8.25 | 4.75 |
| v2 | 5.00 | 2.75 | 6.50 | 2.25 |
| v3 | 5.75 | 3.00 | 7.75 | 4.00 |

**v2 shows that a policy outranks a brief.** All four v2 designs restricted parameter dimensions to bare names, as the policy's example said, although the brief's grammar admits affine expressions there. The policy came as a developer message (Codex) or in the system prompt (Pi), and both rank above the user's brief. The agents followed the higher-ranked instruction where the two conflicted. Fidelity fell by 2.5 points, and fitness with it. A policy rule must never be stated in terms that can contradict a task's fixed specification.

**v3 is the best trade-off, and the gain is small.** It keeps most of v2's reduction: excess falls by one or two items in every cell against v1, and over-engineering by one point in three of the four cells. It also restores most of the fidelity, with fitness equal to v1's in three of the four cells. The size of the effect is about one rubric point, with one run per cell. An earlier session comparing only v1 and v2 found the same direction with larger magnitudes. Counts there were not capped at one per kind, and excess fell from 12.25 to 9.00.

**What no wording removed.** Every policy left two kinds of excess in place:
- contract statuses and evidence formats nobody asked for, such as "a function with no sampled case cannot be accepted" (11 of 12);
- rules for non-finite values in a brief that says inputs are finite.

v3's explicit rule about stated assumptions did not remove the second. These are defaults strong enough that a general instruction does not reach them; a brief that wants them gone has to say so for the specific case.

## 7. Stage 1 implementations: fourteen correct compilers

Fourteen of the sixteen design cells went on to implement: the twelve Codex and Pi cells and the two medium-effort Claude cells. Each received a blind review of its design, about 350 words. A reviewer checked the review's claims against the base revision. Each implementer revised its design, then implemented the language, the IR, the evaluators, the contract and the two passes in its own worktree.

### How the implementations were scored

Three measures were used, all written before any implementation's code was read.

**A hidden acceptance suite.** The suite has 25 tests of the fixed core and API. It compares the six corpus programs bit for bit against hand-written f32 references, and checks f64 precision, the reduction-body rule, precedence, two-index accumulation order, four compile errors, and both passes through `optimizeTix`. Reading the suite against the brief before use found one invalid test, and one test that did not test what it named:
- The two-index test used an output index with no use at all. The brief makes that a compile error, so the test would have failed exactly the correct implementations. Two of them later confirmed this, with "2:5 Cannot infer extent" and "2:31: cannot infer index extent".
- The `inline` test ran only on programs where the brief's inline condition (pointwise, single use) never held. A pass that did nothing would have passed it.

Both were fixed before the first implementation was scored, and the suite was then frozen by hash.

**A differential cross-check.** A generator produces random valid programs in the fixed core as syntax trees. It prints them as Tix and evaluates the trees directly under the brief's f32 rules, so the reference needs no parser. Its programs avoid domain errors by construction: `log` and `sqrt` take e·e + c, `exp` takes tanh(e)·2, and division is by e·e + 1 or by a shape value. Sixty programs with three inputs each contain 88 reductions, 103 calls and 62 unary minuses. Every implementation runs them in its own process. Both passes are correct on every program, so a rejection by `optimizeTix` is a false rejection by the implementation's contract.

**A sensitivity variant.** The suite's mlp program uses `x` both as its input tensor and as an output index, `y[i, x] = …`. The brief does not say whether index and tensor names may coincide. The variant renames that one index and is reported next to the frozen score.

### Results

| Cell | Suite | Variant | Cross-check f32 | `inline` | `split-sum` | `src/tensor` lines | Framework diff |
|---|---|---|---|---|---|---:|---|
| Codex · Astra · medium (B) | 25/25 | 25/25 | 180/180 | 60/60 | 60/60 | 917 | +85/−27 |
| Codex · Astra · high (D) | 25/25 | 25/25 | 180/180 | 60/60 | 60/60 | 972 | +86/−28 |
| Codex · Astra · xhigh (I) | 25/25 | 25/25 | 180/180 | 60/60 | 60/60 | 1,086 | +140/−71 |
| Codex · Sol · medium (C) | 25/25 | 25/25 | 180/180 | 60/60 | 60/60 | 1,380 | +132/−47 |
| Codex · Sol · high (A) | 25/25 | 25/25 | 180/180 | 60/60 | 60/60 | 1,336 | +102/−34 |
| Codex · Sol · xhigh (L) | 25/25 | 25/25 | 180/180 | 60/60 | 60/60 | 1,278 | +112/−45 |
| Pi · Astra · medium (E) | 25/25 | 25/25 | 180/180 | 60/60 | 59/60 | 805 | +85/−26 |
| Pi · Astra · high (H) | 25/25 | 25/25 | 180/180 | 60/60 | 59/60 | 1,004 | +32/−19 |
| Pi · Astra · xhigh (J) | 25/25 | 25/25 | 180/180 | 60/60 | 60/60 | 1,067 | +118/−0 |
| Pi · Sol · medium (F) | 25/25 | 25/25 | 180/180 | 60/60 | 60/60 | 1,300 | +105/−29 |
| Pi · Sol · high (G) | 25/25 | 25/25 | 180/180 | 60/60 | 60/60 | 1,279 | +123/−37 |
| Pi · Sol · xhigh (K) | 25/25 | 25/25 | 180/180 | 60/60 | 55/60 | 1,317 | +177/−81 |
| Claude · Opus · medium (N) | 22/25 | 25/25 | 180/180 | 60/60 | 60/60 | 1,674 | +193/−36 |
| Claude · Fable · medium (P) | 22/25 | 25/25 | 180/180 | 60/60 | 60/60 | 1,717 | +168/−55 |

**Correctness is uniform.** All fourteen implementations agree bit for bit with the tree-walking reference on every random case, in f32, and agree with it in f64. Every result of `inline` is bit-identical to its input. Every accepted `split-sum` computes the same function. The fixed core's f32 meaning, written in four sentences, was precise enough that fourteen independent implementations compute identical bits. No implementation changed a file outside the scope the brief allowed.

**What separates them is the contract.** Three implementations reject a correct `split-sum` on some random programs:
- K on 5 of 60;
- E and H, both Pi with Astra, on the same program.

The rejected programs are well conditioned: plain f32 evaluation stays within 4e-7 of f64, relative to max(1, |r|). K's tolerance is a fixed bound, |c − r| ≤ 2·10⁻⁶ + 2·10⁻⁵·|r|. One design (P) had measured in advance that a fixed relative bound cannot separate correct from wrong programs: correct evaluations reached a relative error of 9.9·10⁻³, wrong ones went as low as 1.6·10⁻⁶. It used a running first-order error bound instead, which accepted every correct `split-sum`. The tolerance is the one place where the brief left a numerical judgement open, and it is the one place where the implementations differ in behaviour.

**The name-reuse rule divides them by vendor.** Both Claude implementations reject `y[i, x]` when `x` is a tensor: "'x' is a tensor and cannot be an index" and "index x is a parameter". All twelve OpenAI implementations accept it. The brief is silent, and neither reading is wrong. The lesson is for the brief: a fixed core must specify its namespaces, and a test must not depend on a rule the brief does not state.

**Size follows the model more than the harness.** Astra wrote 805 to 1,086 lines of tensor source and Sol 1,278 to 1,380, in either harness; the Claude cells wrote about 1,700. In the implementation turn, Sol also generated more output tokens than Astra (38,000 to 46,000 against 20,000 to 33,000). Effort level made no consistent difference to size or correctness.

**The framework changes converge on one entry point.** Every implementation adds a synchronous checked application for passes that return a native value, because the fixed `optimizeTix` is synchronous:
- thirteen in `src/framework/passes/define-pass.ts`, most sharing the native-result steps with `applyPass` through new helpers;
- one (J) in a new file, `passes/sampled-sync.ts`, leaving the existing code untouched.

All sixteen designs had also proposed making `applyPass` open its edit lazily, so that an adapter without `rebuild` can be used. Only four implementations did it (I, K, N, P). Once the synchronous path exists, the fixed API never opens an edit, so the lazy edit is needed only by designs that also test the asynchronous path on the new adapter. Most implementers dropped it: they implemented less than they had designed, and less than the review had approved.

No implementation changed anything else in the framework. The differential contract machinery needed no change in any of the fourteen. The framework generalizes to a second domain with one missing entry point.

### The base for stage 2

The implementation merged as the base for the CUDA stage was chosen by three criteria, in order:
1. every objective check passes;
2. the smallest framework change;
3. the smallest source.

Nine cells meet the first. Codex · Astra · medium (B) and Codex · Astra · high (D) tie on the second, and B is smaller. B's framework change adds `applyNativePassSync(pass, before, gate, params)` and moves the shared native-result steps into two helpers that `applyPass` also uses. Like ten of the fourteen, it does not make `applyPass`'s edit lazy, so the asynchronous path still requires `rebuild`; that remains in the backlog. B's design was one of the two in which the reviewer found nothing it had to change.

## 8. Stage 2 designs: lowering to CUDA, and an exactness nobody claimed

Stage 2 asks for a checked lowering of Tix to CUDA C on the GB10.
- **The mapping is fixed** so that implementations can be compared: one kernel per statement, one thread per output element, each reduction a sequential loop in the order the f32 meaning prescribes.
- **The relation is not fixed.** The lowering's contract runs the candidate on the remote GPU, and each design must decide whether the GPU result is bit-identical with the f32 meaning or only within a tolerance of the f64 reference, and establish its choice by probing.
- **The fixed API adds three functions:** `cudaSource`, `runTixCuda` (returning `gpuMs`, measured with CUDA events) and `checkLowering`.

All twelve agents start from the merged stage 1, on a branch without the experiment's own ticket. The same twelve Codex and Pi cells took part; the Claude cells were left out to save usage.

The question I expected to separate the designs was not stated in the brief. In IEEE mode, CUDA's `+`, `−`, `*`, `/` and `sqrt` are correctly rounded. Rounding a double to f32 is what `Math.fround` does. With one thread per element and a sequential loop, the order of accumulation is the f32 meaning's order. What remains is two things:
- **Contraction:** `nvcc` fuses a·b + c into one FMA by default, unless told `-fmad=false` or given `__fmul_rn` and `__fadd_rn`.
- **The transcendental functions:** `expf`, `logf` and `tanhf` are accurate to a few ulps but not correctly rounded, whereas `Math.fround(Math.exp(x))` almost always is.

Computing them in double and rounding should close the gap. A backend built that way would be bit-exact, and its lowering could be checked under the exact relation, the cheapest and strongest check there is.

| Group | Over-engineering | Fitness | Excess items |
|---|---:|---:|---:|
| Codex · Astra | 1.33 | 9.00 | 3.0 |
| Codex · Sol | 3.33 | 7.00 | 7.3 |
| Pi · Astra | 2.33 | 8.00 | 5.7 |
| Pi · Sol | 3.00 | 8.00 | 7.0 |

**Every design chose the tolerance relation**, and the judge found their arithmetic claims sound. Four designs went further and probed double-precision `exp`, `log` and `tanh` rounded to f32 on the GB10, and found no mismatch apart from NaN bit patterns. None took the step to an exact relation:
- two treated the probe as sampled evidence only;
- two rejected exactness because NaN payloads differ, which the f32 meaning does not define.

An exhaustive comparison over all 2³² f32 inputs for each unary function would have settled it. It needs every GPU result and every rounded JavaScript result, which is large but feasible in chunks. The designs measured the right thing and then defaulted to the weaker, more familiar claim.

**The model effect held; the harness effect did not, for Sol.** Astra over-engineered less than Sol in both harnesses, as in stage 1, and Codex · Astra was again the best group. But Codex · Sol was now the weakest, below Pi · Sol, which contradicts stage 1's finding that the Codex context restrains defensive defaults. With one run per cell, and judges that differ by up to two fitness points, the harness difference for Sol is within the noise.

**The review found one GPU effect most designs missed.** Under CUDA 13's default lazy module loading, a kernel's first timed interval includes loading it: 0.101 ms against 0.003 ms on the next launch, and 0.005 ms after an explicit `cudaFuncGetAttributes`. So nine designs' `gpuMs` would have included start-up time, which the API excludes.

**The framework mostly fits.**
- Ten designs leave `src/framework` unchanged. They use the differential contract's existing `decide`, `baselineKey` and `subjectKey` to batch cases into one remote run and to reuse verdicts.
- Two propose a batch-only differential specification, without the per-case synchronous `run` and `compare` that the current type requires. A third works around the same gap with a stub that throws.
- The one tool change the designs agree on is a private remote working directory per call, with a lock on each compile key, so that concurrent agents cannot see each other's half-written binaries.

## 9. Stage 2 implementations: twelve correct lowerings, three of them exact

All twelve stage-2 implementations lower every Tix program to CUDA, run it on the GB10, and compute the right function. All twelve still pass the frozen stage-1 suite. The evaluation was written before any stage-2 design was read. Its reference is the merged stage-1 interpreter, already validated bit for bit, and it measures more than the brief required.

### Whether the lowering is exact

The decisive measurement is how many output elements are bit-identical to the f32 meaning. Here is a representative cell from each pattern. The table in the diary (step 25) has all twelve.

| Cell | Corpus, small | After the passes | Random programs | Corpus, full size | Construction |
|---|---|---|---|---|---|
| Codex · Sol · high (I) | 6/6 exact | 4/4 | 20/20 | 6/6 | `__fadd_rn`/`__fmul_rn`, transcendentals in double |
| Codex · Sol · medium (J) | 6/6 | 4/4 | 20/20 | 6/6 | the same |
| Pi · Sol · xhigh (C) | 6/6 | 4/4 | 20/20 | 6/6 | the same |
| the other nine | 3/6 | 1/4 | 16/20 | 3/6 | no contraction; `expf`, `tanhf` in single precision |

The nine all fail on the same programs: those that use `exp` or `tanh` (softmax, attention, the MLP's GELU). Their elements differ by about one unit in the last place, and up to 2.2·10⁻⁵ (scaled) at full size in the MLP, where the GELU's differences pass through a second contraction. The programs without transcendentals are bit-exact in all twelve. Every implementation prevented contraction into fused multiply-adds, either with flags or with round-to-nearest intrinsics. That was the one arithmetic difference the designs had all identified.

Three implementations, all running Sol, computed the transcendentals in double and rounded them. Section 8's question was whether that makes the lowering exact. A separate exhaustive check settled it: for all 2³² f32 bit patterns, CUDA's double-precision `exp`, `log` and `tanh`, rounded to f32, equal `Math.fround(Math.exp(x))` and so on. The comparison hashed each block of 2²⁰ results on the GPU and in JavaScript and compared the hashes. It took 1.5 s on the GPU and 156 s in eight worker threads, and found no mismatch. (The f32 meaning is defined through JavaScript's `Math` functions, so this holds for V8 in Node 24.18. It is not a property of the language.)

So three of the twelve backends are bit-exact by construction. **Yet all twelve check their lowering under the tolerance relation.** The strongest available relation was built, and not claimed, by every implementation that built it.

### What else was measured

- **The checks cost seconds.** `checkLowering` took 2.5 to 6.0 s per program. The kernels themselves run for milliseconds, so the time goes to the remote round trip (copying the inputs, compiling unless the build is cached, running, copying back) and to the local reference evaluation. The two were not timed separately. Batching all of a check's cases into one launch, through the differential contract's existing `decide` hook, is what keeps it at one round trip per check.
- **Kernel times are close across implementations,** because the mapping was fixed:

  | Program | GPU time |
  |---|---|
  | 512³ matmul | 0.17–0.26 ms |
  | attention (1,024 × 1,024, width 64) | 1.4–1.8 ms, one outlier at 7.3 ms |
  | MLP | 0.8–1.15 ms |
  | softmax and layernorm, 4,096 × 1,024 | about 0.45 ms |

  These are naive kernels. The comparison with tiled kernels and cuBLAS is a later stage.
- **Size by model:** Astra wrote 391 to 498 lines of new tensor source, Sol 607 to 744. Sol wrote more, and built all three exact backends. Astra wrote less, and built none.
- **Framework and tool changes:**
  - Ten implementations change nothing in `src/framework`. Two add a batch-only differential spec.
  - Eleven change the GPU tool, mostly by giving each call a private remote directory and locking the compile cache. One leaves the tool as it was.

### The base for stage 3

All twelve passed everything the brief required. Stage 3, fusion, benefits most from a base whose lowering is bit-exact: then a fused kernel that keeps the evaluation order can be checked under the exact relation, by comparing bits, with no tolerance to justify. So the criteria were, in order:
1. bit-exact with the f32 meaning on every measured case;
2. the smallest framework change;
3. the smallest tool change;
4. the smallest source.

Codex · Sol · high (I) met all four. It was the stage's worst-scored *design* (over-engineering 4, fitness 6). In neither stage did the design score predict the quality of the implementation.

## 10. A research round: four models on "what would make Tix best in class?"

After stage 2, four configurations got the same open question: Sol and Astra in Codex at high effort, and Opus and Fable as Claude subagents at their default effort. Each was asked to define "best in class" for Tix, propose the compiler work, and back it with literature and with experiments on the GB10. The product code stayed unchanged.
- **The base** held stage 2 as merged, without the coordinator's backlog or analysis, so each idea is the agent's own.
- **The policy** was the same for all four, and neutral: probe before relying on a feature, and stay isolated. The usual anti-over-engineering rules would have capped a creativity round.
- **Time:** every cell finished in 16 to 62 minutes of a three-hour budget.

### What they proposed

All four defined best in class around Tix's exactly specified f32 meaning: the fastest code that stays bit-identical to it, with every step checked. Each found its own way there.

| Cell | Central idea | Strongest evidence |
|---|---|---|
| Astra | fast `exp` with one table coefficient fitted by interval intersection, plus exact fused rows | softmax 4.25× and attention 1.38× (reproduced), bit-identical; the deployed binary certified against Node by digest |
| Opus | exact-meaning scheduling with exhaustively verified fast `exp` and `tanh`, and per-shape checks by symbolic fingerprints | all six programs 2.0–7.6× faster and bit-identical; a planner from the IR at 3.19× geometric mean; `exp` and `tanh` match on all 2³² inputs (reproduced) |
| Fable | acceptance by proof (normal-form equivalence), plus a *parity transducer* | a mutant the merged gate accepts and the proof rejects (reproduced); a parallel fold bit-identical to the sequential one, by two-entry chunk summaries |
| Sol | certified row schedules as v6 postconditions; an INT8 route that is exact on a proved dyadic grid | rows 2.0× and 2.5× faster; exact 512³ tile 3.9× faster than stage 2 (reproduced); INT8 exact but slower than the FP32 tile |

**The convergent measurements** carry the most weight, because independent cells found them:
- **Exact tiling:** an exact tiled 512³ matmul takes 0.054–0.058 ms in three cells. That is about 3.7× faster than stage 2, and 1.6–1.75× slower than cuBLAS. The ceiling is the meaning's separate multiply and add: 14.4 TFLOP/s on this GPU, against 27.0 with FMA.
- **cuBLAS:** at 4096³ it computes exactly a sequential FMA fold, found by two cells.
- **A parallel exact fold** was found by two cells: Fable's parity summary and Astra's even-translation certificate. Neither judge found it in print.

Fable's cell also found a real hole in the merged stage-1 gate. Its sample shapes cycle through three sizes over the sorted shape symbols, so in `mlp` the extents D and O are equal in every case. A pass that confuses them is accepted.

### How it was judged, and what the judging showed

Two blind judges scored the four tickets twice each: a Claude subagent, and Codex · Sol with web access. They scored ingenuity, creativity, scientific depth, evidence, correctness, grounding and padding.

| Model | Claude judge (two runs) | Codex judge (two runs) | Mean | Errors listed |
|---|---|---|---|---|
| Astra | 7, 7 | 9, 9 | **8.0** | 2 |
| Opus | 9, 8 | 6, 7 | 7.5 | 30 |
| Fable | 8, 7 | 7, 7 | 7.25 | 22 |
| Sol | 6, 6 | 8, 8 | 7.0 | 7 |

Each judge put its own family's designs first: by 1.5 points out of 10 for the Claude judge, and 1.75 for the Codex judge. That is more than the largest gap between models once both are averaged (1.0). Each judge repeated itself within a point.

A ranking from either judge alone would have been confident, and reversed by the other. This bears on Sections 5 and 8, whose design scores came from Claude judges only.

**What both judges agree on:**
- **The Claude designs contain more errors.** That holds in all four runs, and every error the coordinator re-checked held. Examples:
  - Opus's claim that batch invariance is a theorem of the meaning fails for `y[i] = x[i] + N`;
  - Fable's comparison with the fixed tolerance used a different reference from the gate's.
- **Sol's design is the least creative,** the closest to the standard fusion and tiling playbook.

Read with the family effect removed:
- **Astra** produced the best-evidenced, most correct design.
- **Opus** produced the broadest and most ambitious one, with the most overclaims.
- **Fable** produced the most original theoretical idea, in the shortest time.
- **Sol** produced the most conventional plan.

The ideas are now items in the workbench's backlog.

### Stages 1 and 2, re-judged by a Codex judge

After R2, the stage-1 and stage-2 design packs went to a Codex judge (Sol, high) with the same rubrics and base revisions. The design scores in Sections 5 and 8 had come from Claude judges alone.

| | Claude judge | Codex judge |
|---|---|---|
| Stage 1, the 4 Claude designs: fitness / over-engineering | 8.50 / 2.75 | 5.25 / 7.00 |
| Stage 1, the 12 OpenAI designs: fitness / over-engineering | 7.08 / 3.50 | 8.92 / 2.08 |
| Stage 1, rank correlation (Spearman), fitness / over-engineering | −0.29 / 0.33 | |
| Stage 2, 12 OpenAI designs only: rank correlation | 0.62 / 0.60 | |

- **Within one family the two judges mostly agree,** as stage 2 shows. That leaves the comparisons among the OpenAI cells standing: Sol against Astra, Codex against Pi, and effort level.
- **Across families they disagree.** On stage 1 their fitness rankings are weakly opposed. Section 5's finding that the Claude designs were the fittest holds only under the Claude judge. Under the Codex judge, Codex · Astra's designs are the fittest (9.17 against Fable's 5.50), and the Claude designs the most over-engineered.

Neither judge is neutral, so the experiment's cross-family design rankings rest on the mean of the two judges. Error counts and reproduced experiments carry more weight than either judge's ranking. The scorecard shows both judges.

## Where the material is

- **Ticket:** `/home/manuel/code/wesen/2026-11-24--compiler-workbench/ttmp/2026/11/26/IRWB-019--tensor-programs-on-the-v6-framework-and-a-codex-model-comparison-on-the-same-tasks/`
  - the diary: `log/01-diary.md`;
  - the briefs: `various/prompts/t1/`, `various/prompts/r1/`;
  - the configuration keys: `various/results/*-config-key.json`;
  - the launchers: `scripts/`;
  - per-round output (logs, heads, extracts): `various/kit/<round>/`.
- **Agents' tickets:** IRWB-020-A to D (stage 1) and IRWB-021-A to D (research round), on branches `t1-<config>/irwb-020-<letter>` and `r1-<config>/irwb-021-<letter>`.

## Related notes

- [[PROJECT REPORT - IR Workbench - Codex Agents as Designers - Where the Over-Engineering Comes From, and What a Revised Brief and a Self-Review Change - A Technical Deep Dive]]
- [[PROJECT REPORT - IR Workbench - Synthesis - Four Milestones, Five Research Plans, and the Order the Measurements Suggest - A Technical Deep Dive]]
- [[PLAYBOOK - Measuring and Reducing Over-Engineering in Agent-Written Designs]]
