# Executable reference kernel

This directory contains a dependency-free implementation of the principal calculus developed in *Semantic Interfaces*.

## Run the included laws

The compiled JavaScript is included, so the executable law suite needs only a recent Node.js runtime:

```bash
npm test
```

To rebuild from TypeScript, make `tsc` available and run:

```bash
npm run verify
```

## Files

- `presentation-type-kernel.ts` — reference implementation.
- `presentation-type-kernel.test.ts` — executable examples and law-oriented tests.
- `dist/` — generated JavaScript, source maps, and declarations.
- `tsconfig.json` — strict compiler configuration.

## Implemented concepts

The kernel includes:

- atomic presentation references;
- nominal subtyping with cycle rejection and transitive closure;
- static and environment-dependent capabilities;
- union, intersection, base-relative difference, and named refinements;
- semantic identity and revision tokens;
- proof-relevant direct matching;
- dependency evidence for positive and negative refinement facts;
- bounded, weighted translator-path search;
- multimethod-style dispatch with product specificity and ambiguity detection;
- at-most-once input contexts;
- linked subject cells for coordinated views.

The central executable judgment is:

```text
registry ; environment ⊢ reference : requested-type ▹ evidence
```

`RegistrySnapshot.direct` implements direct membership. `RegistrySnapshot.match` extends it with translator reachability and records the path used.

## Deliberate limitations

This is a reference interpreter, not a production package. It deliberately omits:

- React components and DOM event handling;
- persistent serialization and plugin loading;
- complete semantic-subtype decision for arbitrary refinements;
- BDD normalization;
- recursive types;
- asynchronous capability and refinement predicates;
- proof-assistant-checked metatheory;
- authorization enforcement.

`isSubtype` is sound for the rules it proves but intentionally incomplete. A `false` answer can mean either “not a subtype” or “not established by this small proof procedure.” The textbook explains how to replace it with a stronger finite-model, clause, SAT, BDD, or mechanized implementation.

## Reading the tests

The law suite builds a project workbench and checks:

1. Boolean smart-constructor identities.
2. Nominal and capability inheritance.
3. Active/owned refinements and negative evidence dependencies.
4. Cross-presentation semantic identity.
5. Selection of a cheaper two-edge translation over a costlier direct edge.
6. More-specific multimethod selection.
7. Context-sensitive methods.
8. At-most-once acceptance.
9. Link-group coherence under link, update, and unlink.
10. Registry-time rejection of subtype cycles.

The tests are executable specifications. They increase confidence but do not replace universal proofs or machine-checked verification.
