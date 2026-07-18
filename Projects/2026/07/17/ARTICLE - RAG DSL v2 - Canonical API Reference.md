---
title: "RAG DSL v2: Canonical API Reference"
aliases:
  - RAG v2 API Reference
  - Canonical RAG Contract Reference
tags:
  - article
  - reference
  - rag
  - researchctl
  - api
  - contracts
status: active
type: article
created: 2026-07-17
repo: /home/manuel/workspaces/2026-07-13/rag-eval-ttc/rag-evaluation-system
source_tickets:
  - RESEARCHCTL-014
author: GPT-5.6 - sol
---

# RAG DSL v2: Canonical API Reference

This note is a compact reference for the active RAG v2 packages, contracts, commands, operator rules, policies, identities, and error namespaces. Historical RAG laboratory APIs are not supported.

## Package map

| Package | Public responsibility | Excluded responsibility |
| --- | --- | --- |
| `pkg/ragcontract` | DTOs, schema constants, strict codecs, manifests, traces, canonical digest | Goja, provider execution, filesystems, databases, researchctl |
| `pkg/ragcompiler` | Registry definitions, defaults, recipes, factors, graph validation, normalization, target compilation, semantic identities | Provider calls and lifecycle |
| `pkg/ragmodel` | Pure typed Go authoring model | I/O, credentials, indexes, workers |
| `pkg/gojamodules/rag` | `require("rag")` factories and immediate configurators | Retained callbacks and execution |
| `pkg/xgoja/providers/rag` | xgoja registration and declarations | Domain runtime |
| `pkg/ragoperators` | Native versioned operators, artifacts, manifests, provider interfaces | Run allocation and persistence |
| `pkg/ragengine` | Canonical graph execution and prepared static state | Product HTTP and research lifecycle |
| `pkg/researchctladapter` | RAG envelope resolution and generic laboratory submission | Generic laboratory persistence internals |
| `pkg/ragproduct` | Product load, bindings, prepared runtime, policies, qualification | Researchctl dependencies |

## Wire contracts

| Schema | Purpose |
| --- | --- |
| `rag-pipeline-ir/v2` | Normalized typed operator DAG. |
| `rag-product-plan/v2` | Online pipeline bindings, request/response, citations, limits, failure and trace policy. |
| `rag-study/v2` | Variants, factors, immutable inputs, dataset, measures, and replicates. |
| `rag-pipeline-execution/v2` | One expanded canonical study cell. |
| `rag-query-trace/v2` | Query/operator/channel/fusion/hydration/generation/evaluation evidence. |
| `rag-product-qualification/v1` | Exact product/model/prompt bindings and equivalent study. |
| `rag-preview-request/v1` | Pure one-query preview selection. |

Operator identities use a separate namespace:

```text
<namespace>.<operation>/<version>
```

## Strict decoding

```go
pipeline, err := ragcontract.DecodePipeline(reader)
product, err := ragcontract.DecodeProduct(reader)
study, err := ragcontract.DecodeStudy(reader)
execution, err := ragcontract.DecodeExecution(reader)
trace, err := ragcontract.DecodeTrace(reader)
```

Decoders reject:

- unknown fields;
- missing required values;
- invalid enum or bounds;
- malformed references;
- trailing JSON values.

Canonical helpers:

```go
raw, err := ragcontract.CanonicalJSON(value)
digest, err := ragcontract.Digest(value)
```

## Compiler APIs

```go
normalized, err := ragcompiler.Normalize(pipeline, registry)
compiledProduct, err := ragcompiler.CompileProduct(product, registry)
compiledStudy, cells, err := ragcompiler.CompileStudy(study, options)
productID, err := ragcompiler.ProductSemanticIdentity(product)
studyID, err := ragcompiler.StudySemanticIdentity(study)
```

Normalization performs recipe expansion, strict defaults, semantic validation, cycle detection, typed port resolution, semantic node ID generation, canonical topological ordering, and stable input/output sorting.

## Authoring APIs

Go entry points:

```go
pipeline := ragmodel.NewPipeline(name, configure)
query := ragmodel.NewQueryPlan(name, configure)
product := ragmodel.NewProduct(name, configure)
study := ragmodel.NewStudy(name, configure)

productPlan, err := ragmodel.CompileProduct(product, options)
studyPlan, cells, err := ragmodel.CompileStudy(study, options)
```

JavaScript entry point:

```javascript
const rag = require("rag");

const pipeline = rag.pipeline("name", p => {
  // Immediate typed configuration.
});

const product = rag.product("service", p => {
  // Compose pipeline and online policies.
});

module.exports = product.compileProduct(inputs);
```

No JavaScript function, Goja value, runtime object, provider callback, secret, file handle, or database handle is serialized into IR.

## Operator interface

```go
type Operator interface {
    Ref() ragcontract.OperatorRef
    Execute(
        context.Context,
        ragcontract.Node,
        map[string]any,
        *Environment,
    ) (map[string]any, error)
}
```

Compiler definitions and runtime registrations must have parity. Duplicate runtime registration fails.

### Required operator properties

- strict canonical config decoding;
- typed runtime values and dimension checks;
- deterministic ordering and ties;
- context cancellation;
- explicit unsupported/failure behavior;
- complete manifest parent lineage;
- canonical trace updates;
- measured usage and cost;
- secret-safe errors and artifacts;
- generated representation/source evidence separation.

## Engine APIs

```go
engine := ragengine.New(registry)

prepared, err := engine.Prepare(ctx, pipeline, corpus, options)
if err != nil {
    return err
}
defer prepared.Close()

options.Prepared = prepared
result, err := engine.Execute(
    ctx,
    execution,
    corpus,
    evaluationDataset,
    observationSink,
    options,
)
```

`Prepare` executes nodes that do not transitively depend on query input. `Prepared` supports concurrent query reads and idempotent close. The engine rejects non-canonical pipelines.

## Researchctl adapter

The adapter:

1. resolves RAG catalog references to immutable envelopes;
2. validates RAG manifests and lineage;
3. writes canonical `rag-pipeline-execution/v2` domain config;
4. maps RAG measures and factors to public generic lab records;
5. probes exact worker capability before allocation;
6. invokes researchctl's generic process runner;
7. reconstructs canonical RAG execution from generic specifications.

Generic identity shape:

```go
lab.ExecutionIdentity{
    SchemaVersion:       lab.ExecutionSpecSchemaVersion,
    IdentityScheme:      lab.ExecutionIdentityScheme,
    Domain:              "rag-pipeline/v2",
    DomainSchemaVersion: "rag-pipeline-execution/v2",
    Inputs:              inputs,
    DomainConfig:        canonicalExecution,
    RequestedMeasures:   measures,
    Factors:             canonicalFactors,
}
```

Researchctl stores `DomainConfig` opaquely.

## Worker capability

`cmd/rag-worker` advertises only:

| Field | Value |
| --- | --- |
| Protocol | `researchctl-runner-stdio/v1` |
| Runner | `rag-worker/v2` |
| Domain | `rag-pipeline/v2` |
| Trace | `rag-query-trace/v2` |

The NDJSON protocol is hello-first, bounded, cancellable, terminal-order checked, and completion is committed only after clean process exit.

## CLI commands

### Validate

```bash
rag-eval study validate STUDY.js \
  --inputs INPUTS.json \
  --ttc-database DATA.db \
  --output json
```

### Explain

```bash
rag-eval study explain STUDY.js \
  --inputs INPUTS.json \
  --ttc-database DATA.db \
  --output json
```

### Compile

```bash
rag-eval study compile STUDY.js \
  --inputs INPUTS.json \
  --ttc-database DATA.db \
  --output-dir DIR \
  --output json
```

### Preview

```bash
rag-eval preview STUDY.js \
  --inputs INPUTS.json \
  --ttc-database DATA.db \
  --query TEXT \
  --variant VARIANT \
  --researchctl-command researchctl \
  --worker-command rag-worker
```

### Run

```bash
rag-eval study run STUDY.js \
  --inputs INPUTS.json \
  --ttc-database DATA.db \
  --project PROJECT.yaml \
  --experiment-id EXPERIMENT_ID \
  --researchctl-command researchctl \
  --worker-command rag-worker \
  --spec-output-dir DIR \
  --output json
```

### Inspect and export

```bash
researchctl lab runs list --project PROJECT.yaml --output json
researchctl lab runs show RUN_ID --project PROJECT.yaml --output json
researchctl lab export RUN_ID --project PROJECT.yaml --output EXPORT.json
```

## Product API

```go
plan, err := ragproduct.Load(reader)
if err != nil {
    return err
}

runtime, err := ragproduct.New(ctx, plan, ragproduct.Bindings{
    Corpus:    corpusArtifact,
    Manifests: manifestResolver,
    Schemas:   schemaResolver,
    Generator: generator,
    Embedder:  embedder,
    Reranker:  reranker,
    Cache:     cache,
    Traces:    traceSink,
})
if err != nil {
    return err
}
defer runtime.Close()

response, err := runtime.Execute(ctx, ragproduct.Request{
    ID: "request-42",
    Values: map[string]any{
        "query": "What is reciprocal rank fusion?",
    },
})
```

Startup verifies the compiled product identity, corpus digest, exact model/prompt references, request/response contracts, and prepared static state.

### Failure policies

| Value | Result |
| --- | --- |
| `fail` | Return an explicit execution error. |
| `abstain` | Return an abstained response without answer, results, or citations. |
| `retrieval-only` | Return available retrieval evidence when generation cannot complete. |

### Trace policies

| Value | Result |
| --- | --- |
| `authoritative` | Include full canonical trace. |
| `metadata-only` | Include reduced trace metadata. |
| `artifact-backed` | Write trace through required sink and omit body trace. |
| `none` | Omit trace. |

### Citation policy

Generated representation text is never a citation. Required citation mode rejects non-abstained responses without hydrated source citations.

## Product HTTP host

`cmd/rag-product-server` is a reference `net/http` host with:

- bounded request bodies;
- server read/write/idle timeouts;
- health and query routes;
- graceful shutdown;
- product runtime concurrency/timeout policy;
- redacted errors.

It imports `pkg/ragproduct`, not researchctl or `pkg/researchctladapter`.

## Evidence semantics

| Concept | Definition |
| --- | --- |
| Representation | Retrieval text derived from a source chunk. |
| Matched representation | Exact representation returned by a retriever. |
| Collapse identity | Parent identity used to remove repeated votes in one channel. |
| Fused identity | Collapse key scored across channels. |
| Hydrated chunk | Exact source chunk recovered after ranking. |
| Citation | Source reference derived from hydrated evidence. |
| Evaluation target | Dataset-declared chunk or unit identity judged relevant. |

Required order:

```text
retrieve representations
  -> collapse independently per channel
  -> weighted fusion
  -> optional final collapse
  -> hydrate source chunks
  -> rerank/generate/evaluate
```

One collapse key contributes at most once per channel. Unit evaluation maps chunks through `ParentUnitID` and deduplicates unit identities.

## Identity domains

Keep these identities separate:

| Identity | Meaning |
| --- | --- |
| Operator reference | Immutable executable semantic version. |
| Semantic node ID | Hash of normalized operator, inputs, config, and semantic order. |
| Pipeline digest | Canonical normalized graph. |
| Product identity | Pipeline plus online bindings and policies. |
| Study identity | Variants, factors, bindings, dataset, measures, replicates. |
| Cell identity | One expanded study combination. |
| Generic specification ID | Opaque domain work plus generic immutable inputs/measures/factors. |
| Run ID | One execution allocation. |
| Attempt ID | One process attempt within a run. |
| Generic artifact digest | Exact file bytes under researchctl custody. |
| RAG manifest digest | Canonical domain content and lineage. |
| Export digest | Exact exported bytes. |

## Error namespaces

| Prefix | Boundary |
| --- | --- |
| `RAG_V2_*` | Authoring, contract, compiler, graph, and config. |
| `RAG_INPUT_*` | Envelope, manifest, binding, and lineage. |
| `RAG_ENGINE_*` | Canonical graph preparation/execution. |
| `RAG_RUNTIME_*` | Operator runtime values and ports. |
| `RAG_PRODUCT_*` | Product loading, bindings, request, policy, execution, trace host. |
| `RAG_WORKER_*` | Worker protocol negotiation and execution. |

Errors do not trigger silent algorithm downgrade. Product-facing provider details are redacted.

## Active evidence and measurements

| Evidence | Location |
| --- | --- |
| Ten-cell candidate matrix | `experiments/rag-sol2/candidate-result.json` |
| Frozen parity contract | `pkg/ragoperators/testdata/rag-sol2-parity-v1.json` |
| Final acceptance measurements | `experiments/final-measurements-v1.json` |
| Phase 8 acceptance | RESEARCHCTL-014 `scripts/09-phase8-acceptance.sh` |

The matrix is labeled `status: candidate`, `benchmarkClaim: false`, and `fixtureProviders: true`.

## Removed interfaces

Do not use or restore:

- `pkg/raglab`;
- `cmd/rag-lab-worker`;
- `internal/services/immutableretrieval`;
- `rag-sol2` playground runtime;
- researchctl RAG schemas, commands, providers, or dependencies;
- retired RAG lifecycle tables;
- `/api/v1/lab/catalog`;
- JavaScript execution/lifecycle methods.

The active artifact catalog route is:

```http
GET /api/v1/artifacts/rag/catalog
```

## See also

- [[ARTICLE - RAG DSL v2 and Researchctl Laboratory - Architecture Implementation and Evidence]]
- [[ARTICLE - RAG DSL v2 - Getting Started Guide]]
- [[ARTICLE - RAG DSL v2 - Developer Guide]]
