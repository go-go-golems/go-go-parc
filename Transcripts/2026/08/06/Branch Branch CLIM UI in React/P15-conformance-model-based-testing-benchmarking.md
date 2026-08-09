---
title: "P15: Conformance, Model-Based Testing, and Comparative Benchmarking"
subtitle: "Build the neutral harness that lets independently developed PBUI subsystems be substituted, stressed, and compared"
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
| Project | **P15: Conformance, Model-Based Testing, and Comparative Benchmarking** |
| Track | Validation / integration science |
| Suggested team | 1-2 students with testing research, property-based testing, benchmarking, or experimental-methods experience |
| Nominal duration | 9-11 weeks |
| Primary result | A black-box conformance laboratory with reference micro-models, generated traces, shrinking, metamorphic laws, reproducible benchmarks, and capability-aware reports. |

## Executive framing

Independent student teams will choose different languages, data structures, proof techniques, and UI frameworks. Direct source-level integration would reward accidental similarity and hide semantic disagreement. The research program therefore needs a neutral laboratory that compares observable claims through versioned traces and deliberately simpler reference models.

This project designs that laboratory. It must distinguish unsupported capability from rejection, crash, timeout, nondeterminism, and semantic disagreement. It should generate well-typed histories across subsystem boundaries, shrink failures while preserving prerequisites, and report what each artifact actually guarantees. The harness is also a check on the program design: if no stable observation boundary can be stated, the subsystem may not yet be sufficiently understood.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- What is the smallest common protocol that permits meaningful comparison without becoming a lowest-common-denominator production API?
- Which observations are semantically relevant and which can be normalized away?
- What independent micro-models can serve as trustworthy oracles for identity, selection, closure, bindings, machines, and replication?
- How should generators maintain typing, revisions, authority, causal context, and reachability preconditions?
- Can shrinkers preserve the reason a cross-subsystem trace fails?
- Which metamorphic laws expose bugs without requiring one privileged implementation?
- How can performance be compared fairly across languages and architectures?

## Falsifiable hypotheses

- A JSONL protocol plus capability manifest is sufficient for first-pass black-box substitution.
- Small executable models catch more semantic mismatches than broad snapshots of production-like code.
- Metamorphic and differential testing complement formal proof by testing bridges and unsupported regions.
- Dependency-aware shrinking can turn long concurrent traces into comprehensible counterexamples.
- Benchmark reports should stratify guarantees before ranking throughput.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- Declaring one architecture the winner from a single composite score.
- Using wall-clock microbenchmarks without warm-up, workload, or uncertainty.
- Depending on undocumented internal APIs.
- Normalizing away meaningful evidence, conflict, or status differences.
- Replacing project-specific proof and user studies.

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

Model each artifact as a labeled transition system with requests $I$, internal state $X$, and observable responses $O$:

$$\delta:X\times I\to X\times O.$$

The harness compares observations under a declared equivalence or refinement relation rather than raw JSON equality. A canonicalization function may erase only fields proven or declared observationally irrelevant, such as generated request IDs.

Metamorphic relations include: duplicate and reordered identity links yield the same partition; permutation of positive base facts yields the same closure; deterministic machine replay yields the same normalized trace; and CRDT delivery orders respecting the declared assumptions converge to equivalent states. For nondeterministic artifacts, comparison is relational: an observation must belong to the specified allowed set or simulation relation.

## Minimum API and executable artifact

```ts
interface ResearchArtifactManifest {
  protocol: "pbui-research/0.1";
  artifact: string;
  version: string;
  capabilities: readonly string[];
  guarantees: readonly GuaranteeClaim[];
  command: readonly string[];
  normalization: readonly string[];
}
interface Harness {
  replay(artifact: Artifact, trace: Trace): RunReport;
  generate(model: ScenarioModel, seed: number): Trace;
  shrink(failure: Failure): Trace;
  compare(a: Artifact, b: Artifact, trace: Trace): ComparisonReport;
  benchmark(suite: BenchmarkSuite): BenchmarkReport;
}
```

Expose `harness.validate-manifest`, `harness.replay`, `harness.generate`, `harness.shrink`, `harness.compare`, and `harness.benchmark`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Protocol and manifests

Finalize envelopes, statuses, evidence references, capabilities, version negotiation, deterministic modes, and guarantee labels.

### Reference micro-models

Implement independent finite models for subject identity, positive selection, recursive closure, port partitions, small machines, and a simple replicated topology.

### Generators and shrinkers

Generate typed fixtures and histories while tracking prerequisites; shrink graph, facts, components, events, causal schedules, and evidence.

### Metamorphic/differential engine

Run laws, cross-implementation comparisons, mutation tests, and bridge checks with explicit observation relations.

### Benchmark laboratory

Define cold/warm runs, workload scaling, resource measurement, correctness gates, uncertainty, and guarantee-stratified comparison.

### Reports and replay viewer

Produce a portable failure bundle with seed, trace, manifests, normalized observations, divergence, and one-command reproduction.

## Required experiments

### Mutation score

Seed realistic faults in micro-models and student adapters; measure which generators and laws detect each fault family.

### Black-box substitution

Swap two implementations behind one capability and replay the same composition trace without source-level changes.

### Nondeterminism study

Compare exact equality, trace inclusion, bounded simulation, and invariant-only relations for concurrent or ranked results.

### Benchmark fairness

Demonstrate how warm-up, batching, validation, evidence level, and workload shape alter apparent rankings.

### Failure comprehension

Give minimized and unminimized reports to developers; measure reproduction success and diagnosis time.

## Proof and validation obligations

- The harness invokes only documented protocol and process boundaries.
- Canonicalization removes only declared observationally irrelevant differences.
- Generators emit well-typed traces satisfying stated prerequisites or intentionally labeled negative cases.
- Shrinkers preserve failure and required dependency/causal structure.
- Every failure bundle includes command, versions, seed, trace, timeout, and normalized outputs.
- Reports distinguish proved, model-checked, property-tested, example-tested, empirical, assumed, and unsupported guarantees.
- Reference models are simpler and independently implemented rather than wrappers around submissions.
- Negative controls and seeded faults demonstrate test sensitivity.
- Nondeterministic comparisons use an explicit relation rather than flaky exact matching.
- Timeout, crash, malformed output, rejection, and unsupported capability are distinct outcomes.

## Measurements to report

- Seeded-fault detection by category.
- Median and tail shrink time and resulting trace size.
- Adapter/protocol implementation effort.
- Cross-implementation disagreement count and cause.
- Benchmark variance and correctness-gate failures.
- Developer reproduction and diagnosis success.

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

Export the protocol schema, manifest schema, capability vocabulary, reference micro-models, generators, shrinkers, metamorphic laws, benchmark suites, report schema, and replay viewer. Every other project supplies a capsule that P15 can invoke. P15 does not dictate internal APIs; it controls only the experimental seam. Composition experiments are accepted only after individual artifacts pass their declared capability suite.

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

- The harness becoming the de facto architecture.
- Shared bugs from copied reference code.
- Overcanonicalizing evidence or order.
- Flaky wall-clock assertions.
- Generating impossible histories.
- One aggregate score hiding guarantee differences.
- Treating unsupported as failure or vice versa.

## Stretch directions

- Coverage-guided semantic trace generation.
- Proof-certificate mutation integration with P14.
- Statistical model checking for selected machine/replica properties.
- Cross-language resource accounting in containers.
- A public corpus of minimized PBUI counterexamples.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Protocol and threat model. |
| Weeks 2-3 | Micro-models and adapters. |
| Weeks 4-5 | Generators/shrinkers. |
| Week 6 | Metamorphic engine and mutations. |
| Weeks 7-8 | Benchmark/reporting. |
| Weeks 9-10 | Cross-team pilot. |
| Week 11 | Refinement and final corpus. |

## Selected readings

1. Patrick Cousot and Radhia Cousot. "Abstract Interpretation Frameworks." Journal of Logic and Computation 2(4), 1992. https://www.di.ens.fr/~cousot/publications.www/CousotCousot-JLC-n2--3-p103--179-1992.pdf
2. J. J. M. M. Rutten. "Universal Coalgebra: A Theory of Systems." Theoretical Computer Science 249, 2000. https://ir.cwi.nl/pub/48/0048D.pdf
3. Marc Shapiro et al. "A Comprehensive Study of Convergent and Commutative Replicated Data Types." INRIA Research Report 7506, 2011. https://inria.hal.science/inria-00555588v1/document
4. Frank McSherry et al. "Differential Dataflow." CIDR 2013. https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
