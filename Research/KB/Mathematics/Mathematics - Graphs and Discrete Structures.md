---
title: "Mathematics - Graphs and Discrete Structures"
aliases:
  - "Graphs and discrete structures"
  - "DAGs"
  - "Incremental computation"
  - "Order theory"
tags:
  - knowledge-base
  - mathematics
  - discrete-math
  - graphs
status: active
type: knowledge-base
created: "2026-11-02"
---

# Graphs and Discrete Structures

Discrete mathematics covers graphs, orders, lattices and relations. In a parametric CAD system the feature tree is a directed acyclic graph, caching depends on its dependency structure, and persistent naming is a correspondence relation between topologies before and after an edit.

Part of [[Mathematics]].

> [!summary]
> - A feature tree is a DAG; a cached result is valid only if every upstream input it depends on is unchanged.
> - Persistent identity is not geometric equality: split and merge are relations between old and new faces, not functions.
> - Orders and lattices appear wherever results are merged or refined: fixpoints, monotone analyses, mergeable summaries.

## Concepts

- Directed acyclic graphs, topological order, dependency graphs.
- Cache keys and incremental recomputation.
- Correspondence relations for split and merge; provenance graphs.
- Partial orders, lattices, fixpoints; monoids for mergeable summaries.

## In the CAD textbook

[[Course - Engineering CAD from First Principles]] treats this topic in:

- [[Engineering CAD 12 - Identity through parametric edits|Chapter 12. Identity through parametric edits]]: identity through parametric edits, provenance, split and merge as correspondence relations.
- [[Engineering CAD 15 - A parametric CAD compiler|Chapter 15. A parametric CAD compiler]]: the feature tree as a DAG, the cache correctness condition, transactions.

## Elsewhere in the vault

### Projects and articles

- [[ARTICLE - Textbook - Weft, From First Principles]]: a JavaScript API for FPGA design whose compiler works on circuit graphs.
- [[ARTICLE - Engineering Temporal Systems - 03 - Mergeable Summaries]]: which summaries can be combined correctly across groups, and why averaging averages loses meaning.
- [[PROJECT REPORT - PBUI Linked Tiles - Interaction Models, Formal Semantics, and an Architecture for Routing, Binding, and Coordination]]: formal semantics of routing and binding between tiles.
- [[ARTICLE - ServiceLang Mathematics - Ownership Dataflow and Semantic Preservation]]: a dataflow model of ownership and a proof that the backend preserves it.
- [[ARTICLE - GateMate Symbolic - Inside a Lazy Graph Reducer]]: graph reduction implemented in FPGA logic.
- [[PROJECT REPORT - From Pattern Zoos to an Architecture Garden - A Shared Mathematical Vocabulary for Composable Systems]]: a shared vocabulary (orders, algebras, morphisms) across many generated research artifacts.

### Research hubs

- [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook|PBUI-MATHS Pattern Zoo Handbook]]: lattices, orders and graphs for presentation-based UIs.
- [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo|RAG-MATHS Pattern Zoo]]: the same for retrieval systems.

## Gaps

Discrete structures are everywhere in the vault's software-architecture work. The CAD-specific problem, persistent naming across topology edits, is covered only in the textbook and the jigcad reports.

## Related topics

- [[Mathematics - Combinatorial and Algebraic Topology]]
- [[Mathematics - Computational Geometry]]
- [[Mathematics - Tolerancing, Uncertainty and Statistics]]
