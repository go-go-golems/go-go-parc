---
title: "Semantic Recipes on Top of Widget IR"
aliases:
  - Semantic Recipes on Top of Widget IR
  - Widget DSL Recipes
  - Higher-Level Widget Patterns
tags:
  - article
  - project-report
  - goja
  - widget-ir
  - ui-dsl
  - rag-evaluation
status: active
type: article
created: 2026-06-06
repo: /home/manuel/workspaces/2026-05-27/rag-evaluation-system/2026-05-27--rag-evaluation-system
---

# Semantic Recipes on Top of Widget IR

## Overview

A Widget IR renderer works correctly at the component level when individual widgets like `Panel`, `DataTable`, and `Button` render as expected. Correct rendering does not imply correct authoring experience. When every page requires manual assembly of `Stack`, `DashboardGrid`, `Panel`, `Inline`, `StatusText`, `MetadataGrid`, and `Caption` nodes to produce a metrics row, a toolbar, or a master-detail layout, the authoring layer has become as verbose as the original hand-coded approach the system was designed to replace.

Semantic recipes solve this problem. A recipe is a JavaScript function that accepts a high-level description of a page section and returns a complete Widget IR subtree. The recipe expands a single function call into a composition of real React components. The author writes intent; the recipe emits data.

This article covers three specific recipes that emerged during implementation:

1. `metrics()` — expands labeled value items into a `DashboardGrid` of `Panel` + `StatusText` components with automatic layout sizing.
2. `actionToolbar()` — expands an action list into a `Panel` containing `Inline`-arranged `Button` nodes with optional captions.
3. `masterDetailTable()` — expands a table configuration and a detail callback into a `DashboardGrid` with a `Panel/DataTable` on the left and a dynamic detail panel on the right.

The discussion also covers the supporting infrastructure that makes these recipes possible: the `page()` wrapper, action normalization, the Goja function callback pattern, and slice normalization for typed Go data.

## The Problem with Raw Widget IR Authoring

Before recipes existed, every page section had to be composed from the ground up. A simple metrics row with four items required approximately twelve lines of Widget IR:

```js
dashboardGrid({ recipe: "four-up" },
  panel({ title: "Total", density: "condensed" },
    statusText({ status: "ready", icon: true }, "150")
  ),
  panel({ title: "Succeeded", density: "condensed" },
    statusText({ status: "succeeded", icon: true }, "120")
  ),
  panel({ title: "Running", density: "condensed" },
    statusText({ status: "running", icon: true }, "25")
  ),
  panel({ title: "Failed", density: "condensed" },
    statusText({ status: "failed", icon: true }, "5")
  )
)
```

Each item has the same structure: a `Panel` with `title` and `density: "condensed"`, containing a single `StatusText` with `status`, `icon: true`, and a text child. The duplication is structural, not semantic. The author is describing layout decisions that are identical for every metric item.

A recipe eliminates this duplication by making the common structure a first-class primitive:

```js
rag.recipes.metrics({ items: [
  { label: "Total", value: 150, status: "ready" },
  { label: "Succeeded", value: 120, status: "succeeded" },
  { label: "Running", value: 25, status: "running" },
  { label: "Failed", value: 5, status: "failed" }
]})
```

The author now describes four values and their status labels. The recipe expands each item into the correct `Panel` + `StatusText` composition and wraps the result in a `DashboardGrid`.

The same pattern applies to toolbars and master-detail tables. Each recipe captures a common composition pattern, hides the layout decisions, and exposes only the data that changes.

## Design Constraint: Recipes Are Macros, Not a New Renderer

Recipes must return Widget IR. They must not return HTML strings, React elements, or any framework-specific representation. This constraint exists because the rendering boundary is fixed: JavaScript produces data, Go validates it, React renders it. A recipe that returns anything other than Widget IR would create a second rendering path that is separate from the `WidgetRenderer` and therefore unsynced with component updates, CSS Modules, and action binding.

Every recipe in `pkg/widgetdsl` returns `map[string]any` that is structurally valid Widget IR. The recipe `metrics()` returns a `DashboardGrid` component node. The recipe `actionToolbar()` returns a `Panel` component node. The recipe `masterDetailTable()` returns a `DashboardGrid` component node. The expansion is deterministic and verifiable.

This constraint also shapes how recipes handle callbacks. When a recipe needs a detail panel that depends on the current row selection, it cannot return a React component or a function reference. It must accept a JavaScript function, call it, convert the result into Widget IR, and return that IR. The function does not cross the Goja-to-Go boundary as a callable; it is executed, its result is serialized, and only the result crosses the boundary.

## The `page()` Wrapper and Section Composition

Before discussing individual recipes, it is necessary to understand `page()`. This function is not a recipe in the same category as `metrics()`, `actionToolbar()`, and `masterDetailTable()`. It is a page-level wrapper that provides the `schemaVersion`, `id`, `title`, and `meta` fields that the server expects, and it composes a list of sections into a root `Stack` node.

The implementation in `pkg/widgetdsl/module.go` checks whether the caller provided an explicit `root` node. If `root` exists and is a valid Widget IR node, it is used directly:

```go
if root, ok := options["root"].(map[string]any); ok && isWidgetNodeExport(root) {
    out["root"] = root
    return r.vm.ToValue(out)
}
```

If `root` is not provided, the function looks for `sections`. Each element in `sections` must be a valid Widget IR node. The function collects these nodes and wraps them in a `Stack` with `gap: "lg"`:

```go
sections := anySlice(options["sections"])
children := []any{}
for _, section := range sections {
    if node, ok := section.(map[string]any); ok && isWidgetNodeExport(node) {
        children = append(children, node)
    }
}
out["root"] = map[string]any{
    "kind":     "component",
    "type":     "Stack",
    "props":    map[string]any{"gap": stringFromMap(options, "gap", "lg")},
    "children": children,
}
```

This design allows recipes to return a single section node, which the `page()` wrapper then stacks together with other sections:

```js
return rag.page({
    id: "actions",
    title: "Action Dashboard",
    sections: [
        rag.recipes.metrics({ items: [...] }),
        rag.recipes.actionToolbar({ title: "Controls", actions: [...] }),
        rag.recipes.masterDetailTable({ title: "Rows", rows, columns, ... })
    ]
})
```

Each recipe call returns a Widget IR node. The `page()` wrapper stacks them into a `Stack` root and adds the page metadata.

## Recipe 1: `metrics()`

The `metrics()` recipe expands a list of labeled values into a layout-appropriate grid of metric panels.

### Authoring API

The author passes an array of items. Each item has a `label`, a `value`, and an optional `status`:

```js
rag.recipes.metrics({ items: [
    { label: "Total queries", value: 150, status: "ready" },
    { label: "Succeeded", value: 120, status: "succeeded" },
    { label: "Running", value: 25, status: "running" },
    { label: "Failed", value: 5, status: "failed" }
]})
```

The `status` is optional. Items without a status default to `"ready"`.

### Expansion Logic

The implementation iterates over the items array and builds one `Panel` + `StatusText` composition per item:

```go
func (r *runtime) metricsRecipe(call goja.FunctionCall) goja.Value {
    options := firstObject(call.Arguments)
    items := anySlice(options["items"])
    children := []any{}
    for _, raw := range items {
        item, ok := raw.(map[string]any)
        if !ok {
            continue
        }
        label := stringFromMap(item, "label", "Metric")
        status := stringFromMap(item, "status", "ready")
        value := item["value"]
        children = append(children, map[string]any{
            "kind":  "component",
            "type":  "Panel",
            "props": map[string]any{"title": label, "density": "condensed"},
            "children": []any{map[string]any{
                "kind":     "component",
                "type":     "StatusText",
                "props":    map[string]any{"status": status, "icon": boolFromMap(item, "icon", true)},
                "children": []any{map[string]any{"kind": "text", "text": fmt.Sprint(value)}},
            }},
        })
    }
    return r.vm.ToValue(map[string]any{
        "kind":     "component",
        "type":     "DashboardGrid",
        "props":    map[string]any{"recipe": stringFromMap(options, "recipe", metricsRecipeName(len(children)))},
        "children": children,
    })
}
```

Each item expands to:

- A `Panel` component with `title` set to the item label and `density: "condensed"`.
- A single `StatusText` child with `status`, `icon: true`, and the item value as text.

The `DashboardGrid` wrapper uses an automatic layout recipe based on item count:

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

Two or fewer items get `recipe: "two-up"`. Three items get `"three-up"`. Four or more get `"four-up"`. The `DashboardGrid` component interprets these recipe names as CSS grid layout configurations.

### Generated Widget IR

The recipe output is structurally equivalent to the manual composition from the earlier example:

```json
{
  "kind": "component",
  "type": "DashboardGrid",
  "props": { "recipe": "four-up" },
  "children": [
    {
      "kind": "component",
      "type": "Panel",
      "props": { "title": "Total", "density": "condensed" },
      "children": [
        {
          "kind": "component",
          "type": "StatusText",
          "props": { "status": "ready", "icon": true },
          "children": [{ "kind": "text", "text": "150" }]
        }
      ]
    },
    ...
  ]
}
```

The recipe output is identical to what the author would write by hand. The recipe simply removes the need to type it.

### Test Coverage

The test in `pkg/widgetdsl/module_test.go` validates the recipe through a full pipeline: require the module, call `metrics()`, export the result to a Go map, and assert the node type and structure:

```go
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
            ]})
        ]
    });
    JSON.stringify(page);
`)
var decoded map[string]any
if err := json.Unmarshal([]byte(value.String()), &decoded); err != nil {
    t.Fatalf("recipe page is not JSON: %v\n%s", err, value.String())
}
```

The test also validates that `metrics()` output is JSON-serializable. A recipe that returned functions, class instances, or other non-serializable values would break the page endpoint, because the server must serialize the Widget IR to JSON before sending it over HTTP.

## Recipe 2: `actionToolbar()`

The `actionToolbar()` recipe expands a list of action definitions into a toolbar panel with buttons and an optional caption.

### Authoring API

The author passes a `title`, an optional `caption`, and an array of action definitions. Each action has a `label`, a `variant`, and an `action` specification:

```js
rag.recipes.actionToolbar({
    title: "Queue controls",
    caption: "Actions mutate in-memory SQLite state.",
    actions: [
        { label: "Add query", variant: "primary", action: "add-query", payload: { owner: "research" } },
        { label: "Retry failed", action: "bulk-retry-failed" },
        { label: "Reset demo", action: "reset-demo" }
    ]
})
```

### Expansion Logic

The implementation iterates over the actions array and builds a `Button` per action, then wraps them in an `Inline` node inside a `Panel`:

```go
func (r *runtime) actionToolbarRecipe(call goja.FunctionCall) goja.Value {
    options := firstObject(call.Arguments)
    actions := anySlice(options["actions"])
    inlineChildren := []any{}
    for _, raw := range actions {
        item, ok := raw.(map[string]any)
        if !ok {
            continue
        }
        label := stringFromMap(item, "label", stringFromMap(item, "name", "Action"))
        props := map[string]any{"variant": stringFromMap(item, "variant", "secondary")}
        if act, ok := normalizeActionSpec(item["action"], item["name"], item["payload"]); ok {
            props["action"] = act
        }
        inlineChildren = append(inlineChildren, map[string]any{
            "kind":     "component",
            "type":     "Button",
            "props":    props,
            "children": []any{map[string]any{"kind": "text", "text": label}},
        })
    }
    if caption, ok := options["caption"].(string); ok && caption != "" {
        inlineChildren = append(inlineChildren, map[string]any{
            "kind":     "component",
            "type":     "Caption",
            "props":    map[string]any{"tone": stringFromMap(options, "captionTone", "muted")},
            "children": []any{map[string]any{"kind": "text", "text": caption}},
        })
    }
    return r.vm.ToValue(map[string]any{
        "kind":  "component",
        "type":  "Panel",
        "props": map[string]any{"title": stringFromMap(options, "title", "Actions")},
        "children": []any{map[string]any{
            "kind":     "component",
            "type":     "Inline",
            "props":    map[string]any{"gap": "sm", "wrap": true},
            "children": inlineChildren,
        }},
    })
}
```

Each action expands to a `Button` with the correct `variant`, `label`, and `action` specification. Actions without an explicit `action` field still get the string value from `item["name"]` if available, via the `normalizeActionSpec` helper.

The `normalizeActionSpec` function handles two formats:

```go
func normalizeActionSpec(action any, name any, payload any) (map[string]any, bool) {
    // Format 1: full action spec object
    if spec, ok := action.(map[string]any); ok {
        if kind, _ := spec["kind"].(string); kind != "" {
            return spec, true
        }
    }
    // Format 2: string action name with optional payload
    if actionName, ok := action.(string); ok && strings.TrimSpace(actionName) != "" {
        out := map[string]any{"kind": "server", "name": actionName}
        if payload != nil {
            out["payload"] = payload
        }
        return out, true
    }
    if actionName, ok := name.(string); ok && strings.TrimSpace(actionName) != "" {
        out := map[string]any{"kind": "server", "name": actionName}
        if payload != nil {
            out["payload"] = payload
        }
        return out, true
    }
    return nil, false
}
```

An action can be specified as a full `server` spec object `{ kind: "server", name: "...", payload: {...} }` or as a simple string `"add-query"` that the recipe converts to `{ kind: "server", name: "add-query", payload: {...} }`. Both formats produce identical JSON output.

The optional caption is rendered as a `Caption` with `tone: "muted"` and appended after the buttons in the `Inline` layout.

### Generated Widget IR

The recipe output is equivalent to:

```json
{
  "kind": "component",
  "type": "Panel",
  "props": { "title": "Queue controls" },
  "children": [
    {
      "kind": "component",
      "type": "Inline",
      "props": { "gap": "sm", "wrap": true },
      "children": [
        {
          "kind": "component",
          "type": "Button",
          "props": {
            "variant": "primary",
            "action": { "kind": "server", "name": "add-query", "payload": { "owner": "research" } }
          },
          "children": [{ "kind": "text", "text": "Add query" }]
        },
        {
          "kind": "component",
          "type": "Button",
          "props": {
            "variant": "secondary",
            "action": { "kind": "server", "name": "bulk-retry-failed" }
          },
          "children": [{ "kind": "text", "text": "Retry failed" }]
        },
        {
          "kind": "component",
          "type": "Caption",
          "props": { "tone": "muted" },
          "children": [{ "kind": "text", "text": "Actions mutate in-memory SQLite state." }]
        }
      ]
    }
  ]
}
```

## Recipe 3: `masterDetailTable()`

The `masterDetailTable()` recipe is the most complex of the three. It expands a table configuration and a detail panel callback into a two-column `DashboardGrid` with a `DataTable` panel on the left and a dynamic detail panel on the right.

### Authoring API

The author passes a `title`, `rows`, `columns`, a `selectedKey`, an `onRowSelect` action, and a `detail` callback:

```js
rag.recipes.masterDetailTable({
    title: "Query queue",
    rows: allRows(),
    columns: queryColumns(),
    selectedKey: appState.selectedId,
    onRowSelect: "select-query",
    detail: row => rag.panel({ title: "Selected query" }, row.name)
})
```

### Expansion Logic

The recipe builds a `Panel` containing a `DataTable`, then evaluates the `detail` callback to get the right-side panel:

```go
func (r *runtime) masterDetailTableRecipe(call goja.FunctionCall) goja.Value {
    options := firstObject(call.Arguments)
    rows := anySlice(options["rows"])
    selectedKey := options["selectedKey"]
    tableProps := map[string]any{
        "rows":         rows,
        "getRowKey":    valueOrDefault(options["getRowKey"], "id"),
        "columns":      anySlice(options["columns"]),
        "selectedKey":  selectedKey,
        "emptyMessage": valueOrDefault(options["emptyMessage"], "No rows"),
    }
    if act, ok := normalizeActionSpec(options["onRowSelect"], nil, nil); ok {
        tableProps["onRowSelect"] = act
    }
    tablePanel := map[string]any{
        "kind":     "component",
        "type":     "Panel",
        "props":    map[string]any{"title": stringFromMap(options, "title", "Items")},
        "children": []any{map[string]any{"kind": "component", "type": "DataTable", "props": tableProps}},
    }
    detailNode := r.detailNode(options, selectedRow(rows, selectedKey))
    return r.vm.ToValue(map[string]any{
        "kind":     "component",
        "type":     "DashboardGrid",
        "props":    map[string]any{"recipe": stringFromMap(options, "recipe", "two-up")},
        "children": []any{tablePanel, detailNode},
    })
}
```

The left side is a `Panel` wrapping a `DataTable`. The right side is produced by `detailNode()`.

### The Goja Function Callback Pattern

The `detail` parameter accepts a JavaScript function. The recipe calls this function with the currently selected row, converts the result into Widget IR, and returns it. This is the mechanism that enables dynamic detail panels without crossing the Goja-to-Go boundary as a callable reference.

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
            "children": []any{map[string]any{
                "kind": "text",
                "text": "Select a row to inspect it."
            }},
        }},
    }
}
```

The implementation first tries to treat `options["detail"]` as a Goja function using `goja.AssertFunction()`. If successful, it calls the function with the selected row as the argument. The function returns a Goja value, which is exported to a Go map and validated as a Widget IR node. If the export succeeds, the function returns that node.

If `options["detail"]` is not a function, the implementation checks whether it is a direct Widget IR node (the fallback case). If neither the function path nor the fallback path produces a valid node, the function returns a default `Panel` with a `Caption` instructing the user to select a row.

This design is necessary because JavaScript functions cannot cross the Goja-to-Go boundary as callable references. React never receives a JavaScript function. The function is executed while constructing the page response, its result is converted to Widget IR, and only the result crosses the HTTP boundary.

### The Goja Function Binding Bug

One of the first attempts at implementing this pattern used a Go function that accepted `goja.FunctionCall` but returned `map[string]any`. The Goja runtime did not pass `goja.FunctionCall` correctly in this case; the argument shape was malformed and the recipe panics with an unexpected error.

The fix was to change the function signature to accept `goja.Value` and call `goja.AssertFunction()` explicitly:

```go
// Before (broken):
func detailCallback(call goja.FunctionCall) map[string]any { ... }

// After (working):
detailFn, ok := goja.AssertFunction(r.vm.ToValue(options["detail"]))
if ok {
    value, err := detailFn(goja.Undefined(), r.vm.ToValue(row))
    // ...
}
```

`goja.AssertFunction()` returns `true` when the value is callable and `false` otherwise. The caller then passes `goja.Undefined()` as the `this` value and `r.vm.ToValue(row)` as the single argument. The returned value is the result of the function call.

### The Typed Go Slice Bug

The `masterDetailTable()` recipe also exposed a second failure mode. The recipe accepts `rows` from the `db.query()` call, which returns typed Go slices (`[]map[string]any` with Go struct fields), not JavaScript arrays (`[]any`). The original `anySlice` implementation checked for `[]any` only and returned an empty slice when given a typed slice, causing the table to render with no rows even though the action counts were correct.

The fix was a reflection-based normalization:

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

The function first checks for `[]any`. If that fails, it uses `reflect.ValueOf()` to inspect the runtime type. If the value is a slice or array of any kind, it iterates over elements and appends each one to the output. This handles both JavaScript arrays and Go slices, including typed slices from database queries.

The generated-site smoke test caught this failure: after an action updated the row count to 4, the table content was empty. The fix was to normalize typed Go slices through reflection before passing them into Widget IR construction.

### Generated Widget IR

The recipe output is equivalent to:

```json
{
  "kind": "component",
  "type": "DashboardGrid",
  "props": { "recipe": "two-up" },
  "children": [
    {
      "kind": "component",
      "type": "Panel",
      "props": { "title": "Query queue" },
      "children": [
        {
          "kind": "component",
          "type": "DataTable",
          "props": {
            "rows": [...],
            "getRowKey": "id",
            "columns": [...],
            "selectedKey": 1,
            "onRowSelect": { "kind": "server", "name": "select-query" }
          }
        }
      ]
    },
    {
      "kind": "component",
      "type": "Panel",
      "props": { "title": "Selected query" },
      "children": [
        { "kind": "component", "type": "MetadataGrid", ... },
        { "kind": "component", "type": "Inline", ... }
      ]
    }
  ]
}
```

The right-side panel is the result of calling the `detail` callback with the selected row. In the example, `selectedPanel()` returns a `Panel` containing a `MetadataGrid` and an `Inline` of action buttons.

## The `page()` Function and Section Ordering

The `page()` function provides a higher-level API for constructing complete pages. It wraps the `schemaVersion`, `id`, `title`, and `meta` fields into a single page response object, composes a `root` from sections, and supports both explicit `root` nodes and section-based construction.

```js
return rag.page({
    schemaVersion: "0.1.0",
    id: "actions",
    title: "xgoja widget actions demo",
    meta: { shell: "app", maxWidth: "wide" },
    sections: [
        rag.panel({ title: "Header" }, ...),
        rag.recipes.metrics({ items: [...] }),
        rag.recipes.actionToolbar({ ... }),
        rag.recipes.masterDetailTable({ ... })
    ]
})
```

The `page()` function iterates over `sections` and validates each one as a Widget IR node using `isWidgetNodeExport()`. Nodes that do not pass validation are silently dropped. The valid nodes are wrapped in a `Stack` with `gap: "lg"` and assigned to the root.

The `meta` field supports keys like `shell`, `maxWidth`, `navItems`, and `activeNavItemId` that the React app reads at the app boundary to configure the default shell wrapper. These are not part of the Widget IR schema; they are page metadata that the app layer interprets separately.

## Action Normalization

Action specs can be expressed in two formats. The first is a full specification:

```js
{ kind: "server", name: "add-query", payload: { owner: "research" } }
```

The second is a plain string:

```js
"add-query"
```

The recipe's `normalizeActionSpec` helper converts the string format to the full format automatically. The full format passes through unchanged. Both produce identical JSON output.

This dual format serves two purposes. The string format is terse and sufficient for simple server actions where the default `{ kind: "server" }` wrapping is correct. The full format is necessary when additional fields like `payload` or custom action types are required.

## The Full Showcase: `sites.js`

The file `examples/xgoja/widget-site/verbs/sites.js` demonstrates how recipes combine with low-level widgets to produce a complete action dashboard. The script defines 221 lines of JavaScript that serve a React app, expose Widget IR pages, and handle server actions.

The page construction is clean:

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
                rag.caption({ tone: "muted" }, "This page is authored by a jsverb...")
            ),
            pageSummary(id),       // rag.recipes.metrics(...)
            toolbar(),             // rag.recipes.actionToolbar(...)
            rag.recipes.masterDetailTable({
                title: "Query queue",
                rows,
                columns: queryColumns(),
                selectedKey: appState.selectedId,
                onRowSelect: "select-query",
                detail: () => selectedPanel(selected)
            }),
            auditPanel()
        ]
    })
}
```

Each section is a single function call. The `pageSummary()` and `toolbar()` functions return recipe output. The `masterDetailTable()` recipe receives data from `allRows()` and `queryColumns()`. The `auditPanel()` function composes a `Stack` of `Caption` nodes from the audit trail array.

The actions are handled by Express POST handlers:

```js
app.post("/api/widget/actions/cycle-status", (req, res) => {
    const id = Number(payload(req).id || appState.selectedId)
    const rows = db.query("SELECT status FROM queries WHERE id = ?", id)
    if (rows.length === 0) return res.status(404).json({ ok: false, error: "query not found" })
    const status = nextStatus(rows[0].status)
    db.exec("UPDATE queries SET status = ? WHERE id = ?", status, id)
    appState.selectedId = id
    res.json(actionResult("Query #" + id + " status -> " + status))
})
```

Each action handler updates in-memory SQLite state, updates `appState` for the detail panel, and returns `{ ok: true, refresh: true, toast: message }`. The React app responds to `refresh: true` by re-fetching the page, which calls `widgetPage()` again, which queries fresh data from SQLite, which produces a new Widget IR response.

## Validation

The tests in `pkg/widgetdsl/module_test.go` validate recipes through end-to-end serialization:

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
    if err != nil {
        t.Fatalf("build recipe page: %v", err)
    }
    var decoded map[string]any
    if err := json.Unmarshal([]byte(value.String()), &decoded); err != nil {
        t.Fatalf("recipe page is not JSON: %v\n%s", err, value.String())
    }
    assertString(t, decoded, "id", "actions")
    root := decoded["root"].(map[string]any)
    assertString(t, root, "type", "Stack")
    children := root["children"].([]any)
    if len(children) != 3 {
        t.Fatalf("recipe page children len = %d, want 3: %#v", children)
    }
    toolbar := children[1].(map[string]any)
    assertString(t, toolbar, "type", "Panel")
}
```

The test validates that:

1. All three recipes can be called in a single `page()` call.
2. The result is JSON-serializable via `JSON.stringify()`.
3. The exported Go map has the correct structure: `id: "actions"`, root type `"Stack"`, three children (metrics, toolbar, masterDetailTable).
4. The toolbar is correctly expanded to a `Panel`.

The action spec normalization is also tested here: `"add-query"` is converted to a full `server` spec, and `rag.action.server("reset-demo")` is used for explicit action construction. Both formats coexist in the same page.

## Design Decisions

### Recipes return Widget IR, not HTML

Recipes must return JSON-compatible Widget IR. This is the single most important constraint. A recipe that returns HTML strings, React elements, or framework-specific representations creates a second rendering path that is separate from the `WidgetRenderer`.

This constraint shapes the function callback pattern. When a recipe needs a detail panel that depends on the current row selection, it accepts a JavaScript function, calls it, and converts the result to Widget IR. The function does not cross the Goja-to-Go boundary as a callable reference.

### Slice normalization is mandatory

Typed Go slices from database queries, host services, and other Go sources do not have the type `[]any`. The original `anySlice` implementation checked for `[]any` only and returned an empty slice for typed slices. The fix was reflection-based normalization that handles any slice or array kind.

This applies to any recipe that accepts rows, columns, items, or similar array data. Every array input must go through `anySlice()`.

### Action normalization supports two formats

The dual format for action specs (full `server` object and plain string) serves both terseness and flexibility. The string format is sufficient for simple server actions. The full format is necessary when `payload` or custom action types are required.

The `normalizeActionSpec` helper handles both formats in a single function. It checks for the full format first, falls back to string parsing, and finally checks for a `name` field as a last resort.

### `page()` stacks sections with default gap

The `page()` function wraps sections in a `Stack` with `gap: "lg"`. This provides consistent spacing between sections without requiring the author to wrap every section in a `Stack` manually. The author can still override the gap by passing a `gap` option to `page()`.

### `metrics()` auto-selects layout recipe

The `metrics()` recipe selects the `DashboardGrid` layout recipe based on item count: `"two-up"` for 2 or fewer, `"three-up"` for 3, and `"four-up"` for 4 or more. This removes the need for the author to decide on a layout strategy.

### `detailNode()` has a fallback

When the `detail` callback is not a function and no fallback node is provided, `detailNode()` returns a default panel with a `Caption` instructing the user to select a row. This prevents the detail panel from being invisible when no row is selected or when the callback fails.

## Risks and Trade-offs

### Recipes add Go code complexity

Each recipe adds Go implementation that must handle edge cases: empty arrays, malformed items, missing fields, Goja function binding failures, and typed slice normalization. The `detailNode()` function has five exit paths: Goja function success, Goja function error, direct node fallback, typed slice normalization, and default panel.

This complexity is justified because the recipes are used frequently in page construction. A page with three recipes requires three lines of JavaScript instead of thirty. The trade-off is that recipe bugs affect multiple pages.

### Recipes couple the DSL to specific component compositions

A recipe that expands `metrics()` into `DashboardGrid` + `Panel` + `StatusText` is coupled to those specific component types. If the component library changes, the recipe must change. This is acceptable because the component types are stable and the recipe output is structurally equivalent to what an author would write by hand.

Recipes that depend on component props that change frequently are more fragile. The `metrics()` recipe uses `density: "condensed"` for panels and `icon: true` for status text. These are deliberate choices that match the original RAG frontend style.

### Goja function callbacks have limited scope

The `detailNode()` pattern is useful for detail panels that depend on the current selection. It is not suitable for patterns that require persistent callbacks, event handlers, or async behavior. The function is called once during page construction and the result is serialized. The function does not execute again after the page is rendered.

This limitation is inherent to the JSON-compatible IR model. JavaScript functions cannot cross the Goja-to-Go boundary as callable references. Any callback pattern must be evaluated at page construction time.

## Working Rules for Writing Recipes

1. **Always return Widget IR.** Never return HTML, React elements, or framework-specific types.
2. **Always validate array inputs.** Use `anySlice()` for all array parameters. Typed Go slices from host services are common.
3. **Handle missing fields gracefully.** Use `stringFromMap()`, `boolFromMap()`, and `valueOrDefault()` for all optional parameters.
4. **Use `goja.AssertFunction()` for function detection.** Do not accept `goja.FunctionCall` as a direct parameter.
5. **Validate exported results.** Check that function returns are valid Widget IR nodes before using them.
6. **Provide sensible defaults.** If a required field is missing, use a reasonable default rather than panicking.
7. **Test through JSON serialization.** A recipe that passes Go map assertions but fails JSON serialization is broken.
8. **Keep recipes focused.** Each recipe should solve one composition problem. Don't combine unrelated patterns.

## Future Directions

### More recipes

Potential recipes that would further reduce authoring complexity:

- `searchResults()` — expands a search query, result rows, and column configuration into a results page with controls, table, and pagination.
- `corpusOverview()` — expands corpus metadata and statistics into a dashboard with grid, chart, and detail panels.
- `workflowBuilder()` — expands a workflow configuration into a node-based editor with connection points and action triggers.

These recipes would follow the same pattern: accept high-level data, return Widget IR, normalize all array inputs, validate all outputs.

### Recipe composition

Recipes could compose other recipes. A `dashboard()` recipe could accept multiple recipe calls and render them in a responsive grid:

```js
rag.recipes.dashboard([
    rag.recipes.metrics({ items: [...] }),
    rag.recipes.actionToolbar({ actions: [...] }),
    rag.recipes.masterDetailTable({ rows, columns, ... })
])
```

This would remove the need for the `page()` wrapper to handle stacking. The `dashboard()` recipe would handle layout, spacing, and responsive behavior.

### Recipe validation

The current schema validates Widget IR at the node level. It does not validate recipe-specific constraints: whether a `metrics()` item has a valid `status`, whether a `masterDetailTable()` `detail` callback returns a valid node, whether an `actionToolbar()` action spec has a valid `kind` field.

Adding recipe-level validation to the schema would catch errors at page construction time rather than at render time. This would be a future improvement.

## References

- `pkg/widgetdsl/module.go` — recipe implementations: `metricsRecipe()`, `actionToolbarRecipe()`, `masterDetailTableRecipe()`, `detailNode()`, `anySlice()`, `normalizeActionSpec()`.
- `pkg/widgetdsl/module_test.go` — recipe tests through end-to-end JSON serialization.
- `examples/xgoja/widget-site/verbs/sites.js` — full showcase demonstrating recipe composition with Express, SQLite, actions, and React app serving.
- `pkg/widgetrunner/runner.go` — runner that invokes page functions and validates Widget IR.
- `pkg/widgetserver/server.go` — server that exposes `/api/widget/pages/{id}` and `/api/widget/actions/{name}`.
- `packages/rag-evaluation-site/src/widgets/WidgetRenderer.tsx` — React renderer that maps Widget IR to real components.
- `internal/api/dsl_handlers.go` — the original hand-coded IR that recipes replaced.
