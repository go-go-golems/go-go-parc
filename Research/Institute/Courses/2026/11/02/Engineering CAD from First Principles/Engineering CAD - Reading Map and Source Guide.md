---
title: "Engineering CAD from First Principles — Reading Map and Source Guide"
aliases:
  - "Engineering CAD reading map"
tags:
  - course
  - cad
  - textbook
  - reading-guide
status: active
type: course
created: 2026-11-02
course: "[[Course - Engineering CAD from First Principles]]"
---

# Reading map and source guide

[[Course - Engineering CAD from First Principles|← Contents]]

> [!info] Source
> Imported from the supplied file `jigcad_reading_guide.md` (2026-11-02). Chapter numbers in the tables are links. The browser laboratories it mentions belong to the HTML edition and are not part of these notes.

This expanded edition combines the original 22-chapter CAD survey with ten deeper chapters and 13 additional teaching labs. The supplied books are the basis for the new topology, representation, arrangement, intersection and meshing material. Mathematical examples and implementation exercises are original. The books' historical statements about research status are not presented as current status claims.

## The shortest useful routes

| Goal | Guide chapters |
|---|---|
| Understand the structure of a solid | [[Engineering CAD 01 - A CAD system is a chain of contracts\|1]] → [[Engineering CAD 23 - Solids as regular sets and representation contracts\|23]] → [[Engineering CAD 03 - Topology and boundary representation\|3]] → [[Engineering CAD 24 - Half-edge structures and Euler construction\|24]] → [[Engineering CAD 25 - Simplicial complexes, links and homology\|25]] |
| Implement robust planar geometry | [[Engineering CAD 09 - Reliable decisions in planar geometry\|9]] → [[Engineering CAD 26 - Predicates, constructions and symbolic perturbation\|26]] → [[Engineering CAD 10 - From planar curves to valid profiles\|10]] → [[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction\|27]] → [[Engineering CAD 28 - Delaunay triangulation and quality refinement\|28]] |
| Understand a sketch solver | [[Engineering CAD 04 - Constraints become equations\|4]] → [[Engineering CAD 05 - Jacobians and automatic differentiation\|5]] → [[Engineering CAD 31 - The linear algebra underneath a geometric solver\|31]] → [[Engineering CAD 06 - Newton, Gauss–Newton, DogLeg and LM\|6]] → [[Engineering CAD 07 - Redundancy, conflict and singularity\|7]] → [[Engineering CAD 08 - Continuation, sparse structure and performance\|8]] |
| Understand curved solid operations | [[Engineering CAD 02 - Curves, surfaces and rational geometry\|2]] → [[Engineering CAD 18 - Surface continuity and advanced modeling\|18]] → [[Engineering CAD 29 - Tracing intersections of curved surfaces\|29]] → [[Engineering CAD 11 - Boolean solids, blending and healing\|11]] → [[Engineering CAD 19 - Tolerance, healing and metrology\|19]] |
| Build an application around a kernel | [[Engineering CAD 12 - Identity through parametric edits\|12]] → [[Engineering CAD 13 - Assembly constraints on rigid motions\|13]] → [[Engineering CAD 14 - B-rep, STEP, meshes and manufacturing\|14]] → [[Engineering CAD 15 - A parametric CAD compiler\|15]] → [[Engineering CAD 16 - Rust, WebAssembly and resource ownership\|16]] → [[Engineering CAD 17 - Verification, differential tests and fuzzing\|17]] |
| Generate and simplify meshes | [[Engineering CAD 25 - Simplicial complexes, links and homology\|25]] → [[Engineering CAD 28 - Delaunay triangulation and quality refinement\|28]] → [[Engineering CAD 30 - Tetrahedral quality and topology-safe simplification\|30]] → [[Engineering CAD 14 - B-rep, STEP, meshes and manufacturing\|14]] |

[[Engineering CAD 32 - A source-guided implementation course|Chapter 32]] specifies four projects: a planar subdivision engine, a small B-rep topology library, a curve/surface evaluator, and a geometric constraint solver. Each project includes a supported input domain, worked acceptance case, adversarial tests, and completion evidence.

## Source locators

“Printed page” is the page number printed in the book. “PDF page” is the one-based position in the supplied file, including front matter. The table lists checked anchor pages; do not infer a constant offset for every page of every file.

| Supplied source | Topic and section | Printed anchor | PDF anchor | Expanded guide |
|---|---|---:|---:|---|
| Mäntylä, *An Introduction to Solid Modeling* | Regularity, §3.4.2 | 33 | 51 | [[Engineering CAD 23 - Solids as regular sets and representation contracts\|23]] |
| Mäntylä | MEV and MEF, §9.2.3 | 149 | 167 | [[Engineering CAD 24 - Half-edge structures and Euler construction\|24]] |
| Mäntylä | Euler–Poincaré formula with rings, §9.4.1 | 154 | 172 | [[Engineering CAD 24 - Half-edge structures and Euler construction\|24]] |
| de Berg et al., *Computational Geometry*, 3rd ed. | DCEL orientation, §2.2 | 31 | 41 | [[Engineering CAD 24 - Half-edge structures and Euler construction\|24]], [[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction\|27]] |
| de Berg et al. | DCEL record example | 32 | 42 | [[Engineering CAD 24 - Half-edge structures and Euler construction\|24]], [[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction\|27]] |
| de Berg et al. | Overlay definition, §2.3 | 33 | 43 | [[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction\|27]] |
| Hoffmann, *Geometric and Solid Modeling* | Regularized Booleans, §2.2.2 | 22 | 42 | [[Engineering CAD 23 - Solids as regular sets and representation contracts\|23]] |
| Hoffmann | Approximate coincidence and conditioning, §4.2 | 118 | 138 | [[Engineering CAD 23 - Solids as regular sets and representation contracts\|23]], [[Engineering CAD 26 - Predicates, constructions and symbolic perturbation\|26]] |
| Hoffmann | Numerical tracing scope, §6.1 | 206 | 226 | [[Engineering CAD 29 - Tracing intersections of curved surfaces\|29]] |
| Hoffmann | SVD, §6.2.4 | 216 | 236 | [[Engineering CAD 29 - Tracing intersections of curved surfaces\|29]], [[Engineering CAD 31 - The linear algebra underneath a geometric solver\|31]] |
| Edelsbrunner, *Geometry and Topology for Mesh Generation* | Filtered signs and symbolic perturbation, §1.4 | 22 | 35 | [[Engineering CAD 26 - Predicates, constructions and symbolic perturbation\|26]] |
| Edelsbrunner | Refinement angle bound, §2.3 | 37 | 50 | [[Engineering CAD 28 - Delaunay triangulation and quality refinement\|28]] |
| Edelsbrunner | Stars and links, chapter 3 | 46 | 59 | [[Engineering CAD 25 - Simplicial complexes, links and homology\|25]] |
| Edelsbrunner | Closed-manifold link condition, §4.2 | 74 | 87 | [[Engineering CAD 30 - Tetrahedral quality and topology-safe simplification\|30]] |
| Edelsbrunner | Tetrahedron shape and slivers, §6.2 | 117 | 130 | [[Engineering CAD 30 - Tetrahedral quality and topology-safe simplification\|30]] |

## What is source-derived and what is supplementary?

**Source-derived foundations:** regular closed sets; regularized Booleans; the planar DCEL convention; Euler operators and ring accounting; simplices, stars and links; sweep-line event organization; overlay face labels; empty-circle tests; constrained refinement; predictor–corrector intersection tracing; link conditions for contraction; tetrahedral sliver limitations. Specific source sections accompany these topics in the chapters.

**Original teaching development:** the integer determinant family with exact value −1; the rectangle laboratories; the explicit square-face splice; signed boundary matrices and the small homology implementation; the sphere–plane Newton trace; the parameterized sliver; the two-equation singular-value example; Rust-oriented interface sketches and project acceptance criteria. These are pedagogical derivations and engineering recommendations, not reproduced textbook algorithms claimed to be complete kernels.

**External supplementary references:** Shewchuk's primary papers and reference implementation, LAPACK's official least-squares and orthogonal-factorization documentation, and the official CGAL arrangement manual. The source library also retains the original edition's official software documentation and research references.

**Further study, not supplied full-text sources:** Farin, Piegl–Tiller, Trefethen–Bau, Nocedal–Wright, and the additional topology books named in the research note. Their role is identified as further reading. This expansion does not claim to have read their complete contents from the four uploaded PDFs.

## A study session

Read the definition and derive the smallest example on paper. Predict a lab output before changing its parameter. Change one parameter across a degenerate case. Read the returned diagnostics and the implementation's stated limits. Complete the exercise, then compare the [[Engineering CAD A - Worked Exercise Solutions|worked-solutions appendix]]. Finally, write an input/output contract and one test that would refute an incorrect implementation.

## Limits of the browser laboratories

All labs are independent educational JavaScript implementations. They do not execute JigCAD's Rust solver or OpenCascade. The sweep lab precomputes intersections; the overlay lab handles rectangles; the refinement lab makes one local decision; the tracing lab starts from an analytic seed; and the collapse lab does not perform global self-intersection detection. These limitations are also stated beside each example.

The original JigCAD case studies remain the earlier source-inspection snapshot dated November 2, 2026. This textbook expansion is not a new audit or a comparative performance benchmark of the project.
