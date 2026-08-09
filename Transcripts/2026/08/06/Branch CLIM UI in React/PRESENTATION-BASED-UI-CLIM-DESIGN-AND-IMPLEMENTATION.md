# Presentation-Based UI in React

## CLIM concepts, architectural analysis, and the implemented PBUI extensions

**Project:** `@hyperslop-systems/pbui` and `@hyperslop-systems/datalab-ui`<br>
**Document date:** 2026-07-31<br>
**Audience:** React and TypeScript developers who are new to presentation-based interfaces, and Common Lisp/CLIM developers evaluating the React design<br>
**Status:** Describes the supplied codebase and the extensions implemented with this document

---

## Executive summary

The original PBUI code already contained the essential seed of a presentation-based interface: visible React elements carried typed references, right-clicking those elements opened object-specific actions, and an `accept` operation temporarily made matching presentations selectable. That was a sound architecture. The main problem was not that it was “insufficiently Lisp-like” in syntax. The problem was that several semantic protocols that CLIM keeps distinct had been collapsed into a few JavaScript values:

- a presentation was only `{ type, value }`;
- object identity meant whatever JavaScript allocation happened to provide;
- selection constraints were ad hoc predicates repeatedly executed during rendering;
- actions belonged only to one exact descriptor;
- types had no runtime subtype relation;
- conversions were a flat, first-success list;
- a logical application view and its selected document had one coupled identity.

The implementation now separates those concerns.

At the generic PBUI layer, the project now has:

1. **Semantic presentation identity** with an explicit identity domain and key.
2. **Runtime presentation subtyping** with cycle detection and cached subtype checks.
3. **Reusable presentation selectors** that support arbitrary lambdas, subtype-aware matching, and a preparation phase that runs once per input context.
4. **Operation-scoped identity memoization** for expensive acceptability checks.
5. **Selector-driven action rules** analogous to a small command-table layer, with priorities and local shadowing by stable action ID.
6. **Named, weighted conversion edges** searched as a bounded graph rather than a first-match loop.
7. **Public identity operations**—`identityFor` and `sameObject`—in the PBUI context.
8. **Backward compatibility** for existing inline `types`/`filter` accept requests and legacy conversion functions.

At the Datalab product layer, the project now has:

1. A concrete identity policy for fields, documents, sources, rows, categories, users, tiles, workspaces, stages, and other product objects.
2. Prepared `Set`-based selectors for field-selection interactions that previously performed repeated linear scans.
3. A new **document-selection subject identity**, `documentBindingId`, distinct from both a logical view ID and a tile placement ID.
4. A PBUI-driven link command: press the chain button in a chart or pipeline DocBar, then click another document-bound tile title.
5. Reducers that link, propagate, and unlink document-role selections while preserving independent applications and placements.
6. Persistence and portable-bundle support that preserves linkage without exporting runtime IDs.
7. A Storybook scenario, **Component Library / Organisms / Tile / Linked Document Selectors**, that exercises the interaction.

The central design result is this:

> A chart view and a pipeline view can remain different logical applications, in different tile placements, while observing one shared document-selection subject.

That is the missing identity layer that the original model needed.

This is not a complete reimplementation of CLIM. In particular, it does not yet provide output history, pointer gestures, parameterized presentation type specifiers, multiple inherited command tables, textual parsers, partial commands, or incremental redisplay records. It does, however, establish the protocols needed to add those features without returning to ad hoc component callbacks.

---

## Contents

1. [Why presentation-based interfaces matter](#1-why-presentation-based-interfaces-matter)
2. [A newcomer’s model of CLIM](#2-a-newcomers-model-of-clim)
3. [The identity problem](#3-the-identity-problem)
4. [Mapping CLIM ideas into React and TypeScript](#4-mapping-clim-ideas-into-react-and-typescript)
5. [Architectural review of the original PBUI](#5-architectural-review-of-the-original-pbui)
6. [Design principles used in the implementation](#6-design-principles-used-in-the-implementation)
7. [Generic PBUI implementation](#7-generic-pbui-implementation)
8. [Selector performance and arbitrary lambdas](#8-selector-performance-and-arbitrary-lambdas)
9. [Actions and command-table-style rules](#9-actions-and-command-table-style-rules)
10. [Subtyping and conversion are different relations](#10-subtyping-and-conversion-are-different-relations)
11. [Datalab semantic identity policies](#11-datalab-semantic-identity-policies)
12. [Linking chart and pipeline document selection](#12-linking-chart-and-pipeline-document-selection)
13. [Persistence and portable representations](#13-persistence-and-portable-representations)
14. [First-time experience](#14-first-time-experience)
15. [Worked extension examples](#15-worked-extension-examples)
16. [Testing and validation](#16-testing-and-validation)
17. [Accessibility, serialization, and security](#17-accessibility-serialization-and-security)
18. [Limitations and a practical roadmap](#18-limitations-and-a-practical-roadmap)
19. [File-by-file implementation map](#19-file-by-file-implementation-map)
20. [Glossary](#20-glossary)
21. [References](#21-references)

---

# 1. Why presentation-based interfaces matter

## 1.1 The ordinary widget model

A conventional React interface is usually described in terms of controls and callbacks:

```tsx
<button onClick={() => openPerson(person.id)}>{person.name}</button>
```

This code says that one button invokes one callback. It is local, explicit, and often entirely adequate. The limitation appears when the same domain object is visible in many forms:

- a person name in a table;
- a node in an organization chart;
- an author badge on a document;
- a search result;
- a mention in an activity stream.

If every occurrence manually wires every applicable behavior, interaction knowledge spreads through the rendering tree. “Inspect person,” “message person,” “assign person,” “compare person,” and “use this person as the argument to the current command” become repeated component decisions.

The resulting interface tends to have three pathologies:

1. **Rendering and command knowledge are coupled.** A component must know every interaction that may be applicable to the object it displays.
2. **New global interactions require broad edits.** Adding “select any user visible anywhere” means revisiting every user renderer.
3. **Semantic equivalence is accidental.** Two allocations for the same person may behave as different objects because JavaScript reference identity says they are different.

## 1.2 The presentation-based model

A presentation-based interface changes the unit of composition. Instead of saying only “this DOM node has this callback,” it says:

> This visible occurrence presents application object **O** under semantic presentation type **T**.

The interaction system can then decide what the occurrence means in the current context.

In PBUI, the basic reference remains intentionally small:

```ts
{
  type: "person",
  value: person,
}
```

The difference is that this reference is no longer expected to carry every semantic policy by itself. A registry supplies labeling, description, actions, identity, and type relationships. An active selector describes the current input context. Conversion edges describe alternate interpretations. The React component marks the visible occurrence.

This produces a useful inversion:

- the component says **what object it is presenting**;
- the input context says **what kind of object is currently wanted**;
- the action system says **what operations apply**;
- the identity protocol says **when two references denote the same application object**.

## 1.3 A communication medium, not merely a component library

Ciccarelli’s work on presentation-based user interfaces frames the interface as a shared communication medium in which system and user manipulate structured presentations of abstract objects. CLIM operationalizes that approach: semantic output can later become input. A value that the system displayed five seconds ago is not merely pixels; it remains associated with the object and type that produced it.

That idea is more important than any individual CLIM macro. It suggests a general design rule:

> Preserve semantics at the boundary where information becomes visible.

React is well suited to this because visible occurrences are already explicit component boundaries. The challenge is that React, JavaScript, and TypeScript do not supply CLIM’s runtime type lattice, generic presentation methods, output history, or dynamic input contexts. Those protocols must be modeled deliberately.

---

# 2. A newcomer’s model of CLIM

CLIM is large. It includes panes, streams, graphics, layout, commands, menus, dialogs, output recording, redisplay, and input editing. This document concentrates on the parts relevant to PBUI.

The most useful mental model has six pieces:

1. application objects;
2. presentation types;
3. presentation occurrences;
4. input contexts;
5. translators and commands;
6. output records and redisplay.

## 2.1 Application objects

An application object is the domain value the program cares about: a student, document, file, graph node, field, row, or pipeline step. Its identity and lifecycle belong to the application.

The visual representation is not the object. A student may be shown as a name, a portrait, a row, or a form. All of those can refer to the same application object.

This distinction matters immediately in React. A rendered object literal, a Redux entity, a server DTO, and a memoized projection may all represent the same domain entity while having different JavaScript references.

## 2.2 Presentation types

A CLIM presentation type is a semantic UI type. It is related to the application’s object classes, but it is not merely a host-language static type annotation.

Presentation types can define or inherit behavior for:

- displaying an object (`present`);
- accepting textual or pointer input (`accept`);
- testing whether an object belongs to the type;
- testing subtype relationships;
- describing the type;
- highlighting and refined hit testing;
- maintaining input history.

CLIM presentation types form a type lattice. If `night-student` is a subtype of `student`, an input context requesting a `student` can accept a presented `night-student`. Type specifiers may also have parameters and options. For example, an integer presentation type can be refined by bounds, while display options can select a base or description.

The crucial point is that a presentation type is **runtime semantic information**. TypeScript’s compile-time types are erased; they cannot by themselves make a DOM occurrence selectable as a supertype.

## 2.3 Presentation occurrences

CLIM defines a presentation as an association among:

1. the underlying application object;
2. its presentation type;
3. its visual representation.

A presentation is also an output record. This means it occupies a particular region in output history and can participate in hit testing and later input.

One object can therefore have many presentation occurrences. The distinction is essential:

- **object identity:** which domain object is denoted;
- **occurrence identity:** which visible rendering was clicked.

PBUI now preserves this distinction during memoized acceptance. It may cache the fact that two occurrences denote the same acceptable object, but when the user commits by clicking one occurrence, PBUI resolves again and returns that clicked occurrence’s payload.

## 2.4 `present` and `accept`

At a high level, `present` emits a visual representation with semantics attached. `accept` requests an object of a presentation type.

An `accept` request can be satisfied in more than one way:

- textual input can be parsed;
- an already visible matching presentation can be clicked;
- a translator can convert another visible presentation into the requested type.

This is one of CLIM’s most powerful unifications. A command argument does not have to know whether it came from a text field, menu, completion system, or pointer selection. The command asks for a semantic type.

PBUI currently implements the pointer-selection part. Its `accept()` returns a promise that resolves to a typed presentation reference or `null`:

```ts
const result = await pbui.accept({
  prompt: "Choose a field",
  selector: presentationSelectors.type("field"),
});
```

The promise resolver remains in a React ref rather than Redux because functions are runtime control state, not serializable application state.

## 2.5 Input contexts and sensitivity

When CLIM is accepting a value, it establishes an input context. Presentations that match the context become sensitive, typically with visual highlighting and pointer behavior.

An input context is more than a list of exact type names. It may involve:

- subtype matching;
- type parameters;
- nested contexts;
- translator availability;
- gestures and modifier keys;
- presentation testers.

PBUI’s `PresentationSelector` is the implemented analogue. It identifies target types, controls subtype matching, and permits arbitrary predicates prepared for one accept operation.

```ts
interface PresentationSelector<Values, Environment> {
  id?: string;
  types: PresentationType<Values> | readonly PresentationType<Values>[];
  includeSubtypes?: boolean;
  cache?: "none" | "identity";
  where?: (reference, environment) => boolean;
  prepare?: (context) => (reference) => boolean;
}
```

This is deliberately a protocol rather than a single callback. The protocol creates a place for performance policy, environment capture, identity, and type relationships.

## 2.6 Presentation translators and testers

A CLIM presentation translator maps an object presented under one type into an object and type usable in another context. Translators can have:

- a source type;
- a destination type;
- a command table;
- a gesture;
- documentation;
- a tester restricting applicability;
- priority.

For example, a displayed student might translate to a `show-transcript` command when selected with a particular gesture. A numeric presentation might translate into another numeric type.

PBUI separates two related ideas:

- a **selector** restricts whether a candidate is acceptable;
- a **conversion edge** changes the candidate’s semantic interpretation.

The implementation supports named conversion edges with cost and priority. It does not yet model gestures, command-producing translators, or nested presentation choice.

## 2.7 Commands and command tables

CLIM commands are structured representations of user intent. Their arguments have presentation types. Command tables organize commands and the interaction styles that invoke them. Tables can be inherited and used to share command sets among modes or applications.

This is materially different from embedding closures in every displayed object. A command can be invoked by menu, pointer translator, command line, or accelerator while retaining one semantic representation.

PBUI’s product verbs already followed an important part of this pattern: descriptors produce serializable verbs rather than directly mutating state. The new action-rule layer adds another part. Rules select presentations and contribute actions globally; descriptor-local actions shadow inherited rules by stable action ID.

It is best described as **command-table-style**, not as a complete CLIM command-table implementation. There are no named table objects, parent table graphs, modes, command parsers, or accelerators yet.

## 2.8 Output recording and output history

CLIM records output in an output-record tree. Presentation records add semantics to that output. Output history allows previously displayed semantic output to remain available for interaction.

React differs sharply here. React normally represents only the current virtual tree and current DOM. Once an occurrence unmounts, PBUI does not retain a semantic output record for it. Scrolling virtualization may also remove occurrences that remain conceptually in a list.

This difference explains why PBUI is presently a **presentation-marked current UI**, not a complete output-history system.

## 2.9 Incremental redisplay and unique IDs

CLIM’s incremental redisplay can identify pieces of output using a unique ID and compare cache values to determine what changed. React reconciliation has a family resemblance: keys identify sibling occurrences across renders, and props/state determine updates.

The analogy is useful but dangerous:

- a React `key` identifies an occurrence for reconciliation within a parent;
- a CLIM redisplay unique ID identifies output for redisplay;
- a PBUI semantic identity identifies an application object;
- a Datalab `viewId` identifies a logical application view;
- a Datalab placement ID identifies geometry.

They should not be collapsed into one “ID” merely because all may be strings.

---

# 3. The identity problem

## 3.1 Common Lisp has several equality relations

Common Lisp programmers are accustomed to choosing among equality predicates such as `eq`, `eql`, `equal`, and `equalp`. CLOS instances also have stable object identity in the running image. This does not eliminate application identity questions, but it makes the distinction visible in the language and programming culture.

JavaScript offers strict equality, `Object.is`, and application-defined comparison. For objects, ordinary equality is reference identity. Two separately decoded values are not equal even when they carry the same database ID:

```ts
const a = { id: "person-1", name: "Ada" };
const b = { id: "person-1", name: "Ada Lovelace" };

Object.is(a, b); // false
```

A presentation system cannot assume that allocation identity is domain identity.

## 3.2 There is no single identity in a UI

The implemented design distinguishes at least seven identities:

| Identity | Example | Purpose |
|---|---|---|
| Domain object identity | document `doc-42` | Determines whether references denote the same application object |
| Presentation type | `field`, `datum`, `tile` | Determines semantic UI interpretation |
| Presentation occurrence | the second row’s clickable cell | Determines which visible occurrence was activated |
| React reconciliation key | `row-42` under one list | Preserves component occurrence across renders |
| Logical view identity | chart view `view-a` | Identifies one open application configuration |
| Placement identity | tile node `leaf-b` | Identifies one rectangle in a workspace layout |
| Shared subject identity | document binding `binding-c` | Identifies a selection/state facet observed by multiple views |

A robust UI model names these identities separately and defines explicit transitions between them.

## 3.3 Semantic identity in PBUI

The generic descriptor can now declare identity:

```ts
person: {
  label: (person) => person.name,
  identityDomain: "entity",
  identity: (person) => person.id,
}
```

The registry returns:

```ts
{
  domain: "entity",
  key: "person-1",
}
```

The domain prevents accidental collisions between unrelated key spaces. A document ID and a user ID may both be the string `"1"`; they are not therefore the same object.

Two presentation types can intentionally share a domain. A `person` and an `employee` presentation can both denote the same entity:

```ts
entity: {
  identityDomain: "entity",
  identity: (value) => value.id,
},
person: {
  identityDomain: "entity",
  identity: (value) => value.id,
},
employee: {
  identityDomain: "entity",
  identity: (value) => value.id,
},
```

`registry.sameObject(left, right, environment)` compares domains and keys using `Object.is`.

## 3.4 Fallback identity

When a descriptor does not define identity, PBUI uses:

- the presentation type as the identity domain;
- the presentation value itself as the key.

This gives sensible defaults:

- strings, numbers, booleans, bigints, `null`, and `undefined` compare by value under `Object.is`;
- objects compare by reference;
- unrelated presentation types remain in separate domains.

The fallback is safe but not magically semantic. Applications should define identity for reconstructed DTOs, normalized entities, and values expected to recur across views.

## 3.5 Identity is not structural equality

It is tempting to stringify every value. That is usually wrong.

Two duplicate rows may have equal field values while representing distinct observations. Objects may contain keys in different orders, cyclic references, transient metadata, or fields irrelevant to identity. JSON serialization also loses values such as `undefined`, symbols, and non-JSON objects.

The Datalab datum policy therefore uses:

- a producer-supplied `rowKey` plus document ID when available;
- otherwise the row object reference.

That policy refuses to collapse structurally equal duplicate rows.

---

# 4. Mapping CLIM ideas into React and TypeScript

## 4.1 The architectural crosswalk

| CLIM concept | PBUI implementation | Important difference |
|---|---|---|
| Application object | `reference.value` | May be DTO, ID, projection, or object reference |
| Presentation type | `reference.type` plus runtime registry | TypeScript types alone are erased |
| Presentation occurrence | `<Presentation reference={...}>` DOM/SVG occurrence | No retained output history after unmount |
| Presentation method | descriptor function or registry protocol | Explicit registry dispatch rather than CLOS generic functions |
| `present` | React rendering wrapped in `Presentation` | Renderer remains owned by application components |
| `accept` | `pbui.accept()` promise | Pointer selection only; no general text parser yet |
| Input context | prepared `PresentationSelector` | One active context per provider; no nested context stack yet |
| Presentation tester | `where` or prepared predicate | Explicit preparation and cache policy added |
| Translator | named conversion edge | No gesture or command-table dispatch yet |
| Command | serializable Datalab verb | Effects applied through Redux/application effect layer |
| Command table | action rules with selector, priority, shadowing | No named tables or inheritance graph yet |
| Presentation type lattice | `supertypes` and `isSubtype` | Names only; no parameterized type specifiers yet |
| Output history | not implemented | Only mounted current occurrences are sensitive |
| Incremental redisplay | React reconciliation | React keys are not semantic identities |

## 4.2 Preserve React’s strengths

A React adaptation should not imitate CLIM’s stream architecture literally. React already provides:

- declarative composition;
- component-local rendering;
- state subscriptions;
- reconciliation;
- platform accessibility primitives;
- an ecosystem for async data and routing.

The useful adaptation is to add semantic protocols at the edges, not to replace React with a Lisp-machine simulation.

Accordingly, PBUI keeps renderers in components. Descriptors do not generate arbitrary React trees. They label, describe, identify, and contribute serializable actions. The `Presentation` wrapper attaches semantics to an occurrence rendered by ordinary React.

## 4.3 Compensate for TypeScript erasure

A discriminated union gives excellent compile-time inference:

```ts
interface PresentationValues {
  field: FieldRef;
  doc: string;
  tile: TileRef;
}

type Reference = PresentationReference<PresentationValues>;
```

But the browser cannot ask TypeScript whether `employee` is a subtype of `person`. Runtime behavior needs runtime data:

```ts
createPresentationRegistry(descriptors, {
  supertypes: {
    employee: ["person"],
    person: ["entity"],
  },
});
```

The implementation validates this graph for cycles at registry creation and caches subtype queries.

## 4.4 Keep application effects serializable

The original project made a strong choice: actions carry verbs, not closures that mutate product state. This supports:

- tracing;
- persistence and replay;
- testing descriptors as pure functions;
- separating menu applicability from effect execution;
- future remote or collaborative command transport.

The new action rules preserve that choice. Arbitrary lambdas decide applicability, but the resulting operation remains a serializable verb.

---

# 5. Architectural review of the original PBUI

## 5.1 What was already strong

The original system had several unusually good boundaries.

### 5.1.1 Domain-neutral generic package

The root PBUI package did not import Redux, Datalab model types, routing, or server APIs. The product package owned its vocabulary and effects. That separation should be retained.

### 5.1.2 Typed presentation vocabulary

`PresentationReference<Values>` used a mapped discriminated union, preserving the relation between a type name and its value type. This is the right TypeScript foundation.

### 5.1.3 Presentation wrappers for DOM and SVG

The same semantic wrapper could mark text, blocks, and SVG groups. That is important for chart marks, where a datum occurrence is not a normal HTML button.

### 5.1.4 Promise-based accept operation outside Redux

The pending resolver lived in a ref. The active request lived in React state. This correctly separated serializable world state from ephemeral control flow.

### 5.1.5 Product verbs rather than direct descriptor effects

Descriptors returned action metadata and verbs. The provider delegated performance to `onPerform`. This is a better foundation than direct store access from every descriptor.

### 5.1.6 Distinction between views and placements

Datalab already separated `AppView` from layout leaves. Multiple placements could show one logical view, while an independent duplicate could create a second view. This distinction made the new binding layer possible.

## 5.2 The original generic constraints

The original `AcceptRequest` was:

```ts
interface AcceptRequest<Values> {
  types: PresentationType<Values> | readonly PresentationType<Values>[];
  prompt: string;
  filter?: (reference: PresentationReference<Values>) => boolean;
}
```

This permitted arbitrary lambdas, but it supplied no lifecycle or policy. A filter could perform a linear search, allocate objects, read mutable state, or execute expensive work every time a presentation rendered.

The original conversion algorithm:

1. checked exact requested types;
2. iterated conversion functions in registration order;
3. accepted the first direct conversion to a requested type.

It could not represent:

- multiple conversion steps;
- relative cost;
- priority;
- named edges for diagnostics;
- cycle control;
- environment-dependent conversion.

The descriptor registry dispatched by exact type only. It had no:

- object identity;
- subtype relation;
- selector-driven actions;
- shared action rules;
- cross-type equivalence.

## 5.3 The original product constraint

An `AppView` contained:

```ts
interface AppView {
  id: ViewId;
  appId: AppId;
  documents: Record<string, DocId>;
  title?: string;
}
```

A layout leaf contained a `viewId`. This yielded two useful modes:

- **linked duplicate placement:** two leaves with the same `viewId`;
- **independent duplicate:** a copied `AppView` with a new `viewId`.

Neither mode expresses the desired relationship between a chart and a pipeline:

- sharing a `viewId` is impossible because they are different applications and configurations;
- copying the view makes their document selections independent;
- relying on one global active document makes every ambient view move together and loses explicit per-view choice.

The missing abstraction was not another tile mode. It was a shared identity for one facet of view state: the document-role selection.

---

# 6. Design principles used in the implementation

## 6.1 Separate denotation from occurrence

A presentation reference denotes an application object under a type. A mounted `Presentation` is one occurrence. Caches may use denotation identity, but activation must honor the selected occurrence.

## 6.2 Make expensive work preparable

An arbitrary lambda is not inherently slow. Repeating setup inside it is slow. The API should make this pattern natural:

```ts
prepare: () => {
  const allowed = new Set(expensiveSource.map(keyOf));
  return (candidate) => allowed.has(keyOf(candidate));
}
```

## 6.3 Scope caches to an interaction

A process-global cache is likely to become stale. An input context has a natural lifetime: from `accept()` until commit or abort. Memoization belongs there.

## 6.4 Keep subtyping and conversion distinct

A subtype is already a member of the requested semantic category. A conversion produces another interpretation. Conflating them causes surprising action and input behavior.

## 6.5 Use stable action IDs as method names

Action labels are presentation text. IDs are semantic slots. A local action with ID `inspect` can override an inherited `inspect` rule without depending on English labels or array positions.

## 6.6 Give every state-sharing relationship its own identity

A logical view, a placement, an application object, and a shared state subject are different things. Sharing one does not imply sharing the others.

## 6.7 Preserve serializable state boundaries

Selectors and predicates may be lambdas because they are ephemeral interaction policy. Persisted layout, verbs, bundles, and world state remain data.

## 6.8 Add compatibility paths deliberately

The new selector form coexists with the old inline form. Legacy conversion functions still work. Existing saved layouts omit `documentBindingId` and fall back to one binding per view.

---

# 7. Generic PBUI implementation

## 7.1 Semantic identity descriptors

`PresentationDescriptor` now has two optional identity hooks:

```ts
interface PresentationDescriptor<Value, Environment, Verb> {
  label(value: Value, environment: Environment): ReactNode;
  describe?(value: Value, environment: Environment): unknown;
  actions?(value: Value, environment: Environment): readonly PresentationAction<Verb>[];
  tone?: PresentationTone;

  identity?(value: Value, environment: Environment): unknown;
  identityDomain?: string;
}
```

The environment parameter is important. Identity should usually be stable and environment-independent, but some applications resolve aliases or scoped IDs through an environment. The protocol does not prohibit that. The documentation recommendation is stricter:

> Prefer identity functions that depend only on immutable value fields. Environment-dependent identity should be rare, deterministic, and coherent for the lifetime of one accept operation.

The registry exposes:

```ts
identityFor(reference, environment): PresentationIdentity;
sameObject(left, right, environment): boolean;
```

The provider also exposes environment-bound versions through `usePbui()`.

## 7.2 Runtime subtype graph

Registry creation accepts:

```ts
interface CreatePresentationRegistryOptions<Values, Environment, Verb> {
  supertypes?: Partial<{
    [Type in PresentationType<Values>]: readonly PresentationType<Values>[];
  }>;
  actionRules?: readonly PresentationActionRule<Values, Environment, Verb>[];
}
```

Example:

```ts
const registry = createPresentationRegistry(descriptors, {
  supertypes: {
    employee: ["person"],
    person: ["entity"],
  },
});
```

The implementation:

- rejects cycles during registration;
- supports multiple direct supertypes;
- walks transitively;
- memoizes `(actual, expected)` results;
- treats every type as a subtype of itself.

This is a name-level runtime lattice. It does not yet support parameterized type specifiers such as bounded integers or `sequence` element types.

## 7.3 Presentation selectors

The reusable selector protocol is:

```ts
interface PresentationSelector<Values, Environment> {
  readonly id?: string;
  readonly types:
    | PresentationType<Values>
    | readonly PresentationType<Values>[];
  readonly includeSubtypes?: boolean;
  readonly cache?: "none" | "identity";
  readonly where?: (
    reference: PresentationReference<Values>,
    environment: Environment,
  ) => boolean;
  readonly prepare?: (
    context: PresentationSelectorPrepareContext<Values, Environment>,
  ) => (reference: PresentationReference<Values>) => boolean;
}
```

Raw selectors default `includeSubtypes` to `true`, mirroring CLIM’s subtype-oriented input contexts.

The context passed to `prepare` provides:

```ts
interface PresentationSelectorPrepareContext<Values, Environment> {
  environment: Environment;
  identityFor(reference): PresentationIdentity;
  sameObject(left, right): boolean;
  isSubtype(actual, expected): boolean;
}
```

This allows a selector to precompute against semantic identities rather than inventing local equality rules.

## 7.4 Typed selector factory

Datalab exports a typed factory:

```ts
export const presentationSelectors =
  createPresentationSelectorFactory<PresentationValues, PbuiEnvironment>();
```

It provides exact-type helpers with value inference:

```ts
presentationSelectors.type("field", {
  where: (field, reference, environment) => {
    // field is FieldRef
    return environment.fieldsFor(field.docId).some((f) => f.name === field.name);
  },
});
```

and unions:

```ts
presentationSelectors.any([
  "field",
  "source",
  "doc",
  "datum",
]);
```

Typed factory selectors are exact by design. A callback typed for `PersonValue` should not silently receive an `EmployeeValue` unless the application has explicitly modeled the value relationship. Raw selectors remain the tool for subtype-polymorphic rules:

```ts
{
  types: "entity", // includes subtypes by default
}
```

## 7.5 Selector preparation order

`preparePresentationSelector` performs the following work once:

1. normalizes one or many target types;
2. removes duplicate types;
3. constructs an exact-type `Set`;
4. captures the subtype policy;
5. invokes `selector.prepare(context)` once.

For each candidate, matching occurs in this order:

1. type or subtype check;
2. `where(reference, environment)`, if present;
3. prepared predicate, if present.

Cheap type rejection therefore happens before application predicates.

## 7.6 Accept request forms

The preferred form is:

```ts
await pbui.accept({
  prompt: "Choose a field",
  selector: presentationSelectors.type("field", { ... }),
});
```

The old form remains supported:

```ts
await pbui.accept({
  prompt: "Choose a field",
  types: "field",
  filter: (reference) => true,
  prepare: (context) => () => true,
  cache: "identity",
  includeSubtypes: true,
});
```

`selectorForAcceptRequest()` normalizes the inline form into a selector. `acceptRequestTypes()` lets UI such as the accept banner display target types without knowing which representation was used.

## 7.7 Prepared matcher lifecycle

When `accept(request)` begins, PBUI:

1. normalizes the selector;
2. captures the provider environment;
3. prepares the selector;
4. creates operation-scoped conversion and identity caches;
5. stores the request and matcher as the active accept state.

If preparation throws, the accept promise rejects and no broken input context is installed.

The environment is a coherent snapshot for that accept operation. A provider re-render with a different environment does not silently reprepare the in-progress selector. This avoids changing the meaning of highlighted candidates halfway through one gesture. Applications that require live acceptability should abort and restart the input context deliberately.

## 7.8 Public context identity helpers

`PbuiContextValue` now includes:

```ts
identityFor(reference): PresentationIdentity;
sameObject(left, right): boolean;
```

This is useful outside selectors. Examples include:

- showing whether two panels denote the same object;
- building a local selected-object set;
- preventing a drag target from accepting the object already present;
- reconciling references from separate API responses.

The helpers bind the current provider environment, so components do not need direct registry access.

---

# 8. Selector performance and arbitrary lambdas

## 8.1 Arbitrary lambdas are retained

The implementation does not replace lambdas with a restrictive query language. Applications can still express conditions such as:

- “a field whose current semantic type is quantitative”;
- “a tile that is document-bound, is not this view, and belongs to another binding group”;
- “a user who is online, is not the current principal, and belongs to this organization”;
- “a geometry object inside the current viewport”;
- “a row whose timestamp is inside the brushed interval.”

The performance improvement comes from giving those lambdas a lifecycle.

## 8.2 Original repeated-scan cost

The original Encoding and Pipeline selectors used logic equivalent to:

```ts
filter: (reference) => {
  const field = fields.find((candidate) => candidate.name === reference.value.name);
  return field ? acceptedTypes.includes(field.type) : false;
}
```

Let:

- `P` be the number of mounted field presentations evaluated while the input context is active;
- `N` be the number of fields in the schema.

The worst-case selector cost is approximately `O(P × N)`. React may re-render those occurrences more than once, multiplying the work.

## 8.3 Prepared-index cost

The migrated version builds an index once:

```ts
selector: presentationSelectors.type("field", {
  cache: "identity",
  prepare: () => {
    const acceptedNames = new Set(
      fields
        .filter((field) => accepts.includes(field.type))
        .map((field) => field.name),
    );
    return (field) => acceptedNames.has(field.name);
  },
}),
```

The cost becomes approximately:

- `O(N)` once to build the set;
- `O(1)` average membership per candidate;
- `O(P)` across candidates.

Total: `O(N + P)` rather than `O(N × P)`.

The same pattern applies to:

- maps indexed by ID;
- interval trees for ranges;
- compiled regular expressions;
- normalized case-folded strings;
- pre-resolved permission sets;
- spatial indices;
- bitsets for feature flags.

## 8.4 Identity memoization

A prepared selector may opt into:

```ts
cache: "identity"
```

PBUI then memoizes whether a presentation is acceptable using:

- presentation type;
- identity domain;
- identity key.

The cache is scoped to one accept operation. Two separately allocated references to the same field or person can share the acceptability result.

This is particularly useful when the same object appears in:

- a table and a chart;
- multiple linked placements;
- a breadcrumb and a content pane;
- repeated labels in a graph;
- a menu and a canvas.

## 8.5 Why the cache includes presentation type

Two references may denote one domain object while being presented under different types. The selector or conversion behavior may differ by type. Therefore the memo key is effectively:

```text
(presentation type, identity domain, identity key)
```

not merely `(domain, key)`.

## 8.6 Why commitment re-evaluates

Suppose two occurrences have the same semantic identity but carry different projections:

```ts
const compact = {
  type: "person",
  value: { id: "1", name: "Ada" },
};

const detailed = {
  type: "person",
  value: { id: "1", name: "Ada Lovelace", biography: "..." },
};
```

Identity memoization can safely say both are acceptable after evaluating one. It must not return the first occurrence’s payload when the user clicks the second.

PBUI therefore uses two paths:

- `isAcceptable(reference)` may use the identity cache;
- `accept(reference)` runs resolution again and returns the clicked occurrence or its conversion.

One extra evaluation at commitment preserves occurrence correctness while retaining render-time savings.

## 8.7 Cache safety rules

Use `cache: "identity"` when the predicate is a pure function of:

- semantic object identity;
- the prepared environment snapshot;
- immutable data captured during preparation.

Do not use it when acceptability differs between occurrences of the same object, for example:

- one occurrence is inside a special drop zone and another is not;
- eligibility depends on DOM geometry;
- the occurrence carries a transient per-render flag not included in identity;
- the predicate intentionally consumes or counts evaluations.

In those cases, use `cache: "none"`, the default.

## 8.8 Avoid allocation in hot predicates

The prepared predicate may run for every mounted presentation render. Prefer:

```ts
const allowed = new Set(keys);
return (reference) => allowed.has(keyOf(reference));
```

Avoid:

```ts
return (reference) =>
  largeArray.map(expensiveProjection).includes(keyOf(reference));
```

Also avoid reading broad Redux state from the predicate. Capture the relevant snapshot in the component before `accept()` or expose a narrow immutable value in the PBUI environment.

## 8.9 Conversion-search cost

For one candidate, named conversions are searched as a bounded weighted graph. With maximum depth `D`, reachable nodes `V`, and conversion edges `E`, the implementation’s simple sorted queue is suitable for the small vocabularies expected here. It is not intended as a general million-node graph engine.

Important limits include:

- default maximum depth: `6`;
- semantic visited map prevents repeating an equal-or-more-expensive state;
- conversion edges are indexed by exact source type;
- lower total cost is considered first;
- priority and registration order provide deterministic tie behavior.

If a future product registers hundreds of conversion edges, the queue can be replaced with a binary heap without changing the public protocol.

---

# 9. Actions and command-table-style rules

## 9.1 The descriptor-only limitation

Originally, actions were obtained only from the exact presentation descriptor:

```ts
registry.actionsFor(reference, environment)
```

This forced common operations such as Inspect and Watch into many descriptors. It also made descriptor-less types unable to participate in shared commands.

## 9.2 Action rules

The registry now accepts rules:

```ts
interface PresentationActionRule<Values, Environment, Verb> {
  id: string;
  selector: PresentationSelector<Values, Environment>;
  priority?: number;
  actions(reference, environment):
    | PresentationAction<Verb>
    | readonly PresentationAction<Verb>[]
    | null
    | undefined;
}
```

A rule combines:

- a semantic selector;
- optional priority;
- a pure action-producing function.

Example:

```ts
{
  id: "inspect-entities",
  selector: { types: "entity" },
  actions: (reference) => ({
    id: "inspect",
    label: "Inspect",
    verb: {
      type: "inspect",
      id: reference.value.id,
    },
  }),
}
```

Because raw selectors include subtypes, this rule applies to `person` and `employee` when they inherit from `entity`.

## 9.3 Ordering and shadowing

Rules are sorted by descending priority and stable registration order. Descriptor-local actions are collected first. Every action ID is emitted at most once.

This gives the following policy:

1. exact descriptor-local definitions win;
2. higher-priority shared rules contribute next;
3. lower-priority rules fill remaining slots;
4. duplicate IDs are suppressed.

A local action can therefore customize a common command:

```ts
person: {
  actions: (person) => [{
    id: "inspect",
    label: "Inspect locally",
    verb: { type: "inspect", id: person.id },
  }],
}
```

The shared `inspect` rule remains available for types that do not override it.

## 9.4 Datalab rules

Datalab registers two common rules:

- Inspect for the full presentation vocabulary;
- Add to watchlist for a selected watchable subset.

Many product descriptors already define one of these actions in a deliberate menu position. The binding adapter maps those local verbs to stable IDs `inspect` and `watch`, allowing them to shadow the common rule without changing existing menu ordering.

The descriptor-less `chart` presentation now receives common actions automatically.

## 9.5 Why rules still return verbs

An action rule may use an arbitrary lambda to decide applicability, but it returns a serializable verb. This is the correct split:

- runtime applicability can depend on environment and object details;
- performed intent remains inspectable, traceable, testable, and replayable.

## 9.6 What a fuller command-table system would add

A future implementation could introduce named command tables:

```ts
interface CommandTable {
  id: string;
  parents: string[];
  actionRules: PresentationActionRule[];
  commands: CommandDefinition[];
  accelerators: AcceleratorDefinition[];
}
```

The provider could select active tables by application mode. The system would then need explicit rules for:

- table inheritance linearization;
- command and translator shadowing;
- gesture conflicts;
- menu grouping;
- enabled versus visible states;
- command argument acquisition.

The present action-rule layer is intentionally smaller.

---

# 10. Subtyping and conversion are different relations

## 10.1 Subtyping means “already is”

If `employee` is a subtype of `person`, an employee presentation is already acceptable in a person input context. No new object is produced.

```text
employee  <:  person  <:  entity
```

The selected reference remains an `employee` reference unless application code deliberately normalizes it.

## 10.2 Conversion means “can be interpreted as”

A category presentation may be interpreted as the field it categorizes:

```text
cat --category-to-field--> field
```

This creates a new presentation reference:

```ts
{
  id: "category-to-field",
  from: "cat",
  to: "field",
  cost: 1,
  convert: (reference) => ({
    type: "field",
    value: {
      docId: reference.value.docId,
      name: reference.value.field,
    },
  }),
}
```

A category is not a subtype of field. It merely carries enough information to produce one.

## 10.3 Named conversion definitions

The generic protocol supports:

```ts
interface PresentationConversionDefinition<Values, Environment, From, To> {
  id: string;
  from: From | readonly From[];
  to: To;
  cost?: number;
  priority?: number;
  convert(reference, environment): PresentationReference<Values, To> | undefined;
}
```

Costs must be positive finite numbers. The result’s runtime type must match the declared `to` type; malformed edges are ignored.

## 10.4 Weighted paths

Consider:

```text
alias --5--> person
alias --1--> handle --1--> person
```

The graph chooses the two-edge path with total cost `2` rather than the direct path with cost `5`. This allows applications to express preferences such as:

- exact semantic conversions are cheaper than lossy projections;
- local data is cheaper than a remote lookup;
- preserving type detail is cheaper than erasing it;
- a canonical conversion is preferred over a compatibility fallback.

## 10.5 Cycle control

Conversions can form cycles:

```text
A -> B -> C -> A
```

The search records the best known cost for each semantic state identified by:

```text
(type, identity domain, identity key)
```

A state reached again at equal or greater cost is not expanded. `maxConversionDepth` provides an additional hard bound.

## 10.6 Legacy conversions

Existing function conversions remain valid:

```ts
(reference) => convertedOrUndefined
```

They are treated as cost-1 edges explored after indexed named edges for a node. New code should prefer named definitions because names, source types, destination types, and costs make the graph auditable.

## 10.7 Current exact-source behavior

Named conversion edges are indexed by exact source presentation type. A conversion registered from `person` does not automatically run for an `employee` presentation merely because `employee` is a subtype.

This is a deliberate conservative boundary in the first implementation. Automatically applying a conversion body typed for a supertype requires the application to guarantee that subtype values satisfy the supertype’s runtime value contract. A future API can add an explicit option such as `includeSourceSubtypes: true` rather than assuming it.

---

# 11. Datalab semantic identity policies

`packages/datalab-ui/src/pbui/registry.ts` binds every product descriptor to an identity policy.

## 11.1 Field

```text
domain: field
key: [docId, field name]
```

Two field chips allocated separately for the same document and field name denote one field. `docId: null` remains meaningful for an ownerless/ambient field.

## 11.2 Source

```text
domain: source
key: [kind, drop, stream, dataset, version, path]
```

The key covers all fields that distinguish a source reference.

## 11.3 Document

```text
domain: document
key: docId
```

The document object itself lives in normalized world state; presentation values use the ID.

## 11.4 Category

```text
domain: category
key: [docId, field, value]
```

A category value is scoped by its field and document.

## 11.5 Datum

```text
domain: datum
key:
  rowKey present  -> [docId, rowKey]
  otherwise       -> row object reference
```

Chart hits now supply `hit.datumKey`. Table rows supply their row index. The fallback refuses unsafe structural equality.

A production data engine with stable primary keys should pass those keys instead of positional indices, especially if sorting, filtering, or live insertion can change row positions.

## 11.6 Geometry and steps

Geometry currently uses the primitive geometry value. Pipeline steps use the step ID.

## 11.7 Users, tokens, members, and uploads

- user: user ID;
- token: token ID;
- member: `[drop, user ID]`;
- upload: `[batch ID, path]`.

Token identity intentionally never contains a secret. The presentation value itself omits secrets, preserving the existing structural security boundary.

## 11.8 Tile

```text
domain: tile-placement
key: placementId
```

A tile presentation denotes the visible placement that was clicked. It does **not** use:

- `viewId`, because two placements can display one logical view;
- `documentBindingId`, because different views may share one selection subject;
- `docId`, because changing the shown document should not change the identity of the tile occurrence.

The `TileRef` carries all three identities explicitly:

```ts
interface TileRef {
  placementId: string;
  viewId: string;
  documentBindingId: string;
  docId: DocId | null;
  docBound: boolean;
  // ...menu facts
}
```

## 11.9 Workspace, stage, and trace entry

- workspace: workspace ID;
- stage: stage ID;
- trace entry: sequence number.

These policies make identity visible at registration rather than implicit in allocation patterns scattered through components.

---

# 12. Linking chart and pipeline document selection

## 12.1 The requirement

The desired interaction is:

1. a chart and pipeline remain different applications;
2. each retains its own title, configuration, placement, and menu;
3. switching the selected document in either switches it in the other;
4. either can be detached later;
5. ordinary independent duplication remains independent;
6. same-view linked duplication remains stronger sharing.

## 12.2 Why sharing `viewId` is wrong

A logical view contains application identity and configuration. A chart view and pipeline view cannot share one `viewId` without making one object pretend to be two applications.

Even two chart views may need different encodings while following the same document. Sharing the entire view would over-couple them.

## 12.3 Why a global active document is insufficient

Datalab already has `activeDocId`, used as a fallback when a view has no explicit primary document. Turning that into the only linkage mechanism would couple every ambient view. It would not represent multiple independent linked groups:

```text
Group A: chart + pipeline -> document α
Group B: table + encoding -> document β
```

A first-class subject identity supports any number of groups.

## 12.4 The third identity layer

`AppView` now has:

```ts
interface AppView {
  id: ViewId;
  appId: AppId;
  documents: Record<string, DocId>;
  documentBindingId?: string;
  title?: string;
}
```

Interpretation:

- `id` identifies the logical application view;
- layout leaf ID identifies a placement;
- `documentBindingId` identifies the document-role selection subject.

The helper:

```ts
function documentBindingId(view: AppView): string {
  return view.documentBindingId ?? view.id;
}
```

makes old saved views backward compatible. A legacy view forms a one-view binding identified by its own view ID.

## 12.5 New-view behavior

Every newly constructed view receives a fresh binding ID. Therefore independent views are independent by default.

An ordinary `duplicateView`:

- creates a new `viewId`;
- copies the current document-role map;
- creates a fresh `documentBindingId`.

The two views initially show the same document but can later diverge.

A `createLinkedDuplicate` creates another placement with the same `viewId`. Since it is the same logical view, it naturally has the same binding and all other view state.

## 12.6 Propagation

`setViewDocument` now:

1. finds the source view;
2. computes its effective binding ID;
3. updates the named role on every view with that binding ID.

```ts
for (const view of Object.values(state.views)) {
  if (documentBindingId(view) !== bindingId) continue;
  if (docId) view.documents[role] = docId;
  else delete view.documents[role];
}
```

All document roles participate, not only `primary`. This matters for future applications with roles such as `left`, `right`, `baseline`, or `reference`.

## 12.7 Linking groups

`linkViewDocuments({ sourceViewId, targetViewId })` merges entire binding groups, not merely two individual views.

At link time:

1. the source and target are resolved;
2. no action occurs if they already share a binding;
3. a fresh binding ID is minted;
4. every member of either old group receives the fresh binding ID;
5. every member receives a copy of the source group’s document-role map.

The source-wins rule is explicit and deterministic. It matches the user’s gesture: “make that tile follow this tile’s current document selection.”

A different product could offer a conflict dialog or role-by-role merge. The reducer policy should remain explicit either way.

## 12.8 Unlinking

`unlinkViewDocuments(viewId)`:

- gives that logical view a fresh binding ID;
- copies its current document-role map;
- leaves all other members in the old group.

The detached view therefore stays on the document it was showing at the moment of unlink. Subsequent selection changes diverge.

If one logical view has multiple linked placements, unlinking the view affects all of those placements. That is correct: placements do not own independent document selection.

## 12.9 PBUI-driven interaction

The DocBar chain button starts this input context:

```ts
const result = await pbui.accept({
  prompt: "LINK DOCUMENT SELECTION — click the title of another document-bound tile",
  selector: presentationSelectors.type("tile", {
    id: "different-document-bound-view",
    cache: "identity",
    prepare: () => (tile) =>
      tile.docBound &&
      tile.viewId !== viewId &&
      tile.documentBindingId !== bindingId,
  }),
});
```

This demonstrates the intended architecture:

- the DocBar requests a semantic `<tile>`;
- every tile title is already a presentation;
- the selector refines eligibility;
- PBUI highlights/selects matching occurrences;
- the resulting typed reference supplies the target `viewId`;
- the reducer performs the state relationship.

No tile registry, DOM query, callback prop chain, or event bus is needed.

## 12.10 Why the title presentation is the target

The tile title already represents the tile as an object and owns the tile menu. Reusing it keeps one semantic hit target. The prompt tells the user to click another document-bound tile title.

A future design could make the entire tile frame a nested presentation. CLIM has rules for choosing the innermost applicable presentation when presentations are nested. PBUI does not yet implement a formal nesting-resolution algorithm, so one clear target is preferable.

## 12.11 Generalizing subject bindings

`documentBindingId` is a concrete first implementation of a broader pattern:

```ts
interface SubjectBindings {
  documentSelection?: string;
  timeRange?: string;
  filterSet?: string;
  cursor?: string;
  rowSelection?: string;
  colorScale?: string;
}
```

Each subject identity can have independent link/unlink semantics. For example:

- two charts share a brushed time range but not documents;
- a map and table share row selection;
- several panels share filters but have independent zoom;
- chart and pipeline share document selection and filter set but not cursor.

Do not replace these with one generic `linkedGroupId` unless the product truly wants all state facets coupled.

---

# 13. Persistence and portable representations

## 13.1 Local persisted layout

`documentBindingId` is optional in the persisted `AppView` validator. Existing layouts remain valid. New layouts preserve the runtime binding IDs directly.

A persisted file containing two views with the same binding ID reconstructs the relationship. Applications should still treat the ID as opaque.

## 13.2 Portable bundles use equivalence classes

Portable bundles should not leak runtime IDs. They now represent binding equivalence with a dense integer:

```ts
interface PortableView {
  app: string;
  binding?: number;
  title?: string;
  documents: Record<string, number>;
}
```

Example:

```json
{
  "views": [
    { "app": "chart", "binding": 0, "documents": { "primary": 0 } },
    { "app": "pipeline", "binding": 0, "documents": { "primary": 0 } }
  ]
}
```

The integer means only “these portable views belong to the same equivalence class.” It is not a runtime identity.

## 13.3 Export behavior

`ViewCollector` maps each effective runtime binding ID to the next dense integer. Multiple views in one group receive the same integer. The original binding string never appears in serialized JSON.

This has two advantages:

- private/runtime identifiers are not transported;
- two imported copies of one bundle do not accidentally link to each other.

## 13.4 Import behavior

Import first mints all view IDs. For each portable binding index:

- the first member’s freshly minted view ID becomes the group’s fresh binding identity;
- later members reuse that identity;
- the first member’s document-role map becomes the coherent group map.

The imported chart and pipeline retain distinct view IDs but share one fresh binding ID and one hydrated document selection.

## 13.5 Additive compatibility

The optional `binding` field was added without changing the current bundle version. Old bundles without it import each view independently. New readers accept both forms.

A future schema governance policy may choose to increment the version for every additive field. The present code treats this addition as backward-compatible within version 3.

## 13.6 Remote workbench protocol limitation

The protobuf `AppView` currently contains:

```proto
message AppView {
  string id = 1;
  string app_id = 2;
  map<string, string> documents = 3;
  optional string title = 4;
}
```

It has no `document_binding_id`. Consequently:

- local Redux state supports linkage;
- local persisted layout supports linkage;
- tile/workspace/stage portable bundles support linkage;
- remote workbench encode/decode does **not** preserve linkage yet.

The codec now contains an explicit note at the boundary. The correct follow-up is:

```proto
optional string document_binding_id = 5;
```

followed by regeneration of:

- Go protobuf code;
- TypeScript protocol code;
- any protocol fixtures;
- codec round-trip tests;
- server validation as applicable.

Manually changing only the TypeScript interface would be incorrect because the generated runtime descriptor controls protobuf JSON and binary behavior.

---

# 14. First-time experience

## 14.1 Install and run Storybook

From the enhanced project’s `pbui` directory:

```bash
corepack enable
pnpm install
pnpm --filter @hyperslop-systems/datalab-ui storybook
```

Open the Storybook URL printed by the command, then navigate to:

```text
Component Library
  → Organisms
    → Tile
      → Linked Document Selectors
```

The supplied execution environment did not contain `node_modules`, and network access was unavailable, so the dependency-backed Storybook build was not run here. The story and interaction test are present in source.

## 14.2 Exercise the link interaction

In the story:

1. Find the chart tile’s DocBar.
2. Press the `⛓` button labeled **link document selection to another tile**.
3. The accept banner prompts for another document-bound tile.
4. Click the **Pipeline view** title.
5. Both DocBars now show `⌁` unlink controls.
6. Change either document dropdown or create a new document with `＋`.
7. Observe that both chart and pipeline follow the same document selection.
8. Press `⌁` on one view.
9. Change a document selection again; the detached view now diverges.

The chart and pipeline remain separate logical views throughout.

## 14.3 Exercise prepared selectors

Navigate to the PBUI playground/story that maps fields to chart channels. Start a mapping operation. Only fields acceptable to the selected channel become sensitive.

The code now builds an accepted-name `Set` once at the beginning of the operation rather than scanning the schema for each field occurrence.

## 14.4 Run project validation after installing dependencies

Recommended commands:

```bash
pnpm typecheck
pnpm test
pnpm build

pnpm --filter @hyperslop-systems/workbench-protocol build
pnpm --filter @hyperslop-systems/datalab-ui typecheck
pnpm --filter @hyperslop-systems/datalab-ui test
pnpm --filter @hyperslop-systems/datalab-ui build-storybook
```

The repository README also documents the Go and protocol gates:

```bash
make ci-check
make protocol-check
```

---

# 15. Worked extension examples

## 15.1 Cross-allocation identity

```ts
interface Values {
  person: { id: string; name: string };
}

const registry = createPresentationRegistry<Values, {}, Verb>({
  person: {
    label: (person) => person.name,
    identityDomain: "person",
    identity: (person) => person.id,
  },
});

const a = {
  type: "person",
  value: { id: "p1", name: "Ada" },
} as const;

const b = {
  type: "person",
  value: { id: "p1", name: "Ada Lovelace" },
} as const;

registry.sameObject(a, b, {}); // true
```

## 15.2 Cross-type identity

```ts
interface Values {
  person: { id: string; name: string };
  employee: { id: string; name: string; department: string };
}

const registry = createPresentationRegistry(
  {
    person: {
      label: (value) => value.name,
      identityDomain: "entity",
      identity: (value) => value.id,
    },
    employee: {
      label: (value) => value.name,
      identityDomain: "entity",
      identity: (value) => value.id,
    },
  },
  {
    supertypes: {
      employee: ["person"],
    },
  },
);
```

Now the same employee may be recognized as one object under two presentation types, while subtype matching independently answers whether it satisfies a person input context.

## 15.3 Prepared permission selector

```ts
const result = await pbui.accept({
  prompt: "Choose an assignable user",
  selector: presentationSelectors.type("user", {
    cache: "identity",
    prepare: ({ environment }) => {
      const assignableIds = new Set(
        environment.members
          .filter((member) => member.canReceiveWork)
          .map((member) => member.userId),
      );

      return (user) => assignableIds.has(user.id);
    },
  }),
});
```

The arbitrary lambda remains expressive. The expensive permission projection happens once.

## 15.4 Selector based on another presented object

```ts
const sourceReference = currentSelection;

const result = await pbui.accept({
  prompt: "Choose a different entity",
  selector: {
    types: "entity",
    cache: "identity",
    prepare: ({ sameObject }) =>
      (candidate) => !sameObject(candidate, sourceReference),
  },
});
```

This avoids reimplementing identity comparison in the feature.

## 15.5 Shared action rule

```ts
const registry = createPresentationRegistry(descriptors, {
  supertypes: {
    employee: ["person"],
    person: ["entity"],
  },
  actionRules: [
    {
      id: "inspect-entity",
      selector: { types: "entity" },
      actions: (reference) => ({
        id: "inspect",
        label: "Inspect",
        verb: {
          kind: "inspect",
          type: reference.type,
          value: reference.value,
        },
      }),
    },
  ],
});
```

Any exact descriptor may override this by returning an action with ID `inspect`.

## 15.6 Costed conversions

```ts
const pbui = createPbui({
  registry,
  defaultEnvironment,
  conversions: [
    {
      id: "alias-to-person-remote",
      from: "alias",
      to: "person",
      cost: 10,
      convert: remoteProjection,
    },
    {
      id: "alias-to-handle",
      from: "alias",
      to: "handle",
      cost: 1,
      convert: aliasToHandle,
    },
    {
      id: "handle-to-person-local",
      from: "handle",
      to: "person",
      cost: 1,
      convert: handleToPerson,
    },
  ],
});
```

The local two-step interpretation wins with total cost `2`.

## 15.7 A second shared subject

To add shared time-range navigation without coupling document selection:

```ts
interface AppView {
  // existing fields
  documentBindingId?: string;
  timeRangeBindingId?: string;
  timeRange?: { start: number; end: number };
}
```

Then implement:

- `timeRangeBindingId(view)` fallback;
- `linkViewTimeRanges`;
- `unlinkViewTimeRange`;
- `setViewTimeRange` propagation;
- a portable equivalence index;
- a PBUI tile selector initiated from a range-link control.

Do not reuse `documentBindingId`; the user may want one relationship without the other.

---

# 16. Testing and validation

## 16.1 Generic registry tests

The implemented tests cover:

- semantic identity across separate allocations;
- shared identity domains across presentation types;
- transitive subtype matching;
- selector-driven shared actions;
- priority ordering;
- descriptor-local shadowing by action ID;
- rejection of cyclic type hierarchies.

## 16.2 Accept and conversion tests

The React tests cover:

- provider environment isolation;
- menu action performance;
- backward-compatible exact accept requests;
- selector preparation exactly once;
- identity-based memoization across semantic twins;
- clicked-occurrence commitment;
- lower-cost multi-edge conversion selection.

## 16.3 Product registry tests

Datalab tests cover:

- common actions on types without local descriptor actions;
- field semantic identity;
- datum identity with and without stable row keys;
- updated tile presentation values.

## 16.4 Layout reducer tests

Reducer tests cover:

- independent duplicate receives a different binding;
- chart and pipeline remain different views;
- linking merges groups;
- source document roles win at link time;
- later document selection propagates;
- unlinking detaches one view while preserving its current selection;
- later selection changes diverge.

## 16.5 Portable bundle tests

Portable tests cover:

- binding indices in exported views;
- two linked heterogeneous views export as `[0, 0]`;
- source runtime binding ID does not appear in JSON;
- import creates distinct view IDs;
- import rebuilds one fresh shared binding;
- shared documents hydrate once and remain shared by ID.

## 16.6 Validation performed in the supplied environment

The archive did not include installed JavaScript dependencies. Full package test/build commands could not run because Corepack attempted to fetch `pnpm@10.15.1` and the execution environment had no DNS/network access.

The following dependency-independent checks were performed:

- TypeScript syntax transpilation over all changed TS/TSX files: **0 syntax diagnostics**.
- Strict type check of generic identity/selector/registry/conversion modules with minimal React type stubs: **passed**.
- Runtime assertion suite for subtype, identity, action rules, prepared selectors, memoization, conversion cost, and cycle rejection: **passed**.
- Strict type check of the portable model and its pure dependencies: **passed**.
- Strict type check of the Datalab presentation registry against the real generic source modules: **passed**.
- Strict type check of the layout reducer with a minimal Redux Toolkit type stub: **passed**.
- Runtime reducer assertions for document binding link/propagate/unlink/duplicate behavior: **passed**.
- Strict type check of the bundle layer with minimal store stubs: **passed**.
- Runtime portable workspace export/import round trip for linked chart and pipeline: **passed**.

These targeted checks provide good evidence for the new pure logic. They do not replace the repository’s normal dependency-backed Vitest, Storybook, Vite, Biome, protobuf, and Go gates.

---

# 17. Accessibility, serialization, and security

## 17.1 Keyboard interaction

`Presentation` occurrences remain keyboard-focusable and use button semantics. Enter and Space commit an acceptable presentation, invoke activation, or open the object menu. Context Menu and Shift+F10 open the menu.

The link interaction therefore does not require a pointer: focus the chain button, start acceptance, focus the target tile title, and press Enter or Space.

## 17.2 Nested interactive elements

A presentation wrapper with `role="button"` should not contain native interactive descendants unless event and accessibility behavior are carefully designed. Tile titles are appropriate standalone targets. Broadly wrapping an entire complex tile would create nested-control problems.

A future occurrence protocol could allow non-button semantic regions and delegate activation to a contained control.

## 17.3 Visual sensitivity

PBUI marks acceptable presentations with `data-state="acceptable"`. Product CSS should ensure that highlighting is visible without relying only on color, remains legible under forced colors, and does not produce motion that violates user preferences.

## 17.4 Serializable verbs and state

Selectors, conversion functions, identity functions, and promise resolvers are runtime code. They do not belong in Redux or portable bundles.

The following remain data:

- application documents;
- layout views and placements;
- binding IDs or portable equivalence indices;
- presentation values placed in watch/trace/inspect state;
- performed verbs.

This boundary is essential for persistence and replay.

## 17.5 Avoid secrets in presentation values

A presentation value can flow into:

- menus;
- inspectors;
- watchlists;
- traces;
- local persistence;
- exported bundles, depending on product behavior.

The Datalab `TokenRef` intentionally excludes token secrets. Identity keys and descriptions must not reintroduce them. An identity function should generally return an opaque ID, not a credential or raw authorization header.

## 17.6 Predicate side effects

Selector predicates may run more often than expected under React rendering, development Strict Mode, or conversion exploration. They must be pure. Do not:

- dispatch actions;
- mutate the candidate;
- consume an iterator;
- log an audit event for every evaluation;
- perform network requests;
- depend on wall-clock time.

Perform effects only after `accept()` resolves.

---

# 18. Limitations and a practical roadmap

## 18.1 Parameterized presentation type specifiers

CLIM presentation types can carry parameters and options. PBUI currently uses string names only.

A future representation might be:

```ts
type PresentationTypeSpecifier<Values> =
  | PresentationType<Values>
  | {
      name: PresentationType<Values>;
      parameters?: readonly unknown[];
      options?: Readonly<Record<string, unknown>>;
    };
```

The hard part is not syntax. The system needs protocols for:

- validation;
- canonicalization;
- parameter-aware type membership;
- parameter-aware subtype checks;
- selector indexing;
- stable serialization and diagnostics.

## 18.2 Descriptor/presentation-method inheritance

The runtime type graph currently affects selectors and action rules. Labels, descriptions, tones, and identity are still resolved from the exact descriptor or fallback.

A fuller presentation-method system could inherit descriptor methods from supertypes. Multiple inheritance would require a deterministic linearization and clear method combination rules. CLOS-style before/after/around combination would be a substantial feature, not a small fallback lookup.

## 18.3 Nested input contexts

The provider permits one active accept operation. A second request resolves `null`. CLIM supports nested input contexts.

A future stack would need:

- clear ordering of inner and outer contexts;
- cancellation semantics;
- highlighting policy;
- promise ownership;
- routing of gestures to the innermost applicable context.

## 18.4 Gestures and translator menus

PBUI currently treats ordinary activation as acceptance and right-click as object menu. It does not model gesture-specific translators such as Shift+click, middle click, or keyboard chords.

A future translator definition could include:

```ts
interface Gesture {
  pointerButton?: number;
  shift?: boolean;
  control?: boolean;
  alt?: boolean;
  meta?: boolean;
  key?: string;
}
```

Conflicts would need priority and discoverable documentation.

## 18.5 Command arguments and partial commands

The current action system produces complete verbs. CLIM commands can have typed arguments acquired through input contexts, and partial commands can hold unsupplied markers.

A useful React command protocol might define:

```ts
interface CommandDefinition<Verb> {
  id: string;
  arguments: readonly CommandArgumentDefinition[];
  build(values: readonly unknown[]): Verb;
}
```

The command runner could sequentially establish selectors, show partial command state, and support abort/backtracking.

## 18.6 Textual acceptance and completion

PBUI accept currently selects mounted presentations. A fuller system could let a presentation type provide:

- parser;
- formatter;
- completion source;
- history key;
- validation diagnostics.

The same `accept()` operation could then be satisfied by typing or pointing.

## 18.7 Output history and virtualization

Unmounted React occurrences are not selectable. To approach CLIM output history, PBUI would need an occurrence registry or semantic output-record tree.

Questions include:

- Should off-screen virtualized rows remain eligible?
- How are stale objects invalidated?
- Does clicking a history item scroll/reveal the occurrence or return the object directly?
- How are nested occurrence regions represented?
- How is accessibility maintained for non-DOM history?

This should be designed with virtualization rather than bolted on afterward.

## 18.8 Incremental redisplay semantics

React handles current-tree reconciliation, but PBUI does not expose semantic unique IDs and cache values for output records. A future output-record layer could support:

- replayable semantic output;
- explicit stable occurrence IDs;
- selective invalidation by domain object identity;
- retained pointer documentation;
- semantic debugging tools.

Do not equate this directly with React keys.

## 18.9 Async selectors and conversions

Current predicates and conversions are synchronous. Async eligibility raises UI questions:

- provisional highlighting;
- cancellation;
- race conditions;
- per-object request fan-out;
- error display;
- caching and expiry.

A better design is often to prepare the needed permission/data index before beginning acceptance. If async support is added, it should be explicit rather than allowing predicates to return ambiguous promises.

## 18.10 Action-rule preparation

Action rules use the selector protocol, including `prepare`, but actions are resolved only when an object menu opens. This is not a presentation-render hot path. If future UI continuously displays action affordances for thousands of occurrences, introduce an environment-scoped prepared action resolver rather than relying on per-menu preparation.

## 18.11 Conversion source subtypes

As noted earlier, named conversion edges currently use exact source types. Add an explicit source-subtype policy after defining the runtime value-contract rule.

## 18.12 Remote protocol support

Add `document_binding_id = 5` to protobuf, regenerate all language bindings, and extend codec and server tests. Until then, remote workbench round trips intentionally lose document-link equivalence.

## 18.13 Normalize shared bindings if complexity grows

The current layout keeps a copy of the document-role map in every member view and updates members atomically. This fits Redux serialization and keeps migration small.

If bindings acquire substantial state or many views, normalize them:

```ts
interface LayoutState {
  views: Record<ViewId, AppView>;
  documentBindings: Record<BindingId, DocumentBindings>;
}
```

Views would then store only the binding ID. This guarantees one canonical map and makes large-group updates cheaper. Migration and deletion/garbage-collection rules would need care.

## 18.14 Developer instrumentation

A presentation-based UI benefits from inspection tooling. Useful additions include:

- a dev overlay showing type, identity domain/key, and occurrence details;
- an input-context panel explaining why a presentation matched or failed;
- conversion-path traces with total cost;
- action-rule provenance and shadowing;
- subtype graph visualization;
- predicate evaluation counters and cache-hit rates.

These tools would make the semantic layer as inspectable as React DevTools makes components.

---

# 19. File-by-file implementation map

## 19.1 Generic PBUI

### `src/presentation/types.ts`

Adds identity, selector, subtype, action-rule, and named-conversion protocols. Keeps legacy inline accept and conversion forms.

### `src/presentation/selectors.ts`

Adds selector normalization, preparation, typed selector factories, union composition, and accept-request helpers.

### `src/presentation/registry.ts`

Adds:

- runtime subtype graph;
- cycle rejection;
- subtype memoization;
- semantic identity;
- same-object comparison;
- selector-driven action rules;
- action priority and stable-ID shadowing.

### `src/presentation/conversions.ts`

Adds the bounded weighted conversion graph and operation-scoped acceptance memoization.

### `src/presentation/createPbui.tsx`

Prepares one matcher per accept operation, exposes identity helpers, carries environment through selectors/conversions, and supports configurable maximum conversion depth.

### `src/presentation/index.ts`

Exports the new public functions and types.

### `src/presentation/registry.test.ts`

Tests identity, subtyping, action rules, shadowing, and cycle detection.

### `src/presentation/createPbui.test.tsx`

Tests preparation lifecycle, semantic memoization, occurrence commitment, and costed conversion paths.

## 19.2 Datalab presentation layer

### `packages/datalab-ui/src/pbui/types.ts`

Adds `DatumRef.rowKey`, `TileRef.docBound`, and `TileRef.documentBindingId`.

### `packages/datalab-ui/src/pbui/registry.ts`

Defines the product identity vocabulary, typed selector factory, common Inspect/Watch rules, and stable local action IDs.

### `packages/datalab-ui/src/pbui/runtime.tsx`

Migrates category-to-field conversion to a named edge.

### `packages/datalab-ui/src/pbui/AcceptBanner.tsx`

Uses `acceptRequestTypes()` so it works with both accept request forms.

### `packages/datalab-ui/src/pbui/index.ts`

Exports product selector constructors and presentation type constants.

### `packages/datalab-ui/src/pbui/Pbui.stories.tsx`

Demonstrates prepared field selectors and supplies new tile reference fields.

## 19.3 Datalab applications

### `EncodingApp.tsx`

Replaces repeated field scans with a prepared accepted-name `Set`.

### `PipelineApp.tsx`

Uses prepared field sets for filter and grouping selection.

### `WatchlistApp.tsx`

Uses a typed union selector.

### `CompareApp.tsx`

Uses a typed chart selector and type-narrowed result.

## 19.4 Presentation producers

### `ChartPanel.tsx`

Adds the chart engine’s stable datum key to datum presentations.

### `TablePanel.tsx`

Adds row indices as available datum keys.

### `Tile.tsx`

Presents placement, logical view, document binding, and document-bound capability as separate facts.

## 19.5 Document linkage

### `store/layout.ts`

Adds binding identity, member lookup, propagation, group linking, unlinking, and independent-duplicate behavior.

### `components/molecules/DocBar/DocBar.tsx`

Adds chain and unlink controls and initiates the PBUI tile input context.

### `components/organisms/Tile/Tile.stories.tsx`

Adds the linked chart/pipeline first-time experience and interaction assertion.

## 19.6 Persistence and transport

### `store/persist.ts`

Accepts optional binding IDs for backward compatibility.

### `model/portable.ts`

Adds optional portable binding equivalence indices and validation.

### `store/bundles.ts`

Exports binding equivalence classes and rebuilds fresh shared bindings on import.

### `remote/codec.ts`

Documents the current protobuf limitation at encode/decode boundaries.

## 19.7 Product tests

### `test/descriptors.test.ts`

Tests common actions and semantic identity.

### `test/store.test.ts`

Tests link, propagation, unlink, and duplicate semantics.

### `test/portable.test.ts`

Tests portable equivalence classes and fresh-ID reconstruction.

---

# 20. Glossary

**Accept operation**

A temporary request for a presented object satisfying a selector.

**Action rule**

A selector-driven rule that contributes one or more actions to matching presentations.

**Application object**

A domain object the program models, independent of how it is displayed.

**Binding / subject identity**

An ID naming a state facet observed by one or more logical views, such as document-role selection.

**Command**

A structured representation of user intent. Datalab verbs play this role for currently implemented actions.

**Conversion**

A function that interprets one presentation reference as another type, potentially with a different value.

**Descriptor**

PBUI’s exact-type registry entry for label, description, tone, local actions, and identity.

**Identity domain**

A namespace for semantic identity keys.

**Input context**

The current semantic requirements for acceptable user input. PBUI represents it with a prepared selector and conversion matcher.

**Logical view**

One open application configuration, identified by `viewId`, independent of its placement rectangles.

**Occurrence**

One visible rendering of a presentation reference.

**Placement**

One leaf/rectangle in the workspace layout tree.

**Presentation**

The association of an application object, semantic presentation type, and visible occurrence.

**Presentation reference**

PBUI’s typed `{ type, value }` denotation carried by an occurrence.

**Presentation selector**

A reusable, preparable predicate protocol describing acceptable presentation types and refinements.

**Presentation type**

A runtime semantic UI category such as `field`, `datum`, or `tile`.

**Prepared predicate**

The candidate predicate returned once by a selector’s `prepare` function for one input context.

**Semantic identity**

The application-defined relation saying that references denote the same domain object.

**Subtype**

A runtime “is-a” relation between presentation types.

**Translator**

CLIM’s gesture-aware mapping from presented objects/types to another type or command. PBUI conversions implement only part of this concept.

---

# 21. References

The design uses CLIM as a conceptual and protocol reference, not as a claim of API compatibility.

1. Eugene C. Ciccarelli, *Presentation Based User Interfaces*, MIT Artificial Intelligence Laboratory, 1984. MIT DSpace: <https://dspace.mit.edu/entities/publication/9673058f-6662-43ea-b3de-c94e50f25769>
2. LispWorks, *CLIM 2.0 User Guide*, §6.1, “Conceptual Overview of CLIM Presentation Types”: <https://www.lispworks.com/documentation/lw81/clim/clim-ch6-1.htm>
3. LispWorks, *CLIM 2.0 User Guide*, §7.2, “CLIM Operators for Defining New Presentation Types”: <https://www.lispworks.com/documentation/lw81/clim/clim-ch7-2.htm>
4. LispWorks, *CLIM 2.0 User Guide*, §8.5–8.6, presentation translator examples and advanced translator matching: <https://www.lispworks.com/documentation/lw80/clim/clim-ch8-5.htm> and <https://www.lispworks.com/documentation/lw80/clim/clim-ch8-6.htm>
5. LispWorks, *CLIM 2.0 User Guide*, §11.1, “Introduction to CLIM Commands”: <https://www.lispworks.com/documentation/lw81/clim/clim-ch11-1.htm>
6. LispWorks, *CLIM 2.0 User Guide*, §11.9, “The CLIM Command Processor”: <https://www.lispworks.com/documentation/lw80/clim/clim-ch11-9.htm>
7. LispWorks, *CLIM 2.0 User Guide*, glossary entries for presentation, output history, input context, incremental redisplay, and unique ID: <https://www.lispworks.com/documentation/lw81/clim/clim-glossary.htm>
8. McCLIM project, *McCLIM User’s Manual*: <https://mcclim.common-lisp.dev/static/manual/mcclim.html>
9. Symbolics, *Common Lisp Interface Manager (CLIM), Release 2.0*: <https://bitsavers.trailing-edge.com/pdf/symbolics/software/genera_8/Common_Lisp_Interface_Manager__CLIM__Release_2.0.pdf>

---

## Closing perspective

The deepest lesson from CLIM is not that every React application needs a Lisp-style macro layer. It is that visible output can retain semantics, and that input can be requested in terms of those semantics rather than in terms of particular widgets.

The enhanced PBUI now has enough separation to make that lesson practical:

- references denote typed objects;
- descriptors define exact-type behavior and identity;
- selectors define input contexts;
- preparation makes arbitrary predicates efficient;
- subtype graphs express “is-a” relationships;
- conversion graphs express alternate interpretations;
- action rules contribute shared commands;
- occurrence commitment remains distinct from semantic caching;
- document bindings share one state subject without merging views or placements.

That architecture can grow toward richer presentation-based interaction while remaining recognizably React, TypeScript, and serializable application code.
