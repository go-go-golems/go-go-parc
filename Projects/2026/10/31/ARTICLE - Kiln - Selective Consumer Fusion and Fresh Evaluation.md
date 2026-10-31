---
title: "Kiln: Selective Consumer Fusion and Fresh Evaluation"
aliases: [Kiln Selective Fusion Implementation and Confirmation]
tags: [article, compilers, cuda, optimization, research]
status: active
type: article
created: 2026-10-31
repo: /home/manuel/code/wesen/kiln/worktrees/passnet
ticket: KILN-005
source_revision: 51b45eb
compiler_revision: d324850
selection_revision: 731e834
report_revision: 4f2d36f7b3dd6b1ae76a18f3a6e52a6fd85d655e
---

# Kiln: Selective Consumer Fusion and Fresh Evaluation

Kiln can now fuse a producer into a chosen subset of its consumers while preserving the producer for consumers that still need it. The implementation extends the existing fusion-rule factory, uses the existing expression substitution and graph transaction machinery, and leaves the default compiler policy unchanged. It passes all 29 core test files, the bounded-policy tests and 108 CUDA fixture comparisons across FP32, FP16 and BF16.

A fresh experiment compiles twelve reusable policy programs over twenty previously unused exact models. Training selects a program with a 1.01454× end-to-end ratio, but confirmation measures 0.97205×, corresponding to about 2.9% more elapsed time than unchanged Kiln. Every confirmation graph passes correctness. The result establishes a usable transformation capability and a failed generalization attempt, rather than a new optimization default.

> [!summary]
> The compiler now supports consumer selection with correct retained-producer accounting. The experiment uses frozen candidates and a committed training selection. The selected program regresses on confirmation and accepts no actual partial fusions on either split. More permissive candidates exercise partial fusion during training but are slower.

## 1. Fusion changes both computation and materialization

A computation graph represents operations as nodes and tensor dependencies as directed edges. A producer kernel p computes a tensor consumed by c1 and c2. Ordinary fusion replaces each consumer load of p with p's expression at the requested coordinates. If no consumer needs the materialized tensor afterward, its producer kernel can be removed.

Kiln's existing rule applies that substitution to every consumer and then checks aggregate estimated work. This produces an all-or-none choice for each producer. Adjusting the global work-growth threshold changes which complete proposals are accepted, but cannot choose c1 while leaving c2 connected to the materialized p.

Selective fusion adds that missing graph operation. A policy first selects consumers, then the compiler constructs and validates the proposed mutation. If only c1 is selected, c2 still reads the original producer. If both are selected, p becomes unused and normal dead-code elimination removes it. No new runtime dispatch mechanism is necessary.

```text
Original dependency:        Partial fusion:
       p -> c1 -> out1      expression(p) -> c1 -> out1
       p -> c2 -> out2      p ------------> c2 -> out2
```

This distinction separates the implemented capability from the policy selected in an experiment. A compiler may support partial fusion while a particular selected program performs only complete fusions or rejections on the observed population. Performance attribution must follow the actual accepted mutations.

## 2. Use the graph transaction machinery already present

The implementation lives in `packages/kiln/src/std/loop.js`. `createFusionRule` gains an optional `selectConsumer` callback. Its default remains null, which selects every consumer and preserves the previous rule behavior. The existing `mergeLoopOps` instance and standard pipeline retain the same default bound.

The rule plans substitutions against one graph state before editing any consumer. The selector receives immutable scalar features, including producer work, consumer work, proposed fused-consumer work, element counts and number of consumers. The general compiler callback also receives a consumer index; the declarative research language deliberately excludes node IDs and consumer order.

```javascript
std.loop.createFusionRule({
  selectConsumer: f => f.fusedConsumerWork <= f.consumerWork * 1.1,
  maxWorkGrowth: 1.02,
  onDecision: event => decisions.push(event)
});
```

This example illustrates the API; it is not the selected policy from the experiment. The callback must return a Boolean. An empty selection follows the existing skip path and creates no rewrite. Selected consumers are changed with `tx.set`; unselected consumers retain their original nodes and edges.

`inlineInto` remains the only expression substitution implementation. It remaps input indices, substitutes producer coordinates and generates fresh reduction binders. Reusing it avoids a second set of semantics for repeated operands and nested reductions. After mutation, `Graph.dce` traces liveness from outputs and effectful nodes. A producer referenced by an unselected consumer remains live. A rejected aggregate guard restores the original graph through the existing transaction path.

The match retains the earlier restrictions: the producer cannot itself be a graph output, and every direct consumer must be a loop kernel. User-storage mutation, alias writeback and side-effecting kernels are outside this transformation's scope.

## 3. Count a retained producer in the proposed cost

Partial fusion invalidates one assumption in the old guard. When every consumer is inlined, the producer disappears, so the post-mutation cost can omit it. With unselected consumers, that computation and materialization still exist.

For direct consumers U(p), the affected-region estimates are:

\[
W_0=W(p)+\sum_{c\in U(p)}W(c),
\]

\[
W_1=\mathbf{1}_{p\;live}W(p)+\sum_{c\in U(p),\;c\;live}W(c').
\]

A selected consumer contributes its substituted expression, while an unselected consumer contributes its original expression. Both complete and partial fusion now use this common formula. Complete fusion reduces to the original accounting because the producer is dead.

A focused regression is constructed so that partial fusion exceeds the 1.02 bound when the retained producer is counted, but would pass if its cost were omitted. The test verifies rejection and exact restoration of the selected consumer object and graph identity. A separate select-all test verifies equivalence with the existing transformation.

The estimate comes from `workOf(schedule(...))`, which weights operations and memory accesses by loop trip counts. This is a model of work, not a measured latency prediction. Kernel launch costs, cache behavior, materialized tensor volume and scheduling choices can still make an accepted program slower. Correct accounting is necessary for meaningful search but does not establish cost-model accuracy.

## 4. Express two decisions in a bounded program

The integration's policy language previously expressed only aggregate profitability. A new selective kind contains a consumer tree and an aggregate tree. Both use the same validated predicate/leaf grammar and share a 31-node budget with maximum depth six.

A consumer threshold compares proposed fused-consumer work against original consumer work. An aggregate threshold compares complete affected-region work, including a retained producer. The existing hard two-times aggregate growth limit remains in force. Unknown features, fields, malformed leaves and nonfinite values are rejected before compilation.

For this experiment, all selective candidates use the following structure:

```text
consumer tree:
    if consumerCount == 1: select
    otherwise: select when fusedConsumerWork <= edgeBound * consumerWork

aggregate tree:
    accept when totalFusedWork <= aggregateBound * totalOriginalWork
```

Always selecting single consumers at the first stage is deliberate. Their consumer-local work can increase while removing the producer makes the complete mutation profitable. The aggregate guard still decides whether that removal justifies the proposal.

The policy validator compiles immutable closures, so later modification of the input JSON cannot alter a running experiment. `compile_policy.mjs` passes both functions to the shared fusion-rule factory. Qualification, source provenance, GPU measurement, training selection and summary tools remain shared with earlier studies.

This is deterministic grammar construction authored by the current Codex session. It is not an external PassAgent invocation, a separately trained model or evidence that an autonomous system discovered a new rewriting algorithm. The new graph capability is implemented directly; the experiment selects reusable programs that control it.

## 5. Validate semantics before timing policies

The focused compiler test checks selected and unselected edges, retained producer identity, exact output structure, empty skips, rollback, select-all equivalence and repeated operands with nested reductions. The initial test incorrectly expected two selector calls while scalar constants introduced two additional broadcast kernels. The saved diagnostic shows those legitimate candidates. Replacing the constants with tensor inputs isolates the intended lifetime assertion without changing compiler behavior to satisfy the test.

The full compiler boundary passes 29 test files. The existing Python integration boundary passes 73 tests; five targeted proposal tests pass after adding the new proposal generator. These scopes are recorded separately rather than describing the earlier Python run as covering later tests.

Independent CUDA fixtures cover elementwise, reduction and nested-reduction fanout in three dtypes. Each form compiles under unchanged, none, partial and all selection modes, giving 36 artifacts. Normal reference checking remains enabled. Three seeds produce 108 CUDA comparisons against independently expressed PyTorch equations, including unchanged-input checks; all pass.

Fixture success establishes tested numerical behavior. It adds no original PassBench task acceptance. The cumulative original replay ledger remains eleven complete tasks and 206 individually passing graphs; import eligibility remains 1,029 graphs and 51 complete families.

## 6. Freeze a fresh experiment

The v6 selector excludes exact models and generated-program hashes from all previous policy corpora, including the completed v5 study, and excludes exact models used by the full 200-task evaluation set. It retains fixed resource bounds and category quotas but uses a new declared salt. Twenty sources are selected after 2,549 task inspections: six reduction and six matrix graphs for training, followed by four of each for confirmation.

The membership hash is `0547e152ab29ae79070177cec031ddb393751f2b45d13499548a583668e7203f`. Exact model exclusions do not imply architectural independence: related models can remain. This is a constrained FP32 development population, not a representative sample of every operation, dtype or layout in PassNet.

Training controls compile before candidate declaration and match under unchanged and explicit-default policies. Their traces contain 69 multi-consumer attempts. The frozen twelve candidates consist of unchanged/default controls, scalar bounds 1.00/1.25, and eight selective combinations. Consumer bounds are 1.00/1.05/1.25/1.50; aggregate bounds are 1.02/1.25.

The reference protocol is explicit from the outset: separate elementary FP32 arithmetic in every compiler variant and highest-precision FP32 matrix operations in PyTorch. This follows the earlier diagnostic of native TF32 reference disagreement. It is a modified compiler-policy research protocol and cannot establish native PassBench acceptance or exact paper reproduction.

The shared `compile_study.py` verifies committed source bytes and frozen declarations around every policy, preserves partial artifacts on failure, and records qualification status. All 240 artifacts compile and qualify from revision `d324850`; unchanged/default outputs match. The remote source snapshot exactly matches compilation snapshot `9ed3c57ddc5a24b1226a99d1eaf3669fbe68b8ddc5eef508a323f7b235ffc52d`.

## 7. Training selects a program; confirmation rejects its generalization

The timing budget remains twenty warmups, one hundred trials and three repeats, with bounded retries when IQR exceeds twenty percent of the median. Distinct executable fingerprints are measured in seeded shuffled order. Exact aliases share evidence. The objective is the family-balanced geometric mean of synchronized end-to-end ratios relative to unchanged Kiln.

Every training candidate qualifies. `select-edge100-total125` scores 1.0145415× and ties exactly with edge105 under the same aggregate bound. Declaration order selects edge100. The selection and complete training measurements are committed in `731e834` before confirmation GPU timing.

The more permissive selective programs accept genuine retained-producer partial mutations during training: edge125/aggregate102 accepts three, and edge125/aggregate125 and edge150/aggregate125 each accept seven. The latter pair scores approximately 0.96831×. The selected policy accepts no partial mutations in training. Its observed decisions therefore cannot support a training gain attributed specifically to partial fusion.

Confirmation times only unchanged Kiln and the committed selection. Every one of the eight graphs passes correctness and timing qualification. No graph is replaced, filtered or used to choose another policy.

| Quantity | Result |
|---|---:|
| Training selected end-to-end ratio | 1.014542× |
| Confirmation end-to-end ratio | 0.972049× |
| Confirmation CUDA-stream elapsed ratio | 0.975411× |
| Confirmation failures | 0 / 8 |
| Accepted partial fusions in selected training / confirmation | 0 / 0 |

A speedup ratio below one means the selected compiler is slower. The end-to-end result corresponds to about 2.88% more elapsed time. Both metrics regress, so the candidate is not adopted as a default.

## 8. Diagnose the regression without altering the experiment

Post-confirmation inspection is descriptive and does not change selection or add a candidate. Three confirmation graphs improve materially: SegFormer measures 1.07387× and two ViTPose variants measure 1.16321× and 1.18831×. The ALBERT graph measures 0.54113×, offsetting those improvements in the geometric mean. Other ratios are near one.

Both compilers emit three kernels for the ALBERT graph, demonstrating why kernel count alone is insufficient. The baseline's first materialized output has shape [2048,1], while the selected program materializes [2048,312]. The corresponding first schedule changes from a 512-thread row mapping to a 1,024-thread row mapping, and the second selected schedule stages all inputs. The graph contains residual addition followed by LayerNorm over width 312.

The enlarged first materialization is a concrete structural correlate of the slowdown: it contains 312 times as many values. This audit does not isolate a single causal mechanism through profiling or an ablation. It does establish that a policy can retain the same kernel count while changing partition boundaries, intermediate storage and schedules substantially.

The diagnosis suggests that future profitability work should represent intermediate volume and reduction reuse explicitly. Any new policy derived from these observations requires a newly declared evaluation population. Reusing the same confirmation results to choose a different winner would answer a different experimental question.

## 9. What is established and what remains open

Selective consumer fusion is implemented through a shared compiler primitive with validated graph lifetimes and aggregate accounting. The bounded policy interface can control consumer edges. A complete fresh selection/confirmation sequence runs on actual CUDA hardware and preserves negative outcomes. These are concrete advances toward optimizing the compiler itself.

The current selected program fails generalization and performs no observed partial fusions. The work does not establish that partial fusion improves performance, that the work model predicts profitability, or that an external LLM can synthesize useful compiler algorithms. Original PassAgent evaluation, remaining full benchmark support, native numerical compatibility and broader synthesis remain open.

Primary implementation files are `packages/kiln/src/std/loop.js`, `packages/kiln/test/selective-fusion.mjs`, and the integration's `fusion_policy.mjs`, `propose_policy.py`, `compile_policy.mjs` and `compile_study.py`. Design 11 explains the mutation contract. Saved scripts 185–200 preserve investigation, fixture generation, frozen selection, compilation, measurement and post-confirmation diagnosis.

For review, run script 199 against the archived artifacts and measurements. It checks frozen declarations, structural qualification, explicit reference flags, exact selection bytes from the pre-confirmation commit and remote source identity. Script 200 reconstructs the descriptive confirmation audit without timing or policy changes. The detailed diary records the implementation failure, corrections, commands and commit boundaries.
