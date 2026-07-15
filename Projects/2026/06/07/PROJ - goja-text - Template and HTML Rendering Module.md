---
title: goja-text — Template and HTML Rendering Module
aliases:
  - goja-text template module
  - goja-text templates
  - GOJA-TEXT-004
tags:
  - project
  - goja
  - go
  - templates
  - html-templates
  - native-modules
  - xgoja
  - text-algorithms
  - templating
status: complete
type: project
created: 2026-06-07
repo: /home/manuel/workspaces/2026-06-07/goja-text-templates/goja-text
source_ticket: GOJA-TEXT-004
---

# goja-text — Template and HTML Rendering Module

This is the rendering and output-boundary branch of the [[goja-text]] project map.

## A Complete Native Module from Design to Bundled Examples

> [!summary]
> - **Go-backed builders for template configuration** — All mutable template state lives in Go structs. JavaScript reads exported field and method names. No JS maps represent parsed templates.
> - **Synchronous JavaScript callbacks** — `JSFunc(name, fn)` registers inline JavaScript helpers that execute during template rendering. Returns are ordinary strings, escaped in HTML mode.
> - **Embedded reusable examples** — xgoja bundles template/data pairs as read-only assets at `/templates`, mounted through a separate `fs:assets` module alias.

This report documents the complete lifecycle of the `template` module — the fourth native module added to `goja-text`. It started as a design document, passed through five implementation phases, and landed as a fully wired xgoja module with CLI commands, JavaScript verb helpers, and bundled examples. Every step was tracked through a docmgr ticket, an investigation diary, and a series of committed checkpoints.

The goal of this note is not to catalog files changed, but to explain *why* each design decision was made, what failed during implementation, and what patterns emerged that will inform future modules.

---

## 1. The Starting Point

`goja-text` already had three native JavaScript modules when this work began. Each one exposed Go-backed text processing through the `modules.NativeModule` interface:

```
goja-text/
  pkg/
    markdown/module.go      — Markdown AST, walk(), Go-backed MarkdownNode
    sanitize/module.go      — YAML/JSON repair, Go-backed options builders
    extract/module.go       — Structured-data extraction, Go-backed candidates
  cmd/goja-text/
    xgoja.yaml              — Provider wiring for gojaget text modules
    jsverbs/                — CLI verb commands for each module
```

Each module followed the same pattern:

- Implement `modules.NativeModule` with `Name()`, `Doc()`, and `Loader()`.
- Register through `init()` and the default module registry.
- Return Go-backed domain objects that JavaScript reads via exported field and method names.
- Wire into the xgoja generated binary through `cmd/goja-text/xgoja.yaml`.

What was missing was the ability to render Go templates — `text/template` for Markdown and plain text, `html/template` for contextually escaped HTML. Scripts that lived in the xgoja runtime had to hand-roll string interpolation or shell out to another tool. The `glazed` package already had template helper functions and Sprig integration, but nothing in `goja-text` let a JavaScript script render a template directly.

The design requirement was clear: expose Go's template engines as a fluent, Go-backed JavaScript API. Not a thin `render(template, object)` wrapper, but a proper builder that accumulated configuration, parsed templates, and rendered results — all while keeping domain state in Go.

---

## 2. Architecture: Native Modules and the Go Backed Object Pattern

Every `goja-text` module implements the same core interface from `go-go-goja`:

```go
type NativeModule interface {
    Name() string
    Doc() string
    Loader(*goja.Runtime, *goja.Object)
}
```

The `Loader` function receives the goja runtime and the module's exports object. It populates `exports` with Go functions that goja calls when JavaScript runs `require("<name>")`. The registry handles the connection between goja-nodejs `require()` and the Go implementation.

For `template`, the module exposes four top-level entrypoints:

```javascript
const template = require("template");

// Two builder factories — one for text, one for HTML
template.text()       // Go-backed text/template builder
template.html()       // Go-backed html/template builder

// Convenience one-shot helpers
template.renderText("Hello {{ .Name }}", { Name: "Ada" });
template.renderHTML("<p>{{ .Name }}</p>", { Name: "Ada" });
```

The critical design choice is what `text()` and `html()` return. They return a `TemplateBuilder` — a Go struct with fluent methods like `Name()`, `Funcs()`, `MissingKey()`, `Delims()`, `Parse()`, and `Render()`. JavaScript invokes these methods through goja's reflection system, and the returned objects are still Go-backed, so the fluent chain continues.

```go
type TemplateBuilder struct {
    cfg         TemplateConfig
    customFuncs texttemplate.FuncMap
    vm          *goja.Runtime    // captured from JS side for JSFunc
    errors      []string
}

type TemplateConfig struct {
    Mode       Mode     // "text" or "html"
    Name       string
    FuncSets   []string // "sprig", "glazed", "none"
    MissingKey string   // "error", "invalid", "zero", "default"
    LeftDelim  string
    RightDelim string
}

type TemplateSet struct {
    Mode    Mode
    Name    string
    text    *template.Template    // only one is non-nil
    html    *htmltemplate.Template
}

type RenderResult struct {
    Text         string
    TemplateName string
    Mode         Mode
    Bytes        int
}
```

This is the same pattern `sanitize` uses for its `YamlOptionsBuilder` and `JsonOptionsBuilder`, and the same pattern `markdown` uses for `MarkdownNode`. The Go representation is the domain model. JavaScript is the query language.

---

## 3. Phase One: The Service Layer

The first implementation step was purely Go code. No goja imports, no module wiring. Just domain types, builders, validation, and rendering logic.

The builder accumulates configuration through chained method calls. Each method modifies the internal `TemplateConfig` or appends to an `errors` slice. Validation happens at `BuildConfig()` and `Validate()` — parsing is deferred until `Parse()` is called, after which the config is frozen.

```go
func NewTextBuilder() *TemplateBuilder {
    return &TemplateBuilder{
        cfg: TemplateConfig{
            Mode: ModeText,
            Name: defaultTemplateName,
            FuncSets: []string{"sprig", "glazed"},
            MissingKey: MissingKeyError,
        },
        customFuncs: texttemplate.FuncMap{},
    }
}
```

Two template engines share one `TemplateSet` wrapper. The struct stores either `*template.Template` or `*htmltemplate.Template`, and `Render()` switches on the `Mode` field to pick the correct one. This keeps the JavaScript surface small while preserving the distinct escaping semantics of each engine.

The function-set system selects helper presets by name rather than accepting a raw `template.FuncMap`. Three presets are available: `"sprig"`, `"glazed"`, and `"none"`. The preset names are stable, documented, and validated. This avoids the friction of JavaScript users trying to construct a `template.FuncMap` — they instead write `.Funcs("sprig", "glazed")` and get predictable results.

The preset merge order matters. Sprig functions are merged first, then Glazed functions override or complement them. Both use the same internal `mergeFuncMap()` which sorts keys for deterministic behavior. The `none` preset is special: it can only be used alone, and the validation logic rejects combinations like `.Funcs("none", "sprig")`.

The validation logic checks:
- Mode is `"text"` or `"html"`
- Name is non-empty
- MissingKey is one of the four allowed values
- Delims are set together and differ from each other
- Function sets are valid names and don't combine `"none"` with other presets

Service-level tests proved this layer worked before any JavaScript plumbing existed:

```bash
cd goja-text
go test ./pkg/template -count=1
```

Tests covered text rendering, HTML escaping, named templates (`{{ define }}` / `{{ template }}`), `missingkey=error` behavior, builder validation errors, and the convenience render functions. All passed on the first run.

---

## 4. Phase Two: Native Module Adapter

With the service layer validated, the next step was exposing it to JavaScript. The module adapter lives in `pkg/template/module.go` and implements `modules.NativeModule` and `modules.TypeScriptDeclarer`.

The `Loader` function is deliberately small. It creates builders, wires convenience render functions, and nothing else:

```go
func (mod module) Loader(vm *goja.Runtime, moduleObj *goja.Object) {
    exports := moduleObj.Get("exports").(*goja.Object)

    modules.SetExport(exports, mod.Name(), "text", func() *TemplateBuilder {
        builder := NewTextBuilder()
        builder.vm = vm
        return builder
    })
    modules.SetExport(exports, mod.Name(), "html", func() *TemplateBuilder {
        builder := NewHTMLBuilder()
        builder.vm = vm
        return builder
    })
    modules.SetExport(exports, mod.Name(), "renderText", func(src string, data goja.Value) (*RenderResult, error) {
        return RenderText(src, exportTemplateData(data))
    })
    modules.SetExport(exports, mod.Name(), "renderHTML", func(src string, data goja.Value) (*RenderResult, error) {
        return RenderHTML(src, exportTemplateData(data))
    })
}
```

The `vm = vm` assignment is a critical detail for a later feature. The builder captures the goja runtime when JavaScript creates it, so that later `JSFunc` calls can convert Go template arguments back to JavaScript values. Without this, `JSFunc` would have no runtime to work with.

The convenience functions accept `goja.Value` and explicitly call `Export()` to convert JavaScript objects into Go maps before passing them to the service layer. This is a deliberate separation: the module adapter handles goja conversion, the service layer handles rendering.

Runtime integration tests use `engine.NewRuntimeFactoryBuilder().UseModuleMiddleware(engine.MiddlewareOnly("template"))` to boot a minimal goja runtime with only the template module. Tests exercise the fluent builder chain, HTML escaping, named template rendering, and validation errors.

**Failure mode: type comparison on exported values.**

The first runtime test compared `got["mode"] != "text"` and failed:

```
unexpected result: map[string]interface {}{"bytes":12, "mode":"text", "name":"greeting", "text":"Hello INTERN"}
```

The printed value looked correct, but the dynamic type of `mode` was not `string` — goja's reflection preserved the Go `Mode` type alias after `Export()`. The fix was to use `fmt.Sprint(got["mode"])` for the comparison.

Another failure appeared during linting. An unused `normalizeTemplateData` function caused `golangci-lint` to fail with:

```
pkg/template/module.go:55:6: func normalizeTemplateData is unused (unused)
```

Removing it was straightforward. The lesson was that helper functions meant for future use should be explicitly unused or removed, not left as dead code in the module layer.

---

## 5. Phase Two B: JavaScript Callbacks with JSFunc

The original design deferred JavaScript callback functions inside templates to a later phase. The implementation proved that this phase is tractable and not especially risky for synchronous use.

The `TemplateBuilder.JSFunc(name, fn)` method registers a JavaScript function as a Go template helper. The name must match `[A-Za-z_][A-Za-z0-9_]*` — template function names are identifiers, not arbitrary strings.

```go
func (b *TemplateBuilder) JSFunc(name string, value goja.Value) *TemplateBuilder {
    if !templateFuncNamePattern.MatchString(name) {
        b.errors = append(b.errors, fmt.Sprintf("invalid JS function name %q", name))
        return b
    }
    fn, ok := goja.AssertFunction(value)
    if !ok {
        b.errors = append(b.errors, fmt.Sprintf("JSFunc %q must be a function", name))
        return b
    }
    if b.vm == nil {
        b.errors = append(b.errors, fmt.Sprintf("JSFunc %q requires a goja runtime-backed builder", name))
        return b
    }
    if b.customFuncs == nil {
        b.customFuncs = map[string]any{}
    }
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
    return b
}
```

The wrapper converts Go template arguments to JavaScript values via `b.vm.ToValue(arg)`, calls the JavaScript function, and converts the result back to Go via `exportTemplateData()`. The template function signature is `func(args ...any) (any, error)` — a natural fit for Go template's variable-arity function calls.

HTML mode preserves contextual escaping: strings returned from JavaScript helpers are treated as untrusted text and escaped by `html/template`. The `#ZgotmplZ` sentinel appears for unsafe URL values, including those returned by JSFunc. This is intentional — JavaScript helpers cannot produce trusted HTML types (`template.HTML`, `template.URL`) from JavaScript.

JavaScript callback validation catches two error paths: invalid function names and non-function values. Thrown JavaScript errors propagate as template rendering errors, which is the correct behavior — a helper that crashes should fail the render.

Runtime tests confirmed:

- `template.text().JSFunc("badge", (v) => `[[${String(v).toUpperCase()}]]`).Parse("{{ badge .Name }}").Render({ Name: "ada" })` returns `"[[ADA]]"`.
- `template.html().JSFunc("rawish", () => "<script>alert(1)</script>").Parse("<div>{{ rawish }}</div>").Render({})` escapes the output to `&lt;script&gt;alert(1)&lt;/script&gt;`.
- Invalid names like `"bad-name"` are rejected by validation.
- Thrown errors (`throw new Error("kaboom")`) appear as render errors.

**Failure mode: runtime capture on the builder.**

The first JSFunc implementation tried to convert Go template arguments back to JavaScript values through the callback value itself. A `goja.Value` does not expose a `Runtime()` method — the API does not support this pattern. The fix was to store the runtime on the builder (captured in `Loader`) and use `b.vm.ToValue(arg)` inside the wrapper. Without this, builders created in pure Go (without JavaScript) would panic when `JSFunc` tried to use a nil `vm`.

**Failure mode: test script variable collision.**

Two test scripts that both declared `const template = require("template")` in the same runtime caused:

```
SyntaxError: Identifier 'template' has already been declared at <eval>:1:1(0)
```

Wrapping each script in an IIFE `(() => { const template = require("template"); ... })()` scoped the declaration per evaluation and eliminated the collision.

---

## 6. Phase Three: xgoja Provider Wiring

The template module is not self-contained in the Go package sense. It requires two separate boundaries to be visible in the generated `goja-text` binary:

1. **Provider registration** — `pkg/xgoja/providers/text/text.go` must blank-import the `template` package so its `init()` runs, then look it up from the default registry and add it to the provider's module entries.

2. **Buildspec module selection** — `cmd/goja-text/xgoja.yaml` must list the `template` module under `modules:` so JavaScript can `require("template")` in the generated command.

```yaml
packages:
  - id: goja-text
    import: github.com/go-go-golems/goja-text/pkg/xgoja/providers/text
    replace: ../..

modules:
  - package: goja-text
    name: template
    as: template
```

The provider code adds the template module alongside the existing markdown, sanitize, and extract modules:

```go
var textModuleNames = []string{
    "markdown",
    "sanitize",
    "extract",
    "template",
}
```

After updating both files, the xgoja buildspec must be regenerated:

```bash
cd goja-text/cmd/goja-text
GOTOOLCHAIN=go1.26.4 GOWORK=off go generate
GOTOOLCHAIN=go1.26.4 GOWORK=off go build -o ../../dist/goja-text .
```

The `GOTOOLCHAIN=go1.26.4` flag is necessary because the generated module's Go version is 1.26.4 while the local `go` command may report an older version. `GOWORK=off` disables workspace mode so the generated module resolves independently.

The dry-run output reports `modules=7` and `packages=3`, confirming the template module and its two new aliases (host fs and assets fs) are included.

**Failure mode: nested module toolchain mismatch.**

Without `GOWORK=off`, the workspace root's `go.mod` takes priority and the generated module cannot find its own packages:

```
main module (github.com/go-go-golems/goja-text) does not contain package github.com/go-go-golems/goja-text/cmd/goja-text
```

With `GOWORK=off` but without `GOTOOLCHAIN=go1.26.4`:

```
go: module ../.. requires go >= 1.26.4 (running go 1.26.1)
```

The combination of both flags resolves this.

---

## 7. Phase Four: Help Documentation

Each `goja-text` module has a pair of Glazed help pages: an API reference and a user guide. These are embedded Markdown files loaded by the provider's `doc` package and exposed through `goja-text help goja-text-<name>-<type>`.

For the template module, four help pages exist:

- `template-api-reference.md` — Exact JavaScript API surface for builders, config, template sets, render results, and `JSFunc`.
- `template-user-guide.md` — Guided introduction to the template module from scripts, including JSFunc examples and the difference between text and HTML mode.
- `template-writing-documentation.md` — Tutorial for generating documentation with templates, including embedded example commands and a troubleshooting table.

The Glazed help system loads all `*.md` files from the provider's doc directory via `embed.FS`. Adding a new markdown file to `pkg/xgoja/providers/text/doc/` is all that is needed for it to appear in the generated binary's help system.

The writing documentation page includes a troubleshooting table:

| Problem | Cause | Solution |
| --- | --- | --- |
| `map has no entry for key` | The `missingkey=error` policy found missing data | Add the field or choose `--missing-key default` |
| Named render fails | `--template-name` does not match a `{{ define }}` block | Run `inspect` and copy the exact name |
| HTML contains `#ZgotmplZ` | `html/template` rejected unsafe URL | Check URL fields, avoid `javascript:` |
| JSFunc returns `[object Promise]` | Helper returned a Promise | `JSFunc` is synchronous; resolve before render |
| Fields lowercase/uppercase | YAML keys vs Go exported field names | Match selectors to the actual data shape |

---

## 8. Phase Five: JavaScript Verbs

The `jsverbs` directory contains JavaScript files that expose `__verb__("name", { metadata })` calls. The xgoja build scans each file for top-level functions and `__verb__` annotations, then registers them as CLI commands in the generated binary.

The template jsverbs file (`cmd/goja-text/jsverbs/template.js`) defines:

- `template text` — Render a `text/template` from a template file and YAML/JSON data.
- `template html` — Render an `html/template` with contextual escaping.
- `template inspect` — List named templates defined by a template file.
- `template check` — Validate template options and parse without rendering.
- `template helper-demo` — Demonstrate a JSFunc helper call.

These commands accept the same builder options as the JavaScript API: `--funcs`, `--missing-key`, `--left-delim`, `--right-delim`, `--template-name`, and `--output-path`.

**Critical lesson: helper functions become commands.**

The first jsverb draft defined helper functions like `readFile`, `parseDataFile`, `configureBuilder`, and `writeMaybe` as top-level function declarations:

```javascript
function readFile(file) { return fs.readFileSync(file, "utf-8"); }
function configureBuilder(builder, options) { ... }
```

The jsverb scanner treats these as commands because it scans for all top-level `function_declaration` and `variable_declarator` nodes. The generated `template --help` showed unwanted commands: `read-file`, `configure-builder`, `parse-data-file`, `write-maybe`.

The fix was to move these into a single top-level `helpers` object:

```javascript
const helpers = {
    readFile(file) { return fs.readFileSync(file, "utf-8"); },
    configureBuilder(builder, options) { ... },
};
```

Methods inside an object are not scanned as standalone commands. Only functions with `__verb__()` annotations become visible CLI commands.

---

## 9. Phase Six: Embedded Template Assets

The final implementation step added reusable template examples as embedded xgoja assets. These are read-only template/data pairs bundled into the generated binary, mounted at `/templates` through a separate `fs:assets` module alias.

The asset structure lives in `cmd/goja-text/template-assets/`:

```
template-assets/
    report.tmpl.md        + report.yaml
    api-reference.tmpl.md + api-reference.yaml
    page.tmpl.html        + page.yaml
```

Each pair demonstrates a different rendering pattern:
- `report`: Markdown status report with `{{ range }}` and `{{ toYaml }}`.
- `api-reference`: Markdown API table generated from structured data.
- `page`: HTML page demonstrating `html/template` escaping and `#ZgotmplZ` URL filtering.

The xgoja buildspec adds two entries:

```yaml
assets:
  - id: goja-text-template-assets
    path: ./template-assets
    embed: true

modules:
  - package: go-go-goja-host
    name: fs
    as: fs:assets
    config:
      embedded:
        allow: true
        mounts:
          - asset: goja-text-template-assets
            mount: /templates
```

The host `fs` module remains at `as: fs` for user-facing read/write operations. The new `fs:assets` alias is read-only and mounted at a fixed path. JavaScript scripts can access bundled examples via:

```javascript
const assets = require("fs:assets");
const template = require("template");

const tmpl = assets.readFileSync("/templates/report.tmpl.md", "utf-8");
const data = require("yaml").parse(assets.readFileSync("/templates/report.yaml", "utf-8"));
console.log(template.renderText(tmpl, data).Text);
```

A `template example` jsverb command provides CLI access to these bundled examples:

```bash
./dist/goja-text template examples          # list all embedded examples
./dist/goja-text template example report    # render the Markdown report
./dist/goja-text template example page      # render the HTML page
```

---

## 10. Architecture Overview

The complete architecture connects these components:

```
┌─────────────────────────────────────────────────────┐
│                  JavaScript Script                   │
│  const template = require("template");              │
│  template.text().Parse(src).Render(data)            │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              goja-text module layer                  │
│  Loader() → exports SetExport()                     │
│  TemplateBuilder, TemplateSet, RenderResult          │
│  JSFunc(name, fn) → closure wrapper                 │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              Go service layer                        │
│  TemplateConfig (validation, freeze)                 │
│  TemplateSet (text or html template pointer)         │
│  funcMapFor(mode, presets) → Sprig + Glazed merge    │
│  RenderTemplate(name, data) → buffer + execute       │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────┬───────────────────────────────┐
│  text/template       │  html/template               │
│  (plain text)        │  (contextual escaping)       │
└─────────────────────┴───────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  fs:assets module (read-only)                        │
│  /templates/*.tmpl.md, /templates/*.yaml             │
│  → bundled in xgoja_embed/assets/                    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  xgoja provider & buildspec                          │
│  template module registered + exported in yaml       │
│  embedded assets configured as read-only mount       │
└─────────────────────────────────────────────────────┘
```

---

## 11. What Was Tricky

**The Go-backed object pattern requires documentation.** JavaScript developers expect camelCase methods and plain objects. The Go-backed API uses PascalCase exported Go method names because the reflection layer exposes Go's export rules. This is consistent across all `goja-text` modules, but it is easy to miss in a short introduction. The TypeScript declarations serve as the bridge — they describe the JavaScript-facing API in terms that match what goja actually exposes.

**JSFunc breaks the pure service boundary.** Before implementing JSFunc, the template service layer had zero goja imports. After, the `TemplateBuilder` carries a `*goja.Runtime` field. This means pure Go consumers of the service layer don't need goja, but the module layer does. The design decision was worth it — the runtime pointer is nil when used from pure Go, and JSFunc validation explicitly rejects it. The compromise is visible but bounded.

**The xgoja build requires two toolchain flags.** `GOWORK=off` prevents the workspace from hijacking the generated module. `GOTOOLCHAIN=go1.26.4` ensures the Go version matches the root module requirement. Both are necessary and non-obvious from the project README.

**Helper function visibility in jsverbs.** The scanner scans all top-level functions, not only those with `__verb__()` annotations. Moving helpers into an object is the only reliable way to keep them private. The existing `markdown.js` and `sanitize.js` files have the same issue (e.g., `markdown read-file` appears as a command) but have not been cleaned up.

---

## 12. Open Questions and Near-Term Next Steps

- **Helper command cleanup.** The jsverb scanner exposes private helper functions as CLI commands across all modules. A future pass could refactor `markdown.js` and `sanitize.js` to use the object-method pattern for helpers.

- **Asynchronous JSFunc.** The current implementation is strictly synchronous. Promise-returning helpers would require either detecting them at registration time (reject with a clear error) or implementing async template execution, which changes the entire rendering contract.

- **Trusted types from JSFunc.** In HTML mode, JavaScript helpers cannot produce `template.HTML`, `template.URL`, or other trusted types because there is no way to create these Go types from JavaScript. If trusted output is needed, a Go-side helper registered through `JSFunc`'s future Go counterpart could produce them.

- **More embedded example templates.** The current three examples cover a report, an API table, and an HTML page. Domain-specific examples (release notes, prompt packs, configuration scaffolds) would make the embedded assets more broadly useful.

- **A `template copy-example` command.** Users might want to copy a bundled template to a host directory for customization before rendering. A command to do this would complete the embedded examples workflow.

---

## 13. What to Read Next

- `pkg/template/types.go` — Domain types and constants
- `pkg/template/builder.go` — Fluent builder and validation
- `pkg/template/render.go` — TemplateSet, parsing, and execution
- `pkg/template/module.go` — NativeModule adapter and JSFunc
- `pkg/template/funcs.go` — Function set selection and merge
- `cmd/goja-text/xgoja.yaml` — Module selection and asset configuration
- `cmd/goja-text/jsverbs/template.js` — CLI command registration
- `cmd/goja-text/template-assets/` — Embedded example files

---

> This report documents work completed in a single session on 2026-06-07, tracked through docmgr ticket `GOJA-TEXT-004`, with a detailed investigation diary and five implementation checkpoints. The codebase is clean, all tests pass, and the generated binary works correctly.
