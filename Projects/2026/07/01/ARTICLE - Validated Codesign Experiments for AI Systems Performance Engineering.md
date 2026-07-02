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
  - literate-programming
status: active
type: article
created: 2026-07-01
repo: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/researchctl
---

# Validated Codesign Experiments for AI Systems Performance Engineering

This article reports the results of running thirty-six simulation experiments that reproduce the performance concepts of *AI Systems Performance Engineering* (Chris Fregly, O'Reilly, 2025), and it does so in a literate style: the important parts of the code that produced each result are woven into the prose, with the codesign JavaScript API explained as it is used. The previous article in this vault documented the experiments as a plan. This one documents what the code looks like and what happened when it ran. Thirty-four of thirty-six experiments validated their hypotheses.

The experiments are authored as JavaScript programs, not as YAML configuration, and executed by a standalone xgoja-generated host. The codesign simulator exposes a JavaScript API through `require("codesign")` that defines custom device cost formulas, scheduling policies, metrics, sweeps, and artifact writers directly from script. Because the experiments needed functions more than static data, hand-authored YAML was the wrong surface. No experiment required a Go recompile. Every custom cost formula is a JavaScript callback device.

## How to run an experiment

Every experiment is a `.js` file under `experiments-js/`. The execution command is identical for all thirty-six:

```bash
./dist/researchctl-jsverbs run experiments-js/<group>/<experiment>.js
```

The host runs the file in a goja runtime that exposes `require("codesign")`, `Math`, `JSON`, `console`, and relative `require`. It exposes no filesystem, no `process`, and no `crypto`. All file output happens through `codesign.writeArtifacts`, which writes a normalized run spec, a manifest with a content hash, and an optional event stream. Each experiment prints a machine-readable JSON summary as its final output, prefixed by a timestamp.

## The two built-in device formulas

Two Go devices carry the weight of the program. Their cost formulas are the foundation every experiment builds on.

The `simple_device` is compute-only:

```
duration = setupNs + ceil(computeUnits / speed)
```

The `bandwidth_device` separates transfer from compute:

```
transfer = ceil((bytesIn + bytesOut) / bandwidthBytesPerNs)
compute  = ceil(computeUnits / speed)
duration = setupNs + transfer + compute
```

The transfer and compute terms are summed, not overlapped. The device runs one task at a time (a single `BusyUntilNS`), and a request's stages run serially. The roofline ridge falls at arithmetic intensity `speed / bandwidthBytesPerNs`. This single formula, swept over `computeUnits` against fixed `bytesIn`, is the experiment that validates every subsequent memory-versus-compute decision.

## The fluent builder

Every run is built the same way: a `runSpec` builder with scoped callbacks for topology, workload, policy, and metrics. The scoped callbacks keep each part's vocabulary local — topology methods only appear inside the topology callback, workload methods only inside the workload callback. The roofline sweep (E1, chapter 6) is the minimal example:

```javascript
function buildRun(computeUnits) {
  return codesign.runSpec(`roofline AI=${computeUnits / BYTES_IN}`)
    .experiment(EXPERIMENT_ID)
    .backend("cpu-sim")
    .topology(t => t.bandwidthDevice("gpu0", {
      speed: SPEED, bandwidthBytesPerNs: BANDWIDTH, setupNs: SETUP_NS,
    }))
    .workload(w => w
      .fixed({ count: COUNT, interarrivalNs: 0 })
      .stage("infer", {
        computeUnits,
        bytesIn: BYTES_IN,
        supportedDevices: ["gpu0"],
      }))
    .policy("first_available")
    .metrics(m => m.latencyP95("lat").tasksByDevice("tbd"));
}
```

The interesting part is that the run is parameterized by `computeUnits`, so one builder function produces a whole sweep by calling it in a loop. The experiment runs each point, records p95, and classifies the regime analytically from the same formula the device uses:

```javascript
const transfer = Math.ceil(BYTES_IN / BANDWIDTH);
const compute = Math.ceil(cu / SPEED);
const regime = transfer > compute ? "memory-bound" : "compute-bound";
```

With speed twenty and bandwidth eight, the ridge falls at arithmetic intensity two point five. The measured regime flips between intensity two and four, straddling the predicted ridge. Transfer is constant at one hundred twenty-five nanoseconds while compute grows from ten to four hundred nanoseconds. The simulator faithfully reproduces the roofline model.

## Multi-stage serial pipelines and device pinning

A request's stages run serially, and each stage can be pinned to a specific device through `supportedDevices`. This is how a storage-to-GPU pipeline is expressed. The storage starvation experiment (E3, chapter 5) builds a two-device, two-stage pipeline:

```javascript
.topology(t => t
  .bandwidthDevice("storage0", { speed: 1, bandwidthBytesPerNs: storageBw, setupNs: 0 })
  .bandwidthDevice("gpu0", { speed: GPU_SPEED, bandwidthBytesPerNs: GPU_BW, setupNs: 0 }))
.workload(w => w
  .fixed({ count: COUNT, interarrivalNs: 0 })
  .stage("load", { computeUnits: 1, bytesIn: BYTES_IN, supportedDevices: ["storage0"] })
  .stage("infer", { computeUnits: COMPUTE_UNITS, bytesIn: 0, supportedDevices: ["gpu0"] }))
```

The `load` stage is pinned to `storage0` and the `infer` stage to `gpu0`. Sweeping `storageBw` from one to sixty-four, latency drops from forty-eight thousand one hundred forty-eight to four thousand eight hundred seventeen nanoseconds, a ten-times range, while GPU utilization rises from ten to ninety-nine point seven percent and plateaus once storage exceeds GPU demand. This is the storage-starvation effect: a bandwidth-starved storage device cannot keep the compute device busy.

The GPU Direct Storage experiment (E4) uses the same stage-pinning mechanism to compare a three-stage path (storage to host to GPU) against a two-stage path (storage to GPU). The difference is exactly the host bounce:

```javascript
// without GDS: load(storage0) → bounce(host0) → infer(gpu0)
.stage("load",   { computeUnits: 1, bytesIn: BYTES_IN, supportedDevices: ["storage0"] })
.stage("bounce", { computeUnits: 1, bytesIn: BYTES_IN, supportedDevices: ["host0"] })
.stage("infer",  { computeUnits: COMPUTE_UNITS, bytesIn: 0, supportedDevices: ["gpu0"] })
// with GDS: load(storage0) → infer(gpu0)  — the bounce stage is removed
```

The measured delta was one hundred twenty-six nanoseconds, matching the expected bounce cost of `ceil(1000 / 8) = 125` nanoseconds. Removing a serial stage removes exactly that stage's transfer cost from the path.

## Policy selection and the offload break-even

The four built-in policies are selected by string and, where needed, configured with an object. The offload break-even experiment (E2) uses `prefer_accel_unless_small` with a threshold:

```javascript
.policy("prefer_accel_unless_small", { threshold })
```

This policy routes tasks below the threshold to a CPU and above to a GPU. Sweeping `computeUnits` against a fixed threshold of two thousand, `tasks_by_device` flips from all-CPU to all-GPU exactly at the threshold. The CPU has no launch overhead; the GPU has `setupNs=500`, so small tasks are faster on the CPU and large tasks on the GPU. The break-even is the point where the GPU's compute advantage overcomes its setup cost.

The policy comparison experiment (E6) runs the same topology and workload under all four policies. The result ranks them by p95: `min_finish_time` is best because it routes each task to whichever device finishes soonest; `first_available` is worst because it sends everything to the first device in topology order, producing a p95 six point six times worse. `min_finish_time` wins because it uses the same cost model as the devices — it asks each device for an estimate and picks the minimum finish time.

## Striping and multi-device load balancing

The striping experiment (E7) builds a variable number of storage devices and uses `min_finish_time` to spread load tasks across them. The topology callback can build devices in a loop:

```javascript
.topology(t => {
  t.bandwidthDevice("gpu0", { speed: GPU_SPEED, bandwidthBytesPerNs: GPU_BW, setupNs: 0 });
  for (const sid of storageIds) {
    t.bandwidthDevice(sid, { speed: 1, bandwidthBytesPerNs: STORAGE_BW, setupNs: 0 });
  }
})
```

The `load` stage lists all storage devices as `supportedDevices`, so `min_finish_time` routes each load to the earliest-finishing storage device. With one, two, and four storage devices, latency drops from twelve thousand one hundred forty-eight to five thousand fifty-one nanoseconds (a two point four times improvement) and GPU utilization rises from thirty-nine point five to ninety-five point two percent. The improvement is sub-linear because the GPU compute stage becomes the bottleneck.

## The shared device library: custom cost formulas as callback devices

The built-in devices cannot express overlap, divergence, access-pattern waste, or multicast reuse, because those are functions of stage metadata the built-in formulas ignore. The shared library `experiments-js/lib/devices.js` defines each as a JavaScript callback device through `codesign.jsDevice(id, callback, config)`. The callback receives the task, the simulator state, and a fallback estimate, and returns an estimate object. Every fragment returns a topology-builder function suitable for `.use(...)`.

### Transfer/compute overlap: the pipelined device

The highest-leverage custom formula is the overlap model. The built-in sums transfer and compute; overlap takes their maximum. This is the formula for chapter ten's intra-kernel double buffering, chapter eleven's cross-stream overlap, and chapter eight's instruction-level parallelism:

```javascript
function pipelinedDevice(id, cfg) {
  const speed = cfg.speed;
  const bandwidthBytesPerNs = cfg.bandwidthBytesPerNs;
  const setupNs = cfg.setupNs || 0;
  return t => t.jsDevice(id, (phase, task, state, fallback) => {
    const transfer = Math.ceil((task.bytesIn + task.bytesOut) / bandwidthBytesPerNs);
    const compute = Math.ceil(task.computeUnits / speed);
    const duration = setupNs + Math.max(transfer, compute);
    return {
      startNs: fallback.startNs,
      durationNs: duration,
      finishNs: fallback.startNs + duration,
      score: fallback.startNs + duration,
    };
  }, cfg);
}
```

The `fallback` argument is the device's own built-in estimate computed from its config (`speed`, `setupNs`); the callback uses `fallback.startNs` so the single-slot busy-until semantics are preserved, and only overrides the duration. If the callback returned nothing valid, the fallback estimate would be used — a safe degradation.

An experiment uses the fragment by passing it to `.use(...)` on the topology builder:

```javascript
.topology(t => t.use(pipelinedDevice("pipe0", {
  speed: SPEED, bandwidthBytesPerNs: BANDWIDTH, setupNs: SETUP_NS,
})))
```

The canonical experiment (P1, chapter 10) sweeps the transfer/compute balance and compares the serial `bandwidth_device` against the pipelined callback. The result is the overlap signature: overlap is never worse than serial (because `max ≤ sum` always holds), and the speedup peaks near the ridge where transfer and compute are balanced.

| AI | Serial p95 | Pipelined p95 | Speedup |
| --- | --- | --- | --- |
| 0.2 | 6480 | 6000 | 1.08 |
| 2.0 | 10800 | 6000 | 1.80 |
| 8.0 | 25200 | 19200 | 1.31 |

The speedup rises from one point zero eight (memory-dominated) to one point eight (near the ridge at two point five) then falls to one point three one (compute-dominated). This same formula was validated three independent times — the chapter ten pipeline, the chapter eleven cross-stream overlap, and the chapter eight instruction-level-parallelism framing — each producing the identical signature. The simulator cannot distinguish an intra-kernel double buffer from a cross-stream `cudaMemcpyAsync`, which is the correct outcome since the performance effect is identical. This makes `max(transfer, compute)` the strongest candidate for promotion to a Go device.

### Warp divergence: inflating compute by a factor

The divergence device reads a factor from the stage metadata the simulator copies into `task.config`, and multiplies the compute by it:

```javascript
return t => t.jsDevice(id, (phase, task, state, fallback) => {
  const factor = (task.config && task.config.divergenceFactor) || 1;
  const effectiveCompute = task.computeUnits * factor;
  const duration = setupNs + Math.ceil(effectiveCompute / speed);
  ...
```

The experiment passes the factor as stage metadata:

```javascript
.stage("infer", {
  computeUnits: COMPUTE_UNITS,
  supportedDevices: ["div0"],
  divergenceFactor,   // copied into task.config by the simulator
})
```

The result is exact linear scaling: factor two doubles latency, factor four quadruples it. A fifty-fifty if-else branch corresponds to factor two, which halves throughput.

### Memory access patterns: inflating bytes by a waste factor

The access-pattern device inflates the transferred bytes by a waste factor derived from the pattern. Coalesced access has waste one; strided access wastes proportionally to the stride; random access wastes more:

```javascript
const waste = pattern === "random" ? randomFactor
  : pattern === "strided" ? Math.max(1, stride)
  : 1;
const effectiveBytes = (task.bytesIn + task.bytesOut) * waste;
const transfer = Math.ceil(effectiveBytes / bandwidthBytesPerNs);
```

Coalesced access produced a p95 of ten thousand eight hundred; strided with factor two produced sixteen thousand eight hundred (one point five six times); random with factor four produced twenty-eight thousand eight hundred (two point six seven times). The latency scales proportionally with the waste factor, confirming the model.

### Multicast reuse: dividing bytes by a factor

The reuse amplifier device divides the effective bytes by a reuse factor, modeling the distributed shared memory multicast traffic reduction from a two-by-two thread-block cluster:

```javascript
const effectiveBytes = Math.ceil((task.bytesIn + task.bytesOut) / reuseFactor);
```

Sweeping the reuse factor over one, two, and four reproduces the up-to-four-times traffic reduction the book describes for cluster multicast.

## Raising arithmetic intensity: the byte and compute trade

Five chapter-nine techniques raise arithmetic intensity, and all five are expressible with the built-in `bandwidth_device` because they are changes to byte or compute-unit counts — no custom device needed. Kernel fusion (F1) compares a fused single stage against two unfused serial stages with an intermediate memory round-trip:

```javascript
// fused: one read, one write, full compute
.stage("fused", { computeUnits: 4000, bytesIn: 1024, bytesOut: 512, supportedDevices: ["gpu0"] })

// unfused: two stages, intermediate 512 bytes written then re-read
.stage("sin",   { computeUnits: 2000, bytesIn: 1024, bytesOut: 512, supportedDevices: ["gpu0"] })
.stage("sqrt",  { computeUnits: 2000, bytesIn: 512,  bytesOut: 256, supportedDevices: ["gpu0"] })
```

The fused stage touches fifteen hundred thirty-six bytes (arithmetic intensity two point six); the unfused stages touch two thousand three hundred four bytes because the intermediate is written and re-read (weighted intensity one point seven). The fused latency was one point two four times lower. The mechanism is the same one the storage experiments used: removing a serial stage removes that stage's bytes from the total.

Mixed precision (F2) sweeps `bytesIn` through powers of two — one thousand twenty-four, five hundred twelve, two hundred fifty-six, one hundred twenty-eight — modeling FP32 down to FP4. Transfer halves at each step and arithmetic intensity doubles, but the per-step latency improvement shrinks because the fixed compute floor becomes dominant. At high arithmetic intensity (compute-bound), halving bytes barely changed latency (one point zero six times), confirming the roofline prediction that precision reduction helps only when memory-bound.

## Callback metrics: goodput and the primary-served fix

Metrics are computations over the event stream, not private simulator counters. The built-in `latency_p95` reads `request_completed` events; a callback metric reads any events. The shared `goodputMetric` counts requests whose latency meets a service-level objective:

```javascript
function goodputMetric(cfg) {
  const sloNs = cfg.sloNs;
  return events => {
    const completed = events.filter(e => e.eventType === "request_completed");
    const meeting = completed.filter(e => {
      const lat = (e.metadata && e.metadata.latencyNs) != null ? e.metadata.latencyNs : Infinity;
      return lat <= sloNs;
    }).length;
    return { value: meeting, unit: "requests" };
  };
}
```

It is wired in through the metrics builder:

```javascript
.metrics(m => m
  .latencyP95("lat")
  .requestCount("rc")
  .callback("goodput", goodputMetric({ sloNs: SLO_NS })))
```

The disaggregation experiment (D1) uses this goodput metric. Under poisson load that exceeds the colocated service time, the colocated configuration backs up: p95 reaches thirty-three thousand eight hundred fifty-nine nanoseconds and goodput is fifty of sixty. The disaggregated configuration — a fast prefill device and a high-bandwidth decode device plus a key-value transfer stage — drops p95 to eight thousand two hundred forty-two nanoseconds (a four point one one times reduction) and raises goodput to sixty of sixty. The improvement is structural: two devices overlap across requests, while one device serializes them.

A subtlety arose in the admission-control experiment (A3). The admission policy rejects overloaded requests to a near-zero-cost "reject" device. The plain `goodputMetric` counts all `request_completed` events, so rejected requests (which complete instantly) passed the SLO check and inflated goodput. The fix is a callback metric that counts only requests whose `task_completed` fired on the primary device:

```javascript
function servedGoodputMetric(cfg) {
  const sloNs = cfg.sloNs;
  const primaryDeviceId = cfg.primaryDeviceId;
  return events => {
    const primaryReqs = {};
    for (const e of events) {
      if (e.eventType === "task_completed" && e.deviceId === primaryDeviceId && e.requestId) {
        primaryReqs[e.requestId] = true;
      }
    }
    let meeting = 0;
    for (const e of events) {
      if (e.eventType === "request_completed" && primaryReqs[e.requestId]) {
        const lat = (e.metadata && e.metadata.latencyNs) != null ? e.metadata.latencyNs : Infinity;
        if (lat <= sloNs) meeting++;
      }
    }
    return { value: meeting, unit: "requests" };
  };
}
```

After the fix, the comparison is honest: accept-all's primary p95 reached one hundred fifty-eight thousand one hundred forty-three nanoseconds (latency collapse), while admission control kept accepted-request p95 bounded at seven thousand four hundred eighty-five nanoseconds, and all seventeen accepted requests met the SLO. The lesson is general — when a policy routes some requests to a different device, a metric that counts all completions conflates the two populations. Filter by device first.

## Callback policies: admission control and adaptive routing

The built-in policies always accept and route every task. A `policyCallback` authors the choice function in JavaScript. It receives the task, the candidate device IDs, the simulator state, and a scores map, and returns a device ID. The admission-control policy reads the primary device's busy-until timestamp from `state.deviceStates` and rejects when the device is too busy:

```javascript
.policyCallback("admission", (task, candidateDeviceIds, state, scores) => {
  const primaryState = state.deviceStates && state.deviceStates["primary"];
  if (primaryState) {
    const busyUntil = primaryState.busyUntilNs || 0;
    const now = state.nowNs || 0;
    if (busyUntil - now > BUSY_THRESHOLD_NS) {
      return "reject";   // route to the near-zero-cost reject device
    }
  }
  return "primary";
})
```

The `state.deviceStates` map exposes each device's `BusyUntilNS` and `TasksCompleted` to the policy, so a callback can make load-aware decisions. This is how an admission controller, a length-aware router, or a capacity-factor balancer is expressed without a Go change.

The adaptive-parallelism experiment (A2, chapter 19) uses two callback devices representing two parallelism strategies — a tensor-parallel-only device with a capacity cap and multi-pass penalty, and a tensor-plus-pipeline device with a fixed pipeline bubble — and a `policyCallback` that routes by request length:

```javascript
.policyCallback("adaptive", (task, candidateDeviceIds, state, scores) => {
  return task.computeUnits < 12000 ? "tp0" : "pp0";
})
```

Short requests go to the tensor-parallel device (no pipeline bubble); long requests go to the pipeline device (no capacity penalty). The adaptive policy beat both fixed strategies: one point one two times better than fixed tensor-parallel and one point two nine times better than fixed pipeline-parallel across a mixed-length workload. The routing decision is a single threshold on `task.computeUnits`, expressed in one line.

## Variable per-request work: parsing the task id

The simulator gives every request in one workload the same stage list, so per-request variable compute (mixed prompt lengths) cannot be expressed through the stage. The head-of-line-blocking experiment (D4, chapter 17) works around this with a callback device that parses the request index from the task id and varies the cost accordingly:

```javascript
return t => t.jsDevice(id, (phase, task, state, fallback) => {
  const match = task.id && task.id.match(/^req-(\d+)\./);
  const reqIndex = match ? parseInt(match[1], 10) : 0;
  const isHeavy = heavyIndices.indexOf(reqIndex) >= 0;
  const cu = isHeavy ? heavyCu : lightCu;
  const bytes = isHeavy ? heavyBytes : lightBytes;
  const transfer = Math.ceil(bytes / bandwidthBytesPerNs);
  const compute = Math.ceil(cu / speed);
  const duration = setupNs + transfer + compute;
  ...
```

A task's id has the form `req-{index}.{stageId}`, so the device reads the request index and decides whether the request is heavy (sixteen thousand compute units) or light (one thousand). A trace workload then arrives heavy requests first in each batch, so under `first_available` (FIFO) the heavy request occupies the device and the light requests queue behind it. FIFO produced a p99 of four thousand two nanoseconds; load-balanced scheduling (`min_finish_time`) spread the work across two devices and halved the p99 to two thousand twenty-six, a forty-nine point four percent reduction. True shortest-job-first request reordering would tighten the tail further, but that needs a workload-level priority queue the simulator does not yet expose — a documented limitation, not a faked result.

## Multi-device serving topologies

The parallelism experiments (P1 to P4, chapter 15) express each strategy as a topology and policy choice. Tensor parallelism splits compute across devices with an all-reduce synchronization stage; the speedup is highest for compute-bound layers and can be less than one for memory-bound layers because the all-reduce transfer exceeds the compute savings. Pipeline parallelism on four devices achieved three point nine times throughput at high concurrency, approaching the theoretical four times, but suffered pipeline bubbles at low concurrency where utilization dropped to zero point one seven. Data parallelism scaled throughput exactly linearly: four replicas gave four point zero zero times. Expert parallelism with skewed routing produced a five point eight times p95 penalty from load imbalance; a capacity-factor policy rerouted overflow.

Speculative decoding (SD1) models the draft-and-verify loop as a workload parameter: the baseline generates one hundred serial steps (one per token); the speculative variant generates one hundred divided by k steps, each with k times the compute units. The per-step overhead is modeled by `setupNs`. The speedup grows with both k and per-step overhead. At zero setup overhead and k equal to eight, speedup was one point seven eight; at one thousand nanoseconds setup overhead, speedup approached k at five point five six. This explains why speculative decoding is most beneficial in the autoregressive regime where many small kernel launches create per-step overhead.

## Adaptive scheduling

The adaptive-batching experiment (A1, chapter 19) runs a fixed batch size at each load point and, at each point, picks the batch with the lowest p95. At high load a batch of thirty-two amortized per-step overhead and dropped p95 to twelve thousand seven hundred sixty-eight nanoseconds; at low load a batch of one minimized latency at three thousand three hundred thirty-three nanoseconds. No single fixed batch achieved both. The adaptive policy strictly Pareto-dominates any fixed batch size across the load range. This captures the trade-off that motivates chunked prefill: at high load, amortizing overhead via larger batches reduces both latency and queueing; at low load, batching only adds head-of-line delay.

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

## What was learned

The JavaScript-first authoring model worked end to end. Every custom cost formula — the pipelined, divergence, access-pattern, and reuse devices, plus the admission, routing, and adaptive policies — was expressible as a callback without a Go change. The formula under test lived in a script file where it could be edited and rerun immediately. This validates the architecture decision to move from YAML-first to JS-first experiment authoring.

The `max(transfer, compute)` overlap formula was validated three independent times with identical speedup signatures. The formula is no longer a hypothesis; it is a validated model, and the strongest candidate for Go promotion. Promoting it would make the formula available from YAML and the CLI, not only from workbench scripts, and would give it unit tests.

The one genuine fidelity gap is multi-slot concurrency. The occupancy and latency-hiding experiment (E8) is blocked because the built-in devices track a single busy-until timestamp and run one task at a time. A closure-based multi-slot prototype is unreliable across sweep cases because the closure state is not reset per run. This is the one device with a current correctness argument for Go promotion: the Go simulator explicitly reinitializes device state per run, so a Go multi-slot device would get correct per-run state reset for free.

The admission-control metric bug taught a general lesson: when a policy routes some requests to a different device, a metric that counts all completions conflates the populations. The fix is to filter by device first. This pattern — a callback metric that joins `task_completed` to `request_completed` by request id — is reusable for any per-population metric.

## Reproduce

Every experiment is a standalone file. The full program runs with one command per file:

```bash
cd ~/workspaces/2026-06-30/benchmark-cpu-inference/researchctl
for f in experiments-js/ch*/*.js; do
  ./dist/researchctl-jsverbs run "$f"
done
```

All thirty-six experiments pass. The shared library is under `experiments-js/lib/`, and the per-chapter reports with full results tables are under `experiments-js/ch*/REPORT.md`.

## Related notes

- The experiment plan (expected results, before running): `Projects/2026/06/30/ARTICLE - A Simulation Experiment Program for AI Systems Performance Engineering.md`
- The codesign API implementation: `Projects/2026/07/01/ARTICLE - Researchctl Codesign API - Implementation and Usage Deep Dive.md`
- The research graph API and the side-effect boundary: `Projects/2026/07/01/ARTICLE - Researchctl API - Implementation and Usage Deep Dive.md`
- Source repository: `github.com/wesen/researchctl`, branch `task/benchmark-cpu-inference`, ticket RESEARCHCTL-008.
