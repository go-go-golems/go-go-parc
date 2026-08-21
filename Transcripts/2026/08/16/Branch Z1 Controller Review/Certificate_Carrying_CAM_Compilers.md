---
title: "Certificate-Carrying CAM Compilers"
subtitle: "Semantics, Intermediate Representations, Verification, and Optimization for CNC Systems"
author: "Prepared for the Dropcut Studio / Makera Z1 project"
date: "First edition - August 2026"
documentclass: book
classoption:
  - openany
  - oneside
papersize: letter
fontsize: 11pt
geometry:
  - top=0.78in
  - bottom=0.82in
  - inner=0.86in
  - outer=0.78in
  - headheight=15pt
linestretch: 1.05
toc: true
toc-depth: 2
numbersections: true
colorlinks: true
linkcolor: MidnightBlue
urlcolor: MidnightBlue
mainfont: "Linux Libertine O"
sansfont: "Linux Biolinum O"
monofont: "DejaVu Sans Mono"
header-includes:
  - |
    \usepackage{microtype}
  - |
    \usepackage{booktabs,longtable,array,tabularx}
  - |
    \usepackage{amsmath,amssymb,mathtools}
  - |
    \usepackage{stmaryrd}
  - |
    \usepackage{fancyhdr}
  - |
    \usepackage{enumitem}
  - |
    \usepackage{caption}
  - |
    \usepackage{float}
  - |
    \usepackage{fvextra}
  - |
    \usepackage[most]{tcolorbox}
  - |
    \usepackage{xcolor}
  - |
    \definecolor{MidnightBlue}{RGB}{22,55,92}
  - |
    \pagestyle{fancy}
  - |
    \fancyhf{}
  - |
    \fancyhead[LE,RO]{\small\nouppercase{\leftmark}}
  - |
    \fancyfoot[C]{\thepage}
  - |
    \setlength{\headwidth}{\textwidth}
  - |
    \setlist{nosep,leftmargin=*}
  - |
    \captionsetup{font=small,labelfont=bf}
  - |
    \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\},fontsize=\small}
  - |
    \newtcolorbox{designrule}{breakable,colback=black!3,colframe=black!45,title=Design rule,fonttitle=\bfseries}
  - |
    \newtcolorbox{warningbox}{breakable,colback=black!2,colframe=black!70,title=Safety note,fonttitle=\bfseries}
  - |
    \newtcolorbox{workedexample}{breakable,colback=black!2,colframe=black!45,title=Worked example,fonttitle=\bfseries}
---

\frontmatter

# Preface {-}

Computer-aided manufacturing software occupies an unusual position in software engineering. It begins with abstractions - features, surfaces, tolerances, tools, and process plans - but ends by commanding a physical mechanism that can remove material, break a tool, damage a fixture, or create an unsafe state. A CAM system is therefore not adequately described as a geometry program, a code generator, or a graphical editor. It is a compiler for a cyber-physical process.

This textbook develops that claim into a complete engineering discipline. It explains how to design a CAM language, a family of intermediate representations, compiler passes, operational and denotational semantics, static analyses, independent validators, quantitative error bounds, certificates, controller protocols, and optimization passes. The running example is a browser and command-line CAM stack for a Makera Z1-class three-axis mill, but the architecture applies to routers, mills, lathes, laser cutters, additive machines, robots, and hybrid manufacturing systems.

The central principle is simple:

> **Machining is the semantic model. G-code is one backend.**

That principle has practical consequences. A pocket operation denotes an acceptable physical result, not a preferred string of `G1` blocks. A traverse denotes motion through certified free space, not necessarily one `G0` command. A certificate is not a green badge produced by the same heuristic that generated the path; it is a structured claim about an exact artifact, supported by evidence that an independent checker can validate. A postprocessor does not merely format numbers; it refines a machine-independent action language into the modal semantics of a specific controller.

The book is organized as a course. Parts I and II establish the semantic and language foundations. Part III treats passes as proof obligations. Part IV develops assertions, invariants, robust geometry, certificates, and controller protocols. Part V introduces operations research for sequencing, linking, and feed scheduling. Part VI turns the theory into a TypeScript implementation strategy and uses the Dropcut/Z1 architecture as a detailed case study.

Each chapter contains learning objectives, worked examples, design rules, and exercises. The exercises range from proofs and counterexamples to API design and executable tests. Selected solutions appear in Appendix E.

## Audience {-}

The primary audience is a software engineer who knows JavaScript or TypeScript, has some mathematical maturity, and understands basic CNC operation. Prior coursework in compilers, formal methods, computational geometry, or optimization is useful but not required. The mathematical prerequisites are developed as needed.

The book also serves several narrower audiences:

- A CAM developer can use the IR and pass architecture directly.
- A controls engineer can focus on the operational and temporal semantics.
- A verification engineer can focus on abstract interpretation, robust geometry, and certificate checking.
- A researcher can use the formal model to state new planning and optimization algorithms precisely.
- A hobby CNC developer can use the worked examples to avoid unsafe assumptions hidden by apparently simple G-code.

## Safety scope {-}

This book is an engineering and research text. It does not certify any machine, controller, program, or workholding setup. Software evidence is always conditional on physical assumptions such as tool dimensions, machine calibration, fixture geometry, work-coordinate registration, spindle behavior, material properties, and controller conformance. The runtime chapters explain how those assumptions should be recorded and checked; they cannot be eliminated by types or proofs alone.

## How to read the book {-}

For a fast architectural path, read Chapters 1, 2, 6, 8, 14, 27, 29, 37, and 40. For implementation work, read Parts II, III, and VI in order. For verification work, read Chapters 5 and 6, then Part IV. For path-planning research, read Chapters 3, 4, 9, 16, 24-26, and Part V.

## Conventions {-}

- `Intent` means a specification of acceptable manufacturing outcomes.
- `IR` means an intermediate representation with defined syntax and semantics.
- `artifact` means a content-addressed input or output of a compiler stage.
- `claim` means a precise proposition about an artifact.
- `evidence` means data that a checker can use to establish a claim.
- `certificate` means a collection of claims, assumptions, evidence, dependencies, and checker identities.
- `machine state` includes physical, controller, modal, coordinate, and process state unless narrowed explicitly.
- Lengths are in millimeters and angles are in radians unless a type or unit annotation says otherwise.

\mainmatter

\part{Part I - Reframing CAM as Compilation}

# The Cyber-Physical Compiler

> **Learning objectives.** By the end of this chapter, the reader should be able to distinguish a CAM compiler from a G-code generator, state an end-to-end refinement theorem, and identify the major semantic boundaries between intent and physical execution.

## From strings to physical behavior

A naive description of a CAM program is:

```text
geometry in -> G-code out
```

This description omits every fact that makes the software difficult. It does not say what the geometry means, what result the operator requested, how the tool and holder occupy space, how the work coordinate system relates to the machine, whether the controller interprets rapids as coordinated lines, whether a feed rate is feasible, or what should happen after an interrupted upload. It also gives no place to state correctness.

A better semantic stack is shown in Figure 1.1.

![A semantic stack from manufacturing intent to physical execution.](figures/semantic_stack.png){width=40%}

At the top, manufacturing intent describes acceptable outcomes: remove a pocket to a depth, leave a finishing allowance, preserve a protected surface, or measure a datum. At the bottom, physical execution is a trace of machine poses, spindle states, sensor readings, communication events, faults, and stock changes. Every compiler stage removes freedom or adds implementation detail.

NIST's canonical machining-command work used a similar separation in the opposite direction: an RS274 interpreter maps modal controller syntax to canonical machining operations [R1, R2]. A semantic CAM compiler begins with machining operations and lowers them to a controller dialect. STEP-NC likewise separates manufacturing features, working steps, and technology from immediate axis-level syntax [R3, R42, R43].

## Source meaning is usually a set

A conventional expression such as `2 + 3` has one mathematical result. A manufacturing operation usually permits many implementations. A pocket can be cut by raster passes, offsets, adaptive clearing, trochoidal motion, or a hybrid. The source operation should therefore denote a set of acceptable executions or outcomes.

Let an intent be $I$. Its meaning is:

$$
\llbracket I \rrbracket \subseteq \mathcal{E},
$$

where $\mathcal{E}$ is a space of physical executions or final workpiece states. A planner selects one implementation $P$ such that the executions of $P$ belong to the allowed set, up to declared approximation:

$$
\operatorname{compile}(I)=P,
$$

$$
\forall \tau \in \operatorname{Exec}(P,A),\quad
\alpha(\tau) \in N_{\varepsilon}(\llbracket I \rrbracket).
$$

Here:

- $A$ is a set of assumptions about the machine, setup, tools, and controller;
- $\tau$ is a possible execution trace;
- $\alpha$ abstracts low-level execution into observations relevant to the intent;
- $N_{\varepsilon}$ is a tolerance neighborhood under a specified metric.

This is a refinement statement. The target program is allowed to choose details that the source left open, but it must not introduce behavior outside the source specification.

## Why the target is not text

G-code text is an encoding of controller behavior. Its meaning depends on:

- modal state inherited from prior blocks;
- active units and coordinate systems;
- controller-specific interpretations of arcs, cycles, probes, and rapids;
- machine configuration and firmware version;
- asynchronous machine state such as homing, alarms, and active playback;
- numerical formatting and rounding;
- physical dynamics and following error.

Two files with different text can be semantically equivalent. Two identical files can behave differently under different initial modal states. Consequently, a compiler theorem should relate source intent to interpreted controller and physical traces, not to strings.

A useful end-to-end statement is:

$$
\operatorname{CheckBundle}(B)=\mathrm{true}
\land \operatorname{AssumptionsHold}(A)
\Longrightarrow
\forall \tau \in \operatorname{Execute}(B,A),
\operatorname{Safe}(\tau)
\land
\operatorname{Conforms}_{\varepsilon}(\tau,I).
$$

The exact job bytes are part of $B$, but they are not the entire object.

## Three kinds of correctness

A serious CAM compiler needs at least three notions of correctness.

**Language correctness** asks whether the program is well formed. Are all names resolved? Are units compatible? Are coordinates in known frames? Is a tool selected before it is used?

**Geometric and process correctness** asks whether the planned tool motion satisfies the manufacturing intent. Does it preserve protected material? Does it remove required stock? Does the holder avoid fixtures? Are entries and links feasible in the evolving stock state?

**Control correctness** asks whether the controller receives, stores, starts, pauses, resumes, aborts, and reports the intended job. Does authorization refer to the exact uploaded bytes? Can a timeout desynchronize the protocol? Does a feed hold actually reach the machine even when another command is pending?

The three cannot be collapsed. A geometrically correct path can be serialized incorrectly. A valid G-code file can be uploaded under the wrong name. A correct upload can be executed under a changed work offset.

## The semantic waist

A robust system benefits from a small, machine-independent language of canonical machining actions. It serves as a semantic waist between high-level planners and low-level postprocessors.

Typical canonical actions include:

```ts
type CanonicalCommand =
  | { kind: "selectTool"; tool: ToolRef }
  | { kind: "setSpindle"; rpm: Rpm; direction: "cw" | "ccw" }
  | { kind: "stopSpindle" }
  | { kind: "traverse"; path: Path; clearance: ClearancePolicy }
  | { kind: "cut"; path: Path; feed: FeedRate; intent: CutIntent }
  | { kind: "probe"; path: Path; expectedContact: ContactModel }
  | { kind: "dwell"; duration: Seconds }
  | { kind: "pause"; reason: string };
```

There is no `G0`, `G17`, or `I/J/K` in this language. Those are controller encodings. Conversely, the canonical language must contain physical distinctions that G-code can obscure, such as the difference between free-space traverse and cutting feed.

## A first design rule

\begin{designrule}
Define correctness at the highest semantic level that expresses the operator's intent, then carry that meaning through explicit refinement relations. Never use textual similarity to stand in for physical equivalence.
\end{designrule}

## Worked example: a rectangular pocket

Suppose the source program requests a $30\,\mathrm{mm}\times20\,\mathrm{mm}$ pocket, $4\,\mathrm{mm}$ deep, with $0.2\,\mathrm{mm}$ radial and axial roughing allowance. A correct source meaning does not name a raster or stepover. It states constraints on the residual stock and protected region.

Let $R$ be the pocket region, $z_f$ the nominal floor, and $\delta_r,\delta_a$ the allowances. One possible specification is:

1. Material above $z_f+\delta_a$ inside the inward-offset pocket $R\ominus B_{\delta_r}$ must be removed.
2. Material outside $R$ must not be removed beyond a geometric tolerance $\varepsilon$.
3. The fixture and holder must remain disjoint for the entire execution.
4. The machine must remain inside its admissible configuration set.

A planner can now select a strategy and produce a witness. A checker evaluates the witness against these four propositions. If the strategy changes from raster to offsets, the intent and checker need not change.

## Exercises

1. Give two different G-code programs that plausibly implement the same straight cutting move. Identify the initial modal assumptions required for equivalence.
2. Define a manufacturing intent for drilling a through-hole without referring to a canned cycle or peck sequence.
3. Explain why a preview renderer is not automatically a verifier, even when its image appears correct.
4. Write an end-to-end correctness statement for a probing operation. Include at least three physical assumptions.
5. Classify each failure as language, geometric/process, control, or cross-boundary: wrong tool diameter, stale work offset, truncated upload, invalid arc radius, job never started.
6. Describe one circumstance in which rejecting a valid source program is preferable to emitting code.

# Manufacturing Intent as a Specification

> **Learning objectives.** The reader should be able to model a manufacturing operation as a predicate over outcomes, distinguish required removal from forbidden removal, and explain why planning is witness synthesis rather than mere path generation.

## Specifications before strategies

CAM user interfaces often conflate an operation with an algorithm: “parallel finishing,” “adaptive clearing,” or “waterline.” These labels are useful, but they are strategies, not meanings. A semantic design starts with a predicate that any acceptable strategy must satisfy.

For a stock solid $S_0$, target solid $P$, protected fixtures $O$, and tool assembly $T$, a manufacturing operation can be viewed as a relation:

$$
\mathcal{M}(S_0,P,O,T,S_f,\tau),
$$

where $S_f$ is final stock and $\tau$ is the execution trace. The relation may constrain:

- material that must be absent;
- material that must remain;
- surface deviation;
- roughness or scallop height;
- tool engagement and process limits;
- machine and fixture clearance;
- operation ordering;
- observable measurements and their uncertainty.

A planner synthesizes a candidate $x$ such that $\mathcal{M}$ is expected to hold. Verification checks the candidate independently.

## Required, permitted, and forbidden regions

It is useful to partition material space into three concepts.

The **required-removal region** $R_{\mathrm{req}}$ must be removed, perhaps within a tolerance.

The **forbidden-removal region** $R_{\mathrm{forbid}}$ must be preserved. It includes the protected target, fixtures, table, and any explicit no-cut volumes.

The **permitted-removal region** $R_{\mathrm{permit}}$ may be removed without violating the operation. Roughing allowance and sacrificial stock often live here.

A conservative checker should not infer one property from another. Showing that the tool did not enter $R_{\mathrm{forbid}}$ does not show that it removed $R_{\mathrm{req}}$. Showing that enough stock disappeared does not show that protected material survived.

This distinction directly determines approximation direction:

- no-gouge and collision claims use an **outer** approximation of the swept tool volume;
- guaranteed-removal claims use an **inner** approximation;
- residual-stock claims use an outer approximation of what remains.

## Features as semantic handles

Manufacturing features are not merely UI objects. They preserve information needed by later passes and certificates. Examples include:

```ts
interface PocketFeature {
  id: FeatureId;
  boundary: Region2D<"workpiece">;
  floor: SurfaceRef;
  depth: Mm;
  radialAllowance: Mm;
  axialAllowance: Mm;
  tolerance: Mm;
  finishClass?: SurfaceFinishRequirement;
}
```

A low-level polyline cannot explain which portion is a floor finish, which wall must be preserved, or why one pass precedes another. Keeping feature identity in provenance allows diagnostics such as:

```text
Pocket P17 floor tolerance unresolved near (18.2, 9.7, -4.0)
because the ball-end tool enclosure exceeds the remaining 0.012 mm budget.
```

## Intent is relational and partial

A source operation can be intentionally incomplete. It might leave strategy, direction, entry, or exact feed unspecified. This is not a defect. The planner's job is to resolve such choices while satisfying constraints.

Let $I$ define a relation between initial and final states:

$$
I \subseteq \Sigma \times \Sigma.
$$

The operation is legal from $\sigma$ when at least one $\sigma'$ satisfies $(\sigma,\sigma')\in I$. A planner may choose any such result, but must emit evidence that connects its path to the relation.

Partiality is also important. If the requested pocket is narrower than the selected tool, the intent may have no feasible implementation under the current tool set. A correct compiler rejects or requests a different tool. It does not silently distort the pocket.

## Planning as witness synthesis

The conventional type:

```ts
Intent -> Toolpath
```

hides the proof obligation. A better conceptual type is:

```ts
interface Planned<I, P, W> {
  intent: I;
  program: P;
  witness: W;
}

type Planner<I, P, W> =
  (intent: I, context: PlanningContext) =>
    Result<Planned<I, P, W>, PlanningDiagnostic[]>;
```

The witness can contain:

- the offset regions used to construct passes;
- coverage cells and residual bounds;
- feature-to-path provenance;
- entry feasibility results;
- precedence decisions;
- claimed approximation bounds;
- solver objective and lower bound.

The checker need not repeat the full search. It verifies that the proposed witness establishes the intended relation.

## Contracts for common operations

A **roughing** contract commonly requires removal of bulk stock while preserving an allowance envelope. It may tolerate a coarse residual model but must prevent fixture and target penetration.

A **finishing** contract typically constrains maximum normal deviation or scallop height on a target surface. It needs a target model and a tool/contact model.

A **drilling** contract constrains hole axis, diameter class, depth, breakthrough, and cycle behavior. It may include chip evacuation and peck constraints.

A **probing** contract produces a measurement value and an updated frame or offset, together with an uncertainty model. It is not simply a move that ends at a commanded coordinate.

A **traverse** contract requires the entire tool assembly to remain in free space. Its endpoint alone is insufficient.

## Worked example: rough then finish

Consider a pocket with nominal target $P$ and a $0.25\,\mathrm{mm}$ roughing allowance. Define the roughing protected region as:

$$
P_{\mathrm{rough}} = P \oplus B_{0.25},
$$

where $\oplus$ is a Minkowski sum. A roughing toolpath is no-gouge if its outer swept volume $W^+$ is disjoint from the interior of $P_{\mathrm{rough}}$:

$$
W^+ \cap \operatorname{int}(P_{\mathrm{rough}})=\varnothing.
$$

The finishing operation uses the nominal target and a much smaller tolerance layer. The two operations have different specifications even if they share geometry. A certificate that says only “gouge checked” is incomplete unless it identifies which protected region, which tolerance, which tool model, and which artifact were checked.

## Design rules

\begin{designrule}
Represent manufacturing operations as predicates or relations over physical outcomes. Treat strategy output as a witness to those predicates. Keep required removal, forbidden removal, and permitted removal as separate claims.
\end{designrule}

## Exercises

1. Specify a contour-finishing operation using a target boundary, side selection, axial range, and tolerance.
2. Construct an example where no-gouge holds but required removal fails.
3. Construct an example where required removal holds but no-gouge fails.
4. Design a witness object for a raster pocket planner.
5. Explain why a probe operation must return a value and uncertainty rather than merely update position.
6. Define a rejection diagnostic for a tool that cannot enter a feature.
7. Identify which parts of a machining intent are stable under toolpath reordering and which are not.

# Mathematical Foundations: Sets, Relations, Metrics, and Orders

> **Learning objectives.** The reader should be able to use relations to model nondeterministic semantics, metrics to state approximation, partial orders to model information, and fixed points to describe iterative analysis.

## Sets and characteristic predicates

A geometric solid can be idealized as a set $S\subseteq\mathbb{R}^3$. Equivalently, it can be represented by a characteristic predicate:

$$
\chi_S(x)=
\begin{cases}
1 & x\in S,\\
0 & x\notin S.
\end{cases}
$$

Different computational representations approximate this set: triangle meshes, signed distance fields, boundary representations, voxels, dexels, constructive solids, or implicit functions. The semantics should name the set; the implementation should state how its representation encloses or approximates that set.

Common set operations have direct manufacturing meanings:

- $A\cup B$: combined occupied volume;
- $A\cap B$: collision or overlap;
- $A\setminus B$: stock after removal;
- $A\oplus B$: dilation, tool compensation, or configuration obstacle;
- $A\ominus B$: erosion, inward allowance, or robust protected core.

## Relations instead of functions

A function maps each input to one output. Physical commands may fail, measurements may vary, and controller behavior may be nondeterministic. A relation is therefore often a more honest semantic object:

$$
R\subseteq A\times B.
$$

For a command $c$, define:

$$
\llbracket c\rrbracket\subseteq\Sigma\times\Sigma\times\mathcal{T}\times\mathcal{O},
$$

where $\mathcal{T}$ contains traces and $\mathcal{O}$ contains outcomes such as success, alarm, timeout, or uncertain completion.

Relations compose:

$$
R;S = \{(a,c)\mid \exists b.\ (a,b)\in R\land(b,c)\in S\}.
$$

This is the semantic basis of sequential execution. It also exposes an important point: an ambiguous timeout may produce several possible successor states. The host must not pretend that the state is unchanged.

## Metrics and neighborhoods

Approximate correctness needs a metric $d$. For points, Euclidean distance is common:

$$
d(x,y)=\|x-y\|_2.
$$

For compact sets, the Hausdorff distance is:

$$
d_H(A,B)=\max\left\{
\sup_{a\in A}\inf_{b\in B}d(a,b),
\sup_{b\in B}\inf_{a\in A}d(a,b)
\right\}.
$$

For a target surface, normal deviation may be more meaningful than Hausdorff distance. For gouge, maximum penetration depth into a protected solid may be the relevant quantity. For a frame transform, translation and rotation errors need separate units and propagation rules.

The tolerance neighborhood of a set is:

$$
N_{\varepsilon}(A)=\{x\mid d(x,A)\le\varepsilon\}.
$$

A certificate must name both $\varepsilon$ and the metric. “Verified to 0.02 mm” is incomplete if it does not say what distance is bounded.

## Equivalence, preorder, and refinement

Exact semantic equivalence is symmetric:

$$
P\equiv Q \quad\Longleftrightarrow\quad
\operatorname{Beh}(P)=\operatorname{Beh}(Q).
$$

Refinement is directional:

$$
Q\sqsubseteq P
\quad\Longleftrightarrow\quad
\operatorname{Beh}(Q)\subseteq\operatorname{Beh}(P).
$$

The target $Q$ makes at least as many decisions as source $P$ and introduces no disallowed behavior. Refinement is generally a preorder: reflexive and transitive, but not necessarily antisymmetric at the syntactic level.

Compiler passes frequently establish different relations:

- normalization: equivalence;
- scheduling: trace refinement;
- curve sampling: bounded geometric refinement;
- optimization: feasible refinement plus objective improvement;
- error recovery: perhaps no refinement at all unless modeled explicitly.

## Lattices of information

Static analysis often computes information ordered by precision. Let $a\sqsubseteq b$ mean that $a$ is at least as precise as $b$, or choose the reverse convention consistently.

An interval domain illustrates the idea. The exact value $5$ is represented by $[5,5]$. The interval $[4,6]$ is less precise, and $[-\infty,\infty]$ represents complete ignorance. Joining two control-flow paths requires an upper bound that contains both possibilities.

A complete lattice provides:

- a bottom element $\bot$;
- a top element $\top$;
- least upper bounds $\sqcup$;
- greatest lower bounds $\sqcap$;
- fixed points for recursive or looping behavior.

Abstract interpretation uses these structures to compute conservative invariants [R7].

## Monotonicity and fixed points

A transfer function $F$ on an abstract domain should be monotone:

$$
a\sqsubseteq b \Longrightarrow F(a)\sqsubseteq F(b).
$$

For a loop or recursive subprogram, the analysis seeks a fixed point:

$$
F(x)=x.
$$

Iterating from $\bot$ may converge to the least fixed point. Widening accelerates convergence when domains contain infinite ascending chains; narrowing can recover precision afterward.

Even a nominally straight-line G-code file can acquire loops through subprogram calls, macros, canned cycles, or controller-specific repetition. A validator must either analyze these constructs soundly or reject them.

## Tolerance is not equality

A common practical relation is:

$$
x\approx_{\varepsilon}y \quad\Longleftrightarrow\quad d(x,y)<\varepsilon.
$$

It is reflexive and symmetric, but not transitive. For $x=0$, $y=0.75\varepsilon$, and $z=1.5\varepsilon$, both adjacent pairs match while $x$ and $z$ do not.

Therefore, tolerance-based endpoint matching cannot be treated as mathematical equality without additional machinery. Repeated snapping or chaining can accumulate error or create inconsistent topology. This observation will become central in Chapter 9 and in the contour-key case study.

## Worked example: an uncertainty box

Suppose a probed work origin has independent coordinate bounds:

$$
x\in[9.98,10.02],\quad
y\in[4.99,5.01],\quad z\in[-0.015,0.015].
$$

A point $(20,12,-3)$ in the work frame maps to a machine-frame box, not a single point. A travel checker should propagate the box through the frame transform and prove that the entire enclosure lies within machine limits. Checking only the nominal transform is a simulation, not a robust travel proof.

## Exercises

1. Prove that relational composition is associative.
2. Give a counterexample to transitivity of $\approx_{\varepsilon}$.
3. State no-gouge as a set-disjointness proposition using a tolerance erosion.
4. Describe an abstract spindle domain that distinguishes definitely off, definitely on, and unknown.
5. Explain why a join at a control-flow merge loses information.
6. Give two metrics that could be relevant to finishing a freeform surface and explain their difference.
7. Model an uncertain command timeout as a relation with multiple outcomes.

# Geometry, Frames, and Units

> **Learning objectives.** The reader should be able to model rigid transforms, prevent frame and unit confusion in an API, propagate transform uncertainty, and distinguish tool-center geometry from full tool-assembly geometry.

## Frames are part of the type

A CNC program contains many coordinate systems:

- machine coordinates;
- work coordinate systems such as G54;
- stock coordinates;
- part-design coordinates;
- fixture coordinates;
- tool-tip and tool-center coordinates;
- camera or probe coordinates.

A tuple of three numbers is not enough to identify a point. The frame is part of its meaning:

```ts
interface Point3<F extends FrameId> {
  readonly x: Mm;
  readonly y: Mm;
  readonly z: Mm;
  readonly frame: F;
}
```

The compiler should reject addition or comparison across unrelated frames unless an explicit transform is supplied.

## Rigid transformations

A pose in three-dimensional Euclidean space can be represented by an element of $SE(3)$:

$$
T =
\begin{bmatrix}
R & p\\
0 & 1
\end{bmatrix},
$$

where $R\in SO(3)$ is a rotation and $p\in\mathbb{R}^3$ is a translation. A point in homogeneous coordinates transforms as:

$$
\bar{x}_{B}=T_{B\leftarrow A}\bar{x}_{A}.
$$

Transforms compose:

$$
T_{C\leftarrow A}=T_{C\leftarrow B}T_{B\leftarrow A}.
$$

A frame graph should make direction explicit. Naming a transform merely `workOffset` encourages inversion mistakes.

## Three-axis simplification and future proofing

For a fixed-orientation three-axis mill, tool orientation is usually constant and the relevant transform may be a translation plus possibly a setup rotation. The semantic model should still avoid baking this simplification into every abstraction. Paths can be parameterized over position only now while poses and transforms remain general enough for indexed or rotary axes later.

A good principle is to make the common case cheap without making the general case impossible.

## Dimensional types

Bare numbers erase physical dimensions. The following errors all type-check in ordinary JavaScript:

```ts
const feed = 600;       // mm/min or mm/s?
const speed = 12000;    // rpm or rad/s?
const angle = 90;       // degrees or radians?
const depth = -3;       // mm, inch, or machine units?
```

Use nominal or branded types at API boundaries:

```ts
type Mm = number & { readonly __unit: "mm" };
type MmPerMin = number & { readonly __unit: "mm/min" };
type Rpm = number & { readonly __unit: "rpm" };
type Radians = number & { readonly __unit: "rad" };
```

Types alone are insufficient. Constructors must enforce finite values and domain restrictions:

```ts
function mm(x: number): Mm {
  if (!Number.isFinite(x)) throw new RangeError("length must be finite");
  return x as Mm;
}

function positiveFeed(x: number): MmPerMin {
  if (!Number.isFinite(x) || x <= 0) {
    throw new RangeError("feed must be finite and positive");
  }
  return x as MmPerMin;
}
```

A cast can forge a brand, so runtime elaboration remains part of the trusted language boundary.

## Tools and assemblies

The tool tip is not the only moving geometry. A tool assembly may include:

- cutting body;
- non-cutting shank;
- collet;
- nut;
- holder;
- spindle nose;
- probe body.

Different claims use different subsets:

- target gouge usually concerns the cutting geometry;
- fixture collision concerns the entire assembly;
- required removal concerns a guaranteed inner cutting volume;
- machine travel concerns the kinematic reference point and axis limits.

A `Tool` should therefore not be only a diameter and flute length. It should refer to geometric models and uncertainty bounds.

## Uncertain transforms

A probed or manually set transform is not exact. One useful representation is a nominal transform plus a bounded perturbation:

$$
T = \hat{T}\exp(\xi^\wedge),\qquad \xi\in\Xi,
$$

where $\xi$ is a six-dimensional twist and $\Xi$ is an uncertainty set. A simpler three-axis system can maintain independent translation intervals and a small angular bound.

A claim about machine travel or collision should quantify over all transforms in the allowed uncertainty set. If that is too expensive, the certificate must state that only the nominal transform was simulated.

## Worked example: work-frame travel

Suppose a toolpath lies within $x\in[0,180]$ in work coordinates. The machine travel is $x\in[0,200]$. It is incorrect to conclude that the path fits unless the work-to-machine transform is known. With a $30$ mm positive offset, the path reaches machine $x=210$ and violates travel.

The correct check is:

$$
\forall q_w\in Q_w,\ \forall T\in\mathcal{T}_{m\leftarrow w},\quad
Tq_w\in Q_m.
$$

For interval boxes and pure translations, this reduces to interval addition. For rotations, the enclosure must account for coupling among axes.

## Design rules

\begin{designrule}
Make units, frames, and tool-assembly identity explicit in the IR. Treat frame transforms and tool dimensions as assumptions with uncertainty, not as unexamined scalar constants.
\end{designrule}

## Exercises

1. Define types for machine, work, stock, and part frames. Show one invalid operation the type system should reject.
2. Derive the inverse of an $SE(3)$ transform.
3. Explain why holder collision and target gouge require different tool solids.
4. Propagate an interval translation through an axis-aligned path bounding box.
5. Design a serializable `ToolAssembly` schema with uncertainty fields.
6. Identify the units and frame of every number in `G1 X10 Y20 F600`.
7. Explain why a runtime-checked constructor is still necessary when TypeScript brands are used.

# Four Semantic Views

> **Learning objectives.** The reader should be able to explain denotational, operational, axiomatic, and trace semantics; select the appropriate view for a question; and connect the views through consistency conditions.

![Four complementary semantic views of a CAM program.](figures/semantic_views.png){width=72%}

No one semantic style answers every engineering question. A credible CAM compiler uses several views of the same language.

## Denotational semantics

Denotational semantics assigns a mathematical meaning to a program. For manufacturing intent, the meaning is often a set of acceptable outcomes. For a path, it may be a continuous curve. For a command, it may be a relation on states.

Let a machine state be:

$$
\sigma=(q,\dot{q},F,W,T,S_p,C,S_{stock},P,O,M,t),
$$

where the components include axis state, frame graph, work system, active tool, spindle and coolant state, stock, target part, obstacles, modal/controller state, and time.

A command can denote:

$$
\llbracket c\rrbracket:\Sigma\to
\mathcal{P}(\Sigma\times\mathrm{Trace}\times\mathrm{Outcome}).
$$

The powerset captures nondeterminism and failure.

## Operational semantics

Operational semantics explains execution step by step [R6]. A small-step relation has the form:

$$
\langle c,\sigma\rangle\to\langle c',\sigma'\rangle.
$$

A big-step relation for an atomic command is:

$$
\langle c,\sigma\rangle\Downarrow(\sigma',e),
$$

where $e$ is an event or trace fragment.

A simplified cutting rule is:

$$
\frac{
\operatorname{Homed}(\sigma)\quad
\operatorname{WCSKnown}(\sigma)\quad
\operatorname{ToolLoaded}(\sigma,T)\quad
\operatorname{SpindleValid}(\sigma)\quad
f>0
}{
\langle\operatorname{Cut}(\gamma,T,f),\sigma\rangle
\Downarrow
\left(
\sigma[q:=\operatorname{end}(\gamma),
S_{stock}:=S_{stock}\setminus\operatorname{Sweep}(T,\gamma)],
\operatorname{motionTrace}(\gamma,f)
\right)
}.
$$

Rules like this are executable specifications for interpreters and validators.

## Axiomatic semantics

Axiomatic semantics reasons with assertions before and after commands [R4, R5]. A Hoare triple is:

$$
\{P\}\ c\ \{Q\}.
$$

For a cut:

$$
\{
\operatorname{Homed}\land
\operatorname{WCSKnown}\land
\operatorname{Tool}=T\land
\operatorname{SpindleOn}\land
\operatorname{PathSafe}(\gamma)
\}
$$

$$
\operatorname{cut}(\gamma,T,f)
$$

$$
\{
\operatorname{Pose}=\operatorname{end}(\gamma)\land
S'=S\setminus\operatorname{Sweep}(T,\gamma)
\}.
$$

This view is natural for preflight requirements, API contracts, and pass invariants.

## Trace and temporal semantics

A controller protocol unfolds over time and includes concurrency. Temporal logic reasons about whole traces [R8, R34]. Typical safety properties use “always” $\Box$:

$$
\Box(\operatorname{Motion}\Rightarrow
\operatorname{Homed}\land\operatorname{Authorized}).
$$

Liveness properties use “eventually” $\Diamond$:

$$
\Box(\operatorname{AbortRequested}\Rightarrow
\Diamond(\operatorname{Stopped}\lor\operatorname{Faulted})).
$$

Artifact binding can also be temporal:

$$
\Box(\operatorname{ExecuteHash}=h\Rightarrow\operatorname{StoredHash}=h).
$$

A static list of canonical commands cannot establish these properties. They belong to the host-controller state machine.

## Consistency among views

The semantic views should agree. If an operational interpreter executes a command from $\sigma$ to $\sigma'$, then $(\sigma,\sigma')$ should belong to the denotational relation. If a Hoare triple is proved, every operational execution starting in a state satisfying $P$ should finish in a state satisfying $Q$, subject to its termination assumptions.

These consistency theorems make the semantics more than parallel documentation. They allow one view to justify a checker implemented in another.

## Which view to use

| Question | Best primary view |
|---|---|
| What final shapes are acceptable? | Denotational |
| What does this modal block do next? | Operational |
| What preflight is required? | Axiomatic |
| Can abort remain pending forever? | Temporal |
| Does a pass preserve all traces? | Denotational/refinement |
| Can the program reach a cut with spindle off? | Operational + abstract interpretation |
| Does the protocol execute the acknowledged bytes? | Temporal |

## Worked example: probe semantics

A probe command is a useful test of semantic completeness. Denotationally, it maps an initial state to a set of possible contact measurements. Operationally, it advances until contact, limit, or failure. Axiomatic reasoning requires a known probe direction, maximum distance, and valid probe state. Temporally, the host must eventually receive either a measurement or a terminal fault; a silent timeout is not a successful no-contact result.

A G-code emitter that treats the commanded endpoint as the measured endpoint confuses syntax with observation. The result of probing is produced by execution, not known at compile time.

## Exercises

1. Give denotational and operational semantics for a dwell command.
2. Write a Hoare triple for tool selection.
3. State a temporal property for feed hold.
4. Explain why liveness generally requires fairness or environmental assumptions.
5. Describe a consistency theorem between a G-code interpreter and canonical IR.
6. Model a probe no-contact failure in all four semantic views.

# Nondeterminism, Approximation, and Refinement

> **Learning objectives.** The reader should be able to distinguish implementation choice from physical uncertainty, state exact and bounded refinement relations, and compose error bounds with explicit metrics.

## Sources of nondeterminism

Nondeterminism enters a CAM system in several ways.

**Specification freedom** arises because an intent permits many implementations. The compiler may select any feasible strategy.

**Algorithmic nondeterminism** arises from parallel scheduling, hash iteration, randomized search, or solver tie-breaking. Reproducible builds should control or record it.

**Controller nondeterminism** includes asynchronous status messages, buffering, alarms, and timing-dependent transitions.

**Physical uncertainty** includes probe noise, backlash, tool runout, thermal drift, spindle regulation, and servo error.

These sources should not be represented by one generic “tolerance.” Choice, uncertainty, and error have different semantics.

## Exact preservation

A semantics-preserving pass satisfies:

$$
\operatorname{Sem}(O)=\operatorname{Sem}(I).
$$

Examples include alpha-renaming, canonical data reordering, or modal compression when the interpreted canonical trace is identical. Exact preservation is a strong claim and should be reserved for passes whose semantics really match.

## Trace refinement

A lowering pass often resolves choices:

$$
\operatorname{Traces}(O)\subseteq\operatorname{Traces}(I).
$$

For example, a high-level traverse permits any safe free-space route. Lowering to retract, XY motion, and descent selects one route. The target is not equivalent to the source because it has fewer behaviors; it refines it.

Abadi and Lamport's refinement mappings formalize how concrete states and traces implement abstract specifications [R9]. The same idea applies across CAM IR levels.

## Bounded geometric refinement

A curve-linearization pass may satisfy:

$$
d_H(\gamma_I,\gamma_O)\le\varepsilon.
$$

That is not automatically enough for physical safety. The checker must establish how centerline error affects the swept tool and holder, including orientation and frame uncertainty. A bound on an arc's sagitta is useful only if it survives subsequent rounding and controller interpolation.

## Quantitative error composition

Suppose a pass $f$ is Lipschitz with constant $L_f$ under the chosen metric and introduces local error $\varepsilon_f$. If the input already has error $\varepsilon_{in}$, then:

$$
\varepsilon_{out}\le L_f\varepsilon_{in}+\varepsilon_f.
$$

For a sequence of passes:

$$
\varepsilon_n\le
\left(\prod_{i=1}^{n}L_i\right)\varepsilon_0
+
\sum_{k=1}^{n}
\left(\prod_{j=k+1}^{n}L_j\right)\varepsilon_k.
$$

A plain scalar sum is valid only under compatible metrics and amplification assumptions. Translation error, angular error, surface-normal error, and maximum gouge depth should remain distinct until a sound propagation rule combines them.

## Approximation direction

A safety checker must know whether an approximation is an under- or over-approximation.

Let $X$ be the true set. Maintain:

$$
X^-\subseteq X\subseteq X^+.
$$

- $X^+$ is an outer enclosure and is appropriate for proving absence of collision.
- $X^-$ is an inner enclosure and is appropriate for proving guaranteed removal.
- A point sample with no enclosure theorem is neither.

![Inner and outer approximations support different proof directions.](figures/inner_outer_geometry.png){width=80%}

## Unknown is a valid result

A checker should have at least these outcomes:

- proved exact;
- proved within a bound;
- refuted with a counterexample;
- inconclusive because the available representation is too coarse;
- not checked;
- conditional on explicit assumptions.

Conflating inconclusive with safe is a semantic error. Refinement-based compiler design permits rejection. A pass may decline to lower an operation it cannot implement within its budget.

## Worked example: arc lowering

For a circular arc of radius $R$ approximated by chords with half-angle $\theta$, the sagitta is:

$$
s=R(1-\cos\theta).
$$

To keep $s\le\varepsilon$, choose:

$$
\theta\le\arccos\left(1-\frac{\varepsilon}{R}\right).
$$

The arc pass can emit a witness containing $R$, total sweep, segment count, and maximum sagitta. An independent checker recomputes the bound and verifies endpoints. The postprocessor must then account for decimal rounding. If each coordinate is rounded by at most $\rho$, the final positional error needs an additional norm-dependent term.

## Design rules

\begin{designrule}
Every approximation must declare its metric, direction, bound, assumptions, and artifact scope. A checker that cannot prove the bound must return inconclusive rather than upgrading sampled evidence into a guarantee.
\end{designrule}

## Exercises

1. Distinguish source-level nondeterminism from physical uncertainty in a pocket operation.
2. Give an example of trace refinement that is not equivalence.
3. Derive the number of linear segments needed for a $20$ mm radius half-circle with $0.01$ mm sagitta tolerance.
4. Explain why a sampled toolpath is not automatically an outer approximation.
5. Compose two error bounds with Lipschitz constants $2$ and $0.5$.
6. Design a result type that separates refuted, inconclusive, and not checked.
7. Give an example where an under-approximation is unsafe for collision checking.

\part{Part II - Language and Intermediate Representation Design}

# JavaScript as a Staged Macro Language

> **Learning objectives.** The reader should be able to separate an authoring language from the stable CAM language, explain staging and elaboration, and design a deterministic capability-limited script boundary.

## The convenience and danger of embedded JavaScript

JavaScript is attractive as a CAM authoring language. It has familiar control flow, functions, data structures, packages, editors, and a large ecosystem. Parametric geometry becomes concise:

```ts
for (let i = 0; i < holeCount; i++) {
  drill({
    at: p(origin.x + i * spacing, origin.y, topZ),
    diameter: mm(3),
    depth: mm(8),
  });
}
```

But unrestricted JavaScript is a poor stable semantic core. It can inspect time, randomness, environment variables, files, network state, prototypes, and host globals. It can loop forever, mutate shared objects, invoke asynchronous callbacks after lexical scopes have ended, or depend on implementation details of the runtime.

The solution is not to discard JavaScript. It is to give it a precise role: **JavaScript is a macro language that constructs an inert CAM abstract syntax tree.**

## Two languages, not one

The authoring language includes JavaScript syntax and its computational power. The stable CAM language is a serializable AST with explicit constructors and no executable closures.

```text
JavaScript source
     |
     | evaluate in isolated staged environment
     v
Immutable authoring AST
     |
     | elaborate names, units, frames, tools
     v
Plan IR
```

After staging, no compiler pass should call user-provided functions. The AST should contain only finite data, identifiers, source spans, and references to declared artifacts.

This resembles multi-stage programming: one program executes now to construct another program that will be analyzed and compiled later [R37]. The staging boundary is a semantic boundary and a security boundary.

## Capability design

The script should receive an explicit capability object:

```ts
interface CamAuthoringCapabilities {
  units: UnitConstructors;
  geometry: GeometryConstructors;
  tools: ToolRegistryBuilder;
  plan: PlanBuilder;
  diagnostics: DiagnosticSink;
}
```

Capabilities prevent accidental ambient access, but ordinary lexical shadowing is not a security sandbox. Same-realm evaluation with `new Function` still exposes standard constructors and prototype chains. A hostile or simply defective script can also block the event loop indefinitely.

A production design should execute scripts in a separately terminable worker, process, or isolate with:

- no ambient network or filesystem access unless explicitly granted;
- a wall-clock deadline enforced outside the script;
- a memory limit;
- deterministic time and randomness sources;
- a versioned API module;
- structured input and output serialization;
- process termination on cancellation;
- no shared mutable object graph with the compiler.

## Determinism and declared inputs

A reproducible authoring run should be modeled as:

$$
\operatorname{eval}(	ext{source},\text{apiVersion},\text{inputs},\text{seed})
=\text{AST}.
$$

Every input must be declared and content-addressed. If a script reads a mesh, tool library, material table, or project parameter, the compilation record should include its hash.

```ts
interface ScriptEvaluationRecord {
  sourceHash: Hash;
  languageVersion: string;
  apiVersion: string;
  inputArtifacts: readonly ArtifactRef[];
  deterministicSeed?: bigint;
  resultAstHash: Hash;
  diagnostics: readonly Diagnostic[];
}
```

The same record should be sufficient to reproduce the AST in a clean environment.

## Scope combinators

An authoring API may use scoped operations:

```ts
withTool(tool, () => {
  withFeed(mmPerMin(400), () => {
    pocket(feature);
  });
});
```

A synchronous implementation usually saves state, invokes the callback, and restores state in `finally`. If the callback returns a promise, restoration can happen before awaited work completes. The apparent lexical semantics are broken.

There are three sound choices:

1. Prohibit asynchronous callbacks and detect promises at runtime.
2. Make the combinator explicitly asynchronous and await the callback before restoration.
3. Avoid dynamic scopes in the AST builder and pass immutable context explicitly.

For a deterministic macro language, the third option is often simplest.

## Mutability at the boundary

If a tool object is registered and then retained by reference, later user mutation can change the plan after validation:

```ts
const tool = { diameter: mm(3.175), fluteLength: mm(12) };
registerTool("T1", tool);
tool.diameter = mm(8); // changes meaning if reference was retained
```

The builder should deep-copy and freeze boundary objects, or convert them immediately into canonical immutable records. Hashing an object only helps if the object cannot change afterward.

## Worked example: staged pocket program

A good authoring run produces data such as:

```ts
const ast: AuthoringProgram = {
  version: "cam-authoring/1",
  tools: [{
    id: "T1",
    geometry: { kind: "flatEndMill", diameter: 3.175, fluteLength: 12 },
    source: { file: "job.cam.js", line: 3, column: 14 },
  }],
  operations: [{
    kind: "rectPocket",
    featureId: "P1",
    frame: "work:G54",
    origin: [10, 10, 0],
    size: [30, 20],
    depth: 4,
    tool: "T1",
    radialAllowance: 0.2,
    axialAllowance: 0.2,
    source: { file: "job.cam.js", line: 8, column: 3 },
  }],
};
```

The AST contains no closure that can later inspect the host environment. It can be validated, displayed, serialized, hashed, diffed, and compiled by another implementation.

## Design rules

\begin{designrule}
Use JavaScript to construct an inert, immutable, content-addressed AST. Do not make the JavaScript realm, closures, mutable objects, or ambient globals part of the CAM semantics.
\end{designrule}

## Exercises

1. List five ambient JavaScript capabilities that damage reproducibility.
2. Design a JSON-serializable AST node for a probing operation.
3. Explain why a timeout checked after a script returns is not an enforced timeout.
4. Show how a synchronous scope combinator fails with an async callback.
5. Define an isolation protocol between a Studio UI and a worker process.
6. Specify which fields must be hashed to reproduce an authoring run.

# A Multi-Level IR Architecture

> **Learning objectives.** The reader should be able to assign concerns to IR levels, define legality at each stage, and avoid both a monolithic universal IR and premature lowering.

## Why one IR is not enough

A universal node type such as:

```ts
interface Operation {
  kind: string;
  data: unknown;
}
```

appears flexible but erases the guarantees that make passes understandable. At the other extreme, lowering directly from authoring syntax to G-code forces every planner to know controller details and destroys manufacturing provenance.

A multi-level compiler retains the right information at each stage and defines explicit conversion points. MLIR demonstrates the value of multiple dialects and legality-controlled transformations for domain-specific compilation [R16]. A CAM compiler benefits even more because its abstraction levels correspond to distinct physical meanings.

![A ladder of CAM intermediate representations.](figures/ir_ladder.png){width=98%}

## Authoring AST

The authoring AST preserves:

- source spans;
- names and declarations;
- macros already expanded into data;
- user-level concepts;
- unresolved references where diagnostics benefit.

It should exclude arbitrary executable values after the staging boundary.

## Elaborated Plan IR

Elaboration resolves:

- units;
- frames;
- tool references;
- geometry artifact references;
- defaults;
- scope-derived settings;
- identifier uniqueness;
- finite values and domain constraints.

The elaborated IR is the first stable, language-independent project representation. It should be possible to save it and compile it without re-running JavaScript.

## Manufacturing Intent IR

Intent IR represents features and operations:

- pockets, holes, slots, surfaces, profiles;
- roughing and finishing requirements;
- allowances and tolerances;
- protected and permitted regions;
- dependencies and setup requirements;
- process constraints.

It deliberately excludes exact tool-center paths.

## Geometric Toolpath IR

Toolpath IR contains continuous or piecewise-continuous curves with process semantics:

```ts
interface CuttingPath<F extends FrameId> {
  geometry: Path<F>;
  tool: ToolRef;
  feedPolicy: FeedPolicy;
  operation: OperationRef;
  phase: "entry" | "rough" | "finish" | "leadOut";
  directionality: "reversible" | "forwardOnly";
}
```

It should still be independent of a controller's modal syntax.

## Scheduled Program IR

Scheduling introduces:

- a total or partially ordered operation sequence;
- path orientation choices;
- entries, retracts, and links;
- tool changes;
- probe dependencies;
- feed schedules or time laws;
- evolving stock-state references.

This is where semantics become stateful. A link that was safe before roughing may be unnecessary afterward; a path that was safe after roughing may be unsafe before it.

## Machine IR

Machine lowering resolves:

- axis and kinematic capabilities;
- supported interpolation primitives;
- machine and work frames;
- travel limits;
- spindle and feed limits;
- tool-change behavior;
- probe and accessory capabilities;
- safe expansion of abstract traverses.

Every remaining operation must be supported by the selected machine profile or rejected.

## Controller IR

Controller IR makes the controller's semantics explicit without committing to final formatting. It may contain:

- set units;
- select plane;
- select work offset;
- set absolute mode;
- linear and arc motion;
- probe cycle;
- spindle and accessory actions;
- upload metadata;
- program end.

The controller IR should have an interpreter. Final G-code text is then a serialization of this IR plus an optional modal-compression optimization.

## Serialized Job Bundle

The final bundle contains more than `.nc` bytes:

- exact controller program bytes;
- content hash;
- machine and firmware profile hash;
- tool and holder manifest;
- stock, target, fixture, and frame artifacts;
- certificate graph;
- declared runtime assumptions;
- optional preview data generated from the same artifact.

## Legality

Each IR has a legality predicate. Examples:

```text
Authoring AST legal:
  no executable closures; all nodes schema-valid

Plan IR legal:
  all units/frames/references resolved; all values finite

Toolpath IR legal:
  all paths continuous; operation provenance total

Machine IR legal:
  every operation supported; all coordinates machine-resolved

Controller IR legal:
  initial modal state explicit; no unknown raw effects

Job bundle legal:
  hashes match; required claims present; assumptions well formed
```

A conversion should fail when it cannot produce legal output.

## Validation is evidence, not a dialect

A type named `ValidatedProgram` is useful as an API guard, but validation does not create a new language. It creates evidence about an artifact.

```ts
interface Certified<T> {
  artifact: T;
  artifactHash: Hash;
  claims: readonly Claim[];
  evidence: readonly Evidence[];
}
```

Different claims attach at different stages. Path continuity evidence belongs to a toolpath artifact; modal equivalence belongs to controller bytes; runtime identity belongs to an execution instance. One global boolean brand cannot express this graph.

## Exercises

1. Assign each concern to an IR level: source span, scallop tolerance, tool-center curve, G17 plane, decimal formatting, upload filename.
2. Write legality predicates for a probing node in Plan IR and Machine IR.
3. Explain why a preview mesh should reference an artifact hash.
4. Give an example of information that must survive planning for later diagnostics.
5. Design an IR conversion that is partial and returns structured diagnostics.
6. Compare a multi-level IR with a universal stringly typed operation list.

# Paths and Curves as Composable Objects

> **Learning objectives.** The reader should be able to model paths categorically, distinguish path image from parameterization, identify the failure of approximate equality, and define safe composition contracts.

## Paths as arrows

A path has a start and end pose:

$$
p:A\to B.
$$

If $q:B\to C$, then composition is defined:

$$
q\circ p:A\to C.
$$

A stationary path $\mathrm{id}_A:A\to A$ acts as an identity, and composition is associative. This is the free-category intuition behind a path builder.

```ts
interface Path<F extends FrameId> {
  frame: F;
  start: Point3<F>;
  end: Point3<F>;
  segments: readonly Segment<F>[];
}
```

A builder that derives `end` from appended segments establishes a valuable representation invariant: the declared endpoint cannot disagree with the final segment.

## Geometry versus parameterization

A curve is often written:

$$
\gamma:[0,1]\to\mathbb{R}^3.
$$

Two parameterizations can trace the same geometric image at different rates. For geometric path equivalence, curves are commonly considered modulo monotone reparameterization. Concatenating two curves changes parameterization even when the physical trace is unchanged.

This matters because a geometric path is not a trajectory. Time enters later through a monotone map:

$$
s:[0,T]\to[0,1],\qquad x(t)=\gamma(s(t)).
$$

Velocity, acceleration, jerk, and controller following error belong to $s(t)$ and machine dynamics, not to the curve alone.

## Segment algebra

Useful primitive segments include:

- line segments;
- circular or helical arcs with geometric center, axis, and sweep;
- splines with declared basis and knot domain;
- polylines with explicit approximation provenance;
- stationary segments or dwells at a pose.

Controller-specific arc offsets such as `I`, `J`, and `K` do not belong in geometric path IR. They are one encoding of the same geometry under a selected plane and endpoint convention.

## Exact joins and approximate joins

Suppose path composition accepts endpoints when:

$$
d(a.end,b.start)<\varepsilon.
$$

This relation is not transitive. It cannot serve as exact object identity in a category. Repeated approximate joins can drift, and topology construction can merge unrelated endpoints.

Safer designs include:

1. Canonical snapping to exact grid or symbolic point identities.
2. Explicit join witnesses recording the displacement.
3. A path result carrying accumulated endpoint uncertainty.
4. Exact rational or integer coordinates for topology decisions.
5. A metric-enriched algebra where composition returns a new error bound.

```ts
interface JoinWitness<F extends FrameId> {
  leftEnd: Point3<F>;
  rightStart: Point3<F>;
  displacement: Mm;
  repair: "none" | "snap-right-to-left" | "insert-link";
}
```

An inserted link is not merely a numerical repair. It is a new motion that needs cut or traverse semantics and clearance checking.

## Reversal and orientation

A geometric path can often be reversed, but a machining action may not be reversible. Direction affects:

- climb versus conventional milling;
- lead-in and lead-out geometry;
- cutter compensation;
- helical entry;
- probe direction;
- one-way process constraints;
- stock engagement.

Directionality belongs in metadata or the action type. An optimizer must not reverse paths solely because the point list is reversible.

## Path continuity is not enough

A syntactically continuous path may still be invalid:

- an arc's declared endpoint may not lie on its circle;
- a polyline segment may include a first point inconsistent with the cursor;
- a spline may have a singular or non-finite evaluation;
- curvature may exceed process or dynamics limits;
- the path may cross forbidden material;
- the frame may be inconsistent.

Distinguish representation invariants from semantic properties.

## Worked example: arc witness

An arc segment can be represented as:

```ts
interface ArcSegment<F extends FrameId> {
  to: Point3<F>;
  center: Point3<F>;
  axis: UnitVec3;
  sweep: Radians;
}
```

A checker given the start point verifies:

1. the axis is unit length within a certified bound;
2. start and end radial distances agree within tolerance;
3. the declared sweep rotates the start radius to the end radius;
4. any axial displacement is consistent with a helical interpretation;
5. all values are finite;
6. the chosen linearization, if any, satisfies its sagitta bound.

## Design rules

\begin{designrule}
Use path composition to enforce endpoint discipline, but do not confuse numerical proximity with equality or structural continuity with machining safety. Make every repair an explicit, semantically classified operation.
\end{designrule}

## Exercises

1. Prove associativity of exact segment-list concatenation.
2. Explain why parameterized-curve equality is too strict for geometric paths.
3. Design a metric-aware result type for approximate concatenation.
4. Give three reasons a path reversal may be illegal.
5. Specify checks for a helical arc.
6. Construct three endpoints that demonstrate non-transitivity of tolerance joins.
7. Explain why automatically inserting a line between discontinuous cut paths can be dangerous.

# Actions, Effects, and Indexed Commands

> **Learning objectives.** The reader should be able to model commands as effectful computations, explain Kleisli composition, and use indexed state to encode legal command sequencing.

## A path is not an action

The same curve can denote a rapid traverse, cutting feed, probe motion, inspection scan, or air move. The geometry alone does not determine effects. A machining command changes machine and stock state, can fail, emits a trace, and may produce a value.

A simple state-and-error command type is:

$$
M(A)=\Sigma\to\operatorname{Result}(A\times\Sigma,E).
$$

In TypeScript:

```ts
type Command<A> =
  (state: MachineState) =>
    Result<{ value: A; state: MachineState }, CommandError>;
```

A probe command returns a measurement; a cut commonly returns `void` but changes stock and pose.

## Why ordinary composition fails

Let:

$$
f:A\to M(B),\qquad g:B\to M(C).
$$

Ordinary composition $g\circ f$ is ill typed because $f$ returns $M(B)$ while $g$ expects $B$. A monad supplies `bind`:

$$
\operatorname{bind}:M(B)\times(B\to M(C))\to M(C).
$$

For a result-and-state computation, `bind` propagates errors and threads the updated state into the next command.

```ts
function bind<A, B>(ma: Command<A>, f: (a: A) => Command<B>): Command<B> {
  return state0 => {
    const ra = ma(state0);
    if (!ra.ok) return ra;
    return f(ra.value.value)(ra.value.state);
  };
}
```

This is Kleisli composition. Monads provide a disciplined way to compose effectful computations [R10, R11].

## CNC effects

A realistic command effect includes more than mutable state:

```ts
interface CommandResult<A> {
  value: A;
  state: MachineState;
  trace: readonly Event[];
  assumptionsUsed: readonly AssumptionRef[];
  claimsProduced: readonly Claim[];
}
```

Potential effects include:

- failure and alarms;
- machine-state mutation;
- stock removal;
- logging and provenance;
- nondeterministic measurement;
- asynchronous controller interaction;
- resource use and time;
- uncertainty propagation.

An effect system can record which operations read or modify which resources [R14].

## Indexed commands

A plain state monad does not express that the type of legal state changes. A parameterized or indexed command type does:

$$
\operatorname{Cmd}\langle S_{before},S_{after},A\rangle.
$$

Composition requires the post-state index of one command to match the pre-state index of the next [R13]. Typestate uses the same idea to restrict operations by protocol state [R12].

```ts
type StartSpindle<S extends Homed & HasTool> =
  Cmd<S, S & SpindleRunning, void>;

type Cut<S extends Homed & HasTool & SpindleRunning & KnownWcs> =
  Cmd<S, S & AtPathEnd, void>;
```

The source API can make impossible sequences difficult to construct.

## Limits of type-level safety

TypeScript types are erased. A forged value, unchecked deserialization, stale controller state, or physical mismatch can violate the index. Type-level typestate proves a property of the host program under its model; it does not prove the machine is physically in that state.

Runtime preflight must re-establish assumptions at the execution boundary.

## Algebraic effects versus monolithic state

One large `MachineState` can become difficult to reason about. An alternative is to describe effects separately:

```ts
type Effect =
  | ReadPose
  | RequireHomed
  | SelectTool
  | SetSpindle
  | Move
  | RemoveStock
  | Probe
  | EmitDiagnostic;
```

Handlers interpret these effects for simulation, validation, preview, or controller execution. This can improve modularity, but it still requires a coherent ordering and state model. The key is not the syntax of monads versus effect handlers; it is the explicit representation of effects and their laws.

## Worked example: probe then offset

A probe returns a measured coordinate:

```ts
type Probe = Cmd<ProbeReady, ProbeReady, Measurement>;
type SetWorkOrigin =
  (m: Measurement) => Cmd<ProbeReady, KnownWcs, void>;
```

Kleisli composition connects the returned value to the next operation:

```ts
const establishWcs = probeSurface(direction, maxTravel)
  .flatMap(measurement => setWorkOrigin(measurement));
```

The data dependency is explicit. A command list that merely places `probe` before `set offset` without binding the result is semantically incomplete.

## Exercises

1. Implement `pure` and `bind` for a result-and-state command type.
2. State the three monad laws and explain their practical value for command sequencing.
3. Design indexed states for unhomed, homed, tool-selected, and spindle-running modes.
4. Explain one invariant that TypeScript typestate cannot establish about a physical machine.
5. Model a probe command that can return contact, no contact, or alarm.
6. Compare a state monad with an explicit effect algebra for CAM.

# State Tokens, SSA, and Ordering

> **Learning objectives.** The reader should be able to use an SSA-style state token to make effects explicit, construct def-use dependencies, and identify which transformations are legal around stateful commands.

## The machine state as a linear resource

A practical IR need not encode every typestate distinction in TypeScript generics. It can make ordering explicit with a state token. Each effectful operation consumes one token and produces the next.

![An SSA-style machine state token threads through commands.](figures/state_token.png){width=98%}

```text
%s0 = machine.initial
%s1 = machine.require_homed %s0
%s2 = tool.select %s1 @T1
%s3 = spindle.start %s2 12000rpm
%s4 = motion.cut %s3 path=@p feed=400
%s5 = spindle.stop %s4
```

The token is not the full runtime state. It is an ordering and dependency witness.

## Relation to SSA

Static single assignment form gives each value one definition and makes data dependencies explicit [R15]. A machine-state token applies the same discipline to side effects. Operations cannot be silently reordered across token dependencies.

Pure geometry computations need no token:

```text
%p1 = path.offset %feature by=1.2mm
%p2 = path.reverse %p1
```

Effectful program construction does:

```text
%s1 = motion.traverse %s0 to=%p1.start
%s2 = motion.cut %s1 path=%p1
```

## Multiple resources

One global token is simple but can over-serialize independent work. A richer IR can use separate tokens for:

- controller state;
- stock state;
- tool library state;
- measurement environment;
- diagnostic/provenance stream.

However, splitting resources requires precise alias and commutativity rules. Two cuts that affect disjoint stock regions might commute geometrically but not mechanically if they change support or linking clearance.

For an initial implementation, a single machine/process token is usually safer.

## Probe values and control flow

SSA makes measurements explicit values:

```text
%m, %s1 = probe.toward %s0 direction=-Z max=10mm
%t       = frame.from_probe %m datum=@top_surface
%s2      = frame.install %s1 %t as=G54
```

A failed probe can branch:

```text
switch %m.status:
  contact -> continue
  no_contact -> abort
  alarm -> quarantine_session
```

The IR can represent merge points with block arguments or phi-like values. A validator must ensure that state invariants hold along every incoming path.

## Effect summaries

Optimization and scheduling require summaries:

```ts
interface EffectSummary {
  reads: readonly ResourceRegion[];
  writes: readonly ResourceRegion[];
  requires: readonly Predicate[];
  ensures: readonly Predicate[];
  mayFail: readonly FailureClass[];
}
```

A pass may commute two operations only if their effects are independent and the reordered preconditions remain valid.

## Linear and affine use

A state token should usually be consumed exactly once. Duplicating it would fork the machine into two contradictory futures. Dropping it can omit required shutdown or recovery behavior.

A linear type system enforces exactly-once use; an affine system permits dropping but not duplication. Most mainstream TypeScript code cannot enforce this statically, but the IR verifier can check def-use counts.

## Worked example: preventing an unsafe reorder

Suppose an optimizer sees:

```text
%s1 = spindle.start %s0 12000rpm
%s2 = motion.cut %s1 @p
%s3 = spindle.stop %s2
```

Moving `spindle.stop` before the cut would require consuming `%s1` and producing a new state passed to the cut. The cut's `SpindleRunning` requirement fails. The token graph exposes the invalid transformation.

## Exercises

1. Convert a small imperative command list into state-token SSA.
2. Explain why duplicating a machine state token is unsound.
3. Design a verifier for single-definition and single-consumption token use.
4. Show a legal reordering of two pure geometry operations.
5. Give a case where two cuts in disjoint regions still should not commute.
6. Model a branch after probing and the merge of its safe paths.

# Provenance, Identity, and Reproducibility

> **Learning objectives.** The reader should be able to design total provenance, content-address artifacts, distinguish identity from display names, and bind diagnostics and certificates to exact inputs.

## Provenance is semantic data

When a final move fails a check, the system should explain which source operation, feature, strategy, and compiler pass produced it. Provenance is therefore not an optional debug string. It supports:

- diagnostics;
- certificate dependency graphs;
- incremental recompilation;
- audit and review;
- visual selection in the UI;
- comparison between compiler versions;
- fault localization.

## A provenance chain

```ts
interface Provenance {
  sourceSpan?: SourceSpan;
  authoringNode?: NodeId;
  operation?: OperationId;
  feature?: FeatureId;
  strategy?: { id: string; version: string };
  passHistory: readonly PassRecord[];
  parentArtifacts: readonly Hash[];
}
```

Every transformation either preserves provenance, refines it, or introduces a synthetic operation with an explicit reason such as `safety-retract` or `postprocessor-spindle-stop`.

## Content addressing

An artifact hash should cover canonical serialization of:

- semantic content;
- schema version;
- relevant configuration;
- referenced artifact hashes.

A display filename is not identity. Two jobs named `part.nc` may differ; the same job may have several names.

Canonical serialization must define:

- map key order;
- number format;
- treatment of negative zero;
- Unicode normalization;
- omitted versus null fields;
- endianness for binary data;
- schema versioning.

## Reproducible passes

A pass result should be a function of explicit inputs:

$$
O=F(I,C,V,S),
$$

where $C$ is configuration, $V$ identifies the pass implementation, and $S$ is any declared random seed. Hidden time, locale, thread interleaving, or unordered iteration can break reproducibility.

Reproducibility does not guarantee correctness, but it makes evidence, debugging, and regression analysis tractable.

## Machine and firmware identity

A machine profile named `z1` is not sufficient if firmware revisions change protocol or motion semantics. The executable bundle should identify:

- machine model and configured limits;
- controller dialect and firmware compatibility range;
- relevant capability flags;
- postprocessor version;
- calibration profile version;
- known semantic deviations.

Runtime preflight compares live identity with the bundle assumptions.

## Provenance through optimization

An optimizer may merge, split, or reorder paths. It should retain a many-to-many mapping:

```ts
interface OriginMap {
  outputRange: CommandRange;
  inputs: readonly {
    artifact: Hash;
    operation?: OperationId;
    pathRange?: ParameterInterval;
  }[];
  transformation: string;
}
```

This allows a gouge counterexample at final block 813 to highlight the source finishing operation and the arc-fitting pass that changed it.

## Worked example: cache key

A toolpath-planning cache key should include more than the feature geometry:

```text
hash(
  intentIR,
  targetMeshHash,
  stockHash,
  toolAssemblyHash,
  strategyIdAndVersion,
  planningTolerance,
  machine-relevant constraints,
  deterministicSeed
)
```

Omitting the tool hash can reuse a path computed for a different cutter. Omitting the tolerance can attach an outdated witness to a stricter request.

## Exercises

1. Design a canonical serialization rule for floating-point numbers.
2. Explain why a filename is not an artifact identity.
3. List the inputs to a deterministic contour-planning cache key.
4. Define provenance for an automatically inserted retract.
5. Describe how a certificate becomes stale after a machine-profile change.
6. Give one source of nondeterminism in JavaScript object iteration or parallel planning and show how to control it.

# Designing an Extensible CAM API

> **Learning objectives.** The reader should be able to design an API that is composable, explicit about context, extensible through strategies and kernels, and resistant to invalid states.

## Separate stable concepts from plugins

The stable API should expose semantic concepts:

- frames and units;
- stock, target, fixtures, and tools;
- manufacturing features and operations;
- paths and motion classes;
- tolerances, assumptions, and diagnostics;
- compilation and certification stages.

Strategies should be plugins:

```ts
interface Strategy<I extends OperationIntent, W> {
  id: string;
  version: string;
  supports(intent: I, context: PlanningContext): SupportResult;
  plan(intent: I, context: PlanningContext): Result<{
    paths: readonly PlannedPath[];
    witness: W;
  }, Diagnostic[]>;
}
```

A strategy may propose output; it should not mint final safety claims.

## Kernel independence

Geometry algorithms should depend on interfaces rather than one mesh library:

```ts
interface SurfaceOracle<F extends FrameId> {
  bounds(): Box3<F>;
  heightAtXY(x: Mm, y: Mm): Interval<Mm> | "outside";
  closestPoint(p: Point3<F>): ClosestPointBound<F>;
  raycast(ray: Ray3<F>): readonly HitBound<F>[];
}
```

Different kernels can implement exact B-rep queries, mesh acceleration structures, interval fields, or remote computation. The semantic contract says what bounds the result provides.

## Explicit contexts

Avoid ambient mutable settings such as “current feed,” “current tool,” or “current frame” inside planners. Pass immutable contexts:

```ts
interface PlanningContext {
  machine: MachineProfileRef;
  setup: SetupRef;
  activeTool: ToolRef;
  frame: FrameId;
  toleranceBudget: ErrorBudget;
  stockState: StockStateRef;
  seed: bigint;
}
```

The authoring API may offer convenient scopes, but elaboration should convert them into explicit fields.

## Result types and diagnostics

Exceptions are appropriate for programmer errors and violated internal invariants. User-level compilation failures should be values:

```ts
type CompileResult<T> =
  | { ok: true; value: T; diagnostics: readonly Diagnostic[] }
  | { ok: false; diagnostics: readonly Diagnostic[] };
```

A diagnostic should include severity, stable code, source provenance, artifact context, quantitative details, and suggested remediation.

## Escape hatches

Advanced users may need raw controller operations. An escape hatch should be isolated:

```ts
interface RawControllerBlock {
  text: string;
  declaredDialect: DialectId;
  declaredEffects?: EffectSummary;
  provenance: Provenance;
}
```

Self-declared effects are assumptions, not proof. An independent parser may establish actual effects for a supported grammar. Otherwise, affected analyses become unknown and production certification should fail closed.

## API layers

A pleasant system can offer three layers:

**Feature API** for most jobs:

```ts
roughPocket(feature, { tool: "T1", strategy: "adaptive" });
finishPocket(feature, { tool: "T2" });
```

**Path API** for custom machining geometry:

```ts
cut(path, { tool: "T1", feed: mmPerMin(350), intent: "finish" });
```

**Machine API** for exact canonical actions:

```ts
program.append(traverse(path, clearance));
program.append(dwell(seconds(1)));
```

Lower layers carry more responsibility and require stronger evidence.

## Law-driven API testing

Algebraic laws become property tests:

- path identity and associativity under exact endpoints;
- frame-transform identity and inverse;
- serialization round trip;
- deterministic planning under fixed inputs;
- pass idempotence for canonicalization;
- effect-summary conservativeness;
- certificate invalidation under changed dependencies.

The API design should make laws visible enough to test.

## Worked example: compiling explicitly

```ts
const authored = evaluateScript(source, scriptEnvironment);
const plan = elaborate(authored.ast, projectContext);
const intent = normalizeIntent(plan.value);
const proposed = strategyRegistry.plan(intent, planningContext);
const checkedPaths = checkPlanningWitness(intent, proposed);
const scheduled = schedule(checkedPaths, schedulingPolicy);
const machine = lowerToMachine(scheduled, z1Profile);
const controller = lowerToMakera(machine, makeraDialect);
const bytes = serialize(controller);
const final = validateFinalArtifact({
  intent,
  machine,
  controller,
  bytes,
  setup,
});
```

Each call has an explicit input and output. There is no hidden global “current job” whose meaning changes between preview and export.

## Exercises

1. Design a strategy interface for constant-Z waterline finishing.
2. Define a geometry-kernel query with a sound outer bound.
3. Explain when to use an exception versus a diagnostic result.
4. Design three API layers for drilling.
5. Specify how a raw controller block affects certification.
6. Write five algebraic or metamorphic properties for the API.
7. Explain why plugin version identity belongs in provenance.

\part{Part III - Compiler Passes and Correctness}

# Pass Contracts and Translation Validation

> **Learning objectives.** The reader should be able to define a compiler pass by a semantic relation, distinguish proof of a pass implementation from validation of one pass execution, and design witnesses and independent checkers.

## A pass is more than a function

A software interface often presents a pass as:

```ts
transform(input: I): O
```

The semantic interface is richer. A pass claims that its output is related to its input by a relation $R$:

$$
R(I,O).
$$

A certifying pass should produce both output and evidence:

```ts
interface PassResult<O, W> {
  output: O;
  witness: W;
  diagnostics: readonly Diagnostic[];
}
```

An independent checker validates the relation:

```ts
check(input: I, output: O, witness: W): CheckResult
```

![An untrusted pass produces output and a witness; a checker establishes the pass relation.](figures/pass_contract.png){width=92%}

## Classes of pass relation

Different passes require different correctness statements.

### Exact semantic preservation

$$
\operatorname{Sem}(O)=\operatorname{Sem}(I).
$$

Appropriate for canonicalization, alpha-renaming, or modal compression under a fixed interpreter.

### Trace refinement

$$
\operatorname{Traces}(O)\subseteq\operatorname{Traces}(I).
$$

Appropriate for scheduling or selecting one implementation allowed by an abstract operation.

### Bounded geometric refinement

$$
d(\operatorname{Geom}(O),\operatorname{Geom}(I))\le\varepsilon.
$$

Appropriate for sampling, fitting, and numerical lowering.

### Witness satisfaction

$$
O\in\llbracket I\rrbracket.
$$

Appropriate when a planner synthesizes one implementation of an intent.

### Feasible optimization

$$
\operatorname{Feasible}(O)\land R(I,O)\land J(O)\le J(I).
$$

Appropriate for reordering, link shortening, or feed optimization. “Optimal” additionally requires a lower bound or proof of global optimality.

## Verified compiler versus validating compiler

A verified compiler proves, once and for all, that the implementation of each pass satisfies its theorem for every accepted input. CompCert is the canonical example of pass-by-pass semantic preservation [R17]. This offers strong assurance but is expensive, particularly for evolving geometric algorithms.

Translation validation checks each actual compilation result. Pnueli and colleagues introduced the approach as an alternative to proving the optimizer itself [R18]. A validator receives $I$ and $O$ and decides whether the required relation holds. Alive2 applies this style to LLVM optimizations [R19].

For an experimental CAM compiler, translation validation is a pragmatic first target:

- strategy and optimization implementations remain ordinary TypeScript;
- each output carries a witness;
- a smaller checker validates the witness;
- failed validation rejects the artifact;
- frequently used checkers can later be mechanized.

## Checker soundness

The key theorem is:

$$
\operatorname{check}(I,O,W)=\mathrm{accept}
\Longrightarrow R(I,O).
$$

The checker need not be complete. It may reject valid outputs when evidence is insufficient. In safety-oriented compilation, false rejection is usually preferable to false acceptance.

Checker implementation should be simpler than the producer. A path planner may search thousands of alternatives; its checker should verify one proposed path. A nonlinear optimizer may use complex heuristics; its checker should validate feasibility and objective value.

## Pass descriptors

```ts
interface PassDescriptor {
  id: string;
  version: string;
  inputSchema: string;
  outputSchema: string;
  relation: RelationId;
  deterministic: boolean;
  configurationHash: Hash;
  implementationHash: Hash;
  checker: CheckerRef;
}
```

The relation identity is as important as the code version. A pass called `refine` might change from a Hausdorff guarantee to a normal-deviation guarantee; the certificate must not treat the claims as interchangeable.

## Local and global validation

Some pass properties are local:

- every arc endpoint lies on its circle;
- every formatted number reparses to the intended value within a bound;
- every operation is supported by the machine profile.

Others are global:

- path reordering preserves all precedence constraints;
- stock-dependent links remain collision-free in sequence;
- modal compression preserves the entire interpreted trace;
- cumulative error stays within budget.

A pass checker should be designed around the strongest dependencies of its claim, not around convenient implementation boundaries.

## Worked example: arc linearization validator

The producer emits a polyline and witness:

```ts
interface ArcLinearizationWitness {
  radius: Mm;
  sweep: Radians;
  chordTolerance: Mm;
  segmentCount: number;
  roundingBound: Mm;
}
```

The checker verifies:

1. the input arc is valid;
2. the output endpoints match;
3. each output vertex lies on the intended parameterized chord sequence or within a numerical enclosure;
4. the analytic sagitta bound is at most `chordTolerance`;
5. coordinate rounding contributes no more than `roundingBound`;
6. the total metric bound is composed correctly.

It does not trust the producer's stated segment count or radius.

## Exercises

1. State the pass relation for a path-reversal optimization.
2. Compare the trusted computing base of a verified compiler and a validating compiler.
3. Explain why a checker may be intentionally incomplete.
4. Design a witness for feed-rate clamping.
5. Identify a local and a global obligation for modal compression.
6. Write the soundness theorem for a scheduling validator.

# Elaboration and Static Checking

> **Learning objectives.** The reader should be able to define elaboration, distinguish normalization from validation, and derive a legal Plan IR from a permissive authoring AST.

## What elaboration does

Elaboration converts convenient surface syntax into explicit semantic data. It resolves omissions and rejects ambiguity before expensive planning begins.

Typical tasks include:

- resolve tool, frame, feature, and geometry names;
- convert all units to canonical internal units;
- expand defaults and scope-derived settings;
- assign stable identifiers;
- freeze mutable values;
- validate finite numbers and domain restrictions;
- establish source provenance;
- reject duplicate or dangling references;
- normalize orientation and coordinate conventions;
- construct a frame graph and check consistency.

## Static semantics

A typing judgment can be written:

$$
\Gamma\vdash e:\tau,
$$

where $\Gamma$ contains declarations and context. For a point constructor:

$$
\frac{
\Gamma\vdash x:\mathrm{Length}\quad
\Gamma\vdash y:\mathrm{Length}\quad
\Gamma\vdash z:\mathrm{Length}\quad
\Gamma\vdash F:\mathrm{Frame}
}{
\Gamma\vdash \operatorname{point}(x,y,z,F):\operatorname{Point3}\langle F\rangle
}.
$$

A pocket operation may require a planar boundary, positive depth, compatible tool, and known workpiece frame.

## Domain checking

Dimensional validity is weaker than domain validity. A feed of `NaN mm/min`, a negative tool diameter, or a zero spindle speed may carry the right unit but remain invalid.

Centralize domain predicates:

```ts
const Domain = {
  finiteLength(x: Mm): boolean,
  positiveLength(x: Mm): boolean,
  nonnegativeAllowance(x: Mm): boolean,
  positiveFeed(x: MmPerMin): boolean,
  validRpm(x: Rpm, profile: MachineProfile): boolean,
  validTolerance(x: Mm): boolean,
};
```

Do not rely on each strategy to rediscover these rules.

## Frame graph consistency

A frame graph contains edges $T_{B\leftarrow A}$. Elaboration should reject:

- cycles whose composed transform is inconsistent beyond tolerance;
- multiple conflicting paths between frames;
- references to unknown frames;
- transforms with non-finite values;
- non-rigid matrices when rigid transforms are required;
- ambiguous work-coordinate selection.

When uncertainty is present, consistency becomes an enclosure question: do the alternative transform paths overlap within their declared bounds?

## Defaults and provenance

Every default should become explicit in Plan IR and retain provenance indicating that it came from configuration rather than source text.

```ts
{
  feed: mmPerMin(400),
  provenance: {
    kind: "default",
    source: "material-library/aluminum-6061.json",
    rule: "slotting-feed:T1",
  }
}
```

This makes re-compilation under a changed material library correctly invalidate downstream artifacts.

## Normal forms

Elaboration can establish a normal form:

- one canonical unit system;
- one orientation convention for polygon rings;
- explicit closed/open path flags;
- sorted map keys;
- explicit optional fields;
- unique identifiers;
- canonical frame names.

Normalization reduces the number of cases later passes and checkers must handle.

## Static versus physical checks

Elaboration can prove that a tool reference exists. It cannot prove that the operator loaded that tool. It can prove that a work frame is defined in the project. It cannot prove that the live machine's G54 matches the definition.

The IR should therefore distinguish **compile-time facts** from **runtime assumptions**.

## Worked example: resolving a pocket

Authoring node:

```ts
pocket({
  at: [10, 10],
  size: [30, 20],
  depth: 4,
  tool: "T1",
});
```

Elaborated node:

```ts
{
  kind: "rectPocket",
  id: "op:4f7c...",
  frame: "work:G54",
  origin: point(mm(10), mm(10), mm(0), "work:G54"),
  width: mm(30),
  height: mm(20),
  depth: mm(4),
  tool: { id: "T1", artifactHash: "sha256:..." },
  tolerance: mm(0.02),
  radialAllowance: mm(0),
  axialAllowance: mm(0),
  source: { file: "job.cam.js", line: 12, column: 1 },
}
```

Every omitted fact has become explicit or produced a diagnostic.

## Exercises

1. Write static rules for a tool definition and a pocket operation.
2. Give three domain errors that unit types do not catch.
3. Design a frame-graph consistency diagnostic.
4. Explain why defaults need provenance.
5. Propose a normal form for polygon rings with holes.
6. Separate compile-time facts from runtime assumptions in a probing setup.

# Planning Features into Toolpaths

> **Learning objectives.** The reader should be able to model planning as constrained synthesis, preserve feature provenance, and design checkable witnesses for coverage and target protection.

## Planner input and output

A planner receives intent, geometry, tools, stock state, process constraints, and an error budget. It returns candidate paths plus evidence.

```ts
interface PlanningInput<I> {
  intent: I;
  stock: StockStateRef;
  target: GeometryRef;
  fixtures: readonly GeometryRef[];
  tool: ToolAssemblyRef;
  context: PlanningContext;
}
```

The output should separate **cut paths** from **entry and linking**. A feature strategy can focus on material-removal geometry; a scheduler later connects paths under state-dependent clearance constraints.

## Coverage and offset planning

For a two-dimensional pocket and a cylindrical cutter, centerline regions are often built by morphological offsets. If the pocket region is $R$ and cutter radius is $r$, a safe center region is approximately:

$$
R_c=R\ominus B_r.
$$

Roughing passes may cover $R_c$ with raster lines, inward offsets, or adaptive loops. A witness can include the arrangement of covered cells and a bound on uncovered required-removal regions.

Offset geometry must handle topology changes, narrow channels, corners, and holes. Exact predicates or robust integer/rational topology are preferable for decisions such as orientation and intersection.

## Drop-cutter planning

For three-axis finishing, a drop-cutter method places the tool at sampled XY positions and finds the lowest collision-free Z against the target. The resulting cutter-location field is an approximation to a configuration-space surface.

A credible planner must state:

- tool geometry used in contact computation;
- target representation and its enclosure error;
- XY sampling strategy;
- interpolation between samples;
- residual or refinement criterion;
- behavior near boundaries and vertical walls;
- whether the field is an inner or outer safety bound.

A height sample alone does not prove continuous no-gouge between samples.

## Constant-scallop intent

A true constant-scallop strategy controls maximum residual cusp height on the target surface. Merely tracing isolines of a distance-like field does not establish a physical scallop bound. The proof must connect:

1. target surface metric;
2. tool contact geometry;
3. field discretization error;
4. extracted contour error;
5. spacing between adjacent passes;
6. final swept material.

Names should not overstate guarantees. An experimental field-contour strategy can be useful while reporting `simulation-only` or `unresolved` scallop evidence.

## Directionality and phase

Paths should carry phase and direction constraints:

```ts
interface PlannedPath {
  path: Path;
  operation: OperationRef;
  phase: "rough" | "semiFinish" | "finish";
  reversible: boolean;
  preferredDirection?: "climb" | "conventional";
  requiredPredecessors: readonly PathId[];
}
```

The scheduler should not infer reversibility from geometry alone.

## Witness design

A raster pocket witness might include:

```ts
interface RasterPocketWitness {
  centerRegion: RegionRef;
  scanDirection: UnitVec2;
  stepover: Mm;
  strips: readonly StripCoverage[];
  unresolvedCells: readonly CellRef[];
  outerBoundaryError: Mm;
  guaranteedRemovalError: Mm;
}
```

The checker verifies coverage, boundary protection, and bound composition. If unresolved cells remain, the claim becomes inconclusive or the planner refines them.

## Worked example: pocket coverage

Suppose a $20$ mm wide center region is cut with a $3$ mm tool and $1.2$ mm stepover. A naive pass count of $\lceil20/1.2\rceil$ does not prove edge coverage because the first pass position and tool radius matter. A checker reconstructs the union of guaranteed inner swept strips and compares it with the required-removal region.

For a flat end mill whose radius has uncertainty $r\in[r^-,r^+]$, guaranteed removal uses $r^-$; protected-boundary checking uses $r^+$.

## Exercises

1. Define a witness for offset-loop pocketing.
2. Explain why target height samples do not prove continuous no-gouge.
3. State the inputs required for a physical scallop-height claim.
4. Give a path property that should prevent reversal.
5. Design a refinement condition for adaptive drop-cutter sampling.
6. Explain why tool-radius uncertainty has opposite directions for removal and gouge checks.

# Scheduling, Entry, and Linking

> **Learning objectives.** The reader should be able to distinguish planning from scheduling, model evolving stock, derive safe links in configuration space, and preserve precedence and process constraints.

## Planning produces islands; scheduling produces a program

Feature planners often produce several disconnected cut paths. The scheduler decides:

- order;
- orientation;
- tool grouping;
- entries and exits;
- traverses and retracts;
- probe and setup dependencies;
- feeds and time law;
- optional path merging.

These decisions are stateful because each cut changes stock.

## Evolving stock state

Let $S_i$ be stock before operation $i$ and $R_i$ its removed region:

$$
S_{i+1}=S_i\setminus R_i.
$$

A link is checked against the stock state that exists when the link executes. Checking every link against initial stock is conservative but may force excessive retracts. Checking every link against final stock is unsound because material may still be present.

Scheduled IR should reference the stock version:

```ts
interface ScheduledMotion {
  beforeStock: StockStateRef;
  command: Traverse | Cut | Probe;
  afterStock: StockStateRef;
}
```

## Entry strategies

Common entries include:

- vertical plunge;
- linear ramp;
- helical ramp;
- predrilled entry;
- edge approach;
- rest-material entry.

Each entry has preconditions. A plunge may require a center-cutting tool and a region free of target or fixture material. A helix requires sufficient radial clearance. An edge approach requires an accessible exterior.

Entry selection is a constrained planning problem, not a cosmetic interpolation.

## Traverse semantics

A traverse means “move through free space,” not “emit `G0`.” A machine lowering may choose:

```text
retract in Z
move in XY
descend in Z
```

because some controllers implement multi-axis rapid as independent axis motion rather than a guaranteed straight segment. The expansion itself must be checked against machine and fixture geometry.

## Configuration space

For fixed tool orientation, expand obstacles by the reflected tool assembly:

$$
O_C=O\oplus(-T_{assembly}).
$$

The tool reference point can then be treated as a point that must avoid $O_C$ [R25]. Stock, fixtures, and machine no-go volumes contribute to the configuration obstacle.

A safe path $\gamma$ satisfies:

$$
\forall s\in[0,1],\quad \gamma(s)\notin O_C.
$$

## Precedence constraints

Dependencies include:

- rough before finish;
- probe before dependent geometry;
- drill pilot before large drill;
- cut internal features before releasing surrounding material;
- maintain support for thin walls;
- tool-change grouping subject to process order.

Represent them as a directed acyclic graph when possible. A scheduler produces a topological order and a witness mapping each edge to positions in the schedule.

## Worked example: two islands

Two finish paths lie in separate pocket islands. Reversing the second path shortens the free-space link, but the path is climb-only. The scheduler must choose among:

- retain direction and accept a longer link;
- add a safe traverse to the required start;
- select a different strategy that produces a legal orientation;
- reject the optimization.

A shortest endpoint distance is not the objective until direction and clearance constraints are included.

## Exercises

1. Explain why final-stock collision checking is unsound for early links.
2. Specify preconditions for a helical entry.
3. Derive a configuration obstacle for a circular tool in 2D.
4. Design a precedence witness for a scheduled operation list.
5. Give an example where a shorter link violates process semantics.
6. Compare a conservative retract policy with free-space path planning.

# Machine Lowering and Capability Resolution

> **Learning objectives.** The reader should be able to describe machine capabilities algebraically, lower abstract actions safely, and reject unsupported semantics instead of guessing.

## Machine profiles as semantic contracts

A machine profile should contain more than travel dimensions. It defines the target language and assumptions for lowering.

```ts
interface MachineProfile {
  id: string;
  version: string;
  axes: readonly AxisProfile[];
  kinematics: KinematicModel;
  interpolation: InterpolationCapabilities;
  spindle: SpindleCapabilities;
  probes: ProbeCapabilities;
  toolChange: ToolChangeCapabilities;
  controller: ControllerSemanticsRef;
  travelEnvelope: ConfigurationSetRef;
  dynamicLimits: DynamicLimits;
}
```

Capabilities should be structured data, not scattered booleans.

## Algebraic capabilities

```ts
type ArcCapability =
  | { kind: "native"; planes: readonly Plane[]; helical: boolean }
  | { kind: "linearize"; maxChordError: Mm }
  | { kind: "unsupported" };
```

A lowering pass pattern-matches exhaustively. If a helical arc is requested and the controller supports planar arcs only, it may linearize within budget or reject. It must not silently emit an invalid arc.

## Coordinate resolution

Machine lowering resolves work-frame paths to machine coordinates under a selected transform. It must also model whether the controller itself applies a work offset. There are two valid approaches:

1. Emit work coordinates and explicit WCS selection, then validate under the controller's offset semantics.
2. Pretransform all coordinates to machine coordinates and use machine-coordinate motion intentionally.

Mixing the two produces double offsets or unchecked travel.

## Dynamic and geometric limits

Travel limits constrain configuration:

$$
q(t)\in Q_{admissible}.
$$

Dynamic limits constrain derivatives:

$$
|\dot q_i|\le v_i^{max},\quad
|\ddot q_i|\le a_i^{max},\quad
|\dddot q_i|\le j_i^{max}.
$$

A geometric feed value does not by itself guarantee these limits; controller trajectory generation and path curvature matter. Machine IR may preserve a feed policy for later time parameterization or lower it to a verified schedule.

## Safe expansion of abstract operations

An abstract `Traverse(A,B)` can lower to a sequence using a certified clearance plane. The pass relation is not textual equivalence. It is:

- same start and end;
- all intermediate motion belongs to certified free space;
- process state is preserved;
- added motion remains within machine limits;
- timing and side effects are acceptable.

Similarly, a tool change may expand into spindle stop, retract, move to change position, prompt, and tool-state update.

## Unsupported and unknown behavior

A target profile should distinguish:

- unsupported by hardware;
- supported but not modeled;
- modeled but not verified;
- verified under constraints.

“Unknown” must not be treated as “probably supported.”

## Worked example: rapid lowering

Suppose canonical IR contains a diagonal traverse from $(0,0,10)$ to $(100,100,10)$. If the controller guarantees coordinated linear rapid, one `G0` may implement it. If rapid axes move independently and fixtures occupy a diagonal corridor, the actual dogleg may intersect them. A safe lowering either uses a known-clear route or emits coordinated feed motion under a verified speed policy.

## Exercises

1. Design algebraic capabilities for probing.
2. Explain two consistent ways to handle work offsets.
3. State the pass relation for traverse expansion.
4. Give an example where a geometrically valid feed violates axis velocity limits.
5. Distinguish unsupported, unmodeled, and unverifiable.
6. Design a machine-profile hash and compatibility rule.

# Controller IR and Modal Semantics

> **Learning objectives.** The reader should be able to model modal state explicitly, interpret G-code blocks, and validate modal compression as a semantics-preserving optimization.

## Modal syntax is compressed state

In RS274-like languages, words persist until replaced. A block omitting `G1`, `F`, or `S` may inherit them. Modal groups constrain which codes can be active simultaneously. Correct meaning depends on the initial state and controller dialect [R2].

Canonical IR should remain non-modal. Controller IR can introduce modal state in a controlled stage.

## Controller state

A simplified state includes:

```ts
interface ModalState {
  units: "mm" | "inch" | "unknown";
  distanceMode: "absolute" | "incremental" | "unknown";
  motionMode: "rapid" | "linear" | "cwArc" | "ccwArc" | "none" | "unknown";
  plane: "XY" | "XZ" | "YZ" | "unknown";
  feedMode: FeedMode;
  feed?: number;
  spindle?: SpindleState;
  wcs?: WorkCoordinateSystem;
  toolLengthComp?: ToolCompState;
  position: AbstractPosition;
}
```

An interpreter maps each block and state to a successor state plus canonical events.

## Blocks are evaluated as units

A G-code block is not necessarily a left-to-right sequence of words. Controller specifications define modal-group updates and execution order. A parser should produce a structured block; an interpreter applies dialect rules.

Raw string prefix classification is not semantic parsing. A line can contain several words, comments, checksums, or controller commands. Multiline payloads require complete grammar validation.

## Initial state

A job should not depend on ambient modal state unless the dependency is an explicit runtime assumption. A preamble usually establishes:

- units;
- absolute/incremental mode;
- plane;
- feed mode;
- work offset;
- cutter and tool-length compensation policy;
- spindle and coolant baseline.

The final validator interprets the complete program from the declared initial state.

## Modal compression

A simple serializer may emit every modal word in every block. A compression pass removes words whose values are already active. Its correctness statement is:

$$
\operatorname{Interpret}(B_{compressed},m_0)
=
\operatorname{Interpret}(B_{explicit},m_0).
$$

A translation validator can interpret both and compare canonical traces and final modal states.

Unknown raw text destroys this proof unless parsed. The safe response is to reset all affected modal components to unknown and require re-establishment before dependent commands, or to reject compression around the block.

## Probes and result semantics

A probe block commands a search path; its actual contact point is a runtime result. Controller IR should distinguish commanded endpoint, maximum travel, success condition, and measurement register. Emitting the expected contact as though it were a deterministic absolute endpoint is incorrect.

## Worked example: stale incremental mode

Consider:

```text
G91
G1 X10 F300
...
X20
```

If the later block is intended as absolute X=20 but `G90` was never restored, it moves an additional 20 mm. A canonical non-modal program would represent the intended target explicitly. The controller interpreter exposes the mismatch during validation.

## Exercises

1. Define modal groups for motion and distance mode.
2. Interpret a short program under two different initial states.
3. State a validator for modal compression.
4. Explain how raw text should affect abstract modal state.
5. Model a probe block's command and result separately.
6. Design a complete, explicit preamble for a three-axis metric job.

# Serialization, Round Trips, and Exact Bytes

> **Learning objectives.** The reader should be able to define deterministic serialization, validate parse-back equivalence, account for rounding, and bind certificates to exact deployed bytes.

## Serialization is a compiler pass

Formatting appears trivial until safety depends on it. The serializer chooses:

- decimal precision;
- suppression of trailing zeros;
- negative-zero handling;
- line endings;
- comments and metadata escaping;
- line numbers and checksums;
- program-end syntax;
- filename and upload encoding.

Each choice can change controller behavior or artifact identity.

## Deterministic formatting

For a given Controller IR and configuration, serialization should produce exactly one byte sequence. Locale-dependent decimal commas, unstable comment order, timestamps, or platform line endings damage reproducibility.

```ts
interface SerializationConfig {
  decimals: number;
  trimTrailingZeros: boolean;
  lineEnding: "\n";
  emitComments: boolean;
  commentEscape: CommentEscapePolicy;
}
```

## Rounding bounds

Rounding each coordinate to $d$ decimal places introduces at most:

$$
\rho=\frac{1}{2}10^{-d}
$$

per scalar in the selected unit. In three dimensions, an independent-coordinate Euclidean bound is:

$$
\rho_3\le\sqrt{3}\rho.
$$

The actual path error also depends on interpolation and repeated endpoints. Arc center and radius formatting can amplify error or make an arc invalid.

## Parse-back validation

After serialization, parse the exact bytes with an independent parser, interpret them under the target dialect, and compare with Controller IR:

$$
\operatorname{Interpret}(\operatorname{Parse}(bytes),m_0)
\approx_{\varepsilon}
\operatorname{Sem}(ControllerIR).
$$

This catches:

- omitted modal resets;
- wrong probe syntax;
- escaped comment failures;
- numeric overflow or scientific notation unsupported by the controller;
- program-end omissions;
- postprocessor bugs.

## Injection through comments and metadata

User-controlled strings inserted into comments or header records must be escaped according to the dialect. Newlines or delimiters can terminate a comment and introduce executable words. The safest design uses structured metadata outside executable text; when comments are required, the serializer enforces a conservative character set.

## Exact-byte binding

A certificate produced before serialization does not automatically apply afterward. The final validation artifact should include:

```ts
interface ByteArtifact {
  bytes: Uint8Array;
  sha256: Hash;
  dialect: DialectId;
  initialModalState: ModalStateRef;
  parseBackClaim: ClaimId;
}
```

Upload and execution must refer to this hash, not merely a filename.

## Safety epilogue

A validator may require a final spindle stop, coolant stop, retract, or program end. The property must be checked on final interpreted bytes. A comment or validation diagnostic saying “M5 appended” is not evidence if the emitter did not actually append it.

## Worked example: round-trip checker

1. Serialize explicit Controller IR.
2. Hash the bytes.
3. Parse with an independent grammar.
4. Interpret from the declared modal state.
5. Compare event traces, endpoints, process state, and final modal state.
6. Attach numeric bounds for rounded motion.
7. Verify the required epilogue.
8. Store the byte hash in every dependent claim.

## Exercises

1. Derive the coordinate rounding bound for four decimal places in millimeters.
2. Design a comment-escaping policy.
3. Explain why parse equality is weaker than semantic equality.
4. Specify a final-byte certificate claim.
5. Give two ways an arc can become invalid after formatting.
6. Explain why the program filename cannot replace the content hash.

# Optimization Without Breaking Meaning

> **Learning objectives.** The reader should be able to state optimization legality, distinguish hard constraints from objectives, and validate local transformations and whole-program changes.

## Optimization is constrained refinement

A CAM optimizer searches for a lower-cost implementation while preserving required behavior:

$$
\min_O J(O)
$$

subject to:

$$
R(I,O)\land\operatorname{Feasible}(O).
$$

Safety constraints are not soft penalties. A path that is one second faster but intersects a fixture is not a worse solution; it is outside the feasible set.

## Common optimizations

- remove zero-length and redundant motions;
- merge collinear segments;
- fit arcs or splines;
- compress modal words;
- reorder independent operations;
- choose path orientation;
- reduce retract height under certified clearance;
- group tool changes;
- schedule feed and spindle changes;
- select among strategy alternatives.

Each has a different pass relation.

## Peephole validation

Local transformations can carry local proofs. Merging two collinear line segments is legal when:

- the intermediate point lies on the same line;
- feed and process state are compatible;
- no event at the intermediate point is semantically observable;
- controller interpolation of the merged move remains within limits;
- provenance is preserved.

A dwell, exact-stop marker, probe, or stock-dependent state change prevents the merge.

## Reordering and commutativity

Two operations commute only when their effects are independent and their preconditions remain valid in either order. A sufficient condition resembles:

$$
W_1\cap(R_2\cup W_2)=\varnothing,
$$

with additional constraints for stock support, probing, tool state, and fixtures. Effect summaries provide a conservative test.

Geometric set subtraction is commutative, but the physical process is not necessarily so.

## Objective evidence

A heuristic may report a candidate cost. A certificate should distinguish:

- feasibility proved;
- objective computed exactly or bounded;
- local improvement relative to a baseline;
- global optimality proved;
- optimality gap bounded by a lower bound.

Without a valid lower bound, call the result optimized or heuristic, not optimal.

## Phase ordering

Passes interact. Arc fitting before machine lowering may create unsupported arcs. Rounding before collision checking may hide final-byte error. Reordering before entry generation may choose endpoints that later become infeasible.

A typical safe order is:

1. semantic planning;
2. scheduling and linking;
3. machine capability lowering;
4. bounded geometric optimization;
5. controller lowering;
6. modal optimization;
7. serialization;
8. final parse-back and geometric validation.

Final validation is necessary even when each pass has a local proof because bugs and omitted assumptions can occur at composition boundaries.

## Worked example: arc fitting

A polyline fitting pass proposes an arc over points $p_i$. Its witness includes maximum deviation, endpoint tangents, sweep, and source range. The checker verifies:

- all covered points lie within the declared metric bound;
- the arc is supported by the target or can be lowered;
- no semantic event lies inside the replaced range;
- the outer swept-volume envelope remains safe;
- the optimization does not exceed remaining error budget.

## Exercises

1. State legality conditions for removing a zero-length move.
2. Give an example where two material-removal operations do not commute.
3. Explain why safety cannot be a weighted objective term.
4. Design a witness for collinear segment merging.
5. Define an optimality gap.
6. Propose a pass order and justify two ordering constraints.

\part{Part IV - Assertions, Invariants, and Certificates}

# Contracts, Hoare Logic, and Weakest Preconditions

> **Learning objectives.** The reader should be able to distinguish assertions, invariants, assumptions, and guarantees; derive weakest preconditions; and use contracts to structure compiler and controller checks.

## Vocabulary matters

Safety discussions become confused when different logical objects share the word “check.” The following distinctions should appear in code and certificate schemas.

An **assertion** is a proposition about one program point or artifact.

A **precondition** must hold before an operation.

A **postcondition** is guaranteed after successful execution, subject to assumptions.

An **invariant** holds initially and is preserved by all relevant transitions.

An **assumption** is an external fact not established by the current checker.

A **guarantee** is a proposition established when the assumptions hold.

A **witness** is data chosen by a producer to help establish a proposition.

A **proof or evidence object** is checked by a specified procedure.

An **attestation** establishes origin or integrity; it does not establish semantic truth.

## Hoare triples

A Hoare triple has the form [R4]:

$$
\{P\}\ c\ \{Q\}.
$$

It means that if command $c$ starts in a state satisfying $P$ and terminates normally, the resulting state satisfies $Q$. Total-correctness variants also establish termination.

A traverse contract might be:

$$
\{
\operatorname{Pose}=a\land
\operatorname{Homed}\land
\operatorname{Free}(\gamma,T,O,S)
\}
$$

$$
\operatorname{Traverse}(\gamma)
$$

$$
\{
\operatorname{Pose}=b\land
S'=S\land
\operatorname{ProcessState}'=\operatorname{ProcessState}
\}.
$$

The stock-equality postcondition distinguishes traverse from cut.

## Sequential composition

If:

$$
\{P\}\ c_1\ \{R\}
$$

and:

$$
\{R\}\ c_2\ \{Q\},
$$

then:

$$
\{P\}\ c_1;c_2\ \{Q\}.
$$

The intermediate assertion $R$ is the interface between commands. Compiler IR design should expose enough state to state $R$.

## Weakest preconditions

The weakest precondition $wp(c,Q)$ is the least restrictive condition that guarantees $Q$ after $c$.

For sequential commands:

$$
wp(c_1;c_2,Q)=wp(c_1,wp(c_2,Q)).
$$

For an assignment $x:=e$:

$$
wp(x:=e,Q)=Q[e/x].
$$

For a conditional:

$$
wp(\mathrm{if}\ b\ \mathrm{then}\ c_1\ \mathrm{else}\ c_2,Q)
=(b\Rightarrow wp(c_1,Q))\land(\neg b\Rightarrow wp(c_2,Q)).
$$

A preflight engine can derive requirements backward from the program rather than maintaining an unrelated checklist.

## CNC weakest-precondition example

Suppose the desired final condition is:

$$
Q=\operatorname{SpindleOff}\land\operatorname{Pose}=p_{safe}.
$$

The program is:

```text
cut path P
retract to p_safe
stop spindle
```

Working backward:

1. `stop spindle` requires a valid controller session and guarantees `SpindleOff`.
2. `retract` requires a collision-free path from `end(P)` to $p_{safe}$.
3. `cut` requires homing, known WCS, selected tool, valid spindle state, safe cutting sweep, and feasible feed.

The derived precondition becomes the basis of compile-time claims and runtime preflight.

## Invariant induction

To prove invariant $I$ over a transition system:

1. **Initialization:** $I(\sigma_0)$.
2. **Preservation:** $I(\sigma)\land T(\sigma,\sigma')\Rightarrow I(\sigma')$.

Examples:

- stock monotonically decreases under cut and remains unchanged under traverse;
- every motion command has a known frame;
- cutting implies a selected tool and active spindle;
- an executing job has one content hash;
- an alarm state cannot transition directly to running without explicit recovery.

## Separation of resources

Separation logic reasons about disjoint mutable resources [R38]. Its central intuition is useful even without a full separation-logic implementation. An operation that removes stock in region $A$ should not affect a disjoint fixture region $B$. Effect summaries can state footprints, enabling local reasoning and safe parallel analysis.

## Design by contract in APIs

Contracts should be executable where possible:

```ts
function cut<S extends ReadyToCut>(
  state: S,
  motion: CuttingMotion,
): Result<CutResult, Diagnostic[]> {
  requireFinitePath(motion.path);
  requirePositiveFeed(motion.feed);
  requireToolMatch(state.tool, motion.tool);
  // geometric and runtime obligations remain explicit claims
}
```

Do not pretend that a runtime assertion about metadata proves physical collision freedom. Contracts should state the boundary of what they establish.

## Exercises

1. Write a Hoare triple for spindle start.
2. Derive $wp$ for `select tool; start spindle; cut` with final condition `stock conforms to roughing intent`.
3. State and prove a stock-monotonicity invariant for a simplified semantics.
4. Distinguish an assumption from a precondition in a live tool check.
5. Give an example of a local resource footprint for two independent operations.
6. Explain partial versus total correctness for an abort command.

# Abstract Interpretation for Machine Programs

> **Learning objectives.** The reader should be able to define concrete and abstract domains, implement sound transfer functions, compute invariants over control flow, and use unknown states conservatively.

## Simulating one trace is not analyzing all traces

A simulator executes one concrete state through one control path. A validator often needs to cover many possible states: unknown initial modal settings, uncertain positions, branches after probing, controller faults, or values from macros. Abstract interpretation computes over-approximations of these possibilities [R7].

Let $C$ be a concrete domain and $A$ an abstract domain. A concretization function:

$$
\gamma:A\to\mathcal{P}(C)
$$

maps an abstract value to the concrete states it represents.

A sound abstract transfer function $\widehat{F}$ satisfies:

$$
F(\gamma(a))\subseteq\gamma(\widehat{F}(a)).
$$

## Abstract machine state

```ts
interface AbstractMachineState {
  position: Box3 | "unknown";
  homing: "homed" | "unhomed" | "maybe";
  tool: ToolRef | Set<ToolRef> | "unknown";
  spindle: "off" | RpmInterval | "unknown";
  wcs: TransformInterval | "unknown";
  motionMode: Set<MotionMode>;
  feed: Interval<number> | "unknown";
  playing: "yes" | "no" | "maybe";
  alarm: "yes" | "no" | "maybe";
}
```

The domain should be just expressive enough for the claims it checks.

## Interval transfer

For a linear absolute move to $X=x$, the abstract X interval becomes $[x,x]$ after accounting for rounding and transform uncertainty. In incremental mode, it becomes:

$$
X' = X + [x-\rho,x+\rho].
$$

If distance mode is `{absolute, incremental}`, the successor joins both possibilities. Precision drops, but soundness remains.

## Modal-state analysis

An abstract G-code interpreter can prove:

- units definitely metric;
- distance mode definitely absolute;
- spindle definitely on before each cut;
- position remains inside travel bounds;
- no motion occurs with unknown WCS;
- raw commands do not leave required modal components unknown;
- final spindle state is definitely off.

Each block records an invariant before and after:

```ts
interface BlockInvariant {
  blockIndex: number;
  before: AbstractMachineState;
  after: AbstractMachineState;
}
```

A small proof checker replays abstract transfers and verifies safety predicates.

## Joins and loss of precision

If one branch selects tool T1 and another selects T2, the merge state contains `{T1,T2}`. A later operation requiring exactly T1 cannot be proved safe without a guard.

Widening may be necessary for loops. For example, repeated incremental motion can make position unbounded unless the loop count is bounded. A production-certifiable dialect may reject unbounded macros rather than analyze them imprecisely.

## Reduced products

Different abstract domains can cooperate. A position box and a linear relation domain may jointly prove tighter bounds. A modal-state domain and typestate domain can reduce each other: if an alarm is definite, playing is false; if spindle is off, RPM interval is zero.

Such combinations increase checker complexity. Begin with simple domains tied to explicit claims.

## Unknown raw effects

A raw block that is not parsed should conservatively set affected state to unknown. Self-declared effects can be recorded as assumptions, but they do not justify a proved claim.

```ts
function transferRaw(state: AbstractState, raw: RawBlock): AbstractState {
  return {
    ...state,
    position: "unknown",
    motionMode: allMotionModes,
    feed: "unknown",
    spindle: "unknown",
    wcs: "unknown",
  };
}
```

A later explicit preamble can re-establish some components.

## Worked example: final spindle state

A program branches around an optional finishing pass. Both branches eventually execute `M5`. At the merge, spindle is definitely off. If one branch omits `M5`, the merge state is `{off,on}` and the final safety epilogue claim fails.

## Exercises

1. Define a concretization function for an interval.
2. Write abstract transfer rules for G90, G91, G20, and G21.
3. Explain why joining branches loses precision.
4. Design a sound state update for an unknown raw command.
5. Show how a loop of incremental X moves can require widening.
6. Propose a reduced product relevant to probing and frames.

# Robust Numerics and Computational Geometry

> **Learning objectives.** The reader should be able to distinguish topological predicates from metric constructions, use exact or adaptive predicates, apply interval enclosures, and identify failure modes of floating-point geometry.

## Why geometric bugs are discontinuous

A small floating-point error in a distance often causes a small distance error. A small error in a sign predicate can change topology completely: two contours connect instead of remaining separate, a polygon changes orientation, or an intersection is missed.

Computational geometry therefore distinguishes:

- **predicates**, which decide discrete facts such as orientation or intersection;
- **constructions**, which compute coordinates.

Predicates deserve stronger numerical methods.

## Orientation predicates

For points $a,b,c$ in 2D, orientation is the sign of:

$$
\operatorname{orient2d}(a,b,c)=
(b_x-a_x)(c_y-a_y)-(b_y-a_y)(c_x-a_x).
$$

Near collinearity, floating-point cancellation can return the wrong sign. Adaptive exact predicates evaluate cheaply in ordinary cases and increase precision only near degeneracy [R22].

Use robust predicates for:

- polygon orientation;
- segment intersection;
- point-in-polygon decisions;
- Delaunay or Voronoi topology;
- contour stitching;
- mesh adjacency and ray intersections.

## Exact topology, approximate geometry

A practical architecture can keep topology exact while allowing bounded approximate coordinates. For grid-generated contours, use grid-edge identifiers rather than re-quantized endpoint coordinates. For polygon kernels, use integer-scaled coordinates within a proven range or exact rational predicates.

The endpoint-key failure discussed later is a violation of this principle: a lossy packed coordinate is used as topological identity.

## Interval arithmetic

An interval $[a,b]$ represents every real number between its endpoints. Arithmetic operations use outward rounding so the exact result is enclosed. IEEE 1788.1 specifies interval arithmetic over binary floating-point endpoints [R23]; Moore, Kearfott, and Cloud provide a broad treatment of interval analysis [R24].

If:

$$
x\in[a,b],\quad y\in[c,d],
$$

then:

$$
x+y\in[a+c,b+d]
$$

with outward-rounded endpoints. Multiplication takes the min and max of all endpoint products.

Intervals can bound:

- curve coordinates over a parameter range;
- transform uncertainty;
- distance to a surface;
- polynomial extrema;
- swept-volume occupancy;
- numerical residuals.

## The dependency problem

Interval arithmetic can overestimate when the same variable appears repeatedly. For $x\in[0,1]$:

$$
x-x=[-1,1]
$$

under naive interval evaluation, although the true result is zero. Subdivision, affine arithmetic, Taylor models, or symbolic simplification can improve tightness.

An inconclusive wide interval is not a false result. The checker can subdivide or reject.

## Conservative meshing

A triangle mesh is often treated as exact geometry, but it approximates a design surface. A certificate should record:

- source artifact hash;
- tessellation tolerance;
- orientation and watertightness status;
- whether the mesh encloses or is enclosed by the intended solid;
- repairs performed;
- unresolved non-manifold or self-intersection issues.

Without an enclosure relation, mesh-based collision checks prove facts about the mesh, not necessarily the intended CAD solid.

## Tolerance and topology

Using one epsilon everywhere is dangerous. Distinct tolerances are needed for:

- numeric comparison;
- geometric construction;
- topological snapping;
- machining allowance;
- certification bound.

A topological snap modifies geometry. Its displacement must be recorded and charged to an error budget.

## Worked example: collision of two nearly touching paths

Suppose a line passes $2\,\mu$m from a fixture in nominal double precision, while tool-radius uncertainty is $5\,\mu$m and frame uncertainty is $10\,\mu$m. An exact floating-point distance does not make the move safe. The relevant outer enclosure intersects the obstacle. Numerical exactness and physical robustness are different dimensions.

## Exercises

1. Compute `orient2d` for three nearly collinear points and explain cancellation risk.
2. Distinguish a predicate from a construction.
3. Give a use of interval subdivision in curve bounding.
4. Explain the interval dependency problem.
5. Design metadata for a mesh enclosure claim.
6. List four different tolerances in a CAM compiler and their roles.
7. Explain why exact arithmetic does not eliminate model uncertainty.

# Swept Volumes, Stock Models, and Collision Proofs

> **Learning objectives.** The reader should be able to define swept volume, choose conservative stock representations, distinguish cutting from holder collision, and formulate no-gouge and guaranteed-removal claims.

## Swept volume

For a tool solid $T$ and pose trajectory $x(t)$, the swept volume is:

$$
\operatorname{Sweep}(T,x)=\bigcup_{t\in[0,T]}x(t)T.
$$

Swept-volume computation is central to collision detection, stock simulation, and manufacturing verification [R26]. Exact computation is difficult for general geometry and trajectories, so practical systems use conservative enclosures or discrete representations.

## Stock evolution

For cutting command $i$ with removed volume $R_i$:

$$
S_{i+1}=S_i\setminus R_i.
$$

A simulator may approximate $R_i$ using the swept cutting geometry. The semantic distinction among commands remains important:

- cut updates stock;
- traverse must not update stock;
- probe ideally stops at first contact and may touch without intended removal;
- tool change and dwell preserve stock.

If a missing traverse is silently converted to a cut, the stock semantics change, not merely the visualization.

## Tool versus holder

Let $T_c$ be cutting geometry and $T_a$ the full assembly. Then:

**No target gouge:**

$$
\operatorname{Sweep}(T_c,x)^+\cap P_{protected}=\varnothing.
$$

**No fixture collision:**

$$
\operatorname{Sweep}(T_a,x)^+\cap O^+=\varnothing.
$$

**Guaranteed removal:**

$$
R_{required}\subseteq \operatorname{Sweep}(T_c,x)^-.
$$

The superscripts indicate outer and inner enclosures.

## Dexel and voxel models

A dexel model stores material intervals along parallel rays. A height field stores one surface value per XY cell and cannot represent undercuts or multiple layers. Triple-dexel models use three orthogonal directions and improve surface representation [R27, R28]. Voxels represent occupancy in three dimensions.

Tradeoffs include:

- memory;
- update speed;
- ability to represent overhangs and cavities;
- surface error;
- ease of conservative enclosure;
- suitability for cutter contact.

For a three-axis no-overhang part, a height field can be efficient, but its resolution must be connected to a continuous-domain bound.

## A grid size is not a guarantee

Sampling motion at spacing $h$ and stock on a grid of cell size $g$ does not by itself prove “verified to $\max(h,g)$.” A narrow fixture or brief penetration can occur between samples.

A sound cell method needs one of:

- conservative occupancy of every cell touched by the continuous sweep;
- interval bounds over each cell and motion interval;
- a Lipschitz bound plus adaptive subdivision;
- exact primitive sweep tests;
- a certified distance-field enclosure.

Otherwise, label the result simulation-only.

## Configuration-space collision

For fixed orientation, configuration-space obstacles reduce moving-solid collision to point-path collision [R25]:

$$
O_C=O\oplus(-T_a).
$$

A clearance checker can build an outer enclosure $O_C^+$ and prove that the tool-reference path is separated by a positive bound.

For rotating tools or multi-axis orientation, configuration space has more dimensions and the expansion varies with orientation.

## Continuous path checking

Lines and arcs often admit analytic bounds. Splines and sampled paths can be recursively subdivided. A generic branch-and-bound checker operates on parameter intervals:

1. Bound path positions over interval $I$.
2. Expand by tool assembly and uncertainty.
3. If disjoint from obstacle enclosure, accept $I$.
4. If definitely intersecting, return a counterexample interval.
5. Otherwise subdivide until a limit.
6. If the limit is reached unresolved, return inconclusive.

This produces honest coverage of the continuous parameter domain.

## Worked example: rapid through stock

A rapid from A to B at low Z is safe only if the entire outer swept assembly is disjoint from current stock and fixtures. Checking endpoints misses an obstacle between them. Checking sampled points can miss a thin wall. A segment-versus-expanded-obstacle test or conservative recursive enclosure addresses the whole move.

## Exercises

1. Write set formulas for no-gouge, fixture collision, and guaranteed removal.
2. Compare height fields, dexels, triple dexels, and voxels.
3. Explain why one grid resolution cannot be attached blindly to all claims.
4. Design a recursive continuous collision checker.
5. Give a case where cutting geometry is clear but holder geometry collides.
6. Explain how stock state affects link verification.

# Error Budgets and Quantitative Refinement

> **Learning objectives.** The reader should be able to construct typed error budgets, compose bounds through passes, allocate tolerances, and distinguish numerical, model, calibration, and process uncertainty.

## A budget is a proof structure

An error budget is not merely a UI sum. It records how a final bound follows from component bounds under explicit propagation rules.

Sources include:

- design-surface tessellation;
- tool geometry approximation;
- tool dimension tolerance and runout;
- path planning discretization;
- curve fitting and linearization;
- coordinate transform uncertainty;
- numeric rounding;
- controller interpolation;
- servo following error;
- probing and calibration;
- thermal and material effects.

Some are compiler-controlled; others are runtime assumptions.

## Typed metrics

```ts
type ErrorBound =
  | { metric: "hausdorff-position"; frame: FrameId; value: Mm }
  | { metric: "normal-surface"; surface: Hash; value: Mm }
  | { metric: "max-gouge-depth"; target: Hash; value: Mm }
  | { metric: "transform-translation"; transform: Hash; value: Mm }
  | { metric: "transform-rotation"; transform: Hash; value: Radians }
  | { metric: "axis-following"; axis: AxisId; value: Mm };
```

Only compatible bounds can be combined directly. Rotational error becomes positional error only after multiplying by a radius or applying a more precise transform bound.

## Budget allocation

Suppose a feature tolerance is $0.05$ mm. The compiler may allocate:

```text
CAD tessellation             0.010 mm
planning and refinement      0.012 mm
postprocessor rounding       0.003 mm
frame and probing            0.010 mm
machine following            0.010 mm
reserve                      0.005 mm
```

This allocation is meaningful only if each number is a valid bound in a compatible metric and the composition theorem supports addition. A planner that consumes more than its allocation must refine or fail.

## Correlation and worst-case composition

Worst-case scalar addition is conservative when errors can align. Root-sum-square composition assumes statistical independence and a probabilistic interpretation; it is not a deterministic maximum bound. Certificates must identify whether a claim is worst-case, probabilistic, empirical, or nominal.

## Pass amplification

A small angular error $\delta\theta$ at radius $r$ creates positional error approximately $r\delta\theta$. An offset operation can amplify boundary error near sharp corners or topology changes. A coordinate transform with scale should not exist in rigid machining frames, but a calibration map may have local condition numbers.

Each pass needs a sensitivity or Lipschitz bound when it propagates prior error.

## Residual-driven refinement

An adaptive algorithm should report a residual related to the claimed metric. For a height field, comparing neighboring samples is not automatically a surface-error residual. A useful refinement loop is:

```text
propose approximation
compute certified local bound
if bound <= allocated budget: accept cell
else if subdivision limit not reached: subdivide
else: inconclusive
```

The residual, subdivision depth, and unresolved regions become evidence.

## Runtime budgets

Some budget components are checked at runtime. A tool measurement may tighten diameter uncertainty; a probe sequence may establish a frame bound; a machine calibration record may establish following-error limits. If live bounds exceed the bundle allocation, execution is refused or the job is recompiled.

## Worked example: final surface error

Suppose:

- target mesh outer deviation: $0.008$ mm;
- drop-cutter field bound: $0.012$ mm;
- arc fitting: $0.004$ mm;
- output rounding: $0.001$ mm;
- frame translation: $0.010$ mm;
- angular frame uncertainty: $0.0002$ rad at 50 mm radius, contributing $0.010$ mm.

A conservative additive position bound is $0.045$ mm if the metrics and directions align. If the requested bound is $0.04$ mm, the program is not certified merely because each individual pass met its local default.

## Exercises

1. Classify six error sources as numerical, model, calibration, or process uncertainty.
2. Convert an angular bound to a positional bound at a given radius.
3. Explain when root-sum-square composition is inappropriate.
4. Design a typed budget for a planar pocket floor.
5. State a residual-driven refinement algorithm.
6. Explain how a runtime measurement can discharge a compile-time assumption.

# Certificate Schemas and Proof Graphs

> **Learning objectives.** The reader should be able to write precise claims, bind them to artifacts and assumptions, organize dependencies as a DAG, and avoid ambiguous status labels.

## A certificate is a graph of propositions

A certificate should not be one boolean or one table of reassuring labels. It is a graph connecting artifacts, assumptions, claims, evidence, and checkers.

![A certificate dependency graph binds source, IRs, final bytes, setup, and runtime state.](figures/certificate_dag.png){width=86%}

A change to any dependency invalidates downstream claims.

## Structured claims

```ts
interface Claim {
  id: ClaimId;
  subject: ArtifactRef;
  proposition: StructuredPredicate;
  result:
    | "proved-exact"
    | "proved-bounded"
    | "translation-validated"
    | "exhaustive-finite-check"
    | "simulation-only"
    | "assumed"
    | "unknown"
    | "refuted";
  method: MethodRef;
  assumptions: readonly AssumptionRef[];
  evidence: readonly EvidenceRef[];
  dependencies: readonly ClaimId[];
  bound?: ErrorBound;
  checker: CheckerIdentity;
}
```

The proposition is not a string such as `"gouge"`. It is structured:

```ts
{
  kind: "max-penetration",
  sweptArtifact: "sha256:...",
  protectedTarget: "sha256:...",
  maximum: mm(0.02),
  metric: "signed-normal-depth",
}
```

## Results and methods are orthogonal

“Checked to resolution” combines method and conclusion. Separate:

- proposition;
- method;
- result;
- quantitative bound;
- coverage;
- assumptions.

A sampled simulation method may produce a counterexample and thus refute a claim. Failure to find a counterexample does not upgrade it to proof.

## Assumption records

```ts
interface Assumption {
  id: AssumptionId;
  proposition: StructuredPredicate;
  source: "operator" | "calibration" | "machine-attestation" | "library";
  evidence?: ArtifactRef;
  validFrom?: Timestamp;
  validUntil?: Timestamp;
  runtimeCheck?: RuntimeCheckSpec;
}
```

Examples:

- tool T1 diameter lies in $[3.170,3.180]$ mm;
- fixture model hash matches setup QR code;
- machine firmware belongs to a compatible semantic profile;
- G54 transform lies inside an interval;
- stock dimensions meet a measured bound.

## Evidence types

```ts
type Evidence =
  | AbstractInterpretationTrace
  | IntervalSubdivisionTree
  | CollisionSeparationWitness
  | CoverageWitness
  | ParseBackTraceComparison
  | SolverCertificate
  | ModelCheckingTrace
  | Counterexample
  | CalibrationRecord
  | SignatureAttestation;
```

Evidence schemas should be stable, versioned, and independently checkable.

## Claim granularity

Separate claims by meaning:

- target no-gouge;
- fixture collision;
- holder collision;
- rapid-through-stock;
- required removal;
- machine travel;
- feed and dynamics;
- modal equivalence;
- final spindle stop;
- exact upload hash;
- controller start acknowledgement.

One generic evidence object should not be able to mint unrelated rows. Strong typing can enforce this:

```ts
function certifyGouge(
  claim: GougeClaim,
  evidence: GougeEvidence,
): CertifiedClaim;
```

## Completeness policy

A bundle policy states which claims are required for a use class:

```text
Preview-only:
  schema, finite values, parse success

Attended air cut:
  travel, controller parse-back, exact bytes, runtime identity

Attended material cut:
  + target, fixture, holder, stock, tool and WCS assumptions

Unattended production:
  + protocol liveness, runtime monitor, calibrated dynamic bounds,
    recovery and interlock claims
```

A function such as `isFullyVerified` must derive from explicit policy, not from absence of severe diagnostics.

## Worked example: false evidence reuse

Suppose a dexel simulation checks low rapids and spoilboard penetration but receives no target surface. It can support:

```text
rapid-through-current-stock sampled simulation
spoilboard penetration sampled simulation
```

It cannot support:

```text
maximum gouge into protected target <= 0.02 mm
```

because the proposition's target artifact is absent. A schema that requires `protectedTargetHash` and target-specific evidence prevents the incorrect promotion.

## Exercises

1. Write a structured claim for machine travel.
2. Design separate evidence types for rapid collision and target gouge.
3. Explain why a digital signature is not a semantic proof.
4. Define a completeness policy for an attended air cut.
5. Draw a dependency graph for an arc-linearized final job.
6. Describe certificate invalidation after a tool change.

# Trusted Checkers and Proof-Carrying CAM

> **Learning objectives.** The reader should be able to minimize a trusted computing base, explain proof-carrying code, design producer-consumer separation, and evaluate checker independence.

## The producer is complicated

CAM planners use spatial indices, heuristics, solvers, floating-point kernels, caches, parallelism, and UI state. Treating this entire implementation as trusted makes assurance fragile.

Proof-carrying code separates an untrusted producer from a consumer-side checker: code arrives with evidence that it satisfies a policy, and the consumer validates the evidence before execution [R20]. Foundational proof-carrying code reduces reliance on specialized verification-condition generators by grounding evidence in a smaller logic [R21].

The analogous CAM architecture is:

```text
complex planner / optimizer / postprocessor
                 |
                 v
        artifact + evidence
                 |
                 v
       small independent checker
                 |
           accept or reject
```

## Trusted computing base

A realistic trusted base includes:

- definitions of claim predicates;
- canonical artifact hashing and serialization;
- independent parsers and semantic interpreters;
- robust numeric primitives used by checkers;
- certificate dependency validation;
- runtime identity and upload-hash handshake;
- a small execution monitor;
- explicitly accepted physical assumptions.

The UI, heuristic planners, optimizers, and preview renderer should not need to be trusted.

## Independence

A checker that calls the same buggy helper as the producer is not strongly independent. Independence can be improved by:

- separate implementations;
- different algorithms or representations;
- reduced feature set;
- smaller codebase;
- strict schemas;
- deterministic behavior;
- extensive property and differential testing;
- optional mechanized proofs for critical kernels.

Independence is a spectrum, not a binary property.

## Proof objects versus recomputation

A checker can:

1. recompute the property independently;
2. verify a compact witness;
3. check a formal proof term;
4. combine these methods.

For contour coverage, a cell decomposition witness may be cheaper than re-running planning. For modal equivalence, replaying both programs is simple. For a linear or mixed-integer optimizer, a solver certificate or dual bound may support optimality.

## Checker resource bounds

Evidence can be adversarial or malformed. Checkers need:

- schema validation;
- size and recursion limits;
- deterministic resource bounds;
- integer overflow protection;
- denial-of-service resistance;
- explicit version compatibility;
- no execution of producer-supplied code.

## Compositional certificates

If pass $P_1$ establishes $R_1(A,B)$ and $P_2$ establishes $R_2(B,C)$, a composition theorem establishes $R(A,C)$:

$$
R_1(A,B)\land R_2(B,C)\Longrightarrow R(A,C).
$$

The theorem may accumulate quantitative bounds. Certificate composition should be implemented by a checker, not inferred from matching stage names.

## Mechanization strategy

Formalize the small semantic core first:

- canonical command semantics;
- controller modal semantics;
- pass-relation composition;
- certificate validity;
- state-machine authorization;
- numeric lemmas for common primitives.

Leave complex search algorithms unverified but validated. This yields more assurance per unit effort than attempting to prove an entire CAM application at once.

## Worked example: validating a solver schedule

An untrusted optimizer returns operation order $\pi$, path orientations, total cost $J$, and a lower bound $L$. The checker verifies:

1. $\pi$ is a permutation of required operations;
2. all precedence edges are respected;
3. every selected orientation is legal;
4. each transition cost is recomputed;
5. total cost equals the sum;
6. the lower-bound certificate is valid;
7. the reported gap $(J-L)/L$ is correct.

The optimizer's internal search does not enter the trusted base.

## Exercises

1. List the trusted components in a minimal CAM checker.
2. Give an example where a checker is insufficiently independent.
3. Compare recomputation with witness checking.
4. Design resource limits for a certificate checker.
5. State a composition theorem for two bounded geometric passes.
6. Choose three components suitable for formal mechanization and justify them.

# Temporal Semantics and Controller Protocols

> **Learning objectives.** The reader should be able to model the host-controller interaction as a state machine, state safety and liveness properties, and reason about ambiguous failures and authorization races.

## The protocol is part of the compiler target

A final G-code file is useless unless the correct bytes are transferred, stored, selected, and executed. The controller interface is therefore part of the compilation and deployment semantics.

![A simplified controller and job lifecycle state machine.](figures/controller_fsm.png){width=96%}

## States and transitions

A controller model should include states such as:

- disconnected;
- connected but unidentified;
- idle;
- uploading;
- ready with a specific stored hash;
- running a specific execution instance;
- held;
- stopped;
- alarmed;
- ambiguous or quarantined after timeout.

Transitions have guards and effects. `Resume` is not a read-only command; it enables motion. `FeedHold` is a stop-class action and should remain available even when ordinary command admission is blocked.

## Safety properties

Examples:

$$
\Box(\operatorname{Running}(h)\Rightarrow
\operatorname{Authorized}(h)).
$$

$$
\Box(\operatorname{Start}(h)\Rightarrow
\operatorname{StoredHash}=h).
$$

$$
\Box(\operatorname{Motion}\Rightarrow
\neg\operatorname{Alarm}).
$$

$$
\Box(\operatorname{GenericReadPath}\Rightarrow
\neg\operatorname{MotionEffect}).
$$

The last property requires complete parsing, not prefix classification.

## Liveness properties

$$
\Box(\operatorname{UploadStarted}\Rightarrow
\Diamond(\operatorname{Ready}\lor\operatorname{Failed}\lor\operatorname{Quarantined})).
$$

$$
\Box(\operatorname{AbortRequested}\Rightarrow
\Diamond(\operatorname{Stopped}\lor\operatorname{Alarm})).
$$

Liveness depends on assumptions about network delivery, controller scheduling, and machine responsiveness. Those assumptions must be stated.

## Atomic admission and execution

A preflight that checks state, releases a lock, and later sends motion has a time-of-check/time-of-use gap. Another command can change the state between admission and execution.

A safer design serializes:

```text
acquire session authority
refresh live state
check preconditions
bind authorization to command/job hash and state epoch
send command
observe acknowledgement or quarantine
release authority
```

The state epoch invalidates admission if intervening events occur.

## Ambiguous timeout

After sending a command, a timeout does not imply that the machine did nothing. The command may have executed while the reply was lost. The correct successor state is a set of possibilities. The session should enter an ambiguous/quarantined state until re-synchronized through a trusted status query and protocol boundary.

Blind retry is especially dangerous for motion or state-changing commands.

## Message streams and loss

Safety-relevant events should not share a lossy queue designed for UI telemetry. A dropped alarm, completion marker, or protocol sentinel can make the host state inconsistent. Separate durable control events from best-effort display updates.

Partial writes must also be handled. A transport `Write` may write fewer bytes than requested without a fatal error; command framing must loop until complete or fail before execution can be assumed.

## Model checking

A finite abstraction of the protocol can be exhaustively checked for invariants and deadlocks. TLA-style specifications are well suited to concurrency and temporal properties [R8, R34]. Hybrid automata extend state machines with continuous dynamics when stop distance and watchdog timing matter [R35].

## Worked example: compound command classification

A classifier that examines only the first whitespace token may label:

```text
status\nG0 X100
```

as read-only because `status` is first. The semantic policy concerns every parsed command in the payload. A fail-closed grammar rejects embedded newlines or parses all blocks and proves that every effect belongs to the allowed class.

## Exercises

1. Define states and transitions for upload, start, hold, resume, and abort.
2. State three safety and two liveness properties.
3. Explain the time-of-check/time-of-use race in preflight.
4. Model an ambiguous timeout as a set of successor states.
5. Explain why stop commands should bypass ordinary motion admission.
6. Design a fail-closed read-only command grammar.
7. Identify which messages require durable delivery.

# Runtime Assurance and Physical Assumptions

> **Learning objectives.** The reader should be able to bind compile-time evidence to live machine state, design a runtime assurance monitor, and distinguish logical proof from physical validation.

## Conditional assurance

A compile-time certificate proves a conditional theorem:

```text
if assumptions A hold, artifact B satisfies claims C
```

Runtime preflight must establish as much of $A$ as possible. The remaining assumptions require operator acceptance, calibration records, or physical interlocks.

## Hash-bound execution

![A runtime handshake binds authorization to exact bytes and live state.](figures/runtime_handshake.png){width=88%}

A robust protocol is:

1. Host proposes certified bundle hash $H$ and assumptions $A$.
2. Controller stores exact bytes and reports stored hash $H'$.
3. Controller reports identity, firmware, homing, WCS, tool state, alarm state, and job state $M$.
4. Host verifies $H'=H$ and $M\models A$.
5. Host authorizes one execution instance of $H$.
6. Controller acknowledges start of that exact instance.
7. Host monitors state until terminal completion, abort, or fault.

## Runtime checks

Possible checks include:

- machine identity and firmware semantics profile;
- homed axes;
- active work coordinate system and measured transform;
- tool ID, length, and optional diameter measurement;
- fixture/setup identifier;
- stock presence and dimensions;
- door, probe, and accessory interlocks;
- no active alarm;
- exact stored job hash;
- controller idle or permitted paused state;
- calibration validity period.

## Runtime assurance monitor

A runtime assurance architecture places a small trusted monitor around a more capable controller or host planner. Simplex-style systems switch to a trusted safety action when an advanced component approaches an unsafe region; modern runtime-assurance frameworks apply this to cyber-physical systems [R36].

For a Z1-class machine, a realistic monitor can enforce:

- authorized state transitions;
- command classes;
- job-hash binding;
- axis and feed envelopes;
- spindle/tool consistency;
- watchdog policy;
- communication-loss behavior;
- explicit confirmation of stop.

## Stopping distance and latency

A stop request is not an instantaneous stop. If velocity is $v$ and guaranteed deceleration is $a$, a simple lower bound on stopping distance is:

$$
d_{stop}\ge\frac{v^2}{2a},
$$

plus command, communication, and controller latency. A safety envelope must reserve this distance. Feed hold may preserve the job and decelerate differently from emergency stop or reset.

## Physical model validation

Even perfect software cannot prove that the CAD fixture model matches reality. Useful physical validation practices include:

- setup identifiers and photographs;
- measured stock and tool records;
- probing routines with uncertainty;
- air cuts and reduced-feed first runs;
- witness marks or sacrificial stock;
- calibration artifacts;
- independent inspection of critical dimensions;
- bounded validity periods for calibration.

These produce assumptions and attestations, not mathematical facts from the compiler.

## Degradation policies

A runtime system should define what happens when an assumption cannot be established:

- refuse execution;
- downgrade to preview or air-cut mode;
- require explicit operator override with recorded rationale;
- reduce feed and restrict motion envelope;
- re-probe or re-measure;
- recompile with wider uncertainty;
- quarantine the session after ambiguity.

Silent continuation is not a policy.

## Worked example: changed G54

A job was certified under work transform $T_0$ with uncertainty set $\Xi$. Before execution, the live controller reports $T_1$. The runtime checker computes whether $T_1$ lies inside the certified set. If not, the travel and collision claims are stale. The correct response is to revalidate or recompile, not to rely on the same file hash.

## Design rules

\begin{warningbox}
A certificate is valid only for the exact artifact and assumption set named by its claims. Live machine identity, tools, frames, setup, and controller state are inputs to execution, not incidental operator details.
\end{warningbox}

## Exercises

1. Design a runtime assumption manifest for a pocket job.
2. Explain why upload success is weaker than exact-byte execution.
3. Derive stopping distance for a given velocity and deceleration, then add latency distance.
4. List five monitor-enforceable properties and five physical assumptions it cannot prove.
5. Design a degradation policy for an unknown tool measurement.
6. Explain how a changed WCS invalidates geometric certificates.

\part{Part V - Operations Research for CAM}

# Feasibility Before Optimality

> **Learning objectives.** The reader should be able to formulate CAM planning as constrained optimization, separate hard constraints from objectives, and state what evidence is needed for feasibility and optimality claims.

## The feasible set comes first

Operations research gives a useful decomposition:

$$
\min_{x\in\mathcal{F}} J(x),
$$

where $\mathcal{F}$ is the feasible set and $J$ is an objective.

![Feasibility is independently checked before objective claims are trusted.](figures/or_decomposition.png){width=94%}

For CAM, hard constraints may include:

- target and fixture separation;
- required material removal;
- machine travel and kinematics;
- tool compatibility;
- process precedence;
- entry feasibility;
- maximum velocity, acceleration, jerk, and contour error;
- stock-dependent support and clearance;
- probing and setup dependencies;
- controller capability.

The objective may combine cycle time, retract distance, tool changes, wear, energy, surface quality, or risk margin.

## Why safety is not a penalty

A common heuristic objective is:

$$
J=T+\lambda C_{collision}.
$$

No finite $\lambda$ makes collision categorically forbidden. A sufficiently large time benefit can outweigh the penalty. Safety belongs in constraints:

$$
C_{collision}(x)=0.
$$

Soft penalties are appropriate for preferences, not invariant violations.

## Decision variables

A full CAM problem may contain:

- discrete strategy choices;
- tool assignment;
- operation ordering;
- path orientation;
- entry selection;
- link route;
- feed schedule;
- spindle schedule;
- setup assignment;
- tolerances allocated to passes.

This creates mixed discrete-continuous optimization. Solving it monolithically is often impractical. A staged architecture solves subproblems while preserving feasibility certificates.

## Constraint generation

Not every constraint must be enumerated upfront. A cutting-plane or lazy-constraint workflow can:

1. solve a relaxed problem;
2. check the candidate geometrically;
3. extract a violated constraint or conflict;
4. add it to the optimization model;
5. repeat.

The checker remains authoritative. The optimizer uses counterexamples to improve search.

## Feasible, optimal, and near-optimal

These claims are distinct:

- **Feasible:** all hard constraints have been checked.
- **Locally optimal:** no move in a specified neighborhood improves the objective.
- **Globally optimal:** no feasible solution has lower objective.
- **Gap bounded:** $L\le J^*\le J$, where $L$ is a valid lower bound.

The relative gap is:

$$
\frac{J-L}{\max(|L|,\eta)},
$$

with a small $\eta$ to avoid division by zero.

## Lexicographic objectives

Safety remains a constraint, but quality objectives may have strict priority:

1. meet dimensional and finish requirements;
2. minimize tool changes;
3. minimize cycle time;
4. minimize retract distance.

Lexicographic optimization avoids arbitrary weights between incomparable units.

## Worked example: roughing schedule

Suppose three roughing operations can use T1, while a finish operation requires T2 and must follow all roughing. The optimizer chooses among roughing orders and path orientations to minimize links, then performs one tool change. A candidate schedule includes a precedence witness and independently checked links. The objective value is accepted only after feasibility is established.

## Exercises

1. Formulate a CAM problem with three hard constraints and two objective terms.
2. Explain why a collision penalty is insufficient.
3. Give two discrete and two continuous decision variables.
4. Design a lazy-constraint loop using a collision checker.
5. Distinguish feasible, locally optimal, and globally optimal.
6. Propose a lexicographic objective for a hobby CNC job.

# Sequencing and Precedence-Constrained Routing

> **Learning objectives.** The reader should be able to model operation ordering as a routing problem with precedence, encode orientation choices, and validate a schedule independently.

## From nearest neighbor to routing

Choosing the nearest next path is fast but ignores precedence, directionality, tool changes, and stock effects. A more complete abstraction treats operations or path endpoints as nodes in a routing problem.

The precedence-constrained traveling salesman problem has been applied directly to CNC toolpath optimization [R31]. Variants include generalized TSP, asymmetric TSP, and clustered routing.

## Node and state expansion

A path with two legal orientations can be represented by two states:

```text
P.forward: enter at A, exit at B
P.reverse: enter at B, exit at A
```

Selecting one excludes the other. Transition cost depends on exit and entry positions, stock state, tool state, and link feasibility.

For tool choices, create states `(operation, tool, orientation, entry)`. This can grow rapidly, motivating decomposition and pruning.

## Precedence graph

Let binary variable $y_{ij}=1$ when operation $i$ occurs before $j$. For each precedence edge $(i,j)$:

$$
pos_i+1\le pos_j.
$$

A simpler schedule checker receives a permutation $\pi$ and verifies:

$$
\forall(i,j)\in E,\quad \pi^{-1}(i)<\pi^{-1}(j).
$$

## Asymmetric transition costs

Link costs are often asymmetric:

- a path endpoint may have different safe exits;
- climb-only orientation changes entry and exit;
- Z heights differ;
- stock removal makes later links easier;
- spindle or coolant transitions have direction-dependent costs.

Use a directed cost graph.

## Mixed-integer model sketch

Let $x_{ij}$ indicate transition from state $i$ to $j$:

$$
\min \sum_{i,j}c_{ij}x_{ij}
$$

subject to one incoming and outgoing transition for each selected operation state, selection constraints, precedence constraints, and subtour elimination. Tool changes can add fixed transition costs.

For large jobs, exact MILP may be too slow. Heuristics, local search, dynamic programming over small precedence width, or branch-and-bound can provide good candidates. Verification remains the same.

## Stock-dependent edges

A fixed edge cost $c_{ij}$ assumes the link from $i$ to $j$ is independent of earlier operations. This is often false. One conservative approach computes links against initial stock. A more precise approach augments state with relevant stock features or recomputes edges during search.

The abstraction should state which stock model the cost and feasibility use.

## Schedule witness

```ts
interface ScheduleWitness {
  permutation: readonly OperationId[];
  chosenVariants: readonly VariantId[];
  precedencePositions: ReadonlyMap<OperationId, number>;
  transitions: readonly {
    from: VariantId;
    to: VariantId;
    link: PathRef;
    cost: Seconds;
    stockState: StockStateRef;
  }[];
  objective: Seconds;
  lowerBound?: Seconds;
}
```

The checker recomputes every field.

## Worked example: four contours

Four contour paths have two orientations each. Two inner contours must precede the outer contour so the part remains supported. A nearest-neighbor tour chooses the outer contour second and violates support. A precedence-aware solver excludes that tour, then selects orientations minimizing legal transition cost.

## Exercises

1. Create a directed state graph for two reversible and one fixed-direction path.
2. Write a permutation-based precedence checker.
3. Explain why transition costs are asymmetric.
4. Formulate one-in/one-out routing constraints.
5. Give a case where stock-dependent links break a static cost matrix.
6. Design a schedule witness and checker.

# Free-Space Linking and Configuration Space

> **Learning objectives.** The reader should be able to formulate linking as path planning in configuration space, compare retract, graph-search, and field methods, and attach a continuous clearance certificate.

## The link planner's problem

Given start configuration $q_s$, goal $q_g$, obstacles $O_C$, and admissible configurations $Q$, find:

$$
\gamma:[0,1]\to Q\setminus O_C
$$

minimizing a cost such as length or time.

For a three-axis machine with fixed orientation, the configuration is usually $(x,y,z)$. Fixtures, stock, and machine exclusions are expanded by the tool assembly.

## Baseline: certified retract policy

A simple policy is:

1. rise to a certified clearance Z;
2. move in XY;
3. descend.

Advantages:

- easy to reason about;
- predictable;
- often robust to stock complexity.

Disadvantages:

- unnecessary vertical motion;
- clearance plane may not exist around tall fixtures;
- machine rapids may not follow assumed paths;
- one global height can be overly conservative.

A baseline policy is valuable as a fallback and reference implementation.

## Visibility graphs and A*

For polygonal or polyhedral configuration obstacles, graph methods connect visible vertices and search for a shortest route. A raster or voxel occupancy grid supports A* or Dijkstra search. The discretization must be conservative: blocked cells should outer-enclose obstacles, and diagonal corner cutting must be controlled.

A path found on a grid needs smoothing and continuous revalidation.

## Distance fields and Eikonal equations

A weighted shortest-path field $T(x)$ can satisfy an Eikonal equation:

$$
|\nabla T(x)|F(x)=1,
$$

where $F$ is a speed or inverse cost field. Fast marching computes monotonically advancing arrival times efficiently [R29]. Backtracing the gradient yields a candidate path. Fast marching has also been used for geodesic computation on surfaces [R30].

The numerical field does not itself prove collision freedom. The extracted path must be checked against a conservative obstacle enclosure, and discretization error must be bounded.

## Clearance-aware objectives

Shortest distance can graze obstacles. A robust cost may penalize low clearance:

$$
J(\gamma)=\int_0^1
\left(1+\lambda\phi(d(\gamma(s),O_C))\right)
\|\gamma'(s)\|ds,
$$

where $\phi$ grows as clearance decreases. Hard minimum clearance remains a constraint.

## Dynamic feasibility

A geometric link with a sharp corner may be dynamically infeasible at rapid speed. The linker can:

- produce piecewise paths then rely on controller blending with a certified contour-error bound;
- round corners within free-space margins;
- generate a dynamically feasible spline;
- lower the speed near corners.

Geometry and time parameterization should remain separate but coordinated.

## Link certificate

A link claim should include:

- path artifact hash;
- stock-state hash;
- fixture and tool-assembly hashes;
- frame and uncertainty assumptions;
- minimum certified separation or collision-free enclosure;
- machine travel claim;
- dynamics claim or explicit handoff to feed scheduling.

## Worked example: low retract

A planner proposes a low Z link through a region cleared by the immediately preceding roughing pass. The link is shorter than a full retract. Its certificate depends on the post-roughing stock artifact. Reordering the link earlier invalidates the certificate even though the path geometry is unchanged.

## Exercises

1. Formulate a three-axis link problem in configuration space.
2. Compare retract, visibility graph, A*, and fast marching approaches.
3. Explain why a grid path needs continuous revalidation.
4. Design a clearance-aware cost with a hard margin.
5. Give a dynamically infeasible but collision-free path.
6. List the dependencies of a stock-specific link certificate.

# Feed Scheduling and Optimal Control

> **Learning objectives.** The reader should be able to separate geometric path from time law, derive path-coordinate constraints, and validate a feed schedule under machine and process limits.

## Path parameterization

Given geometric path $q(s)$ for $s\in[0,1]$, choose monotone $s(t)$. Then:

$$
\dot q=q'(s)\dot s,
$$

$$
\ddot q=q''(s)\dot s^2+q'(s)\ddot s.
$$

Axis velocity and acceleration limits become inequalities in $\dot s$ and $\ddot s$. Jerk adds another derivative and coupling terms.

## Time-optimal path parameterization

The objective is:

$$
\min T=\int_0^1\frac{1}{\dot s(s)}ds
$$

subject to dynamic constraints. CNC minimum-time trajectory research includes velocity, acceleration, jerk, and tracking-error limits [R32]. TOPP-RA formulates reachability-based time-optimal path parameterization for general constraints [R33].

## Curvature and contour speed

For planar curvature $\kappa$, normal acceleration is:

$$
a_n=v^2\kappa.
$$

Thus:

$$
v\le\sqrt{\frac{a_n^{max}}{|\kappa|}}.
$$

A sharp corner has unbounded ideal curvature and requires stopping, blending, or geometric smoothing. Controller lookahead determines the actual trajectory.

## Process constraints

Machine dynamics are not the only limits. Cutting may constrain:

- chip load;
- spindle power and torque;
- tool deflection;
- engagement angle;
- material removal rate;
- surface finish;
- minimum feed to avoid rubbing;
- maximum plunge feed.

A feed schedule should reference process models and their uncertainty.

## Controller realization

A host schedule expressed as continuously varying feed may be approximated by discrete feed changes or controller overrides. The postprocessor needs a realization theorem: the controller's trajectory remains within the certified envelope.

If the controller performs undocumented lookahead, host-side optimality and dynamic guarantees are conditional on a calibrated model.

## Feed schedule witness

```ts
interface FeedScheduleWitness {
  pathHash: Hash;
  knots: readonly {
    s: number;
    speed: MmPerMin;
    accelerationBound: number;
  }[];
  axisVelocityMargins: readonly Interval<number>[];
  axisAccelerationMargins: readonly Interval<number>[];
  processMargins: readonly ProcessMargin[];
  estimatedTime: Seconds;
}
```

The checker evaluates constraints over each interval, not only at knots.

## Worked example: circular path

For a circle of radius $10$ mm and maximum normal acceleration $500$ mm/s$^2$:

$$
\kappa=0.1\ \mathrm{mm}^{-1},
$$

$$
v\le\sqrt{500/0.1}=70.71\ \mathrm{mm/s}
=4242.6\ \mathrm{mm/min}.
$$

A requested feed of $6000$ mm/min violates the acceleration constraint even before axis limits and process force are considered.

## Exercises

1. Derive $\dot q$ and $\ddot q$ from $q(s(t))$.
2. Compute a curvature-limited feed for a given radius and acceleration.
3. Explain why knot-only checking can miss a violation.
4. List four process constraints beyond machine dynamics.
5. Design a schedule witness for piecewise-constant feed.
6. Explain how controller lookahead complicates guarantees.

# Robust and Multiobjective Optimization

> **Learning objectives.** The reader should be able to formulate robust constraints, compare worst-case and chance constraints, construct Pareto tradeoffs, and record optimization evidence honestly.

## Nominal optimization is brittle

A plan optimal for nominal tool diameter, transform, and stock may become unsafe under small deviations. Robust optimization requires constraints to hold for every parameter in an uncertainty set $\mathcal{U}$:

$$
g(x,u)\le0\quad\forall u\in\mathcal{U}.
$$

This can be conservative but aligns with bounded safety claims.

## Chance constraints

When uncertainty has a justified probability model, a chance constraint is:

$$
\Pr[g(x,U)\le0]\ge1-\alpha.
$$

A 99.9% success probability is not equivalent to a deterministic safety bound. The certificate must identify the distribution, evidence, and acceptable risk level. For collision and protected-target constraints, deterministic robust margins are generally preferable.

## Scenario methods

When robust constraints are difficult, optimize over sampled scenarios and validate the final candidate with a deterministic checker. Scenario optimization can improve candidates but sampled feasibility alone should not be labeled universal proof.

## Multiple objectives

Cycle time, surface quality, tool wear, energy, noise, and safety margin can conflict. The Pareto frontier contains solutions where no objective improves without worsening another.

Methods include:

- weighted sums;
- lexicographic optimization;
- epsilon constraints;
- interactive selection;
- goal programming.

The UI should expose meaningful tradeoffs rather than one opaque score.

## Margin as an objective

After hard minimum clearance is satisfied, additional margin can be optimized:

$$
\max \min_{t} d(\operatorname{Assembly}(t),O).
$$

This produces more robust links, though it may increase time. Margin evidence can also simplify runtime uncertainty accommodation.

## Sensitivity analysis

A useful optimizer reports how objective and feasibility change with inputs:

- time sensitivity to feed limit;
- clearance sensitivity to WCS error;
- scallop sensitivity to stepover;
- tool-change sensitivity to operation grouping;
- optimality sensitivity to stock-dependent link costs.

High sensitivity identifies assumptions that deserve measurement or larger reserve.

## Worked example: two link candidates

Candidate A takes 1.2 seconds with certified clearance 0.15 mm. Candidate B takes 1.35 seconds with clearance 2.0 mm. If frame uncertainty can reach 0.2 mm, A is infeasible under the robust model while B remains feasible. The nominal fastest candidate is not the robust optimum.

## Exercises

1. Formulate a robust travel constraint under bounded WCS translation.
2. Distinguish robust and chance constraints.
3. Explain why scenario testing is not universal proof.
4. Construct a two-objective Pareto example for time and clearance.
5. Define clearance margin as an optimization objective.
6. Propose a sensitivity report for a finishing operation.

\part{Part VI - Implementation and the Dropcut/Z1 Case Study}

# Package Architecture for a TypeScript CAM Compiler

> **Learning objectives.** The reader should be able to map semantic layers to packages, enforce dependency direction, isolate trusted checkers, and design compilation artifacts for browser and command-line frontends.

## Architectural boundaries

A package graph should follow semantic dependency, not UI convenience. A practical decomposition is:

```text
@cam/units, @cam/math
        |
@cam/ir, @cam/machine
        |
@cam/geometry, @cam/strategies
        |
@cam/planner
        |
@cam/compiler
        |
@cam/post-*
        |
@cam/analysis and checker packages
```

User interfaces depend on these packages. Core packages should not depend on React, Redux, CodeMirror, Three.js, browser globals, or controller sockets.

![The reviewed Dropcut package architecture and controller boundary.](figures/dropcut_arch.png){width=92%}

## A semantics package

The reviewed architecture contains IR, compiler, analysis, and postprocessor packages, but a mature design should add a pure semantic center:

```text
@cam/semantics
  canonical command interpreter
  machine-state transition relation
  stock-effect semantics
  trace events
  structured predicates
```

All of the following should use it:

- simulator;
- static analyzer;
- time estimator;
- pass validators;
- final G-code comparator;
- controller model;
- tests.

A viewer may approximate for speed but should not silently become the reference semantics.

## Checker packages

Separate producer and checker namespaces:

```text
@cam/geometry              untrusted algorithms
@cam/geometry-checker      robust predicates and witness checks

@cam/compiler              untrusted passes
@cam/pass-checker          translation validators

@cam/post-makera           serializer
@cam/gcode-semantics       independent parser and interpreter

@cam/analysis              simulations and diagnostics
@cam/certificate-checker   policy and proof graph verification
```

This separation helps detect accidental reuse of producer code in the checker.

## Artifact store

Large arrays and meshes should not be duplicated through Redux or JSON. Use content-addressed immutable artifacts:

```ts
interface ArtifactStore {
  put<T>(schema: SchemaRef<T>, value: T): Promise<ArtifactRef<T>>;
  get<T>(ref: ArtifactRef<T>): Promise<Readonly<T>>;
  has(hash: Hash): Promise<boolean>;
}
```

The project state contains references. Derived artifacts can be cached by pass key and invalidated by dependency hashes.

## Worker boundaries

Browser execution should isolate expensive or untrusted work:

- script evaluation worker or subprocess;
- planning worker;
- geometry/checker worker;
- viewer worker when practical.

Messages contain immutable artifact references and structured diagnostics. The UI thread never executes user scripts or long geometric loops.

## CLI and Studio parity

The Studio and CLI should call the same compilation service over the same artifacts. A shared orchestration function prevents divergence:

```ts
interface CompileRequest {
  source: ArtifactRef<ScriptSource>;
  project: ArtifactRef<ProjectManifest>;
  target: TargetProfileRef;
  policy: AssurancePolicyRef;
}

interface CompileResponse {
  artifacts: CompilationArtifactGraph;
  diagnostics: readonly Diagnostic[];
  finalBundle?: ArtifactRef<ExecutableBundle>;
}
```

The Studio adds interactive visualization; the CLI adds reproducible automation. Neither should implement hidden pass logic.

## Dependency rules

Enforce with linting or build tooling:

- `@cam/ir` imports only units, math, and schema utilities;
- strategies do not import postprocessors;
- postprocessors do not import UI packages;
- checkers do not import producer implementations except shared semantic definitions;
- controller code does not accept arbitrary CAM objects, only final bundles and explicit control operations;
- code that can move the machine is in a narrow package with mandatory authorization context.

## Versioning

Version separately:

- schemas;
- semantic relations;
- pass implementations;
- checkers;
- controller dialect profiles;
- machine profiles;
- certificate policies.

A pass bug fix may change implementation version without changing its relation. A revised geometric metric changes the relation and requires a new claim type.

## Worked package layout

```text
packages/
  units/
  math/
  schemas/
  ir/
  semantics/
  geometry/
  geometry-checker/
  strategies/
  planner/
  compiler/
  pass-checker/
  machine/
  controller-ir/
  gcode-parser/
  gcode-semantics/
  post-rs274/
  post-makera/
  certificate-schema/
  certificate-checker/
  runtime-assurance/
apps/
  studio/
  cli/
  z1-controller/
```

## Exercises

1. Draw an allowed import graph for the proposed packages.
2. Identify three producer/checker code-sharing risks.
3. Design an artifact-store cache key for machine lowering.
4. Specify a worker message for planning progress and cancellation.
5. Explain how Studio and CLI can share the exact same compiler.
6. Define a version-compatibility rule for a certificate checker.

# An End-to-End Certified Pocket Example

> **Learning objectives.** The reader should be able to trace one operation through every IR, state pass relations, construct a certificate graph, and identify compile-time and runtime obligations.

## Source program

Consider a rectangular pocket in aluminum:

```ts
const T1 = tool.flatEndMill({
  id: "T1",
  diameter: mm(3.175),
  fluteLength: mm(12),
  stickout: mm(18),
});

const P1 = feature.rectPocket({
  id: "P1",
  frame: "work:G54",
  origin: p(mm(10), mm(10), mm(0)),
  width: mm(30),
  height: mm(20),
  depth: mm(4),
  wallTolerance: mm(0.04),
  floorTolerance: mm(0.04),
});

job.rough(P1, {
  tool: T1,
  radialAllowance: mm(0.20),
  axialAllowance: mm(0.20),
  strategy: "offset-pocket",
});

job.finish(P1, {
  tool: T1,
  strategy: "wall-and-floor",
});
```

The source leaves pass count, stepover, path orientation, entries, and links unspecified.

## Authoring and elaboration

The staged evaluator emits an immutable AST. Elaboration resolves:

- the G54 frame;
- tool geometry artifact;
- stock, target, and fixture references;
- material defaults;
- finite and positive domains;
- explicit tolerances and allowances;
- source spans and operation IDs.

Claims:

```text
C1: Plan IR is schema-valid and all references resolve.
C2: Every numeric field is finite and satisfies its domain.
C3: Every geometric quantity has a unit and frame.
```

## Intent IR

The roughing protected solid is the target dilated by allowance. The finishing protected solid is the nominal target eroded only by the allowed gouge tolerance. Required-removal regions are defined separately.

```ts
interface PocketIntent {
  requiredRemoval: SolidRef;
  forbiddenRemoval: SolidRef;
  permittedRemoval: SolidRef;
  wallMetric: SurfaceDeviationMetric;
  floorMetric: SurfaceDeviationMetric;
  dependencies: readonly OperationId[];
}
```

## Planning

The roughing strategy computes an inward tool-center region and offset loops. It emits:

- cut paths;
- coverage witness;
- boundary protection witness;
- directionality;
- local geometric error bounds;
- unresolved cells, ideally empty.

The finishing strategy emits one floor path family and one wall contour family with feature provenance.

Claims:

```text
C4: guaranteed inner sweep covers roughing required-removal region.
C5: outer cutting sweep avoids roughing protected region.
C6: finishing path deviation meets wall and floor metrics.
```

## Scheduling and linking

The scheduler chooses:

1. roughing passes from high to low depth;
2. floor finish;
3. wall finish;
4. safe entries and links against each evolving stock state;
5. spindle start before first cut and stop after final retract.

A schedule witness verifies precedence and recomputed transition costs.

Claims:

```text
C7: schedule respects all operation and stock-support dependencies.
C8: each entry is feasible for the tool and current stock.
C9: each traverse outer assembly sweep avoids stock and fixtures.
```

## Machine lowering

The Z1 profile resolves:

- machine travel;
- G54 semantics;
- supported spindle range;
- arc capability;
- maximum feeds;
- traverse expansion policy;
- probe and accessory semantics.

If the profile does not guarantee coordinated diagonal rapid, abstract traverses lower to explicit Z/XY/Z moves.

Claims:

```text
C10: every scheduled operation is supported or soundly transformed.
C11: all transformed poses remain within machine travel under WCS uncertainty.
C12: feeds and spindle requests lie within static profile limits.
```

## Controller lowering and serialization

Controller IR establishes a known modal state, emits explicit motion semantics, and ends in a defined safe state. The serializer generates deterministic bytes.

A final independent parser interprets the exact bytes and compares them to Controller IR.

Claims:

```text
C13: parsed final bytes produce the same canonical trace within rounding bound.
C14: no raw or unknown controller effect remains.
C15: final interpreted spindle state is off.
C16: byte artifact hash is H.
```

## Geometric final validation

Final interpreted motion is checked, not merely pre-postprocessor paths. The checker uses:

- outer tool and holder sweeps for forbidden intersections;
- inner cutting sweeps for guaranteed removal;
- evolving stock for traverses;
- target-specific deviation metrics;
- typed error budgets including formatting and transform uncertainty.

A local counterexample invalidates the corresponding claim and links back through provenance.

## Executable bundle

```ts
interface ExecutableBundle {
  jobBytes: ArtifactRef<Uint8Array>;
  jobHash: Hash;
  intent: ArtifactRef<IntentIR>;
  setup: ArtifactRef<SetupManifest>;
  machineProfile: ArtifactRef<MachineProfile>;
  certificate: ArtifactRef<CertificateGraph>;
  runtimePolicy: AssurancePolicyRef;
}
```

## Runtime discharge

Before start, the host establishes:

- live machine and firmware compatible with profile;
- homing complete;
- G54 inside certified interval;
- T1 loaded and measured within bounds;
- fixture/setup identity correct;
- no alarm;
- exact stored hash equals $H$.

Only then does it authorize one execution instance.

## Failure example

Suppose coordinate formatting consumes $0.003$ mm and the live G54 uncertainty is $0.020$ mm rather than the budgeted $0.010$ mm. The finishing wall budget exceeds $0.04$ mm. The same `.nc` bytes may remain syntactically valid, but the executable assurance bundle is not valid under the live setup. Revalidation or re-probing is required.

## Exercises

1. Draw the artifact and claim DAG for the pocket.
2. Identify which claims are exact, bounded, assumed, and runtime-checked.
3. Design a coverage witness for the roughing loops.
4. State the machine-lowering relation for a traverse.
5. Explain why final geometric checks use interpreted bytes.
6. Give three changes that invalidate the bundle without changing source code.

# Testing: Properties, Fuzzing, Differential, and Metamorphic Methods

> **Learning objectives.** The reader should be able to build a layered test strategy, derive property and metamorphic tests from semantics, and target numerical and protocol edge cases.

## Tests are not proofs, but semantics improve tests

Testing cannot establish universal correctness over continuous geometry and unbounded programs. It remains essential for finding defects, validating checkers, and protecting implementations. Formal semantics supply high-value oracles and transformations.

## Unit tests

Unit tests cover:

- constructors and domain checks;
- individual transfer functions;
- parser productions;
- numeric primitives;
- artifact hashing;
- diagnostic provenance;
- known controller replies;
- known geometry regressions.

Every reported production defect should become a permanent regression.

## Property-based tests

Properties include:

```text
path identity:
  concat(empty(start(p)), p) == p

exact transform inverse:
  inverse(T) * (T * p) == p within numeric bound

serialization determinism:
  serialize(ir, c) has stable bytes

round trip:
  parse(serialize(ir)) semantically equals ir

certificate dependency:
  changing any hashed input invalidates dependent claims

contour chaining:
  optimized result equals a collision-free tuple-key reference
```

Generate data across the full machine envelope, not only near the origin.

## Metamorphic testing

When an exact expected output is difficult, transform the input in a way that predicts a relation between outputs.

Examples:

- translating the entire setup and machine envelope should translate paths and preserve relative collision results;
- rotating a symmetric problem should rotate the output and preserve objective value;
- subdividing a line should preserve interpreted motion;
- adding redundant modal words should preserve canonical trace;
- reordering independent declarations should not change artifact semantics;
- increasing a tolerance should not turn a previously feasible geometric approximation infeasible, absent a strategy change.

Metamorphic tests are particularly effective for CAM algorithms.

## Differential testing

Compare independent implementations:

- optimized contour chaining versus slow tuple-key reference;
- postprocessor parse-back versus canonical interpreter;
- analytic line/arc bounds versus dense high-precision sampling;
- TypeScript checker versus a Python or exact-kernel reference;
- controller protocol parser versus captured traces;
- simulator representations at increasing resolution.

Agreement does not prove correctness, but disagreement is highly informative.

## Fuzzing parsers and protocols

Fuzz:

- embedded newlines;
- compound G-code blocks;
- comments and delimiters;
- truncated frames;
- duplicate or late replies;
- partial writes;
- invalid lengths and checksums;
- random byte loss;
- protocol switches;
- huge numeric fields;
- negative zero and non-finite values.

Stateful protocol fuzzing should track the model state and search for invariant violations.

## Numerical adversaries

Generate cases near:

- collinearity and tangency;
- grid nodes exactly on contour levels;
- saddle cells;
- coordinate quantization boundaries;
- machine travel limits;
- arc sweeps near $0$, $\pi$, and $2\pi$;
- very large and very small scales;
- negative coordinates;
- repeated points;
- tool/feature widths differing by tiny amounts.

## Checker mutation testing

Deliberately corrupt artifacts and witnesses:

- alter one coordinate after certification;
- change tool hash;
- remove a precedence edge;
- change modal preamble;
- truncate bytes;
- swap evidence between claim types;
- lie about resolution;
- modify a runtime assumption.

The checker should reject every mutation that affects the proposition.

## Physical test ladder

A physical bring-up sequence should progress through:

1. offline semantics and checker tests;
2. protocol tests against a fake machine;
3. live read-only status;
4. stop and hold tests;
5. bounded jog tests;
6. spindle/accessory tests without a tool where appropriate;
7. air cuts above stock;
8. sacrificial soft material;
9. attended real material at conservative feeds;
10. only then broader operation.

Each step has explicit pass/fail criteria and recovery procedures.

## Exercises

1. Write five property tests for path and frame algebra.
2. Design a translation metamorphic test for a pocket job.
3. Build a differential oracle for contour chaining.
4. List ten protocol fuzz cases.
5. Design a certificate mutation suite.
6. Define pass/fail criteria for an air-cut test.

# The Dropcut/Z1 Case Study: What the Defects Teach

> **Learning objectives.** The reader should be able to connect concrete implementation defects to missing semantic distinctions, derive architectural remedies, and avoid local patches that leave the underlying proof obligation undefined.

## Scope of the reviewed snapshot

The case study refers to the Dropcut Studio and Makera Z1 controller snapshot reviewed in August 2026, including the `task/cnc-control-dropcut` branch near commit `e82bed1e5a00f38f4441e6ea13e1265edc775928`. The repository already contains several strong decisions:

- non-modal canonical machining commands;
- explicit path objects and provenance;
- separate planning, machine lowering, postprocessing, and analysis packages;
- capability-driven lowering;
- emitted-motion analysis;
- risk classes and fresh preflight in the controller;
- visible distinctions between exact, sampled, unchecked, and unverifiable states.

The critical defects are valuable because each reveals a missing theory boundary.

## Case A: evidence for one claim minted another claim

In `packages/analysis/src/checks.ts`, sampled checks simulate emitted moves against stock and record rapid-through-material and spoilboard penetration. The inputs do not include a protected target surface or allowance model. In `packages/analysis/src/certificate.ts` and `packages/compiler/src/recertify.ts`, the same generic sampled status is attached to both `rapidCrash` and `gouge`.

The failure is not primarily a bad conditional. It is an evidence-type failure:

```text
SampledEvidence
   -> generic status
   -> any sampled certificate row
```

A correct architecture is:

```text
RapidCollisionEvidence -> RapidCollisionClaim
GougeEvidence          -> GougeClaim
RequiredRemovalEvidence -> RequiredRemovalClaim
```

The claim schema should require the target artifact hash. Without that dependency, a gouge proposition is not even well formed.

**Theory lesson:** propositions, methods, and evidence types must be separated. Sampled simulation without a continuous enclosure is not a bounded proof.

## Case B: same-realm script execution was described honestly but remained unsafe

`packages/script-host/src/sandbox.ts` shadows obvious globals and documents that this is not a security boundary. It still compiles with `new Function` in the current realm. The `timeoutMs` option is not enforced inside `runScript`; it relies on a caller to terminate a worker, while Node execution remains in-process.

A constructor/prototype path can recover ambient authority, and a nonterminating script can block an in-process CLI or worker until external termination.

The architectural fix is staging:

1. execute JavaScript in a separately terminable environment;
2. give it only serializable capabilities and inputs;
3. return an inert AST;
4. destroy the execution environment;
5. compile the AST without invoking user code.

**Theory lesson:** a capability API is not a sandbox unless the runtime enforces the capability boundary. The authoring language and CAM language must be distinct.

## Case C: free-text command classification used lexical prefixes instead of semantics

The controller classifier in `makera-z1-cli/pkg/makera/safety.go` splits on whitespace, classifies `parts[0]`, and returns read-only for unknown plain verbs. The protocol encoder strips only trailing newlines, so embedded separators can remain. A payload beginning with an allowed read verb can contain a later motion command.

The local patch “inspect more tokens” is not enough because controller syntax is block-structured and dialect-specific. The correct boundary is a fail-closed parser:

```text
bytes -> complete payload grammar -> command/effect AST -> risk policy
```

Unknown syntax is not read-only. It is denied or routed through explicit authorization.

**Theory lesson:** authorization is a semantic property of the complete parsed payload. Prefix classifiers are not interpreters.

## Case D: a packed endpoint key changed topology

`packages/geometry/src/contours.ts` quantizes coordinates at $10^{-6}$ mm and takes each coordinate modulo $2^{26}$. The key repeats after:

$$
2^{26}\times10^{-6}\ \mathrm{mm}=67.108864\ \mathrm{mm}.
$$

That period lies inside the machine work envelope. Unrelated endpoints separated by the period can share identity, causing disconnected contour segments to merge or appear closed.

The optimization was motivated by avoiding string allocation. It silently replaced a tuple with a non-injective encoding.

Repairs include:

- nested maps keyed by exact quantized integers;
- string tuple keys if performance is sufficient;
- signed integer pairing with a proven range;
- `BigInt` pairing;
- best of all for marching squares, grid-edge topology IDs.

**Theory lesson:** topological identity must be injective over the declared domain. Approximate numerical equality and hash keys require domain proofs, not comments.

## Cross-boundary findings

Several high-severity issues in the same snapshot follow the same pattern:

- work offsets were accepted in the API but not consistently emitted or incorporated into machine travel checks;
- a validator documented a safety epilogue that the final emitter did not append;
- probe commands confused the commanded endpoint with the measured result;
- a missing traverse could be replaced by a cut, changing stock semantics;
- raw text could invalidate modal compression;
- machine-profile identity was not fully bound to validation;
- entry and linking used incomplete stock and holder models;
- an error budget added heterogeneous geometric numbers without a formal metric;
- controller preflight and execution were not one atomic state transition;
- timeout and message-stream behavior could leave ambiguous session state.

Each is a boundary mismatch: API versus emitter, canonical versus modal semantics, planned versus final motion, nominal versus physical frame, admission versus execution.

## What should be preserved

The correct response is not a rewrite that discards the strong structure. Preserve:

- canonical non-modal commands;
- path and provenance types;
- capability-based lowering;
- exact-versus-sampled status distinctions;
- emitted-motion timeline;
- typed controller operations;
- stop commands that remain available;
- fresh preflight;
- no blind retry after ambiguous motion failure;
- dead-man jog behavior.

Then strengthen the semantic contracts and checker boundaries.

## Counterexample-driven architecture

Each critical bug should become more than a regression test. It should shape a type or schema:

| Counterexample | Architectural response |
|---|---|
| Gouge row without target | Target hash required by `GougeClaim`; only `GougeEvidence` can discharge it |
| Constructor escape | Process/worker isolation; AST-only output |
| Multiline command hidden after read verb | Complete fail-closed payload parser |
| 67.108864 mm key alias | Injective topology identity over machine envelope |
| WCS not reflected in travel | Frame-explicit machine lowering and runtime transform assumption |
| Safety stop promised but absent | Final-byte parse-back claim |
| Raw command changes modality | Unknown abstract state or rejection |
| Timeout reply arrives late | Quarantined protocol state and resynchronization |

## Exercises

1. For each critical bug, identify the false proposition the implementation could appear to establish.
2. Redesign the evidence types for sampled analysis.
3. Specify a fail-closed command grammar and policy.
4. Prove that a proposed endpoint-key scheme is injective over a declared coordinate range.
5. Explain why a final-byte validator catches an omitted epilogue.
6. Design a quarantined session state after timeout.
7. Choose one high-severity finding and state its missing pass relation.

# A Staged Migration Roadmap

> **Learning objectives.** The reader should be able to prioritize semantic risk, introduce certificates incrementally, and define acceptance gates for progressively stronger operating modes.

## Principles for migration

A running codebase cannot become formally verified in one step. The migration should:

- remove false claims before adding stronger claims;
- make unknown states explicit;
- introduce independent checkers at stable boundaries;
- preserve productive planners and UI work;
- bind artifacts and versions early;
- move physical control behind a narrow assurance interface;
- define operating modes with clear evidence requirements.

## Phase 0: stop overclaiming

Immediate changes:

1. Remove the automatic gouge upgrade when no target-specific evidence exists.
2. Rename sampled statuses to `simulation-only` unless a continuous enclosure theorem exists.
3. Mark holder, fixture, WCS, and machine identity dependencies explicitly.
4. Fail closed around raw controller effects and unknown commands.
5. Bind every certificate to the exact final byte hash.
6. Disable production-cut labels for bundles missing required claims.

This phase improves honesty even before new algorithms exist.

## Phase 1: harden language and identity

- execute scripts in a separately terminable environment;
- produce an immutable authoring AST;
- centralize finite/domain checks;
- deep-freeze or copy boundary objects;
- make units and frames explicit;
- content-address all major artifacts;
- record pass, strategy, machine, firmware, and checker versions;
- establish reproducible CLI compilation.

Acceptance gate: identical declared inputs produce identical Plan IR and final bytes.

## Phase 2: executable semantics and final-byte validation

- create `@cam/semantics`;
- create an independent controller parser and interpreter;
- define canonical trace events;
- validate modal compression;
- parse back exact bytes;
- compare interpreted final motion to Machine IR;
- verify preamble and epilogue on bytes;
- propagate rounding bounds.

Acceptance gate: every emitted production file has a successful parse-back equivalence claim.

## Phase 3: pass witnesses

Introduce translation validators for:

- unit/frame elaboration;
- path continuity and arc validity;
- traverse expansion;
- arc linearization and fitting;
- feed clamping;
- operation scheduling and precedence;
- machine capability lowering;
- serialization.

Acceptance gate: each production pass either emits a checked witness or is inside the trusted core with an explicit test/proof plan.

## Phase 4: robust geometric kernel

- exact/adaptive predicates for topology;
- interval and conservative bounding primitives;
- injective contour identity;
- tool and holder geometry;
- target, stock, and fixture artifact schemas;
- inner and outer swept-volume approximations;
- continuous line/arc collision checks;
- adaptive subdivision for general paths;
- claim-specific evidence.

Acceptance gate: no-gouge, fixture, holder, and required-removal claims are separate and target-specific.

## Phase 5: controller state machine

- replace generic free-text read paths with parsed operations;
- serialize admission and execution under one authority;
- add state epochs and exact job hashes;
- quarantine after ambiguous timeout;
- handle partial writes;
- separate durable control events from lossy telemetry;
- model upload, start, hold, resume, abort, and alarm;
- model-check key safety and liveness properties.

Acceptance gate: every motion-enabling transition is authorized against fresh state and exact artifact identity.

## Phase 6: runtime assurance

- live machine and firmware identity;
- tool/setup/WCS checks;
- calibration records and validity;
- exact upload hash acknowledgement;
- execution-instance binding;
- watchdog and stop confirmation;
- bounded dynamic envelopes;
- explicit degradation modes.

Acceptance gate: compile-time claims and runtime assumptions compose into one checked execution authorization.

## Phase 7: optimization maturity

Only after feasibility checking is dependable:

- precedence-aware sequencing;
- stock-dependent link planning;
- clearance-aware free-space search;
- feed scheduling under dynamics and process limits;
- solver certificates and objective gaps;
- robust/multiobjective optimization.

Optimization should consume and produce certified artifacts, not bypass the assurance pipeline.

## Operating-mode gates

### Development and preview

- schema-valid AST and IR;
- deterministic build record;
- simulation diagnostics;
- no machine connection required.

### Attended air cut

- exact bytes and parse-back;
- machine travel and controller-state claims;
- known tool and WCS;
- machine identity and fresh preflight;
- operator present with stop access.

### Attended material cut

- target, stock, fixture, holder, and tool models;
- no-gouge and collision evidence;
- required-removal or explicit limitation;
- runtime assumption discharge;
- conservative feeds and physical setup verification.

### Unattended or production use

- validated protocol liveness and recovery;
- runtime assurance monitor;
- calibrated dynamic and stopping envelopes;
- durable event logging;
- interlocks and physical risk assessment;
- organizational release and incident process.

## Definition of done

A production compiler is not done because it emits plausible G-code. A meaningful definition of done is:

1. Every stage has explicit syntax, semantics, and legality.
2. Every pass names a refinement relation.
3. Every approximation names metric, direction, bound, and assumptions.
4. Every safety claim has claim-specific evidence and an independent checker.
5. Every certificate is bound to exact artifacts and versions.
6. Every controller transition belongs to a checked state machine.
7. Runtime authorization establishes live assumptions and exact job identity.
8. Unknowns cause rejection or explicit degradation, never silent success.

## Final perspective

The theoretical framework is not decoration around CAM algorithms. It tells the implementation where facts live and which conclusions follow from them. Category theory clarifies path composition and effectful sequencing. Denotational semantics identifies acceptable physical outcomes. Operational semantics makes modal and machine behavior executable. Hoare logic derives preconditions. Abstract interpretation covers families of states. Robust geometry distinguishes samples from enclosures. Translation validation makes evolving algorithms practical. Proof-carrying architecture keeps the trusted base small. Operations research improves performance after feasibility is established. Temporal logic and runtime assurance close the gap between files and machines.

The result is not a claim that software can eliminate physical uncertainty. It is a system that states exactly what it knows, what it assumes, how it knows it, which artifact the statement concerns, and what must still be checked before motion begins.

## Exercises

1. Convert the roadmap into a twelve-month engineering plan with dependencies.
2. Define acceptance criteria for Phase 2 final-byte validation.
3. Choose three claims to implement first and justify their risk reduction.
4. Design an operating-mode policy for a hobby workshop.
5. Explain why optimization maturity is deliberately last.
6. Write a one-page assurance case for an attended air cut.

\appendix

# Notation and Mathematical Reference

This appendix collects the notation used throughout the book. It is intended as a working reference rather than a substitute for a course in analysis, geometry, logic, or optimization.

## Sets and functions

| Symbol | Meaning |
|---|---|
| $x\in A$ | $x$ is an element of set $A$ |
| $A\subseteq B$ | every element of $A$ belongs to $B$ |
| $A\cup B$ | union |
| $A\cap B$ | intersection |
| $A\setminus B$ | set difference |
| $A\times B$ | Cartesian product |
| $\mathcal{P}(A)$ | powerset of $A$ |
| $f:A\to B$ | total function from $A$ to $B$ |
| $R\subseteq A\times B$ | relation between $A$ and $B$ |
| $R;S$ | relational composition |

A partial function can be modeled as a total function into an option or result type, or as a relation with no successor for some inputs.

## Logic

| Symbol | Meaning |
|---|---|
| $\neg P$ | not $P$ |
| $P\land Q$ | $P$ and $Q$ |
| $P\lor Q$ | $P$ or $Q$ |
| $P\Rightarrow Q$ | implication |
| $P\Leftrightarrow Q$ | equivalence |
| $\forall x.P(x)$ | for every $x$, $P(x)$ |
| $\exists x.P(x)$ | there exists an $x$ satisfying $P(x)$ |
| $\Box P$ | always $P$ in temporal logic |
| $\Diamond P$ | eventually $P$ in temporal logic |

A safety property states that a bad event never occurs. A liveness property states that a good event eventually occurs. Many controller requirements combine both.

## Orders and lattices

A preorder $\sqsubseteq$ is reflexive and transitive. A partial order is also antisymmetric. In compiler refinement, $Q\sqsubseteq P$ commonly means that $Q$ has no behaviors outside those allowed by $P$.

A lattice provides least upper bounds $a\sqcup b$ and greatest lower bounds $a\sqcap b$. Abstract interpretation uses joins to combine control-flow paths.

## Metric spaces

A metric $d$ satisfies:

1. $d(x,y)\ge0$;
2. $d(x,y)=0$ iff $x=y$;
3. $d(x,y)=d(y,x)$;
4. $d(x,z)\le d(x,y)+d(y,z)$.

The open ball of radius $\varepsilon$ is:

$$
B_{\varepsilon}(x)=\{y\mid d(x,y)<\varepsilon\}.
$$

The distance from point $x$ to set $A$ is:

$$
d(x,A)=\inf_{a\in A}d(x,a).
$$

The Hausdorff distance between compact sets is:

$$
d_H(A,B)=\max\left(
\sup_{a\in A}d(a,B),
\sup_{b\in B}d(b,A)
\right).
$$

## Geometry and morphology

| Symbol | Meaning |
|---|---|
| $\mathbb{R}^n$ | $n$-dimensional Euclidean space |
| $SO(3)$ | three-dimensional rotation group |
| $SE(3)$ | rigid motions in three dimensions |
| $A\oplus B$ | Minkowski sum |
| $A\ominus B$ | erosion / Minkowski difference in morphological usage |
| $\partial A$ | boundary of $A$ |
| $\operatorname{int}(A)$ | interior of $A$ |
| $A^-$ | guaranteed inner approximation |
| $A^+$ | guaranteed outer approximation |

For sets $A,B\subseteq\mathbb{R}^n$:

$$
A\oplus B=\{a+b\mid a\in A,b\in B\}.
$$

The configuration obstacle for a translating tool $T$ and obstacle $O$ is $O\oplus(-T)$.

## Paths and trajectories

A geometric path is:

$$
\gamma:[0,1]\to Q,
$$

where $Q$ is configuration space. A time law is a monotone function:

$$
s:[0,T]\to[0,1].
$$

The trajectory is $q(t)=\gamma(s(t))$.

For a tool solid $T$ and pose $X(t)$:

$$
\operatorname{Sweep}(T,X)=\bigcup_t X(t)T.
$$

## Error and uncertainty

A deterministic bound states:

$$
|x-\hat{x}|\le\varepsilon.
$$

An interval enclosure states:

$$
x\in[x^-,x^+].
$$

A probabilistic statement has the form:

$$
\Pr(|X-\hat{x}|\le\varepsilon)\ge1-\alpha.
$$

These are not interchangeable.

## Optimization

A constrained optimization problem is:

$$
\min_x J(x)\quad\text{subject to}\quad g_i(x)\le0,\ h_j(x)=0.
$$

A lower bound $L$ and feasible candidate cost $J$ satisfy:

$$
L\le J^*\le J.
$$

The gap quantifies the possible distance from global optimality.

# Reference IR and Certificate Schemas

The following schemas are intentionally explicit. They illustrate a coherent design; a production implementation may split fields or use generated codecs.

## Primitive identities and units

```ts
type Hash = string & { readonly __brand: "sha256" };
type SchemaId = string & { readonly __brand: "schema" };
type ArtifactId = string & { readonly __brand: "artifact-id" };
type FrameId = string & { readonly __brand: "frame" };
type ToolId = string & { readonly __brand: "tool-id" };
type FeatureId = string & { readonly __brand: "feature-id" };
type OperationId = string & { readonly __brand: "operation-id" };
type ClaimId = string & { readonly __brand: "claim-id" };
type AssumptionId = string & { readonly __brand: "assumption-id" };

type Mm = number & { readonly __unit: "mm" };
type MmPerMin = number & { readonly __unit: "mm/min" };
type Rpm = number & { readonly __unit: "rpm" };
type Radians = number & { readonly __unit: "rad" };
type Seconds = number & { readonly __unit: "s" };

interface ArtifactRef<T = unknown> {
  readonly id: ArtifactId;
  readonly hash: Hash;
  readonly schema: SchemaId;
  readonly mediaType: string;
  readonly byteLength: number;
  readonly _type?: T;
}
```

## Frames and transforms

```ts
interface Point3<F extends FrameId = FrameId> {
  readonly x: Mm;
  readonly y: Mm;
  readonly z: Mm;
  readonly frame: F;
}

interface Quaternion {
  readonly x: number;
  readonly y: number;
  readonly z: number;
  readonly w: number;
}

interface RigidTransform<From extends FrameId, To extends FrameId> {
  readonly from: From;
  readonly to: To;
  readonly translation: readonly [Mm, Mm, Mm];
  readonly rotation: Quaternion;
}

interface TransformUncertainty {
  readonly translationBox: readonly [
    readonly [Mm, Mm],
    readonly [Mm, Mm],
    readonly [Mm, Mm],
  ];
  readonly angularRadius: Radians;
  readonly confidence: "deterministic-bound" | "probabilistic";
}
```

## Geometry and setup

```ts
type GeometryRef = ArtifactRef<GeometryArtifact>;

interface GeometryArtifact {
  readonly kind:
    | "mesh"
    | "brep"
    | "implicit"
    | "voxel"
    | "dexel"
    | "height-field"
    | "primitive";
  readonly frame: FrameId;
  readonly enclosure?: {
    readonly direction: "inner" | "outer" | "two-sided" | "none";
    readonly metric: ErrorMetric;
    readonly bound?: ErrorBound;
  };
}

interface ToolAssembly {
  readonly id: ToolId;
  readonly cuttingGeometry: GeometryRef;
  readonly assemblyGeometry: GeometryRef;
  readonly fluteLength: Mm;
  readonly stickout: Mm;
  readonly measurementUncertainty: readonly ErrorBound[];
}

interface SetupManifest {
  readonly stock: GeometryRef;
  readonly target: GeometryRef;
  readonly fixtures: readonly GeometryRef[];
  readonly tools: readonly ArtifactRef<ToolAssembly>[];
  readonly frameGraph: ArtifactRef<FrameGraph>;
  readonly workSystem: string;
  readonly material?: ArtifactRef;
  readonly setupIdentity?: string;
}
```

## Paths

```ts
interface LineSegment<F extends FrameId> {
  readonly kind: "line";
  readonly to: Point3<F>;
}

interface ArcSegment<F extends FrameId> {
  readonly kind: "arc";
  readonly to: Point3<F>;
  readonly center: Point3<F>;
  readonly axis: readonly [number, number, number];
  readonly sweep: Radians;
}

interface SplineSegment<F extends FrameId> {
  readonly kind: "spline";
  readonly basis: "bezier" | "bspline" | "nurbs";
  readonly degree: number;
  readonly controlPoints: readonly Point3<F>[];
  readonly knots?: readonly number[];
  readonly weights?: readonly number[];
}

type Segment<F extends FrameId> =
  | LineSegment<F>
  | ArcSegment<F>
  | SplineSegment<F>;

interface Path<F extends FrameId = FrameId> {
  readonly frame: F;
  readonly start: Point3<F>;
  readonly end: Point3<F>;
  readonly segments: readonly Segment<F>[];
  readonly identityPolicy: "exact" | "snapped" | "witnessed-approximate";
  readonly approximation?: readonly ErrorBound[];
}
```

## Intent IR

```ts
interface RegionSpecification {
  readonly geometry: GeometryRef;
  readonly interpretation:
    | "required-removal"
    | "forbidden-removal"
    | "permitted-removal";
}

interface SurfaceRequirement {
  readonly surface: GeometryRef;
  readonly metric: "normal-deviation" | "hausdorff" | "scallop-height";
  readonly maximum: Mm;
}

interface OperationIntentBase {
  readonly id: OperationId;
  readonly feature: FeatureId;
  readonly frame: FrameId;
  readonly toolConstraints: readonly ToolConstraint[];
  readonly predecessors: readonly OperationId[];
  readonly regions: readonly RegionSpecification[];
  readonly surfaceRequirements: readonly SurfaceRequirement[];
  readonly provenance: Provenance;
}

interface PocketIntent extends OperationIntentBase {
  readonly kind: "pocket";
  readonly floor: GeometryRef;
  readonly boundary: GeometryRef;
  readonly roughingAllowance: {
    readonly radial: Mm;
    readonly axial: Mm;
  };
}

type OperationIntent = PocketIntent | HoleIntent | SurfaceIntent | CustomIntent;

interface IntentProgram {
  readonly schemaVersion: string;
  readonly setup: ArtifactRef<SetupManifest>;
  readonly operations: readonly OperationIntent[];
}
```

## Toolpath and schedule IR

```ts
interface PlannedPath {
  readonly id: string;
  readonly path: ArtifactRef<Path>;
  readonly operation: OperationId;
  readonly tool: ToolId;
  readonly phase: "entry" | "rough" | "semi-finish" | "finish" | "exit";
  readonly directionality:
    | { readonly kind: "reversible" }
    | { readonly kind: "fixed"; readonly reason: string };
  readonly feedPolicy: FeedPolicy;
  readonly provenance: Provenance;
}

interface ScheduledStep {
  readonly id: string;
  readonly beforeState: string;
  readonly afterState: string;
  readonly beforeStock: ArtifactRef;
  readonly afterStock: ArtifactRef;
  readonly command: CanonicalCommand;
  readonly dependencies: readonly string[];
}

interface ScheduledProgram {
  readonly setup: ArtifactRef<SetupManifest>;
  readonly steps: readonly ScheduledStep[];
  readonly finalState: string;
}
```

## Canonical commands

```ts
type CanonicalCommand =
  | {
      readonly kind: "selectTool";
      readonly tool: ToolId;
    }
  | {
      readonly kind: "startSpindle";
      readonly rpm: Rpm;
      readonly direction: "cw" | "ccw";
    }
  | {
      readonly kind: "stopSpindle";
    }
  | {
      readonly kind: "traverse";
      readonly path: ArtifactRef<Path>;
      readonly clearanceClaim?: ClaimId;
    }
  | {
      readonly kind: "cut";
      readonly path: ArtifactRef<Path>;
      readonly tool: ToolId;
      readonly feed: FeedPolicy;
      readonly operation: OperationId;
    }
  | {
      readonly kind: "probe";
      readonly path: ArtifactRef<Path>;
      readonly expectedContact: ContactModel;
      readonly outputBinding: string;
    }
  | {
      readonly kind: "dwell";
      readonly duration: Seconds;
    }
  | {
      readonly kind: "pause";
      readonly reason: string;
    };
```

## Machine and controller IR

```ts
interface MachineCommandBase {
  readonly beforeToken: string;
  readonly afterToken: string;
  readonly provenance: Provenance;
}

type MachineCommand =
  | (MachineCommandBase & {
      readonly kind: "axisMove";
      readonly interpolation: "rapid" | "linear" | "cwArc" | "ccwArc";
      readonly target: Point3<"machine">;
      readonly center?: Point3<"machine">;
      readonly feed?: MmPerMin;
    })
  | (MachineCommandBase & {
      readonly kind: "setSpindle";
      readonly rpm: Rpm;
      readonly direction: "cw" | "ccw" | "off";
    })
  | (MachineCommandBase & {
      readonly kind: "probeMove";
      readonly direction: readonly [number, number, number];
      readonly maximumTravel: Mm;
      readonly feed: MmPerMin;
      readonly outputBinding: string;
    });

interface ControllerBlock {
  readonly words: readonly ControllerWord[];
  readonly comments: readonly string[];
  readonly provenance: Provenance;
}

interface ControllerProgram {
  readonly dialect: string;
  readonly declaredInitialState: ModalState;
  readonly blocks: readonly ControllerBlock[];
}
```

## Diagnostics and provenance

```ts
interface SourceSpan {
  readonly artifact: Hash;
  readonly start: { readonly line: number; readonly column: number };
  readonly end: { readonly line: number; readonly column: number };
}

interface PassRecord {
  readonly passId: string;
  readonly passVersion: string;
  readonly relation: string;
  readonly inputHashes: readonly Hash[];
  readonly configurationHash: Hash;
}

interface Provenance {
  readonly source?: SourceSpan;
  readonly feature?: FeatureId;
  readonly operation?: OperationId;
  readonly parents: readonly Hash[];
  readonly passHistory: readonly PassRecord[];
}

interface Diagnostic {
  readonly code: string;
  readonly severity: "info" | "warning" | "error";
  readonly message: string;
  readonly provenance?: Provenance;
  readonly claim?: ClaimId;
  readonly counterexample?: ArtifactRef;
  readonly remediation?: string;
}
```

## Quantitative claims

```ts
type ErrorMetric =
  | "hausdorff-position"
  | "normal-surface"
  | "max-gouge-depth"
  | "minimum-clearance"
  | "transform-translation"
  | "transform-rotation"
  | "axis-following";

interface ErrorBound {
  readonly metric: ErrorMetric;
  readonly value: number;
  readonly unit: "mm" | "rad";
  readonly frame?: FrameId;
  readonly subject?: Hash;
  readonly interpretation: "deterministic" | "probabilistic" | "empirical";
  readonly confidence?: number;
}

type StructuredPredicate =
  | {
      readonly kind: "disjoint";
      readonly left: Hash;
      readonly right: Hash;
      readonly minimumSeparation?: Mm;
    }
  | {
      readonly kind: "max-penetration";
      readonly swept: Hash;
      readonly protectedTarget: Hash;
      readonly maximum: Mm;
      readonly metric: "signed-normal-depth" | "euclidean-depth";
    }
  | {
      readonly kind: "contains";
      readonly outer: Hash;
      readonly inner: Hash;
      readonly tolerance?: Mm;
    }
  | {
      readonly kind: "trace-refines";
      readonly source: Hash;
      readonly target: Hash;
      readonly relation: string;
    }
  | {
      readonly kind: "runtime-state-satisfies";
      readonly state: Hash;
      readonly assumptionSet: Hash;
    };
```

## Certificate graph

```ts
interface CheckerIdentity {
  readonly id: string;
  readonly version: string;
  readonly binaryHash: Hash;
  readonly relationVersion: string;
}

interface Claim {
  readonly id: ClaimId;
  readonly subject: ArtifactRef;
  readonly proposition: StructuredPredicate;
  readonly result:
    | "proved-exact"
    | "proved-bounded"
    | "translation-validated"
    | "exhaustive-finite-check"
    | "simulation-only"
    | "assumed"
    | "unknown"
    | "refuted";
  readonly method: string;
  readonly assumptions: readonly AssumptionId[];
  readonly evidence: readonly ArtifactRef[];
  readonly dependencies: readonly ClaimId[];
  readonly bound?: ErrorBound;
  readonly checker: CheckerIdentity;
}

interface Assumption {
  readonly id: AssumptionId;
  readonly proposition: StructuredPredicate;
  readonly source: "operator" | "calibration" | "machine" | "library";
  readonly evidence?: ArtifactRef;
  readonly runtimeCheck?: string;
  readonly validUntil?: string;
}

interface CertificateGraph {
  readonly schemaVersion: string;
  readonly rootSubject: ArtifactRef;
  readonly artifacts: readonly ArtifactRef[];
  readonly assumptions: readonly Assumption[];
  readonly claims: readonly Claim[];
  readonly policy: string;
}
```

# Checker Algorithms

This appendix gives reference algorithms. They emphasize the shape of soundness obligations rather than a particular implementation language.

## Certificate graph checker

```text
checkCertificate(graph, policy):
  validate schema and version compatibility
  verify every artifact hash against its bytes
  build maps for artifacts, assumptions, and claims

  for each claim:
    require unique claim id
    require subject exists and hash matches
    require all dependencies exist
    require all evidence artifacts exist
    require all assumptions exist
    require checker identity allowed by policy

  require claim dependency graph is acyclic
  process claims in topological order:
    require dependencies have acceptable results
    invoke claim-specific checker
    compare returned proposition, result, and bound
    reject if producer metadata overstates checker result

  require every policy-required proposition exists
  require no required claim is unknown, assumed-only, or simulation-only
  return accepted graph plus normalized summary
```

Soundness depends on claim-specific checkers and policy definitions. The graph checker prevents missing, stale, cyclic, or cross-applied evidence.

## Translation-validation skeleton

```text
validatePass(input I, output O, witness W, relation R):
  verify hash(I), hash(O), hash(W)
  verify schemas and pass versions
  switch R:
    ExactTraceEquality:
      ti = interpret(I)
      to = interpret(O)
      return compareExact(ti, to)

    TraceRefinement:
      return checkSimulationRelation(I, O, W)

    BoundedGeometry(metric, epsilon):
      return checkGeometricWitness(I, O, W, metric, epsilon)

    IntentSatisfaction:
      return checkIntentWitness(I, O, W)

    FeasibleOptimization:
      f = checkFeasibility(O, W.feasibility)
      j = recomputeObjective(O)
      l = checkLowerBound(W.lowerBound)
      return combine(f, j, l)
```

## Abstract-state proof checker

```text
checkAbstractTrace(program, proof):
  require proof has one entry per block
  state = abstractInitialState(program.initialAssumptions)

  for i in 0 .. program.blocks.length-1:
    require state is included in proof[i].before
    computed = abstractTransfer(program.blocks[i], proof[i].before)
    require computed is included in proof[i].after
    require localSafetyPredicates(proof[i].before, program.blocks[i])
    state = proof[i].after

  require finalPolicy(state)
  return success
```

“Included” uses the abstract-domain order. The producer may provide less precise states than the checker computes, but they must remain conservative.

## Continuous collision checker

```text
checkPath(path gamma, assembly T, obstacles O, interval I, budget):
  P = boundPath(gamma, I)             // outer pose enclosure
  W = sweepEnclosure(P, T, uncertainty)

  if disjoint(W, outer(O)) with separation delta > 0:
    return ProvedSafe(I, delta)

  if definitelyIntersects(inner(W), inner(O)):
    return Refuted(I, counterexampleRegion)

  if width(I) <= budget.parameterLimit
     or diameter(P) <= budget.spatialLimit
     or recursionDepth >= budget.maxDepth:
    return Inconclusive(I, W)

  split I into I1, I2
  r1 = checkPath(gamma, T, O, I1, budget)
  r2 = checkPath(gamma, T, O, I2, budget)
  return combine(r1, r2)
```

The `definitelyIntersects` branch requires inner enclosures. If these are unavailable, the checker may prove safety or return inconclusive but cannot always prove collision.

## Required-removal checker

```text
checkRequiredRemoval(required R, cutMotions M):
  guaranteed = empty set
  for motion in M:
    innerSweep = computeInnerSweep(motion.tool, motion.path)
    guaranteed = union(guaranteed, innerSweep)

  residual = difference(R, guaranteed)
  if residual is empty by exact/conservative test:
    return proved
  if a definitely nonempty inner subset of residual is found:
    return refuted with residual witness
  return inconclusive with unresolved cells
```

## Modal parse-back checker

```text
checkFinalBytes(controllerIR C, bytes B, dialect D, initialState M0):
  parsed = independentParse(B, D)
  if parse error: reject

  sourceTrace = interpretControllerIR(C, M0)
  byteTrace = interpretParsedBlocks(parsed, M0)

  compare:
    event kinds and ordering
    tool/spindle/accessory state
    path endpoints and interpolation semantics
    probe command/result bindings
    final modal state
    numeric deviation against formatting budget

  verify required preamble and epilogue predicates
  return trace-equivalence or bounded-refinement claim
```

## Schedule checker

```text
checkSchedule(intent, candidate, witness):
  require candidate contains each required operation exactly once
  require no unknown operations

  positions = map operation -> index
  for each precedence edge (a,b):
    require positions[a] < positions[b]

  state = initial process state
  cost = 0
  for each step:
    require step preconditions hold in state
    verify chosen orientation and entry
    verify link against referenced stock state
    state = apply certified effects(step, state)
    cost += recompute transition and operation cost

  require state satisfies final policy
  require cost == witness.objective within numeric bound
  optionally verify lower-bound certificate
```

## Error-budget composition

```text
composeBound(inputBound e, passLocal p, sensitivity L, metric m):
  require e.metric == m or verified metric conversion exists
  require p.metric == m
  require L is a valid upper Lipschitz/sensitivity bound
  return L * e.value + p.value
```

For vector or transform bounds, use a matrix or interval propagation rule rather than a scalar function.

## Runtime authorization checker

```text
authorize(bundle B, liveState M, storedHash H'):
  verify certificate graph of B under requested operating policy
  require H' == B.jobHash
  require live machine identity matches B.machineProfile
  require firmware semantics compatible
  require no alarm and permitted controller state
  require homing state satisfies assumptions
  require active WCS lies inside certified transform set
  require tool and setup identity satisfy assumptions
  require calibration records valid

  epoch = read controller state epoch
  token = sign(jobHash, epoch, assumptionSnapshotHash, expiry)
  return one-use authorization token
```

Execution consumes the token only if the state epoch remains unchanged.

# A Temporal Controller Model

The following TLA+-style pseudocode illustrates a model suitable for refinement and model checking. It is not tied to a specific syntax version.

## Variables

```text
VARIABLES
  conn,                 \* disconnected | connected
  identity,             \* unknown or machine/profile identity
  ctrlState,            \* idle | uploading | ready | running | held | alarm | quarantined
  storedHash,           \* hash or none
  executingHash,        \* hash or none
  authorizedHash,       \* hash or none
  stateEpoch,           \* monotonically increasing integer
  commandQueue,
  durableEvents,
  telemetry,
  homed,
  activeWcs,
  tool,
  alarm,
  lastOutcome
```

## Initial state

```text
Init ==
  /\ conn = "disconnected"
  /\ identity = "unknown"
  /\ ctrlState = "idle"
  /\ storedHash = None
  /\ executingHash = None
  /\ authorizedHash = None
  /\ stateEpoch = 0
  /\ commandQueue = << >>
  /\ durableEvents = << >>
  /\ telemetry = << >>
  /\ homed = FALSE
  /\ activeWcs = Unknown
  /\ tool = Unknown
  /\ alarm = FALSE
  /\ lastOutcome = None
```

## Connection and identification

```text
Connect ==
  /\ conn = "disconnected"
  /\ conn' = "connected"
  /\ identity' = "unknown"
  /\ UNCHANGED <<ctrlState, storedHash, executingHash, ...>>

Identify(id) ==
  /\ conn = "connected"
  /\ identity' = id
  /\ stateEpoch' = stateEpoch + 1
  /\ UNCHANGED <<conn, ctrlState, storedHash, ...>>
```

## Upload

```text
BeginUpload(h) ==
  /\ conn = "connected"
  /\ ctrlState = "idle"
  /\ ctrlState' = "uploading"
  /\ storedHash' = None
  /\ lastOutcome' = None
  /\ stateEpoch' = stateEpoch + 1

UploadSucceeded(h) ==
  /\ ctrlState = "uploading"
  /\ ctrlState' = "ready"
  /\ storedHash' = h
  /\ Append(durableEvents, [kind |-> "upload-ack", hash |-> h])
  /\ stateEpoch' = stateEpoch + 1

UploadAmbiguous ==
  /\ ctrlState = "uploading"
  /\ ctrlState' = "quarantined"
  /\ storedHash' = Unknown
  /\ lastOutcome' = "ambiguous-upload"
  /\ stateEpoch' = stateEpoch + 1
```

## Authorization and start

```text
Authorize(h, epoch) ==
  /\ ctrlState = "ready"
  /\ storedHash = h
  /\ epoch = stateEpoch
  /\ homed
  /\ ~alarm
  /\ RuntimeAssumptionsHold(identity, activeWcs, tool)
  /\ authorizedHash' = h
  /\ UNCHANGED <<ctrlState, executingHash, stateEpoch, ...>>

Start(h) ==
  /\ ctrlState = "ready"
  /\ storedHash = h
  /\ authorizedHash = h
  /\ ctrlState' = "running"
  /\ executingHash' = h
  /\ authorizedHash' = None        \* consume one-use authorization
  /\ stateEpoch' = stateEpoch + 1
```

## Hold, resume, abort, and alarm

```text
FeedHold ==
  /\ ctrlState = "running"
  /\ ctrlState' = "held"
  /\ stateEpoch' = stateEpoch + 1

Resume(h, epoch) ==
  /\ ctrlState = "held"
  /\ executingHash = h
  /\ authorizedHash = h
  /\ epoch = stateEpoch
  /\ ctrlState' = "running"
  /\ authorizedHash' = None
  /\ stateEpoch' = stateEpoch + 1

Abort ==
  /\ ctrlState \in {"running", "held", "uploading", "ready"}
  /\ ctrlState' = "idle"
  /\ executingHash' = None
  /\ authorizedHash' = None
  /\ Append(durableEvents, [kind |-> "aborted"])
  /\ stateEpoch' = stateEpoch + 1

Fault(reason) ==
  /\ ctrlState \in {"running", "held", "uploading", "ready"}
  /\ ctrlState' = "alarm"
  /\ alarm' = TRUE
  /\ lastOutcome' = reason
  /\ authorizedHash' = None
  /\ stateEpoch' = stateEpoch + 1
```

## Next-state relation

```text
Next ==
  \/ Connect
  \/ \E id : Identify(id)
  \/ \E h : BeginUpload(h)
  \/ \E h : UploadSucceeded(h)
  \/ UploadAmbiguous
  \/ \E h, epoch : Authorize(h, epoch)
  \/ \E h : Start(h)
  \/ FeedHold
  \/ \E h, epoch : Resume(h, epoch)
  \/ Abort
  \/ \E reason : Fault(reason)
  \/ StatusUpdate
  \/ Disconnect
```

## Invariants

```text
TypeInvariant ==
  ctrlState \in {"idle", "uploading", "ready", "running", "held", "alarm", "quarantined"}

RunningIsAuthorized ==
  ctrlState = "running" => executingHash # None

RunningMatchesStored ==
  ctrlState = "running" => executingHash = storedHash

NoMotionInAlarm ==
  alarm => ctrlState # "running"

UnknownUploadCannotRun ==
  storedHash = Unknown => ctrlState # "running"

OneUseAuthorization ==
  ctrlState = "running" => authorizedHash = None
```

## Temporal properties

```text
AbortEventuallyTerminal ==
  [](AbortRequested => <>(ctrlState \in {"idle", "alarm", "quarantined"}))

UploadEventuallyResolves ==
  [](ctrlState = "uploading" => <>(ctrlState \in {"ready", "alarm", "quarantined", "idle"}))

NoHashSubstitution ==
  [](ctrlState = "running" => executingHash = storedHash)
```

These liveness properties require fairness and environment assumptions. A model checker should search for deadlocks, unauthorized transitions, stale-epoch authorizations, and dropped durable events.

# Selected Exercise Solutions

These solutions emphasize method. Many design exercises admit several correct architectures; the proposed answers state the assumptions under which they are sound.

## Chapter 1

**Exercise 1.** Two programs for the same metric absolute linear cut are:

```text
G21 G90 G1 X10 Y0 F300
```

and:

```text
G21
G90
G1 F300
X10 Y0
```

They are equivalent only if both start from the same known position, use the same plane and coordinate system, and the controller treats omitted Z as unchanged. The second depends on modal persistence of `G1` and `F300`; the first states them in the motion block.

**Exercise 4.** A probing theorem can be stated:

$$
\operatorname{CheckProbeBundle}(B)=true\land A
\Rightarrow
\operatorname{Execute}(B)
\in\{\operatorname{Contact}(m),\operatorname{NoContact},\operatorname{Alarm}\},
$$

where any contact measurement $m$ lies inside the declared uncertainty model and the path remains within travel. Assumptions include a functioning probe, correct probe radius/length, known direction, and compatible firmware semantics.

## Chapter 2

**Exercise 2.** A toolpath that never crosses the target but stops halfway through a pocket satisfies no-gouge and fails required removal. This demonstrates that preservation and completion are independent propositions.

**Exercise 4.** A raster witness can contain the eroded tool-center region, scan direction, line offsets, guaranteed inner swept strips, protected-boundary outer sweep, unresolved boundary cells, and local error bounds. The checker recomputes strip coverage and boundary separation.

## Chapter 3

**Exercise 1.** For relations $R\subseteq A\times B$, $S\subseteq B\times C$, and $T\subseteq C\times D$, an element $(a,d)$ belongs to $(R;S);T$ iff there exist $b,c$ with $(a,b)\in R$, $(b,c)\in S$, and $(c,d)\in T$. The same existential condition characterizes $R;(S;T)$, so composition is associative.

**Exercise 7.** After an ambiguous motion timeout, a relation can map the pre-state to at least two successors: command not executed, or command executed but reply lost. The host should enter a state representing both until a trusted status exchange resolves the uncertainty.

## Chapter 4

**Exercise 2.** For:

$$
T=\begin{bmatrix}R&p\\0&1\end{bmatrix},
$$

with $R^{-1}=R^T$:

$$
T^{-1}=\begin{bmatrix}R^T&-R^Tp\\0&1\end{bmatrix}.
$$

**Exercise 4.** If work X lies in $[0,180]$ and work-to-machine translation lies in $[29.8,30.2]$, machine X lies in $[29.8,210.2]$. A machine limit of 200 mm is violated for part of the uncertainty set.

## Chapter 5

**Exercise 1.** Denotationally, a dwell preserves physical configuration and stock while advancing time by the requested duration within timing tolerance. Operationally:

$$
\langle dwell(d),\sigma\rangle\Downarrow(\sigma[t:=t+d'],\operatorname{DwellEvent}(d'))
$$

for $d'$ in the controller's allowed timing interval.

**Exercise 3.** A feed-hold property is:

$$
\Box(\operatorname{HoldRequested}\Rightarrow
\Diamond(\operatorname{Held}\lor\operatorname{Stopped}\lor\operatorname{Alarm})).
$$

A stronger bounded-time property requires assumptions about communication and deceleration.

## Chapter 6

**Exercise 3.** For $R=20$ mm, half-circle sweep $\pi$, and sagitta $\varepsilon=0.01$ mm:

$$
\theta_{max}=\arccos(1-0.01/20)\approx0.03162.
$$

Each full chord spans $2\theta_{max}\approx0.06324$ rad, so at least $\lceil\pi/0.06324\rceil=50$ segments are required.

**Exercise 6.** A sound result type is:

```ts
type ProofResult =
  | { kind: "proved"; bound?: ErrorBound; evidence: ArtifactRef }
  | { kind: "refuted"; counterexample: ArtifactRef }
  | { kind: "inconclusive"; unresolved: ArtifactRef; reason: string }
  | { kind: "not-checked"; reason: string };
```

## Chapter 7

**Exercise 3.** A timer started before `compiled()` and checked afterward cannot interrupt an infinite loop. Enforcement requires an external agent that can terminate the worker or process while the script is running.

**Exercise 4.** A synchronous `withTool` restores the old tool immediately after the callback returns a promise, not after the promise completes. Any code after `await` observes the restored context. Either reject promises, await them, or make context explicit.

## Chapter 8

**Exercise 1.** Source span belongs to Authoring AST and provenance; scallop tolerance to Intent IR; tool-center curve to Toolpath IR; G17 plane to Controller IR; decimal formatting to serialization; upload filename to deployment metadata.

**Exercise 6.** A universal operation list permits unsupported combinations and forces every pass to switch on unvalidated strings. Multi-level IRs establish legality and allow each pass to consume a smaller, stronger language.

## Chapter 9

**Exercise 1.** Exact segment-list concatenation is associative because list concatenation is associative and the start of the result is the first start while the end is the last end. Definedness requires all adjacent endpoint equalities.

**Exercise 6.** Let $x=0$, $y=0.75\varepsilon$, and $z=1.5\varepsilon$. Then $|x-y|<\varepsilon$ and $|y-z|<\varepsilon$, but $|x-z|>\varepsilon$.

## Chapter 10

**Exercise 1.** `pure(a)` returns success with value `a` and unchanged state. `bind(ma,f)` runs `ma`; on failure it propagates the error; on success it passes the returned value to `f` and threads the returned state.

**Exercise 4.** Typestate cannot prove that the physical spindle actually reached the requested RPM, that the correct tool is loaded, or that the live controller state matches the host model. These are runtime and physical assumptions.

## Chapter 11

**Exercise 2.** Duplicating `%s1` allows two commands to claim they both start from the same machine state and produce incompatible futures. A real machine cannot execute both histories independently. The token models a linear chronology.

**Exercise 5.** Two cuts in disjoint regions may still fail to commute if the first releases a thin wall, changes workpiece support, or clears a link needed by the second.

## Chapter 12

**Exercise 1.** A canonical float encoding can prohibit NaN and infinities, normalize `-0` to `0`, use shortest round-trip decimal form, and specify exact exponent rules. Binary arrays can instead hash IEEE 754 bytes with fixed endianness.

**Exercise 5.** If the machine profile changes, claims depending on travel, arc capability, feed limits, WCS semantics, or controller dialect become stale. Hash dependencies cause automatic invalidation.

## Chapter 13

**Exercise 4.** A raw block that cannot be parsed should invalidate modal, motion, and process-state analyses it might affect. Production policy can reject the job; a lower policy can retain it as `unknown` with explicit operator assumption.

**Exercise 6.** Useful laws include deterministic compilation, path identity, frame inverse, serialization round trip, monotonic certificate invalidation, and strategy output stability under translation of the entire setup.

## Chapter 14

**Exercise 1.** Reversal is legal when the reversed path has the same geometric image, the operation is reversible, direction-dependent process constraints are preserved, entry/exit semantics are rebuilt, and all links remain safe. The relation is bounded geometric equivalence plus process-state refinement.

**Exercise 3.** A checker may reject a valid candidate because its purpose is sound acceptance, not maximal acceptance. Incompleteness is acceptable when unsupported evidence causes rejection rather than unsafe approval.

## Chapter 15

**Exercise 2.** Correct units do not reject `NaN mm`, `-3 mm` tool diameter, or `0 mm/min` feed. Domain predicates are required.

**Exercise 5.** A polygon normal form can require an outer ring with positive orientation, holes with negative orientation, no repeated final vertex in storage, exact closure metadata, and canonical start vertices selected lexicographically.

## Chapter 16

**Exercise 2.** Heights at discrete XY samples leave the surface between samples unconstrained. A narrow target ridge or tool contact peak may lie between samples. A continuous no-gouge result needs an interpolation/enclosure theorem or adaptive bounds.

**Exercise 6.** For guaranteed removal, use the smallest possible cutter radius because it yields the smallest guaranteed sweep. For no-gouge, use the largest possible radius because it yields the largest possible sweep.

## Chapter 17

**Exercise 1.** A link checked against final stock can cross material that has not yet been removed at the time the link executes. The certificate must reference the before-stock artifact.

**Exercise 3.** In 2D, for circular tool radius $r$, expand each obstacle by a disk $B_r$. The tool center must avoid $O\oplus B_r$.

## Chapter 18

**Exercise 2.** Either emit work coordinates plus an explicit WCS selection and validate controller offset semantics, or pretransform to machine coordinates and use machine-coordinate motion. Emitting transformed coordinates while also selecting the WCS applies the offset twice.

**Exercise 5.** Unsupported means the target cannot perform the action. Unmodeled means it may perform it but the compiler lacks semantics. Unverifiable means semantics exist but available evidence cannot establish the requested claim.

## Chapter 19

**Exercise 2.** Under initial G90, `X10` is an absolute target. Under G91, it is an increment. A block without an explicit distance mode therefore has different meanings.

**Exercise 4.** Unparsed raw text should set potentially affected modal fields to unknown. Later explicit words can re-establish known values; dependent motion before re-establishment is rejected.

## Chapter 20

**Exercise 1.** Four decimal places in millimeters give scalar rounding at most $0.00005$ mm. A three-coordinate Euclidean bound is $\sqrt{3}\times0.00005\approx0.0000866$ mm, before interpolation effects.

**Exercise 3.** Parse equality only shows that bytes form the expected syntax tree. Semantic equality additionally checks modal initial state, execution order, interpolation, and dialect behavior.

## Chapter 21

**Exercise 1.** A zero-length move can be removed only if it has no observable process event, exact-stop semantics, timing effect, probe action, or state transition. Its provenance should remain available for diagnostics if removal changes source mapping.

**Exercise 3.** A weighted penalty permits tradeoff against violation. A hard constraint excludes every unsafe candidate regardless of objective improvement.

## Chapter 22

**Exercise 1.** One spindle-start triple is:

$$
\{\operatorname{ToolLoaded}\land rpm\in R_{machine}\land\neg Alarm\}
\operatorname{StartSpindle}(rpm)
\{\operatorname{SpindleCommanded}(rpm)\}.
$$

A physical-speed postcondition additionally assumes a functioning spindle and feedback model.

**Exercise 6.** Partial correctness says that if abort terminates, the terminal state is stopped or alarmed. Total correctness also requires abort eventually terminate under stated communication and controller fairness assumptions.

## Chapter 23

**Exercise 1.** For interval $[a,b]$, $\gamma([a,b])=\{x\in\mathbb{R}\mid a\le x\le b\}$. The top interval maps to all reals.

**Exercise 4.** An unknown raw command conservatively maps position, feed, spindle, WCS, and motion mode to unknown unless a parser proves narrower effects.

## Chapter 24

**Exercise 2.** “Do segments intersect?” is a predicate with a discrete answer. “Where is the intersection point?” is a construction. A small predicate error can change topology; a small construction error often changes only coordinates.

**Exercise 7.** Exact arithmetic proves facts about the mathematical input model. It does not prove that the mesh matches the CAD surface, the tool matches its nominal diameter, or the fixture matches the model.

## Chapter 25

**Exercise 1.** Let $W_c^+$ be outer cutting sweep, $W_a^+$ outer assembly sweep, and $W_c^-$ inner cutting sweep. Then no-gouge is $W_c^+\cap P=\varnothing$; fixture safety is $W_a^+\cap O=\varnothing$; required removal is $R_{req}\subseteq W_c^-$.

**Exercise 3.** A spatial grid may bound stock occupancy but not temporal sampling along motion. Tool and holder checks also have different geometry. One scalar “resolution” does not characterize all approximation errors.

## Chapter 26

**Exercise 2.** At radius $r$, small angular uncertainty $\delta\theta$ contributes approximately $r\delta\theta$. At $50$ mm and $0.0002$ rad, the contribution is $0.010$ mm.

**Exercise 3.** Root-sum-square is a statistical model requiring independence or known covariance. It is not a deterministic maximum bound when errors can align.

## Chapter 27

**Exercise 1.** A travel claim names the final interpreted motion artifact, machine-profile hash, WCS uncertainty set, and admissible configuration set, asserting that every pose enclosure lies inside the travel set.

**Exercise 3.** A signature proves that a key signed bytes. It does not show that the signer performed the advertised geometric check or that the proposition is true.

## Chapter 28

**Exercise 2.** If planner and checker both call the same `endpointKey` function, a collision in that function can cause both to agree on a wrong topology. A tuple-key or grid-edge reference checker provides stronger independence.

**Exercise 5.** If pass 1 has error $\varepsilon_1$ and pass 2 is $L$-Lipschitz with local error $\varepsilon_2$, composition has bound $L\varepsilon_1+\varepsilon_2$ under compatible metrics.

## Chapter 29

**Exercise 3.** Preflight reads idle/homed state, releases authority, and a second client starts a job before the first sends motion. The first command is now admitted under stale state. A lock plus state epoch binds the check to execution.

**Exercise 4.** Timeout successors include “not received,” “received but not executed,” “executed and reply lost,” and “executing.” The session remains quarantined until status and framing are re-established.

## Chapter 30

**Exercise 2.** Upload success can mean only that bytes were transferred. Exact-byte execution additionally requires a stored content hash, selected-job identity, start acknowledgement, and monitoring of that execution instance.

**Exercise 3.** At $v=100$ mm/s and $a=500$ mm/s$^2$, ideal braking distance is $10$ mm. With 80 ms total latency, add at least $8$ mm of travel, for 18 mm before further margin.

## Chapter 31

**Exercise 2.** A penalty cannot express categorical prohibition because objective terms trade off. A collision constraint removes the candidate from $\mathcal{F}$.

**Exercise 4.** Solve a relaxed route, run the continuous collision checker, add a forbidden-edge or clearance constraint from the counterexample, and repeat until a feasible candidate or infeasibility proof is obtained.

## Chapter 32

**Exercise 2.** Build a map from operation to schedule index, then verify every precedence edge $(a,b)$ satisfies `pos[a] < pos[b]`. Also reject duplicates and missing operations.

**Exercise 5.** Removing stock in an earlier operation can open a low link. A static matrix computed against initial stock overestimates cost; one computed against final stock may be unsafe.

## Chapter 33

**Exercise 3.** A grid path proves only occupancy at the chosen discretization. Smoothing can leave cells, diagonal movement can cut blocked corners, and obstacles may be under-resolved. Continuous outer-enclosure validation remains necessary.

**Exercise 5.** A polyline with a 90-degree corner is collision-free but requires infinite acceleration at nonzero speed under an ideal point-mass model. It needs a stop, blend, or rounded geometry.

## Chapter 34

**Exercise 1.** By the chain rule, $\dot q=q'(s)\dot s$. Differentiating again gives $\ddot q=q''(s)\dot s^2+q'(s)\ddot s$.

**Exercise 3.** A polynomial or spline speed between knots can exceed endpoint values. Constraint bounds must cover the entire interval using analytic extrema, convex hull properties, or interval evaluation.

## Chapter 35

**Exercise 1.** If nominal machine X path is $[20,180]$ and WCS translation uncertainty is $[-0.3,0.3]$, robust travel requires $[19.7,180.3]$ lie inside machine travel. The constraint quantifies over every allowed offset.

**Exercise 4.** Candidate A: 10 s and 0.5 mm clearance. Candidate B: 11 s and 2 mm clearance. Neither dominates the other; both lie on the Pareto frontier.

## Chapter 36

**Exercise 2.** Risks include reusing the producer's geometry predicate, importing producer normalization that discards a counterexample, and sharing a mutable artifact cache. Shared semantic types are acceptable; shared decision logic reduces independence.

**Exercise 5.** Put orchestration in a headless compile service that consumes artifact references. Studio and CLI provide adapters for source loading, progress, and presentation but receive the same response graph.

## Chapter 37

**Exercise 2.** Exact claims include schema validity and hash equality. Bounded claims include geometric path deviation and travel under transform intervals. Assumptions include physical tool dimensions and fixture identity. Runtime checks include homing, WCS, live tool, and stored hash.

**Exercise 6.** Changing a material-library default, machine profile, tool measurement, fixture model, strategy version, or WCS can invalidate the bundle without editing source.

## Chapter 38

**Exercise 2.** Translate stock, target, fixtures, frames, and machine envelope by vector $v$. The output paths should translate by $v$; operation order and relative distances should remain unchanged; certificate propositions should reference transformed artifacts with equal margins.

**Exercise 5.** Mutate one dependency at a time and assert rejection: job byte, tool hash, WCS interval, claim target, evidence type, pass version, or checker identity. Include cross-claim evidence swaps.

## Chapter 39

**Exercise 1.** The four false propositions are: target gouge was bounded; script authority was limited and time-bounded; the generic path carried no motion effect; and quantized endpoint identity was unique inside the machine envelope.

**Exercise 4.** A nested map `Map<qx, Map<qy, bucket>>` is injective for integer pairs because equality requires both integers equal. Range proofs are then needed only for quantization overflow, not modulo aliasing.

## Chapter 40

**Exercise 3.** High-value first claims are final-byte parse-back, machine travel under explicit frames, and exact job-hash execution. They close major cross-boundary gaps and can be implemented before full volumetric verification.

**Exercise 5.** Optimization is last because it increases transformation complexity and search space. Reliable feasibility and evidence checking must exist before faster or shorter candidates are trusted.

# Glossary

This glossary uses the meanings intended throughout the book. Several terms have broader meanings in compilers, formal methods, computational geometry, or manufacturing; the definitions below identify the interpretation relevant to a certificate-carrying CAM system.

**Abstract domain.** A mathematical domain whose elements conservatively represent sets of concrete program or machine states. Examples include intervals, axis-aligned boxes, finite sets of modal states, and symbolic frame relations.

**Abstract interpretation.** A framework for computing sound approximations of program behavior by interpreting a program over an abstract domain rather than enumerating concrete executions.

**Abstraction function.** A mapping from detailed physical or controller traces to the observations relevant at a higher semantic level, such as final stock, protected-surface penetration, or feature dimensions.

**Acceptance gate.** A machine-enforced condition that an artifact must satisfy before it can advance to a later lifecycle stage, such as preview, air cut, attended cutting, or production execution.

**Acyclic dependency graph.** A directed graph with no cycles. Certificate dependencies should normally form such a graph so that artifacts and claims can be checked in a finite topological order.

**Admissible set.** The subset of states, configurations, paths, or schedules satisfying all hard constraints.

**Affine transform.** A transform consisting of a linear map and a translation. Rigid frame transforms are the special case preserving distances and orientation or reflection, depending on the determinant.

**Alarm state.** A controller or machine state in which ordinary execution is blocked or modified because a fault, interlock, or exceptional condition has been detected.

**Alias collision.** Two distinct semantic objects receiving the same identifier or lookup key. In geometry this can merge unrelated endpoints, contours, cells, or topology components.

**Artifact.** An immutable, content-addressed input or output of a compiler stage: source, AST, IR, mesh, tool model, machine profile, controller program, serialized bytes, evidence, or certificate.

**Artifact identity.** The stable identity of an artifact, normally a cryptographic content hash plus a schema or media type. A filename or in-memory object address is not sufficient.

**Assertion.** A proposition intended to hold at one program point, controller state, geometric stage, or runtime checkpoint.

**Assumption.** An external fact required by a proof but not established by that proof. Tool measurement, machine calibration, fixture identity, controller conformance, and work-coordinate registration are typical assumptions.

**Assumption discharge.** The act of replacing an assumption with evidence or a runtime check that establishes it for a specific execution.

**Attestation.** Signed evidence about provenance, identity, configuration, or execution. Attestation authenticates a statement; it does not by itself establish the statement's mathematical truth.

**Authorization epoch.** A monotonically changing identifier binding an authorization decision to the machine state on which it was based. It prevents stale preflight results from authorizing later, changed states.

**Backend.** The portion of a compiler that lowers machine-independent operations to a target machine, controller dialect, serialization, or transport protocol.

**Bounded refinement.** A refinement relation that permits a quantified deviation under a named metric, such as Hausdorff distance, normal-direction surface error, or timing error.

**Canonical command.** A machine-oriented action with explicit machining meaning but without target-controller syntax or accidental modal dependence.

**Certificate.** A machine-checkable package binding claims, artifact identities, assumptions, evidence, dependency claims, checker identities, and quantitative bounds.

**Certificate checker.** A comparatively small program that validates evidence and decides whether a certificate claim follows for the named artifact under the named assumptions.

**Certificate DAG.** The dependency graph connecting source artifacts, transformed artifacts, claims, evidence, runtime facts, and final execution authorization.

**Certified artifact.** An artifact accompanied by one or more successfully checked claims. Certification is property-specific; it does not mean that every desirable property has been proved.

**Checker independence.** The degree to which a checker avoids sharing the producer's algorithms, data normalizations, hidden state, and defect modes. Independent implementation is often more valuable than nominal modular separation.

**Claim.** A precise proposition about a precise subject artifact, such as a travel-envelope inclusion or a maximum target-penetration bound.

**Clearance.** A distance or separation condition between the tool assembly and stock, target, fixtures, machine structures, or forbidden configuration-space regions.

**Closed-world command language.** A command language in which every permitted operation is explicitly enumerated and unknown operations are rejected. This is preferred for machine-control authorization.

**Compiler pass.** A transformation or analysis from one IR stage to another, ideally accompanied by an explicit semantic relation and a checker or proof obligation.

**Concrete semantics.** The detailed semantics of actual states and transitions, as opposed to an abstract analysis that represents sets of them.

**Configuration space.** A space whose points represent complete machine configurations. Collision of a moving solid can be transformed into point avoidance in an expanded forbidden region of configuration space.

**Conformance.** Satisfaction of a specification, standard, target intent, controller dialect, or certificate proposition.

**Conservative approximation.** An approximation oriented so that a successful check implies the desired property. Collision checks use outer obstacle and sweep enclosures; guaranteed-removal checks use inner removal enclosures.

**Constraint.** A hard condition defining feasibility. A safety constraint must not be converted into a soft objective penalty unless the resulting violations are categorically rejected later.

**Content-addressing.** Naming an artifact by a digest of its exact bytes and relevant encoding metadata, making changes observable and dependency invalidation mechanical.

**Controller dialect.** The syntax and operational interpretation implemented by a particular controller and firmware profile, including modal groups, commands, extensions, numeric ranges, and protocol behavior.

**Controller IR.** A structured representation of controller-level operations after machine lowering but before textual serialization.

**Controller semantics profile.** A versioned, content-addressed description of how a target firmware interprets commands, modes, uploads, acknowledgements, and lifecycle operations.

**Counterexample.** A concrete input, state, trace, geometry, or schedule showing that a claimed invariant or transformation relation is false.

**Cutting sweep.** The swept volume of the material-removing portion of the tool along a trajectory.

**Cyber-physical compiler.** A compiler whose target semantics includes physical mechanisms, continuous dynamics, sensors, actuators, material state, faults, and communication rather than only abstract machine instructions.

**Denotation.** The mathematical meaning assigned to a syntax element or IR object. A manufacturing operation often denotes a set of acceptable outcomes rather than one path.

**Denotational semantics.** A compositional mapping from programs or operations to mathematical objects such as functions, relations, traces, or sets of acceptable workpiece states.

**Dexel.** A depth element representing intervals of material along a ray. A triple-dexel model uses three orthogonal ray families.

**Diagnostic.** A structured explanation of an error, warning, unproved obligation, assumption, or source-to-output provenance relationship.

**Dialect conversion.** A checked transformation from one IR dialect or abstraction level to another under explicit legality and semantic-preservation rules.

**Dimensional type.** A type carrying physical dimension, such as length, angle, speed, acceleration, or spindle rate, so dimensionally invalid operations are rejected.

**Dijkstra monad.** A specification-indexed computational abstraction that associates effectful computations with predicate transformers or Hoare-style contracts.

**Discretization.** Replacement of a continuous object by finite samples, cells, segments, time steps, or basis coefficients. A discretization parameter alone is not a proof of continuous-domain error.

**Effect summary.** A conservative description of the state, resources, stock regions, probe values, frames, or modalities read and written by an operation.

**Effect system.** A static system that records and constrains computational or machine effects in addition to ordinary value types.

**Elaboration.** The pass that resolves names, defaults, units, frames, tools, parameters, and syntactic sugar into an explicit, typed representation.

**Enclosure.** A set guaranteed to contain an exact but potentially unknown quantity or geometry. Intervals and conservative swept volumes are enclosures.

**End-to-end theorem.** A statement relating checked source intent and assumptions to all permitted final physical executions, composed across every compiler, controller, and runtime boundary.

**Evidence.** Data consumed by a checker to establish a claim: proof terms, interval bounds, abstract states, parse-back traces, separating axes, spatial covers, solver certificates, or exhaustive state tables.

**Exact claim.** A claim established without an approximation tolerance relative to the stated mathematical input model. It can still depend on assumptions connecting the model to reality.

**Execution instance.** One uniquely identified controller run of one stored job under one machine-state epoch. A filename does not uniquely identify an execution instance.

**Feasible set.** The set of candidates satisfying all hard constraints. Optimization should search within this set rather than trade safety against cost.

**Final-byte validation.** Re-parsing and interpreting the exact serialized bytes that will be uploaded, then checking equivalence or refinement against the certified controller IR.

**Frame.** A coordinate system with an identity and transform relationships. Coordinates without frames are incomplete semantic values.

**Frame graph.** A graph of named coordinate frames and transforms, possibly with interval-valued uncertainty and time-varying measurements.

**Free-space link.** A non-cutting connection between machining segments whose tool-and-holder sweep is certified to avoid current stock, fixtures, protected geometry, and forbidden machine regions.

**G-code block.** One controller input record containing words evaluated under modal and dialect-specific semantics. Textual order inside a block does not necessarily imply sequential execution.

**Gouge.** Material removal beyond the allowed target or allowance region. A gouge claim requires a target or protected-material model.

**Hash binding.** Inclusion of an artifact hash in a claim, protocol step, authorization, or signature so the statement cannot silently transfer to different bytes.

**Hausdorff distance.** A metric measuring the greatest nearest-point deviation between two sets. It is useful for path approximation but does not alone encode orientation, process, or topology preservation.

**Height field.** A surface representation with one height per planar location. It is efficient for three-axis material models but cannot represent arbitrary undercuts or multiple layers.

**Hoare triple.** A contract of the form $\{P\}\;c\;\{Q\}$ stating that command $c$, when started in a state satisfying $P$, establishes $Q$ if it terminates.

**Hybrid system.** A system combining discrete mode transitions with continuous state evolution, such as controller states plus machine position, velocity, and braking dynamics.

**Identity morphism.** In a path category, the zero-motion path at a pose. It acts as the neutral element for path composition under the chosen equality notion.

**Information order.** A partial order describing precision of abstract values, often written $a\sqsubseteq b$ when $b$ contains at least as much uncertainty or information according to the selected convention.

**Inner approximation.** A set guaranteed to lie inside the true set. Inner removal approximations support claims that material was definitely removed.

**Intent IR.** A representation of manufacturing features, working steps, allowances, tolerances, resources, and dependencies before a specific tool-center path is selected.

**Interlock.** A condition preventing or terminating an operation when required safety or process state is absent.

**Interval arithmetic.** Arithmetic on closed intervals with outward rounding so the exact real-valued result remains enclosed.

**Invariant.** A property true initially and preserved by every relevant transition or compiler step.

**IR legality.** The syntactic, typing, capability, and semantic conditions an artifact must satisfy at a given intermediate representation level.

**Job bundle.** The complete execution package: exact program bytes, machine and firmware profiles, tool/holder models, stock/target/fixture artifacts, frame data, assumptions, certificates, and metadata.

**Kleisli composition.** Composition of effectful functions through a monad or indexed effect abstraction rather than ordinary function composition.

**Language sandbox.** An execution environment intended to restrict a macro or scripting language. A same-realm wrapper that retains access to host globals is not a security boundary.

**Lattice.** A partially ordered set in which every pair has a least upper bound and greatest lower bound. Many abstract domains use lattices to merge control-flow information and compute fixed points.

**Legality checker.** A checker deciding whether an IR contains only operations, types, frames, units, and capabilities permitted at that level.

**Lipschitz bound.** A constant $L$ satisfying $d(f(x),f(y))\le Ld(x,y)$. It describes how input uncertainty or approximation can be amplified by a transformation.

**Liveness property.** A temporal property stating that some desired event eventually occurs, such as an abort eventually reaching a stopped or faulted state.

**Lowering.** Refinement from a higher-level IR to a more concrete IR by selecting machine, controller, geometry, or serialization details.

**Machine envelope.** The admissible set of axis configurations or tool poses under travel, soft-limit, fixture, and machine-structure constraints.

**Machine IR.** A representation after target-machine capabilities, frames, kinematics, limits, and trajectories have been made explicit but before controller syntax is serialized.

**Machine profile.** A versioned artifact describing kinematics, axis limits, rates, acceleration, jerk, spindle and tool capabilities, controller dialect, and other target constraints.

**Macro language.** A language executed at compile time to construct an inert AST or plan. It should not retain arbitrary executable closures inside trusted compiler passes.

**Material-removal semantics.** A semantics in which cutting commands transform stock solids, typically by set difference with a cutting sweep.

**Metric.** A distance function satisfying non-negativity, identity, symmetry, and triangle inequality. Approximation claims must name the metric under which their bounds hold.

**Modal state.** Controller state that persists across blocks until replaced, such as motion mode, units, plane, feed, spindle speed, or work offset.

**Modal compression.** Omission of redundant modal words during serialization. It is correct only if interpreted traces remain equivalent under the specified initial state and dialect.

**Model checking.** Exhaustive or symbolic exploration of a finite or finitely abstracted transition system to establish temporal properties or find counterexamples.

**Monad.** A compositional abstraction for computations with effects. For CAM, state, failure, nondeterminism, logging, and external interaction are relevant effects.

**Monotone analysis.** An analysis whose transfer functions preserve the abstract-domain order, enabling fixed-point computation and sound iteration.

**Nondeterminism.** Multiple possible successor states or traces arising from underspecified intent, sensor uncertainty, communication outcomes, faults, or environmental variation.

**Numerical kernel.** The small collection of arithmetic, predicates, interval operations, and geometric primitives trusted by certificate checkers.

**Objective.** A quantity minimized or maximized among feasible candidates, such as cycle time, rapid distance, tool changes, energy, or predicted wear.

**Operational semantics.** Rules describing how a configuration changes step by step as commands execute.

**Operations research.** Mathematical modeling and optimization of decisions such as operation sequencing, tool assignment, linking, and feed scheduling under constraints.

**Outer approximation.** A set guaranteed to contain the true set. Outer sweeps and obstacles support collision-absence and no-gouge claims.

**Parse-back validation.** Parsing emitted controller bytes back into structured IR and comparing their interpreted semantics with the pre-serialization artifact.

**Partial correctness.** A guarantee that the postcondition holds if execution terminates. It does not prove termination or eventual progress.

**Pass contract.** A specification of a pass's accepted input, produced output, semantic relation, error bound, assumptions, diagnostics, witness, and checker.

**Path.** A parameterized geometric curve through a frame. It does not by itself define timing, controller interpolation, or material-removal process.

**Path equivalence.** The chosen relation under which two path values are considered semantically equal, often equality modulo monotone reparameterization and a stated geometric tolerance.

**Path parameterization.** A monotone function mapping time to geometric path progress. It determines velocity, acceleration, jerk, and cycle time along a fixed path.

**Planner.** A generally complex and heuristic producer that chooses a toolpath, schedule, or process implementation satisfying an intent specification.

**Postcondition.** A proposition promised after an operation terminates from a state satisfying its precondition.

**Postprocessor.** A target-specific compiler backend lowering machine or canonical IR into a controller dialect and exact serialized job bytes.

**Precondition.** A proposition that must hold before an operation may execute or a theorem may be applied.

**Predicate transformer.** A function mapping desired postconditions backward to sufficient preconditions. Weakest-precondition semantics is a principal example.

**Process model.** A model of cutting, probing, spindle, stock, tool engagement, or machine dynamics used to interpret and check operations.

**Proof obligation.** A proposition that must be established before a pass result, job bundle, or runtime action can be accepted.

**Proof-producing analysis.** An analyzer that emits evidence allowing a smaller checker to validate its result rather than requiring the analyzer itself to be trusted.

**Protected material.** Target or fixture material that a claim forbids the cutting sweep from entering beyond a stated tolerance.

**Provenance.** Structured information linking output objects and diagnostics to source spans, compiler passes, parameters, input artifacts, and tool versions.

**Quantization.** Mapping continuous or high-precision values to discrete integer bins. Quantization can be useful, but a lossy packed key must not be mistaken for unique topology identity.

**Rapid safety.** A claim that a non-cutting motion's tool-and-holder sweep avoids current stock and obstacles under controller rapid semantics and machine uncertainty.

**Raw command.** An escape hatch containing target syntax whose effects have not been derived from a trusted parser. Conservative analyses must reject it or set affected abstract state to unknown.

**Reachability.** The set of states obtainable from an initial state under the transition relation and assumptions.

**Reference semantics.** A simple, explicit semantic implementation used as the standard against which optimized or target-specific implementations are compared.

**Refinement.** A relation in which a concrete implementation removes choices or adds detail without introducing behavior forbidden by the abstract specification.

**Refinement mapping.** A mapping from concrete states and traces to abstract states and traces used to demonstrate that one system implements another.

**Representation invariant.** A property ensuring an in-memory value is internally coherent, such as a path endpoint matching its last segment. It is narrower than a machining-safety claim.

**Residual stock.** Material remaining after the modeled removal operations. Conservative residual stock usually requires outer stock and inner removal approximations.

**Robust predicate.** A predicate whose result is correct for the mathematical input model despite floating-point degeneracy, normally through filtered, adaptive, exact, or interval methods.

**Runtime assurance.** A small trusted mechanism that monitors an advanced component or physical system and intervenes before a safety property can be violated.

**Safety property.** A temporal property stating that a bad event never occurs. A finite violation has a counterexample prefix.

**Semantic preservation.** Equality, refinement, or bounded correspondence between the meanings of a pass input and output.

**Semantic waist.** A compact intermediate language separating many high-level producers from many low-level targets while retaining the physical distinctions needed for correctness.

**Serialization.** Conversion of structured controller IR to exact bytes, including number formatting, line endings, comments, checksums, and encoding.

**Signature.** A cryptographic authentication of bytes or statements. A signature establishes origin and integrity under a key-management assumption, not semantic correctness.

**Simulation-only result.** Evidence from one or more concrete executions or samples without a theorem covering all relevant states or the continuous domain.

**Small-step semantics.** An operational semantics in which each rule performs one local transition, making interleavings, faults, and protocol states explicit.

**Soundness.** The property that every fact reported as established is true of all represented concrete behaviors under the stated assumptions. A sound analysis may conservatively reject safe programs.

**Source map.** A mapping from generated IR nodes, commands, and diagnostics back to source syntax and macro-expansion provenance.

**SSA state token.** A single-assignment value consumed and produced by state-changing IR operations, making effect order and data dependencies explicit.

**Staged programming.** Execution of one program phase to construct code or data for a later phase. The phase boundary should remove ambient authority and retain only inert, validated artifacts.

**Stock monotonicity.** The ideal subtractive-process invariant $S_{i+1}\subseteq S_i$. It excludes material addition but does not by itself establish correct removal.

**Swept volume.** The union of all poses of a solid along a trajectory. Different claims require the cutting tool sweep or the complete tool-and-holder assembly sweep.

**Target surface.** The desired final boundary or protected part geometry against which gouge, allowance, and residual-material claims are stated.

**Temporal logic.** A logic with operators over traces, such as always $\Box$, eventually $\Diamond$, and next, used for controller safety and liveness properties.

**Time-optimal path parameterization.** Selection of progress $s(t)$ along a fixed geometric path to minimize time while satisfying velocity, acceleration, torque, jerk, tracking, and process constraints.

**Total correctness.** Partial correctness plus termination or liveness under stated assumptions.

**Trace.** A finite or infinite sequence of states and observable events representing one system execution.

**Trace refinement.** Inclusion of concrete traces, after abstraction, in the set allowed by an abstract program.

**Trajectory.** A time-indexed pose or configuration function. A path becomes a trajectory only after time parameterization.

**Translation validation.** Independent checking that one actual pass output correctly refines its actual input, instead of proving the transformer correct for all inputs.

**Trusted computing base.** The code, semantics, numeric primitives, key material, and assumptions whose correctness must be trusted for the assurance argument to hold.

**Typestate.** Static representation of protocol state in types so only operations valid in the current state can be expressed.

**Uncertainty set.** A set of possible values for a physical or numerical quantity, such as a transform interval, tool-radius interval, or following-error bound.

**Validation.** Checking an artifact against a relation, policy, or specification. Validation should state exactly what was checked and by what method.

**Verification.** Establishment of a formal or mathematically justified claim. In this book the term is reserved for claims with explicit propositions, assumptions, and evidence rather than visual inspection alone.

**Weakest precondition.** The least restrictive precondition sufficient to ensure a desired postcondition after execution of a command.

**Witness.** Producer-supplied data demonstrating a construction or optimization choice, such as a path decomposition, correspondence, abstract invariant, separating plane, or schedule assignment.

**Work coordinate system.** A frame relating part-program coordinates to machine coordinates. Its identity and uncertainty are runtime-critical inputs to travel and collision claims.

# Guided Reading and Project Tracks

The chapters are intentionally cross-disciplinary. This appendix gives compact routes through the material for different implementation goals.

## Compiler and language track

Read Chapters 1, 2, 7-15, 18-20, 27, 28, 36, 37, and 40. Implement the inert plan AST, the multi-level IR ladder, pass contracts, content-addressed artifacts, and parse-back validation before adding advanced planning strategies. The central external readings are multi-stage programming [R37], MLIR [R16], SSA [R15], CompCert [R17], translation validation [R18, R19], and NIST's canonical machining interface [R1, R2].

## Static-analysis and formal-methods track

Read Chapters 3, 5, 6, 10, 11, 14, and 22-30. Begin with Hoare logic and weakest preconditions [R4, R5], structural operational semantics [R6], abstract interpretation [R7], refinement mappings [R9], temporal logic [R8, R34], and proof-carrying code [R20, R21]. Parameterized effects [R12-R14] and Dijkstra monads [R39] provide a route from API typing to machine-checkable contracts.

## Robust geometry and verification track

Read Chapters 3, 4, 9, 16, 24-28, 33, and 37. Build exact or adaptive topology predicates before accelerating constructions [R22]. Use interval enclosures [R23, R24], configuration-space reasoning [R25], conservative swept-volume techniques [R26], and representations such as triple dexels [R27, R28]. Keep target protection, fixture clearance, and guaranteed removal as separate propositions.

## Controller and runtime track

Read Chapters 1, 5, 18-20, 22, 23, 29, 30, 37, and 39. Implement a closed command grammar, explicit modal interpreter, protocol state machine, state epochs, hash-bound upload/start operations, and abort recovery. NIST's interpreters and canonical commands provide the machining semantics foundation [R1, R2]. TLA-style specification [R8, R34], hybrid systems [R35], and runtime assurance [R36] cover the protocol and physical-monitoring boundary.

## Planning and optimization track

Read Chapters 2-4, 6, 9, 16, 17, and Part V. Treat every optimizer as an untrusted producer of candidates inside a separately checked feasible set. Relevant foundations include configuration spaces [R25], fast marching and geodesics [R29, R30], precedence-constrained routing [R31], and constrained feed scheduling [R32, R33].

## Manufacturing-information track

Read Chapters 1, 2, 7, 8, 12, 13, 16, 18, 27, and 37. Compare the semantic-waist architecture with STEP-NC's feature and working-step model [R3, R42, R43]. Conformance testing is as important as schema design; Barnard Feeney and Frechette provide a manufacturing-specific testing perspective [R40].

## A twelve-week implementation course

| Week | Reading | Laboratory |
|---:|---|---|
| 1 | Chapters 1-2 | Define one pocket intent and three acceptable implementations. |
| 2 | Chapters 3-4 | Implement dimensional types and a checked frame graph. |
| 3 | Chapters 5-6 | Write denotational and small-step semantics for five canonical commands. |
| 4 | Chapters 7-9 | Build an isolated macro-to-AST boundary and path algebra. |
| 5 | Chapters 10-13 | Add effects, machine-state tokens, provenance, and extensible operation schemas. |
| 6 | Chapters 14-15 | Implement pass manifests and one translation validator. |
| 7 | Chapters 16-20 | Lower a pocket to controller IR and validate emitted bytes by parse-back. |
| 8 | Chapters 22-23 | Implement weakest-precondition rules and an interval/modal abstract interpreter. |
| 9 | Chapters 24-26 | Add robust predicates, interval transforms, and typed error budgets. |
| 10 | Chapters 27-30 | Build the certificate DAG, protocol model, and runtime preflight handshake. |
| 11 | Chapters 31-35 | Add precedence-aware sequencing and a checked free-space linker. |
| 12 | Chapters 36-40 | Integrate the headless compiler, checker process, CLI, and Z1 dry-run workflow. |

## Research directions

The architecture leaves several substantive research problems open:

1. A compositional specification language for machining features whose denotation covers tolerance zones, surface texture, process constraints, and intermediate stock support.
2. Efficient conservative swept-volume bounds for arbitrary tool assemblies and spline trajectories under uncertain transforms.
3. Proof-producing adaptive stock representations that combine dexel speed with local volumetric refinement.
4. Translation validators for geometry algorithms that emit compact correspondence or separation witnesses.
5. Robust scheduling with stock-dependent transition costs and structural-support constraints.
6. Controller semantics learned from traces but converted into explicit, reviewable, versioned profiles.
7. Small proof formats for geometric certificates; compact proof representation and checking remain important engineering concerns [R41].
8. Runtime monitors that combine discrete protocol assurance with bounded stopping dynamics and sensor uncertainty.

\backmatter

# References {-}

\markboth{References}{References}

The bracketed identifiers in the text refer to the entries below. DOI links name the version of record when available; institutional pages are used for standards and technical reports.

**[R1]** Thomas R. Kramer, Frederick M. Proctor, and Elena R. Messina. *The NIST RS274/NGC Interpreter, Version 3*. NISTIR 6556, National Institute of Standards and Technology, 2000. <https://www.nist.gov/publications/nist-rs274ngc-interpreter-version-3>.

**[R2]** Frederick M. Proctor, Thomas R. Kramer, and John L. Michaloski. *Canonical Machining Commands*. NISTIR 5970, National Institute of Standards and Technology, 1997. <https://doi.org/10.6028/NIST.IR.5970>.

**[R3]** ISO 14649-1. *Industrial Automation Systems and Integration -- Physical Device Control -- Data Model for Computerized Numerical Controllers -- Part 1: Overview and Fundamental Principles*. International Organization for Standardization.

**[R4]** C. A. R. Hoare. “An Axiomatic Basis for Computer Programming.” *Communications of the ACM* 12, no. 10 (1969): 576-580, 583. <https://doi.org/10.1145/363235.363259>.

**[R5]** Edsger W. Dijkstra. “Guarded Commands, Nondeterminacy and Formal Derivation of Programs.” *Communications of the ACM* 18, no. 8 (1975): 453-457. <https://doi.org/10.1145/360933.360975>.

**[R6]** Gordon D. Plotkin. “A Structural Approach to Operational Semantics.” Originally DAIMI FN-19, Aarhus University, 1981; reprinted in *Journal of Logic and Algebraic Programming* 60-61 (2004): 17-139. <https://doi.org/10.1016/j.jlap.2004.03.009>.

**[R7]** Patrick Cousot and Radhia Cousot. “Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints.” In *Proceedings of POPL 1977*, 238-252. <https://doi.org/10.1145/512950.512973>.

**[R8]** Leslie Lamport. “The Temporal Logic of Actions.” *ACM Transactions on Programming Languages and Systems* 16, no. 3 (1994): 872-923. <https://doi.org/10.1145/177492.177726>.

**[R9]** Martín Abadi and Leslie Lamport. “The Existence of Refinement Mappings.” *Theoretical Computer Science* 82, no. 2 (1991): 253-284. <https://doi.org/10.1016/0304-3975(91)90224-P>.

**[R10]** Eugenio Moggi. “Notions of Computation and Monads.” *Information and Computation* 93, no. 1 (1991): 55-92. <https://doi.org/10.1016/0890-5401(91)90052-4>.

**[R11]** Philip Wadler. “The Essence of Functional Programming.” In *Proceedings of POPL 1992*, 1-14. <https://doi.org/10.1145/143165.143169>.

**[R12]** Robert E. Strom and Shaula Yemini. “Typestate: A Programming Language Concept for Enhancing Software Reliability.” *IEEE Transactions on Software Engineering* SE-12, no. 1 (1986): 157-171. <https://doi.org/10.1109/TSE.1986.6312929>.

**[R13]** Robert Atkey. “Parameterised Notions of Computation.” *Journal of Functional Programming* 19, nos. 3-4 (2009): 335-376. <https://doi.org/10.1017/S095679680900728X>.

**[R14]** John M. Lucassen and David K. Gifford. “Polymorphic Effect Systems.” In *Proceedings of POPL 1988*, 47-57. <https://doi.org/10.1145/73560.73564>.

**[R15]** Ron Cytron, Jeanne Ferrante, Barry K. Rosen, Mark N. Wegman, and F. Kenneth Zadeck. “Efficiently Computing Static Single Assignment Form and the Control Dependence Graph.” *ACM Transactions on Programming Languages and Systems* 13, no. 4 (1991): 451-490. <https://doi.org/10.1145/115372.115320>.

**[R16]** Chris Lattner, Mehdi Amini, Uday Bondhugula, Albert Cohen, Andy Davis, Jacques Pienaar, River Riddle, Tatiana Shpeisman, Nicolas Vasilache, and Oleksandr Zinenko. “MLIR: Scaling Compiler Infrastructure for Domain Specific Computation.” In *Proceedings of CGO 2021*, 2-14. <https://doi.org/10.1109/CGO51591.2021.9370308>.

**[R17]** Xavier Leroy. “Formal Verification of a Realistic Compiler.” *Communications of the ACM* 52, no. 7 (2009): 107-115. <https://doi.org/10.1145/1538788.1538814>.

**[R18]** Amir Pnueli, Michael Siegel, and Eli Singerman. “Translation Validation.” In *Tools and Algorithms for the Construction and Analysis of Systems, TACAS 1998*, 151-166. <https://doi.org/10.1007/BFb0054170>.

**[R19]** Nuno P. Lopes, Juneyoung Lee, Chung-Kil Hur, Zhengyang Liu, and John Regehr. “Alive2: Bounded Translation Validation for LLVM.” In *Proceedings of PLDI 2021*. <https://doi.org/10.1145/3453483.3454030>.

**[R20]** George C. Necula. “Proof-Carrying Code.” In *Proceedings of POPL 1997*, 106-119. <https://doi.org/10.1145/263699.263712>.

**[R21]** Andrew W. Appel. “Foundational Proof-Carrying Code.” In *Proceedings of the 16th Annual IEEE Symposium on Logic in Computer Science*, 247-256, 2001. <https://doi.org/10.1109/LICS.2001.932501>.

**[R22]** Jonathan Richard Shewchuk. “Adaptive Precision Floating-Point Arithmetic and Fast Robust Geometric Predicates.” *Discrete & Computational Geometry* 18 (1997): 305-363. <https://doi.org/10.1007/PL00009321>.

**[R23]** IEEE. *IEEE Standard for Interval Arithmetic (Simplified)*. IEEE Std 1788.1-2017. <https://standards.ieee.org/ieee/1788.1/6074/>.

**[R24]** Ramon E. Moore, R. Baker Kearfott, and Michael J. Cloud. *Introduction to Interval Analysis*. SIAM, 2009. <https://doi.org/10.1137/1.9780898717716>.

**[R25]** Tomás Lozano-Pérez. “Spatial Planning: A Configuration Space Approach.” *IEEE Transactions on Computers* C-32, no. 2 (1983): 108-120. <https://doi.org/10.1109/TC.1983.1676196>.

**[R26]** Silvia Sellán, Noam Aigerman, and Alec Jacobson. “Swept Volumes via Spacetime Numerical Continuation.” *ACM Transactions on Graphics* 40, no. 4 (2021). <https://doi.org/10.1145/3450626.3459780>.

**[R27]** Masatomo Inui, Takashi Sakurai, and Nobuyuki Umezu. “Data Conversion Technology between Triple Dexel Model and Polygonal Model.” *Journal of the Japan Society for Precision Engineering* 76, no. 2 (2010): 226-231. <https://doi.org/10.2493/jjspe.76.226>.

**[R28]** Weihan Zhang and Ming-Chuan Leu. “Surface Reconstruction Using Dexel Data from Three Sets of Orthogonal Rays.” *Journal of Computing and Information Science in Engineering* 9, no. 1 (2009): 011008. <https://doi.org/10.1115/1.3086034>.

**[R29]** J. A. Sethian. “A Fast Marching Level Set Method for Monotonically Advancing Fronts.” *Proceedings of the National Academy of Sciences* 93, no. 4 (1996): 1591-1595. <https://doi.org/10.1073/pnas.93.4.1591>.

**[R30]** Ron Kimmel and J. A. Sethian. “Computing Geodesic Paths on Manifolds.” *Proceedings of the National Academy of Sciences* 95, no. 15 (1998): 8431-8435. <https://doi.org/10.1073/pnas.95.15.8431>.

**[R31]** Ilker Kucukoglu, Tulin Gunduz, Fatma Balkancioglu, Emine Chousein Topal, and Oznur Sayim. “Application of Precedence Constrained Travelling Salesman Problem Model for Tool Path Optimization in CNC Milling Machines.” *An International Journal of Optimization and Control: Theories & Applications* 9, no. 3 (2019): 59-68. <https://doi.org/10.11121/ijocta.01.2019.00662>.

**[R32]** Qiang Zhang, Shurong Li, and Jianxin Guo. “Minimum Time Trajectory Optimization of CNC Machining with Tracking Error Constraints.” *Abstract and Applied Analysis* 2014, Article 835098. <https://doi.org/10.1155/2014/835098>.

**[R33]** Hung Pham and Quang-Cuong Pham. “A New Approach to Time-Optimal Path Parameterization Based on Reachability Analysis.” *IEEE Transactions on Robotics* 34, no. 3 (2018): 645-659. <https://doi.org/10.1109/TRO.2018.2819195>.

**[R34]** Leslie Lamport. *Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers*. Addison-Wesley, 2002. <https://lamport.azurewebsites.net/tla/book.html>.

**[R35]** Rajeev Alur, Costas Courcoubetis, Thomas A. Henzinger, and Pei-Hsin Ho. “The Algorithmic Analysis of Hybrid Systems.” *Theoretical Computer Science* 138, no. 1 (1995): 3-34. <https://doi.org/10.1016/0304-3975(94)00202-T>.

**[R36]** J. Tanner Slagel, Lauren M. White, Aaron Dutle, César A. Muñoz, and Nicolas Crespo. “A Formal Verification Framework for Runtime Assurance.” In *NASA Formal Methods 2024*, 322-328. <https://doi.org/10.1007/978-3-031-60698-4_19>.

**[R37]** Walid Taha and Tim Sheard. “MetaML and Multi-Stage Programming with Explicit Annotations.” *Theoretical Computer Science* 248, nos. 1-2 (2000): 211-242. <https://doi.org/10.1016/S0304-3975(00)00053-0>.

**[R38]** John C. Reynolds. “Separation Logic: A Logic for Shared Mutable Data Structures.” In *Proceedings of the 17th Annual IEEE Symposium on Logic in Computer Science*, 55-74, 2002. <https://doi.org/10.1109/LICS.2002.1029817>.

**[R39]** Kenji Maillard, Danel Ahman, Robert Atkey, Guido Martínez, Cătălin Hriţcu, Exequiel Rivas, and Éric Tanter. “Dijkstra Monads for All.” *Proceedings of the ACM on Programming Languages* 3, ICFP, Article 104 (2019). <https://doi.org/10.1145/3341708>.

**[R40]** Allison Barnard Feeney and Simon P. Frechette. “Testing STEP-NC Implementations.” In *Proceedings of World Automation Congress 2002*. National Institute of Standards and Technology. <https://www.nist.gov/publications/testing-step-nc-implementations>.

**[R41]** George C. Necula and Peter Lee. “Efficient Representation and Validation of Proofs.” In *Proceedings of the 13th Annual IEEE Symposium on Logic in Computer Science*, 93-104, 1998. <https://doi.org/10.1109/LICS.1998.705646>.

**[R42]** Thomas R. Kramer and Frederick M. Proctor. *Feature-Based Control of a Machining Center*. NISTIR 5926, National Institute of Standards and Technology, 1996. <https://www.nist.gov/publications/feature-based-control-machining-center>.

**[R43]** John L. Michaloski, Thomas R. Kramer, Frederick M. Proctor, Xun Xu, Sid Venkatesh, and David Odendahl. “STEPNC++ -- An Effective Tool for Feature-Based CAM/CNC.” In *Advanced Design and Manufacturing Based on STEP*. Springer, 2009. <https://www.nist.gov/publications/stepnc-effective-tool-feature-based-camcnc>.

# Source Snapshot and Reproducibility Notes {-}

\markboth{Source Snapshot and Reproducibility Notes}{Source Snapshot and Reproducibility Notes}

The implementation-specific case study is based on the supplied `dropcut-studio.zip` snapshot and the public repository branch `task/cnc-control-dropcut` near commit `e82bed1e5a00f38f4441e6ea13e1265edc775928`, inspected in August 2026. The case study is not a statement about later revisions. Where firmware behavior is discussed, the reviewed source evidence used the Makera stock Carvera firmware repository at commit `1683b6fb5c7ec1d341c476c6fdb2a22f7a26220e` and explicitly distinguished stock behavior from community-firmware changes.

The textbook's diagrams are generated from Graphviz or Matplotlib source stored with the Markdown edition. The PDF is rendered from the same Markdown source. Equations, algorithms, and TypeScript interfaces are pedagogical specifications; they must be implemented, tested, and connected to machine-specific assumptions before they can support a production certificate.

