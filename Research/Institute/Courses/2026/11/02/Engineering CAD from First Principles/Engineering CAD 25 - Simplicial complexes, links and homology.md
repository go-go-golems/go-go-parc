---
title: "Engineering CAD from First Principles — Chapter 25. Simplicial complexes, links and homology"
aliases:
  - "Chapter 25. Simplicial complexes, links and homology"
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

# Chapter 25. Simplicial complexes, links and homology

[[Engineering CAD 24 - Half-edge structures and Euler construction|← Chapter 24. Half-edge structures and Euler construction]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 26 - Predicates, constructions and symbolic perturbation|Chapter 26. Predicates, constructions and symbolic perturbation →]]

Mathematics in this chapter: [[Mathematics - Combinatorial and Algebraic Topology|Combinatorial and Algebraic Topology]] (see [[Mathematics]]).

A closed mesh can pass an edge-count check and still fail at a vertex. A boundary can have the right Euler characteristic and still intersect itself. To understand these failures, we need three levels of structure: a combinatorial complex, its local neighborhoods, and its geometric realization. This chapter builds those levels and adds a small algebraic calculation that distinguishes a loop from a filled region.

**Source basis.** Edelsbrunner chapter 3 supplies simplices, complexes, stars, links, realizations, manifolds, and Euler characteristic. Hoffmann §2.4 connects topological polyhedra and manifold tests to B-rep validity. The signed boundary matrices and homology computation below are an original supplementary development prompted by the research note; they are not presented as a chapter-by-chapter summary of Edelsbrunner's meshing book. [[Engineering CAD B - Source Library#^ref-edelsbrunner-upload|Edelsbrunner]] · [[Engineering CAD B - Source Library#^ref-hoffmann-upload|Hoffmann]] · [[Engineering CAD B - Source Library#^ref-research-upload|Research note]].

## 25.1 Affine independence before simplices

An affine combination of points $p_0,\ldots,p_k$ has the form $x=\sum_i\lambda_i p_i$ with $\sum_i\lambda_i=1$. It is a convex combination when every $\lambda_i\ge0$. The convex hull is the set of all convex combinations.

The points are **affinely independent** when the vectors $p_1-p_0,\ldots,p_k-p_0$ are linearly independent. Their convex hull is then a $k$-simplex. Two distinct points define a segment; three noncollinear points define a triangle; four noncoplanar points define a tetrahedron. A flattened tetrahedron fails affine independence even if four distinct vertex IDs remain in memory.

Every subset of the vertices determines a face, including the simplex itself and the empty face. A tetrahedron therefore has four vertices, six edges, four triangular faces, and one three-dimensional simplex. Its boundary contains everything except that last simplex.

## 25.2 A mesh is more than a collection of triangles

A geometric **simplicial complex** $K$ satisfies two conditions. First, every face of every simplex in $K$ also belongs to $K$. Second, two simplices intersect only in a common face, possibly the empty face.

A T-junction violates the second condition if the endpoint of one triangle lies in the interior of another triangle's edge without that edge being subdivided. Two crossing triangles also violate it. A complex is a conforming decomposition, not simply a file containing plausible triangles.

An **abstract simplicial complex** retains only vertex sets. If $\{0,1,2\}$ is a triangle, it must also include $\{0,1\}$, $\{0,2\}$, $\{1,2\}$ and their vertices. Coordinates are absent. A geometric realization assigns points to vertices so that these abstract simplices become a geometric complex with the same incidences.

This separates two kinds of mistakes. An abstract incidence structure can be invalid before coordinates are considered. Alternatively, its combinatorics can be valid while the chosen coordinates create intersections or degeneracies. A CAD validator needs to say which layer failed.

## 25.3 Stars and links expose the neighborhood

The **star** of a simplex $\tau$ is the collection of simplices containing it. The closed star adds all their faces. The **link** keeps faces in the closed star that are disjoint from $\tau$:

$$
\operatorname{St}(\tau)=\{\sigma\in K:\tau\subseteq\sigma\},\qquad
\operatorname{Lk}(\tau)=\{\eta\in\overline{\operatorname{St}(\tau)}:\eta\cap\tau=\varnothing\}.
$$

Here the bar means closure under faces, not Euclidean point-set closure. Context matters: the same word “closure” appears in different mathematical structures.

For a vertex in the interior of a triangulated two-manifold, its link is a single cycle. At a boundary vertex it is a single path. Along an interior edge, the link consists of two vertices, one for each incident triangle. These are local combinatorial tests in the two-dimensional simplicial setting.

Take two tetrahedron boundaries and identify exactly one vertex between them. Every edge still has exactly two incident triangles. Yet the link of the shared vertex consists of two disjoint cycles. No disk neighborhood can have that link. An edge-incidence test alone has missed a nonmanifold pinch.

> **Try it.** Open [the vertex-link lab](lab:sketch?id=vertexlink). Compare an interior fan, a boundary fan, three sheets, and the pinched shells. For the pinched shells, notice the combination: every surface edge has two uses, but the shared vertex has a disconnected link.

%%FIG:25%%

For an implementation, construct the vertex's link graph from all incident triangles: triangle $(v,a,b)$ contributes link edge $(a,b)$. Then test connectivity and degrees. A cycle has one connected component and all degrees two. A path has two degree-one vertices and all other degrees two. These tests assume a pure, nondegenerate triangular surface and must be supplemented with duplicate-face and incidence checks.

## 25.4 Orient a simplex and take its boundary

Order a simplex's vertices to choose its orientation. Reversing two vertices changes the orientation sign. Define

$$
\partial[v_0,\ldots,v_k]=\sum_{i=0}^k(-1)^i[v_0,\ldots,\widehat{v_i},\ldots,v_k].
$$

The hat means that vertex is omitted. For a directed edge, $\partial[a,b]=[b]-[a]$. For an oriented triangle,

$$
\partial[a,b,c]=[b,c]-[a,c]+[a,b].
$$

Taking the boundary again cancels every endpoint:

$$
\partial^2[a,b,c]=([c]-[b])-([c]-[a])+([b]-[a])=0.
$$

This is the **boundary-of-a-boundary identity**. It is an exact algebraic invariant, not a numerical tolerance test.

Choose edge basis $([a,b],[a,c],[b,c])$ and vertex basis $([a],[b],[c])$. The matrices for a filled triangle are

$$
B_1=\begin{bmatrix}-1&-1&0\\1&0&-1\\0&1&1\end{bmatrix},\qquad
B_2=\begin{bmatrix}1\\-1\\1\end{bmatrix}.
$$

Multiplication gives $B_1B_2=0$. This provides a small exact test of a boundary-matrix builder. It also explains why consistent orientation makes shared edges cancel in the sum of a closed shell's faces.

## 25.5 Cycles, boundaries, and what homology counts

A **chain** is a linear combination of simplices. Fix coefficients in a field, such as the rational numbers $\mathbb Q$ or the two-element field $\mathbb F_2$. A $k$-cycle is a chain in $\ker B_k$: it has zero boundary. A $k$-boundary is a chain in $\operatorname{im}B_{k+1}$: it bounds a chain one dimension higher. The identity $B_kB_{k+1}=0$ ensures every boundary is a cycle.

Homology records cycles modulo those that are boundaries:

$$
H_k=\ker B_k/\operatorname{im}B_{k+1}.
$$

Its dimension, the **Betti number**, can be computed from matrix ranks:

$$
\beta_k=n_k-\operatorname{rank}B_k-\operatorname{rank}B_{k+1}.
$$

For a triangle boundary, $n_0=3,n_1=3,n_2=0$ and $\operatorname{rank}B_1=2$. Therefore $\beta_0=1$ and $\beta_1=1$: there is one connected component and one independent loop not filled by a face. Add the triangular face. Now $\operatorname{rank}B_2=1$, so $\beta_1=0$. The same loop exists as a cycle, but it is now the boundary of the face and represents zero in homology.

For a tetrahedron boundary the counts are $(n_0,n_1,n_2)=(4,6,4)$, with ranks $3$ and $3$. Hence $(\beta_0,\beta_1,\beta_2)=(1,0,1)$. Filling the tetrahedron adds one 3-simplex whose boundary has rank one, eliminating $\beta_2$.

> **Try it.** Use [the chain-complex lab](lab:sketch?id=homology) to switch among the triangle boundary, filled triangle, tetrahedron boundary, and filled tetrahedron. Read the cell counts and boundary ranks before looking at the Betti numbers. Predict which rank changes when the interior simplex is added.

The lab uses $\mathbb F_2$, so addition is XOR and minus equals plus. This makes the implementation small and avoids numerical rank thresholds. It also discards orientation signs. Do not use an $\mathbb F_2$ calculation as evidence that a surface is orientable. Integer homology can additionally detect torsion; that is outside this lab's scope.

## 25.6 Euler characteristic is an alternating sum

For a finite complex,

$$
\chi(K)=\sum_k(-1)^k n_k=\sum_k(-1)^k\beta_k.
$$

Substitute the rank formula into the right-hand side. Each boundary-matrix rank appears twice with opposite signs, so it cancels. This is a direct algebraic explanation of the equality.

The triangle boundary has $\chi=3-3=0=1-1$. The filled triangle has $\chi=3-3+1=1$. A tetrahedron boundary has $\chi=4-6+4=2$; the filled tetrahedron has $\chi=4-6+4-1=1$. Confusing a solid with its boundary produces different counts even for this simplest three-dimensional example.

For a connected closed orientable surface, $\chi=2-2g$. That statement includes assumptions. A single integer cannot establish those assumptions. More generally, Betti numbers do not determine homeomorphism type, local manifoldness, or whether the coordinates self-intersect. Topological invariants are powerful checks, not a complete validity certificate.

## 25.7 From topology back to kernel engineering

A practical audit can proceed in dependency order. Check record references and face closure first. Then check simplex or cell incidence and orientation. Next inspect vertex links and boundary components. Finally examine geometric embedding, tolerances, and whether the chosen oriented shells bound the desired material.

For curved B-reps, the topology need not arrive as a simplicial complex. Faces may have holes, seams, and singular parameterizations. A validated triangulation can provide a derived complex for some checks, but the relationship between that complex and the original B-rep must itself be controlled. A mesh with the wrong trim boundary is not an independent witness to the B-rep's topology.

This is where abstract mathematics becomes operational. A boundary operator is executable data; $B_1B_2=0$ is a test. A vertex link is a finite graph; connectedness is a test. A realization is geometric data; intersection and incidence checks test its compatibility. None replaces the others.

## 25.8 Exercises and checkpoint

> **Exercise 25.A.** Write $B_1$ and $B_2$ for two triangles forming a square, using consistent orientations. Show that the shared diagonal cancels from the sum of the two face boundaries.

> **Exercise 25.B.** Compute the cell counts and Euler characteristic of two tetrahedron boundaries identified at one vertex. Explain why the edge-incidence test passes and the link test fails.

> **Exercise 25.C.** Implement exact Gaussian elimination over $\mathbb F_2$ for boundary ranks. Test both $B_kB_{k+1}=0$ and the displayed Betti-number formula. Compare a triangulated disk with an annulus.

The checkpoint is a small simplicial-complex inspector with independent abstract-incidence, local-link, and geometric-realization reports. Keep these reports separate in the API.

> **Careful.** The browser homology lab works over the two-element field. It cannot certify orientation and does not test geometric self-intersections.

## Toward a reusable API

```text
closure_under_faces(maximal_simplices) -> AbstractComplex
link(complex, simplex) -> Subcomplex
boundary_matrix(complex, dimension, coefficient_field) -> Matrix
betti_numbers(complex, coefficient_field) -> Vector
check_surface_links(complex) -> ManifoldFindings
check_realization(complex, coordinates) -> GeometryFindings
```

## Key points

A simplex requires affine independence. A geometric complex requires compatible intersections as well as face closure. Links describe local topology and detect failures that edge counts miss. Signed boundaries satisfy the exact identity that a boundary has no boundary. Homology distinguishes cycles from filled boundaries, while Euler characteristic compresses those counts into one number. Neither homology nor Euler characteristic certifies an embedded solid.

## Further reading

[[Engineering CAD B - Source Library#^ref-edelsbrunner-upload|Edelsbrunner, chapter 3, printed pp. 44–67]], is the supplied source for complexes, links, realizations, and Euler characteristic; the star/link definitions are printed p. 46, PDF p. 59. [[Engineering CAD B - Source Library#^ref-hoffmann-upload|Hoffmann, §2.4, printed pp. 46–61]], develops topological validity for B-reps. The [[Engineering CAD B - Source Library#^ref-research-upload|research note's abstract-topology progression]] motivates the supplementary chain-complex material. Edelsbrunner and Harer's *Computational Topology* is a further-study suggestion from that note, not an uploaded source inspected for this edition.

---

[[Engineering CAD 24 - Half-edge structures and Euler construction|← Chapter 24. Half-edge structures and Euler construction]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 26 - Predicates, constructions and symbolic perturbation|Chapter 26. Predicates, constructions and symbolic perturbation →]]
