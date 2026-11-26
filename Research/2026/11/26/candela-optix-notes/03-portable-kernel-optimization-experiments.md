---
title: "Portable kernel optimization experiments"
tags: [article, candela, optix, gpu, rendering]
type: article
status: published
created: 2026-11-26
repo: /home/manuel/code/wesen/go-go-golems/jig
ticket: JIG-030
---

# Portable kernel optimization experiments

Consider a pixel on the Singer hook as a strip light crosses the metal. Candela may send a camera ray toward the hook, choose a light sample, and send a second ray toward that point on the strip. The camera query needs the distance, occurrence, face and local surface coordinates of the nearest hit. The second query asks whether any eligible surface blocks a finite segment. Those requests have different output requirements. They constitute a particularly tractable starting point for improving both the browser WGSL implementation and its plain-CUDA translation.

This note is a source inspection and experimental design. The historic measurements cited below come from Candela's recorded Spark runs. The proposed kernel changes have no measured speedups yet. All repository paths are relative to the Jig checkout at `/home/manuel/code/wesen/go-go-golems/jig`.

## 1. Distinguish closest intersection from finite-segment visibility

In `import/candela/src/engine/kernel.ts`, `traceAll` searches unbounded objects and walks a binary tree over bounded objects. Each node encloses all its children in an axis-aligned bounding box. Missing that box skips the entire branch. For a mesh occurrence, `hitObj` transforms the ray into object coordinates and calls `hitMesh`, which walks a second tree over that mesh's triangles. A successful closest triangle records a triangle address and barycentric coordinates, the weights used to interpolate attributes across the triangle. Only after traversal does `finishHit` resolve the selected triangle's normal, UV coordinates, face and material. The current software path already defers most shading work.

The software `occluded` entry calls `traceAll(ro, rd, tmax, true)` and returns whether the result identifies an object. The flag filters glowing objects that the shadow convention excludes. The two tree walks still seek the closest intersection. A first prototype can terminate at the first accepted blocker in an unbounded object, bounded analytic primitive or mesh triangle. The following example is proposed control flow.

```text
if object is excluded by shadow visibility:
    continue
if object is a mesh:
    transform the ray using the occurrence and shutter time
    if a triangle satisfies the original intersection and interval tests:
        return blocked
else if its existing primitive test returns a qualifying distance:
    return blocked
continue until all reachable candidates are exhausted
return clear
```

Returning early only from the scene loop would still traverse a dense mesh to find its closest triangle. Returning at the first box intersection would produce false shadows. Preserve ray start offsets and endpoint handling, the unbounded-object loop, geometric transforms, and tests for degenerate triangles. Direct lighting in `neeAt` separately evaluates medium transmittance after the visibility query succeeds. Early termination applies to the binary surface query. Transmittance integration keeps its separate numerical behavior.

Candela's native target selector in `import/candela/src/engine/targets/cuda.ts` tells the translator to omit WGSL's `traceAll` for OptiX. A C++ device implementation supplies that operation using `optixTrace` and a terminate-on-first-hit flag for shadow rays. Putting a separate WGSL traversal directly inside `occluded` would bypass that existing substitution on the OptiX target. Either specialize the portable walk inside the existing boundary or explicitly introduce corresponding closest/occlusion entries on every target. For the first experiment, use a generated-code check and execution counters to verify that the native shadow path still dispatches hardware traversal. [OptiX traversal source](https://github.com/go-go-golems/jig/blob/main/import/candela/native/rt/kernels/candela_traversal.inc)

## 2. Separate node order, tree construction and scene updates

Both software walks push consecutive left and right child indices in a fixed order and pop the last one first. When a nearer child yields a hit, its distance shortens the interval that subsequent boxes must overlap. Visiting the nearer child first could therefore reduce triangle tests. Modify the existing slab intersection to return the entry distance as well as overlap, then test the children and push the farther surviving child first. A second variant uses a cheap child-order approximation based on split axis and ray direction if the builder stores the axis. Compare these separately. Extra bound reads, duplicate box tests on pop, or an increase in local stack pressure can outweigh a reduction in visited triangles. [PBRT's bounding-volume hierarchy implementation](https://pbr-book.org/4ed/Primitives_and_Intersection_Acceleration/Bounding_Volume_Hierarchies)

Tree *construction* is a separate variable. `compile.ts::buildBVH` splits bounded occurrences at the median along the widest range of centroid coordinates, with up to three occurrences per leaf. `mesh.ts::blasOf` already builds and caches a mesh-local tree using 12-bin surface-area splits and a small-leaf decision. Changing the top-level builder to use a binned surface-area cost is a candidate for many-occurrence scenes. It would add build work during a repack. A moving assembly also admits a cheaper experiment: retain a compatible occurrence tree, update transformed leaf bounds, and propagate bounds to its root. Compare rebuild, refit, and occasional rebuild after extensive motion using **total pack plus traversal time**, including bounded and unbounded objects. Maintain a stable mapping from occurrence identity to its physical data row. The current packer orders object rows by leaf order and remaps dependent records. A changed ordering can otherwise give a correct distance with an incorrect exposed component ID.

Node storage also has a correctness constraint. The shader declares local stacks of 40 indices in the scene walk and 48 in the mesh walk. It conditionally suppresses pushes near those capacities. Restricting builder depth, proving a bound, or using an overflow strategy are possible solutions when experimenting with new tree layouts. Measure high-water depth with deliberately unbalanced mesh inputs. A traversal that drops children under pressure can appear very fast. The reference image and ray checks must establish completeness.

## 3. Test the triangle data layout independently

A software triangle occupies seven four-float records, or 112 bytes. During intersection the code references its base vertex and two edge vectors in the first three records. The final four records supply attributes including shading normals and UV components after a winner is known. This distinction concerns the addresses the source references. Actual GPU memory traffic depends on caching, compiler transformations and the platform.

Compare the current layout with dense intersection records for triangles plus separate shading attributes indexed by stable triangle identity. Measure memory throughput and ray time for coherent camera rays and for divergent glossy bounces. Include the cost of packing or uploading both layouts. The native OptiX target reconstructs triangle vertices from these same packed records and uses the primitive index to find the shading record. Changing the stride without updating this translation would silently damage face IDs, face-specific materials or interpolated normals. Test each with a mesh having adjacent triangles of distinct materials. The relevant routines are `hitMesh` and `finishHit` in `kernel.ts` and `verticesOf` in `src/engine/targets/optix.ts`.

## 4. Make expensive shader changes earn their complexity

The generated pixel program handles camera, direct-light and bounce rays as well as different materials and media. Secondary rays can diverge into different code paths. A proposed wavefront path tracer would record pending path state in GPU queues and run selected categories of work together. It could reduce divergent execution or register pressure in a measured workload. Its queue reads, writes and synchronization consume bandwidth and dispatch time. First test a narrow split, such as deferring shadow visibility for one direct-light contribution per path. Include camera-only and low-depth workloads in the comparison. Record register use, spills, kernel time, queue occupancy and total produced-frame time. [PBRT on mapping path tracing to a GPU](https://pbr-book.org/4ed/Wavefront_Rendering_on_GPUs/Mapping_Path_Tracing_to_the_GPU)

Candela has a directly relevant caution from hardware shader execution reordering. In the archived OptiX 9.0 GB10 experiment at 960 × 540 and 256 spp, reordering increased K-09 mesh time from 911 ms to 1130–1148 ms, while X-02's procedural workload improved from 1154 ms to 911 ms. Those figures measure NVIDIA's reordering primitive in the recorded implementations. They do not predict the effect of a portable queue. They justify collecting materially different scene classes before setting a default. See CANDELA-002, `various/22-ser.txt` and the later `23-builtin-spheres.txt`, under `ttmp/2026/11/21/`.

## 5. Control the statistical experiment

Throughput at fixed samples per pixel and time to a chosen noise level answer different questions. Candela's `renderPixel` seeds a pseudorandom stream from the pixel, dispatch index and seed. Shutter stratification and spectral sampling also use the sample index local to the batch. Batching 2048 samples into groups of 1, 4, 8 or 16 can reduce GPU launch overhead while changing the actual paths traced. Compare the mean of linear-radiance estimates over multiple seeds to an independent longer reference. Test moving geometry with motion blur as well as static RGB mode. An eventual sample-range API could address rays by logical frame, pixel and absolute sample index for progressive resumption.

A separate experiment can improve the distribution of direct-light samples. The present `neeAt` chooses uniformly among scene lights, sun and environment; the environment itself can be importance-sampled. Try a mixture of power-weighted light selection and a uniform component that retains support for weak emitters. Update the selection probability in direct samples, emissive hits and environment misses wherever it enters the multiple-importance weights. Otherwise selection and evaluation describe different distributions. The key/fill/rim studio is a small, inspectable test. Exchange two light IDs, fade one light to zero, and place a dim light very close to the subject. Measure both mean radiance and the time to resolve the moving reflection across frames. [PBRT on selecting lights and evaluating their probabilities](https://pbr-book.org/4ed/Light_Sources/Light_Sampling)

## 6. Establish the ray contract before timing a candidate

Use hand-computed rays on elementary fixtures, GPU replay on baseline and candidate paths, and representative rendered scenes. These levels catch different errors.

| Fixture | Assertion | Failure it detects |
|---|---|---|
| A ray aimed at a finite strip-light sample, with a triangle before or beyond the endpoint | Only the in-range triangle blocks | A blocker behind the light, or a returned bounding-box hit |
| A glowing occurrence in front of an ordinary blocker | The shadow ignores the glowing occurrence and still finds the ordinary one | Premature exit before applying the query mask |
| A rigidly moving mesh at several shutter times, including nonuniform static scaling | Hit distance in scene ray parameters, stable face and surface point within a declared tolerance | Incorrect ray transform, direction normalization or motion bounds |
| Two neighboring triangles sharing an edge; a coplanar overlap | Unique interior hits agree on face ID. Record accepted tie sets and hit-position tolerance for ambiguous rays | A traversal-order change mistaken for a changed silhouette or shading |
| Nested bounds, degenerate triangles and nearly axis-parallel rays | Agreement with a brute-force primitive walk for unambiguous cases; record maximum pending-node depth | Stack truncation, invalid slab math or missed close intersections |
| A Singer hook close-up, open cut, wide view and moving reflection | Stable subject masks, depth, face appearance and readable clearance where visible | Correct single-ray answers with wrong attribute decoding or temporal placement |

Capture each replay ray's origin, direction, extent, shutter time, query type and mask, plus the scene revision. Compare visible occurrence IDs in the stable application namespace, since BVH leaf order can change packed indices. For timings, separate recording from replay. Record node visits and candidate tests in diagnostic builds, then remove counters for the timed run. Record both resolution and sample count, whether kernels and assets were warm, fixed scene and camera identities, and per-scene spread over repeated runs. The existing golden pack tests protect compiled scene representation. Ray replay and per-frame evaluation cover traversal and image behavior.

The first bounded deliverable is a reproducible ray corpus and an early-exit shadow implementation. A faster software result on Singer deserves to ship when it also preserves ray semantics on the fixtures and reports its measured costs on small analytic, mesh-heavy and divergent workloads. The further experiments remain independently testable and can be selected using where time is actually spent.

Related synthesis: [[ARTICLE - One path tracer, three ways to find a surface]].
