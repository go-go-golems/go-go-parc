---
title: "Mathematics - Rigid Motions and Kinematics"
aliases:
  - "Rigid motions"
  - "Kinematics"
  - "SE(3)"
  - "Coordinate transforms"
tags:
  - knowledge-base
  - mathematics
  - geometry
  - kinematics
status: active
type: knowledge-base
created: "2026-11-02"
---

# Rigid Motions and Kinematics

Rigid motions are the distance-preserving transformations of space: rotations and translations, forming the groups SO(3) and SE(3). Kinematics studies how constrained bodies move. In CAD this is the mathematics of placing parts in an assembly; in graphics and CNC it is the mathematics of frames and cameras.

Part of [[Mathematics]].

> [!summary]
> - A pose is an element of SE(3); small changes live in its Lie algebra and are mapped back with the exponential map.
> - Joints restrict relative motion; a closed loop of joints adds nonlinear equations r(q) = log(T_loop(q)) = 0.
> - Mobility counts (Grübler) are informative but can be wrong at singular configurations.

## Concepts

- SO(3) and SE(3); rotation matrices and homogeneous transforms.
- Lie algebra so(3), exponential and logarithm maps.
- Joints, closed kinematic loops, mobility counts, four-bar linkage singularity.
- Numerical assembly solving; collision is separate from closure.
- Camera, view and projection transforms; nested coordinate frames.

## In the CAD textbook

[[Course - Engineering CAD from First Principles]] treats this topic in:

- [[Engineering CAD 13 - Assembly constraints on rigid motions|Chapter 13. Assembly constraints on rigid motions]]: SE(3), joints, closed loops, mobility counts, numerical assembly solving, collision versus closure.

## Elsewhere in the vault

### Projects and articles

- [[ARTICLE - M5Dial Proper 3D Renderer - Building a Z-Buffered Planet and Terrain on ESP32-S3]]: model, view and projection transforms on a microcontroller.
- [[ARTICLE - Recursive Zoomable Portals - Nested Cameras and Look-On Navigation]]: nested camera transforms in a zoomable interface.
- [[PROJECT REPORT - Falllinie Native GLES Spike - Deterministic Terrain, Print Shaders and Mali Depth Precision]]: camera and projection matrices for terrain rendering.
- [[PROJECT REPORT - Factory Multi-Camera Person Tracking - Research Program, Literature System, and the Twin-Lab Series]]: camera calibration and homographies for tracking across cameras.
- [[ARTICLE - M5StackChan - Deep Dive Technical Analysis of a Kawaii Desktop Robot Platform]]: servo kinematics of a desktop robot.

### CNC research (transcript artifacts)

- [[Transcripts/2026/08/08/CHATGPT TRANSCRIPT - CNC Precision Re-mounting Techniques|CNC Precision Re-mounting Techniques]]: registration pins and coordinate frames for flipping a workpiece.
- [[Transcripts/2026/08/16/Branch Z1 Controller Review/Compiling_Metal|Compiling Metal]]: frames, units and motion planning in a CAM compiler.

## Gaps

There is no vault note on Lie groups as such. Assembly kinematics appears only in the CAD textbook; frames and cameras appear across rendering and CNC notes.

## Related topics

- [[Mathematics - Numerical Linear Algebra]]
- [[Mathematics - Nonlinear Solving and Optimization]]
- [[Mathematics - Curves and Surfaces]]
