---
title: "Engineering CAD from First Principles — Chapter 32. A source-guided implementation course"
aliases:
  - "Chapter 32. A source-guided implementation course"
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

# Chapter 32. A source-guided implementation course

[[Engineering CAD 31 - The linear algebra underneath a geometric solver|← Chapter 31. The linear algebra underneath a geometric solver]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD A - Worked Exercise Solutions|Appendix A. Worked exercise solutions →]]

The subjects in this book become easier to retain when each definition is attached to a small implementation and a failure that it prevents. This chapter turns the supplied reading plan into four projects: a planar subdivision engine, a B-rep topology library, a curve evaluator, and a geometric constraint solver. Each project has a restricted contract, an independent test strategy, and a point at which to stop adding features and verify what already exists.

**Source basis.** The four-project sequence comes from the supplied research note. Mäntylä provides a constructive solid-modeling path; de Berg provides discrete algorithms and data structures; Hoffmann supplies robustness and curved-intersection analysis; Edelsbrunner supplies topology and meshing. The milestones, proposed interfaces, and acceptance tests are this guide's engineering synthesis, not prescriptions quoted from those authors. [[Engineering CAD B - Source Library#^ref-research-upload|Research note]].

## 32.1 Choose a route through the book

The original chapters form a survey of a programmable CAD system. The added chapters are deeper studies and need not be read only after completing the survey. The following routes give prerequisites before their uses.

| Route | Read in this guide | Main supplied reading |
|---|---|---|
| Understand geometric representations | 1 → 23 → 3 → 24 → 25 | Mäntylä §§3.3–3.6 and chapters 6, 9–11; Hoffmann §2.4; Edelsbrunner chapter 3 |
| Build reliable planar geometry | 9 → 26 → 10 → 27 → 28 | de Berg chapters 1–3, 6, 9; Edelsbrunner chapters 1–2; Hoffmann chapter 4 |
| Understand and improve a sketch solver | 4 → 5 → 31 → 6 → 7 → 8 | Hoffmann §6.2.4; supplementary LAPACK and optimization references |
| Work on curved solid operations | 2 → 18 → 29 → 11 → 19 | Hoffmann chapters 5–6; Mäntylä chapters 13–15 for the polyhedral foundation |
| Build an application around a kernel | 12 → 13 → 14 → 15 → 16 → 17 | Original source-linked software chapters; supplied books for the underlying geometry |
| Mesh and simplify safely | 25 → 28 → 30 → 14 | Edelsbrunner chapters 2, 4, 5–6 |

No route requires beginning with advanced algebraic topology. Graphs, incidence, and local manifold neighborhoods already explain many practical B-rep failures. Chain complexes add useful global checks once those definitions are secure. The abstract material is connected to executable finite data rather than introduced as a prerequisite barrier.

%%FIG:32%%

## 32.2 Use the four uploaded books for different questions

**Mäntylä asks how to construct a modeler.** Read the regular-set definition, then the boundary data structures, then Euler operators and their implementations. Its Geometric WorkBench is useful because the layers connect: mathematical model, topology edits, geometric algorithms, Booleans, undo, and interface. It is a historical, primarily polyhedral construction, not a ready-made curved industrial kernel.

**de Berg et al. ask how to design and analyze discrete geometric algorithms.** Chapter 2 is particularly valuable because it proceeds from segment intersections to a DCEL and then to map overlay. Read the invariant and complexity argument as carefully as the pseudocode. The authors distinguish algorithm design from robust primitive implementation; do not assume the high-level proof supplies an exact floating-point orientation routine.

**Hoffmann asks where representations, arithmetic, and geometry interact.** Chapter 4 explains why individually plausible decisions can be inconsistent. Chapters 5–6 connect representation choices to curved intersections. Its numerical tracing assumes regularity and an initial point. That limitation belongs in your implementation contract as well as in your reading notes.

**Edelsbrunner asks how geometry and topology support meshing.** Chapters 1–2 give Delaunay and refinement techniques; chapter 3 supplies precise language; chapter 4 uses it for topology-preserving simplification; chapters 5–6 reveal the additional difficulties in three dimensions. Keep theorem hypotheses attached to the result. The planar minimum-angle property is not a tetrahedral sliver guarantee.

These descriptions are grounded in the supplied texts. The dated discussion of then-open questions in Hoffmann and Edelsbrunner should be read as part of their historical presentation, not as an updated research-status survey.

## 32.3 Project A: a planar subdivision engine

**Restricted contract.** Accept finite line segments whose coordinates are integers. Return a planar subdivision with rational intersection coordinates, explicit faces, and point classification. Begin with no overlapping collinear intervals; detect and report them as unsupported rather than silently dropping them. Then extend the contract deliberately.

Start with an exact orientation oracle and a segment-intersection classifier. Represent a rational number as a normalized numerator and positive denominator. Before constructing a rational point, decide whether the segments are disjoint, meet in one point, or overlap. Preserve original segment IDs in every split edge.

A small record vocabulary is enough:

```text
InputSegment { id, endpoint_a, endpoint_b }
Event { exact_point, incident_segment_ids }
AtomicEdge { origin_event, destination_event, source_intervals }
HalfEdge { origin, twin, next, prev, face }
Face { outer_cycle, inner_cycles, input_labels }
```

First use all-pairs intersection. This keeps the correctness problem small and produces a reference against which a later sweep can be compared. Build the DCEL from atomic edges, then implement boundary traversal and face grouping. Add a point-location query only after the incidence structure passes its audits.

**Worked acceptance case.** Use the rectangle pair from chapter 27. With shift two, verify intersection area four, union area seventeen, difference area eight, and symmetric-difference area thirteen. Verify selected face membership at representative interior points. Then vary the shift through exact contact and ensure the result's dimension agrees with the selected regularization policy.

**Adversarial cases.** Test shared endpoints, three segments crossing at one rational point, a vertical segment crossing several others, duplicate segments, a boundary with a hole, disconnected components, and a segment passing through an existing vertex. Check that reordering the input preserves the represented subdivision up to stable relabeling.

**Completion evidence.** Every half-edge invariant passes; every input segment is covered by its atomic pieces; no atomic-edge interior contains an unrepresented crossing; face labels match independent membership tests; the efficient algorithm agrees with the quadratic reference on small exact cases. Only after those conditions hold should you optimize event handling.

Read [[Engineering CAD B - Source Library#^ref-deberg-upload|de Berg chapter 2]], then [[Engineering CAD 26 - Predicates, constructions and symbolic perturbation|chapter 26]] for arithmetic decisions and [[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction|chapter 27]] for the implementation pipeline.

## 32.4 Project B: a small B-rep topology library

**Restricted contract.** Model closed, oriented manifold polyhedral boundaries with planar disk faces. Later add faces with inner loops. Keep coordinate storage separate from incidence. Initially support only a handful of explicit edits, not arbitrary Boolean operations.

Implement stable arena IDs, directed edge uses, loop traversal, and local audits. Add face splitting, edge subdivision, and inverse operations. Give every operation typed preconditions: “same loop,” “distinct adjacent faces,” and “live ID” are more useful than a generic invalid-input error.

Build the cube from chapter 24 and record the counts after every operation. Then build a rectangular through-hole and add ring accounting. The moment rings are introduced, update the Euler audit rather than treating a failed old formula as numerical noise.

**Geometry layer.** Verify that the vertices of every purported planar face satisfy its supporting plane within a declared policy; check that face loops are non-self-intersecting and properly nested; verify consistent shared-edge geometry. The topology library should not claim that a positive Euler result proves these facts.

**Undo trace.** Begin from a validated cube snapshot. Split one face, subdivide one edge, and change a coordinate. Undo in reverse order. Compare record identities, incidences, attributes, and coordinates against the original snapshot. Comparing only $V,E,F$ would miss many incorrect undo implementations.

**Completion evidence.** Edits are transactional; invalid preconditions cause no mutation; local and global audits agree; undo restores the exact model state; intentionally pinched vertex neighborhoods fail the manifold audit; intentionally intersecting coordinates fail the geometric audit while the topological audit remains explainable.

Read [[Engineering CAD B - Source Library#^ref-mantyla-upload|Mäntylä chapters 9–11 and 16]], [[Engineering CAD B - Source Library#^ref-hoffmann-upload|Hoffmann §2.4]], and [[Engineering CAD 24 - Half-edge structures and Euler construction|chapters 24–25]]. The supplied books use different supported boundary domains; choose one explicitly rather than mixing their assumptions.

## 32.5 Project C: a curve and surface evaluator

**Restricted contract.** Evaluate polynomial Bézier curves first, then B-splines, then rational curves and tensor-product surfaces. Do not begin with trimming or surface intersection. Establish evaluation and derivative consistency before introducing topology.

For a Bézier curve, implement de Casteljau evaluation and derivative control points. Check endpoints and affine equivariance: transforming all control points then evaluating should agree with evaluating then applying the affine transform, within the expected arithmetic error.

For B-splines, represent degree, knot vector, and control points. Document the valid parameter domain and the convention at repeated knots and at the final endpoint. Verify partition of unity on the valid domain, nonnegativity of ordinary basis functions, and local support. Test repeated knots explicitly rather than dividing by a zero knot interval.

For a rational curve, evaluate homogeneous control points $(w_ix_i,w_iy_i,w_iz_i,w_i)$ and divide by the final weight only when it is admissible. Positive weights give useful convex-hull behavior; arbitrary signed weights require a different contract and can introduce poles.

**Worked acceptance case.** The quadratic rational curve with control points $(1,0),(1,1),(0,1)$ and weights $(1,1/\sqrt2,1)$ represents a quarter circle. Sample it and verify $x^2+y^2\approx1$. At the middle parameter it gives $(1/\sqrt2,1/\sqrt2)$. Changing the middle weight to one should deliberately break the circle identity while preserving the endpoints.

**Knot insertion.** Add a knot without changing the represented curve. Verify the old and new evaluations and derivatives at sample points away from derivative discontinuities. This is a metamorphic test: the representation changes while the geometry does not. A useful independent comparison is between the original evaluator and the equivalent refined control polygon representation, not two calls through the same cached path.

**Completion evidence.** Endpoints, continuity, basis identities, knot-insertion invariance, and rational-circle tests pass. Tensor-product derivatives agree with independent finite differences on well-scaled smooth test cases. Those finite differences are test instruments, not the production derivative implementation.

The mathematical introduction is [[Engineering CAD 02 - Curves, surfaces and rational geometry|chapter 2]], followed by [[Engineering CAD 18 - Surface continuity and advanced modeling|chapter 18]]. The supplied note recommends Farin before Piegl–Tiller for a sustained CAGD course. Their full texts were not attached; use them as further-reading references rather than pretending the four uploaded books supply a complete NURBS algorithm manual. Hoffmann chapters 5–6 then connect the evaluator to intersection and trimming problems.

## 32.6 Project D: a geometric constraint solver

**Restricted contract.** Begin with two-dimensional points, line segments, and circles; support coincidence, fixed point, distance, horizontal/vertical, parallel/perpendicular, and a carefully specified tangency relation. Give each residual a unit and characteristic scale.

Implement residual evaluation and analytic or automatic derivatives. Compare Jacobian rows with independent finite differences on smooth, nondegenerate, well-scaled samples. Explicitly exclude or separately test nondifferentiable points rather than treating disagreement there as proof that AD is wrong.

Add a trusted least-squares solve before writing a custom factorization. Learn the mathematics from chapter 31, but separate a learning implementation from a production numerical dependency. Then add a nonlinear strategy with accepted/rejected steps and a complete trace of residual, step length, damping or trust radius, and termination reason.

**Worked acceptance case.** Constrain a point to the circle $x^2+y^2=25$ and line $x+y=3$. Substitution gives $2x^2-6x-16=0$, hence

$$
x=\frac{3\pm\sqrt{41}}2,\qquad y=\frac{3\mp\sqrt{41}}2.
$$

There are two valid solutions. Test both branches, not only the one reached from a preferred starting point. Changing the line offset to $c$ gives two intersections for $|c|<5\sqrt2$, one tangent intersection at equality, and none beyond it. This single family tests ordinary convergence, branch choice, singularity, and genuine infeasibility.

**Diagnostics.** Add a duplicate constraint, a conflicting distance, an unconstrained translation, and a singular initial configuration. Require distinct statuses for a small feasible residual, weak numerical rank, exhausted iteration budget, and supported evidence of inconsistency. Do not classify a system as impossible merely because one start failed.

**Completion evidence.** Analytic solutions match; Jacobian checks pass under their assumptions; translation and unit changes are tested with proper input accounting; underconstrained steps follow a documented metric; changing dimensions continuously does not unexpectedly switch branches in regular cases; a failure produces enough data to reproduce it.

Read [[Engineering CAD 04 - Constraints become equations|chapters 4–8]] and [[Engineering CAD 31 - The linear algebra underneath a geometric solver|chapter 31]]. Hoffmann's SVD section is the uploaded book connection; the nonlinear optimization readings are supplementary. The educational browser labs are not benchmarks of JigCAD's actual Rust solver.

## 32.7 Integrate only after the contracts are stable

A useful integration exercise is a parameterized plate with a hole. The constraint solver produces a valid sketch configuration. The subdivision engine identifies the profile. The B-rep layer extrudes it. A derived mesh supports display. A file exporter preserves units and geometry. Each stage should retain a reference to the input entities that produced it.

For a plate $20\times12$ with a strictly internal radius-two through-hole and thickness five, the analytic volume is

$$
V=5(240-4\pi)=1200-20\pi\approx1137.168147.
$$

Check the same dimensions after parameter edits and after an export/import round trip. Move the hole toward the outer boundary to exercise the contact policy. Change only the thickness and verify that unrelated sketch calculations are not invalidated. These tests connect geometry, naming, caching, and interoperability without requiring a large application first.

When targeting WebAssembly, reuse the numerical tests unchanged where possible. Add boundary tests for buffers, handles, memory growth, and repeated allocation/free cycles. Compare native and WASM results under documented tolerances and arithmetic conventions. A successful compilation proves target compatibility, not algorithmic robustness.

## 32.8 Build an evidence ledger

For each feature, maintain a small ledger containing its mathematical contract, input restrictions, source reading, implementation location, independent oracle, known counterexamples, and test status. This is more useful than a checklist saying “Booleans supported.”

```text
Feature: segment intersection
Domain: rational planar segments, including endpoint contacts
Unsupported: collinear overlaps until milestone A3
Oracle: exact all-pairs reference on generated small inputs
Invariants: split coverage, shared event identity, DCEL consistency
Evidence: saved seed + exact input + expected classification
```

For each experimental result, record the commit, platform, compiler options, precision, and input corpus. For each historical theorem, record the assumptions and exact source section. For each current software claim, record whether it came from source inspection, documentation, or an executed test. These evidence types should never be silently exchanged.

## 32.9 Exercises and selected answers

The new chapters include exercises numbered 23.A through 31.C. The [[Engineering CAD A - Worked Exercise Solutions|**Worked solutions** appendix]] provides calculations, counterexamples, and implementation checkpoints. Use it after writing down a prediction and running the associated lab. An answer that matches a diagram but cannot state its assumptions is not yet an implementation contract.

> **Exercise 32.A.** Choose one project and write its first milestone as a complete input/output specification. Include at least one unsupported case, one exact oracle, one invariant, and one adversarial example.

> **Exercise 32.B.** For the integrated plate, explain how equal volume could coexist with an incorrect model. Add an independent semantic test and a membership test that would detect a different class of error.

> **Exercise 32.C.** Select a theorem from one uploaded book. Write its assumptions separately from its conclusion, then change one assumption and construct or search for a counterexample. Do not claim the original theorem applies to the changed problem.

> **Careful.** The supplied books support the mathematics and learning sequence. They do not establish current performance or robustness of JigCAD.

## Toward a reusable API

```text
Case { inputs, units, supported_domain, expected_semantics }
Evidence { source_locator, oracle, invariant_results, counterexample }
Reproduction { version, platform, exact_inputs, random_seed, trace }
Milestone { contract, acceptance_tests, known_limits, next_extension }
```

## Key points

Study a mathematical definition alongside the finite data and tests that make it operational. The four books answer complementary questions rather than forming interchangeable references. Small exact or analytic cases provide strong independent oracles. Expand a supported input domain deliberately, including degeneracies and failure statuses. Integration should preserve provenance and units across subsystem boundaries. Compilation, source inspection, and benchmark execution establish different kinds of evidence.

## Further reading

The [[Engineering CAD B - Source Library#^ref-research-upload|supplied research note]] is the source of the four-project progression. Use [[Engineering CAD B - Source Library#^ref-mantyla-upload|Mäntylä]] for constructive topology and modeler architecture, [[Engineering CAD B - Source Library#^ref-deberg-upload|de Berg et al.]] for discrete algorithms and their analyses, [[Engineering CAD B - Source Library#^ref-hoffmann-upload|Hoffmann]] for robustness and curved representations, and [[Engineering CAD B - Source Library#^ref-edelsbrunner-upload|Edelsbrunner]] for topology and quality meshing. The [[Engineering CAD B - Source Library|source library]] distinguishes these uploaded texts from external primary references and further-study books. The source archive includes the editable teaching implementations, numerical checks, and build scripts, but not the uploaded textbook PDFs.

---

[[Engineering CAD 31 - The linear algebra underneath a geometric solver|← Chapter 31. The linear algebra underneath a geometric solver]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD A - Worked Exercise Solutions|Appendix A. Worked exercise solutions →]]
