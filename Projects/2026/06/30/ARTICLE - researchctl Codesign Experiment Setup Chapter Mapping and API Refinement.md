---
title: "researchctl Codesign: Experiment Setup, Chapter Mapping, and API Refinement"
aliases:
  - researchctl codesign experiment setup
  - codesign API refinement
  - chapter simulation preliminary research
tags:
  - article
  - researchctl
  - cpu-gpu-codesign
  - simulation
  - experiments
  - go
  - go-go-goja
  - roofline
status: active
type: article
created: 2026-07-01
repo: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/researchctl
---

# researchctl Codesign: Experiment Setup, Chapter Mapping, and API Refinement

This article documents the preliminary research that prepares a CPU/GPU codesign simulator to reproduce the performance concepts of four chapters of *AI Systems Performance Engineering*. It covers three things: the study of the existing `researchctl` codesign simulator, the mapping of chapter concepts onto that simulator's primitives, and the set of application-programming-interface refinements the study surfaced. It includes a worked example — a roofline simulation — that runs today, and it states precisely which concepts require new simulator capabilities. The goal is to record, before any heavy implementation, exactly what the simulator can already express and where its boundaries are.

This article is indexed by the [[researchctl]] knowledge map and is the planning/catalog entry for the later runtime and validation reports.

> [!summary]
> This report covers four things you should take away:
> 1. What the codesign simulator is: a discrete-event scheduler over devices that estimate task cost, with an extensible registry of devices, policies, and metrics.
> 2. How chapters 5 through 8 map onto it: seven experiments run today with built-in primitives; four require new device families.
> 3. A worked example: an arithmetic-intensity sweep that reproduces the chapter-6 roofline ridge point deterministically.
> 4. The API refinements the study produced: experiment types (workload patterns, sweeps, comparison metrics), device families, and JavaScript-callback devices — captured as a requirements document for the implementer.

## Why this note exists

The long-term goal is to study GPU performance concepts by simulating them cheaply and deterministically before measuring them on hardware. `researchctl` contains a codesign simulation backend intended for exactly this. Before writing experiments, it was necessary to understand what the simulator can already express, to confirm that its primitives capture the book's concepts faithfully, and to identify the gaps that would require new code. This article preserves the result of that preliminary study so the experiment program can proceed without re-deriving the analysis, and so the requested application-programming-interface changes are recorded in one place.

## The codesign simulation model

The codesign backend in `researchctl` is a discrete-event scheduler. Everything it models is built from four abstractions.

A task is a unit of work. It carries a number of compute units, a number of input bytes, a number of output bytes, and the list of devices that may run it. A task is one stage of one request.

A device is anything that can run a task. The device interface has two methods that matter for modeling: `Estimate`, which returns when a task can start, how long it takes, and when it finishes; and `Run`, which executes the task and updates device state. The duration formula inside `Estimate` is the model. Changing the cost model means changing a device's `Estimate`.

A policy decides which compatible device runs each task. A metric computes a number from the event stream the simulation produces.

The simulator is a single loop. For each request, for each stage, it asks the policy to choose a device, asks the device to run the task, advances time, and emits events.

```go
for each request r in workload:
    for each stage s in workload.stages:
        task = Task{r, s, computeUnits, bytesIn, bytesOut, supportedDevices}
        candidates = devices that CanRun(task)
        decision   = policy.Choose(task, candidates, state)
        result     = device.Run(task, &state)
        emit task_started, task_completed
    emit request_completed with latencyNs
for each metric: metric.Compute(eventStream)
```

Two structural facts follow from this loop and shape every experiment. First, stages within a request run serially; a request's stage N must finish before stage N+1 begins. There is no inter-stage overlap in the built-in simulator. Second, each device is effectively single-slot: it tracks one busy-until timestamp, so a second task on the same device waits for the first to finish. These are the boundaries of the current model, and they determine which concepts are expressible today.

## The device vocabulary

The built-in devices define what can be modeled. A simple device is a pure compute device. Its duration is its setup overhead plus the task's compute units divided by the device's speed. It has no notion of bytes. It models a compute-only processor, or a GPU stage where memory cost is irrelevant.

```go
duration = setupNs + ceil(computeUnits / speed)
```

A bandwidth device separates compute cost from memory cost. This is the single most important device for the chapters studied, because separating the two rates makes arithmetic intensity expressible.

```go
transfer = ceil((bytesIn + bytesOut) / bandwidthBytesPerNs)
compute  = ceil(computeUnits / computeUnitsPerNs)
duration = setupNs + transfer + compute
```

Arithmetic intensity is the ratio of compute work to bytes transferred. It is the horizontal axis of the roofline model from chapter 6. By sweeping arithmetic intensity, a task transitions from transfer-dominated — memory-bound — to compute-dominated — compute-bound. The bandwidth device is the primitive that makes that transition simulatable.

The four built-in policies cover the scheduling decisions the chapters discuss. `first_available` places a task on the first compatible device and is the naive baseline. `min_finish_time` chooses the device with the earliest estimated finish and models greedy offload. `round_robin` rotates through candidates and spreads load. `prefer_accel_unless_small` sends small tasks to the CPU and large tasks to the accelerator, with a configurable threshold; it is the chapter-5 offload decision expressed in one line.

## The chapter mapping

Each chapter concept maps to a choice of device type, workload shape, and policy. The study produced a catalog of eleven experiments. Seven run today with built-in primitives. Four require new device families.

Seven experiments are runnable now. A roofline experiment sweeps the arithmetic intensity of a bandwidth device and reproduces the chapter-6 ridge point. An offload break-even experiment sweeps the threshold of the size-based policy and finds where the accelerator takes a majority of tasks. A storage-pipeline experiment chains a low-bandwidth storage device to a high-compute GPU and measures starvation as the storage bandwidth scales. A direct-storage experiment compares a two-stage path through a host device against a one-stage direct path and measures the latency difference, modeling the chapter-5 GPU Direct Storage concept. A compression experiment trades fewer transferred bytes for more compute units and shows where the trade-off pays off. A policy-comparison experiment holds topology and workload fixed and varies the policy. A striping experiment adds parallel storage devices and measures aggregate throughput scaling.

Four experiments require new device families because the built-in devices cannot express them. Occupancy and latency hiding require a device with multiple concurrent slots, so a stalled slot does not block ready tasks. Coalesced versus strided memory access requires a device that inflates transferred bytes by an access-pattern factor. Warp divergence requires a device that multiplies effective compute by a divergence factor. Instruction-level parallelism requires a device with independent math and memory pipelines that issue in parallel. The last of these — a pipelined device — is the highest-leverage addition, because it would also close the fidelity gap that prevents the simulator from expressing the overlap of transfer with compute.

## A worked example: the roofline

The roofline experiment runs today and validates the mapping. A bandwidth device models the GPU, with a compute rate of twenty units per nanosecond, a memory rate of eight bytes per nanosecond, and a setup overhead of one thousand nanoseconds. A single inference stage runs one hundred requests on that device. A sweep varies the stage's compute units against its transferred bytes and prints the transfer time, the compute time, and the regime.

```
bytesIn  bytesOut   CU      AI       transferNs   computeNs   regime
1024     128        200     0.174    144          10          memory-bound
1024     128        2000    1.736    144          100         memory-bound
1024     128        4000    3.472    144          200         compute-bound
1024     128        8000    6.944    144          400         compute-bound
1024     128        32000   27.778   144          1600        compute-bound
```

The regime column flips from memory-bound to compute-bound between a compute-size of two thousand and four thousand, which is exactly where the transfer time stops exceeding the compute time. That crossover is the roofline ridge point. The simulator reproduces it deterministically from the device's cost formula, with no model call and no hardware.

The ridge point is predictable analytically. The regime flips where transfer time equals compute time.

```
ceil((bytesIn + bytesOut) / bandwidthBytesPerNs) = ceil(computeUnits / computeUnitsPerNs)
```

At the point where the two are equal, the arithmetic intensity equals the ratio of compute rate to memory rate: twenty divided by eight, or two and a half compute units per byte. The sweep confirms this: the crossover lies between arithmetic intensity 1.736 and 3.472. This agreement between the analytic formula and the simulated output is the evidence that the bandwidth device faithfully expresses the roofline concept.

## The application-programming-interface refinements

Studying the simulator against the chapters surfaced a set of refinements. These were captured as a requirements document — `03-requested-codesign-api-extensions.md` — for the colleague who implements the JavaScript bindings. The document states what is wanted and leaves the tradeoffs to the implementer. The refinements fall into four groups.

The first group is experiment types. The simulator runs one specification at a time and produces one manifest. There is no first-class concept for the things a researcher does repeatedly. A workload registry would make arrival patterns pluggable, so fixed, Poisson, bursty, and trace-driven arrivals become selectable types rather than a single hardcoded shape. A sweep specification would declare a base run and one or more axes to vary, and the simulator would expand the matrix and write one aggregate manifest with a row per combination. Comparison metrics would reduce a sweep to a conclusion — a delta against a baseline, a crossover point, a regime label — instead of leaving the researcher to compute those by hand. An experiment lifecycle would close the loop between a run and the research graph, so a measured result moves an experiment's status according to machine-evaluable success criteria.

The second group is device families. These are new device types implementing the device interface and registered alongside the built-ins. A multi-slot device models occupancy. An access-pattern device models coalescing efficiency. A divergence device models warp divergence. A pipelined device models instruction-level parallelism and, critically, the overlap of transfer with compute that the current serial model cannot express.

The third group is JavaScript-callback devices, policies, and metrics. Today every cost model is compiled Go. A JavaScript-callback device would let a researcher author the cost function — the body of `Estimate` — in JavaScript, passed as a function, without writing or recompiling Go. The same applies to a policy's choice function and a metric's computation. This is the refinement that fuses the goja runtime with the simulator, which today has no goja dependency, and it carries real runtime requirements: the goja runtime is single-threaded, so callbacks from the Go simulator loop must be marshalled onto the runtime safely; JavaScript values must be held and re-invoked across the boundary; and errors thrown in callbacks must propagate without crashing the simulation. The requirements document records these requirements without prescribing their solution.

The fourth group is the artifact layer. A sweep manifest type would distinguish a sweep result from a single run. Richer per-run provenance would record which device and workload types ran, not just which backend. A content-addressed run identity derived from the normalized specification would make identical specifications produce identical artifacts and enable caching within sweeps.

## Sequencing

The refinements are not all of a kind, and their ordering affects how much rework the program incurs. The device families are cheap to write in Go and force the actual cost formulas to be pinned down. The experiment types — the workload registry, the sweep specification, the comparison metrics — are the structural additions that turn a single-run simulator into an experiment platform. The JavaScript fluent module is the ergonomic layer that makes sweeps readable as loops and topologies reusable as fragments; it can be built on top of the registry without editing the core. The JavaScript-callback layer is the one item that changes the runtime's architecture, and it should follow the device families so that the cost models it hosts are already settled.

This sequencing is recorded here as the study's conclusion, not as a prescription on the implementer, who owns the tradeoffs.

## Working rules

Model a concept as a device whose `Estimate` formula expresses the concept's cost. Sweep one parameter at a time and keep everything else fixed, and verify the simulated result against an analytic prediction before trusting it across a range. Treat the research graph as the record of why an experiment exists and what it showed, not as a notepad. When the simulator's primitives cannot express a concept, add a device family rather than bending an existing device. Keep the cost-model language as Go until the formulas are proven, then promote user-defined models to JavaScript callbacks.

## Related notes

- The book was prepared as Markdown by the tool documented in `Projects/2026/06/30/ARTICLE - epub-extract A Born-Digital EPUB to Markdown Pipeline.md`.
- Source repository: `github.com/wesen/researchctl` branch `task/benchmark-cpu-inference`, tickets `RESEARCHCTL-004` (the chapter-mapping guide) and `RESEARCHCTL-003` (the bindings implementation guide and the extensions requirements document).
- The bootstrap of this workspace is documented in `Projects/2026/06/30/PROJECT REPORT - benchmark-cpu-inference Workspace - researchctl Bootstrap Deep Dive.md`.
