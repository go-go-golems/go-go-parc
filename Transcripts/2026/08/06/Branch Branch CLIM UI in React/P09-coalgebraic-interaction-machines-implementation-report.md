---
title: "P09 - Coalgebraic Interaction Machines"
subtitle: "Reference implementation, experiments, and composition boundary"
author: "PBUI subsystem research program"
date: "2026-08-05"
lang: en-US
toc: true
toc-depth: 3
geometry: margin=0.82in
fontsize: 10pt
colorlinks: true
linkcolor: blue
urlcolor: blue
header-includes:
  - |
    ```{=latex}
    \usepackage{microtype}
    \usepackage{fvextra}
    \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\}}
    \setlength{\parskip}{0.45em}
    \setlength{\parindent}{0pt}
    ```
---

# Executive summary

P09 replaces an implicit callback-and-promise interaction protocol with explicit, inspectable machines. Each interaction is defined by:

1. an internal state;
2. a pure observation function;
3. a pure transition function from the current state and an input event to a successor state and effect data;
4. an external interpreter for product commands, requests, notifications, cancellation, and terminal resolution.

The supplied productivity-suite prototype already has the essential product behavior: every rendered object is a typed presentation; some actions request a second object; acceptable presentations become visually sensitive across tiles and workspaces; activating one resolves a pending promise. The prototype stores that continuation in one ambient `accepting` value and clears it after acceptance or Escape. P09 preserves the user-facing behavior while making the control state explicit and independently executable.

The implementation contains four product workflows:

- scheduling a meeting with a contact by choosing a typed calendar slot;
- promoting a transcript action item to a task after choosing an optional project;
- obtaining an external booking approval before committing a calendar event;
- collecting one or more contacts for a compose operation.

It also contains two small accept machines that have different internal state representations but the same public behavior. A complete finite-state bisimulation checker verifies their equivalence over all reachable states and all events in the declared alphabet. A deliberately broken machine yields a one-event counterexample: it accepts a `<project>` when the request requires a `<contact>`.

The runtime records logical traces, enforces at-most-once resolution, treats terminal states as absorbing, checks revision-bearing occurrence tokens, interprets product commands transactionally, supports cancellable external requests, and can replay, rewind, fork, and serialize a session. An interaction manager makes input ownership explicit: one pointer channel can queue competing workflows while an independent network channel continues to progress.

The implementation is intentionally a reference model rather than a production framework. It does not provide a general statechart language, weak bisimulation, nondeterminism, distributed session ownership, mechanized proofs, or the algebraic workflow language assigned primarily to P10. It provides a small executable substrate on which those alternatives can be compared.

# 1. Research framing

## 1.1 Problem statement

A callback-oriented user interface can encode almost any interaction. That is not the same as giving the interaction a stable semantic object.

Consider the source protocol:

```text
button callback
  -> store a promise resolver in ambient UI state
  -> highlight matching presentations
  -> a later click invokes the resolver
  -> clear the ambient state
  -> resume arbitrary caller code
```

This implementation is concise. However, the continuation, terminal behavior, cancellation semantics, enabled events, and effect boundary are distributed among closures and component lifecycle. Questions such as the following require reconstructing behavior from control flow:

- Can the session resolve twice?
- What happens when a response arrives after cancellation?
- Which state owns Escape?
- Can two interactions run simultaneously?
- Is a stale rendered occurrence revalidated?
- Can the sequence be replayed without React?
- Are two refactored implementations behaviorally equivalent?
- Which product mutations were caused by which transition?

P09 asks whether a small explicit machine protocol makes these questions executable and, for finite cases, exhaustively checkable.

## 1.2 Research questions

The implementation addresses the following questions.

1. **Semantic separation.** Can observation, transition, and product effects be separated without losing the directness of the presentation-based interaction?
2. **Stale-input safety.** Can a rendered occurrence be represented as a revision-bearing event token and revalidated both on selection and at commit?
3. **Terminal discipline.** Can cancellation, failure, rejection, and successful completion be terminal values with at-most-once resolution?
4. **Asynchrony.** Can an external request remain explicit while the machine waits, and can a late response be ignored after cancellation?
5. **Ownership.** Can competing pointer interactions be queued while an unrelated background interaction proceeds?
6. **Replay.** Can the public result be reproduced from the initial world and a portable sequence of external inputs?
7. **Behavioral equivalence.** Can two internal representations be compared through public observations and effects rather than structural state equality?
8. **Composition boundary.** Can this subsystem drive later selection, capability, port-linking, bidirectional-repair, and effect-language implementations without importing them now?

## 1.3 Hypotheses

- A machine with explicit state and observation will make enabled inputs and terminal behavior easier to inspect than a promise resolver stored in component state.
- A read-only transition snapshot plus interpreted command effects will prevent accidental product mutation during control-state evolution.
- Revision-bearing occurrence tokens will expose stale-selection races before command execution.
- Recording external inputs rather than host-language continuations will permit deterministic replay when handlers are deterministic.
- A finite bisimulation checker will distinguish representation changes from user-observable changes and will produce useful counterexample traces.
- Channel ownership and queuing will make concurrent interaction policy explicit, but will not by themselves solve distributed concurrency or fairness.

## 1.4 Non-goals

This implementation does not attempt to:

- claim that every UI is finite state;
- identify a React component with a coalgebra;
- provide a general theorem that arbitrary JavaScript machines are pure or deterministic;
- replace the product command kernel with a state machine;
- implement a complete Harel statechart semantics;
- implement interaction trees, free monads, or a general algebraic-effect language;
- prove equivalence of the complete productivity suite;
- treat visual action availability as authorization;
- solve replicated or multi-user session ownership;
- optimize large dynamic candidate sets.

# 2. Source-derived scenario

The supplied JSX establishes a personal-productivity world containing email, calendar, contacts, tasks, booking links, transcripts, tiles, and workspaces. Its central PBUI mechanism has three relevant properties.

First, visible objects are wrapped as typed presentations. Second, one ambient acceptance request records a desired type and a promise resolver. Third, a presentation checks whether its type matches the request; if so, activation resolves the promise and clears the request. Escape resolves the request with `null`.

P09 takes three scenarios directly from that vocabulary:

- a contact operation requests a calendar slot and creates an event;
- a transcript action item requests a project and creates a task;
- a booking is approved and converted into a calendar event.

The standalone data fixture uses a compact subset of the source records, including Sarah Chen, Jamie Torres, Nikhil Rao, the Q4 and hiring projects, transcript action items, a pending product-demo booking, and several fixed calendar slots.

The source remains unchanged under `reference/pbui-productivity-suite.jsx`. P09 does not modify or depend on its React components. It treats the source as the product vocabulary and comparative baseline.

# 3. Formal model

## 3.1 A deterministic machine with observations and effects

For input events in a set \(I\), observations in \(O\), effects in \(E\), and machine states in \(S\), the design can be presented as a coalgebra of the shape

\[
\gamma : S \longrightarrow O \times (S \times E^*)^I.
\]

Given a state, the machine exposes a current observation and, for every input event, a successor state with a finite sequence of effects.

The implementation splits this curried form into two functions:

\[
\mathsf{observe} : S \times W \longrightarrow O
\]

and

\[
\mathsf{transition} : S \times I \times W \longrightarrow S \times E^*,
\]

where \(W\) is a read-only product snapshot. This resembles the familiar distinction between a Moore observation and a Mealy transition.

The JavaScript interface is:

```js
{
  id,
  initial(input, context) -> state,
  observe(state, context) -> observation,
  transition(state, event, context) -> { state, effects },
  eventAlphabet?(state, context) -> events,
  publicObservation?(observation) -> observableView
}
```

The optional event alphabet is used only for finite exploration. The optional public-observation projection supports behavioral comparison when an implementation exposes diagnostic fields that are not part of the public protocol.

## 3.2 The complete runtime state

The machine state alone is not the complete application system. The executable runtime contains:

\[
R = S \times W \times P \times Q \times T \times \mathsf{Option}(A),
\]

where:

- \(S\) is the current machine state;
- \(W\) is product state;
- \(P\) is the map of pending external requests;
- \(Q\) is the sequence of portable external inputs;
- \(T\) is the logical trace;
- \(A\) is a terminal resolution value.

The runtime itself can therefore be viewed as a larger transition system. P09 keeps the smaller machine definition independent because it is the intended authoring and comparison unit.

## 3.3 Observations

An observation is renderer-independent data:

```js
{
  title,
  phase,
  status,
  prompt,
  expectedSort,
  candidates,
  controls,
  terminal,
  outcome,
  error,
  progress
}
```

Not every machine uses every field. The React laboratory interprets the observation as prompts, candidate cards, buttons, status chips, and progress bars. Another interpreter could expose the same observation through a command line, accessibility tree, remote protocol, or test driver.

The candidate list is not durable machine state in this implementation. It is recomputed from the current product snapshot. This means a slot disappearing from the world also disappears from the next observation, even if the machine state itself does not change.

## 3.4 Events

Events are immutable data. The implemented families include:

```text
choose-occurrence
confirm
back
cancel
submit
choose-none
finish
command-succeeded
command-failed
external-response
```

A semantic occurrence event carries:

```js
{
  occurrenceId,
  sort,
  subjectId,
  revision,
  label,
  metadata
}
```

The revision is part of the event evidence. It does not prove that the subject is still valid. The machine asks the current product snapshot to resolve the token and rejects it when the stored revision no longer matches.

## 3.5 Effects

Machine transitions do not mutate the durable product world. They emit one of four effect families.

### World command

```js
{
  type: "world-command",
  requestId,
  command
}
```

The product interpreter validates and applies the command transactionally. It then sends either `command-succeeded` or `command-failed` back into the machine.

### External request

```js
{
  type: "external-request",
  requestId,
  request
}
```

The runtime stores this request until an explicit `external-response` event is delivered. No JavaScript promise continuation is stored in the machine.

### Resolution

```js
{
  type: "resolve",
  outcome
}
```

The runtime accepts the first resolution and traces any attempted duplicate. The implemented machines enter a terminal state on the same transition that emits a resolution.

### Notification

```js
{
  type: "notification",
  level,
  message
}
```

Notifications are recorded separately from the semantic outcome.

## 3.6 Terminal behavior

A terminal observation has `terminal: true`. The reference runtime checks this before calling the machine transition function. Every subsequent event is recorded as `event-ignored-terminal` and cannot emit a product command or replace the resolution.

For the finite accept machines, terminal absorption is also checked directly against every event in the declared alphabet:

\[
\forall s \in \mathsf{Terminal},\;\forall i \in I,
\quad \delta(s,i)=(s,[]).
\]

This two-level treatment is deliberate. The runtime protects a session even if a custom machine omits the absorbing case, while audited machine specifications remain independently well behaved.

## 3.7 Traces and replay

The runtime records logical trace entries rather than wall-clock timestamps. Relevant entries include:

```text
session-started
observation
event-received
transition
effect-emitted
command-started
command-succeeded
command-failed
external-request-opened
external-response-delivered
session-resolved
event-ignored-terminal
```

Replay does not serialize every internal transition. It serializes the initial world, machine identifier, initial input, and external inputs:

```text
machine event
world/environment command
external response delivery
```

Deterministic command interpretation then regenerates internal command responses and traces. The replay claim is conditional:

\[
\mathsf{Replay}(W_0,Q)=R
\]

only when the machine functions and effect handlers are deterministic for \(W_0\) and \(Q\).

## 3.8 Bisimulation

Two machines may use different state representations while exposing the same behavior. P09 checks a strong deterministic bisimulation over a finite event alphabet.

A relation \(\mathcal{R}\subseteq S_1\times S_2\) is accepted when related states have equal public observations and, for every event, emit equal normalized effects and transition to another related pair.

For related \((s_1,s_2)\):

\[
\mathsf{publicObserve}_1(s_1)=\mathsf{publicObserve}_2(s_2),
\]

and for every \(i\in I\):

\[
\delta_1(s_1,i)=(s_1',e_1),
\quad
\delta_2(s_2,i)=(s_2',e_2),
\]

with

\[
e_1=e_2
\quad\text{and}\quad
(s_1',s_2')\in\mathcal{R}.
\]

The checker performs breadth-first exploration of reachable state pairs. If observations or effects diverge, it returns the event path leading to the mismatch.

This is not weak bisimulation. It does not hide internal \(\tau\)-steps, compare nondeterministic branching, or reason about infinite data-dependent state spaces.

## 3.9 Composition and channels

The interaction manager is an operational composition mechanism. It is not presented as a categorical product theorem.

A named channel has at most one active owner. A new session may:

- activate immediately when the channel is free;
- be queued;
- be rejected;
- cancel and replace the current owner;
- use a different channel and proceed independently.

The demonstration uses an exclusive `pointer` channel and a separate `network` channel. Recipient selection owns the pointer channel; scheduling queues behind it; booking approval advances on the network channel. When recipient selection terminates, scheduling is promoted.

# 4. Implementation architecture

## 4.1 `defineMachine`

`src/core/machine.js` validates the required shape and supplies small constructors for unchanged transitions, command effects, external requests, resolutions, and notifications.

It intentionally does not implement a class hierarchy or registry mutation. A machine is an immutable record of functions and metadata.

## 4.2 `MachineRuntime`

`src/core/runtime.js` is the primary interpreter. Its responsibilities are:

- initialize a machine from input and a product snapshot;
- compute observations;
- receive external and internal events;
- verify that a transition did not mutate durable world state;
- update machine state;
- interpret emitted effects;
- maintain pending external requests;
- enforce at-most-once resolution;
- record a logical trace;
- record portable external inputs;
- replay, fork, and serialize sessions.

The transition context contains a cloned world. This is a pragmatic runtime enforcement of one boundary: mutating `context.world` cannot affect durable state. It is not a proof that the transition is referentially transparent, because a transition could still access ambient globals or perform external effects. Application code is expected to obey the specification, and future work can use a restricted language or stronger sandbox.

## 4.3 Product command interpreter

`src/core/product.js` separates typed occurrence lookup from product mutation.

The command interpreter clones the input world, validates the command, and returns either:

```js
{ ok: true, world, value, events }
```

or:

```js
{ ok: false, reason, details }
```

Failed commands return no new world and leave the input unchanged. Implemented commands include:

- `create-event-from-contact-slot`;
- `promote-action-item`;
- `approve-booking-to-event`;
- `save-compose-draft`;
- environment commands used to test stale tokens and authority changes.

Capability checks occur here rather than only in machine observations. A machine may have been started while authority existed and commit after it was revoked.

## 4.4 Occurrence revisions

The source prototype sends a type and value when a presentation is clicked. P09 enriches that event with a revision. Slot, project, contact, action-item, and booking records have revisions. A selection token is validated against the current entity.

The schedule machine checks the slot twice:

1. when `choose-occurrence` is received;
2. immediately before emitting the create-event command.

The command interpreter checks it a third time using `expectedSlotRevision`. These checks protect different boundaries: machine input, machine-to-effect transition, and authoritative mutation.

## 4.5 Workflow machines

### Schedule contact

States:

```text
choosing-slot
confirming
committing
completed | cancelled | failed
```

The machine demonstrates typed selection, backtracking, cancellation, stale selection, commit-time revalidation, command effects, capability failure, and terminal resolution.

### Promote action item

States:

```text
choosing-project
confirming
committing
completed | cancelled | failed
```

The project is optional. The action-item occurrence itself is captured at initialization and revalidated before the task command.

### Booking approval

States:

```text
reviewing
waiting-approval
committing
completed | rejected | cancelled | failed
```

Submitting emits an external request. Approval produces a world command. Cancellation while waiting is terminal; a later response is logged and ignored.

### Compose recipients

States:

```text
collecting
completed | cancelled
```

This machine remains in its input context after each selected contact, allowing multiple recipients before `finish`.

## 4.6 Interaction manager

`src/core/manager.js` manages channel ownership and a FIFO queue. Sessions share one `WorldStore`, so a command issued by one session is immediately visible to observations in another.

The manager is deliberately small. It does not provide fairness beyond FIFO promotion, priorities, nested ownership, focus restoration, distributed leases, or compensation when an owner crashes.

## 4.7 Finite model checker

`src/core/modelcheck.js` provides:

- reachable-state exploration;
- deterministic transition comparison by repeated evaluation;
- terminal absorption checks;
- resolve-effect discipline checks;
- stable graph labeling;
- strong finite bisimulation checking.

The event alphabet is supplied by the machine. Completeness is therefore relative to that alphabet and the chosen context.

## 4.8 React laboratory

`src/App.jsx` interprets observations but does not own workflow continuations. Buttons dispatch event data to a runtime. Candidate cards display the exact revision-bearing token that will be sent.

The final artifact is compiled into one offline HTML file using a small JSX adapter. That adapter is not part of the machine semantics and should be replaced by React proper in a production integration.

# 5. User experiments

## 5.1 Typed scheduling

1. Open the **Schedule** tab.
2. Choose a contact.
3. Select a visible `<slot>` candidate.
4. Inspect the `confirming` observation.
5. Confirm.
6. Inspect the created product event and command trace.

The event is not created by the click handler. The click sends a `choose-occurrence` event. Confirmation emits a serializable command effect. The product interpreter creates the event and sends `command-succeeded` back to the machine.

## 5.2 Stale occurrence token

1. Reset the schedule machine.
2. Capture a slot token.
3. Occupy that slot externally.
4. Dispatch the captured token.

The slot revision has changed. The machine stays in `choosing-slot`, reports `stale-occurrence`, and emits no command.

A second variation selects a currently valid slot, changes the world while the machine is in `confirming`, and then confirms. The machine revalidates the token and returns to selection with an invalidation error.

## 5.3 Capability revocation

1. Select a slot.
2. Turn off `scheduleEvent` authority.
3. Confirm.

The command interpreter rejects the command with `capability-revoked`. The machine terminates in `failed`. The UI's earlier availability did not grant permanent authority.

## 5.4 Action-item promotion

1. Open **Promotion**.
2. Choose an unpromoted transcript action item.
3. Select a project or choose no project.
4. Confirm task creation.

The command creates a task and writes its ID back to the action item. An external-promotion button can invalidate the captured action-item token before commit.

## 5.5 Cancellable external request

1. Open **Async approval**.
2. Submit the policy request.
3. Cancel while the machine is waiting.
4. Deliver the previously opened approval response.

The response remains visible in the trace, but the terminal machine does not issue a booking command. The booking stays pending.

## 5.6 Parallel sessions

1. Start recipient selection on the pointer channel.
2. Queue scheduling on the same channel.
3. Start booking approval on the network channel.
4. Select a recipient and finish.
5. Observe scheduling become pointer owner.
6. Submit and resolve the booking request independently.

This experiment separates input ownership from product state sharing.

## 5.7 Bisimulation

The **Bisimulation** tab presents:

- a passing complete comparison between flat and factored accept machines;
- a failing comparison with a deliberately broken machine;
- the counterexample event path;
- the finite state and edge tables;
- an interactive side-by-side stepper.

The correct machines retain equal public observations after a valid contact, wrong project, stale contact, or cancellation event. Their internal records are visibly different.

## 5.8 Trace, replay, rewind, and branch

The **Trace + replay** tab can run a successful or stale scheduling trace. `replay and compare` checks final state, product world, resolution, and public observation. `rewind one external input` reconstructs the prefix. A later cancellation creates a new branch without changing the original session.

# 6. Laws and validation claims

## 6.1 Transition-world separation

For every runtime transition, durable product state before and after calling the machine transition must be equal:

\[
W_{\mathrm{before}} = W_{\mathrm{after-transition-call}}.
\]

Only an interpreted world-command effect may replace the durable world.

The runtime enforces this by giving the machine a clone and comparing the durable world around the transition call.

## 6.2 At-most-once resolution

For each session trace:

\[
\#\{t\in T\mid t.\mathsf{type}=\mathsf{session-resolved}\}\le 1.
\]

The runtime stores the first outcome and traces attempted duplicates. The finite machine audit additionally rejects a transition containing multiple resolve effects.

## 6.3 Terminal absorption

For audited finite machines:

\[
\mathsf{terminal}(s) \Rightarrow
\forall i\in I,\;\delta(s,i)=(s,[]).
\]

For every runtime, terminal observations prevent the machine transition from being invoked again.

## 6.4 Typed and fresh occurrence acceptance

For a machine expecting sort \(T\), an occurrence token is accepted only if:

\[
\mathsf{token.sort}=T,
\]

its subject exists, its revision equals the current subject revision, and its domain-specific availability predicate holds.

In the schedule case, stale or occupied slots cannot reach the command effect.

## 6.5 Command-time authority

A successful product mutation implies that the required capability held at command interpretation time. UI availability and previous machine observations are insufficient.

## 6.6 Deterministic replay

For the implemented deterministic machines and handlers, replay of the same initial world and external input sequence produces equal:

- final machine state;
- final product world;
- terminal resolution;
- public observation.

This is tested over explicit scenarios and 300 generated runs.

## 6.7 Strong finite bisimulation

The flat and factored accept machines are compared over their complete reachable finite graphs. The checker examines all events declared by both machines at every related pair.

The passing result is specific to this finite model. It is not a theorem about arbitrary runtime callbacks or the larger product workflows.

# 7. Validation results

The packaged run produced the following results.

## 7.1 Automated tests

```text
21 tests
21 passed
0 failed
```

The tests cover:

- successful typed scheduling;
- wrong-sort rejection;
- stale selection rejection;
- commit-time revalidation;
- authority revocation;
- terminal absorption and single resolution;
- task promotion and stale action items;
- cancellable external requests and late responses;
- successful booking approval;
- deterministic replay;
- rewind and branch;
- portable session restoration;
- pointer-channel queueing;
- independent network-channel progress;
- transactional command failure;
- 250 randomized scheduling traces;
- finite machine audits;
- passing and failing bisimulation checks.

## 7.2 Finite-state results

The flat and factored accept machines each have:

```text
5 reachable states
20 labeled edges
2 terminal states
6 resolve-producing edges across all nonterminal diagnostic states
```

Their bisimulation relation contains five reachable state pairs. The broken machine diverges after one event:

```json
{
  "type": "choose",
  "sort": "project",
  "key": "p-wrong",
  "valid": true
}
```

The correct machine records a wrong-sort diagnostic; the broken machine emits a selected result.

## 7.3 Replay

```text
300 replay attempts
300 equal final states
300 equal worlds
300 equal resolutions
300 equal public observations
```

## 7.4 Stale and late-input experiments

The stale slot experiment terminates its step in `choosing-slot`, reports `stale-occurrence`, and emits zero product commands.

The late approval response arrives after cancellation. The machine remains `cancelled`, the booking remains `pending`, and one `event-ignored-terminal` trace row is recorded.

## 7.5 Channel composition

The manager experiment finishes recipient collection, promotes the queued scheduling session to pointer owner, and completes booking approval on the network channel. The two channels share the updated product world but maintain independent control states.

## 7.6 Local throughput observation

A local experiment ran 3,000 deterministic scheduling sessions. All 3,000 created events. The observed rate in the packaging environment was approximately 1,142 sessions per second with an average of 18 trace rows per session.

This number characterizes a small in-process fixture with cloned JSON state. It is not a production throughput guarantee and should not be compared directly with a DOM interaction rate.

## 7.7 Browser smoke test

A headless Chromium test exercises all tabs, including:

- scheduling and command completion;
- stale-token rejection;
- action-item promotion;
- cancellation plus late response;
- queued pointer ownership and independent booking approval;
- passing and failing bisimulation results;
- deterministic replay and serialization rendering.

# 8. Failure modes explored

## 8.1 Wrong semantic sort

A `<contact>` occurrence supplied to a `<slot>` request is rejected without leaving selection or issuing a command.

## 8.2 Missing or stale subject

Revision mismatch, deletion, prior promotion, and occupied slots are structured failures rather than accidental `undefined` access.

## 8.3 Time-of-check/time-of-use race

A token valid at selection can become invalid before confirmation. The machine checks again before emitting a command, and the command handler checks the expected revision again.

## 8.4 Revoked authority

Authority can disappear between observation and command interpretation. The command fails transactionally.

## 8.5 Duplicate or late response

A response delivered after terminal resolution is recorded but cannot change product state. A response with an unrelated request ID is ignored by a waiting machine.

## 8.6 Competing pointer workflows

The second workflow is queued under the selected policy instead of silently replacing the first continuation.

## 8.7 Behaviorally incorrect refactor

The broken accept machine demonstrates a state representation that appears similar but changes behavior. The bisimulation checker returns a concrete distinguishing event.

## 8.8 Hidden impurity

Cloning the world blocks direct mutation of durable product state, but it cannot prevent a machine from accessing global mutable variables, random numbers, network APIs, or the clock. Such behavior would undermine replay and must be prohibited by convention, static analysis, sandboxing, or a reified language.

# 9. API boundary for later composition

The machine subsystem imports four conceptual interfaces.

## 9.1 Typed occurrence provider

```js
listOccurrences(sort) -> OccurrenceToken[]
lookupOccurrence(token) -> Result<Subject, OccurrenceError>
```

P01 can supply semantic identities; P02 can supply mounted occurrence status; P03 can replace direct enumeration with compiled selectors and evidence.

## 9.2 Product command interpreter

```js
execute(world, command) ->
  { ok: true, world, value, events }
  | { ok: false, reason, details }
```

P05 can attach capabilities and authoritative evidence. A server-backed interpreter can preserve the same response protocol.

## 9.3 Observation renderer

```js
render(observation)
route(event)
```

React is only one renderer. P13 can add explanation and accessibility semantics.

## 9.4 Session scheduler

```js
start(machine, input, channelPolicy)
dispatch(channel, event)
deliver(session, request, response)
```

P12 can investigate replicated ownership and causal delivery.

## 9.5 P08 composition

P08 exports explicit link, pause, resume, repair, and conflict-resolution commands. P09 can wrap those commands in machines such as:

```text
choose source endpoint
choose target endpoint
choose reconciliation policy
issue create-link
wait for result
resolve or enter conflict workflow
```

The current P09 product fixture does not import the P08 runtime. The composition capsule records the intended adapter rather than creating a first-pass dependency.

# 10. Limitations and unresolved questions

## 10.1 Finite model restriction

The complete explorer and bisimulation checker require a finite event alphabet and reachable state graph. Product workflows contain entity IDs, revisions, and unbounded traces, so they are tested and sampled rather than completely explored.

## 10.2 Strong rather than weak bisimulation

The checker compares emitted effects exactly. It cannot hide internal bookkeeping transitions or compare systems that split one public step into several silent steps.

## 10.3 No nondeterminism

Every transition is deterministic. Races are represented as explicit event orderings. There is no branching scheduler, probability, or adversarial environment exploration.

## 10.4 No general hierarchy

The machine states are plain tagged records. The implementation does not provide nested statecharts, history, orthogonal regions, entry/exit actions, or formal priority semantics.

## 10.5 Effect vocabulary is fixed

The runtime recognizes four effect families. P10 should determine whether workflows should be authored through an extensible algebraic effect signature and compiled to or interpreted as machines.

## 10.6 Trace growth

Traces are retained in memory and include observations. A production system needs retention policies, indexing, redaction, secure audit separation, and perhaps event sourcing rather than a diagnostic array.

## 10.7 World cloning

The reference interpreter clones JSON state for transactional simplicity and transition isolation. Production integration should use immutable snapshots, transactions, patches, or a persistent store.

## 10.8 React adapter

The standalone HTML uses a minimal JSX runtime. It does not model React concurrent rendering, effect lifetimes, real accessibility focus, portal menus, or virtualized occurrences.

## 10.9 Liveness assumptions

The machine can wait forever for an external response. Cancellation is available, but no theorem guarantees that an external service responds or that a scheduler is fair.

# 11. Suggested second-pass experiments

1. **P02 + P09:** mount and unmount real occurrences during a pending selection; verify focus, virtualization, and stale DOM events.
2. **P03 + P09:** compile machine candidate observations from a selector AST and compare incremental candidate updates.
3. **P05 + P09:** carry revision-sensitive capability evidence into command effects and distinguish advisory from authoritative observations.
4. **P08 + P09:** implement link creation and conflict resolution as machines, including cancellation while repair is in flight.
5. **P10 + P09:** define one workflow in an algebraic interaction language, compile it to a machine, and compare traces by bisimulation or refinement.
6. **P11 + P09:** incrementally maintain observations and prove equality with full recomputation over generated traces.
7. **P12 + P09:** model two clients competing for pointer ownership and delivering duplicated or reordered external responses.
8. **P13 + P09:** generate accessible prompts and explanations from observation and transition evidence.
9. **P14 + P09:** mechanize the finite accept machine, terminal absorption, exactly-once resolution, and the flat/factored bisimulation.
10. **P15 + P09:** generate event traces from the finite graph and run the same conformance suite against multiple runtimes.

# 12. Reproduction

From the project root:

```bash
npm run test
npm run experiment
npm run build
python experiments/ui-smoke.py
```

The built artifact is:

```text
dist/p09-coalgebraic-interaction-machines.html
```

The artifact is self-contained and can be opened from the filesystem.

# Appendix A - File map

```text
README.md
composition-capsule.json
package.json
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
    ui.jsx
  core/
    machine.js
    manager.js
    modelcheck.js
    modelcheck.test.js
    product.js
    runtime.js
    runtime.test.js
    utils.js
    workflows.js
experiments/
  run.mjs
  results.json
  ui-smoke.py
  initial.png
  p09-ui.png
dist/
  authoring-bundle.js
  p09-coalgebraic-interaction-machines.html
docs/
  P09_IMPLEMENTATION_REPORT.md
  P09_IMPLEMENTATION_REPORT.pdf
```

# Appendix B - Representative state transitions

## B.1 Scheduling

```json
{
  "state": {
    "tag": "choosing-slot",
    "contactId": "c-sarah",
    "attempt": 1
  },
  "event": {
    "type": "choose-occurrence",
    "occurrence": {
      "sort": "slot",
      "subjectId": "slot-tu-1000",
      "revision": 1
    }
  },
  "next": {
    "tag": "confirming"
  },
  "effects": []
}
```

Confirmation emits:

```json
{
  "type": "world-command",
  "requestId": "schedule:c-sarah:slot-tu-1000:1",
  "command": {
    "type": "create-event-from-contact-slot",
    "contactId": "c-sarah",
    "slotId": "slot-tu-1000",
    "expectedSlotRevision": 1
  }
}
```

## B.2 External request and cancellation

```text
reviewing
  --submit / external-request--> waiting-approval
  --cancel / resolve(cancelled)--> cancelled
cancelled
  --external-response--> cancelled, no effects
```

## B.3 Channel queue

```text
pointer owner: compose-recipients
pointer queue: [schedule-contact]
network owner: booking-approval

compose completes
  -> schedule-contact promoted
booking-approval continues independently
```

# Appendix C - Selected references

- David Harel. "Statecharts: A Visual Formalism for Complex Systems." *Science of Computer Programming* 8(3), 1987, pp. 231-274. DOI: [10.1016/0167-6423(87)90035-9](https://doi.org/10.1016/0167-6423(87)90035-9).
- J. J. M. M. Rutten. "Universal Coalgebra: A Theory of Systems." *Theoretical Computer Science* 249(1), 2000, pp. 3-80. DOI: [10.1016/S0304-3975(00)00056-6](https://doi.org/10.1016/S0304-3975(00)00056-6).
- Li-yao Xia, Yannick Zakowski, Paul He, Chung-Kil Hur, Gregory Malecha, Benjamin C. Pierce, and Steve Zdancewic. "Interaction Trees: Representing Recursive and Impure Programs in Coq." *Proceedings of the ACM on Programming Languages* 4(POPL), Article 51, 2020. DOI: [10.1145/3371119](https://doi.org/10.1145/3371119).
- Alexandra Silva, Filippo Bonchi, Marcello Bonsangue, and Jan Rutten. "Generalizing Determinization from Automata to Coalgebras." *Logical Methods in Computer Science* 9(1), 2013. [arXiv:1302.1046](https://arxiv.org/abs/1302.1046).

# Appendix D - Claim discipline

The implementation supports the following evidence levels.

**Exhaustive for the declared finite model:** reachable-state exploration, deterministic transition comparison, terminal absorption, resolve-effect discipline, and the flat/factored bisimulation.

**Executable over generated traces:** replay equality, stale-token handling, command-time authority, cancellation, channel ownership, and randomized scheduling traces.

**Architectural intention only:** production React refinement, distributed ownership, mechanized coinduction, general workflow compilation, and complete product-suite behavioral equivalence.
