---
title: "From Boilerplate to Recipes: Building Higher-Level Widgets on Top of Widget IR"
aliases:
  - Semantic Recipes
  - Recipe Pattern
  - Widget IR Recipes
tags:
  - article
  - widget-dsl
  - ui-dsl
  - goja
  - react
  - rag-evaluation
status: active
type: article
created: 2026-06-08
repo: /home/manuel/workspaces/2026-05-27/rag-evaluation-system/2026-05-27--rag-evaluation-system
---

# From Boilerplate to Recipes: Building Higher-Level Widgets on Top of Widget IR

This article explains the semantic recipe layer for the Widget DSL system. It shows how a small set of higher-level helpers reduce the amount of Widget IR an author must write by expanding common layout patterns into the same plain data that the WidgetRenderer already knows how to render.

The central pattern is simple: a recipe is a JavaScript function exposed through `require("widget.dsl")` that accepts user-provided data and returns a JSON-compatible Widget IR node. Recipes do not introduce new rendering behavior. They are macros that compose the existing component vocabulary into recognizable page sections. A recipe for a metrics dashboard, an action toolbar, and a master-detail table can each reduce dozens of lines of raw IR into a few lines of declarative data.

## The Problem with Raw Widget IR

The WidgetRenderer renders real React components. It receives Widget IR — a tree of `TextNode`, `ElementNode`, and `ComponentNode` objects — and maps each component node to the corresponding React component. This works correctly because React owns rendering, CSS Modules, event handling, table behavior, and accessibility.

However, composing raw Widget IR is verbose. A single dashboard section with four metric cards requires a `DashboardGrid` containing four `Panel` components, each containing a `StatusText` with a title and a numeric value. An action toolbar requires a `Panel` wrapping an `Inline` layout containing `Button` components and an optional `Caption`. A master-detail view requires a `DashboardGrid` with two `Panel` children: one containing a `DataTable`, the other containing row-specific metadata.

These compositions are not random. They appear repeatedly across different pages. Each time an author writes the same structure, they must choose the right grid recipe, the right density, the right action spec, and the right alignment. Small inconsistencies in props produce inconsistent visual output.

The recipe layer addresses this by providing named helpers that expand into known-good compositions.

## How Recipes Work

Recipes are implemented as functions in `pkg/widgetdsl/module.go`. Each recipe function receives a `goja.FunctionCall`, extracts the user-provided options as `map[string]any`, builds a Widget IR node tree as `map[string]any`, and returns the node wrapped in `r.vm.ToValue()`.

The recipes are installed into the `exports.recipes` object:

```go
recipes := r.vm.NewObject()
setExport(recipes, "metrics", r.metricsRecipe)
setExport(recipes, "actionToolbar", r.actionToolbarRecipe)
setExport(recipes, "masterDetailTable", r.masterDetailTableRecipe)
setExport(exports, "recipes", recipes)
```

This makes them available in JavaScript as `rag.recipes.metrics()`, `rag.recipes.actionToolbar()`, and `rag.recipes.masterDetailTable()`.

## Recipe 1: `metrics`

The `metrics` recipe produces a compact metrics dashboard. It accepts an array of items, each with a `label`, `value`, and optional `status`. It returns a `DashboardGrid` containing `Panel` components, each wrapping a `StatusText`.

The JavaScript call looks like this:

```js
rag.recipes.metrics({
  items: [
    { label: "Total queries", value: 12, status: "ready" },
    { label: "Succeeded", value: 8, status: "succeeded" },
    { label: "Running", value: 3, status: "running" },
    { label: "Failed", value: 1, status: "failed" }
  ]
})
```

The Go implementation iterates over the items, builds a `Panel` for each one with `density: "condensed"`, and nests a `StatusText` inside with the provided status and value. The `DashboardGrid` receives an auto-determined recipe based on item count:

```go
func metricsRecipeName(count int) string {
    if count <= 2 {
        return "two-up"
    }
    if count == 3 {
        return "three-up"
    }
    return "four-up"
}
```

The resulting Widget IR is a `ComponentNode` with `type: "DashboardGrid"` containing `children` — each a `ComponentNode` with `type: "Panel"`, `props` including `title` and `density`, and a `children` array containing a single `ComponentNode` with `type: "StatusText"`.

A single call to `rag.recipes.metrics()` replaces approximately four lines of raw IR per metric:

```js
// Raw IR equivalent of one metric:
rag.panel({ title: "Total queries", density: "condensed" },
  rag.statusText({ status: "ready", icon: true }, "12")
)

// Recipe call:
rag.recipes.metrics({ items: [
  { label: "Total queries", value: 12, status: "ready" }
]})
```

## Recipe 2: `actionToolbar`

The `actionToolbar` recipe produces a labeled panel containing a horizontal row of action buttons. It accepts a `title`, an optional `caption`, and an array of action definitions. Each action has a `label`, an optional `variant`, an optional `payload`, and an action specification that resolves to a server action.

The JavaScript call looks like this:

```js
rag.recipes.actionToolbar({
  title: "Queue controls",
  caption: "Actions mutate SQLite state and refresh the React app.",
  actions: [
    { label: "Add query", variant: "primary", action: "add-query", payload: { owner: "research" } },
    { label: "Retry failed", action: "bulk-retry-failed" },
    { label: "Reset demo", action: "reset-demo" }
  ]
})
```

The Go implementation iterates over the actions, builds a `Button` for each one with the specified variant and action spec, and nests them inside an `Inline` layout. If a `caption` is provided, it adds a `Caption` with tone `muted` to the inline layout. The entire content is wrapped in a `Panel` with the provided title.

The action resolution uses a normalization helper that accepts either a string action name with an optional payload, or a full action spec object:

```go
func normalizeActionSpec(action any, name any, payload any) (map[string]any, bool) {
    if spec, ok := action.(map[string]any); ok {
        if kind, _ := spec["kind"].(string); kind != "" {
            return spec, true
        }
    }
    if actionName, ok := action.(string); ok && strings.TrimSpace(actionName) != "" {
        out := map[string]any{"kind": "server", "name": actionName}
        if payload != nil {
            out["payload"] = payload
        }
        return out, true
    }
    return nil, false
}
```

This helper serves two purposes. It allows authors to write `{ label: "Add", action: "add-query" }` without thinking about the `kind` and `name` fields. It also allows authors to write `{ label: "Add", action: rag.action.server("add-query") }` when they need the explicit action spec form.

The resulting Widget IR is a `ComponentNode` with `type: "Panel"`, `props` including `title`, and a `children` array containing a single `ComponentNode` with `type: "Inline"`, `props` including `gap: "sm"` and `wrap: true`, and a `children` array containing `Button` components and an optional `Caption`.

A single call to `rag.recipes.actionToolbar()` replaces approximately six to eight lines of raw IR:

```js
// Raw IR equivalent:
rag.panel({ title: "Queue controls" },
  rag.inline({ gap: "sm", wrap: true },
    rag.button({ variant: "primary", action: { kind: "server", name: "add-query", payload: { owner: "research" } } }, "Add query"),
    rag.button({ action: { kind: "server", name: "bulk-retry-failed" } }, "Retry failed"),
    rag.button({ action: { kind: "server", name: "reset-demo" } }, "Reset demo"),
    rag.caption({ tone: "muted" }, "Actions mutate SQLite state...")
  )
)

// Recipe call:
rag.recipes.actionToolbar({
  title: "Queue controls",
  caption: "Actions mutate SQLite state and refresh the React app.",
  actions: [
    { label: "Add query", variant: "primary", action: "add-query", payload: { owner: "research" } },
    { label: "Retry failed", action: "bulk-retry-failed" },
    { label: "Reset demo", action: "reset-demo" }
  ]
})
```

## Recipe 3: `masterDetailTable`

The `masterDetailTable` recipe produces a two-up dashboard layout with a data table on the left and a detail panel on the right. It accepts rows, column definitions, a `selectedKey`, an optional `onRowSelect` action, and an optional `detail` callback or fallback node.

The JavaScript call looks like this:

```js
rag.recipes.masterDetailTable({
  title: "Query queue",
  rows: allRows(),
  columns: [
    { id: "name", header: "Query", cell: rag.cell.field("name") },
    { id: "status", header: "Status", cell: rag.cell.status("status", { icon: true }) }
  ],
  selectedKey: appState.selectedId,
  onRowSelect: "select-query",
  detail: row => rag.panel({ title: "Selected query" },
    rag.metadataGrid({ density: "compact", items: [
      { key: "Name", value: row.name },
      { key: "Status", value: rag.statusText({ status: row.status, icon: true }, row.status) }
    ]})
  )
})
```

The Go implementation builds a `DataTable` with the provided rows, columns, selected key, and on-row-select action. It wraps the table in a `Panel`. It then determines the detail node either from a Goja function callback or from a fallback Widget IR node.

The detail callback is the most complex part of this recipe. It receives a JavaScript function that the author passes as the `detail` option. The Go code checks whether this value is a Goja function using `goja.AssertFunction()`, and if so, invokes it with the selected row as an argument. The function returns a Widget IR node, which the Go code exports to JSON-compatible data before returning.

```go
func (r *runtime) detailNode(options map[string]any, row any) any {
    if detailFn, ok := goja.AssertFunction(r.vm.ToValue(options["detail"])); ok {
        value, err := detailFn(goja.Undefined(), r.vm.ToValue(row))
        if err != nil {
            panic(err)
        }
        if exported, ok := value.Export().(map[string]any); ok && isWidgetNodeExport(exported) {
            return exported
        }
    }
    if fallback, ok := options["detail"].(map[string]any); ok && isWidgetNodeExport(fallback) {
        return fallback
    }
    return map[string]any{
        "kind":     "component",
        "type":     "Panel",
        "props":    map[string]any{"title": stringFromMap(options, "detailTitle", "Details")},
        "children": []any{map[string]any{
            "kind":     "component",
            "type":     "Caption",
            "props":    map[string]any{"tone": "muted"},
            "children": []any{map[string]any{"kind": "text", "text": "Select a row to inspect it."}}
        }}
    }
}
```

The `masterDetailTable` recipe wraps the table panel and the detail node in a `DashboardGrid` with recipe `"two-up"`. If the detail callback produces no valid Widget IR node, the recipe falls back to a default panel with a muted caption.

A single call to `rag.recipes.masterDetailTable()` replaces approximately fifteen to twenty lines of raw IR that would otherwise consist of a `DashboardGrid` with `Panel`/`DataTable` and a detail `Panel`/`MetadataGrid` composition.

## The `page` Helper

The `page` helper provides a convenient way to create a complete page response with metadata. It accepts an options object with `id`, `title`, `schemaVersion`, optional `meta`, and either a `root` or `sections`. When `sections` is provided, `page` wraps them in a `Stack` with a configurable gap (defaulting to `"lg"`).

```js
rag.page({
  id: "actions",
  title: "Query Actions",
  schemaVersion: "0.1.0",
  meta: { shell: "app", maxWidth: "wide" },
  sections: [
    rag.recipes.metrics({ items: [...] }),
    rag.recipes.actionToolbar({ title: "Controls", actions: [...] }),
    rag.recipes.masterDetailTable({ title: "Query queue", rows, columns, selectedKey, onRowSelect, detail })
  ]
})
```

The `page` helper handles several responsibilities:

1. **Default values**: If `id` is not provided, it defaults to `"page"`. If `title` is not provided, it defaults to the `id`.
2. **Schema version**: Defaults to `"0.1.0"`.
3. **Metadata passthrough**: The `meta` object is passed through as-is. This is where page-level configuration like `shell`, `maxWidth`, and `navItems` lives.
4. **Section wrapping**: When `sections` is provided instead of `root`, the helper wraps all sections in a `Stack` with `gap: "lg"`. Each section must already be a valid Widget IR node.

The `page` helper is itself a recipe in the sense that it takes structured input and returns a complete Widget IR page. It sits at a higher level than `metrics`, `actionToolbar`, and `masterDetailTable` because it produces the page wrapper rather than a single component tree.

## Integration with the Showcase Script

The `examples/xgoja/widget-site/verbs/sites.js` showcase script demonstrates how recipes compose with raw IR to produce a complete action dashboard. The script builds three sections:

1. A title panel with row count and status.
2. A metrics dashboard showing query counts by status.
3. An action toolbar with queue controls.
4. A master-detail table with column definitions, row selection, and detail panel.
5. An audit trail panel showing recent action results.

```js
function widgetPage(id) {
  const rows = allRows()
  const selected = selectedRow()
  return rag.page({
    schemaVersion: "0.1.0",
    id,
    title: "xgoja widget actions demo",
    sections: [
      rag.panel({ title: "xgoja widget actions demo" },
        rag.statusText({ status: "succeeded", icon: true }, "Rows: " + rows.length),
        rag.caption({ tone: "muted" }, "This page is authored by a jsverb.")
      ),
      rag.recipes.metrics({ items: [
        { label: "Total queries", value: counts().total, status: "ready" },
        { label: "Succeeded", value: counts().succeeded, status: "succeeded" },
        { label: "Running", value: counts().running, status: "running" },
        { label: "Failed", value: counts().failed, status: "failed" }
      ]}),
      rag.recipes.actionToolbar({
        title: "Queue controls",
        caption: "Actions mutate in-memory SQLite state and ask the React app to refresh.",
        actions: [
          { label: "Add query", variant: "primary", action: "add-query", payload: { owner: "research" } },
          { label: "Retry failed", action: "bulk-retry-failed" },
          { label: "Reset demo", action: "reset-demo" }
        ]
      }),
      rag.recipes.masterDetailTable({
        title: "Query queue",
        rows,
        columns: queryColumns(),
        selectedKey: appState.selectedId,
        onRowSelect: "select-query",
        detail: () => selectedPanel(selected)
      }),
      rag.panel({ title: "Action audit trail", density: "condensed" },
        rag.stack({ gap: "xs" },
          appState.audit.slice(-6).reverse().map(entry => rag.caption({ tone: "muted" }, entry))
        )
      )
    ]
  })
}
```

This script uses `page` and `metrics` for the page wrapper and metrics section, `actionToolbar` for controls, `masterDetailTable` for the main data area, and raw `panel`/`stack`/`caption` for the audit trail. The recipes handle the complex compositions while the raw helpers handle the simple layouts.

## Implementation Details

The recipe functions operate within the same Goja runtime as the component helpers. They share the same `goja.Runtime` reference and use the same value conversion utilities. This means recipes can call into the same `anySlice()` normalization, `stringFromMap()` fallback logic, and `boolFromMap()` type coercion functions.

### Goja Function Invocation

The `detailNode` function in `masterDetailTable` demonstrates the only case where a recipe invokes a Goja function. The pattern is:

```go
if detailFn, ok := goja.AssertFunction(r.vm.ToValue(options["detail"])); ok {
    value, err := detailFn(goja.Undefined(), r.vm.ToValue(row))
    if err != nil {
        panic(err)
    }
    if exported, ok := value.Export().(map[string]any); ok && isWidgetNodeExport(exported) {
        return exported
    }
}
```

`goja.AssertFunction()` checks whether the value is callable. If it is, `detailFn()` invokes it with `goja.Undefined()` as `this` and the row converted to a Goja value as the argument. The return value is exported to `map[string]any`, checked to confirm it is a Widget IR node, and returned.

### Slice Normalization

The `anySlice()` function handles the conversion of Go-backed values to `[]any`. This matters because database query results arrive as typed Go slices (`[]map[string]any`), while JavaScript arrays arrive as `[]any`. The recipe functions need to handle both:

```go
func anySlice(value any) []any {
    if value == nil {
        return []any{}
    }
    if out, ok := value.([]any); ok {
        return out
    }
    rv := reflect.ValueOf(value)
    if rv.Kind() != reflect.Slice && rv.Kind() != reflect.Array {
        return []any{}
    }
    out := make([]any, 0, rv.Len())
    for i := 0; i < rv.Len(); i++ {
        out = append(out, rv.Index(i).Interface())
    }
    return out
}
```

This is not a recipe-specific problem. It is a general pattern for any Goja-to-Go boundary where JavaScript arrays and Go slices must both be accepted.

### Action Spec Normalization

The `normalizeActionSpec()` function handles two input forms:

1. A string action name with optional payload: `{ label: "Add", action: "add-query", payload: { owner: "research" } }`
2. A full action spec: `{ label: "Add", action: { kind: "server", name: "add-query", payload: { owner: "research" } } }`

```go
func normalizeActionSpec(action any, name any, payload any) (map[string]any, bool) {
    if spec, ok := action.(map[string]any); ok {
        if kind, _ := spec["kind"].(string); kind != "" {
            return spec, true
        }
    }
    if actionName, ok := action.(string); ok && strings.TrimSpace(actionName) != "" {
        out := map[string]any{"kind": "server", "name": actionName}
        if payload != nil {
            out["payload"] = payload
        }
        return out, true
    }
    return nil, false
}
```

This allows recipe authors to write concise action references without manually constructing the `{ kind: "server", name: "..." }` object. The function returns `(nil, false)` when the action cannot be resolved, and the calling code omits the `action` prop entirely.

## Validation

The recipes are validated through Go tests in `pkg/widgetdsl/module_test.go`. The test `TestSemanticRecipesAndActionsAreJSONSerializable` exercises the complete recipe chain:

```go
func TestSemanticRecipesAndActionsAreJSONSerializable(t *testing.T) {
    vm := goja.New()
    reg := require.NewRegistry()
    Register(reg)
    reg.Enable(vm)

    value, err := vm.RunString(`
        const rag = require("widget.dsl");
        const rows = [{ id: 1, name: "Alpha", status: "running" }];
        const page = rag.page({
            id: "actions",
            title: "Actions",
            meta: { shell: "app", maxWidth: "wide" },
            sections: [
                rag.recipes.metrics({ items: [
                    { label: "Total", value: rows.length, status: "ready" },
                    { label: "Running", value: 1, status: "running" }
                ]}),
                rag.recipes.actionToolbar({ title: "Controls", actions: [
                    { label: "Add", action: "add-query", variant: "primary", payload: { owner: "test" } },
                    { label: "Reset", action: rag.action.server("reset-demo") }
                ]}),
                rag.recipes.masterDetailTable({
                    title: "Rows",
                    rows,
                    columns: [{ id: "name", header: "Name", cell: rag.cell.field("name") }],
                    selectedKey: 1,
                    onRowSelect: "select-query",
                    detail: row => rag.panel({ title: "Selected" }, row.name)
                })
            ]
        });
        JSON.stringify(page);
    `)
    // ... assert JSON round-trip and structure
}
```

The test verifies two things:

1. **JSON round-trip**: The output can be serialized to JSON and parsed back without error. This confirms that all recipe output is JSON-compatible and contains no non-serializable values.
2. **Structure**: The parsed result contains the expected metadata fields (`id`, `title`, `meta`), the root is a `Stack` wrapping three sections, and the second section is a `Panel` (the action toolbar).

## Design Principles

The recipe layer follows several design principles that keep it simple and composable.

### Recipes Are Pure Expansions

A recipe takes data and returns Widget IR. It does not render, does not modify state, does not call APIs, and does not perform side effects. The recipe for `metrics` does not query a database. It does not know about the current user or the page id. It only knows about the items array it receives and expands it into a `DashboardGrid` with `Panel`/`StatusText` composition.

This purity means recipes can be tested in isolation with synthetic data and still produce valid, renderable output.

### Recipes Use the Existing Component Vocabulary

Recipes compose existing components (`Panel`, `DashboardGrid`, `Inline`, `Button`, `Caption`, `StatusText`, `DataTable`, `MetadataGrid`) rather than introducing new ones. They do not require changes to the WidgetRenderer, the component library, or the CSS Modules. They only use what already exists.

This is important because adding a new component would require changes to the WidgetRenderer switch statement, the TypeScript IR types, and the npm package surface. A recipe only requires changes to `pkg/widgetdsl/module.go`.

### Recipes Are Optional

A script can mix raw IR and recipes in any combination. The showcase script uses `page`, `metrics`, `actionToolbar`, and `masterDetailTable` for the complex layouts, but uses raw `panel`, `stack`, and `caption` for the title panel and audit trail. The `rag.page()` helper itself is a recipe-level function that sits above the widget recipes.

Authors are free to write raw IR for simple layouts and use recipes only where they save significant typing or improve consistency.

### Recipes Are Extensible

Adding a new recipe follows the same pattern as adding a component helper: write a Go function that accepts `goja.FunctionCall`, extracts options as `map[string]any`, builds a Widget IR node as `map[string]any`, and returns it via `r.vm.ToValue()`. Install it in the `recipes` object during `install()`.

No other files need to change. The WidgetRenderer already renders any component type it recognizes, and the recipe only uses components that are already in the renderer's switch statement.

## Common Patterns for Future Recipes

Several patterns are ready to be extracted into new recipes:

1. **Form sections**: A `FormRow` for a label/control pair, or a `FormRow` list for multi-field forms. The showcase script could benefit from a recipe that takes field definitions and produces a `Stack` of `FormRow` components.

2. **Tab lists with detail content**: A `TabList` containing tab items and a detail panel that updates based on the active tab. This would combine `TabList` with `Inline` or `Stack` layout.

3. **Search workbench**: The original RAG frontend had a search workbench with a query input, strategy buttons (bm25/hybrid/vector), and a results table. This could become a single recipe that accepts a query string, a list of strategy options, and result rows.

4. **Status indicator badges**: A small recipe that produces a compact inline badge showing status, icon, and value. This is a subset of the `metrics` recipe but without the `DashboardGrid` wrapper.

5. **Navigation bar**: A recipe that produces a top-level `AppNav` or `TabList` based on page metadata (`navItems`, `activeNavItemId`). This would complement the `page` helper's `meta.navItems` field.

## Testing and Validation

Recipes should be validated through three complementary approaches:

1. **Unit tests**: Test each recipe function with synthetic data and verify JSON round-trip and structural correctness. The `TestSemanticRecipesAndActionsAreJSONSerializable` test demonstrates this pattern.

2. **Generated binary smoke**: Run the xgoja widget-site example and verify that recipe-based pages render correctly with `make smoke` or `devctl smoke`. This validates the full integration from recipe expansion through HTTP response through React rendering.

3. **Browser action smoke**: Use Playwright to verify that recipe-based pages respond to user interaction. Clicking buttons, selecting rows, and verifying refresh behavior proves that recipe-generated action specs work end-to-end.

## Related Files

- `pkg/widgetdsl/module.go` — Recipe implementations: `metricsRecipe`, `actionToolbarRecipe`, `masterDetailTableRecipe`, `detailNode`, `page`
- `pkg/widgetdsl/module_test.go` — Tests for recipe JSON serialization and structure
- `pkg/widgetdsl/registrar.go` — RuntimeModuleSpec registration for the widget.dsl module
- `examples/xgoja/widget-site/verbs/sites.js` — Showcase script using recipes with raw IR
- `pkg/xgoja/providers/widgetsite/doc/01-widget-dsl-getting-started.md` — Provider-bundled getting started docs
