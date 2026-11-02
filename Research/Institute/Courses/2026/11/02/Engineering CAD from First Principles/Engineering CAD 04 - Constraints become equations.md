---
title: "Engineering CAD from First Principles — Chapter 4. Constraints become equations"
aliases:
  - "Chapter 4. Constraints become equations"
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

# Chapter 4. Constraints become equations

[[Engineering CAD 03 - Topology and boundary representation|← Chapter 3. Topology and boundary representation]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 05 - Jacobians and automatic differentiation|Chapter 5. Jacobians and automatic differentiation →]]

A sketch solver is a numerical engine for equations implied by geometric relationships. Before studying algorithms, we need to know what the unknowns are, which constraints contribute independent equations, and why “three constraints” is not the same thing as “three degrees of freedom removed.”

## 4.1 Choosing coordinates for entities

A point $P=(x,y)$ has two scalar unknowns. A circle may use $(c_x,c_y,r)$, so it has three. A line segment may be stored by endpoints $(a_x,a_y,b_x,b_y)$, so it has four. These are **parameterization degrees of freedom**, not necessarily the physical degrees of freedom after constraints are applied.

For a line from $A$ to $B$, horizontal means $b_y-a_y=0$. A specified length $L$ means

$$
\sqrt{(b_x-a_x)^2+(b_y-a_y)^2}-L=0.
$$

Fixing $A$ at $(0,0)$ contributes two equations: $a_x=0$ and $a_y=0$. A fixed start, horizontal direction and prescribed length usually leave no continuous freedom. Yet the length equation does not specify whether the line points to the left or the right. There may be **two disconnected solution branches** with endpoints $(L,0)$ and $(-L,0)$.

A local Newton solver often selects the branch closest to its starting estimate. This is why a constrained sketch must keep an initial configuration and, ideally, preserve branch identity during edits.

## 4.2 The residual vector

Write all scalar unknowns as $x\in\mathbb R^n$. Each scalar constraint becomes a component $F_i(x)$, forming

$$
F(x)=\begin{bmatrix}F_1(x)\\\vdots\\F_m(x)\end{bmatrix}.
$$

A feasible configuration satisfies $F(x)=0$, to a declared numerical tolerance. Some constraints contribute several scalar equations: coincident points in 2D require equality of both $x$ and $y$ coordinates. A parallelism constraint between line directions $u,v$ can be expressed by their 2D cross product $u_xv_y-u_yv_x=0$, but this equation also vanishes if either vector has zero length. The residual formulation must state its valid geometric domain.

For robust solving, normalized parallelism can be expressed by

$$
F_{\parallel}=\frac{u_xv_y-u_yv_x}{\|u\|\|v\|},
$$

provided both directions are nonzero. The normalization improves scale behavior but creates a singularity at a degenerate line. A solver should detect that case explicitly rather than rely on an arbitrary tiny denominator.

## 4.3 The Jacobian and local freedom

Near a configuration $x_0$, a differentiable system has the first-order approximation

$$
F(x_0+\Delta x)\approx F(x_0)+J(x_0)\Delta x,
$$

where $J_{ij}=\partial F_i/\partial x_j$. At an exact solution, a displacement that leaves constraints satisfied to first order lies in the null space:

$$
J\Delta x=0.
$$

If $J$ has rank $r$, the *infinitesimal* degree-of-freedom count is $n-r$. This is a local statement. At singular configurations, the null space may contain motions that do not integrate into genuine finite motions. Global connectivity and discrete branches are separate issues.

Consider two points $A$ and $B$ with a fixed distance of $5$ mm, and fix $A$ at the origin. There are four unknown coordinates and three generically independent scalar equations: two fixing $A$ and one fixing the distance. Hence $4-3=1$ free parameter: $B$ can move on a circle. If one more constraint says $b_y=0$, the remaining configuration is discrete (usually two possible points).


%%FIG:4%%

**Try it.** In [the constraint-circle bench](lab:sketch?id=constraint), move the line $x+y=s$ across the circle $x^2+y^2=r^2$. See how two solutions merge to one at tangency and disappear when the line is outside. A local rank calculation alone cannot tell the whole global story.

## 4.4 Underconstrained, overconstrained and redundant

An **underconstrained** regular system has a nontrivial null space. A **redundant** constraint adds an equation already implied locally by others. A genuinely **inconsistent** system has no configuration satisfying all constraints. These conditions are distinct.

For example, suppose a line is fixed horizontal, and we add a constraint that it is parallel to another line already fixed horizontal. The new parallelism equation does not reduce local freedom; it is redundant. Conversely, fixing a line length to both $10$ and $11$ mm creates an inconsistency, not a loss of freedom.

Equation count is therefore not sufficient. Two identical constraints contribute two rows to $J$ but only one to its rank. A rank-revealing factorization or row-space analysis is necessary.

## 4.5 Constraints with discrete orientation choices

Tangency, signed angles, distances and symmetry can describe multiple branches. For circle–circle tangency, center separation can satisfy $d=r_1+r_2$ (external) or $d=|r_1-r_2|$ (internal). Choosing one branch based only on the initial drawing may cause an unexpected jump after a large parameter edit.

A more explicit constraint representation records not only `tangent(A,B)` but the intended kind and orientation whenever possible. The solver can then detect that the selected branch has ceased to exist instead of jumping silently to another.

Jig's [constraint definitions](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/sketch/constraints.js) encode many geometric relations as expression nodes and determine certain orientation choices from the initial sketch. These are legitimate local strategies with predictable limits.

## 4.6 Building a minimal solver

The full task can be decomposed into a small sequence:

```text
1. Assign scalar variables to entities.
2. Generate residual equations and their dependencies.
3. Partition the incidence graph into independent clusters.
4. Evaluate residuals and Jacobians.
5. Find a local zero or least-squares minimum.
6. Analyze rank, free motion, and constraint satisfaction.
7. Preserve the chosen configuration across edits.
```

A cluster is a connected component of the bipartite graph linking variables to equations. Two rectangles with no shared constraints can be solved independently. This is cheaper than solving one large dense problem and makes interactive dragging local.

> **Exercise.** A rectangle is represented by four independent 2D vertices. Impose four edge-direction constraints (horizontal and vertical in alternation), two dimensions for width and height, and fix one corner. Assuming regular geometry, how many scalar equations are independent? Is the rectangle fully constrained? What changes if a redundant parallel constraint is added?

> **Careful.** A sketch with no explicit constraints may have zero *editable* DOF because its coordinates are treated as fixed. JigCAD calls that **explicit** mode. This is a modeling-language rule, not a consequence of a Jacobian calculation.

### Deeper study: from equations to a reliable linear subproblem

The equation count is not the same as the number of independent constraints. [[Engineering CAD 31 - The linear algebra underneath a geometric solver|Chapter 31]] derives the least-squares projection, minimum-norm steps and singular-value diagnostics used to interpret a linearized system. Its one-equation example x+y=2 makes the role of the parameter metric explicit: multiple steps satisfy the same equation, but a movement preference selects among them. At singular nonlinear solutions, Jacobian nullity need not equal the dimension of actual finite motion.

## Toward a reusable API

```text
Entity.variables() -> variable ids and initial values
Constraint.residuals() -> differentiable scalar expressions
System.jacobian(x) -> dense or sparse Jacobian
System.connectedComponents() -> clusters
System.dof(x) -> local rank and null-space information
System.branch() -> discrete orientation and tangency choices
```

## Key points

A constraint solver begins with a clear coordinate parameterization. Each geometric relation becomes one or more equations. Degrees of freedom come from Jacobian rank, not the number of constraint objects. Underconstrained, redundant, singular and inconsistent are different outcomes. Multiple discrete solutions require deliberate branch handling.

## Further reading

- [SolveSpace constraint tutorial](https://solvespace.com/constraints.pl) works through difficult constrained drawings.
- [SolveSpace reference](https://solvespace.com/ref.pl) distinguishes driven and reference dimensions.
- [JigCAD core API](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/CORE-API.md) documents its entity/constraint model.
- [JigCAD solver guide](https://github.com/go-go-golems/jig/blob/main/import/jigcad/content/docs/solver.md) describes explicit mode, DOF and dragging.

---

[[Engineering CAD 03 - Topology and boundary representation|← Chapter 3. Topology and boundary representation]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 05 - Jacobians and automatic differentiation|Chapter 5. Jacobians and automatic differentiation →]]
