---
title: Retrieval Evaluation - Judged Sets, Ranking Metrics, and Per-Query Analysis
aliases:
  - Retrieval Evaluation
  - Ranking Metrics
tags:
  - article
  - evaluation
  - information-retrieval
  - metrics
  - rag
status: active
type: article
created: 2026-07-30
repo: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/rag-ttc
---

# Retrieval Evaluation: Judged Sets, Ranking Metrics, and Per-Query Analysis

This article presents the methodology for measuring retrieval quality: the structure of judged evaluation sets, the definitions and sensitivities of the standard ranking metrics, the necessity of per-query analysis alongside aggregates, and the auditing practices that determine whether a metric can be believed. The material generalizes from the evaluation harness of [[PROJ - RAG-TTC Chunk Lab - Chunking and Representation Experiments on a Free LLM Gateway]].

> [!summary]
> 1. Retrieval evaluation requires three artifacts — queries, graded judgments, and a stable target identity (the evaluation unit) — and the mapping from system output to target identity is itself a design decision.
> 2. The standard metrics (MRR, Recall@k, HitRate@k, nDCG@k) disagree by construction; their disagreement localizes effects and is information, not noise.
> 3. Aggregates conceal redistribution: a mean can rise while a third of queries regress. Per-query win/loss accounting against a fixed baseline is mandatory.
> 4. A metric is only as honest as its coverage audit: unjudged queries and out-of-corpus relevance both produce numbers that look precise and mean less than they appear to.

## Why this note exists

Retrieval changes are cheap to make and expensive to judge by eye. A team that lacks a judged evaluation set argues from anecdotes; a team that has one but reads only aggregate means ships regressions hidden inside improvements. The evaluation harness this note distills measured twenty-seven experimental configurations in an afternoon and attributed every aggregate movement to named queries — the difference between "the number went up" and "these ten queries improved because the summary removed scoring noise, and these two regressed because the summary dropped their key term". The methodology is small; its absence is the single most common defect in retrieval work.

## Core mental model

### The three artifacts

A judged evaluation set consists of:

1. **Queries** — texts drawn from the distribution the system will actually serve. In the motivating set: 148 questions.
2. **Judgments** — assertions that a *target* is relevant to a query, with a grade. Grades permit distinguishing "the answer" from "related background"; binary metrics collapse grades, nDCG uses them. In the motivating set: 243 judgments.
3. **Target identity** — the granularity at which relevance is defined. Judging at chunk level couples the judgments to one chunking configuration, which destroys comparability the moment chunking changes. Judging at *evaluation unit* level — a stable identity mapped from documents — makes the set immune to re-chunking: any configuration's chunk hits collapse to unit rankings before scoring.

The collapse operation deserves emphasis because it is what makes experiments comparable at all:

```
ranked_units(query):
    seen = {}
    for hit in ranked_chunk_hits(query, k):
        unit = unit_of(hit.document)
        if unit not in seen:
            seen.add(unit)          # a unit keeps its best rank
            emit unit
```

Configurations with 855 large chunks and 7,632 small chunks both reduce to rankings over the same 200 units; their metrics are then commensurable. Without a stable target identity, every chunking experiment would silently redefine its own ground truth.

### The metrics and their sensitivities

For one query, let $R$ be its judged-relevant unit set, and let the system emit a deduplicated ranked unit list. Let $r$ denote the rank of the first relevant unit.

**Reciprocal rank** is $1/r$, or 0 when no relevant unit appears; **MRR** is its mean over evaluated queries. MRR is a *top-position* metric: it moves only when the first relevant result moves, and its increments quantize by rank ($1 \to 1/2 \to 1/3 \dots$). It best predicts the experience of a user who reads from the top and stops early.

**Recall@k** is $|R \cap \text{top-}k|\,/\,|R|$: the fraction of the relevant set found within the cutoff. It is a *breadth* metric, indifferent to order within the top $k$; it best predicts the ceiling of a downstream stage (a generator can only cite what admission saw, and admission draws from the top $k$).

**HitRate@k** is the indicator $[\,R \cap \text{top-}k \neq \emptyset\,]$: did the user who reads $k$ results see at least one relevant one. It is the bluntest and most saturable metric — the motivating system's HitRate@10 sits above 0.93, so most experiments cannot move it and the residual headroom lives in a small, enumerable set of hard queries.

**nDCG@k** discounts graded gain by position and normalizes by the ideal ordering:

$$\text{DCG@k} = \sum_{i=1}^{k} \frac{2^{g_i}-1}{\log_2(i+1)}, \qquad \text{nDCG@k} = \frac{\text{DCG@k}}{\text{IDCG@k}}$$

where $g_i$ is the grade at position $i$. It is the only standard metric that uses grades, and the only one that rewards *ordering quality within* the cutoff rather than membership alone.

The metrics' structural disagreement is diagnostic. In the motivating laboratory's chunk-size sweep, Recall@10 rose substantially with chunk size while MRR moved little: larger chunks made more relevant units *findable* per ranking without changing which unit surfaced *first*. That pattern localizes the effect to breadth, and redirects tuning attention — the first position is governed by term-density effects that chunk size does not touch.

### Per-query analysis

An aggregate is a sum of movements, and movements cancel. The mandatory complement is a per-query accounting against a *fixed baseline configuration*: for each query, compare first-relevant ranks and classify the query as improved, unchanged, or regressed; report the three counts beside every aggregate; persist the full per-query rank table for drill-down.

Two configurations from the motivating laboratory illustrate why the counts are not optional. `breadcrumb` (heading paths prepended to indexed text) scored +4 improved / −0 regressed: a strict improvement, adoptable without reservation. `size-300` (small chunks) scored +6 / −6: a *redistribution*, whose aggregate resembles the strict improvement's but whose adoption trades one user population against another. Means alone cannot distinguish these cases; the distinction is frequently the entire decision.

The baseline must run inside every experimental invocation rather than being quoted from history, for two reasons: harness drift (any change to measurement code shows up immediately as a baseline shift) and environmental identity (deltas are only meaningful when both sides ran under identical conditions).

### Coverage auditing

A metric lies silently in two ways, both of which produce precise-looking numbers.

**Unjudged queries** are skipped, shrinking the denominator. The skip is correct — scoring an unjudged query as zero would punish the system for the set's gaps — but it must be *reported*: "144 evaluated, 4 skipped" is part of the result, and growth of the skipped count over time indicates evaluation-set rot.

**Out-of-corpus relevance** occurs when a query's judged-relevant units are absent from the (sub)corpus under test. Such queries can never score; they depress every configuration equally, mask true headroom, and — worse — their existence is invisible in the metrics themselves. The audit is a join: for every query, verify at least one judged-relevant unit exists in the corpus. In the motivating set the audit returned clean (144 of 148 covered; the 4 uncovered are exactly the unjudged ones; zero queries with relevance only outside the corpus), which upgrades every reported number from "MRR over the set" to "MRR over a set with no hidden holes". The audit is one page of code and is the difference between those two claims.

### Controlled comparison

Three rules make experimental numbers interpretable rather than merely reproducible:

1. **One variable per configuration.** An arm that changes chunk size and representation simultaneously yields a number that cannot be attributed. Configuration axes multiply; the discipline is to hold all but one fixed.
2. **Permanent configuration names, recorded parameters.** Result directories are the lab notebook; a renamed or silently modified configuration orphans every historical comparison. A changed prompt or parameter is a *new* name.
3. **Exact-reproduction exit tests.** When the measurement harness itself changes, the first requirement is digit-exact reproduction of a previously recorded table. Only that reproduction certifies that subsequent differences are properties of configurations rather than of the measuring instrument.

## Common failure modes

- **Reading means without win/loss counts** — regressions ship inside improvements.
- **Judging at chunk granularity** — the ground truth silently changes with every re-chunking; judge at a stable unit identity and collapse.
- **Ignoring the skipped-query count** — the denominator erodes and the metric inflates.
- **Comparing against a quoted historical baseline** — harness drift and environmental differences masquerade as effects.
- **Tuning against a saturated metric** — HitRate near ceiling cannot register improvements; choose the metric with headroom or enumerate the residual failures directly.
- **Trusting the set without a coverage audit** — precise numbers over hidden holes.

## Working rules

- Score against stable evaluation units; collapse system output to that identity before any metric.
- Report MRR, Recall@k, HitRate@k, and nDCG@k together; interpret their disagreement, do not average it away.
- Attach improved/unchanged/regressed counts versus an in-run baseline to every reported aggregate; persist per-query ranks.
- Audit coverage once per corpus change; report evaluated and skipped counts with every table.
- Gate harness changes on digit-exact reproduction of a recorded result.

## Related notes

- [[PROJ - RAG-TTC Chunk Lab - Chunking and Representation Experiments on a Free LLM Gateway]]
- [[ARTICLE - Retrieval Models - Lexical, Vector, and Hybrid Retrieval in RAG Systems]]
- [[ARTICLE - Reproducibility Engineering - Digests, Caches, Budgets, and Provenance]]
