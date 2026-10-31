---
title: "Kiln: A Reusable Fusion Policy Selected on Training Graphs"
aliases: [Kiln First Fusion Policy Optimization Result]
tags: [article, compilers, cuda, optimization, research]
status: active
type: article
created: 2026-10-30
repo: /home/manuel/code/wesen/kiln/worktrees/passnet
ticket: KILN-005
source_revision: 7ce40f6
---

# Kiln: A Reusable Fusion Policy Selected on Training Graphs

The first controlled compiler-policy experiment selected a fusion threshold using training measurements, applied it unchanged to a separate set of graph families, and measured a positive transfer result. The selected threshold produced a family-balanced end-to-end speedup of **1.0186× relative to unchanged Kiln** on seven held-out FP32 graphs. One executable changed and measured **1.1589×** speedup; the other six were identical to their baseline executables.

This is a small development study on one GB10 GPU. It establishes a working sequence from policy proposal through compilation, correctness, training-only selection and held-out evaluation. It does not establish a new rewriting algorithm, a globally optimal fusion threshold, or performance across the complete PassBench corpus.

> [!summary]
> The selected maximum work-growth ratio is 1.25, compared with Kiln's default 1.02. Training used three graphs from two families; held-out evaluation used seven graphs from four distinct families. All replay correctness checks passed, followed by 60 domain-valid random-input comparisons. The global default remains unchanged; the selected policy is explicit and its complete evidence is committed.

## 1. Make the compiler policy the object of optimization

Fusion combines computations into fewer kernels. A producer computes a tensor consumed by another operation. Materializing that tensor requires a kernel launch, storage and subsequent reads. Inlining the producer into its consumer can eliminate those costs, but can also repeat arithmetic or increase the resources used by the resulting kernel.

Kiln's existing `mergeLoopOps` rule already separates eligibility from profitability. Its matcher excludes graph outputs and requires loop-kernel consumers. Its mutation inlines a producer into those consumers. Its guard estimates work before and after the transformation and accepts when:

$$
W_{\mathrm{after}}\leq1.02W_{\mathrm{before}}.
$$

The estimate is computed from scheduled loops. Reads and writes have weight 12; arithmetic uses the corresponding scalar function's estimated flop cost. These are weighted cost units, not a measurement of elapsed time or a count of FLOPs alone. The guard has no explicit term for the fixed cost of launching an additional kernel through the runtime.

The experiment preserves the matcher and mutation and exposes the profitability decision through `createFusionRule`. The factory receives a maximum work-growth ratio or a decision callback, plus an optional observer. A callback sees immutable scalar features: original work, fused work, consumer count and producer element count. It does not receive runtime tensor values.

Given a fixed target, the selected compiler variant is constructed through the existing pipeline API:

```javascript
const baseline = std.emmy.pipeline({ target });
const selected = baseline.replaceRule(
  "loop/fusion",
  "merge_loop_ops",
  std.loop.createFusionRule({ maxWorkGrowth: 1.25 })
);
```

The ordinary `mergeLoopOps` export is created with the original default settings. Its behavior was checked against a separately constructed default factory and then against complete compiled artifacts. Ten real programs produced identical default and unchanged executable bodies. The experiment therefore changes an explicit compiler variant rather than silently changing the reference compiler.

## 2. Establish a useful structural contrast before timing

A parameter search can produce no useful information if every candidate generates the same program. The first check is therefore structural: compile the proposed policies and compare their executable artifacts before spending a timing budget.

The declared controls were unchanged Kiln and thresholds 0, 1, 1.02, 1.25 and 2. A threshold of zero acts as a disabled-fusion control for these positive-work candidates. The strict and default thresholds produced baseline-equivalent programs. The relaxed thresholds changed a normalization computation from two kernels to one in the training set.

The first frozen corpus contained seven graphs. Although it exposed that training contrast, neither relaxed threshold changed any held-out executable. Such a set can detect a regression but offers no opportunity to demonstrate a speed gain from the intervention. Before any candidate timing, a second corpus version added distinct normalization families to the held-out set. Both manifests and the first preflight remain archived.

The final split contains ten FP32 graphs:

| Role | Graphs | Task families | Representative source models |
|---|---:|---:|---|
| Training | 3 | 2 | LINKX, MobileOne, RepVGG |
| Held-out | 7 | 4 | Nystromformer, GhostNet, RepViT, RepGhostNet |

Graph selection deduplicates generated programs and takes minimum and maximum eligible input volume per family, with a 20-million-input-element limit. All variants of a selected task family stay on one side. Source-model identities do not overlap between training and held-out sets. The expanded manifest's membership hash is `7bf086a3e2968974db811a38283e95471e711d6b670f0a8dcb56aed2e495dcbf`.

These tasks were drawn from the published evaluation list and had partly been observed during integration. The corpus is a curated development set, with held-out policy-search timing feedback. It is not an untouched or randomly representative sample of the paper's evaluation distribution. A later confirmation must reserve a new evaluation protocol rather than reuse these observations as blind evidence.

## 3. Preserve executable and correctness identity

Each policy was compiled over all ten graphs, producing 60 compilation records. A record includes source hash, policy identity, kernel identities, a full executable fingerprint, guard decisions, compile/reference/export time and internal reference-check outcome.

Qualification checks the actual artifact body as well as the receipt. The configurable default must match unchanged Kiln after removing only descriptive name/source/policy metadata. Each artifact file receives a SHA256, and the measurement runner verifies those bytes before loading the program. This prevents a stale receipt from silently describing a different executable.

Synthetic compiler checks need inputs in the source operation's domain. Batch normalization's running variance is therefore made positive in the internal reference fixture through `abs(value)+0.1`. A source-derived sidecar identifies that input through FX references, including aliases. The same separately hashed sidecar applies to every compiler policy. GPU correctness uses the original PassBench replay inputs and trusted source model, not those synthetic compiler fixtures.

Before timing, the direct runner compares every output's structure, shape, dtype and numerical values against the source model. It also verifies that inputs have not changed. Programs with identical executable fingerprints share one correctness/timing record. Their policy names do not cause separate executions to compete on measurement noise.

## 4. Select from training feedback only

The measurement plan was frozen before timing: 20 warmups, 100 trials and three repeats. Each repeat uses a seeded shuffle of the distinct executables for that graph. A measurement is retried at most twice when either metric's IQR exceeds 20% of its median. Raw samples, retries and per-repeat summaries are retained.

Two metrics are recorded separately. Synchronized end-to-end time includes output and scratch allocation, launch and final synchronization. CUDA-event stream elapsed time includes dispatch gaps and must not be interpreted as pure device-kernel duration. JavaScript compilation/reference/export cost and CUDA program-load cost are separate fields; the first selection objective assigns compilation cost coefficient zero.

Scheduling uses the existing A100 cost-model proxy while NVRTC compiles for the actual GB10 architecture. Both variants use the same scheduling configuration. This is not an A30 reproduction or a native GB10 cost-model claim.

The selector computes speedup relative to unchanged Kiln. It averages log speedup within each family, then averages families equally:

$$
S(\phi)=\exp\left(\frac{1}{F}\sum_{f=1}^{F}
\frac{1}{N_f}\sum_{i\in f}\log\frac{T_0(i)}{T_\phi(i)}\right).
$$

Equal family weighting prevents a family with many shape variants from dominating through its size. A correctness or persistent stability failure makes a candidate ineligible. The selector rejects incomplete membership, an altered candidate list and held-out rows in its input.

Training chose threshold 1.25:

| Candidate | Training family-balanced end-to-end speedup |
|---|---:|
| 1.25 | 1.117468× |
| 2.0 | 1.117468× |
| Unchanged / 1.0 / 1.02 | 1.000000× |
| Disabled fusion | 0.322675× |

Thresholds 1.25 and 2 generated identical executables on this corpus, so they share measurements. The predeclared order resolves their exact tie in favor of the lower threshold. This establishes the best tested choice in a small grid; it does not prove that 1.25 is optimal. Untested values between 1.02 and 1.25 may produce equal or better decisions.

The selected policy and all training evidence were committed as `575effd` before held-out timing started. The held-out runner requires that selection record and measures only unchanged Kiln and the selected policy. It does not run the candidate grid on held-out timing.

```mermaid
flowchart LR
    A[Frozen corpus and controls] --> B[Compile and verify identity]
    B --> C[Training correctness and timing]
    C --> D[Training-only selection]
    D --> E[Commit selected policy]
    E --> F[Held-out baseline and selected policy]
    F --> G[Post-selection numerical stress]
```

## 5. Follow the changed held-out program

The affected RepViT graph adds two tensors of shape `[32,384,8,8]`, computes their spatial mean to obtain `[32,384]`, applies inference batch normalization, and returns both the normalized result and the pooled values. The normalization statistics and affine parameters are channel vectors of length 384.

Unchanged Kiln emits three kernels:

1. A channel-only normalization intermediate with shape `[1,384]`.
2. The residual addition and spatial mean, producing `[32,384]`.
3. The final normalized output, consuming the intermediate and pooled result.

The selected policy keeps the pooling kernel and incorporates the channel-only computation into the final normalization kernel. It produces two kernels and removes an intermediate buffer. The same reusable threshold is applied across every graph; there is no RepViT task identifier or shape-specific dispatch condition in the policy.

The original guard rejected transformations with weighted-work ratios around 1.047–1.061 in this case. The selected threshold admits them. In the training LINKX normalization, related rejected ratios were around 1.060–1.075. The repeated computation increases the proxy's work while reducing launches and intermediate storage.

The measurements are:

| Metric | Unchanged Kiln | Selected policy |
|---|---:|---:|
| Kernel count | 3 | 2 |
| Median synchronized end-to-end time | 0.0362335 ms | 0.0312650 ms |
| End-to-end speedup | 1.0000× | 1.1589× |
| CUDA stream elapsed speedup | 1.0000× | 1.1746× |

The three paired repeat speedup ratios were 1.1523, 1.1595 and 1.1546. Within-repeat end-to-end IQR fractions were approximately 0.9–1.4%. The consistent repeat direction is useful exploratory evidence, but three warm repeats are not strong statistical confidence or an independent replication.

The other six held-out executables were identical to their baseline counterparts. They provide correctness and identity controls, not six independent demonstrations of speedup. Across all four families, the family-balanced end-to-end score is **1.018607×** and the stream-elapsed score is **1.020316×**.

The small aggregate follows directly from the weighting. The changed RepViT family has two graphs, only one of which changes, and is one of four equally weighted families. With all other ratios equal to one, the aggregate is approximately `1.1589^(1/8)`, or 1.0186. Reporting only the changed program would overstate the corpus-level effect.

This experiment does not isolate the separate contributions of launch removal, allocation, memory traffic and changed arithmetic. Their combined effect is measured through the fixed runtime. A later profiler study can separate those costs.

## 6. Check more than the replay distribution

The earlier convolution integration passed its original replay inputs while retaining failures on broader random inputs. That experience motivates an additional check after policy selection.

The selected policy remained fixed while unchanged and selected programs were compared on seeded random FP32 inputs for all ten graphs. Running variances satisfied the source-derived positivity constraint. Seeds 1, 7 and 42 produced 60 graph/policy/seed comparisons, all of which passed. The maximum output error was `3.814697265625e-06` with FP32 rtol 1.3e-6 and atol 1e-5. Inputs were also checked for unintended mutation.

These checks support the numerical validity of this specific intervention on the declared corpus. They do not prove arbitrary-input equivalence, resolve the earlier low-precision convolution limitation, or establish FP16/BF16 performance. No policy was retuned using the stress or held-out result.

## 7. Interpret the milestone at its actual scope

The compiler-policy experiment has now completed a full automated sequence: construct candidates, compile them, verify correctness, measure training performance, choose one reusable policy and evaluate it unchanged on held-out graph families. It demonstrates transfer of a scalar profitability choice from a LINKX normalization workload to a different RepViT residual/mean/normalization pattern on GB10.

It is automated parameter tuning. LLM-generated feature-dependent decision programs, new rewriting algorithms and comparisons against per-task kernel synthesis remain future work. The global threshold remains 1.02 because this development study is too small to justify changing behavior across every program. Users of the experiment can apply the selected 1.25 rule explicitly through the pipeline API.

This result also does not change official PassBench coverage. Five complete tasks containing 73 graph variants remain verified through the declared integration protocol. The direct policy study uses selected FP32 variants and does not add complete accepted tasks or produce the paper's aggregate score. Import coverage remains a separate count: 804 translatable graphs across 24 completely translatable tasks.

The next research step is a richer policy family using immutable compiler features, with a new reserved confirmation set and an equal search budget. The current held-out observations should become development knowledge rather than being repeatedly reused to claim unseen generalization. Full compiler coverage and the unchanged PassNet reproduction continue as separate tracks.

## 8. Evidence and reproduction

The implementation is in `/home/manuel/code/wesen/kiln/worktrees/passnet`, ticket KILN-005. The policy API and frozen protocol were committed as `7a20a9b`, training selection as `575effd`, and held-out/stress evidence as `7ce40f6`.

The main artifacts are under the ticket's `sources/policy-corpus-v2`, `sources/policy-artifacts-v2` and `sources/policy-measurements-v1` directories. `selection.json` records the chosen candidate; `train.json` and `heldout.json` retain raw measurements; `stress.json` preserves all seeded comparisons; `summary.json` and `verified-facts.json` record the checked outcome.

The shared implementation consists of `compile_policy.mjs`, `measure_policy.py`, `select_policy.py`, `summarize_policy.py` and `stress_policy.py` under `integrations/passnet`. Numbered scripts 69–79 preserve corpus construction, control compilation, isolation, selection, held-out execution and verification. Scripts 77 and 79 reproduce the result accounting from saved evidence.

The broader integration architecture and limitations are explained in [[ARTICLE - PassNet and Kiln - Compiler Integration and the Self-Optimization Experiment]]. This milestone supplies the first measured reusable-policy result anticipated by that report.
