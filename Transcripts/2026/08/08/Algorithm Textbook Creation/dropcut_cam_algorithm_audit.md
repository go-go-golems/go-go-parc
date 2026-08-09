# Dropcut CAM Algorithm Audit and Repair Record

**Scope.** This document records the extraction, diagnosis, repair, and execution of the algorithms in `dropcut-cam(1).jsx`. The repaired computational core is `src/dropcut-core.mjs`; the repaired React/Three.js application is `src/dropcut-cam-fixed.jsx`. The unmodified source is preserved as `src/dropcut-cam-original.jsx`, and the extracted baseline core is preserved as `src/dropcut-core-baseline.mjs`.

**Safety classification.** The software is an educational and research reference. It is not a certified CAM kernel or controller-specific postprocessor. Generated G-code must be independently simulated, checked against the actual control's arc and modal conventions, dry-run above the workpiece, and proven out under supervision.

## 1. Executive result

The source already contained a substantial 3-axis CAM pipeline: STL import, an exact triangle/cutter contact evaluator, Z-level roughing, raster and hybrid finishing, a sampled cutter-location (CL) field, marching squares, a fast-sweeping Eikonal solver, arc fitting, G-code export, and dexel verification. The main defects were not syntax errors. They were algorithm-integration defects, numerical edge cases, coverage gaps, and verification inconsistencies.

The repaired build passes **14/14 executable tests**. A representative 3,872-triangle benchmark produces finite, exportable jobs for all finishing strategies. On the benchmark's sampled part mask, the repaired verification reports:

| Strategy | Generation | Verification | Toolpath | RMS deviation | Samples in tolerance band |
|---|---:|---:|---:|---:|---:|
| Raster | 87.1 ms | 142.2 ms | 796.253 mm | 0.05770 mm | 99.030% |
| Coverage-first hybrid | 202.1 ms | 130.0 ms | 1,047.321 mm | 0.05147 mm | 99.407% |
| Surface-graph iso-spacing | 90.5 ms | 106.3 ms | 733.477 mm | 0.05059 mm | 99.835% |

These values are run-specific measurements from `benchmarks/benchmark-results.json`, not general performance guarantees.

## 2. Extraction boundary

The original JSX mixed four concerns:

1. geometry and CAM algorithms;
2. browser scheduling and cancellation;
3. Three.js rendering;
4. React state and user-interface controls.

The repair separates them:

- `src/dropcut-core.mjs` is a dependency-free ES module containing geometry, toolpath generation, export, and verification;
- `src/dropcut-cam-fixed.jsx` imports that module and retains the interactive application;
- `tests/run-tests.mjs` runs the core directly under Node;
- `benchmarks/run-benchmarks.mjs` generates reproducible jobs and reports;
- `visual_lab/` is a standalone canvas-based explanatory tool.

This separation made the algorithms directly executable without a browser or GPU and exposed integration defects that were hidden inside rendering code.

## 3. Defect and repair matrix

| ID | Original behavior | Consequence | Repair | Evidence |
|---|---|---|---|---|
| A1 | Binary STL accepted only when `84 + 50 n` was exactly the file length; ASCII matching was case-sensitive; coordinates were not validated. | Valid binary files with trailers failed; uppercase ASCII could fail; non-finite values propagated. | Accept typed arrays and buffers, allow legal trailing bytes, case-insensitive ASCII parsing, validate complete finite triangles and positive model scale. | Tests: STL parser and model normalization. |
| A2 | The uniform grid did not store maximum bounds or handle query-ID wrap. | Out-of-domain queries could form invalid cell intervals; a very long session could reuse stamps. | Add min/max bounds, early out for disjoint cutter footprints, clamp cell indices, and clear stamps before `Uint32` wrap. | Evaluator tests and finite-strategy test. |
| A3 | Point-in-triangle used an absolute `1e-9` threshold and accepted a degenerate triangle because all three signs were zero. | Scale sensitivity and false facet hits on zero-area projected triangles. | Use a signed orientation determinant, scale-relative tolerance, orientation independence, and explicit degenerate rejection. | Point-in-triangle test. |
| A4 | CL-field dimensions used `ceil(span/gs)` but still evaluated nodes at `x0+i*gs`, which could overshoot the declared boundary; interpolation clamped short of the last row/column. | Boundary geometry and gradient samples were internally inconsistent. | Compute exact `hx=span/nx`, `hy=span/ny`; evaluate the exact rectangle; allow exact boundary interpolation; retain both gradient components. | Eikonal and metric tests; all strategy jobs finite. |
| A5 | Marching-squares edge points were formed eagerly, including edges that did not cross the contour. Ambiguous cases 5/10 were resolved by the arithmetic mean of corner values. | Potential division by zero/NaN; topologically wrong connectivity for bilinear cells. | Compute only required edge intersections, clamp interpolation, use the bilinear asymptotic decider `Q=f00*f11-f10*f01`, and use scale-relative endpoint keys. | Asymptotic-decider and closed-loop tests. |
| A6 | Masking a closed contour treated its duplicated start/end as an ordinary linear sequence. | A kept run that crossed the seam was split or lost. | Merge the first and last partial runs when they belong to the same closed-loop component. | Baseline probe lost the seam run; repaired test passes. |
| A7 | Fast sweeping assumed a square grid, used four fixed sweep cycles, and seeded only the rectangular outer boundary. | Wrong metric on non-square cells; no convergence criterion or general sources. | Use anisotropic `hx,hy`, a consistent upwind quadratic update, configurable seeds/boundary, and convergence-based repeated four-direction sweeps. | Analytic distance-to-rectangle test. |
| A8 | Helix/ramp entry validated only 12 points on one helix orbit and did not validate the full descending path; ramp fallback was not path-checked. | A nominally accepted entry could cross the inflated CL surface between samples or on later turns. | Validate every generated segment at a spacing tied to tool radius and fallback helix -> ramp -> plunge. | Roughing-entry test and entry visualization. |
| A9 | Roughing interval boundaries were located with relatively coarse axial sampling and used directly. | Narrow obstructions could be missed; a boundary point could sit exactly on a tolerance edge. | Increase axial sampling density, bisect transitions, and nudge cut interval endpoints into the verified free region. | Roughing job finite and verified. |
| A10 | Adaptive path refinement checked only the midpoint. | An oscillatory or locally peaked CL profile could pass the midpoint test while violating chord tolerance elsewhere. | Check quarter, midpoint, and three-quarter samples before accepting a segment. | Strategy-generation and verification tests. |
| A11 | Hybrid finishing cut raster only in the shallow mask and waterlines only in the steep mask with a hysteresis band. | The two masks did not constitute a proven cover; sampled tests showed large uncut islands. | Make raster the coverage guarantee over the full domain and add waterline contours in steep regions. | Baseline probe: 78.76% in band. Repaired probe: 96.40%; benchmark hybrid: 99.407%. |
| A12 | Waterline segments used interpolated CL-grid contour coordinates at a nominal constant Z. | The exact evaluator could be higher between samples, causing contact/gouge risk. | Densify contour polylines, reevaluate exact CL heights, and raise each constant-Z contour to the maximum required exact height. | Finite path and dexel verification tests. |
| A13 | The implementation labelled `|grad T|=sqrt(1+|grad f|^2)/s0` as constant scallop. | This scalar approximation accounts for surface slope but not direction-dependent first fundamental form or cutter/surface curvature; the label overstated the guarantee. | Retain it as `slope-eikonal`, add an 8-neighbor Dijkstra distance weighted by actual 3D CL-edge length (`surface-graph`), and relabel both as approximate iso-spacing methods. | Surface-metric anisotropy test and comparison figures. |
| A14 | Arc fitting compressed each cut move's point array, but many cut arrays intentionally omitted the incoming current point. Export started at the second vertex. | The first cut segment of 23 arc-fitted moves vanished in the baseline probe. This is a material toolpath defect. | Prepend the actual incoming point to a separate `arcPts` stream before fitting and export from that stream. | Baseline: 23 omissions; repaired: 0. First G-code line now includes the missing `X-7.875` segment. |
| A15 | G-code did not declare incremental arc-center mode; comments and coordinates were not validated; plane-direction mapping needed controller-frame review. | Controller modal state could reinterpret I/J/K; malformed text or non-finite values could enter output; arcs could reverse in G18/G19. | Emit `G91.1`, sanitize comments, reject non-finite coordinates, and map signs according to positive-axis plane views. | G18/G19 test and example programs. |
| A16 | Verification flattened all moves to one point stream and skipped a segment only when the destination was rapid. A rapid-to-cut transition could be swept from the prior point. Arc-fit geometry was not simulated. | False stock removal and disagreement between exported and verified paths. | Simulate move-by-move; never cut rapid transitions; sample fitted arcs; sub-sample lines and stamp the analytic cutter footprint. | Part-mask verification test. |
| A17 | Target height was triangle-rasterized directly at nodes, while machining used the drop-cutter evaluator. Statistics mixed part and background and counted tolerance over all grid nodes. | Target discretization disagreed with generation; background dominated percentages; min/max included irrelevant stock. | Evaluate the exact upper envelope at all verification nodes, construct an explicit projected part mask, and compute every statistic over that mask. | Part-mask test and improved probe/benchmark results. |
| A18 | One cancellation reference was shared across generation and verification in the UI. | A stale cancellation could affect the wrong asynchronous operation. | Use separate cancellation references and lifecycle resets. | Manual UI inspection and JSX parse check. |

## 4. The critical arc-start defect

The internal move representation is valid: a `cut` move may store only the points *after* the current machine position. The baseline arc compressor treated the first stored point as index zero and generated operations starting at index one. Thus, the segment from the current machine position to the first stored point was not represented by an operation.

The baseline probe found **23 affected finishing moves**. In its first move, the tool was at `(-9,-9,0)` while the first stored point was `(-7.875,-9,0)`. The exported program jumped directly to `X-6.750`, deleting 2.25 mm of intended cutting path, including the 1.125 mm incoming segment. The repair constructs

```text
arcPts = [incoming current point] + stored cut points
```

before fitting. `mo.pts` remains unchanged for application rendering and accounting; `mo.arcPts` is the authoritative fitted/exported geometry. This preserves the first segment without changing the compact internal move convention.

![Arc-start omission and repair](../figures/arc_start_omission.png)

## 5. Hybrid coverage diagnosis

The original hybrid strategy attempted to partition the CL domain using two slope tests:

```text
shallow: |grad F| <= 1.15 tan(theta)
steep:   |grad F| >= 0.85 tan(theta)
```

The overlap was intended to avoid a hard seam, but coverage still depended on three sampled operations:

- shallow intervals were sampled along raster rows;
- waterline contours were sampled on a coarser CL grid;
- contours were split by a sampled steep predicate.

No invariant proved that every point would be reached by either family. The baseline probe measured only 78.76% of verification samples inside its band. The repaired strategy uses a simpler safety invariant:

> Every point receives the ordinary raster strategy; steep regions may receive additional waterline passes.

This is longer and partially redundant, but its coverage argument is explicit. A production hybrid should replace redundancy with a formal cover plus a controlled overlap strip, not merely complementary threshold names.

## 6. Constant-spacing terminology

For a graph surface `z=f(x,y)`, the induced metric is

```math
G = I + (grad f)(grad f)^T.
```

For a planar displacement `d=(dx,dy)`, the corresponding differential surface length is

```math
ds = sqrt(dx^2 + dy^2 + (f_x dx + f_y dy)^2).
```

The old scalar Eikonal right-hand side `sqrt(1+|grad f|^2)/s0` is direction independent. It equals the stretch only when motion is aligned with the gradient; across contours it overestimates or mischaracterizes the local metric. The new `surface-graph` option builds a graph on CL samples and assigns each edge its actual 3D chord length. Multi-source Dijkstra then produces approximate geodesic distance from the boundary. Level sets at integer multiples of the requested spacing are therefore approximate equal-*surface-distance* contours.

Neither method is an exact constant-scallop algorithm. Exact scallop height depends on tool geometry, the local normal section, surface curvature, and pass direction. The application and textbook now make this limitation explicit.

![Metric comparison](../figures/metric_field_difference.png)

## 7. Verification model and error budget

The repaired verifier is a 2.5D dexel/height-map simulation. For each sampled cutter position `(x_c,y_c,z_tip)`, it updates a node `(x,y)` inside the cutter footprint using

```math
z_cut(x,y) = z_tip + q(r),
```

where `r=sqrt((x-x_c)^2+(y-y_c)^2)` and

```math
q_ball(r) = R - sqrt(R^2-r^2),
q_flat(r) = 0.
```

The machined stock height is the minimum over all sampled placements. The target is the model's upper envelope evaluated by the exact triangle evaluator. Deviation is

```math
d = H_machined - H_target.
```

- `d < 0` indicates possible gouge;
- small nonnegative `d` is remaining stock within tolerance;
- large positive `d` is excess stock.

The reported tolerance band includes requested machining tolerance and a grid-discretization allowance. It is an engineering diagnostic, not a proof. A formal or production-grade verifier would need adaptive sampling, holder/shank collision, controller interpolation semantics, acceleration effects where relevant, and an independent geometric kernel.

## 8. Tests

`node tests/run-tests.mjs` currently reports:

```text
PASS  STL parser accepts uppercase ASCII and binary trailers
PASS  model normalization centers XY and raises minimum Z to zero
PASS  point-in-triangle is orientation independent and rejects degenerate triangles
PASS  drop-cutter evaluator agrees with dense triangle optimization
PASS  marching squares uses bilinear asymptotic decider
PASS  marching squares chains a sampled circle into a closed loop
PASS  mask splitting joins a run crossing a closed seam
PASS  fast sweeping solves distance to rectangle boundary
PASS  surface metric graph distance respects slope anisotropy
PASS  arc fitting prepends actual current and preserves first segment
PASS  G18/G19 arc mapping uses positive-axis CNC views
PASS  all finishing strategies generate finite exportable jobs
PASS  roughing entries are generated and finite
PASS  dexel verification reports part-mask statistics

14/14 tests passed
```

The exact run output is stored in `tests/test-report.txt`.

## 9. Benchmark interpretation

The benchmark is useful for regression, not ranking all CAM strategies. It uses one smooth height-field model, one ball tool, one tolerance set, one grid verifier, and Node's current JIT/runtime. Its main findings are:

- raster is the simplest coverage baseline;
- coverage-first hybrid improves sampled deviation but increases path length;
- surface-graph iso-spacing is compact on this example and produces the best sampled band percentage;
- the legacy slope-Eikonal field is retained for comparison, not as the recommended metric.

Re-run the benchmark after any numerical or path-linking change. Compare the JSON, G-code, and verification images, not only execution time.

## 10. Remaining limitations

1. **2.5D upper envelope.** Only the highest surface under each `(x,y)` is represented. Undercuts, vertical overlap, and inaccessible internal surfaces are outside the model.
2. **Three-axis, fixed tool axis.** The tool axis is +Z. There is no 3+2 or five-axis orientation planning.
3. **Limited cutter family.** Ball and flat end mills are supported. Bull/toroidal cutters, tapered tools, shanks, holders, and fixtures are absent.
4. **No exact-solid stock.** Roughing and verification use sampled CL fields and dexels rather than exact volumetric Boolean operations.
5. **Floating-point predicates.** Scale-aware tolerances improve behavior but do not provide exact-predicate guarantees.
6. **Uniform hash.** The spatial grid is effective for the intended examples but can be memory- or workload-imbalanced on highly nonuniform meshes. A BVH or kd-tree is the natural production replacement.
7. **Sampling-based collision checks.** Entry and linking checks can miss a feature narrower than the sample spacing.
8. **Approximate iso-spacing.** The surface-graph method discretizes geodesic distance on an eight-neighbor grid. It is neither rotation invariant at coarse resolution nor curvature/cutter-aware.
9. **Reference postprocessor.** Controller dialects differ. Arc centers, full circles, helical arcs, modal behavior, coordinate offsets, tool changes, spindle/coolant, and safety blocks require a machine-specific post.
10. **No dynamics.** Feed estimates use path length divided by nominal feed/rapid rates; acceleration, jerk, look-ahead, and controller blending are not modeled.

## 11. Reproduction commands

From the project root:

```bash
node tests/run-tests.mjs
node tests/probe-baseline.mjs
node tests/probe-fixed.mjs
node benchmarks/run-benchmarks.mjs
python -m http.server 8765
```

Then open `http://localhost:8765/visual_lab/` for the interactive visual laboratory.
