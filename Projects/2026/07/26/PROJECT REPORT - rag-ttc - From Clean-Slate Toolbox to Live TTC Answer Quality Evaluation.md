---
title: "rag-ttc: From Clean-Slate Toolbox to Live TTC Answer-Quality Evaluation"
aliases:
  - rag-ttc live evaluation project report
  - RAG-TTC-LIVE-E2E-001 deep dive
  - TTC answer quality experiment implementation report
tags:
  - project-report
  - rag
  - ttc
  - go
  - evaluation
  - retrieval
  - llm
  - caching
  - reproducibility
status: active
type: project-report
created: 2026-07-26
repo: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/rag-ttc
source_tickets:
  - RAG-TTC-CLEAN-SLATE-001
  - RAG-TTC-BACKENDS-001
  - RAG-TTC-LIVE-E2E-001
---

# rag-ttc: From Clean-Slate Toolbox to Live TTC Answer-Quality Evaluation

`rag-ttc` began as a deliberate reduction in scope. The preceding TTC RAG
evaluation environment had accumulated a RAG DSL, JavaScript authoring,
workflow lowering, Scraper Workflow V3 execution, Researchctl experiment
custody, database-backed lifecycle state, and several layers of reporting.
Those systems contained useful implementations and operational lessons, but
their combined control plane had become larger than the retrieval questions
being investigated. The replacement made experiments ordinary Go programs and
retained only the shared capabilities needed to run them safely.

This report describes the complete engineering sequence from that clean-slate
decision through persistent search backends, Geppetto provider integration,
real TTC retrieval measurements, recoverable provider execution, a fixed
answer-quality protocol, an authorized OpenAI smoke experiment, and the first
30-query paired pilot. It also records the exact boundary at which work
stopped: provider execution succeeded, but independent zero-budget replay
revealed an identity instability that must be resolved before human review
files are distributed.

The earlier architectural baseline remains in [[PROJECT REPORT - rag-ttc - Clean-Slate RAG Experiments in Plain Go]]. The repository-oriented technical
reference is [[ARTICLE - rag-ttc - Architecture of a Reproducible Go RAG Evaluation System]]. Both are indexed by [[rag-ttc]] and related to the
historical [[rag-evaluation-system]].

> [!summary]
> - The project replaced a multi-layer workflow platform with typed Go
>   capabilities, explicit Glazed experiment commands, and filesystem run
>   directories.
> - It added persistent Bleve BM25, SQLite FTS5, and SQLite exact-vector
>   backends; Geppetto generation, embedding, and reranking adapters; and
>   Pinocchio-compatible profile loading without direct environment access.
> - Provider work is bounded by workers, rates, stage budgets, conservative
>   cost preflight, and per-item caches that preserve completed work after a
>   late failure.
> - A five-query OpenAI smoke completed ten answer cells and replayed with zero
>   provider work. The 30-query pilot completed 60 answer cells within the
>   approved budget, but a later independent replay exposed unstable semantic
>   identity. Human review has therefore not begun.

## 1. The initial reset

The original design problem was not a lack of features. It was that changing a
retrieval hypothesis could require reasoning across several representations:

```text
JavaScript experiment
  -> RAG DSL
  -> canonical workflow representation
  -> lowering and validation
  -> durable workflow operations
  -> Researchctl case and attempt state
  -> projected observations
  -> analysis specification
  -> publication
```

The new repository adopted a different rule:

```text
share stable RAG operations and execution safety;
keep experiment control flow in the experiment program.
```

This rule produced three boundaries.

1. `pkg/rag` owns domain values and focused capabilities.
2. `pkg/rag/execution` owns reusable control of expensive work.
3. `pkg/experiment` owns run-directory custody and terminal state.

The experiment itself remains Go code. It chooses which representations to
create, which indexes to query, which arms to compare, which metrics to
calculate, and which artifacts to write. No generic pipeline graph owns that
sequence.

The foundation landed in `800ad75` and its documentation in `77747a8`. Six
offline examples proved chunking, lexical retrieval, hybrid evaluation,
controlled execution, cache recovery, and complete experiment-directory
creation. At this point the system was structurally useful but still relied on
deterministic synthetic data and local substitute providers.

## 2. The first toolbox

The initial toolbox defined serializable records for documents, chunks,
representations, vectors, queries, judgments, hits, fused hits, evidence,
provider requests, provider results, and usage. Narrow interfaces made each
provider or backend replaceable without introducing a service registry:

```go
type Embedder interface {
    Embed(context.Context, EmbeddingRequest) (EmbeddingResult, error)
}

type Searcher interface {
    Search(context.Context, Query, int) ([]Hit, error)
}

type Generator interface {
    Generate(context.Context, GenerationRequest) (GenerationResult, error)
}

type Reranker interface {
    Rerank(context.Context, RerankRequest) (RerankResult, error)
}
```

The source-preserving chunk model was central. A chunk retained its document
ID, ordinal, byte range, text digest, and chunker identity. Search operated on
representations, while citations and answer generation returned to source
chunks. This prevented a generated summary or hypothetical question from
being treated as authoritative evidence.

The first local implementations were intentionally deterministic:

- an in-memory BM25 index;
- a signed hashing embedder;
- exact in-memory cosine search;
- weighted reciprocal-rank fusion;
- term-overlap reranking;
- an extractive generator;
- MRR, recall, precision, hit rate, and nDCG;
- Markdown and CSV report renderers.

These implementations established contracts and test oracles. They were not
presented as production-quality retrieval providers.

## 3. Execution control became a first-class package

Provider work has three independent constraints:

- concurrency limits simultaneous work;
- rate limiting controls admission over time;
- budgets cap total authorized work.

`pkg/rag/execution` represented these constraints independently and composed
them through a limiter chain. Every worker accepted a context, and goroutine
coordination used `errgroup`. Ordered maps preserved input order even when
work completed out of order.

The cache algorithm resolves hits before requesting limiter admission:

```text
for every input:
    derive semantic cache key
    load cache entry

group remaining misses
acquire budget and rate admission only for misses
execute bounded provider work

for every successful result:
    atomically store the individual item
    mark the item recoverable
```

This ordering matters. A zero-budget replay must be able to read completed
work. If the budget were charged before cache lookup, replay would fail even
though no provider operation was necessary.

Batch embedding received a separate implementation. It batches unique misses
for provider efficiency but stores each result under an individual key before
continuing. If item 1,999 of 2,000 fails, the previous 1,998 results remain
recoverable. Duplicate keys execute once and are copied back into all
corresponding input positions.

Later work added `work_calls` to cache reports. Hits, misses, writes, budget
items, and provider invocations are distinct quantities. A batch of 100
embedding items consumes 100 budget items but represents one adapter work call.
The counter increments immediately before invoking the work callback and
survives provider or cache-store failure.

## 4. Run directories replaced experiment lifecycle services

`pkg/experiment` creates one self-contained directory per execution:

```text
<run-root>/<timestamp>-<name>-<suffix>/
├── config.json
├── manifest.json
├── status.json
├── inputs/
├── preparation/
├── observations/
├── results/
└── summary.md
```

The directory records configuration, copied input digests, prepared chunks and
vectors, append-only observations, per-query results, aggregate reports, and a
terminal status. A failed directory remains useful because it retains every
artifact written before failure. A completed terminal state acts as the
experiment commit marker.

This design deliberately separates custody from scheduling. The run package
does not know about RAG stages or provider concurrency. It records what the
experiment program writes.

## 5. Persistent and provider-backed components

The next ticket studied the earlier RAG evaluation system and extracted useful
backend patterns without importing its workflow architecture. Three persistent
search implementations were added:

| Backend | Storage | Query behavior | Primary role |
| --- | --- | --- | --- |
| Bleve BM25 | Bleve directory | boosted title/body lexical search | persistent production lexical baseline |
| SQLite FTS5 | SQLite database | native FTS5 lexical ranking | compact inspectable lexical alternative |
| SQLite exact vector | SQLite vectors + Go scan | exact cosine top-k | persistent semantic oracle |

Persistent builders publish atomically. They create a temporary index beside
the target, fully populate and validate it, close it, and rename it into place.
They do not overwrite an existing destination silently. Manifests record
backend type, version, representation count, model identity, dimensions, and
retrieval configuration where applicable.

Geppetto adapters connected the generic interfaces to real generation,
embedding, and reranking providers. The embedding adapter validates:

- requested model agreement;
- non-empty input batches;
- result count equal to input count;
- expected dimensions;
- finite vector values.

Generation translates the generic request into Geppetto inference settings and
returns text, finish reason, citations, and available usage. Reranking performs
the equivalent translation for candidate evidence.

Provider configuration follows Pinocchio and Geppetto profiles. Glazed command
sections accept registry paths and a profile selection. The CLI resolves a
composite provider bundle once, exposes only non-secret metadata, and owns
cleanup. No experiment command reads credentials through `os.Getenv`.

The repository setup added `glazed-lint`, pinned lint dependencies, logcopter
generation checks, unit and smoke tests, security checks, and GitHub Actions.
Review and CI remediation produced the merged baseline in pull request 1.

## 6. The real TTC retrieval baseline

The repository imported a canonical candidate dataset:

- 200 TTC corpus documents;
- 1,982 raw chunk representations under the selected chunk plan;
- an evaluation dataset containing judged queries and explicit target IDs.

The backend bakeoff command exercised persistent lexical and vector paths
against this data. It measured each retrieval arm rather than inferring quality
from successful index construction.

The result established several practical facts:

- BM25 was a meaningful baseline for TTC policy, catalog, and care questions.
- Vector retrieval required real provider embeddings and explicit query
  embedding budgets.
- RRF could be evaluated only after both channels preserved compatible target
  identities.
- Per-query results were necessary because aggregate metrics concealed
  category-specific failures.

Query embedding was then moved under the same cache and budget controls as
corpus embedding. This closed a cost-control gap: an experiment with a cached
corpus could still make an unbounded number of query embedding calls unless
the query path was independently metered.

## 7. The answer-quality experiment was designed before execution

Retrieval metrics do not measure the final answer. The next ticket introduced
one Glazed command:

```text
rag-ttc experiments answer-quality run
```

The command fixes the experiment surface rather than accepting a generic
pipeline description. Its configuration includes:

- corpus and evaluation paths;
- exact query IDs or a split;
- retrieval arms;
- chunk and context limits;
- retrieval and evidence cutoffs;
- provider profile registries and profile;
- worker counts;
- per-stage budgets;
- conservative unit prices and a USD ceiling;
- an optional annotation file.

The execution arms are explicit:

- BM25;
- vector;
- RRF over BM25 and vector;
- RRF followed by provider reranking when configured.

Every arm receives the same query set. RRF collapses representation duplicates,
fuses ranks, and hydrates source evidence. The reranked arm uses the same RRF
candidate population before applying a provider reranker.

### 7.1 Budget preflight

Before provider resolution performs paid work, the command calculates cold
ceilings:

```text
embedding items = representation count + query count
generation calls = query count × enabled answer arms
reranking calls = query count × enabled reranked arms
```

It rejects insufficient budgets unless the operator explicitly enables a
partial warm-cache run. It multiplies ceilings by operator-supplied unit prices
and rejects a value above `--max-estimated-usd`. Missing prices require a
separate explicit override.

Budgets are still enforced at runtime. Preflight is an authorization check, not
a substitute for admission control.

### 7.2 Grounded generation contract

The answer prompt and JSON schema are versioned files. The model receives only
the query and packed source evidence. Its result must contain:

```json
{
  "answer": "text",
  "citation_chunk_ids": ["chunk-id"],
  "abstained": false
}
```

Parsing disallows unknown fields and trailing objects. Contract validation
requires:

- a non-empty answer when not abstaining;
- at least one citation when not abstaining;
- no citations when abstaining;
- every citation to occur in the supplied evidence;
- no duplicate citation IDs.

Invalid output is converted to a safe abstention and classified as a parse or
contract failure. The raw generation is retained for inspection.

### 7.3 Blinded human review

Each answer produces two artifacts:

- `review-queue.jsonl` contains review ID, query, evidence, and answer;
- `review-key.json` privately maps review ID to query ID and arm.

The reviewer scores correctness, groundedness, completeness, citation
correctness, and appropriate abstention. Arm comparison uses only queries with
complete paired reviews. A later extension records reviewer overlap,
per-dimension exact agreement, mean absolute differences, maximum differences,
and item-level disagreement.

The pilot predeclared 60 primary annotations and ten balanced second reviews.
No parameter tuning may use the pilot and then report the same pilot as
confirmatory evidence.

## 8. Validation before live providers

The implementation proceeded through explicit phases:

1. Glazed command and typed settings.
2. Composite provider resolution.
3. Cached generation and reranking.
4. Stage budgets and cost preflight.
5. Fixed retrieval alternatives.
6. Grounded-answer parsing and contract validation.
7. Blinded human-review reports.
8. Late-failure recovery, zero-budget replay, sample command execution, build,
   race, lint, and schema checks.

The tests covered corrupted cache entries, duplicate inputs, callback errors,
provider errors, store failures, result-count mismatches, budget exhaustion,
missing pricing, incomplete judgments, deterministic artifact ordering, and
annotation validation.

The canonical TTC data was then imported and a five-query smoke was frozen. The
operator boundary documented exactly which corpus text, query text, retrieved
evidence, providers, model names, call limits, and USD ceiling would leave the
machine.

## 9. The five-query OpenAI smoke

The authorized smoke used:

- OpenAI `text-embedding-3-small`, 1,536 dimensions;
- OpenAI Responses `gpt-5-nano`;
- BM25 and RRF;
- no reranker;
- five fixed queries;
- at most 1,987 embedding items and ten generations;
- a `$0.05` command ceiling.

The live directory was:

```text
sources/live-smoke/runs/
  20260726T171137.818510209Z-answer-quality-f8154e0c3e29
```

All ten answer cells completed. The embedding budget spent exactly 1,987 items:
1,982 corpus representations plus five queries. Generation spent ten calls.
Generation reported 14,143 input and 4,978 output tokens. Embedding token usage
and provider-authoritative USD cost were unavailable, so the report retained
the conservative ceiling rather than presenting a partial actual price.

Every answer was manually inspected. Four answerable query pairs were grounded;
the negative blueberry query safely abstained in both arms. The inspection
recorded two minor content concerns: compressed planting-timing language and
asymmetric evidence in a catalog comparison.

The replay used zero budgets for every provider stage. It recovered:

- 1,982 corpus embeddings;
- five query embeddings;
- ten generations.

It made no provider work calls and produced the same semantic answers. This
validated the intended failure-recovery path at smoke scale.

## 10. Freezing the 30-query pilot

The Phase 10 selection was frozen before provider execution in
`phase10-pilot-v1.json`, with SHA-256:

```text
db3636b2bb8bcbdb48f95d083eb468e3cb1183917e2fa162b058695c8dcbc10b
```

Thirty judged queries were selected across five categories, six per category:

- commerce and support;
- planting procedures;
- care and diagnosis;
- selection, site, and zone;
- catalog comparison.

The queries excluded the smoke population and used a category-round-robin
execution order. The experiment retained BM25 and RRF, the same corpus,
evaluation set, chunking, prompt, schema, provider profile, models, cutoffs,
and context policy.

The proposed warm-cache authorization was:

- 30 query embedding items;
- 60 generation calls;
- zero reranking calls;
- `$0.06030` expected warm-cache estimate;
- `$0.08012` static cold preflight estimate;
- `$0.10` maximum command ceiling.

A deliberately impossible `$0.000001` ceiling was tested first. Preflight
rejected `$0.080120` and created no run directory.

## 11. The 30-query live pilot

After explicit approval, the command executed the frozen population. The live
directory was:

```text
sources/phase10/runs/
  20260726T174305.486090890Z-answer-quality-1835fc62a319
```

Both arms completed:

| Arm | Queries | Completed | Execution failures |
| --- | ---: | ---: | ---: |
| BM25 | 30 | 30 | 0 |
| RRF | 30 | 30 | 0 |

Provider and cache evidence was:

| Stage | Hits | Misses | Writes | Work calls |
| --- | ---: | ---: | ---: | ---: |
| Corpus embedding | 1,982 | 0 | 0 | 0 |
| Query embedding | 0 | 30 | 30 | 30 |
| Generation | 0 | 60 | 60 | 60 |
| Reranking | 0 | 0 | 0 | 0 |

Generation reported 89,543 input and 30,702 output tokens. The live run stayed
below the approved ceiling and produced 60 queue records and 60 private key
records.

The strict output contract classified 50 cells as valid:

| Arm | Total | Valid | Parse failures | Contract failures | Safe abstentions |
| --- | ---: | ---: | ---: | ---: | ---: |
| BM25 | 30 | 25 | 1 | 4 | 13 |
| RRF | 30 | 25 | 0 | 5 | 7 |

These invalid cells were not deleted. They are part of answer quality and
should remain in the blinded review population once identity is stable.

## 12. The replay finding

The first zero-budget replay recovered all provider-derived work:

- 1,982 corpus embedding hits;
- 30 query embedding hits;
- 60 generation hits;
- zero misses, writes, work calls, or budget spending.

All 60 parsed answers and raw generation texts matched. One review ID differed.
Artifact comparison found that the corresponding BM25 context contained the
same ordered chunks and ranks, but one floating retrieval score differed at the
last representable digits:

```text
1.996638799554313
1.9966387995543127
```

The initial diagnosis was that review identity should not include floating
retrieval and reranker scores when the evidence content, order, answer, and
policy are unchanged. A local, uncommitted change projected review identity
onto chunk content and rank while excluding scores. Focused and race tests
passed.

Two further independent zero-budget replays were then attempted. The first
completed. The second reported a generation cache miss and correctly failed
because its generation budget was zero. This proves that the reproducibility
problem is broader than the first review-ID symptom. The current artifacts do
not yet prove whether the later miss came from changed evidence membership,
ordering, another semantic key input, or an upstream nondeterministic
retrieval path. `GenerationCacheKeyInput` itself uses ordered chunk IDs and
content digests rather than scores, so the exact root cause requires a coherent
identity audit rather than another isolated patch.

The correct decision was to stop reviewer distribution. If reviewers annotate
IDs that a later import run cannot reproduce, the annotation file becomes
unusable or requires an unsafe translation layer.

## 13. Current repository state

The committed implementation through `a1add8d` contains:

- the typed RAG toolbox and run ledger;
- persistent search backends;
- Geppetto adapters and profile-backed Glazed commands;
- real TTC corpus and evaluation loaders;
- the backend bakeoff;
- the answer-quality experiment;
- provider caches, budgets, rates, cost guards, and work-call evidence;
- strict grounded-answer contracts;
- blinded review and disagreement aggregation;
- frozen smoke and pilot runbooks;
- live smoke evidence.

The working tree additionally contains:

- the uncommitted score-insensitive review-ID change and test;
- Step 19 diary and task updates;
- ignored or untracked Phase 10 live and replay artifacts;
- the populated provider cache.

Those changes should not be folded into the committed architecture until the
generation identity failure is understood.

## 14. What the work established

Several results are now supported by execution evidence.

- The clean-slate Go architecture can run a realistic TTC corpus through real
  embeddings, persistent retrieval, answer generation, measurement, and
  artifact custody.
- Provider work can resume from completed items. Both the smoke and the first
  pilot replay avoided repeat provider calls.
- Static cost preflight, runtime budgets, and cache-first admission constrain
  different risks and are all necessary.
- Successful HTTP/provider execution is not equivalent to a valid answer. Ten
  of 60 pilot cells failed the local structured-answer contract despite zero
  provider errors.
- Review blinding requires stable semantic identity. A deterministic-looking
  hash is not sufficient if its input contains nondeterministic material.
- Aggregate retrieval metrics, contract metrics, human-answer metrics,
  reviewer agreement, latency, usage, and cache behavior are separate
  measurement layers.

## 15. Required next step

The next task is an identity design pass, not another paid experiment.

The audit should enumerate every field used by:

- corpus embedding keys;
- query embedding keys;
- generation keys;
- reranking keys;
- review IDs;
- run configuration digests.

It should then define one canonical selected-evidence identity. A candidate is:

```text
selected evidence identity =
  context policy version
  + context limits
  + ordered [
      rank
      chunk ID
      chunk content digest
    ]
```

Retrieval scores remain observations. They should enter identity only if a
score change can affect the provider request or reviewer-visible material. If
scores are displayed to reviewers or serialized into prompts, they must be
normalized under an explicit versioned rule or removed from that surface.

Acceptance requires at least two independent zero-budget runs that produce:

- zero provider work calls;
- identical selected chunk membership and order;
- identical semantic answers;
- identical review IDs;
- identical queue and key semantic digests.

Only after that evidence exists should the 60-cell primary queue and balanced
ten-cell secondary queue be distributed.

## 16. Commit map

The following commits mark the major implementation stages:

| Commit | Result |
| --- | --- |
| `800ad75` | Clean-slate toolbox, execution primitives, run ledger, examples |
| `ba08bc1` | Profile-backed persistent search backends |
| `661220e` | Real TTC backend quality measurement |
| `ae72aec` | Cached and budgeted query embeddings |
| `e8eeec5` | Merged backend and provider baseline |
| `cf6b2c0` | Answer-quality Glazed command |
| `1673f64` | Composite Geppetto provider resolution |
| `b57981c` | Cached generation and reranking |
| `2b360a7` | Stage budgets and cost preflight |
| `ccdc6e0` | Fixed retrieval arms |
| `057f95d` | Grounded-answer safety contract |
| `1c8aad3` | Blinded human-review reports |
| `64d6074` | Late-provider recovery tests |
| `2ef26ab` | Canonical TTC candidate dataset |
| `0e5d45e` | Per-item recoverable batch caching |
| `8f60e01` | Five-query live smoke evidence |
| `7865e2a` | Frozen 30-query pilot selection |
| `3a8b705` | Provider adapter work-call reporting |
| `6cac376` | Reviewer disagreement reporting |
| `a1add8d` | Frozen Phase 10 operator runbook |

## 17. Reading guide

- [[PROJECT REPORT - rag-ttc - Clean-Slate RAG Experiments in Plain Go]]
  explains the original reduction and first toolbox.
- [[ARTICLE - rag-ttc - Architecture of a Reproducible Go RAG Evaluation System]]
  describes the present repository without implementation history.
- [[ARTICLE - RAG Evaluation System - Search Retrieval Foundation Deep Dive]]
  covers the historical search foundation.
- [[ARTICLE - RAG Evaluation - Building and Validating an Initial Fixed-Truth Dataset]]
  explains TTC judgment construction and dataset integrity.
- [[rag-ttc]] is the current project map.
- [[rag-evaluation-system]] indexes the predecessor and related retrieval work.
