---
title: "P08 - Bidirectional Links and Consistency Restoration"
subtitle: "Implementation report for a self-contained PBUI research laboratory"
author: "PBUI subsystem study"
date: "2026-08-04"
toc: true
toc-depth: 3
geometry: margin=0.85in
fontsize: 11pt
mainfont: "DejaVu Serif"
sansfont: "DejaVu Sans"
monofont: "DejaVu Sans Mono"
colorlinks: true
linkcolor: blue
urlcolor: blue
header-includes:
  - |
    \usepackage{microtype}
  - |
    \usepackage{longtable}
  - |
    \usepackage{booktabs}
  - |
    \usepackage{fvextra}
  - |
    \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\}}
  - |
    \usepackage{enumitem}
  - |
    \setlist{nosep}
---

# Executive summary

P08 investigates a specific question inside a presentation-based UI architecture:

> When two independently authored views expose related state, what must a link mean, how is consistency restored after either side changes, and how can failures and conflicts remain explicit rather than being hidden inside callbacks?

The implementation is a self-contained browser laboratory derived from the supplied PBUI productivity-suite prototype. The source prototype treats objects such as tasks, contacts, events, transcripts, moments, and booking links as typed live presentations. It also centralizes mutable product records and records mutations in a trace. P08 preserves that product vocabulary and visual character while replacing direct cross-object mutation with an explicit link subsystem.

The result separates five concerns:

1. **Endpoint definitions** describe typed, readable and writable projections of product state.
2. **Relation specifications** state when two endpoint values are consistent and how either side can repair the other.
3. **Explicit links** connect endpoint references through one named relation and retain complement, baseline, dirty-side, status, and conflict information.
4. **A transactional runtime** applies commands and propagates changes through the active link graph until quiescence.
5. **Executable law audits and experiments** test consistency restoration, round trips, merge laws, cyclic propagation, unlinking, partial failure, serialization, and composition.

The most important design conclusion is that a bidirectional link is not merely two setters. It is a persistent object containing a declared consistency relation, two directional repair procedures, a conflict policy, and enough retained information to explain and reverse topology changes.

# 1. Research framing

## 1.1 Problem statement

A presentation-based UI makes domain objects available across visual contexts. Once components can select, inspect, and act on objects presented elsewhere, users naturally expect some of those views to remain coordinated.

Examples from the productivity domain include:

- a task's due date and a calendar event's start time;
- a task title and the title of a calendar focus block;
- an event's attendees and the participant set of a related call transcript;
- an action item extracted from a transcript and the task created from it;
- a booking's start time and the event materialized from that booking.

These pairs do not all have the same semantics. Some are equality links. Some relate unequal representations. Some preserve hidden information. Some can merge concurrent changes. Some are partial. Some should report a conflict rather than select a winner.

A generic implementation therefore cannot reduce all links to:

```js
onChangeA(value => setB(value));
onChangeB(value => setA(value));
```

That formulation hides the consistency predicate, cannot distinguish repair from ordinary editing, provides no principled conflict semantics, is vulnerable to feedback loops, and is difficult to compose or test.

## 1.2 Research questions

The implementation is organized around these questions:

1. Can a small relation interface express equality links, unequal but related views, complement-preserving transformations, partial repair, and mergeable conflicts?
2. Can independently declared links compose through shared product resources without components knowing about one another?
3. Can a finite work-queue runtime propagate changes through cycles to quiescence while detecting non-convergence?
4. Can paused links make divergence and conflict observable instead of silently applying a last-writer rule?
5. Can relation laws be tested independently of the runtime and can deliberately bad specifications be falsified?
6. Can unlinking alter topology while preserving all current endpoint values?
7. Which state must be durable so a future composition pass can serialize, inspect, replay, and migrate links?

## 1.3 Hypotheses

The prototype evaluates the following hypotheses.

**H1 - Explicit relation specifications improve testability.** A relation represented by `check`, `repairFromLeft`, and `repairFromRight` admits direct law checks that callback wiring does not expose.

**H2 - Conflict should be state, not control flow.** If both sides change while repair is suspended, resuming should create an inspectable conflict object rather than invoking an undocumented precedence rule.

**H3 - Composition requires resource-level invalidation.** Two endpoint references may be different projections of the same underlying entity. A write through one projection must notify links attached to other affected projections.

**H4 - Topology and value policy are separate.** Removing a link changes the graph but should not itself rewrite either endpoint. Creating a link requires an explicit initial reconciliation policy.

**H5 - Useful laws can be checked without pretending arbitrary JavaScript is proven.** Executable samples and property tests can falsify common defects while the report states the limits of that evidence.

## 1.4 Non-goals

P08 does not attempt to provide:

- a production distributed database;
- a complete symmetric-lens calculus;
- automatic synthesis of repair functions from a relation;
- authorization or capability proofs;
- a complete PBUI selector, action, or presentation registry;
- conflict-free replication across offline devices;
- a mechanized proof in Lean or Coq;
- production React reconciliation semantics.

Those concerns are separate projects or second-pass integration work.

# 2. Source-derived scenario

The supplied source is a single JSX productivity suite with email, calendar, contacts, tasks, booking links, and transcripts. Its product records are deliberately JSON-like and centrally mutable. It presents tasks, projects, contacts, events, transcript moments, action items, links, bookings, tiles, and workspaces as first-class typed objects.

P08 reuses a focused subset of that world:

- the task **Draft SOC2 timeline for Daniel**;
- its corresponding calendar focus event;
- the **TechFlow QBR** event and **Customer call - Jamie Torres** transcript;
- **Book ferry for Labor Day**, a pre-read event, and a product-demo booking for cyclic instant propagation;
- the transcript action item **Send Daniel real SOC2 timeline by Friday** and its task/event chain.

This is not a wrapper around the original `World` class. The laboratory extracts the domain fixtures and builds a new subsystem boundary around explicit endpoint and relation registries.

# 3. Formal model

## 3.1 Worlds, endpoints, and values

Let \(W\) be the space of product worlds. An endpoint reference \(p\) has a semantic sort \(S_p\), a read function, and a write operation:

\[
  \mathsf{read}_p : W \to S_p
\]

\[
  \mathsf{write}_p : W \times S_p \to W.
\]

The implementation treats writes transactionally by cloning the durable state before applying a command. Endpoint definitions also declare one or more resource keys:

\[
  \mathsf{resources}(p) \subseteq \mathcal{R}.
\]

Resource keys state which underlying product entities may be changed by a write. They are needed because two different endpoints can overlap. For example:

```text
 taskTitle:tk-4  -> resource task:tk-4
 taskFocus:tk-4  -> resource task:tk-4
```

A title write through the first endpoint can change the value observed by the second endpoint even though their endpoint keys differ.

## 3.2 Consistency relations

For left sort \(L\), right sort \(R\), and complement state \(C\), a relation specification contains a predicate:

\[
  \mathcal{K} \subseteq L \times R \times C.
\]

The executable form is:

```js
check(left, right, complement)
  -> { consistent, differences }
```

The `differences` field is explanatory evidence. It is not part of the mathematical predicate, but it is essential for diagnostics and conflict UI.

## 3.3 Directional repair

A left-to-right repair may update the right value, the complement, or both:

\[
  \mathsf{putR} : L \times R \times C
    \rightharpoonup R \times C.
\]

A right-to-left repair is:

\[
  \mathsf{putL} : L \times R \times C
    \rightharpoonup L \times C.
\]

The hooked arrow denotes partiality. The implementation returns a tagged result rather than throwing for a domain-level repair failure:

```js
{ ok: true, right, complement, explanation }
```

or:

```js
{ ok: false, reason, details }
```

Partiality is important. A task with no due instant cannot produce a positioned calendar block under the structured relation. An event whose end precedes its start cannot be converted into a valid task focus.

## 3.4 Complements

A complement retains information that one side does not represent. In the task/event relation, the task carries title and due date but does not carry event duration. The link therefore retains:

```js
{
  durationMs: event.end - event.start
}
```

When the task changes, the event moves to the new due instant while preserving duration. When the event changes, the task receives the event start and normalized title while the edited duration becomes the new complement.

This is a pragmatic complement-based bidirectional transformation. It is not presented as a full formal symmetric lens.

## 3.5 Links

A durable link has approximately this structure:

```js
{
  id,
  relation,
  left,
  right,
  status,       // active | paused | conflict | error
  complement,
  baseline: { left, right, complement },
  dirty: { left, right },
  conflict,
  revision
}
```

The baseline is the last known consistent state. Dirty flags record which side changed while the link was paused. Conflict data records both proposals and the relation's explanation of their disagreement.

## 3.6 Runtime transition system

Let \(\Sigma\) be the complete runtime state and \(C\) a command. The runtime implements a deterministic transition:

\[
  \mathsf{dispatch} : \Sigma \times C \to \Sigma \times \mathsf{Result}.
\]

Commands include:

```text
create-link
remove-link
edit-endpoint
pause-link
resume-link
resolve-conflict
repair-link
clear-trace
```

An endpoint edit adds affected resources to a work queue. Active incident links run their appropriate directional repair. Any endpoint writes produced by repair add their resources to the queue. The transaction ends when the queue is empty or a step bound is exceeded.

## 3.7 Quiescence

For a finite active link graph, propagation seeks a state \(\Sigma^*\) such that another propagation round performs no endpoint write:

\[
  F(\Sigma^*) = \Sigma^*.
\]

P08 does not claim that arbitrary user-defined relations always converge. The runtime imposes a maximum propagation-step limit and transitions the transaction to an explicit non-convergence error if the limit is exceeded.

# 4. Implementation architecture

## 4.1 Endpoint registry

`src/core/endpoints.js` defines `EndpointRegistry`. Each endpoint kind declares:

- stable kind name;
- semantic sort;
- existence predicate;
- human label;
- read function;
- write function;
- equality function where default deep equality is insufficient;
- resource keys for overlap detection.

The productivity registry includes:

| Endpoint kind | Sort | Product projection |
|---|---|---|
| `taskFocus` | `task-focus` | task title, due, project, status |
| `eventFocus` | `event-focus` | event title, start, end, kind, notes |
| `taskDue` | `instant` | task due timestamp |
| `eventStart` | `instant` | event start, preserving duration on write |
| `bookingStart` | `instant` | booking start timestamp |
| `taskTitle` | `text` | task title |
| `actionItemText` | `text` | nested transcript action-item text |
| `eventAttendees` | `contact-set` | canonicalized attendee set |
| `transcriptParticipants` | `contact-set` | canonicalized participant set |
| `scalar` | `scalar` | generic laboratory scalar |

Typed sorts reject invalid links before they are installed.

## 4.2 Relation registry

`src/core/relations.js` defines the following successful relation specifications.

### Equal instant

\[
  l = r.
\]

Either repair copies the source instant. A two-sided conflict has no commutative merge, although rollback to the baseline remains available.

### Equal text

\[
  l = r.
\]

This relation is used in the action-item-to-task-title link.

### Equal contact set

\[
  \mathrm{set}(l) = \mathrm{set}(r).
\]

Values are canonicalized by uniqueness and sorting. The merge operation is set union:

\[
  l \sqcup r = l \cup r.
\]

The relation declares and tests idempotence, commutativity, and associativity of this merge algebra.

### Task/event focus

The consistency relation requires:

\[
  \mathsf{event.start} = \mathsf{task.due},
\]

\[
  \mathsf{event.end}
    = \mathsf{event.start} + \mathsf{complement.durationMs},
\]

and:

\[
  \mathsf{event.title}
    = \texttt{"Focus: "} + \mathsf{normalize}(\mathsf{task.title}).
\]

Repair from the task normalizes the event title, moves the event, and preserves duration. Repair from the event reads start and normalized title into the task and updates the duration complement.

### Deliberate counterexamples

Two intentionally bad relations demonstrate the audit's ability to reject defects:

- integer Celsius/Fahrenheit conversion with rounding loses information and violates a round-trip property;
- a Boolean relation declares `right = not left`, but its right-to-left repair copies rather than negates.

## 4.3 Bidirectional runtime

`src/core/runtime.js` owns topology and propagation. Important design decisions are:

### Explicit initial reconciliation

Creating a link requires a policy such as `prefer-left` or `prefer-right`. The runtime never pretends that merely connecting two endpoints determines which current value should survive.

### Pausing

A paused link performs no repair. Edits still update the world and mark the corresponding side dirty.

### Resuming

- no dirty side: verify and activate;
- only left dirty: repair from left;
- only right dirty: repair from right;
- both dirty: create a conflict.

### Conflicts

Conflict state retains:

- current left and right proposals;
- last consistent baseline;
- complement;
- relation-specific differences.

Resolution strategies are:

- `prefer-left`;
- `prefer-right`;
- `merge`, when the relation provides it;
- `rollback` to the baseline.

### Resource-level composition

The first implementation keyed propagation only by endpoint reference. That failed in the composition scenario: changing `taskTitle:tk-4` also changes the value observed by `taskFocus:tk-4`, but the latter link was not notified.

The fix was to record resource overlap. Every write captures before/after values for all registered endpoint references touching the affected resource. Any changed projection is queued. This permits independently declared links to compose through a shared entity without one relation importing the other.

### Trace

Every command and repair produces trace records with transaction IDs. The trace separates:

- command boundaries;
- direct endpoint writes;
- repair endpoint writes;
- relation activations;
- conflict creation and resolution;
- errors;
- overlapping projection changes.

## 4.4 React laboratory

`src/App.jsx` renders six tabs:

1. **task ↔ event** - unequal structured representations and retained complement;
2. **set merge** - set-valued endpoints and conflict union;
3. **cycle** - three equality links reaching quiescence;
4. **composition** - action item → task title → structured event relation;
5. **law audit** - successful laws and intentional counterexamples;
6. **trace** - command and repair history plus state export.

A right-hand inspector shows topology, selected-link internals, current relation status, and a generic compatible-link composer.

The browser artifact uses `scripts/mini-react-runtime.js`, a deliberately small JSX adapter implementing only the hooks and DOM behavior needed by this laboratory. It is not part of the bidirectional semantics.

# 5. User experiments

## 5.1 Structured task/event relation

The initial link connects the SOC2 task focus to its calendar focus block.

Try:

1. Edit the task title. The event title becomes `Focus: <normalized task title>`.
2. Move the task due date. The event moves but retains its duration.
3. Edit the event start or end. The task due date and complement update.
4. Pause the link and edit only one side. Resume; the one-sided edit repairs automatically.
5. Pause the link, edit both sides, and resume. The UI exposes a conflict.
6. Resolve by preferring either side or rolling back.
7. Unlink. Both current values remain unchanged.

This scenario demonstrates an asymmetric representation and complement preservation.

## 5.2 Set-valued merge

The event attendees and transcript participants are linked by set equality.

Try:

1. Add or remove contacts while active; the peer set follows.
2. Pause the link.
3. Add one contact only to the event and another only to the transcript.
4. Resume to obtain a conflict.
5. Select merge. Both sides become the set union.

This scenario demonstrates a lawful merge algebra rather than a winner-selection policy.

## 5.3 Cyclic propagation

Three `instant` endpoints form a cycle:

```text
 task due ↔ event start ↔ booking start ↔ task due
```

Changing any endpoint propagates through the cycle. Equality repair is idempotent, so the work queue reaches quiescence. The UI reports the number of relation activations and endpoint writes in the last transaction.

This is a convergence example, not a proof that arbitrary cycles converge.

## 5.4 Composition across overlapping projections

The action-item text is equality-linked to a task title. The complete task focus is independently related to an event focus.

```text
 actionItemText --equal-text--> taskTitle
                                   |
                              same task resource
                                   |
 taskFocus --task-event-focus--> eventFocus
```

Editing the action item changes the task title. Resource-level invalidation observes that the task-focus projection also changed and activates the task/event link. The event title then updates.

This scenario is the key second-pass composition result inside P08: independently declared links compose without directly naming each other.

## 5.5 Law audit

The law tab executes relation-level checks over sample values. The successful relations should pass. The two deliberately defective relations should fail with concrete failed obligations.

## 5.6 Trace and export

The trace tab shows the most recent runtime records. Export writes the durable runtime state as JSON, including world records, links, baselines, complements, conflicts, revisions, and trace.

# 6. Laws and validation claims

## 6.1 Repair establishes consistency

For every successful left repair sample:

\[
  \mathsf{putR}(l,r,c)=(r',c')
  \Longrightarrow
  \mathcal{K}(l,r',c').
\]

For every successful right repair sample:

\[
  \mathsf{putL}(l,r,c)=(l',c')
  \Longrightarrow
  \mathcal{K}(l',r,c').
\]

## 6.2 Idempotent repair on a consistent pair

After a repair establishes consistency, repeating the same directed repair should not change the observable normalized pair.

## 6.3 Round-trip stability

The audit checks sample-level round trips in both directions. For the structured relation, equality is understood after the relation's explicit normalization and complement treatment, not as byte-for-byte preservation of every source representation.

## 6.4 Merge algebra

For the contact-set merge, the audit checks:

\[
  a \sqcup a = a,
\]

\[
  a \sqcup b = b \sqcup a,
\]

\[
  (a \sqcup b) \sqcup c = a \sqcup (b \sqcup c).
\]

## 6.5 Active-link invariant

After a successful transaction reaches quiescence:

\[
  \forall \ell \in \mathsf{ActiveLinks},
  \quad \mathcal{K}_\ell(l_\ell,r_\ell,c_\ell).
\]

The randomized test performs 250 active edits across the laboratory graph and checks this invariant after every transaction.

## 6.6 Unlink value preservation

Removing a link changes topology but performs no endpoint write:

\[
  \mathsf{read}_{p}(W_{before})
    = \mathsf{read}_{p}(W_{after})
\]

for each former endpoint of the removed link.

## 6.7 Serialization

Serialization preserves the durable world and explicit link graph. It does not serialize executable registry code; the same endpoint and relation registries must be supplied when a serialized state is interpreted.

## 6.8 Scope of evidence

The law audit is executable falsification over declared samples, supplemented by deterministic tests and randomized traces. It is not a universal proof over arbitrary JavaScript values or arbitrary relation implementations. The counterexamples illustrate why the distinction matters.

# 7. Validation results

The final local validation command was:

```bash
npm run check
```

It completed with:

- 16 passing Node tests;
- successful law reports for `equal-instant`, `equal-contact-set`, and `task-event-focus`;
- intentional failures for both defective counterexamples;
- 3,000 benchmark edits with all active links consistent at completion;
- an explicit conflict observed in the paused two-sided divergence scenario;
- a successful standalone HTML build.

A separate Chromium smoke test exercised:

- task-to-event propagation;
- paused double edit and conflict creation;
- prefer-left conflict resolution;
- set-union conflict merge;
- cyclic propagation;
- action-item/task/event composition;
- law-audit rendering;
- trace rendering.

The most recent machine-specific result is stored in `experiments/results.json`. On this run the benchmark observed approximately 4,768 edits per second, six relation activations per edit, and three endpoint writes per edit. These numbers describe this small fixed graph on one environment; they are not a general performance claim.

![Initial state of the P08 laboratory](../experiments/p08-ui-initial.png){width=100%}

# 8. Failure modes explored

## 8.1 Incompatible sorts

A link between endpoints whose sorts do not match the relation's declared left and right sorts is rejected before installation.

## 8.2 Partial repair

Clearing a task due date makes task-to-event repair undefined. The runtime leaves the product edit intact, pauses the link, and records an explicit error rather than inventing a time.

## 8.3 Two-sided divergence

When both sides change while paused, resume produces conflict state and performs no hidden arbitration.

## 8.4 Non-convergent cycles

The runtime has a propagation-step bound. A relation network that continues changing values instead of reaching quiescence results in a non-convergence error. The supplied successful cycle uses idempotent equality repair and does converge.

## 8.5 Overlapping projections

Endpoint-key-only invalidation is unsound when multiple projections touch one entity. The composition regression test protects the resource-overlap fix.

## 8.6 Lossy transformation

Integer temperature conversion demonstrates that apparently reasonable round-trip conversions can violate consistency or preservation after rounding.

# 9. API boundary for later composition

The machine-readable `composition-capsule.json` records the subsystem's imports, exports, commands, events, schemas, guarantees, assumptions, and known gaps.

The principal exported abstractions are:

```js
EndpointRegistry
RelationRegistry
BidirectionalRuntime
serializeRuntimeState
createProductivityEndpointRegistry
createRelationRegistry
```

A future PBUI composition pass should adapt:

- P01 semantic subject identities into endpoint references;
- P02 mounted occurrences into interactive endpoint affordances;
- P03 selectors into endpoint/link target queries;
- P05 capabilities into command preconditions for link creation, editing, and resolution;
- P06 typed port identities into P08 endpoint references;
- P07 component signatures into endpoint-kind and relation imports;
- P09 interaction machines into conflict and link-creation workflows;
- P10 effect handlers into persistence, remote commands, and user prompts;
- P11 incremental maintenance into a replacement for the current small work queue;
- P12 replication into explicit replicated topology and value protocols;
- P13 explanations into relation difference and trace presentation;
- P14 mechanized laws into certificates or verified relation kernels;
- P15 conformance tests into common trace and state schemas.

# 10. Limitations and unresolved questions

## 10.1 No general bidirectional calculus

Relation implementations are handwritten JavaScript. The interface organizes and tests them but does not derive them or prove totality, determinism, or confluence.

## 10.2 Global cloning

Each command clones the laboratory state. That is acceptable for the small fixture and makes rollback and test isolation simple. A production system would use persistent data structures, transactions, or structured patches.

## 10.3 Coarse resource declarations

Resource overlap is manually declared by endpoint kinds. Incorrect declarations can cause unnecessary propagation or missed invalidation. A richer system could derive dependencies from optics, schema paths, or instrumented reads and writes.

## 10.4 Single-process scheduling

The runtime is synchronous and single-process. There are no asynchronous effects, interleaved remote transactions, or replicated clocks.

## 10.5 Conflict policy remains application-specific

Set union is lawful for participant sets but unsuitable for every domain. Scalar time conflicts deliberately have no commutative merge. Product design must choose between coordination, user choice, multi-value state, precedence, or a domain algebra.

## 10.6 Complement migration

A relation's complement is durable but not versioned independently. Relation-schema evolution would need complement codecs and migrations.

## 10.7 UI adapter

The tiny JSX runtime exists solely to keep the result offline and dependency-free. It is not intended as a React replacement and does not implement effects, context, concurrent rendering, keyed lifecycle semantics, or production accessibility infrastructure.

# 11. Suggested second-pass experiments

1. Replace endpoint `resources` declarations with law-tested optics and compare invalidation precision.
2. Connect P06 port quotient classes to P08 equality endpoints and determine which semantics belong in each layer.
3. Let P09 model link creation and conflict resolution as explicit interaction machines.
4. Add P05 capability evidence and test stale-authority rejection at command commit time.
5. Feed P08 trace records into P15 model-based conformance testing.
6. Replace the work queue with a P11 differential runtime and compare reference equivalence and invalidation cost.
7. Add P12 replicated edge and value semantics; test concurrent link/remove and incompatible scalar writes.
8. Mechanize the equal-set and task/event relation fragments in P14, including complement laws and unlink preservation.
9. Conduct user studies comparing hidden automatic precedence, explicit conflict, and merge-oriented resolution.
10. Explore dynamic link graphs with hundreds of endpoints and adversarial cycles.

# 12. Reproduction

No dependency installation is required.

```bash
cd p08-bidirectional-links-lab
npm run check
```

Open:

```text
dist/p08-bidirectional-links.html
```

To serve over HTTP:

```bash
npm run serve
```

The source fixture is retained unchanged at:

```text
reference/pbui-productivity-suite.jsx
```

# Appendix A - File map

```text
README.md
composition-capsule.json
dist/
  p08-bidirectional-links.html
  authoring-bundle.js
docs/
  P08_IMPLEMENTATION_REPORT.md
  P08_IMPLEMENTATION_REPORT.pdf
experiments/
  run.mjs
  results.json
  ui-smoke.py
  p08-ui-initial.png
  p08-ui.png
reference/
  pbui-productivity-suite.jsx
scripts/
  build-standalone.mjs
  mini-react-runtime.js
src/
  App.jsx
  data.js
  styles.css
  components/
  core/
```

# Appendix B - Command examples

Create a typed link:

```js
runtime.dispatch(state, {
  type: "create-link",
  id: "link-task-event",
  relation: "task-event-focus",
  left: { kind: "taskFocus", id: "tk-4" },
  right: { kind: "eventFocus", id: "e-17" },
  policy: "prefer-left",
});
```

Edit an endpoint:

```js
runtime.dispatch(state, {
  type: "edit-endpoint",
  endpoint: { kind: "taskDue", id: "tk-13" },
  value: Date.UTC(2026, 7, 6, 14, 0),
  actor: "task-editor",
});
```

Pause, diverge, and resume:

```js
state = runtime.dispatch(state, {
  type: "pause-link",
  id: "link-attendees",
}).state;

// Independent edits occur here.

state = runtime.dispatch(state, {
  type: "resume-link",
  id: "link-attendees",
}).state;
```

Resolve with a relation-provided merge:

```js
state = runtime.dispatch(state, {
  type: "resolve-conflict",
  id: "link-attendees",
  strategy: "merge",
}).state;
```
