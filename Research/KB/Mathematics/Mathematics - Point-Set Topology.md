---
title: "Mathematics - Point-Set Topology"
aliases:
  - "Point-set topology"
  - "General topology"
  - "Regularized sets"
tags:
  - knowledge-base
  - mathematics
  - topology
  - cad
status: active
type: knowledge-base
created: "2026-11-02"
---

# Point-Set Topology

Point-set (general) topology studies sets with a notion of nearness: open and closed sets, interior, closure, boundary, continuity and manifolds. In solid modeling it gives the definition of a solid as a set of points and explains what a Boolean operation on solids should return.

Part of [[Mathematics]].

> [!summary]
> - A solid is first a point set: membership comes before any picture or data structure.
> - Regularization (closure of the interior) removes dangling faces, edges and points, which is why regularized Booleans differ from set Booleans.
> - Regular is not the same as manifold; a representation policy chooses which of the two it supports.

## Concepts

- Open and closed sets, interior, closure, boundary; dependence on the ambient dimension.
- Regular closed sets and regularized union, intersection and difference.
- Jordan curves: one outer boundary and inner boundaries of a planar profile.
- Manifolds and manifold boundaries; regularity does not imply manifoldness.
- Tangency and slivers as topological events under perturbation.
- Locales and frames: topology described through the lattice of open sets (Vickers).

## In the CAD textbook

[[Course - Engineering CAD from First Principles]] treats this topic in:

- [[Engineering CAD 10 - From planar curves to valid profiles|Chapter 10. From planar curves to valid profiles]]: define the filled set before implementing it; tangency is a topological event.
- [[Engineering CAD 11 - Boolean solids, blending and healing|Chapter 11. Boolean solids, blending and healing]]: sets first, representations second; a two-circle calculation.
- [[Engineering CAD 19 - Tolerance, healing and metrology|Chapter 19. Tolerance, healing and metrology]]: modeling tolerance as a topological policy.
- [[Engineering CAD 23 - Solids as regular sets and representation contracts|Chapter 23. Solids as regular sets and representation contracts]]: membership, regularization, solid Booleans, and why regular is not manifold.

## Elsewhere in the vault

### Projects and articles

- [[PROJECT REPORT - book-ocr - A Go-Hosted OCR Workbench and the Full Conversion of Topology via Logic]]: the full conversion of Steven Vickers' *Topology via Logic*: topology through frames, locales and lattices.

### Foundations research

- [[Research/Institute/Research/2026/04/16/philosophical-foundations-of-mathematics/sources/web/nlab-constructive-mathematics|nLab: constructive mathematics]]: locales and topological spaces in constructive mathematics.
- [[Research/Institute/Research/2026/04/16/philosophical-foundations-of-mathematics/sources/web/wikipedia-reverse-mathematics|Reverse mathematics (source)]]: which axioms the Jordan curve theorem and closed-set results need.
- [[Research/Institute/Research/2026/04/16/philosophical-foundations-of-mathematics/sources/web/wikipedia-computable-analysis|Computable analysis (source)]]: open and closed sets as computational objects.

### Transcript textbooks

- [[Transcripts/2026/08/16/Branch Cohomology explanation/sessionstream_sheaves_topoi_textbook|SessionStream sheaves and topoi textbook]]: open sets and topological spaces as the base for presheaves and sheaves over a software system.
- [[Transcripts/2026/08/15/Cohomology explanation/Session-Spaces-Custom-Textbook|Session spaces textbook]]: topological spaces built from sessions and their overlaps.

## Gaps

The vault approaches topology from logic and sheaves (Vickers, Goldblatt) rather than from geometry. The CAD textbook's chapter 23 is the only note that uses point-set topology to define solids.

## Related topics

- [[Mathematics - Combinatorial and Algebraic Topology]]
- [[Mathematics - Computational Geometry]]
- [[Mathematics - Tolerancing, Uncertainty and Statistics]]
