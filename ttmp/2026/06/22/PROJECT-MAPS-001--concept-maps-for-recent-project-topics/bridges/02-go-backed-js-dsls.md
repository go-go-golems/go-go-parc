---
Title: Bridge 2 — Go-Backed JavaScript DSLs
Ticket: PROJECT-MAPS-001
Status: active
Topics:
    - research
    - projects
    - concept-maps
    - goja
    - xgoja
    - dsl
    - javascript
    - go
DocType: bridge-report
Intent: long-term
Owners: []
RelatedFiles:
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/05-bridge-topic-reports-plan.md
      Note: Bridge topic plan that assigned this report (Bridge 2)
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/04-refined-topic-concept-maps-v2.md
      Note: Refined concept maps that revealed this bridge spanning T1, T2, T5, T6, T7
    - Path: Projects/2026/06/22/ARTICLE - Designing DSLs with go-go-goja - Go-Backed JavaScript APIs.md
      Note: Canonical cross-project DSL design synthesis; the ownership maxim
ExternalSources: []
Summary: Textbook-style report on the Go-backed JavaScript DSL pattern: JavaScript owns composition, Go owns domain state, invariants, lifecycle, and typed values. Covers API-shape selection, concrete DSL instances, the wrapper-first pattern, failure modes, and a learning path.
LastUpdated: 2026-06-22T23:59:00-04:00
WhatFor: Understand the recurring design contract behind goja-bleve, Geppetto, Widget IR, Loupedeck, CSS Visual Diff, goja-text, protobuf builders, and auth route planners before designing a new DSL.
WhenToUse: Before authoring a new Go-backed JavaScript DSL, or before reviewing whether an existing one has drifted toward plain-object domain state.
---

# Bridge 2 — Go-Backed JavaScript DSLs

A Go-backed JavaScript DSL is an authoring surface where the syntax the user writes is JavaScript, but the semantics that matter live in Go. The pattern repeats across at least eight concrete systems in this project family: `goja-bleve`, Geppetto's wrapper-first agent API, the Widget IR pipeline, the Loupedeck device runtime, the CSS Visual Diff workflow engine, the `goja-text` template and Markdown builders, generated protobuf builders, and the Express auth route planner. This report explains the one design question that all of them answer, why the answer is what it is, how to choose between the API shapes that follow from it, and how the pattern fails when the boundary is drawn badly.

The reader should finish this chapter able to look at any `require("...")` module in the `go-go-goja` ecosystem and answer two questions: what does JavaScript own here, and what does Go own? When those two questions have a clear answer, the DSL is healthy. When they do not, the failure modes documented at the end of this chapter are already present.

## The central design question

Before writing a module loader, decide what the JavaScript author is allowed to own. This single decision determines the rest of the API.

The canonical answer, stated in the synthesis article `Projects/2026/06/22/ARTICLE - Designing DSLs with go-go-goja - Go-Backed JavaScript APIs.md`, is:

> Go owns lifecycle, domain state, validation, host resources, and typed boundaries. JavaScript owns policy, composition, recipes, and presentation assembly.

This is not a stylistic preference. It is the answer that falls out of asking what would break if JavaScript owned more. A plain JavaScript object is convenient to construct:

```javascript
const doc = markdown.document(source, {
  frontmatter: { format: "yaml", repair: true, optional: true },
  blocks: [
    { name: "context-window", fence: "context-window", json: true, strip: true }
  ]
});
```

That object is readable. It also moves the domain model into a loose structure that Go can only inspect after the fact. Misspelled keys, contradictory options, missing required fields, and invalid nested shapes all become runtime decoding problems discovered late. Every caller can construct slightly different shapes, and the API begins to depend on examples rather than on an explicit object model.

The same capability as a Go-backed fluent API is more verbose, but it gives Go a place to hold state and enforce invariants while the user is still composing:

```javascript
const doc = markdown.document(source)
  .Frontmatter()
    .YAML()
    .Repair()
    .Optional()
    .End()
  .Blocks()
    .Block("context-window")
      .FromFence("context-window")
      .JSON().Repair().Optional().End()
      .StripFromBody()
      .End()
    .End()
  .Build();
```

The second form has named intermediate objects: `DocumentBuilder`, `FrontmatterBuilder`, `BlockSetBuilder`, `BlockRuleBuilder`, and `JSONBlockBuilder`. Each object has a small responsibility and a narrow set of legal transitions. The builder can reject duplicate block names, unsupported formats, impossible parse policies, and missing required blocks. JavaScript still reads like a workflow, but Go owns the shape of that workflow.

The rule is not "always build fluent APIs." The rule is: **when intermediate state has invariants, keep that state in Go**. If the capability is a stateless conversion such as `yaml.parse(text)`, a flat function is better. If the capability is a stable query contract, a data recipe may be better. Fluent builders are appropriate when they encode a real construction process.

## Why the ownership split exists

The split exists because JavaScript objects are easy to create and hard to govern. Go structs are harder to write and easy to govern. A DSL is the meeting point: JavaScript gives the user a compact language for expressing intent; Go gives the host a place to enforce the rules that make that intent safe.

Consider what would happen if Geppetto's inference settings were plain JavaScript maps. A script could write:

```javascript
const settings = {
  provider: "openai",
  model: "gpt-4",
  apiKey: process.env.OPENAI_API_KEY,
  temperature: 0.7,
  maxTokens: 4096
};
```

That object looks reasonable. It is also wrong in at least three ways. First, the API key should not be constructible from a JavaScript string; it should be resolved from a registry profile so that secrets never become JavaScript-visible values that can be logged, serialized, or accidentally returned from `toJSON()`. Second, the `model` field should not be a free string; it should be resolved from a profile that the Go host has validated, so that the script cannot select a model the host has not authorized. Third, `temperature` and `maxTokens` should be validated against the provider's actual constraints, not accepted as loose numbers.

The Geppetto wrapper-first cutover (`Projects/2026/06/01/ARTICLE - Geppetto JS Bindings - Wrapper First Hard Cutover.md`) removed the old permissive namespaces (`profiles`, `runner`, `turns`, `engines`, `schemas`, `middlewares`, `tools`) and replaced them with a small set of Go-backed builders: `inferenceProfiles`, `engine`, `agent`, `turn`, `tool`, `toolRegistry`, `schema`, `events`. The removed `gp.inferenceSettings()` constructor is the most important absence. Scripts cannot mutate provider, model, sampling, token, base URL, model metadata, or credential configuration through JavaScript setters. Those settings are selected by resolving a registry profile, and the resolved result is a Go-owned `InferenceSettings` wrapper that can be inspected only in redacted form.

The pattern is the same in every DSL in this family. The question "what does Go own?" has the same shape of answer: the things that have invariants, the things that carry credentials or resources, the things that cross process boundaries as typed values, and the things whose lifecycle outlives a single JavaScript expression.

## Choosing the right API shape

A common mistake is to start from a syntax the author likes. The better starting point is to classify the capability. The following table, drawn from the DSL synthesis article, is the practical decision guide.

| Capability shape | Use this JavaScript surface | Go owns | Concrete instance |
| --- | --- | --- | --- |
| Stateless conversion | Flat function | Parsing and error conversion | `yaml.parse(text)` |
| Small namespace with modes | Namespaced functions | Mode-specific implementation | `sanitize.yaml.sanitize(text)` |
| Reusable parsed object | Builder returning a parsed set | Parse config and compiled state | `template.text().Parse(src)` in `goja-text` |
| Programmatic construction | Fluent builder over a Go document/tree | Blocks, validation, serialization | `markdown.builder().Table().End()` in `goja-text` |
| Source parsing with policies | Nested builder plus built result views | Extraction rules and typed accessors | `markdown.document(source).Frontmatter().Build()` |
| Stable data access | Query recipes and view helpers | Schema, SQL, row contracts | `mt.queries.turnBlockRows(opts)` in minitrace-viz |
| Host needs typed payloads | Generated protobuf builders | Concrete protobuf messages | `pb.Task.builder().title("...").build()` |
| UI/page authoring | IR helpers and recipes | Schema, registry, validation | `ui.panel(...)`, `rag.dataTable(...)` |

This table is a guide, not a law. The point is to keep the API proportional to the state it represents.

### When to use flat functions

Use flat functions when the operation is stateless and the parameters are already the domain. A YAML parser does not need a builder if all it does is parse one string with a small fixed option set. Flat functions are easy to document and test. Their weakness is that options grow badly. Once a function has five optional behaviors, nested data, validation modes, callbacks, and reusable internal state, the flat shape collapses under its own convenience.

### When to use fluent builders

Use a fluent builder when the user is constructing something with state. The object being constructed might be a template configuration, a Markdown document, a search mapping, a protobuf message, or an auth route plan. The builder exists because the final value is not meaningful until several choices have been made.

A good builder has four properties, as documented in the `goja-text` fluent builder article (`Projects/2026/06/07/ARTICLE - Fluent Builders with Go-Backed Objects for JavaScript.md`):

1. It stores intermediate state in Go.
2. It exposes methods that correspond to domain choices.
3. It has an explicit completion step such as `Build()`, `Parse()`, `Render()`, or `End()`.
4. It can explain invalid state with domain-specific errors.

The builder must not be a thin wrapper around a map. The anti-pattern is a generic `Set(name, value)` method that stores into an untyped bag. A real builder names the fields and transitions it cares about. The `MissingKey` method on the `goja-text` template builder does not store a string; it interprets a domain option and records a validation error at the point where the user made the mistake:

```go
func (b *TemplateBuilder) MissingKey(policy string) *TemplateBuilder {
    switch policy {
    case "default", "zero", "error", "invalid":
        b.cfg.MissingKey = policy
    default:
        b.errors = append(b.errors, fmt.Sprintf("unknown missing-key policy %q", policy))
    }
    return b
}
```

### When to use data recipes instead of builders

Do not use builders when the real reusable asset is a stable data contract. This was one of the strongest lessons from the minitrace-viz redesign. If a capability can be expressed as normalized rows, a query recipe, and a small view helper, that may be better than a deep fluent object tree.

Compare these two approaches:

```javascript
const report = mt.archiveFile(path)
  .report()
  .preset("full")
  .includeTools(true)
  .includeFiles(true)
  .build();
```

```javascript
const rows = db.query(mt.queries.turnBlockRows({ sessionId }).sql);
const frames = mt.views.groupTurnFrames(rows);
```

The builder reads nicely, but it can become an opaque wrapper around many hidden decisions. The query recipe exposes a stable contract: rows with named fields. JavaScript can group, filter, and present those rows. Go still owns the schema and query construction. The rule is: **use builders for constructing domain objects; use data contracts for transporting facts**.

## Concrete DSL instances

The pattern is not theoretical. Eight concrete systems in this project family implement it, each with a different domain and a different final value type. The table below maps each instance to its API shape and the thing Go owns.

| DSL | Module | API shape | Go owns | Primary article |
| --- | --- | --- | --- | --- |
| `goja-bleve` | `require("bleve")` | Fluent builders with hidden refs | Mappings, queries, indexes, batches, search requests; FAISS/CGO lifecycle | `Projects/2026/06/03/ARTICLE - Goja Bleve - Native Search Bindings for JavaScript RAG Pipelines.md` |
| Geppetto wrapper-first | `require("geppetto")` | Wrapper-first builders; hidden `__geppetto_ref` | Inference settings, engine profile registries, agent sessions, turns, tool registries, credentials | `Projects/2026/06/01/ARTICLE - Geppetto JS Bindings - Wrapper First Hard Cutover.md` |
| Widget IR | `require("widget.dsl")`, `require("rag.dsl")` | IR helpers and recipes | Schema, registry, validation, HTTP transport; React is sole renderer | `Projects/2026/06/05/ARTICLE - Building a Goja UI DSL from Scratch - Widget IR to xgoja.md` |
| Loupedeck JS API | `require("host")`, `require("ui")`, `require("anim")` | Owner-thread reactive runtime; retained UI | Rendering, pacing, serial/WebSocket transport safety; hardware writer | `Projects/2026/04/11/ARTICLE - Loupedeck - Goja JavaScript Runtime and API Deep Dive.md` |
| CSS Visual Diff | `require("css-visual-diff")` | Flat functions + workflow engine | Browser automation, artifact writing, service runtime types | `Projects/2026/04/29/ARTICLE - CSS Visual Diff - Retiring the Native YAML Runner for a JavaScript First Workflow Engine.md` |
| `goja-text` | `require("template")`, `require("markdown")` | Fluent builders over Go document trees | Template config, parsed template sets, Markdown document tree, escaping | `Projects/2026/06/07/PROJ - goja-text - Template and HTML Rendering Module.md` |
| Protobuf builders | `require("examples.xgoja.protobuf.v1")` | Generated fluent builders | Concrete `proto.Message` values; clone-on-boundary; descriptor validation | `Projects/2026/06/12/ARTICLE - go-go-goja Protobuf Builders - Goja Native Fluent Proto Construction.md` |
| Express auth route planner | `require("express")` | Staged planned-route builders | `RoutePlan` security contract; enforcer pipeline; SQL stores | `Projects/2026/06/12/ARTICLE - go-go-goja Express Auth - Go Backed Fluent Route Plans.md` |

### goja-bleve: search objects as hidden refs

`goja-bleve` exposes Bleve as `require("bleve")` for RAG scripts. The public API is fluent JavaScript, but the real state — mappings, queries, indexes, batches, search requests — lives in Go-backed refs attached to wrapper objects through a non-enumerable `__bleve_ref` property. JavaScript cannot forge a mapping, query, or index by assembling a compatible-looking object. If a method expects a field mapping, it unwraps a `fieldMappingRef`. If the caller passes a query or a plain object, the API returns a type-specific error instead of attempting to interpret the object dynamically.

```javascript
const bleve = require("bleve");

const text = bleve.field().text().store(true).build();
const doc = bleve.docMapping().dynamic(false).field("text", text).build();
const mapping = bleve.mapping().defaultMapping(doc).build();
const idx = bleve.memory().mapping(mapping).build();

idx.index("chunk-1", { text: "privacy preserving retrieval" });

const req = bleve.search()
  .query(bleve.match("privacy").field("text"))
  .fields(["text"])
  .build();

const result = idx.search(req);
idx.close();
```

Every value in that sequence is a wrapper around a Go object until the final `result`. The final result is converted to plain JavaScript-friendly data because callers need to inspect it, serialize it, and feed it into downstream reporting. Vector search is build-tag-aware: normal builds compile without FAISS, while `-tags=vectors` builds expose Bleve KNN through FAISS-backed vector indexes.

### Geppetto: wrapper-first when credentials and sessions matter

Geppetto is the strongest case for wrapper-first design because the domain includes credentials, provider configuration, and session state. The hard cutover removed legacy permissive namespaces and replaced them with Go-backed builders. The hidden reference mechanism is the same technical trick as `goja-bleve` — a non-enumerable, non-writable, non-configurable property — but the stakes are higher because the hidden ref carries inference settings, agent sessions, and tool registries that must not be reconstructible from JavaScript.

```javascript
const gp = require("geppetto");

const registry = gp.inferenceProfiles.load("./profiles.yaml");
const settings = registry.resolve("assistant");

console.log(settings.toJSON()); // redacted snapshot
registry.close();
```

The `InferenceSettings` wrapper exposes three methods: `toJSON()` (redacted), `clone()` (new wrapper around cloned Go settings), and `debug()` (redacted debug object plus provenance). The implementation clones on construction and clones again when JavaScript passes settings into another builder. JavaScript receives snapshots and wrapper methods, not ownership of the Go settings struct. The absence of `gp.inferenceSettings()` is the most important design decision: scripts cannot build provider/model settings directly.

### Widget IR: Goja authors data, React renders

The Widget IR DSL has a different final value. It does not produce an opaque Go object that the host recovers. It produces a JSON-compatible tree that a React renderer consumes. The central invariant, stated in `Projects/2026/06/05/ARTICLE - Building a Goja UI DSL from Scratch - Widget IR to xgoja.md`, is: **Goja authors data; React renders UI**.

```javascript
const ui = require("ui.dsl");
const data = require("data.dsl");

exports.page = ui.page("sessions", {
  root: ui.stack([
    ui.panel({ title: "Sessions" }, [
      data.dataTable({ rows, columns })
    ])
  ])
});
```

The output is a `WidgetNode` tree with three node kinds: `TextNode`, `ElementNode`, and `ComponentNode`. The `component` node is the important one: `type: "Panel"` is not an instruction to emit a `<div>`; it is an instruction for `WidgetRenderer` to call the React `Panel` component with serialized props and children. Go still owns helper registration, schema validation, and provider wiring; JavaScript owns page composition. Recipes expand to ordinary IR — the renderer should not care whether a node came from a recipe, a direct helper, or generated JSON.

### Loupedeck: JavaScript owns UI description, Go owns transport

The Loupedeck JS runtime is a device-control DSL where the ownership split is enforced by the physics of serial transport. JavaScript never pushes a framebuffer directly. Scripts mutate signals and retained tile state. Go owns rendering, pacing, and serial/WebSocket safety. The runtime is five stacked layers: an owned goja runtime that serializes all JS callbacks onto one owner thread, a pure-Go reactive state runtime, a pure-Go retained UI model for named pages and tiles, a pure-Go host runtime for buttons/knobs/touch/animation, and a live runner that flushes retained UI through the existing Go renderer/writer/transport stack to real hardware.

The most important architectural rule, stated in `Projects/2026/04/11/ARTICLE - Loupedeck - Goja JavaScript Runtime and API Deep Dive.md`, is that JavaScript does not own transport. Scripts define pages, tiles, signals, and animations. Those abstractions are realized by Go code, which then flushes the resulting dirty tiles through the transport-safe frontend. This is why the JS runtime can exist without undoing the backpressure and writer work that preceded it.

### CSS Visual Diff: retiring a native YAML runner for a JavaScript-first engine

The CSS Visual Diff refactor is a case study in what happens when a native config schema grows past its useful size. The tool used to have two orchestration models: a native Go YAML runner and a JavaScript/Goja scripting layer. The refactor removed the native runner, deleted the old config package and config-driven modes, and kept the tool focused on direct commands plus `css-visual-diff verbs`.

The lesson, stated in `Projects/2026/04/29/ARTICLE - CSS Visual Diff - Retiring the Native YAML Runner for a JavaScript First Workflow Engine.md`, is the distinction between schema-as-data and schema-as-API. YAML remains useful as data. Project-specific specs are still loaded and interpreted. The difference is that those specs now belong to userland JavaScript. The `css-visual-diff` core no longer promises to understand a universal visual-diff manifest schema. New features enter through service/runtime types and the JavaScript API, not through native manifest schemas. This keeps the core small while letting projects compose arbitrarily complex workflows.

### goja-text: fluent builders over Go document trees

`goja-text` is the canonical small-DSL example. It has two modules that follow the same three-layer architecture: a service layer (pure Go, zero goja imports, testable independently), a native module adapter (Loader, SetExport, goja conversion), and provider wiring (xgoja buildspec and embedded assets).

The template module exposes `template.text()` and `template.html()` as builder factories that return a `TemplateBuilder` — a Go struct with fluent methods. The markdown module exposes `markdown.builder()` which returns a `MarkdownBuilder` that appends typed blocks. Tables are first-class child builders because they have their own invariants: `Table()` returns a `TableBuilder`, and `End()` returns the parent `MarkdownBuilder`. The child builder lifecycle is the most error-prone part of the API, and the implementation guards against double `End()` with a `closed` flag.

The design decision worth noting is that JavaScript helpers in HTML mode cannot produce trusted HTML types like `template.HTML` or `template.URL` because there is no way to create these Go types from JavaScript. Ordinary strings returned from JavaScript helpers remain untrusted and are escaped by `html/template`. JavaScript code running in a `goja-text` script is untrusted input, not a trusted library.

### Protobuf builders: generated fluent construction for typed payloads

The protobuf builder system in `go-go-goja` is the generated-builder case. The trigger was planning Goja bindings for `sessionstream`, which is protobuf-first: commands, backend events, UI events, and timeline entities are concrete protobuf messages. A direct binding could accept plain objects and convert them through protojson, but that makes plain JavaScript objects the primary construction representation.

The better representation constructs the protobuf message directly inside the Goja runtime:

```javascript
const pb = require("examples.xgoja.protobuf.v1");

const task = pb.Task.builder()
  .id("task-1")
  .title("Ship protobuf builders")
  .addTags("xgoja")
  .putLabels("component", "provider")
  .priority(pb.TaskPriority.TASK_PRIORITY_HIGH)
  .build();
```

The resulting value is not JSON. Go can recover a concrete protobuf message from the Goja value via `protogoja.MessageFromValue(value)`. The runtime contract is clone-on-boundary: `NewMessageRef` clones the input message before storing it, and `Message()` clones again before returning a message to a caller. A value returned from `.build()` behaves as a stable built value. If the builder later mutates its internal state, the previously built value does not change. Generated builders are appropriate when a schema already exists and the host needs concrete typed objects.

### Express auth route planner: Go owns the security contract

The Express auth work is the case where Go ownership is not a convenience but a security requirement. Before the work, `app.get(path, handler)` accepted a raw JavaScript handler with no host-owned authentication boundary. The hard cutover replaced that with staged planned-route builders:

```javascript
app.patch("/orgs/:orgId/projects/:projectId")
  .auth(express.user().required())
  .resource(
    express.resource("project")
      .idFromParam("projectId")
      .tenantFromParam("orgId")
      .mustExist()
  )
  .csrf()
  .allow("project.update")
  .audit("project.updated")
  .handle((ctx, res) => {
    const project = ctx.resource("project")
    res.json({ updated: project.id, tenant: project.tenantId })
  })
```

JavaScript declares route intent through staged Go-backed builders. Go owns the `RoutePlan`, validates it at registration time, and enforces the security pipeline in `pkg/gojahttp.Host` before JavaScript handlers run. The implementation deliberately avoids accepting arbitrary JavaScript objects as security declarations. A dynamic object like `{ required: true }` is easy to write but hard to trust: Go would have to parse and validate object shape, defaults, nested fields, unknown keys, and conflicting options. Instead, `express.user()` and `express.resource(type)` return Go-backed JavaScript objects, and the builder accepts only those trusted objects. The old `app.get(path, handler)` form was intentionally removed — keeping it beside the new planned-route API would make it too easy for applications to accidentally create unauthenticated routes that look visually similar to secured routes.

## The wrapper-first pattern

The wrapper-first pattern is the implementation strategy that makes the ownership split enforceable rather than conventional. It appears in `goja-bleve`, Geppetto, the protobuf builders, and the Express auth route planner. The mechanics are the same in each case: a JavaScript object carries a hidden Go reference, public methods re-enter Go to retrieve the typed reference, and plain JavaScript objects cannot substitute for wrapper objects because the hidden reference is non-enumerable, non-writable, and non-configurable.

The attachment code is small and nearly identical across `goja-bleve` and Geppetto:

```go
func (m *moduleRuntime) attachRef(o *goja.Object, ref any) {
    _ = o.Set(hiddenRefKey, ref)
    _ = o.DefineDataProperty(hiddenRefKey, o.Get(hiddenRefKey),
        goja.FLAG_FALSE, // writable
        goja.FLAG_FALSE, // enumerable
        goja.FLAG_FALSE, // configurable
    )
}
```

The key point is not that there is a hidden property. The key point is that public methods re-enter Go, retrieve the typed reference, clone or validate it, and then operate on Go data. This prevents plain JavaScript objects from becoming accidental substitute implementations. A typed extraction helper enforces the boundary:

```go
func getTypedRef[T any](m *moduleRuntime, v goja.Value, expected string) (*T, error) {
    ref := m.getRef(v)
    if ref == nil {
        return nil, fmt.Errorf("expected %s wrapper, got value without Go reference", expected)
    }
    typed, ok := ref.(*T)
    if !ok {
        return nil, fmt.Errorf("expected %s wrapper, got %T", expected, ref)
    }
    return typed, nil
}
```

### When wrapper-first is mandatory

Wrapper-first is mandatory when the domain includes any of the following:

- **Credentials** — API keys, OAuth tokens, service account keys. These must never become JavaScript-visible values that can be logged, serialized, or returned from `toJSON()`. Geppetto redacts secrets before any snapshot reaches JavaScript.
- **Sessions and typed state** — agent sessions, durable object identities, inference profile registries. These have lifecycle that outlives a single JavaScript expression and must not be reconstructible from loose maps.
- **Host resources** — file handles, database connections, network sockets, index handles. These have cleanup semantics that JavaScript's garbage collector does not understand.
- **Typed boundary values** — protobuf messages that Go handlers must recover without JSON round trips, `http.Handler` references that compose across modules, Bleve search requests whose KNN clauses must be validated against the index mapping.

### When wrapper-first is overkill

Wrapper-first is overkill when the capability is a stateless conversion or a stable data contract. `yaml.parse(text)` does not need a hidden Go reference. A query recipe that returns named rows does not need a wrapper around each row. The minitrace-viz redesign explicitly chose data recipes over builders for its query layer because the reusable asset was a stable row contract, not a construction process. Forcing a builder onto a data contract hides data policy behind an opaque chain and makes the output harder to inspect.

## Failure modes

Every DSL in this family was shaped by concrete failures. The failure modes are first-class design drivers, not footnotes. Understanding them is the fastest way to understand why the ownership split is drawn where it is.

### Plain-object domain state drift

This is the foundational failure. JavaScript owns too much state, and the domain model becomes a pile of maps. The symptoms are vague errors that arrive late:

```text
cannot convert undefined to string
```

instead of:

```text
markdown.table: row 3 has 2 cells, expected 4 columns
```

The CSS Visual Diff refactor documents this failure at the schema level. The native YAML runner let business logic grow around a file format rather than around runtime concepts. Once a `config.Config` type sits at the center, every mode tends to depend on it. The config schema becomes the API. If a later JavaScript workflow wants the same functionality, it either has to manufacture a fake config object or the service code has to be refactored away from config types. The fix was to retire the native runner entirely and let JavaScript own workflow composition while Go owns service runtime types.

The prevention is the ownership maxim: if the model has invariants, name it in Go. If the model is just rows being transported, a data contract is fine.

### Hidden-ref lifecycle bugs

Hidden Go references carry lifecycle that JavaScript's garbage collector does not see. The `goja-bleve` shipping work (`Projects/2026/06/06/ARTICLE - Goja Bleve - Shipping a Vector RAG Runtime with xgoja.md`) documented three lifecycle bugs discovered during review:

- **Reopened index mapping**: when an index was reopened, the stored mapping was not loaded. The fix loads the stored mapping on reopen so the index is usable.
- **`.size(0)` default**: `SearchRequest.Size(0)` means "count only, no hits." The default was silently zero in some paths, returning empty results. The fix preserves `.size(0)` explicitly so the caller's intent is visible.
- **Batch execution timing**: a batch was marked executed before the underlying Bleve batch actually succeeded. If the Bleve call failed, the JavaScript-visible batch reported success. The fix marks the batch executed only after the underlying call succeeds.

The pattern across all three is the same: the hidden ref carries real state, and that state's transitions must be honest. A batch that reports success before the write commits is a lie that propagates downstream.

### Schema/buildspec/runtime drift

This failure appears when the same concept is represented in three places — a source schema, a generated buildspec, and a runtime representation — and they diverge. The xgoja RuntimePlan v2 hard cutover (`Projects/2026/06/13/ARTICLE - xgoja v2 RuntimePlan Hard Cutover - Technical Deep Dive.md`) is the canonical response. Old top-level keys (`packages`, `modules`, `commandProviders`, `jsverbs`, `help`, `assets`) are rejected during decode, not migrated. The design rule is: stale generated output fails immediately, rather than silently bridging into an incomplete representation.

The Widget IR pipeline documents the same failure at the component level. Adding a new component requires updating five surfaces: TypeScript IR types, React renderer, Goja DSL helpers, server schema, and stories/tests. Missing any surface produces visible failures. The prevention is to treat the manifest as the source of truth and generate contracts, registries, helper tables, docs, and coverage checks from it — while keeping semantic adaptation code handwritten.

### Options-map trap

The options-map trap is the convenient-but-weak variant of plain-object drift. An options map is attractive because it is quick to write and easy to extend. It becomes a trap when it holds domain state that deserves names and validation:

```javascript
// Convenient, but weak once the shape grows.
markdown.document(source, {
  frontmatter: true,
  repair: true,
  blocks: [{ name: "context-window", json: true }]
});
```

The fix is to introduce Go-backed builders or typed config objects with `Validate()` when the options interact. The `goja-text` template builder does not simply store a string for `MissingKey`; it interprets a domain option and records a validation error at the point where the user made the mistake.

### Builder-sprawl trap

The opposite failure is builder-sprawl: a builder invented for every view, even when the data is naturally rows, messages, or plain facts. The symptom is a long chain that hides too much data policy behind opaque decisions:

```javascript
// May hide too much data policy in a builder.
archive.report().preset("full").includeTools().includeFiles().build();

// Often better for reusable analysis.
const rows = db.query(queries.turns({ sessionId }).sql);
const view = views.groupTurns(rows);
```

The prevention is the data-contract rule: use builders for constructing domain objects; use data contracts for transporting facts.

### Invisible-runtime trap

Any callback or async API that ignores runtime ownership is wrong even if it works in small tests. Goja runtimes are single-threaded from JavaScript's point of view. Native modules must not call JavaScript functions, touch `goja.Value`, settle promises, or mutate JS objects from arbitrary goroutines. This is part of the DSL contract whenever callbacks or async work appear.

The Geppetto `runAsync` EventEmitter design documents this explicitly. Synchronous `run()` blocks live callbacks because the JS owner thread waits for inference. `runAsync(turn)` returns a promise handle; listeners attached at builder-level via `.events(emitter)` before run start. Run-scoped emitter refs are adopted and closed deterministically at settlement — garbage collection is not a lifecycle protocol. The `handle.on(...)` pattern was rejected as racy because early events are lost before listener registration.

### Compatibility-wrapper trap

Compatibility wrappers preserve old concepts. Sometimes that is necessary. Sometimes it blocks the new design from becoming clear. The Geppetto hard cutover removed legacy namespaces entirely rather than wrapping them. The xgoja RuntimePlan v2 cutover rejects legacy keys rather than migrating them. The CSS Visual Diff refactor deleted the native YAML runner rather than bridging it. The recurring discipline is: if a project explicitly allows a clean break, prefer deleting old broad modules over wrapping them indefinitely. Compatibility wrappers are not free; they preserve old concepts in the new design.

## A learning path for designing a new Go-backed DSL

The DSL synthesis article provides a design checklist and an implementation checklist. The condensed learning path, ordered by the point at which each decision matters, is:

**1. State the ownership split before writing code.** Write one sentence: "JavaScript owns X; Go owns Y." If you cannot write that sentence, you are not ready to implement. The Geppetto cutover's most important design decision was the absence of `gp.inferenceSettings()` — the thing JavaScript does not own is as important as the things it does.

**2. Classify the capability.** Use the decision table. Is this a stateless conversion (flat function), a reusable parsed object (builder returning a parsed set), programmatic construction (fluent builder), stable data access (query recipe), a typed payload (generated builder), or UI authoring (IR helpers)? The API shape should be proportional to the state it represents.

**3. Design the Go model first, testable without Goja.** If the service layer cannot be tested without a runtime, the module boundary is too tangled. The `goja-text` pattern is explicit: implement the core logic in a pure Go package with zero goja imports, test it with `go test`, then add the module adapter.

**4. Decide whether wrapper-first is needed.** If the domain includes credentials, sessions, typed state, host resources, or typed boundary values, use hidden Go references. If the domain is stateless or transports plain facts, flat functions or data recipes are better.

**5. Define the builder lifecycle.** Every builder needs a lifecycle: create → configure → validate → build/render/parse → use result. Nested builders need explicit commit points (`End()`) with deterministic double-call behavior. Choose strict or idempotent deliberately and test it.

**6. Make escape hatches explicit and searchable.** Name them `Raw()`, `rawWidget()`, `JSFunc()`. A reviewer should be able to search for risky boundaries. Do not hide escape hatches behind generic names like `Value`, `Any`, or `Custom`.

**7. Define the validation model.** Distinguish configuration validation (checks builder state before doing work) from execution validation (checks source or data while parsing/rendering). A builder should accumulate configuration errors and report them together, rather than failing on the first method call. Errors should carry domain context, not reflection or JSON decoding language.

**8. Document the data conversion rules.** For every nontrivial module, document whether JavaScript objects are accepted as input, whether Go-backed objects are accepted, whether returned values are Go-backed or plain JSON, how `undefined`/`null`/dates/arrays/maps/functions are handled, and whether property names are case-sensitive.

**9. Handle runtime ownership for callbacks and async work.** If the DSL stores callbacks, answer: who owns the callback lifetime, how is it released, which context cancels pending work, can the callback be invoked after runtime shutdown begins, are calls serialized through the owner, and what happens if the callback throws. If the design cannot answer these questions, defer callbacks.

**10. Ship TypeScript declarations, help docs, examples, and tests as part of the definition of done.** A DSL without TypeScript declarations is harder for humans and agents to use. Declarations force the API author to name the public contract. If the types are full of `any`, the API is too loose. Documentation drift is API drift — if a help page shows `markdown.builder().Table()`, there should be a smoke test that exercises that shape.

**11. For large DSLs, use manifests and codegen to prevent drift.** Separate three artifacts: the wire contract (serializable shapes), the authoring DSL (Goja helpers and recipes that produce the wire contract), and renderer adapters (handwritten code that adapts wire props to actual components). Generate contracts, registries, helper tables, docs, and coverage checks. Keep semantic adaptation code handwritten. A validation command should fail if two widgets declare the same type, two helpers collide, an adapter is missing, a stable widget lacks docs or stories, generated outputs are stale, or a DSL helper appears without a schema entry.

**12. Decide whether a clean break is allowed before adding compatibility wrappers.** If the project can tolerate it, delete old broad modules and update callers. Compatibility wrappers preserve old concepts in the new design and are not free.

## Key points

- A Go-backed JavaScript DSL is defined by the presence of a domain vocabulary and an ownership boundary, not by chaining. A flat function can be a DSL if it exposes a domain vocabulary; a long chain can fail to be a DSL if it hides an untyped map behind methods.
- Go owns lifecycle, domain state, validation, host resources, and typed boundaries. JavaScript owns policy, composition, recipes, and presentation assembly. This rule came out of real applications, not from syntax preference.
- The API shape should be proportional to the state it represents: flat functions for stateless conversions, builders for construction with invariants, data recipes for transporting facts, generated builders for typed payloads, IR helpers for authoring serializable trees.
- Wrapper-first is mandatory when the domain includes credentials, sessions, typed state, host resources, or typed boundary values. It is overkill for stateless conversions and stable data contracts.
- The wrapper-first mechanism — a non-enumerable, non-writable, non-configurable hidden Go reference — is the same across `goja-bleve`, Geppetto, the protobuf builders, and the Express auth route planner. The pattern is reusable.
- Failure modes are first-class design drivers. Plain-object domain state drift, hidden-ref lifecycle bugs, schema/buildspec/runtime drift, options-map traps, builder-sprawl traps, invisible-runtime traps, and compatibility-wrapper traps each shape the boundary in a specific way.
- The hard-cutover discipline — delete legacy paths once a typed substrate exists, do not wrap — recurs across Geppetto, xgoja RuntimePlan v2, CSS Visual Diff, and the Express auth route planner. Compatibility wrappers preserve old concepts in the new design.
- A DSL is successful when users can express domain work in JavaScript without inheriting the accidental complexity of the Go implementation, and when Go can still enforce the invariants that make the domain safe. If JavaScript owns too much, the DSL becomes a collection of unvalidated maps. If Go owns too much, the DSL becomes a rigid wrapper that cannot express application policy.

## Closing

Every DSL in this family is an instance of the same contract. The contract is worth restating because it is the thing that survives implementation details: JavaScript owns composition; Go owns domain state, validation, resources, lifecycle, and typed boundary values. The eight concrete instances differ in domain — search, inference, UI, hardware, visual diff, text, protobuf, auth — but not in contract. A reader who understands why Geppetto removed `gp.inferenceSettings()` understands why `goja-bleve` rejects plain objects as field mappings, why the Express auth planner rejects raw handlers, and why the Widget IR pipeline insists that Goja authors data while React renders.

The next bridge report, on the single-binary Go + SPA pattern, builds on this one. A Go-backed DSL that produces Widget IR is one half of a single-binary application; the React renderer that consumes that IR is the other. The boundary between them — JSON-compatible data, not executable code — is what makes the single binary safe to ship.
