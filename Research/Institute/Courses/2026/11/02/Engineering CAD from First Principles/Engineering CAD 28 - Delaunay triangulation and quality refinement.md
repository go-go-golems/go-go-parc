---
title: "Engineering CAD from First Principles — Chapter 28. Delaunay triangulation and quality refinement"
aliases:
  - "Chapter 28. Delaunay triangulation and quality refinement"
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

# Chapter 28. Delaunay triangulation and quality refinement

[[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction|← Chapter 27. Plane sweep, DCEL overlays and profile extraction]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 29 - Tracing intersections of curved surfaces|Chapter 29. Tracing intersections of curved surfaces →]]

Mathematics in this chapter: [[Mathematics - Computational Geometry|Computational Geometry]] (see [[Mathematics]]).

A triangulation answers how to divide a region into triangles. A quality mesh must additionally respect boundaries, avoid unsuitable element shapes, and place enough vertices to resolve small features. Delaunay triangulation is an important part of that process, but it is not the whole process. This chapter derives the empty-circle test, traces an edge flip, and then adds constraints and refinement.

**Source basis.** de Berg et al. chapter 9 develops planar Delaunay triangulation and randomized construction. Edelsbrunner chapters 1–2 develop the empty-circle characterization, edge flipping, constrained triangulations, refinement, and local feature size. We preserve the assumptions of the supplied refinement analysis rather than extending its guarantees to arbitrary inputs. [[Engineering CAD B - Source Library#^ref-deberg-upload|de Berg]] · [[Engineering CAD B - Source Library#^ref-edelsbrunner-upload|Edelsbrunner]].

## 28.1 What must a triangulation cover?

For a finite point set in the plane, a triangulation partitions its convex hull into triangles whose vertices are the input points, with compatible intersections. For a polygonal region, the required domain is different: triangles must stay inside the region and respect any holes and constrained segments.

A simple polygon with $n$ boundary vertices has $n-2$ triangles in a triangulation with no additional vertices. For a connected polygonal region with $h$ holes, $n$ total boundary vertices, and no additional vertices, the count becomes $n+2h-2$. These formulas assume nondegenerate conforming triangulations and suitable simple boundaries. Adding Steiner vertices changes the count.

A triangulation can be correct yet have long, thin triangles. Their small angles can amplify error in some interpolation and numerical-analysis tasks. Quality requirements should be chosen for the downstream computation, not inferred from a pleasing wireframe.

## 28.2 Derive the empty-circle criterion

For sites $p_i$, a Voronoi region consists of points at least as close to $p_i$ as to every other site. Adjacent Voronoi regions define a Delaunay edge between their sites. Where three regions meet, their sites lie on an empty circle centered at the Voronoi vertex.

In general position, a triangle is Delaunay exactly when its circumcircle contains no other input point in its interior. If four sites are cocircular, the circle criterion allows more than one diagonal. The degeneracy is mathematical; exact arithmetic does not remove the ambiguity.

The **power** of a point $x$ relative to a circle with center $o$ and radius $R$ is

$$
\pi(x)=\|x-o\|^2-R^2.
$$

Power is negative inside, zero on, and positive outside. It has squared-length units. It is not the Euclidean signed distance to the circle.

## 28.3 Lift the circle test into one higher dimension

Map each planar point $(x,y)$ to $(x,y,x^2+y^2)$ on a paraboloid. The circle equation

$$
(x-o_x)^2+(y-o_y)^2=R^2
$$

rearranges to

$$
x^2+y^2=2o_xx+2o_yy+(R^2-o_x^2-o_y^2).
$$

The right-hand side is a plane height. A point lies inside the circle exactly when its lifted point lies below that plane. The circle predicate is therefore an orientation-like determinant in lifted space.

With $a,b,c$ counterclockwise, the convention

$$
\operatorname{incircle}(a,b,c,d)=
\det\begin{bmatrix}
a_x&a_y&a_x^2+a_y^2&1\\
b_x&b_y&b_x^2+b_y^2&1\\
c_x&c_y&c_x^2+c_y^2&1\\
d_x&d_y&d_x^2+d_y^2&1
\end{bmatrix}
$$

is positive when $d$ is inside. Reversing the orientation of $a,b,c$ reverses that sign. Edelsbrunner's §1.4 puts the column of ones first, giving the opposite determinant sign: moving it from last to first is three column swaps. This is a notation difference, not a disagreement about the geometry. Write the convention into tests.

## 28.4 Work through a diagonal flip

Take a convex quadrilateral

$$
A=(0,0),\quad B=(4,0),\quad C=(4,3),\quad D=(0,h),\qquad h>0.
$$

The circumcircle of $ABC$ has center $(2,1.5)$ and radius $2.5$. The power of $D$ is

$$
\pi(D)=4+(h-1.5)^2-6.25=h(h-3).
$$

For $0<h<3$, $D$ lies inside this circle, so diagonal $AC$ is not locally Delaunay. Flip it to $BD$. At $h=3$, all four points lie on the rectangle's circumcircle and either diagonal is Delaunay. For $h>3$, $AC$ passes this local test.

At $h=1$, the minimum angle using $AC$ is about $10.305^\circ$, whereas the minimum using $BD$ is about $14.036^\circ$. The flip improves the worst angle but does not produce equilateral triangles: the point positions still constrain what is possible.

> **Try it.** Use [the Delaunay-flip lab](lab:sketch?id=delaunay). Set height 1, force each diagonal, and compare the minimum angles. Move height to 3 and observe the cocircular tie. Switch to automatic choice to see the diagonal change as the power changes sign.

%%FIG:28%%

Edelsbrunner proves that, in the planar setting, repeated locally Delaunay flips lead to a Delaunay triangulation and that a Delaunay triangulation maximizes the minimum angle among triangulations of the same point set. This is not a statement that every angle is maximized, nor a guarantee about arbitrary three-dimensional tetrahedral shapes.

## 28.5 Boundaries constrain which flips are allowed

A **constrained triangulation** must include prescribed input segments as edges. They may form an outer boundary, holes, or interior interfaces. An unconstrained Delaunay triangulation of the vertices can cross those segments and is therefore not a valid replacement.

A constrained Delaunay condition modifies the empty-circle test using visibility: a point hidden behind a constraint does not invalidate a triangle in the same way as a visible point. Constrained edges are never flipped merely to improve a circle test. Edelsbrunner §2.1 develops this definition and its local characterization.

Do not confuse constrained and conforming Delaunay meshes. A constrained triangulation permits a protected edge that is not an ordinary Delaunay edge. A conforming construction may add vertices along the protected segment until the required boundary is covered by ordinary Delaunay edges. Both preserve the boundary geometry, but their combinatorial objects and guarantees differ.

## 28.6 Refinement introduces new vertices

Let $R$ be a triangle's circumradius and $\ell_{\min}$ its shortest edge. By the sine rule, the smallest angle $\alpha$ satisfies

$$
\frac{R}{\ell_{\min}}=\frac1{2\sin\alpha}.
$$

Thus bounding this ratio controls the smallest angle in two dimensions. A common refinement idea inserts a circumcenter of a bad triangle, then updates the Delaunay triangulation. But a proposed point can **encroach** on a protected segment: it lies inside that segment's diametral disk. In that case, split the protected segment before inserting the proposed circumcenter.

For segment endpoints $A,B$, a point $q$ lies inside the open diametral disk exactly when

$$
(q-A)\cdot(q-B)<0.
$$

This follows by writing $m=(A+B)/2$ and expanding the dot product as $\|q-m\|^2-\|A-B\|^2/4$.

For $A=(0,0)$, $B=(4,0)$, $C=(1,1)$, the circumcenter is $O=(2,-1)$. The encroachment value is $(2,-1)\cdot(-2,-1)=-3$. Therefore a bad-triangle refinement request cannot simply insert $O$ while preserving the protected segment $AB$; the segment must be handled first.

> **Try it.** Open [the constrained-refinement decision lab](lab:sketch?id=refinement). At the default triangle, inspect the circumcenter and the diametral disk. Increase the height of $C$ and compare when the proposed point encroaches. The requested angle is an input to this local decision, not a claim that the complete mesh can attain it.

The lab protects only $AB$ and executes one decision. A complete algorithm needs queues for all encroached segments and bad triangles, geometric domain tests, and an update procedure preserving the triangulation.

## 28.7 Why refinement termination requires proof

Adding points does not automatically terminate. A new point can create a new bad triangle or encroach on another segment. Edelsbrunner's analysis controls insertion distances using **local feature size**: roughly, the distance scale at which two nonincident input features become simultaneously relevant.

The supplied analysis in §2.3 uses a target angle strictly below

$$
\arcsin\!\left(\frac1{2\sqrt2}\right)\approx20.7048^\circ,
$$

and the preceding presentation assumes no sharp input angles below $\pi/2$. These are hypotheses of that particular analysis. They are not practical universal limits on all meshing software, and they do not prove that a slider set to $30^\circ$ will terminate for arbitrary geometry.

The proof strategy is instructive: show a lower bound on the separation of newly inserted vertices relative to local feature size, then use a packing argument in a bounded domain. This connects a combinatorial loop to a geometric size bound. When input features are arbitrarily close, a small local feature size correctly demands more samples rather than being dismissed as a numerical nuisance.

## 28.8 Exercises and checkpoint

> **Exercise 28.A.** Derive the power expression $h(h-3)$ and determine the permitted diagonals for $h=1,3,4$. Explain the change in answer under the alternative determinant column convention.

> **Exercise 28.B.** Use the sine rule to show that $R/\ell_{\min}\le1$ implies a smallest angle of at least $30^\circ$. Why does this fact alone not prove that a refinement algorithm terminates?

> **Exercise 28.C.** Implement edge flips on a convex quadrilateral with an exact integer incircle oracle. Add cocircular ties and a protected diagonal. Your function should distinguish `Legal`, `Illegal`, `Tie`, and `Protected` rather than encoding all four as a boolean.

The checkpoint is a triangulation inspector that validates boundary preservation, orientation, and local circle conditions separately from its quality measurements.

> **Careful.** The local refinement lab does not implement a complete algorithm or establish termination at every requested angle.

## Toward a reusable API

```text
incircle(a, b, c, d) -> certified sign
edge_legality(edge, constraints) -> Legal | Illegal | Tie | Protected
flip(edge) -> edit with precondition checks
quality(triangle) -> angles, circumradius, shortest edge, area
refinement_candidate(triangle) -> point
encroached_segments(point, boundary) -> protected segments
```

## Key points

Point-set triangulation and domain meshing have different contracts. Empty circumcircles characterize planar Delaunay triangles under the appropriate degeneracy convention. The determinant sign depends on orientation and column order. Constrained edges alter which flips and visibility tests are legal. Refinement must protect boundaries before improving triangle shapes. Termination and size bounds depend on geometric hypotheses, not on a favorable example.

## Further reading

[[Engineering CAD B - Source Library#^ref-edelsbrunner-upload|Edelsbrunner, chapter 1, printed pp. 1–25]], derives Voronoi duality, flips, lifted predicates, and perturbation. Read chapter 2, printed pp. 26–43, for constrained triangulations, encroachment, and the feature-size analysis; the angle bound is on printed p. 37, PDF p. 50. [[Engineering CAD B - Source Library#^ref-deberg-upload|de Berg et al., chapter 9, printed pp. 191–218]], supplies a complementary algorithmic treatment and randomized construction. Return to [[Engineering CAD 30 - Tetrahedral quality and topology-safe simplification|chapter 30]] before transferring two-dimensional quality intuition to tetrahedra.

---

[[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction|← Chapter 27. Plane sweep, DCEL overlays and profile extraction]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 29 - Tracing intersections of curved surfaces|Chapter 29. Tracing intersections of curved surfaces →]]
