---
title: sessionstream — Index of Design Patterns (Rationale)
aliases:
  - sessionstream index rationale
  - why each sessionstream index term belongs
status: active
type: architecture-garden-index-rationale
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
  - rationale
related_notes:
  - "[[Research/Software Architecture Garden/sessionstream/README]]"
  - "[[Research/Software Architecture Garden/sessionstream/Index of Design Patterns]]"
  - "[[Research/Software Architecture Garden/README]]"
---

# sessionstream — Index of Design Patterns (Rationale)

This document is the companion to the [[Research/Software Architecture Garden/sessionstream/Index of Design Patterns|sessionstream index]]. An index is only as good as its omissions: a back-of-the-book index that lists every noun is useless. So this document states the principles that earned a term an entry, then justifies each entry in the index — what kind of evidence grounds it, and what a reader loses if it is dropped. Read it as the editor's marginalia on the index, not as a second pass through the study.

The index is a deliberate **hybrid**: a glossary (one-sentence *what does this mean?*) folded into an index (locators — *where can I read about this?*), because the task asked for both a short description and links. It follows two disciplines that sharpened the revision. First, the index/glossary/notation separation: the notation table ([[Index of Design Patterns#Identity strings, schemas, and budgets]]) carries the versioned handles and closed vocabularies a reader will look up as "what did `SessionId` mean again?" or "which transport frame is this?", rather than burying them in the alphabetic list. Second, the reader-memory rule — *index according to how readers might remember the knowledge, not how the author happened to phrase it* — which is why the index carries `See` redirects from alternate phrasings ("batch-patch-into-delta" → Streaming delta with accumulated state; "reconnect, snapshot-before-live" → Snapshot cut plus live suffix; "prefix cut" → Snapshot cut plus live suffix) and why every entry is a heading so every `See` and `see also` is a proper clickable anchor.

The evidence and provenance are inherited from the [[Research/Software Architecture Garden/sessionstream/README|sessionstream study]] (commit `fb6b70d6`, branch `main`, analysis date 2026-08-10). Where the study cites a file and line, the index links to the study section that does the citing; this rationale never claims evidence the study did not first pin. One caveat the study itself records: its commit anchor predates later heartbeat-kernel and observer-trace hardening, so two entries ([[Index of Design Patterns#Heartbeat failure detector kernel]] and the post-anchor observer state behind [[Index of Design Patterns#Bounded asynchronous observer dispatcher]]) reflect work the study's pinned snapshot does not yet contain; those entries say so.

## The five principles of selection

A term earned an index entry only if it satisfied one or more of these. The principles are ordered by how much value an entry adds when a reader meets the concept cold.

1. **It distinguishes two things that are easy to conflate.** The Garden's central discipline is anti-flattening: a registry is not authority, a snapshot is not always an immutable release, a UI event is not a mounted occurrence, a command is not an event, a projection checkpoint is not the snapshot cut. The sessionstream study is rich in these distinctions because the substrate is built around them — the UI/timeline/backend-event separation exists to prevent a handler from smuggling frontend or persistence concerns into the canonical record. An entry that prevents a conflation is the most valuable kind, because the conflation is the failure mode the substrate was designed to make impossible.

2. **It is evidence-backed, not prose-backed.** A term names something with concrete interfaces, tests, a recorded limitation, or a design entry in the pinned snapshot, ranked by the Garden's [[Research/Software Architecture Garden/README#Evidence hierarchy|evidence hierarchy]] (runtime code and public interfaces above tests above design docs above git history). Pure intent recorded only in a comment did not earn an entry unless it named a Garden-defined term.

3. **It is transferable or it must travel intact.** A term belongs if it names a *candidate ecosystem pattern* — a structure stable enough to compare across repositories — or if it is a vocabulary term that must be carried unchanged for cross-project comparison to be honest. The candidate common vocabulary (`Scope key`, `Ordinal`, `Prefix cut`, `Projection checkpoint`) is the clearest case: these are local names for relations the wider Garden and the [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo|RAG]] / [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook|PBUI]] Pattern Zoos already recognize, so the index gives them their canonical name and a `↳` link rather than inventing a new one.

4. **It carries an operational consequence.** A term belongs if naming it tells an operator or implementer something about ordering, freshness, failure, or limit — the snapshot cut (what a reconnect is allowed to see), the projection error policy (fail vs advance, and the silent-skip risk), the drop-accounting law (loss must be reported), the per-session serializability obligation (out-of-order apply is a real hazard). These entries make the index useful to someone running or extending the system, not only to a taxonomist.

5. **It is Garden-defined vocabulary.** The maturity labels and the open-correctness-obligation category are the Garden's own language. They belong so the index speaks the same dialect as every other entry in the Garden and can be read alongside them. The study's own "Laws that should guide hardening" section is the Garden's maturity discipline applied to this repository, so the index foregrounds those laws as entries.

## What was deliberately excluded

A good index is defined by what it leaves out. Three classes of thing appear in the study but were not given entries, and the reason matters:

- **The chatdemo's own streaming mechanics** — `TokensDeltaEvent`'s `chunk`/`text` fields, the `chunkText` helper, the 10-byte chunk size, the 20 ms delay. The study treats these as the *example application*, not the substrate's contribution; the durable pattern (a delta event carrying accumulated state plus a whole-state batch upsert in the projection) is indexed as [[Index of Design Patterns#Streaming delta with accumulated state]], but the demo's specific numbers and helpers are implementation detail that a reader can find at the cited file. Indexing them would be a concordance, not an index.
- **Routine composition over upstream Garden projects** — the Goja/JS module, the Systemlab chapters, the Pinocchio/CoinVault consumer notes. These are documented in their own entries (or their own repositories); sessionstream's contribution is the *substrate*, and the index reflects that scope. The Goja implications are indexed only where the study draws a *law* from them (the elegant-JS-API principles), not as a product feature catalog.
- **One-off identifiers with no conceptual weight** — Go field names, config keys, and SQL column names, except where the name *is* the concept (`SessionId`, `Command`, `Event`, `TimelineEntity`, `SchemaRegistry`, the transport frames). These last are included because they are the durable handles a reader will meet in the code and the wire, and because they are identity coordinates, not implementation detail.

The exclusion principle is the Garden's own: one repository establishes local evidence; ecosystem guidance requires comparison. The index indexes what sessionstream *contributes or hardens*, and points outward for what it merely consumes (Pinocchio, CoinVault, the Pattern Zoos).

## Per-term rationale

Entries are alphabetical to match the index, so a reader can move between the two documents in parallel. Each gives a category, the reason it was chosen, and the reason it belongs — what is lost if it is omitted. Categories: **Pattern** (a design pattern with a maturity label), **Law** (a stated invariant), **Vocabulary** (a named object, identity string, or schema), **Failure mode** (a named class of failure), **Debt/Open** (architecture debt or open obligation), **Garden term** (Garden-defined vocabulary).

### Admission registry — Vocabulary
> Index entry: [[Index of Design Patterns#Admission registry]].

**Chosen because** it is the Garden-wide name for what sessionstream calls `SchemaRegistry`; the `See` redirect keeps the Garden's shared vocabulary stable while preserving the local name.

**Belongs because** a reader coming from another Garden entry will search "admission registry" and should land at the canonical entry, not miss it because this study uses a different word.

### Append-only event log and replay — Pattern (established locally)
> Index entry: [[Index of Design Patterns#Append-only event log and replay]].

**Chosen because** the free-monoid + fold-associativity law (`fold(S0,xy)=fold(fold(S0,x),y)`) is the mathematical core the study states first, and it grounds the timeline rebuild path.

**Belongs because** without it, "replay" and "rebuild" read as magic. Drop it and the reader cannot see *why* the event log is append-only: so the fold is regroupable without changing the result.

### Atomic projection progress — Debt/Open
> Index entry: [[Index of Design Patterns#Atomic projection progress]].

**Chosen because** it is the most load-bearing open obligation: event append, entity apply, and cursor advance are separate boundaries today, so a checkpoint at *n* does not yet *prove* every event through *n* is materialized.

**Belongs because** an index that lists only the established projection machinery flatters the system. This entry keeps the gap visible; it is exactly the kind of failure the Garden's "index the open obligations" rule demands.

### Batch-patch-into-delta — Vocabulary
> Index entry: [[Index of Design Patterns#Batch-patch-into-delta]].

**Chosen because** it is the reader-memory phrasing the user asked about; the `See` redirect routes it to the canonical entry. The phrase captures the two coupled ideas (delta event + whole-state batch upsert) that the study's abstract §7 leaves implicit.

**Belongs because** a reader who remembers "the batch-patch-into-delta thing" but not the study's spelling must still land at the right entry; that is the case `See` redirects exist to serve.

### Bounded asynchronous observer dispatcher — Pattern (candidate)
> Index entry: [[Index of Design Patterns#Bounded asynchronous observer dispatcher]].

**Chosen because** it is the only pattern the study elevated to its own design entry with a formal-verification program (TLA+/Alloy/Coq/Lean), and it generalizes beyond sessionstream.

**Belongs because** it carries the drop-accounting and lifecycle laws that make observers safe; drop it and a reader cannot find *why* diagnostics are lossy-but-reported rather than silently lossy.

### Canonical event, multiple projections — Pattern (candidate)
> Index entry: [[Index of Design Patterns#Canonical event, multiple projections]].

**Chosen because** it is the study's central candidate ecosystem pattern: one admitted occurrence, several derived views, the event stream authoritative.

**Belongs because** it is the axis the whole substrate is built around. Without it, the UI/timeline separation and the rebuild path have no organizing principle.

### Command, not authority — Pattern (candidate)
> Index entry: [[Index of Design Patterns#Command, not authority]].

**Chosen because** it is the Garden's anti-flattening discipline applied here: a command is intent, not authority; the name grants nothing. It maps to PBUI Pattern 5.

**Belongs because** it prevents the conflation "the command was accepted, so it was authorized" — the framework deliberately leaves auth external, and this entry keeps that visible.

### Consistent SQLite snapshot cut — Debt/Open
> Index entry: [[Index of Design Patterns#Consistent SQLite snapshot cut]].

**Chosen because** it is a concrete, named open law: `lastEventOrdinal(x) ≤ snapshotOrdinal` must hold, but the cursor and entity reads are not one transaction.

**Belongs because** a reader implementing a concurrent store must know this gap exists; indexing only the happy path would hide a real correctness hazard.

### Cross-project comparison — Vocabulary
> Index entry: [[Index of Design Patterns#Cross-project comparison]].

**Chosen because** the study's cross-project table is the Garden's comparison method in action; the entry routes a reader to it rather than re-summarizing it.

**Belongs because** the index is a node in a Garden-wide glossary; this entry is the signpost to the sibling entries (devctl, upwork, publish-vault, rag-ttc, etc.).

### Deterministic replay — Debt/Open
> Index entry: [[Index of Design Patterns#Deterministic replay]].

**Chosen because** it is the law `rebuild(S0,H)=liveFold(S0,H)`, and the study is explicit that the burden is identifying every hidden input (clocks, randomness, networks, mutable globals).

**Belongs because** it is the obligation that makes "rebuild" trustworthy or not; without it, a reader might assume replay is free, when projectors can break it by reading undeclared state.

### Drop accounting — Law
> Index entry: [[Index of Design Patterns#Drop accounting]].

**Chosen because** it is the single sentence that distinguishes a *safe* lossy observer from a *silent* lossy one: loss is reported (`Server.ObserverDroppedRecords`), never swallowed.

**Belongs because** silent loss is the failure mode that makes diagnostics useless; naming the law keeps the implementer honest.

### Effect-acknowledged state machines — Pattern (candidate)
> Index entry: [[Index of Design Patterns#Effect-acknowledged state machines]].

**Chosen because** it is the shared `State × Event → State × Action*` model behind heartbeat and chat startup, and the study devotes a design entry to refining it.

**Belongs because** it is the bridge from a pure kernel (testable) to the runtime that interprets it (harder); without it, the heartbeat's purity looks like an accident rather than a deliberate refinement boundary.

### Error store — Pattern (established locally)
> Index entry: [[Index of Design Patterns#Error store]].

**Chosen because** it is the durable DLQ seam that makes projection/fanout/decode/ordinal/store errors observable and replayable rather than swallowed.

**Belongs because** without it, the `reportError` calls in the hub read as fire-and-forget; the entry shows they persist when an `ErrorStore` is configured.

### Failure modes, indexing of — Garden term
> Index entry: [[Index of Design Patterns#Failure modes, indexing of]].

**Chosen because** it is the Garden's own meta-rule applied to this index: index the failures and open obligations as carefully as the patterns.

**Belongs because** it is the entry that justifies why this index contains so many `[Open correctness obligation]` entries; it states the discipline rather than letting the debt entries look like accidents.

### Heartbeat failure detector kernel — Pattern (candidate)
> Index entry: [[Index of Design Patterns#Heartbeat failure detector kernel]].

**Chosen because** it is the pure state machine behind the WebSocket heartbeat, and "suspected ≠ dead" is the honest framing the study insists on.

**Belongs because** it is the clearest example of the pure-kernel + supervisor split. Caveat: the kernel was added *after* the study's pinned commit, so this entry reflects newer evidence the study should fold in.

### Materialized entity — Vocabulary
> Index entry: [[Index of Design Patterns#Materialized entity]].

**Chosen because** it is the durable read model derived from an event prefix — the Garden-wide "materialized entity" / "read model" concept, local to sessionstream.

**Belongs because** it must not be confused with the canonical event or the snapshot; the entry keeps the three distinct, which is the substrate's central separation.

### Maturity assessment — Garden term
> Index entry: [[Index of Design Patterns#Maturity assessment]].

**Chosen because** the study's per-pattern maturity table is the Garden's grading discipline applied here; the entry routes to it.

**Belongs because** every pattern entry in the index carries a maturity bracket drawn from it; the entry is the legend that makes those brackets readable.

### Observer as diagnostic projection — Pattern (candidate)
> Index entry: [[Index of Design Patterns#Observer as diagnostic projection]].

**Chosen because** the study is explicit that the observer is a *diagnostic* projection with a deliberately weaker bounded/lossy contract — not an authority path.

**Belongs because** it prevents the conflation "the observer saw it, so it happened"; observers are best-effort, and correctness must not be built on them.

### Open correctness obligations — Debt/Open
> Index entry: [[Index of Design Patterns#Open correctness obligations]].

**Chosen because** the study groups six named laws (per-session serializability, consistent-cut, stable retry identity, atomic progress, deterministic replay, snapshot-plus-suffix completeness) as not-yet-executable.

**Belongs because** it is the umbrella a reader uses to find the whole debt cluster; without it, each open law looks isolated rather than a coordinated hardening program.

### Per-session serializability — Debt/Open
> Index entry: [[Index of Design Patterns#Per-session serializability]].

**Chosen because** it is the most concrete concurrency hazard: `projectAndApply` runs after the ordinal mutex releases, so two publishers can apply out of order.

**Belongs because** it names the exact fix surface (per-session sequencer, transactional compare-and-set, or store-enforced stale-write rejection); an implementer needs this entry.

### Prefix cut — Vocabulary
> Index entry: [[Index of Design Patterns#Prefix cut]].

**Chosen because** "prefix cut" is the Garden-wide name a reader will search; the `See` redirect routes to the canonical Snapshot cut plus live suffix.

**Belongs because** a reader from publish-vault or the RAG zoo will use this term; the redirect makes the index searchable across the Garden's shared vocabulary.

### Product decomposition and noninterference — Pattern (candidate)
> Index entry: [[Index of Design Patterns#Product decomposition and noninterference]].

**Chosen because** it is the state-separation law (`S = ∏ S_s`) that lets distinct sessions commute while within-session events require order; it maps to PBUI Pattern 10.

**Belongs because** it is the foundation under scoping, and the study is careful to note it is a *state-separation* law, not an authorization policy — the entry preserves that distinction.

### Product interpretation of projections — Law
> Index entry: [[Index of Design Patterns#Product interpretation of projections]].

**Chosen because** it is the compositional law `(p⊗q)(s,e)=(p(s,e),q(s,e))` that justifies deriving UI/timeline/audit/metrics from one event, and the study is careful to note it does *not* permit hidden cross-projection effects.

**Belongs because** it is the algebraic statement of "canonical event, multiple projections"; without it, the separation looks like a style choice rather than a lawful decomposition.

### Production authorization boundary (external) — Debt/Open (intentionally external)
> Index entry: [[Index of Design Patterns#Production authorization boundary (external)]].

**Chosen because** the framework deliberately leaves auth, origin policy, and rate limiting to production wrappers; it is *intentionally* external, not an oversight.

**Belongs because** it prevents the conflation "sessionstream authorizes commands"; it does not, and an operator deploying it must know.

### Projection checkpoint — Vocabulary
> Index entry: [[Index of Design Patterns#Projection checkpoint]].

**Chosen because** it is the per-projector progress watermark, distinct from the event-store cursor and the snapshot cut — a three-way distinction the study's vocabulary discipline insists on.

**Belongs because** conflating the three is the failure mode the "must not be confused with" note prevents; the entry keeps them separate.

### Projection error policy — Vocabulary
> Index entry: [[Index of Design Patterns#Projection error policy]].

**Chosen because** `Advance` vs `Fail` is an operational choice with a silent-skip risk, and UI/timeline are independent — a non-obvious surface an implementer must understand.

**Belongs because** without it, a reader might assume all projection errors stop the pipeline; the entry surfaces the `Advance` option and its hazard.

### Reconnect, snapshot-before-live — Vocabulary
> Index entry: [[Index of Design Patterns#Reconnect, snapshot-before-live]].

**Chosen because** it is the reader-memory phrasing for the reconnect contract; the `See` redirect routes to Snapshot cut plus live suffix.

**Belongs because** a reader who remembers "the snapshot-before-live thing" must land at the right entry; the redirect serves exactly that case.

### Schema registry — Pattern (candidate)
> Index entry: [[Index of Design Patterns#Schema registry]].

**Chosen because** `SchemaRegistry` is the local name for the admission registry; it binds names to concrete schemas, rejects conflicts, and does typed decode. It maps to PBUI Pattern 9.

**Belongs because** it is the boundary that makes "registration is data" (Pattern 8 in the study) safe; drop it and typed decode has no home.

### Schema-vet — Pattern (established locally)
> Index entry: [[Index of Design Patterns#Schema-vet]].

**Chosen because** the Go analyzer that rejects top-level `google.protobuf.Struct` is the framework making "contracts stay typed" a *build-time* guarantee, not a convention. It maps to RAG Pattern 10 (small trusted validators).

**Belongs because** it is the only pattern that enforces the typed-sum contract at compile time; without it, the registry is a runtime check that can be bypassed.

### Scope key — Pattern (candidate)
> Index entry: [[Index of Design Patterns#Scope key]].

**Chosen because** it is the Garden-wide canonical name for `SessionId`; the index files the shared concept under its Garden name with a `↳` to PBUI Pattern 10.

**Belongs because** cross-project comparison requires the shared name; if every study invented its own term, the Garden could not compare them.

### Sequence coordinate — Vocabulary
> Index entry: [[Index of Design Patterns#Sequence coordinate]].

**Chosen because** it is the Garden-wide name for `Ordinal`, and it carries the browser-`uint64`-as-string sharp edge the study flags.

**Belongs because** the `uint64` precision rule is an operational consequence a frontend author will hit; burying it would be a disservice.

### Snapshot cut plus live suffix — Pattern (candidate)
> Index entry: [[Index of Design Patterns#Snapshot cut plus live suffix]].

**Chosen because** it is the reconnect contract: a snapshot materializes one prefix (the cut) and the suffix is strictly newer; the WebSocket adapter's buffer/discard/flush mechanics implement it.

**Belongs because** it is the payoff of the whole append/projection/snapshot apparatus — the user-visible reason the substrate exists. Drop it and reconnect reads as magic.

### Snapshot-plus-suffix completeness — Debt/Open
> Index entry: [[Index of Design Patterns#Snapshot-plus-suffix completeness]].

**Chosen because** it is the law that every live batch after a cut *n* must be > *n*, delivered once, or cause an explicit overflow/reconnect.

**Belongs because** it is the contract the hydration buffer implements; naming the law lets a tester know what to check, not just what the buffer happens to do today.

### Stable retry identity — Debt/Open (emergent)
> Index entry: [[Index of Design Patterns#Stable retry identity]].

**Chosen because** `accept(e);accept(e) ≡ accept(e)` is the idempotence law, and the study flags it as only *emergent* — the store enforces it only when the duplicate keeps the same ordinal and payload.

**Belongs because** bus redelivery can produce a fresh ordinal without a stable event ID; without this entry, a reader might assume bus delivery is idempotent when it is not yet.

### Stateful event algebras — Law
> Index entry: [[Index of Design Patterns#Stateful event algebras]].

**Chosen because** the two projectors modeled as `δ_T:S×E→S` and `δ_U:S×E→S×U*` is the mathematical framing the study gives the UI/timeline split.

**Belongs because** it is the algebra behind "canonical event, multiple projections"; without it, the separation reads as two functions rather than two algebras over one signature.

### Streaming delta with accumulated state — Pattern
> Index entry: [[Index of Design Patterns#Streaming delta with accumulated state]].

**Chosen because** it is the concrete pattern the user asked about: the wire event is a delta *and* carries the accumulated full state, and the timeline projection patches the durable entity with the whole state each tick (a batch upsert). The study's §7 is abstract; this entry names the concrete realization.

**Belongs because** it is the pattern that makes snapshot-before-live work for streaming content — the snapshot *is* the batch, and deltas resume only after it. Drop it and the connection between streaming and hydration is invisible.

### Streaming work as a labeled transition system — Law
> Index entry: [[Index of Design Patterns#Streaming work as a labeled transition system]].

**Chosen because** the coalgebraic view `γ:W→E×W+O` is the study's framing of streaming work as an unfolding machine, with cancellation and terminal-state uniqueness as safety laws.

**Belongs because** it distinguishes a durable event stream from a callback/Promise/mutable UI object — a distinction the JS API implications section relies on.

### Temporal materialization — Pattern (established locally)
> Index entry: [[Index of Design Patterns#Temporal materialization]].

**Chosen because** the SQLite store keeps current entities *and* historical versions, so `entityAt:(Kind,ID,n)` is indexed by both semantic key and event cut; `Snapshot(asOf)` gives point-in-time lookup.

**Belongs because** it is the property that makes "as-of" snapshots possible; without it, a reader might assume the store only keeps current state.

### Timeline rebuild from event history — Pattern (established locally)
> Index entry: [[Index of Design Patterns#Timeline rebuild from event history]].

**Chosen because** retry-from-cursor and from-scratch rebuild re-run the timeline projection from the event log to repair materialized state, and rebuild suppresses live fanout.

**Belongs because** it is the recovery path that makes a projection bug non-fatal; drop it and the store looks immutable when it is rebuildable.

### Typed intent, host-owned effect — Pattern (candidate)
> Index entry: [[Index of Design Patterns#Typed intent, host-owned effect]].

**Chosen because** it is the candidate ecosystem pattern name the study proposes for "commands are data; the interpreter checks authority."

**Belongs because** it is the Garden-wide phrasing that should travel across projects; filing it under the canonical name keeps the vocabulary stable.

### Typed sums at trust boundaries — Pattern (established locally)
> Index entry: [[Index of Design Patterns#Typed sums at trust boundaries]].

**Chosen because** commands/events/UI-events/entities/frames are finite named alternatives carrying concrete protobuf messages — tagged sums, not arbitrary JSON — and the study is careful to flag that the contract is *not* statically closed end-to-end (`Any`, string names, `any` metadata).

**Belongs because** the open-closing caveat is exactly the kind of limit an index must keep visible; without it, a reader might assume end-to-end static typing when the wire is deliberately dynamic at the payload slot.

### Typed transition systems and trace algebra — Pattern (candidate)
> Index entry: [[Index of Design Patterns#Typed transition systems and trace algebra]].

**Chosen because** it is the common math behind events, projections, heartbeat reducers, observers, and dispatch — and the study is explicit it should *not* become one universal event bus.

**Belongs because** it prevents the conflation "everything is an event on one bus"; the entry keeps the typed-transition family distinct from a unified bus, which the study argues against.

### UI event is not a mounted occurrence — Law
> Index entry: [[Index of Design Patterns#UI event is not a mounted occurrence]].

**Chosen because** it is the Garden's standing discipline stated against this substrate: a `UIEvent` is a transport observation, not a mounted visual occurrence with lifecycle identity.

**Belongs because** it prevents the conflation "the UI event is the widget"; the framework separates transport observations from mounted occurrences, and the entry keeps that visible.

### UI projection and timeline projection are separate — Pattern (candidate)
> Index entry: [[Index of Design Patterns#UI projection and timeline projection are separate]].

**Chosen because** it is the study's central separation: UI projection decides what a connected client sees *now*; timeline projection decides what durable state exists *after*; neither is the backend event.

**Belongs because** it is the axis the whole substrate is built around; without it, "why not just return UI state from the handler?" has no answer.

### Verification research, constraining the Go binary — Vocabulary
> Index entry: [[Index of Design Patterns#Verification research, constraining the Go binary]].

**Chosen because** it is the refinement-boundary program (proved kernel → thin Go shell → synctest → runtime/trace) that takes the dispatcher proof to a constrained executable.

**Belongs because** it is the path from formal proof to running binary; without it, the Coq/Lean work looks detached from the shipped code.

### Verification research, proving the dispatcher — Vocabulary
> Index entry: [[Index of Design Patterns#Verification research, proving the dispatcher]].

**Chosen because** it is the formal attack on the observer-dispatcher contract (TLA+/Alloy/Coq/Lean + a 3.3M-execution fuzz campaign catching all five mutations).

**Belongs because** it is the evidence that the dispatcher's drop/lifecycle laws are not just stated but proved; drop it and the dispatcher reads as asserted, not verified.

### Witness/gate separation, sessionstream's analogue — Law
> Index entry: [[Index of Design Patterns#Witness/gate separation, sessionstream's analogue]].

**Chosen because** the study's projection-vs-store split is the local instance of the Garden-wide witness/gate discipline: projections *interpret* (witness), the store *applies* (gate), and the store is the only writer to materialized state.

**Belongs because** it connects the substrate to a Garden-wide relation without flattening them; the entry notes it is an *analogue*, preserving the local distinction.

## PR #15 persistence-pattern addendum (2026-08-18)

The MySQL hydration and AsyncEventStore review added four focused designs after this rationale’s original pinned study. They do not replace the earlier open obligations; they turn four obligations into teachable candidate patterns with concrete counterexamples and proposed enforcement shapes.

### Admission and shutdown share one linearization boundary — Pattern (candidate/open)
> Index entry: [[Index of Design Patterns#Admission and shutdown share one linearization boundary]].

**Chosen because** PR #15 supplied both safety counterexamples (FIFO bypass and send-after-close) and an unpublished liveness counterexample (the rotating `notFull` lost wake). The reusable idea is broader than that file: lossless bounded admission and lifecycle transition must be one concurrent object.

**Belongs because** the existing bounded observer dispatcher has a superficially similar channel shape but a deliberately lossy contract. The new entry prevents reuse-by-shape: diagnostic `TrySubmit` and durable backpressure are not the same pattern.

### Volatile admission is not durable append — Pattern (candidate/open)
> Index entry: [[Index of Design Patterns#Volatile admission is not durable append]].

**Chosen because** the async decorator returns at in-memory admission while `Hub.projectAndApply` proceeds to durable materialization and checkpoint writes. This exposes the difference between accepted, durable, materialized, and checkpointed histories.

**Belongs because** atomic projection progress was already indexed as an obligation, but the acceptance/durability distinction supplies the missing API and custody vocabulary. The `Durable prefix before projection progress` redirect files the law under the phrase a reader is likely to remember.

### Storage equality is a domain identity contract — Pattern (candidate/open)
> Index entry: [[Index of Design Patterns#Storage equality is a domain identity contract]].

**Chosen because** `utf8mb4_unicode_ci` makes exact Go/SQLite session, entity, kind, event, and projector keys case/accent-insensitive in MySQL. The same failure appeared in Pinocchio’s turn-store adapter, providing a second concrete occurrence in the same migration stack.

**Belongs because** product decomposition and noninterference depend on storage preserving the scope-key equivalence relation. A session scope is not isolated when the primary key silently aliases another spelling. The `Collation is identity semantics` redirect prevents readers from filing this as mere database tuning.

### Snapshot ordinals require a transactional read cut — Pattern (candidate/open)
> Index entry: [[Index of Design Patterns#Snapshot ordinals require a transactional read cut]].

**Chosen because** the earlier study named a consistent SQLite cut as open; PR #15 copied the cursor-then-rows shape into a multi-connection MySQL pool, making the concrete interleaving easier to exhibit. The note separates database-cut coherence from the independently established WebSocket snapshot-before-live fence.

**Belongs because** the pair `(SnapshotOrdinal, Entities)` is one versioned value. Without the entry, readers can find the transport fence and mistakenly infer that it repairs database rows from a later commit. The `Transactional read cut` redirect provides the conventional database term.

## Reader-situation usability test

The test the index guide recommends: invent realistic reader situations and trace each to the entry that serves it. The situations that needed a `See` redirect are exactly the ones where a reader remembers the *idea* but not the study's spelling — which is the case the redirects exist to serve.

1. *"There was a pattern where the wire event is a delta but the durable state is patched with the whole accumulated text each tick."* → [[Index of Design Patterns#Batch-patch-into-delta]] → [[Index of Design Patterns#Streaming delta with accumulated state]] → §7 (and the cited `examples/chatdemo`).
2. *"What was the reconnect rule — snapshot first, then live?"* → [[Index of Design Patterns#Reconnect, snapshot-before-live]] → [[Index of Design Patterns#Snapshot cut plus live suffix]] → §4.
3. *"The study kept saying a command isn't authority — where was that?"* → [[Index of Design Patterns#Command, not authority]] → §6, §Candidate ecosystem patterns.
4. *"What did they call the per-session ordering number, and why must the browser treat it as a string?"* → [[Index of Design Patterns#Sequence coordinate]] → §Candidate common vocabulary, §4.
5. *"There was an open law about the SQLite snapshot reading cursor and entities separately."* → [[Index of Design Patterns#Consistent SQLite snapshot cut]] → §Consistent-cut snapshots.
6. *"Where did they list the six laws that aren't executable yet?"* → [[Index of Design Patterns#Open correctness obligations]] → §Laws that should guide hardening.
7. *"The heartbeat is a pure state machine plus a supervisor — where?"* → [[Index of Design Patterns#Heartbeat failure detector kernel]] → §Effect-acknowledged state machines. (Note: post-anchor.)
8. *"Why is the observer lossy but still safe?"* → [[Index of Design Patterns#Drop accounting]] → [[Index of Design Patterns#Bounded asynchronous observer dispatcher]] → §Bounded asynchronous observer dispatcher.
9. *"What's the local name for the Garden's 'scope key' concept?"* → [[Index of Design Patterns#Scope key]] → §Candidate common vocabulary, §3.
10. *"They proved the observer dispatcher in Coq and Lean — where?"* → [[Index of Design Patterns#Verification research, proving the dispatcher]] → §Verification research: proving the dispatcher.
11. *"Why are UI events and timeline entities separate, and why is neither the backend event?"* → [[Index of Design Patterns#UI projection and timeline projection are separate]] → §The architecture in one diagram, §2.
12. *"What rejects `google.protobuf.Struct` at the top level?"* → [[Index of Design Patterns#Schema-vet]] → §6, §Maturity assessment.
13. *"Is bus redelivery idempotent yet?"* → [[Index of Design Patterns#Stable retry identity]] → §Stable retry identity (emergent, not complete).
14. *"What's the algebra that justifies deriving UI, timeline, and audit from one event?"* → [[Index of Design Patterns#Product interpretation of projections]] → §Implications for elegant JavaScript APIs.
15. *"The contract isn't statically closed end-to-end — where did they say that?"* → [[Index of Design Patterns#Typed sums at trust boundaries]] → §6.
16. *"Where is the table comparing sessionstream to devctl, upwork, publish-vault, etc.?"* → [[Index of Design Patterns#Cross-project comparison]] → §Cross-project comparison.
17. *"What does `SnapshotOrdinal` actually promise?"* → [[Index of Design Patterns#Snapshot cut plus live suffix]] → §4.
18. *"Is auth in the framework?"* → [[Index of Design Patterns#Production authorization boundary (external)]] → §Maturity assessment (intentionally external).
19. *"What's the Garden name for the per-projector progress cursor, and why isn't it the snapshot cut?"* → [[Index of Design Patterns#Projection checkpoint]] → §Candidate common vocabulary.
20. *"They kept saying a UI event isn't a mounted occurrence — where?"* → [[Index of Design Patterns#UI event is not a mounted occurrence]] → §Correlation with the Pattern Zoos.

## Related documents

- [[Research/Software Architecture Garden/sessionstream/Index of Design Patterns|sessionstream index]] — the index this rationale explains.
- [[Research/Software Architecture Garden/sessionstream/README|sessionstream study]] — the evidence-pinned source.
- [[Research/Software Architecture Garden/README|Software Architecture Garden]] — the Garden root, its maturity vocabulary, and its evidence hierarchy.
- [[Research/Software Architecture Garden/coinvault/Index of Design Patterns|CoinVault index]] — the worked example this index is calibrated against.
