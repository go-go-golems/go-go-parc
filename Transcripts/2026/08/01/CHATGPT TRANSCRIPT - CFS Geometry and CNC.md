# CFS Geometry and CNC

- URL: https://chatgpt.com/c/6a6d90af-aa5c-83ea-94e8-1d72ddb1eefb
- Created: 2026-08-01T06:23:01.924Z

---

> teach me how https://haisenzhao.github.io/CFS/index.html works, i don't know much about geometry and such, i do know some maths and i have done some CNC programming in the past. dig deep

I’ll map the system from the public demo and paper, then rebuild the ideas from CNC intuition: coordinates, toolpaths, local frames, surface geometry, and optimization.

```json
{"open":[{"ref_id":"https://haisenzhao.github.io/CFS/index.html"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Inspected PDF instructions, metadata, rendered pages, and contact sheet visuals**

</details>

```json
{"system1_search_query":[{"q":"\"Connected Fermat Spirals\" code implementation"},{"q":"\"Connected Fermat Spirals for Layered Fabrication\" supplementary material"},{"q":"site:github.com \"Connected Fermat Spirals\""},{"q":"\"Fermat spiral\" toolpath implementation CFS"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 18 websites**

</details>

```unknown
bash -lc pdftotext -layout /mnt/data/fermat_spirals.pdf /mnt/data/fermat_spirals.txt && sed -n '1,260p' /mnt/data/fermat_spirals.txt
```

<details><summary>💭 Thinking</summary>

**Extracted PDF text, headings, equations, and supplementary files**

</details>

```json
{"open":[{"ref_id":"turn111032search1"},{"ref_id":"turn111032search0"}],"response_length":"long"}
```

```json
{"paths":["GitHub"],"query":"repository"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search","args":{"repository_name":"ejbosia/connected-fermat-spirals","query":"class def","topn":50}}
```

<details><summary>💭 Thinking</summary>

**Inspected repository and reviewed Fermat spiral implementation and utilities**

</details>

```json
{"system1_search_query":[{"q":"\"supplement.zip\" \"Connected Fermat Spirals\""},{"q":"\"a100-zhao-aux.zip\""},{"q":"\"fermat_spirals.pptx\" CFS source code"},{"q":"\"Connected Fermat Spirals\" \"C++\" MATLAB source"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Clarifying the geometry**

I’m distinguishing a true Fermat curve, \(r=a\sqrt{\theta}\), from the paper’s Fermat-style path. The method uses evenly spaced inward offsets, then connects alternating contours into one spiral-like route.

**Clarified the geometry**

**Assessing practical limitations**

I’m connecting the method to CNC and G-code while keeping its scope clear: it’s a planar deposition path, not a complete machining strategy. Offset spacing, holes, branches, collisions, motion limits, coverage, and corner behavior still need careful handling.

**Assessed practical limitations**

</details>

```json
{"open":[{"ref_id":"turn111032search2"}],"response_length":"long"}
```

```json
{"query":"polar graph Fermat spiral r equals square root theta geometry learning visualization"}
```

<details><summary>💭 Thinking</summary>

**Applying chart guidance**

I’m prioritizing readable charts: one clear series by default, concise axis labels, appropriate date formatting, scatter plots for relationships, and pie charts only for simple proportions.

**Selecting chart types**

I’m choosing charts based on the data’s structure: lines for ordered trends, bars for rankings, pies only for meaningful shares, and horizontal bars when labels or category counts require extra room.

**Choosing learning widgets**

I’m using an interactive learning block only when a listed equation or function is central and visualization improves the explanation. I’ll keep formula content in LaTeX and place each widget beside the relevant concept.

**Reviewing math topics**

I’m identifying the available visualizations for lines, slopes, polynomial roots, derivatives, and differential equations. I’ll use exact supported concepts only when they directly clarify the requested mathematical reasoning.

**Mapping geometry widgets**

I’m extending the math review to coordinate geometry and area relationships, including distance, midpoint, transformations, parallel or perpendicular lines, angle relationships, and plane-area formulas.

**Extending math coverage**

I’m adding area and whole-number visualizations, covering rectangles, squares, trapezoids, perimeter optimization, integer operations, absolute value, factor pairs, and common factors or multiples.

**Building more visualizations**

I’m covering factorization, multiples, arithmetic operations, place value, scientific notation, division, perfect-square patterns, and quadratic reasoning with targeted interactive explanations when they add clarity.

**Exploring quadratic triangles**

I’m adding visual tools for quadratic inequalities and vertex form, alongside triangle classification, similarity, area, angle relationships, and foundational theorems such as Pythagorean and cosine laws.

**Applied chart guidance and mapped math learning visualizations**

**Searched 10 websites**

</details>

```unknown
z=[5.87,6.58,4.11,4.86,1.81,4.84,1.18,1.25,4.35,5.12]
c=[1.40,1.55,1.19,0.46,0.83,1.07,2.11,0.51,1.08,0.88]
f=[1.38,1.08,0.81,0.93,0.52,0.56,0.23,0.31,0.81,0.70]
sum(z)/10,sum(c)/10,sum(f)/10

```

<details><summary>💭 Thinking</summary>

**Compared sharp-turn percentages across shapes**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"ejbosia/connected-fermat-spirals","path":"connected_fermat_spiral/image_conversion.py"}}
```

<details><summary>💭 Thinking</summary>

**Interacted with GitHub**

</details>

```json
{"system1_search_query":[{"q":"Fermat spiral r = a sqrt theta MathWorld"},{"q":"Fermat spiral polar equation Wolfram"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 4 websites**

</details>

iturn468951image0

# Connected Fermat Spirals, from CNC intuition upward

The project page is not an interactive program. It presents a 2016 SIGGRAPH paper, videos, example outputs, slides, and supplementary material. The underlying system takes a **connected, filled 2D shape** and a desired line spacing, then generates a mostly smooth, globally continuous filling path. citeturn487788view0turn111032search2

The single most important idea is:

> **CFS does not take a mathematical spiral and distort it into the shape. It starts with ordinary inward-offset contours, cuts them at carefully selected positions, and reconnects them into one path.**

That is very close to contour-parallel pocketing in CAM, except the disconnected offset loops are “rewired” into a continuous stroke.

---

## 1. What problem is it solving?

Suppose you need to fill this shape:

```text
   ┌──────────────────┐
   │                  │
   │   ┌────┐         │
   │   │hole│         │
   │   └────┘         │
   │             ┌─┐  │
   │             └─┘  │
   └──────────────────┘
```

A conventional contour-parallel strategy generates something like:

```text
Contour 0:  ─────────────────── closed loop
Contour 1:    ───────────────   closed loop
Contour 2:      ───────────     closed loop
Contour 3:        ───────       closed loop
```

These are smooth, but disconnected. For additive manufacturing, every disconnection may require stopping extrusion, moving, restarting, and managing pressure transients. For CNC, the analogous costs are retracts, repositioning, re-entry, lost feed continuity, and extra cycle time.

A raster or zigzag is easier to connect:

```text
→→→→→→→
      ↓
←←←←←←←
↓
→→→→→→→
```

But it has frequent reversals. Machines must slow near those reversals, and deposition can accumulate or thin out there.

CFS tries to retain the good part of contour-parallel paths—long boundary-following moves—while making the whole thing one continuous route. The authors describe the resulting curves as mostly long, low-curvature paths, with fewer interruptions than contour-parallel filling and fewer sharp turns than zigzag filling. citeturn487788view0turn312811search0

---

# 2. The geometry vocabulary you need

You do not need much classical geometry. You mainly need four ideas.

| Term | Plain meaning | CNC analogy |
|---|---|---|
| Region \(R\) | The area that must be filled | Pocket or machining boundary |
| Boundary \(\partial R\) | The outline and hole outlines | Part contour |
| Distance field \(D_R\) | Distance from every interior point to the nearest boundary | A map of how far you are from the wall |
| Iso-contour | All points with the same distance value | An inward offset curve |

## The distance field

For every point \(p=(x,y)\) inside the shape, define:

\[
D_R(p)=\min_{q\in\partial R}\|p-q\|
\]

This says:

1. Consider every point \(q\) on the boundary.
2. Measure the Euclidean distance from \(p\) to \(q\).
3. Keep the shortest one.

Imagine turning the shape into terrain:

- Every boundary is at height 0.
- Moving inward raises the terrain.
- The center of a thick area is high.
- Narrow areas form low passes.
- Thick lobes form peaks.

An iso-contour is a horizontal contour line on this imaginary terrain:

\[
c(d)=\{p\in R:D_R(p)=d\}
\]

So \(c(2\text{ mm})\) is the curve consisting of all points exactly 2 mm from the nearest boundary.

In CAM terms, these are essentially successive inward offsets.

The paper uses offsets located at approximately

\[
d_i=\left(i-\frac12\right)w
\]

where \(w\) is the desired fill width or path spacing. The first centerline is therefore half a bead width from the boundary, then the others occur one width apart. citeturn312811search0

---

## “Space filling” does not mean the centerline has area

A normal curve is one-dimensional, so mathematically it has no area. Fabrication fills an area because the path has a physical width.

You can think of it as sweeping a disk along the path:

\[
\text{covered area}\approx P\oplus B_{w/2}
\]

In plain language:

- \(P\) is the centerline.
- \(B_{w/2}\) is a disk with radius half the extrusion width.
- Move that disk along \(P\).
- The swept area should approximately equal the required region.

For milling, replace \(w/2\) with the effective cutter radius when considering swept cutter area, while treating stepover separately.

This is also why uniform spacing matters. If two passes are too close, their swept areas overlap excessively. If they are too far apart, a gap remains.

---

# 3. What makes a region “spirallable”?

Consider a rounded rectangle. Its inward offsets remain one closed loop until they disappear near the center:

```text
┌────────────────────┐
│ ┌────────────────┐ │
│ │ ┌────────────┐ │ │
│ │ │  ┌──────┐  │ │ │
│ │ │  └──────┘  │ │ │
│ │ └────────────┘ │ │
│ └────────────────┘ │
└────────────────────┘
```

You can cut each loop and connect it to the next loop, producing one ordinary inward spiral.

Now consider a dumbbell shape:

```text
     ______          ______
   /        \_______/      \
  |                        |
   \________/       \______/
```

At first, its inward offsets form one loop. Deeper inward, the narrow neck disappears and the offset splits into two loops:

```text
Outer level:       one contour

Middle level:    ( left )--( right )

Inner level:     ( left )   ( right )
```

The distance field has two peaks—one inside each lobe. Each peak creates a separate **pocket**.

A region is called **spirallable** when its distance field has one local maximum, or one connected maximum plateau, so that the nested contours can be converted into one spiral without dealing with branching. A region with multiple peaks must first be understood as several spirallable pockets connected through branching areas. citeturn312811search0

A useful mental model is:

- The distance field is terrain.
- Pockets are mountain summits.
- Narrow connections are mountain passes.
- The contour topology tells you how those summits are connected.

---

# 4. What is “Fermat” about the spiral?

## The classical mathematical Fermat spiral

In polar coordinates, a point is represented by:

- \(r\): distance from the origin.
- \(\theta\): angle around the origin.

A classical Fermat spiral satisfies:

\[
r^2=a^2\theta
\]

or equivalently:

\[
r=\pm a\sqrt{\theta}
\]

The positive and negative signs give two interleaving branches. citeturn425488search0turn425488search2

However, the CFS algorithm does **not** normally evaluate this equation to produce the toolpath. An arbitrary pocket has no natural circular origin, and the required spacing is set by offset geometry rather than the analytic Fermat formula.

The name refers mainly to the path’s structure:

- One interleaving arm travels inward.
- It turns around near the center.
- A second interleaving arm travels outward.
- The start and end are both on the outer boundary.

That last property is the essential manufacturing advantage.

---

## Ordinary spiral versus Fermat-style spiral

An ordinary inward spiral behaves like:

```text
boundary start → inward → inward → inward → center end
```

Its end is buried in the center. To connect another pocket, you generally need a separate move.

A Fermat-style fill behaves like:

```text
boundary start → inward → center turn → outward → boundary exit
```

The exit can be placed close to the start:

```text
        start •
              ↓
      inward spiral
           ↘
          center
           ↗
      outward spiral
              ↑
         exit •
```

That means the algorithm can enter a pocket from a parent path, fill the entire pocket, and come back out near where it entered—similar to calling a subroutine that returns control to its caller.

---

## A discrete “even and odd rings” interpretation

Suppose a simple pocket has offset rings:

\[
C_0,C_1,C_2,C_3,C_4,C_5
\]

A practical way to understand the two arms is:

- The inward arm uses approximately \(C_0,C_2,C_4\).
- The outward arm uses approximately \(C_5,C_3,C_1\), in reverse order.
- They join near the center.
- The start on \(C_0\) and exit on \(C_1\) can be placed near each other.

```text
Start
  │
  C0 ─── bridge ─── C2 ─── bridge ─── C4
                                           \
                                            center turn
                                           /
  C1 ─── bridge ─── C3 ─── bridge ─── C5
  │
Exit
```

The actual paper describes this more generally using inward and outward links obtained by following the gradient of the distance field. But the even/odd-ring picture captures the topology well.

A simplified independent Python implementation makes this interpretation explicit: it separates a contour list into even- and odd-indexed contours, generates two spirals, reverses the second, and merges them. fileciteturn3file0L2-L2

---

# 5. How the individual offset rings are connected

Assume we already have an ordinary spiral path \(\pi\) through a spirallable pocket.

For a point \(p\) on one turn, the distance-field gradient points approximately perpendicular to the local offset contour and inward toward the next turn.

The paper defines two conceptual links:

- \(I(p)\): the point where an inward gradient trace reaches the next inner part of the spiral.
- \(O(p)\): the corresponding outward link.

These are essentially cross-links between adjacent turns.

The algorithm:

1. Travels along a contour.
2. Stops slightly before a selected exit position.
3. Crosses to an inner contour using an inward link.
4. Travels around that contour.
5. Repeats until reaching the center.
6. Makes one central turn.
7. Uses the untraversed pieces and outward links to return toward the outside.
8. Exits at the chosen boundary position.

The seams are staggered. If all the transitions happened at exactly the same angular position, the result would resemble a zipper with a large straight seam and poor spacing.

The construction initially creates visible “stair steps” at rerouting points. Those are treated later by the optimization stage. citeturn312811search0

---

# 6. Arbitrary shapes require a contour graph

For a simple pocket, the offset contours form a chain:

```text
C0 — C1 — C2 — C3 — C4
```

For a complicated shape, they branch:

```text
             C3a — C4a
            /
C0 — C1 — C2
            \
             C3b — C4b
```

Here:

- \(C_0\) is the outer contour.
- \(C_2\) reaches a branching area.
- \(C_{3a}\) and \(C_{3b}\) belong to different pockets.

The paper represents this using a **spiral-contour tree**.

## Nodes

Every individual contour is a node:

\[
c_{i,j}
\]

where:

- \(i\) is the offset-depth level.
- \(j\) distinguishes disconnected contours at the same depth.

For example:

\[
c_{4,1},\quad c_{4,2},\quad c_{4,3}
\]

are three separate loops at the fourth offset level.

## Candidate edges

Edges are considered between contours on neighboring depth levels, such as \(c_{i,j}\) and \(c_{i+1,j'}\).

The formal candidate region is:

\[
O_{i,j,j'}
=
\left\{
p\in c_{i,j}\;:\;
d(p,c_{i+1,j'})
<
d(p,c_{i+1,k})
\text{ for }k\ne j'
\right\}
\]

This looks worse than it is. It means:

> Find the part of the outer contour for which a particular inner contour is the nearest inner contour.

It is a nearest-neighbor ownership region, similar in spirit to a Voronoi partition.

If that region is nonempty, the contours can potentially be connected there.

---

## Why edge weights are based on candidate-segment length

The weight assigned to a candidate edge is the length of its possible connection region.

The algorithm prefers **shorter** connection regions.

Why?

A long candidate region is a long section where two contours run cleanly beside one another. That is valuable, smooth machining or deposition territory. Cutting and rerouting there would disturb a long, low-curvature segment.

A short candidate region is often near a narrow transition or branch. Sacrificing that small region to make the connection preserves more of the long smooth sections.

So the algorithm is effectively saying:

> Put the seams in the least valuable places.

---

## Minimum spanning tree

The candidate contour graph can contain redundant connections. The algorithm chooses a **minimum-weight spanning tree**.

A spanning tree:

- Includes every contour node.
- Connects all nodes.
- Contains no cycles.

“Minimum-weight” means the total selected connection cost is minimized.

For CNC intuition, imagine that every contour is an operation and every possible transition has a seam cost. The spanning tree chooses enough transitions to connect all operations while avoiding unnecessary transition cycles.

The outer contour is used as the root. citeturn312811search0

---

# 7. The tree divides the shape into pockets and junctions

The paper classifies contour-tree nodes by degree.

## Type I: degree at most 2

These nodes form chains:

```text
A — B — C — D
```

A chain corresponds to a spirallable subregion. Its contours can be transformed into one local Fermat spiral.

## Type II: degree greater than 2

These are branching junctions:

```text
       child
         |
child — junction — child
         |
       parent
```

They are interfaces between pockets.

In physical terms:

- Type I chains are areas you can fill using one inward/outward spiral.
- Type II nodes are roundabouts where several local spiral fills must be attached.

---

# 8. Connecting all the local spirals

The tree is processed from the leaves upward toward the root.

Suppose a child pocket has a local Fermat spiral whose start and end are near each other:

```text
parent contour ───── A     B ───── parent contour
                     \     /
                      child
                      spiral
```

The parent contour is cut near points \(A\) and \(B\). The child spiral is inserted between them:

```text
parent before A
       ↓
child spiral start
       ↓
entire child fill
       ↓
child spiral exit
       ↓
parent after B
```

This is a path splice.

Because the start and exit of the child fill are close together, the parent only loses a short section. The traversal then continues along the parent.

Applying this recursively gives:

```text
root path
  ├── visit child pocket
  │     └── visit grandchild pocket
  ├── return to root
  ├── visit next child pocket
  └── return and finish
```

The final result is analogous to a depth-first traversal of a tree, except that every visit is represented geometrically by cutting and splicing actual contours.

---

# 9. Why the raw result is not yet machine-quality

After rerouting, the path is continuous in the \(C^0\) sense:

- Consecutive pieces meet at the same coordinate.
- There is no positional gap.

But their tangent directions may not match:

```text
───────┐
       └──────
```

This is continuous, but it contains a corner.

In CNC language, merely eliminating a retract does not guarantee smooth feed. A controller may still decelerate heavily if adjacent line segments change direction abruptly.

The raw CFS path also tends to have uneven spacing around rerouting seams:

```text
good:       ─────────────
            ─────────────

too close:  ─────────────
              ───────────

too far:    ─────────────

                ─────────
```

Therefore the paper performs a post-optimization.

---

# 10. The curve optimization, without hiding the maths

Let the raw path be sampled into points:

\[
p_1^0,p_2^0,\ldots,p_N^0
\]

The optimized points are:

\[
p_1,p_2,\ldots,p_N
\]

The objective is approximately:

\[
E(P)
=
E_{\text{stay}}
+\alpha E_{\text{smooth}}
+\beta E_{\text{spacing}}
\]

Each term has a specific job.

## A. Stay near the original path

\[
E_{\text{stay}}
=
\sum_i\|p_i-p_i^0\|^2
\]

This penalizes large movement.

Without it, the smoothing and spacing forces could substantially distort the shape or pull the path away from required boundary regions.

Think of every path point as attached to its original location by a spring.

---

## B. Reduce bending

A common discrete smoothness term compares a point with an average of its neighbors.

For uniformly spaced samples, a simple form would be:

\[
\|p_i-2p_{i+1}+p_{i+2}\|^2
\]

If three points lie on a straight line at even spacing, this is zero.

The paper uses a chord-length-weighted version:

\[
E_{\text{smooth}}
=
\sum_i
\left\|
(1-u_i)p_i+u_i p_{i+2}-p_{i+1}
\right\|^2
\]

where \(u_i\) compensates for nonuniform point spacing.

This is a discrete one-dimensional Laplacian. In physical terms, it behaves like bending a flexible strip so abrupt changes are reduced.

---

## C. Maintain the desired spacing

For each point \(p_i\), find a nearest point \(f_i\) on a neighboring portion of the path.

Then penalize:

\[
E_{\text{spacing}}
\approx
\sum_i
\left(\|p_i-f_i\|-w\right)^2
\]

- If the neighboring strand is closer than \(w\), the term pushes them apart.
- If it is farther than \(w\), the term pulls them together.
- If it is exactly \(w\), that contribution is zero.

Finding the correct “neighboring strand” is not trivial. The nearest point must not simply be the preceding or following point along the toolpath; it must be a point on an adjacent physical pass.

The paper handles this using nearest footpoints on nearby line segments.

---

## Alternating optimization

There are two coupled unknowns:

1. Where the path points should move.
2. Which segments are their relevant nearest neighbors.

The algorithm alternates:

```text
hold path fixed
→ recompute nearest footpoints

hold footpoints fixed
→ move path points using Gauss–Newton

repeat
```

Gauss–Newton is appropriate because the objective is expressed as a sum of squared residuals.

This remains a local optimization. It improves the raw construction but does not prove globally optimal curvature or perfect spacing. citeturn312811search0turn111032search2

---

# 11. The complete algorithm

A condensed representation is:

```text
INPUT
    Filled 2D region R
    Desired spacing w

1. Generate inward offset contours
    c[i,j] = contour at depth (i - 1/2)w

2. Construct candidate contour connections
    Compare contours at consecutive depth levels

3. Assign connection weights
    Prefer seams with short candidate regions

4. Compute a minimum spanning tree
    Root it at the outer boundary

5. Identify nonbranching contour chains
    Each chain becomes a spirallable subregion

6. Convert each chain into a local Fermat spiral
    Travel inward, turn near the center, travel outward

7. Traverse the tree from leaves to root
    Splice each child spiral into its parent contour

8. Sample and optimize the resulting path
    Stay close + smooth curvature + preserve spacing

9. Convert the final polyline to machine commands
```

In pseudocode:

```python
def connected_fermat_fill(region, spacing):
    contours = generate_offsets(region, spacing)

    graph = build_contour_adjacency_graph(contours)
    tree = minimum_spanning_tree(graph)

    local_spirals = {}
    for chain in find_nonbranching_chains(tree):
        local_spirals[chain] = make_fermat_spiral(chain)

    path = splice_bottom_up(tree, local_spirals)
    path = optimize_fairness_and_spacing(path, spacing)

    return path
```

The intellectual core is not generating offsets. CAM software has done that for decades.

The hard parts are:

- Recognizing how offsets split and merge.
- Choosing where to cut them.
- Connecting them without crossings.
- Preserving one continuous traversal.
- Repairing spacing and curvature afterward.

---

# 12. A worked dumbbell example

Consider:

```text
       left lobe         right lobe
       ________           ________
     /          \_______/          \
    |                                |
     \__________/       \__________/
```

Let the spacing be \(w=5\) mm.

## Offset levels

At 2.5 mm:

```text
one large contour
```

At 7.5 mm:

```text
one contour, but narrow at the neck
```

At 12.5 mm:

```text
two contours: left and right
```

At 17.5 mm:

```text
two smaller contours
```

The contour tree is approximately:

```text
C0
|
C1
|\
| \
L2 R2
|   |
L3 R3
```

## Local spirals

The left chain \(L2-L3-\cdots\) becomes one Fermat spiral.

The right chain \(R2-R3-\cdots\) becomes another.

Each spiral starts and exits near the location where its lobe meets the parent contour \(C1\).

## Global path

The parent contour is traversed until the left connection:

```text
C0 → C1 → enter left lobe
             ↓
        fill left spiral
             ↓
        return to C1
             ↓
        continue on C1
             ↓
        enter right lobe
             ↓
        fill right spiral
             ↓
        return to C1
             ↓
        finish outward route
```

No teleporting is required. The final line is one continuous sequence.

This is why the start/exit-on-boundary property is more important than the exact appearance of a Fermat spiral.

---

# 13. What an implementation actually looks like

The authors’ project page provides the research materials rather than an online generator. citeturn487788view0

A later independent Python implementation offers a useful, simplified view of the pipeline.

## Raster image to geometry

It:

1. Reads a binary image with OpenCV.
2. Extracts exterior contours and hole relationships.
3. Converts them into Shapely polygons.
4. Optionally simplifies rough pixel-derived outlines. fileciteturn5file0L2-L2

## Contour tree generation

It repeatedly erodes the polygon by the requested distance.

When an erosion remains one polygon, the new exterior is added to the current contour chain.

When an erosion becomes a `MultiPolygon`, the contour tree branches and each resulting polygon is processed recursively. fileciteturn4file0L2-L2

Conceptually:

```python
while shape still exists:
    shape = erode(shape, spacing)

    if shape is one polygon:
        append its exterior contour

    elif shape splits into polygons:
        recursively process each child polygon
        stop the current chain
```

## Local Fermat fill

The simplified implementation divides each chain into even and odd contours, generates an inward spiral for each set, reverses one, and joins them. fileciteturn3file0L2-L2

## Global connection

It recursively connects child spirals into parent spirals by:

- Projecting child endpoints onto the parent path.
- Cutting the parent near those positions.
- Reversing the child if its orientation is inconvenient.
- Merging parent-before, child, and parent-after. fileciteturn3file0L2-L2

Its demonstration script is therefore essentially:

```python
polygons = image_to_polygons(image)

for polygon in polygons:
    tree = generate_spirals(polygon, distance)
    path = connect_fermat_spirals(tree, distance)
    plot(path)
```

fileciteturn2file0L2-L2

This implementation is useful for learning, but it is a simplified independent recreation. It should not be treated as identical to the paper’s weighted contour graph, minimum-spanning-tree selection, and curve optimization.

---

# 14. Translating the path into CNC terms

CFS primarily solves a **geometric ordering problem**:

> In which continuous XY sequence should the offset-like paths be traversed?

It does not by itself solve the complete manufacturing process.

## For extrusion

Given path points:

\[
P_0,P_1,\ldots,P_N
\]

each segment has length:

\[
L_i=\|P_{i+1}-P_i\|
\]

Extrusion can be accumulated proportionally:

\[
\Delta E_i=kL_i
\]

producing commands conceptually like:

```gcode
G1 X20.000 Y10.000 E0.438 F2400
G1 X21.124 Y10.173 E0.492
G1 X22.205 Y10.501 E0.551
```

Pressure advance, acceleration, flow limits, temperature, bead width and junction behavior remain separate concerns.

## For planar pocket milling

The analogous commands might be:

```gcode
G1 Z-2.000 F300
G1 X20.000 Y10.000 F1200
G1 X21.124 Y10.173
G1 X22.205 Y10.501
```

But several additional steps are required:

- Offset the usable region for cutter radius.
- Design plunge, ramp or helical entry.
- Check that connecting bridges do not create excessive engagement.
- Decide climb versus conventional direction.
- Respect holder and fixture clearance.
- Control chip evacuation.
- Apply feed reduction based on curvature and engagement.
- Fit arcs or splines where appropriate.
- Account for controller look-ahead and minimum block time.

So CFS is closer to a **CAM path topology generator** than a complete CNC strategy.

Later research generalized connected Fermat spiral ideas to subtractive manufacturing and freeform surfaces, including scallop-height control, but that is beyond the planar 2016 algorithm on the project page. citeturn111032search24turn127345search3

---

# 15. What the results mean

The paper evaluated “sharp turns” using its own geometric metric rather than controller jerk or measured axis acceleration. From the ten examples in its table, the arithmetic mean of the reported sharp-turn shares is approximately:

genui{"chart":{"content":{"chartType":"bar","meta":{"title":"Average reported sharp-turn share","description":"Arithmetic mean across the paper's 10 test shapes.","footer":"This is the paper's geometric sharp-turn metric, not measured CNC jerk."},"xKey":"pattern","series":[{"dataKey":"sharpTurnShare","label":"Sharp-turn share","axisLabel":"Percent","valueFormat":"raw","valueSuffix":"%"}],"data":[{"pattern":"Zigzag","sharpTurnShare":4},{"pattern":"Contour-parallel","sharpTurnShare":1.11},{"pattern":"CFS","sharpTurnShare":0.73}]}}}

This supports the intended result: CFS behaves much more like contour-parallel filling than zigzagging in terms of turning, while avoiding contour plurality by producing one path. The authors also emphasize that CFS does not have all the mathematical properties of classical recursive space-filling curves. citeturn312811search0

Do not interpret this chart as proof that CFS is always the fastest machining strategy. The paper optimizes connection placement, smoothness and spacing; it does not solve a globally minimum-time toolpath problem.

---

# 16. Important limitations

## Coverage is approximate

The authors explicitly note that CFS is not guaranteed to completely cover every arbitrary region, even at arbitrarily high resolution. In practical fabrication, coverage is assessed using the finite bead or track width, not just the mathematical centerline. citeturn312811search0

## Sharp corners remain difficult

Smoothing a path near a concave or convex corner can pull it away from the corner, creating underfill. Keeping it in the corner can require high curvature. This is an unavoidable trade-off between coverage and fairness.

## The initial path is only position-continuous

The rerouted result joins geometrically, but does not automatically have matched tangents or continuous curvature. Post-optimization reduces visible corners but does not turn the path into an exact analytic spline with guaranteed \(G^2\) continuity.

## It is contour-biased

Successive layers tend to contain similarly oriented contour-following paths. In extrusion, that may not produce the directional cross-weaving obtained by rotating raster infill between layers. The paper identifies this as a concern for inter-layer structural behavior. citeturn111032search2turn312811search0

## Robust offsets are hard

Real inputs contain:

- Tiny gaps.
- Self-intersections.
- Nearly coincident edges.
- Slivers.
- Features narrower than \(w\).
- Holes that disappear or merge.
- Multiple disconnected islands.

These are topology problems, not just floating-point problems. A production implementation needs robust polygon cleanup and offsetting.

## One continuous path cannot solve disconnected components

If the layer contains two physically disconnected islands, a deposition path cannot move between them while remaining inside printable material. Each connected component requires its own path or a non-extruding travel.

## CNC constraints are not encoded

CFS continuity does not imply:

- Safe cutter engagement.
- Constant material-removal rate.
- Good chip evacuation.
- No gouging.
- Minimal cycle time.
- Suitable tool orientation.
- Suitable entry and exit motion.

Those need a machining-specific layer above the CFS geometry.

---

# 17. The shortest accurate mental model

Think of CFS as this sequence:

```text
ordinary CAM offsets
        ↓
observe where they split
        ↓
represent splits as a tree
        ↓
turn every nonbranching chain into
an inward-and-outward spiral
        ↓
splice child spirals into parent paths
        ↓
smooth the seams and correct spacing
        ↓
emit one ordered polyline
```

Or, in one sentence:

> **Connected Fermat Spirals are contour-parallel offsets that have been topologically rewired into a depth-first, inward-and-outward traversal of the shape’s distance-field tree.**

That is the core of the entire method.

