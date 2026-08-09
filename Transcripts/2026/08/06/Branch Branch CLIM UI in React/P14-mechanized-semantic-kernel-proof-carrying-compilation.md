---
title: "P14: Mechanized Semantic Kernel and Proof-Carrying Compilation"
subtitle: "Formalize a deliberately small PBUI core and connect checked theorems to executable binding and selection artifacts"
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

# Project brief

| Field | Assignment |
|---|---|
| Project | **P14: Mechanized Semantic Kernel and Proof-Carrying Compilation** |
| Track | Formal verification |
| Suggested team | 1-2 students with Lean, Coq, Agda, Isabelle, proof assistants, or mechanized semantics experience |
| Nominal duration | 11-13 weeks |
| Primary result | A proof-assistant development of typed subjects, positive selection, typed port equations, quotient bindings, and certificates checked by an executable bridge. |

## Executive framing

The broader PBUI architecture contains too many host-language, browser, network, and human factors to verify monolithically. A more credible strategy is to identify a small semantic kernel, mechanize its definitions and central theorems, and make optimized or foreign implementations produce artifacts checked against that kernel.

This project should resist two opposite failures: formalizing an elegant toy with no connection to the experimental API, and encoding the implementation so literally that the proof merely restates code. The target is a small model that makes sort safety, candidate soundness, generated link equivalence, and equal binding observations precise, then connects those results to a JSON or certificate format usable by P03, P06, and P15.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- What is the smallest kernel that captures typed subjects, facts, positive selectors, evidence, ports, link declarations, equivalence closure, and interpretation?
- Should bindings use quotients, canonical finite partitions, or both with an equivalence theorem?
- Which theorems express selector soundness without formalizing all JavaScript?
- How can an optimized compiler emit a certificate checked by the kernel rather than being trusted?
- What assumptions are needed to connect extracted or mirrored definitions to a TypeScript runtime?
- Which host features must remain foreign, and how are those assumptions represented?
- How should engineering claims map to theorem statements so proof scope is not overstated?

## Falsifiable hypotheses

- A sort-indexed finite kernel can prove the most important selection and identity-link properties with modest proof-assistant effort.
- Canonical partitions are executable and quotient types are conceptually clean; proving their correspondence yields a useful bridge.
- A binding compiler can emit a compact certificate consisting of a projection map plus edge checks.
- Selector soundness can be proved for a positive typed fragment while opaque predicates remain explicit assumptions.
- Mutation testing of certificates will expose whether the checker validates meaningful structure.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- Verifying React, browsers, Redux, network stacks, or arbitrary TypeScript.
- Formalizing all fifteen projects.
- Using `admit`, `sorry`, or unreported axioms in claimed theorems.
- Treating finite testing as a substitute for proof.
- Generating production code before the model stabilizes.

## Shared laboratory setting

Every project is self-contained, but all teams use the same deliberately small domain so that results can be compared without importing another team's implementation.

The domain is an analytical workbench containing four independently developed components:

- a **source browser** that presents documents and fields;
- a **chart** with a primary-document port and a row-selection port;
- a **pipeline editor** with a primary-document port, a filter port, and an output-document port;
- a **table** with a primary-document port and a row-selection port.

The fixed fixture contains documents `doc-a`, `doc-b`, and deleted tombstone `doc-z`; fields `station`, `temperature`, `pressure`, and `internal_id`; users `analyst`, `admin`, and `viewer`; views `chart-1`, `pipeline-1`, `table-1`, and `browser-1`; multiple occurrences of the same semantic field; immutable copies with different JavaScript references; one stale occurrence; one unauthorized operation; and one deliberately ambiguous bidirectional update.

The mandatory user-visible traces are:

1. **Same subject, different occurrence.** Select `temperature` from either a field chip or a table header and obtain the same semantic subject.
2. **Refined selection.** Ask for a non-internal numeric field owned by the currently selected document.
3. **Identity linking.** Link the chart and pipeline primary-document ports, then switch the document from either component.
4. **Transformed linking.** Translate a table row selection into a pipeline filter and expose ambiguity rather than silently guessing.
5. **Staleness and authority.** Render an action, revoke its authority or retire its occurrence, then attempt to commit it.
6. **Concurrent topology.** On two replicas, link and unlink overlapping groups while offline, then merge.

A team may add fixtures, but it may not remove or weaken these six traces.

## Common artifact boundary

Each submission exposes a deterministic command-line adapter over JSON Lines. It may implement only relevant messages, but unsupported messages return a typed `unsupported` result.

```ts
interface LabEnvelope<T = unknown> {
  protocol: "pbui-research/0.1";
  requestId: string;
  kind: string;
  payload: T;
}

interface LabResult<T = unknown> {
  protocol: "pbui-research/0.1";
  requestId: string;
  status: "ok" | "rejected" | "unsupported" | "error";
  payload?: T;
  explanation?: Explanation;
}
```

This adapter is an experimental seam for replay, comparison, and later substitution. It is not the proposed production API.

## Formal object of study

Choose a proof assistant and define:

- semantic sorts $S$ and sort-indexed references $\operatorname{Ref}:S\to\mathsf{Type}$;
- finite typed facts and a positive query judgment;
- proof-relevant candidate derivations;
- port types and sort-indexed ports $\operatorname{Port}:S\to\mathsf{Type}$;
- typed link declarations and the generated equivalence relation $\sim$;
- either the quotient $Q_s=\operatorname{Port}(s)/{\sim}$ or a canonical finite partition;
- a binding interpretation $v_s:Q_s\to V_s$ and port observation $v_s\circ q_s$.

Representative target theorems are:

$$\operatorname{derive}(q,D,r,e)\Longrightarrow r\in\llbracket q\rrbracket_D,$$

$$p\sim q\Longrightarrow \operatorname{project}(p)=\operatorname{project}(q),$$

and therefore

$$p\sim q\Longrightarrow f(\operatorname{project}(p))=f(\operatorname{project}(q))$$

for any interpretation $f$. State theorem assumptions and computational relevance explicitly.

## Minimum API and executable artifact

```lean
inductive Sort | document | field | selection
inductive Port : Sort -> Type
inductive Linked : {s : Sort} -> Port s -> Port s -> Prop

abbrev Binding (s : Sort) := Quotient (portSetoid s)
def project {s} (p : Port s) : Binding s := Quotient.mk _ p

theorem linked_same_binding {s} {p q : Port s}
  (h : Linked p q) : project p = project q := Quotient.sound h

theorem linked_same_widget {p q : Port .document}
  (h : Linked p q) (f : Binding .document -> Widget) :
  f (project p) = f (project q) := congrArg f (linked_same_binding h)
```

Expose a checker command such as `pbui-kernel check binding-certificate.json` plus machine-readable theorem/build metadata.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Kernel freeze

Write a one-page trusted-base and theorem inventory; choose finite representations, decidable equality, and foreign assumptions.

### Mechanized definitions

Formalize sorts, references, facts, selectors, evidence, ports, links, equivalence closure, partitions/quotients, and interpretations.

### Core theorems

Prove selector type/soundness, equivalence laws, linked-equal-projection, linked-equal-observation, and certificate soundness for the chosen fragment.

### Executable certificate bridge

Define a language-neutral certificate; implement encoder from a small TypeScript or reference compiler and checker invocation.

### Countermodel collaboration

Use failed proof attempts and finite counterexamples to refine P03/P06 contracts rather than weakening theorem statements silently.

### Proof audit

Document trusted axioms, extraction/FFI boundary, theorem-to-claim map, proof statistics, and reproducible toolchain.

## Required experiments

### Representation comparison

Compare quotient-based, representative-map, and canonical-partition encodings for proof effort, execution, and API clarity.

### Certificate size/cost

Generate random typed port graphs and measure compiler certificate size and checker time.

### Mutation test

Corrupt projection maps, edge justifications, sorts, class membership, and evidence; verify rejection and minimize accepted bad mutations if any.

### API drift test

Change the external schema in controlled ways and record whether the bridge fails loudly or silently misinterprets it.

### Selector corpus

Encode a small positive subset of shared selectors and compare checked derivations with an independent evaluator.

## Proof and validation obligations

- Claimed theorem files contain no unreported axioms, `sorry`, `admit`, or equivalent escape hatches.
- Ill-sorted identity links are unrepresentable or rejected before certificate acceptance.
- Every checked candidate derivation denotes a subject of the declared sort and satisfies the reference semantics.
- Generated linking is reflexive, symmetric, and transitive.
- Linked ports project to equal bindings and therefore have equal observations under any common interpretation.
- Every accepted binding plan satisfies every source identity equation.
- The certificate checker rejects incompatible sorts and malformed projections.
- The TypeScript/JSON bridge performs a clean, tested encoding rather than relying on unchecked object casts.
- Every theorem is mapped to an exact engineering claim and does not imply browser/runtime properties outside the model.
- All finiteness, decidability, and foreign-function assumptions are explicit.

## Measurements to report

- Definitions/theorems and proof lines by concept.
- Trusted axioms and executable bridge size.
- Certificate bytes and check time by graph size.
- Mutation rejection score.
- External scenarios represented without new axioms.
- Proof-maintenance cost under schema changes.

## Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

## Composition capsule

Export proof source, pinned toolchain, theorem inventory, trusted-base report, executable checker, certificate schema, positive-selector subset, binding-plan subset, and golden accepted/rejected certificates. P03 and P06 produce artifacts; P11 may add a derivative certificate; P15 mutates and replays them. Downstream claims cite theorem names and assumptions, not the generic phrase "formally verified."

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

## Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

## Baseline acceptance criteria

- The core distinction is explicit in code or proof terms.
- The reference semantics executes at least three shared traces.
- At least five nontrivial laws are tests or formal theorems.
- At least one plausible but incorrect design is shown to fail.
- Errors and conflicts are typed and observable.
- There is no hidden process-global mutable singleton.
- A second team can invoke the artifact through the common adapter.
- Claims over opaque callbacks are explicitly bounded.
- Performance reports include data size, hardware, warm-up, and uncertainty.
- Visual demonstrations are keyboard-operable.

## Risks and failure modes to seek deliberately

- Proving a theorem about a model disconnected from artifacts.
- Encoding union-find internals as the mathematical definition.
- Hiding axioms in convenience libraries or extraction.
- Making evidence proof-irrelevant when downstream explanations need it.
- Overstating equal observations as synchronization or liveness.
- Letting proof scope expand until no executable result ships.

## Stretch directions

- Prove quotient/canonical-partition equivalence.
- Mechanize finite least-fixed-point closure for positive rules.
- Proof-producing selector normalization.
- Verified code extraction for the checker.
- A logical-relations bridge between an executable evaluator and denotation.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Kernel/theorem inventory. |
| Weeks 2-4 | Definitions and basic lemmas. |
| Weeks 5-7 | Selection and binding theorems. |
| Weeks 8-9 | Certificate bridge and mutation tests. |
| Weeks 10-11 | External corpus and proof audit. |
| Weeks 12-13 | Stretch theorem and report. |

## Selected readings

1. Alfred Tarski. "A Lattice-Theoretical Fixpoint Theorem and Its Applications." Pacific Journal of Mathematics 5(2), 1955. https://msp.org/pjm/1955/5-2/pjm-v5-n2-p11-s.pdf
2. Michael Arntzenius and Neelakantan R. Krishnaswami. "Datafun: A Functional Datalog." ICFP 2016. https://www.rntz.net/files/datafun.pdf
3. John C. Baez and Kenny Courser. "Structured Cospans." Theory and Applications of Categories 35, 2020. https://math.ucr.edu/home/baez/structured.pdf
4. J. J. M. M. Rutten. "Universal Coalgebra: A Theory of Systems." Theoretical Computer Science 249, 2000. https://ir.cwi.nl/pub/48/0048D.pdf

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
