---
title: Branch-and-Bound Spatial Queries — Tight Bounds Beat Fast Code
aliases:
  - Drop-cutter pruning
  - Admissible ceilings over a uniform grid
  - Nearest-first max query with running best
status: established
type: architecture-garden-design
created: 2026-10-25
analyzed: 2026-10-25
analysis_author: claude-opus-5-5
repository: /home/manuel/code/wesen/dropcut-studio
repository_remote: git@github.com:wesen/dropcut-studio.git
repository_commit: f3ebac2d5291b4a371bde25ae3a44d6f752cff41
tags:
  - architecture-garden
  - dropcut-studio
  - geometry
  - performance
  - branch-and-bound
  - spatial-index
  - testing
related_files:
  - packages/geometry/src/drop-cutter.ts
  - packages/geometry/src/spatial-index.ts
  - packages/geometry/src/drop-cutter.test.ts
  - packages/geometry/src/cl-field.ts
  - packages/planner/src/run.ts
related_notes:
  - "[[Research/Software Architecture Garden/dropcut-studio/claude-opus/01 - Project Architecture Overview - A Compiler Whose Narrow Waist Is Machining]]"
  - "[[Research/Software Architecture Garden/dropcut-studio/claude-opus/10 - Architecture Debt and Patterns Not to Repeat]]"
---

# Branch-and-Bound Spatial Queries — Tight Bounds Beat Fast Code

The geometric kernel of a CAM system answers one question millions of times per job: if the tool is placed at `(x, y)` and lowered until it touches the part, where is its tip? DROPCUT Studio's first correct implementation answered it 3,197 times per second. The fix that mattered was not micro-optimisation; it was replacing a correct but loose upper bound with a correct and tight one, and visiting candidates in an order that makes the bound bite early. This chapter explains that branch-and-bound structure, why its pruning cannot change the answer, and how the kernel is tested against closed-form geometry rather than against its own previous output.

> [!summary]
> - The **drop-cutter** query is a maximum over triangles of an exact per-triangle contact height (vertex, edge, face cases in closed form).
> - A uniform grid in CSR layout supplies candidates; a **generation stamp** deduplicates them without allocation.
> - A running best plus an **admissible ceiling** prunes whole cells and triangles. For a ball tool the ceiling is $h + \sqrt{R^2 - d^2}$, not $h + R$.
> - Cells are visited **nearest-first** in Chebyshev rings so the best tightens immediately.
> - Measured effect (README): 3,197 → ~78,000 queries/s; the loose bound alone gave ×1.35. At the analysed commit the benchmark test reports 96,580 q/s on 18,432 triangles.
> - Correctness is pinned by analytic identities: a ball of radius $R$ on a hemisphere of radius $R_0$ has a CL surface that is a hemisphere of radius $R_0 + R$, lowered by $R$.

## 1. The query

Define the **cutter-location surface** $\mathrm{CL}(x, y)$ as the lowest tip height at which a tool on the vertical axis through $(x, y)$ does not intersect the part. For a triangle mesh $\{T_k\}$ it decomposes as a maximum:

$$
\mathrm{CL}(x, y) = \max\Big(\text{floor},\; \max_k\, c_k(x, y)\Big)
$$

where $c_k$ is the contact height of the tool against triangle $T_k$ alone. The decomposition is exact: the tool comes to rest at the first contact on the way down, which is the highest of the individual contacts.

Each $c_k$ is itself a maximum over the triangle's features — three vertices, three edges and the interior — and `packages/geometry/src/drop-cutter.ts` solves each in closed form instead of lowering the tool iteratively.

**Ball tool, vertex at horizontal distance $d < R$ and height $z_v$.** The sphere centre sits at $z_v + \sqrt{R^2 - d^2}$.

**Ball tool, face on the plane $z = Ax + By + C$.** The sphere rests on the plane with its contact point offset uphill from the axis by $R(A, B)/g$, where $g = \sqrt{1 + A^2 + B^2}$. The contact is valid only if that offset point lies inside the triangle; the centre height is then $Ax + By + C + Rg$.

**Ball tool, edge.** Project the axis onto the edge. With perpendicular distance $d_\perp < R$, the sphere can touch anywhere in an interval of half-width $r_p = \sqrt{R^2 - d_\perp^2}$, along which the edge rises with slope $m$. The centre height as a function of position $s$ is $z_f + ms + \sqrt{r_p^2 - s^2}$, maximised at

$$
s^\* = \frac{m\, r_p}{\sqrt{1 + m^2}}
$$

clamped to the part of the interval that lies on the edge. The function `sphereEdge` is that derivation, line for line, with the derivation in its comment.

Flat tools have the analogous cases (vertex in disc, edge crossing the disc via a quadratic, the plane's uphill rim point, and the disc centre over a flat region). The result is the sphere-centre height minus $R$ for a ball, or the contact height directly for a flat.

The query cost is dominated not by these formulas but by how many triangles reach them.

## 2. Candidates: a uniform grid in CSR layout

`packages/geometry/src/spatial-index.ts` buckets triangles by their XY bounding boxes into a uniform grid. Three decisions in it are worth copying.

**Cell size is about half the query radius.** Much larger, and one tall triangle keeps a whole cell alive under pruning. Much smaller, and per-cell loop overhead dominates. At $R/2$, a query spans roughly a 5×5 neighbourhood with useful pruning granularity.

**Storage is compressed sparse row (CSR).** Instead of an array of arrays, the index holds `cellStart: Int32Array` and `cellItems: Int32Array`, so cell $k$'s triangles are `cellItems[cellStart[k] .. cellStart[k+1])`. It is built with two passes — count occupancy, prefix-sum, scatter — which is a counting sort. The comment records the payoff: on a 100,000-triangle mesh, avoiding tens of thousands of small arrays is the difference between 300 ms and 3 s. The current benchmark builds the index for 96,800 triangles in 5.1 ms.

**Deduplication uses a generation stamp.** A triangle spanning several cells appears in each of them. Rather than allocating a `Set` per query, the index keeps `stamp: Int32Array` (one entry per triangle) and a counter. Each query increments the counter; a triangle is visited only if its stamp differs, and is then stamped. That is $O(1)$ per candidate and zero allocation per query.

## 3. Bounds: the branch-and-bound core

**Branch and bound** is the search technique of keeping the best solution found so far and discarding any part of the search space whose *upper bound* cannot beat it. Its correctness depends on one property of the bound: it must be **admissible**, meaning it never underestimates what the discarded region could contribute. Its efficiency depends on two others: the bound must be tight, and good solutions must be found early.

The index stores, per triangle and per cell, the maximum Z of any vertex (`triMaxZ`, `cellMaxZ`). The query accepts a `ceiling(maxZ, d²)` predicate and skips any cell or triangle for which it returns false. Each tool supplies its own ceiling.

For a flat tool, contact height *is* a mesh height, so nothing whose top is below the current best can matter:

```ts
const ceiling = (maxZ: number, _d2: number) => maxZ > best;
```

For a ball tool, the naive admissible bound is $h + R$: geometry topping out at $h$ cannot lift a sphere centre above $h + R$. It is correct and almost useless, because near the rim of the disc it is far too generous. The tight bound uses the horizontal distance $d$ from the axis to the candidate's bounding box:

```ts
const ceiling = (maxZ: number, d2: number) => maxZ + Math.sqrt(R2 - d2) > best;
```

### 3.1 Why the tight bound is still admissible

Let a cell (or triangle) have maximum height $h$ and closest horizontal distance $d$ to the query axis. Every point $p$ in it has $z_p \le h$ and horizontal distance $d_p \ge d$. A sphere of radius $R$ centred on the axis that touches $p$ has its centre at

$$
z_p + \sqrt{R^2 - d_p^2} \;\le\; h + \sqrt{R^2 - d^2}.
$$

Every contact height the region could produce is bounded by the ceiling, so discarding the region when the ceiling is at or below `best` cannot remove the true maximum. Pruning with an admissible bound changes the running time, never the result.

### 3.2 Making the bound bite early: nearest-first traversal

A bound prunes only relative to `best`, so the order in which candidates are visited decides how much is pruned. `queryDisc` walks cells in **Chebyshev rings** outwards from the cell containing the query point:

```text
ring 0         ring 1            ring 2
                ┌─┬─┬─┐        ┌─┬─┬─┬─┬─┐
   ┌─┐          │1│1│1│        │2│2│2│2│2│
   │0│          ├─┼─┼─┤        ├─┼─┼─┼─┼─┤
   └─┘          │1│0│1│        │2│ │ │ │2│
                ├─┼─┼─┤        │2│ │0│ │2│ …
                │1│1│1│        │2│ │ │ │2│
                └─┴─┴─┘        │2│2│2│2│2│
```

The centre cell almost always contains the contact for a smooth surface, so `best` becomes nearly final after the first ring and most outer cells fail the ceiling test before any of their triangles are touched. The comment in the index describes the effect on a dense mesh: scanning a few dozen triangles per query instead of about 1,400.

### 3.3 The measured result

The README records the history:

| Version | Queries per second | Factor |
|---|---|---|
| First correct kernel | 3,197 | 1× |
| + naive ceiling $h + R$ | ≈ 4,300 | ×1.35 |
| + distance-aware ceiling and nearest-first rings | ≈ 78,000 | ×24 |

The benchmark tests at the analysed commit print 96,580 q/s on 18,432 triangles ("typical density") and 60,404 q/s on 96,800 triangles ("dense"). The README's summary is the lesson of the chapter: *both bounds are correct; only one is useful.*

## 4. Hot-loop discipline

The evaluator closures are written in a style the module comment defends explicitly: *do not "clean it up" into classes.* Each tool type gets its own specialised closure (`ballEvaluator`, `flatEvaluator`), so there is no polymorphic dispatch on tool type inside the loop; triangle coordinates are read from one flat `Float64Array` with stride 9; `queryDisc` takes a monomorphic `visit` callback instead of returning a candidate array. These are the conditions under which V8 inlines the callback and keeps the loop allocation-free.

That discipline is confined to the kernel. Everything that calls it — the CL-field builder, strategies, the linker's surface queries — uses ordinary readable code. The planner also memoises evaluators by inflation and CL fields by `(spacing, inflate)` per operation (`makeContext` in `packages/planner/src/run.ts`), because hybrid and constant-scallop finishing both need a field that costs seconds to build.

## 5. Testing against closed-form ground truth

`drop-cutter.test.ts` opens with a statement of method: *prototype parity would only prove we copied faithfully.* The tests instead use shapes whose CL surface is known analytically.

| Shape | Tool | Exact CL | What it exercises |
|---|---|---|---|
| Flat plate at $z = h$ | ball, flat | $h$ everywhere over the plate; floor elsewhere | face case, floor fallback |
| 45° ramp, slope $m = 1$ | ball radius $R$ | $z(x) + R(\sqrt{1+m^2} - 1)$ | face case with lateral contact offset |
| 45° ramp | flat radius $R$ | $z(x + R)$ — the uphill rim | flat-tool rim case |
| Hemisphere radius $R_0$ | ball radius $R$ | hemisphere of radius $R_0 + R$ about the same centre, lowered by $R$ | all three cases at once |

The hemisphere identity is the strongest of these. A sphere of radius $R$ touching a sphere of radius $R_0$ from outside has its centre at distance $R_0 + R$ from the other centre, so the locus of tool centres is a sphere of radius $R_0 + R$. It is exact, it holds over the whole dome, and a tessellated dome exercises vertex, edge and face contacts depending on where the query lands. Because the identity is independent of the implementation, a bug the prototype also had would still fail it.

## 6. Where the kernel approximates

Two tool types are handled approximately, and the direction of each approximation matters.

- **Bull nose (torus).** `bullEvaluator` returns `max(flat(R), ball(cornerRadius))`. A flat disc of the full radius reaches lower at the rim than the torus does, so it contacts geometry earlier and reports a CL that is never below the true one. The comment states this is conservative: it can leave material but cannot gouge.
- **V-bit (cone).** `makeCutterLocation` approximates a V-bit with a flat disc of the tip diameter. That disc ignores the cone's flanks, which extend outwards above the tip. A feature outside the tip radius but inside the cone's footprint can rise above the cone's surface, so the true CL is higher than the reported one. This approximation is **not conservative** — it can report a tip height at which the cone intersects the part. The comment calls it "for now" but does not state its direction, and no error-budget contribution or certificate row reflects it. See [[Research/Software Architecture Garden/dropcut-studio/claude-opus/10 - Architecture Debt and Patterns Not to Repeat|chapter 10]].

## 7. Applicability

The pattern — maximise (or minimise) over many candidates, each with a cheap admissible bound, visited in an order that finds good candidates first — is general:

- nearest-neighbour and k-NN search over spatial indexes;
- ray casting against a BVH, where the running best is the nearest hit distance;
- collision broad phase with bounding-volume ceilings;
- top-k document retrieval with per-term score upper bounds (the WAND and MaxScore algorithms);
- A* search, whose admissible heuristic is the same admissibility condition stated over paths.

It pays when the per-candidate exact computation is much more expensive than the bound check and when the candidate set is large. It does not pay for a handful of candidates, and it is unsafe the moment the bound is not admissible — a too-tight bound silently returns a wrong maximum.

## 8. Candidate ecosystem guidance

1. Before optimising code, check whether a tighter admissible bound exists. A bound that uses more of the geometry (distance, not just height) often dominates every constant-factor improvement.
2. Prove admissibility in a comment next to the bound; it is the only thing standing between pruning and a wrong answer.
3. Visit candidates in an order likely to establish a good running best early.
4. Use flat typed arrays, CSR buckets and generation stamps in kernels called millions of times; keep that style confined to the kernel.
5. Test numerical kernels against closed-form identities, not against previous output.
6. When approximating, record the direction of the error (conservative or not) and surface non-conservative approximations in the verification report.

## 9. Evidence and references

- `packages/geometry/src/drop-cutter.ts:46` (`makeCutterLocation`), `:78` (`ballEvaluator`), `:165` (`sphereEdge`), `:203` (`flatEvaluator`), `:313` (`bullEvaluator`); V-bit branch in `makeCutterLocation`.
- `packages/geometry/src/spatial-index.ts:57` (`buildIndex`, CSR two-pass build), `:143` (`queryDisc`, rings, stamps, ceilings).
- `packages/geometry/src/drop-cutter.test.ts` — plate, ramp and hemisphere identities; performance tests.
- `packages/planner/src/run.ts:331` — `makeContext` evaluator and CL-field memoisation.
- README section "The drop-cutter needed a better bound, not faster code."
- Test run at `f3ebac2`: `drop-cutter: 96,580 q/s on 18,432 tri`, `60,404 q/s on 96,800 tri`, `index build: 5.1 ms for 96,800 triangles`.
