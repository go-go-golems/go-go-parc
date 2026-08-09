# P08 Handoff Note

## Solid results

The smallest kernel another team can rely on is:

```text
versioned policy metadata
+ consistency evidence
+ Repair<T>
+ explicit conflict strategy
+ deterministic schedule trace
```

The implementation makes identity reference, directed derivation, asymmetric lens, symmetric consistency, and delta repair distinct in code. Identity uses one shared cell, not recursive setters. Directed backward propagation is rejected. Partial inverses return typed choices. Stable successful repairs are checked to remain unchanged, and successful repairs are checked to establish consistency in the supported fragment.

The generated law harness, finite checks, 18 Node tests, trace replay, capsule validation, and benchmark correctness gates all run through `npm run verify:compiled`. The seeded unlawful toggle reliably produces a minimized counterexample.

## Provisional results

The filter language is intentionally small. Opaque predicates are preserved but treated as true by the reference evaluator. Station-summary inverse choices are enumerated over five fixture rows and are not a scalable query planner.

The deterministic scheduler has an explicit order and atomic rollback, but it is single-process and synchronous. It does not establish fairness under asynchronous effects. Conflict scores are deterministic heuristics, not proof of user preference.

The React adapter has been syntax-checked against a shim and shares the semantic kernel, but it was not bundled against a production React version in this environment. The dependency-free browser laboratory is the executable UI reference.

`proofs/Main.lean` is plausible finite proof source but was not checker-validated because Lean was unavailable. Do not cite it as a checked theorem.

## Non-composable or intentionally excluded results

P08's identity-reference adapter is only a session-level alias used to compare identity and transformed links. It does not replace P06's persistent quotient compiler. It supports one bounded identity link and uses a documented left-initialization rule when the common trace omits a merge policy.

P08 does not implement component signature discovery, authorization, occurrence staleness, or replicated topology. Typed unsupported trace responses mark these boundaries. In particular, replicated merge must not be inferred from lens laws.

## Worst future integration mistake

The worst mistake is selecting identity mode because two endpoint payloads have the same TypeScript shape. Identity requires one semantic resource, compatible update algebra, authority, lifetime, and conflict policy for preexisting values. Unequal representations should use directed or repair-based policies.

The second-worst mistake is composing policies without making scheduler order explicit. Repair functions can be individually lawful while their cycle is oscillating or order-sensitive.

## Counterexample that most changed the design

The toggle negative control made the edit/state distinction concrete. A click handler that feels natural can be an invalid `put`, because it changes state when the requested view is already satisfied. This led to explicit delta policies rather than pretending every event is a desired-state lens update.

## Reimplementation recommendation

Before production adoption, independently reimplement:

1. the row/filter consistency denotation and inverse choice generator;
2. the scheduler's repeated-state detection and commit semantics;
3. the conflict-ranking authority boundary.

Compare both implementations through the JSONL capsule and generated law fixtures.
