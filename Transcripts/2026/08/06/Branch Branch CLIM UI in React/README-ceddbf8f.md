# P06 — Typed Ports and the Binding Quotient Compiler

A self-contained PBUI research artifact for compiling typed identity-link declarations into binding classes and projecting those classes to shared widget resources.

## What it demonstrates

```text
local typed port --q--> persistent binding --v--> shared resource --> widget
```

- Identity-link compatibility is based on semantic contracts, not raw payload shape.
- The reference semantics is finite equivalence closure by graph traversal.
- The optimized implementation uses union-find but never exposes its roots as persistent identities.
- One process-local `SharedCell` is allocated per binding class.
- Chart, pipeline, and table widgets read and write through generated projections.
- Merge and unlink value policies are explicit because quotienting does not choose them.
- Link declarations and provenance are retained, so unlinking means remove a declaration and recompile.
- A JSONL adapter exposes the subsystem for later composition experiments.

The visual workbench adapts the compact tiled, typed-presentation grammar of the supplied PBUI productivity-suite JSX. The original foundation treats screen objects as typed live presentations and supports cross-tile accept mode; this artifact preserves that exploratory workbench character while replacing the central semantic problem with typed port wiring and quotient compilation.

## Run

The compiled JavaScript is included. No install step is required for verification.

```bash
./scripts/reproduce --verify
```

Expected final line:

```text
P06 verification complete.
```

Start the dependency-free browser laboratory:

```bash
./scripts/reproduce --demo
```

Open the local URL printed by the server.

Run the common JSONL adapter:

```bash
./scripts/reproduce --adapter
```

Replay the identity-link trace:

```bash
node scripts/replay.mjs fixtures/trace-identity-link.jsonl
```

Rerun the benchmark:

```bash
./scripts/reproduce --benchmark
```

## Quick API

```ts
import {
  PortBindingResolverRegistry,
  component,
  portContract,
} from "./dist/index.js";

const document = portContract({
  semanticTag: "primary-document",
  payloadSort: "document",
  mode: "read-write",
  authorityDomain: "workspace-1",
  multiplicity: "one",
  updateAlgebra: "replace",
  lifetime: "workspace",
});

const chartDocument = component("chart-1").port("document", document);
const pipelineDocument = component("pipeline-1").port("document", document);

const registry = new PortBindingResolverRegistry();
registry
  .declare(chartDocument, { sort: "document", key: "doc-a" })
  .declare(pipelineDocument, { sort: "document", key: "doc-b" })
  .compile();

registry.identify(chartDocument, pipelineDocument, {
  linkId: "chart-pipeline-document",
  mergePolicy: { kind: "prefer-left", left: chartDocument },
});

const chart = registry.projection(chartDocument);
const pipeline = registry.projection(pipelineDocument);

console.assert(chart.bindingId === pipeline.bindingId);
console.assert(chart.resourceId === pipeline.resourceId);

pipeline.set({ sort: "document", key: "doc-z" });
console.assert(chart.get().key === "doc-z");
```

## Artifact map

- `src/` — canonical TypeScript semantic implementation
- `dist/` — checked-in compiled ESM and declarations
- `web/` — dependency-free interactive laboratory
- `react/` — optional React JSX host adapter
- `test/` — 20 executable tests, including 2,000 generated graphs
- `scripts/` — verification, adapter, replay, benchmark, and static server
- `proofs/` — Lean quotient and widget-factorization proof source
- `counterexamples/` — minimized failed design assumptions
- `capsule/` — composition manifest, schemas, exports, and reliance statement
- `docs/REPORT.md` — full framing and results report
- `docs/REPORT.pdf` — typeset report
- `docs/API.md` — API details
- `docs/DEMO-SCRIPT.md` — 10–15 minute demonstration
- `docs/HANDOFF.md` — solid, provisional, and non-composable results
- `docs/EVIDENCE.md` — evidence ledger
- `benchmarks/results.json` — raw performance data

## Evidence status

The delivered TypeScript build, Node test suite, JSONL trace parsing, manifest schemas, and browser interaction smoke passed during assembly. The included Lean source was not executed because the assembly environment had no Lean executable. It must be checked independently before being cited as verified proof evidence.

## Scope boundary

This artifact implements **identity links only**. A transformed selection-to-filter relationship is not an identity equation and returns `unsupported` through the research adapter. Replicated topology, lens laws, scheduling, authority issuance, and whole-component composition belong to separate research projects.

## Tooling

- Runtime: Node 20 or later
- Build source: TypeScript 5-compatible compiler when rebuilding `dist/`
- Browser demo: standard browser with ES modules
- Proof source: Lean 4 toolchain declared in `proofs/lean-toolchain`

## License

MIT. See `LICENSE`.
