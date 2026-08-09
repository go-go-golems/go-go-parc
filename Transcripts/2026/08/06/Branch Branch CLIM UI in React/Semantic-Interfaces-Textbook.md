# Semantic Interfaces

## Presentation Types, Mathematical Foundations, and Proof-Oriented UI Architecture

### From Common Lisp CLIM to a Set-Theoretic PBUI in TypeScript and React

**First working edition — August 2026**

---

> A rendered object should not lose its meaning merely because it has become pixels.

---

## About this book

This book develops a presentation-based user-interface architecture from first principles. Its practical destination is an API for TypeScript and React in which rendered output retains a semantic relationship to application objects; input contexts can ask for objects by semantic type; types can be combined by union, intersection, and difference; predicates can refine applicability; translators can change representation without being confused with subtyping; actions can be selected by multiple dispatch; and matching can produce evidence rather than only a Boolean.

The route to that API is deliberately mathematical. We begin with sets, predicates, relations, equivalence relations, orders, lattices, Boolean algebras, partial functions, judgments, inference rules, and proof techniques. We then define a small **presentation type calculus**, give denotational and operational readings, state its intended laws, prove central properties, and turn those definitions into an implementation architecture.

The book is also a design manual. Every major feature is accompanied by a section titled **What can be omitted?** or **Alternative design**, so that a project can stop at a smaller coherent system instead of inheriting complexity by default.

The recurring case study is a data-oriented workbench with documents, fields, charts, pipeline views, tiles, workspaces, users, and commands. The initial PBUI implementation already has several important ideas:

- a `PresentationReference` discriminated union;
- descriptors for labels, descriptions, tones, and actions;
- a React `Presentation` wrapper;
- an asynchronous `accept` operation;
- a small conversion mechanism;
- provider-local environment and interaction state.

We retain that foundation and ask what follows when its concepts are separated more sharply.

## Intended audience

The primary reader knows ordinary JavaScript or TypeScript and React. No prior Common Lisp, CLIM, logic, or type theory is required. Mathematical maturity helps, but the necessary foundations are developed in the text.

Three reading tracks are marked throughout:

- **Builder track** — follow the examples and implementation chapters; proofs may be skimmed on a first pass.
- **Foundations track** — work through definitions, propositions, and proof exercises.
- **Research track** — study open-world typing, semantic subtyping algorithms, proof mechanization, and comparisons with language research.

## Pedagogical conventions

Each chapter contains most of the following:

- **Learning objectives**;
- **Definitions**, which introduce exact terminology;
- **Running examples** from the workbench;
- **Laws and theorems**;
- **Proofs or proof sketches**;
- **Design checkpoints** connecting mathematics to API choices;
- **Exercises** labeled *conceptual*, *proof*, *design*, or *implementation*.

A proof sketch omits routine bookkeeping but should contain the decisive argument. It is not machine-checked unless explicitly stated.

## Citation style

References use bracketed keys such as [Pierce2002] and [CLIM2]. Full bibliographic entries appear at the end. URLs are included for open resources and official project documentation. The bibliography distinguishes textbooks, research papers, specifications, and implementations.

---

# Contents

## Part I — Why semantic interfaces?

1. [Output that remembers what it means](#1-output-that-remembers-what-it-means)
2. [The CLIM model](#2-the-clim-model)
3. [A minimal PBUI in React](#3-a-minimal-pbui-in-react)
4. [Separating the relations](#4-separating-the-relations)

## Part II — Mathematical foundations

5. [Sets, predicates, and extensional meaning](#5-sets-predicates-and-extensional-meaning)
6. [Relations, equality, identity, and quotients](#6-relations-equality-identity-and-quotients)
7. [Preorders, partial orders, lattices, and closure](#7-preorders-partial-orders-lattices-and-closure)
8. [Logic, evidence, and judgments](#8-logic-evidence-and-judgments)
9. [Semantics and proof methods](#9-semantics-and-proof-methods)

## Part III — A presentation type calculus

10. [Syntax and semantic domains](#10-syntax-and-semantic-domains)
11. [Membership and semantic subtyping](#11-membership-and-semantic-subtyping)
12. [Atoms, capabilities, and nominal declarations](#12-atoms-capabilities-and-nominal-declarations)
13. [Refinements and parameterized types](#13-refinements-and-parameterized-types)
14. [Semantic identity](#14-semantic-identity)
15. [Translations, coercions, and paths](#15-translations-coercions-and-paths)
16. [Evidence-producing matching](#16-evidence-producing-matching)
17. [Actions as multimethods](#17-actions-as-multimethods)
18. [Input contexts as a transition system](#18-input-contexts-as-a-transition-system)
19. [Views, placements, subjects, and links](#19-views-placements-subjects-and-links)

## Part IV — Building the TypeScript and React API

20. [Runtime type values with static guidance](#20-runtime-type-values-with-static-guidance)
21. [The registry, compiler, and matcher](#21-the-registry-compiler-and-matcher)
22. [Performance, caching, and invalidation](#22-performance-caching-and-invalidation)
23. [React integration, interaction, and accessibility](#23-react-integration-interaction-and-accessibility)
24. [Persistence, plugins, and open-world evolution](#24-persistence-plugins-and-open-world-evolution)
25. [Testing laws and proof obligations](#25-testing-laws-and-proof-obligations)
26. [Explanations, authorization, and observability](#26-explanations-authorization-and-observability)

## Part V — Choosing a system

27. [Four coherent feature profiles](#27-four-coherent-feature-profiles)
28. [Alternative architectures](#28-alternative-architectures)
29. [Related systems and implementations](#29-related-systems-and-implementations)
30. [A staged roadmap for PBUI](#30-a-staged-roadmap-for-pbui)

## Appendices

- A. [Reference API](#appendix-a-reference-api)
- B. [Selected exercise solutions](#appendix-b-selected-exercise-solutions)
- C. [Mechanization roadmap](#appendix-c-mechanization-roadmap)
- D. [Glossary](#appendix-d-glossary)
- E. [Bibliography](#appendix-e-bibliography)

---
# Part I — Why semantic interfaces?

# 1. Output that remembers what it means

## Learning objectives

After this chapter you should be able to:

1. distinguish a rendered occurrence from the application object it presents;
2. explain why local event handlers become repetitive in object-rich interfaces;
3. describe a presentation as a semantic relation among an object, a type, and output;
4. identify the smallest useful presentation-based interaction loop;
5. recognize cases where a presentation system would add little value.

## 1.1 From widgets to meanings

A conventional interface is often described as a tree of widgets. A button owns an `onClick` callback, a table row owns another callback, and a menu item owns a third. This is a good implementation model when the principal question is *which widget received the event?*

An analytical workbench raises a different question: *which application object did the user indicate, and in what semantic role?*

Consider a field named `temperature`. It may occur as:

- a chip in a source browser;
- a table header;
- the label of a chart axis;
- an input socket in a pipeline;
- a token in command history;
- an item in an inspector;
- a sentence fragment in explanatory text.

These occurrences differ visually and structurally, but they may denote the same field. If each occurrence independently implements “map to x-axis,” “inspect,” “filter by,” and “use as command argument,” the application accumulates duplicated policy.

A presentation-based interface records a semantic assertion alongside output:

\[
\operatorname{presents}(o,\tau,x),
\]

where:

- \(o\) is an output occurrence;
- \(\tau\) is a presentation type;
- \(x\) is an application object or reference.

The assertion does not imply that the occurrence visually exposes every property of \(x\). A short label can present a large object. Nor does it imply that every occurrence has the same behavior. Behavior is selected using the presented type, current command context, gesture, environment, and possibly other arguments.

### Running example

We use a workbench containing documents, projects, fields, charts, pipelines, tiles, users, and workspaces. A minimal TypeScript representation is:

```ts
interface Values {
  document: Document;
  field: Field;
  project: Project;
  projectId: string;
  tile: TileReference;
}

type PresentationReference<V extends object> = {
  [K in keyof V & string]: {
    readonly type: K;
    readonly value: V[K];
  }
}[keyof V & string];
```

A rendered field can retain a reference:

```tsx
<Presentation
  reference={{ type: "field", value: temperatureField }}
>
  <AxisLabel>Temperature</AxisLabel>
</Presentation>
```

The child component controls appearance. The wrapper declares meaning.

## 1.2 The three-stage interaction pattern

The smallest useful semantic interaction has three stages.

### Stage 1: presentation

The application renders occurrences annotated with semantic references.

```text
[Temperature] presents <field> temperature
[Pipeline A]  presents <tile>  pipeline-placement-7
```

### Stage 2: input context

An operation declares what it needs:

```text
Choose a field belonging to document α.
```

This request is not necessarily a modal dialog. It is a temporary semantic context over the already-rendered interface.

### Stage 3: acceptance

Occurrences capable of satisfying the request become sensitive. Activating one returns an accepted reference to the operation that requested it.

```ts
const selected = await pbui.accept({
  type: FieldOf(documentId),
  prompt: "Choose a field from the active document",
});
```

The operation then constructs a command or verb. Selection and mutation remain distinct:

```ts
if (selected) {
  dispatch({
    type: "setChartXField",
    chartId,
    field: selected.value,
  });
}
```

This separation is foundational. The presentation says what an occurrence means. The input context says what is wanted. The command says what to do.

## 1.3 Why ordinary callbacks are not enough

Ordinary callbacks can implement any computable behavior. The issue is not expressiveness in the computability sense. The issue is *where knowledge resides* and *whether it composes*.

Suppose every field occurrence receives:

```ts
interface FieldOccurrenceProps {
  field: Field;
  onInspect(field: Field): void;
  onMapToX(field: Field): void;
  onMapToY(field: Field): void;
  onFilter(field: Field): void;
  onUseAsCommandArgument(field: Field): void;
}
```

The component interface grows with every global operation. A presentation wrapper instead exposes the stable semantic fact—“this is field \(f\)”—and lets context determine applicable operations.

This is an inversion of dependency:

```text
widget-centric
operation knows occurrences, and occurrences know operations

presentation-centric
occurrences declare objects; operations declare semantic requirements
```

The latter resembles dependency inversion in software architecture. Both sides depend on a semantic protocol rather than on one another's concrete components.

## 1.4 Presentations are not merely data attributes

One can add `data-object-id` attributes to DOM nodes. That is useful but insufficient. A full presentation protocol normally needs:

1. a semantic type, not only an identifier;
2. a way to recover or carry the typed value;
3. a definition of semantic identity;
4. applicability rules for input contexts;
5. transformations between representations;
6. action selection;
7. lifecycle and cancellation semantics;
8. accessibility behavior;
9. explanation and debugging facilities.

The DOM attribute is an occurrence-level projection of a richer runtime relation.

## 1.5 What a presentation system does not replace

A presentation system does not replace:

- ordinary form controls;
- local component state;
- layout and styling;
- a normalized application store;
- validation at trust boundaries;
- authorization checks on the server;
- accessible names, roles, focus, and keyboard interaction;
- transactional command execution.

It coordinates semantic interaction among them.

## 1.6 When can this chapter's machinery be omitted?

A presentation system may be unnecessary when:

- the UI is primarily a linear form;
- objects appear in only one location;
- each interaction is local to one component;
- there are few cross-cutting commands;
- there is no need to select existing output as an argument;
- the semantic vocabulary is unstable and not yet understood.

Start with ordinary components. Introduce presentations when object meaning is repeatedly reconstructed from component position, ad hoc IDs, drag payloads, or duplicated callbacks.

## 1.7 Design checkpoint

The minimal architectural commitment is:

```ts
interface PresentationOccurrence<R> {
  readonly reference: R;
  readonly occurrenceId: string;
}

interface InputContext<T> {
  readonly prompt: string;
  match(reference: unknown): T | undefined;
}
```

Everything else in this book elaborates the `match` relation and the surrounding lifecycle.

## Exercises

1. **Conceptual.** List five visual occurrences of one domain object in an application you know. Which operations are duplicated across them?
2. **Conceptual.** Give an example where two visually identical occurrences denote different objects.
3. **Design.** Rewrite a component interface with several object-specific callbacks so that it declares one semantic reference instead.
4. **Proof preparation.** State, in ordinary language, what it would mean for acceptance to be *sound*.
5. **Implementation.** Add a development-only DOM annotation `data-presentation-type` to a React wrapper. Explain why storing the complete object in a DOM property would still not define semantic identity.
6. **Critical.** Describe an interface where presentations would create more abstraction than value. Defend the simpler design.

---

# 2. The CLIM model

## Learning objectives

After this chapter you should be able to:

1. explain presentations, presentation types, input contexts, translators, commands, and command tables in CLIM;
2. map those concepts cautiously to React architecture;
3. distinguish CLIM's output-recording model from React's render tree;
4. identify which CLIM facilities this book adopts and which it leaves out.

## 2.1 CLIM in context

The Common Lisp Interface Manager, usually abbreviated CLIM, is a layered user-interface architecture developed around Common Lisp. The CLIM II specification and implementation manuals describe application frames, panes, drawing, output recording, presentation types, presentation translators, commands, command tables, input editing, and redisplay [CLIM2; LispWorksCLIM]. McCLIM is a free implementation of the CLIM II ideas [McCLIM].

CLIM matters here not because React should imitate Common Lisp syntax, but because CLIM takes semantic output seriously. Its presentation system associates output with application objects and presentation types. A command processor can establish an input context; pointer gestures over applicable presentations can then provide objects or commands. Command tables organize commands, menus, and translators.

A simplified CLIM interaction loop is:

```text
read command or argument
        ↓
establish input context
        ↓
locate applicable presentations and translators
        ↓
translate gesture into object or command
        ↓
execute command
        ↓
redisplay affected output
```

The actual system is richer, but this loop exposes the transferable architecture.

## 2.2 Application frames

A CLIM application frame brings together application state, panes, layouts, and command policy. It is not exactly a window, component, or global store.

A React analogue is distributed:

```text
CLIM application frame
  ≈ application/store instance
  + PBUI provider instance
  + environment
  + active action tables
  + transient input context
  + visual subtree
```

The analogy should not be pushed too far. React rendering is declarative and typically event-driven; a CLIM application may be described through an explicit command loop. The useful lesson is that semantic interaction belongs to an application instance, not necessarily to a process-wide singleton.

## 2.3 Presentation types

CLIM presentation types are interface-semantic types. They are distinct from ordinary Common Lisp implementation types, although they may correspond to or inspect Lisp objects. Presentation types can be parameterized and can participate in subtype relationships [LispWorksCLIM; Moore2008].

A presentation type might mean:

```text
integer between 0 and 100
a pathname satisfying a policy
a command name
a document in workspace W
a field of document D
```

The important phrase is *in the interface*. A JavaScript string does not tell us whether it denotes a project ID, document ID, field name, or user handle. A presentation type preserves that semantic role.

## 2.4 Presentations and output records

CLIM's output recording facilities retain a structured history of output. Presentations are specialized output records with semantic associations. Output records support facilities such as hit testing, scrolling, redisplay, and structured output [CLIM2; LispWorksCLIM].

React's virtual element tree is not an output history:

- unmounted output is generally not retained as a semantic record;
- DOM hit testing is delegated to the browser;
- React keys are reconciliation hints, not object identities;
- a virtualized off-screen object may have no mounted occurrence;
- redisplay is state-driven reconciliation, not CLIM incremental redisplay.

A React presentation wrapper is therefore an analogue only for *currently mounted semantic output*. A richer application can separately maintain an index of unmounted or virtualized semantic objects.

## 2.5 Input contexts

An input context describes the type of object currently being requested. When a command needs an argument, output presentations that can satisfy the requested type become sensitive.

For a chart command, the context might be:

```text
(field-of active-document)
```

A table header, source-browser chip, or pipeline socket could all satisfy that request if each presents the appropriate field.

In React, an asynchronous operation gives a natural surface syntax:

```ts
const field = await pbui.accept({
  type: FieldOf(activeDocumentId),
  prompt: "Choose the field for the horizontal axis",
});
```

Internally, this is a state transition, not a blocked thread. Chapter 18 gives an operational account.

## 2.6 Presentation translators

A presentation translator says that a source presentation can satisfy another semantic request by producing a target object or command. Applicability can depend on source type, target type, context, gesture, parameters, and a tester [CLIM2; LispWorksCLIM].

For example:

```text
presented project-id
       │ translator lookup
       ▼
accepted project object
```

The translator is not a subtype declaration. Looking up a project by ID may fail, consult an environment, require authorization, or perform I/O. We formalize translators as partial computations in Chapter 15.

## 2.7 Commands and command tables

CLIM commands are named operations with typed arguments. Command tables organize available commands, menu entries, and translators, and can inherit from other tables. This permits contextual command languages: the same object may expose different operations in an editor, administrator console, or comparison workflow.

PBUI can adopt the separation without reproducing a Lisp command parser:

```ts
type Verb =
  | { type: "inspectProject"; projectId: string }
  | { type: "archiveProject"; projectId: string }
  | { type: "linkDocumentSubjects"; leftViewId: string; rightViewId: string };
```

The presentation system discovers or constructs serializable verbs. The application interprets them.

## 2.8 What this book adopts

The proposed PBUI adopts:

- semantic presentation references;
- runtime presentation type values;
- input contexts;
- type-directed acceptance;
- translators;
- contextual action tables;
- subtype-aware applicability;
- explanation of matching and dispatch;
- object identity distinct from occurrence identity.

It extends the CLIM-inspired model with contemporary concerns:

- React provider scoping;
- TypeScript static guidance;
- normalized client state;
- persistence and network schemas;
- revision-aware memoization;
- open plugin registries;
- explicit evidence objects;
- accessible DOM interaction.

## 2.9 What this book leaves out

The core design does not require:

- a textual command parser;
- command-line completion;
- a complete gesture grammar;
- a retained output history;
- arbitrary drawing streams;
- CLIM's pane and sheet hierarchy;
- a full Common Lisp Object System analogue;
- full CLIM parameterized presentation-type syntax;
- every feature of incremental redisplay.

These can be added independently. A useful design is not measured by how many historical facilities it copies.

## 2.10 Design checkpoint: translate concepts, not APIs

An elegant modern system should preserve semantic distinctions while using native host-language forms:

| CLIM concept | PBUI form |
|---|---|
| presentation | React occurrence carrying a typed reference |
| presentation type | runtime `TypeExpr` plus TypeScript representation |
| input context | provider state and a promise-like request |
| translator | typed partial transformation with metadata |
| command | serializable application verb |
| command table | named action/dispatch scope |
| presentation tester | refinement or applicability predicate |
| output record | mounted occurrence, optionally plus semantic index |

## Exercises

1. **Reading.** Read the presentation-type and translator chapters of a CLIM guide. List three facilities not represented in the table above.
2. **Conceptual.** Explain why `ProjectId -> Project` should normally be a translator rather than a subtype.
3. **Design.** Map a desktop or web application you use onto the concepts of application frame, presentations, input contexts, and commands.
4. **Critical.** React developers sometimes say that component composition already solves this problem. Identify what component composition solves and what semantic relation it leaves implicit.
5. **Research.** Compare CLIM output records with a browser accessibility tree. Which information overlaps, and which is fundamentally different?

---

# 3. A minimal PBUI in React

## Learning objectives

After this chapter you should be able to:

1. implement a minimal presentation reference and descriptor registry;
2. represent an input context as provider state;
3. explain the limitations of exact type matching and one-step conversion;
4. preserve compatibility while preparing for a richer type algebra.

## 3.1 The discriminated reference

A strong starting point is a map from presentation names to runtime representations:

```ts
interface Values {
  document: Document;
  field: Field;
  project: Project;
  projectId: string;
  tile: TileReference;
}
```

The corresponding union is derived mechanically:

```ts
type PresentationType<V extends object> = Extract<keyof V, string>;

type PresentationReference<V extends object> = {
  [K in PresentationType<V>]: {
    readonly type: K;
    readonly value: V[K];
  }
}[PresentationType<V>];
```

This is preferable to `{ type: string; value: unknown }` because narrowing the `type` narrows the value:

```ts
function label(ref: PresentationReference<Values>): string {
  switch (ref.type) {
    case "project":
      return ref.value.title;       // Project
    case "projectId":
      return `#${ref.value}`;       // string
    case "field":
      return ref.value.name;        // Field
    default:
      return ref.type;
  }
}
```

The union is the static representation layer. It does not yet define runtime subtyping.

## 3.2 Descriptors

A descriptor supplies presentation-policy methods for one atomic type:

```ts
interface PresentationDescriptor<T, E, V> {
  label(value: T, environment: E): string;
  describe?(value: T, environment: E): unknown;
  actions?(value: T, environment: E): readonly Action<V>[];
  identity?(value: T, environment: E): SemanticIdentity;
  revision?(value: T, environment: E): string | number;
}
```

The descriptor should normally avoid rendering React elements. Keeping semantics separate from visual components has several benefits:

- the registry can be tested without a DOM;
- multiple visual renderers can present the same type;
- labels and identity remain usable in menus, logs, and commands;
- server-side or worker code can share semantic declarations.

A minimal registry is a typed dictionary:

```ts
type DescriptorMap<V extends object, E, Verb> = {
  [K in keyof V & string]: PresentationDescriptor<V[K], E, Verb>;
};
```

## 3.3 Provider-local state

The provider needs at least:

```ts
interface AcceptState<V extends object, E> {
  readonly request: AcceptRequest<V, E>;
  readonly resolve: (
    result: PresentationReference<V> | null,
  ) => void;
}
```

Starting an input context:

```ts
function accept(request: AcceptRequest<Values, Environment>) {
  return new Promise<PresentationReference<Values> | null>((resolve) => {
    setAcceptState({ request, resolve });
  });
}
```

Activating a presentation asks whether the reference is acceptable. If so, the provider resolves the request and clears transient state.

The provider must define replacement semantics. Common choices are:

1. reject a second `accept` while one is active;
2. abort the previous request;
3. stack nested contexts;
4. represent contexts as an explicit workflow machine.

For an initial implementation, rejecting or replacing is safer than an implicit stack.

## 3.4 Exact type matching

The simplest request is:

```ts
interface AcceptRequest<V extends object, E> {
  readonly types: PresentationType<V> | readonly PresentationType<V>[];
  readonly prompt: string;
  readonly filter?: (
    reference: PresentationReference<V>,
    environment: E,
  ) => boolean;
}
```

Applicability is:

```ts
function exactMatch<V extends object, E>(
  request: AcceptRequest<V, E>,
  reference: PresentationReference<V>,
  environment: E,
): boolean {
  const wanted = Array.isArray(request.types)
    ? request.types
    : [request.types];

  return wanted.includes(reference.type) &&
    (request.filter?.(reference, environment) ?? true);
}
```

This already supports useful interactions. It is also easy to reason about.

## 3.5 One-step conversions

A conversion can be tried after direct matching fails:

```ts
interface Conversion<V extends object, E> {
  convert(
    reference: PresentationReference<V>,
    environment: E,
  ): PresentationReference<V> | undefined;
}
```

The provider checks the converted result against the request. This permits `projectId -> project` without changing every occurrence.

The limitations are immediate:

- source and target types are not declared;
- every conversion may be tried for every reference;
- ambiguity is resolved by registration order;
- conversion chains are absent or ad hoc;
- conversion metadata is unavailable;
- explanation is difficult;
- identity preservation is unknown.

These limitations motivate later chapters. They are not evidence that the minimal system is wrong. A small coherent implementation is often the correct first version.

## 3.6 Presentation wrapper

A wrapper can expose states such as:

```ts
type PresentationState =
  | "ordinary"
  | "acceptable"
  | "menu-open"
  | "disabled";
```

A simplified component:

```tsx
function Presentation({ reference, children }: Props) {
  const pbui = usePbui();
  const acceptable = pbui.isAcceptable(reference);

  return (
    <span
      data-pbui="presentation"
      data-presentation-type={reference.type}
      data-state={acceptable ? "acceptable" : "ordinary"}
      role={acceptable ? "button" : undefined}
      tabIndex={acceptable ? 0 : undefined}
      onClick={() => {
        if (acceptable) pbui.commit(reference);
      }}
      onContextMenu={(event) => {
        event.preventDefault();
        pbui.openObjectMenu(reference, event.currentTarget);
      }}
    >
      {children}
    </span>
  );
}
```

Do not infer accessibility merely from `role="button"`. Chapter 23 discusses focus order, keyboard activation, status announcements, cancellation, pointer gestures, and conflicts with nested interactive elements.

## 3.7 Failure modes in the minimal design

### Duplicate object instances

Two immutable snapshots of project `p-7` are not `===`, even though they denote the same project.

### Type-name proliferation

Without intersections or refinements, an application may invent names such as:

```text
active-project
active-project-owned-by-me
active-project-owned-by-me-in-workspace-7
```

### Action duplication

If actions exist only on exact descriptors, every inspectable type repeats an `inspect` action.

### Predicate cost

An arbitrary filter may run for every occurrence on every render. A filter that scans a list makes applicability \(O(nm)\) for \(n\) occurrences and an \(m\)-element list.

### Stale applicability

A presentation can be highlighted while valid and become invalid before activation.

### Hidden ambiguity

Several conversions or action rules may apply, with registration order silently choosing one.

Each failure suggests a separate relation or protocol. Chapter 4 names them.

## 3.8 What can be left out?

A production system can remain at this chapter's level if:

- presentation type names are few;
- exact matching covers the workflows;
- conversions are rare and unambiguous;
- object identity is already normalized by stable references;
- predicates are cheap;
- actions are type-local;
- plugins are not expected.

Do not implement a type calculus preemptively. Adopt richer machinery in response to concrete pressure.

## Exercises

1. **Implementation.** Implement the discriminated-union derivation and verify that a `switch` narrows `value` correctly.
2. **Implementation.** Choose and implement a policy for starting a second input context.
3. **Design.** Add a development inspector that prints a presentation's type and label without depending on its visual child.
4. **Analysis.** For \(n\) mounted occurrences and \(k\) one-step conversions, derive the worst-case number of conversion calls in one applicability pass.
5. **Testing.** Write a test showing why JavaScript reference equality is insufficient after immutable update.
6. **Critical.** Give a case where descriptor-local actions are preferable to a global rule system.

---

# 4. Separating the relations

## Learning objectives

After this chapter you should be able to:

1. distinguish representation, membership, subtyping, identity, translation, and dispatch;
2. diagnose category errors caused by conflating those relations;
3. state the architectural principle that guides the remainder of the book.

## 4.1 One overloaded word: “is”

Developers say:

```text
A project is an entity.
This ID is a project.
This row is the same record.
This project is archivable.
This tile is linked to that chart.
This menu item is applicable.
```

The word “is” hides several different mathematical relations.

### Representation

What host-language value is carried?

```text
projectId is represented by a string
project is represented by a Project object
```

### Membership

Does a particular semantic reference belong to a presentation type?

\[
r \in \llbracket \tau \rrbracket_e
\]

### Subtyping

Is every member of one type also a member of another?

\[
\tau \leq \sigma
\]

### Identity

Do two references denote the same application object?

\[
r_1 \approx_e r_2
\]

### Translation

Can a source reference be transformed into a target reference?

\[
r \xrightarrow{t,e} r'
\]

### Capability or proposition

Does a semantic property hold?

\[
e \vDash \operatorname{Inspectable}(r)
\]

### Dispatch applicability

Does an action method's signature accept the current arguments and context?

\[
\operatorname{applicable}(m,\vec r,e)
\]

### Subject linkage

Do two views observe the same mutable selection cell?

\[
\operatorname{binding}(v_1)=\operatorname{binding}(v_2)
\]

These relations interact, but they are not interchangeable.

## 4.2 Typical category errors

### Error 1: lookup represented as subtyping

Declaring `projectId <: project` is unsound when one is a string and the other a `Project` object. A consumer expecting a project cannot safely read `.title` from the ID.

Correct relation: translation.

### Error 2: capability represented as inheritance

Declaring every inspectable object beneath one `InspectableBaseClass` forces unrelated representations into a class hierarchy.

Correct relation: capability membership or protocol implementation.

### Error 3: semantic identity represented as deep equality

Two equal-looking rows may be duplicate observations and therefore distinct. Two differently shaped values may denote the same normalized entity.

Correct relation: explicit semantic identity.

### Error 4: permission represented as stable type ancestry

“Archivable by the current user” depends on environment and time. It is not an eternal nominal parent.

Correct relation: environment-dependent refinement.

### Error 5: view linkage represented as object equality

A chart view and pipeline view can be distinct objects while intentionally sharing one document selector.

Correct relation: shared binding identity.

### Error 6: action priority represented as registration order

When two action methods apply, whichever was imported first should not silently win.

Correct relation: specificity plus explicit preference for genuine ambiguity.

## 4.3 The six-protocol principle

A mature semantic UI should normally expose independent protocols for:

1. **representation** — the JavaScript value associated with an atomic presentation type;
2. **typing** — membership and subtype relations among semantic type expressions;
3. **identity** — application-level sameness;
4. **refinement evidence** — propositions that currently hold;
5. **translation** — partial changes of representation or role;
6. **behavior dispatch** — applicable renderers, actions, and commands.

Subject bindings form a seventh protocol at the application-model level.

This separation resembles long-standing lessons from programming-language design. Behavioral subtyping concerns substitutability, not arbitrary conversion [LiskovWing1994]. Multiple-dispatch systems distinguish method applicability from conversion [JuliaMethods]. Refinement systems distinguish base representation from proven propositions [LiquidTypes; TypedRacket].

## 4.4 A dependency diagram

```text
JavaScript representation
        │
        ▼
Presentation reference ───── identity protocol ───── same domain object?
        │
        ├──── membership evaluator ───── belongs to TypeExpr?
        │                                   │
        │                                   └──── refinement evidence
        │
        ├──── translator graph ───────── changes representation/role
        │
        └──── dispatcher ─────────────── selects behavior from matches

View model ───── subject binding ───── shares selected document/state
```

A lower layer should not secretly perform the work of another layer. For example, subtype checking should not run a network lookup. Translation may do so, but must declare its effect and asynchrony.

## 4.5 Design checkpoint: substitutability

A useful test for a proposed subtype declaration is:

> Can every value presented as the subtype be passed directly, without conversion or lookup, to every semantic consumer of the supertype while preserving the consumer's stated expectations?

This combines representation safety with behavioral intent. It does not solve every variance or mutation issue, but it filters obvious errors.

For capabilities, ask instead:

> Does the presentation currently satisfy the proposition or support the protocol?

For translation:

> Is there a computation that may produce the requested representation?

For identity:

> Do these references denote one domain object despite different occurrences or representations?

## 4.6 What can be left out?

A small system does not need seven public namespaces. Separation can begin conceptually:

```ts
registry.sameObject(...)
registry.isSubtype(...)
registry.translate(...)
registry.actionsFor(...)
```

The important requirement is that one operation is not implemented by pretending to be another.

## Exercises

1. **Classification.** Classify each statement as representation, membership, subtyping, identity, translation, refinement, dispatch, or binding:
   - “A chart can be inspected.”
   - “This token resolves to project 7.”
   - “These two rows refer to the same database record.”
   - “An employee can be consumed as a person.”
   - “Both tiles follow the same selected document.”
2. **Counterexample.** Construct a counterexample to `string project ID <: Project`.
3. **Design.** For a file browser, separate `path`, `file`, `readable`, `selected`, and `same inode` into the appropriate relations.
4. **Proof preparation.** Explain why semantic identity should be transitive. What UI anomaly occurs if it is not?
5. **Architecture.** Find one overloaded relation in an existing codebase and propose a separated protocol.

---
# Part II — Mathematical foundations

# 5. Sets, predicates, and extensional meaning

## Learning objectives

After this chapter you should be able to:

1. read a type as a set of semantic references;
2. move between set notation and predicate notation;
3. derive union, intersection, difference, top, and bottom laws;
4. distinguish extensional meaning from syntactic representation;
5. explain why this viewpoint is called semantic subtyping.

## 5.1 Universes and elements

A **set** is a collection considered by membership. We write

\[
x \in A
\]

when \(x\) is a member of set \(A\), and

\[
x \notin A
\]

otherwise. A universe \(\Omega\) fixes the collection of objects under discussion.

For PBUI, an element of \(\Omega\) is not necessarily a raw JavaScript value. It is a semantic reference:

\[
r = \langle a,v\rangle,
\]

where \(a\) is an atomic presentation tag and \(v\) is its representation.

Examples are:

\[
\langle \textsf{project}, p_7\rangle,
\qquad
\langle \textsf{project-id}, \texttt{"p-7"}\rangle,
\qquad
\langle \textsf{field}, f_{temperature}\rangle.
\]

We write \(\Omega_R\) when the universe depends on registry \(R\). In an implementation, the universe is often potentially infinite: all references that can be constructed according to the registered representation contracts.

## 5.2 A type denotes a set

The central interpretation of this book is:

> A presentation type denotes the set of references acceptable as that type.

If \(\tau\) is a type expression, its denotation in registry \(R\) and environment \(e\) is

\[
\llbracket \tau \rrbracket^R_e \subseteq \Omega_R.
\]

The brackets \(\llbracket - \rrbracket\) mean “the semantic meaning of.”

For example:

\[
\llbracket \textsf{Project} \rrbracket^R_e
= \{\langle \textsf{project},p\rangle \mid p \text{ is a registered project representation}\}.
\]

A refinement can depend on the environment:

\[
\llbracket \operatorname{OwnedByCurrentUser}(\textsf{Project}) \rrbracket^R_e
= \{r \in \llbracket \textsf{Project} \rrbracket^R_e
\mid \operatorname{owner}(r)=e.\operatorname{currentUser}\}.
\]

The environment parameter is explicit because permission, ownership, visibility, selection, and lifecycle state can change.

## 5.3 Predicates as characteristic functions

Every set \(A \subseteq \Omega\) has a **characteristic predicate**:

\[
\chi_A : \Omega \to \{\mathsf{true},\mathsf{false}\}
\]

such that

\[
\chi_A(x)=\mathsf{true} \quad\text{iff}\quad x\in A.
\]

Conversely, every Boolean predicate \(p : \Omega \to \mathsf{Bool}\) determines a set:

\[
\{x\in\Omega \mid p(x)\}.
\]

This correspondence explains why arbitrary lambdas can define refinements:

```ts
const activeProject = (reference: ProjectRef): boolean =>
  !reference.value.archived;
```

Semantically:

\[
\{r\in\llbracket\textsf{Project}\rrbracket_e
\mid \neg\operatorname{archived}(r)\}.
\]

However, a JavaScript function is an opaque *implementation* of a predicate. The runtime cannot automatically know its dependencies, purity, cost, or logical relationship to another function. Later chapters separate the mathematical predicate from its registered executable witness.

## 5.4 Set operations as type constructors

Let \(A,B\subseteq\Omega\).

### Union

\[
A\cup B = \{x\mid x\in A \lor x\in B\}.
\]

A union type accepts either alternative:

\[
\llbracket \tau\lor\sigma\rrbracket_e
=\llbracket\tau\rrbracket_e\cup\llbracket\sigma\rrbracket_e.
\]

Example:

```text
Project ∨ Workspace
```

### Intersection

\[
A\cap B = \{x\mid x\in A \land x\in B\}.
\]

An intersection type requires both properties:

```text
Project ∧ Inspectable
```

### Complement and difference

Relative to a universe \(\Omega\), the complement is:

\[
\overline{A}=\Omega\setminus A.
\]

Difference is:

\[
A\setminus B=\{x\mid x\in A\land x\notin B\}.
\]

For an extensible UI, difference is often safer to expose than unrestricted complement:

```text
Project \ Archived
```

Its meaning is stable relative to `Project`, whereas global `¬Archived` includes every non-archived object in the registry universe.

### Top and bottom

The **top type** denotes the whole universe:

\[
\llbracket\top\rrbracket_e=\Omega_R.
\]

The **bottom type** denotes the empty set:

\[
\llbracket\bot\rrbracket_e=\varnothing.
\]

Bottom is useful for impossible branches and ambiguity analysis even though no occurrence can inhabit it.

## 5.5 Extensional equality

Two sets are equal when they have the same members:

\[
A=B \quad\text{iff}\quad \forall x.\;x\in A \Leftrightarrow x\in B.
\]

This is the **principle of extensionality**. Applied to types:

\[
\tau \equiv \sigma
\quad\text{iff}\quad
\forall e.\;\llbracket\tau\rrbracket_e=\llbracket\sigma\rrbracket_e.
\]

The expressions may look different while denoting the same set:

\[
\tau\land\top \equiv \tau,
\]

\[
\tau\lor\bot \equiv \tau,
\]

\[
\tau\land(\sigma\lor\rho)
\equiv
(\tau\land\sigma)\lor(\tau\land\rho).
\]

A runtime may normalize expressions to exploit these equivalences, but semantic equality is the criterion—not identical syntax.

## 5.6 Boolean laws

The powerset \(\mathcal P(\Omega)\), equipped with union, intersection, complement, empty set, and universe, forms a Boolean algebra. Therefore type denotations satisfy familiar laws.

### Commutativity

\[
\tau\lor\sigma\equiv\sigma\lor\tau,
\qquad
\tau\land\sigma\equiv\sigma\land\tau.
\]

### Associativity

\[
(\tau\lor\sigma)\lor\rho
\equiv
\tau\lor(\sigma\lor\rho),
\]

and similarly for intersection.

### Idempotence

\[
\tau\lor\tau\equiv\tau,
\qquad
\tau\land\tau\equiv\tau.
\]

### Absorption

\[
\tau\lor(\tau\land\sigma)\equiv\tau,
\]

\[
\tau\land(\tau\lor\sigma)\equiv\tau.
\]

### De Morgan laws

\[
\neg(\tau\lor\sigma)\equiv\neg\tau\land\neg\sigma,
\]

\[
\neg(\tau\land\sigma)\equiv\neg\tau\lor\neg\sigma.
\]

### Proof of one law

We prove \(A\cap(B\cup C)=(A\cap B)\cup(A\cap C)\).

Take arbitrary \(x\).

\[
\begin{aligned}
x\in A\cap(B\cup C)
&\Leftrightarrow x\in A \land x\in(B\cup C)\\
&\Leftrightarrow x\in A \land (x\in B\lor x\in C)\\
&\Leftrightarrow (x\in A\land x\in B)\lor(x\in A\land x\in C)\\
&\Leftrightarrow x\in(A\cap B)\cup(A\cap C).
\end{aligned}
\]

Because \(x\) was arbitrary, extensionality gives equality. This elementwise method is the standard proof pattern for set identities.

## 5.7 Finite worked model

Let the universe be:

\[
\Omega=\{p_1,p_2,p_3,w_1\}.
\]

Suppose:

\[
\textsf{Project}=\{p_1,p_2,p_3\},
\]

\[
\textsf{Archived}=\{p_3\},
\]

\[
\textsf{Inspectable}=\{p_1,p_2,w_1\}.
\]

Then:

\[
\textsf{Project}\setminus\textsf{Archived}
=\{p_1,p_2\},
\]

\[
\textsf{Project}\cap\textsf{Inspectable}
=\{p_1,p_2\},
\]

and these two expressions happen to be extensionally equal in this model. They need not remain equal after adding an inspectable archived project or a non-inspectable active project.

This distinction matters for tests. Equality observed over a finite fixture is not proof of universal equivalence.

## 5.8 Semantic versus syntactic types

A **syntactic type expression** is a data structure:

```ts
{
  kind: "intersection",
  members: [
    { kind: "atom", id: "project" },
    { kind: "capability", id: "inspectable" },
  ],
}
```

Its **semantic type** is the set it denotes. Semantic subtyping begins with denotation and defines subtype by inclusion. This approach is associated with set-theoretic type systems and is developed in work on semantic subtyping and CDuce [FrischCastagnaBenzaken2008; Castagna2022; CDuce].

The UI type algebra in this book is deliberately smaller than a programming-language type system. It does not initially type functions, mutable references, recursive data, or polymorphic programs. It uses the same semantic idea for a narrower purpose: deciding which presented references satisfy which interaction contexts.

## 5.9 What can be left out?

A project can use only atoms and conjunctions of named predicates. Union, global complement, and bottom are not mandatory. The non-negotiable insight is that a type means a membership condition, not merely a node in a class tree.

## Exercises

1. **Calculation.** In the finite model above, compute `Project ∪ Inspectable`, `Inspectable \ Project`, and `¬Archived`.
2. **Proof.** Prove idempotence of union by elementwise extensional reasoning.
3. **Proof.** Prove the absorption law \(A\cap(A\cup B)=A\).
4. **Countermodel.** Extend the finite model so that `Project \ Archived` and `Project ∩ Inspectable` are no longer equal.
5. **Design.** Give three useful union types and three useful intersections for the workbench.
6. **Critical.** Why is an arbitrary JavaScript predicate not automatically a satisfactory persistent type definition?
7. **Implementation.** Represent `top`, `bottom`, `union`, `intersection`, and `difference` as immutable TypeScript data.

---

# 6. Relations, equality, identity, and quotients

## Learning objectives

After this chapter you should be able to:

1. define binary relations, functions, and partial functions;
2. state and test the laws of an equivalence relation;
3. model semantic object identity independently of representation;
4. explain quotient sets and their relevance to normalized UI state;
5. identify where identity invariance is and is not required.

## 6.1 Binary relations

A binary relation from set \(A\) to set \(B\) is a subset of their Cartesian product:

\[
R\subseteq A\times B.
\]

We write \(aRb\) when \((a,b)\in R\).

Examples in PBUI include:

- subtype: \(\tau\leq\sigma\);
- identity: \(r_1\approx r_2\);
- direct translation: \(r\xrightarrow{t}r'\);
- view binding: \(v\sim_b w\);
- action preference: \(m_1\succ m_2\).

The properties appropriate to one relation are not automatically appropriate to another. Identity should be symmetric; translation usually is not. Subtyping should be transitive; direct translation need not be.

## 6.2 Functions and partial functions

A total function \(f:A\to B\) assigns exactly one \(b\in B\) to every \(a\in A\).

A partial function is written:

\[
f:A\rightharpoonup B.
\]

It may be undefined for some inputs. A project lookup is naturally partial:

\[
\operatorname{lookupProject}:\textsf{ProjectId}\rightharpoonup\textsf{Project}.
\]

In TypeScript:

```ts
function lookupProject(
  id: string,
  environment: Environment,
): Project | undefined;
```

An asynchronous partial function can be represented with a result type:

```ts
type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

function fetchProject(
  id: string,
  signal: AbortSignal,
): Promise<Result<Project, LookupError>>;
```

Treating failure explicitly becomes important for translators.

## 6.3 Equivalence relations

A relation \(\approx\) on \(A\) is an **equivalence relation** when it is:

1. reflexive: \(a\approx a\);
2. symmetric: if \(a\approx b\), then \(b\approx a\);
3. transitive: if \(a\approx b\) and \(b\approx c\), then \(a\approx c\).

Semantic object identity should satisfy these laws within one coherent environment snapshot.

### Why reflexivity matters

If a reference is not identical to itself, selecting an occurrence and later comparing it to the stored selection can fail immediately.

### Why symmetry matters

If a project card is “the same as” an ID token but the ID token is not “the same as” the card, menus and highlighting depend on comparison order.

### Why transitivity matters

If card \(a\) matches token \(b\), and token \(b\) matches inspector row \(c\), then card \(a\) must match row \(c\). Otherwise a linked selection can split into inconsistent clusters.

## 6.4 Identity keys

A practical identity protocol maps references to keys:

\[
\operatorname{id}_e:\Omega\rightharpoonup K,
\]

where a key contains both a namespace and a key value:

```ts
interface SemanticIdentity {
  readonly namespace: string;
  readonly key: string;
}
```

Define:

\[
r_1\approx_e r_2
\quad\text{iff}\quad
\operatorname{id}_e(r_1)=\operatorname{id}_e(r_2),
\]

when both identities are defined. For references lacking semantic identity, an implementation may use a fallback relation based on primitive value or object reference.

### Proposition 6.1 — Key equality induces an equivalence relation

Assume `id` is deterministic over one environment snapshot and total on subset \(D\subseteq\Omega\). Define \(r\approx s\) iff \(\operatorname{id}(r)=\operatorname{id}(s)\). Then \(\approx\) is an equivalence relation on \(D\).

#### Proof

- Reflexivity follows because every key equals itself.
- Symmetry follows from symmetry of equality.
- Transitivity follows from transitivity of equality. ∎

The proof is simple; the engineering assumptions are not. If identity depends on mutable display labels or nondeterministic serialization, the induced relation may appear unstable over time.

## 6.5 Identity domains

The namespace prevents accidental cross-domain equality:

```ts
{ namespace: "project", key: "7" }
{ namespace: "user", key: "7" }
```

Different presentation types may intentionally share a domain:

```ts
project.identity(project) =>
  ({ namespace: "project", key: project.id })

projectId.identity(id) =>
  ({ namespace: "project", key: id })
```

Thus:

\[
\langle\textsf{project},p_7\rangle
\approx
\langle\textsf{project-id},\texttt{"7"}\rangle.
\]

They are the same domain object but not the same presentation role or representation.

## 6.6 Quotient sets

Given equivalence relation \(\approx\) on \(A\), the equivalence class of \(a\) is:

\[
[a]=\{b\in A\mid b\approx a\}.
\]

The **quotient set** is:

\[
A/{\approx}=\{[a]\mid a\in A\}.
\]

Informally, quotienting treats equivalent representations as one abstract object.

For PBUI:

```text
Ω / semantic-identity
```

is the set of domain objects denoted by presentation references. A normalized client store often implements a concrete quotient representation: all project occurrences point through the key `project:7` to one normalized entity node.

Quotienting is a conceptual tool, not a requirement that the implementation allocate equivalence-class objects.

## 6.7 Congruence and identity-sensitive operations

An operation \(f\) respects identity when:

\[
r\approx s \Rightarrow f(r)=f(s),
\]

or, when the result also has identity,

\[
r\approx s \Rightarrow f(r)\approx f(s).
\]

Such an operation is compatible with the quotient.

Should type membership respect semantic identity? Not always.

The same project can be presented as a `project` object and as a `projectId` token. The former may belong directly to `Project`; the latter may require translation. Therefore:

\[
r\approx s
\centernot\Rightarrow
(r\in\llbracket\tau\rrbracket \Leftrightarrow s\in\llbracket\tau\rrbracket)
\]

for every presentation type \(\tau\).

This is not a defect. Presentation types classify semantic roles and representations, while identity classifies denotation.

An **identity-invariant capability**, however, may deliberately require congruence. For example, if `Archived` is a property of the underlying project, then every identity-preserving representation should agree once resolved against the same snapshot.

## 6.8 Occurrence identity and React identity

Let:

- \(r\) be a semantic reference;
- \(o\) be a mounted occurrence;
- \(k\) be a React key.

Several occurrences can carry one reference:

\[
\operatorname{reference}(o_1)=\operatorname{reference}(o_2)=r.
\]

One occurrence can be remounted with a different occurrence identity while retaining semantic identity. A React key is meaningful only in the local reconciliation context of sibling elements. It should not be exported as a domain identity.

## 6.9 Stable identity and time

Let environments be indexed by time \(e_t\). Identity stability means:

\[
\operatorname{id}_{e_t}(r)=\operatorname{id}_{e_{t+1}}(r')
\]

when \(r\) and \(r'\) are successive representations of the same persistent object.

Avoid keys based on:

- mutable titles;
- array positions;
- JSON serialization of the whole object;
- display formatting;
- memory addresses across persistence boundaries.

Prefer application-assigned IDs or explicit composite keys.

## 6.10 What can be left out?

If every presentation carries a normalized entity key already, a separate descriptor identity method may be redundant. Still document that the key defines semantic identity and test its laws.

Cross-type identity can also be omitted until alternate representations arise. Fallback object identity is safe but less powerful; unsafe structural equality should not be the default.

## Exercises

1. **Proof.** Prove that equality of a deterministic composite key `(namespace, key)` induces an equivalence relation.
2. **Counterexample.** Define a non-transitive “similarity” relation on projects and show why it is unsuitable as identity.
3. **Design.** Choose semantic identities for fields, documents, rows, chart marks, tiles, and view placements. Identify any cases without a stable key.
4. **Quotients.** List three presentation references that could belong to one equivalence class.
5. **Critical.** Give a capability that should be identity-invariant and a presentation type that should not be.
6. **Implementation.** Write property-based tests for reflexivity, symmetry, and transitivity over generated references.

---

# 7. Preorders, partial orders, lattices, and closure

## Learning objectives

After this chapter you should be able to:

1. define preorders and partial orders;
2. explain why semantic subtyping is initially a preorder;
3. obtain a partial order by quotienting semantic equivalence;
4. identify joins, meets, top, and bottom in a type lattice;
5. use transitive closure to implement nominal subtype declarations;
6. recognize monotone functions and fixed-point requirements.

## 7.1 Preorders and partial orders

A **preorder** \((P,\leq)\) is a set with a relation that is:

- reflexive: \(x\leq x\);
- transitive: \(x\leq y\land y\leq z\Rightarrow x\leq z\).

A **partial order** additionally requires antisymmetry:

\[
x\leq y\land y\leq x\Rightarrow x=y.
\]

Subtype syntax naturally forms a preorder because distinct expressions can denote the same type:

\[
\tau \leq \tau\land\top,
\qquad
\tau\land\top \leq \tau,
\]

but the syntax trees are not identical.

If we quotient expressions by semantic equivalence \(\equiv\), the induced subtype relation becomes antisymmetric:

\[
[\tau]\leq[\sigma]
\quad\text{iff}\quad
\tau\leq\sigma.
\]

## 7.2 Inclusion as an order

Set inclusion is defined by:

\[
A\subseteq B
\quad\text{iff}\quad
\forall x.\;x\in A\Rightarrow x\in B.
\]

Inclusion is a partial order on \(\mathcal P(\Omega)\):

- reflexive because membership in \(A\) implies membership in \(A\);
- transitive because implications compose;
- antisymmetric by set extensionality.

Semantic subtyping will use this order.

## 7.3 Hasse diagrams and nominal graphs

A finite partial order can be drawn as a Hasse diagram, omitting reflexive and transitively implied edges:

```text
             Entity
             /    \
      Document   User
        /   \
  Project  Dataset
```

An edge `Project -> Document` can be read as `Project ≤ Document`. Multiple inheritance yields a directed acyclic graph rather than a tree.

A nominal registry typically stores only declared edges and computes reflexive-transitive closure.

Let \(D\subseteq A\times A\) be the declared immediate-supertype relation. Its reflexive-transitive closure \(D^*\) is the smallest relation containing \(D\) that is reflexive and transitive.

A worklist algorithm computes reachability. For a small type vocabulary, a depth-first search with memoization is sufficient. For repeated queries, precompute ancestor bitsets.

## 7.4 Cycles

A declared cycle:

```text
Project < Entity
Entity  < Project
```

may mean either:

1. the two names are intended to be semantically equivalent; or
2. the declarations are erroneous.

A nominal API should usually reject cycles because users expect distinct names to form a DAG. Semantic equivalence can be represented explicitly by aliases or normalized names.

Rejecting cycles also prevents confusing specificity order in action dispatch.

## 7.5 Upper and lower bounds

Given \(a,b\in P\), an upper bound \(u\) satisfies:

\[
a\leq u \land b\leq u.
\]

A **least upper bound**, or **join**, is an upper bound no larger than any other upper bound. It is written \(a\vee b\).

A lower bound \(l\) satisfies:

\[
l\leq a \land l\leq b.
\]

A **greatest lower bound**, or **meet**, is written \(a\wedge b\).

For sets ordered by inclusion:

\[
A\vee B=A\cup B,
\qquad
A\wedge B=A\cap B.
\]

This gives the logical reading of union and intersection types.

## 7.6 Lattices and complete lattices

A **lattice** is a partial order in which every pair has a join and meet. A **bounded lattice** has top and bottom elements. A **complete lattice** has joins and meets for every subset, including infinite subsets.

The powerset lattice \((\mathcal P(\Omega),\subseteq)\) is complete:

\[
\bigvee \mathcal A = \bigcup\mathcal A,
\qquad
\bigwedge \mathcal A = \bigcap\mathcal A.
\]

This mathematical completeness does not mean an implementation can decide all equalities or represent every subset. The semantic domain can be complete while the type language denotes only a fragment.

Order and lattice theory provide the right vocabulary for type approximation, joins after control-flow branches, meets after successful tests, and fixed-point definitions [DaveyPriestley2002].

## 7.7 Monotone functions

A function \(f:P\to Q\) between ordered sets is **monotone** when:

\[
x\leq y\Rightarrow f(x)\leq f(y).
\]

Many type constructors are monotone:

\[
A\subseteq B
\Rightarrow
A\cap C\subseteq B\cap C,
\]

\[
A\subseteq B
\Rightarrow
A\cup C\subseteq B\cup C.
\]

Difference is monotone in its first argument and antitone in its second:

\[
A\subseteq B\Rightarrow A\setminus C\subseteq B\setminus C,
\]

\[
C\subseteq D\Rightarrow A\setminus D\subseteq A\setminus C.
\]

Variance language in type systems generalizes these observations.

## 7.8 Closure operators

A **closure operator** \(c:\mathcal P(A)\to\mathcal P(A)\) is:

1. extensive: \(X\subseteq c(X)\);
2. monotone: \(X\subseteq Y\Rightarrow c(X)\subseteq c(Y)\);
3. idempotent: \(c(c(X))=c(X)\).

The ancestor closure of a set of atomic types is a closure operator:

\[
\operatorname{ancestors}(X)
= X\cup\{b\mid \exists a\in X.\;aD^*b\}.
\]

This gives an efficient fact representation. If a reference is directly tagged `Project`, its closed nominal fact set includes `Project`, `Document`, and `Entity`.

### Proposition 7.1 — Ancestor closure is a closure operator

Assume \(D^*\) is reflexive and transitive.

- Extensiveness follows from reflexivity.
- Monotonicity follows because every witness from \(X\) is also in \(Y\) when \(X\subseteq Y\).
- Idempotence follows from transitivity: ancestors of ancestors are already ancestors. ∎

This proposition justifies caching a closed atom bitset.

## 7.9 Recursive types and fixed points

Recursive type definitions such as:

```text
Tree = Leaf ∨ Node(Tree, Tree)
```

are interpreted using fixed points of monotone operators. If \(F\) maps candidate sets to new candidate sets, a fixed point satisfies:

\[
F(X)=X.
\]

The Knaster–Tarski theorem guarantees least and greatest fixed points for monotone functions on complete lattices. A full semantic subtype system for recursive data relies on such machinery.

PBUI can initially omit recursive type expressions because presentation references already carry ordinary application data whose structure is checked elsewhere. Recursive runtime UI types should be added only for concrete use cases such as recursive command argument schemas.

## 7.10 What can be left out?

A practical implementation needs only:

- a nominal DAG;
- cached ancestor closure;
- union and intersection expressions;
- semantic subtype tests for the supported fragment.

It does not need a generic lattice library, infinite joins, or recursive fixed points. Those concepts explain the design and show where extensions would fit.

## Exercises

1. **Proof.** Prove that set inclusion is reflexive and transitive.
2. **Proof.** Show that syntactic type expressions under semantic subtyping form a preorder.
3. **Proof.** Show that quotienting by mutual subtyping yields a partial order.
4. **Calculation.** Draw a Hasse diagram for a domain with `Entity`, `Document`, `Project`, `Dataset`, `Person`, and `User`.
5. **Algorithm.** Implement cycle detection for nominal subtype declarations.
6. **Algorithm.** Compare per-query depth-first search with precomputed ancestor bitsets. Under what workloads does each win?
7. **Advanced proof.** Prove antitonicity of set difference in its second argument.
8. **Research.** Read an introductory chapter on lattices and identify one additional application to program analysis.

---

# 8. Logic, evidence, and judgments

## Learning objectives

After this chapter you should be able to:

1. read propositions as specifications of evidence;
2. distinguish truth, decidability, and proof objects;
3. read and construct typing judgments and inference rules;
4. explain why a match result can carry evidence rather than only `true`;
5. distinguish constructive failure from classical negation.

## 8.1 Propositions and connectives

A proposition is a statement capable of being true or false. We use:

- \(P\land Q\): both hold;
- \(P\lor Q\): at least one holds;
- \(P\Rightarrow Q\): evidence for \(P\) can be transformed into evidence for \(Q\);
- \(\neg P\): \(P\Rightarrow\bot\);
- \(\forall x.P(x)\): every \(x\) satisfies \(P\);
- \(\exists x.P(x)\): there is an \(x\) satisfying \(P\).

Under the propositions-as-types correspondence, proofs are values inhabiting proposition-like types [Wadler2015; TheLittleTyper; HoTTBook]. We do not need dependent types in TypeScript to benefit from the operational idea: a successful check can return structured evidence explaining *why* it succeeded.

## 8.2 Booleans versus evidence

A Boolean matcher has type:

```ts
(reference: Reference) => boolean
```

It discards the reason for success. An evidence-producing matcher has type:

```ts
type MatchResult<R> =
  | { readonly ok: true; readonly match: Match<R> }
  | { readonly ok: false; readonly failure: MatchFailure };
```

Evidence can record:

- which union branch matched;
- evidence for every intersection member;
- the refinement predicate and dependency fingerprint;
- subtype declarations used;
- translation steps;
- registry and environment versions;
- specificity information for dispatch.

This supports explanation, auditing, cache validation, and safer commitment.

## 8.3 Judgments

A **judgment** is a formal assertion made under explicit assumptions. We write:

\[
R;e\vdash r:\tau\triangleright\pi
\]

and read:

> Under registry \(R\) and environment \(e\), reference \(r\) has presentation type \(\tau\), with evidence \(\pi\).

A subtype judgment is:

\[
R\vdash \tau\leq\sigma.
\]

A translation judgment is:

\[
R;e\vdash r\xRightarrow{t}r'.
\]

An action applicability judgment is:

\[
R;e;c\vdash m\;\mathsf{applicable}\;\vec r.
\]

Explicit contexts prevent hidden dependencies.

## 8.4 Inference rules

An inference rule has premises above a line and a conclusion below it.

### Top

\[
\frac{ }{R;e\vdash r:\top\triangleright\mathsf{top}}
\]

Every reference belongs to top.

### Atom

\[
\frac{\operatorname{atomOf}(r)=a}
     {R;e\vdash r:a\triangleright\mathsf{atom}(a)}
\]

### Subsumption

\[
\frac{R;e\vdash r:\tau\triangleright\pi
\qquad R\vdash\tau\leq\sigma}
{R;e\vdash r:\sigma\triangleright\mathsf{subsume}(\pi,\tau\leq\sigma)}
\]

### Intersection introduction

\[
\frac{R;e\vdash r:\tau\triangleright\pi_1
\qquad R;e\vdash r:\sigma\triangleright\pi_2}
{R;e\vdash r:\tau\land\sigma\triangleright\mathsf{and}(\pi_1,\pi_2)}
\]

### Union introduction, left

\[
\frac{R;e\vdash r:\tau\triangleright\pi}
{R;e\vdash r:\tau\lor\sigma\triangleright\mathsf{orL}(\pi)}
\]

There is a symmetric right rule.

### Refinement

\[
\frac{R;e\vdash r:\tau\triangleright\pi
\qquad p(r,e,\theta)=\mathsf{true}}
{R;e\vdash r:\operatorname{refine}(\tau,p,\theta)
\triangleright\mathsf{refine}(\pi,p,\theta,d)}
\]

Here \(d\) is a dependency fingerprint.

These rules can directly guide an evaluator.

## 8.5 Proof relevance

Two proofs of the same proposition may carry different operational information. A project ID can satisfy `Project` through one of several translators. The accepted semantic type may be the same while the path differs in cost, authority, or latency.

Therefore match evidence is **proof-relevant**:

```ts
interface TranslationEvidence {
  readonly translatorId: string;
  readonly source: PresentationReference;
  readonly target: PresentationReference;
  readonly cost: number;
}
```

A purely extensional type system may identify all proofs of membership. A UI runtime should often retain selected proof details for explanation and dispatch.

## 8.6 Decidability

A proposition is decidable when an algorithm can return either evidence for it or evidence for its negation.

For finite nominal graphs, subtype reachability is decidable. For registered executable refinements, membership is decidable only under assumptions:

- the predicate terminates;
- it returns a Boolean or result;
- required data is available;
- asynchronous cancellation is handled.

An arbitrary JavaScript lambda can loop forever or throw. The registry must define an operational contract even when the host language cannot enforce it.

```ts
interface RefinementContract {
  readonly purity: "structural" | "pure" | "environment" | "volatile";
  readonly cost: "constant" | "small" | "unbounded";
  readonly failure: "false" | "diagnostic";
}
```

## 8.7 Negation and failure

Failure to prove \(P\) is not always proof of \(\neg P\).

A project lookup may fail because:

- the project does not exist;
- data has not loaded;
- access is denied;
- the network failed;
- the lookup was cancelled.

Only the first may justify semantic non-membership. Therefore a matcher can distinguish:

```ts
type MatchFailure =
  | { kind: "not-member"; reason: Evidence }
  | { kind: "unknown"; reason: Diagnostic }
  | { kind: "error"; error: unknown };
```

A two-valued synchronous core is simpler. An advanced system may use three-valued applicability:

\[
\{\mathsf{yes},\mathsf{no},\mathsf{unknown}\}.
\]

The UI must then decide how unknown occurrences appear and whether selection can trigger loading.

## 8.8 Evidence erasure

The public API can erase evidence when the caller only needs a value:

```ts
const selected = await pbui.accept({ type: ActiveProject });
```

An advanced API retains it:

```ts
const result = await pbui.acceptWithEvidence({
  type: ActiveProject,
});
```

Evidence should be optional in storage cost but foundational in design. A Boolean implementation can be viewed as an evidence evaluator followed by erasure.

## 8.9 What can be left out?

A minimal system can return only `boolean` and log a short reason in development mode. Full proof objects are valuable when:

- translators compete;
- authorization matters;
- explanations are user-visible;
- cached predicates need validation;
- action dispatch has ambiguity;
- tests need to assert which rule applied.

## Exercises

1. **Derivation.** Construct an evidence tree showing that an active inspectable project belongs to `Project ∧ Inspectable`.
2. **Logic.** Explain the evidence required for a union and for an intersection.
3. **Critical.** Give an example where lookup failure is `unknown`, not evidence of non-membership.
4. **Implementation.** Define TypeScript unions for atomic, subtype, union, intersection, and refinement evidence.
5. **Proof.** Derive `r : Entity` from `r : Project` and `Project ≤ Entity` using subsumption.
6. **Design.** Decide which evidence should survive in production and which can be development-only.
7. **Advanced.** Model applicability with a three-valued logic and define truth tables for conjunction and disjunction.

---

# 9. Semantics and proof methods

## Learning objectives

After this chapter you should be able to:

1. distinguish syntax, denotational semantics, and operational semantics;
2. state soundness and completeness properties;
3. use induction, inversion, and countermodels;
4. translate mathematical laws into executable property tests;
5. understand the status and limits of proofs in this book.

## 9.1 Syntax and semantics

A language has **syntax**: the expressions we can write. It has **semantics**: what those expressions mean or how they execute.

For presentation types:

```text
syntax
  Project ∧ (Inspectable ∨ Editable)

semantic denotation
  a subset of semantic references

operational evaluator
  a program that attempts to construct evidence of membership
```

Keeping these levels separate permits us to ask whether the evaluator correctly implements the denotation.

## 9.2 Denotational semantics

A denotational semantics maps syntax into mathematical objects. Our type denotation is:

\[
\llbracket-\rrbracket^R_e:\mathsf{TypeExpr}\to\mathcal P(\Omega_R).
\]

Compositionality means the denotation of a compound expression is determined by the denotations of its parts:

\[
\llbracket\tau\land\sigma\rrbracket_e
=\llbracket\tau\rrbracket_e\cap\llbracket\sigma\rrbracket_e.
\]

Denotational semantics gives a concise specification against which implementations can be checked. Standard references include Winskel's *The Formal Semantics of Programming Languages*, Pierce's *Types and Programming Languages*, and Harper's *Practical Foundations for Programming Languages* [Winskel1993; Pierce2002; Harper2016].

## 9.3 Operational semantics

An operational semantics describes evaluation steps or judgments. A big-step relation might be:

\[
R;e\vdash\operatorname{match}(r,\tau)\Downarrow q,
\]

where \(q\) is success evidence or failure.

A small-step semantics decomposes computation:

\[
\langle r,\tau,e,s\rangle\to\langle r,\tau',e,s'\rangle.
\]

For simple synchronous matching, big-step rules are readable. For input contexts, cancellation, asynchronous translators, and provider lifecycle, a transition system is more informative.

## 9.4 Soundness

A matcher is sound when success implies semantic membership.

### Theorem schema — Matcher soundness

If

\[
R;e\vdash\operatorname{match}(r,\tau)\Downarrow\mathsf{success}(\pi),
\]

then

\[
r\in\llbracket\tau\rrbracket^R_e.
\]

The proof proceeds by induction on the matching derivation:

- atom success follows from the atom interpretation;
- intersection success has two induction hypotheses, giving membership in both sets;
- union success has one branch hypothesis;
- difference success establishes base membership and excluded non-membership;
- refinement success establishes base membership and a true predicate;
- subtype subsumption follows from inclusion.

For executable predicates, the theorem relies on the registry contract that the predicate correctly implements its declared proposition.

## 9.5 Completeness

A matcher is complete when semantic membership implies that the evaluator can succeed:

\[
r\in\llbracket\tau\rrbracket^R_e
\Rightarrow
\exists\pi.\;R;e\vdash\operatorname{match}(r,\tau)\Downarrow\mathsf{success}(\pi).
\]

Completeness is harder and may be intentionally weakened.

Examples:

- a bounded translator search may omit a valid long path;
- asynchronous data may be unavailable;
- an opaque predicate may throw;
- an implementation may use a conservative approximation;
- open-world plugins may not yet be loaded.

A practical matcher can be sound but incomplete. The UI then fails to highlight some valid presentations but does not accept invalid ones. For destructive actions, that is usually the safer trade.

## 9.6 Subtype soundness

A subtype algorithm is sound when:

\[
\operatorname{subtype}_R(\tau,\sigma)=\mathsf{true}
\Rightarrow
\forall e.\;\llbracket\tau\rrbracket_e\subseteq\llbracket\sigma\rrbracket_e.
\]

It is complete for a fragment when every semantic inclusion in that fragment is recognized.

A nominal graph algorithm is sound relative to declared-edge assumptions but not complete for all set-theoretic inclusions. It may not infer:

\[
A\land B\leq A,
\qquad
A\leq A\lor B,
\]

unless the expression algorithm includes these rules.

## 9.7 Induction

Induction is the principal proof method for syntax trees and derivations.

### Structural induction on type expressions

To prove property \(P(\tau)\) for every type expression:

1. prove it for atoms, top, and bottom;
2. assume it for immediate subexpressions;
3. prove it for union, intersection, difference, and refinement.

### Induction on derivations

To prove a property of every successful matching judgment, consider the last inference rule used and apply induction hypotheses to its premises.

This often aligns directly with a recursive TypeScript function.

## 9.8 Inversion

An **inversion lemma** extracts facts from the shape of a derivation.

If:

\[
R;e\vdash r:\tau\land\sigma\triangleright\pi,
\]

and the only introduction rule for intersection requires both premises, then inversion tells us:

\[
R;e\vdash r:\tau
\quad\text{and}\quad
R;e\vdash r:\sigma.
\]

In code, discriminated evidence makes inversion executable:

```ts
if (evidence.kind === "intersection") {
  evidence.left;
  evidence.right;
}
```

## 9.9 Countermodels

To disprove a universal claim, construct one model where it fails.

Claim:

```text
Every identity-equivalent reference has exactly the same presentation types.
```

Countermodel:

```text
<project> p7       ≈ <project-id> "p7"
<project> p7       ∈ Project
<project-id> "p7" ∉ Project directly
```

Therefore identity does not imply role-membership invariance.

Countermodels are essential in API design. They reveal which law belongs to which relation.

## 9.10 Preservation and progress analogues

Programming-language type safety is often expressed through progress and preservation.

For PBUI, useful analogues are:

### Acceptance preservation

If an occurrence is accepted with evidence under snapshot \((R,e)\), and the evidence remains valid at commitment, the returned reference satisfies the requested type.

### Input-context progress

An active context is in one of these states:

- it can accept at least one available occurrence;
- it is waiting for future output or data;
- it can be aborted;
- it completes with a result.

Unlike a closed programming-language term, a UI can legitimately wait for user input. “Progress” means the state machine has defined transitions, not that it computes autonomously.

### Link preservation

If all views in one binding class agree on role \(q\) before a `setSubject` transition, they still agree afterward.

We prove these in later chapters.

## 9.11 From laws to tests

A mathematical law can become a property-based test.

Commutativity:

```ts
fc.assert(fc.property(typeExprArb, typeExprArb, (a, b) => {
  return equivalent(and(a, b), and(b, a), finiteModel);
}));
```

Identity transitivity:

```ts
if (sameObject(a, b) && sameObject(b, c)) {
  expect(sameObject(a, c)).toBe(true);
}
```

Soundness over a finite generated model:

```ts
if (matcher.match(reference, type).ok) {
  expect(denotation(type, model).has(reference)).toBe(true);
}
```

Testing explores instances; proof establishes a universal result under assumptions. Neither replaces the other. Tests catch implementation defects and incorrect assumptions; proofs expose the exact assumptions and structure of correctness.

Software Foundations demonstrates how semantics and proofs can be mechanized in Coq, while Programming Language Foundations in Agda develops similar material in Agda [SoftwareFoundations; PLFA]. Appendix C outlines a mechanization path for this calculus.

## 9.12 Trusted computing base

A proof about the abstract evaluator depends on trusted components:

- JavaScript equality and map behavior;
- registry well-formedness checks;
- descriptor identity methods;
- refinement implementations;
- environment snapshot/version discipline;
- translator metadata and bodies;
- React event lifecycle;
- persistence decoding.

A theorem is only as applicable as its assumptions. The purpose of proof-oriented design is not to claim absolute certainty, but to reduce vague confidence to inspectable obligations.

## 9.13 What can be left out?

A team need not mechanize proofs. It can still benefit from:

- a denotational specification;
- named laws;
- proof sketches for central algorithms;
- property tests;
- explicit trusted assumptions;
- counterexamples for rejected designs.

## Exercises

1. **Proof.** Give a structural-induction proof that normalization preserving each constructor's denotation preserves the whole expression's denotation.
2. **Proof.** Sketch matcher soundness for union and intersection.
3. **Countermodel.** Disprove the claim that a shortest translation path is always semantically preferable.
4. **Testing.** Turn the absorption law into a property test over a finite reference universe.
5. **Analysis.** Identify the trusted computing base for a selector predicate that consults a Redux store.
6. **Research.** Compare big-step and small-step semantics. Which better describes an asynchronous translator and why?
7. **Critical.** Describe a useful system that is deliberately sound but incomplete.

---
# Part III — A presentation type calculus

# 10. Syntax and semantic domains

## Learning objectives

After this chapter you should be able to:

1. read the complete core grammar of the presentation type calculus;
2. identify the registry and environment components required by its semantics;
3. distinguish well-formed expressions from arbitrary data;
4. calculate the denotation of a compound presentation type;
5. choose a smaller grammar when the full calculus is unnecessary.

## 10.1 Design goals

The calculus should be expressive enough for:

```text
Project
Project ∨ Workspace
Project ∧ Inspectable
Project \ Archived
FieldOf(document-7)
Project ∧ OwnedBy(user-3) \ Archived
```

It should also remain executable in a JavaScript runtime. We therefore separate a small algebraic syntax from registered functions.

## 10.2 Semantic references

Let \(A\) be a finite or countable set of atomic presentation names. Each atom \(a\in A\) has a representation set \(V_a\).

The universe of tagged references is the disjoint union:

\[
\Omega_R=\sum_{a\in A}V_a.
\]

An element is a pair:

\[
\langle a,v\rangle \quad\text{where}\quad v\in V_a.
\]

The dependent sum notation emphasizes that the valid representation depends on the tag.

In TypeScript, the `Values` map approximates this family:

```ts
interface Values {
  project: Project;
  projectId: string;
  document: Document;
  field: Field;
}
```

```ts
type Ref<V extends object> = {
  [K in keyof V & string]: Readonly<{
    type: K;
    value: V[K];
  }>
}[keyof V & string];
```

## 10.3 Registry structure

We model a registry as:

\[
R=\langle A,D,C,P,I,T,M\rangle,
\]

where:

- \(A\): atomic presentation declarations and representation contracts;
- \(D\subseteq A\times A\): nominal immediate-subtype declarations;
- \(C\): capability declarations and implementations;
- \(P\): named refinement predicates and parameter schemas;
- \(I\): semantic identity functions;
- \(T\): translators;
- \(M\): action methods and preference declarations.

The core type semantics needs only \(A,D,C,P\). Identity, translation, and methods are deliberately separate extensions.

An environment \(e\in E\) is an immutable logical snapshot containing dynamic application facts needed by refinements and translators. The actual JavaScript object may use persistent references or store selectors, but it must expose version information sufficient for cache validity.

## 10.4 Core syntax

Let \(a\) range over atomic type names, \(c\) over capability names, \(p\) over refinement names, and \(\theta\) over serializable arguments.

\[
\begin{aligned}
\tau ::=\;& \top
\mid \bot
\mid a
\mid \operatorname{cap}(c)\\
&\mid \tau\lor\tau
\mid \tau\land\tau
\mid \tau\setminus\tau\\
&\mid \operatorname{refine}(p,\theta,\tau).
\end{aligned}
\]

Parameterized presentation types are syntactic sugar:

\[
C(\theta)\triangleq\operatorname{refine}(p_C,\theta,\operatorname{base}(C)).
\]

For example:

\[
\operatorname{FieldOf}(d)
\triangleq
\operatorname{refine}(\textsf{field-of},d,\textsf{Field}).
\]

## 10.5 TypeScript syntax values

```ts
type TypeExpr =
  | Readonly<{ kind: "top" }>
  | Readonly<{ kind: "bottom" }>
  | Readonly<{ kind: "atom"; id: string }>
  | Readonly<{ kind: "capability"; id: string }>
  | Readonly<{
      kind: "union";
      members: readonly TypeExpr[];
    }>
  | Readonly<{
      kind: "intersection";
      members: readonly TypeExpr[];
    }>
  | Readonly<{
      kind: "difference";
      base: TypeExpr;
      excluded: TypeExpr;
    }>
  | Readonly<{
      kind: "refinement";
      id: string;
      base: TypeExpr;
      args: unknown;
    }>;
```

Smart constructors should flatten associative nodes, remove identities, sort canonical members, and reject malformed empty cases:

```ts
and(Project, top(), and(Inspectable, Project))
```

can normalize to:

```text
Project ∧ Inspectable
```

Normalization is an optimization and explanation aid. The denotational semantics remains authoritative.

## 10.6 Well-formedness

A judgment

\[
R\vdash\tau\;\mathsf{wf}
\]

states that \(\tau\) is well formed in registry \(R\).

Representative rules are:

\[
\frac{a\in A}{R\vdash a\;\mathsf{wf}}
\]

\[
\frac{c\in C}{R\vdash\operatorname{cap}(c)\;\mathsf{wf}}
\]

\[
\frac{R\vdash\tau\;\mathsf{wf}\qquad R\vdash\sigma\;\mathsf{wf}}
{R\vdash\tau\land\sigma\;\mathsf{wf}}
\]

\[
\frac{p\in P\qquad R\vdash\tau\;\mathsf{wf}\qquad
\operatorname{argsValid}_p(\theta)}
{R\vdash\operatorname{refine}(p,\theta,\tau)\;\mathsf{wf}}.
\]

Registry construction should validate:

- all names are unique;
- declared supertypes exist;
- nominal cycles are rejected or explicitly aliased;
- refinement argument decoders are available;
- capability implementations refer to known atoms;
- expression IDs are deterministic when persistence is required.

## 10.7 Atomic facts

Each reference has a direct atom:

\[
\operatorname{tag}(\langle a,v\rangle)=a.
\]

Nominal closure produces atomic supertypes:

\[
\operatorname{atoms}_R(r)
=\operatorname{ancestors}_R(\{\operatorname{tag}(r)\}).
\]

Capability facts may be static declarations or dynamic predicates:

\[
\operatorname{caps}_{R,e}(r)
=\{c\mid \operatorname{implements}_{R,e}(r,c)\}.
\]

Static capabilities can be merged into a bitset. Dynamic capabilities are refinements in operational disguise and should declare dependencies.

## 10.8 Denotational semantics

The core denotation is:

\[
\llbracket\top\rrbracket^R_e=\Omega_R,
\]

\[
\llbracket\bot\rrbracket^R_e=\varnothing,
\]

\[
\llbracket a\rrbracket^R_e
=\{r\mid a\in\operatorname{atoms}_R(r)\},
\]

\[
\llbracket\operatorname{cap}(c)\rrbracket^R_e
=\{r\mid c\in\operatorname{caps}_{R,e}(r)\},
\]

\[
\llbracket\tau\lor\sigma\rrbracket^R_e
=\llbracket\tau\rrbracket^R_e\cup\llbracket\sigma\rrbracket^R_e,
\]

\[
\llbracket\tau\land\sigma\rrbracket^R_e
=\llbracket\tau\rrbracket^R_e\cap\llbracket\sigma\rrbracket^R_e,
\]

\[
\llbracket\tau\setminus\sigma\rrbracket^R_e
=\llbracket\tau\rrbracket^R_e\setminus\llbracket\sigma\rrbracket^R_e,
\]

\[
\llbracket\operatorname{refine}(p,\theta,\tau)\rrbracket^R_e
=\{r\in\llbracket\tau\rrbracket^R_e
\mid \operatorname{test}_{R}(p,r,\theta,e)\}.
\]

## 10.9 Example calculation

Let:

\[
\tau=
(\textsf{Project}\land\operatorname{cap}(\textsf{Inspectable}))
\setminus
\operatorname{cap}(\textsf{Archived}).
\]

Then:

\[
\begin{aligned}
\llbracket\tau\rrbracket_e
=\{r\mid &\textsf{Project}\in\operatorname{atoms}(r)\\
&\land \textsf{Inspectable}\in\operatorname{caps}_e(r)\\
&\land \textsf{Archived}\notin\operatorname{caps}_e(r)\}.
\end{aligned}
\]

This is exactly the intended reading: inspectable projects that are not archived.

## 10.10 Environment-local and stable meaning

Some types have environment-independent denotations:

```text
Project
Project ∨ Workspace
```

Others vary:

```text
Visible
OwnedByCurrentUser(Project)
Writable(Document)
```

We call a type \(\tau\) **stable** over environment relation \(\leadsto\) when:

\[
e\leadsto e'\Rightarrow
\llbracket\tau\rrbracket_e=\llbracket\tau\rrbracket_{e'}.
\]

Stable types admit stronger caching and persistence. The registry can conservatively classify expression stability from its parts.

## 10.11 What can be left out?

The smallest useful grammar is:

\[
\tau::=a\mid\tau\lor\tau\mid\operatorname{refine}(p,\theta,\tau).
\]

Intersections can be represented by multiple required selectors; difference can be a negative predicate; capabilities can be ordinary atoms. The larger syntax becomes worthwhile when explanation, normalization, subtype reasoning, and method specificity need explicit structure.

## Exercises

1. **Syntax.** Encode `active project owned by user 7 and inspectable` using the grammar.
2. **Semantics.** Expand its denotation into set-builder notation.
3. **Well-formedness.** Write inference rules for union and difference well-formedness.
4. **Implementation.** Build smart constructors that flatten nested unions and intersections.
5. **Proof.** Prove that smart-constructor removal of `top` from an intersection preserves denotation.
6. **Design.** Decide whether `Archived` should be a capability, atom, or refinement in three different application models.

---

# 11. Membership and semantic subtyping

## Learning objectives

After this chapter you should be able to:

1. define global and environment-local semantic subtyping;
2. derive basic subtype laws from set inclusion;
3. distinguish semantic subtyping from a nominal reachability approximation;
4. understand soundness and completeness of a subtype algorithm;
5. reason about open-world negation.

## 11.1 Membership

Membership is the fundamental question:

\[
R;e\vDash r:\tau
\quad\text{iff}\quad
r\in\llbracket\tau\rrbracket^R_e.
\]

An evaluator attempts to decide this relation and produce evidence.

Note the direction of dependence:

```text
type expression + registry + environment + reference
                              ↓
                       membership result
```

A type expression is not a class whose methods are invoked on a value. It is a query interpreted by a registry.

## 11.2 Global semantic subtyping

Define:

\[
R\vDash\tau\leq\sigma
\quad\text{iff}\quad
\forall e\in E.\;
\llbracket\tau\rrbracket^R_e
\subseteq
\llbracket\sigma\rrbracket^R_e.
\]

This is an environment-uniform claim. It says that every reference satisfying \(\tau\), in every admissible environment, also satisfies \(\sigma\).

Examples:

\[
\textsf{Project}\land\operatorname{cap}(\textsf{Inspectable})
\leq
\textsf{Project},
\]

\[
\textsf{Project}
\leq
\textsf{Project}\lor\textsf{Workspace}.
\]

## 11.3 Environment-local subtyping

Sometimes we need:

\[
R;e\vDash\tau\leq_e\sigma
\quad\text{iff}\quad
\llbracket\tau\rrbracket^R_e
\subseteq
\llbracket\sigma\rrbracket^R_e.
\]

For example, in an environment where every visible project happens to be editable:

\[
\textsf{VisibleProject}\leq_e\textsf{Editable}.
\]

This may not hold globally. Environment-local inclusion is useful for optimization or explanation but should not normally justify persistent method ordering or static API contracts.

## 11.4 Basic subtype laws

By set inclusion:

### Reflexivity

\[
\tau\leq\tau.
\]

### Transitivity

\[
\tau\leq\sigma\land\sigma\leq\rho
\Rightarrow\tau\leq\rho.
\]

### Bottom and top

\[
\bot\leq\tau\leq\top.
\]

### Intersection elimination

\[
\tau\land\sigma\leq\tau,
\qquad
\tau\land\sigma\leq\sigma.
\]

### Intersection greatest lower bound

If \(\rho\leq\tau\) and \(\rho\leq\sigma\), then:

\[
\rho\leq\tau\land\sigma.
\]

### Union introduction

\[
\tau\leq\tau\lor\sigma,
\qquad
\sigma\leq\tau\lor\sigma.
\]

### Union least upper bound

If \(\tau\leq\rho\) and \(\sigma\leq\rho\), then:

\[
\tau\lor\sigma\leq\rho.
\]

### Difference

\[
\tau\setminus\sigma\leq\tau,
\]

\[
(\tau\setminus\sigma)\land\sigma\equiv\bot.
\]

## 11.5 Named declarations as axioms

A declaration:

```ts
types.declareSubtype(Project, Entity);
```

adds an axiom:

\[
R\vdash\textsf{Project}\leq\textsf{Entity}.
\]

For soundness, the registry must ensure or assume:

\[
\llbracket\textsf{Project}\rrbracket_e
\subseteq
\llbracket\textsf{Entity}\rrbracket_e.
\]

In TypeScript, a representation-level condition can catch many mistakes:

```ts
type SafeSupertypeMap<V extends object> = {
  [K in keyof V & string]?: readonly {
    [S in keyof V & string]: V[K] extends V[S] ? S : never
  }[keyof V & string][];
};
```

If `Project` structurally extends `Entity`, direct consumption is representation-safe. Static structural inclusion is not a full proof of behavioral substitutability, especially with mutation or stronger semantic contracts [LiskovWing1994], but it is a useful guardrail.

## 11.6 A decidable core algorithm

A syntax-directed subtype algorithm can implement rules such as:

```text
τ ≤ top
bottom ≤ σ
atom a ≤ atom b when b is in ancestorClosure(a)
τ ∧ σ ≤ τ
τ ∧ σ ≤ σ
τ ≤ τ ∨ σ
σ ≤ τ ∨ σ
ρ ≤ τ and ρ ≤ σ  => ρ ≤ τ ∧ σ
τ ≤ ρ and σ ≤ ρ  => τ ∨ σ ≤ ρ
```

Care is required. Naive recursive rules can loop or branch exponentially. Normalize expressions, memoize pairs `(leftId, rightId)`, and track in-progress pairs.

A practical algorithm may compile expressions to clauses:

```ts
interface Clause {
  readonly requiredAtoms: bigint;
  readonly excludedAtoms: bigint;
  readonly refinements: readonly RefinementInstance[];
}
```

A union is a set of clauses. Inclusion becomes a coverage problem plus registered implication facts among refinements.

## 11.7 Refinement implications

From set semantics:

\[
\operatorname{refine}(p,\theta,\tau)\leq\tau.
\]

But the runtime cannot generally decide:

\[
\operatorname{OwnedBy}(7,\textsf{Project})
\leq
\operatorname{Visible}(\textsf{Project}).
\]

Even if application policy makes it true, the executable predicates are opaque.

The registry may declare implication lemmas:

```ts
types.declareRefinementImplication({
  from: OwnedBy(currentUserId),
  to: Visible,
  scope: "authorization-policy-v3",
});
```

Such declarations enter the trusted base and should be testable against policy fixtures.

## 11.8 Soundness and completeness boundary

Let `algSubtype(R, τ, σ)` be the implementation.

Soundness requires:

\[
\operatorname{algSubtype}(R,\tau,\sigma)=\mathsf{true}
\Rightarrow R\vDash\tau\leq\sigma.
\]

Completeness for grammar fragment \(F\) requires:

\[
\tau,\sigma\in F\land R\vDash\tau\leq\sigma
\Rightarrow
\operatorname{algSubtype}(R,\tau,\sigma)=\mathsf{true}.
\]

A PBUI implementation should document its fragment. Claiming “semantic subtyping” does not imply that the algorithm decides every inclusion among arbitrary JavaScript predicates.

## 11.9 Open-world negation

Suppose a compiled type is:

\[
\neg\textsf{Archived}.
\]

A plugin later registers `ExternalReport`, none of whose members are archived. The complement now includes new values. The meaning changed because the universe changed.

Three policies are coherent:

### Registry-snapshot semantics

Every compiled expression records `registryVersion`. Plugin installation invalidates compiled complements.

### Base-relative difference

Expose only:

\[
\textsf{Project}\setminus\textsf{Archived}.
\]

The base constrains the relevant universe.

### Closed-world modules

A type expression belongs to a sealed registry module whose universe cannot be extended.

The recommended default is base-relative difference plus registry-versioned compilation.

## 11.10 What can be left out?

A system can use only nominal reachability and selector predicates. It should then call the operation `isNominalSubtype`, not imply complete set-theoretic reasoning. Add unions and intersections when action specificity or reusable compound contexts require them.

## Exercises

1. **Proof.** Prove intersection elimination from denotational semantics.
2. **Proof.** Prove the union least-upper-bound rule.
3. **Algorithm.** Implement memoized subtype checking for atoms, unions, intersections, top, and bottom.
4. **Counterexample.** Show that TypeScript structural assignability alone does not establish behavioral substitutability for mutable objects.
5. **Open world.** Construct a plugin example where global complement changes denotation.
6. **Design.** Write a precise completeness claim for a subtype algorithm that treats refinements as opaque atoms.
7. **Advanced.** Investigate how CDuce represents union, intersection, and negation types and compare its problem domain with PBUI.

---

# 12. Atoms, capabilities, and nominal declarations

## Learning objectives

After this chapter you should be able to:

1. distinguish domain-role atoms from behavioral capabilities;
2. declare representation-safe nominal subtyping;
3. model static and dynamic capability membership;
4. prevent combinatorial nominal-type proliferation;
5. choose between atoms, capabilities, and refinements.

## 12.1 Atomic presentation roles

An atom names a fundamental semantic role with one representation family:

```text
Project
ProjectId
Document
Field
Tile
Workspace
```

Atoms answer:

> In what basic semantic role is this value being presented?

They should be stable, relatively few, and owned by a registry namespace.

```ts
const Project = types.atom<Project>("project", {
  validate: isProject,
  identity: project => ({
    namespace: "project",
    key: project.id,
  }),
});
```

## 12.2 Nominal subtype declarations

A subtype declaration says direct substitution is intended:

```ts
types.declareSubtype(Project, Entity);
types.declareSubtype(Document, Entity);
```

The registry computes transitive closure:

```text
Project ≤ DocumentLike ≤ Entity
therefore Project ≤ Entity
```

Multiple inheritance is permitted when representations and semantics support it:

```text
Dataset ≤ Document
Dataset ≤ Tabular
```

However, `Tabular` may be better modeled as a capability if its purpose is to select behavior rather than provide one representation contract.

## 12.3 Capabilities

A capability names a proposition or supported interface:

```text
Inspectable
Editable
DocumentBacked
LinkableSubject
Searchable
Exportable
```

Capabilities answer:

> What semantic affordance or behavior applies?

```ts
const Inspectable = types.capability("inspectable");
const DocumentBacked = types.capability("document-backed");

types.implement(Project, Inspectable);
types.implement(Project, DocumentBacked);
types.implement(Chart, Inspectable);
```

This resembles protocols or traits more than class inheritance. Clojure protocols and Elixir protocols are useful comparative models: behavior is declared independently of one class tree [ClojureProtocols; ElixirProtocols].

## 12.4 Static capabilities

A static implementation always holds for direct members of an atom:

\[
\llbracket\textsf{Project}\rrbracket_e
\subseteq
\llbracket\operatorname{cap}(\textsf{Inspectable})\rrbracket_e.
\]

This is effectively a subtype edge to a capability proposition and can be compiled into the atom fact closure.

```ts
types.implement(Project, Inspectable, {
  mode: "static",
});
```

## 12.5 Dynamic capabilities

A dynamic capability depends on object or environment state:

```ts
types.implement(Project, Archivable, {
  mode: "dynamic",
  test(project, environment) {
    return environment.permissions.canArchive(project.id) &&
      !project.archived;
  },
  dependencies(project, environment) {
    return [
      project.revision,
      environment.permissions.epoch,
    ];
  },
});
```

Mathematically, this is a refinement set. The capability syntax is convenient for dispatch, but the implementation must retain refinement semantics.

A useful rule is:

```text
static, representation-wide fact → capability implementation
value- or environment-dependent fact → named refinement or dynamic capability
```

## 12.6 Why not put everything in the hierarchy?

A hierarchy like:

```text
Entity
└── InspectableEntity
    └── EditableInspectableEntity
        └── ActiveEditableInspectableProjectOwnedByCurrentUser
```

mixes independent dimensions and grows exponentially. With \(n\) independent Boolean properties, there can be \(2^n\) combinations.

Intersections keep dimensions orthogonal:

\[
\textsf{Project}
\land\textsf{Inspectable}
\land\textsf{Editable}
\setminus\textsf{Archived}.
\]

## 12.7 Role versus capability ambiguity

Some names can be modeled either way.

### `DocumentBacked`

If it merely enables a “change document” action, use a capability.

If every document-backed reference has a common representation that consumers directly inspect, a nominal supertype may be appropriate.

### `Tabular`

If it means “supports row/column operations through a protocol,” use a capability.

If `TabularValue` is an explicit shared interface carried directly by all subtypes, a nominal atom may be useful.

### `Archived`

If archived objects have a distinct stable lifecycle representation, an atom might be justified. If it is a mutable flag, use a refinement or dynamic capability.

## 12.8 Behavioral subtyping

Liskov and Wing's account of behavioral subtyping emphasizes that subtype objects should preserve properties expected by supertype clients [LiskovWing1994]. In mutable object-oriented systems this includes method preconditions, postconditions, and invariants.

PBUI nominal subtyping is narrower: it governs direct semantic consumption of tagged values. Still, the same caution applies. If an `EditableProject` strengthens a required precondition for an `Entity` operation, a purely structural declaration can be misleading.

Document semantic expectations on atomic descriptors:

```ts
interface AtomContract<T> {
  readonly representation: RuntimeSchema<T>;
  readonly invariants: readonly string[];
  readonly consumersMayAssume: readonly string[];
}
```

These strings are documentation unless backed by tests or refinements, but they make the contract inspectable.

## 12.9 Capability methods

Capabilities can optionally define operations, making them closer to protocols:

```ts
const DocumentBacked = types.protocol("document-backed", {
  documentId(value, environment): string;
});
```

Implementation:

```ts
types.implementProtocol(Project, DocumentBacked, {
  documentId(project) {
    return project.documentId;
  },
});
```

This is useful when actions require a uniform operation. If capabilities are only set membership, action methods must narrow or translate each representation separately.

A protocol method should not be confused with a UI action. It is a semantic operation used to implement actions.

## 12.10 What can be left out?

A project can omit capabilities and use intersections of nominal atoms only. It can also model capabilities as zero-argument refinements. Add a dedicated capability layer when:

- many unrelated atoms support one behavior;
- action signatures repeatedly mention the behavior;
- protocol operations provide a useful uniform API;
- static fact bitsets materially improve matching.

## Exercises

1. **Classification.** Classify `Project`, `Inspectable`, `Selected`, `DocumentBacked`, `ProjectId`, and `Writable` as atom, capability, or refinement. State your assumptions.
2. **Design.** Replace a four-level capability-heavy class hierarchy with atoms and intersections.
3. **Proof.** Show that a static capability implementation induces a subtype relation from the implementing atom to the capability set.
4. **Implementation.** Compile static capabilities into an atomic fact bitset.
5. **Behavioral analysis.** Give a structurally safe TypeScript subtype declaration that violates a semantic expectation.
6. **Protocol design.** Define a `DocumentBacked` protocol and implementations for chart and pipeline views.

---

# 13. Refinements and parameterized types

## Learning objectives

After this chapter you should be able to:

1. define refinements as subsets of a base type;
2. distinguish named, parameterized refinements from ephemeral lambdas;
3. model predicate dependencies and revisions;
4. relate UI refinement to occurrence typing and liquid types;
5. state the limits of subtype reasoning over opaque predicates.

## 13.1 Refinement types

A refinement type restricts a base type by a proposition:

\[
\{r:\tau\mid p(r,e,\theta)\}.
\]

Our syntax is:

\[
\operatorname{refine}(p,\theta,\tau).
\]

Its fundamental law is:

\[
\operatorname{refine}(p,\theta,\tau)\leq\tau.
\]

Examples:

```text
{ p : Project | not p.archived }
{ f : Field   | f.documentId = d }
{ d : Document| canWrite(currentUser, d) }
```

Refinement types in programming-language research use logical predicates to strengthen ordinary types. Liquid Types restrict refinements to decidable logical fragments and use automated reasoning [LiquidTypes; LiquidHaskell]. Typed Racket's occurrence typing refines variable types after successful predicates and control-flow tests [TypedRacket]. PBUI uses runtime checks but benefits from the same conceptual separation between representation and established proposition.

## 13.2 Named refinements

A named refinement has a registry identity:

```ts
const OwnedBy = types.defineRefinement<
  Project,
  { readonly userId: string },
  Environment
>({
  id: "project/owned-by",
  base: Project,

  test(project, args) {
    return project.ownerId === args.userId;
  },

  dependencies(project, args) {
    return [project.revision, args.userId];
  },
});
```

Instantiation is data:

```ts
const MyProjects = OwnedBy({ userId: currentUser.id });
```

Named instances can be:

- serialized;
- hashed;
- explained;
- cached;
- compared syntactically;
- referenced in action signatures;
- reconstructed after persistence.

## 13.3 Parameterized presentation types

A parameterized type is a named refinement family:

```ts
const FieldOf = types.defineRefinement<
  Field,
  { readonly documentId: string },
  Environment
>({
  id: "field/of-document",
  base: Field,
  test(field, { documentId }) {
    return field.documentId === documentId;
  },
});
```

Use:

```ts
await pbui.accept({
  type: FieldOf({ documentId: activeDocumentId }),
  prompt: "Choose a field in this document",
});
```

This avoids inventing one global atom per document.

## 13.4 Ephemeral refinements

Some predicates are workflow-local:

```ts
const temporarySet = new Set(selectedCandidateIds);

const selector = types.ephemeral(Project, {
  description: "one of the current comparison candidates",
  cache: "operation",
  test(project) {
    return temporarySet.has(project.id);
  },
});
```

An ephemeral refinement cannot normally be serialized or compared for semantic equivalence. Give it an operation-local identity so caches and diagnostics can distinguish it.

## 13.5 Predicate preparation

A selector often needs preprocessing:

```ts
types.ephemeral(Field, {
  prepare(environment) {
    const allowed = new Set(
      environment.schema.fields
        .filter(field => field.quantitative)
        .map(field => field.id),
    );

    return (field: Field) => allowed.has(field.id);
  },
});
```

Preparation changes the cost from repeated scanning to one indexing pass:

```text
without preparation: O(nm)
with preparation:    O(m) + O(n)
```

where \(n\) is the number of occurrences and \(m\) the schema size.

The prepared predicate must be tied to one coherent environment snapshot.

## 13.6 Dependency fingerprints

A cached refinement result is valid only while every observed dependency remains unchanged.

```ts
interface DependencyFingerprint {
  readonly refinementId: string;
  readonly parts: readonly (string | number | boolean | null)[];
}
```

A refinement declaration can provide:

```ts
dependencies(project, args, environment) {
  return {
    refinementId: "project/archivable",
    parts: [
      project.id,
      project.revision,
      environment.authorizationEpoch,
      args.policyVersion,
    ],
  };
}
```

A dependency list is a proof obligation: if the predicate result can change while the fingerprint remains equal, cache reuse is unsound.

## 13.7 Purity and effect classification

Predicates should be classified:

| Class | Example | Recommended cache | Serializable? |
|---|---|---:|---:|
| structural | `field.kind === "number"` | by object revision | yes, if named |
| pure | deterministic computation | by declared dependencies | yes, if named |
| environment-dependent | permission lookup in snapshot | environment epoch | usually |
| volatile | pointer proximity, current transient set | operation only | no |
| effectful | network request, mutation | not a refinement | no |

An effectful or asynchronous operation belongs in translation, loading, or command execution. Keeping core membership synchronous makes highlighting predictable.

An advanced system can represent `unknown` and schedule data acquisition, but this should be explicit rather than hidden inside a Boolean predicate.

## 13.8 Refinement implication

The system always knows:

\[
\operatorname{refine}(p,\theta,\tau)\leq\tau.
\]

It may know parameter-specific implications:

\[
\operatorname{OwnedBy}(u,\textsf{Project})
\leq
\operatorname{VisibleTo}(u,\textsf{Project}),
\]

if policy declares and justifies them.

Opaque lambdas admit almost no automatic implication reasoning. Two syntactically different functions can be extensionally equal, and determining arbitrary program equivalence is undecidable.

Therefore the subtype engine should treat unnamed lambdas as distinct opaque refinements except for identity and base-type rules.

## 13.9 Occurrence typing in the UI

After a successful test, an occurrence has additional evidence:

```ts
const match = matcher.match(ref, ActiveProject);

if (match.ok) {
  // Operationally, match carries evidence that archived === false
}
```

This resembles occurrence typing, where control-flow tests refine the type of a variable in a branch [TypedRacket].

TypeScript can expose a narrowed view using branded wrappers:

```ts
type Proven<R, T extends TypeExpr> = Readonly<{
  reference: R;
  evidence: Evidence<T>;
}>;
```

Avoid permanently branding the mutable project object itself as `ActiveProject`. The proposition may cease to hold after an archive command. Evidence is snapshot-indexed.

## 13.10 Restricted guard languages

Elixir guards illustrate another design: restrict predicates to an analyzable, side-effect-free language. Such a language can support:

- serialization;
- dependency extraction;
- implication checking;
- remote execution;
- query planning.

A PBUI guard AST might be:

```ts
type GuardExpr =
  | { kind: "field"; path: readonly string[] }
  | { kind: "literal"; value: unknown }
  | { kind: "eq"; left: GuardExpr; right: GuardExpr }
  | { kind: "and"; members: readonly GuardExpr[] }
  | { kind: "not"; operand: GuardExpr }
  | { kind: "in"; value: GuardExpr; set: readonly unknown[] };
```

This can coexist with arbitrary lambdas:

```text
named guard AST → optimized, serializable, explainable
arbitrary lambda → local escape hatch
```

## 13.11 What can be left out?

A selector API can support only `where(reference, environment)`. Add named refinements when predicates recur, require explanation, or need persistence. Add dependency fingerprints when profiling shows applicability checks are material. Add a guard language only if serialization, static analysis, or remote evaluation is an actual requirement.

## Exercises

1. **Definition.** Define `FieldOf(documentId)` and `OwnedBy(userId)` refinements.
2. **Proof.** Prove that every refinement is a subtype of its base.
3. **Counterexample.** Show why a permanent `ActiveProject` brand is unsound under mutation.
4. **Performance.** Transform an \(O(nm)\) selector into a prepared \(O(m+n)\) selector.
5. **Dependency analysis.** Find a missing dependency in a permission predicate and construct a stale-cache failure.
6. **Language design.** Extend the guard AST with numeric comparison while keeping evaluation total.
7. **Research.** Compare unrestricted PBUI lambdas with Liquid Types' decidable predicate discipline.

---

# 14. Semantic identity

## Learning objectives

After this chapter you should be able to:

1. define a typed semantic identity protocol;
2. compare references across presentation types without structural equality;
3. state identity stability and revision laws;
4. use identity safely in matching caches and linked selections;
5. explain when identity must remain undefined.

## 14.1 Identity as a separate interpretation

Typing asks which set contains a reference. Identity asks which domain object it denotes.

Define a partial identity interpretation:

\[
\operatorname{id}^R_e:\Omega_R\rightharpoonup N\times K,
\]

where \(N\) is an identity namespace and \(K\) a stable key domain.

```ts
interface SemanticIdentity {
  readonly namespace: string;
  readonly key: string;
}
```

Two identity-bearing references are the same object when keys are equal:

\[
r\approx^R_e s
\quad\text{iff}\quad
\operatorname{id}^R_e(r)=\operatorname{id}^R_e(s).
\]

## 14.2 Descriptor definitions

```ts
const Project = types.atom<Project>("project", {
  identity(project) {
    return {
      namespace: "project",
      key: project.id,
    };
  },
  revision(project) {
    return project.revision;
  },
});

const ProjectId = types.atom<string>("project-id", {
  identity(projectId) {
    return {
      namespace: "project",
      key: projectId,
    };
  },
});
```

The shared namespace intentionally equates alternate representations.

## 14.3 Undefined identity

Not every value has stable semantic identity.

Examples:

- an unsaved anonymous expression;
- a transient aggregate computed from a selection;
- a row without a producer-supplied key;
- a duplicate value where occurrence matters;
- an error object whose identity should be its occurrence.

The identity function should return `undefined` rather than guess.

Fallback policy can be explicit:

```ts
type IdentityFallback =
  | "none"
  | "primitive-value"
  | "object-reference";
```

Deep structural equality should require an explicit domain declaration because it can collapse distinct duplicates and is expensive on large or cyclic objects.

## 14.4 Composite identities

A field may be identified by document and field key:

```ts
identity(field) {
  return {
    namespace: "field",
    key: stableTuple([field.documentId, field.name]),
  };
}
```

Use an unambiguous encoding. String concatenation with a delimiter can collide:

```text
("a:b", "c") and ("a", "b:c")
```

Safer options include canonical JSON arrays, length-prefix encoding, or structured key objects hashed by a deterministic canonicalizer.

## 14.5 Revisions

Identity answers *which object*. Revision answers *which observable state*.

```ts
interface SemanticVersion {
  readonly identity: SemanticIdentity;
  readonly revision: string | number;
}
```

Two references can have equal identity and different revisions:

\[
r_t\approx r_{t+1}
\qquad
\operatorname{rev}(r_t)\neq\operatorname{rev}(r_{t+1}).
\]

Caches for predicates should normally key by both identity and relevant revision.

## 14.6 Identity-preserving translation

A translator \(t\) is identity-preserving when:

\[
t(r)=r'\Rightarrow r\approx r'.
\]

`ProjectId -> Project` is usually intended to preserve identity. `Field -> AggregateField` may not.

Metadata:

```ts
interface TranslatorContract {
  readonly preservesIdentity: boolean;
}
```

The runtime may verify the claim when both identities are available:

```ts
if (translator.preservesIdentity &&
    !registry.sameObject(source, target, environment)) {
  throw new IdentityPreservationViolation(translator.id);
}
```

## 14.7 Identity cache correctness

Suppose a predicate \(p\) is identity-invariant at revision \(v\):

\[
r\approx s
\land \operatorname{rev}(r)=\operatorname{rev}(s)=v
\Rightarrow p(r,e)=p(s,e).
\]

Then one predicate result may be reused across identity-equivalent occurrences.

However, the accepted payload should still be materialized from the activated occurrence or rerun translation. Otherwise the cache may return the wrong representation instance even though applicability is shared.

This yields a two-level strategy:

```text
cache applicability decision by semantic identity + revision
commit using the clicked occurrence and current environment
```

## 14.8 Identity and selection

A selection model should decide whether it stores:

- an occurrence ID;
- a semantic reference;
- a semantic identity key;
- a subject binding containing one of the above.

For “highlight every occurrence of the selected project,” store semantic identity. For “keep focus on this exact card,” store occurrence identity. For “chart and pipeline follow the same document,” store or share a subject binding.

## 14.9 Identity law suite

For all identity-bearing references in one snapshot:

```text
reflexive:  sameObject(a, a)
symmetric:  sameObject(a, b) = sameObject(b, a)
transitive: sameObject(a, b) ∧ sameObject(b, c) ⇒ sameObject(a, c)
stable:     immutable redecoding preserves identity
namespaced: unrelated domains do not collide
```

Additional domain laws:

```text
project-id translation preserves project identity
field identity changes when document identity changes
placement identity does not collapse two placements of one view
```

## 14.10 Security boundary

Semantic identity is not authorization. Knowing that two references denote project 7 does not grant access to project 7. Server commands must validate identity and permissions independently.

Do not include secrets or untrusted user-controlled strings in identity namespaces without canonicalization and boundary validation.

## 14.11 What can be left out?

If references already consist only of normalized IDs, identity can be ordinary typed key equality. Revision support can be deferred until caching or optimistic updates require it. Cross-type identity is optional until alternate presentations or translators need it.

## Exercises

1. **Design.** Specify identity and revision for a field, chart mark, table row, logical view, and placement.
2. **Proof.** Prove that deterministic key equality is an equivalence relation.
3. **Counterexample.** Construct two distinct rows that deep structural equality would collapse.
4. **Implementation.** Implement a collision-free canonical composite-key encoder for JSON scalar tuples.
5. **Testing.** Test that `ProjectId -> Project` preserves identity across immutable updates.
6. **Cache analysis.** State the exact assumptions required to reuse a refinement result across two identity-equivalent references.

---
# 15. Translations, coercions, and paths

## Learning objectives

After this chapter you should be able to:

1. model a translator as a typed partial computation rather than a subtype edge;
2. describe translator effects, totality, purity, and identity preservation;
3. define path cost and select paths deterministically;
4. identify ambiguity, cycles, and unsafe implicit conversion;
5. state soundness conditions for translator results.

## 15.1 Translation changes representation or role

Suppose the interface presents:

\[
r=\langle\textsf{project-id},\texttt{"p-7"}\rangle.
\]

An input context requests `Project`. A lookup can produce:

\[
r'=\langle\textsf{project},p_7\rangle.
\]

The source is not directly a `Project` reference, even though it may denote the same object. The relation is translation:

\[
R;e\vdash r\xRightarrow{t}r'.
\]

## 15.2 Typed translator declaration

```ts
interface Translator<
  V extends object,
  From extends keyof V & string,
  To extends keyof V & string,
  E
> {
  readonly id: string;
  readonly from: From;
  readonly to: To;
  readonly cost: number;
  readonly priority?: number;
  readonly total: boolean;
  readonly pure: boolean;
  readonly asynchronous: boolean;
  readonly preservesIdentity: boolean;

  applicable?(
    value: V[From],
    environment: E,
  ): boolean;

  translate(
    value: V[From],
    environment: E,
    signal: AbortSignal,
  ):
    | V[To]
    | undefined
    | Promise<V[To] | undefined>;
}
```

The generic parameters ensure that a declared `projectId -> project` translator consumes a string and returns a project representation.

## 15.3 Partiality

A translator may be undefined because:

- a lookup key is absent;
- the source is outside a tester-defined subset;
- authorization denies resolution;
- required data is not loaded;
- the transformation is mathematically partial.

Use a structured result when failure distinctions matter:

```ts
type TranslationResult<T> =
  | { readonly kind: "success"; readonly value: T }
  | { readonly kind: "not-applicable" }
  | { readonly kind: "unknown"; readonly reason: string }
  | { readonly kind: "error"; readonly error: unknown };
```

`undefined` is adequate for a synchronous, local, non-diagnostic core.

## 15.4 Totality and purity

A translator is **total** on its declared source type when:

\[
\forall r\in\llbracket\textsf{from}\rrbracket_e.
\;\exists r'.\;r\xRightarrow{t}r'.
\]

A translator is **pure** when repeated evaluation in the same logical snapshot yields observationally equivalent results and performs no externally visible effect.

Purity matters for:

- hover applicability;
- speculative path search;
- memoization;
- replay and explanation;
- server/client consistency.

Do not run a mutating translator merely to decide whether an occurrence should highlight.

## 15.5 Synchronous versus asynchronous translation

Synchronous translators are suitable for pointer-time matching:

```text
category reference -> field reference
row reference      -> document reference
```

Asynchronous translators may require loading:

```text
project ID -> remote project
```

Two coherent UI policies exist.

### Policy A: synchronous applicability only

Only already-resolvable translators influence highlighting. Selection never waits on unknown remote data.

### Policy B: staged acceptance

An occurrence can be marked “resolvable.” Activating it enters a pending state, runs the asynchronous translator with cancellation, and either completes or reports failure.

Policy B is more powerful but needs the state machine in Chapter 18 and an accessible pending/error experience.

## 15.6 Translation graph

Let translator types form directed edges:

\[
\textsf{ProjectId}\xrightarrow{t_1}\textsf{Project},
\]

\[
\textsf{Project}\xrightarrow{t_2}\textsf{EntitySummary}.
\]

A path is a sequence:

\[
p=t_1;t_2;\ldots;t_n.
\]

Its partial composition is defined only when every step succeeds:

\[
\llbracket p\rrbracket_e(r)
=\llbracket t_n\rrbracket_e(\cdots\llbracket t_1\rrbracket_e(r)).
\]

With nonnegative edge costs:

\[
\operatorname{cost}(p)=\sum_{i=1}^{n}\operatorname{cost}(t_i).
\]

Cost is a policy measure, not proof of semantic quality. It can approximate latency, information loss, cognitive surprise, or preferred directness.

## 15.7 Path search

A bounded Dijkstra-style search is appropriate when:

- costs are nonnegative;
- edges are indexed by source atom;
- target membership can be checked after each step;
- the graph is modest;
- the maximum path depth and explored-state count are bounded.

Priority queue entries contain:

```ts
interface SearchNode<R> {
  readonly reference: R;
  readonly path: readonly TranslatorId[];
  readonly cost: number;
  readonly depth: number;
}
```

Visited states should use both presentation role and semantic identity when available:

```text
(type, identity namespace, identity key)
```

Fallback to representation occurrence identity if no semantic identity exists.

### Proposition 15.1 — Least-cost path

For a finite graph with nonnegative edge costs and deterministic edge expansion, Dijkstra's algorithm returns a minimum-cost reachable target state when one exists.

The standard proof uses the invariant that when a node is removed from the priority queue with least tentative cost, no later path can reach it more cheaply because every remaining extension has nonnegative cost.

The PBUI qualification is important: translator execution can be partial and may produce value-dependent graph states. The theorem applies to the concrete state graph actually explored in one snapshot.

## 15.8 Cycles

Type-level cycles are possible:

```text
A -> B -> A
```

Value-level cycles are possible even without type cycles if translators reconstruct fresh representations.

Defenses:

- maximum path depth;
- maximum expanded states;
- visited semantic states;
- cancellation;
- rejection of zero-cost cycles;
- diagnostics showing the path prefix.

A single direct translation is the safest default. Graph search should be opt-in for applications that need compositional conversion.

## 15.9 Ambiguity

Two paths can reach acceptable targets:

```text
ProjectId -> CachedProject
ProjectId -> RemoteProject
```

or:

```text
Category -> Field
Category -> FilterPredicate -> FieldExpression
```

Resolution can consider, in order:

1. direct membership before translation;
2. lower total cost;
3. more specific target type;
4. explicit translator priority;
5. stable translator ID for deterministic diagnostics;
6. an ambiguity error when semantics remain incomparable.

Do not silently depend on module registration order.

## 15.10 Information loss and explicitness

Some conversions are lossy:

```text
Project -> ProjectTitle
Timestamp -> Date
RichField -> FieldName
```

Metadata can classify:

```ts
readonly information: "preserving" | "lossy" | "enriching";
readonly implicit: boolean;
```

A lossy conversion may be valid for rendering but unsuitable as an implicit command-argument translator. Separate registries or policies can govern:

- acceptance translations;
- display projections;
- persistence migrations;
- user-confirmed conversions.

## 15.11 Translator soundness

A translator declaration claims:

\[
R;e\vdash r:\operatorname{from}(t)
\land t_e(r)=r'
\Rightarrow
R;e\vdash r':\operatorname{to}(t).
\]

The TypeScript return type provides static guidance. Runtime schemas can validate untrusted or plugin-produced values.

For identity-preserving translators:

\[
t_e(r)=r'\Rightarrow r\approx_e r'.
\]

Property tests should exercise both claims.

## 15.12 Translation and acceptance closure

Direct denotation remains unchanged by translators. Define a separate relation:

\[
R;e\vDash r\Downarrow\tau
\]

meaning that \(r\) can satisfy a request for \(\tau\). It holds when either:

1. \(r\in\llbracket\tau\rrbracket_e\); or
2. there exists an allowed translator path \(p\) and \(r'\) such that \(p_e(r)=r'\) and \(r'\in\llbracket\tau\rrbracket_e\).

This prevents translation policy from silently redefining the type denotation itself.

## 15.13 What can be left out?

Most applications should begin with direct, one-step, synchronous translators. Add path search only when translators compose in genuine user workflows. Add asynchronous translation only when the pending state has an explicit interaction design. Metadata can begin with `id`, `from`, `to`, and `cost`.

## Exercises

1. **Classification.** Decide whether each relation is subtyping or translation: `Employee -> Person`, `ProjectId -> Project`, `CSVBytes -> Table`, `EditableProject -> Project`.
2. **Proof.** State and prove the identity-preservation law for a project lookup under a normalized store assumption.
3. **Algorithm.** Implement bounded least-cost translator search with visited semantic states.
4. **Counterexample.** Give a case where the shortest path is more lossy than a longer path.
5. **Design.** Specify failure and pending UI states for an asynchronous translator.
6. **Testing.** Generate translator paths and verify every successful final reference satisfies the declared target schema.
7. **Security.** Explain why a client-side identity-preserving translator does not establish authorization.

---

# 16. Evidence-producing matching

## Learning objectives

After this chapter you should be able to:

1. define direct and translated match results;
2. construct proof-relevant evidence trees;
3. state and sketch the central matching soundness theorem;
4. design useful failure explanations;
5. revalidate evidence safely at commitment.

## 16.1 Match, do not merely test

The core API should conceptually be:

```ts
match(reference, typeExpression, environment): MatchResult
```

rather than only:

```ts
accepts(reference): boolean
```

A match records the source occurrence and the accepted representation:

```ts
interface Match<R> {
  readonly source: R;
  readonly accepted: R;
  readonly requestedType: TypeExpr;
  readonly membership: MembershipEvidence;
  readonly translationPath: readonly TranslationEvidence<R>[];
  readonly specificity: Specificity;
  readonly validity: ValidityToken;
}
```

When no translation occurs, `source === accepted` by reference or semantic role. When translation occurs, they differ.

## 16.2 Membership evidence

```ts
type MembershipEvidence =
  | { readonly kind: "top" }
  | { readonly kind: "atom"; readonly atom: string }
  | {
      readonly kind: "nominal-subtype";
      readonly from: string;
      readonly to: string;
      readonly path: readonly string[];
    }
  | {
      readonly kind: "capability";
      readonly capability: string;
      readonly implementation: string;
      readonly dependencies: DependencyFingerprint;
    }
  | {
      readonly kind: "union";
      readonly branch: number;
      readonly evidence: MembershipEvidence;
    }
  | {
      readonly kind: "intersection";
      readonly members: readonly MembershipEvidence[];
    }
  | {
      readonly kind: "difference";
      readonly base: MembershipEvidence;
      readonly excluded: NonMembershipEvidence;
    }
  | {
      readonly kind: "refinement";
      readonly id: string;
      readonly args: unknown;
      readonly base: MembershipEvidence;
      readonly dependencies: DependencyFingerprint;
    };
```

Proof objects need not serialize the full source value. IDs, normalized paths, and fingerprints are usually enough.

## 16.3 Failure evidence

```ts
type MatchFailure =
  | {
      readonly kind: "wrong-atom";
      readonly actual: string;
      readonly expected: readonly string[];
    }
  | {
      readonly kind: "missing-capability";
      readonly capability: string;
    }
  | {
      readonly kind: "refinement-failed";
      readonly refinement: string;
      readonly explanation?: string;
    }
  | {
      readonly kind: "excluded";
      readonly excludedBy: TypeExpr;
    }
  | {
      readonly kind: "no-translation-path";
      readonly sourceType: string;
      readonly requested: TypeExpr;
    }
  | {
      readonly kind: "ambiguous-translation";
      readonly candidates: readonly CandidateSummary[];
    }
  | {
      readonly kind: "unknown";
      readonly diagnostic: string;
    };
```

Failure trees should be bounded. A large union can produce hundreds of branch failures. Keep the most explanatory failures using specificity and cost heuristics.

## 16.4 Direct matching algorithm

A recursive direct matcher follows the syntax.

```ts
function matchDirect(
  reference: Reference,
  type: TypeExpr,
  context: MatchContext,
): DirectMatchResult {
  switch (type.kind) {
    case "top":
      return success({ kind: "top" });

    case "bottom":
      return failure({ kind: "bottom" });

    case "atom":
      return matchAtom(reference, type.id, context);

    case "capability":
      return matchCapability(reference, type.id, context);

    case "union":
      return matchFirstBestUnion(reference, type.members, context);

    case "intersection":
      return matchEvery(reference, type.members, context);

    case "difference":
      return matchDifference(reference, type, context);

    case "refinement":
      return matchRefinement(reference, type, context);
  }
}
```

The evaluator should be pure relative to the supplied context. Caches live in that context and do not mutate application state.

## 16.5 Translated matching algorithm

```text
1. Try direct membership.
2. If direct succeeds, return it.
3. If translations are disallowed, fail.
4. Search permitted translator paths.
5. After each successful step, test target membership.
6. Order candidate matches by cost and specificity.
7. Return a unique best match or explicit ambiguity.
```

Direct membership normally outranks translation, even if a translator has cost zero. This avoids surprising representation changes.

## 16.6 Match soundness

### Theorem 16.1 — Direct matcher soundness

If:

\[
\operatorname{matchDirect}_{R,e}(r,\tau)
=\mathsf{success}(\pi),
\]

then:

\[
r\in\llbracket\tau\rrbracket^R_e.
\]

#### Proof sketch

By structural induction on \(\tau\).

- `top`: immediate from its denotation.
- atom: the atom matcher succeeds only from direct tag or a registered nominal subtype path; registry well-formedness establishes inclusion.
- capability: success requires a valid static implementation or a true dynamic implementation predicate.
- union: success contains evidence for one member; apply induction hypothesis and union inclusion.
- intersection: success contains evidence for every member; apply hypotheses and intersection introduction.
- difference: base succeeds and excluded membership is decidably false; therefore membership lies in set difference.
- refinement: base succeeds and the registered predicate returns true. ∎

### Theorem 16.2 — Translated acceptance soundness

If full matching returns source \(r\), accepted reference \(r'\), and requested type \(\tau\), then:

\[
r'\in\llbracket\tau\rrbracket^R_e,
\]

and every step in the recorded path satisfies its translator contract.

The theorem does **not** claim that the source \(r\) directly belongs to \(\tau\).

## 16.7 Validity tokens

Evidence is relative to a snapshot. A validity token collects relevant versions:

```ts
interface ValidityToken {
  readonly registryVersion: number;
  readonly environmentEpoch: string | number;
  readonly dependencies: readonly DependencyFingerprint[];
}
```

The token supports:

```ts
matcher.isStillValid(match.validity, currentEnvironment)
```

A coarse environment epoch is simple but invalidates broadly. Fine-grained dependencies improve reuse but enlarge the trusted contract.

## 16.8 Commit revalidation

Pointer hover and rendering may happen milliseconds or seconds before activation. The safe commitment algorithm is:

```text
1. Receive the exact activated occurrence and request token.
2. Confirm the input context is still active.
3. If evidence is valid, reuse the applicability decision.
4. Re-materialize value-dependent translations from the source occurrence.
5. Otherwise rematch against the current snapshot.
6. Confirm the final accepted reference still satisfies the request.
7. Atomically resolve the context once.
```

This avoids returning a translated object from another identity-equivalent occurrence merely because the Boolean decision was memoized.

## 16.9 Specificity evidence

For dispatch, a match can summarize how narrow the successful type is:

```ts
interface Specificity {
  readonly requiredAtomCount: number;
  readonly refinementCount: number;
  readonly excludedAtomCount: number;
  readonly semanticType: TypeExpr;
}
```

Numeric summaries are hints. The definitive comparison is subtype ordering:

\[
\tau\text{ is more specific than }\sigma
\quad\text{iff}\quad
\tau\leq\sigma\land\neg(\sigma\leq\tau).
\]

## 16.10 Explanations

A development panel can render evidence:

```text
Accepted <project-id> #p-7 as ActiveInspectableProject

1. translator project-id/to-project succeeded
2. target has atom Project
3. Project implements Inspectable
4. refinement Active succeeded
   dependency project:p-7 revision 18
5. Archived exclusion succeeded
```

Explanations make a semantic UI debuggable. They are also valuable for user-facing disabled reasons:

```text
Archive unavailable: project is already archived.
```

Avoid revealing authorization-sensitive facts. Chapter 26 addresses redaction.

## 16.11 What can be left out?

The runtime may initially retain only:

```ts
{ accepted, translatorId?, cacheKey? }
```

Full evidence becomes valuable as the number of rules and transformations grows. Design the internal result as an extensible record even if most fields are development-only.

## Exercises

1. **Derivation.** Construct complete evidence for a project ID accepted as `Project ∧ Inspectable \ Archived`.
2. **Proof.** Fill in the difference case of direct matcher soundness.
3. **Implementation.** Write a direct matcher for the core grammar and return evidence.
4. **Design.** Rank failure messages for a union with five failed branches.
5. **Race analysis.** Construct a stale-hover scenario and show how commit revalidation prevents invalid acceptance.
6. **Testing.** Compare the matcher against an explicit finite denotation for randomly generated expressions.

---

# 17. Actions as multimethods

## Learning objectives

After this chapter you should be able to:

1. model actions as methods over several semantic arguments;
2. compute applicability and specificity using product orders;
3. detect and resolve ambiguity explicitly;
4. distinguish action discovery from command execution;
5. relate the design to CLIM command tables, Clojure multimethods, and Julia multiple dispatch.

## 17.1 Actions are relational

An action does not necessarily belong to one object. Its applicability may depend on:

- the subject presentation;
- an input or command context;
- a gesture;
- the current user or role;
- a second semantic argument;
- active command tables.

For linking two views:

```text
source: DocumentBacked
argument: DocumentBacked
context: LinkDocumentContext
```

Attaching every possible action to each descriptor obscures this relation.

## 17.2 Method signatures

Define an action method signature:

\[
S_m=\langle\tau_s,\tau_c,\tau_g,\tau_1,\ldots,\tau_n\rangle,
\]

where:

- \(\tau_s\): subject type;
- \(\tau_c\): context type;
- \(\tau_g\): gesture type;
- \(\tau_i\): additional argument types.

TypeScript API:

```ts
pbui.actions.define({
  id: "archive-project",
  table: "admin",
  subject: and(Project, Archivable),
  context: AdministrativeContext,
  gesture: ContextMenuGesture,

  action({ subject }) {
    return {
      id: "archive-project",
      label: "Archive project",
      danger: true,
      verb: {
        type: "archiveProject",
        projectId: subject.accepted.value.id,
      },
    };
  },
});
```

## 17.3 Applicability

A method is applicable when every actual argument matches the corresponding signature type and its command table is active.

\[
\operatorname{applicable}(m,\vec r,e,c)
\quad\text{iff}\quad
\forall i.\;R;e\vDash r_i\Downarrow\tau_i^m
\land \operatorname{tableActive}(m,c).
\]

Action discovery should usually disallow expensive asynchronous translators. A menu should not issue network requests for every candidate method. Use direct membership and cheap pure translations, or mark the action as pending-capable.

## 17.4 Product specificity

For two signatures of equal arity:

\[
S_1\preceq S_2
\quad\text{iff}\quad
\forall i.\;\tau_i^{S_1}\leq\tau_i^{S_2}.
\]

`S1` is strictly more specific when:

\[
S_1\preceq S_2
\land
\neg(S_2\preceq S_1).
\]

Example:

```text
m1: subject Project
m2: subject Project ∧ Archivable
```

`m2` is more specific.

For two arguments:

```text
m1: (DocumentBacked, DocumentBacked)
m2: (Chart, Pipeline)
```

`m2` is more specific when `Chart ≤ DocumentBacked` and `Pipeline ≤ DocumentBacked`.

Julia's method system is a prominent practical example of dispatch over the types of all arguments [JuliaMethods]. Clojure multimethods combine arbitrary dispatch values with ad hoc hierarchies and explicit preferences [ClojureMultimethods]. CLIM command tables and presentation translators supply a related contextual command model [CLIM2].

## 17.5 Maximal applicable methods

Let \(A\) be the set of applicable methods. A method \(m\in A\) is maximal when no other applicable method is strictly more specific.

Three cases arise:

1. no applicable method: no action;
2. one maximal method: deterministic winner;
3. several incomparable maximal methods: ambiguity or method combination.

### Theorem 17.1 — Unique-maximal determinism

If method applicability is deterministic and the applicable set has exactly one maximal method under specificity, dispatch selects that method independently of registration order.

The proof is immediate from uniqueness: any correct maximal-element selection must return the sole maximal method. ∎

## 17.6 Ambiguity

Consider:

```text
mA: Project ∧ Editable
mB: Project ∧ OwnedByCurrentUser
```

For a project satisfying both, neither signature is necessarily a subtype of the other. Both are maximal.

Options:

### Reject ambiguity

Registry validation can detect obvious static overlaps, while runtime dispatch reports value-dependent ambiguity.

### Explicit preference

```ts
pbui.actions.prefer("owned-project-action", "editable-project-action");
```

Preferences must be acyclic.

### Method combination

Menus often combine independent actions rather than select one method. Stable action IDs then control overriding:

```text
descriptor-local inspect
common Inspectable inspect
```

The more specific action with ID `inspect` shadows the general one, while unrelated IDs coexist.

### Qualifiers

A CLOS-inspired system could support `before`, `after`, and `around` methods. This is powerful but usually excessive for UI action discovery.

## 17.7 Command tables and scopes

Named tables organize action vocabulary:

```ts
pbui.actionTables.define({ id: "global" });
pbui.actionTables.define({ id: "workspace", parents: ["global"] });
pbui.actionTables.define({ id: "admin", parents: ["workspace"] });
```

A provider activates tables:

```tsx
<PbuiProvider actionTables={["admin"]}>
  <Application />
</PbuiProvider>
```

Table inheritance and semantic type inheritance are separate relations. A project does not become an administrator object merely because the admin command table is active.

## 17.8 Actions versus verbs

Action discovery returns data:

```ts
interface Action<Verb> {
  readonly id: string;
  readonly label: string;
  readonly description?: string;
  readonly danger?: boolean;
  readonly enabled?: boolean;
  readonly disabledReason?: string;
  readonly verb: Verb;
}
```

Execution belongs to the application:

```ts
onPerform(action.verb);
```

This provides:

- serialization;
- undo/redo integration;
- logging;
- authorization checks;
- deterministic tests;
- separation between semantic discovery and mutation.

Some actions open a new input context rather than immediately produce a business verb. Represent these as workflow commands interpreted by the PBUI/application coordinator.

## 17.9 Binary actions and argument acquisition

A binary action can start with a subject and request a second object:

```ts
const target = await pbui.accept({
  type: DocumentBacked,
  excludeIdentity: subject.identity,
  prompt: "Choose another view to link",
});
```

The eventual verb carries stable identities:

```ts
{
  type: "linkDocumentSubjects",
  sourceViewId,
  targetViewId,
}
```

This is a modern rendering of a typed command argument interaction.

## 17.10 Performance

Index methods by:

- active table;
- one selective positive atomic or capability requirement;
- arity and gesture.

Then run full matching only on candidates. Complexity becomes proportional to plausible methods rather than all registered methods.

Cache compiled signatures by registry version. Cache value-dependent applicability only with evidence fingerprints.

## 17.11 What can be left out?

A simple registry can keep descriptor-local actions and a list of selector-driven action rules. Add full product-order dispatch when:

- actions depend on multiple semantic arguments;
- rule ambiguity becomes difficult;
- plugins contribute methods;
- registration order is no longer acceptable;
- reusable command scopes matter.

## Exercises

1. **Dispatch.** Given five method signatures, compute which are applicable and maximal for a concrete subject and context.
2. **Proof.** Prove that componentwise subtyping is a preorder on equal-arity signatures.
3. **Ambiguity.** Construct two incomparable action signatures and propose an explicit preference.
4. **Implementation.** Implement maximal-method selection without relying on registration order.
5. **Design.** Model “compare this field with another quantitative field in the same document” as a two-argument action.
6. **Critical.** When should action methods combine rather than choose one winner?
7. **Research.** Compare Clojure multimethod preferences with Julia method ambiguity errors.

---

# 18. Input contexts as a transition system

## Learning objectives

After this chapter you should be able to:

1. model `accept` as explicit state transitions;
2. define cancellation, replacement, and commitment behavior;
3. integrate synchronous and asynchronous matching safely;
4. state acceptance safety and at-most-once resolution properties;
5. reason about nested contexts and provider lifecycle.

## 18.1 Why a state machine

The surface API:

```ts
const result = await pbui.accept(request);
```

looks like a blocking read, but JavaScript continues running. The provider stores a pending interaction. Rendering, pointer events, keyboard events, data updates, cancellation, and unmounting can interleave.

An explicit state machine prevents accidental double resolution and stale commitment.

## 18.2 States

Let context IDs be unique tokens \(q\).

```ts
type AcceptMachine<R> =
  | { readonly state: "idle" }
  | {
      readonly state: "active";
      readonly id: string;
      readonly request: CompiledRequest<R>;
      readonly startedAt: number;
    }
  | {
      readonly state: "resolving";
      readonly id: string;
      readonly request: CompiledRequest<R>;
      readonly source: R;
      readonly controller: AbortController;
    };
```

Completion can immediately transition to `idle` while resolving the caller's promise exactly once. Historical completion belongs in logs, not necessarily live state.

## 18.3 Events

```ts
type AcceptEvent<R> =
  | { type: "START"; id: string; request: Request<R> }
  | { type: "COMMIT"; id: string; source: R }
  | { type: "RESOLVE"; id: string; result: Match<R> }
  | { type: "FAIL"; id: string; diagnostic: Diagnostic }
  | { type: "ABORT"; id: string; reason: AbortReason }
  | { type: "REPLACE"; id: string; request: Request<R> }
  | { type: "PROVIDER_UNMOUNT" };
```

Every event carrying an ID is ignored if it targets a stale context. This token check is the principal defense against late asynchronous completion.

## 18.4 Transition relation

We write:

\[
s\xrightarrow{event}s'.
\]

Representative transitions:

### Start

\[
\mathsf{idle}\xrightarrow{\mathsf{START}(q,req)}
\mathsf{active}(q,\operatorname{compile}(req)).
\]

### Commit with synchronous match

\[
\frac{\operatorname{match}(r,req)=\mathsf{success}(m)}
{\mathsf{active}(q,req)
\xrightarrow{\mathsf{COMMIT}(q,r)}
\mathsf{idle}}
\]

with the side effect of resolving the request with \(m\).

### Commit requiring asynchronous translation

\[
\mathsf{active}(q,req)
\xrightarrow{\mathsf{COMMIT}(q,r)}
\mathsf{resolving}(q,req,r,controller).
\]

### Abort

\[
\mathsf{active}(q,req)
\xrightarrow{\mathsf{ABORT}(q)}
\mathsf{idle}.
\]

The caller receives `null` or a structured abort result.

### Stale completion

A `RESOLVE(q, result)` event in any state with a different ID has no effect.

## 18.5 At-most-once resolution

### Invariant 18.1

Each context ID resolves its continuation at most once.

Implementation technique:

```ts
interface Continuation<R> {
  settled: boolean;
  resolve(value: R | null): void;
}

function settleOnce<R>(continuation: Continuation<R>, value: R | null) {
  if (continuation.settled) return;
  continuation.settled = true;
  continuation.resolve(value);
}
```

The reducer controls state; a coordinator owns continuations in a map keyed by context ID. Continuations themselves should not be persisted or placed in Redux state.

## 18.6 Acceptance safety

### Theorem 18.1 — Acceptance safety

Assume:

1. matcher soundness;
2. translator contract soundness;
3. commit revalidation against the current request and environment;
4. stale context IDs cannot resolve active contexts.

If context requesting \(\tau\) resolves successfully with accepted reference \(r'\), then:

\[
r'\in\llbracket\tau\rrbracket^R_e
\]

for the commitment snapshot \(e\).

#### Proof sketch

A successful resolution can arise only from the `COMMIT/RESOLVE` transition for the active ID. Revalidation produces a sound match under the commitment snapshot. The machine resolves with the match's accepted reference. Therefore matcher soundness gives membership. Stale asynchronous events are excluded by the ID check. ∎

## 18.7 Replacement policies

When `START` arrives during `active`, choose one policy.

### Reject

Return an error to the second caller. Simple and explicit.

### Replace

Abort the current context, resolve it as cancelled, then start the new context. Suitable for global “current tool” behavior.

### Stack

Suspend the current context while a nested context obtains an argument. This resembles nested reads but complicates cancellation and focus restoration.

### Workflow machine

Represent multi-stage commands in one explicit state machine. This is preferable for complex interactions such as:

```text
choose source field
choose target chart
confirm lossy conversion
execute
```

The default PBUI API should reject or replace. Stacking should be an advanced feature.

## 18.8 Provider unmount

Unmounting must abort active work:

```text
PROVIDER_UNMOUNT
  → abort asynchronous translator
  → resolve pending caller with provider-unmounted reason
  → remove global Escape ownership
  → release occurrence registrations
```

Leaving a promise unresolved is a lifecycle leak.

## 18.9 Environment changes

While active, the environment may change. Two policies are possible.

### Snapshot request

The request captures environment \(e_0\). Highlighting and commitment use that snapshot. This is coherent but may accept stale business state.

### Live request

The compiled expression remains, but matching uses current environment \(e_t\). Applicability updates reactively. Commitment always revalidates.

For UI selection, live requests are usually preferable. Preparation caches must invalidate when declared dependencies change.

## 18.10 Accessibility state

An active input context should expose:

- a visible instruction;
- an `aria-live` status announcement;
- keyboard-reachable acceptable occurrences;
- a consistent activation key;
- Escape cancellation;
- focus restoration;
- pending and failure announcements for asynchronous resolution.

Do not make every presentation a tab stop when no input context is active. Context-sensitive roving focus or a command-palette alternative can reduce keyboard burden.

## 18.11 What can be left out?

A synchronous-only implementation needs `idle`, `active`, and abort. It still needs unique IDs and at-most-once settlement. Add `resolving` only for asynchronous translation. Add stacks only for proven nested-workflow needs.

## Exercises

1. **State modeling.** Draw the transition graph for idle, active, and resolving states.
2. **Proof.** Prove at-most-once resolution from a `settled` flag plus context-ID checks.
3. **Race.** Analyze an asynchronous translator completing after Escape.
4. **Design.** Choose replacement semantics for a global application tool and justify it.
5. **Implementation.** Implement the reducer as a pure function and keep promise continuations outside state.
6. **Accessibility.** Design keyboard behavior for selecting one of 500 virtualized presentations.
7. **Advanced.** Extend the machine with a stack and state the focus-restoration invariant.

---

# 19. Views, placements, subjects, and links

## Learning objectives

After this chapter you should be able to:

1. distinguish logical views, placements, domain objects, and subject bindings;
2. model shared selection as an explicit cell or equivalence class;
3. define link, unlink, and update operations;
4. state and prove a link-coherence invariant;
5. serialize subject-sharing relationships without leaking runtime IDs.

## 19.1 Four identities in a tiled workbench

A tiled workbench commonly conflates:

1. **domain identity** — document `d-7`;
2. **logical view identity** — chart configuration `view-c`;
3. **placement identity** — tile rectangle `placement-12`;
4. **subject-binding identity** — selected-document cell `binding-b`.

Two placements can show one logical view. Two logical views can share one document binding. Neither relation implies the other.

## 19.2 Data model

```ts
type ViewId = string & { readonly __brand: "ViewId" };
type PlacementId = string & { readonly __brand: "PlacementId" };
type BindingId = string & { readonly __brand: "BindingId" };
type DocumentId = string & { readonly __brand: "DocumentId" };

interface LogicalView {
  readonly id: ViewId;
  readonly appId: string;
  readonly documentBindingId: BindingId;
  readonly configuration: unknown;
}

interface Placement {
  readonly id: PlacementId;
  readonly viewId: ViewId;
  readonly rectangle: Rectangle;
}

interface SubjectBinding {
  readonly id: BindingId;
  readonly subjects: Readonly<Record<string, DocumentId>>;
}
```

A role map supports multiple document slots:

```text
primary
comparison
reference
```

## 19.3 Private bindings as the default

Every new logical view receives a fresh private binding:

```text
view-c -> binding-c -> primary document α
view-p -> binding-p -> primary document β
```

This means ordinary duplication creates independent selectors.

A linked duplicate that reuses the same `viewId` is different: both placements show one logical view and therefore naturally share all its configuration, not merely document selection.

## 19.4 Linking

To link source view \(v_s\) and target view \(v_t\), choose or create one binding and assign every member of both binding classes to it.

```ts
linkViewSubjects({ sourceViewId, targetViewId })
```

Policy question: which subject values win at link time?

A clear rule is source-wins:

```text
source group's role map becomes the merged role map
```

Alternative policies:

- target-wins;
- reject if values differ;
- ask the user;
- merge non-conflicting roles and resolve conflicts explicitly.

The policy should be visible in the command description.

## 19.5 Updating a linked subject

```ts
setViewSubject({
  viewId,
  role: "primary",
  documentId: nextDocumentId,
});
```

The reducer resolves the view's binding and updates the binding once. Every linked view reads the same cell.

Do not propagate by dispatching one update per view. That produces intermediate disagreement and requires knowledge of all members. A shared source of truth makes coherence structural.

## 19.6 Unlinking

Unlink one logical view by cloning the current binding state into a fresh binding:

```text
before
  view-c ─┐
          ├─ binding-b -> document γ
  view-p ─┘

after unlink(view-p)
  view-c -> binding-b -> document γ
  view-p -> binding-new -> document γ
```

The visible selection does not jump during unlinking.

Garbage-collect an old binding when no view refers to it.

## 19.7 Link-coherence invariant

Define:

\[
\operatorname{bind}(v)=b
\]

and:

\[
\operatorname{subject}(v,q)
=\operatorname{bindings}[\operatorname{bind}(v)].\operatorname{subjects}[q].
\]

### Invariant 19.1 — Binding coherence

For all views \(v,w\) and roles \(q\):

\[
\operatorname{bind}(v)=\operatorname{bind}(w)
\Rightarrow
\operatorname{subject}(v,q)=\operatorname{subject}(w,q).
\]

### Theorem 19.1 — `setViewSubject` preserves coherence

Assume the state is well formed and `setViewSubject(v,q,d)` updates only the one binding cell referenced by \(v\). Then binding coherence holds after the transition.

#### Proof

Take arbitrary linked views \(x,y\) with the same binding after the transition.

- If their binding is not the updated binding, neither subject value changes, so prior coherence applies.
- If their binding is the updated binding, both read role \(q\) from the same updated map entry \(d\), and all other roles from the same unchanged binding map.

Therefore their subjects agree for every role. ∎

### Theorem 19.2 — `unlinkView` preserves visible subject

If unlink clones the old binding's role map into a fresh binding before reassigning the view, the unlinked view's subject values are equal before and immediately after the operation.

Proof follows from equality of the cloned role maps. ∎

## 19.8 Binding equivalence formulation

Instead of explicit cells, one can store an equivalence relation over views. Each equivalence class shares selection. The cell model is a concrete representation of the quotient:

\[
\mathsf{Views}/{\sim_b}.
\]

Explicit binding IDs are easier for immutable reducers, persistence, and incremental update.

Use union-find only when links are merged frequently and never split. Unlinking a member makes classical disjoint-set union less convenient because it does not support efficient deletion. Persistent binding records are simpler at UI scale.

## 19.9 PBUI interaction for linking

Linking itself is naturally presentation-based.

1. The source view starts an input context requesting another `DocumentBacked` view or tile.
2. The source identity is excluded.
3. Applicable tile titles highlight.
4. Selecting a target returns its logical view reference.
5. The operation emits `linkViewSubjects`.

```ts
const target = await pbui.accept({
  type: and(Tile, DocumentBacked),
  where: ref => ref.value.viewId !== sourceViewId,
  prompt: "Choose a view whose document selector should be linked",
});
```

This demonstrates the architecture's compositional goal: new interaction is expressed as a semantic request over existing output.

## 19.10 Persistence

Runtime binding IDs should not be trusted across import. A portable bundle can encode equivalence classes with dense local indices:

```json
{
  "views": [
    { "app": "chart", "subjectGroup": 0 },
    { "app": "pipeline", "subjectGroup": 0 },
    { "app": "table", "subjectGroup": 1 }
  ]
}
```

Import creates fresh view IDs and fresh binding IDs, preserving only the equivalence relation.

Schema invariants:

- every view references an existing binding;
- every placement references an existing view;
- every binding role references an existing document or an allowed unresolved handle;
- unused bindings are rejected or normalized away;
- imported IDs cannot collide with runtime IDs.

## 19.11 Remote synchronization

For collaborative or remote workbenches, decide whether subject binding is:

- durable shared application state;
- per-user view state;
- per-session transient state.

A shared chart configuration might be collaborative while each user keeps a private selected document. Binding scope should be explicit:

```ts
type BindingScope = "workspace" | "user" | "session";
```

Do not add runtime linkage only to local state while claiming remote round-trip fidelity. Protocol schemas must carry the relation or intentionally drop it with documented semantics.

## 19.12 What can be left out?

If only two components share one selector, ordinary lifted React state may be sufficient. Add binding IDs when:

- arbitrary views can link and unlink dynamically;
- links persist across layouts;
- multiple subject roles exist;
- logical views and placements are already separate;
- bundles must preserve sharing topology.

## Exercises

1. **Modeling.** Draw domain, view, placement, and binding identities for two chart placements and one pipeline view.
2. **Proof.** Prove that source-wins linking preserves coherence.
3. **Proof.** Prove that unlinking one view does not affect the remaining group's subjects.
4. **Implementation.** Write immutable reducers for link, unlink, and set subject.
5. **Persistence.** Design import/export normalization using dense group indices.
6. **Collaboration.** Decide whether document-selection bindings are shared or per-user in a collaborative analytics product.
7. **Critical.** Compare explicit binding cells with direct update propagation to every linked view.

---
# Part IV — Building the TypeScript and React API

# 20. Runtime type values with static guidance

## Learning objectives

After this chapter you should be able to:

1. divide responsibilities between TypeScript and the runtime registry;
2. construct typed runtime presentation expressions;
3. validate untrusted references at boundaries;
4. expose useful narrowing without promising timeless refinements;
5. design an API that remains usable before every advanced feature is adopted.

## 20.1 Two type systems

A TypeScript PBUI has two related but distinct type systems.

### Host-language static types

TypeScript checks source code before execution. It can establish that:

- an atom named `project` carries `Project`;
- a translator from `projectId` receives `string` and returns `Project`;
- a project action constructs a valid application verb;
- refinement parameters have the declared shape;
- a descriptor method receives the correct representation.

### Runtime semantic types

The PBUI registry decides at runtime:

- whether a concrete reference belongs to a compound type expression;
- which environment-dependent propositions hold;
- whether one semantic type is a subtype of another;
- which translator path is applicable;
- which action method is most specific;
- whether evidence remains valid.

TypeScript erases types at runtime. It also cannot infer plugin declarations or changing permissions merely from a structural interface. Therefore the runtime registry remains authoritative.

## 20.2 Typed atoms

A runtime type expression can carry a phantom output type:

```ts
declare const outputType: unique symbol;

interface TypeExpr<T = unknown> {
  readonly kind: string;
  readonly id: string;
  readonly [outputType]?: T;
}

interface Atom<T> extends TypeExpr<T> {
  readonly kind: "atom";
  readonly atomId: string;
}
```

Builder:

```ts
function atom<T>(id: string): Atom<T> {
  return Object.freeze({
    kind: "atom",
    id: `atom:${id}`,
    atomId: id,
  }) as Atom<T>;
}
```

The phantom field has no runtime cost. It guides APIs:

```ts
const Project = atom<Project>("project");
const ProjectId = atom<string>("project-id");
```

## 20.3 Union and intersection output types

For union:

```ts
function or<A, B>(
  left: TypeExpr<A>,
  right: TypeExpr<B>,
): TypeExpr<A | B>;
```

For intersection, TypeScript's `A & B` is useful only when both expressions describe the same representation value:

```ts
function and<T>(
  ...members: readonly TypeExpr<T>[]
): TypeExpr<T>;
```

Capabilities and refinements usually preserve the base representation, so:

```ts
const ActiveProject: TypeExpr<Project> =
  and(Project, Active);
```

But semantic intersections can include references of different tags that happen to satisfy capability facts. A single generic `T` cannot perfectly encode every runtime set expression. The API should prefer sound but sometimes broad static output types over clever unsound inference.

One strategy is to distinguish **reference representation** from **semantic proposition**:

```ts
interface PredicateExpr<T> extends TypeExpr<T> {
  readonly preservesRepresentation: true;
}
```

Then `refine(Project, ...)` is statically `Project`, while a union of atoms produces a reference union.

## 20.4 Typed references from atom handles

Instead of exposing string tags everywhere:

```ts
interface TypedReference<T, Id extends string = string> {
  readonly type: Id;
  readonly value: T;
}

function reference<T, Id extends string>(
  atom: Atom<T> & { readonly atomId: Id },
  value: T,
): TypedReference<T, Id> {
  return { type: atom.atomId, value };
}
```

Usage:

```ts
const ref = reference(Project, project);
```

For compatibility with a `Values` map, atom handles can be generated from a descriptor map and retain literal keys.

## 20.5 Runtime schemas

TypeScript does not validate network or plugin data. Each atom can optionally carry a runtime schema:

```ts
interface RuntimeSchema<T> {
  parse(input: unknown): T;
  is(input: unknown): input is T;
}
```

ArkType is one existing TypeScript implementation that treats runtime types as set-theoretic values and supports runtime type relationships [ArkType]. Zod, Valibot, io-ts, and JSON Schema ecosystems are alternatives for boundary schemas, although they are not presentation systems.

The PBUI type registry should accept a schema interface rather than depend on one validation library:

```ts
types.atom<Project>("project", {
  schema: projectSchemaAdapter,
});
```

Boundary rule:

```text
trusted in-process constructors may use static checks
untrusted persistence/network/plugin input must be parsed
```

## 20.6 Refinement typing

A refinement preserves its base representation:

```ts
function refine<T, Args>(
  base: TypeExpr<T>,
  definition: RefinementDefinition<T, Args>,
  args: Args,
): TypeExpr<T>;
```

A successful runtime match can return:

```ts
interface Proven<T, Expr extends TypeExpr<T>> {
  readonly value: T;
  readonly expression: Expr;
  readonly evidence: MembershipEvidence;
  readonly validity: ValidityToken;
}
```

Do not expose the result merely as `T & ActiveBrand` when `Active` can later become false. The evidence object indicates snapshot-relative proof.

## 20.7 Type guards

Structural predicates may be TypeScript type guards:

```ts
interface StructuralRefinementDefinition<Base, Narrow extends Base> {
  readonly id: string;
  test(value: Base): value is Narrow;
}
```

This is safe within the immediate control-flow branch if the underlying value does not mutate in a way that invalidates the predicate. It still does not justify persistence of the narrowed brand beyond the evidence lifetime.

## 20.8 Static subtype declarations

A builder can constrain direct subtyping:

```ts
function declareSubtype<Sub extends Super, Super>(
  sub: Atom<Sub>,
  sup: Atom<Super>,
): void;
```

This catches `ProjectId <: Project` at compile time because `string` does not extend `Project`.

TypeScript structural assignability can admit semantically questionable declarations. Runtime registry validation, documentation, and tests remain necessary.

## 20.9 Typed translators

```ts
function defineTranslator<From, To>(definition: {
  readonly id: string;
  readonly from: Atom<From>;
  readonly to: Atom<To>;
  readonly cost?: number;
  translate(
    value: From,
    environment: Environment,
    signal: AbortSignal,
  ): To | undefined | Promise<To | undefined>;
}): Translator<From, To>;
```

The source and target handles provide both runtime names and static representation types.

## 20.10 Ergonomic facade

The mathematical kernel should not dominate ordinary application code. Offer a facade:

```ts
const pbui = createPbui({ values, environment, verbs })
  .atom("project", projectDescriptor)
  .atom("projectId", projectIdDescriptor)
  .subtype("project", "entity")
  .capability("inspectable")
  .implements("project", "inspectable")
  .refinement("active-project", {
    base: "project",
    test: project => !project.archived,
  })
  .translator("project-id/to-project", {
    from: "projectId",
    to: "project",
    translate: ...,
  })
  .build();
```

Advanced users can import the algebra directly:

```ts
const requestType = and(
  Project,
  Inspectable,
  difference(top(), Archived),
);
```

## 20.11 Compatibility layer

Preserve a simple request form:

```ts
pbui.accept({
  types: ["project"],
  filter: reference => !reference.value.archived,
  prompt: "Choose a project",
});
```

Compile it internally to:

```text
atom(project) ∧ ephemeral(filter)
```

Migration can be incremental. A formal core does not require an abrupt public-API break.

## 20.12 What can be left out?

A JavaScript-only application can use untyped runtime expressions. A TypeScript application can keep the `Values` map and string tags instead of atom handles. Runtime schemas are needed only at untrusted boundaries. Phantom output types and `Proven` wrappers are optional ergonomic improvements.

## Exercises

1. **Implementation.** Define typed `atom`, `or`, `refine`, and `reference` builders.
2. **Static safety.** Write a declaration that TypeScript correctly rejects because the subtype representation is incompatible.
3. **Boundary design.** Adapt a runtime schema library of your choice to `RuntimeSchema<T>`.
4. **Critical.** Find an example where TypeScript structural subtyping is representation-safe but semantically misleading.
5. **API design.** Design an overload for `accept` that infers the accepted representation from a `TypeExpr<T>`.
6. **Migration.** Specify how legacy `types` and `filter` compile into the new algebra.

---

# 21. The registry, compiler, and matcher

## Learning objectives

After this chapter you should be able to:

1. decompose the implementation into registry, compiler, matcher, translator, and dispatcher services;
2. freeze and version a validated registry;
3. compile type expressions into efficient plans;
4. implement direct matching without React dependencies;
5. preserve explanation information through optimization.

## 21.1 Architectural layers

A clean implementation has five pure or mostly pure layers:

```text
Declarations
   ↓ validate/freeze
Registry snapshot
   ↓ compile
Type and method plans
   ↓ evaluate with environment
Matcher / translator / dispatcher
   ↓ adapt
React provider and components
```

Avoid putting React hooks in descriptors or type declarations. The semantic kernel should run in Node tests, workers, and development tooling.

## 21.2 Mutable builder, immutable snapshot

Registration is easiest through a mutable builder:

```ts
const builder = new RegistryBuilder();
builder.addAtom(...);
builder.addSubtype(...);
builder.addRefinement(...);
```

Runtime use should receive an immutable snapshot:

```ts
const registry = builder.freeze();
```

Freeze performs:

- unique-name validation;
- schema and descriptor validation;
- nominal-cycle detection;
- ancestor closure computation;
- static capability closure;
- translator source indexing;
- action-table inheritance validation;
- method index construction;
- stable registry hash or version assignment.

This separates setup errors from pointer-time interaction.

## 21.3 Registry version

```ts
interface RegistrySnapshot {
  readonly version: number;
  readonly hash: string;
}
```

Every compiled plan records the version. A plugin update produces a new snapshot rather than mutating the existing one under active contexts.

This supports snapshot isolation:

```text
active input context uses registry R7
plugin builds registry R8
new contexts use R8
old context completes or is explicitly invalidated
```

## 21.4 Atom indexing

Assign dense indices:

```ts
interface AtomInfo {
  readonly id: string;
  readonly index: number;
  readonly ancestorMask: bigint;
  readonly staticCapabilityMask: bigint;
}
```

For more than the convenient `bigint` range—there is no fixed bit limit but operations and serialization may become cumbersome—use a typed array of machine words.

Reference facts:

```ts
interface StaticFacts {
  readonly atomMask: bigint;
  readonly capabilityMask: bigint;
}
```

Direct atomic checks become bit operations.

## 21.5 Expression interning

Canonical expressions can be interned:

```ts
const id = hashCanonicalExpression(expression);
const existing = expressionPool.get(id);
```

Interning provides:

- fast syntactic equality;
- shared compiled plans;
- compact evidence references;
- stable persistence IDs for named expressions;
- memoized subtype pairs.

Ephemeral lambdas require an operation-local unique ID and cannot be content-hashed reliably.

## 21.6 Compilation target

A useful first compiler target is an expression DAG with precomputed indices:

```ts
type CompiledExpr =
  | { kind: "always" }
  | { kind: "never" }
  | { kind: "mask"; required: bigint; excluded: bigint }
  | { kind: "union"; branches: readonly CompiledExpr[] }
  | { kind: "intersection"; members: readonly CompiledExpr[] }
  | {
      kind: "refinement";
      base: CompiledExpr;
      test: PreparedRefinement;
    };
```

Fuse adjacent static atoms and capabilities into masks. Preserve source mappings:

```ts
interface SourceMapEntry {
  readonly expressionId: string;
  readonly sourcePath: readonly number[];
}
```

so explanations can refer to original type syntax after optimization.

## 21.7 Clause compilation

For modest expressions, normalize to disjunctive clauses:

```ts
interface CompiledClause {
  readonly requiredMask: bigint;
  readonly excludedMask: bigint;
  readonly refinements: readonly PreparedRefinement[];
  readonly sourceExpression: TypeExpr;
}

interface CompiledTypePlan {
  readonly clauses: readonly CompiledClause[];
}
```

Matching succeeds when one clause succeeds.

Beware distributive blow-up:

\[
(A_1\lor B_1)\land\cdots\land(A_n\lor B_n)
\]

has \(2^n\) naive disjunctive clauses. Keep an expression DAG or introduce decision diagrams when expansion exceeds a budget.

## 21.8 Prepared refinements

Compilation against environment \(e\) can prepare predicates:

```ts
interface PreparedRefinement {
  readonly id: string;
  readonly expressionId: string;
  readonly cachePolicy: CachePolicy;
  test(reference: Reference): RefinementResult;
  fingerprint(reference: Reference): DependencyFingerprint;
}
```

Separate registry compilation from environment preparation:

```text
compile(TypeExpr, Registry) -> CompiledTemplate
prepare(CompiledTemplate, EnvironmentSnapshot) -> MatchPlan
```

This permits reuse of structural work across environment updates.

## 21.9 Direct matcher

The direct matcher needs:

```ts
interface MatchContext {
  readonly registry: RegistrySnapshot;
  readonly environment: EnvironmentSnapshot;
  readonly cache: MatchCache;
  readonly budget: EvaluationBudget;
  readonly explain: boolean;
}
```

Budget fields:

```ts
interface EvaluationBudget {
  readonly maxPredicateCalls: number;
  readonly maxEvidenceNodes: number;
  readonly deadline?: number;
}
```

Budget exhaustion should produce `unknown`, not false semantic evidence.

## 21.10 Subtype service

```ts
interface SubtypeService {
  isSubtype(left: TypeExpr, right: TypeExpr): boolean;
  compare(left: TypeExpr, right: TypeExpr):
    | "less"
    | "equal"
    | "greater"
    | "incomparable";
  explain(left: TypeExpr, right: TypeExpr): SubtypeExplanation;
}
```

Memoize ordered pairs by expression ID and registry version.

Keep `isNominalSubtype(atomA, atomB)` available separately. Debugging becomes easier when callers can distinguish nominal reachability from full expression inclusion.

## 21.11 Translator service

```ts
interface TranslationService {
  directCandidates(sourceAtom: string): readonly TranslatorPlan[];
  findMatches(
    source: Reference,
    request: CompiledTypePlan,
    options: TranslationPolicy,
  ): Promise<readonly Match[]>;
}
```

Do not make the core direct matcher know graph-search policy. The top-level acceptance matcher orchestrates direct and translated matching.

## 21.12 Dispatcher service

```ts
interface ActionDispatcher {
  actionsFor(input: DispatchInput): readonly ResolvedAction[];
  explain(input: DispatchInput): DispatchExplanation;
}
```

The dispatcher requests evidence from the matcher for candidate method signatures, computes maximal methods, applies preferences, and combines actions by stable ID.

## 21.13 Error taxonomy

Distinguish setup errors from runtime non-applicability.

### Registry errors

```text
duplicate atom
unknown supertype
nominal cycle
unknown capability
invalid refinement arguments
translator target mismatch
action-table cycle
preference cycle
```

### Runtime failures

```text
not a member
refinement false
translation not applicable
translation unknown
budget exhausted
ambiguous method
stale context
```

Setup errors should fail early. Runtime failures should be evidence or diagnostics, not thrown exceptions unless a declared contract is violated.

## 21.14 What can be left out?

For fewer than a few dozen types and rules, recursive expression evaluation plus maps is adequate. Add bitsets, interning, source maps, and compilation budgets only after semantics are stable. Keep the architectural service boundaries even when their first implementations are small functions.

## Exercises

1. **Architecture.** Draw module boundaries and dependency directions for the five services.
2. **Implementation.** Build and freeze a registry with nominal-cycle detection.
3. **Compilation.** Fuse an intersection of three static facts and one refinement into a plan.
4. **Complexity.** Construct an expression that causes exponential DNF expansion.
5. **Design.** Decide how registry snapshots interact with hot-reloaded plugins.
6. **Testing.** Verify that optimized plans and direct syntax evaluation agree over a finite model.

---

# 22. Performance, caching, and invalidation

## Learning objectives

After this chapter you should be able to:

1. build a cost model for presentation matching;
2. index candidates before invoking predicates;
3. choose cache keys that include semantic revisions and environment dependencies;
4. state the cache-soundness theorem and its assumptions;
5. decide when bitsets, clauses, DAGs, or BDDs are appropriate.

## 22.1 Measure the right workload

Let:

- \(n\): mounted presentation occurrences;
- \(q\): active input contexts, usually 0 or 1;
- \(m\): registered action methods;
- \(k\): translators reachable from a source atom;
- \(p\): expensive predicate calls;
- \(u\): environment updates per second.

A naive render-time design can perform:

\[
O(n(m+k+p))
\]

work per update. A compiled and indexed design aims for:

\[
O(n\cdot c_{static}) + O(candidates\cdot c_{predicate}),
\]

where static checks are bit operations and candidate sets are narrow.

## 22.2 Stage the matcher

Order checks from cheap and selective to expensive:

```text
1. context inactive? stop
2. source atom / static mask check
3. exact direct match
4. indexed cheap translator candidates
5. cached identity decision
6. dynamic capability and refinement predicates
7. expensive or asynchronous resolution only after activation
```

A predicate should not run for an occurrence whose atom cannot possibly satisfy any positive branch.

## 22.3 Positive indexing

For each compiled clause, select one positive index key:

```ts
interface ClauseIndexKey {
  readonly kind: "atom" | "capability" | "universal";
  readonly index: number;
}
```

Prefer the rarest statically known fact. A registry can collect approximate occurrence frequencies from development telemetry, but a fixed heuristic—most specific atom first—is often enough.

Action methods are similarly indexed by active table and subject fact.

## 22.4 Bitsets

With dense atom and capability indices:

```ts
const hasRequired =
  (facts & clause.requiredMask) === clause.requiredMask;

const hasExcluded =
  (facts & clause.excludedMask) !== 0n;
```

This makes static conjunction and exclusion fast and branch-light.

Bitsets are less helpful for:

- high-cardinality parameter values;
- arbitrary predicates;
- frequently changing dynamic capabilities;
- open-ended plugin universes without recompilation.

Use them for registry-snapshot facts, not every property.

## 22.5 Cache layers

### Expression cache

```text
(TypeExpr canonical ID, registry version) -> compiled template
```

### Prepared-plan cache

```text
(compiled template ID, preparation fingerprint) -> prepared plan
```

### Membership cache

```text
(type expression ID,
 identity namespace/key or occurrence identity,
 object revision,
 refinement dependency fingerprints,
 registry version) -> decision/evidence
```

### Subtype cache

```text
(left expression ID, right expression ID, registry version) -> relation
```

### Translation cache

Only pure translators should be cached automatically. Key by source identity/revision, translator ID, and environment dependencies. Do not cache `AbortSignal`-dependent failure as semantic non-applicability.

## 22.6 Cache soundness

Let \(F_p(r,e)\) be the fingerprint declared for predicate \(p\).

### Dependency completeness assumption

\[
F_p(r,e)=F_p(r',e')
\land r\approx r'
\Rightarrow
p(r,e)=p(r',e').
\]

This says equal fingerprints and identity imply equal predicate results.

### Theorem 22.1 — Membership cache soundness

Assume:

1. the registry version is equal;
2. the type-expression ID is equal;
3. every reused predicate satisfies dependency completeness;
4. static atom and capability facts are correct for the reference identity/revision;
5. cached translation decisions are reused only under their contracts.

Then reusing cached membership evidence yields the same Boolean membership result as reevaluation.

#### Proof sketch

Structural induction on the compiled expression. Static constructors depend only on equal registry facts. For each refinement node, dependency completeness gives equal predicate result. Union, intersection, and difference preserve equality of child results. ∎

The theorem exposes the risk: a missing dependency invalidates the argument.

## 22.7 Coarse versus fine invalidation

### Coarse

```text
environmentEpoch increments on any relevant store change
```

Advantages: simple and safe. Disadvantage: low reuse.

### Fine

```text
project revision
authorization epoch
workspace membership version
schema version
```

Advantages: high reuse. Disadvantage: more proof obligations.

Begin coarse. Refine only after measurement.

## 22.8 Weak maps and object-reference fallback

For objects without semantic identity, a `WeakMap<object, ...>` gives occurrence-instance caching without preventing garbage collection.

Primitive values need namespaced value keys. Beware unbounded maps for attacker-controlled strings; use operation-scoped caches or bounded LRU policies.

## 22.9 React render behavior

`isAcceptable(reference)` may be called on every render. Reduce churn by:

- compiling once per active request and registry version;
- exposing a stable matcher function;
- memoizing descriptor-derived static facts;
- subscribing only to relevant environment epochs;
- using `useSyncExternalStore` for coherent external snapshots;
- avoiding new reference wrapper objects when data is unchanged;
- virtualizing large occurrence collections.

Do not use `useMemo` as a correctness mechanism. React may discard memoized values; correctness must come from semantic caches or recomputation.

## 22.10 Decision diagrams

Normalizing arbitrary union/intersection/negation expressions to DNF can explode exponentially. Binary decision diagrams provide a canonical graph representation for Boolean functions under a fixed variable ordering [Bryant1986; Bryant1992].

Elixir's set-theoretic type implementation has publicly discussed moving beyond eager normal forms and optimizing lazy BDD-style representations as its type inference expanded [ElixirBDD; Elixir120]. This is a relevant modern implementation precedent.

PBUI adoption rule:

```text
use syntax DAGs and bitsets first
instrument normalization size
introduce BDDs only when measured expressions exceed budgets
```

The variable-ordering problem and dynamic refinements make BDDs a serious engineering commitment.

## 22.11 Benchmark design

Benchmark representative workloads:

1. 10,000 mounted references, exact atomic request;
2. 10,000 references, one static capability intersection;
3. 10,000 references, identity-cached refinement;
4. 1,000 action methods indexed by table and atom;
5. translator graph with branching and cycles;
6. environment epoch changes at interactive rates;
7. cold and warm caches;
8. explanation disabled and enabled.

Measure:

- median and tail latency;
- predicate call count;
- allocation count;
- cache hit ratio;
- compiled-plan size;
- UI commit duration.

A fast incorrect cache is worse than a slower correct matcher. Include differential correctness checks in benchmark fixtures.

## 22.12 What can be left out?

For ordinary screens, operation-scoped `Map` caches and atom-indexed rules are often enough. Bitsets and BDDs are not prerequisites. The essential performance pattern is to compile and index before invoking arbitrary predicates, and to make cache invalidation explicit.

## Exercises

1. **Cost model.** Estimate matcher calls for a screen with 2,000 occurrences and 60 action methods under naive and indexed designs.
2. **Proof.** Formalize dependency completeness for a permission refinement.
3. **Bug construction.** Omit one dependency and demonstrate an unsound cached acceptance.
4. **Implementation.** Add a per-input-context identity cache with commit revalidation.
5. **Benchmark.** Compare a `Set` prepared predicate with repeated array scanning.
6. **Research.** Implement a tiny reduced ordered BDD for Boolean atom expressions and compare node counts under two variable orders.

---

# 23. React integration, interaction, and accessibility

## Learning objectives

After this chapter you should be able to:

1. expose the semantic kernel through React without coupling it to rendering;
2. implement presentation occurrences and provider-local input contexts;
3. manage nested interactive elements and event precedence;
4. design keyboard and screen-reader behavior;
5. handle virtualization, concurrency, and server rendering.

## 23.1 Provider API

```ts
interface PbuiContextValue<V extends object, E, Verb> {
  readonly registry: RegistrySnapshot<V, E, Verb>;
  readonly environment: E;
  readonly activeRequest: ActiveRequest<V> | null;

  accept<T>(request: TypedAcceptRequest<T>): Promise<Accepted<T> | null>;
  abortAccept(reason?: string): void;
  probe(reference: PresentationReference<V>): ProbeResult;
  commit(reference: PresentationReference<V>, occurrenceId: string): void;
  actionsFor(reference: PresentationReference<V>): readonly Action<Verb>[];
  perform(verb: Verb): void;
}
```

The provider owns transient interaction state. Durable domain and layout state remain in the application store.

## 23.2 Environment snapshots

The environment should be narrow and intentionally versioned:

```ts
interface Environment {
  readonly snapshotId: number;
  readonly authorizationEpoch: number;
  readonly documents: DocumentReader;
  readonly projects: ProjectReader;
}
```

Do not pass an unrestricted Redux store if descriptors only need a few stable query methods. A narrow environment makes dependencies testable and supports alternate hosts.

## 23.3 Presentation component

```tsx
interface PresentationProps<R> {
  readonly reference: R;
  readonly children: React.ReactNode;
  readonly asChild?: boolean;
  readonly occurrenceId?: string;
  readonly disabled?: boolean;
  readonly description?: string;
}
```

The wrapper derives:

```ts
const probe = pbui.probe(reference);
```

Possible probe states:

```ts
type ProbeResult =
  | { kind: "ordinary" }
  | { kind: "acceptable"; preview: MatchPreview }
  | { kind: "resolvable"; preview: MatchPreview }
  | { kind: "rejected"; reason?: MatchFailure }
  | { kind: "unknown"; diagnostic?: string };
```

## 23.4 Event precedence

When an input context is active, primary activation normally means acceptance. When no context is active, primary activation belongs to the child component or default action.

```text
active acceptable context
  click / Enter / Space -> commit presentation

no active context
  preserve child's ordinary interaction

context menu gesture
  discover object actions
```

Nested native controls are difficult. A presentation wrapping a link or button should not turn every click on the inner control into acceptance without a deliberate policy.

Options:

- require `asChild` and compose handlers;
- use a dedicated activation gesture while accepting;
- let descendants opt out with `data-pbui-stop`;
- present only the semantic label, not the entire interactive region.

## 23.5 Nested presentations

Output can be semantically nested:

```tsx
<Presentation reference={projectRef}>
  <ProjectCard>
    <Presentation reference={ownerRef}>
      <OwnerChip />
    </Presentation>
  </ProjectCard>
</Presentation>
```

Pointer events should choose the innermost applicable presentation by default. Event propagation already supplies a candidate order, but explicit occurrence registration makes behavior testable.

A modifier can request outer presentation selection, or a disambiguation menu can list both semantic paths.

## 23.6 Focus strategy

Making thousands of occurrences permanently tabbable is unusable. Strategies include:

### Contextual tab stops

Only acceptable occurrences receive `tabIndex=0` during an input context. This can still create many stops.

### Roving focus

One occurrence per presentation region has `tabIndex=0`; arrow keys move among candidates.

### Semantic navigator

A command opens a searchable list of acceptable objects, synchronized with visual occurrences.

### Existing-control integration

Table cells and tree items retain their native composite-widget keyboard model; PBUI acceptance hooks into their activation.

Provide more than one path. Pointer sensitivity alone is inaccessible.

## 23.7 Announcements

When an input context begins:

```text
Choose a field for the horizontal axis. 12 visible choices.
Press Escape to cancel.
```

When focus reaches a candidate:

```text
Temperature, field, acceptable.
```

When asynchronous resolution begins:

```text
Resolving project p-7.
```

When it fails:

```text
Project could not be resolved. The selection remains active.
```

Use an appropriately configured `aria-live` region. Avoid announcing every render-time applicability fluctuation.

## 23.8 Menus

The object menu receives actions already resolved by semantic dispatch. It must then implement ordinary accessible menu behavior:

- focus enters the menu;
- arrow-key navigation;
- Escape closes and restores focus;
- disabled reasons are exposed;
- destructive actions are marked and may require confirmation;
- menu position does not determine semantic context.

A command palette can expose the same resolved actions without pointer use.

## 23.9 Virtualization

A virtualized table may render only 50 of 100,000 fields or rows. An input context over mounted presentations sees only those 50 unless the application supplies a semantic index.

Two modes should be explicit:

```ts
type SearchScope =
  | "mounted-occurrences"
  | "registered-domain-index";
```

Mounted mode means “choose from what is currently visible.” Domain-index mode can open a virtualized semantic picker backed by data, while still highlighting mounted occurrences of the same identities.

## 23.10 Concurrent rendering

React may render speculatively. Do not mutate global occurrence registries during render. Register mounted occurrences in layout/effect phases with stable IDs, and make registration idempotent.

Event handlers must read the current context token, not a stale closure alone. `useEvent`-style stable callbacks or refs can bridge current state.

The semantic matcher should be pure and safe to call during render. Asynchronous translation begins only after committed user activation.

## 23.11 Server rendering and hydration

On the server:

- semantic labels and DOM annotations can render;
- no active client input context exists;
- occurrence IDs must hydrate consistently or be regenerated without becoming domain identities;
- environment-sensitive actions may be omitted until client authorization state is available.

Do not serialize arbitrary object references or closures into HTML.

## 23.12 Styling contract

Expose semantic states through stable attributes:

```html
<span
  data-pbui="presentation"
  data-pbui-type="field"
  data-pbui-state="acceptable"
  data-pbui-match="direct"
>
```

CSS can style without coupling to internal class names. Do not communicate applicability by color alone; add cursor, outline, text, icon, or status changes.

## 23.13 What can be left out?

A first implementation can support pointer click, Enter/Space, Escape, a live prompt, and context menus. Roving focus, semantic indexing, nested disambiguation, and asynchronous pending states can follow. Accessibility is not optional; the breadth of interaction modes is negotiable.

## Exercises

1. **Implementation.** Build a `Presentation` wrapper that composes child handlers without double activation.
2. **Accessibility.** Design focus behavior for a chart containing 300 marks.
3. **Nested semantics.** Specify how users select an owner chip versus its enclosing project card.
4. **Virtualization.** Add a domain-index search mode to a virtualized field table.
5. **Concurrency.** Identify a render-phase mutation bug and redesign it using effects.
6. **Testing.** Write keyboard tests for start, navigate, accept, abort, and focus restoration.

---
# 24. Persistence, plugins, and open-world evolution

## Learning objectives

After this chapter you should be able to:

1. decide which semantic artifacts are serializable;
2. version registry names and persisted type expressions;
3. add plugins without mutating active snapshots;
4. handle open-world negation and method ambiguity;
5. secure plugin declarations and persistence boundaries.

## 24.1 Data versus executable code

The type algebra is deliberately data-shaped:

```json
{
  "kind": "intersection",
  "members": [
    { "kind": "atom", "id": "core/project" },
    {
      "kind": "refinement",
      "id": "core/owned-by",
      "args": { "userId": "u-7" },
      "base": { "kind": "atom", "id": "core/project" }
    }
  ]
}
```

Named expressions can be serialized because executable predicate bodies remain in the registry and the data contains only stable IDs and arguments.

Arbitrary lambdas cannot be serialized faithfully. A string containing source code is not a safe or reliable substitute: closures, module dependencies, authority, and language versions are missing.

## 24.2 Serialization classes

| Artifact | Portable? | Conditions |
|---|---:|---|
| atomic type reference | yes | stable namespaced ID |
| union/intersection/difference | yes | children portable |
| named refinement instance | yes | args schema and registry definition |
| ephemeral lambda | no | operation-local only |
| semantic identity | usually | namespace and stable key |
| revision | sometimes | meaningful in destination |
| match evidence | partially | redact values; versions may be local |
| translator path | descriptively | translator IDs exist in destination |
| action verb | yes | application command schema |
| promise continuation | no | process-local control state |

## 24.3 Namespacing

Use globally coherent registry IDs:

```text
core/project
core/inspectable
analytics/field-of-document
plugin.acme/exportable
```

Do not let two plugins silently claim `project`. Namespace aliases can support ergonomic local names, but persisted data should use canonical IDs.

## 24.4 Versioning definitions

A stable name does not guarantee stable meaning. Refinement `core/writable-document` can change after policy revisions.

Version options:

```text
core/writable-document@2
```

or registry metadata:

```ts
interface DefinitionVersion {
  readonly id: string;
  readonly semanticVersion: number;
}
```

A persisted expression stores the expected semantic version or the registry bundle hash. Import then:

- accepts exact compatibility;
- runs a migration;
- marks the expression unresolved;
- rejects it with a precise diagnostic.

## 24.5 Schema migrations

Migrations are transformations between serialized syntax versions:

```ts
interface TypeExpressionMigration {
  readonly from: number;
  readonly to: number;
  migrate(input: unknown): unknown;
}
```

Migrations should be:

- deterministic;
- pure;
- tested on historical fixtures;
- idempotent at the target version;
- separate from application command execution.

Validate after every migration step.

## 24.6 Plugin registry construction

Plugins contribute declarations to a builder:

```ts
interface PbuiPlugin {
  readonly id: string;
  readonly version: string;
  register(builder: RestrictedRegistryBuilder): void;
}
```

The host:

1. starts from a frozen base snapshot;
2. creates a new builder or persistent derivative;
3. applies plugin declarations through a restricted capability;
4. validates names, cycles, schemas, and preferences;
5. freezes a new registry version;
6. switches new contexts to the new snapshot.

Active contexts either retain their snapshot or are explicitly restarted.

## 24.7 Open-world subtype effects

Adding a new atom beneath an existing supertype extends the supertype denotation:

```text
plugin adds ForecastProject ≤ Project
```

Existing positive expressions remain monotone in a useful sense: their denotations may gain new members, but registered existing references do not become invalid merely because of the new subtype.

Negation is different:

```text
not Archived
```

Its denotation depends on the whole universe. Therefore compiled complements are registry-version specific.

Base-relative difference remains local:

```text
Project \ Archived
```

but the extension of `Project` can still add new members. That is normally intended.

## 24.8 Open-world methods

A plugin can introduce a new action method more specific than an existing method. This changes dispatch for matching values.

This is ordinary open-method behavior, but it can surprise application owners. Support policies:

```ts
type ExtensionPolicy =
  | "open"
  | "namespaced-only"
  | "host-approval"
  | "sealed";
```

Sealed actions reject plugin overrides. Host-approval requires an explicit preference or authorization for a plugin method to shadow core behavior.

## 24.9 Trust and sandboxing

A registry plugin can execute predicate, translator, label, and action-construction code. In ordinary JavaScript, this is arbitrary code execution with the authority of its host realm.

Schema validation does not sandbox functions.

Untrusted plugins require a real isolation boundary:

- separate origin or iframe;
- worker with restricted messaging;
- server-side process isolation;
- capability-based API;
- declarative guard and action languages rather than arbitrary functions.

Do not describe a plugin as “safe” merely because its manifest is JSON.

## 24.10 Remote evaluation

A serializable type expression can be sent to a server only if the server recognizes the same semantic definitions. The server should not trust client-provided evidence.

Possible protocol:

```ts
interface RemoteTypeRequest {
  readonly registryContract: string;
  readonly expression: SerializedTypeExpr;
  readonly subjectIdentity: SemanticIdentity;
}
```

The server resolves the identity, evaluates its own predicates and authorization, and returns a result. Client evidence can be included as a performance hint or diagnostic correlation, never as proof of authority.

## 24.11 Portable subject links

As Chapter 19 described, portable workspaces should encode sharing topology, not runtime binding IDs. The same principle applies to type definitions:

```text
persist semantic relation and stable names
reconstruct runtime identities on import
```

## 24.12 Failure-tolerant import

A workbench can remain usable when a plugin type is missing:

```ts
type LoadedExpression =
  | { kind: "resolved"; expression: TypeExpr }
  | {
      kind: "unresolved";
      serialized: unknown;
      missingDefinitions: readonly string[];
    };
```

Unresolved commands should not execute. The UI can preserve and display their metadata until the plugin is restored.

## 24.13 What can be left out?

A closed application can freeze one registry at startup and persist only atomic IDs and command verbs. Plugin snapshots, semantic versions, and unresolved expressions become necessary only when extension and long-lived documents are product requirements.

## Exercises

1. **Serialization.** Classify ten PBUI artifacts as portable or process-local.
2. **Migration.** Write a migration from `owner: string` to `{ userId: string }` refinement arguments.
3. **Open world.** Show how adding one atom changes a complement type.
4. **Plugin design.** Define a restricted builder that allows new actions but not new identity implementations for core atoms.
5. **Security.** Threat-model an untrusted plugin predicate.
6. **Remote semantics.** Design a protocol that lets a server re-evaluate a client selection without trusting client evidence.

---

# 25. Testing laws and proof obligations

## Learning objectives

After this chapter you should be able to:

1. organize tests by algebraic laws and semantic contracts;
2. use finite models for differential testing;
3. test state machines and race conditions;
4. distinguish verified assumptions from untested declarations;
5. build a practical assurance plan without a proof assistant.

## 25.1 Test the algebra, not only examples

Example tests answer:

```text
Does this project match this selector?
```

Law tests answer:

```text
Does intersection behave commutatively for every generated fixture?
Does identity remain transitive?
Does optimized matching agree with reference semantics?
```

Both are required.

## 25.2 Test layers

### Unit tests

Test one declaration or constructor:

- atom descriptor labels;
- refinement predicate;
- translator body;
- identity key;
- expression normalization.

### Algebraic property tests

Test:

- union/intersection commutativity;
- associativity;
- idempotence;
- absorption;
- difference disjointness;
- subtype reflexivity and transitivity;
- identity equivalence laws.

### Differential tests

Compare optimized implementation with a simple reference interpreter over finite generated universes.

### Model-based state-machine tests

Generate sequences of:

```text
start, commit, abort, replace,
async-resolve, unmount,
link, unlink, set-subject
```

and compare implementation state with a small model.

### Integration and accessibility tests

Exercise React event behavior, focus, announcements, menus, and virtualization.

### Persistence tests

Round-trip schemas across historical versions and verify semantic topology.

## 25.3 Finite denotation oracle

For testing, choose a finite universe:

```ts
const universe: readonly Reference[] = [
  project1,
  project2,
  archivedProject,
  workspace1,
];
```

Interpret each expression as a `Set` of reference IDs. Then:

```ts
function semanticallyEquivalent(a: TypeExpr, b: TypeExpr): boolean {
  return equalSets(denote(a, universe), denote(b, universe));
}
```

This is not proof over every universe, but it is an excellent differential oracle for normalization and compiler defects.

## 25.4 Expression generators

A recursive generator should control depth and avoid pathological size:

```ts
function typeExprArbitrary(maxDepth: number): Arbitrary<TypeExpr> {
  if (maxDepth === 0) return atomArbitrary;
  return oneof(
    atomArbitrary,
    tuple(child, child).map(([a, b]) => and(a, b)),
    tuple(child, child).map(([a, b]) => or(a, b)),
    tuple(child, child).map(([a, b]) => difference(a, b)),
  );
}
```

When a property fails, shrink to a small counterexample. Canonical pretty-printing makes failures readable.

## 25.5 Subtype law suite

```ts
property("reflexive", expr, t => subtype(t, t));

property("transitive", expr3, ([a, b, c]) => {
  if (subtype(a, b) && subtype(b, c)) {
    expect(subtype(a, c)).toBe(true);
  }
});

property("intersection elimination", expr2, ([a, b]) => {
  expect(subtype(and(a, b), a)).toBe(true);
  expect(subtype(and(a, b), b)).toBe(true);
});
```

Do not generate only syntax. Generate registries and finite denotations too, or the tests may merely confirm the implementation against itself.

## 25.6 Identity law suite

Generate alternate representations of the same entities:

```text
<Project> p7
<ProjectId> "p7"
<ProjectSummary> { id: "p7", ... }
```

Check equivalence laws and domain-specific expectations. Include malformed and missing identities.

Mutation testing is valuable: deliberately remove the identity namespace, alter one composite-key component, or return a mutable title. Good tests should fail.

## 25.7 Refinement obligations

For each named refinement, test:

- positive and negative fixtures;
- determinism under equal dependencies;
- dependency completeness under known state changes;
- termination within an expected budget;
- explanation redaction;
- argument schema validation.

A dependency-mutation harness can change one environment field at a time and verify that either the predicate result is unchanged or the fingerprint changes.

## 25.8 Translator obligations

For each translator:

- source schema accepted;
- every success satisfies target schema;
- `applicable=false` implies translate is not invoked, if that is the contract;
- identity-preserving claim holds;
- totality claim holds over generated valid sources;
- pure claim survives repeated evaluation;
- cancellation prevents late side effects;
- cost and priority produce expected path selection.

Graph-level tests cover cycles, limits, equal-cost ambiguity, and deterministic explanation.

## 25.9 Dispatch obligations

Test:

- applicability of each signature component;
- componentwise specificity;
- unique maximal selection;
- ambiguity detection;
- preference acyclicity;
- action-ID shadowing;
- table inheritance;
- registration-order independence.

A useful metamorphic test shuffles method registration order and expects the same resolved actions.

## 25.10 Input-context state machine tests

Model at-most-once settlement:

```ts
expect(resolutionCount(contextId)).toBeLessThanOrEqual(1);
```

Race scenarios:

- click then Escape before async completion;
- context replacement then old translator resolves;
- provider unmount while active;
- environment revision changes between hover and click;
- double click;
- nested event bubbling commits inner and outer occurrences.

Fake schedulers make timing deterministic.

## 25.11 Link-model tests

Generate arbitrary sequences of:

```text
create view
create placement
link groups
set subject role
unlink view
delete view
round-trip persistence
```

After every operation assert:

```text
every view has one existing binding
linked views read one subject map
unlink preserves current subject
unused binding policy holds
placements reference existing views
```

## 25.12 Accessibility tests

Automated tests can cover:

- roles and names;
- keyboard activation;
- Escape;
- focus restoration;
- disabled states;
- live-region text;
- menu navigation.

Manual testing remains necessary for screen-reader experience, visual focus, nested controls, and large virtualized surfaces.

## 25.13 Proof-obligation register

Maintain a table in the repository:

| Component | Claim | Evidence | Status |
|---|---|---|---|
| identity | equivalence relation | property tests | checked on generators |
| subtype core | sound for supported grammar | proof sketch + differential tests | reviewed |
| refinement X | dependency complete | mutation tests | checked |
| translator Y | identity preserving | property tests | checked |
| dispatcher | registration-order independent | shuffle tests | checked |
| link reducer | coherence preserving | proof + model tests | checked |

This avoids saying “formally verified” when only a subset is proved or tested.

## 25.14 Mechanized proof boundary

A proof assistant can verify the pure calculus and state machines. It cannot automatically prove an arbitrary JavaScript refinement correctly implements business policy. Those functions remain axioms or must be re-expressed in a verified language.

Mechanization is most valuable for:

- algebraic normalization;
- subtype rules;
- matcher soundness;
- dispatch maximality;
- input-context settlement;
- link coherence.

## 25.15 What can be left out?

A small project can use example tests plus a handful of central law tests. The most valuable additions are differential testing for optimized matching, registration-order shuffling for dispatch, dependency mutation for caches, and model-based race tests.

## Exercises

1. **Property testing.** Write generators for finite registries and type expressions.
2. **Differential testing.** Compare a bitset matcher with a set-based reference interpreter.
3. **Mutation testing.** Design mutations that should break identity, refinement, and translator contracts.
4. **State machine.** Generate races between commit, abort, replace, and async completion.
5. **Assurance.** Create a proof-obligation register for a feature in your project.
6. **Critical.** Explain why passing 10,000 generated tests is not a proof of transitivity.

---

# 26. Explanations, authorization, and observability

## Learning objectives

After this chapter you should be able to:

1. turn evidence trees into useful developer and user explanations;
2. separate semantic applicability from security authorization;
3. redact sensitive evidence;
4. instrument matching without collecting domain secrets;
5. diagnose rule conflicts and performance regressions.

## 26.1 Why explanation is part of the architecture

Once behavior is selected indirectly, debugging by reading one component's callback no longer works. Developers need to answer:

```text
Why is this occurrence highlighted?
Why is that action missing?
Which translator won?
Which predicate failed?
Why are these views linked?
Which cache entry was reused?
```

Evidence-producing matching makes these questions answerable without reenacting internal control flow from logs.

## 26.2 Explanation tree

```ts
interface ExplanationNode {
  readonly title: string;
  readonly outcome: "success" | "failure" | "unknown";
  readonly details?: Readonly<Record<string, unknown>>;
  readonly children?: readonly ExplanationNode[];
  readonly sensitivity?: "public" | "developer" | "secret";
}
```

Example:

```text
Archive action: unavailable
└─ subject requires Project ∧ Archivable
   ├─ Project: yes
   └─ Archivable: no
      └─ policy predicate: denied
```

The user-facing message may be only:

```text
You cannot archive this project.
```

The developer view can include policy version and dependency epochs without exposing private data.

## 26.3 Positive and negative explanations

Positive explanations are useful for surprising acceptance:

```text
This project ID is selectable because it resolves to project p-7.
```

Negative explanations help disabled actions:

```text
Link unavailable because this tile has no document subject.
```

Avoid turning every ordinary rejected occurrence into visual noise. Explanations can appear on focus, request, or in a semantic inspector.

## 26.4 Authorization is not client evidence

Client-side refinements improve UX:

```text
show archive action only when permission snapshot says yes
```

They do not authorize server mutation. The server must:

1. authenticate the principal;
2. resolve stable subject identities;
3. validate command schema;
4. re-evaluate current authorization and state;
5. execute transactionally;
6. return an auditable result.

A client evidence object can correlate why the UI offered the action, but the server must not accept it as proof.

## 26.5 Information leaks

A failed predicate may reveal:

```text
project exists but belongs to another customer
user lacks administrator role
confidential document is archived
remote object has a particular title
```

Classify diagnostics:

```ts
type DiagnosticVisibility =
  | "user-safe"
  | "authenticated-developer"
  | "server-log-only";
```

Refinements and translators should return public failure codes separately from private diagnostics.

## 26.6 Semantic inspector

A development tool can inspect the occurrence under the pointer:

```text
Occurrence
  id: occurrence-182
  atom: field
  label: Temperature
  identity: field:[doc-7,temperature]
  revision: 14

Active request
  FieldOf(doc-7) ∧ Quantitative

Match
  direct: yes
  field-of: yes
  quantitative: yes
  cache: identity hit

Actions
  inspect — descriptor
  map-to-x — chart-encoding table
  add-to-watchlist — global rule
```

This is analogous in spirit to object-centric inspectors in systems such as Glamorous Toolkit and Portal, where domain values can expose contextual views and commands [GlamorousToolkit; Portal].

## 26.7 Tracing

A match trace can use spans:

```text
pbui.match
  expression.id
  source.atom
  result
  direct.duration
  predicate.count
  cache.hits
  translation.paths.explored
```

Do not record full values by default. Prefer namespaced identities hashed or sampled according to privacy policy.

## 26.8 Metrics

Useful aggregate metrics:

- direct match latency;
- p95 predicate count per probe;
- prepared-selector reuse;
- translation ambiguity count;
- stale commit revalidation count;
- action dispatch ambiguity count;
- active-context abort rate;
- cache hit ratio;
- registry compile size and duration;
- unresolved persisted type definitions;
- link/unlink operations and orphan cleanup failures.

Metrics should diagnose architecture, not surveil users.

## 26.9 Deterministic logs

Use stable IDs and canonical expression printing:

```json
{
  "event": "pbui.dispatch.ambiguous",
  "registryVersion": 18,
  "subjectAtom": "core/project",
  "methodIds": [
    "core/editable-project-action",
    "core/owned-project-action"
  ]
}
```

Avoid logging registration order, memory addresses, or whole closure source as identifiers.

## 26.10 Replay

A replayable interaction record contains:

```ts
interface InteractionRecord {
  readonly registryContract: string;
  readonly requestExpression: SerializedTypeExpr;
  readonly sourceIdentity?: SemanticIdentity;
  readonly sourceAtom: string;
  readonly selectedTranslatorIds: readonly string[];
  readonly resultingVerb?: unknown;
}
```

Replay still requires compatible data snapshots. It is not a substitute for event sourcing unless the broader application model is designed that way.

## 26.11 Explanation soundness

An explanation should correspond to actual evaluator evidence. Do not regenerate a plausible reason from current state after the fact; state may have changed.

### Property

If an explanation node claims that refinement \(p\) succeeded, the associated match evidence must contain a successful \(p\) node with the same arguments and validity token.

This can be tested structurally.

## 26.12 What can be left out?

A first version can provide a development console trace and safe disabled reasons. A semantic inspector and production metrics become important as rules, plugins, and translations grow. Authorization separation and diagnostic redaction are required whenever sensitive operations or data exist.

## Exercises

1. **Explanation.** Render a match evidence tree as concise user text and detailed developer text.
2. **Security.** Identify three information leaks in naive refinement failure messages.
3. **Observability.** Design privacy-preserving metrics for matcher performance.
4. **Testing.** Verify that every explanation claim is backed by an evidence node.
5. **Architecture.** Specify server-side validation for an `archiveProject` verb selected through PBUI.
6. **Tooling.** Design a semantic inspector panel for nested presentations.

---
# Part V — Choosing a system

# 27. Four coherent feature profiles

## Learning objectives

After this chapter you should be able to:

1. choose a coherent subset of the architecture;
2. understand the operational and conceptual cost of each feature;
3. recognize when a project should stop adding machinery;
4. plan migration without requiring the final research-oriented profile.

## 27.1 Why profiles matter

The full architecture is a design space, not a mandatory checklist. A system that implements half of every advanced idea is often worse than one that implements a smaller closed set well.

This chapter defines four coherent profiles. Each profile has a stable semantic story, test strategy, and upgrade path.

## 27.2 Profile A — Nominal presentations

### Features

- discriminated presentation references;
- exact atomic type matching;
- descriptor labels and local actions;
- provider-local `accept` and abort;
- optional one-step conversions;
- JavaScript object or primitive fallback identity;
- pointer and keyboard activation.

### Public form

```ts
await pbui.accept({
  types: "field",
  filter: ref => ref.value.documentId === activeDocumentId,
  prompt: "Choose a field",
});
```

### Semantic claim

The request accepts references whose exact atom is in a finite requested set and whose filter returns true. Conversions are tried in documented order.

### Strengths

- small implementation;
- easy debugging;
- low conceptual overhead;
- excellent for proving product value;
- compatible with ordinary React patterns.

### Limitations

- no reusable semantic identity across representations;
- repeated filters and actions;
- registration-order conversion ambiguity;
- limited explanation;
- no compound type algebra.

### Stop here when

The application has fewer than roughly a few dozen presentation types, conversions are rare, and most actions are naturally local.

## 27.3 Profile B — Practical semantic PBUI

### Features

Everything in Profile A, plus:

- explicit semantic identity and revisions;
- named and ephemeral prepared selectors;
- operation-scoped identity caching;
- direct typed translators with source/target indexes;
- selector-driven action rules and action tables;
- commit revalidation;
- document-subject binding IDs;
- evidence summaries for diagnostics.

### Public form

```ts
const ActiveOwnedProject = selector(Project, {
  id: "active-owned-project",
  cache: "identity",
  prepare(environment) {
    const allowed = new Set(
      environment.projects
        .filter(p => !p.archived && p.ownerId === environment.userId)
        .map(p => p.id),
    );
    return project => allowed.has(project.id);
  },
});
```

### Semantic claim

Selectors are predicates over typed references in one logical environment snapshot. Identity caches are valid under declared revision dependencies. Translation remains direct and explicit.

### Strengths

- solves most practical duplication and linking problems;
- retains straightforward runtime model;
- supports arbitrary lambdas with performance discipline;
- introduces few abstract type constructors;
- easy incremental migration from an existing PBUI.

### Limitations

- subtype and specificity remain mostly nominal or selector-specific;
- compound contexts are less inspectable;
- method ambiguity may still use priorities;
- persistent selector composition is limited.

### Recommended default

This is the recommended target for the current PBUI before adopting the complete algebra. It captures most user-visible value and establishes the right identity and lifecycle boundaries.

## 27.4 Profile C — Algebraic semantic interfaces

### Features

Everything in Profile B, plus:

- atoms, capabilities, and nominal subtype DAG;
- union, intersection, and base-relative difference;
- named parameterized refinements;
- semantic subtype service for a documented fragment;
- evidence-producing direct matching;
- costed translator paths;
- multimethod action signatures and ambiguity detection;
- compiled plans, static fact masks, and subtype caches;
- portable type expressions.

### Public form

```ts
const ActiveInspectableProject = and(
  Project,
  Inspectable,
  difference(Project, Archived),
);

const project = await pbui.accept({
  type: ActiveInspectableProject,
});
```

### Semantic claim

Type expressions denote sets of references. Subtyping is semantic inclusion for the supported expression fragment. Successful matching returns evidence whose accepted reference belongs to the requested denotation.

### Strengths

- compositional type vocabulary;
- principled action specificity;
- reusable and explainable requests;
- strong plugin and persistence story;
- mathematical laws guide optimization and testing.

### Limitations

- larger implementation and teaching burden;
- opaque refinements constrain subtype completeness;
- expression normalization needs budgets;
- open-world evolution needs version discipline.

### Stop here when

Most research-oriented benefits are achieved without introducing unrestricted complement, recursive types, theorem-prover integration, or speculative asynchronous membership.

## 27.5 Profile D — Research-oriented semantic runtime

### Features

Everything in Profile C, potentially plus:

- unrestricted negation with registry-snapshot universes;
- recursive and parametric type constructors;
- BDD or automata-based subtype reasoning;
- three-valued or effectful applicability;
- asynchronous staged translation;
- declarative guard language with implication solver;
- proof-carrying evidence checked by a small kernel;
- machine-checked metatheory;
- distributed registry contracts;
- capability-secure plugin execution.

### Semantic claim

The exact claim depends on the chosen formalization. It may include sound and complete subtype decision for a richer grammar, mechanically verified matcher soundness, or distributed proof checking.

### Strengths

- research platform;
- powerful static and runtime explanation;
- supports large, extensible semantic languages;
- can produce publishable engineering and formal results.

### Risks

- implementation can become a programming language project;
- BDD and recursive-type engineering is nontrivial;
- declarative predicates may restrict host-language ergonomics;
- proof maintenance competes with product work;
- end users may not benefit from the deepest machinery.

### Adopt only when

The semantic interface engine is itself a strategic product, research artifact, or platform used by many independently developed applications.

## 27.6 Feature matrix

| Feature | A | B | C | D |
|---|:---:|:---:|:---:|:---:|
| tagged references | ✓ | ✓ | ✓ | ✓ |
| exact acceptance | ✓ | ✓ | ✓ | ✓ |
| semantic identity | optional | ✓ | ✓ | ✓ |
| prepared arbitrary predicates | — | ✓ | ✓ | ✓ |
| named refinements | — | limited | ✓ | ✓ |
| nominal subtype DAG | — | optional | ✓ | ✓ |
| union/intersection/difference | — | — | ✓ | ✓ |
| direct translators | limited | ✓ | ✓ | ✓ |
| path search | — | — | optional | ✓ |
| selector action rules | — | ✓ | ✓ | ✓ |
| multimethod specificity | — | — | ✓ | ✓ |
| evidence trees | — | summary | ✓ | ✓ |
| BDD/recursive types | — | — | — | optional |
| machine proofs | — | — | proof sketches | optional |

## 27.7 Decision questions

Choose the lowest profile that answers “yes” to the important questions.

### Identity pressure

- Does one domain object appear in several representations?
- Must selection highlight all occurrences of the same object?
- Do immutable updates recreate objects?

If yes, add semantic identity.

### Predicate pressure

- Are selection predicates expensive?
- Do they recur across workflows?
- Must they be explained or persisted?

If yes, add prepared and named refinements.

### Composition pressure

- Do requirements frequently say “A or B,” “A and capability C,” or “A except D”?
- Are nominal type names proliferating combinatorially?

If yes, add the algebra.

### Dispatch pressure

- Do plugins or contexts contribute actions?
- Do actions depend on multiple objects?
- Is registration-order resolution causing bugs?

If yes, add multimethod specificity.

### Research pressure

- Must subtype checking be complete for negation-rich expressions?
- Must proofs be machine-checked?
- Are recursive semantic types central?

If yes, investigate Profile D.

## Exercises

1. **Assessment.** Place the current PBUI in one profile and justify every feature assignment.
2. **Planning.** Define a Profile B milestone with no algebraic type expressions.
3. **Critical.** Identify one Profile C feature that would not benefit your product.
4. **Costing.** Estimate implementation, documentation, and maintenance cost for moving one profile upward.
5. **Architecture.** Specify an API facade that hides Profile C complexity from Profile A users.

---

# 28. Alternative architectures

## Learning objectives

After this chapter you should be able to:

1. compare presentation typing with other UI and programming architectures;
2. choose simpler alternatives when semantic types are not the central problem;
3. combine PBUI with normalized stores, statecharts, schemas, and command buses;
4. recognize when a rule engine or query language is a better foundation.

## 28.1 Component-owned callbacks

The conventional React model is:

```tsx
<FieldChip onInspect={...} onMapToX={...} />
```

Use it when behavior is local and explicit. It has excellent traceability: follow the callback. It becomes cumbersome when many visually unrelated occurrences must acquire the same contextual operations.

PBUI should complement rather than eliminate local callbacks. A slider's drag behavior is not improved by semantic dispatch merely because its value is meaningful.

## 28.2 Classical object-oriented inheritance

One can define:

```ts
class InspectableProject extends Project {
  inspect() { ... }
}
```

This bundles representation and behavior. It works when:

- objects are class instances;
- one hierarchy fits the domain;
- behavior is stable and intrinsic;
- cross-cutting contexts are few.

It performs poorly for normalized JSON data, orthogonal capabilities, environment-dependent permission, and multi-argument actions. Mixins and traits alleviate some issues, but do not by themselves provide input contexts or output semantics.

## 28.3 Visitor pattern

A visitor centralizes operations over a closed tagged union:

```ts
visit(reference, {
  project: ...,
  field: ...,
  document: ...,
});
```

Visitors are excellent for exhaustive processing when the set of variants is closed. They are less convenient when new plugins add types or new contexts add operations independently. PBUI's action methods favor open operations and potentially open types, accepting the corresponding ambiguity and versioning complexity.

## 28.4 Normalized entity stores

A normalized store maps stable IDs to entities and lets many components observe one node. Fulcro's normalization and ident model is a strong example [FulcroBook].

Normalization solves:

- shared entity identity;
- update propagation;
- graph-shaped client state;
- deduplication.

It does not by itself solve:

- semantic presentation roles;
- input contexts;
- action discovery;
- translation among representations;
- view subject linkage distinct from entity identity.

PBUI should use normalized identity where available rather than duplicate it.

## 28.5 Command bus

A command bus executes serializable commands:

```ts
commandBus.dispatch({
  type: "archiveProject",
  projectId,
});
```

This is complementary. PBUI discovers arguments and applicable commands; the bus validates and executes them. Do not move transactional effects into presentation descriptors.

## 28.6 Statecharts

Statecharts model multi-stage workflows, concurrency, and cancellation. They are a better foundation than nested promises for complex tools:

```text
idle
  → selectingSource
  → selectingTarget
  → confirming
  → executing
  → success/error
```

PBUI supplies semantic selection events to the statechart. The statechart owns workflow progression. For simple one-argument acceptance, the smaller state machine in Chapter 18 is enough.

## 28.7 Entity-component systems

An entity-component system attaches orthogonal components such as `Inspectable`, `DocumentBacked`, or `Selected` to entity IDs. This maps naturally to capabilities and can make bitset matching extremely efficient.

Use an ECS when the whole application is already organized around dense entities and systems. For ordinary object graphs and server data, introducing an ECS solely for UI capabilities may be excessive.

## 28.8 Rule engines and Datalog

A rule engine can express:

```text
archivable(Project, User) :-
  owns(User, Project),
  not archived(Project),
  role(User, admin).
```

Datalog-like systems offer declarative joins, recursion, explanation provenance, and incremental evaluation. They may be superior when action applicability is primarily relational across many entities rather than type-shaped.

A PBUI integration can ask the rule engine for capabilities and evidence. The type algebra then remains the interface layer over rule-derived facts.

Costs include a second query language, data synchronization, negation semantics, and operational complexity.

## 28.9 Schema validators

ArkType, Zod, Valibot, io-ts, JSON Schema, Malli, and Clojure spec validate data shapes or predicates. Malli in particular demonstrates data-driven schemas and registries, while Clojure spec combines predicates, composition, explanation, and generation [Malli; ClojureSpec].

These systems can implement representation validation and some refinements. They do not generally provide semantic object identity, input contexts, action dispatch, or view bindings.

Prefer integration over reimplementation of structural validation.

## 28.10 Pattern matching

Languages and libraries with algebraic pattern matching can express applicability clearly:

```ts
match(reference)
  .with({ type: "project", value: { archived: false } }, ...)
```

Pattern matching is excellent for local closed-case logic. Presentation type expressions make reusable patterns into runtime values that can be stored, composed, indexed, and compared.

A restricted guard AST can compile to a pattern-matching engine.

## 28.11 Signals and reactive derivations

Signals or selectors can derive `isArchivable(projectId)` reactively. They solve dependency tracking and incremental recomputation.

PBUI can use signals as refinement implementations:

```ts
test(project) {
  return archivableSignal(project.id).get();
}
```

The signal graph can supply revision tokens. Signals do not define subtype algebra or action specificity by themselves.

## 28.12 Attribute grammars and incremental computation

A semantic output tree could propagate inherited context and synthesize facts in a way reminiscent of attribute grammars. Incremental-computation systems can update only affected matches after state changes.

This is relevant for very large semantic surfaces, but ordinary React state and indexed caches are simpler for most applications.

## 28.13 Full dependent or refinement language

One could embed Lean, Agda, Idris, or a theorem-prover-generated kernel and represent rich dependent propositions. This is appropriate when proofs are the product or safety requirements justify the cost.

For a web UI, most predicates ultimately depend on dynamic server state and unverified JavaScript. A small proof-oriented runtime with explicit assumptions often provides a better cost-benefit ratio.

## 28.14 Choosing by problem shape

| Primary problem | Prefer |
|---|---|
| local widget behavior | callbacks/components |
| shared entity updates | normalized store |
| multi-stage workflow | statechart |
| transactional mutation | command bus |
| structural data validation | schema library |
| relational policy over many facts | rule engine/Datalog |
| orthogonal dense capabilities | ECS/protocols |
| semantic selection over rendered objects | PBUI |
| proof of a closed calculus | proof assistant |

The architectures can coexist. Elegance comes from assigning each relation to the tool designed for it.

## Exercises

1. **Comparison.** For one feature, compare component callbacks, a command bus, and PBUI.
2. **Integration.** Design a PBUI refinement backed by a reactive signal.
3. **Rule systems.** Express an archiving policy in Datalog-like notation and as a PBUI refinement. Compare explanation quality.
4. **Statecharts.** Model a three-argument command using a statechart plus PBUI input contexts.
5. **Critical.** Identify a part of PBUI that should be delegated to an existing schema library.
6. **Architecture.** Build a decision record choosing PBUI or a simpler alternative for a real workflow.

---

# 29. Related systems and implementations

## Learning objectives

After this chapter you should be able to:

1. locate PBUI ideas in historical and modern systems;
2. distinguish full presentation-based interaction from adjacent facilities;
3. identify implementations worth studying for type algebra, dispatch, identity, or object-centric tooling;
4. avoid claiming that one project supplies facilities it does not.

## 29.1 CLIM and McCLIM

CLIM is the principal historical source for this book's interaction model. Its facilities include presentation types, presentations associated with output, input contexts, presentation translators, commands, command tables, application frames, and output recording [CLIM2; LispWorksCLIM]. Moore discusses implementation concerns for CLIM presentation types, including the relationship between subtype reasoning and parameters [Moore2008]. McCLIM is an open implementation and living codebase [McCLIM].

Study CLIM for:

- semantic output;
- typed command arguments;
- translator applicability;
- contextual command tables;
- presentation sensitivity;
- the integration of output and input.

Do not assume that React's DOM or virtual tree already supplies CLIM output recording.

## 29.2 Semantic subtyping and CDuce

Semantic subtyping defines types by their denotations and subtyping by set inclusion. Work by Frisch, Castagna, and Benzaken develops this approach for XML-oriented and functional languages with unions, intersections, and negation [FrischCastagnaBenzaken2008]. CDuce is an implementation and language built around these ideas [CDuce].

Study this line of work for:

- set-theoretic type connectives;
- semantic equivalence;
- decision procedures;
- recursive types;
- the algorithmic difficulty of Boolean type operations.

PBUI's universe is tagged semantic references rather than arbitrary program values, and its refinements may call opaque application predicates. Therefore a complete CDuce-style decision procedure does not transfer directly.

## 29.3 Elixir's set-theoretic type system

Elixir began publicly developing a gradual set-theoretic type system in 2022. Elixir 1.20, released in June 2026, completed a milestone that gradually checks and infers across every Elixir program without requiring annotations; its type language and narrowing use unions, intersections, and negations [ElixirSetTypes; Elixir120]. The implementation work has also discussed BDD-related performance techniques [ElixirBDD].

Study Elixir for:

- fitting set-theoretic types to an existing dynamic language;
- recovering negative information from guards and control flow;
- gradual boundaries;
- practical compiler performance;
- understandable diagnostics.

PBUI differs because it builds an application semantic layer rather than a language-wide static type checker.

## 29.4 ArkType

ArkType is a TypeScript runtime type system with a set-theoretic orientation and APIs for runtime relationships such as checking whether one type extends another [ArkType].

Study ArkType for:

- runtime types as values;
- TypeScript inference from builder syntax;
- compiled validation;
- introspection and type relationships;
- ergonomic error messages.

Potential integration:

```ts
types.atom("project", {
  schema: adaptArkType(ProjectSchema),
});
```

ArkType is not a presentation UI, command table, semantic identity, or view-binding system.

## 29.5 Typed Racket and occurrence typing

Typed Racket refines the type of variables based on predicates and control-flow occurrences [TypedRacket; TobinHochstadtFelleisen2010]. This is closely related to retaining evidence that a particular occurrence satisfied a refinement.

Study Typed Racket for:

- predicate-driven narrowing;
- positive and negative occurrence information;
- sound interaction with a dynamic language;
- the limits of mutation-sensitive refinement.

## 29.6 Liquid Types and LiquidHaskell

Liquid Types combine conventional types with logical predicates drawn from a decidable refinement logic and use automated solvers [LiquidTypes]. LiquidHaskell demonstrates a substantial implementation for Haskell [LiquidHaskell].

Study them for:

- refinement implications;
- automated checking;
- predicate abstraction;
- proof obligations and counterexamples;
- the trade between expressive arbitrary code and decidable logic.

PBUI's named guard language could eventually adopt a liquid-style decidable fragment while retaining arbitrary local lambdas as an escape hatch.

## 29.7 Clojure multimethods and hierarchies

Clojure multimethods dispatch on arbitrary values. Its hierarchy operations support ad hoc derivation independent of Java classes, tuple-like dispatch values, and explicit method preferences [ClojureMultimethods].

This is one of the closest precedents for PBUI action dispatch:

```text
[subject type, context type, gesture type]
```

Study Clojure for:

- open method definition;
- independent hierarchies;
- ambiguity and preference;
- dispatch values beyond one receiver.

## 29.8 Clojure protocols, spec, and Malli

Clojure protocols define polymorphic operations independently of class inheritance [ClojureProtocols]. Clojure spec treats predicates and combinators as specifications and provides explanation and generation [ClojureSpec]. Malli is a high-performance data-driven schema system with registries and transformations [Malli].

Together they provide strong precedents for separating:

```text
protocol behavior
predicate specification
data-driven schema
ad hoc hierarchy
```

PBUI combines analogous separations around semantic references and rendered occurrences.

## 29.9 Julia multiple dispatch

Julia dispatches methods based on all argument types and separates method dispatch from conversion and promotion [JuliaMethods; JuliaConversion].

Study Julia for:

- product-order method specificity;
- ambiguity detection;
- parametric methods;
- keeping conversion distinct from applicability;
- avoiding overuse of values as type parameters.

Julia's types are language runtime types, not UI presentation types, but its dispatch principles transfer well.

## 29.10 Portal

Portal is a Clojure data exploration tool with selectable values, multiple viewers, commands, and viewer applicability predicates [Portal].

Study Portal for:

- nested value selection;
- switching among applicable viewers;
- keyboard-oriented command discovery;
- object navigation and history;
- integrating data semantics with an inspector UI.

Portal is particularly relevant to the experiential side of PBUI even though its formal type model differs.

## 29.11 Glamorous Toolkit

Glamorous Toolkit is an object-centric development environment in which domain objects can expose contextual views, actions, and searches [GlamorousToolkit]. Its “moldable development” approach treats domain-specific tools as first-class and composable.

Study it for:

- context-specific object views;
- inspectability as an extensible capability;
- explanations and object journeys;
- developer-defined semantic tooling;
- the value of making object meaning visible.

## 29.12 Fulcro

Fulcro is a full-stack Clojure/ClojureScript application framework whose normalized database and component idents let multiple UI views refer to the same entity [FulcroBook].

Study Fulcro for:

- semantic entity keys;
- normalized graph state;
- different visual projections of one entity;
- persistence and mutation around stable identity.

Fulcro's entity identity does not by itself provide CLIM-like input contexts or presentation translators, but it is a strong identity precedent.

## 29.13 Lively.next and Smalltalk-style environments

Lively.next is a browser-based JavaScript programming environment with live object inspection and direct manipulation [LivelyNext]. More broadly, Smalltalk environments and Morphic systems treat live objects, inspectors, and interactive tools as an integrated programming medium.

Study them for:

- live object identity;
- direct manipulation;
- inspector extensibility;
- development inside the running system.

## 29.14 Observable Inspector

Observable's Inspector renders arbitrary JavaScript values into reactive DOM output [ObservableInspector]. It is useful as a reference for generic value rendering and reactive display.

It does not provide semantic presentation types, translators, or action dispatch, but it demonstrates how a small rendering protocol can cover a wide range of runtime values.

## 29.15 No single direct JavaScript equivalent

The reviewed JavaScript and TypeScript ecosystem contains strong implementations of runtime schemas, validation, reactive state, command buses, inspectors, and pattern matching. There does not appear to be one mainstream project that combines the full CLIM-like set of:

- semantic output occurrences;
- input contexts over existing output;
- presentation type algebra;
- translators;
- contextual command tables;
- semantic identity;
- linked view subjects.

This is an opportunity, but also a warning: integration quality and interaction design matter more than re-creating terminology.

## 29.16 Reading paths

### CLIM path

1. CLIM user-guide chapters on presentation types and translators.
2. Command tables and application frames.
3. Output recording and redisplay.
4. McCLIM source around presentation matching.

### Type-theory path

1. Pierce or Harper for operational and type-theoretic foundations.
2. Davey and Priestley for orders and lattices.
3. semantic-subtyping introductions and CDuce.
4. occurrence and refinement typing.
5. Elixir implementation reports.

### Systems path

1. Clojure multimethods and protocols.
2. Julia methods and conversion.
3. Portal and Glamorous Toolkit.
4. Fulcro normalization.
5. ArkType and Malli implementation techniques.

## Exercises

1. **Comparative reading.** Choose two systems and map their concepts to the six-protocol principle.
2. **Implementation study.** Inspect one open-source dispatch implementation and summarize its ambiguity policy.
3. **Critical.** Identify one concept that this book borrows imperfectly from CLIM and explain the mismatch.
4. **Research.** Compare Elixir's use of negation with PBUI's base-relative difference.
5. **Design.** Propose a concrete integration between PBUI and ArkType, Malli, or a normalized store.
6. **Survey.** Search for another presentation-oriented UI system and evaluate it using this chapter's criteria.

---

# 30. A staged roadmap for PBUI

## Learning objectives

After this chapter you should be able to:

1. migrate the existing PBUI without a rewrite;
2. define exit criteria for each stage;
3. preserve compatibility while introducing the type algebra;
4. identify optional research branches;
5. decide where the project should intentionally stop.

## 30.1 Baseline

The starting PBUI already contains the right seed concepts:

```text
PresentationReference
presentation descriptors
Presentation wrapper
accept request
one-step conversion
provider-local environment and state
serializable application verbs
```

The migration should preserve these interfaces while moving semantics into independently testable services.

## 30.2 Stage 0 — Write the semantic contracts

Before adding features:

- document what exact acceptance means;
- define context replacement and abort behavior;
- specify conversion order;
- identify all existing presentation atoms;
- inventory object identities and missing stable keys;
- list action duplication and cross-view selection workflows;
- add baseline race and keyboard tests.

### Exit criteria

- every current type has a representation declaration;
- existing behavior is covered by focused tests;
- unresolved identity cases are listed rather than guessed.

### Stop option

A well-documented Profile A may be enough.

## 30.3 Stage 1 — Semantic identity and revisions

Extend descriptors:

```ts
identity?(value, environment): SemanticIdentity | undefined;
revision?(value, environment): string | number | undefined;
```

Add:

```ts
registry.identityFor(reference, environment);
registry.sameObject(left, right, environment);
```

Use identity for:

- selected-object highlighting;
- operation-scoped applicability caching;
- translator preservation tests;
- cross-representation diagnostics.

### Exit criteria

- identity law tests pass;
- fields, documents, projects, rows, logical views, and placements have deliberate policies;
- no deep-equality fallback is implicit.

## 30.4 Stage 2 — Prepared selectors

Introduce:

```ts
interface PresentationSelector<T> {
  readonly id?: string;
  readonly types: readonly string[];
  readonly cache?: "none" | "occurrence" | "identity";
  readonly where?: Predicate<T>;
  readonly prepare?: PreparePredicate<T>;
}
```

Compile legacy requests:

```text
{ types, filter } -> selector
```

Add commit revalidation and dependency epochs.

### Exit criteria

- expensive selectors prepare once;
- cache keys include identity and revision;
- clicked occurrence is re-materialized at commitment;
- profiling reports predicate call counts.

### Stop option

This establishes Profile B and may deliver most value.

## 30.5 Stage 3 — Linked subject cells

Separate:

```text
viewId
placementId
documentBindingId
```

Add reducers and portable bundle encoding for link, unlink, and subject update. Express link-target selection through PBUI.

### Exit criteria

- chart and pipeline can share selected document while retaining distinct configurations;
- ordinary duplicates remain independent;
- linked duplicates retain existing semantics;
- local and portable persistence round-trip sharing topology;
- remote protocol limitations are explicit.

## 30.6 Stage 4 — Nominal subtypes and capabilities

Add a frozen registry snapshot with:

```ts
supertypes
static capabilities
action tables
```

Compile ancestor masks. Keep exact selectors available.

Use capabilities first for repeated cross-type behavior:

```text
Inspectable
DocumentBacked
Watchable
```

### Exit criteria

- nominal cycles fail at setup;
- subtype declarations are representation-safe;
- common actions no longer repeat across descriptors;
- registration-order shuffling does not change action output.

## 30.7 Stage 5 — Named refinements and type expressions

Add the algebra:

```ts
atom
or
and
difference
refinement
```

Initially support semantic subtype rules for:

- atoms and nominal closure;
- top and bottom;
- unions and intersections;
- base-relative difference with conservative reasoning;
- refinement-to-base.

Treat unrelated predicates as opaque.

### Exit criteria

- denotational reference interpreter exists for tests;
- optimized matcher is differentially tested;
- public documentation states subtype completeness limits;
- serialized expressions use namespaced IDs and schemas.

## 30.8 Stage 6 — Evidence and multimethods

Change internal Boolean matching to structured evidence. Introduce action signatures and maximal-method selection.

Keep the ordinary public API simple:

```ts
const project = await pbui.accept({ type: ActiveProject });
```

Expose advanced inspection separately.

### Exit criteria

- action resolution is registration-order independent;
- ambiguity produces a diagnostic or explicit preference requirement;
- evidence powers a semantic inspector;
- sensitive diagnostics are redacted.

## 30.9 Stage 7 — Typed translator graph

Replace untyped conversions with declarations containing:

```text
id, from, to, cost, totality, purity,
asynchrony, identity preservation
```

Start with direct indexed translation. Add bounded paths only after a real chained workflow appears.

### Exit criteria

- every translator success validates target representation;
- identity-preserving claims are tested;
- cycles and budgets are tested;
- asynchronous translation has cancellation and pending UI.

## 30.10 Stage 8 — Optional research branches

### Branch A: guard language

Build a serializable predicate AST with dependency extraction and explanation.

### Branch B: BDD subtype core

Instrument expression growth, then evaluate BDD or automata techniques for negation-rich expressions.

### Branch C: mechanized kernel

Formalize direct type denotation, matching, subtype rules, dispatch, and link reducers in Lean, Coq, or Agda.

### Branch D: distributed registry contracts

Define compatible client/server semantic registries and server re-evaluation of selections.

### Branch E: retained semantic output index

Index unmounted and virtualized domain objects so input contexts can search beyond mounted occurrences.

Each branch should have a user or research question, not only technical novelty.

## 30.11 Recommended stopping point

For the supplied PBUI, the strongest practical stopping point is:

```text
Profile B
+ nominal capabilities
+ a small explicit TypeExpr algebra
+ evidence summaries
```

This yields:

- linked chart/pipeline document subjects;
- reusable and prepared selection predicates;
- semantic identity;
- subtype-aware common actions;
- typed direct translators;
- explainable matching;
- a route to richer theory without requiring a compiler-scale type checker.

Full negation, BDDs, recursive types, and machine-checked proofs should remain optional research work until measured expression complexity or platform goals justify them.

## 30.12 Governance

Every new feature should answer:

1. Which distinct relation does it model?
2. What user workflow requires it?
3. What is its denotational or operational contract?
4. What are its proof obligations?
5. How is it tested?
6. How is it explained?
7. Can it be omitted by ordinary users?
8. What persistence and plugin consequences follow?

This checklist protects the project from becoming a collection of clever but interacting mechanisms.

## 30.13 Final perspective

The destination API is not elegant because it uses advanced type terminology. It is elegant when each operation has one meaning:

```text
subtype       = safe semantic inclusion
capability    = supported proposition or protocol
refinement    = snapshot-relative subset
identity      = same domain object
translation   = partial change of representation or role
matching      = evidence-producing applicability
multimethod   = behavior chosen by several semantic arguments
binding       = shared mutable subject cell
```

Once those meanings are separated, both the mathematics and the user interface become easier to extend.

## Exercises

1. **Project plan.** Turn the stages into milestones for the supplied repository, including files and tests.
2. **Exit criteria.** Choose a deliberate stopping point and defend it.
3. **Risk analysis.** List the three highest-risk migrations and mitigation strategies.
4. **Research proposal.** Write a one-page proposal for one optional branch, including a falsifiable success criterion.
5. **Governance.** Apply the eight governance questions to a proposed “automatic translator chaining” feature.

---
# Appendix A — Reference API

This appendix presents a consolidated API sketch. It is a design target, not a claim that every declaration is required in one package. The no-dependency companion implementation supplied with this book implements the algebraic core and demonstrates the principal laws; React bindings and application-store reducers remain host-specific.

## A.1 Core identifiers and references

```ts
export type TypeId = string & { readonly __typeId: unique symbol };
export type AtomId = TypeId & { readonly __atomId: unique symbol };
export type CapabilityId = TypeId & { readonly __capabilityId: unique symbol };
export type RefinementId = string & { readonly __refinementId: unique symbol };
export type TranslatorId = string & { readonly __translatorId: unique symbol };
export type ActionMethodId = string & { readonly __actionMethodId: unique symbol };
export type ActionTableId = string & { readonly __actionTableId: unique symbol };

export interface SemanticIdentity {
  readonly namespace: string;
  readonly key: string;
}

export type PresentationType<Values extends object> =
  Extract<keyof Values, string>;

export type PresentationReference<Values extends object> = {
  [K in PresentationType<Values>]: Readonly<{
    type: K;
    value: Values[K];
  }>;
}[PresentationType<Values>];
```

## A.2 Runtime type expressions

```ts
declare const expressionOutput: unique symbol;

export interface TypeExpr<T = unknown> {
  readonly kind:
    | "top"
    | "bottom"
    | "atom"
    | "capability"
    | "union"
    | "intersection"
    | "difference"
    | "refinement";
  readonly id: string;
  readonly [expressionOutput]?: T;
}

export interface TopExpr extends TypeExpr<unknown> {
  readonly kind: "top";
}

export interface BottomExpr extends TypeExpr<never> {
  readonly kind: "bottom";
}

export interface AtomExpr<T> extends TypeExpr<T> {
  readonly kind: "atom";
  readonly atom: AtomId;
}

export interface CapabilityExpr<T = unknown> extends TypeExpr<T> {
  readonly kind: "capability";
  readonly capability: CapabilityId;
}

export interface UnionExpr<T> extends TypeExpr<T> {
  readonly kind: "union";
  readonly members: readonly TypeExpr[];
}

export interface IntersectionExpr<T> extends TypeExpr<T> {
  readonly kind: "intersection";
  readonly members: readonly TypeExpr[];
}

export interface DifferenceExpr<T> extends TypeExpr<T> {
  readonly kind: "difference";
  readonly base: TypeExpr<T>;
  readonly excluded: TypeExpr;
}

export interface RefinementExpr<T, Args = unknown> extends TypeExpr<T> {
  readonly kind: "refinement";
  readonly refinement: RefinementId;
  readonly base: TypeExpr<T>;
  readonly args: Args;
}
```

Smart constructors:

```ts
export interface TypeAlgebra {
  top(): TopExpr;
  bottom(): BottomExpr;

  atom<T>(id: string): AtomExpr<T>;
  capability<T = unknown>(id: string): CapabilityExpr<T>;

  or<A, B>(left: TypeExpr<A>, right: TypeExpr<B>): TypeExpr<A | B>;
  or<T>(...members: readonly TypeExpr<T>[]): TypeExpr<T>;

  and<T>(...members: readonly TypeExpr<T>[]): TypeExpr<T>;

  difference<T>(
    base: TypeExpr<T>,
    excluded: TypeExpr,
  ): TypeExpr<T>;

  refine<T, Args>(
    base: TypeExpr<T>,
    refinement: RefinementId,
    args: Args,
  ): RefinementExpr<T, Args>;

  print(expression: TypeExpr): string;
  serialize(expression: TypeExpr): SerializedTypeExpr;
  parse(input: unknown): TypeExpr;
}
```

## A.3 Runtime schemas

```ts
export interface RuntimeSchema<T> {
  is(input: unknown): input is T;
  parse(input: unknown): T;
  describe?(): unknown;
}
```

## A.4 Atomic descriptors

```ts
export interface AtomDescriptor<T, Environment, Verb> {
  readonly schema?: RuntimeSchema<T>;

  label(value: T, environment: Environment): string;

  describe?(value: T, environment: Environment): unknown;

  identity?(
    value: T,
    environment: Environment,
  ): SemanticIdentity | undefined;

  revision?(
    value: T,
    environment: Environment,
  ): string | number | undefined;

  actions?(
    value: T,
    environment: Environment,
  ): readonly Action<Verb>[];
}
```

## A.5 Capability and protocol declarations

Set-only capability:

```ts
export interface CapabilityDefinition {
  readonly id: CapabilityId;
  readonly description?: string;
}

export interface StaticCapabilityImplementation {
  readonly mode: "static";
  readonly atom: AtomId;
  readonly capability: CapabilityId;
}

export interface DynamicCapabilityImplementation<
  T,
  Environment
> {
  readonly mode: "dynamic";
  readonly atom: AtomId;
  readonly capability: CapabilityId;
  readonly id: string;

  test(value: T, environment: Environment): boolean;

  dependencies?(
    value: T,
    environment: Environment,
  ): DependencyFingerprint;
}
```

Optional protocol methods can be layered over capabilities:

```ts
export interface Protocol<Methods extends object> {
  readonly id: CapabilityId;
  readonly methods: Methods;
}
```

The exact generic API for protocol implementations is host-specific because method signatures vary.

## A.6 Refinements

```ts
export type PredicateClass =
  | "structural"
  | "pure"
  | "environment-dependent"
  | "volatile";

export type CachePolicy =
  | "none"
  | "occurrence"
  | "identity"
  | "dependencies";

export interface DependencyFingerprint {
  readonly definitionId: string;
  readonly parts: readonly (
    | string
    | number
    | boolean
    | null
  )[];
}

export interface RefinementDefinition<T, Args, Environment> {
  readonly id: RefinementId;
  readonly base: TypeExpr<T>;
  readonly argsSchema?: RuntimeSchema<Args>;
  readonly classification: PredicateClass;
  readonly cache: CachePolicy;
  readonly description?: string;

  prepare?(
    args: Args,
    environment: Environment,
  ): PreparedRefinement<T>;

  test?(
    value: T,
    args: Args,
    environment: Environment,
  ): boolean;

  dependencies?(
    value: T,
    args: Args,
    environment: Environment,
  ): DependencyFingerprint;

  explainFailure?(
    value: T,
    args: Args,
    environment: Environment,
  ): PublicDiagnostic | undefined;
}

export interface PreparedRefinement<T> {
  test(value: T): boolean;
  fingerprint?(value: T): DependencyFingerprint;
}
```

Ephemeral selector:

```ts
export interface EphemeralRefinement<T, Environment> {
  readonly id?: string;
  readonly description?: string;
  readonly cache?: "none" | "occurrence" | "identity";

  prepare?(
    environment: Environment,
  ): (value: T) => boolean;

  where?(
    value: T,
    environment: Environment,
  ): boolean;
}
```

## A.7 Registry builder

```ts
export interface RegistryBuilder<
  Values extends object,
  Environment,
  Verb
> {
  addAtom<K extends keyof Values & string>(
    id: K,
    descriptor: AtomDescriptor<Values[K], Environment, Verb>,
  ): AtomExpr<Values[K]> & { readonly atom: K };

  declareSubtype<Sub extends Super, Super>(
    sub: AtomExpr<Sub>,
    sup: AtomExpr<Super>,
  ): this;

  addCapability(
    id: string,
    options?: { readonly description?: string },
  ): CapabilityExpr;

  implementStatic<T>(
    atom: AtomExpr<T>,
    capability: CapabilityExpr,
  ): this;

  implementDynamic<T>(
    atom: AtomExpr<T>,
    capability: CapabilityExpr,
    implementation: DynamicCapabilityImplementation<T, Environment>,
  ): this;

  addRefinement<T, Args>(
    definition: RefinementDefinition<T, Args, Environment>,
  ): RefinementFactory<T, Args>;

  addTranslator<From, To>(
    definition: TranslatorDefinition<From, To, Environment>,
  ): this;

  addActionTable(definition: ActionTableDefinition): this;

  addActionMethod(
    definition: ActionMethodDefinition<Values, Environment, Verb>,
  ): this;

  preferActionMethod(
    preferred: ActionMethodId,
    over: ActionMethodId,
  ): this;

  freeze(): RegistrySnapshot<Values, Environment, Verb>;
}
```

Refinement factory:

```ts
export interface RefinementFactory<T, Args> {
  readonly id: RefinementId;
  readonly base: TypeExpr<T>;
  (args: Args): RefinementExpr<T, Args>;
}
```

## A.8 Registry snapshot

```ts
export interface RegistrySnapshot<
  Values extends object,
  Environment,
  Verb
> {
  readonly version: number;
  readonly hash: string;
  readonly algebra: TypeAlgebra;

  descriptor<K extends keyof Values & string>(
    type: K,
  ): AtomDescriptor<Values[K], Environment, Verb>;

  identityFor(
    reference: PresentationReference<Values>,
    environment: Environment,
  ): SemanticIdentity | undefined;

  revisionFor(
    reference: PresentationReference<Values>,
    environment: Environment,
  ): string | number | undefined;

  sameObject(
    left: PresentationReference<Values>,
    right: PresentationReference<Values>,
    environment: Environment,
  ): boolean;

  isNominalSubtype(sub: string, sup: string): boolean;

  isSubtype(left: TypeExpr, right: TypeExpr): boolean;

  compareTypes(
    left: TypeExpr,
    right: TypeExpr,
  ): "less" | "equal" | "greater" | "incomparable";

  compile<T>(expression: TypeExpr<T>): CompiledTemplate<T>;
}
```

## A.9 Evidence and matching

```ts
export interface ValidityToken {
  readonly registryVersion: number;
  readonly environmentEpoch: string | number;
  readonly dependencies: readonly DependencyFingerprint[];
}

export interface Match<
  Values extends object,
  T = unknown
> {
  readonly source: PresentationReference<Values>;
  readonly accepted: PresentationReference<Values>;
  readonly value: T;
  readonly requestedType: TypeExpr<T>;
  readonly membership: MembershipEvidence;
  readonly translationPath: readonly TranslationEvidence<Values>[];
  readonly validity: ValidityToken;
}

export type MatchResult<Values extends object, T = unknown> =
  | { readonly ok: true; readonly match: Match<Values, T> }
  | { readonly ok: false; readonly failure: MatchFailure };

export interface Matcher<Values extends object, Environment> {
  direct<T>(
    reference: PresentationReference<Values>,
    expression: TypeExpr<T>,
    environment: Environment,
  ): MatchResult<Values, T>;

  match<T>(
    reference: PresentationReference<Values>,
    expression: TypeExpr<T>,
    environment: Environment,
    options?: MatchOptions,
  ): Promise<MatchResult<Values, T>>;

  isStillValid(
    token: ValidityToken,
    environment: Environment,
  ): boolean;
}

export interface MatchOptions {
  readonly translations?: "none" | "direct" | "paths";
  readonly maxTranslationDepth?: number;
  readonly maxTranslationStates?: number;
  readonly explain?: boolean;
  readonly signal?: AbortSignal;
}
```

## A.10 Translators

```ts
export interface TranslatorDefinition<From, To, Environment> {
  readonly id: TranslatorId;
  readonly from: AtomExpr<From>;
  readonly to: AtomExpr<To>;
  readonly cost?: number;
  readonly priority?: number;
  readonly total?: boolean;
  readonly pure?: boolean;
  readonly asynchronous?: boolean;
  readonly preservesIdentity?: boolean;
  readonly information?: "preserving" | "lossy" | "enriching";
  readonly implicit?: boolean;

  applicable?(
    value: From,
    environment: Environment,
  ): boolean;

  translate(
    value: From,
    environment: Environment,
    signal: AbortSignal,
  ): To | undefined | Promise<To | undefined>;

  dependencies?(
    value: From,
    environment: Environment,
  ): DependencyFingerprint;
}
```

## A.11 Actions and multimethods

```ts
export interface Action<Verb> {
  readonly id: string;
  readonly label: string;
  readonly description?: string;
  readonly danger?: boolean;
  readonly enabled?: boolean;
  readonly disabledReason?: string;
  readonly verb: Verb;
}

export interface ActionTableDefinition {
  readonly id: ActionTableId;
  readonly parents?: readonly ActionTableId[];
  readonly sealed?: boolean;
}

export interface ActionSignature {
  readonly subject: TypeExpr;
  readonly context?: TypeExpr;
  readonly gesture?: TypeExpr;
  readonly arguments?: readonly TypeExpr[];
}

export interface ActionMethodDefinition<
  Values extends object,
  Environment,
  Verb
> {
  readonly id: ActionMethodId;
  readonly table: ActionTableId;
  readonly signature: ActionSignature;
  readonly actionId: string;
  readonly description?: string;

  actions(input: {
    readonly subject: Match<Values>;
    readonly context?: Match<Values>;
    readonly gesture?: Match<Values>;
    readonly arguments: readonly Match<Values>[];
    readonly environment: Environment;
  }): Action<Verb> | readonly Action<Verb>[];
}
```

## A.12 Input contexts

```ts
export interface AcceptRequest<T> {
  readonly type: TypeExpr<T>;
  readonly prompt: string;
  readonly translations?: "none" | "direct" | "paths";
  readonly searchScope?: "mounted-occurrences" | "registered-domain-index";
  readonly excludeIdentity?: SemanticIdentity;
}

export interface Accepted<T, Values extends object> {
  readonly value: T;
  readonly reference: PresentationReference<Values>;
  readonly match: Match<Values, T>;
}

export interface PbuiRuntime<
  Values extends object,
  Environment,
  Verb
> {
  accept<T>(
    request: AcceptRequest<T>,
  ): Promise<Accepted<T, Values> | null>;

  acceptWithEvidence<T>(
    request: AcceptRequest<T>,
  ): Promise<Match<Values, T> | null>;

  abortAccept(reason?: string): void;

  probe(
    reference: PresentationReference<Values>,
  ): ProbeResult;

  commit(
    reference: PresentationReference<Values>,
    occurrenceId: string,
  ): void;

  actionsFor(
    reference: PresentationReference<Values>,
    input?: Partial<DispatchInput<Values>>,
  ): readonly Action<Verb>[];

  perform(verb: Verb): void;
}
```

## A.13 React facade

```ts
export interface CreatePbuiOptions<
  Values extends object,
  Environment,
  Verb
> {
  readonly registry: RegistrySnapshot<Values, Environment, Verb>;
  readonly defaultEnvironment: Environment;
  readonly defaultActionTables?: readonly ActionTableId[];
}

export interface CreatedPbui<Values extends object, Environment, Verb> {
  Provider(props: {
    readonly environment?: Environment;
    readonly actionTables?: readonly ActionTableId[];
    readonly onPerform?: (verb: Verb) => void;
    readonly children: React.ReactNode;
  }): React.ReactElement;

  Presentation(props: {
    readonly reference: PresentationReference<Values>;
    readonly children: React.ReactNode;
    readonly occurrenceId?: string;
    readonly block?: boolean;
    readonly disabled?: boolean;
  }): React.ReactElement;

  ObjectMenu(): React.ReactElement | null;

  AcceptStatus(): React.ReactElement | null;

  usePbui(): PbuiRuntime<Values, Environment, Verb> & {
    readonly environment: Environment;
    readonly activeRequest: unknown | null;
  };
}
```

## A.14 Subject bindings

```ts
export type ViewId = string & { readonly __viewId: unique symbol };
export type PlacementId = string & { readonly __placementId: unique symbol };
export type SubjectBindingId = string & {
  readonly __subjectBindingId: unique symbol;
};

export interface SubjectBinding<SubjectId> {
  readonly id: SubjectBindingId;
  readonly scope: "workspace" | "user" | "session";
  readonly subjects: Readonly<Record<string, SubjectId>>;
}

export interface SubjectLinkedView {
  readonly id: ViewId;
  readonly appId: string;
  readonly subjectBindingId: SubjectBindingId;
}

export type SubjectLinkAction<SubjectId> =
  | Readonly<{
      type: "linkViewSubjects";
      sourceViewId: ViewId;
      targetViewId: ViewId;
      policy: "source-wins" | "target-wins" | "reject-conflict";
    }>
  | Readonly<{
      type: "unlinkViewSubjects";
      viewId: ViewId;
    }>
  | Readonly<{
      type: "setViewSubject";
      viewId: ViewId;
      role: string;
      subjectId: SubjectId;
    }>;
```

## A.15 Complete example

```ts
interface Entity {
  id: string;
}

interface Project extends Entity {
  title: string;
  ownerId: string;
  archived: boolean;
  documentId: string;
  revision: number;
}

interface Values {
  entity: Entity;
  project: Project;
  projectId: string;
  tile: { viewId: ViewId };
}

interface Environment {
  snapshotId: number;
  authorizationEpoch: number;
  currentUserId: string;
  projects: ReadonlyMap<string, Project>;
  canArchive(projectId: string): boolean;
}

type Verb =
  | { type: "openProject"; projectId: string }
  | { type: "archiveProject"; projectId: string }
  | { type: "linkViewSubjects"; source: ViewId; target: ViewId };

const builder = createRegistryBuilder<Values, Environment, Verb>();

const Entity = builder.addAtom("entity", {
  label: entity => entity.id,
  identity: entity => ({ namespace: "entity", key: entity.id }),
});

const Project = builder.addAtom("project", {
  label: project => project.title,
  identity: project => ({ namespace: "project", key: project.id }),
  revision: project => project.revision,
});

const ProjectId = builder.addAtom("projectId", {
  label: id => `#${id}`,
  identity: id => ({ namespace: "project", key: id }),
});

builder.declareSubtype(Project, Entity);

const Inspectable = builder.addCapability("inspectable");
const DocumentBacked = builder.addCapability("document-backed");
const Archived = builder.addCapability("archived");
const Archivable = builder.addCapability("archivable");

builder.implementStatic(Project, Inspectable);
builder.implementStatic(Project, DocumentBacked);

builder.implementDynamic(Project, Archived, {
  id: "project/archived",
  atom: Project.atom,
  capability: Archived.capability,
  mode: "dynamic",
  test: project => project.archived,
  dependencies: project => ({
    definitionId: "project/archived",
    parts: [project.id, project.revision],
  }),
});

builder.implementDynamic(Project, Archivable, {
  id: "project/archivable",
  atom: Project.atom,
  capability: Archivable.capability,
  mode: "dynamic",
  test: (project, environment) =>
    !project.archived && environment.canArchive(project.id),
  dependencies: (project, environment) => ({
    definitionId: "project/archivable",
    parts: [
      project.id,
      project.revision,
      environment.authorizationEpoch,
    ],
  }),
});

const OwnedBy = builder.addRefinement<Project, { userId: string }>({
  id: "project/owned-by" as RefinementId,
  base: Project,
  classification: "pure",
  cache: "dependencies",
  test: (project, { userId }) => project.ownerId === userId,
  dependencies: (project, { userId }) => ({
    definitionId: "project/owned-by",
    parts: [project.id, project.revision, userId],
  }),
});

builder.addTranslator({
  id: "project-id/to-project" as TranslatorId,
  from: ProjectId,
  to: Project,
  cost: 1,
  total: false,
  pure: true,
  asynchronous: false,
  preservesIdentity: true,
  translate(id, environment) {
    return environment.projects.get(id);
  },
});

builder.addActionTable({ id: "global" as ActionTableId });
builder.addActionTable({
  id: "admin" as ActionTableId,
  parents: ["global" as ActionTableId],
});

builder.addActionMethod({
  id: "project/archive" as ActionMethodId,
  table: "admin" as ActionTableId,
  actionId: "archive",
  signature: {
    subject: builder.algebra.and(Project, Archivable),
  },
  actions({ subject }) {
    const project = subject.value as Project;
    return {
      id: "archive",
      label: "Archive project",
      danger: true,
      verb: {
        type: "archiveProject",
        projectId: project.id,
      },
    };
  },
});

const registry = builder.freeze();
const pbui = createPbui({
  registry,
  defaultEnvironment,
  defaultActionTables: ["global" as ActionTableId],
});

const MyActiveProject = registry.algebra.and(
  Project,
  OwnedBy({ userId: currentUserId }),
  registry.algebra.difference(Project, Archived),
);
```

Acceptance:

```ts
const accepted = await pbuiRuntime.accept({
  type: MyActiveProject,
  prompt: "Choose one of your active projects",
  translations: "direct",
});
```

---
# Appendix B — Selected exercise solutions

The solutions are intentionally selective. Exercises not solved here are suitable for design reviews, study groups, or implementation assignments.

## B.1 Chapter 1, Exercise 4 — Acceptance soundness

A plain-language soundness statement is:

> Whenever an input context requesting type \(\tau\) successfully returns a reference \(r\), that returned reference actually satisfies the semantic membership condition denoted by \(\tau\) in the environment used for commitment.

With translations, distinguish source and result:

> If occurrence source \(s\) is accepted through translation and the operation returns \(r\), then \(r\), not necessarily \(s\), belongs to \(\llbracket\tau\rrbracket_e\), and every recorded translator step satisfies its contract.

## B.2 Chapter 4, Exercise 2 — Project IDs are not projects

Let:

```ts
interface Project {
  id: string;
  title: string;
}
```

A consumer of `Project` may evaluate:

```ts
project.title.toUpperCase()
```

The value `"p-7"` cannot be passed directly to that consumer. Therefore `ProjectId <: Project` violates substitutability. A lookup translator is appropriate:

```ts
lookup("p-7") => { id: "p-7", title: "Compiler" }
```

The lookup may fail, which is another reason it is not subtyping.

## B.3 Chapter 5, Exercise 2 — Union idempotence

We prove \(A\cup A=A\).

For arbitrary \(x\):

\[
\begin{aligned}
x\in A\cup A
&\Leftrightarrow x\in A\lor x\in A\\
&\Leftrightarrow x\in A.
\end{aligned}
\]

By extensionality, \(A\cup A=A\). Therefore \(\tau\lor\tau\equiv\tau\).

## B.4 Chapter 5, Exercise 3 — Absorption

We prove \(A\cap(A\cup B)=A\).

For arbitrary \(x\):

\[
\begin{aligned}
x\in A\cap(A\cup B)
&\Leftrightarrow x\in A\land(x\in A\lor x\in B)\\
&\Leftrightarrow x\in A.
\end{aligned}
\]

The last equivalence is propositional absorption. Extensionality completes the proof.

## B.5 Chapter 6, Exercise 2 — Non-transitive similarity

Define projects to be similar when their titles have edit distance at most one.

```text
"cat"  similar to "cut"
"cut"  similar to "cute"
"cat"  not similar to "cute"
```

Similarity is not transitive, so it cannot partition occurrences into stable identity classes. Selecting the middle item could cause both endpoints to highlight even though the endpoints do not match each other.

## B.6 Chapter 7, Exercise 3 — Quotienting a subtype preorder

Let \(\leq\) be a preorder and define:

\[
x\equiv y \quad\text{iff}\quad x\leq y\land y\leq x.
\]

First, \(\equiv\) is an equivalence relation:

- reflexivity follows from preorder reflexivity;
- symmetry is built into the definition;
- transitivity follows from transitivity of \(\leq\) in both directions.

Define order on equivalence classes:

\[
[x]\preceq[y] \quad\text{iff}\quad x\leq y.
\]

This is well defined: if \(x\equiv x'\), \(y\equiv y'\), and \(x\leq y\), then

\[
x'\leq x\leq y\leq y'.
\]

Antisymmetry follows because `[x] ≤ [y]` and `[y] ≤ [x]` imply \(x\equiv y\), hence `[x]=[y]`.

## B.7 Chapter 8, Exercise 1 — Evidence for an active inspectable project

Suppose:

```text
r has atom Project
Project statically implements Inspectable
Active(r,e) = true
```

Evidence tree:

```text
intersection
├─ refinement Active
│  ├─ atom Project
│  └─ predicate Active succeeded at project revision 8
└─ capability Inspectable
   └─ static implementation Project -> Inspectable
```

Formally:

\[
\frac{
  \frac{r:\textsf{Project}\qquad Active(r,e)}
       {r:\operatorname{refine}(Active,(),\textsf{Project})}
  \qquad
  r:\operatorname{cap}(Inspectable)
}{r:\operatorname{refine}(Active,(),\textsf{Project})
  \land\operatorname{cap}(Inspectable)}.
\]

## B.8 Chapter 9, Exercise 2 — Matcher soundness cases

### Union

If the matcher succeeds on \(\tau\lor\sigma\), it succeeded on one branch, say \(\tau\). By induction, \(r\in\llbracket\tau\rrbracket\). By union introduction, \(r\in\llbracket\tau\rrbracket\cup\llbracket\sigma\rrbracket\).

### Intersection

If the matcher succeeds on \(\tau\land\sigma\), it has successful child derivations for both. By induction, \(r\) belongs to both denotations, hence to their intersection.

## B.9 Chapter 10, Exercise 5 — Removing top

For arbitrary \(r\):

\[
\begin{aligned}
r\in\llbracket\tau\land\top\rrbracket_e
&\Leftrightarrow r\in\llbracket\tau\rrbracket_e
\land r\in\Omega\\
&\Leftrightarrow r\in\llbracket\tau\rrbracket_e.
\end{aligned}
\]

Therefore replacing `and(τ, top)` with `τ` preserves denotation.

## B.10 Chapter 11, Exercise 1 — Intersection elimination

By definition:

\[
\llbracket\tau\land\sigma\rrbracket_e
=\llbracket\tau\rrbracket_e\cap\llbracket\sigma\rrbracket_e.
\]

Every member of an intersection is a member of its left set, so:

\[
\llbracket\tau\land\sigma\rrbracket_e
\subseteq\llbracket\tau\rrbracket_e.
\]

Because this holds for every environment, \(\tau\land\sigma\leq\tau\).

## B.11 Chapter 11, Exercise 4 — Structural safety is not full substitutability

```ts
interface Entity {
  id: string;
}

interface CachedEntity extends Entity {
  refresh(): Promise<void>;
}
```

Structurally, `CachedEntity` can be passed where `Entity` is expected. Now suppose the semantic contract of `Entity` says `id` never changes, but `refresh()` may replace `id` after server reconciliation. The structure is compatible while the behavioral invariant is not. TypeScript assignability checks fields, not the application's temporal contract.

## B.12 Chapter 13, Exercise 3 — Mutable refinement brand

Suppose:

```ts
type ActiveProject = Project & { readonly __active: true };
```

After checking `!project.archived`, code casts to `ActiveProject`. Another operation then mutates or replaces state so the project becomes archived. The brand remains in the static type even though its proposition is false. A snapshot-indexed evidence object avoids treating the proposition as eternal.

## B.13 Chapter 14, Exercise 6 — Identity cache assumptions

Reusing a refinement result across identity-equivalent references requires:

1. both references have the same semantic identity;
2. the predicate is identity-invariant;
3. relevant object revisions are equal;
4. environment dependency fingerprints are equal;
5. the refinement definition and registry version are equal;
6. the cached value is only an applicability decision unless translated payload identity and representation are also safe to reuse;
7. commitment revalidates current state.

Omitting any dependency can produce stale acceptance.

## B.14 Chapter 15, Exercise 4 — Shortest can be worse

Suppose:

```text
RichProject -> ProjectTitle          cost 1, lossy
RichProject -> ProjectSummary        cost 1, preserving summary facts
ProjectSummary -> SearchDocument     cost 1
ProjectTitle -> SearchDocument       cost 0
```

The cost-1 path through title may discard identity and metadata, while the cost-2 path preserves them. Cost must encode semantic preference or be combined with information-loss policy. Graph distance alone is not enough.

## B.15 Chapter 16, Exercise 2 — Difference soundness

A successful match for \(\tau\setminus\sigma\) contains:

1. success evidence for \(r:\tau\);
2. decidable non-membership evidence for \(r:\sigma\).

By induction, \(r\in\llbracket\tau\rrbracket_e\). The second premise gives \(r\notin\llbracket\sigma\rrbracket_e\). Therefore:

\[
r\in\llbracket\tau\rrbracket_e\setminus\llbracket\sigma\rrbracket_e.
\]

If the excluded result is merely unknown, the matcher must not construct difference success.

## B.16 Chapter 17, Exercise 2 — Product specificity is a preorder

Let signatures have equal arity and define componentwise order:

\[
S\preceq T \quad\text{iff}\quad \forall i.\;S_i\leq T_i.
\]

Reflexivity follows because each component subtype relation is reflexive. Transitivity follows componentwise: if \(S_i\leq T_i\) and \(T_i\leq U_i\), then \(S_i\leq U_i\). Thus signature order is a preorder. Quotienting component types by semantic equivalence gives a partial order.

## B.17 Chapter 18, Exercise 2 — At-most-once resolution

Maintain two invariants:

```text
only the continuation for the active context ID may settle
settleOnce changes settled from false to true atomically
```

Suppose two events attempt to resolve context `q`. The first sees `settled=false`, changes it to true, and invokes the continuation. The second sees true and performs no invocation. Stale IDs are rejected before settlement. Therefore the continuation is invoked at most once.

## B.18 Chapter 19, Exercise 3 — Unlink does not affect the remaining group

Let view \(v\) be removed from binding \(b\). The operation:

1. copies \(b\)'s subject map to fresh binding \(b'\);
2. assigns only \(v\) to \(b'\);
3. leaves every other view assigned to \(b\);
4. leaves \(b\)'s map unchanged.

Therefore every remaining view still reads the same binding and subject values. Coherence and visible state for the remaining group are preserved.

## B.19 Chapter 22, Exercise 3 — Missing dependency

Predicate:

```ts
canArchive(project, environment) {
  return !project.archived &&
    environment.permissions.canArchive(project.id);
}
```

Incorrect fingerprint:

```ts
[project.id, project.revision]
```

If an administrator role is revoked without changing the project revision, the fingerprint remains equal and a cached `true` is reused. The action remains available incorrectly. Include an authorization or permission epoch.

## B.20 Chapter 25, Exercise 6 — Tests are not universal proof

A generated test suite samples finitely many values, expressions, and execution paths. Transitivity is a universal statement over all admissible triples. Passing samples raises confidence in the implementation and can find counterexamples, but does not logically entail the universal property. A proof derives the property from definitions and assumptions for all cases.

---

# Appendix C — Mechanization roadmap

This appendix sketches how to formalize the pure core in a proof assistant. It does not claim that the supplied implementation has been machine verified.

## C.1 Scope the first mechanization narrowly

Begin with:

- finite atomic names;
- a well-formed nominal preorder;
- static capabilities;
- top, bottom, union, intersection, and difference;
- total decidable named refinements treated as abstract predicates;
- direct matching only;
- no translators, React, or arbitrary JavaScript.

This yields useful theorems without importing host-language effects.

## C.2 Core definitions in Lean-like notation

```lean
inductive Ty where
  | top
  | bottom
  | atom : AtomId → Ty
  | capability : CapabilityId → Ty
  | union : Ty → Ty → Ty
  | inter : Ty → Ty → Ty
  | diff : Ty → Ty → Ty
  | refine : RefinementId → Args → Ty → Ty

structure Ref where
  atom : AtomId
  value : Value

structure Registry where
  nominal : AtomId → AtomId → Prop
  nominal_decidable : DecidableRel nominal
  capability : Env → Ref → CapabilityId → Prop
  capability_decidable : ∀ e r c, Decidable (capability e r c)
  refinement : RefinementId → Args → Env → Ref → Prop
  refinement_decidable : ∀ p a e r, Decidable (refinement p a e r)
```

Denotation as a predicate:

```lean
def Denote (R : Registry) (e : Env) : Ty → Ref → Prop
  | .top, _ => True
  | .bottom, _ => False
  | .atom a, r => R.nominal r.atom a
  | .capability c, r => R.capability e r c
  | .union a b, r => Denote R e a r ∨ Denote R e b r
  | .inter a b, r => Denote R e a r ∧ Denote R e b r
  | .diff a b, r => Denote R e a r ∧ ¬ Denote R e b r
  | .refine p args base, r =>
      Denote R e base r ∧ R.refinement p args e r
```

Semantic subtyping:

```lean
def Subtype (R : Registry) (a b : Ty) : Prop :=
  ∀ e r, Denote R e a r → Denote R e b r
```

## C.3 Basic theorem suite

```lean
theorem subtype_refl : Subtype R t t := ...

theorem subtype_trans :
  Subtype R a b → Subtype R b c → Subtype R a c := ...

theorem inter_left : Subtype R (.inter a b) a := ...

theorem union_upper :
  Subtype R a c → Subtype R b c →
  Subtype R (.union a b) c := ...

theorem refine_base :
  Subtype R (.refine p args base) base := ...

theorem diff_disjoint :
  ∀ e r,
    Denote R e (.diff a b) r →
    ¬ Denote R e b r := ...
```

Most proofs are short introductions and eliminations over propositions.

## C.4 Evidence datatype

```lean
inductive Evidence (R : Registry) (e : Env) (r : Ref) : Ty → Type
  | top : Evidence R e r .top
  | atom : R.nominal r.atom a → Evidence R e r (.atom a)
  | capability : R.capability e r c →
      Evidence R e r (.capability c)
  | unionLeft : Evidence R e r a →
      Evidence R e r (.union a b)
  | unionRight : Evidence R e r b →
      Evidence R e r (.union a b)
  | inter : Evidence R e r a → Evidence R e r b →
      Evidence R e r (.inter a b)
  | diff : Evidence R e r a → (¬ Denote R e b r) →
      Evidence R e r (.diff a b)
  | refine : Evidence R e r base →
      R.refinement p args e r →
      Evidence R e r (.refine p args base)
```

The type of `Evidence` indexes proofs by the exact registry, environment, reference, and type.

## C.5 Decidable matcher

```lean
def match (R : Registry) (e : Env) (r : Ref) :
  (t : Ty) → Decidable (Denote R e t r)
```

Because every atomic capability and refinement proposition is assumed decidable, `match` follows the type structure.

The central theorem may be definitional:

```lean
theorem match_sound
  (h : match R e r t = isTrue proof) :
  Denote R e t r := proof
```

An extracted Boolean matcher can erase proof terms while retaining the theorem in the formal development.

## C.6 Nominal closure

Instead of assuming `nominal` is already reflexive and transitive, formalize declarations and path reachability:

```lean
inductive Reachable (edge : AtomId → AtomId → Prop) :
  AtomId → AtomId → Prop
  | refl : Reachable edge a a
  | step : edge a b → Reachable edge b c → Reachable edge a c
```

Prove reflexivity and transitivity. A verified closure algorithm can then be shown equivalent to `Reachable` for finite atom IDs.

## C.7 Subtype algorithm

For the full Boolean algebra over finite atoms, one can compile expressions into Boolean formulas or finite sets and prove:

```lean
algSubtype R a b = true ↔ Subtype R a b
```

For opaque refinements, complete implication is unavailable. Treat each refinement instance as an independent proposition and prove completeness only for the propositional abstraction.

A future BDD formalization would prove that reduced ordered diagrams preserve Boolean denotation and that implication testing corresponds to unsatisfiability of \(a\land\neg b\).

## C.8 Translation formalization

Add a translator relation:

```lean
structure Translator where
  source : AtomId
  target : AtomId
  run : Env → Ref → Option Ref
  sound : ∀ e r r',
    run e r = some r' →
    Denote R e (.atom target) r'
```

A path is a list with composable endpoints. Prove by induction that successful path composition produces a reference satisfying the final target atom.

Least-cost path correctness can be imported from a verified graph library or proved separately under finiteness and nonnegative costs.

## C.9 Input-context state machine

Formalize state and events as inductive types. Keep promise continuations abstract; track a set of resolved context IDs.

Invariant:

```lean
∀ q, resolutionCount history q ≤ 1
```

Prove preservation by case analysis on transitions.

Acceptance safety combines:

- state-machine active-ID invariant;
- matcher soundness;
- translator path soundness;
- revalidation premise.

## C.10 Link reducer

State:

```lean
structure LinkState where
  views : ViewId → Option BindingId
  bindings : BindingId → Option (Role → Option SubjectId)
```

Well-formedness:

```lean
∀ v b, views v = some b → ∃ subjects, bindings b = some subjects
```

Define `subjectOf`. Prove coherence directly from function equality, then prove each reducer preserves well-formedness and the visible-subject condition for unlink.

This is a small and promising first mechanization because the state space is clear and the theorems are product-relevant.

## C.11 Host-language boundary

The following remain assumptions unless reimplemented or verified:

- JavaScript refinement bodies;
- identity key correctness;
- translator side effects;
- environment dependency completeness;
- runtime schema parsers;
- React event delivery;
- server authorization.

A small verified kernel can check declarative evidence, but it cannot make arbitrary host functions trustworthy by declaration.

## C.12 Choosing a proof assistant

### Coq

Software Foundations offers a structured path through operational semantics, type systems, and proofs [SoftwareFoundations]. Coq has mature extraction and many verified data-structure libraries.

### Agda

Programming Language Foundations in Agda presents type-safety and language metatheory with proofs as programs [PLFA]. Agda's dependent pattern matching makes evidence structures direct.

### Lean

Lean has modern tooling, a large mathematical library, and good support for executable definitions. It is attractive for proving the algebra and generating test vectors, although direct TypeScript extraction may require custom tooling.

### Isabelle/HOL

Isabelle is strong for inductive semantics and code generation, particularly if the team prefers classical higher-order logic.

Choose based on team fluency and integration, not fashion.

## C.13 Incremental mechanization plan

1. finite atom calculus and denotation;
2. evidence matcher and soundness;
3. nominal closure algorithm;
4. normalization laws;
5. link reducer invariants;
6. input-context settlement;
7. translator path soundness;
8. method specificity and unique maximal dispatch;
9. generated fixtures consumed by TypeScript tests;
10. optional proof-certificate checker in JavaScript.

---
# Appendix D — Glossary

**Acceptance.** The act of satisfying an active input context with a direct or translated presentation reference.

**Action.** User-facing command data, usually containing a stable ID, label, enabled state, and application verb.

**Action method.** A rule that contributes or selects actions based on semantic signatures and command scope.

**Action table.** A named scope organizing action methods, often with inheritance from parent tables; analogous in purpose to a subset of CLIM command-table facilities.

**Ad hoc hierarchy.** A subtype or derivation relation independent of the host language's class hierarchy.

**Algebraic law.** An equation or ordering property such as commutativity, idempotence, or absorption.

**Ambiguity.** A dispatch or translation state with several incomparable best candidates and no declared preference.

**Antisymmetry.** Order property: \(x\leq y\) and \(y\leq x\) imply \(x=y\).

**Atom.** A fundamental named presentation role associated with one representation family.

**Atomic fact mask.** A bitset encoding nominal atoms and static capabilities known for a reference.

**Behavioral subtyping.** A notion of subtyping based on preserving expectations and behavioral contracts of supertype clients.

**BDD.** Binary decision diagram, a graph representation of Boolean functions. Reduced ordered BDDs are canonical for a fixed variable order.

**Binding coherence.** The invariant that views sharing one subject binding observe the same subject values for every role.

**Bottom type.** The type \(\bot\) with empty denotation.

**Bounded search.** Search limited by depth, states, time, or cost to guarantee operational control even when a graph contains cycles.

**Cache soundness.** The property that reusing a cached decision gives the same semantic result as reevaluation under stated fingerprint assumptions.

**Capability.** A semantic proposition or supported protocol that may be implemented by otherwise unrelated atomic types.

**Characteristic predicate.** A Boolean predicate that is true exactly for members of a set.

**Clause.** A compiled conjunction of required facts, excluded facts, and refinements; several clauses represent a union.

**CLIM.** Common Lisp Interface Manager, the primary historical source for presentations, presentation types, input contexts, translators, command tables, and output recording used in this book.

**Closure operator.** A monotone, extensive, and idempotent function on an ordered set. Nominal ancestor expansion is a closure operator.

**Command.** A named operation with semantic arguments. In PBUI, commands are usually represented as serializable verbs interpreted by the application.

**Command context.** Dynamic semantic state determining which commands or action tables are active.

**Commitment.** Final activation of an acceptable occurrence, including current-context checks and revalidation.

**Completeness.** For a decision algorithm, the property that every semantically true judgment in the claimed fragment is recognized.

**Complement.** Relative set negation \(\Omega\setminus A\). Its meaning depends on the chosen universe.

**Compositional semantics.** Semantics in which the meaning of a compound expression is determined by the meanings of its parts.

**Congruence.** An equivalence relation respected by an operation or constructor.

**Context ID.** Unique token identifying one active input context and preventing stale asynchronous completion from settling another.

**Conversion.** General transformation between representations. This book prefers the more specific term *translation* for acceptance-related conversions.

**Countermodel.** One model in which a universal claim is false.

**Decidability.** Existence of a terminating algorithm that determines whether a proposition holds.

**Denotation.** Mathematical meaning of an expression. A presentation type denotes a set of semantic references.

**Dependency completeness.** The assumption that equal declared fingerprints imply equal predicate outcomes for identity-equivalent references.

**Dependency fingerprint.** Stable tuple summarizing every state component on which a cached predicate result depends.

**Difference type.** A base-relative exclusion \(\tau\setminus\sigma\).

**Direct match.** Membership success without translation.

**Dispatch.** Selection or combination of behavior based on semantic arguments.

**Discriminated union.** TypeScript union whose variants are distinguished by a literal field such as `type`.

**DNF.** Disjunctive normal form: a union of conjunctions. Naive conversion can grow exponentially.

**Domain identity.** Sameness of the real application object denoted by references.

**Effectful predicate.** A predicate performing I/O, mutation, or other externally visible effects. It should generally not define synchronous type membership.

**Environment.** Logical snapshot of dynamic application facts used by refinements, translators, and action methods.

**Environment-local subtyping.** Set inclusion that holds in one environment but not necessarily every environment.

**Equivalence class.** Set of all elements equivalent to one representative under an equivalence relation.

**Equivalence relation.** A reflexive, symmetric, and transitive relation.

**Evidence.** Structured witness explaining a successful or failed semantic judgment.

**Evidence erasure.** Removal of proof details when only a value or Boolean result is needed.

**Expression interning.** Reusing one canonical runtime object for equal normalized expressions.

**Extensional equality.** Equality determined by having exactly the same members or behavior, not by identical syntax.

**Fallback identity.** Policy used when no explicit semantic identity exists, such as primitive equality or object-reference identity.

**Guard language.** Restricted declarative predicate language designed for analysis, serialization, and predictable execution.

**Hasse diagram.** Diagram of a finite partial order omitting reflexive and transitively implied edges.

**Identity domain.** Namespace preventing equal key strings in unrelated domains from denoting the same object.

**Identity preservation.** Translator property that source and target denote the same domain object.

**Identity revision.** Version of the observable state of one semantically identified object.

**Immutable registry snapshot.** Validated, frozen collection of semantic declarations with a stable version.

**Implication declaration.** Trusted assertion that one named refinement entails another.

**Input context.** Temporary interaction state describing the semantic object currently requested.

**Intersection type.** Type denoting references satisfying all member types.

**Inversion.** Proof method that derives premises or structural facts from the last rule that could have produced a judgment.

**Join.** Least upper bound in an order; union in the powerset lattice.

**Judgment.** Formal assertion under explicit contexts, such as \(R;e\vdash r:\tau\).

**Lattice.** Partial order in which every pair has a meet and join.

**Link group.** Set of views referring to one shared subject binding.

**Logical view identity.** Identity of one view configuration independent of where it is placed.

**Matcher.** Runtime evaluator producing membership or acceptance evidence.

**Mechanization.** Encoding definitions and proofs in a proof assistant.

**Meet.** Greatest lower bound in an order; intersection in the powerset lattice.

**Method combination.** Policy for composing several applicable methods rather than choosing one.

**Monotone function.** Order-preserving function.

**Multiple dispatch.** Behavior selection using the semantic types of several arguments rather than one receiver.

**Nominal subtype.** Subtype relation based on declared names and edges.

**Normalization.** Rewriting expressions to a canonical or simpler form while preserving denotation.

**Occurrence.** One mounted visual presentation of a semantic reference.

**Occurrence identity.** Identity of one rendered occurrence, separate from domain and React identity.

**Occurrence typing.** Refinement of a variable or occurrence's type using predicates and control-flow facts.

**Open world.** Registry model in which later modules or plugins can add types and methods.

**Output record.** Retained representation of output in CLIM; richer than an ordinary React element.

**Parameterized type.** Family of semantic types indexed by arguments, implemented here as named refinements.

**Partial function.** Function that may be undefined for some inputs.

**Partial order.** Reflexive, transitive, and antisymmetric relation.

**Placement identity.** Identity of one workspace rectangle showing a logical view.

**Presentation.** Association of visual output with an application reference and semantic presentation type.

**Presentation reference.** Tagged pair of atomic semantic role and representation value.

**Presentation type.** Runtime semantic classification used by the interface, not merely a JavaScript representation type.

**Prepared predicate.** Predicate compiled or indexed once for an input-context snapshot.

**Preorder.** Reflexive and transitive relation; syntactic types under semantic subtyping form a preorder before quotienting equivalent expressions.

**Proof obligation.** Claim a component must establish through proof, testing, validation, or explicit trust.

**Proof relevance.** Property that distinct proofs of the same proposition carry operationally meaningful information.

**Protocol.** Named set of semantic operations implemented by multiple representations.

**Quotient set.** Set of equivalence classes formed by treating equivalent elements as one abstract element.

**React identity.** Reconciliation identity controlled locally by React keys and mounted element structure.

**Reference interpreter.** Simple, obviously structured implementation used as a correctness oracle for optimized code.

**Refinement.** Subset of a base type selected by a predicate, possibly parameterized and environment-dependent.

**Registry contract.** Versioned agreement about names and meanings of semantic definitions.

**Registry version.** Identity of one immutable declaration snapshot used to validate caches and persisted expressions.

**Relation.** Set of ordered pairs; identity, subtype, translation, preference, and binding are different relations.

**Representation.** Host-language value carried by a presentation atom.

**Revalidation.** Rechecking applicability at commitment against current state.

**Role map.** Mapping from subject roles such as `primary` or `comparison` to selected domain identities.

**Semantic identity.** Explicit application-level sameness across occurrences and possibly across presentation types.

**Semantic subtyping.** Definition of subtype by inclusion between denoted sets.

**Serializable verb.** Data describing an application command without embedding executable closure state.

**Set-theoretic type.** Type expression interpreted using set operations such as union, intersection, and negation or difference.

**Smart constructor.** Function that builds well-formed syntax and performs safe normalization.

**Snapshot.** Coherent registry or environment state against which evidence is valid.

**Soundness.** Property that every successful algorithmic judgment is semantically true.

**Specificity.** Ordering used to determine which applicable action method is narrower.

**Stable type.** Type whose denotation does not change across a specified class of environment transitions.

**Static capability.** Capability holding for every direct member of an atomic type without inspecting changing state.

**Subject.** Domain selection observed by a logical view, such as its active document.

**Subject binding.** Explicit shared cell containing one or more subject roles.

**Subsumption.** Rule permitting a value of a subtype to be used at a supertype.

**Subtype DAG.** Directed acyclic graph of declared nominal subtype edges.

**Top type.** Type \(\top\) denoting the whole registry universe.

**Translation.** Typed partial computation turning one presentation reference into another role or representation.

**Translation closure.** Acceptance relation including references reachable through allowed translator paths.

**Translator tester.** Cheap predicate determining whether a translator applies to a source value in an environment.

**Trusted computing base.** Components and assumptions not proved by the current formal argument but required for its application.

**Type algebra.** Syntax and operations for constructing presentation type expressions.

**Type evidence.** Proof object showing that a reference belongs to a type expression.

**Type expression.** Runtime data representing an atomic or compound presentation type.

**Union type.** Type denoting references satisfying at least one member type.

**Unique maximal method.** Sole applicable method not strictly less specific than another applicable method.

**Universe.** Collection of semantic references over which type denotations and complement are interpreted.

**Validity token.** Registry and environment version information carried with evidence for later revalidation.

**View binding identity.** Identity of a shared subject-selection cell, distinct from view and placement identity.

**Well-formedness.** Static registry-relative validity of a type expression or declaration.

---

# Appendix E — Bibliography

This bibliography emphasizes primary specifications, research papers, official implementation documentation, and textbooks that support the mathematical and architectural development in this book. Access dates are omitted for stable publications and included only implicitly for continuously updated project documentation.

## E.1 Type theory, logic, order, and semantics

**[Pierce2002]** Benjamin C. Pierce. *Types and Programming Languages*. MIT Press, 2002. A standard introduction to operational semantics, the typed lambda calculus, subtyping, polymorphism, recursive types, and proof techniques. <https://mitpress.mit.edu/9780262162098/types-and-programming-languages/>

**[Harper2016]** Robert Harper. *Practical Foundations for Programming Languages*, second edition. Cambridge University Press, 2016. Develops programming languages from judgments, syntax, dynamics, statics, and structural metatheory. <https://www.cs.cmu.edu/~rwh/pfpl/>

**[Winskel1993]** Glynn Winskel. *The Formal Semantics of Programming Languages: An Introduction*. MIT Press, 1993. Covers structural operational, denotational, and axiomatic semantics together with proof methods. <https://mitpress.mit.edu/9780262231695/the-formal-semantics-of-programming-languages/>

**[DaveyPriestley2002]** B. A. Davey and H. A. Priestley. *Introduction to Lattices and Order*, second edition. Cambridge University Press, 2002. A standard source for preorders, partial orders, lattices, closure systems, and fixed points. <https://www.cambridge.org/highereducation/books/introduction-to-lattices-and-order/0E1B48E1A2A7F94E3B376FD7D9B88A1E>

**[Wadler2015]** Philip Wadler. “Propositions as Types.” *Communications of the ACM* 58, no. 12 (2015): 75–84. Relates propositions, proofs, types, and programs through the Curry–Howard correspondence. <https://doi.org/10.1145/2699407>

**[TheLittleTyper]** Daniel P. Friedman and David Thrane Christiansen. *The Little Typer*. MIT Press, 2018. A dialogue-based introduction to dependent types and proof construction. <https://mitpress.mit.edu/9780262536431/the-little-typer/>

**[HoTTBook]** The Univalent Foundations Program. *Homotopy Type Theory: Univalent Foundations of Mathematics*. Institute for Advanced Study, 2013. An open textbook on dependent type theory, identity types, equivalence, and univalence. <https://homotopytypetheory.org/book/>

**[SoftwareFoundations]** Benjamin C. Pierce et al. *Software Foundations*. Continuously maintained open textbook series using Coq for programming-language semantics, logic, and verified programming. <https://softwarefoundations.cis.upenn.edu/>

**[PLFA]** Wen Kokke, Jeremy G. Siek, and Philip Wadler. *Programming Language Foundations in Agda*. Open textbook using Agda to develop lambda calculi, semantics, and metatheory. <https://plfa.github.io/>

## E.2 CLIM and presentation-based interfaces

**[CLIM2]** Scott E. Hudson, Robert C. McKay, William M. York, Paul T. Withington, and others. *Common Lisp Interface Manager: CLIM Release 2.0 Specification*. 1993. The principal specification for application frames, presentation types, presentations, input contexts, translators, commands, command tables, output recording, and redisplay. <https://bauhh.dyndns.org:8000/clim-spec/index.html>

**[LispWorksCLIM]** LispWorks. *CLIM 2.0 User Guide*. Official product documentation describing application frames, commands, presentation types, translators, output recording, and related facilities. <https://www.lispworks.com/documentation/lw81/clim/clim.htm>

**[McCLIM]** McCLIM Project. *McCLIM User's Manual* and source implementation. McCLIM is a free implementation of the CLIM II architecture and a useful living reference for presentation types and translators. <https://mcclim.common-lisp.dev/static/manual/mcclim.html>

**[Moore2008]** Timothy Moore. “An Implementation of CLIM Presentation Types.” *Journal of Universal Computer Science* 14, no. 20 (2008): 3358–3369. Discusses implementation issues in presentation-type subtype reasoning and parameter handling. <https://doi.org/10.3217/jucs-014-20-3358>

**[RaoYorkDoughty1990]** Ramana Rao, William M. York, and Dennis Doughty. “A Guided Tour of the Common Lisp Interface Manager.” Published in *ACM SIGPLAN Lisp Pointers* 4, no. 1 (1990): 17–37. <https://doi.org/10.1145/121994.121996>

## E.3 Semantic subtyping, refinements, and behavioral substitutability

**[FrischCastagnaBenzaken2008]** Alain Frisch, Giuseppe Castagna, and Véronique Benzaken. “Semantic Subtyping: Dealing Set-Theoretically with Function, Union, Intersection, and Negation Types.” *Journal of the ACM* 55, no. 4 (2008), article 17, 1–64. <https://doi.org/10.1145/1391289.1391293>

**[Castagna2022]** Giuseppe Castagna. “Programming with Union, Intersection, and Negation Types.” 2022. A broad tutorial and survey of set-theoretic type systems and their programming implications. <https://arxiv.org/abs/2111.03354>

**[CDuce]** CDuce Project. *CDuce Language and Documentation*. An implementation of set-theoretic types with unions, intersections, negation, recursive types, and semantic subtyping. <https://www.cduce.org/>

**[GentleSemanticSubtyping]** Giuseppe Castagna and Alain Frisch. “A Gentle Introduction to Semantic Subtyping.” A step-by-step account of deriving a semantic subtyping relation and decision procedure. <https://www.cduce.org/papers/gentle.pdf>

**[LiquidTypes]** Patrick M. Rondon, Ming Kawaguchi, and Ranjit Jhala. “Liquid Types.” In *Proceedings of PLDI 2008*, 159–169. Introduces refinement inference over decidable logical qualifiers. <https://doi.org/10.1145/1375581.1375602>

**[LiquidHaskell]** LiquidHaskell Project. *LiquidHaskell Documentation and Implementation*. Applies refinement typing and SMT-backed verification to Haskell programs. <https://ucsd-progsys.github.io/liquidhaskell/>

**[TobinHochstadtFelleisen2010]** Sam Tobin-Hochstadt and Matthias Felleisen. “Logical Types for Untyped Languages.” In *Proceedings of ICFP 2010*. Presents occurrence typing and the logical structure underlying Typed Racket's control-flow-sensitive refinements. <https://doi.org/10.1145/1863543.1863561>

**[TypedRacket]** Racket Project. *Typed Racket Guide: Occurrence Typing*. Official documentation for predicate- and control-flow-based type refinement. <https://docs.racket-lang.org/ts-guide/occurrence-typing.html>

**[LiskovWing1994]** Barbara Liskov and Jeannette M. Wing. “A Behavioral Notion of Subtyping.” *ACM Transactions on Programming Languages and Systems* 16, no. 6 (1994): 1811–1841. Distinguishes behavioral substitutability from mere representation inclusion. <https://doi.org/10.1145/197320.197383>

## E.4 Decision procedures and set-theoretic implementation techniques

**[Bryant1986]** Randal E. Bryant. “Graph-Based Algorithms for Boolean Function Manipulation.” *IEEE Transactions on Computers* C-35, no. 8 (1986): 677–691. Introduces reduced ordered binary decision diagrams and their canonical representation under a fixed variable order. <https://doi.org/10.1109/TC.1986.1676819>

**[Bryant1992]** Randal E. Bryant. “Symbolic Boolean Manipulation with Ordered Binary-Decision Diagrams.” *ACM Computing Surveys* 24, no. 3 (1992): 293–318. A survey of BDD algorithms and engineering tradeoffs. <https://doi.org/10.1145/136035.136043>

**[ElixirSetTypes]** José Valim. “The Road to Set-Theoretic Types in Elixir.” Elixir project blog, 2022. Announces the design direction and gradual migration strategy. <https://elixir-lang.org/blog/2022/10/05/my-future-with-elixir-set-theoretic-types/>

**[ElixirBDD]** José Valim and the Elixir team. “Lazier BDDs for Set-Theoretic Types.” Elixir project blog, 2025. Discusses implementation pressure from normal forms and lazy BDD-oriented representations. <https://elixir-lang.org/blog/2025/12/02/lazier-bdds-for-set-theoretic-types/>

**[Elixir120]** José Valim. “Elixir v1.20 Released: Now a Gradually Typed Language.” Elixir project blog, June 3, 2026. Describes the first full-language milestone of Elixir's gradual set-theoretic type system. <https://elixir-lang.org/blog/2026/06/03/elixir-v1-20-0-released/>

**[ElixirProtocols]** Elixir Project. *Protocols*. Official language documentation for polymorphism defined independently of one inheritance tree. <https://hexdocs.pm/elixir/protocols.html>

## E.5 Dispatch, protocols, schemas, and implementation precedents

**[ArkType]** ArkType Project. *ArkType Documentation*. A TypeScript runtime type system with set-theoretic operations, introspection, and compiled validation. <https://arktype.io/>

**[ClojureMultimethods]** Clojure Project. *Multimethods and Hierarchies*. Official reference for arbitrary dispatch values, ad hoc derivation, preferences, and multiple-dispatch-like method selection. <https://clojure.org/reference/multimethods>

**[ClojureProtocols]** Clojure Project. *Protocols*. Official reference for named polymorphic operations independent of one concrete class hierarchy. <https://clojure.org/reference/protocols>

**[ClojureSpec]** Clojure Project. *spec Guide*. Official guide to predicate-based specifications, composition, conforming, explanation, and generation. <https://clojure.org/guides/spec>

**[Malli]** Metosin. *Malli*. Data-driven schema library for Clojure and ClojureScript with registries, transformations, validation, explanation, and generation. <https://github.com/metosin/malli>

**[JuliaMethods]** Julia Project. *Methods*. Official manual chapter on generic functions, multiple dispatch, specificity, and ambiguity. <https://docs.julialang.org/en/v1/manual/methods/>

**[JuliaConversion]** Julia Project. *Conversion and Promotion*. Official manual chapter separating dispatch from explicit and implicit representation conversion. <https://docs.julialang.org/en/v1/manual/conversion-and-promotion/>

## E.6 Object-centric and state-identity precedents

**[Portal]** djblue. *Portal*. A Clojure data exploration tool with selectable values, multiple viewers, commands, and viewer applicability predicates. <https://github.com/djblue/portal>

**[GlamorousToolkit]** feenk. *Glamorous Toolkit Documentation*. An object-centric and moldable development environment in which objects expose contextual views, actions, searches, and explanations. <https://book.gtoolkit.com/>

**[FulcroBook]** Tony Kay. *The Fulcro Developer's Guide*. Documents normalized application state, entity idents, graph queries, and multiple views over shared entities. <https://book.fulcrologic.com/>

**[LivelyNext]** Lively Kernel Project. *Lively.next*. A browser-based JavaScript programming environment centered on live objects, inspection, direct manipulation, and editable tools. <https://lively-next.org/>

**[ObservableInspector]** Observable. *Inspector*. A small open-source renderer that displays arbitrary JavaScript values in reactive DOM output. <https://github.com/observablehq/inspector>

## E.7 How to use this bibliography

For a first formal pass, read [Pierce2002], [Winskel1993], and [DaveyPriestley2002] alongside Chapters 5–11. For semantic subtyping, begin with [GentleSemanticSubtyping], then read [FrischCastagnaBenzaken2008] and inspect [CDuce]. For proof-oriented refinement systems, compare [LiquidTypes], [TypedRacket], and [SoftwareFoundations]. For interaction architecture, read the presentation and command chapters of [CLIM2] together with [Moore2008] and the [McCLIM] implementation. For modern engineering precedents, compare [Elixir120], [ArkType], [ClojureMultimethods], [JuliaMethods], [Portal], and [GlamorousToolkit].
