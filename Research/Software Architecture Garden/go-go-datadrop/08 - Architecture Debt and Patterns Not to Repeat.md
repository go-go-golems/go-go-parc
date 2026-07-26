---
title: go-go-datadrop — Architecture Debt and Patterns Not to Repeat
aliases:
  - datadrop architecture debt
  - hand rolled cli output layer
  - decision record numbering collision
  - datadrop repaired debt
tags:
  - architecture-garden
  - go-go-datadrop
  - architecture-debt
  - cli
status: active
type: architecture-pattern-study
pattern_maturity: architecture-debt
created: 2026-07-26
analyzed: 2026-07-26
repository: /home/manuel/code/wesen/go-go-golems/go-go-datadrop
repository_commit: ef996430f8a3a63e6812d961eb2bae5d631272a0
analysis_commit: 69b82257f75a4ca236d985629dc298844128409f
source_tickets:
  - DATADROP-9 (item 1, repaired 2026-07-26)
  - DATADROP-8 (planned remediation of item 3)
last_reviewed: 2026-07-26
related_files:
  - pkg/cli/build.go
  - pkg/cli/rows.go
  - cmd/datadrop/tree_test.go
  - ui/GUIDELINES.md
  - ui/src/pbui/registry.ts
  - ui/src/components/organisms/WorkspaceStrip/WorkspaceStrip.tsx
  - ui/src/model/pipeline.ts
---

# Architecture Debt and Patterns Not to Repeat

Seven items were recorded at the first analysis. Two are now repaired, and this document is organised accordingly: **open debt first, repaired debt second.** A repaired item is kept rather than deleted only when the repair taught something the original entry did not know — otherwise it goes, because a debt register that never shrinks is a list nobody reads.

Reviewed 2026-07-26 after DATADROP-9.

## Open debt

## 1. The decision-record sequence collides with itself

Decisions are numbered globally and cited from 86 source files, which is one of this project's best properties. But the sequence forked at the start: the backend ticket numbered its decisions DR-1 through DR-4, and the first frontend ticket restarted at DR-1.

Nothing is ambiguous in practice — every citation inside `ui/` means the frontend sequence — but two sequences share one namespace, and a reader arriving at `DR-2` from a code comment has to know which document to open.

**Why it is debt:** the citation mechanism's whole value is that a number resolves to an argument. A namespace with two occupants degrades that quietly, and the degradation grows with every new reader.

**What another project should take from this:** if decision records are going to be cited from code, the identifier needs to be unique across the project from the first one. A prefix per area (`BE-1`, `UI-1`) costs nothing at the start and cannot be retrofitted cheaply once 86 files cite the short form.

## 2. Two declared presentation types have no descriptor, and one advertises a feature that does not exist

`tile` and `workspace` are in the presentation vocabulary, are wrapped in real `<Presentation>` elements, and have no entry in the descriptor map — so right-clicking a tile produces *"no verbs for this object yet"*.

Worse, the workspace strip has rendered this help text since DATADROP-4:

> L switches · double-click renames · **R for duplicate / delete** · ⌾ is defined in code

Right-clicking a workspace produces an empty menu. The sentence has described a feature that has never existed for the entire life of the component.

There is a second-order consequence: because there is no rename verb, double-click-to-rename has **no keyboard route at all**. That is an accessibility gap created by an incomplete abstraction rather than by an oversight in the control.

**Remediation:** DATADROP-8 adds the three descriptors. Designed, not implemented. The gap is recorded in a lint suppression at the site, so the next reader of that component meets it.

**What another project should take from this:** a declared-but-unimplemented member of an extensible vocabulary is invisible to the type system and visible to users. If a registry has a `Partial<Record<...>>` shape, something should assert which members are intentionally absent.

## 3. Guidelines that under-report their own enforcement

`ui/GUIDELINES.md §10` is a table headed *"What the tests actually guarantee"*. It lists five tests. There are thirteen.

Missing: the token-reference resolver, the tour/registry set equality, the multi-instance guards, the lesson anti-rot test, the fixture round-trip, and the render-path guards.

**Why it is debt:** a newcomer reads that table to decide what they can rely on and what they must check by hand. Under-reporting by eight makes them more cautious than necessary in six places and gives them no reason to trust the eight that exist. A table that is wrong in the *conservative* direction is still wrong.

**What another project should take from this:** a document that enumerates its own tests needs the same set-equality guard that [[Research/Software Architecture Garden/go-go-datadrop/06 - Executable Documentation|document 06]] recommends for registries. This is precisely the failure that pattern prevents, in the one place it was not applied.

## 4. No continuous integration on the browser lint

`bun run --cwd=ui lint` exists and is clean over 425 files. Nothing runs it automatically. The Go side has a pre-commit hook that runs `golangci-lint` and the test suite; the browser side has neither.

**Why it is debt:** the linter found two genuine defects in its first execution. A tool with that hit rate that runs only when someone remembers is a tool that will stop running.

## 5. A convenience dependency that tripled the artefact

Recorded in full in [[Research/Software Architecture Garden/go-go-datadrop/07 - Single Binary Delivery and Operational Surface|document 07]]: the embedded help system took the binary from 18.8 MB to 55.7 MB and the module graph from 52 to 194, with 28 MB attributable to one Cobra-integration import that pulls in a terminal UI, a spreadsheet writer, a JSON query engine and a secrets-manager client.

**Why it is debt rather than a decision:** it *was* a decision — the size was measured and accepted — but nothing records a threshold at which it would be revisited, and the lighter path (the help core without the Cobra integration, at 27.7 MB) was identified and not taken.

**What another project should take from this:** measure the artefact before and after adding a convenience dependency, and write down the number. A dependency whose cost is never measured is never reconsidered.

## Repaired debt, and what the repair taught

Two items are gone from the register. They are kept here because in both cases the repair produced knowledge the original entry did not have — which is the only reason to keep a repaired item at all.

### R1. The hand-rolled output layer — repaired by DATADROP-9, 2026-07-26

**What it was.** `pkg/cli/output.go`, 162 lines: two `tabwriter` renderers, a three-valued `--output` flag, a truncation helper, and a JSON encoder configured three different ways. Eleven of the nineteen verbs called one helper whose entire body was "encode with two-space indent," so those eleven had no table rendering at all and `--output table` was accepted and silently ignored.

**What the repair was.** All nineteen verbs converted to `glazed` commands emitting rows: fifteen `GlazeCommand`, one `WriterCommand` (`export`, which copies bytes the server formatted), three `BareCommand`. `output.go`, `read.go`, `push.go` and `dataset.go` deleted — 1 467 lines. Eleven verbs gained a table; every data-producing verb gained CSV, YAML, Markdown, Excel, field selection, jq filtering, sorting and templating.

**What the repair taught, which the original entry did not know.** Three things:

- **The remediation cost was three breaking flag renames, two of them forced.** The application's `--stream` and `--flatten` collided with fields the framework's own sections own, and a collision fails the construction of the *entire command tree* rather than of one verb. Neither was foreseen; the ticket's design document listed `--stream` among the flags the framework *adds*, without noticing the application already had one.
- **The original lesson was right but incomplete.** "A flag that is parsed and unused is worse than an unimplemented flag" holds. The repair adds its converse: *a flag whose name the framework later occupies with a different type is worse than a removed flag*, because the old spelling still parses and produces a plausible error about an unrelated rule.
- **Deleting a hand-rolled layer does not reduce line count.** `pkg/cli` went from 2 486 lines to 4 721. What was removed was per-verb maintenance; what replaced it is declarative — field definitions, help text, and projections that are now a pinned contract. Recording this matters because "delete the hand-rolled layer" reads like a simplification and is not one.

The failure taxonomy the repair produced is documented in [[Research/Software Architecture Garden/go-go-datadrop/10 - Adopting a Command Framework|document 10]].

### R2. A type-level exhaustiveness gap that would have emptied a table

Both filter callbacks in the pipeline engine switched over the four members of the comparison-operator union and returned nothing on the implicit fifth path. `Array.prototype.filter` reads `undefined` as false, so a fifth operator added without a case would have **removed every row**, in both branches, with no error anywhere.

Found by a linter on its first run over a codebase with 229 passing tests. Repaired with a compiler-enforced exhaustiveness assertion, verified by adding a fifth operator and watching both branches fail to compile.

**Why it is recorded here rather than as a fixed bug:** the class remains. A `switch` over a union with no `default` is only safe while the union is closed, and TypeScript does not require the author to say they are relying on that.

**What another project should take from this:** an exhaustive switch inside a callback whose return type is `boolean | undefined` is a silent failure waiting for a union to grow. The assertion costs four lines.

## Debt-removal sequence

If this project were being brought to a clean state, the order that removes the most risk per unit of work:

1. **Item 4** (lint in CI) — hours, and it protects everything else.
2. **Item 3** (the guidelines table) — minutes, and it is the entry point every newcomer reads. Note that it is now wrong in a second direction as well: the structural-guard genre gained four Go instances in DATADROP-9 that the table does not mention.
3. **Item 2** (the missing descriptors) — DATADROP-8; removes a user-visible lie and an accessibility gap.
4. **Item 1** (decision-record namespace) — cheap only if done as a prefix on *new* records; retrofitting 86 citations is not worth it.
5. **Item 5** (the binary size) — revisit if the tool is ever distributed by container pull frequency rather than by download.

## Related notes

- [[Research/Software Architecture Garden/go-go-datadrop/01 - Project Architecture Overview]]
- [[Research/Software Architecture Garden/go-go-datadrop/07 - Single Binary Delivery and Operational Surface]]
- [[Research/Software Architecture Garden/go-go-datadrop/09 - Candidate Ecosystem Guidelines]]
- [[Research/Software Architecture Garden/go-go-datadrop/10 - Adopting a Command Framework]]
- [[PROJECT REPORT - go-go-datadrop v0.7 - What Makes a Defect Findable]]
- [[PROJECT REPORT - go-go-datadrop v0.8 - Nineteen Verbs, and the Four Silences of Framework Adoption]]
