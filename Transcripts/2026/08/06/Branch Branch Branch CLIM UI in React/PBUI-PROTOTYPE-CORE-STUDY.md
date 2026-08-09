---
title: "A Semantic Spine for Exploratory React Interfaces"
subtitle: "Deriving a Minimal Presentation-Based Core for High-Fidelity Design Prototypes"
author: "Architecture study for the PBUI project"
date: "5 August 2026"
lang: en-US
papersize: letter
fontsize: 11pt
mainfont: "Noto Serif"
sansfont: "Lato"
monofont: "DejaVu Sans Mono"
geometry:
  - margin=0.82in
  - headheight=15pt
colorlinks: true
linkcolor: blue
urlcolor: blue
toc: true
toc-depth: 3
numbersections: false
classoption:
  - titlepage
---

# Abstract

This study asks a practical architectural question: what is the smallest amount of engine structure that should be required in the next self-contained React design prototype so that the prototype can explore ambitious graphical and interaction ideas without becoming a dead end?

The question matters because visual prototypes tend to optimize for the first demonstration. They place state wherever a component happens to need it, encode meaning in click handlers, synchronize views by copying values, and model workflows with several loosely related booleans. That is fast for one screen and expensive for the second iteration. Once a prototype contains charts, pipeline editors, document selectors, menus, inspectors, linked views, keyboard interaction, and asynchronous operations, the original shortcuts become the architecture.

The thesis of this document is that an exploratory prototype should be **visually permissive but semantically strict**. The designer should be free to change layout, motion, component anatomy, density, navigation, visual hierarchy, and interaction details. A small semantic spine should remain fixed underneath those experiments. The spine consists of ten principles:

1. Rendered things represent explicit semantic subjects.
2. Domain identity is stable and separate from rendered occurrence identity.
3. Durable state has one owner and belongs to a named state category.
4. User gestures produce semantic intents and serializable commands rather than hidden mutations.
5. Selection is a query over presented subjects rather than a special picker baked into each component.
6. Views expose typed ports, and links connect ports rather than copying arbitrary state.
7. Multi-step interactions have explicit states, cancellation, and completion rules.
8. Effects occur at the boundary; the core transition is deterministic and replayable.
9. Pointer, keyboard, touch, and assistive technology share one behavior contract.
10. The prototype includes inspection, stories, and narrow subscriptions from the beginning.

These principles are derived from several lines of work rather than copied from one framework. Presentation-based systems contribute the idea that displayed output retains semantic meaning. Direct-manipulation research contributes continuous representation, incremental action, and reversibility. The Elm architecture, Redux guidance, and modern React documentation contribute unidirectional state flow, minimal state, pure updates, and disciplined effects. Statecharts contribute explicit modes and valid transitions. WAI-ARIA and WCAG contribute input-independent interaction contracts. Bidirectional transformations contribute laws for synchronized views. Incremental-computation research contributes the requirement that an optimized runtime agree with full recomputation. Open-system and categorical models contribute the idea that components should expose typed boundaries that can be connected without becoming mutually aware.

The result is not a production theorem prover and not a full CLIM reimplementation. It is a small, designer-friendly engine contract that can be implemented in a few focused TypeScript modules. The document provides a reference data model, a React adapter, a chart-pipeline linking example, a folder structure, a prototype evaluation plan, and a migration path toward the richer proof-oriented architecture studied in the companion volumes.

# Plain-language thesis

A good prototype is not one that predicts the final visual design. It is one that lets the visual design change repeatedly without forcing the team to rewrite the meaning of the product each time.

The engine should know that a rectangle is showing document `doc-42`, that two different rectangles may show the same document, that a chart and a pipeline can share only their document selection while retaining independent local settings, and that a user is currently being asked to choose a field. React should decide how those facts look. It should not be the only place where those facts exist.

The proposed prototype therefore separates three questions:

- **What is this?** A document, field, row, view, placement, or port with stable identity.
- **What may happen now?** A command, selection, link, or workflow transition allowed by the current state.
- **How should it look and feel?** The designer's React components, layout, motion, visual states, and interaction treatment.

The first two questions form the semantic spine. The third remains deliberately open.

# Executive summary

## The immediate recommendation

Ask the web designer to build the next self-contained React prototype on a tiny engine with these concrete modules:

```text
src/core/
  ids.ts              branded IDs and subject references
  state.ts            five named state buckets
  commands.ts         serializable user intent
  reducer.ts          pure state transitions
  queries.ts          selection and action predicates
  ports.ts            typed view ports and link graph
  workflow.ts         explicit interaction states
  store.ts            snapshot, dispatch, subscribe
  debug.ts            event log and state inspector

src/react/
  EngineProvider.tsx
  useEngineSelector.ts
  SemanticOccurrence.tsx
  SelectionSurface.tsx

src/features/
  chart/
  pipeline/
  workspace/
```

The designer may choose a different visual component hierarchy. The semantic modules should not import those components.

## The minimum demonstration

The prototype should demonstrate all of the following in one small workspace:

1. One document appears in at least two visually different places.
2. Both places identify the same semantic subject while retaining separate occurrence IDs.
3. Starting a "choose a document" operation highlights every matching mounted occurrence.
4. The operation can be completed by pointer or keyboard and can be cancelled.
5. A chart and a pipeline expose a `primaryDocument` port.
6. Linking those ports makes their document selectors follow one shared binding.
7. Unlinking separates them without changing the document currently shown.
8. Every lasting change appears as a command in a debug log.
9. Reloading or replaying the command sequence reproduces the same durable state.
10. Storybook or an equivalent fixture surface contains the important visual and interaction states.

## What the designer is free to change

The prototype brief should explicitly permit experimentation with:

- page and tile layout;
- direct manipulation, menus, command palettes, drag and drop, or radial controls;
- visual presentation of selection and linking;
- dense versus spacious information design;
- animation and transitions;
- component anatomy;
- responsive behavior;
- color, typography, iconography, and tokens;
- whether the same semantic operation appears in several visual forms.

The core contract does not prescribe a dashboard look, a component library, or a particular interaction aesthetic.

## What should not be improvised

The designer should not invent a new identity rule, copy durable state between components, directly mutate shared state from a click handler, use effects to derive state, hide a multi-step workflow behind several booleans, or create mouse-only semantics. These are not visual decisions. They are engine decisions whose accidental variation makes the prototype difficult to extend.

# Part I - The research problem

# 1. Why visually successful prototypes become engineering dead ends

## 1.1 The prototype optimization function

A normal design prototype is optimized for a short feedback loop:

```text
idea -> visible screen -> stakeholder reaction -> revision
```

That optimization is rational. It encourages direct component state, local event handlers, hard-coded fixture data, and one-off coordination. The first version often needs only enough behavior to communicate a visual idea.

The problem appears when the artifact is also expected to become the foundation of the next artifact. The optimization function changes:

```text
idea -> visible screen -> stakeholder reaction
     -> new feature -> cross-view behavior -> persistence
     -> accessibility -> remote data -> collaboration
```

The original shortcuts now determine the cost of every later experiment. A visual prototype becomes an accidental application framework.

The failure is not that the first prototype was insufficiently abstract. The failure is that it failed to distinguish **visual uncertainty**, which should remain cheap to change, from **semantic invariants**, which should be explicit from the start.

## 1.2 Common failure patterns

### Duplicated identity

A document is represented by a full object in one component, an ID string in another, and an array index in a third. Equality becomes whichever comparison happens to be convenient. Immutable updates produce new object references, and the interface stops recognizing that two occurrences denote the same document.

### State synchronization by effect

A chart stores `selectedDocumentId`. A pipeline stores another copy. Two effects attempt to keep them equal. A later loading state or conditional mount causes an update loop, stale value, or surprising reset.

### Meaning inside event handlers

The only statement that a field chip can be selected is an `onClick` closure attached to that particular chip. The table header, legend, search result, and pipeline output each receive different handlers. Adding a new workflow requires modifying every visual occurrence.

### Impossible modes

A workflow uses independent flags such as:

```ts
isSelecting
isLoading
isConfirming
hasError
isComplete
```

Several combinations have no product meaning, but JavaScript can still represent them. Components accumulate defensive branches for states that should have been impossible.

### Component lifetime as domain lifetime

A semantic fact exists only while a React component is mounted. Virtualization, tab switching, or responsive re-layout unexpectedly destroys the source of truth.

### Accessibility added after behavior

Pointer behavior is implemented first. Keyboard and screen-reader behavior are added later as parallel logic. The variants drift because they do not invoke the same semantic operation.

### Effects as an internal event bus

Effects watch state and set other state. The application becomes a collection of hidden reactions whose ordering depends on render and scheduling details rather than an explicit transition model.

## 1.3 The cost is paid in design freedom

These patterns are commonly described as engineering debt. For a design prototype, the more important cost is **reduced design freedom**.

When meaning is attached to a particular component, the component cannot be replaced freely. When state is copied into several tiles, a new layout must preserve those accidental ownership relationships. When a workflow is encoded in modal implementation details, exploring an inline or spatial alternative becomes a rewrite.

A semantic spine therefore serves the designer. It gives the visual layer fewer hidden responsibilities and makes radical presentation changes safer.

# 2. What must survive a redesign

A useful way to derive a minimum engine is to imagine replacing every visible component. Which facts must remain true after the redesign?

For an analytical workspace, the following usually survive:

- domain entities and their stable identities;
- logical views and the state that makes each view meaningful;
- workspace placements and layout relationships;
- commands that change durable state;
- which operations are currently valid;
- links between explicit aspects of views;
- the current interaction workflow;
- permissions and other capability facts;
- persistence and replay boundaries;
- accessibility semantics of each interaction.

The following may change completely:

- component nesting;
- CSS and token choices;
- whether a command appears in a context menu, toolbar, command palette, drag gesture, or inline control;
- whether a document is represented by a chip, card, thumbnail, label, or spatial region;
- whether linking is initiated through a chain icon, direct manipulation, or a command;
- how many simultaneous occurrences of an entity are visible;
- responsive layout and viewport-specific anatomy.

This distinction leads to the main engineering rule:

> The prototype core should own only facts that must remain meaningful when the entire render tree is replaced.

# 3. A semantic spine, not a miniature production platform

## 3.1 The desired boundary

![The semantic spine separates durable meaning from rendering and external effects.](assets/semantic-spine.png){ width=86% }

The core sits between domain data, interaction, rendering, and effects. It does not attempt to be a complete database, rules engine, collaboration layer, or theorem prover.

A good primitive core provides:

- stable semantic references;
- explicit state ownership;
- pure transitions;
- queryable presented objects;
- typed links;
- explicit interaction modes;
- subscriptions;
- inspection.

A bad primitive core provides:

- a generic abstraction for every future possibility;
- a global registry that any component mutates;
- a style API disguised as engine architecture;
- a large inheritance hierarchy;
- a mandatory query language before simple predicates are useful;
- distributed synchronization before local linking is correct;
- formal terminology without executable laws.

## 3.2 The level of rigor

The prototype does not need machine-checked proofs. It should be arranged so that important properties are easy to state and test:

```text
same ID => same domain subject
one command + one state => one next state
linked compatible ports => one observed binding value
cancelled selection => no durable mutation
unlinked view => retains its current document
pointer and keyboard activation => same semantic intent
replay commands => same durable state
```

This is a useful proof-oriented posture without requiring the designer to work in a proof assistant.

# Part II - Research traditions and their practical lessons

# 4. Presentation-based interfaces: keep meaning attached to output

The Common Lisp Interface Manager organized interaction around presentations: displayed output retained a relationship to an application object and a presentation type. An input context could then ask for an object of a type, and already displayed presentations could become sensitive. CLIM documentation explicitly groups "output with its semantics attached," input contexts, inheritance, and translators as one interaction model [R1].

The valuable lesson is independent of CLIM's dynamic Lisp mechanisms:

> A rendered occurrence should be able to answer what application subject it represents.

This is stronger than giving a DOM node a test ID. A test ID identifies an element for a test. A semantic subject identifies an application object across multiple visual representations.

The next prototype should therefore wrap meaningful output in a small adapter:

```tsx
<SemanticOccurrence subject={documentSubject("doc-42")}>
  <DocumentPill title="Readings" />
</SemanticOccurrence>
```

The `DocumentPill` remains an ordinary visual component. The wrapper registers the occurrence with the engine and gives pointer, keyboard, menu, and selection behavior one shared semantic route.

## 4.1 What not to copy from CLIM

The prototype does not need:

- a dynamic presentation-type hierarchy;
- a command parser;
- global dynamic variables;
- gesture dispatch specialized through a generic-function system;
- a complete output-record history;
- arbitrary translator search.

Those may inspire later work. The minimum result is simply that output is not semantically anonymous.

# 5. Direct manipulation: visible objects, incremental action, reversibility

Shneiderman's direct-manipulation work characterized a style based on continuous representation of the objects of interest, physical actions rather than complex command syntax, and rapid, incremental, reversible operations [R2].

This tradition supplies three constraints for the prototype core.

## 5.1 Operations target visible semantic objects

A user should be able to act on a document, field, tile, or connection where it is already represented. This supports menus, drag gestures, selection modes, and keyboard commands without forcing each visual representation to reinvent object lookup.

## 5.2 Intermediate state is legitimate state

Dragging, linking, selecting, and previewing produce temporary visual feedback. The core must represent an interaction-in-progress rather than treating it as a series of unrelated DOM events.

## 5.3 Reversibility needs command boundaries

An operation can be undone or replayed only if it has a recognizable semantic boundary. A sequence of arbitrary local setters has no stable inverse. A command such as `LinkPorts` or `SetViewDocument` can be logged, validated, reversed, or reapplied.

The core does not need to implement a full undo stack in the first prototype. It should make commands explicit enough that an undo stack is possible later.

# 6. Declarative state: describe valid states, not DOM manipulations

React's current documentation recommends thinking in terms of visual states, avoiding redundant state, and removing combinations that do not correspond to valid interfaces [R3]. It also distinguishes effects as synchronization with external systems rather than a general mechanism for deriving one piece of state from another [R4]. Redux guidance makes the same architectural point at application scale: reducers should be side-effect free, state should be minimal, and additional values should be derived [R5].

These sources converge on a practical rule:

> Store the smallest set of facts needed to reconstruct the interface, and make transitions between valid facts explicit.

## 6.1 Derived data is not a second source of truth

Do not store both:

```ts
selectedDocumentId
selectedDocument
selectedDocumentTitle
isDocumentSelected
```

Store the ID. Resolve the object and title. Derive the Boolean.

## 6.2 Shared state has one owner

React commonly teaches lifting state to a common owner when two components must change together [R6]. For a dynamic workspace, the common owner should not always be a visual parent, because placements and component nesting may change. A semantic store or binding cell can be the owner while React subscribes through a stable snapshot interface [R7].

## 6.3 Effects are edge adapters

Use an effect to subscribe to a browser API, network, storage layer, or non-React system. Do not use effects as a private rule engine:

```ts
// Avoid: copying durable state through render-time synchronization.
useEffect(() => {
  setPipelineDocument(chartDocument);
}, [chartDocument]);
```

The same behavior should be expressed by one binding or one command transition.

# 7. Statecharts: model modes, transitions, and cancellation explicitly

Harel's statecharts extended ordinary state-transition diagrams with hierarchy, concurrency, and communication to model complex reactive systems [R8]. A prototype does not need full statechart tooling to benefit from the central insight: an interaction has a finite set of meaningful modes and explicit events that move between them.

![A simple interaction machine makes valid modes and cancellation visible.](assets/interaction-machine.png){ width=90% }

A link workflow can be represented as:

```ts
type LinkWorkflow =
  | { status: "idle" }
  | { status: "selectingTarget"; sourcePort: PortId }
  | { status: "confirming"; sourcePort: PortId; targetPort: PortId }
  | { status: "committing"; commandId: CommandId }
  | { status: "failed"; error: EngineError; retry: LinkCommand };
```

This union excludes nonsensical combinations. It also tells the designer exactly which states need visual treatment.

## 7.1 State machines are a collaboration artifact

The machine is not merely implementation detail. It provides a common vocabulary for design and engineering:

- What can the user do in each state?
- What is highlighted?
- What owns Escape?
- Can the operation be cancelled?
- What happens if the target disappears?
- What does failure look like?
- Does retry repeat the same command or start over?

The answers can be explored visually while remaining tied to one state model.

# 8. Accessibility: one semantic operation, several input methods

WAI-ARIA Authoring Practices defines common widget patterns in terms of roles, states, properties, and keyboard support [R9]. WCAG 2.2 expresses testable requirements that apply across technologies and devices [R10]. The practical lesson for an experimental interface is not "add ARIA later." It is:

> Pointer, keyboard, touch, and assistive technology should invoke the same semantic operations through different event adapters.

A semantic occurrence might receive activation from:

- pointer click;
- Enter or Space;
- a context-menu key;
- a command palette result;
- a screen-reader control;
- a touch gesture.

All should produce the same intent:

```ts
activateOccurrence({ occurrenceId, gesture: "primary" })
```

The engine decides whether activation completes an active selection, opens an action surface, or invokes the default action. Visual code does not duplicate the policy for each device.

## 8.1 Focus is engine-visible interaction state

The DOM remains responsible for actual focus. The semantic layer should know enough to answer:

- which occurrence is active;
- whether a selection context is open;
- which occurrences are acceptable;
- what keyboard command cancels or commits;
- where focus should return after a modal or menu closes.

This makes accessibility behavior part of the prototype's designed states rather than a patch.

# 9. Component anatomy and stories: document behavior, not only styling

Open UI's research process starts by establishing shared terminology and component anatomy, then derives behavior and events from those parts [R11]. Storybook describes a story as a captured rendered state of a component [R12]. These ideas support two prototype requirements.

## 9.1 Anatomy should be named sparingly

A component should identify meaningful parts needed by behavior, accessibility, or theming:

```text
Tile
  header
  title
  status
  actions
  body
  resize handle
```

It should not expose every wrapper as a permanent public part. The goal is to let the designer explore anatomy while making the actual interaction surfaces reviewable.

## 9.2 Stories should cover semantic states

A story is valuable when a reviewer can decide whether the behavior or appearance is wrong. For the core prototype, required stories include:

- ordinary occurrence;
- acceptable occurrence during selection;
- same subject in two visual forms;
- linked ports;
- link target selection;
- disabled action with reason;
- loading, empty, error, and stale data;
- keyboard focus and high-contrast presentation;
- narrow viewport and overflow;
- interaction failure and retry.

This turns the prototype into a reusable design laboratory rather than a single scripted demo.

# 10. Bidirectional transformations: linking is more than copying values

Bidirectional-transformation research studies paired mappings that read a view from a source and propagate view updates back while satisfying consistency laws. Lens systems formalize expectations such as reading after writing and avoiding destructive no-op updates [R13].

The prototype does not need a lens library. It should inherit the design discipline:

- a view port declares how it reads its local value;
- it declares how a new value updates local state;
- linking connects compatible ports through one explicit binding;
- reconciliation is named when linked ports disagree;
- unlinking preserves a coherent local value.

This is more robust than running two effects that assign into each other's component state.

# 11. Incremental computation: optimize without changing meaning

Incremental-computation systems such as Adapton maintain results as inputs change and define correctness relative to full recomputation [R14]. React's external-store API similarly depends on stable snapshots and explicit subscriptions [R7].

The prototype only needs the simplest consequence:

> Components subscribe to the smallest semantic observation they render, and any cache must produce the same answer as recomputing from current state.

Do not make the entire workspace rerender because one menu opened. Do not place a query result in durable state merely to avoid recomputation. Begin with pure selectors and narrow subscriptions. Add indexes only after measurement.

# 12. Open components: connect boundaries, not implementation details

Research on open systems models systems by their typed boundaries and composes them by connecting compatible interfaces [R15]. The practical, non-mathematical version is straightforward:

- a chart exposes a document input/output port;
- a pipeline exposes a document input/output port;
- the workspace may connect those ports;
- neither component imports or reaches into the other's store;
- each component remains independently renderable and testable.

The port is an engine concept. The visual connector, chain icon, drag target, or linking animation is a design concept.

# Part III - Deriving the core principles

# 13. Derivation method

The principles below are not a wish list. Each is derived by applying three tests.

## 13.1 Redesign survival test

Would the fact remain meaningful if every React component were replaced?

If yes, it belongs in or behind the semantic core. If no, it normally belongs in rendering.

## 13.2 Composition test

Can a new view or workflow participate by declaring a boundary, or must it import and modify existing components?

A core principle should reduce mutual awareness.

## 13.3 Assurance test

Can the desired behavior be stated as a small property and tested without a browser?

The prototype is on solid ground when its essential properties can be tested against plain data.

# 14. Principle 1 - Meaning before pixels

Every interactive domain representation must declare the semantic subject it represents.

```ts
type SubjectRef =
  | { kind: "document"; id: DocumentId }
  | { kind: "field"; id: FieldId }
  | { kind: "view"; id: ViewId }
  | { kind: "placement"; id: PlacementId }
  | { kind: "port"; id: PortId };
```

The subject is stable across visual forms. The same document can appear as a title, card, breadcrumb, chart caption, or search result.

## 14.1 Why it is required

Without a subject, interactions attach to components. With a subject, interactions can be contextual:

```text
"the active workflow accepts a document"
```

rather than:

```text
"this particular pill has an onClick that knows one workflow"
```

## 14.2 Designer interpretation

The designer should ask of every interactive region: "What thing in the product does this represent?" The answer becomes a subject reference. The designer does not need to change the visual component itself into an engine object.

# 15. Principle 2 - Separate subject identity from occurrence identity

A semantic subject may appear more than once. Each mounted appearance is an occurrence.

![One semantic subject can have several independent visual occurrences.](assets/identity-occurrence.png){ width=82% }

```ts
type Occurrence = {
  id: OccurrenceId;
  subject: SubjectRef;
  surface: SurfaceId;
  role?: "label" | "card" | "mark" | "row" | "tile-title";
};
```

## 15.1 Required identities

The prototype should distinguish at least:

| Identity | Meaning |
|---|---|
| Subject ID | The application object, such as document `doc-42` |
| View ID | One logical chart or pipeline configuration |
| Placement ID | One visual placement of a view |
| Occurrence ID | One mounted semantic region |
| Port ID | One named connection boundary on a view |
| Command ID | One attempted durable operation |

React keys may be derived from some of these IDs, but a React key is not the identity model.

## 15.2 Property

```text
If occurrence A and occurrence B have the same subject reference,
then subject-level selections and actions treat them as the same object,
while focus, geometry, and mounting remain occurrence-specific.
```

# 16. Principle 3 - Divide state into five named buckets

![The five state categories prevent accidental duplication and ownership drift.](assets/state-buckets.png){ width=96% }

The prototype should use five categories.

## 16.1 Domain state

Data that exists independently of the interface:

- documents;
- fields and schemas;
- pipeline steps;
- data-source metadata;
- users and permissions.

## 16.2 View state

Durable configuration of a logical view:

- selected document;
- chart encodings;
- pipeline editor settings;
- table columns;
- inspector target.

## 16.3 Layout state

How logical views are arranged:

- placements;
- split ratios;
- active workspace;
- tile size;
- z-order where relevant.

## 16.4 Interaction state

Temporary workflow state:

- menu open at an occurrence;
- selecting a link target;
- dragging a divider;
- pending confirmation;
- command in flight;
- current keyboard focus return target.

## 16.5 Derived state

Values calculated from the other buckets:

- labels;
- whether an occurrence is acceptable;
- available actions;
- highlights;
- linked-group membership;
- display title;
- visible filtered lists.

Derived state should normally be computed, not independently written.

## 16.6 Ownership rule

Every durable fact has one authoritative owner. Other components observe it or focus it through a port. They do not maintain synchronized copies.

# 17. Principle 4 - Gestures become semantic intent, then commands

DOM events are device-specific. Commands are domain-specific.

![Events are translated into semantic commands before durable state changes.](assets/command-loop.png){ width=98% }

A button click might become:

```ts
{ type: "SetViewDocument", viewId, documentId }
```

A drag gesture might become:

```ts
{ type: "LinkPorts", sourcePortId, targetPortId, policy: "prefer-source" }
```

A context-menu item might become:

```ts
{ type: "ArchiveDocument", documentId, expectedRevision }
```

## 17.1 Command requirements

A prototype command should be:

- serializable plain data;
- named for user intent rather than component implementation;
- validated by a central transition;
- logged in development mode;
- independent of a React synthetic event;
- explicit about target IDs and relevant revision.

## 17.2 Reducer requirements

```ts
type Transition = (
  state: EngineState,
  command: Command,
) => Result<{ state: EngineState; effects: EffectRequest[] }, EngineError>;
```

The transition should not call the network, read the DOM, generate random IDs, or depend on current time without receiving those values explicitly.

# 18. Principle 5 - Selection is a query over subjects and occurrences

Selection should be a reusable engine operation:

```ts
const result = await engine.select({
  subjectKind: "document",
  where: subject => !subject.archived,
  scope: "mounted-occurrences",
  prompt: "Choose a document",
});
```

During selection, matching occurrences receive derived visual state. Activating any matching occurrence completes the same workflow.

## 18.1 Minimal query model

The first prototype does not need a relational language. It needs a structured request with an optional predicate:

```ts
type SelectionQuery = {
  subjectKind: SubjectKind | SubjectKind[];
  scope: "mounted-occurrences" | "all-subjects";
  where?: (subject: SubjectRef, snapshot: EngineSnapshot) => boolean;
  exclude?: SubjectRef[];
};
```

The predicate is intentionally local and pure. A later engine may replace it with a reified query AST for serialization and proof. The prototype should at least keep the predicate out of visual components and evaluate it against a coherent snapshot.

## 18.2 Selection result

```ts
type SelectionResult =
  | { status: "selected"; subject: SubjectRef; occurrenceId?: OccurrenceId }
  | { status: "cancelled" }
  | { status: "invalidated"; reason: string };
```

Cancellation and invalidation are normal outcomes, not thrown implementation errors.

# 19. Principle 6 - Links connect typed ports

A view exposes named aspects that may be connected.

```ts
type Port<T> = {
  id: PortId;
  ownerViewId: ViewId;
  name: string;
  valueType: ValueType<T>;
  mode: "read" | "write" | "read-write";
};
```

For the initial prototype:

```ts
chart.primaryDocument: Port<DocumentId>
pipeline.primaryDocument: Port<DocumentId>
```

![Chart and pipeline remain separate views while their document ports share one binding.](assets/linking-ports.png){ width=96% }

## 19.1 Link state

```ts
type LinkEdge = {
  id: LinkId;
  left: PortId;
  right: PortId;
  policy: "require-equal" | "prefer-left" | "prefer-right";
};
```

The durable source of truth is the set of explicit edges. A derived index computes connected binding groups.

## 19.2 Important distinction

Linking a chart and a pipeline does not merge the views. It shares only the named document value. Their chart encodings, pipeline steps, placement IDs, menus, and local interaction state remain independent.

## 19.3 Unlink property

```text
Removing a link changes connectivity but preserves each resulting view's current document value.
```

That behavior should be a reducer test.

# 20. Principle 7 - Multi-step interactions are explicit workflows

Any operation with more than one meaningful phase should have one discriminated state machine.

Examples:

- link target selection;
- drag and drop with validation;
- rename with asynchronous persistence;
- destructive confirmation;
- import preview and commit;
- command palette with nested argument selection.

## 20.1 Required workflow properties

Every workflow declares:

- start event;
- valid states;
- events accepted in each state;
- cancellation behavior;
- completion result;
- failure behavior;
- focus return behavior;
- durable command boundary.

## 20.2 Designer deliverable

For each multi-step feature, include one state table or statechart beside the visual prototype. This is not bureaucracy; it is the list of screens and transitions that need design.

# 21. Principle 8 - Effects stay at the edge

The core transition returns effect requests as data:

```ts
type EffectRequest =
  | { type: "PersistWorkspace"; revision: number }
  | { type: "FetchDocument"; documentId: DocumentId }
  | { type: "CopyToClipboard"; text: string }
  | { type: "Announce"; message: string };
```

An adapter performs them and dispatches result commands.

## 21.1 Why this matters in a prototype

- fixtures can run without a server;
- failure states can be forced;
- commands can be replayed;
- visual stories can render exact pending states;
- network behavior does not leak through every component;
- a later remote backend can replace the local handler.

The prototype may use fake handlers. It should not hide fake effects inside components.

# 22. Principle 9 - Accessibility is a behavior contract

Every interactive semantic operation needs:

- a keyboard route;
- visible focus;
- an accessible name;
- correct native semantics where available;
- a cancellation path;
- status or error announcement when state changes are not otherwise obvious;
- no dependence on color alone;
- pointer target sizing appropriate to the prototype's devices;
- a story or test showing the keyboard state.

## 22.1 Prefer native controls

Use a native button for a button, a native select where its behavior fits, and a native dialog when supported by the chosen browser target. ARIA describes missing semantics; it does not improve an incorrect custom interaction automatically.

## 22.2 Engine advantage

When keyboard and pointer events both translate into the same `ActivateOccurrence` intent, accessibility does not require a second business-logic path.

# 23. Principle 10 - Inspectability is part of the primitive core

A prototype engine should have a development panel that can show:

- current durable state by bucket;
- active interaction state;
- mounted occurrences and their subjects;
- active selection query;
- which occurrences match and why;
- current ports, links, and binding groups;
- the last commands and transition results;
- pending effect requests;
- current revision.

## 23.1 Why inspectability matters to design

A designer exploring a novel interaction needs to know whether a visual inconsistency is caused by CSS, state, identity, linking, or workflow. Without inspection, every bug looks like a component bug and is repaired locally.

## 23.2 Stories as an executable catalogue

The prototype should also expose important states as stories or fixture routes. Storybook is convenient, but a custom fixture gallery is acceptable if it provides deterministic states and accessibility checking.

# Part IV - The minimal engine specification

# 24. Scope of the primitive core

The primitive core should be small enough to understand in one sitting. It is not responsible for:

- backend authentication;
- a general database;
- arbitrary plugin loading;
- multiplayer conflict resolution;
- a formal query language;
- undo history beyond command logging;
- server-side rendering unless already needed;
- production-scale virtualized data;
- universal design-system components.

It is responsible for making later versions possible without reinterpreting existing behavior.

# 25. Reference type model

The following is an illustrative TypeScript model. Names may change; distinctions should not.

```ts
type Brand<Value, Name extends string> = Value & { readonly __brand: Name };

type DocumentId = Brand<string, "DocumentId">;
type ViewId = Brand<string, "ViewId">;
type PlacementId = Brand<string, "PlacementId">;
type OccurrenceId = Brand<string, "OccurrenceId">;
type PortId = Brand<string, "PortId">;
type LinkId = Brand<string, "LinkId">;
type CommandId = Brand<string, "CommandId">;

type SubjectRef =
  | { kind: "document"; id: DocumentId }
  | { kind: "view"; id: ViewId }
  | { kind: "placement"; id: PlacementId }
  | { kind: "port"; id: PortId }
  | { kind: "field"; documentId: DocumentId; name: string };

interface DocumentRecord {
  id: DocumentId;
  name: string;
  revision: number;
}

interface ViewRecord {
  id: ViewId;
  kind: "chart" | "pipeline" | "table" | "inspector";
  title?: string;
  primaryDocumentId: DocumentId | null;
  config: unknown;
}

interface PlacementRecord {
  id: PlacementId;
  viewId: ViewId;
  workspaceId: string;
  rect: { x: number; y: number; width: number; height: number };
}

interface PortRecord {
  id: PortId;
  viewId: ViewId;
  name: "primaryDocument" | string;
  valueType: "DocumentId" | string;
  mode: "read" | "write" | "read-write";
}

interface LinkRecord {
  id: LinkId;
  left: PortId;
  right: PortId;
  policy: "require-equal" | "prefer-left" | "prefer-right";
}
```

# 26. Engine state

```ts
interface EngineState {
  revision: number;

  domain: {
    documents: Record<DocumentId, DocumentRecord>;
  };

  views: {
    byId: Record<ViewId, ViewRecord>;
  };

  layout: {
    placements: Record<PlacementId, PlacementRecord>;
    order: PlacementId[];
  };

  links: {
    ports: Record<PortId, PortRecord>;
    edges: Record<LinkId, LinkRecord>;
  };

  interaction: InteractionState;
}
```

Derived binding groups, labels, selectable occurrences, and available actions do not need to be stored here.

# 27. Command model

```ts
type Command =
  | {
      id: CommandId;
      type: "SetViewDocument";
      viewId: ViewId;
      documentId: DocumentId;
    }
  | {
      id: CommandId;
      type: "LinkPorts";
      left: PortId;
      right: PortId;
      policy: LinkRecord["policy"];
    }
  | {
      id: CommandId;
      type: "Unlink";
      linkId: LinkId;
    }
  | {
      id: CommandId;
      type: "MovePlacement";
      placementId: PlacementId;
      rect: PlacementRecord["rect"];
    }
  | {
      id: CommandId;
      type: "RenameView";
      viewId: ViewId;
      title: string;
    };
```

A command carries semantic identifiers. It does not carry component instances, DOM nodes, callbacks, promises, or events.

# 28. Transition model

```ts
interface AcceptedTransition {
  ok: true;
  state: EngineState;
  effects: EffectRequest[];
}

interface RejectedTransition {
  ok: false;
  error: {
    code: string;
    message: string;
  };
}

type TransitionResult = AcceptedTransition | RejectedTransition;

function transition(state: EngineState, command: Command): TransitionResult {
  switch (command.type) {
    case "SetViewDocument":
      return setViewDocument(state, command);
    case "LinkPorts":
      return linkPorts(state, command);
    case "Unlink":
      return unlink(state, command);
    case "MovePlacement":
      return movePlacement(state, command);
    case "RenameView":
      return renameView(state, command);
  }
}
```

Every command has a focused pure function with tests.

# 29. Binding semantics

For the first prototype, link semantics can be deliberately simple.

## 29.1 Derive connected components

Treat each compatible equality link as an undirected edge between ports. Derive connected components. Each component is one binding group.

```ts
function bindingGroupOf(state: EngineState, portId: PortId): PortId[];
```

For a small workspace, breadth-first search is sufficient. A later implementation may cache components or use union-find for additions.

## 29.2 Read a document port

A document port focuses the owning view's `primaryDocumentId`.

```ts
function readPort(state: EngineState, portId: PortId): DocumentId | null;
```

For a valid linked group, all members should resolve to one value. The transition enforces this property.

## 29.3 Write a linked group

`SetViewDocument` resolves the view's document port, finds its group, and updates every owner view in one transition.

```ts
function setViewDocument(state, command) {
  const port = primaryDocumentPort(command.viewId);
  const group = bindingGroupOf(state, port.id);
  const affectedViews = unique(group.map(port => port.viewId));

  return updateViewsAtomically(
    state,
    affectedViews,
    view => ({ ...view, primaryDocumentId: command.documentId }),
  );
}
```

The exact implementation may store a separate binding value instead. The critical property is atomic coherence, not storage layout.

## 29.4 Link reconciliation

When chart and pipeline currently show different documents, the link command's named policy decides the initial value.

```text
prefer-left   -> use left port's current value
prefer-right  -> use right port's current value
require-equal -> reject unless equal
```

Do not silently use "last rendered" or whichever effect runs last.

# 30. Selection runtime

The engine maintains mounted occurrence records outside durable workspace state:

```ts
interface MountedOccurrence {
  id: OccurrenceId;
  subject: SubjectRef;
  surface: string;
  element?: HTMLElement;
}
```

The DOM element is adapter-local and never persisted.

A selection context contains:

```ts
interface SelectionContext {
  id: string;
  prompt: string;
  query: SelectionQuery;
  startedAtRevision: number;
  returnFocusTo?: OccurrenceId;
}
```

The engine can derive:

```ts
function acceptanceFor(
  occurrence: MountedOccurrence,
  context: SelectionContext,
  snapshot: EngineSnapshot,
): { acceptable: boolean; reason?: string };
```

## 30.1 Commit-time recheck

When a user activates an occurrence, evaluate the query again against the current snapshot. Highlighting is advisory; commit uses current state.

## 30.2 Context ownership

The simplest prototype permits one modal selection context at a time. Starting a second request should reject, queue, or explicitly replace the first. It should not silently orphan the first promise.

# 31. Store and subscription API

```ts
interface EngineStore {
  getSnapshot(): EngineSnapshot;
  subscribe(listener: () => void): () => void;
  dispatch(command: Command): TransitionResult;
  select(request: SelectionRequest): Promise<SelectionResult>;
  cancelSelection(reason?: string): void;
  mountOccurrence(input: MountedOccurrence): () => void;
}
```

React consumes the store through a narrow selector hook:

```ts
function useEngineSelector<T>(
  selector: (snapshot: EngineSnapshot) => T,
  equals: (a: T, b: T) => boolean = Object.is,
): T;
```

A robust implementation can build on `useSyncExternalStore`, whose contract requires explicit subscribe and stable snapshot functions [R7].

# 32. React adapter

```tsx
interface SemanticOccurrenceProps {
  subject: SubjectRef;
  occurrenceId?: OccurrenceId;
  role?: string;
  children: React.ReactNode;
}

function SemanticOccurrence(props: SemanticOccurrenceProps) {
  const engine = useEngine();
  const id = useStableOccurrenceId(props.occurrenceId);
  const state = useOccurrenceState(id, props.subject);

  useLayoutEffect(() => engine.mountOccurrence({
    id,
    subject: props.subject,
    surface: "workspace",
  }), [engine, id, props.subject]);

  return (
    <span
      data-semantic-occurrence=""
      data-subject-kind={props.subject.kind}
      data-selection-state={state.selectionState}
      tabIndex={state.focusable ? 0 : undefined}
      onClick={event => activateOccurrence(engine, id, event)}
      onKeyDown={event => activateOccurrenceFromKeyboard(engine, id, event)}
    >
      {props.children}
    </span>
  );
}
```

This is illustrative. The actual wrapper may support block layout, child cloning, or render props. It should preserve native control semantics rather than wrapping every interactive element in an inappropriate `span`.

# 33. Headless behavior and visual freedom

The engine should expose behavior state as data:

```ts
interface OccurrenceViewModel {
  selectable: boolean;
  selected: boolean;
  focused: boolean;
  actions: ActionViewModel[];
  linkTarget: boolean;
  disabledReason?: string;
}
```

The designer decides how to render it:

```tsx
<DocumentCard
  data-state={selectable ? "selectable" : "idle"}
  emphasized={linkTarget}
  onActivate={activate}
/>
```

Do not make the engine choose CSS classes, animation duration, menu layout, or component composition.

# 34. Example: chart and pipeline document linking

## 34.1 Initial state

```text
Chart view C
  primaryDocument = doc-A
  placement = left tile

Pipeline view P
  primaryDocument = doc-B
  placement = right tile

No link edges
```

## 34.2 User starts linking

The chain control on the chart dispatches a transient intent:

```ts
startWorkflow({
  type: "linkPort",
  sourcePortId: chartPrimaryDocumentPort,
});
```

The workflow enters `selectingTarget`. A query accepts mounted compatible document ports except the source and ports already in the same group.

The UI may highlight the pipeline's selector, tile title, or whole tile. All are visual occurrences of the target port or owning view. The semantic candidate remains the port.

## 34.3 User selects the pipeline

Pointer or keyboard activation returns the target port. The workflow may commit immediately or show a confirmation/preview depending on the design.

The command is:

```ts
{
  type: "LinkPorts",
  left: chartPrimaryDocumentPort,
  right: pipelinePrimaryDocumentPort,
  policy: "prefer-left",
}
```

## 34.4 Reducer behavior

The transition:

1. verifies both ports exist;
2. verifies both carry `DocumentId`;
3. verifies they use equality-cell semantics;
4. adds a link edge;
5. resolves the new group's value using `doc-A`;
6. updates chart and pipeline document state atomically;
7. increments revision;
8. emits persistence and announcement effects.

## 34.5 Later document change

Changing the pipeline selector to `doc-C` dispatches `SetViewDocument` for the pipeline view. The reducer finds the linked group and updates both views in one transition.

## 34.6 Unlink

Removing the link edge separates the graph. Both views currently contain `doc-C`, so each independent component begins with that value. Subsequent changes no longer propagate.

## 34.7 Visual experiments remain open

The designer may represent the relationship with:

- a chain badge;
- a line between tiles;
- matching outline treatment;
- a shared selector region;
- animated propagation;
- a link inspector;
- no persistent visual indicator beyond a status menu.

The state semantics remain the same.

# Part V - Instructions for a design-led implementation

# 35. Separate the prototype into contracts and skins

A useful working rule is:

```text
core files answer "what does it mean?"
feature model files answer "what can this feature do?"
React files answer "what does it look and feel like?"
```

The designer should be able to restyle or replace a React feature without editing the reducer or identity rules.

# 36. Required folder structure

The exact names may vary, but the dependency direction should be visible.

```text
src/
  core/
    ids.ts
    subjects.ts
    state.ts
    commands.ts
    reducer.ts
    selectors.ts
    occurrences.ts
    selection.ts
    ports.ts
    links.ts
    workflow.ts
    effects.ts
    store.ts
    debug.ts
    core.test.ts

  react/
    EngineProvider.tsx
    SemanticOccurrence.tsx
    useEngine.ts
    useEngineSelector.ts
    useSelection.ts
    DebugPanel.tsx

  components/
    primitives/
    data-display/
    workspace/

  features/
    chart/
      model.ts
      ports.ts
      ChartView.tsx
      ChartView.stories.tsx
    pipeline/
      model.ts
      ports.ts
      PipelineView.tsx
      PipelineView.stories.tsx
    linking/
      linkWorkflow.ts
      LinkIndicator.tsx
      LinkStates.stories.tsx

  fixtures/
    workspace.ts
    stories.ts
```

The `core` directory imports no React. The `react` directory adapts the core. Feature React components may import feature model definitions and the adapter.

# 37. The designer's component contract

A design-led component should generally receive:

- display-ready data;
- explicit interaction state;
- semantic callbacks or intents;
- named slots or composition points;
- no access to the entire engine unless it is a feature boundary.

Example:

```ts
interface DocumentSelectorViewProps {
  label: string;
  options: readonly DocumentOption[];
  value: DocumentId | null;
  linkState: "unlinked" | "linked" | "link-target";
  status: "idle" | "loading" | "error";
  onChange(documentId: DocumentId): void;
  onStartLink(): void;
  onUnlink(): void;
}
```

This component can be shown in Storybook without a store. A feature container obtains observations from the engine and translates callbacks into commands.

# 38. Keep interactive components controllable

For important feature state, prefer a controlled visual component:

```tsx
<DocumentSelectorView
  value={view.primaryDocumentId}
  onChange={documentId => dispatch(setViewDocument(view.id, documentId))}
/>
```

Local state is appropriate for purely visual details whose loss does not alter product meaning:

- hover;
- a temporary animation phase;
- measured geometry;
- uncontrolled text while composing before commit;
- local disclosure when the product does not require persistence.

If losing the component during re-layout would be surprising, the state likely belongs above it.

# 39. Use design tokens, but do not make tokens the engine

A token layer should cover visual decisions such as color, typography, spacing, elevation, motion, and density. The Design Tokens Community Group published a stable exchange specification in 2025, which reinforces the value of keeping visual decisions portable between tools [R16].

Tokens do not represent semantic identity, workflow state, or link topology. A `--linked-color` token may style a linked state, but the existence of a link belongs in engine state.

# 40. Story requirements for the prototype

At minimum, provide stories or fixture routes for:

## 40.1 Semantic occurrence

- ordinary;
- selectable;
- rejected;
- same subject in two visual forms;
- focused;
- context menu open.

## 40.2 Document selector

- unlinked;
- linked;
- acting as link source;
- valid target;
- invalid target;
- loading;
- no documents;
- stale document;
- error.

## 40.3 Workspace

- chart and pipeline independent;
- chart and pipeline linked;
- same logical view in two placements;
- narrow viewport;
- overflow;
- keyboard link workflow;
- command failure;
- target disappears during selection.

## 40.4 Debugging

- event log populated;
- active selection query;
- link graph visualization;
- rejected command with reason.

# 41. Accessibility acceptance criteria

The prototype is not accepted if the linking and selection demonstration works only by mouse.

Required:

1. Every action has a keyboard path.
2. Focus is always visible.
3. Starting selection moves or preserves focus predictably.
4. Escape cancels the active interaction and returns focus.
5. Selectable occurrences communicate their state without color alone.
6. A linked-state indicator has text or an accessible name.
7. Errors and completion are announced where appropriate.
8. Native controls are used where their semantics match.
9. The tab order remains coherent when tiles move or duplicate.
10. At least one manual screen-reader pass is recorded.

# 42. Performance requirements appropriate to a prototype

The initial goal is not maximum throughput. It is to avoid architecture that forces global work.

Recommended budgets:

- opening a menu should not rerender every tile;
- changing one view's local configuration should rerender that view and directly linked observations only;
- selection matching should first narrow by subject kind before an arbitrary predicate;
- mounted occurrence registration should be incremental;
- derived labels and actions should not be placed into durable state;
- large fixture lists should support virtualization without changing subject identity;
- the debug panel may be slower but can be disabled outside development.

Measure before adding a complex cache. Every cache should be disposable because pure selectors define the reference answer.

# 43. Required tests without a browser

The following tests should run against plain TypeScript data:

```text
identity keys are stable
commands are serializable
transition does not mutate the input state
invalid port types cannot link
linking propagates the selected value atomically
link insertion order does not change binding membership
unlink preserves current values
an unlinked view changes independently
replaying commands reproduces state
cancelled selection produces no durable command
selection rechecks at commit revision
```

Browser tests then cover focus, keyboard input, DOM registration, and visible states.

# 44. Prototype review questions

A reviewer should be able to ask:

- What semantic subject is under the pointer?
- Which ID proves that two representations are the same object?
- Which state bucket owns this value?
- Which command caused this change?
- Can the transition be replayed without the DOM?
- Is this value stored or derived?
- Which typed port is linked?
- What happens if linked values disagree?
- Which workflow state owns Escape?
- Can the same operation be completed by keyboard?
- Which story demonstrates the failure state?

If the prototype cannot answer these questions, it is still a visual demo rather than a reusable foundation.

# Part VI - Failure modes and counterexamples

# 45. Anti-pattern: component IDs as domain IDs

```tsx
<ProjectCard key={index} id={`card-${index}`} />
```

This identifies a list position, not a project. Reordering changes identity. Use a project ID for the subject and a separate occurrence ID if needed.

# 46. Anti-pattern: state copied through effects

```ts
const [chartDoc, setChartDoc] = useState("A");
const [pipelineDoc, setPipelineDoc] = useState("B");

useEffect(() => setPipelineDoc(chartDoc), [chartDoc]);
useEffect(() => setChartDoc(pipelineDoc), [pipelineDoc]);
```

This has unclear authority and can loop. Use one link binding or an atomic reducer transition.

# 47. Anti-pattern: global click mode

```ts
window.isChoosingDocument = true;
```

This has no owner, cancellation result, prompt, or focus policy. Use an explicit selection context in interaction state.

# 48. Anti-pattern: menus defined by visual components

```tsx
<FieldChip onContextMenu={() => openMenu([
  { label: "Use in chart", onClick: () => ... },
])} />
```

This makes the action available only from one rendering. The feature layer should derive semantic actions for a field; the chip only renders the returned menu model.

# 49. Anti-pattern: one giant context value

A provider that exposes the entire mutable engine state causes broad rerenders and lets every component bypass commands. Expose a stable engine object and selector subscriptions instead.

# 50. Anti-pattern: every visual state is durable state

Hover, measured size, animation progress, and provisional text do not automatically belong in the global store. Use the five state buckets and persistence test.

# 51. Anti-pattern: premature generality

Do not begin with generic category-theory objects, arbitrary graph rewriting, a complete rule engine, or a universal plugin protocol. Begin with document ports, explicit commands, and one selection query. The architecture is successful when later generalization preserves working semantics.

# Part VII - Evaluation and research plan

# 52. Evaluation questions

The next prototype should be evaluated against four dimensions.

## 52.1 Visual plasticity

Can the team radically change component anatomy and layout without editing identity, command, link, or workflow semantics?

## 52.2 Semantic coherence

Do all occurrences of one subject participate consistently in selection and actions? Do linked views remain coherent under change and unlinking?

## 52.3 Interaction completeness

Are the actual modes explicit? Can all workflows cancel, fail, retry, and complete? Do pointer and keyboard use one semantic path?

## 52.4 Extension cost

How many existing files must change to add:

- a new visual occurrence of a document;
- a new view type with a document port;
- a new action on a field;
- a second linking protocol;
- a command-palette surface;
- persistence?

A solid base makes these additive rather than invasive.

# 53. Demonstration scenarios

## Scenario A - Same subject, different appearances

Show `doc-42` as a chart title and pipeline selector. Start document selection. Both become acceptable. Select either. The result contains the same subject ID and the occurrence used.

## Scenario B - Linked document ports

Link chart and pipeline. Change document from either selector. Both views update. Local chart encodings and pipeline steps remain unchanged.

## Scenario C - Duplicate placement

Render the same chart view in two placements. Changing the chart's document updates both placements because they present one logical view. This is distinct from two different linked views.

## Scenario D - Unlink

Unlink chart and pipeline. Both retain the current document. Change one. The other remains unchanged.

## Scenario E - Cancellation

Start link target selection. Press Escape. No link command appears in the durable log. Focus returns to the source control.

## Scenario F - Invalid target

Attempt to link a document port to an incompatible port. The target is not highlighted, and a forged command is rejected by the reducer.

## Scenario G - Failure

Configure the persistence effect to fail. The durable local transition remains defined according to the chosen policy, and the workflow exposes a designed error/retry state.

# 54. Metrics

Useful prototype metrics include:

- number of durable state owners for each fact, target: one;
- number of commands required for the demonstration;
- number of React components importing core transition internals, target: zero;
- number of effects used to derive internal state, target: zero;
- number of required interaction states represented by booleans instead of a union, target: zero for core workflows;
- number of semantic operations without keyboard paths, target: zero;
- number of global rerenders for a local menu operation;
- number of source files edited to add a new occurrence, target: one component plus story;
- percentage of key states available as deterministic stories;
- replay equivalence between initial state plus command log and current durable state.

# 55. Threats and tradeoffs

## 55.1 More structure can slow the first screen

Defining IDs, commands, and a reducer takes longer than local `useState`. The brief limits the core to a small number of operations and provides templates so the cost remains bounded.

## 55.2 A custom engine can duplicate existing libraries

The proposed core deliberately resembles established patterns. A team may implement it with Redux Toolkit, Zustand plus a pure reducer, XState, or another store. The required deliverable is the semantic contract, not original infrastructure.

## 55.3 Opaque predicates remain difficult to analyze

The first selection API permits pure lambdas. This is pragmatic but not serializable or statically optimizable. The follow-on architecture can introduce a reified query language while preserving the same selection surface.

## 55.4 Link semantics can become more complex

Equality of document IDs is simple. Filters, selections, and heterogeneous representations may need lenses, merge policies, or conflict objects. Typed ports and named policies create room for those additions without requiring them now.

## 55.5 Visual wrappers can harm semantics

A generic occurrence wrapper can produce invalid nested interactive markup. The React adapter must support native controls and render-prop integration rather than assuming every occurrence is a `span` with `role=button`.

# Part VIII - Expansion path

# 56. From predicate functions to reified queries

The primitive query:

```ts
where: subject => subject.kind === "field"
```

can later become:

```ts
query.from(Field)
  .where(Field.documentId.eq(context.activeDocumentId))
  .where(Field.kind.in(["number", "integer"]));
```

The engine can then inspect dependencies, index candidates, serialize the query, explain rejection, and prove optimizer equivalence. The prototype's selection state and occurrence model remain unchanged.

# 57. From hand-coded actions to derived rules

Initially:

```ts
function actionsFor(subject, snapshot): Action[]
```

Later, contextual rules can derive actions from subject type, capability, workflow, and state. The visual action-menu model does not need to change.

# 58. From simple workflows to effect programs

Initially, discriminated unions and reducer events model workflows. Later, typed effect programs can express selection, confirmation, command dispatch, and asynchronous waiting under replaceable handlers. The prototype has already separated these operations from React callbacks.

# 59. From graph traversal to incremental link runtime

A small workspace can recompute connected components. Later, explicit link edges support cached connectivity, provenance, collaboration, and portable serialization. The durable model remains valid.

# 60. From property tests to formal models

The primitive core's pure transition and reference selectors can be modeled in Alloy, TLA+, Lean, or Coq without modeling CSS or React. Formalization is optional, but the architecture no longer blocks it.

# 61. From local links to collaborative links

Explicit edges and named reconciliation policies can later acquire actor IDs, logical times, CRDT semantics, or server transactions. Copying state through component effects offers no comparable migration path.

# Conclusion

The next design prototype should not be asked to solve the final architecture. It should be asked to preserve the distinctions that make a final architecture possible.

The core proposal is intentionally modest:

- a subject has a stable semantic identity;
- a rendered occurrence presents that subject;
- durable facts have one owner;
- user intent becomes a command;
- the transition is pure;
- selection is contextual and query-based;
- links connect typed ports;
- workflows have explicit states;
- effects are external;
- React observes and renders the result;
- accessibility and inspection are built into the behavior surface.

These rules do not constrain visual ambition. They protect it. A designer can replace a grid with a canvas, a menu with a spatial command surface, a title bar with direct manipulation, or a chip with a rich embedded visualization while the semantic meaning remains coherent.

The desired prototype is therefore neither a disposable mock nor a prematurely generalized framework. It is a design laboratory with a small semantic spine.

# Appendix A - One-page principle catalogue

| Principle | Plain-language rule | Prototype proof |
|---|---|---|
| Meaning before pixels | Every interactive domain representation says what it represents | Same subject works in several visual forms |
| Separate identities | Object, view, placement, occurrence, and port IDs are different | Duplicate placement does not duplicate view state |
| Five state buckets | Domain, view, layout, interaction, derived | Every stored value has a named owner |
| Commands, not hidden mutation | Gestures become serializable intent | Command replay reproduces durable state |
| Query-based selection | Ask for subjects; do not wire every chip to every workflow | One selection highlights multiple occurrences |
| Typed ports | Share only named compatible state | Chart and pipeline share document, not all state |
| Explicit workflows | Multi-step operations have finite modes | Cancel and failure states are deterministic |
| Effects at boundary | Pure core requests network/storage effects | Fixtures run without external systems |
| One behavior contract | Pointer and keyboard invoke the same intent | Keyboard completes and cancels every workflow |
| Inspectability | State, commands, occurrences, and links are visible | Debug panel explains current behavior |

# Appendix B - Suggested two-week prototype plan

## Days 1-2: semantic foundation

- define branded IDs and subject references;
- define engine state buckets;
- create fixture documents, chart view, pipeline view, and placements;
- implement pure transition and command log;
- add transition tests.

## Days 3-4: React adapter

- implement provider and selector subscription;
- implement occurrence registration;
- add debug panel;
- render chart and pipeline fixtures;
- verify no core file imports React.

## Days 5-6: selection

- implement one modal selection context;
- derive acceptable occurrence state;
- implement pointer and keyboard activation;
- implement Escape cancellation and focus return;
- add selection stories.

## Days 7-8: links

- define document ports;
- implement explicit link edges and connected components;
- implement `LinkPorts`, `SetViewDocument`, and `Unlink`;
- add reducer tests;
- design linked/unlinked/target visuals.

## Days 9-10: refinement

- add loading, error, invalidation, and target-disappears states;
- accessibility pass;
- performance measurement;
- fixture and Storybook coverage;
- record design questions for the next architecture iteration.

# Appendix C - Prototype handoff checklist

## Semantic core

- [ ] IDs are branded or otherwise not accidentally interchangeable.
- [ ] Subject identity is independent of object reference equality.
- [ ] Logical view and placement are separate records.
- [ ] Every lasting change is a serializable command.
- [ ] The reducer is pure and tested.
- [ ] Derived values are not duplicated into durable state without justification.

## Presentations and selection

- [ ] Meaningful rendered objects register semantic occurrences.
- [ ] The same subject can appear in several occurrences.
- [ ] Selection is represented as interaction state.
- [ ] Match is rechecked when selection commits.
- [ ] Cancel returns a typed result and restores focus.

## Links

- [ ] Views expose named typed ports.
- [ ] Link edges are explicit durable records.
- [ ] Reconciliation policy is named.
- [ ] Linked writes are atomic.
- [ ] Unlink preserves current values.
- [ ] Duplicate placement is tested separately from linked views.

## React and UX

- [ ] Core modules import no React.
- [ ] Visual components can be rendered with props in isolation.
- [ ] Pointer and keyboard use one semantic intent path.
- [ ] Important states exist as stories or fixtures.
- [ ] A debug panel exposes commands, state, occurrences, selection, and links.
- [ ] Effects are isolated in handlers.

# Appendix D - Glossary for designers and frontend engineers

**Action**  
A visible opportunity to issue a command, such as a menu item or toolbar control.

**Binding**  
The shared value observed by a compatible group of linked ports.

**Command**  
Plain data describing a requested durable change.

**Derived state**  
A value calculated from authoritative state rather than stored independently.

**Domain state**  
Product data that exists independently of a particular screen.

**Effect**  
Interaction with an external system such as the network, clipboard, timer, browser API, or persistence layer.

**Interaction state**  
Temporary mode such as selecting, dragging, confirming, or waiting.

**Occurrence**  
One mounted visual appearance of a semantic subject.

**Placement**  
One location displaying a logical view.

**Port**  
A named, typed aspect of a view that may be read, written, or linked.

**Presentation**  
A rendered occurrence together with the subject it represents.

**Query**  
A request describing which subjects or occurrences are acceptable.

**Reducer / transition**  
A pure function that validates a command and computes the next state.

**Semantic spine**  
The small engine layer that preserves identity, state, commands, queries, links, and workflows while rendering changes.

**Subject**  
A domain object or engine object such as a document, field, view, placement, or port.

**View**  
A logical application configuration, such as one chart or pipeline, independent of where it is displayed.

**Workflow**  
A multi-step interaction with explicit states and outcomes.

# References

**[R1]** LispWorks. *CLIM User Guide: Presentation Types and Presentation Translators*. The guide organizes presentations around output with semantics attached, input contexts, inheritance, and translators. <https://www.lispworks.com/documentation/lw44/CLIM/html/climguide-2.htm>

**[R2]** Ben Shneiderman. "Direct Manipulation: A Step Beyond Programming Languages." *Computer* 16(8), 1983, pp. 57-69. <https://doi.org/10.1109/MC.1983.1654471>

**[R3]** React documentation. *Reacting to Input with State* and *Choosing the State Structure*. Accessed 5 August 2026. <https://react.dev/learn/reacting-to-input-with-state> and <https://react.dev/learn/choosing-the-state-structure>

**[R4]** React documentation. *You Might Not Need an Effect*. Accessed 5 August 2026. <https://react.dev/learn/you-might-not-need-an-effect>

**[R5]** Redux documentation. *Redux Style Guide*. See the rules on side-effect-free reducers, serializable values, normalized data, treating reducers as state machines, and minimal state. <https://redux.js.org/style-guide/>

**[R6]** React documentation. *Sharing State Between Components*. <https://react.dev/learn/sharing-state-between-components>

**[R7]** React documentation. *useSyncExternalStore*. <https://react.dev/reference/react/useSyncExternalStore>

**[R8]** David Harel. "Statecharts: A Visual Formalism for Complex Systems." *Science of Computer Programming* 8(3), 1987, pp. 231-274. <https://doi.org/10.1016/0167-6423(87)90035-9>

**[R9]** W3C Web Accessibility Initiative. *ARIA Authoring Practices Guide*. <https://www.w3.org/WAI/ARIA/apg/>

**[R10]** W3C. *Web Content Accessibility Guidelines (WCAG) 2.2*. W3C Recommendation. <https://www.w3.org/TR/WCAG22/>

**[R11]** Open UI Community Group. *Getting Involved: Component Research Process*. The process begins with shared terminology and anatomy, then derives behavior and events. <https://open-ui.org/get-involved/>

**[R12]** Storybook documentation. *How to Write Stories*. <https://storybook.js.org/docs/writing-stories>

**[R13]** J. Nathan Foster, Michael B. Greenwald, Jonathan T. Moore, Benjamin C. Pierce, and Alan Schmitt. "Combinators for Bidirectional Tree Transformations: A Linguistic Approach to the View-Update Problem." *ACM TOPLAS* 29(3), 2007. <https://doi.org/10.1145/1232420.1232424>

**[R14]** Matthew A. Hammer, Khoo Yit Phang, Michael Hicks, and Jeffrey S. Foster. "Adapton: Composable, Demand-Driven Incremental Computation." *PLDI 2014*. <https://doi.org/10.1145/2594291.2594324>

**[R15]** John C. Baez and Kenny Courser. "Structured Cospans." *Theory and Applications of Categories* 35, 2020, pp. 1771-1822. <https://arxiv.org/abs/1911.04630>

**[R16]** Design Tokens Community Group. *Design Tokens Format Module 2025.10*. W3C Community Group Final Report, 2025. <https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/>
