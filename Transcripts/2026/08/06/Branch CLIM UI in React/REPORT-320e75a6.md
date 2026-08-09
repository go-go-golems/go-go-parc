---
title: "P08: Bidirectional Links and Consistency Restoration"
subtitle: "Reference semantics, conflict evidence, deterministic scheduling, and a PBUI laboratory"
author: "PBUI Research Program - P08 independent implementation"
date: "2026-08-05"
lang: en-US
documentclass: article
geometry: margin=0.72in
fontsize: 10pt
toc: true
toc-depth: 3
numbersections: true
colorlinks: true
linkcolor: blue
urlcolor: blue
header-includes:
  - |
    \usepackage{microtype}
    \usepackage{longtable}
    \usepackage{booktabs}
    \usepackage{enumitem}
    \setlist{nosep}
---

# Abstract

Presentation-based user interfaces need links among components, but not all links have the same semantics. A chart and a pipeline can share one primary document. A table selection can derive a pipeline filter. A textual query and an abstract syntax tree can represent the same intent with unequal information. Two offline editors can require replicated merge rather than local consistency repair. Treating all of these cases as equality, callbacks, or generic two-way binding creates silent information loss and feedback behavior that depends on event timing.

This report presents an independent implementation of PBUI project P08: a link-policy laboratory for identity references, directed derivations, partial asymmetric lenses, symmetric consistency relations, and delta-aware repair. The implementation makes repair outcomes explicit:

$$
\operatorname{Repair}(T)
=
\operatorname{Updated}(T)
+
\operatorname{Unchanged}(T)
+
\operatorname{Conflict}(T)
+
\operatorname{Invalid}.
$$

Every result carries inspectable evidence describing consistency before and after repair, information loss, preserved and discarded intent, provenance, assumptions, and optional edit deltas. A deterministic transactional scheduler composes policies through an explicit work order, reports stable convergence, detects repeated-state oscillation, bounds divergence, and rolls back unresolved transactions by default.

The experimental domain links a table row selection and a pipeline filter over a five-row analytical fixture. Four policy designs are compared under add, remove, reorder, and replacement edits. Directed replacement and an ordinary exact-view lens discard target-local filter clauses. Symmetric envelope-aware and delta-aware repairs preserve those clauses. Delta repair does not uniquely improve clause preservation; its stronger observed benefit is edit provenance and scheduling granularity. A lawful set-oriented lens is shown to be visibly surprising, while an intuitive toggle handler violates a round-trip law and is reduced to a minimal counterexample.

The artifact includes a TypeScript reference implementation, compiled JavaScript, 18 Node tests, generated property tests with shrinkers, finite model checks, a 22-case link taxonomy, a JSONL composition adapter, benchmarks, a dependency-free browser laboratory, a React adapter, and an unchecked Lean proof sketch. It deliberately does not claim network-replica convergence, arbitrary filter inversion, persistent binding quotienting, or universal formal verification.

# Research framing

## The problem is not generic two-way binding

A generic two-way binding abstraction often assumes a pair of setters:

```text
left changes  -> set right
right changes -> set left
```

This shape is attractive because it appears symmetric. It hides at least six questions:

1. Are the endpoints two names for one resource, or two representations?
2. Is one direction derivational and the other undefined?
3. Does the inverse lose information or admit several valid results?
4. Which prior intent should be preserved during repair?
5. What happens when repairs form a cycle?
6. Who has authority to choose among ambiguous repairs?

A UI callback can answer these questions accidentally through control flow. A link subsystem should answer them explicitly through semantic objects.

## Bounded objective

P08 is not a universal synchronization language. It is a bounded subsystem study. The objective is to make the following distinctions executable and testable:

- identity sharing;
- directed transformation;
- source/view lens behavior;
- peer consistency and repair;
- delta-sensitive repair;
- replicated merge as a separate category.

The artifact is successful when it refuses to guess as reliably as when it produces a value.

## Falsifiable hypotheses

The study begins with four claims.

**H1 - Mode distinction.** A first-class distinction among identity, directed, lens, symmetric, delta, and replicated policies prevents equality mistakes and feedback bugs.

**H2 - Typed partiality.** Partial repairs with typed conflicts are more honest than total functions that select arbitrary inverses.

**H3 - Delta intent.** Delta-aware synchronization preserves selection/filter intent better than replacement.

**H4 - Laws and usability.** Lens laws are necessary for some policies but do not replace conflict, provenance, or usability analysis.

Each claim has a possible failure. For example, H3 would fail in its strong form if a non-delta symmetric repair preserved the same target intent.

# Laboratory setting

## Component constellation

The visual laboratory contains four independently framed components:

- **source browser**, presenting documents and fields;
- **chart**, with `chart.document` and `chart.selection` ports;
- **table**, with `table.document` and `table.selection` ports;
- **pipeline**, with `pipeline.document` and `pipeline.filter` ports.

The right-hand policy laboratory exposes policy selection, repair direction, ambiguity strategy, evidence, laws, feedback traces, and taxonomy.

The visual interaction grammar was adapted from the supplied PBUI productivity-suite JSX: typed live presentations, shell-level accept mode, compact bordered tiles, hover documentation, right-click inspection, and a persistent status strip. The synchronization kernel is new and independent of P07.

## Fixed rows

The transformed-link fixture has five rows:

| Row | Station | Temperature | Pressure |
|---|---|---:|---:|
| `row-7` | A | 18.4 | 1008 |
| `row-9` | B | 21.1 | 1003 |
| `row-11` | A | 19.7 | 1006 |
| `row-13` | C | 17.8 | 1012 |
| `row-17` | B | 22.0 | 1001 |

The repeated station values are intentional. They create an inverse that is semantically ambiguous without requiring a large dataset.

## Selection and filter domains

A row selection is an ordered sequence:

```ts
interface RowSelection {
  readonly rows: readonly RowId[];
}
```

The filter language is inspectable syntax:

```ts
type FilterExpr =
  | { op: "true" }
  | { op: "inRows"; rows: readonly RowId[] }
  | { op: "stationIn"; stations: readonly string[] }
  | { op: "and"; args: readonly FilterExpr[] }
  | { op: "or"; args: readonly FilterExpr[] }
  | { op: "opaque"; id: string; label: string };
```

The distinction between syntax and denotation matters. Two different filters can select the same rows. A filter can also contain target-local intent that is not derivable from the table selection.

## Equivalence relations

The artifact exposes two selection equivalences:

$$
s_1 \equiv_{\mathrm{set}} s_2
\quad\text{and}\quad
s_1 \equiv_{\mathrm{sequence}} s_2.
$$

Set equivalence deduplicates and sorts row IDs. Sequence equivalence preserves order and duplicates. A policy law must state which equivalence it uses. Without that declaration, a law may be technically true while violating a visible UI invariant.

# Semantic objects

## Policy metadata

Every policy has versioned metadata:

```ts
interface PolicyMetadata {
  readonly id: string;
  readonly version: string;
  readonly label: string;
  readonly kind: PolicyKind;
  readonly leftSort: string;
  readonly rightSort: string;
  readonly description: string;
  readonly supportedDirections: readonly Direction[];
  readonly declaredLaws: readonly string[];
  readonly assumptions: readonly string[];
  readonly opaqueCallbacks: readonly string[];
}
```

Metadata is part of semantics. A host can reject an unsupported direction before running a repair. Assumptions and opaque callbacks bound what can be inferred from a successful result.

## Consistency relation

For endpoint domains $L$ and $R$, a policy defines an inspectable judgment:

$$
C : L \times R \longrightarrow \operatorname{ConsistencyEvidence}.
$$

`ConsistencyEvidence` contains a Boolean result, relation name, summary, facts, and information-loss statements. The Boolean says whether a relation holds; the rest explains what the relation means.

For the selection/filter case, let $\mathcal{D}(f)$ be the set of fixture rows satisfying filter $f$, and let $\operatorname{set}(s)$ be the selected row set. The principal extensional relation is:

$$
C(s,f)
\iff
\operatorname{set}(s)=\mathcal{D}(f).
$$

A station summary may satisfy this relation while losing row-level provenance. Consistency is therefore not equivalent to information preservation.

## Typed repair

The minimum API is:

```ts
interface LinkPolicy<L, R> {
  readonly metadata: PolicyMetadata;
  consistent(left: L, right: R): ConsistencyEvidence;
  propagate(
    request: PropagationRequest<L, R>,
  ): Repair<L> | Repair<R>;
}
```

The repair sum is:

```ts
type Repair<T> =
  | { kind: "updated"; value: T; evidence: RepairEvidence }
  | { kind: "unchanged"; value: T; evidence: RepairEvidence }
  | {
      kind: "conflict";
      choices: readonly RepairChoice<T>[];
      conflictKind: ConflictKind;
      evidence: RepairEvidence;
    }
  | { kind: "invalid"; reason: string; evidence: RepairEvidence };
```

This representation avoids three common collapses:

- `unchanged` is not confused with failure;
- `conflict` is not confused with invalid input;
- a partial inverse does not return `undefined` without explanation.

## Evidence

A repair evidence object includes:

```ts
interface RepairEvidence {
  evidenceId: string;
  policyId: string;
  policyKind: PolicyKind;
  direction: Direction;
  summary: string;
  consistencyBefore: ConsistencyEvidence;
  consistencyAfter: ConsistencyEvidence;
  informationLoss: readonly string[];
  preservedIntent: readonly string[];
  discardedIntent: readonly string[];
  provenance: readonly string[];
  delta?: JsonValue;
  assumptions: readonly string[];
}
```

This is proof-relevant runtime data, not a machine-checked proof. It supports explanation, audit, and composition testing. The registry retains repairs by evidence ID so a later request can retrieve the complete decision.

# Link modes

## Identity reference

Identity means that two endpoint occurrences project onto one logical resource. It is not a pair of transformations.

The implementation uses one cell:

```ts
class IdentityCell<T> {
  get(): T;
  set(value: T, actor?: string): IdentityWrite<T>;
  projection(endpoint: string): IdentityProjection<T>;
}
```

For endpoints $p$ and $q$, both projections factor through one cell $B$:

$$
p \longrightarrow B \longleftarrow q.
$$

A write through either projection changes the cell revision once. The other endpoint observes the same value because it reads the same cell, not because a callback called its setter.

Persistent binding class identity, quotient topology, merge policy for preexisting values, and unlink behavior belong to P06. P08 implements only a single-session reference because it needs a concrete contrast with transformed links.

## Directed derivation

The directed policy maps a row selection to an exact filter:

$$
d : S \longrightarrow F.
$$

It supports only forward propagation. A backward request returns `invalid` with direction evidence.

The policy is intentionally destructive with respect to the previous target representation. It answers a narrow question: what exact filter denotes this selection? It does not claim to preserve target-local clauses.

## Partial asymmetric lens

An asymmetric lens has:

$$
\operatorname{get}:S\to V,
\qquad
\operatorname{put}:S\times V\to S.
$$

Candidate laws include:

$$
\operatorname{get}(\operatorname{put}(s,v)) \equiv_V v
$$

and:

$$
\operatorname{put}(s,\operatorname{get}(s)) \equiv_S s.
$$

P08's `get` maps a selection to an exact row filter. Its `put` is total on exact row filters and partial on coarse or compound filters. The API does not force a mathematically total function by guessing. Instead it returns a conflict containing possible preimages.

The ordinary lens still replaces the richer target during `get`. Lens laws alone do not imply preservation of unrelated view structure.

## Symmetric consistency and repair

A symmetric policy begins with a relation $C\subseteq L\times R$ and restoration procedures:

$$
\rho_R : L\times R \to \operatorname{Repair}(R),
$$

$$
\rho_L : L\times R \to \operatorname{Repair}(L).
$$

The principal obligations are:

**Restoration:** whenever a repair returns a value, the resulting pair satisfies $C$.

$$
\rho_R(l,r)=r'
\Longrightarrow C(l,r').
$$

**Stability:** a consistent pair should not be rewritten without a separate reason.

$$
C(l,r)
\Longrightarrow \rho_R(l,r)=\operatorname{Unchanged}(r).
$$

The selection/filter policy preserves a compound filter envelope where it can locate a selection clause. For example:

```json
{
  "op":"and",
  "args":[
    {"op":"opaque","id":"owner","label":"owner=analyst"},
    {"op":"inRows","rows":["row-7","row-9"]}
  ]
}
```

can be repaired by replacing only `inRows` and preserving `owner=analyst`.

## Delta-aware consistency

A state-based repair knows old and new values only. A delta-aware repair also receives an edit:

```ts
interface SelectionDelta {
  readonly add: readonly RowId[];
  readonly remove: readonly RowId[];
  readonly order?: readonly RowId[];
}
```

The delta policy's left state is:

```ts
interface DeltaLeftState {
  before: RowSelection;
  after: RowSelection;
  delta: SelectionDelta;
}
```

This distinction matters for reorder-only edits. The filter denotation is already consistent, so state-based repair returns unchanged. Delta evidence can still report that an order change occurred and that the target cannot represent it.

Delta-aware repair is not automatically superior. It depends on trustworthy edit production and introduces a richer scheduling interface.

## Replicated merge

Replicated merge is present in the taxonomy but absent from the implementation. Offline replicas require a merge algebra, causal metadata, tombstones, or explicit conflict semantics. A pair of local lens laws does not establish replica convergence.

The common concurrent-topology trace receives typed `unsupported` responses. This is a deliberate boundary with P12.

# Filter semantics and preservation

## Normalization

`normalizeFilter` performs deterministic syntactic normalization:

- row IDs and stations are deduplicated and sorted;
- nested conjunctions and disjunctions are flattened;
- neutral `true` clauses are removed from conjunctions;
- compound arguments are stably sorted.

This is sufficient for evidence, comparison, and state hashing. It is not a complete Boolean equivalence procedure.

## Opaque clauses

An opaque clause has an ID and label but no evaluator in the reference kernel. The denotational evaluator treats it as true. This choice permits preservation experiments without importing arbitrary callbacks into the trusted core.

The limitation is explicit:

- P08 can prove that an opaque clause remains in the syntax;
- P08 cannot prove what that clause means or whether it is semantically compatible with a row selection.

## Ambiguous inverse enumeration

For `stationIn`, P08 enumerates bounded subsets of the five fixture rows whose station summary matches the target. Choices are scored using prior-row preservation and deterministic tie-breaking.

This procedure establishes a useful local property:

$$
\forall c\in\operatorname{choices}(s,f),\quad C(c,f).
$$

It does not establish completeness for arbitrary filter languages or scalability to large datasets.

# Conflict semantics

## Choice structure

A conflict choice contains a value, label, score, explanation, information-loss statement, and provenance. A user interface can therefore show why a candidate exists, not only its serialized value.

## Strategy versus policy

The policy produces possible repairs. A host strategy determines whether any candidate may be committed:

- **automatic**: choose only a uniquely top-ranked candidate;
- **ranked**: preserve a pending ranked list;
- **dialog**: require explicit selection;
- **refuse**: decline the repair.

This separates semantic possibility from authority. A policy author does not automatically obtain the right to commit a lossy repair.

## Why a unique score is insufficient

A score can express heuristics such as preservation of prior row identity. It cannot prove that the user intended that row. Therefore the automatic strategy is available for experimentation but does not establish a product recommendation.

# Deterministic transactional scheduler

## Graph model

The scheduler stores nodes and directed edges:

```ts
interface SchedulerNode<T> {
  id: string;
  sort: string;
  value: T;
  revision: number;
}

interface SchedulerEdge {
  id: string;
  policyId: string;
  from: string;
  to: string;
  direction: Direction;
  priority: number;
}
```

Each edge names a policy and an orientation. Composition does not infer direction from endpoint position.

## Explicit order

Edges are sorted by priority, edge ID, and target ID. The schedule signature hashes this normalized order. Reversing declaration order therefore does not change the signature.

Scheduling is part of semantics. A host that silently changes order can change results even when every individual policy remains unchanged.

## Transaction algorithm

A transaction proceeds as follows:

1. clone committed node state;
2. apply initiating changes to the clone;
3. enqueue changed nodes;
4. process outgoing edges in deterministic order;
5. apply successful repairs to the working copy;
6. enqueue changed targets;
7. stop at stable queue exhaustion, conflict, invalid repair, repeated state, or step bound;
8. commit only under the configured terminal policy.

With the default `commitOnStableOnly`, unresolved ambiguity rolls the transaction back to its initial state.

## Oscillation detection

A state alone is not enough to identify scheduler repetition because the same state with different pending work can evolve differently. The detector hashes:

$$
(\text{normalized global state},\ \text{pending-work signature}).
$$

A repeated pair is reported as oscillation with first and repeated step indexes.

## Bounded divergence

A cycle may generate a fresh state at every step and never repeat. The unbounded increment scenario demonstrates this case. After the configured limit the scheduler reports bounded failure rather than claiming oscillation or success.

## No propagation suppression flag

The implementation does not set a global `currentlyPropagating` flag to ignore recursive updates. Such a flag can hide feedback and make results depend on call-stack timing. P08 executes the queue explicitly and reports what happens.

# Law harness

## Evidence levels

The law report distinguishes:

- example-tested;
- property-tested;
- finite-model-checked.

A generated property test is not described as a theorem over an infinite domain.

## Generators and shrinkers

The harness uses a deterministic random generator. Selection generators draw row IDs with possible duplicates and order variation. Filter generators produce exact and station summaries. Array shrinkers remove chunks and values to reduce failures.

Every failure records:

- original input;
- minimized input;
- observed result;
- expected property;
- shrink count;
- explanation.

## Checked obligations

The current law report has 14 passing obligations:

1. finite exact right repair restores consistency;
2. finite exact left repair restores consistency;
3. finite stable exact states are unchanged;
4. identity projections observe one cell;
5. generated right repair restores consistency;
6. every ambiguous choice is consistent;
7. stable right states are unchanged;
8. stable left states are unchanged;
9. right repair is idempotent;
10. asymmetric `get-put`;
11. asymmetric exact-fragment `put-get`;
12. zero delta does not rewrite;
13. delta forward repair restores consistency;
14. the lawful-surprising lens satisfies its law under set equivalence.

## Seeded negative control

The bad policy treats a requested membership state as a toggle event. The initial generated failure is shrunk to:

```json
{
  "source":{"rows":[]},
  "view":{"selected":false}
}
```

The current view is false, so `put(source, view)` should preserve the empty selection. The implementation adds `row-7`.

This example distinguishes two semantic forms:

```text
event: toggle membership
state: establish membership = false
```

An event delta can be useful, but it is not a lawful state-setting `put`.

# Required experiments

## Selection-to-filter comparison

The initial target is an enriched conjunction containing two opaque clauses and one exact selection clause. Four edit cases are run against four designs.

### Clause preservation totals

| Design | Clauses preserved across four cases |
|---|---:|
| Directed replacement | 0 |
| Asymmetric exact-view lens | 0 |
| Symmetric envelope repair | 8 |
| Delta envelope repair | 8 |

Both symmetric designs preserve all two unrelated clauses in each case.

### Add and remove

Add and remove edits establish consistency under all four forward designs. The distinction is target intent:

- replacement and lens projection discard the enriched envelope;
- symmetric repair replaces only the selection clause;
- delta repair does the same and records the specific add or remove.

### Reorder only

The selection moves from `[row-7,row-9]` to `[row-9,row-7]`. Under set equivalence the filter remains consistent.

- symmetric repair returns unchanged;
- delta repair returns unchanged and records `order`;
- replacement and lens projection rewrite the view even though denotation is unchanged.

### Result for H3

The strong claim that delta repair uniquely preserves more target structure is falsified in this fixture. The weaker claim is supported: delta repair preserves explicit edit provenance and provides a more granular scheduling input.

## Law versus usability

A set lens sorts and deduplicates row IDs. Under set equivalence it satisfies the round-trip law. In a UI that visibly represents order, the output can be surprising.

The negative toggle feels natural as a click handler but fails as a lens update. Therefore:

```text
lawful does not imply unsurprising
intuitive event behavior does not imply lawful state repair
```

## Feedback cycles

Three scenarios are executed with a 24-step bound.

| Scenario | Status | Steps | States visited |
|---|---|---:|---:|
| trim and lowercase | stable | 5 | 4 |
| modulo-three cycle | oscillation | 8 | 8 |
| unbounded increment | bounded failure | 24 | 24 |

The scheduler can report the distinction but cannot decide general termination.

## Ambiguity policy

The station A+B inverse produces nine bounded candidates in the main scenario. Automatic mode selects the uniquely highest-scoring choice; ranked and dialog leave the choice pending; refuse declines.

The experiment uses scripted decision-cost proxies rather than human measurements. No usability claim is inferred from those numbers.

# Results against hypotheses

## H1 - Mode distinction

**Outcome: supported in the implemented fragment.**

Evidence:

- identity uses shared reference aliasing;
- directed backward requests are invalid;
- transformed inverse ambiguity is explicit;
- feedback cycles are reported rather than suppressed;
- replicated cases are classified separately.

This does not prove that every future policy will be classified correctly.

## H2 - Typed partiality

**Outcome: supported.**

The station summary has several consistency-preserving preimages. The implementation exposes choices and information loss instead of selecting an arbitrary row identity.

## H3 - Delta intent

**Outcome: supported with qualification.**

Delta repair records add, remove, and reorder intent and preserves the enriched filter envelope. However, symmetric envelope-aware repair preserved the same clauses. Delta's distinctive benefit is provenance and edit granularity, not universal structural preservation.

## H4 - Laws and usability

**Outcome: supported.**

The lawful-surprising lens and intuitive-unlawful toggle provide opposite counterexamples. Laws remain useful, but their equivalence relation and visible consequences must be evaluated separately.

# Link taxonomy

The taxonomy contains 22 plausible PBUI links. It preserves disputed cases rather than forcing one global answer.

Examples:

- `chart.primaryDocument` and `pipeline.primaryDocument`: identity reference;
- `pipeline.outputDocument` to `chart.primaryDocument`: directed;
- `table.rowSelection` and `pipeline.filter`: delta consistency;
- `queryText` and `queryAst`: asymmetric lens;
- two collaborative text editors: replicated merge;
- `authorityState` to offered affordances: directed;
- saved view and ad hoc workspace state: disputed symmetric, lens, or no-link case.

A taxonomy entry is not a runtime dispatch rule. The host must still bind concrete endpoint contracts to a versioned policy.

# JSONL composition capsule

## Protocol

The adapter uses one JSON object per line:

```ts
interface LabEnvelope<T = unknown> {
  protocol: "pbui-research/0.1";
  requestId: string;
  kind: string;
  payload: T;
}
```

Responses are `ok`, `rejected`, `unsupported`, or `error`.

## P08 capabilities

The principal capabilities are:

```text
links.check-policy
links.propagate
links.explain-repair
links.simulate-feedback
links.run-laws
links.taxonomy
```

The adapter also supports a bounded identity-reference subset of `bindings.*` so the common identity trace can be replayed. That implementation is marked partial and does not allocate persistent quotient classes.

## Shared traces

The identity and transformed-link traces are fully replayed. Same-subject comparison is partial. Refined selection, stale authority, and concurrent topology produce typed unsupported results for operations owned by other projects.

Typed unsupported behavior is a compositional result: another subsystem can distinguish absence from failure or silence.

## Export classifications

The capsule classifies exports as:

- extensional data: policy metadata;
- intensional syntax: filter AST;
- proof evidence: repair evidence;
- opaque callback: opaque filter predicates;
- mutable resource: identity cell;
- event stream: scheduler trace.

# Browser and React prototypes

## Dependency-free browser laboratory

The `web/` application imports the compiled semantic kernel directly. It implements:

- typed port cards;
- accept-mode endpoint picking;
- identity and transformed links;
- row and filter editing;
- repair evidence and choices;
- law, feedback, and taxonomy panels;
- keyboard cancellation and activation;
- right-click inspection.

The laboratory is an adapter, not a second policy implementation.

## React adapter

`react/P08BidirectionalLinkLab.jsx` uses the same compiled modules. React owns mounted occurrences and event adaptation. Policy semantics, evidence, and law results remain outside React component callbacks.

The React source was syntax-checked with TypeScript's JSX parser and a local declaration shim. It was not bundled against a production React dependency during artifact assembly.

## Accessibility boundary

The browser prototype supports keyboard traversal, Enter or Space activation for acceptable ports, Escape cancellation, labels on select controls, and visible focus outlines. It is not a complete accessibility audit. In particular, dynamic conflict announcements and screen-reader testing require a later user study.

# Performance observations

## Environment

The recorded benchmark ran under Node 22.16.0 on Linux x64 with five visible Intel Xeon Platinum 8370C CPUs and approximately 6.37 GB of memory.

## Filter normalization

Mean time ranged from approximately 0.28 ms for 10 clauses to 15.78 ms for 5,000 clauses. These measurements include deterministic sorting and normalization.

## Scheduler chains

Mean transaction time was approximately:

- 0.70 ms for 10 edges;
- 16.77 ms for 100 edges;
- 267.33 ms for 500 edges.

The scheduler benchmark includes node and edge construction, evidence creation, normalization, and propagation. It is not an isolated repair-function benchmark. The growth indicates that the current reference scheduler is suitable for research and modest graphs but should not be treated as an optimized reactive engine.

# Validation

The validated executable evidence includes:

- strict TypeScript compilation;
- 18 passing Node tests;
- 14 passing generated/model obligations;
- one expected failing negative control;
- generated counterexample shrinking;
- four experiment groups and negative findings;
- benchmark correctness gates;
- common trace replay;
- capsule and schema checks;
- source import independence from P07;
- browser JavaScript syntax check;
- React JSX syntax check.

The full command is:

```bash
npm run verify
```

The compiled no-install path is:

```bash
npm run verify:compiled
```

# Formal proof sketch

`proofs/Main.lean` models a two-row exact fragment. It states and attempts proofs of:

- `get-put`;
- `put-get`;
- `put-put`;
- right and left consistency restoration;
- stable states unchanged;
- ambiguity of a station summary;
- agreement of projections from one identity cell.

Lean was unavailable in the assembly environment. The file is therefore unchecked formal source. The report does not count it among validated theorems.

A later checked development should connect the finite model mechanically to the TypeScript evaluator or use generated proof certificates rather than maintaining two independent specifications indefinitely.

# Limitations and threats to validity

## Small fixture

The row catalogue has five rows. Power-set inverse enumeration is feasible only because the model is tiny. A production system needs database queries, symbolic constraints, indexes, or domain-provided inverse strategies.

## Opaque semantics

Opaque clauses are preserved but not evaluated. Clause-preservation results are syntactic. They do not establish that the full repaired filter has the intended business meaning.

## Equivalence selection

Set equivalence is appropriate for filter denotation but may be inappropriate for a UI that exposes order. Lawfulness depends on the declared quotient.

## Conflict authority

Ranking is deterministic, but authority is external. No user study established which strategy is preferable for a particular risk class.

## Synchronous scheduling

The scheduler assumes synchronous policy calls. Asynchronous effects, cancellation, stale endpoint revisions, and distributed fairness require additional semantics.

## Single-host benchmarks

The reported timings are empirical observations from one host. They are not confidence intervals across machines or browser environments.

## Prototype UI

The browser laboratory is designed for scenario exploration, not production styling, localization, or comprehensive accessibility conformance.

# Composition boundaries

## P06

P06 owns typed port contracts, identity equations, quotient classes, persistent binding IDs, and topology editing. P08 can consume resolved endpoint identities and supply transformed-link policies.

## P07

P07 may declare open component signatures and compatible boundaries. P08 was implemented independently and does not reuse P07 code. Future composition should occur through contract data, not source imports.

## P09

P09 may model the link-creation interaction as a machine. It can call P08 policy checks and present P08 repair conflicts while retaining ownership of workflow state.

## P12

P12 owns replicated topology and values. It must not treat P08's local consistency relation as a replica merge algebra without a separate proof.

## P13

P13 can consume repair evidence to provide explanations and accessible conflict dialogs. It should not infer completeness beyond the evidence assumptions.

# Negative findings

The project records the following negative results.

1. Delta repair did not uniquely outperform symmetric envelope repair on clause preservation.
2. A lawful lens can surprise users when its equivalence ignores visible order or duplicates.
3. A deterministic scheduler can diagnose but not force convergence.
4. Unique top score does not prove user intent.
5. Finite inverse enumeration is not a scalable general algorithm.
6. Identity reference cannot recover two previous independent values after merge without an external policy.
7. Local lens laws do not establish replicated convergence.

These results narrow the architecture and should survive into later composition rather than being optimized away.

# Conclusions

The smallest useful P08 kernel is not a universal two-way binding abstraction. It is the combination of:

```text
versioned policy metadata
+ explicit consistency relation
+ typed Repair<T>
+ information-loss and provenance evidence
+ authority-aware conflict strategy
+ deterministic schedule trace
```

Identity should be implemented as one resource with several projections. Directed links should reject invented inverses. Asymmetric lenses should state their domain of totality and equivalence relation. Symmetric repairs should expose ambiguity and preserve target-local intent where the syntax permits it. Deltas should be used when edit provenance affects explanation or scheduling. Replicated merge should remain a separate construction.

The strongest implementation lesson is that successful synchronization is not merely obtaining equal-looking values. It is establishing a declared relation while accounting for what information and authority were used to restore it.

# Reproduction commands {.unnumbered}

```bash
# Complete rebuild and validation
npm run verify

# Validate the compiled artifact without rebuilding
npm run verify:compiled

# Run only tests
npm test

# Regenerate law and experiment artifacts
npm run laws
npm run experiments

# Run benchmark
npm run benchmark

# Start browser laboratory
npm run demo

# Start JSONL adapter
npm run adapter
```

# Artifact map {.unnumbered}

```text
src/domain.ts        syntax, denotation, equivalence, deltas
src/policies.ts      identity, directed, lens, symmetric, delta
src/repair.ts        typed outcomes and conflict resolution
src/registry.ts      versioned policy dispatch and evidence store
src/scheduler.ts     deterministic transactions and feedback
src/laws.ts          generators, shrinkers, finite checks
src/experiments.ts   comparative studies
src/taxonomy.ts      22 link classifications
src/adapter.ts       JSONL composition seam
web/                 dependency-free interactive laboratory
react/               React adapter
capsule/             schemas and reliance manifest
results/             generated evidence
counterexamples/     minimized failures
proofs/              unchecked Lean source
```

# Selected references {.unnumbered}

1. J. Nathan Foster, Michael Greenwald, Jonathan Moore, Benjamin Pierce, and Alan Schmitt. *Combinators for Bidirectional Tree Transformations*. ACM TOPLAS 29(3), 2007. <https://inria.hal.science/inria-00484971v1/document>
2. Martin Hofmann, Benjamin C. Pierce, and Daniel Wagner. *Symmetric Lenses*. POPL, 2011. <https://www.cis.upenn.edu/~bcpierce/papers/symmetric.pdf>
3. Michael Johnson and Robert Rosebrugh. *Symmetric Delta Lenses and Spans of Asymmetric Delta Lenses*. Journal of Object Technology 16(1), 2017. <https://www.jot.fm/issues/issue_2017_01/article2.pdf>
4. Matthew Pickering, Jeremy Gibbons, and Nicolas Wu. *Profunctor Optics*. 2017. <https://arxiv.org/abs/1703.10857>
