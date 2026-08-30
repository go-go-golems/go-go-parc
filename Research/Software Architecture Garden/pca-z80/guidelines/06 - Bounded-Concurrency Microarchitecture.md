---
title: PCA-Z80 Research Brief — Bounded-Concurrency Microarchitecture
status: assigned
type: architecture-garden-research-guideline
created: 2026-08-29
repository: /home/manuel/code/wesen/2026-08-28--pca-gatemate
repository_commit: c07e700652732cd7264af6e2473eb1c6e1f20cc9
pattern_maturity: established-locally
tags: [architecture-garden, pca-z80, concurrency, serialization, microarchitecture]
related_notes:
  - "[[Research/Software Architecture Garden/pca-z80/index]]"
  - "[[Research/Software Architecture Garden/pca-z80/guidelines/00 - Shared Research and Subentry Guidelines]]"
---

# Bounded-Concurrency Microarchitecture — Research Brief

## Assignment

Write `designs/06 - Bounded-Concurrency Microarchitecture.md`. Analyze the deliberate choice to permit one end-to-end object transaction in flight and one packet per router. Explain the correctness, area, latency, and scaling consequences without presenting serialization as universally desirable.

## Central question

When does reducing concurrency make an architecture easier to prove and implement, and when does the same restriction become the dominant performance limit?

## Required local evidence

Read completely:

- `pca_z80/rtl/obj_decode.sv` request sequencing;
- `pca_z80/rtl/z80_mesh_adapter.sv` master states;
- `pca_z80/rtl/pca_router.sv` arbitration and one-packet state;
- `pca_z80/rtl/z80_mesh_core.sv` counters and composition;
- direct and mesh integration tests;
- blink-rate measurement script 20;
- P5 routing evidence.

Identify exactly where new work is prevented from entering and where buffers do or do not exist.

## Required quantitative analysis

Use at least two measurements:

1. direct versus mesh blink transition cycles;
2. one assembled program's retired instructions versus mesh transactions and cycles.

Derive or measure:

- average object transactions per instruction for the chosen program;
- round-trip latency by route length;
- throughput upper bound under one in-flight transaction;
- packet/router storage requirements;
- what metadata would be required for two or more outstanding requests.

Label approximations and assumptions.

## External research requirements

Research:

1. finite-state serialized microarchitectures;
2. Kahn process networks and CSP-style communication where relevant;
3. latency-insensitive design;
4. network-on-chip flow control;
5. store-and-forward versus wormhole or virtual-channel routing;
6. tagged/outstanding bus transactions;
7. reorder buffers and response correlation;
8. queueing/backpressure trade-offs.

Use original or authoritative sources from NoC and computer-architecture literature. Compare PCA-Z80's one-flit, one-in-flight design with at least one architecture that supports multiple outstanding transactions.

## Required experiment

Run one of:

- instrument per-hop request/response cycle latency;
- compare programs with different object-transaction density;
- add a test-only source attempting a second request and document how it is blocked;
- model the additional state/fields required for two outstanding transactions.

Do not implement production concurrency as part of the research assignment.

## Required argument

Explain which structures disappear under the bound:

- transaction IDs;
- outstanding-request tables;
- response reordering;
- endpoint queues;
- multi-response arbitration;
- timeout ownership for concurrent operations.

Then explain the cost:

- accumulated round-trip latency;
- low network utilization;
- serialized independent object work;
- slow firmware-visible loops;
- limited scalability.

Separate processor serialization from router arbitration; they are related bounds at different layers.

## Textbook structure

Begin with the concrete one-in-flight contract and its proof surface. Introduce alternatives only after the baseline is understood. Include a state-space comparison table, a latency path diagram, measured cycle data, and a scoped evolution plan for adding concurrency safely.

## Candidate subentries

- One Transaction in Flight.
- Fixed-Priority Single-Packet Router.
- Correlation Without Transaction IDs.
- Serialization as Proof-Surface Reduction.
- Direct-versus-Mesh Latency Measurement.

## Definition of done

A reviewer can identify every serialization point, quantify one latency consequence, list the machinery avoided by the bound, and state concrete workload/scale conditions under which the pattern should be rejected or evolved.
