# From Propagation by Convention to Quotient Semantics

## Reengineering the Sentinel Window, Linking, and Cross-Interaction Kernel

**A doctoral-style engineering thesis and implementation report**  
**Date:** 6 August 2026  
**Artifact:** `sentinel-kernel-reimplementation`

---

## Abstract

Presentation-based interfaces are attractive because they allow objects already visible in one part of an application to serve as inputs, pivots, commands, and coordination points elsewhere. The supplied Sentinel Rev 4 prototype demonstrates this attraction unusually well. Its fraud-analysis console combines a review queue, order inspector, entity-linkage view, transaction ledger, risk chart, ring graph, multiple workspaces, window placements, typed port badges, named links, presentation-sensitive interactions, and a command listener. The visual design is coherent and the interaction vocabulary is sophisticated. The prototype nevertheless places too much semantic responsibility on conventions embedded in one React file. Its graph stores one copy of a purportedly shared value at every port; its link-group identity is inferred from edge order; reducer output depends on module-global counters; transient selection state contains executable closures; a context provider is bypassed by a global store subscription; view kinds can diverge from their port schemas; and accepted transitions are not checked against complete-state invariants.

This thesis reports a source-grounded assessment and a reimplementation of the prototype's kernel. The replacement preserves the product concepts while changing their semantics. Views are instances of typed open-component schemas. Ports are local boundary occurrences. Durable link edges are generating equations between compatible ports. The link graph induces an equivalence relation, and the runtime materializes its quotient as one canonical binding cell per connected component. Values and link-group metadata are stored once per quotient class rather than copied to each endpoint. Linking is an atomic command that adds an equation, rebuilds the quotient, and applies an explicit reconciliation policy. Unlinking removes one generating equation, recomputes connectivity, and preserves the current value on every resulting class. All durable operations pass through a deterministic pure transition function and a whole-state invariant checker. Transient input contexts are serializable data interpreted by an instance-scoped engine. Effects and rendering are outside the command kernel.

The implementation comprises a typed TypeScript model, component schema, union-find quotient compiler, reconciliation layer, invariant checker, deterministic command kernel, interaction engine, derived-query layer, and a thin browser adapter. A live executable demonstrates two workspaces and the original fraud-analysis scenarios. Twenty-four Node tests exercise algebraic laws and regressions; fourteen browser assertions exercise linked focus propagation, quotient splitting, typed compatible-port selection, relinking, invalid-write rejection, and workspace switching. Five browser screenshots and three architecture diagrams document the running artifact.

The work does not claim mechanized verification. Instead, it establishes a proof-oriented boundary: the state space, commands, invariants, and reference algorithms are explicit enough to support property testing, bounded model checking, temporal specification, and later mechanization. The principal conclusion is that robust cross-window interaction requires separating four structures that the original prototype partly conflates: local component ports, the graph of user-declared link equations, the quotient of that graph, and the value-reconciliation algebra. A quotient explains which endpoints have become one logical interface; it does not itself choose a winning value, authorize an operation, or define a bidirectional update policy. Making those distinctions executable turns a compelling UI prototype into a kernel that can be replayed, tested, extended, and reasoned about.

**Keywords:** presentation-based interface, open component, typed port, quotient, coequalizer, link graph, command kernel, invariant, interaction workflow, React, CLIM, incremental computation.

---

## Declaration of scope and evidence

This document is based primarily on the supplied Sentinel Rev 4 source, preserved without modification at [`original/SentinelRev4.jsx`](../original/SentinelRev4.jsx). Source line references in the assessment chapters refer to that copy. The replacement implementation is contained in `src/`, the tests in `tests/`, and the browser evidence in `docs/figures/`.

Theoretical discussion is used to clarify the engineering decomposition, not to imply that the TypeScript artifact has been formally derived in a proof assistant. Statements labeled **proposition** are mathematical consequences of the stated model. Statements labeled **implementation invariant** are executable predicates checked by `src/invariants.ts`. Statements labeled **test evidence** report automated checks. Statements labeled **future proof obligation** remain design targets.

The implementation deliberately changes the rendering technology at the adapter boundary: the replacement demonstration uses a small DOM renderer rather than React. This is not an argument against React. It is an experimental control showing that the semantic kernel no longer depends on a component framework. A React adapter can subscribe to the same immutable engine snapshots through `useSyncExternalStore`; React's own documentation treats that hook as the integration point for external stores and requires repeated `getSnapshot` calls to return a stable cached snapshot while the store is unchanged [React 2026a].

---

# Part I — Problem, Method, and Findings

## 1. Introduction

Window systems become difficult at the point where windows cease to be independent rectangles. A queue row should focus an order inspector. The same order should become the center of a graph. Selecting a card should pivot every linkage-aware view. A chart and pipeline may remain distinct applications while observing one document selection. A logical view may have several visual placements. A link may be named, colored, persisted, removed, merged with another link, or carried into another workspace. Each operation seems small in isolation. Together they create a semantic kernel.

The Sentinel prototype already recognizes this. Its opening comment describes a progression from “subjects → occurrences → commands → ports → links,” and its UI makes those concepts visible. The failure is not one missing helper function. It is that the implementation has no single answer to the question:

> What is the authoritative object that two linked selectors share?

At different points, the answer is an edge, a reachable set of ports, an arbitrary representative edge, a collection of duplicated endpoint values, or a convention enforced by `writePortValue`. Such plural answers are tolerable in a visual experiment but unstable as an application platform.

This thesis asks four research questions.

1. **Representation:** What minimal state model gives linked windows one coherent semantic meaning without collapsing view identity, placement identity, and port identity?
2. **Transition:** How should link, unlink, write, kind-change, and placement-lifetime operations be defined so that invalid intermediate states are never published?
3. **Assurance:** Which properties can be stated as mathematical propositions, which can be checked as runtime invariants, and which require tests or future formalization?
4. **Integration:** How can the new kernel preserve the prototype's interaction quality while remaining independent of React and compatible with a future presentation/query system?

The answer developed here is a layered kernel based on typed open components and quotient-derived binding cells.

![The rebuilt triage workspace at initial state.](figures/01-triage-overview.png){#fig:triage-overview width=100%}


## 2. Method

The work followed a reconstruction-and-refinement method rather than a greenfield rewrite.

### 2.1 Static reconstruction

The supplied 2,098-line JSX file was decomposed conceptually into:

- domain fixtures;
- semantic subject identity;
- logical views and visual placements;
- local ports;
- link topology and propagated values;
- durable commands;
- transient engine state;
- presentation occurrences;
- view renderers;
- menus and workflows;
- window layout behavior;
- effects and export.

The purpose of this pass was to preserve the prototype's terminology and intent. A critique that replaced the application with a generic state-management tutorial would not answer the engineering problem.

### 2.2 Failure-mode analysis

Each mutation path was examined against five questions:

1. Is the operation a pure function of state and command?
2. Is its result serializable and replayable?
3. Does the state have one authoritative representation of each logical fact?
4. Are cross-object references and type constraints checked?
5. Can a complete-state invariant reject a malformed candidate before publication?

The assessment in Chapter 3 records the failures found.

### 2.3 Reference semantics before optimization

The replacement uses deliberately direct algorithms:

- union-find to compile link connectivity;
- canonical sorted member lists for binding IDs;
- complete quotient rebuilding after topology changes;
- full invariant validation on every accepted command;
- immutable snapshots;
- direct DOM rerendering for the demonstration.

This prioritizes a small reference semantics over premature incremental machinery. The implementation can later replace whole-graph rebuilding or whole-page rendering while differentially testing the optimization against the reference result.

### 2.4 Executable evaluation

Evaluation has three layers:

- **kernel tests:** deterministic commands, graph laws, validation, immutability, lifecycle, and engine isolation;
- **browser assertions:** actual user-flow behavior against the built demonstration;
- **visual evidence:** screenshots of initial, propagated, split, selected, relinked, and ring-analysis states.

The final suite contains 24 Node tests and 14 browser assertions.

## 3. Assessment of the supplied kernel

### 3.1 Strengths worth preserving

The prototype deserves a precise assessment because its strengths are the reason the kernel matters.

First, it distinguishes a **subject** from an occurrence. `subj(type, key)` produces a compact semantic reference, and the `O` wrapper associates that reference with rendered output. This is the central insight of presentation-based interaction: text, table rows, and SVG marks can all denote the same domain object.

Second, it models **commands as data** for most durable operations. `ApproveOrder`, `WritePort`, `LinkPorts`, and window commands are records interpreted by one reducer. That is substantially better than embedding domain mutations in every click handler.

Third, it distinguishes **views from placements**. A view is a logical configuration; a layout leaf places it in a workspace. This distinction is necessary for linked duplicates, multiple occurrences, and future persistence.

Fourth, ports carry a declared value type, protocol, and mode. Although these declarations are weakly enforced, the vocabulary is already present.

Fifth, the prototype places downloads at an **effect boundary** rather than inside state transitions. This is retained.

Finally, the visual design communicates semantics. Port badges expose links; colored names distinguish groups; hover tracing reveals reachability; the listener displays command flow; selection changes occurrence sensitivity. The rebuilt kernel is intended to support, not erase, this interaction language.

### 3.2 Critical defect: the context provider is bypassed

The React adapter creates a module-global engine (`original/SentinelRev4.jsx:772`), passes it as the context default, and reads it through `usePbui`. But `useApp` subscribes directly to that global variable (`:775`):

```js
const engine = new PbuiEngine(initialState());
const PbuiContext = createContext(engine);
const usePbui = () => useContext(PbuiContext);
const useApp = () => useSyncExternalStore(engine.subscribe, engine.getState);
```

This is not merely stylistic. A subtree can receive engine B from the provider while rendering continues to subscribe to engine A. Commands and observations can therefore target different stores. React context is defined precisely so descendants receive the innermost provided value [React 2026b]; hardcoding the singleton defeats that mechanism.

The replacement has no module-global semantic engine. `KernelEngine` is constructed explicitly, and every snapshot, listener, selection continuation, occurrence registry, and log belongs to that instance. The corresponding test creates two engines, dispatches to one, and proves the other remains at revision zero.

### 3.3 Critical defect: reducer determinism depends on global counters

The original source declares:

```js
let viewSeq = 0;
const makeViewId = () => `V-${++viewSeq}`;
```

at lines `100-101`. `SplitPlacement` invokes `makeView` inside `applyCommand` (`409-413`). Thus the nominal reducer is not a function

\[
\delta:S\times C\to S,
\]

because output also depends on ambient module state \(g\):

\[
\delta:S\times C\times G\to S.
\]

Two calls with structurally equal states and commands can allocate different IDs. Replay after process restart cannot be justified solely by the event log. Tests can interfere through import order.

The replacement stores counters inside `AppState`. Allocation is part of the candidate transition, and a deterministic test compares two independent evaluations of the same command.

### 3.4 Critical defect: a shared value is represented by copies

The original graph traversal (`305-319`) discovers all ports reachable from one port. The write helper (`321-325`) clones the endpoint-value map and assigns the same value to every reachable port:

```js
function writePortValue(state, portId, value) {
  const group = connectedPorts(state, portId);
  const portValues = { ...state.portValues };
  for (const p of group) portValues[p] = value;
  return { ...state, portValues };
}
```

This is denormalization without an authoritative normalized value. The claim “these ports share one selection” is implemented as “these several keys currently contain equal data.” The equality can be broken by import, migration, debugging tools, a forgotten mutation path, or a future feature. No read can identify the canonical copy.

The replacement stores one value at the quotient binding. Endpoints contain no copies. A read is an indexed lookup through `portBinding`.

### 3.5 High-severity defect: group metadata is attached to arbitrary edges

The original `LinkPorts` command stores `name` and `color` on the new edge (`355-370`). `RenameLink` and `SetLinkColor` modify one edge (`381-391`). Yet the UI describes connected components as named link groups. `linkGroups` scans the component and chooses `members[0]` as representative (`132-149`).

This creates several anomalies:

- two edges in one component can have different names;
- merging two named components does not define a group name;
- deleting the representative edge can change the visible name without changing the remaining membership;
- object insertion order can influence the chosen representative;
- a port badge may display a concatenation of edge names rather than one binding identity.

The replacement attaches metadata to `BindingCell`. Link edges have only `id`, `left`, and `right`. Metadata follows the logical class, and a merge explicitly chooses or overrides it.

### 3.6 High-severity defect: topology silently chooses a value policy

After adding an edge, the original command executes:

```js
next = writePortValue(next, a.id, state.portValues[a.id] ?? null);
```

The source endpoint wins. This may be a defensible interaction choice, but it is not a consequence of connecting ports. The topological operation “identify these endpoints” and the algebraic operation “resolve two existing values” are independent.

The replacement makes reconciliation an explicit command field:

```ts
type ReconcilePolicy =
  | "prefer-source"
  | "prefer-target"
  | "require-equal";
```

`require-equal` rejects a conflicting merge atomically. The rejected candidate neither retains the new edge nor increments the revision.

### 3.7 Critical defect: values are not checked against port sorts

The original `WritePort` verifies only that the port exists. An object can be written to an `order-id` port; a string can be written to a `subject-ref` port; a subject can name an entity absent from the domain store. These malformed states fail later in renderers, where errors are harder to diagnose and no longer attributable to one command.

The replacement validates both representation and referential integrity. `order-id` accepts `null` or the ID of an existing order. `subject-ref` accepts `null` or a typed reference whose target exists. Every binding value is rechecked for every member port by the invariant checker.

### 3.8 High-severity defect: view kind and boundary schema can diverge

Changing a view to `listener` creates no new ports but does not remove old ports or links (`393-407`). Splitting can create standard ports regardless of the requested kind (`409-413`). This violates a fundamental open-component invariant: the public boundary must be determined by the component schema.

The replacement moves boundary declarations into `src/schema.ts`. The kernel compares a view's actual ports to `portsForView(view)`. A kind change removes or adds ports in the same candidate transaction. Removing a port that belongs to a non-singleton binding is rejected with an instruction to unlink first.

### 3.9 High-severity defect: closing a window leaks semantic state

The original `ClosePlacement` edits the layout tree but leaves an unplaced view, its ports, values, and links in state. That makes visual lifetime and logical lifetime inconsistent. Hidden ports can remain in connected components and continue receiving propagated values.

The replacement counts remaining placements. Closing one occurrence of a multiply placed view preserves the view. Closing its final placement removes the view, its ports, incident edges, and now-obsolete binding cells atomically.

### 3.10 High-severity defect: interaction state contains code

The link workflow constructs a request with an `accepts(subject, engine)` closure (`1368-1380`). `selectOne` stores that request in interaction state (`599-607`), and every occurrence invokes the callback during render (`791-792`). This state cannot be serialized, transferred to a worker, deterministically compared, inspected without execution, or reconstructed from an event log.

The workflow also selects a view and then calls `.find` to choose its first compatible port. A view with two compatible ports creates hidden ambiguity.

The replacement request is data:

```ts
{
  id: "SEL-1",
  prompt: "Choose a compatible port",
  query: {
    kind: "compatible-port",
    sourcePortId: "V-3/focus-order"
  }
}
```

The runtime interprets the finite query kind. The user selects an actual port endpoint.

### 3.11 Medium-severity defect: preview updates mutate authoritative state

Splitter movement calls `setSplitRatioLive`, which updates the engine's principal state outside `applyCommand` (`589-592`, `1602`). Pointer release later dispatches one command (`1610`). This is acceptable as a rendering optimization only if preview state is explicitly ephemeral. Here it is the same state observed by all components and omitted from the command log, so the log cannot reproduce the exact sequence of published snapshots.

The reimplementation omits the window-resize subsystem because the request was to rebuild the semantic core. The required migration rule is nevertheless clear: preview geometry belongs to adapter-local interaction state; the final geometry belongs to a validated durable command.

### 3.12 Medium-severity defect: repeated graph scans

`connectedPorts` loops over all links for every queue element. Compatibility, group naming, writes, hover tracing, and status rendering repeatedly call it. The same connected component may be rediscovered many times per pointer movement.

For \(n=|P|\) ports and \(m=|E|\) edges, the scan-based traversal is approximately \(O(nm)\) in the worst case because each visited vertex scans every edge. A page with \(k\) port badges can multiply the cost during rendering. The replacement pays \(O((n+m)\alpha(n))\) to rebuild all components using disjoint-set union and then answers class lookup in expected \(O(1)\) through a map. Tarjan's analysis provides the classic near-linear amortized bounds for union-find with rank and path compression [Tarjan 1975].

### 3.13 Critical defect: no whole-state invariant gate

The original reducer has local checks but no definition of a valid global state. It can accept stale link endpoints, duplicated edges, orphan values, unplaced views, schema-mismatched ports, or class divergence. A robust kernel must define validity separately from individual commands:

\[
\operatorname{Valid}:S\to\{\mathsf{true},\mathsf{false}\}.
\]

Every accepted transition must satisfy:

\[
\operatorname{Valid}(s)\land
\delta(s,c)=s'
\Longrightarrow
\operatorname{Valid}(s').
\]

The replacement checks the incoming state, constructs a candidate, validates the complete candidate, and publishes only if the predicate holds.

## 4. Requirements derived from the assessment

The reconstructed kernel requirements are as follows.

### 4.1 Semantic requirements

1. A logical view and a visual placement are distinct identities.
2. A component kind determines a typed set of local ports.
3. A link is a durable user-declared equation between compatible ports.
4. The transitive closure of link equations determines binding membership.
5. A binding has one value and one metadata record.
6. Topology changes and value reconciliation are distinct operations.
7. Unlinking removes one equation, not an entire inferred group.
8. Port values satisfy both sort and referential-integrity constraints.
9. Interaction requests are serializable data.
10. Commands are deterministic functions of explicit state and input.

### 4.2 Operational requirements

1. Rejected commands leave the state and semantic revision unchanged.
2. Accepted commands publish only invariant-satisfying snapshots.
3. Effects execute after an accepted transition.
4. Multiple engine instances are isolated.
5. Occurrence lifetime does not define domain-object lifetime.
6. The reference algorithms are simple enough to audit.
7. Optimized implementations can be compared with the reference semantics.

### 4.3 Assurance requirements

1. The state validator reports structured issue codes and paths.
2. Tests cover algebraic graph properties, not only UI examples.
3. Browser tests exercise the built artifact.
4. Audit notes explain significant semantic steps.
5. Claims of proof distinguish mathematical consequence, executable invariant, and test evidence.

---

# Part II — Formal and Architectural Model

## 5. Semantic identities

A cross-interaction system needs several identity domains.

### 5.1 Domain subject identity

A subject is a pair:

\[
\operatorname{SubjectRef}=\operatorname{SubjectType}\times\operatorname{Key}.
\]

For Sentinel, subject types include order, customer, card, device, IP, and view. Two references denote the same subject when both fields agree. This is semantic equality, not JavaScript object identity:

\[
(t_1,k_1)\equiv(t_2,k_2)
\iff t_1=t_2\land k_1=k_2.
\]

This distinction appears in the test that attempts to rewrite a pivot cell with a freshly allocated `{type: "card", key: "K-4411"}`. The command is rejected as already current even though the object reference differs.

### 5.2 View identity

A view is one logical component instance. Changing its focus changes every placement that presents that instance. A view has a `ViewId`, kind, and component-local state or ports.

### 5.3 Placement identity

A placement is a visual occurrence of a view within a workspace area. Closing a placement does not necessarily close the view. This distinction is required for linked duplicates and multi-window presentations.

### 5.4 Port identity

A port is one named boundary occurrence owned by one view:

\[
p=(\operatorname{owner},\operatorname{name},\operatorname{sort},
\operatorname{protocol},\operatorname{mode}).
\]

`V-3/focus-order` and `V-1/focus-order` have the same schema but distinct local identity until linked.

### 5.5 Link identity

A link edge records one user-declared identification. It has its own identity because it must be named in undo, unlink, audit, persistence, and collaboration protocols. Two paths can connect the same ports; removing one edge must not remove connectivity supplied by another path.

### 5.6 Binding identity

A binding is a derived equivalence class of ports. Its runtime ID is canonicalized from sorted members:

```text
B:V-1/focus-order|V-2/focus-order|V-3/focus-order|V-4/focus-order
```

The string is an implementation convenience. The semantic object is the member set. In a distributed or import context, binding IDs may be alpha-renamed while preserving incidence.

## 6. Typed open components

An open component has internal behavior and a public boundary. Sentinel views are open because they expose ports that other views can connect without learning their rendering internals.

The replacement schema is independent of fixtures and UI:

```ts
export function portsForView(view: ViewState): readonly PortState[] {
  if (view.kind === "kernel") return [];
  return [
    {
      id: focusPortId(view.id),
      owner: view.id,
      name: "focus-order",
      sort: "order-id",
      protocol: "equality-cell",
      mode: "read-write",
    },
    {
      id: pivotPortId(view.id),
      owner: view.id,
      name: "pivot",
      sort: "subject-ref",
      protocol: "equality-cell",
      mode: "read-write",
    },
  ];
}
```

A link is well typed only when endpoint sorts and protocols match. In judgment form:

\[
\frac{
\Gamma\vdash p:\operatorname{Port}(A,\pi,m_p)
\qquad
\Gamma\vdash q:\operatorname{Port}(A,\pi,m_q)
\qquad
\operatorname{compatibleMode}(m_p,m_q)
}{
\Gamma\vdash p\equiv q\;\mathsf{linkable}
}.
\]

The current equality-cell protocol allows read-write peers and rejects the same endpoint, endpoints owned by the same component instance, different sorts, different protocols, and endpoints already in one quotient class. Future protocols may distinguish event streams, directed mappings, commands, constraints, or monotone knowledge cells. Those should not be disguised as equality links.

Structured-cospan research treats open systems through explicit input and output interfaces and composes them by gluing compatible boundaries [Baez and Courser 2020]. The present implementation uses only the elementary finite-set shadow of that idea, but the architectural consequence is the same: components publish typed boundaries; composition acts on boundaries rather than private implementation.

![Layered architecture of the replacement artifact.](figures/06-architecture-layers.png){#fig:architecture width=86%}


## 7. Links as generators of an equivalence relation

Let \(P\) be the finite set of ports. Let \(E\) be the finite set of link edges. Each edge has two endpoint maps:

\[
s,t:E\rightrightarrows P.
\]

The link graph generates the least equivalence relation \(\sim_E\) satisfying:

\[
\forall e\in E,\quad s(e)\sim_E t(e).
\]

For an undirected equality-link protocol, \(\sim_E\) is graph connectivity. Reflexivity, symmetry, and transitivity are not optional implementation details; they define the meaning of a shared binding.

The quotient set is:

\[
Q=P/{\sim_E}.
\]

The quotient map

\[
q:P\to Q
\]

sends each local port to its binding class.

### 7.1 Coequalizer interpretation

The map \(q\) coequalizes the endpoint maps:

\[
q\circ s=q\circ t.
\]

That is, each edge's endpoints receive the same global binding identity. More importantly, if another interpretation \(f:P\to X\) treats every linked pair equally, then there is a unique map \(\bar f:Q\to X\) such that:

\[
f=\bar f\circ q.
\]

This universal property explains why downstream code should consume binding classes instead of repeatedly traversing raw edges. Any link-respecting observation factors through the quotient.

![Port identification as a finite coequalizer/quotient construction.](figures/07-port-quotient.png){#fig:quotient width=100%}


### 7.2 Concrete compilation

`rebuildBindings` implements the finite quotient using union-find:

1. initialize one singleton set per port;
2. validate every edge endpoint and type;
3. union each edge's endpoints;
4. group ports by representative;
5. sort members to obtain a canonical class description;
6. collect internal generating edge IDs;
7. choose a value and metadata seed;
8. populate `bindings` and `portBinding` indexes.

The implementation does not persist the union-find parent forest. It persists the source graph and materializes a canonical quotient snapshot. This is intentional: union-find supports additions efficiently but forgets the provenance needed for arbitrary deletion.

### 7.3 Proposition: insertion-order independence

**Proposition 1.** For a fixed port set \(P\) and edge set \(E\), the equivalence classes produced by union operations are independent of the order in which edges are processed.

**Proof sketch.** Each union operation adds one equation to the generated equivalence closure. The least equivalence relation containing a set of pairs depends on the set, not its enumeration. Union-find representatives may differ internally, but grouping by connectivity and canonical sorting produces the same member sets. ∎

**Test evidence.** The test suite reverses all initial edge insertion order, rebuilds, and compares `portBinding` and canonical member sets.

### 7.4 Proposition: alternate paths preserve identification

**Proposition 2.** Removing an edge \(e\) does not separate ports \(p,q\) if a path from \(p\) to \(q\) remains in \(E\setminus\{e\}\).

This is a basic graph-connectivity result. It matters operationally because “unlink this edge” is not equivalent to “separate these two ports.” The test suite adds an alternate edge, removes the original bridge, and confirms the class does not split.

## 8. Binding cells and value semantics

The quotient describes topology. A separate value function supplies state:

\[
v:Q\to V.
\]

For a port \(p\), reading is:

\[
\operatorname{read}(p)=v(q(p)).
\]

The implementation materializes a binding cell:

```ts
interface BindingCell {
  id: BindingId;
  members: readonly PortId[];
  edgeIds: readonly LinkId[];
  sort: PortSort;
  protocol: PortProtocol;
  value: PortValue;
  meta: BindingMeta;
}
```

This normalization removes the need for propagation. A write to any member updates one cell.

### 8.1 Proposition: linked-port coherence

**Proposition 3.** If \(p\sim_E q\), then `read(p) = read(q)`.

**Proof.** Since \(p\sim_E q\), the quotient map gives \(q(p)=q(q)\). Applying the function \(v\) to equal arguments yields \(v(q(p))=v(q(q))\). ∎

This proposition is true by representation, not by a convention that commands must copy values correctly.

### 8.2 Proposition: write coherence

Define a write to port \(p\) with value \(x\) as replacing \(v(q(p))\) by \(x\). For every \(r\sim_E p\):

\[
\operatorname{read}_{\operatorname{write}(p,x)}(r)=x.
\]

The implementation reports this as an audit note: “wrote one quotient cell shared by \(n\) port(s).” Figure 4 shows the user-visible consequence.

![Cross-view focus propagation by one binding-cell update.](figures/02-linked-focus-propagation.png){#fig:focus-propagation width=100%}


### 8.3 Value typing

Each binding class has one sort because all linked endpoints are compatible. Let \(\llbracket A\rrbracket_S\) be the valid runtime values of sort \(A\) in domain state \(S\). A well-formed binding requires:

\[
v(B)\in\llbracket \operatorname{sort}(B)\rrbracket_S.
\]

For `order-id`:

\[
\llbracket\operatorname{order-id}\rrbracket_S
=
\{\mathsf{null}\}\cup\operatorname{dom}(S.\operatorname{orders}).
\]

For `subject-ref`, validity requires a recognized subject type and an existing referent in the corresponding domain table.

### 8.4 Reconciliation is not topology

Before linking, two classes \(B_s\) and \(B_t\) may carry values \(x\) and \(y\). Adding an edge determines the new member set but does not mathematically imply a value. The command must supply an algebra or policy:

\[
\rho:V\times V\to V+\operatorname{Conflict}.
\]

The implemented policies are:

\[
\begin{aligned}
\rho_{source}(x,y)&=x,\\
\rho_{target}(x,y)&=y,\\
\rho_{equal}(x,y)&=
\begin{cases}
x & x\equiv y,\\
\operatorname{Conflict}(x,y)&\text{otherwise.}
\end{cases}
\end{aligned}
\]

`require-equal` demonstrates why this is a transaction. The candidate edge is created only in an uncommitted state. If reconciliation fails, the old graph and revision are returned unchanged.

### 8.5 Unlink semantics

Removing one edge can leave a class connected or split it into several components. The quotient alone cannot tell which edge to remove; therefore explicit edge provenance is retained.

When a class \(B\) with value \(x\) splits into \(B_1,\ldots,B_k\), the replacement initializes:

\[
\forall i,\quad v'(B_i)=x.
\]

Thus unlinking changes future coupling but not current observations.

**Proposition 4 (value preservation on unlink).** Immediately after an unlink command, every surviving endpoint reads the same value it read before the command.

**Proof sketch.** Each new component's predecessor set contains the old binding. `rebuildBindings` copies that predecessor's value into every resulting component. No value-changing command is composed with unlink. ∎

After the split, classes are independently writable. A test isolates the inspector, writes `ORD-1050` to it, and confirms the queue remains `ORD-1043`.

## 9. Commands as atomic transitions

The durable kernel is a transition function:

\[
\delta:S\times C\to
\operatorname{Accepted}(S',F,N)
+
\operatorname{Rejected}(r,I).
\]

Here \(F\) is a finite list of effects, \(N\) audit notes, \(r\) a reason, and \(I\) optional invariant issues.

A command follows the pipeline shown in Figure 5.

![Atomic command transaction and publication path.](figures/08-command-transaction.png){#fig:command-flow width=74%}


### 9.1 Accepted transitions

An accepted transition:

1. starts from an invariant-valid state;
2. validates command-local preconditions;
3. constructs an immutable candidate;
4. recomputes derived quotient structures where necessary;
5. validates all global invariants;
6. increments the semantic revision once;
7. returns effects and audit notes;
8. publishes only after the kernel returns.

### 9.2 Rejected transitions

A rejected transition returns the exact previous state object. It does not increment counters or revisions, install partial edges, or run effects. This gives the atomicity law:

\[
\delta(s,c)=\operatorname{Rejected}(-)
\Longrightarrow s_{after}=s.
\]

### 9.3 Determinism

For explicit state and command data:

\[
\forall s,c,\quad \delta(s,c)=\delta(s,c).
\]

The expression is logically trivial but operationally meaningful: there are no clock reads, random IDs, module counters, DOM queries, or ambient engines in `applyCommand`. Effects are descriptions, not executions.

### 9.4 Effects

`ExportView` returns a `download` effect while leaving domain and binding state unchanged. The semantic revision still advances because the command was accepted and recorded. A stricter event-sourced design might maintain separate domain and command-log revisions; the prototype uses one semantic revision for simplicity.

Algebraic-effect research provides a more general account in which effectful programs are built from operations and interpreted by handlers [Plotkin and Pretnar 2013]. The current artifact uses a small first-order effect list, sufficient to separate browser APIs from the kernel.

## 10. Executable invariants

`validateState` is a total inspection from `AppState` to a list of structured issues. It checks the following families.

### 10.1 Workspace and placement invariants

- the active workspace exists;
- every placement references an existing workspace and view;
- no workspace has duplicate area occupancy;
- every view has at least one placement.

### 10.2 Component-schema invariants

- every port owner exists;
- every view has exactly the ports declared by its kind;
- port IDs, names, sorts, protocols, and modes agree with the schema.

### 10.3 Link invariants

- every edge endpoint exists;
- linked endpoints have equal sort and protocol;
- duplicate undirected endpoint pairs are rejected.

### 10.4 Quotient invariants

- binding member arrays are sorted and nonempty;
- binding IDs are canonical functions of members;
- every port appears in exactly one binding;
- `portBinding` and `bindings` agree in both directions;
- binding sort and protocol agree with every member;
- every binding value is valid for every member;
- `edgeIds` exactly match edges internal to the class;
- every link's endpoints map to the same binding;
- metadata names are nonempty.

### 10.5 Implementation invariant preservation

The kernel checks the incoming state with `assertValidState` and checks every candidate before returning `accepted`. Therefore, assuming `validateState` itself is correct:

\[
\operatorname{Valid}(s)\land
\delta(s,c)=\operatorname{Accepted}(s')
\Longrightarrow
\operatorname{Valid}(s').
\]

This is an executable preservation theorem schema, not a mechanized proof of each command branch. Tests corrupt an index deliberately and verify that the checker identifies both the local mismatch and missing target binding.

## 11. Interaction as serializable transient state

The durable state should not contain closures, DOM nodes, promise continuations, or menu callbacks. The engine therefore maintains a separate `InteractionSnapshot`:

```ts
interface InteractionSnapshot {
  selection: SelectionRequest | null;
  hoverPortId: PortId | null;
  hoverSubject: SubjectRef | null;
}
```

A selection request is finite data. The pending JavaScript promise resolver remains private to the engine and is cleared exactly once on success or cancellation.

### 11.1 Selection state machine

The implemented protocol is:

```text
Idle
  --selectCompatiblePort(source)--> Selecting(request)
Selecting
  --resolve(incompatible)---------> Selecting
Selecting
  --resolve(compatible)-----------> Idle + selected(port)
Selecting
  --cancel------------------------> Idle + null
```

Tests establish that requests serialize, incompatible endpoints do not resolve the operation, compatible endpoints resolve once, later resolutions fail, and cancellation is terminal.

### 11.2 Occurrences

An occurrence is an adapter-level registration associating a DOM element with a subject, view, or port. Occurrence count is observational data. It is not part of durable domain state and does not control subject lifetime.

CLIM presentations similarly associate screen output with an object and semantic presentation type, allowing displayed objects to satisfy later input requests [LispWorks 2021a]. The replacement retains this semantic association while moving link topology and values out of the presentation occurrence itself.

### 11.3 Coalgebraic extension

The current selection machine is finite. Rich workflows can be unbounded: select, fetch, retry, confirm, commit, compensate, and wait for external responses. Interaction trees represent recursive impure behavior as coinductive structures over uninterpreted events and handlers, with equivalence based on weak bisimulation [Xia et al. 2020]. A future PBUI workflow layer can interpret the same program in the browser, tests, replay tools, or a proof assistant.

---

# Part III — Implementation

## 12. Artifact architecture

The replacement artifact is intentionally small enough to inspect. Its semantic TypeScript source is approximately 1,400 lines excluding the browser renderer; tests add about 300 lines. The architecture follows dependency direction rather than feature location.

```text
model.ts
   ↑
schema.ts       fixtures.ts
   ↑                ↑
graph.ts ─────── invariants.ts
   ↑                ↑
kernel.ts ──────────┘
   ↑
queries.ts      engine.ts
      \          /
          ui.ts
```

`model.ts` defines data but executes no domain behavior. `schema.ts` defines component boundaries. `graph.ts` computes quotient and value judgments. `invariants.ts` checks complete state. `kernel.ts` transacts commands. `queries.ts` derives read-only observations and actions. `engine.ts` owns instance-scoped transient behavior. `ui.ts` renders and translates browser events.

The dependency graph is not perfectly acyclic in the abstract mathematical sense because invariants inspect structures created by graph and schema modules, while the kernel invokes invariants. It is nevertheless organized so that rendering cannot become a hidden dependency of semantics.

## 13. The data model

### 13.1 Durable state

`AppState` contains:

```ts
interface AppState extends DomainState {
  revision: number;
  counters: Counters;
  views: Readonly<Record<ViewId, ViewState>>;
  ports: Readonly<Record<PortId, PortState>>;
  links: Readonly<Record<LinkId, LinkEdge>>;
  bindings: Readonly<Record<BindingId, BindingCell>>;
  portBinding: Readonly<Record<PortId, BindingId>>;
  workspaces: Readonly<Record<WorkspaceId, WorkspaceState>>;
  workspaceOrder: readonly WorkspaceId[];
  activeWorkspaceId: WorkspaceId;
  placements: Readonly<Record<PlacementId, PlacementState>>;
}
```

Two fields deserve explanation.

`links` is extensional source state: the user-declared generating equations. `bindings` and `portBinding` are materialized derived indexes. Storing both source and derived state introduces a consistency obligation, which the invariant checker enforces. The alternative would be to compute all bindings on every read, reproducing the original performance problem. In a production event-sourced implementation, bindings could be an in-memory projection reconstructed from durable links.

`counters` are durable because allocation is part of command semantics. More sophisticated systems may use UUIDs supplied by commands, server-assigned IDs, or content-derived identifiers. The essential requirement is that allocation input be explicit.

### 13.2 Immutable update convention

The implementation uses TypeScript `readonly` interfaces and shallow structural copying. Runtime objects are not deeply frozen, so immutability remains a programming discipline rather than an enforcement mechanism. A test serializes the input state before an accepted command and confirms it remains unchanged.

A production kernel could strengthen this through:

- persistent data structures;
- development-mode deep freezing;
- a language with linear or uniqueness types;
- generated update functions;
- mechanized extraction from a pure language.

For this artifact, the combination of pure functions, narrow module boundaries, and tests is adequate evidence.

## 14. Component schema

The original prototype generated ports in fixture code and repeated assumptions in view logic. The reimplementation isolates schema in `src/schema.ts`.

This module is deliberately boring. Its importance lies in being singular: initial-state creation, invariant checking, and kind-change commands all call the same `portsForView`. A view is not allowed to “mostly” match its declared kind.

### 14.1 Why `kernel` has no ports

The demonstration's kernel inspector is observational. It is not intended to participate in focus or pivot linking, so its schema is empty. This creates a useful regression case: changing a linked inspector into a kernel view requires removing two ports. The command is rejected until those ports are singleton classes.

### 14.2 Port mode

The current mode model supports `read`, `write`, and `read-write`, but compatibility checks presently focus on equality-cell sorts and protocols because all fixtures are read-write. A complete mode judgment should reject a class with no readable endpoint or define how write-only publishers interact with readers. This remains an explicit extension point rather than an undocumented assumption.

## 15. Quotient compiler

### 15.1 Union-find implementation

`UnionFind` stores a parent map and rank map. `find` performs path compression; `union` applies union by rank. The data structure determines connectivity, not final binding identity. After union operations, the compiler iterates over all ports, groups by root, and sorts each member list.

The canonical binding ID is:

```ts
const canonicalBindingId = (members: readonly PortId[]): string =>
  `B:${members.join("|")}`;
```

Canonical IDs simplify tests and screenshots. They also make topology changes visible: adding or removing a member changes the ID. Code that needs identity stable across topology changes should use explicit lineage/provenance rather than treating binding IDs as durable entity IDs.

### 15.2 Predecessor tracking

A topology rebuild must transfer values and metadata from old classes to new classes.

For each new component, the compiler finds predecessor binding IDs by looking up every member in the previous `portBinding`. There are three ordinary cases:

1. **No predecessor:** a new port; use a seed function or default null value.
2. **One predecessor:** unchanged class or split result; preserve value and metadata.
3. **Two predecessors under an explicit merge:** apply the command's reconciliation and metadata policy.

An unexplained new component with multiple predecessors throws. This guard prevents a future caller from constructing a graph merge outside the command path and silently selecting the first old value.

### 15.3 Merge metadata

For `prefer-source`, the source binding supplies default name and color; `prefer-target` uses the target. Command fields can override either. `require-equal` uses source metadata after proving semantic value equality.

This policy is intentionally simple. A larger system may need:

- immutable user-defined binding entities whose identity survives class changes;
- metadata merge dialogs;
- provenance lists recording all predecessor names;
- policy objects rather than string enums;
- collaborative conflict values.

The key correction is that the choice is explicit and located beside value reconciliation.

### 15.4 Semantic value equality

`samePortValue` treats strings by primitive equality and `SubjectRef` by `(type,key)`. This prevents referential allocation from affecting semantic behavior.

The current value universe is a tagged union. A generalized kernel should move equality into the port sort declaration:

```ts
interface PortSort<A> {
  name: string;
  validate(state: AppState, value: unknown): value is A;
  equals(left: A, right: A): boolean;
  format(value: A): string;
}
```

That would allow dates, sets, ranges, versioned documents, or domain-specific equivalence without extending one central switch.

## 16. Command kernel

### 16.1 The accept helper

Every successful branch calls one helper that increments revision, validates the candidate, and constructs the accepted result. This avoids a common reducer failure in which one new branch forgets to enforce global rules.

```ts
function accept(previous, nextWithoutRevision, notes = [], effects = []) {
  const next = {
    ...nextWithoutRevision,
    revision: previous.revision + 1,
  };
  const issues = validateState(next);
  if (issues.length > 0) {
    return {
      status: "rejected",
      state: previous,
      reason: "command would violate kernel invariants",
      issues,
    };
  }
  return { status: "accepted", state: next, effects, notes };
}
```

The helper is not a substitute for command-local errors. It is a final safety net. Local validation supplies clearer messages and avoids unnecessary candidate construction.

### 16.2 `WritePort`

The branch checks:

1. endpoint existence;
2. write mode;
3. value representation and referent;
4. binding existence;
5. semantic change rather than object-reference change.

It updates only one `BindingCell`. Class members and edge topology are unchanged.

### 16.3 `LinkPorts`

The branch:

1. calls `canLinkPorts`;
2. allocates a link ID from state;
3. constructs a base candidate with the new edge;
4. calls `rebuildBindings` with merge evidence and policy;
5. catches a typed `ReconciliationError`;
6. commits the new quotient if all invariants hold.

The audit notes name the generating equation, resulting class size, and reconciliation policy. Those notes are not formal proof terms, but they make the semantic path inspectable.

### 16.4 `UnlinkPorts`

The branch removes exactly one edge and rebuilds. It does not delete a “group,” copy endpoint values manually, or assume the class splits. The graph determines the result.

This is an important product distinction. A visible port group may have a star, chain, or redundant graph. Users may eventually need commands such as “detach this port” or “dissolve this binding,” but those should compile to explicit edge-set changes rather than overloading one edge-removal command.

### 16.5 Binding metadata commands

`RenameBinding` and `SetBindingColor` address a port, then resolve its current class. The metadata operation therefore follows class topology. After a split, each descendant initially inherits the old metadata and can be renamed independently.

### 16.6 Domain commands

Order approval, decline, escalation, and card compromise remain direct pure updates. They demonstrate that the port/link kernel coexists with ordinary application commands rather than replacing them.

### 16.7 View kind changes

`SetViewKind` calculates old and desired boundary schemas. Removing a linked port is rejected because silently deleting it would mutate another component's logical binding. Singleton ports may be removed. New ports receive singleton binding cells through quotient rebuilding.

### 16.8 Placement closing

`ClosePlacement` first enforces at least one placement per workspace. It then removes the placement. If another placement references the same view, the view survives. Otherwise, the kernel removes the view, its ports, incident edges, and derived bindings.

This logic makes placement lifetime explicit without requiring reference-count fields that can drift.

## 17. Engine and snapshot protocol

`KernelEngine` is an imperative shell around the pure kernel. It owns:

- current durable state;
- cached `EngineSnapshot`;
- listeners;
- command log;
- interaction snapshot;
- occurrence registry;
- one pending selection continuation;
- effect handler.

### 17.1 Cached snapshots

React requires an external store's `getSnapshot` to return the same object while the underlying store is unchanged [React 2026a]. The engine constructs and caches one snapshot on publication rather than allocating a fresh wrapper on every read.

### 17.2 Publication order

For a command:

1. call the pure kernel;
2. replace durable state only on acceptance;
3. append a deterministic log entry;
4. publish one new snapshot;
5. run effects after publication.

The log records both rejected and accepted commands. Rejections use the same pre- and post-revision. This supports diagnosis without pretending a rejected operation modified semantic state.

### 17.3 Effect handler

The engine accepts an optional handler `(effect,state) => void`. Tests can omit it, record it, or substitute a deterministic handler. The browser adapter can implement downloads without contaminating command evaluation.

### 17.4 Selection continuations

The selection request is public data; the resolver is private process state. `selectCompatiblePort` first cancels an existing request, avoiding two simultaneous owners of the same modal interaction channel. A more general engine should support named channels or nested scopes, but ownership must remain explicit.

## 18. Derived query layer

`queries.ts` contains pure observations:

- compatible-port acceptance;
- ports owned by a view;
- focused order and pivot subject;
- orders using an entity;
- related orders;
- subject labels;
- derived actions.

These functions are not yet represented as a reified query language. They are conventional pure TypeScript functions and therefore partially opaque to an optimizer. The separation is still useful: renderers do not reach directly into binding internals.

A future rule/query system can compile these relations incrementally. Tarski's fixed-point theorem gives least and greatest fixed points for monotone functions on complete lattices [Tarski 1955], and differential dataflow maintains changes through iterative computations using differences indexed by logical time [McSherry et al. 2013]. The current link quotient is finite and rebuilt directly; the architecture leaves room for an incremental derived-fact layer without requiring it prematurely.

## 19. Browser adapter

### 19.1 Why a DOM adapter

The user requested the core to be reimplemented. Rebuilding in vanilla DOM proves that:

- the state model does not depend on React hooks;
- the interaction engine is independently instantiable;
- screenshots exercise compiled kernel code rather than mocked diagrams;
- a later React adapter is a replaceable interpretation.

This is not a production recommendation to abandon React. React components should remain pure in rendering and synchronize with external systems through effects or store hooks [React 2026c; React 2026d]. The original bug arose because context and subscription targets disagreed, not because an external store is inherently wrong.

### 19.2 Semantic occurrence markup

Rendered subjects carry data attributes such as:

```html
<span
  data-subject-type="order"
  data-subject-key="ORD-1048"
  data-view-id="V-1"
>
  ORD-1048
</span>
```

Event delegation translates DOM activation into semantic commands. Port badges carry endpoint IDs and test IDs. This keeps browser elements as occurrences of kernel objects rather than the objects themselves.

### 19.3 Kernel inspector

The rightmost view exposes:

- invariant status;
- semantic revision;
- port, edge, class, and occurrence counts;
- each binding's name, value, members, and edge IDs;
- reset, isolate, and relink scenarios;
- recent accepted and rejected commands;
- semantic audit notes.

The inspector is part of the implementation method. It turns hidden topology into visible evidence and makes screenshot states scientifically interpretable.

## 20. Worked interaction scenarios

### 20.1 Initial triage topology

In the triage workspace, four focus ports form one `triage-focus` class, and four pivot ports form one `triage-pivot` class. The queue, linkage view, inspector, and ledger are independent component instances. They share only the declared cells.

The initial screenshot in Figure 1 shows `ORD-1043` as the focus value and `card:K-4411` as the pivot. The kernel inspector reports that invariants hold.

### 20.2 One focus write, four observations

Clicking order `ORD-1048` in the queue resolves the local view's `focus-order` endpoint, maps it to the four-member binding, and writes one cell. The inspector presents `ORD-1048`, the ledger switches to Dana Vex, and the linkage view updates through the same focus/pivot context. Figure 4 captures this state.

This scenario tests the most important replacement claim: there is no propagation loop. All readers converge because they use one cell.

### 20.3 Unlink and compatible-port selection

The “ISOLATE INSPECTOR” scenario removes edge `L-1`. In the star-shaped initial focus graph, that edge is a bridge for the inspector, so the quotient splits into:

\[
\{V1,V2,V4\}
\qquad\text{and}\qquad
\{V3\}.
\]

Both classes retain `ORD-1048`. Clicking the isolated inspector port starts a serializable compatible-port selection. Focus ports in other classes are highlighted; pivot ports are visibly rejected because their sort differs.

![Typed compatible-port selection after quotient splitting.](figures/03-compatible-port-selection.png){#fig:port-selection width=100%}


This screenshot also demonstrates that link selection targets ports, not whole views. The interaction state contains no lambda.

### 20.4 Relinking and reconciliation

Selecting the queue's focus port issues:

```ts
{
  type: "LinkPorts",
  source: "V-3/focus-order",
  target: "V-1/focus-order",
  reconcile: "prefer-source"
}
```

The new edge merges the singleton inspector class into the three-member class. The quotient compiler creates a canonical four-member binding. The command trace names the equation and policy.

![Relinked quotient and command/proof trace.](figures/04-relinked-quotient-and-proof-trace.png){#fig:relinked width=100%}


### 20.5 Ring-analysis workspace

The second workspace exercises the same kernel with graph and chart occurrences. Five focus ports share `ring-focus`; five pivot ports share `ring-pivot`. Clicking an SVG order mark writes the same typed focus cell as clicking a table row.

![Ring-analysis workspace demonstrating renderer-independent occurrences.](figures/05-ring-workspace.png){#fig:ring-workspace width=100%}


The graph and chart renderers do not own linking. They emit occurrences and commands against ports defined by component schema.

---

# Part IV — Evaluation

## 21. Test strategy

The evaluation is organized around semantic risk rather than file coverage.

### 21.1 Reference-state tests

Initial-state tests establish:

- repeated construction yields deep-equal states;
- all invariants hold;
- transitive edges produce one expected quotient;
- initial values and metadata seed the correct classes.

This detects hidden counters and import-order effects.

### 21.2 Algebraic graph tests

The suite checks:

- transitive closure;
- link insertion-order independence;
- one-cell write coherence;
- bridge removal and split;
- alternate-path preservation;
- independent writes after split;
- class-level metadata;
- same-class duplicate-link rejection;
- typed sort incompatibility.

These are closer to laws than examples. They can later be generalized through property-based generators.

### 21.3 Reconciliation and atomicity tests

Tests construct two classes with unequal values and then:

- merge with `prefer-source`, confirming source value and explicit name;
- merge with `require-equal`, confirming rejection, unchanged graph, and unchanged state object.

This ensures that conflict handling is not an afterthought in UI code.

### 21.4 Value-safety tests

The suite rejects:

- a typed subject object written to an `order-id` port;
- a subject reference to a nonexistent card;
- a semantically redundant subject write using a newly allocated object.

### 21.5 Lifecycle tests

The suite verifies:

- a linked view cannot change to a portless kind;
- an isolated view can change kind and removes its ports atomically;
- closing a final placement garbage-collects the view, ports, and edges;
- accepted effects do not alter domain or binding state.

### 21.6 Engine tests

Engine tests verify:

- instance isolation;
- cached independent state;
- serializable selection requests;
- one-shot resolution;
- explicit cancellation;
- rejected-command logging without revision change.

### 21.7 Invariant mutation test

One test manually corrupts `portBinding` and confirms that validation reports both a binding-index mismatch and a missing index target. This is mutation testing at the state-representation level.

## 22. Automated results

The final Node run reports:

```text
24 tests
24 passed
0 failed
```

The complete TAP output is stored at [`docs/test-results.txt`](test-results.txt).

The headless browser run reports:

```text
E2E CHECKS: 14 assertions passed
```

Its script verifies:

1. triage workspace mounts;
2. kernel invariants display as holding;
3. `ORD-1048` updates the inspector;
4. all four linked focus ports observe `ORD-1048`;
5. inspector isolation splits the class;
6. selection mode appears;
7. at least three compatible ports highlight;
8. at least one incompatible port dims;
9. selecting a target relinks the classes;
10. both endpoints map to one binding;
11. a malformed object write is rejected;
12. rejected writes do not advance revision;
13. the log records rejection;
14. the ring workspace and graph/chart views mount without page errors.

The browser output is stored at [`docs/e2e-results.txt`](e2e-results.txt).

## 23. Test matrix

| Property | Test mechanism | Result |
|---|---|---:|
| deterministic initial state | deep equality | pass |
| invariant-valid fixture | executable checker | pass |
| transitive quotient | member-set assertion | pass |
| one-cell write coherence | all member observations | pass |
| explicit source reconciliation | merge scenario | pass |
| atomic conflict rejection | state identity and edge count | pass |
| unlink split preserves value | bridge scenario | pass |
| alternate path preserves class | redundant-edge scenario | pass |
| runtime value typing | malformed writes | pass |
| semantic subject equality | fresh object, same key | pass |
| class metadata coherence | rename through one member | pass |
| link-order independence | reversed edge enumeration | pass |
| post-unlink independence | divergent write | pass |
| corruption detection | stale index mutation | pass |
| command determinism | equal transition results | pass |
| input immutability | serialized pre-state | pass |
| schema-safe kind change | reject/accept scenarios | pass |
| placement garbage collection | final occurrence closure | pass |
| engine instance isolation | two stores | pass |
| serializable selection | JSON serialization | pass |
| one-shot selection | repeated resolution | pass |
| browser propagation | Playwright | pass |
| browser split/relink | Playwright | pass |
| browser malformed write | Playwright | pass |

## 24. Complexity analysis

Let \(n=|P|\), \(m=|E|\), and \(b=|Q|\).

### 24.1 Topology rebuild

Union-find initialization is \(O(n)\). Processing links is \(O(m\alpha(n))\) amortized. Grouping ports is \(O(n\alpha(n))\). The implementation then scans edges for each component to collect `edgeIds`, which can reach \(O(bm)\). At the current scale this is immaterial; a production compiler should index edges by root in one pass, reducing the complete rebuild to near \(O((n+m)\alpha(n))\).

### 24.2 Read and write

`portBinding[portId]` and `bindings[bindingId]` are object-map lookups. Reads are expected \(O(1)\). Writes clone the binding map and one cell; with plain JavaScript objects, copying the top-level map is \(O(b)\). A persistent hash trie or localized mutable transaction could reduce this while preserving snapshot semantics.

### 24.3 Link and unlink

The reference implementation rebuilds all classes after each topology change. This is intentionally simple. For predominantly additive graphs, an incremental union-find cache is natural. Arbitrary deletion requires retaining the source graph and either:

- recomputing only the affected old component;
- using a fully dynamic connectivity structure;
- maintaining spanning forests plus replacement-edge search.

The durable representation does not constrain this optimization because links remain explicit.

### 24.4 Rendering

The demonstration rerenders the whole application on every snapshot. This is not proposed as a production strategy. A React adapter should subscribe to keyed observations such as:

```text
binding value by BindingId
binding metadata by BindingId
view observation by ViewId
interaction acceptance by PortId
workspace placements by WorkspaceId
```

The semantic decomposition enables fine-grained subscription; the demonstration prioritizes auditability.

## 25. Comparative failure behavior

### 25.1 Malformed port value

**Original:** accepted, copied through the component, renderer may fail later.  
**Replacement:** rejected before mutation with a specific sort error; revision unchanged.

### 25.2 Conflicting class merge

**Original:** source value silently wins.  
**Replacement:** caller chooses source, target, or equality requirement; equality conflict rejects atomically.

### 25.3 Edge deletion with redundant path

**Original:** values remain copied, but no explicit class object explains whether topology changed.  
**Replacement:** quotient recomputation proves the class remains one component.

### 25.4 Removing a view kind's ports

**Original:** old ports can survive a listener conversion.  
**Replacement:** boundary schema changes in the same transaction; linked removal is rejected.

### 25.5 Multiple application instances

**Original:** provider and subscription can point at different engines.  
**Replacement:** all state, listeners, and workflows are instance-owned; isolation is tested.

## 26. Validity threats

### 26.1 Fixture scale

The demonstration has tens of ports, not millions. Complexity conclusions about constant lookup are sound, but throughput and memory behavior at platform scale are not empirically established.

### 26.2 Handwritten tests

The suite covers important laws but is not exhaustive. It does not yet use generated random graph sequences, mutation testing across all invariant clauses, or exhaustive bounded-state exploration.

### 26.3 Browser adapter difference

The replacement UI uses DOM rendering rather than a direct modification of the original React file. This strengthens evidence of kernel independence but means the study does not measure React-specific rendering regressions. A production migration needs a React adapter test suite.

### 26.4 No concurrency

Commands are single-threaded and synchronous. Concurrent users, optimistic server reconciliation, stale capability evidence, and replicated link edits are outside the implementation.

### 26.5 No mechanized proof

The propositions are proof sketches over a straightforward finite model. The TypeScript implementation and invariant checker are not extracted from Lean, Coq, or Agda. Compiler bugs, JavaScript mutation, and unchecked casts remain in the trusted computing base.

---

# Part V — Theoretical Interpretation and Proof Roadmap

## 27. Relation to presentation-based user interfaces and CLIM

CLIM's presentation facility remembers output together with the associated Lisp object and a semantic presentation type. Previously displayed objects can then satisfy later input requests [LispWorks 2021a; LispWorks 2021b]. The supplied Sentinel prototype adopts this idea directly: `O` wraps rendered content with a `SubjectRef`, and a temporary input context changes which occurrences are sensitive.

The reimplementation does not reject that model. It narrows its jurisdiction.

### 27.1 What presentation semantics should own

A presentation/occurrence layer should answer:

- what semantic subject does this rendered region denote?
- on which surface and in which view is it mounted?
- is it pointer- and keyboard-reachable?
- which current input contexts can it satisfy?
- which contextual actions are available?
- how should acceptance and default activation be exposed accessibly?

### 27.2 What presentation semantics should not own

It should not be the sole owner of:

- logical view identity;
- port schemas;
- link topology;
- binding values;
- value reconciliation;
- command authorization;
- persistent workspace state;
- effect execution;
- view lifecycle.

CLIM command tables mediate commands, menus, and presentation translators [McCLIM 2026], while input contexts designate the kind of object currently requested [LispWorks 2021c]. The modern decomposition proposed here retains semantic occurrences and input contexts but treats them as clients of a separate open-component and command kernel.

This separation addresses a difference between CLIM output histories and React. CLIM presentations are specialized output records retained in a window's output history [LispWorks 2021d]. React's mounted tree is not a durable semantic history: virtualization and unmounting can remove occurrences while domain subjects and links remain. Therefore the kernel must not equate “currently mounted” with “exists.”

## 28. Why quotient and coequalizer language is useful

Category-theoretic terminology is justified only if it isolates a compositional law. Here the finite quotient does so.

### 28.1 Local names versus global interfaces

Each component owns local boundary names. Linking does not mutate those names into one JavaScript object. It declares that downstream link-respecting interpretations must treat them equally.

The quotient map is canonical relative to the edge set. It creates a smallest global interface in which all declared equations hold. “Smallest” is expressed by the coequalizer's universal property: it imposes no equality beyond that generated by the links.

This guards against two opposite implementation failures:

- **too fine:** keeping linked endpoints as independent state cells and merely copying values;
- **too coarse:** merging ports that happen to carry equal values or share a type without an explicit link path.

### 28.2 Pushout composition of open components

A complete composition of open components can be described as a pushout over a shared boundary. Informally:

1. take the disjoint union of component internals and boundaries;
2. identify the boundary ports named by the wiring interface;
3. retain the resulting open external boundary.

Structured cospans provide a general categorical framework for open networks with explicit interfaces [Baez and Courser 2020]. The artifact does not implement a generic cospan library. Its component schemas and equality links instantiate one practical special case.

### 28.3 The quotient is derived, the graph is durable

The universal construction forgets the history of how an equivalence class was generated. That is appropriate for consumers but insufficient for editing. A user must be able to remove link `L-1`, not merely request that an equivalence class somehow split.

The correct data architecture therefore stores both:

```text
source: explicit generating diagram (ports and edges)
derived: quotient binding classes
```

This mirrors compiler design: source syntax and normalized intermediate representation coexist because each answers different questions.

### 28.4 Colimits do not resolve values

The categorical gluing construction answers which interfaces are identified. It does not choose between `ORD-1043` and `ORD-1050`. A value policy is an additional algebra over the carrier.

This distinction generalizes:

- a pushout does not authorize the link;
- a coequalizer does not make writes transactional;
- a quotient does not provide undo provenance;
- connectedness does not imply bidirectional update laws;
- isomorphic topology does not imply equal runtime IDs.

A design that says “use a colimit for shared state” without these qualifications is incomplete.

## 29. Limits, compatible states, and lenses

Quotients answer the name-identification question. Compatible state spaces often have a limit shape.

Suppose chart state \(S_C\) and pipeline state \(S_P\) each expose a document observation:

\[
f:S_C\to D,
\qquad
g:S_P\to D.
\]

The pairs that already agree form the pullback:

\[
S_C\times_D S_P
=
\{(c,p)\mid f(c)=g(p)\}.
\]

This does not define how to repair a disagreeing pair. It describes the consistent subspace.

### 29.1 Shared cell versus synchronized projections

There are two broad implementation strategies.

**Normalized shared cell.** Both components' ports read one binding value. Local view state excludes duplicated document selection. This is the strategy used by the artifact.

**Bidirectional projections.** Each component retains its own representation, and a synchronizer translates updates. This is necessary when chart and pipeline selections are structurally different.

### 29.2 Lens laws

A lens from source \(S\) to view \(A\) has `get` and `put` operations. Classical laws include:

\[
\begin{aligned}
\operatorname{get}(\operatorname{put}(s,a))&=a &&\text{(Put-Get)},\\
\operatorname{put}(s,\operatorname{get}(s))&=s &&\text{(Get-Put)},\\
\operatorname{put}(\operatorname{put}(s,a),b)&=\operatorname{put}(s,b) &&\text{(Put-Put)}.
\end{aligned}
\]

Bidirectional-transformation research develops combinators satisfying such well-behavedness conditions [Foster et al. 2007]. Lenses are suitable for connecting a port to a nested component-state location or translating between representations. They are not a replacement for the link graph: a multi-party dynamic network can have cycles, concurrent writers, and topology changes outside the classical one-source/one-view lens setting.

### 29.3 Recommended separation

```text
component local state --lawful optic--> local typed port
local typed ports      --link graph--> quotient class
quotient proposals     --reconciliation algebra--> one class value
```

Each arrow has its own laws. This modularity is more useful than attempting to define one “super-link” abstraction.

## 30. Commands, effects, and ongoing interaction

The command kernel is inductive: commands and finite transitions are data. User interaction can be potentially unbounded and is better modeled coalgebraically or through effect programs.

### 30.1 Command algebra

The command union is a first-order syntax. Interpreting it through `applyCommand` is a fold over constructors. This supports structural case analysis and exhaustive checking. New command constructors require updating the interpreter, logger, and codecs, making the extension surface visible.

### 30.2 Algebraic effects

Operations such as:

```text
ChoosePort
ConfirmConflict
IssueCommand
AwaitPersistence
NotifyUser
```

can be represented without committing to a browser implementation. A handler supplies meaning. Plotkin and Pretnar's account relates handlers to models of algebraic theories and homomorphisms from free models [Plotkin and Pretnar 2013].

The artifact implements only `download` as a returned effect and a private promise-based selection workflow. A next version can represent the link workflow as effect syntax:

```ts
const linkPorts = workflow(function* (source: PortId) {
  const target = yield* chooseCompatiblePort(source);
  const policy = yield* chooseReconciliation(source, target);
  return yield* issue({
    type: "LinkPorts",
    source,
    target,
    reconcile: policy,
  });
});
```

Production, test, replay, and remote handlers can interpret the same program.

### 30.3 Coinductive behavior

Long-running workflows, streams, and event loops may not terminate. Interaction trees model such behavior with coinductive event trees and continuations, while still supporting executable interpreters and equational reasoning [Xia et al. 2020].

A future correctness goal for a React adapter is trace refinement:

\[
\operatorname{Traces}(H_{React}(p))
\subseteq
\operatorname{Traces}(H_{Spec}(p)).
\]

The browser may introduce rendering and scheduling steps, but every semantic selection, cancellation, and command must be allowed by the reference handler.

## 31. Fixed points, recursive rules, and transfinite induction

The implemented quotient is a finite graph computation, not a transfinite runtime. Fixed-point reasoning becomes relevant when the system derives facts recursively.

### 31.1 A possible fact layer

Base facts could include:

```text
Port(p, sort, protocol)
Link(e, p, q)
Mounted(occurrence, subject, view)
Requests(context, sort)
Capability(context, operation)
```

Rules could derive:

```text
SameBinding(p, q)
Acceptable(context, occurrence)
AvailableAction(context, subject, action)
ReachableTarget(context, port)
```

For positive rules over a finite active domain, an immediate-consequence operator

\[
T:\mathcal P(F)\to\mathcal P(F)
\]

is monotone. The intended facts are the least fixed point \(\mu T\). Tarski established that monotone endofunctions on complete lattices have a complete lattice of fixed points [Tarski 1955].

### 31.2 Finite runtime convergence

If only finitely many ground facts can exist and rules only add facts, ascending iteration stabilizes in finitely many strict additions:

\[
\varnothing\subseteq T(\varnothing)
\subseteq T^2(\varnothing)\subseteq\cdots.
\]

A worklist or semi-naive evaluator is sufficient. This is the practical target for subtype closure, link reachability, action inheritance, and mounted-candidate queries.

### 31.3 Transfinite metatheory

For a general monotone operator on a complete lattice, one may define ordinal approximants:

\[
X_0=\bot,
\qquad
X_{\alpha+1}=T(X_\alpha),
\qquad
X_\lambda=\bigvee_{\beta<\lambda}X_\beta.
\]

A transfinite induction proof of an invariant \(I(X_\alpha)\) has base, successor, and limit obligations. This is a legitimate proof technique for general fixed-point semantics. It does not justify ordinal counters in JavaScript.

For Sentinel's current finite ports and edges, connectivity terminates through ordinary finite algorithms. Transfinite reasoning belongs in the general semantics of an extensible recursive rule language, not the link-button event handler.

### 31.4 Fixed-point induction for safety

If a rule system's operator is monotone, a property \(P\) containing the base facts and closed under one consequence step contains the least fixed point:

\[
T(P)\subseteq P
\Longrightarrow
\mu T\subseteq P.
\]

This is a natural route to proving that every derived action carries a valid capability premise or that every accepted target has compatible sort evidence.

## 32. Incremental maintenance and provenance

The artifact rebuilds derived structures directly. A platform-scale PBUI should maintain them incrementally while retaining explainability.

### 32.1 Change equation

For query \(q\), world \(W\), and change \(\Delta W\), an incremental implementation should satisfy:

\[
\operatorname{eval}(q,W\oplus\Delta W)
=
\operatorname{eval}(q,W)
\oplus
\operatorname{update}(q,W,\Delta W).
\]

The operator \(\oplus\) depends on the result domain. Sets use insertions/removals; maps use keyed patches; lattice facts use joins.

Differential dataflow generalizes incremental computation to iterative operators and changing inputs [McSherry et al. 2013]. It is relevant if action applicability, link reachability, and cross-view queries become one recursive derived database.

### 32.2 Provenance

The kernel inspector currently stores human audit notes. A richer rule layer can attach derivation provenance. Semiring provenance uses addition for alternative derivations and multiplication for joint premises [Green, Karvounarakis, and Tannen 2007].

For example:

```text
CanLink(V3.focus,V1.focus)
  because
    sameSort(order-id)
    × sameProtocol(equality-cell)
    × differentOwner
    × distinctBinding
```

Different interpretations can answer:

- whether any derivation exists;
- how many supports exist;
- which base facts matter;
- which derivation is cheapest;
- what explanation should be displayed.

A provenance expression is not automatically an authorization credential. The command kernel must still validate current authoritative state.

## 33. Formal verification roadmap

The current implementation is proof-oriented rather than formally verified. A staged verification program is feasible.

### 33.1 Property-based testing

Generate finite valid states and command sequences. Compare invariants after every accepted command. Specific generators should cover:

- arbitrary forests and cyclic link graphs;
- bridge and non-bridge deletion;
- link insertion permutations;
- class merges with all reconciliation policies;
- view/placement reference graphs;
- valid and invalid port values;
- import/export alpha-renaming.

A slow breadth-first reference quotient can be compared with union-find output after every topology change.

### 33.2 Alloy model

Alloy is designed for compact relational structural models and bounded automatic analysis [Jackson 2002]. A small model can search for counterexamples to:

- every port belongs to exactly one binding;
- every link's endpoints share a binding;
- closing a final placement leaves no orphan view;
- unlink affects no unrelated component;
- schema changes preserve endpoint compatibility;
- duplicate links are rejected.

Bounded analysis is not an unbounded proof, but it is well suited to finding missing relations in a state schema.

### 33.3 TLA+ model

TLA represents state-transition actions and temporal properties [Lamport 1994]. It is suitable once commands become asynchronous or distributed. Candidate properties include:

```text
Safety:
  Accepted(LinkPorts) => endpoints existed and were compatible

Atomicity:
  Rejected(command) => state' = state

NoDoubleResolve:
  a selection ID reaches at most one terminal outcome

EventualResolution:
  under fairness, every selected compatible target eventually
  commits, rejects as stale, or is explicitly cancelled
```

### 33.4 Lean or Coq kernel

A mechanized core can define:

- finite ports and edges;
- generated equivalence closure;
- quotient observations;
- typed values;
- commands and transition relation;
- invariant preservation;
- selection-state machine.

Candidate theorems are listed in Chapter 34. The TypeScript implementation can initially be tested against extracted test vectors. Later, a verified reference evaluator or generated kernel could reduce the trusted code base.

### 33.5 Refinement boundary

The most valuable mechanized theorem is not “the CSS is correct.” It is that optimized and adapter layers refine the semantic core:

\[
\operatorname{observe}(\operatorname{Impl}(s,c))
=
\operatorname{observe}(\operatorname{Spec}(s,c)).
\]

The observation function can ignore caches, generated IDs, and rendering-only fields while preserving domain, topology, values, command outcomes, and effects.

## 34. Theorem and invariant catalogue

| ID | Statement | Status |
|---|---|---|
| Q1 | Every port maps to exactly one quotient class | executable invariant + tests |
| Q2 | Every link's endpoints map to the same class | executable invariant + tests |
| Q3 | Class membership is independent of edge insertion order | proof sketch + test |
| Q4 | Alternate paths preserve identification after edge removal | graph theorem + test |
| V1 | Equivalent ports observe equal values | by representation + test |
| V2 | One write updates every equivalent observation | by representation + browser test |
| V3 | Binding values satisfy every member port's sort | executable invariant + tests |
| L1 | `require-equal` merge is atomic | test |
| L2 | Unlink preserves immediate endpoint observations | proof sketch + test |
| L3 | Split descendants become independently writable | test |
| C1 | Accepted commands preserve complete-state validity | runtime gate; mechanized proof pending |
| C2 | Rejected commands leave semantic state unchanged | implementation + tests |
| C3 | Commands are deterministic from explicit state and input | architecture + test |
| C4 | Accepted commands do not mutate input snapshots | test |
| S1 | View ports exactly match component schema | executable invariant + tests |
| P1 | Every view has a placement | executable invariant |
| P2 | Closing a final placement removes semantic orphans | test |
| I1 | Selection request is serializable | test |
| I2 | A selection resolves at most once | test |
| I3 | Engine instances are isolated | test |
| R1 | React/DOM adapter traces refine workflow traces | future proof obligation |
| D1 | Encoded workspaces round-trip up to ID renaming | future proof obligation |

---

# Part VI — Migration, Limitations, and Conclusions

## 35. Migration plan for the original React prototype

The new kernel can be integrated without rewriting the visual components.

### 35.1 Phase 1: replace the global store contract

Construct `KernelEngine` inside an application root or dependency-injection boundary. Provide it through context:

```tsx
const KernelContext = createContext<KernelEngine | null>(null);

function useKernel(): KernelEngine {
  const engine = useContext(KernelContext);
  if (!engine) throw new Error("missing KernelContext");
  return engine;
}

function useKernelSnapshot(): EngineSnapshot {
  const engine = useKernel();
  return useSyncExternalStore(
    engine.subscribe,
    engine.getSnapshot,
    engine.getSnapshot,
  );
}
```

Both subscription and dispatch now use the same context value.

### 35.2 Phase 2: adapt existing views to binding reads

Replace:

```js
state.portValues[focusPortId(viewId)]
```

with:

```ts
readPortValue(snapshot.state, focusPortId(viewId))
```

The view components need not know whether the value is shared or local.

### 35.3 Phase 3: replace link-group UI data

Port badges should read `bindingForPort` for class name, color, value, and members. Edge menus should still enumerate explicit `edgeIds` so users can unlink one generator.

This resolves the previous ambiguity between a named group and a named edge.

### 35.4 Phase 4: translate gestures into commands

Existing action buttons can dispatch the new command records. Link workflow should select `PortId`, not `ViewId`. Context menus should carry action IDs and command data rather than closures inside durable state.

### 35.5 Phase 5: separate preview state

Draggable tile positions, splitter previews, hover, open menus, and focus rings remain adapter state. Only committed layout changes become durable commands. This restores replayability without making pointer motion sluggish.

### 35.6 Phase 6: preserve visual language

The original monochrome styling, risk colors, SVG nodes, port badges, status bar, and menus can be retained nearly unchanged. The visual designer's work is not the target of the rewrite.

### 35.7 Phase 7: add persistence codecs

Persist:

- views and their kinds;
- placements;
- ports derivable from schema or explicitly versioned;
- link edges;
- binding values keyed by a portable class representation;
- class metadata;
- counters or fresh-ID policy.

Do not persist union-find parent pointers. On load, rebuild the quotient and validate the complete snapshot.

## 36. Production hardening

### 36.1 Generalize port sorts

Move validation, equality, display, and codec behavior into declared sort objects. Avoid one central switch as plugins add sorts.

### 36.2 Separate binding lineage from canonical class ID

Canonical member IDs are excellent for reference semantics but change under every split or merge. Durable user identity may require a lineage entity or event-derived identity. Its semantics must specify which predecessor identity survives a merge.

### 36.3 Add authorization capabilities

UI action availability is not security. `LinkPorts`, domain verdicts, and destructive view operations should require capability evidence validated by an authoritative command handler or server.

### 36.4 Add optimistic concurrency

Commands should carry expected revisions or dependency versions. A stale link target can be rejected or re-evaluated before commit.

### 36.5 Add undo and redo

Because explicit edges and commands are retained, several models are possible:

- inverse commands where well defined;
- event-log branch navigation;
- snapshot restoration;
- compensating commands for external effects.

`UnlinkPorts` is not always the inverse of `LinkPorts` if subsequent edges or values changed. Undo semantics should refer to command history, not assume algebraic invertibility.

### 36.6 Add incremental quotient maintenance

For large workspaces, recompute only the affected old class on edge deletion and merge classes incrementally on addition. Keep a slow complete rebuild in tests.

### 36.7 Add rule-based actions

Replace hand-coded `deriveActions` with reified rules over subject, context, capability, occurrence, and state. Compile them to indexed or incremental plans and retain provenance.

### 36.8 Add workflow effects

Represent select, confirm, issue, await, notify, and cancel as effect syntax. Interpret in React, tests, replay, and remote sessions.

## 37. Limitations of the delivered artifact

The implementation makes a strong core claim but a bounded product claim.

It does **not** include:

- the original recursive split-tree window manager;
- drag and resize behavior;
- durable persistence or migration codecs;
- multiple placements of the same logical view in the demonstration;
- distributed collaboration;
- conflict-free replicated links;
- authentication or authorization;
- undo/redo;
- a general query AST;
- recursive action rules;
- incremental rendering;
- a React adapter in the delivered demonstration;
- mechanized proofs.

These omissions are deliberate. The artifact isolates the kernel failure that made other features unreliable. It provides a reference semantics to which those features can be added.

## 38. Conclusions

The supplied Sentinel prototype demonstrates that a good interface designer can reach the right product concepts before the implementation has a stable mathematical center. Subjects, occurrences, commands, views, placements, ports, links, and workspaces are all present. The difficulty lies in deciding which of those objects owns shared truth.

The original implementation made graph reachability a repeated query, copied values across every reachable endpoint, attached group identity to representative edges, and allowed reducers and subscriptions to depend on global process state. Those choices are locally convenient and globally brittle.

The reimplementation adopts four explicit layers:

1. **Typed local ports** describe component boundaries.
2. **Durable link edges** record user-declared equations and retain editing provenance.
3. **A quotient of the edge graph** defines logical binding classes.
4. **A reconciliation algebra and one binding cell per class** define value behavior.

Commands transform these structures atomically under a whole-state invariant. Interaction requests are serializable. Effects and rendering are interpreted outside the kernel. The result is not merely cleaner code: the representation makes core properties true by construction. Linked ports agree because they read one cell, not because every command remembered to propagate. Unlinking is meaningful because source edges were retained. Merge conflicts are explicit because topology and value choice are distinct. Multiple engines compose because no hook reaches around its provider to a singleton.

The broader architectural lesson is that cross-window interaction is not fundamentally a React state-sharing problem. It is a problem of open-system boundaries, generated equivalence, typed state, transactions, and effectful workflows. Category theory contributes a precise account of boundary identification; lattice theory contributes fixed-point semantics for future recursive facts; lenses contribute laws for local state focus; algebraic effects and coalgebra contribute workflow semantics. None of these replaces careful engineering. Each names a separate obligation that ad hoc callbacks tend to hide.

The delivered artifact establishes a practical base for the next stage. Its quotient compiler, command kernel, invariant checker, and tests are small enough to audit. Its screenshots show that the fraud-analysis experience survives the semantic rewrite. Its limitations are explicit. The kernel can now be optimized, connected to React, extended with persistence and collaboration, or modeled in a proof assistant without changing the meaning of a link.

---

# Appendices

## Appendix A. Implementation file map

| File | Role | Approximate trust level |
|---|---|---|
| `src/model.ts` | types for state, commands, effects, interactions | semantic schema |
| `src/schema.ts` | component kind to port-boundary mapping | trusted declaration |
| `src/fixtures.ts` | example domain and initial workspace | demonstration data |
| `src/graph.ts` | quotient construction, equality, validation | trusted kernel |
| `src/invariants.ts` | complete-state validity | trusted checker |
| `src/kernel.ts` | command transition function | trusted kernel |
| `src/queries.ts` | pure derived observations and actions | application semantics |
| `src/engine.ts` | snapshot/store/workflow/effect shell | runtime boundary |
| `src/ui.ts` | DOM renderer and event translation | adapter |
| `tests/*.test.mjs` | kernel and law tests | executable evidence |
| `scripts/e2e_check.py` | browser assertions | integration evidence |
| `scripts/capture_screenshots.py` | figure production | documentation tooling |

## Appendix B. Command catalogue

| Command | Principal preconditions | State effect |
|---|---|---|
| `WritePort` | endpoint exists, writable, value valid | update one binding cell |
| `LinkPorts` | endpoints compatible and distinct classes | add edge, reconcile, rebuild quotient |
| `UnlinkPorts` | edge exists | remove edge, rebuild quotient, preserve values |
| `RenameBinding` | port and binding exist, nonempty name | update class metadata |
| `SetBindingColor` | valid color, binding exists | update class metadata |
| `ApproveOrder` | order exists, not already approved | change status |
| `DeclineOrder` | order exists, not already declined | change status |
| `EscalateOrder` | order exists, not already escalated | change status |
| `MarkCardCompromised` | card exists, not already flagged | set compromised flag |
| `SwitchWorkspace` | workspace exists and differs | change active workspace |
| `SetViewKind` | view exists; removed ports are unlinked | change schema and topology atomically |
| `ClosePlacement` | placement exists; workspace retains one | remove occurrence; optionally GC view |
| `ExportView` | view exists | emit download effect |

## Appendix C. Complete invariant checklist

1. Active workspace exists.
2. Every placement references an existing workspace.
3. Every placement references an existing view.
4. Workspace area occupancy is unique.
5. Every view is placed at least once.
6. Every view's actual ports equal its schema ports.
7. Every port owner exists.
8. Every edge endpoint exists.
9. Every edge connects equal sorts and protocols.
10. No duplicate undirected endpoint pair exists.
11. Binding members are sorted.
12. Binding IDs are canonical member functions.
13. No binding is empty.
14. Every member port exists.
15. No port appears in two bindings.
16. Binding and member sorts/protocols agree.
17. `portBinding` points back to the containing binding.
18. Binding values validate against all members.
19. Binding edge lists equal graph-internal edges.
20. Binding names are nonempty.
21. Every port appears in some binding.
22. Every port has a valid `portBinding` entry.
23. `portBinding` has no removed-port keys.
24. `portBinding` has no missing-binding targets.
25. Every link's endpoints belong to one quotient class.

## Appendix D. Reproducibility

From the project root:

```bash
bash scripts/build.sh
bash scripts/test.sh
python -m http.server 4173 --directory dist
```

Then open:

```text
http://127.0.0.1:4173/index.html
```

Browser assertions:

```bash
python scripts/e2e_check.py
```

Screenshot generation:

```bash
python scripts/capture_screenshots.py
```

The screenshot script assumes Chromium at `/usr/bin/chromium` and Playwright's Python package. The browser environment used for this report had a managed URL policy that required a temporary local testing exception; that environment-specific step is not part of the source artifact.

## Appendix E. Selected source-to-replacement mapping

| Supplied source | Replacement |
|---|---|
| `sameSubject` | `sameSubject`, `samePortValue` |
| `viewPorts` | `schema.portsForView` |
| `connectedPorts` | `rebuildBindings` + `portBinding` |
| `portValues` | `BindingCell.value` |
| edge `name`/`color` | `BindingCell.meta` |
| implicit source preference | explicit `ReconcilePolicy` |
| `applyCommand` | invariant-gated pure `applyCommand` |
| global `engine` | explicit `KernelEngine` instance |
| callback selection query | serializable `SelectionQuery` |
| view-title link target | exact port target |
| unlogged authoritative preview | future adapter-local preview |
| leaked final placement | view/port/link garbage collection |

## Appendix F. Bibliography

**Baez, John C., and Kenny Courser.** “Structured Cospans.” *Theory and Applications of Categories* 35 (2020): 1771–1822. [Primary paper](https://arxiv.org/abs/1911.04630).

**Foster, J. Nathan, Michael B. Greenwald, Jonathan T. Moore, Benjamin C. Pierce, and Alan Schmitt.** “Combinators for Bidirectional Tree Transformations: A Linguistic Approach to the View-Update Problem.” *ACM Transactions on Programming Languages and Systems* 29, no. 3 (2007). [Author-hosted paper](https://www.cis.upenn.edu/~bcpierce/papers/lenses-toplas-final.pdf).

**Green, Todd J., Grigoris Karvounarakis, and Val Tannen.** “Provenance Semirings.” *Proceedings of PODS 2007*, 31–40. [Author-hosted paper](https://web.cs.ucdavis.edu/~green/papers/pods07.pdf).

**Jackson, Daniel.** “Alloy: A Lightweight Object Modelling Notation.” *ACM Transactions on Software Engineering and Methodology* 11, no. 2 (2002): 256–290. [MIT paper](https://groups.csail.mit.edu/sdg/pubs/2002/alloy-journal.pdf).

**Lamport, Leslie.** “The Temporal Logic of Actions.” *ACM Transactions on Programming Languages and Systems* 16, no. 3 (1994): 872–923. [Author-hosted paper](https://lamport.azurewebsites.net/pubs/lamport-actions.pdf).

**LispWorks.** “Conceptual Overview of CLIM Presentation Types.” *CLIM 2.0 User Guide*, accessed 2026. [Official manual](https://www.lispworks.com/documentation/lw80/clim/clim-ch6-1.htm). Cited as **LispWorks 2021a**.

**LispWorks.** “Using CLIM Presentation Types for Output.” *CLIM 2.0 User Guide*, accessed 2026. [Official manual](https://www.lispworks.com/documentation/lw80/clim/clim-ch6-3.htm). Cited as **LispWorks 2021b**.

**LispWorks.** “Applicability of CLIM Presentation Translators.” *CLIM 2.0 User Guide*, accessed 2026. [Official manual](https://www.lispworks.com/documentation/lw80/clim/clim-ch8-2.htm). Cited as **LispWorks 2021c**.

**LispWorks.** “Conceptual Overview of Output Recording.” *CLIM 2.0 User Guide*, accessed 2026. [Official manual](https://www.lispworks.com/documentation/lw80/clim/clim-ch14-1.htm). Cited as **LispWorks 2021d**.

**McCLIM Project.** *McCLIM User's Manual*, accessed 2026. [Official manual](https://mcclim.common-lisp.dev/static/manual/mcclim.html). Cited as **McCLIM 2026**.

**McSherry, Frank, Derek G. Murray, Rebecca Isaacs, and Michael Isard.** “Differential Dataflow.” *Proceedings of CIDR 2013*. [Conference paper](https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf).

**Plotkin, Gordon D., and Matija Pretnar.** “Handling Algebraic Effects.” *Logical Methods in Computer Science* 9, no. 4:23 (2013). [Primary paper](https://arxiv.org/abs/1312.1399).

**React.** “useSyncExternalStore.” React API Reference, accessed 2026. [Official documentation](https://react.dev/reference/react/useSyncExternalStore). Cited as **React 2026a**.

**React.** “createContext.” React API Reference, accessed 2026. [Official documentation](https://react.dev/reference/react/createContext). Cited as **React 2026b**.

**React.** “Keeping Components Pure.” React Learning Guide, accessed 2026. [Official documentation](https://react.dev/learn/keeping-components-pure). Cited as **React 2026c**.

**React.** “useEffect.” React API Reference, accessed 2026. [Official documentation](https://react.dev/reference/react/useEffect). Cited as **React 2026d**.

**Tarjan, Robert Endre.** “Efficiency of a Good But Not Linear Set Union Algorithm.” *Journal of the ACM* 22, no. 2 (1975): 215–225. [DOI record](https://doi.org/10.1145/321879.321884).

**Tarski, Alfred.** “A Lattice-Theoretical Fixpoint Theorem and Its Applications.” *Pacific Journal of Mathematics* 5, no. 2 (1955): 285–309. [Project Euclid](https://projecteuclid.org/journals/pacific-journal-of-mathematics/volume-5/issue-2/A-lattice-theoretical-fixpoint-theorem-and-its-applications/pjm/1103044538.full).

**Xia, Li-yao, Yannick Zakowski, Paul He, Chung-Kil Hur, Gregory Malecha, Benjamin C. Pierce, and Steve Zdancewic.** “Interaction Trees: Representing Recursive and Impure Programs in Coq.” *Proceedings of the ACM on Programming Languages* 4, POPL Article 51 (2020). [Primary paper](https://arxiv.org/abs/1906.00046).

---

## Closing statement

A polished interface can conceal a weak semantic substrate for a surprisingly long time. The appropriate response is not to burden the designer with more local callbacks. It is to give the interface a kernel whose representations make the desired relationships explicit. In Sentinel, that kernel is the graph of typed ports, the quotient it generates, the single value associated with each quotient class, and the command transaction that changes them under checked invariants.
