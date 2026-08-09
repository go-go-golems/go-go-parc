# P08 Composition Reliance Statement

Consumers may rely on the following, within policy version `0.1` and the stated fixture fragment:

1. Every response is a typed `Repair` outcome or a typed protocol status.
2. `updated` and `unchanged` outcomes include consistency evidence.
3. Successful production-policy repairs are tested to establish their declared relation in the supported filter fragment.
4. Ambiguous inverse repairs expose choices and information-loss evidence rather than silently choosing inside the policy.
5. Policy metadata declares kind, endpoint sorts, supported directions, laws, assumptions, and opaque callbacks.
6. The scheduler uses an explicit deterministic edge order and reports its schedule signature.
7. Unknown protocol operations return `unsupported` rather than being ignored.

Consumers must not rely on:

- persistent identity quotienting or binding IDs;
- completeness of inverse enumeration;
- semantic evaluation of opaque filter clauses;
- network-replica convergence;
- user preference inferred from repair scores;
- asynchronous fairness or cancellation behavior;
- the unchecked Lean source as accepted proof evidence.

Foreign assumptions:

- P01 provides canonical cross-form semantic identity when sort/key equality is insufficient.
- P02 and P05 provide occurrence freshness and authority.
- P06 provides persistent identity classes and topology edits.
- P07 may provide component and port signatures.
- P09 may provide the interaction machine that creates or resolves links.
- P12 provides replicated merge.
