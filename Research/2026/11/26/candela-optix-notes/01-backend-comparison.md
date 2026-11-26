---
title: "Three ways Candela answers a ray query"
tags: [article, candela, optix, gpu, rendering]
type: article
status: published
created: 2026-11-26
repo: /home/manuel/code/wesen/go-go-golems/jig
ticket: JIG-030
---

# Three ways Candela answers a ray query

A pixel on the Singer hook can show a reflection of the studio strip light. Candela generates a camera ray, finds its first surface, evaluates the metal, samples lighting and accumulates an estimate of radiance. The backends agree on these operations because the scene compiler supplies a shared rendering program. They differ at a particularly expensive operation. Given a ray origin, direction, and maximum permissible distance, which eligible surface does the ray hit? The answer must carry enough information to shade the selected face. A shadow query asks the cheaper question of whether any eligible blocker lies before the light. The two questions permit different traversal algorithms.

This note describes the source inspected at Jig revision `af8a1e08` and the independently recorded GB10 experiments dated November 21–22, 2026. Timings below come from the archived experiments. No new device-speed measurements were taken for this comparison.

## Who executes each operation?

| Operation | WebGPU | Plain CUDA | OptiX |
|---|---|---|---|
| Generate a camera sample, evaluate materials, sample emitters, follow bounces | Candela WGSL compute shader | Candela’s translated shading functions | The translated Candela functions called inside its ray-generation program |
| Find the nearest mesh triangle | Candela traverses the object hierarchy and the mesh hierarchy in shader code | The translated software traversal over the same packed representation | OptiX traverses the instance and mesh acceleration structures. Candela’s closest-hit program returns information used by the shared shading code |
| Intersect custom analytical shapes | Candela’s shape routines | Translated Candela routines | OptiX bounds the search for bounded custom primitives, then invokes Candela’s intersection routine. Eligible spheres also have a built-in path |
| Intersect unbounded objects | Explicit loop | Translated loop | An explicit loop in the OptiX traversal shim |
| Accumulate radiance and auxiliary channels | Candela’s compute dispatch | Native CUDA entry point | Candela’s OptiX ray-generation entry point |
| Display the image | WebGPU compute passes | Native postprocessing over the accumulated output | Native postprocessing over the accumulated output, with optional OptiX AI denoising |

“Plain CUDA” and “OptiX” are options of the same native executable. Both use NVIDIA device code. In `targets/cuda.ts`, the plain target translates the shared shader including `traceAll`. For the OptiX target, the translator omits that function, includes a native tracing implementation in its place, and installs a ray-generation entry point. A WebGPU dispatch covers pixels in 8 × 8 workgroups. The plain CUDA entry point also computes pixel coordinates from its launch grid. On the OptiX target, `optixGetLaunchIndex()` supplies the pixel coordinates. All three paths reach Candela’s `renderPixel`. The author of a new metallic material can therefore implement sampling and evaluation in the shared layer. The author of a new primitive must also define how each backend can intersect it.

## Follow one triangle through the implementation

A mesh definition contains triangles, normals, texture coordinates and a relationship between each triangle and its original CAD face. An occurrence is an installed copy of that mesh with its own placement. When the metal hook rotates, it remains the same mesh occurrence viewed at a different placement.

In the software backend, `traceAll` searches the top-level bounding-volume hierarchy, a tree whose nodes enclose groups of objects. For a mesh candidate, `hitMesh` searches a second tree over its triangles. The compiler builds that mesh tree using an estimate of traversal cost based on surface area. For each triangle candidate, the shader computes distance and barycentric coordinates. The latter are weights locating a point relative to the triangle’s three vertices. The nearest admissible result supplies the object, triangle and interpolation data used by `finishHit`.

The OptiX backend builds a geometry acceleration structure for each mesh definition. Each mesh occurrence refers to its geometry through an instance. The triangle order in that geometry is deliberate. OptiX’s local primitive index selects the corresponding record in Candela’s packed triangle data. The closest-hit program obtains the instance ID, primitive index, barycentric coordinates and ray distance. The traversal shim translates these values into the representation expected by `finishHit`. The shared code can then interpolate normals and look up the face and material. A correct distance with an incorrect primitive-index mapping could produce the right silhouette while assigning the wrong finish to a face.

For direct lighting, Candela points a ray toward the sampled light with a finite distance limit. Its OptiX shim sets `OPTIX_RAY_FLAG_TERMINATE_ON_FIRST_HIT` for shadow rays and uses the shadow visibility mask. Once the surface-visibility question is settled, the integrator can still evaluate transmittance through a medium using `shadowTr`. Those are distinct operations. A software early-exit optimization must leave that medium contribution and the existing emitter-visibility rule intact. The software `occluded` currently obtains a closest-hit result with `traceAll(..., true)` and tests the returned object index.

## Frame evaluation and resource lifetime

The native command starts V8, evaluates the Candela engine bundle, reads the scene modules and constructs a headless scene session. When it renders a Jig track, `setSample` installs the film camera, occurrence matrices and optional emitter values and seeks the evaluated scene to the supplied time. The host uploads scene state after detecting a version change. The OptiX path also supplies the frame’s instances, shutter transforms and analytical bounds. It can reuse mesh structures across frames within a scene. Its current native frame builder allocates frame resources and builds acceleration structures with the build operation. Tracking each kind of change would allow a camera-only edit, a rigid joint movement and a topology-changing section cut to take different update paths.

During accumulation the host requests shader uniforms from V8 and launches the backend until it reaches the sample target. The reported native `renderMs` interval surrounds per-frame state evaluation, updates, launches and synchronization. A separate output interval includes postprocessing and writing the requested format. These timer boundaries matter when measuring a multi-stage Jig job that also transfers a file, draws CAD layers and later encodes a movie. A time recorded around the whole job cannot identify how long traversal took.

## What the GB10 measurements establish

The November 21 test used GB10 (sm_121), OptiX SDK 9.0.0, driver 580, and NVRTC 13.0. The following render-time comparison used 960 × 540, 256 samples per pixel, and disabled motion blur. The OptiX measurement used a maximum register count of 255. The last column is plain CUDA time divided by OptiX time. A ratio greater than one means the OptiX run finished sooner.

| Preset | WebGPU/Dawn | Plain CUDA | OptiX | CUDA time / OptiX time |
|---|---:|---:|---:|---:|
| B-01, Hello sphere | 516 ms | 141 ms | 422 ms | 0.33 |
| K-09, lockstitch head | 5,201 ms | 973 ms | 741 ms | 1.31 |
| X-02, ten thousand | 14,829 ms | 2,001 ms | 1,144 ms | 1.75 |
| V-04, cloud | 8,110 ms | 4,671 ms | 8,295 ms | 0.56 |

The comparison demonstrates scene dependence. These four rows alone cannot isolate a traversal or scheduling cost because the dispatch and machine code also change. One register experiment illustrates why. On K-09, a register limit of 168 yielded 1,474 ms, and 255 yielded 749 ms in the separate register sweep. V-04 took 8,126 ms at 168 and 8,295 ms at 255. The choice with a strong effect for K-09 had little benefit for the cloud. A general backend policy needs a workload corpus and separate measurements for cold startup and warm render throughput.

The current automatic-selection rule chooses OptiX for a scene containing meshes or more than 64 bounded analytical entries across custom shapes and built-in spheres. Shader execution reordering has a separate automatic rule that requires a mesh-free OptiX scene and more than 64 custom bounds. This distinction follows a later November 22 experiment. X-02 took 1,161 ms with custom primitives and reordering disabled. Introducing built-in spheres reduced the time to 845–859 ms with reordering disabled. Ratios from different generations of the renderer have to retain their revision or experimental context.

## Parity requires more than a visually similar image

In the historical parity sweep, 105 of 105 presets compiled to OptiX IR and created a module and pipeline. On the 64-spp, 320 × 180 image comparison, the recorded display-space 8 × 8 block metric fell within 2% of white for 104 of 105 presets. F-03 measured 2.9%. In X-03 a rare sun glint produced a reported linear block-relative RMSE of 584% alongside a display-space value of 0.34%. Spatial averaging and tone mapping change what an error metric exposes. Compilation success, radiometric agreement, CAD face identity and temporal stability each require their own checks.

The sphere experiment supplies a more direct counterexample. Replacing custom sphere intersections with a built-in primitive changed R-03’s image error to 19.42% in the recorded initial comparison. Inspection attributed the failure to rays starting inside a sphere in the tested built-in path. The compiler subsequently retained custom intersections for materials that allow paths to enter. Regression cases should consequently include origins inside solids, grazing rays, transparent and subsurface materials, and signed distances at shared triangle boundaries. Read the historical observation with its tested SDK, material configuration and renderer integration.

A useful common contract would replay recorded ray inputs independently of a whole film. Give closest-hit cases an interval, visibility class, time, and expected instance/face identity or allowed set at a geometric tie. Give shadow cases an expected Boolean result. Include the material, normal, and emitted-radiance checks in separate surface and image fixtures. Following a failing ray from payload to face lookup gives a maintainer a specific location to investigate.

## Source trail

All paths below are relative to the Jig repository root. The native code and browser renderer are both under `import/candela/`.

| Implementation or evidence | Source |
|---|---|
| Shared shading, software geometry and shadow queries | `import/candela/src/engine/kernel.ts` (`hitMesh`, `finishHit`, `traceAll`, `occluded`, `neeAt`, `renderPixel`) |
| Mesh hierarchy construction and WebGPU dispatch | `import/candela/src/engine/mesh.ts`, `import/candela/src/engine/render.ts` |
| Native target specialization and packed OptiX scene | `import/candela/src/engine/targets/cuda.ts`, `import/candela/src/engine/targets/optix.ts` |
| Native entry points and payload mapping | `import/candela/native/rt/kernels/candela_compute.cuh`, `candela_optix_programs.cuh`, `candela_traversal.inc` in the same directory |
| Device structures, target choice and timers | `import/candela/native/rt/src/optix_renderer.cpp`, `import/candela/src/engine/headless.ts`, `import/candela/native/rt/src/main.cpp` |
| Original benchmark and parity evidence | CANDELA-002 ticket, `various/16-phase3-optix.txt`, `various/22-ser.txt`, `various/23-builtin-spheres.txt` |

The complete CANDELA-002 directory is `ttmp/2026/11/21/CANDELA-002--fast-candela-rendering-on-the-dgx-spark-gpu-browser-native-webgpu-runner-optix-backend/`.

Related synthesis: [[ARTICLE - One path tracer, three ways to find a surface]].
