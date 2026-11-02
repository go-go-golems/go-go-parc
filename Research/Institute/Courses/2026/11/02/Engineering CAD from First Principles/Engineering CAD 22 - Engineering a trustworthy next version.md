---
title: "Engineering CAD from First Principles — Chapter 22. Engineering a trustworthy next version"
aliases:
  - "Chapter 22. Engineering a trustworthy next version"
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

# Chapter 22. Engineering a trustworthy next version

[[Engineering CAD 21 - Design-space search and robust optimization|← Chapter 21. Design-space search and robust optimization]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 23 - Solids as regular sets and representation contracts|Chapter 23. Solids as regular sets and representation contracts →]]

The preceding chapters supply a criterion for deciding which work matters: a feature is useful only if its inputs, mathematical meaning, numerical result and exported geometry remain consistent. This final chapter turns the mathematics into a staged development program and a capstone exercise: repair a planar profile pipeline, then validate an entire parametric CAD workflow.

## 22.1 Start with an executable specification

Choose a simple mechanical part with a plate, two holes, one fillet, and a parameter-driven change. Record its intended geometry as equations and invariants before touching implementation code. For a rectangular plate of width $w$, depth $d$ and thickness $h$ with two disjoint fully contained cylindrical holes of radius $r$, the exact volume is

$$
V=h(wd-2\pi r^2).
$$

This formula defines a family, not one screenshot. If an input hole moves near the boundary, document the exact domain on which the formula remains valid and the modeling semantics at tangency.

Define a machine-readable test case containing parameters, constraints, expected volume, expected topology, source face roles and the features that should recompute after each edit. A reference model that can be checked automatically is more useful than a long informal promise of “robustness.”

## 22.2 Milestone A: trustworthy planar profiles

Implement a canonical curve representation, a precise intersection contract, a directed planar arrangement, and profile validation. Support line segments and circular arcs rigorously first; then extend to ellipses and splines with explicit approximation guarantees.

Acceptance criteria should include: no volume increase from a pure subtraction; consistent hole classification across parameter sweeps; rejection or correct handling of exact tangency; closed spline shape matching between sketch and solid; and a minimized reproduction for every new failure. Reuse the samples in Jig's issue register as regression cases.

%%FIG:22%%

## 22.3 Milestone B: trustworthy numerical sketch solving

Preserve Jig's Rust tape and DogLeg/LM structure while improving status semantics and scaling. Add dimension-aware feasibility checks, branch continuation, rank evidence and independent conflict verification. Benchmark against mathematical oracles and SolveSpace on a shared constraint subset.

Acceptance means that the solver never labels a merely nonconverged local search as *proven infeasible*. The numeric residual for every active constraint must be checked individually against a declared tolerance. Feasible and infeasible examples with degenerate starts must produce meaningful reproducible diagnostics.

## 22.4 Milestone C: trust the B-rep operations

Expose richer OpenCascade validation and shape-healing functions. Record operation history, generated face roles, shape-validity reports and tolerance changes. Audit fillets at singular radii and test Boolean tangencies across a range of scales.

A repaired operation should include the amount of geometric change. A recovered model that silently alters an important dimension is not acceptable engineering output even if it becomes topologically valid.

## 22.5 Milestone D: assemblies and interoperability

Build a real rigid-body joint graph and closure solver on $SE(3)$. Test a planar four-bar as the simplest closed-loop example, then a spatial mechanism. Add STEP import with a typed imported-body representation. Use XDE when the desired exchange workflow requires part names, assemblies or other product metadata.

For round-trip validation, compare geometry and product structure separately: importing a STEP file cannot reconstruct Jig's original feature script unless that history was deliberately serialized elsewhere.

## 22.6 Milestone E: production hardening

Make native Rust unit tests and Rust/JS parity checks explicit in CI. Add fuzzers, property tests, shrinking and nightly degeneracy sweeps. Profile WASM load time, retained memory after repeated compiles, and worst-case latency. Separate the pure numerical Rust crate from ABI and browser policy code.

Document what has **not** been tested. A bounded “supported geometry domain” is more trustworthy than claiming arbitrary industrial CAD robustness without evidence.

## 22.7 Capstone: design a geometry regression laboratory

Build one test runner with a small data model:

```text
case: tangent-hole
shape: square(width=20, height=20) - circle(radius=4, center=(c,0))
parameterSweep: c = [5.9, 5.999999, 6, 6.000001, 6.1]
checks:
  - classify contact regime before B-rep creation
  - subtraction cannot increase total volume
  - no malformed profile is silently accepted
  - any accepted solid passes independent validity checks
  - export and reimport preserve geometry within tolerances
  - diagnostics identify the responsible sketch entities
```

First implement the independent geometric classification. Next run the existing Jig implementation against it. Record the first stage at which the model changes meaning. Then modify the profile builder or reject unsupported contact semantics. After fixing it, add the case to the continuous regression suite and a randomized neighborhood around the critical parameter.

The same experiment generalizes to closed-spline interpolation mismatch, invalid shell thickness, fillet tangency, unstable face naming and closed-loop assemblies. Each deserves a reproduction with **input, mathematical expectation, current behavior, and measurable acceptance criteria**.

## 22.8 Recommended implementation order

Do not start by replacing OpenCascade or adding exotic new primitives. Repair correctness at the boundaries first. Then improve solver status and numerical reliability. Next extend OCCT validation and import, build real assembly closure, and invest in performance only after benchmarks show where time is spent.

The most ambitious long-term possibility is a general-purpose programmable CAD environment with transparent compilation traces, verified geometry contracts and reusable Rust numerical algorithms. Its differentiator would be *trustworthy inspectability*, not a longer menu of shapes.

> **Exercise.** Turn the capstone specification into a suite with one analytic oracle, one topological oracle, one metamorphic relation, and one cross-kernel differential check. What evidence would convince you that a false volume increase was fixed rather than merely suppressed by a warning?

> **Careful.** A project's issue register and source files describe a state at a particular commit. Re-run the failure corpus against the exact revision before treating an old defect as current.

### Deeper study: a source-guided route beyond the survey

Parts VI–VIII deepen the foundations behind this roadmap. [[Engineering CAD 32 - A source-guided implementation course|Chapter 32]] offers four bounded projects with input contracts, mathematical oracles, adversarial examples and acceptance criteria. Start with the component whose failure you want to understand, not with every feature of a full CAD application. The supplied textbooks provide distinct theoretical perspectives; their historical statements are not evidence of the current quality of any kernel.

## Toward a reusable API

```text
GeometryContract { preconditions, postconditions, tolerances }
ReproCase { model, parameterSweep, oracle, expectedClassification }
ValidatedResult<T> { value, evidence, provenance, diagnostics }
ReleaseGate { correctnessSuite, performanceTargets, supportedDomain }
```

## Key points

Engineering priorities should follow the earliest representation boundary where meaning is lost. A canonical curve and robust profile layer are high-leverage improvements. The Rust solver should retain its strong numerical foundation while reporting failure more honestly. OpenCascade integration needs richer validation and import, not immediate replacement. A reproducible regression laboratory is the central tool for making these changes safe.

## Further reading

- [JigCAD issue register](https://github.com/go-go-golems/jig/blob/main/import/jigcad/BOOK-ISSUES.md) defines the initial regression seeds.
- [JigCAD API status](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/KERNEL-API.md) describes what is already implemented and what is still missing.
- [OpenCascade Boolean guide](https://www.occt3d.com/dev/doc/overview/html/specification__boolean_operations.html) covers the mature engine underneath JigCAD.
- [SolveSpace constraints tutorial](https://solvespace.com/constraints.pl) is a useful competing source of user-facing solver behavior.

---

[[Engineering CAD 21 - Design-space search and robust optimization|← Chapter 21. Design-space search and robust optimization]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 23 - Solids as regular sets and representation contracts|Chapter 23. Solids as regular sets and representation contracts →]]
