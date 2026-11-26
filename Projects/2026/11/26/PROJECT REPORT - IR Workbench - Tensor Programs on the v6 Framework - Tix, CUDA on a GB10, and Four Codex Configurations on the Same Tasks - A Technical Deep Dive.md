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
source_revision: 4dff51b
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
