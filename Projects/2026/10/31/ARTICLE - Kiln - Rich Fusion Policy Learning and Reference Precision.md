---
title: "Kiln: Learning Fusion Policies with Explicit Reference Precision"
aliases: [Kiln Rich Fusion Policy Study]
tags: [article, compilers, cuda, optimization, research]
status: active
type: article
created: 2026-10-31
repo: /home/manuel/code/wesen/kiln/worktrees/passnet
ticket: KILN-005
source_revision: b4a4102
selection_revision: 2a4162c
report_revision: fce41a3
---

# Kiln: Learning Fusion Policies with Explicit Reference Precision

Kiln now has a complete reusable-policy experiment over a corpus containing matrix operations, reductions and multiple consumers. Twelve candidate policies compile across twenty source graphs. A selection made from twelve training graphs is committed before timing the eight confirmation graphs. Every graph passes the explicitly declared full-precision FP32 research protocol. The selected threshold measures 1.000568× end-to-end speedup and 0.999585× CUDA-stream elapsed speedup on confirmation. These differences provide no convincing evidence of a performance improvement.

The experiment also exposes a numerical distinction that affects compiler evaluation. The native PyTorch reference permits TF32 on this machine. Two matrix graphs fail comparison even though Kiln agrees closely with FP64 and full-precision PyTorch. The native experiment remains failed. A separate declaration changes the research reference precision while retaining every graph, candidate, tolerance and compiled binary. Understanding this distinction is necessary to interpret both the optimization result and benchmark coverage.

> [!summary]
> This milestone establishes a richer selection/confirmation experiment, an audited distinction between native and full-precision references, and a near-zero optimization result. Original benchmark acceptance remains eleven complete tasks and 206 individually passing graphs. Import eligibility is larger: 1,029 graphs and 51 complete families.

## 1. Define the object being optimized

A compiler pass transforms an intermediate representation, or IR, into another representation with the same required observable behavior. Fusion is one such transformation: a computation that previously produced an intermediate tensor is inserted into its consumers. This can eliminate intermediate memory traffic and GPU launches, but can also duplicate work when there are multiple consumers.

Kiln's existing fusion rule attempts the graph mutation and compares estimated work before and after it. Its default permits a small increase:

\[
W_{after} \leq 1.02 W_{before}.
\]

The policy determines whether this already implemented mutation is profitable. It does not define the legality of a new graph rewrite. In this experiment, candidate programs replace that profitability decision while preserving the existing mutation, compiler pipeline and fixed numerical contract.

For example, scalar105 accepts a proposed mutation when the estimated work after fusion is no more than 1.05 times the estimated work before fusion. A conditional candidate can choose its bound using the number of consumers, the producer's element count or estimated original work. The same candidate applies to every graph; the system does not select a separate kernel implementation for each confirmation example.

The implementation boundary is `createFusionRule` in `packages/kiln/src/std/loop.js`. Its observer records attempted decisions and their features. `integrations/passnet/fusion_policy.mjs` validates a bounded policy grammar, and `compile_policy.mjs` replaces `merge_loop_ops` inside the standard pipeline. The grammar is authored by this Codex session from training evidence. No external PassAgent invocation or newly synthesized graph mutation is claimed.

## 2. Broaden the workload before expanding the compiler algorithm

Earlier experiments exercised a narrow training population. Structural inspection found fourteen fused kernels, no reduction-containing kernels, no multi-consumer kernels and no exact internal duplicates. That evidence limited the value of immediately implementing more elaborate fusion or duplicate-elimination algorithms: the selected workloads could not test their main opportunities.

The new source selector draws from the official training list, excludes exact models used by all 200 evaluation tasks and prior policy corpora, and imposes static resource bounds. It orders tasks deterministically using a declared salt and SHA256. It selects six matrix and six reduction graphs for training, followed by four of each for confirmation, with unique exact models and generated-program hashes.

The resource envelope permits at most two million input elements, eight million elements in an individual generated tensor, sixty-four million generated tensor elements in total, 128 tensor nodes and sixteen million matrix scalar products. The scan is bounded to 4,096 tasks and eight FP32 graph candidates per task. These restrictions define a development population; the result cannot be extrapolated to all PassNet tasks or dtypes.

The first attempt exhausted that scan without filling its reduction quota. Its incomplete directory and log remain archived. Missing LayerNorm import support was a frequent cause. After adding that binding, the same salt, quotas, exclusions and volume bounds select twenty sources after 888 tasks. The successful source membership hash is `f3df1ddadef41f31d9b88ab9953c7c7a2a6cd3bffa75bb830159205b40848ad0`.

The resulting training IR has 34 kernels after default fusion, including eighteen reduction-containing and eleven multi-consumer kernels. Without fusion it has 215 kernels. Exact internal-duplicate analysis still finds no removable groups. This provides concrete justification for studying fusion decisions and less support for prioritizing exact duplicate elimination on this particular population.

## 3. Import LayerNorm through an existing Kiln primitive

Layer normalization computes a mean and variance over a declared trailing shape, normalizes the input, and optionally applies affine weight and bias. For a row containing n values:

\[
\mu=\frac1n\sum_i x_i,\qquad
\sigma^2=\frac1n\sum_i(x_i-\mu)^2,\qquad
y_i=\frac{x_i-\mu}{\sqrt{\sigma^2+\epsilon}}w_i+b_i.
\]

The importer validates that the normalized shape exactly matches a positive static suffix of the input shape. It flattens that suffix into one width dimension, flattens the remaining dimensions into rows, and invokes the existing `N.layer_norm` primitive. It then restores the output shape. Missing affine values become shape-correct ones and zeros. FP16 and BF16 arithmetic widens to FP32 before the result is narrowed back to the declared dtype.

This centralizes the numerical computation in Kiln rather than creating a second normalization implementation in the integration. `fx_norm_ops.py` owns source binding and validation; Kiln owns lowering. Mixed affine precision and tuple outputs containing native normalization statistics remain unsupported.

The fixture boundary contains seven forms across three dtypes, giving 21 compiled programs. Three seeds and random/constant inputs produce 126 CUDA comparisons, all passing. Maximum absolute errors are approximately 4.77e-7 for FP32, 4.88e-4 for FP16 and zero for BF16. Fixtures establish these tested forms, not original benchmark acceptance.

The complete import audit rises to 1,029 graphs and 51 complete eligible families. Acceptance through original replay remains eleven complete tasks and 206 individually passing graphs. A complete task requires every member to pass; successful members of incomplete tasks contribute to the graph count without completing the family. This is why the two percentages differ.

Official PyTorch v2.9.1 API definitions, native source and license are archived with URL and SHA256 provenance in `sources/pytorch/layer-norm`. The integration ports the source operation's shape and binding contract; it does not copy PyTorch's native normalization algorithm.

## 4. Freeze candidates before confirmation evidence

The unchanged and explicit-default controls compile identically on training sources. Their trace contains 260 attempted decisions: 181 accepted and 79 rejected. Twenty rejections have modest estimated work ratios, approximately 1.0264 through 1.1424. Those decisions provide actual opportunities for threshold relaxation.

The frozen set contains twelve policies: unchanged, explicit default 1.02, disabled fusion, scalar bounds 1.00/1.05/1.10/1.25/1.50/2.00, and three conditional policies. Conditional cutoffs are derived from training features: producer size 2,048 elements and original work 1,694,208. The grammar has fixed node/depth limits. Confirmation records do not enter candidate generation.

```text
select sources and split models
    -> compile training controls
    -> derive bounded policies from training traces
    -> freeze policies and measurement procedure
    -> compile and qualify all 240 artifacts
    -> measure training and commit one selection
    -> measure baseline and selected policy on confirmation
```

The compile driver checks committed source bytes and frozen declarations around every candidate. The structural gate requires complete membership, consistent numerical policy, valid artifact hashes and unchanged/default equivalence. Receipts explicitly identify full compilation scope and contraction policy. Equal executable fingerprints share measurements, preventing aliases from being presented as independent performance contrasts.

All 240 programs compile and qualify from revision `b4a4102`. Remote source verification matches compilation snapshot `30aba36209d93331d0da726af45bbdc390a144a4b0cfc4f43d732db6a6dac29a` exactly. No missing, changed or additional source files are observed within the recorded snapshot scope.

## 5. Separate source precision from reference precision

The first native training run completes all twelve graphs, but two unchanged baselines fail. Pegasus has 4,921 mismatches among 10,240 projected values; Opus has 6,893 among 25,088. The maximum absolute differences are 7.24e-5 and 3.95e-5. The selection code raises `ValueError: Unchanged compiler baseline is not qualified` and writes no selection.

The container reports float32 matrix precision `high` and TF32 allowed. TF32 permits a reduced-precision multiplication path for operations whose tensor storage is FP32. Storage dtype alone therefore does not fully specify the native matrix implementation's numerical behavior.

The diagnostic replays the same source graph and inputs against FP64, default native PyTorch and highest-precision PyTorch. It changes reference precision only within the diagnostic and restores the previous setting afterward.

| Comparison | Pegasus maximum absolute error | Opus maximum absolute error |
|---|---:|---:|
| Kiln versus default native reference | 7.24e-5 | 3.95e-5 |
| Kiln versus FP64 | 2.19e-8 | 1.50e-8 |
| Kiln versus highest-precision PyTorch | 2.98e-8 | 3.73e-8 |

These observations show that the failed comparison is not evidence of a less accurate Kiln matrix result on these inputs. They also do not permit rewriting the native experiment's acceptance decision. Benchmark compatibility is defined by the chosen protocol, including its reference behavior.

The separate v5-r2 declaration uses `torch.set_float32_matmul_precision("highest")` for the research reference. It preserves every source, split, candidate, tolerance, timing budget and compiled binary. A hashed wrapper verifies the declaration and checks that TF32 is disabled for this reference before executing measurements. The original v5-r1 training result remains failed and archived. This is an explicit modified FP32 research protocol, not a PassNet reproduction result.

## 6. Measure selection and confirmation

The budget is twenty warmups, one hundred trials and three repeats, with at most two retries when IQR exceeds twenty percent of the median. The harness records synchronized end-to-end latency and CUDA-event stream elapsed time separately. Stream elapsed time can include gaps between launches from the host; it is not an isolated single-kernel instruction measurement.

Selection maximizes the family-balanced geometric mean of end-to-end ratios relative to unchanged Kiln:

\[
S(\pi)=\exp\left(\frac1F\sum_f\frac1{|G_f|}
\sum_{g\in G_f}\log\frac{T_0(g)}{T_\pi(g)}\right).
\]

Each candidate must qualify on every training graph to be eligible, and the baseline must qualify on the complete training membership. Exact ties preserve declaration order, preferring unchanged Kiln. Compile-cost weight is zero in this declaration.

Every training candidate qualifies under the explicit full-precision reference. Scalar105 wins with 1.001319×. Disabled fusion scores 0.174909×, approximately 5.72 times slower. This establishes substantial value for existing fusion on these workloads, but offers little evidence that the chosen threshold improves it.

Selection is committed in `2a4162c` before confirmation GPU timing. The confirmation runner permits only unchanged Kiln and scalar105, with the same reference protocol and budget. All eight confirmation graphs qualify.

| Quantity | Observed result |
|---|---:|
| Training selected end-to-end ratio | 1.001319× |
| Confirmation end-to-end ratio | 1.000568× |
| Confirmation CUDA-stream elapsed ratio | 0.999585× |
| Confirmation failures | 0 / 8 |
| Confirmation artifact fingerprints changed | 8 / 8 |

Per-graph end-to-end ratios range from approximately 0.98765× to 1.00758×, and individual repeat ratios vary more than the aggregate change. A 0.057% aggregate difference on one GPU with three warm repeats does not establish a reliable improvement. The stream metric has the opposite sign. The appropriate conclusion is that this richer threshold/conditional-policy search has not demonstrated a meaningful advantage over the starting compiler.

## 7. Architectural consequences and remaining research

The new operation binding reuses an existing compiler primitive, and the reference-protocol revision lives in a small explicit execution wrapper. Compilation, structural qualification, selection and summarization continue using shared harness components. The experiment does not introduce a parallel evaluator or a second normalization algorithm.

The next intervention should target a transformation whose structure can change beyond a small work-growth bound. Selective producer fusion is a concrete candidate: the current mutation inlines into every consumer, while an alternative could retain the producer for some consumers and fuse only into profitable ones. That requires a precise mutation/lifetime design, semantic validation and evidence of relevant opportunities before measurement. It is proposed work, not implemented functionality.

The result does not close the larger project. Original PassAgent evaluation, remaining operation/layout/dtype support, native reduced-precision compatibility, uniform compiler-release coverage and broader pass synthesis remain open. Exact-model exclusions also do not establish separation between related model architectures. The present held-out result tests eight fresh exact models within a constrained development population.

The hardware is a GB10 DGX Spark with a newer NVIDIA PyTorch/CUDA container, rather than the paper's A30 environment. Original replay uses documented integration extensions, and the eleven-task ledger is cumulative across recorded compiler snapshots. Neither that ledger nor this modified-reference policy study is an exact paper reproduction.

## 8. Evidence and continuation

The repository is `/home/manuel/code/wesen/kiln/worktrees/passnet`. Ticket KILN-005 stores the detailed design, chronological diary, upstream provenance, frozen declarations and raw measurements. The main review sequence is:

- Read design 10 for LayerNorm binding and rich-corpus selection, then scripts 174–183 for the preserved execution sequence.
- Inspect `sources/policy-measurements-v5-r1/train.json` and `selection-attempt.log` for the native failure.
- Compare `sources/rich-matrix-numerics.json` with both reference declarations to understand the precision change.
- Inspect `sources/policy-measurements-v5-r2/selection.json`, its pre-confirmation commit, and `summary.json` for the research result.
- Run script 183 to recheck frozen files, artifact qualification, source verification, reference flags and the selection commitment.

The experiment establishes an auditable route from reusable policy proposals to complete training selection and fresh confirmation. Its measured outcome directs the next compiler experiment toward more expressive transformations while preserving the current default and the unresolved native benchmark failures.
