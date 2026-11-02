---
title: "Mathematics - Computational Geometry"
aliases:
  - "Computational geometry"
  - "Geometric algorithms"
  - "Delaunay"
  - "Plane sweep"
tags:
  - knowledge-base
  - mathematics
  - geometry
  - algorithms
status: active
type: knowledge-base
created: "2026-11-02"
---

# Computational Geometry

Computational geometry designs and analyzes algorithms on geometric input: intersections, arrangements, triangulations, meshes. Its distinctive concerns are combinatorial correctness under degenerate input and exact decisions (predicates) separate from computed coordinates (constructions).

Part of [[Mathematics]].

> [!summary]
> - A predicate returns a discrete fact (left, right, on); a construction returns coordinates. Algorithms should branch only on predicates.
> - Plane sweep turns geometry into changing adjacency; the DCEL stores the resulting subdivision with faces that can be labeled.
> - Delaunay triangulations satisfy the empty-circle criterion and maximize the minimum angle; quality refinement adds Steiner points and needs a termination proof.

## Concepts

- Orientation and in-circle predicates as determinant signs.
- Segment intersection and degeneracy; plane sweep; arrangements and DCEL overlays; profile extraction.
- Delaunay triangulation, edge flips, the lifting map to a paraboloid, constrained triangulation, refinement.
- Tetrahedral mesh quality: radius–edge ratio, dihedral angles, signed volume, slivers.
- Mesh simplification by edge contraction; quadric error metrics.
- Scanline rasterization, winding numbers and fill rules.

## In the CAD textbook

[[Course - Engineering CAD from First Principles]] treats this topic in:

- [[Engineering CAD 09 - Reliable decisions in planar geometry|Chapter 9. Reliable decisions in planar geometry]]: predicates versus constructions, segment intersection, arrangements and DCELs.
- [[Engineering CAD 10 - From planar curves to valid profiles|Chapter 10. From planar curves to valid profiles]]: from planar curves to valid profiles.
- [[Engineering CAD 14 - B-rep, STEP, meshes and manufacturing|Chapter 14. B-rep, STEP, meshes and manufacturing]]: meshes, mass properties and round-trip tests.
- [[Engineering CAD 26 - Predicates, constructions and symbolic perturbation|Chapter 26. Predicates, constructions and symbolic perturbation]]: predicates, filters and symbolic perturbation.
- [[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction|Chapter 27. Plane sweep, DCEL overlays and profile extraction]]: plane sweep, DCEL overlays and profile extraction.
- [[Engineering CAD 28 - Delaunay triangulation and quality refinement|Chapter 28. Delaunay triangulation and quality refinement]]: Delaunay triangulation and quality refinement.
- [[Engineering CAD 30 - Tetrahedral quality and topology-safe simplification|Chapter 30. Tetrahedral quality and topology-safe simplification]]: tetrahedral quality and topology-safe simplification.

## Elsewhere in the vault

### Projects and articles

- [[ARTICLE - TTF Rasterizer Bug Hunting - Scale, Windings, and Coverage]]: scanline rasterization: winding values, span coverage, fill rules.
- [[Research/Institute/Magazine/Issues/002/03 - From Outline to Pixel|From Outline to Pixel (magazine)]]: nonzero winding and why glyph counters filled with gray.
- [[ARTICLE - M5Dial Proper 3D Renderer - Building a Z-Buffered Planet and Terrain on ESP32-S3]]: triangle rasterization with a z-buffer on a microcontroller.
- [[PROJ - ABS Bicolor V-Engraver - From Single-File Artifact to Multi-Tool CAM Pipeline]]: polygon offsets and V-carve toolpaths from outlines.
- [[PROJ - DROPCUT Studio - A CAM Compiler Where G-Code Is Just A Backend]]: a CAM compiler built on drop-cutter geometry over triangle meshes.

### CAM research and textbooks (transcript artifacts)

- [[dropcut_cam_textbook]]: drop-cutter over triangle meshes, waterlines, marching squares, fast sweeping, dexel verification.
- [[Transcripts/2026/08/08/Algorithm Textbook Creation/dropcut_cam_algorithm_audit|Dropcut algorithm audit]]: boundary defects in that geometry code: degenerate projections, closed-loop seams, coverage guarantees.
- [[Transcripts/2026/08/16/Z1 Controller Review/Certificate_Carrying_CAM_Compilers|Certificate-Carrying CAM Compilers]]: a CAM book: sets, metrics and orders, frames and units, approximation and refinement, certificates for toolpaths.
- [[Transcripts/2026/08/17/Branch Branch Z1 Controller Review/From_Intent_to_Motion|From Intent to Motion]]: geometry, planning and checker algorithms for CAM, with a mathematical toolkit chapter.
- [[Transcripts/2026/08/02/CHATGPT TRANSCRIPT - CAM algorithms resources|CAM algorithms resources (transcript)]]: books and resources on CAM algorithms.

## Gaps

Computational geometry in the vault is strong on the CAM side (drop-cutter, offsets) and on 2D rasterization. Delaunay meshing and exact predicates appear only in the CAD textbook.

## Related topics

- [[Mathematics - Floating-Point and Exact Arithmetic]]
- [[Mathematics - Combinatorial and Algebraic Topology]]
- [[Mathematics - Curves and Surfaces]]
