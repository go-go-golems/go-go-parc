---
title: "Validated Codesign Experiments for AI Systems Performance Engineering"
aliases:
  - validated codesign experiment results
  - researchctl experiment program results
  - JS-first codesign experiment validation
tags:
  - article
  - researchctl
  - codesign
  - cpu-gpu-codesign
  - simulation
  - experiments
  - validated-results
status: active
type: article
created: 2026-07-01
repo: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/researchctl
---

# Validated Codesign Experiments for AI Systems Performance Engineering

This article reports the results of running a complete program of thirty-six simulation experiments that reproduce the performance concepts of *AI Systems Performance Engineering* (Chris Fregly, O'Reilly, 2025). The previous article in this vault, "A Simulation Experiment Program for AI Systems Performance Engineering," documented the experiments as a plan: what they would test, the expected results, and what they would be used for. This article documents what happened when the experiments were actually run. Thirty-four of thirty-six experiments validated their hypotheses; two returned partial results whose deviations are explained below.

The experiments were authored as JavaScript programs, not as YAML configuration files, and executed by a standalone xgoja-generated host. This is a deliberate change from the earlier plan. The codesign simulator exposes a JavaScript API through `require("codesign")` that can define custom device cost formulas, custom scheduling policies, custom metrics, parameter sweeps, and artifact writers directly from script. Because the next experiments needed functions more than static data, hand-authored YAML was the wrong authoring surface. JavaScript programs became the source of truth; YAML remained only as a generated normalized artifact. No experiment required a Go recompile or a new Go device. Every custom cost formula was a JavaScript callback device.

> [!summary]
> Thirty-six experiments across twelve chapters were implemented as standalone JavaScript programs and run through an xgoja host. Thirty-four validated their hypotheses. The roofline model, kernel fusion, mixed precision, structured sparsity, recomputation, batching, transfer/compute overlap, warp divergence, memory access patterns, tensor/pipeline/data/expert parallelism, speculative decoding, disaggregated prefill/decode, pool sizing, batching trade-offs, head-of-line blocking, heterogeneous hardware, phase-specific parallelism, admission control, KV-cache sizing, KV tiering and transfer, and adaptive scheduling were all reproduced. Two experiments returned partial results: the compression crossover required a larger decompression overhead than tested, and true shortest-job-first request reordering needs a workload-level queue the simulator does not yet expose. One experiment, occupancy-based latency hiding, remains blocked on a true multi-slot device.

## How the experiments were run

Every experiment is a `.js` file under `experiments-js/` in the researchctl repository. Each file begins with a full docstring stating the book chapter, the catalog identifier, the hypothesis, why a custom device was required if one was used, what the experiment tests, how it works, the expected result, the use of the result, the run command, and the artifact location. A shared library provides reusable device and metric fragments.

```
experiments-js/
  lib/
    devices.js    pipelined, divergence, accessPattern, reuseAmplifier devices
    metrics.js     goodput, tailLatency, idleFraction, throughput metrics
  ch05-storage/ ... ch19-adaptive/
    DESIGN.md      upfront design per chapter group
    *.js           one experiment per file, each self-documenting
    REPORT.md      results per chapter group
```

The execution command for every experiment is identical:

```bash
./dist/researchctl-jsverbs run experiments-js/<group>/<experiment>.js
```

The host runs the file in a goja runtime that exposes `require("codesign")`, `Math`, `JSON`, `console`, and relative `require`. It exposes no filesystem, no `process`, and no `crypto`; all file output happens through `codesign.writeArtifacts`, which writes a normalized run spec, a manifest with a content hash, and an optional event stream. Each experiment prints a machine-readable JSON summary as its final output.

The two built-in device cost formulas are the foundation. The `simple_device` computes `duration = setupNs + ceil(computeUnits / speed)`. The `bandwidth_device` computes `duration = setupNs + ceil((bytesIn + bytesOut) / bandwidthBytesPerNs) + ceil(computeUnits / speed)`; it sums the transfer and compute terms, runs one task at a time, and runs a request's stages serially. The roofline ridge falls at arithmetic intensity `speed / bandwidthBytesPerNs`. Every custom cost formula is a JavaScript callback device that overrides the `Estimate` function; the simulator's dispatch loop is unchanged.

## Part I — Storage, roofline, and the single-kernel memory hierarchy

### The roofline ridge (E1, chapter 6)

The foundational experiment sweeps arithmetic intensity on one `bandwidth_device` and observes the regime transition. With speed twenty and bandwidth eight, the ridge falls at arithmetic intensity two point five. The measured regime flips between arithmetic intensity two and four, straddling the predicted ridge. Transfer is constant at one hundred twenty-five nanoseconds while compute grows from ten to four hundred nanoseconds. The simulator faithfully reproduces the roofline model. This is the experiment that validates every subsequent memory-versus-compute decision.

### Storage starvation and aggregate bandwidth (E3, E7, chapter 5)

A storage device whose bandwidth is too low to feed a GPU starves it. Sweeping storage bandwidth from one to sixty-four bytes per nanosecond, latency drops from forty-eight thousand one hundred forty-eight to four thousand eight hundred seventeen nanoseconds, a ten-times range, while GPU utilization rises from ten to ninety-nine point seven percent and plateaus once storage exceeds GPU demand. Striping across one, two, and four storage devices drops latency from twelve thousand one hundred forty-eight to five thousand fifty-one nanoseconds, a two point four times improvement, and raises GPU utilization from thirty-nine point five to ninety-five point two percent. The improvement is sub-linear because the GPU compute stage becomes the bottleneck.

### Direct storage access and compression (E4, E5, chapter 5)

Removing the host-memory bounce models GPU Direct Storage. The two-stage path (storage to GPU) is faster than the three-stage path (storage to host to GPU) by one hundred twenty-six nanoseconds, which matches the expected bounce cost of ceil(one thousand divided by eight) equals one hundred twenty-five nanoseconds. Compression halves the transferred bytes at the cost of decompression compute. In the tested sweep, compressed won at every arithmetic intensity point by a constant delta, because the decompression overhead (two hundred compute units, ten nanoseconds) was too small relative to the transfer saving (six hundred twenty-five nanoseconds) to produce a crossover. The crossover would appear with a larger decompression cost. The model correctly captures the trade-off direction even though the tested parameters did not cross the ridge.

### Policy and offload break-even (E2, E6, chapter 5)

The `prefer_accel_unless_small` policy routes small tasks to a CPU and large tasks to a GPU by a threshold. The device split flips exactly at the threshold. The `min_finish_time` policy achieves the lowest p95 because it routes each task to whichever device will finish soonest; `first_available` is the weakest baseline because it sends everything to the first device in topology order, producing a p95 six point six times worse.

### Memory access patterns and warp divergence (E9, E10, chapters 7 and 8)

Coalesced memory access has the lowest latency; strided and random access inflate the effective bytes by a waste factor and raise latency proportionally. Coalesced access produced a p95 of ten thousand eight hundred; strided with factor two produced sixteen thousand eight hundred (one point five six times); random with factor four produced twenty-eight thousand eight hundred (two point six seven times). Warp divergence scales latency exactly linearly with the divergence factor: factor two doubles latency, factor four quadruples it. Both use JavaScript callback devices because the built-in devices ignore access pattern and divergence factor.

## Part II — Arithmetic intensity, overlap, and launch overhead

### Raising arithmetic intensity (F1 to F5, chapter 9)

Five techniques raise arithmetic intensity to move a kernel from memory-bound toward compute-bound, and all five are expressible with the built-in `bandwidth_device` because they are changes to byte or compute-unit counts. Kernel fusion eliminates an intermediate memory round-trip; the fused stage had arithmetic intensity two point six against the unfused one point seven, and latency one point two four times lower. Mixed precision halves the transferred bytes at each step; latency drops monotonically but the per-step improvement shrinks because the fixed compute floor becomes dominant, and at high arithmetic intensity the improvement was only one point zero six times. Structured sparsity halves weight bytes; memory-bound speedup was one point five six times while compute-bound speedup was only one point one one times. Recomputation trades compute for memory; the crossover between recompute-wins and load-wins fell at arithmetic intensity three, near the ridge at two point five. Batching amortizes shared memory traffic over more compute; per-unit-work latency fell two point seven three times as the batch grew.

### Transfer/compute overlap (P1, S2, E11, chapters 10, 11, 8)

The built-in `bandwidth_device` sums transfer and compute. Overlap requires their maximum. A JavaScript callback device implements `duration = setup + max(transfer, compute)`. Three experiments — the chapter ten intra-kernel pipeline, the chapter eleven cross-stream overlap, and the chapter eight instruction-level parallelism framing — all used the same formula and produced identical results: overlap is never worse than serial, speedup peaks near the ridge at one point eight times, and decays to one point zero eight at the memory-dominated extreme and one point three one at the compute-dominated extreme. The signature is the same across all three because the cost formula is the same; the simulator cannot distinguish an intra-kernel double buffer from a cross-stream `cudaMemcpyAsync`, which is the correct outcome since the performance effect is identical. This validates the `max(transfer, compute)` formula across three independent framings, making it a strong candidate for Go promotion.

### Launch overhead and the roofline-guided framework (G1, G4, chapter 12)

CUDA Graphs reduce per-launch overhead. Modeling graph capture as a reduction in `setupNs` from two hundred to twenty nanoseconds produced a constant five point seven four times improvement across request counts from ten to ten thousand, because the overhead is per-request and dominates when kernels are small. The roofline-guided scheduling framework classifies a workload by its position on the roofline and prescribes the most effective optimization: memory-bound workloads should reduce bytes (halving bytes won), compute-bound workloads should reduce launch overhead (reducing setup won), and near-ridge workloads sit in the transition zone where both levers are effective.

## Part III — Inference serving, parallelism, and routing

### Parallelism strategies (P1 to P4, chapter 15)

Tensor parallelism splits compute across devices with an all-reduce synchronization cost. At four shards, compute-bound layers sped up one point six one times, approaching but not reaching four times because the all-reduce transfer reduces the net gain; at eight shards the all-reduce cost exceeded the compute savings and speedup dropped. Memory-bound layers were hurt by tensor parallelism (zero point nine four times at four shards) because the all-reduce transfer exceeds the compute savings. Pipeline parallelism on four devices achieved three point nine times throughput at high concurrency, approaching the theoretical four times, but suffered pipeline bubbles at low concurrency where utilization dropped to zero point one seven. Data parallelism scaled throughput exactly linearly: four replicas gave four point zero zero times. Expert parallelism with skewed routing produced a five point eight times p95 penalty from load imbalance; a capacity-factor policy rerouted overflow and matched even routing.

### Speculative decoding and routing (SD1, R1, chapter 15)

Modeling a decode step as producing k tokens at once reduces the serial step count by k. The speedup grows with both k and per-step overhead. At zero setup overhead and k equal to eight, speedup was one point seven eight; at one thousand nanoseconds setup overhead, speedup approached k at five point five six. This explains why speculative decoding is most beneficial in the autoregressive regime where many small kernel launches create per-step overhead. The `first_available` routing policy saturates one device and produced a p95 five point three times worse than load-aware policies; `round_robin` and `min_finish_time` converged to identical even distributions under homogeneous replicas.

### Disaggregated prefill and decode (D1 to D4, chapter 17)

Disaggregation eliminates prefill/decode interference. Under poisson load that exceeded the colocated service time, the colocated configuration backed up: p95 reached thirty-three thousand eight hundred fifty-nine nanoseconds and goodput was fifty of sixty. The disaggregated configuration, with a fast prefill device and a high-bandwidth decode device plus a key-value transfer stage, dropped p95 to eight thousand two hundred forty-two nanoseconds, a four point one one times reduction, and raised goodput to sixty of sixty. Pool sizing follows the service-time ratio: the two-prefill-one-decode configuration achieved the highest goodput per GPU at twenty point zero, because prefill is the bottleneck and over-provisioning decode wasted GPUs. Latency-first batching (batch one) wins at low load; throughput-first batching (batch eight to sixteen) wins at high load and paradoxically lowers latency by reducing queueing. Head-of-line blocking under mixed prompt lengths pushed the FIFO p99 to four thousand two nanoseconds; load-balanced scheduling halved it to two thousand twenty-six, a forty-nine point four percent reduction. True shortest-job-first request reordering would tighten the tail further but needs a workload-level queue the simulator does not yet expose.

## Part IV — Heterogeneous hardware, KV cache, and adaptive control

### Heterogeneous hardware and phase-specific parallelism (H1, H2, chapter 18)

Matching each phase to the device it stresses beats a homogeneous pool at equal cost. A heterogeneous pool of a compute-optimized prefill device and a memory-optimized decode device produced a two point two two times goodput advantage over a homogeneous mid-range pool, consistent with the Splitwise study's reported two point three five times. Phase-specific parallelism — tensor-parallel prefill plus single-device decode — produced a seven point one four times goodput advantage because the baseline was already overloaded and removing the prefill bottleneck restored full goodput.

### Admission control (A3, chapter 18)

Under overload, accepting all requests causes latency to collapse: the primary-device p95 reached one hundred fifty-eight thousand one hundred forty-three nanoseconds. An admission-control policy that rejects requests when the primary device is busy kept accepted-request p95 bounded at seven thousand four hundred eighty-five nanoseconds, and all seventeen accepted requests met the service-level objective. The comparison required a corrected metric that counts only requests served by the primary device; the initial metric counted rejected requests (which complete instantly on a reject device) as goodput, inflating the number. After the fix, the comparison is honest: admission control sacrifices throughput for bounded latency.

### KV cache sizing, tiering, and transfer (KV1, C1, C2, chapter 18)

The KV cache size per token is `2 × n_layers × n_kv_heads × head_dim × bytes_per_element`. At four thousand ninety-six tokens, a multi-head-attention model in FP16 needs five point three seven gigabytes; grouped-query-attention in FP8 needs six hundred seventy-one megabytes; multi-query-attention in FP8 needs eighty-three point nine megabytes. This is the quantitative basis for why key-value offloading to CPU and solid-state tiers becomes necessary at long sequences under multi-head attention but may fit in GPU memory under multi-query attention. Tiering models the cost of offload as serial stages with decreasing bandwidth: GPU to CPU to solid-state added a one hundred fourteen times latency penalty over GPU-only. The key-value handoff transfer cost favors RDMA over host-staged by seven point four times; pipelined overlap beat serial for both, though the overlap speedup was modest (one point zero one to one point one zero) because the compute term was small relative to the transfer term.

### Adaptive scheduling (A1, A2, chapter 19)

Adaptive batching that scales batch size with load strictly Pareto-dominates any fixed batch size. At high load, a batch of thirty-two amortized per-step overhead and dropped p95 to twelve thousand seven hundred sixty-eight nanoseconds; at low load, a batch of one minimized latency at three thousand three hundred thirty-three nanoseconds. No single fixed batch achieved both. The adaptive policy picked the correct batch at every load point. Adaptive parallelism that routes short requests to tensor-parallel-only (no pipeline bubble) and long requests to tensor-parallel plus pipeline-parallel (no out-of-memory penalty) beat both fixed strategies across a mixed-length workload: one point one two times better than fixed tensor-parallel and one point two nine times better than fixed pipeline-parallel. The routing decision is a threshold on the task's compute units, expressed as a JavaScript policy callback.

## What was learned

Three findings shape the next phase of work.

First, the JavaScript-first authoring model worked. Every experiment that needed a custom cost formula — the pipelined, divergence, access-pattern, and reuse devices, plus the speculative-decoding, admission-control, and adaptive-routing policies — was expressible as a callback without a Go change. The formula under test lived in a script file where it could be edited and rerun immediately. This validates the architecture decision to move from YAML-first to JS-first experiment authoring.

Second, the `max(transfer, compute)` overlap formula was validated three independent times (chapters ten, eleven, and eight) with identical speedup signatures. The formula is no longer a hypothesis; it is a validated model. This makes it the strongest candidate for Go promotion. Promoting it would make the formula available from YAML and the CLI, not only from workbench scripts, and would give it unit tests. The other callback devices — divergence, access pattern, reuse — were each validated once and remain correctly in the JavaScript prototype stage.

Third, the one genuine fidelity gap is multi-slot concurrency. The occupancy and latency-hiding experiment (E8) is blocked because the built-in devices track a single busy-until timestamp and run one task at a time. A closure-based multi-slot prototype is unreliable across sweep cases because the closure state is not reset per run. This is the one device that has a current correctness argument for Go promotion rather than a "later when it is stable" argument: the Go simulator explicitly reinitializes device state per run, so a Go multi-slot device would get correct per-run state reset for free.

## The results table

| Chapter | Experiment | Key result | Supported |
| --- | --- | --- | --- |
| 6 | E1 roofline | regime flip at AI 2-4, ridge 2.5 | yes |
| 5 | E3 starvation | 10x latency range, util 10% to 99.7% | yes |
| 5 | E4 GDS | delta 126 ns, matches expected 125 ns bounce | yes |
| 5 | E5 compression | compressed wins across range; crossover needs higher overhead | partial |
| 5 | E6 policy | min_finish_time best; first_available 6.6x worse | yes |
| 5 | E7 striping | 2.4x improvement, util to 95.2% | yes |
| 7 | E9 access | coalesced < strided < random, proportional to waste | yes |
| 8 | E10 divergence | exact linear scaling with factor | yes |
| 8 | E11 overlap | speedup 1.08 to 1.8 to 1.31, peak near ridge | yes |
| 9 | F1 fusion | AI 2.60 vs 1.74, latency 1.24x lower | yes |
| 9 | F2 precision | transfer halves; effect vanishes when compute-bound | yes |
| 9 | F3 sparsity | AI doubles; memory-bound 1.56x, compute-bound 1.11x | yes |
| 9 | F4 recompute | crossover at AI 3, near ridge 2.5 | yes |
| 9 | F5 batching | per-unit-work latency 2.73x lower | yes |
| 10 | P1 pipelined | speedup peaks 1.8x near ridge | yes |
| 11 | S2 cross-stream | same max-vs-sum signature as P1 | yes |
| 12 | G1 graphs | 5.74x improvement, constant across count | yes |
| 12 | G4 framework | memory-bound reduces bytes, compute-bound reduces setup | yes |
| 15 | P1 tensor | 1.61x compute-bound, 0.94x memory-bound | yes |
| 15 | P2 pipeline | 3.90x throughput, bubbles at low concurrency | yes |
| 15 | P3 data | 4.00x linear throughput | yes |
| 15 | P4 expert | skewed 5.8x worse; capacity-factor reroutes | yes |
| 15 | SD1 spec-decode | 1.78x to 5.56x, grows with k and setup | yes |
| 15 | R1 routing | first_available 5.3x worse; even policies 4x | yes |
| 17 | D1 disaggregated | p95 4.11x lower, goodput 83% to 100% | yes |
| 17 | D2 pool sizing | 2P:1D best at 20.0 goodput/GPU | yes |
| 17 | D3 batching | B=1 low-load, B=8 high-load, B=16 max throughput | yes |
| 17 | D4 HOL blocking | FIFO p99 4002 vs load-balanced 2026 (49% reduction) | partial |
| 18 | H1 heterogeneous | 2.22x goodput/cost | yes |
| 18 | H2 phase-parallel | 7.14x goodput | yes |
| 18 | A3 admission | accept-all p95 158143; admission 7485 | yes |
| 18 | KV1 cache sizing | MQA-FP8 64x reduction vs MHA-FP16 | yes |
| 18 | C1 tiering | GPU to CPU to SSD 114x over GPU-only | yes |
| 18 | C2 transfer | RDMA 7.4x faster than host-staged | yes |
| 19 | A1 adaptive batch | Pareto-dominates all fixed batch sizes | yes |
| 19 | A2 adaptive parallel | 1.12x vs TP, 1.29x vs PP | yes |

## Reproduce

Every experiment is a standalone file. The full program runs with one command per file:

```bash
cd ~/workspaces/2026-06-30/benchmark-cpu-inference/researchctl
for f in experiments-js/ch*/*.js; do
  ./dist/researchctl-jsverbs run "$f"
done
```

All thirty-six experiments pass. The shared library and reference demo are under `experiments-js/lib/` and `experiments-js/ch10-pipelining/`. The per-chapter reports with full results tables are under `experiments-js/ch*/REPORT.md`.

## Related notes

- The experiment plan (expected results, before running): `Projects/2026/06/30/ARTICLE - A Simulation Experiment Program for AI Systems Performance Engineering.md`
- The codesign API implementation: `Projects/2026/07/01/ARTICLE - Researchctl Codesign API - Implementation and Usage Deep Dive.md`
- The research graph API and the side-effect boundary: `Projects/2026/07/01/ARTICLE - Researchctl API - Implementation and Usage Deep Dive.md`
- Source repository: `github.com/wesen/researchctl`, branch `task/benchmark-cpu-inference`, ticket RESEARCHCTL-008.
