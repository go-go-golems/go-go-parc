# Beyond CLIM

## Proof-oriented architectures for a modern presentation-based system

**Status:** Clean-slate architecture study  
**Analyzed codebase:** the enhanced `pbui` repository and its `packages/datalab-ui` application supplied with this conversation  
**Date:** 2026-08-03  
**Relationship to the earlier documents:** this is a second architecture study. The first study explains CLIM and extends the existing PBUI design. The linked-workspace study develops subject bindings and application ports within that design. This document deliberately asks what the system could become if CLIM were treated as historical evidence rather than as the decomposition to preserve.  
**Implementation status:** no source changes are claimed in this document. Code fragments marked **Illustrative API** describe candidate interfaces and semantic intermediate representations.

---

## Executive summary

A presentation-based interface can be defined more generally than “objects are presented with types, selectors accept them, translators convert them, and commands act on them.” That decomposition was exceptionally productive in Common Lisp CLIM, but it is not the only possible semantic center for a system built today.

The clean-slate question is:

> What small mathematical kernel could describe denotation, visible occurrences, admissible interaction, component linking, state transition, explanation, and incremental execution in a form that is compositional, serializable, and open to proof?

The strongest answer is not one new abstraction. Different parts of the problem have different mathematical shapes:

- **Inductive syntax and effectful interaction programs** are naturally described by initial algebras, free monads, and algebraic effects.
- **Eligibility, action availability, conversion reachability, permissions, and dependency closure** are naturally described by monotone rules and least fixed points.
- **Applications with typed ports and reusable workspace templates** are naturally described as open systems, wiring diagrams, structured cospans, or typed hypergraphs.
- **Link, unlink, fork, duplicate, and delete** are state changes on graph-like objects and are naturally described by typed graph rewrites.
- **Editable views of shared state** require bidirectional laws and are naturally described by lenses or related bidirectional transformations.
- **Long-running interactive behavior** is naturally described coalgebraically or as a temporal transition system.
- **Responsive recomputation** belongs to incremental computation and differential dataflow, not to the denotational API itself.
- **Collaborative convergence** belongs to semilattices, CRDTs, and coordination analysis, and should not be assumed merely because the local semantics is monotone.

This study therefore recommends a layered **Open Presentation Kernel**, abbreviated **OPK**, rather than a modernized CLIM clone.

Its semantic spine is a typed, serializable world model:

1. A **schema** declares entity sorts, relations, protocols, commands, and effects.
2. A **base instance** contains application objects, visible occurrences, components, ports, junctions, permissions, and current subjects.
3. A **positive rule theory** derives facts such as eligibility, available actions, ownership, compatibility, conversion paths, and affected views.
4. The derived world is the least fixed point

   \[
   C_\Gamma(I) = \mu X.\; I \cup T_\Gamma(X).
   \]

5. Open components are assembled as a wiring diagram. Its mathematical semantics may be a colimit or structured-cospan composition, while the implementation stores a normalized incidence graph.
6. Commands transform the base instance through typed graph rewrites and emit algebraic effects.
7. React renders a projection of the saturated world and registers visible occurrences. It is an interpreter and adapter, not the semantic owner of interaction.
8. An incremental engine maintains the fixed point and render queries as small deltas arrive.

The fixed-point construction can be linked directly to categorical structure. Under suitable conditions, saturation is a closure operator and a reflector:

\[
C_\Gamma \dashv J : \mathbf{Sat}_\Gamma \hookrightarrow \mathbf{Inst}_\Sigma,
\]

where `Inst` is the category of typed instances and `Sat` is the full subcategory of instances closed under the rule theory. Because a reflector is a left adjoint, it preserves colimits. This yields a precise version of the desired slogan:

> **Compose raw components by a colimit, then apply semantic closure.**

For a diagram \(D\) of already saturated components, the composed saturated system is, when the stated assumptions hold,

\[
\operatorname{colim}_{\mathbf{Sat}_\Gamma} D
\;\cong\;
C_\Gamma\!\left(
  \operatorname{colim}_{\mathbf{Inst}_\Sigma} JD
\right).
\]

This is not decorative category theory. It gives a concrete modularity criterion: plugin union, workspace assembly, and link-group formation can be separated from the rules that derive what becomes selectable and actionable after composition.

Transfinite induction also has a legitimate, but bounded, role. For a monotone operator on a complete lattice, one may define an ordinal-indexed chain

\[
X_0=\bot,\qquad
X_{\alpha+1}=F(X_\alpha),\qquad
X_\lambda=\bigvee_{\beta<\lambda}X_\beta.
\]

It supports existence proofs, free constructions, and invariant proofs at limit stages. It should not become a browser algorithm. A finite UI world with a positive finite rule program reaches its least fixed point after finitely many fact additions. An \(\omega\)-continuous domain can use ordinary Kleene iteration. Infinite-height analyses may require worklists, widening, or domain-specific solvers. Arbitrary JavaScript callbacks do not become monotone or provable by being placed behind a TypeScript method named `prove`.

The recommended API therefore has two explicit tiers:

- an **analyzable core DSL**, represented as data, with known semantics, dependency tracking, generated proof obligations, deterministic replay, and multiple interpreters;
- a **foreign JavaScript boundary** for React rendering, database calls, opaque predicates, and product-specific algorithms, where purity, monotonicity, dependencies, and capabilities are declared assumptions rather than silently inferred.

For the existing repository, this direction preserves its strongest decisions:

- serializable Datalab verbs;
- pure presentation descriptors;
- explicit semantic identity;
- the distinction between application views and placements;
- `GraphicDocument` as a typed analytical intermediate representation;
- pure portable bundle hydration;
- explicit analysis execution ports.

It changes the center of gravity:

- selectors become logical goals;
- subtype traversal becomes a derived relation;
- conversions become proof-producing typed derivations, optionally weighted over a semiring;
- action rules become command-applicability rules;
- `documentBindingId` becomes a typed junction carrying a subject;
- application descriptors declare protocols and ports rather than a `docBound` Boolean;
- layout reducers become compiled graph-rewrite commands;
- PBUI context methods become interpreters over an algebraic interaction program.

The result is not a single mathematically pure object. It is a disciplined correspondence between several structures, each used where its universal property or proof principle is actually relevant.

---

## Contents

1. [Why reconsider the architecture](#1-why-reconsider-the-architecture)  
2. [What remains essential in a presentation-based UI](#2-what-remains-essential-in-a-presentation-based-ui)  
3. [The current PBUI and Datalab baseline](#3-the-current-pbui-and-datalab-baseline)  
4. [Design criteria for a clean-slate kernel](#4-design-criteria-for-a-clean-slate-kernel)  
5. [What “prove properties” can mean](#5-what-prove-properties-can-mean)  
6. [Mathematical foundations for newcomers](#6-mathematical-foundations-for-newcomers)  
7. [Architecture family A: algebraic effects and command algebras](#7-architecture-family-a-algebraic-effects-and-command-algebras)  
8. [Architecture family B: monotone relational and fixed-point semantics](#8-architecture-family-b-monotone-relational-and-fixed-point-semantics)  
9. [Architecture family C: open systems, cospans, and wiring diagrams](#9-architecture-family-c-open-systems-cospans-and-wiring-diagrams)  
10. [Architecture family D: presheaves and categorical data](#10-architecture-family-d-presheaves-and-categorical-data)  
11. [Architecture family E: typed graph rewriting](#11-architecture-family-e-typed-graph-rewriting)  
12. [Architecture family F: lenses and bidirectional transformations](#12-architecture-family-f-lenses-and-bidirectional-transformations)  
13. [Architecture family G: coalgebraic and temporal behavior](#13-architecture-family-g-coalgebraic-and-temporal-behavior)  
14. [Architecture family H: incremental and differential execution](#14-architecture-family-h-incremental-and-differential-execution)  
15. [Architecture family I: semilattices, CRDTs, and coordination](#15-architecture-family-i-semilattices-crdts-and-coordination)  
16. [Architecture family J: constraint and proof-carrying APIs](#16-architecture-family-j-constraint-and-proof-carrying-apis)  
17. [Comparison of the architecture families](#17-comparison-of-the-architecture-families)  
18. [Recommended synthesis: the Open Presentation Kernel](#18-recommended-synthesis-the-open-presentation-kernel)  
19. [The formal world model](#19-the-formal-world-model)  
20. [Fixed-point closure as a reflection](#20-fixed-point-closure-as-a-reflection)  
21. [Transfinite construction and its practical boundary](#21-transfinite-construction-and-its-practical-boundary)  
22. [Colimits, linking, and reusable workspaces](#22-colimits-linking-and-reusable-workspaces)  
23. [An illustrative TypeScript API](#23-an-illustrative-typescript-api)  
24. [Presentations and input contexts as judgments](#24-presentations-and-input-contexts-as-judgments)  
25. [Actions as commands with preconditions and effects](#25-actions-as-commands-with-preconditions-and-effects)  
26. [Conversions as derivations with cost and provenance](#26-conversions-as-derivations-with-cost-and-provenance)  
27. [Graph rewrites for link, unlink, fork, and duplicate](#27-graph-rewrites-for-link-unlink-fork-and-duplicate)  
28. [Lenses for editable application views](#28-lenses-for-editable-application-views)  
29. [Behavior, concurrency, and model checking](#29-behavior-concurrency-and-model-checking)  
30. [Foreign JavaScript and the proof boundary](#30-foreign-javascript-and-the-proof-boundary)  
31. [Incremental execution and performance](#31-incremental-execution-and-performance)  
32. [Worked Datalab census workspace](#32-worked-datalab-census-workspace)  
33. [Mapping the proposal onto the current repository](#33-mapping-the-proposal-onto-the-current-repository)  
34. [Verification strategy and theorem inventory](#34-verification-strategy-and-theorem-inventory)  
35. [Migration roadmap](#35-migration-roadmap)  
36. [Risks, limits, and rejected simplifications](#36-risks-limits-and-rejected-simplifications)  
37. [Glossary](#37-glossary)  
38. [References](#38-references)  
39. [Final recommendation](#39-final-recommendation)

---

# 1. Why reconsider the architecture

The earlier PBUI work starts from a productive historical question: how can the ideas of CLIM presentations, input contexts, translators, commands, and semantic identity be carried into React and TypeScript?

That question produces direct improvements. The enhanced repository now has prepared selectors, operation-scoped semantic memoization, runtime subtyping, selector-driven action rules, weighted conversion paths, explicit object identity, and shared document bindings. These features make the system substantially more expressive.

The next question is different:

> If the design began today, with no requirement to preserve CLIM’s named abstractions, which semantic decomposition would make the system easiest to compose, analyze, optimize, serialize, and verify?

There are three reasons to ask this now.

## 1.1 CLIM’s decomposition combines several semantic problems

A CLIM presentation type participates in at least four roles:

- it classifies a visible object;
- it helps determine whether an input context accepts that object;
- it participates in translation and command applicability;
- it influences rendering and interaction conventions.

That integration is convenient in a dynamic object system. It is less ideal when the goals include remote execution, serializable plans, incremental dependency tracking, generated verification models, plugin isolation, and React rendering.

Modern systems tend to separate:

- **syntax from interpretation**;
- **base facts from derived facts**;
- **component interfaces from component implementations**;
- **state transitions from effects**;
- **views from update propagation**;
- **denotational meaning from incremental execution**.

The separation does not imply that these layers are independent. It makes their correspondence explicit.

## 1.2 JavaScript flexibility conflicts with analyzability

The enhanced selector API can accept arbitrary lambdas. This is valuable product flexibility, but an arbitrary JavaScript closure may:

- read ambient mutable state;
- perform I/O;
- depend on time;
- throw;
- be non-deterministic;
- be non-monotone;
- hide its dependency set;
- be impossible to serialize;
- be impossible to run remotely;
- invalidate caches without notification.

No mathematical reframing removes that fact. A proof-oriented system must distinguish an analyzable expression from an opaque callback.

The core architectural choice is therefore not “functions or data.” It is:

> Which functions are represented as syntax with declared semantics, and where is opaque host-language computation permitted?

## 1.3 Linking exposed a more general composition problem

The linked-workspace requirement initially looked like synchronized selectors. It led to a deeper structure:

- applications have ports;
- ports carry typed subjects;
- multiple applications can be connected to one junction;
- templates are open networks with exposed ports;
- duplication has graph-copy semantics;
- unlinking changes the factorization of a network;
- source retargeting is not the same transition as analysis rebinding.

This is not primarily a presentation-type problem. It is an open-system composition problem with presentation-based interaction layered over it.

The redesign should therefore make composition a first-class semantic concern rather than encoding it in special reducers and descriptor flags.

---

# 2. What remains essential in a presentation-based UI

Moving beyond CLIM does not mean discarding the phenomenon that CLIM identified.

A presentation-based UI differs from an ordinary widget system because a visible region participates in a semantic interaction space. The system knows not only that a DOM node was clicked, but also:

- which application entity it denotes;
- under which presentation interpretation it is visible;
- which input goals it can satisfy;
- which commands can consume it;
- which conversions can derive another admissible value from it;
- why it is or is not currently available;
- which state and capabilities its actions may affect.

A clean-slate system still requires the following distinctions.

## 2.1 Entity and occurrence

An **entity** is an application-level object: a field, document, chart specification, user, pipeline step, analysis port, or workspace.

An **occurrence** is one visible or otherwise addressable manifestation of an entity. The same field can occur in a table header, encoding editor, chart axis label, and command palette.

Occurrence identity must remain distinct from entity identity. Pointer targeting, focus, geometry, and local affordances belong to the occurrence. Cross-view equality, selection, watchlists, and ownership belong to the entity.

## 2.2 Denotation and representation

A rendered label or mark denotes an entity, but visual representation is not the entity’s identity. Two different renderers can denote the same entity. One renderer can also expose several semantic occurrences within one visual component.

## 2.3 Input as a goal

An input context should be understood as a goal to satisfy, not merely as an event listener waiting for a type tag. The goal may include:

- a required sort or protocol;
- ownership conditions;
- permissions;
- compatibility with another selected object;
- cardinality constraints;
- a ranking or cost model;
- a request for evidence or an explanation.

## 2.4 Action as a parameterized transition

An action should not be a closure attached to a descriptor. It is better understood as a command schema with:

- typed parameters;
- an applicability proposition;
- a state transition;
- declared effects;
- authorization requirements;
- postconditions;
- provenance and audit information.

A context menu is then a rendered query result over applicable command instances.

## 2.5 Conversion as derivation

A conversion is not merely a function from one tagged value to another. It is a derivation that states why a target interpretation follows from a source interpretation. It can carry:

- a path;
- a cost;
- assumptions;
- dependencies;
- a proof object or explanation;
- an effect classification.

## 2.6 Composition as structure

Applications should expose typed boundaries. Connecting components should be a semantic operation with known laws, not only a sequence of assignments to IDs.

## 2.7 State change and observation

The system must distinguish:

- the current world;
- facts derived from that world;
- a command that changes the world;
- effects required to realize the command;
- observations rendered to the user;
- the event trace through which the world evolved.

These distinctions form the minimal content of “presentation-based” after the CLIM-specific names are removed.

---

# 3. The current PBUI and Datalab baseline

The enhanced repository already contains several seams that support a more formal architecture.

## 3.1 Generic PBUI

The generic PBUI package currently models a presentation reference as a tagged value:

```ts
type PresentationReference = {
  type: PresentationType;
  value: unknown;
};
```

Its registry provides:

- presentation descriptors;
- semantic identity domains and keys;
- a runtime subtype graph;
- prepared selectors with arbitrary predicates;
- action rules selected by selectors;
- weighted conversion edges;
- operation-scoped identity memoization.

The React adapter provides a promise-based `accept` operation. Visible occurrences register through a `Presentation` component and become sensitive while an input context is active.

This is a capable runtime registry. It is not yet a semantic intermediate representation. Important behavior is still distributed among descriptor functions, selector functions, conversion callbacks, registry traversal, React context state, and the product verb interpreter.

## 3.2 Serializable Datalab verbs

Datalab’s PBUI actions produce serializable verbs rather than performing product effects directly. This is one of the strongest existing decisions.

A verb is data that can be:

- reduced in Redux;
- logged;
- tested;
- replayed;
- sent over a boundary;
- interpreted differently in another environment.

This is already close to an algebraic command language. The missing step is to give commands declarative preconditions, transition semantics, effect signatures, and generated proof obligations.

## 3.3 Explicit identity

Datalab defines semantic keys for fields, documents, sources, categories, rows, pipeline steps, users, tokens, uploads, members, placements, workspaces, stages, and trace entries.

This should be retained. In a proof-oriented world model, semantic identity becomes a key constraint or explicit equality relation rather than a callback used only during selection.

## 3.4 Application views, placements, and bindings

The layout model distinguishes:

- a logical application view;
- a placement of that view in a workspace;
- a selected document;
- an optional shared `documentBindingId`.

This distinction enabled chart, table, pipeline, and encoding views to observe one document subject. It also exposed the need for first-class ports and junctions.

In the proposed architecture, `documentBindingId` is not generalized into more ID fields. It becomes a typed graph node representing a junction or binding.

## 3.5 `GraphicDocument` as an intermediate representation

`GraphicDocument` is already a declarative analytical object containing sources, transforms, views, encodings, and parameters. Datalab compiles it to a logical graph and then to executable analysis operations.

This is an example of the architecture this study recommends:

- authoring syntax is data;
- validation and compilation are explicit;
- execution is behind a port;
- diagnostics are values.

The presentation system should adopt the same pattern rather than embedding its semantics in host-language callbacks.

## 3.6 Portable bundle hydration

Portable export and import deduplicate documents and views, encode binding equivalence, mint fresh runtime identities, and reconstruct sharing. This is graph-aware copying.

It can become the implementation basis for categorical-looking operations such as template instantiation and workspace fork, without forcing the runtime to materialize abstract colimits literally.

## 3.7 The central limitation

Selectors, actions, conversions, bindings, and transitions are currently separate mechanisms:

```text
selector predicates
    + subtype graph
    + conversion graph
    + action-rule registry
    + layout reducers
    + product verb interpreter
    + React occurrence registration
```

Each mechanism is reasonable in isolation. Their composition has no single inspectable semantics. A user can see that an action exists, but the system cannot uniformly answer:

- Which base facts made it available?
- Which rule derived it?
- Which conversion path was chosen?
- Which permissions were consulted?
- Which views will be affected?
- Which cache entries depend on those facts?
- Which invariant guarantees that the resulting link is valid?

The redesign should turn those questions into queries over one semantic core.

---

# 4. Design criteria for a clean-slate kernel

A modern architecture should be judged against more than API elegance.

## 4.1 Semantic criteria

The kernel should have:

1. **Explicit denotation.** Every occurrence denotes an entity through a first-class relation.
2. **Explicit identity.** Identity is typed, namespaced, and independent of object allocation.
3. **Compositional interfaces.** Components expose named, typed ports.
4. **Declarative admissibility.** Selection and action availability are represented as formulas or rules.
5. **Serializable transitions.** Commands are data with known preconditions and effects.
6. **Lawful projections.** Editable views declare or generate bidirectional laws.
7. **Deterministic resolution.** Ambiguity, priority, cost, and shadowing have specified semantics.
8. **Explainability.** Derived results can carry evidence and dependency provenance.

## 4.2 Proof criteria

The kernel should make it possible to establish:

- well-typedness of states and transitions;
- preservation of structural invariants;
- termination of finite saturation;
- existence of least or greatest fixed points under stated assumptions;
- associativity or coherence of component composition;
- soundness of eligibility and action derivations;
- lawfulness of view updates;
- equivalence between incremental and from-scratch evaluation;
- safety and liveness of concurrent interaction protocols;
- convergence of collaborative data types where applicable.

The API need not prove every application theorem inside TypeScript. It must preserve enough structure to export, check, or test these obligations.

## 4.3 Engineering criteria

The system should support:

- React and SVG rendering;
- keyboard and pointer interaction;
- local and remote interpreters;
- server-side precomputation;
- deterministic logs and undo;
- hot plugin loading;
- schema evolution;
- fast incremental updates;
- bounded memory use;
- developer inspection tools;
- graceful use of ordinary JavaScript where formalization is not economical.

## 4.4 Product criteria

The architecture should make common operations direct:

- select a visible field;
- invoke an action on a chart mark;
- link application ports;
- explain why an item is disabled;
- duplicate a workspace independently;
- instantiate a workspace template on a new dataset;
- keep several views synchronized by shared subject;
- support comparison views with more than one subject;
- preserve workflows while changing compatible data sources.

A mathematically elegant core that makes these tasks cumbersome is not a successful UI architecture.

## 4.5 Epistemic honesty

The system must distinguish four statuses:

- **proved from the formal core**;
- **model-checked within a finite scope**;
- **tested against generated cases**;
- **assumed about foreign code**.

These statuses should appear in tooling and diagnostics. A declaration such as `monotone: true` is an assumption unless a verifier checks it.

---

# 5. What “prove properties” can mean

The phrase “prove properties of the API” covers several different activities.

## 5.1 Construction by type

Some invalid programs can be made unrepresentable by the host type system. Examples include:

- connecting a selection port to an analysis-document junction;
- issuing a command without required parameters;
- treating an occurrence ID as an entity ID;
- using a field reference without its owning document key.

TypeScript can assist here, but its erased structural type system is not a theorem prover. Runtime schema validation remains necessary at persistence and network boundaries.

## 5.2 Algebraic law by construction

Combinators can preserve laws. For example:

- composition of well-behaved lenses preserves standard lens laws;
- folding an initial algebra gives a unique homomorphism;
- composing structured cospans is associative up to canonical isomorphism under the required colimit assumptions;
- positive relational rule composition preserves monotonicity.

The API can expose only constructors whose semantics is already known to preserve a class of properties.

## 5.3 Inductive proof over syntax or traces

If commands and queries are represented as inductive syntax, proofs can proceed by structural induction.

If state changes are represented as a trace of transitions, safety can be proved by ordinary induction:

1. the invariant holds in the initial state;
2. every command preserves it;
3. therefore it holds in every reachable finite state.

This is often more useful than transfinite induction for actual UI transitions.

## 5.4 Fixed-point proof

Recursive derivation systems are interpreted as least or greatest fixed points. Proof obligations include:

- monotonicity of the immediate-consequence operator;
- continuity where ordinary Kleene iteration is claimed;
- finite-height or widening conditions where termination is claimed;
- stratification when negation or aggregation is used.

## 5.5 Transfinite induction

Transfinite induction is appropriate when a construction is indexed by all ordinals until it stabilizes. The proof has three cases:

- a base case at \(0\);
- a successor case from \(\alpha\) to \(\alpha+1\);
- a limit case proving the property is preserved by the colimit or supremum of all earlier stages.

This can justify:

- a least fixed point of a general monotone operator;
- a free algebra generated by a transfinite chain;
- closure under an open-ended family of constructors;
- an invariant of a colimit at a limit ordinal.

It is rarely the right operational account for a finite browser session.

## 5.6 Bounded model checking

Alloy is effective for finding small structural counterexamples:

- a port belongs to two forbidden exclusive junctions;
- a workspace fork accidentally retains an identity alias;
- deletion leaves a dangling subject reference;
- link and unlink do not preserve a declared multiplicity.

A bounded check does not prove the property for all cardinalities, but it is valuable architecture feedback.

## 5.7 Temporal model checking

TLA+ is suitable for state-machine properties involving interleavings:

- two users link and unlink the same views concurrently;
- an analysis execution completes after its binding was rebound;
- a stale revision overwrites a newer source fork;
- undo races with remote persistence;
- every accepted command eventually receives success or failure.

## 5.8 Theorem proving

A compact kernel can be encoded in Lean, Rocq, Agda, Isabelle, or another prover. The TypeScript API can emit the same core IR for runtime and formal translation.

The practical target should be small metatheorems about the kernel and generated obligations for product schemas, not a proof of every React component.

## 5.9 Proof-carrying results

A runtime result can carry an evidence term:

```ts
type Judgement<P> = {
  proposition: P;
  derivation: Derivation;
  dependencies: readonly FactKey[];
  assumptions: readonly AssumptionId[];
};
```

The evidence need not be a proof-assistant term. It can be a checked derivation tree whose rule applications are validated by the kernel. This supports explanation, invalidation, auditing, and test diagnostics.

---

# 6. Mathematical foundations for newcomers

This section introduces the structures used later. It is intentionally concrete.

## 6.1 Posets and lattices

A **partial order** is a set equipped with a relation \(\leq\) that is reflexive, antisymmetric, and transitive.

A common UI example is a set of known facts ordered by inclusion:

\[
F_1 \leq F_2 \quad\text{when}\quad F_1 \subseteq F_2.
\]

A **join** \(x\vee y\) is the least value above both \(x\) and \(y\). For fact sets, it is union.

A **complete lattice** has joins and meets for every subset, including infinite ones. A power set ordered by inclusion is a complete lattice.

## 6.2 Monotone functions

A function \(f:L\to L\) is monotone when

\[
x\leq y \implies f(x)\leq f(y).
\]

For facts, this says that supplying more input facts cannot make the operator derive fewer facts.

Positive Datalog-style rules are monotone. A rule based on the absence of a fact usually is not.

## 6.3 Fixed points

A fixed point of \(f\) is an \(x\) such that \(f(x)=x\).

The least fixed point is the smallest stable result. It is the natural meaning of recursive positive rules: derive only facts forced by the base data and rules.

For example, transitive subtype closure can be generated by:

```text
subtype*(x, x)
subtype*(x, z) :- subtype(x, y), subtype*(y, z)
```

The least fixed point contains exactly the reachable subtype pairs, not arbitrary additional pairs.

## 6.4 Kleene iteration

When the domain and operator satisfy the required continuity assumptions, the least fixed point can be obtained by iteration from the least element:

\[
\bot,\; f(\bot),\; f^2(\bot),\ldots
\]

For a finite set of possible facts, a worklist reaches stability after finitely many new facts.

## 6.5 Ordinals and transfinite iteration

Ordinals extend finite counting with ordered limit stages. At a successor stage, apply the operator. At a limit stage, take the supremum of all previous stages.

For an inflationary monotone operator \(F\), or for the standard chain generated from bottom, define:

\[
X_0=\bot,
\]

\[
X_{\alpha+1}=F(X_\alpha),
\]

\[
X_\lambda=\bigvee_{\beta<\lambda}X_\beta
\quad\text{for a limit ordinal }\lambda.
\]

Because a set-sized lattice cannot contain a strictly increasing chain longer than its cardinality permits, the chain eventually stabilizes. The first stage at which it stabilizes is a closure ordinal.

## 6.6 Categories and universal properties

A **category** has objects and composable arrows. An arrow may represent a function, a graph homomorphism, a schema mapping, or another structure-preserving map.

A **universal property** characterizes an object by how all compatible arrows factor through it. This matters because universal constructions compose coherently and are unique up to canonical isomorphism.

Category theory is useful here only when the chosen objects and arrows are specified. “This looks like a colimit” is not a design until the category and diagram are named.

## 6.7 Coproducts, pushouts, and colimits

A **coproduct** combines independent objects. In `Set`, it is a tagged disjoint union.

A **pushout** glues two objects along a shared interface:

```text
      B
     / \
    v   v
   X     Y
    \   /
     v v
      P
```

The pushout \(P\) is the most general object containing \(X\) and \(Y\) while identifying the images of \(B\).

A **colimit** generalizes coproducts and pushouts to arbitrary diagrams.

For UI architecture, legitimate uses include:

- combining plugin vocabularies by coproduct;
- gluing component ports by pushout;
- assembling a workspace network as a colimit;
- taking a limit-stage union in a transfinite construction.

## 6.8 Initial algebras

For an endofunctor \(F\), an \(F\)-algebra is a map

\[
F(A)\to A.
\]

An **initial** \(F\)-algebra is the canonical object generated by the constructors described by \(F\). It supports induction and a unique fold into every other \(F\)-algebra.

Abstract syntax trees are the standard programming example. If a query language has constructors for conjunction, existential quantification, relation lookup, and equality, its syntax is an inductively generated algebraic data type.

A handler or interpreter is a fold from that syntax into a semantic algebra.

## 6.9 Free monads and algebraic effects

An algebraic effect signature declares operations without fixing their implementation. A program is built from pure values and effect operations. A handler interprets those operations.

For a presentation system, operations might include:

```text
Ask(goal)
Choose(candidates)
Perform(command)
ReadWorld(query)
Emit(effect)
OpenMenu(actions)
```

The same program can be interpreted by:

- a React interaction handler;
- a test simulator;
- a remote protocol handler;
- a trace recorder;
- an accessibility-oriented handler.

## 6.10 Final coalgebras and coinduction

An \(F\)-coalgebra has a map

\[
A\to F(A).
\]

Coalgebras model systems by their observations and possible next states. A UI session is ongoing behavior, not merely finite syntax.

Coinduction proves two systems behaviorally equivalent by exhibiting a bisimulation rather than by unfolding an infinite trace.

## 6.11 Adjunctions and reflections

An adjunction \(L\dashv R\) expresses a best correspondence between arrows out of \(L(A)\) and arrows into \(R(B)\).

A **reflection** is an adjunction where a full subcategory is included into a larger category and every object has a best approximation inside the subcategory.

Rule saturation can form a reflection when every base instance has a least saturated extension. This becomes central in Section 20.

## 6.12 Presheaves and typed instances

A graph schema can be represented by a small category. An instance assigns a set of elements to each sort and a function to each structural arrow. This is a Set-valued functor.

This representation supports:

- typed graphs;
- database-like instances;
- pointwise limits and colimits;
- schema mappings and data migration;
- structural validation.

The implementation need not expose the word “presheaf” to application developers.

## 6.13 Lenses

A basic asymmetric lens from source \(S\) to view \(V\) has:

```text
get : S → V
put : S × V → S
```

Common laws include:

- **GetPut:** putting back what was just read does not change the source;
- **PutGet:** reading after putting returns the requested view;
- **PutPut:** only the most recent view update matters.

These laws are relevant when a pipeline editor, encoding editor, or form edits one projection of a shared `GraphicDocument`.

## 6.14 Graph rewriting

A typed graph rewrite identifies a pattern, preserves part of it, removes part of it, and creates a replacement. Double-pushout rewriting represents a rule as a span

\[
L \leftarrow K \rightarrow R.
\]

Applied to a matching subgraph, it produces a new graph while making deletion and preservation explicit.

This is a natural semantic model for link, unlink, fork, and delete.

## 6.15 Semirings and provenance

A semiring supplies addition and multiplication. Database provenance uses these operations to combine alternative derivations and joint dependencies.

Different semirings answer different questions:

- Boolean: is a derivation possible?
- Natural numbers: how many derivations exist?
- Provenance polynomials: which source facts support the result?
- Min-plus: what is the minimum conversion cost?

This makes provenance and weighted conversion two instances of a common evaluation pattern, although priority and left-biased overriding may require a separate deterministic resolution phase.

---

# 7. Architecture family A: algebraic effects and command algebras

The first alternative makes **interaction programs** the center of the API.

Instead of `accept` directly mutating React context and returning a promise, the application constructs a program in a small interaction language. The program requests semantic operations; handlers decide how those operations are realized.

## 7.1 Core idea

Consider an effect signature:

```ts
// Illustrative API
interface InteractionEffects {
  ask<A>(goal: Goal<A>): A;
  choose<A>(choice: Choice<A>): A;
  inspect<P>(proposition: P): Judgement<P> | null;
  perform<C extends Command>(command: C): CommandResult<C>;
  emit<E extends ExternalEffect>(effect: E): EffectResult<E>;
}
```

A command can then be written independently of React:

```ts
// Illustrative API
const linkAnalysis = program(function* (fx) {
  const source = yield* fx.ask(selectFocusedPort(AnalysisProtocol));
  const target = yield* fx.ask(
    selectVisiblePort(AnalysisProtocol, {
      where: compatibleWith(source),
      excluding: source,
    }),
  );

  const evidence = yield* fx.inspect(canConnect(source, target));
  if (!evidence) return cancelled("No compatible target");

  return yield* fx.perform(
    ConnectPorts({ source, target, evidence }),
  );
});
```

Possible handlers include:

```text
React pointer/keyboard handler
headless deterministic test handler
remote interaction protocol handler
screen-reader dialog handler
trace and replay handler
command-line handler
```

The application program does not know which handler is active.

## 7.2 Mathematical strength

The syntax of interaction programs is an initial algebra or free monadic construction over the operation signature. This gives several useful proof principles.

### Structural induction

A property of all programs can be proved by showing it for:

- pure values;
- each primitive operation;
- sequencing or continuation.

For example, a capability theorem can state that every program constructed without the `Network` effect is network-free under every faithful handler.

### Equational reasoning

Operations can satisfy equations. A read-only world query may commute with another read-only query. Logging may be handled homomorphically. A test interpreter can be proved equivalent to a production handler on the pure command subset.

### Handler modularity

An effect handler gives an algebra for the syntax. Interpretation is a fold. This makes “same command language, several runtimes” a semantic property rather than a convention.

## 7.3 Fit with the current repository

Datalab verbs already form a serializable command vocabulary. The generic PBUI `perform` method already separates action selection from product mutation. The promise-based `accept` operation already resembles an effect operation whose continuation resumes after a selection.

A migration could begin by representing `accept` and `perform` as operations in one program type while preserving the current React handler.

## 7.4 What this architecture solves well

It is particularly strong for:

- cancellation and resumption;
- multi-step commands;
- testing interaction without a DOM;
- logging and deterministic replay;
- separating command intent from effects;
- capability-oriented security;
- alternative accessibility handlers;
- remote or collaborative interpreters.

It also gives a clean account of a partial command. A command whose parameters are not yet filled is simply a program that has performed some `ask` operations and awaits the rest.

## 7.5 What it does not solve by itself

An algebraic effect system does not determine:

- which visible occurrences satisfy a goal;
- how subtyping or conversion is derived;
- how application ports compose;
- how shared state is linked;
- how derived facts are incrementally maintained;
- how a view update is propagated lawfully.

Those questions need another semantic layer.

## 7.6 Open effects and plugins

Effect signatures can be combined by sums or coproducts. A plugin can add an effect vocabulary without rewriting the core syntax.

However, JavaScript’s ordinary union types do not automatically provide the coherence, exhaustiveness, or algebraic laws of a formal coproduct. A practical implementation should compile plugin operation declarations into a normalized schema with globally namespaced operation IDs.

## 7.7 Main risk

It is easy to replace ordinary callback code with a fashionable generator or free-monad API while retaining opaque semantics. The value appears only when:

- operations are data;
- handlers are explicit;
- effects are typed and capability-scoped;
- laws are attached to constructors rather than asserted about arbitrary callbacks;
- the interaction program does not hide state reads in host-language closures.

## 7.8 Verdict

Use algebraic effects as the **command and interaction language**, not as the entire presentation architecture.

---

# 8. Architecture family B: monotone relational and fixed-point semantics

The second alternative makes a **typed relational world and its derived closure** the center of the system.

This is the strongest candidate for unifying selectors, subtyping, action availability, conversion reachability, permissions, ownership, dependency analysis, and explanations.

## 8.1 Core idea

The base world contains facts:

```text
denotes(occurrence-17, field-census-region)
presentedAs(occurrence-17, field)
visibleOn(occurrence-17, surface-chart-4)
requests(context-9, field)
subtype(quantitative-field, field)
owns(field-census-region, document-census)
can(actor-alice, select, field-census-region)
```

Rules derive additional facts:

```text
subtypeStar(x, x).
subtypeStar(x, z) :- subtype(x, y), subtypeStar(y, z).

eligible(q, o) :-
  requests(q, expected),
  presentedAs(o, actual),
  subtypeStar(actual, expected),
  denotes(o, entity),
  can(actorOf(q), select, entity),
  visibleInContext(o, q).
```

An action menu is a query:

```text
availableAction(context, occurrence, commandInstance)
```

A conversion is another derived relation:

```text
derives(sourceEntity, targetType, targetEntity, evidence, cost)
```

## 8.2 Least-fixed-point semantics

Let \(I\) be the base facts and \(T_\Gamma\) the immediate-consequence operator for rule theory \(\Gamma\). Define:

\[
F_I(X)=I\cup T_\Gamma(X).
\]

For positive rules, \(F_I\) is monotone. Its least fixed point is the intended derived world:

\[
C_\Gamma(I)=\mu F_I.
\]

This gives a stable semantic meaning independent of evaluation order.

## 8.3 Finite termination

Suppose the active world has a finite universe and the rule language creates no fresh entities during saturation. Then there are finitely many possible ground facts. Each strict iteration adds at least one fact, so saturation terminates.

A practical engine uses semi-naive evaluation or worklists rather than rescanning every rule from scratch.

## 8.4 Monotonicity types

A typed DSL can track where values are used monotonically. Datafun demonstrates that higher-order functional programming and Datalog-like monotonicity can be combined by a type system.

For PBUI, this suggests a distinction between:

- ordinary values;
- lattice-valued collections;
- monotone functions over those collections;
- snapshot-only non-monotone computations.

An application developer could write a higher-level query while the type checker prevents a monotone rule from using negation or destructive selection in an unsound position.

## 8.5 Explanation and provenance

Because a fact is derived by named rules, the engine can retain a derivation DAG. It can answer:

```text
Why is this field selectable?
Why is “Link analyses” enabled?
Why did this chart qualify as a target?
Why was this conversion preferred?
Which facts would invalidate this action?
```

The same dependency DAG supports precise cache invalidation.

## 8.6 Non-monotone requirements

Real UIs need non-monotone behavior:

- “show this action only if no link exists”;
- maximum-priority rule wins;
- choose the lowest-cost conversion;
- remove an occurrence when a component unmounts;
- revoke a permission;
- delete a document.

These do not invalidate the approach, but they must be modeled correctly.

### Snapshot transitions

Base-world deletion is a transition from \(I\) to \(I'\). Each snapshot is saturated independently. The rule engine may incrementally propagate negative deltas, but the denotational semantics remains `closure of the current base world`.

### Stratified negation

Some absence tests can be placed in a higher stratum after the lower relations have reached a fixed point. This gives deterministic semantics when the dependency graph is stratifiable.

### Aggregation and choice

Minimum cost, maximum priority, and grouping can be represented by specialized lattices, semirings, or a deterministic resolution phase after candidate derivation. They should not be smuggled into ordinary positive Boolean rules.

## 8.7 Selectors become goals

The current selector object contains types, subtype behavior, a predicate, preparation, and cache policy. In a relational design, the analyzable portion becomes a formula:

```ts
// Illustrative API
const selectableField = goal(Field, ({ value, context }) =>
  and(
    belongsTo(value, context.subjectDocument),
    not(isInternal(value)),
    hasCapability(context.actor, "field.select"),
  ),
);
```

The callback above is a syntax builder. It is not executed as the predicate. Calls such as `and`, `belongsTo`, and `hasCapability` build an expression tree.

Expensive foreign preparation can remain available behind an explicit oracle, discussed in Section 30.

## 8.8 Conversions become recursive derivations

The current bounded weighted graph search can be expressed relationally:

```text
coerce(x, t, x, 0) :- hasType(x, t).
coerce(x, target, z, c1 + c2) :-
  conversion(edge, source, mid, c1),
  applies(edge, x, y),
  coerce(y, target, z, c2).
```

Operationally, nonnegative costs compile to a shortest-path algorithm. Semantically, the result can be evaluated over the min-plus semiring.

## 8.9 Modular rule theories

Plugins contribute facts and rules. A dependency graph over derived relations can determine:

- which modules are mutually recursive;
- whether negation is stratified;
- whether a plugin can affect existing relations;
- which fixed-point strata need recomputation;
- whether an extension is conservative over the old vocabulary.

A useful plugin policy is:

> A plugin may derive core extension relations only through declared extension points; otherwise its rules may have heads only in plugin-owned relations.

This makes conservative-extension checks feasible.

## 8.10 Main risk

A relational kernel can become a generic logic-programming platform whose developer experience is worse than ordinary TypeScript. The design needs:

- domain-specific constructors;
- strong schema inference;
- good errors;
- query plans visible in developer tools;
- first-class explanations;
- strict limits on recursive or non-stratified rules;
- escape hatches with explicit proof boundaries.

## 8.11 Verdict

Use a monotone relational core as the **derived semantic layer**. It is the best place for eligibility, applicability, ownership, compatibility, permissions, dependency closure, and evidence.

---

# 9. Architecture family C: open systems, cospans, and wiring diagrams

The third alternative makes **components with typed boundaries** the center of the architecture.

This family directly addresses linked views, workspace templates, composition, nesting, and reuse.

## 9.1 Components as open systems

A component is not only a React function. It has:

- internal state or an internal graph;
- input and output ports;
- protocols carried by those ports;
- constraints on multiplicity and direction;
- an observation or rendering implementation.

For example:

```text
Chart
  analysis : duplex GraphicDocument
  selection : duplex SelectionSet
  viewport : local ViewportState

Table
  analysis : duplex GraphicDocument
  selection : duplex SelectionSet
  sort : local SortState

Pipeline
  analysis : duplex GraphicDocument
```

The `analysis` ports can be connected to one junction. The `selection` ports may be connected to another. Local ports remain unshared.

## 9.2 Structured cospans

A structured cospan has the form

\[
L(a)\longrightarrow x\longleftarrow L(b),
\]

where \(a\) and \(b\) are boundary objects and \(x\) is the internal system. Under suitable finite-colimit and adjoint assumptions, structured cospans compose by pushout and form a symmetric monoidal structure.

For a UI component:

- the boundary object lists exposed typed ports;
- `L` turns a boundary into a discrete typed graph;
- the apex contains the component instance and its internal relationships;
- composition identifies compatible boundary points.

## 9.3 Wiring diagrams and operads

An operad of wiring diagrams focuses on hierarchical substitution:

- boxes have typed ports;
- a wiring diagram explains how smaller boxes fill a larger box;
- composition substitutes one diagram into another;
- an algebra assigns executable meaning to each box and wire.

This is a strong model for workspace templates. A template is an open diagram with exposed slots. Instantiation plugs a dataset or analysis component into those slots.

## 9.4 Why a junction graph is preferable in storage

A literal pushout quotient can obscure user-visible identities. The runtime should usually store an incidence graph:

```text
port-chart-analysis ──┐
port-table-analysis ──┼── junction-main-analysis ── subject-document-census
port-pipeline-analysis┘
```

The categorical semantics explains composition, but storage retains explicit ports and junctions. This supports:

- unlinking one port;
- naming a link group;
- inspecting membership;
- retaining provenance;
- implementing undo;
- distinguishing shared reference from copied value.

## 9.5 Link is not peer synchronization

A component does not subscribe to every peer. It reads the subject carried by its junction.

Rebinding updates one edge or subject relation:

```text
carries(junction-main-analysis, document-census)
```

becomes:

```text
carries(junction-main-analysis, document-employment)
```

All connected views derive their current subject from the junction.

## 9.6 Unlink is not an inverse pushout

Pushouts are universal constructions, not reversible user operations. Unlinking should be modeled as a graph rewrite that changes the network’s factorization:

- detach one port from the shared junction;
- create a private junction;
- copy or reference the current subject according to policy;
- preserve the component and its occurrence identities.

Calling this “the inverse of the colimit” would be mathematically misleading.

## 9.7 Copy, share, and merge require modalities

A wire can mean several things:

- shared identity;
- copied value;
- event propagation;
- one-way dataflow;
- bidirectional synchronization;
- capability delegation.

A generic hypergraph category often includes copy and discard structure, but a product API must not conflate these semantics. Protocol declarations should state the sharing mode.

```ts
// Illustrative API
const AnalysisProtocol = protocol("analysis", GraphicDocument, {
  mode: "shared-subject",
  cardinality: "exactly-one-subject",
});
```

## 9.8 What this architecture solves well

It is strong for:

- named application ports;
- linked views;
- reusable workspace templates;
- nested applications;
- component replacement;
- compositional dependency analysis;
- visualization of architecture;
- local proofs that composition preserves interface typing.

## 9.9 What it does not solve by itself

Open-system composition does not determine:

- whether a visible field satisfies an input goal;
- which command is authorized;
- how an editable projection updates a document;
- how commands are sequenced;
- how the composed system is rendered efficiently.

## 9.10 Main risk

Category-theoretic diagrams can encourage a framework whose conceptual vocabulary exceeds the product’s needs. The public API should use familiar words—component, port, junction, protocol, template—while retaining the categorical model in the kernel and verification tooling.

## 9.11 Verdict

Use ports, junctions, and wiring diagrams as the **composition layer**. Use structured-cospan or hypergraph semantics where it yields actual coherence and colimit results.

---

# 10. Architecture family D: presheaves and categorical data

The fourth alternative models the entire system as a **typed instance over a schema**.

This is more radical than using a graph store. It treats schema mappings, plugin composition, and data migration as first-class functorial operations.

## 10.1 Schema as a small category

A simplified presentation schema might contain objects:

```text
Entity
Occurrence
PresentationType
Component
Port
Protocol
Junction
Command
Actor
```

and arrows:

```text
Occurrence --denotes--> Entity
Occurrence --presentedAs--> PresentationType
Port --owner--> Component
Port --protocol--> Protocol
Port --attachedTo--> Junction
CommandInstance --actor--> Actor
```

Equations can express path constraints.

An instance assigns a set to every object and a function to every arrow while respecting the equations.

## 10.2 Typed graphs as functorial instances

Ordinary typed graphs are special cases of this construction. The benefit is a mature mathematical account of:

- limits and colimits;
- schema migration;
- natural transformations between instances;
- queries as structured mappings;
- integrity constraints.

## 10.3 Data migration functors

A schema mapping can induce canonical migrations often written as:

- \(\Delta\): pull data back along a schema map;
- \(\Sigma\): left-adjoint migration, often merging or freely extending;
- \(\Pi\): right-adjoint migration, often matching or aggregating compatible structure.

For PBUI, this could support:

- upgrading a plugin schema;
- mapping legacy presentation records to a new world schema;
- importing a workspace vocabulary;
- projecting a large system into a product-specific view;
- adapting a generic port protocol to a specialized one.

## 10.4 Colimits are pointwise

Functor categories have limits and colimits computed pointwise when the target category does. This makes plugin and workspace composition mathematically tractable.

However, “pointwise colimit” does not automatically preserve application invariants. The result may need semantic closure or validation after gluing. This is one reason to combine categorical data with the reflection described later.

## 10.5 Schema evolution

Current PBUI types are TypeScript declarations and runtime descriptor maps. A categorical schema can be versioned as data. Migrations become explicit, composable artifacts rather than one-off deserializers.

A workspace bundle could record:

```text
schema version
instance data
plugin schema imports
migration path
proof/check status
```

## 10.6 Identity

Entity identity can be represented by keys and key constraints rather than by structural equality. A schema can distinguish:

- nominal identity;
- occurrence identity;
- aliases;
- equivalence relations;
- copied entities.

A coequalizer should be used only when the product truly intends to quotient identities. Most UI links should connect entities through a junction rather than identify the entities themselves.

## 10.7 What this architecture solves well

It is strong for:

- explicit schemas;
- plugin composition;
- persistence and migration;
- typed graph validation;
- reusable query infrastructure;
- structural interoperability;
- mathematically controlled colimits.

## 10.8 What it does not solve by itself

A Set-valued instance does not specify:

- recursive eligibility rules;
- command effects;
- temporal behavior;
- bidirectional editing;
- execution performance;
- React rendering.

## 10.9 Main risk

This approach can impose high conceptual and tooling cost. It is justified when the system is expected to have:

- many independently developed plugins;
- long-lived persisted workspaces;
- multiple execution environments;
- significant schema evolution;
- formal import/export requirements.

For a small local UI library, it may be excessive.

## 10.10 Verdict

Use a categorical or typed-instance model as the **world representation and schema-evolution foundation** if PBUI is intended to become an extensible platform. Keep the public API domain-specific.

---

# 11. Architecture family E: typed graph rewriting

The fifth alternative makes **state transitions on a typed attributed graph** the central abstraction.

This is a natural fit because the proposed world already contains entities, occurrences, views, placements, ports, junctions, documents, and ownership edges.

## 11.1 State as a typed graph

A state contains nodes such as:

```text
View
Placement
Component
Port
Junction
GraphicDocument
Workspace
Actor
```

and typed edges such as:

```text
Placement --places--> View
View --instanceOf--> Component
Port --belongsTo--> View
Port --attachedTo--> Junction
Junction --carries--> GraphicDocument
View --memberOf--> Workspace
```

Attributes contain labels, revisions, geometry, and product data.

## 11.2 Rewrite rules

A connect rule can be described by left, interface, and right graphs:

```text
Left:
  sourcePort attachedTo sourceJunction
  targetPort attachedTo targetJunction

Preserve:
  sourcePort
  targetPort
  sourceJunction

Right:
  sourcePort attachedTo sourceJunction
  targetPort attachedTo sourceJunction
```

Additional policy decides what happens to an empty target junction.

A fork rule can:

- match a workspace and its reachable graph;
- preserve referenced immutable plugin definitions;
- copy selected view, binding, and document nodes;
- generate fresh nominal IDs;
- rewire internal references to the copies;
- leave external source references shared or copied according to policy.

## 11.3 Structural invariants

Examples include:

```text
Every placement places exactly one view.
Every port belongs to exactly one component instance.
Every analysis junction carries at most one GraphicDocument.
Every attached port has a protocol compatible with its junction.
No workspace-owned view is reachable from two independent workspace forks unless explicitly mirrored.
```

A rewrite can be checked locally for invariant preservation. Global reachability constraints may require auxiliary analysis.

## 11.4 Adhesive categories

Adhesive categories provide a setting in which pushouts along monomorphisms behave like well-controlled graph gluing. They support general results about double-pushout rewriting, parallel independence, and local confluence.

Typed graphs and many presheaf categories fit this style of reasoning.

This gives meaning to questions such as:

- Do two independent commands commute?
- Can two rewrites be applied in parallel?
- Which critical pairs expose conflicts?
- Is undo a valid inverse rule under a recorded match?

## 11.5 Negative application conditions

A command often requires absence:

```text
Connect only if the ports are not already in the same junction.
Delete a document only if no protected reference remains.
Create a singleton app only if none exists.
```

Graph transformation systems can attach negative application conditions to rewrite rules. These require more care than positive matching and affect concurrency results.

## 11.6 Transactions and effects

The rewrite describes the pure state transition. External effects are interpreted after or around it:

```text
persist workspace
start analysis execution
cancel stale request
emit audit record
announce accessibility update
```

A transaction handler can stage the rewrite, validate postconditions, commit the graph, and then execute idempotent effects with revision tokens.

## 11.7 Undo

Generic undo is difficult when later commands depend on changed state. A rewrite system can nevertheless record:

- the rule ID;
- the match;
- deleted subgraph;
- created IDs;
- causal revision.

An inverse command can be generated for locally reversible rules and rejected when its preconditions no longer hold.

## 11.8 What this architecture solves well

It is strong for:

- link and unlink;
- deletion;
- fork and duplicate;
- structural invariants;
- graph-aware persistence;
- command conflict analysis;
- precise undo records.

## 11.9 What it does not solve by itself

A graph rewrite system does not provide:

- a convenient interactive command language;
- derived eligibility closure;
- view-update laws;
- efficient rendering;
- external-effect semantics.

## 11.10 Main risk

A fully general graph-rewrite DSL can be difficult to author and optimize. The public API should expose product operations such as `connect`, `detach`, `forkSubgraph`, and `deleteSubject`, while compiling them to a small verified rewrite IR.

## 11.11 Verdict

Use typed graph rewriting as the **pure transition semantics** for structural commands.


# 12. Architecture family F: lenses and bidirectional transformations

The sixth alternative makes **lawful bidirectional views** the center of the API.

This family is especially relevant to Datalab because chart, table, pipeline, and encoding applications are not merely readers. Several are editors of different projections of one `GraphicDocument`.

## 12.1 The view-update problem

Suppose an encoding editor displays:

```ts
{
  x: { field: "region", type: "nominal" },
  y: { field: "population_total", type: "quantitative" },
}
```

This is a projection of a larger document containing sources, transforms, views, parameters, scales, and metadata.

When the user changes `x`, the system must update the source document while preserving unrelated information. Writing `get` is easy. Writing a predictable `put` is the hard part.

## 12.2 Basic lens structure

A lens can be modeled as:

```ts
// Illustrative API
interface Lens<S, V> {
  get(source: S): V;
  put(source: S, updatedView: V): S;
}
```

For proof and tooling, the implementation should not merely claim lawfulness. A lens should be built from known combinators or carry explicit proof obligations.

## 12.3 Standard laws

For source \(s\) and views \(v,v'\):

### GetPut

\[
\operatorname{put}(s,\operatorname{get}(s))=s.
\]

A no-op edit does not rewrite IDs or erase hidden information.

### PutGet

\[
\operatorname{get}(\operatorname{put}(s,v))=v.
\]

The requested view edit is observable after update.

### PutPut

\[
\operatorname{put}(\operatorname{put}(s,v),v')
=
\operatorname{put}(s,v').
\]

The last update determines the current view.

These laws may need adaptation for validation, generated defaults, partiality, or revision tracking.

## 12.4 Partial and validated lenses

A Datalab edit may fail because:

- a field does not exist;
- an encoding is incompatible with a mark;
- a pipeline output schema changed;
- the document revision is stale.

A practical lens returns a result:

```ts
// Illustrative API
interface ValidatedLens<S, V, E> {
  get(source: S): V;
  put(source: S, updatedView: V): Result<S, E>;
}
```

The laws are then stated on successful updates or in an appropriate category of partial maps.

## 12.5 Symmetric lenses

Sometimes neither side is the canonical source. Two independently evolving structures are synchronized through a complement or correspondence state. This is relevant to:

- local and remote workspace replicas;
- a UI authoring document and a server execution plan;
- two schema versions;
- imported and native workspace formats.

Symmetric lenses are more appropriate than pretending one representation is always primary.

## 12.6 Delta lenses

For performance, an edit can be represented as a delta rather than a full replacement:

```text
set encoding.x.field = "city"
rename output population_total → total_population
insert transform after step-3
```

A delta lens translates view deltas to source deltas. This aligns well with incremental execution and precise undo.

## 12.7 Lenses and component ports

A component port can expose not only a subject protocol but also a lawful projection:

```ts
// Illustrative API
const EncodingEditor = component("encoding", {
  ports: {
    analysis: duplex(AnalysisProtocol, {
      view: encodingLens,
    }),
  },
});
```

The component edits the view type. The junction carries the source type. The lens mediates updates.

This is more precise than saying that every document-bound app receives the entire document and dispatches arbitrary document-editing verbs.

## 12.8 What this architecture solves well

It is strong for:

- predictable editor behavior;
- preserving hidden state;
- composition of projections;
- synchronization between representations;
- generating tests from laws;
- translating small edits;
- separating authoring views from canonical models.

## 12.9 What it does not solve by itself

Lenses do not determine:

- which occurrence is selectable;
- how components are linked;
- which commands exist;
- how permissions work;
- how asynchronous effects are handled;
- how a network of many views is saturated.

## 12.10 Main risk

A manually written pair of `get` and `put` functions can violate the laws while still having the TypeScript type `Lens<S,V>`. The architecture gains real value only if:

- common lenses are generated or composed from lawful primitives;
- law checks are part of CI;
- partiality and normalization are explicit;
- foreign lenses are marked as assumptions.

## 12.11 Verdict

Use lenses as the **editable projection layer**, especially for `GraphicDocument` applications. Do not use them as the entire presentation kernel.

---

# 13. Architecture family G: coalgebraic and temporal behavior

The seventh alternative makes the UI a **reactive state machine observed through behavior**.

This addresses questions that static schemas, fixed points, and graph rewrites do not answer alone: what can happen over time, which event sequences are legal, and when two implementations behave the same.

## 13.1 A UI as a coalgebra

A simplified deterministic system can be represented as:

\[
\delta : S \times E \to O \times S,
\]

where:

- \(S\) is state;
- \(E\) is an event or command;
- \(O\) is an observation, result, or emitted effect.

Equivalently, curry it into a coalgebra:

\[
S \to (O\times S)^E.
\]

Nondeterminism, failure, asynchronous effects, and probability lead to richer behavioral functors.

## 13.2 Behavior rather than representation

Two internal implementations can be considered equivalent when no allowed observer can distinguish their event traces. Coalgebraic bisimulation gives a proof technique for such behavioral equivalence.

This matters for migrations:

- old registry implementation versus new fixed-point engine;
- eager versus incremental saturation;
- local versus remote command handler;
- direct reducer versus compiled graph rewrite.

A refinement test can compare externally visible behavior rather than internal data layout.

## 13.3 Safety and liveness

Temporal properties include:

### Safety

“Something bad never happens.”

```text
A stale analysis result is never committed to a rebound view.
A command never mutates an entity without the required capability.
An exclusive port is never connected to two junctions.
```

### Liveness

“Something good eventually happens.”

```text
Every accepted command eventually succeeds, fails, or is cancelled.
Every committed binding change eventually triggers a fresh analysis result.
Keyboard selection can eventually reach every pointer-selectable occurrence.
```

## 13.4 TLA+ as a companion model

TLA+ is appropriate for a compact model of:

- base state variables;
- link, unlink, rebind, execute, complete, cancel, persist, and undo actions;
- revisions and request tokens;
- fairness assumptions;
- safety invariants;
- liveness properties.

The TypeScript kernel should not attempt to embed full temporal logic. It should export command schemas and state variables in a form from which a small TLA+ model can be maintained.

## 13.5 Event sourcing

An event log records accepted semantic commands or committed transitions:

```text
WorkspaceCreated
ViewAdded
PortsConnected
BindingRebound
AnalysisForked
EncodingChanged
WorkspaceForked
```

Benefits include:

- deterministic replay;
- auditability;
- debugging;
- temporal queries;
- rebuilding materialized views;
- synchronization.

The log should record semantic events, not raw pointer movements or every Redux action.

## 13.6 Commands versus events

A command is a request that may fail. An event records a committed fact about what happened.

```text
Command: ConnectPorts(source, target)
Event: PortsConnected(source, target, junction, revision)
```

Keeping these distinct is important for retries and distributed operation.

## 13.7 Coinduction and streams

Long-running input contexts, analysis result streams, and collaborative event feeds can be modeled coinductively. The system can reason about infinite behavior without constructing the complete trace.

This is conceptually useful, but most product verification will use transition invariants and model checking rather than hand-written coalgebraic proofs.

## 13.8 What this architecture solves well

It is strong for:

- concurrent protocols;
- stale-result prevention;
- behavioral refinement;
- event sourcing;
- safety and liveness;
- replay and audit;
- equivalence of execution strategies.

## 13.9 What it does not solve by itself

A state-machine model does not provide:

- a schema for entities and ports;
- derived selection logic;
- component colimits;
- lawful view updates;
- efficient query maintenance.

## 13.10 Main risk

A temporal model can drift from implementation. The command IR and event vocabulary should be generated from or shared with the runtime schema wherever practical.

## 13.11 Verdict

Use coalgebraic and temporal models as the **behavioral semantics and verification companion**.

---

# 14. Architecture family H: incremental and differential execution

The eighth alternative makes **change propagation** the primary implementation model.

This is essential for performance, but it should be treated as a compilation target for the semantic layers rather than as the definition of presentation meaning.

## 14.1 The performance problem

A presentation-based system can derive many values from each state change:

- eligible occurrences for active contexts;
- available command instances;
- conversion paths;
- link compatibility;
- ownership and dependency closure;
- affected applications;
- rendered models;
- chart data and table rows.

Recomputing every query from scratch on each render is not viable at scale.

## 14.2 Incremental view maintenance

Let a query be \(Q(I)\). Given an input change \(\Delta I\), an incremental evaluator computes \(\Delta Q\) such that:

\[
Q(I\oplus\Delta I)
=
Q(I)\oplus\Delta Q(I,\Delta I).
\]

The correctness criterion is equality with from-scratch recomputation.

## 14.3 Semi-naive fixed-point evaluation

For recursive rules, semi-naive evaluation propagates only newly derived facts through each round. It avoids reproducing derivations already known.

When an occurrence mounts, only rules depending on occurrence presence, its entity, and the active contexts need work. When a binding changes, only subject-dependent queries should invalidate.

## 14.4 Differential dataflow and DBSP

Differential dataflow represents collections with differences and maintains iterative computations under change. DBSP provides an algebraic account of incrementalizing rich database programs, including recursion and aggregation.

These systems suggest implementation techniques for OPK:

- represent base and derived relations as indexed collections;
- propagate weighted positive and negative deltas;
- maintain recursive strata incrementally;
- share arrangements among queries;
- batch React mount/unmount changes;
- retain a declarative query plan independent of execution strategy.

## 14.5 Self-adjusting computation

Self-adjusting computation records dynamic data and control dependencies during execution. When inputs change, it re-executes only affected portions.

This is useful for foreign or higher-order computations that are difficult to compile to relational algebra, provided their reads are instrumented.

## 14.6 Demand-driven computation

Not every derived relation must be fully materialized. A demand-driven engine can activate rules and indexes only for:

- the current input context;
- visible surfaces;
- open action menus;
- active link operations;
- subscribed application ports.

This avoids global closure over irrelevant product vocabulary.

## 14.7 Stable names

Incremental systems need stable identities for cached computations and facts. The enhanced repository’s semantic identity domains are directly useful.

However, a cache key must include all semantic dependencies. An entity key alone is insufficient when eligibility also depends on actor, context, subject revision, and permissions.

## 14.8 Incremental rendering

React should receive stable `OccurrenceModel` and `ActionModel` values keyed by semantic occurrence identity. It should not be asked to rediscover semantic sensitivity during reconciliation.

A possible pipeline is:

```text
base graph delta
  → relational closure delta
  → command/query result delta
  → render-model delta
  → React external-store notification
```

## 14.9 What this architecture solves well

It is strong for:

- large occurrence counts;
- recursive selector logic;
- shared query work;
- precise invalidation;
- rapidly changing bindings;
- interactive chart and table updates;
- equivalence checks against batch evaluation.

## 14.10 What it does not solve by itself

A dataflow graph can efficiently execute a bad or ambiguous semantics. It does not determine:

- which facts are authoritative;
- which rules are valid;
- what a link means;
- what commands are allowed;
- how effects are handled.

## 14.11 Main risk

Incremental runtimes can dominate the architecture and leak operational constraints into the API. OPK should specify batch semantics first and treat incremental evaluation as a correctness-preserving compilation.

## 14.12 Verdict

Use incremental and differential computation as the **execution substrate** for rules, queries, and render models.

---

# 15. Architecture family I: semilattices, CRDTs, and coordination

The ninth alternative makes **monotone replicated state** central.

This becomes important if workspaces, links, selections, pipelines, and presentations are edited concurrently by several clients.

## 15.1 Join-semilattice state

A state-based CRDT uses a partial order and a join operation. Replicas merge by least upper bound:

\[
s_{merged}=s_1\vee s_2.
\]

Updates are inflationary, and merge is associative, commutative, and idempotent. Under the CRDT assumptions, replicas converge.

## 15.2 Naturally monotone UI facts

Some facts fit this model well:

- an append-only audit event;
- a set of observed occurrence IDs within a trace;
- a set of acknowledged capabilities;
- immutable content-addressed document revisions;
- a grow-only set of analysis results keyed by request ID.

## 15.3 Non-monotone UI operations

Many important commands are not simple joins:

- unlink a port;
- delete a view;
- revoke permission;
- replace the subject of an exclusive junction;
- undo a pipeline edit;
- choose one winner among competing bindings.

These require specific CRDT designs, tombstones, causal metadata, arbitration, or coordination. A local monotone rule engine does not make the distributed mutation model coordination-free.

## 15.4 CALM as a design diagnostic

The CALM principle connects logical monotonicity with coordination-free consistency. It is useful as a question:

> Can this conclusion remain valid as more information arrives?

If yes, it may be derived without coordination. If no, some boundary of coordination or finality is required.

For example:

- “this candidate has at least one valid derivation” is monotone;
- “this is the unique cheapest candidate” may change when another candidate arrives;
- “no other user has linked this exclusive port” is non-monotone under incomplete information.

## 15.5 Event-log and CRDT combination

A practical collaborative architecture may use:

- immutable, causally ordered events;
- CRDTs for text, sets, and maps;
- server-coordinated commands for exclusive structural changes;
- deterministic derived closure at each replica;
- revision or vector-clock guards for analysis execution.

## 15.6 Shared selection

Not every linked UI state should be collaborative. A selection can be:

- private local focus;
- shared group selection;
- presenter-controlled broadcast state;
- durable workspace state.

The port protocol should declare replication and persistence mode.

## 15.7 What this architecture solves well

It is strong for:

- offline edits;
- replicated convergence;
- conflict-free sets and maps;
- append-only traces;
- explicit coordination analysis.

## 15.8 What it does not solve by itself

CRDTs do not define:

- presentation eligibility;
- component interfaces;
- action semantics;
- view-update laws;
- local render performance.

## 15.9 Main risk

Applying a generic CRDT map to a graph of exclusive references can produce states that converge but violate product invariants. Convergence is not semantic validity.

## 15.10 Verdict

Use semilattices and CRDTs as an **optional replication layer**, selected per protocol and command. Do not make every local state value a CRDT.

---

# 16. Architecture family J: constraint and proof-carrying APIs

The tenth alternative makes **constraints, evidence, and proof obligations** visible in the application API.

This is less a separate mathematical semantics than a discipline that can organize the other families.

## 16.1 From Boolean predicates to judgments

A traditional selector returns `true` or `false`.

A proof-carrying selector returns:

```ts
// Illustrative API
type Eligibility =
  | {
      ok: true;
      occurrence: OccurrenceId;
      entity: EntityRef;
      derivation: Derivation;
      dependencies: readonly FactKey[];
      cost: number;
    }
  | {
      ok: false;
      reasons: readonly FailedPremise[];
    };
```

This enables:

- “why can I not select this?” UI;
- stable invalidation;
- audit logs;
- test assertions on rule choice;
- safe command parameterization.

## 16.2 Preconditions and postconditions

A command schema can declare:

```text
requires P(state, parameters)
transition R(state, parameters, nextState)
ensures Q(state, parameters, nextState)
```

The runtime checks `requires`. The verifier attempts to establish:

\[
Invariant(s)\land P(s,p)\land R(s,p,s')
\implies
Invariant(s')\land Q(s,p,s').
\]

The status can be:

```text
proved
bounded-checked
property-tested
runtime-checked
assumed
```

## 16.3 Refinement and capability types

A parameter may be more precise than its base sort:

```text
Port<AnalysisProtocol> & Unlocked & Visible
GraphicDocument & CompilesSuccessfully
Field & BelongsTo<DocId> & Quantitative
```

TypeScript can represent brands, but the refinements are established by runtime evidence. A `Refined<T,P>` value should carry or reference the judgment that established `P`.

## 16.4 Generated models

The kernel can emit:

- Alloy signatures and facts for bounded structural analysis;
- TLA+ state variables and actions for temporal analysis;
- SMT formulas for local command obligations;
- Lean or Rocq definitions for kernel metatheorems;
- property-test generators for laws and round trips.

The generated artifact should be small and readable enough to inspect.

## 16.5 Proof irrelevance versus explanation relevance

For execution, two proofs of the same eligibility proposition may be interchangeable. For explanation and ranking, the derivation path matters.

The system should distinguish:

- **logical validity**: at least one derivation exists;
- **operational witness**: which conversion or command instance to use;
- **explanation provenance**: which derivation to display;
- **ranking**: which witness has minimum cost or highest priority.

## 16.6 Trusted computing base

The proof-oriented kernel should be small:

- schema checker;
- expression type checker;
- rule evaluator;
- derivation checker;
- rewrite matcher and validator;
- serializer;
- effect capability dispatcher.

React components, DuckDB, network clients, and opaque product algorithms remain outside the trusted core.

## 16.7 What this architecture solves well

It is strong for:

- explanations;
- auditability;
- local verification;
- generated tooling;
- explicit assumptions;
- safer command execution;
- precise developer diagnostics.

## 16.8 What it does not solve by itself

A proof-carrying API needs an underlying semantics. Without one, evidence becomes a manually constructed token with no meaning.

## 16.9 Main risk

The API can become ceremony-heavy. Evidence should normally be generated by the kernel and passed implicitly through query and command results. Application code should request explanations only when needed.

## 16.10 Verdict

Use evidence and proof obligations as a **cross-cutting API discipline** over the relational, graph, command, and lens layers.

---

# 17. Comparison of the architecture families

No family covers the complete problem. The table below summarizes their natural domain.

| Family | Semantic center | Best proof principle | Strongest PBUI use | Main deficiency |
|---|---|---|---|---|
| Algebraic effects | Inductive interaction program | Structural induction; handler homomorphism | Multi-step commands, cancellation, interpreters | Does not derive eligibility or compose ports |
| Fixed-point relations | Least model of facts and rules | Lattice theory; induction on derivations | Selectors, actions, conversions, permissions, explanation | Non-monotone choice and mutation require layers |
| Cospans / wiring | Open components with boundaries | Universal properties; coherence | Linked views, templates, component composition | Does not define commands or editing |
| Presheaf / categorical data | Typed instance over schema | Functoriality; adjunctions; pointwise colimits | Schema, plugins, migration, persistence | High conceptual cost; no behavior by itself |
| Graph rewriting | Typed graph transitions | Invariant preservation; critical-pair analysis | Link, unlink, fork, delete, duplicate | Rule authoring and query semantics are separate |
| Lenses / BX | Lawful source-view relation | Equational laws; compositionality | Pipeline and encoding editors | Not a selection or command system |
| Coalgebra / temporal | Observable transition behavior | Coinduction; temporal logic | Concurrency, stale results, replay | Does not provide static world semantics |
| Incremental dataflow | Deltas and dependency graph | Equivalence to batch semantics | Performance and live recomputation | Executes semantics but does not define it |
| CRDT / semilattice | Monotone replicated state | Convergence by join laws | Collaboration and offline state | Deletion and exclusivity need special treatment |
| Proof-carrying constraints | Judgments and obligations | Derivation checking; model checking | Explanation and verified commands | Needs one or more underlying semantics |

## 17.1 Three possible overall strategies

### Strategy 1: choose one family as universal

Examples include “everything is Datalog,” “everything is a graph rewrite,” or “everything is an effect.”

This has conceptual uniformity but forces several problems into unnatural encodings.

### Strategy 2: retain the current object registry and borrow techniques

This is the smallest migration. Add more selector combinators, port descriptors, graph utilities, and tests.

It is pragmatic but does not produce one inspectable semantic core.

### Strategy 3: use a small layered kernel

Use each structure for the role matching its proof principle, with explicit translations between layers.

This study recommends Strategy 3.

## 17.2 The required discipline

A layered architecture can become incoherent if every layer has its own identity and truth. The synthesis needs:

- one canonical world schema;
- one base-state instance;
- one command and event vocabulary;
- generated or checked translations;
- batch semantics before optimization;
- explicit boundaries for foreign code;
- stable IDs shared across interpreters.

The following sections define that synthesis.


# 18. Recommended synthesis: the Open Presentation Kernel

The recommended architecture is a layered semantic kernel named **Open Presentation Kernel**.

“Open” has three meanings:

1. components have exposed boundaries and can be composed;
2. plugins may extend schemas, rules, commands, and renderers;
3. interactions may remain partially specified until visible entities supply parameters.

“Kernel” means that it does not own the full UI framework. React, Redux, DuckDB, persistence, networking, and product components remain interpreters or clients.

## 18.1 The layers

OPK has eight semantic layers.

### Layer 1: schema

Declares:

- entity sorts;
- relations and functional arrows;
- keys and identity domains;
- component types;
- protocols and ports;
- command and event schemas;
- external effect signatures;
- integrity constraints.

### Layer 2: base world

Contains authoritative state:

- application entities;
- component instances;
- visible occurrences;
- port-junction connections;
- subjects carried by junctions;
- actor capabilities;
- workspace membership;
- pending operations and revisions.

### Layer 3: derived closure

A rule theory derives:

- subtype closure;
- occurrence eligibility;
- command applicability;
- conversion reachability;
- ownership;
- compatibility;
- affected components;
- diagnostic and explanation facts.

### Layer 4: open composition

A workspace is a typed incidence graph or wiring diagram of components, ports, and junctions. Its mathematical semantics is given by a colimit-style assembly in the chosen category of typed instances.

### Layer 5: commands and rewrites

Commands match evidence-backed parameters, apply pure typed graph rewrites, and produce semantic events.

### Layer 6: effects and handlers

External operations are algebraic effects interpreted by handlers:

- persistence;
- analysis execution;
- network access;
- focus and announcement;
- telemetry;
- file or clipboard access.

### Layer 7: projections and renderers

Queries and lenses produce render models and editable views. React renders them and reports occurrence geometry and lifecycle changes.

### Layer 8: incremental runtime

Indexes, semi-naive evaluation, differential updates, demand tracking, and memoization implement the batch semantics efficiently.

## 18.2 The semantic flow

```text
plugin schemas + product schema
          ↓
     normalized schema Σ
          ↓
 authoritative base instance I
          ↓
  least fixed-point closure CΓ(I)
          ↓
 queries, judgments, command instances
          ↓
 render models and interaction programs
          ↓
 React / headless / remote handlers
          ↓
 evidence-backed command
          ↓
 typed graph rewrite I → I′ + semantic event
          ↓
 external effects and incremental reclosure
```

## 18.3 Why the derived world is separate

Derived facts should not be stored as independent mutable truth.

For example, do not store all of these as unrelated state:

```text
view.currentDocumentId
tile.isLinked
linkGroup.memberViewIds
chart.activeDocument
pipeline.activeDocument
encoding.activeDocument
```

Store:

```text
attachedTo(port, junction)
carries(junction, document)
```

Derive:

```text
observes(view, document)
linked(viewA, viewB)
linkGroupOf(view, junction)
```

This reduces synchronization bugs and makes explanations possible.

## 18.4 Why commands change only base facts

A command should update authoritative graph structure. The fixed-point engine then retracts and derives dependent facts.

This avoids commands that manually maintain every denormalized cache.

## 18.5 Why React is not the semantic core

React is excellent for:

- component composition;
- DOM and SVG rendering;
- lifecycle and local ephemeral state;
- accessibility attributes;
- reconciliation.

It is not the right owner for:

- semantic equality;
- command applicability;
- conversion planning;
- persistent link topology;
- proof evidence;
- remote command semantics.

OPK presents React with stable values and callbacks generated from the semantic runtime.

## 18.6 Why this is not “category theory everywhere”

Each categorical construction has a limited purpose:

- initial algebras: syntax and induction;
- free constructions: extensible command/effect terms;
- reflection: semantic saturation;
- colimits: open-system composition;
- adhesive pushouts: graph rewriting;
- final coalgebras: behavior and coinduction;
- Kan extensions: schema migration where used.

Ordinary maps, arrays, sets, and indexes can implement the finite runtime.

---

# 19. The formal world model

This section gives a more precise candidate semantics. It is intentionally abstract enough to support several implementations.

## 19.1 Schema \(\Sigma\)

Let \(\Sigma\) be a finite typed schema. It contains sorts such as:

\[
\begin{aligned}
&\mathsf{Entity},\mathsf{Occurrence},\mathsf{PType},\mathsf{Context},\\
&\mathsf{Component},\mathsf{Port},\mathsf{Protocol},\mathsf{Junction},\\
&\mathsf{Command},\mathsf{CommandInstance},\mathsf{Actor},\mathsf{Capability},\\
&\mathsf{Workspace},\mathsf{Surface},\mathsf{Effect},\mathsf{Event}.
\end{aligned}
\]

Product schemas extend `Entity` with sorts such as:

\[
\mathsf{GraphicDocument},\mathsf{Field},\mathsf{PipelineStep},\mathsf{Source},\mathsf{SelectionSet}.
\]

The schema declares relations including:

\[
\begin{aligned}
&\mathsf{denotes}:\mathsf{Occurrence}\times\mathsf{Entity},\\
&\mathsf{presentedAs}:\mathsf{Occurrence}\times\mathsf{PType},\\
&\mathsf{visibleOn}:\mathsf{Occurrence}\times\mathsf{Surface},\\
&\mathsf{requests}:\mathsf{Context}\times\mathsf{Goal},\\
&\mathsf{subtype}:\mathsf{PType}\times\mathsf{PType},\\
&\mathsf{owns}:\mathsf{Entity}\times\mathsf{Entity},\\
&\mathsf{hasPort}:\mathsf{Component}\times\mathsf{Port},\\
&\mathsf{speaks}:\mathsf{Port}\times\mathsf{Protocol},\\
&\mathsf{attachedTo}:\mathsf{Port}\times\mathsf{Junction},\\
&\mathsf{carries}:\mathsf{Junction}\times\mathsf{Entity},\\
&\mathsf{holds}:\mathsf{Actor}\times\mathsf{Capability}.
\end{aligned}
\]

A concrete implementation may represent functional relations as fields and many-to-many relations as indexed tables. The formal model treats them uniformly enough for query and migration semantics.

## 19.2 Base instances

A base instance \(I\in\mathbf{Inst}_\Sigma\) assigns finite sets and relations satisfying schema-level constraints.

Base facts are those directly authored or observed:

- an occurrence mounted;
- a port attached;
- a document exists;
- an actor holds a capability;
- a command is pending;
- a component is in a workspace.

## 19.3 Derived relations

Let \(\Gamma\) be a typed rule theory. Its relation symbols are divided into:

- extensional relations, supplied by \(I\);
- intensional relations, derived by rules.

Representative intensional relations are:

```text
subtypeStar(actual, expected)
eligible(context, occurrence)
canSatisfy(context, occurrence, witness, cost)
available(commandSchema, context, occurrence, instance)
compatible(portA, portB)
observes(component, subject)
affected(commandInstance, component)
invalid(entity, diagnostic)
```

## 19.4 The immediate-consequence operator

Given a candidate fact set \(X\), \(T_\Gamma(X)\) contains the heads of all rule instances whose premises hold in \(X\).

The inflationary closure operator for base instance \(I\) is:

\[
F_I(X)=I\cup X\cup T_\Gamma(X).
\]

Including \(X\) makes inflationarity explicit. For positive rules, \(F_I\) is monotone.

The saturated world is:

\[
C_\Gamma(I)=\mu F_I.
\]

## 19.5 Judgments and evidence

A derived tuple is accompanied by a derivation node:

```ts
// Illustrative semantic IR
interface DerivationNode {
  id: DerivationId;
  conclusion: GroundAtom;
  ruleId: RuleId | "base";
  premises: readonly DerivationId[];
  assumptions: readonly AssumptionId[];
  annotation?: SemiringValue;
}
```

The kernel checks that:

- the rule exists;
- substitutions are well typed;
- each premise concludes the required atom;
- the instantiated head equals the conclusion;
- annotations compose according to the relation’s evaluation algebra.

## 19.6 Identity

Every nominal entity has a typed key:

```text
Key(Field) = (DocumentId, FieldName)
Key(GraphicDocument) = DocumentId
Key(Occurrence) = OccurrenceId
Key(Port) = (ComponentInstanceId, PortName)
Key(Junction) = JunctionId
```

Equality is defined per sort. Cross-sort key equality is meaningless unless an explicit coercion or shared identity domain is declared.

Aliases are represented explicitly:

```text
alias(entityA, entityB)
```

If the application truly wants quotient identity, it may derive or materialize equivalence classes. Most commands should preserve nominal identity and connect entities rather than quotient them.

## 19.7 Integrity constraints

Constraints include key and cardinality rules:

```text
Each occurrence denotes exactly one entity.
Each port belongs to exactly one component instance.
An exclusive junction carries at most one subject.
A port attaches to at most one junction unless its protocol permits fan-out.
Every attached port and junction have compatible protocols.
Every placement belongs to one workspace and places one logical view.
```

Constraint checking occurs:

- when loading an instance;
- before and after a rewrite;
- during development after each command;
- in production according to cost and risk.

## 19.8 Protocols

A protocol is not only a value type. It declares behavioral and ownership expectations:

```ts
// Illustrative model
interface Protocol<T> {
  id: ProtocolId;
  subjectSort: Sort<T>;
  direction: "in" | "out" | "duplex";
  multiplicity: "one" | "optional" | "many";
  sharing: "shared-reference" | "copy-on-connect" | "event-stream";
  persistence: "ephemeral" | "workspace" | "durable";
  replication: "local" | "broadcast" | "collaborative";
}
```

Compatibility is a derived relation, not JavaScript structural assignability.

## 19.9 Occurrences

An occurrence has semantic and geometric parts:

```ts
interface OccurrenceRecord {
  id: OccurrenceId;
  entity: EntityRef;
  presentationType: PresentationTypeId;
  surface: SurfaceId;
  ownerComponent?: ComponentInstanceId;
  interactionModes: readonly InteractionMode[];
  geometryHandle?: GeometryHandle;
  lifecycleRevision: number;
}
```

Geometry can remain in a specialized index. The world contains the stable handle and semantic metadata.

## 19.10 Contexts as entities

An active input context is itself a world entity. It has:

- owner interaction program;
- actor;
- goal formula;
- scope of surfaces;
- cardinality;
- ranking algebra;
- cancellation token;
- revision.

This allows several contexts when policy permits and makes context state visible to debugging and remote handlers.

---

# 20. Fixed-point closure as a reflection

The most important categorical connection in the proposal is between fixed-point saturation and colimits.

## 20.1 Saturated instances

Call an instance \(S\) **\(\Gamma\)-saturated** when applying the rule closure adds no new facts:

\[
C_\Gamma(S)=S.
\]

Let \(\mathbf{Sat}_\Gamma\) be the full subcategory of saturated instances inside \(\mathbf{Inst}_\Sigma\).

## 20.2 Least saturated extension

For every base instance \(I\), suppose \(C_\Gamma(I)\) is:

1. saturated;
2. equipped with an inclusion or structure-preserving map
   \(\eta_I:I\to C_\Gamma(I)\);
3. least among saturated extensions of \(I\).

“Least” means that for any saturated \(S\) and map \(f:I\to S\), there is a unique compatible map

\[
\bar f:C_\Gamma(I)\to S
\]

such that

\[
\bar f\circ\eta_I=f.
\]

Under these conditions, closure is left adjoint to inclusion:

\[
C_\Gamma \dashv J.
\]

## 20.3 Closure operator laws

On a poset of fact sets, the same structure appears as a closure operator:

### Extensive

\[
I\le C_\Gamma(I).
\]

### Monotone

\[
I\le I'\implies C_\Gamma(I)\le C_\Gamma(I').
\]

### Idempotent

\[
C_\Gamma(C_\Gamma(I))=C_\Gamma(I).
\]

These laws are directly testable in finite instances and provable for the kernel’s positive rule semantics.

## 20.4 Colimit preservation

Left adjoints preserve colimits. Therefore, for a diagram \(D:K\to\mathbf{Sat}_\Gamma\), its colimit in saturated models can be computed by:

1. forget saturation and form the raw colimit in \(\mathbf{Inst}_\Sigma\);
2. close the result under \(\Gamma\).

Formally:

\[
\operatorname{colim}_{\mathbf{Sat}_\Gamma}D
\cong
C_\Gamma\left(\operatorname{colim}_{\mathbf{Inst}_\Sigma}JD\right).
\]

## 20.5 Meaning for plugins

Suppose the core schema and two plugins contribute components and base facts. Their raw union may introduce new subtype paths, ownership relationships, conversions, or action applicability.

The workflow is:

```text
coproduct / pushout of declared instances
             ↓
          raw instance
             ↓
       semantic closure CΓ
             ↓
newly derived eligible occurrences, actions, and diagnostics
```

Plugin composition and semantic consequence remain separate operations with a precise relationship.

## 20.6 Meaning for linked workspaces

A chart component and table component are open instances with analysis ports. A junction instance connects them and carries a document.

Their raw colimit assembles the structural graph. Closure then derives:

```text
observes(chart, censusDocument)
observes(table, censusDocument)
linked(chart, table)
available(detach, chart.analysisPort)
```

## 20.7 Conditions and caveats

The reflection does not exist automatically for arbitrary PBUI behavior.

It is endangered by:

- arbitrary host-language predicates;
- rules that mint fresh nominal entities without a controlled free construction;
- unstratified negation;
- priority semantics that is not monotone;
- side effects during derivation;
- identity callbacks that change over time;
- non-functorial schema transformations.

The analyzable core must restrict these features or place them in explicit later strata.

## 20.8 A closure monad

An adjunction induces a monad. For a reflection, the monad is idempotent. Intuitively:

```text
close once = close completely
closing an already closed world changes nothing
```

This gives the fixed-point engine a categorical interpretation without changing its finite worklist implementation.

## 20.9 Why this connection is useful

It supports a practical modularity rule:

> Structural composition may happen locally and independently. Semantic closure is then applied uniformly, and no plugin manually patches every derived registry.

It also gives a testable architecture contract: the incremental closure of a composed world must equal the batch closure of the same raw colimit.

---

# 21. Transfinite construction and its practical boundary

The user explicitly raised transfinite induction and fixed-point iteration. This section states where they are meaningful and where they are not.

## 21.1 General monotone fixed points

Let \(L\) be a complete lattice and \(F:L\to L\) monotone. Knaster–Tarski guarantees a complete lattice of fixed points, including a least fixed point.

An ordinal chain can be defined by:

\[
X_0=\bot,
\]

\[
X_{\alpha+1}=F(X_\alpha),
\]

\[
X_\lambda=\bigvee_{\beta<\lambda}X_\beta.
\]

Because \(\bot\le F(\bot)\) and \(F\) is monotone, the chain is ascending. It eventually reaches a stationary stage in a set-sized lattice.

## 21.2 Invariant proof by transfinite induction

Suppose property \(P\) satisfies:

1. **Base:** \(P(\bot)\).
2. **Successor preservation:** \(P(X)\Rightarrow P(F(X))\).
3. **Limit closure:** for every ascending chain whose elements satisfy \(P\), the supremum also satisfies \(P\).

Then every stage \(X_\alpha\) satisfies \(P\), including the stabilized least fixed point.

For OPK, a candidate invariant might be:

```text
Every derived eligible occurrence denotes a well-typed entity
and has a finite derivation rooted in base facts or declared assumptions.
```

In the finite engine, ordinary induction over worklist additions is enough. The transfinite proof establishes the more general metatheorem.

## 21.3 Initial-algebra chains

For an endofunctor \(F\), the initial chain begins:

\[
0\to F0\to F^2 0\to F^3 0\to\cdots
\]

At a limit ordinal, take the colimit of the previous stages. Under appropriate preservation or accessibility assumptions, the chain stabilizes and yields an initial algebra.

This is relevant to:

- freely generated command syntax;
- recursive query syntax;
- plugin-combined effect signatures;
- open-ended term constructors;
- free completion of partial schemas.

For ordinary finite algebraic data types, the construction stabilizes in the familiar finite-tree union at \(\omega\). Transfinite machinery becomes relevant for more general functors and equations.

## 21.4 Limit stages are colimits

The requested connection between transfinite induction and colimits is exact:

\[
X_\lambda=\operatorname{colim}_{\beta<\lambda}X_\beta.
\]

To continue a structure through the limit stage, the relevant functor must preserve the colimit or satisfy another theorem providing the needed comparison map.

This is where category theory contributes substantive proof obligations:

- what category contains the stages?
- which colimits exist?
- does the endofunctor preserve the relevant chains?
- at what ordinal can stabilization be expected?

## 21.5 Runtime classifications

OPK should classify recursive computations into operational regimes.

### Finite relational closure

Conditions:

- finite active universe;
- finite relation arities;
- no fresh-name generation in rules;
- positive or stratified rule program.

Implementation:

- worklist or semi-naive iteration;
- guaranteed finite termination.

### \(\omega\)-continuous domain

Conditions:

- complete partial order;
- operator preserves suprema of increasing \(\omega\)-chains.

Implementation:

- ordinary Kleene iteration may converge at \(\omega\);
- practical evaluation still needs finite approximations or a symbolic solver.

### Infinite-height abstract domain

Conditions:

- monotone equations over intervals, schemas, costs, or other infinite domains;
- finite convergence not guaranteed.

Implementation:

- widening to reach a post-fixed point;
- narrowing to recover precision;
- explicit approximation status.

### General monotone operator

Semantics:

- transfinite least-fixed-point construction.

Implementation:

- do not attempt literal ordinal iteration in the browser;
- require a domain-specific solver, bound, abstraction, or offline proof.

### Non-monotone recursion

Semantics:

- no automatic least-model interpretation from monotonicity.

Implementation:

- reject;
- stratify;
- use a different semantics such as stable models;
- move the operation into command transition logic.

## 21.6 Fresh names

Commands create new views, junctions, and documents. Positive derivation rules should normally not mint fresh nominal identities, because repeated closure could create an unbounded chain.

Fresh names belong to explicit commands or free-construction stages with controlled universal semantics.

## 21.7 Widening is not user-visible truth

If an analysis uses widening, the result is generally an over-approximation or post-fixed point. The UI must label it accordingly. A proof-oriented architecture should not report an approximation as an exact derived fact.

## 21.8 Practical conclusion

Transfinite induction belongs in:

- kernel metatheory;
- free-construction proofs;
- general closure theorems;
- exported proof models.

Finite saturation, incremental worklists, and domain-specific solvers belong in the runtime.

---

# 22. Colimits, linking, and reusable workspaces

This section develops the composition model in product terms.

## 22.1 The category must be chosen

A useful choice is a category of finite typed attributed graphs or finite instances over schema \(\Sigma\), with structure-preserving maps.

Attributes such as labels and geometry require a disciplined treatment. Common options are:

- model attributes as nodes and arrows in the schema;
- use attributed C-sets with specified attribute algebras;
- keep opaque attributes outside the categorical core and require stable handles.

The last option is simplest for React geometry.

## 22.2 Components as open instances

A component instance \(X\) has a boundary \(B_X\) containing its exposed ports and a map:

\[
L(B_X)\to X.
\]

A complete open component may be represented by a structured cospan when inputs and outputs are separated, or by a typed open hypergraph when a more symmetric connection model is desired.

## 22.3 Junctions as explicit mediators

Rather than quotienting ports directly, introduce junction nodes. A junction has:

- protocol;
- subject cardinality;
- sharing mode;
- persistence and replication policy;
- optional label;
- current subject or stream endpoint.

Connecting a port adds an incidence edge. The colimit semantics identifies the interface relationships while storage preserves the mediator.

## 22.4 Workspace composition

A workspace template is a diagram containing:

- internal component instances;
- internal junctions;
- exposed boundary ports or slots;
- constraints and defaults.

Instantiation supplies another open instance and composes it with the template along compatible boundaries.

For a regional-population analysis template:

```text
External boundary:
  mainAnalysis : GraphicDocument

Internal network:
  chart.analysis    ──┐
  table.analysis    ──┤
  pipeline.analysis ──┼── mainAnalysis junction
  encoding.analysis ──┘
```

A dataset-specific `GraphicDocument` is plugged into `mainAnalysis`.

## 22.5 Colimit followed by closure

After raw composition, semantic closure derives:

- each component’s observed subject;
- available link and detach commands;
- field occurrences valid for the document;
- affected views for future commands;
- diagnostics for incompatible ports.

This realizes the reflection equation from Section 20.

## 22.6 Workspace mirror

A mirror creates another placement or workspace view of the same logical component network. It shares component and junction identities.

Categorically, it is not a graph copy. It is another reference or observation of the same object.

## 22.7 Workspace fork

A fork copies a selected subgraph while preserving its internal incidence pattern. Nominal IDs are fresh. External references follow declared copy policy.

This is not generally a colimit. It is a graph-copy functor or rewrite driven by a copying comonad-like policy, depending on the formalization. The product should call it `fork`, not disguise it as ordinary composition.

## 22.8 Template instantiation

A template should be represented without runtime identities for instance-owned objects. Instantiation performs a free or parameterized construction:

- allocate fresh component instances;
- allocate fresh internal junctions;
- bind exposed slots;
- validate protocols;
- saturate rules;
- execute required initialization effects.

The current portable bundle hydrator already performs much of this graph remapping.

## 22.9 Merge versus connect

Connecting two ports makes them participate in one junction. Merging two subjects attempts to identify or reconcile the entities carried by their junctions.

These are different commands.

```text
Connect chart.analysis to pipeline.analysis
```

usually means both observe one selected document.

```text
Merge document A and document B
```

would require application-specific reconciliation and should not be implied by linking.

## 22.10 Coequalizers and explicit identity merge

When the user genuinely declares two aliases to be one entity, a coequalizer or quotient construction may model the identification. Because this can destroy distinctions and invalidate references, it should be rare, explicit, and provenance-preserving.

## 22.11 Hierarchical composition

A composed workspace can itself expose ports and become a reusable component. Wiring-diagram or operadic semantics gives this hierarchy a coherent substitution operation.

For example:

```text
Regional population tool
  exposes: analysis, selection
  contains: chart, table, pipeline, encoding
```

can be nested inside a larger comparison workspace with `leftAnalysis` and `rightAnalysis`.

## 22.12 Composition theorem target

A useful kernel theorem is:

> If every component instance is well typed, every boundary map preserves protocol typing, and every connection is made through a compatible junction, then the assembled raw workspace is well typed. After closure, all derived `observes` and `eligible` facts remain sort correct.

The structural part follows from the chosen category and gluing discipline. The derived part follows from rule type soundness.


# 23. An illustrative TypeScript API

The public API should look like a domain-specific modeling library, not like direct manipulation of category-theoretic objects.

The examples below are deliberately illustrative. They show where syntax must be represented as data and where ordinary JavaScript remains appropriate.

## 23.1 System declaration

```ts
// Illustrative API
import {
  defineSystem,
  key,
  sort,
  relation,
  protocol,
  component,
  command,
  effect,
  lens,
} from "@hyperslop-systems/opk";

export const datalab = defineSystem("datalab", (s) => {
  const GraphicDocument = s.sort("GraphicDocument", {
    schema: graphicDocumentSchema,
    key: key.property("id"),
  });

  const Field = s.sort("Field", {
    schema: fieldReferenceSchema,
    key: key.tuple("docId", "name"),
  });

  const Analysis = s.protocol("Analysis", {
    subject: GraphicDocument,
    sharing: "shared-reference",
    multiplicity: "exactly-one-subject",
    persistence: "workspace",
  });

  return { GraphicDocument, Field, Analysis };
});
```

The schema callback executes at definition time and builds normalized data. It does not become an arbitrary runtime predicate.

## 23.2 Relations

```ts
// Illustrative API
const Denotes = datalab.relation("Denotes", {
  columns: {
    occurrence: Core.Occurrence,
    entity: Core.Entity,
  },
  key: ["occurrence"],
});

const OwnsField = datalab.relation("OwnsField", {
  columns: {
    document: datalab.GraphicDocument,
    field: datalab.Field,
  },
  key: ["field"],
});
```

The relation declaration creates:

- runtime codecs;
- typed query constructors;
- indexes;
- serialization metadata;
- formal schema entries.

## 23.3 Rule syntax

```ts
// Illustrative API
const Eligible = datalab.derived("Eligible", {
  columns: {
    context: Core.InputContext,
    occurrence: Core.Occurrence,
    entity: Core.Entity,
  },
});

datalab.rule("eligible-direct-presentation", ({ v, and, exists }) =>
  Eligible(v.context, v.occurrence, v.entity).when(
    exists({ actual: Core.PresentationType, expected: Core.PresentationType },
      and(
        Core.ContextRequests(v.context, v.expected),
        Core.Denotes(v.occurrence, v.entity),
        Core.PresentedAs(v.occurrence, v.actual),
        Core.SubtypeStar(v.actual, v.expected),
        Core.VisibleToContext(v.occurrence, v.context),
        Core.Permitted(
          Core.ActorOf(v.context),
          Core.SelectCapability(v.entity),
        ),
      ),
    ),
  ),
);
```

The callback receives a syntax builder. It cannot branch on runtime object values with ordinary JavaScript `if`. It constructs a typed logical formula.

## 23.4 Components and ports

```ts
// Illustrative API
const ChartComponent = datalab.component("chart", {
  ports: {
    analysis: datalab.port.duplex(datalab.Analysis),
    selection: datalab.port.duplex(datalab.Selection),
    viewport: datalab.port.local(datalab.ViewportState),
  },

  renderer: datalab.foreign.renderer("ChartRenderer", {
    dependsOn: ["analysis", "selection", "viewport"],
    render: ChartApp,
  }),
});
```

The renderer is explicitly foreign. Its dependencies are declared and instrumented. The component interface is part of the analyzable schema.

## 23.5 Junctions

```ts
// Illustrative API
const mainAnalysis = workspace.junction(datalab.Analysis, {
  id: junctionId,
  subject: censusDocument,
  label: "Main analysis",
});

workspace.connect(chart.port.analysis, mainAnalysis);
workspace.connect(table.port.analysis, mainAnalysis);
workspace.connect(pipeline.port.analysis, mainAnalysis);
workspace.connect(encoding.port.analysis, mainAnalysis);
```

These builder calls create base instance data or a command program. They do not directly mutate peer component state.

## 23.6 Queries

```ts
// Illustrative API
const candidates = runtime.query(
  Eligible.where({ context: activeContext }),
  {
    evidence: "minimal",
    orderBy: [Core.ConversionCost.asc(), Core.ScreenDistance.asc()],
  },
);
```

The result is a live relation or snapshot with stable keys.

## 23.7 Commands

```ts
// Illustrative API
const ConnectAnalysisPorts = datalab.command("ConnectAnalysisPorts", {
  parameters: {
    source: datalab.portRef(datalab.Analysis),
    target: datalab.portRef(datalab.Analysis),
  },

  requires: ({ source, target }) =>
    datalab.logic.and(
      Core.PortCompatible(source, target),
      Core.CanModify(Core.CurrentActor, source),
      Core.CanModify(Core.CurrentActor, target),
      datalab.logic.not(Core.SameJunction(source, target)),
    ),

  transition: datalab.rewrite.connectPorts({
    source: "source",
    target: "target",
    mergePolicy: "source-subject-wins",
  }),

  ensures: ({ source, target }) =>
    Core.SameJunction(source, target),

  effects: [Core.PersistWorkspace, Core.AnnounceChange],
});
```

The `requires` callback builds a formula. `transition` builds a rewrite term. `ensures` emits a proof obligation. Effects are symbolic operations.

## 23.8 Interaction programs

```ts
// Illustrative API
const LinkFocusedAnalysis = datalab.program("LinkFocusedAnalysis", function* (fx) {
  const source = yield* fx.read(Core.FocusedPort(datalab.Analysis));

  const target = yield* fx.ask(
    datalab.goal.port(datalab.Analysis, {
      where: Core.CompatibleWith(source),
      prompt: "Select another analysis view",
    }),
  );

  return yield* fx.perform(
    ConnectAnalysisPorts({ source, target }),
  );
});
```

The program is syntax. A React handler can render sensitive occurrences. A test handler can choose a candidate by ID. A remote handler can send the goal to another client.

## 23.9 Lenses

```ts
// Illustrative API
const EncodingLens = datalab.lens("EncodingLens", {
  source: datalab.GraphicDocument,
  view: datalab.EncodingModel,

  get: datalab.expr.object({
    mark: datalab.expr.path("views", "main", "mark"),
    channels: datalab.expr.path("views", "main", "encodings"),
  }),

  put: datalab.update.mergeAt(["views", "main"], {
    mark: datalab.update.fromView("mark"),
    encodings: datalab.update.fromView("channels"),
  }),

  laws: ["GetPut", "PutGet", "PutPut"],
});
```

A product may use a foreign lens when the update is too complex, but it is then property-tested and marked as an assumption.

## 23.10 Effects and handlers

```ts
// Illustrative API
const ExecuteAnalysis = datalab.effect("ExecuteAnalysis", {
  request: datalab.schema.object({
    document: datalab.GraphicDocument.ref(),
    revision: datalab.schema.number(),
  }),
  response: datalab.AnalysisResult,
  capability: "analysis.execute",
  idempotencyKey: ({ document, revision }) => `${document.id}:${revision}`,
});

runtime.handle(ExecuteAnalysis, duckDbAnalysisHandler);
runtime.handle(Core.PersistWorkspace, localAndRemotePersistenceHandler);
```

The effect handler is foreign execution. The effect request and response are typed, serializable data.

## 23.11 Renderer boundary

A renderer receives a model that has already been semantically resolved:

```ts
interface OccurrenceModel<T> {
  occurrenceId: OccurrenceId;
  entity: EntityRef<T>;
  presentationType: PresentationTypeId;
  label: string;
  tone?: Tone;
  eligibility: readonly ContextEligibility[];
  actions: readonly CommandOffer[];
  registerGeometry(handle: GeometryHandle): void;
}
```

It does not call the registry repeatedly to rediscover actions and conversions.

## 23.12 Developer tooling

The same schema supports an inspector:

```text
Occurrence field:census/region@chart-axis
  denotes Field(census, region)
  presented as field
  eligible for context link-field-12
    via rule eligible-direct-presentation
    because field <: selectable-object
    because actor holds field.select
  available commands
    InspectField
    AddToWatchlist
    UseAsEncoding(x)
  dependencies
    context revision 7
    document schema revision 12
    permission set revision 3
```

This is a major practical benefit of representing semantics as data.

---

# 24. Presentations and input contexts as judgments

The clean-slate architecture does not need a descriptor object to be the unit of meaning. A presentation is a collection of judgments about an occurrence.

## 24.1 Core judgments

Representative judgments are:

\[
\mathsf{Denotes}(o,e)
\]

\[
\mathsf{PresentedAs}(o,t)
\]

\[
\mathsf{VisibleIn}(o,s)
\]

\[
\mathsf{Eligible}(q,o,e)
\]

\[
\mathsf{Offers}(o,c)
\]

\[
\mathsf{Converts}(e,t,e',w)
\]

where \(w\) is a witness containing cost and provenance.

## 24.2 Rendering is one projection

A renderer consumes an entity and presentation intent and produces:

- visual or auditory output;
- occurrence records;
- geometry handles;
- interaction affordances.

The renderer does not own eligibility. The same occurrence can become eligible for different contexts without rerendering its underlying entity.

## 24.3 Presentation types become vocabulary terms

Presentation types remain useful as semantic vocabulary, but their role is narrower:

- classify ways an entity may be interpreted;
- participate in subtype and compatibility rules;
- select default renderer families;
- name protocol conversions.

They are no longer required to own all actions, identity, and conversion callbacks.

## 24.4 Goal formulas

An input context carries a formula with a result type.

Examples:

```text
select one Field owned by the current document
select two distinct Analysis ports with compatible protocols
select one visible Pipeline and derive its owning GraphicDocument
select any entity that can supply a quantitative field
select a target workspace that is not an ancestor of the source
```

A goal can include existentially derived values. Clicking a pipeline occurrence may satisfy a `GraphicDocument` goal through an ownership derivation.

## 24.5 Direct and converted eligibility

Direct eligibility:

```text
occurrence denotes entity e
e is presented under type t
t satisfies expected type u
```

Converted eligibility:

```text
occurrence denotes e
derivation converts e to e′ of expected type u
```

The result carries the chosen witness. The commit step validates that witness against the current revision before accepting it.

## 24.6 Cardinality

Input goals should express cardinality:

```text
exactly one
zero or one
at least one
exactly two distinct
finite set satisfying a group constraint
ordered tuple of parameters
```

Multi-selection becomes part of the interaction program rather than repeated nested `accept` calls with ad hoc state.

## 24.7 Scope

A context can restrict candidates to:

- one surface;
- one workspace;
- visible occurrences;
- an accessibility tree;
- a command palette index;
- remote collaborators’ shared occurrences;
- entities with no current visible occurrence.

The last case shows that presentation-based input need not be limited to pointing at pixels. A palette can synthesize virtual occurrences that denote the same entities.

## 24.8 Ranking

Eligibility and ranking should be separate.

Eligibility answers whether a witness is valid. Ranking chooses among valid witnesses by:

- directness;
- conversion cost;
- priority;
- pointer distance;
- recency;
- keyboard order;
- user preference.

This separation avoids a high-priority rule making an invalid candidate appear valid.

## 24.9 Failure explanations

For an ineligible visible occurrence, the engine can retain a compact failed proof:

```text
Cannot link this tile:
  ✓ it exposes an analysis port
  ✓ the protocols match
  ✗ the target is already in the same junction
```

This supports disabled states and onboarding.

## 24.10 Dynamic context changes

When permissions, bindings, or visible occurrences change, the query result changes incrementally. A selected witness is revalidated at commit time.

The current PBUI implementation already reruns conversion on commitment. OPK generalizes that rule to all proof-carrying selections.

## 24.11 Textual and gestural input

A textual parser, command palette, voice input, and pointer click can all produce candidate judgments. They differ in occurrence source and ranking, not in command semantics.

This recovers one of CLIM’s strengths without making output history the center of the API.

---

# 25. Actions as commands with preconditions and effects

An action offer is a proof that a command schema can be instantiated in the current world.

## 25.1 Command schema

A command schema contains:

```text
name
parameter sorts
precondition formula
pure transition relation or rewrite
postcondition formula
effect program
authorization requirements
conflict and idempotency metadata
presentation metadata
```

## 25.2 Command instance

A command instance binds all parameters and carries evidence that the precondition held at a particular revision.

```ts
interface CommandInstance<C extends CommandSchema> {
  schema: C["id"];
  parameters: ParametersOf<C>;
  precondition: DerivationRef;
  basedOnRevision: WorldRevision;
  idempotencyKey?: string;
}
```

## 25.3 Available action derivation

A rule can produce an offer:

```text
available(InspectField, occurrence, commandInstance) :-
  denotes(occurrence, field),
  hasSort(field, Field),
  permitted(actor, inspect(field)).
```

Common actions are contributed by rules over sorts and capabilities. Product-specific actions can refine them.

## 25.4 Shadowing and priority

The enhanced PBUI registry lets descriptor-local actions shadow action-rule actions by stable ID. OPK should specify this as a resolution algebra rather than array order.

One option:

1. derive every applicable candidate;
2. partition by command family or stable offer key;
3. reject incomparable conflicting definitions unless the schema declares an override relation;
4. choose the maximal override or priority according to a deterministic partial order;
5. retain suppressed candidates for explanation.

This is safer than silently taking the first callback result.

## 25.5 Partial commands

A partial command is an inductive program with unfilled parameters:

```text
UseFieldAsEncoding(
  document = current,
  field = ?,
  channel = x
)
```

The command’s next goal is derived from its missing parameter and current constraints. Selection fills the parameter and recomputes remaining obligations.

## 25.6 Capability-based authority

Effects and mutations require capabilities. A command should not receive ambient access to every store and service.

```text
workspace.modify
analysis.execute
source.read
clipboard.write
remote.persist
```

Handlers verify capabilities independently of UI visibility. Hiding a menu item is not authorization.

## 25.7 Pure transition before effects

A command pipeline is:

```text
validate evidence and revision
  → compute pure next state or rewrite plan
  → validate invariants and postconditions
  → commit semantic event
  → interpret external effects
  → process effect completion events
```

For effects that must precede commit, use a saga or reservation protocol with explicit states rather than mutating during rule evaluation.

## 25.8 Idempotency

Commands that may be retried should carry idempotency keys. Analysis execution can be keyed by document and revision. Persistence can be keyed by event ID.

## 25.9 Stale evidence

An offer derived at revision \(r\) may no longer be valid at revision \(r+1\). The executor rechecks:

- referenced entities still exist;
- precondition still holds;
- actor capabilities remain valid;
- exclusive resources have not changed.

If the proof is stale, the command returns a structured conflict and may request new input.

## 25.10 Menus as query projections

A menu renderer receives command offers. It controls grouping and visual order but does not invent applicability.

```text
Inspect
Use in chart
Link analysis
Fork workspace
Delete
```

The same offers can appear in a keyboard palette or screen-reader command list.

## 25.11 Command laws

Commands may declare algebraic properties:

```text
idempotent
commutesWith(commandFamily)
reversibleBy(inverseCommand)
requiresCoordination
localOnly
```

These are proof obligations or checked metadata, not unchecked optimization hints.

---

# 26. Conversions as derivations with cost and provenance

Conversions are one of the places where the relational and algebraic views combine particularly well.

## 26.1 Conversion edge

A conversion declaration contains:

```text
source sort or presentation type
target sort or presentation type
logical precondition
result construction
nonnegative cost
effect class
provenance label
```

Pure conversions can participate in selection. Effectful conversions should normally become commands because they may allocate, fetch, or mutate.

## 26.2 Example conversions

```text
Field occurrence → owning GraphicDocument
Pipeline occurrence → owning GraphicDocument
Chart occurrence → chart’s Analysis port
Tile occurrence → primary compatible port
Category mark → Field reference
GraphicDocument → Source reference
```

## 26.3 Path composition

If \(e_1:x\to y\) has cost \(c_1\) and \(e_2:y\to z\) has cost \(c_2\), the composite has cost:

\[
c_1+c_2.
\]

Alternative paths choose the minimum cost:

\[
\min(c_a,c_b).
\]

This is evaluation in the tropical or min-plus semiring.

## 26.4 Boolean versus witness semantics

The Boolean question is:

```text
Is any conversion possible?
```

The witness question is:

```text
Which target value and derivation should be used?
```

The engine must retain enough information to reconstruct or validate the chosen target occurrence.

## 26.5 Provenance semirings

A derivation can be annotated with a polynomial over source facts. For example:

```text
pipelineOwnsDocument(pipeline-4, document-census)
```

may be supported by:

```text
occurrence denotes pipeline-4
pipeline-4 belongs to view-8
view-8 observes document-census
```

The provenance expression identifies invalidation dependencies and an explanation path.

## 26.6 Priority is not simply cost

Some conversions are semantically preferred regardless of numeric path length. For example, a direct owner-qualified pipeline-to-document conversion may be preferred over an ambient “active document” conversion.

Represent this with a lexicographic ranking domain:

```text
(effectClass, semanticPriority, numericCost, pathLength, stableEdgeOrder)
```

The order must be deterministic and documented.

## 26.7 Cycles

The current registry prevents infinite conversion traversal with visited identities and path depth. A relational engine similarly needs:

- finite entity universe or bounded term generation;
- cycle-safe fixed-point evaluation;
- no negative-cost cycles;
- explicit maximum derivation depth for foreign constructors if needed.

Positive recursive closure over a finite relation terminates even with cycles because duplicate facts are not re-added.

## 26.8 Revalidation

A conversion witness is checked at commit:

- source occurrence still denotes the same entity;
- ownership relations still hold;
- foreign assumptions are at the same dependency revision;
- target entity still exists;
- cost or priority changes do not make the witness invalid under command policy.

The system may accept any still-valid witness or require the currently optimal witness, depending on the goal.

## 26.9 Conversion versus migration

A lightweight semantic conversion derives another reference or interpretation of existing state.

A migration transforms persisted data or creates a new document. It is a command with effects and validation.

For example:

```text
Pipeline → owning GraphicDocument
```

is a conversion.

```text
Apply this pipeline blueprint to another source schema
```

is a migration or fork command.

## 26.10 Developer explanation

A chosen conversion can be displayed as:

```text
Selected document “Census analysis” from pipeline “Regional population”
  pipeline occurrence
    → owning pipeline entity        cost 0
    → pipeline’s application view   cost 0
    → view’s analysis junction      cost 1
    → junction’s document subject   cost 0
  total cost 1
```

This makes implicit UI behavior inspectable.

---

# 27. Graph rewrites for link, unlink, fork, and duplicate

The structural commands that motivated the linked-workspace study should be specified as graph transformations.

## 27.1 Connect two ports

### Preconditions

```text
source and target exist
both ports speak compatible protocols
actor may modify both components or workspace
ports are not already in the same junction
multiplicity constraints permit connection
subject merge policy is defined
```

### Transition variants

If both ports have private junctions:

- choose or create the resulting junction;
- attach both ports;
- select a subject according to policy;
- remove empty private junctions.

If one port is unattached:

- attach it to the other port’s junction.

If both are in nontrivial junctions:

- merge junction memberships only if policy permits;
- otherwise reject or request explicit group selection.

### Postcondition

```text
SameJunction(source, target)
```

## 27.2 Detach one port

### Preconditions

```text
port belongs to a shared junction
actor may modify the connection
```

### Transition

- remove the incidence edge;
- create a private junction for the detached port;
- carry the old subject into the private junction by shared reference;
- retain all component, view, and placement identities.

### Postcondition

```text
not SameJunction(port, any former peer)
observed subject remains unchanged immediately after detach
```

## 27.3 Rebind a junction

### Preconditions

```text
junction accepts the subject sort
actor may modify the junction
subject exists and is valid
```

### Transition

Replace one `carries` edge. Do not update every connected view.

### Postcondition

Every incident component derives the new subject through closure.

## 27.4 Mirror a view

A mirror creates another placement referencing the same logical component instance or view.

```text
new placement ID
same logical view ID
same ports and junctions
```

This is the current `createLinkedDuplicate` style of relationship.

## 27.5 Duplicate a logical view independently

An independent duplicate creates:

```text
new logical view ID
new component instance ID
new port IDs
new private junctions initialized from current subjects
new placement ID
```

It preserves configuration values but not future sharing.

## 27.6 Fork a workspace

A workspace fork computes the reachable owned subgraph and a copy policy.

### Copy

- workspace;
- layout nodes;
- placements;
- logical views;
- component instances;
- ports;
- internal junctions;
- selected documents if policy says analysis fork.

### Share

- immutable app definitions;
- plugin schemas;
- source catalog entities unless source copy is requested;
- users and global capabilities.

### Rewire

Every internal edge points to the copied endpoint. External edges follow policy.

### Preserve equivalence classes

If four original ports share one junction, the four copied ports share one fresh copied junction. They do not each receive separate bindings.

## 27.7 Template instantiation

Template nodes have symbolic IDs. Instantiation allocates nominal IDs and substitutes slot bindings. It is similar to graph copying with parameter substitution.

## 27.8 Delete

Deletion is constrained graph rewriting:

- remove owned nodes;
- preserve shared nodes;
- reject when protected incoming references remain;
- cascade only through declared ownership edges;
- emit tombstones or events where replication requires them.

## 27.9 Critical pairs

Potential conflicts include:

```text
connect port A to group X
concurrently connect exclusive port A to group Y

unlink port A
concurrently rebind its group

fork workspace
concurrently delete a document in the source workspace
```

Critical-pair or model-checking analysis can determine whether commands commute, require arbitration, or need revision guards.

## 27.10 Reducer compilation

The runtime does not need a generic category-theory engine for every dispatch. A rewrite compiler can produce:

- indexed match code;
- an immutable update plan;
- changed relation deltas;
- inverse metadata;
- effect requests;
- postcondition checks.

This preserves ordinary Redux-style performance while centralizing transition semantics.


---

# 28. Lenses for editable application views

A shared subject is useful only if each application can read and edit the part of that subject it is responsible for. The chart editor, pipeline editor, table configuration, encoding editor, parameter panel, and metadata panel should not each receive unrestricted mutation access to the entire `GraphicDocument`.

The clean-slate architecture therefore needs an explicit account of **bidirectional views**.

## 28.1 A read projection is not enough

A projection can explain how to derive a view from a document:

```ts
const chartModel = projectChart(document, viewId);
```

It does not explain what should happen when the user edits the projected value:

```ts
chartModel.mark = "bar";
```

Several policies are possible:

- update one named view in the document;
- create a view if it does not exist;
- reject the edit because the view is inherited or read-only;
- normalize the requested mark to a supported mark;
- alter a pipeline output rather than the view definition;
- fork the document before editing;
- issue a command requiring authorization and revision checks.

The update direction is product semantics, not something React can infer from the getter.

## 28.2 Classical lenses

A simple lens from source type `S` to view type `A` consists of operations usually written:

\[
\operatorname{get}:S\to A,
\qquad
\operatorname{put}:S\times A\to S.
\]

The familiar laws are:

### Get–Put

Writing back the value just read changes nothing observably:

\[
\operatorname{put}(s,\operatorname{get}(s))=s.
\]

### Put–Get

After writing a view value, reading returns that value:

\[
\operatorname{get}(\operatorname{put}(s,a))=a.
\]

### Put–Put

Only the most recent write matters:

\[
\operatorname{put}(\operatorname{put}(s,a_1),a_2)
=
\operatorname{put}(s,a_2).
\]

These laws are valuable because they rule out surprising editors. They also compose: lawful lenses can be combined to obtain lawful access to nested state.

They are not universally appropriate. A product UI often has validation, normalization, missing data, permissions, asynchronous effects, or commands that create related objects. The architecture should keep the law vocabulary while admitting richer variants.

## 28.3 A command-producing lens

Directly returning a new source value bypasses command authorization, history, collaboration, and effects. OPK should use a **command-producing lens**:

```ts
type LensRead<S, A> = (source: S) => A;

type LensProposal<S, A, C> = (args: {
  source: S;
  current: A;
  proposed: A;
}) =>
  | { kind: "accepted"; command: C; normalized: A }
  | { kind: "rejected"; diagnostics: readonly Diagnostic[] };

interface CommandLens<S, A, C> {
  id: string;
  read: LensRead<S, A>;
  propose: LensProposal<S, A, C>;
}
```

The lens does not mutate. It translates a proposed view edit into a typed command. The ordinary command interpreter then checks:

- identity and revision;
- authorization;
- structural preconditions;
- graph-rewrite invariants;
- effect capabilities;
- persistence and undo policy.

This preserves one transition path for pointer actions, keyboard actions, automation, remote clients, and bidirectional editors.

## 28.4 Validated and normalizing laws

Suppose `normalize : A -> A` puts a requested value into canonical form. A normalizing lens can satisfy:

\[
\operatorname{get}(\operatorname{apply}(s,\operatorname{propose}(s,a)))
=
\operatorname{normalize}(a).
\]

The corresponding laws become observational rather than literal:

- **Get–Propose:** proposing the current observation yields a no-op command or an observationally equivalent state;
- **Propose–Get:** a successful proposal reads back its declared normalized result;
- **Last successful proposal wins:** sequential successful proposals are observationally equivalent to applying the latter against the appropriate current revision;
- **Rejection preservation:** a rejected proposal leaves the world unchanged.

The result should include normalization evidence so that the UI can explain why, for example, an unsupported logarithmic scale became a linear scale or why a field was removed from an encoding.

## 28.5 Partial lenses

Some views exist only for part of the source domain. A pipeline-step editor requires a step that still exists. An encoding editor may require a view with an encoding block.

Use an explicit partial read:

```ts
type ReadResult<A> =
  | { kind: "present"; value: A; evidence: EvidenceId }
  | { kind: "absent"; reason: Diagnostic };

interface PartialCommandLens<S, A, C> {
  read(source: S): ReadResult<A>;
  propose(args: {
    source: S;
    proposed: A;
    evidence: EvidenceId;
  }): ProposalResult<C, A>;
}
```

The evidence token binds the editor to the assumptions under which the view existed. Commit revalidates it. This prevents an edit from targeting a pipeline step that disappeared while the user was typing.

## 28.6 Parameterized lenses

Datalab applications do not generally edit “the chart” in a document. They edit one chart view identified by `viewId`, one transform identified by `stepId`, or one encoding channel identified by a path.

The appropriate abstraction is parameterized:

```ts
interface LensFamily<S, Key, A, C> {
  at(key: Key): PartialCommandLens<S, A, C>;
}
```

Examples include:

```ts
const chartViewLens = lenses.family<
  GraphicDocument,
  GraphicViewId,
  ChartEditorModel,
  UpdateGraphicView
>(/* ... */);

const transformLens = lenses.family<
  GraphicDocument,
  TransformId,
  PipelineStepEditorModel,
  UpdateTransform
>(/* ... */);
```

The key is semantic identity, not an array index. Reordering transforms must not retarget an open editor.

## 28.7 Port-relative lenses

A component instance should not close over one document ID. It owns a port and resolves the current subject through the saturated world:

```ts
interface PortLens<Key, A, C> {
  port: PortId;
  at(key: Key): {
    read(world: SaturatedWorld): ReadResult<A>;
    propose(world: SaturatedWorld, value: A): ProposalResult<C, A>;
  };
}
```

Resolution is conceptually:

```text
component instance
  -> analysis port
  -> junction
  -> carried GraphicDocument
  -> keyed lens into that document
```

When the junction is rebound, the same component and lens family now project the corresponding part of the new subject. The component does not receive a synchronization notification from every peer. It simply observes a different subject through its port.

## 28.8 Lens composition

A document editor may be factored into reusable lenses:

```text
GraphicDocument
  -> named view
  -> encoding map
  -> channel "x"
  -> field reference
```

Composition should preserve diagnostic paths and command provenance:

```ts
const xFieldLens = compose(
  graphicViewLens.at(viewId),
  encodingLens,
  channelLens("x"),
  fieldReferenceLens,
);
```

A naive lens composition returns a nested structural update. A command-lens composition should instead build a typed patch or command term whose path remains inspectable:

```json
{
  "command": "graphic.update",
  "document": "doc:census",
  "path": ["views", "view:population", "encoding", "x", "field"],
  "value": "region",
  "expectedRevision": 42
}
```

This representation is serializable, auditable, and suitable for conflict analysis.

## 28.9 Delta lenses

Replacing a whole editor model is inefficient and can erase concurrent changes. A delta lens maps a view-level edit to a source-level delta:

\[
\delta A \longrightarrow \delta S.
\]

For example:

```ts
type EncodingEdit =
  | { kind: "setField"; channel: Channel; field: FieldId }
  | { kind: "setAggregate"; channel: Channel; aggregate?: Aggregate }
  | { kind: "removeChannel"; channel: Channel };
```

The lens converts this edit to a narrow `GraphicDocument` command. Delta lenses support:

- smaller event logs;
- better merge behavior;
- incremental invalidation;
- precise undo;
- meaningful authorization such as “may edit encodings but not sources.”

A full replacement operation can still exist as an administrative command. It should not be the default editor protocol.

## 28.10 Multi-source views are not ordinary lenses

A comparison chart may read two documents. A join editor may update a relation between them. Such a view is not naturally a lens into either document alone.

Options include:

- a lens into a product source `S1 × S2` when both are one owned aggregate;
- a multi-lens that emits a transaction over several subjects;
- a command-specific editor that is not advertised as a lens;
- a separate relationship entity whose own lens is edited.

The architecture should avoid forcing every bidirectional interaction into the simplest lens signature.

## 28.11 Source replacement is generally a migration, not a lens write

The current Datalab `setDocSource` operation resets transforms, views, encodings, and parameters. That behavior violates the intuitive expectations of a lawful lens from `GraphicDocument` to `SourceRef`: putting a new source destroys unrelated observations.

There are two honest interpretations:

1. `source` is not an independently editable lens. Replacing it is a destructive document-reinitialization command.
2. Retargeting an analysis is a schema-aware migration that attempts to preserve the analysis program under a field mapping.

The linked-workspace product requirement needs the second operation for reusable analytical setups. It should be named `rebaseAnalysis`, `forkOntoSource`, or `instantiateTemplate`, not hidden inside a generic `put`.

## 28.12 Lens laws at the repository boundary

For `GraphicDocument`, useful executable laws include:

```text
read(apply(noOpProposal(read(doc)))) == read(doc)
read(apply(setMark("bar"))) == normalized("bar")
rejectedProposal leaves document and revision unchanged
editing view A leaves view B unchanged unless an explicit invariant requires repair
editing a transform preserves stable IDs of unaffected transforms
composed lens update equals its generated direct patch
undo(apply(command)) restores an observationally equivalent document
```

Property-based generators can construct valid documents, views, steps, and edits. Counterexamples should print the smallest document and command sequence that violates a law.

## 28.13 Presentations over lens targets

A visible encoding pill can denote both:

- the field entity it currently refers to;
- the editable lens target `(document, view, channel)`.

These are different occurrences and may expose different commands.

For example, dropping a field occurrence onto an `encodingTarget` occurrence can derive a partial command:

```text
field occurrence
  + encoding target occurrence
  -> SetEncodingField(document, view, channel, field)
```

The presentation system therefore does not disappear when lenses are introduced. It provides semantic operands to a lawful update path.

## 28.14 Recommended rule

Use a lens when the product intends a stable editable view with stated round-trip laws. Use a command when the operation changes topology, identity, ownership, source compatibility, or multiple independent aggregates. Do not label every getter/setter pair a lens.

---

# 29. Behavior, concurrency, and model checking

The saturated relational world describes what is true at a snapshot. Graph rewrites describe atomic state changes. Neither alone describes asynchronous interaction over time.

A real PBUI operation can span:

- opening an input context;
- registering and removing occurrences as React renders;
- highlighting candidates;
- receiving a pointer or keyboard gesture;
- converting and validating a selection;
- asking for confirmation;
- running DuckDB or a network request;
- committing a result only if its assumptions remain current;
- cancelling when a component unmounts or a newer request supersedes it.

This behavior needs a transition-system semantics.

## 29.1 Snapshot semantics and temporal semantics

Keep two models distinct:

- **snapshot semantics** answers “which facts, commands, and occurrences are valid now?”;
- **temporal semantics** answers “which sequences of states and effects are allowed?”

The first is relational and fixed-point based. The second can be modeled as a labeled transition system, state machine, event system, or coalgebra.

A state machine may use variables such as:

```text
baseWorld
activeContexts
visibleOccurrences
pendingEffects
requestRevisions
committedEvents
focus
clockOrLogicalTime
```

A transition label records a command, user gesture, render registration, effect completion, or cancellation.

## 29.2 A small interaction machine

An input context can have states:

```text
Dormant
  -> Open
  -> CandidateChosen
  -> Revalidating
  -> Committed | Rejected | Cancelled
```

Representative transitions are:

```text
OpenContext(goal, owner)
RegisterOccurrence(occurrence)
UnregisterOccurrence(occurrence)
OfferGesture(gesture, occurrence)
ChooseCandidate(derivation)
CommitSelection(expectedRevision)
CancelContext(reason)
```

The important point is that registration and eligibility are not equivalent. An occurrence may remain registered while becoming ineligible after a permission or subject change. Eligibility is re-derived from the current world.

## 29.3 Command/effect/commit protocol

Long-running analysis should use an explicit protocol:

1. **Prepare:** validate the command against revision `r`; compute an effect request and a commit token.
2. **Run effect:** perform DuckDB, file, network, or worker computation outside the pure state transition.
3. **Complete:** return a result associated with the request and expected revision.
4. **Commit or discard:** atomically revalidate assumptions; apply the result or record it as stale.

Illustrative data:

```ts
interface EffectTicket<Result> {
  id: RequestId;
  commandId: CommandId;
  subject: EntityRef<"graphicDocument">;
  expectedRevision: number;
  dependencyFingerprint: string;
  request: EffectRequest<Result>;
}
```

This avoids the common race in which an old query finishes after the user switches the linked workspace to a new document and overwrites the new chart.

## 29.4 Structural safety properties

A bounded Alloy model is well suited to finding small counterexamples in graph structure. Candidate assertions include:

```text
Every exclusive port is incident to at most one live junction.
Every junction carries subjects compatible with its protocol.
Every placement references one live logical view.
Every logical view belongs to exactly one component instance.
Every internal template edge is rewired to a fresh internal node after fork.
No forked internal node points back to an original internal junction.
A mirror shares logical identity; an independent duplicate does not.
A deleted owned node has no live owned descendant unless explicitly retained.
```

The model does not prove the TypeScript implementation correct by itself. It tests whether the proposed invariants and rewrite definitions admit counterexamples within a finite scope.

## 29.5 Temporal safety properties

TLA+ or a similar temporal formalism is better for interleavings. Useful invariants include:

### At-most-one settlement

An accept operation resolves or rejects at most once.

### Commit validity

A committed selection has a derivation valid in the world revision against which commit occurred.

### No stale analysis overwrite

A result produced for dependency fingerprint `f` never replaces output whose current dependency fingerprint differs from `f`.

### Binding atomicity

A rebind is observed as one junction update. There is no intermediate state in which some incident views observe the old subject and others the new subject.

### Authorization at commit

Every committed command was authorized at its commit revision, not merely when its menu item was first displayed.

### Cancellation isolation

Completing a cancelled effect does not mutate live application state.

### Focus ownership

A closed input context cannot retain active keyboard focus ownership.

## 29.6 Liveness properties

Liveness requires assumptions about the environment. Examples include:

```text
If an enabled local pure command is selected, it eventually commits or reports rejection.
If an effect handler is fair and returns, its request eventually settles.
A superseded request eventually leaves the pending set.
A visible modal context can always be cancelled by an allowed gesture.
A successfully committed rebind eventually produces updated projections for all live incident components.
```

It is incorrect to state unconditional liveness for a network call. The model must include fairness and failure assumptions.

## 29.7 A compact TLA+-style sketch

The following is pseudocode, not a complete specification:

```text
VARIABLES world, contexts, requests, outputs

Init ==
  /\ WellTyped(world)
  /\ contexts = {}
  /\ requests = {}

OpenContext(c) ==
  /\ c \notin contexts
  /\ contexts' = contexts \cup {c}
  /\ UNCHANGED <<world, requests, outputs>>

Rebind(j, d) ==
  /\ Authorized(j, d, world)
  /\ Compatible(j, d, world)
  /\ world' = RewriteRebind(world, j, d)
  /\ UNCHANGED <<contexts, requests, outputs>>

Complete(q, result) ==
  /\ q \in requests
  /\ IF CurrentFingerprint(world, q.subject) = q.fingerprint
        THEN outputs' = ApplyResult(outputs, q, result)
        ELSE outputs' = outputs
  /\ requests' = requests \ {q}
  /\ UNCHANGED <<world, contexts>>

Next ==
  \/ \E c : OpenContext(c)
  \/ \E j, d : Rebind(j, d)
  \/ \E q, r : Complete(q, r)
  \/ ...
```

A model checker can explore sequences such as `start query -> rebind -> old query completes` and verify the stale-result invariant.

## 29.8 Revisions and dependency fingerprints

A single global revision is easy but invalidates too broadly. A dependency fingerprint can include the revisions of exactly the entities or relations an operation read:

```text
GraphicDocument revision
source asset revision
pipeline plan hash
parameter values revision
plugin compiler version
authorization epoch
```

The query engine should derive this dependency set from the compiled expression where possible. A foreign callback must declare it.

## 29.9 Serializability and linearization points

For local commands, the reducer application is a natural linearization point. For remote collaboration, linearization may occur at a server log, consensus index, or CRDT merge.

The API should state which semantics it offers:

- optimistic local application with possible compensation;
- server-authoritative serialization;
- causally ordered event application;
- convergent replicated data type;
- transaction across a bounded aggregate.

“React state update” is not a concurrency contract.

## 29.10 Event sourcing as an optional interpreter

Because commands and rewrites are serializable, an event-sourced interpreter can record:

```text
command requested
command accepted or rejected
base delta committed
effect requested
result committed or discarded
```

Replay reconstructs base state. Derived closure is recomputed, not persisted as independent truth unless used as a cache with a theory version.

An event log gives:

- deterministic regression fixtures;
- auditability;
- undo and compensation metadata;
- temporal-property test traces;
- migration support.

It does not automatically solve merge conflicts or guarantee that old commands remain meaningful after schema evolution.

## 29.11 Coalgebraic view

A component runtime can be regarded as a coalgebra whose observations and next states are determined by inputs:

\[
c : S \to O \times S^{I}
\]

or by a more suitable effectful functor. This perspective is useful for **behavioral equivalence**. Two implementations are equivalent when no allowed interaction trace can distinguish their observable behavior, even if their internal caches differ.

For migration, one can aim for a simulation or bisimulation between:

- the current PBUI Promise-based accept runtime;
- the OPK interaction interpreter.

The relation need not equate internal states. It should preserve visible candidates, selected denotations, rejection behavior, and committed commands for the compatibility subset.

## 29.12 Model-checking workflow

A pragmatic workflow is:

1. Write the smallest structural Alloy model for entities, ports, junctions, and rewrite postconditions.
2. Generate counterexamples before writing reducers.
3. Write a TLA+ model for asynchronous request and input-context interleavings.
4. Check bounded instances continuously in CI.
5. Generate TypeScript property tests from the same command vocabulary where practical.
6. Record production traces in a normalized form and replay them against both the current and replacement interpreters.
7. Promote stable invariants into runtime assertions at trust boundaries.

The purpose is not to formalize CSS or every pointer coordinate. It is to attack topology, identity, stale state, and asynchronous races where ordinary example tests are weakest.

---

# 30. Foreign JavaScript and the proof boundary

A proof-oriented API must be honest about host-language code. JavaScript and TypeScript can implement pure, deterministic mathematics, but the language and runtime do not enforce those properties in general.

The architecture should therefore define a visible boundary between **terms interpreted by the kernel** and **foreign operations trusted under declared assumptions**.

## 30.1 Core terms are data

Core selectors, rules, commands, effects, rewrites, and queries should have serializable abstract syntax. For example:

```ts
const goal = and(
  isSort("field", variable("candidate")),
  relates("belongsToDocument", variable("candidate"), parameter("document")),
  not(relates("hidden", variable("candidate"))),
);
```

The kernel can:

- type-check the term;
- compute dependencies;
- choose an evaluation strategy;
- serialize it;
- produce evidence;
- compare or hash it;
- run it in a worker or on a server;
- generate an Alloy, SMT, or Datalog approximation;
- reject unsupported recursion or negation.

A closure over a `Set` cannot provide these properties without further representation.

## 30.2 Foreign operations need classes

Not every callback has the same risk. OPK should classify foreign code.

### Renderer

```text
Saturated projection -> React nodes
```

A renderer may be effectful in ordinary React ways, but it does not add logical facts. It receives opaque entity handles and occurrence-registration APIs.

### Pure total function

```text
serializable input -> serializable output
```

Examples include formatting, deterministic key derivation, and small normalization routines. The declaration claims termination and no observable effects.

### Deterministic predicate

```text
input -> boolean
```

It may participate in filtering but is not assumed monotone. Its exact dependency set and cache key must be known.

### Monotone oracle

```text
partial knowledge -> additional positive facts
```

This is the strongest useful foreign declaration. The plugin claims that adding input facts cannot retract its emitted facts. Such an oracle may participate in fixed-point closure if the runtime can bound and schedule it safely.

### Effect handler

```text
effect request -> asynchronous result
```

Examples are DuckDB, network requests, clipboard access, file selection, and navigation. It never runs inside pure closure.

### External data source

```text
subscription -> revisioned fact deltas
```

A database or server feed injects new base facts. Retractions are explicit negative deltas or new snapshots, not hidden mutation.

### Solver or compiler

```text
well-typed term -> result plus certificate or diagnostics
```

Examples include the GraphicDocument compiler, schema compatibility checker, and query planner. It may be deterministic without being simple enough to encode in the core logic.

## 30.3 A foreign declaration

Illustrative API:

```ts
const fieldCompatibility = foreign.predicate({
  id: "datalab.fieldCompatibility.v1",
  input: schema.tuple([
    schema.ref("field"),
    schema.ref("encodingTarget"),
  ]),
  output: schema.boolean(),

  assumptions: {
    pure: true,
    deterministic: true,
    total: true,
    monotone: false,
  },

  dependencies: [
    relation("fieldType"),
    relation("channelAcceptsType"),
    relation("pluginVersion"),
  ],

  cache: {
    key: "semantic-input-and-dependency-revisions",
    scope: "world-revision",
  },

  run: ([field, target], environment) =>
    environment.encodings.accepts(field, target),
});
```

The declaration is a contract and a cache plan. It is not a proof. Verification may test or discharge some assumptions, but the trusted computing base must still record them.

## 30.4 Assumption provenance

A derivation that depends on foreign code should say so:

```text
Candidate field: population
  because field(population)
  and belongsToDocument(population, census)
  and foreign predicate datalab.fieldCompatibility.v1 returned true
  under plugin version 8f91…
```

The evidence graph can distinguish:

- kernel-proved rule steps;
- base facts supplied by an authoritative store;
- foreign assumptions;
- cached foreign results;
- user assertions;
- remote attestations.

“Proof-carrying UI” should not conceal an opaque predicate under the same evidence node as a logical inference.

## 30.5 Monotonicity declarations

A monotonicity declaration should state an order. “Monotone” without a domain order is incomplete.

For a foreign index:

```ts
order: {
  input: "fact-set-inclusion",
  output: "fact-set-inclusion",
}
```

For permission information, the natural order may not be simple set inclusion because revocation exists. It may be safer to treat authorization snapshots as versioned base inputs and avoid putting a permission oracle inside positive closure.

The kernel can perform lightweight checks:

- sample `x <= y` pairs and test `f(x) <= f(y)`;
- reject observed counterexamples;
- require deterministic re-execution in development;
- compare declared and actual dependency reads through instrumentation.

Passing these tests increases confidence but does not prove the universal property.

## 30.6 Prepared selectors become query plans or foreign indexes

The enhanced PBUI selector `prepare` hook performs work once per accept operation. In OPK, there are two more explicit cases:

1. The selector is a core query. The planner builds indexes and a reusable execution plan automatically.
2. The selector depends on opaque product logic. A foreign index declares how it is built, keyed, invalidated, and queried.

Illustrative foreign index:

```ts
const allowedFieldNames = foreign.index({
  id: "datalab.allowedFieldNames.v1",
  buildInput: schema.array(schema.string()),
  key: schema.string(),
  build: (names) => new Set(names),
  has: (set, name) => set.has(name),
  deterministic: true,
  invalidation: "build-input-hash",
});
```

This is more analyzable than an arbitrary closure capturing an untracked array, while retaining the performance benefit of `Set` membership.

## 30.7 Dependency capture

Foreign code should not receive the complete mutable application store. Give it a capability-scoped environment:

```ts
interface ForeignReadContext {
  read<R extends RelationId>(relation: R): ReadonlyRelationSnapshot<R>;
  asset<A extends AssetCapability>(capability: A): AssetReader<A>;
  signal: AbortSignal;
}
```

The runtime records which relations and assets were read. It can then:

- validate a declared dependency set;
- derive a fingerprint;
- invalidate caches precisely;
- cancel stale work;
- report hidden dependency violations in development.

Dynamic dependency tracking is not a replacement for static declaration, but the two can cross-check one another.

## 30.8 Capability discipline

Foreign operations must declare capabilities such as:

```text
read relation X
read document asset Y
execute DuckDB query
use network origin Z
write clipboard
open file picker
navigate
emit telemetry event class T
```

A renderer does not automatically receive command authority. An effect handler does not automatically receive the full world. This confines plugins and makes command authority auditable.

## 30.9 Time, randomness, and locale

Time, randomness, locale, and feature flags must be explicit inputs when they affect semantics:

```ts
foreign.pure({
  input: schema.struct({
    value: schema.number(),
    locale: schema.locale(),
    timeZone: schema.timeZone(),
  }),
  /* ... */
});
```

A label formatter can remain renderer-only if its output has no semantic role. A parser or identity function cannot silently depend on the user’s locale or current clock.

## 30.10 Failure and resource contracts

A foreign function can throw, hang, allocate excessively, or return malformed data. Its declaration should include:

- runtime codec for inputs and outputs;
- synchronous or asynchronous mode;
- cancellation support;
- time and memory budget class;
- failure taxonomy;
- retry and idempotency policy;
- worker or sandbox requirement;
- maximum emitted fact count for an oracle;
- theory re-entry policy.

An oracle that can emit unbounded fresh entities is especially dangerous because it may prevent fixed-point convergence. Fresh identity creation should remain a command or bounded import operation.

## 30.11 Cache safety

Cache keys should include:

```text
foreign operation version
semantic input identity
all dependency revisions
relevant capability or authorization epoch
locale/time-zone inputs where semantic
schema and rule-theory version
```

Never reuse a Boolean eligibility result merely because two DOM occurrences have similar props. Cache semantic derivations and retain occurrence-specific payloads, as the enhanced PBUI conversion code already does by re-running conversion for the committed occurrence.

## 30.12 Plugin conservativity

A plugin that only adds new sorts, relations, renderers, and commands should ideally be conservative over existing vocabulary: old facts about old entities do not change merely because the plugin is installed.

This property can fail when a plugin adds:

- rules deriving old predicates;
- higher-priority commands that shadow existing commands;
- subtype edges affecting existing goals;
- lower-cost conversions changing chosen paths;
- global negation assumptions.

The plugin manifest should classify extensions and surface possible non-conservative effects. A stronger plugin system can require explicit import points for rules that affect core predicates.

## 30.13 Development modes

Three useful modes are:

### Strict analyzable mode

Only core terms and certified foreign operations are accepted. Suitable for server execution, portable templates, and sensitive workflows.

### Assumption-tracked mode

Foreign operations are accepted, but every result carries the relevant assumption and version. Suitable for most product code.

### Local escape mode

Arbitrary lambdas are allowed for prototyping. They are non-serializable, local-only, conservatively invalidated, and visibly excluded from proof claims.

This preserves JavaScript’s exploratory strength without allowing prototype shortcuts to silently define the permanent semantic kernel.

---

# 31. Incremental execution and performance

A fixed-point or relational architecture is only useful if ordinary interaction remains immediate. The denotational model and the runtime strategy must be separated: the same query can be interpreted naively for testing and incrementally for production.

## 31.1 Base facts, derived facts, and projections

Maintain three layers:

```text
Base store
  durable or transient facts changed by commands and subscriptions

Derived store
  closure facts maintained from base deltas and rules

Projection cache
  component- and surface-specific query results consumed by React
```

Derived facts are reproducible from the base store and theory version. Projection caches are reproducible from the saturated world and query version.

## 31.2 Compile rules before runtime

A rule compiler should:

1. type-check relation positions and variables;
2. build a predicate dependency graph;
3. identify recursive strongly connected components;
4. reject or stratify negation;
5. choose join orders;
6. select indexes;
7. determine delta variants;
8. determine provenance requirements;
9. generate explanation templates;
10. emit dependency metadata for projections.

The runtime should not interpret a general logical AST from scratch for every pointer move.

## 31.3 Seminaive fixed-point evaluation

For positive recursive rules, seminaive evaluation avoids repeatedly deriving facts from only old facts. At iteration `i`, each rule variant uses at least one newly derived relation delta `Δ_i`.

Conceptually:

```text
R_0 = base facts
Δ_0 = R_0

while Δ_i is not empty:
  candidates = evaluate rules using at least one Δ_i input
  Δ_(i+1) = candidates - known facts
  known facts += Δ_(i+1)
```

For finite active universes, each new fact is inserted at most once. Indexing and join order then dominate cost.

## 31.4 Demand-driven saturation

The full product vocabulary can be large, but one input context usually asks a small goal. The engine can maintain:

- always-on core closure for cheap structural relations;
- component projection queries for mounted applications;
- demand-driven goal slices for active input contexts and menus;
- lazy provenance expansion when the user asks “why?”

A magic-set-like transformation or dependency slicing can restrict evaluation to predicates and constants reachable from the current goal.

Demand must not change semantics. It changes which equivalent computation is materialized.

## 31.5 Occurrence registration as a delta stream

React mounts and unmounts occurrences frequently. Treat registration as indexed base deltas:

```text
+ occurrence(o)
+ denotes(o, field:population)
+ renderedIn(o, surface:chart-1)
- occurrence(o)
```

Eligibility joins registered occurrences with semantic entities and current goals. Semantic closure about fields and documents can remain stable while placements rerender.

Occurrence IDs should be allocation-stable for the life of the mounted semantic region. Recreating every ID each render causes avoidable churn.

## 31.6 Deletions and retractions

UI state is not append-only. Views close, permissions revoke, ports detach, and subjects rebind. Positive fixed-point semantics still permits recomputation from a changed base, but an efficient runtime must process retractions.

Options include:

- reference counts for nonrecursive derivations;
- derivation counts or provenance polynomials;
- delete-and-rederive strategies;
- differential arrangements with positive and negative weights;
- recomputation of small recursive strongly connected components;
- versioned snapshots when deletions are rare and worlds are small.

The first implementation should choose the simplest correct strategy per predicate class rather than implement a universal incremental theorem prover.

## 31.7 Provenance cost policy

Full derivation provenance can be much larger than Boolean results. Use levels:

```text
none       only truth and invalidation counts
witness    one selected derivation
bounded    top k derivations or paths
complete   semiring expression or proof DAG
```

Eligibility highlighting usually needs one witness. Debugging a plugin conflict may need all minimal-cost derivations. Audited authorization may require a durable proof trace.

## 31.8 Shared query plans

Menus, hover feedback, keyboard traversal, and click acceptance should consume one compiled eligibility relation rather than each running a selector independently.

For an active goal `g`, maintain something like:

```text
eligible(g, occurrence, value, derivation, rank)
```

Then:

- highlighting queries occurrences;
- keyboard navigation orders occurrences by geometry and rank;
- click commit looks up and revalidates the selected derivation;
- accessibility announcements project labels and rejection reasons;
- tests inspect the same relation.

This removes semantic drift between interaction modalities.

## 31.9 Incremental command menus

Available actions are a query over:

```text
selected occurrence or entity
current subject bindings
permissions
component state
command schemas
foreign capability availability
```

The menu can subscribe to the resulting relation. A permission delta removes commands without rebuilding every descriptor. A newly installed plugin adds command rows through the same mechanism.

## 31.10 Conversion search

A weighted conversion graph should be compiled by source sort and guarded edge conditions. For nonnegative scalar costs, a bounded Dijkstra-style search is sufficient. More generally, path annotations may form a semiring or ordered algebra carrying:

```text
cost
priority
lossiness
required confirmation
capabilities
provenance
```

The selection order must be explicit. Lexicographic order is often safer than collapsing all concerns into one floating-point number:

```text
1. reject paths violating hard constraints
2. prefer no-confirmation over confirmation where product policy says so
3. minimize semantic loss class
4. minimize numeric cost
5. maximize command priority
6. deterministic edge-ID tie break
```

Compiled shortest-path results can be cached by theory version, source semantic identity, goal parameter fingerprint, and relevant base revisions.

## 31.11 Incremental graph rewrites

A command should emit relation deltas directly:

```ts
interface WorldDelta {
  insert: readonly Fact[];
  remove: readonly Fact[];
  touchedEntities: readonly EntityRef[];
  inverse?: SerializableCommand;
}
```

The closure engine consumes the delta; projections receive their own deltas. Avoid cloning a monolithic JavaScript object and diffing it afterward to discover what changed.

Redux or another store can still hold normalized tables. The important improvement is that the command compiler knows the semantic delta.

## 31.12 React integration

React should subscribe through an external-store interface with immutable snapshots:

```ts
const projection = useSyncExternalStore(
  query.subscribe,
  query.getSnapshot,
  query.getServerSnapshot,
);
```

Each component observes a compact projection. The engine publishes only after an atomic command and its synchronous closure delta have reached a consistent snapshot. This prevents tearing in which the link indicator shows a new junction while the chart still resolves the old subject.

Expensive analysis results may arrive later as a separate revisioned relation. The UI can explicitly represent `pending`, `current`, `stale`, and `failed` states.

## 31.13 Worker boundary

A practical split is:

### Main thread

- React rendering;
- pointer geometry and focus;
- small occurrence-registration deltas;
- optimistic command dispatch;
- immediate projection snapshots.

### Worker

- larger fixed-point maintenance;
- conversion planning;
- provenance expansion;
- schema compatibility;
- graph critical-pair diagnostics;
- DuckDB orchestration where supported.

The protocol should send normalized deltas and revisioned projection updates, not entire application stores. Small core queries may remain on the main thread to avoid message latency.

## 31.14 Analysis data versus UI metadata

The table rows of a census dataset should not become one logical fact per cell in the UI kernel unless semantic interaction requires it. Keep bulk analytical data in DuckDB, Arrow, or another columnar engine. The presentation world stores:

- dataset and document identities;
- schema and field identities;
- query-plan identities;
- row-key handles for visible rows;
- current result-set revisions;
- visible occurrences;
- selected values where needed.

A table viewport can register only visible row occurrences. Queries over millions of rows remain in the analytical engine.

## 31.15 Stable keys and identity indexes

Identity lookups should be constant-time by declared keys. For a field:

```text
identity domain: field
key: (document ID, field name or stable field ID)
```

For a row:

```text
preferred: producer-supplied stable row key
fallback: object identity for one result snapshot
```

Structural deep equality is both expensive and semantically unsafe for duplicate rows.

## 31.16 Cache invalidation hierarchy

Use version vectors or epochs at useful granularity:

```text
schemaVersion
ruleTheoryVersion
pluginSetVersion
baseRelationRevision[R]
entityRevision[E]
assetRevision[A]
projectionQueryVersion
```

A query plan declares which versions affect it. A blanket global version remains a correct fallback, but precise revisions preserve responsiveness.

## 31.17 Resource budgets

The engine should expose diagnostics for:

- fact count by relation;
- delta size by command;
- rule firings;
- recursive iterations;
- index memory;
- projection recomputations;
- provenance nodes;
- foreign callback time;
- worker round trips;
- React commit count.

Rules and plugins can carry budgets:

```text
maximum derivation depth
maximum conversion path length
maximum candidate count before narrowing
maximum provenance alternatives
maximum foreign oracle emissions
```

Budget exhaustion should produce an explicit incomplete result, never silently reinterpret “not computed” as “false.”

## 31.18 Correctness of incrementalization

The principal runtime theorem target is:

> Applying the incremental evaluator to a valid base delta yields the same saturated observable result as recomputing the declarative semantics from the updated base instance.

Formally, for base state `I`, delta `δ`, batch closure `C`, and incremental maintenance `inc`:

\[
\operatorname{apply}\big(C(I),\operatorname{inc}(I,\delta)\big)
\cong
C\big(\operatorname{apply}(I,\delta)\big).
\]

The isomorphism permits implementation-specific fact IDs and cache structure but must preserve public relations, chosen ordering policy, and evidence semantics.

A slow reference interpreter is therefore strategically important. Random command traces can compare incremental and batch results.

## 31.19 Performance conclusion

The mathematically clean API should not require the product to execute category-theory constructions or full proofs on every event. It should make the semantics explicit enough that compilers can produce ordinary indexes, worklists, immutable updates, worker jobs, and React subscriptions whose correctness can be compared against a reference meaning.

---

# 32. Worked Datalab census workspace

This section applies the proposed architecture to the concrete Datalab fixture rather than to an abstract chart example.

The repository’s census data contains 24 rows with these fields:

```text
station_id   nominal identifier
region       nominal category
population   quantitative measure
area_km2     quantitative measure
```

The finished demonstration document named **Population by region** uses:

```text
source: regional census
transform: sum population, grouped by region
output field: population_total
mark: bar
x: region
y: population_total
color: region
```

The workspace requirement is to show the same analysis through a chart, table, pipeline, and encoding editor, and to change all four coherently when the analysis subject changes.

## 32.1 Base entities

An OPK instance could contain the following nominal entities:

```text
GraphicDocument  doc:census-population
SourceAsset      source:regional-census
Transform        transform:aggregate-population
GraphicView      graphicView:population-bars
Field            field:census.region
Field            field:census.population
Field            field:census.population_total

Component        component:chart-1
Component        component:table-1
Component        component:pipeline-1
Component        component:encoding-1

Port             port:chart-1.analysis
Port             port:table-1.analysis
Port             port:pipeline-1.analysis
Port             port:encoding-1.analysis

Junction         junction:main-analysis
```

The field `population_total` is a logical field produced by the aggregate transform. It is not a source column even though it is selectable and presentable like one.

## 32.2 Base relations

Representative base facts are:

```text
hasSort(doc:census-population, graphicDocument)
hasSort(source:regional-census, sourceAsset)

owns(component:chart-1, port:chart-1.analysis)
owns(component:table-1, port:table-1.analysis)
owns(component:pipeline-1, port:pipeline-1.analysis)
owns(component:encoding-1, port:encoding-1.analysis)

portProtocol(port:chart-1.analysis, analysisSubject)
portProtocol(port:table-1.analysis, analysisSubject)
portProtocol(port:pipeline-1.analysis, analysisSubject)
portProtocol(port:encoding-1.analysis, analysisSubject)

incident(port:chart-1.analysis, junction:main-analysis)
incident(port:table-1.analysis, junction:main-analysis)
incident(port:pipeline-1.analysis, junction:main-analysis)
incident(port:encoding-1.analysis, junction:main-analysis)

junctionProtocol(junction:main-analysis, analysisSubject)
carries(junction:main-analysis, doc:census-population)

documentSource(doc:census-population, source:regional-census)
documentTransform(doc:census-population, transform:aggregate-population)
documentView(doc:census-population, graphicView:population-bars)
```

The source, transform, and view internals may remain in `GraphicDocument` storage and be projected into relations on demand. They do not have to be duplicated as independently mutable truth.

## 32.3 Derived observation

A positive rule derives the document observed by each component:

```text
observes(Component, Document) :-
  owns(Component, Port),
  incident(Port, Junction),
  carries(Junction, Document),
  portProtocol(Port, analysisSubject).
```

Closure yields:

```text
observes(component:chart-1, doc:census-population)
observes(component:table-1, doc:census-population)
observes(component:pipeline-1, doc:census-population)
observes(component:encoding-1, doc:census-population)
```

Each application projection now resolves through `observes`. No chart-to-table, pipeline-to-chart, or encoding-to-pipeline synchronization event exists.

## 32.4 Component projections

The chart projection reads the document’s root view and compiled result:

```text
ChartProjection =
  mark bar
  x region
  y population_total
  color region
  result relation aggregate-population.output
```

The table projection can choose a declared relation port or default to the root view’s relation:

```text
TableProjection =
  columns region, population_total
  rows from aggregate-population.output
```

The pipeline projection reads:

```text
scan regional-census
  -> aggregate groupBy region, sum population as population_total
```

The encoding projection reads the root view’s channel map:

```text
x     -> region
y     -> population_total
color -> region
```

These are different projections of one subject. They need not share application state such as table sort order, chart zoom, pipeline panel expansion, or local selection.

## 32.5 The link indicator as a presentation occurrence

Each component header renders an occurrence denoting its analysis port:

```ts
<Present
  entity={ref("analysisPort", "port:chart-1.analysis")}
  role="link-indicator"
>
  <LinkIcon />
</Present>
```

The icon’s visual state is derived:

```text
unlinked   port incident to a private one-member junction
linked     junction has two or more incident analysis ports
warning    junction carries no valid subject or protocol conflict exists
pending    a link or migration command is awaiting completion
```

The icon is not the binding object. It is an occurrence denoting a port and exposing commands derived from the current graph.

## 32.6 Linking by selecting another port

Activating **Link analysis with…** opens an interaction goal:

```text
Find an analysisPort candidate P such that:
  P is not the source port
  P accepts the analysisSubject protocol
  connecting sourcePort and P preserves exclusivity constraints
  actor may modify both relevant junctions
```

Every compatible link icon, tile title, or application surface may satisfy the goal if it denotes the required port. The user clicks the pipeline tile’s link icon. The selected value is a semantic port reference, not a DOM node or `viewId` guessed by the action handler.

The command is:

```json
{
  "kind": "workspace.connectPorts",
  "left": "port:chart-1.analysis",
  "right": "port:pipeline-1.analysis",
  "mergePolicy": "prefer-left-subject",
  "expectedRevision": 18
}
```

The rewrite either:

- attaches a private port to the other port’s junction;
- merges two junctions under a declared subject-conflict policy;
- rejects because both junctions carry incompatible non-equal subjects and no policy was supplied.

The existing PBUI `linkViewDocuments` action corresponds to a specialized version of this rewrite.

## 32.7 Switching the linked workspace to another document

Suppose a second complete `GraphicDocument` exists:

```text
doc:production-yield
  source: production-batches
  transform: mean yield_pct grouped by line
  output: mean_yield
  chart: bar, x line, y mean_yield
```

Selecting that document from any linked component issues one command:

```json
{
  "kind": "workspace.rebindJunction",
  "junction": "junction:main-analysis",
  "subject": "doc:production-yield",
  "expectedRevision": 24
}
```

The base delta is approximately:

```text
- carries(junction:main-analysis, doc:census-population)
+ carries(junction:main-analysis, doc:production-yield)
```

Closure now derives that all four components observe `doc:production-yield`. Their projections become:

```text
chart:    yield by production line
pipeline: mean yield_pct grouped by line
table:    line, mean_yield
encoding: x line, y mean_yield, color line
```

This is the simple and robust case: the destination document already contains a complete compatible analysis setup. Rebinding changes the subject, not the internals of either document.

## 32.8 Selecting a pipeline occurrence

The user may initiate the switch by clicking a pipeline tile rather than a document selector. The selected occurrence denotes a component, port, transform, or pipeline step. A conversion derivation can recover the owning analysis subject:

```text
pipeline component
  -> owns analysis port
  -> incident junction
  -> carries GraphicDocument
```

or, for a step:

```text
pipeline step
  -> belongsTo GraphicDocument
```

The conversion is proof-producing. The menu can explain:

```text
Switch linked workspace to “Population by region”
  because this pipeline step belongs to that document.
```

The repository’s current step presentation should include owning document identity for this reason. A bare step ID is insufficient when IDs are only document-local or when the ambient active document can differ.

## 32.9 Rebinding is not analysis migration

Suppose the user chooses a raw dataset rather than an existing complete document. The target source has fields:

```text
municipality
residents
land_area
```

There is no target `GraphicDocument` already defining:

```text
sum residents grouped by municipality
bar x municipality y residents_total
```

Simply replacing `source:regional-census` inside the existing census document is unsafe. The transform refers to `region` and `population`; the encodings refer to `region` and `population_total`.

The product needs a different command:

```text
Fork analysis onto source
```

It performs a schema-aware migration.

## 32.10 Analysis contract

The census workspace can expose a reusable contract:

```ts
const regionalPopulationContract = analysisContract({
  id: "regional-population.v1",
  fields: {
    category: fieldRequirement({
      semanticType: "nominal",
      aliases: ["region", "city", "municipality", "district"],
    }),
    amount: fieldRequirement({
      semanticType: "quantitative",
      aliases: ["population", "residents", "inhabitants"],
    }),
  },
  output: {
    total: derivedField({
      semanticType: "quantitative",
      expression: sum(field("amount")),
    }),
  },
});
```

A compatibility query returns candidates and evidence:

```text
category <- municipality
  because semantic type nominal and alias similarity

amount <- residents
  because semantic type quantitative and alias similarity
```

Automatic mapping should have a confidence threshold and never silently choose among materially ambiguous fields.

## 32.11 Transactional migration

After mapping, the command constructs a fresh document:

```json
{
  "kind": "analysis.forkOntoSource",
  "sourceDocument": "doc:census-population",
  "targetSource": "source:municipal-register",
  "fieldMapping": {
    "region": "municipality",
    "population": "residents"
  },
  "resultDocument": "doc:municipal-population",
  "rebind": "junction:main-analysis"
}
```

The pure preparation phase:

1. validates source and target revisions;
2. compiles the old document to discover actual dependencies;
3. applies the field mapping to transforms, views, and references;
4. allocates stable fresh IDs where necessary;
5. compiles the candidate new document;
6. confirms that `population_total` is still produced and accepted by the `y` channel;
7. builds one atomic graph and document delta;
8. records inverse or provenance metadata.

Only after successful compilation does the command create the new document and rebind the junction. Failure leaves the existing workspace unchanged.

## 32.12 Template form

A reusable workspace should separate internal wiring from its external subject slot:

```text
Template: Regional population analysis

Input slot
  analysis : GraphicDocument satisfying regional-population.v1

Internal components
  chart
  table
  pipeline
  encoding

Internal junction
  mainAnalysis

Wiring
  each component.analysis -> mainAnalysis
  template.analysis       -> mainAnalysis
```

Instantiation with an existing document performs ordinary open-system composition. Instantiation with a raw source first runs the contract-driven document constructor and then binds the resulting document.

The template can itself be presented as an entity. Actions include:

```text
Instantiate with document…
Instantiate on source…
Open as mirror
Fork current instance
Inspect requirements
Export template
```

## 32.13 Duplicate workspace semantics

The product should offer distinct commands:

### Mirror workspace

Creates another layout observation of the same components, junction, and document. Rebinding either location affects both.

### Duplicate layout

Copies placements but may continue referencing the same logical components. This is close to the current `cloneSpace` behavior and should be labeled as sharing state.

### Fork workspace

Copies components, ports, internal junctions, and optionally documents. The fork starts with census data but can later rebind independently.

### Instantiate template

Creates fresh components and junctions from a symbolic template and binds its external slot to a chosen existing or newly constructed document.

For the stated goal—“duplicate the same workspace but use different datasets”—**fork** or **template instantiation** is the correct operation, not a geometry clone.

## 32.14 Selection linking is another protocol

The chart and table may also share row or category selection. That is not the `analysisSubject` protocol.

Add ports such as:

```text
chart.selectionOut : SelectionSet<DatumKey | CategoryKey>
table.selectionIn  : SelectionSet<DatumKey | CategoryKey>
```

A separate junction carries selection state. Conversion rules may map a chart category to matching table rows. This preserves independent decisions:

- share the analysis but not selection;
- share selection but compare two related analyses;
- link filters but keep chart zoom local.

A generic `linked: true` flag cannot express these configurations.

## 32.15 Explanation visible to a user

A diagnostic panel could report:

```text
Chart “Population by region” observes document “Population by region”
  through port chart-1.analysis
  connected to link group “Main analysis”
  which currently carries doc:census-population.

Encoding editor is linked to the same subject.

The y encoding is valid because:
  population_total is produced by aggregate-population;
  aggregate-population sums quantitative field population;
  channel y accepts quantitative fields.
```

After rebinding, the same explanation graph changes at the junction edge and downstream derivations. This is a practical consequence of evidence-aware fixed-point semantics.

## 32.16 Worked-example conclusion

The census workspace demonstrates the division of responsibilities:

- **ports and junctions** express which applications share an analysis subject;
- **least-fixed-point rules** derive observation, eligibility, actions, and explanations;
- **presentations** let users select ports, documents, sources, steps, and templates semantically;
- **graph rewrites** implement link, detach, rebind, mirror, fork, and instantiate;
- **lenses** implement local lawful edits inside the currently observed document;
- **migration commands** preserve an analysis across a different source schema;
- **incremental execution** updates all projections from one small base delta.

No component has to know the identities or implementation types of the other linked components.

---

# 33. Mapping the proposal onto the current repository

The proposal is intentionally not constrained to the current decomposition. A migration still benefits from recognizing which existing concepts already carry the right information.

## 33.1 Concept map

| Current PBUI/Datalab concept | OPK interpretation | Recommended change |
|---|---|---|
| `PresentationReference<T>` | nominal entity reference plus sort | Preserve as a compatibility shape; move type membership into schema relations. |
| Rendered `<Presentation>` | semantic occurrence | Give every occurrence explicit identity, denotation, surface, role, and geometry registration. |
| Descriptor `label`/rendering | renderer projection | Keep outside the logical closure; consume saturated projections. |
| Descriptor identity domain/key | schema key and entity identity policy | Preserve; validate keys centrally and version migrations. |
| Presentation type descriptor | mixed classifier, renderer, actions, conversions | Split into schema vocabulary, renderers, command rules, and derivations. |
| `PresentationSelector` | goal formula or compiled query | Add a serializable query AST; retain lambdas only through the foreign boundary. |
| Selector `prepare` | query planning or foreign index construction | Compile core goals automatically; make opaque indexes declare dependencies and invalidation. |
| subtype map | `subtype` base relation plus transitive closure | Derive reachability under a typed positive rule. |
| action rules | command-applicability rules | Make preconditions, authority, operands, and explanations explicit data. |
| verbs | serializable commands/events | Preserve and strengthen with schemas, revisions, effects, and postconditions. |
| conversion graph | derivation relation with path annotations | Represent edges as typed rules and select paths under explicit ordered cost policy. |
| `pbui.accept()` Promise | interpreter for an interaction program | Preserve a convenience adapter while moving semantics into goals and effect operations. |
| one active accept context | runtime policy | Represent ownership and nesting explicitly rather than as a hidden singleton limitation. |
| `AppDescriptor` | component type declaration | Replace `docBound` with named typed ports and projection/lens declarations. |
| `AppView` | logical component/view instance | Preserve distinction from placement; normalize instance ownership and ports. |
| layout leaf | placement occurrence | Keep geometry and logical view identity separate. |
| `documentBindingId` | junction identity for one protocol | Generalize to explicit `Junction` records and typed incidence edges. |
| `documents: Record<string, DocId>` | port-role subjects stored redundantly | Move subject to junction; derive what each component observes. |
| layout reducers | hand-written graph rewrites | Wrap or generate from typed command/rewrite declarations. |
| `GraphicDocument` | domain-specific analytical IR and subject entity | Preserve; add stable lens families, contracts, revisions, and migration commands. |
| Graphic compiler | foreign deterministic compiler/solver | Declare dependencies, version, diagnostics, and optional certificates. |
| analysis logical plan and ports | execution IR | Preserve separately from UI port topology; connect via subject/result relations. |
| portable bundle collector/hydrator | graph export, copying, and template instantiation | Reuse as the seed of generic graph-copy policies. |
| `cloneSpace` | layout mirror/copy retaining logical references | Rename or expose sharing semantics; do not present as an independent workspace fork. |
| Redux normalized state | base instance storage | Retain as one interpreter; emit relation deltas and maintain derived closure beside it. |

## 33.2 `src/presentation/types.ts`

This file already contains the enhanced vocabulary for:

- semantic identity;
- selectors with `where` and `prepare`;
- action rules;
- named weighted conversions.

It is the natural place to introduce a compatibility layer, but it should not become the permanent formal kernel. The mixed generic types make every descriptor responsible for several interpreters.

A staged replacement could add:

```ts
export interface CoreGoalReference {
  kind: "core-goal";
  term: GoalTerm;
}

export type SelectorLike<T> =
  | PresentationSelector<T>
  | CoreGoalReference;
```

Legacy selectors compile to foreign predicates. New selectors compile to relation queries.

## 33.3 `selectors.ts`

The existing prepared-selector implementation establishes useful operational behavior:

- preparation once per accept operation;
- optional semantic identity memoization;
- exact or subtype-aware matching;
- payload re-evaluation at commit.

OPK should preserve these observable guarantees. Internally:

- type matching becomes a query over `hasSort` and `subtype*`;
- preparation becomes plan compilation;
- memoization keys come from entity identity plus dependency revisions;
- re-evaluation becomes evidence revalidation.

The legacy selector adapter can emit an assumption-tagged foreign predicate.

## 33.4 `registry.ts`

The registry currently owns subtype closure, identity comparison, descriptors, and selector-driven action rules. It is effectively a small semantic database implemented by maps and callbacks.

Refactoring target:

```text
Schema registry
  sorts, relations, protocols, command schemas, effect schemas

Theory registry
  positive rules, stratified queries, conversion derivations

Renderer registry
  labels, React projections, occurrence renderers

Foreign registry
  predicates, compilers, effect handlers, indexes
```

These registries may share one plugin manifest, but their semantics should remain separate.

## 33.5 `conversions.ts`

The current bounded weighted search is a sound product improvement. It should become an interpreter over declared conversion edges rather than disappear.

Near-term changes:

- define hard guards separately from path costs;
- include lossiness and confirmation requirements;
- return a derivation object rather than only a converted reference;
- record foreign assumptions;
- key caches by dependency fingerprints;
- expose alternative minimal paths for debugging;
- continue re-running occurrence-specific conversion at commit.

Eventually, simple conversions can be generated from relational rules, while product-specific conversions remain foreign solvers.

## 33.6 `createPbui.tsx`

This file currently combines React context, occurrence collection, highlighting, gestures, Promise settlement, and active-operation ownership.

A compatibility interpreter can retain the public API:

```ts
const value = await pbui.accept({ selector, prompt });
```

but implement it as:

```text
compile selector to goal
issue OpenInputContext effect
subscribe to eligible occurrence projection
interpret gesture
choose derivation
revalidate
return decoded value
```

Longer term, interaction programs should be composable data or algebraic-effect computations rather than nested Promise callbacks. The React provider remains one handler.

## 33.7 Datalab `pbui/types.ts` and `pbui/registry.ts`

The Datalab presentation vocabulary should be converted into schema sorts and keys. Examples:

```text
field
sourceAsset
sourceCoordinate
graphicDocument
datumKey
categoryValue
pipelineStep
analysisPort
template
componentInstance
junction
```

The existing identities are valuable source material. The important correction is ownership context:

```text
pipelineStep identity = (document ID, step ID)
encoding target identity = (document ID, view ID, channel)
field identity = stable field ID, or (document ID, field name) during migration
```

A step payload containing only `stepId` should be deprecated.

## 33.8 `pbui/verbs.ts`

Serializable verbs are among the repository’s strongest design choices. They should become command instances with:

- command schema ID and version;
- typed operands;
- actor and capability context;
- expected revisions;
- idempotency key where effects are retried;
- evidence or derivation references;
- result and diagnostic schema.

The current verb dispatcher can remain as an effect/command handler during migration.

## 33.9 `appkit/registry.ts`

`AppDescriptor` presently distinguishes document-bound applications with a Boolean-like property. Replace this with named ports:

```ts
componentType({
  id: "chart",
  ports: {
    analysis: port.input("analysisSubject", {
      cardinality: "exactly-one",
      defaultJunction: "private",
    }),
    selection: port.duplex("selectionSet", {
      cardinality: "optional",
    }),
  },
  projections: {
    model: chartProjection,
  },
  lenses: {
    rootView: chartViewLens,
  },
});
```

Table, pipeline, and encoding applications can expose the same analysis protocol while differing in optional ports and editor lenses.

World-scoped applications such as a source catalog expose no `analysisSubject` port. A future document-scoped dataset application does.

## 33.10 `store/layout.ts`

`AppView` correctly separates logical view identity from placement identity. Preserve that distinction.

The current binding representation duplicates the same `documents` map into each member of a binding group. This works for one protocol but complicates generalization and creates redundant truth.

Normalize toward:

```ts
interface ComponentInstance {
  id: ComponentId;
  type: ComponentTypeId;
  state: JsonValue;
}

interface PortInstance {
  id: PortId;
  component: ComponentId;
  name: string;
  protocol: ProtocolId;
}

interface Junction {
  id: JunctionId;
  protocol: ProtocolId;
  subjects: readonly EntityRef[];
}

interface Incidence {
  port: PortId;
  junction: JunctionId;
}
```

A compatibility selector can continue to compute `view.documents.primary` from the junction while old application code is migrated.

The current reducers map naturally:

```text
setViewDocument      -> RebindJunction
linkViewDocuments    -> ConnectPorts or MergeJunctions
unlinkViewDocuments  -> DetachPort with fresh private junction
createLinkedDuplicate-> MirrorPlacement or MirrorView
createDuplicate      -> DuplicateComponent
cloneSpace           -> DuplicateLayoutSharingViews
```

Names should expose their identity and sharing semantics.

## 33.11 `DocBar.tsx`

The enhanced chain interaction is a useful first-time experience and should remain. Its implementation can become generic:

```text
render LinkIndicator occurrence for analysis port
query available commands for that occurrence
run LinkWith partial command
open goal for compatible destination port
commit ConnectPorts
```

The DocBar should not be the semantic location of document-link rules. Other renderers—tile title, outline tree, workspace inspector, command palette—should expose the same commands by denoting the same port.

## 33.12 `model/graphic.ts`

`GraphicDocument` is already a declarative authoring IR with stable IDs for sources, transforms, views, fields, operations, values, and parameters. It should remain a domain aggregate rather than be exploded indiscriminately into generic graph facts.

Additions that support OPK:

- document revision and compiler version;
- explicit field provenance and stable output-field identities through edits;
- lens families for views, transforms, encodings, and parameters;
- a dependency extractor;
- analysis contracts and schema requirements;
- migration result diagnostics;
- canonical serialization and semantic hash;
- command-level patches instead of broad object replacement.

The compiled logical graph can expose fact projections used by selection and explanation without becoming the authoritative editor state.

## 33.13 `model/graphicAuthoring.ts`

The current source replacement behavior resets transforms, views, encodings, and parameters. Preserve it only as an explicitly destructive command such as:

```text
Reset document from source
```

Add a separate preserving path:

```text
Analyze compatibility
Map fields
Construct migrated document
Compile and validate
Commit fresh document
Optionally rebind a junction
```

These operations have different laws, failure modes, and user expectations.

## 33.14 `analysis/*`

The analysis package already compiles declarative logical operations to an execution environment and has explicit execution ports. Do not conflate these with workspace wiring ports:

- **workspace ports** connect application components to semantic subjects and interaction streams;
- **analysis execution ports** connect logical operators or runtime assets in a query plan.

A relation can connect the two levels:

```text
component observes GraphicDocument
GraphicDocument compilesTo LogicalPlan
LogicalPlan executesTo ResultHandle
component projection consumes ResultHandle
```

Each level keeps its own type system and performance engine.

## 33.15 `store/bundles.ts`

The portable collector already converts runtime IDs to indices, preserves document-binding equivalence classes, allocates fresh IDs, and rewires imported views. This is close to a graph-copy interpreter.

Generalize it by making policies explicit:

```ts
interface CopyPolicy {
  node(type: NodeType): "copy" | "share" | "omit" | "slot";
  externalEdge(edge: Edge): "preserve" | "drop" | "parameterize";
  subject(junction: Junction): "share" | "copy" | "slot";
}
```

Then implement:

- workspace mirror;
- layout duplicate;
- independent workspace fork;
- template export;
- template instantiation;
- stage export;
- cross-account import.

The same normalized graph copier should be tested independently of Redux.

## 33.16 Remote protocol

The current remote workbench protocol does not encode binding equivalence. A generalized protocol needs records for:

```text
component instances
ports
junctions
incidence
subjects or subject slots
schema/plugin versions
command/event revisions
```

An additive `document_binding_id` field can preserve the existing specialized behavior as an intermediate step. A generic port graph is the longer-term representation.

Protocol evolution must specify how older clients interpret unknown component types, ports, and commands. Opaque preservation is preferable to destructive dropping.

## 33.17 Compatibility architecture

A realistic transition uses adapters:

```text
Legacy descriptor
  -> generated schema sort and renderer registration
  -> foreign selector/action/conversion declarations

Legacy AppView
  -> generated component instance and primary analysis port
  -> generated junction from documentBindingId

Legacy verb
  -> command handler adapter

Legacy Redux reducer
  -> command transition adapter producing before/after delta
```

Adapters let the new query and explanation tooling operate before every product surface has been rewritten.

## 33.18 What should not be preserved

The migration should not preserve these accidental constraints as architectural principles:

- one active accept operation globally;
- exact descriptor ownership of every action;
- ambient active-document lookup for semantically owned objects;
- document binding represented by repeated maps in every view;
- source replacement as destructive reset under a generic name;
- workspace clone terminology that hides shared logical identities;
- arbitrary callback semantics without dependency declarations;
- React lifecycle as the authoritative interaction state machine.

The goal is behavioral compatibility where behavior is intentional, not structural fidelity to the current implementation.

---

# 34. Verification strategy and theorem inventory

The architecture is valuable only if its proof ambitions are specific. This section lists candidate properties, their assumptions, and an appropriate verification method.

No theorem listed here is claimed to have been machine-proved for the supplied repository.

## 34.1 Layers of assurance

Use several levels rather than one binary label “verified”:

### By construction

The API makes an invalid state unrepresentable or rejects it during schema compilation.

### Kernel theorem

A property is proved once for the generic core under explicit assumptions.

### Generated obligation

A plugin or component declaration creates a finite obligation checked automatically or reviewed manually.

### Bounded model check

A tool searches finite instances or executions for counterexamples.

### Property test

Random valid instances and command traces test a law against an executable interpreter.

### Runtime check

A boundary validates codecs, revisions, capabilities, postconditions, or declared dependencies.

### Audit evidence

A derivation or event trace records why a particular action was allowed and what assumptions it used.

These levels are complementary. A bounded Alloy check is not an unbounded proof; a TypeScript type is not a temporal guarantee; an informal categorical analogy is not a theorem.

## 34.2 Schema well-formedness

**Statement.** Every relation position, entity reference, port protocol, command operand, and effect payload refers to a declared sort or schema.

**Method.** Schema compiler plus runtime codecs at untyped boundaries.

**Obligations.** Plugins use globally stable IDs, declare versions, and do not introduce inconsistent duplicate definitions.

## 34.3 Rule type soundness

**Statement.** If all premises of a rule are well-sorted facts, every fact emitted by its conclusion is well sorted.

**Method.** Check variable sorts and relation signatures when compiling the rule AST.

**Proof sketch.** Induction on the syntax of terms and formulas. Every variable occurrence is constrained to one compatible sort; substitutions preserve relation signatures.

This theorem is straightforward precisely because arbitrary JavaScript cannot appear as an untyped rule conclusion.

## 34.4 Monotonicity of the positive theory

**Statement.** For base instances `I <= J`, the immediate-consequence operator satisfies:

\[
T_\Gamma(I)\le T_\Gamma(J).
\]

**Assumptions.** Rules use positive relational premises and monotone foreign oracles over stated orders. No hidden negation, revocation read, or side effect participates.

**Method.** Structural induction over formula syntax plus trusted obligations for monotone foreign oracles.

**Consequence.** Least fixed points exist on a complete lattice of fact sets.

## 34.5 Fixed-point existence

**Statement.** The closure operator

\[
C_\Gamma(I)=\mu X.\;I\cup T_\Gamma(X)
\]

exists.

**Assumptions.** The fact domain is a complete lattice and the operator is monotone.

**Method.** Knaster–Tarski at the metatheory level.

This establishes existence, not a finite runtime bound.

## 34.6 Finite termination

**Statement.** A finite positive rule theory over a finite active entity universe, with no fresh-name generation in rules, reaches closure after finitely many new fact insertions.

**Method.** Count the finite set of possible well-sorted ground atoms. Each strict iteration adds at least one previously absent fact; no atom is removed.

**Bound.** The crude bound is the number of possible ground atoms. Practical evaluation depends on rule and index structure.

## 34.7 Soundness of derived evidence

**Statement.** Every evidence DAG returned for a derived fact corresponds to a valid sequence of base facts, rule instances, conversions, and declared foreign assumptions that derives the fact.

**Method.** Induction on evidence construction.

**Runtime check.** A standalone evidence checker can replay a proof DAG against a schema and theory version.

## 34.8 Relative completeness of evidence

**Statement.** If the evaluator reports a fact as true under a mode that promises witnesses, it can return at least one finite evidence DAG for that fact.

**Assumptions.** Rules are finitary; foreign true results provide assumption leaves; provenance budget is not exhausted.

**Caveat.** Complete enumeration of all derivations may be exponential or infinite in cyclic theories. The API must distinguish one witness from complete provenance.

## 34.9 Closure laws

For each fixed theory `Γ`, closure should satisfy:

### Extensive

\[
I\le C_\Gamma(I).
\]

### Monotone

\[
I\le J\Rightarrow C_\Gamma(I)\le C_\Gamma(J).
\]

### Idempotent

\[
C_\Gamma(C_\Gamma(I))=C_\Gamma(I).
\]

**Method.** Standard least-fixed-point reasoning, subject to the chosen instance order and operator definition.

These laws justify treating saturation as a closure operator.

## 34.10 Reflection theorem

**Target statement.** Saturated models and appropriate structure-preserving maps form a reflective full subcategory of raw instances, with `CΓ` as reflector.

**Required work.** Define:

- the category of instances;
- morphisms and their preservation obligations;
- the saturated subcategory;
- how closure acts on morphisms;
- the unit map `I -> J CΓ(I)`;
- the universal factorization.

**Important assumption.** The theory must be functorial with respect to the chosen morphisms. Arbitrary nominal tests or callbacks can break this.

**Method.** Mathematical proof, potentially formalized in Lean or Rocq after the kernel stabilizes.

## 34.11 Colimit preservation

**Statement.** If `CΓ` is a left adjoint reflector, it preserves colimits that exist in the raw instance category:

\[
C_\Gamma(\operatorname{colim}D)
\cong
\operatorname{colim}(C_\Gamma D).
\]

For a diagram already in saturated models, compute its colimit by taking the raw colimit and closing it.

**Use.** Modular workspace assembly and plugin/component composition.

**Non-use.** Unlinking, deletion, and arbitrary state mutation are not inferred to preserve colimits.

## 34.12 Protocol composition safety

**Statement.** Connecting compatible ports through a well-typed junction yields a well-typed open system.

**Assumptions.** Boundary maps preserve port sorts and protocol constraints; subject cardinalities are respected.

**Method.** By-construction type checking plus a structural theorem for the selected cospan or hypergraph category. Alloy checks find omitted edge cases.

## 34.13 Rewrite invariant preservation

For each command rewrite `r` and invariant `P`:

\[
P(W)\land \operatorname{pre}_r(W)
\Rightarrow
P(r(W)).
\]

Examples:

- exclusive ports have at most one junction;
- no incidence edge targets a missing node;
- a junction only carries protocol-compatible subjects;
- forked internal references target copied nodes;
- every placement references a live logical view.

**Method.** Generated proof obligations where simple; bounded Alloy analysis; property-based command traces; runtime postcondition checks in development.

## 34.14 Critical-pair analysis

**Statement.** For pairs of rewrite rules whose matches overlap, either:

- the commands commute;
- their results can be joined to an equivalent state;
- a declared conflict policy resolves them;
- or concurrent execution must be serialized/rejected.

**Method.** Graph-rewrite critical-pair tools or a product-specific bounded model. Use results to define revision guards and collaboration policy.

## 34.15 Command authorization soundness

**Statement.** Every committed command has an authorization derivation valid at the commit revision and invokes only declared capabilities.

**Method.** Command interpreter enforces capability schemas and evidence revalidation. Temporal model checks races involving revocation between menu display and commit.

**Caveat.** The theorem trusts the authority supplying permission facts and the integrity of effect handlers.

## 34.16 Interaction settlement

**Statement.** Each input-context request settles at most once; cancellation and commitment are mutually exclusive terminal outcomes.

**Method.** TLA+ model plus implementation state-machine tests.

**Implementation technique.** Store one terminal state guarded by an atomic transition; ignore late gestures and effect completions.

## 34.17 Occurrence commitment

**Statement.** Semantic memoization never causes the payload of one occurrence to be returned when a different occurrence is committed.

**Method.** The current PBUI pattern already suggests the proof: cache admissibility by semantic identity, but rerun occurrence-sensitive conversion and extract the selected occurrence payload at commit. Property-test duplicate semantic entities rendered in different contexts.

## 34.18 Lens laws

For every declared lens family, state which laws it promises:

```text
lawful total lens
normalizing lens
partial validated lens
delta lens with observational laws
no lens claim; command-only editor
```

**Method.** Property-based tests over generated valid `GraphicDocument` instances; optional equational proof for generated structural lenses.

**Caveat.** A lens using a foreign normalizer carries that assumption.

## 34.19 Migration preservation

A source-migration command should state a preservation contract. For example:

```text
all mapped source dependencies resolve
all transform outputs type-check
all view encodings refer to produced fields
root view remains present
unmapped optional references are reported, never silently redirected
old document remains unchanged
new document has fresh nominal identity
```

**Method.** Compiler checks, property tests over schema renamings, and golden fixtures. Exact result equality is not expected when schemas differ.

## 34.20 Incremental correctness

**Statement.** Incremental maintenance is observationally equivalent to batch recomputation after every valid delta.

**Method.** Generic proof for selected operator algebra where possible; random differential testing against a simple reference evaluator; Lean-checked primitives if adopting a DBSP-like approach.

**Coverage.** Test insertion, deletion, junction rebind, permission revocation, plugin addition/removal, occurrence churn, and recursive subtype or ownership closure.

## 34.21 Deterministic ranking

**Statement.** Given the same saturated world, goal, gesture, and policy version, candidate ranking and chosen conversion path are deterministic.

**Method.** Require total tie-break rules; property-test insertion-order changes; canonicalize IDs and weights.

A partial order without tie-breaking can produce non-replayable menus.

## 34.22 Stale-result safety

**Statement.** No effect result commits to an output whose current dependency fingerprint differs from the ticket’s fingerprint, unless a handler supplies and validates an explicit merge operation.

**Method.** TLA+ interleaving model and integration tests with controlled delayed promises.

This is a high-value theorem for linked analytical workspaces.

## 34.23 Behavioral refinement during migration

Let `Old` be the current runtime and `New` the compatibility interpreter. For a constrained feature subset, define an observation function:

```text
visible semantic candidates
highlighted occurrences
selected entity and action
committed verb
cancellation/rejection result
```

**Target.** Every old trace is matched by a new trace with the same observations, or differences are documented intentional changes.

**Method.** Golden trace replay, differential tests, and a simulation relation at the model level.

## 34.24 Plugin conservativity

**Statement.** A plugin classified as conservative does not change derivable facts in pre-existing predicates over pre-existing entities.

**Method.** Static manifest restrictions plus theory-difference analysis. Bounded counterexample search can detect common violations.

A plugin that contributes new action rules for core entities is intentionally non-conservative and should declare that fact.

## 34.25 Replicated convergence

For each replicated state type, state an independent convergence theorem. A generic example for a join-semilattice CRDT is:

```text
merge is associative, commutative, and idempotent
local updates are inflationary in the state order
all delivered updates eventually yield equal replicas
```

Port rewiring with exclusive cardinality is not automatically a CRDT. It may require arbitration, multi-value conflicts, or coordination.

## 34.26 Privacy and noninterference

A stronger system may aim for:

> Changes to facts outside a component’s declared read capabilities do not alter its observable projection.

This is a noninterference property. It requires disciplined capabilities and no ambient store access in renderers or foreign code.

**Method.** Static dependency declarations, dynamic read instrumentation, information-flow analysis for selected core terms, and security review of foreign handlers.

## 34.27 Tool allocation

| Concern | Primary tool | Secondary evidence |
|---|---|---|
| Schema and term typing | TypeScript schema compiler, runtime codecs | property tests |
| Structural topology | Alloy | graph-rewrite tests |
| Async races and liveness | TLA+ | deterministic integration tests |
| Fixed-point metatheory | mathematical proof | Lean/Rocq for stable kernel |
| Lens laws | property-based testing | generated equational proof for structural lenses |
| Incremental equivalence | differential testing | mechanized operator proofs |
| UI compatibility | trace replay | Storybook interaction tests |
| Foreign assumptions | runtime instrumentation | code review, fuzzing, sandboxing |
| Accessibility | semantic projection tests | browser/assistive-technology tests |
| Performance | benchmarks and budgets | query-plan diagnostics |

## 34.28 Proof artifact versioning

Every evidence object or checked theorem instance should identify:

```text
schema version
rule-theory version
plugin manifest hash
foreign operation versions
command schema version
compiler or checker version
base snapshot or revision
```

A proof for one theory does not automatically validate a later plugin set. Derived caches and portable evidence should be rejected or rechecked when versions differ.

## 34.29 Trusted computing base

The initial trusted computing base includes:

- schema and rule compilers;
- batch closure reference interpreter;
- evidence checker;
- command/rewrite interpreter;
- identity and codec implementations;
- foreign declarations and their actual code;
- persistence and transport decoders;
- authority and capability providers.

Mechanization can shrink portions of this base, but React, DuckDB, browser APIs, and product plugins remain substantial trusted components. The design should document rather than obscure them.

## 34.30 Verification priority

The first high-value properties are not the most abstract ones. They are:

1. no stale asynchronous result overwrites a newly rebound linked workspace;
2. link, detach, fork, and mirror preserve their advertised identity semantics;
3. command authorization is checked at commit;
4. semantic identity caching never substitutes the wrong occurrence payload;
5. migrated GraphicDocuments compile before replacing live subjects;
6. incremental and batch eligibility agree;
7. portable graph copies preserve internal equivalence classes and fresh identity.

The reflection and colimit theorem should guide the kernel design, but these operational properties should gate production adoption.

---

# 35. Migration roadmap

A proof-oriented rewrite should not begin by replacing React components or by introducing a category-theory library. It should first extract semantics from code paths that already work, establish reference behavior, and then replace mechanisms behind compatibility adapters.

The phases below are ordered to produce product value and verification leverage early.

## 35.1 Phase 0: define the compatibility envelope

Before changing architecture, record what the current system intentionally guarantees.

Create golden scenarios for:

- direct and subtype selector acceptance;
- arbitrary `where` and prepared selectors;
- semantic identity memoization;
- conversion ranking and commit-time payload recovery;
- descriptor-local and rule-contributed action ordering;
- cancellation and rejection;
- linked chart/pipeline document switching;
- unlinking;
- ordinary and linked duplication;
- portable bundle round trips;
- census chart, table, pipeline, and encoding projections.

Record normalized traces rather than pixel snapshots alone:

```text
registered occurrences
active selector or goal
eligible semantic identities
chosen occurrence
conversion derivation
verb dispatched
state delta
visible projection
```

### Exit gate

A deterministic test harness can replay the major interaction paths without relying on timing accidents or opaque DOM selectors.

## 35.2 Phase 1: introduce nominal schema and entity references

Add a small package, for example `packages/opk-schema`, containing:

- sort declarations;
- relation declarations;
- entity references;
- stable identity keys;
- runtime codecs;
- schema versioning;
- plugin manifest composition.

Initially, generate these declarations from the Datalab presentation vocabulary and app registry.

```ts
const datalabSchema = schema.define({
  sorts: {
    graphicDocument: nominal(),
    field: nominal(),
    pipelineStep: nominal(),
    component: nominal(),
    analysisPort: nominal(),
    junction: nominal(),
    occurrence: nominal(),
  },
  relations: {
    owns: relation("component", "analysisPort"),
    denotes: relation("occurrence", "entity"),
    belongsToDocument: relation("field", "graphicDocument"),
  },
});
```

Do not add fixed-point recursion yet. Use normalized maps and direct indexes.

### Exit gate

Every existing presentation value can be losslessly converted to a nominal reference with an explicit identity policy. Pipeline steps and other document-local entities include ownership context.

## 35.3 Phase 2: separate occurrences from entities

Create one occurrence service shared by the old and new runtimes. Registration includes:

```text
occurrence ID
entity reference
presentation role
surface and component
geometry/focus metadata
local payload handle
lifetime token
```

The existing `<Presentation>` component becomes an adapter to this service.

### Product benefit

Duplicate semantic entities in different surfaces can be inspected, focused, and committed reliably. Accessibility and debug tooling obtain one occurrence inventory.

### Exit gate

All current click and keyboard acceptance tests pass with the normalized occurrence service, including cases where two occurrences denote the same entity but carry different local payloads.

## 35.4 Phase 3: add a serializable goal language

Implement a deliberately small query AST:

```text
sort membership
equality and inequality
relation atoms
and/or
bounded existential variables
parameters
stratified negation for nonrecursive queries
ranking annotations
foreign predicate leaves
```

Compile common selectors:

```text
type selector          -> hasSort / subtype closure goal
filter lambda          -> foreign predicate leaf
prepared selector      -> foreign index leaf
multiple types         -> disjunction
exact type             -> equality without subtype traversal
```

Keep `pbui.accept()` unchanged at the call site.

### Exit gate

Every selector in repository stories and tests either compiles to a core goal or is explicitly reported as a foreign assumption. Candidate results match the old evaluator for the compatibility envelope.

## 35.5 Phase 4: implement a batch relational reference engine

Build the simplest correct interpreter before optimizing:

- immutable fact sets;
- positive rule evaluation;
- finite worklist closure;
- one-witness evidence DAGs;
- goal evaluation;
- deterministic ordering;
- explicit incomplete/error results.

Move these mechanisms into rules:

- subtype transitive closure;
- component-to-subject observation;
- basic command applicability;
- ownership chains;
- common conversions.

Do not put analytical table rows into this engine.

### Exit gate

Batch-derived subtype, eligibility, action, and observation results match current behavior. Evidence can explain at least one census-field and one link-command result.

## 35.6 Phase 5: command schemas around existing verbs

Define command metadata while keeping existing reducers and verb handlers as interpreters:

```text
command ID/version
operand schemas
precondition goal
authorization goal
effect capabilities
expected revisions
result schema
postcondition hooks
```

A command adapter:

1. evaluates preconditions;
2. invokes the old reducer or verb;
3. computes or receives a normalized delta;
4. checks development postconditions;
5. records a trace.

### Product benefit

Menus and automation use the same command inventory. Authorization and stale-state checks become centralized.

### Exit gate

All user-triggerable verbs in the selected feature slice have schemas and can be invoked without going through their original React button.

## 35.7 Phase 6: normalize component ports and junctions

Introduce explicit component, port, junction, and incidence tables beside `AppView`.

Migrate current document bindings deterministically:

```text
one component instance per AppView
one primary analysis port for each doc-bound app
one junction per effective documentBindingId
one carries edge from junction to selected primary document
```

For a transition period, derive `AppView.documents` and `documentBindingId` from the normalized graph or update both under one invariant-checked adapter.

### Product benefit

The UI can link any compatible component port, expose named link groups, and add selection/filter protocols without another special binding field.

### Exit gate

Current linked-selector stories pass entirely through generic `ConnectPorts`, `DetachPort`, and `RebindJunction` commands. A consistency assertion detects any divergence from legacy fields.

## 35.8 Phase 7: distinguish mirror, layout copy, component duplicate, and workspace fork

Rename product actions before implementing more copying behavior. Then build a generic graph copier from the portable bundle machinery.

Copy policy tests must cover:

- fresh nominal IDs;
- preserved internal junction equivalence classes;
- declared shared external entities;
- no accidental back-edges to original internals;
- stable source and document copy policies;
- deterministic index-based portable representation.

### Exit gate

The product offers at least:

```text
Open mirror
Duplicate component independently
Fork workspace
Instantiate template
```

and each operation has explicit tests for subsequent rebind isolation or sharing.

## 35.9 Phase 8: introduce GraphicDocument lenses and migrations

Add narrow command-producing lenses for:

- root view mark;
- encoding channels;
- view relation;
- transform fields and measures;
- parameters;
- reference lines.

Keep destructive source reset under a renamed explicit command. Add analysis contracts and a transactional `forkOntoSource` path.

### Exit gate

The census analysis can be forked onto a fixture with renamed compatible fields, compiled before commit, and rebound into a linked workspace atomically. Failed mappings leave the old workspace intact.

## 35.10 Phase 9: replace action and conversion registries with theory declarations

Convert common descriptor action rules to command-applicability rules. Convert straightforward conversions to derivation edges with evidence.

Retain adapters for:

- renderer-local actions;
- foreign product predicates;
- legacy conversion callbacks.

Add a conflict report showing when plugins change action ordering or minimal conversion paths.

### Exit gate

Descriptor modules no longer need to repeat global inspect/watch/link logic. The same available-command query drives context menus, command palette entries, and keyboard affordances.

## 35.11 Phase 10: incremental engine

After the batch semantics is stable, add:

- relation indexes;
- seminaive recursion;
- precise dependency revisions;
- deletion support by predicate class;
- shared query subscriptions;
- worker execution for large slices;
- differential tests against batch recomputation.

Do not discard the batch evaluator. It is the executable specification and recovery path.

### Exit gate

For randomized base deltas and command traces, incremental and batch public projections agree. Interaction latency and memory meet stated budgets on representative workspaces.

## 35.12 Phase 11: explicit interaction programs

Introduce an algebraic interaction DSL for multi-step flows:

```text
choose entity satisfying goal
ask confirmation
request text or number
invoke command
run effect
report progress
handle cancellation
```

Provide Promise, generator, and React-hook interpreters as needed. Migrate:

- link-with;
- choose field for encoding;
- fork analysis onto source;
- resolve ambiguous mapping;
- import template;
- destructive-delete confirmation.

### Exit gate

The same interaction program can run through the visual UI and a headless test interpreter. Cancellation semantics are model checked.

## 35.13 Phase 12: verification artifacts in CI

Add small checked models rather than one enormous formalization:

- Alloy: ports, junctions, copy and delete rewrites;
- TLA+: input settlement and stale analysis results;
- property tests: lens laws and graph-copy policies;
- differential tests: old/new compatibility and batch/incremental closure;
- evidence checker tests;
- schema/plugin compatibility checks.

Only after the kernel interfaces stabilize should a mechanized proof effort in Lean or Rocq formalize reflection, closure, or incremental operators.

### Exit gate

The CI failure message identifies a violated invariant with a minimal counterexample or replayable trace.

## 35.14 Phase 13: remote protocol and collaboration

Extend persistence and transport with normalized components, ports, junctions, and versions. Choose collaboration semantics per command family:

```text
server-serialized
optimistic with revision rejection
commutative CRDT
multi-value conflict
manual merge
```

Do not declare the whole workspace a CRDT. Exclusive rewiring and destructive migration require explicit policy.

### Exit gate

A remote round trip preserves linked groups and template boundaries. Concurrent rebind and detach scenarios have specified outcomes and checked traces.

## 35.15 Phase 14: retire mixed descriptors

Once a feature area uses:

- schema sorts;
- core goals;
- command rules;
- derivation conversions;
- explicit renderers;
- foreign manifests;

remove its legacy descriptor semantics. Keep a thin package for public compatibility only if external consumers require it.

### Exit gate

No core product behavior depends on ambient registry callbacks. Local escape-mode callbacks are visibly marked and excluded from portable templates and remote execution.

## 35.16 Suggested first vertical slice

The best first slice is the census linked workspace:

```text
chart + table + pipeline + encoding
one analysisSubject junction
field and step presentations
link, detach, rebind
one existing-document switch
one schema-aware fork onto source
```

It exercises entity identity, occurrences, goals, commands, ports, lenses, compilation, asynchronous results, and copying without requiring every Datalab application to migrate.

## 35.17 Migration governance

Every phase should publish:

- semantic decisions and names;
- compatibility changes;
- trusted assumptions;
- benchmark results;
- proof or model-checking status;
- persistence migration behavior;
- plugin API stability level.

A formal architecture can become less trustworthy than an ordinary one when theorem-like language outruns implemented checks. Status labels should remain exact.

---

# 36. Risks, limits, and rejected simplifications

The proposed architecture has substantial upside, but it can fail through overreach as easily as through under-design.

## 36.1 Risk: formalism without product leverage

A category, logic, or effect calculus can become an internal hobby while ordinary features remain harder to build.

Mitigation:

- each formal layer must remove duplicated product logic or enable a concrete tool;
- begin with link groups, command availability, explanations, and stale-result safety;
- maintain ergonomic builders and visual inspectors;
- benchmark developer effort, not only runtime;
- retain escape hatches with explicit status.

The criterion is not mathematical elegance alone. It is whether one declaration powers rendering, selection, automation, explanation, persistence, and verification more reliably than several hand-written mechanisms.

## 36.2 Risk: one universal model becomes a new monolith

A typed relational world can become a dumping ground for CSS state, data rows, network responses, and every local widget Boolean.

Mitigation:

- define strict ownership boundaries;
- keep bulk analytical data in its specialized engine;
- keep ephemeral purely visual state local unless it participates in semantic interaction;
- expose handles and revisions rather than duplicating large values;
- require a reason for every relation to enter the kernel.

The world model is a semantic coordination layer, not the only data structure in the application.

## 36.3 Risk: proof/runtime mismatch

A theorem about an ideal rule language does not cover:

- a buggy compiler;
- wrong identity keys;
- malformed persistence;
- foreign callbacks that violate declarations;
- React code that commits the wrong occurrence;
- remote authorization defects.

Mitigation:

- keep a small reference interpreter;
- check evidence independently;
- instrument foreign dependencies;
- test compiled against reference semantics;
- expose the trusted computing base;
- avoid marketing every guarantee as end-to-end verification.

## 36.4 Risk: monotonicity is over-applied

Many UI facts retract:

```text
permission revoked
occurrence unmounted
port detached
request cancelled
candidate becomes invalid
selected row removed
```

Positive fixed-point semantics describes closure at a snapshot, not an append-only history. The base snapshot can change by deletions, after which closure is recomputed or incrementally maintained with negative deltas.

CALM-style coordination conclusions apply only to carefully defined distributed programs and monotone outputs. They do not make every command coordination-free.

## 36.5 Risk: transfinite terminology obscures finite engineering

Ordinal-indexed constructions are relevant to general existence and induction arguments. They are usually irrelevant to a finite active UI snapshot.

Mitigation:

- state the lattice and operator whenever transfinite iteration is mentioned;
- state whether continuity or accessibility gives a smaller convergence ordinal;
- implement finite worklists or domain solvers;
- report widening and approximation explicitly;
- never represent browser iterations as ordinal objects for aesthetic reasons.

## 36.6 Risk: categorical structure is asserted too loosely

Words such as “colimit,” “pushout,” “adjunction,” and “functor” are easy to use metaphorically.

For every claimed construction, specify:

```text
category
objects
morphisms
relevant diagram
universal property
existence assumptions
implementation representation
what equivalence means
```

For example, linking may have a pushout semantics for open boundaries while being stored as an explicit junction graph. Unlinking is a rewrite, not “the inverse pushout.”

## 36.7 Risk: identity migration

Changing field identity from `(document, name)` to a stable field ID affects:

- bookmarks;
- action evidence;
- watchlists;
- portable templates;
- cached conversions;
- event logs;
- remote references.

Mitigation:

- version identity schemes;
- provide explicit alias/migration relations;
- never silently reuse an old key for a new entity;
- keep occurrence identity independent;
- retain provenance for migrated references.

## 36.8 Risk: plugin interaction explosion

Open rules and commands can interact in unexpected ways:

- new subtype edges widen selectors;
- lower-cost conversions change chosen commands;
- action rules shadow existing actions;
- foreign oracles add expensive dependencies;
- plugin removal retracts facts used by persisted templates.

Mitigation:

- classify extension points;
- namespace and version vocabulary;
- generate theory-difference reports;
- require explicit imports for rules affecting core predicates;
- cap derivation depth and candidate counts;
- preserve unknown plugin data opaquely in persistence;
- allow workspaces to pin plugin manifests.

## 36.9 Risk: performance cliffs

A declarative query that is small in source can induce a large join or provenance graph.

Mitigation:

- compile and inspect query plans;
- establish relation cardinality expectations;
- restrict recursion and negation profiles;
- demand-drive active goals;
- expose budget exhaustion as incomplete;
- use bulk-engine handles for datasets;
- retain hand-optimized foreign solvers where justified.

A declarative API must expose enough structure for optimization and enough diagnostics for developers to understand cost.

## 36.10 Risk: developer ergonomics

Raw relational ASTs and graph rewrites are verbose. Most developers should use typed builders and domain modules:

```ts
fieldGoals.inObservedDocument()
workspaceCommands.linkAnalysis()
graphicLenses.encodingChannel("x")
```

The builder should compile to inspectable data. It should not hide another arbitrary callback system.

Development tools should show:

- schema browser;
- current facts;
- derivation explanation;
- port graph;
- command precondition failures;
- dependency and cache keys;
- rewrite preview;
- event trace;
- query-plan cost.

## 36.11 Risk: attribute modeling becomes cumbersome

Categorical graph models handle topology cleanly, but practical attributes include strings, JSON, geometry, SQL plans, and React component IDs.

Options should be mixed deliberately:

- first-class nodes for semantically queried attributes;
- typed scalar attributes with codecs for ordinary metadata;
- opaque handles for large or host-specific values;
- external stores for bulk data;
- stable hashes when equality or invalidation is needed.

Do not force every JSON leaf into a categorical arrow to preserve ideological purity.

## 36.12 Risk: bidirectional laws do not fit migrations

A preserving source migration may normalize, drop optional features, request mappings, or create new identities. It is not a simple lawful lens.

Mitigation:

- use lenses for local stable views;
- use transactional commands for migrations and topology changes;
- state observational laws and preservation contracts separately;
- expose partial results and diagnostics;
- never use “lens” as a synonym for setter.

## 36.13 Risk: security assumptions leak through renderers

A React renderer with access to the complete Redux store can bypass the kernel’s capability model.

Mitigation:

- supply narrow projections;
- make command dispatch capability-aware;
- instrument or lint ambient store imports in plugin packages;
- isolate untrusted plugins in workers or frames where warranted;
- validate every remote command server-side;
- treat client evidence as an explanation, not sole authority.

## 36.14 Risk: accessibility becomes a second semantic implementation

If keyboard navigation and screen-reader descriptions are coded independently from pointer eligibility, they drift.

Mitigation:

- derive all modalities from the same eligible-occurrence and command relations;
- store semantic labels and rejection reasons in projections;
- test focus order and announcements against the occurrence graph;
- permit modality-specific gestures without modality-specific truth.

## 36.15 Risk: collaboration semantics are underspecified

A local graph rewrite can be deterministic while concurrent remote rewrites conflict.

Examples:

```text
two users rebind one exclusive junction to different documents
one user detaches a port while another renames the link group
one user forks while another edits the source document
a permission revocation races with command commit
```

Mitigation:

- classify command families by concurrency semantics;
- use revisions and server arbitration by default;
- adopt CRDTs only for data types with stated merge laws;
- surface multi-value conflicts rather than inventing silent last-writer behavior;
- model critical interleavings.

## 36.16 Rejected simplification: “make everything Datalog”

Datalog-like rules are excellent for finite relational closure, but not every concern belongs there.

Poor fits include:

- long-running effects;
- fresh nominal identity creation;
- destructive topology changes;
- rich numerical optimization;
- React rendering;
- transactional schema migration;
- arbitrary stream behavior;
- user confirmation and cancellation.

Use the rule engine for derived snapshot facts and query planning, not as the sole programming language.

## 36.17 Rejected simplification: “make everything category theory”

Category theory supplies compositional structure and universal properties. It does not by itself choose:

- a user-visible conflict policy;
- a cache invalidation strategy;
- a keyboard traversal order;
- a source-field mapping heuristic;
- an authorization model;
- an error message.

Use categories to specify open composition, data migration, reflection, and law-preserving interpreters where those structures genuinely exist. Use ordinary algorithms and product policies elsewhere.

## 36.18 Rejected simplification: “Redux already is the architecture”

Redux provides a state container and reducer discipline. It does not provide:

- semantic entity/occurrence separation;
- typed open-component protocols;
- selector explanations;
- conversion derivations;
- bidirectional laws;
- model-checked asynchronous behavior;
- graph-copy semantics;
- plugin conservativity.

Redux can remain an implementation of the base store and command transition layer.

## 36.19 Rejected simplification: arbitrary lambdas plus annotations

Adding fields such as `pure: true` and `monotone: true` to arbitrary closures does not create a proof-oriented core.

Annotations are useful at an explicit foreign boundary, provided:

- core alternatives exist;
- assumptions propagate into evidence;
- dependencies and invalidation are enforced;
- portable and remote modes can reject unsupported callbacks;
- runtime checks can expose violations.

They are not a substitute for representing common semantics as data.

## 36.20 Rejected simplification: literal colimits in the browser store

The runtime does not need to construct quotient sets or carry universal arrows as ordinary application objects. It can store a normalized typed graph with explicit junctions and have a mathematical semantics related to a colimit.

This representation supports:

- stable inspectable IDs;
- unlinking;
- permissions and labels on junctions;
- persistence;
- efficient incidence indexes;
- user-facing explanations.

The categorical construction guides correctness and composition; it need not dictate memory layout.

## 36.21 Rejected simplification: compile the React tree into the proof model

React reconciliation, portals, suspense, virtualization, and local component state are implementation details. The semantic occurrence graph should be explicitly registered from React, not reverse-engineered from the fiber tree.

Only semantically relevant regions enter the model.

## 36.22 Rejected simplification: one global subject

A workspace can share analysis while keeping independent:

- selection;
- filters;
- time window;
- comparison side;
- theme;
- chart zoom;
- table sort;
- parameter values.

Named typed ports and junctions express these choices. A single workspace `currentDocument` atom recreates hidden coupling and prevents more advanced compositions.

## 36.23 Rejected simplification: structural equality for application objects

Deep equality can collapse distinct duplicate rows, be expensive, and change when irrelevant metadata changes. Nominal identity with explicit keys is required. Structural equivalence can be a separate derived relation with provenance.

## 36.24 Rejected simplification: make every state a CRDT

Some values have clean semilattice or sequence semantics. Others have exclusive ownership, invariants, external effects, or destructive migrations.

Forcing every command into a CRDT can produce surprising conflict resolution and large metadata. Choose replicated types per domain and retain coordinated commands where correctness requires them.

## 36.25 Rejected simplification: TypeScript proves the laws

TypeScript can ensure that an implementation has methods named `read` and `propose`. It cannot establish lens laws, purity, totality, monotonicity, termination, or temporal liveness.

Use types to eliminate classes of representation errors. Use proof, model checking, property tests, runtime checks, and audits for semantic laws.

## 36.26 Open research questions for this system

Several questions should remain explicit experiments:

1. Which fragment of the goal language gives enough product expressiveness while retaining decidable, explainable, incrementally maintainable evaluation?
2. Should the world schema use a conventional relational model, attributed C-sets, or a generated hybrid representation?
3. Which category of instances and morphisms makes the saturation reflector theorem fit nominal IDs, attributes, and plugin extension most naturally?
4. Can command applicability and authorization share one logic without leaking sensitive negative information through explanations?
5. Which provenance representation gives useful “why?” answers without unacceptable memory growth?
6. How should non-monotone ranking and default-selection policies compose with monotone eligibility?
7. Can GraphicDocument migration contracts be inferred from compiler dependencies and enriched with user-declared semantic roles?
8. Which graph rewrites admit useful automated critical-pair analysis in the actual workspace model?
9. How much of the incremental engine should be custom versus delegated to an embedded Datalog or differential dataflow implementation?
10. Which compatibility observations are sufficient to establish behavioral refinement from current PBUI to OPK?
11. How should portable templates reference plugin-defined vocabulary so that unknown plugins are preserved but not executed?
12. Can a restricted foreign-function interface produce proof certificates or dependency witnesses that reduce the trusted boundary?

These are tractable design and research tasks. They should be evaluated through prototypes and counterexamples rather than settled by terminology.

## 36.27 Limits of the recommendation

OPK is a proposed synthesis, not a demonstrated production framework. The strongest categorical theorem depends on definitions and assumptions that still need formalization. The incremental strategy needs benchmarking against actual Datalab workloads. The foreign boundary remains substantial. The migration requires enough product discipline to distinguish subjects, ports, commands, lenses, and effects consistently.

Those limits do not invalidate the direction. They determine where proof claims must stop and engineering evidence must begin.

# 37. Glossary

This glossary fixes the meaning of recurring terms within this study. Several words have broader meanings in category theory, logic, programming languages, databases, or UI engineering. The definitions below identify the intended use in OPK.

## 37.1 Semantic and logical terms

**Active universe**  
The finite set of entity IDs, values, component instances, occurrences, ports, actors, and other atoms currently admitted to one runtime snapshot. Restricting derivation to an active universe is one reason ordinary finite saturation is sufficient for the browser even when the metatheory permits infinite structures.

**Base fact**  
A fact asserted directly by an authoritative subsystem rather than inferred by the rule theory. Examples include `entity(field42, Field)`, `denotes(mark9, field42)`, `member(user7, workspace3)`, and `connected(portA, junction5)`.

**Base instance**  
The collection of all base facts for one world snapshot, organized according to a schema. In the proposed architecture, commands change the base instance; rules recompute or incrementally maintain derived facts.

**Batch semantics**  
The reference meaning obtained by evaluating a query or rule theory from a complete input snapshot. An incremental implementation is correct when its maintained result is observationally equivalent to this batch result after the same updates.

**Closure operator**  
An operation \(C\) on an ordered collection satisfying three laws: extensivity \(X \le C(X)\), monotonicity \(X \le Y \Rightarrow C(X) \le C(Y)\), and idempotence \(C(C(X)) = C(X)\). Semantic saturation under positive rules is intended to form such an operator.

**Conservative extension**  
An extension of a vocabulary or rule theory that does not change the truths expressible in the old vocabulary for old inputs, except where the extension explicitly declares an override. This is a desirable plugin property, not something TypeScript guarantees automatically.

**Derived fact**  
A fact supported by one or more rule derivations. Examples include `eligible(occurrence, goal)`, `available(action, occurrence)`, `compatible(portA, portB)`, and `affectedBy(view, junction)`.

**Derivation**  
A structured witness showing how a conclusion follows from base facts, rules, conversions, and assumptions. A derivation may be compacted, hashed, or retained only on demand, but it is conceptually different from a Boolean result.

**Denotation**  
The semantic entity or value to which a presentation occurrence refers. A DOM element, chart mark, table cell, or token is a representation; its denotation is the application-level object exposed to the interaction system.

**Evidence**  
Machine-readable support for a judgment. Evidence can include a rule proof tree, conversion path, permission decision, field-contract match, capability token, or foreign-function assumption. It should be sufficient to explain or audit a result at the level promised by the API.

**Fixed point**  
A value \(X\) satisfying \(F(X)=X\). A least fixed point is the smallest such value in the relevant order. Positive recursive rules are normally interpreted by their least fixed point so that only finitely or inductively justified conclusions are admitted.

**Goal**  
A declarative request for evidence. An input context is represented as a goal such as “find an occurrence denoting a field owned by this document and satisfying this policy,” rather than solely as an imperative callback.

**Judgment**  
A proposition evaluated within a world and context, usually with evidence. Examples are “occurrence \(o\) satisfies input goal \(g\)” and “actor \(a\) may execute command \(c\) against entity \(x\).”

**Monotone**  
Preserving an information order: adding input information cannot retract an already produced result. Monotonicity is relative to a stated order; it is not synonymous with purity, determinism, or mathematical elegance.

**Positive rule**  
A rule whose recursive dependencies do not require negating the relation being defined. Positive relational rules induce monotone immediate-consequence operators and support least-fixed-point semantics.

**Provenance**  
Information recording where a result came from and how alternatives combine. Boolean provenance records existence; lineage records contributing facts; semiring provenance can distinguish alternative and joint causes.

**Rule theory**  
A serializable collection of rules defining derived relations. It is separated from base facts so that the same theory can be interpreted in batch, incremental, explanatory, test, and verification modes.

**Saturation**  
Applying a rule theory until no new derived facts are produced. The saturated world includes the base instance and its semantic closure.

**Stratified negation**  
A disciplined use of negation in which negative dependencies flow only from a later stratum to an already completed earlier stratum. It can express many closed-world policies while avoiding unstratified recursive paradoxes, but it weakens simple global monotonicity.

**Subject**  
The semantic value carried by a junction and observed through connected ports. In Datalab, a subject may be a `GraphicDocument`, a selection set, a time window, a parameter environment, or another explicitly typed value.

**Transfinite induction**  
A proof principle over ordinals with successor and limit cases. In this architecture it is useful for metatheoretic closure and free-construction arguments. It is not a proposal to represent arbitrary ordinals in React state.

**Transfinite iteration**  
An ordinal-indexed construction with joins at limit ordinals. It can establish convergence for monotone constructions beyond finite or \(\omega\)-stage iteration. Runtime engines should use finite worklists, incremental maintenance, or domain-specific solvers whenever the active model is finite.

**Widening and narrowing**  
Abstract-interpretation techniques for accelerating convergence in infinite-height domains. Widening deliberately over-approximates to force convergence; narrowing may then regain precision. These operations require domain-specific soundness arguments and should not be inserted into ordinary UI rule evaluation by default.

## 37.2 Categorical and compositional terms

**Algebra**  
For an endofunctor \(F\), an \(F\)-algebra is an object \(A\) with a structure map \(F(A)\to A\). In software terms it can interpret one layer of syntax or operations into a carrier.

**Initial algebra**  
An algebra from which there is a unique algebra homomorphism to every other algebra of the same signature. Initiality supports structural recursion and induction over freely generated syntax.

**Coalgebra**  
For an endofunctor \(F\), an \(F\)-coalgebra is an object \(X\) with a behavior map \(X\to F(X)\). Coalgebras model state-based systems by describing observable output and possible next behavior.

**Colimit**  
A universal way to assemble a diagram by identifying the parts specified by its arrows. Coproducts and pushouts are common colimits. In OPK, colimits provide a semantics for composing open components and identifying compatible boundaries; the runtime may store an equivalent normalized graph rather than an explicit quotient object.

**Component**  
An open application module with internal state, declared ports, required capabilities, projections, and command handlers. A component is not identical to a React component, although a React subtree may render one.

**Cospan**  
A diagram \(A\to X\leftarrow B\), often read as an open system \(X\) with input and output interfaces \(A\) and \(B\). Structured cospans enrich this pattern so the interfaces and apex inhabit related categories with useful composition.

**Functor**  
A mapping between categories that preserves identities and composition. In this study, interpreters and schema migrations are candidates for functorial treatment only when their source and target categories and preservation laws are specified.

**Junction**  
A first-class node connecting compatible ports and carrying a current subject. It replaces a hidden equivalence encoded only by repeated `documentBindingId` strings. A junction can also carry policy, provenance, labels, and synchronization state.

**Open system**  
A system whose boundary is explicit and supports composition with compatible systems. A chart application is open when its analysis input, selection input, and other dependencies are represented as ports rather than ambient global state.

**Port**  
A named, typed boundary endpoint declared by a component. A port has a protocol, direction or variance policy, cardinality, and possibly a lens or command interface. It is more specific than “this application is document-bound.”

**Presheaf or C-set instance**  
A functor-valued representation of structured data over a small category or schema. Attributed C-sets extend graph-like structure with typed data attributes. They are one candidate representation for OPK’s world graph, not a mandatory user-facing abstraction.

**Protocol**  
The contract governing values and operations at a port: its subject type, readable observations, admissible updates, effects, capabilities, version behavior, and compatibility rules.

**Pushout**  
A colimit that glues two objects along a shared interface. Pushouts are relevant to link and component assembly semantics. A later unlink operation is generally not an inverse pushout; it is a new graph rewrite requiring retained identity and incidence data.

**Reflection**  
An adjunction in which a full subcategory is included by a right adjoint and the left adjoint maps arbitrary objects to their closest objects in the subcategory. If semantic closure is a reflector into saturated models, it preserves colimits.

**Universal property**  
A characterization of an object by unique factorization rather than by a particular data representation. Claims such as “linking is a pushout” are meaningful only after the category, diagram, and relevant universal property are defined.

**Wiring diagram**  
A compositional syntax describing how typed ports are interconnected. A wiring diagram can be interpreted into several semantics: relational constraints, state machines, dataflow plans, or rendered documentation.

## 37.3 Interaction and command terms

**Action**  
A user-visible affordance backed by a command schema and applicability evidence. The label, icon, shortcut, and menu placement are presentation metadata; the command’s semantics remain separate.

**Algebraic effect**  
An abstract operation requested by an interaction program, such as `Choose`, `Confirm`, `Notify`, `ReadClock`, `QueryDatabase`, or `CommitCommand`. A handler supplies the concrete interpretation for React, tests, remote sessions, or replay.

**Capability**  
An explicit authority or resource required to perform an operation. Capabilities may represent permission to mutate a workspace, access a data source, run a query, invoke a foreign function, or emit a remote effect.

**Command**  
A serializable intent with typed parameters, preconditions, authorization requirements, a deterministic state-transition meaning where possible, and an explicit effect plan. Datalab’s serializable verbs are a strong starting point for this layer.

**Effect handler**  
An interpreter for algebraic operations. Different handlers can render a prompt, drive a keyboard-only session, generate a test trace, run a command remotely, or reject unsupported capabilities.

**Foreign operation**  
Host-language computation outside the analyzable core. Its declaration must state dependencies, capabilities, determinism, purity or effect class, cache policy, execution location, and any proof assumptions.

**Input context**  
A delimited interaction seeking evidence for a goal. It includes the goal, actor, scope, occurrence policy, cancellation behavior, version fingerprint, and continuation.

**Interaction program**  
A serializable or typed program built from effect operations. It can express multi-step flows such as choose a target port, select a migration mapping, confirm destructive changes, commit atomically, and display the result.

**Occurrence commitment**  
The policy that committing a visible choice re-evaluates the actual selected occurrence and its current denotation, rather than returning a cached payload from a semantically equal occurrence.

**Presentation occurrence**  
A semantically registered region or virtual item that denotes an entity under one interpretation. It carries occurrence identity, geometry or focus order, ownership, and renderer-specific metadata.

**Selector**  
In the current PBUI, a prepared predicate over presentation references. In OPK, most selectors become declarative goals; opaque selectors remain foreign predicates with explicit assumptions and dependencies.

**Settlement**  
The terminal outcome of an input context or interaction program: committed, cancelled, failed, timed out, superseded, or denied. Protocols should ensure at-most-once terminal settlement.

## 37.4 State, rewriting, and bidirectionality terms

**Command-producing lens**  
A view abstraction whose proposed update does not mutate the source directly. It emits a validated command or patch request, allowing authorization, invariants, undo, and collaboration policies to participate in the update.

**Delta**  
A change representation describing additions, removals, replacements, or weighted differences. Incremental maintenance propagates deltas instead of recomputing every relation and projection from scratch.

**Double-pushout rewrite**  
A categorical graph-rewriting construction that removes a matched subobject and adds a replacement under stated gluing conditions. It is a candidate formal semantics for structural commands such as link, unlink, fork, and delete.

**Graph rewrite**  
A typed transformation from one graph-shaped base instance to another under a pattern, preconditions, and postconditions. A reducer can be generated from, or checked against, this rewrite specification.

**Lens**  
A bidirectional abstraction with a read direction and an update direction, normally governed by laws such as Get–Put and Put–Get. Partial, validated, normalizing, and command-producing variants require correspondingly adjusted laws.

**Migration**  
A transformation that preserves an analysis contract while changing the source, field mapping, or schema. It is not a simple lens update when successful execution requires preflight, compilation, mapping choices, and transactional replacement.

**Nominal identity**  
Identity based on an explicit domain and key rather than structural equality. Two occurrences may denote the same nominal entity while remaining distinct occurrences; two structurally identical rows may remain distinct entities.

**Rewrite invariant**  
A property preserved by every valid graph rewrite, such as port type compatibility, no dangling placement references, binding-group coherence, or unique ownership of a document revision.

**Transition system**  
A set of states with labeled next-state relations. Temporal safety and liveness properties are stated over paths through this system rather than over isolated reducer calls.

**Undo**  
A compensating or inverse command under a stated history model. Not every effect has a true inverse, so undo semantics may restore a prior base snapshot, emit a compensating operation, or be unavailable after an external effect commits.

## 37.5 Runtime and distribution terms

**Actor**  
The user, service, or delegated agent on whose authority a judgment or command is evaluated. Actor identity is an explicit input to authorization and explanation, not ambient React context alone.

**CRDT**  
A replicated data type designed so independently applied concurrent updates converge under its stated delivery assumptions. A CRDT solves a particular replicated-state problem; it does not automatically preserve every application invariant.

**Incrementalization**  
Transforming a batch computation into one that updates its result from an input delta and prior result. Correctness is normally stated by equivalence with re-running the batch semantics.

**Projection**  
A derived, usually read-only view consumed by a renderer, command palette, accessibility tree, or inspector. Projections should declare dependencies and should not become the authoritative source of semantic state.

**Semilattice**  
A partially ordered set in which pairs have a join or meet. Join-semilattices support monotone accumulation and appear in fixed-point evaluation, deterministic parallelism, and some state-based CRDTs.

**Snapshot fingerprint**  
A compact identifier for the semantic versions on which a prepared decision depends. Before commitment, the system verifies the fingerprint or re-evaluates the goal to prevent stale acceptance.

**Trusted computing base**  
The code and assumptions that must be correct for a claimed property to hold. In OPK it includes the core interpreter, schema compiler, rule engine, command executor, identity allocator, selected foreign declarations, and any extraction or model-checking correspondence.


# 38. References

The references below are not presented as a claim that one paper supplies the full OPK design. They identify the primary mathematical and systems traditions from which the architecture families, proof principles, and implementation strategies in this study are drawn.

## 38.1 Fixed points, induction, and transfinite construction

1. Alfred Tarski. “A Lattice-Theoretical Fixpoint Theorem and Its Applications.” *Pacific Journal of Mathematics* 5(2), 1955, pp. 285–309. [DOI: 10.2140/pjm.1955.5.285](https://doi.org/10.2140/pjm.1955.5.285).

2. G. M. Kelly. “A Unified Treatment of Transfinite Constructions for Free Algebras, Free Monoids, Colimits, Associated Sheaves, and So On.” *Bulletin of the Australian Mathematical Society* 22, 1980, pp. 1–83. [DOI: 10.1017/S0004972700006353](https://doi.org/10.1017/S0004972700006353).

3. Jiří Adámek, Stefan Milius, and Lawrence S. Moss. “Initial Algebras Without Iteration.” In *9th Conference on Algebra and Coalgebra in Computer Science (CALCO 2021)*, LIPIcs 211, Article 5. [DOI: 10.4230/LIPIcs.CALCO.2021.5](https://doi.org/10.4230/LIPIcs.CALCO.2021.5). See also [arXiv:2104.09837](https://arxiv.org/abs/2104.09837).

4. Patrick Cousot and Radhia Cousot. “Comparing the Galois Connection and Widening/Narrowing Approaches to Abstract Interpretation.” In *Programming Language Implementation and Logic Programming*, LNCS 631, 1992. [DOI: 10.1007/3-540-55844-6_142](https://doi.org/10.1007/3-540-55844-6_142).

## 38.2 Algebraic effects, monotone languages, and derivation

5. Gordon D. Plotkin and Matija Pretnar. “A Logic for Algebraic Effects.” In *23rd Annual IEEE Symposium on Logic in Computer Science*, 2008, pp. 118–129. [DOI: 10.1109/LICS.2008.45](https://doi.org/10.1109/LICS.2008.45).

6. Gordon D. Plotkin and Matija Pretnar. “Handlers of Algebraic Effects.” In *Programming Languages and Systems, ESOP 2009*, LNCS 5502, pp. 80–94. [DOI: 10.1007/978-3-642-00590-9_7](https://doi.org/10.1007/978-3-642-00590-9_7).

7. Matija Pretnar. “An Introduction to Algebraic Effects and Handlers.” *Electronic Notes in Theoretical Computer Science* 319, 2015, pp. 19–35. [DOI: 10.1016/j.entcs.2015.12.003](https://doi.org/10.1016/j.entcs.2015.12.003).

8. Michael Arntzenius and Neel Krishnaswami. “Datafun: A Functional Datalog.” In *Proceedings of the 21st ACM SIGPLAN International Conference on Functional Programming*, 2016, pp. 214–227. [DOI: 10.1145/2951913.2951948](https://doi.org/10.1145/2951913.2951948).

9. Michael Arntzenius and Neel Krishnaswami. “Seminaïve Evaluation for a Higher-Order Functional Language.” *Proceedings of the ACM on Programming Languages* 4, POPL, Article 22, 2020. [DOI: 10.1145/3371090](https://doi.org/10.1145/3371090).

10. Todd J. Green, Grigoris Karvounarakis, and Val Tannen. “Provenance Semirings.” In *Proceedings of the Twenty-Sixth ACM SIGMOD-SIGACT-SIGART Symposium on Principles of Database Systems*, 2007. [DOI: 10.1145/1265530.1265535](https://doi.org/10.1145/1265530.1265535).

## 38.3 Open systems, categorical data, and graph rewriting

11. John C. Baez and Kenny Courser. “Structured Cospans.” *Theory and Applications of Categories* 35, 2020, pp. 1771–1822. [arXiv:1911.04630](https://arxiv.org/abs/1911.04630).

12. David I. Spivak. “The Operad of Wiring Diagrams: Formalizing a Graphical Language for Databases, Recursion, and Plug-and-Play Circuits.” 2013. [arXiv:1305.0297](https://arxiv.org/abs/1305.0297).

13. Dmitry Vagner, David I. Spivak, and Eugene Lerman. “Algebras of Open Dynamical Systems on the Operad of Wiring Diagrams.” *Theory and Applications of Categories* 30, 2015, pp. 1793–1822. [arXiv:1408.1598](https://arxiv.org/abs/1408.1598).

14. David I. Spivak. “Functorial Data Migration.” *Information and Computation* 217, 2012, pp. 31–51. [DOI: 10.1016/j.ic.2012.05.001](https://doi.org/10.1016/j.ic.2012.05.001).

15. Evan Patterson, Owen Lynch, and James Fairbanks. “Categorical Data Structures for Technical Computing.” *Compositionality* 4(5), 2022. [DOI: 10.32408/compositionality-4-5](https://doi.org/10.32408/compositionality-4-5). See also [arXiv:2106.04703](https://arxiv.org/abs/2106.04703).

16. Stephen Lack and Paweł Sobociński. “Adhesive Categories.” In *Foundations of Software Science and Computation Structures, FoSSaCS 2004*, LNCS 2987, pp. 273–288. [DOI: 10.1007/978-3-540-24727-2_20](https://doi.org/10.1007/978-3-540-24727-2_20).

## 38.4 Bidirectionality, behavior, and verification

17. J. Nathan Foster, Michael B. Greenwald, Jonathan T. Moore, Benjamin C. Pierce, and Alan Schmitt. “Combinators for Bidirectional Tree Transformations: A Linguistic Approach to the View-Update Problem.” *ACM Transactions on Programming Languages and Systems* 29(3), 2007, Article 17. [DOI: 10.1145/1232420.1232424](https://doi.org/10.1145/1232420.1232424).

18. J. J. M. M. Rutten. “Universal Coalgebra: A Theory of Systems.” *Theoretical Computer Science* 249(1), 2000, pp. 3–80. [DOI: 10.1016/S0304-3975(00)00056-6](https://doi.org/10.1016/S0304-3975(00)00056-6).

19. Leslie Lamport. “The Temporal Logic of Actions.” *ACM Transactions on Programming Languages and Systems* 16(3), 1994, pp. 872–923. [DOI: 10.1145/177492.177726](https://doi.org/10.1145/177492.177726).

20. Daniel Jackson. “Alloy: A Lightweight Object Modelling Notation.” *ACM Transactions on Software Engineering and Methodology* 11(2), 2002, pp. 256–290. [DOI: 10.1145/505145.505149](https://doi.org/10.1145/505145.505149).

## 38.5 Incremental execution and distributed coordination

21. Yufei Cai, Paolo G. Giarrusso, Tillmann Rendel, and Klaus Ostermann. “A Theory of Changes for Higher-Order Languages: Incrementalizing λ-Calculi by Static Differentiation.” In *Proceedings of PLDI 2014*, pp. 145–155. [DOI: 10.1145/2594291.2594304](https://doi.org/10.1145/2594291.2594304).

22. Mihai Budiu, Tej Chajed, Frank McSherry, Leonid Ryzhyk, and Val Tannen. “DBSP: Automatic Incremental View Maintenance for Rich Query Languages.” *Proceedings of the VLDB Endowment* 16(7), 2023, pp. 1601–1614. [DOI: 10.14778/3587136.3587137](https://doi.org/10.14778/3587136.3587137).

23. Marc Shapiro, Nuno Preguiça, Carlos Baquero, and Marek Zawirski. “Conflict-Free Replicated Data Types.” In *Stabilization, Safety, and Security of Distributed Systems, SSS 2011*, LNCS 6976, pp. 386–400. [DOI: 10.1007/978-3-642-24550-3_29](https://doi.org/10.1007/978-3-642-24550-3_29).

24. Joseph M. Hellerstein and Peter Alvaro. “Keeping CALM: When Distributed Consistency Is Easy.” *Communications of the ACM* 63(9), 2020, pp. 72–81. [DOI: 10.1145/3369736](https://doi.org/10.1145/3369736). See also [arXiv:1901.01930](https://arxiv.org/abs/1901.01930).

## 38.6 Historical and project context

25. The LispWorks CLIM documentation, especially its chapters on presentations, input contexts, output recording, command tables, and translators, remains useful historical context for understanding the architecture that PBUI originally adapted. [CLIM User Guide](https://www.lispworks.com/documentation/lw81/clim/clim.htm).

26. `PRESENTATION-BASED-UI-CLIM-DESIGN-AND-IMPLEMENTATION.md`, produced earlier in this work, documents the enhanced PBUI selector, identity, action-rule, conversion, and shared-document-binding design.

27. `LINKED-ANALYSIS-WORKSPACES-PBUI-DATALAB-STUDY.md`, produced earlier in this work, develops Datalab subject bindings, named application ports, fork and template semantics, migration contracts, and product interaction flows.

28. The enhanced repository itself is the primary source for all code-specific observations in this study, especially:

   - `src/presentation/types.ts`
   - `src/presentation/selectors.ts`
   - `src/presentation/registry.ts`
   - `src/presentation/conversions.ts`
   - `src/createPbui.tsx`
   - `packages/datalab-ui/src/pbui/registry.ts`
   - `packages/datalab-ui/src/pbui/verbs.ts`
   - `packages/datalab-ui/src/appkit/registry.ts`
   - `packages/datalab-ui/src/store/layout.ts`
   - `packages/datalab-ui/src/store/bundles.ts`
   - `packages/datalab-ui/src/model/graphic.ts`
   - `packages/datalab-ui/src/model/graphicAuthoring.ts`
   - `packages/datalab-ui/src/analysis/`


# 39. Final recommendation

The recommended direction is not to replace PBUI with category-theory terminology. It is to replace the accidental semantic center of the system with a small set of structures whose laws can be stated independently and whose implementations can be compared against reference meanings.

## 39.1 Adopt OPK as a semantic kernel, not as a UI framework

React should remain responsible for rendering, local composition, focus integration, measurement, and ordinary component ergonomics. Redux or the existing store infrastructure can remain responsible for concrete state storage and reducer execution. DuckDB and the current analysis compiler can remain responsible for bulk analytical computation.

OPK should own a narrower but deeper layer:

1. **typed nominal entities and occurrences;**
2. **open components with named protocol ports;**
3. **junctions carrying shared subjects;**
4. **base facts and positive derived rules;**
5. **goals and evidence-producing judgments;**
6. **serializable commands and graph rewrites;**
7. **algebraic interaction operations;**
8. **projections and command-producing lenses;**
9. **dependency metadata for incremental interpretation;**
10. **an explicit foreign-function boundary.**

This is enough structure to explain presentations, linking, action availability, conversions, authorization, reusable templates, migration, and responsive recomputation without forcing every product concern into one abstraction.

## 39.2 Make the typed relational world the source of semantic truth

The most consequential decision is to represent common semantics as data rather than callbacks.

The base world should contain facts such as:

```text
entity(document_17, GraphicDocument)
entity(chart_view_2, ApplicationView)
entity(chart_analysis_port, AnalysisPort)
entity(binding_9, AnalysisJunction)

owns(chart_view_2, chart_analysis_port)
connected(chart_analysis_port, binding_9)
carries(binding_9, document_17)

denotes(mark_41, field_population)
occursIn(mark_41, chart_view_2)
actorMemberOf(alice, workspace_census)
```

The rule theory should derive facts such as:

```text
subjectOf(chart_view_2, document_17)
eligible(mark_41, chooseNumericFieldGoal)
available(linkAction, chart_analysis_port)
compatible(chart_analysis_port, table_analysis_port)
affectedBy(chart_view_2, binding_9)
```

This representation creates one inspectable dependency graph for behavior that is currently distributed among descriptor methods, React context, reducers, selectors, conversion search, and component-local assumptions.

## 39.3 Use fixed-point closure as the principal proof boundary

The core semantic equation should be:

\[
C_\Gamma(I)=\mu X.\; I\cup T_\Gamma(X).
\]

For the initial implementation, \(I\) is finite, the rule vocabulary is finite, and recursive rules are positive. The reference interpreter can therefore compute closure with a straightforward worklist. The production interpreter may use indexes, semi-naive evaluation, demand-driven materialization, and deltas.

The critical engineering theorem is not merely “the worklist terminates.” It is:

> For every accepted finite program and finite base instance, the incremental interpreter produces the same observable derived relations and evidence as the batch least-fixed-point semantics after the same committed command sequence.

This creates a stable target against which optimization can proceed.

Where the system later admits stratified negation, aggregation, weighted search, or abstract domains, each extension should identify its own semantics and proof obligations. It should not silently inherit claims made for the positive fragment.

## 39.4 Make closure a reflector only after the category is specified

The categorical target worth formalizing is:

\[
C_\Gamma \dashv J : \mathbf{Sat}_\Gamma \hookrightarrow \mathbf{Inst}_\Sigma.
\]

The work required to justify this statement is concrete:

- define the schema \(\Sigma\);
- define instances and instance morphisms;
- define the positive theory \(\Gamma\);
- show that closure is functorial;
- show extensivity, monotonicity, and idempotence;
- identify saturated instances;
- construct the universal arrow into the inclusion.

Once this is done, preservation of colimits follows from left-adjointness. For a diagram of open components, the semantic composition law becomes:

\[
\operatorname{colim}_{\mathbf{Sat}_\Gamma} D
\cong
C_\Gamma\!\left(
  \operatorname{colim}_{\mathbf{Inst}_\Sigma} JD
\right).
\]

That result would justify a modular implementation discipline:

1. assemble component instances and identify interfaces;
2. normalize the resulting graph;
3. close it under the semantic theory;
4. query the saturated result for presentations and commands.

The theorem should be proved for a deliberately small core before being generalized to every attribute and plugin feature. Nominal IDs, partial maps, authorization-sensitive facts, and foreign predicates can invalidate an overbroad formulation.

## 39.5 Use wiring diagrams for static composition and graph rewrites for change

Workspace templates should be represented as open typed networks:

```text
Census analysis template

  analysis input ──┬── dataset table
                   ├── pipeline editor
                   ├── encoding editor
                   └── bar chart
```

Instantiating a template fills an exposed port with a subject or connects it to another component. Linking two existing applications identifies compatible boundaries through a junction.

The runtime should not attempt to encode unlinking as a categorical inverse. It should execute typed graph-rewrite commands:

- `ConnectPorts`
- `DisconnectPort`
- `RebindJunction`
- `ForkJunction`
- `MirrorWorkspace`
- `ForkWorkspace`
- `InstantiateTemplate`
- `MigrateAnalysisOntoSource`

Each rewrite should declare its match, negative application conditions where needed, preserved interface, created and deleted elements, authorization requirements, postconditions, and undo policy. Small structural models can be explored in Alloy; asynchronous command behavior can be modeled in TLA+.

## 39.6 Use algebraic effects for interaction protocols

`accept(): Promise<T>` is a useful adapter, but it should not be the fundamental expression of a multi-step interaction.

An interaction should be able to request abstract operations:

```ts
const linkAnalysis = opk.program(function* () {
  const target = yield* choose({
    goal: goals.compatibleAnalysisPort(sourcePort),
    prompt: "Link analysis to…",
  });

  const preview = yield* evaluateCommand({
    command: commands.connectPorts(sourcePort, target),
  });

  if (preview.warnings.length > 0) {
    yield* confirm({ warnings: preview.warnings });
  }

  return yield* commit(preview.command);
});
```

The exact TypeScript syntax can differ. The semantic requirement is that choosing, prompting, confirming, previewing, committing, notifying, and cancelling are named operations with handlers.

This permits:

- a React pointer-and-keyboard handler;
- a command-palette handler;
- deterministic interaction tests;
- remote execution with capability filtering;
- accessibility-specific rendering;
- trace generation for model checking;
- replay and debugging.

## 39.7 Preserve Datalab’s declarative analysis object and sharpen its boundaries

`GraphicDocument` should remain the subject that jointly determines a chart, table, pipeline, and encoding view. It is already a useful declarative intermediate representation.

Three operations must remain distinct:

1. **Rebind a view or link group to another complete `GraphicDocument`.**  
   Every connected analysis view observes the new document.

2. **Fork or duplicate a `GraphicDocument`.**  
   A new document identity is created, with explicit sharing or copying of sources and derived artifacts.

3. **Migrate an analysis onto another source while preserving intent.**  
   The system extracts field contracts, proposes mappings, recompiles, reports incompatibilities, and commits a new document revision transactionally.

The current `setDocSource` behavior resets transformations, views, encodings, and parameters. That operation should be named as destructive replacement. A preserving migration must be a separate command with a different type and interaction protocol.

## 39.8 Normalize document bindings into junctions

`documentBindingId` has proven the value of shared subject identity, but the equivalence class is implicit. Replace it incrementally with a first-class entity:

```ts
interface Junction<S, P extends Protocol<S>> {
  id: JunctionId;
  protocol: P;
  subject: S;
  revision: bigint;
  policy: JunctionPolicy;
}

interface Port<P extends Protocol<unknown>> {
  id: PortId;
  owner: ComponentId;
  protocol: P;
  role: string;
}

interface Connection {
  port: PortId;
  junction: JunctionId;
}
```

The first concrete protocol should be `AnalysisSubject<GraphicDocumentId>`. Later protocols can cover selection, time range, parameters, comparison subjects, or filters without forcing them into one global binding.

The chain icon should itself be a presentation occurrence denoting the analysis port. Its actions should be ordinary command-applicability results:

- link to compatible port;
- inspect binding;
- change subject;
- unlink this port;
- fork this binding;
- save group as template.

This connects the product interaction directly to the semantic model rather than adding another special dialog subsystem.

## 39.9 Retain arbitrary JavaScript, but make it visibly foreign

A practical React system cannot eliminate host-language functions. Renderers, database drivers, formatting, specialized geometry, schema inference, and many product policies will remain JavaScript or WebAssembly.

The API should distinguish three modes:

1. **Analyzable core** — serializable expressions with complete reference semantics.
2. **Assumption-tracked foreign operation** — a declared callback with explicit dependencies, effects, capabilities, cache scope, and claimed properties.
3. **Local escape hatch** — non-portable code permitted only in explicitly non-verifiable and non-remote contexts.

A foreign declaration might be shaped as follows:

```ts
foreignPredicate({
  id: "datalab.field.hasSemanticRole",
  input: tuple(entity("Field"), string()),
  dependencies: [relation("fieldProfile"), relation("fieldMetadata")],
  execution: "worker",
  determinism: "declared",
  monotonicity: "unknown",
  portability: "local-plugin",
  evaluate: (field, role, services) => {
    // Opaque host-language implementation.
  },
});
```

The result may still be useful. Its evidence must state that it depends on a foreign assumption. It cannot silently participate in the strongest closure, portability, or proof claims.

## 39.10 Build one vertical slice before generalizing the metamodel

The first end-to-end slice should implement the census linked workspace using only a small vocabulary:

- entity sorts for `GraphicDocument`, `ApplicationView`, `Placement`, `AnalysisPort`, `AnalysisJunction`, `Occurrence`, and `Actor`;
- relations for ownership, connection, carried subject, denotation, visibility, and membership;
- rules for `subjectOf`, `compatiblePort`, `eligible`, `availableAction`, and `affectedView`;
- commands for `ConnectPorts`, `DisconnectPort`, and `RebindJunction`;
- interaction effects for `Choose`, `Preview`, `Confirm`, `Commit`, and `Notify`;
- one React occurrence adapter;
- one batch reference interpreter;
- one incremental interpreter checked against it;
- one Alloy structural model;
- one TLA+ model for stale selection and atomic rebind;
- portable bundle round-trip tests preserving junction equivalence.

The user-visible result should be exactly the product behavior motivating the work:

- chart, table, pipeline, and encoding views visibly share one active analysis;
- either view can rebind the group;
- the link indicator exposes ordinary presentation-based actions;
- unlinking one view preserves its current subject;
- forking a workspace creates fresh identities while preserving internal linkage;
- instantiating a template binds one exposed analysis port to a selected document;
- stale choices cannot commit against a materially changed world.

This slice is sufficiently small to specify rigorously and sufficiently valuable to test the architecture against real Datalab behavior.

## 39.11 Preserve the current system as a behavioral oracle during migration

The redesign should be introduced by refinement rather than by a wholesale rewrite.

For each migrated feature:

1. capture the current behavior with golden interaction traces and state snapshots;
2. express the corresponding OPK base facts, rules, command, and projection;
3. run the old and new interpreters in shadow mode where possible;
4. compare available actions, accepted occurrences, command outputs, and final layout state;
5. document intentional semantic differences;
6. switch authority only after the correspondence is understood.

This makes “modern mathematical architecture” accountable to actual product behavior. It also gives a path to discover where the old behavior was accidental or internally inconsistent.

## 39.12 The concise architectural decision

The clean-slate formulation is:

> A presentation-based system is a typed open relational world whose semantic judgments are obtained by fixed-point closure, whose components compose through explicit boundaries, whose user operations are proof-producing commands and algebraic effects, whose structural changes are graph rewrites, whose editable projections obey bidirectional laws, and whose runtime incrementally interprets the same batch semantics.

For PBUI and Datalab, the practical decision is therefore:

- **keep** React, serializable verbs, semantic identity, `GraphicDocument`, application/placement separation, and graph-aware portable bundles;
- **promote** occurrences, actors, ports, junctions, commands, evidence, and revisions to explicit entities;
- **replace** most semantic lambdas with a typed goal-and-rule language;
- **compile** selectors, action availability, subtype membership, conversions, compatibility, ownership, and affected-view queries from one saturated world;
- **model** link, unlink, rebind, fork, duplicate, and migration as distinct typed commands;
- **interpret** multi-step interaction through algebraic effects;
- **verify** the finite reference semantics, rewrite invariants, and temporal protocols with the tool appropriate to each layer;
- **incrementalize** only after the batch meaning is executable and tested;
- **quarantine** opaque JavaScript behind explicit assumptions rather than pretending it is proved;
- **use** transfinite and categorical constructions in the metatheory where they establish existence, modularity, and induction principles, not as ornamental names for ordinary loops and object merging.

This architecture is farther from Common Lisp CLIM in decomposition while remaining faithful to its deepest insight: visible output should retain enough semantic structure to participate directly in the application’s command language. The difference is that the semantic structure is no longer owned by presentation types. It is distributed across a small, explicit, compositional kernel whose parts admit different and more appropriate proof principles.
