---
title: "PBUI Research Project Index"
subtitle: "Subsystem briefs, sequencing, and assignment guidance"
author: "PBUI Research Program"
date: "2026-08-04"
lang: en-US
documentclass: article
geometry: margin=0.8in
fontsize: 10pt
toc: true
toc-depth: 3
numbersections: true
colorlinks: true
linkcolor: blue
urlcolor: blue
---

# Project list

| Project | Track | Principal artifact |
|---|---|---|
| [P01: Semantic Identity and the Subject Registry](projects/P01-semantic-identity-subject-registry.md) | Semantic foundations | A reference model and API for stable semantic subjects that does not confuse JavaScript references, values, aliases, or rendered occurrences. |
| [P02: Occurrence Semantics and the Concurrent React Adapter](projects/P02-occurrence-lifecycle-react-adapter.md) | Semantic foundations / runtime boundary | A renderer-independent occurrence model plus a React adapter whose committed registrations refine that model. |
| [P03: Inspectable Typed Selectors and Selection Evidence](projects/P03-typed-selector-language-evidence.md) | Query semantics | A typed selector AST, reference evaluator, and proof-relevant candidate format with a controlled foreign-predicate boundary. |
| [P04: Recursive Rules, Fixed Points, and Provenance](projects/P04-recursive-rules-fixed-points-provenance.md) | Query semantics / formal foundations | A finite relational rule engine with explicit least-fixed-point semantics, provenance, and an optimized evaluator checked against the reference closure. |
| [P05: Operations, Capabilities, and Invariant-Preserving Affordances](projects/P05-operations-capabilities-invariants.md) | Operations and authority | An operation model separating menu affordances from authoritative transitions and making preconditions, effects, and invariants explicit. |
| [P06: Typed Ports and the Binding Quotient Compiler](projects/P06-typed-ports-binding-quotient-compiler.md) | Open systems / wiring | A typed wiring compiler that turns identity-link equations into canonical binding classes and proves linked ports observe one runtime resource. |
| [P07: Open Components, Plugin Signatures, and Composition](projects/P07-open-components-plugin-composition.md) | Open systems / modularity | A component signature and plugin compiler separating interface gluing from behavior and testing associativity, compatibility, and schema evolution. |
| [P08: Bidirectional Links and Consistency Restoration](projects/P08-bidirectional-links-consistency-restoration.md) | Synchronization semantics | A link-policy laboratory making consistency relations, repair direction, partiality, ambiguity, and lens laws explicit. |
| [P09: Coalgebraic Interaction Machines](projects/P09-coalgebraic-interaction-machines.md) | Interaction semantics | A small machine IR and runtime for PBUI workflows, with checks for safety, cancellation, resolution, and behavioral equivalence. |
| [P10: Algebraic Interaction Programs and Effect Handlers](projects/P10-algebraic-effects-workflow-handlers.md) | Interaction programming | A typed interaction-program language with handlers for browser execution, deterministic simulation, tracing, and static effect analysis. |
| [P11: Incremental and Differential Evaluation](projects/P11-incremental-differential-evaluation.md) | Runtime / optimization | A reference evaluator and an incremental runtime whose updates, deletions, evidence, and recursive results are continuously checked for from-scratch consistency. |
| [P12: Local-First Replicated Bindings and Topology](projects/P12-local-first-replicated-bindings-topology.md) | Replication / coordination | A replicated workspace model for link declarations, unlinking, values, deletion, and conflicts, with explicit convergence and coordination claims. |
| [P13: Explanation, Accessibility, and Proof-Relevant Interaction](projects/P13-explanation-accessibility-proof-relevant-interaction.md) | Human factors / semantics | A renderer-neutral explanation model and accessible interaction laboratory for selection, authority, staleness, linking, conflicts, and machine phase. |
| [P14: Mechanized Semantic Kernel and Proof-Carrying Compilation](projects/P14-mechanized-semantic-kernel-proof-carrying-compilation.md) | Formal verification | A proof-assistant development of typed subjects, positive selection, typed port equations, quotient bindings, and certificates checked by an executable bridge. |
| [P15: Conformance, Model-Based Testing, and Comparative Benchmarking](projects/P15-conformance-model-based-testing-benchmarking.md) | Validation / integration science | A black-box conformance laboratory with reference micro-models, generated traces, shrinking, metamorphic laws, reproducible benchmarks, and capability-aware reports. |

# Assignment guidance

## Foundations and semantics

- **P01** suits students interested in identity, data modeling, and typed evidence.
- **P03** suits programming-languages or database students who want an inspectable query core.
- **P04** suits logic and database students studying recursion, fixed points, and provenance.
- **P14** suits proof-assistant students and should begin after its team reads P01, P03, and P06, while remaining implementation-independent.

## Components and interaction

- **P02** studies the difficult boundary between semantic objects and concurrent React lifecycles.
- **P06** is the focused `PortBindingResolverRegistry` project: typed port contracts, generated equivalence, quotients/coequalizers, resource allocation, and dynamic unlinking.
- **P07** studies independently developed open components and plugin substitution.
- **P08** handles unequal representations and must not be merged conceptually with P06 identity links.
- **P09** studies explicit interaction state and behavioral equivalence.
- **P10** studies effectful authoring and its relationship to P09 machines.

## Runtime, distribution, and evaluation

- **P05** studies operation authority and invariant-preserving affordances.
- **P11** studies optimized maintenance while preserving from-scratch meaning.
- **P12** studies replicated declarations, convergence, conflicts, and coordination.
- **P13** studies explanation and cross-modality accessibility as semantic projections.
- **P15** builds the neutral comparison lab and should coordinate fixture changes but not dictate internal APIs.

# Recommended cohort arrangements

For a cohort of five teams, assign one project from each cluster:

1. semantic kernel: P01/P03/P04;
2. component boundary: P02/P06/P07/P08;
3. interaction: P05/P09/P10;
4. runtime/distribution: P11/P12/P14;
5. human/validation: P13/P15.

For a cohort of ten or more teams, run all projects except that P14 may start two weeks later, using frozen initial subsets from P03 and P06.

For individual doctoral rotations, P01, P02, P03, P06, P09, and P13 have the smallest initial dependency surface. P04, P11, P12, and P14 are better suited to longer rotations.

# First-pass sequencing

The projects are independent in code but not in conversation. Suggested seminar order:

```text
Weeks 1-2: P01, P02, P03, P06 present semantic objects
Weeks 3-4: P04, P05, P07, P08 present laws and counterexamples
Weeks 5-6: P09, P10, P11, P12 present dynamics and change
Week 7:    P13 presents user-visible status taxonomy
Week 8:    P14 presents proof-kernel scope
Week 9:    P15 freezes the comparison protocol
Weeks 10+: external reproduction and capsule freeze
```

The protocol may gain additive fields before the freeze, but project meanings should not be forced into one common implementation model.

# Expected project size

A project is intentionally smaller than a complete PBUI platform. A good submission often contains:

- 500-2,500 lines of reference implementation;
- 1,000-6,000 lines of experimental implementation or proof;
- 30-150 generated properties or formal lemmas;
- 5-20 minimized counterexamples;
- one focused React or textual demonstration;
- one versioned capsule and reproducibility script.

These are orientation ranges, not quotas. Semantic precision and negative results matter more than line count.

# Supervisor checkpoints

At each checkpoint, ask:

1. What exact statement would make the project fail?
2. Is the current implementation the definition or an interpreter of a separate model?
3. What is the smallest foreign assumption?
4. Which user-visible state cannot yet be explained?
5. Which adjacent project might interpret the shared boundary differently?
6. What evidence would justify narrowing or rejecting the design?

# Deliverable map

- `00-PROGRAM-HANDBOOK.md` - overall research design and governance.
- `projects/*.md` - the fifteen detailed individual briefs.
- `shared/INTEROP-CONTRACT.md` - experimental process and data seam.
- `shared/EVALUATION-RUBRIC.md` - scoring and evidence discipline.
- `shared/PHASE-2-COMPOSITION-MAP.md` - controlled later integrations.
- `fixtures/` - common domain, occurrences, trace samples, and manifest schema.
- `pdf/` - typeset counterparts generated from all principal Markdown documents.
- `PBUI-RESEARCH-PROJECTS-COMPENDIUM.md` - combined printable source.
