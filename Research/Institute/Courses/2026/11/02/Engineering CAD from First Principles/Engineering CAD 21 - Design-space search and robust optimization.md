---
title: "Engineering CAD from First Principles — Chapter 21. Design-space search and robust optimization"
aliases:
  - "Chapter 21. Design-space search and robust optimization"
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

# Chapter 21. Design-space search and robust optimization

[[Engineering CAD 20 - Manufacturing, drawings and sheet metal|← Chapter 20. Manufacturing, drawings and sheet metal]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 22 - Engineering a trustworthy next version|Chapter 22. Engineering a trustworthy next version →]]

A parametric CAD model defines a family of possible objects. Optimization asks which members of that family satisfy engineering constraints and perform best according to measurable objectives. The attractive feature of JigCAD's declarative architecture is that parameters, geometry, analysis and compilation trace can all be evaluated programmatically. This chapter derives constrained design search, Pareto tradeoffs, sampling, and robust decision-making.

## 21.1 A parametric part defines a feasible set

Let $p=(p_1,\ldots,p_n)$ be a vector of design parameters, such as width, thickness and hole spacing. Compilation maps $p$ to a geometric object $S(p)$, where defined. Evaluations then produce metrics $f_i(p)$ such as volume, mass, stiffness or required support material.

An ordinary constrained optimization problem is

$$
\min_{p\in\mathcal P}f(p)\quad\text{subject to}\quad g_i(p)\le0,\quad h_j(p)=0.
$$

The constraints must include both physics and geometry. A point in parameter space is not feasible if the sketch fails to solve, the solid is invalid, a wall becomes thinner than required, or a joint collides. It is not acceptable to optimize an objective value produced from invalid geometry and then describe that sample as an engineering design.

## 21.2 Work a plate thickness tradeoff

Take a plate $60\times40\,\mathrm{mm}$ with two strictly contained through holes of radius $3\,\mathrm{mm}$. For thickness $t$, its ideal volume is

$$
V(t)=t(60\cdot40-2\pi\cdot3^2)=t(2400-18\pi).
$$

The coefficient is approximately $2343.4513\,\mathrm{mm}^2$. At $t=2\,\mathrm{mm}$, $V\approx4686.90\,\mathrm{mm}^3$; at $t=4$, $V\approx9373.81\,\mathrm{mm}^3$. Mass is $\rho V$ for homogeneous material density $\rho$.

For a beam-like bending model with otherwise fixed geometry, bending stiffness scales approximately as $t^3$. Doubling thickness from 2 to 4 mm then increases stiffness by a factor of eight while doubling mass. These are two competing objectives: reduce mass and increase stiffness. The plate is not necessarily a beam, so this scaling is a model to validate for the actual load case, not an automatic exact performance claim for every plate.

**Try it.** [The Pareto bench](lab:sketch?id=pareto) draws the mass–stiffness tradeoff across thickness choices and highlights the feasible region under a minimum-stiffness requirement.

%%FIG:21%%

## 21.3 Pareto dominance and non-dominated fronts

For minimizing two objectives $f_1,f_2$, design $a$ **dominates** design $b$ when $f_i(a)\le f_i(b)$ for both objectives and at least one is strictly smaller. A design is Pareto-optimal relative to a sample if no other sampled design dominates it.

A Pareto front is not a single winner. It describes the tradeoff boundary. To pick a design, one still needs constraints, preferences, acceptable tradeoffs or a scalar decision rule. Weighted sums $w_1f_1+w_2f_2$ are simple but depend heavily on scaling and cannot discover every point on a nonconvex Pareto front. Lexicographic optimization preserves priority ordering; an $\varepsilon$-constraint method minimizes one objective while imposing bounds on the others.

Jig's design-space API supports grid/random/Latin-hypercube exploration and several objective styles, including Pareto sorting. Its documented implementation is minimal, which is a reason to validate feasibility filtering, units, seed determinism and correctness of result ranking before adding more search strategies.

## 21.4 Sampling before optimizing

A grid over $n$ parameters with $k$ values each requires $k^n$ evaluations. With six parameters and ten samples each, that is one million configurations. This curse of dimensionality motivates more economical sampling.

A **Latin hypercube sample** of $N$ points allocates one point to each of $N$ equal strata along every coordinate and permutes the strata independently between coordinates. This guarantees uniform one-dimensional stratification, but not uniform coverage of every pair or higher-dimensional projection. Sobol sequences and other low-discrepancy designs are alternatives.

For each sample, record the input vector, compiled result hash, objective values, constraint violations, and random seed. A compilation failure is a first-class outcome, not a data point with a fabricated zero volume. In optimization, returning an artificially small objective for failed geometry is a direct route to selecting invalid designs.

## 21.5 Sensitivity and automatic differentiation

If a metric $f(p)$ is differentiable, its gradient helps identify important parameters. For the plate volume above,

$$
\frac{\partial V}{\partial t}=2400-18\pi\approx2343.4513\;\mathrm{mm}^2.
$$

The derivative predicts a $234.345\,\mathrm{mm}^3$ volume increase for a small thickness increase of $0.1\,\mathrm{mm}$, provided the geometry remains in the same topological regime.

However, a CAD compiler is not globally smooth. A hole can touch an outer boundary, a feature can appear or disappear, a Boolean can change body count, and a fillet can fail above a critical radius. A derivative computed inside one topology branch is not evidence about a discontinuity across that boundary. Prefer derivative-aware local optimization only within stable feasible regions and use discrete search or explicit topology events elsewhere.

## 21.6 Robust design under uncertainty

Suppose a required clearance $c(p,\eta)$ depends on design parameters $p$ and manufacturing variation $\eta$. A nominal constraint $c(p,0)\ge c_{\min}$ may fail on a real part.

A **worst-case robust constraint** requires $c(p,\eta)\ge c_{\min}$ for every $\eta$ in a declared uncertainty set. A **chance constraint** instead requires

$$
\Pr\{c(p,\eta)\ge c_{\min}\}\ge1-\alpha,
$$

under a specified probability model. The latter can be useful when the manufacturing distribution is measured and justified. Neither formulation is interchangeable with simply subtracting an arbitrary “safety factor.”

For a hole and shaft with bounded dimensional variation, the worst-case guarantee is the interval calculation from Chapter 19. A design optimizer should propagate these limits into feasible-set filtering, not merely optimize nominal mass.

## 21.7 Expensive simulations and surrogate models

If each design evaluation includes full finite-element analysis or computational fluid dynamics, evaluating thousands of CAD variants may be prohibitively expensive. A **surrogate** approximates the measured response using a cheaper model fitted to known evaluations. Polynomial response surfaces, radial basis functions and Gaussian-process models are common choices.

A surrogate is only reliable within its training domain and must carry uncertainty or error estimates. The optimization loop should validate promising candidates using the real simulator, add those results to the dataset, and update its approximation. Never treat a surrogate's smooth prediction as proof that a Boolean feature can be built at those parameters.

## 21.8 Reproducibility and compilation caching

The feature DAG and content-hash cache can accelerate repeated design evaluation when samples share unchanged upstream work. But correctness comes before speed. A cache key must capture parameters, feature definitions, fit profiles, geometric environment and every dependency affecting the output. Hidden dependency omissions lead to stale geometry that can corrupt the Pareto front without an obvious runtime error.

A reproducible experiment records the repository revision, WASM module hash, solver settings, tolerance policy, material/print profile, seeds and the exact design-space domain. Compare a cached and uncached sweep on a representative subset to certify that caching did not change the objective values or feasibility classification.

> **Exercise.** Using $V(t)=t(2400-18\pi)$, tabulate volume at thicknesses $t=2,3,4,5$. Let a proxy bending stiffness be $K(t)=t^3$. If $K\ge27$, which of these choices has minimum volume? Repeat when $K\ge65$. State why the answer is only valid for the stated proxy model.

> **Careful.** Pareto optimality is relative to the evaluated design set. A plotted non-dominated sample is not proof of global optimality over the continuous parameter domain.

## Toward a reusable API

```text
DesignSpace { parameters, bounds, discreteChoices, constraints }
Candidate { parameters, compileStatus, metrics, violations, provenance }
Sampler { grid, random, latinHypercube, lowDiscrepancy }
MultiObjective { dominance, front, ranking, crowding }
UncertaintyModel { interval, probabilistic, correlated }
Experiment { seeds, kernelRevision, evaluations, acceptedDesigns }
```

## Key points

Optimization must respect geometrical feasibility before comparing objectives. Pareto fronts display tradeoffs rather than selecting a unique solution. Latin hypercube sampling reduces some weaknesses of grids in moderate dimensions. Gradients help within fixed topology regimes but not across topology changes. Manufacturing variation should enter the constraints. Reproducibility and cache correctness are mathematical parts of the optimization result.

## Further reading

- [Nocedal and Wright, *Numerical Optimization*](https://link.springer.com/book/10.1007/978-0-387-40065-5) develops constrained optimization and numerical methods.
- [Forrester, Sóbester and Keane, *Engineering Design via Surrogate Modelling*](https://onlinelibrary.wiley.com/doi/book/10.1002/9780470770801) describes surrogate-based expensive engineering search.
- [Deb et al., NSGA-II](https://doi.org/10.1109/4235.996017) is a foundational algorithm for multiobjective ranking and crowding.
- [JigCAD kernel API](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/KERNEL-API.md) documents the current design-space search interface and limitations.
- [JigCAD feature cache implementation](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/compile.js) shows why optimization results depend on correct parameter dependency tracking.

---

[[Engineering CAD 20 - Manufacturing, drawings and sheet metal|← Chapter 20. Manufacturing, drawings and sheet metal]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 22 - Engineering a trustworthy next version|Chapter 22. Engineering a trustworthy next version →]]
