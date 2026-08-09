# DataDrop Professional Plotting Suite — TypeScript Reference

An executable reference architecture for evolving `go-go-datadrop` into a layered, scientific grammar-of-graphics system.

The package is dependency-free at runtime and targets Node.js 20+. TypeScript is the only development dependency.

## Deliverables

- [`datadrop-plotting-suite-report.md`](datadrop-plotting-suite-report.md): repository audit, architecture, compiler design, performance strategy, migration plan, and implementation assessment.
- `src/`: TypeScript implementation.
- `examples/generate.ts`: four scientific examples.
- `output/gallery.html`: generated gallery.
- `output/*.document.json`: serializable authoring IR.
- `output/*.scene.json`: renderer-neutral scene IR.
- `output/*.svg`: accessible vector output.
- `output/*.canvas.html`: Canvas interpreter output.
- `output/*.png`: review previews generated from the SVG outputs.

## Run

```bash
npm install
npm run verify
```

Individual commands:

```bash
npm run build
npm test
npm run examples
```

## API example

```ts
import {
  plot,
  renderProgram,
  tableFromRows,
} from "./src/index.js";

const table = tableFromRows(
  "experiment",
  [
    { time: 0, response: 4.2, treatment: "control" },
    { time: 1, response: 5.1, treatment: "control" },
    { time: 0, response: 4.4, treatment: "active" },
    { time: 1, response: 7.8, treatment: "active" },
  ],
  [
    { name: "time", semanticType: "quantitative", unit: "h" },
    { name: "response", semanticType: "quantitative", unit: "µmol/L" },
    { name: "treatment", semanticType: "nominal" },
  ],
);

const chart = plot(table)
  .mapping((m) => m
    .x("time")
    .y("response")
    .color("treatment")
    .group("treatment"))
  .layer((layer) => layer
    .name("observations")
    .point((geom) => geom.radius(3).opacity(0.45)))
  .layer((layer) => layer
    .name("fit")
    .stat((stat) => stat.linearRegression({ confidence: 0.95 }))
    .line((geom) => geom.strokeWidth(2)))
  .labels((labels) => labels
    .title("Experimental response")
    .x("Time (h)")
    .y("Response (µmol/L)"))
  .theme((theme) => theme.preset("publication"));

const rendered = renderProgram(chart.program());
if (!rendered.svg) {
  throw new Error(rendered.compile.diagnostics.map((d) => d.message).join("; "));
}

console.log(chart.toJSON());  // versioned authoring IR
console.log(rendered.scene);  // backend-neutral scene IR
console.log(rendered.svg);    // accessible SVG
```

## Builder semantics

`PlotBuilder` is immutable. Each top-level call returns a new builder. Configuration lambdas mutate only a private cloned draft and are not stored in the document.

```ts
const base = plot(table).theme((t) => t.preset("publication"));
const points = base.layer((l) => l.point());
const lines = base.layer((l) => l.line());

// base, points, and lines are independent documents.
```

Expressions follow the same pattern. A callback builds a serializable AST:

```ts
const filtered = plot(table)
  .parameter("minimum", 5)
  .transform((t) => t.filter((e) => e.and(
    e.gte("response", e.parameter("minimum")),
    e.isFinite("response"),
  )));
```

## Pipeline

```text
PlotDocument v2
  → compilePlot
  → LogicalPlot
  → executeProgram
  → ExecutionResult
  → buildScene
  → SceneGraph
  → sceneToSvg / sceneToCanvasHtml
```

The in-memory executor is provided for tests and examples. Production DataDrop should plug the logical/physical plan into its existing DuckDB-Wasm runtime and use Arrow batches at the data boundary.

## Current DataDrop migration

`migrateGraphicDocumentV1()` converts the current `datadrop.gog.document@1` shape into the v2 layered document:

```ts
const migrated = migrateGraphicDocumentV1(legacyDocument, table);
const rendered = renderProgram(migrated.program);
```

The adapter:

- orders the current transform chain from relation edges,
- converts filter/extend/project/aggregate/sort/limit,
- converts the expression core,
- maps the root view to a layer,
- maps the legacy facet and y scale,
- converts reference lines to rule layers,
- reports unsupported or lossy cases through diagnostics.

## Built-ins

### Geoms

`point`, `line`, `area`, `bar`, `ribbon`, `errorbar`, `rule`, `text`, `boxplot`

### Statistics

`identity`, `count`, `bin`, `summary`, `linearRegression`, `density`, `boxplot`

### Positions

`identity`, `stack`, `fill`, `dodge`, `jitter`

### Scales

`linear`, `log`, `symlog`, `sqrt`, `pow`, `time`, `utc`, `band`, `point`, `ordinal`, `categorical`, `sequential`, `diverging`

### Themes

`professional`, `publication`, `dark`

## Plugins

```ts
import { PlotRegistry, type StatPlugin } from "./src/index.js";

const stat: StatPlugin = {
  id: "org.example:stat:custom",
  compile(context) {
    return { schema: context.inputSchema, mapping: context.mapping };
  },
  execute(context) {
    return { rows: context.rows, schema: context.schema, mapping: context.mapping };
  },
};

const registry = new PlotRegistry();
registry.registerStat(stat);
const rendered = renderProgram(chart.program(), registry);
```

Persisted documents contain only plugin IDs and JSON options. Runtime plugin code is registered separately.

## Verified output

The current package passes 11 Node tests and generates four example plots without compiler or scene warnings.

Open `output/gallery.html` after running `npm run examples`.

## Scope boundary

This is a substantial reference implementation, not a finished replacement for DataDrop’s production browser engine. The report identifies the remaining work: DuckDB physical lowering for the new operators, Arrow-native execution, shared-plan optimization, live interactions, WebGL/WebGPU, PDF/PNG export, text measurement, label collision, geospatial coordinates, and additional scientific statistics.
