# Study guide and course plan

This guide turns *Semantic Interfaces* into a structured independent-study course or seminar. It assumes one substantial reading session and one exercise or implementation session per week.

## Tracks

### Builder track

Prioritize Chapters 1–4, 12–19, 20–26, and 30. Implement a working PBUI incrementally. Read proofs for the contracts they impose, but postpone mechanization.

### Foundations track

Prioritize Chapters 5–18 and Appendices B–C. Rewrite every judgment and theorem in your own notation, complete proof exercises, and compare paper proofs with executable laws.

### Research track

Complete both tracks, then study open-world negation, decision procedures, multimethod coherence, dependency-complete caching, and mechanization. Reproduce one result in Lean, Coq, Agda, or Isabelle/HOL.

## Fourteen-week plan

| Week | Reading | Mathematical focus | Laboratory or written work |
|---:|---|---|---|
| 1 | Chapters 1–2 | Presentations as semantic relations; CLIM concepts | Annotate one existing UI with object/type/occurrence triples. |
| 2 | Chapters 3–4 | Separation of identity, subtype, translation, behavior, and binding | Implement the minimal `PresentationReference` and `accept` loop. |
| 3 | Chapter 5 | Sets, characteristic predicates, extensional equality | Prove union idempotence and absorption; encode smart constructors. |
| 4 | Chapter 6 | Relations, equivalence, quotient sets | Design semantic identity keys and adversarial equality tests. |
| 5 | Chapter 7 | Preorders, partial orders, lattices, closure | Compute nominal transitive closure and reject cycles. |
| 6 | Chapters 8–9 | Judgments, evidence, induction, denotational and operational semantics | Write derivation trees for three successful and three failed matches. |
| 7 | Chapters 10–11 | Type syntax, denotation, semantic subtyping | Implement the direct reference interpreter and prove its atom/union/intersection cases sound. |
| 8 | Chapters 12–14 | Atoms, capabilities, refinements, parameterization, identity | Add a named environment-dependent refinement with dependency evidence. |
| 9 | Chapters 15–16 | Partial functions, translation closure, proof-relevant matching | Implement bounded weighted path search and preserve path evidence. |
| 10 | Chapters 17–18 | Product orders, unique maximal methods, transition systems | Implement multimethod resolution and an at-most-once input context. |
| 11 | Chapter 19 | State invariants and simulation | Implement linked document selectors and prove coherence preservation. |
| 12 | Chapters 20–22 | Static/runtime boundary, compilation, caching | Add revision-aware memoization and a stale-evidence test. |
| 13 | Chapters 23–26 | React concurrency, accessibility, plugins, tests, authorization, explanations | Integrate the kernel with one real React view and build an explanation panel. |
| 14 | Chapters 27–30 and appendices | System selection, migration, proof scope | Write an architecture decision record selecting a feature profile and defending omissions. |

## Capstone options

### Capstone A — Practical PBUI

Implement Profile B from Chapter 27 in the supplied workbench: semantic identity, prepared selectors, direct translators, action rules, revalidation, and linked subjects. Deliver interaction tests and a migration note.

### Capstone B — Algebraic kernel

Extend the companion kernel with a complete decision procedure for a finite atom/capability fragment. State the supported grammar, prove soundness and completeness on paper, and use exhaustive finite-model tests as a second oracle.

### Capstone C — Mechanized proof

Formalize the direct matcher for atoms, union, intersection, and difference in a proof assistant. Prove matcher soundness and acceptance safety. Clearly mark host-language assumptions for refinement predicates.

### Capstone D — Dispatch coherence

Implement product-order multimethod dispatch with explicit preferences. Construct ambiguity examples, prove the unique-maximal determinism theorem, and design diagnostics that explain incomparable signatures.

### Capstone E — Incremental semantic index

Build a retained index of mounted or virtualized presentations. Compare DOM-only discovery, normalized-store discovery, and output-record-like retention. Define freshness and consistency guarantees.

## Assessment rubric

A strong project is evaluated on five independent dimensions:

1. **Semantic clarity** — relations are named and not conflated.
2. **Formal contract** — judgments, invariants, and soundness claims are explicit.
3. **Implementation fidelity** — successful runtime results satisfy those contracts.
4. **Failure design** — ambiguity, stale evidence, unknown definitions, and invalid persistence produce useful diagnostics.
5. **Scope discipline** — omitted features are intentional and documented rather than accidentally half-implemented.

## Recommended order for external reading

Begin with Pierce and Winskel for language metatheory, then Davey and Priestley for order theory. Read the CLIM II presentation and command chapters in parallel with Chapters 1–4. Use Castagna and Frisch's gentle semantic-subtyping paper before the full JACM treatment. Compare Typed Racket and Liquid Types for two different approaches to refinements. Study Clojure multimethods and Julia methods before implementing dispatch. Inspect Elixir's current set-theoretic type work for a modern production account of unions, intersections, negation, graduality, and decision-procedure engineering.
