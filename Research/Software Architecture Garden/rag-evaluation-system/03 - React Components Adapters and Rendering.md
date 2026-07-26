---
title: rag-evaluation-system — React Components, Adapters, and Rendering
aliases:
  - Widget adapter architecture
tags:
  - architecture-garden
  - react
  - design-system
  - widget-ir
  - adapters
status: active
type: architecture-pattern-study
pattern_maturity: established
created: 2026-07-26
analyzed: 2026-07-26
repository: /home/manuel/code/wesen/go-go-golems/rag-evaluation-system
repository_commit: 7164b02ce8fedb21697e6d4079e785984007b0b7
analysis_commit: 42aef1f6aafa5a2029bcebef3d227ce92fd63787
source_ticket: RAG-WIDGET-SYSTEM-SIMPLIFICATION-2026-07-26
related_files:
  - packages/rag-evaluation-site/GUIDELINES.md
  - packages/rag-evaluation-site/src/widgets/ir/core.ts
  - packages/rag-evaluation-site/src/widgets/registry.ts
  - packages/rag-evaluation-site/src/widgets/defaultRegistry.ts
  - packages/rag-evaluation-site/src/widgets/WidgetRenderer.tsx
  - packages/rag-evaluation-site/src/components/molecules/DataTable/DataTable.tsx
  - packages/rag-evaluation-site/src/components/molecules/DataTable/DataTable.widget.tsx
---

# React Components, Adapters, and Rendering

The frontend separates visual components from the serialized Widget protocol through colocated adapters. A React component accepts idiomatic React props and callbacks. Its adapter accepts JSON-compatible Widget props, creates interaction context, binds ActionSpecs, and calls the component. The renderer knows how to traverse nodes and locate adapters, but it does not know every component's prop translation.

> [!summary]
> - Presentational components and transport components are related but not identical catalogs.
> - Colocated adapters isolate serialization and action binding from visual implementation.
> - The pattern remains valuable after removing unused registry generality and raw-only adapters.

## The component hierarchy

The package organizes reusable UI into five layers:

```text
foundation → atoms → layout → molecules → organisms
```

### Foundation

Foundation components define semantic text and display roles: `Text`, `Caption`, `CodeText`, `StatusText`, `Divider`, and accessibility helpers. They translate theme vocabulary into reusable APIs.

### Atoms

Atoms are small controls and markers such as buttons, text inputs, tags, badges, and icons. They should not own page layout.

### Layout

Layout components place regions: panels, stacks, inline groups, split panes, sidebars, grids, scrolling areas, and form rows. They avoid domain nouns.

### Molecules

Molecules implement reusable data and content behavior: DataTable, FieldRenderer, MarkdownArticle, pagination, context diagrams, activity feeds, and transcript cards.

### Organisms

Organisms compose lower layers into domain panels and shells. They can understand course, CMS, transcript, or scheduling data while remaining presentational.

This hierarchy is useful because it constrains dependency direction. A foundation primitive should not import a domain organism. A package organism should not import an application API service.

## The adapter seam

Consider a simplified table adapter:

```tsx
export const dataTableWidget = defineWidget<DataTableWidgetProps>({
  type: "DataTable",
  module: "widget.dsl",
  render(props, children, ctx) {
    return (
      <DataTable
        rows={props.rows}
        columns={props.columns}
        selectedKey={props.selectedKey}
        onRowSelect={props.onRowSelectAction
          ? (row, rowKey) => ctx.dispatchAction(
              props.onRowSelectAction,
              { row, rowKey, componentType: "DataTable" }
            )
          : undefined}
      />
    );
  }
});
```

The underlying `DataTable` does not know that actions arrived through JSON. It receives a normal callback. The adapter owns the protocol-specific translation.

This separation produces three kinds of reuse:

1. Direct React code can use `DataTable` without Widget IR.
2. A server-generated page can use the adapter through `WidgetRenderer`.
3. Storybook can test direct component states and separately test IR integration.

## Renderer mechanics

`WidgetRenderer.tsx` handles three node kinds:

```pseudo
render(node):
    if node.kind == "text":
        return node.text
    if node.kind == "element":
        return createElement(node.tag, node.attrs, render(node.children))
    if node.kind == "component":
        adapter = registry.get(node.type)
        if adapter is missing:
            return UnknownWidget(node.type)
        return adapter.render(node.props, render(node.children), context)
```

The renderer deliberately does not switch on 90 component names. Component-specific translation remains colocated. This keeps the traversal algorithm small and lets component owners review their transport behavior beside the component.

## Why colocation works

A component directory can contain:

```text
DataTable/
├── DataTable.tsx
├── DataTable.module.css
├── DataTable.stories.tsx
├── DataTable.widget.tsx
└── index.ts
```

A maintainer changing row selection can see visual behavior, styles, stories, and transport binding in one place. The multi-selection work demonstrated this advantage: the React component needed active-row and checked-row semantics, while the adapter needed to carry `selectedKeys`, action context, and bulk action definitions.

Colocation does not require a YAML manifest. Executable source is already colocated. A manifest that repeats type, props type, adapter path, export symbol, component name, actions, and documentation creates another synchronization obligation unless it generates those files.

## The two catalogs must be separated

The repository currently tends to treat every useful React component as a potential Widget component. That produces 90 adapters and a very large props union. The stronger architecture distinguishes:

```text
React component catalog
    all reusable visual building blocks

Widget protocol catalog
    components stable enough for remote serialized authoring
```

A transcript card may be useful inside a React organism but unnecessary as a public remote node. A calendar panel may be a Storybook composition without needing a permanent Widget transport contract. Conversely, DataTable is clearly a useful transport component because server-authored applications use its data, selection, actions, and keyboard behavior.

The decision test for a Widget adapter should be:

- Is the component API stable?
- Are its props meaningfully JSON-compatible?
- Is there a semantic reason for server-side authors to emit it?
- Can all interaction be represented through ActionSpecs and context?
- Is the adapter covered by behavior or integration tests?

If the answer is no, keep the component React-only.

## Type correlation

The current IR declares a `RagWidgetType` union and a separate `WidgetProps` union, but it does not correlate them. `ComponentNode.type` also permits any string, and base props permit arbitrary keys.

A closed contract map is more honest:

```ts
interface WidgetContractMap {
  Panel: PanelWidgetProps;
  DataTable: DataTableWidgetProps;
  FormDialog: FormDialogWidgetProps;
}

type ComponentNode = {
  [K in keyof WidgetContractMap]: {
    kind: "component";
    type: K;
    props: WidgetContractMap[K];
    children?: WidgetNode[];
  }
}[keyof WidgetContractMap];
```

This type does not validate untrusted JSON at runtime, but it prevents package authors from pairing known types with unrelated props. A boundary parser handles external data.

## Registry simplification

The current adapter interface repeats `module: "widget.dsl"` 90 times. The default registry builds six partial registries and merges them. Runtime lookup uses only the component type.

The simpler target is:

```ts
interface WidgetAdapter<K extends WidgetType> {
  type: K;
  render(
    props: WidgetContractMap[K],
    children: ReactNode[],
    context: RenderContext
  ): ReactNode;
}

const defaultWidgetRegistry = createWidgetRegistry([
  panelWidget,
  dataTableWidget,
  formDialogWidget,
]);
```

Remove fields and methods only after repository search confirms they have no consumer. The point is not to make the registry minimal at all costs. The point is to avoid extension infrastructure before an extension user exists.

## Host versus renderer

`WidgetRenderer` should remain small and reusable. `RagEvaluationSiteApp` owns page fetching, location state, shells, shortcuts, transport, refresh, and toasts. This is a sound package/application split:

```text
WidgetRenderer
    deterministic interpretation of a node tree

RagEvaluationSiteApp
    environment-specific page lifecycle and effects
```

The host currently includes legacy shell paths. Those paths should be removed after producers migrate, but the host itself is a useful product boundary.

## What goes wrong

### Every component becomes a protocol component

This expands remote compatibility obligations without increasing product capability. The project then maintains adapter props, registrations, manifests, and stories for components no server author uses.

### The adapter becomes the component

`FormDialog.widget.tsx` currently owns state, focus, subscriptions, form serialization, and rendering without a separate presentational component. This bypasses the documented React-first rule. The fix is to extract a real component/controller boundary and keep protocol translation in the adapter.

### Registry abstractions anticipate hypothetical plugins

Partial registries, merge functions, module metadata, and public entry enumeration add concepts. They should remain only if a named host composes registries independently.

### Raw component authoring bypasses the contract

An arbitrary component name defeats type correlation and semantic builder validation. It can fail only when the browser reports an unknown widget.

## When to use this pattern

Use a component/adapter boundary when:

- the same component has direct React and serialized uses;
- transport props differ from idiomatic React props;
- actions require runtime context binding;
- the renderer should remain independent of component details;
- components are reviewed and versioned as a library.

Do not create adapters for private child components, implementation fragments, or story-only compositions.

## Candidate ecosystem rules

- Reusable React components are not automatically remote protocol components.
- Keep transport translation colocated with the component it adapts.
- Keep application services out of presentational package components.
- Correlate protocol component names with their prop types.
- Introduce registry composition only for a named composition use case.
- Give stateful interactive organisms direct component tests, not only Widget stories.

## Related notes

- [[Research/Software Architecture Garden/rag-evaluation-system/01 - Project Architecture Overview]]
- [[Research/Software Architecture Garden/rag-evaluation-system/04 - Serializable Actions and Host Owned Effects]]
- [[Research/Software Architecture Garden/rag-evaluation-system/07 - Storybook Tests and Golden Contracts]]
