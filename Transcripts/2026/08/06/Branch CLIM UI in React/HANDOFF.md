# P06 handoff note

## Solid results

The semantic kernel is small and independently implemented twice:

1. validate typed port declarations and identity links;
2. form the generated equivalence relation;
3. emit disjoint contract-homogeneous classes and a total projection;
4. assign persistent external binding identities separately;
5. allocate one runtime cell per persistent class;
6. expose projections, explanations, and factorization.

The reference graph-closure compiler and optimized union-find compiler produce the same normalized partition in all current tests, including 2,000 seeded generated graphs. The optimized registry checks itself against the reference compiler by default.

The runtime makes merge and unlink initialization explicit. A failed candidate edit does not replace the installed plan. Link declarations and provenance are retained, so deletion is defined as removing one declaration and recompiling rather than attempting to subtract an equivalence from union-find.

The JSONL adapter, serializable plan, example capsule, counterexamples, and dependency-free demo are ready for independent use.

## Provisional results

Persistent binding identity uses anchors, overlap, birth ordinals, and stable fresh hashes. This policy behaves well in the current experiments but is not categorically determined. A product with user-named or server-issued bindings may choose another policy.

The compatibility relation uses definitional equality of all declared identity fields. This is safe and simple. It may be stricter than necessary if later work defines variance, delegated authority, or compatible update algebras.

The runtime uses synchronous mutable cells. It is adequate for demonstrating projection and aliasing, not for making claims about distributed or asynchronous scheduling.

The React adapter is a hostable demonstration rather than the verified execution path. The dependency-free `web/` demo uses the same compiled semantic core and should be used for reproducible evaluation.

## Non-composable claims

Do not use identity links for:

- table selection to pipeline filter;
- primary document to derived document;
- event streams;
- unequal bidirectional representations;
- replicated topology without a P12 merge protocol.

Do not persist union-find representatives. Do not infer an unlink value from the partition. Do not let a component maintain an unsynchronized shadow value and then cite the quotient invariant.

## Reliance summary

A consumer may rely on:

- class totality and disjointness after successful compilation;
- contract homogeneity of every class;
- equality of projections for every accepted link endpoint pair;
- one allocated cell per persistent binding class;
- typed rejection of incompatible identity links;
- typed rejection of missing merge or unlink policies where required.

A consumer may not rely on:

- global transactionality;
- distributed convergence;
- fairness or scheduling;
- proof-carrying TypeScript compilation;
- stable IDs across arbitrary semantic migrations;
- transformed-link consistency.

## Reimplementation priority

Before adoption, independently reimplement or check the five-step semantic kernel: graph validation, equivalence closure, class normalization, total projection, and endpoint-equality checks. The persistence and allocation layers should then be compared against application-specific requirements rather than adopted as mathematical necessities.
