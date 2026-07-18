---
title: "RAG DSL v2: Developer Guide"
aliases:
  - RAG v2 Extension Guide
  - RAG Operator Developer Guide
tags:
  - article
  - guide
  - rag
  - go
  - javascript
  - compiler
  - operator-authoring
status: active
type: article
created: 2026-07-17
repo: /home/manuel/workspaces/2026-07-13/rag-eval-ttc/rag-evaluation-system
source_tickets:
  - RESEARCHCTL-014
author: GPT-5.6 - sol
---

# RAG DSL v2: Developer Guide

This guide explains how to modify RAG DSL v2 without weakening its semantic, evidence, or lifecycle boundaries. It covers package selection, operator authoring, compiler/runtime parity, typed JavaScript exposure, manifests, prepared state, traces, product/study equivalence, and required tests.

> [!info]
> **Audience:** maintainers adding operators, contracts, authoring descriptors, providers, study behavior, or product behavior.
>
> **Primary rule:** observable retrieval behavior belongs to a versioned Go operator or versioned RAG contract. It does not belong in an arbitrary JavaScript callback or a researchctl domain case.

## Package selection

Choose the package by responsibility:

| Change | Package |
| --- | --- |
| Wire DTO, schema, manifest, trace record, strict codec | `pkg/ragcontract` |
| Operator definition, config defaults, graph validation, identity | `pkg/ragcompiler` |
| Pure typed authoring value or descriptor | `pkg/ragmodel` |
| `require("rag")` factory and TypeScript declaration | `pkg/gojamodules/rag`, `pkg/xgoja/providers/rag` |
| Native operator and domain artifact materialization | `pkg/ragoperators` |
| Graph scheduling or query/static execution | `pkg/ragengine` |
| Immutable RAG input resolution and researchctl wrapping | `pkg/researchctladapter` |
| Product request/policy/runtime/qualification | `pkg/ragproduct` |
| Generic runs, attempts, retries, custody, import/export | researchctl `pkg/lab` |

Do not add RAG types to researchctl. Do not import researchctl in `pkg/ragproduct`, `pkg/ragengine`, `pkg/ragoperators`, or the product server.

## Adding a native operator

### 1. define observable semantics

Write down:

- exact input and output port kinds;
- deterministic ordering and tie-breaking;
- strict configuration fields and defaults;
- cancellation points;
- resource ownership;
- manifest parents and production metadata;
- trace records and usage/cost updates;
- failure behavior;
- whether the node is query-dependent;
- whether product and study targets can use it.

Choose an immutable reference:

```text
<namespace>.<operation>/<version>
```

Examples include `retrieve.vector/v1` and `fusion.weighted-rrf/v1`. Increment the version if defaults, scores, ordering, truncation, lineage, trace shape, or failure behavior changes.

### 2. add the compiler definition

Register the definition in `pkg/ragcompiler/registry.go`. A definition declares the operator reference, execution phase, typed ports, configuration schema/defaults, capabilities, resources, and expected observations.

Conceptually:

```go
registry.Register(ragcompiler.OperatorDefinition{
    Ref: ragcontract.OperatorRef{
        Kind: "retrieve.example",
        Version: "v1",
    },
    Inputs: []ragcompiler.PortDefinition{
        {Name: "query", Kind: ragcontract.PortQuery},
        {Name: "index", Kind: ragcontract.PortIndex},
    },
    Outputs: []ragcompiler.PortDefinition{
        {Name: "ranked", Kind: ragcontract.PortRankedRepresentations},
    },
    Config: /* strict fields and defaults */,
})
```

Use the actual repository types and helpers; the sketch shows the required information. Normalized config must be canonical JSON. Unknown fields must fail. Unsafe combinations must fail before runtime.

If an input family is dynamic, such as `channel.<name>` for weighted RRF, define a constrained dynamic-port rule in the compiler rather than accepting arbitrary names globally.

### 3. implement `ragoperators.Operator`

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

The implementation must:

1. decode canonical config strictly;
2. validate input runtime types and dimensions;
3. check `ctx.Err()` before and after expensive or provider operations;
4. produce deterministic ordering for equal scores and unordered collections;
5. return explicit errors rather than changing algorithms;
6. create complete manifest lineage for materialized values;
7. update canonical trace sections;
8. report measured usage and cost;
9. keep generated text separate from source evidence;
10. omit credentials and endpoint secrets from errors, traces, and artifacts.

Register the runtime implementation once in `pkg/ragoperators/registry.go`. Duplicate registration is an error. The compiler/runtime parity test must pass.

### 4. preserve identity and lineage

Materialization operators generally follow this sequence:

```text
validate inputs and canonical config
  -> produce deterministic records
  -> canonicalize and digest records
  -> create manifest with ordered parent roles
  -> emit semantic value plus manifest/artifact observation
```

Do not include a manifest's own digest in the value from which that digest is computed. Parent role ordering must be canonical. Record the exact model/prompt/config identity used for generated representations or embeddings.

For source-derived values, retain all identities needed to recover evidence:

```text
representation ID
parent chunk ID
parent unit ID
source record/revision identity
exact source range
production manifest identity
```

### 5. expose a typed authoring descriptor

Add a factory in `pkg/ragmodel`. The descriptor should contain typed intent, not an executor. If JavaScript authors need it, expose the same factory through `pkg/gojamodules/rag` and regenerate precise TypeScript declarations.

Configurator functions must run immediately. Store Go-owned data behind private symbols. Reject fabricated wrappers. Do not expose:

- raw node constructors;
- provider callbacks;
- `goja.Value` in contract types;
- database or index handles;
- worker or run lifecycle methods;
- credentials or mutable endpoint state.

### 6. decide static versus query-dependent behavior

`ragengine.Prepare` computes static node IDs by query dependency. A node is eligible for prepared state only when it does not transitively depend on the query input.

Prepared values must be:

- immutable for the duration of the runtime;
- safe for concurrent reads;
- deterministically closeable if they own resources;
- valid under exact pipeline and artifact digests.

If an operator mutates retained state per query, it is not safe for `Prepared`. Redesign it with query-local values or explicit synchronization and test under `go test -race`.

## Retrieval-specific rules

### Representations

A representation is retrieval material derived from a source chunk. Generated summaries and questions can match queries, but their text cannot be returned as source citation evidence.

### Collapse

Collapse repeated parent identities independently within each retrieval channel before fusion. One collapse key contributes at most once per channel. Preserve the winning representation and removed candidates in trace data where defined.

### Fusion

Weighted RRF must record every contribution. Stable tie-breaking is part of the operator version. Final collapse is a separate post-fusion policy.

### Hydration

Hydration resolves fused identities to exact source chunks and source ranges. Only hydrated chunks can become citations. Missing lineage is a failure, not a reason to return representation text.

### Reranking

A reranker preserves first-stage identity and scores in the trace. Resolve exact reranker model manifests and validate result cardinality and IDs.

### Evaluation

Evaluation obeys the dataset's explicit target. Unit-target evaluation maps chunks through `ParentUnitID` and deduplicates units. Metric names, versions, cutoffs, relevance thresholds, and failed-query policy are part of scientific interpretation.

## Adding or changing a provider adapter

Providers belong behind host-supplied interfaces in `ragoperators.Environment`. Operators do not read environment variables or credentials directly.

A production provider integration must freeze:

- provider and server implementation/version;
- endpoint policy without embedding secret URLs in traces;
- model digest and dimensions;
- prompt/template digest;
- tokenizer and truncation behavior;
- request parameters;
- output schema and cardinality;
- timeout and retry behavior;
- token accounting and pricing revision.

Credential references are opaque. Resolve them in host code. Errors returned to product callers must be redacted. Research artifacts may retain stable failure codes and safe diagnostic fields, never the credential or endpoint secret.

Cache keys include semantic input, operator/config identity, and exact model/prompt manifest identities. A cache hit must produce trace and usage semantics defined by the operator version.

## Extending contracts

Change `pkg/ragcontract` when the wire representation itself needs a new field or invariant. Determine whether the change is compatible with the current schema's documented semantics. If it changes interpretation or required behavior, add a new schema version rather than making old bytes ambiguous.

For every contract:

- add or update JSON Schema;
- retain strict unknown-field rejection;
- validate nested enums, references, and bounds;
- define canonical JSON and semantic identity impact;
- add valid and malformed golden cases;
- add fuzz/property tests where parsing or normalization is complex;
- document display-only fields excluded from identity.

Do not add a decoder dispatch table for deleted prototype schemas unless a separate migration specification explicitly requires it.

## Study integration

Study changes pass through `pkg/ragcompiler` and `pkg/researchctladapter`.

A new factor or measure must have canonical value semantics. Expanded cells must include only consumed input bindings. The adapter converts each cell to a generic `lab.ExecutionIdentity` with opaque canonical `DomainConfig`. Researchctl must not interpret the factor's RAG meaning.

Worker capability preflight occurs before run allocation. Worker-side strict decoding, canonical equality, manifest validation, and lineage checks still occur after process startup.

Preview must use the same compiler, adapter, process worker, and researchctl lifecycle as a normal one-query candidate study. Do not add an in-process preview executor.

## Product integration

A product-capable operator must work through the normalized pipeline and prepared engine. Product-specific behavior belongs in the plan or `pkg/ragproduct`, not in a separate copy of retrieval semantics.

Test:

- exact corpus and model binding failures at startup;
- request field types and rune-length limits;
- maximum concurrency and cancellation;
- timeout behavior;
- `fail`, `abstain`, and `retrieval-only` policies;
- `authoritative`, `metadata-only`, `artifact-backed`, and `none` traces;
- required citations;
- redacted provider failures;
- close/drain behavior;
- product/study `ResultTrace` equivalence;
- absence of researchctl imports.

## Test matrix

Minimum commands for an operator/compiler change:

```bash
go test ./pkg/ragcontract ./pkg/ragcompiler ./pkg/ragmodel \
  ./pkg/gojamodules/rag ./pkg/ragoperators ./pkg/ragengine -count=1

go test -race ./pkg/ragoperators ./pkg/ragengine -count=1
go vet ./...
GOWORK=off go test ./... -count=1
GOWORK=off go run github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.12.2 run ./...
xgoja doctor -f examples/xgoja/rag-v2/xgoja.yaml
```

Add targeted tests for:

- normalized defaults and semantic node identity;
- malformed/unknown config;
- missing, unknown, and wrong-kind ports;
- deterministic sorting and tie-breaking;
- compiler/runtime registry parity;
- manifest digest and parent lineage;
- context cancellation and provider failure;
- partial evidence and stable error code;
- trace completeness and secret canaries;
- Unicode ranges, cardinality, graph, or parser fuzzing;
- race behavior for retained state;
- algorithmic/storage benchmarks where material;
- product/study equivalence where applicable.

Run the phase acceptance script relevant to the touched boundary. The final cross-cutting suite is in the closed RESEARCHCTL-014 ticket's `scripts/09-phase8-acceptance.sh`.

## Review checklist

### Semantic review

- [ ] The operator has a new immutable version if behavior changed.
- [ ] Config defaults and ordering are canonical.
- [ ] Compiler and runtime port definitions agree.
- [ ] Unsupported behavior fails explicitly.
- [ ] Generated representations remain separate from evidence.
- [ ] Collapse and fusion contribution limits remain correct.
- [ ] Evaluation maps to the declared target.

### Resource and security review

- [ ] Expensive operations honor cancellation.
- [ ] Prepared values are immutable and concurrently safe.
- [ ] Owned resources close once after active use.
- [ ] Artifact paths cannot escape custody roots.
- [ ] No secret appears in error, trace, frame, or artifact.
- [ ] Usage and cost are explicit.

### Boundary review

- [ ] JavaScript contains no executor or retained callback.
- [ ] Researchctl contains no RAG schema or import.
- [ ] Product code contains no researchctl dependency.
- [ ] Preview uses the normal worker lifecycle.
- [ ] No retired alias, route, table, command, or package was restored.

## See also

- [[ARTICLE - RAG DSL v2 and Researchctl Laboratory - Architecture Implementation and Evidence]]
- [[ARTICLE - RAG DSL v2 - Getting Started Guide]]
- [[ARTICLE - RAG DSL v2 - Canonical API Reference]]
