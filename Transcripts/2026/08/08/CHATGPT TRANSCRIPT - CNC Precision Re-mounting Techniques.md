# CNC Precision Re-mounting Techniques

- URL: https://chatgpt.com/c/6a766f25-86fc-83ea-a315-a1b7ed3e305d
- Created: 2026-08-07T23:50:45.623Z

---

> [image: sediment://file_00000000999481fba42eaa24bf2f2d67]
> [image: sediment://file_00000000ab8c822f81eeb92bdce291bf]
> Imagine I want to mill this with my CNC mill. How can I do this without losing the precision of placing the center hole when turning the piece over? What are common techniques to keep machining precision when remounting the piece?

<details><summary>💭 Thinking</summary>

**Planning the machining setup**

I’m focusing on preserving alignment while flipping an irregular part. I’ll compare datum holes, dowel pins, sacrificial stock, mandrels, and soft fixtures, then recommend a practical sequence for the rounded shape and center hole.

**Planned the machining setup**

**Refining the setup**

For this part, I’m favoring a sacrificial carrier: machine the front while attached, register the carrier with two asymmetrical dowel holes, flip onto matching pins, machine the back cavity, and cut the part free last.

**Refined the setup**

</details>

For a small irregular part like this, the usual approach is **not to try to re-clamp the finished outer shape accurately**. Instead, keep the part attached to a larger, accurately registered carrier until both sides are finished.

A good setup for your part would be:

1. Start with stock larger than the finished black piece.
2. Machine **two precision registration holes in the waste area** of the stock. Ream them if you need good repeatability.
3. Put matching dowel pins in a fixture plate.
4. Machine the first side while the part is still connected to the surrounding stock by tabs or an onion-skin.
5. Remove the whole stock, flip it, and put the same registration holes back over the dowel pins.
6. Machine the rear face and the magnet/center pocket.
7. Cut the part free only at the very end.

The important point is that the CNC is locating the **fixture/carrier**, not the organic black shape.

### For the center hole specifically

If the rear magnet pocket needs to be exactly centered relative to features machined on the front, there are two particularly good methods.

**Method A — register the whole workpiece with two pins.** This is usually what I'd choose. Put two dowel holes somewhere outside the final contour:

```text
First operation, top view

   registration pin                 registration pin
          ○                                ○

       +--------------------------------------+
       |                                      |
       |             finished part            |
       |               ______                 |
       |             /        \               |
       |            |    +     |  <- center   |
       |             \________/               |
       |                                      |
       +--------------------------------------+
                     waste stock
```

After flipping:

```text
fixture plate

             ●                    ●
          dowel pin            dowel pin

                 flipped stock
```

Two pins are preferable to one because a **single circular hole fixes X and Y but does not fix rotation**. Two pins, or one pin plus a slot/flat, fully register the part.

A common precision-fixture arrangement is actually **one round dowel pin + one diamond pin/slotted locator**. That avoids over-constraining the workpiece if the spacing between two holes is off by a few microns.

### Method B — make the center itself a datum

If the geometry permits it, you can machine a small center reference during the first operation. For example, drill/ream a center hole all the way through, or create a reference bore.

After flipping, locate that hole with:

- a precision dowel pin,
- an indicating pin,
- a touch probe,
- a coaxial indicator,
- or an expanding mandrel.

Then set CNC X0/Y0 from the measured bore center.

This is especially effective when the rear feature must be **concentric** with something on the front.

If the final magnet pocket is blind and you don't want a through-hole, the external registration-hole approach is generally easier.

### Other common flip-fixturing techniques

**Machined soft jaws** are very common. Machine a negative pocket matching the first-side shape into aluminum or machinable jaws, place the finished first side into that nest, and machine the second side. This works well for production, although the accuracy depends on how well the first-side geometry locates in the nest.

**An expanding mandrel or precision arbor** is excellent when the part already has an accurate central bore. The bore becomes the datum, and the workpiece is clamped concentrically around it. This is particularly useful for circular parts.

**3-2-1 locating** is the general fixture-design principle. Three points establish the primary plane, two establish a secondary direction, and one establishes the remaining direction. Proper fixtures are designed so the workpiece always returns to the same six constrained degrees of freedom.

**Probing after the flip** is another option. Instead of relying entirely on mechanical repeatability, probe known bores, bosses, or edges and rotate/translate the coordinate system accordingly. This is useful if your machine has a decent touch probe.

A simple **vise stop + parallels** works for rectangular stock and moderate accuracy, but I wouldn't use that as the sole method for a precisely concentric feature on a small sculpted part.

### What I'd use for the object in your photos

I'd machine several of these at once from a single plate:

```text
      dowel ○                             ○ dowel

 ┌──────────────────────────────────────────────────┐
 │                                                  │
 │     blob 1         blob 2         blob 3         │
 │      ___            ___            ___           │
 │    /     \        /     \        /     \         │
 │   |   +   |      |   +   |      |   +   |        │
 │    \_____/        \_____/        \_____/         │
 │                                                  │
 └──────────────────────────────────────────────────┘
```

Machine all of the sculpted fronts in Op 1, while leaving every part attached to the plate. Then flip the **entire plate** using two precision fixture locators and machine all the magnet pockets from the rear. Finally, machine through the perimeter or remove the tabs.

That way, the center of every rear magnet pocket comes directly from the same CNC coordinate system used for the front geometry. You never have to figure out where the center of an irregular finished blob is after reclamping it.

For a one-off, I'd use **two dowel holes in sacrificial stock + a fixture plate**. It's simple, inexpensive, and can give substantially better repeatability than trying to locate the finished part itself.


---

> algorithms to compute the 3d milling path for this type of creature, and the maths behind it. Let's assume it has no overhangs.

<details><summary>💭 Thinking</summary>

**Formulating milling paths**

I’m modeling the creature as a single-valued height field, then computing the cutter-center surface as a spherical offset. For a ball end mill, this is a max-plus dilation; raster or contour paths can sample it while respecting stepover and scallop limits.

**Formulated milling paths**

**Choosing machining algorithms**

I’m extending the model from top finishing to complete 3-axis machining: use configuration-space offsets, waterline contours for steep areas, and raster passes for shallow regions. A hybrid strategy usually balances accuracy, efficiency, and scallop control.

**Chose machining algorithms**

</details>

With **no overhangs**, the geometry becomes much simpler: the creature's upper surface can be treated as a **height field**

\[
z=f(x,y).
\]

That turns 3-axis toolpath generation into a mostly 2D planning problem plus a computation of the correct cutter height.

The key concept is the **cutter-location surface**: instead of following the model surface directly, compute the surface on which the cutter's reference point must move so that the cutter is tangent to the model without entering it.

## 1. The fundamental geometry

Suppose you use a ball end mill of radius \(R\). Let its center be

\[
q=(X,Y,Z).
\]

At a horizontal displacement \(r=(dx,dy)\) from the tool axis, the bottom hemisphere is

\[
z_{\text{tool}}(r)
=
Z-\sqrt{R^2-\|r\|^2},
\qquad \|r\|\leq R.
\]

To avoid gouging the desired surface,

\[
Z-\sqrt{R^2-\|(x,y)-(X,Y)\|^2}
\geq f(x,y)
\]

for every surface point underneath the cutter.

Therefore, for a given tool-axis position \((X,Y)\), the lowest legal ball-center height is

\[
\boxed{
Z(X,Y)=
\max_{\|(x,y)-(X,Y)\|\leq R}
\left[
f(x,y)+
\sqrt{R^2-\|(x,y)-(X,Y)\|^2}
\right].
}
\]

This equation is almost the whole problem.

It says:

> Put a sphere of radius \(R\) over the model and lower it vertically until it first touches the surface.

In CAM terminology, this is essentially a **drop-cutter calculation**.

Mathematically it is also a kind of **morphological dilation / max-plus convolution**.

---

## 2. Why simply adding the tool radius is wrong

You might initially think

\[
Z(X,Y)=f(X,Y)+R.
\]

That is only correct where the surface is horizontal.

For a smooth surface,

\[
z=f(x,y),
\]

the upward unit normal is

\[
n=
\frac{
(-f_x,-f_y,1)
}{
\sqrt{1+f_x^2+f_y^2}
}.
\]

At a tangent contact point \(s=(x,y,f(x,y))\), the ball center is

\[
q=s+Rn.
\]

So

\[
q=
\begin{pmatrix}
x\\y\\f
\end{pmatrix}
+
\frac{R}{\sqrt{1+f_x^2+f_y^2}}
\begin{pmatrix}
-f_x\\-f_y\\1
\end{pmatrix}.
\]

Notice that **X and Y change too**. On a slope, the ball center isn't vertically above the contact point.

This normal-offset formula works locally, but for concave geometry the offset surface can fold or self-intersect. The max-envelope/drop-cutter equation above automatically chooses the correct accessible branch.

---

# 3. If your input is an STL triangle mesh

You don't actually have to convert the STL into a dense heightmap.

For every desired cutter-axis coordinate

\[
p=(X,Y),
\]

find all triangles whose XY projections are within \(R\) of \(p\), and determine the highest possible ball position caused by each triangle.

Then

\[
Z(p)=\max_i Z_i(p).
\]

A BVH, R-tree, quadtree, or spatial hash makes the triangle lookup fast.

For an individual triangle whose plane is

\[
z=ax+by+c,
\]

write

\[
g=(a,b).
\]

For ball-end contact on the **interior of the triangle**, the maximizing contact point is

\[
u^*
=
p+
\frac{R g}{\sqrt{1+\|g\|^2}}.
\]

If \(u^*\) lies inside the projected triangle, the cutter-center height is

\[
\boxed{
Z
=
f(p)+R\sqrt{1+\|g\|^2}.
}
\]

That is the exact tangent position against the planar triangle.

If \(u^*\) lies outside the triangle, the maximum must occur on one of its edges or vertices.

### Edge contact

For an edge, reduce the problem to one dimension.

Take horizontal distance \(s\) along the edge, measured from the perpendicular projection of the cutter axis onto the edge's XY line. Let the edge height be locally

\[
z(s)=z_0+ms.
\]

Let the horizontal perpendicular distance from the cutter axis to the edge line be \(d_\perp\). The available ball radius in that section is

\[
r'=\sqrt{R^2-d_\perp^2}.
\]

Then maximize

\[
z_0+ms+\sqrt{r'^2-s^2}.
\]

The unconstrained optimum is

\[
\boxed{
s^*=\frac{m r'}{\sqrt{1+m^2}}.
}
\]

Clamp that position to the actual edge segment. Testing the endpoints handles vertex contacts.

So an exact triangle-based drop-cutter algorithm basically checks:

1. triangle-face contact,
2. three edge contacts,
3. vertices,
4. takes the maximum resulting \(Z\).

For a smooth creature made from an STL, that's a very workable implementation.

---

# 4. Once you have \(Z(X,Y)\), generating the actual path is easy

For a basic **parallel/raster finishing pass**, choose

\[
Y_i=Y_0+i\,s
\]

where \(s\) is the stepover.

Then sweep \(X\):

\[
P_i(t)
=
\left(
X(t),
Y_i,
Z(X(t),Y_i)
\right).
\]

Reverse direction every row:

```text
>>>>>>>>>>>>>>>>>
<<<<<<<<<<<<<<<<<
>>>>>>>>>>>>>>>>>
<<<<<<<<<<<<<<<<<
```

so the machine doesn't retract and return to the same side after every pass.

This is essentially what CAM packages call things like **parallel finishing, raster finishing, planar finishing, or scanline machining**.

For your rounded creature, this is probably the first algorithm I'd implement.

---

# 5. Stepover comes directly from the scallop geometry

With a ball cutter, adjacent passes leave a small cusp.

On a locally flat surface, if the ball radius is \(R\) and stepover is \(s\), the exact scallop height is

\[
\boxed{
h=
R-\sqrt{R^2-\left(\frac{s}{2}\right)^2}.
}
\]

Solving for stepover gives

\[
\boxed{
s=2\sqrt{2Rh-h^2}.
}
\]

For \(h\ll R\),

\[
s\approx\sqrt{8Rh}.
\]

This is useful because instead of arbitrarily saying "use a 0.2 mm stepover," you can specify:

> maximum geometric machining error = 0.01 mm

and calculate the stepover from that.

---

## Surface curvature modifies this

For a curved surface, the local scallop changes.

Take the normal section perpendicular to the toolpath. Let the signed curvature of the part in that direction be \(\kappa\), using positive curvature for a valley.

For small stepovers,

\[
h
\approx
\frac{s^2}{8}
\left(
\frac1R-\kappa
\right).
\]

For a flat surface,

\[
\kappa=0
\]

and you recover

\[
h\approx\frac{s^2}{8R}.
\]

This gives the basis of **constant-scallop machining**: vary the path spacing according to local surface curvature rather than using a fixed XY stepover.

---

# 6. Slope matters too

Suppose the XY cross-feed direction is a unit vector \(d\).

A horizontal displacement \(ds\) corresponds to a surface displacement

\[
d\ell
=
ds\sqrt{1+(\nabla f\cdot d)^2}.
\]

So a 0.5 mm stepover in XY does not correspond to 0.5 mm along a steep surface.

The surface itself has metric

\[
\boxed{
G=I+\nabla f\,\nabla f^T
}
\]

so for an XY displacement \(d\xi\),

\[
d\ell^2=d\xi^T G\,d\xi.
\]

That metric becomes useful if you're writing a sophisticated constant-scallop path generator.

---

# 7. More advanced path algorithms

Once you can evaluate the cutter-location surface, there are several standard ways of traversing it:

- **Raster / parallel:** parallel XY lines lifted onto \(Z(X,Y)\). Simple, robust, good for your blob-like geometry.
- **Contour-parallel:** start at the outer boundary and repeatedly offset the planar contour inward, evaluating cutter height along every contour.
- **Z-level / waterline:** intersect the cutter-location surface with planes \(Z=z_i\). Very good on steep sides.
- **Hybrid:** raster on shallow areas, Z-level contours on steep areas. This is common for organic 3D parts.
- **Constant scallop:** choose each subsequent path so that the predicted cusp height between it and the previous path stays approximately constant.

For something shaped like the black creature, **hybrid raster + waterline** is substantially better than uniform raster if its sides get steep.

---

# 8. Constant-scallop as a mathematical field problem

A more advanced way to generate paths is to calculate a desired local spacing

\[
s(x,y)
\]

from curvature, cutter radius, and allowed scallop.

Then construct a scalar field \(T(x,y)\) satisfying an Eikonal-type equation.

On the actual surface,

\[
\|\nabla_S T\|
=
\frac{1}{s(x,y)}.
\]

Then paths can be extracted as level sets

\[
T(x,y)=0,1,2,3,\ldots
\]

so consecutive contours are approximately the desired surface distance apart.

Fast marching or fast sweeping methods can solve this type of equation numerically.

This is one route from a basic CAM algorithm toward a true **iso-scallop toolpath generator**.

---

# 9. The most general mathematical interpretation

There's an even cleaner formulation.

Let \(W\) be the solid workpiece you must not cut into, and let \(C\) describe the cutter relative to its reference point.

Putting the cutter at position \(q\) causes a collision when

\[
(q+C)\cap W\neq\emptyset.
\]

Equivalently,

\[
q\in W\oplus(-C),
\]

where \(\oplus\) is the **Minkowski sum**.

So

\[
\boxed{
W\oplus(-C)
}
\]

is the set of forbidden cutter-reference positions.

The boundary of this configuration-space obstacle is exactly what CAM needs to follow.

For a height-field part and vertically oriented cutter, the complicated 3D Minkowski-sum problem collapses into the drop-cutter/max-envelope calculation above.

This formulation also generalizes cleanly from a ball end mill to flat, bullnose, tapered, or custom cutters.

For example, for a flat end mill of radius \(R\),

\[
\boxed{
Z(X,Y)=
\max_{\|(x,y)-(X,Y)\|\leq R}f(x,y).
}
\]

A flat cutter is therefore literally a **maximum filter over a circular neighborhood**.

---

# 10. A practical implementation architecture

For a first CAM implementation for this exact kind of part, I'd use this pipeline:

```text
STL
 │
 ▼
triangle BVH
 │
 ▼
choose XY raster locations
 │
 ▼
ball drop-cutter
 │
 │  facet tests
 │  edge tests
 │  vertex tests
 ▼
cutter-location points
 │
 ▼
adaptive interpolation to chord tolerance
 │
 ▼
zig-zag path
 │
 ▼
safe links/retracts
 │
 ▼
G-code
```

An important extra step is **adaptive sampling**. Don't generate a point every fixed 0.01 mm.

Calculate two endpoints, then calculate the actual cutter height at their midpoint. Compare it with the linear interpolation of the endpoints. If the deviation exceeds your machining tolerance, subdivide again.

For a curve with curvature \(\kappa_c\), the chordal error approximately behaves as

\[
e\approx\frac{\kappa_c L^2}{8},
\]

so a reasonable segment length is approximately

\[
L\lesssim
\sqrt{\frac{8e}{\kappa_c}}.
\]

Flat areas consequently produce long G-code moves, while the eyes, bumps, and rounded transitions automatically receive more points.

For this particular project, the combination of **triangle drop-cutter + raster traversal + scallop-controlled stepover + adaptive chord-error sampling** would give you a relatively small CAM implementation while already producing quite respectable 3-axis finishing paths.


---

> what are maths books / maths fields / resources i can use to learn this, with exercises and such. I am curious abut the maths itself

```json
{"system2_search_query":[{"q":"site:ocw.mit.edu multivariable calculus exercises MIT OpenCourseWare 18.02"},{"q":"site:ocw.mit.edu numerical analysis exercises MIT OpenCourseWare"},{"q":"site:cs.cmu.edu geometry processing course notes exercises meshes differential geometry"},{"q":"site:springer.com Computational Geometry Algorithms and Applications de Berg exercises"},{"q":"site:cambridge.org Differential Geometry of Curves and Surfaces do Carmo exercises"},{"q":"site:siam.org Level Set Methods and Fast Marching Methods Sethian"},{"q":"site:crcpress.com Curves and Surfaces for CAGD Farin exercises"},{"q":"site:press.princeton.edu Convex Optimization Boyd Vandenberghe exercises"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Mapping mathematical ideas**

I’m mapping the formulas to fields: differential geometry for normals and curvature; computational geometry for triangles and Voronoi methods; CAGD for splines; numerical analysis for approximation; PDEs and morphology for envelopes and toolpaths.

**Mapped mathematical ideas**

**Searched 9 websites**

</details>

The mathematics behind 3-axis CAM sits at an unusually good intersection of **classical geometry, calculus, numerical mathematics, and algorithms**. If the mathematics itself is what interests you, I would not start with a CNC-specific text. I would work through the underlying subjects and use machining as the source of exercises.

The most relevant fields are:

\[
\boxed{
\text{multivariable calculus}
\rightarrow
\text{differential geometry}
\rightarrow
\text{computational geometry}
\rightarrow
\text{numerical analysis}
}
\]

with **CAGD/geometric modeling**, **convex geometry**, and **PDEs/level-set methods** branching off from there.

## 1. Multivariable calculus and linear algebra

Start here if expressions such as

\[
\nabla f,\qquad
\frac{\partial f}{\partial x},\qquad
n=\frac{(-f_x,-f_y,1)}
{\sqrt{1+f_x^2+f_y^2}}
\]

aren't yet completely natural.

The pieces you particularly want are vectors, dot/cross products, matrices, parameterized curves and surfaces, partial derivatives, gradients, tangent planes, optimization with several variables, and Taylor approximation.

A very good free route is **MIT 18.02 Multivariable Calculus**. MIT has a self-study version as well as extensive supplementary problems; its newer recitation notes explicitly include exercises with solutions. citeturn652158search0turn652158search3

For your CNC interest, make yourself solve things like:

\[
z=f(x,y)
\]

and derive its tangent plane; compute the normal; find where a sphere is tangent to that surface; minimize the distance between a point and a surface; and derive the intersection between planes, lines, triangles, spheres, and cylinders.

Those are not artificial exercises—they become cutter-contact calculations later.

---

## 2. Differential geometry of curves and surfaces

**This is probably the field you will enjoy most.**

It studies things such as:

- tangent vectors and tangent planes
- surface normals
- arc length
- curvature and torsion
- first and second fundamental forms
- principal curvatures
- geodesics
- Gaussian and mean curvature
- offsets of curves and surfaces

Those are directly connected to questions such as:

> How far apart should two ball-end-mill passes be?

> What does "0.2 mm apart" mean on a steep curved surface?

> What happens to an offset surface near a concavity?

> In what direction is the surface bending most strongly?

A particularly good self-study text is **Shoshichi Kobayashi, _Differential Geometry of Curves and Surfaces_**. The Springer edition has many exercises **with full solutions** and starts with ordinary curves and surfaces in \(\mathbb R^3\), rather than throwing you immediately into abstract manifolds. citeturn585297view0

For example, after learning curvature, derive the ball-mill scallop approximation

\[
h\approx \frac{s^2}{8R}.
\]

Then redo the calculation when the workpiece itself has curvature.

That's differential geometry turning directly into machining mathematics.

---

## 3. Discrete differential geometry

After classical differential geometry, study what happens when your beautiful smooth surface becomes an **STL made of triangles**.

This is **discrete differential geometry (DDG)**.

Keenan Crane's CMU course is unusually well matched to what you're interested in. It deliberately combines traditional differential geometry with practical algorithms on 3D geometry; the course covers curvature, numerical methods, finite elements, exterior calculus, topology, and numerical linear algebra. Better still, there are both written and programming assignments and public exercise frameworks. citeturn585297view1

This is where questions like

\[
\text{What is the normal of a triangular mesh?}
\]

or

\[
\text{How do I approximate curvature on vertices?}
\]

become mathematically interesting.

A good project would be:

1. load an STL,
2. compute face normals,
3. compute vertex normals,
4. estimate curvature,
5. color the mesh according to curvature,
6. use that curvature to estimate a locally appropriate machining stepover.

That project ties together linear algebra, differential geometry, meshes, and numerical approximation.

---

## 4. Computational geometry

Differential geometry studies the geometry. **Computational geometry studies algorithms for geometry.**

This is where you get:

- point-in-triangle tests
- intersections
- nearest-point calculations
- convex hulls
- Voronoi diagrams
- Delaunay triangulations
- spatial searching
- point location
- quadtrees
- geometric robustness
- motion planning

The classic textbook recommendation is de Berg et al., **_Computational Geometry: Algorithms and Applications_**. It was written as a textbook/self-study resource and contains exercises; its subjects include point location, Voronoi diagrams, Delaunay triangulations, convex hulls, robot motion planning, and quadtrees. citeturn585297view2

This field explains the algorithmic side of something I mentioned earlier:

> Given cutter position \((X,Y)\), efficiently find the triangles that could collide with the cutter.

Naively, if there are \(N\) triangles and \(M\) cutter positions, you could test

\[
O(MN)
\]

triangle/tool combinations.

Computational geometry asks how you instead organize space so each query examines only a tiny relevant subset.

A nice sequence of exercises would be to implement a ray/triangle intersection, closest point on a triangle, bounding boxes, a quadtree or BVH, and then compare naïve drop-cutter performance against spatially accelerated drop-cutter performance.

---

## 5. Computer-aided geometric design — CAGD

This is the mathematics of **representing shapes**.

Search specifically for:

> **Computer-Aided Geometric Design**

or

> **Geometric Modeling**

You will encounter:

\[
\text{Bézier curves}
\rightarrow
\text{B-splines}
\rightarrow
\text{NURBS}
\rightarrow
\text{tensor-product surfaces}.
\]

This is enormously relevant to CAD/CAM because real CAD systems do not fundamentally think in terms of STL triangles.

Gerald Farin's **_Curves and Surfaces for CAGD: A Practical Guide_** is a standard applied text. It develops curve and surface methods from theory to implementation and includes programming exercises. citeturn585297view3

Here you'll meet expressions such as a Bézier curve

\[
C(t)=
\sum_{i=0}^{n}
B_i^n(t)P_i
\]

with Bernstein basis functions

\[
B_i^n(t)
=
{n\choose i}
t^i(1-t)^{n-i}.
\]

Then you get beautiful questions like:

- why does the curve remain inside its control polygon?
- why does de Casteljau subdivision work?
- how do derivatives of splines work?
- how do you compute curvature directly from a spline?
- how accurately must you tessellate a NURBS surface before machining?

If you enjoy the mathematical side of CAD itself, this subject is a major rabbit hole.

---

## 6. Numerical analysis

Eventually virtually every exact geometric formula has to become numbers in a computer.

That's **numerical analysis**.

You want interpolation, numerical differentiation, numerical root finding, error bounds, approximation, conditioning, floating-point arithmetic, convergence, and adaptive subdivision.

MIT's **18.330 Introduction to Numerical Analysis** describes the subject essentially as understanding how ordinary mathematical objects—functions, derivatives, integrals, differential equations—are represented and manipulated numerically, and it has problem sets available. citeturn585297view4turn652158search15

This becomes crucial when you say:

> Approximate this smooth cutter path with straight G-code segments, but guarantee no more than \(5\,\mu\text{m}\) error.

If a locally circular path has radius \(\rho\), then the sagitta of a segment with chord length \(L\) is approximately

\[
e\approx\frac{L^2}{8\rho}.
\]

Hence

\[
L\approx\sqrt{8\rho e}.
\]

That simple formula is the beginning of an **adaptive numerical discretization scheme**: use small segments where curvature is large and long segments where curvature is small.

This style of reasoning appears everywhere in CAM.

---

## 7. Convex geometry and Minkowski sums

This is where cutter compensation becomes especially elegant.

The operation

\[
A\oplus B
=
\{a+b:a\in A,\ b\in B\}
\]

is the **Minkowski sum**.

If \(W\) is the workpiece and \(C\) the cutter, collision testing can be transformed into reasoning about

\[
W\oplus(-C).
\]

This same mathematics appears in robotics because moving a robot around obstacles and moving a cutter around a part are both **configuration-space problems**.

Jean Gallier's **_Geometric Methods and Applications_** is a nice broad bridge text here: it covers affine and Euclidean geometry, convex sets, SVD, optimization, differential geometry and some computational geometry, with many exercises. citeturn328295view0

I would study this **after** basic differential and computational geometry rather than before them.

---

## 8. Mathematical morphology and max-plus mathematics

This is the slightly unexpected field hiding behind the ball-end-mill formula.

Recall

\[
Z(X,Y)
=
\max_{x,y}
\left[
f(x,y)
+
\sqrt{R^2-(x-X)^2-(y-Y)^2}
\right].
\]

That's not an ordinary linear convolution because instead of

\[
\sum ab
\]

you have operations built from

\[
\max
\quad\text{and}\quad
+.
\]

This connects to **mathematical morphology**, dilation/erosion, and **max-plus algebra**.

For a flat cylindrical cutter, the connection becomes extremely obvious:

\[
Z(X,Y)
=
\max_{\|(x,y)-(X,Y)\|\le R} f(x,y).
\]

That's essentially a geometric dilation/max filter by a disk-shaped structuring element.

Mathematical morphology itself grew from set-theoretic approaches to shape and uses set theory, topology, and related algebraic structures. citeturn812726search28

This isn't where I'd start, but once you recognize cutter compensation as dilation, it gives a quite different mathematical perspective on CAM.

---

## 9. PDEs, Eikonal equations, level sets and fast marching

This is the advanced direction behind things such as **constant-scallop paths**.

Suppose you want curves whose spacing varies according to a desired local metric. Rather than manually offsetting each curve, you can sometimes construct a distance-like function \(T\) satisfying an Eikonal equation such as

\[
|\nabla T|=F(x,y)
\]

and extract paths from

\[
T(x,y)=c.
\]

James Sethian's **_Level Set Methods and Fast Marching Methods_** is one of the classic references in this area. Fast marching methods are numerical methods for Eikonal and related Hamilton–Jacobi equations. citeturn585297view6turn652158search28

I would leave this until later. It's much more satisfying once gradients, curvature, numerical discretization, and geometric algorithms are already familiar.

---

# A route I'd actually follow

Rather than reading eight fields simultaneously, I'd do:

**MIT 18.02 multivariable calculus**  
↓  
**Kobayashi — Differential Geometry of Curves and Surfaces**  
↓  
**CMU/Keenan Crane — Discrete Differential Geometry**  
↓  
**de Berg — Computational Geometry**  
↓  
**Farin — Curves and Surfaces for CAGD**  
↓  
**numerical analysis as needed**

Then branch into **Minkowski/convex geometry** and **Eikonal/level-set methods** when they naturally become useful. The CMU DDG course is particularly valuable because it explicitly assumes only linear algebra, multivariable calculus, and some coding, then makes students derive and implement geometric algorithms. citeturn585297view1

If you want **one book to buy first specifically for the mathematical curiosity**, I'd pick **Kobayashi's _Differential Geometry of Curves and Surfaces_**. If you want **one free resource to work through**, I'd pick **Keenan Crane's Discrete Differential Geometry course** after getting comfortable with multivariable calculus. citeturn585297view0turn585297view1

And I'd keep one long-running programming exercise throughout: **write your own tiny 3-axis CAM kernel**. Start with \(z=f(x,y)\), then add normals, a spherical cutter, scallop control, STL triangles, acceleration structures, adaptive chord tolerance, and eventually constant-scallop paths. Each new mathematical subject will then have an immediate physical interpretation.


---

> what are the next steps algorithms for more complicated geometry?

<details><summary>💭 Thinking</summary>

**Planning algorithmic progression**

I’m organizing the next steps by geometric difficulty: arbitrary meshes, steep regions, pockets, overhangs, and internal cavities. I’ll connect each case to accessibility, collision detection, tool orientation, offset geometry, and multi-axis planning.

**Planned algorithmic progression**

</details>

```json
{"system2_search_query":[{"q":"site:sciencedirect.com 5-axis machining tool orientation accessibility cone freeform surfaces paper"},{"q":"site:link.springer.com 5-axis machining tool orientation collision avoidance freeform surface paper"},{"q":"site:dl.acm.org cutter location surface milling Minkowski sum machining paper"},{"q":"site:hal.science 5-axis milling tool orientation collision avoidance paper"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Structuring the progression**

I’m extending the method from heightfields to solid meshes, pockets, multi-setup machining, and simultaneous five-axis motion. The key shift is replacing simple visibility with configuration-space accessibility, collision checks, and orientation planning.

</details>

```json
{"system2_search_query":[{"q":"site:sciencedirect.com dexel model NC machining simulation swept volume paper"},{"q":"site:dl.acm.org CNC machining simulation swept volume dexel paper"},{"q":"site:link.springer.com CNC machining simulation dexel tool swept volume paper"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 5 websites**

</details>

The main conceptual jump is this:

\[
\text{simple 3-axis CAM: }(x,y)\mapsto z
\]

becomes

\[
\boxed{\text{general CAM: find a collision-free pose of a rigid tool}}
\]

For a fully general tool, a pose lives in \(SE(3)\): three position coordinates and three orientation coordinates. For an axisymmetric mill, rotation about its own axis is usually geometrically irrelevant, so you can often work with

\[
(q,u)\in \mathbb R^3\times S^2,
\]

where \(q\) is a tool reference point and \(u\) is the tool-axis direction. This configuration-space viewpoint is central to more general multi-axis machining algorithms. citeturn211554search0turn211554search8

A useful progression is the following.

### 1. Arbitrary mesh, but still 3-axis and top-accessible

Your first version assumed

\[
S=\{(x,y,f(x,y))\}.
\]

Relax that. Let the part simply be a triangle mesh representing the boundary of a solid \(W\).

Keep the tool axis fixed:

\[
u=(0,0,1).
\]

Now your basic query becomes

\[
\boxed{
\text{For a particular }(X,Y),\text{ what is the lowest legal tool position?}
}
\]

You can still implement a **drop-cutter**, except now you work directly against triangles, edges and vertices rather than a heightmap.

The important algorithms to add are:

- triangle/edge/vertex contact calculations,
- ray casting,
- point-in-mesh tests,
- BVH or AABB trees,
- triangle–tool collision tests,
- mesh connectivity,
- contour extraction.

For fixed-axis 3-axis machining, global accessibility has a close relationship to visibility/hidden-surface removal along the tool direction. citeturn211554search0

This gets you geometries such as steep walls, complicated pockets and non-height-field meshes, as long as the regions you intend to machine are actually accessible from the fixed tool direction.

---

### 2. Stop modeling only the cutting tip

This is a surprisingly important next step.

Your original ball-end cutter might be approximated as just

\[
C_{\rm ball}.
\]

But a real tool is more like

\[
C=
C_{\rm cutting}
\cup C_{\rm shank}
\cup C_{\rm holder}.
\]

A tool tip may fit into a cavity while the shank crashes into a nearby wall.

So every candidate position has two different tests:

\[
\text{local gouging test}
\]

and

\[
\text{global collision test}.
\]

Local gouging asks whether the cutting surface penetrates the desired part around the contact point. Global collision asks whether **any other part of the tool assembly** intersects the workpiece.

At this point BVHs become extremely useful: first reject almost all triangles using bounding boxes, then perform expensive exact geometric tests only against nearby ones.

---

### 3. Learn configuration-space geometry

This is the clean mathematical generalization of the whole subject.

Let \(C\) be the cutter and \(W\) the forbidden workpiece.

For a purely translating cutter,

\[
\mathcal C_{\rm obs}
=
W\oplus(-C).
\]

Every point inside this Minkowski sum corresponds to a cutter position that causes a collision.

So instead of asking

> Does this complicated cutter intersect this complicated part?

you transform the problem into

> Is this point inside the configuration-space obstacle?

For arbitrary orientation, define

\[
\mathcal C_{\rm obs}
=
\left\{
g\in SE(3):
g(C)\cap W\ne\emptyset
\right\}.
\]

Then machining becomes a form of **motion planning**:

\[
\gamma(t)\in SE(3)\setminus\mathcal C_{\rm obs}.
\]

That's where CAM and robotics begin to look like the same branch of mathematics.

---

### 4. Undercuts: move from 3-axis to 3+2

A fixed vertical cutter simply cannot reach a true undercut.

The simplest extension is **3+2 machining**:

1. choose a tool orientation,
2. hold it fixed,
3. perform an ordinary 3-axis operation,
4. reorient,
5. repeat.

Mathematically, sample candidate orientations

\[
u_i\in S^2.
\]

For each \(u_i\), determine the subset of the surface that is accessible:

\[
A_i\subset S.
\]

Now you have an interesting combinatorial problem:

\[
\text{choose }A_{i_1},A_{i_2},\ldots
\]

such that

\[
S_{\rm target}
\subseteq
A_{i_1}\cup A_{i_2}\cup\cdots
\]

while minimizing the number of setups, reorientations, machining time, etc.

That begins to resemble **set cover, clustering, spherical sampling and optimization** rather than just differential geometry.

---

### 5. Then simultaneous 5-axis

This is the big jump.

At every surface point \(p\), there is no longer one cutter orientation. There is a **set of allowable orientations**:

\[
F(p)\subset S^2.
\]

You can imagine \(F(p)\) as regions painted on a sphere.

Some orientations are ruled out because of local gouging:

\[
u\notin F_{\rm local}(p),
\]

and others because the shank or holder collides somewhere else:

\[
u\notin F_{\rm global}(p).
\]

Hence

\[
F(p)
=
F_{\rm local}(p)
\cap
F_{\rm global}(p).
\]

Research on 5-axis machining explicitly treats global accessibility, feasible orientations and configuration-space searches in this way. citeturn211554search0turn211554search8turn211554search10

Now your problem is no longer just to find a path across the part:

\[
p_0,p_1,\ldots,p_n.
\]

You need to choose both points **and orientations**:

\[
(p_0,u_0),
(p_1,u_1),
\ldots,
(p_n,u_n).
\]

---

### 6. Turn orientation selection into a graph problem

This makes a very nice algorithmic project.

At surface point \(p_i\), sample legal orientations:

\[
u_i^1,u_i^2,\ldots,u_i^{k_i}.
\]

Each legal pair

\[
(p_i,u_i^j)
\]

becomes a graph node.

Connect compatible states at consecutive cutter-contact points:

\[
(p_i,u_i^j)
\longrightarrow
(p_{i+1},u_{i+1}^{k}).
\]

Assign a cost such as

\[
E=
\alpha\,\Delta\theta
+
\beta\,\Delta\theta^2
+
\gamma\,\text{machine-motion-cost}.
\]

Then solve a shortest-path/dynamic-programming problem.

You might penalize

\[
\Delta\theta
=
\arccos(u_i\cdot u_{i+1})
\]

so that the tool doesn't twitch violently between orientations.

Configuration-space search and subsequent smoothing/optimization of tool orientation are established approaches for 5-axis sculptured-surface machining. citeturn211554search8

You can later replace the discrete graph with continuous optimization.

---

### 7. Generalize the cutter itself

A ball end mill is mathematically friendly because the sphere has constant curvature.

A bullnose, toroidal, barrel, flat-end or custom cutter introduces another layer.

Instead of simply writing

\[
q=p+Rn,
\]

you may have an unknown cutter contact parameter \(s\), unknown tool orientation \(u\), and unknown location \(q\).

You solve tangency conditions like

\[
C(s;q,u)=p
\]

together with matching normals

\[
n_C(s;q,u)
=
-n_S(p)
\]

and nonpenetration constraints.

This becomes a **constrained nonlinear optimization / root-finding problem**.

Modern algorithms for non-spherical 5-axis cutters jointly reason about contact point, tool posture, feed direction, collision avoidance and cusp constraints. citeturn211554search4

This is where topics such as differential geometry of two contacting surfaces become especially useful.

---

### 8. Replace path spacing with true surface geometry

Another escalation is to stop thinking about XY stepover entirely.

On an arbitrary parameterized surface

\[
r(u,v),
\]

the differential surface distance is

\[
ds^2
=
E\,du^2+2F\,du\,dv+G\,dv^2,
\]

where

\[
E=r_u\cdot r_u,\qquad
F=r_u\cdot r_v,\qquad
G=r_v\cdot r_v.
\]

That's the **first fundamental form**.

The second fundamental form gives you directional surface curvature.

Now you can calculate path spacing based upon:

- local surface curvature,
- cutter curvature,
- tool orientation,
- desired scallop height.

So instead of

```text
0.3 mm XY stepover everywhere
```

you attempt

\[
\boxed{\text{scallop height}\approx 10\ \mu m\quad\text{everywhere}.}
\]

Then path generation becomes a problem involving **surface metrics, curvature fields, geodesics and level sets**. Five-axis toolpath work also optimizes path placement while accounting for cusp requirements and machine constraints. citeturn211554search4turn211554search7

---

### 9. Topology enters when you offset paths

Suppose you generate an initial closed machining curve and repeatedly offset it.

Eventually:

```text
        _______
      /         \
     /           \
    |             |
     \           /
      \_________/

            ↓ offset inward

        ______
      /        \
     |          |
      \________/

            ↓

       ___    ___
      /   \  /   \
      \___/  \___/
```

One loop can suddenly split into two.

Or two loops can merge.

This is a **topological event**.

A robust CAM system therefore needs algorithms for:

- curve offsetting,
- self-intersection detection,
- planar arrangements,
- clipping,
- connected components,
- contour trees,
- medial axes / Voronoi diagrams.

This part of CAM starts looking heavily like computational geometry.

---

### 10. Roughing requires modeling the *current stock*

Finishing asks:

> Where is the final surface?

Roughing asks:

> What material still exists right now?

So introduce a time-dependent stock:

\[
W_0,W_1,W_2,\ldots
\]

After tool motion \(i\),

\[
W_{i+1}
=
W_i
\setminus
V_i,
\]

where \(V_i\) is the volume swept out by the tool during that motion.

The swept volume is

\[
V
=
\bigcup_{t\in[0,1]} C(t).
\]

Computing and subtracting cutter swept volumes is a fundamental formulation of machining simulation. Implementations use representations such as dexels, voxels, octrees and exact or approximate sweep envelopes. citeturn904591search0turn904591search3turn904591search5

This lets you do **rest machining**:

\[
R
=
W_{\rm current}\setminus W_{\rm desired}.
\]

Then generate the next toolpath specifically for \(R\).

---

### 11. Adaptive clearing adds medial-axis/distance-field ideas

For roughing pockets, you often don't want simple parallel passes.

Compute something like a distance field

\[
d(x)=
\operatorname{dist}(x,\partial W).
\]

Its ridges relate to the **medial axis**.

That geometry tells you where there is space for the cutter and how far it can be from walls.

This leads naturally toward algorithms built around:

- distance transforms,
- Voronoi diagrams,
- medial axes,
- offset curves,
- variable-width spirals,
- trochoidal/adaptive clearing.

There is a beautiful mathematical connection here: much of high-performance pocket-clearing is really about navigating the geometry of the **free space available to a disk**.

---

### 12. Finally, the CNC machine itself becomes part of the geometry

Up to this point you can generate an ideal tool pose

\[
(q(t),u(t)).
\]

But your actual 5-axis machine has joint coordinates

\[
Q(t)
=
(X,Y,Z,A,B),
\]

or some other configuration.

You therefore need inverse kinematics

\[
(q,u)\longmapsto Q.
\]

There may be:

- multiple inverse-kinematic solutions,
- rotary-axis limits,
- singular configurations,
- discontinuous branch changes,
- velocity limits,
- acceleration limits.

So two geometrically similar cutter paths can behave completely differently on the actual machine. Five-axis path research therefore considers tool orientation together with rotary motion, machine kinematic capacity and singularities rather than treating cutter geometry alone. citeturn211554search3turn211554search7

This is where **robot kinematics and optimal control** enter the picture.

---

## The hierarchy I would implement

If you're building your own CAM as a way to learn the mathematics, I would go in this order:

\[
\boxed{\text{1. Heightfield ball drop-cutter}}
\]

\[
\downarrow
\]

\[
\boxed{\text{2. Triangle-mesh drop-cutter + BVH}}
\]

\[
\downarrow
\]

\[
\boxed{\text{3. Full tool/shank collision detection}}
\]

\[
\downarrow
\]

\[
\boxed{\text{4. Z-level + contour-parallel paths}}
\]

\[
\downarrow
\]

\[
\boxed{\text{5. Evolving stock + swept-volume simulation}}
\]

\[
\downarrow
\]

\[
\boxed{\text{6. Constant-scallop paths}}
\]

\[
\downarrow
\]

\[
\boxed{\text{7. 3+2 accessibility planning}}
\]

\[
\downarrow
\]

\[
\boxed{\text{8. 5-axis feasible-orientation computation}}
\]

\[
\downarrow
\]

\[
\boxed{\text{9. Graph/optimization-based orientation planning}}
\]

\[
\downarrow
\]

\[
\boxed{\text{10. Machine inverse kinematics + verification}}
\]

The especially interesting mathematical transition is around **steps 7–9**. Before that you're primarily doing computational/differential geometry. After that you're doing **geometry + configuration spaces + motion planning + optimization + robotics**.

And the unifying object changes from a simple cutter-height function

\[
Z=f(X,Y)
\]

to a **free configuration space**

\[
\boxed{
\mathcal F
=
\{(q,u):C(q,u)\cap W=\varnothing\}.
}
\]

A sophisticated CAM algorithm is, in a very literal sense, searching for a good curve through \(\mathcal F\). citeturn211554search0turn211554search8

