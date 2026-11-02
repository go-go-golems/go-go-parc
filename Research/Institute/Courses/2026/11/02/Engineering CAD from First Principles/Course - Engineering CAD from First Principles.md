---
title: "Course - Engineering CAD from First Principles"
aliases:
  - "Engineering CAD from First Principles"
  - "Engineering CAD textbook"
  - "jigcad textbook"
tags:
  - course
  - cad
  - textbook
  - jigcad
  - computational-geometry
status: active
type: course
created: 2026-11-02
repo: /home/manuel/code/wesen/go-go-golems/jig
---

# Engineering CAD from First Principles

Expanded source-guided edition. Original survey plus ten deeper chapters based on the supplied solid-modeling and computational-geometry texts. JigCAD observations are inherited from the earlier 2026-11-02 source-inspection snapshot; this expansion is not a fresh kernel benchmark.

> [!summary]
> - Chapters 1–22 survey a parametric CAD system end to end: geometry, topology, constraint solving, Booleans, identity, assemblies, exchange formats, the compiler, verification and manufacturing, with JigCAD as the running case study.
> - Chapters 23–32 go deeper from the solid-modeling and computational-geometry books (Mäntylä, Hoffmann, de Berg et al., Edelsbrunner): regular sets, half-edges and Euler operators, links and homology, robust predicates, sweeps and overlays, Delaunay refinement, surface intersection, tetrahedral meshes, and the linear algebra of solvers.
> - Chapter 32 ends with four implementation projects with acceptance tests; appendix A has worked exercise solutions, appendix B the source library.

> [!info] Source
> Imported from the supplied file `jigcad_textbook_expanded.md` (2026-11-02). The text is kept as supplied; only chapter and source-library links were rewritten into wikilinks.

The JigCAD project the case studies inspect is mapped in [[jigcad]].

## Reading routes

The [[Engineering CAD - Reading Map and Source Guide|reading map]] gives short routes through the book for one goal each, and page anchors into the supplied books.

| Goal | Route |
|---|---|
| Understand the structure of a solid | [[Engineering CAD 01 - A CAD system is a chain of contracts\|1]] → [[Engineering CAD 23 - Solids as regular sets and representation contracts\|23]] → [[Engineering CAD 03 - Topology and boundary representation\|3]] → [[Engineering CAD 24 - Half-edge structures and Euler construction\|24]] → [[Engineering CAD 25 - Simplicial complexes, links and homology\|25]] |
| Implement robust planar geometry | [[Engineering CAD 09 - Reliable decisions in planar geometry\|9]] → [[Engineering CAD 26 - Predicates, constructions and symbolic perturbation\|26]] → [[Engineering CAD 10 - From planar curves to valid profiles\|10]] → [[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction\|27]] → [[Engineering CAD 28 - Delaunay triangulation and quality refinement\|28]] |
| Understand a sketch solver | [[Engineering CAD 04 - Constraints become equations\|4]] → [[Engineering CAD 05 - Jacobians and automatic differentiation\|5]] → [[Engineering CAD 31 - The linear algebra underneath a geometric solver\|31]] → [[Engineering CAD 06 - Newton, Gauss–Newton, DogLeg and LM\|6]] → [[Engineering CAD 07 - Redundancy, conflict and singularity\|7]] → [[Engineering CAD 08 - Continuation, sparse structure and performance\|8]] |
| Understand curved solid operations | [[Engineering CAD 02 - Curves, surfaces and rational geometry\|2]] → [[Engineering CAD 18 - Surface continuity and advanced modeling\|18]] → [[Engineering CAD 29 - Tracing intersections of curved surfaces\|29]] → [[Engineering CAD 11 - Boolean solids, blending and healing\|11]] → [[Engineering CAD 19 - Tolerance, healing and metrology\|19]] |
| Build an application around a kernel | [[Engineering CAD 12 - Identity through parametric edits\|12]] → [[Engineering CAD 13 - Assembly constraints on rigid motions\|13]] → [[Engineering CAD 14 - B-rep, STEP, meshes and manufacturing\|14]] → [[Engineering CAD 15 - A parametric CAD compiler\|15]] → [[Engineering CAD 16 - Rust, WebAssembly and resource ownership\|16]] → [[Engineering CAD 17 - Verification, differential tests and fuzzing\|17]] |
| Generate and simplify meshes | [[Engineering CAD 25 - Simplicial complexes, links and homology\|25]] → [[Engineering CAD 28 - Delaunay triangulation and quality refinement\|28]] → [[Engineering CAD 30 - Tetrahedral quality and topology-safe simplification\|30]] → [[Engineering CAD 14 - B-rep, STEP, meshes and manufacturing\|14]] |

## Contents

### Part I. The original survey (chapters 1–22)

- [[Engineering CAD 01 - A CAD system is a chain of contracts|Chapter 1. A CAD system is a chain of contracts]]
- [[Engineering CAD 02 - Curves, surfaces and rational geometry|Chapter 2. Curves, surfaces and rational geometry]]
- [[Engineering CAD 03 - Topology and boundary representation|Chapter 3. Topology and boundary representation]]
- [[Engineering CAD 04 - Constraints become equations|Chapter 4. Constraints become equations]]
- [[Engineering CAD 05 - Jacobians and automatic differentiation|Chapter 5. Jacobians and automatic differentiation]]
- [[Engineering CAD 06 - Newton, Gauss–Newton, DogLeg and LM|Chapter 6. Newton, Gauss–Newton, DogLeg and LM]]
- [[Engineering CAD 07 - Redundancy, conflict and singularity|Chapter 7. Redundancy, conflict and singularity]]
- [[Engineering CAD 08 - Continuation, sparse structure and performance|Chapter 8. Continuation, sparse structure and performance]]
- [[Engineering CAD 09 - Reliable decisions in planar geometry|Chapter 9. Reliable decisions in planar geometry]]
- [[Engineering CAD 10 - From planar curves to valid profiles|Chapter 10. From planar curves to valid profiles]]
- [[Engineering CAD 11 - Boolean solids, blending and healing|Chapter 11. Boolean solids, blending and healing]]
- [[Engineering CAD 12 - Identity through parametric edits|Chapter 12. Identity through parametric edits]]
- [[Engineering CAD 13 - Assembly constraints on rigid motions|Chapter 13. Assembly constraints on rigid motions]]
- [[Engineering CAD 14 - B-rep, STEP, meshes and manufacturing|Chapter 14. B-rep, STEP, meshes and manufacturing]]
- [[Engineering CAD 15 - A parametric CAD compiler|Chapter 15. A parametric CAD compiler]]
- [[Engineering CAD 16 - Rust, WebAssembly and resource ownership|Chapter 16. Rust, WebAssembly and resource ownership]]
- [[Engineering CAD 17 - Verification, differential tests and fuzzing|Chapter 17. Verification, differential tests and fuzzing]]
- [[Engineering CAD 18 - Surface continuity and advanced modeling|Chapter 18. Surface continuity and advanced modeling]]
- [[Engineering CAD 19 - Tolerance, healing and metrology|Chapter 19. Tolerance, healing and metrology]]
- [[Engineering CAD 20 - Manufacturing, drawings and sheet metal|Chapter 20. Manufacturing, drawings and sheet metal]]
- [[Engineering CAD 21 - Design-space search and robust optimization|Chapter 21. Design-space search and robust optimization]]
- [[Engineering CAD 22 - Engineering a trustworthy next version|Chapter 22. Engineering a trustworthy next version]]

### Part II. Source-guided deep chapters (23–32)

- [[Engineering CAD 23 - Solids as regular sets and representation contracts|Chapter 23. Solids as regular sets and representation contracts]]
- [[Engineering CAD 24 - Half-edge structures and Euler construction|Chapter 24. Half-edge structures and Euler construction]]
- [[Engineering CAD 25 - Simplicial complexes, links and homology|Chapter 25. Simplicial complexes, links and homology]]
- [[Engineering CAD 26 - Predicates, constructions and symbolic perturbation|Chapter 26. Predicates, constructions and symbolic perturbation]]
- [[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction|Chapter 27. Plane sweep, DCEL overlays and profile extraction]]
- [[Engineering CAD 28 - Delaunay triangulation and quality refinement|Chapter 28. Delaunay triangulation and quality refinement]]
- [[Engineering CAD 29 - Tracing intersections of curved surfaces|Chapter 29. Tracing intersections of curved surfaces]]
- [[Engineering CAD 30 - Tetrahedral quality and topology-safe simplification|Chapter 30. Tetrahedral quality and topology-safe simplification]]
- [[Engineering CAD 31 - The linear algebra underneath a geometric solver|Chapter 31. The linear algebra underneath a geometric solver]]
- [[Engineering CAD 32 - A source-guided implementation course|Chapter 32. A source-guided implementation course]]

### Appendices

- [[Engineering CAD A - Worked Exercise Solutions|Appendix A. Worked exercise solutions]]
- [[Engineering CAD B - Source Library|Appendix B. Source library]]

## Related notes

- [[jigcad]] — the JigCAD project map: the system the case studies inspect.
- [[Engineering CAD - Reading Map and Source Guide]] — routes, source locators, and what is source-derived.
- [[Mathematics]]: the mathematics map; each branch the book touches has a topic map that links back to the chapters.
