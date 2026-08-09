# Algorithm Textbook Creation

- URL: https://chatgpt.com/c/6a770ddc-8a24-83ea-9312-c18ef7195a59
- Created: 2026-08-08T11:07:09.073Z

---

> Extract the algorithms and fix them (you can run them), and then write a textbook (markdown and pdf) about the algorithms used and the  maths involved. It should be reasonably self-contained, and also reference the relevant books. Also take screenshots. Feel free to also cover algorithms that build up to the CAM algorithms and create intermediate visualizations / interactive tools (screenshots!) to make diagrams and illustrate the algorithms.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Preparing the implementation**

I’m identifying the required deliverables, then I’ll inspect the algorithms for boundary and numerical issues, separate reusable code from the interface, run tests, and produce the visualization, documentation, and screenshots.

**Prepared the implementation**

**Diagnosing algorithmic issues**

I’m focusing on three corrections: joining retained loop segments across the seam, preserving closed-loop behavior consistently, and replacing fixed sweeping passes with convergence-based iteration for more reliable solutions.

**Diagnosed algorithmic issues**

**Strengthening safety checks**

I’m reviewing path validation next. I’m checking endpoint and chord sampling, ramp clearance, interval-resolution limits, and whether narrow protected regions could be missed during roughing.

**Strengthened safety checks**

**Refining path generation**

I’m checking empty outputs, raster transitions, shallow-region truncation, hybrid step heuristics, mask-boundary crossings, and whether the distance field’s boundary conditions create unintended floor passes.

**Refined path generation**

**Inspected PDF skills and DropCut CAM JSX source structure**

**Searched geometry, mesh, distance, geodesic, and Eikonal methods**

</details>

```json
{"search_query":[{"q":"site:springer.com Choi Jerard Sculptured Surface Machining Theory and Applications book"},{"q":"site:springer.com Held Computational Geometry Pocket Machining book"},{"q":"fast sweeping method Eikonal equations Zhao 2005 paper PDF"},{"q":"asymptotic decider marching cubes Nielson Hamann 1991 paper"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 16 websites**

</details>

```unknown
bash -lc node --version && npm --version && python --version && which chromium || which chromium-browser || which google-chrome || true && which pandoc && which xelatex && which latexmk
```

<details><summary>💭 Thinking</summary>

**Checked installed tools, dependencies, and npm access**

</details>

```json
{"search_query":[{"q":"Van Hook real-time shaded NC milling display dexel 1986 paper"},{"q":"Pratt direct least squares fitting algebraic surfaces circle 1987 paper"},{"q":"Dijkstra 1959 note on two problems in connexion with graphs PDF"},{"q":"Lorensen Cline marching cubes 1987 paper ACM"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 30 websites**

</details>

```unknown
bash -lc set -e
ROOT=/mnt/data/dropcut_cam_deliverables
rm -rf "$ROOT"
mkdir -p "$ROOT"/{src,tests,web/vendor,screenshots,figures,benchmarks,build}
cp /mnt/data/dropcut-cam\(1\).jsx "$ROOT/src/dropcut-cam-original.jsx"
ls -R "$ROOT" | sed -n '1,120p'
```

<details><summary>💭 Thinking</summary>

**Organizing deliverables**

I’ll build a corrected, testable CAM core, interactive visualizations, screenshots, and a self-contained textbook in Markdown and PDF, while documenting approximations, mathematics, references, validation, and known limitations.

**Building and validating artifacts**

I’m moving from design to execution: I’ll test the core library first, then assemble the browser interface and educational lab, capture screenshots, benchmark representative jobs, and finish the textbook and PDF package.

**Organized deliverables and validated artifacts**

</details>

```unknown
bash -lc find /mnt/data/dropcut_cam_deliverables -maxdepth 3 -type f -printf '%p %s bytes
' | sort | sed -n '1,200p' && echo '---' && node --check /mnt/data/dropcut_cam_deliverables/src/dropcut-core.mjs
```

<details><summary>💭 Thinking</summary>

**Created DropCut CAM core, tests, convergence checks, and repaired interface defaults**

</details>

```json
{"open":[{"ref_id":"https://unpkg.com/react@18.3.1/umd/react.production.min.js"},{"ref_id":"https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js"},{"ref_id":"https://unpkg.com/three@0.160.1/build/three.min.js"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```unknown
bash -lc set -e
mkdir -p /mnt/data/dropcut_cam_deliverables/web/vendor
curl -L --fail --silent --show-error https://unpkg.com/react@18.3.1/umd/react.production.min.js -o /mnt/data/dropcut_cam_deliverables/web/vendor/react.production.min.js
curl -L --fail --silent --show-error https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js -o /mnt/data/dropcut_cam_deliverables/web/vendor/react-dom.production.min.js
curl -L --fail --silent --show-error https://unpkg.com/three@0.160.1/build/three.min.js -o /mnt/data/dropcut_cam_deliverables/web/vendor/three.min.js
wc -c /mnt/data/dropcut_cam_deliverables/web/vendor/*
```

<details><summary>💭 Thinking</summary>

**Downloaded React and Three.js dependencies**

</details>

```json
{"search_query":[{"q":"site:unpkg.com/react@18.3.1/umd/react.production.min.js"},{"q":"site:unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js"},{"q":"site:unpkg.com/three@0.160.1/build/three.min.js"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```json
{"search_query":[{"q":"registry.npmjs.org react 18.3.1 tarball"},{"q":"registry.npmjs.org react-dom 18.3.1 tarball"},{"q":"registry.npmjs.org three 0.160.1 tarball"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 15 websites**

</details>

```json
{"open":[{"ref_id":"https://registry.npmjs.org/react/-/react-18.3.1.tgz"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching 7 websites**

</details>

```json
{"search_query":[{"q":"react 18.3.1","domains":["registry.npmjs.org"]},{"q":"react-dom 18.3.1","domains":["registry.npmjs.org"]},{"q":"three 0.160.1","domains":["registry.npmjs.org"]}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

</details>

```unknown
bash -lc find /usr /opt /home/oai -type f \( -name 'react.production.min.js' -o -name 'react-dom.production.min.js' -o -name 'three.min.js' -o -name 'three.module.min.js' -o -name 'react.development.js' \) 2>/dev/null | head -100
```

<details><summary>💭 Thinking</summary>

**Searched filesystem and caches for React and Three.js files**

</details>

```json
{"open":[{"ref_id":"https://registry.npmjs.org/three/-/three-0.160.1.tgz"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching 8 websites**

</details>

```unknown
bash -lc cat > /mnt/data/dropcut_cam_deliverables/benchmarks/run-benchmarks.mjs <<'EOF'
import { performance } from 'node:perf_hooks';
import fs from 'node:fs';
import {
  PRESETS, heightfieldTris, buildModel, generateJob, verifyJob,
  buildGrid, makeEvaluator,
} from '../src/dropcut-core.mjs';

function params(overrides = {}) {
  return {
    roughOn: false,
    allowance: 0.25,
    stepdown: 2,
    roughStepPct: 55,
    entryMode: 'auto',
    rampAngle: 3,
    floorZ: 0,
    clearance: 4,
    margin: 0.8,
    direction: 'X',
    strategy: 'raster',
    scallop: 0.12,
    stepoverPct: 35,
    chordTol: 0.04,
    steepDeg: 35,
    arcFit: true,
    arcTol: 0.03,
    feed: 900,
    rpm: 12000,
    ...overrides,
  };
}

const cases = [
  { name: 'dome-raster', preset: { ...PRESETS.dome, n: 48 }, strategy: 'raster' },
  { name: 'dome-hybrid', preset: { ...PRESETS.dome, n: 48 }, strategy: 'hybrid' },
  { name: 'dome-surface-distance', preset: { ...PRESETS.dome, n: 48 }, strategy: 'scallop' },
  { name: 'hills-hybrid', preset: { ...PRESETS.hills, n: 44 }, strategy: 'hybrid' },
  { name: 'star-rough-hybrid', preset: { ...PRESETS.star, n: 40 }, strategy: 'hybrid', roughOn: true },
];

const tool = { type: 'ball', diameter: 4 };
const results = [];
for (const c of cases) {
  const model = buildModel(heightfieldTris(c.preset), 1, c.name);
  const prm = params({ strategy: c.strategy, roughOn: Boolean(c.roughOn) });
  const t0 = performance.now();
  const job = await generateJob(model, tool, prm);
  const ms = performance.now() - t0;
  const opCount = job.moves.reduce((sum, m) => sum + (m.ops?.length ?? m.pts.length / 3), 0);
  results.push({
    case: c.name,
    triangles: model.nTri,
    generation_ms: Number(ms.toFixed(2)),
    path_points: job.nPts,
    output_motion_records: opCount,
    arcs: job.stats.arc?.arcs ?? 0,
    fitted_lines: job.stats.arc?.lines ?? 0,
    rough_levels: job.stats.roughLevels,
    estimated_minutes: Number(job.stats.timeMin.toFixed(3)),
    path_length_mm: Number(job.stats.cutLenMM.toFixed(2)),
    description: job.stats.finDesc,
  });
}

// Spatial-grid query throughput on the 48x48 dome.
{
  const model = buildModel(heightfieldTris({ ...PRESETS.dome, n: 48 }), 1, 'dome-query');
  const grid = buildGrid(model, tool.diameter / 2);
  const evalF = makeEvaluator(model, grid, tool, 0);
  const samples = 50_000;
  let checksum = 0;
  let seed = 0x12345678;
  const rand = () => {
    seed ^= seed << 13; seed ^= seed >>> 17; seed ^= seed << 5;
    return (seed >>> 0) / 2 ** 32;
  };
  const t0 = performance.now();
  for (let k = 0; k < samples; k++) {
    const x = model.bbox.minX + (model.bbox.maxX - model.bbox.minX) * rand();
    const y = model.bbox.minY + (model.bbox.maxY - model.bbox.minY) * rand();
    checksum += evalF(x, y);
  }
  const ms = performance.now() - t0;
  results.push({
    case: 'drop-cutter-query-throughput',
    triangles: model.nTri,
    generation_ms: Number(ms.toFixed(2)),
    path_points: samples,
    output_motion_records: Math.round(samples / (ms / 1000)),
    arcs: 0,
    fitted_lines: 0,
    rough_levels: 0,
    estimated_minutes: 0,
    path_length_mm: 0,
    description: `${Math.round(samples / (ms / 1000)).toLocaleString()} exact queries/s; checksum ${checksum.toFixed(3)}`,
  });
}

// One end-to-end dexel verification case.
{
  const model = buildModel(heightfieldTris({ ...PRESETS.dome, n: 32 }), 1, 'dome-verification');
  const prm = params({ strategy: 'hybrid', roughOn: true, scallop: 0.16, stepdown: 3 });
  const job = await generateJob(model, tool, prm);
  const t0 = performance.now();
  const v = await verifyJob(job, model, prm, tool);
  const ms = performance.now() - t0;
  results.push({
    case: 'dome-dexel-verification',
    triangles: model.nTri,
    generation_ms: Number(ms.toFixed(2)),
    path_points: job.nPts,
    output_motion_records: v.stats.activeNodes,
    arcs: job.stats.arc?.arcs ?? 0,
    fitted_lines: job.stats.arc?.lines ?? 0,
    rough_levels: job.stats.roughLevels,
    estimated_minutes: Number(job.stats.timeMin.toFixed(3)),
    path_length_mm: Number(job.stats.cutLenMM.toFixed(2)),
    description: `verification RMS ${v.stats.rms.toFixed(4)} mm; min ${v.stats.minDev.toFixed(4)}; max ${v.stats.maxDev.toFixed(4)}; in-band ${v.stats.pctOK.toFixed(1)}%`,
  });
}

const outDir = new URL('.', import.meta.url).pathname;
fs.writeFileSync(`${outDir}/benchmark-results.json`, JSON.stringify(results, null, 2));
const headers = Object.keys(results[0]);
const esc = (v) => `"${String(v).replaceAll('"', '""')}"`;
fs.writeFileSync(`${outDir}/benchmark-results.csv`, [headers.join(','), ...results.map(r => headers.map(h => esc(r[h])).join(','))].join('\n') + '\n');
console.table(results);
EOF
node /mnt/data/dropcut_cam_deliverables/benchmarks/run-benchmarks.mjs | tee /mnt/data/dropcut_cam_deliverables/benchmarks/benchmark-output.txt
```

<details><summary>💭 Thinking</summary>

**Testing completed**

I’m consolidating the validated implementation, benchmarks, browser tools, screenshots, and documentation into a coherent deliverable set, while keeping the mathematical assumptions and verification limitations explicit.

**Tested completion status**

</details>

```unknown
bash -lc ls -R /mnt/data/dropcut_cam_deliverables | sed -e 's/.*//g' | head; find /mnt/data/dropcut_cam_deliverables -maxdepth 3 -type f -printf '%p %s bytes
' | sort
```

<details><summary>💭 Thinking</summary>

**Built and validated DropCut CAM algorithms, workbench, tests, figures, and textbook**

</details>

```json
{"search_query":[{"q":"Choi Jerard Sculptured Surface Machining 1998 Springer DOI"},{"q":"Martin Held On the Computational Geometry of Pocket Machining 1991 Springer Lecture Notes Computer Science 500"},{"q":"Nielson Hamann asymptotic decider 1991 paper DOI"},{"q":"Hongkai Zhao fast sweeping method Eikonal equations 2005 Mathematics of Computation DOI"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 34 websites**

</details>

```unknown
bash -lc cat >> /mnt/data/dropcut_cam_deliverables/Dropcut_CAM_Textbook.md <<'MD'
\newpage

# Appendix A - Algorithm reference

## A.1 Exact ball drop-cutter query

```text
BALL-DROP-CUTTER(X, Y, model, spatial-grid, R, floorZ)
    best-centre-height <- floorZ + R
    candidates <- triangles in grid cells touched by radius-R footprint

    for each distinct candidate triangle (a,b,c):
        reject if projected triangle bounding box is farther than R

        for vertex p in {a,b,c}:
            d2 <- (p.x-X)^2 + (p.y-Y)^2
            if d2 <= R^2:
                best <- max(best, p.z + sqrt(R^2-d2))

        for edge e in {(a,b),(b,c),(c,a)}:
            best <- max(best, exact projected edge support)

        if triangle is not vertical:
            write face plane z = A x + B y + C
            pxy <- (X,Y) + R(A,B)/sqrt(1+A^2+B^2)
            if pxy is inside projected triangle:
                best <- max(best, A X + B Y + C
                                  + R sqrt(1+A^2+B^2))

    return best - R
```

Implementation: `makeEvaluator`, `edgeBall`, and `pointInTri` in `src/dropcut-core.mjs`.

## A.2 Exact flat drop-cutter query

```text
FLAT-DROP-CUTTER(X, Y, triangle, R)
    best <- floorZ

    add heights of triangle vertices inside the radius-R disk

    for each projected edge:
        solve quadratic interval where edge lies inside disk
        add the higher feasible endpoint height

    if face is not vertical:
        compute disk support point in direction (A,B)
        if support point lies in triangle:
            add its plane height
        if (X,Y) lies in triangle:
            add plane height directly below centre

    return maximum candidate
```

## A.3 Cutter-location field

```text
BUILD-CL-FIELD(evaluate, [x0,x1] x [y0,y1], nominal-step)
    nx <- max(4, ceil((x1-x0)/nominal-step))
    ny <- max(4, ceil((y1-y0)/nominal-step))
    dx <- (x1-x0)/nx
    dy <- (y1-y0)/ny

    for j = 0..ny:
        for i = 0..nx:
            F[i,j] <- evaluate(x0+i*dx, y0+j*dy)

    compute centred finite differences GX, GY
    G <- sqrt(GX^2 + GY^2)
    return field with bilinear sampling functions
```

## A.4 Marching squares with asymptotic decider

```text
MARCHING-SQUARES(F, level)
    segments <- empty
    for each grid cell:
        subtract level from four corners
        create deterministic sign bits, symbolically breaking exact ties
        find linearly interpolated edge intersections

        if case is not ambiguous:
            emit the lookup-table segment
        else:
            q <- v00*v11 - v10*v01
            choose the two segment connections from sign(q)

        label every endpoint by its canonical shared grid-edge key

    chain unused segments through equal endpoint keys
    classify each chain as open or closed
    return polylines
```

## A.5 Fast sweeping for an isotropic Eikonal field

For

$$
|\nabla T|=F,
$$

with neighbour minima $a$ and $b$, the equal-grid update is

$$
T=\begin{cases}
\min(a,b)+Fh,&|a-b|\ge Fh,\\[3pt]
\dfrac{a+b+\sqrt{2(Fh)^2-(a-b)^2}}{2},&|a-b|<Fh.
\end{cases}
$$

The repaired implementation solves the corresponding rectangular-grid quadratic when $\Delta x\ne\Delta y$ and repeatedly applies four Gauss-Seidel sweep directions until convergence.

```text
FAST-SWEEP(F, boundary-values)
    initialise interior to infinity
    repeat:
        old-change <- 0
        for ordering in {(+x,+y), (-x,+y), (+x,-y), (-x,-y)}:
            visit all nodes in ordering
            compute upwind local update
            T <- min(T, update)
            record maximum decrease
    until maximum decrease < tolerance or cycle limit reached
```

## A.6 Surface-distance contours

```text
SURFACE-DISTANCE(F, nominal-spacing s0)
    create graph node p_ij = (x_i, y_j, F_ij)
    connect 4 or 8 grid neighbours
    edge weight = Euclidean 3D chord length / s0
    use all boundary nodes as zero-distance sources
    run multi-source Dijkstra
    extract integer level sets with marching squares
    lift and adaptively refine every contour against exact CL evaluator
```

## A.7 Roughing intervals

```text
FIND-LEVEL-INTERVALS(g, lo, hi, z, scan-step)
    evaluate inside(a) := g(a) <= z
    scan from lo to hi
    whenever inside changes:
        bisect the transition
        open or close an interval
    discard intervals below minimum width
    return intervals
```

Rows of intervals are grouped by union-find when adjacent-row intervals overlap.

## A.8 Arc compression

```text
COMPRESS-CUT(points, tolerance)
    partition the polyline into maximal runs in one controller plane
    for each sufficiently long run:
        grow a least-squares circle fit
        enforce endpoint bisector constraint
        check radius, radial residuals, monotone angular direction, sweep
        emit the longest last-good arc; otherwise emit one line
```

## A.9 Dexel verification

```text
VERIFY(job, target-mesh, tool)
    create exact rectangular dexel grid
    H <- initial stock top
    T <- floor

    rasterise upper target triangles into T

    for each nonrapid segment:
        sample segment with step tied to grid pitch
        for every cutter placement:
            for nodes inside cutter footprint:
                H[node] <- min(H[node], tipZ + cutter-profile(radius))

    deviation <- H - T
    compute min, max, RMS, and diagnostic-band percentage
    only on nodes belonging to the part
```

# Appendix B - Parameter guide

| Parameter | Meaning | Numerical effect | Practical caution |
|---|---|---|---|
| Tool type | ball or flat | selects contact and footprint formula | must match physical tool geometry |
| Diameter | cutter diameter | contact offset, roughing row step, verifier footprint | positive; verify actual measured diameter |
| Scale | model unit multiplier | all geometry | STL has no unit metadata |
| Floor Z | minimum machinable/reference plane | initial contact and roughing bottom | not a fixture or stock model |
| Margin | extra XY field around bounds | raster extent and verification grid | increases air cutting and memory |
| Clearance | rapid plane above model | link/retract height | must clear stock, clamps, holder; code cannot prove this |
| Stepdown | roughing layer depth | number of rough levels | process-dependent; not geometrically optimised |
| Rough stepover % | row spacing as diameter fraction | coverage and time | too large leaves ridges |
| Allowance | material left for finishing | inflated-tool field | approximate normal allowance |
| Entry mode | auto, ramp, or plunge | transition geometry | tool/material capability is not modelled |
| Ramp angle | descent angle | entry length and load | consult tool data |
| Strategy | raster, hybrid, surface-distance | path topology | no strategy is universally best |
| Scallop | flat-plane nominal cusp for ball tool | computes $s_0$ | not a curved-surface guarantee |
| Stepover % | flat-tool nominal spacing | coverage | ideal flat tool leaves step discontinuities at edges |
| Chord tolerance | midpoint height deviation threshold | point density and path fidelity | output rounding and CL-grid error also matter |
| Steep angle | hybrid slope threshold | shallow/steep partition, waterline step | based on sampled CL slope |
| Arc fitting | enable circle replacement | smaller G-code | controller-specific verification required |
| Arc tolerance | radial residual threshold | arc count and geometric error | must exceed output quantisation and noise |
| Feed | nominal cutting feed | estimated time and G-code | no engagement or acceleration scheduling |
| RPM | spindle command | G-code only | no material/tool database |
| Dexel pitch | internally selected verification grid | detection resolution and runtime | sampled diagnostic only |

# Appendix C - Exercises and projects

## C.1 Analytic contact

1. Derive the ball-cutter plane formula by maximising
   $$Ax+By+C+\sqrt{R^2-(x-X)^2-(y-Y)^2}-R.$$
2. Derive the flat-cutter plane formula as a disk support function.
3. Show that both formulas reduce to the plane height when $A=B=0$.
4. For small slope, expand the ball offset term through fourth order in $A^2+B^2$.

## C.2 Robust predicates

1. Implement an adaptive orientation predicate and replace the scaled epsilon in `pointInTri`.
2. Construct a triangle/query family for which a fixed absolute epsilon changes classification under uniform scaling.
3. Design a test for a contour passing exactly through a grid vertex and compare four tie-breaking policies.

## C.3 Marching squares

1. Derive the asymptotic-decider determinant from a bilinear function
   $$f(u,v)=a+bu+cv+duv.$$
2. Prove that canonical grid-edge keys agree across neighbouring cells.
3. Extend the contour chainer to report nonmanifold degree-$>2$ endpoints rather than selecting an arbitrary next segment.
4. Add Douglas-Peucker simplification followed by exact CL lifting, and quantify the error.

## C.4 Surface metrics

1. Verify that $g=I+\nabla f\nabla f^T$ has eigenvalues $1$ and $1+|\nabla f|^2$.
2. Identify the corresponding eigenvectors and explain their geometric meaning.
3. Compare Euclidean planar distance, graph-grid Dijkstra distance, and analytic surface distance on a constant-slope plane.
4. Implement fast marching on a triangulated graph surface and compare rotational anisotropy with the 8-neighbour grid.

## C.5 Scallop models

1. Derive the exact flat-plane scallop formula in Figure \ref{fig:scallop}.
2. Numerically machine a cylinder using raster passes parallel and perpendicular to its axis. Explain why identical planar stepovers produce different scallops.
3. Estimate normal curvature from the Hessian of a graph surface and design a local curvature-aware spacing rule. State clearly which approximations are used.

## C.6 Verification

1. Repeat the dome verification at three dexel pitches and plot RMS, minimum, and maximum deviation against pitch.
2. Replace point-sampled segment sweeping with adaptive subdivision based on tool-placement displacement.
3. Parse emitted G2/G3 arcs and verify them directly rather than verifying their pre-fit polylines.
4. Extend the heightfield dexel to a multi-dexel representation that can store several material intervals per column.

## C.7 Software engineering

1. Replace the uniform spatial hash with a BVH and benchmark both on uniform and highly clustered meshes.
2. Add property-based tests that generate random tilted planes and compare exact formulas.
3. Add deterministic snapshot tests for G-code modal transitions.
4. Build a controller-specific postprocessor interface rather than embedding one dialect in `toGcode`.

# Appendix D - Implementation map

| Function | File and approximate lines | Role |
|---|---|---|
| `heightfieldTris` | `src/dropcut-core.mjs:90` | triangulates analytic presets |
| `parseSTL` | `src/dropcut-core.mjs:134` | binary/ASCII STL import |
| `buildModel` | `src/dropcut-core.mjs:195` | normalisation and bounds |
| `buildGrid` | `src/dropcut-core.mjs:235` | projected spatial hash |
| `pointInTri` | `src/dropcut-core.mjs:277` | projected triangle predicate |
| `edgeBall` | `src/dropcut-core.mjs:291` | exact ball-edge support |
| `makeEvaluator` | `src/dropcut-core.mjs:315` | exact ball/flat drop-cutter closure |
| `buildCLField` | `src/dropcut-core.mjs:446` | sampled CL field and gradients |
| `bilin` | `src/dropcut-core.mjs:493` | exact-domain bilinear interpolation |
| `marchSquares` | `src/dropcut-core.mjs:533` | contour extraction and chaining |
| `splitByMask` | `src/dropcut-core.mjs:689` | mask clipping with seam repair |
| `solveEikonal` | `src/dropcut-core.mjs:767` | converged rectangular fast sweeping |
| `solveSurfaceDistance` | `src/dropcut-core.mjs:868` | graph-metric multi-source Dijkstra |
| `validateParameters` | `src/dropcut-core.mjs:914` | central input checks |
| `emitEntry` | `src/dropcut-core.mjs:956` | helix/ramp/plunge entry |
| `generateJob` | `src/dropcut-core.mjs:1078` | roughing, finishing, linking, flattening |
| `compressCut` | `src/dropcut-core.mjs:1640` | plane-run segmentation for arcs |
| `fitArcsRun` | `src/dropcut-core.mjs:1664` | bounded-error circle fitting |
| `toGcode` | `src/dropcut-core.mjs:1761` | modal G-code postprocessor |
| `verifyJob` | `src/dropcut-core.mjs:1852` | dexel target and swept-stock comparison |

# Bibliography

1. Botsch, M., Kobbelt, L., Pauly, M., Alliez, P., and Levy, B. *Polygon Mesh Processing*. A K Peters, 2010.
2. Choi, B. K., and Jerard, R. B. *Sculptured Surface Machining: Theory and Applications*. Kluwer Academic / Springer, 1998. DOI: 10.1007/978-1-4615-5283-3.
3. Crane, K. *Discrete Differential Geometry: An Applied Introduction*. Course notes, version dated 29 January 2025.
4. de Berg, M., Cheong, O., van Kreveld, M., and Overmars, M. *Computational Geometry: Algorithms and Applications*. 3rd ed., Springer, 2008.
5. Dijkstra, E. W. "A Note on Two Problems in Connexion with Graphs." *Numerische Mathematik* 1 (1959): 269-271. DOI: 10.1007/BF01386390.
6. Held, M. *On the Computational Geometry of Pocket Machining*. Lecture Notes in Computer Science 500, Springer-Verlag, 1991. DOI: 10.1007/3-540-54103-9.
7. Kobayashi, S. *Differential Geometry of Curves and Surfaces*. Springer Undergraduate Mathematics Series, Springer Nature Singapore, 2019. DOI: 10.1007/978-981-15-1739-6.
8. Lorensen, W. E., and Cline, H. E. "Marching Cubes: A High Resolution 3D Surface Construction Algorithm." *ACM SIGGRAPH Computer Graphics* 21(4) (1987): 163-169. DOI: 10.1145/37402.37422.
9. Nielson, G. M., and Hamann, B. "The Asymptotic Decider: Resolving the Ambiguity in Marching Cubes." *Proceedings Visualization '91* (1991): 83-91. DOI: 10.1109/VISUAL.1991.175782.
10. Pratt, V. "Direct Least-Squares Fitting of Algebraic Surfaces." *ACM SIGGRAPH Computer Graphics* 21(4) (1987): 145-152. DOI: 10.1145/37402.37420.
11. Sethian, J. A. *Level Set Methods and Fast Marching Methods*. 2nd ed., Cambridge University Press, 1999.
12. Van Hook, T. "Real-Time Shaded NC Milling Display." *ACM SIGGRAPH Computer Graphics* 20(4) (1986): 15-20. DOI: 10.1145/15886.15887.
13. Zhao, H. "A Fast Sweeping Method for Eikonal Equations." *Mathematics of Computation* 74(250) (2005): 603-627. DOI: 10.1090/S0025-5718-04-01678-3.
14. Crane, K., Weischedel, C., and Wardetzky, M. "Geodesics in Heat: A New Approach to Computing Distance Based on Heat Flow." *ACM Transactions on Graphics* 32(5), 2013.

# Colophon

The mathematical exposition was written from the supplied source code and the listed references. All diagrams in `figures/` and all browser screenshots in `screenshots/` were generated from the repaired implementation or from independent plotting scripts included with the deliverables. No screenshot is a photograph of a physical machining result.
MD
wc -w /mnt/data/dropcut_cam_deliverables/Dropcut_CAM_Textbook.md
wc -l /mnt/data/dropcut_cam_deliverables/Dropcut_CAM_Textbook.md
```

<details><summary>💭 Thinking</summary>

**Compiled and validated CAM textbook PDF and simulation deliverables package**

</details>

```json
{"paths":["files"]}
```

# Deliverables

- **Complete source, tests, benchmarks, figures, screenshots, visual lab, G-code examples, and documentation:** [Download the complete package](sandbox:/mnt/data/dropcut_cam_fixed_package.zip)
- **103-page textbook PDF:** [Download the PDF](sandbox:/mnt/data/dropcut_cam_textbook.pdf)
- **Textbook Markdown source:** [Download the Markdown](sandbox:/mnt/data/dropcut_cam_textbook.md)
- **Algorithm audit and repair record:** [Download the audit](sandbox:/mnt/data/dropcut_cam_algorithm_audit.md)
- **Repaired React/Three.js application:** [Download dropcut-cam-fixed.jsx](sandbox:/mnt/data/dropcut-cam-fixed.jsx)
- **Extracted dependency-free algorithm core:** [Download dropcut-core.mjs](sandbox:/mnt/data/dropcut-core.mjs)
- **Baseline-to-repaired unified diff:** [Download the patch](sandbox:/mnt/data/dropcut_cam_fixed/dropcut-core.patch)

The original source advertised helix/ramp entries, hybrid raster-waterline finishing, an Eikonal-based constant-scallop strategy, dexel verification, and G17/G18/G19 arc fitting. Those features were extracted into an independently runnable core rather than treated only as UI code. fileciteturn0file0L5-L17

## Main repairs

The most consequential defect was in arc fitting: many cut moves stored only destinations after the current machine position, but the compressor did not prepend that incoming position. The baseline probe found **23 arc-fitted moves whose first cutting segment disappeared from exported G-code**. The repaired arc stream preserves all incoming segments.

Other repairs include:

- coverage-first hybrid finishing, replacing the shallow/steep partition that left sampled uncut islands;
- bilinear asymptotic-decider handling for marching-squares cases 5 and 10;
- correct cyclic mask splitting across a closed contour’s storage seam;
- rectangular-cell, convergence-based fast sweeping;
- a surface-graph distance method using actual lifted 3D edge lengths;
- explicit terminology distinguishing approximate constant surface spacing from exact cutter-aware constant scallop;
- full-path validation for helix and ramp entries;
- quarter/midpoint/three-quarter adaptive refinement;
- exact CL reevaluation and safe raising of constant-Z contours;
- explicit `G91.1`, finite-coordinate validation, comment sanitization, and corrected G17/G18/G19 direction mapping;
- move-aware dexel simulation of the fitted/exported path;
- exact upper-envelope target evaluation and part-mask-only deviation statistics;
- separate cancellation state for generation and verification.

The mathematical treatment uses the first fundamental form and graph-surface metric from classical differential geometry, including induced curve length and surface coefficients. fileciteturn2file1L129-L218 It connects these smooth constructions to Crane’s computational treatment of differentials and induced metrics. fileciteturn3file2L118-L152 Triangle meshes are treated as piecewise-linear surfaces, with STL explicitly handled as a face-set or triangle-soup representation. fileciteturn4file0L19-L45 The robustness discussion follows the computational-geometry distinction between degeneracies, primitive predicates, floating-point consistency, and exact arithmetic. fileciteturn5file1L64-L115

## Validation

The executable Node test suite currently reports:

```text
14/14 tests passed in 0.38 s
```

[Test report](sandbox:/mnt/data/dropcut_cam_fixed/tests/test-report.txt)  
[Baseline defect probe](sandbox:/mnt/data/dropcut_cam_fixed/tests/probe-baseline-report.txt)  
[Repaired probe](sandbox:/mnt/data/dropcut_cam_fixed/tests/probe-fixed-report.txt)  
[Benchmark results](sandbox:/mnt/data/dropcut_cam_fixed/benchmarks/benchmark-results.json)

The benchmark covers raster, coverage-first hybrid, surface-graph iso-spacing, and the retained legacy slope-Eikonal method. The three verified strategies report approximately **99.03%, 99.41%, and 99.84%** of sampled part-mask nodes inside their respective diagnostic bands. These are regression measurements for the included model and sampled verifier, not universal machining-accuracy guarantees.

The final PDF was rendered at 130 dpi and inspected across all 103 pages for clipping, overlap, missing figures, broken equations, and glyph failures.

## Interactive material and screenshots

The standalone laboratory requires no external JavaScript packages:

[Open the interactive visual laboratory](sandbox:/mnt/data/dropcut_cam_fixed/visual_lab/index.html)

Captured scenes:

[Triangle/cutter contact](sandbox:/mnt/data/dropcut_cam_fixed/screenshots/visual_lab_contact.png) ·
[Marching squares](sandbox:/mnt/data/dropcut_cam_fixed/screenshots/visual_lab_marching.png) ·
[Ball scallop geometry](sandbox:/mnt/data/dropcut_cam_fixed/screenshots/visual_lab_scallop.png) ·
[Surface metrics](sandbox:/mnt/data/dropcut_cam_fixed/screenshots/visual_lab_metric.png) ·
[Dexel verification](sandbox:/mnt/data/dropcut_cam_fixed/screenshots/visual_lab_dexel.png)

The package also contains 21 generated textbook figures and four reference G-code programs.

## Operational limitation

This remains a three-axis, fixed-vertical-axis, 2.5D upper-envelope reference. It does not model undercuts, shanks, holders, fixtures, machine kinematics, controller dynamics, or an exact continuous stock solid. The G-code must be checked with a machine-specific postprocessor and independent simulator, then dry-run and proven out under supervision.

