---
title: "PBUI Prototype Brief"
subtitle: "A visually adventurous React prototype on a solid semantic core"
author: "Shareable design and frontend guidelines"
date: "5 August 2026"
lang: en-US
papersize: letter
fontsize: 10pt
mainfont: "Lato"
sansfont: "Lato"
monofont: "DejaVu Sans Mono"
geometry:
  - margin=0.72in
colorlinks: true
linkcolor: blue
urlcolor: blue
toc: false
---

# 1. The assignment

Build a self-contained React prototype that is free to explore graphical and UX ideas, but has enough engine structure that we can extend it instead of throwing it away.

The prototype is **not** expected to predict the final product architecture. It **is** expected to preserve the basic meaning of objects, state changes, selections, and links while the visual design changes.

The north star is:

> **Visual freedom on top. Semantic discipline underneath.**

You may radically change layout, component anatomy, navigation, motion, density, menus, direct manipulation, and visual language. Do not make core product meaning depend on one component tree or one click handler.

![The core engine holds meaning; React is free to explore its presentation.](assets/semantic-spine.png){ width=88% }

# 2. What the prototype must demonstrate

Use a small workspace containing at least:

- one chart view;
- one pipeline view;
- two or more documents;
- a document selector in each view;
- the same document represented in more than one visual form;
- an interaction for choosing an already-visible object;
- an interaction for linking the chart and pipeline document selectors;
- an unlink operation;
- a development inspector or event log.

The finished demo must prove these behaviors:

1. The same document can appear in several places and still be recognized as the same object.
2. Starting "choose a document" highlights every matching visible occurrence.
3. Selection works by pointer and keyboard and can be cancelled.
4. A chart and pipeline can share only their selected document while retaining independent local settings.
5. Changing the document from either linked view updates both.
6. Unlinking keeps the current document in both views, after which they change independently.
7. Every lasting change is visible as a named command in the debug log.
8. The important states can be opened directly in Storybook or a fixture gallery.

# 3. The eight core rules

## Rule 1 - Every meaningful thing has a semantic subject

A card, chip, chart title, table row, tile, or search result may represent a domain object. Say which object it represents explicitly.

```ts
type SubjectRef =
  | { kind: "document"; id: DocumentId }
  | { kind: "field"; documentId: DocumentId; name: string }
  | { kind: "view"; id: ViewId }
  | { kind: "placement"; id: PlacementId }
  | { kind: "port"; id: PortId };
```

Use a small React adapter:

```tsx
<SemanticOccurrence subject={{ kind: "document", id: document.id }}>
  <DocumentCard document={document} />
</SemanticOccurrence>
```

The visual component stays ordinary and easy to story. The wrapper tells the engine what the rendered region means.

### Why

A workflow can then ask for "a document" and use any visible document representation. We do not need custom handlers in every chip, title, and card.

---

## Rule 2 - Object identity and screen occurrence are different

One object may appear many times.

![One subject can have several mounted occurrences.](assets/identity-occurrence.png){ width=80% }

Keep these IDs separate:

| ID | Meaning |
|---|---|
| `DocumentId` / `FieldId` | The real product object |
| `ViewId` | One logical chart, pipeline, table, or inspector |
| `PlacementId` | One place where a view is shown |
| `OccurrenceId` | One mounted semantic region |
| `PortId` | One named linkable aspect of a view |

Do not use array indexes, DOM IDs, or React keys as domain identity.

---

## Rule 3 - Put state in one of five buckets

![Every fact has a named state category and one authoritative owner.](assets/state-buckets.png){ width=98% }

1. **Domain state:** documents, fields, pipeline steps, source metadata.
2. **View state:** selected document, chart encoding, table columns.
3. **Layout state:** placements, tile sizes, split positions.
4. **Interaction state:** menu open, selecting, dragging, confirming, loading.
5. **Derived state:** labels, highlights, available actions, link membership.

Only the first four are normally stored. Derived state is calculated.

### One-owner test

Ask: "If this component unmounted, should the value disappear?"

- Yes: it may be local visual state.
- No: give it one owner in the engine or feature model.

Never keep two durable copies synchronized with `useEffect`.

---

## Rule 4 - Gestures produce commands, not hidden mutations

A click, keyboard activation, drag, or menu choice becomes a semantic command.

```ts
type Command =
  | { type: "SetViewDocument"; viewId: ViewId; documentId: DocumentId }
  | { type: "LinkPorts"; left: PortId; right: PortId; policy: "prefer-left" }
  | { type: "Unlink"; linkId: LinkId }
  | { type: "MovePlacement"; placementId: PlacementId; rect: Rect };
```

![The visual event is translated into intent before state changes.](assets/command-loop.png){ width=98% }

A pure transition validates the command and returns the next state:

```ts
transition(state, command) -> { state, effects } | { error }
```

Commands contain IDs and plain data. They do not contain DOM nodes, React events, promises, or callbacks.

### Why

Commands can be logged, replayed, tested, rejected, persisted, and eventually undone.

---

## Rule 5 - Selection is a reusable engine mode

Do not build a separate object picker into every feature. Start a selection request:

```ts
const result = await engine.select({
  subjectKind: "document",
  prompt: "Choose a document",
  scope: "mounted-occurrences",
});
```

While the request is active, matching occurrences receive a visual state such as `selectable` or `link-target`. Activating any one completes the request.

Selection must return one of:

```ts
{ status: "selected", subject, occurrenceId }
{ status: "cancelled" }
{ status: "invalidated", reason }
```

Recheck the match when the user commits, because state may have changed after highlighting.

---

## Rule 6 - Link named typed ports, not whole components

A chart and pipeline are separate logical views. They can share one named value without sharing everything.

```ts
chart.primaryDocument: Port<DocumentId>
pipeline.primaryDocument: Port<DocumentId>
```

![Link the document ports; keep the views independent.](assets/linking-ports.png){ width=96% }

Store explicit link edges:

```ts
type Link = {
  id: LinkId;
  left: PortId;
  right: PortId;
  policy: "require-equal" | "prefer-left" | "prefer-right";
};
```

Rules:

- only compatible port types can link;
- a document change updates the whole linked group atomically;
- reconciliation is explicit when current values differ;
- unlinking preserves the current value in each resulting view;
- duplicated placements are not the same thing as linked views.

The visual treatment of a link is open for design exploration.

---

## Rule 7 - Multi-step interactions have explicit states

Do not use several unrelated booleans for a workflow.

```ts
type LinkWorkflow =
  | { status: "idle" }
  | { status: "selectingTarget"; source: PortId }
  | { status: "confirming"; source: PortId; target: PortId }
  | { status: "committing" }
  | { status: "failed"; message: string };
```

![Design every meaningful workflow state, including cancel and failure.](assets/interaction-machine.png){ width=90% }

For each workflow, define:

- start;
- valid states;
- accepted events;
- cancel behavior;
- success result;
- failure and retry;
- focus return.

This state list is also the story list.

---

## Rule 8 - One behavior contract for pointer, keyboard, and accessibility

Pointer and keyboard events must translate into the same semantic intent.

```ts
activateOccurrence({ occurrenceId, gesture: "primary" })
```

Required:

- native controls where they fit;
- visible focus;
- keyboard route for every action;
- Escape cancels the active workflow and restores focus;
- state is never communicated by color alone;
- errors and non-obvious completion are announced;
- accessible names for icon-only controls;
- sensible tab order after moving or duplicating tiles.

ARIA is not a replacement for correct native semantics. Use the WAI-ARIA Authoring Practices patterns when building a custom widget.

# 4. Minimal code shape

```text
src/
  core/
    ids.ts
    state.ts
    commands.ts
    reducer.ts
    queries.ts
    occurrences.ts
    ports.ts
    links.ts
    workflow.ts
    store.ts
    debug.ts

  react/
    EngineProvider.tsx
    useEngineSelector.ts
    SemanticOccurrence.tsx
    DebugPanel.tsx

  features/
    chart/
    pipeline/
    linking/

  components/
    primitives/
    workspace/

  fixtures/
```

Rules for dependencies:

- `core` imports no React;
- visual components can render from props in isolation;
- feature containers read engine observations and dispatch commands;
- effects such as network, persistence, clipboard, and timers live in handlers at the edge;
- no component receives a mutable global state object.

# 5. Component handoff pattern

Build visual components from display-ready props:

```ts
interface DocumentSelectorViewProps {
  label: string;
  options: DocumentOption[];
  value: DocumentId | null;
  linkState: "unlinked" | "linked" | "source" | "target";
  status: "idle" | "loading" | "error";
  onChange(id: DocumentId): void;
  onStartLink(): void;
  onUnlink(): void;
}
```

The component should not reach directly into the store. A small feature container translates engine state into these props.

This keeps Storybook useful and lets the visual component be replaced later.

# 6. Required stories or fixture routes

## Semantic occurrence

- ordinary;
- selectable;
- focused;
- same subject in two appearances;
- rejected or disabled with reason;
- context action surface open.

## Document selector

- unlinked;
- linked;
- link source;
- valid link target;
- invalid target;
- loading;
- empty;
- stale;
- error.

## Workspace

- chart and pipeline independent;
- chart and pipeline linked;
- same view in two placements;
- narrow viewport;
- overflow;
- keyboard-only link workflow;
- target disappears during selection;
- command or persistence failure.

A state is worth a story when a reviewer can look at it and say, "that behavior or appearance is wrong."

# 7. Development inspector

Include a panel or route that shows:

- current state split into domain, view, layout, and interaction;
- current revision;
- mounted occurrence IDs and subjects;
- active selection request;
- matching and rejected occurrences;
- ports and link edges;
- derived linked groups;
- last 20 commands and whether they succeeded;
- pending fake effects.

This is a required design tool, not optional debugging polish.

# 8. What not to build

Do not spend prototype time on:

- a universal plugin system;
- a full rules engine;
- arbitrary presentation-type inheritance;
- a complex query language;
- collaboration or CRDTs;
- production authentication;
- a generic style-prop component framework;
- a complete undo system;
- global drag-and-drop infrastructure if one local workflow proves the concept.

Also avoid:

```text
array index as identity
one giant React context containing all changing state
shared state copied through effects
commands represented as callbacks
mouse-only interactions
several booleans for one workflow
components importing each other's stores
linking whole views when only one value should be shared
```

# 9. Acceptance checklist

## Core

- [ ] Core TypeScript imports no React.
- [ ] Stable subject, view, placement, occurrence, and port IDs exist.
- [ ] Durable state is divided into named buckets.
- [ ] Lasting changes use serializable commands.
- [ ] The transition is pure and tested.
- [ ] Derived values are calculated rather than synchronized manually.

## Presentations and selection

- [ ] The same document is shown in at least two visual forms.
- [ ] Both forms use the same semantic subject ID.
- [ ] A selection mode highlights all valid mounted occurrences.
- [ ] Pointer and keyboard can complete it.
- [ ] Escape cancels and restores focus.
- [ ] Selection is revalidated on commit.

## Linking

- [ ] Chart and pipeline expose compatible document ports.
- [ ] Linking shares only the document value.
- [ ] A named policy resolves different starting values.
- [ ] Changes propagate atomically.
- [ ] Unlinking preserves current values.
- [ ] Invalid port links are rejected by core logic.

## Design and accessibility

- [ ] Important states are directly openable as stories or fixtures.
- [ ] Focus is visible.
- [ ] Meaning is not carried by color alone.
- [ ] Icon controls have accessible names.
- [ ] Loading, empty, error, and stale states are designed.
- [ ] Narrow and overflow layouts are demonstrated.

## Inspectability

- [ ] Debug panel shows state, occurrences, selection, links, and commands.
- [ ] A recorded command sequence can reproduce durable state.
- [ ] A reviewer can tell whether a problem is visual, identity-related, state-related, or link-related.

# 10. Final note to the designer

This brief is not asking for conservative visuals. It is asking for clean semantic boundaries so the visuals can be more adventurous.

Feel free to challenge the tile model, menu model, density, navigation, and interaction language. Keep the following invariant:

```text
The engine knows what objects exist, who owns state,
which command changes it, what is being selected,
and which named ports are connected.

React decides how all of that is experienced.
```

# Sources and further reading

- LispWorks, *CLIM User Guide: Presentation Types and Presentation Translators*: <https://www.lispworks.com/documentation/lw44/CLIM/html/climguide-2.htm>
- Ben Shneiderman, "Direct Manipulation: A Step Beyond Programming Languages," 1983: <https://doi.org/10.1109/MC.1983.1654471>
- React, *Reacting to Input with State*, *Choosing the State Structure*, and *You Might Not Need an Effect*: <https://react.dev/learn/managing-state>
- Redux, *Style Guide*: <https://redux.js.org/style-guide/>
- David Harel, "Statecharts: A Visual Formalism for Complex Systems," 1987: <https://doi.org/10.1016/0167-6423(87)90035-9>
- W3C, *ARIA Authoring Practices Guide*: <https://www.w3.org/WAI/ARIA/apg/>
- W3C, *WCAG 2.2*: <https://www.w3.org/TR/WCAG22/>
- Storybook, *How to Write Stories*: <https://storybook.js.org/docs/writing-stories>
