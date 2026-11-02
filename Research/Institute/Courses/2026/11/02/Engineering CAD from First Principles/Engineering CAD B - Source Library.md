---
title: "Engineering CAD from First Principles — Appendix B. Source library"
aliases:
  - "Source library"
tags:
  - course
  - cad
  - textbook
  - jigcad
status: active
type: course
created: 2026-11-02
course: "[[Course - Engineering CAD from First Principles]]"
---

# Appendix B. Source library

[[Engineering CAD A - Worked Exercise Solutions|← Appendix A. Worked exercise solutions]] · [[Course - Engineering CAD from First Principles|Contents]]

**OCCT-overview** — [Technical overview and modeling data](https://www.occt3d.com/dev/doc/overview/html/index.html). Open CASCADE Technology. Architecture: geometry, topology, modeling algorithms and data exchange. ^ref-OCCT-overview

**OCCT-brep** — [BREP format specification](https://occt3d.com/dev/doc/overview/html/specification__brep_format.html). Open CASCADE Technology. Vertices, edges, wires, faces, shells, orientations and persistent representations. ^ref-OCCT-brep

**OCCT-booleans** — [Boolean operations user guide](https://www.occt3d.com/dev/doc/overview/html/specification__boolean_operations.html). Open CASCADE Technology. Intersection, splitting, classification, rebuilding and modification history. ^ref-OCCT-booleans

**OCCT-healing** — [Shape Healing user guide](https://www.occt3d.com/dev/doc/overview/html/occt_user_guides__shape_healing.html). Open CASCADE Technology. Analysis, wire repair, tolerance management and shape normalization. ^ref-OCCT-healing

**OCCT-step** — [STEP translator user guide](https://occt3d.com/dev/doc/overview/html/occt_user_guides__step.html). Open CASCADE Technology. STEP translators, XDE assembly metadata, names, colors and GD&T. ^ref-OCCT-step

**OCCT-wire** — [ShapeAnalysis_Wire class reference](https://dev.opencascade.org/doc/occt-7.6.0/refman/html/class_shape_analysis___wire.html). Open CASCADE Technology. Wire ordering, connectivity, degeneracy and self-intersection diagnostics. ^ref-OCCT-wire

**OCCT-ocaf** — [OCAF overview](https://www.occt3d.com/dev/doc/overview/html/occt_user_guides__ocaf.html). Open CASCADE Technology. Application-data framework, labels and model history. ^ref-OCCT-ocaf

**CGAL-arr** — [2D Arrangements user manual](https://doc.cgal.org/latest/Arrangement_on_surface_2/index.html). CGAL Project. Planar subdivisions, exact curve predicates and arrangement data structures. ^ref-CGAL-arr

**Shewchuk** — [Adaptive Precision Floating-Point Arithmetic and Fast Robust Geometric Predicates](https://people.eecs.berkeley.edu/~jrs/papers/robustr.pdf). Jonathan Richard Shewchuk. Adaptive exact orientation and incircle tests for robust geometry. ^ref-Shewchuk

**FreeCAD-naming** — [Topological naming problem](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Topological_naming_problem.md). FreeCAD project. A practical account of unstable topology references and their limits. ^ref-FreeCAD-naming

**Nocedal** — [Numerical Optimization (2nd ed.)](https://link.springer.com/book/10.1007/978-0-387-40065-5). Jorge Nocedal and Stephen Wright. Trust-region methods, Newton, Gauss–Newton and nonlinear least squares. ^ref-Nocedal

**Baydin** — [Automatic Differentiation in Machine Learning: A Survey](https://www.jmlr.org/papers/v18/17-468.html). A. G. Baydin et al.. Forward and reverse automatic differentiation with computational graphs. ^ref-Baydin

**SolveSpace** — [Constraint solver tutorial](https://solvespace.com/constraints.pl). SolveSpace. Practical constraint branches, redundancy and solver failures. ^ref-SolveSpace

**SolveSpace-ref** — [Reference manual](https://solvespace.com/ref.pl). SolveSpace. Constrained modeling, reference dimensions and 3D constraints. ^ref-SolveSpace-ref

**Piegl** — [The NURBS Book (2nd ed.)](https://link.springer.com/book/10.1007/978-3-642-59223-2). Les Piegl and Wayne Tiller. Basis functions, exact rational conics, curve fitting and surface construction. ^ref-Piegl

**ModernRobotics** — [Modern Robotics: Mechanics, Planning, and Control](https://modernrobotics.northwestern.edu/). Kevin Lynch and Frank Park. Rigid transforms, Lie groups, kinematics, Jacobians and loop closure. ^ref-ModernRobotics

**WasmSpec** — [WebAssembly Core Specification](https://www.w3.org/TR/wasm-core/). W3C. Linear memory, modules, functions and portability guarantees. ^ref-WasmSpec

**ThreeMF** — [3MF Core Specification v1.3](https://3mf.io/wp-content/uploads/sites/106/2025/02/3MF_Core_Specification_v1.3.0.pdf). 3MF Consortium. Watertight triangle topology, model units and package structure. ^ref-ThreeMF

**Jig-README** — [JigCAD repository README](https://github.com/go-go-golems/jig/blob/main/README.md). go-go-golems. Project entry point and workbench aims. ^ref-Jig-README

**Jig-build** — [JigCAD build contract](https://github.com/go-go-golems/jig/blob/main/import/jigcad/BUILD.md). go-go-golems. Worker protocol, program data and system architecture. ^ref-Jig-build

**Jig-kernel** — [JigCAD kernel API status](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/KERNEL-API.md). go-go-golems. Documented implemented, partial and unsupported modeling features. ^ref-Jig-kernel

**Jig-core** — [JigCAD core API](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/CORE-API.md). go-go-golems. Dimensions, expressions, sketches and patterns. ^ref-Jig-core

**Jig-issues** — [Book issues and correction status](https://github.com/go-go-golems/jig/blob/main/import/jigcad/BOOK-ISSUES.md). go-go-golems. Source-reported correctness cases and unresolved limitations. ^ref-Jig-issues

**Jig-solve** — [jig-compute Rust nonlinear solver](https://github.com/go-go-golems/jig/blob/main/import/jigcad/rust/jig-compute/src/solve.rs). go-go-golems. DogLeg, LM, Newton and dragging in Rust/WASM. ^ref-Jig-solve

**Jig-linalg** — [jig-compute dense linear algebra](https://github.com/go-go-golems/jig/blob/main/import/jigcad/rust/jig-compute/src/linalg.rs). go-go-golems. Householder QR, rank and Cholesky. ^ref-Jig-linalg

**Jig-tape** — [jig-compute tape reverse-mode derivatives](https://github.com/go-go-golems/jig/blob/main/import/jigcad/rust/jig-compute/src/tape.rs). go-go-golems. Reverse AD interpreter for residual expressions. ^ref-Jig-tape

**Jig-sketch** — [Sketch solver orchestration](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/sketch/solver.js). go-go-golems. Cluster decomposition, conflict selection and fallback behavior. ^ref-Jig-sketch

**Jig-profiles** — [Sketch profile builder](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/sketch/profiles.js). go-go-golems. Planar intersection splitting, half-edge walks and containment. ^ref-Jig-profiles

**Jig-shapes** — [Geometric shape constructors](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/shapes.js). go-go-golems. Profiles to wires, faces, prisms, sweeps and lofts. ^ref-Jig-shapes

**Jig-ops** — [OpenCascade operation wrappers](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/ops.js). go-go-golems. Boolean, fillet, chamfer and shell implementations. ^ref-Jig-ops

**Jig-name** — [Topology provenance implementation](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/body.js). go-go-golems. Generated/Modified/IsDeleted propagation and split suffixes. ^ref-Jig-name

**Jig-assembly** — [Assembly placement and joint evaluation](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/assembly.js). go-go-golems. Port transforms, joint handling and interference. ^ref-Jig-assembly

**Jig-io** — [CAD export implementation](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/io.js). go-go-golems. STEP, STL, 3MF, SVG and IR bundle exports. ^ref-Jig-io

**Jig-cache** — [Parametric feature compilation and cache](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/compile.js). go-go-golems. Feature keys, parameter dependencies and cache reuse. ^ref-Jig-cache

**Jig-wasm** — [Rust WebAssembly loader and FFI](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/rs/wasm.js). go-go-golems. WASM instantiation, linear-memory marshalling and JS fallback. ^ref-Jig-wasm

**Jig-tests** — [Rust/JS numerical parity tests](https://github.com/go-go-golems/jig/blob/main/import/jigcad/test/rs/parity.mjs). go-go-golems. Differential testing of Rust and JS calculations. ^ref-Jig-tests

**Jig-agents** — [Agent evaluation harness](https://github.com/go-go-golems/jig/blob/main/import/jigcad/test/agent-eval/harness.test.mjs). go-go-golems. Model-edit checks and oracle testing. ^ref-Jig-agents

**Jig-ci** — [GitHub Actions CI workflow](https://github.com/go-go-golems/jig/blob/main/.github/workflows/push.yml). go-go-golems. Actual build and test coverage in continuous integration. ^ref-Jig-ci

**OCCT-modeling-data** — [Modeling Data and continuity of curves and surfaces](https://documentation.help/Open-Cascade/occt_user_guides__modeling_data.html). Open CASCADE Technology. G0/G1/G2 and C0/C1/C2 continuity semantics and geometry types. ^ref-OCCT-modeling-data

**BIPM-GUM** — [Guide to the Expression of Uncertainty in Measurement and related publications](https://www.bipm.org/en/committees/jc/jcgm/publications). BIPM and JCGM. Engineering measurement uncertainty and reporting. ^ref-BIPM-GUM

**Forrester** — [Engineering Design via Surrogate Modelling](https://onlinelibrary.wiley.com/doi/book/10.1002/9780470770801). Forrester, Sóbester and Keane. Surrogate-based optimization of expensive engineering designs. ^ref-Forrester

**Deb** — [A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II](https://doi.org/10.1109/4235.996017). Deb, Pratap, Agarwal and Meyarivan. Non-dominated sorting and crowding-based multiobjective search. ^ref-Deb

**Jig-fit** — [JigCAD fit profiles and calibration](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/fit.js). go-go-golems. Fit class computations and calibration implementation. ^ref-Jig-fit

**mantyla-upload** — An Introduction to Solid Modeling (1988). Martti Mäntylä. User-provided book. Read §§3.4–3.5 (regular sets and manifolds), chapter 6 (boundary models), chapters 9–11 (Euler operators and half-edges), chapters 14–16 (splitting, Booleans, undo). New chapters 23–25 and 32 use this source. Printed page numbers and PDF page positions are listed in the source guide. ^ref-mantyla-upload

**deberg-upload** — Computational Geometry: Algorithms and Applications, third edition (2008). Mark de Berg, Otfried Cheong, Marc van Kreveld and Mark Overmars. User-provided book. Read §1.2 (degeneracy/robustness), §§2.1–2.4 (sweep, DCEL and overlay), chapter 3 (polygon triangulation), chapter 6 (point location), chapter 9 (Delaunay). New chapters 26–28 and 32 follow these topics. ^ref-deberg-upload

**hoffmann-upload** — Geometric and Solid Modeling: An Introduction (1989). Christoph M. Hoffmann. User-provided book. Read §§2.2–2.4 (regularized Booleans, B-rep validity), chapters 3–4 (Booleans and arithmetic), chapters 5–6 (curved geometry and intersections). The book’s remarks about the state of research describe its publication era, not 2026. ^ref-hoffmann-upload

**edelsbrunner-upload** — Geometry and Topology for Mesh Generation (2001; supplied paperback printing 2006). Herbert Edelsbrunner. User-provided book. Chapters 1–2 develop planar Delaunay/refinement; chapter 3 develops simplicial complexes, manifolds and Euler characteristic; chapters 4–6 cover simplification and tetrahedral meshing. The signed-chain and homology calculations in chapter 25 are an explicitly labeled supplementary bridge. ^ref-edelsbrunner-upload

**research-upload** — Mathematics and textbooks for CAD kernels, B-rep, and computational geometry. User-provided research note. Supplied 2 November 2026. Motivates the five mathematical areas and four implementation projects. Books mentioned but not supplied are identified as further reading, not as inspected full texts. ^ref-research-upload

**lapack-lls** — [LAPACK Users’ Guide: linear least squares problems](https://www.netlib.org/lapack/lug/node27.html). LAPACK authors. Primary documentation distinguishing full-rank QR/LQ, complete orthogonal factorization and minimum-norm SVD drivers. Supplement to chapter 31. ^ref-lapack-lls

**lapack-orthogonal** — [LAPACK Users’ Guide: orthogonal factorizations](https://www.netlib.org/lapack/lug/node39.html). LAPACK authors. Primary documentation for norm preservation by orthogonal transformations and their use in stable least-squares methods. ^ref-lapack-orthogonal

**shewchuk-short** — [Robust Adaptive Floating-Point Geometric Predicates](https://people.eecs.berkeley.edu/~jrs/papers/robust-predicates.pdf). Jonathan Richard Shewchuk. Author-hosted paper, opened and inspected. Adaptive exact signs for floating-point inputs; supplement to the uploaded books’ discussion of robust arithmetic. ^ref-shewchuk-short

---

[[Engineering CAD A - Worked Exercise Solutions|← Appendix A. Worked exercise solutions]] · [[Course - Engineering CAD from First Principles|Contents]]
