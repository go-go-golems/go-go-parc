---
title: "rag-ttc: Reproducible TTC RAG Evaluation with Blinded LLM Judges"
aliases:
  - TTC RAG answer-quality pilot
  - rag-ttc LLM judge evaluation
  - RAG-TTC-LIVE-E2E-001 results
tags:
  - article
  - rag
  - ttc
  - evaluation
  - retrieval
  - llm-as-judge
  - reproducibility
status: complete
type: article
created: 2026-07-27
analyzed: 2026-07-27
repo: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/rag-ttc
repository_commit: c94d41c0501e0602cc8508d4440b778a0529af9b
repository_branch: task/ttc-live-rag-quality-experiment
repository_remote: git@github.com:wesen/rag-ttc.git
source_ticket: RAG-TTC-LIVE-E2E-001
source_run: 20260727T200731.330446235Z-answer-quality-11e8ab230bd7
related_files:
  - cmd/rag-ttc/cmds/experiments/answerquality/runner.go
  - cmd/rag-ttc/cmds/experiments/answerquality/review.go
  - cmd/rag-ttc/cmds/experiments/answerquality/measure.go
  - pkg/rag/evidence_identity.go
  - prompts/ttc-grounded-answer-v1.txt
  - prompts/ttc-grounded-answer-v1.schema.json
---

# rag-ttc: Reproducible TTC RAG Evaluation with Blinded LLM Judges

This article explains a complete answer-quality experiment over the Tree Center
corpus: fixed inputs, two retrieval arms, grounded generation, deterministic
contract checks, blinded LLM judging, paired analysis, and a zero-provider-work
annotation import. The experiment is small enough to inspect and strict enough
to expose the difference between retrieval quality, answer validity, judged
quality, and reproducibility.

It continues the implementation account in
[[PROJECT REPORT - rag-ttc - From Clean-Slate Toolbox to Live TTC Answer Quality Evaluation]]
and relies on the architecture described in
[[ARTICLE - rag-ttc - Architecture of a Reproducible Go RAG Evaluation System]].
The package reorganization that made this execution tractable is analyzed in
[[ARTICLE - rag-ttc - Refactoring Explicit Experiments and Reusable Mechanisms]].
All of these documents are indexed by [[rag-ttc]].

> [!summary]
> - The pilot compared BM25 with reciprocal-rank fusion over the same 30 judged
>   queries, prompt, context policy, generator, and five-evidence limit.
> - RRF improved MRR from `0.9000` to `0.9733`, Recall@10 from `0.7000` to
>   `0.8389`, and every mean judge dimension.
> - Paired bootstrap intervals excluded zero for correctness and completeness,
>   but not for groundedness, citation correctness, or abstention.
> - Two independent `umans-glm-5.2` Pi sessions produced 70 blinded
>   annotations: 60 primary scores and a balanced 10-item overlap.
> - The annotation import recovered 1,982 corpus embeddings, 30 query
>   embeddings, and 60 generations from cache with zero provider work.
> - One overlap item received scores of 0 and 3 because the rubric did not
>   define how correctness and citations apply to an abstained answer. The
>   result supports RRF for a follow-up experiment, but it is not human-review
>   evidence and does not settle the rubric.

## 1. What the experiment measures

A RAG answer is produced by several decisions. The retriever selects evidence;
the context policy decides which selected items enter the prompt; the generator
constructs an answer; a contract validator decides whether the response is safe
to expose; and a reviewer evaluates the exposed answer against the evidence.
Combining these into one score would make failures difficult to interpret.

The run therefore preserves four evidence classes:

| Evidence class | Question answered | Canonical artifact |
|---|---|---|
| Retrieval | Did the arm rank judged material highly? | `results/retrieval-summary.json` |
| Contract | Was generated JSON parseable and were citations valid? | `results/answer-contract-summary.json` |
| Review | Was the exposed answer correct, grounded, complete, cited, and appropriately abstained? | `results/human-review-summary.json` |
| Operations | Did execution respect budgets and avoid unnecessary provider work? | `observations/cache.json`, `observations/budgets.json` |

This separation matters when reading the result. RRF can retrieve better
evidence yet still produce a contract failure. A generator can produce a useful
answer whose citation identifier is malformed by one character; the safety
layer converts that cell to an abstention. A judge then evaluates the safe
exposed answer, not the invalid raw response.

## 2. Frozen experimental design

The corpus contains 200 TTC documents. Fixed markdown-aware chunking produced
1,982 raw representations. The evaluation subset contains 30 judged queries,
stratified into five categories with six queries each:

- commerce and support;
- planting procedures;
- care and diagnosis;
- site, zone, and plant selection;
- catalog comparison.

Every query was executed through two arms:

```text
BM25:
  query -> Bleve BM25 -> hydrate five chunks -> generate

RRF:
  query -> Bleve BM25 ---------\
                                -> reciprocal-rank fusion
  query -> exact vector search /   -> hydrate five chunks -> generate
```

The generation profile used OpenAI `gpt-5-nano`; embeddings used
`text-embedding-3-small` at 1,536 dimensions. Both arms used the same versioned
prompt, schema, generator, context policy, and maximum evidence count. This
holds generation policy constant while changing retrieval.

The experiment directory copied the corpus, evaluation set, prompt, schema,
configuration, and imported annotations. It retained per-query records before
constructing aggregate reports. A future reader can therefore recompute a mean
or inspect a single failure without reconstructing transient process state.

## 3. Grounded generation and contract enforcement

The prompt requires a JSON answer with answer text, cited chunk IDs, and an
explicit abstention flag. The validator checks syntax and semantics:

```text
parse raw response
if parsing fails:
    expose safe abstention
else if a citation is not among the supplied chunks:
    expose safe abstention
else if abstention fields contradict one another:
    expose safe abstention
else:
    expose parsed grounded answer
```

The contract results were:

| Arm | Cells | Valid | Parse failures | Contract failures | Exposed abstentions |
|---|---:|---:|---:|---:|---:|
| BM25 | 30 | 25 | 1 | 4 | 13 |
| RRF | 30 | 25 | 0 | 5 | 7 |

Both arms produced 25 valid cells. RRF produced more citation-success cells,
23 versus 17, and fewer abstentions. The counts must not be read as a pure
generator comparison: different retrieved evidence changes both the answer and
whether answering is justified.

One representative BM25 failure answered the shipping-notification question
correctly but cited `chunk-02f6f7112c22f48` instead of the supplied
`chunk-02f6f7112c22f48c`. The validator rejected the unknown identifier and
exposed an abstention. This is an important result. A factual answer with an
invalid evidence reference is not a valid grounded answer under the experiment
contract.

## 4. Semantic identity and zero-authority replay

The first live pilot exposed sub-ULP score drift in BM25:

```text
1.996638799554313
1.9966387995543127
```

The ranked chunks, text, and answer were identical, but a cache and review
identity that included the score changed. The corrected semantic evidence
identity is the ordered sequence of chunk IDs and content digests:

```go
type EvidenceIdentity struct {
    ChunkID       string
    ContentDigest string
}
```

Order carries ranking semantics. Raw scores and mutable rank fields remain
observations, not semantic identity. Generation caching, reranking caching, and
review IDs use this same projection.

After current-version cache regeneration, two independent runs with embedding,
generation, and reranking budgets all set to zero produced byte-identical
60-record review queues and private keys. The final annotation import also
used literal-zero budgets:

| Stage | Hits | Misses | Writes | Work calls |
|---|---:|---:|---:|---:|
| Corpus embedding | 1,982 | 0 | 0 | 0 |
| Query embedding | 30 | 0 | 0 | 0 |
| Generation | 60 | 0 | 0 | 0 |
| Reranking | 0 | 0 | 0 | 0 |

This is stronger than reporting that a replay was inexpensive. The replay had
no authority to perform provider work. Any missing cache entry would have
failed before a request.

## 5. Blinded LLM judging

Two independent Pi sessions used the `umans/umans-glm-5.2` profile. The primary
judge received all 60 queue records. The secondary judge received a
deterministic ten-item subset: the lexicographically smallest review ID in each
of five category by two arm groups. Neither session received the private key
that maps review IDs to arms.

The queue contained only what a judge needed:

```text
review ID
query
five evidence chunks
exposed answer
citation IDs
abstention state
```

The judges scored correctness, groundedness, completeness, and citation
correctness on 0–3 scales, and abstention on a 0–2 scale. The combined file
contained 70 unique `(review_id, reviewer)` pairs and was validated before
import.

Blinding removes direct arm-label bias. It does not make two model sessions
equivalent to two human experts. Both sessions used the same model family,
rubric, and prompt. Their overlap measures within-model judgment stability
under independent contexts, not independent human agreement.

## 6. Retrieval and answer-quality results

RRF improved every retrieval aggregate:

| Arm | MRR | Recall@10 | nDCG@10 | Hit rate@10 |
|---|---:|---:|---:|---:|
| BM25 | 0.9000 | 0.7000 | 0.7274 | 0.9333 |
| RRF | 0.9733 | 0.8389 | 0.8628 | 1.0000 |

The imported review report averages duplicate overlap annotations at the item
level, so each query-arm cell contributes once:

| Dimension | BM25 | RRF | RRF minus BM25 |
|---|---:|---:|---:|
| Correctness | 1.65 | 2.30 | +0.65 |
| Groundedness | 1.68 | 2.27 | +0.58 |
| Completeness | 1.55 | 2.23 | +0.68 |
| Citation correctness | 1.72 | 2.23 | +0.52 |
| Appropriate abstention | 1.53 | 1.73 | +0.20 |

The paired analysis reports BM25 relative to RRF:

| Dimension | BM25 wins | Ties | BM25 losses | BM25 − RRF mean | Bootstrap 95% interval |
|---|---:|---:|---:|---:|---:|
| Correctness | 4 | 16 | 10 | -0.65 | [-1.25, -0.017] |
| Groundedness | 4 | 15 | 11 | -0.58 | [-1.217, 0.033] |
| Completeness | 5 | 15 | 10 | -0.68 | [-1.30, -0.083] |
| Citation correctness | 4 | 16 | 10 | -0.52 | [-1.15, 0.10] |
| Appropriate abstention | 2 | 22 | 6 | -0.20 | [-0.533, 0.133] |

Correctness and completeness have intervals below zero. The other three
dimensions favor RRF in their means, but their intervals include zero. With 30
pairs, the disciplined conclusion is that the pilot provides stronger evidence
for correctness and completeness improvements than for the remaining
dimensions.

## 7. What disagreement revealed

The two judges agreed exactly on all abstention decisions, nine of ten
completeness scores, and seven of ten scores for each remaining dimension. The
mean absolute disagreement was `0.1` for completeness and `0.5` for
correctness, groundedness, and citation correctness.

The Canada-shipping item produced the largest discrepancy. The answer
abstained because the evidence said TTC ships throughout the United States but
did not explicitly state whether Canada is supported. Judge A assigned zero to
correctness, groundedness, completeness, and citation correctness. Judge B
assigned three to correctness, groundedness, and citation correctness, one to
completeness, and agreed that abstention was debatable.

Both interpretations are internally defensible because the rubric defines
whether abstention is appropriate but does not specify what the other four
dimensions mean when no substantive answer is given. Before the next study,
the rubric should state one of these policies:

- score non-abstention dimensions as not applicable and exclude them;
- score the factual content of the abstention explanation;
- assign fixed values derived from the abstention score.

The first policy is the cleanest. It avoids treating absence of a claim as
either perfectly correct or entirely incorrect.

The hydrangea overlap also found a genuine evidence-reading ambiguity. One
judge treated “mauve” as unsupported for Vienna; the other found related
uncited material but penalized citation correctness. This indicates that judge
instructions should distinguish support anywhere in supplied evidence from
support in explicitly cited chunks.

## 8. Conclusions and next experiment

This pilot supports using RRF as the stronger retrieval arm for the next TTC
experiment. The conclusion has boundaries:

- it covers 30 stratified queries, not the complete evaluation set;
- it uses one generator and one fixed context policy;
- it uses two sessions of one LLM judge profile, not human experts;
- two judge dimensions show intervals excluding zero;
- abstention scoring requires revision before another confirmatory comparison.

The next experiment should preserve this frozen query set and compare vector
retrieval with RRF after revising the rubric. A later experiment can compare
RRF with reranked RRF when a real reranker is configured. Parameters should not
be tuned on this pilot and then evaluated on the same 30 queries as if the
result were confirmatory.

## 9. Source map

The principal implementation and evidence paths are:

- `cmd/rag-ttc/cmds/experiments/answerquality/runner.go`
- `cmd/rag-ttc/cmds/experiments/answerquality/answer.go`
- `cmd/rag-ttc/cmds/experiments/answerquality/review.go`
- `cmd/rag-ttc/cmds/experiments/answerquality/measure.go`
- `pkg/rag/evidence_identity.go`
- `ttmp/2026/07/25/RAG-TTC-LIVE-E2E-001--first-live-end-to-end-ttc-rag-quality-experiment`
- `sources/phase10/reviewed-runs/20260727T200731.330446235Z-answer-quality-11e8ab230bd7`

The durable engineering rules are:

- freeze scientific inputs before provider execution;
- preserve per-query records before aggregates;
- validate generated answers independently of judged quality;
- derive semantic identity from stable content, not floating-point scores;
- make replay incapable of paid work;
- blind judges from arm identity;
- treat judge disagreement as evidence about the rubric;
- state statistical and evaluator limitations beside the result.

## Related notes

- [[rag-ttc]]
- [[PROJECT REPORT - rag-ttc - Clean-Slate RAG Experiments in Plain Go]]
- [[PROJECT REPORT - rag-ttc - From Clean-Slate Toolbox to Live TTC Answer Quality Evaluation]]
- [[PROJECT REPORT - rag-ttc - Simplifying a Recoverable and Measurable RAG Experiment System]]
- [[ARTICLE - rag-ttc - Architecture of a Reproducible Go RAG Evaluation System]]
- [[ARTICLE - rag-ttc - Refactoring Explicit Experiments and Reusable Mechanisms]]
