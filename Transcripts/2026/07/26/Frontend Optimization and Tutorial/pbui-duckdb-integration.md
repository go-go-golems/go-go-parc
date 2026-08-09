# PBUI frontend query and graph integration

This package contains two drop-in TSX components:

- `pbui-gog-duckdb.tsx` — the workbench, product guide, and four live exercises.
- `pbui-landing-duckdb.tsx` — the product landing page, live hero, three guided exercises, and open brief.

Both components include the same browser query and plotting core so either file can run independently.

## 1. Install DuckDB-Wasm

```bash
npm install @duckdb/duckdb-wasm
```

No eager DuckDB import is added to the initial render path. The component dynamically imports the package when the first pipeline evaluation is requested.

## 2. Runtime behavior

Each visible pipeline is compiled to a sequence of SQL CTEs. The compiler currently covers:

- filter
- derive, including arithmetic and `log10`
- summarize with count, sum, mean, min, and max
- sort
- limit

The first frame still uses the small JavaScript evaluator. DuckDB-Wasm starts lazily in a Web Worker, registers the bundled datasets once, runs the equivalent SQL, and places normalized row objects in an LRU cache. A query-engine subscription causes the relevant views to redraw from the DuckDB result when it arrives. Subsequent equivalent pipeline states read synchronously from cache.

Transient step IDs are excluded from the semantic query key. Query failures, JavaScript fallback results, field summaries, and built plot geometry are also bounded by LRU caches.

## 3. Default development setup

With no extra configuration, the component uses DuckDB's jsDelivr bundle map and selects the compatible bundle at runtime. The remote worker is bootstrapped through a same-origin Blob worker.

This is convenient for a prototype. It requires network access on first load and a Content Security Policy that permits the CDN and Blob workers.

## 4. Recommended production setup for Vite

Self-host the WASM and worker assets through the application bundle. Define the bundle map before the component evaluates its first query:

```ts
import duckdbMvp from "@duckdb/duckdb-wasm/dist/duckdb-mvp.wasm?url";
import workerMvp from "@duckdb/duckdb-wasm/dist/duckdb-browser-mvp.worker.js?url";
import duckdbEh from "@duckdb/duckdb-wasm/dist/duckdb-eh.wasm?url";
import workerEh from "@duckdb/duckdb-wasm/dist/duckdb-browser-eh.worker.js?url";

(globalThis as any).__PBUI_DUCKDB_BUNDLES__ = {
  mvp: {
    mainModule: duckdbMvp,
    mainWorker: workerMvp,
  },
  eh: {
    mainModule: duckdbEh,
    mainWorker: workerEh,
  },
};
```

The supplied bundle map makes PBUI construct the selected worker directly. This removes the CDN dependency and avoids the Blob-worker requirement. The same override can point to manually hosted asset URLs in non-Vite builds.

## 5. Graph-building changes

The plot builder is now bounded by the available display resolution instead of emitting one SVG object for every row:

- Dense point layers use deterministic even sampling.
- Line and area series use Largest-Triangle-Three-Buckets-style decimation.
- The total line-series budget is divided across a bounded number of groups.
- Bar layers have a fixed per-panel mark budget.
- Numeric domains are computed in one pass without spreading large arrays.
- Categorical values and bar positions use maps and preserve pipeline order.
- Facets and nominal legends have explicit caps with a visible disclosure when values are omitted.
- Scales and ticks still use the full query result.
- Built geometry is cached by semantic query state, chart specification, dimensions, and query revision.

The result is substantially lower DOM/SVG pressure while preserving the full-result context needed for axes and domains.

## 6. Tutorial and landing-page structure

The revised landing page has one product story rather than a collection of disconnected lesson tracks:

1. A live hero demonstrates direct manipulation from a mark.
2. Three embedded exercises teach objects, question-to-chart analysis, and branching.
3. An open brief asks the user to filter, summarize, map, save, and expose tabular evidence.
4. A runtime section explains the worker, fallback, caches, and resolution-aware plotting.

Tutorial completion is derived from the resulting workbench state. A user can complete each objective manually or use a specific “show this move” control; the checker evaluates the same state either way.

## 7. Validation performed

The delivered files were checked with TypeScript's JSX transpiler and a Node-based core harness. The harness covers:

- JavaScript pipeline evaluation
- SQL CTE generation and string escaping
- aggregate and sort schema evolution
- semantic cache keys
- field-statistics caching
- categorical order after summarize and sort
- plot-geometry caching
- point, line, and bar budgets on synthetic inputs of up to 50,000 rows

The DuckDB package could not be installed in the execution container because the package fetch timed out, so browser worker startup was not executed here. The integration follows the official DuckDB-Wasm instantiation and JSON-ingestion APIs; run the component in the target bundler as the final environment check.
