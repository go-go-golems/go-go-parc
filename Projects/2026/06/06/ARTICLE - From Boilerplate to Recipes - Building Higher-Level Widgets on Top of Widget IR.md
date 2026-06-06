---
title: "From Boilerplate to Recipes: Building Higher-Level Widgets on Top of Widget IR"
date: 2026-06-06
type: article
tags: [widget-dsl, widget-ir, recipes, dsl, goja, react]
status: draft
---

# From Boilerplate to Recipes: Building Higher-Level Widgets on Top of Widget IR

> The Widget IR tree is a JSON-compatible data structure.  A recipe is simply a function that returns Widget IR — the same IR that the renderer already understands. Recipes let you write one function call instead of ten lines of repetitive Widget IR composition.

## The Problem: Ten Lines of IR for One Concept

Consider a dashboard showing three status metrics. Written in low-level Widget IR, a simple metrics dashboard needs at least:

```javascript
const rag = require("widget.dsl");

exports.pages = {
  dashboard: rag.page({
    id: "dashboard",
    schemaVersion: "0.1.0",
    sections: [
      rag.panel({ title: "Total Queries", density: "condensed" }, [
        rag.statusText({ status: "ready" icon: true }, "42"),
      rag.panel({ title: "Running", density: "condensed" }, [
        rag.statusText({ status: "running", icon: true }, "3"),
      ]),
    ],
  }),
```

That is verbose and fragile.  Every metric panel repeats the `density: "condensed"` pattern.  If you want three metrics, you write three panels.  If you want a toolbar with labeled actions, you build an inline row of `Button` widgets manually.

Widget IR is powerful — you can express any layout — but it carries no semantic meaning.  Recipes close the gap between *intent* and *mechanism*.

## The Pattern: Recipes Are Just Functions That Return IR

A **recipe** is a Go function that returns Widget IR.  It takes high-level intent ("show four status metrics") and returns the expanded IR tree.  The renderer never sees the recipe; it sees only the IR the recipe produced.

```text
Recipe function  → Widget IR tree → Renderer
```

This is not a new concept: `React` `Component` is a function that returns React elements.  Recipes are the Widget IR equivalent.

## Recipe 1: `metrics()` — Dashboards in One Call

**Goal:** Show 4 KPI tiles in a responsive grid.

```go
func (r *runtime) metricsRecipe(call goja.FunctionCall) goja.Value {
    options := firstObject(call.Arguments)
    items := anySlice(options["items"])
    children := []any{}
    for _, raw := range items {
        item, ok := raw.(map[string]any)
        if !ok { continue }
        label := stringFromMap(item, "label", "Metric")
        status := stringFromMap(item, "status", "ready")
        value := item["value"]
        children = append(children, map[string]any{
            "kind":  "component",
            "type":  "Panel",
            "props":  map[string]any{"title": label, "density": "condensed"},
            "children": []any{map[string]any{
                "kind":  "component",
                "type":  "StatusText",
                "props":    map[string]any{"status": status, "icon": true},
                "children": []any{map[string]any{"kind": "text", "text": fmt.Sprint(value)}},
            },
        },
    }
    return r.vm.ToValue(map[string]any{
        "kind":    "component",
        "type":   "DashboardGrid",
        "props":  map[string]any{"recipe": metricsRecipeName(len(children))},
        "children": children,
    })
}
```

The Go implementation matches the mental model: *loop over the input items, emit one `Panel` per item, wrap in a `DashboardGrid`.

Usage from JavaScript:

```javascript
const rag = require("widget.dsl")

rag.recipes.metrics({
  items: [
    { label: "Total queries", value: 42, status: "ready" },
    { label: "Running", value: 3, status: "running" },
    { label: "Failed", value: 2, status: "failed" },
  ],
})
```

The JavaScript author writes one line instead of ~20 lines of IR.

## Recipe 2: `actionToolbar()` — Action Bars Without Boilerplate

Toolbar buttons are one of the most repetitive patterns. The `actionToolbar` recipe packages an Inline row of Buttons with a caption.

```go
func (r *runtime) actionToolbarRecipe(call goja.FunctionCall) goja.Value {
    options := firstObject(call.Arguments)
    actions := anySlice(options["actions"])
    buttons := []any{}
    for _, raw := range actions {
        item, ok := raw.(map[string]any)
        if !ok { continue }
        label := stringFromMap(item, "label", "Action")
        props := map[string]any{"variant": stringFromMap(item, "variant", "secondary")}
        if act, ok := normalizeActionSpec(item["action"], item["name"], item["payload"]); ok {
            props["action"] = act
        }
        buttons = append(buttons, map[string]any{
            "kind":     "component",
            "type":    "Button",
            "props": props,
            "children": []any{map[string]any{"kind": "text", "text": label},
        })
    }
    if caption, ok := options["caption"].(string); ok && caption != "" {
        captionNode := map[string]any{
            "kind":  "component",
            "type":  "Caption",
            "props": map[string]any{"tone": "muted"},
            "children": []any{map[string]any{"kind": "text", "text": caption},
        }
        buttons = append(buttons, caption)
    }
    return r.vm.ToValue(map[string]any{
        "kind":     "component",
        "type":    "Panel",
        "props":   map[string]any{"title": stringFromMap(options, "title", "Actions")},
        "children": []any{
            map[string]any{
                "kind":  "component",
                "type":   "Inline",
                "props": map[string]any{"gap": stringFromMap(options, "gap", "sm"), "wrap": true},
                "children": buttons,
            },
        },
    })
}
```

A call looks like:

```javascript
rag.recipes.actionToolbar({
  title: "Queue controls",
  caption: "Actions mutate in-memory SQLite state.",
  actions: [
    { label: "Add query", variant: "primary", action: { kind: "server", name: "add-query", payload: { owner: "research" } },
    { label: "Retry failed", action: "bulk-retry-failed" },
    { label: "Reset demo", action: "reset-demo" },
  ],
})
```

The recipe returns a single Panel containing an `Inline` of Buttons.

## Recipe 3: `masterDetailTable` — The Whole Dashboard in One Function

The most powerful recipe.  A master-detail table with an optional detail pane.  The recipe takes rows, columns, selected-key handling, and a `detail` callback — it generates a `DashboardGrid` with a data table panel on the left and an optional detail panel on the right.

```go
func (r *runtime) masterDetailTableRecipe(call goja.FunctionCall) goja.Value {
    options := firstObject(call.Arguments)
    rows := anySlice(options["rows"])
    tableProps := map[string]any{
        "rows":   rows,
        "columns": anySlice(options["columns"]),
        "getRowKey":  valueOrDefault(options["getRowKey"], "id"),
        "emptyMessage": valueOrDefault(options["emptyMessage"], "No rows"),
    }
    if act, ok := normalizeActionSpec(options["onRowSelect"], nil, nil); ok {
        tableProps["onRowSelect"] = act
    }
    tableNode := map[string]any{
        "kind":  "component",
        "type":  "DataTable",
        "props": tableProps,
    }
    detailNode := r.detailNode(options, rows)
    return r.vm.ToValue(map[string]any{
        "kind":    "component",
        "type":     "DashboardGrid",
        "props":    map[string]any{"recipe": stringFromMap(options, "recipe", "two-up")},
        "children": []any{
            map[string]any{
                "kind":     "component",
                "type":     "Panel",
                "props":    map[string]any{"title": stringFromMap(options, "title", "Items")},
                "children": []any{tableNode},
            },
            detailNode,
        },
    })
}
```

Usage:

```javascript
rag.recipes.masterDetailTable({
  title: "Query queue",
  rows: allRows(),
  columns: queryColumns(),
  selectedKey: appState.selectedId,
  onRowSelect: "select-query",
  detail: (row) => selectedDetailPanel(row),
})
```

The `detail:` callback receives a row and can return a Widget IR node.  When a row is selected, the right panel re-renders.

### The `detail:` Callback Pattern

The `detail` option is important.  In Goja, a function passed from JavaScript to Go and back must cross the Goja↔JS bridge correctly.  The `detail` function is stored as a Goja `Value` and called with `goja.AssertFunction()`.  The recipe calls this function to produce the detail panel IR:

```go
func (r *runtime) detailNode(options map[string]any, rows []any) any {
    if detailFn, ok := options["detail"]; ok {
        if fn, ok := detailFn.(*goja.Object); ok {
            rows := anySlice(rows)
            selectedKey := stringFromMap(options, "selectedKey", "id")
            selectedRow := selectedRow(rows, selectedKey)
            val, err := detailFn(goja.Undefined(), r.vm.ToValue(selectedRow))
            if err != nil {
                panic(err)
            }
            if exported, ok := val.Export().(map[string]any); ok && isWidgetNodeExport(exported) {
                return exported
            }
        }
    }
    // fallback detail node
    return map[string]any{
        "kind":     "component",
        "type":    "Panel",
        "props":    map[string]any{"title": stringFromMap(options, "detailTitle", "Details")},
        "children": []any{map[string]any{
            "kind":  "component",
            "type":  "Caption",
            "props": map[string]any{"tone": "muted"},
            "children": []any{map[string]any{"kind": "text", "text": "Select a row to inspect."}},
        },
    }
}
```

The Goja runtime passes `selectedRow` into the callback, gets back a Widget IR node, and places it as the right-hand panel in a `DashboardGrid`.

## How Recipes Compose

Recipes are just functions returning Widget IR, so they compose naturally.  A `page` recipe uses the `metrics` recipe, an `actionToolbar`, a `masterDetailTable`, and an audit trail panel:

```javascript
const rag = require("widget.dsl")

exports.pages = {
  actions: (ctx) => rag.page({
    schemaVersion: "0.1.0",
    id: "actions",
    title: "Widget actions demo",
    sections: [
      rag.recipes.metrics({ items: [ ... ] }),
      rag.recipes.actionToolbar({ ... }),
      rag.recipes.masterDetailTable({ ... }),
      auditPanel(),
  ]}),
```

Each recipe returns standard Widget IR, so it can be nested arbitrarily.

## The Design Contract for New Recipes

Any recipe must follow these rules:

1.  **Return valid Widget IR.**  The recipe is a Go function that returns a `map[string]any` (or `[]any` for array) whose structure matches Widget IR.  The renderer never sees the recipe; it only sees the expanded IR.

2.  **Use `anySlice()` for slice parameters.** The JavaScript author may pass a Go struct-backed array (e.g., database query results).  The Go implementation must handle both Go-backed arrays and JavaScript arrays uniformly. The `anySlice()` helper normalizes both into `[]any`.

3.  **Normalize actions with `normalizeActionSpec`.  Recipes must pass action specs through `normalizeActionSpec`, which accepts a string shorthand or full spec object.

4.  **Make the `detail` callback work across the JS/Go bridge.  When a callback is a `goja` function, call it with the provided arguments and return the exported result.  Remember that `goja.AssertFunction` validates that the value is callable; if the callback is optional, handle the nil case.

5.  **Document the recipe in the provider help docs.** The `widget-dsl-getting-started` and `widget-dsl-js-api-reference` help pages cover the recipe functions.

## Gotchas and Lessons

### The Go slice problem

Goja returns JavaScript arrays as Goja `Value` objects.  A naive Go implementation that casts the slice via `value.Export().([]any)` will miss Go-backed rows (e.g. from `db.query`), which come back as `reflect.Slice` or `reflect`-based types. The `anySlice()` helper uses `reflect` to inspect the actual Go type and normalize all the elements:

```go
func anySlice(value any) []any {
    if value == nil {
        return nil
    }
    rv := reflect.ValueOf(value)
    if rv.Kind() == reflect.Slice || rv.Kind() == reflect.Array {
        n := rv.Len()
        result := make([]any, 0, n)
        for i := 0; i < n; i++ {
            out = append(out, rv.Index(i).Interface())
        }
        return out
    }
    // already a []any, or a single object, pass through
    switch v := value.(type) {
    case []any:
        return v
    case any:
        return []any{v}
    default:
        return []any{}
    }
}
```

Without this step, Go-backed arrays silently disappear or cause runtime panics.

### Callbacks across the language boundary

When `masterDetailTable` receives a `detail` callback (a JavaScript function), that callback must be called from **Go**, not JavaScript.  Go code calls the function using `detailFn(goja.Undefined(), r.vm.ToValue(selectedRow))`, where the first argument is `undefined` (since Goja's function call API is positional, not named).

### The `detail:` option can be a plain Widget IR

If the `detail` option is a Widget IR node (a map with `kind: "component"`), it is used directly as the detail panel content, and no callback invocation is needed. This pattern is useful for static details.

## The full recipe API

| Recipe | Purpose | Parameters | Returns
|---|---|---|---|
| `metrics` | Dashboard-style metric tiles | `items` (array of `{label, value, status}`), | DashboardGrid with panels |
| `actionToolbar` | Action bar with buttons | `actions` (array of action specs), `title`, `caption` | Panel with Inline buttons |
| `masterDetailTable` | Two-up layout with detail pane | `rows`, `columns`, `selectedKey`, `onRowSelect`, `detail` callback | DashboardGrid with DataTable + detail panel |

## Extending with your own recipes

To add a new recipe, add a new method on the `runtime` struct in `module.go`.  Each recipe is a function that:

1. Takes a `goja.FunctionCall`
2. Reads named arguments from `firstObject(call.Arguments)`
3. Returns a valid Widget IR node

For example, a `chart` recipe could generate a Panel with a CodeText code block showing syntax-highlighted code.  The important point is that recipes return the same IR the renderer already understands, so they work with zero modifications to the renderer.

## Further Reading

- The Widget IR types: `packages/rag-evaluation-site/src/widgets/ir.ts`
- The renderer: `packages/rag-evaluation-site/src/widgets/WidgetRenderer.tsx`
- The Go implementation: `pkg/widgetdsl/module.go`
