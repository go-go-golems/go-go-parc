---
title: "Engineering CAD from First Principles — Chapter 30. Tetrahedral quality and topology-safe simplification"
aliases:
  - "Chapter 30. Tetrahedral quality and topology-safe simplification"
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

# Chapter 30. Tetrahedral quality and topology-safe simplification

[[Engineering CAD 29 - Tracing intersections of curved surfaces|← Chapter 29. Tracing intersections of curved surfaces]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 31 - The linear algebra underneath a geometric solver|Chapter 31. The linear algebra underneath a geometric solver →]]

Mathematics in this chapter: [[Mathematics - Combinatorial and Algebraic Topology|Combinatorial and Algebraic Topology]], [[Mathematics - Computational Geometry|Computational Geometry]] (see [[Mathematics]]).

A tetrahedron can have reasonable edge lengths and circumradius while its volume approaches zero. A surface can be simplified by a short edge collapse that changes its topology. These examples show why mesh quality and mesh validity need several independent tests. This chapter constructs a sliver explicitly and derives the link condition used to decide whether a surface edge contraction preserves topology.

**Source basis.** Edelsbrunner chapter 6 develops tetrahedral shape, radius–edge ratio, refinement, and sliver exudation. Chapter 4 develops surface simplification and topology-preserving contractions. The parameterized sliver, numerical measurements, and simplified geometry guards below are original worked examples. The book's theorem assumptions are stated where relevant. [[Engineering CAD B - Source Library#^ref-edelsbrunner-upload|Edelsbrunner]].

## 30.1 A tetrahedral mesh has several obligations

A tetrahedron with vertices $a,b,c,d$ has signed volume

$$
V_s=\frac16\det[b-a\;c-a\;d-a].
$$

The magnitude is its volume; the sign depends on orientation. Zero means the four points are coplanar or otherwise affinely dependent. A tetrahedral mesh additionally requires compatible simplex intersections, coverage of the intended domain, and preservation of constrained boundary features.

A mesh can satisfy these topological and domain requirements yet be poor for a numerical method. Quality criteria include aspect ratios, dihedral angles, interpolation conditioning, element size, and size variation. No single number certifies all of them. Surface approximation error is another independent property: an excellent mesh of the wrong boundary is still the wrong model.

In a CAD workflow, distinguish a visualization mesh from an analysis mesh. The first may prioritize visual error and rendering cost. The second must meet the numerical method's geometry, boundary, and element-quality requirements. Refining a rendering mesh until it looks smooth does not establish the latter.

## 30.2 Construct a sliver with four coordinates

Consider

$$
A=(1,0,0),\quad B=(-1,0,0),\quad
C=(0,1,h),\quad D=(0,-1,h),\qquad 0<h\le1.
$$

The four points lie close to one plane when $h$ is small, but no pair is especially close. The edges $AB$ and $CD$ have length $2$; the other four have length $\sqrt{2+h^2}$. Thus the shortest edge is

$$
L=\sqrt{2+h^2}.
$$

By symmetry the circumsphere center is $O=(0,0,h/2)$, and all four squared distances to $O$ equal $1+h^2/4$. Hence

$$
R=\sqrt{1+h^2/4}.
$$

The determinant gives $|V_s|=2h/3$. Therefore

$$
\frac RL=\frac{\sqrt{1+h^2/4}}{\sqrt{2+h^2}}
\longrightarrow\frac1{\sqrt2},\qquad
\frac{V}{L^3}=\frac{2h}{3(2+h^2)^{3/2}}\longrightarrow0.
$$

The radius–edge ratio stays bounded while the normalized volume vanishes. This is the distinguishing behavior of a sliver. At $h=0.1$, $V=0.0666667$ and $R/L\approx0.706227$. At $h=0.001$, $V=0.000666667$ while $R/L$ remains close to $0.707107$.

> **Try it.** Open [the sliver-quality lab](lab:sketch?id=sliver). Decrease the logarithmic height while watching both quality measures. Rotate the projection and vary the vertical exaggeration to see the nearly flat geometry. The displayed metrics always use the unexaggerated coordinates.

%%FIG:30%%

In two dimensions, the radius–shortest-edge ratio controls the minimum triangle angle by the sine rule. The sliver shows exactly why that inference cannot simply be transferred to tetrahedra. Good triangular faces do not imply a well-shaped three-dimensional element.

## 30.3 Delaunay tetrahedrization is not a quality certificate

A Delaunay tetrahedron has an empty circumsphere. Our four-point sliver satisfies that condition vacuously when there are no other points. It can therefore be Delaunay and still be nearly flat. Adding more points, changing weights, or moving points are different strategies for improving the mesh; each must preserve boundary and domain constraints.

Edelsbrunner's sliver-exudation discussion uses weighted Delaunay structures. The particular theorem presented avoids boundary difficulties through a periodic setting and assumes a radius–edge ratio property. The text explicitly notes that four points forming a sliver cannot have the sliver removed solely by a weight assignment while retaining the same four-point tetrahedral coverage. Do not turn the theorem into the unconditional claim “weights remove every sliver in any constrained mesh.”

A practical quality report should list more than a pass flag: signed volumes, a normalized shape measure, minimum and maximum dihedral angles, constraint recovery, and the worst locations. A requested tolerance and an achieved error bound should be separate fields.

## 30.4 Edge contraction changes both combinatorics and coordinates

To simplify a triangular surface, choose an edge $ab$ and replace its endpoints by one vertex $q$. Remove triangles that contain both endpoints, and replace occurrences of either endpoint by $q$ in the other incident triangles. This is an **edge contraction**.

Two decisions are separate. The combinatorial decision asks whether this identification preserves the topological type. The geometric decision asks where $q$ should be placed without creating unacceptable distortion, flipped triangles, or self-intersections. A midpoint is a placement heuristic, not a topology test.

For a triangulated closed two-manifold, Edelsbrunner's Link Condition Lemma states that contraction preserves topological type exactly when

$$
\operatorname{Lk}(a)\cap\operatorname{Lk}(b)=\operatorname{Lk}(ab).
$$

These are complexes, not merely sets of neighboring vertices. The intersection includes any shared link edges and other simplices. For surfaces with boundary, the book modifies the condition using boundary augmentation; for more general complexes it requires further conditions. Use the lemma only within its stated domain.

## 30.5 Why checking common neighbors is too weak

On the boundary of a tetrahedron with vertices $0,1,2,3$, consider contracting edge $01$. The common neighbors are $2$ and $3$, which may look like the expected two opposite vertices. But both vertex links contain edge $23$. Their intersection contains that edge as well as its endpoints.

The link of edge $01$ consists of vertices $2$ and $3$ without edge $23$, because the boundary complex does not contain tetrahedron $0123$. Therefore the full link condition fails. A test comparing only the two common-neighbor IDs would accept an invalid contraction.

On an octahedron boundary, a suitable edge contraction does satisfy the link condition. This gives a positive example that can be tested against the tetrahedron failure.

> **Try it.** Use [the edge-collapse lab](lab:sketch?id=collapse). Compare the octahedron with the tetrahedron. Read the full common link and edge link. For the octahedron, move the proposed collapsed vertex vertically: the topological test stays unchanged while the local geometric guard can reject the placement.

The lab also checks whether surviving face normals become degenerate or turn beyond a right angle relative to their old normals. This is a conservative local guard, not a complete global self-intersection test. It intentionally reports that the latter was not performed.

## 30.6 Geometry guards are independent of the link condition

For triangle $(a,b,c)$, the unnormalized normal is $n=(b-a)\times(c-a)$. After a candidate contraction, compute $n'$. Reject near-zero area under a documented geometric policy. Comparing $n\cdot n'$ can detect a large orientation change, but it is not a complete proof of embedding validity: remote triangles might now intersect even while every local normal remains acceptable.

A robust simplifier must check candidate changes against nearby and potentially overlapping triangles. A spatial hierarchy can reduce the candidate pairs, but bounding boxes only reject distant pairs; they do not decide triangle intersection. Also preserve protected boundaries, sharp features, material interfaces, and any attributes needed downstream.

If geometric error is measured against the original surface, specify the direction of the distance. Bounding each new vertex's distance to the old surface does not bound the entire new triangle, and a one-sided bound does not necessarily bound the reverse deviation. Certified Hausdorff-style bounds require more work than a few samples.

## 30.7 Quadric error proposes a point; it does not validate it

One useful placement objective sums squared distances to nearby face planes. For normalized plane equations $n_i\cdot x+d_i=0$, write the homogeneous point $\widetilde x=(x,y,z,1)^T$ and plane vector $p_i=(n_i,d_i)^T$. Then

$$
E(x)=\sum_i(n_i\cdot x+d_i)^2
=\widetilde x^T\left(\sum_i p_ip_i^T\right)\widetilde x.
$$

The matrix $Q=\sum_i p_ip_i^T$ is the quadric. Combining the quadrics of two vertices gives a compact objective for a collapse candidate. Solving the corresponding three-variable quadratic problem proposes a position. If the system is singular, a flat region may allow many minimizers; use a documented fallback such as an endpoint or midpoint, or a rank-aware constrained solve.

Edelsbrunner §4.1 discusses quadratic error measures before §4.2's topology conditions. That organization is instructive: low error and valid topology are separate requirements. A zero plane-distance error can still collapse a handle or cross another part of the surface.

## 30.8 Exercises and checkpoint

> **Exercise 30.A.** Compute the six edge lengths, circumsphere center, and signed volume of the sliver family. Explain why its quality does not follow from the quality of each triangular face.

> **Exercise 30.B.** List every simplex in $\operatorname{Lk}(0)\cap\operatorname{Lk}(1)$ and $\operatorname{Lk}(01)$ for the tetrahedron boundary. Identify the exact extra simplex that causes failure.

> **Exercise 30.C.** Construct a candidate contraction with small plane-distance error but invalid geometry. Design separate tests for topology, local area, protected features, and remote self-intersection.

The checkpoint is a simplification candidate inspector, not a complete production remesher: it should show the proposed edit, each acceptance criterion, and every criterion not yet implemented.

> **Careful.** The collapse lab has no global triangle-intersection test. Passing its local guards is not a complete embedding certificate.

## Toward a reusable API

```text
cell_quality(tetrahedron) -> volume, normalized_shape, angle_range
mesh_audit(mesh, domain) -> incidence, coverage, constraints, quality
collapse_link_test(surface, edge) -> Pass | Fail + witness
propose_collapse(edge, objective) -> position + objective_value
validate_collapse_geometry(edge, position) -> local + global findings
apply_collapse(candidate) -> transactional edit
```

## Key points

A bounded radius–edge ratio does not exclude tetrahedral slivers. Empty circumspheres do not certify analysis-mesh quality. The edge-contraction link condition is a statement about full complexes under manifold assumptions. Common-neighbor counts can miss an invalid collapse. Geometric placement and self-intersection tests remain necessary after topology passes. An optimization objective proposes a candidate; validation decides whether it is admissible.

## Further reading

[[Engineering CAD B - Source Library#^ref-edelsbrunner-upload|Edelsbrunner, §6.2, printed pp. 117–122]], develops tetrahedral shape and the radius–edge ratio. Read §6.4, printed pp. 127–133, with its periodic-setting assumptions intact. For simplification, §4.1 introduces error measures and §4.2, printed pp. 73–78, gives the link conditions; the closed-manifold lemma is printed p. 74, PDF p. 87. Return to [[Engineering CAD 25 - Simplicial complexes, links and homology|chapter 25]] for the definitions of links and geometric realization.

---

[[Engineering CAD 29 - Tracing intersections of curved surfaces|← Chapter 29. Tracing intersections of curved surfaces]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 31 - The linear algebra underneath a geometric solver|Chapter 31. The linear algebra underneath a geometric solver →]]
