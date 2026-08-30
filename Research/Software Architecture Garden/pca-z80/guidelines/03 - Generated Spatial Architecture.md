---
title: PCA-Z80 Research Brief — Generated Spatial Architecture
status: assigned
type: architecture-garden-research-guideline
created: 2026-08-29
repository: /home/manuel/code/wesen/2026-08-28--pca-gatemate
repository_commit: c07e700652732cd7264af6e2473eb1c6e1f20cc9
pattern_maturity: established-locally
tags: [architecture-garden, pca-z80, placement, generation, noc]
related_notes:
  - "[[Research/Software Architecture Garden/pca-z80/index]]"
  - "[[Research/Software Architecture Garden/pca-z80/guidelines/00 - Shared Research and Subentry Guidelines]]"
---

# Generated Spatial Architecture — Research Brief

## Assignment

Write `designs/03 - Generated Spatial Architecture.md`. Explain how a logical object graph is compiled into deterministic coordinates, route evidence, generated RTL constants, and endpoint wiring. Evaluate when generated spatial configuration is preferable to handwritten topology or runtime discovery.

## Central question

How does the build turn architectural identity and communication demand into a reproducible spatial implementation without creating a second handwritten authority?

## Required local evidence

Read completely:

- `pca_z80/config/z80_objects.json`
- `pca_z80/tools/placer.py`
- `pca_z80/sim/test_placer.py`
- generated `build/placement.json`
- generated `build/pca_placement_pkg.sv`
- `pca_z80/rtl/z80_mesh_core.sv`
- `pca_z80/rtl/pca_types.sv`
- `pca_z80/Makefile`

Read design-docs 04–06 and diary Steps 28–30 and 33. Re-run generation from a clean build directory.

## Required artifact trace

Trace one object, such as `OBJ_FLAGS`, through:

```text
object id/name in input JSON
→ validation and canonicalization
→ weighted degree and candidate cost
→ selected (x,y)
→ cell_id and exact XY route metadata
→ generated scalar constants
→ local-port wiring in z80_mesh_core
→ routed request in simulation
```

Record every place where identity could drift and the mechanism preventing it.

## External research requirements

Research:

1. graph placement and weighted Manhattan objectives;
2. network-on-chip task mapping and topology-aware placement;
3. deterministic/reproducible code generation;
4. placement heuristics versus exact optimization;
5. exact XY routing and deadlock properties;
6. architecture-description languages or hardware generators;
7. one independent generated-topology RTL project.

Use original NoC/task-mapping papers, established VLSI placement texts, and maintained generator implementations. Identify where PCA-Z80's simple greedy algorithm departs from literature-grade placement.

## Required experiments

Run and record:

1. identical input twice → byte-identical JSON and SV;
2. reordered arrays → equivalent canonical output;
3. one fixed-coordinate case;
4. one capacity or collision rejection;
5. one topology variation and its weighted-hop/resource consequence.

Inspect whether `--check` modifies files. It must not.

## Required design analysis

Explain:

- why JSON is canonical and SV is generated;
- why source hashes use the canonical model rather than raw bytes;
- why deterministic tie-breaking includes `(cost,y,x)`;
- why exact route paths are evidence while routers compute next hops at runtime;
- why scalar constants replaced unpacked arrays under Icarus;
- why 3×2 is physical topology rather than merely a prettier placement;
- why this remains logical placement, not runtime LUT relocation.

## Pattern forces

Analyze determinism, optimization quality, tool compatibility, reviewability, stale artifacts, topology capacity, physical resource cost, and future extensibility.

## Textbook structure

Start with the danger of coordinate knowledge existing in multiple handwritten files. Include:

- a graph-to-artifact pipeline diagram;
- the input and output schema fragments;
- pseudocode for placement and tie-breaking;
- a table of canonicalization invariants;
- a trace for one object;
- valid/rejection experiment results;
- comparison with alternative placement approaches.

## Candidate subentries

- Canonical Generated Artifact.
- Stable Input Hash After Canonicalization.
- Generated Scalar Placement Package.
- Stale-Artifact Check.
- Exact XY Route Metadata.

## Definition of done

A reviewer can regenerate coordinates, explain why output is deterministic, distinguish route metadata from runtime routing, identify algorithmic limits, and state why generated placement is architecture rather than build convenience.
