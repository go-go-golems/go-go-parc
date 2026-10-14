---
title: Falllinie Optimization Reports
aliases: [Falllinie performance reading map]
type: project
status: active
created: 2026-10-12
tags: [project, falllinie, performance, moc]
repo: /home/manuel/code/wesen/2026-10-12--falllinie-spike
---

# Falllinie optimization reports

This index connects the eight reports on the native Falllinie port's fidelity, workload, audio, JavaScript experiments and rendering performance. They describe successive checkpoints and different workloads, not eight interchangeable benchmark results. Each report now links back here and directly to every other report.

> [!summary]
> Buffered audio is implemented and has finite target qualification. CPU/driver attribution and GPU counter collection are measured. JavaScript remains an isolated embedding experiment. The compiler-guided shader candidate did not show a convincing live benefit and was not promoted. Complete visual parity and robust integrated 60 FPS are not established by this collection.

## Choose a reading route

**For the current rendering evidence**, read [[PROJECT REPORT - Falllinie Tracing - CPU Execution, Driver Waits and GPU Attribution|Tracing]] → [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|Rendering Measurements]] → [[PROJECT REPORT - Falllinie GPU Profiling - Hardware Counters, Shader Compilation and a Rejected Optimization|GPU Profiling]]. This moves from definitions and the proposed investigation to actual CPU/perf results, then actual hardware counters, offline compilation and the rejected shader experiment.

**For source-faithful optimization constraints**, read [[PROJECT REPORT - Falllinie Native GLES Spike - Deterministic Terrain, Print Shaders and Mali Depth Precision|Native GLES Spike]] → [[PROJECT REPORT - Falllinie Playable Port - Dual Views, Frame Profiling and Cooperative Terrain Streaming|Playable Port]] → [[PROJECT REPORT - Falllinie Integrated Native Game - Precision, Real-Time Audio, Developer Telemetry and JavaScript Embedding|Integrated Native Game]]. These explain the original graphics semantics, shared-view ownership, streaming, the expanded workload and camera-relative precision correction.

**For audio scheduling**, read [[PROJECT REPORT - Falllinie Integrated Native Game - Precision, Real-Time Audio, Developer Telemetry and JavaScript Embedding|Integrated Native Game]] → [[PROJECT REPORT - Falllinie Buffered Audio - PCM Ownership, Callback Deadlines and Measured Producer Scheduling|Buffered Audio]] → [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|Rendering Measurements]]. DSP cost, callback deadline safety and all-thread CPU attribution answer different questions.

**For embedded JavaScript**, read [[PROJECT REPORT - Falllinie Integrated Native Game - Precision, Real-Time Audio, Developer Telemetry and JavaScript Embedding|Integrated Native Game]] → [[PROJECT REPORT - Falllinie JavaScript Embedding - ARM64 Qualification, V8 Ownership and Bounded Rules|JavaScript Embedding]], then compare its proposed integration scope with [[PROJECT REPORT - Falllinie Buffered Audio - PCM Ownership, Callback Deadlines and Measured Producer Scheduling|audio ownership]] and [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|actual rendering costs]]. A fast isolated V8 benchmark does not establish available game-frame budget.

## Report catalogue and evidence progression

| Report | What it contributes | How to read its checkpoint today |
|---|---|---|
| [[PROJECT REPORT - Falllinie Native GLES Spike - Deterministic Terrain, Print Shaders and Mali Depth Precision|Native GLES Spike]] | Terrain oracle, encoded scene/print pipeline, Mali sampler precision. | Graphics foundation and fidelity limits, not complete gameplay or integrated performance qualification. |
| [[PROJECT REPORT - Falllinie Playable Port - Dual Views, Frame Profiling and Cooperative Terrain Streaming|Playable Port]] | Dual-view ownership, pacing, profiling and cooperative terrain streaming. | Its frame-rate result belongs to the earlier smaller workload. |
| [[PROJECT REPORT - Falllinie Integrated Native Game - Precision, Real-Time Audio, Developer Telemetry and JavaScript Embedding|Integrated Native Game]] | Expanded gameplay, projection precision, source DSP work, telemetry and initial JS investigation. | Establishes why the earlier performance result cannot be carried into the larger game unchanged. |
| [[PROJECT REPORT - Falllinie Buffered Audio - PCM Ownership, Callback Deadlines and Measured Producer Scheduling|Buffered Audio]] | Implemented producer/SPSC/copy-only callback transport and target comparisons. | Target callback deadline success is not physical latency, backend XRUN or universal listening qualification. |
| [[PROJECT REPORT - Falllinie JavaScript Embedding - ARM64 Qualification, V8 Ownership and Bounded Rules|JavaScript Embedding]] | Actual ARM64 engine embeddings, measured workloads and proposed ownership/validation contract. | Isolated engine qualification; production game integration remains proposed. |
| [[PROJECT REPORT - Falllinie Tracing - CPU Execution, Driver Waits and GPU Attribution|Tracing]] | Measurement concepts, constructed scheduler example and investigation design. | Follow with Rendering Measurements for actual execution evidence and discovered kernel limitations. |
| [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|Rendering Measurements]] | Paired clocks, perf CPU attribution, observed frame distributions and timer anomalies. | Driver CPU execution is not GPU utilization; residual time is not proven GPU wait. |
| [[PROJECT REPORT - Falllinie GPU Profiling - Hardware Counters, Shader Compilation and a Rejected Optimization|GPU Profiling]] | Working G52 counters, exact-input compiler results, bypass and ABBA candidate experiments. | Bypass changes appearance; the image-matching candidate showed no convincing performance benefit. |

## Connections that matter technically

### Precision and shader cost are connected, but correctness comes first

The [[PROJECT REPORT - Falllinie Native GLES Spike - Deterministic Terrain, Print Shaders and Mali Depth Precision|sampler correction]] and [[PROJECT REPORT - Falllinie Integrated Native Game - Precision, Real-Time Audio, Developer Telemetry and JavaScript Embedding|camera-relative projection correction]] explain why reducing precision is not a free optimization. The [[PROJECT REPORT - Falllinie GPU Profiling - Hardware Counters, Shader Compilation and a Rejected Optimization|compiler investigation]] analyzes the adapted submitted shader, not just the unmodified asset, and retains those constraints.

### Moving audio computation changes scheduling, not the existence of its cost

The [[PROJECT REPORT - Falllinie Buffered Audio - PCM Ownership, Callback Deadlines and Measured Producer Scheduling|buffered transport]] removes synthesis from the callback without claiming to eliminate synthesis work. The [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|perf campaign]] observes producer execution separately from main-thread driver execution. Read these together before interpreting total process CPU or callback timing.

### Newer tools resolve availability questions, not every attribution question

The [[PROJECT REPORT - Falllinie Tracing - CPU Execution, Driver Waits and GPU Attribution|tracing plan]] precedes implementation. [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|Actual measurements]] establish paired-clock/perf results and the current kernel's tracing limitations. [[PROJECT REPORT - Falllinie GPU Profiling - Hardware Counters, Shader Compilation and a Rejected Optimization|The subsequent GPU investigation]] establishes that counters and offline compilation work. None of those later successes repairs the anomalous elapsed-query values or supplies a scheduler trace that was never captured.

### A promising subsystem is not a successful local optimization

The non-parity post bypass and the source-formula-preserving candidate are separate interventions in [[PROJECT REPORT - Falllinie GPU Profiling - Hardware Counters, Shader Compilation and a Rejected Optimization|GPU Profiling]]. Removing the post pass improved tails; the narrow candidate did not. Its fixed fixture matched, but its live ABBA timings did not justify promotion. The [[PROJECT REPORT - Falllinie Rendering Measurements - CPU Execution, Mali Driver Work and GPU Timer Limits|CPU/driver results]] leave other rendering hypotheses open rather than proving that the local shader edit had to succeed.

## Reading rules for comparisons

Preserve each report's workload, runtime revision, clock definition and evidence boundary when comparing numbers. Earlier 60-FPS observations do not qualify later expanded workloads. Whole-device GPU counters do not isolate a render pass, and static compiler estimates are not runtime milliseconds. A conceptual example is not a captured trace; a proposed integration is not an implemented feature.

The cross-link additions are editorial navigation, explicitly requested after publication. Original report bodies, data and figures remain unchanged. Original publication hashes describe their historical versions; the vault's later navigation commit records these additions separately. This index adds no experiment and claims no new optimization result.
