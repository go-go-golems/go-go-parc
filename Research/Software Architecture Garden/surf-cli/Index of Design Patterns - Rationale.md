---
title: "surf-cli — Index of Design Patterns - Rationale"
aliases:
  - surf design pattern index rationale
  - surf index rationale
status: active
type: architecture-garden-index-rationale
created: 2026-08-16
analyzed: 2026-08-16
analysis_schema: architecture-garden-v1
repository: /home/manuel/workspaces/2026-08-07/add-3d-model-verbs/surf-cli
repository_commit: 89aadf5
derived_from: Research/Software Architecture Garden/surf-cli/README.md
tags:
  - architecture-garden
  - surf
  - design-pattern-index
  - rationale
related_notes:
  - "[[Research/Software Architecture Garden/surf-cli/Index of Design Patterns]]"
  - "[[Research/Software Architecture Garden/surf-cli/README]]"
  - "[[Research/Software Architecture Garden/README]]"
---

# surf-cli — Index of Design Patterns - Rationale

This is the editor's marginalia for the [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns|surf-cli index]]. It records, for every entry, *why that term was chosen* and *what a reader loses if it is omitted* — the conflation it prevents, the operational consequence it carries, or the open obligation it keeps visible. It is the reasoning an index cannot carry itself.

The index is filed by how a reader remembers the knowledge, not by how the study happened to phrase it; this rationale explains the filing decisions, the redirects, and the omissions.

## The five principles of selection

1. **Index the law before the mechanism.** surf's load-bearing decisions are invariants (authority flows from being browser-launched; one writer is one linearization point; disconnect is a cascade, not a silent failure), not file names. The canonical entries name the law; the mechanism (the framing, the socket, the router) lives in the notation table or in `see also`. A reader who remembers "the host can't start itself" must land on the law, not on `installer/native_host.go`.

2. **Preserve the five fundamentals as first-class entries, then go deep on the flagship.** The study is organized as Patterns A–E, so the index gives each its own entry and routes the flagship (B) into its own deep-treatment locators. The overview and the deep entry are *different locators for the same pattern*, and the index says so rather than collapsing them.

3. **File by the verb a reader remembers.** "JavaScript behind a tooling facade" is the study's Pattern C heading, but a reader often remembers the *action* — "running JS behind a facade" — so `JavaScript behind a tooling facade` is a `See` redirect to [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Tool facade|Tool facade]], which is filed under the noun a reader searches. The same logic produces `Auth is not surf's job` and `Surf is not a daemon`.

4. **Index the failure modes and open obligations as carefully as the patterns.** An index that lists only successes flatters the system. surf's most operationally surprising behavior (extension reload kills in-flight work), its security scope (the socket is not a trust boundary), its real bug (JSON number precision loss), and its acknowledged gaps (Windows transport; unknown-id drops; no pending TTL) all get entries, because a reader will search for them and must find the honest treatment.

5. **Use `See` redirects for every plausible alternate phrasing, especially the ones that refute a tempting wrong design.** The redirects are the strongest signal that the index was *designed*: "Surf is not a daemon", "Browser owns the host", "The host cannot start itself" all route to the law that refutes the user-started-daemon alternative. A reader who remembers the *refutation* lands on the *rule*.

## What was deliberately excluded

- **Routine composition over upstream projects.** surf depends on `glazed` (the command/CLI framework) and the browser extension. The extension's own message-handling contract and `glazed`'s dual-mode builder are *not* indexed here — they belong to their own studies. surf's use of them is noted where it shapes a pattern (dual-mode commands), but the index does not reproduce their internals.
- **Per-site extractor logic.** The ~60 embedded site scripts (kagi, chatgpt, upwork, …) are surf's payload, not its architecture. The facade *pattern* is indexed; the individual extractors are not. Indexing them would turn an index into a directory.
- **The full tool list.** The ~103-arm tool router is indexed as the facade; the individual tool names are not enumerated as entries. The closed vocabularies that *gate* tools (`providerPrefixes`, `deferredTools`) go in the notation table because they are the enumerated sets a reader must reason about, not a list to scan.
- **Every occurrence of a noun.** "Socket", "browser", "frame" appear throughout the study; they are indexed only where the study *substantively* treats the concept (the socket-as-not-trust-boundary entry, the native-framing entry), applying the disappointed-reader test. A passing mention is not a locator.
- **A concordance of the diagram.** The architecture diagram is evidence, not a section to point at; no entry's locator is "see the diagram". The locators point at prose that teaches.
- **Re-explanation.** Every entry's definition is one sentence. Where this rationale was tempted to explain further, it was writing a second study, not an index — and was cut.

## Per-term rationale

> Each section links back to its index entry. Maturity labels are the study's, from [[Research/Software Architecture Garden/surf-cli/README#Maturity assessment|the maturity table]].

### Authority flows from being browser-launched — Law

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Authority flows from being browser-launched]].

**Chosen because** the law is stated before any mechanism in the deep entry, and it is the half of the broker pattern a user-started-daemon design gets wrong. **Belongs because** omitting it lets a reader file the broker as "a server with a socket" and miss that the *direction of the spawn* is the authority — the conflation that the whole pattern exists to prevent.

### Browser-Launched Host Broker — Pattern (established)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Browser-Launched Host Broker]].

**Chosen because** it is the study's flagship and the strongest cross-project candidate, with concrete evidence (manifest installer, framing codec, two-loop host) and a deep entry. **Belongs because** it is the one pattern a reader most needs when asking "how do I script a browser from a CLI", and the one most likely to be mis-implemented as a user-started daemon if the direction-of-authority law is lost.

### Cascade disconnect — Pattern (established)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Cascade disconnect]].

**Chosen because** the disconnect propagation is a distinct safety property with its own math (§6.4), separate from the broker's existence. **Belongs because** without it a reader might assume a disconnect is handled ad hoc and miss that it is a *never-block-forever* invariant the host implements deliberately.

### CLI client / host broker split — Pattern (established)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#CLI client / host broker split]].

**Chosen because** Pattern A is the defining decision of the project and is cleanly separable from B. **Belongs because** it is the prerequisite that makes the CLI disposable and the host persistent; collapsing A into B would hide *why* the host needs a socket at all.

### Declarative intent over a serialized effect channel — Pattern (established)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Declarative intent over a serialized effect channel]].

**Chosen because** Pattern E is the glue that makes A and C composable across process boundaries, and the study gives it its own law. **Belongs because** it is the answer to "why can concurrent CLIs share one browser safely", a question a reader will bring to the study; without it the serialization looks incidental rather than load-bearing.

### Disconnect is a graceful cascade, not a silent failure — Pattern (candidate ecosystem)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Disconnect is a graceful cascade, not a silent failure]].

**Chosen because** the deep entry elevates this to a candidate ecosystem rule, not just a mechanism. **Belongs because** it is the *guidance* a reader would extract for a new project, distinct from the mechanism ([[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Cascade disconnect|Cascade disconnect]]) that implements it here.

### Dual-mode commands (Markdown / rows toggle) — Pattern (established)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Dual-mode commands (Markdown / rows toggle)]].

**Chosen because** the toggle is a concrete, repeated shape (~73 wirings) inside Pattern C, not the facade itself. **Belongs because** a reader who remembers "the command that prints Markdown by default and rows with a flag" needs a distinct entry from the facade that *hosts* the scripts.

### Effect channel — Pattern (established)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Effect channel]].

**Chosen because** "effect channel" is the deep entry's own vocabulary for the single write path, and it is the noun a reader will reuse. **Belongs because** it is the bridge between the Pattern E law ([[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Declarative intent over a serialized effect channel|Declarative intent…]]) and the math ([[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#One writer is one linearization point|One writer…]]); omitting it leaves the law and the proof unconnected.

### Escape hatch — Pattern (established)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Escape hatch]].

**Chosen because** the raw `js` surface is an *intentional, documented* part of the design, and surf-distinctive: the Garden's other escape hatches (go-go-goja) are debt, not intent. **Belongs because** without it a reader might assume the facade is closed and propose "add a tool for everything", missing that the escape hatch is the design's release valve.

### Extension reload kills in-flight work — Failure mode

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Extension reload kills in-flight work]].

**Chosen because** it is the most operationally surprising behavior and the one most likely to be filed as a bug. **Belongs because** an index that hides it would flatter the system; a reader who hits a reload mid-export must find that it is *correct and terminal*, not a defect to "fix" by making the host outlive the browser.

### The host cannot start itself — Pattern (established)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#The host cannot start itself]].

**Chosen because** it is a direct corollary of the authority law and a frequent source of user confusion ("why doesn't `surf` just start the host?"). **Belongs because** the corollary is what a reader hits in practice; stating it as its own entry saves a reader from re-deriving the law to answer a usability question.

### Identity rewrite at the boundary — Pattern (established)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Identity rewrite at the boundary]].

**Chosen because** the id bijection is a distinct mechanism with its own math (§6.3), separate from serialization. **Belongs because** it answers "how do N clients share one stream without leaking identity", and without it a reader might assume the host passes client ids straight through.

### Implicit authority — Pattern (established)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Implicit authority]].

**Chosen because** Pattern D is arguably the reason surf exists, and "implicit authority" names the law rather than the mechanism (cookie checks, readiness probes). **Belongs because** omitting it lets a reader propose "let surf log in", re-importing the browser's hardest problems; the entry is the refutation.

### JSON number precision loss — Failure mode

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#JSON number precision loss]].

**Chosen because** it is a real, documented bug (issue #5) with a non-obvious fix (`UseNumber`), and a project-wide hazard. **Belongs because** any new code crossing the JSON boundary must respect it; indexing the failure keeps the hazard visible where a "numbers" entry in a glossary would not.

### Native framing — Pattern (established)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Native framing]].

**Chosen because** the 4-byte LE length-prefix contract is the entire byte-level agreement between host and extension, and the 16 MiB cap is a security boundary. **Belongs because** it is the notation a reader needs before reading any of the host's I/O code; it is the symbol-table entry for the protocol.

### Native-messaging host — Vocabulary

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Native-messaging host]].

**Chosen because** "native-messaging host" is the browser-defined role surf inhabits, distinct from the *broker* surf adds on top. **Belongs because** the distinction (host ≠ broker) is exactly the anti-flattening the Garden wants: a host that serves one in-process client is not a broker.

### One writer is one linearization point — Law

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#One writer is one linearization point]].

**Chosen because** the linearization math (§6.2) is the proof behind the effect channel, and the conclusion is more memorable than the name. **Belongs because** it states what the law *does and does not* prove (dispatch, not execution), the negative space that prevents a reader over-claiming ordering guarantees.

### Owned-tab retry with an idempotency boundary — Pattern (candidate ecosystem)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Owned-tab retry with an idempotency boundary]].

**Chosen because** the transferable idea is the *documented idempotency boundary* on the retry helper, not the retry itself. **Belongs because** a reader who remembers "the retry that's only safe for reads" must find that the boundary is a contract, not an implementation detail; without the entry, the boundary is buried in a helper.

### Pure error classification at the effect boundary — Pattern (established)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Pure error classification at the effect boundary]].

**Chosen because** the "error iff `error` present and all else nil" rule is a distinct structural contract, with a recorded bug that motivated it. **Belongs because** it prevents a reader from treating an `error` field inside a successful payload as a failure, and keeps the extension-internal-key stripping ([[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Extension-internal bookkeeping keys|Extension-internal bookkeeping keys]]) visible as part of the same contract.

### Readiness fence (stable-for window) — Pattern (emergent)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Readiness fence (stable-for window)]].

**Chosen because** the stability-over-time property is distinct from "wait for readyState", and the study labels it emergent. **Belongs because** it is the answer to "how does surf know a page is really loaded and logged in", and the entry keeps the wall-clock-vs-event negative space visible.

### Socket is not a trust boundary — Open obligation

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Socket is not a trust boundary]].

**Chosen because** it is a deliberate scope (single-user workstation), not a bug, and an adopter must state it. **Belongs because** an index that omits it would let a reader deploy the broker on a shared host in good faith; the entry is the obligation that keeps the scope honest.

### Tab targeting (preferred-order, absence-as-sentinel) — Pattern (emergent)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Tab targeting (preferred-order, absence-as-sentinel)]].

**Chosen because** the `-1`-as-absent convention and the three-location resolution are an emergent contract, not a typed one. **Belongs because** it documents a sharp edge (0 is a valid tab id) that a future change could break silently; the entry keeps the convention visible where a type would have made it unnecessary.

### Tool facade — Pattern (established)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Tool facade]].

**Chosen because** Pattern C's reusable idea is the facade (closed verbs + embedded scripts + escape hatch), and "tool facade" is the noun a reader searches. **Belongs because** it is the parent of [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Dual-mode commands (Markdown / rows toggle)|Dual-mode commands]] and [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Escape hatch|Escape hatch]], and the entry that hosts the `see also` to both; without it those two float.

### Versioned capture envelope — Pattern (candidate ecosystem)

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Versioned capture envelope]].

**Chosen because** the `marketplace-capture/v1` envelope is a shared-lineage structure (Upwork Tracker) and a candidate, not just a local helper. **Belongs because** it connects surf to the Garden's existing capture-boundary vocabulary; omitting it would leave the cross-project correspondence untraceable.

### Windows named-pipe transport (not implemented) — Open obligation

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Windows named-pipe transport (not implemented)]].

**Chosen because** it is an acknowledged gap, not a hidden one, and the study states it explicitly. **Belongs because** an index that hides acknowledged gaps flatters the system; a Windows adopter must find that the client transport is a stub before relying on it.

### Extension-internal bookkeeping keys — Vocabulary

> Index entry: [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Extension-internal bookkeeping keys]].

**Chosen because** `_resolvedTabId`/`_hint` are a closed vocabulary the extension appends and the host must strip, and they have a recorded bug history. **Belongs because** it is the notation-table row a reader needs when reading the error-classification code; burying it in the alphabetic list would make it unfindable.

## Reader-situation test

Twenty realistic situations a reader might bring to the index, each traced to the entry that serves it. The situations that needed a `See` redirect are exactly the ones where a reader remembers the *idea* but not the study's spelling.

1. *"There was a pattern where the browser starts the host, not the other way around."* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Browser owns the host]] → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Browser-Launched Host Broker]] → Pattern B.
2. *"Why doesn't `surf` just start the host for me?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Surf is not a daemon]] → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#The host cannot start itself]] → §9.6.
3. *"My bulk export died when I reloaded the extension — is that a bug?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Extension reload kills in-flight work]] → §9.1.
4. *"How do several CLIs share one browser without corrupting it?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Declarative intent over a serialized effect channel]] → Pattern E; *see also* [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#One writer is one linearization point]] → §6.2.
5. *"How does the host know which reply goes to which client?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Identity rewrite at the boundary]] → §4.4, §6.3.
6. *"The tab id came back as scientific notation and got rejected — what happened?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Numbers are not safe across JSON]] → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#JSON number precision loss]] → Pattern E.
7. *"Is the socket safe to expose on a shared machine?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Socket is not a trust boundary]] → §9.2, §13.
8. *"Surf never asks me to log in — how does auth work?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Auth is not surf's job]] → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Implicit authority]] → Pattern D.
9. *"Can I just run arbitrary JS in the page?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Escape hatch]] → Pattern C.
10. *"Is that raw JS surface sandboxed?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Escape hatch is not a sandbox]] → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Escape hatch]].
11. *"The command prints Markdown by default and rows with a flag — what's that called?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Dual-mode commands (Markdown / rows toggle)]] → Pattern C.
12. *"How does surf turn a tool name into something the browser understands?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Tool facade]] → Pattern C.
13. *"Does the facade type-check my args?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#The facade is not a type system]] → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Tool facade]].
14. *"What's the byte format on the native channel?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Native framing]] → §4.1.
15. *"What does `surf.browser.host` mean?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Native-messaging host]] → §3; *see notation table*.
16. *"What happens to in-flight requests when the extension disconnects?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Cascade disconnect]] → §5, §6.4.
17. *"Is disconnect handled silently or loudly?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Disconnect is a graceful cascade, not a silent failure]] → §12.
18. *"The retry helper said it's only safe for reads — why?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Owned-tab retry with an idempotency boundary]] → overview §Open questions.
19. *"Does surf work on Windows?"* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Windows named-pipe transport (not implemented)]] → §4.5.
20. *"There was a capture format that validates itself and fingerprints."* → [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns#Versioned capture envelope]] → overview §Open questions; ↳ Upwork Tracker.

## Related documents

- [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns|Index of Design Patterns]] — the index this rationale explains.
- [[Research/Software Architecture Garden/surf-cli/README|surf-cli study]] — the evidence-pinned source.
- [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview|Project Architecture Overview]] — the five fundamentals.
- [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker|Browser-Launched Host Broker]] — the flagship deep entry.
- [[Research/Software Architecture Garden/README|Software Architecture Garden]] — the Garden root and its maturity vocabulary.
