# DataDrop Professional Plotting Suite

## Repository audit, grammar design, compiler architecture, migration plan, and TypeScript reference implementation

**Prepared:** 2026-07-28  
**Repository analyzed:** `go-go-golems/go-go-datadrop`  
**Baseline:** `main` at commit `06fe133876fdb45ffa33f9f6257b29a68f437f50`  
**Reference implementation:** `@datadrop/professional-plotting-suite-reference` in this directory

---

## Executive recommendation

DataDrop already has the hardest architectural prerequisite for a serious plotting system: a typed table boundary, an authoring document, a semantic compiler, a logical relational graph, a parameterized DuckDB physical compiler, and a pure geometry builder. The correct next move is **not** to keep enlarging `ui/src/model/plot.ts`. The correct move is to turn the current single-view pipeline into a staged, layered plotting compiler.

The target architecture should enforce three boundaries:

1. **The fluent TypeScript API builds data, not behavior.** Configuration lambdas mutate short-lived draft builders and disappear. The resulting authoring document is versioned, JSON-serializable, diffable, clonable, migratable, and safe to persist.
2. **Field names are resolved exactly once.** Authoring may use ergonomic names, but the semantic compiler binds every field reference to a stable `FieldId`, type, unit, timezone, role, nullability, and provenance. No downstream stage should return to bare names as identity.
3. **Renderers consume a backend-neutral scene graph.** SVG, Canvas, WebGL/WebGPU, PDF, PNG, and UI inspection should interpret the same planned scene. React should host a renderer; it should not be the plotting engine.

The recommended pipeline is:

```text
fluent builder
    ↓
versioned authoring document
    ↓  bind, type-check, desugar, infer defaults
semantic / logical plot IR
    ↓  lower transforms, statistics, positions
physical data plan (DuckDB / Arrow / in-memory test backend)
    ↓  execute and train scales
layout + guide plan
    ↓  emit backend-neutral primitives
scene graph
    ↓
SVG | Canvas | WebGL/WebGPU | PDF | PNG | accessibility tree
```

The TypeScript implementation delivered with this report demonstrates that shape. It includes an immutable fluent builder, a serializable v2 authoring IR, semantic compilation, stable-field binding, transforms, statistics, positions, scales, facets, themes, scene construction, SVG and Canvas interpreters, a plugin registry, a v1 DataDrop migration adapter, tests, and generated scientific plots.

It is an executable architectural reference, not a claim that every production feature described below is finished. The production integration should retain DataDrop’s existing DuckDB compiler and replace the reference implementation’s in-memory data interpreter with a physical-plan backend.

---

## 1. What exists today

### 1.1 The current pipeline

DataDrop’s browser visualization path is already divided into recognizable compiler stages:

```text
server table + inferred schema
    ↓
GraphicDocument v1
    ↓  compileGraphicDocument
LogicalGraphic (stable field symbols, relational operations)
    ↓  compileDuckDBRelation
parameterized DuckDB SQL
    ↓  AnalysisRuntime
normalized result table
    ↓  buildPlotFromResult
Plot geometry
    ↓  ChartPanel / PlotSvg
React-rendered SVG
```

The main source files are:

| Concern | Current file | Assessment |
|---|---|---|
| Typed table wire model | [`ui/src/model/table.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/src/model/table.ts) | Good boundary; too little metadata for scientific work. |
| Authoring and logical graphics IR | [`ui/src/model/graphic.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/src/model/graphic.ts) | Strong relational foundation; visual grammar is intentionally narrow. |
| Authoring helpers | [`ui/src/model/graphicAuthoring.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/src/model/graphicAuthoring.ts) | Useful helpers; mutable and specialized to one root view/chain. |
| DuckDB lowering | [`ui/src/analysis/compile.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/src/analysis/compile.ts) | Correctly parameterized and field-ID based; should be retained and generalized. |
| Browser execution | [`ui/src/analysis/runtime.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/src/analysis/runtime.ts) | Clear lifecycle and metrics; ingestion and scheduling need evolution. |
| Plot compilation | [`ui/src/model/plot.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/src/model/plot.ts) | Pure and testable, but monolithic and too narrow to extend safely. |
| SVG presentation | [`ui/src/components/organisms/ChartPanel/ChartPanel.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/src/components/organisms/ChartPanel/ChartPanel.tsx) | Useful interaction seam; renderer-specific and minimal. |
| Plot tests | [`ui/test/plot.test.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/test/plot.test.ts) | Good pure-function tests; coverage reflects the narrow grammar. |

### 1.2 What is already correct

#### Typed-table seam

The server decides field types and carries inference provenance. That is the correct trust boundary. Scientific plotting should not repeatedly reinterpret values at every visual layer. The server or analytical backend should remain authoritative for physical types, while the plot document may apply local semantic roles such as quantitative, ordinal, temporal, identifier, interval endpoint, or weight.

#### Stable field symbols in the relational compiler

`graphic.ts` distinguishes authoring field references from compiled `FieldSymbol`s and uses stable IDs and provenance in the logical graph. This is one of the strongest parts of the codebase. It enables safe rename handling, transform-produced fields, diagnostics, and deterministic physical aliases.

#### Declarative authoring document

The current document is structured-clone and JSON safe. That property must remain non-negotiable. It enables persistence, permalinks, undo/redo, comparisons, migrations, collaboration, test fixtures, and provenance.

#### Explicit coverage and truncation

DataDrop distinguishes bounded windows from whole-dataset results and reports truncation. A professional plotting system must preserve that information into the scene and export metadata. A visually polished chart that silently represents only the first 10,000 rows is analytically misleading.

#### Parameterized physical compilation

The DuckDB compiler builds CTEs and bound parameters rather than interpolating user values into SQL. The plotting redesign should extend this compiler rather than replace it with ad hoc JavaScript data manipulation in production.

#### Pure geometry generation

`buildPlotFromResult` has no React or DOM dependency. That is the right direction. The replacement should preserve purity while decomposing the monolith into compiler services and plugins.

#### Diagnostics instead of exceptions

The current compiler reports draft transforms, missing fields, cycles, ambiguous names, invalid types, and invalid limits. A professional plotting compiler should continue this pattern and expand it to visual semantics, layout, statistics, units, scale domains, guide conflicts, renderer limits, and incomplete coverage.

---

## 2. The central defects to fix

### 2.1 Stable identity is lost at the plotting boundary

The relational compiler resolves authoring references to stable `FieldId`s, but `buildPlotFromResult` receives the authoring `AuthoringView` and reconstructs its mapping by field **name**. It then validates against `fields` by name and reads rows with `row[name]`.

This creates two systems of truth:

```text
relational compiler: FieldId + type + provenance
plot compiler:        string name + q/n/t
```

Consequences:

- A rename can compile correctly relationally and still break visually.
- Duplicate display names cannot be represented safely.
- A transformed field’s provenance is unavailable to tooltips, diagnostics, and interactions.
- Units, timezones, nullability, and semantic roles cannot reach scale inference.
- The renderer cannot identify which source or transform produced a mark.
- UI edits may target an authoring name rather than the field actually rendered.

**Required change:** the plot compiler must consume a compiled visual view or `LogicalPlot`, never the authoring view. Rows may still use physical column aliases at the backend boundary, but the mapping from `FieldId` to physical column must remain explicit.

### 2.2 A view is not a grammar

The current `AuthoringView` has:

- one relation,
- one mark,
- one mapping,
- one `yScale`,
- optional references.

A layered grammar needs at least:

- plot-level data and mapping,
- zero or more layers,
- per-layer data, transforms, mapping, stat, geom, position, parameters, and inheritance,
- one scale per aesthetic channel,
- guides,
- faceting,
- coordinate systems,
- theme,
- annotations,
- interactions,
- renderer/export policy.

A confidence ribbon plus regression line plus raw points is not three chart types. It is three layers that share data, facets, and scales. The layer must be the primary composition unit.

### 2.3 `plot.ts` mixes too many compiler phases

The current file performs all of the following in one function:

- mapping validation,
- semantic validation,
- facet enumeration,
- category pooling,
- color interpolation,
- scale-domain inference,
- domain expansion,
- log fallback,
- tick generation,
- panel layout,
- mark limiting,
- grouping,
- sorting,
- position calculation,
- geom construction,
- reference-line clipping,
- legend construction.

That is manageable for four marks and five channels. It becomes brittle when adding stacking, dodging, statistical transforms, free scales, dual interval channels, coordinate transforms, guide merging, text measurement, or multiple renderers.

**Required change:** split the compiler into named passes with typed input/output contracts.

### 2.4 Hard-coded policy is embedded in geometry

The current engine includes fixed values such as:

- eight category colors,
- six facets,
- 5,000 marks per panel,
- one continuous color ramp,
- one fixed panel arrangement heuristic,
- one fixed padding model,
- one tick algorithm,
- one legend placement,
- one category-overflow behavior.

Limits are necessary, but they are policy. They belong in `RenderSpec`, `LayoutSpec`, theme defaults, backend capabilities, and diagnostics—not as hidden geom behavior.

### 2.5 The renderer is SVG-specific

`ChartPanel` renders a hand-written SVG vocabulary and wraps individual marks in PBUI presentations. That is useful for interaction, but it couples:

- scene representation,
- SVG elements,
- React reconciliation,
- accessibility,
- event targeting,
- mark-count limits.

A 50,000-point scatter plot should not require 50,000 React components. A publication export should not depend on a mounted React tree. A Canvas or WebGL renderer should not need to reverse-engineer SVG geometry.

### 2.6 The table schema is too small for scientific plotting

The current `Field` contains `name`, `q/n/t`, inference source, distinct count, and null count. A professional schema should carry:

```ts
interface FieldSchema {
  id: FieldId;
  name: string;
  label?: string;
  physicalType: PhysicalType;
  semanticType: SemanticType;
  role?: "dimension" | "measure" | "identifier" | "weight" | "interval";
  nullable: boolean;
  unit?: string;
  timezone?: string;
  order?: JsonPrimitive[];
  provenance?: FieldProvenance;
  statistics?: FieldStatistics;
}
```

This is necessary for correct temporal scales, ordinal order, unit labels, uncertainty channels, missing-value diagnostics, and stable bindings.

### 2.7 The execution path serializes row objects through NDJSON

The current runtime serializes JavaScript rows to NDJSON, registers a file, creates a table, and copies JSON into DuckDB. This is a reasonable initial implementation, but it becomes expensive for large tables and repeats type conversion. DuckDB-Wasm supports Arrow table and Arrow IPC stream ingestion, and Arrow is a columnar format designed for analytical interchange.[^duckdb-ingestion] [^arrow]

**Required change:** make Arrow the preferred runtime table representation and retain row objects only as an ergonomic authoring/test adapter.

### 2.8 Statistics are not first-class

Aggregation exists as a relational transform, but visual statistics do not. A grammar needs to distinguish:

- data transforms that create a reusable relation,
- a layer statistic that computes display values,
- a geom that draws those values,
- a position adjustment that resolves overlap.

For example:

```text
raw rows
  → stat_summary(mean, ci95)
  → position_dodge
  → geom_errorbar + geom_bar
```

Those components must be independently replaceable and inspectable.

---

## 3. Design model

The design follows the layered grammar articulated by Wickham: graphics are composed from data, mappings, statistical transformations, geometric objects, positions, scales, coordinates, facets, and theme.[^wickham] ggplot2’s own layer contract explicitly combines data, mapping, stat, geom, and position, with inheritance and override behavior.[^ggplot-layer] Vega-Lite demonstrates the complementary compiler approach: a concise declarative grammar lowers into a more explicit runtime specification while retaining override points.[^vegalite] Observable Plot reinforces mark layering, tidy data, inferred scales, and a practical JavaScript-facing API.[^observable-marks]

### 3.1 Core nouns

| Noun | Responsibility | Must not do |
|---|---|---|
| `DataSource` | Schema, coverage, origin, runtime handle | Decide visual encodings |
| `Transform` | Produce a new reusable relation | Draw marks |
| `Mapping` | Bind data or constants to aesthetic channels | Calculate pixels |
| `Stat` | Compute layer display variables | Choose the visual shape |
| `Position` | Adjust overlapping display variables | Train scales after arbitrary mutation |
| `Geom` | Emit semantic mark primitives from scaled values | Query DuckDB |
| `Scale` | Map data space to aesthetic space | Own panel layout |
| `Guide` | Explain a scale through an axis or legend | Recompute the scale independently |
| `Facet` | Partition data into panels | Duplicate global annotations accidentally |
| `Coordinate` | Transform positioned aesthetic space | Mutate source data |
| `Theme` | Default visual policy | Change analytical results |
| `Interaction` | Declare selections and event semantics | Become persisted closures |
| `SceneGraph` | Renderer-neutral, resolved visual plan | Contain compiler callbacks |
| `Renderer` | Interpret scene nodes | Re-infer statistics, scales, or layout |

### 3.2 Opinionated defaults with local escape hatches

The system should be opinionated in a hierarchy:

```text
package defaults
    < theme preset
    < document-level settings
    < layer-level settings
    < explicit scale/guide/geom override
    < renderer capability override
```

Defaults should optimize for truthful scientific graphics:

- no silent row or mark truncation,
- colorblind-oriented categorical palette,
- zero baseline by default for bars, not for arbitrary point/line plots,
- UTC for unzoned instants unless a timezone is declared,
- area encodes magnitude and point radius uses square-root scaling,
- confidence intervals state their method in metadata,
- ordinal fields preserve declared order,
- missing/invalid values produce counts and diagnostics,
- facets share scales by default for comparison,
- axes and guides derive titles from field labels and units,
- exports embed document fingerprint, coverage, compiler version, and warnings.

Every default must be overridable through a typed builder or a lower-level document edit.

### 3.3 Lambdas configure builders; they are never serialized

The desired fluent pattern is appropriate when the lambdas only construct declarative data:

```ts
const chart = plot(table)
  .mapping((m) => m
    .x("time")
    .y("response")
    .color("treatment")
    .group("treatment"))
  .layer((layer) => layer
    .name("observations")
    .point((geom) => geom.radius(2.2).opacity(0.35)))
  .layer((layer) => layer
    .name("95% confidence band")
    .stat((stat) => stat.linearRegression({ confidence: 0.95 }))
    .ribbon((geom) => geom.opacity(0.18)))
  .layer((layer) => layer
    .name("fitted model")
    .stat((stat) => stat.linearRegression({ confidence: 0.95 }))
    .line((geom) => geom.strokeWidth(2.4)))
  .facet((facet) => facet.wrap("batch").columns(2))
  .scales((scales) => {
    scales.x((scale) => scale.linear().zero(true).nice(6));
    scales.y((scale) => scale.linear().zero(false).nice(6));
    scales.color((scale) => scale.categorical().title("Treatment"));
  })
  .theme((theme) => theme.preset("publication"));
```

The callback is executed immediately against a private draft. The stored IR contains only objects, arrays, strings, numbers, booleans, and null. This gives the ergonomics of code and the operational properties of a document format.

The reference implementation makes the outer `PlotBuilder` immutable. Each method deep-clones the document, revises the clone, and returns a new builder. Nested builders may mutate only that private clone. This supports composition:

```ts
const scientificBase = (p: PlotBuilder) => p
  .theme((t) => t.preset("publication"))
  .render((r) => r.auto().embedMetadata())
  .layout((l) => l.dpi(144));

const withStandardAxes = (p: PlotBuilder) => p.scales((s) => {
  s.x((x) => x.nice(6).guide((g) => g.grid(true)));
  s.y((y) => y.nice(6).guide((g) => g.grid(true)));
});

const chart = withStandardAxes(scientificBase(plot(table)))
  .mapping((m) => m.x("time").y("value"))
  .layer((l) => l.line());
```

### 3.4 Expression lambdas also produce data

Transforms should avoid arbitrary JavaScript callbacks because closures are not portable to DuckDB, workers, persistence, or server execution. Instead, expression builders create an AST:

```ts
const filtered = plot(table)
  .parameter("minimum", 12)
  .transform((t) => t
    .filter((e) => e.and(
      e.gte("measurement", e.parameter("minimum")),
      e.isFinite("measurement"),
    ))
    .mutate(
      "log_measurement",
      "quantitative",
      (e) => e.log10("measurement"),
    ));
```

The document stores this:

```json
{
  "kind": "binary",
  "operator": "and",
  "left": {
    "kind": "binary",
    "operator": "gte",
    "left": { "kind": "field", "name": "measurement" },
    "right": { "kind": "parameter", "parameter": "minimum" }
  },
  "right": {
    "kind": "unary",
    "operator": "isFinite",
    "value": { "kind": "field", "name": "measurement" }
  }
}
```

That AST can be interpreted in tests, lowered to parameterized SQL, compiled to Arrow compute kernels, or sent to a server.

---

## 4. Versioned IR architecture

A full system should use multiple IRs rather than a single “spec” that accumulates both author intent and runtime details.

### 4.1 Stage A: authoring document

Characteristics:

- ergonomic names permitted,
- incomplete/draft states permitted in UI memory,
- serializable and versioned,
- no functions,
- explicit overrides only,
- suitable for persistence and collaborative edits.

The reference format is:

```ts
interface PlotDocument {
  format: "datadrop.plot.document";
  version: 2;
  id: string;
  name: string;
  sourceId: string;
  sources: Record<string, DataSourceSpec>;
  parameters: Record<string, ParameterValue>;
  transforms: TransformSpec[];
  mapping: MappingSpec;
  layers: LayerSpec[];
  scales: Partial<Record<ScaleChannel, ScaleSpec>>;
  facet?: FacetSpec;
  coordinate: CoordinateSpec;
  theme: ThemeSpec;
  layout: LayoutSpec;
  labels: LabelSpec;
  interactions: InteractionSpec[];
  render: RenderSpec;
  metadata?: Record<string, JsonValue>;
}
```

A layer is independently composable:

```ts
interface LayerSpec {
  id: string;
  name?: string;
  sourceId?: string;
  enabled: boolean;
  inheritMapping: boolean;
  mapping: MappingSpec;
  transforms: TransformSpec[];
  stat: StatSpec;
  geom: GeomSpec;
  position: PositionSpec;
  showLegend: boolean | "auto";
  facetMode: "auto" | "panel" | "repeat" | "super";
}
```

### 4.2 Stage B: semantic/logical plot IR

The compiler resolves all authoring ambiguity:

- field names → stable IDs,
- physical and semantic types,
- units and timezones,
- inherited mappings,
- transform output schemas,
- `afterStat` fields,
- default stats, positions, scales, guides, and geom parameters,
- shared versus independent scale groups,
- facet semantics,
- renderer capability requirements.

A bound field resembles:

```ts
interface BoundFieldRef {
  kind: "field";
  fieldId: FieldId;
  name: string;
  label: string;
  valueType: {
    physicalType: PhysicalType;
    semanticType: SemanticType;
    nullable: boolean;
    unit?: string;
    timezone?: string;
  };
}
```

The logical layer carries both the input mapping and the post-stat mapping. This is essential for histogram bins, summary intervals, regression bands, density estimates, boxplot quartiles, and computed labels.

### 4.3 Stage C: physical data plan

The logical plot should lower to a DAG of relational and statistical operators. It should not assume that every layer independently scans and transforms the source.

Example:

```text
scan(source)
  └─ filter(valid && treatment != null)
      ├─ materialize raw relation ───────────────→ point layer
      ├─ group(treatment, batch) + regress ─────→ line layer
      └─ reuse regression output ────────────────→ ribbon layer
```

The physical planner should:

- deduplicate equivalent prefixes,
- push filters and projections toward scans,
- share bins and summaries across compatible layers,
- select DuckDB SQL, Arrow compute, or local kernels per operator,
- insert materialization boundaries only when useful,
- preserve deterministic ordering where geoms require it,
- include row/byte estimates and coverage semantics,
- support cancellation and partial invalidation.

The current DataDrop relational compiler can remain the initial physical backend. Add operators for joins, windows, binning, quantiles, regression, density, sampling, and domain summaries rather than moving those operations into React.

### 4.4 Stage D: trained visual plan

After data execution, the visual compiler has concrete values and can train:

- domains,
- breaks/ticks,
- categorical order,
- palettes,
- legends,
- facet panel keys,
- shared/free scale groups,
- axis extents,
- text measurements,
- panel dimensions,
- clipping regions.

This stage should be deterministic for a given logical plan, result batches, dimensions, font metrics, and renderer capability profile.

### 4.5 Stage E: scene graph

The scene is the renderer contract. It contains resolved primitives in device-independent pixels, styles, clip IDs, z-order, accessibility metadata, and datum provenance.

The reference scene supports:

```ts
type SceneNode =
  | LineNode
  | RectNode
  | CircleNode
  | PathNode
  | TextNode;
```

A production scene should add:

- groups/transforms,
- symbols,
- images/raster tiles,
- gradients and patterns,
- rich text spans,
- marker definitions,
- hit-test regions,
- semantic axis/legend groups,
- renderer hints,
- optional instanced mark batches for GPU backends.

The renderer must not infer domains or recalculate statistics. It only interprets the scene.

---

## 5. Compiler passes

A compiler pipeline should be explicit and inspectable. Each pass should accept one IR and return another plus diagnostics.

### Pass 0: validate envelope and migrate

- Check magic format and version.
- Apply pure `vN → vN+1` migrations.
- Preserve unknown metadata.
- Reject future versions with a clear diagnostic.
- Record migration provenance.

### Pass 1: normalize/desugar

Convert conveniences into a smaller core:

- implicit point plot → explicit layer,
- `boxplot()` → `stat_boxplot + geom_boxplot`,
- `histogram()` → `stat_bin + geom_bar`,
- `smooth()` → stat plus line/ribbon layers,
- `coordFlip()` → coordinate transform,
- annotation helpers → constant-data layers,
- theme preset → complete theme values.

Sugar should not leak into later stages.

### Pass 2: resolve sources and relation graph

- Verify every source exists.
- Topologically order transforms.
- Detect cycles.
- Resolve disabled nodes to their input.
- Preserve coverage and provenance.
- Build schema versions at every relation edge.

### Pass 3: bind expressions and field references

- Resolve authoring names against the input schema.
- Prefer stored `FieldId` when present.
- Reject stale IDs rather than silently binding a same-named field.
- Infer expression result physical type, semantic type, nullability, unit, and timezone.
- Validate function signatures.
- Bind parameters and verify their types.

### Pass 4: merge mappings

For every layer:

```text
plot mapping
  + layer mapping override
  - removed channels
  = effective pre-stat mapping
```

Mappings should support:

- field,
- constant,
- expression,
- `afterStat(name)`,
- future `afterScale(name)` for specialized annotations.

### Pass 5: compile statistics

A stat plugin receives the bound input schema and mapping, then declares:

- required channels,
- grouping variables,
- output fields and types,
- output mapping rewrites,
- physical execution capabilities,
- deterministic/order properties,
- whole-data requirements,
- incremental support.

For example, `stat_summary` may expose:

```text
__summary_x
__summary_y
__summary_ymin
__summary_ymax
__summary_n
```

The layer’s mapping is then resolved against those outputs.

### Pass 6: validate geom semantics

A geom declares required and optional channels, accepted semantic types, and defaults. Examples:

| Geom | Required | Common optional |
|---|---|---|
| point | x, y | color, fill, size, shape, opacity, tooltip |
| line | x, y | group, color, strokeWidth, order |
| ribbon | x, ymin, ymax | group, fill, opacity |
| bar | x, y or xmin/xmax/ymin/ymax | group, fill, color |
| errorbar | x, ymin, ymax | group, color, capWidth |
| boxplot | x, quartile outputs | fill, color, width |
| text | x, y, label | color, size, angle |
| rule | x or y; or endpoints | color, width, dash, label |

Validation belongs here, not in the renderer.

### Pass 7: compile positions

Positions operate after statistical output and before scales are finalized. They should emit explicit positional channels such as `xmin`, `xmax`, `ymin`, and `ymax`.

Built-ins should include:

- identity,
- stack,
- fill/normalize,
- dodge,
- jitter,
- jitter-dodge,
- nudge,
- beeswarm/quasirandom,
- collision avoidance for labels.

A position plugin must state whether it operates in data space, scale space, or pixel space. Stacking and dodging should generally operate in data/discrete-slot space; label collision requires pixel-space feedback and therefore a later layout pass.

### Pass 8: infer and validate scales

Scale inference should use semantic type and channel:

| Semantic/channel | Default |
|---|---|
| quantitative x/y | linear continuous |
| temporal x/y | UTC/time continuous |
| nominal x/y | band or point |
| ordinal x/y | ordered band/point |
| nominal color/fill | categorical |
| ordinal color/fill | ordered categorical/sequential |
| quantitative color/fill | sequential; diverging only with explicit pivot or semantic hint |
| quantitative size | square-root |
| opacity | clamped linear |
| shape | categorical symbol scale |

Supported scale families should include:

- linear,
- log,
- symlog,
- sqrt/power,
- time/UTC,
- band,
- point,
- ordinal,
- sequential,
- diverging,
- threshold/quantize/quantile.

Scale validation should diagnose non-positive log values, incompatible shared units, invalid manual domains, unknown categories, and conflicting layer requirements.

### Pass 9: resolve facets and scale groups

Faceting must be more general than one field and six panels:

- wrap by one or more fields,
- grid by row and column fields,
- fixed/free x/free y/free both,
- fixed/free space,
- drop or retain empty levels,
- margins/totals,
- strip placement and labeling,
- per-layer facet behavior:
  - `panel`: subset to each panel,
  - `repeat`: repeat annotation in every panel,
  - `super`: draw once over the whole plot,
  - `auto`: infer safe behavior.

The planner should enforce configurable panel budgets and report omitted panels explicitly.

### Pass 10: guides

Axes and legends are views over scales, not independent decorations. Guide merging should occur when compatible layers share a scale. Guide conflicts should be deterministic and diagnosable.

Features needed for professional output:

- titles with units,
- major/minor ticks,
- custom breaks and labels,
- scientific notation and SI prefixes,
- timezone-aware temporal formatting,
- label rotation/wrapping/elision,
- secondary transformed axes with a declared one-to-one transform,
- legend ordering and multiple columns,
- continuous color bars,
- combined color/shape legends,
- legend key glyphs supplied by geoms,
- guide placement inside or outside panels.

### Pass 11: layout

Layout should be a constraint problem, not fixed padding constants:

1. reserve title/subtitle/caption,
2. measure guide labels,
3. reserve axes and strips,
4. allocate legend boxes,
5. solve panel grid and aspect constraints,
6. train ranges against final panel dimensions,
7. rerun label collision/rotation if needed,
8. emit clip regions and transforms.

Text measurement must be abstracted so browser, headless Node, and PDF backends can provide compatible metrics.

### Pass 12: scene emission and optimization

Geoms emit semantic primitives. A scene optimizer may:

- merge collinear paths,
- batch same-style points,
- deduplicate definitions,
- simplify paths within a pixel tolerance,
- rasterize selected dense layers,
- retain vector axes/text over raster marks,
- build hit-test indices,
- strip row payloads from export scenes while retaining stable datum keys.

---

## 6. Data and analytical execution

### 6.1 Keep DuckDB as the production analytical backend

The existing DuckDB compiler is a good foundation because it provides:

- typed relational execution,
- parameterized SQL,
- aggregations and windows,
- efficient sorting and filtering,
- Arrow result transport,
- a path to browser and server parity.

The plotting compiler should not emit one monolithic SQL string directly. It should emit a physical operator DAG that a DuckDB lowerer converts into named CTEs, prepared parameters, and result projections. This retains inspectability and makes backend substitution possible.

### 6.2 Use Arrow as the execution interchange

DuckDB-Wasm can ingest Arrow tables or IPC streams and return Arrow data; Apache Arrow provides a language-independent columnar format designed for efficient analytics and zero-copy reads.[^duckdb-ingestion] [^arrow] The preferred path is:

```text
DataDrop server
  → Arrow IPC stream / Parquet / typed column batches
  → DuckDB-Wasm relation
  → Arrow RecordBatch stream
  → scale/stat domain consumers
  → renderer buffers
```

Avoid converting the entire result to `Array<Record<string, unknown>>` when a geom can consume vectors. Row views can be materialized lazily for tooltips and PBUI actions.

### 6.3 Backend contract

```ts
interface AnalyticalBackend {
  capabilities(): BackendCapabilities;
  prepare(plan: PhysicalPlan, signal: AbortSignal): Promise<PreparedPlan>;
  execute(
    prepared: PreparedPlan,
    parameters: Record<string, Scalar>,
    signal: AbortSignal,
  ): AsyncIterable<RecordBatch>;
  summarizeDomain?(request: DomainRequest, signal: AbortSignal): Promise<DomainSummary>;
  dispose(): Promise<void>;
}
```

Backends:

- `DuckDbWasmBackend` for browser production,
- `DuckDbServerBackend` for large/remote datasets,
- `ArrowComputeBackend` for simple vector operations,
- `InMemoryBackend` for deterministic unit tests and small examples.

The delivered implementation uses the last option so it has no runtime dependency. Its interfaces and IR are designed so the existing DataDrop DuckDB path can replace it.

### 6.4 Execution coverage

Coverage must flow through transformations and statistics:

```ts
interface Coverage {
  kind: "complete" | "bounded" | "sampled" | "stream-window" | "approximate";
  rows: number;
  hasMore: boolean;
  strategy?: "head" | "latest" | "uniform" | "reservoir" | "stratified";
  sourceRows?: number;
  confidence?: number;
  description?: string;
}
```

Rules:

- Filtering a bounded input remains bounded.
- Aggregating a bounded input does not become complete.
- A server-side whole-dataset aggregate may be complete even if the returned relation is small.
- Approximate algorithms must name the algorithm and error/confidence metadata.
- Every export should include a coverage summary.

### 6.5 Incremental invalidation

Use fingerprints at each stage:

```text
source fingerprint
transform fingerprint
layer data-plan fingerprint
scale-domain fingerprint
layout fingerprint
scene fingerprint
```

Changing a title should not rerun DuckDB. Changing a palette should not recompute statistics. Changing a filter should invalidate downstream data and scales. Resizing should rerun layout and scene emission, but not relational execution unless a resolution-dependent aggregation explicitly requests it.

### 6.6 Scheduling and cancellation

The current runtime serializes work through one promise queue. Production behavior should add:

- `AbortSignal` propagation,
- latest-request-wins cancellation,
- priority for visible plots,
- deduplication of identical plans,
- a bounded result cache,
- worker restart after memory pressure,
- per-principal purge as already implemented,
- optional backend pool only after measurement.

DuckDB-Wasm is single-threaded by default and browser memory is constrained, so concurrency should be deliberate rather than assumed.[^duckdb-wasm]

---

## 7. Statistics for scientific graphics

Statistics should be plugins with separate compile and execute/lower phases.

### 7.1 Baseline built-ins

The reference implementation includes:

- identity,
- count,
- bin/histogram,
- summary with mean/median/sum/min/max and SD/SE/normal CI,
- ordinary least-squares linear regression with confidence band,
- kernel density estimate,
- boxplot summaries.

A production suite should add:

- quantiles and arbitrary summary functions,
- bootstrap confidence intervals,
- Wilson/Agresti–Coull intervals for proportions,
- robust regression,
- polynomial/GAM/LOESS smoothers,
- survival curves and confidence bands,
- empirical CDF,
- two-dimensional binning and hexbin,
- contours and density contours,
- rolling/window summaries,
- cumulative sums and ranks,
- model prediction layers from externally supplied model results,
- uncertainty propagation for transformed values.

### 7.2 Do not conceal statistical assumptions

Each stat output should record metadata such as:

```json
{
  "method": "ordinary-least-squares",
  "confidence": 0.95,
  "interval": "mean-response",
  "grouping": ["treatment", "batch"],
  "n": 51,
  "dropped": 2
}
```

Tooltips, captions, inspectors, and exports can expose this metadata. A convenience method may choose defaults, but the resulting IR must be explicit.

### 7.3 Grouping rules

Grouping should be compiled, not guessed repeatedly. Default grouping can derive from mapped discrete aesthetics (`group`, color, fill, linetype, shape) and facets, but the compiler should store the resolved group key. Ambiguous grouping should produce an info diagnostic and a suggested explicit `group()` mapping.

### 7.4 Missing and invalid values

Every layer execution should report:

- rows in,
- rows out,
- nulls removed per required channel,
- non-finite values removed,
- log-domain violations,
- out-of-domain values clipped or censored,
- stat-specific omissions,
- renderer/mark reductions.

These are not console warnings. They are structured diagnostics and scene metadata.

---

## 8. Geoms and positions

### 8.1 Geom catalog

A professional initial catalog should cover:

- point, line, step, path,
- area, ribbon,
- bar, column, rect, tile,
- histogram and frequency polygon via stat/geom composition,
- rule, segment, arrow,
- errorbar, linerange, pointrange,
- boxplot and violin,
- density and contour,
- text, label, repel-label,
- rug,
- raster/image,
- hexbin,
- candlestick/OHLC where appropriate,
- geospatial point/path/polygon after coordinates exist.

Avoid “chart type” classes. A histogram is `stat_bin + geom_bar`; a regression chart is points + regression stat line + interval ribbon.

### 8.2 Position semantics

Positions must produce explicit bounds so geoms remain simple. For example, stacking should output `__position_ymin` and `__position_ymax`. Dodging should output slot offsets. Jitter must be seeded for deterministic exports.

The reference implementation includes identity, stack, fill, dodge, and seeded jitter.

### 8.3 Mark identity and interaction

Every emitted mark should carry:

- layer ID,
- stable datum key,
- source/field provenance,
- grouped row IDs or aggregate membership summary,
- accessible label,
- tooltip fields,
- selection payload.

For aggregate marks, the interaction payload should not pretend there is one source row. It should represent the aggregate group and stat output, with an optional action to reveal contributing rows.

---

## 9. Scales, coordinates, and guides

### 9.1 Scale objects are first-class

A trained scale must expose:

```ts
interface TrainedScale {
  channel: ScaleChannel;
  type: ScaleType;
  domain: JsonPrimitive[];
  range: JsonPrimitive[];
  ticks: Tick[];
  bandwidth?: number;
  map(value: unknown): number | string;
}
```

The authoring scale controls domain, range, limits, out-of-bounds behavior, transform, zero inclusion, nice values, reversal, padding, palette/scheme, unknown values, guide, and title.

### 9.2 Units

Units should be semantic metadata, not text pasted into labels. Rules:

- A shared positional scale may combine fields only if units are compatible or a declared conversion exists.
- Automatic titles render `Label (unit)` unless the user overrides the title.
- Converted units create a new field/provenance node.
- Secondary axes are allowed only as a declared invertible transform of the primary scale.
- Tooltips format values through the same unit formatter as guides.

Consider integrating a units library behind a narrow interface rather than embedding a large ontology in the plot compiler.

### 9.3 Time

Temporal handling needs:

- instant versus local date/time distinction,
- timezone metadata,
- UTC and local scales,
- calendar-aware tick intervals,
- DST-safe formatting,
- date truncation in the analytical backend,
- explicit parsing rather than repeated `Date.parse` guessing,
- interval/range channels.

### 9.4 Coordinates

Start with:

- Cartesian,
- flipped Cartesian,
- fixed aspect ratio.

Then add plugins for:

- polar,
- map projections,
- ternary,
- transformed coordinates.

Coordinate transforms occur after scale positioning and before final scene emission. Geospatial projections need their own topology, clipping, and graticule support; they should not be treated as ordinary x/y numeric scales.

---

## 10. Themes and professional output

### 10.1 Complete themes

A theme should be a complete value object, not CSS variables read deep inside a renderer. It must define:

- plot/panel backgrounds,
- foreground and muted colors,
- major/minor grids,
- axis lines/ticks/text/titles,
- title/subtitle/caption,
- facet strips,
- legend box and typography,
- palettes,
- default point/line/bar values,
- spacing.

The reference implementation includes professional, publication, and dark presets and allows targeted lambda overrides.

### 10.2 Export formats

Production outputs should include:

- SVG with embedded metadata and accessible text,
- PNG at requested dimensions/DPI,
- PDF with embedded fonts or controlled font substitution,
- Canvas for interactive raster rendering,
- WebGL/WebGPU for dense marks,
- scene JSON for debugging and reproducibility,
- data/analysis table export for each layer,
- complete plot-document JSON.

A hybrid export path is valuable: rasterize dense marks while preserving vector text, axes, and annotations.

### 10.3 Typography and font policy

Do not serialize or distribute font binaries. The document may specify font families and fallback stacks. Export backends should report substitutions. For reproducible publication output, operators can configure approved server-side fonts, but the plot artifact should record the resolved family and metrics fingerprint.

### 10.4 Color and accessibility

Color cannot be the only carrier for critical distinctions. Provide shape, dash, direct labels, facets, and patterns. Meaningful graphical objects should satisfy non-text contrast requirements; WCAG guidance uses a 3:1 threshold for necessary graphical boundaries and controls.[^wcag]

The system should include:

- color-vision-deficiency simulation in the inspector,
- palette contrast diagnostics,
- warnings when categories exceed distinguishable defaults,
- automatic fallback to color + shape for small category counts,
- accessible title and long description,
- a generated data summary/table,
- keyboard-navigable legend selections,
- semantic SVG grouping and focus order,
- reduced-motion behavior.

Observable Plot’s accessibility model is a useful practical reference for exposing ARIA labels and descriptions while keeping author control.[^observable-accessibility]

---

## 11. Renderer strategy

### 11.1 Backend selection

Do not select a backend from raw row count alone. Use estimated scene complexity:

```text
mark count
+ path vertex count
+ text count
+ interaction/hit-test requirements
+ transparency/overdraw estimate
+ export target
+ device capability
```

Suggested policy:

| Scene | Backend |
|---|---|
| publication/vector, modest marks | SVG |
| tens of thousands of simple marks | Canvas |
| hundreds of thousands/millions of points or tiles | WebGL/WebGPU |
| headless publication | SVG/PDF, possibly hybrid raster layers |

The document expresses preference and thresholds; the compiled render plan records the actual selection and reason.

### 11.2 Resolution-aware reduction

When data density exceeds display resolution, prefer analytical reduction over arbitrary truncation:

- aggregate into screen-space bins,
- hexbin or density,
- min/max envelope per pixel column for time series,
- LTTB or another documented line simplification for overview views,
- reservoir/stratified sampling for exploratory scatter plots,
- server-side tiles for very large data.

The system must label reduced/approximate output and make the method inspectable.

### 11.3 Hit testing

SVG can use element targeting for modest scenes. Canvas/WebGL should build spatial indices or encoded picking buffers. The hit-test result maps back to the same scene metadata and PBUI presentation object, so interactions remain renderer-independent.

### 11.4 Renderer parity

Test all backends against the scene contract:

- same panel geometry,
- same scale mapping within tolerance,
- same visible layers,
- same text content,
- same accessibility description,
- same clipping and z-order,
- documented differences for antialiasing and text metrics.

---

## 12. Interaction architecture

Interactions should be declarative nodes in the document and compiled into a signal/dataflow plan, following the same general separation that makes Vega’s runtime reactive.[^vegalite]

Initial interactions:

- tooltip,
- crosshair,
- point/category selection,
- interval brush,
- pan/zoom,
- legend filtering/highlighting,
- linked views,
- parameter controls.

A selection compiles to:

```ts
interface SelectionPlan {
  id: string;
  input: "pointer" | "keyboard" | "legend" | "control";
  projection: FieldId[];
  resolve: "global" | "union" | "intersect";
  empty: "all" | "none";
  outputs: SignalId[];
}
```

Signals can drive:

- filter transforms,
- scale domains,
- conditional aesthetics,
- annotations,
- external PBUI actions.

The authoring document stores the declaration, not event-handler closures.

---

## 13. Plugin system

### 13.1 Plugin boundaries

The delivered registry demonstrates stat, position, and geom plugins:

```ts
interface StatPlugin {
  id: string;
  compile(context: StatCompileContext): StatCompileOutput;
  execute(context: StatExecuteContext): StatExecuteOutput;
}

interface PositionPlugin {
  id: string;
  execute(context: PositionExecuteContext): PositionExecuteOutput;
}

interface GeomPlugin {
  id: string;
  requiredChannels: AestheticChannel[];
  validate?(context: GeomValidationContext): void;
  build(context: GeomBuildContext): SceneNode[];
}
```

Production should add registries for:

- transforms/functions,
- physical-plan lowerers,
- scales,
- coordinates/projections,
- guides,
- themes,
- interactions,
- renderers/exporters,
- migrations.

### 13.2 Namespacing and versioning

Plugin IDs should be namespaced:

```text
core:stat:summary
core:geom:ribbon
org.example:stat:survival
org.example:coord:ternary
```

A persisted document should record plugin requirements and compatible versions. Missing plugins produce a diagnostic and a non-destructive placeholder; the system must not silently reinterpret the layer.

### 13.3 Security

Persisted plugins must not inject arbitrary executable code into a document. Runtime code is installed through trusted packages or registered host modules. The document references plugin IDs and JSON options. Server execution should apply an allowlist and resource limits.

---

## 14. DataDrop-specific integration plan

### 14.1 Preserve the current strengths

Keep:

- server-authored typed table schema,
- explicit source coverage,
- `GraphicDocument` persistence mechanics and reducers,
- compiler diagnostics pattern,
- stable field identities and provenance,
- parameterized DuckDB lowering,
- one analytical runtime owner per workbench root,
- PBUI presentation semantics,
- pure model modules with no React imports.

### 14.2 Replace the visual seam

The immediate target should be:

```text
compileGraphicDocument
  currently: LogicalGraphic + LogicalView
  target:    LogicalDataGraph + LogicalPlot
```

`LogicalPlot` references relation values and stable fields. The chart hook should call:

```ts
const compiled = compilePlotDocument(document, environment, registry);
const result = await executor.execute(compiled.physicalPlan);
const scene = buildScene(compiled.visualPlan, result, viewport, metrics);
```

It should not call `buildPlotFromResult(result, AuthoringView, width, height)`.

### 14.3 Recommended module layout

```text
ui/src/plot/
  authoring/
    document.ts
    builder.ts
    migrations.ts
    legacy-v1.ts
  semantic/
    fields.ts
    expressions.ts
    diagnostics.ts
    compiler.ts
  logical/
    data.ts
    layers.ts
    scales.ts
    facets.ts
  physical/
    plan.ts
    duckdb.ts
    arrow.ts
    optimizer.ts
  runtime/
    coordinator.ts
    cache.ts
    execution.ts
  stats/
  positions/
  geoms/
  scales/
  guides/
  coordinates/
  layout/
  scene/
  renderers/
    svg.ts
    canvas.ts
    webgl.ts
  accessibility/
  testing/
```

Do not create all directories before call sites exist. Extract each subsystem as the corresponding pass is introduced.

### 14.4 Current file-by-file evolution

#### `ui/src/model/graphic.ts`

- Keep core scalar/physical types and expression concepts.
- Split data relation IR from plot IR.
- Expand `SemanticType` and `FieldSymbol` metadata.
- Replace `AuthoringView` with `PlotSpec` + `LayerSpec[]`.
- Add migration from v1.
- Make references ordinary annotation layers.

#### `ui/src/model/graphicAuthoring.ts`

- Replace mutable helpers with an immutable fluent builder over a private draft.
- Retain direct document-edit helpers for reducers and UI forms.
- Stop re-inspecting row values when authoritative schema exists.
- Add reusable builder combinators.

#### `ui/src/model/plot.ts`

Retire it in slices:

1. extract scales/ticks,
2. extract facet/layout planning,
3. extract geom emitters,
4. introduce scene types,
5. replace `buildPlotFromResult` with staged compile/execute/scene APIs,
6. leave a compatibility adapter until all call sites migrate.

#### `ui/src/analysis/compile.ts`

- Retain field aliases and parameter binding.
- Extend operation lowering.
- Compile only required DAG branches.
- Share common layer subplans.
- Return Arrow-friendly typed output metadata.
- Add plan explain output for the inspector.

#### `ui/src/analysis/runtime.ts`

- Prefer Arrow/IPC ingestion over NDJSON.
- Support cancellation and lazy record batches.
- Cache registered sources by content/schema fingerprint.
- Cache physical plans separately from result batches.
- Preserve current metrics and principal purge behavior.

#### `ChartPanel.tsx`

- Become a renderer host and interaction overlay.
- Receive `SceneGraph`, renderer choice, and event callbacks.
- Do no scale or mark arithmetic.
- Use one PBUI presentation bridge for renderer hit-test results rather than one React wrapper per dense mark.

---

## 15. Migration roadmap

### Phase 0 — freeze invariants

Before changing the document:

- add golden fixtures for current plots,
- record v1 document JSON fixtures,
- assert coverage/truncation propagation,
- assert stable field IDs survive every compiled view,
- record plot geometry for representative charts,
- establish performance baselines.

### Phase 1 — introduce v2 authoring types and adapter

- Add `datadrop.plot.document@2` beside v1.
- Implement pure v1 → v2 conversion.
- Store v2 for new plots behind a feature flag.
- Render converted v1 and native v2 through the same downstream path.

The delivered `src/datadrop-v1.ts` demonstrates this adapter. It orders the current transform chain, converts expressions and transforms, maps the root view to a layer, maps facets/scales, turns reference lines into rule layers, and reports unsupported information.

### Phase 2 — fix the stable-field seam

- Compile v2 mapping names to `FieldId`s.
- Change the plot builder to consume bound mappings and typed fields.
- Keep current four geoms initially.
- Remove name-based mapping validation from the render path.

This is the highest-value correctness change and should land before broad feature work.

### Phase 3 — layered logical plot

- Add multiple layers with mapping inheritance.
- Share relation execution across layers.
- Turn references into ordinary layers.
- Add `stat_identity` and `position_identity` explicitly.
- Preserve current output exactly through compatibility defaults.

### Phase 4 — scene graph and renderer host

- Introduce backend-neutral primitives.
- Port existing SVG output as the first interpreter.
- Move ChartPanel to scene hosting.
- Add Canvas for dense point/bar scenes.
- Retain PBUI via scene metadata and hit testing.

### Phase 5 — statistics and positions

Prioritize features that unlock scientific work:

1. summary + error bars/ribbons,
2. bin/histogram,
3. stack/fill/dodge/jitter,
4. regression/smoothers,
5. boxplot/density,
6. 2D bins/contours.

Lower group/aggregate/bin/window operations to DuckDB when possible. Use specialized kernels only when SQL is unsuitable.

### Phase 6 — scales, guides, and facets

- General x/y/color/fill/size/shape/opacity scales,
- fixed/free facet scales,
- guide merging,
- unit/time formatting,
- text measurement and label collision,
- manual palettes/domains/breaks.

### Phase 7 — performance and Arrow

- Arrow ingestion and result batches,
- incremental cache and cancellation,
- Canvas/WebGL backend policy,
- resolution-aware aggregation,
- hybrid exports,
- million-row benchmark suite.

### Phase 8 — interactive grammar

- compiled selections/signals,
- linked plots,
- brush-driven filters/domains,
- legend interaction,
- parameter controls,
- renderer-independent hit testing.

### Phase 9 — retire v1

Only after:

- all stored documents migrate,
- v1 fixture corpus converts without errors or has explicit exemptions,
- UI editors operate on v2,
- old permalinks remain readable,
- the compatibility renderer has no callers.

---

## 16. Testing strategy

### 16.1 Compiler tests

- migration golden files,
- name-to-ID binding,
- stale ID behavior,
- expression typing and nullability,
- unit compatibility,
- mapping inheritance,
- stat output schemas,
- scale inference,
- facet scale groups,
- plugin absence/version diagnostics.

### 16.2 Property tests

- builder operations preserve earlier builders,
- document JSON round-trips,
- deterministic fingerprints,
- scale monotonicity,
- inverse scale round-trips where defined,
- positions preserve totals,
- stack bounds do not overlap incorrectly,
- seeded jitter is reproducible,
- equivalent plans yield equivalent scenes.

### 16.3 Statistical tests

Use independently calculated fixtures for:

- means, variance, SE, confidence intervals,
- quantiles and boxplot fences,
- bin edges and counts,
- regression coefficients and intervals,
- density normalization,
- grouped/faceted behavior,
- missing-value handling.

Do not generate expected values from the implementation under test.

### 16.4 Scene and renderer tests

- scene-node geometry assertions,
- SVG DOM structure and accessibility text,
- Canvas command snapshots,
- cross-backend geometry parity,
- clipping/z-order,
- text-measurement fixtures,
- pixel diffs for a small reviewed gallery,
- browser tests for resizing and hit testing.

### 16.5 Performance tests

Measure separately:

- source registration,
- logical compile,
- physical compile,
- query execution,
- Arrow normalization,
- scale training,
- layout,
- scene emission,
- renderer draw,
- hit-test build,
- memory high-water marks.

Datasets should cover wide schemas, many categories, many facets, long time series, dense scatter, and large aggregate inputs.

---

## 17. Delivered TypeScript reference implementation

### 17.1 Package contents

```text
src/
  types.ts          authoring, logical, execution, scene types
  defaults.ts       themes, default document, table adapter
  expr.ts           serializable expression builder/interpreter
  builder.ts        immutable fluent API and nested configuration builders
  datadrop-v1.ts    migration adapter for current DataDrop document shape
  registry.ts       stat/position/geom plugin contracts
  compiler.ts       semantic compiler and scale inference
  transforms.ts     in-memory relational transform interpreter
  stats.ts          built-in statistical plugins
  positions.ts      built-in position plugins
  scales.ts         scale training, ticks, color interpolation, legends
  geoms.ts          scene emitters
  scene.ts          facet layout, guides, labels, scene construction
  svg.ts            SVG interpreter
  canvas.ts         Canvas HTML/script interpreter
  runtime.ts        logical execution orchestrator
  render.ts         compile → execute → scene → render façade
  index.ts          public API
examples/
  generate.ts       four scientific examples and artifact generation
test/
  compiler.test.ts
  migration.test.ts
  runtime.test.ts
  scales-registry.test.ts
output/
  SVG, PNG previews, Canvas HTML, authoring IR, scene IR, gallery
```

### 17.2 Implemented capabilities

- Immutable fluent builder with nested lambdas.
- Pure JSON v2 authoring document.
- Stable field IDs and semantic binding.
- Rich field schema: physical type, semantic type, role, unit, timezone, order, coverage.
- Expressions and parameters.
- Global and per-layer transforms:
  - filter,
  - mutate,
  - select,
  - aggregate,
  - sort,
  - limit/offset,
  - bin,
  - fold,
  - deterministic sample.
- Layer mapping inheritance and override.
- Aesthetics:
  - x/y/x2/y2,
  - xmin/xmax/ymin/ymax,
  - color/fill,
  - size/shape/opacity/stroke width,
  - group/order/label/weight/tooltip.
- Stats:
  - identity,
  - count,
  - bin,
  - summary with intervals,
  - linear regression with confidence ribbon,
  - density,
  - boxplot.
- Positions:
  - identity,
  - stack,
  - fill,
  - dodge,
  - seeded jitter.
- Geoms:
  - point,
  - line,
  - area,
  - bar,
  - ribbon,
  - error bar,
  - rule,
  - text,
  - boxplot.
- Scales:
  - linear,
  - log,
  - symlog,
  - sqrt/power core,
  - time/UTC,
  - band/point/ordinal,
  - categorical/sequential/diverging.
- Facet wrap/grid with fixed/free scale declarations.
- Cartesian and flipped coordinates.
- Professional/publication/dark themes.
- Titles, subtitles, captions, axis labels, legends.
- Backend-neutral scene graph.
- Accessible SVG with title/description metadata.
- Canvas interpreter.
- Automatic backend selection metadata.
- Namespaced stat/position/geom plugin registry.
- Current DataDrop v1 migration adapter.
- Structured diagnostics and execution metrics.

### 17.3 Generated examples

#### Regression, confidence intervals, raw observations, and facets

![Regression facets](output/01-regression-facets.png)

Artifacts:

- `output/01-regression-facets.svg`
- `output/01-regression-facets.canvas.html`
- `output/01-regression-facets.document.json`
- `output/01-regression-facets.scene.json`

#### Summary bars with confidence intervals and dodge

![Summary error bars](output/02-summary-errorbars.png)

#### Faceted histogram

![Histogram facets](output/03-histogram-facets.png)

#### Boxplots with deterministic jittered observations

![Boxplot jitter](output/04-boxplot-jitter.png)

### 17.4 Verification

The delivered package was verified with:

```bash
npm test
npm run examples
```

Result at delivery:

```text
11 tests passed
0 failed
4 example documents compiled and rendered
0 example warnings
```

The examples generated:

| Example | Scene marks |
|---|---:|
| regression facets | 212 |
| summary + error bars | 16 |
| histogram facets | 51 |
| boxplot + jitter | 173 |

### 17.5 Deliberate limitations of the reference

The implementation proves the architecture but does not yet provide every production capability in this report:

- Data execution is an in-memory interpreter, not the DataDrop DuckDB physical backend.
- The compiler does not yet optimize a shared physical DAG across equivalent layer stats.
- Joins, pivots, windows, and multi-relation transforms are not implemented.
- Interactions are represented in the authoring document but not compiled into a live signal runtime.
- Canvas output is a self-contained HTML interpreter; WebGL/WebGPU and PDF exporters are not implemented.
- PNG previews were generated from SVG for review; there is no built-in PNG encoder.
- Text metrics use deterministic approximations rather than a pluggable font measurement service.
- Label collision avoidance, secondary axes, polar/geospatial coordinates, patterns, and rich text are not implemented.
- Regression uses a normal critical-value approximation and ordinary least squares; it is not a general statistical modeling framework.
- Free facet scale declarations exist, but production-grade independent panel sizing and complete guide duplication need further work.
- The v1 migration adapter intentionally warns and degrades legacy casts because the reference v2 expression core does not yet model physical casts.

These gaps are bounded and correspond directly to the extension seams described above.

---

## 18. Concrete recommendation for the first production pull requests

### PR 1: stable visual field binding

- Add a compiled visual mapping keyed by `FieldId`.
- Pass it to the existing plot builder.
- Remove use of `AuthoringView.encodings[channel].name` from geometry generation.
- Add rename/stale-field tests.

This fixes correctness without changing visible features.

### PR 2: explicit one-layer v2 document

- Add v2 document types and v1 adapter.
- Represent the current view as one layer with identity stat/position.
- Preserve current UI behavior and serialization.
- Store migration diagnostics.

### PR 3: scene graph and SVG interpreter

- Convert current `Plot` geometry to scene nodes.
- Move SVG element selection out of `ChartPanel`.
- Keep current output visually equivalent.
- Add accessible title/description and scene JSON snapshots.

### PR 4: multiple layers and rule annotations

- Support shared relation/mapping/scales.
- Move reference lines to rule layers.
- Render raw points + line + area/ribbon combinations.

### PR 5: summary statistic and error-bar geom

- Implement stat output schemas and `afterStat` binding.
- Lower summary aggregation to DuckDB.
- Add error bar/ribbon geoms and dodge position.
- Ship a scientific gallery fixture.

This sequence creates value early while keeping each change reviewable.

---

## 19. Architectural decisions

### AD-1 — The persisted format is data-only

No callbacks, class instances, DOM nodes, or renderer objects in the document.

### AD-2 — Builders are immutable at the public boundary

Nested builders mutate only private drafts. Reusable functions compose builders.

### AD-3 — Stable identity wins over display name

Names are for authoring and labels. `FieldId` is the compiled identity.

### AD-4 — Layers are the composition primitive

Do not create an inheritance tree of chart types.

### AD-5 — Stat, geom, and position are independent

Convenience methods may pair defaults, but the IR stores each component.

### AD-6 — The physical plan is separate from the visual plan

DuckDB execution and scene generation can evolve independently.

### AD-7 — The scene graph is the only renderer input

Renderers do not recompile analytical or scale semantics.

### AD-8 — Coverage and omissions are first-class

Every bounded, sampled, dropped, clipped, pooled, or rasterized result is inspectable.

### AD-9 — Defaults are centralized and overridable

No hidden hard-coded palette, cap, or tick policy inside a geom.

### AD-10 — Extensions are referenced by namespaced IDs

Documents stay portable; runtime code remains trusted and installed separately.

### AD-11 — Determinism is a feature

Seed jitter/sampling, stable category order, stable fingerprints, and record backend/font differences.

### AD-12 — Accessibility is compiled, not appended

Descriptions, mark semantics, contrast diagnostics, keyboard behavior, and data alternatives belong in the plan.

---

## 20. Final assessment

DataDrop is unusually well positioned for this evolution. It is not starting from a chart component; it already has a document, a semantic relational compiler, a physical SQL compiler, explicit data coverage, and a pure plot function. The primary risk is allowing the current plot builder to become the permanent home for every visual feature. That would erase the compiler structure just as the feature set begins to require it.

The recommended v2 system keeps the current strengths and makes the visual side symmetrical with the analytical side:

```text
relation authoring  → typed logical relation  → physical DuckDB plan
plot authoring      → typed logical plot      → scene/render plan
```

The fluent API should remain pleasant and opinionated. The compiled document should remain explicit and portable. The runtime should remain pluggable. The output should be scientifically honest, reproducible, accessible, and suitable for both interactive exploration and publication.

The delivered TypeScript package demonstrates that these goals are compatible rather than competing.

---

## References

### Grammar and plotting systems

[^wickham]: Hadley Wickham, [“A layered grammar of graphics”](https://vita.had.co.nz/papers/layered-grammar.html), *Journal of Computational and Graphical Statistics* 19(1), 2010.

[^ggplot-layer]: ggplot2 documentation, [“Create a new layer”](https://ggplot2.tidyverse.org/reference/layer.html). The layer contract combines data, mapping, statistical transformation, geom, and position, with mapping inheritance and overrides.

[^vegalite]: Vega-Lite, [“A Grammar of Interactive Graphics”](https://vega.github.io/vega-lite/). Vega-Lite uses a concise declarative specification, compiler-generated scales/axes/legends, transformations, layers, multi-view composition, and selections.

[^observable-marks]: Observable Plot, [“Marks”](https://observablehq.com/plot/features/marks). Plot composes charts from layered marks, data-space channels, inferred scales, and tidy or columnar data.

[^observable-accessibility]: Observable Plot, [“Accessibility”](https://observablehq.com/plot/features/accessibility).

### Data and execution

[^duckdb-ingestion]: DuckDB, [“Data Ingestion — DuckDB-Wasm”](https://duckdb.org/docs/clients/wasm/data_ingestion). The API includes Arrow table and Arrow IPC stream ingestion in addition to CSV and JSON.

[^duckdb-wasm]: DuckDB, [“DuckDB Wasm”](https://duckdb.org/docs/stable/clients/wasm/overview). The browser client runs in WebAssembly and documents single-threaded defaults and browser memory constraints.

[^arrow]: Apache Arrow, [project overview](https://arrow.apache.org/). Arrow defines a language-independent columnar memory format for analytical operations and efficient interchange.

### Accessibility

[^wcag]: W3C WAI, [“Understanding Success Criterion 1.4.11: Non-text Contrast”](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html).

### DataDrop source baseline

- [`ui/src/model/graphic.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/src/model/graphic.ts)
- [`ui/src/model/graphicAuthoring.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/src/model/graphicAuthoring.ts)
- [`ui/src/model/plot.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/src/model/plot.ts)
- [`ui/src/analysis/compile.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/src/analysis/compile.ts)
- [`ui/src/analysis/runtime.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/src/analysis/runtime.ts)
- [`ui/src/components/organisms/ChartPanel/ChartPanel.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/src/components/organisms/ChartPanel/ChartPanel.tsx)
- [`ui/test/plot.test.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/06fe133876fdb45ffa33f9f6257b29a68f437f50/ui/test/plot.test.ts)
