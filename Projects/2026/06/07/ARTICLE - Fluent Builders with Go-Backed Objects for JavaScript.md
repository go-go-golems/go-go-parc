---
title: "Fluent Builders with Go-Backed Objects for JavaScript"
aliases:
  - goja-text fluent builder pattern
  - Go-backed JavaScript builders
  - NativeModule builder pattern
  - GOJA-TEXT-004
  - GOJA-TEXT-005
tags:
  - article
  - goja
  - go
  - fluent-api
  - native-modules
  - xgoja
  - text-algorithms
  - templating
  - markdown
  - builder-pattern
  - javascript
status: active
type: article
created: 2026-06-07
repo: /home/manuel/workspaces/2026-06-07/goja-render-markdown/goja-text
---

# Fluent Builders with Go-Backed Objects for JavaScript

This article examines a design pattern used in `goja-text` to expose fluent, typed builders from Go to JavaScript through the goja runtime. It shows how Go owns the domain model, validation, and serialization while JavaScript drives the workflow through method chains. The article is based on two consecutive implementations — the `template` module for Go `text/template` and `html/template` rendering, and the `markdown` module's builder for generating Markdown documents programmatically.

The target audience is someone who writes Go and JavaScript and needs to expose a Go-backed API to JavaScript scripts that run inside a goja runtime, without falling into the trap of letting JavaScript maps represent the domain model.

> [!summary]
> - **Go owns the domain model, JavaScript owns the workflow.** All mutable state lives in Go structs. JavaScript calls PascalCase exported Go methods through reflection. The returned objects are still Go-backed, so fluent chains continue.
> - **Three phases, one boundary at a time.** Each module follows the same sequence: service layer (pure Go, no goja imports), native module adapter (Loader, SetExport, goja conversion), and provider wiring (xgoja buildspec and embedded assets).
> - **Fluent APIs fail when they become too thin.** A bare `render(template, data)` wrapper forces JavaScript to construct the domain. A proper builder that accumulates configuration through chained methods keeps Go in control of validation, normalization, and output formatting.

---

## The Problem: When JavaScript Maps Become the Source of Truth

The most common way to expose a Go API to JavaScript is to accept `goja.Value` objects, call `Export()` to get `map[string]interface{}`, and process that map. This works for simple one-shot functions. It breaks down when the JavaScript caller needs to build something with state: configuration, a document tree, a set of parameters that must validate against each other.

Consider a template rendering API. The naive version looks like this:

```javascript
const result = template.render({
    template: "Hello {{ .Name }}",
    name: "Ada",
    funcs: ["sprig", "glazed"]
});
```

The problem is not with the function call itself. The problem is that the object above is a JavaScript map that the Go side receives as a Go map. JavaScript constructs it. Go reads it. Neither side has type safety. The Go side cannot validate that `name` is the right field for the template engine. It cannot enforce that `funcs` contains only recognized preset names. It cannot freeze the configuration and reject mutations after parsing.

The JavaScript caller also cannot chain method calls. It must assemble a single configuration object. There is no way to express intent incrementally.

A fluent builder fixes this. The Go side defines the domain model as typed structs. JavaScript calls exported methods that modify the struct in place and return the same builder reference. The chain continues. Validation happens before the final `Render()` call. The result is a Go-backed object that JavaScript reads through its exported fields.

```javascript
const result = template.text()
    .Name("greeting")
    .Funcs("sprig", "glazed")
    .Parse("Hello {{ .Name | upper }}")
    .Render({ Name: "Ada" });

console.log(result.Text);      // "Hello ADA"
console.log(result.Bytes);     // number
```

The domain model — `TemplateConfig`, `TemplateSet`, `RenderResult` — lives entirely in Go. JavaScript sees the same field names because goja exports Go's exported identifiers. The JavaScript interface uses PascalCase methods and fields because that is how Go exports work, not because it is idiomatic JavaScript. This is a deliberate tradeoff.

---

## The Go-Backed Object Pattern

Every `goja-text` module follows the same architecture. The pattern has three layers, each with a single responsibility.

### Layer 1: The Service Layer

The service layer contains the domain types and the core logic. It imports zero goja packages. It can be tested with `go test` and used by pure Go consumers.

```go
type TemplateBuilder struct {
    cfg         TemplateConfig
    customFuncs texttemplate.FuncMap
    errors      []string
}

func (b *TemplateBuilder) Name(name string) *TemplateBuilder {
    name = strings.TrimSpace(name)
    if name == "" {
        b.errors = append(b.errors, "name must not be empty")
        return b
    }
    b.cfg.Name = name
    return b
}

func (b *TemplateBuilder) Funcs(names ...string) *TemplateBuilder {
    b.cfg.FuncSets = normalizeFuncSets(names)
    return b
}

func (b *TemplateBuilder) Parse(source string) (*TemplateSet, error) {
    return b.ParseNamed(b.cfg.Name, source)
}
```

Each fluent method modifies the internal `cfg` or `customFuncs` and returns `*TemplateBuilder`. The `errors` slice accumulates problems detected by individual calls. Actual validation happens later, either explicitly through `Validate()` or implicitly when `Parse()` or `Render()` is called.

This separation is important. JavaScript never manipulates the config directly. It calls methods. The methods validate at the point of modification (name must not be empty, delimiters must be set together) and defer structural validation (function-set combination rules, mode consistency) until the builder is ready to produce output. This means the JavaScript caller gets immediate feedback for simple mistakes and deferred feedback for complex ones.

### Layer 2: The Native Module Adapter

The adapter layer lives in a `module.go` file. It implements `modules.NativeModule` and wires the service layer into the goja runtime.

```go
type module struct{}

func (module) Name() string { return "template" }

func (module) Doc() string {
    return `
The template module renders Go text/template and html/template documents from JavaScript.

Functions:
  text(): Create a Go-backed text/template builder.
  html(): Create a Go-backed html/template builder with contextual escaping.
  renderText(source, data?): Render a text template in one call.
  renderHTML(source, data?): Render an HTML template in one call.
`
}

func (mod module) Loader(vm *goja.Runtime, moduleObj *goja.Object) {
    exports := moduleObj.Get("exports").(*goja.Object)

    modules.SetExport(exports, mod.Name(), "text", func() *TemplateBuilder {
        builder := NewTextBuilder()
        return builder
    })
    modules.SetExport(exports, mod.Name(), "renderText", func(source string, data goja.Value) (*RenderResult, error) {
        return RenderText(source, exportTemplateData(data))
    })
}

func init() {
    modules.Register(&module{})
}
```

The `Loader` function receives the goja runtime and the module's exports object. It uses `modules.SetExport` to register each JavaScript-visible function. The first argument to `SetExport` is the exports object, the second is the package name (for namespacing), the third is the JavaScript property name, and the fourth is a Go function that goja calls when JavaScript accesses that property.

For builder factories like `text()`, the exported function creates a new `TemplateBuilder` and returns it directly. goja wraps the Go return value so JavaScript can call its methods. The builder object is Go-backed — its methods and fields are the exported Go identifiers.

For one-shot functions like `renderText`, the exported function accepts `goja.Value` for the data argument, calls `Export()` to convert the JavaScript object into a Go-compatible type, and passes the result to the service layer. This is the one boundary where goja conversion happens: the adapter handles the boundary, the service layer handles the logic.

### Layer 3: Provider Registration and Buildspec

The goja-text modules are not self-contained binaries. They are packaged into a generated xgoja binary through a two-step process.

First, the provider package must blank-import the module so its `init()` registration runs:

```go
import (
    _ "github.com/go-go-golems/goja-text/pkg/template"
)
```

Second, the `xgoja.yaml` buildspec must list the module so JavaScript can `require("template")`:

```yaml
modules:
  - package: goja-text
    name: template
    as: template
```

This pattern means every module has two registration points. Missing either one renders the module invisible at runtime.

---

## The Markdown Builder: A Different Kind of Fluent API

The template module solves one problem: render fixed template files with runtime data. The markdown builder solves a different one: assemble Markdown documents from structured data without string concatenation or template files.

The service layer defines a document model as typed blocks:

```go
type markdownDocument struct {
    Blocks []markdownBlock
}

type markdownBlock interface {
    markdownBlockKind() string
}

type headingBlock struct {
    Level int
    Text  []markdownInline
}

type tableBlock struct {
    Columns []tableColumn
    Rows    [][]markdownInline
}

type listItem struct {
    Inlines []markdownInline
}
```

The Markdown builder is not a parser. It is a serializer. It takes structured input from JavaScript and produces well-formed Markdown output. Go owns the output formatting: blank lines between blocks, table alignment and pipe escaping, code fence selection, inline text escaping.

```go
func (b *MarkdownBuilder) Title(text any) *MarkdownBuilder {
    return b.Heading(1, text)
}

func (b *MarkdownBuilder) Heading(level int, text any) *MarkdownBuilder {
    if level < 1 || level > 6 {
        b.addError("heading level must be 1..6, got %d", level)
        return b
    }
    inlines, err := normalizeInlineInputs([]any{text})
    if err != nil {
        b.addError("heading: %v", err)
        return b
    }
    b.doc.Blocks = append(b.doc.Blocks, headingBlock{Level: level, Text: inlines})
    return b
}

func (b *MarkdownBuilder) RenderString() (string, error) {
    result, err := b.Render()
    if err != nil {
        return "", err
    }
    return result.Text, nil
}
```

JavaScript drives the workflow through fluent calls:

```javascript
const markdown = require("markdown");
const i = markdown.inline();

const output = markdown.builder()
    .Title("Sprint report")
    .Paragraph("Generated from structured data.")
    .Table()
        .Columns(
            { label: "Name", align: "left" },
            { label: "Score", align: "right" }
        )
        .Row("Parser", 42)
        .Row("Builder", "in progress")
        .End()
    .Heading(2, "Next steps")
    .Checklist([
        { text: "Expose goja API", checked: true },
        { text: "Write docs" }
    ])
    .RenderString();
```

The output is clean Markdown:

```markdown
# Sprint report

Generated from structured data.

| Name    | Score |
| :------ | ----: |
| Parser  | 42    |
| Builder | in progress |

## Next steps

- [x] Expose goja API
- [ ] Write docs
```

The builder does not use templates at all. Templates are useful when the document shape is known ahead of time. The builder is useful when the document is assembled programmatically — sections are added conditionally, tables are built from runtime data, lists are generated in loops.

---

## Table Rendering: The Core Complexity

Markdown tables are the most fragile structure in plain text. A pipe inside a cell breaks rendering. An empty row creates a malformed table. Misaligned columns produce hard-to-read output. The markdown builder's table implementation handles all of this through a typed cell model and deterministic formatting.

The table builder is a child builder. It returns itself for chaining and returns the parent `MarkdownBuilder` when `End()` is called:

```go
type TableBuilder struct {
    parent *MarkdownBuilder
    table  *tableBlock
    closed bool
}

func (t *TableBuilder) Columns(columns ...any) *TableBuilder {
    t.table.Columns = t.table.Columns[:0]
    for _, column := range columns {
        parsed, err := normalizeTableColumn(column)
        if err != nil {
            t.parent.addError("table columns: %v", err)
            continue
        }
        t.table.Columns = append(t.table.Columns, parsed)
    }
    return t
}

func (t *TableBuilder) Row(cells ...any) *TableBuilder {
    row := make([]markdownInline, 0, len(cells))
    for _, cell := range cells {
        inlines, err := normalizeInlineInput(cell)
        if err != nil {
            t.parent.addError("table row: %v", err)
            continue
        }
        row = append(row, cellInline(inlines))
    }
    t.table.Rows = append(t.table.Rows, row)
    return t
}

func (t *TableBuilder) End() *MarkdownBuilder {
    if t.closed {
        t.parent.addError("table end: table already ended")
        return t.parent
    }
    t.closed = true
    t.parent.doc.Blocks = append(t.parent.doc.Blocks, *t.table)
    return t.parent
}
```

The renderer formats tables through a multi-pass approach. First it computes column widths by scanning headers and all rows. Then it renders each row with padded cells. Table cells escape pipes as `\|` and convert newlines to `<br>`. Alignment controls the separator row: `:---` for left, `:---:` for center, `---:` for right.

```go
func renderTable(block tableBlock) (string, error) {
    columns := len(block.Columns)
    if columns == 0 {
        return "", fmt.Errorf("table requires at least one column")
    }
    widths := computeWidths(block)
    headers := renderHeaders(block.Columns, widths)
    alignmentRow := renderAlignmentRow(block.Columns, widths)
    dataRows := renderDataRows(block.Rows, widths)
    return strings.Join(append(headers, alignmentRow, dataRows...), "\n"), nil
}

func escapeTableCell(s string) string {
    s = strings.ReplaceAll(s, "|", `\|`)
    s = strings.ReplaceAll(s, "\n", "<br>")
    return strings.TrimSpace(s)
}
```

The child builder lifecycle — `Table()` creates, methods accumulate, `End()` commits — is the most error-prone part of the API. The implementation guards against double `End()` by setting a `closed` flag and recording a validation error. Calls after `End()` are rejected but do not panic, because panicking in a builder that JavaScript is calling would crash the goja runtime.

---

## JavaScript Callbacks: When JavaScript Lives Inside Go Templates

The template module includes a feature that the markdown builder does not need: `JSFunc`. It lets JavaScript register a function as a Go template helper:

```javascript
const result = template.text()
    .JSFunc("badge", (value) => `[[${String(value).toUpperCase()}]]`)
    .Parse("{{ badge .Name }}")
    .Render({ Name: "ada" });

console.log(result.Text); // "[[ADA]]"
```

The implementation wraps the JavaScript function in a Go function that converts template arguments to JavaScript values, calls the JS function, and converts the result back:

```go
b.customFuncs[name] = func(args ...any) (any, error) {
    jsArgs := make([]goja.Value, 0, len(args))
    for _, arg := range args {
        jsArgs = append(jsArgs, b.vm.ToValue(arg))
    }
    ret, err := fn(goja.Undefined(), jsArgs...)
    if err != nil {
        return nil, err
    }
    return exportTemplateData(ret), nil
}
```

This breaks the service layer's pure-Go boundary because the builder must now carry a `*goja.Runtime` pointer. The design decision was worth it: the runtime pointer is nil when the builder is used from pure Go, and `JSFunc` validation explicitly rejects nil runtime pointers. The compromise is visible but bounded.

HTML mode adds another constraint. JavaScript helpers cannot produce trusted HTML types like `template.HTML` or `template.URL` because there is no way to create these Go types from JavaScript. Ordinary strings returned from JavaScript helpers remain untrusted and are escaped by `html/template`. This is intentional: JavaScript code running in a `goja-text` script is untrusted input, not a trusted library.

---

## The Markdown Inline Factory

The markdown builder handles ordinary text through escaping. A string passed to `Paragraph()` is rendered as escaped Markdown text. This prevents accidental markdown-sensitive characters (`*`, `_`, `[`, `]`, `<`, `>`, `` ` ``) from breaking the output.

But sometimes a paragraph needs a code span, a link, emphasis, or explicit raw Markdown. The inline factory provides typed constructors for these cases:

```javascript
const i = markdown.inline();

markdown.builder()
    .Paragraph(
        "Run ",
        i.Code("go test ./..."),
        " and read ",
        i.Link("docs", "https://example.com"),
        "."
    )
    .RenderString();
```

The inline factory returns typed Go structs: `CodeInline`, `RawInline`, `LinkInline`, `EmphasisInline`, `StrongInline`. The renderer handles each type appropriately: code spans choose a fence length based on the backtick content, links render as `[text](url title?)`, and raw inline is inserted verbatim.

This separation between escaped text and explicit inline nodes is a design principle: the default is safe, the escape hatch is explicit. Users who want raw Markdown must reach for `Raw()`. Users who want code spans must reach for `i.Code()`. There is no middle ground where a string is "sometimes escaped, sometimes raw."

---

## Help Pages and CLI Commands

Each module ships with Glazed help pages embedded as Markdown files. The provider's `doc` package embeds them with `go:embed *.md` and loads them through `help.LoadSectionsFromFS`. Users can query them with `goja-text help goja-text-<name>-<type>`.

The template module has four pages:
- `template-api-reference.md` — API surface
- `template-user-guide.md` — Guided introduction
- `template-writing-documentation.md` — Tutorial
- (for the markdown builder) `markdown-builder-api-reference.md` — Dedicated reference for the builder API

The markdown builder also has a separate dedicated API reference page. This makes sense because the builder's method list is long enough that it would bloat the general Markdown API reference.

CLI commands come from jsverbs: JavaScript files that define functions with `__verb__()` annotations. The xgoja build scans each file, extracts function signatures and metadata, and registers them as CLI commands. The markdown builder's jsverb adds `builder-examples` and `builder-example` commands that render bundled YAML fixtures through the builder API:

```javascript
const builderHelpers = {
    renderReport(data) {
        const doc = markdown.builder()
            .Title(data.title)
            .Paragraph(data.summary)
            .Table()
                .Columns(
                    { label: "Name", align: "left" },
                    { label: "Status", align: "center" },
                    { label: "Owner", align: "left" }
                );

        for (const row of data.statusRows || []) {
            doc.Row(row.name, row.status, row.owner);
        }

        return doc.End()
            .Heading(2, "Next steps")
            .Checklist(data.nextSteps || [])
            .RenderString();
    },
};
```

---

## Common Failure Modes

The implementations of both the template module and the markdown builder revealed several failure modes that are worth documenting.

### goja value type comparison

goja preserves Go type aliases after `Export()`. A Go `Mode` type alias becomes a value whose dynamic type is not `string` after JavaScript goes through the runtime. Comparing `got["mode"] != "text"` fails because the value's Go type is `Mode`, not `string`. The fix is `fmt.Sprint(got["mode"])` for comparison, which converts through the string representation.

### Top-level function visibility in jsverbs

The jsverb scanner treats all top-level function declarations as commands. Private helpers like `readFile`, `configureBuilder`, and `writeMaybe` become visible CLI commands unless they are moved inside an object. This affects all jsverb files in the project, not just the ones that were written with this knowledge.

### xgoja buildspec toolchain flags

The nested generated module requires both `GOWORK=off` and `GOTOOLCHAIN=go1.26.4`. Without `GOWORK=off`, the workspace root takes priority and the generated module cannot find its packages. Without `GOTOOLCHAIN=go1.26.4`, the Go version mismatch prevents the generated module from loading. Both flags are necessary and non-obvious from the project README.

### Table builder lifecycle

The `End()` method is the only way to commit a table to the document. Forgetting to call it means the table is never appended. Calling it twice records a validation error but does not produce duplicate output. The implementation uses a `closed` flag to make the second call deterministic rather than a no-op with silent failure.

### Child builder return type

`Table()` returns a `*TableBuilder`, not a `*MarkdownBuilder`. The JavaScript caller must call `.End()` to get back to the document builder. This is the source of a common misunderstanding: the builder does not auto-commit tables on the next `Heading()` or `Paragraph()` call. The parent method chain is interrupted by the child builder, and only `End()` resumes it.

---

## Working Rules

From both implementations, several rules emerged that should guide future modules:

1. **Service layer first.** Implement the core logic in a pure Go package with zero goja imports. Test it with `go test` before adding the module adapter. This makes the core logic independently reviewable and testable.

2. **Go owns the domain model.** JavaScript maps should never represent the domain. The domain lives in Go structs. JavaScript calls exported Go methods. JavaScript reads exported Go fields.

3. **Fluent methods return the receiver.** Every builder method returns the same struct pointer so chains continue. This includes error-handling methods — `Name("")` returns `b` after recording an error, not `nil`.

4. **Validate before render, not after.** The builder accumulates errors during method calls. `Render()` calls `Validate()` first and returns a namespaced error if validation fails. The JavaScript caller can also call `Validate()` explicitly to inspect errors without producing output.

5. **Child builders must have a commit point.** `Table()` returns a child builder that must be committed with `End()`. The implementation must handle double `End()` and post-commit calls deterministically.

6. **Help pages live in the provider doc directory.** Adding a `*.md` file to `pkg/xgoja/providers/text/doc/` is all that is needed for it to appear in the generated binary's help system.

7. **JavaScript helpers in jsverbs must be objects, not top-level functions.** The jsverb scanner treats all top-level function declarations as commands.

---

## File Reference

Key files for the template module:
- `pkg/template/types.go` — Domain types and constants
- `pkg/template/builder.go` — Fluent builder and validation
- `pkg/template/render.go` — TemplateSet, parsing, and execution
- `pkg/template/module.go` — NativeModule adapter and JSFunc
- `pkg/template/funcs.go` — Function set selection and merge
- `pkg/template/module_test.go` — Runtime integration tests

Key files for the markdown builder:
- `pkg/markdown/builder_types.go` — Document, block, inline, table types
- `pkg/markdown/builder.go` — Fluent builder methods and validation
- `pkg/markdown/builder_render.go` — Markdown serialization and escaping
- `pkg/markdown/builder_table.go` — TableBuilder and inline factory
- `pkg/markdown/builder_test.go` — Service tests
- `pkg/markdown/module.go` — Goja module export with builder and inline
- `pkg/markdown/module_test.go` — Runtime integration tests

Key files for xgoja wiring:
- `pkg/xgoja/providers/text/text.go` — Provider registration
- `cmd/goja-text/xgoja.yaml` — Module selection and asset configuration
- `cmd/goja-text/jsverbs/markdown.js` — CLI commands
- `pkg/xgoja/providers/text/doc/markdown-builder-api-reference.md` — Glazed help page

## Related notes

- [[ARTICLE - Minitrace API Redesign - From Prototype Complexity to Normalized SQL and Fluent Builders]] — applies the same Go-backed builder pattern to a larger data/query API and records the hard cut away from legacy query surfaces.
- [[ARTICLE - Minitrace Viz API Redesign - Normalized SQL and Fluent Goja Builders]] — earlier minitrace-viz snapshot showing why a single fluent builder surface replaced overlapping DSL/lens/workbench APIs.
- [[PROJ - goja-text - Template and HTML Rendering Module]] — project report for the template builder work that helped establish this pattern.
- [[PROJ - Geppetto - Opinionated JS APIs and Engine Profiles]] — related public-API cleanup: opinionated high-level JS API over explicit lower-level machinery, with engine/runtime ownership kept separate.
- [[ARTICLE - CozoDB Editor Modernization - Sessionstream Hard Cutover]] — later notebook modernization work using the same hard-cutover instinct: typed substrate first, no compatibility wrappers once the new ownership model is clear.

---

> This article documents patterns developed during the implementation of the `template` module (GOJA-TEXT-004) and the `markdown` builder module (GOJA-TEXT-005) in the `goja-text` repository. Both modules share the same architectural pattern and failure modes. The article is written for future contributors who need to add new modules or adapt the pattern to different domains.
