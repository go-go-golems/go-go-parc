---
title: "PROJECT REPORT - Transcript RAG Bleve - goja-bleve 0.0.6 and the Native RRF Restoration"
aliases:
  - Transcript RAG Bleve 0.0.6 Followup
  - Bleve Native RRF Restoration
  - TRANSCRIPT-RAG-BLEVE Correction
tags:
  - project-report
  - rag
  - bleve
  - xgoja
  - goja
  - faiss
  - vectors
  - rrf
  - scorch
status: active
type: project-report
created: 2026-07-13
repo: /home/manuel/code/wesen/2026-07-09--transcript-rag
supersedes: "[[Projects/2026/07/09/PROJECT REPORT - Transcript RAG Bleve - Hybrid Search, Empirical Findings, and the Corrected Architecture]]"
---

# PROJECT REPORT - Transcript RAG Bleve - goja-bleve 0.0.6 and the Native RRF Restoration

This is the current release and ranking-correction branch of the [[goja-bleve]] project map.

This note corrects the conclusion of the earlier Transcript RAG Bleve report. That report concluded that bleve kNN was unusable and that the semantic leg had to stay as a brute-force cosine scan in JavaScript. The conclusion was wrong. It was an artifact of validating against `bleve.memory()`, which goja-bleve 0.0.5 built as an upsidedown index. Vector kNN executes through scorch, so the in-memory index returned empty results and made both the recall measurement and the fusion measurement fail. goja-bleve 0.0.6 fixed the memory index to use scorch and exposed the FAISS IVF probe parameters. Re-tested against a persistent scorch index — the index type production actually uses — bleve kNN has 100% recall and native reciprocal-rank fusion produces a true lexical∪semantic union. The project now runs the original design: one bleve index holds text and vectors, and a single native RRF search fuses the two legs.

This note is written for an engineer who read the earlier report and needs to know what to believe instead. It states what changed, proves the correction with a re-test, and records the lesson. It does not use analogies.

> [!summary]
> - The earlier report's two findings — native `Score: "rrf"` does not union, and bleve kNN has ~0% recall — were **artifacts of `bleve.memory()`**, which goja-bleve 0.0.5 built as an upsidedown index. Vector kNN requires scorch.
> - goja-bleve 0.0.6 fixed `bleve.memory()` to use scorch and exposed `knn(field, vector, k, { ivfNprobePct, ivfMaxCodesPct })`. Issue [#10](https://github.com/go-go-golems/goja-bleve/issues/10) is closed.
> - Re-tested on a persistent scorch index: **100% kNN recall** and **native RRF unions**.
> - The project now uses native bleve kNN + RRF (the original design). `rag_vectors` and brute-force cosine are removed. Validated end-to-end.

## What changed in goja-bleve 0.0.6

Two commits, tracked under the `BLEVE-KNN-PARAMS` ticket and merged in PR #11:

1. **Memory index fix** (`5d4d325`, "fix: use Scorch for vector memory indexes"). `bleve.memory()` previously delegated to `bleve.NewMemOnly`, which constructs an *upsidedown* index. Vector kNN executes through the *scorch* index type, so an upsidedown memory index silently returned no vector results. The fix routes the vector-enabled memory builder through scorch (using bleve's in-memory key-value store with `NewUsing` and the scorch index type). Non-vector builds retain `NewMemOnly`. Persistent indexes created with `bleve.create(path)` already used scorch and were never affected.
2. **IVF search parameters** (`743a858`, "feat: expose KNN IVF search parameters"). The `knn` builder now accepts an optional trailing params object:

   ```typescript
   knn(field: string, vector: Vector, k: number, boost?: number, params?: KNNIVFParams): this;
   knn(field: string, vector: Vector, k: number, params?: KNNIVFParams): this;

   interface KNNIVFParams {
     ivfNprobePct?: number;   // percentage of clusters to probe
     ivfMaxCodesPct?: number; // percentage of vectors to visit
   }
   ```

   The binding maps lower-camel JavaScript keys to bleve's snake-case JSON keys (`ivf_nprobe_pct`, `ivf_max_codes_pct`), validates each value to `[0, 100]`, and rejects unknown keys. It assigns the marshalled JSON to `KNNRequest.Params` after `AddKNN`. A side effect of the same investigation: pure kNN via `query(bleve.matchNone())` now returns hits (it returned zero in 0.0.5).

## The root cause of the earlier report's error

The earlier report's two findings shared one cause. Its validation experiments used `bleve.memory()` to build small test indexes. In goja-bleve 0.0.5, `bleve.memory()` built an upsidedown index. Vector kNN runs through scorch, so the upsidedown memory index returned empty kNN candidate lists. With empty kNN candidates:

- The native RRF rescorer's `mergeDocs` had no kNN-only hits to append, so the fused result contained only the lexical matches. The report read this as "native RRF does not union."
- The recall test measured zero overlap with exact cosine. The report read this as "bleve kNN has ~0% recall," including the exact-match smoking gun where a query identical to an indexed document failed to return it.

The project's production index was never affected. `build-index.js` creates the index with `bleve.create(dir)`, which uses scorch. The error was in the validation method, not in the production system. The earlier report even noted, in passing, that the two-document case worked — the one configuration where an upsidedown index degenerates to a single effective cluster and happens to return a result.

## The re-test

Re-testing against a persistent scorch index — the index type production uses — reverses both findings.

**kNN recall.** One hundred forty deterministic 768-dimensional vectors, ten queries, top-5 overlap against exact brute-force cosine:

| Configuration | Recall |
| --- | --- |
| default params | 100% (50/50) |
| `ivfNprobePct: 100` | 100% (50/50) |

The exact-match smoking gun does not reproduce: a query identical to `d21` returns `d21` at rank 1.

**Native RRF union.** A four-document index where the lexical leg and the semantic leg disagree:

| id | text | vector | matches lexical "privacy"? | close to query vector? |
| --- | --- | --- | --- | --- |
| `both` | "privacy retrieval" | `[0.9, 0.1, 0, 0]` | yes | yes |
| `lex` | "privacy policy" | `[0, 0, 1, 0]` | yes | no |
| `vec` | "retrieval ranking" | `[0.95, 0.05, 0, 0]` | no | yes |

```js
bleve.search()
  .query(bleve.match("privacy").field("text"))
  .knn("embedding", [0.9, 0.1, 0, 0], 5, { ivfNprobePct: 100 })
  .knnOperator("or")
  .score("rrf").scoreRankConstant(60).scoreWindowSize(10)
  .fields(["doc_key"]).size(5).build()
```

Result:

```
total: 3
  both@0.0328   (rank 1 in both legs: 1/61 + 1/61)
  lex@0.0320    (lexical rank 2 + semantic rank 3)
  vec@0.0161    (semantic rank 2 only)
```

All three documents return. The document that ranks high in both legs scores highest; the semantic-only document is present in the union. This is the behavior the earlier report declared missing.

## The restored architecture

The project now runs the original design. One per-generation bleve index holds the chunk text and the embedding vector. Search is a single native RRF request:

```js
bleve.search()
  .query(bleve.match(query).field("text"))                        // lexical leg
  .knn("embedding", qVec, k, { ivfNprobePct: cfg.ivfNprobePct })  // semantic leg
  .knnOperator("or")                                              // union
  .score("rrf").scoreRankConstant(60)                            // RRF, agentsview's k
  .scoreWindowSize(k).size(k).fields([...]).build();
```

`ivfNprobePct` defaults to 100, which probes every IVF cluster and is therefore exact. For the small teaching corpus this is cheap and correct. At scale it can be lowered to trade recall for latency. The rank constant is 60, matching `agentsview`'s `rrfMerge`.

The SQLite store shrank. `rag_vectors` is removed; the database now holds only `rag_docs` (the content-addressed mirror), `rag_generations`, and `rag_meta` (the content-hash stamps). The content-hash incremental invariant is unchanged: the stamp gates the bleve upsert, so an unchanged transcript is a no-op, and the delete pass removes retired units from bleve (located by a `term` query on `doc_key`), the stamp, and the mirror row.

## Validation

| Scenario | Result |
| --- | --- |
| Unit tests | 15/15 pass (mapping, pure kNN, native RRF union, create-or-open, rollup, subordinate penalty) |
| Fresh index | 37 chunks in bleve; tables = `rag_docs, rag_generations, rag_meta` (no `rag_vectors`) |
| `rag search "sqlite migration"` | top hit 0.031 (both-leg RRF boost) |
| `rag search "loadColumns"` | lexical leg finds exact identifier mentions |
| Incremental no-op | 0 pending, 0.48 s |
| Delete pass | 3 sessions (77/89) → re-index 1 → 45 removed, 32/37/1, activates |
| `rag ask` | grounded answer citing the fix |

## The lesson

Validate against the index backend production uses, not the in-memory convenience path. `bleve.memory()` and `bleve.create(path)` are not interchangeable for vector work in goja-bleve 0.0.5: one builds upsidedown, the other scorch, and only scorch executes kNN. A test that passes on the memory index and fails on the persistent index — or the reverse — is not a test of the production behavior. The earlier report's architecture correction was a real engineering decision made on false evidence, and it propagated into a design-doc erratum, a diary, and this vault. Correcting it required re-running the same experiments against the production backend and accepting that the earlier conclusion was wrong.

A secondary lesson: when a library exposes a capability the binding does not, the gap is usually thin. The IVF params fix was one struct field, one method argument, and one assignment. Filing the issue with a reproduction and a proposed patch made the fix cheap for the maintainer.

## What to believe now

- The earlier report's *description* of the bleve JS API, the FAISS build configuration, the per-generation index layout, the content-hash invariant, and the hydration logic remains accurate.
- The earlier report's *conclusion* — keep brute-force cosine, use application-level RRF — is superseded. The project uses native bleve kNN and native RRF.
- The earlier report's two findings should be read as "what happens when you test vector kNN against an upsidedown memory index," not as properties of bleve kNN or native RRF.

## Important project docs

- Corrected design doc (§16 supersedes §15): `ttmp/2026/07/09/TRANSCRIPT-RAG-BLEVE--implement-bleve-hybrid-lexical-vector-search-replacing-brute-force-cosine-and-fts5/design-doc/01-bleve-hybrid-lexical-vector-search-design-and-implementation-guide.md`
- Diary Step 7 (re-evaluation): `…/TRANSCRIPT-RAG-BLEVE--…/reference/01-investigation-diary.md`
- Upstream issue (closed): [go-go-golems/goja-bleve#10](https://github.com/go-go-golems/goja-bleve/issues/10)
- goja-bleve 0.0.6 KNN-params design: `goja-bleve/ttmp/2026/07/11/BLEVE-KNN-PARAMS--…/design-doc/01-knn-parameter-api-and-recall-test-design.md`

## Related notes

- [[Projects/2026/07/09/PROJECT REPORT - Transcript RAG Bleve - Hybrid Search, Empirical Findings, and the Corrected Architecture]] (superseded conclusion; description still accurate)
- [[Projects/2026/07/09/PROJECT REPORT - Transcript RAG - Analyzing agentsview Vector Search and Recreating It in JavaScript]]

---

*Drafted by the umans-glm-5.2 model running under the Pi coding-agent harness (go-go-golems). This note corrects the earlier Transcript RAG Bleve report after goja-bleve 0.0.6 fixed the memory-index vector bug and exposed IVF probe parameters.*
