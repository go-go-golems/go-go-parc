---
title: Optimization and Performance Engineering
aliases: [Falllinie performance reading map, MOC - Falllinie Optimization Reports, Optimization MOC]
type: article
status: active
created: 2026-10-13
tags: [moc, performance, optimization, profiling, ebpf]
---

# Optimization and performance engineering

A question-oriented map of performance investigations across the vault: Linux profiling and eBPF, memory attribution, graphics and display pipelines, runtime boundaries, database queries, and experimental methodology. The Falllinie reports form a detailed case-study series below; they are no longer the scope of the whole index.

> [!summary]
> Begin with a defined workload and quantity. Distinguish execution, waiting, allocation, traffic and static estimates. Read corrections and rejected experiments alongside successful changes. A tracing proposal, simulation or archived conversation is not a measured production result.

## Start with the question, not the tool

| Question | Start here | Important distinction |
|---|---|---|
| Is the benchmark measuring the real workload? | [[ARTICLE - Screencast Studio - Performance Investigation Approaches and Tricks|Screencast investigation methods]]; [[ARTICLE - Measuring Before Optimizing - An X11 Window Manager Resize Path|X11 resize investigation]] | Synthetic clients and nested display servers can change the conclusion. |
| Is time spent executing, blocked, or runnable? | Falllinie tracing/rendering series below; off-CPU resources below | CPU samples and wall-minus-CPU residuals do not identify the same thing. |
| Are page faults or memory growth actually causing the slowdown? | [[01-REPORT-x264-Go-CGO-Page-Fault-Root-Cause-Analysis|x264 / Go / CGO page-fault investigation]]; [[ARTICLE - Publish Vault Memory Optimization - From OOM Incidents to Phase-Attributed Baselines|Publish Vault memory investigation]] | Resident memory, heap allocation, faults and sustained CPU work require separate attribution. |
| Which pixels or bytes need to be processed at all? | [[ARTICLE - Optimizing an X11 Window Manager Paint Path|X11 paint-path optimization]]; [[ARTICLE - ESP32-P4 PicoCalc Display Optimization - Queued SPI and Dirty Rectangles|PicoCalc queued SPI and dirty rectangles]]; [[ARTICLE - Optimizing WiFi Image Upload on ESP32-P4 - From 6 Seconds to Sub-Second|ESP32-P4 Wi-Fi image upload]] | Work avoidance, transfer granularity and queue ownership can matter more than instruction tuning. |
| Is the runtime boundary or query shape expensive? | [[ARTICLE - Goja Site Rendering Performance Internals and Export Boundary Deep Dive|Goja rendering and export-boundary costs]]; [[ARTICLE - SQLite in the Browser - Measuring and Fixing sql.js Performance in Static Code Review Sites|Browser SQLite query optimization]] | Measure conversion, allocation and query expansion rather than assuming the runtime itself is the cause. |
| What should be instrumented continuously? | [[ARTICLE - Screencast Studio - Prometheus Metrics Architecture and Field Guide|Screencast metrics field guide]] | Operational metrics locate changes; targeted profiling answers narrower causal questions. |

## Linux profiling, eBPF and corrected causal explanations

The strongest older eBPF-related investigation found is [[01-REPORT-x264-Go-CGO-Page-Fault-Root-Cause-Analysis|x264 / Go / CGO page-fault investigation]] (April 2026), under `Research/Institute/Technical Reports/`, rather than the Projects folder. It records uprobes, bpftrace fault stacks, allocator comparisons and memory-map analysis. **Read its two errata first.** The initial CGO/malloc explanation was disproved; the later buffer-pool/page-fault explanation described real memory behavior but did not explain sustained CPU load. The final CPU diagnosis was silently rejected encoder property settings, leaving a more expensive default configuration active. Some lower sections preserve earlier interpretations: the errata is essential context, not an optional footnote.

Pair that report with [[ARTICLE - Screencast Studio - Performance Investigation Approaches and Tricks|Screencast investigation methods]], which explains reproducible workloads, real-browser versus synthetic baselines and why disproven hypotheses remain useful. The Falllinie tracing → rendering → GPU sequence below provides a newer example of choosing available instrumentation on a constrained kernel rather than assuming every eBPF or scheduler facility exists.

Two archived conversations broaden the questions but are **discussion sources, not independently qualified experiments**: [[CHATGPT TRANSCRIPT - JavaScript Interpreter Instrumentation — Goja eBPF|Goja/eBPF instrumentation conversation]] (July 2026) and [[CHATGPT TRANSCRIPT - eBPF for Wi-Fi Disconnects|Wi-Fi disconnect tracing conversation]] (August 2026). Use them for investigation ideas and then consult implementation evidence and tool documentation before treating suggested probes as working measurements.

## Memory, allocation and observability

[[ARTICLE - Publish Vault Memory Optimization - From OOM Incidents to Phase-Attributed Baselines|Publish Vault memory investigation]] distinguishes Go heap from RSS and attributes peak usage to load/index phases. It records both completed representation/indexing changes and remaining uncertainty inside index construction. This is a useful companion to the x264 report: neither a large virtual mapping nor a high fault count is, by itself, a complete explanation of runtime cost.

[[ARTICLE - Screencast Studio - Prometheus Metrics Architecture and Field Guide|Screencast metrics field guide]] covers the application's metrics architecture. Read it alongside a targeted profiler investigation rather than treating metrics, CPU profiles, execution traces and heap snapshots as substitutes for one another. The Falllinie buffered-audio report below adds ownership and scheduling constraints: moving work off a deadline-sensitive callback does not remove that work from the process.

## Graphics, display and transfer costs

- [[ARTICLE - Measuring Before Optimizing - An X11 Window Manager Resize Path|X11 resize investigation]] follows changing diagnoses, a misleading harness, decomposition and bounded image-difference decisions.
- [[ARTICLE - Optimizing an X11 Window Manager Paint Path|X11 paint-path optimization]] records work avoidance, glyph caching, backing-store strategies, rejected changes and differences between Xephyr and the target display stack.
- [[ARTICLE - ESP32-P4 PicoCalc Display Optimization - Queued SPI and Dirty Rectangles|PicoCalc queued SPI and dirty rectangles]] connects clock-source selection, transfer size, queued DMA lifetime and dirty-region geometry. Its queued-transfer ownership invariant matters as much as the throughput number.
- [[ARTICLE - Optimizing WiFi Image Upload on ESP32-P4 - From 6 Seconds to Sub-Second|ESP32-P4 Wi-Fi image upload]] separates payload compression, decompressor stack requirements and timeout configuration, while keeping future transfer ideas distinct from implemented changes.

Compare these with Falllinie's GPU reports below: fewer source operations, a smaller transfer or an apparently cheaper path is a hypothesis until the complete target workload supports it. Explicitly accepted small visual differences in one project do not grant permission to relax another project's fidelity contract.

## Runtime boundaries, database work and simulation

[[ARTICLE - Goja Site Rendering Performance Internals and Export Boundary Deep Dive|Goja rendering and export-boundary costs]] profiles JavaScript object construction and `goja.Value.Export()` at the native UI boundary, and broadens benchmarks to avoid optimizing only one page. [[ARTICLE - SQLite in the Browser - Measuring and Fixing sql.js Performance in Static Code Review Sites|Browser SQLite query optimization]] shows how compatibility-view expansion and query shape can dominate perceived browser responsiveness; moving execution to a worker and reducing query work address different problems.

[[PROJECT REPORT - researchctl CPU GPU Codesign Experiment Runtime Deep Dive|researchctl CPU/GPU experiment runtime]] documents a deterministic simulator, event-derived metrics and durable experiment manifests. It is valuable for experimental architecture and reproducibility, but its simulated execution is not evidence of a measured hardware speedup. Likewise, Falllinie's isolated ARM64 JavaScript embeddings below do not establish integrated game-frame headroom.

## Online references: choose the instrument for the quantity

These are external references, not additional local experiments. Search-discovered methodology links and official tool/project documentation were selected for the questions covered by this MOC; tool availability and syntax still depend on the target's versions and kernel configuration.

### Methodology and CPU attribution

- [Brendan Gregg — USE Method](https://www.brendangregg.com/usemethod.html): utilization, saturation and errors as a systematic resource investigation checklist.
- [Brendan Gregg — Linux perf examples](https://www.brendangregg.com/perf.html): CPU sampling, counters and tracing examples; select events appropriate to the claim.
- [Brendan Gregg — Off-CPU Analysis](https://www.brendangregg.com/offcpuanalysis.html): investigating time not executing, with contextual stacks and explicit scope.
- [Brendan Gregg — Flame Graphs](https://www.brendangregg.com/flamegraphs.html): interpretation of aggregated stacks; horizontal position is not a time axis.

### eBPF and language-runtime diagnostics

- [bpftrace official project](https://github.com/bpftrace/bpftrace) and [versioned 0.22 reference](https://bpftrace.org/docs/0.22): probe types, language and aggregation. Select documentation matching the installed release; this link is not a claim that 0.22 is current.
- [BCC project and tools](https://github.com/iovisor/bcc): Linux BPF-based tracing utilities and examples. Check kernel support, permissions and collection overhead before use.
- [Go diagnostics](https://go.dev/doc/diagnostics): profiling, tracing and runtime diagnostics; choose CPU, heap, blocking or execution-trace evidence according to the question.

### GPU counters and static shader analysis

- [Arm libGPUCounters](https://github.com/ARM-software/libGPUCounters): hardware counter collection; product-specific event definitions and derived denominators are part of interpretation.
- [Pinned Mali-G52 counter reference used by Falllinie](https://github.com/ARM-software/libGPUCounters/blob/378c7b59e2dae87cbbffb0ac9cf96ed13c939823/docs/mali-g52_counter_reference.html): the definitions associated with that actual campaign, rather than an unqualified latest mapping.
- [Arm Mali Offline Compiler](https://developer.arm.com/tools-and-software/mali-offline-compiler): target-specific shader resource estimates. Static cycles, register allocation and occupancy guide experiments; they do not replace live timing or appearance checks.

## Falllinie case-study series

This case-study series connects nine reports on the native Falllinie port's fidelity, workload, audio, JavaScript experiments and CPU/GPU performance, plus a later review of the performance investigation. They describe successive checkpoints and different workloads, not interchangeable benchmark results. Reports link back here; the catalogue includes later additions to the original cross-linked collection.

> [!summary]
> Buffered audio is implemented and has finite target qualification. CPU/driver attribution and GPU counter collection are measured. JavaScript remains an isolated embedding experiment. The compiler-guided shader candidate did not show a convincing live benefit and was not promoted. Complete visual parity and robust integrated 60 FPS are not established by this collection.

### Choose a reading route

**For the current rendering evidence**, read [[PROJECT REPORT - Falllinie Tracing - CPU Execution, Driver Waits and GPU Attribution|Tracing]] → [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|Rendering Measurements]] → [[PROJECT REPORT - Falllinie GPU Profiling - Hardware Counters, Shader Compilation and a Rejected Optimization|GPU Profiling]]. This moves from definitions and the proposed investigation to actual CPU/perf results, then actual hardware counters, offline compilation and the rejected shader experiment. Continue with [[PROJECT REPORT - Falllinie CPU PMU - Cache Events, Driver Cycles and an Audio-Disabled Baseline|CPU PMU]] for the subsequent main-thread CPU cache/TLB/branch counts and hardware-cycle profile. Its audio-disabled workload is explicitly different from the integrated runs. The living CPU follow-up adds event-location profiles and an indexed-range candidate that reduces scene CPU cost without demonstrating a frame-time gain. Then return to Sections 10–16 of GPU Profiling for the implemented deterministic live replay, resolution/view-count scaling, and evidence of a possible presentation ceiling. That audio-disabled benchmark preserves the real rendering paths but deliberately fixes simulation input and streaming work per frame. Section 17 adds the repeated non-parity scene/post experiment: scene simplification has the larger timing effect, while combined reductions expose the apparent presentation floor. These are changed-image sensitivity results, not accepted production optimizations. Section18 follows with conservative shadow rejection:12.46% lower mean interval and40 pixel-equal multi-endpoint comparisons, with full-window screenshots; it remains an opt-in candidate pending broader/integrated qualification.

**For source-faithful optimization constraints**, read [[PROJECT REPORT - Falllinie Native GLES Spike - Deterministic Terrain, Print Shaders and Mali Depth Precision|Native GLES Spike]] → [[PROJECT REPORT - Falllinie Playable Port - Dual Views, Frame Profiling and Cooperative Terrain Streaming|Playable Port]] → [[PROJECT REPORT - Falllinie Integrated Native Game - Precision, Real-Time Audio, Developer Telemetry and JavaScript Embedding|Integrated Native Game]]. These explain the original graphics semantics, shared-view ownership, streaming, the expanded workload and camera-relative precision correction.

**For audio scheduling**, read [[PROJECT REPORT - Falllinie Integrated Native Game - Precision, Real-Time Audio, Developer Telemetry and JavaScript Embedding|Integrated Native Game]] → [[PROJECT REPORT - Falllinie Buffered Audio - PCM Ownership, Callback Deadlines and Measured Producer Scheduling|Buffered Audio]] → [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|Rendering Measurements]]. DSP cost, callback deadline safety and all-thread CPU attribution answer different questions.

**For embedded JavaScript**, read [[PROJECT REPORT - Falllinie Integrated Native Game - Precision, Real-Time Audio, Developer Telemetry and JavaScript Embedding|Integrated Native Game]] → [[PROJECT REPORT - Falllinie JavaScript Embedding - ARM64 Qualification, V8 Ownership and Bounded Rules|JavaScript Embedding]], then compare its proposed integration scope with [[PROJECT REPORT - Falllinie Buffered Audio - PCM Ownership, Callback Deadlines and Measured Producer Scheduling|audio ownership]] and [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|actual rendering costs]]. A fast isolated V8 benchmark does not establish available game-frame budget.

**For an assessment of the performance investigation and the next plan**, read [[PROJECT REPORT - Falllinie Performance Review - Measurement Discipline, Missed Bottlenecks and a Path to 60 FPS|Performance Review]] after the rendering route above. It goes through each experiment and rates it, then re-analyses the committed frame CSVs and counter summaries. The re-analysis finds that the mean frame interval is almost entirely explained by the share of frames that miss a refresh. It also finds that about 8 of the 14 million GPU-active cycles in a 384×288 dual-view replay frame do not scale with internal resolution, and that geometry density was never examined. The review then proposes an ordered plan: measure shadow bounds at the shipping configuration, collect geometry counters, then make pixel-identical geometry reductions. Its cycle-budget figures are estimates derived from published rates, not new device measurements.

**For the measured follow-up**, read [[PROJECT REPORT - Falllinie GPU Budget Recovery - Shadow Bounds at the Shipping Size, Geometry Counters and Presentation Acquisition|GPU Budget Recovery]]. It executes the review's plan on the device: shadow bounds at the shipping size, geometry counters, pixel-identical row-block culling and 16-bit indices, a rejected fog shortcut, and a direct measurement of the presentation wait. Live autoplay with audio drops from 7.6% to 0.1% long frames with the new defaults.

### Report catalogue and evidence progression

| Report | What it contributes | How to read its checkpoint today |
|---|---|---|
| [[PROJECT REPORT - Falllinie Native GLES Spike - Deterministic Terrain, Print Shaders and Mali Depth Precision|Native GLES Spike]] | Terrain oracle, encoded scene/print pipeline, Mali sampler precision. | Graphics foundation and fidelity limits, not complete gameplay or integrated performance qualification. |
| [[PROJECT REPORT - Falllinie Playable Port - Dual Views, Frame Profiling and Cooperative Terrain Streaming|Playable Port]] | Dual-view ownership, pacing, profiling and cooperative terrain streaming. | Its frame-rate result belongs to the earlier smaller workload. |
| [[PROJECT REPORT - Falllinie Integrated Native Game - Precision, Real-Time Audio, Developer Telemetry and JavaScript Embedding|Integrated Native Game]] | Expanded gameplay, projection precision, source DSP work, telemetry and initial JS investigation. | Establishes why the earlier performance result cannot be carried into the larger game unchanged. |
| [[PROJECT REPORT - Falllinie Buffered Audio - PCM Ownership, Callback Deadlines and Measured Producer Scheduling|Buffered Audio]] | Implemented producer/SPSC/copy-only callback transport and target comparisons. | Target callback deadline success is not physical latency, backend XRUN or universal listening qualification. |
| [[PROJECT REPORT - Falllinie JavaScript Embedding - ARM64 Qualification, V8 Ownership and Bounded Rules|JavaScript Embedding]] | Actual ARM64 engine embeddings, measured workloads and proposed ownership/validation contract. | Isolated engine qualification; production game integration remains proposed. |
| [[PROJECT REPORT - Falllinie Tracing - CPU Execution, Driver Waits and GPU Attribution|Tracing]] | Measurement concepts, constructed scheduler example and investigation design. | Follow with Rendering Measurements for actual execution evidence and discovered kernel limitations. |
| [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|Rendering Measurements]] | Paired clocks, perf CPU attribution, observed frame distributions and timer anomalies. | Driver CPU execution is not GPU utilization; residual time is not proven GPU wait. |
| [[PROJECT REPORT - Falllinie GPU Profiling - Hardware Counters, Shader Compilation and a Rejected Optimization|GPU Profiling]] | Working counters/compiler, rejected shader candidate, and deterministic live replay with actual resolution/view scaling. | Dual-view cost rises with internal resolution; single-view throughput stays near 60/s despite rising activity. No calibrated GPU utilization or production optimization claim. |
| [[PROJECT REPORT - Falllinie CPU PMU - Cache Events, Driver Cycles and an Audio-Disabled Baseline|CPU PMU]] | Actual Cortex-A55 counts and event profiles, verified driver scan, and an opt-in indexed-range experiment. | Audio-disabled workload; scene CPU decreases, but frame timing does not clearly improve. No causal cache-latency diagnosis. |
| [[PROJECT REPORT - Falllinie Performance Review - Measurement Discipline, Missed Bottlenecks and a Path to 60 FPS|Performance Review]] | An experiment-by-experiment assessment; re-analysis of committed frame and counter data (refresh-miss structure, per-frame GPU cycles and bytes); and a prioritised plan. | A review with derived estimates, not a new device campaign. Its predictions, such as shadow bounds reaching budget at 384×288 dual view, remain to be measured. |
| [[PROJECT REPORT - Falllinie GPU Budget Recovery - Shadow Bounds at the Shipping Size, Geometry Counters and Presentation Acquisition|GPU Budget Recovery]] | Shipping-size shadow bounds, geometry counters, pixel-identical culling and 16-bit indices promoted to defaults, presentation-acquire measurement, live acceptance with audio. | Replay and live autoplay on the device. PERF-009 defaults are byte-identical at five checkpoints; the later 60 m terrain detail (owner-approved, 0.6–1.4% of pixels changed) and 512×384 internal size hold 60 Hz in 110-second live sessions at about 90% GPU busy. |

### Connections that matter technically

#### Precision and shader cost are connected, but correctness comes first

The [[PROJECT REPORT - Falllinie Native GLES Spike - Deterministic Terrain, Print Shaders and Mali Depth Precision|sampler correction]] and [[PROJECT REPORT - Falllinie Integrated Native Game - Precision, Real-Time Audio, Developer Telemetry and JavaScript Embedding|camera-relative projection correction]] explain why reducing precision is not a free optimization. The [[PROJECT REPORT - Falllinie GPU Profiling - Hardware Counters, Shader Compilation and a Rejected Optimization|compiler investigation]] analyzes the adapted submitted shader, not just the unmodified asset, and retains those constraints.

#### Moving audio computation changes scheduling, not the existence of its cost

The [[PROJECT REPORT - Falllinie Buffered Audio - PCM Ownership, Callback Deadlines and Measured Producer Scheduling|buffered transport]] removes synthesis from the callback without claiming to eliminate synthesis work. The [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|perf campaign]] observes producer execution separately from main-thread driver execution. Read these together before interpreting total process CPU or callback timing.

#### Newer tools resolve availability questions, not every attribution question

The [[PROJECT REPORT - Falllinie Tracing - CPU Execution, Driver Waits and GPU Attribution|tracing plan]] precedes implementation. [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|Actual measurements]] establish paired-clock/perf results and the current kernel's tracing limitations. [[PROJECT REPORT - Falllinie GPU Profiling - Hardware Counters, Shader Compilation and a Rejected Optimization|The subsequent GPU investigation]] establishes that counters and offline compilation work. None of those later successes repairs the anomalous elapsed-query values or supplies a scheduler trace that was never captured.

#### A promising subsystem is not a successful local optimization

The non-parity post bypass and the source-formula-preserving candidate are separate interventions in [[PROJECT REPORT - Falllinie GPU Profiling - Hardware Counters, Shader Compilation and a Rejected Optimization|GPU Profiling]]. Removing the post pass improved tails; the narrow candidate did not. Its fixed fixture matched, but its live ABBA timings did not justify promotion. The [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|CPU/driver results]] leave other rendering hypotheses open rather than proving that the local shader edit had to succeed.

#### Repeatability requires more than a seeded game

The later GPU Profiling checkpoint fixes both raw simulation input and terrain row-work units. A wall-budgeted streaming job can change mesh arrival even when input dt is fixed. Matching selected-state signatures and same-resolution endpoint images improve workload comparability; they do not prove universal parity. The scaling matrix also shows why flat frame time can hide increased hardware demand when presentation limits throughput.

### Reading rules for comparisons

Preserve each report's workload, runtime revision, clock definition and evidence boundary when comparing numbers. Earlier 60-FPS observations do not qualify later expanded workloads. Whole-device GPU counters do not isolate a render pass, and static compiler estimates are not runtime milliseconds. A conceptual example is not a captured trace; a proposed integration is not an implemented feature.

The cross-link additions are editorial navigation, explicitly requested after publication. Historical report bodies, data and figures remain preserved; explicitly dated living-report follow-ups add later measurements without rewriting earlier outcomes. Original publication hashes describe their historical versions; later editorial and measurement-publication commits record the additions separately. This index adds no experiment and claims no new optimization result.
