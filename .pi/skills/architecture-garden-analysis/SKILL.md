---
name: architecture-garden-analysis
description: Studies a concrete repository as an evidence-backed Software Architecture Garden entry, identifies reusable patterns and architecture debt, cross-correlates them with existing Garden projects and RAG/PBUI Pattern Zoos, derives restrained mathematical and computer-science foundations, proposes shared ecosystem vocabulary, and records implications for composable Go and JavaScript APIs. Use when asked to add a repository to the Architecture Garden, compare a project's architecture with the zoos, or build common pattern vocabulary across repositories.
---

# Architecture Garden Analysis

## Purpose

Create a repository-pinned architecture study that connects concrete implementation evidence to reusable ecosystem patterns. The output should help maintainers recognize one invariant under different project-local names without pretending that similar-looking structures are identical.

The default destination in this repository is:

```text
Research/Software Architecture Garden/<project-slug>/README.md
```

Read [the full playbook](references/PLAYBOOK.md) before beginning a substantial study. Draft from [the project-entry template](references/PROJECT-ENTRY-TEMPLATE.md). Validate with `scripts/validate_garden_entry.py`.

## Required qualities

A Garden entry must:

1. pin every claim to a repository path, commit, branch, worktree state, and analysis date;
2. inspect runtime code, public interfaces, tests, persistence, transports, build/release paths, and recorded failures—not only README prose;
3. explain the actual execution and authority flow before naming patterns;
4. assign each local pattern one maturity label—established, emergent, candidate ecosystem pattern, architecture debt, retired, or open correctness obligation—and separately grade every cross-project comparison as strong, partial, adjacent, negative, or non-equivalent;
5. compare semantic objects, laws, failure modes, and authority boundaries rather than matching vocabulary;
6. include exact, path-qualified Obsidian links for Garden and Zoo references;
7. distinguish canonical evidence, observations, projections, materializations, snapshots, cursors, and presentation values where relevant;
8. derive mathematics from concrete code behavior and state its operational consequence and limit;
9. identify concurrency, retry, idempotency, atomicity, authorization, lifecycle, and schema-evolution obligations;
10. propose common vocabulary, mathematical foundations, and API implications when concrete evidence supports them; otherwise state that no supported shared claim is available rather than forcing every project into one framework;
11. validate links and Markdown structure and receive substantive review before being called complete.

## Workflow

### 1. Establish the analysis contract

Record:

- repository and project slug;
- analysis purpose and audience;
- source snapshot and whether uncommitted work is included;
- likely comparison projects and Zoo chapters;
- expected output files;
- whether source modification is explicitly out of scope.

Default to read-only analysis of the target repository. Do not change the analyzed repository unless the user separately requests implementation.

### 2. Pin the source snapshot

Capture exact evidence:

```bash
git -C /path/to/repo rev-parse HEAD
git -C /path/to/repo branch --show-current
git -C /path/to/repo show -s --format='%cI%n%s' HEAD
git -C /path/to/repo remote get-url origin
git -C /path/to/repo status --short
```

If the worktree is dirty, say whether claims refer to committed source, working-tree source, or both. Never silently describe a moving checkout as a stable snapshot.

### 3. Map the concrete system

Read project instructions and primary docs, then trace at least one end-to-end path through source and tests. Inspect, as applicable:

- command/request ingress;
- typed values and schema ownership;
- handlers/interpreters and external effects;
- state ownership and persistence;
- events, journals, projections, reducers, and snapshots;
- concurrency, ordering, retry, cancellation, and terminal outcomes;
- adapters, transports, UI boundaries, Goja/JavaScript APIs;
- authorization and disclosure boundaries;
- build, packaging, deployment, and release;
- architecture tests, migrations, incidents, and debt.

Write the concrete runtime flow before abstracting it.

### 4. Extract evidence-backed pattern cards

For each candidate capture:

```text
Problem:
Concrete code shape:
Semantic objects:
Operation or relation:
Protected invariant/law:
Operational consequence:
Failure when violated:
Source files and tests:
Maturity:
Nearby Garden projects:
Nearby Zoo chapters:
Important non-equivalence:
```

One repository establishes local evidence. Ecosystem guidance requires comparison with an independent implementation under a comparable constraint.

### 5. Cross-correlate without flattening

Classify every comparison:

- **strong correspondence** — substantially the same objects, law, and failure;
- **partial correspondence** — a shared nucleus with missing or different obligations;
- **adjacent analogy** — useful explanation but not implementation evidence for the target pattern;
- **negative evidence** — a concrete bypass or failure demonstrating why the law matters;
- **non-equivalence** — similar representation or terminology with different semantics.

A registry is not authority. A snapshot is not always an immutable release. A UI event is not a mounted PBUI occurrence. An experiment coordinate is not a job invocation key. An append-only log is not automatically idempotent or event-sourced.

### 6. Derive restrained foundations

Use this order:

```text
concrete values and transitions
  -> sets/types
  -> functions/relations
  -> laws
  -> production consequence
  -> counterexample and limit
```

Relevant foundations often include:

- tagged sums and products;
- state machines and labeled transition systems;
- free event monoids and reducer folds;
- partial orders, prefix orders, closures, and high-water marks;
- temporal relations and as-of queries;
- idempotence, associativity, commutativity, and monotonicity;
- linearization points, serializability, and consistent cuts;
- noninterference and authority domination;
- interpreters, algebras, coalgebras, and explicit effects.

Do not introduce category theory unless it clarifies an API law, test oracle, admission rule, or composition boundary.

### 7. Propose common vocabulary

Build a table with:

| Proposed term | Project-local name | Invariant | Nearby ecosystem names | Difference retained |
|---|---|---|---|---|

Prefer terms that survive implementation changes. Preserve overloaded local names and explicitly state what must remain distinct.

### 8. Connect theory to API design

Where the repository exposes Goja, JavaScript, TypeScript, CLI, UI, or plugin APIs, derive practical consequences:

- represent intent as typed data rather than serialized callbacks;
- keep effects behind explicit interpreters;
- expose identity, revision, cursors, outcomes, and cancellation honestly;
- generate branded types and codecs from schemas;
- provide combinators only when their identity/associativity/replay laws are clear;
- hide wire details without destroying exact round-trip behavior;
- name recovery semantics explicitly (`snapshotThenLive`, `replayFrom`, etc.).

The theory should make APIs smaller and easier to compose, not decorate them with mathematical nouns.

### 9. Write and link the entry

Create the project directory and `README.md`. Keep a single substantive entry until the project contains enough independent subsystems to justify focused companion studies.

Every entry requires snapshot/evidence, architecture/runtime, maturity, debt/open obligations, and related-studies sections. Common vocabulary, mathematics, Zoo correlation, cross-project comparison, composable-API implications, and ecosystem-pattern sections are conditional: include them when evidence supports a useful claim, or state briefly why they are not applicable. Do not invent a formalization merely to satisfy a template.

Update `Research/Software Architecture Garden/README.md` with:

- an analyzed-project entry;
- only well-supported cross-correlation rows;
- explicit strength and limitations.

Do not edit Zoo chapters merely to manufacture bidirectionality. Add Zoo backlinks only when the project supplies useful evidence for that exact chapter.

### 10. Validate and review

From the repository root:

```bash
python3 .pi/skills/architecture-garden-analysis/scripts/validate_garden_entry.py \
  "Research/Software Architecture Garden/<project-slug>/README.md"
```

Run the validator's regression suite after changing the skill itself:

```bash
python3 .pi/skills/architecture-garden-analysis/scripts/test_validate_garden_entry.py -v
```

Run focused tests in the analyzed repository when practical. Report the exact command and distinguish a test failure from an invocation/cwd failure.

Then review for:

- false equivalence or overclaim;
- citations that resolve but do not support the clause;
- laws stronger than implementation evidence;
- hidden partial commits and stale-write races;
- unsupported exactly-once, causal-order, snapshot, or authorization claims;
- speculative mathematics presented as implemented behavior;
- source paths or commit metadata that have drifted.

## Evidence hierarchy

Prefer evidence in this order:

1. runtime code and public interfaces;
2. tests asserting the claimed invariant;
3. active consumers and deployment configuration;
4. persistence schemas, build and release workflows;
5. implementation diaries and design documents;
6. git history explaining migrations;
7. README prose, comments, and naming.

Documentation can explain intent. It cannot by itself prove runtime behavior.

## Stop conditions

Do not call an entry complete until:

- source snapshot metadata is exact;
- at least one runtime path is traced end to end;
- every strong claim cites implementation or tests;
- partial and negative correspondences are labeled;
- mathematical symbols are defined from concrete values;
- architecture debt and open laws are visible;
- internal links and headings resolve;
- the Garden root links back to the entry;
- focused validation passes or failures are reported honestly;
- temporary research artifacts are removed or deliberately retained outside project documentation.
