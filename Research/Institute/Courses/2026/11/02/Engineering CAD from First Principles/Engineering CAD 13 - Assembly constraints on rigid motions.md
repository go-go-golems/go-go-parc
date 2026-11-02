---
title: "Engineering CAD from First Principles — Chapter 13. Assembly constraints on rigid motions"
aliases:
  - "Chapter 13. Assembly constraints on rigid motions"
tags:
  - course
  - cad
  - textbook
  - jigcad
status: active
type: course
created: 2026-11-02
course: "[[Course - Engineering CAD from First Principles]]"
---

# Chapter 13. Assembly constraints on rigid motions

[[Engineering CAD 12 - Identity through parametric edits|← Chapter 12. Identity through parametric edits]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 14 - B-rep, STEP, meshes and manufacturing|Chapter 14. B-rep, STEP, meshes and manufacturing →]]

Mathematics in this chapter: [[Mathematics - Rigid Motions and Kinematics|Rigid Motions and Kinematics]] (see [[Mathematics]]).

A sketch solver moves points in a plane. An assembly solver moves entire rigid bodies in three-dimensional space while satisfying joint relations. The mathematics is related, but the state space is different: rotations are not ordinary unconstrained vectors, mechanisms can contain closed loops, and the number of joint objects does not determine mobility by simple counting.

## 13.1 Rigid transformations form SE(3)

A rigid-body pose consists of a rotation $R\in SO(3)$ and a translation $t\in\mathbb R^3$. In homogeneous coordinates,

$$
T=\begin{bmatrix}R&t\\0&1\end{bmatrix}\in SE(3).
$$

Multiplying transforms composes placements: if $p$ is a point in local coordinates, its world coordinates are $p_w=Rp+t$. A rotation matrix satisfies $R^\top R=I$ and $\det R=1$. Its nine entries are constrained, so it has only three local degrees of freedom. Translation adds three, giving six free coordinates for an unconstrained rigid body.

Using nine rotation-matrix entries directly as independent solver variables would require enforcing six orthogonality conditions and a determinant condition. Instead, assembly solvers often use local rotation increments in the Lie algebra $\mathfrak{so}(3)$ and map those increments back to $SO(3)$ with an exponential map. Near the current pose, a six-vector twist $\xi=(v,\omega)$ gives a small update $T_{new}\approx T\exp(\widehat\xi)$.

## 13.2 Joints restrict relative motion

A rigid joint permits no relative motion; a revolute joint permits one rotation about an axis; a prismatic joint permits one translation; a cylindrical joint permits rotation and translation along a common axis; a ball joint permits three rotations about a common point.

A joint connects two body-fixed port frames, not just two abstract nodes. Let body poses be $T_A$ and $T_B$, their port transforms $F_A,F_B$, and a joint displacement $J(q)$. Then a satisfied relative-placement relation is

$$
T_B=T_AF_AJ(q)F_B^{-1}.
$$

For a tree of components, this equation can place child components sequentially. That is what JigCAD's `solveAssembly` currently does for common revolute and slider joints. It computes placements; it is not, by itself, a general solver for cyclic mechanisms.

## 13.3 Closed loops add nonlinear equations

Imagine four links connecting four pivots in a planar four-bar mechanism. Three hinge positions can determine the fourth only if the links close. Multiplying relative transforms around a loop must give identity:

$$
J_1(q_1)T_1J_2(q_2)T_2J_3(q_3)T_3J_4(q_4)T_4=I.
$$

A generic 3D closure residual can be obtained by taking the matrix logarithm of the transform error and mapping it to six local coordinates, $r(q)=\log_{SE(3)}(T_{loop}(q))^\vee$. Solve $r(q)=0$, possibly together with joint limits and other geometric constraints.

For a planar four-bar, the closure can be reduced to circle intersection. Let ground pivots be $A=(0,0)$ and $D=(8,0)$, crank length $|AB|=3$, coupler length $|BC|=6$, and rocker length $|CD|=3$. Given input angle $\theta$, compute $B=A+3(\cos\theta,\sin\theta)$. Point $C$ is an intersection of the circle centered at $B$ of radius 6 and the circle centered at $D$ of radius 3.

The mechanism can have two branches (“open” and “crossed”). A valid solver must preserve which branch the user intended while the input angle varies. If the two circles cease to intersect, the mechanism cannot attain that position; if they become tangent, the constraint Jacobian becomes singular.


%%FIG:13%%

**Try it.** [The four-bar bench](lab:sketch?id=fourbar) varies the crank angle and branch. It calculates the closure point from two circle intersections and shows the precise configuration. It is a planar kinematic experiment, not a full SE(3) assembly engine.

## 13.4 Mobility counts are informative but insufficient

For a generic planar linkage with $n$ links including ground and $j$ lower-pair joints, a common generic count is $M=3(n-1)-2j$. For a four-bar with four links and four revolute joints, $M=3(3)-8=1$. This agrees with the input-angle description in regular configurations.

However, constraint dependencies, redundant joints, special geometry and singular positions can invalidate naive counts. A reliable assembly solver computes the rank of the assembled kinematic constraint Jacobian at the current pose. It also distinguishes local infinitesimal mobility from reachable finite motions.

Jig's `mobility` helper uses joint-count formulas and a heuristic for repeated ports. These are useful descriptive estimates, but are not equivalent to solving and linearizing the full joint constraint system.

## 13.5 Numerical assembly solving

The architecture resembles a sketch solver:

```text
1. Choose a grounded component and local pose variables for the others.
2. Build relative-frame residuals for each joint.
3. Build a component–joint graph and detect cycles.
4. Evaluate a sparse Jacobian using local SE(3) perturbations.
5. Solve constrained least squares or a trust-region system.
6. Enforce joint limits and retain discrete branches.
7. Check collisions through the motion range.
```

Each joint normally touches only two bodies, making the Jacobian block sparse. It is often advantageous to eliminate tree placements analytically and solve only loop variables numerically. This avoids introducing six independent pose variables for every component unnecessarily.

Jig's Rust autodiff and nonlinear-solving ideas could be reused, but an actual assembly solver also needs differentiable rigid transforms, group-aware local updates and a block-sparse layout.

## 13.6 Collision is not the same as closure

A mechanism may satisfy all joint constraints yet have components interpenetrating. Collision detection is a separate geometric query. A discrete check at one pose is not sufficient for a moving mechanism: parts can pass through one another between sampled times. Continuous collision checking or adaptive trajectory sampling is needed for reliable motion studies.

Jig can perform exact B-rep or approximate mesh-based interference checks on request. Its documented mesh-gap implementation was improved to detect crossing and containment. For high-consequence clearances, exact B-rep checks and independent safety margins remain preferable.

> **Exercise.** Derive the planar four-bar mobility formula. Then explain why a special singular pose can have additional infinitesimal motion without creating a genuine second finite degree of freedom.

> **Careful.** A statement such as “the assembly has one DOF” should specify whether it is a generic mechanism count, a local Jacobian result, or a verified reachable configuration family.

## Toward a reusable API

```text
Pose3 { rotation, translation }
Joint { type, bodyA, frameA, bodyB, frameB, parameters, limits }
AssemblyGraph { components, joints, grounding, cycles }
ClosureResidual -> six-dimensional twist error
AssemblySolveReport { status, poses, jointValues, rank, dof, branch }
```

## Key points

Rigid motions live in $SE(3)$, not a flat Euclidean parameter space. A tree of joints can be placed by transform propagation. A closed-loop mechanism requires nonlinear closure equations. Mobility formulas give generic estimates, while Jacobian rank gives local information. Joint satisfaction and noninterference are independent requirements.

## Further reading

- [Lynch and Park, *Modern Robotics*](https://modernrobotics.northwestern.edu/) develops $SE(3)$, twists and kinematics from first principles.
- [SolveSpace assembly and linkage tutorials](https://solvespace.com/tutorial.pl) demonstrate constrained mechanisms.
- [JigCAD assembly source](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/assembly.js) shows current sequential placement and interference logic.

---

[[Engineering CAD 12 - Identity through parametric edits|← Chapter 12. Identity through parametric edits]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 14 - B-rep, STEP, meshes and manufacturing|Chapter 14. B-rep, STEP, meshes and manufacturing →]]
