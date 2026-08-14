---
title: Ragkit as a Building Block — Reproducible Research to Production
aliases:
  - Ragkit building blocks study
  - Ragkit reuse kernel analysis
  - Content-addressed RAG kernel from bench to serving
status: active
type: architecture-pattern-study
created: 2026-08-14
analyzed: 2026-08-14
repository: /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/ragkit
repository_remote: git@github.com:go-go-golems/ragkit.git
repository_commit: 988679f54125398d2bc1f3e72497eb7472a0ebc2
repository_commit_date: 2026-08-13T16:05:00-04:00
repository_commit_subject: "feat(indexbundle): require explicit verifier scratch directory"
repository_branch: task/deploy-dev-indexer
repository_worktree: clean
go_module: github.com/go-go-golems/ragkit
tags:
  - architecture-garden
  - ragkit
  - rag
  - reproducible-research
  - content-addressing
  - production-hardening
  - flowkit
  - building-blocks
related_files:
  - rag/types.go
  - rag/components.go
  - rag/evidence_identity.go
  - rag/indexbundle/identity.go
  - rag/indexbundle/types.go
  - rag/indexbundle/staging_kernel.go
  - rag/indexbundle/build_stream.go
  - rag/indexbundle/preflight.go
  - rag/indexbundle/verification_relation.go
  - rag/generation/flow_step.go
  - rag/generation/flow_adapters.go
  - rag/reranking/cached.go
  - rag/flowpolicy/classifier.go
  - rag/provider/geppetto/embedding.go
  - boundary_test.go
related_notes:
  - "[[Research/Software Architecture Garden/ragkit/README|Architecture Garden — Ragkit]]"
  - "[[Research/Software Architecture Garden/ragopt/README|Ragopt]]"
  - "[[Research/Software Architecture Garden/coinvault/README|CoinVault]]"
  - "[[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]]"
  - "[[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]]"
---

# Ragkit as a Building Block — Reproducible Research to Production

The existing [[Research/Software Architecture Garden/ragkit/README|Ragkit Garden entry]] analyzed the library's authority discipline at commit `c4a2366` (2026-08-09): who owns source text, what a derived representation may influence, and why hydration rebinds evidence to caller-installed chunks. This study asks a different question at a snapshot four days and thirty-eight commits later: **what kind of building block is ragkit** — for a researcher who needs experiments to replay exactly, for a team assembling a new RAG application, and for an operator running retrieval in production? The interval between the two snapshots is unusually informative, because it contains three deliberate boundary moves: the generic execution engine was extracted *out* into flowkit under an explicit identity-stability law, provider adapters were let *in* under a quarantined import boundary, and the index-bundle subsystem acquired a memory-bounded, fail-closed build and verification path driven by a real out-of-memory incident in its largest consumer.

The one-sentence answer this document defends: ragkit is a **content-addressed retrieval kernel** — a small set of typed values, laws, and verified materializations — that deliberately exports identity and custody while refusing to own policy, authorization, run custody, or promotion; its consumers demonstrate two distinct reuse styles, and its recent history shows the kernel hardening exactly along the axis production contact demanded.

> [!summary]
> - Ragkit's reuse surface is three layers: core types and validators (`rag`), engines and materializations (chunking, lexical, vector, content, indexbundle), and decorators/adapters (cached embedder/reranker/generation, flowkit steps, Geppetto provider adapters). Applications implement five narrow interfaces — `Chunker`, `Embedder`, `Generator`, `Reranker`, `Searcher` — and reuse everything else.
> - Since the prior Garden study, the flow/execution engine moved to flowkit under a written law — "wiring may change, identity may not" — and the generation flow step reproduces the legacy cache key byte-for-byte, so populations cached before the extraction replay after it.
> - The reproducibility spine is an identity ladder: document content digest → chunk digest → representation digest → per-backend content digests → a 16-hex bundle ID computed over a schema-versioned identity structure. A bundle pins retrieval materialization exactly; it does not pin provider behavior, and the cache-key completeness obligation from the prior study still stands.
> - The production arc is concrete: a SQLite staging kernel admits input in bounded validated batches through a phase state machine, seals identity by streaming digests, and `BuildStream` publishes atomically with per-stage cross-checks; verification runs through a bounded scratch relation whose directory is required and preflighted by exercising the real write path, not by checking writability.
> - Two consumer styles exist in this workspace: rag-ttc consumes the full service stack (answering, dataset, evaluation, flow), while CoinVault consumes the kernel (indexbundle, retrieval, reranking, representations) and builds its own evidence ledger, authorization, and fusion policy on top. Both styles are intended; the boundary between them is where product authority begins.
> - The workspace itself records a live migration hazard: ragkit HEAD no longer contains `ragkit/flow` and `ragkit/execution`, but rag-ttc in the same `go.work` still imports them, so rag-ttc does not compile against workspace ragkit. Version skew across a shared workspace is a real operational failure mode of library extraction.

## Snapshot identity and evidence

| Field | Value |
|---|---|
| Repository | `/home/manuel/workspaces/2026-08-12/deploy-dev-indexer/ragkit` |
| Remote | `git@github.com:go-go-golems/ragkit.git` |
| Branch | `task/deploy-dev-indexer` |
| Commit | `988679f54125398d2bc1f3e72497eb7472a0ebc2` (2026-08-13, "feat(indexbundle): require explicit verifier scratch directory") |
| Worktree | Clean |
| Prior study baseline | `c4a2366` (2026-08-09); 38 commits between the snapshots |
| Analysis date | 2026-08-14 |
| Consumers examined | `coinvault/` and `rag-ttc/` sibling checkouts in the same workspace only |

Consumer resolution needs one paragraph of care, because three coordinates disagree. CoinVault's `go.mod` pins `ragkit v0.1.2` and rag-ttc's pins `v0.1.7`, but the workspace `go.work` includes `./ragkit`, so builds inside this workspace resolve both consumers against ragkit HEAD. CoinVault compiles and runs against HEAD — its production code calls `indexbundle.BuildStream` and passes the scratch directories HEAD requires (`coinvault/internal/knowledgebuild/build.go:507-524`, `coinvault/internal/knowledge/service.go:104-126`). rag-ttc does **not** compile against HEAD: it still imports `ragkit/flow` in at least seven files and `ragkit/execution` in eighteen, packages that no longer exist after the flowkit extraction; a direct probe (`go build ./rag-ttc/cmd/rag-ttc/cmds/experiments/chunkcompare/`) fails with "no required module provides package github.com/go-go-golems/ragkit/flow". Claims below about rag-ttc's consumption therefore describe its pinned-version usage pattern, not a working HEAD integration.

Validation performed for this study, from the pinned ragkit root:

```text
GOWORK=off go build ./...          # pass
GOWORK=off go test ./... -count=1  # all 27 packages ok (indexbundle 1.196s the longest)
```

These are local deterministic checks, not live-provider or deployment evidence. No source repository was modified.

## 1. What kind of building block this is

A library earns the name "building block" by what it makes unnecessary, and by what it refuses to decide for you. Ragkit's surface sorts cleanly into three layers, and the sorting is enforced rather than aspirational.

**Layer 1 — values and laws.** `rag/types.go` defines the domain algebra: `Document`, half-open `Range`, `Chunk`, `Representation`, `Vector`, `Query`, `Judgment`, `EvaluationSet`, `Hit`, `Contribution`, `FusedHit`, `Evidence`, `Usage` (`rag/types.go:3-119`). The comments are contracts, not decoration: a representation "is retrieval material, not source evidence" (`rag/types.go:30-32`), and `Usage` uses pointer fields because "pointers distinguish missing values from values explicitly reported as zero" (`rag/types.go:110-112`). Validators (`rag/validate.go`) and the score-independent `EvidenceIdentity` projection (`rag/evidence_identity.go:14-41`) — which recomputes each chunk's content digest and rejects a stored digest that disagrees with the text — make the laws checkable at every boundary that admits data.

**Layer 2 — engines and materializations.** Chunkers (fixed, markdown, markdown-heading, plus Go-source chunking in `rag/gochunk`), the BM25 and Bleve lexical indexes, exact and SQLite-exact and deterministic-HNSW vector indexes, the SQLite content store, retrieval collapse/fusion/filtering, evaluation metrics with target-level coherence, and — the largest single subsystem — `indexbundle`, which turns a validated corpus-plus-derivations into an immutable, digest-named, self-verifying directory.

**Layer 3 — decorators and adapters.** Cached embedder and reranker decorators keyed on semantic identity, generation caching and its flowkit step/batcher adapters, the ragkit-owned retry-classification policy, and — new since the prior study — Geppetto provider adapters under `rag/provider/geppetto`.

The layering is enforced by the boundary guard, which changed meaningfully between the snapshots. The prior study recorded a flat prohibition: no Geppetto, Pinocchio, Glazed, Cobra, or Bubble Tea anywhere in compile dependencies. The current test carves a single sanctioned opening: "Provider adapters under rag/provider/... are the only place LLM-framework dependencies are allowed; CLI frameworks are never allowed because ragkit is a library" (`boundary_test.go:9-20`), and the test walks `go list -deps` for every non-adapter package to prove the core stays clean (`boundary_test.go:22-48`). This is the structural-guard genre the Garden first catalogued in go-go-datadrop, applied to dependency direction: the rule that keeps the kernel provider-neutral is a test, so it cannot rot into a convention.

What the kernel refuses to own is as load-bearing as what it provides. There is no run directory, no experiment custody, no gate, no authorization, no HTTP surface, no release pipeline. The prior study established those refusals; this snapshot confirms every one of them still holds, and the consumers below show why the refusals are the reuse story rather than gaps in it.

## 2. The two boundary moves

### 2.1 Extraction outward: flowkit, under an identity-stability law

Commit `01ddff5` ("Consume extracted Flowkit module") removed ragkit's own `flow/` and `execution/` packages — the cache-first, policy-separated work engine the prior study analyzed in detail — and replaced them with a dependency on `flowkit v0.1.0`. What makes this extraction Garden-worthy is not the move but the law that governed it, written directly above the adapter:

> "Its identity reproduces the generation cache key EXACTLY — same "generation"/"v1" keyspace, same GenerationCacheKeyInput bytes, same GenerationCacheEnvelope value — so a flow run replays every entry the GenerateCached era stored and vice versa (RAG-TTC-FLOW-001 DR-3: wiring may change, identity may not). The adapter lives here, not in pkg/flow: flow stays generic, the domain adapts itself to it." (`rag/generation/flow_step.go:14-20`)

Two distinct rules are packed in there. First, **cache identity survives engine replacement**: a research population cached under the old in-tree engine replays byte-identically under the extracted one, because the key bytes and envelope type are frozen even though every line of wiring changed. This is the same discipline CoinVault's judge applies with `judgePromptVersion` — the instrument may be rebuilt, but its population key may not drift silently — and it is the strongest concrete instance yet of the [[Research/Software Architecture Garden/Research/evaluation-loops/README|evaluation-loops research family's]] frozen-instrument law applied to a *library refactoring* rather than a measurement campaign. Second, **the domain adapts to the generic engine, never the reverse**: flowkit knows nothing about generation requests; ragkit supplies `Identity`, `Policy`, `Do`, and `AttemptMeter` (`rag/generation/flow_step.go:48-69`).

Usage custody crosses the same boundary with its own rule: replayed results have their usage zeroed, "because cached usage was spent by whichever run stored the entry, not this one" (`rag/generation/flow_step.go:72-82`); fresh spend travels as flow meters and converts back losslessly, with absent fields staying absent rather than becoming zeros (`UsageMeters` at `flow_step.go:86-107`, `UsageFromMeters` at `flow_adapters.go:33-52`). Cost attribution is therefore per-invocation truth even under heavy cache reuse — the property a research cost ledger and a production billing report both require. The `FlowBatcher`/`FlowGenerator` adapters preserve the legacy reporting shape while noting exactly where legacy and flow semantics differ (work sequences versus physical attempts, `flow_adapters.go:54-74`), and the shared `provider-steps` cache directory is kept stable across harnesses because "the chunk-compare → answer-quality promotion seam depends on it" (`flow_adapters.go:14-20`).

Retry policy stayed behind, and the file that holds it is a small archive of operational history: `rag/flowpolicy/classifier.go` enumerates transient-failure markers with, for each, the incident that taught it — "embeddings item 49 death after 13,847 completed summaries (2026-07-31)", "read connection timed out during judge execution (2026-07-31)", "HTTP/2 INTERNAL_ERROR during screening (2026-07-31)" (`classifier.go:18-41`). The comment states the placement rule: keep string matching "next to the application that owns the policy, rather than in Flowkit's domain-neutral default." Failure classification is domain knowledge; the generic engine must not accrete it.

### 2.2 Admission inward: provider adapters, quarantined

The prior study noted that ragkit "intentionally ships no adapter," leaving every consumer to write Geppetto glue. Commit `037cd5b` reversed that at the cost of one carefully fenced package: `rag/provider/geppetto` adapts an already-configured Geppetto embeddings provider and reranker. The adapter is defensive in exactly the ways a boundary adapter should be: it validates provider model metadata at construction, rejects model-name mismatches per request, and checks batch alignment, per-vector dimensionality, and finiteness before any vector reaches an index or cache (`rag/provider/geppetto/embedding.go:23-77`). Provider construction and credential handling remain application responsibilities — the adapter takes a built provider, never configuration. The net effect on consumers: the mechanical translation layer every product previously duplicated now lives once, inside the boundary test's sanctioned exception, while credential and profile authority stay outside the kernel where [[Research/Software Architecture Garden/geppetto/README|Geppetto]] and the applications own them.

## 3. Lens one — reproducible research

### 3.1 The identity ladder

Everything replayable in ragkit hangs off one ladder of content addresses. `digest.JSON` canonicalizes and hashes documents, chunks, and representations; per-backend content digests cover the lexical records, vector entries, and content store; and the bundle ID is a truncated digest (`rk-` + 16 hex) over an `identity` structure that includes the schema version, corpus/chunk/representation digests, chunker identity (name and rune parameters), sorted representation kinds, lexical backend identity (backend, version, channel, boosts, content digest), optional vector identity (backend, version, channel, provider, model, dimensions, representation digest, content digest), and content-store identity (`rag/indexbundle/identity.go:12-87`, `rag/indexbundle/types.go:18-60`). The consequences a researcher can rely on:

- Two builds from identical inputs and identical engine configuration produce the same bundle ID, and `BuildStream` proves it by verifying and reusing an existing destination rather than rebuilding (`rag/indexbundle/build_stream.go:67-87`).
- Any change that could change retrieval behavior — a chunker parameter, a boost, an embedding model or dimension count, the backend schema version — changes the bundle ID, because each is a field of the identity structure.
- The embedding model's identity is pinned per bundle, so a query-time embedder that disagrees is rejected at `Open` rather than silently producing incomparable vectors.

Equally important is what the ladder does *not* pin, and the prior study's obligations here remain accurate at this snapshot: a bundle digest is not provider behavior (generation and reranking still happen outside it), cache-key completeness is still a caller obligation (an omitted decoding parameter still produces unsound hits), and `dataset.LoadEvaluation` still drops `EvaluationSet.ID` and tolerates an empty `CorpusDigest` (`rag/dataset/load.go:38-56`), so binding an evaluation set to a corpus remains a host's job — which is precisely the gap [[Research/Software Architecture Garden/ragopt/README|Ragopt]] fills with suite digests and CoinVault fills with its digest-locked eval set.

### 3.2 What the evaluation-loops research family inherits

The connection runs in both directions. Downstream, ragkit's identities are the *inputs* to instrument freezing: CoinVault's RAGOPT preflight verifies the bundle ID, corpus digest, and the byte digests of `bleve/rag-manifest.json` and `vectors.sqlite` as locked snapshot dimensions — those values exist and are stable because this library computes and persists them. Upstream, ragkit's caches are population-keyed stores in exactly the sense project 01 of the [[Research/Software Architecture Garden/Research/evaluation-loops/README|research family]] formalizes: the reranking cache key covers model, query digest, ordered `EvidenceIdentity` values, result count, and adapter version (`rag/reranking/cached.go:19-26`), so bumping the adapter version retires the population, and the score-independent evidence identity guarantees that a reranker's own output can never feed back into its cache key. The flowkit extraction's byte-frozen key is the cross-repository proof that this discipline holds under refactoring pressure, not only under measurement.

## 4. Lens two — RAG research and applications

### 4.1 The contract: five interfaces in, everything else reused

A new application supplies implementations of at most five single-method interfaces — `Chunker`, `Embedder`, `Generator`, `Reranker`, `Searcher` (`rag/components.go:9-88`) — and in the common case fewer, because the Geppetto adapters cover embedding and reranking and the built-in indexes cover search. Each interface carries an error-contract sentence that matters operationally: "a non-nil error does not imply an empty result: providers and decorators must preserve any result fields, especially billed Usage, that were produced before the error" (`rag/components.go:32-34`, repeated for `Embedder` and `Reranker`). Cost custody under failure is part of the interface, not an afterthought — a provider call that dies mid-stream still reports what it billed.

What the application must still supply for itself, because ragkit refuses to: corpus admission policy (which documents, which metadata), authorization and scoping, evidence budgets and presentation, prompt content, run custody, and every gate or promotion decision. The refusals define the product seam.

### 4.2 Two consumer styles, both intended

The workspace's two consumers use the kernel in structurally different ways, and the difference is the most instructive evidence in this study.

| Dimension | rag-ttc (full-service style) | CoinVault (kernel style) |
|---|---|---|
| Import profile | 105 × `rag`, 53 × `rag/answering`, plus dataset, evaluation, generation, flow | 33 × `rag`, 15 × `rag/indexbundle`, plus digest, representations, retrieval, reranking; **zero** `rag/answering` |
| Answering | Ragkit's `answering.Service` with its grounded-answer contract, in the admin assistant (`rag-ttc/internal/admin/assistant/`) | Its own tool loop, evidence ledger (`E1..En`, 12-item/18k-rune budget), and citation grounding — none of it ragkit code |
| Retrieval policy | Service strategies and validated request options | Own pre-fusion authorization, weighted RRF configuration, comparison plans, synonym expansion |
| Bundle usage | Build/open for experiment indexes | Production `BuildStream` with stage telemetry and preflighted scratch directories, serving `Open` with startup-stage observers |

rag-ttc, the lineage parent, consumes the whole stack including the opinionated answering service. CoinVault, the production application, consumes the kernel below the answering layer and re-implements everything above it — because its evidence budget, its authorization model, and its `[E#]` citation contract are product policy that the [[Research/Software Architecture Garden/coinvault/README|CoinVault study]] documents as deliberately server-owned. The question this study set out to answer — "coinvault's evidence ledger, authorization, and comparison plans sit outside ragkit: is that the right boundary?" — resolves affirmatively on the evidence: those components encode per-product law (who may see which source roles, how many evidence items a judge and a prompt may consume, which retrieval plans were human-reviewed), exactly the category ragkit's refusals exclude, and CoinVault's ledger interoperates with ragkit identities (chunk IDs, content digests) without needing ragkit code. The kernel's value to CoinVault is the layer that is genuinely product-independent: validated types, digests, bundles, fusion arithmetic, cached decorators.

The one asymmetry worth recording: `rag/answering` currently has exactly one consumer style exercising it (rag-ttc), so its contract-fence and abstention machinery — including the newer `contract_fence_test.go` and query-generation tests — carries less cross-product evidence than the kernel layers both consumers share. It is the layer most likely to evolve if a second full-service consumer appears.

## 5. Lens three — running in production

The thirty-eight commits between the snapshots are dominated by one arc, and its origin is recorded in the consumer: CoinVault's `COINVAULT-INDEX-OOM-001` ticket ("bounded-memory full knowledge bundle build"). The prior `Build` API took complete `[]rag.Document`, `[]rag.Chunk`, `[]rag.Representation`, `[]rag.Vector` slices — fine for research corpora, fatal for a production corpus that exceeds memory. The response was not a bigger machine but a re-architecture of admission, and it is the best current example in the Garden of a research kernel hardening into an operational one without changing its identity semantics.

### 5.1 Bounded staged admission

`BuildStream` accepts a `Produce` callback that pushes data through a `Stager` in bounded batches (`rag/indexbundle/types.go:82-98`). The stager writes into a SQLite staging relation with a strict phase state machine — documents → chunks → representations → vectors → sealed — where every batch is a transaction, every row is validated at admission against its already-staged parent (a chunk loads its document and passes `ValidateChunk`; a representation loads its chunk and passes `ValidateRepresentations`; a vector must match the declared embedding model and dimensions and be finite), phase transitions from an empty phase are rejected, and batch sizes outside `[1, BatchSize]` are rejected (`rag/indexbundle/staging_kernel.go:141-215, 592-668, 670-699`). `seal` refuses incomplete relations, then computes every identity digest by *streaming* rows out of SQLite in canonical order rather than materializing slices (`staging_kernel.go:217-281, 283-322`). Heap use is bounded by batch size and SQLite's page cache, not corpus cardinality.

The sealed plan then drives the same publish protocol as before — temporary sibling directory, backends built from streamed records, atomic rename — but with a new class of check: after each backend is built from the staged relation, its measured identity must equal the sealed plan's ("streamed content identity differs from sealed identity", "streamed lexical content digest differs from sealed identity"; `rag/indexbundle/build_stream.go:105-140`). The build proves it wrote what it promised, stage by stage.

### 5.2 Fail-closed scratch custody and preflight

Verification of large bundles needs disk-backed scratch state (a bounded SQLite relation with `journal_mode=OFF`, `WITHOUT ROWID` identity tables, and 512-row batches; `rag/indexbundle/verification_relation.go:14-90`). The HEAD commit makes the scratch directory a **required** parameter on `StreamInput`, `VerifyOptions`, and `OpenOptions`, each with the same recorded rationale: fail closed rather than fall back to `os.TempDir`, "which may be unwritable under a read-only root or an unowned mounted volume," and fail *early* "so a late permission failure cannot occur after expensive staging and sealing" (`types.go:91-98, 152-163, 173-184`). `PreflightScratch` completes the thought with a check that is stronger than a writability test: it opens a real verification relation, pushes a probe row through the actual chunk-identity admission path, commits, and removes — "a success predicts late-phase verification success rather than only directory writability" (`rag/indexbundle/preflight.go:19-56`). This is the treatment-exercise instinct — configuration is not behavior; exercise the real path — applied to infrastructure preflight, and CoinVault consumes it directly in its own build preflight (`coinvault/internal/knowledgebuild/preflight.go`).

### 5.3 Serving posture and observability vocabulary

The remaining arc commits harden serving: Bleve indexes open read-only for both verification and serving, bundles open "without eager payload slices," an identity-bound content store is published inside the bundle, and vector inspection is cancellable with bounded chunk validation. Every long-running operation now emits typed stage identifiers — fifteen `BuildStage` values from `input_validated` through `bundle_published`/`result_measured`, six `VerifyStage` values, seven `OpenStage` values — documented as "stable log/telemetry identifiers rather than display strings," with observer contracts that demand quick, non-mutating callbacks (`types.go:100-148`). CoinVault attaches memory and duration telemetry to exactly these hooks (`coinvault/internal/knowledgebuild/build.go:507`, `internal/knowledge/service.go:104-126`). A library exporting a *stable stage vocabulary* rather than log lines is the difference between a consumer building dashboards and a consumer grepping strings; it is the observability analogue of the presentation-protocol pattern.

`Bundle.Close` closes all three backends exactly once under `sync.Once`, preserving the first error (`types.go:196-216`) — small, but the kind of detail that separates a library that survives serving restarts from one that leaks file handles.

### 5.4 What production still does not get

The refusals stand, and they matter operationally: there is still no active-pointer or activation protocol (a serving process must own its own atomic bundle switch — CoinVault does), no cross-process build coordination (two builders racing one bundle ID still have rename-loser semantics), no authentication or tenancy, and no release pipeline in this repository beyond Makefile release targets. The workspace itself supplies the sharpest operational lesson: extracting flowkit created a window in which one workspace member (rag-ttc) imports packages its workspace-resolved dependency no longer has. Library extraction under an identity-stability law protected the *data* (caches replay); nothing protected the *workspace build* (consumers skew). A monorepo-style workspace with multi-repo versioning gets the failure modes of both unless membership and migration land together.

## 6. Pattern maturity assessment

| Pattern or law | Maturity | Evidence or limitation |
|---|---|---|
| Content-addressed bundle identity over a schema-versioned identity projection | Established | Build/reuse/tamper tests; two consumers; identity fields cover every behavior-relevant build parameter |
| Cache identity stability across engine extraction ("wiring may change, identity may not") | Candidate ecosystem pattern | Written law with byte-frozen key and dual-era replay intent (`flow_step.go:14-20`); one extraction event; a second migration under the same law would confirm it |
| Bounded staged admission with per-batch validation and streamed sealing | Established | Phase state machine, per-row parent validation, streamed digests, production-shaped bounded-build tests, and a production consumer (CoinVault `BuildStream`) |
| Fail-closed required scratch custody with real-path preflight | Candidate ecosystem pattern | One implementation plus one consumer; the "preflight by exercising the real path" idea generalizes well beyond bundles |
| Stable stage-identifier observability vocabulary | Candidate ecosystem pattern | Three stage enums with documented observer contracts; CoinVault telemetry consumes them; no second independent library does this yet |
| Incident-annotated transient-failure classification kept domain-side | Candidate ecosystem pattern | `flowpolicy` markers each cite the teaching incident; placement rule written; generalizes to any retry policy at a generic-engine boundary |
| Provider-adapter quarantine via dependency-direction structural guard | Established | `boundary_test.go` walks the full dependency closure; second Garden occurrence of the structural-guard genre applied to imports |
| Usage custody under failure (pointer semantics, preserve-on-error, replay zeroing, meter round-trip) | Established | Interface contracts, meter conversions preserving missing-vs-zero, adapter tests |
| Full-service answering layer as a reusable product surface | Emergent | Single consumer style (rag-ttc); contract fence exists but lacks cross-product evidence |
| Workspace version coherence across extraction | Architecture debt (workspace-level) | rag-ttc fails to compile against workspace ragkit HEAD; stale `go.mod` pins coexist with `go.work` overrides |

## 7. Failure modes and open obligations

- **The migration window is open.** rag-ttc's eighteen `ragkit/execution` and seven `ragkit/flow` import sites must move to flowkit before the workspace builds coherently. Until then, any claim that "the workspace builds" is false for one member, and CI that runs per-repository with `GOWORK=off` will not notice.
- **Carried forward from the prior study, still unresolved at this snapshot:** generic cache-key completeness remains a caller obligation; cross-invocation and cross-process duplicate execution now belongs to flowkit's ledger rather than ragkit's, but no single-flight or CAS exists on either side; `LoadEvaluation` still discards the evaluation-set ID; and the answering/`Service` path still does not prove generic hit-parent lineage for arbitrary searchers.
- **Two-writer bundle publication** still resolves by rename with an unexamined loser. The staging arc made single-builder behavior provably bounded and atomic; it did not add coordination.
- **The scratch-directory API is a breaking change** (three option structs grew a required field). CoinVault absorbed it inside the workspace; the pinned-version consumers have not. This is the ordinary cost of fail-closed retrofits, worth recording because the alternative — a defaulted, silently fallback-prone parameter — was explicitly rejected in the field comments.

## 8. Candidate ecosystem guidance

1. **Freeze cache identity across refactorings, in writing, at the adapter.** When an engine is extracted or replaced, the population key's bytes are a compatibility contract equal in rank to the public API; state the law in the code that implements it and test replay across the boundary.
2. **Preflight by exercising the real path.** A preflight that checks a precondition proxy (writability, existence) predicts less than one that performs a probe transaction through the same code that will run later. Ragkit's scratch preflight and CoinVault's `--preflight-only` are the same pattern at two scales.
3. **Make long operations emit a stable stage vocabulary.** Typed stage identifiers with documented observer contracts let every consumer build telemetry without string coupling, and make "where did the build die" a data question.
4. **Keep failure taxonomy with the domain that learned it.** Transient-marker lists annotated with their teaching incidents belong beside the domain policy owner, not inside the generic engine — the engine stays reusable, and the annotations preserve why each rule exists.
5. **Admit streamed input through a validated phase machine, then seal identity from the staged relation.** Bounded memory and exact identity are compatible; the trick is computing digests by streaming the durable staging store, and cross-checking each built backend against the sealed plan.

Each of these has one strong implementation and at least one consumer here; none should be promoted past candidate status without an independent second implementation, per the Garden's comparison rule.

## 9. Open questions

1. Should `answering.Service` absorb CoinVault-style evidence budgeting as an optional policy object, or is the budget/ledger inherently product law? The two-consumer evidence suggests the latter, but a third consumer would decide it.
2. Does flowkit inherit the identity-stability law as its own documented contract, or does the law live only in ragkit's adapter comments? The extraction is only half-finished if the generic engine can change its key handling freely.
3. What is the minimal bundle-activation protocol (current pointer, reader fence, delayed cleanup) worth standardizing, given publish-vault and CoinVault both hand-roll one over atomic snapshot swap?
4. Should `EvaluationSet.ID` and `CorpusDigest` become required at load, with the permissive path renamed, now that two downstream systems (Ragopt suites, CoinVault's eval set) have independently rebuilt the binding ragkit declined to enforce?
5. When rag-ttc migrates to flowkit, does its cached population replay byte-identically as DR-3 promises? That migration is the natural experiment that would promote the identity-stability pattern to established.

## Related studies

- [[Research/Software Architecture Garden/ragkit/README|Architecture Garden — Ragkit]] — the authority-discipline study this document extends
- [[Research/Software Architecture Garden/ragkit/designs/01 - Source-Authoritative Evidence Ledger Kernel|Source-Authoritative Evidence Ledger Kernel]]
- [[Research/Software Architecture Garden/ragopt/README|Ragopt]] — the experiment-custody complement
- [[Research/Software Architecture Garden/coinvault/README|CoinVault]] — the kernel-style production consumer
- [[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]] — the full-service lineage consumer
- [[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]] — the research family whose frozen-instrument and population-key projects build on these identities
- [[Research/Software Architecture Garden/geppetto/README|Geppetto]] — the provider runtime behind the sanctioned adapters
