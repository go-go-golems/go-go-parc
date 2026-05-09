---
title: CSS Visual Diff JavaScript API Design and Implementation Deep Dive
aliases:
  - CSSVD JavaScript API Deep Dive
  - css-visual-diff JS API implementation report
  - CollectedSelection and SelectionComparison API
tags:
  - article
  - textbook
  - css-visual-diff
  - javascript-api
  - visual-regression
  - goja
  - browser-automation
status: active
type: article
created: 2026-04-25
repo: /home/manuel/workspaces/2026-04-21/hair-v2/css-visual-diff
ticket: CSSVD-JSAPI-PIXEL-WORKFLOWS
branch: task/add-js-interpreter
---

# CSS Visual Diff JavaScript API Design and Implementation Deep Dive

This note explains the new `css-visual-diff` JavaScript API as an implementation story and as a design lesson. The goal is not only to record which files changed, but to make the architecture understandable enough that a future maintainer can extend it safely. The central idea is simple: a visual-diff script should be able to talk in JavaScript concepts — pages, locators, collected selections, comparisons, artifacts, and reports — while the expensive and fragile browser/image work remains in typed Go services.

> [!summary]
> - The new API is organized around two durable values: `CollectedSelection`, which is browser truth for one selector at one moment, and `SelectionComparison`, which compares two collected selections without re-querying the browser.
> - The implementation is service-first. Go owns collection, pixel diffing, selection comparison, artifact writing, and schema stability; Goja exposes these as Promise-first, Proxy-backed JavaScript handles.
> - The public JavaScript surface is intentionally canonical and opinionated: `cvd.compare.region(...)` is the low-effort path, while `locator.collect(...)` plus `cvd.compare.selections(...)` is the primitive path.
> - Built-in compare verbs now dogfood the public `require("css-visual-diff")` API instead of relying on private `require("diff")` / `require("report")` helper modules.

## 1. Why this API had to exist

Before this work, `css-visual-diff` already had real capabilities. It could drive Chromium, inspect selectors, capture screenshots, evaluate styles, create catalogs, run YAML workflows, and expose repository-scanned JavaScript verbs. The missing part was not raw browser automation. The missing part was a coherent JavaScript vocabulary for pixel-accurate visual feedback loops.

A downstream Pyxis workflow made the gap visible. Pyxis could reproduce a YAML page-section comparison using the built-in command:

```bash
css-visual-diff verbs script compare region ...
```

The measured JavaScript region diff matched the YAML diff closely:

```text
Archive content YAML diff:      7.1281%
Archive content JS region diff: 7.128146453089244%
```

That result proved the engine was capable. It also proved the public JavaScript API was not yet comfortable. A project script could orchestrate pages and inspect data, but the documented `require("css-visual-diff")` module did not expose the region comparison primitive that the built-in verb used internally. The API boundary was backwards: the command had the useful primitive, but scripts could not call it directly in a clean, documented way.

The first tempting fix would have been a narrow helper:

```js
await cvd.comparePixels({
  left: { page, selector },
  right: { page, selector },
})
```

That would have solved one immediate pain, but it would have shaped the whole API around the wrong object. A visual comparison is not just pixels. It is also bounds, text, computed styles, attributes, screenshot artifacts, markdown reports, JSON manifests, and human policy decisions. Calling the whole thing `comparePixels` would make the rich parts feel bolted on.

The implementation therefore chose a deeper model:

```js
const left = await leftPage.locator("#cta").collect({ inspect: "rich" })
const right = await rightPage.locator("#cta").collect({ inspect: "rich" })
const comparison = await cvd.compare.selections(left, right)
```

and a low-effort wrapper:

```js
const comparison = await cvd.compare.region({
  left: leftPage.locator("#cta"),
  right: rightPage.locator("#cta"),
  outDir: "artifacts/cta",
})
```

The distinction matters. The first form exposes the primitive concepts. The second form gives users a quick path. Both are honest about what the system is doing.

## 2. The core mental model

The new API has four main nouns. Once those nouns are clear, the implementation becomes much easier to read.

| Concept | What it means | Is it live? | Who owns it? |
|---|---|---:|---|
| `Page` | A Chromium page controlled by `css-visual-diff`. | Yes | Go service + JS wrapper |
| `Locator` | A page-bound selector handle, created by `page.locator(selector)`. | Yes | Goja Proxy handle |
| `CollectedSelection` | Immutable browser facts for one selector at one time. | No | Go service data + Goja Proxy handle |
| `SelectionComparison` | Deterministic comparison of two collected selections. | No | Go service data + Goja Proxy handle |

A locator is like a question: “Which element do you mean on this loaded page?” A collected selection is an answer: “At this moment, that selector existed, had these bounds, this text, these styles, these attributes, and maybe this screenshot.” A comparison is analysis over two answers. It should not ask the browser again.

That separation is the key design move. Browser state is dynamic. Pages mutate. Animations run. Fonts load. React hydrates. If a comparison repeatedly queries live browser state, the script becomes harder to reason about. By collecting once and comparing collected values, scripts get stable data that can be filtered, serialized, reported, and cataloged.

A useful pseudocode version of the architecture looks like this:

```text
browser.page(url)  -> Page handle
page.locator(sel)  -> Locator handle
locator.collect()  -> CollectedSelection handle over immutable data
compare.selections(left, right) -> SelectionComparison handle over immutable data
comparison.report / artifacts / toJSON -> outputs
```

The low-effort comparison API is just the same sequence packed into one operation:

```text
compare.region({ left, right })
  collect left locator
  collect right locator
  capture region screenshots
  compare collected selections
  write pixel diff artifacts
  return SelectionComparison handle
```

This shape is deliberately JavaScript-native. There is no workflow builder. Scripts use ordinary JavaScript functions, loops, conditionals, arrays, maps, and object returns. The API supplies strong primitive boundaries; JavaScript supplies orchestration.

## 3. Architecture at a glance

The implementation is split into three layers.

```mermaid
flowchart TD
    JS[Repository-scanned JS verb] --> API[require("css-visual-diff") JS API]
    API --> Proxy[Goja Proxy-backed handles]
    Proxy --> Services[internal/cssvisualdiff/service]
    Services --> Browser[Chromium / chromedp]
    Services --> Images[PNG / image diff primitives]
    Services --> Files[JSON, Markdown, PNG artifacts]

    subgraph Public_JS_Surface[Public JavaScript surface]
      API
      Proxy
    end

    subgraph Typed_Go_Core[Typed Go core]
      Services
      Browser
      Images
      Files
    end

    style API fill:#e8f2ff,stroke:#3572a5
    style Services fill:#ecffe8,stroke:#3a7d3a
    style Proxy fill:#fff4d6,stroke:#b7791f
```

The service layer is intentionally independent of Goja. It knows about pages, selectors, images, JSON-shaped data, and artifacts. It does not know about JavaScript promises or proxies. This makes it testable with ordinary Go tests.

The JS API layer is intentionally thin but strict. It decodes JavaScript options, unwraps Proxy handles, calls service functions, and wraps service data back into behavior-rich handles. It does not reimplement image diffing or DOM collection in JavaScript.

The built-in verbs sit above the JS API just like user scripts do. That is an important outcome of Phase 8. The built-ins are no longer special clients of private native helper modules for compare workflows. They prove that the public API is sufficient.

## 4. The implementation timeline

The work landed in a sequence of focused commits:

| Commit | Purpose |
|---|---|
| `b13933a` | Add collected selection service model. |
| `6ca2498` | Extract pixel diff service primitives. |
| `29c8aca` | Add selection comparison service. |
| `5c76cd7` | Expose collected selection and comparison handles in JS. |
| `88ddac5` | Add canonical `cvd.compare.region` workflow and built-in dogfooding. |
| `86a6947`, `f2830b7`, `c1dd80f`, `071a922`, `f656d15` | Record ticket docs, tasks, changelog, diary, and smoke scripts. |

The ordering matters. It would have been possible to start with the JavaScript binding and then fill in the Go services behind it. That would have produced a more fragile API because early JS shapes would have been guesses. Instead, each browser/image/data primitive was made real in Go first, tested, and only then wrapped in Goja.

## 5. Phase 1: collected selector data

The first implementation phase added:

```text
internal/cssvisualdiff/service/collection.go
internal/cssvisualdiff/service/collection_test.go
```

The core type is `CollectedSelectionData`, also aliased as `SelectionData`:

```go
const CollectedSelectionSchemaVersion = "cssvd.collectedSelection.v1"

type CollectedSelectionData struct {
    SchemaVersion  string                `json:"schemaVersion"`
    Name           string                `json:"name,omitempty"`
    URL            string                `json:"url,omitempty"`
    Selector       string                `json:"selector"`
    Source         string                `json:"source,omitempty"`
    Status         SelectorStatus        `json:"status"`
    Exists         bool                  `json:"exists"`
    Visible        bool                  `json:"visible"`
    Bounds         *Bounds               `json:"bounds,omitempty"`
    Text           string                `json:"text,omitempty"`
    HTML           string                `json:"html,omitempty"`
    ComputedStyles map[string]string     `json:"computedStyles,omitempty"`
    Attributes     map[string]string     `json:"attributes,omitempty"`
    Screenshot     *ScreenshotDescriptor `json:"screenshot,omitempty"`
}
```

The service entry point is:

```go
func CollectSelection(
    page *driver.Page,
    locator LocatorSpec,
    opts CollectOptions,
) (CollectedSelectionData, error)
```

This function is the line between live browser state and immutable data. It uses existing DOM primitives such as `LocatorStatus`, `LocatorText`, `LocatorBounds`, `LocatorComputedStyle`, and `LocatorAttributes`. It then returns one stable value.

### Collection profiles

The service supports three profiles:

| Profile | Intended use | What it collects |
|---|---|---|
| `minimal` | Cheap readiness checks and large batches. | Status, existence, visibility, bounds. |
| `rich` | Default script-facing comparison. | Text, common styles, common attributes, status, bounds. |
| `debug` | Deep diagnosis. | HTML, all computed styles, all attributes, text, status, bounds. |

This is the first place where the API favors the common user path. Rich collection is the default because collection is cheap relative to navigation, screenshot capture, image normalization, and pixel diffing. If the script already paid to load the page, it is usually better to collect enough browser facts once and filter them later in JavaScript.

The implementation also adds explicit typed errors:

```go
type CollectionErrorKind string

const (
    CollectionErrorInvalidSelector CollectionErrorKind = "invalidSelector"
    CollectionErrorBrowser         CollectionErrorKind = "browser"
    CollectionErrorArtifact        CollectionErrorKind = "artifact"
)
```

Invalid selectors are especially important. `LocatorStatus` can return a selector error inside a status payload. `CollectSelection` converts that into a `CollectionError` of kind `invalidSelector`, which later allows JS errors to become more helpful.

### Why collection is not comparison

A common mistake would be to let `locator.collect()` compare against another locator directly. That would make collection do too much. Collection should answer one question: what does the browser say about this selector now? Comparison should answer a different question: how do two collected answers differ?

Keeping those responsibilities separate allows this kind of JavaScript:

```js
const selected = await page.locator("#cta").collect({ inspect: "rich" })

if (!selected.summary().exists) {
  return { ok: false, reason: "missing cta" }
}

const typography = selected.styles(["font-size", "font-family", "line-height"])
return { ok: true, typography }
```

No comparison is needed here. Collection is useful on its own.

## 6. Phase 2: pixel diff service primitives

The second implementation phase moved image comparison out of mode-shaped code and into the service layer:

```text
internal/cssvisualdiff/service/pixel.go
internal/cssvisualdiff/service/pixel_test.go
```

The service result is deliberately lowerCamel because it is meant to lower cleanly into JavaScript:

```go
type PixelDiffResult struct {
    Threshold          int     `json:"threshold"`
    TotalPixels        int     `json:"totalPixels"`
    ChangedPixels      int     `json:"changedPixels"`
    ChangedPercent     float64 `json:"changedPercent"`
    NormalizedWidth    int     `json:"normalizedWidth"`
    NormalizedHeight   int     `json:"normalizedHeight"`
    DiffComparisonPath  string  `json:"diffComparisonPath,omitempty"`
    DiffOnlyPath        string  `json:"diffOnlyPath,omitempty"`
}
```

The main functions are:

```go
ReadPNG(path)
WritePNG(path, img)
PadToSameSize(a, b)
DiffImages(left, right, opts)
DiffPNGFiles(leftPath, rightPath, opts)
ComputePixelDiff(left, right, threshold)
CombineSideBySide(left, right, diff)
WritePixelDiffImages(leftPath, rightPath, comparisonPath, diffOnlyPath, opts)
```

The algorithm is straightforward and intentionally visible:

```text
read left PNG
read right PNG
convert both to NRGBA
pad both to the same width and height with white pixels
for every pixel:
  compute squared RGB distance
  if distance > threshold²:
    mark changed
    paint diff pixel red
write diff-only image
write side-by-side left/right/diff image
return counts and percentages
```

The threshold is an RGB distance threshold from `0` to `255`. A full black-to-white change still counts as changed at threshold `255`, because the squared distance across three channels exceeds `255²`. The tests document this behavior because it is a subtle point future maintainers could otherwise misread.

### Why image diffing belongs in `service`

Before this extraction, pixel helpers lived under `internal/cssvisualdiff/modes`. That was fine while only CLI modes needed them. It became limiting once JavaScript wanted to compare regions directly. If `cvd.image.diff(...)` and `cvd.compare.region(...)` both need image diffing, then image diffing is a service, not a mode implementation detail.

The old mode-local helper names remain as wrappers. This lets older mode tests keep validating behavior while the implementation now flows through service primitives.

## 7. Phase 3: comparing two selections

The third implementation phase added:

```text
internal/cssvisualdiff/service/selection_compare.go
internal/cssvisualdiff/service/selection_compare_test.go
```

The service entry point is:

```go
func CompareSelections(
    left SelectionData,
    right SelectionData,
    opts CompareSelectionOptions,
) (SelectionComparisonData, error)
```

The result has its own schema:

```go
const SelectionComparisonSchemaVersion = "cssvd.selectionComparison.v1"
```

and combines several kinds of evidence:

```go
type SelectionComparisonData struct {
    SchemaVersion string              `json:"schemaVersion"`
    Name          string              `json:"name,omitempty"`
    Left          SelectionSummary    `json:"left"`
    Right         SelectionSummary    `json:"right"`
    Pixel         *PixelDiffResult    `json:"pixel,omitempty"`
    Bounds        BoundsDiff          `json:"bounds"`
    Text          TextDiff            `json:"text"`
    Styles        []MapValueDiff      `json:"styles,omitempty"`
    Attributes    []MapValueDiff      `json:"attributes,omitempty"`
    Artifacts     []SelectionArtifact `json:"artifacts,omitempty"`
}
```

The most important rule is this: comparison does not query the browser. It only compares the data already present in `SelectionData`. That rule prevents a whole class of race conditions. If a page changes after collection, the comparison is unaffected.

### Deterministic map diffs

Styles and attributes are maps, and maps are unordered. Reports and tests, however, need stable ordering. The comparison service therefore computes a selected key set, applies include/exclude filters, sorts the keys, and emits changed values in order.

In pseudocode:

```text
selectedMapKeys(left, right, include, exclude):
  if include is non-empty:
    keys = include minus exclude
  else:
    keys = union(keys(left), keys(right)) minus exclude
  return sort(keys)

for key in selectedMapKeys(...):
  if left[key] != right[key]:
    append { name: key, left: left[key], right: right[key], changed: true }
```

This makes JavaScript output predictable:

```js
comparison.styles.diff().map(d => d.name)
// ["color", "font-size", "line-height"] — stable order
```

### Pixel integration

If both selections include screenshot descriptors, comparison delegates to the Phase 2 pixel service. If no artifact paths are provided, it can compute stats only. If artifact paths are provided, both `diffOnlyPath` and `diffComparisonPath` must be present. Partial artifact configuration is rejected because it creates ambiguous output.

This design lets later JavaScript choose between analysis-only and artifact-producing workflows.

## 8. Phases 4 and 5: Goja handles

The fourth and fifth phases exposed the service data to JavaScript:

```text
internal/cssvisualdiff/jsapi/collect.go
internal/cssvisualdiff/jsapi/compare.go
```

The public collection API is:

```js
const selected = await page.locator("#cta").collect({ inspect: "rich" })
const same = await cvd.collect.selection(page.locator("#cta"), { inspect: "minimal" })
```

The public comparison API is:

```js
const comparison = await cvd.compare.selections(left, right, {
  styleProps: ["font-size", "line-height", "color"],
  attributes: ["class"],
})
```

Both return Go-backed Proxy handles. The handles are behavior-rich, but they do not serialize accidentally. Scripts explicitly lower them:

```js
return selected.summary()
return selected.toJSON()
return comparison.summary()
return comparison.toJSON()
```

This explicit lowering is important. A Proxy handle is an interactive object with methods and controlled property access. It is not itself a JSON document. The API makes the boundary visible.

### CollectedSelection methods

`cvd.collectedSelection` exposes:

```js
selected.summary()
selected.toJSON()
selected.status()
selected.bounds()
selected.text()
selected.styles(["color", "font-size"])
selected.attributes(["class"])
```

The object is immutable from JavaScript's point of view. If a user wants a different selector, they should create a different locator. If a user wants a fresh view of the page, they should collect again.

### SelectionComparison methods

`cvd.selectionComparison` exposes both methods and nested namespaces:

```js
comparison.summary()
comparison.toJSON()
comparison.left()
comparison.right()
comparison.artifact("diffComparison")

comparison.pixel.summary()
comparison.bounds.diff()
comparison.styles.diff(["color"])
comparison.attributes.diff(["class"])
comparison.report.markdown()
await comparison.report.writeMarkdown("out/compare.md")
comparison.artifacts.list()
await comparison.artifacts.write("out", ["json", "markdown"])
```

The property namespaces — `pixel`, `bounds`, `styles`, `attributes`, `report`, `artifacts` — required extending the Proxy infrastructure. Earlier handles were method-only. A comparison object reads more naturally as a small object graph, not as a flat list of methods.

### The `.then` trap

One subtle bug appeared when returning Proxy handles from Promises. JavaScript Promise resolution checks whether a resolved value is a thenable by reading its `.then` property. Our Proxy originally treated every unknown property read as an error, so this failed:

```js
const selected = await page.locator("#cta").collect()
```

with an error like:

```text
TypeError: cvd.collectedSelection: unknown method .then(). Available: attributes, bounds, status, styles, summary, text, toJSON.
```

The fix was to make the Proxy return `undefined` for property `then`. That tells Promise resolution the handle is not a thenable. This is now a general invariant for all Promise-returned Proxy handles.

```go
if property == "then" {
    return goja.Undefined()
}
```

This is a small line with architectural weight. Without it, Promise-first handles are not safe.

## 9. Phase 6: the low-effort comparison path

The sixth phase implemented the public quick path:

```js
const comparison = await cvd.compare.region({
  left: leftPage.locator("#cta"),
  right: rightPage.locator("#cta"),
  outDir: "artifacts/cta",
})
```

This is not a wrapper around the old CLI mode. It is ordinary orchestration over the new primitives:

```text
compare.region(options)
  validate left/right are cvd.locator handles
  choose inspect = "rich" by default
  choose threshold = 30 by default
  collect left under left page lock
  capture left region screenshot
  collect right under right page lock
  capture right region screenshot
  compare selections using service.CompareSelections
  return cvd.selectionComparison handle
```

The implementation deliberately collects each side under that side's `runExclusive` page lock and releases it before comparing. This avoids nested page locks. Same-page comparisons are serialized. Separate-page comparisons are safe and deterministic, even if not aggressively parallelized yet.

### What the quick path writes

When `outDir` is provided, the quick path writes:

```text
left_region.png
right_region.png
diff_only.png
diff_comparison.png
```

The returned comparison can then write JSON and Markdown:

```js
await comparison.artifacts.write("artifacts/cta", ["json", "markdown"])
```

which produces:

```text
compare.json
compare.md
```

This gives scripts one object that can answer questions and write evidence.

## 10. Phase 7: canonical namespaces

The ticket explicitly moved away from backward compatibility as a design constraint. That does not mean every old internal alias was removed in one pass, but it does mean the documented public surface now teaches explicit names:

| Old ambiguous shape | Canonical shape |
|---|---|
| `cvd.snapshot(page, probes)` | `cvd.snapshot.page(page, probes)` |
| `cvd.diff(before, after)` | `cvd.diff.structural(before, after)` |
| `cvd.catalog(options)` | `cvd.catalog.create(options)` |
| `cvd.loadConfig(path)` | `cvd.config.load(path)` |
| Internal `require("diff")` | Public `cvd.compare.region(...)` / `cvd.image.diff(...)` |

The reason is not aesthetic. Each top-level shortcut creates ambiguity. What does `cvd.diff` mean in a tool whose main purpose is visual diffing? Structural JSON diff? Pixel diff? Style diff? The canonical names answer that question before the user has to ask it.

The public map now looks like this:

```js
cvd.collect.selection(locator, options)
cvd.compare.selections(left, right, options)
cvd.compare.region({ left, right, ... })
cvd.image.diff({ left, right, threshold })
cvd.diff.structural(before, after, options)
cvd.snapshot.page(page, probes, options)
cvd.catalog.create(options)
cvd.config.load(path)
```

This structure is slightly more verbose. It is also easier to remember because related operations live together.

## 11. Phase 8: built-ins dogfood the public API

The built-in compare script used to call internal helpers:

```js
require("diff").compareRegion(...)
require("report").renderAgentBrief(...)
```

It now uses the public module:

```js
const cvd = require("css-visual-diff")
const comparison = await cvd.compare.region({ ... })
```

The file is:

```text
internal/cssvisualdiff/dsl/scripts/compare.js
```

The built-in command remains:

```bash
css-visual-diff verbs script compare region ...
```

but its implementation is now an example of the public API. That matters because built-ins are the most realistic smoke test. They exercise jsverbs metadata, command parsing, browser setup, page loading, selector collection, screenshot capture, pixel diffing, artifact writing, and structured output.

The output schema intentionally changed from old mode-shaped fields like:

```text
computed_diffs
pixel_diff
```

to the new comparison schema:

```text
cssvd.selectionComparison.v1
```

This was acceptable because the ticket explicitly did not require backward compatibility. The design favors a coherent future API over preserving an old internal shape.

## 12. The current validation story

The work is covered by several layers of validation.

### Service tests

Service-level tests cover:

- collection profiles,
- invalid selectors,
- all styles and all attributes,
- pixel diff thresholds,
- different-size image normalization,
- PNG artifact writing,
- selection comparison diffs,
- deterministic ordering,
- JSON schema shape.

Representative commands:

```bash
go test ./internal/cssvisualdiff/service -run 'TestCollectSelection' -count=1
go test ./internal/cssvisualdiff/service -run 'TestDiffImages|TestWritePixelDiff|TestValidatePixel' -count=1
go test ./internal/cssvisualdiff/service -run 'TestCompareSelections' -count=1
```

### JavaScript integration tests

The repository-scanned JS integration tests live in:

```text
internal/cssvisualdiff/verbcli/command_test.go
```

They exercise real Goja/jsverbs execution and real Chromium-backed local pages. Important tests include:

```text
TestCVDModuleCollectsLocatorSelection
TestCVDModuleComparesCollectedSelections
TestCVDModuleCompareRegionLowEffortAPI
TestCVDModuleCompareRegionRejectsRawObjects
```

### Ticket smoke scripts

The ticket keeps replayable smoke scripts under:

```text
ttmp/2026/04/25/CSSVD-JSAPI-PIXEL-WORKFLOWS--design-js-api-additions-for-pixel-comparison-and-workflow-orchestration/scripts/
```

Relevant scripts:

```text
001-service-collection-smoke.sh
002-pixel-service-smoke.sh
003-selection-compare-service-smoke.sh
004-js-collected-selection-smoke.sh
005-js-selection-comparison-smoke.sh
006-js-compare-region-smoke.sh
007-canonical-api-surface-smoke.sh
008-built-in-compare-dogfood-smoke.sh
```

The full suite has passed with:

```bash
go test ./... -count=1
```

The docmgr ticket also validates:

```bash
docmgr doctor --root ./ttmp --ticket CSSVD-JSAPI-PIXEL-WORKFLOWS --stale-after 30
```

### What has not yet been tested

The implementation has been tested with real Chromium, but so far against local fixture pages, not an external production site. A useful next validation would run `cvd.compare.region(...)` against a real public site or a Pyxis target page and preserve the artifacts as a new smoke or research result. The local tests are strong regression tests; they are not a substitute for a real-site trial with network variability, fonts, lazy loading, cookies, and content security policies.

## 13. Failure modes and design lessons

### Failure mode: returning Proxy handles from Promises

The `.then` issue is the kind of bug that appears only when a design crosses language boundaries. In Go, returning a Proxy object from a Promise resolver looks straightforward. In JavaScript, Promise resolution performs thenable assimilation. A strict Proxy that throws on unknown properties must therefore special-case `then`.

The rule for future handle authors is simple:

> Any Goja Proxy value that can be resolved from a Promise must return `undefined` for `.then` unless it intentionally implements thenable behavior.

### Failure mode: too many browser sessions in tests

Early collection tests started many Chromium instances. During a full `go test ./...`, Chrome startup pressure produced an error involving `/dev/null` and zygote startup. The fix was not to hide the error; it was to reduce unnecessary browser churn by consolidating related assertions into fewer browser-backed tests.

The lesson is that browser tests should be meaningful but not wasteful. Unit-test pure data logic heavily. Use Chromium-backed tests for the paths that actually need Chromium.

### Failure mode: temporary Go smoke tests outside the repo

One smoke script generated a temporary Go test under `/tmp` and imported:

```go
github.com/go-go-golems/css-visual-diff/internal/cssvisualdiff/service
```

Go rejected it because `internal` packages can only be imported from inside the parent tree. The fix was to create the temporary smoke package inside the repository root and remove it on exit.

The general rule is:

> If a smoke test imports an `internal/...` package, generate it inside the repository tree.

### Failure mode: mode-shaped results leaking into the API

The old compare mode had fields such as `computed_diffs` and `pixel_diff`. Those names made sense for a CLI mode. They do not make sense as the long-term JavaScript comparison object. The new schema uses lowerCamel and centers on comparison concepts:

```js
comparison.styles
comparison.pixel
comparison.bounds
comparison.attributes
comparison.artifacts
```

This is a design lesson: implementation history should not be allowed to name the public model.

## 14. How to read the code

A good review path is:

1. Start with `internal/cssvisualdiff/service/collection.go`. Understand what gets captured and when browser state becomes data.
2. Read `internal/cssvisualdiff/service/pixel.go`. Understand image normalization, thresholding, and artifact writing.
3. Read `internal/cssvisualdiff/service/selection_compare.go`. Understand pure comparison over collected data.
4. Read `internal/cssvisualdiff/jsapi/collect.go`. See how `locator.collect(...)` wraps the service.
5. Read `internal/cssvisualdiff/jsapi/compare.go`. See how `cvd.compare.selections(...)` and `cvd.compare.region(...)` are exposed.
6. Read `internal/cssvisualdiff/jsapi/proxy.go`. Notice `Properties` and the `.then` special case.
7. Read `internal/cssvisualdiff/dsl/scripts/compare.js`. See the built-in dogfood example.
8. Read `internal/cssvisualdiff/verbcli/command_test.go`. See real repository-scanned JS verbs use the API.

The most important files are:

```text
internal/cssvisualdiff/service/collection.go
internal/cssvisualdiff/service/pixel.go
internal/cssvisualdiff/service/selection_compare.go
internal/cssvisualdiff/jsapi/collect.go
internal/cssvisualdiff/jsapi/compare.go
internal/cssvisualdiff/jsapi/proxy.go
internal/cssvisualdiff/dsl/scripts/compare.js
internal/cssvisualdiff/doc/topics/javascript-api.md
```

## 15. Working examples

### Low-effort region comparison

```js
async function compareCTA(leftUrl, rightUrl, outDir) {
  const cvd = require("css-visual-diff")
  const browser = await cvd.browser()
  let leftPage, rightPage

  try {
    leftPage = await browser.page(leftUrl, { viewport: { width: 1280, height: 720 } })
    rightPage = await browser.page(rightUrl, { viewport: { width: 1280, height: 720 } })

    const comparison = await cvd.compare.region({
      name: "cta",
      left: leftPage.locator("#cta"),
      right: rightPage.locator("#cta"),
      outDir,
      styleProps: ["font-size", "line-height", "color", "background-color"],
      attributes: ["class", "aria-label"],
    })

    await comparison.artifacts.write(outDir, ["json", "markdown"])
    return comparison.summary()
  } finally {
    if (leftPage) await leftPage.close()
    if (rightPage) await rightPage.close()
    await browser.close()
  }
}
```

### Primitive collect-and-compare path

```js
const left = await leftPage.locator("#content").collect({
  inspect: "rich",
  styles: ["font-size", "line-height", "color"],
  attributes: ["class"],
})

const right = await rightPage.locator("#content").collect({
  inspect: "rich",
  styles: ["font-size", "line-height", "color"],
  attributes: ["class"],
})

const comparison = await cvd.compare.selections(left, right, {
  styleProps: ["font-size", "line-height", "color"],
  attributes: ["class"],
})

const typographyChanges = comparison.styles.diff(["font-size", "line-height"])
const bounds = comparison.bounds.diff()

return {
  ok: typographyChanges.length === 0 && !bounds.changed,
  summary: comparison.summary(),
  typographyChanges,
  bounds,
}
```

### Image diff primitive

```js
const pixels = await cvd.image.diff({
  left: "artifacts/left.png",
  right: "artifacts/right.png",
  threshold: 30,
  diffOnlyPath: "artifacts/diff_only.png",
  diffComparisonPath: "artifacts/diff_comparison.png",
})

return {
  changedPercent: pixels.changedPercent,
  diff: pixels.diffComparisonPath,
}
```

## 16. Open questions

The core API is now in place, but several questions remain.

### Should old top-level aliases be removed immediately?

Public docs now teach canonical names, but old implementation aliases still exist. Removing them would better match the no-backward-compat stance. Keeping them for a short time avoids unrelated breakage while the new API is still landing. This is a product/API decision more than a technical one.

### How should PNG artifacts be managed by comparison handles?

`cvd.compare.region(...)` writes PNG artifacts because it captures screenshots. `comparison.artifacts.write(...)` currently writes JSON and Markdown comparison outputs. A future artifact layer could copy, move, or lazily materialize PNGs as named artifacts. That should be designed carefully so scripts can predict paths.

### How should catalogs record comparisons?

Phase 9 should let catalogs record `SelectionComparison` handles directly. The catalog should not just store arbitrary JSON; it should know that a comparison has a schema version, summaries, artifacts, and report links.

### What should real-site validation look like?

The implementation has local Chromium-backed tests. A next smoke should compare a real public site or a Pyxis page pair and store the artifacts. Real sites introduce fonts, network timing, lazy loading, sticky headers, consent dialogs, and animation. These are exactly the conditions a visual diff tool must eventually handle.

## 17. Near-term next steps

The next implementation phase should focus on catalog/report/artifact integration:

1. Add a way to record a `cvd.selectionComparison` in a catalog.
2. Ensure catalog manifests include comparison summaries and artifact paths.
3. Make index Markdown link to comparison reports and PNG artifacts.
4. Clarify artifact semantics for existing PNGs versus generated JSON/Markdown.
5. Add `scripts/009-comparison-catalog-smoke.sh`.
6. Run a real-site comparison smoke and preserve the findings.

After that, the documentation should be refreshed as a user guide rather than an implementation report. The API is now coherent enough that the next documentation layer can teach users how to build pixel-perfect feedback loops, not just how the internals work.

## 18. Key takeaways

- A locator is live browser intent; a collected selection is immutable browser evidence. Confusing those two concepts makes scripts unstable.
- A comparison should compare data, not keep asking the browser for facts. This is what makes reports deterministic.
- Pixel diffing is a service primitive, not a CLI mode detail. Once extracted, it can serve built-ins, JavaScript APIs, and future catalog/report flows.
- Goja Proxy handles are powerful, but Promise-returned proxies must be `.then` safe.
- The best low-effort API is not a shortcut around the model. `cvd.compare.region(...)` is useful because it is exactly the primitive path with sensible defaults.
- Built-ins should dogfood public APIs. When built-ins require private helpers, the public API is probably incomplete.

The design is now in a useful place: it gives simple scripts a one-call comparison path and gives advanced scripts typed, queryable primitives. That combination is what makes the API worth building. It does not force users into a workflow builder, and it does not leave them with unstructured blobs. It gives them JavaScript objects that reflect the actual domain: pages, selectors, collected evidence, comparisons, reports, and artifacts.
