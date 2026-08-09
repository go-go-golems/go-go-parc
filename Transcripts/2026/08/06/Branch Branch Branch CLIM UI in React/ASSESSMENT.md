# Assessment of Sentinel Rev 4

## Executive finding

Sentinel Rev 4 has a coherent interaction vocabulary and a strong visual prototype, but its semantic kernel is not yet a dependable substrate for window linking, cross-view focus, or document-style shared selection. The central issue is not the appearance of the UI. It is that several logically distinct structures are represented through mutable conventions rather than enforced state invariants.

The prototype already names many of the right concepts: subjects, occurrences, commands, ports, links, views, placements, workspaces, and an effect boundary. The implementation nonetheless collapses or weakly couples several of them:

- port values are replicated per endpoint instead of stored once per logical binding;
- a link group is inferred repeatedly from edge reachability, while its name and color remain attached to arbitrary edges;
- reducer determinism depends on module-global counters;
- interaction requests contain executable callbacks;
- a React context provider is present, but subscriptions still target a module-global engine;
- component kind changes do not enforce a corresponding port schema;
- closing a placement does not garbage-collect an otherwise unreachable logical view;
- no complete-state invariant gate protects accepted transitions.

The result is a prototype that works along its rehearsed happy path but is difficult to replay, persist, test in isolation, compose with plugins, or extend without semantic drift.

## Source-grounded observations

Line references below refer to [`original/SentinelRev4.jsx`](../original/SentinelRev4.jsx), an unmodified copy of the supplied source.

### 1. Reducer behavior depends on ambient module state

`viewSeq` and `makeViewId` are module-global (`100-104`). `SplitPlacement` calls `makeView` from inside the command reducer (`409-413`). Therefore the same serializable state and the same command need not produce the same result if the ambient counter differs. This blocks reliable replay and makes test isolation order-sensitive.

**Severity:** high.  
**Replacement:** all allocation counters live in `AppState`; accepted commands advance them transactionally.

### 2. A provided engine is not the subscribed engine

The source creates one global engine at line `772`, uses it as the context default, and provides it through `PbuiContext`. Yet `useApp` subscribes directly to the global variable at line `775`, rather than reading the engine from context. A nested provider can change `usePbui()` while `useApp()` continues observing the singleton. This creates a split-brain component: commands can be sent to one engine while rendering subscribes to another.

**Severity:** critical for composition and tests.  
**Replacement:** the rebuilt UI receives one explicit `KernelEngine`; each engine owns a cached immutable snapshot and independent listeners.

### 3. Logical binding values are copied, not represented

`connectedPorts` recomputes a connected component by scanning all links (`305-319`). `writePortValue` then writes the same value into every member's `portValues` entry (`321-325`). This represents one logical fact as many physical copies.

The convention is fragile because coherence depends on every mutation going through the propagating helper. Import, migration, debugging code, partial state restoration, or a future command can create drift. Reads cannot tell which copy is authoritative. A write costs a graph traversal plus a copy proportional to class size.

**Severity:** critical.  
**Replacement:** link edges generate an equivalence relation over ports; each equivalence class has exactly one `BindingCell.value`.

### 4. Link-group identity and metadata are edge-local

`linkGroups` discovers components dynamically and picks the first touching edge as the representative for group name and color (`132-149`). `LinkPorts` stores name and color on the new edge (`355-370`); rename and color commands modify one edge (`381-391`). When two pre-existing groups are merged, or when edges in a component have been renamed independently, there is no canonical group metadata.

Object insertion order can affect which name the UI presents. Removing the representative edge can change a group's displayed identity without changing its connected ports.

**Severity:** high.  
**Replacement:** metadata belongs to the quotient binding class. Edges record only the equations that generated the class.

### 5. Merge conflict resolution is implicit

`LinkPorts` always propagates the source endpoint's current value after adding an edge (`371-372`). This is a product policy hidden inside topology mutation. There is no `require-equal` mode, target preference, conflict object, or user-mediated resolution.

**Severity:** high for document linking.  
**Replacement:** every merge names a reconciliation policy: `prefer-source`, `prefer-target`, or `require-equal`. A conflict rejects the whole candidate transition atomically.

### 6. Port writes are not type- or reference-checked

`WritePort` verifies only that a port exists and then accepts any JavaScript value (`335-337`). An `order-id` port can receive an object; a `subject-ref` port can receive an untyped string or a reference to a missing entity. Rendering code then relies on unchecked assumptions.

**Severity:** critical for kernel safety.  
**Replacement:** port sort and domain referential integrity are validated before any state change.

### 7. View kinds and port schemas can diverge

`SetViewKind` creates missing ports for non-listener views but does not remove ports when changing to `listener` (`393-407`). `SplitPlacement` creates the standard ports even if a caller requests a listener (`409-413`). A view can therefore claim one kind while retaining the boundary of another, and hidden links can continue affecting the rest of the workspace.

**Severity:** high.  
**Replacement:** `schema.ts` is the single source of truth. Kind changes add/remove ports atomically and reject removal of a linked port until it is explicitly unlinked.

### 8. Placement lifetime and logical-view lifetime are conflated incompletely

`ClosePlacement` removes a layout leaf but leaves the logical view, ports, values, and links in the store. Repeated window operations can accumulate unreachable semantic state.

**Severity:** high for long-running workspaces.  
**Replacement:** closing a non-final occurrence preserves the logical view; closing its final placement garbage-collects that view, its ports, incident links, and derived binding cells in one transaction.

### 9. Interaction requests are not data

`selectOne` stores the request in state (`599-607`). The link workflow supplies `query.accepts`, a closure capturing behavior (`1368-1380`), and the presentation wrapper calls that callback during render (`791-792`). The state is not serializable, replayable, comparable, worker-transferable, or statically inspectable.

The workflow also asks the user to choose a **view** and then selects the first compatible port owned by that view (`1381-1384`). This is ambiguous as soon as a view owns more than one compatible port.

**Severity:** high.  
**Replacement:** the transient request is serializable data: `{kind: "compatible-port", sourcePortId}`. The user selects the actual port endpoint.

### 10. Live layout updates bypass the command boundary

During splitter dragging, `setSplitRatioLive` mutates authoritative engine state directly (`589-592`, invoked at `1602`), while only the final ratio is dispatched as a command (`1610`). This is reasonable as a visual preview, but because preview state and durable state are the same object graph, intermediate state changes bypass reducer validation and audit. Replay of the command log cannot reproduce the exact observed state sequence.

**Severity:** medium.  
**Replacement direction:** keep ephemeral layout preview in adapter-local interaction state; commit only one validated layout command.

### 11. Derived graph work is repeated in rendering paths

`connectedPorts` scans all links for each dequeued port. It is called by compatibility checks, link-group construction, writes, hover tracing, and status rendering. Some render paths call it repeatedly for the same endpoint.

For a graph with \(|P|\) ports and \(|E|\) edges, a single component discovery is approximately \(O(|P||E|)\) in the current scan-based form. Repeating it across many mounted badges can dominate interaction latency as the workspace grows.

**Severity:** medium at current fixture size; high at platform scale.  
**Replacement:** construct the quotient once per topology revision and use `portBinding[portId]` for constant-time class lookup.

### 12. No accepted-transition invariant gate exists

The reducer validates individual cases ad hoc but does not check complete-state properties. It can accept a state with missing endpoints, stale values, orphan views, schema-mismatched ports, duplicate link edges, or a link whose endpoints do not map to the same logical binding.

**Severity:** critical.  
**Replacement:** every candidate accepted transition is checked by `validateState`; a failure returns the unchanged previous state and structured issues.

## Positive qualities retained

The critique should not erase what the prototype gets right:

- semantic subjects are separated from rendered labels;
- occurrences are explicit and accessible through keyboard activation;
- commands are mostly serializable records;
- domain effects such as download are separated from the reducer;
- view identity and placement identity are separate concepts;
- link endpoints declare a value type, protocol, and mode;
- selection is represented as a temporary interaction mode;
- the command listener makes semantic operations visible to users;
- the visual language communicates linkage and risk effectively.

The reimplementation keeps those ideas and replaces the unenforced conventions beneath them.

## Replacement kernel in one statement

Let \(P\) be the finite set of typed ports and \(E\) the durable set of equality-link edges. Endpoint maps

\[
s,t:E\rightrightarrows P
\]

generate the least equivalence relation \(\sim_E\) containing \(s(e)\sim_E t(e)\) for every edge \(e\). The runtime computes the quotient

\[
q:P\to P/{\sim_E}.
\]

A binding-value function

\[
v:P/{\sim_E}\to V
\]

stores one well-typed value for each class. Reading a port is composition:

\[
\operatorname{read}(p)=v(q(p)).
\]

Writing a port changes exactly \(v(q(p))\). Linking changes \(E\), recomputes the affected quotient, and applies an explicit value-reconciliation policy. Unlinking removes one generator from \(E\), recomputes connectivity, and copies the old class value to each resulting class. The source graph is retained because a quotient alone does not preserve enough provenance to reverse one user link.

This model is the core implemented in `src/graph.ts`, checked by `src/invariants.ts`, and transacted by `src/kernel.ts`.
