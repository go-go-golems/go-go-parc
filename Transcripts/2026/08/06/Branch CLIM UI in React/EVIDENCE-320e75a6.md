# P08 Evidence Ledger

## Evidence labels

This artifact uses the following labels.

| Label | Meaning |
|---|---|
| **Definition** | Follows from the implemented representation or API contract. |
| **Example-tested** | Exercised by concrete deterministic tests. |
| **Property-tested** | Exercised over generated inputs with a recorded seed and shrinker. |
| **Finite-model-checked** | Exhaustively checked over an explicitly bounded model. |
| **Empirical** | Measured on one recorded runtime and host. |
| **Unchecked formal source** | A proof script is supplied but was not accepted by a checker in the assembly environment. |
| **Conjectural** | Proposed for later composition or research, not established here. |

None of the generated property tests are described as universal formal proofs.

## Claim ledger

| Claim | Level | Scope | Evidence | Assumptions / limits |
|---|---|---|---|---|
| Identity endpoints observe one shared resource. | Example-tested and definition | `IdentityCell` session | `test/policies.test.ts`, `results/laws.json` | Persistent binding identity belongs to P06. |
| Directed replacement has no backward repair. | Definition and example-tested | `row-selection-replacement/0.1` | policy metadata and tests | Other applications may define a different partial inverse under a different policy ID. |
| Successful symmetric right repair establishes consistency. | Property-tested and finite-model-checked | supported row/filter language over fixture rows | `results/laws.json` | Opaque predicates are preserved but not semantically evaluated. |
| Successful symmetric left repair establishes consistency. | Property-tested and finite-model-checked | same | `results/laws.json` | Inverse enumeration is bounded by `maxChoices`. |
| Stable exact consistent states remain unchanged. | Property-tested and finite-model-checked | exact-row fragment | `results/laws.json` | Equivalence is row-set equivalence. |
| Every returned ambiguous inverse satisfies the target relation. | Property-tested | generated station and exact filters | `results/laws.json` | Only returned choices are checked; enumeration is not complete for arbitrary languages. |
| Symmetric forward repair is idempotent. | Property-tested | generated supported inputs | `results/laws.json` | Deterministic normalization and stable fixture. |
| The asymmetric lens satisfies `get-put`. | Property-tested | supported generated selections | `results/laws.json` | Law equality is declared row-set equivalence. |
| The asymmetric lens satisfies exact-fragment `put-get`. | Property-tested | exact-row views | `results/laws.json` | Does not claim totality for station summaries or compounds. |
| Zero delta does not rewrite a consistent target. | Property-tested and example-tested | delta policy | laws and tests | Target equivalence uses normalized filter semantics. |
| Delta forward repair restores consistency. | Property-tested | generated deltas | `results/laws.json` | Delta does not encode arbitrary filter-language edits. |
| The intuitive toggle implementation violates a round-trip law. | Property-tested with shrinking | seeded negative control | counterexample corpus | Intentional failing control, not a production policy. |
| Scheduler order is independent of edge declaration order. | Example-tested | explicit priorities and IDs | `test/policies.test.ts` | Changing priority or IDs changes the semantic schedule. |
| Stable scheduler transactions commit atomically. | Example-tested | single-process synchronous policies | tests | No foreign async callbacks. |
| Unresolved ambiguity rolls back by default. | Example-tested | `dialog` strategy | tests | Host may configure different commit behavior. |
| Feedback simulator distinguishes convergence, oscillation, and bounded failure. | Example-tested | three supplied scenarios | tests and experiments | Does not decide general termination. |
| Symmetric and delta repair preserve the two unrelated fixture clauses. | Example-tested experiment | four scripted edits | `results/experiments.json` | Opaque clause meaning is not evaluated. |
| Delta repair uniquely preserves more clauses than symmetric repair. | Falsified | scripted enriched filter | negative finding | Both preserve all eight clause occurrences across four cases. |
| Delta repair carries more explicit edit provenance. | Definition and example-tested | add/remove/reorder cases | repair evidence in experiments | Provenance quality depends on caller-supplied delta. |
| Automatic ambiguity resolution captures user intent. | Not established | ranked fixture choices | experiment negative finding | Unique score is not user authority. |
| Normalization and scheduler timings have the recorded magnitudes. | Empirical | one host and runtime | `results/benchmark.json` | Not a guarantee; includes setup and evidence costs. |
| Lean exact-fragment theorems typecheck. | Unchecked formal source | `proofs/Main.lean` | source file only | Lean was unavailable during assembly. |
| Replicated topology converges. | Unsupported / out of scope | network replicas | typed unsupported trace results | P12 owns replicated merge. |

## Test inventory

Node test suites:

```text
identity reference
policy distinctions
delta repair
law versus usability controls
scheduler
research outputs
```

The compiled run currently reports 18 passing tests and no unexpected failures.

The law harness reports:

```text
passed:      14
failed:       1  expected negative control
unsupported:  0
```

The failing law is retained in the report so a green test summary does not hide the bad design. The ordinary test suite asserts that this specific control fails and that no production policy law unexpectedly fails.

## Shared trace coverage

| Trace | Requests | OK | Unsupported | Interpretation |
|---|---:|---:|---:|---|
| Identity link | 5 | 5 | 0 | Fully replayed by the bounded identity-reference adapter. |
| Transformed link | 3 | 3 | 0 | Fully replayed through selection/filter propagation. |
| Same subject | 3 | 2 | 1 | Sort/key comparison is supported; richer P01 identity behavior is not. |
| Refined selection | 5 | 1 | 4 | Control handshake only; selector subsystem belongs to P03. |
| Stale authority | 4 | 1 | 3 | Authority and occurrence lifecycle belong to P02/P05. |
| Concurrent topology | 7 | 1 | 6 | Replication belongs to P12. |

Typed unsupported responses are counted as boundary evidence, not as successful feature coverage.

## Benchmark protocol

- Timer: `performance.now`.
- Normalization: 5 warm-ups, 25 samples.
- Scheduler: 3 warm-ups, 15 samples.
- Correctness gates execute in each measured function.
- Environment is recorded in the JSON result.
- No claim is made about browser rendering performance.

## Trusted and foreign parts

### Trusted within the artifact

- filter AST parsing and normalization;
- finite fixture denotation;
- policy metadata and dispatch;
- repair outcome structure;
- deterministic queue ordering;
- law generators and shrinkers;
- JSONL serialization.

### Foreign or bounded assumptions

- meaning of opaque filter predicates;
- user authority to choose an ambiguous repair;
- lifecycle and authorization of component endpoints;
- persistent binding IDs;
- network replication;
- fairness and latency of asynchronous host systems;
- React host and browser event semantics.

## Reproduce

Full TypeScript rebuild and checks:

```bash
npm run verify
```

Compiled artifact only:

```bash
npm run verify:compiled
```
