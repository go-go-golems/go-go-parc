---
title: PCA-Z80 Garden — Shared Research and Subentry Guidelines
aliases:
  - PCA-Z80 intern research protocol
  - PCA-Z80 pattern authoring guidelines
status: active
type: architecture-garden-research-guideline
created: 2026-08-29
repository: /home/manuel/code/wesen/2026-08-28--pca-gatemate
repository_commit: c07e700652732cd7264af6e2473eb1c6e1f20cc9
tags:
  - architecture-garden
  - pca-z80
  - research-guidelines
  - textbook-authoring
  - evidence
related_notes:
  - "[[Research/Software Architecture Garden/pca-z80/index]]"
  - "[[Research/Software Architecture Garden/README]]"
---

# Shared Research and Subentry Guidelines

This document is the common research and writing contract for every PCA-Z80 Garden entry. Read it before the pattern-specific brief. The goal is not to produce six persuasive essays with attractive names. The goal is to determine what the code establishes, connect it to relevant prior work, expose its limits, and teach the resulting structure precisely enough that another engineer could recognize or reject it in a different system.

> [!summary]
> - Pin evidence before interpreting it.
> - Read complete runtime paths and tests, not isolated symbols.
> - Use primary external sources whenever possible and record provenance.
> - Distinguish patterns, tactics, idioms, checks, failures, and open obligations.
> - Write foundational, concrete, analogy-free textbook prose.
> - A local implementation produces a local pattern candidate; comparison is required before ecosystem guidance.

## 1. Deliverables

Each assigned expressive pattern produces one study under `pca-z80/designs/`. Supporting work may produce subentries under `idioms/` or `checks/`, but only when the material justifies an independent page.

Every researcher must also contribute source provenance to:

```text
Research/Software Architecture Garden/pca-z80/sources/SOURCES.md
```

If the file does not yet exist, the first researcher creates it using the source-ledger format below. Downloaded files belong under `sources/` when licenses and access permit. Otherwise preserve a clean Markdown snapshot, bibliographic metadata, and stable URL.

## 2. Freeze the research snapshot

Before reading architecture into the code, record:

```bash
cd /home/manuel/code/wesen/2026-08-28--pca-gatemate
git rev-parse HEAD
git branch --show-current
git status --short
git remote get-url origin
git show -s --format='%H%n%cI%n%s'
```

The entry frontmatter must contain:

- `repository`;
- `repository_commit`;
- `repository_branch`;
- `repository_worktree`;
- `analyzed` date;
- `pattern_maturity`;
- `related_files`.

If the worktree is dirty, either stop and establish why, or state exactly which uncommitted files affect the analysis. Never cite “current code” without a commit or worktree statement.

## 3. Evidence hierarchy

Use evidence in this order:

1. Runtime RTL, public types, generated artifacts, and board constraints.
2. Tests that assert protocol or architectural behavior.
3. Build commands, synthesis reports, route reports, and physical captures.
4. Active top-level composition and firmware consumers.
5. Design documents and chronological diary entries.
6. Git history explaining why a boundary changed.
7. Comments and names, used as intent evidence only.

A design document can explain why code exists. It cannot prove that the current code still behaves that way. A utilization line can prove allocation. It cannot prove firmware contents or execution.

## 4. Required local investigation

### 4.1 Read full paths

Do not stop after finding the named module. Trace at least one complete path:

```text
firmware instruction
→ decode FSM request
→ object bus or master adapter
→ router path
→ slave adapter
→ object acceptance
→ response path
→ decode state update
→ test or physical observation
```

For synthesis-oriented patterns, trace:

```text
source representation
→ assembler/generated artifact
→ Yosys mapping
→ primitive/netlist evidence
→ nextpnr placement/routing
→ packed bitstream
→ board observation
```

### 4.2 Read focused tests

Tests reveal the protected contract. Record:

- which behavior the test asserts;
- which behavior it merely happens to exercise;
- whether it tests positive, negative, reset, stall, and duplicate paths;
- whether it runs direct RTL, mesh RTL, or synthesized cells;
- whether a failure produces a reliable nonzero exit.

### 4.3 Inspect history selectively

Use `git log -- <file>` and `git show <commit>` when a current boundary has a non-obvious shape. Do not write a chronological commit summary. Use history to answer a specific question, such as why packet data must be returned for ALU write-like requests or why coordinates narrowed to two bits.

### 4.4 Reproduce one bounded experiment

Every expressive pattern entry must run or adapt at least one bounded experiment. Examples:

- hold a request after acknowledgement and count side effects;
- corrupt response metadata and observe protocol error behavior;
- reorder placement input and compare exact output bytes;
- synthesize a memory shape and inspect primitive mapping;
- compare route congestion after a width/topology change;
- measure cycles for direct versus mesh execution.

Store reusable experiments in the PCA-Z80 ticket's numbered `scripts/` directory or in a committed Garden `sources/`/experiment location. Do not leave the only copy in `/tmp`.

## 5. External research protocol

External research is mandatory. It should explain the lineage, alternatives, and limits of the local pattern—not decorate the introduction with citations.

### 5.1 Search sequence

1. Start from vocabulary in the local invariant, not the proposed pattern title.
2. Search for primary papers, standards, vendor manuals, and tool documentation.
3. Find one survey or textbook that locates the mechanism among alternatives.
4. Find at least one independent implementation or case study.
5. Search explicitly for counterexamples, limitations, or failure conditions.
6. Revisit the pattern name after research; rename it if literature uses a stronger term.

### 5.2 Source quality tiers

| Tier | Examples | Expected use |
|---|---|---|
| Primary | Standards, original papers, official tool/vendor manuals, source repositories | Support protocol, algorithm, and tool claims |
| Strong secondary | University texts, peer-reviewed surveys, established technical books | Establish vocabulary and comparison space |
| Implementation evidence | Maintained open-source RTL, test suites, synthesis examples | Compare concrete design shapes |
| Tertiary | Wikipedia, blog posts, forum answers | Discovery only; verify important claims elsewhere |

Do not cite generated search summaries as sources. Follow them to the underlying document.

### 5.3 Minimum external evidence per expressive pattern

Each pattern study must include:

- at least two primary sources;
- at least one strong secondary source;
- at least one independent implementation or comparison project;
- at least one source that complicates or limits the proposed pattern.

More citations are not automatically better. Each cited source must support a specific sentence, distinction, algorithm, or failure claim.

### 5.4 Source ledger

Each `SOURCES.md` entry should contain:

```markdown
## NN — Title

- **Kind:** paper | standard | manual | source repository | survey | article
- **Authors/organization:** ...
- **Published/version:** ...
- **URL:** ...
- **Retrieved:** YYYY-MM-DD
- **Local file:** `sources/...` or `N/A`
- **SHA-256:** ... or `N/A`
- **Why retained:** the exact research question it informs
- **Claims used:** entry section(s) and precise claim
- **Caveats:** version, scope, license, or authority limits
```

Use stable publication pages or repository permalinks when possible. For source code, pin a commit or release tag.

## 6. Pattern-level taxonomy

Classify each finding before giving it a page.

### Design pattern

A recurring problem, forces, structural solution, invariants, consequences, and evidence. This is the level of the six assigned studies.

### Tactic

A localized architectural choice that supports a pattern, such as returning a response for every operation or narrowing coordinate width.

### RTL idiom

A recognizable code shape such as a `captured` bit, flattened packed slicing, or an elaboration-time `generate` branch.

### Verification check

An executable observation that protects a claim, such as conservation counters or primitive INIT inspection.

### Failure study

A concrete historical failure and the boundary that caught it. A failure study may produce a candidate pattern, but the failure alone is not the pattern.

### Open correctness obligation

A promised law not fully established by the implementation or tests. State the missing evidence and operational consequence.

If an item can be explained fully in one subsection of its parent pattern, do not create a separate page.

## 7. Textbook-authoring contract

### 7.1 Foundational first

Open with what the reader should understand and why the problem exists. Do not begin with a file inventory or pattern name.

Good:

> An acknowledgement can report several different events: a link accepted a packet, an object performed a mutation, or a processor may advance its state. The mesh design must keep these events separate because they occur at different clocks and imply different correctness guarantees.

Weak:

> PCA-Z80 uses the End-to-End Semantic Completion pattern. The files involved are...

### 7.2 Developed prose

Paragraphs should develop one thought: claim, mechanism, consequence. Avoid a sequence of one-sentence declarations that merely restate headings.

### 7.3 Concrete evidence

Show actual structures:

- real fields from `bus_req_t` or `msg_t`;
- real state transitions;
- generated placement output;
- test output or transaction counts;
- synthesis resources and routed timing;
- physical byte captures.

Explain what the evidence proves and what it does not prove.

### 7.4 No analogies

Do not compare routers to traffic, adapters to translators, objects to rooms, or pipelines to factories. Use state diagrams, message sequences, field tables, and traces.

### 7.5 Rhythm

Use prose for reasoning, tables for comparisons, diagrams for topology/sequence, code for contracts, and bullets for complete takeaways. Lists should not replace explanation.

### 7.6 Direct claims

Remove filler and hedging:

- “In the evolving landscape...”
- “It is worth noting...”
- “One might observe...”
- “Clearly...”
- “As you can see...”
- “This elegant pattern...”

State the claim and provide evidence.

## 8. Required study structure

Each expressive pattern entry should use this order unless evidence demands a better one:

1. **Opening purpose.** What should the reader understand?
2. **Engineering problem.** What fails or becomes coupled without the pattern?
3. **Forces.** Correctness, latency, area, tool support, observability, reuse, or complexity in tension.
4. **Concrete PCA-Z80 shape.** Files, fields, states, generated artifacts, and runtime path.
5. **One complete trace.** Step-by-step request, build, or observation.
6. **Invariant.** State it in prose and, where useful, temporal logic, equations, or pseudocode.
7. **Why it works.** Connect structure to invariant.
8. **Observed failures.** Exact commands/errors and the correction.
9. **External lineage and alternatives.** Literature terminology and competing designs.
10. **Applicability.** When another project should use it.
11. **Non-applicability.** When the trade-off is wrong.
12. **Consequences.** Benefits, costs, scaling limits, and new obligations.
13. **Maturity assessment.** Local evidence versus ecosystem status.
14. **Candidate guidance.** Conservative wording suitable for comparison.
15. **Reproduction and review.** Commands and starting symbols.
16. **Key points.** Complete-sentence summary bullets.
17. **References.** Local evidence and external sources.

## 9. Required diagrams and tables

Every expressive pattern entry includes at least:

- one architecture, state, sequence, or evidence-flow diagram;
- one comparison table;
- one real code/pseudocode block;
- one failure or evidence table.

Diagrams must reflect the project. Do not paste generic protocol diagrams that omit PCA-Z80's adapters, acknowledgement boundaries, or generated coordinates.

## 10. Pattern maturity and claim discipline

Use the Garden maturity vocabulary exactly.

A single strong implementation may be:

- **Established locally** when source, tests, and active physical/runtime use agree.
- **Candidate ecosystem pattern** when the invariant appears transferable but comparison is incomplete.
- **Open correctness obligation** when the architecture promises more than tests establish.

Do not promote a candidate because external literature describes a similar mechanism. Garden promotion requires another concrete project under comparable forces.

Separate these sentence forms:

- **Observed:** “Router2 seed 1 did not converge within 1,200 seconds.”
- **Derived:** “Packet width contributed materially because narrowing coordinates reduced LUTs and enabled closure.”
- **Risk:** “Larger meshes may require pipelining.”
- **External claim:** “Source X defines latency-insensitive design as...”

## 11. Subentry rules

A supporting subentry should answer one narrow implementation question and link upward to exactly one primary pattern, while acknowledging secondary relations.

Required subentry shape:

1. Parent pattern and role: tactic, idiom, check, or failure study.
2. Intent and context.
3. Minimal RTL or command template.
4. Invariants and preconditions.
5. Failure modes.
6. Tests or observations.
7. Toolchain implications.
8. Reuse boundary.
9. Links to parent and sibling entries.

A subentry must not repeat the entire pattern. For example, “Capture-Once Slave” explains the local exactly-once code shape; “End-to-End Semantic Completion” explains why that shape participates in a larger completion protocol.

## 12. Research diary

Each intern keeps a short chronological research diary in their working branch or assigned task document. Record:

- exact prompt/assignment;
- files read;
- searches and sources retained;
- commands and outputs;
- failed hypotheses;
- terminology changes;
- experiments;
- what warrants review.

A polished Garden entry must not erase failed experiments that changed the conclusion.

## 13. Review procedure

### Technical review

The reviewer traces one end-to-end path and checks every field/state claim against code. Commands must be reproducible from a clean checkout or state their prerequisites.

### Source review

The reviewer opens every external link used for an important claim and checks that the cited source actually supports it. Sources must be pinned by version, date, DOI, or commit when possible.

### Textbook review

The reviewer asks:

1. Does the reader learn the problem before the solution name?
2. Does each abstract claim have code, trace, diagram, or source evidence?
3. Are alternatives and trade-offs explained?
4. Are analogies absent?
5. Are bullets complete thoughts?
6. Does the conclusion state applicability and non-applicability?

### Garden review

The reviewer checks that local evidence is not mislabeled as ecosystem guidance and that shared terms match existing Garden vocabulary where invariants genuinely coincide.

## 14. Validation checklist

Before commit:

```bash
# In the vault
python3 - <<'PY'
# Parse YAML frontmatter, check balanced fences, and verify local wikilink targets.
PY

git diff --check
git status --short
```

Also verify:

- Mermaid blocks render in Obsidian;
- headings are unique and stable;
- no source path points to `/tmp`;
- no generated build artifact is committed accidentally;
- source ledger entries have retrieval dates and provenance;
- only intended Garden files are staged.

## 15. Definition of done

A study is done only when:

- repository snapshot is pinned;
- assigned local files and tests were read;
- one end-to-end path is traced;
- one bounded experiment is recorded;
- external source minimum is met;
- source ledger is updated;
- observed failures and open obligations are explicit;
- pattern applicability and non-applicability are stated;
- textbook review passes;
- Obsidian formatting validates;
- another researcher cross-reviews terminology and evidence;
- commit contains only intended Garden work.

## 16. Working rule

Name the invariant only after tracing the mechanism. Keep the expressive pattern small in number and the supporting evidence rich in detail.
