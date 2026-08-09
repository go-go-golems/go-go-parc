---
title: "PBUI Research Capsules P01-P04"
subtitle: "Implemented reference systems for identity, occurrence lifecycle, typed selection, and recursive rules"
author: "Research prototype package"
date: "2026-08-05"
toc: true
toc-depth: 3
numbersections: true
---


# PBUI P01-P04 Implementation Report

## Status

Four research capsules have been implemented as independent TypeScript projects. Together they contain:

- 2,592 lines of TypeScript source;
- 44 executable tests;
- four runnable demonstrations;
- no runtime package dependencies;
- a reference implementation for each semantic subsystem;
- explicit limitations and proof obligations;
- a shared first-pass interoperability contract.

The command below builds and tests all four capsules:

```bash
npm test
```

All 44 tests pass under Node.js 22.16.0 and TypeScript 5.8.3 in the delivery environment.

## Research objective

The implementation tests whether the first four PBUI subsystems can be separated without losing the information needed for later composition:

```text
semantic identity
  -> committed visual occurrence
  -> inspectable selection
  -> recursive derived applicability
```

The projects remain independent. This is a methodological choice rather than an unfinished integration. If P03 imported P01's internal registry or P04 imported P03's unifier during the first pass, their interfaces would reflect one implementation rather than independently investigated requirements.

## P01 result: identity is a sort-indexed equivalence relation

P01 replaces ambient object/reference equality with an explicit semantic coordinate:

```ts
interface SubjectRef {
  sort: string;
  key: string;
}
```

The prototype supports three independent mechanisms:

1. **Key identity:** values of one sort map to stable keys.
2. **Representation identity:** a token or alternate visual value maps to the same sort/key.
3. **Alias identity:** explicit evidence-bearing edges generate an equivalence relation among keys of one sort.

This separation prevented several common conflations during implementation:

- a current snapshot is not the identity;
- a JavaScript object is not the identity;
- a display form is not the identity;
- an alias edge is not the entire equivalence class;
- a canonical representative is not the definition of sameness.

The durable alias graph retains provenance and supports removal. The current implementation recomputes connected components by graph traversal. That is deliberately slower but semantically clearer than persisting only a union-find root.

### Main validated cases

- Project object and project-ID token identify one subject.
- Equal labels and equal object fields do not merge different keys.
- Equal key strings in different sorts remain different.
- Alias evidence is transitive and reversible by edge removal.
- Canonicalization is deterministic under link insertion order.
- Entity snapshots reject stale and same-revision conflicting data.

### Main unresolved question

Should the production identity layer expose a single canonical reference or preserve a presented reference plus evidence of equivalence to a canonical reference? The implementation report recommends preserving both because audit, user explanation, and import migration need the original coordinate.

## P02 result: occurrence publication must be commit-phase and generation-scoped

P02 models a visual occurrence as committed semantic state. Preparation is intentionally not visible:

```text
prepare -> commit -> update* -> cleanup
```

Every committed occurrence ID has a generation. Update and remount produce a newer generation. Cleanup carries a lease and succeeds only for the currently active generation.

This solves a concrete race:

```text
mount X@1
mount replacement X@2
late cleanup X@1
```

Without a generation check, the late cleanup deletes the replacement. With a lease, it becomes a no-op and an explicit lifecycle event.

The same generation is included in activation evidence. A delayed click cannot be accepted after an occurrence has been repurposed for another subject.

### Main validated cases

- Prepared but abandoned renders leave no occurrence.
- Committing one preparation twice is idempotent.
- Old cleanup cannot remove a newer generation.
- Updates are atomic from the registry observer's perspective.
- Several occurrences can present one subject.
- Surface, visibility, reachability, and enabled status remain distinct.
- Activation evidence expires after update or unmount.
- Virtualization removes only the occurrence.

### Main unresolved question

The pure commit protocol now needs at least two concrete React adapters for comparison: one based on layout effects and one based on an external-store registration service. Their semantic traces should be checked against the same P02 transition model before the production API is chosen.

## P03 result: unification makes selectors proof-relevant rather than Boolean

P03 implements first-order terms and a syntactic unifier. A pattern such as:

```text
field(?doc, ?name, "number")
```

returns bindings when matched against a ground field term. Those bindings can be consumed by the inspectable predicate language and retained in evidence.

This is materially stronger than a callback returning `true`:

```text
Boolean callback:
  accepted

unification-based selector:
  accepted because pattern P unified with term T
  using substitution sigma
  and predicate evidence E held under sigma
```

The reference evaluator scans a sort. The compiled evaluator extracts simple equality indexes and then applies the complete semantics. Tests compare their candidate keys, preserving a slow semantic oracle for later optimizer work.

### Main validated cases

- Constructor decomposition and variable elimination.
- Repeated-variable consistency.
- Occurs-check rejection.
- Substitution-composition law on examples.
- A more specific unifier factors through a computed general solution on the tested variables.
- Reference and indexed evaluators agree on fixture candidates.
- Dependency analysis supports serialization and index planning.
- Opaque JavaScript is visible as a guarantee downgrade.
- Evidence is invalidated by store revision changes.

### Use of the unification chapter

The implementation follows the chapter's core syntactic distinctions:

- terms are generated from variables and constructors;
- substitutions extend through term structure;
- a useful solver constructs a general unifier, not only a yes/no answer;
- the occurs check prevents cyclic finite-term substitutions;
- syntactic and equational unification are distinct problems.

The report also adopts a caution from the chapter's category-theoretic reformulation: most-general unifiers and coequalizers have related factorization intuitions, but the uniqueness condition of a categorical coequalizer is stronger. The selector result is therefore called a unifier/substitution, not a quotient.

Primary source: <https://www.cs.bu.edu/fac/snyder/publications/UnifChapter.pdf>

## P04 result: recursive UI semantics can use a finite least-fixed-point kernel

P04 implements a function-free, range-restricted rule language. The function-free restriction is important: without fresh term construction, a finite active constant domain yields only finitely many possible ground atoms at fixed arities.

The reference evaluator computes each stratum to quiescence. The positive agenda evaluator reacts to new facts and anchors rule-body occurrences to them. A persistent positive engine supports insertion-only incremental updates.

Provenance records the rule, substitution, positive premises, and checked negative atoms for each derivation. A certificate checker reconstructs the instantiated rule and recursively verifies premises.

### Main validated cases

- Recursive transitive closure reaches the expected least fixed point.
- Agenda and naive evaluators agree on the fixture.
- Rule and base-fact order do not change the result.
- Re-evaluation from the completed fact set is idempotent.
- Stratified negation derives actions only in the completed lower-stratum absence case.
- Recursion through negation is rejected.
- Unsafe head/negative variables and function-generating terms are rejected.
- Unification enforces repeated-variable joins.
- Insertion-only incremental evaluation matches full recomputation on the fixture.
- Recursive derivations are explainable and checkable.

### Main unresolved question

The generic rule engine and specialized algorithms overlap. Link connectedness, for example, can be derived by recursive rules, but a quotient compiler will use graph algorithms. The integration pass should treat P04 as the declarative specification and compare specialized implementations against its finite reference semantics.

## Why P01 does not use the P03 unifier

The additional theoretical material might suggest treating subject identity as a unification problem. The implementation deliberately rejects that design.

Unification solves equations containing variables in a chosen term theory. P01 identity compares ground application coordinates under an application-defined key/alias theory. Two structurally similar projects do not become one subject because a substitution exists between their descriptions.

The subsystems may interact later:

```text
P03 pattern variable ?subject
  binds to a P01 SubjectRef
```

but the substitution does not establish the validity of the P01 identity relation.

## Why P04 contains its own unifier

The first-pass condition requires independent subsystem evaluation. P04 therefore contains a copy of the small first-order term implementation rather than importing P03.

This duplication creates a useful phase-two experiment:

1. compare both unifiers over a shared generated corpus;
2. define the minimum common interface;
3. determine whether selectors need features rules do not, or vice versa;
4. replace both only after differential conformance is established.

Premature sharing would hide those differences.

## Composition hypothesis for the next pass

A composed selection operation can retain four evidence objects:

```ts
interface CompositeSelectionEvidence {
  identity: IdentityEvidence;        // P01
  occurrence: ActivationEvidence;   // P02
  selector: SelectionEvidence;      // P03
  derivation: RuleEvidence;         // P04
}
```

A commit is accepted only if all four remain valid at their respective revisions. The revisions should remain a tuple, not be collapsed into one global counter.

The first integration constellation should implement this narrow flow:

1. register a P01 field subject;
2. commit two P02 occurrences presenting it;
3. export occurrences into a P03 selector store;
4. select one occurrence using a parameterized pattern;
5. export the selected candidate and capability facts to P04;
6. derive an `inspect` action;
7. mutate or unmount one input;
8. show which evidence component invalidates and why.

This is a better first integration target than building a complete React menu system.

## Validation summary

| Capsule | TypeScript source lines | Tests | Result |
|---|---:|---:|---|
| P01 | 476 | 9 | pass |
| P02 | 405 | 11 | pass |
| P03 | 843 | 13 | pass |
| P04 | 868 | 11 | pass |
| **Total** | **2,592** | **44** | **pass** |

The checks establish executable behavior for the prototypes. They do not establish full metatheoretic soundness, completeness, or refinement to React. The project READMEs list proof obligations individually.

## Recommended next experiments

1. **Differential unifier corpus:** run P03 and P04 against generated term-equation suites and compare substitutions modulo variable renaming.
2. **P01 quotient model in Lean:** prove equivalence laws and evidence-path soundness for finite alias graphs.
3. **P02 trace model:** express prepare/commit/update/cleanup in TLA+ and model stale cleanup and double activation.
4. **P03 compiler proof:** structurally prove that every extracted index is a sound candidate restriction and that full predicate evaluation preserves completeness.
5. **P04 evaluator proof:** mechanize fixed-point soundness for the positive fragment and validate agenda/reference equivalence.
6. **Evidence invalidation study:** compare coarse global revisions with dependency-specific version vectors.
7. **User explanation prototype:** render P03 and P04 evidence as concise “why selectable?” and “why available?” explanations.
8. **Specialized graph compiler:** compare P04 `sameBinding` closure with a P06-style quotient implementation.

## Reproduction

```bash
cd pbui-p01-p04
npm test
npm run demo
```

No package installation is required when Node.js and TypeScript are already available.


\newpage


# P01 - Semantic Identity and the Subject Registry

## Research question

How should a presentation-based UI decide that two independently produced values denote the same application subject, without confusing domain identity with JavaScript reference equality, structural equality, React reconciliation keys, or screen occurrence identity?

This capsule builds a small executable answer based on:

- nominal semantic sorts;
- sort-scoped stable keys;
- alternate representation declarations;
- explicit, evidence-bearing alias edges;
- reversible equivalence classes derived from those edges;
- revisioned current snapshots that remain separate from identity.

## Why this subsystem exists

The current PBUI reference shape carries a semantic type and a value:

```ts
{ type: "field", value: { docId: "doc-readings", name: "temperature" } }
```

That is enough to render and dispatch local actions, but it leaves several questions unspecified:

- Are two newly allocated field objects with equal coordinates the same field?
- Is a project card presenting a project object the same subject as a token presenting its project ID?
- Can a document ID and a user ID both equal to `"1"` collide?
- What happens when imported identifiers are discovered to alias canonical identifiers?
- Can an alias later be revoked without losing its provenance?
- Does an immutable update change identity?
- How is stale captured data detected?

P01 makes those decisions explicit.

## Executable model

### Semantic sorts

A sort defines a domain of identity:

```ts
interface SubjectSort<A> {
  name: string;
  key(value: A): string;
  revision?(value: A): number;
  fingerprint?(value: A): string;
}
```

Example:

```ts
const Project = {
  name: "project",
  key: project => project.id,
  revision: project => project.revision,
};
```

The semantic reference is:

```ts
interface SubjectRef {
  sort: string;
  key: string;
}
```

The sort is part of the identity domain. Therefore:

```text
project:1 != document:1
```

unless an application deliberately defines a common super-domain outside this registry.

### Alternate representations

A representation explains how another displayed value identifies a subject of an existing sort:

```ts
const ProjectId = {
  name: "project-id-token",
  sort: Project,
  key: id => id,
};
```

Both calls produce the same semantic coordinate:

```ts
registry.ref(Project, project)
registry.refFromRepresentation(ProjectId, project.id)
```

No conversion of the visual representation into an entity snapshot is required merely to establish identity.

### Alias graph

Sometimes two different keys are discovered to denote one subject:

```ts
registry.addAlias(
  { sort: "project", key: "legacy-17" },
  { sort: "project", key: "project-17" },
  { reason: "workspace import", authority: "migration-v4" },
);
```

Aliases are stored as explicit edges. The relation used by `same` is the reflexive, symmetric, transitive closure of those edges.

The implementation intentionally does not persist only a destructive union-find partition. Retaining generating edges provides:

- provenance;
- deterministic export;
- alias removal;
- recomputation after corrections;
- a clear distinction between asserted equations and their equivalence closure.

For the small registry prototype, breadth-first graph traversal is adequate. A production runtime can cache connected components or use dynamic connectivity while retaining the edge graph as the source of truth.

### Comparison evidence

`compare(left, right)` returns either:

```ts
{ same: true, evidence: { kind: "same-key", ... } }
```

or:

```ts
{
  same: true,
  evidence: {
    kind: "alias-path",
    path: [edge1, edge2],
  },
}
```

or a negative reason such as `different-sort` or `disconnected`.

This evidence is useful for inspectors, migration diagnostics, audit trails, and future proof-carrying adapters. The Boolean convenience method `same` is derived from the evidence-producing operation.

### Canonicalization

`canonical(ref)` returns the lexicographically least key in the current equivalence class. This policy is deterministic under alias insertion order.

The canonical representative is a runtime normalization policy, not the definition of identity. Consumers that need persistent application-preferred keys should define a stronger authority or ranking policy rather than depend on lexicographic order.

### Revisioned snapshots

Identity and current data are separate:

```ts
registry.register(Project, {
  id: "project-17",
  title: "Compiler",
  revision: 4,
});
```

The registry rejects:

- a lower revision for the same semantic reference;
- a different fingerprint at the same revision.

A greater revision updates the current snapshot without changing the subject reference.

This demonstrates an important design rule:

> A semantic reference should remain stable while the value currently describing that subject evolves.

## Formal model

For each sort `S`, let `K_S` be its set of keys. Alias declarations generate a relation:

\[
E_S \subseteq K_S \times K_S.
\]

The semantic sameness relation is the least equivalence relation containing `E_S`:

\[
\sim_S = \operatorname{EqClosure}(E_S).
\]

A subject reference is a pair:

\[
(S,k), \qquad k \in K_S.
\]

Sameness is defined by:

\[
(S,k) \approx (T,j)
\iff
S=T \land k \sim_S j.
\]

The implementation tests reflexivity, symmetry, and transitivity over generated finite graphs.

A snapshot store is a partial map:

\[
\operatorname{snapshot} : \sum_S K_S \rightharpoonup
  (\mathbb{N} \times \operatorname{Value}_S).
\]

Its update rule requires monotone revisions. This order is independent of the alias equivalence relation.

## Relationship to unification theory

Unification provides a useful contrast but is not the implementation of subject identity.

A first-order unifier answers whether variables can be substituted so that symbolic terms become equal. P01 receives ground domain coordinates and application assertions. It does not infer that two projects are identical because their fields can be unified, nor does it search for a substitution between arbitrary entity values.

The additional Baader-Snyder chapter is therefore used negatively here:

- **unifiability is not domain identity**;
- a domain identity theory must be declared rather than accidentally inherited from object structure;
- if future aliases are inferred modulo an equational theory, that theory and its decidability properties must be explicit;
- the term-DAG equivalence-class techniques motivate possible optimization, but do not replace the domain contract.

See the repository-level [`docs/UNIFICATION-NOTES.md`](../docs/UNIFICATION-NOTES.md).

## Tests and experiments

The capsule currently contains nine executable tests covering:

1. one subject through an entity object and an ID token;
2. rejection of accidental structural equality;
3. sort-domain collision isolation;
4. reflexive, symmetric, transitive aliases with path evidence;
5. deterministic canonicalization under different edge orders;
6. removal of an alias and resulting component split;
7. stale and conflicting revision rejection;
8. serialization and restoration of alias topology;
9. equivalence laws over a generated finite graph.

Run:

```bash
npm test
npm run demo
```

## Results established by the prototype

### By construction

- Cross-sort aliases are rejected.
- Alternate representations can only target declared sorts.
- Snapshot identity is the pair `(sort, key)` and does not depend on object allocation.
- The durable alias state retains its generating evidence.

### By executable tests

- `same` behaves as an equivalence relation on the tested finite graph.
- Canonicalization is independent of alias insertion order for the selected policy.
- Removing an edge can split an equivalence class.
- Snapshot revision checks reject stale or conflicting values.

### Not yet proved

- completeness and minimality of the path evidence;
- asymptotic guarantees for a production dynamic-connectivity implementation;
- correctness of a future union-find cache with deletion;
- correspondence between TypeScript and a mechanized quotient model;
- safe behavior under concurrent distributed alias edits.

## Deliberate limitations

1. Keys are strings. A production API should accept codecs and nominal key types.
2. The default fingerprint is a stable best-effort serialization, not a cryptographic content hash.
3. Lexicographic canonicalization is a neutral experiment policy, not a product recommendation.
4. Alias imports allocate new local alias IDs. Semantic topology, not those IDs, is the portable invariant.
5. The registry does not resolve authorization for alias creation.
6. The registry does not infer aliases from labels, values, or unification.
7. Snapshots are in-memory and single-process.

## Integration seam

P01 exports `SubjectRef`. P02 should attach that reference to occurrences. P03 should query records keyed by it. P04 should encode it into ground facts through an adapter.

A composed implementation must decide whether selector evidence stores the original reference, the current canonical reference, or both. The recommended approach is both:

```ts
{
  presented: SubjectRef,
  canonicalAtRevision: SubjectRef,
  identityEvidence: SameSubjectEvidence,
}
```

That preserves what the user acted on while allowing canonical state access.

## Research extensions

- formalize the alias graph as a setoid and its quotient in Lean;
- compare explicit graph closure, union-find caching, and fully dynamic connectivity;
- add authority and revocation semantics to alias evidence;
- model identity migration across schema versions;
- test identity under fork, merge, import, and anonymization;
- investigate groupoid-style invertible representation witnesses;
- add distributed alias-edge CRDT semantics without collapsing value reconciliation into topology.


\newpage


# P02 - Occurrence Semantics and the Concurrent React Adapter

## Research question

How should a presentation runtime represent the lifetime of a rendered semantic occurrence when a modern renderer may prepare, abandon, commit, update, remount, hide, virtualize, and clean up UI work out of the simple one-render/one-unmount order assumed by imperative registration APIs?

This capsule builds a renderer-neutral commit-phase occurrence registry and tests it against the lifecycle hazards associated with concurrent and strict rendering.

## Subject versus occurrence

A semantic subject is something such as:

```ts
{ sort: "field", key: "doc-readings/temperature" }
```

An occurrence is one addressable presentation of that subject:

```ts
{
  id: "occ-chart-temperature",
  subject: { sort: "field", key: "doc-readings/temperature" },
  forms: ["field-chip"],
  surface: "workspace",
  placement: "placement-chart",
  visible: true,
  reachable: true,
  enabled: true,
}
```

The same subject may have several occurrences: a chart label, table header, source-browser chip, and command-history entry. Removing one occurrence does not remove the subject.

This distinction is required for PBUI input contexts. A subject may be a valid semantic candidate but have no currently mounted pointer-selectable occurrence. Conversely, one subject may be selectable through several visual forms.

## Lifecycle protocol

### Prepare

```ts
const prepared = registry.prepareMount(descriptor);
```

Preparation is pure with respect to the committed registry. It can happen during a speculative renderer phase. If the render is abandoned, `abortPrepared` leaves no semantic occurrence behind.

### Commit

```ts
const lease = registry.commitMount(prepared);
```

Commit publishes one occurrence and returns a generation lease:

```ts
interface OccurrenceLease {
  occurrenceId: string;
  generation: number;
  leaseId: string;
}
```

Committing the same prepared token twice is idempotent.

### Update

```ts
const preparedUpdate = registry.prepareUpdate(lease, nextDescriptor);
const nextLease = registry.commitUpdate(preparedUpdate);
```

An update is atomic. Before commit, readers observe the old descriptor. After commit, they observe the new descriptor and a greater generation. Subject, forms, visibility, reachability, and metadata change as one committed revision.

### Cleanup

```ts
registry.cleanup(lease);
```

Cleanup succeeds only when the lease still names the active generation. An old cleanup cannot delete a newer remount or update.

This is the central stale-cleanup law:

```text
activeGeneration(id) != lease.generation
  => cleanup(lease) is observationally inert
```

## Why generations are necessary

Consider this legal interleaving:

```text
commit occurrence X generation 1
prepare and commit replacement X generation 2
late cleanup for generation 1
```

A registry keyed only by occurrence ID would delete generation 2. The lease makes cleanup conditional on both ID and generation.

The same mechanism protects activation evidence. A click captured against generation 1 is invalid after generation 2 changes the subject or reachability.

## Activation evidence

```ts
interface ActivationEvidence {
  occurrenceId: string;
  generation: number;
  subject: SubjectRef;
  surface: string;
  registryRevision: number;
}
```

`activationEvidence(id)` returns evidence only for an occurrence that is:

- committed;
- visible;
- reachable;
- enabled.

`validateEvidence` checks that the occurrence still has the same generation, subject, and surface and remains activatable.

This prevents a delayed pointer event from selecting a different subject after a keyed component has been repurposed.

## Surface and reachability semantics

The registry records separate facts:

- **mounted:** implied by presence in the registry;
- **visible:** presently rendered rather than intentionally hidden;
- **reachable:** available through the current interaction modality;
- **enabled:** not locally disabled;
- **surface:** workspace, menu, overlay, command palette, or another semantic surface.

These should not be collapsed into one Boolean. A screen-reader surface, pointer surface, and searchable semantic subject set can differ.

`selectable` supports filters but does not itself decide an input-context query. P03 and P04 should derive semantic applicability; P02 supplies committed occurrence facts.

## Renderer-neutral commit bridge

The capsule includes `createCommitPhaseBridge`. It models the portion of a React hook that must remain stable across renders:

```ts
const bridge = createCommitPhaseBridge(registry);
const prepared = bridge.prepare(descriptor);  // render-safe
bridge.commitPrepared(prepared);              // commit phase
bridge.cleanup();                             // effect cleanup
```

A concrete React hook can be built around `useRef` and `useLayoutEffect`. The important constraint is that render must not publish an occurrence.

Illustrative adapter:

```tsx
function useSemanticOccurrence(descriptor: OccurrenceDescriptor) {
  const runtime = useRuntime();
  const bridgeRef = useRef<CommitPhaseBridge>();
  bridgeRef.current ??= createCommitPhaseBridge(runtime.occurrences);

  const prepared = bridgeRef.current.prepare(descriptor);

  useLayoutEffect(() => {
    bridgeRef.current?.commitPrepared(prepared);
    return () => {
      bridgeRef.current?.cleanup();
    };
  }, [prepared]);
}
```

A production hook needs careful memoization so it does not treat every render as a semantic update, and it must align with the chosen React version's external-store recommendations. The capsule isolates the semantic protocol that such a hook must implement.

## Formal model

Let an active occurrence map be:

\[
A : \operatorname{OccurrenceId}
  \rightharpoonup
  (\operatorname{Generation} \times \operatorname{Descriptor}).
\]

A lease is valid in state `A` when:

\[
\operatorname{valid}_A(i,g,\ell)
\iff
A(i)=(g,d) \land d.\operatorname{leaseId}=\ell.
\]

Cleanup is:

\[
\operatorname{cleanup}(A,L)=
\begin{cases}
A \setminus \{L.i\}, & \operatorname{valid}_A(L),\\
A, & \text{otherwise}.
\end{cases}
\]

Commit replaces the current record with a record at a strictly greater generation. Prepared values do not occur in `A`, so abandoning one is unobservable.

An activation certificate is valid only if its generation and semantic coordinates agree with the active record.

## Tests and experiments

The eleven executable tests cover:

1. speculative preparation with no committed side effect;
2. idempotent commit of one prepared mount;
3. stale cleanup after a newer remount;
4. atomic subject and visibility update;
5. rejection of an update using an old lease;
6. several occurrences presenting one subject;
7. surface, visibility, reachability, and enabled filtering;
8. activation evidence invalidation after update and unmount;
9. virtualization removing an occurrence but not its subject coordinate;
10. renderer-neutral prepare/commit/update/cleanup bridge behavior;
11. coherent subscription snapshots after mutations.

Run:

```bash
npm test
npm run demo
```

## Results established by the prototype

### By construction

- Speculative preparation does not alter committed occurrence state.
- Every committed mount or update receives a monotonically increasing generation for its occurrence ID.
- Cleanup and update require a matching lease.
- Occurrence IDs and semantic subject references are separate types and fields.

### By executable tests

- Strict/remount-style late cleanup cannot remove the newest generation.
- Activation evidence becomes invalid after a semantic update.
- Multiple occurrences of one subject remain independently addressable.
- Subscribers see snapshots at coherent registry revisions.

### Not yet proved

- linearizability under actual multithreaded mutation;
- behavior under React Offscreen and future renderer semantics;
- absence of tearing in a concrete `useSyncExternalStore` adapter;
- liveness of keyboard focus transfer during virtualization;
- refinement between DOM event traces and the semantic event protocol.

## Deliberate limitations

1. The prototype is renderer-neutral and does not import React.
2. It uses one active record per `OccurrenceId`; callers must allocate distinct IDs for simultaneous visual copies.
3. It does not derive visibility from the DOM or intersection observers.
4. It does not persist occurrence state; occurrences are transient by definition.
5. It uses exact `(sort, key)` subject comparison. A future adapter should delegate alias-aware comparison to P01.
6. It does not resolve modality precedence when several input contexts are active.
7. It does not decide actions or selection predicates.

## Integration seam

A future composed runtime should publish P02 records as extensional facts:

```text
presents(occurrenceId, subjectSort, subjectKey)
form(occurrenceId, formName)
surface(occurrenceId, surfaceName)
visible(occurrenceId)
reachable(occurrenceId)
enabled(occurrenceId)
generation(occurrenceId, n)
```

P03 can query those records directly. P04 can derive `selectable` and `availableAction`. Before commit, the orchestrator validates P02 activation evidence and P03/P04 evidence together.

## Research extensions

- implement and test a real React `useSyncExternalStore` adapter;
- model focus, hover, pointer capture, and keyboard modality as separate occurrence relations;
- add visibility-observer and virtualization adapters;
- specify occurrence traces as a labeled transition system;
- compare generation leases with epoch-based and capability-based lifecycle models;
- model server-rendered and hydrated occurrences;
- build a TLA+ specification for stale cleanup and double-resolution races;
- prove trace refinement between a React test renderer and the pure occurrence machine.


\newpage


# P03 - Inspectable Typed Selectors and Selection Evidence

## Research question

Can PBUI selection predicates be made inspectable, serializable, optimizable, incrementally maintainable, and evidence-producing without eliminating the ability to call application-specific JavaScript?

This capsule implements a small typed selector language with:

- first-order term patterns;
- syntactic unification and most-general substitutions;
- a first-order predicate AST;
- explicit parameters, attributes, and pattern bindings;
- a reference evaluator;
- a simple indexed compiler;
- dependency and portability analysis;
- proof-relevant selection evidence;
- revision-sensitive evidence validation;
- an explicit opaque-lambda boundary.

## Problem with callback-only selectors

A callback such as:

```ts
reference =>
  reference.type === "field" &&
  reference.value.docId === activeDocument &&
  reference.value.kind === "number"
```

is easy to write but hides information needed by a semantic runtime:

- dependencies;
- candidate indexes;
- serialization;
- worker execution;
- equivalence checking;
- explanation;
- monotonicity analysis;
- incremental invalidation;
- proof by structural induction.

P03 replaces the common first-order fragment with data while preserving a named opaque escape hatch.

## Subject records

The selector evaluator consumes records:

```ts
interface SubjectRecord {
  sort: string;
  key: string;
  term: Term;
  attributes: Record<string, Scalar>;
}
```

Example:

```ts
{
  sort: "field",
  key: "doc-readings/temperature",
  term: field("doc-readings", "temperature", "number"),
  attributes: {
    docId: "doc-readings",
    name: "temperature",
    kind: "number",
    archived: false,
  },
}
```

The term supports structural pattern matching. Attributes support conventional indexed predicates. These representations deliberately overlap so the experiment can compare them.

## Term language and unification

Terms are:

```ts
type Term =
  | { tag: "var"; name: string }
  | { tag: "atom"; value: Scalar }
  | { tag: "node"; symbol: string; args: Term[] };
```

A selector pattern can be:

```ts
field(?doc, ?name, "number")
```

When matched against:

```ts
field("doc-readings", "temperature", "number")
```

unification returns:

```text
?doc  -> "doc-readings"
?name -> "temperature"
```

The substitution is retained in selection evidence and can be referenced by later predicates.

### Algorithm

The implementation is a readable worklist transformation algorithm with these cases:

- delete equal terms;
- orient a variable to the left;
- eliminate a variable by substitution;
- decompose equal constructors;
- reject atom or constructor clashes;
- reject cyclic bindings through the occurs check.

The result is normalized to an idempotent substitution.

The prototype also provides:

- substitution application;
- composition;
- unifier checking;
- idempotence checking;
- a finite `factorSubstitution` experiment showing how a more specific solution factors through a computed general solution on selected variables.

## Selector syntax

```ts
interface Selector {
  id: string;
  description?: string;
  from: string;
  pattern?: Term;
  where: Predicate;
}
```

Example:

```ts
const selector = {
  id: "active-numeric-field-in-document",
  from: "field",
  pattern: node(
    "field",
    variable("doc"),
    variable("name"),
    atom("number"),
  ),
  where: predicate.and(
    predicate.eq(
      expr.attribute("docId"),
      expr.parameter("document"),
    ),
    predicate.eq(
      expr.binding("doc"),
      expr.parameter("document"),
    ),
    predicate.eq(
      expr.attribute("archived"),
      expr.literal(false),
    ),
  ),
};
```

Predicate constructors currently include:

- literal true and false;
- equality and inequality;
- finite membership;
- conjunction;
- disjunction;
- negation;
- opaque predicates with declared dependencies.

Value expressions read:

- literals;
- record attributes;
- operation parameters;
- atom-valued unification bindings.

## Selection evidence

Successful evaluation returns:

```ts
interface SelectionCandidate {
  record: SubjectRecord;
  substitution: Substitution;
  evidence: SelectionEvidence;
}
```

Evidence records:

- selector ID;
- store revision;
- selected subject coordinate;
- requested and encountered terms;
- the unifying substitution;
- a tree of predicate evidence.

A later commit calls `verifySelectionEvidence` against the current store revision and selector. This is not a cryptographic proof. It is a locally checkable certificate produced by the reference semantics.

## Reference and compiled evaluators

### Reference evaluator

`evaluateReference` scans every record in the requested sort and applies pattern matching and predicates. Its simplicity makes it the semantic oracle for tests.

### Indexed compiler

`compileSelector` performs static analysis and extracts equality probes of the form:

```text
attribute = literal
attribute = parameter
```

At execution time it chooses the smallest available indexed bucket, then applies the complete semantics to those candidates.

The compiler returns execution statistics:

```ts
{
  sourceCount,
  examined,
  accepted,
  usedIndex,
}
```

This is intentionally a small optimizer. It demonstrates why reification matters without pretending to be a general relational planner.

## Dependency and portability analysis

`analyzeSelector` returns:

```ts
{
  sorts: ["field"],
  attributes: ["archived", "docId"],
  parameters: ["document"],
  opaquePredicates: [],
  portable: true,
}
```

A portable selector can be serialized as JSON. An opaque predicate cannot.

### Opaque boundary

```ts
predicate.opaque(
  "bespoke-title-heuristic",
  ["attr:name", "param:minimumLength"],
  ({ record, parameters }) => /* arbitrary JavaScript */,
)
```

The declared dependencies permit conservative invalidation and documentation. They are trust assumptions, not inferred proofs. Opaque selectors are marked process-local and serialization fails explicitly.

## Formal model

Let `R_S` be the finite set of records of sort `S`. A selector is interpreted relative to parameters `p` and store revision `r`:

\[
\llbracket q \rrbracket_{R,p,r}
\subseteq
R_S \times \operatorname{Substitution} \times \operatorname{Evidence}.
\]

For a record `x`:

1. if a pattern exists, compute `mgu(pattern, term(x))`;
2. evaluate the predicate under attributes, parameters, and that substitution;
3. construct evidence when both succeed.

Compiler correctness is the extensional statement:

\[
\operatorname{keys}(\operatorname{execute}(\operatorname{compile}(q),R,p))
=
\operatorname{keys}(\llbracket q \rrbracket_{R,p}).
\]

The tests compare both evaluators on fixtures and verify that the indexed evaluator examines fewer records for an indexed parameter.

## Use of Baader-Snyder unification theory

The additional chapter is central to this capsule.

### Most-general solutions

The selector pattern should not enumerate every ground way it can match. A unifier provides a substitution, and a most-general unifier captures all more specific solutions through further instantiation.

P03 uses this idea to make variable bindings reusable evidence rather than a one-time Boolean match.

### Occurs check

The prototype rejects:

```text
?x = f(?x)
```

because finite first-order substitutions cannot represent that equation without cyclic or infinite terms.

### Syntactic scope

The chapter distinguishes syntactic unification from unification modulo an equational theory. P03 implements only the syntactic case. This is an explicit guarantee boundary.

For example, these terms do not unify in P03:

```text
set(a, b)
set(b, a)
```

even if an application wishes to treat a set constructor as commutative. Such behavior would require named normalization or an AC unification module. The chapter explains why arbitrary equational unification cannot safely inherit the simple promise of one MGU.

### MGU and coequalizer are not synonyms

The source gives a categorical reformulation in which a unifier equalizes a parallel pair and a most-general unifier has a factorization property. It also notes that a categorical coequalizer imposes uniqueness of the factor, which ordinary MGU definitions do not always supply without further restriction.

P03 therefore calls its result a substitution or unifier. It does not call it the quotient of the selector.

## Tests and experiments

The thirteen executable tests cover:

1. MGU construction for a field pattern;
2. consistency of repeated variables;
3. occurs-check failure;
4. constructor clash;
5. substitution-composition law;
6. factorization of a specific unifier through a computed general one;
7. candidate production with unification and predicate evidence;
8. compiled/reference extensional equivalence;
9. indexed candidate reduction;
10. dependency extraction and serialization round trip;
11. opaque guarantee downgrade;
12. rejection of forged predicate evidence;
13. revision-sensitive evidence and rejection explanations.

Run:

```bash
npm test
npm run demo
```

## Results established by the prototype

### By construction

- The inspectable core is a finite AST.
- Portable selectors contain no executable callbacks.
- Pattern variables and substitutions are explicit data.
- The compiled evaluator always applies the full reference predicate after index narrowing.

### By executable tests

- The unifier handles representative delete, orient, eliminate, decompose, clash, and occurs-check cases.
- Returned example substitutions are idempotent unifiers.
- A representative specific solution factors through the computed general solution.
- The indexed and reference evaluators return equal candidate keys on the fixture.
- Evidence fails validation after a store revision change.

### Not yet proved

- soundness and completeness of the unifier for all first-order terms;
- principal/MGU status of every successful result;
- compiler correctness for all AST constructors;
- soundness of dependency extraction;
- optimizer correctness under future rewrites;
- security of evidence against forged JavaScript objects.

These are appropriate targets for P14-style mechanization.

## Deliberate limitations

1. The store is in-memory and scalar-attribute only.
2. Pattern bindings can be consumed as scalar predicates only when they bind atoms.
3. The compiler uses one simple equality index rather than a cost-based join planner.
4. Predicate negation is local Boolean negation, not recursive logical negation.
5. Opaque dependency declarations are not verified.
6. Evidence is revision-sensitive and intentionally invalidated by any store mutation, even an unrelated one.
7. Equational, higher-order, sorted, and nominal unification are out of scope.

## Integration seam

P01 should construct the subject coordinates used as record sort/key. P02 should expose committed occurrences as records. P04 can either consume P03 candidate results as extensional facts or compile a common relational fragment into both engines.

A future composed selection result should include:

```ts
{
  subjectIdentityEvidence,
  occurrenceActivationEvidence,
  selectorEvidence,
  ruleOrCapabilityEvidence,
}
```

The commit operation must revalidate each component at its own revision.

## Research extensions

- prove unifier soundness and principality in Lean;
- add sort-aware and order-sorted terms;
- compare matching with full unification for selector patterns;
- implement a term-DAG/union-find optimizer and differential-test it;
- add join, projection, aggregation, and recursive query constructors;
- derive an incremental evaluator from change structures;
- introduce a checked monotone fragment;
- investigate AC/ACUI selectors for tags and capability sets;
- generate human-readable minimal rejection explanations;
- benchmark AST interpretation, bytecode, generated JavaScript, and relational plans.


\newpage


# P04 - Recursive Rules, Fixed Points, and Provenance

## Research question

Can PBUI applicability, compatibility, inherited scope, translator reachability, link connectivity, and action availability be expressed as a finite declarative rule program with an inspectable least-fixed-point semantics and checkable derivations?

This capsule implements a small function-free Datalog-like core with:

- ground facts and range-restricted rules;
- positive and stratified-negative literals;
- first-order syntactic unification during rule matching;
- a naive stratum-by-stratum fixed-point evaluator;
- an agenda evaluator for the positive fragment;
- incremental insertion for positive programs;
- bounded provenance alternatives;
- human-readable explanation trees;
- derivation verification;
- validation of arities, safety, finiteness restrictions, and negation strata.

## Why a rule layer is useful for PBUI

Many presentation properties are relational rather than local descriptor fields:

```text
selectable(context, occurrence, subject)
compatible(sourceSort, targetSort)
translatorReachable(sourceSort, targetSort)
availableAction(context, subject, action)
sameBinding(portA, portB)
```

They depend on combinations of facts:

```text
selectable(C, O, S) :-
  wants(C, T),
  presents(O, S, U),
  compatible(U, T),
  reachable(O).
```

A descriptor callback can compute one answer but does not expose the relation, its recursive dependencies, or the reason for the result. P04 makes those explicit.

## Executable language

### Terms and atoms

Rules use first-order variables and atomic constants:

```ts
relation("reachable", v("x"), v("y"))
fact("edge", "chart", "pipeline")
```

The fixed-point fragment is function-free. Compound terms in rule arguments are rejected. This Datalog restriction keeps the active Herbrand base finite when constants come only from the finite input program and facts.

### Literals

```ts
positive(relation("edge", v("x"), v("y")))
negative(relation("archived", v("project")))
```

Negative variables must also occur in a positive body literal. Head variables must be range-restricted by positive body literals.

### Rules

```ts
{
  id: "reachable-transitive",
  head: relation("reachable", v("x"), v("z")),
  body: [
    positive(relation("reachable", v("x"), v("y"))),
    positive(relation("edge", v("y"), v("z"))),
  ],
}
```

Rule identifiers are stable provenance names.

## Unification in rule matching

For each positive body literal, the evaluator unifies the instantiated literal with candidate ground facts. The resulting substitution is composed with bindings accumulated from earlier literals.

Example:

```text
reachable(?x, ?y)
edge(?y, ?z)
```

matched against:

```text
reachable("chart", "pipeline")
edge("pipeline", "table")
```

produces:

```text
?x -> "chart"
?y -> "pipeline"
?z -> "table"
```

and derives:

```text
reachable("chart", "table")
```

Repeated variables are handled by unification, so:

```text
pair(?x, ?x)
```

matches `pair("a", "a")` but not `pair("a", "b")`.

The term/unification code is copied into P04 rather than imported from P03. This is deliberate for the first research pass: P04 can be assessed independently and later compared with a shared unification service.

## Fixed-point semantics

For a positive program, let `T_P` be the immediate-consequence operator on sets of ground facts. The intended result is:

\[
\operatorname{lfp}(T_P)
=
\bigcup_{n \geq 0} T_P^n(B),
\]

where `B` is the extensional base database.

Because the implemented language is function-free and the active constants and predicates are finite, there are only finitely many possible ground atoms at fixed arities. Monotone iteration therefore stabilizes after finitely many fact insertions.

### Naive evaluator

The reference evaluator repeatedly executes every rule in one stratum until no new fact appears. It then advances to the next stratum.

This evaluator is intentionally simple and serves as the semantic oracle.

### Agenda evaluator

For positive programs, the agenda evaluator reacts to newly added facts. Rules are indexed by body predicate, and one body occurrence is anchored to the new fact while other body literals range over the complete known database.

The tests compare its final fact set with the naive evaluator.

### Incremental additions

`IncrementalPositiveEngine` retains the derived knowledge base. Adding new base facts seeds the agenda with only those facts and newly derived consequences.

This prototype supports insertions only. Retractions require dependency counts, DRed-style maintenance, differential collections, or affected-region recomputation.

## Stratified negation

Rules such as:

```text
availableAction(P, "archive") :-
  project(P),
  not archived(P).
```

are evaluated by assigning predicates to strata. A negative dependency requires a strictly lower stratum; a positive dependency permits the same stratum.

The compiler solves constraints:

```text
stratum(head) >= stratum(positiveBody)
stratum(head) >  stratum(negativeBody)
```

If repeated relaxation does not stabilize within the finite bound, the program contains recursion through negation and is rejected.

Thus the capsule has a defined semantics for stratified negation, not arbitrary nonmonotone recursion.

## Provenance

Each fact stores one or more derivations:

```ts
type Derivation =
  | { kind: "base"; id: string }
  | {
      kind: "rule";
      ruleId: string;
      substitution: Substitution;
      premises: string[];
      negativeChecks: string[];
    };
```

A recursive explanation can show:

```text
reachable(chart, table)
  via reachable-transitive
    reachable(chart, pipeline)
      via edge-is-reachable
        edge(chart, pipeline) [base]
    edge(pipeline, table) [base]
```

The store deduplicates derivations and caps alternatives per fact to prevent an explanation experiment from consuming unbounded memory in cyclic programs.

### Verification

`verifyFactDerivation` checks a stored derivation against:

- the rule named by the derivation;
- the recorded substitution;
- the instantiated head;
- the expected positive premises;
- absence of instantiated negative facts;
- recursively verifiable premise facts.

This is a small certificate checker. It does not prove that the evaluator found every derivable fact, but it prevents an optimized evaluator from inventing a fact without a valid local derivation.

## PBUI examples

### Compatibility and selection

```text
compatible(S, S) :- sort(S).

selectable(C, O, Subject) :-
  wants(C, TargetSort),
  presents(O, Subject, SourceSort),
  compatible(SourceSort, TargetSort),
  reachable(O).
```

### Action availability

```text
action(C, Subject, "inspect") :-
  selectable(C, O, Subject),
  canInspect(C).
```

### Port link closure

```text
sameBinding(A, B) :- link(A, B).
sameBinding(B, A) :- sameBinding(A, B).
sameBinding(A, C) :- sameBinding(A, B), sameBinding(B, C).
```

The last example is appropriate for reasoning and explanation, though a production port compiler may use a specialized graph quotient algorithm for efficiency.

## Formal safety conditions

The validator enforces:

1. every predicate has one arity throughout the program;
2. base facts are ground;
3. terms are function-free;
4. rule IDs are unique;
5. every head variable appears in a positive body literal;
6. every negative variable appears in a positive body literal;
7. recursion through negation is absent.

These conditions support finite evaluation and safe instantiation. They are not a complete proof of termination if future extensions add aggregates, fresh values, external functions, or infinite domains.

## Use of Baader-Snyder unification theory

The chapter is relevant in three ways.

### Rule matching produces substitutions

Rule evaluation is not merely a predicate-name join. Variables shared across body literals impose equations, and unification constructs a substitution satisfying them.

### Generality avoids ground enumeration

A rule is written once with variables. The unifier computes the necessary instantiation from current facts. This is the same broad automation benefit that makes unification central to resolution and rewriting: the system avoids enumerating arbitrary ground substitutions before matching.

### Efficiency guidance

The source describes term-DAG algorithms and equivalence-class approaches to unification. P04 currently uses a simple tree unifier because it is easier to audit. Future optimized matching can use shared term DAGs or union-find closure, but must be differential-tested against the current reference semantics.

The chapter's warnings about equational unification also constrain the rule language. P04 does not silently match modulo associativity, commutativity, idempotence, or application-specific equations. Those require explicitly named theory modules and may produce complete sets of unifiers rather than one principal solution.

## Tests and experiments

The eleven executable tests cover:

1. least transitive closure from recursive rules;
2. agenda/reference evaluator equality;
3. rule and base-fact order independence;
4. fixed-point idempotence;
5. recursive provenance explanation and verification;
6. stratified action derivation with negation;
7. rejection of recursion through negation;
8. rejection of unsafe and function-generating rules;
9. repeated-variable unification in rule matching;
10. incremental insertion equality with full recomputation;
11. a PBUI-style selectable-occurrence/action constellation.

Run:

```bash
npm test
npm run demo
```

## Results established by the prototype

### By construction

- Facts are only added during fixed-point evaluation.
- Function-free range-restricted rules cannot generate fresh term structure.
- Negative dependencies are assigned to lower strata or rejected.
- Derivations name stable rules and explicit premises.

### By executable tests

- The two positive evaluators agree on the reachability fixture.
- Rule ordering does not change the tested fixed point.
- Re-evaluating with the completed fact set is idempotent.
- Incremental insertions match complete recomputation on the fixture.
- Stored recursive derivations pass the certificate checker.

### Not yet proved

- soundness and completeness of either evaluator;
- termination bound for all validated programs;
- correctness of the stratification solver;
- equivalence of agenda and naive evaluation for all positive programs;
- completeness of provenance alternatives;
- incremental correctness under arbitrary insertion sequences;
- correctness under deletion and negation retractions.

## Deliberate limitations

1. No function symbols in rule atoms.
2. No aggregation, arithmetic, comparison predicates, or foreign functions.
3. No disjunction in one rule body; use several rules with the same head.
4. No retractions in the incremental engine.
5. Provenance alternatives are capped.
6. Negation is stratified absence from a completed lower stratum.
7. The engine is in-memory and single-threaded.
8. The derivation checker trusts the program and term implementation.
9. It does not track semantic revisions from P01-P03.

## Integration seam

A later composition pass should compare two strategies:

### Strategy A: P03-first

P03 selects candidate records. The adapter inserts those candidates as extensional P04 facts, and P04 derives recursive actions and authority.

### Strategy B: shared relational core

A common query/rule IR compiles both nonrecursive selectors and recursive rules. P03 becomes the nonrecursive evidence-producing view of the shared engine.

The first strategy is simpler. The second may eliminate duplicated semantics but risks making the rule engine the universal abstraction. Both should be prototyped before consolidation.

## Research extensions

- formalize least-fixed-point semantics and evaluator soundness in Lean;
- add semi-naive delta relations rather than fact-anchored agenda evaluation;
- implement deletions with support counts or differential dataflow;
- add semiring provenance and minimal-proof extraction;
- compile rules to indexed joins;
- investigate sorted unification and typed predicate signatures;
- introduce monotone lattice-valued attributes;
- model well-founded or stable-model semantics as explicit alternative engines;
- benchmark graph-specialized algorithms against generic rules;
- test proof certificates emitted by an optimized worker runtime.


\newpage


# P01-P04 Interoperability Contract

## Purpose

The first-pass prototypes remain implementation-independent. They exchange only small semantic records. This prevents one team's design decisions from becoming accidental requirements for the other projects.

## Canonical subject reference

```ts
interface SubjectRef {
  sort: string;
  key: string;
}
```

P01 is authoritative for constructing and comparing these references. P02, P03, and P04 treat them as opaque nominal coordinates. They must not infer sameness from labels, object structure, or React keys.

## Occurrence projection

P02 associates a visual occurrence with a subject:

```ts
interface OccurrenceProjection {
  occurrenceId: string;
  generation: number;
  subject: SubjectRef;
  forms: string[];
  surface: string;
  visible: boolean;
  reachable: boolean;
  enabled: boolean;
}
```

A future adapter exports committed P02 records as P03 records and P04 facts:

```text
P03 record:
  sort = "occurrence"
  key  = occurrenceId
  attributes.subjectSort = subject.sort
  attributes.subjectKey  = subject.key

P04 facts:
  occurrence(occurrenceId)
  presents(occurrenceId, subjectSort, subjectKey)
  visible(occurrenceId)
  reachable(occurrenceId)
```

The generation must participate in evidence validation but not in domain identity.

## Selector result

P03 returns:

```ts
interface SelectionCandidate {
  record: SubjectRecord;
  substitution: Substitution;
  evidence: SelectionEvidence;
}
```

The later input-context orchestrator should retain the complete evidence until commit. Before accepting the subject it should revalidate:

1. P02 occurrence generation is still current;
2. P01 subject reference is still valid and, if needed, canonicalized;
3. P03 store revision and parameters still match;
4. P04 authority/action derivation is still current, or is re-derived.

## Rule facts

P04 uses function-free ground atoms. Recommended encodings:

```text
subject("field", "doc-readings/temperature")
presents("occ-17", "field", "doc-readings/temperature")
wants("ctx-2", "field")
reachable("occ-17")
hasCapability("ctx-2", "inspect")
```

The strings are identifiers, not trusted semantic structure. The adapter owns escaping and codec validation.

## Revision discipline

Each capsule has a local revision:

- P01 snapshot revisions belong to domain entities;
- P02 registry revisions belong to committed occurrence topology;
- P03 store revisions belong to selector inputs;
- P04 fixed-point results belong to one extensional fact snapshot.

A composed evidence object should contain a tuple of revisions rather than collapse them into one integer.

## Non-composition in this pass

No code in P01 imports P02, and so on. This is deliberate. The integration pass should compare at least two adapters for each seam before selecting a common representation.


\newpage


# Mapping the Current PBUI to P01-P04

The supplied PBUI implementation currently centers on:

```ts
PresentationReference<Values> = { type, value }
AcceptRequest = { types, prompt, filter? }
PresentationDescriptor = { label, describe, actions, tone }
```

The four prototypes decompose that API as follows.

## Presentation references

Current:

```ts
{ type: "field", value: { docId, name } }
```

Proposed split:

```text
P01 semantic subject:
  { sort: "field", key: "docId/name" }

P02 occurrence:
  { id: "occ-...", subject, forms: ["field-chip"], surface: "workspace" }

optional current snapshot:
  P01 registry.snapshot(subject)
```

The semantic reference no longer retains an arbitrary captured value as its identity.

## Presentation component

The current React `Presentation` component simultaneously:

- supplies a reference;
- determines mounted lifetime;
- handles acceptability;
- opens menus;
- performs pointer and keyboard behavior.

P02 extracts the mounted-occurrence lifecycle. A React wrapper should register only in commit-safe effects and receive derived acceptability/action observations from the runtime.

## Accept requests

Current:

```ts
accept({
  types: "field",
  filter: reference => reference.value.docId === activeDoc,
})
```

P03:

```ts
{
  from: "field",
  pattern: field(?doc, ?name, ?kind),
  where: ?doc = $activeDocument
}
```

Legacy lambdas become explicit opaque predicates with declared dependencies and downgraded portability/incrementality guarantees.

## Conversions and action descriptors

Current conversions are ordered callback functions, and actions are returned directly by exact-type descriptors. P04 instead represents recursive compatibility and applicability as facts and rules:

```text
compatible(sourceSort, targetSort)
selectable(context, occurrence, subject)
action(context, subject, actionId)
```

A descriptor can remain authoring sugar compiled into nonrecursive rules.

## Suggested migration order

1. Introduce P01-style semantic keys behind `PresentationReference`.
2. Wrap the existing `Presentation` component with P02 generation leases.
3. Compile exact type/filter requests into P03 selectors; retain callbacks as opaque nodes.
4. Shadow current action/conversion results with P04-derived facts and compare them in tests.
5. Switch individual workflows only after the reference and new evaluators agree on fixtures.


\newpage


# Unification Theory Notes for P01-P04

Primary source:

Franz Baader and Wayne Snyder, “Unification Theory,” Chapter 8 in the *Handbook of Automated Reasoning* (2001):
<https://www.cs.bu.edu/fac/snyder/publications/UnifChapter.pdf>

## Concepts used directly

### Terms and substitutions

P03 and P04 use first-order terms generated from variables, atoms, and fixed-arity constructors. A substitution maps variables to terms and extends homomorphically through constructors.

The implementation's composition convention is documented by the law:

```text
apply(t, compose(sigma, theta))
  = apply(apply(t, sigma), theta)
```

### Most-general unifiers

For a solvable syntactic problem, P03 returns one substitution intended to be more general than any ground specialization used by a selector. Tests exercise factorization on representative examples.

This is useful for PBUI because evidence can retain one general explanation:

```text
field(?doc, ?name, number)
  unifies with
field(doc-readings, temperature, number)

substitution:
  ?doc  -> doc-readings
  ?name -> temperature
```

Downstream predicates then consume the bound variables.

### Occurs check

The equation `?x = f(?x)` is rejected. Without this check, the finite term representation would implicitly require an infinite rational tree and substitution application could cycle.

### Term DAGs and equivalence classes

The chapter's term-DAG discussion is relevant to future optimization. Shared term nodes avoid repeated structure, and efficient unification algorithms can replace repeated substitution work with equivalence-class operations plus an acyclicity check.

The current prototype deliberately uses a simpler persistent term tree and worklist algorithm. This makes the reference semantics easier to inspect. A DAG/union-find implementation should be added only as an optimized evaluator and tested against this reference.

## Concepts used as architectural cautions

### Domain identity is not unifiability

P01 does not decide whether two projects are the same by unifying their object structures. Two structurally identical projects with different application keys remain distinct. Conversely, two different representations can identify one entity because their registered key functions agree.

### Syntactic versus equational unification

P03 and P04 implement syntactic unification only. If future selectors match modulo associativity, commutativity, units, idempotence, alpha-equivalence, or domain equations, the theory must be named explicitly.

The source surveys why equational unification is qualitatively harder: depending on the theory, solvability can be undecidable, and a solvable problem may lack a single most-general unifier. The API must therefore not promise one canonical substitution for arbitrary equations.

### Most-general unifier versus coequalizer

The chapter gives a category-theoretic reformulation of unification and observes that the universal factorization property of an MGU resembles a coequalizer. It also stresses a difference: categorical coequalizers demand uniqueness of the factorizing morphism, whereas ordinary MGU definitions require existence up to instantiation. Some syntactic MGUs can be restricted to produce coequalizers, but the notions are not interchangeable in general.

This matters for PBUI terminology:

- P03 computes substitutions solving pattern equations.
- P01 aliases establish an application-defined equivalence relation.
- a future port-binding compiler may form a quotient/coequalizer of explicit endpoint equations.

These are related constructions, not one mechanism.

## Deferred investigations

1. DAG-based unification and sharing benchmarks.
2. Sorted or order-sorted unification for semantic type hierarchies.
3. Matching versus unification as distinct selector operators.
4. AC or ACUI unification for set-like capability and tag expressions.
5. Complete sets of unifiers when one MGU does not exist.
6. Proof-producing unification in Lean, including soundness and principal-solution properties.
