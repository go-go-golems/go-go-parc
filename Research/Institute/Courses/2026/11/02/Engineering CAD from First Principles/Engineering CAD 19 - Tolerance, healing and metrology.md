---
title: "Engineering CAD from First Principles — Chapter 19. Tolerance, healing and metrology"
aliases:
  - "Chapter 19. Tolerance, healing and metrology"
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

# Chapter 19. Tolerance, healing and metrology

[[Engineering CAD 18 - Surface continuity and advanced modeling|← Chapter 18. Surface continuity and advanced modeling]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 20 - Manufacturing, drawings and sheet metal|Chapter 20. Manufacturing, drawings and sheet metal →]]

CAD systems operate with several meanings of “precision,” and confusing them produces models that are numerically valid but unsuitable for engineering. Floating-point roundoff, geometric modeling tolerance, dimension tolerance and manufacturing variability are different quantities. This chapter separates them, derives fit limits for a shaft and hole, and specifies what a shape-healing operation must disclose.

## 19.1 Four meanings of error

**Rounding error** is introduced by finite-precision computation. A double-precision number carries roughly 15–16 decimal significant digits, but subtraction of close quantities can lose relative accuracy. This is a property of an algorithm and its representation.

A **modeling tolerance** says when a geometric kernel treats two positions, edges or surfaces as agreeing for a particular operation. It is commonly local to topology, rather than a single universal threshold. A modeling tolerance is not the same as the accuracy of physical fabrication.

A **dimensional tolerance** specifies allowable variation in the manufactured object: for instance, diameter $5.00\pm0.15\,\mathrm{mm}$ describes a permitted interval. **Measurement uncertainty** quantifies uncertainty in an observed measurement and must be reported with its methodology and coverage assumptions. It does not automatically license an out-of-spec part.

If a CAD system conflates these four, it may grow a topological tolerance to complete a Boolean operation and then describe the changed shape as if the designer had accepted that dimensional change.

## 19.2 Work a shaft–hole fit from intervals

Let a hole diameter be $H=5.00\pm0.15\,\mathrm{mm}$ and a shaft diameter $S=4.80\pm0.10\,\mathrm{mm}$. The diametral clearance is $C=H-S$. At nominal size, $C_0=0.20\,\mathrm{mm}$. The strict worst-case limits are

$$
C_{\min}=4.85-4.90=-0.05\,\mathrm{mm},\qquad C_{\max}=5.15-4.70=0.45\,\mathrm{mm}.
$$

Thus the stated manufacturing limits allow a slight **interference fit**, despite a positive nominal clearance. If the design requires at least $0.10\,\mathrm{mm}$ diametral clearance in every compliant part, this tolerance allocation is unacceptable.

Worst-case tolerancing adds absolute bounds. If the deviations are instead random independent zero-mean variables with standard deviations $\sigma_H$ and $\sigma_S$, then

$$
\sigma_C=\sqrt{\sigma_H^2+\sigma_S^2}.
$$

For $\sigma_H=0.15$ and $\sigma_S=0.10$ mm, $\sigma_C\approx0.1803$ mm. This probabilistic calculation is **not** interchangeable with the worst-case interval above: the symbols $\pm0.15$ and $\pm0.10$ must explicitly represent standard deviations for the formula to apply.

**Try it.** In [the fit-tolerance bench](lab:sketch?id=tolerances), adjust hole and shaft tolerance bands. Observe the possible interference region and the effect of changing nominal clearance.

%%FIG:19%%

## 19.3 Modeling tolerance is a topological policy

A B-rep vertex, edge or face may carry a tolerance describing the admitted mismatch between underlying geometric representations. In OpenCascade, shape-analysis tools can inspect tolerances on subshapes, and shape-healing tools may adjust them within configured minimum and maximum values. This is fundamentally different from saying that every coordinate is accurate to the same number of micrometers.

Suppose an imported wire has two endpoints separated by $0.03\,\mathrm{mm}$. A repair tool might connect them by moving one or both endpoints, or by increasing a local tolerance enough that they count as coincident. Either choice may enable a valid face. But if the wire bounds a precision bore with a $0.02\,\mathrm{mm}$ tolerance, the repair may violate the engineering contract. The repair therefore needs a declared modification budget and an auditable record.

The source [OpenCascade Shape Healing guide](https://www.occt3d.com/dev/doc/overview/html/occt_user_guides__shape_healing.html) describes `ShapeFix_Shape`, `ShapeFix_Wire`, `ShapeAnalysis_Wire` and tolerance-analysis functionality. JigCAD's inspected WASM binding does not expose every OCCT analysis or healing class, so simply saying that OpenCascade can repair a wire does not imply that JigCAD can already invoke that repair.

## 19.4 A tolerance budget across the pipeline

A useful contract records separate contributions: sketch-solving error, profile intersection construction error, B-rep edge–surface mismatch, tessellation deviation and eventual machine deviation. Their total should not be collapsed automatically into a single scalar, because some are bounds, some are stochastic, and some are local geometric errors.

For a conservative bound on a computed distance made from successive approximations with certified errors $\varepsilon_1,\dots,\varepsilon_k$, the triangle inequality gives

$$
|d_{\mathrm{reported}}-d_{\mathrm{ideal}}|\le\sum_{i=1}^k\varepsilon_i.
$$

This bound may be pessimistic, but it is explicit. A bound on a mesher's *input deflection setting* is not necessarily a proof of maximum surface distance. Likewise, the typical error of an FDM-printed hole is not a tolerance guarantee for every machine, material and orientation.

## 19.5 Healing must preserve meaning

A robust repair pipeline should first diagnose the defect: disconnected wire, self-intersection, inconsistent orientation, excessive face tolerance, small edges or an open shell. It should then attempt a **typed repair**, measure the geometric change and validate the result independently.

A repair is unacceptable if it silently eliminates a required hole, merges separate parts, shifts a mating datum, or changes a critical dimension beyond budget. Returning a topologically valid shape is necessary but not sufficient.

For each repair, record original and final shape hashes, changed entities, maximum measured displacement, before/after tolerance distributions, feature genealogy consequences, and whether the operation was automatic or approved. These are the data needed for a meaningful “healed” status.

## 19.6 Metrology and dimensioning

Physical verification uses datums, measuring instruments, calibration, sampling strategy and a stated uncertainty model. A CAD fit design may specify a diameter interval, but a coordinate-measuring machine must establish how that diameter is estimated from observed points. Form error, cylindricity, runout and measurement strategy are not reducible to a single bounding-box measurement.

Engineering drawings communicate dimensional requirements and geometric tolerances using a standard system such as ISO GPS or ASME GD&T. A model might be geometrically exact yet lack the annotation and datum structure necessary to manufacture and inspect it consistently.

For a CAD workbench, useful additions include named datum features, toleranced dimensions, measurement reports, gauge geometry, and traceable connections from a dimension annotation to the original parametric feature.

## 19.7 Test shape healing, not only shape validity

Create a wire with one controlled defect at a time: a gap of $0.005$, $0.02$, $0.05$ and $0.2$ mm; a reversed edge; a duplicate short edge; and a slight self-intersection. Run repair policies with several allowed maximum displacements. Record whether repair succeeds, how far geometry moves, and whether the postcondition is satisfied.

Then repeat after translating and scaling the model. A fixed absolute threshold can be appropriate for a physical length scale, but it must be explicitly selected rather than leaked from a numerical derivative tolerance. Preserve the original failing case for regression.

> **Exercise.** Change the hole specification above to $5.10\pm0.05\,\mathrm{mm}$ while keeping the shaft $4.80\pm0.10\,\mathrm{mm}$. Compute nominal, minimum and maximum clearance. Does the new allocation guarantee at least $0.10$ mm clearance?

> **Careful.** A shape-healing algorithm can make a file easier to process by modifying its geometry. “Healing succeeded” must not be presented as “the repaired geometry equals the intended geometry.”

### Deeper study: treat tolerance changes as explicit model edits

The relation “closer than epsilon” is not transitive. [[Engineering CAD 23 - Solids as regular sets and representation contracts|Chapter 23]] works through the three-point counterexample and explains why union-find clustering can merge a group wider than the original pairwise threshold. [[Engineering CAD 26 - Predicates, constructions and symbolic perturbation|Chapter 26]] separates that modeling policy from a floating-point error bound. Shape healing should record displacement and topology changes rather than using a larger tolerance as an unexplained success condition.

## Toward a reusable API

```text
ToleranceBudget { geometric, numerical, tessellation, manufacturing }
ShapeAnalysis { disconnected, selfIntersection, orientation, localTolerance }
HealingPolicy { maxDisplacement, maxToleranceGrowth, preserveDatums }
HealingReport { before, after, edits, maxMeasuredChange, accepted }
FitInterval { minimum, nominal, maximum, uncertaintyModel }
```

## Key points

Rounding, modeling tolerance, design allowance and measurement uncertainty must be separated. Worst-case stack-ups and probabilistic stack-ups answer different questions. CAD topology can have local tolerances. Shape healing must be controlled by an explicit modification budget and verified geometrically after execution. Metrology requires datums and an uncertainty model beyond solid geometry alone.

## Further reading

- [OpenCascade Shape Healing guide](https://www.occt3d.com/dev/doc/overview/html/occt_user_guides__shape_healing.html) documents wire diagnostics and tolerance handling.
- [BIPM/JCGM publications](https://www.bipm.org/en/committees/jc/jcgm/publications) collects the Guide to the Expression of Uncertainty in Measurement.
- [JigCAD fit and kernel API](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/KERNEL-API.md) describes fit profiles, inspection and current limitations.
- [OpenCascade's STEP guide](https://occt3d.com/dev/doc/overview/html/occt_user_guides__step.html) explains representation exchange and related shape processing.

---

[[Engineering CAD 18 - Surface continuity and advanced modeling|← Chapter 18. Surface continuity and advanced modeling]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 20 - Manufacturing, drawings and sheet metal|Chapter 20. Manufacturing, drawings and sheet metal →]]
