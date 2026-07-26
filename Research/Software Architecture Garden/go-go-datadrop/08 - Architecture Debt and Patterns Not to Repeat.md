---
title: go-go-datadrop — Architecture Debt and Patterns Not to Repeat
aliases:
  - datadrop architecture debt
  - hand rolled cli output layer
  - decision record numbering collision
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
  - DATADROP-9 (planned remediation of item 1)
  - DATADROP-8 (planned remediation of item 3)
related_files:
  - pkg/cli/output.go
  - pkg/cli/dataset.go
  - pkg/cli/read.go
  - ui/GUIDELINES.md
  - ui/src/pbui/registry.ts
  - ui/src/components/organisms/WorkspaceStrip/WorkspaceStrip.tsx
  - ui/src/model/pipeline.ts
---

# Architecture Debt and Patterns Not to Repeat

Seven items, ordered by how much they would cost another project that copied them. Two have remediation tickets; the rest are recorded.

## 1. A hand-rolled output layer, and eleven commands that ignore their own flag

`pkg/cli/output.go` is 162 lines: two `tabwriter` renderers, a three-valued `--output` flag, a truncation helper, and a JSON encoder configured three different ways.

The measurable consequence is that **eleven of the nineteen CLI verbs call one helper whose entire body is "encode with two-space indent"**. Those eleven have no table rendering at all — `datadrop dataset list mydrop` prints JSON whether or not `--output table` was requested, and the flag is accepted and silently ignored.

That is not a design. It is eleven places where nobody wanted to write a twelfth `tabwriter` block, and the absence became the behaviour.

**Why it is debt rather than a missing feature.** The flag exists and lies. A user who passes `--output table` and receives JSON has been told the tool has a capability it does not, which is worse than the tool not having it.

**Remediation:** DATADROP-9 converts the CLI to framework commands that emit rows, deleting the file. The design is written; nothing is implemented. Note that the conversion carries the exit-code defect described in [[Research/Software Architecture Garden/go-go-datadrop/07 - Single Binary Delivery and Operational Surface|document 07]], which the ticket handles explicitly.

**What another project should take from this:** a flag that is parsed and unused is worse than an unimplemented flag, because it cannot be discovered by reading the help text. If eleven call sites all reach for the same trivial escape hatch, the escape hatch is the design.

## 2. The decision-record sequence collides with itself

Decisions are numbered globally and cited from 86 source files, which is one of this project's best properties. But the sequence forked at the start: the backend ticket numbered its decisions DR-1 through DR-4, and the first frontend ticket restarted at DR-1.

Nothing is ambiguous in practice — every citation inside `ui/` means the frontend sequence — but two sequences share one namespace, and a reader arriving at `DR-2` from a code comment has to know which document to open.

**Why it is debt:** the citation mechanism's whole value is that a number resolves to an argument. A namespace with two occupants degrades that quietly, and the degradation grows with every new reader.

**What another project should take from this:** if decision records are going to be cited from code, the identifier needs to be unique across the project from the first one. A prefix per area (`BE-1`, `UI-1`) costs nothing at the start and cannot be retrofitted cheaply once 86 files cite the short form.

## 3. Two declared presentation types have no descriptor, and one advertises a feature that does not exist

`tile` and `workspace` are in the presentation vocabulary, are wrapped in real `<Presentation>` elements, and have no entry in the descriptor map — so right-clicking a tile produces *"no verbs for this object yet"*.

Worse, the workspace strip has rendered this help text since DATADROP-4:

> L switches · double-click renames · **R for duplicate / delete** · ⌾ is defined in code

Right-clicking a workspace produces an empty menu. The sentence has described a feature that has never existed for the entire life of the component.

There is a second-order consequence: because there is no rename verb, double-click-to-rename has **no keyboard route at all**. That is an accessibility gap created by an incomplete abstraction rather than by an oversight in the control.

**Remediation:** DATADROP-8 adds the three descriptors. Designed, not implemented. The gap is recorded in a lint suppression at the site, so the next reader of that component meets it.

**What another project should take from this:** a declared-but-unimplemented member of an extensible vocabulary is invisible to the type system and visible to users. If a registry has a `Partial<Record<...>>` shape, something should assert which members are intentionally absent.

## 4. Guidelines that under-report their own enforcement

`ui/GUIDELINES.md §10` is a table headed *"What the tests actually guarantee"*. It lists five tests. There are thirteen.

Missing: the token-reference resolver, the tour/registry set equality, the multi-instance guards, the lesson anti-rot test, the fixture round-trip, and the render-path guards.

**Why it is debt:** a newcomer reads that table to decide what they can rely on and what they must check by hand. Under-reporting by eight makes them more cautious than necessary in six places and gives them no reason to trust the eight that exist. A table that is wrong in the *conservative* direction is still wrong.

**What another project should take from this:** a document that enumerates its own tests needs the same set-equality guard that [[Research/Software Architecture Garden/go-go-datadrop/06 - Executable Documentation|document 06]] recommends for registries. This is precisely the failure that pattern prevents, in the one place it was not applied.

## 5. A type-level exhaustiveness gap that would have emptied a table

Both filter callbacks in the pipeline engine switched over the four members of the comparison-operator union and returned nothing on the implicit fifth path. `Array.prototype.filter` reads `undefined` as false, so a fifth operator added without a case would have **removed every row**, in both branches, with no error anywhere.

Found by a linter on its first run over a codebase with 229 passing tests. Repaired with a compiler-enforced exhaustiveness assertion, verified by adding a fifth operator and watching both branches fail to compile.

**Why it is recorded here rather than as a fixed bug:** the class remains. A `switch` over a union with no `default` is only safe while the union is closed, and TypeScript does not require the author to say they are relying on that.

**What another project should take from this:** an exhaustive switch inside a callback whose return type is `boolean | undefined` is a silent failure waiting for a union to grow. The assertion costs four lines.

## 6. No continuous integration on the browser lint

`bun run --cwd=ui lint` exists and is clean over 425 files. Nothing runs it automatically. The Go side has a pre-commit hook that runs `golangci-lint` and the test suite; the browser side has neither.

**Why it is debt:** the linter found two genuine defects in its first execution. A tool with that hit rate that runs only when someone remembers is a tool that will stop running.

## 7. A convenience dependency that tripled the artefact

Recorded in full in [[Research/Software Architecture Garden/go-go-datadrop/07 - Single Binary Delivery and Operational Surface|document 07]]: the embedded help system took the binary from 18.8 MB to 55.7 MB and the module graph from 52 to 194, with 28 MB attributable to one Cobra-integration import that pulls in a terminal UI, a spreadsheet writer, a JSON query engine and a secrets-manager client.

**Why it is debt rather than a decision:** it *was* a decision — the size was measured and accepted — but nothing records a threshold at which it would be revisited, and the lighter path (the help core without the Cobra integration, at 27.7 MB) was identified and not taken.

**What another project should take from this:** measure the artefact before and after adding a convenience dependency, and write down the number. A dependency whose cost is never measured is never reconsidered.

## Debt-removal sequence

If this project were being brought to a clean state, the order that removes the most risk per unit of work:

1. **Item 6** (lint in CI) — hours, and it protects everything else.
2. **Item 4** (the guidelines table) — minutes, and it is the entry point every newcomer reads.
3. **Item 3** (the missing descriptors) — DATADROP-8; removes a user-visible lie and an accessibility gap.
4. **Item 1** (the CLI output layer) — DATADROP-9; the largest, and blocked on the upstream exit-code question.
5. **Item 2** (decision-record namespace) — cheap only if done as a prefix on *new* records; retrofitting 86 citations is not worth it.
6. **Item 7** (the binary size) — revisit if the tool is ever distributed by container pull frequency rather than by download.

Item 5 is repaired.

## Related notes

- [[Research/Software Architecture Garden/go-go-datadrop/01 - Project Architecture Overview]]
- [[Research/Software Architecture Garden/go-go-datadrop/07 - Single Binary Delivery and Operational Surface]]
- [[Research/Software Architecture Garden/go-go-datadrop/09 - Candidate Ecosystem Guidelines]]
- [[PROJECT REPORT - go-go-datadrop v0.7 - What Makes a Defect Findable]]
