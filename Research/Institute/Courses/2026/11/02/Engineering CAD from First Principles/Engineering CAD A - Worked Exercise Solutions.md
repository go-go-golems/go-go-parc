---
title: "Engineering CAD from First Principles — Appendix A. Worked exercise solutions"
aliases:
  - "Worked exercise solutions"
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

# Appendix A. Worked exercise solutions

[[Engineering CAD 32 - A source-guided implementation course|← Chapter 32. A source-guided implementation course]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD B - Source Library|Appendix B. Source library →]]

These are guided solutions to the end-of-chapter exercises. Each solution states its assumptions, gives the calculation or design argument and identifies what an implementation must actually verify. The answers are not substitutes for executing the associated benches: a useful study sequence is to solve on paper, test the bench, then compare the reasoning below.

## A.1 Chapter 1 — independent CAD oracles

Consider a rectangular plate $60\times40\times5$ mm with four nonoverlapping through holes of radius $2$ mm and strictly contained centers. Its ideal volume is

$$
V=5(60\cdot40-4\pi\cdot2^2)=12000-80\pi\approx11748.6726\;\mathrm{mm}^3.
$$

An **analytic volume oracle** detects a missing or filled hole because that changes volume by $5\pi(2^2)=20\pi\approx62.832$ mm³. A **semantic topology oracle** checks that four distinct cylindrical bore faces descend from four intended feature or sketch identities; this detects a wrong face name even when the resulting geometry has the correct volume. An **export oracle** writes and re-imports STEP, checks the unit definition and compares dimensions against 60, 40 and 5 mm; a 25.4× unit conversion error will not pass. The three oracles are independent in what they measure. None alone proves full correctness.

## A.2 Chapter 2 — cubic Bézier derivatives and chord error

Write $B(t)=P_0(1-t)^3+3P_1t(1-t)^2+3P_2t^2(1-t)+P_3t^3$. Differentiate by the product rule, regroup terms and obtain

$$
B'(t)=3[(P_1-P_0)(1-t)^2+2(P_2-P_1)t(1-t)+(P_3-P_2)t^2].
$$

For a second piece $Q$, positional and $C^1$ continuity at the junction require $P_3=Q_0$ and $P_3-P_2=Q_1-Q_0$. For a circle of radius $R$ approximated by an $N$-gon, bisect one of the isosceles triangles formed by a segment and two radii. The half-chord has central angle $\pi/N$; the distance from circle center to chord is $R\cos(\pi/N)$, hence the sagitta is $R(1-\cos(\pi/N))$.

## A.3 Chapter 3 — Euler characteristic of an open cube

A closed cube boundary has $V=8$, $E=12$, $F=6$ and Euler characteristic $\chi=8-12+6=2$. Remove the interior of one face, retaining the twelve edges and eight vertices. The resulting surface is topologically a disk, not a closed sphere. With the remaining five faces, $\chi=8-12+5=1$. This does not contradict the sphere formula: the **underlying space changed** and now has a boundary loop. For a connected orientable surface of genus $g$ with $b$ boundary components, $\chi=2-2g-b$. Here $g=0$, $b=1$, giving $\chi=1$. State whether boundary vertices and edges are included when using a combinatorial count.

## A.4 Chapter 4 — rectangle degrees of freedom

Four independent planar vertices contribute eight scalar variables. Four alternate horizontal/vertical edge constraints contribute four independent scalar equations in a regular rectangle. Width and height dimensions add two independent equations. Fixing one corner contributes two more. The rank is therefore eight, giving

$$
\operatorname{DOF}=8-8=0.
$$

A parallel constraint between the two horizontal edges is already implied by their separate horizontal constraints; it does not increase rank. The sketch remains fully constrained, and a good solver reports the extra condition as redundant rather than overconstrained. The count is conditional on a nondegenerate geometric configuration and independent constraint formulations.

## A.5 Chapter 5 — singular Jacobian is not infinitely many solutions

For $F(x,y)=(x^2+y^2-r^2,x-y)$,

$$
J(x,y)=\begin{bmatrix}2x&2y\\1&-1\end{bmatrix}.
$$

At $(0,0)$, its rank is one. This means the *local linearization at that point* sees only one independent first-order restriction. For $r>0$, however, the equations $x=y$ and $2x^2=r^2$ have exactly two real solutions, $(r/\sqrt2,r/\sqrt2)$ and $(-r/\sqrt2,-r/\sqrt2)$. The origin is not even feasible, since the first residual equals $-r^2$. Jacobian rank at an infeasible singular guess cannot be interpreted as the dimension of the nonlinear feasible set.

## A.6 Chapter 6 — Newton versus one damped LM step

At $(4,-1)$, $F=(-8,0)$ and $J=\begin{bmatrix}8&-2\\1&1\end{bmatrix}$. Newton solves $Jp=-F$, giving $p_N=(0.8,-0.8)$, with step norm approximately $1.13137$. The new residual is $(1.28,0)$, norm $1.28$.

With $\mu=1$, solve $(J^\top J+I)p=-J^\top F$. The normal matrix is $\begin{bmatrix}66&-15\\-15&6\end{bmatrix}$, the right side $(64,-16)$ and determinant 171. Thus

$$
p_{LM}=\left(\frac{144}{171},-\frac{96}{171}\right)\approx(0.842105,-0.561404).
$$

Its norm is approximately $1.01208$. At the new point $(4.842105,-1.561404)$, the residual is approximately $(0.883964,0.280702)$, norm $0.92746$. Here the damped step happens to give a smaller *actual* residual after one iteration, but that is an observed property of this example, not a universal theorem favoring LM over Newton.

## A.7 Chapter 7 — nonunique minimal conflicts

The pair $\{x=0,x=1\}$ is already inconsistent and minimal: either equality alone is feasible. Another minimal inconsistent subset is $\{x=0,x+y=0,y=1\}$. The first two force $y=0$, contradicting $y=1$; deleting any one of the three permits a solution. A third minimal subset uses $x=1$, $x+y=0$ and $y=1$. A greedy deletion algorithm checks constraints in some order and keeps removing those whose deletion leaves infeasibility. Its output depends on order because there is not a unique minimal inconsistent subsystem. Returning *a* minimal subset does not imply returning *the* smallest-cardinality subset, nor all independent conflicts.

## A.8 Chapter 8 — continuation near tangency

A circle $x^2+y^2=R^2$ intersecting the horizontal line $y=c$ has

$$
x(c)=\pm\sqrt{R^2-c^2},\qquad x'(c)=\mp\frac{c}{\sqrt{R^2-c^2}}.
$$

At $c=\pm R$, the two branches meet at $x=0$ and the derivative is unbounded as the tangent configuration is approached from the feasible side. For $|c|>R$ there are no real intersections. A predictor based on the previous derivative takes increasingly large steps near $|c|=R$, so continuation must reduce its step size and detect the singular branch event. The constraint Jacobian is also rank deficient at tangency, which is the numerical reflection of this geometric transition.

## A.9 Chapter 9 — orientation invariances

The oriented area determinant is $\det(B-A,C-A)$. Swapping $B$ and $C$ swaps the determinant columns, changing its sign. Translating all points by $v$ leaves the differences $(B+v)-(A+v)=B-A$ and $(C+v)-(A+v)=C-A$ unchanged in exact arithmetic. In floating point, adding a huge $v$ can round away small differences, so the computed determinant after translation may become zero or inaccurate. The algebraic antisymmetry may still hold for a particular implementation, but a rearranged or independently rounded computation need not have an exactly opposite value. Use filtered exact predicates when the sign controls topology.

## A.10 Chapter 10 — the regime of a contained hole

For a $20\times20$ square and a radius-four circular hole strictly inside, the material area is

$$
A=400-16\pi\approx349.7345\;\mathrm{mm}^2.
$$

The formula remains an ordinary real number even if the circle moves outside. But once its boundary touches the square, the *topological interpretation* changes: the removed region may meet the outer boundary, so it is no longer an independent enclosed hole. As it crosses the side, only the portion intersecting the square should be removed. Correct area becomes $A=400-\operatorname{area}(\text{square}\cap\text{disk})$, not the original constant subtraction. A correct implementation must classify the contact regime before building loops.

## A.11 Chapter 11 — volume identity is necessary, not sufficient

Partition $A\cup B$ into three disjoint measurable sets: $A\setminus B$, $B\setminus A$ and $A\cap B$. Then $V(A)+V(B)$ counts the intersection twice, while $V(A\cup B)$ counts it once. Adding $V(A\cap B)$ to the union restores exactly the double count, proving

$$
V(A\cup B)+V(A\cap B)=V(A)+V(B).
$$

A Boolean result could still have all face orientations reversed or inconsistent despite a separately computed unsigned volume matching the identity. Add a topology/orientation oracle: traverse adjacent faces and verify compatible edge uses, test outward normals at sample points known to be outside and inside, and verify solid classification. An oriented-mesh signed-volume test can add another independent signal.

## A.12 Chapter 12 — when a split face later merges

Represent the original face $F$ as parent of $F_a,F_b,F_c$. Suppose a later operation merges $F_b$ and $F_c$ into $M$. Its ancestry is $\{F_b,F_c\}$, not automatically a unique old identifier. An algorithm must ask whether the merged region is geometrically the same conceptual feature, whether downstream references intended the whole parent face or a particular piece, and whether the merge destroys the distinction previously used by a selector. A stable representation may need a **set-valued correspondence** plus explicit ambiguity status. Choosing the alphabetically first name is deterministic but can be semantically wrong.

## A.13 Chapter 13 — four-bar mobility and singularity

A planar rigid body has three degrees of freedom: two translations and one rotation. Ground one of four links, leaving $3(4-1)=9$ free coordinates. Four ideal planar revolute joints impose two independent positional constraints each in a generic configuration, reducing mobility to $9-2(4)=1$. This is the planar Grübler count.

A singular pose can make one Jacobian row dependent on others, increasing the *infinitesimal* null space. But an infinitesimal direction may fail to integrate into a finite path of valid configurations: higher-order terms can block motion. Rank of the first-order Jacobian and dimension of a connected family of actual solutions are different concepts. The assembly solver should report which statement it has established.

## A.14 Chapter 14 — polygonal approximation of a round hole

The hole radius is $R=2$ mm. For $N=24$ equal segments, radial sagitta is

$$
\delta=2\left(1-\cos\frac{\pi}{24}\right)\approx0.0171103\;\mathrm{mm}.
$$

To require $\delta\le0.01$ mm, solve $2(1-\cos(\pi/N))\le0.01$, giving $N\ge\pi/\arccos(0.995)\approx31.41$; hence use at least **32 segments**. An inscribed polygon cannot preserve exact circular curvature or analytic cylindrical faces, and depending on triangulation it may not preserve exact mass properties. It can preserve approximate dimensions to a declared geometric error but is not an exact B-rep circle.

## A.15 Chapter 15 — a cache key that ignores upstream geometry

Let feature `extrude-body` extrude a sketch by depth 5 mm. In model A, the sketch is a $20\times10$ rectangle; in model B it is a $30\times10$ rectangle. A cache key storing only `(featureId='extrude-body', explicitDepth=5)` collides, although the correct volumes are 1000 and 1500 mm³. The minimal fix is to include a canonical fingerprint of the upstream profile geometry (or a content hash of the dependency node that produces it). A production key also includes the relevant kernel/tolerance settings and any environmental parameters that affect the operation.

## A.16 Chapter 16 — generation-tagged handles

Encode a 32-bit handle as `((generation & 0xffff) << 16) | slot`, reserving a null value. Each time the slot is reused, increment its generation and reject handles whose stored generation differs from the current one. After $2^{16}=65536$ generation increments, a naive 16-bit generation wraps, and an extremely old handle with the same slot and generation could become accidentally valid.

The required safety invariant is **no stale handle can ever compare equal to a live handle that refers to a different object**. Enforce this by rejecting a wrapped slot permanently, using a larger generation field, introducing an epoch with externally enforced lifetime rules, or otherwise proving no old handle can remain reachable. Merely assuming clients will free everything is insufficient for an untrusted or long-lived WASM interface.

## A.17 Chapter 17 — a valid random-hole generator

Sample $w,d,h>0$, an integer $n\ge0$, radii $r_i>0$ and centers $(x_i,y_i)$ satisfying $r_i<x_i<w-r_i$ and $r_i<y_i<d-r_i$, with pairwise distances strictly greater than $r_i+r_j+m$ for a fixed positive margin $m$. Reject or resample configurations that cannot pack within the plate. For the valid domain the oracle is

$$
V=h\left(wd-\pi\sum_{i=1}^{n}r_i^2\right).
$$

A shrinker can first remove whole holes, reduce $n$, simplify dimensions, or move centers toward easy rational coordinates while rechecking the strict containment and nonoverlap preconditions. If it changes a parameter so that a hole crosses the boundary, it has changed the test's premise and must not compare against the old oracle.

## A.18 Chapter 18 — continuity of cubic pieces

The full first- and second-derivative endpoint formulas are

$$
C'(0)=3(P_1-P_0),\quad C'(1)=3(P_3-P_2),
$$

$$
C''(0)=6(P_2-2P_1+P_0),\quad C''(1)=6(P_3-2P_2+P_1).
$$

For a junction at $(1,0)$, choose $P_3=Q_0=(1,0)$, $P_2=(0.7,0)$ and $Q_1=(1.6,0)$. Then the end/start tangent vectors are $(0.9,0)$ and $(1.8,0)$: positive collinear directions give $G^1$, but the unequal lengths violate $C^1$. To enforce $C^2$ in the same parameterization, require both $P_3-P_2=Q_1-Q_0$ and $P_3-2P_2+P_1=Q_2-2Q_1+Q_0$, as well as positional equality.

## A.19 Chapter 19 — revised fit limits

With $H=5.10\pm0.05$ mm, the hole interval is $[5.05,5.15]$ mm. With $S=4.80\pm0.10$ mm, the shaft interval is $[4.70,4.90]$ mm. Nominal clearance is $5.10-4.80=0.30$ mm, minimum clearance is $5.05-4.90=0.15$ mm, and maximum is $5.15-4.70=0.45$ mm. Because the minimum is at least 0.10 mm, the new specification guarantees the stated **diametral** clearance for parts that satisfy both intervals. This conclusion is an interval guarantee, not a probabilistic yield estimate.

## A.20 Chapter 20 — meshing and bend allowance

The right triangle joining the circle center, chord midpoint and arc endpoint has hypotenuse $R$ and adjacent length $R\cos(\pi/N)$. The sagitta is the difference $R-R\cos(\pi/N)$. For $R=20$ mm and target sagitta $\delta\le0.05$ mm,

$$
N\ge\frac{\pi}{\arccos(1-0.05/20)}\approx44.43.
$$

Thus choose **45 segments** or more. For a right-angle bend with $R=3$, $t=2$ mm and $K=0.4$, the neutral-axis radius is $3+0.4(2)=3.8$ mm. Bend allowance is $(\pi/2)(3.8)\approx5.9690$ mm. These calculations address a circular chord tolerance and a neutral-axis bend model; neither alone specifies a complete toolpath or flat pattern.

## A.21 Chapter 21 — sampled design optimization

For $t=2,3,4,5$ mm, $V(t)=t(2400-18\pi)$ gives approximately $4686.903$, $7030.354$, $9373.805$ and $11717.257$ mm³. The stiffness proxy $K=t^3$ gives $8,27,64,125$. If $K\ge27$, feasible options start at $t=3$, which has the smallest volume among feasible sampled choices. If $K\ge65$, $t=4$ fails ($K=64$) and $t=5$ wins in the given discrete set.

This is only an answer under the proxy $K=t^3$ and the stipulated constant-density, constant-planform geometry. The actual part may be a plate with complex loading, anisotropic printing or buckling, requiring a verified mechanical model. The sample-optimal result is not a claim of global optimum over all possible materials and geometries.

## A.22 Chapter 22 — a regression laboratory that can reject wrong geometry

Use a plate with two known through-holes. The **analytic oracle** calculates $V=h(wd-2\pi r^2)$ on the strict-containment domain. A **topological oracle** verifies one closed orientable solid, expected connected components and two bore roles with consistent face adjacency. A **metamorphic relation** translates the entire part and verifies invariant volume and topology, then uniformly scales it and verifies volume scales by $s^3$. A **differential check** builds the same model directly in an independently configured OpenCascade implementation and compares geometry after exporting and importing STEP.

For a previously failing tangent hole, test the exact parameter at contact plus a decreasing sequence on either side. The fix is credible only if the result is either the correctly classified geometry or an explicit unsupported-case rejection, not merely a warning attached to a wrong solid. Require the geometric oracles to pass on all accepted results, add the minimized case to CI, and verify that no regression occurs on the adjacent parameter regimes. Preserve the independent test code so the “fix” cannot trivially change the expected answer.

## How to study with these solutions

Reproduce each calculation without copying it. Change one parameter in the corresponding lab and predict the new result before moving a slider. When you implement your own version of a method, write one analytic oracle and one adversarial test first. The important engineering skill is not memorizing one number; it is knowing which invariants distinguish a correct CAD result from a plausible-looking but wrong one.

---

## Source-guided extension: selected worked solutions

These solutions apply to chapters 23–32. All coordinates and calculations below are original worked examples. Historical textbook references establish definitions and theorem assumptions; they are not benchmark evidence about JigCAD.

## B.23 Regularized sets

**23.A.** The ordinary intersection is $\{2\}\times[1,2]$, an edge of length one. Its interior in $\mathbb R^2$ is empty, so its regularized intersection is empty. Both squares have area four and their common area is zero; the union area is eight. Regularized difference has area four. An area-only oracle returns zero for both the contact edge and the empty set, so it cannot distinguish them. A result-dimension or contact-classification oracle can.

**23.B.** Two closed cubes meeting at exactly one vertex give a regular closed union with a nonmanifold boundary. Triangulate their boundaries without merging any other vertices. The link of the shared vertex consists of two disconnected cycles, not one cycle. This local graph test detects the pinch. Regularity is a point-set property; the link condition checks local boundary topology.

**23.C.** For each rectangle pair, derive intersection intervals independently. Test result membership at points strictly away from all boundary coordinates. Include an exact contact test separately; do not move contact points by an epsilon and then claim the exact boundary semantics passed. Use inclusion–exclusion for area, but also verify disconnected components and contact dimensions. Equal area is a necessary numerical check, not a set-equality proof.

## B.24 Half-edge edits

**24.A.** Label half-edges as follows: $h_0=AB,h_1=BC,h_2=CD,h_3=DA,h_4=BA,h_5=CB,h_6=DC,h_7=AD,h_8=AC,h_9=CA$. Twin pairs are $(0,4),(1,5),(2,6),(3,7),(8,9)$. Choose cycles $f_1=(0,1,9)$, $f_2=(8,2,3)$, and $f_\infty=(4,7,6,5)$. Next is the cyclic successor in each listed tuple, and previous is its cyclic predecessor. This specification supplies the complete connectivity table. There are four vertices, five undirected edges, and three faces including the exterior, so the Euler total is two.

**24.B.** Inserting a vertex inside an ordinary edge replaces one edge by two. Thus $\Delta V=1,\Delta E=1,\Delta F=0$, preserving $V-E+F$. The edit must update both directed uses and both incident face cycles. These count changes resemble a MEV, but a general MEV is defined by splitting a vertex's incidence cycle, not by the English phrase “insert a point into an edge.” A higher-level edge-subdivision operation may be implemented through a suitable primitive sequence.

**24.C.** A diagonal across a face with two well-separated holes can leave one hole on either side. The splice determines two outer cycles. The remaining inner cycles must be assigned by geometric containment in the resulting regions, using a policy that rejects or resolves contact with the new diagonal. The pointer update alone cannot infer this classification. Test that no loop becomes unassigned or is assigned to both faces.

## B.25 Complexes and homology

**25.A.** Orient a square $ABCD$ counterclockwise and split it by $AC$. Then $\partial[ABC]=[AB]+[BC]-[AC]$ and $\partial[ACD]=[AC]+[CD]-[AD]$. Their sum is $[AB]+[BC]+[CD]-[AD]$, the square boundary, because the diagonal cancels. Taking the boundary again cancels each vertex twice with opposite signs. This checks both the matrix convention and the face orientations.

**25.B.** A tetrahedron boundary has $(V,E,F)=(4,6,4)$. Identifying one vertex between two copies gives $(7,12,8)$ and Euler characteristic three. Each edge still belongs to exactly two triangles. The shared vertex has two disconnected triangular link cycles. Its neighborhood is not a disk, so the complex is not a two-manifold even though each component before identification was a sphere. No genus formula for a connected closed orientable surface applies to the pinched result.

**25.C.** Over $\mathbb F_2$, represent each column as a bit vector. Eliminate a pivot by XOR, not by floating-point subtraction. A disk has $(\beta_0,\beta_1)=(1,0)$; an annulus has $(1,1)$. For a closed orientable sphere-like surface, $\beta_2=1$, but a filled three-dimensional ball has $\beta_2=0$. Always record whether the input is a boundary surface or a volume complex.

## B.26 Predicates and constructions

**26.A.** Expansion gives $N^2+2N-(N^2+2N+1)=-1$. For the separate-product binary64 expression used by the lab, exponents 24, 25, and 26 retain a determinant of $-1$; exponent 27 gives zero. The exact input coordinates still fit within the exact-integer range. A fused instruction or a different evaluation algorithm may behave differently, so the observed threshold belongs to this specific computation, not to all possible floating-point implementations.

**26.B.** With homogeneous coordinates $(X,Y,W)=(1,1,3)$, the lines become $Y-X=0$ and $Y+2X-W=0$. Both evaluate to integer zero. No approximation to $1/3$ is needed. The point at infinity has $W=0$ and requires separate interpretation; a rational affine-point API should reject that case rather than divide by zero.

**26.C.** For cocircular sites, either diagonal can satisfy the Delaunay contract. A stable symbolic tie break can select one. For tangent solids, perturbing the contact can produce either overlap or separation, changing the contact set and potentially the topology. A useful implementation either handles the degeneracy exactly or records a justified perturbation policy and reconstructs the intended unperturbed meaning where required.

## B.27 Subdivisions and overlays

**27.A.** The rectangle boundaries meet at $(4,1)$ and $(2,3)$. The common region has width two and height two, hence area four. Since the operand areas are twelve and nine, union is seventeen, difference $A\setminus B$ is eight, and symmetric difference is thirteen. Atomic grid cells can be labeled independently, but adjacent cells with identical membership can belong to one maximal connected overlay face.

**27.B.** There are two disk interiors, a rectangular interior with those disks removed, and the unbounded exterior. The region between rectangle and circles has one outer boundary and two inner boundaries. Enumerating cycles returns these boundary components but does not by itself say which share a face. Face grouping needs containment or equivalent adjacency information.

**27.C.** A sound progression is exact pair classification, exact event identity, parameter sorting along each segment, twin creation, cyclic ordering at vertices, next/previous linkage, cycle traversal, then cycle-to-face grouping. Save the quadratic implementation as an oracle. The sweep should change the search strategy, not the intended output representation or degeneracy semantics.

## B.28 Delaunay and refinement

**28.A.** The circumcircle of $ABC$ has center $(2,1.5)$ and squared radius $6.25$. Substitution of $D=(0,h)$ yields $4+(h-1.5)^2-6.25=h(h-3)$. At $h=1$ the power is $-2$, so $AC$ is illegal and $BD$ is selected. At $h=3$ both are legal. At $h=4$ the power is four, so $AC$ is locally Delaunay. Moving the column of ones across three other columns reverses the determinant sign but must not reverse the geometric classification.

**28.B.** From $\ell_{\min}=2R\sin\alpha$, a ratio at most one gives $\sin\alpha\ge1/2$. Because the smallest triangle angle is at most $60^\circ$, this implies $\alpha\ge30^\circ$. It says nothing about whether repeated insertion reaches such a mesh: an insertion can create new bad elements, and input angles can make the target impossible. Termination requires additional hypotheses and a separation or packing argument.

**28.C.** Keep the protected-edge status separate from geometric legality. A constrained edge may be retained even when it fails the ordinary empty-circle test. In a cocircular tie, a deterministic choice must not flip forever between equal-quality diagonals. Include exact integer-coordinate rectangles as tie cases and nearly cocircular configurations as arithmetic stress cases.

## B.29 Surface tracing

**29.A.** For $F(u)=u\cdot u-\rho^2$, the linearized equation is $2u\cdot\delta=-F(u)$. The minimum-norm solution is parallel to $u$, so write $\delta=\alpha u$. Solving gives $\alpha=-F(u)/(2\|u\|^2)$. At $u_0=(4,1)$, $\rho=4$, this yields $u_1=(66/17,33/34)$. One more application gives $(3.8805704099821745,0.9701426024955436)$. Its squared-radius residual is approximately $3.37600605\times10^{-6}$; its radial error is approximately $4.22000734\times10^{-7}$.

**29.B.** At heights zero and three the intersection circles have radii five and four. At height five the intersection is the north pole $(0,0,5)$, not a regular curve. At height six the intersection is empty. The gradient cross product vanishes at the tangent point. A tracer that treats that event as an ordinary small-radius circle violates its regularity assumption.

**29.C.** Pcurve validation compares each stored parameter pair mapped through its surface against the stored spatial point. Branch-jump diagnostics can compare tangent continuity, predicted progress, correction size, and nearby previously traced branches. None alone proves global completeness. The record also needs a termination reason such as closed, trim boundary, singular, step budget exhausted, or unresolved.

## B.30 Slivers and edge contraction

**30.A.** The two opposite edges $AB$ and $CD$ have length two; the remaining edges have length $\sqrt{2+h^2}$. The center $(0,0,h/2)$ has squared distance $1+h^2/4$ from all vertices. The signed determinant for the stated vertex order is $-4h$, so signed volume is $-2h/3$ and volume is $2h/3$. The sign is orientation, not invalidity by itself. For small $h$, all edge lengths stay bounded away from zero while the volume vanishes.

**30.B.** For the tetrahedron boundary, $\operatorname{Lk}(0)$ includes triangle-boundary edges $12,13,23$ and their faces. $\operatorname{Lk}(1)$ includes $02,03,23$. Their intersection contains edge $23$ and vertices $2,3$ (and the empty simplex). The link of $01$ contains vertices $2,3$ and the empty simplex, but no edge $23$. The extra shared edge makes the link condition fail.

**30.C.** In a planar region, many contractions have zero error to the plane, including contractions that join inappropriate boundary components. The plane objective cannot detect that topology change. Even when the link condition passes, moving the new vertex across a remote sheet may cause self-intersection. Require topological, local geometric, feature-preservation, and global embedding checks as separate acceptance stages.

## B.31 Least squares and rank

**31.A.** With $x=(2,4/3)$, $Ax=(10/3,2/3,4/3)$ and $r=(1/3,-1/3,-2/3)$. Dotting $r$ with columns $(1,1,0)$ and $(1,-1,1)$ gives zero in both cases. The squared residual norm is $1/9+1/9+4/9=2/3$. With the last entry of $b$ changed to one, $x=(2,1)$ gives $Ax=b$ exactly.

**31.B.** $J^TJ=\begin{bmatrix}2&\varepsilon\\\varepsilon&\varepsilon^2\end{bmatrix}$ has trace $2+\varepsilon^2$ and determinant $\varepsilon^2$. Solving its characteristic quadratic gives the displayed $\lambda_\pm$. For small epsilon the direct expression for the smaller eigenvalue subtracts nearly equal numbers. Computing $\sigma_{\min}=|\varepsilon|/\sigma_{\max}$ avoids that cancellation when the determinant is known accurately for this special family.

**31.C.** At $\varepsilon=0$, minimize $x^2+(x-d)^2$; the minimizer is $x=d/2$. The unused variable has minimum-norm value $y=0$. The residual norm is $|d|/\sqrt2$. For nonzero epsilon the exact residual can be zero with $x=0,y=d/\varepsilon$, but those solutions diverge as epsilon approaches zero with fixed nonzero $d$. The discontinuity explains why numerical rank and regularization are necessary policies rather than cosmetic options.

## B.32 Integration and study practice

**32.A.** A first milestone could accept nondegenerate integer segments with no collinear overlaps and return exact rational crossing events. An exact all-pairs oracle and permutation-invariance checks establish a restricted result. A vertical segment through a shared endpoint tests an important boundary case. Returning `UnsupportedOverlap` is better than returning a false empty result before overlap handling is implemented.

**32.B.** Moving a hole to a different fully internal location preserves volume while violating placement intent. A semantic test can verify the named hole center relative to its datum, and membership probes can verify that material is absent at the intended bore center and present at a displaced location. These tests detect errors that the scalar volume cannot.

**32.C.** A suitable example is the planar radius–edge relationship and a mistaken extension to tetrahedral shape. The sliver family in chapter 30 keeps $R/L$ bounded while its normalized volume approaches zero. This does not contradict the planar result; it violates the dimension and geometry of that result's hypotheses.

---

[[Engineering CAD 32 - A source-guided implementation course|← Chapter 32. A source-guided implementation course]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD B - Source Library|Appendix B. Source library →]]
