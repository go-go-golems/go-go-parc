# P08 Experiments and Measurements

## 1. Method

The experiment suite is deterministic and uses seed `20260808`. It is designed to compare semantic choices, not to claim population-level HCI results.

The common worked case links:

```text
table.rowSelection <-> pipeline.filter
```

The initial selection is:

```json
{"rows":["row-7","row-9"]}
```

The target filter is deliberately richer than a row selection:

```json
{
  "op":"and",
  "args":[
    {"op":"opaque","id":"owner","label":"owner=analyst"},
    {"op":"opaque","id":"quality","label":"quality!=rejected"},
    {"op":"inRows","rows":["row-7","row-9"]}
  ]
}
```

The two opaque clauses stand for intent that originated in the pipeline rather than in the table selection. The reference evaluator preserves them but does not interpret their truth.

Four designs are compared:

1. directed replacement;
2. partial asymmetric lens;
3. symmetric envelope-aware repair;
4. delta-aware envelope repair.

The scripted edit cases are add, remove, reorder-only, and replace-all.

## 2. Hypotheses

| ID | Claim | Falsification criterion | Result |
|---|---|---|---|
| H1 | A first-class link-mode distinction prevents equality mistakes and feedback bugs. | A directed policy accepts an invented inverse, identity uses recursive setters, or cycles are silently suppressed. | Supported in the implemented fragment. |
| H2 | Partial repairs with typed conflicts are more honest than arbitrary total inverses. | A station summary has one defensible inverse or the API silently commits an arbitrary preimage. | Supported. |
| H3 | Delta-aware repair preserves selection/filter intent. | Delta repair loses unrelated clauses or provides no additional provenance over replacement. | Supported, with an important qualification. |
| H4 | Lens laws do not replace usability and conflict UX. | Every lawful lens is behaviorally unsurprising and every intuitive handler is lawful. | Supported. |

These results are bounded to the fixture and implementation. They are not universal theorems about all lenses or UI links.

## 3. Selection-to-filter comparison

### 3.1 Clause preservation

Across four edit cases, the enriched target contains two unrelated clauses.

| Design | Preserved clauses per case | Total preserved across cases | Characterization |
|---|---:|---:|---|
| Directed replacement | 0 / 2 | 0 | Discards the target representation and derives an exact filter. |
| Asymmetric lens | 0 / 2 | 0 | Lawful on its exact fragment, but `get` still replaces the richer view. |
| Symmetric repair | 2 / 2 | 8 | Replaces only the inspectable selection clause. |
| Delta repair | 2 / 2 | 8 | Preserves the same envelope and records the edit delta. |

The result falsifies a stronger version of the delta hypothesis: delta repair did not uniquely outperform symmetric envelope-aware repair on clause preservation. Its distinctive benefit was provenance and edit granularity.

### 3.2 Add row

Edit:

```text
before: row-7, row-9
after:  row-7, row-9, row-11
```

Delta:

```json
{"add":["row-11"],"remove":[]}
```

Replacement and asymmetric `get` discard both opaque clauses. Symmetric and delta repair preserve them.

### 3.3 Remove row

Edit:

```text
before: row-7, row-9
after:  row-9
```

Delta:

```json
{"add":[],"remove":["row-7"]}
```

The preservation result matches the add case. Delta evidence identifies the removed row rather than only the final state.

### 3.4 Reorder only

Edit:

```text
before: row-7, row-9
after:  row-9, row-7
```

The consistency relation uses row-set equivalence, so the target filter is already extensionally consistent.

- symmetric repair returns `unchanged`;
- delta repair also returns `unchanged`, but records the reorder intent and reports that the target representation cannot express it;
- replacement and the asymmetric lens rewrite the target representation despite no denotational change.

This case demonstrates why an edit can matter even when the extensional relation remains true.

### 3.5 Replace all

A broad selection replacement again preserves unrelated clauses under symmetric and delta repair. Delta evidence distinguishes the operation from a series of unrelated state snapshots.

## 4. Lawfulness versus visible behavior

### 4.1 Lawful but surprising

`lawful-surprising-set-lens/0.1` treats selections as sets. Its `get` sorts and deduplicates rows.

```text
source: row-9, row-7, row-7
view:   row-7, row-9
```

The round trip is lawful under set equivalence:

```text
{row-9,row-7,row-7} ~= {row-7,row-9}
```

It is not structurally equal. A UI that visibly represents order or duplicates can therefore surprise a user even though the stated law holds.

### 4.2 Intuitive but unlawful

The negative control implements a click-like toggle as though it were a `put` operation. The minimized failure is:

```json
{
  "source":{"rows":[]},
  "view":{"selected":false}
}
```

A correct `put` should leave the source unchanged. The toggle adds `row-7`, violating `put(s, get(s)) = s`.

The lesson is not that toggles are bad. It is that an event handler and a lens update have different contracts.

## 5. Feedback cycle study

The simulator uses a deterministic work queue and no mutable "currently propagating" suppression flag.

| Scenario | Result | Steps | Diagnostic |
|---|---:|---:|---|
| Trim then lowercase | Stable | 5 | Reaches `a=alpha`, `b=alpha`. |
| Increment modulo three | Oscillation | 8 | A prior global state repeats. |
| Unbounded increment | Bounded failure | 24 | No state repeats before the step limit. |

The deterministic scheduler makes these outcomes reproducible. It does not transform a non-convergent system into a convergent one.

## 6. Ambiguous inverse study

The filter:

```json
{"op":"stationIn","stations":["A","B"]}
```

has several row-selection preimages in the five-row fixture. The inverse enumerator produces nine bounded choices in the main scenario.

Four host strategies are compared:

| Strategy | Automatic commit | Explicit decision | Refusal | Scripted decision-cost proxy |
|---|---:|---:|---:|---:|
| Automatic | 1 | 0 | 0 | 0.3 |
| Ranked | 0 | 1 | 0 | 1.0 |
| Dialog | 0 | 1 | 0 | 2.5 |
| Refuse | 0 | 0 | 1 | 0.2 |

The decision-cost values are scenario parameters, not measured human completion times. They are included only to exercise policy comparison.

Automatic mode commits only if the highest score is unique. This still depends on application-specific ranking authority. A unique numeric score is not proof of user intent.

## 7. Information-loss evidence

A station summary can be consistent with several row selections. For station A, the fixture contains `row-7` and `row-11`. A summary can therefore preserve station membership while losing which row occurrence was intended.

The experiment checks that:

- the consistency relation may hold;
- evidence contains information-loss facts;
- backward repair exposes multiple choices;
- every returned choice satisfies the requested relation.

## 8. Benchmarks

Environment recorded in `results/benchmark.json`:

```text
Node:       v22.16.0
Platform:   linux x64
CPU:        Intel Xeon Platinum 8370C, 5 visible CPUs
Memory:     6,367,956,992 bytes
Timer:      performance.now
```

### 8.1 Filter normalization

25 measured samples after 5 warm-ups:

| Compound clauses | Mean ms | Median ms | p95 ms | Std dev ms |
|---:|---:|---:|---:|---:|
| 10 | 0.279 | 0.131 | 1.557 | 0.541 |
| 100 | 0.711 | 0.571 | 1.276 | 0.296 |
| 1,000 | 3.416 | 3.385 | 3.574 | 0.096 |
| 5,000 | 15.780 | 14.545 | 15.378 | 6.291 |

### 8.2 Scheduler chains

15 measured samples after 3 warm-ups:

| Edges | Mean ms | Median ms | p95 ms | Std dev ms |
|---:|---:|---:|---:|---:|
| 10 | 0.698 | 0.548 | 2.066 | 0.423 |
| 100 | 16.766 | 13.569 | 39.485 | 8.124 |
| 500 | 267.330 | 270.844 | 275.892 | 6.950 |

The benchmark measures transaction setup, repair evidence, normalization, and propagation. It is not a microbenchmark of only the relation function. It is one-host empirical evidence, not a performance guarantee.

## 9. Negative findings

The generated report records five negative findings:

1. Delta repair did not uniquely outperform symmetric repair on envelope-clause preservation.
2. A lawful lens can violate visible ordering expectations when its equivalence is coarser than the presentation.
3. A deterministic scheduler cannot make a non-convergent cycle converge.
4. Automatic conflict resolution needs application-specific authority; a score alone is insufficient.
5. Finite inverse enumeration over five rows is not a scalable general inverse algorithm.

These findings are part of the deliverable rather than defects to conceal.

## 10. Reproduction

```bash
npm run verify:compiled
```

Generated outputs:

```text
results/laws.json
results/experiments.json
results/benchmark.json
results/trace-replay.json
counterexamples/law-counterexamples.json
```
