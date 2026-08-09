# P06 — Typed Ports and the Binding Quotient Compiler

## Framing report and implementation study

**Artifact:** `p06-port-binding-lab`  
**Version:** `0.1.0`  
**Protocol:** `pbui-research/0.1`  
**Status:** executable research prototype

---

## Abstract

A user instruction such as “link the chart to the pipeline” hides several different operations. It may mean copying a value once, establishing one-way propagation, maintaining a bidirectional relation, sharing a mutable resource, or declaring that two local interface names are aliases for one global binding. P06 studies only the last of these: **identity wiring**.

The artifact gives identity wiring an explicit typed semantics. Every port occurrence carries a contract containing semantic tag, payload sort, temporal mode, authority domain, multiplicity, update algebra, and lifetime. Identity links are accepted only when these fields agree definitionally. For each contract fiber, link declarations generate an equivalence relation on local port occurrences. The compiler computes its quotient, or equivalently in finite sets the coequalizer of the two endpoint maps. A separate persistence layer assigns stable external binding identities; union-find representatives are never exposed. A runtime interpreter allocates one shared cell for each binding class and returns typed projections to components. Merge and unlink value choices are explicit policies because neither follows from quotient semantics.

The artifact contains two independent compilers: a transparent graph-closure reference implementation and an optimized union-find implementation. Every optimized registry compilation can be checked against the reference semantic signature. Generated tests compare both algorithms on 2,000 typed graphs containing duplicates, cycles, disconnected components, and randomized ordering. The runtime tests cover shared observation, explicit merge conflicts, four unlink-policy families, stable resources across unrelated edits, port removal, persistence up to binding-ID renaming, and universal factorization of link-respecting interpretations.

A dependency-free browser laboratory renders a chart, pipeline, and table from projected binding resources while displaying quotient classes, resources, provenance, compatibility diagnoses, laws, and counterexamples. A React variant adapts the supplied PBUI visual vocabulary. A small Lean file contains proof terms for relation-to-quotient, factorization, uniqueness, and linked-widget theorems for an indexed finite model. Lean was unavailable in the assembly environment, so the source remains unchecked here; even after checking, it would not certify the TypeScript process.

The principal result is not that union-find is useful. The principal result is that a useful `PortBindingResolverRegistry` can be decomposed into a small denotational kernel, an independently testable optimization, a persistent identity policy, and an operational allocation layer. This decomposition makes both proofs and negative findings sharper.

---

## 1. Problem statement

### 1.1 The ambiguity of “link”

Suppose a workbench contains three independently developed components:

- a chart with a primary-document selector;
- a pipeline with a primary-document selector and a derived output;
- a table with a primary-document selector.

The user wants the chart and pipeline to follow the same selected document. A direct implementation might subscribe each component to the other:

```text
chart change    → update pipeline
pipeline change → update chart
```

This produces several immediate problems:

- the callbacks form a directed graph, not a symmetric identity relation;
- adding a third component requires more propagation edges;
- callback order becomes observable;
- cycles require scheduling policy;
- disconnected local caches can diverge;
- deleting one edge may or may not split the intended group;
- persistence is tied to component-specific addresses;
- there is no canonical explanation for why two values are synchronized.

For an identity link, the intended statement is simpler:

> The local names `chart-1.document` and `pipeline-1.document` denote one global binding.

This statement is structural. It should be represented before deciding how the resulting binding stores a value or schedules updates.

### 1.2 Scope

P06 implements identity links only. It deliberately excludes:

- transformed links such as row selection to filter expression;
- bidirectional lenses between unequal representations;
- stream processing and event scheduling;
- distributed topology reconciliation;
- capability acquisition or dynamic authorization;
- whole-component pushout composition.

These exclusions are positive design boundaries. An API that calls every connection an identity link would make semantic equality depend on arbitrary adapters and update code, defeating the purpose of the quotient model.

### 1.3 Research hypotheses

The artifact evaluates four hypotheses.

1. Identity links are better represented as a generated typed equivalence relation than as pairwise callbacks.
2. Union-find can optimize the quotient computation without defining external binding identity.
3. The quotient universal property provides a useful boundary for downstream interpreters.
4. Unlinking requires provenance and explicit initialization because the quotient has no canonical inverse.

Each hypothesis has a corresponding executable experiment or counterexample.

---

## 2. Semantic objects

### 2.1 Contract fibers

A port contract is:

```ts
interface PortContractSpec {
  contractId: string;
  semanticTag: string;
  payloadSort: string;
  mode: "read" | "write" | "read-write" | "event-source" | "event-sink";
  authorityDomain: string;
  multiplicity: "one" | "optional" | "many";
  updateAlgebra: string;
  lifetime: "component" | "workspace" | "persistent" | "replicated";
}
```

`contractId` names a published contract, but identity compatibility is judged from the normalized semantic fields. Two ports may carry values with the same JavaScript representation and still inhabit different fibers.

Examples:

```text
primary document : DocumentRef, read-write
pipeline output  : DocumentRef, read
```

Both use `DocumentRef`; they do not mean the same interface. Making them one cell would allow a primary selector to overwrite a derived result or would make the primary selector unexpectedly read-only. The compatibility judgment therefore checks:

\[
\begin{aligned}
&\text{semanticTag},\ 
\text{payloadSort},\ 
\text{mode},\ 
\text{authorityDomain},\\
&\text{multiplicity},\ 
\text{updateAlgebra},\ 
\text{lifetime}.
\end{aligned}
\]

This is intentionally conservative. Future studies may define variance or subtyping for particular fields, but P06’s identity operation uses definitional equality.

### 2.2 Port occurrences

A local port occurrence consists of a component identifier, a port name, and a contract:

```ts
interface PortAddress {
  component: string;
  name: string;
}

type PortRef<T> = PortAddress & {
  contract: PortContractSpec;
};
```

The canonical local key is `component.name`, such as:

```text
chart-1.document
pipeline-1.document
pipeline-1.outputDocument
```

A port occurrence is not a binding. Before any links are declared, every port forms a singleton binding class.

### 2.3 Link declarations

An identity link is stored as data:

```ts
interface IdentityLink {
  linkId: string;
  left: PortAddress;
  right: PortAddress;
  mode: "identity";
  provenance?: {
    actor?: string;
    reason?: string;
    logicalTime?: string;
  };
}
```

The link declaration is retained after compilation. This is essential because the quotient alone forgets which generating equations produced a class.

### 2.4 The typed quotient

Fix a normalized contract \(\tau\). Let:

- \(P_\tau\) be the finite set of declared port occurrences with contract \(\tau\);
- \(R_\tau\) be the finite set of active identity-link declarations in that fiber;
- \(s_\tau,t_\tau:R_\tau\rightrightarrows P_\tau\) select the two endpoints of each declaration.

The compiler produces:

\[
q_\tau:P_\tau\to Q_\tau
\]

such that:

\[
q_\tau\circ s_\tau=q_\tau\circ t_\tau.
\]

In `Set`, \(Q_\tau\) is the quotient of \(P_\tau\) by the smallest equivalence relation containing all endpoint pairs. Operationally, it is the connected-component partition of the undirected link graph.

The implementation performs this construction independently in each contract fiber. No class may contain ports with different contract fingerprints.

### 2.5 Universal factorization

Let \(g:P_\tau\to X\) be any interpretation that respects every link:

\[
\forall r\in R_\tau,\quad
 g(s_\tau(r))=g(t_\tau(r)).
\]

Then there is a unique map:

\[
\bar g:Q_\tau\to X
\]

such that:

\[
g=\bar g\circ q_\tau.
\]

The registry exposes a finite executable form:

```ts
const witness = registry.factor({
  "chart-1.document": "document-widget",
  "pipeline-1.document": "document-widget",
  "table-1.document": "table-widget",
});
```

If two members of one class receive different values, factorization is rejected with `interpretation-does-not-respect-links`. Otherwise the returned witness contains one value per binding and commuting checks for every port.

This boundary is useful because a renderer, serializer, subscription allocator, capability ledger, or debugging view may be specified first as a port-level interpretation. If it respects the generated equations, it can operate canonically on bindings instead.

---

## 3. Architecture

The implementation uses six layers.

```text
contracts and port declarations
            ↓
validated typed link graph
            ↓
semantic quotient compiler
            ↓
persistent binding identity assignment
            ↓
resource allocation and projection
            ↓
registry, adapter, and UI interpreters
```

### 3.1 Contracts

`src/contracts.ts` supplies:

- `portContract<T>(...)`;
- `component(id).port(name, contract)`;
- `checkIdentityCompatibility(left, right)`;
- `PayloadSortRegistry` for runtime validation and defaults.

The `T` parameter gives TypeScript users a useful static payload relationship. Runtime checks remain necessary at JSON and process boundaries.

### 3.2 Graph preparation

`prepareGraph` performs all semantic checks before either compiler runs:

- duplicate port keys are rejected;
- conflicting duplicate declarations are rejected;
- duplicate link IDs are rejected;
- link endpoints must be declared;
- endpoint contracts must be identity-compatible;
- reflexive links are accepted but diagnosed as semantically redundant.

Both compilers consume the same prepared graph. This prevents the optimized implementation from silently adopting different validation behavior.

### 3.3 Reference compiler

`compileReference` builds an undirected adjacency map and computes connected components by deterministic breadth-first traversal. It is intentionally ordinary and transparent.

Its purpose is semantic, not performance. The output is normalized by sorted port keys, sorted link IDs, contract fingerprints, and sorted class members. The resulting signature is independent of traversal and input insertion order.

### 3.4 Optimized compiler

`compileOptimized` uses union-find with path compression and union by rank. Importantly, union-find roots are discarded after grouping. The compiler sends only member sets to the common semantic-plan builder.

This means:

```text
union-find representative ≠ class key ≠ persistent binding ID
```

The optimized registry may verify every result against the reference signature. A disagreement is a typed `compiler-disagreement` failure, not a warning.

### 3.5 Semantic class keys

A semantic class receives a deterministic `classKey` derived from:

- the normalized contract fingerprint;
- the complete sorted member list.

A class key identifies one exact partition block at one semantic topology. It is useful for comparison and certificates but is not the long-lived external binding identity, because adding or removing a member necessarily changes it.

### 3.6 Persistent binding identity

`assignPersistentBindings` compares the new semantic partition with the previous persistent plan.

For every old class, it finds overlapping new fragments. On a split, the fragment containing the old anchor retains the old binding ID; if no fragment contains the anchor, the largest deterministic overlap is preferred. On a merge, overlapping prior classes nominate identities, and the earliest birth ordinal wins. Exact unchanged classes retain their IDs.

A fresh class receives an ID of the form:

```text
b-<stable hash of contract fingerprint and members>
```

This strategy has two purposes:

1. external identity never exposes union-find roots;
2. unrelated topology edits preserve unaffected binding and resource identities.

The plan records lineage:

```ts
interface BindingLineage {
  kind: "new" | "unchanged" | "expanded" | "contracted" | "merged" | "split";
  previousBindingIds: readonly string[];
  mergedFrom: readonly string[];
  splitFrom?: string;
  retainedBecause?: string;
}
```

It also records churn metrics for created, retained, and retired classes/resources and rewired subscriptions.

---

## 4. Runtime interpretation

### 4.1 One resource per class

`BindingRuntime` allocates one `SharedCell` for each persistent binding class. A port projection contains:

```ts
interface PortProjection<T> {
  port: PortRef<T>;
  bindingId: string;
  resourceId: string;
  get(): T;
  set(value: T): void;
  subscribe(listener: (value: T, revision: number) => void): () => void;
}
```

Every projection in one class points to the same `SharedCell` object. Therefore, provided a component reads and writes through its projection:

\[
q(p)=q(p')
\implies
v(q(p))=v(q(p')).
\]

This is an aliasing guarantee. It is not a scheduling theorem for arbitrary component-local state.

### 4.2 Mode enforcement

Projection reads and writes check the declared temporal mode.

- `write` and `event-sink` ports cannot be read;
- only `write` and `read-write` ports may be assigned through `setThrough`;
- payload sort validators run before resource mutation.

This does not model linear ownership or effect capability. It prevents straightforward API misuse in the prototype.

### 4.3 Transactional candidate compilation

Topology edits compile a complete candidate plan and allocation plan before committing registry state. If compatibility, merge, split, or payload validation fails, the old plan and runtime remain installed.

The allocation phase decides all values before mutating reused cells. This avoids partially applying a topology edit that later encounters a conflict.

The artifact does not claim multi-process transactionality or asynchronous atomic rendering. It provides synchronous in-process all-or-nothing registry edits.

---

## 5. Value policy is not quotient semantics

### 5.1 Merge policies

If two classes with different values are identified, the quotient says that their ports belong to one future class. It does not say which old value that class should contain.

P06 therefore defines:

```ts
type MergePolicy =
  | { kind: "require-equal" }
  | { kind: "preserve-winner" }
  | { kind: "prefer-left"; left: PortAddress }
  | { kind: "prefer-right"; right: PortAddress }
  | { kind: "user-choice"; value: unknown };
```

`require-equal` is the default. Unequal source values cause `merge-value-conflict`. The browser and React demonstrations ask the user to choose a value before installing the link.

`preserve-winner` follows persistent binding-ID retention. It is deterministic but represents a policy choice, not a theorem.

### 5.2 Unlink policies

Removing one stored equation causes the compiler to recompute the generated relation. The resulting partition may remain unchanged if another path still connects the endpoints, or it may split one class into several classes.

The quotient does not remember independent pre-link values. P06 requires:

```ts
type UnlinkPolicy =
  | { kind: "copy-current" }
  | { kind: "reset" }
  | { kind: "history-restore" }
  | { kind: "user-choice"; values: Record<string, unknown> };
```

- `copy-current` copies the shared value to every new class;
- `reset` uses the payload-sort default;
- `history-restore` uses stored detached values when available, with warnings for missing or ambiguous history;
- `user-choice` requires explicit values for new classes.

None is an inverse of quotienting. `history-restore` is a history-based product feature layered on top of topology semantics.

### 5.3 Port removal

Removing a port also removes incident link declarations and recompiles the quotient. Surviving nonempty classes retain resources when possible. An empty class is never materialized.

---

## 6. The registry API

The stateful API is `PortBindingResolverRegistry`.

### 6.1 Declare and compile

```ts
registry
  .declare(chartDocument, { sort: "document", key: "doc-a" })
  .declare(pipelineDocument, { sort: "document", key: "doc-b" })
  .compile({ engine: "optimized" });
```

Declarations before the first compile are accumulated without hidden global state. Dynamic ports use `addPort` after compilation.

### 6.2 Check a proposed identity link

```ts
const judgment = registry.checkLink(chartDocument, pipelineDocument);
```

A rejected result identifies every mismatching field and provides typed diagnostics. The method has no side effect.

### 6.3 Add an equation

```ts
registry.identify(chartDocument, pipelineDocument, {
  linkId: "chart-pipeline-document",
  mergePolicy: { kind: "prefer-left", left: chartDocument },
  provenance: {
    actor: "analyst",
    reason: "compare the pipeline result with the chart",
  },
});
```

The operation recompiles from stored declarations. It does not mutate union-find in place and then attempt to recover from failure.

### 6.4 Remove an equation

```ts
registry.unlink("chart-pipeline-document", {
  policy: { kind: "copy-current" },
});
```

No default is permitted at this API boundary.

### 6.5 Projection and allocation

```ts
const p = registry.projection(chartDocument);
p.get();
p.set({ sort: "document", key: "doc-b" });
p.subscribe((value, revision) => { /* render */ });
```

The builder API additionally provides `allocate(interpreter)`, applying one interpreter invocation to each binding class.

### 6.6 Explain

```ts
registry.explain([chartDocument, pipelineDocument]);
```

The explanation contains:

- requested port keys;
- binding class and resource when common;
- each projection;
- a path of generating link IDs between each requested pair;
- a human-readable summary.

This is provenance for topology, not a general proof object for arbitrary application behavior.

### 6.7 Factor

```ts
registry.factor(portInterpretation, equality);
```

This checks the premise of the quotient universal property and constructs one value per binding. It is useful for interpreters that should be invariant under the local naming of linked ports.

### 6.8 Snapshot

`registry.snapshot()` serializes ports, active declarations, persistent plan, resource snapshots, projection snapshots, and registry events. It excludes subscribers and executable callbacks.

---

## 7. Common process adapter

The JSONL adapter exposes the project through `pbui-research/0.1`.

Supported capabilities are:

- `bindings.check-link`;
- `bindings.compile`;
- `bindings.edit`;
- `bindings.explain`;
- `bindings.allocate`;
- `bindings.factor`.

The adapter distinguishes:

- `ok` — operation completed;
- `rejected` — the request was meaningful but violated a semantic precondition;
- `unsupported` — outside the P06 fragment;
- `error` — malformed input or internal failure.

For example, `links.propagate` and `replica.merge` return `unsupported` rather than pretending identity wiring includes transformed or replicated behavior.

The adapter sorts declarations before compilation to stabilize experiment traces. It records the assumption that an absent merge policy in fixture compilation uses a named preference; production callers should supply the policy explicitly.

---

## 8. User-facing demonstrations

### 8.1 Dependency-free browser laboratory

`web/` is the primary reproducible visual artifact. It imports only `dist/index.js` and runs through a small static server.

The user can:

1. inspect chart, pipeline, and table document ports;
2. select two endpoint cards;
3. see a compatibility judgment;
4. choose a merge-value policy;
5. add an identity equation;
6. change the document from either widget;
7. observe all class projections display the same resource ID and value;
8. add a third port transitively;
9. remove one declaration under a chosen unlink policy;
10. inspect classes, projection graph, provenance, laws, counterexamples, and trace;
11. run randomized differential tests in the browser;
12. test universal factorization and a deliberately invalid interpretation.

The browser widgets do not keep independent copies of the selected document. Their `<select>` controls read from and write through the registry.

### 8.2 React laboratory

`react/P06PortBindingLab.jsx` adapts the supplied JSX foundation’s visual language:

- paper-like palette and heavy borders;
- typed presentation wrappers with keyboard behavior;
- shell-level interaction mode;
- chart, pipeline, table, source-browser, inspector, and trace tiles;
- hover documentation and right-click inspection;
- user-visible conflict resolution.

The semantic change is substantial. The original presentation wrapper coordinated an accept request by matching a presentation type. The P06 wrapper presents typed ports and coordinates an endpoint-linking mode. Compatible ports become selectable; incompatible ports are diagnosed; unequal resources prompt for a merge policy; and the post-link widgets render from generated projections.

The component intentionally remains a host adapter. The dependency-free demo is used for artifact verification so that React package management cannot obscure the semantic kernel.

### 8.3 Keyboard operation

Port cards are buttons or keyboard-focusable presentations. Enter and Space activate them. Form controls use native keyboard semantics. Motion is disabled under `prefers-reduced-motion` in the React adapter. The demo does not claim a completed accessibility study; it establishes the baseline acceptance criterion that core scenarios are keyboard-operable.

---

## 9. Validation

### 9.1 Unit and scenario tests

The delivered Node test suite currently contains twenty tests.

Contract tests establish:

- payload-sort equality alone is insufficient;
- definitionally equal contracts are accepted.

Compiler tests establish:

- transitive closure;
- reference and optimized semantic agreement;
- duplicate and insertion-order invariance;
- incompatible fibers cannot be merged after type erasure.

Generated tests establish:

- 2,000 seeded typed graphs produce the same normalized partition under both compilers.

Runtime and registry tests establish:

- conflicting merge values require an explicit policy;
- linked endpoints share one resource and update together;
- unlink requires an explicit policy;
- copy-current does not claim inversion;
- unrelated topology edits preserve document-resource identity;
- removing a port preserves surviving nonempty classes;
- link-respecting interpretations factor through classes.

Persistence tests establish:

- serialized declarations reconstruct the same relation up to external ID renaming;
- external binding IDs are not port names or union-find roots.

Adapter tests establish:

- an identity-link trace returns one allocated resource;
- semantic-fiber mismatches are rejected;
- unlink without a policy is rejected;
- transformed and replicated operations are typed unsupported.

### 9.2 Verification command

`npm run verify` runs all tests and then parses and answers mandatory shared traces relevant to P06. Identity linking is executed. Concurrent topology and transformed-link traces are answered with valid typed protocol results while remaining outside the implemented semantics.

### 9.3 Empirical compiler measurements

The recorded benchmark uses Node.js 22.16.0 on Linux/x64 with an AMD EPYC 9V74 processor. It is a single-process compiler microbenchmark and excludes browser rendering, runtime allocation, and network work.

Representative mean times from the included run are:

| Ports | Links | Reference mean | Optimized mean |
|---:|---:|---:|---:|
| 10 | 8 | approximately 0.11 ms | approximately 0.06 ms |
| 100 | 94 | approximately 0.66 ms | approximately 0.45 ms |
| 1,000 | 947 | approximately 16.1 ms | approximately 17.3 ms |
| 5,000 | 4,739 | approximately 338.3 ms | approximately 316.6 ms |
| 10,000 | 9,480 | approximately 1.37 s | approximately 1.33 s |

The mixed and relatively small differences across sizes reveal that normalization, hashing, sorting, contract checking, and plan construction dominate this prototype. This is a useful negative result: substituting union-find does not by itself make the entire compiler near-linear when the remainder of the pipeline performs substantial canonicalization work.

These measurements are empirical observations from one environment, not complexity proofs. The script records sample counts, mean, standard deviation, median, fifth and ninety-fifth percentiles, and extrema.

### 9.4 Churn observations

Persistent identity tests show that an edit in the row-selection fiber does not replace the primary-document resource. The plan records resource and subscription churn explicitly. The implementation currently recompiles the complete finite graph on every topology edit; it preserves unaffected runtime resources through persistent class matching rather than through an incremental dynamic-connectivity algorithm.

---

## 10. Mechanized core

`proofs/Main.lean` uses only Lean’s `Init` library.

The model defines:

```lean
inductive Contract where
  | primaryDocument
  | rowSelection
  | derivedDocument

inductive Port : Contract → Type where
  | chartDocument : Port .primaryDocument
  | pipelineDocument : Port .primaryDocument
  | pipelineOutputDocument : Port .derivedDocument
  -- ...
```

The contract index prevents an invalid proposition such as linking the chart primary document to the pipeline derived output from being well-typed.

`Linked` is the equivalence closure generated by two primitive document-link declarations. `Binding c` is a Lean quotient by the resulting setoid. The file states and supplies proof terms for:

- `Linked p q → project p = project q`;
- existence of a quotient factor for every link-respecting interpretation;
- commutation of the factorization triangle;
- uniqueness of the factor;
- chart and pipeline project to the same binding;
- transitivity identifies chart and table;
- linked projections yield equal resources;
- applying `f : Binding primaryDocument → Widget` yields equal widgets.

The executable `main` renders the chart, pipeline, and table binding as the same document-picker widget.

### 10.1 Proof boundary

The Lean model is not generated from the TypeScript source, and the TypeScript plan does not carry a proof term checked by Lean. Therefore:

- quotient and factorization theorems are **intended to be proved for the Lean model**, pending an independent run of the pinned toolchain;
- correspondence to TypeScript is **example-tested and reviewed**;
- optimized/reference equivalence is **property-tested on finite generated graphs**;
- arbitrary future TypeScript changes are **not certified**.

A later P14 integration could define a serialization format for a binding plan and a small independent checker or produce extracted code from a common formal core.

---

## 11. Counterexamples and negative findings

### 11.1 Payload sort only

A primary document and a derived document both carry `DocumentRef`. A checker that compares only `payloadSort` accepts an unsound identity link. The repair is a complete identity contract.

### 11.2 Pairwise callback chain

With callbacks `A → B` and `B → C`, a write to `C` need not update `A` or `B`. The callback graph does not automatically generate symmetry and transitivity. The repair is one resource per equivalence class or another semantics that explicitly provides those laws.

### 11.3 Representative as persistent ID

Union order and rank heuristics can choose different roots for the same equivalence relation. Serializing roots makes persistence depend on optimization details. The repair is an independent persistent-ID assignment.

### 11.4 Unlink without declarations

The partition `{A,B,C}` is compatible with several generating edge sets. The quotient does not reveal which `A-B` declaration should be removed. The repair is to persist declarations and recompile.

### 11.5 Shadow state

Even if `chart.document` and `pipeline.document` project to one binding, components can diverge if they render from independent local caches. The quotient guarantees equality only through the generated interpretation. The repair is to render from projections or prove a separate synchronization relation.

### 11.6 Union-find is not the performance story

The benchmark shows that canonicalization and plan production dominate large cases in this prototype. Replacing breadth-first search with union-find changes only part of the pipeline. A production optimizer should profile hashing, sorting, contract normalization, provenance construction, and persistent class matching before claiming asymptotic gains.

### 11.7 Dynamic deletion is recompilation

The optimized compiler is not a fully dynamic connectivity data structure. Link deletion causes deterministic recompilation from retained declarations. This is acceptable for the bounded artifact and makes semantics clear. It is not a proof that the chosen data structure will meet production edit-latency requirements at arbitrary scale.

---

## 12. Composition boundaries

### 12.1 P07 open components

P07 may use P06 as the identity-wiring backend for compatible ports. It should consume contracts, declarations, classes, and projections rather than union-find state. Whole-component composition remains P07’s concern.

### 12.2 P08 bidirectional links

P08 must not encode a lens as an identity link. A transformed link has different endpoint contracts and a consistency-restoration procedure. P06 can allocate cells at its endpoints, but it cannot prove the lens laws.

### 12.3 P09 interaction machines

A coalgebraic link-creation workflow may call `checkLink`, collect a merge policy, call `identify`, and expose the resulting state. P06 does not define the workflow state machine.

### 12.4 P10 effect handlers

An algebraic interaction program can request `ConnectIdentityPorts`. A handler can delegate to the JSONL adapter or registry. The program should distinguish rejection from unsupported transformed linking.

### 12.5 P12 replicated topology

P12 should replicate link declarations and explicit policies or commands, then deterministically recompile a quotient. Replicating persistent binding IDs directly is insufficient because concurrent topology edits require their own merge semantics. P06 does not claim convergence.

### 12.6 P14 mechanized kernel

P14 receives the Lean model, serializable plan schema, and guarantee classification. The next step is an independently checked plan certificate or extracted reference compiler.

---

## 13. Trust and guarantee classification

| Claim | Level | Evidence | Limit |
|---|---|---|---|
| The indexed Lean relation quotients linked ports | proof source, unchecked here | `proofs/Main.lean` | Finite hand-written model only; Lean unavailable |
| Link-respecting maps factor uniquely | proof source, unchecked here | `proofs/Main.lean` | Lean model only; Lean unavailable |
| Reference and optimized compilers agree | property-tested | 2,000 seeded generated graphs plus per-compile check | Not exhaustive over all JavaScript inputs |
| Linked runtime projections share one cell | example-tested | registry and adapter tests | Components can bypass projections |
| Link order and duplicates preserve relation | example/property-tested | compiler and generated tests | Assumes deterministic normalized contracts |
| Unrelated edits preserve resource identity in tested case | example-tested | registry test | No general mechanized incremental proof |
| Performance at recorded sizes | empirical | `benchmarks/results.json` | One machine and implementation version |
| Distributed replicas converge | unsupported | none | Assigned to P12 |
| Transformed links satisfy consistency laws | unsupported | none | Assigned to P08 |

This table is also encoded in the capsule manifest so composition tooling does not infer stronger guarantees from capability names.

---

## 14. API design assessment

### 14.1 What worked

The most successful decomposition is:

```text
semantic partition
≠ persistent identity
≠ runtime value
≠ user interaction workflow
```

Keeping these separate made conflicts explicit and tests local.

The typed compatibility matrix produced useful diagnostics. In particular, it prevents a common failure where two ports with the same TypeScript payload are assumed to be interchangeable.

Retaining link declarations rather than only classes made unlinking intelligible and explainable.

The reference compiler was inexpensive to write and highly valuable. It gave the optimized implementation a concrete oracle and made generated testing meaningful.

### 14.2 What remains provisional

The persistent-ID policy is useful but not canonical. Anchor retention and birth-ordinal precedence are product policies. Another system may prioritize component ownership, explicit user-named bindings, or stable server-issued IDs.

The contract equality judgment is conservative. Some modes may admit safe variance, and some authority domains may be related through delegated capabilities. Those extensions need explicit semantics rather than ad hoc exceptions.

The `SharedCell` runtime is intentionally simple. It does not define batch transactions, effect scheduling, backpressure, or distributed updates.

The JSONL adapter is a research seam, not a proposed ergonomic application API.

### 14.3 Smallest trusted kernel

A future reimplementation should trust as little as possible:

1. normalize and compare contracts;
2. validate endpoint declarations;
3. compute the generated equivalence relation;
4. emit classes and projection;
5. check totality, disjointness, contract homogeneity, and endpoint equality.

Persistent IDs, resource allocation, UI, provenance prose, and merge policies should be built above that kernel.

---

## 15. Reproduction

From the artifact root:

```sh
npm run verify
npm run benchmark
npm run demo
```

The first command runs tests and relevant shared traces. The second writes `benchmarks/results.json`. The third starts the local browser lab.

With TypeScript 5.8.3 available:

```sh
npm run build
```

With Lean 4.19.0 available:

```sh
cd proofs
lean Main.lean
lean --run Main.lean
```

The delivered environment did not contain Lean, so the Lean file was syntax-reviewed but not executed here. This limitation is recorded rather than converted into a proof claim.

---

## 16. Conclusions

P06 supports the claim that identity wiring is usefully modeled as a typed quotient of port occurrences generated by explicit link declarations. The quotient formulation provides laws that pairwise callbacks do not: equivalence closure, insertion-order independence, canonical factorization, and a clear notion of one global binding behind multiple local names.

The implementation also demonstrates the limits of that statement. Quotienting does not select a value when classes merge, recover private values when a class splits, schedule events, grant authority, prevent components from keeping shadow state, or reconcile offline replicas. Treating those matters as explicit adjacent layers is more powerful than trying to hide them inside “link.”

The strongest practical architecture emerging from the project is therefore:

```text
small typed quotient kernel
        + explicit persistent identity policy
        + explicit allocation/value policy
        + inspectable interaction layer
        + independent conformance oracle
```

This architecture is suitable for the later composition pass because it exports stable semantic data and clear reliance conditions rather than an opaque registry object whose correctness depends on one implementation technique.
