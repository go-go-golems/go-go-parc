---
title: "Engineering CAD from First Principles — Chapter 26. Predicates, constructions and symbolic perturbation"
aliases:
  - "Chapter 26. Predicates, constructions and symbolic perturbation"
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

# Chapter 26. Predicates, constructions and symbolic perturbation

[[Engineering CAD 25 - Simplicial complexes, links and homology|← Chapter 25. Simplicial complexes, links and homology]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction|Chapter 27. Plane sweep, DCEL overlays and profile extraction →]]

Mathematics in this chapter: [[Mathematics - Computational Geometry|Computational Geometry]], [[Mathematics - Floating-Point and Exact Arithmetic|Floating-Point and Exact Arithmetic]] (see [[Mathematics]]).

A geometric algorithm frequently makes a discrete decision from a numerical expression. The sign of one determinant can decide which edges meet, which face contains a point, or which diagonal a triangulation retains. This chapter shows an exact integer example where ordinary floating-point evaluation loses that sign, then separates three remedies that are often confused: exact predicates, exact constructions, and symbolic perturbation.

**Source basis.** de Berg et al. §1.2 distinguishes algorithm design, degeneracy handling, and numerical implementation. Hoffmann chapter 4 analyzes the interaction between symbolic structure and arithmetic. Edelsbrunner §1.4 develops Simulation of Simplicity and filtered exact decisions. Shewchuk's primary papers provide the adaptive-precision approach. The integer family and rational-intersection trace below are original examples. [[Engineering CAD B - Source Library#^ref-deberg-upload|de Berg]] · [[Engineering CAD B - Source Library#^ref-hoffmann-upload|Hoffmann]] · [[Engineering CAD B - Source Library#^ref-edelsbrunner-upload|Edelsbrunner]] · [[Engineering CAD B - Source Library#^ref-Shewchuk|Shewchuk]].

## 26.1 A predicate returns a fact, not an approximate coordinate

For planar points $a,b,c$, define the orientation determinant

$$
D(a,b,c)=(b_x-a_x)(c_y-a_y)-(b_y-a_y)(c_x-a_x).
$$

Its sign is positive for a counterclockwise turn, negative for a clockwise turn, and zero for collinearity. Its magnitude is twice the triangle's area. The predicate is the sign; the determinant is the expression used to compute it.

A **construction** returns a new geometric object: the intersection point of two lines, the circumcenter of a triangle, or an offset curve. A construction can be ill-conditioned even when the predicate that determines its existence is exact. Conversely, accurate-looking intersection coordinates do not guarantee that all later classifications are consistent.

The distinction guides an interface. A predicate can return an exact three-way sign. A numerical construction may return coordinates together with an error estimate or certified enclosure. The caller must not pretend these outputs have the same guarantees.

## 26.2 Work through a lost sign

Let $N=2^k$ and take

$$
a=(0,0),\qquad b=(N,N+1),\qquad c=(N+1,N+2).
$$

All these coordinates are exactly representable as binary64 numbers for the exponents used in the lab. The exact determinant is

$$
D=N(N+2)-(N+1)^2
=N^2+2N-(N^2+2N+1)=-1.
$$

At $k=27$, $N=134\,217\,728$. The first product equals $18\,014\,398\,777\,917\,440$ and the second equals $18\,014\,398\,777\,917\,441$. Their exact difference is one. At this magnitude, binary64 spacing is four. The two separately rounded products are equal, so their subtraction evaluates to zero in the straightforward JavaScript expression.

The input rounding error here is zero. The failure comes from arithmetic on the represented inputs. No uncertainty about what points were supplied is needed to produce the wrong collinearity decision.

The perpendicular distance from $c$ to the line through $a,b$ is

$$
\frac{|D|}{\|b-a\|}=\frac1{\sqrt{N^2+(N+1)^2}}.
$$

That distance is tiny, but the topological question still has an exact answer for these coordinates. Whether an application deliberately treats the points as nearly collinear is a separate modeling policy.

> **Try it.** Open [the exact-predicate lab](lab:sketch?id=exactpredicate). Increase the exponent from 24 to 27. Compare the two products and the determinant computed with ordinary numbers against the `BigInt` integer oracle. The geometry does not become exactly collinear when the ordinary result becomes zero.

%%FIG:26%%

The lab uses integers because this makes the reference answer easy to inspect. `BigInt` is not a drop-in exact implementation for arbitrary real-valued curves, transcendental functions, or already rounded surface intersections.

## 26.3 Why a fixed epsilon cannot repair the predicate

Under uniform scaling by $s$, orientation scales by $s^2$:

$$
D(sa,sb,sc)=s^2D(a,b,c).
$$

Comparing an orientation determinant against a fixed numerical epsilon therefore changes the decision when the same configuration is expressed in different units. The determinant has area units, not length units. An epsilon intended as “one micrometer” cannot be applied directly to it.

Even a scale-aware tolerance does not automatically produce globally consistent decisions. Hoffmann's point-coincidence example shows that approximate equality is not transitive. de Berg likewise warns that independently thresholding predicates can create impossible combinations of decisions. A tolerance changes the modeled question; an arithmetic error bound estimates uncertainty in computing the original question. Keep those two quantities distinct.

A useful API can expose both an exact sign and a separate geometric near-degeneracy measure. For example, orientation can be negative while perpendicular distance is below a manufacturing tolerance. The first answer controls combinatorial consistency; the second can trigger a warning or an explicit simplification policy.

## 26.4 Filters: pay for precision only when needed

A **floating-point filter** evaluates a fast approximation $\widehat D$ and a proven upper bound $E$ on its absolute evaluation error. If $|\widehat D|>E$, zero cannot lie in the uncertainty interval $[\widehat D-E,\widehat D+E]$, so the sign is certified. Otherwise the algorithm uses a more accurate or exact method.

```text
orientation(a, b, c):
    approximate, error_bound = fast_evaluation_with_proof(a, b, c)
    if approximate > error_bound: return Positive
    if approximate < -error_bound: return Negative
    return exact_orientation_of_represented_inputs(a, b, c)
```

The proof must match the actual instruction sequence, floating-point model, and exceptional-value assumptions. It must account for the coordinate subtractions as well as products and the final subtraction. Overflow, underflow, fused multiply-add, extended precision, and compiler transformations can change those assumptions. Copying a plausible multiple of machine epsilon is not equivalent to implementing a proven filter.

Shewchuk's approach uses expansions of floating-point numbers and error-free transformations to recover increasingly precise information. Easy cases terminate rapidly; nearly degenerate cases require more work. The important guarantee is not “more digits than double” but a correct predicate result under the implementation's stated arithmetic assumptions. The linked reference code and paper should be read together.

For production Rust, choose or audit a predicate implementation against its documented contract and test it under the actual target architecture. A benchmark that measures random well-separated points says little about the difficult cases that trigger exact fallback.

## 26.5 Exact predicates do not make constructions exact

Consider the lines $y=x$ and $y=-2x+1$. Their exact intersection is $(1/3,1/3)$. This point is rational but not exactly representable as a finite binary fraction. Storing an approximate point and later asking an exact orientation predicate about that stored point answers a question about the approximation—not the original exact intersection.

For lines through rational input points, intersections can be represented as rationals. In a homogeneous representation, a point $(x,y)$ is encoded by $(X,Y,W)$ with $x=X/W$, $y=Y/W$. The intersection above can be stored as $(1,1,3)$, avoiding premature division. Equality and incidence can then be tested by cross multiplication, with appropriate exact integer arithmetic and normalization.

This approach has costs. Repeated constructions can grow numerator and denominator sizes. Curved intersections may require algebraic numbers rather than rationals. A rational parameterization may omit exceptional points. There is no single numeric type that makes all geometric modeling operations simple.

The engineering choice is therefore operation-specific: exact construction, certified interval, controlled approximation with provenance, or a symbolic relation that postpones evaluation. Hoffmann's chapter 4 is valuable precisely because it examines how numeric and symbolic decisions interact rather than prescribing “use more precision” as a universal solution.

## 26.6 Symbolic perturbation answers a deliberately changed question

Four cocircular points do not determine a unique Delaunay diagonal. This degeneracy remains even with perfect arithmetic. Exact evaluation returns zero; it does not choose a triangulation.

**Symbolic perturbation** associates a consistent infinitesimal perturbation with the input. Predicates are evaluated as formal expressions in an infinitesimal parameter, and the first nonzero coefficient determines the sign. The coordinates need not actually be moved by a finite floating-point epsilon. Edelsbrunner's Simulation of Simplicity uses a carefully ordered family of infinitesimals tied to point indices.

A consistent scheme preserves nondegenerate decisions and resolves zero cases coherently. It is not the same as independently adding random noise each time a test is called. The point ordering, permutation parity, and tie-breaking semantics become part of the algorithm's reproducibility contract.

For a triangulation, selecting one of several valid diagonals may be appropriate. For two intentionally tangent CAD faces, replacing contact with either overlap or separation may change the design. The algorithm must retain or reconstruct the original degeneracy when the application needs it. Edelsbrunner discusses limitations of perturbation, and de Berg's notes warn that recovering the desired unperturbed result can be nontrivial.

## 26.7 Turn numerical correctness into tests

Test predicates against an independent exact oracle for an input family that the oracle can represent. For integer points, arbitrary-precision integers suffice for orientation. Include large offsets, large products with tiny differences, repeated points, collinear points, input permutations, and exact scalings.

Orientation obeys antisymmetry: swapping two arguments reverses its sign. Cyclically permuting the three arguments preserves it. Translating every point by the same *exactly represented* vector preserves it mathematically; when the translation is rounded, the test must account for the changed represented input. That qualification prevents a misleading test from accusing an exact predicate of failing on data that were already altered.

A differential test should record both the original input values and their binary representations. A decimal string printed with too few digits may not reproduce the failing input. Preserve a seed and minimize failures without accidentally moving them out of the near-degenerate family.

## 26.8 Exercises and checkpoint

> **Exercise 26.A.** Derive $D=-1$ for the integer family and explain why its magnitude is independent of $N$. Find the first exponent at which the straightforward implementation loses the sign on the tested JavaScript runtime.

> **Exercise 26.B.** Represent the intersection of $y=x$ and $y=-2x+1$ in homogeneous rational coordinates. Check both incidences without dividing by three.

> **Exercise 26.C.** Specify whether a cocircular tie in a triangulation and an exact contact in a solid Boolean should use the same perturbation policy. Give a counterexample to a blanket “perturb all zero predicates” rule.

The checkpoint is an orientation API with an exact integer oracle, a degeneracy test corpus, and explicit separation between certified sign and application-level tolerance.

> **Careful.** An exact answer about rounded input is not an exact reconstruction of the unrounded design intent.

## Toward a reusable API

```text
orient2d(a, b, c) -> Negative | Zero | Positive
incircle(a, b, c, d) -> signed result with documented orientation convention
intersect_lines_exact(a, b) -> RationalPoint | Parallel | Coincident
construct_intersection(a, b, policy) -> Exact | Enclosed | Approximate
resolve_degeneracy(event, policy, stable_ids) -> documented combinatorial choice
```

## Key points

Predicates make discrete decisions and constructions create geometric values. Exact input coordinates can still produce an incorrect floating-point determinant. A tolerance is a modeling policy, not an arithmetic proof. Filters certify easy cases and defer difficult ones to exact computation. Exact predicates cannot recover geometry lost by approximate constructions. Symbolic perturbation resolves a selected perturbed problem and must not silently alter intended CAD contacts.

## Further reading

[[Engineering CAD B - Source Library#^ref-hoffmann-upload|Hoffmann, chapter 4, printed pp. 111–153]], treats arithmetic, conditioning, symbolic consistency, and representation. [[Engineering CAD B - Source Library#^ref-deberg-upload|de Berg et al., §1.2, printed pp. 8–10]], separates degeneracies from implementation robustness; the notes on printed p. 14 discuss epsilon inconsistencies. [[Engineering CAD B - Source Library#^ref-edelsbrunner-upload|Edelsbrunner, §1.4, printed pp. 18–23]], develops Simulation of Simplicity and filtering. [[Engineering CAD B - Source Library#^ref-Shewchuk|Shewchuk's long paper and reference implementation]] supply the adaptive arithmetic; the [[Engineering CAD B - Source Library#^ref-shewchuk-short|short primary paper]] is a compact entry point. [[Engineering CAD B - Source Library#^ref-CGAL-arr|CGAL's arrangement manual]] shows how geometry traits and combinatorial structure are separated in a mature library.

---

[[Engineering CAD 25 - Simplicial complexes, links and homology|← Chapter 25. Simplicial complexes, links and homology]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction|Chapter 27. Plane sweep, DCEL overlays and profile extraction →]]
