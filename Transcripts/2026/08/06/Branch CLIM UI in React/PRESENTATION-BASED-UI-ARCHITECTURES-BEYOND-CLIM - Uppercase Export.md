# Architectures for a Provable Presentation-Based User Interface

## Beyond CLIM: relational semantics, algebraic interfaces, open systems, fixed points, and bidirectional links

> **Status:** architecture study and design proposal  
> **Relationship to the first document:** companion volume. The first document explains presentation-based interaction through CLIM and develops an incremental React implementation. This document deliberately steps outside that decomposition and asks what the system would look like if designed today around proof, composition, incremental computation, concurrency, and explicit semantics.  
> **Audience:** engineers comfortable with TypeScript and React, and readers willing to learn the relevant logic, order theory, programming-language semantics, and category theory as they become useful.

---

## Abstract

A presentation-based UI should not merely attach callbacks to rendered objects. It should make explicit a semantic relationship among domain subjects, rendered occurrences, interaction contexts, admissible selections, commands, effects, and synchronized views. Once these relationships are explicit, several useful questions become mathematical rather than anecdotal:

- Is every selectable occurrence a sound witness for the requested semantic object?
- Do two visual forms that claim to denote the same object agree on identity?
- Can an action ever be offered without the authority or precondition required to execute it?
- Does linking two view ports preserve a stated consistency relation?
- Does recursive derivation converge, and is its result independent of evaluation order?
- Is incremental recomputation observationally equivalent to recomputing from scratch?
- Can independently developed components be composed without inventing ad hoc glue code?
- Under concurrency, do replicas converge, and which invariants require coordination?

The main conclusion is that no single abstraction—neither “presentation type,” “category,” “signal,” “lens,” nor “fixed point”—answers all of these questions. A stronger architecture separates concerns into layers whose mathematics match their obligations:

1. **A typed relational semantic kernel** represents subjects, occurrences, capabilities, links, and derived affordances as facts and rules.
2. **An inspectable query language** replaces most arbitrary selection lambdas and admits soundness proofs, dependency extraction, provenance, optimization, and incremental maintenance.
3. **A monotone or stratified fixed-point layer** gives recursive rules a least-fixed-point semantics. Transfinite iteration is useful for metatheory; practical programs should normally be restricted to fragments that converge finitely or by stage \(\omega\).
4. **An algebraic interaction language** represents choosing, performing, opening, cancelling, reading time, and other effects as data interpreted by handlers.
5. **Open typed components with ports** compose by explicit wiring. Pushouts and structured cospans explain composition of interfaces; quotients or coequalizers explain identification of ports.
6. **Bidirectional transformations** describe synchronization when linked views do not literally share one cell. Lens laws or consistency-restoration laws become component obligations.
7. **Coalgebraic machines or statecharts** describe temporal behavior such as idle, choosing, menu-open, dragging, and cancelled states. Coinduction and temporal model checking address behavior rather than static data.
8. **Incremental and differential evaluation** compiles declarative rules into efficient updates while preserving a from-scratch correctness theorem.
9. **Semilattice and CRDT techniques** are used only where distributed or parallel convergence is required; they are not forced onto ordinary local UI state.
10. **React is an adapter and renderer**, not the source of semantic truth. It registers committed visual occurrences and translates browser events into semantic operations.

The proposed API is therefore “deep” at its semantic boundary: selectors, rules, effects, links, and component contracts are reified syntax with interpreters. Ordinary JavaScript remains available through explicitly marked foreign extensions, but those extensions declare dependencies and proof assumptions and are excluded from claims the kernel cannot justify.

---

# Part I — Reframing the problem

## 1. The current API and the opportunity to redesign it

The current generic PBUI layer is intentionally small. Its central reference is a discriminated union:

```ts
export type PresentationReference<Values> = {
  [K in keyof Values]: {
    type: K;
    value: Values[K];
  };
}[keyof Values];
```

A descriptor supplies labels, descriptions, actions, and tone. An input request names acceptable presentation types and may contain an arbitrary predicate:

```ts
export interface AcceptRequest<Values> {
  types: keyof Values | readonly (keyof Values)[];
  prompt: string;
  filter?: (reference: PresentationReference<Values>) => boolean;
}
```

Conversions are arbitrary JavaScript functions from one reference to another. React occurrences ask the provider whether they are acceptable and, when activated, resolve a pending promise.

This is a useful prototype because it exposes the essential interaction: rendered output can answer a later request for an object. It also reveals the limits of a callback-first design:

- a `filter` is opaque to the system;
- its dependencies are unknown;
- its monotonicity is unknown;
- its cost is unknown;
- it cannot be serialized, explained, optimized, differentiated, or translated into a proof obligation;
- conversions have no declarative source and target theory beyond what the implementation happens to inspect;
- identity is entangled with the chosen presentation value;
- actions are generated at the edge rather than derived from an authorization and capability model;
- link behavior is a state-management convention rather than part of component semantics;
- temporal interaction lives in provider implementation details;
- React mounting and semantic existence are easy to conflate.

These are not defects in a small library. They are signals that a second-generation architecture needs a more explicit semantic center.

## 2. The first separation: subject, occurrence, form, and evidence

The most important redesign is to stop using one “presentation reference” to mean four different things.

### 2.1 Subject

A **subject** is the semantic thing the application reasons about. It can be an entity with stable identity, such as a document, or a value without independent identity, such as the number 12.

```ts
type Ref<S extends Sort> = {
  readonly sort: S;
  readonly id: IdOf<S>;
};
```

A project card and a project-ID token can both denote the same `Ref<Project>`. The card need not contain the complete project object, and the token need not be converted into a card-shaped value.

### 2.2 Occurrence

An **occurrence** is one addressable rendering of a subject. It has a lifetime and a location in a view or surface.

```ts
type OccurrenceId = Branded<string, "OccurrenceId">;
```

Two occurrences can denote one subject. A virtualized object may exist semantically while having no mounted occurrence. A global command palette may select an unmounted subject; direct manipulation can require a mounted occurrence.

### 2.3 Form

A **form** describes how an occurrence presents its subject: project card, ID token, table row, pipeline node, chart mark, compact link, or accessible textual alternative.

```ts
type FormId = Branded<string, "FormId">;
```

Form is not semantic object type. It is closer to a view, renderer, or affordance profile.

### 2.4 Evidence

A selection should carry **evidence** explaining why the occurrence satisfies the request. The evidence may be a derivation in a rule system, a direct sort witness, a capability token, or a foreign assumption.

```ts
interface Candidate<S extends Sort> {
  readonly subject: Ref<S>;
  readonly occurrence?: OccurrenceId;
  readonly derivation: DerivationId;
  readonly provenance: Provenance;
}
```

This distinction eliminates several accidental complexities. “Converting a project-ID presentation to a project presentation” is often unnecessary: both occurrences denote a project subject. A true semantic conversion remains possible, but it is represented as a relation or proof-producing morphism between semantic sorts rather than as a blind callback between display payloads.

## 3. A minimal semantic model

Let a PBUI state contain the following sets:

- \(E\): semantic subjects;
- \(O\): rendered occurrences;
- \(V\): logical views;
- \(P\): component ports;
- \(C\): interaction contexts;
- \(A\): actions or operations;
- \(K\): capabilities or authority tokens.

The kernel maintains typed relations such as:

\[
\begin{aligned}
\operatorname{Denotes} &\subseteq O \times E \\
\operatorname{Mounted} &\subseteq O \\
\operatorname{InView} &\subseteq O \times V \\
\operatorname{RenderedAs} &\subseteq O \times \text{Form} \\
\operatorname{HasSort} &\subseteq E \times \text{Sort} \\
\operatorname{HasCapability} &\subseteq C \times E \times K \\
\operatorname{Connected} &\subseteq P \times P \\
\operatorname{Exposes} &\subseteq V \times P \\
\operatorname{Enabled} &\subseteq C \times O \times A.
\end{aligned}
\]

Application relations add domain facts:

\[
\operatorname{OwnedBy}(p,u),\quad
\operatorname{Archived}(p),\quad
\operatorname{PrimaryDocument}(v,d),\quad
\operatorname{FieldOf}(f,d).
\]

A request for a mounted, active project owned by the current user is then a query over relations, not an arbitrary callback:

\[
\begin{aligned}
\operatorname{CandidateProject}(c,o,p) \iff{}&
\operatorname{CurrentContext}(c) \land
\operatorname{Mounted}(o) \land
\operatorname{Denotes}(o,p) \\
&\land \operatorname{HasSort}(p,\textsf{Project})
\land \operatorname{OwnedBy}(p,\operatorname{CurrentUser}(c)) \\
&\land \neg\operatorname{Archived}(p).
\end{aligned}
\]

The displayed highlight is a projection of this relation onto occurrences. Acceptance returns the subject together with a derivation witness.

## 4. What should be provable?

“Provable UI” is too vague unless the desired properties are named. The architecture should support several classes of theorem.

### 4.1 Static well-formedness

Examples:

- every relation is applied to arguments of the declared sorts;
- every component connection joins compatible ports;
- recursive rules are positive or stratified as required by the evaluator;
- every operation names an effect handler;
- every form renderer returns occurrences whose declared subject sort matches the renderer contract;
- action IDs are unique in a scope or have an explicit precedence rule.

These are mostly type checking and schema validation.

### 4.2 Selection soundness

For request \(Q\), state \(S\), and returned candidate \(x\):

\[
x \in \operatorname{eval}(Q,S)
\implies
\llbracket Q \rrbracket_S(x).
\]

In words: anything the runtime allows the user to select satisfies the denotational meaning of the request.

Completeness needs a qualification. For direct manipulation, only mounted and indexed occurrences can be clicked:

\[
\llbracket Q \rrbracket_S(x) \land \operatorname{MountedWitness}(x)
\implies
x \in \operatorname{eval}(Q,S).
\]

A global search interpreter can use a broader universe and establish a different completeness theorem.

### 4.3 Identity coherence

If two occurrences denote the same typed subject, operations that are extensional in subject identity should agree:

\[
\operatorname{Denotes}(o_1,e) \land \operatorname{Denotes}(o_2,e)
\implies
\operatorname{Actions}(c,o_1) \equiv_e \operatorname{Actions}(c,o_2),
\]

except where an action explicitly depends on occurrence, form, or view. This makes occurrence-sensitive behavior visible rather than accidental.

### 4.4 Authorization and invariant preservation

An offered operation should have a derivable precondition, and execution should preserve declared safety invariants:

\[
\operatorname{Enabled}(c,o,a)
\implies
\operatorname{Authorized}(c,\operatorname{subject}(o),a).
\]

For transition \(S \xrightarrow{a} S'\):

\[
I(S) \land \operatorname{Pre}_a(S)
\implies
I(S') \land \operatorname{Post}_a(S,S').
\]

UI visibility is not a security boundary, so the effect handler must recheck authority. The useful theorem is agreement between affordance derivation and authoritative execution, not “the menu hid the button.”

### 4.5 Link consistency

If a chart port and a pipeline port are linked by consistency relation \(R\), reachable states should satisfy:

\[
R(s_{chart},s_{pipeline}).
\]

For equal document-selection ports, \(R(x,y)\) is equality. For different representations, \(R\) may be a lens consistency relation.

### 4.6 Determinism, confluence, and convergence

Depending on the subsystem, one may want:

- deterministic evaluation of pure queries;
- confluence of rule saturation independent of work-list order;
- determinism of parallel monotone updates;
- eventual convergence of replicas;
- explicit conflict results rather than hidden last-writer behavior.

These are different properties. A deterministic local evaluator says nothing about network convergence; a convergent CRDT does not guarantee a business invariant.

### 4.7 Incremental correctness

Let \(Q\) be a query, \(S\) a state, and \(\Delta S\) a change. An incremental evaluator should satisfy a from-scratch consistency equation:

\[
\operatorname{apply}\bigl(\operatorname{eval}(Q,S),
  \Delta_Q(S,\Delta S)\bigr)
=
\operatorname{eval}\bigl(Q,\operatorname{apply}(S,\Delta S)\bigr).
\]

The theorem permits aggressive indexes, memoization, and differential maintenance without changing observable semantics.

### 4.8 Temporal safety and liveness

Examples:

- at most one pointer-owned object menu is open;
- cancellation always settles a pending choice exactly once;
- a disabled action is never executed through the same interaction path;
- after entering a choice mode, either a candidate is returned or cancellation remains possible;
- no stale occurrence can complete a newer request.

Safety properties say “nothing bad happens.” Liveness properties say “something good eventually happens,” usually under fairness assumptions. They require a transition-system semantics, not only a static query language.

## 5. Proof-friendly API design: deep syntax, not invisible callbacks

The defining architectural decision is whether an API operation is **shallow** or **deep**.

### 5.1 Shallow embedding

A shallow selector is ordinary JavaScript:

```ts
const activeOwned = (project: Project, env: Env) =>
  project.ownerId === env.currentUserId && !project.archived;
```

Advantages:

- familiar;
- unrestricted expressiveness;
- excellent local ergonomics;
- direct access to existing libraries.

The system sees only a function value. It cannot generally know which fields it reads, whether it terminates, whether it is pure, whether it is monotone, or why it returned true.

### 5.2 Deep embedding

A deep selector constructs an abstract syntax tree:

```ts
const activeOwned = selector(Project, ({ subject, param, rel, and, not }) =>
  and(
    rel(OwnedBy, subject, param(CurrentUser)),
    not(rel(Archived, subject)),
  ),
);
```

The callback here is only a builder convenience. It executes once to construct inspectable syntax; it is not run once per candidate as an opaque predicate. The resulting tree can be:

- type checked;
- normalized;
- interpreted;
- compiled to indexes;
- translated to SQL, Datalog, an SMT formula, or a model checker;
- differentiated;
- serialized;
- assigned provenance;
- explained in developer tools;
- used as the induction structure of a proof.

### 5.3 Three extension tiers

A practical system should not demand that all application logic fit the core language on day one. It should make the proof boundary explicit.

#### Tier 1 — kernel terms

Fully inspectable expressions built from certified constructors. All advertised theorems apply.

#### Tier 2 — certified extensions

An extension supplies an implementation plus a machine-checkable certificate or is implemented in a language whose compiler proves the relevant property.

```ts
externRelation({
  name: "isValidGlob",
  inputs: [Text, Text],
  purity: "pure",
  monotonicity: "discrete",
  implementation: verifiedWasmModule,
  certificate: certificateHash,
});
```

In ordinary TypeScript, a declaration such as `monotonicity: "monotone"` is an assumption, not a proof. The trusted computing base must say so.

#### Tier 3 — opaque foreign predicates

Legacy callbacks remain available but must declare dependencies and invalidation policy:

```ts
foreignPredicate({
  id: "legacy-active-owned-project",
  reads: [Project.ownerId, Project.archived, Context.currentUserId],
  cache: "per-revision",
  evaluate: (project, context) =>
    project.ownerId === context.currentUserId && !project.archived,
});
```

The evaluator can remain correct by invalidating pessimistically. Formal claims are conditional on the callback contract, and proof-producing tools mark the result as containing a foreign assumption.

### 5.4 The expressiveness ladder

Interaction programs have another useful hierarchy:

| Structure | What can depend on prior results? | Static analyzability |
|---|---:|---:|
| Applicative | no later request depends on earlier values | highest; requests can be listed and parallelized |
| Selective applicative | a bounded branch can depend on an earlier result | high; an upper bound on future effects is visible |
| Monad/free interaction tree | later requests may be generated from earlier values | lower; maximum flexibility |
| Opaque async function | arbitrary control and effects | minimal |

The API need not choose only one level. Simple forms can use an applicative plan; conditional workflows can use a selective plan; genuinely dependent interaction can use a free-monadic or effect-handler representation. The system should preserve the least expressive structure needed by a program because that structure is proof and optimization information.

---
# Part II — Architectural families

## 6. Architecture A: a typed relational and fixed-point kernel

### 6.1 Basic idea

The interface state is a typed database. Base facts are asserted by application stores, security services, and committed renderers. Derived facts are computed by rules. Selection and action availability are queries.

```text
base facts
  Subject(project-17)
  Sort(project-17, Project)
  Owner(project-17, person-1)
  Mounted(occ-93)
  Denotes(occ-93, project-17)
  InView(occ-93, chart-view-4)

rules
  ActiveProject(p) :- Project(p), not Archived(p)
  Selectable(c,o,p) :-
      Choosing(c, ActiveProjectSelector),
      Mounted(o),
      Denotes(o,p),
      ActiveProject(p),
      Owner(p, CurrentUser(c))
```

The programming model resembles typed Datalog, relational algebra, or a functional language whose type system tracks monotonicity. Datalog is attractive because its positive fragment has a simple least-fixed-point semantics and practical evaluation strategies. Datafun demonstrates a related direction: higher-order functional programming while tracking monotonicity in types so fixed-point computations remain controlled [Arntzenius and Krishnaswami 2016].

### 6.2 Denotational semantics

For a finite set of rules, let \(L\) be the lattice of possible fact sets ordered by inclusion. Let \(F_R : L \to L\) be the immediate-consequence operator induced by rules \(R\). For positive rules, \(F_R\) is monotone:

\[
X \subseteq Y \implies F_R(X) \subseteq F_R(Y).
\]

The meaning of the program is its least fixed point:

\[
\operatorname{lfp}(F_R).
\]

Tarski's fixed-point theorem states that the fixed points of a monotone endomap on a complete lattice form a complete lattice; in particular, least and greatest fixed points exist [Tarski 1955]. This gives a clean semantic target independent of a particular work-list algorithm.

### 6.3 Transfinite construction

A general monotone function need not reach its least fixed point after finitely many steps or even after the first \(\omega\) steps. Its closure sequence can be described by transfinite recursion:

\[
\begin{aligned}
x_0 &= \bot, \\
x_{\alpha+1} &= F(x_\alpha), \\
x_\lambda &= \bigvee_{\beta<\lambda} x_\beta
\quad\text{for a limit ordinal }\lambda.
\end{aligned}
\]

For a monotone endomap on a set-sized complete lattice, this increasing chain eventually stabilizes before the successor cardinal \( |L|^+ \): there cannot be more than \( |L| \) strict increases through distinct lattice elements. Cousot and Cousot use this general pattern when describing concrete and abstract semantic iterations, limit joins, convergence, and acceleration by widening [Cousot and Cousot 1992].

This matters in a UI architecture mainly as a proof principle, not as an implementation plan. A browser runtime should not attempt to enumerate arbitrary ordinals. Practical fragments should provide a stronger bound:

- finite domains or finite-height lattices imply finite stabilization;
- finitary Datalog over a finite active domain stabilizes after finitely many new facts;
- Scott-continuous or \(\omega\)-continuous functions reach the least fixed point at the supremum of the finite iterates;
- numeric or infinite abstract domains may use widening, accepting an over-approximation with a separate soundness theorem.

### 6.4 Transfinite induction for invariants

Suppose \(P(x)\) is an invariant of the closure sequence. A transfinite induction proof has three obligations:

1. **Base:** \(P(\bot)\).
2. **Successor:** \(P(x) \Rightarrow P(F(x))\).
3. **Limit:** if \(P(x_\beta)\) holds for every \(\beta<\lambda\), then \(P(\bigvee_{\beta<\lambda}x_\beta)\).

Then \(P(x_\alpha)\) holds at every stage and therefore at the stabilized fixed point.

For UI rules, a useful invariant might be:

> Every derived `Selectable(context, occurrence, subject)` fact has a mounted occurrence denoting that subject and a proof of every selector clause.

The successor case examines each rule that can derive `Selectable`. The limit case follows if the property is closed under union of fact sets. This proof shape is far more difficult when applicability is an arbitrary callback with hidden state.

### 6.5 Negation, deletion, and the monotonicity trap

Many UI conditions are nonmonotone:

```text
project is selectable if it is not archived
menu item is enabled if no conflicting edit exists
show placeholder if there are no results
```

If `Archived(p)` is later added, `ActiveProject(p)` must be removed. The query is not monotone under simple set inclusion. Several disciplined solutions exist:

1. **Stratified negation.** Compute lower strata first, then permit negation only over completed lower strata. This gives a well-defined perfect-model-style semantics for a broad practical fragment.
2. **Signed or multiset changes.** Maintain additions and retractions with an incremental algebra such as differential dataflow or DBSP. The semantic result can still be nonmonotone even though the change-processing machinery is algebraic.
3. **Event-sourced facts plus a current-state projection.** The log is append-only; “current project state” is a derived temporal relation.
4. **Three- or four-valued knowledge.** Distinguish false from not-yet-known where open-world data matters.
5. **Coordination.** In a distributed system, globally sound negation may require knowing that no remote fact can still arrive.

A type system can distinguish discrete variables from monotone variables, as Datafun does, so fixed-point variables cannot be used in anti-monotone positions accidentally.

### 6.6 Provenance and explanations

Relational answers can carry annotations from a semiring. In database provenance, addition represents alternative derivations and multiplication represents joint use of premises. Symbolic polynomials can therefore explain why an answer exists, and fixed-point extensions support recursive queries [Green, Karvounarakis, and Tannen 2007].

For PBUI, provenance can answer:

```text
Why is this tile selectable?
  because occurrence occ-93 is mounted
  and it denotes project-17
  and project-17 is owned by person-1
  and the current selector requests active projects owned by person-1
  and the archived relation contains no project-17 in the completed stratum
```

Provenance is useful beyond developer tooling:

- choose the most direct occurrence when several derive the same subject;
- show an accessible explanation for a disabled action;
- invalidate only outputs depending on a changed fact;
- audit authorization decisions;
- diagnose unexpected links or conversions.

### 6.7 Strengths

- excellent fit for selection, affordance derivation, permissions, and semantic identity;
- explicit recursion and fixed-point semantics;
- natural dependency and provenance model;
- amenable to query optimization and incremental view maintenance;
- straightforward translation to SQL, Datalog engines, SMT fragments, or proof assistants;
- supports order-independent saturation in the positive fragment.

### 6.8 Weaknesses

- temporal interaction is awkward if encoded only as facts;
- unrestricted negation, aggregation, JavaScript calls, and effects can destroy the clean theory;
- developers may find relational syntax less local than component callbacks;
- object construction and rich recursive data are less natural than in an algebraic language;
- a naïve engine can do far more work than a direct handler.

### 6.9 Assessment

This is the strongest candidate for the **semantic kernel**, but not the whole architecture. It should answer “what is true, selectable, enabled, connected, or derivable,” while other layers answer “what happens over time” and “how components are composed.”

## 7. Architecture B: algebraic syntax and multiple interpreters

### 7.1 Basic idea

Instead of representing selectors as functions, define them as an initial algebra—an inductive syntax generated by constructors:

```ts
type Formula<Env> =
  | { tag: "true" }
  | { tag: "relation"; relation: RelationId; args: readonly Term[] }
  | { tag: "equal"; left: Term; right: Term }
  | { tag: "and"; clauses: readonly Formula<Env>[] }
  | { tag: "or"; clauses: readonly Formula<Env>[] }
  | { tag: "not"; clause: Formula<Env> }
  | { tag: "exists"; sort: SortId; body: Formula<Env> }
  | { tag: "parameter"; name: keyof Env };
```

The constructors define a polynomial-like endofunctor \(F\). The syntax type is an initial \(F\)-algebra \((\mu F,\mathsf{in})\) when the required initial algebra exists. Each interpreter is an \(F\)-algebra, and the unique homomorphism from the initial algebra is a fold or catamorphism.

```text
Formula AST
   ├── evaluator interpreter
   ├── dependency interpreter
   ├── SQL/Datalog compiler
   ├── explanation printer
   ├── normalizer
   ├── monotonicity checker
   └── proof-term generator
```

### 7.2 Structural induction

Because formulas are inductively generated, properties can be proved by constructor cases. For selection soundness:

- `true` is immediate;
- `relation` follows from the relation lookup contract;
- `and` follows from induction hypotheses for all children;
- `or` follows from the chosen child's hypothesis;
- `not` requires the semantics and stratification assumptions;
- `exists` adds a witness and invokes the body hypothesis.

The API shape is therefore the proof structure. This is one of the clearest benefits of a deep embedding.

### 7.3 Initial chains and colimits

Under suitable accessibility or continuity assumptions, an initial algebra can be constructed from an initial chain:

\[
0 \to F0 \to F^2 0 \to F^3 0 \to \cdots
\]

and its colimit. Adámek's work characterizes conditions under which such chain constructions produce free or initial algebras; modern formalizations continue to refine and mechanize these constructions [Adámek 1974; Wißmann and Milius 2024].

For an engineer, the practical point is not to run category-theoretic colimits in TypeScript. It is that finite syntax trees are finite stages of a recursively generated language, and recursive or infinitary syntax requires explicit guardedness or completion conditions.

### 7.4 Initial versus final encodings

TypeScript supports two broad encodings.

#### Initial encoding

Use discriminated-union ASTs. New interpreters are easy to add; adding a new constructor requires updating existing interpreters. This is usually preferable for a stable kernel language whose tooling should see every node.

#### Final/tagless encoding

Represent a term as a function polymorphic over an algebra interface:

```ts
interface FormulaAlg<R> {
  relation(id: RelationId, args: readonly Term[]): R;
  and(parts: readonly R[]): R;
  not(part: R): R;
}

type Formula = <R>(alg: FormulaAlg<R>) => R;
```

New interpretations remain easy, and some host-language typing improves, but serialization and inspection require reification. Parametricity gives useful guarantees only to the extent that TypeScript and foreign code respect the encoding.

A practical system can offer a typed builder that produces an initial AST. This gives final-style authoring ergonomics with initial-style tooling.

### 7.5 Normal forms and equations

Constructors alone do not capture algebraic laws. For Boolean formulas, one may want:

\[
A \land \top = A,\quad
A \land A = A,\quad
A \land B = B \land A.
\]

For bag semantics or weighted queries, idempotence may not hold. The kernel must state which equations define each language. A normalizer can orient selected equations as rewrite rules, but termination and confluence of the rewrite system become proof obligations.

### 7.6 Strengths

- direct structural induction;
- many interpreters from one source language;
- excellent serialization and tooling;
- clear trusted kernel;
- supports staged compilation and partial evaluation;
- can expose a friendly builder API without sacrificing inspectability.

### 7.7 Weaknesses

- recursive query semantics still needs an order-theoretic layer;
- open-ended third-party extension is harder than calling JavaScript;
- binding constructs require careful representation to avoid capture bugs;
- TypeScript cannot itself establish all desired metatheorems;
- a giant universal AST becomes unmaintainable.

### 7.8 Assessment

This should be the **representation technique** for selectors, rules, effects, contracts, and link policies. It is not an alternative to relational semantics; it is how the relational and interaction languages become inspectable and inductively defined.

## 8. Architecture C: algebraic specifications and institutions

### 8.1 Basic idea

A component is not primarily a React function. It is a **theory**:

- a signature of sorts, relations, operations, events, and ports;
- sentences describing invariants and operation contracts;
- optionally, models or implementations satisfying that theory.

For example, a document selector component might declare:

```text
sort Document
sort SelectorState
operation selected : SelectorState -> Option<Document>
operation choose   : SelectorState × Document -> SelectorState
axiom choose-selects:
  selected(choose(s,d)) = some(d)
```

A chart component imports the document-selector theory and adds chart-specific vocabulary. A pipeline component imports the same theory. A workspace combines them and adds equations identifying their chosen document ports.

Institution theory abstracts the notion of a logical system into signatures, sentences, models, and a satisfaction relation invariant under change of notation [Goguen and Burstall 1992]. This is relevant when different subsystems use different logics: relational rules for selection, equational laws for lenses, temporal logic for machines, and refinement logic for operations.

### 8.2 Why an institution-like boundary is useful

Without such a boundary, “proof support” often means every subsystem must be translated into one enormous logic. An institutional architecture instead asks every logic adapter to provide:

```text
Signature
Sentence(signature)
Model(signature)
Satisfaction(model, sentence)
SignatureMorphism
sentence translation
model reduct
satisfaction condition
```

The satisfaction condition says that truth is preserved when notation changes appropriately. This lets component composition and tooling remain logic-independent at the outer layer.

A production TypeScript implementation would probably use a lighter “logic plugin” interface rather than formal institution terminology, but the abstraction prevents accidental coupling to one theorem prover.

### 8.3 Modules as colimits of theories

Suppose theories \(T_1\) and \(T_2\) share an imported interface \(T_0\):

```text
T1  ←  T0  →  T2
```

Their combined specification can often be formed as a pushout:

```text
T1  →  T
↑       ↑
T0  →  T2
```

Intuitively, the pushout includes both theories while identifying the common vocabulary according to the import maps. More general module diagrams can be assembled by colimits.

This is the right place to discuss colimits: they combine **specifications or interfaces**, not arbitrary runtime states.

### 8.4 From specification colimits to model compatibility

Models vary contravariantly with signatures: extending a signature gives a reduct operation from larger models to smaller ones. Under semi-exactness or model-amalgamation conditions, a pushout of signatures can be mapped by the model functor to a pullback of model categories. In concrete language:

> A model of the combined specification corresponds to component models whose reducts agree on the shared interface, subject to the exactness conditions of the specification framework.

These conditions matter. It is incorrect to say categorically, without qualification, that “colimits always become pullbacks of models.” Institution literature identifies exactness assumptions and practical cases where they fail [Diaconescu 2002].

### 8.5 Strengths

- explicit component contracts and invariants;
- principled heterogeneous logic support;
- theory imports, renaming, hiding, and combination;
- categorical account of modular specification;
- suitable foundation for proof artifacts and code generation.

### 8.6 Weaknesses

- substantial conceptual and tooling cost;
- model amalgamation may fail;
- specifications can drift from implementations unless generated or checked;
- too heavy for every leaf component;
- does not by itself define efficient runtime evaluation.

### 8.7 Assessment

Use this architecture at the **component and module boundary**, especially for reusable subsystems, protocol schemas, and generated verification. Do not require every presentational span to be a standalone institution theory.

## 9. Architecture D: open systems and structured cospans

### 9.1 Basic idea

An open component is a system with a declared boundary. A cospan has the shape:

\[
I \xrightarrow{i} X \xleftarrow{o} O,
\]

where \(X\) is the internal system and \(I,O\) are boundary interfaces. Structured cospans enrich this picture so the apex carries the relevant system structure. They provide a general framework for open networks and compose compatible boundaries using pushouts [Baez and Courser 2020].

For UI components, a boundary can contain typed ports rather than only directional input/output wires:

```ts
const Chart = component({
  ports: {
    primaryDocument: port.inout(DocumentRef),
    selectedMarks: port.output(SetOf(MarkRef)),
    filter: port.input(FilterExpression),
  },
  // rules, operations, machine, and renderer omitted
});
```

A pipeline may expose the same `primaryDocument` sort and a different set of ports. A workspace wires them without reaching inside their React trees.

### 9.2 Composition by pushout

If component \(X\) exposes an output boundary \(B\), and component \(Y\) exposes a compatible input boundary \(B\), composition glues the two copies of \(B\). At the structural level, this gluing is a pushout.

This gives associativity up to the relevant categorical equivalence, making large workspaces compositional rather than a collection of special-case reducers.

### 9.3 Hypergraph-like wiring

UI links are often not one-output-to-one-input functions. Multiple views can observe one document selection; a filter can feed several charts; two panels can jointly constrain one query. Cospan and hypergraph intuitions are therefore more appropriate than a simple tree or callback graph.

The architecture can support:

- fan-out by connecting several ports to one junction;
- explicit feedback, subject to guardedness or fixed-point conditions;
- hiding internal ports after composition;
- renaming and adapting boundary types;
- graphical editors whose wires have formal semantics.

### 9.4 Structure is not behavior

A structured cospan says how systems are connected. It does not automatically say:

- what a port value means;
- how conflicting writes are resolved;
- whether propagation terminates;
- whether updates are synchronous or asynchronous;
- which invariants the apex satisfies.

Those come from the chosen semantic functor, lens, transition system, or relational theory decorating the structure.

### 9.5 Strengths

- first-class, typed component boundaries;
- principled composition and rewiring;
- natural basis for visual workspace editors;
- separates component internals from network topology;
- categorical associativity and modularity.

### 9.6 Weaknesses

- requires another semantic layer for runtime meaning;
- unrestricted feedback can introduce causality problems;
- categorical equivalence may not correspond to desirable user-visible equivalence;
- dynamic mounting and disposal need an operational account.

### 9.7 Assessment

This is the strongest model for **workspace topology and component composition**. It should not replace the query kernel or state machine.

## 10. Architecture E: coalgebraic interaction machines and statecharts

### 10.1 Basic idea

Inductive data and syntax are described by algebras. Ongoing behavior is naturally described by coalgebras. A deterministic Mealy-style interaction machine has a transition function:

\[
\delta : S \times I \to S \times O,
\]

where \(S\) is state, \(I\) browser or semantic input, and \(O\) emitted operations. Equivalently, one can curry it as a coalgebra for a functor such as \(F(X)=O^I\times X^I\), depending on the chosen representation.

PBUI interaction modes fit this model:

```text
Idle
Choosing(selector, continuation)
MenuOpen(occurrence, position)
Dragging(source, candidateTargets)
Confirming(operation)
Disposed
```

Events include pointer activation, key input, occurrence unmounting, state changes, cancellation, and handler completion.

### 10.2 Coinduction and bisimulation

Two machines are behaviorally equivalent when no sequence of observations can distinguish them. Bisimulation provides a coinductive proof technique: relate states and show that related states produce compatible observations and transition to related states for every input. Universal coalgebra develops this general account across many state-based systems [Rutten 2000].

This is useful for refactoring. A promise-based `accept()` interpreter and an explicit interaction-tree interpreter can be shown equivalent at the semantic event boundary even if their internal states differ.

### 10.3 Statecharts

Flat automata become unmanageable when interaction has orthogonal modes and hierarchy. Statecharts add hierarchy, concurrency, and broadcast communication to conventional state diagrams [Harel 1987]. A PBUI statechart might separate:

```text
Pointer mode:  idle | pointing | dragging
Choice mode:   none | selecting | resolving
Overlay mode:  none | object-menu | command-palette | modal
Network mode:  online | offline | reconciling
```

An explicit machine avoids combinations that should be impossible, such as two overlays both owning the pointer or a disposed provider retaining an unresolved choice.

### 10.4 Temporal properties

A machine can be translated to a model checker or checked with a temporal logic. Candidate properties include:

```text
AG (menuOpen -> not dragging)
AG (disposed -> AX disposed)
AG (choosing -> selectableOccurrenceExists OR cancelEnabled)
AG (resolved(request) -> AX not pending(request))
```

The exact notation depends on the checker. Liveness claims require environmental assumptions: the browser may never deliver a click, the network may remain offline, and a user may decline to choose forever.

### 10.5 Strengths

- precise temporal semantics;
- explicit cancellation, interruption, and lifecycle behavior;
- coinductive behavioral equivalence;
- model checking of finite abstractions;
- better control of race conditions than scattered hooks.

### 10.6 Weaknesses

- not a good language for relational selection by itself;
- state explosion in model checking;
- hierarchy and concurrency semantics can surprise developers;
- asynchronous effects require an integration discipline;
- rich data may need abstraction before verification.

### 10.7 Assessment

Use a coalgebraic machine or statechart for the **interaction protocol**, while queries determine candidates and effect handlers perform operations.

---
## 11. Architecture F: bidirectional transformations, lenses, and consistency restoration

### 11.1 Basic idea

A linked UI is often described too casually as “shared state.” That description is correct only when both views expose the same state type and should literally observe one cell. More general links connect different representations:

```text
chart selection:    Set<MarkId>
pipeline selection: Set<RowId>
shared meaning:     Set<EntityId>
```

A bidirectional transformation defines:

1. when two states are consistent;
2. how to restore consistency after one side changes;
3. laws constraining those restorers.

Lenses are a major family of such transformations. Asymmetric lenses treat one structure as a source and another as a view. Symmetric lenses treat both sides as peers, often carrying complement information that remembers data not represented on both sides [Hofmann, Pierce, and Wagner 2011]. Delta lenses propagate changes rather than only whole new states [Johnson and Rosebrugh 2017].

### 11.2 Ordinary asymmetric lens laws

For a source \(S\), view \(V\), getter `get : S -> V`, and updater `put : S × V -> S`, common laws include:

\[
\begin{aligned}
\text{GetPut:}\quad & \operatorname{put}(s,\operatorname{get}(s)) = s, \\
\text{PutGet:}\quad & \operatorname{get}(\operatorname{put}(s,v)) = v, \\
\text{PutPut:}\quad & \operatorname{put}(\operatorname{put}(s,v_1),v_2)
                         = \operatorname{put}(s,v_2).
\end{aligned}
\]

Different lens traditions vary in exact laws and treatment of partiality. The architecture should name the selected law set rather than use “lens” as a decorative label.

### 11.3 Symmetric consistency

For peer views \(A\) and \(B\), define a consistency relation \(R \subseteq A\times B\). Restorers have shapes such as:

\[
\operatorname{putR}: A \times B \to B,
\qquad
\operatorname{putL}: B \times A \to A,
\]

or operate on deltas and complements. Laws normally require that restoration establishes consistency, stable states do not change gratuitously, and sequential composition behaves predictably.

This is a better model than “dispatch the same setter to both views” when the two components have different internal states.

### 11.4 Three linking modes

A component API should distinguish these cases explicitly.

#### Mode 1 — identity link

Both ports have the same type and semantics. Compile the link to one shared cell or one equivalence class of port identities.

```ts
workspace.identify(chart.primaryDocument, pipeline.primaryDocument);
```

#### Mode 2 — directed view link

One side is derived from the other through an asymmetric lens.

```ts
workspace.view(
  table.selectedRows,
  chart.highlightedMarks,
  rowSelectionToMarksLens,
);
```

#### Mode 3 — peer synchronization

Neither side is authoritative. Use a symmetric lens or explicit consistency-restoration protocol, including conflict and complement state.

```ts
workspace.synchronize(
  chart.filter,
  pipeline.predicate,
  filterPredicateSymmetricLens,
);
```

Treating these as one `link()` operation hides meaningful laws and conflict behavior.

### 11.5 Partiality and ambiguity

Many UI updates are not invertible. Selecting an aggregate chart bar may correspond to many rows; editing a textual predicate may not round-trip through a graphical builder; a document deleted on one replica has no ordinary value on the other.

The link policy should therefore expose:

- partial results;
- conflict values;
- user-choice requests;
- complement state;
- lossiness declarations;
- repair operations;
- authorization failures.

```ts
type RestoreResult<A> =
  | { tag: "consistent"; value: A }
  | { tag: "ambiguous"; choices: readonly A[] }
  | { tag: "conflict"; conflict: Conflict }
  | { tag: "rejected"; reason: Reason };
```

A proof-friendly system does not convert ambiguity into an arbitrary first match.

### 11.6 Strengths

- laws precisely describe linked-view behavior;
- handles unequal representations;
- separates consistency from update direction;
- supports round-trip and stability tests;
- delta variants align with incremental UI updates.

### 11.7 Weaknesses

- lawfulness can be difficult to prove for rich, partial transforms;
- conflict and complement state complicate APIs;
- composition may require stronger structures than naïve lens combinators provide;
- not every relation admits a useful deterministic restorer.

### 11.8 Assessment

Use lenses for **synchronization semantics**, not for every state access. Identity links should remain simpler; genuinely ambiguous links should expose conflicts.

## 12. Architecture G: functional reactive programming and guarded recursion

### 12.1 Basic idea

Functional reactive programming treats time-varying values and event streams as first-class semantic objects. A presentation query can be understood as a behavior:

\[
\operatorname{Candidates}_Q : \operatorname{Time} \to \mathcal{P}(\operatorname{Candidate}),
\]

or as a stream transducer consuming state changes and producing candidate-set changes.

The attractive promise is compositional time: derive the acceptable set from current state without manually subscribing and unsubscribing to every dependency.

### 12.2 Causality

A reactive output at time \(t\) must not depend on future input. Causal stream functions can be modeled so equal input prefixes imply equal output prefixes. Guarded recursion strengthens this idea by requiring recursive uses to occur “later,” making feedback productive and avoiding instantaneous cycles.

Semantic work on GUIs and reactive programming has used ultrametric spaces, guardedness, and linearity to model causality, recursive widgets, nondeterministic user input, and resource usage. Krishnaswami and Benton give a denotational GUI model in which ultrametric structure enforces causality and guardedness supports well-founded recursive definitions; later modal calculi such as Simply RaTT target reactive programming without implicit space leaks [Krishnaswami and Benton 2011; Bahr et al. 2019].

### 12.3 Why this matters to React PBUI

A callback-based system can accidentally create:

- a feedback loop where linked views update each other forever;
- a stale closure reading an old environment;
- an event subscription that survives unmount;
- a history-retaining signal with an unbounded space leak;
- a render-time side effect that is replayed by concurrent rendering.

A causal reactive core can make feedback require a delay, make dependencies explicit, and state lifecycle rules denotationally.

### 12.4 Signals are not subjects

A signal `Behavior<ProjectId>` is a changing value. It is not the project itself, nor an occurrence, nor a proof that a project is selectable. FRP should carry the outputs of the semantic kernel, not replace semantic identity and rules.

### 12.5 Pull, push, and hybrid evaluation

A PBUI runtime needs both:

- **push:** document or permission changes should promptly update highlights;
- **pull:** a committing click should revalidate against the latest state;
- **hybrid:** demand should determine which portions of a large derivation graph remain active.

Push-pull FRP and self-adjusting computation explore such combinations. The architecture should expose semantic dependencies and allow the runtime to select an evaluation strategy without changing meaning.

### 12.6 Strengths

- principled time-varying composition;
- explicit causality and feedback;
- potential static productivity and resource guarantees;
- natural bridge to rendering subscriptions;
- can eliminate stale manual observer logic.

### 12.7 Weaknesses

- semantic identity and permissions still need another layer;
- naïve FRP can leak time and space;
- glitches and transaction boundaries require precise semantics;
- higher-order dynamic networks are difficult to optimize;
- React already has a scheduling model that an FRP runtime must integrate with carefully.

### 12.8 Assessment

FRP is a useful **execution model for changing denotations**, especially if the chosen calculus enforces causality. It should not be the sole public ontology of the presentation system.

## 13. Architecture H: incremental and differential computation

### 13.1 Basic idea

A declarative query can be semantically elegant and operationally disastrous if recomputed against every occurrence after every store update. Modern incremental computation gives a separate implementation layer with a correctness contract.

The central idea is to transform a function \(f : A \to B\) into a change function or derivative:

\[
Df : A \times \Delta A \to \Delta B
\]

such that:

\[
f(a \oplus \delta a) = f(a) \oplus Df(a,\delta a).
\]

The incremental lambda calculus develops static differentiation for higher-order functional programs [Cai et al. 2014]. Differential dataflow maintains iterative computations across changing inputs and partially ordered logical times [McSherry et al. 2013]. DBSP gives an algebraic account of incremental view maintenance over streams and supports automatically transforming query circuits into incremental circuits [Budiu et al. 2023].

### 13.2 UI change algebra

The system must define what a change is for each type:

```ts
interface ChangeStructure<A, Delta> {
  empty: Delta;
  apply(base: A, delta: Delta): A;
  compose(first: Delta, second: Delta): Delta;
}
```

Examples:

- sets: additions and removals;
- maps: key-wise insert/update/delete deltas;
- numbers: additive difference or replacement;
- records: field-wise changes;
- rule outputs: signed tuple multiplicities;
- component graphs: node and edge edits;
- derivations: provenance-polynomial updates.

There is no one universal efficient delta representation. The compiler should select or require an appropriate change structure.

### 13.3 From-scratch consistency

An incremental engine is trusted only if it satisfies from-scratch consistency. Naming and memoization systems such as Adapton and Nominal Adapton emphasize a related theorem: incremental reevaluation yields results consistent with ordinary evaluation, provided naming disciplines are respected [Hammer et al. 2014; Hammer et al. 2015].

For PBUI, this theorem should be tested at three levels:

1. kernel interpreter versus incremental interpreter;
2. candidate relation versus DOM highlight projection;
3. linked-state delta propagation versus full consistency restoration.

### 13.4 Stable names and semantic identities

Incremental computation needs stable nodes. PBUI already needs typed semantic identities. The two should align without becoming identical:

- subject IDs name domain entities;
- occurrence IDs name mounted outputs;
- query node IDs name compiled expressions;
- derivation IDs name proof paths;
- component instance IDs name open systems.

Reusing an ID for a semantically different node invalidates incremental assumptions. Generating a fresh ID for every render destroys reuse. A naming discipline is therefore part of correctness, not merely performance.

### 13.5 Incremental recursion

Recursive selectors, reachability, dependency graphs, and inherited capabilities are common. Differential dataflow's partially ordered timestamps and nested iteration are relevant when maintaining such fixed points under changes. For a browser library, a smaller semi-naïve Datalog evaluator may be sufficient initially:

```text
new facts at round n
  -> join only with deltas where possible
  -> derive round n+1 delta
  -> stop when delta is empty
```

The semantic least fixed point remains the specification; semi-naïve or differential evaluation is an optimization validated against it.

### 13.6 Strengths

- reconciles declarative semantics with interactive latency;
- precise dependency-based invalidation;
- supports large mounted workspaces and recursive queries;
- provides a clear optimization-correctness theorem;
- provenance and deltas can share infrastructure.

### 13.7 Weaknesses

- change structures and differential operators add considerable complexity;
- memory retained for indexes may exceed recomputation cost on small UIs;
- opaque callbacks force coarse invalidation;
- dynamic query generation complicates reuse;
- incorrect names or transaction boundaries cause subtle bugs.

### 13.8 Assessment

Make incrementality a **compiler/runtime concern behind a pure denotation**. Do not expose memoization as the primary semantics of the public API.

## 14. Architecture I: semilattices, LVars, CRDTs, and local-first verification

### 14.1 Basic idea

When facts or state are updated in parallel or replicated, a join-semilattice can make merge deterministic:

\[
x \sqcup y = y \sqcup x,
\quad
(x \sqcup y) \sqcup z = x \sqcup (y \sqcup z),
\quad
x \sqcup x = x.
\]

If every update moves upward and replicas merge by join, message duplication and reordering do not change the eventual joined result.

LVars apply user-specified lattices to deterministic parallel programming: writes monotonically increase information, while threshold reads observe when enough information is present [Kuper and Newton 2013]. CRDTs use related algebraic conditions to obtain eventual convergence in replicated systems [Shapiro et al. 2011].

### 14.2 Where monotone state fits a UI

Good candidates include:

- accumulated provenance;
- discovered capabilities;
- append-only operation logs;
- sets of acknowledged replicas;
- immutable content-addressed assets;
- grow-only presence information within an epoch;
- analysis results that refine from unknown to known.

Poor candidates include ordinary “currently selected document” if users expect replacement and undo. It can still be encoded by a CRDT register, but the user semantics include a conflict-resolution policy, not simple set growth.

### 14.3 CALM and coordination

The CALM line of work connects monotonicity with coordination-free distributed computation. The useful design lesson is narrower than “monotone programs never need coordination”: when a distributed result can grow monotonically with new information, replicas can often make irrevocable progress without waiting for global absence information. Nonmonotone operations such as negation, uniqueness, or replacing a value may require coordination or explicit conflict semantics [Hellerstein and Alvaro 2020].

A PBUI permission query involving revocation is particularly sensitive. “Capability has been observed” is monotone; “capability is currently valid and not revoked anywhere” is not, unless the authorization model supplies epochs, leases, or an authoritative check.

### 14.4 Invariant-preserving local-first operations

Convergence alone is insufficient. Two individually legal operations can merge into an illegal state. LoRe is an example of a programming model combining reactive data, invariants, interactions, and analysis to determine when concurrent interactions require coordination to preserve safety [Haas et al. 2023].

A future distributed PBUI could classify operations:

```text
commutative and invariant-preserving
    -> execute locally and merge

convergent but jointly invariant-breaking
    -> coordinate selected operation pairs

nonconvergent
    -> provide an explicit conflict object or authoritative service
```

### 14.5 Strengths

- deterministic parallel and convergent replicated updates;
- algebraic merge laws;
- offline-first and multi-user potential;
- clear separation between monotone and coordination-requiring operations;
- suitable for proof of convergence and selected invariants.

### 14.6 Weaknesses

- not all UI state is naturally monotone;
- CRDT convergence can preserve undesirable states;
- tombstones, causal metadata, and compaction have costs;
- security revocation and absence queries remain hard;
- forcing every local state into a CRDT distorts the design.

### 14.7 Assessment

Use lattice and CRDT techniques at a **replication boundary**, not as the universal local state model. The local semantic kernel should expose enough operation structure to determine which pieces can be replicated safely.

## 15. Architecture J: algebraic effects and handlers

### 15.1 Basic idea

Interaction contains effects:

```text
choose a subject
open an object menu
perform a command
read current time
request confirmation
navigate
persist
send a remote mutation
cancel
```

Rather than calling providers and services directly, represent these operations in an algebraic effect signature and interpret them with handlers. Plotkin and Pretnar's effect-handler account treats operations and their equations as an algebraic theory; handlers provide models or interpretations of that theory [Plotkin and Pretnar 2009].

An illustrative interaction program is:

```ts
const compareProjects = Choose(activeProject).flatMap((left) =>
  Choose(activeProject.where(notSameSubject(left))).flatMap((right) =>
    Perform({ type: "openComparison", left, right }),
  ),
);
```

This is syntax. A browser handler highlights occurrences and waits for input. A test handler returns scripted choices. A static handler collects possible effects. A server handler may reject UI-only operations.

### 15.2 Why promises are not enough

A promise records eventual completion but hides the operation's semantic structure. `await pbui.accept(...)` is convenient, but once compiled into an ordinary async function the system cannot easily:

- enumerate future effects;
- replay or serialize the workflow;
- swap a deterministic test handler;
- prove cancellation laws;
- distinguish interaction from network I/O;
- model-check the continuation structure.

An effect API can still expose `await`-like syntax through generators or language transforms, while retaining an underlying interaction tree.

### 15.3 Handlers as architectural boundaries

Handlers make platform policy explicit:

```ts
const browserHandler = handle(program, {
  Choose: runOccurrenceChoice,
  Perform: dispatchAuthorizedOperation,
  Confirm: openConfirmationDialog,
  Navigate: updateRouter,
});

const testHandler = handle(program, {
  Choose: nextScriptedSubject,
  Perform: recordOperation,
  Confirm: () => true,
  Navigate: recordNavigation,
});
```

Different handlers can have different capabilities. A pure explanation interpreter can reject `Network` and `Clock` effects by type.

### 15.4 Equations and handler correctness

An effect signature should state equations only when handlers are expected to respect them. For example, logging may form a monoid; cancellation may be idempotent; two independent reads may commute. User choices generally do not commute with arbitrary state changes.

A handler correctness theorem relates abstract operations to concrete transitions. The browser handler is part of the trusted runtime unless verified against the machine semantics.

### 15.5 Strengths

- interaction programs become data;
- excellent testing and simulation;
- separates domain commands from platform effects;
- explicit cancellation and resource scopes;
- multiple interpreters and capability typing.

### 15.6 Weaknesses

- unrestricted monadic continuations limit static analysis;
- JavaScript lacks native typed algebraic effects;
- generator encodings can obscure stack traces and cancellation;
- handlers still need a state-machine and concurrency semantics;
- equations must be selected carefully.

### 15.7 Assessment

Use an effect language for **interaction orchestration and operations**. Preserve applicative or selective structure where possible and lower to an explicit machine for execution.

## 16. Architecture K: presheaves, contextual semantics, and gluing

### 16.1 Basic idea

UI meaning is contextual. A presentation can be legal in one workspace, permission scope, document revision, or component subtree and illegal in another. One categorical approach models contexts as a category \(\mathcal{C}\), with arrows representing restriction or refinement. A presheaf assigns data to each context and restriction maps to each context morphism:

\[
F : \mathcal{C}^{op} \to \mathbf{Set}.
\]

Examples:

- subjects visible in a scope;
- valid selector terms under a schema;
- capabilities available to a principal;
- occurrence indexes within a subtree;
- proofs whose assumptions are available in a context.

### 16.2 Restriction and weakening

If context \(c'\) refines \(c\), a restriction map transports information from the broader context to the narrower one where appropriate. This makes “current environment” a typed semantic index rather than an unstructured object captured by callbacks.

```text
workspace context
  ↓ restrict to document α
view context
  ↓ restrict to selected rows
mark interaction context
```

Type-theoretic contexts, capability scopes, and component nesting can all be represented by related but not necessarily identical context categories.

### 16.3 Sheaf-like gluing

A sheaf adds a gluing property: compatible local data over a cover determine a unique global datum. This is conceptually appealing for composed workspaces:

- each component provides a local model;
- overlaps describe shared ports or subjects;
- compatibility on overlaps permits a global workspace model.

This resembles the earlier pushout/pullback account but emphasizes locality and descent rather than module syntax.

### 16.4 Where it helps

- permissions and assumptions indexed by scope;
- local proofs that must agree on overlaps;
- collaborative or spatial interfaces with partial knowledge;
- plugin systems where components see restricted vocabularies;
- formal treatment of context-dependent denotation.

### 16.5 Where it becomes excessive

Most React components do not need sheaf semantics. Covers and gluing conditions are useful only if locality is a real architectural concern and the implementation has concrete restriction maps. Saying that “the component tree is a presheaf” without defining the context category and functor adds no proof value.

### 16.6 Assessment

Presheaf methods are a plausible **advanced context and locality layer**, especially for heterogeneous plugins or distributed partial views. They should not be the first implementation milestone.

---
# Part III — How the categorical constructions fit together

## 17. A warning against category washing

Category theory is valuable here because it distinguishes kinds of composition and universal property. It becomes harmful when every merge is called a colimit, every getter is called a lens, and every recursive function is called an initial algebra without specifying a category, objects, morphisms, and equations.

For each categorical claim, the design should answer:

1. What is the category?
2. What are its objects?
3. What are its morphisms?
4. What equality or equivalence is used between morphisms?
5. Does the required limit, colimit, initial algebra, or final coalgebra exist?
6. What implementation artifact corresponds to the universal object?
7. Which theorem uses the universal property?

The following map keeps the main constructions distinct.

| Design problem | Mathematical structure | Practical artifact |
|---|---|---|
| recursively generated selector/effect syntax | initial algebra \(\mu F\) | typed AST and folds |
| recursively derived facts | least fixed point of a monotone operator | rule saturation |
| ongoing interaction behavior | coalgebra, often final semantics \(\nu F\) | transition machine and traces |
| combine component theories | pushout or general colimit | composed specification |
| connect open component boundaries | structured cospan composition by pushout | workspace wiring graph |
| identify two port names | coequalizer or quotient | one binding-equivalence class |
| states agreeing on a shared value | pullback | compatible state pairs |
| transport semantics along a schema map | Kan extension or reduct/reindexing | migration/adaptation compiler |
| keep two representations consistent | lens or consistency-restoration structure | link policy |
| incrementalize a denotation | derivative/change action | delta evaluator |
| replicate monotone information | join-semilattice and homomorphisms | CRDT/LVar state |

## 18. Initial algebras, fixed points, and final coalgebras are not interchangeable

### 18.1 Initial algebra: finite construction and recursion

For an endofunctor \(F : \mathcal{C}\to\mathcal{C}\), an \(F\)-algebra is a map:

\[
a : F(A) \to A.
\]

An initial algebra \((\mu F,\mathsf{in})\) has a unique algebra homomorphism into every other \(F\)-algebra. In programming, \(\mu F\) commonly describes finite syntax or finite recursive data, and the unique homomorphism is a fold.

For selector syntax:

```text
F(X) = True
     + Relation(Terms)
     + And(List<X>)
     + Not(X)
     + Exists(Sort, X)
```

A formula is a finite tree in \(\mu F\). Evaluation, dependency extraction, and pretty-printing are folds.

### 18.2 Least fixed point: recursive definitions inside a semantic domain

A least fixed point concerns an endomap on an ordered semantic domain:

\[
F : L \to L.
\]

It gives the smallest solution of recursive equations. Rule systems use this for transitive closure, inherited capabilities, reachability, and recursive affordances.

Although an initial algebra is a fixed point up to isomorphism under Lambek's lemma, the engineering roles differ:

- the initial algebra is the **syntax generated by constructors**;
- the lattice least fixed point is the **meaning of recursive definitions**.

Conflating them hides whether induction is over a finite syntax tree or over stages of semantic approximation.

### 18.3 Final coalgebra: potentially infinite observation

An \(F\)-coalgebra is a map:

\[
c : C \to F(C).
\]

A final coalgebra \((\nu F,\mathsf{out})\) receives a unique coalgebra homomorphism from every other coalgebra. It captures observable behavior such as streams, transition systems, or possibly infinite interaction traces.

Use:

- induction for finite syntax and generated data;
- fixed-point induction or transfinite induction for recursive semantic closure;
- coinduction and bisimulation for ongoing behavior.

A request/response protocol contains both inductive and coinductive parts. The request formula is inductive syntax; the running provider is a coalgebra producing observations over time.

## 19. Fixed-point iteration in more detail

### 19.1 Tarski versus Kleene-style iteration

Tarski gives existence of least and greatest fixed points for monotone endomaps on complete lattices. It does not by itself say that the least fixed point is reached after countably many iterations from bottom.

A Kleene-style theorem adds continuity assumptions. For an \(\omega\)-continuous function on an appropriate complete partial order:

\[
\operatorname{lfp}(F) = \bigvee_{n<\omega} F^n(\bot).
\]

For finite-height lattices, the chain stabilizes at a finite stage. A design document should therefore not infer an \(\omega\)-iteration implementation merely from Tarski monotonicity.

### 19.2 Closure ordinals

The least ordinal \(\gamma\) such that \(x_\gamma=x_{\gamma+1}\) is a closure ordinal for the iteration. In finite PBUI fact domains it is finite. In an abstract semantic model with infinite values, it may be larger.

The API can attach a convergence class to recursive definitions:

```ts
type RecursionClass =
  | { tag: "finite-domain"; bound?: number }
  | { tag: "finite-height"; height: number }
  | { tag: "omega-continuous" }
  | { tag: "widened"; widening: WideningId }
  | { tag: "assumed"; justification: string };
```

The compiler rejects recursion with no accepted convergence story in strict mode.

### 19.3 Fixed-point induction

For a continuous \(F\), admissible predicate \(P\), and least fixed point \(\mu F\), a common proof rule is:

\[
P(\bot)
\quad\land\quad
\forall x.\ P(x)\Rightarrow P(F(x))
\quad\Longrightarrow\quad
P(\mu F),
\]

with an admissibility or limit-closure condition depending on the domain theory. In the transfinite formulation, this condition becomes the limit-stage obligation.

### 19.4 Greatest fixed points in UI semantics

Greatest fixed points can model coinductive safety envelopes or compatibility relations. For example, a bisimulation is often the greatest fixed point of a relation transformer. A pair of interaction states is behaviorally equivalent when it belongs to this greatest fixed point.

Least fixed points answer “what can be finitely derived?” Greatest fixed points answer “what relation can be maintained forever under observation?” Both may appear in one system.

## 20. Pushouts, coequalizers, and pullbacks for linking

Consider two views with document ports:

\[
p_c : C \to D,
\qquad
p_p : P \to D,
\]

where \(C\) and \(P\) are chart and pipeline state spaces, and \(D\) is the document-reference space.

### 20.1 Compatible states form a pullback

The states in which both views select the same document form:

\[
C \times_D P
=
\{(c,p)\in C\times P \mid p_c(c)=p_p(p)\}.
\]

This is the pullback of the two projections to \(D\). It is a **limit**: it selects compatible pairs from the product.

The pullback describes the invariant state space. It does not say how an inconsistent pair is repaired after one side changes. That operational question is answered by a shared-cell implementation, lens, transaction, or conflict protocol.

### 20.2 Identifying port names is a quotient or coequalizer

Suppose a workspace graph initially has separate port nodes `chart.document` and `pipeline.document`. Linking identifies those nodes. If two maps select the pair to identify, the universal quotient that makes their images equal is a coequalizer.

Operationally, union-find computes equivalence classes of linked identity ports. This is a concrete quotient implementation. The category-theoretic value is the universal property: any later interpretation that already treats linked ports equally factors through the quotient.

### 20.3 Composing components along a shared interface is a pushout

When two open components each include a copy of a common interface, gluing them along that interface is described by a pushout. This is not identical to taking the pullback of their state spaces:

```text
specification/topology side:  pushout glues vocabulary or boundary
model/state side:             pullback selects agreeing models/states
```

Under an exact contravariant semantics, the first can induce the second. Without the exactness condition, compatible local models may fail to amalgamate uniquely or at all.

### 20.4 A concrete TypeScript compilation

```ts
const workspace = compose(chart, pipeline)
  .identify(chart.ports.primaryDocument, pipeline.ports.primaryDocument)
  .compile({
    identityPorts: "shared-cell",
    unequalPorts: "require-lens",
  });
```

The compiler can perform:

1. type compatibility checking;
2. quotienting of identity-linked port names;
3. cycle and authority analysis;
4. allocation of one cell per equivalence class;
5. generation of projection/restriction maps to components;
6. construction of the global invariant stating that component observations agree;
7. generation of a proof obligation or law test for every nonidentity link.

## 21. Colimits of specifications and pullbacks of models

### 21.1 The contravariance

Let `Sig` be a category of signatures. A signature morphism \(\sigma:\Sigma\to\Sigma'\) maps vocabulary from a smaller signature into a larger one. A \(\Sigma'\)-model can be reduced along \(\sigma\) to a \(\Sigma\)-model:

\[
\operatorname{Mod}(\sigma):
\operatorname{Mod}(\Sigma') \to \operatorname{Mod}(\Sigma).
\]

Thus `Mod` is contravariant, or covariant from \(\mathbf{Sig}^{op}\).

If a pushout combines signatures:

\[
\Sigma_1 \leftarrow \Sigma_0 \rightarrow \Sigma_2,
\]

then a model of the combined signature reduces to a pair of component models agreeing on \(\Sigma_0\). Exactness asks whether this correspondence is a pullback in the relevant model category and whether compatible models can be amalgamated.

### 21.2 Why this is relevant to plugins

A chart plugin and pipeline plugin can be independently specified against a shared document-selection signature. The workspace does not need either plugin's implementation type. It combines their theories and asks implementations to supply compatible models.

This supports:

- plugin verification against local contracts;
- independent evolution with explicit signature morphisms;
- generated adapters and migration checks;
- multi-language components, provided each language supplies the institutional interface.

### 21.3 Where the correspondence can fail

Examples of failure include:

- hidden global resources make two local models incompatible;
- both components require ownership of a supposedly shared port;
- equations added in the pushout collapse values unexpectedly;
- one logic's model reduct loses information required for amalgamation;
- side effects create operational constraints absent from the static theory.

The architecture should make model-amalgamation checks an explicit compilation phase rather than assume composition is always valid.

## 22. Kan extensions as schema adaptation

Kan extensions are a general way to transport data or semantics along a functor. They are not required for an initial implementation, but they clarify two recurring tasks.

### 22.1 Left Kan extension: freely extend along a schema map

Suppose a plugin is written against schema \(A\), and a host embeds \(A\) into larger schema \(B\). A left Kan extension can describe the most general way to extend an \(A\)-indexed construction to \(B\) while preserving the specified mapping.

Engineering analogues include:

- deriving default behavior for newly introduced presentation forms;
- migrating facts into an expanded vocabulary;
- freely adding host context around a plugin model;
- compiling local provenance into a global namespace.

### 22.2 Right Kan extension: compatible completion

A right Kan extension often corresponds to the most general compatible way to infer or restrict behavior from surrounding observations. Possible uses include:

- collecting all host contexts in which a plugin query remains valid;
- deriving a compatible global observation from local projections;
- conservative adaptation where no arbitrary defaults may be invented.

These analogies become rigorous only after the relevant indexing categories and functors are defined. They are design tools for schema evolution, not terminology to expose in the ordinary React API.

## 23. Adjunctions and free constructions

Several layers naturally form free/forgetful adjunctions:

- free selector syntax versus its underlying signature;
- free interaction program versus its effect operations;
- free component composition versus the underlying port graph;
- free semilattice generated by facts versus a concrete semilattice model.

A free construction gives the least structure satisfying the required operations and equations. Its universal property yields a unique interpretation into every model of that structure.

This motivates a robust library pattern:

```text
user constructs a free, inspectable term
        ↓
validator checks well-formedness
        ↓
interpreter uniquely extends primitive meanings
        ↓
optimized compiler is proved equivalent to reference interpreter
```

The free term is a portable specification. The handlers and evaluators are models.

## 24. Profunctors and optics

Optics generalize lenses, traversals, prisms, and related compositional access patterns. Profunctor encodings can unify many optics and provide elegant composition [Pickering, Gibbons, and Wu 2017]. They may be useful inside the link compiler for focusing a large component state onto a port:

```ts
const primaryDocument = lens<ComponentState, DocumentRef>(...);
const selectedRows = traversal<ComponentState, RowRef>(...);
```

However, an optic only specifies access/update structure. It does not establish that two components should be linked, that an update is authorized, or that an interaction query is sound. Optics are implementation and composition tools within the synchronization layer.

## 25. A worked categorical link example

Assume:

```text
Chart specification C
  exports port chartDoc : Document

Pipeline specification P
  exports port pipelineDoc : Document

Document-port interface D
  contains one value of sort Document
```

### Step 1 — component composition

Represent each component as an open system containing an inclusion of \(D\). Form a pushout to glue the component boundaries. The resulting specification contains chart and pipeline behavior with one identified document interface.

### Step 2 — port quotient

At the graph implementation level, quotient the two port names into one equivalence class:

```text
{ chartDoc, pipelineDoc } ↦ binding-7
```

### Step 3 — state semantics

The compatible global states are pairs \((c,p)\) with equal document projections. This is the pullback \(C\times_D P\).

### Step 4 — runtime realization

If both projections are ordinary total lenses to the same `DocumentRef`, allocate one shared cell. Component-local states either read that cell or receive a projection synchronized transactionally.

### Step 5 — theorem

Assuming component updates use the generated port handler:

\[
\forall s\in\operatorname{Reachable}.
\quad
\operatorname{chartDoc}(s)=\operatorname{pipelineDoc}(s).
\]

Prove by induction over transition traces:

- initial state is constructed in the pullback;
- every generated transition writes the shared cell once and updates both projections consistently;
- unrelated transitions preserve the projections.

If updates bypass the generated handler through an opaque callback, the theorem becomes conditional on that callback respecting the port invariant.

---
# Part IV — A recommended architecture

## 26. Comparison scorecard

The following table compares the architectural families as primary foundations. Scores are qualitative: high means the family directly supports the concern, not that an implementation receives the property automatically.

| Architecture | Static proof | Recursive derivation | Temporal behavior | Component composition | Linked-state laws | Incremental execution | Distributed convergence | React ergonomics |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| callback/registry | low | low | medium | low | low | low | low | high |
| typed relational kernel | high | high | low | medium | medium | high | medium | medium |
| algebraic AST/interpreters | high | medium | medium | medium | medium | medium | low | medium |
| specification theories/institutions | high | medium | low | high | medium | low | low | low |
| structured cospans/open systems | medium | low | low | high | medium | medium | medium | medium |
| coalgebra/statecharts | high for finite abstractions | low | high | medium | medium | medium | medium | medium |
| lenses/bidirectional transformations | high for stated laws | low | medium | medium | high | medium | medium | medium |
| guarded FRP | high for causality/productivity | medium | high | medium | medium | high | medium | medium |
| differential computation | high for from-scratch theorem | high | medium | medium | medium | high | medium | low |
| semilattice/CRDT | high for convergence | medium | medium | medium | medium | high | high | medium |
| algebraic effects/handlers | high for effect structure | low | high | medium | medium | medium | medium | high |
| presheaf/contextual model | high | medium | medium | high | medium | low | medium | low |

No row dominates. The design should therefore be layered rather than doctrinaire.

## 27. Recommended stack: a relational open-system interaction architecture

The proposed stack has seven public semantic layers and two runtime layers.

```text
┌──────────────────────────────────────────────────────────────┐
│ 7. React and other renderers                                 │
│    DOM occurrences, accessibility, pointer/keyboard events   │
├──────────────────────────────────────────────────────────────┤
│ 6. Interaction programs and handlers                         │
│    Choose, Perform, Confirm, Navigate, Cancel, Observe        │
├──────────────────────────────────────────────────────────────┤
│ 5. Interaction machines                                     │
│    statecharts / coalgebraic transition systems              │
├──────────────────────────────────────────────────────────────┤
│ 4. Open components and link policies                         │
│    typed ports, pushout wiring, shared cells, lenses          │
├──────────────────────────────────────────────────────────────┤
│ 3. Operations and invariants                                 │
│    preconditions, effects, authority, postconditions         │
├──────────────────────────────────────────────────────────────┤
│ 2. Queries, rules, provenance                                │
│    typed relational AST, fixed points, stratification        │
├──────────────────────────────────────────────────────────────┤
│ 1. Schema and semantic facts                                 │
│    subjects, sorts, relations, contexts, occurrences         │
├──────────────────────────────────────────────────────────────┤
│ R1. Reference evaluator and checker                          │
├──────────────────────────────────────────────────────────────┤
│ R2. Incremental compiler, indexes, scheduler, persistence    │
└──────────────────────────────────────────────────────────────┘
```

The reference evaluator defines meaning. The optimized runtime is replaceable and must remain equivalent to it. React is one occurrence interpreter; command-line, canvas, remote, and test interpreters can coexist.

## 28. Layer 1: schema, subjects, and typed facts

### 28.1 Sort declarations

The public schema declares semantic sorts independently of JavaScript representation:

```ts
const User = sort("User", stringId());
const Document = sort("Document", stringId());
const Project = sort("Project", stringId());
const Field = sort("Field", tupleId(Document, text()));
const View = sort("View", uuidId());
const Occurrence = sort("Occurrence", uuidId());
const Context = sort("Context", uuidId());
```

A `sort` is nominal. `Document` and `Project` do not become interchangeable because both use strings.

The runtime reference contains only identity:

```ts
export interface Ref<S extends AnySort> {
  readonly sort: S["id"];
  readonly key: S["Key"];
}
```

Attributes live in relations or entity records indexed by references. This prevents stale object snapshots from serving as identity.

### 28.2 Values without identity

Not everything should be an entity. The schema also supports value sorts:

```ts
const Percentage = valueSort("Percentage", numberCodec(), {
  invariant: x => 0 <= x && x <= 100,
});
```

A value can be presented without inventing a durable ID. If an occurrence needs stable incremental identity, the occurrence itself has an ID.

### 28.3 Relations

Relations are typed declarations:

```ts
const Owner = relation("Owner", [Project, User]);
const Archived = relation("Archived", [Project]);
const FieldOf = relation("FieldOf", [Field, Document]);
const PrimaryDocument = relation("PrimaryDocument", [View, Document]);

const Denotes = relation("Denotes", [Occurrence, AnySubject]);
const Mounted = relation("Mounted", [Occurrence]);
const InView = relation("InView", [Occurrence, View]);
const RenderedAs = relation("RenderedAs", [Occurrence, Form]);
```

A heterogeneous `AnySubject` can be represented by a tagged dependent pair. The implementation should preserve the subject sort tag at runtime.

### 28.4 Transactions

Base facts change through transactions, not individual callbacks:

```ts
kernel.transact(tx => {
  tx.assert(Owner(project17, person1));
  tx.retract(Archived(project17));
  tx.assert(PrimaryDocument(chart4, docA));
});
```

A transaction defines one semantic instant for incremental evaluation and React notification. Observers never see half of a link update.

### 28.5 Revisions and consistency

Every committed transaction receives a revision:

```ts
type Revision = bigint;
```

Candidates and derivations record the revision against which they were computed. Committing a user choice performs an authoritative revalidation at the latest revision or returns a typed stale result:

```ts
type CommitResult<S extends Sort> =
  | { tag: "accepted"; candidate: Candidate<S>; revision: Revision }
  | { tag: "stale"; previous: Candidate<S>; current: readonly Candidate<S>[] }
  | { tag: "cancelled" }
  | { tag: "unauthorized"; reason: Reason };
```

This is stronger than assuming a highlighted occurrence remains valid until clicked.

## 29. Occurrences as committed semantic resources

### 29.1 Registration protocol

A renderer creates an occurrence description:

```ts
interface OccurrenceSpec<S extends AnySort> {
  readonly id: OccurrenceId;
  readonly subject: Ref<S>;
  readonly form: FormId;
  readonly view: Ref<typeof View>;
  readonly capabilities?: readonly CapabilityId[];
  readonly metadata?: Readonly<Record<string, JsonValue>>;
}
```

Registration is transactional:

```ts
const lease = runtime.mountOccurrence(spec);
lease.update(nextSpec);
lease.dispose();
```

A lease prevents duplicate disposal and associates lifecycle with a concrete runtime owner.

### 29.2 React concurrency rule

React render must remain pure. An occurrence is not mounted merely because a component function was called; concurrent React may render and discard work. Registration therefore occurs after commit through an adapter effect, and disposal occurs in cleanup.

The occurrence ID should remain stable across semantically continuous commits. The adapter can derive it from a component-instance allocator plus a local key, not from array position.

### 29.3 Direct and indirect candidates

Queries declare an occurrence policy:

```ts
type OccurrencePolicy =
  | "mounted-required"
  | "mounted-preferred"
  | "subject-only";
```

- `mounted-required` supports direct manipulation;
- `mounted-preferred` can fall back to a palette or generated result row;
- `subject-only` is a semantic query independent of current rendering.

This avoids treating virtualization as a correctness failure.

### 29.4 Occurrence-sensitive conditions

Most selectors should be extensional in the subject. Some legitimately depend on the occurrence:

```text
choose a tile in the right workspace column
choose a chart mark under the pointer
choose a visible field chip, not the hidden table column
```

The query language distinguishes subject variables from occurrence variables, making the dependency reviewable.

## 30. Layer 2: the query and rule API

### 30.1 A builder that constructs syntax

An illustrative API is:

```ts
const activeOwnedProject = defineSelector({
  id: "active-owned-project",
  result: Project,
  parameters: { currentUser: User },
  occurrence: "mounted-required",
  body: q => q.exists(Occurrence, occurrence =>
    q.and(
      q.rel(Denotes, occurrence, q.result),
      q.rel(Mounted, occurrence),
      q.rel(Owner, q.result, q.param("currentUser")),
      q.not(q.rel(Archived, q.result)),
    ),
  ),
});
```

The `body` callback receives symbolic variables and constructors. It returns a `Formula` AST. It never receives a `Project` object and is not invoked per candidate.

### 30.2 Typed variables and terms

```ts
interface Var<S extends Sort> {
  readonly sort: S;
  readonly binder: BinderId;
}

interface Term<S extends Sort> {
  readonly sort: S;
  readonly node: TermNode;
}
```

Relation application checks sorts at construction time and again during schema validation. The serialized AST uses de Bruijn indices or globally unique binder IDs to avoid variable capture.

### 30.3 Query constructors

The initial kernel can remain intentionally small:

```ts
q.rel(relation, ...terms)
q.eq(left, right)
q.and(...formulas)
q.or(...formulas)
q.not(formula)                 // stratification checked
q.exists(sort, variable => formula)
q.forall(sort, variable => formula) // compiled where supported
q.let(term, variable => formula)
q.aggregate(group, aggregate) // separate stratification rules
```

Domain convenience methods are macros that expand to this core. A small kernel is easier to mechanize and audit.

### 30.4 Derived relations

```ts
const ActiveProject = derived("ActiveProject", [Project], p =>
  q.and(
    q.rel(ProjectExists, p),
    q.not(q.rel(Archived, p)),
  ),
);

const ReachableDependency = recursive("ReachableDependency", [Stage, Stage], r => [
  rule([r.x, r.y]).when(q.rel(DependsDirectly, r.x, r.y)),
  rule([r.x, r.z]).when(
    q.exists(Stage, y => q.and(
      q.rel(DependsDirectly, r.x, y),
      q.rel(r.self, y, r.z),
    )),
  ),
], {
  recursion: { tag: "finite-domain" },
});
```

The rule compiler checks positivity of recursive occurrences and computes strongly connected components of the relation-dependency graph.

### 30.5 Selection returns witnesses

```ts
const session = runtime.choose(activeOwnedProject, {
  currentUser: person1,
});

session.candidates.subscribe(candidates => {
  // Candidate<Project>[] with occurrence and derivation IDs
});

const result = await session.result;
```

A candidate can be inspected:

```ts
runtime.explain(candidate.derivation);
```

Example result:

```json
{
  "rule": "active-owned-project",
  "subject": ["Project", "compiler"],
  "premises": [
    { "fact": "Mounted", "args": [["Occurrence", "occ-31"]] },
    { "fact": "Denotes", "args": [["Occurrence", "occ-31"], ["Project", "compiler"]] },
    { "fact": "Owner", "args": [["Project", "compiler"], ["User", "person-1"]] },
    { "stratifiedAbsence": "Archived", "args": [["Project", "compiler"]] }
  ]
}
```

### 30.6 Ranking is separate from truth

Applicability is Boolean or relational; ranking is an ordered policy:

```ts
const ranked = activeOwnedProject.rankBy([
  preferSameView(),
  preferDirectForm("project-card"),
  recencyDescending(Project.lastOpenedAt),
]);
```

A ranking does not make an invalid candidate valid. Ties have a deterministic stable rule or remain a set requiring user choice.

### 30.7 Foreign predicates

```ts
const fuzzyMatches = foreignRelation({
  id: "fuzzy-matches",
  args: [Text, Text],
  reads: [],
  purity: "pure-assumed",
  totality: "total-assumed",
  evaluate: (candidate, needle) => expensiveLibrary(candidate, needle),
  invalidation: "arguments-only",
});
```

The derivation records a foreign leaf. Formal reports state that soundness is conditional on that implementation.

## 31. Layer 3: operations, capabilities, and invariants

### 31.1 Operations are state transitions, not menu callbacks

```ts
const ArchiveProject = operation({
  id: "archive-project",
  input: { project: Project },
  requires: ({ project, context }, q) => q.and(
    q.rel(CanArchive, context.principal, project),
    q.not(q.rel(Archived, project)),
  ),
  effect: ({ project }, tx) => [
    tx.assert(Archived(project)),
    tx.emit(AuditEvent({ kind: "project-archived", project })),
  ],
  ensures: ({ project }, before, after, q) =>
    q.relAt(after, Archived, project),
});
```

The illustrative `effect` is still an AST builder. A database handler, local store handler, or remote protocol interpreter performs it.

### 31.2 Affordances are derived

```ts
const archiveAffordance = affordance({
  operation: ArchiveProject,
  label: text("Archive project"),
  group: "administration",
  danger: true,
  for: Project,
  when: ({ subject, context }, q) =>
    ArchiveProject.precondition({ project: subject, context }, q),
});
```

The menu derives available affordances from the same precondition used by execution. The authoritative handler checks it again at commit revision.

### 31.3 Capability evidence

For sensitive actions, an enabled candidate may carry a capability witness:

```ts
interface AuthorizedAction<A extends Operation> {
  readonly operation: A;
  readonly arguments: ArgumentsOf<A>;
  readonly capability: CapabilityToken;
  readonly derivation: DerivationId;
  readonly revision: Revision;
}
```

A token can be local and short-lived; it need not be a security bearer token. Its purpose is to connect UI derivation to handler validation and audit.

### 31.4 Invariant modules

```ts
const WorkspaceInvariants = invariants({
  onePrimaryDocumentPerView: formula(...),
  linkedIdentityPortsAgree: formula(...),
  occurrencesReferenceExistingViews: formula(...),
});
```

Each operation declares which relations it may change. A frame rule lets the verifier avoid rechecking invariants unaffected by those relations. More complex invariants can be discharged with SMT, theorem-prover export, or runtime assertions, depending on the selected verification tier.

## 32. Layer 4: open components and typed ports

### 32.1 Component declaration

```ts
const ChartComponent = defineComponent({
  id: "chart",
  state: ChartState,

  ports: {
    primaryDocument: inoutPort(Document, {
      semantics: "current-selection",
    }),
    highlightedRows: inputPort(SetOf(Row), {
      semantics: "highlight-set",
    }),
    selectedMarks: outputPort(SetOf(Mark), {
      semantics: "selection-set",
    }),
  },

  facts: chartFactProjection,
  machine: chartInteractionMachine,
  operations: [SetChartDocument, SelectMark],
  invariants: [ChartStateIsWellFormed],
  renderer: ChartReactRenderer,
});
```

The component's public theory is generated from ports, operations, facts, and invariants. The renderer is one implementation field, not the definition of the component.

### 32.2 Connection compatibility

Port compatibility has several dimensions:

```ts
interface PortContract<S extends Sort> {
  readonly value: S;
  readonly direction: "input" | "output" | "inout";
  readonly multiplicity: "one" | "optional" | "many";
  readonly update: "replace" | "delta" | "monotone-join";
  readonly authority: "owner" | "peer" | "observer";
  readonly temporal: "instant" | "event" | "behavior";
  readonly semantics: SemanticTag;
}
```

Equal value types are insufficient. A stream of document-open events is not compatible with a current-document behavior even though both mention `Document`.

### 32.3 Wiring API

```ts
const workspace = system("analysis-workspace")
  .add("chart", ChartComponent)
  .add("pipeline", PipelineComponent)
  .identify(
    port("chart", "primaryDocument"),
    port("pipeline", "primaryDocument"),
  )
  .connect(
    port("pipeline", "selectedRows"),
    port("chart", "highlightedRows"),
    { via: rowToHighlightDeltaLens },
  )
  .hide(port("pipeline", "internalCursor"))
  .assert(WorkspaceInvariants)
  .compile();
```

`identify` is available only for semantically equal identity ports. `connect` requires an adapter, morphism, or lens. `hide` removes a port from the external boundary while retaining internal semantics.

### 32.4 Dynamic topology

Tiles can be added and linked at runtime. The runtime treats topology edits as typed graph transactions:

```ts
workspace.reconfigure(graph =>
  graph
    .add("chart-2", ChartComponent)
    .identify(
      port("chart-2", "primaryDocument"),
      port("chart", "primaryDocument"),
    ),
);
```

The compiler incrementally recomputes affected equivalence classes and link obligations. A topology edit either commits atomically or returns a structured error.

## 33. Layer 5: interaction machines

### 33.1 Kernel machine

The generic PBUI runtime can use a small explicit machine:

```ts
type InteractionState =
  | { tag: "idle" }
  | { tag: "choosing"; session: ChoiceSessionId; selector: SelectorId }
  | { tag: "menu"; occurrence: OccurrenceId; at: Point }
  | { tag: "confirming"; operation: PendingOperationId }
  | { tag: "disposed" };
```

Events are semantic:

```ts
type InteractionEvent =
  | { tag: "begin-choice"; session: ChoiceSessionId }
  | { tag: "activate-occurrence"; occurrence: OccurrenceId }
  | { tag: "open-menu"; occurrence: OccurrenceId; at: Point }
  | { tag: "escape" }
  | { tag: "occurrence-unmounted"; occurrence: OccurrenceId }
  | { tag: "state-revised"; revision: Revision }
  | { tag: "dispose" };
```

Browser events are translated to these inputs by the renderer adapter. The machine never receives a raw React synthetic event.

### 33.2 Outputs

```ts
type InteractionOutput =
  | { tag: "resolve-choice"; session: ChoiceSessionId; result: CommitResult<AnySort> }
  | { tag: "show-menu"; occurrence: OccurrenceId; actions: readonly ActionView[] }
  | { tag: "hide-overlay" }
  | { tag: "announce"; message: AccessibleMessage }
  | { tag: "run-operation"; operation: PendingOperationId };
```

An output interpreter integrates overlays, ARIA announcements, and operation handlers.

### 33.3 Model abstraction

The full machine has unbounded IDs and domain data. For model checking, generate a finite abstraction preserving relevant predicates:

```text
candidate count: zero | one | many
occurrence status: mounted | unmounted
request age: current | stale
permission: allowed | denied
```

Prove or test that the abstraction simulates the concrete machine for the properties checked.

## 34. Layer 6: algebraic interaction programs

### 34.1 Core operations

```ts
type UIEffect<A> =
  | ChooseEffect<A>
  | PerformEffect<A>
  | ConfirmEffect<A>
  | NavigateEffect<A>
  | ObserveEffect<A>
  | CancelScopeEffect<A>;
```

A program is a free structure over these operations. The exact encoding may be a free monad, freer monad, interaction tree, or a compact custom instruction tree.

### 34.2 Authoring API

```ts
const compareOwnedProjects = program(function* ($) {
  const left = yield* $.choose(activeOwnedProject, {
    prompt: "Choose the first project",
  });

  const right = yield* $.choose(
    activeOwnedProject.where(q => q.neq(q.result, q.constant(left.subject))),
    { prompt: "Choose a different project" },
  );

  const confirmed = yield* $.confirm({
    title: "Open comparison?",
    body: describePair(left.subject, right.subject),
  });

  if (confirmed) {
    yield* $.perform(OpenComparison, {
      left: left.subject,
      right: right.subject,
    });
  }
});
```

A generator syntax is acceptable only if the builder records instructions rather than immediately performing them. If the generator's control depends on actual runtime values, the result is a resumable interaction tree built step by step; static analysis can still inspect the revealed prefix and use abstract interpretation for broader claims.

### 34.3 Resource scopes

Every interaction runs in a scope:

```ts
using scope = runtime.interactionScope();
const result = await scope.run(compareOwnedProjects);
```

Disposal cancels pending effects, releases occurrence subscriptions, and settles continuations according to a specified cancellation law. Structured concurrency is preferable to detached promises.

## 35. Layer 7: React adapter

### 35.1 Presentation component

```tsx
function ProjectCard({ project }: { project: Ref<typeof Project> }) {
  return (
    <Present
      subject={project}
      form={ProjectCardForm}
      occurrenceKey={project.key}
    >
      {occurrence => (
        <article {...occurrence.domProps}>
          <ProjectContents project={project} />
        </article>
      )}
    </Present>
  );
}
```

The adapter supplies DOM properties based on the current semantic projection:

```ts
interface OccurrenceDomProps {
  readonly "data-occurrence": string;
  readonly "data-semantic-state": "ordinary" | "candidate" | "disabled";
  readonly role?: AriaRole;
  readonly tabIndex?: number;
  readonly onClick: MouseEventHandler;
  readonly onContextMenu: MouseEventHandler;
  readonly onKeyDown: KeyboardEventHandler;
}
```

The handlers map the event to an occurrence ID and send a machine event. They do not decide selection locally.

### 35.2 Subscription protocol

The React adapter subscribes to a narrow projection using an external-store contract:

```ts
const state = useOccurrenceProjection(occurrenceId, projection => ({
  candidate: projection.isCandidate(activeSession),
  actionsRevision: projection.actionsRevision,
  documentation: projection.documentation,
}));
```

The projection should be stable under irrelevant fact changes. The incremental engine computes dependency sets; React receives one notification per committed semantic transaction.

### 35.3 Server rendering and hydration

Server-rendered markup can contain subject and form identifiers but cannot claim a mounted browser occurrence until hydration commits. The client allocates or reconciles occurrence IDs and registers them. Choice sessions should not begin on the server unless an alternate non-DOM interpreter is active.

### 35.4 Accessibility

Because applicability is semantic, keyboard and assistive-technology interaction use the same candidate relation as pointer interaction. The renderer is responsible for:

- focusability of candidate occurrences;
- announcing mode entry and exit;
- conveying disabled reasons from derivations;
- avoiding color-only highlighting;
- defining deterministic traversal when occurrences overlap or repeat one subject.

Accessibility is an interpreter obligation checked against semantic states, not a separate callback path.

## 36. Runtime architecture

### 36.1 Reference interpreter

Implement the simplest obviously correct evaluator first:

```text
facts as immutable sets
rules by straightforward stage iteration
queries by recursive AST interpretation
provenance as explicit derivation trees
links by transactionally recomputing compatible state
machine by pure transition function
```

It may be slow. It is the executable specification used in tests and differential checking.

### 36.2 Compiled indexes

The optimized runtime compiles:

- one index per relation and join key;
- selector plans by relation cardinality and bound variables;
- dependency graphs from formulas to relations;
- recursive strongly connected components;
- action indexes by subject sort and capability;
- occurrence indexes by subject, view, form, and mounted state;
- union-find structures for identity port links;
- delta propagation plans for lens links.

### 36.3 Transactions and logical time

Every external change enters as a transaction. Recursive evaluation may use internal rounds:

```text
revision 42, round 0: base deltas
revision 42, round 1: first derived deltas
revision 42, round 2: recursive closure deltas
revision 42, stable: notify observers
```

This resembles a two-dimensional logical time without requiring the full generality of differential dataflow. The public UI sees only stable revisions unless a streaming-progress selector explicitly opts into intermediate results.

### 36.4 Budgets

A browser runtime needs operational limits even for semantically terminating programs:

```ts
interface EvaluationBudget {
  readonly maxDerivedFacts: number;
  readonly maxIterations: number;
  readonly maxProvenanceNodes: number;
  readonly maxWallTimeMs: number;
}
```

Budget exhaustion yields an explicit `incomplete` result with soundness status. A sound over-approximation can still be useful for static diagnostics; a direct-manipulation selector should normally fail closed rather than highlight an unverified candidate.

### 36.5 Worker boundary

Large relational and proof computations can run in a Web Worker. Because the semantic IR and transactions are serializable, the main thread sends revisions and receives deltas. Occurrence registration remains a compact fact stream rather than sharing React objects.

---
# Part V — Verification strategy

## 37. Match each property to its proof method

A common failure in formally inspired architecture is to choose one proof technique and force every property into it. The proposed stack uses different methods for different semantic layers.

| Property | Primary technique | Typical artifact |
|---|---|---|
| AST well-formedness | inductive typing derivation | kernel type checker |
| selector soundness | structural induction on formula | mechanized metatheorem |
| recursive-rule closure | fixed-point/transfinite induction | rule-system theorem |
| query termination | finite-domain argument, stratification, sized recursion | checker certificate |
| optimized evaluation correctness | simulation or denotational equivalence | compiler proof/tests |
| incremental correctness | change-action theorem | derivative certificate |
| action invariant preservation | Hoare/refinement reasoning, SMT | verification condition |
| link round trips | equational lens laws | proof or property suite |
| machine safety | reachability/model checking | model-checker certificate |
| behavioral equivalence | bisimulation/coinduction | relation witness |
| parallel determinism | lattice/independence proof | concurrency theorem |
| replica convergence | semilattice/CRDT proof | merge-law certificate |
| local-first safety | commutativity and invariant-preservation analysis | coordination plan |
| React integration | refinement and lifecycle tests | adapter conformance suite |

## 38. The trusted computing base

The architecture should publish its trusted computing base rather than imply that TypeScript types prove the entire system.

### 38.1 Minimal trusted core

A strong target is:

1. schema decoder and validator;
2. reference formula/rule semantics;
3. proof-certificate checker;
4. transaction and revision kernel;
5. operation authorization boundary;
6. occurrence lease implementation;
7. adapter from verified plans to concrete side effects.

The incremental compiler does not need to be trusted if it emits certificates checked by the core or is continuously compared against the reference interpreter.

### 38.2 What TypeScript establishes

TypeScript can provide valuable but limited guarantees:

- nominal wrappers prevent many accidental sort mismatches;
- relation constructors can enforce arity and argument types;
- effect handlers can be required for all operations in a closed union;
- component port directions and value types can be checked;
- discriminated unions support exhaustiveness;
- builder APIs can prevent construction of some invalid ASTs.

TypeScript does not establish, by itself:

- that an arbitrary callback is pure, total, or monotone;
- that a recursive rule terminates;
- that a lens implementation satisfies its laws;
- that a React renderer registers exactly the intended occurrences;
- that a remote service enforces an operation precondition;
- that a declared refinement predicate is mathematically true;
- that unsafe casts or external data respect nominal wrappers.

Runtime validation and mechanized metatheory remain necessary for stronger claims.

### 38.3 Mechanize the kernel once

The best return on formalization effort is to mechanize a small core language rather than every application component manually. A proof assistant model can define:

```text
sorts and typed tuples
fact databases
formula syntax
formula satisfaction
positive and stratified rule semantics
least fixed points
candidate derivations
operation transition relation
machine transition relation
```

Then prove:

- type preservation of evaluation;
- soundness of derivation checking;
- least-fixed-point rule soundness;
- reference evaluator correctness;
- selected compiler rewrite laws;
- serialization round trips.

Generated component certificates are checked against this kernel.

### 38.4 Proof-producing compilation

A query compiler can return:

```ts
interface CompiledQuery<S extends Sort> {
  readonly plan: EvaluationPlan<S>;
  readonly dependencies: ReadonlySet<RelationId>;
  readonly monotonicity: MonotonicitySummary;
  readonly strata: readonly Stratum[];
  readonly convergence: ConvergenceCertificate;
  readonly equivalence: PlanEquivalenceCertificate;
}
```

A small checker verifies certificates. The optimizer may be large and untrusted; an invalid optimization is rejected.

In an early implementation, property-based differential tests can stand in for formal certificates:

```text
for generated schemas, facts, and valid queries:
  referenceEvaluate(query, facts)
    == optimizedEvaluate(compile(query), facts)
```

This is not a proof, but it preserves the architecture's separation and gives a migration path to one.

## 39. Proof obligations for selectors

### 39.1 Formula soundness

Define an inductive judgment:

\[
S,\rho \models \varphi
\]

where \(S\) is a fact state and \(\rho\) maps variables to typed values. The evaluator returns environments and derivations. Prove by induction on the derivation that every returned environment satisfies the formula.

### 39.2 Subject/occurrence coherence

For a selector producing `Candidate<S>`:

\[
\operatorname{candidate}(o,e,d)
\implies
\operatorname{Denotes}(o,e)
\land
\operatorname{HasSort}(e,S)
\land
\operatorname{validDerivation}(d).
\]

If the occurrence policy is `subject-only`, omit the occurrence premise. The type of candidate should reflect that distinction rather than use an optional field indiscriminately in the verified core.

### 39.3 Commit safety

Highlighting and committing are separate judgments:

\[
\operatorname{previewCandidate}(S_r,o,e)
\]

at revision \(r\), and:

\[
\operatorname{commitCandidate}(S_{r'},o,e)
\]

at latest revision \(r'\). The commit theorem states that an accepted result is valid in \(S_{r'}\), even if preview evidence came from \(S_r\).

### 39.4 Foreign leaves

A derivation containing a foreign predicate has an assumption set \(\Gamma\):

\[
\Gamma \vdash S,\rho\models\varphi.
\]

The UI can surface this status in diagnostics:

```text
verified: kernel
assumptions:
  - fuzzy-matches implementation satisfies declared totality
  - legacy-can-edit reads only declared dependencies
```

Proof status should be data, not marketing prose.

## 40. Proof obligations for links

### 40.1 Identity links

For identity-linked ports, prove:

- port types and semantic tags are equal;
- all members map to one equivalence class;
- every read resolves through that class;
- every write is one atomic class update;
- unlink creates a fresh class initialized with the current value;
- persistence round-trips the equivalence relation.

Union-find correctness is well understood; persistence needs a canonical class encoding rather than serializing parent pointers.

### 40.2 Lens links

At minimum, check selected round-trip and consistency laws. When exhaustive proof is not available, generate property tests from sort generators:

```ts
law("PutGet", forAll(sourceGen, viewGen), (s, v) =>
  eq(lens.get(lens.put(s, v)), v),
);
```

For partial lenses, the law quantifies only over defined operations and must state how rejection behaves.

### 40.3 Network links

For distributed links, add:

- merge commutativity, associativity, and idempotence where applicable;
- inflationary local updates for state-based semilattices;
- causal or operation-delivery assumptions;
- convergence theorem;
- separate invariant-preservation analysis.

“Both replicas eventually show the same document” and “the shown document is authorized” are separate theorems.

## 41. Proof obligations for interaction machines

### 41.1 Single resolution

Each choice session has at most one terminal output:

\[
\Box\bigl(
\operatorname{resolved}(s)
\Rightarrow
\Box\neg\operatorname{resolvesAgain}(s)
\bigr).
\]

The implementation enforces this with linear session ownership or an atomic terminal-state transition.

### 41.2 Stale occurrence safety

If an occurrence unmounts before activation is processed, the machine either rejects it or resolves it only after current-state revalidation. A DOM node reference is never accepted as semantic evidence by itself.

### 41.3 Cancellation

Cancellation should be idempotent and scoped:

```text
cancel(cancel(session)) = cancel(session)
```

Cancelling an inner confirmation should not necessarily cancel its parent workflow; the effect program specifies propagation.

### 41.4 Overlay exclusion

If the product design requires only one pointer-owning overlay, encode it as one sum-typed machine state rather than two Booleans. The property then follows from construction at the model level, and the React adapter is tested to render exactly the overlay represented by the state.

## 42. Incremental correctness proof plan

### 42.1 Start with relational algebra

Give each core operator a derivative:

- selection filters changed tuples;
- projection maps tuple changes;
- union combines changes;
- join derives changes from left delta, right delta, and their interaction;
- difference or stratified negation requires signed multiplicities or stratum recomputation;
- aggregation has an aggregate-specific state and delta.

Prove the derivative equation per constructor, then lift it by structural induction to complete queries.

### 42.2 Recursive rules

For recursive strata, prove that delta iteration reaches the same least fixed point as full iteration. A semi-naïve proof shows that each new derivation is generated without needing to reconsider combinations containing no new premise, while no derivation is lost.

### 42.3 End-to-end observer theorem

Let `renderProjection` map semantic candidate facts to occurrence display states. The desired theorem is:

\[
\operatorname{ReactSnapshot}(
  \operatorname{incrementalUpdate}(S,\Delta S))
=
\operatorname{ReactSnapshot}(
  \operatorname{fromScratch}(S\oplus\Delta S)).
\]

This theorem is conditional on the React adapter subscribing and committing according to its contract. Visual pixel equivalence is not required; semantic DOM state and accessibility outputs are the appropriate observations.

---

# Part VI — End-to-end example

## 43. Domain schema

Consider a workspace containing project tiles, a chart, and a pipeline. Chart and pipeline can be linked to one primary document. A command asks the user to choose two different active projects owned by the current user.

```ts
const schema = defineSchema({
  sorts: {
    User,
    Project,
    Document,
    View,
    Occurrence,
    Form,
    Context,
  },

  relations: {
    ProjectExists,
    Owner,
    Archived,
    ProjectDocument,
    CurrentPrincipal,
    PrimaryDocument,
    Denotes,
    Mounted,
    InView,
    RenderedAs,
    CanOpen,
    CanLinkDocument,
  },
});
```

The fact store contains identities and attributes:

```ts
kernel.transact(tx => {
  tx.assert(ProjectExists(projectCompiler));
  tx.assert(Owner(projectCompiler, person1));
  tx.assert(ProjectDocument(projectCompiler, compilerDoc));

  tx.assert(ProjectExists(projectRenderer));
  tx.assert(Owner(projectRenderer, person2));
  tx.assert(ProjectDocument(projectRenderer, rendererDoc));

  tx.assert(CurrentPrincipal(workspaceContext, person1));
});
```

## 44. Two visual forms, one denotation

The project card and ID token are registered as different occurrences and forms:

```ts
mount({
  id: occProjectCard,
  subject: projectCompiler,
  form: ProjectCardForm,
  view: projectBrowser,
});

mount({
  id: occProjectId,
  subject: projectCompiler,
  form: ProjectIdTokenForm,
  view: projectBrowser,
});
```

No project-ID-to-project conversion is needed. Both denote the same typed subject. A selector may prefer the card by ranking, but either is a sound witness.

A true conversion would involve different semantics, for example a project denoting its primary document:

```ts
const ProjectPrimaryDocument = derived(
  "ProjectPrimaryDocument",
  [Project, Document],
  (project, document) => q.rel(ProjectDocument, project, document),
);
```

A request can explicitly ask for a document reachable through this relation. The derivation explains the path.

## 45. Selector

```ts
const activeOwnedProject = defineSelector({
  id: "active-owned-project",
  result: Project,
  parameters: { context: Context },
  occurrence: "mounted-required",

  body: q => q.exists(Occurrence, occurrence =>
    q.exists(User, principal => q.and(
      q.rel(Mounted, occurrence),
      q.rel(Denotes, occurrence, q.result),
      q.rel(CurrentPrincipal, q.param("context"), principal),
      q.rel(Owner, q.result, principal),
      q.not(q.rel(Archived, q.result)),
    )),
  ),

  rank: [
    preferForm(ProjectCardForm),
    preferSameViewAsFocus(),
  ],
});
```

The selector has:

- a result sort;
- explicit parameters;
- an occurrence policy;
- an inspectable formula;
- a separate ranking.

The compiler knows it depends on `Mounted`, `Denotes`, `CurrentPrincipal`, `Owner`, and `Archived`. It can index candidate occurrences by denoted subject and update only when these relations change.

## 46. Interaction program

```ts
const OpenProjectComparison = program(function* ($) {
  const first = yield* $.choose(activeOwnedProject, {
    context: workspaceContext,
    prompt: "Choose the first active project you own",
  });

  const secondSelector = activeOwnedProject.where(q =>
    q.neq(q.result, q.constant(first.subject)),
  );

  const second = yield* $.choose(secondSelector, {
    context: workspaceContext,
    prompt: "Choose a different active project you own",
  });

  yield* $.perform(OpenComparison, {
    left: first.subject,
    right: second.subject,
  });
});
```

The first choice returns a subject and evidence, not the React object or card payload. The second query adds a semantic inequality. If both the card and token for the first project are visible, both are excluded because inequality is on project identity.

## 47. Link chart and pipeline

Component declarations expose compatible document ports:

```ts
const chart = workspace.instance("chart", ChartComponent);
const pipeline = workspace.instance("pipeline", PipelineComponent);

workspace.identify(
  chart.port("primaryDocument"),
  pipeline.port("primaryDocument"),
);
```

Compilation performs these steps:

```text
1. Verify both ports carry Document and have current-selection semantics.
2. Verify both permit peer inout identity linking.
3. Add an equation chart.primaryDocument = pipeline.primaryDocument.
4. Quotient the port graph by that equation.
5. Allocate one binding cell for the equivalence class.
6. Initialize it according to an explicit policy:
     source-wins | target-wins | require-equal | ask-user.
7. Generate component projections and transactional setters.
8. Add the linked-port invariant to the workspace theory.
```

No component knows the identity of the other. A third table can join the same class without changing chart or pipeline code.

## 48. A trace and its proof annotations

```text
revision 10
  chart.doc = doc-A
  pipeline.doc = doc-A
  no choice session

input: begin OpenProjectComparison
  machine -> Choosing(session-1, active-owned-project)
  query -> candidates occ-card-compiler, occ-id-compiler
  provenance -> both denote project-compiler

input: activate occ-id-compiler
  commit revalidates at revision 10
  result -> project-compiler
  machine -> Choosing(session-2, active-owned-project != project-compiler)

transaction revision 11
  assert Archived(project-compiler)
  incremental query retracts both compiler occurrences from session-2
  first result remains a historical program value

input: choose another valid project
  operation precondition checked at current revision
  OpenComparison transition commits

input: set pipeline.primaryDocument = doc-B
  generated class setter writes binding once
  chart and pipeline projections update in one transaction
  linked-port invariant holds at revision 12
```

Proof annotations can record:

```text
selector result: kernel-verified
foreign assumptions: none
operation precondition: checked at revision 11
link policy: identity/shared-cell
link invariant: generated by compiler
incremental result: compared against reference evaluator in debug mode
```

## 49. Failure cases become typed outcomes

### 49.1 Stale selection

The project is archived between pointer-down and commit:

```ts
{ tag: "stale", previous, current: [] }
```

The machine announces that the item is no longer selectable and remains in or exits choice mode according to program policy.

### 49.2 Link conflict

Chart shows `doc-A`, pipeline shows `doc-B`, and the link policy is `require-equal`:

```ts
{
  tag: "link-conflict",
  left: docA,
  right: docB,
  resolutions: ["use-left", "use-right", "cancel"]
}
```

### 49.3 Foreign predicate timeout

A fuzzy foreign predicate exceeds its budget:

```ts
{
  tag: "incomplete",
  soundness: "unknown-for-foreign-leaf",
  cause: "budget-exhausted",
}
```

A direct selection request fails closed. A search surface may show partial results with a progress status.

### 49.4 Authorization changed

An action remains visible from an older projection but commit authorization fails:

```ts
{ tag: "unauthorized", reason: capabilityRevoked }
```

The handler does not trust menu visibility.

---
# Part VII — Adoption, alternatives, and decision

## 50. How this differs from a CLIM-shaped decomposition

This proposal retains the valuable observation that rendered output can participate in later semantic interaction. Its decomposition is otherwise substantially different.

| CLIM-shaped concept | Proposed replacement or reinterpretation |
|---|---|
| presentation type combines semantic role and presentation protocol | semantic subject sort is separated from visual form and occurrence |
| `accept` establishes a presentation-type input context | `Choose` interprets a typed relational selector and returns a candidate witness |
| translator maps one presented type to another accepted type | occurrences directly denote subjects; genuine semantic mappings are derived relations or proof-producing morphisms |
| command table organizes commands and translators | affordances are relational derivations over operations, capabilities, context, subject, and occurrence |
| application frame combines state, panes, and command loop | open component theory, interaction machine, effect handler, and renderer are separate artifacts |
| output history records presentations | committed occurrence facts form a semantic index; persistent output history is an optional separate component |
| generic-function extensibility | algebraic syntax plus interpreters, typed plugin theories, and explicit foreign extensions |
| frame loop | coalgebraic machine and structured effect scopes |

The objective is not to claim that these replacements are universally superior. The objective is to make proof and composition boundaries first-class in a language ecosystem where runtime functions, asynchronous effects, rendering schedules, workers, and distributed state are normal.

## 51. Migration from the current PBUI API

A complete rewrite would delay learning and discard a useful working prototype. The architecture supports a sequence of adapters.

### 51.1 Phase 0 — state the laws

Before changing public types, add executable specifications for current behavior:

- direct exact-type selection;
- conversion order;
- filter evaluation and click-time revalidation;
- Escape cancellation;
- one provider's independence from another;
- menu action ordering;
- occurrence unmount behavior.

These become compatibility tests for the legacy interpreter.

### 51.2 Phase 1 — introduce typed subject identity

Add a `SubjectRef` beside existing values:

```ts
interface LegacyPresentationReference<T, V> {
  type: T;
  value: V;
  subject?: AnyRef;
  form?: FormId;
}
```

Descriptors can derive a subject reference. When absent, the adapter creates an occurrence-local value subject, preserving old semantics but not claiming cross-occurrence identity.

### 51.3 Phase 2 — add the query AST beside `filter`

```ts
type AcceptRequest<Values> =
  | LegacyAcceptRequest<Values>
  | SemanticChooseRequest;
```

Legacy `filter` becomes a foreign predicate whose dependencies default to “all environment state.” This is correct but pessimistic. Applications migrate hot paths to declarative selectors.

### 51.4 Phase 3 — make occurrences explicit

Replace local “is acceptable” checks with occurrence registration and a candidate projection. The existing `Presentation` component remains the React facade.

```tsx
<Presentation
  reference={{ type: "project", value: project }}
  subject={Project.ref(project.id)}
  form={ProjectCardForm}
>
  ...
</Presentation>
```

The provider can initially run the reference query evaluator in memory.

### 51.5 Phase 4 — replace conversions selectively

Classify each conversion:

1. two forms denote one subject — remove conversion and share `subject`;
2. an attribute lookup — model a relation;
3. a total semantic map — model a typed morphism;
4. a partial contextual interpretation — model a rule with premises and provenance;
5. an effectful lookup — move it outside selection or represent it as an explicit effectful search surface.

This classification will likely simplify the conversion graph substantially.

### 51.6 Phase 5 — derive actions from operations

Keep descriptor actions as foreign affordance providers while introducing operation declarations. Migrate security-sensitive and widely reused actions first. The menu can merge both sources and mark provenance in developer mode.

### 51.7 Phase 6 — introduce typed ports and identity links

Start only with equal-type document selection. Compile identity links to shared cells and persist equivalence classes. Add lens links only when a concrete unequal-representation use case appears.

### 51.8 Phase 7 — lower interaction into a machine

Keep the `await accept()` facade, but implement it as a handler for `Choose` effects over an explicit machine. Existing application code does not need to change immediately.

### 51.9 Phase 8 — incremental compilation

After query semantics stabilize, add indexes and deltas. Maintain a debug mode that evaluates both reference and optimized engines and reports discrepancies.

### 51.10 Phase 9 — formal kernel and certificates

Mechanize the smallest settled core. Avoid formalizing rapidly changing convenience APIs. Generate and check certificates at build time, with a compact runtime checker for untrusted plugins if needed.

### 51.11 Phase 10 — optional local-first layer

Only after operation semantics and invariants are explicit should replicated links or collaborative workspaces be introduced. Otherwise the system will replicate accidental reducer behavior rather than a stable semantic model.

## 52. A practical first implementation slice

The smallest implementation that validates the architecture is narrower than the complete proposal.

### Milestone A — semantic subjects and occurrences

Implement:

- nominal subject refs;
- forms and occurrence IDs;
- mount/update/dispose leases;
- indexes by subject, form, and view;
- a React `Present` adapter;
- direct exact-sort selectors.

### Milestone B — query AST

Implement:

- relation, equality, conjunction, disjunction, existential quantification;
- stratified unary negation;
- parameters;
- structural interpreter;
- dependency extraction;
- derivation trees;
- foreign predicates.

Do not implement arbitrary recursive rules yet.

### Milestone C — operations and affordances

Implement:

- operation schemas;
- declarative preconditions;
- action derivation;
- commit-time revalidation;
- structured failure outcomes.

### Milestone D — identity ports

Implement:

- component instances and port contracts;
- identity linking by union-find;
- atomic shared-cell transactions;
- unlinking;
- canonical persistence;
- chart/pipeline demonstration.

### Milestone E — machine and effect interpreter

Implement:

- idle/choosing/menu/disposed machine;
- `Choose`, `Perform`, and `CancelScope` effects;
- browser and scripted test handlers;
- model-based tests.

### Milestone F — recursive and incremental engine

Implement:

- positive recursive rules;
- semi-naïve evaluation;
- finite-domain convergence certificates;
- delta updates;
- reference-versus-incremental differential checking.

This sequence yields value at each step without requiring an institution framework or proof assistant before the semantic API has been tested in product code.

## 53. When another architecture should dominate

### 53.1 Choose an event-sourced architecture first when audit is primary

If the central product requirement is a legally auditable history, define commands and events as the primary semantics, then derive presentation facts from projections. The relational kernel remains useful for queries, but event history—not current fact state—is authoritative.

### 53.2 Choose a statechart-first architecture for interaction-heavy editors

A diagram editor with modal tools, gestures, drag thresholds, snapping, and concurrent pointer/keyboard modes may benefit from defining the interaction machine before the semantic query language. Presentations then serve as machine-readable hit-test results.

### 53.3 Choose an FRP-first architecture for continuous media

Audio, animation, simulation, and high-frequency visualization may require a causal signal network as the primary runtime. The relational kernel should stay off the hot sample loop and describe control-level semantics.

### 53.4 Choose a CRDT-first architecture for offline collaborative state

If every core object is concurrently edited across replicas, operation and merge semantics must be designed before local reducers. Presentation selection is then a projection of replicated state.

### 53.5 Choose a theorem-prover-native DSL when assurance dominates ecosystem fit

For medical, avionics, or similarly high-assurance environments, the core may be better implemented in Lean, Coq, Agda, F*, or another proof-oriented language and exported to JavaScript or WebAssembly. TypeScript becomes an adapter. The proposed semantics still applies, but its trusted boundary moves.

### 53.6 Keep the current callback API when the domain is small

A proof-oriented kernel has real cost. A small internal tool with dozens of objects, no plugins, no concurrency, and simple menus may be better served by the existing API plus good tests. Architecture should respond to risk and scale, not to mathematical fashion.

## 54. Performance model

The declarative architecture should publish costs in semantic terms.

### 54.1 Registration

Occurrence mounting is approximately:

```text
O(number of maintained occurrence indexes)
```

rather than scanning every active selector. A new occurrence triggers only selectors whose dependencies include changed occurrence relations and whose result sorts are compatible.

### 54.2 Query evaluation

A compiled conjunctive query cost depends on join order and index cardinality. The developer tool should show a plan:

```text
1. Mounted occurrences in focused view              18 rows
2. join Denotes by occurrence                       18 rows
3. filter subject sort Project                       6 rows
4. join Owner by project                             6 rows
5. filter current principal                          2 rows
6. anti-join Archived                                1 row
```

This is more actionable than “the predicate ran 7,000 times.”

### 54.3 Multiple active queries

Most interfaces have few active choice sessions but many affordance and style queries. Common subexpressions should be interned by normalized AST plus parameter bindings. Derived relations such as `ActiveProject` are shared rather than recomputed per menu.

### 54.4 Provenance control

Full derivation trees can be large. Modes include:

```text
none             — only truth values
witness          — retain one derivation
minimal          — retain a cost-minimal derivation
all-symbolic     — semiring/provenance expression
on-demand        — retain dependency edges and reconstruct later
```

Security audit may require more provenance than hover highlighting.

### 54.5 React rendering

Semantic candidate changes should update only affected occurrences. Subject-level deduplication must not prevent all occurrences from receiving visual state. The index maps candidate subjects back to mounted occurrences, while ranking and chosen occurrence remain separate.

### 54.6 Opaque callback cost

Foreign predicates declare a cost class:

```ts
type CostClass =
  | "constant"
  | "logarithmic"
  | "linear-in-subject"
  | "external-io"
  | "unknown";
```

This is advisory, not proof. The planner can refuse `external-io` predicates in synchronous direct-manipulation selectors and route them to an asynchronous search interpreter.

## 55. Risks

### 55.1 The universal-DSL risk

A language that attempts to include arbitrary objects, time, effects, recursion, concurrency, rendering, and proofs in one AST becomes harder to understand than the callbacks it replaces. Keep several small languages with explicit translations.

### 55.2 False proof confidence

A checked selector does not prove the database facts are true, the renderer denotes the correct subject, or the server enforces authorization. Every theorem must state assumptions and trusted adapters.

### 55.3 Host-language impedance

TypeScript users expect ordinary functions and objects. Builders must preserve familiar autocomplete and local syntax. Generated types and devtools are not optional ergonomics.

### 55.4 Semantic drift

If the React component manually derives a label from one object snapshot while the relational kernel reasons about another revision, users see incoherence. Renderers should read through typed projections tied to revisions or declare when stale display is acceptable.

### 55.5 Over-indexing

Maintaining every possible relation index is wasteful. Compile indexes from active query plans and retain them with lifecycle-aware caches.

### 55.6 Dynamic plugin trust

Untrusted plugins cannot be allowed to inject arbitrary JavaScript into the trusted kernel while retaining formal claims. Run them in a sandbox, constrain them to data IR, or mark their outputs as foreign assumptions.

### 55.7 Category-driven API leakage

Users should write `identify`, `connect`, `choose`, and `operation`, not `constructCoequalizer` or `takePullback`. Category theory guides semantics and laws; the ordinary API names domain operations.

## 56. Open research questions

The proposal leaves several questions worth prototyping or formal study.

### 56.1 A useful monotonicity type system for TypeScript builders

Can a builder track positive, negative, discrete, and monotone variable use without producing intolerable error messages? Datafun shows the semantic possibility, but a TypeScript DSL needs a pragmatic design.

### 56.2 Proof-relevant UI queries

How much derivation evidence should be retained at runtime? Can compact proof terms support explanation, authorization, ranking, and incremental invalidation without excessive memory?

### 56.3 Dynamic component colimits

Can runtime graph edits preserve useful universal properties and verification certificates incrementally, rather than recompiling the entire workspace theory?

### 56.4 Lens synthesis

For common schema mappings, can the system synthesize lawful identity or asymmetric links and ask the developer only for ambiguity policy? Schema evolution and relational view-update research may help.

### 56.5 Causal React integration

Can an occurrence adapter be given a formal refinement proof against a React-like concurrent lifecycle, including speculative rendering, transitions, hydration, and offscreen trees?

### 56.6 Selection under partial and remote knowledge

What is the correct user experience when candidate truth is `unknown`, `pending`, or valid only under a lease? A two-valued candidate model is insufficient for federated data.

### 56.7 Abstract interpretation of interaction programs

Can dependent effect programs be abstractly interpreted to infer all possible requested sorts, operation capabilities, cancellation paths, and liveness risks while preserving a convenient monadic authoring style?

### 56.8 Mechanized link compilation

A compact verified compiler from typed port graphs to shared-cell and lens networks could provide a high-value proof target. The theorem would connect graph quotienting, compatible-state invariants, and generated transition code.

### 56.9 Provenance-aware ranking

Ranking candidates by proof cost, locality, authority strength, or information loss may produce better interaction than hard-coded visual priority. The UX consequences need empirical study.

## 57. Final recommendation

The next PBUI generation should not begin by adding more callbacks to descriptors or more cases to `acceptedReference`. It should begin by defining a small semantic language and reference interpreter.

The recommended order of commitment is:

1. **Separate subject identity from occurrence and visual form.**
2. **Represent selection as a typed relational query returning proof-relevant candidates.**
3. **Represent operations and authority independently from menu rendering.**
4. **Represent components as open systems with typed ports.**
5. **Use identity links, lenses, and distributed merge structures as distinct link policies.**
6. **Execute interaction through an explicit machine and algebraic effect handlers.**
7. **Compile the denotation incrementally and retain a simple reference evaluator.**
8. **Mechanize the small kernel and check generated certificates rather than trying to prove arbitrary JavaScript.**

Transfinite induction and categorical constructions then have concrete roles:

- transfinite or fixed-point induction proves properties of recursive semantic closure;
- initial algebras support structural induction over inspectable syntax;
- final coalgebras and bisimulation reason about ongoing interaction;
- pushouts combine interfaces and open components;
- coequalizers identify linked ports;
- pullbacks characterize compatible component states;
- lenses restore consistency across unequal representations;
- derivatives preserve denotation under incremental execution;
- semilattices support deterministic or convergent growth where the domain permits it.

The architecture is intentionally plural. Its unifying idea is not one mathematical object but one engineering rule:

> Choose a semantic structure whose laws match the property being claimed, expose that structure as inspectable data, and isolate every escape into unstructured JavaScript as an explicit assumption boundary.

---

# Appendix A — Condensed API surface

```ts
// Semantic schema
const Project = sort("Project", stringId());
const Owner = relation("Owner", [Project, User]);
const Archived = relation("Archived", [Project]);

// Selector syntax
const activeOwned = defineSelector({
  result: Project,
  parameters: { user: User },
  occurrence: "mounted-required",
  body: q => q.and(
    q.rel(Owner, q.result, q.param("user")),
    q.not(q.rel(Archived, q.result)),
  ),
});

// Operation and affordance
const Archive = operation({
  input: { project: Project },
  requires: ({ project, context }, q) =>
    q.rel(CanArchive, context.principal, project),
  effect: ({ project }, tx) => [tx.assert(Archived(project))],
});

// Open components and links
const system = workspace()
  .add("chart", Chart)
  .add("pipeline", Pipeline)
  .identify(
    port("chart", "primaryDocument"),
    port("pipeline", "primaryDocument"),
  )
  .connect(
    port("pipeline", "selectedRows"),
    port("chart", "highlightedRows"),
    { via: rowHighlightLens },
  )
  .compile();

// Interaction program
const workflow = program(function* ($) {
  const project = yield* $.choose(activeOwned, { user: person1 });
  yield* $.perform(OpenProject, { project: project.subject });
});

// React occurrence
<Present subject={project} form={ProjectCardForm}>
  {occ => <article {...occ.domProps}>...</article>}
</Present>
```

# Appendix B — Law checklist

## Query kernel

- relation applications are well sorted;
- derivation checker is sound;
- recursive dependencies satisfy the selected positivity/stratification rules;
- convergence class is accepted;
- optimized plan equals reference denotation;
- foreign assumptions are listed.

## Occurrence adapter

- register only after renderer commit;
- unregister exactly once;
- stable occurrence naming obeys the naming contract;
- activated IDs are revalidated;
- semantic and accessible states agree.

## Operations

- affordance precondition implies operation precondition;
- authoritative handler rechecks at commit revision;
- effect footprint is declared;
- affected invariants are preserved;
- failures are typed and observable.

## Identity links

- port contracts are equal;
- equivalence classes are canonical in persistence;
- writes are atomic;
- unlink preserves current value in a fresh class;
- generated projections agree.

## Lens links

- consistency restoration establishes the relation;
- stable consistent inputs remain stable;
- selected round-trip laws hold;
- partiality and conflicts are explicit;
- delta composition is coherent if deltas are supported.

## Machines

- every state/event case is handled;
- terminal sessions resolve once;
- cancellation is scoped and idempotent;
- disposed state is terminal;
- stale occurrences cannot bypass revalidation;
- checked temporal properties list fairness assumptions.

## Incremental runtime

- every core operator has a valid derivative;
- transaction boundaries are preserved;
- recursive delta evaluation matches full fixed point;
- indexes are invalidated by all declared dependencies;
- debug differential checking is available.

# Appendix C — Glossary

**Affordance**  
A contextually available way to invoke an operation, together with display metadata. It is derived from subject, occurrence, context, authority, and operation preconditions.

**Candidate**  
A subject, optional occurrence witness, and derivation showing that a selector is satisfied.

**Coalgebra**  
A structure describing how a state can be observed or unfolded into future behavior.

**Colimit**  
A universal way to combine a diagram. In this proposal, colimits primarily combine signatures, theories, or open-system boundaries.

**Context**  
A typed collection of parameters and assumptions relevant to a query or interaction, not an arbitrary JavaScript environment object.

**Derivation**  
A proof-relevant record of the rule and premises establishing a result.

**Fixed point**  
A value \(x\) satisfying \(F(x)=x\). Least fixed points define the minimal closure of recursive rules.

**Foreign predicate**  
An opaque host-language extension whose declared properties are assumptions unless independently certified.

**Form**  
The visual or interaction representation used by an occurrence, separate from the subject's semantic sort.

**Institution**  
An abstraction of a logic through signatures, sentences, models, and satisfaction preserved under change of notation.

**Lens**  
A bidirectional transformation structure governed by explicit consistency or round-trip laws.

**Occurrence**  
One mounted or otherwise addressable presentation of a subject in a particular form and view.

**Port**  
A typed component boundary carrying a value, event, behavior, or delta under a declared update and authority policy.

**Presentation**  
In the broad sense, the relationship by which an occurrence denotes a semantic subject in a form. The proposed API does not make “presentation type” the sole organizing abstraction.

**Pullback**  
A universal compatible pairing. Linked component states agreeing on a shared projection form a pullback.

**Pushout**  
A universal gluing construction. It combines components or theories along a shared interface.

**Selector**  
An inspectable typed query defining acceptable subjects and, optionally, occurrence constraints and ranking.

**Subject**  
The semantic entity or value denoted by an occurrence.

**Transfinite induction**  
Induction over ordinals with base, successor, and limit cases. It is useful for properties of general closure iterations.

---

# References and further reading

The references below are primary papers or authoritative specifications used to ground the architectural alternatives. The proposed API and synthesis are original design recommendations; the cited works do not endorse this particular system.

1. **Jiří Adámek.** “Free Algebras and Automata Realizations in the Language of Categories.” *Commentationes Mathematicae Universitatis Carolinae* 15(4), 1974. <https://dml.cz/handle/10338.dmlcz/105583>
2. **Michael Arntzenius and Neelakantan R. Krishnaswami.** “Datafun: A Functional Datalog.” ICFP 2016. <https://www.rntz.net/files/datafun.pdf>
3. **Patrick Bahr, Christian Graulund, and Rasmus Ejlers Møgelberg.** “Simply RaTT: A Fitch-Style Modal Calculus for Reactive Programming without Space Leaks.” 2019. <https://arxiv.org/abs/1903.05879>
4. **John C. Baez and Kenny Courser.** “Structured Cospans.” *Theory and Applications of Categories* 35, 2020. <https://math.ucr.edu/home/baez/structured.pdf>
5. **Mihai Budiu, Frank McSherry, Leonid Ryzhyk, and Val Tannen.** “DBSP: Automatic Incremental View Maintenance for Rich Query Languages.” *Proceedings of the VLDB Endowment* 16(7), 2023. <https://www.vldb.org/pvldb/vol16/p1601-budiu.pdf>
6. **Yufei Cai, Paolo G. Giarrusso, Tillmann Rendel, and Klaus Ostermann.** “A Theory of Changes for Higher-Order Languages: Incrementalizing Lambda Calculi by Static Differentiation.” PLDI 2014. <https://arxiv.org/abs/1312.0658>
7. **Patrick Cousot and Radhia Cousot.** “Abstract Interpretation Frameworks.” *Journal of Logic and Computation* 2(4), 1992. <https://www.di.ens.fr/~cousot/publications.www/CousotCousot-JLC-n2--3-p103--179-1992.pdf>
8. **Răzvan Diaconescu.** “Grothendieck Institutions.” *Applied Categorical Structures* 10(4), 2002. <https://www.imar.ro/~diacon/PDF/gi.pdf>
9. **J. Nathan Foster, Michael B. Greenwald, Jonathan T. Moore, Benjamin C. Pierce, and Alan Schmitt.** “Combinators for Bidirectional Tree Transformations: A Linguistic Approach to the View-Update Problem.” TOPLAS 29(3), 2007. <https://inria.hal.science/inria-00484971v1/document>
10. **Joseph A. Goguen and Rod M. Burstall.** “Institutions: Abstract Model Theory for Specification and Programming.” *Journal of the ACM* 39(1), 1992. <https://cseweb.ucsd.edu/~goguen/pps/ins.pdf>
11. **Todd J. Green, Grigoris Karvounarakis, and Val Tannen.** “Provenance Semirings.” PODS 2007. <https://web.cs.ucdavis.edu/~green/papers/pods07.pdf>
12. **Jonathan Haas, Roland Mogk, Elena Yanakieva, Annette Bieniusa, and Mira Mezini.** “LoRe: A Programming Model for Verifiably Safe Local-First Software.” ECOOP 2023. <https://drops.dagstuhl.de/storage/00lipics/lipics-vol263-ecoop2023/LIPIcs.ECOOP.2023.12/LIPIcs.ECOOP.2023.12.pdf>
13. **Matthew A. Hammer et al.** “Adapton: Composable, Demand-Driven Incremental Computation.” PLDI 2014. <https://matthewhammer.org/adapton/adapton-pldi2014.pdf>
14. **Matthew A. Hammer et al.** “Incremental Computation with Names.” OOPSLA 2015. <https://arxiv.org/abs/1503.07792>
15. **David Harel.** “Statecharts: A Visual Formalism for Complex Systems.” *Science of Computer Programming* 8, 1987. <https://www.state-machine.com/doc/Harel87.pdf>
16. **Joseph M. Hellerstein and Peter Alvaro.** “Keeping CALM: When Distributed Consistency Is Easy.” *Communications of the ACM* 63(9), 2020. <https://arxiv.org/abs/1901.01930>
17. **Martin Hofmann, Benjamin C. Pierce, and Daniel Wagner.** “Symmetric Lenses.” POPL 2011. <https://www.cis.upenn.edu/~bcpierce/papers/symmetric.pdf>
18. **Michael Johnson and Robert Rosebrugh.** “Symmetric Delta Lenses and Spans of Asymmetric Delta Lenses.” *Journal of Object Technology* 16(1), 2017. <https://www.jot.fm/issues/issue_2017_01/article2.pdf>
19. **Neelakantan R. Krishnaswami and Nick Benton.** “A Semantic Model for Graphical User Interfaces.” ICFP 2011. Publication information and abstract: <https://www.cl.cam.ac.uk/~nk480/>
20. **Lindsey Kuper and Ryan R. Newton.** “LVars: Lattice-Based Data Structures for Deterministic Parallelism.” FHPC 2013. <https://users.soe.ucsc.edu/~lkuper/papers/lvars-fhpc13.pdf>
21. **Frank McSherry, Derek G. Murray, Rebecca Isaacs, and Michael Isard.** “Differential Dataflow.” CIDR 2013. <https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf>
22. **Matthew Pickering, Jeremy Gibbons, and Nicolas Wu.** “Profunctor Optics: Modular Data Accessors.” *The Art, Science, and Engineering of Programming* 1(2), 2017. <https://arxiv.org/abs/1703.10857>
23. **Gordon Plotkin and Matija Pretnar.** “Handlers of Algebraic Effects.” ESOP 2009. <https://homepages.inf.ed.ac.uk/gdp/publications/Effect_Handlers.pdf>
24. **J. J. M. M. Rutten.** “Universal Coalgebra: A Theory of Systems.” *Theoretical Computer Science* 249, 2000. <https://ir.cwi.nl/pub/48/0048D.pdf>
25. **Marc Shapiro, Nuno Preguiça, Carlos Baquero, and Marek Zawirski.** “A Comprehensive Study of Convergent and Commutative Replicated Data Types.” INRIA Research Report 7506, 2011. <https://inria.hal.science/inria-00555588v1/document>
26. **Alfred Tarski.** “A Lattice-Theoretical Fixpoint Theorem and Its Applications.” *Pacific Journal of Mathematics* 5(2), 1955. <https://msp.org/pjm/1955/5-2/pjm-v5-n2-p11-s.pdf>
27. **Thorsten Wißmann and Stefan Milius.** “Initial Algebras Unchained: A Novel Initial Algebra Construction Formalized in Agda.” 2024. <https://arxiv.org/abs/2405.09504>
28. **W3C.** “State Chart XML (SCXML): State Machine Notation for Control Abstraction.” W3C Recommendation. <https://www.w3.org/TR/scxml/>
