---
title: claude-opus study — dropcut-studio CAM core
aliases:
  - dropcut-studio CAM compiler patterns
  - DROPCUT Studio claude-opus Garden study
status: active
type: architecture-garden-project
created: 2026-10-25
analyzed: 2026-10-25
analysis_schema: architecture-garden-v1
analysis_author: claude-opus-5-5
repository: /home/manuel/code/wesen/dropcut-studio
repository_remote: git@github.com:wesen/dropcut-studio.git
repository_branch: main
repository_commit: f3ebac2d5291b4a371bde25ae3a44d6f752cff41
repository_worktree: clean apart from untracked .pi/ and cam-ide-live.png
tags:
  - architecture-garden
  - dropcut-studio
  - cam
  - compiler
  - typescript
  - verification
related_notes:
  - "[[Research/Software Architecture Garden/dropcut-studio/README|Architecture Garden — dropcut-studio]]"
  - "[[Research/Software Architecture Garden/README|Software Architecture Garden]]"
---

# claude-opus study — dropcut-studio CAM core

This directory is a pattern study of the **TypeScript CAM core** of `dropcut-studio` on `main` at `f3ebac2`: the scripting host, planner, geometry kernel, compiler, emitters, verification and the studio app's state architecture. It complements the sibling `designs/` entries, which study the Go controller (`makera-z1-cli`) and its machine protocol on a separate branch and explicitly exclude the CAM compiler and certificate.

The chapters are written in a textbook style: each defines its terms, follows a concrete example through the code, states the pattern and its law, records where the implementation falls short of its own contract, and ends with candidate guidance.

> [!summary]
> - The system is a compiler whose narrow waist is a **non-modal machining IR**; G-code is one serialisation backend, and modality reappears only in one compression function checked by a round-trip oracle.
> - Target machines are **capability records**; the IR states intents the records decide.
> - Pipeline gates are **types**, and verification is **graded evidence per check**.
> - **Open correctness obligation found:** the certificate reports `PASS gouge` without running a gouge check. A 2.5D pocket cut 13 mm into the part compiles clean (chapter 05 §7).

## Reading order

1. [[Research/Software Architecture Garden/dropcut-studio/claude-opus/01 - Project Architecture Overview - A Compiler Whose Narrow Waist Is Machining|01 — Project Architecture Overview: A Compiler Whose Narrow Waist Is Machining]] — vocabulary, pipeline values, package layering. Read first.
2. [[Research/Software Architecture Garden/dropcut-studio/claude-opus/02 - Modality as a Final Compression Pass - The Non-Modal IR and Its Round-Trip Oracle|02 — Modality as a Final Compression Pass]] — non-modal IR, `compress()`, the round-trip oracle and what it cannot prove.
3. [[Research/Software Architecture Garden/dropcut-studio/claude-opus/03 - Capabilities as Data - Intent Commands Lowered by a Profile Record|03 — Capabilities as Data]] — `MachineProfile`, traverse-as-intent, the configuration-only Makera backend.
4. [[Research/Software Architecture Garden/dropcut-studio/claude-opus/04 - Certified Stage Types - A Brand Minted in One Place|04 — Certified Stage Types]] — `ValidatedProgram`, `unique symbol` brands, and how strong the guarantee really is.
5. [[Research/Software Architecture Garden/dropcut-studio/claude-opus/05 - Graded Evidence Certificates - Say What Was Verified and to What Resolution|05 — Graded Evidence Certificates]] — four-way `CheckStatus`, monotone recertification, error budgets, and the gouge counterexample.
6. [[Research/Software Architecture Garden/dropcut-studio/claude-opus/06 - Branch-and-Bound Spatial Queries - Tight Bounds Beat Fast Code|06 — Branch-and-Bound Spatial Queries]] — drop-cutter closed forms, admissible ceilings, nearest-first rings, analytic ground-truth tests.
7. [[Research/Software Architecture Garden/dropcut-studio/claude-opus/07 - Capability-Passing Script Host - Named Parameters, Boxed Units and Scope Combinators|07 — Capability-Passing Script Host]] — named-parameter capabilities, declarative plans, runtime units, scope combinators, honest non-isolation.
8. [[Research/Software Architecture Garden/dropcut-studio/claude-opus/08 - Strategies Produce Geometry, the Planner Owns the Gaps|08 — Strategies Produce Geometry, the Planner Owns the Gaps]] — linking, entry ladder, stock-top floor, and the thin `ToolpathSet` contract (CAM-002).
9. [[Research/Software Architecture Garden/dropcut-studio/claude-opus/09 - Three-Tier Application State - Serializable Store, Artifact Cache, Imperative Clock|09 — Three-Tier Application State]] — Redux ids, artifact cache, imperative clock, versioned documents, load generations.
10. [[Research/Software Architecture Garden/dropcut-studio/claude-opus/10 - Architecture Debt and Patterns Not to Repeat|10 — Architecture Debt and Patterns Not to Repeat]] — ranked register of eleven items.
11. [[Research/Software Architecture Garden/dropcut-studio/claude-opus/11 - Candidate Ecosystem Guidelines|11 — Candidate Ecosystem Guidelines]] — twenty-one candidate rules with comparison targets.
12. [[Research/Software Architecture Garden/dropcut-studio/claude-opus/12 - Claims and Their Evidence - Lossless Encoding, Signed Error Budgets, Per-Claim Certificates and Three-Key Shortcuts|12 — Claims and Their Evidence]] — **start here if you know the standard patterns.** The four less familiar ideas (lossless modal encoding, signed error budgets, per-claim certificates, three-key shortcuts), each with a measured gap: a mutation experiment on the round-trip oracle and a chord-deviation probe of the error budget.

## Pattern maturity

| Pattern | Chapter | Maturity |
|---|---|---|
| Non-modal IR with modality as a final compression pass | 02 | Established |
| Round-trip oracle for a stateful serializer | 02 | Established |
| Capabilities as data; intent commands | 03 | Established |
| Dialect as configuration over a generic emitter | 03 | Established |
| Certified stage types (brand minted in one place) | 04 | Established; guarantee overstated in comments |
| Graded evidence certificate | 05 | Candidate ecosystem pattern; **open correctness obligation** |
| Branch-and-bound drop-cutter with admissible ceilings | 06 | Established |
| Capability-passing script host with boxed units | 07 | Established; not an isolation boundary |
| Strategy/linker separation with entry ladder | 08 | Established; contract too thin (CAM-002) |
| Three-tier application state | 09 | Established |
| Versioned document with migration seam | 09 | Established |
| Duplicated compile pipeline in the app | 10 | Architecture debt |

## Evidence and method

- Source read at `f3ebac2` across all fourteen packages and both apps, plus `original/DESIGN-01`, `original/DESIGN-02`, and the docmgr tickets `CAM-001` and `CAM-002` under `ttmp/2026/08/`.
- `npx vitest run`: **16 test files, 235 tests, all passing.**
- Three scratch experiments, none committed to the repository:
  - a CLI compile of a 2.5D pocket through the `dome` mesh, to test the gouge row (chapter 05 §7.1);
  - a CLI compile of a script that reaches the global object through `Function.prototype.constructor`, to test the sandbox's stated limits (chapter 07 §2.1);
  - a `tsc --strict` check of single-cast brand forgery (chapter 04 §4).
- Greps for unconsulted declarations (`helical`, `timeoutMs`, test-only helpers, unemitted `DiagnosticCode`s) are listed in chapter 10.

Where the code and the repository's comments or design notes disagree, the chapters report the code and say so.
