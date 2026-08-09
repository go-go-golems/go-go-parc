# Researchctl 2
## A clean architecture for reproducible, staged RAG experiment programs

**Status:** Greenfield design guide  
**Audience:** ML scientists, research engineers, platform engineers, and implementers  
**Design stance:** The current implementation is treated as a valuable prototype and source of tested components, not as an API or data-model compatibility constraint.

---

## 1. Executive decision

The clean version of `researchctl` should be a **scientific control plane and provenance ledger**. It should not also try to be a workflow language, statistical programming environment, notebook runtime, generic project-management graph, and plugin application platform.

Its job is to answer, rigorously and conveniently:

1. What question was being investigated?
2. What protocol revision and experimental design were frozen before execution?
3. Which treatment combinations, blocks, randomization assignments, and replicate slots were planned?
4. What code, inputs, software environment, hardware, provider configuration, and random seeds actually executed?
5. Which artifacts and observations were produced by each step?
6. Which computations were reused from cache, and why were they considered compatible?
7. Which runs succeeded, failed, were excluded, or were replaced?
8. Which analysis consumed which exact run set?
9. Which reviewed evidence and decisions were derived from that analysis?
10. Can the entire research object be exported in an interoperable form?

The architectural thesis is:

```text
canonical protocol data
        |
        v
frozen study assignments
        |
        v
domain compiler -> generic execution DAG -> executor adapter
        |                         |
        |                         v
        |                 ordinary Python/R/shell/tools
        v
append-only provenance ledger <-> content-addressed artifact store
        |
        v
recorded analysis activities -> reviewed evidence -> decisions/reports
```

The system has four hard boundaries:

- **Protocol:** prospective scientific intent.
- **Study:** frozen assignments and design decisions.
- **Execution:** retrospective computational facts.
- **Interpretation:** reviewed analysis, evidence, and decisions.

Those boundaries must remain distinct in the data model, identity model, CLI, and user interface.

---

## 2. Concrete scenario: a full RAG research program

Assume a machine learning scientist is developing a retrieval-augmented question-answering system over a hypothetical corpus of 250,000 technical documents. The corpus contains manuals, support incidents, design documents, and policy material. The scientist has a curated evaluation set with:

- question IDs;
- answerability labels;
- reference answers where available;
- relevant document and passage judgments;
- question categories and difficulty strata;
- a development split and an untouched confirmatory holdout split.

The team is not merely tuning `top_k`. It is investigating a chain of interacting design choices.

### 2.1 Scientific questions

The program contains several linked questions:

1. **Chunking:** Do structural or semantic chunks outperform fixed token windows? What chunk size and overlap produce the best retrieval coverage without overwhelming the generator?
2. **Pre-index enrichment:** Does adding a short chunk summary improve dense retrieval? Do synthetic questions improve lexical or hybrid retrieval? Should original text, summaries, and synthetic questions be indexed in separate fields?
3. **Representation:** Which embedding model, vector normalization, and dimensionality are effective for this corpus?
4. **Indexing:** How sensitive are results to ANN parameters, lexical analyzer settings, index sharding, and index build concurrency?
5. **Retrieval:** How do BM25, vector, and hybrid retrieval compare? Which fusion strategy and weights work best? How many candidates should enter reranking?
6. **Reranking:** Does a cross-encoder or LLM reranker improve answer quality enough to justify latency and cost?
7. **Context construction:** How should retrieved chunks be deduplicated, diversified, parent-expanded, ordered, and packed into the context window?
8. **Answering:** Which model and prompt produce the best correctness, faithfulness, citation quality, and abstention behavior?
9. **Systems behavior:** How do batching, internal parallelism, query concurrency, provider rate limits, and hardware affect latency, cost, failures, and possibly output quality?
10. **Interactions:** Does the best retriever depend on the chunking strategy? Does enrichment help vector retrieval but harm lexical precision? Does a stronger generator compensate for weaker retrieval, or merely hide failures?

The primary decision might be:

> Select a RAG configuration that maximizes held-out answer correctness, subject to minimum retrieval coverage, p95 latency below 2.5 seconds, cost below $0.02 per answered query, and an explicit abstention target for unanswerable questions.

The system must preserve that multi-objective statement. It must not collapse the study into one scalar metric too early.

### 2.2 Candidate factors

| Phase | Candidate factors | Scientific or operational? | Natural scope |
|---|---|---:|---|
| Parse | parser version, OCR mode, table extraction | scientific when compared | document set |
| Normalize | deduplication policy, boilerplate removal | scientific | document set |
| Chunk | method, target tokens, overlap, boundary policy | scientific | chunk set |
| Enrich | summary model/prompt/length, synthetic-question count | scientific | chunk set |
| Embed | model, dimensions, normalization | scientific | embedding set |
| Embed execution | batch size, API concurrency, accelerator | either; must be declared | build activity |
| Lexical index | analyzer, stemming, BM25 parameters | scientific | lexical index |
| Vector index | engine, distance, HNSW build/search parameters | scientific | vector index |
| Retrieval | lexical/vector/hybrid, top-k, fusion algorithm/weight | scientific | query |
| Rerank | method, candidate count, model | scientific | query |
| Context | token budget, diversity, parent expansion, ordering | scientific | query |
| Answer | model, prompt, temperature, citation/abstention policy | scientific | answer sample |
| Serving | max in-flight studies | operational | scheduler |
| Serving | query concurrency or batching under test | scientific | system treatment |
| Evaluation | judge, rubric, calibration set | analysis protocol | evaluation activity |

The distinction in the third column is critical. `max_in_flight: 20` may simply make the study finish sooner. `query_concurrency: 20` may be a treatment if the study measures tail latency or provider throttling. The same-looking number can have completely different scientific meaning.

### 2.3 Why a naïve grid is unacceptable

A modest factor set can already produce thousands of configurations. For example:

```text
3 chunk methods
x 3 chunk sizes
x 3 enrichment modes
x 2 embedding models
x 3 retriever families
x 3 top-k values
x 2 reranker choices
x 2 answer models
x 3 query-concurrency settings
= 5,832 configurations
```

Three run-level replicates would require 17,496 study runs, before accounting for stochastic answer samples or judge replication.

The architecture must therefore support:

- staged studies;
- screening designs;
- user-supplied assignment tables;
- constrained and conditional search spaces;
- adaptive ask/tell optimization;
- upstream artifact reuse;
- exact preservation of why each assignment was selected.

Experiment design is not just a scheduler feature. It is first-class research provenance.

---

## 3. What the prototype taught us

The prototype contains several strong ideas worth retaining:

- strict schemas and unknown-field rejection;
- stable, canonical identities;
- a real distinction between scientific replicates and technical attempts;
- append-only run custody;
- verified artifact digests and safe path handling;
- process-boundary validation and cancellation tests;
- deterministic plan expansion;
- immutable run exports;
- explicit missingness and unit checks in basic summaries.

It also demonstrated several boundaries that should be redrawn:

- a claim/evidence/project graph should not be the execution kernel;
- project JavaScript, plan JavaScript, analysis JavaScript, a simulator DSL, a REPL, and plugins create too many user mental models;
- a run identity, a desired replicate slot, and a reusable cache entry are different things;
- plan membership should not live primarily inside an attempt environment object;
- terminal failure must never silently satisfy a desired replicate;
- inline base64 artifacts in an NDJSON stream are not a general artifact transport;
- a closed reducer engine is useful for summaries but should not pretend to replace Python, R, Julia, Stan, or domain analysis code;
- report generation must join the protocol, actual executions, analyses, and reviewed evidence rather than rendering a largely separate project graph;
- a generic plugin registry is premature until one first-party domain workflow is excellent.

The clean system copies tested low-level code where appropriate, but replaces the product model.

---

## 4. Design principles

### 4.1 Canonical data is authoritative; code is a compiler

The frozen protocol, study design, assignments, workflow IR, and result manifests are versioned JSON-compatible data. YAML is an authoring serialization. A Python SDK may generate the same data for convenience.

The digest is calculated over normalized canonical data, not over the Python or YAML source text. The source is retained as provenance, but the compiled document is authoritative.

This gives four benefits:

- a protocol can be reviewed without executing arbitrary code;
- multiple authoring tools can target the same contract;
- the frozen object can be signed and compared;
- the executor does not need the authoring runtime.

### 4.2 Prospective and retrospective provenance are separate

A protocol or execution plan describes what is intended. Run and step records describe what actually happened. The system never overwrites the plan with the outcome and never pretends an intended step executed merely because it appeared in the DAG.

### 4.3 Scientific identity is separate from computational cache identity

A case is a scientific treatment combination. An assignment is a planned occurrence of a case in a block and replicate slot. A run is an actual observation. A cache entry is a reusable computational result.

A cache hit may save computation, but it still creates a new run or step-run record for the new study and records that the outputs were materialized from an earlier computation.

### 4.4 Scientific factors, blocks, covariates, and execution policy are typed separately

Every parameter belongs to one of these roles:

- `treatment`: intentionally varied to estimate an effect;
- `block`: known nuisance factor used in assignment and analysis;
- `covariate`: measured context that may explain variation;
- `fixed`: scientifically relevant but not varied in this study;
- `execution`: operational scheduler policy, not part of the treatment;
- `secret`: referenced by identity/version only, never serialized as a value.

The role is not inferred from a key name.

### 4.5 Artifacts are first-class immutable entities

Every material input or output has:

- a cryptographic digest;
- byte size;
- media type;
- logical/schema type;
- storage location;
- producing activity;
- input/derivation edges;
- classification and retention policy.

A path is a convenience. The digest is the identity.

### 4.6 The generic core does not understand RAG

The core understands protocols, studies, assignments, activities, artifacts, observations, executors, and provenance. A RAG domain package understands chunkers, enrichers, embedding models, index types, retrieval traces, answer records, and RAG metrics.

The domain package compiles a RAG case into a generic execution plan.

### 4.7 Ordinary scientific code remains ordinary code

Steps may be Python, R, Julia, shell, a compiled binary, a container, a CWL tool, a Snakemake workflow, or a Nextflow pipeline. The system wraps and records them; it does not force every computation into a custom DSL.

### 4.8 Analysis is another recorded activity

An analysis consumes a frozen study dataset and produces tables, models, figures, and reports. It has code, an environment, inputs, outputs, logs, and provenance like any other computation.

A small built-in summarizer may exist, but it is explicitly a convenience layer.

### 4.9 Local-first does not mean local-only

The first release should work as one binary with SQLite and a filesystem CAS. The contracts must also map cleanly to PostgreSQL plus S3/OCI storage and remote executors.

### 4.10 Corrections are explicit revisions, not forbidden realities

Run facts are append-only. Human-entered metadata, evidence, and decisions may need correction. Corrections create superseding revisions or annotations. Sensitive artifacts may be tombstoned or deleted according to policy while retaining a provenance record that deletion occurred.

---

## 5. Core conceptual model

### 5.1 Protocol revision

A **ProtocolRevision** is a content-addressed, reviewable statement of:

- research questions and hypotheses;
- datasets and their frozen identities;
- primary and secondary outcomes;
- factors and allowed levels;
- constraints and conditional parameters;
- replication, blocking, randomization, and exclusion rules;
- pipeline template and domain configuration;
- analysis plan;
- stopping rules and resource budget;
- reproducibility expectations.

A draft may change. A frozen revision cannot. An amendment creates a child revision with a reason.

### 5.2 Study

A **Study** binds one frozen protocol revision to one concrete design realization:

- design generator and version;
- randomization seed;
- immutable assignment table;
- block definitions;
- staged or adaptive wave history;
- execution policy;
- budget;
- development or confirmatory status.

The study digest includes the assignment-table digest. Two studies may use the same protocol revision but different randomizations or stages.

### 5.3 Case

A **Case** is a unique scientific treatment combination after defaults and conditional rules are resolved. It contains only scientifically meaningful configuration and fixed scientific inputs.

Display names and scheduler settings do not enter the case digest.

### 5.4 Assignment

An **Assignment** is a desired observation slot:

```text
study + case + block + replicate index + planned/randomized ordinal
```

An assignment remains unfilled until a valid run closes successfully or a scientist explicitly marks it excluded or waived with a reason. A failed run does not fill it.

### 5.5 Run

A **Run** is an occurrence that attempts to fill an assignment. It has a unique occurrence ID, timestamps, realized block/covariate information, and terminal outcome.

A replacement run can target the same assignment after a technical or scientific failure. The replacement relationship is explicit.

### 5.6 Attempt

An **Attempt** is a technical retry within a run. It records:

- resolved execution fingerprint;
- executor and executor version;
- runtime environment attestation;
- step executions;
- logs and failure classification;
- start/end times;
- cancellation and timeout behavior.

Retries do not increment scientific replication.

### 5.7 Step run

A **StepRun** is one realized execution of a workflow node within an attempt. It records exact inputs, implementation, environment, parameters, output artifacts, observations, and cache disposition.

### 5.8 Artifact

An **Artifact** is a file, directory tree, dataset, model, index snapshot, log set, or external immutable object identified by digest or by a versioned external identifier plus verification policy.

### 5.9 Observation set

An **ObservationSet** is a typed, potentially large dataset of measurements. Examples:

- one-row run summary;
- query-level retrieval metrics;
- answer-level judge results;
- step timing events;
- provider token and cost records;
- failure records.

Large observations belong in Parquet/Arrow/JSONL artifacts. The relational ledger stores searchable summaries and references, not millions of individual event rows by default.

### 5.10 Analysis run

An **AnalysisRun** consumes an exact study snapshot and produces derived artifacts. It records exclusions, model formulas, code, environment, and outputs.

### 5.11 Evidence revision

An **EvidenceRevision** is a reviewed interpretation that cites analysis and source artifacts. The system may draft factual evidence, but acceptance, confidence, limitations, and claim direction require human review.

### 5.12 Decision revision

A **DecisionRevision** records the action taken, evidence considered, confidence, limitations, and reversal conditions.

### 5.13 Identity hierarchy

```text
protocol revision digest
  -> study ID + study digest
      -> case digest
          -> assignment ID
              -> run ID
                  -> attempt ID
                      -> step-run ID
                          -> artifact digest / observation-set digest

execution fingerprint
  -> cache record
      -> may be reused by many step-runs

analysis-run ID
  -> evidence revision
      -> decision revision
```

This hierarchy is the most important correction to the prototype.

---

## 6. The RAG pipeline as a typed artifact DAG

A RAG pipeline is not one opaque command. It is a DAG whose boundaries are chosen to make scientific changes and computational reuse visible.

```text
CorpusSnapshot
    |
    v
ParseDocuments -> NormalizedDocuments -> ChunkSet
                                         |      \
                                         |       -> SyntheticQuestionSet
                                         -> ChunkSummarySet
                                                  |
ChunkSet + enrichments ---------------------------+
    |                                              |
    +-> LexicalIndex                               +-> EmbeddingSet -> VectorIndex
                                                        
EvaluationQueries -> QueryPreparation
                         |
                         v
       LexicalIndex / VectorIndex -> RetrievalResults
                                      |
                                      v
                                FusedCandidates
                                      |
                                      v
                                RerankedCandidates
                                      |
                                      v
                                  ContextSet
                                      |
                                      v
                                    AnswerSet
                                      |
                                      v
                                EvaluationTable
```

### 6.1 Recommended RAG artifact types

| Logical type | Required content |
|---|---|
| `rag/corpus-snapshot/v1` | source identities, licensing/classification, file manifests |
| `rag/document-set/v1` | normalized document IDs, text, metadata, source lineage |
| `rag/chunk-set/v1` | chunk IDs, document spans, token counts, parent/neighbor links |
| `rag/chunk-summary-set/v1` | chunk ID, prompt/model provenance, summary text |
| `rag/synthetic-question-set/v1` | chunk ID, generated questions, generation provenance |
| `rag/embedding-set/v1` | row-to-chunk mapping, vector dimensions/type, model provenance |
| `rag/lexical-index/v1` | engine snapshot or rebuild manifest, analyzer configuration |
| `rag/vector-index/v1` | engine snapshot or rebuild manifest, distance/index parameters |
| `rag/retrieval-results/v1` | query, rank, score, source channel, chunk ID, timing |
| `rag/context-set/v1` | selected chunks, order, token budget, truncation decisions |
| `rag/answer-set/v1` | query, answer sample, citations, raw model response metadata |
| `rag/evaluation-table/v1` | raw and derived retrieval/generation/system measurements |

Each artifact schema is owned by the RAG package, not the generic core.

### 6.2 Why these boundaries matter

Changing the answer prompt should not rebuild an index. Changing `top_k` should not recompute embeddings. Changing the reranker should reuse retrieval candidates. Changing chunk size should invalidate all downstream artifacts.

The planner creates a graph of **unique materializations**, not a separate full pipeline per case. If 60 cases share one chunk set, that chunk set is built once and referenced by 60 downstream branches.

### 6.3 Managed services

Some indexes or models live in external services and cannot be copied as files. The artifact then represents a verified snapshot reference:

```yaml
logicalType: rag/vector-index/v1
external:
  provider: example-vector-service
  collectionId: rag-study-2026-07
  snapshotId: snap-01H...
  region: us-east
  configurationDigest: sha256:...
verification:
  mode: provider-snapshot
reproducibilityClass: provider-dependent
```

The system must state honestly that this is not bitwise portable.

---

## 7. Authoring model

### 7.1 Canonical protocol YAML

A representative protocol might look like this:

```yaml
schemaVersion: researchctl-protocol/v1
kind: ResearchProtocol
id: RAG-CORPUS-QUALITY-01
name: Chunking, retrieval, and answer-quality study

question:
  text: >-
    Which RAG pipeline maximizes held-out answer correctness subject to
    retrieval coverage, latency, cost, and abstention constraints?
  hypotheses:
    - id: H-CHUNK
      claim: Structural chunking improves retrieval coverage over fixed windows.
    - id: H-ENRICH
      claim: Summary and synthetic-question enrichment improve hybrid retrieval.
    - id: H-RERANK
      claim: Reranking improves answer correctness enough to justify its cost.

inputs:
  corpus:
    artifact: sha256:CORPUS...
    logicalType: rag/corpus-snapshot/v1
  developmentQuestions:
    artifact: sha256:DEVSET...
    logicalType: rag/question-set/v1
  holdoutQuestions:
    artifact: sha256:HOLDOUT...
    logicalType: rag/question-set/v1
    access: blinded-until-confirmation

pipeline:
  domain: rag
  template: rag/full-evaluation/v1
  fixed:
    normalize.deduplicate: exact-and-near
    answer.citationPolicy: required
    evaluation.unanswerablePolicy: explicit-abstention

factors:
  - path: chunk.method
    role: treatment
    type: categorical
    levels: [recursive, structural, semantic]
  - path: chunk.targetTokens
    role: treatment
    type: integer
    levels: [256, 512, 1024]
    unit: tokens
  - path: chunk.overlapTokens
    role: treatment
    type: integer
    levels: [0, 64]
    unit: tokens
  - path: enrichment.mode
    role: treatment
    type: categorical
    levels: [none, summary, summary-and-questions]
  - path: embedding.model
    role: treatment
    type: categorical
    levels: [embed-small-v3, embed-large-v3]
  - path: retrieval.kind
    role: treatment
    type: categorical
    levels: [bm25, vector, hybrid]
  - path: retrieval.topK
    role: treatment
    type: integer
    levels: [5, 10, 20]
  - path: retrieval.hybrid.alpha
    role: treatment
    type: decimal-string
    levels: ["0.25", "0.50", "0.75"]
    when: retrieval.kind == "hybrid"
  - path: rerank.kind
    role: treatment
    type: categorical
    levels: [none, cross-encoder]
  - path: answer.model
    role: treatment
    type: categorical
    levels: [answer-small, answer-large]
  - path: answer.temperature
    role: fixed
    type: decimal-string
    value: "0.0"
  - path: serving.queryConcurrency
    role: treatment
    type: integer
    levels: [1, 8, 32]

blocks:
  - name: executionDay
    source: runtime.date
  - name: acceleratorClass
    source: runtime.accelerator.class

constraints:
  - expression: retrieval.kind != "hybrid" implies absent(retrieval.hybrid.alpha)
  - expression: enrichment.mode == "none" implies absent(enrichment.generator)

outcomes:
  primary:
    metric: answer.correctness
    sampleUnit: query
    direction: maximize
  secondary:
    - metric: retrieval.ndcg_at_10
      direction: maximize
    - metric: answer.faithfulness
      direction: maximize
    - metric: system.latency_p95
      direction: minimize
      unit: milliseconds
    - metric: system.cost_per_query
      direction: minimize
      unit: USD
  constraints:
    - metric: retrieval.recall_at_20
      op: ">="
      value: 0.90
    - metric: system.latency_p95
      op: "<="
      value: 2500
      unit: milliseconds

replication:
  runReplicates: 3
  seedPolicy: derived-from-assignment
  failedAssignmentPolicy: replace-with-linked-run

analysisPlan:
  entrypoint: analysis/confirmatory.py
  environment:
    ociImage: ghcr.io/example/rag-analysis@sha256:IMAGE...
  exclusions:
    - failed-before-answer-generation
    - corpus-integrity-failure
  multiplicityPolicy: hierarchical-fdr

stages:
  - id: calibration
    dataset: developmentQuestions
    design: user-table
    assignments: designs/calibration.csv
  - id: screening
    dataset: developmentQuestions
    design:
      kind: fractional-or-space-filling
      budget: 72
  - id: focused
    dataset: developmentQuestions
    design:
      kind: user-table
      assignments: designs/focused.csv
  - id: confirmation
    dataset: holdoutQuestions
    design:
      kind: finalists
      maximumCases: 3
```

This file is reviewed and compiled to canonical JSON. The frozen compiled document receives a digest. The YAML remains an authored source artifact.

### 7.2 Optional Python builder

A Python SDK is useful to generate constrained factors, import sample metadata, or build assignment tables. It must compile to the same canonical protocol object.

```python
from researchctl import Protocol, Factor

protocol = (
    Protocol("RAG-CORPUS-QUALITY-01")
    .factor(Factor.categorical("chunk.method", ["recursive", "structural", "semantic"]))
    .factor(Factor.integer("retrieval.topK", [5, 10, 20]))
)

protocol.write("protocol.compiled.json")
```

The Python source is not the protocol identity. `protocol.compiled.json` is.

### 7.3 Canonicalization

Use RFC 8785 JSON Canonicalization Scheme through a maintained implementation rather than another custom serializer. Domain-separate digests:

```text
sha256("researchctl:protocol:v1\0" + JCS(protocol))
sha256("researchctl:study:v1\0" + JCS(study))
sha256("researchctl:execution-plan:v1\0" + JCS(plan))
```

Precise decimal factor values should be strings or typed quantities. Display labels, comments, and creation timestamps are stored but excluded from scientific identity unless semantically required.

---

## 8. Experimental-design compiler

### 8.1 Output: an immutable assignment table

The design compiler does not directly launch work. It produces an assignment artifact such as:

| assignment_id | case_digest | block | replicate | randomized_ordinal | factors_digest |
|---|---|---|---:|---:|---|
| ASN-001 | sha256:A | day-1/gpu-a | 1 | 14 | sha256:FA |
| ASN-002 | sha256:B | day-1/gpu-a | 1 | 2 | sha256:FB |
| ASN-003 | sha256:A | day-2/gpu-b | 2 | 7 | sha256:FA |

The assignment table and design metadata are content-addressed and included in the study digest.

### 8.2 Supported design modes

The first clean release should support only a small, explicit set:

1. `grid`: exhaustive constrained Cartesian product.
2. `random`: seeded random sample from the valid search space.
3. `space-filling`: Sobol or Latin-hypercube style generator supplied by a design package.
4. `user-table`: CSV/Parquet assignments created by the scientist or statistical software.
5. `finalists`: selected cases from a prior stage with recorded selection criteria.
6. `adaptive`: ask/tell service that emits assignments in waves.

Advanced factorial and response-surface generation can be separate libraries. The core only needs a stable assignment contract and provenance for the generator.

### 8.3 Staged RAG design

A sensible program for the scenario is:

#### Stage 0: calibration and contract tests

Use 20–50 questions and a handful of cases to verify:

- every artifact schema;
- metric completeness;
- citation parsing;
- judge calibration;
- timeout and failure handling;
- deterministic seeds;
- resource estimates.

These results are exploratory and do not support the final claim.

#### Stage 1: screening

Use a budgeted design to identify the influential phase choices. Run cheaper answer models and a development subset. Preserve enough interaction coverage to detect obvious chunking/retriever and retrieval/reranker interactions.

#### Stage 2: focused comparison

Select a small region and use a balanced, blocked design with full query coverage and multiple run-level replicates. Include current production and simple baselines.

#### Stage 3: confirmatory holdout

Freeze finalists and analysis code before unblinding the holdout. Run only the declared finalists, with exact replacement/exclusion rules.

This staged workflow is more defensible and economical than a giant grid. Screening and subsequent focused modeling are standard experimental-design patterns when many candidate factors exist.

### 8.4 Blocking and randomization

A block is explicit data, not an ordering strategy. Examples:

- execution day;
- GPU class;
- provider region;
- index shard allocation;
- corpus ingestion batch;
- evaluator/judge batch.

The planner randomizes assignments within blocks. It records:

- planned randomized ordinal;
- scheduler admission ordinal;
- actual start and end timestamps;
- resolved worker and hardware;
- any deviation from assignment order.

Operational concurrency means planned order and realized temporal order can differ. Both are preserved.

### 8.5 Experimental units and repeated observations

A query-level metric is not automatically an independent replicate of an index-building treatment. Queries are often paired repeated observations within a pipeline run. The system therefore requires every observation schema to declare a sample unit and scope.

Examples:

```text
retrieval.ndcg_at_10
  sampleUnit: query
  nestedWithin: run

system.index_build_seconds
  sampleUnit: index-build-run

answer.correctness
  sampleUnit: query-answer-sample
  nestedWithin: query, run
```

The system should prevent the built-in summarizer from presenting query count as run-level `n`. Serious analysis remains explicit statistical code.

### 8.6 Adaptive optimization

An adaptive study uses an append-only sequence:

```text
wave 1 assignments -> observations -> optimizer state/result
                                      |
                                      v
wave 2 suggestions -> reviewed/admitted assignments -> ...
```

Every suggestion records:

- optimizer implementation and version;
- previous observation snapshot digest;
- search-space digest;
- RNG seed/state;
- acquisition or selection metadata;
- admitted, rejected, or modified disposition.

An optimizer suggestion is not silently treated as a preregistered confirmatory assignment.

---

## 9. Domain compilation and generic execution IR

### 9.1 Three compilation levels

```text
ResearchProtocol
  scientific questions, factors, outcomes, design
        |
        v
RagCasePlan
  RAG-specific resolved component graph and typed contracts
        |
        v
ExecutionPlan
  domain-neutral DAG of executable nodes and artifact edges
```

Each level is schema-versioned, canonicalized, and stored.

### 9.2 Domain compiler contract

The core invokes a configured compiler executable. Avoid an in-process generic plugin runtime in the first release.

```text
researchctl-domain/v1 describe
researchctl-domain/v1 validate
researchctl-domain/v1 compile-case
```

Input and output are JSON files or stdin/stdout messages. The compiler returns:

- resolved defaults;
- case identity data;
- generic execution plan;
- expected artifact and observation schemas;
- human-readable explanation;
- compiler identity and source digest.

### 9.3 Generic execution node

A generic node contains:

```yaml
key: build-vector-index
implementation:
  kind: oci-command
  image: ghcr.io/example/rag-worker@sha256:...
  command: [python, -m, rag_worker.build_vector_index]
  codeArtifact: sha256:SOURCE_BUNDLE...
inputs:
  - role: embeddings
    fromNode: embed-chunks
    output: embeddings
parameters:
  distance: cosine
  hnsw:
    m: 32
    efConstruction: 200
outputs:
  - role: index
    logicalType: rag/vector-index/v1
    mediaType: application/vnd.researchctl.artifact-tree+json
observations:
  - schema: rag/index-build-metrics/v1
resources:
  cpu: 8
  memory: 32GiB
  accelerator: none
capabilities:
  network: false
  secrets: []
cache:
  mode: exact
reproducibility:
  class: environment-pinned
```

### 9.4 Executor interface

An executor adapter supports:

```text
prepare(plan, attempt_context) -> prepared_execution
submit(prepared_execution) -> external_execution_id
inspect(external_execution_id) -> state
cancel(external_execution_id, reason)
collect(external_execution_id) -> result_manifest
```

Initial adapters:

1. local process/container executor;
2. existing Scraper Workflow adapter;
3. one standards-oriented adapter such as CWL or a Nextflow/Snakemake wrapper.

The core does not schedule individual remote jobs when the delegated workflow engine already owns that problem.

### 9.5 Local step sandbox

Each local step receives a private directory:

```text
step/
  request.json          read-only execution request
  inputs/               read-only materialized artifacts
  work/                 scratch space
  outputs/              only declared results
  result.json           terminal result manifest
  logs/
    stdout.log
    stderr.log
  telemetry/            optional compressed events/traces
```

The process receives only explicit environment variables and secret handles. It does not inherit the entire parent environment.

### 9.6 Result manifest

```yaml
schemaVersion: researchctl-step-result/v1
status: succeeded
outputs:
  - role: retrieval-results
    path: outputs/retrieval.parquet
    logicalType: rag/retrieval-results/v1
    mediaType: application/vnd.apache.parquet
observations:
  summary:
    - name: retrieval.query_count
      value: 2000
      unit: queries
  sets:
    - path: outputs/retrieval_metrics.parquet
      schema: rag/retrieval-metrics/v1
telemetry:
  events: telemetry/events.jsonl.zst
  traces: telemetry/traces.jsonl.zst
providerRecords:
  - path: outputs/provider_requests.parquet
```

The core verifies and imports declared files after the process closes. Artifacts are never transported as base64 inside lifecycle events.

### 9.7 Progress and streaming

A small NDJSON or socket channel may carry:

- heartbeat;
- progress counters;
- structured warnings;
- external operation IDs;
- provisional metrics.

It is not the artifact transport and not the sole durable record. Durable files are imported at checkpoints or completion.

---

## 10. Reproducibility and identity

### 10.1 Three identities, three purposes

#### Case digest

Answers: “Is this the same scientific treatment?”

Includes:

- resolved scientific factors;
- fixed scientific configuration;
- frozen scientific input artifact identities;
- domain template/compiler contract versions.

Excludes:

- timestamps;
- display labels;
- scheduler concurrency;
- occurrence IDs.

#### Execution fingerprint

Answers: “Can this computational result be reused exactly or compatibly?”

Calculated per step and includes:

- implementation type and command;
- source bundle or binary digest;
- OCI image digest or full environment lock digest;
- input artifact digests;
- normalized step parameters;
- RNG algorithm and seed;
- executor semantics version;
- declared non-secret environment values;
- relevant secret reference versions when semantically meaningful;
- required hardware/driver compatibility class;
- external provider/model identity and request semantics;
- cache policy version.

#### Run ID

Answers: “Which occurrence filled or attempted this assignment?”

It is always unique, even when all results came from cache.

### 10.2 Runtime attestation

The control plane records what was resolved, not merely what the user requested:

- source repository, commit, and dirty patch/source bundle digest;
- command and arguments;
- executable digest where possible;
- container manifest digest and platform manifest digest;
- dependency lock digest;
- OS, kernel, architecture, locale, timezone;
- CPU/GPU/accelerator, driver, and relevant library versions;
- environment allowlist and captured values;
- secret reference names and versions, never values;
- hosted model requested alias and returned/resolved model metadata;
- provider request IDs, region, client version, and response metadata;
- clock source and timestamps.

The provenance model should borrow the useful distinction from software-build attestations: external parameters, internal/resolved parameters, dependencies, builder identity, and output subjects.

### 10.3 Reproducibility classes

Every step declares one of:

- `bitwise`: same exact environment and inputs are expected to produce identical bytes;
- `deterministic-logical`: content may serialize differently but normalized results should match;
- `statistical`: stochastic outputs are expected; seeds and distributional comparison are required;
- `provider-dependent`: hosted service behavior cannot be fully pinned;
- `non-reproducible`: allowed only in exploratory mode or with an explicit waiver.

This classification appears in reports. The system never labels a hosted-model call “fully reproducible” merely because the request JSON was saved.

### 10.4 Cache record

A cache record contains:

```text
execution fingerprint
result manifest digest
output artifact digests
producer step-run
verification status
compatibility class
creation time
retention status
```

A cache lookup returns a candidate. The core verifies all output artifacts and compatibility policy before reuse.

### 10.5 Cache hit semantics

On a cache hit:

1. create the new step-run occurrence;
2. record `disposition: materialized-from-cache`;
3. link to the producer step-run and cache record;
4. verify referenced outputs;
5. attach those outputs to the new activity via derivation/reuse edges;
6. continue downstream.

No prior run is relabeled as belonging to the new study.

### 10.6 Resume semantics

`resume` means: continue filling the same immutable study assignment table.

For each assignment:

- successful compatible run: assignment is filled;
- active run with live ownership: monitor it;
- orphaned active run: explicit recovery operation;
- failed/cancelled/abandoned run: assignment remains unfilled;
- excluded run: apply declared replacement rule;
- changed protocol or assignment table: a different study, not a resume.

Runner or environment changes may reuse step-level cache where policy permits, but they never cause a failed or incompatible run to count silently.

### 10.7 Retry semantics

- step retry: another step attempt within the same run attempt;
- run attempt retry: same scientific run, same assignment and seeds;
- replacement run: new run occurrence linked to the failed/excluded run;
- additional scientific replicate: new assignment.

External operations should use idempotency keys derived from step-run identity where supported.

---

## 11. Artifact store

### 11.1 Content-addressed storage

Local layout:

```text
.researchctl/
  objects/
    sha256/ab/cd/abcdef...
  manifests/
  staging/
  ledger.sqlite
```

Shared mode:

- PostgreSQL metadata;
- S3/GCS/Azure/OCI-compatible object storage;
- direct client upload for large artifacts;
- signed URLs or workload identity.

### 11.2 File artifact

```yaml
schemaVersion: researchctl-artifact/v1
digest: sha256:...
sizeBytes: 1840021
mediaType: application/vnd.apache.parquet
logicalType: rag/retrieval-results/v1
storage:
  uri: cas://sha256/...
classification: internal
```

### 11.3 Directory/tree artifact

A tree is represented by a sorted Merkle-style manifest containing relative POSIX paths, digest, size, and media type. The tree manifest itself has a digest.

This is appropriate for vector index snapshots, model directories, and report bundles.

### 11.4 Staging and large files

Workers write to a per-step staging directory or upload directly to an object-store staging prefix. The control plane:

1. checks path confinement;
2. computes/verifies size and digest;
3. validates the logical schema where possible;
4. atomically promotes the object into CAS;
5. records the generation edge.

No general artifact size limit is imposed by the event protocol.

### 11.5 Logical aliases

Human-facing aliases may point to immutable digests:

```text
study/RAG-01/final/vector-index -> sha256:...
```

Changing an alias creates a new alias revision. It does not mutate the artifact.

### 11.6 Retention, deletion, and sensitive data

Artifact metadata includes:

- classification;
- encryption policy;
- retention class;
- legal hold;
- exportability;
- redaction/tombstone state.

If policy requires deletion, bytes are deleted and a tombstone event remains. The system must not use “immutability” to violate privacy or regulatory obligations.

---

## 12. Ledger and storage model

### 12.1 Relational, typed, append-oriented

Do not store the primary system as a generic entity graph. Use typed relational tables with constraints and explicit provenance edge tables. Export to graph standards later.

Representative tables:

```text
protocol_revision
study
study_stage
case_definition
block_definition
assignment
run
run_attempt
step_run
step_attempt
artifact
activity_input
activity_output
cache_record
observation_set
metric_summary
state_transition
annotation
analysis_run
evidence_revision
decision_revision
agent
runtime_attestation
```

### 12.2 Key relationships

```text
protocol_revision 1---* study
study 1---* assignment
case_definition 1---* assignment
assignment 1---* run
run 1---* run_attempt
run_attempt 1---* step_run
step_run *---* artifact through activity_input/activity_output
step_run 0..1---1 cache_record reuse relation
study 1---* analysis_run
analysis_run *---* evidence_revision
evidence_revision *---* decision_revision
```

### 12.3 Immutable facts and mutable projections

Primary records and terminal summaries are append-only. Current status is a materialized projection of `state_transition` events.

This allows:

- clear audit history;
- corrections through superseding annotations;
- efficient current-state queries;
- crash-safe transactions without committing to full event sourcing.

### 12.4 SQLite and PostgreSQL

Use the same logical schema with dialect-specific migrations.

Local SQLite requirements:

- foreign keys enabled;
- WAL mode;
- explicit read-only/read-write/execute connections;
- transactionally closed attempts and runs;
- periodic integrity checks;
- export and backup commands.

Shared PostgreSQL adds:

- row-level authorization;
- leases and advisory locks;
- concurrent workers;
- notification/event delivery;
- durable object-store references.

### 12.5 Observation volume

Do not insert every token event, retrieval candidate, or provider operation as an individual relational row by default.

Store:

- searchable run/step summaries in SQL;
- high-volume telemetry and query-level records as compressed typed artifacts;
- optional indexes or projections for commonly queried fields.

This avoids transaction-per-event bottlenecks while retaining full data.

---

## 13. The RAG domain package

The RAG package is a separate versioned component with four responsibilities.

### 13.1 Schemas

It owns schemas for:

- RAG protocol configuration;
- document, chunk, enrichment, embedding, index, retrieval, context, answer, and evaluation artifacts;
- RAG metrics and telemetry;
- provider/model references;
- index-engine snapshots.

### 13.2 Compiler

It resolves one case into a generic execution plan. It performs domain validation such as:

- hybrid retrieval requires compatible lexical and vector indexes;
- cosine search requires normalized vectors when the implementation contract requires it;
- reranker candidate count must not exceed retrieval candidate count;
- context token budget must fit the selected answer model contract;
- enrichment references must correspond to the same chunk-set digest;
- index and query embedding models must match;
- conditional factor values must be absent when irrelevant.

### 13.3 Workers

Reference workers implement stable CLIs:

```text
rag-worker parse
rag-worker normalize
rag-worker chunk
rag-worker summarize
rag-worker generate-questions
rag-worker embed
rag-worker build-index
rag-worker retrieve
rag-worker rerank
rag-worker pack-context
rag-worker answer
rag-worker evaluate
```

They consume request files and typed artifacts and produce result manifests. Users may replace any worker with another implementation that satisfies the same contract.

### 13.4 Metric catalog

The package publishes metric definitions including:

- name and schema version;
- unit;
- scope and sample unit;
- direction;
- required inputs;
- producer implementation;
- aggregation caveats.

Examples:

```text
retrieval.recall_at_k
retrieval.mrr
retrieval.ndcg_at_k
retrieval.context_precision
answer.correctness
answer.faithfulness
answer.citation_precision
answer.citation_recall
answer.abstention_accuracy
system.latency_ms
system.cost_usd
system.provider_retries
system.rate_limit_failures
```

The core treats these as typed observations without claiming domain ownership.

---

## 14. Evaluation and analysis

### 14.1 Evaluate components separately

RAG is modular. A single final-answer score cannot explain failure. The study should record at least:

- retrieval effectiveness;
- context composition;
- generator use of retrieved evidence;
- answer correctness and completeness;
- faithfulness/citation support;
- abstention behavior;
- latency, cost, throughput, and failures.

This follows the practical lesson of RAG evaluation frameworks: retrieval and generation require separate, diagnostic measurements rather than only an aggregate score.

### 14.2 Query-level data model

A generated analysis dataset should contain linked tidy tables:

```text
cases.parquet
assignments.parquet
runs.parquet
queries.parquet
retrieval_candidates.parquet
retrieval_metrics.parquet
contexts.parquet
answers.parquet
answer_metrics.parquet
system_metrics.parquet
failures.parquet
artifacts.parquet
```

Every row carries the relevant case, assignment, run, attempt, query, and sample IDs.

### 14.3 Failures and missingness

A failed query is not silently omitted. The dataset records:

- phase of failure;
- retry count;
- terminal classification;
- whether an answer exists;
- which metrics are undefined;
- exclusion rule, if any.

Coverage is reported beside every aggregate.

### 14.4 LLM judges

An LLM judge is another model-based measurement instrument. Capture:

- judge provider and resolved model metadata;
- prompt/rubric digest;
- temperature and seed where supported;
- raw input and verdict artifacts subject to privacy policy;
- calibration dataset digest;
- human agreement metrics;
- repeated-judge policy;
- failure and refusal records.

Judge scores should not replace retrieval ground truth or human review where those are available.

### 14.5 Analysis as executable workflow

An analysis definition is ordinary code plus an execution manifest:

```yaml
schemaVersion: researchctl-analysis/v1
id: rag-confirmatory-analysis
entrypoint: analysis/confirmatory.py
environment:
  ociImage: ghcr.io/example/rag-analysis@sha256:...
inputs:
  studySnapshot: STUDY-SNAPSHOT-DIGEST
outputs:
  - role: model-results
    logicalType: researchctl/statistical-results/v1
  - role: figures
    logicalType: researchctl/figure-bundle/v1
  - role: report
    logicalType: researchctl/analysis-report/v1
```

The analysis writes a machine-readable result manifest with:

- selected assignments and runs;
- exclusions and reasons;
- formulas/models;
- estimates and uncertainty;
- multiplicity handling;
- diagnostics;
- output artifacts;
- interpretation draft.

### 14.6 Built-in summarizer

A small built-in command may provide:

- completeness tables;
- grouped means/medians/quantiles;
- paired differences;
- Pareto-front views;
- cost and latency plots;
- missingness/failure summaries.

Call it `researchctl summarize`, not a general analysis system.

### 14.7 Multi-objective decisions

The report should show:

- feasible configurations satisfying hard constraints;
- Pareto frontier for correctness, latency, and cost;
- uncertainty intervals;
- performance by question stratum;
- robustness across blocks;
- sensitivity to exclusions and judge choice.

The decision layer chooses among feasible alternatives; the platform does not hide the tradeoff in a proprietary scalar.

---

## 15. Evidence, decisions, and reports

### 15.1 Automatic factual drafting

After an analysis closes, the system can draft statements such as:

> Analysis `ANL-123` consumed study snapshot `sha256:...`, included 69 of 72 planned assignments, and found configuration `CASE-X` had an estimated +4.1 percentage-point answer-correctness difference versus baseline, with the recorded interval and diagnostics shown in artifact `sha256:...`.

That draft is factual provenance, not automatic scientific acceptance.

### 15.2 Human evidence review

A scientist reviews and records:

- claim direction: supports, contradicts, inconclusive;
- confidence;
- limitations;
- generalization scope;
- sensitivity to assumptions;
- relevant failed or excluded runs;
- reviewer identity and date.

### 15.3 Decision record

A decision might state:

- selected configuration;
- operational constraints;
- evidence references;
- rejected alternatives;
- confidence;
- deployment or next-study action;
- reversal conditions.

### 15.4 Report assembly

A report joins:

1. protocol revision and amendment history;
2. study design and assignment table;
3. execution completeness and deviations;
4. environment and reproducibility classes;
5. analysis artifacts;
6. reviewed evidence;
7. decisions and reversal conditions.

Reports are views over the authoritative records, not a separate hand-maintained graph.

---

## 16. User experience

### 16.1 Two modes

#### Exploratory mode

Low ceremony. Every run still captures code, inputs, and environment, but the protocol may be mutable and assignments are not confirmatory.

```bash
researchctl explore run rag-draft.yaml --executor local
```

#### Registered study mode

Protocol and assignment table are frozen before execution.

```bash
researchctl protocol validate protocol.yaml
researchctl protocol freeze protocol.yaml
researchctl study plan protocol.lock.json --stage screening
researchctl study explain study.lock.json
researchctl study run study.lock.json --executor local
```

Exploratory results may be imported as background evidence but cannot silently fill registered assignments.

### 16.2 CLI surface

```text
researchctl init --template rag

researchctl protocol validate|compile|freeze|diff|amend
researchctl study plan|explain|run|status|resume|close|snapshot
researchctl run show|follow|replace|exclude
researchctl artifact show|verify|materialize|gc
researchctl summarize
researchctl analysis run|show
researchctl evidence draft|review|show
researchctl decision create|supersede|show
researchctl report render
researchctl pack --format ro-crate
researchctl export --format prov|openlineage|mlflow
```

No `apply` command. Scaffolding is `init` or `scaffold`; execution is `run`.

### 16.3 Workspace layout

```text
rag-study/
  protocol.yaml
  protocol.lock.json
  pipeline/
  designs/
    screening.csv
    focused.csv
  analysis/
    confirmatory.py
    environment.lock
  researchctl.toml
  .researchctl/
    ledger.sqlite
    objects/
    staging/
    snapshots/
  reports/
```

Only authored source files need to be pleasant to edit. Generated lock files and ledger records are machine-owned.

### 16.4 End-to-end scenario

1. Initialize the RAG template.
2. Import and fingerprint the corpus and evaluation sets.
3. Run exploratory calibration on a small subset.
4. Freeze protocol revision 1.
5. Generate and review a 72-assignment screening study.
6. Execute; the planner builds shared chunk, enrichment, embedding, and index artifacts once per unique upstream configuration.
7. Inspect completeness, failures, and query-level diagnostics.
8. Author the focused assignment table and freeze study 2.
9. Execute balanced blocked replicates.
10. Freeze finalists and confirmatory analysis before unblinding holdout.
11. Execute study 3.
12. Run the recorded analysis environment.
13. Draft and review evidence.
14. Record the selection decision and reversal conditions.
15. Export a complete research crate.

---

## 17. Security and privacy

### 17.1 Clean execution environment

Workers receive a minimal environment. The default is deny-by-default, not inherited `os.Environ()`.

Explicitly pass:

- locale/timezone if required;
- declared non-secret configuration;
- secret handles;
- proxy/network configuration only when permitted;
- artifact and result paths.

### 17.2 Secrets

Secrets are references such as:

```yaml
secrets:
  - name: llm-provider-api
    version: vault://team/rag/provider-key#7
```

The value is delivered out of band. Logs and result manifests are scanned according to policy, but leak scanning is defense in depth rather than the primary containment mechanism.

### 17.3 Network capabilities

Each node declares:

- no network;
- allowlisted hosts;
- unrestricted network with waiver.

External calls record provider operation IDs and bounded request/response metadata.

### 17.4 Sensitive corpus data

Artifacts support classification, encryption, ACL, redacted exports, and retention. A public research crate can include manifests and synthetic fixtures while excluding protected source bytes.

### 17.5 Attestation and signatures

Optional later hardening:

- sign frozen protocol and study digests;
- sign runtime attestations;
- use in-toto/SLSA-style predicates for code/environment provenance;
- anchor study snapshots in an external immutable store.

The first release should be honest append-only software, not claim cryptographic immutability it does not provide.

---

## 18. Interoperability

### 18.1 W3C PROV mapping

Internal typed records map naturally:

- protocol, assignment table, and artifacts -> `prov:Entity`;
- run, step, and analysis -> `prov:Activity`;
- researcher, software, and executor -> `prov:Agent`;
- inputs -> `prov:used`;
- outputs -> `prov:wasGeneratedBy`;
- cache/materialization -> `prov:wasDerivedFrom`;
- protocol revision -> `prov:wasRevisionOf`;
- activity plan -> `prov:hadPlan`.

Use PROV as an interchange model, not the primary transactional schema.

### 18.2 Workflow Run RO-Crate

`researchctl pack` should emit a crate containing prospective and retrospective provenance:

- protocol and execution workflow;
- step tools;
- source code;
- software environments;
- input and output artifacts;
- step executions;
- intermediate outputs where policy permits;
- analysis, evidence, decision, and report objects;
- creators, licenses, and citations.

### 18.3 OpenLineage

An optional emitter can publish step/job/run/dataset events and custom research facets to existing lineage systems.

### 18.4 MLflow

Import/export can map cases and runs to MLflow experiments and runs, metrics to logged metrics, and artifacts to the artifact store. `researchctl` remains authoritative for frozen protocols, assignments, replicate semantics, and reviewed evidence.

### 18.5 Workflow engines

CWL is a useful portability target for command-line tools. Snakemake and Nextflow adapters can preserve their native environment, caching, cluster, and cloud execution strengths while emitting `researchctl` provenance.

---

## 19. Implementation architecture

### 19.1 Language split

- **Go core:** CLI, canonical identities, ledger, CAS, local executor, import/export, verification.
- **Python SDK/domain package:** ML-friendly authoring helpers, RAG compiler, reference workers, design and analysis integrations.
- **Language-neutral contracts:** JSON Schema, OpenAPI/JSON messages, artifact schemas.

Python is a convenience for scientists, not a dependency of the core data model.

### 19.2 Suggested repository boundaries

```text
researchctl/
  cmd/researchctl/
  pkg/canonical/
  pkg/identity/
  pkg/protocol/
  pkg/study/
  pkg/ledger/
  pkg/artifact/
  pkg/execution/
  pkg/provenance/
  pkg/export/
  adapters/executor/local/
  adapters/executor/process/
  adapters/executor/cwl/
  sdk/python/

researchctl-rag/
  schemas/
  compiler/
  workers/
  metrics/
  fixtures/
```

The RAG package may initially live in the same monorepo for development, but its dependency direction remains one-way: RAG depends on core contracts; core never imports RAG.

### 19.3 Core interfaces

```go
type ArtifactStore interface {
    Put(ctx context.Context, source PathOrReader, descriptor Descriptor) (Artifact, error)
    Open(ctx context.Context, digest Digest) (io.ReadCloser, error)
    Verify(ctx context.Context, digest Digest) error
    Materialize(ctx context.Context, digest Digest, destination string) error
}

type Ledger interface {
    CreateStudy(ctx context.Context, study Study) error
    AdmitAssignment(ctx context.Context, assignment Assignment) error
    StartRun(ctx context.Context, assignmentID ID) (Run, error)
    StartAttempt(ctx context.Context, runID ID, attestation RuntimeAttestation) (Attempt, error)
    RecordStepResult(ctx context.Context, result StepResult) error
    CloseRun(ctx context.Context, summary RunSummary) error
}

type Executor interface {
    Prepare(ctx context.Context, plan ExecutionPlan, attempt AttemptContext) (Prepared, error)
    Submit(ctx context.Context, prepared Prepared) (ExternalID, error)
    Inspect(ctx context.Context, id ExternalID) (ExecutionState, error)
    Cancel(ctx context.Context, id ExternalID, reason string) error
    Collect(ctx context.Context, id ExternalID) (ExecutionResult, error)
}
```

Actual boundaries should be expressed through versioned DTOs so adapters can be separate processes.

### 19.4 API discipline

- Every durable document has `schemaVersion` and `kind`.
- Major incompatible changes receive new schema URIs.
- Decoders reject unknown fields for frozen authoring contracts.
- Event consumers may allow additive fields according to version policy.
- Golden fixtures exist for every boundary.
- Canonical digests are test vectors across Go and Python.

### 19.5 Code to salvage from the prototype

After review and refactoring, likely candidates include:

- safe artifact path confinement;
- file and tree digest verification;
- strict run export validation;
- process cancellation and frame-shape tests;
- SQLite transaction patterns;
- run/attempt closure invariants;
- secret-canary test fixtures;
- deterministic ordering tests;
- CLI output utilities.

Do not copy blindly:

- the global `(specification_id, replicate_index)` run uniqueness rule;
- terminal-run resume logic;
- plan provenance hidden in attempt environment;
- generic JavaScript loaders;
- inline artifact frames;
- the general analysis reducer as the main analysis layer;
- claim graph as the execution source of truth;
- deferred plugin abstractions without a concrete first-party use.

### 19.6 Testing strategy

#### Identity tests

- cross-language JCS test vectors;
- factor order does not change case digest;
- code, environment, input, seed, and relevant hardware changes invalidate execution fingerprints;
- display text does not alter scientific identity.

#### State-machine tests

- failed run never fills assignment;
- cache hit creates a new step/run provenance occurrence;
- attempt retry does not create a replicate;
- replacement run links to failure and fills the same slot only on success;
- changed assignment table creates a new study.

#### Crash tests

Inject process death:

- before run creation;
- after run creation but before attempt;
- during output staging;
- after artifact upload but before ledger commit;
- after terminal result but before close;
- during cancellation.

Recovery must be idempotent and explainable.

#### Artifact tests

- traversal, symlink, hard-link, overwrite, and collision rejection;
- large-file streaming;
- tree manifest verification;
- corrupted remote object detection;
- tombstone behavior.

#### RAG vertical-slice tests

- two chunkers;
- lexical, vector, and hybrid retrieval;
- one local embedding fake and one bounded real-provider test;
- reranker on/off;
- answer and judge fakes;
- shared upstream reuse;
- query-level metric completeness;
- holdout access control.

#### Reproducibility acceptance

- same deterministic inputs and pinned environment produce matching artifacts;
- changed source or image digest cannot reuse exact cache;
- provider-dependent steps are labeled correctly;
- complete study export reproduces the execution graph and analysis inputs;
- no secret values appear in ledger, artifacts, errors, or export fixtures.

---

## 20. Delivery roadmap

### Milestone 0: contract freeze

Deliver:

- canonical identity rules;
- protocol/study/assignment/run/attempt schemas;
- artifact and result manifests;
- executor and domain-compiler contracts;
- cross-language test vectors;
- relational schema and migration policy.

No workbench, plugins, or generalized reports.

### Milestone 1: local reproducible kernel

Deliver:

- SQLite ledger;
- filesystem CAS;
- local process/container executor;
- clean environment and secret handles;
- run/attempt/step state machine;
- exact cache with correct occurrence provenance;
- inspect/follow/export commands.

Acceptance: a shell or Python multi-step workflow can be frozen, run, interrupted, resumed, verified, and exported.

### Milestone 2: RAG vertical slice

Deliver:

- RAG schemas and compiler;
- document, chunk, embed, index, retrieve, answer, evaluate workers;
- typed artifacts and observation sets;
- shared upstream materialization;
- one complete tutorial.

Acceptance: the concrete scenario can compare at least two chunkers and three retriever families without custom core code.

### Milestone 3: study design

Deliver:

- user-table, grid, random, and space-filling designs;
- assignment lock artifact;
- blocks, randomization, replacement, and exclusion;
- staged studies and holdout controls;
- adaptive ask/tell contract.

Acceptance: failed runs never count, randomized order is auditable, and a confirmatory stage is frozen before holdout access.

### Milestone 4: analysis and interpretation

Deliver:

- frozen study snapshots and tidy data export;
- recorded Python/R analysis runs;
- lightweight summarizer;
- evidence drafting/review;
- decision revisions;
- integrated report rendering.

Acceptance: every reported number traces to analysis code, environment, exact run set, and raw observation artifacts.

### Milestone 5: interoperability and remote execution

Deliver:

- Workflow Run RO-Crate export;
- W3C PROV export;
- OpenLineage emitter;
- one established workflow-engine adapter;
- remote object store.

### Milestone 6: shared service

Only after the local contracts stabilize:

- PostgreSQL backend;
- authentication and authorization;
- team review workflow;
- remote worker leases;
- UI for protocol review, study status, provenance, artifacts, and evidence.

The UI is a read/write client of the same contracts, not a second product model.

---

## 21. Product acceptance criteria

The clean first major version is successful when a new ML scientist can:

1. initialize a RAG study without learning Go, JavaScript runtimes, or a custom analysis language;
2. describe a protocol in reviewable YAML or generate it with Python;
3. freeze an assignment table with explicit factors, blocks, randomization, and outcomes;
4. run ordinary Python tools locally in pinned environments;
5. reuse expensive chunking, embedding, and index artifacts without confusing cache reuse with scientific replication;
6. inspect every run, attempt, step, artifact, and failure;
7. distinguish operational retries from scientific replicates;
8. analyze query-level data with ordinary Python or R while preserving run-level sampling structure;
9. review evidence and record a decision;
10. export a complete, interoperable research object.

The architecture should reject these anti-goals:

- no new general workflow language in v1;
- no JavaScript as the universal authoring substrate;
- no general statistical DSL;
- no generic claim graph as the execution database;
- no implicit environment inheritance;
- no cache hit masquerading as a prior run belonging to a new study;
- no failed run satisfying a replicate slot;
- no artifact bytes embedded in lifecycle messages;
- no plugin framework before stable compiler/executor contracts;
- no workbench-first development.

---

## 22. Final recommendation

Build the new system around one sentence:

> **A protocol freezes what the scientist intends; a study freezes what will be assigned; an executor records what happened; artifacts preserve what was produced; analysis derives results; humans review evidence and make decisions.**

For the RAG scenario, this produces a system that is both rigorous and practical. It can represent thousands of possible phase combinations without executing a naïve grid, share upstream computation without corrupting replication semantics, capture hosted-model uncertainty honestly, and preserve a complete chain from corpus snapshot through chunking, enrichment, indexing, retrieval, answer generation, evaluation, analysis, evidence, and final decision.

That is a much narrower product than the prototype attempted. It is also a substantially stronger one.

---

## References and standards informing the design

- W3C PROV-O: https://www.w3.org/TR/prov-o/
- Workflow Run RO-Crate / Provenance Run Crate: https://www.researchobject.org/workflow-run-crate/profiles/provenance_run_crate/
- Common Workflow Language: https://www.commonwl.org/
- Nextflow caching and resuming: https://docs.seqera.io/nextflow/cache-and-resume
- Snakemake distribution and reproducibility: https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html
- Portable Encapsulated Projects: https://pep.databio.org/
- OpenLineage specification: https://openlineage.io/docs/spec/
- OCI Image Specification: https://github.com/opencontainers/image-spec
- RFC 8785 JSON Canonicalization Scheme: https://www.rfc-editor.org/rfc/rfc8785.html
- SLSA provenance: https://slsa.dev/spec/v1.2/provenance
- MLflow Tracking: https://mlflow.org/docs/latest/ml/tracking/
- NIST Engineering Statistics Handbook, experimental design: https://www.itl.nist.gov/div898/handbook/pri/pri.htm
- Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks: https://papers.nips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html
- Thakur et al., BEIR: https://arxiv.org/abs/2104.08663
- Es et al., RAGAS: https://arxiv.org/abs/2309.15217
- Ru et al., RAGChecker: https://arxiv.org/abs/2408.08067
- Hurlbert, Pseudoreplication and the Design of Ecological Field Experiments: https://doi.org/10.2307/1942661
