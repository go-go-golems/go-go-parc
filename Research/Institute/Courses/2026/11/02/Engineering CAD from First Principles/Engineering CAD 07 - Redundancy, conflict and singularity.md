---
title: "Engineering CAD from First Principles — Chapter 7. Redundancy, conflict and singularity"
aliases:
  - "Chapter 7. Redundancy, conflict and singularity"
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

# Chapter 7. Redundancy, conflict and singularity

[[Engineering CAD 06 - Newton, Gauss–Newton, DogLeg and LM|← Chapter 6. Newton, Gauss–Newton, DogLeg and LM]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 08 - Continuation, sparse structure and performance|Chapter 8. Continuation, sparse structure and performance →]]

A solver can return a small residual, a large residual, a zero gradient, or an unexpected rank. None of those numbers by itself tells the user what went wrong. This chapter formalizes the diagnostic categories a CAD system needs and examines why Jig's conflict finder can propose misleading repairs.

## 7.1 Five outcomes, not two

A well-designed sketch solver should distinguish at least: **feasible and locally rigid**, **feasible with free motion**, **feasible but numerically singular**, **not converged from the supplied start**, and **proven inconsistent within a stated domain**. A sixth category, **ambiguous branch**, is useful when several discrete configurations satisfy the same equations.

Consider $F(x)=x^2-1$. Starting Newton at $x_0=0$ gives derivative $F'(0)=0$, so the Newton step is undefined. Yet the system clearly has two solutions, $x=\pm1$. Calling it inconsistent would be a factual error. Conversely, $F(x)=x^2+1$ has no real root; iterations cannot repair its inconsistency by a better starting point.

A practical numerical method usually has only local evidence. It should communicate that limitation in its status rather than silently upgrade failure to a theorem.

## 7.2 Redundant rows and rank

Suppose a sketch has constraints $x=2$, $y=3$ and $2x=4$. Its Jacobian is

$$
J=\begin{bmatrix}1&0\\0&1\\2&0\end{bmatrix}.
$$

There are three equations but rank two. The third is locally redundant, and here it is also globally implied by the first. If the third instead says $2x=5$, the Jacobian is unchanged, but the system is inconsistent. **Rank alone cannot distinguish redundant consistency from contradiction; residual values also matter.**

For nonlinear constraints, rank at one point can be misleading. The residual $x^2=0$ has zero derivative at its only solution. Its first-order null space suggests free motion even though every nonzero $x$ violates the original equation. This is called an infinitesimal singularity.

%%FIG:7%%

## 7.3 Minimal inconsistent subsets

A **minimal unsatisfiable subset** (MUS), or irreducible inconsistent subset under a precise notion of feasibility, is a set of constraints that has no solution while every proper subset is feasible. Multiple MUSes can exist.

Consider $x=0$, $x=1$, $y=0$, $y=1$. There are two independent contradictions: the $x$ pair and the $y$ pair. Removing one constraint from the $x$ pair does not make the full system feasible because the $y$ pair remains. Thus a diagnostic stating “drop any one of these four constraints” would be false.

A deletion filter can find a minimal subset by testing feasibility repeatedly. It has two complications: a nonlinear feasibility oracle can return a false negative when the local solver fails, and a heuristic may hold some constraints as a fixed background. In the latter case the reported set is minimal only **relative to that background**, not necessarily minimal among all constraints.

Jig's own issue register records an example in which independent conflicts are combined incorrectly. The code uses dependency support, candidate narrowing, and a bounded deletion filter. This is a useful start, but the report should state whether the result is exact, heuristic or budget-truncated.

**Try it.** Open [the conflict diagnostic bench](lab:sketch?id=conflicts). Add an independent contradiction and try dropping one constraint. The interface shows why one deletion is insufficient.

## 7.4 Singular derivatives and zero-distance constraints

The residual $\|P-Q\|$ is geometrically natural but its derivative with respect to coordinates is undefined when $P=Q$. If the intended constraint is **coincidence**, use the two component equations $P_x-Q_x=0$ and $P_y-Q_y=0$ instead. They remain smooth and have full rank near the coincidence.

Jig's issue register indicates that a zero-distance coincidence problem was repaired this way. This is an example of **better mathematical modeling** being more valuable than tuning solver tolerances. The best fix for a singular residual is often to choose a better residual, not a larger iteration budget.

At a tangent contact between a circle and a line, geometric branch structure may change. If an angle residual uses a wrapped trigonometric expression, it can be smooth on a local branch but discontinuous where the wrapping convention changes. Guard such configurations explicitly.

## 7.5 Separating feasibility search from diagnosis

A sound diagnostic workflow begins by attempting a local solve. If it fails, try principled restarts or continuation. Record the best residual and conditioning. Only then attempt to extract a conflict, and label it **candidate conflict** unless the feasibility oracle is sufficiently reliable.

For linear equality constraints, feasibility and minimal conflicting sets can be analyzed exactly or to well-controlled numerical accuracy. For arbitrary nonlinear constraints, certifying infeasibility may require interval methods, algebraic techniques, branch-and-bound, or restrictive assumptions. A production CAD system need not solve all such mathematical cases, but should avoid false certainty.

## 7.6 A diagnostic transcript as an engineering artifact

Imagine changing a radius from $4.0$ mm to $4.1$ mm causes the sketch to fail. A useful trace records: initial branch, normalized residual, minimum singular value estimate, DogLeg acceptance history, LM fallback attempts, and whether the proposed conflict survives independent re-solving. A bare string `sketch.overConstrained` loses nearly all that evidence.

Jig's IR and execution trace make this feasible architecturally. Some current traces show only the final successful solve after a dropped constraint, concealing the failed iterations and conflict search. Improving that instrumentation would significantly raise debugging quality.

> **Exercise.** For constraints $x=0$, $x=1$, $x+y=0$, $y=1$, list two possible minimal inconsistent subsets. Explain why a greedy deletion order can return different answers.

> **Careful.** A set of constraints may be structurally dependent without being algebraically contradictory. Do not interpret a small singular value or a redundant row as a conflict by itself.

### Deeper study: use exact counterexamples to calibrate diagnostics

At a regular solution, the implicit-function viewpoint connects Jacobian rank to local freedom. At a singular solution that connection can fail: the equation x²=0 has zero derivative at zero but only one local real solution. [[Engineering CAD 31 - The linear algebra underneath a geometric solver|Chapter 31]] makes this distinction explicit. A numerical solver therefore needs an unresolved or nonconvergent status rather than forcing every failed iteration into the category “inconsistent constraints.”

## Toward a reusable API

```text
SolveStatus = Solved | Underconstrained | Singular | NotConverged |
              CandidateConflict | CertifiedInconsistent | Ambiguous
ConflictReport { ids, relativeToBackground, oracle, budgetExhausted,
                 counterexampleIfFound, alternatives }
DiagnosticTrace { attempts, residuals, rankEvidence, branchChanges }
```

## Key points

Rank and residual information answer different questions. A local solver's failure is not an infeasibility certificate. Minimal inconsistent subsets are not unique, and several can coexist. Degenerate geometric residuals can create artificial singularities. Good diagnostics preserve their evidential basis and their uncertainty.

## Further reading

- [SolveSpace's constraint tutorial](https://solvespace.com/constraints.pl) includes practical cases with multiple solutions and nonconvergence.
- [JigCAD issue register](https://github.com/go-go-golems/jig/blob/main/import/jigcad/BOOK-ISSUES.md) describes the mixed-conflict and false-conflict cases.
- [JigCAD conflict-search implementation](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/sketch/solver.js) shows candidate narrowing and iteration budgets.
- [Nocedal and Wright](https://link.springer.com/book/10.1007/978-0-387-40065-5) provides mathematical context for nonlinear optimality and convergence.

---

[[Engineering CAD 06 - Newton, Gauss–Newton, DogLeg and LM|← Chapter 6. Newton, Gauss–Newton, DogLeg and LM]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 08 - Continuation, sparse structure and performance|Chapter 8. Continuation, sparse structure and performance →]]
