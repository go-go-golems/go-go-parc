---
title: sessionstream — Index of Design Patterns
aliases:
  - sessionstream design pattern index
  - sessionstream pattern index
  - sessionstream glossary
status: active
type: architecture-garden-index
created: 2026-08-15
analyzed: 2026-08-15
analysis_schema: architecture-garden-v1
repository: /home/manuel/code/wesen/go-go-golems/sessionstream
repository_commit: fb6b70d62915874e3d3cb9c0b1557814e638ac68
derived_from: Research/Software Architecture Garden/sessionstream/README.md
tags:
  - architecture-garden
  - sessionstream
  - design-pattern-index
  - event-sourcing
  - projections
  - streaming
  - protobuf
related_notes:
  - "[[Research/Software Architecture Garden/sessionstream/README]]"
  - "[[Research/Software Architecture Garden/sessionstream/Index of Design Patterns - Rationale]]"
  - "[[Research/Software Architecture Garden/README]]"
---

# sessionstream — Index of Design Patterns

This is the back-of-the-book index for the [[Research/Software Architecture Garden/sessionstream/README|sessionstream architecture study]]. It catalogues the design patterns, laws, and vocabulary of the session-scoped, event-driven streaming substrate so a reader can find a concept by name, recall it in one sentence, and jump to the exact place it is established, applied, compared, or owed.

This is a **hybrid index-plus-glossary**: each entry carries a one-sentence definition (the glossary job — *what does this mean?*) and a set of locators (the index job — *where can I read about this?*). It is filed by how a reader is likely to remember a concept, not by how the study happened to phrase it, so it carries many `See` redirects from alternate phrasings to the canonical entry.

## How to read this index

- Each entry is a **heading**, so every `See` and `see also` is a clickable link that lands on that entry.
- A trailing **§n** (or **§n.m**) links into the sessionstream study, e.g. [[Research/Software Architecture Garden/sessionstream/README#4. Snapshots as cuts in the prefix order|§4]]. § is the primary appearance; later §-links are further occurrences. The locator points at the section that *substantively* treats the concept — a passing mention is not indexed (the disappointed-reader test).
- A leading **↳** marks a cross-reference into the wider Garden or a Pattern Zoo, so the reader can tell at a glance whether a pattern is local or travels.
- A trailing bracket, e.g. `[Established]`, `[Candidate ecosystem pattern]`, or `[Open correctness obligation]`, is the Garden's [[Research/Software Architecture Garden/README#Pattern maturity vocabulary|maturity label]] for that pattern, taken from [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity assessment]].
- **`See`** redirects to the canonical entry when the entry itself has no locators (alternate phrasing, synonym, reader-memory handle). **`see also`** links to a *related but distinct* concept the reader should not collapse into one.
- For identity strings, schema versions, budgets, and closed vocabularies, see the [[#Identity strings, schemas, and budgets|notation table]] near the end — the analogue of a symbol table for a codebase that speaks in versioned handles.

The reasoning behind every entry — what kind of evidence grounds it, and what a reader loses if it is omitted — is in [[Research/Software Architecture Garden/sessionstream/Index of Design Patterns - Rationale|the companion rationale]].

---

## A

### Admission registry

*See* [[#Schema registry]]. (The Garden-wide name for the bounded, deterministic registry that binds symbolic names to concrete schemas and rejects conflicts; sessionstream calls it `SchemaRegistry`.)

### Append-only event log and replay

Canonical backend events are durably appended per session and may be folded again to rebuild a view; regrouping a sequential fold may change evaluation strategy but not the result (`fold(S0,xy)=fold(fold(S0,x),y)`). [Established locally] [[Research/Software Architecture Garden/sessionstream/README#1. Session-indexed event words|§1]], [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity]]. ↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 7: Append-Only Events, Pure Reducers, and Observable Idempotence|RAG Pattern 7]]. *see also* [[#Timeline rebuild from event history]], [[#Deterministic replay]], [[#Stable retry identity]].

### Atomic projection progress

An open law: a projector checkpoint at *n* should mean every event through *n* has its promised materialization and no later event is claimed; today event append, entity apply, and cursor advance are separate boundaries, not one transaction. [Open correctness obligation] [[Research/Software Architecture Garden/sessionstream/README#Atomic projection progress|§Atomic projection progress]], [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity]]. *see also* [[#Projection checkpoint]], [[#Append-only event log and replay]], [[#Consistent SQLite snapshot cut]].

## B

### Batch-patch-into-delta

*See* [[#Streaming delta with accumulated state]]. (The reader-memory phrasing: the wire event is a *delta*, but the timeline projection *patches the durable entity with the full accumulated state* each tick — a batch upsert, not a patch log.)

### Bounded asynchronous observer dispatcher

The design that separates a domain observer from its callback delivery: bounded admission, ordered asynchronous delivery, nonblocking producers, explicit drop accounting, panic isolation, admission closure, accepted-work draining, and completion waiting. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/sessionstream/README#Bounded asynchronous observer dispatcher|§Bounded asynchronous observer dispatcher]]. ↳ [[Research/Software Architecture Garden/sessionstream/designs/01 - Bounded Asynchronous Observer Dispatcher|design 01]]. *see also* [[#Observer as diagnostic projection]], [[#Drop accounting]].

## C

### Canonical event, multiple projections

Record one admitted occurrence (the backend event) and derive several purpose-specific views (UI, timeline, audit) from it; the event stream stays authoritative while projections may change. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/sessionstream/README#Candidate ecosystem patterns|§Candidate ecosystem patterns]], [[Research/Software Architecture Garden/sessionstream/README#2. Stateful event algebras|§2]]. ↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 4 — Typed Plans and Multiple Interpreters|RAG Pattern 4 (structural analogy only)]]. *see also* [[#Command, not authority]], [[#UI projection and timeline projection are separate]], [[#Product interpretation of projections]].

### Command, not authority

A command is a serializable typed intent; the command name alone grants no authority — the interpreter checks current authority. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/sessionstream/README#Candidate ecosystem patterns|§Candidate ecosystem patterns]], [[Research/Software Architecture Garden/sessionstream/README#6. Typed sums at trust boundaries|§6]]. ↳ [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook#Pattern 5 — Command as Data|PBUI Pattern 5]]. *see also* [[#Typed intent, host-owned effect]], [[#Admission registry]], [[#Production authorization boundary (external)]].

### Consistent SQLite snapshot cut

An open law: every returned entity should satisfy `lastEventOrdinal(x) ≤ snapshotOrdinal`, but the SQLite store currently reads the cursor and entity rows in separate operations rather than one read transaction. [Open correctness obligation] [[Research/Software Architecture Garden/sessionstream/README#Consistent-cut snapshots|§Consistent-cut snapshots]], [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity]]. *see also* [[#Snapshot cut plus live suffix]], [[#Atomic projection progress]], [[#Temporal materialization]].

### Cross-project comparison

The table mapping sessionstream's invariants to devctl, upwork-tracker, publish-vault, rag-ttc, rag-evaluation-system, go-go-datadrop, and zitadel-go-test, each with a shared invariant and an important difference. [[Research/Software Architecture Garden/sessionstream/README#Cross-project comparison|§Cross-project comparison]]. *see also* [[Research/Software Architecture Garden/sessionstream/README#Candidate ecosystem patterns|§Candidate ecosystem patterns]], [[Research/Software Architecture Garden/sessionstream/README#Correlation with the Pattern Zoos|§Correlation with the Pattern Zoos]].

## D

### Deterministic replay

An open law: for a fixed initial view, session metadata, schema version, and event prefix, rebuild should produce the same timeline materialization; the burden is identifying every input hidden behind either side (clocks, randomness, networks, mutable globals). [Open correctness obligation] [[Research/Software Architecture Garden/sessionstream/README#Deterministic replay|§Deterministic replay]], [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity]]. *see also* [[#Timeline rebuild from event history]], [[#Append-only event log and replay]], [[#Per-session serializability]].

### Drop accounting

The observer-dispatcher law that loss is *reported* (`Server.ObserverDroppedRecords`), never silent; silent loss makes diagnostics useless. [[Research/Software Architecture Garden/sessionstream/README#Bounded asynchronous observer dispatcher|§Bounded asynchronous observer dispatcher]]. *see also* [[#Bounded asynchronous observer dispatcher]], [[#Observer as diagnostic projection]].

## E

### Effect-acknowledged state machines

The model `State × Event → State × Action*` shared by the heartbeat reducer/supervisor and chat startup, with commit-before-concurrency, action-completion events, lifecycle laws, generation isolation, linearization points, and trace inclusion; only heartbeat currently has a pure reducer and serialized supervisor. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/sessionstream/README#Effect-acknowledged state machines and runtime refinement|§Effect-acknowledged state machines]]. ↳ [[Research/Software Architecture Garden/sessionstream/designs/03 - Effect-Acknowledged State Machines and Runtime Refinement|design 03]]. *see also* [[#Heartbeat failure detector kernel]], [[#Streaming work as a labeled transition system]], [[#Verification research, constraining the Go binary]].

## F

### Error store

The optional durable runtime-error/DLQ seam (`ErrorStore.RecordError`) that persists projection, fanout, decode, ordinal, and store errors keyed by session and ordinal, so failures are observable and replayable rather than swallowed. [Established locally] [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity assessment]]. *see also* [[#Open correctness obligations]], [[#Projection error policy]].

### Failure modes, indexing of

The Garden discipline that an index must list the failure modes and open obligations as carefully as the established patterns; an index that lists only successes flatters the system. [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity assessment]]. *see also* [[#Open correctness obligations]], [[#Maturity assessment]].

## H

### Heartbeat failure detector kernel

A pure state machine (`Phase × Event → Phase × Effect*`, no I/O) behind a supervisor that owns timers, writes, and nonce generation; "suspected" is not "dead" — the detector reports what it measured under the configured timing assumption. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/sessionstream/README#Effect-acknowledged state machines and runtime refinement|§Effect-acknowledged state machines]]. ↳ [[Research/Software Architecture Garden/sessionstream/designs/03 - Effect-Acknowledged State Machines and Runtime Refinement|design 03]]. *see also* [[#Effect-acknowledged state machines]], [[#Bounded asynchronous observer dispatcher]]. (Post-anchor hardening: the kernel was added after the study's pinned commit.)

## I

### Identity strings, schemas, and budgets

This is the index's notation table. sessionstream speaks in versioned handles and closed vocabularies; a reader will frequently think "what did `SessionId` mean again?" or "what transport frame is this?" Look it up here, then follow the §-link.

| Handle / schema | Kind | Meaning | Where |
|---|---|---|---|
| `SessionId` | scope key | Indexes one independent routing, ordering, state, cursor, and fanout domain. | [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[#Scope key]] |
| `Command` | intent value | Serializable typed request; not authority and not the effect itself. | [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[#Command, not authority]] |
| `Event` | canonical event | Typed statement admitted to the backend event path under one scope and ordinal; durable replay evidence only when an `EventStore` is configured. | [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[#Canonical event, multiple projections]] |
| `UIProjection`, `TimelineProjection` | projection | Interpretation of canonical input into one view without changing the input's identity. | [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[#UI projection and timeline projection are separate]] |
| `TimelineEntity` | materialized entity | Durable query-oriented state derived from an event prefix. | [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[#Materialized entity]] |
| `Ordinal` | sequence coordinate | Monotone per-scope position used for ordering and freshness. | [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[#Sequence coordinate]] |
| `SnapshotOrdinal` | prefix cut | Declares the greatest event coordinate represented by one coherent snapshot. | [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[#Snapshot cut plus live suffix]] |
| Projection cursor | projection checkpoint | Greatest event prefix successfully interpreted by a named projector. | [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[#Projection checkpoint]] |
| `SchemaRegistry` | admission registry | Binds stable symbolic names to concrete transport and persistence schemas and rejects conflicts. | [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[#Schema registry]] |
| `UIEvent` | live suffix | Ordered observations strictly newer than the snapshot cut. | [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[#Snapshot cut plus live suffix]] |
| WebSocket transport frames | transport schema | Protobuf-JSON frames: `Snapshot`, `SnapshotEntity`, `UiEventFrame`, `PingFrame`, `PongFrame`. | [[Research/Software Architecture Garden/sessionstream/README#6. Typed sums at trust boundaries|§6]], [[#Snapshot cut plus live suffix]] |
| `google.protobuf.Any` | transport payload | The deliberately dynamic payload slot inside the typed envelope; the contract is not statically closed end-to-end. | [[Research/Software Architecture Garden/sessionstream/README#6. Typed sums at trust boundaries|§6]], [[#Typed sums at trust boundaries]] |
| `Session.Metadata` | metadata slot | Typed as `any`; an explicit schema-evolution policy is required. | [[Research/Software Architecture Garden/sessionstream/README#6. Typed sums at trust boundaries|§6]], [[#Typed sums at trust boundaries]] |
| Transport observers | closed vocabulary | Bus/Pipeline/Transport/Error/heartbeat/Systemlab traces share a typed transition-and-trace foundation; Bus/Pipeline/Error were removed with Systemlab. | [[Research/Software Architecture Garden/sessionstream/README#Typed transition systems and trace algebra|§Typed transition systems]], [[#Typed transition systems and trace algebra]] |
| Error kinds | closed vocabulary | `decode | ordinal | ui-projection | timeline-projection | fanout | store`. | [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity assessment]], [[#Error store]] |
| Projection error policies | closed vocabulary | `ProjectionErrorPolicyFail | ProjectionErrorPolicyAdvance` (per-projection: UI and timeline independent). | [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity assessment]], [[#Projection error policy]] |
| Maturity labels | Garden vocabulary | `Established locally | Candidate ecosystem pattern | Open correctness obligation | Intentionally external`. | [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity assessment]], [[#Maturity assessment]] |

---

## M

### Materialized entity

Durable query-oriented state derived from an event prefix (a read model, timeline row, cached view) — *not* a canonical domain object. [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[Research/Software Architecture Garden/sessionstream/README#5. Temporal materialization|§5]]. ↳ [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook#Pattern 11 — Authoritative State, Resolver, and Revision|PBUI Pattern 11]]. *see also* [[#Temporal materialization]], [[#Canonical event, multiple projections]]. *Must not be confused with* the canonical event or the snapshot.

### Maturity assessment

The study's per-pattern table grading each as candidate ecosystem pattern, established locally, open correctness obligation, or intentionally external, with evidence or limitation. [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity assessment]]. *see also* [[#Failure modes, indexing of]], [[#Open correctness obligations]].

## O

### Observer as diagnostic projection

The observer is a diagnostic trace projection with a deliberately weaker bounded/lossy delivery contract — not an authority path; its model/interval evidence and refinement obligations are documented. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/sessionstream/README#Observer as diagnostic projection and refinement boundary|§Observer as diagnostic projection]]. ↳ [[Research/Software Architecture Garden/sessionstream/designs/04 - Observer as Diagnostic Projection and Refinement Boundary|design 04]]. *see also* [[#Bounded asynchronous observer dispatcher]], [[#Drop accounting]].

### Open correctness obligations

The cluster of laws the study names as not-yet-executable: per-session serializability, consistent-cut snapshots, stable retry identity, atomic projection progress, deterministic replay, snapshot-plus-suffix completeness. [Open correctness obligation] [[Research/Software Architecture Garden/sessionstream/README#Laws that should guide hardening|§Laws that should guide hardening]], [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity assessment]]. *see also* [[#Maturity assessment]], [[#Failure modes, indexing of]].

## P

### Per-session serializability

An open law: visible materialization for one session should be observationally equivalent to applying events in ordinal order, but `projectAndApply` runs after releasing the ordinal mutex, so two concurrent publishers can apply out of order. [Open correctness obligation] [[Research/Software Architecture Garden/sessionstream/README#Per-session serializability|§Per-session serializability]], [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity]]. *see also* [[#Sequence coordinate]], [[#Atomic projection progress]], [[#Deterministic replay]].

### Prefix cut

*See* [[#Snapshot cut plus live suffix]].

### Product decomposition and noninterference

Global state decomposes by session: an event for session *a* modifies `S_a` without changing `S_b`; operations from distinct sessions may commute because they act on disjoint components, while events within one session require a declared order — a state-separation law, not by itself an authorization policy. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/sessionstream/README#3. Product decomposition and noninterference|§3]], [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity]]. ↳ [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook#Pattern 10 — Scoped Runtime and Context|PBUI Pattern 10]]. *see also* [[#Scope key]], [[#Per-session serializability]].

### Product interpretation of projections

The compositional law `(p⊗q)(s,e)=(p(s,e),q(s,e))` justifies deriving UI, timeline, audit, metrics, and accessibility views from one canonical event without coupling their representations; it does *not* justify letting one projector perform hidden effects that alter another projector's input. [[Research/Software Architecture Garden/sessionstream/README#Implications for elegant JavaScript APIs|§Implications for elegant JavaScript APIs]]. *see also* [[#Canonical event, multiple projections]], [[#Deterministic replay]].

### Production authorization boundary (external)

Authentication, authorization, origin policy, and rate limiting are deliberately *external* to the framework; the WebSocket documentation requires production wrappers. [Intentionally external] [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity assessment]]. *see also* [[#Command, not authority]], [[#Scope key]].

### Projection checkpoint

The greatest event prefix successfully interpreted by a named projector; not automatically the same as the event-store cursor or the snapshot cut. [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[Research/Software Architecture Garden/sessionstream/README#5. Temporal materialization|§5]]. ↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 7: Append-Only Events, Pure Reducers, and Observable Idempotence|RAG Pattern 7]]. *see also* [[#Atomic projection progress]], [[#Timeline rebuild from event history]]. *Must not be confused with* the snapshot cut.

### Projection error policy

`ProjectionErrorPolicyFail` (default) stops processing on a projection error; `ProjectionErrorPolicyAdvance` advances the cursor even if a projection fails — useful but means a projection can silently skip; UI and timeline are independent. [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity assessment]]. *see also* [[#Atomic projection progress]], [[#Open correctness obligations]].

## R

### Reconnect, snapshot-before-live

*See* [[#Snapshot cut plus live suffix]].

## S

### Schema registry

The bounded, deterministic registry that binds stable symbolic names to concrete transport and persistence schemas (commands, events, UI events, timeline entities), rejects duplicate names and type mismatches, and performs typed decode; assembly is currently process-local. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[Research/Software Architecture Garden/sessionstream/README#6. Typed sums at trust boundaries|§6]]. ↳ [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook#Pattern 9 — Registry and Module Boundary|PBUI Pattern 9]]. *see also* [[#Command, not authority]], [[#Typed sums at trust boundaries]], [[#Schema-vet]].

### Schema-vet

The small trusted admission boundary: a Go analyzer that rejects top-level `google.protobuf.Struct` registrations so contracts stay typed end-to-end across Go, Goja, JSON, persistence, and browser clients. [Established locally] [[Research/Software Architecture Garden/sessionstream/README#6. Typed sums at trust boundaries|§6]], [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity]]. ↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 10 — Large Producers, Small Trusted Validators / Proof-Carrying Artifacts|RAG Pattern 10]]. *see also* [[#Schema registry]], [[#Typed sums at trust boundaries]].

### Scope key

The Garden-wide name for `SessionId`: the index of one independent routing, ordering, state, cursor, and fanout domain. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[Research/Software Architecture Garden/sessionstream/README#3. Product decomposition and noninterference|§3]]. ↳ [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook#Pattern 10 — Scoped Runtime and Context|PBUI Pattern 10]]. *see also* [[#Product decomposition and noninterference]], [[#Per-session serializability]], [[#Production authorization boundary (external)]].

### Sequence coordinate

The Garden-wide name for `Ordinal`: a monotone per-scope position used for ordering and freshness; browser clients must treat `uint64` ordinals as protobuf-JSON strings, not JS `number`. [[Research/Software Architecture Garden/sessionstream/README#Candidate common vocabulary|§Candidate common vocabulary]], [[Research/Software Architecture Garden/sessionstream/README#4. Snapshots as cuts in the prefix order|§4]]. *see also* [[#Snapshot cut plus live suffix]], [[#Per-session serializability]].

### Snapshot cut plus live suffix

The reconnect contract: a snapshot materializes one event prefix (the cut, declared by `SnapshotOrdinal`) and buffered/future `UIEvent` values provide the ordered suffix strictly after that cut; the WebSocket adapter buffers concurrent batches, sends the snapshot, discards batches at or before the cut, flushes later batches in order, then marks the subscription live. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/sessionstream/README#4. Snapshots as cuts in the prefix order|§4]], [[Research/Software Architecture Garden/sessionstream/README#Candidate ecosystem patterns|§Candidate ecosystem patterns]]. ↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 11 — Immutable Release as Synchronization Root|RAG Pattern 11 (analogy)]]. *see also* [[#Snapshot-plus-suffix completeness]], [[#Consistent SQLite snapshot cut]], [[#Temporal materialization]].

### Snapshot-plus-suffix completeness

An open law: for a subscription cut *n*, every delivered live batch must have ordinal greater than *n*, and every accepted live batch after registration must be represented in the snapshot, delivered exactly once in the suffix, or cause an explicit overflow/reconnect outcome. [Open correctness obligation] [[Research/Software Architecture Garden/sessionstream/README#Snapshot-plus-suffix completeness|§Snapshot-plus-suffix completeness]], [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity]]. *see also* [[#Snapshot cut plus live suffix]], [[#Consistent SQLite snapshot cut]].

### Stable retry identity

An open law: duplicate delivery of one logical event should not create another accepted event (`accept(e);accept(e) ≡ accept(e)`); today the store enforces this only when the duplicate retains the same ordinal and payload, so bus messages need a stable event identity. [Open correctness obligation / Emergent] [[Research/Software Architecture Garden/sessionstream/README#Stable retry identity|§Stable retry identity]], [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity]]. *see also* [[#Append-only event log and replay]], [[#Sequence coordinate]].

### Stateful event algebras

The two projectors modeled as transitions over one event: a timeline projector `δ_T:S×E→S` and a UI projector `δ_U:S×E→S×U*`; both read the pre-event `TimelineView`, the timeline projector returns replacement entities, the UI projector returns zero or more `UIEvent` values. [[Research/Software Architecture Garden/sessionstream/README#2. Stateful event algebras|§2]]. *see also* [[#Canonical event, multiple projections]], [[#Product interpretation of projections]].

### Streaming delta with accumulated state

The streaming-event shape where the wire event is a *delta* (an incremental chunk) but also carries the accumulated full state, and the timeline projection *patches the durable entity with the whole accumulated state* each tick (a batch upsert keyed by `(session, kind, id)`, not a patch log); this is what lets a snapshot *be* the batch and deltas resume only *after* it. [[Research/Software Architecture Garden/sessionstream/README#7. Streaming work as a labeled transition system|§7]]. *see also* [[#Snapshot cut plus live suffix]], [[#Streaming work as a labeled transition system]]. (Concrete pattern: the study's §7 is abstract; the delta-carrying-accumulated-state event and batch-upsert projection are realized in `examples/chatdemo`.)

### Streaming work as a labeled transition system

The coalgebraic view of streaming: a command starts an effectful machine whose observations unfold over time, `γ:W→E×W+O`, where `W` is running work and `O` is a terminal outcome; cancellation and terminal-state uniqueness become explicit safety laws. [[Research/Software Architecture Garden/sessionstream/README#7. Streaming work as a labeled transition system|§7]]. *see also* [[#Streaming delta with accumulated state]], [[#Effect-acknowledged state machines]].

## T

### Temporal materialization

The SQLite store keeps current entities and historical entity versions, so entity lookup is indexed by both semantic key and event cut: `entityAt:(Kind,ID,n)→Entity∪{missing}`; `CreatedOrdinal`, `LastEventOrdinal`, tombstones, and `Snapshot(asOf)` give the materialization temporal semantics. [Established locally] [[Research/Software Architecture Garden/sessionstream/README#5. Temporal materialization|§5]], [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity]]. ↳ [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook#Pattern 11 — Authoritative State, Resolver, and Revision|PBUI Pattern 11]]. *see also* [[#Materialized entity]], [[#Snapshot cut plus live suffix]], [[#Consistent SQLite snapshot cut]].

### Timeline rebuild from event history

Retry-from-cursor and from-scratch rebuild re-run the timeline projection from the event log to repair materialized state; rebuild suppresses live fanout. [Established locally] [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity assessment]]. *see also* [[#Append-only event log and replay]], [[#Projection checkpoint]], [[#Deterministic replay]].

### Typed intent, host-owned effect

Commands and verbs are serializable values; current authority is checked by the interpreter, not carried by the command. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/sessionstream/README#Candidate ecosystem patterns|§Candidate ecosystem patterns]]. ↳ [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook#Pattern 5 — Command as Data|PBUI Pattern 5]]. *see also* [[#Command, not authority]], [[#Schema registry]].

### Typed sums at trust boundaries

Commands, events, UI events, entities, and WebSocket frames are finite named alternatives carrying concrete protobuf messages — tagged sums, not arbitrary JSON; the contract is *not* statically closed end-to-end (transport uses `Any`, names remain strings, `Session.Metadata` is `any`), so browser/JS clients need descriptor distribution and an explicit schema-evolution policy. [Established locally] [[Research/Software Architecture Garden/sessionstream/README#6. Typed sums at trust boundaries|§6]]. ↳ [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook#Pattern 8 — Serializable Semantic Contract|PBUI Pattern 8]]. *see also* [[#Schema registry]], [[#Schema-vet]], [[#Command, not authority]].

### Typed transition systems and trace algebra

The common mathematical structure behind canonical events, projections, heartbeat reducers, observers, bounded dispatch, and checks: subsystems as typed transitions, histories as words, projections and checks as folds, observers as trace projections, dispatchers as queue transducers with explicit loss and lifecycle laws — *not* one universal event bus. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/sessionstream/README#Typed transition systems and trace algebra|§Typed transition systems]]. ↳ [[Research/Software Architecture Garden/sessionstream/designs/02 - Typed Transition Systems and Trace Algebra|design 02]]. *see also* [[#Bounded asynchronous observer dispatcher]], [[#Effect-acknowledged state machines]], [[#Observer as diagnostic projection]].

## U

### UI event is not a mounted occurrence

A `UIEvent` is a transport observation, not a mounted visual occurrence with lifecycle identity; the Garden's standing discipline that a UI event is not a mounted occurrence. [[Research/Software Architecture Garden/sessionstream/README#Correlation with the Pattern Zoos|§Correlation with the Pattern Zoos]]. *see also* [[#Canonical event, multiple projections]], [[#Snapshot cut plus live suffix]].

### UI projection and timeline projection are separate

The central separation: a UI projection decides what a connected client should observe *now*; a timeline projection decides what durable materialized state should exist *after* the event; keeping them separate prevents handlers from knowing too much about frontend rendering or persistence. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/sessionstream/README#The architecture in one diagram|§The architecture in one diagram]], [[Research/Software Architecture Garden/sessionstream/README#Maturity assessment|§Maturity]]. *see also* [[#Canonical event, multiple projections]], [[#Materialized entity]], [[#Stateful event algebras]]. *Neither is an alias for the other, and neither is the backend event.*

## V

### Verification research, constraining the Go binary

The refinement boundary program: a proved deterministic kernel, a thin Go concurrency shell, versioned model events checked with a PGo/TraceLink-style constrained TLC validator, Gobra ownership verification, optional Goose/Perennial proofs, Gomela/SPIN protocol exploration, deterministic `testing/synctest` shell tests, and correlated `runtime/trace` diagnostics. [[Research/Software Architecture Garden/sessionstream/README#Verification research: constraining the Go executable|§Verification research: constraining the Go executable]]. ↳ [[Research/Software Architecture Garden/sessionstream/designs/research/02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables|research 02]]. *see also* [[#Verification research, proving the dispatcher]], [[#Effect-acknowledged state machines]].

### Verification research, proving the dispatcher

The formal attack on the observer-dispatcher contract: a TLA+ concurrent model, an Alloy temporal model, mechanized invariant proofs in Coq and Lean 4, and a Go verification scaffold replaying execution traces through an oracle transliterated from the proved kernel, with a 3.3M-execution fuzz campaign and five contract-targeted mutations all caught. [[Research/Software Architecture Garden/sessionstream/README#Verification research: proving the dispatcher|§Verification research: proving the dispatcher]]. ↳ [[Research/Software Architecture Garden/sessionstream/designs/research/01 - Proving the Bounded Asynchronous Observer Dispatcher|research 01]]. *see also* [[#Bounded asynchronous observer dispatcher]], [[#Verification research, constraining the Go binary]].

## W

### Witness/gate separation, sessionstream's analogue

The sessionstream analogue of witness/gate separation is the projection-vs-store split: projections *interpret* (witness) and the store *applies* (gate); the store is the only writer to materialized state, and projections must not mutate the `view` they read. [[Research/Software Architecture Garden/sessionstream/README#2. Stateful event algebras|§2]], [[Research/Software Architecture Garden/sessionstream/README#Laws that should guide hardening|§Laws]]. *see also* [[#Atomic projection progress]], [[#Deterministic replay]].

---

## Cross-reference summary

The concepts above connect to the wider Garden through a small number of load-bearing correspondences. Each is a *correspondence*, not an equivalence: the Garden's discipline is that a registry is not authority, a snapshot is not always an immutable release, and a UI event is not a mounted occurrence.

- **Identity is a deliberate scoped projection, not incidental serialization** — [[#Scope key]], [[#Schema registry]], [[#Typed sums at trust boundaries]]. ↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 1 — Semantic Identity as Explicit Projection|RAG Pattern 1]].
- **Exact experimental coordinates form a finite product** — [[#Scope key]], [[#Sequence coordinate]], [[#Snapshot cut plus live suffix]]. ↳ [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook#Pattern 11 — Authoritative State, Resolver, and Revision|PBUI Pattern 11]] (revisioned materialization).
- **Constraint-first decisions and partial preference** — [[#Schema registry]], [[#Schema-vet]]. ↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 9: Constraint-First Decisions and Partial Preference|RAG Pattern 9]].
- **Run custody retains configuration, inputs, observations, status, and results under one coordinate** — [[#Scope key]], [[#Temporal materialization]]. ↳ [[Research/Software Architecture Garden/rag-ttc/03 - Reproducible Experiment Custody and Semantic Identity|rag-ttc run custody]].
- **Append-only evidence, pure reducers, observable idempotence** — [[#Append-only event log and replay]], [[#Timeline rebuild from event history]], [[#Stable retry identity]]. ↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 7: Append-Only Events, Pure Reducers, and Observable Idempotence|RAG Pattern 7]].
- **Snapshot cut plus live suffix** — [[#Snapshot cut plus live suffix]], [[#Snapshot-plus-suffix completeness]]. ↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 11 — Immutable Release as Synchronization Root|RAG Pattern 11 (analogy, not equivalence)]].

Patterns marked *Candidate ecosystem pattern* ([[#Canonical event, multiple projections]], [[#Command, not authority]], [[#Scope key]], [[#Snapshot cut plus live suffix]], [[#Typed intent, host-owned effect]], [[#Bounded asynchronous observer dispatcher]], [[#Typed transition systems and trace algebra]], [[#Effect-acknowledged state machines]], [[#Observer as diagnostic projection]], [[#Product decomposition and noninterference]]) have structural or single-implementation evidence and remain candidates until an independent implementation confirms them.

## Related documents

- [[Research/Software Architecture Garden/sessionstream/README|sessionstream study]] — the evidence-pinned source this index catalogues.
- [[Research/Software Architecture Garden/sessionstream/Index of Design Patterns - Rationale|Rationale]] — why each term was chosen and why it belongs.
- [[Research/Software Architecture Garden/README|Software Architecture Garden]] — the Garden root and its maturity vocabulary.
