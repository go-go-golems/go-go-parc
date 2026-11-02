---
title: "Engineering CAD from First Principles — Chapter 17. Verification, differential tests and fuzzing"
aliases:
  - "Chapter 17. Verification, differential tests and fuzzing"
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

# Chapter 17. Verification, differential tests and fuzzing

[[Engineering CAD 16 - Rust, WebAssembly and resource ownership|← Chapter 16. Rust, WebAssembly and resource ownership]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 18 - Surface continuity and advanced modeling|Chapter 18. Surface continuity and advanced modeling →]]

A successful unit test establishes that one observed execution met one expected condition. Trustworthy CAD needs much more: it must survive parameter changes, scale changes, degenerate geometry, export/import cycles and long operation histories. This chapter develops property-based tests and independently checkable invariants so that a system can detect wrong geometry before a user manufactures it.

## 17.1 An oracle should not share the bug

If a geometry routine computes volume and its test repeats the same algorithm to compute expected volume, a shared mistake may pass. An **independent oracle** is derived differently: a closed-form mathematical formula, a second implementation, a topological invariant, a known-good reference CAD kernel, or a physical constraint such as nonnegative material volume.

For a cylindrical hole of radius $r$ through a plate of thickness $h$, the removed volume is $\pi r^2h$ when the hole is strictly inside and fully contained. That is an independent oracle. An STL mesh volume integration provides another check, subject to tessellation error. Comparing both is stronger than either alone.

## 17.2 Property-based and metamorphic testing

A property-based test generates many inputs and checks a general invariant. For CAD, useful *metamorphic relations* include translation invariance, rotation invariance, scale covariance, Boolean inclusion–exclusion, and stable behavior under a small parameter perturbation that does not cross a topology event.

If $T$ is a rigid transform, then $V(TS)=V(S)$ and $A(TS)=A(S)$. For a uniform scale $s>0$, volume scales as $s^3$ and area as $s^2$. These exact relations are inexpensive independent tests for a huge family of shapes.


%%FIG:17%%

**Try it.** [The metamorphic-testing bench](lab:sketch?id=metamorphic) changes a solid's scale and displays the predicted volume and area transformations. It also illustrates why a false absolute tolerance can hide defects for tiny shapes and overreact for large shapes.

## 17.3 Shrinking failing cases

Random testing is much more useful when a failure can be reduced to a small reproduction. A 70-feature model that crashes during one fillet is hard to understand. A reduced model with two boxes and one failing blend is an actionable regression test.

A CAD-specific shrinker can remove features, delete unrelated sketch entities, simplify curves, reduce coordinate magnitudes, replace general surfaces with planes/cylinders where possible, and shorten the parameter history. Every reduction must preserve the failing property. A generic array shrinker alone is not enough because many geometry inputs require closure and valid incidence.

Jig's law-testing utilities currently have documented limits, including incomplete law selection and no general shrinking. Improving the test framework would be a high-leverage investment because it helps every subsystem.

## 17.4 Differential testing of solvers

Implement the same constraint system in two independent solvers, or compare Jig against SolveSpace on a shared subset of supported primitives. Generate sketches with known solutions by constructing geometry first and deriving constraint target values. Perturb the starting guesses and measure:

$$
\max_i\frac{|F_i(x)|}{\tau_i},\quad\text{correct DOF},\quad\text{branch},\quad\text{runtime},\quad\text{classification}.
$$

The maximum normalized constraint violation is useful because a small Euclidean residual norm can hide one unacceptable individual constraint. Check that perturbing the initial guess does not convert a feasible problem into a false inconsistency report without warning.

Jig already has a Rust-versus-JavaScript parity suite. That is valuable for detecting porting errors, but shared residual definitions mean both backends can agree on the same incorrectly formulated constraint. Cross-library and mathematical oracles remain necessary.

## 17.5 Differential testing of geometry

Compare a Jig-generated B-rep to a reference implementation such as direct native OpenCascade or another established CAD frontend. Check volume, area, connected components, genus (when valid), and distances between corresponding surfaces. Include model edits, not just fresh builds.

A particularly strong suite would include **contact stratification**: for a critical parameter value $p_0$ (e.g. a hole just tangent to a boundary), test $p_0-\varepsilon$, $p_0$, and $p_0+\varepsilon$ over decreasing values of $\varepsilon$. This reveals whether the implementation handles the topology event coherently.

## 17.6 The full correctness ladder

A reliable CI pipeline can be organized into increasing-cost layers:

```text
L0  unit tests: arithmetic, predicates, parsers, basic topology
L1  analytic geometry: closed-form area/volume and simple constraints
L2  metamorphic/property tests: random transforms and parameters
L3  differential cross-kernel tests and export/import round trips
L4  adversarial degeneracies: tangency, overlap, slivers, singularity
L5  realistic assemblies and long parametric edit histories
L6  stress: memory, timeouts, browser worker and WASM lifecycle
```

The expensive layers can run nightly; the lightweight layers should run on every commit. Keep random seeds, all input models, exact binary versions and the minimized failure reproductions so a regression is repeatable.

## 17.7 What passing CI means for Jig today

The GitHub repository already contains JavaScript core and engine tests, UI tests, agent evaluation tests, Rust unit tests, and a Rust/JS parity suite. The inspected main CI workflow builds the web app and runs the JavaScript suite, Go tests, and an embedded-binary smoke test. It does not explicitly invoke the standalone Rust parity script or `cargo test` as named separate CI steps.

A green CI result is meaningful evidence that the exercised scenarios pass. It is **not** evidence that arbitrary Boolean combinations, highly coupled sketches, STEP imports or closed-loop assemblies have been validated. Coverage claims should always identify the actual tested domain.

> **Exercise.** Design a property-based generator for a rectangular plate with $n$ strictly contained, nonoverlapping circular holes. State the constraints on generated input, the exact volume oracle, and how to shrink a failing case without accidentally moving a hole outside the plate.

> **Careful.** A test that checks only the absence of exceptions may certify a model that returns a successful but incorrect solid. Check physical and mathematical invariants after every operation.

### Deeper study: use the new labs as independent counterexample generators

The expanded chapters add exact and analytic oracle families: a determinant equal to −1, a sphere–plane intersection, a near-singular two-equation system, a tetrahedral sliver, and a pinched surface vertex. Each isolates a distinct failure mode. [[Engineering CAD 32 - A source-guided implementation course|Chapter 32]] organizes them into acceptance tests for four implementations. They are educational tests of those small algorithms, not a measured reliability score for JigCAD or OpenCascade.

## Toward a reusable API

```text
TestCase { seed, model, parameterHistory, expectedProperties }
Oracle { analytic | referenceKernel | metamorphic | structural }
Failure { minimalRepro, observed, expected, environment, trace }
PropertyGenerator { generate, validatePreconditions, shrink }
```

## Key points

Independent oracles reduce correlated failures. Property tests explore input families; metamorphic tests compare related executions when exact outputs are unknown. Shrinking makes complex geometric failures actionable. Differential testing should cover solver classifications and geometry, not only numeric outputs. A CI pass is meaningful only within its actual test coverage.

## Further reading

- [Shewchuk's robust predicate paper](https://people.eecs.berkeley.edu/~jrs/papers/robustr.pdf) is an example of proving numeric predicate correctness and validating implementations.
- [CGAL arrangements](https://doc.cgal.org/latest/Arrangement_on_surface_2/index.html) provides a reference system for difficult planar cases.
- [JigCAD parity suite](https://github.com/go-go-golems/jig/blob/main/import/jigcad/test/rs/parity.mjs) shows existing numerical differential tests.
- [JigCAD CI configuration](https://github.com/go-go-golems/jig/blob/main/.github/workflows/push.yml) is the source for observed automated coverage.
- [JigCAD issue register](https://github.com/go-go-golems/jig/blob/main/import/jigcad/BOOK-ISSUES.md) contains ready-made failure corpus seeds.

---

[[Engineering CAD 16 - Rust, WebAssembly and resource ownership|← Chapter 16. Rust, WebAssembly and resource ownership]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 18 - Surface continuity and advanced modeling|Chapter 18. Surface continuity and advanced modeling →]]
