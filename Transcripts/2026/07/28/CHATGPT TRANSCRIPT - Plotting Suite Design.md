# Plotting Suite Design

- URL: https://chatgpt.com/c/6a68d9ea-9804-83ea-81c0-5722f9542446
- Created: 2026-07-28T16:33:47.082Z

---

> Analyze github.com/go-go-golems/go-go-datadrop, the graphic compiler and plot builder and plot visualizations. I want to turn this into a full featured plotting suite for professional / scientific graphs based on th egrammar of graphics / tidyverse principle. How would you implement a full system to do all this, with graph output.
>
> I don't mind opinionated, but it should allow customization as well. I have been enjoying a pattern where I have a fluent builder API that is opinionated but can be composed, and passing lambdas to do proper configuration. Which is then all compiled to an IR that then gets interpreted to do the actual work. 
>
> Analyze, design, research, study, think, engineer and then write a full markdown.md report and a TS implementation

I’ll inspect the repository’s plotting compiler and architecture, compare established grammar-of-graphics systems, then deliver a design report and runnable TypeScript implementation with examples, tests, and graph output.

<details><summary>💭 Thinking</summary>

**Setting up research**

I’m preparing to inspect the repository, compare its architecture with established grammar-of-graphics systems, and review relevant visualization libraries. I’ll then design an implementation and package the findings with TypeScript examples in Markdown.

**Retrieved go-go-datadrop metadata and searched for graphic compiler components**

</details>

```unknown
bash -lc rm -rf /mnt/data/go-go-datadrop && git clone --depth 1 https://github.com/go-go-golems/go-go-datadrop.git /mnt/data/go-go-datadrop && git -C /mnt/data/go-go-datadrop rev-parse HEAD && find /mnt/data/go-go-datadrop -maxdepth 2 -type f | sed 's#/mnt/data/go-go-datadrop/##' | sort | head -200
```

<details><summary>💭 Thinking</summary>

**Cloned the Go-Go Datadrop repository**

**Searched repository for plot-related files**

</details>

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/go-go-datadrop"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/go-go-datadrop/archive/refs/heads/main.zip"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```json
{"open":[{"ref_id":"https://codeload.github.com/go-go-golems/go-go-datadrop/zip/refs/heads/main"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

**Inspected GitHub repository structure and searched for GraphicsDocument references**

**Finding repository access**

The first repository route is limited, so I’m switching to a broader inspection method. I’ll identify the project structure and key files, then use those findings to ground the design rather than guessing.

**Checked repository access**

</details>

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/go-go-datadrop/tree/main/ui?plain=1"},{"ref_id":"https://github.com/go-go-golems/go-go-datadrop/tree/main/ui?output=1"},{"ref_id":"https://github.com/go-go-golems/go-go-datadrop/tree/main/ui?tab=readme-ov-file"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching github.com**

</details>

The existing typed-table-to-canonical-graphics-document boundary is promising; I’m now identifying where the compiler, executor, and renderer abstractions remain too narrow for professional scientific plotting.

<details><summary>💭 Thinking</summary>

**Fetched the Visualization Workbench implementation guide**

**Fetched implementation guide sections and current UI source files**

</details>

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/go-go-datadrop/find/main"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

**Investigated buildPlot architecture and implemented useDocPlot with compilation checks**

**Inspecting project structure**

I’m moving from repository access toward a grounded design review. I’ll examine the existing plotting, compiler, transformation, and testing patterns, then align the proposed TypeScript implementation with those conventions.

**Fetched graphic UI and plot tests from GitHub**

**Framing the architecture**

I’m treating the existing system as a promising compiler-based foundation, then extending it toward a complete grammar-of-graphics platform with composable builders, an explicit IR, and interchangeable rendering backends.

**Designing the plotting suite**

I’m shaping the proposal around layered grammar, tidy data, fluent immutable builders, staged compilation, extensible intermediate representations, statistical transformations, professional themes, accessibility, and SVG/Canvas/export backends.

**Framed the architecture and designed the plotting suite**

</details>

```json
{"search_query":[{"q":"site:ggplot2-book.org ggplot2 grammar of graphics layers scales coordinates facets official"},{"q":"site:tidyverse.org ggplot2 extension system official ggproto geoms stats scales"},{"q":"A Layered Grammar of Graphics Wickham 2010 pdf"},{"q":"site:vega.github.io/vega-lite specification grammar of interactive graphics composition transform scale official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 8 websites**

</details>

```unknown
bash -lc node --version; npm --version; bun --version 2>/dev/null || true; tsc --version 2>/dev/null || true
```

<details><summary>💭 Thinking</summary>

**Built scientific plotting suite with uncertainty and color support**

</details>

```json
{"search_query":[{"q":"site:ggplot2.tidyverse.org/reference stat_summary geom_errorbar ggplot2 official confidence intervals"},{"q":"site:ggplot2.tidyverse.org/reference facet_grid facet_wrap scales free official"},{"q":"site:ggplot2.tidyverse.org/reference coord_cartesian coord_fixed coord_polar official"},{"q":"site:ggplot2.tidyverse.org/reference theme complete themes official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Fetched encoding app source and EncodingPanel UI component**

</details>

```unknown
bash -lc set -euo pipefail
ROOT=/mnt/data/datadrop-gog-suite
rm -rf "$ROOT"
mkdir -p "$ROOT"/{src,examples/output,test}
cat > "$ROOT/package.json" <<'EOF'
{
  "name": "@datadrop/gog-suite-reference",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "description": "Reference grammar-of-graphics compiler and scientific plotting kernel for go-go-datadrop",
  "scripts": {
    "build": "tsc -p tsconfig.json",
    "test": "npm run build && node --test dist/test/*.test.js",
    "examples": "npm run build && node dist/examples/scientific.js",
    "check": "npm run test && npm run examples"
  },
  "engines": {
    "node": ">=22"
  },
  "license": "MIT"
}
EOF
cat > "$ROOT/tsconfig.json" <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "declaration": true,
    "sourceMap": true,
    "outDir": "dist",
    "rootDir": ".",
    "skipLibCheck": true
  },
  "include": ["src/**/*.ts", "examples/**/*.ts", "test/**/*.ts"]
}
EOF
cat > "$ROOT/.gitignore" <<'EOF'
dist/
node_modules/
EOF
printf '%s\n' "$ROOT"
```

The plot pass currently loses stable field identity and couples visual stages. I’ve implemented a serializable v2 model and scenegraph; next come scales, statistics, positions, and rendering.

<details><summary>💭 Thinking</summary>

**Built a TypeScript grammar-of-graphics plotting suite with utilities, scales, themes, plugins, registries, coordinates, and rendering**

</details>

```unknown
bash -lc cat > /mnt/data/datadrop-gog-suite/src/compiler.ts <<'EOF'
import type {
  Channel,
  CompileResult,
  CompiledDatum,
  CompiledLayerIR,
  DataEnvironment,
  DataRef,
  Datum,
  Diagnostic,
  FacetScalePolicy,
  FacetSpec,
  FieldSchema,
  JsonObject,
  PanelIR,
  PlotIR,
  PlotSpec,
  PositionSpec,
  RegistryLike,
  ResolvedData,
  ResolvedEncoding,
  ResolvedFieldEncoding,
  ResolvedMapping,
  ScaleChannel,
  ScalePlanIR,
  ScaleSpec,
  SemanticType,
  StatSpec,
  ThemeSpec,
} from "./types.js";
import { themeScientific } from "./themes.js";
import {
  INTERNAL_PREFIX,
  clone,
  deterministicUnit,
  diagnostic,
  fieldType,
  groupBy,
  mergeSchema,
  mergeTheme,
  stableKey,
  toJsonPrimitive,
  toNumber,
  toText,
  uniqueStable,
} from "./utils.js";

interface ResolvedLayerInput {
  layerIndex: number;
  layerId: string;
  data: ResolvedData;
  spec: PlotSpec["layers"][number];
}

interface PanelAssignment {
  panel: PanelIR;
  row: Datum;
  sourceIndex: number;
}

const POSITION_CHANNELS_X: readonly Channel[] = ["x", "x2", "xmin", "xmax"];
const POSITION_CHANNELS_Y: readonly Channel[] = ["y", "y2", "ymin", "ymax"];
const DISCRETE_GROUP_CHANNELS: readonly Channel[] = ["color", "fill", "shape", "linetype", "detail"];

function hasErrors(diagnostics: readonly Diagnostic[]): boolean {
  return diagnostics.some((item) => item.severity === "error");
}

function resolveData(
  ref: DataRef | undefined,
  environment: DataEnvironment,
  diagnostics: Diagnostic[],
  path: string,
): ResolvedData | null {
  if (!ref) {
    diagnostics.push(
      diagnostic("error", "resolve", "data.missing", "No data source is available for this layer", {
        path,
        hint: "Attach inline data, name a registered dataset, or reference a DataDrop relation.",
      }),
    );
    return null;
  }
  if (ref.kind === "inline") {
    const rows = ref.values as readonly Datum[];
    return {
      name: ref.name ?? path,
      rows,
      schema: mergeSchema(ref.schema, rows),
      ...(ref.coverage ? { coverage: clone(ref.coverage) } : {}),
    };
  }
  const resolved = ref.kind === "named" ? environment.named?.[ref.name] : environment.relations?.[ref.relationId];
  if (!resolved) {
    const identifier = ref.kind === "named" ? ref.name : ref.relationId;
    diagnostics.push(
      diagnostic("error", "resolve", "data.unresolved", `Data source '${identifier}' is not registered`, {
        path,
      }),
    );
    return null;
  }
  return {
    ...resolved,
    rows: resolved.rows,
    schema: mergeSchema(resolved.schema, resolved.rows),
  };
}

function resolveMapping(
  mapping: PlotSpec["mapping"],
  schema: readonly FieldSchema[],
  diagnostics: Diagnostic[],
  path: string,
  layerId: string,
): ResolvedMapping {
  const resolved: ResolvedMapping = {};
  for (const [channel, encoding] of Object.entries(mapping ?? {}) as Array<[Channel, NonNullable<typeof mapping>[Channel]]>) {
    if (!encoding) continue;
    if (encoding.kind === "value") {
      resolved[channel] = clone(encoding);
      continue;
    }
    const inferred = fieldType(schema, encoding.field);
    if (!inferred && encoding.source !== "stat") {
      diagnostics.push(
        diagnostic("error", "resolve", "field.missing", `Field '${encoding.field}' mapped to ${channel} does not exist`, {
          path: `${path}.${channel}`,
          nodeId: layerId,
          hint: "Use stable field ids in the host adapter and surface stale mappings instead of silently clearing them.",
        }),
      );
      continue;
    }
    resolved[channel] = {
      ...clone(encoding),
      type: encoding.type ?? inferred ?? "quantitative",
    } as ResolvedFieldEncoding;
  }
  return resolved;
}

function mergeMappings(global: PlotSpec["mapping"], layer: PlotSpec["layers"][number]): PlotSpec["mapping"] {
  return layer.inheritMapping === false
    ? clone(layer.mapping ?? {})
    : { ...(global ?? {}), ...(layer.mapping ?? {}) };
}

function categoryValues(inputs: readonly ResolvedLayerInput[], field: string): unknown[] {
  return uniqueStable(
    inputs.flatMap((input) => input.data.rows.map((row) => row[field]).filter((value) => value !== undefined)),
    (value) => stableKey([value]),
  );
}

function makePanels(
  facet: FacetSpec | undefined,
  inputs: readonly ResolvedLayerInput[],
  diagnostics: Diagnostic[],
): PanelIR[] {
  if (!facet) return [{ id: "panel:0", row: 0, column: 0 }];
  if (facet.type === "wrap") {
    const values = categoryValues(inputs, facet.field);
    if (values.length === 0) {
      diagnostics.push(
        diagnostic("warning", "resolve", "facet.empty", `Facet field '${facet.field}' has no observed values`, {
          path: "facet.field",
        }),
      );
      return [{ id: "panel:0", row: 0, column: 0, title: "(empty)" }];
    }
    const columns = Math.max(1, Math.floor(facet.columns ?? Math.ceil(Math.sqrt(values.length))));
    return values.map((value, index) => ({
      id: `panel:${stableKey([value])}`,
      row: Math.floor(index / columns),
      column: index % columns,
      columnValue: toJsonPrimitive(value),
      title: toText(value),
    }));
  }
  const rowValues = facet.rows ? categoryValues(inputs, facet.rows) : [null];
  const columnValues = facet.columns ? categoryValues(inputs, facet.columns) : [null];
  const panels: PanelIR[] = [];
  for (let row = 0; row < rowValues.length; row += 1) {
    for (let column = 0; column < columnValues.length; column += 1) {
      const rowValue = rowValues[row];
      const columnValue = columnValues[column];
      const observed = inputs.some((input) =>
        input.data.rows.some((datum) =>
          (!facet.rows || datum[facet.rows] === rowValue) && (!facet.columns || datum[facet.columns] === columnValue),
        ),
      );
      if (facet.drop !== false && !observed) continue;
      const title = [
        facet.rows ? `${facet.rows}=${toText(rowValue)}` : null,
        facet.columns ? `${facet.columns}=${toText(columnValue)}` : null,
      ]
        .filter(Boolean)
        .join(" · ");
      panels.push({
        id: `panel:${stableKey([rowValue, columnValue])}`,
        row,
        column,
        ...(facet.rows ? { rowValue: toJsonPrimitive(rowValue) } : {}),
        ...(facet.columns ? { columnValue: toJsonPrimitive(columnValue) } : {}),
        ...(title ? { title } : {}),
      });
    }
  }
  return panels.length > 0 ? panels : [{ id: "panel:0", row: 0, column: 0, title: "(empty)" }];
}

function panelsForRow(row: Datum, panels: readonly PanelIR[], facet: FacetSpec | undefined): PanelIR[] {
  if (!facet) return [panels[0]!];
  if (facet.type === "wrap") {
    if (!(facet.field in row)) return [...panels];
    const value = toJsonPrimitive(row[facet.field]);
    return panels.filter((panel) => panel.columnValue === value);
  }
  const hasRow = !facet.rows || facet.rows in row;
  const hasColumn = !facet.columns || facet.columns in row;
  if (!hasRow || !hasColumn) return [...panels];
  const rowValue = facet.rows ? toJsonPrimitive(row[facet.rows]) : undefined;
  const columnValue = facet.columns ? toJsonPrimitive(row[facet.columns]) : undefined;
  return panels.filter(
    (panel) => (!facet.rows || panel.rowValue === rowValue) && (!facet.columns || panel.columnValue === columnValue),
  );
}

function groupingFields(mapping: ResolvedMapping): ResolvedFieldEncoding[] {
  const explicit = mapping.group;
  if (explicit?.kind === "field") return [explicit];
  const fields: ResolvedFieldEncoding[] = [];
  for (const channel of DISCRETE_GROUP_CHANNELS) {
    const encoding = mapping[channel];
    if (encoding?.kind === "field" && encoding.type !== "quantitative" && encoding.type !== "temporal") {
      fields.push(encoding);
    }
  }
  return uniqueStable(fields, (field) => field.field);
}

function groupIdFor(row: Datum, fields: readonly ResolvedFieldEncoding[]): string {
  return fields.length === 0 ? "group:all" : `group:${stableKey(fields.map((field) => row[field.field]))}`;
}

function validateChannels(
  required: readonly Channel[] | undefined,
  mapping: ResolvedMapping,
  diagnostics: Diagnostic[],
  phase: "validate" | "stat",
  layerId: string,
  owner: string,
): void {
  for (const channel of required ?? []) {
    if (mapping[channel]) continue;
    diagnostics.push(
      diagnostic("error", phase, `${owner}.channel.${channel}`, `${owner} '${owner === "geom" ? "geometry" : "statistic"}' requires channel ${channel}`, {
        nodeId: layerId,
        path: `layers.${layerId}.mapping.${channel}`,
        hint: `Map ${channel} globally or on this layer.`,
      }),
    );
  }
}

function valueAt(row: CompiledDatum, mapping: ResolvedMapping, channel: Channel): unknown {
  const encoding = mapping[channel];
  return encoding?.kind === "field" ? row.values[encoding.field] : encoding?.value;
}

function applyStack(
  rows: CompiledDatum[],
  mapping: ResolvedMapping,
  normalize: boolean,
  diagnostics: Diagnostic[],
  layerId: string,
): ResolvedMapping {
  const y = mapping.y;
  const x = mapping.x;
  if (y?.kind !== "field" || !x) {
    diagnostics.push(
      diagnostic("error", "position", "position.stack.mapping", "stack/fill requires x and a field-mapped y", {
        nodeId: layerId,
      }),
    );
    return mapping;
  }
  const buckets = groupBy(rows, (row) => `${row.panelId}|${stableKey([valueAt(row, mapping, "x")])}`);
  for (const bucket of buckets.values()) {
    let positive = 0;
    let negative = 0;
    const positiveTotal = bucket.reduce((sum, row) => {
      const value = toNumber(row.values[y.field]);
      return sum + (value > 0 ? value : 0);
    }, 0);
    const negativeTotal = Math.abs(
      bucket.reduce((sum, row) => {
        const value = toNumber(row.values[y.field]);
        return sum + (value < 0 ? value : 0);
      }, 0),
    );
    for (const row of bucket) {
      let value = toNumber(row.values[y.field]);
      if (!Number.isFinite(value)) continue;
      if (normalize) value = value >= 0 ? value / (positiveTotal || 1) : value / (negativeTotal || 1);
      const start = value >= 0 ? positive : negative;
      const end = start + value;
      if (value >= 0) positive = end;
      else negative = end;
      row.values[`${INTERNAL_PREFIX}stack0`] = start;
      row.values[`${INTERNAL_PREFIX}stack1`] = end;
    }
  }
  return {
    ...mapping,
    y: { kind: "field", field: `${INTERNAL_PREFIX}stack1`, source: "stat", type: "quantitative", title: y.title ?? y.field },
    y2: { kind: "field", field: `${INTERNAL_PREFIX}stack0`, source: "stat", type: "quantitative" },
  };
}

function applyDodge(rows: CompiledDatum[], mapping: ResolvedMapping): void {
  const buckets = groupBy(rows, (row) => `${row.panelId}|${stableKey([valueAt(row, mapping, "x")])}`);
  for (const bucket of buckets.values()) {
    const groupIds = uniqueStable(bucket.map((row) => row.groupId), (value) => value);
    for (const row of bucket) {
      row.values[`${INTERNAL_PREFIX}dodgeIndex`] = groupIds.indexOf(row.groupId);
      row.values[`${INTERNAL_PREFIX}dodgeCount`] = groupIds.length;
    }
  }
}

function applyJitter(
  rows: CompiledDatum[],
  mapping: ResolvedMapping,
  position: PositionSpec,
  diagnostics: Diagnostic[],
  layerId: string,
): ResolvedMapping {
  const x = mapping.x;
  const y = mapping.y;
  const width = typeof position.params?.width === "number" ? position.params.width : 0.1;
  const height = typeof position.params?.height === "number" ? position.params.height : 0;
  const next = { ...mapping };
  if (x?.kind === "field" && x.type === "quantitative") {
    for (const row of rows) {
      const value = toNumber(row.values[x.field]);
      if (!Number.isFinite(value)) continue;
      row.values[`${INTERNAL_PREFIX}jitterX`] = value + (deterministicUnit(`${layerId}:${row.sourceIndex}:x`) - 0.5) * width * 2;
    }
    next.x = { kind: "field", field: `${INTERNAL_PREFIX}jitterX`, source: "stat", type: "quantitative", title: x.title ?? x.field };
  } else if (width !== 0) {
    diagnostics.push(
      diagnostic("warning", "position", "position.jitter.discrete", "Numeric jitter width was ignored for a non-quantitative x scale", {
        nodeId: layerId,
      }),
    );
  }
  if (y?.kind === "field" && y.type === "quantitative" && height !== 0) {
    for (const row of rows) {
      const value = toNumber(row.values[y.field]);
      if (!Number.isFinite(value)) continue;
      row.values[`${INTERNAL_PREFIX}jitterY`] = value + (deterministicUnit(`${layerId}:${row.sourceIndex}:y`) - 0.5) * height * 2;
    }
    next.y = { kind: "field", field: `${INTERNAL_PREFIX}jitterY`, source: "stat", type: "quantitative", title: y.title ?? y.field };
  }
  return next;
}

function applyPosition(
  rows: CompiledDatum[],
  mapping: ResolvedMapping,
  position: PositionSpec,
  diagnostics: Diagnostic[],
  layerId: string,
): ResolvedMapping {
  if (position.type === "identity") return mapping;
  if (position.type === "stack") return applyStack(rows, mapping, false, diagnostics, layerId);
  if (position.type === "fill") return applyStack(rows, mapping, true, diagnostics, layerId);
  if (position.type === "dodge" || position.type === "dodge2") {
    applyDodge(rows, mapping);
    return mapping;
  }
  if (position.type === "jitter") return applyJitter(rows, mapping, position, diagnostics, layerId);
  diagnostics.push(
    diagnostic("error", "position", "position.unknown", `Unknown position adjustment '${position.type}'`, {
      nodeId: layerId,
    }),
  );
  return mapping;
}

function inferScaleType(
  channel: ScaleChannel,
  semanticType: SemanticType,
  layers: readonly CompiledLayerIR[],
): NonNullable<ScaleSpec["type"]> {
  if (channel === "x" || channel === "y") {
    if (semanticType === "temporal") return "utc";
    if (semanticType === "nominal" || semanticType === "ordinal") {
      const bandGeom = layers.some((layer) => ["bar", "boxplot", "rect"].includes(layer.geom.type));
      return bandGeom ? "band" : "point";
    }
    return "linear";
  }
  if (channel === "color" || channel === "fill") {
    return semanticType === "quantitative" || semanticType === "temporal" ? "linear" : "ordinal";
  }
  if (channel === "size") return "sqrt";
  if (channel === "shape" || channel === "linetype") return "ordinal";
  return "linear";
}

function scaleChannelsFor(scale: ScaleChannel): Channel[] {
  if (scale === "x") return [...POSITION_CHANNELS_X];
  if (scale === "y") return [...POSITION_CHANNELS_Y];
  return scale === "color" ? ["color", "stroke"] : [scale];
}

function sharingFor(channel: ScaleChannel, policy: FacetScalePolicy | undefined): "shared" | "panel" {
  if (!policy || policy === "fixed") return "shared";
  if (policy === "free") return channel === "x" || channel === "y" ? "panel" : "shared";
  if (policy === "free_x") return channel === "x" ? "panel" : "shared";
  if (policy === "free_y") return channel === "y" ? "panel" : "shared";
  return "shared";
}

function buildScalePlans(
  spec: PlotSpec,
  layers: readonly CompiledLayerIR[],
  diagnostics: Diagnostic[],
): ScalePlanIR[] {
  const plans: ScalePlanIR[] = [];
  const facetPolicy = spec.facet?.scales;
  for (const channel of ["x", "y", "color", "fill", "size", "alpha", "strokeWidth", "shape", "linetype"] as const) {
    const sourceChannels = scaleChannelsFor(channel);
    const contributors: ScalePlanIR["contributors"] = [];
    const types: SemanticType[] = [];
    for (const layer of layers) {
      const used: Channel[] = [];
      for (const sourceChannel of sourceChannels) {
        const encoding = layer.mapping[sourceChannel];
        if (encoding?.kind !== "field" || encoding.scale === false) continue;
        used.push(sourceChannel);
        types.push(encoding.type);
      }
      if (used.length > 0) contributors.push({ layerId: layer.id, channels: used });
    }
    if (contributors.length === 0) continue;
    const uniqueTypes = uniqueStable(types, (type) => type);
    const incompatible = uniqueTypes.length > 1 &&
      !(uniqueTypes.length === 2 && uniqueTypes.includes("quantitative") && uniqueTypes.includes("temporal"));
    if (incompatible) {
      diagnostics.push(
        diagnostic("error", "scale", "scale.type.conflict", `Channel ${channel} mixes incompatible semantic types: ${uniqueTypes.join(", ")}`, {
          path: `scales.${channel}`,
          hint: "Use independent layers/views or explicitly transform fields to a common type.",
        }),
      );
    }
    const semanticType = uniqueTypes[0] ?? "quantitative";
    const configured = clone(spec.scales?.[channel] ?? {});
    const type = configured.type ?? inferScaleType(channel, semanticType, layers);
    const zeroByGeom = (channel === "y" || channel === "x") && layers.some((layer) => ["bar", "area"].includes(layer.geom.type));
    const scale: ScaleSpec = {
      ...configured,
      type,
      ...(configured.zero === undefined && zeroByGeom && semanticType === "quantitative" ? { zero: true } : {}),
      ...(configured.nice === undefined && (channel === "x" || channel === "y") && semanticType === "quantitative" ? { nice: true } : {}),
    };
    plans.push({
      channel,
      spec: scale,
      semanticType,
      sharing: sharingFor(channel, facetPolicy),
      contributors,
    });
  }
  return plans;
}

function coverageDiagnostics(data: ResolvedData, diagnostics: Diagnostic[], layerId: string): void {
  const coverage = data.coverage;
  if (!coverage || coverage.kind === "complete") return;
  diagnostics.push(
    diagnostic("warning", "resolve", "data.partial", `Layer '${layerId}' is based on ${coverage.kind} data`, {
      nodeId: layerId,
      hint: coverage.note ?? "Keep coverage metadata with the plot and disclose it in exported figure captions.",
      details: {
        kind: coverage.kind,
        hasMore: coverage.hasMore ?? false,
        rows: coverage.rows ?? data.rows.length,
        strategy: coverage.strategy ?? "unknown",
      },
    }),
  );
}

function compileLayer(
  input: ResolvedLayerInput,
  plot: PlotSpec,
  panels: readonly PanelIR[],
  registry: RegistryLike,
  diagnostics: Diagnostic[],
): CompiledLayerIR | null {
  const { spec: layer, data, layerId } = input;
  const geom = registry.geom(layer.geom.type);
  if (!geom) {
    diagnostics.push(diagnostic("error", "validate", "geom.unknown", `Unknown geometry '${layer.geom.type}'`, { nodeId: layerId }));
    return null;
  }
  const statSpec: StatSpec = layer.stat ?? { type: geom.defaultStat ?? "identity" };
  const stat = registry.stat(statSpec.type);
  if (!stat) {
    diagnostics.push(diagnostic("error", "validate", "stat.unknown", `Unknown statistic '${statSpec.type}'`, { nodeId: layerId }));
    return null;
  }
  const position: PositionSpec = layer.position ?? { type: geom.defaultPosition ?? "identity" };
  const merged = mergeMappings(plot.mapping, layer);
  let mapping = resolveMapping(merged, data.schema ?? [], diagnostics, `layers.${layerId}.mapping`, layerId);
  validateChannels(stat.requiredChannels, mapping, diagnostics, "stat", layerId, "stat");
  const groupFields = groupingFields(mapping);
  const assignments: PanelAssignment[] = [];
  data.rows.forEach((row, sourceIndex) => {
    for (const panel of panelsForRow(row, panels, plot.facet)) assignments.push({ panel, row, sourceIndex });
  });
  const byPanelAndGroup = groupBy(assignments, (assignment) =>
    `${assignment.panel.id}|${groupIdFor(assignment.row, groupFields)}`,
  );
  const compiledRows: CompiledDatum[] = [];
  let mappedByStat: ResolvedMapping | undefined;
  for (const assignmentsInGroup of byPanelAndGroup.values()) {
    const first = assignmentsInGroup[0];
    if (!first) continue;
    const groupId = groupIdFor(first.row, groupFields);
    const result = stat.compute({
      layerId,
      rows: assignmentsInGroup.map((assignment) => assignment.row),
      mapping,
      params: statSpec.params ?? {},
      panelId: first.panel.id,
      groupId,
      schema: data.schema ?? [],
    });
    diagnostics.push(...(result.diagnostics ?? []));
    if (result.mapping) {
      if (!mappedByStat) mappedByStat = result.mapping;
      else if (JSON.stringify(mappedByStat) !== JSON.stringify(result.mapping)) {
        diagnostics.push(
          diagnostic("error", "stat", "stat.mapping.unstable", `Statistic '${statSpec.type}' returned different mappings for different groups`, {
            nodeId: layerId,
          }),
        );
      }
    }
    result.rows.forEach((values, resultIndex) => {
      compiledRows.push({
        values,
        panelId: first.panel.id,
        groupId,
        sourceIndex: first.sourceIndex + resultIndex / 1_000_000,
      });
    });
  }
  mapping = mappedByStat ?? mapping;
  mapping = applyPosition(compiledRows, mapping, position, diagnostics, layerId);
  validateChannels(geom.requiredChannels, mapping, diagnostics, "validate", layerId, "geom");
  coverageDiagnostics(data, diagnostics, layerId);
  if (data.rows.length > 250_000) {
    diagnostics.push(
      diagnostic("warning", "resolve", "data.large", `Layer '${layerId}' materialized ${data.rows.length.toLocaleString()} rows in JavaScript`, {
        nodeId: layerId,
        hint: "Push SQL-lowerable stats into DuckDB and pass Arrow record batches to the scene compiler.",
      }),
    );
  }
  return {
    id: layerId,
    geom: clone(layer.geom),
    stat: clone(statSpec),
    position: clone(position),
    mapping,
    rows: compiledRows,
    params: { ...(geom.defaultParams ?? {}), ...(layer.params ?? {}) } as JsonObject,
    showLegend: layer.showLegend ?? true,
    zIndex: layer.zIndex ?? input.layerIndex,
    ...(data.coverage ? { sourceCoverage: clone(data.coverage) } : {}),
    ...(layer.metadata ? { metadata: clone(layer.metadata) } : {}),
  };
}

export interface CompileOptions {
  environment?: DataEnvironment;
  theme?: ThemeSpec;
}

export function compilePlot(
  spec: PlotSpec,
  registry: RegistryLike,
  options: CompileOptions = {},
): CompileResult {
  const diagnostics: Diagnostic[] = [];
  if (spec.format !== "datadrop.gog.plot" || spec.version !== 2) {
    diagnostics.push(
      diagnostic("error", "authoring", "plot.version", `Unsupported plot format ${spec.format}@${spec.version}`, {
        hint: "Run a registered document migration before compilation.",
      }),
    );
    return { ir: null, diagnostics };
  }
  if (spec.layers.length === 0) {
    diagnostics.push(
      diagnostic("error", "authoring", "plot.layers.empty", "A plot needs at least one layer", {
        hint: "Add a geometry such as geomPoint(), geomLine(), or geomBar().",
      }),
    );
    return { ir: null, diagnostics };
  }
  const environment = options.environment ?? {};
  const defaultData = spec.data ? resolveData(spec.data, environment, diagnostics, "data") : null;
  const inputs: ResolvedLayerInput[] = [];
  spec.layers.forEach((layer, layerIndex) => {
    const data = layer.data
      ? resolveData(layer.data, environment, diagnostics, `layers.${layer.id}.data`)
      : defaultData;
    if (data) inputs.push({ layerIndex, layerId: layer.id, data, spec: layer });
  });
  for (const input of inputs) {
    for (const field of input.data.schema ?? []) {
      if (field.name.startsWith(INTERNAL_PREFIX)) {
        diagnostics.push(
          diagnostic("error", "resolve", "field.reserved", `Field '${field.name}' uses the reserved compiler prefix '${INTERNAL_PREFIX}'`, {
            nodeId: input.layerId,
          }),
        );
      }
    }
  }
  const panels = makePanels(spec.facet, inputs, diagnostics);
  const layers = inputs
    .map((input) => compileLayer(input, spec, panels, registry, diagnostics))
    .filter((layer): layer is CompiledLayerIR => layer !== null)
    .sort((a, b) => a.zIndex - b.zIndex);
  const scales = buildScalePlans(spec, layers, diagnostics);
  if (hasErrors(diagnostics)) return { ir: null, diagnostics };
  const ir: PlotIR = {
    format: "datadrop.gog.ir",
    version: 1,
    plotId: spec.id,
    layers,
    panels,
    scales,
    ...(spec.facet ? { facet: clone(spec.facet) } : {}),
    coord: clone(spec.coord ?? { type: "cartesian", clip: true, reverse: "none" }),
    guides: clone(spec.guides ?? []),
    labels: clone(spec.labels ?? {}),
    theme: mergeTheme(themeScientific(), mergeTheme(options.theme ?? {}, spec.theme)),
    ...(spec.metadata ? { metadata: clone(spec.metadata) } : {}),
  };
  return { ir, diagnostics };
}
EOF
```

<details><summary>💭 Thinking</summary>

**Implemented compiler, rendering, DataDrop adapter, and TypeScript fixes**

</details>

```unknown
bash -lc cat > /mnt/data/datadrop-gog-suite/examples/scientific.ts <<'EOF'
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import {
  compilePlot,
  createDefaultRegistry,
  ggplot,
  interpretPlot,
  renderSvg,
  themePublication,
  type Datum,
  type PlotSpec,
} from "../src/index.js";

interface DoseRow extends Datum {
  site: string;
  treatment: string;
  concentration: number;
  response: number;
  replicate: number;
}

function noise(seed: number): number {
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return (x - Math.floor(x) - 0.5) * 2;
}

function doseResponseData(): DoseRow[] {
  const rows: DoseRow[] = [];
  const sites = ["North lab", "South lab"];
  const treatments = ["Control", "Compound A", "Compound B"];
  for (let siteIndex = 0; siteIndex < sites.length; siteIndex += 1) {
    for (let treatmentIndex = 0; treatmentIndex < treatments.length; treatmentIndex += 1) {
      for (let concentration = 1; concentration <= 10; concentration += 1) {
        for (let replicate = 1; replicate <= 4; replicate += 1) {
          const slope = [0.35, 0.95, 1.35][treatmentIndex]!;
          const offset = [5.1, 4.5, 3.8][treatmentIndex]! + siteIndex * 0.8;
          rows.push({
            site: sites[siteIndex]!,
            treatment: treatments[treatmentIndex]!,
            concentration,
            response: offset + slope * concentration + noise(siteIndex * 1000 + treatmentIndex * 100 + concentration * 10 + replicate) * 1.15,
            replicate,
          });
        }
      }
    }
  }
  return rows;
}

function scientificScatter(): PlotSpec<DoseRow> {
  const rows = doseResponseData();
  return ggplot(rows)
    .named("dose-response")
    .aes((aes) => aes.x("concentration", "quantitative").y("response", "quantitative").color("treatment", "nominal").group("treatment", "nominal"))
    .geomSmooth((layer) => layer.strokeWidth(2).zIndex(0))
    .geomPoint((layer) => layer.size(3.2).alpha(0.68).zIndex(1))
    .facetWrap("site", (facet) => facet.columns(2).scales("fixed"))
    .scaleX((scale) => scale.linear().nice().zero(false).expand(0.03))
    .scaleY((scale) => scale.linear().nice().zero(false).expand(0.05))
    .scaleColor((scale) => scale.ordinal().title("Treatment"))
    .labs((labels) =>
      labels
        .title("Dose–response experiment")
        .subtitle("Ordinary least-squares trend with pointwise 95% confidence bands")
        .x("Concentration (µmol/L)")
        .y("Normalized response (a.u.)")
        .caption("Synthetic demonstration data · n = 4 replicates per concentration")
        .description("Two faceted dose-response scatterplots. Each treatment has observed points, a fitted linear trend, and a 95 percent confidence band."),
    )
    .theme(themePublication({ options: { gridY: true, gridX: false, outerAxesOnly: true } }))
    .build();
}

function uncertaintySummary(): PlotSpec<DoseRow> {
  const rows = doseResponseData().filter((row) => row.concentration === 8);
  return ggplot(rows)
    .named("uncertainty-summary")
    .aes((aes) => aes.x("treatment", "nominal").y("response", "quantitative").color("treatment", "nominal"))
    .geomPointrange((layer) =>
      layer
        .stat("summary", { fun: "mean_ci", level: 0.95 })
        .position("dodge")
        .size(4.4)
        .strokeWidth(1.35),
    )
    .facetWrap("site", (facet) => facet.columns(2))
    .scaleY((scale) => scale.nice().zero(false).expand(0.1))
    .scaleColor((scale) => scale.ordinal().guide("none"))
    .labs((labels) =>
      labels
        .title("Response at 8 µmol/L")
        .subtitle("Mean and t-based 95% confidence interval")
        .x("Treatment")
        .y("Normalized response (a.u.)")
        .caption("Intervals summarize four synthetic replicates per site and treatment."),
    )
    .theme(themePublication({ options: { gridY: true, legendPosition: "none" } }))
    .build();
}

interface DistributionRow extends Datum {
  cohort: string;
  value: number;
}

function distributionData(): DistributionRow[] {
  const rows: DistributionRow[] = [];
  for (let index = 0; index < 160; index += 1) {
    rows.push({ cohort: "Reference", value: 50 + noise(index + 1) * 8 + noise(index * 3 + 7) * 3 });
    rows.push({ cohort: "Intervention", value: 58 + noise(index + 501) * 7 + noise(index * 5 + 11) * 2.5 });
  }
  return rows;
}

function densityPlot(): PlotSpec<DistributionRow> {
  return ggplot(distributionData())
    .named("density-comparison")
    .aes((aes) => aes.x("value", "quantitative").color("cohort", "nominal").fill("cohort", "nominal").group("cohort", "nominal"))
    .geomDensity((layer) => layer.alpha(0.24).strokeWidth(1.7))
    .scaleX((scale) => scale.nice().zero(false))
    .scaleY((scale) => scale.nice().zero(true))
    .scaleColor((scale) => scale.ordinal().title("Cohort"))
    .scaleFill((scale) => scale.ordinal().title("Cohort"))
    .labs((labels) =>
      labels
        .title("Distribution comparison")
        .subtitle("Gaussian kernel density estimate with Silverman bandwidth")
        .x("Measurement")
        .y("Density")
        .caption("Synthetic demonstration data · 160 observations per cohort"),
    )
    .theme(themePublication({ options: { gridY: true } }))
    .build();
}

function emit(name: string, spec: PlotSpec, width: number, height: number): void {
  const registry = createDefaultRegistry();
  const compiled = compilePlot(spec, registry);
  if (!compiled.ir) {
    throw new Error(`Compilation failed for ${name}:\n${compiled.diagnostics.map((item) => `${item.code}: ${item.message}`).join("\n")}`);
  }
  const interpreted = interpretPlot(compiled.ir, registry, { width, height });
  if (!interpreted.scene) {
    throw new Error(`Interpretation failed for ${name}:\n${interpreted.diagnostics.map((item) => `${item.code}: ${item.message}`).join("\n")}`);
  }
  const output = join(process.cwd(), "examples", "output");
  mkdirSync(output, { recursive: true });
  writeFileSync(join(output, `${name}.svg`), renderSvg(interpreted.scene, { pretty: true }));
  writeFileSync(join(output, `${name}.ir.json`), JSON.stringify(compiled.ir, null, 2));
  writeFileSync(join(output, `${name}.scene.json`), JSON.stringify(interpreted.scene, null, 2));
  const warnings = [...compiled.diagnostics, ...interpreted.diagnostics].filter((item) => item.severity !== "info");
  console.log(`${name}: ${interpreted.scene.nodes.length} top-level nodes, ${warnings.length} warnings/errors`);
}

emit("scientific-scatter", scientificScatter(), 1120, 620);
emit("uncertainty-summary", uncertaintySummary(), 1020, 540);
emit("density-comparison", densityPlot(), 900, 520);
EOF
```

<details><summary>💭 Thinking</summary>

**Compiled scientific plotting examples**

**Designing the implementation**

I’m now translating the architecture into concrete TypeScript files: staged compiler passes, registries, statistical transforms, shared scales, scene construction, and deterministic SVG output, with the report documenting tradeoffs and migration steps.

**Engineering a reference suite**

I’m assembling the report and implementation around a staged, extensible compiler: fluent builders become serializable specifications, specifications become validated IR, and IR becomes backend-neutral scenes for deterministic graph output.

**Designed implementation and engineered a reference suite**

</details>

```unknown
bash -lc find /mnt/data/datadrop-gog-suite -maxdepth 3 -type f -printf '%P
' | sort | sed -n '1,240p' && printf '\n--- package ---\n' && cat /mnt/data/datadrop-gog-suite/package.json && printf '\n--- git? ---\n' && du -sh /mnt/data/datadrop-gog-suite
```

<details><summary>💭 Thinking</summary>

**Applying scale patch and rebuilding project**

</details>

```unknown
bash -lc cat > /mnt/data/datadrop-gog-suite/examples/node-shim.d.ts <<'EOF'
declare module "node:fs" {
  export function mkdirSync(path: string, options?: { recursive?: boolean }): string | undefined;
  export function writeFileSync(path: string, data: string | Uint8Array): void;
}

declare module "node:path" {
  export function join(...paths: string[]): string;
}

declare const process: {
  cwd(): string;
};
EOF
cd /mnt/data/datadrop-gog-suite && npm run build && npm run examples
```

<details><summary>💭 Thinking</summary>

**Updating Top-Level Marks Group Test**

</details>

```unknown
bash -lc sed -n '760,870p' /mnt/data/datadrop-gog-suite/src/builder.ts
```

<details><summary>💭 Thinking</summary>

**Implemented coordinate validation, axis orientation, and bottom legend rendering with tests**

</details>

```json
{"search_query":[{"q":"site:ggplot2.tidyverse.org/reference ggplot2 layer data mapping stat geom position official"},{"q":"site:vega.github.io/vega-lite documentation layering faceting transforms selections official"},{"q":"site:observablehq.com/plot features scales facets official Observable Plot"},{"q":"site:duckdb.org/docs/stable/clients/wasm DuckDB Wasm official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

```unknown
bash -lc cat > /mnt/data/datadrop-gog-suite/README.md <<'EOF'
# DataDrop Grammar-of-Graphics Suite — TypeScript Reference Kernel

This package is a substantial, dependency-free reference implementation for evolving
[`go-go-golems/go-go-datadrop`](https://github.com/go-go-golems/go-go-datadrop)
from its current single-view plot builder into a layered, extensible grammar-of-graphics
system for professional and scientific figures.

It is not presented as a drop-in finished product. It is an executable architecture:

```text
immutable fluent builder
        ↓
serializable PlotSpec v2
        ↓
validated/statistically evaluated PlotIR
        ↓
layout + scale interpretation
        ↓
backend-neutral SceneGraph
        ↓
SVG or Canvas
```

The design report in [`REPORT.md`](./REPORT.md) explains the repository audit,
production architecture, compiler passes, plugin ABI, data-execution strategy,
scientific correctness requirements, and phased migration plan.

## What is implemented

- Immutable, typed fluent authoring API with configuration lambdas.
- Serializable and versioned `PlotSpec`; no callbacks or React nodes survive authoring.
- Layer inheritance and per-layer data, mappings, stats, positions, parameters, and z-order.
- Aesthetic channels for position intervals, colour, fill, stroke, size, shape, alpha,
  linewidth, linetype, grouping, detail, labels, tooltips, weights, and order.
- Facet wrap and facet grid with fixed or free position scales.
- Cartesian, fixed-aspect, and flipped coordinates; clipping can be disabled.
- Built-in stats: identity, count, bin/histogram, summary intervals, linear regression with
  confidence bands, kernel density, and boxplot summaries.
- Built-in positions: identity, stack, fill, dodge, and deterministic jitter.
- Built-in scales: linear, logarithmic, symlog, square root, power, local/UTC time,
  band, point, ordinal, quantile, quantize, threshold, and identity.
- Built-in geoms: point, line, bar/column, area, ribbon, smooth, error bar,
  point-range, rectangle, rule, text, and boxplot.
- Scientific, publication, minimal, and dark themes.
- Guide inference and compatible colour/fill guide coalescing.
- Explicit diagnostics instead of silent fallbacks, including rejection of invalid log domains.
- Source coverage/provenance propagation for bounded, sampled, and stream-window data.
- Extensible registries for stats, geoms, scales, and formatters.
- Backend-neutral scene graph, deterministic SVG renderer, and Canvas interpreter.
- Structural adapter from the current DataDrop v1 evaluated view model.
- Executable examples and Node test suite.

## Run

Node 22 or later and TypeScript 5.8 or later are sufficient. No runtime packages are required.

```bash
npm run check
```

The command compiles the project, runs the tests, and regenerates the example SVG, IR,
and scene files under `examples/output/`.

Other commands:

```bash
npm run build
npm test
npm run examples
```

## Minimal example

```ts
import {
  compilePlot,
  createDefaultRegistry,
  ggplot,
  interpretPlot,
  renderSvg,
  themePublication,
} from "@datadrop/gog-suite-reference";

const rows = [
  { dose: 1, response: 4.2, treatment: "control", site: "north" },
  { dose: 2, response: 4.8, treatment: "control", site: "north" },
  { dose: 1, response: 5.0, treatment: "active", site: "north" },
  { dose: 2, response: 6.7, treatment: "active", site: "north" },
];

const spec = ggplot(rows)
  .aes((aes) =>
    aes
      .x("dose", "quantitative")
      .y("response", "quantitative")
      .color("treatment", "nominal")
      .group("treatment", "nominal"),
  )
  .geomSmooth((layer) => layer.strokeWidth(2).zIndex(0))
  .geomPoint((layer) => layer.size(3.2).alpha(0.7).zIndex(1))
  .facetWrap("site")
  .scaleX((scale) => scale.linear().nice().zero(false))
  .scaleY((scale) => scale.linear().nice().zero(false))
  .labs((labels) =>
    labels
      .title("Dose response")
      .x("Dose (µmol/L)")
      .y("Response (a.u.)")
      .description("Observed values with fitted linear trends and confidence bands."),
  )
  .theme(themePublication())
  .build();

const registry = createDefaultRegistry();
const compiled = compilePlot(spec, registry);
if (!compiled.ir) throw new Error(JSON.stringify(compiled.diagnostics, null, 2));

const interpreted = interpretPlot(compiled.ir, registry, { width: 960, height: 540 });
if (!interpreted.scene) throw new Error(JSON.stringify(interpreted.diagnostics, null, 2));

const svg = renderSvg(interpreted.scene, { pretty: true });
```

## Builder composition

Builders are immutable. Configuration lambdas mutate only short-lived helper objects and are
immediately compiled into JSON-compatible values. Reusable components remain ordinary functions:

```ts
import { component, type Datum } from "./src/index.js";

const publicationAxes = component<Datum>((plot) =>
  plot
    .scaleX((scale) => scale.nice().zero(false).expand(0.03))
    .scaleY((scale) => scale.nice().zero(false).expand(0.05))
    .theme((theme) => theme.grid({ x: false, y: true })),
);

const figure = ggplot(rows)
  .aes((aes) => aes.x("x").y("y"))
  .geomPoint()
  .use(publicationAxes)
  .build();
```

A built `PlotSpec` can be cloned, serialized, diffed, migrated, sent to a worker, stored in a
DataDrop document, or lowered by another backend.

## Extension example

The extension ABI separates statistical computation from graphical display. A stat answers
“what values should be shown”; a geom answers “how should those values be drawn”.

```ts
const registry = createDefaultRegistry();

registry.registerStat({
  id: "double-y",
  requiredChannels: ["y"],
  compute(context) {
    const y = context.mapping.y;
    if (y?.kind !== "field") return { rows: [] };
    return {
      rows: context.rows.map((row) => ({ ...row, double_y: Number(row[y.field]) * 2 })),
      mapping: {
        ...context.mapping,
        y: { kind: "field", field: "double_y", source: "stat", type: "quantitative" },
      },
    };
  },
});
```

Custom geoms return scene nodes, not SVG or React elements. This keeps them compatible with all
rendering backends.

## Example outputs

`npm run examples` writes:

- `examples/output/scientific-scatter.svg` — faceted observations, OLS fits, and 95% bands.
- `examples/output/uncertainty-summary.svg` — means with t-based 95% intervals.
- `examples/output/density-comparison.svg` — grouped kernel-density estimates.
- Matching `.ir.json` and `.scene.json` files for inspection and golden testing.

PNG previews produced during validation are under `examples/preview/`.

## Source layout

```text
src/
  builder.ts           immutable fluent authoring API
  types.ts             authoring AST, compiler IR, scene IR, plugin contracts
  compiler.ts          resolution, validation, stats, grouping, facets, positions, scale plans
  stats.ts             built-in statistical transforms
  scales.ts            scale training, mapping, ticks, formatting
  geoms.ts             scene construction for built-in graphical marks
  interpreter.ts       layout, axes, legends, panels, accessibility, scene assembly
  render-svg.ts        deterministic vector backend
  render-canvas.ts     immediate-mode Canvas backend
  registry.ts          extension registry
  themes.ts            opinionated themes and palettes
  datadrop-adapter.ts  migration seam from the current v1 view
  index.ts             public API and convenience facade
examples/
  scientific.ts        executable scientific figure examples
  output/               generated SVG, PlotIR, and SceneGraph files
test/
  kernel.test.ts        authoring, compiler, correctness, plugins, rendering, migration
```

## Deliberate boundaries

The reference kernel demonstrates the semantic and rendering seams. A production DataDrop suite
should add composition trees, selections and reactive signals, SQL/Arrow stat pushdown, text
measurement services, vector PDF output, WebGL/raster layers, richer temporal ticks, spatial
coordinates, unit algebra, expression compilation, schema-driven plugin editors, and formal IR
migration packages. Those items are designed in `REPORT.md`; they are not falsely represented as
complete here.
EOF
cat > /mnt/data/datadrop-gog-suite/LICENSE <<'EOF'
MIT License

Copyright (c) 2026 DataDrop grammar-of-graphics reference implementation contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
cd /mnt/data/datadrop-gog-suite && npm run check
```

<details><summary>💭 Thinking</summary>

**Created architecture README documentation**

**Fetching Exact Chart Panel Implementation**

**Building the plotting suite**

I’m consolidating the repository analysis, research, implementation, tests, and generated graph examples into the final deliverables. The result is a staged TypeScript plotting kernel with fluent authoring, explicit IR, statistical layers, and deterministic rendering.

**Built the plotting suite**

</details>

```unknown
bash -lc find /mnt/data/datadrop-gog-suite -maxdepth 3 -type f | sort | sed -n '1,240p' && printf '\n--- package ---\n' && cat /mnt/data/datadrop-gog-suite/package.json && printf '\n--- size ---\n' && du -sh /mnt/data/datadrop-gog-suite
```

<details><summary>💭 Thinking</summary>

**Inspected project files, README, and API types for report alignment**

</details>

```unknown
bash -lc cat > REPORT.md <<'EOF'
# Engineering a Professional Grammar-of-Graphics Suite for DataDrop

**Repository reviewed:** [`go-go-golems/go-go-datadrop`](https://github.com/go-go-golems/go-go-datadrop)  
**Target:** browser-first TypeScript plotting system for professional and scientific graphics  
**Architectural style:** immutable fluent authoring API → serializable authoring document → typed compiler IR → interpreted scene graph → SVG / Canvas / future backends  
**Reference implementation:** `@datadrop/gog-suite-reference` in this package  
**Date:** 2026-07-28

---

## Executive summary

DataDrop already has the correct foundation for a serious plotting system. It does **not** need to discard its compiler architecture or replace its workbench with a thin wrapper around a third-party chart component. The current codebase already contains four unusually valuable seams:

1. a typed tabular boundary between storage and visualization;
2. a serializable `GraphicDocument` authoring model;
3. a compiler from that authoring model to a typed logical relational graph;
4. a pure plot builder that emits geometry independently of React and SVG.

Those choices are sound. The present limitation is narrower: the *graphics grammar* is still encoded as a small set of closed TypeScript unions and one monolithic plotting algorithm. The current view supports four marks (`point`, `line`, `bar`, `area`), five channels (`x`, `y`, `color`, `size`, `facet`), one layer, one facet variable, and only a linear/logarithmic y-scale switch. Rendering is then implemented with chart-specific SVG logic. This is a good workbench MVP, but extending it by adding more branches to `buildPlotFromResult` will produce a rigid plotting engine rather than a grammar.

The recommended system preserves the existing relational compiler and DuckDB execution path, then adds a second compiler boundary specifically for graphics:

```text
DataDrop source / relation graph
              │
              ▼
       evaluated typed relation
              │
              ▼
 PlotSpec v2 (authoring grammar)
              │
              ▼
 semantic graphics compiler
   ├─ resolve mappings and inheritance
   ├─ partition facets and groups
   ├─ run/lower statistics
   ├─ apply position adjustments
   ├─ train and validate scales
   ├─ plan guides and coordinates
   └─ preserve coverage/provenance
              │
              ▼
            PlotIR
              │
              ▼
 layout + scale interpreter
              │
              ▼
          SceneGraph IR
       ┌──────┼────────┐
       ▼      ▼        ▼
      SVG   Canvas    future PDF/WebGL
```

The central design decision is: **geoms, stats, scales, coordinates, guides, formatters, and themes are registered compiler/interpreter plugins, not hard-coded switches in UI components.** The fluent API is an ergonomic front end over a versioned JSON-compatible `PlotSpec`; it is not itself the storage model. Configuration lambdas may configure temporary builders, but functions never survive into persisted specifications or compiler IR.

The reference implementation supplied with this report demonstrates that architecture end to end. It includes an immutable fluent builder, layer inheritance, facets, statistics, positions, scales, themes, diagnostics, coverage provenance, extensible registries, a backend-neutral scene graph, deterministic SVG output, a Canvas interpreter, tests, and three generated scientific figures. It is a substantial executable vertical slice, not a claim that every production feature listed in this report is already complete.

### Direct recommendation

Implement the production system in three deliberate strata:

- **Relational analysis stays where it is.** Continue compiling the existing `GraphicDocument` transform graph to DuckDB SQL. Add richer relational operators separately; do not make every geom responsible for data manipulation.
- **Introduce a versioned graphics grammar above evaluated relations.** A plot contains layers, mappings, stats, geoms, positions, scales, coordinates, facets, guides, labels, themes, parameters, annotations, and composition.
- **Render only a scene graph.** React should display the scene and attach DataDrop/PBUI interactions. It should not compute domains, ticks, statistics, positions, or geometry.

This approach gives DataDrop an opinionated default experience while retaining customization at every layer. It also avoids coupling scientific semantics to SVG, React, DuckDB, or a single browser rendering strategy.

---

## 1. Scope and product definition

The requested system is broader than “more chart types.” A professional plotting suite must be able to represent, validate, compute, render, inspect, export, and reproduce a scientific figure. The product should support at least the following workflows:

- exploratory plots that choose useful defaults from typed data;
- publication figures with explicit scales, labels, units, themes, and dimensions;
- statistical graphics such as histograms, densities, confidence intervals, regression fits, boxplots, quantiles, smoothers, and reference regions;
- layered graphics in which raw observations, summaries, models, and annotations coexist;
- faceted and composed figures with controlled scale sharing;
- deterministic vector export and high-resolution raster export;
- large-data plots that are honest about sampling, truncation, aggregation, and rasterization;
- interactive selections whose semantics are stored as parameters, not hidden component state;
- reusable plot components that can be composed in TypeScript;
- serializable documents that survive persistence, migration, collaboration, and headless rendering;
- third-party extensions without allowing plugins to bypass diagnostics, provenance, or rendering backends.

A grammar-of-graphics system is valuable because it models these as combinations of orthogonal concepts rather than as a catalog of unrelated chart constructors. Wilkinson’s grammar and Wickham’s layered formulation treat a layer as a combination of data, aesthetic mapping, statistical transformation, geometric object, and position adjustment. The current ggplot2 documentation states this decomposition explicitly in [`layer()`](https://ggplot2.tidyverse.org/reference/layer.html), and separates [`geoms`](https://ggplot2.tidyverse.org/reference/index.html#geoms) from [`stats`](https://ggplot2.tidyverse.org/reference/index.html#stats). Vega-Lite demonstrates a complementary compiler architecture: a concise declarative input is normalized and compiled into a lower-level Vega program rather than rendered directly from the authoring object. See the [Vega-Lite documentation](https://vega.github.io/vega-lite/docs/) and [specification overview](https://vega.github.io/vega-lite/docs/spec.html).

DataDrop should adopt both lessons:

1. use the layered grammar as its semantic model;
2. use compiler passes and explicit intermediate representations rather than interpreting loose authoring JSON in React.

---

## 2. Repository audit

### 2.1 What the current architecture gets right

#### A single typed table boundary

The visualization design correctly insists that charts consume typed tables, not storage-specific stream or dataset objects. This makes source projection, truncation, schema ownership, and visualization independent. It is the right contract for DuckDB ingestion, testing, and later Arrow-based execution.

#### A serializable authoring document

`ui/src/model/graphic.ts` defines `GraphicDocument` as a versioned, JSON-compatible document with sources, transforms, views, parameters, and metadata. It distinguishes semantic types from physical types and stores stable field identities. This is substantially better than saving component state or callback closures.

The current model already has useful compiler-grade concepts:

- `PhysicalType` and `SemanticType` are separate;
- mappings use stable `FieldId` values where available;
- relation fields carry source/operation provenance;
- source coverage records bounded windows and whether more rows exist;
- disabled transforms resolve transparently to their inputs;
- invalid, missing, cyclic, ambiguous, or incomplete nodes produce diagnostics rather than arbitrary behavior.

These are the beginnings of a proper language implementation, not merely a chart configuration object.

#### A real logical compiler

`compileGraphicDocument` resolves source schemas, walks the relation graph, type-checks expressions, validates aggregates and projections, preserves relation coverage, and emits ordered `LogicalOperation` values. `ui/src/analysis/compile.ts` then lowers those operations into parameterized DuckDB SQL. `AnalysisRuntime` owns a worker/database/connection lifecycle, caps result rows, normalizes Arrow output, and reports execution metrics.

This division should remain. It means the future plotting system can ask for a typed evaluated relation and does not need to reimplement filtering, deriving, aggregation, sorting, or limiting in every renderer.

#### Pure geometry before React

`ui/src/model/plot.ts` is intentionally a pure function from rows, fields, view, and size to drawable geometry. `ChartPanel` performs no scale arithmetic. This is one of the strongest choices in the repository: geometry tests can run without a DOM, and React remains a presentation layer.

#### Honest partial-result reporting

The current system reports source truncation, mark overflow, facet overflow, missing reference lines, and invalid mappings. It refuses to draw invalid specifications with actionable messages. That posture is essential for scientific graphics and must become a system-wide invariant.

#### PBUI interaction integration

Current marks are wrapped as typed presentations, allowing a plotted datum or legend category to produce real document operations such as filters. This is more coherent than maintaining a separate chart-only interaction model. The future scene graph should preserve data identities and semantic hit targets so the same interaction architecture continues to work.

### 2.2 Where the current graphics model stops scaling

The current authoring view is structurally equivalent to:

```ts
interface AuthoringView {
  relation: RelationRef;
  mark: "point" | "line" | "bar" | "area";
  encodings: Partial<Record<"x" | "y" | "color" | "size" | "facet", FieldRef>>;
  yScale: "linear" | "log";
  references?: ReferenceLine[];
}
```

This creates several constraints.

#### One view means one layer

A scientific plot commonly needs raw observations, a model fit, an uncertainty band, a target line, and a label layer. Those layers may use different data, mappings, stats, groups, and z-orders. Encoding them as one mark plus special “references” fields will cause every new layer type to become an exception in `AuthoringView`.

#### Stats are confused with transforms or renderer behavior

A histogram is not simply a bar geom. It requires binning, count/density computation, and post-stat mappings. A boxplot is not five hand-authored layers in the UI. A smooth is not a line through original rows. These require a first-class `Stat` abstraction whose outputs can be mapped by later stages.

#### Scales are not just an axis toggle

A complete scale model needs independent control over transformation, domain, range, out-of-bounds policy, expansion, reversal, breaks, labels, missing values, palettes, guide behavior, and facet sharing. Logarithmic scaling must validate its domain; zooming through coordinates must not accidentally delete data before a statistic is computed.

#### Faceting is coupled to one channel

Professional faceting needs wrap and grid layouts, row/column variables, ordering, labellers, empty-cell policy, pagination, margins, and fixed/free x/y scales. A single `facet` aesthetic cannot express those semantics.

#### Grouping is inferred from one color channel

Lines, ribbons, dodged summaries, and model fits need an explicit grouping model. `group`, `detail`, `order`, `weight`, and panel keys are compiler semantics, not renderer conveniences.

#### Geom logic, scale logic, layout, and rendering are interleaved

`buildPlotFromResult` currently performs validation, facet partitioning, color-scale training, position-scale training, tick generation, panel layout, geom grouping, path construction, overflow capping, and guide construction in one function. It remains testable, but it is not independently extensible.

#### The output geometry is chart-specific rather than backend-neutral

The current `Plot` structure is close to a scene graph but still exposes chart concepts such as one global tick list, one legend, and marks that know a narrow set of SVG primitives. It should evolve into a general scene with groups, clips, transforms, styles, text, symbols, gradients, metadata, hit targets, and accessibility descriptions.

#### UI choices are compiled into closed arrays

`MARKS`, `CHANNELS`, and `CHANNEL_ACCEPTS` are fixed constants. A plugin cannot add a violin geom or a custom statistical interval without changing the core TypeScript unions and editor code. The UI should be generated from registry descriptors and JSON-compatible option schemas.

### 2.3 The key conclusion from the audit

The codebase does not need a replacement “chart library.” It needs a **graphics language layer** inserted between evaluated relational data and the scene renderer.

Preserve:

- the typed table contract;
- stable field identity and provenance;
- the relation compiler;
- DuckDB-Wasm execution;
- pure non-React compilation;
- diagnostic-first failure behavior;
- PBUI semantic interaction.

Replace or generalize:

- single-view/single-mark authoring;
- fixed mark and channel unions as the extension mechanism;
- renderer-specific special cases in the document;
- monolithic plot building;
- one-off SVG component logic;
- chart-specific legends, axes, and facet layouts.

---

## 3. Design principles

### 3.1 The persisted specification is data, never behavior

The authoring document must remain JSON-compatible. Callbacks are allowed only while constructing a specification:

```ts
const plot = ggplot(rows)
  .aes((aes) => aes.x("dose").y("response").color("treatment"))
  .geomPoint((layer) => layer.size(3).alpha(0.65))
  .scaleY((scale) => scale.log10().breaks([1, 10, 100]))
  .build();
```

The lambda receives a short-lived typed builder. Calling `.build()` produces plain values. No callback, class instance, DOM node, React node, closure, or function pointer enters `PlotSpec`, `PlotIR`, or `SceneGraph`.

This gives the user the ergonomics of a fluent TypeScript DSL while retaining deterministic serialization, diffing, migration, worker transfer, reproducibility, and headless execution.

### 3.2 Defaults should be strong and inspectable

An opinionated plotting system should make a credible figure from minimal input. It should infer semantic types, select readable scales, use accessible palettes, choose sensible tick counts, merge compatible guides, include zero where magnitude semantics require it, and sort temporal paths.

Every inferred choice must remain inspectable in compiled IR or diagnostics. “Automatic” must not mean “hidden.” A scientific user should be able to see that a domain was expanded, a palette was selected, a statistic removed invalid rows, or a source was sampled.

### 3.3 Customization occurs through orthogonal components

Do not create constructors such as `professionalScatterWithRegressionAndCI`. Compose:

```ts
plot
  .geomSmooth((l) => l.method("lm").confidence(0.95))
  .geomPoint((l) => l.alpha(0.55))
  .facetWrap("site")
  .scaleColor((s) => s.ordinal().palette("okabe-ito"))
  .coord((c) => c.fixed(1))
  .theme(themePublication())
  .labs((l) => l.title("Dose response").x("Dose (µM)").y("Response (a.u.)"));
```

Each component has one semantic responsibility and can be overridden without replacing the rest of the plot.

### 3.4 Compiler phases are explicit and testable

Do not let a plugin silently perform work from another phase. A stat returns computed rows and mappings; a geom returns scene nodes from trained scales; a scale trains and maps values; a guide renders a scale description; a coordinate maps panel coordinates to screen coordinates. This separation allows deterministic tests and backend substitution.

### 3.5 No silent loss or semantic fallback

The compiler/interpreter must report:

- source truncation or sampling;
- result truncation;
- dropped missing/non-finite/out-of-domain values;
- invalid logarithmic domains;
- categories or facets omitted by explicit limits;
- rasterized layers;
- approximate statistics;
- unresolved fields or stale mappings;
- incompatible shared scale requirements;
- unsupported renderer capabilities;
- non-embedded or substituted fonts during export.

A fallback may be allowed only when it is declared by policy and surfaced as a diagnostic. For example, an interactive preview may choose Canvas for 200,000 points, but the scene metadata must state that the layer was rasterized.

### 3.6 Source coverage is part of the plot meaning

DataDrop already knows whether the source relation is a bounded head/latest window. Extend that model to represent exact, sampled, aggregated, streamed, and approximate coverage. Every compiled layer must retain coverage lineage. A caption or export manifest can then state exactly what the figure represents.

### 3.7 The scene graph is the rendering contract

SVG, Canvas, PDF, and WebGL backends must interpret the same semantic scene where feasible. A geom plugin produces scene primitives, not JSX and not an SVG path string as its only interface. Backend-specific optimizations are allowed behind capability negotiation.

### 3.8 Stable IDs matter at every level

Fields, layers, scales, panels, guides, scene nodes, parameters, and interaction targets need stable identities. Stable IDs enable incremental compilation, selection preservation, undo/redo, diffing, animation, testing, and PBUI actions.

---
EOF
```

The end-to-end kernel now passes strict compilation and tests, renders verified scientific SVG/PNG examples, and includes a tested v1-to-v2 adapter. I’m packaging the report and artifacts.

<details><summary>💭 Thinking</summary>

**Checking npm installation status**

</details>

```unknown
bash -lc npm run check
```

<details><summary>💭 Thinking</summary>

**Ran package checks, analyzed images, corrected uncertainty wording, and packaged outputs**

</details>

```json
{"paths":["GitHub"],"query":"repository"}
```

```json
{"uri":"/response/turn30","query":"MaxStreamTableRows"}
```

```json
{"uri":"/response/turn30","start_line":1,"num_lines":50}
```

```json
{"paths":["GitHub"],"query":"fetch_file"}
```

## Delivered

- [Full architecture and repository analysis report](sandbox:/mnt/data/datadrop-professional-plotting-suite/datadrop-plotting-suite-report.md)
- [Complete TypeScript implementation, tests, compiled JavaScript, examples, IR files, and graph outputs](sandbox:/mnt/data/datadrop-professional-plotting-suite.zip)
- [Implementation README and API guide](sandbox:/mnt/data/datadrop-professional-plotting-suite/README.md)
- [Generated graph gallery](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/gallery.html)
- [Archive SHA-256 checksum](sandbox:/mnt/data/datadrop-professional-plotting-suite.zip.sha256)

## Principal conclusion

DataDrop already has a strong foundation: typed tables, explicit coverage, a serializable graphics document, stable field symbols in the logical relational graph, parameterized DuckDB compilation, and a pure geometry function. The physical DuckDB compiler is especially worth retaining: it resolves stable field identities to deterministic aliases, compiles only the required relation chain, and emits parameterized CTE SQL. fileciteturn25file0L221-L317

The main architectural problem occurs immediately after that. The current plot compiler returns to authoring field **names**, builds a name-to-type map, and reads channels using those names. This discards the stable field identity and provenance established by the relational compiler. fileciteturn33file0L206-L252

The current plot pass is admirably pure and DOM-independent, but it also centralizes nearly every visual concern and embeds fixed policies such as one palette, eight categories, six facets, and 5,000 marks per panel. fileciteturn33file0L3-L8 fileciteturn33file0L17-L44 The presentation layer is subsequently tied to a React-hosted SVG vocabulary, including axes, legends, marks, and PBUI datum wrappers. fileciteturn27file0L113-L218

My recommended replacement is:

```text
immutable fluent builder
    ↓
datadrop.plot.document@2
    ↓  migration, binding, type checking, desugaring
LogicalPlot
    ↓  transforms, statistics, positions
physical analytical plan
    ↓  DuckDB / Arrow / test interpreter
executed layer tables
    ↓  scale training, facets, guides, layout
backend-neutral SceneGraph
    ↓
SVG | Canvas | WebGL/WebGPU | PDF | PNG
```

The layer is the primary composition unit:

```text
data + mapping + transforms + stat + position + geom
```

That separation follows the layered grammar implemented by ggplot2, while the explicit authoring-to-runtime compilation model follows the successful distinction used by Vega-Lite and Vega. Observable Plot provides a useful JavaScript precedent for composing charts from layered marks rather than named chart classes. citeturn856890view1turn856890view2turn856890view3

## TypeScript implementation

The delivered package contains approximately 7,900 lines of TypeScript, examples, and tests. Its public API uses immutable builders and immediate configuration lambdas:

```ts
const chart = plot(table)
  .mapping((m) => m
    .x("time")
    .y("response")
    .color("treatment")
    .group("treatment"))
  .layer((layer) => layer
    .name("Observed values")
    .point((geom) => geom.radius(2.2).opacity(0.35)))
  .layer((layer) => layer
    .name("95% confidence band")
    .stat((stat) => stat.linearRegression({
      confidence: 0.95,
      points: 90,
    }))
    .ribbon((geom) => geom.opacity(0.18)))
  .layer((layer) => layer
    .name("Linear model")
    .stat((stat) => stat.linearRegression({
      confidence: 0.95,
      points: 90,
    }))
    .line((geom) => geom.strokeWidth(2.4)))
  .facet((facet) => facet
    .wrap("batch")
    .columns(2)
    .scales("fixed"))
  .scales((scales) => {
    scales.x((scale) => scale
      .linear()
      .zero(true)
      .nice(6));

    scales.y((scale) => scale
      .linear()
      .zero(false)
      .nice(6));

    scales.color((scale) => scale
      .categorical()
      .title("Treatment"));
  })
  .theme((theme) => theme.preset("publication"));
```

The lambdas are not retained. They configure a private cloned draft, after which the builder contains only serializable IR. Calling `chart.toJSON()` therefore produces a versioned document with no closures, classes, DOM objects, or runtime plugins.

Implemented subsystems include:

| Subsystem | Included |
|---|---|
| Authoring | Immutable `PlotBuilder`, nested configuration builders, parameters, expressions, metadata |
| Compilation | Stable-field binding, transform schemas, mapping inheritance, `afterStat`, diagnostics, scale inference |
| Transforms | Filter, mutate, select, aggregate, sort, limit, bin, fold, deterministic sampling |
| Statistics | Identity, count, histogram binning, summaries and intervals, regression and confidence bands, density, boxplot |
| Positions | Identity, stack, proportional fill, dodge, seeded jitter |
| Geoms | Point, line, area, bar, ribbon, error bar, rule, text, boxplot |
| Scales | Linear, log, symlog, sqrt/power, time/UTC, band, point, ordinal, categorical, sequential, diverging |
| Composition | Multiple layers, shared mappings, multiple data sources, facet wrap/grid, fixed/free scale declarations |
| Presentation | Professional, publication, and dark themes; titles, captions, axes, grids, legends |
| Rendering | Backend-neutral scene IR, accessible SVG, Canvas interpreter, automatic backend policy |
| Extensibility | Namespaced stat, position, and geom registries |
| Migration | Current `datadrop.gog.document@1` to layered v2 adapter |

For production DataDrop, the reference in-memory interpreter should be replaced by an adapter to the existing DuckDB compiler. Arrow tables or IPC streams should become the preferred interchange rather than serializing the complete JavaScript row set through NDJSON. DuckDB-Wasm already exposes Arrow-table and Arrow-stream ingestion, while Arrow provides a language-independent columnar representation intended for analytical interchange. citeturn993755search1turn993755search12

## Graph output

### Regression, confidence intervals, raw observations, and facets

[PNG preview](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/01-regression-facets.png) · [SVG](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/01-regression-facets.svg) · [Canvas version](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/01-regression-facets.canvas.html) · [Authoring IR](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/01-regression-facets.document.json) · [Scene IR](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/01-regression-facets.scene.json)

### Summary bars, dodge, and confidence intervals

[PNG preview](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/02-summary-errorbars.png) · [SVG](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/02-summary-errorbars.svg) · [Authoring IR](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/02-summary-errorbars.document.json)

### Faceted histogram

[PNG preview](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/03-histogram-facets.png) · [SVG](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/03-histogram-facets.svg) · [Authoring IR](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/03-histogram-facets.document.json)

### Boxplots and deterministic jitter

[PNG preview](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/04-boxplot-jitter.png) · [SVG](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/04-boxplot-jitter.svg) · [Authoring IR](sandbox:/mnt/data/datadrop-professional-plotting-suite/output/04-boxplot-jitter.document.json)

## Verification

The final package was built and executed successfully:

```text
11 tests passed
0 tests failed

01-regression-facets:   212 marks, 0 warnings
02-summary-errorbars:    16 marks, 0 warnings
03-histogram-facets:     51 marks, 0 warnings
04-boxplot-jitter:      173 marks, 0 warnings
```

The tests cover immutable builder behavior, serializable lambda-built expressions, stable field binding, compiler diagnostics, v1 document migration, facet-local statistics, stack bounds, regression intervals, scale behavior, accessible SVG/Canvas output, and plugin registration.

The implementation is standalone rather than applied directly to the upstream repository. Its analytical executor is deliberately dependency-free and in-memory; the report provides the concrete file-by-file migration path for connecting the logical plot and scene stages to DataDrop’s current DuckDB-Wasm runtime.

