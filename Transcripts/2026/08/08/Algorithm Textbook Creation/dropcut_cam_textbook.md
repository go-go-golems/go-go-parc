---
title: "Drop-Cutter CAM"
subtitle: "Geometry, Algorithms, Verification, and a Repaired Executable Reference"
author: "Algorithm reconstruction and technical exposition"
date: "August 8, 2026"
documentclass: book
classoption:
  - openany
  - oneside
papersize: letter
fontsize: 10pt
geometry:
  - margin=0.82in
  - headheight=14pt
toc: true
toc-depth: 3
numbersections: true
secnumdepth: 3
colorlinks: true
linkcolor: NavyBlue
urlcolor: NavyBlue
citecolor: NavyBlue
link-citations: true
bibliography: references.bib
reference-section-title: References
nocite: |
  @*
keywords:
  - CAM
  - drop-cutter
  - computational geometry
  - differential geometry
  - toolpath generation
  - dexel verification
header-includes:
  - \usepackage{amsmath,amssymb,mathtools}
  - \usepackage{booktabs,longtable,array}
  - \usepackage{float}
  - \usepackage{microtype}
  - \usepackage{enumitem}
  - \usepackage{fancyhdr}
  - \usepackage{xcolor}
  - \usepackage{caption}
  - \definecolor{NavyBlue}{RGB}{22,65,112}
  - \definecolor{LightGray}{RGB}{245,247,249}
  - \setlist{nosep}
  - \pagestyle{fancy}
  - \fancyhf{}
  - \fancyhead[LE,RO]{\small Drop-Cutter CAM}
  - \fancyhead[RE,LO]{\small Geometry, Algorithms, and Verification}
  - \fancyfoot[C]{\thepage}
  - \setlength{\parskip}{0.35em}
  - \setlength{\parindent}{0pt}
---

\frontmatter

# Preface {-}

This book reconstructs, repairs, executes, and explains a compact three-axis drop-cutter CAM system. The starting artifact was a single React/Three.js JSX file that combined geometric algorithms, asynchronous browser control, rendering, a user interface, G-code export, and a sampled material-removal verifier. The repaired implementation separates the numerical core from the interface, adds an executable test suite, records baseline-versus-fixed probes, generates reference G-code, and supplies a standalone interactive visual laboratory.

The central question is simple to state:

> Given a triangle mesh, a vertical-axis cutter, and a horizontal cutter location $(X,Y)$, how low may the cutter tip move without intersecting the model?

The answer defines a *cutter-location surface* or *CL surface*. Once the CL surface can be evaluated reliably, many familiar CAM strategies become geometric sampling problems: raster finishing traces the CL surface along parallel rows; waterline finishing traces its level sets; Z-level roughing finds horizontal free-space intervals; approximate constant-spacing finishing traces level sets of a distance field on the CL surface; and verification sweeps the cutter over a sampled stock height field.

The mathematics therefore spans several fields:

- differential geometry, for surface metrics, gradients, curvature, and geodesic distance;
- computational geometry, for robust predicates, spatial indexing, offsets, contour extraction, and degeneracies;
- numerical analysis, for interpolation, fast sweeping, graph shortest paths, and error budgets;
- CNC programming, for interpolation planes, modal state, arc centers, and postprocessing;
- geometry processing, for triangle soups, sampled scalar fields, and dexel representations.

The exposition is self-contained at the level of multivariable calculus, vectors, basic data structures, and elementary algorithm analysis. It uses the uploaded books as its principal mathematical context: Kobayashi for smooth curves and surfaces [@kobayashi2019], Botsch et al. for polygon meshes and sampled fields [@botsch2010], de Berg et al. for geometric algorithms and robustness [@deberg2008], and Crane for the computational viewpoint on differential geometry [@crane2025]. CAM-specific context comes primarily from Choi and Jerard [@choi1998], Feng and Li [@feng2002], and Kim [@kim2007].

## What was repaired {-}

The original program was ambitious and mostly coherent, but several defects mattered materially:

1. arc fitting omitted the incoming first segment of many finishing moves;
2. the shallow/steep hybrid did not guarantee coverage and left sampled islands uncut;
3. the marching-squares ambiguity rule did not respect the bilinear interpolant;
4. closed-contour mask splitting lost runs that crossed the stored seam;
5. the Eikonal solver assumed square cells and a fixed number of sweeps;
6. the so-called constant-scallop equation was a scalar slope approximation rather than the full surface metric;
7. entry paths, links, target sampling, and dexel verification were not mutually consistent;
8. STL parsing, boundary interpolation, predicates, modal G-code state, and asynchronous cancellation had edge-case faults.

The repaired build passes 14 executable tests. The complete defect matrix appears in `docs/algorithm-audit.md` and in Appendix B.

## Safety notice {-}

This is a research and educational reference, not a certified CAM kernel. A visually plausible toolpath can still be unsafe. The implementation does not model the holder, shank, fixtures, machine kinematics, acceleration limits, controller-specific interpolation semantics, or undercuts. Any generated program must be checked in an independent simulator, reviewed for the actual controller, dry-run above the workpiece, and proven out under supervision.

## Repository map {-}

| Path | Purpose |
|---|---|
| `src/dropcut-core.mjs` | Repaired, dependency-free computational core |
| `src/dropcut-cam-fixed.jsx` | Repaired React/Three.js application |
| `src/dropcut-cam-original.jsx` | Preserved uploaded source |
| `src/dropcut-core-baseline.mjs` | Extracted baseline core used for probes |
| `tests/run-tests.mjs` | Executable regression suite |
| `tests/probe-*.mjs` | Baseline-versus-fixed defect demonstrations |
| `benchmarks/run-benchmarks.mjs` | Reproducible strategy benchmark |
| `examples/*.ngc` | Reference G-code exports |
| `visual_lab/` | Standalone interactive explanatory tool |
| `figures/`, `screenshots/` | Generated diagrams and captured interaction states |

\clearpage

# Notation and conventions {-}

We use a right-handed machine coordinate system. The cutter axis is the positive $z$ axis, and the cutter translates only: there is no tool-axis tilt. A cutter location is $(X,Y,Z)$, where $Z$ is the tip height. A triangle has vertices

$$
\mathbf a=(a_x,a_y,a_z),\qquad
\mathbf b=(b_x,b_y,b_z),\qquad
\mathbf c=(c_x,c_y,c_z).
$$

The cutter radius is $R$. The model's upper envelope is the greatest model height at a horizontal position. The safe cutter-tip height is denoted $F(X,Y)$; a sampled CL field stores $F_{ij}=F(x_i,y_j)$.

For a graph surface $z=f(x,y)$ we write

$$
f_x=\frac{\partial f}{\partial x},\qquad
f_y=\frac{\partial f}{\partial y},\qquad
\nabla f=(f_x,f_y).
$$

A planar path is $\gamma(t)=(x(t),y(t))$. Its lifted CL path is

$$
\widehat\gamma(t)=\bigl(x(t),y(t),F(x(t),y(t))\bigr).
$$

Unless stated otherwise, distances are in millimetres, feed rates are in millimetres per minute, and angles are in radians inside formulas.

\mainmatter

# The CAM Problem as a Geometric Pipeline

## Three-axis drop-cutter machining

A fixed-axis three-axis machine moves a cutter in $x$, $y$, and $z$ while keeping the cutter axis parallel to $z$. For a prescribed horizontal cutter-center position $(X,Y)$, the drop-cutter operation lowers the cutter until it first touches the model. The resulting tip height is the smallest collision-free $Z$.

This is a configuration-space problem. Instead of moving a finite cutter around a fixed model, one may enlarge or transform the model by the reflected cutter and move a point representing the cutter reference. The same idea appears in robot motion planning, where a configuration-space obstacle is a Minkowski sum of an obstacle with a reflected robot [@deberg2008]. In three-axis CAM the symmetry and fixed orientation allow a particularly efficient 2.5D formulation: for each $(X,Y)$, compute one scalar $F(X,Y)$.

![End-to-end repaired pipeline](../figures/pipeline_overview.png){width=96%}

The executable pipeline is:

1. parse STL triangles;
2. normalize and bound the mesh;
3. build a spatial index over projected triangle boxes;
4. evaluate exact ball- or flat-cutter contact against candidate triangles;
5. optionally sample the evaluator into a CL field;
6. generate roughing and finishing paths;
7. refine path segments to a chordal tolerance;
8. link paths with safe cuts, retracts, ramps, or helices;
9. optionally replace polyline runs by planar arcs;
10. export modal G-code;
11. simulate material removal on a dexel grid;
12. compare the machined height field with the target upper envelope.

Each stage has its own approximation. Reliability comes not from pretending the approximations disappear, but from stating their invariants and making their error budgets compatible.

## The upper-envelope assumption

The program treats the part as a height field in the machining direction. A vertical line may intersect many triangles, but only the highest accessible surface affects a cutter approaching from $+z$. This yields the *upper envelope*

$$
h(x,y)=\max\{z:(x,y,z)\text{ lies on a model triangle}\}.
$$

The representation is appropriate for molds, reliefs, terrain-like parts, and other 2.5D surfaces. It cannot represent an undercut that requires the cutter to pass beneath an overhang, nor can it reason about a vertical wall as a separate lower sheet. The limitation is geometric, not merely an implementation detail.

A general polygon mesh consists of topology plus vertex positions; an STL face set discards most connectivity and stores independent triangles, often called a triangle soup [@botsch2010]. The drop-cutter evaluator needs only triangle geometry and therefore can work directly on STL. Topological algorithms such as manifold repair would need richer connectivity.

## Invariants that organize the implementation

The repaired core uses the following invariants:

- **Model invariant:** every coordinate and scale is finite; every triangle contributes exactly nine numbers.
- **Evaluator invariant:** `evalTipZ(X,Y)` returns a finite safe tip height or throws on non-finite input.
- **CL-field invariant:** the sampled grid exactly spans its declared rectangle; boundary interpolation is exact in the grid coordinates.
- **Path invariant:** a stored move is interpreted relative to the machine position left by the preceding move.
- **Arc invariant:** fitted operations include the actual incoming point, even when the compact move array does not.
- **Verification invariant:** only non-rapid geometry removes stock; the simulated geometry matches the exported fitted geometry.
- **Statistics invariant:** deviation statistics are computed on an explicit projected-part mask, not on background stock.

These invariants are more valuable than a collection of special-case fixes. They let tests target contracts rather than screenshots.

## A minimal mathematical statement

Let $S$ be the model surface and let $C_Z$ be the cutter placed with tip at $(X,Y,Z)$. The drop-cutter height is

$$
F(X,Y)=\inf\{Z:C_Z\cap S=\varnothing\text{ and }C_{Z+\epsilon}\cap S=\varnothing\text{ for all }\epsilon>0\}.
$$

For the supported cutters, the cutter surface above the tip can be written as a radial function $q(r)$ for $0\le r\le R$:

$$
q_{\mathrm{flat}}(r)=0,
$$

$$
q_{\mathrm{ball}}(r)=R-\sqrt{R^2-r^2}.
$$

A model point $(x,y,z)$ under the footprint imposes

$$
Z+q\left(\sqrt{(x-X)^2+(y-Y)^2}\right)\ge z.
$$

Therefore

$$
F(X,Y)=\max_{(x,y,z)\in S,\;r\le R}\left[z-q(r)\right],
$$

with a floor constraint added outside the model. This max-envelope formula is the conceptual core of the entire program.

## Exercises

1. Explain why an upper-envelope method cannot distinguish two triangles whose $xy$ projections overlap if the lower triangle is everywhere below the upper triangle.
2. Show that a flat end mill makes $F(X,Y)$ the maximum model height inside a disk of radius $R$ centered at $(X,Y)$.
3. For a ball tool, verify that $q(0)=0$ and $q(R)=R$.
4. List three safety-relevant machine properties that are absent from the geometric model.

# Mathematical Foundations

## Curves, speed, and arc length

A parametric space curve is a map

$$
\mathbf p:[a,b]\to\mathbb R^3,\qquad t\mapsto\mathbf p(t).
$$

Its velocity is $\mathbf p'(t)$, its speed is $\|\mathbf p'(t)\|$, and its length is

$$
L=\int_a^b\|\mathbf p'(t)\|\,dt.
$$

When a curve is parameterized by arc length $s$, its tangent has unit length. Curvature measures the rate at which this tangent changes; for a unit-speed curve, $\kappa=\|d\mathbf T/ds\|$ [@kobayashi2019; @crane2025]. CAM uses these ideas in three places:

- estimating path length and machining time;
- controlling polyline chord error;
- replacing sufficiently circular point sequences by CNC arcs.

For a circular arc of radius $\rho$ and central angle $\theta$, the length is $\rho|\theta|$. The maximum sagitta between the arc and its chord is

$$
e=\rho\left(1-\cos\frac{|\theta|}{2}\right).
$$

For small $\theta$, $e\approx \rho\theta^2/8$. This relation explains why smaller chord tolerances cause rapidly increasing point counts in curved regions.

## Parametric surfaces and the first fundamental form

A smooth surface patch is a map

$$
\mathbf p(u,v):\Omega\subset\mathbb R^2\to\mathbb R^3.
$$

The tangent vectors $\mathbf p_u$ and $\mathbf p_v$ span the tangent plane when they are linearly independent. Their inner products define

$$
E=\mathbf p_u\cdot\mathbf p_u,\qquad
F=\mathbf p_u\cdot\mathbf p_v,\qquad
G=\mathbf p_v\cdot\mathbf p_v.
$$

The squared length of a parameter displacement $(du,dv)$ is

$$
ds^2=E\,du^2+2F\,du\,dv+G\,dv^2.
$$

This quadratic form is the first fundamental form, or induced metric [@kobayashi2019]. It tells us how planar parameter-space motion stretches on the surface. Crane presents the same idea as

$$
g(X,Y)=d\mathbf p(X)\cdot d\mathbf p(Y),
$$

emphasizing that the differential pushes tangent vectors from the parameter domain into space [@crane2025].

## Graph surfaces

The CL surface is represented as a graph

$$
\mathbf p(x,y)=\bigl(x,y,f(x,y)\bigr).
$$

Then

$$
\mathbf p_x=(1,0,f_x),\qquad
\mathbf p_y=(0,1,f_y),
$$

so

$$
E=1+f_x^2,\qquad F=f_xf_y,\qquad G=1+f_y^2.
$$

In matrix form,

$$
\mathbf G=
\begin{bmatrix}
1+f_x^2 & f_xf_y\\
f_xf_y & 1+f_y^2
\end{bmatrix}
=\mathbf I+\nabla f\,\nabla f^T.
$$

For a planar displacement $d\mathbf x=(dx,dy)^T$,

$$
ds^2=d\mathbf x^T\mathbf G\,d\mathbf x
=dx^2+dy^2+(f_xdx+f_y dy)^2.
$$

This direction dependence is crucial. Along the direction of steepest ascent, the stretch factor is $\sqrt{1+\|\nabla f\|^2}$. Along a level-set tangent, $\nabla f\cdot d\mathbf x=0$, so the instantaneous surface length equals the planar length. A scalar slope factor cannot capture both directions simultaneously.

The surface area element is

$$
dA=\sqrt{EG-F^2}\,dx\,dy
=\sqrt{1+f_x^2+f_y^2}\,dx\,dy.
$$

These graph-surface formulas are standard consequences of the first fundamental form [@kobayashi2019].

## Normals, slope, and steep regions

A unit normal to the graph is

$$
\mathbf n=\frac{(-f_x,-f_y,1)}{\sqrt{1+f_x^2+f_y^2}}.
$$

Let $\alpha$ be the angle between the normal and $+z$. Then

$$
\cos\alpha=\frac{1}{\sqrt{1+\|\nabla f\|^2}},\qquad
\tan\alpha=\|\nabla f\|.
$$

Thus a user-specified steepness angle $\alpha_0$ translates naturally to the threshold

$$
\|\nabla f\|\gtrless\tan\alpha_0.
$$

The hybrid strategy uses this relation on the sampled CL field, not directly on the model. This distinction matters because the cutter offset smooths and changes the geometry.

## Level sets

For a scalar field $\phi(x,y)$, a level set is

$$
\Gamma_c=\{(x,y):\phi(x,y)=c\}.
$$

Where $\nabla\phi\ne0$, the gradient is normal to the level set. Marching squares extracts a piecewise-linear approximation of $\Gamma_c$ from a rectangular grid. Waterline machining uses $\phi=F$ and constant height $c=z$. Approximate constant-spacing machining uses a distance-like field $\phi=T$ and levels $c=1,2,3,\ldots$.

## Curvature and scallop height

For a ball end mill of radius $R$, two adjacent passes on a flat plane leave a cusp. In the normal cross-section, two circles of radius $R$ have center spacing $s$. At the midpoint, the cusp height $h$ above the tangent plane satisfies

$$
(R-h)^2+\left(\frac{s}{2}\right)^2=R^2.
$$

Solving,

$$
s=2\sqrt{2Rh-h^2}.
$$

For $h\ll R$,

$$
s\approx\sqrt{8Rh}.
$$

This exact flat-plane relation is used to choose a nominal spacing. On a curved surface the effective normal-section radius changes with surface curvature and path direction. Hence equal pass distance does not, in general, imply equal scallop height [@feng2002; @kim2007].

![Ball-end scallop geometry](../figures/ball_scallop_geometry.png){width=78%}

## Exercises

1. Derive the graph-surface metric from $\mathbf p_x$ and $\mathbf p_y$.
2. Prove that a level-set tangent is orthogonal to the gradient.
3. Compute the nominal pass spacing for $R=2$ mm and $h=0.08$ mm.
4. Explain why the slope stretch factor is exact along $\nabla f$ but not perpendicular to it.
5. Derive the small-$h$ approximation $s\approx\sqrt{8Rh}$.

# Triangle Meshes, STL, and the Upper Envelope

## Triangle meshes as piecewise-linear surfaces

A triangle mesh may be viewed as a continuous piecewise-linear surface. Inside a triangle with vertices $\mathbf a$, $\mathbf b$, and $\mathbf c$, every point has barycentric coordinates

$$
\mathbf p=\lambda_a\mathbf a+\lambda_b\mathbf b+\lambda_c\mathbf c,
\qquad
\lambda_a+\lambda_b+\lambda_c=1.
$$

For an interior point, all three coefficients are nonnegative. Each triangle is therefore a linear parameterized patch. Botsch et al. emphasize that this piecewise-linear interpretation remains valid even when the file format stores only discrete vertex positions [@botsch2010].

For a smooth surface sampled with maximum edge length $h$, a well-shaped piecewise-linear approximation commonly has geometric error of order $O(h^2)$ away from singular features. The constant depends on curvature, so high-curvature regions need denser sampling [@botsch2010]. This observation is directly relevant to CAM: no path-generation algorithm can recover features that the STL did not resolve.

## STL as a triangle soup

STL stores independent triangular facets. Binary STL consists of:

- an 80-byte header;
- a 32-bit little-endian triangle count;
- for each triangle: a normal, three vertices, and a two-byte attribute count.

ASCII STL stores repeated `vertex x y z` records. Neither format guarantees watertightness, consistent orientation, unique shared vertices, or a valid manifold. A parser should therefore distinguish *syntactic acceptance* from *geometric validity*.

The repaired parser makes only the assumptions required by the drop-cutter core:

- the input is an `ArrayBuffer` or typed-array view;
- a binary file may contain trailing application bytes after its triangle records;
- ASCII keywords are case-insensitive;
- coordinates must be finite;
- at least one complete triangle must be present.

It deliberately does not trust stored facet normals, because the evaluator recomputes triangle planes from the vertices.

### Parser pseudocode

```text
PARSE_STL(bytes)
    if bytes can contain a binary header then
        n <- little-endian uint32 at byte 80
        required <- 84 + 50 n
        if n > 0 and required <= byte_count then
            read n triangles
            reject any non-finite coordinate
            return triangle array
    decode bytes as text
    find all case-insensitive "vertex x y z" triples
    reject non-finite numbers
    discard an incomplete final triangle, if any
    reject an empty result
    return triangle array
```

A production parser may additionally validate attribute records, report ignored bytes, detect implausible triangle counts before allocation, and support explicit format selection. The repaired parser chooses binary first because a binary header is allowed to begin with the word `solid`; using that prefix as the sole discriminator is unsafe.

## Model normalization

The model builder computes an axis-aligned bounding box and applies a simple affine normalization:

$$
x'=(x-c_x)s,
\qquad
y'=(y-c_y)s,
\qquad z'=(z-z_{\min})s,
$$

where

$$
c_x=\frac{x_{\min}+x_{\max}}{2},
\qquad
c_y=\frac{y_{\min}+y_{\max}}{2}.
$$

This centers the part in $x$ and $y$, places its minimum $z$ at zero, and applies a positive user scale $s$. The transformation is convenient for visualization and examples. It is not a general setup transformation: a real CAM system would preserve or explicitly manage work offsets, stock coordinates, fixture coordinates, units, and part orientation.

The builder rejects:

- an empty array;
- an array whose length is not divisible by nine;
- non-finite coordinates;
- a non-finite or nonpositive scale.

These checks are small but important. A single `NaN` in a bounding box can poison every later grid dimension, interpolation, and G-code line.

## The projected triangle and plane equation

For drop-cutter contact, each nonvertical triangle is expressed as a graph over its $xy$ projection. Let

$$
\mathbf u=\mathbf b-\mathbf a,
\qquad
\mathbf v=\mathbf c-\mathbf a,
\qquad
\mathbf n=\mathbf u\times\mathbf v=(n_x,n_y,n_z).
$$

When $n_z\ne0$, the plane can be written

$$
z=Ax+By+C,
$$

with

$$
A=-\frac{n_x}{n_z},
\qquad
B=-\frac{n_y}{n_z},
\qquad
C=a_z-Aa_x-Ba_y.
$$

A triangle whose projected area is zero has $n_z=0$. Such a triangle cannot be treated as a single-valued graph. Its edges and vertices may still affect a finite cutter, so the evaluator does not simply discard the whole triangle; it skips only the facet-interior plane candidate.

## Point-in-triangle predicates

The signed twice-area of three planar points is

$$
\operatorname{orient2d}(\mathbf a,\mathbf b,\mathbf p)
=(b_x-a_x)(p_y-a_y)-(b_y-a_y)(p_x-a_x).
$$

For a nondegenerate projected triangle, a point is inside or on the boundary if the three edge orientations have the same sign, allowing a small error bound. The repaired test first checks the triangle's own signed area. This prevents a degenerate triangle from accepting every point merely because all three edge determinants are near zero.

The tolerance is scaled as

$$
\varepsilon=64\,\epsilon_{\mathrm{mach}}\,M^2,
$$

where $M$ is the largest relevant coordinate magnitude. The $M^2$ factor matches the determinant's units. This is a heuristic floating-point filter, not an exact predicate. Robust computational geometry often computes determinant signs with adaptive precision [@shewchuk1997], and de Berg et al. warn that naive fixed epsilon rules can create mutually inconsistent decisions [@deberg2008].

## Upper-envelope construction from triangles

For a flat point probe, the model height at $(x,y)$ is

$$
h(x,y)=\max_{t:\,(x,y)\in\pi_{xy}(t)} z_t(x,y),
$$

where $z_t(x,y)$ is the plane height of triangle $t$ and $\pi_{xy}$ denotes projection. The actual cutter evaluator generalizes this maximum by considering a disk neighborhood and a cutter profile.

The repaired verifier obtains its target height field from the same exact upper-envelope machinery used by path generation, rather than from a separate triangle rasterizer. This removes one avoidable disagreement between generation and verification.

## Mesh defects and their practical effect

STL defects influence drop-cutter CAM differently:

- **inconsistent normals:** usually harmless here because normals are recomputed;
- **duplicate triangles:** waste time and may duplicate contact candidates, but the maximum is unchanged;
- **small cracks:** may expose a lower sheet or floor through the upper envelope;
- **self-intersections:** the maximum is still defined, but may not correspond to the intended solid boundary;
- **nonmanifold edges:** do not prevent local contact evaluation, but signal an ambiguous model;
- **zero-area facets:** should be rejected or reduced to edge/vertex contributions;
- **thin vertical walls:** their projected area may vanish, so only edge contact remains;
- **unit mismatch:** scales every geometric parameter and is potentially catastrophic.

Triangle-soup repair is a separate and difficult problem. Volumetric conversion and re-extraction can produce a watertight model but may erase fine features [@botsch2010]. The repaired application does not silently repair topology; it keeps the model geometry explicit.

## Exercises

1. Derive the plane coefficients $A,B,C$ from the cross product normal.
2. Show that `orient2d` has units of length squared and explain why its tolerance should scale similarly.
3. Give an example in which a crack in the top surface exposes an unintended lower triangle to a drop-cutter query.
4. Explain why stored STL normals are unnecessary for the exact contact formulas used here.
5. Design a parser test for a binary STL whose 80-byte header begins with `solid`.

# Robust Geometry and Spatial Indexing

## Why geometry code fails differently

In ordinary numerical code, a small error often produces a small output error. In geometric code, a small sign error may change topology: an inside test becomes outside, two contour segments connect differently, or an arc changes direction. De Berg et al. organize the problem into general-position reasoning, explicit treatment of degeneracies, and careful implementation of primitive predicates [@deberg2008].

The repaired core follows a pragmatic hierarchy:

1. reject non-finite data early;
2. phrase topology in terms of a small number of determinant and interval predicates;
3. use scale-aware tolerances rather than unrelated absolute constants;
4. reject degenerate objects rather than assigning them arbitrary interiors;
5. preserve structural output even when exact arithmetic is not used;
6. test known degenerate and nearly degenerate cases.

For safety-critical production code, adaptive exact predicates remain preferable where a sign changes connectivity.

## Broad phase and narrow phase

A cutter query should not test every triangle. Let $n$ be the number of triangles and $q$ the number of CL evaluations. A brute-force evaluator is $O(nq)$, which is prohibitive because finishing may call the evaluator thousands or millions of times.

Collision-detection systems separate:

- a **broad phase**, which cheaply finds possible contacts;
- a **narrow phase**, which evaluates exact contact formulas.

The repaired core uses a uniform 2D spatial hash over triangle projection boxes. A triangle is inserted into every grid cell intersected by its $xy$ bounding box. A query visits cells intersected by the cutter footprint and then checks expanded triangle boxes before exact geometry.

![Uniform spatial hash query](../figures/spatial_hash_query.png){width=84%}

## Choosing cell size

The cell size is

$$
c=\max\left(R,\frac{\sqrt{W^2+H^2}}{256},0.25\right),
$$

where $W,H$ are model spans. This is a heuristic compromise:

- cells much smaller than the cutter radius cause one query to visit many cells;
- cells much larger than local triangles produce long candidate lists;
- a lower bound avoids enormous grids for tiny radii;
- the diagonal term caps the grid resolution near $256$ cells across a characteristic span.

No single uniform-grid choice is optimal for highly nonuniform geometry. A bounding-volume hierarchy or kd-tree adapts more naturally; kd-trees provide linear storage and $O(n\log n)$ construction for point data, with analogous spatial-pruning principles for geometric objects [@deberg2008]. The uniform hash is used because it is compact, easy to inspect, and effective for the intended height-field examples.

## Duplicate suppression by query stamps

A triangle spanning several cells would otherwise be tested once per visited cell. The index stores a stamp array with one integer per triangle. Every query increments a query identifier $q$; a triangle is processed only when `stamp[t] != q`, after which its stamp is set to $q$.

This replaces a temporary `Set` allocation with $O(1)$ array operations. Because the identifier is a 32-bit unsigned integer, the repaired code clears the stamp array before wraparound. Long-running browser sessions should not rely on integer overflow silently preserving uniqueness.

## Expanded bounding boxes

A triangle can touch a radius-$R$ cutter centered outside the triangle's own projection. Therefore the narrow-phase box test uses

$$
X\in[x_{\min}-R,x_{\max}+R],\qquad
Y\in[y_{\min}-R,y_{\max}+R].
$$

This is equivalent to expanding the projected triangle box by the cutter disk's axis-aligned bounding box. Passing this test is necessary but not sufficient; it merely avoids exact calculations for distant triangles.

## Outside-domain behavior

If the entire cutter disk lies outside the model's grid bounds, the evaluator immediately returns the floor contact height. Without this guard, a query could produce an index range with the lower bound greater than the upper bound or depend on implementation quirks of empty loops. Explicit domain behavior also makes linking paths beyond the model margin predictable.

For a ball tool, the internal `best` quantity is initially the ball-center height above the floor, $z_{\mathrm{floor}}+R$, and the evaluator returns `best-R`. For a flat tool, the reference is already the tip plane.

## Complexity model

Let $k$ be the number of distinct candidate triangles visited by a query. The evaluator is approximately $O(k)$, with a small constant number of vertex, edge, and facet calculations per triangle. Grid construction is proportional to the total number of triangle-cell overlaps, not merely $n$.

A useful performance model is

$$
T_{\mathrm{total}}
\approx T_{\mathrm{index}}
+N_{\mathrm{eval}}\,\mathbb E[k]T_{\mathrm{contact}}
+T_{\mathrm{path}}
+T_{\mathrm{verify}}.
$$

In practice, reducing unnecessary evaluator calls often matters as much as optimizing a single contact formula. Shared CL fields, adaptive refinement, and candidate indexing are therefore architectural decisions, not micro-optimizations.

## Exercises

1. Explain why a triangle must be inserted into all spatial-hash cells touched by its projection box.
2. Construct a mesh for which a uniform grid performs poorly but a BVH performs well.
3. Show that expanding a triangle box by $R$ is necessary for a disk-footprint query.
4. Estimate the memory used by a stamp array for ten million triangles.
5. Describe how adaptive exact orientation predicates could be integrated without changing the higher-level algorithms.

# Cutter Geometry and Configuration Space

## Cutter reference and radial profile

The implementation uses the cutter tip as its $z$ reference. For an axisymmetric cutter, the lower cutter surface at horizontal radius $r$ is

$$
z_{\mathrm{cutter}}(r)=Z+q(r).
$$

For a flat end mill,

$$
q(r)=0,\qquad 0\le r\le R.
$$

For a ball end mill,

$$
q(r)=R-\sqrt{R^2-r^2},\qquad 0\le r\le R.
$$

The ball center is at height $Z+R$. At the axis, the sphere reaches the tip; at the equator, the cutter surface is $R$ above the tip.

## Contact as a max-plus dilation

A point $\mathbf p=(x,y,z)$ imposes

$$
Z\ge z-q(r),
\qquad
r=\sqrt{(x-X)^2+(y-Y)^2}.
$$

Taking the maximum over all model points under the footprint gives

$$
F(X,Y)=\sup_{\mathbf p\in S,\;r\le R}\bigl(z-q(r)\bigr).
$$

This is a morphological dilation in a max-plus algebra: the surface is combined with a reflected cutter profile. It is also a fixed-orientation configuration-space obstacle boundary. The equivalence is the CAM counterpart of replacing a translating robot by a point and enlarging obstacles via a Minkowski sum [@deberg2008].

For a flat tool, $q=0$, so the CL surface is the maximum of the model over a horizontal disk. For a ball tool, points near the disk edge are discounted by almost $R$ because the ball is high there.

## Why the maximum occurs at vertex, edge, or facet contact

Restrict the max-envelope objective to one triangle. The feasible point lies in a compact triangular domain intersected with the cutter footprint. A maximum can occur:

- at a triangle vertex;
- on a triangle edge;
- at an interior stationary point of the triangle facet.

This is the geometric reason the evaluator decomposes contact into vertex, edge, and facet candidates. The decomposition is analogous to feature-based collision detection: a smooth convex cutter touches a polyhedron at a combination of cutter and polyhedron features.

![Ball-tool triangle contact candidates](../figures/ball_contact_decomposition.png){width=88%}

## Cutter allowance as an offset

For roughing, the implementation leaves a requested allowance $a$ by using a larger cutter of radius $R+a$ and then adding a vertical allowance $a$ to the resulting tip height. This produces a conservative 3-axis envelope:

$$
F_a(X,Y)\approx F_{R+a}(X,Y)+a.
$$

It should not be confused with an exact constant normal offset of the target surface. Exact normal allowance depends on local surface orientation, cutter shape, and accessibility. The implemented construction is simple, monotone, and safe-biased for the intended 2.5D roughing use, but may leave more stock than requested on slopes.

## Floor contact

A finite stock floor prevents the cutter from dropping without bound outside the model. The floor is treated as a horizontal plane. For the flat tool, the safe tip is `floorZ`; for the ball tool, the internal center height is `floorZ+R`, yielding the same tip height after subtracting $R$.

This convention keeps the returned `evalTipZ` value consistently tied to the cutter tip.

## Tool families not represented

A toroidal or bull-nose tool has a piecewise profile involving a corner radius and a flat central region. A tapered tool has a radius that changes with $z$. Holders and shanks are non-cutting collision bodies. All can still be treated through configuration-space geometry, but the feature-contact cases expand substantially. A production implementation normally represents the entire tool assembly and computes both cutting contact and non-cutting collision.

## Exercises

1. Starting from the ball equation, derive $q_{\mathrm{ball}}(r)$.
2. Show that increasing the model height anywhere cannot decrease $F(X,Y)$.
3. Explain why the maximum over a triangular domain can occur on its boundary even if the unconstrained stationary point lies outside.
4. Sketch a radial profile for a bull-nose cutter and identify its different feature regions.
5. Discuss why a normal stock allowance is not the same as a vertical allowance.

# Exact Drop-Cutter Contact with a Triangle

## Ball-tool vertex contact

Let the ball center be $(X,Y,Z_c)$ and radius $R$. A triangle vertex $\mathbf a$ can contact the lower hemisphere only when its horizontal distance

$$
d_a^2=(a_x-X)^2+(a_y-Y)^2
$$

is less than $R^2$. The sphere equation gives the center height required to pass through the vertex:

$$
Z_c=a_z+\sqrt{R^2-d_a^2}.
$$

The tip height is $Z=Z_c-R$. The evaluator takes the maximum over all feasible vertex candidates.

## Ball-tool edge contact

Consider an edge parameterized by horizontal arc-length coordinate $t$:

$$
\mathbf e(t)=\mathbf e_1+t\widehat{\mathbf u},\qquad 0\le t\le L,
$$

where $\widehat{\mathbf u}$ is the unit direction of the edge's $xy$ projection and $L$ is its projected length. Let the query point project to coordinates $(t_f,d_\perp)$ in this local frame. The sphere's cross-section at perpendicular offset $d_\perp$ has radius

$$
\rho=\sqrt{R^2-d_\perp^2}.
$$

If $d_\perp\ge R$, the edge cannot contact the ball. Let $s=t-t_f$ be displacement from the projected foot. Along the edge, height is linear:

$$
z(s)=z_f+ms,
$$

where $m=\Delta z/L$. The required center height is

$$
\Phi(s)=z_f+ms+\sqrt{\rho^2-s^2}.
$$

Differentiate:

$$
\Phi'(s)=m-\frac{s}{\sqrt{\rho^2-s^2}}.
$$

Setting $\Phi'(s)=0$ yields

$$
s^*=\frac{m\rho}{\sqrt{1+m^2}}.
$$

The feasible interval must satisfy both the sphere cross-section and the finite edge:

$$
s\in[-\rho,\rho]\cap[-t_f,L-t_f].
$$

The algorithm clamps $s^*$ to this interval and evaluates $\Phi$. If the projected edge length is negligible, the edge is treated through its vertices instead.

This one-dimensional optimization is exact for a linear edge and a sphere. It avoids iterative root finding.

## Ball-tool facet contact

Let the triangle plane be

$$
z=Ax+By+C.
$$

For a ball center above $(X,Y)$, tangency to the infinite plane occurs along the plane normal. The upward unit normal is proportional to $(-A,-B,1)$. Define

$$
g=\sqrt{1+A^2+B^2}.
$$

The contact point's planar coordinates are

$$
x_c=X+\frac{RA}{g},\qquad
y_c=Y+\frac{RB}{g}.
$$

The required ball-center height is

$$
Z_c=AX+BY+C+Rg.
$$

To see this, the signed distance from $(X,Y,Z_c)$ to the plane must equal $R$:

$$
\frac{Z_c-AX-BY-C}{\sqrt{1+A^2+B^2}}=R.
$$

The candidate is valid only if $(x_c,y_c)$ lies inside the projected triangle. The returned tip height is again $Z_c-R$.

## Complete ball evaluator

For each candidate triangle:

1. evaluate its three vertex contacts;
2. evaluate its three edge contacts;
3. evaluate the facet tangent contact when the projected facet is nondegenerate;
4. retain the greatest required center height;
5. after all triangles, subtract $R$.

Because the safe height is a maximum of necessary constraints, missing any feature can gouge. Testing all three feature classes is therefore essential.

### Pseudocode

```text
BALL_TRIANGLE_HEIGHT(X,Y,triangle,R)
    best <- -infinity
    for each vertex v
        if horizontal_distance(v,(X,Y)) < R
            best <- max(best, v.z + sqrt(R^2-d^2))
    for each edge e
        best <- max(best, exact_edge_ball_height(e,X,Y,R))
    if projected triangle is nondegenerate
        form z = A x + B y + C
        g <- sqrt(1+A^2+B^2)
        p <- (X + R A/g, Y + R B/g)
        if p is inside projected triangle
            best <- max(best, A X+B Y+C+R g)
    return best - R
```

## Flat-tool contact

A flat end mill occupies a vertical cylinder of radius $R$ whose bottom is the plane $z=Z$. The safe tip is the maximum triangle height over the intersection of the projected triangle with the disk.

The maximum of a linear plane over a convex clipped polygon occurs at a vertex of the clipped polygon. Such vertices arise from:

- original triangle vertices inside the disk;
- intersections of triangle edges with the disk boundary;
- in the special case of the disk entirely inside the triangle, the point on the circle in the direction of increasing plane height.

The implementation checks:

1. triangle vertices inside the disk;
2. each edge's interval inside the disk, choosing the endpoint with greater $z$;
3. the point on the disk boundary in the planar gradient direction $(A,B)$ when it lies in the triangle;
4. the disk center $(X,Y)$ when it lies in the triangle.

The center check covers a horizontal facet ($A=B=0$), where every point has the same height. The gradient-direction check covers a clipped circle maximum. Together with edge and vertex candidates, these characterize the maximum of the facet's linear height over the disk-triangle intersection.

![Flat-tool triangle contact candidates](../figures/flat_contact_decomposition.png){width=88%}

## Correctness by feature exhaustion

A concise correctness argument is:

- the feasible set for one triangle is compact;
- the objective is continuous, so a maximum exists;
- for the ball, an interior constrained stationary point gives facet contact; a boundary stationary point gives edge contact; boundary endpoints give vertex contact;
- for the flat tool, maximizing a linear function over the convex disk-triangle intersection occurs at an extreme point, which belongs to the enumerated feature set;
- the global safe height is the maximum over triangles because every triangle imposes an independent nonintersection constraint.

The test suite checks the evaluator against dense numerical optimization on representative triangles. Dense sampling is not a proof, but it is a valuable independent oracle for regression.

## Numerical considerations

- Comparisons near $d=R$ determine whether a square root is real. The implementation uses strict or tolerant inequalities to avoid negative radicands from rounding.
- Nearly vertical facets have small $n_z$ and unstable $A,B$. Their facet-interior candidate is skipped, while edges and vertices remain.
- Very short projected edges are skipped as edge features.
- The final maximum operation is numerically benign: overestimating a candidate leaves extra stock; underestimating can gouge.
- A production kernel would use filtered exact predicates for feature validity and carefully bounded arithmetic for contact heights.

## Exercises

1. Derive the edge stationary point $s^*$.
2. Verify the facet-center formula using signed point-to-plane distance.
3. Explain why the ball contact point shifts in the direction $(A,B)$ rather than $(-A,-B)$.
4. Prove that a linear function on a compact convex polygon achieves a maximum at a vertex.
5. Construct a case where checking only triangle vertices underestimates the required ball height.

# The Cutter-Location Field

## Why sample an exact evaluator?

The triangle evaluator answers one query accurately but some strategies need a coherent scalar field over a region. Waterline contours require repeated level-set extraction; slope classification requires gradients; distance-based paths require a metric field. Sampling amortizes expensive triangle queries and provides a regular data structure for numerical algorithms.

Let the rectangular domain be

$$
[x_0,x_1]\times[y_0,y_1].
$$

Given a requested grid spacing $g_s$, the repaired code chooses

$$
n_x=\max\left(4,\left\lceil\frac{x_1-x_0}{g_s}\right\rceil\right),
\qquad
n_y=\max\left(4,\left\lceil\frac{y_1-y_0}{g_s}\right\rceil\right),
$$

then defines exact cell dimensions

$$
h_x=\frac{x_1-x_0}{n_x},\qquad
h_y=\frac{y_1-y_0}{n_y}.
$$

Nodes are

$$
x_i=x_0+ih_x,
\qquad
y_j=y_0+jh_y.
$$

This distinction is subtle but essential. If one uses `ceil` for the count and still steps by the requested $g_s$, the last node overshoots the declared domain. Field bounds, contour coordinates, and interpolation then disagree.

## Bilinear interpolation

Within one cell, write normalized coordinates

$$
u=\frac{x-x_i}{h_x},\qquad v=\frac{y-y_j}{h_y},\qquad 0\le u,v\le1.
$$

For corner samples $f_{00},f_{10},f_{01},f_{11}$, the bilinear interpolant is

$$
\widetilde f(u,v)
=(1-u)(1-v)f_{00}
+u(1-v)f_{10}
+(1-u)vf_{01}
+uvf_{11}.
$$

Bilinear interpolation is linear along each cell edge but generally hyperbolic inside the cell. That interior structure is why ambiguous marching-squares cases need a bilinear decider rather than an average of corner values.

The repaired interpolation clamps to the exact node rectangle and handles a query on the last row or column by selecting the final cell with $u=1$ or $v=1$. It does not clamp to `nx - epsilon`, which would perturb exact boundary values.

## Gradient estimation

The code stores both components of the sampled gradient. At an interior node,

$$
F_x(i,j)\approx\frac{F_{i+1,j}-F_{i-1,j}}{2h_x},
$$

$$
F_y(i,j)\approx\frac{F_{i,j+1}-F_{i,j-1}}{2h_y}.
$$

At a boundary, the available one-sided span is used. The slope magnitude is

$$
G_{ij}=\sqrt{F_x(i,j)^2+F_y(i,j)^2}.
$$

Storing only $G$ is enough for steep/shallow classification but insufficient for the full metric. The matrix

$$
\mathbf G=\mathbf I+\nabla F\nabla F^T
$$

requires the direction of the gradient, not merely its magnitude.

## Sampling error

A grid field introduces several errors:

- **model discretization:** the STL approximates the intended CAD surface;
- **CL sampling:** the exact evaluator is sampled at finite spacing;
- **interpolation:** bilinear patches approximate the true CL surface between nodes;
- **gradient error:** finite differences amplify height errors and depend on cell size;
- **contour error:** marching squares approximates level sets inside each cell;
- **path lifting:** contour vertices may be reevaluated exactly, but their planar route came from the sampled field.

These errors are coupled. Refining only the final polyline cannot repair a contour that took the wrong topological branch on a coarse grid.

For a twice-differentiable scalar field, interpolation error is commonly $O(h^2)$ locally, while a first-derivative estimate is typically $O(h)$ or $O(h^2)$ depending on stencil and boundary position. Sharp CL ridges caused by changes in active contact feature are not twice differentiable, so smooth-error estimates do not apply there.

## Adaptive chordal refinement

A finishing path initially connects evaluated endpoints by a straight 3D segment. Let endpoints be $\mathbf p_0$ and $\mathbf p_1$. The linearly predicted height at parameter $t$ is

$$
z_L(t)=(1-t)z_0+tz_1.
$$

The exact CL height is

$$
z_F(t)=F((1-t)x_0+tx_1,(1-t)y_0+ty_1).
$$

A segment is subdivided if it is too long or if

$$
|z_F(t)-z_L(t)|>\tau
$$

at one of $t=1/4,1/2,3/4$. Checking only $t=1/2$ can miss an off-center peak or oscillation. The recursion stops at a maximum depth or a minimum segment length.

This is a sampling test, not a formal bound. A guaranteed bound would need curvature or Lipschitz information, interval arithmetic, or an adaptive evaluator with certified envelopes.

## Exact reevaluation of sampled contours

A marching-squares waterline is extracted from the interpolated grid at nominal level $z_0$. If its planar vertices are sent directly to the machine at $z_0$, the exact triangle evaluator may require a higher tip at some point. The repaired code therefore:

1. densifies the contour polyline;
2. evaluates the exact CL height at all dense points;
3. sets the entire waterline run to the maximum exact required height.

The result remains a true constant-$Z$ CNC contour and is safe at the sampled points. It may leave extra stock where the sampled grid underestimated the CL field. A fully adaptive contouring algorithm would refine the scalar field itself near the contour.

## Field visualization

![CL surface, slope, and metric paths](../figures/cl_surface_metric_paths.png){width=94%}

The figure distinguishes three objects that are often conflated:

- model height;
- cutter-location height after tool offset;
- distance or strategy fields computed on the CL surface.

Path planning should be explicit about which field it uses. A steep region of the model may be smoothed by a large ball tool; a CL ridge may arise even when the original mesh is smooth because the active contact feature changes.

## Exercises

1. Show that bilinear interpolation reproduces each of its four corner values exactly.
2. Give a bilinear function whose zero set is a hyperbola.
3. Explain why a central difference must divide by $2h$, not by $h$.
4. Construct a one-dimensional function whose midpoint lies on its chord but whose quarter point deviates strongly.
5. Identify which error sources are reduced by refining the STL and which are reduced by refining the CL grid.

# Z-Level Roughing

## Roughing as horizontal free-space slicing

At a roughing level $z_k$, the cutter may occupy horizontal positions where the allowance-adjusted CL surface satisfies

$$
F_a(x,y)\le z_k.
$$

For a raster direction, each row reduces this two-dimensional free-space set to one-dimensional intervals. The algorithm samples along the row, detects Boolean transitions, bisects them, and returns intervals $[a_0,a_1]$ that are safe at the current level.

The roughing levels are

$$
z_k=z_{\max}-k\,d_z,
$$

ending at the allowance-adjusted bottom. Here $d_z$ is the stepdown. This is a Z-level or waterline-style roughing scheme with raster clearing at each level.

## Conservative allowance field

The roughing field is generated using an inflated cutter and an added vertical allowance. Let $a$ be stock allowance. The implementation uses radius $R+a$ and then adds $a$ to the returned tip height. The condition

$$
F_a(x,y)\le z_k
$$

therefore excludes a larger neighborhood of the target than the finish cutter would require.

This method is easy to evaluate because it reuses the exact contact engine. It is not an exact offset surface in the differential-geometric sense. On a slope it tends to be conservative, which is appropriate for roughing but may increase remaining stock.

## Finding row intervals

Let $g(a)=F_a(W(a,b))-z_k$, where $W$ maps row coordinates $(a,b)$ into $(x,y)$ according to the chosen raster direction. Free space satisfies $g(a)\le0$.

The row scanner:

1. evaluates `free` at the row start;
2. advances in increments $\Delta a$;
3. whenever the Boolean state changes, performs a fixed number of bisections;
4. starts or closes an interval at the refined transition;
5. discards intervals shorter than a small threshold;
6. nudges endpoints into the verified free side.

The repaired sample interval is tied more tightly to cutter radius than the baseline. A narrow forbidden feature can still be missed if it lies entirely between samples. Exact interval construction would require intersecting the horizontal level with the full CL geometry or using an adaptive root-isolation process.

### Transition bisection

If $g(a_L)$ and $g(a_R)$ have opposite free/blocked states, bisection repeatedly sets

$$
a_M=\frac{a_L+a_R}{2}
$$

and replaces the endpoint whose state matches $g(a_M)$. After $m$ steps, the bracket width is reduced by $2^{-m}$.

## Connecting intervals across rows

Intervals on adjacent rows overlap if

$$
a_0^{(i)}\le a_1^{(j)}+\varepsilon
\quad\text{and}\quad
 a_1^{(i)}\ge a_0^{(j)}-\varepsilon.
$$

The algorithm treats each interval as a node and unions overlapping nodes on consecutive rows. A disjoint-set union structure maintains connected components with near-constant amortized operations. Each component is then machined as a local zigzag.

This connectivity step prevents the tool from repeatedly retracting between rows that belong to the same pocket. It is a sampled approximation to connected components of the planar free-space slice.

## Zigzag traversal

Within a component, intervals are grouped by row and ordered left-to-right or right-to-left on alternating rows. Alternating direction reduces non-cutting repositioning. When a component has multiple intervals on one row, their order follows the current row direction.

The current tool position is carried across intervals. A short link may remain at cutting depth if sampled points along the link satisfy

$$
F_a(x(t),y(t))\le z_k+\varepsilon.
$$

Otherwise the link rises to a locally estimated safe height, moves rapidly, and reenters.

## Entry strategy

At the first interval of a component, the tool must descend from a top height $z_{\mathrm{top}}$ to $z_k$. The available modes are:

- **helix:** circular motion with continuously decreasing $z$;
- **zigzag ramp:** repeated linear traversals along the first cut direction;
- **plunge:** vertical entry.

In `auto` mode, the algorithm tries helix, then ramp, then plunge.

### Helix geometry

For helix radius $r_h$ and ramp angle $\theta$, the vertical descent per radian is

$$
p=r_h\tan\theta.
$$

At angular parameter $\phi$,

$$
\begin{aligned}
x(\phi)&=c_x-r_h\cos\phi\,u_x+r_h\sin\phi\,n_x,\\
y(\phi)&=c_y-r_h\cos\phi\,u_y+r_h\sin\phi\,n_y,\\
z(\phi)&=\max(z_k,z_{\mathrm{top}}-p\phi),
\end{aligned}
$$

where $\mathbf u$ is the interval direction and $\mathbf n$ its in-plane normal. After reaching depth, the path completes the current revolution at constant $z$ to flatten the entry floor.

### Ramp geometry

For ramp length $L_r$, one traversal drops

$$
\Delta z=L_r\tan\theta.
$$

The tool alternates between the near and far endpoints until it reaches depth.

## Full-path validation

The baseline validated only a small set of points on one helix orbit. The repaired implementation validates every generated path segment against the allowance field. A line segment from $\mathbf p_0$ to $\mathbf p_1$ is sampled at a spacing related to tool radius, and every sample must satisfy

$$
z(t)\ge F_a(x(t),y(t))-\varepsilon.
$$

If a helix fails, the ramp is constructed and checked; if the ramp fails, the code emits a plunge. A plunge itself is not proven safe against uncut stock by this rule; it is the last-resort behavior and should be enabled only when the process allows vertical entry at the chosen start.

![Helix, ramp, and plunge entry paths](../figures/entry_paths.png){width=92%}

## Roughing limitations

- The free-space slice is sampled, not exact.
- The stock model is implicit; rest material from earlier rows is not used to adapt later paths.
- There is no pocket boundary offset independent of the CL field.
- Entry checks ignore holder and flute-length limits.
- Stay-down links are sampled and may miss narrow obstacles.
- A full-width raster may air-cut large free regions.
- There is no trochoidal load control or engagement-angle model.

The method is nevertheless valuable as a compact demonstration of how CL evaluation, one-dimensional root finding, connected components, and path linking form a complete roughing pipeline.

## Exercises

1. Prove the interval-overlap test used by the union-find stage.
2. Derive the descent per helix revolution.
3. For a 3-degree ramp and a 10 mm traverse, compute the vertical drop.
4. Explain why endpoint nudging should move into the free region rather than onto the estimated boundary.
5. Propose an adaptive scanner that cannot miss a blocked interval wider than a prescribed tolerance.

# Raster Finishing

## Raster as the coverage baseline

Raster finishing samples the CL surface on parallel rows. It is conceptually simple, predictable, and provides a useful coverage baseline. Let the cross-feed span be $B=b_{\max}-b_{\min}$ and nominal spacing $s_0$. The code chooses

$$
n=\max\left(1,\left\lceil\frac{B}{s_0}\right\rceil\right),
\qquad
s=\frac{B}{n}.
$$

The actual spacing $s$ exactly partitions the span and is no greater than $s_0$.

Rows alternate direction, forming a boustrophedon or zigzag path. The end of one row is connected to the start of the next by a cross-feed segment lifted onto the CL surface.

![Raster finishing path](../figures/paths_raster.png){width=92%}

## Nominal spacing for a ball tool

Given requested scallop $h$ and ball radius $R$, the code uses the flat-plane formula

$$
s_0=2\sqrt{2Rh-h^2}.
$$

It clamps the result to numerical and tool-relative limits. This spacing is exact only for adjacent parallel passes on a flat surface and a ball tool. It is a sensible nominal parameter for raster finishing, not a global error guarantee.

For a flat tool, spacing is chosen as a percentage of diameter:

$$
s_0=D\frac{p}{100}.
$$

A perfectly flat end mill on a smooth sculptured surface can still leave cusp error because the cutter contacts at edges and facets; percentage stepover is a process parameter rather than a geometric scallop formula.

## Adaptive row sampling

Each row begins with exact endpoint evaluations. Recursive refinement subdivides a segment if:

- its planar length exceeds a nominal maximum;
- the exact CL field at quarter, midpoint, or three-quarter differs from linear interpolation by more than the chord tolerance.

The resulting polyline approximates the lifted curve

$$
\widehat\gamma(a)=\bigl(W(a,b),F(W(a,b))\bigr).
$$

The same procedure refines the cross-feed connection between rows. This matters because the CL surface may rise sharply between adjacent row endpoints.

## The first move and continuous stream

The plain raster is stored as one large point stream:

1. rapid to the first point at clearance;
2. plunge to the first CL height;
3. one continuous cut through all row and cross-feed points;
4. rapid to clearance after finishing.

This representation minimizes move-object overhead and makes time accounting straightforward. It also means arc fitting sees long runs with changing constant axes; the compressor partitions them by interpolation plane before fitting.

## Coverage versus finish quality

Raster covers the rectangular machining domain, but coverage alone does not imply good finish:

- on steep walls, a horizontal stepover corresponds to a large surface distance;
- path direction can align poorly with principal curvature;
- cross-feed links may leave marks;
- a rectangular margin can cause air cutting;
- a fixed spacing chosen from flat geometry can violate scallop targets on curved surfaces.

The hybrid and metric strategies address some of these weaknesses while keeping raster as a reference.

## Error sources in a raster pass

A useful error decomposition is

$$
e_{\mathrm{total}}
\lesssim e_{\mathrm{mesh}}+e_{\mathrm{contact}}+e_{\mathrm{stepover}}+e_{\mathrm{chord}}+e_{\mathrm{arc}}+e_{\mathrm{controller}}.
$$

Here:

- $e_{\mathrm{mesh}}$ is the STL approximation error;
- $e_{\mathrm{contact}}$ is numerical evaluator error;
- $e_{\mathrm{stepover}}$ is residual scallop between passes;
- $e_{\mathrm{chord}}$ is polyline approximation error along a pass;
- $e_{\mathrm{arc}}$ is optional arc-fitting error;
- $e_{\mathrm{controller}}$ includes interpolation, rounding, and machine response.

The terms are not strictly additive or independent, but the decomposition prevents a common mistake: setting chord tolerance to a small number does not control between-pass scallop.

## Exercises

1. Show that $s=B/\lceil B/s_0\rceil\le s_0$.
2. Compute the number of passes for a 24 mm span with $s_0=1.12$ mm.
3. Explain why the cross-feed link must be refined against the CL surface.
4. Compare errors controlled by scallop height and chord tolerance.
5. Suggest a way to trim raster rows to the projected part mask while preserving a coverage proof.

# Marching Squares and Contour Topology

## The contour-extraction problem

Given scalar samples $A_{ij}$ and a level $\ell$, marching squares approximates

$$
A(x,y)=\ell
$$

inside each rectangular cell. Each corner is classified by the sign of $A_{ij}-\ell$, producing a four-bit case index from 0 to 15. Cases 0 and 15 contain no crossing. Most other cases contain one segment; checkerboard cases 5 and 10 contain two possible pairings.

Marching squares is the two-dimensional analogue of marching cubes [@lorensen1987]. The same local simplicity that makes it fast also makes its ambiguity rule important.

## Edge interpolation

Along an edge with signed endpoint values $v_a$ and $v_b$, the linear zero occurs at

$$
t=\frac{v_a}{v_a-v_b}.
$$

The repaired code computes an edge point only when the case table actually needs that edge. This avoids evaluating the formula on equal-sign or equal-valued endpoints that do not cross. When the denominator is extremely small, it uses the midpoint as a stable fallback and clamps $t$ to $[0,1]$.

## Ambiguous cases and the asymptotic decider

Consider a bilinear cell with signed corners

$$
f_{00},f_{10},f_{11},f_{01}.
$$

In cases 5 and 10, opposite corners have the same sign. An arithmetic center average does not generally determine the topology of the bilinear zero set. The asymptotic decider uses

$$
Q=f_{00}f_{11}-f_{10}f_{01}.
$$

The sign of $Q$ chooses which pair of corners is connected through the positive region. This criterion follows from the bilinear interpolant's saddle structure and is the two-dimensional form of the ambiguity resolution introduced for marching methods [@nielson1991].

![Marching-squares ambiguity and bilinear decider](../figures/marching_squares_asymptotic_decider.png){width=90%}

When $Q$ is numerically zero, the code uses the corner sum as a deterministic tie-breaker. An exact topological implementation would define a symbolic convention for equality and consistently handle level values exactly at grid vertices.

## Segment chaining

Marching produces independent segments. A CAM contour needs ordered polylines. The algorithm quantizes each segment endpoint to a key

$$
k(x,y)=\left(\operatorname{round}\frac{x}{\delta},
\operatorname{round}\frac{y}{\delta}\right),
$$

where $\delta$ is relative to cell size. It stores a map from endpoint key to incident segment ends. Starting from an unused segment, it extends forward and backward until no unused incident segment remains.

A polyline is marked closed when its first and last endpoint keys agree. Quantization absorbs roundoff from independent edge interpolation. Too large a tolerance can merge nearby contours; too small a tolerance can leave a loop open. Scaling it with $h_x,h_y$ is more defensible than a fixed world-coordinate multiplier.

## Branches and degeneracies

For a generic level of a bilinear field, each edge intersection has degree two in the contour graph. Degenerate cases can produce:

- a contour through a grid vertex;
- a whole edge at the level;
- multiple coincident segment endpoints;
- a saddle exactly at the level.

The compact implementation does not build a full planar arrangement for these cases. It uses strict `>0` classification and deterministic tie-breaking. Production contouring should document a consistent ownership rule for zero-valued corners and may perturb the level symbolically.

## Splitting a contour by a mask

Hybrid machining may retain only contour vertices satisfying a predicate, such as `steep(x,y)`. For an open polyline, splitting is a linear scan. A closed loop is cyclic: the stored first vertex is an arbitrary seam. If a kept run crosses that seam, a naive scan returns two partial runs or loses one.

The repaired algorithm finds one rejected vertex, begins scanning just after it, and wraps exactly once around the loop. The seam is therefore placed in a rejected region, so every kept connected run is emitted once. If every vertex is kept, the original closed loop is preserved.

This small change fixed a concrete baseline probe in which a closed seam run was truncated.

## Waterline ordering

At each height, the code extracts all contours, optionally masks them, and orders runs greedily by distance from the current tool position. An open run may be reversed to reduce the link. A closed loop chooses a start vertex nearest the cursor.

Nearest-first ordering is a heuristic for a traveling-salesperson-like problem. It is fast and often effective, but it can be suboptimal. A production system may group nested contours, respect climb/conventional direction, avoid trapping stock islands, and optimize links globally.

## Exercises

1. Derive the edge interpolation formula.
2. Evaluate $Q$ for the two examples in the ambiguity figure and predict the pairing.
3. Explain why an endpoint key should be based on cell scale.
4. Construct a closed-loop mask pattern that fails under a naive linear scan.
5. Describe a symbolic rule for a contour passing exactly through a grid vertex.

# Hybrid Finishing: Raster Plus Waterlines

## Motivation

A single finishing direction behaves differently across a sculptured surface. On shallow regions, a raster pass gives smooth, predictable coverage. On steep regions, adjacent raster rows can be far apart in surface distance and may produce pronounced cusps or striping. Constant-$Z$ waterlines naturally follow steep walls and keep the cutter at one machine height.

A hybrid strategy therefore combines:

- raster paths for general or shallow coverage;
- waterline contours for steep regions.

The algorithm classifies steepness using the CL-field slope

$$
\|\nabla F\|\gtrless\tan\theta_s,
$$

where $\theta_s$ is a user angle.

## Why a nominal partition failed

The baseline attempted to define two overlapping predicates:

$$
\text{shallow}:\quad \|\nabla F\|\le1.15\tan\theta_s,
$$

$$
\text{steep}:\quad \|\nabla F\|\ge0.85\tan\theta_s.
$$

The overlap was intended to prevent a visible seam. Yet the actual paths were not the continuous sets described by these inequalities:

- shallow intervals were found by discrete samples along raster rows;
- waterlines existed only at discrete $z$ levels;
- waterline vertices were split by sampled steepness;
- short intervals and runs were discarded;
- contouring occurred on a finite CL grid.

Therefore the union of generated paths did not inherit a coverage theorem from the union of the two predicates. The baseline probe produced large sampled areas outside its tolerance band.

This illustrates a general algorithm-design principle:

> A classification cover is not automatically a machining cover. One must prove that the *discrete path families* cover the domain under their sampling and pruning rules.

## Coverage-first repair

The repaired hybrid uses full raster finishing as the coverage guarantee, then adds waterline passes where the CL field is steep. The invariant is immediate:

- deleting all waterlines recovers the complete raster strategy;
- waterlines can improve steep-wall sampling but cannot create a coverage hole.

![Coverage-first hybrid path](../figures/paths_hybrid.png){width=92%}

The cost is redundancy. Some regions are machined twice, path length increases, and surface marks from crossing path families may interact. The benchmark reflects this tradeoff: hybrid has a lower sampled RMS deviation than raster but a longer path and higher estimated time.

## Selecting waterline levels

Let $F_{\max}$ be the maximum sampled CL height. The top waterline is placed slightly below the top to avoid a degenerate contour at an isolated maximum. Subsequent levels are separated by the nominal spacing $s_0$:

$$
z_k=z_{\mathrm{top}}-ks_0.
$$

This uses the same numerical distance for horizontal and vertical pass spacing. It is a pragmatic choice, not a constant-scallop derivation. On a steep planar wall of angle $\alpha$, a vertical height increment $\Delta z$ corresponds to surface-normal spacing dependent on $\alpha$.

A more principled waterline step could derive from local normal curvature and tool radius, or adapt to a cusp estimate along the contour family.

## Steep-mask hysteresis

Although raster now guarantees coverage, the waterline mask still uses a transition band. One may define

$$
\text{waterline eligible}:\quad \|\nabla F\|\ge c\tan\theta_s
$$

with $c<1$ to extend contours slightly into the transition. This reduces abrupt starts and stops but increases overlap. Because contour vertices are sampled, a robust implementation should interpolate the exact mask boundary along contour segments rather than simply retaining or dropping vertices.

The current `splitByMask` acts on contour vertices. It can produce a small positional bias at mask transitions. The bias is usually less important than the coverage defect it replaced, but it is documented.

## Constant-$Z$ safety adjustment

A waterline extracted from the sampled field at level $z_k$ is not guaranteed to be safe against the exact triangle evaluator. The repaired path is densified and lifted to

$$
z_{\mathrm{safe}}=\max_i F(x_i,y_i)
$$

for its dense samples. Every point in the CNC run is then emitted at this one height. This preserves G17 arc-fitting eligibility and controller simplicity.

The price is local air cutting: if one sample needs a higher $z$, the entire contour is raised. An alternative is a nonconstant-$Z$ contour lifted exactly to the CL surface, but it is no longer a waterline and would use G18/G19 or 3D linear interpolation.

## Path-family interaction

Combining raster and waterline passes raises practical questions beyond geometry:

- Which family runs first?
- Should raster links cross already finished waterlines?
- Should waterlines use climb direction consistently?
- How much overlap is needed at the transition?
- Can one family erase marks left by the other?
- Does the tool deflect differently on steep walls?

The reference implementation runs raster spans before waterlines and uses nearest-first contour ordering. It does not model cutting force or surface texture. A production hybrid usually treats strategy partitioning, overlap, and direction as first-class process-planning decisions.

## A path toward a nonredundant hybrid

A safer nonredundant design would:

1. construct a continuous steepness field with bounded interpolation error;
2. define an overlap strip $\Omega_o$ around the threshold;
3. trim raster passes to $\Omega_{\mathrm{shallow}}\cup\Omega_o$ using interval intersections with interpolated mask boundaries;
4. trim waterlines to $\Omega_{\mathrm{steep}}\cup\Omega_o$;
5. prove that the two trimmed domains cover the projected part;
6. verify that pruning short runs cannot open a hole larger than tolerance;
7. add boundary-following transition passes where needed;
8. validate coverage independently on an adaptive grid.

The repaired implementation intentionally chooses the simpler coverage-first invariant rather than claiming this proof.

## Exercises

1. Explain why overlapping steep/shallow predicates do not prove discrete path coverage.
2. For a planar wall $z=mx$, relate a vertical waterline step $\Delta z$ to the surface distance between contours.
3. Propose a criterion for choosing the overlap-strip width.
4. Compare the likely surface texture of raster-only and raster-plus-waterline finishing.
5. Design a verification test that specifically detects a hybrid transition hole.

# Approximate Constant-Spacing and Constant-Scallop Paths

## Three different goals

The phrases *constant stepover*, *constant surface spacing*, and *constant scallop height* describe different constraints.

1. **Constant planar stepover:** adjacent projected paths are separated by a fixed distance in the $xy$ plane.
2. **Constant surface spacing:** adjacent paths are separated by a fixed geodesic distance measured on a surface, here the CL surface.
3. **Constant scallop height:** the residual material height produced by the actual cutter and surface geometry is constant.

The first is easy, the second is a metric problem, and the third is a cutter/surface envelope problem involving local curvature and pass direction. Constant surface spacing is often a useful approximation to constant scallop, but they are not identical [@feng2002; @kim2007].

## Distance-field construction

Suppose a scalar field $T(x,y)$ measures distance from a seed curve, such as the rectangular domain boundary. If the levels

$$
T=k,\qquad k=1,2,3,\ldots
$$

are extracted, neighboring contours are approximately one distance unit apart. By scaling edge weights or the Eikonal right-hand side with a requested spacing $s_0$, unit level increments correspond to about $s_0$ millimetres.

The implementation supplies two methods:

- `slope-eikonal`: a legacy scalar approximation solved by fast sweeping;
- `surface-graph`: multi-source Dijkstra on the sampled CL surface, recommended in this reference.

## The scalar slope-Eikonal approximation

The legacy method solves

$$
\|\nabla T\|=\frac{\sqrt{1+\|\nabla F\|^2}}{s_0}
$$

with $T=0$ on the domain boundary. Its intuition is that a planar displacement should be reduced where the surface stretches. If the path from the boundary follows the gradient direction of $F$, then a planar step $d\ell$ lifts to surface length

$$
ds=\sqrt{1+\|\nabla F\|^2}\,d\ell,
$$

so the equation is appropriate along that direction.

But the full metric gives

$$
ds^2=d\mathbf x^T(\mathbf I+\nabla F\nabla F^T)d\mathbf x.
$$

The stretch depends on the angle between $d\mathbf x$ and $\nabla F$. Along a level set, the stretch is one, not $\sqrt{1+\|\nabla F\|^2}$. Therefore the scalar right-hand side defines an isotropic refractive index, not the true anisotropic surface metric.

The method remains useful as a computational comparison and often produces visually plausible contours. It is now labelled `slope-eikonal` rather than presented as exact constant scallop.

![Legacy scalar slope-Eikonal field](../figures/metric_slope_eikonal.png){width=88%}

## The isotropic Eikonal equation

The Eikonal equation

$$
\|\nabla T\|=f(x,y),\qquad f\ge0,
$$

models an arrival time whose local propagation speed is $1/f$. For constant $f=1$, $T$ is Euclidean distance from the seed set. Fast marching and fast sweeping are standard numerical approaches [@sethian1996; @sethian1999; @zhao2005].

The repaired solver accepts rectangular cells $h_x\ne h_y$. Let

$$
a=\min(T_{i-1,j},T_{i+1,j}),\qquad
b=\min(T_{i,j-1},T_{i,j+1}).
$$

The first-order upwind discretization is

$$
\left(\frac{T-a}{h_x}\right)^2+
\left(\frac{T-b}{h_y}\right)^2=f_{ij}^2,
$$

provided the solution is no smaller than both accepted neighbors. Expanding gives

$$
AT^2+BT+C=0,
$$

where

$$
A=\frac1{h_x^2}+\frac1{h_y^2},
$$

$$
B=-2\left(\frac{a}{h_x^2}+\frac{b}{h_y^2}\right),
$$

$$
C=\frac{a^2}{h_x^2}+\frac{b^2}{h_y^2}-f_{ij}^2.
$$

The larger root is considered if it is at least $\max(a,b)$. Otherwise a one-sided update is used:

$$
T=\min(a+f h_x,b+f h_y).
$$

## Fast sweeping

Fast sweeping repeatedly visits the grid in all combinations of coordinate directions:

1. $i$ increasing, $j$ increasing;
2. $i$ decreasing, $j$ increasing;
3. $i$ increasing, $j$ decreasing;
4. $i$ decreasing, $j$ decreasing.

Characteristics entering from different quadrants are propagated efficiently by different sweep orders. The baseline ran exactly four cycles. The repaired solver repeats cycles until the maximum update is below a tolerance or a maximum cycle count is reached. It also supports explicit seed masks and optional boundary seeding.

For a rectangle with boundary value zero and $f=1$, the exact solution is distance to the nearest rectangle side. This analytic case is included in the test suite.

## Surface-graph distance

The recommended method treats CL samples as vertices of a graph embedded in 3D:

$$
\mathbf p_{ij}=(x_i,y_j,F_{ij}).
$$

Each node connects to its four axial and four diagonal neighbors. An edge from $p$ to $q$ has weight

$$
w_{pq}=\frac{\|\mathbf p_q-\mathbf p_p\|_2}{s_0}
=\frac{\sqrt{(\Delta x)^2+(\Delta y)^2+(\Delta F)^2}}{s_0}.
$$

All boundary nodes are inserted into a priority queue with distance zero. Multi-source Dijkstra computes

$$
D(q)=\min_{\pi:\partial\Omega\leadsto q}\sum_{(p,r)\in\pi}w_{pr}.
$$

Level sets $D=k$ are then approximately $k s_0$ surface-distance units from the boundary.

![Surface-graph distance field](../figures/metric_surface_graph.png){width=88%}

This approach directly uses 3D edge lengths and therefore captures directional slope anisotropy better than the scalar equation. On a planar surface, an edge parallel to level contours has no $\Delta F$ penalty, while an edge uphill is longer.

## Relation to the continuous metric

For a small grid edge $d\mathbf x=(\Delta x,\Delta y)$,

$$
\Delta F\approx\nabla F\cdot d\mathbf x.
$$

Hence

$$
w^2s_0^2
\approx \|d\mathbf x\|^2+(\nabla F\cdot d\mathbf x)^2
=d\mathbf x^T\mathbf G\,d\mathbf x.
$$

Thus the graph edge weight is a discrete approximation to length under the first fundamental form. Dijkstra then approximates geodesic distance using paths restricted to graph edges.

The restriction causes grid anisotropy. With only four neighbors, paths prefer axes strongly. Eight neighbors reduce but do not eliminate the effect. More directions, triangular grids, ordered upwind methods, fast marching on triangulated surfaces, or the heat method can improve rotational behavior [@crane2013heat].

## Boundary-parallel contours

Both methods seed the rectangular outer boundary. Their level sets propagate inward and form nested contours. This choice is convenient but arbitrary. Other seed sets can generate different path families:

- a selected boundary curve;
- one or more feature curves;
- a point or set of points;
- a waterline contour;
- a medial axis or pocket boundary.

A true machining strategy should choose seeds based on part topology, accessibility, desired direction, and link behavior rather than merely the bounding rectangle.

## Lifting distance contours onto the CL surface

Marching squares extracts planar polylines from $D$. Each vertex $(x,y)$ is lifted using the exact evaluator:

$$
\widehat{\mathbf p}=(x,y,F(x,y)).
$$

Unlike waterlines, these paths are not constant $z$. They follow the CL surface and are exported as 3D linear moves unless portions happen to lie in a supported constant-axis plane and pass arc fitting.

![Approximate surface-metric iso-spacing paths](../figures/paths_surface-graph.png){width=92%}

## Why this is still not exact scallop

Scallop is determined by the envelope of two neighboring swept cutter surfaces. In a normal section, it depends on:

- cutter radius and local cutter profile;
- normal curvature of the target or CL surface;
- path tangent and cross-feed direction;
- changes in active cutter contact feature;
- finite spacing, not only differential distance.

Kim formulates constant cusp-height paths as geodesic parallels under a specially constructed abstract Riemannian metric [@kim2007]. The simple CL first fundamental form used here measures ordinary surface distance, not that cutter-aware scallop metric. Therefore the implementation uses the descriptive phrase **approximate constant surface spacing** and reports dexel verification rather than asserting a theorem it does not satisfy.

## Comparison of the two fields

![Difference between scalar and surface-graph metric fields](../figures/metric_field_difference.png){width=94%}

The difference image is not merely numerical noise. It reflects different geometric models:

- scalar Eikonal: direction-independent local cost based on slope magnitude;
- graph metric: direction-dependent cost approximated through 3D chords.

On coarse grids, each also has distinct discretization artifacts. The benchmark includes both so future changes can be compared against a retained legacy behavior.

## Exercises

1. On the plane $F(x,y)=mx$, compute graph edge weights in the $x$ and $y$ directions.
2. Derive the anisotropic quadratic update for $h_x\ne h_y$.
3. Explain why the larger quadratic root is selected.
4. Show that Dijkstra with all boundary vertices seeded computes the shortest graph distance to the boundary set.
5. Give two reasons equal surface spacing may fail to produce equal scallop height.
6. Propose a graph with more directions than the eight-neighbor grid and discuss its cost.

# Linking, Ordering, and Safe Motion

## Cutting paths versus machine motion

A path generator often focuses on contact curves and treats links as an afterthought. In practice, non-cutting motion can dominate cycle time and create collisions. The repaired job representation distinguishes:

- `rapid`: non-cutting positioning;
- `plunge`: vertical or entry feed;
- `ramp`: helix or zigzag entry feed;
- `cut`: roughing or finishing feed.

Every move stores a sequence of target points. The machine starts a move at the final point of the previous move; the first stored point may therefore be reached by a segment not explicitly duplicated in the array. This compact convention caused the original arc-start defect when a later algorithm forgot the incoming state.

## Riding the CL surface

For two nearby finishing endpoints $\mathbf p$ and $\mathbf q$, the code may link them by a cut refined against the exact CL surface. The link is not the straight 3D chord; it is recursively sampled and lifted so the cutter remains on or above $F$.

This stay-down link is attempted only when the planar distance is below a multiple of the pass spacing. The threshold is a heuristic. A short link can still cross a sharp ridge, which is why geometric validation matters more than distance alone.

## Retract links

For a longer link, the algorithm samples the straight planar route to estimate

$$
h_{\max}=\max_t F((1-t)\mathbf p_{xy}+t\mathbf q_{xy}).
$$

It then uses a local retract height

$$
z_L=\min(z_{\mathrm{clear}},h_{\max}+\delta),
$$

rapids horizontally at $z_L$, and plunges at the destination. This can be much shorter than returning to global clearance after every contour.

Again the maximum is sampled. A certified collision-free link would need conservative bounds or exact swept-volume tests, including the holder.

## Greedy contour ordering

For a set of open or closed contour runs, the code repeatedly selects the run endpoint nearest the current cursor. Open runs may be reversed. Closed runs are rotated to begin at the nearest stored vertex.

The heuristic is approximately

```text
while unvisited runs remain
    choose the admissible start/end with minimum Euclidean distance
    orient or rotate that run accordingly
    append it
```

This is $O(m^2n)$ in a simple implementation with $m$ runs and average $n$ vertices examined for closed-loop starts. For modest CAM contours it is acceptable. Spatial indexing of endpoints or a routing optimizer would improve large jobs.

## Directional process constraints

Nearest-first ignores:

- climb versus conventional milling;
- inside-before-outside or outside-before-inside rules;
- stock trapping and island stability;
- preferred entry side;
- surface grain direction;
- machine rotary or travel constraints;
- thermal and force balancing.

A production path planner should express these as constraints before optimizing link distance. The shortest route is not necessarily the safest or best-cutting route.

## Clearance hierarchy

It is useful to distinguish:

1. **contact height:** exact cutter tip on the CL surface;
2. **local link height:** sampled maximum CL plus a small margin;
3. **entry top:** current level plus stepdown and entry margin;
4. **global clearance:** part maximum plus user clearance;
5. **machine safe plane:** a setup-specific height above stock, clamps, and fixtures.

The reference core models the first four. The fifth belongs in a machine setup and postprocessor.

## Time estimate

The job flattener accumulates Euclidean segment length and divides by nominal speed. Rapid uses a fixed reference speed; plunge and ramp use reduced fractions of feed. If segment $i$ has length $L_i$ and assigned speed $v_i$, then

$$
t_{\mathrm{est}}=\sum_i\frac{L_i}{v_i}.
$$

This ignores acceleration, jerk, corner blending, look-ahead, spindle ramp, tool changes, and controller-specific arc execution. It is useful for relative comparisons, not quoting production cycle time.

## Exercises

1. Explain why a move array may legally omit its incoming start point.
2. Construct a short planar link that crosses a high narrow CL ridge.
3. Give an example where nearest-first contour ordering violates a machining constraint.
4. Extend the time estimate to include trapezoidal acceleration on a line segment.
5. Propose a data structure for finding the nearest unvisited contour endpoint efficiently.

# Arc Fitting and Polyline Compression

## Why fit arcs?

A finely sampled CL path may contain hundreds of nearly circular points. CNC controls can execute planar arcs using G2/G3, reducing program size and sometimes producing smoother controller interpolation. Arc fitting is therefore a lossy compression problem under a geometric tolerance.

The implementation supports arcs in the three principal planes:

- G17: $XY$, constant $z$;
- G18: $XZ$, constant $y$;
- G19: $YZ$, constant $x$.

A general 3D curve whose all three coordinates vary cannot be represented by one standard planar G2/G3 block.

## Partitioning by constant axis

For each consecutive polyline segment, the compressor determines whether one coordinate is constant within a small tolerance:

- $|\Delta y|\approx0$ and $|\Delta x|>0$: G18 candidate;
- $|\Delta x|\approx0$ and $|\Delta y|>0$: G19 candidate;
- $|\Delta z|\approx0$: G17 candidate.

Consecutive segments with the same constant axis form a run. Runs shorter than a minimum point count remain lines. Longer runs are passed to the circle fitter.

This segmentation is intentionally conservative. A nearly planar 3D run with small variation in its nominally constant axis is not projected and fitted; it stays linear.

## Algebraic circle fit

In plane coordinates $(u,v)$, a circle satisfies

$$
(u-u_c)^2+(v-v_c)^2=r^2.
$$

Expanding,

$$
u^2+v^2+Au+Bv+C=0,
$$

where

$$
u_c=-\frac A2,\qquad v_c=-\frac B2.
$$

For sampled points $(u_k,v_k)$, the code accumulates sums and solves the normal equations for $A,B,C$. To improve conditioning, coordinates are translated by the first run point before forming powers.

Algebraic least squares minimizes residual in the implicit equation, not geometric radial distance. The implementation subsequently validates actual radial error, so the algebraic fit serves only as a fast candidate generator.

## Endpoint-consistent center

A least-squares circle center need not be equidistant from the selected arc endpoints. The code projects the fitted center onto the perpendicular bisector of the endpoint chord. Let endpoint-relative vectors be $\mathbf a$, $\mathbf b$, midpoint $\mathbf m=(\mathbf a+\mathbf b)/2$, and unit chord direction $\mathbf e$. If the fitted center is $\mathbf c$, remove its chord-parallel offset:

$$
\mathbf c' = \mathbf c - [ (\mathbf c-\mathbf m)\cdot\mathbf e]\mathbf e.
$$

Then $\|\mathbf a-\mathbf c'\|=\|\mathbf b-\mathbf c'\|$ up to rounding, making the center compatible with a single CNC arc from start to end.

## Acceptance tests

A candidate arc is accepted only when:

1. the normal-equation determinant is sufficiently nonzero;
2. radius lies within practical bounds;
3. every sample's radial deviation is at most the arc tolerance $\tau_a$;
4. angular increments have one consistent sign;
5. total sweep is below about 2.9 radians;
6. enough segments are replaced to justify an arc.

The sweep restriction avoids long arcs and branch ambiguity. Full circles are not emitted.

A greedy extender adds points until fits fail. It remembers the longest recent valid prefix and tolerates a few misses before stopping, then emits either that arc or one line segment.

## The missing incoming segment defect

A `cut` move often stores only destinations after the current tool position. Suppose the machine is at $\mathbf p_0$, while the move array begins with $\mathbf p_1,\mathbf p_2,\ldots$. The intended polyline contains

$$
\mathbf p_0\to\mathbf p_1\to\mathbf p_2\to\cdots.
$$

The baseline compressor treated $\mathbf p_1$ as point zero and generated operations from index one onward. The first emitted operation therefore ended at $\mathbf p_2$, deleting $\mathbf p_0\to\mathbf p_1$ and, depending on indexing, also failing to emit the correct first destination.

The repaired algorithm builds a separate stream

$$
P_{\mathrm{arc}}=[\mathbf p_0,\mathbf p_1,\mathbf p_2,\ldots]
$$

before fitting. The compact original array remains unchanged for other consumers. The baseline probe found 23 affected arc-fitted moves; the repaired probe found zero.

![Arc-start integration defect](../figures/arc_start_omission.png){width=90%}

This defect demonstrates why stateful geometry transforms must make their input state explicit. A pure `compress(polyline)` function cannot reconstruct a missing start point unless the caller supplies it.

## Direction and plane orientation

The sign of angular change is computed in each local $(u,v)$ coordinate frame. CNC G2/G3 direction, however, is defined as viewed from the positive axis normal to the selected plane. The mappings are:

- G17 uses $(u,v)=(x,y)$, viewed from $+z$;
- G18 uses $(u,v)=(x,z)$, viewed from $+y$, whose screen orientation reverses one intuitive convention;
- G19 uses $(u,v)=(y,z)$, viewed from $+x$.

The repaired mapping was tested with known arcs in G18 and G19. Plane conventions must still be confirmed against the target controller.

![CNC interpolation planes and arc direction](../figures/gcode_arc_planes.png){width=88%}

## Verification of fitted arcs

A verifier that simulates only the pre-fit polyline does not verify the exported program. The repaired dexel simulator reconstructs points on each fitted arc. If the center is $(u_c,v_c)$, start angle $\theta_0$, and signed sweep $\Delta\theta$, then

$$
\begin{aligned}
u(t)&=u_c+r\cos(\theta_0+t\Delta\theta),\\
v(t)&=v_c+r\sin(\theta_0+t\Delta\theta),\qquad 0\le t\le1.
\end{aligned}
$$

Samples are spaced according to arc length relative to the dexel cell size. The constant coordinate is restored according to G17, G18, or G19.

## Exercises

1. Derive the expanded implicit circle equation.
2. Prove that projecting a point onto the perpendicular bisector makes its distances to the chord endpoints equal.
3. Explain why radial error must be tested after an algebraic fit.
4. Work out the G2/G3 mapping for a quarter circle in each principal plane.
5. Design a property test that ensures arc fitting never changes the first segment of a move.

# G-Code Export and Modal Semantics

## A postprocessor is part of the algorithm

Geometry is not complete until it is encoded in a controller dialect. G-code is modal: omitted words inherit previous states, and the same coordinates can mean different motions under different plane, distance, or arc-center modes. A postprocessor must therefore establish the states on which it depends.

The reference exporter begins with:

```text
G21 G90 G94 G17 G91.1
```

meaning:

- millimetres;
- absolute endpoint coordinates;
- feed per minute;
- $XY$ interpolation plane;
- incremental I/J/K arc-center offsets.

It then starts the spindle, moves to clearance, and emits move blocks.

## Linear and rapid moves

Rapid destinations use G0 with explicit $X,Y,Z$. Cutting, plunge, and ramp points use G1. The exporter changes feed only when needed:

- nominal cutting feed $F$;
- plunge feed $\max(30,F/3)$;
- ramp feed $\max(30,F/2)$.

These ratios are placeholders. Real feeds depend on tool, material, engagement, spindle speed, machine rigidity, and process planning.

## Arc centers

With incremental center mode, I/J/K are offsets from the arc start:

- G17: $I=u_c-x_s$, $J=v_c-y_s$;
- G18: $I=u_c-x_s$, $K=v_c-z_s$;
- G19: $J=u_c-y_s$, $K=v_c-z_s$.

The current position must therefore be correct at every arc. The missing incoming segment bug was especially dangerous because it corrupted both path coverage and the reference from which center offsets were computed.

## Plane changes

Before an arc, the exporter selects G17, G18, or G19. After an arc-fitted cut move, it restores G17. Linear G1 moves are plane independent in standard controls, but explicit restoration reduces dependence on later code assumptions.

Plane selection is modal and belongs to the same modal group. An exporter that emits a G18 arc and then assumes an unspoken G17 state can reverse or reinterpret later arcs.

## Direction mapping

The fitted arc stores a sign for increasing or decreasing angle in its internal plane coordinates. The exporter maps that sign to G2/G3 according to the controller's positive-axis view. In this implementation:

```text
G17: positive local angle -> G3
G18: positive local angle -> G2
G19: positive local angle -> G3
```

The asymmetry is a coordinate-orientation consequence, not an arbitrary exception. Controller documentation remains authoritative [@linuxcncgcode].

## Output validation

The repaired exporter:

- throws if any coordinate is non-finite;
- formats coordinates to three decimal places;
- sanitizes parentheses and newlines in comments;
- emits a model and tool comment;
- records roughing levels and finishing description;
- retracts to clearance, stops the spindle, and ends with M30.

Formatting to three decimals quantizes geometry to $1\ \mu$m in millimetres, which is typically much finer than the other errors in this reference. A real post should make precision configurable and appropriate for the controller.

## What the reference post omits

- tool selection and length compensation;
- work coordinate selection and probing;
- coolant and spindle direction variants;
- machine-specific safe-start blocks;
- canned cycles;
- helical G2/G3 output for entry moves;
- inverse-time feed or five-axis kinematics;
- controller limits on radius, sweep, and center format;
- subprograms and line numbers;
- fixture, stock, and machine limits;
- feed scheduling and corner rounding modes.

The examples in `examples/` are therefore reference outputs for inspecting geometry and modal logic, not machine-ready production programs.

## Exercises

1. Explain why G90 does not necessarily determine I/J/K semantics.
2. Compute I and J for a G17 arc from $(10,0)$ to $(0,10)$ centered at the origin.
3. Describe the failure if a controller interprets incremental centers as absolute centers.
4. Add a configurable decimal precision to the exporter and state the resulting quantization bound.
5. Draft a machine-specific safe-start block and identify which assumptions it establishes.

# Dexel Material-Removal Verification

## What a dexel represents

A dexel model stores material height on a regular grid of vertical rays. For node $(x_i,y_j)$, $H_{ij}$ is the highest remaining stock. It is a 2.5D representation: one scalar per column. Van Hook used depth-based methods for real-time NC milling display, and later work used sampled stock representations for error assessment [@vanhook1986; @huang1994].

The reference initializes

$$
H_{ij}=z_{\mathrm{stock\ top}}
$$

and lowers $H_{ij}$ as cutter positions sweep over the grid.

## Target field

The target height $T_{ij}$ is evaluated from the model upper envelope at every verification node. The repaired verifier uses the exact triangle evaluator with an effectively point-sized flat probe rather than a separate barycentric rasterizer. This aligns the target definition with the path generator's model.

An explicit `partMask` marks nodes whose $(x,y)$ projection lies inside at least one triangle. Statistics use this mask. Without it, background stock outside the part can dominate the reported percentage and distort min/max deviation.

## Cutter stamping

At a sampled cutter tip $(x_c,y_c,z_c)$, every dexel node within radius $R$ is updated by

$$
H_{ij}\leftarrow\min(H_{ij},z_c+q(r_{ij})),
$$

where

$$
r_{ij}=\sqrt{(x_i-x_c)^2+(y_j-y_c)^2}.
$$

For a flat tool, $q=0$. For a ball tool,

$$
q(r)=R-\sqrt{R^2-r^2}.
$$

The implementation computes the actual node offset rather than rounding the cutter center to one grid cell and applying integer footprint offsets. This subcell stamping reduces aliasing when the path crosses between nodes.

## Sweeping line segments

A move segment of 3D length $L$ is sampled with

$$
n=\max\left(1,\left\lceil\frac{L}{d_s}\right\rceil\right),
$$

where $d_s$ is a fraction of the smaller dexel cell dimension. The cutter is stamped at the $n$ interior/end samples.

Sampling a moving cutter by discrete placements can miss material between samples, especially near a flat tool's vertical footprint boundary. Choosing $d_s$ below the grid spacing makes the error small relative to the dexel resolution, but not zero. Exact swept-disk rasterization would update all grid nodes whose columns intersect the continuous swept volume.

## Move-boundary correctness

The baseline flattened all moves into one point stream. It skipped a segment only when the destination point's kind was rapid. A transition from a rapid endpoint to a cutting point could therefore sweep the cutter from the previous rapid location as though it were a cut.

The repaired verifier iterates move objects:

- rapid moves update current position without removing stock;
- plunge, ramp, and unfitted cut moves sweep their own segments;
- fitted cut moves simulate the authoritative `arcPts` and arc operations;
- no material-removal segment is inferred across a rapid-to-cut move boundary unless the cut move explicitly begins there.

Stateful segmentation is therefore respected in both export and verification.

## Deviation

At a part-mask node,

$$
d_{ij}=H_{ij}-T_{ij}.
$$

Interpretation:

- $d<0$: the simulated stock is below target, indicating possible gouge;
- $d\approx0$: target reached;
- $d>0$: excess stock remains.

The reported statistics are

$$
d_{\min}=\min d_{ij},\qquad d_{\max}=\max d_{ij},
$$

$$
\operatorname{RMS}=\sqrt{\frac1N\sum d_{ij}^2},
$$

and the percentage satisfying

$$
-g\le d_{ij}\le b,
$$

where $g$ is a gouge tolerance and $b$ is an excess-stock band.

![Dexel verification heat maps](../figures/verification_raster.png){width=92%}

## Tolerance band

The reference band is an engineering diagnostic:

$$
b=\max(e_{\mathrm{nominal}},e_{\mathrm{chord}})
+e_{\mathrm{arc}}
+0.75\max(h_x,h_y).
$$

The final term acknowledges dexel discretization. The gouge threshold is also tied partly to cell size. These formulas should not be interpreted as rigorous confidence bounds. Their purpose is to avoid declaring a sampled method wrong for an error smaller than its measurement resolution.

A more formal verifier would separately estimate:

- target sampling error;
- path sampling error;
- cutter stamping error;
- arc interpolation error;
- STL error;
- floating-point error.

## Visualization

The heatmap uses three qualitative regions:

- red for gouge beyond tolerance;
- green/teal for in-band stock;
- blue for excess material.

Outside the projected part mask, the visualization should be muted or omitted. A single global color scale can hide small gouges when excess stock is large; production tools often provide separate clipped scales and numeric probes.

![Coverage-first hybrid verification](../figures/verification_hybrid.png){width=92%}

![Surface-graph strategy verification](../figures/verification_surface-graph.png){width=92%}

## What dexel verification cannot prove

- collisions with holder, shank, fixtures, or machine;
- undercut or multi-sheet stock geometry;
- exact continuous swept volume between samples;
- surface finish, chatter, deflection, runout, or thermal error;
- controller rounding and servo dynamics;
- correctness of work offsets or tool length;
- stock remaining below an overhanging upper sheet.

It is a useful independent numerical check, especially for gross coverage and gouge regressions, but not the final authority.

## Exercises

1. Derive the ball-tool stamp height from the sphere equation.
2. Explain why using only the destination move kind can cut an unintended transition segment.
3. Estimate the maximum unsampled travel between cutter stamps.
4. Show how background nodes can inflate an in-tolerance percentage.
5. Design an adaptive dexel refinement rule near high-deviation cells.

# Testing Geometric Algorithms

## Test layers

The repaired project uses several complementary forms of evidence:

1. **unit tests** for predicates, interpolation, contour topology, and arc direction;
2. **numerical-oracle tests** comparing contact formulas with dense optimization;
3. **integration tests** generating complete finite jobs and G-code;
4. **baseline/fixed probes** exposing concrete defects;
5. **dexel verification** as an independent sampled geometry check;
6. **benchmark snapshots** for performance and output regression;
7. **visualizations** for topology and qualitative inspection.

No one layer is sufficient. A path can look correct and still omit a segment. A unit test can pass while a strategy leaves a large untested region. A dexel verifier can share a bug with the generator unless their implementations are sufficiently independent.

## Deterministic unit tests

The current test suite covers:

- uppercase ASCII STL and binary trailers;
- model normalization;
- orientation-independent point-in-triangle and degenerate rejection;
- ball and flat contact against dense sampling;
- the bilinear asymptotic decider;
- closed contour chaining;
- seam-crossing mask runs;
- analytic rectangle-boundary Eikonal distance;
- directional surface-metric distance;
- incoming-point preservation in arc fitting;
- G18/G19 direction mapping;
- finite generation/export for every finishing strategy;
- roughing entry generation;
- part-mask verification statistics.

The report is stored in `tests/test-report.txt`.

## Contact tests with a dense oracle

For a triangle and cutter query, the exact formula is compared with a dense sample of points over the triangle. For each sampled point, compute the required tip height from the radial cutter profile, then take the maximum. Increasing sample density should approach the analytic evaluator from below.

This oracle can miss a narrow maximum if too coarse, so the test uses multiple representative contacts and a tolerance consistent with sampling density. It is valuable because its implementation follows a different route from the feature formulas.

## Topology tests

Marching-squares tests should assert connectivity, not merely point coordinates. Useful cases include:

- a sampled circle should chain into one closed loop;
- cases 5 and 10 should follow the asymptotic decider;
- two close contours should remain distinct under endpoint quantization;
- a contour through a mask seam should remain one run;
- exact-level corners should follow a documented convention.

Topological tests often catch errors that an image comparison misses.

## The baseline arc probe

The baseline probe counted arc-fitted cut moves whose first stored point differed from the incoming machine position. It found 23. It then printed the initial G-code, making the missing segment visible:

```text
current position: X-9.000
first stored point: X-7.875
first baseline cut block: X-6.750
```

The repaired probe distinguishes the legal compact representation from the authoritative arc stream:

```text
raw cut arrays omitting incoming point: 46
repaired arc streams omitting incoming point: 0
```

A good defect test preserves the original failing example and asserts the specific repaired invariant.

## Strategy-level verification

The baseline hybrid probe reported approximately 78.76% of samples in its tolerance band. The repaired coverage-first probe reported approximately 96.40% under its revised verifier. Because the verifier also changed, this is not a controlled one-variable scientific experiment. The evidence is still useful when interpreted correctly:

- the original path demonstrably had uncovered regions;
- the repaired path restores raster coverage;
- the repaired verifier removes background and move-boundary biases;
- the benchmark provides a stable current regression target.

Claims should therefore be phrased as *run results under the stated verifier*, not universal accuracy guarantees.

## Property-based tests worth adding

1. **Monotonicity:** raising any model vertex must not lower the safe CL height.
2. **Tool monotonicity:** increasing flat-tool radius must not lower CL height.
3. **Translation:** translating model and query together in $xy$ preserves height.
4. **Vertical shift:** adding $c$ to all model $z$ values adds $c$ to CL height.
5. **Triangle permutation:** reordering triangle vertices preserves evaluator output.
6. **Arc reconstruction:** every accepted arc stays within tolerance of all source points.
7. **G-code round-trip:** parsed emitted operations reconstruct the same path within formatting tolerance.
8. **Verification monotonicity:** adding a cutting move cannot increase the simulated stock height.

Property-based random generation is especially effective for computational geometry, provided degenerate cases are generated intentionally rather than filtered away.

## Independent implementations

Shared code can create false confidence. The repaired verifier still uses the same `pointInTri` and exact upper-envelope evaluator as generation. A stronger validation harness would use:

- a separate BVH library;
- exact or adaptive predicates;
- an independent mesh-to-height rasterizer;
- analytic benchmark surfaces such as planes, spheres, and cylinders;
- a second G-code parser/simulator;
- cross-checks against established CAM or geometry libraries.

## Exercises

1. Write the monotonicity property for a ball tool formally.
2. Explain why a dense numerical oracle normally underestimates a maximum.
3. Design a test for a contour passing exactly through a grid corner.
4. State which baseline/fixed comparison variables changed simultaneously.
5. Propose an analytic benchmark for a ball tool on a plane and derive the expected CL surface.

# Complexity, Performance, and Memory

## Stage-by-stage complexity

Let:

- $n$ be triangle count;
- $M$ be total triangle-cell overlaps in the spatial hash;
- $Q$ be the number of exact CL evaluations;
- $\bar k$ be average candidate triangles per query;
- $N=(n_x+1)(n_y+1)$ be CL-grid nodes;
- $E_g\approx8N$ be metric graph edges;
- $P$ be total toolpath points;
- $V$ be dexel nodes;
- $S$ be total cutter sweep samples.

Approximate costs are:

| Stage | Time | Memory |
|---|---:|---:|
| STL parsing | $O(n)$ | $O(n)$ |
| Spatial hash build | $O(n+M)$ | $O(n+M)$ |
| Exact queries | $O(Q\bar k)$ | $O(n)$ stamps |
| CL field | $O(N\bar k)$ | $O(N)$ |
| Gradient field | $O(N)$ | $O(N)$ |
| Marching squares per level | $O(N)$ | $O(N)$ worst-case segments |
| Fast sweeping | $O(cN)$ | $O(N)$ |
| Surface-graph Dijkstra | $O(E_g\log N)$ | $O(N+E_g)$ implicit edges |
| Arc fitting | roughly $O(Pw)$ | $O(P)$ |
| Dexel verification | $O(SR^2/(h_xh_y))$ | $O(V)$ |

Here $c$ is the number of sweep cycles and $w$ is the average fitting window work. The graph edges are generated on demand, so they are not stored explicitly.

## Exact evaluator dominance

For many jobs, exact CL evaluations dominate generation. Strategies differ in how they use them:

- raster evaluates along refined rows;
- hybrid also builds a CL grid and exact-checks waterlines;
- metric strategies build a CL grid, solve a field, then exact-lift contours;
- roughing repeatedly samples an allowance evaluator across levels and rows.

Caching can help when many calls repeat or cluster, but a naive memoization by floating coordinates has low hit rate. More useful approaches include:

- reuse a CL grid for all strategies;
- hierarchical/adaptive CL sampling;
- per-cell local polynomial bounds;
- vectorized or parallel triangle queries;
- a BVH with coherent traversal;
- GPU compute for large regular query batches.

## Uniform grid occupancy

Let a triangle overlap $m_t$ hash cells. Total index storage is

$$
M=\sum_{t=1}^n m_t.
$$

Long thin triangles may overlap many cells even if their area is small. A rotated box or triangle-cell intersection test could reduce false insertions, but increases build cost. A BVH avoids duplication at the cost of tree traversal and less trivial implementation.

The grid is most effective when triangle size, cutter radius, and cell size are of similar order.

## CL-grid resolution tradeoff

Halving both $h_x$ and $h_y$ approximately quadruples $N$. It also:

- quadruples exact field samples;
- quadruples gradient and marching work per level;
- increases metric Dijkstra work by about four times plus a logarithmic factor;
- can increase the number and detail of contours;
- improves geometric and topological resolution.

Adaptive grids can concentrate resolution near CL ridges and contour levels. Botsch et al. describe how adaptive spatial structures reduce memory by refining only geometrically significant regions [@botsch2010]. Adapting marching and distance algorithms to nonuniform cells is more complex but often worthwhile.

## Dexel cost

At each cutter stamp, the implementation loops over a rectangular index box of roughly

$$
\left(\frac{2R}{h_x}+1\right)
\left(\frac{2R}{h_y}+1\right)
$$

nodes and rejects those outside the disk. Verification cost therefore grows quadratically with tool radius measured in grid cells and linearly with sweep samples.

Possible optimizations:

- precompute footprint offsets for discrete subcell phases;
- rasterize swept capsules rather than repeated disks;
- parallelize independent dexel tiles;
- use a coarse-to-fine verifier;
- restrict verification to a padded part mask;
- exploit monotone lowering with typed-array SIMD or GPU kernels.

## Benchmark

The supplied benchmark uses a 3,872-triangle three-hill height field, a 4 mm ball tool, and 0.08 mm requested scallop. Its current results are:

| Strategy | Generation ms | Verification ms | Points | Cut length mm | Estimated min | RMS mm | In band |
|---|---:|---:|---:|---:|---:|---:|---:|
| Raster | 87.1 | 142.2 | 699 | 796.253 | 1.0961 | 0.05770 | 99.030% |
| Hybrid | 202.1 | 130.0 | 1,875 | 1,047.321 | 1.4932 | 0.05147 | 99.407% |
| Surface graph | 90.5 | 106.3 | 1,262 | 733.477 | 1.0105 | 0.05059 | 99.835% |
| Slope Eikonal | 81.9 | not run | 1,289 | 747.416 | 1.0291 | - | - |

![Benchmark RMS deviation](../figures/benchmark_rms.png){width=78%}

Timing is sensitive to Node version, JIT warm-up, machine load, and data. Treat it as a regression snapshot. The geometric outputs and verification fields are more important than small timing differences.

## Exercises

1. Estimate CL-field node count for a $50\times30$ mm domain at 0.25 mm spacing.
2. Explain why halving grid spacing can more than quadruple total runtime.
3. Derive the approximate number of dexel nodes in a circular cutter footprint.
4. Compare expected behavior of a uniform grid and BVH for many tiny triangles plus one very large triangle.
5. Propose a benchmark suite covering planes, spheres, sharp ridges, narrow pockets, and noisy STL data.

# Production Hardening

## From reference implementation to CAM kernel

The repaired code is deliberately small enough to understand. A production system needs stronger representations and contracts. The most important changes are architectural rather than cosmetic.

### Replace the triangle soup with a validated model layer

A model layer should report:

- units and transforms;
- connected components and shells;
- boundary, nonmanifold, and self-intersection defects;
- facet quality and degenerate triangles;
- normal consistency;
- upper-envelope ambiguity and undercut regions;
- local feature size relative to tool diameter and tolerance.

It should not silently change geometry without recording the repair tolerance.

### Replace the uniform hash where appropriate

Use a BVH, kd-tree, or hybrid spatial structure with:

- robust bounding boxes;
- coherent batched queries;
- refitting for transformed models;
- parallel traversal;
- bounded memory for highly nonuniform triangles.

The exact feature-contact formulas can remain as the narrow phase.

### Introduce certified or filtered predicates

At minimum, orientation and interval topology should use adaptive filters:

1. evaluate in ordinary floating point;
2. compare against a rigorous error bound;
3. if uncertain, recompute in extended or exact arithmetic.

This approach preserves speed on ordinary inputs and consistency near degeneracies [@shewchuk1997; @higham2002].

## Adaptive CL representations

A uniform CL grid spends samples in flat regions and may still miss narrow ridges. An adaptive quadtree could refine when:

- corner/center interpolation residual exceeds tolerance;
- active contact feature changes within the cell;
- gradient or curvature estimate is large;
- a requested contour crosses the cell;
- verification detects a local error.

Each cell should carry conservative lower and upper bounds for $F$. A contour or path can then be refined until the bounds guarantee topology and clearance.

Adaptive contouring must handle nonconforming neighbors and crack-free segment connection. The benefit is that complexity follows geometric detail rather than total bounding-box area.

## Exact and cutter-aware scallop planning

A more faithful constant-scallop strategy needs a local metric derived from the envelope of neighboring cutter sweeps. A general development is:

1. choose a seed path with tangent $\mathbf t$;
2. determine the surface cross-feed direction $\mathbf n_s$;
3. compute local normal curvature in that direction;
4. combine surface curvature with cutter curvature in the normal section;
5. derive the cross-feed distance producing requested cusp height;
6. propagate the next path as an offset in the resulting anisotropic metric;
7. correct by direct swept-surface scallop evaluation.

Feng and Li present constant scallop-height path construction for three-axis sculptured surfaces [@feng2002]. Kim interprets cusp-height paths as geodesic parallels in an abstract Riemannian metric [@kim2007]. The reference `surface-graph` method is a pedagogical step toward this framework, not a substitute for it.

## Stock-aware roughing

A production rougher should update stock after each operation and generate rest machining. Options include:

- dexel stock with efficient difference queries;
- voxel or octree stock;
- boundary representations and Boolean operations;
- layered depth images;
- GPU height fields for three-axis stock.

Stock-aware planning can avoid air cuts, choose entry points in already cleared regions, control engagement, and detect thin residual islands.

## Collision model

Tool collision should include:

- cutting flute;
- non-cutting flute length;
- shank;
- holder and arbor;
- fixtures and clamps;
- stock, not only target model;
- machine travel and axis limits.

For fixed-axis three-axis work, each component can still be reduced to a radial profile or union of simple solids in many cases. The CL surface becomes the maximum constraint over all collision bodies, while only the cutter portion is allowed to remove stock.

## Controller-aware postprocessing

A robust postprocessor should be configured by machine/control capabilities:

- supported planes and arc-center modes;
- maximum arc sweep and radius;
- helical interpolation support;
- coordinate precision and line length;
- feed semantics and inverse time;
- work and tool offsets;
- spindle/coolant/tool-change syntax;
- safe retract policy;
- exact-stop or blending modes;
- subprogram conventions.

Postprocessing should be followed by parsing the emitted program back into a neutral motion model. Verification should operate on that parsed model. This closes the gap between internal geometry and actual output text.

## Independent verification

A strong validation stack includes:

1. internal fast verifier for interactive feedback;
2. independent high-resolution software simulation;
3. controller preview or backplot;
4. machine dry run with tool above stock;
5. single-block proof with conservative overrides;
6. in-process probing where appropriate;
7. first-article inspection.

Software geometry is only one layer of machining safety.

## Reproducibility and auditability

Every generated job should record:

- source model hash;
- model transform and units;
- tool assembly identifier;
- all strategy and tolerance parameters;
- software version/commit;
- postprocessor version;
- test and verification summaries;
- machine/setup identifier;
- timestamp and operator approvals.

The supplied JSON benchmark files demonstrate the value of machine-readable reports. A screenshot alone is not an audit trail.

## Exercises

1. Rank the listed hardening steps by safety impact for a three-axis mold job.
2. Design a conservative bound for a bilinear CL cell using corner values and a Lipschitz estimate.
3. Explain why collision checking against the target model is insufficient during roughing.
4. Propose a neutral intermediate representation for parsing G-code back into motion.
5. Define the minimum provenance record needed to reproduce one reference benchmark.

# Worked Example: Three Gaussian Hills

## Model and setup

The benchmark model is a sampled height field formed from three Gaussian hills and triangulated into 3,872 facets. Its normalized bounding box is

$$
[-12,12]\times[-12,12]\times[0,7.4656]\ \mathrm{mm}.
$$

The cutter is a 4 mm diameter ball end mill. Finishing parameters include:

- requested scallop: 0.08 mm;
- chord tolerance: 0.03 mm;
- margin: 1.5 mm;
- raster direction: $x$;
- steep threshold: 38 degrees;
- arc fitting: enabled, 0.025 mm tolerance;
- feed: 750 mm/min;
- clearance: 4 mm above model maximum.

The nominal flat-plane ball spacing is

$$
s_0=2\sqrt{2(2)(0.08)-0.08^2}\approx1.120\ \mathrm{mm}.
$$

## Raster result

The cross-feed span, including margin, is approximately 27 mm. The implementation generates 26 passes at an actual spacing near 1.08 mm. Adaptive refinement produces 699 path points. Arc fitting replaces portions with 41 arcs and 458 remaining lines from 695 raw segments.

![Raster path for the benchmark](../figures/paths_raster.png){width=92%}

The dexel verifier reports:

$$
\operatorname{RMS}=0.05770\ \mathrm{mm},
$$

with 99.030% of part-mask samples inside its stated band. Maximum excess stock is concentrated where planar raster spacing stretches on steep slopes and where the sampled verifier captures between-pass cusps.

## Coverage-first hybrid result

The hybrid begins with the same coverage raster and adds seven steep waterline contours. It produces 1,875 path points and a 1,047.321 mm cut length, compared with 796.253 mm for raster. The longer path reflects intentional overlap.

Its sampled RMS falls to 0.05147 mm and its in-band percentage rises to 99.407%. The result supports the expected qualitative tradeoff: extra wall-following passes improve sampled steep-region material removal at the cost of time.

![Hybrid verification field](../figures/verification_hybrid.png){width=92%}

## Surface-graph result

The surface-graph strategy samples the CL field, computes multi-source graph distance from the rectangular boundary, extracts 13 integer levels, and lifts them through the exact evaluator. It produces 1,262 points and the shortest path among the three verified strategies in this benchmark: 733.477 mm.

Its sampled RMS is 0.05059 mm and 99.835% of samples lie inside the diagnostic band. These results should not be generalized to arbitrary parts. Nested boundary-parallel contours happen to fit this smooth, simply connected height field well.

![Surface-graph verification field](../figures/verification_surface-graph.png){width=92%}

## Interpreting the comparison

The benchmark does **not** show that surface-graph paths are universally superior. It omits:

- pockets and islands;
- sharp vertical walls;
- narrow channels;
- noisy or defective STL;
- roughing stock;
- holder collision;
- controller and machine dynamics;
- measured physical surface finish.

It does show that the repaired code executes all strategies, exports finite programs, and supports quantitative regression. It also illustrates how path length, point count, program compression, and sampled deviation can move in different directions.

## Reproduction

From the project root:

```bash
node tests/run-tests.mjs
node benchmarks/run-benchmarks.mjs
```

Outputs are written to `benchmarks/` and `examples/`. The benchmark JSON contains exact run parameters and results. Figures are generated from these data by

```bash
python figures/make_figures.py
```

## Exercises

1. Recompute the nominal spacing from the stated radius and scallop.
2. Compute the percentage increase in hybrid cut length relative to raster.
3. Compare line/arc compression ratios for raster and hybrid.
4. Explain why the shortest toolpath is not necessarily the fastest on a real controller.
5. Design a second benchmark on a hemisphere and predict which strategy may perform well.

# Interactive Visual Laboratory

## Purpose

Static diagrams communicate one configuration. The standalone visual laboratory in `visual_lab/` lets a reader vary geometric parameters and inspect how algorithms respond. It uses the browser Canvas API and has no external dependencies.

Run it from the project root:

```bash
python -m http.server 8765
```

Then open `http://localhost:8765/visual_lab/`.

## Contact scene

The contact scene illustrates vertex, edge, and facet candidates for ball and flat cutters. Moving the cutter projection shows why the active maximum can jump from one feature to another. Such jumps create nonsmooth ridges on the CL surface even when the triangle mesh is piecewise planar.

![Interactive contact scene screenshot](../screenshots/visual_lab_contact.png){width=94%}

Suggested observations:

- move the cutter near a projected vertex and watch the vertex constraint dominate;
- move across an edge and compare edge and facet candidates;
- change radius and observe the broadened configuration-space footprint;
- compare the ball's smooth radial profile with the flat disk.

## Marching-squares scene

The marching scene exposes the four corner values of a bilinear cell, the requested level, the case index, and the two possible checkerboard connections. Adjust values until case 5 or 10 appears, then change the sign of

$$
Q=f_{00}f_{11}-f_{10}f_{01}.
$$

![Interactive marching-squares screenshot](../screenshots/visual_lab_marching.png){width=94%}

The scene makes clear that the contour is not determined by the arithmetic center average alone. It also shows how a small value change can alter connectivity without moving edge intersections very far.

## Scallop scene

The scallop scene displays two ball profiles and the residual cusp between them. Vary radius and pass spacing, and compare the measured height with

$$
h=R-\sqrt{R^2-(s/2)^2}.
$$

![Interactive scallop screenshot](../screenshots/visual_lab_scallop.png){width=94%}

The tool is a geometry filter: increasing radius lowers cusp for fixed spacing, while increasing spacing raises it nonlinearly.

## Metric scene

The metric scene compares planar distance, scalar slope-weighted distance, and 3D surface-graph distance. It visualizes directional anisotropy: uphill edges lengthen, while edges tangent to a contour do not incur a height increment.

![Interactive metric screenshot](../screenshots/visual_lab_metric.png){width=94%}

This is the conceptual bridge from elementary graph shortest paths to the first fundamental form.

## Dexel scene

The dexel scene sweeps a cutter over a sampled stock cross-section and colors remaining-stock deviation. Adjust sample spacing to observe aliasing and the difference between a point sample and a continuous swept volume.

![Interactive dexel screenshot](../screenshots/visual_lab_dexel.png){width=94%}

## Using screenshots as test artifacts

The screenshots are not substitutes for numeric tests, but they are useful visual-regression artifacts. A reproducible capture should fix:

- canvas dimensions;
- device pixel ratio;
- parameter values;
- browser version;
- animation time or paused state.

A future test harness could compare rendered pixels with a tolerance, while retaining geometric assertions as the primary oracle.

## Exercises

1. In the contact scene, find a location where the active feature changes from facet to edge.
2. Construct two case-5 cells with identical corner sum but opposite asymptotic-decider sign.
3. Verify the scallop formula numerically for three radii.
4. In the metric scene, identify a direction with minimal surface stretch.
5. Increase dexel spacing and document the first visible aliasing artifact.

\appendix

# Reference Pseudocode

This appendix summarizes the executable core without React or rendering details. The actual source remains authoritative.

## Spatial index

```text
BUILD_GRID(model, cutter_radius)
    choose cell size c from radius and model span
    allocate nx * ny cell lists
    for each triangle t
        compute projected bounding box B_t
        insert t into every grid cell overlapped by B_t
        store B_t
    allocate one query-stamp integer per triangle
    return grid
```

```text
QUERY_CANDIDATES(grid, X, Y, R)
    if disk(X,Y,R) is outside grid bounds
        return empty
    increment query id; clear stamps before integer wrap
    for each cell overlapped by disk bounding box
        for each triangle t in cell
            if stamp[t] is current id: continue
            stamp[t] <- current id
            if expanded projected box of t contains (X,Y)
                yield t
```

## Exact drop-cutter evaluator

```text
MAKE_EVALUATOR(model, grid, tool, floor_z)
    return function EVAL(X,Y)
        best <- floor constraint in cutter reference
        for t in QUERY_CANDIDATES(grid,X,Y,R)
            if ball tool
                best <- max(best, all vertex center heights)
                best <- max(best, all exact edge center heights)
                best <- max(best, valid facet tangent center height)
            else
                best <- max(best, vertices in disk)
                best <- max(best, edge/disk intersection extrema)
                best <- max(best, valid facet disk maximum)
        if ball tool: return best - R
        else: return best
```

## CL field

```text
BUILD_CL_FIELD(eval, rectangle, requested_spacing)
    nx <- ceil(width / requested_spacing)
    ny <- ceil(height / requested_spacing)
    hx <- width / nx
    hy <- height / ny
    for every exact node (i,j)
        F[i,j] <- eval(x0+i hx, y0+j hy)
    compute finite-difference Fx, Fy, and magnitude G
    return field with bilinear samplers
```

## Marching squares

```text
MARCHING_SQUARES(A, level)
    segments <- empty
    for every cell
        classify four signed corner values
        if empty/full: continue
        create only the edge intersections used by the case
        if checkerboard case 5 or 10
            Q <- f00*f11 - f10*f01
            choose pairing from sign(Q), with deterministic tie-break
        append local segment(s)
    quantize endpoints relative to cell size
    chain unused segments forward and backward
    mark a chain closed when endpoint keys match
    return polylines
```

## Fast sweeping Eikonal

```text
SOLVE_EIKONAL(f, hx, hy, seeds)
    T <- infinity at all nodes
    set seed nodes to prescribed values and mark fixed
    repeat
        max_change <- 0
        for each of four sweep directions
            for each nonfixed node
                a <- smaller horizontal neighbor
                b <- smaller vertical neighbor
                candidate <- one-sided update
                if both neighbors finite
                    solve anisotropic quadratic
                    accept causal larger root if valid
                lower T and update max_change
    until max_change < tolerance or cycle limit reached
    return T
```

## Surface-graph distance

```text
SURFACE_GRAPH_DISTANCE(field, spacing)
    create one graph node per CL sample
    seed all boundary nodes with distance 0
    priority queue <- all seeds
    while queue not empty
        pop node p with smallest tentative distance
        for each of 8 neighbors q
            w <- 3D distance between lifted samples p and q / spacing
            relax D[q] with D[p] + w
    return D
```

## Z-level roughing

```text
GENERATE_ROUGHING(model, tool, parameters)
    build allowance evaluator using inflated tool
    create descending z levels
    for each level z
        for each raster row
            scan allowance evaluator for safe/blocked transitions
            bisect transitions and form safe intervals
            union overlapping intervals on adjacent rows
        for each connected interval component
            traverse rows in alternating directions
            at first interval, emit validated helix/ramp/plunge entry
            between intervals, stay down only if sampled link is safe
            otherwise retract to sampled local clearance and reenter
            cut each interval
        retract component to global clearance
```

## Coverage-first hybrid

```text
GENERATE_HYBRID(eval, CL_field, parameters)
    generate complete raster finishing over the domain
    classify steepness from sampled |grad F|
    for descending z levels
        contours <- marching squares on F=z
        runs <- split contours by steep mask
        greedily order and orient runs
        densify each run
        safe_z <- maximum exact evaluator height on dense run
        link safely and cut entire run at safe_z
```

## Arc fitting

```text
APPLY_ARC_FITTING(moves, tolerance)
    current <- null
    for each move
        if move is a cut and current exists
            P <- prepend current unless move already begins there
            split P into constant-axis runs
            greedily fit endpoint-consistent circles
            validate radial error and monotone sweep
            store fitted operations against P as arcPts
        current <- final raw move point
```

## Dexel verification

```text
VERIFY(job, model, tool, parameters)
    build exact target height field and projected part mask
    initialize stock heights to stock top
    current <- null
    for each move
        if rapid: update current without cutting
        else if fitted arc move:
            reconstruct and sample every line/arc operation
            stamp cutter footprint at samples
        else:
            sample every explicit segment and stamp cutter
    deviation <- stock - target
    compute min, max, RMS, and in-band percentage on part mask
    return fields and statistics
```

# Repair Matrix

| Area | Baseline defect | Repaired invariant |
|---|---|---|
| STL | exact binary length and case-sensitive ASCII | valid trailers, case-insensitive parsing, finite coordinates |
| Model | unvalidated array and scale | finite complete triangles and positive scale |
| Grid | no max bounds or stamp wrap | explicit domain and query-id lifecycle |
| Predicate | absolute epsilon; degenerate accepted | scale-aware orientation; degenerate rejected |
| CL grid | overshot boundary; square-cell assumption | exact rectangle with $h_x,h_y$ |
| Marching | eager unsafe interpolation; center-average ambiguity | lazy edges and bilinear asymptotic decider |
| Mask split | closed seam lost | cyclic scan from a rejected vertex |
| Eikonal | four fixed square-grid cycles | anisotropic converged fast sweeping |
| Metric | scalar slope labelled constant scallop | surface-graph distance plus explicit approximation label |
| Hybrid | no discrete coverage guarantee | raster coverage plus steep waterlines |
| Entry | partial helix sampling only | full generated-path validation and fallback |
| Refinement | midpoint only | quarter/mid/three-quarter tests |
| Arc fit | incoming segment omitted | prepend actual current into authoritative arc stream |
| G-code | implicit arc-center mode | explicit G91.1 and finite/sanitized output |
| Verification | flattened move transitions; ignored arcs | move-aware and fitted-geometry simulation |
| Statistics | background mixed with part | explicit part mask |
| UI | shared cancel reference | separate generation and verification cancellation |

The detailed audit, line-level descriptions, and run evidence are in `docs/algorithm-audit.md`.

# Selected Exercise Solutions

## Ball scallop spacing

From Chapter 2, with $R=2$ mm and $h=0.08$ mm,

$$
s=2\sqrt{2Rh-h^2}
=2\sqrt{2(2)(0.08)-0.08^2}
=2\sqrt{0.3136}
=1.12\ \mathrm{mm}.
$$

## Graph-surface metric

For $\mathbf p(x,y)=(x,y,f(x,y))$,

$$
d\mathbf p=(dx,dy,f_xdx+f_y dy).
$$

Taking the squared Euclidean norm,

$$
\|d\mathbf p\|^2=dx^2+dy^2+(f_xdx+f_y dy)^2,
$$

which expands to the first fundamental form with

$$
E=1+f_x^2,\quad F=f_xf_y,\quad G=1+f_y^2.
$$

## Edge-ball stationary point

For

$$
\Phi(s)=z_f+ms+\sqrt{\rho^2-s^2},
$$

set

$$
0=\Phi'(s)=m-\frac{s}{\sqrt{\rho^2-s^2}}.
$$

Then

$$
m^2(\rho^2-s^2)=s^2,
$$

so

$$
s^2=\frac{m^2\rho^2}{1+m^2}.
$$

The sign must match $m$, hence

$$
s^*=\frac{m\rho}{\sqrt{1+m^2}}.
$$

Clamp this value to the interval where the finite edge lies inside the sphere cross-section.

## Waterline spacing on a plane

Let the wall be $z=mx$. Two waterlines separated vertically by $\Delta z$ have planar $x$ separation

$$
\Delta x=\frac{\Delta z}{|m|}.
$$

The surface distance along the slope is

$$
\Delta s=\sqrt{(\Delta x)^2+(\Delta z)^2}
=\Delta z\sqrt{1+\frac1{m^2}}.
$$

As the wall becomes steeper, $|m|\to\infty$ and $\Delta s\to\Delta z$.

## Hybrid length increase

Using the benchmark values,

$$
\frac{1047.321-796.253}{796.253}\times100\%
\approx31.53\%.
$$

This extra path is the cost of the coverage-first overlap in that run.

## Monotonicity of the CL surface

Let model $S'$ be obtained by raising one or more model points so that every corresponding height satisfies $z'\ge z$. For every cutter location and every point constraint,

$$
z'-q(r)\ge z-q(r).
$$

Taking maxima preserves the inequality:

$$
F_{S'}(X,Y)\ge F_S(X,Y).
$$

A test violation would reveal a candidate-selection, indexing, or numerical error.

## G17 center offsets

An arc starts at $(10,0)$ and ends at $(0,10)$ with center $(0,0)$. Under incremental-center mode,

$$
I=0-10=-10,
\qquad
J=0-0=0.
$$

The endpoint remains absolute under G90:

```text
G3 X0.000 Y10.000 I-10.000 J0.000
```

assuming counterclockwise direction in G17.

# Glossary

**Allowance**  Material intentionally left for a later operation.

**Arc fit**  Replacement of a polyline run by one or more circular interpolation commands within a tolerance.

**Asymptotic decider**  A rule that resolves checkerboard marching ambiguity using the bilinear interpolant rather than a corner average.

**Ball end mill**  A cutter whose lower end is a hemisphere.

**Bilinear interpolation**  Interpolation linear in each of two coordinates separately over a rectangular cell.

**Broad phase**  Cheap spatial pruning that finds possible contacts before exact tests.

**Boustrophedon**  Alternating left-to-right and right-to-left traversal, as in raster machining.

**C-obstacle**  The set of robot or cutter reference configurations that cause collision.

**Chord tolerance**  Permitted deviation between a sampled curve and a straight segment or fitted arc.

**CL surface**  Cutter-location surface: the safe cutter-reference height as a function of horizontal location.

**Configuration space**  A space whose points represent complete placements of a moving object.

**Contour**  A connected component of a scalar-field level set.

**Coverage**  The property that a path family reaches every region that must be machined to the specified geometric criterion.

**Cusp/scallop**  Residual material ridge between adjacent cutter passes.

**Dexel**  A depth element; here, one vertical stock-height sample on a 2D grid.

**Drop cutter**  Lowering a fixed-axis cutter at a horizontal location until first model contact.

**Eikonal equation**  A first-order nonlinear PDE of the form $\|\nabla T\|=f$.

**Facet contact**  Cutter contact at an interior point of a triangle face.

**Fast sweeping**  Iterative Eikonal solution by alternating directional grid traversals.

**First fundamental form**  The quadratic form measuring lengths and angles induced on a parameterized surface.

**Flat end mill**  A cylindrical cutter with a planar bottom.

**G17/G18/G19**  CNC interpolation planes $XY$, $XZ$, and $YZ$.

**G91.1**  Incremental arc-center mode on controls following the LinuxCNC-style convention.

**Geodesic distance**  Shortest path length measured on a surface or under a metric.

**Height field**  A surface represented by one scalar height for every planar coordinate.

**Hybrid finishing**  Combination of two or more path families, here raster and waterline.

**Marching squares**  Cell-by-cell extraction of planar contours from a rectangular scalar grid.

**Minkowski sum**  $A\oplus B=\{a+b:a\in A,b\in B\}$; used to form configuration-space obstacles.

**Narrow phase**  Exact geometric contact test on candidates found by the broad phase.

**Part mask**  Grid indicator identifying samples that belong to the projected part region.

**Predicate**  A geometric yes/no or sign decision, such as orientation or inside/outside.

**Raster finishing**  Parallel passes with a fixed projected cross-feed direction.

**Roughing**  Bulk material removal that intentionally leaves allowance.

**Spatial hash**  Grid-based map from spatial cells to overlapping primitives.

**Stepover**  Distance between adjacent passes, usually measured in a specified projection or metric.

**STL**  A triangle-soup exchange format commonly used for manufacturing meshes.

**Surface graph**  Graph whose vertices are samples lifted onto a surface and whose edge weights approximate surface length.

**Toolpath linking**  Motion between cutting paths, including stay-down, retract, rapid, plunge, ramp, and helix moves.

**Upper envelope**  Highest model height among all surface sheets above a planar coordinate.

**Waterline**  Constant-$Z$ contour path.

# Source-Code Cross-Reference

| Topic | Repaired function |
|---|---|
| Preset triangulation | `heightfieldTris` |
| STL import | `parseSTL` |
| Normalization | `buildModel` |
| Uniform hash | `buildGrid` |
| Orientation predicate | `orient2d`, `pointInTri` |
| Ball edge contact | `edgeBall` |
| Exact drop-cutter | `makeEvaluator` |
| CL sampling | `buildCLField`, `bilin` |
| Contouring | `marchSquares`, `splitByMask` |
| Eikonal | `solveEikonal` |
| Surface metric | `solveSurfaceMetricDistance` |
| Entry validation | `pathIsSafe`, `emitEntry` |
| Job generation | `generateJob` |
| Arc compression | `compressCut`, `fitArcsRun`, `applyArcFitting` |
| G-code | `toGcode` |
| Verification | `verifyJob`, `devColor` |

\backmatter

# References {-}

::: {#refs}
:::
