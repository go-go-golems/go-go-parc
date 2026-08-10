# Software Architecture Garden Project Analysis Playbook

## 1. Purpose

A Software Architecture Garden entry is an evidence-backed study of how one repository actually works and what its design contributes to the wider ecosystem. It is not a package inventory, a generic architecture review, or an attempt to make every project conform to one master design.

Its unit of study is:

```text
real engineering constraint
  + concrete implementation shape
  + protected invariant
  + executable evidence
  + observed failure or limit
  + comparison with another project
```

The Garden supports three related goals:

1. preserve repository-specific architecture knowledge;
2. recognize shared patterns despite fragmented vocabulary;
3. derive small mathematical and computer-science foundations that improve composition, validation, and API design.

The analysis must move in that order. Starting from abstract vocabulary and imposing it on a repository produces attractive but unreliable correlations.

## 2. Define the research contract

Before reading source, write a short internal contract.

| Field | Question |
|---|---|
| Repository | Which checkout and remote are being studied? |
| Snapshot | Which commit, branch, date, and worktree state support the claims? |
| Scope | Whole repository or named subsystem? |
| Audience | New contributor, ecosystem maintainer, API designer, or formal-methods reader? |
| Goal | Local explanation, cross-project comparison, shared vocabulary, or implementation planning? |
| Evidence standard | Which claims require code, tests, consumers, or deployment evidence? |
| Non-goals | Is source modification, benchmarking, or downstream auditing excluded? |
| Deliverable | One README, several focused studies, root index changes, or Zoo backlinks? |

A useful default contract is:

```text
Study the repository at one pinned source snapshot. Trace its principal runtime
and persistence paths. Identify established patterns, debt, and open laws.
Compare only against Garden/Zoo structures with matching invariants. Write one
professional onboarding entry with restrained mathematics and practical API
consequences. Do not modify the analyzed repository.
```

## 3. Pin provenance before interpretation

Run:

```bash
git -C "$REPO" rev-parse HEAD
git -C "$REPO" branch --show-current
git -C "$REPO" show -s --format='%cI%n%s' HEAD
git -C "$REPO" remote get-url origin
git -C "$REPO" status --short
```

Record the results in frontmatter and a visible snapshot table.

### Dirty worktrees

A dirty worktree creates two possible evidence sets:

- **committed snapshot:** claims refer to `HEAD`; uncommitted work is excluded;
- **working snapshot:** claims include current files; record dirty state and do not imply reproducibility from the commit alone.

Prefer the committed snapshot unless the user explicitly wants active work studied. If active work matters, distinguish committed behavior from uncommitted observations sentence by sentence.

### Source drift

Before resuming an older entry, compare the current target `HEAD` to the recorded commit. A study does not become false when the target advances, but it becomes historical evidence and should not be described as current without revalidation.

## 4. Build a system evidence map

### 4.1 Read project instructions first

Look for:

```text
AGENT.md
AGENTS.md
README.md
CONTRIBUTING.md
go.mod / package.json
Makefile
.github/workflows
Dockerfile / deploy /
ttmp / docs / design records
```

Project instructions define repository boundaries and expected validation. Design docs guide navigation, but implementation and tests decide current behavior.

### 4.2 Inventory by responsibility

Do not enumerate every file. Identify owners for:

| Responsibility | Questions |
|---|---|
| Ingress | Where do commands, requests, jobs, or messages enter? |
| Identity | What names semantic entities, requests, runs, sessions, artifacts, or occurrences? |
| Schema | Who owns payload shape and protocol evolution? |
| Authority | Which component may commit state or perform effects? |
| State | Which facts are canonical, derived, cached, local, transient, or external? |
| Execution | How are long-running work, cancellation, deadlines, resources, and retries handled? |
| Evidence | What records what happened, why, and under which coordinate? |
| Projection | Which read models, UI values, reports, or snapshots are derived? |
| Persistence | What is transactional, append-only, versioned, rebuildable, or mutable? |
| Transport | What crosses process, language, browser, plugin, or toolkit boundaries? |
| Extension | How are handlers, modules, providers, commands, or renderers registered? |
| Security | Where are identity, authorization, disclosure, tenant, and secret boundaries enforced? |
| Delivery | How are assets built, binaries packaged, images published, and deployments reconciled? |
| Validation | Which tests protect behavior, contracts, structure, migration, and deployment? |

### 4.3 Trace complete runtime paths

A complete path is more valuable than ten disconnected interfaces. Typical paths:

```text
command -> handler -> effect -> event -> persistence -> projection -> transport
```

```text
configuration -> plan -> worker -> artifact -> validator -> promotion -> activation
```

```text
identity provider -> verified principal -> app projection -> tenant store -> response
```

```text
source document -> parser -> canonical map -> snapshot -> request handler
```

For each transition record:

- input and output types;
- authority owner;
- failure behavior;
- transaction or lock boundary;
- retry identity;
- tests exercising the seam.

## 5. Separate object families before naming patterns

Many false correlations begin by collapsing related records.

### 5.1 State and evidence families

Ask whether each value is:

- command or intent;
- canonical domain entity;
- event or occurrence record;
- derivation/provenance object;
- measurement/observation;
- mutable workflow decision;
- read model or projection;
- materialized entity;
- snapshot or release;
- cursor, revision, ordinal, or epoch;
- presentation value or mounted occurrence;
- audit/evidence record;
- external effect result.

These categories can share fields while requiring different identity and authority laws.

### 5.2 Identity families

Do not use “ID” as a complete analysis. Distinguish:

- semantic identity;
- occurrence identity;
- artifact/content identity;
- request/idempotency identity;
- run/attempt identity;
- transport connection identity;
- release/snapshot identity;
- projection revision;
- authorization principal or tenant identity.

For each, ask what mutation must preserve or change it.

### 5.3 Graph families

Similar graph data structures may encode:

- execution dependency;
- provenance/derivation;
- invalidation support;
- UI binding;
- authorization domination;
- deployment ownership.

Traversal code can be shared while edge meaning remains separate.

## 6. Extract pattern cards

Create one card per candidate:

```markdown
## Candidate: <working name>

- Constraint:
- Runtime path:
- Semantic objects:
- Authority owner:
- Operation/relation:
- Required law:
- Operational consequence:
- Concrete failure without the law:
- Source paths/symbols:
- Tests/deployment evidence:
- Maturity:
- Comparison targets:
- Non-equivalence:
- Possible shared name:
```

### Counterfactual test

Ask:

> What specifically becomes incorrect, ambiguous, insecure, stale, or unrecoverable if this law is removed?

If the answer is only “the system becomes less elegant,” the candidate is not yet a core architecture pattern.

### Deletion test

A shared ecosystem abstraction is promising when it can delete duplicated semantic authority. If it adds an interface while every consumer keeps its own interpretation, it is vocabulary—not yet a reusable kernel.

## 7. Assign maturity and evidence strength

### 7.1 Garden maturity

| Label | Meaning |
|---|---|
| **Established** | Important runtime paths use it successfully; source, tests, and active use agree. |
| **Emergent** | A useful repeated shape exists, but ownership or contract remains implicit. |
| **Candidate ecosystem pattern** | One strong implementation and credible independent comparison target exist. |
| **Architecture debt** | Duplicate authority, obsolete paths, false contracts, or failure-prone structure remain active. |
| **Retired** | A former pattern has a named replacement and migration evidence. |
| **Open correctness obligation** | The design promises a law that current implementation or tests do not fully establish. |

### 7.2 Cross-correlation strength

| Relation | Required evidence |
|---|---|
| **Strong** | Same semantic roles, same important law, same failure class. |
| **Partial** | Shared nucleus, with explicit missing/different obligations. |
| **Adjacent** | Explanatory resemblance only; not confirmation. |
| **Negative** | Observed bypass/failure demonstrates why the law matters. |
| **Non-equivalent** | Surface similarity hides different objects, authority, or mathematics. |

Never present a generated thesis, architecture comment, or repeated branch as independent implementation evidence.

## 8. Cross-correlate projects systematically

For each candidate, compare at four levels.

### 8.1 Object correspondence

Can project-local objects map without changing their role?

```text
backend event -> canonical occurrence record
UI event      -> live projected observation
```

This does not imply:

```text
UI event == PBUI mounted occurrence
```

### 8.2 Law correspondence

Do operations satisfy the same equations or ordering obligations?

```text
append-only event fold: ordered, associative by prefix regrouping
variant evidence join: associative, commutative, idempotent
```

Both combine many inputs, but one is order-sensitive and the other is not.

### 8.3 Failure correspondence

Do violations fail similarly?

- stale snapshot cut: client loses or duplicates updates;
- stale authorization: forbidden effect occurs;
- stale dependency closure: invalid artifact is reused;
- stale UI binding revision: wrong shared selection commits.

Different failures usually indicate different patterns even when implementation machinery overlaps.

### 8.4 Authority correspondence

Who is allowed to decide?

- registry: discovers and validates names;
- interpreter: performs an effect;
- validator: admits an artifact;
- reducer: computes derived state;
- service transaction: commits domain truth;
- UI: proposes intent and renders results.

If two systems place authority in different components, record the difference.

## 9. Build common vocabulary

A useful vocabulary table has five columns:

| Proposed term | Local term | Invariant | Related terms | Difference retained |
|---|---|---|---|---|

### Naming rules

Prefer names that:

- describe semantic role rather than implementation technology;
- survive language and storage changes;
- imply one authority boundary;
- make invalid substitutions sound wrong;
- can be used in tests and API documentation.

Avoid names that:

- claim universality from one project;
- use “semantic,” “canonical,” “proof,” or “event” without defining the observation boundary;
- conflate identity with revision;
- conflate evidence with truth;
- conflate discovery with authority;
- conflate snapshots, releases, and caches.

### Vocabulary promotion

A term becomes ecosystem vocabulary gradually:

```text
local name
  -> comparison term
  -> candidate shared term
  -> applied in another project
  -> established ecosystem term
```

Keep source-local aliases visible throughout that progression.

## 10. Derive mathematical foundations

### 10.1 Start from values

Bad sequence:

```text
“This is a coalgebra.” -> search for something stateful
```

Good sequence:

```text
running job emits one observation and a continuation
  -> W -> E × W + O
  -> coalgebraic unfolding
  -> terminal uniqueness and cancellation laws
```

### 10.2 Core mathematical toolkit

#### Tagged sums

Use for disjoint outcomes, commands, events, or protocol frames:

$$
O=\mathrm{Success}+\mathrm{Rejected}+\mathrm{Cancelled}+\mathrm{Failed}.
$$

Operational payoff: exhaustive handling and no ambiguous boolean/error combinations.

#### Products and scoped decomposition

Use when independent state components coexist:

$$
S=\prod_{i\in I}S_i.
$$

Operational payoff: actions in distinct scopes can commute if they modify disjoint components.

#### Free event monoid and fold

A finite event history is a word $H\in E^*$:

$$
\operatorname{fold}(S_0,xy)
=
\operatorname{fold}(\operatorname{fold}(S_0,x),y).
$$

Operational payoff: replay and incremental continuation agree when the reducer and dependencies are deterministic.

Do not infer commutativity. Ordered histories are usually noncommutative.

#### Idempotence

$$
f(f(x))=f(x).
$$

Operational payoff: duplicate delivery or retry has no additional declared effect. State the exact key and observation boundary; an idempotent insert does not make a command handler idempotent.

#### Monotonicity and high-water marks

$$
x\le y\Longrightarrow f(x)\le f(y).
$$

Operational payoff: cursors and evidence sets do not move backward. A monotone cursor can still lie about missing materialization if advancement is not atomic with apply.

#### Prefix order and consistent cuts

$$
x\preceq y \iff \exists z:\;xz=y.
$$

Operational payoff: snapshots and suffix replay can state exactly which observations are included.

#### Closure

$$
C(C(X))=C(X),\quad X\subseteq C(X).
$$

Operational payoff: invalidation and dependency analysis reach every affected artifact without repeatedly expanding an already closed set.

#### Partial orders and admission

Use predicates for hard feasibility before preference:

$$
\mathrm{Eligible}(x)=\bigwedge_i P_i(x).
$$

Operational payoff: product preference cannot compensate for failed safety, custody, authorization, or completeness constraints.

#### Noninterference and domination

State which protected input changes must not alter which observations, and ensure every path to an effect crosses authorization.

Operational payoff: one adapter cannot bypass policy enforced only by another.

#### Linearizability and serializability

Identify the instant at which an operation takes effect, or prove concurrent execution observationally equivalent to an allowed serial order.

Operational payoff: assigned sequence numbers and applied state cannot disagree under concurrency.

#### Temporal relations

Versioned entities support:

$$
\operatorname{valueAt}(k,n)
=
\arg\max_{v.\mathrm{ordinal}\le n}v.
$$

Operational payoff: as-of snapshots and audits reconstruct one declared point in history.

### 10.3 State the abstraction limit

Every mathematical section should answer:

1. What code values do the symbols denote?
2. Which law is actually tested or enforced?
3. What production behavior follows?
4. Which stronger result is **not** established?

Examples:

- protobuf validation establishes payload-shape admission, not truth;
- sequence ordinals establish local order, not global causality;
- immutable images establish delivery identity, not behavior-complete releases;
- append-only storage establishes retained history, not exactly-once execution;
- a projection interface permits deterministic folds but does not enforce purity.

## 11. Audit operational laws

### Ordering

- Is order global, partitioned, causal, or merely arrival order?
- Who assigns it?
- Can assignment and application reorder?
- Are stale writes rejected?
- Are overflows and gaps explicit?

### Retry and idempotency

- What stable key recognizes a retry?
- Is identity bound to arguments, actor, tenant, and observation boundary?
- Does duplicate handling compare full content?
- Can the same message receive a new sequence number?
- Is replay producer-free, or can projectors call external systems?

### Transactions

- Which writes commit together?
- Are event, projection, cursor, and audit atomic?
- Does fanout happen before or after durable commit?
- Can a monotone cursor advance past missing state?
- Is recovery automatic, explicit, or absent?

### Snapshots

- What authorities are included?
- Is the read a database-consistent cut?
- Can returned rows be newer than the declared cursor?
- How are concurrent live updates buffered or replayed?
- Is old snapshot cleanup safe for active readers?

### Authorization

- Is policy checked in the authoritative service transaction?
- Can CLI, REST, Widget, plugin, or automation paths bypass it?
- Does authorization dominate remote disclosure as well as final mutation?
- Are scope IDs routing partitions or actual security boundaries?

### Lifecycle

- Are cancellation and terminal outcomes explicit?
- Can two terminal events occur?
- Who owns cleanup?
- Are stale goroutines, callbacks, leases, and registrations fenced?

## 12. Connect foundations to API design

Theory is successful when it simplifies APIs and review.

### Typed intent APIs

Prefer:

```javascript
await session.commands.rename({ subject, expectedRevision, title })
```

over callbacks serialized through transports or UI-owned mutation logic.

### Snapshot and stream APIs

Prefer explicit recovery semantics:

```javascript
for await (const item of session.snapshotThenLive({ sessionId })) {
  // Snapshot | LiveEvent | Overflow | Closed
}
```

over a generic subscription whose baseline, replay, and gap behavior are hidden.

### Generated branded coordinates

Use distinct TypeScript brands or wrappers for:

```text
SemanticId
OccurrenceId
SessionId
Revision
EventOrdinal
ProjectionCursor
SnapshotCut
```

The goal is to prevent accidental substitution, not to add runtime ceremony.

### Lawful combinators

Candidate combinators need laws:

- product of independent projections;
- sequential command programs;
- retry with stable request identity;
- filtered event streams preserving coordinates;
- replay from a declared checkpoint;
- explicit cancellation and terminal outcomes.

Do not provide a generic `compose` until its identity, associativity, authority, and failure behavior are known.

## 13. Write the Garden entry

Use `PROJECT-ENTRY-TEMPLATE.md` as a starting point.

### Single entry versus several studies

Start with one `README.md`. Split into focused documents only when:

- subsystems have independent runtime and evidence paths;
- one document cannot explain them coherently;
- each subdocument has a distinct central question;
- the README remains an overview rather than a table of contents dump.

### Required core and conditional sections

Every entry must contain, in narrative order:

1. repository purpose and why it belongs in the Garden;
2. source snapshot and evidence scope;
3. concrete architecture and at least one runtime path;
4. maturity assessment;
5. architecture debt and open obligations;
6. related studies.

Add candidate shared vocabulary, mathematical/CS foundations, Zoo correlation, cross-project comparison, composable-API implications, and candidate ecosystem patterns when concrete evidence supports them. If one of these is expected by the analysis contract but no supported claim exists, say so explicitly instead of manufacturing an abstraction. The validator treats these as conditional sections and warns when they are absent; a warning is a review prompt, not a demand to add unsupported content.

### Diagrams

Mermaid diagrams should show owners and transitions, not generic boxes. Use different nodes for canonical records, derived projections, mutable pointers, external effects, and clients.

### Source citations

For Garden/Zoo material use path-qualified wikilinks with exact headings. For an external checkout, record repository-relative code paths and symbols in prose/frontmatter. Do not create broken vault links to files outside the vault.

## 14. Update the Garden root carefully

Add:

- one concise analyzed-project paragraph;
- cross-correlation rows only for claims the entry substantiates;
- strength and limitation in the row itself.

Do not turn the root table into a complete project summary. The project entry owns detail.

Zoo chapter backlinks are optional. Add them when the repository provides strong, useful implementation or counterexample evidence for that exact chapter. A link that merely repeats vocabulary reduces trust.

## 15. Validate

Run:

```bash
python3 .pi/skills/architecture-garden-analysis/scripts/validate_garden_entry.py \
  "Research/Software Architecture Garden/<slug>/README.md"
```

After changing the skill or validator, run its regression suite:

```bash
python3 .pi/skills/architecture-garden-analysis/scripts/test_validate_garden_entry.py -v
```

Also run:

```bash
git diff --check -- \
  "Research/Software Architecture Garden/README.md" \
  "Research/Software Architecture Garden/<slug>/README.md"
```

When practical, run focused tests in the target repository from its root:

```bash
cd /path/to/target
GOWORK=off go test ./relevant/package/... -count=1
```

An invocation from the wrong directory is an invocation failure, not a test failure. Correct it and report the final evidence accurately.

## 16. Substantive review checklist

Ask a fresh reviewer to inspect the actual entry and cited evidence.

### Evidence

- Does every strong claim have code/test evidence?
- Does each deep link support the exact clause?
- Are docs being treated as intent rather than runtime proof?
- Are repeated artifacts counted once?

### Semantics

- Are commands, events, observations, projections, entities, and snapshots distinct?
- Are identity and revision separate?
- Are routing scopes confused with authorization scopes?
- Are release roots confused with ordinary immutable artifacts?

### Mathematics

- Are symbols introduced from code values?
- Does the operation satisfy the claimed laws?
- Is an ordered fold incorrectly called commutative?
- Is a local sequence incorrectly called causal order?
- Is a schema witness incorrectly called a correctness proof?

### Concurrency and failure

- Is the claimed linearization point real?
- Can ordinal assignment and apply reorder?
- Can stale writes overwrite newer state?
- Are snapshot cursor and rows one consistent cut?
- Can retries allocate a fresh identity?
- Can one adapter bypass policy?
- Do cancellation and cleanup race?

### Composition and APIs

- Does a proposed common interface remove duplicate authority?
- Do combinators preserve identity, order, evidence, and effects?
- Is advanced theory earning its implementation cost?
- Are JS APIs simpler because of the model?

## 17. Completion criteria

A study is complete when:

- snapshot metadata is reproducible;
- required core sections are present and conditional sections are included only when evidence supports them;
- architecture is explained through real runtime paths;
- patterns include failures and limits;
- cross-project relations are graded, not binary;
- vocabulary preserves important distinctions;
- mathematics yields concrete laws or tests;
- API implications are practical and restrained;
- architecture debt remains visible;
- links, headings, frontmatter, fences, and math validate;
- focused target tests pass or failures are documented;
- Garden root navigation is updated;
- independent review finds no unsupported strong claims.
