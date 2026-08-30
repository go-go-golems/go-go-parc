---
title: "Hyperslop Plot: Completing the Compiler from Mechanical Scenes to Plot Algebra"
aliases:
  - Hyperslop Plot HSPLOT-005 through HSPLOT-010 Project Report
  - Mechanical Scenes to Plot Algebra
  - Hyperslop Plot Compiler Deep Dive
  - Plot Grammar Completion Report
tags:
  - article
  - project-report
  - plotting
  - grammar-of-graphics
  - typescript
  - react
  - architecture
status: active
type: article
created: 2026-08-30
repo: /home/manuel/workspaces/2026-08-24/use-optkit/plot
source_tickets:
  - HSPLOT-005
  - HSPLOT-006
  - HSPLOT-007
  - HSPLOT-008
  - HSPLOT-009
  - HSPLOT-010
---

# Hyperslop Plot: Completing the Compiler from Mechanical Scenes to Plot Algebra

`@hyperslop-systems/plot` is a serializable statistical-graphics compiler. A caller supplies a `PlotDocument`, a typed schema, bounded rows, and a viewport. The package validates and normalizes the document, evaluates derived variables, executes statistics and positions, trains scales, plans geometry and guides, applies coordinate transforms, projects structured semantics, lowers a renderer-neutral scene, and finally lets a host render that scene. React is one host boundary. It is not the grammar, compiler, planner, or semantic model.

This report explains the completed HSPLOT-005 through HSPLOT-010 program. It begins where HSPLOT-003 and HSPLOT-004 left the system: one canonical grammar, one deterministic `NormalizedGrammar`, explicit statistics and geometry stages, and renderer-neutral `PlotSemantics`. It then follows the changes that made presentation geometry complete, authoring functional, compact plots product-ready, guides and annotations configurable, coordinates extensible, and variables algebraic. The emphasis is not the list of features. The emphasis is how the implementation preserved one execution path while increasing the expressive power of the public language.

> [!summary]
> - HSPLOT-005 moved presentation measurement and guide geometry into a complete serializable `PlotPlan`, leaving scene construction as mechanical lowering.
> - HSPLOT-006 added a React-free functional authoring package whose helpers construct ordinary canonical documents and never invoke a private compiler path.
> - HSPLOT-007 proved parity in Datalab and RAG-TTC, replaced a hand-written operational SVG with ordinary grouped line grammar, and hardened 120×24 sparklines through browser evidence and benchmarks.
> - HSPLOT-008 made axes, legends, and annotations first-class serializable components whose geometry and semantics are resolved before rendering.
> - HSPLOT-009 introduced transpose and polar coordinates as late geometry transforms. Ordinary stacked bars become sector paths without a pie-chart geometry or renderer branch.
> - HSPLOT-010 added finite derived-variable expressions and cross/nest/blend/unity algebra that lower before statistics into the existing normalized composition.
> - The completed system passes 133 tests across 22 files, typecheck, lint, production and Storybook builds, packed author-only and React consumer tests, tarball inspection, browser inspection, and six clean ticket doctors.

## 1. The engineering problem

A statistical plot combines decisions with different semantics and different lifetimes. Variables identify values. Composition assigns those variables to dimensions, groups, and facets. Statistics derive rows or intervals. Positions alter geometric relationships such as stacking or dodging. Scales map domains into visual ranges. Coordinates transform geometric space. Guides explain scales. Layout reserves display regions. A scene records drawing primitives. A renderer paints those primitives. An application owns data acquisition, product state, commands, and domain-specific continuity rules.

The system becomes difficult to reason about when one phase performs work that belongs to another. A scene builder that measures axis labels is no longer a mechanical scene builder. A color mapping that silently creates line groups is no longer only an aesthetic mapping. A sparkline component that bypasses the ordinary line geometry creates a named-chart path. A polar renderer that interprets rectangles as sectors duplicates geometry semantics below planning. A derived-variable callback embedded in a document breaks serialization and makes diagnostics dependent on runtime closures.

The project therefore adopted a strict rule: every capability must enter through the canonical language or through an explicit compiler stage. Convenience APIs may construct the language. They may not create another language. New runtime behavior may extend compilation, data materialization, planning, coordinate transformation, semantics, or scene lowering. It may not hide in React or SVG.

The rule produced a stable set of invariants:

| Invariant | Consequence |
|---|---|
| One canonical `PlotDocument` | Literal objects, helpers, presets, adapters, and persisted JSON share one schema. |
| One `compileGrammar` boundary | Every authoring form receives identical validation and diagnostics. |
| Deterministic normalized IR | Equal document and schema inputs produce equal serializable compiler output. |
| Explicit grouping and facets | Appearance does not silently alter statistical identity. |
| Complete planning | Scene lowering receives final geometry rather than analytical intent. |
| Renderer-neutral semantics | Meaning can be inspected without reading SVG. |
| React-free core and author package | Non-React consumers can compile, plan, inspect, and package plots. |
| Diagnostics instead of approximation | Unsupported or invalid combinations fail at a stable path. |
| No named-chart branches | Sparklines and polar sectors arise from ordinary grammar composition. |

These invariants are executable. `src/architecture.test.ts` scans production sources to prevent imports and symbols that would violate them. The package tests compare literal and helper-authored documents, serialize normalized grammar and plans, inspect generated scenes, validate tarballs in clean consumers, and render Storybook specimens in a browser.

## 2. The completed pipeline

The final execution path contains one surface grammar and a sequence of typed transformations. HSPLOT-010 inserted immutable data materialization before statistics, but did not change the planner’s responsibility. HSPLOT-009 inserted coordinate transformation after scaled Cartesian geometry, but did not change statistical variables or scale domains. HSPLOT-008 enriched guide and annotation planning, but did not move presentation policy into the renderer.

```mermaid
flowchart LR
    DOC[PlotDocument] --> COMPILE[compileGrammar]
    SCHEMA[PlotSchema] --> COMPILE
    COMPILE --> IR[NormalizedGrammar]
    IR --> MATERIALIZE[materializePlotData]
    ROWS[PlotData] --> MATERIALIZE
    MATERIALIZE --> PLAN[planPlot]
    PLAN --> STATS[statistics]
    STATS --> POS[position adjustment]
    POS --> SCALE[scale training]
    SCALE --> GEOM[geometry planning]
    GEOM --> COORD[coordinate transform]
    COORD --> PLOTPLAN[PlotPlan]
    PLOTPLAN --> SEM[PlotSemantics]
    PLOTPLAN --> SCENE[buildScene]
    SCENE --> SVG[SvgRenderer]
    SVG --> HOST[PlotHost]

    style IR fill:#805bd7,color:#f3f3ef
    style PLOTPLAN fill:#2db878,color:#050607
    style SEM fill:#f2ad00,color:#050607
```

The surface document remains plain data:

```ts
interface PlotDocument {
  format: "hyperslop.plot";
  version: 1;
  id: PlotId;
  description?: string;
  variables: Readonly<Record<VariableId, VariableSpec>>;
  composition: CompositionSpec;
  layers: readonly LayerSpec[];
  scales?: ScaleMap;
  coordinate?: CoordinateSpec;
  presentation?: PresentationSpec;
  annotations?: readonly AnnotationSpec[];
  limits?: RenderLimits;
  metadata?: Readonly<Record<string, JsonValue>>;
}
```

The document does not contain functions, React elements, DOM nodes, SVG commands, runtime registries, or application state. Branded IDs improve TypeScript checking while serializing as ordinary strings. `ValueRef` values point to variables, constants, or named after-stat outputs. Layer composition uses explicit inheritance, replacement, and `null` clearing. Groups and facets are ordered lists of values rather than secondary effects of aesthetic mappings.

Compilation resolves this surface into `NormalizedGrammar`. Every enabled layer owns its effective dimensions, groups, facets, statistic, geometry, position, and aesthetics. Variables are deterministic. Presentation states are normalized. Coordinate defaults are concrete. Annotation references are compiled. Derived-variable and algebra programs are retained as bounded data programs, not functions. Source indexes and canonical document paths survive normalization so diagnostics remain useful.

The planner does not import `PlotDocument`. It receives normalized contracts plus materialized rows and a viewport. The scene builder does not import the compiler, scales, presentation resolver, or layout functions. The SVG renderer does not understand statistics, algebra, or polar coordinates. This separation is the principal result of the project.

## 3. HSPLOT-005: complete planning and mechanical scenes

HSPLOT-005 addressed the remaining ambiguity between planning and scene construction. Before this phase, the system had a normalized grammar and explicit analytical stages, but `buildScene` still decided enough presentation geometry that it was not purely mechanical. Axis lines, grids, legend positions, title placement, frame ownership, and compact-layout constraints needed one authoritative owner.

The solution was a complete serializable `PlotPlan`. Planning now resolves the plot title, content bounds, plot bounds, frame, panels, positional guides, legends, annotation geometry, statistics metadata, coordinate metadata, and final mark geometry. Scene lowering consumes these values and translates them into generic scene nodes.

```mermaid
flowchart TD
    PRES[CompiledPresentation] --> RESOLVE[resolvePresentation]
    RESOLVE --> MEASURE[measureFacetLayout]
    MEASURE --> PANELS[panel bounds]
    PANELS --> GUIDES[planned axes and legends]
    PANELS --> MARKS[planned layer geometry]
    GUIDES --> PLAN[complete PlotPlan]
    MARKS --> PLAN
    PLAN --> LOWER[buildScene]
    LOWER --> NODES[line rect path symbol text group]
```

### 3.1 Presence is a three-state contract

Presentation uses explicit presence values:

```ts
type Presence<T> =
  | { kind: "auto" }
  | { kind: "none" }
  | { kind: "configured"; options: T };
```

`auto` asks package policy to decide whether the component exists. `none` suppresses it. `configured` supplies bounded declarative options. The distinction matters because a scale and a guide are not the same object. A hidden color legend does not disable the color scale. A compact sparkline may use operational x and y scales while suppressing every explanatory guide.

The normalized presentation resolver makes these decisions before layout. Layout then receives concrete title, x guide, y guide, legends, frame, and padding values. There is no need for SVG or CSS to infer whether space should be reserved.

### 3.2 Compact layout is a real layout mode

The old layout imposed a fixed minimum viewport that made tiny plots impossible. HSPLOT-005 removed the 160×120 floor and made component presence determine reservations. A 120×24 sparkline with two pixels of padding and no title, guides, legends, or frame receives a 116×20 content and panel rectangle:

```json
{
  "contentBounds": { "x": 2, "y": 2, "width": 116, "height": 20 },
  "panelBounds": [{ "x": 2, "y": 2, "width": 116, "height": 20 }]
}
```

This is not a CSS scaling trick. The planner computes geometry for the requested viewport. The SVG viewBox and host dimensions then represent the same compact plot.

### 3.3 The plan has no first-panel aliases

Earlier plan types exposed convenience aliases such as root `panel`, `xScale`, `yScale`, `axes`, and `layers`. Those aliases made the first panel structurally privileged and invited downstream code to bypass facets. HSPLOT-005 removed them. Consumers use `plan.panels`, and each planned panel carries its own scales, layers, facet key, strip, and bounds.

This removal was deliberate. No compatibility shim preserved the aliases. Tests and documentation were updated to the canonical structure. `src/architecture.test.ts` now inspects the `PlotPlan` interface and fails if those root aliases return.

### 3.4 Scene lowering is mechanical

`buildScene` translates planned axis segments, tick labels, grid segments, swatches, paths, rectangles, symbols, and text into scene nodes. It does not train scales, inspect normalized grammar, measure labels, decide component presence, or compute legend domains.

The host CSS was also constrained. It cannot restore a border or background that the plan omitted. Frame ownership belongs to planning and scene lowering, not to a viewport stylesheet.

The result is a useful review boundary:

```text
If geometry is wrong in PlotPlan, inspect compilation or planning.
If PlotPlan is right and SceneGraph is wrong, inspect mechanical lowering.
If SceneGraph is right and pixels are wrong, inspect the renderer or host theme.
```

This separation became essential in HSPLOT-007, where the scene was valid but a pale fallback stroke made marks nearly invisible on a white background.

## 4. HSPLOT-006: a functional authoring package without a second language

The canonical document is explicit by design. Repeating every discriminator and nested object is useful for fixtures and storage, but application code benefits from constructors. HSPLOT-006 added `@hyperslop-systems/plot/author` as a separate package entrypoint.

The author package contains pure functions. It has no classes, fluent state, mutable builders, registries, closures, side effects, compiler imports, React imports, or host imports. Each helper returns canonical grammar data.

```ts
const document = plot({
  id: plotId("response-trend"),
  variables: {
    [at]: variable.field(fieldId("observed_at")),
    [value]: variable.field(fieldId("response")),
    [treatment]: variable.field(fieldId("treatment")),
  },
  composition: composition.cartesian({
    x: value.variable(at),
    y: value.variable(value),
    groups: [value.variable(treatment)],
  }),
  layers: [
    layer({
      id: layerId("trend"),
      stat: stat.identity(),
      geom: geom.line({ width: 2 }),
      position: position.identity(),
      mapping: { color: value.variable(treatment) },
    }),
  ],
});
```

The output is equal to an independently written literal document. It follows the same compiler path and produces the same diagnostics. Compile-time vocabulary maps use TypeScript discriminated unions to expose drift when a statistic, geometry, position, scale, or coordinate variant is added.

### 4.1 Sparkline is an expansion, not a geometry

The `sparkline()` preset is the strongest proof of the authoring rule. It creates variables, explicit composition, a line layer, optional grouping, optional y-domain configuration, Cartesian coordinates, and compact presentation. It does not create `geom.sparkline`, a named-chart tag, a preset compiler, or a renderer mode.

Conceptually, the expansion is:

```ts
function sparkline(input): PlotDocument {
  return plot({
    id: input.id,
    variables: explicitFieldVariables(input),
    composition: composition.cartesian({
      x: value.variable(input.x),
      y: value.variable(input.y),
      groups: input.group ? [value.variable(input.group)] : [],
    }),
    layers: [
      layer({
        id: layerId(`${input.id}:line`),
        stat: stat.identity(),
        geom: geom.line(),
        position: position.identity(),
      }),
    ],
    coordinate: coordinate.cartesian(),
    presentation: presentation.compact(),
  });
}
```

Tests prove helper-versus-literal equality, JSON round trips, absence of functions and symbols, empty input behavior, one-point behavior, flat domains, sparse groups, and equal invalid-document diagnostics.

### 4.2 Packaging is part of the architecture

A source-level import graph is not enough to prove that the author package is React-free. The validation process packs the actual tarball, installs it in a clean plain-JavaScript project with peer dependencies omitted, renders a plot, and verifies that no React directory was installed. A second clean consumer installs React and builds the host package.

This caught practical concerns that unit tests do not cover:

- nested declaration files must ship;
- `author.d.ts` and `author/index.d.ts` must both be reachable;
- exports must resolve from the tarball rather than workspace aliases;
- the author chunk must not import host code accidentally;
- package metadata must support both non-React and React consumers.

By the final HSPLOT-010 audit, the author package also covered guides, annotations, transpose, polar, derived variables, transforms, and algebra while retaining the same packaging proof.

## 5. HSPLOT-007: parity is behavioral, visual, and operational

A grammar package is not complete when isolated fixtures pass. Existing applications encode product semantics that must survive migration. HSPLOT-007 audited Datalab and RAG-TTC, built a parity matrix, added compact Storybook states, benchmarked repeated small plots, and inspected actual browser output.

### 5.1 Product adapters own product rules

RAG-TTC’s durable progress display contains phase changes, resets, gaps, unknown totals, stale state, rate, ETA, and terminal-state text. The plot package should not infer those concepts from missing values. The product adapter detects continuity and emits explicit segment groups. Plot then renders ordinary grouped line grammar.

```mermaid
flowchart LR
    EVENTS[durable work events] --> PROJECT[progress projection]
    PROJECT --> SEGMENTS[explicit phase reset gap segments]
    SEGMENTS --> ROWS[plot rows with segment group]
    ROWS --> SPARK[sparkline PlotDocument]
    SPARK --> HOST[120×24 PlotHost]
    PROJECT --> TEXT[rate ETA phase stale terminal text]
```

The migration replaced a hand-written 640×160 SVG with a 24-pixel `PlotHost` while preserving adjacent operational text and state behavior. Domain gap/reset ownership remained in RAG-TTC. No discontinuity inference entered Plot.

Datalab adapters were ported directly to the canonical grammar. A stale keyboard-routing expectation surfaced during the full consumer suite: Shift+Mod+K was implemented and independently tested as rebalancing, while one old test expected the launcher. The test was corrected to the existing product contract rather than changing unrelated behavior under a plotting task.

### 5.2 Browser inspection found defects that structural tests missed

The first grouped sparse sparkline had a valid path, finite coordinates, and no diagnostic. Its computed stroke was `rgb(243, 243, 239)` on white. The neutral mark fallback was effectively invisible. The fix changed unmapped marks to:

```css
var(--hs-plot-foreground, #171916)
```

The renderer-neutral scene still carries a CSS variable string, which is serializable. Theme resolution remains a host concern.

One-point line groups exposed a second issue. A path containing only `M x y` has no visible extent. Planning now carries `singlePointRadius`, and scene lowering emits an ordinary symbol for a group containing exactly one datum. This is a line-geometry lowering rule, not a sparkline special case.

Storybook wrapper dimensions exposed a third issue. A 120×24 viewBox initially expanded across the full Storybook canvas, producing a visually large specimen. The story now constrains the wrapper to 120 pixels, and browser inspection confirms a 23.99-pixel rendered height.

These findings establish a validation rule: scene validity and browser visibility are separate properties. Both must be tested.

### 5.3 Benchmark evidence rejected premature caching

The benchmark harness measures construction and rendering for 1, 20, and 100 compact plots, including document and data reuse. Representative medians were approximately:

| Scenario | Median time |
|---|---:|
| Construct and render 1 | 0.145 ms |
| Construct and render 20 | 1.33 ms |
| Construct and render 100 | 6.35 ms |
| Reused document across 100 datasets | 5.24 ms |

These measurements did not justify a cache. A cache would require identity, invalidation, memory, and lifecycle contracts that the package did not otherwise need. The decision was evidence-based: preserve the simple deterministic pipeline until measured pressure requires another design.

## 6. HSPLOT-008: configured guides are grammar components

HSPLOT-008 extended presentation from `auto` and `none` into bounded configured axes and legends, then added document-owned annotations. The implementation preserved the rule that scales are operational mappings while guides are explanatory components.

### 6.1 Axis configuration

An axis can configure:

- label;
- side (`top` or `bottom` for x, `left` or `right` for y);
- automatic tick count or explicit tick values;
- number, percent, or temporal formatting;
- no grid or major grid.

The compiler validates dimension participation, supported sides, positive automatic counts, explicit value types, declared-domain membership, formatter compatibility, and bounded fractional digits. Formatting is a closed JSON union. There is no formatter callback.

Explicit temporal ticks arrive as ISO strings but temporal scales operate on numeric milliseconds. Planning parses accepted values, maps them through the existing scale, formats them through a bounded `Intl.DateTimeFormat` configuration, and preserves the exact configured tick set. Automatic tick generation may produce more “nice” ticks than requested, so configured automatic counts deterministically select at most the requested count while retaining endpoints.

### 6.2 Legend configuration and compatibility

Legends configure title, vertical or horizontal orientation, explicit value order, reversal, and maximum entries. Layout reserves one right column for vertical legends and deterministic bottom rows for horizontal legends.

Guide merging required a semantic identity rule. The first implementation compared channel-specific scale specifications too strictly. Compatible color, fill, and shape explanations for the same variable split into five guides instead of the previous two. The final compatibility key requires:

- the same mapped variable identity;
- the same resolved domain and order;
- the same orientation;
- the same title.

Different aesthetic families may explain the same semantic variable and ordered domain. They can therefore share one guide. This rule preserved existing scale-family tests while making configured ordering operational.

### 6.3 Stable annotations

Annotations are document-owned values with stable IDs:

```ts
type AnnotationSpec =
  | RuleAnnotation
  | TextAnnotation
  | RegionAnnotation
  | PointAnnotation;
```

Each annotation records intent (`reference`, `target`, `limit`, or `note`), optional facet selection, and bounded appearance (`tone`, `emphasis`, `dash`). Anchors are data-relative, datum-relative, or panel-relative. Panel coordinates use x left-to-right and y bottom-to-top, consistent with plot coordinates.

Compilation validates IDs, duplicates, references, panel fractions, and region endpoint coordinate spaces. Planning resolves data values through panel scales, maps panel anchors through panel bounds, and creates exact line, rectangle, symbol, or text geometry. Scene lowering translates these planned forms into generic nodes.

Datum anchors are structurally accepted but currently emit a notice and no node because stable datum identity belongs to HSPLOT-011. The system does not guess a row. Out-of-domain data annotations are omitted with a diagnostic rather than extrapolated silently. Mixed panel/data region endpoints are rejected during compilation.

### 6.4 Semantics is independent from pixels

`PlotSemantics` now records guide visibility, channel, display side, label, tick or entry values, participating variable IDs, and scale domains. Annotation semantics records stable ID, kind, label, intent, anchor, text, and visible panels.

A consumer can therefore answer questions such as:

- Which variable does this legend explain?
- Was an x guide intentionally hidden?
- Which scale domain produced these entries?
- Is this threshold a reference, target, or limit?
- Which facets contain this annotation?

None of these questions requires traversing SVG.

## 7. HSPLOT-009: coordinates transform geometry late

Coordinates change the display space of already computed geometry. They do not rename variables, rerun statistics, change grouping, or train different semantic domains. HSPLOT-009 implemented this rule with a closed `CoordinateSpec` and a compiled coordinate stage.

```ts
type CoordinateSpec =
  | { kind: "cartesian" }
  | { kind: "transpose" }
  | {
      kind: "polar";
      theta: "x" | "y";
      startAngle?: number;       // radians
      direction?: "clockwise" | "counterclockwise";
      innerRadius?: number;      // [0, 1)
    };
```

Compilation supplies a default start angle of `-Math.PI / 2`, clockwise direction, and zero inner radius. It rejects non-finite angles and inner radii outside `[0,1)`.

### 7.1 Normalized and device space

`src/coordinates.ts` is React-, DOM-, and SVG-free. It converts device points to panel-normalized coordinates, applies a package-owned transform, and returns device points. For transpose:

```text
normalized input:  (x, y)
normalized output: (y, x)
```

For polar coordinates:

```text
angle  = startAngle + direction × thetaFraction × 2π
radius = innerRadiusPx + radialFraction × (outerRadiusPx - innerRadiusPx)
x      = centerX + cos(angle) × radius
y      = centerY + sin(angle) × radius
```

Positive angular direction is clockwise in SVG device space because device y increases downward. The compiled coordinate stores direction as `1` or `-1`; semantics projects the public string.

### 7.2 Transpose changes display orientation, not variable meaning

The transpose Storybook proof keeps the original temporal x variable and quantitative y variable in semantics. Temporal ticks appear on the vertical display axis; quantitative ticks appear on the horizontal display axis. The labels remain `Observed at` and `Response (ms)`.

A subtle bug appeared in the first implementation. It normalized typography offsets along with data positions. On a non-square panel, a 39-pixel bottom-label offset became a much larger horizontal offset after swapping normalized dimensions, pushing `Observed at` partly outside the SVG. The correction separates two spaces:

- scale positions and geometric vertices transform in normalized panel space;
- tick and label offsets remain fixed device-space layout quantities on the resolved display side.

This distinction is central to coordinate-aware guide planning. Geometric positions transform. Typography metrics do not become data coordinates.

### 7.3 Ordinary bars become sectors

Polar bars are not a new geometry. Existing bar planning produces a device rectangle from an x interval and radial baseline/value interval. Coordinate lowering converts the rectangle back to normalized boundaries, assigns theta and radius according to the coordinate, samples the outer arc, samples the inner arc in reverse, and returns one closed generic path.

```text
polarRectangle(rect):
    normalized = deviceRectToPanelFractions(rect)
    thetaStart, thetaEnd = angular boundaries
    radialStart, radialEnd = radial boundaries

    outer = sampleArc(thetaStart, thetaEnd, radialEnd)
    inner = sampleArc(thetaEnd, thetaStart, radialStart)

    return closePath(outer + inner)
```

The Storybook proof contains 15 ordinary stacked bars and 15 mark paths. The SVG renderer receives generic paths. It contains no `polar`, `sector`, `pie`, or `rose` branch.

Rules have two polar topologies. A rule on the theta dimension becomes a ray. A rule on the radial dimension becomes a circle. Positional guides follow the same distinction: angular ticks create rays; radial ticks create circles. Legends remain external because they explain non-positional scales rather than coordinate geometry.

### 7.4 Unsupported topology is explicit

Point, line, bar, and rule geometry support transpose and polar transforms. Area, ribbon, error-bar, and boxplot topology require dedicated boundary and orientation work. HSPLOT-009 does not transform them approximately. Planning emits `coordinate.geometry.unsupported` with the layer ID and returns no partial plan or scene.

This is a deliberate correctness boundary. A transformed vertex list can self-intersect or encode the wrong interval semantics. Supporting a new topology requires hand-calculated fixtures and a real consumer requirement.

## 8. HSPLOT-010: variables are mappings and algebra lowers before planning

Initial variables represented schema fields and constants. HSPLOT-010 extended them with derived expressions and unity. It also introduced cross, nest, blend, and unity algebra under `composition.algebra`. The public language remains finite JSON.

### 8.1 Derived expressions

The supported expression subset is:

```ts
type VariableExpression =
  | { kind: "variable"; variable: VariableId }
  | { kind: "unary"; op: "log" | "exp" | "sqrt" | "abs" | "sign"; input: VariableExpression }
  | { kind: "binary"; op: "add" | "subtract" | "multiply" | "divide" | "power";
      left: VariableExpression; right: VariableExpression }
  | { kind: "cut"; input: VariableExpression; breaks: readonly number[] };
```

There is no `eval`, function callback, source string, SQL fragment, runtime plugin, lag, or inferred grouped transform. The compiler checks every reference, detects dependency cycles, verifies quantitative operands, validates finite strictly increasing cut breaks, infers semantic type, and records canonical paths.

Dependency resolution is recursive. A visiting stack detects cycles and reports the exact cycle rather than failing later during row evaluation. Dependencies are inserted before dependents, giving materialization a deterministic topological order.

### 8.2 Materialization occurs before statistics

`materializePlotData` clones every input row and writes package-owned derived columns. The caller’s rows are never mutated. Invalid numeric domains produce `null` and increment a per-variable diagnostic count. Examples include log of a non-positive value, square root of a negative value, division by zero, invalid power, overflow, and nonnumeric input.

```mermaid
flowchart LR
    INPUT[immutable input rows] --> CLONE[clone row + source index]
    CLONE --> DERIVED[evaluate derived variables in dependency order]
    DERIVED --> NEST[materialize compound identities]
    NEST --> BLEND[expand blend operands in source order]
    BLEND --> ORDINARY[ordinary PlotData rows]
    ORDINARY --> STATS[existing statistics stage]
```

The transform-before-stat order has a direct test. Two rows contain responses `e¹` and `e³`. A derived `log(response)` variable produces `1` and `3`. A summary mean then produces `2`. If statistics ran first, the result would be `log((e + e³)/2)`, a different value.

The first version of this test exposed a fixture error rather than a compiler error: the summary statistic requires an explicit interval configuration, and the test omitted it. The runtime reported `Cannot read properties of undefined (reading 'multiplier')`. Adding the standard-error interval made the test exercise the intended order.

### 8.3 Cross preserves dimensional order

Cross concatenates ordered algebra terms. In positional composition, it must lower to exactly two dimensions:

```ts
composition.algebra({
  position: algebra.cross(
    algebra.variable(observedAt),
    algebra.variable(logResponse),
  ),
});
```

Compilation lowers the first operand to x and the second to y. Noncommutative order is never sorted. A position that does not produce exactly two dimensions is invalid.

Unity contributes one constant identity value, `__unity__`. It lets lower-order terms participate without inventing a source column.

### 8.4 Nest preserves conditional identity

Nest combines explicit outer and inner values into one generated nominal variable. Equal inner labels under different outer values remain distinct. The acceptance fixture contains `Springfield` under US and CA and produces two group keys.

The identity encoding preserves type and value:

```json
[
  ["string", "US"],
  ["string", "Springfield"]
]
```

Typed pairs avoid collisions between values such as numeric `1`, string `"1"`, and null. A nest can receive an explicit generated variable ID. If omitted, the compiler derives a deterministic ID from the canonical algebra path.

### 8.5 Blend expands cases and retains source identity

Blend unions several variables into one value dimension. One source row therefore becomes one row per operand. The compiler creates two ordinary compiled variables:

- a blended value variable;
- a source discriminator variable.

The source discriminator is added explicitly to normalized groups. It does not appear because color happened to reference it. A layer may also map the explicit discriminator ID to color.

For two source rows and two population operands:

```text
input:
  { category: A, pop80: 80, pop00: 100 }
  { category: B, pop80: 60, pop00: 90 }

materialized:
  { category: A, population: 80,  year: pop80, sourceRow: 0 }
  { category: A, population: 100, year: pop00, sourceRow: 0 }
  { category: B, population: 60,  year: pop80, sourceRow: 1 }
  { category: B, population: 90,  year: pop00, sourceRow: 1 }
```

Operand order determines expansion order. Source row identity remains in `__plot_source_row_index`. Blend operands must have one common semantic type. Empty blends and nested forms that do not lower to one value per operand diagnose before execution.

### 8.6 Algebra disappears before planning

The planner, scene builder, SVG renderer, and React host contain no imports of algebra or variable-expression modules and no branches on `cross`, `nest`, `blend`, or `unity`. They receive ordinary compiled variables, explicit composition, and ordinary rows.

This is the central success criterion for HSPLOT-010. The public language grew. The downstream execution model did not acquire a parallel interpretation layer.

## 9. Structured semantics as an independent product

A plot is not fully described by visible marks. Statistical method, variable identity, grouping, data coverage, hidden guides, annotation intent, coordinate meaning, and algebra provenance are not reliably recoverable from pixels.

`PlotSemantics` is projected from normalized grammar, planning metadata, and diagnostics. It does not import `SceneGraph`. Its final structure includes:

- variables with source, field ID, semantic type, unit, timezone, constant, derived expression, and provenance;
- composition with x, y, ordered groups, facets, and partitions;
- layers with statistics, outputs, assumptions, geometry, position, aesthetics, and groups;
- scale channels, kinds, domains, units, and timezones;
- guide visibility, side/orientation, labels, ticks/entries, participating variables, and domains;
- annotations with ID, kind, intent, anchor, text, and visible panels;
- nest and blend provenance, including generated IDs and operands;
- coordinate kind, theta, start angle, direction, and inner radius;
- bounded data coverage and non-error notices.

The independence test mutates a scene object and verifies that semantics does not change. Architecture guards reject scene imports. This makes semantics suitable for accessibility descriptions, export metadata, inspection tools, debugging, and future agent-facing interfaces.

## 10. Diagnostics are part of the language

A declarative compiler must explain invalid documents at stable paths. Throwing a generic exception or rendering a plausible approximation makes the language impossible to use safely.

The completed phases added diagnostics for:

| Area | Representative diagnostics |
|---|---|
| Guides | missing dimension/aesthetic, unsupported side/format, invalid tick count, out-of-domain values |
| Annotations | invalid/duplicate ID, missing anchor, incompatible region spaces, excluded facets, outside domain |
| Coordinates | invalid start angle/inner radius, unsupported geometry topology |
| Variables | unknown reference, cycle, transform type, invalid runtime domain count |
| Algebra | overlapping surfaces, invalid dimension count, empty blend, mixed operand types |
| Data | invalid positional values, empty valid result, bounded category overflow |

Compile-time errors return no normalized value. Planning errors return no plan or scene. Runtime transform-domain failures produce counted warnings and null values; if every positional value becomes invalid, the existing data-stage error remains visible as a second truthful diagnostic. Tests use `arrayContaining` rather than suppressing one result to make another assertion simpler.

Diagnostic paths preserve source indexes and canonical algebra locations, such as:

```text
variables.logged-response.expression
composition.algebra.position.left.variable
composition.algebra.groups[0]
coordinate.innerRadius
annotations[2].from
presentation.xGuide.options.ticks.values[1]
```

This path discipline is as important as successful output. It defines how users and tools repair a document.

## 11. Testing strategy: prove boundaries, not only outputs

The final test suite contains 133 tests across 22 files. The important property is the variety of evidence.

### 11.1 Contract tests

Contract tests compile literal documents and inspect normalized grammar. They verify defaults, source paths, generated IDs, effective layer composition, diagnostic codes, and serializability.

### 11.2 Numeric and geometric tests

Numeric tests use hand-calculated expectations:

- transpose applied twice returns the original point within floating-point tolerance;
- polar cardinal points match center and radius calculations;
- inner radius moves a radial-zero point to the expected device radius;
- ordinary stacked bars produce bounded sector paths;
- log transforms execute before summary means;
- blend materialization yields `[60, 80, 90, 100]` under numeric sorting.

### 11.3 Architecture tests

Architecture tests read source text and enforce negative constraints:

- downstream stages do not import `PlotDocument`;
- core and author code do not import React or DOM/SVG APIs;
- scene lowering does not import presentation, layout, compiler, or scales;
- geometry planning does not create guide nodes;
- root plan aliases do not return;
- host CSS does not restore omitted frames;
- planner, scene, SVG renderer, and React host do not import algebra or interpret algebra operators;
- obsolete mapping and migration vocabulary remains absent.

Negative architecture tests are valuable because a feature can pass behavioral tests while violating a boundary that only matters to future work.

### 11.4 Package tests

The final package validation sequence is:

```bash
pnpm install --frozen-lockfile
pnpm test
pnpm typecheck
pnpm lint
pnpm build
pnpm build-storybook
pnpm consumer:smoke
pnpm pack:check
git diff --check
```

The frozen install confirms the lockfile. The known warning is that pnpm ignored the `esbuild` build script. Production and Storybook builds still pass.

The packed tarball contains 105 entries, including author and root JavaScript, declarations, source maps, CSS, README, and package metadata. It contains no `src/`, ticket workspace, or `storybook-static` tree.

### 11.5 Browser tests

Browser inspection covered:

- grouped sparse, flat, one-point, and empty 120×24 sparklines;
- configured top and right axes, explicit temporal ticks, major grids, horizontal legend, threshold, region, and note;
- transposed points with temporal values on the vertical display axis;
- 15 ordinary stacked bars rendered as 15 polar paths with radial grids;
- derived logarithmic values with a `Log response` axis.

Screenshots live in each ticket’s `reference/screenshots/` directory. Browser evaluation checked viewBoxes, computed styles, role counts, finite numeric attributes, path counts, and accessibility descriptions.

## 12. Failure analysis and corrections

The diaries preserve failed attempts because they explain the final contracts better than a clean changelog.

### 12.1 Presentation and guide failures

The first HSPLOT-008 full run failed 32 tests with `ReferenceError: scale is not defined`. A legend compatibility key referenced a nonexistent local. Replacing the reference with mapped-variable identity and resolved domain/order fixed the runtime error.

The next compatibility rule was too strict and treated color, fill, and shape scale specifications as separate semantic identities. Existing merged guides expanded unexpectedly. The final rule compares variable identity, resolved domain/order, title, and orientation instead.

Guide formatter validation initially read semantic type directly from `CompiledVariableRef`; variable refs store it on `value.variable`. Narrowing the compiled value fixed temporal and quantitative validation.

### 12.2 Coordinate failures

The first screenshot capture failed because the screenshots directory did not exist. The durable process now creates evidence directories before browser capture.

The first transpose guide implementation transformed typography offsets through normalized geometry. This exposed the difference between data space and device layout space and led to the fixed-offset rule described earlier.

### 12.3 Algebra failures

The first summary transform test omitted interval configuration. The failure demonstrated that fixtures must satisfy the statistic contract before they can prove stage ordering.

The first invalid-transform assertion expected one diagnostic, but an all-invalid result also triggers the existing no-valid-data error. The test was corrected to preserve both truths.

The first blend-value check used JavaScript’s default lexical sort and produced `[100, 60, 80, 90]`. An explicit numeric comparator made the expected numeric order unambiguous.

### 12.4 Consumer and tool failures

`pnpm smoke:consumer` failed because the actual script is `pnpm consumer:smoke`. The diary records the exact command and correction.

The first Storybook browser evaluation used a malformed expression and returned `SyntaxError: Unexpected token ')'`. A smaller explicit traversal produced reliable evidence.

Storybook static serving reports a missing `/favicon.ico`. This is server chrome, not a plot runtime failure, and remains documented rather than misclassified.

## 13. Design decisions that should remain stable

The completed work makes several decisions that future changes should preserve unless a new ticket replaces them explicitly.

### 13.1 A scale is not a guide

Suppressing a guide never disables its scale. This enables compact plots and intentionally unexplained encodings without changing mark generation.

### 13.2 Product continuity is not inferred by Plot

Applications decide where operational progress has gaps, resets, and phase boundaries. Plot renders explicit groups.

### 13.3 Coordinate transformation is late

Statistics, grouping, positions, and domains remain in source-variable semantics. Coordinates alter planned geometry and positional guides.

### 13.4 Algebra lowers completely

Cross, nest, blend, and unity do not survive into planning or rendering. Generated variables and materialized rows use the existing execution model.

### 13.5 Unsupported topology diagnoses

The package does not claim area, ribbon, error-bar, or boxplot polar support until it can preserve their topology with evidence.

### 13.6 Presets expand to ordinary grammar

Sparkline remains ordinary line grammar. A future pie-like preset may construct bar intervals plus polar coordinates, but it must not introduce `geom.pie` merely for convenience.

### 13.7 Semantics is not derived from SVG

Accessibility, inspection, and automation should consume `PlotSemantics`, supplemented by scene interaction metadata where physical geometry matters.

## 14. The current public authoring surface

The final author package covers the canonical vocabulary without requiring consumers to write every discriminator manually.

| Area | Constructors |
|---|---|
| Plot | `plot` |
| Variables | `variable.field`, `constant`, `derived`, `unity` |
| Expressions | `transform.variable`, `unary`, `binary`, `log`, `sqrt`, `cut` |
| Algebra | `algebra.variable`, `unity`, `cross`, `nest`, `blend` |
| Composition | `composition.cartesian`, `composition.algebra` |
| Layers | `layer` |
| Statistics | identity, summary, bin, OLS, boxplot, density |
| Geometry | point, line, bar, area, ribbon, rule, error-bar, boxplot |
| Position | identity, stack, fill, dodge, jitter |
| Scales | positional and aesthetic scale families |
| Coordinates | Cartesian, transpose, polar |
| Presentation | presence, compact presentation, configured guides |
| Annotation | rule, text, region, point |
| Presets | ordinary-grammar sparkline |

A combined example shows the language composition:

```ts
const logResponse = variableId("log-response");
const year = variableId("population-year");
const population = variableId("population-value");

const document = plot({
  id: plotId("population-analysis"),
  variables: {
    [category]: variable.field(fieldId("category")),
    [pop1980]: variable.field(fieldId("pop1980")),
    [pop2000]: variable.field(fieldId("pop2000")),
    [logResponse]: variable.derived(
      transform.log(transform.variable(response)),
      { label: "Log response" },
    ),
  },
  composition: composition.algebra({
    position: algebra.cross(
      algebra.variable(category),
      algebra.blend(
        [algebra.variable(pop1980), algebra.variable(pop2000)],
        { valueId: population, discriminatorId: year },
      ),
    ),
  }),
  layers: [
    layer({
      id: layerId("population-lines"),
      stat: stat.identity(),
      geom: geom.line(),
      position: position.identity(),
      mapping: { color: value.variable(year) },
    }),
  ],
  coordinate: coordinate.polar({
    theta: "x",
    startAngle: -Math.PI / 2,
    direction: "clockwise",
    innerRadius: 0.16,
  }),
  presentation: {
    yGuide: presence.configured(
      guide.axis({ label: "Population", side: "right", grid: "major" }),
    ),
  },
  annotations: [
    annotation.rule({
      id: annotationId("target"),
      channel: "y",
      value: value.constant(100),
      label: "Target",
      intent: "target",
    }),
  ],
});
```

Not every combination is accepted. Compilation and coordinate planning reject invalid semantic types, ambiguous composition overlap, and unsupported geometry topology. The important property is that this example is still one serializable document evaluated by one compiler.

## 15. Current limits and next work

The completed program closes HSPLOT-005 through HSPLOT-010. The remaining work belongs to later tickets rather than hidden debt in these phases.

### 15.1 Stable datum identity and inversion

HSPLOT-011 is the next architectural step. Datum-relative annotation anchors currently diagnose and omit because the package does not yet expose stable datum identity through all transforms. Coordinate inversion is also absent. Interaction should reuse compiled coordinates and source/blend identity rather than inspect SVG paths.

### 15.2 Additional polar topology

Area, ribbon, error-bar, and boxplot transforms remain unsupported. Each needs explicit boundary semantics, ordering rules, and hand-calculated tests. A real consumer should activate that work.

### 15.3 Text measurement and collision

Layout uses deterministic fixed metrics. Configured ticks and polar labels do not invoke DOM measurement. Future collision and wrapping work must preserve deterministic planning, potentially through package-owned measurement inputs rather than renderer queries.

### 15.4 Data materialization performance

Blend currently expands immutable rows. This favors correctness, inspectability, and compatibility with existing stages. Larger bounded datasets may justify a columnar evaluation view, but only measurement should drive that change.

### 15.5 Additional transform vocabulary

Lag, rank, grouped transforms, and arbitrary expressions remain absent. Grouped transforms need explicit `by` operands. No transform should infer grouping from aesthetics or facets.

## 16. How to review and reproduce the result

The repository is:

```text
/home/manuel/workspaces/2026-08-24/use-optkit/plot
```

Run the complete package gates:

```bash
cd /home/manuel/workspaces/2026-08-24/use-optkit/plot
pnpm install --frozen-lockfile
pnpm test
pnpm typecheck
pnpm lint
pnpm build
pnpm build-storybook
pnpm consumer:smoke
pnpm pack:check
```

Run focused tests by phase:

```bash
pnpm exec vitest run src/presentation.test.ts src/presentation-golden.test.ts
pnpm exec vitest run src/author.test.ts src/architecture.test.ts
pnpm exec vitest run src/configured-guides-annotations.test.ts
pnpm exec vitest run src/coordinates.test.ts
pnpm exec vitest run src/algebra.test.ts
```

Launch Storybook:

```bash
pnpm storybook
```

Inspect these stories under `Grammar/PlotHost`:

- grouped sparse, flat, one-point, and empty sparklines;
- Configured Guides And Annotations;
- Transposed Point Plot;
- Polar Stacked Bars;
- Derived Variable Algebra.

The final evidence audit is:

```text
/home/manuel/workspaces/2026-08-24/use-optkit/plot/ttmp/2026/08/29/
HSPLOT-010--public-variables-transforms-and-plot-algebra/
reference/03-hsplot-005-010-completion-audit.md
```

## 17. Commit and ticket map

| Ticket | Principal implementation | Closure/evidence |
|---|---|---|
| HSPLOT-005 | `d81e25c` | `6bef4c1`, diary and presentation proof |
| HSPLOT-006 | `2ec1002` | `de0718f`, packed author-only consumer |
| HSPLOT-007 | `7945c37` | `bfad538`, parity matrix and benchmark |
| HSPLOT-008 | `4ea024e` | `f75cd9b`, configured browser proof |
| HSPLOT-009 | `b0bc530` | `4789a04`, transpose and polar proofs |
| HSPLOT-010 | `8605b4c` | `9f13cba`, `acf7e9e`, final audit |

Consumer commits include RAG-TTC `a57c2f1f8` and `29ce99150`, plus Datalab `980e745`. The final plot audit added frozen-install evidence in `54c6b54`.

Every ticket has checked tasks, synchronized changelog and relations, a strict-format implementation diary, phase start and completion slips, focused commits, and a clean `docmgr doctor` report.

## 18. Conclusion

The HSPLOT-005 through HSPLOT-010 program converted an already staged grammar into a complete, extensible compiler system. Presentation geometry moved into planning. Scene construction became mechanical. Functional authoring remained ordinary grammar construction. Product parity proved compact plots in real applications. Guides and annotations became serializable components. Coordinates transformed geometry late. Derived variables and algebra lowered before statistics into the existing normalized execution model.

The project’s main achievement is architectural continuity. Each phase increased expressiveness without creating a second planner, renderer policy, named-chart hierarchy, callback language, or React dependency below the host. The final system can explain what it will render, diagnose why a document is invalid, serialize every public input and major intermediate form, and prove its behavior through numeric, structural, packaging, consumer, and browser evidence.

## References

### Project source

| Source | Purpose |
|---|---|
| `src/document.ts` | Canonical public grammar, IDs, guides, annotations, coordinates, expressions, and algebra. |
| `src/compile.ts` | Variable dependency compiler, algebra lowering, guide/annotation/coordinate validation, normalized grammar. |
| `src/variables.ts` | Immutable derived-variable, nest, and blend materialization. |
| `src/presentation.ts` | Presentation presence and configured-guide resolution. |
| `src/layout.ts` | Deterministic panel and guide space allocation. |
| `src/plan.ts` | Statistics orchestration, scales, complete geometry, guides, annotations, and coordinate planning. |
| `src/coordinates.ts` | Renderer-free Cartesian, transpose, and polar transforms. |
| `src/semantics.ts` | Renderer-neutral semantic projection. |
| `src/scene.ts` | Mechanical generic scene lowering. |
| `src/renderers/svg/SvgRenderer.tsx` | Accessible SVG rendering from scene nodes. |
| `src/author/` | Pure functional constructors for canonical grammar. |
| `src/architecture.test.ts` | Executable package-boundary guards. |
| `src/configured-guides-annotations.test.ts` | HSPLOT-008 acceptance matrix. |
| `src/coordinates.test.ts` | HSPLOT-009 numeric and topology matrix. |
| `src/algebra.test.ts` | HSPLOT-010 transform and algebra matrix. |
| `scripts/consumer-smoke.mjs` | Packed plain-JavaScript and React consumer validation. |

### Ticket documentation

| Source | Purpose |
|---|---|
| `HSPLOT-005/reference/01-implementation-diary.md` | Complete planning, compact layout, and research chronology. |
| `HSPLOT-006/reference/01-implementation-diary.md` | Functional author package and packaging failures. |
| `HSPLOT-007/reference/01-implementation-diary.md` | Product parity, browser defects, benchmark, and consumer validation. |
| `HSPLOT-007/reference/02-parity-matrix.md` | Plot-family and application parity evidence. |
| `HSPLOT-007/reference/04-sparkline-benchmark.md` | Compact construction/render measurements. |
| `HSPLOT-008/reference/01-implementation-diary.md` | Configured-guide and annotation decisions and failures. |
| `HSPLOT-008/reference/02-validation-and-rendered-inspection.md` | Rendered guide/annotation acceptance. |
| `HSPLOT-009/reference/01-implementation-diary.md` | Coordinate-transform chronology and topology decisions. |
| `HSPLOT-009/reference/02-coordinate-matrix-and-validation.md` | Supported coordinate matrix and browser evidence. |
| `HSPLOT-010/reference/01-implementation-diary.md` | Derived-variable and algebra implementation chronology. |
| `HSPLOT-010/reference/02-algebra-matrix-and-validation.md` | Transform and algebra acceptance matrix. |
| `HSPLOT-010/reference/03-hsplot-005-010-completion-audit.md` | Final requirement-by-requirement completion audit. |

All ticket paths are rooted at:

```text
/home/manuel/workspaces/2026-08-24/use-optkit/plot/ttmp/2026/08/29/
```

### Prior vault reports

- [[From Canonical Grammar to Plot Algebra - Deep Technical Analysis]] — the pre-implementation research and design program for HSPLOT-005 through HSPLOT-010.
- [[PROJECT REPORT - Hyperslop Plot v0.2 - From Grammar to Published PBUI Runtime]] — the earlier v0.2 package, PBUI integration, publication, and scientific authoring report.
- [[PROJ - Hyperslop Plot - Building a Frontend Grammar of Graphics as a Staged Compiler]] — the initial staged-compiler project architecture.
