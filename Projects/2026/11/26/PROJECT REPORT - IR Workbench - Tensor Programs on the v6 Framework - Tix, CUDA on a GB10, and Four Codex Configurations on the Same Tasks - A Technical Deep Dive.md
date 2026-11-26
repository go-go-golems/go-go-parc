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
source_revision: 0a54e14
---

# Tensor programs on the v6 framework: Tix, CUDA on a GB10, and four Codex configurations on the same tasks

The IR Workbench's framework layer, `src/framework/`, has carried one domain so far: Typed, a scalar imperative language compiled to 32-bit RISC-V. Every optimization pass in that domain is checked against the original program. The framework comprises artifacts with content hashes, IR definitions, contracts, passes with correspondence, dataflow and strategies, about 11,400 lines in all. It was written to be general, but generality that has been exercised by one client is a claim, not a measurement.

This report follows a second domain built on the same framework: tensor programs written in Tix, a small index-notation language, to be compiled to CUDA and run on an NVIDIA GB10. The domain is chosen because it differs from Typed in every way that should stress the framework. Its values are arrays with shapes rather than scalars. Its optimizations change floating-point results legitimately, so a bit-exact meaning check no longer works. Its fastest engine is a remote GPU reached over ssh. Its cost, GPU time, is noisy.

The stages are designed and implemented by Codex agents. Each task is given to four Codex configurations at once, with identical briefs, so the same work also measures how the configurations compare. This report is written as the work proceeds. The sections below describe the setup, and results are added as each round finishes.

> [!summary]
> - **The question is the framework's generality.** The primary result of each stage is the list of changes the tensor domain forces in `src/framework`, each with its reason.
> - **Tix is index notation with five constructs:** shaped parameters, pointwise expressions, `sum` and `max` reductions over named indices, single-assignment statements, and affine index arithmetic. Its f32 meaning is fixed down to the order of accumulation, so implementations can be compared bit for bit.
> - **Four configurations per task:** gpt-6.2-sol and gpt-6.2-astra, each at medium and high reasoning effort. Each configuration writes its own ticket, design, implementation, diary and report. The coordinator reviews the designs, and a blind judge and a hidden test suite score them.

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
