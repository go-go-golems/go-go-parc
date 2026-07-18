---
title: "RAG DSL v2: Getting Started Guide"
aliases:
  - RAG v2 Quickstart
  - RAG Study Getting Started
tags:
  - article
  - guide
  - rag
  - javascript
  - researchctl
  - getting-started
status: active
type: article
created: 2026-07-17
repo: /home/manuel/workspaces/2026-07-13/rag-eval-ttc/rag-evaluation-system
source_tickets:
  - RESEARCHCTL-014
author: GPT-5.6 - sol
---

# RAG DSL v2: Getting Started Guide

This guide takes a developer from the checked-out repository to a validated RAG v2 study, a one-query preview, a researchctl-backed run, and an inspected export. It uses the active v2 commands and contracts. It does not use the removed `raglab` package, `rag-lab-worker`, `/api/v1/lab/catalog`, or JavaScript lifecycle APIs.

> [!info]
> **Audience:** developers running or modifying RAG studies.
>
> **Outcome:** a canonical study is compiled from pure JavaScript, bound to immutable inputs, executed by `rag-worker` through researchctl, and inspected as generic run evidence.

## Synopsis

```bash
cd /home/manuel/workspaces/2026-07-13/rag-eval-ttc/rag-evaluation-system

go test ./pkg/ragcontract ./pkg/ragcompiler ./pkg/ragmodel \
  ./pkg/ragoperators ./pkg/ragengine ./pkg/researchctladapter -count=1

go run ./cmd/rag-eval study validate examples/rag-v2/06-raw-study.js \
  --inputs examples/rag-v2/inputs-ttc-catalog.json \
  --ttc-database data/rag-eval.db --output json
```

Use installed `rag-eval`, `rag-worker`, and `researchctl` binaries in normal operation. `go run` is convenient during development.

## Prerequisites

You need:

- Go at the version declared by the repository;
- the RAG repository checkout;
- a researchctl binary containing the public generic laboratory SDK and process runner;
- a `rag-worker` built from the same RAG semantic revision as the CLI;
- immutable corpus and evaluation envelopes, or a read-only TTC catalog that resolves aliases to them;
- provider bindings only when the selected operators require non-fixture providers.

Check the repository and binaries:

```bash
git status --short
go version
go test ./pkg/ragcontract ./pkg/ragcompiler -count=1
go run ./cmd/rag-eval --help
go run ./cmd/rag-worker --help
researchctl --help
```

If module resolution fails because the researchctl laboratory SDK has not yet been published, inspect `go.mod`. The current sibling-checkout `replace` is temporary and assumes the documented workspace layout.

## Step 1: read the active examples

Start with:

```text
examples/rag-v2/01-product.js
examples/rag-v2/06-raw-study.js
examples/rag-v2/inputs.json
examples/rag-v2/inputs-ttc-catalog.json
```

The JavaScript file declares typed intent. The inputs file supplies explicit bindings. Keep these roles separate. A study source must not open the TTC database, resolve a model endpoint, read credentials, allocate a run, or write artifacts.

A study has this conceptual structure:

```javascript
const rag = require("rag");

const pipeline = rag.pipeline("raw", p => {
  // Add typed, registered operator descriptors.
  // Bind graph outputs explicitly.
});

module.exports = rag.study("raw-study", s => {
  s.variant("raw", pipeline);
  // Declare factors, dataset, measures, and replicate policy.
});
```

Configurator functions execute immediately. `module.exports` is a Go-owned study value, not a callback that the worker will execute.

## Step 2: bind immutable inputs

An input file maps semantic roles to exact envelopes or RAG-owned catalog references. Common roles include:

- corpus;
- evaluation dataset;
- model manifest;
- prompt manifest;
- schema manifest;
- precomputed representation, embedding, or index artifacts where the pipeline expects them.

When using the TTC catalog, pass its database explicitly:

```bash
--inputs examples/rag-v2/inputs-ttc-catalog.json \
--ttc-database data/rag-eval.db
```

Catalog names are authoring conveniences. Before researchctl submission, `pkg/researchctladapter` resolves each name to verified immutable bytes and a RAG manifest. Researchctl then verifies the staged file digest without decoding the domain content. The worker validates the RAG manifest and lineage again.

> [!warning]
> A generic file digest and a RAG manifest digest identify different values. Preserve both. Do not copy one into the other field.

## Step 3: validate

Run structural and semantic validation before compiling or allocating a run:

```bash
rag-eval study validate examples/rag-v2/06-raw-study.js \
  --inputs examples/rag-v2/inputs-ttc-catalog.json \
  --ttc-database data/rag-eval.db \
  --output json
```

Validation checks:

- typed graph structure and acyclicity;
- registered operator identities;
- input/output port kinds;
- strict config fields and defaults;
- factor references and values;
- variant bindings;
- dataset policy and relevance target;
- requested measures;
- immutable input roles and lineage policy;
- stable cell expansion.

Errors use stable boundary prefixes. `RAG_V2_*` indicates authoring, contract, compiler, graph, or config failure. Fix the source or binding; do not add a permissive decoder or fallback.

## Step 4: explain the expanded study

```bash
rag-eval study explain examples/rag-v2/06-raw-study.js \
  --inputs examples/rag-v2/inputs-ttc-catalog.json \
  --ttc-database data/rag-eval.db \
  --output json
```

Review the output rather than treating successful validation as sufficient. Confirm:

1. the expected variant names;
2. the expected Cartesian factor count;
3. the exact representation channels;
4. collapse scope in every channel;
5. fusion weights and rank constant;
6. provider and model requirements;
7. evaluation target and measures;
8. candidate/frozen status and split;
9. artifacts consumed by each variant.

A variant's cell identity should include only artifacts that variant actually consumes.

## Step 5: compile without execution

```bash
rm -rf /tmp/rag-v2-compiled
rag-eval study compile examples/rag-v2/06-raw-study.js \
  --inputs examples/rag-v2/inputs-ttc-catalog.json \
  --ttc-database data/rag-eval.db \
  --output-dir /tmp/rag-v2-compiled \
  --output json
```

Compilation applies defaults, substitutes factors, expands recipes, validates typed edges, computes semantic node IDs, topologically orders nodes, and writes canonical `rag-pipeline-execution/v2` values.

Inspect the generated files:

```bash
find /tmp/rag-v2-compiled -type f -maxdepth 2 -print
jq . /tmp/rag-v2-compiled/*.json | less
```

Recompiling the same authoring value against the same immutable bindings must reproduce canonical execution bytes and identity. Display labels can remain outside semantic identity where the contract documents that exclusion.

## Step 6: run a preview

Preview is the fastest end-to-end diagnostic:

```bash
rag-eval preview examples/rag-v2/06-raw-study.js \
  --inputs examples/rag-v2/inputs-ttc-catalog.json \
  --ttc-database data/rag-eval.db \
  --query 'What is reciprocal rank fusion?' \
  --variant raw \
  --researchctl-command researchctl \
  --worker-command rag-worker
```

Preview still performs normal compilation, input resolution, worker capability probing, researchctl allocation, process execution, artifact custody, and trace persistence. Its dataset contains one candidate query. The result is diagnostic evidence and must not be reported as a benchmark.

Inspect these trace sections first:

- channel rankings;
- per-channel collapse;
- weighted RRF contributions;
- hydration selection;
- exact source citation;
- failures and partial evidence;
- usage and cost.

If generated summaries or questions appear as citations, stop. Only hydrated source chunks are valid citation evidence.

## Step 7: execute a study

```bash
rag-eval study run examples/rag-v2/06-raw-study.js \
  --inputs examples/rag-v2/inputs-ttc-catalog.json \
  --ttc-database data/rag-eval.db \
  --project project.yaml \
  --experiment-id EXP-RAG \
  --researchctl-command researchctl \
  --worker-command rag-worker \
  --spec-output-dir /tmp/rag-v2-compiled \
  --output json
```

The adapter first probes the worker for exact protocol, runner, domain, and trace capabilities. This happens before run allocation so an incompatible worker does not create a run. The worker still performs canonical config and lineage validation after allocation; preflight is not a trust shortcut.

During execution, researchctl owns:

- specification and run IDs;
- attempt allocation and retries;
- process cancellation and terminal state;
- staged input custody;
- generic metric, trace, and artifact observations;
- persistence and export.

The RAG worker owns:

- strict `rag-pipeline-execution/v2` decoding;
- RAG envelope and lineage validation;
- operator execution;
- `rag-query-trace/v2` content;
- RAG metrics and output artifacts.

## Step 8: inspect and export

Use researchctl's generic commands:

```bash
researchctl lab runs list --project project.yaml --output json
researchctl lab runs show RUN_ID --project project.yaml --output json
researchctl lab export RUN_ID --project project.yaml --output run-export.json
```

Check:

- terminal status and attempt count;
- requested versus observed measures;
- failed and abstained query counts;
- trace kind and schema version;
- artifact file digests and sizes;
- RAG manifest identities inside domain artifacts;
- dataset status and split labels;
- storage, provider usage, and cost.

A successful terminal state proves process completion, not scientific validity. Review metric definitions, relevance targets, traces, and failures before comparing runs.

## Step 9: reconstruct canonical intent

The adapter supports canonical specification reconstruction from the generic researchctl record. Acceptance tests require the reconstructed RAG execution to match the original canonical value and require staged corpus/evaluation bytes to remain unchanged.

Use reconstruction when reviewing an export or investigating a run. It answers “what exact domain work was requested?” independently of worker output.

## Common failures

### `RAG_V2_OPERATOR_UNKNOWN`

The graph names an operator absent from the compiler registry. Use an active immutable operator ID or implement a new operator version in both compiler and runtime registries.

### `RAG_V2_PORT_MISMATCH`

An edge connects incompatible port kinds. Inspect the upstream output and downstream input definitions. Do not coerce values dynamically.

### `RAG_ENGINE_PIPELINE_NONCANONICAL`

A caller supplied a pipeline that had not passed through canonical normalization. Compile the authoring value and execute the compiler output.

### Worker capability failure

Confirm that `rag-worker` advertises:

```text
researchctl-runner-stdio/v1
rag-worker/v2
rag-pipeline/v2
rag-query-trace/v2
```

Do not allocate with a worker from the removed prototype runtime.

### Manifest or lineage failure

Verify envelope bytes, manifest digest, parent roles, model dimensions, evaluation target, and exact bound artifact. Do not bypass worker-side validation.

### Product citation failure

A product plan with required citations produced no hydrated source citation. Inspect hydration and generation citation IDs. Do not cite generated representation text.

## Validation checklist

- [ ] JavaScript performs only typed composition.
- [ ] Inputs resolve to immutable envelopes and exact manifests.
- [ ] `study validate` succeeds with strict decoding.
- [ ] `study explain` shows the expected cells and bindings.
- [ ] Repeated compilation reproduces identity.
- [ ] Preview uses researchctl and `rag-worker`.
- [ ] Collapse occurs per channel before fusion.
- [ ] Citations refer to hydrated source chunks.
- [ ] Run failures, latency, storage, usage, and cost are inspected.
- [ ] Candidate or fixture evidence is not called a benchmark.

## See also

- [[ARTICLE - RAG DSL v2 and Researchctl Laboratory - Architecture Implementation and Evidence]]
- [[ARTICLE - RAG DSL v2 - Developer Guide]]
- [[ARTICLE - RAG DSL v2 - Canonical API Reference]]
