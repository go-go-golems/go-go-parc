---
title: "Mathematics - Combinatorial and Algebraic Topology"
aliases:
  - "Algebraic topology"
  - "Combinatorial topology"
  - "Homology"
  - "Euler characteristic"
tags:
  - knowledge-base
  - mathematics
  - topology
  - cad
status: active
type: knowledge-base
created: "2026-11-02"
---

# Combinatorial and Algebraic Topology

Combinatorial topology describes shapes by finite pieces (vertices, edges, faces, simplices) and how they attach; algebraic topology attaches algebra to those pieces (chain complexes, homology) to count holes. In CAD this is the *topology* layer of a B-rep and the theory behind mesh validity.

Part of [[Mathematics]].

> [!summary]
> - Topology is the connectivity a B-rep stores; geometry is what each piece is attached to. Both must be valid, separately.
> - The Euler characteristic V − E + F constrains any valid construction; faces with holes (rings) correct the formula.
> - Homology counts holes from boundary matrices; Betti numbers and edge counts alone do not prove a mesh is a manifold.

## Concepts

- Half-edge structures, the DCEL, directed edge uses, face cycles.
- Euler characteristic and genus; Euler–Poincaré with rings; Euler operators (MEV, MEF) as local constructions with preconditions.
- Simplices, affine independence, simplicial complexes, stars and links.
- Oriented simplices, the boundary operator, ∂∘∂ = 0, chain complexes.
- Cycles modulo boundaries: homology groups and Betti numbers from matrix ranks.
- The link condition for edge contraction in mesh simplification.

## In the CAD textbook

[[Course - Engineering CAD from First Principles]] treats this topic in:

- [[Engineering CAD 03 - Topology and boundary representation|Chapter 3. Topology and boundary representation]]: geometry versus topology, half-edges, pcurves, Euler characteristic and genus.
- [[Engineering CAD 24 - Half-edge structures and Euler construction|Chapter 24. Half-edge structures and Euler construction]]: half-edge invariants, a face split traced pointer by pointer, Euler operations, rings.
- [[Engineering CAD 25 - Simplicial complexes, links and homology|Chapter 25. Simplicial complexes, links and homology]]: simplicial complexes, stars and links, boundaries, homology, Euler characteristic as an alternating sum.
- [[Engineering CAD 30 - Tetrahedral quality and topology-safe simplification|Chapter 30. Tetrahedral quality and topology-safe simplification]]: edge contraction and the link condition.

## Elsewhere in the vault

### Transcript textbooks and research

- [[Transcripts/2026/08/16/Branch Cohomology explanation/sessionstream_sheaves_topoi_textbook|SessionStream sheaves and topoi textbook]]: chain complexes, simplicial complexes, Betti numbers and elementary cohomology applied to SessionStream consistency.
- [[Transcripts/2026/08/16/Branch Cohomology explanation/local-truth-in-sessionstream|Local truth in SessionStream]]: homology and Betti numbers of overlapping local views.
- [[Transcripts/2026/08/16/Branch Cohomology explanation/sessionstream_local_to_global|SessionStream: local to global]]: cohomology as the obstruction to gluing local state into a global one.
- [[Transcripts/2026/08/16/Branch Cohomology explanation/local-truth-global-execution-sessionstream|Local truth, global execution]]: chain complexes and cohomology for distributed execution.
- [[Transcripts/2026/08/15/CHATGPT TRANSCRIPT - Cohomology explanation|Cohomology explanation (transcript)]]: the conversation that produced these: can local API data be glued into a consistent global state?
- [[Research/Institute/Research/2026/04/16/philosophical-foundations-of-mathematics/sources/web/nlab-computational-trilogy|nLab: computational trilogy]]: homotopy and cohomology in the logic–types–categories correspondence.

### Projects and articles

- [[PROJECT REPORT - jigcad - Architecture of a Browser CAD Workbench, from Script to Agent]]: the named faces and edges of a jigcad Program come from the OpenCascade B-rep topology.

## Gaps

The vault's algebraic topology is about sheaves and cohomology for software consistency. The CAD textbook is the only material on half-edges, Euler operators and mesh links; no note yet compares the two uses.

## Related topics

- [[Mathematics - Point-Set Topology]]
- [[Mathematics - Computational Geometry]]
- [[Mathematics - Graphs and Discrete Structures]]
