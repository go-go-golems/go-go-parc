# Evidence ledger

| Claim | Status | Evidence | Boundary |
|---|---|---|---|
| Every declared port occurs in exactly one semantic class | Property-tested | `test/compiler.test.mjs`, `test/generated.test.mjs` | Finite valid graphs |
| Incompatible identity contracts are rejected | Example- and generated-tested | `test/contracts.test.mjs`, `test/compiler.test.mjs`, adapter tests | Declared equality policy |
| Optimized and reference compilers agree | Property-tested | 2,000 seeded graphs in `test/generated.test.mjs`; per-compile reference check | Shared validation and normalization are trusted common code |
| Link order and redundant equations do not change the quotient relation | Property-tested | `test/compiler.test.mjs` | Relation comparison ignores declaration provenance |
| Linked endpoints observe one process-local resource | Example-tested | `test/registry.test.mjs`, browser interaction smoke | Components must use generated projections |
| Unlinking requires explicit initialization | Example-tested | registry and adapter tests | Single-process topology edits |
| Persistence preserves the relation up to binding-ID renaming | Example-tested | `test/persistence.test.mjs` | Replayed declarations, same contract registry |
| A class-respecting finite interpretation factors through bindings | Example-tested | `registry.factor` tests and UI experiment | Supplied equality predicate is trusted |
| Quotient factorization and widget equality | Proof source included, not checked here | `proofs/Main.lean` | Type-indexed finite port model |
| Compile latency observations | Empirical | `benchmarks/results.json` | Host-specific Node microbenchmark |
| Visual and keyboard interaction | Browser smoke-tested during assembly | `web/`, `docs/demo-screenshot.png` | Chromium smoke; no formal accessibility audit |

## Verification snapshot

The assembled artifact completed:

```text
TypeScript build: passed
Node tests: 20 passed, 0 failed
Generated graph trials: 2,000
JSONL fixture parsing: identity, transformed, and concurrent traces answered
Browser module smoke: rendered without console/page errors
Browser interaction smoke: identity link, shared write, invalid-link diagnosis, random differential experiment
Manifest/schema validation: passed
Lean execution: not run; executable unavailable
```

Evidence labels are deliberately not collapsed. A test is not a proof, and an included proof source is not a checked proof until a trusted Lean toolchain accepts it.
