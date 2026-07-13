---
title: PBUI Documentation - Structure, Method, and Handoff
aliases:
  - PBUI docs handoff
  - PBUI documentation report
tags:
  - project
  - pbui
  - documentation
  - technical-writing
  - handoff
status: active
type: project
created: 2026-07-13
repo: /home/manuel/code/wesen/2026-07-12--clim-jsx
---

# PBUI Documentation — Structure, Method, and Handoff

This report explains how the PBUI framework's documentation set was written and structured, so that the next technical writer can maintain and extend it without reverse-engineering the decisions. It covers the inventory (what exists and what each piece is for), the audience architecture (why the set has exactly these documents and no others), the writing method (the style rules, the sourcing discipline, and the revision loop that shaped the current text), the structural contracts the documentation depends on (places where prose is coupled to tested behavior), and the open tasks. The framework itself is described in [[PROJ - PBUI - Presentation-Based UIs in TypeScript and React]] and its conceptual foundations in [[ARTICLE - Presentation-Based UIs - Porting the CLIM Interaction Model to React]]; this note is about the documentation as an artifact.

> [!summary]
> 1. The set is seven kinds of document with disjoint jobs — orientation README, per-package READMEs, a checkpoint-driven tutorial, an explanatory textbook (user guide), an exhaustive API reference, a how-to recipe (PORTING-NOTES), and demos-as-worked-examples — deliberately matching the tutorial / how-to / reference / explanation separation.
> 2. Every document follows one style contract: textbook prose that explains why before how, terms defined before first use, no analogies, and real code only — every excerpt verified against source, which turned documentation-writing into a code audit (it found three stale source comments and three behavioral hazards).
> 3. Several pieces of prose are coupled to tested behavior (the echo grammar, CSS state-class names, command argument key names, package names). The report lists these couplings; a writer who edits examples without knowing them will produce documentation that contradicts CI.
> 4. The current text is the product of three explicit revision passes driven by reader feedback, recorded here as the QA loop to continue.

## Why this note exists

The PBUI repository (`/home/manuel/code/wesen/2026-07-12--clim-jsx`) acquired its documentation set in a compressed period (2026-07-12/13, commits `5dd9fdb`, `1aadb6c`, `47fd0ec`, `d1ee4d5`), written by the same hands that wrote the code. That is a strength — the docs are accurate to the implementation at commit time — and a risk: the structure and its constraints live in one head. This note moves them onto paper. A technical writer joining the project should be able to read this report, then confidently answer the three questions that govern all documentation work here: *where does a new fact go*, *what am I allowed to change*, and *how do I know a change is safe*.

## The inventory

All paths are relative to the repository root.

| Document | Size | Job | Audience state |
|---|---|---|---|
| `README.md` | ~90 lines | orientation: what PBUI is in one screen, a screenshot gallery of all seven demos, links onward | knows nothing |
| `packages/*/README.md` (5 files) | 38–73 lines each | per-package role, one minimal example, key-exports table, load-bearing contracts | evaluating or importing one package |
| `apps/demos/README.md` | ~40 lines | a *reading order* through the seven demos, one row per demo stating what it uniquely teaches | learning by example |
| `docs/getting-started.md` | 412 lines | tutorial: builds a bug tracker from an empty file, checkpoint after every section, troubleshooting table | first hour with the framework |
| `docs/user-guide.md` | ~600 lines | explanation: Part I teaches the 1984 model from the primary source; Part II explains each mechanism and how the parts interrelate | building something real; needs the *why* |
| `docs/api-reference.md` | ~1,030 lines | reference: every public export, exact signatures, defaults, define-time errors, the CSS contract | mid-task lookup |
| `apps/demos/PORTING-NOTES.md` | ~90 lines | how-to recipe: the steps to write a new application, special techniques, rules | knows the concepts, wants the checklist |

Supporting artifacts that function as documentation: the seven demos (each file header states what it demonstrates; the Hello demo is deliberately the smallest complete example), `docs/screenshots/` (eight staged 3200×2000 captures used by the README), and the design documents and diaries under `ttmp/` (rationale; not user documentation, but the place where "why is the boundary here" questions are answered).

## The audience architecture

The set maps onto the four-quadrant model of documentation (tutorial, how-to guide, reference, explanation — the separation popularized as Diátaxis), and the mapping is intentional: each quadrant answers a different reader question, and mixing them degrades both. The concrete assignments:

- **Tutorial** = `getting-started.md`. Learning-oriented; the reader does, the document guides. Its distinctive obligations here: a checkpoint after every section (a verifiable outcome before proceeding), no elided code (everything is typeable), and a symptom→cause troubleshooting table, because first-run failures in this framework have distinctive signatures (missing theme import, missing root class, a hand-wired `onClick` defeating the input context).
- **How-to** = `PORTING-NOTES.md`. Task-oriented; assumes competence; a recipe plus rules. It predates the rest of the set (it was written to direct code-writing agents during development) and earns its keep unchanged — do not merge it into the tutorial.
- **Reference** = `api-reference.md`. Information-oriented; complete, flat, and factual. One deliberate extension beyond API signatures: the CSS custom properties and class names of the theme package are documented *as API*, because components emit only structure and the stylesheet is the actual contract.
- **Explanation** = `user-guide.md`. Understanding-oriented, and the largest investment. Its two-part structure is the report's most important structural decision, discussed next.

The READMEs sit outside the quadrants as *entry points*: their job is routing a reader to the right quadrant document in under a minute, plus stating the two or three contracts a package consumer must not violate. Keep them short; when a README paragraph grows past its purpose, its content belongs in the user guide.

## The user guide's two-part structure

The user guide is organized as Part I (the model) before Part II (the framework), and the ordering carries the set's central pedagogical claim: **the framework's API is only memorizable, but the model is understandable — and a reader who understands the model can predict the API.** Part I teaches the presentation-based interface model from the primary source: Ciccarelli's 1984 thesis (AI-TR-794), a full transcription of which lives in the repository at `ttmp/2026/07/12/CLIM-JSX-001--*/sources/aitr-794.md`. Part II then presents each framework mechanism as the implementation of a named model element, with a model-to-module table as the hinge between the parts.

Three method decisions inside the guide are worth preserving:

1. **Primary-source citation with line anchors.** Part I quotes the thesis directly and cites as `aitr-794.md:NN`. This is not decoration: the anchors make every historical claim checkable in seconds, and they surfaced genuinely useful material — the thesis passage that *anticipates* the input context twelve years before CLIM built it (aitr-794.md:2067) is the guide's best single paragraph, and it was found by reading, not by remembering. When extending Part I, read the source; do not paraphrase from memory.
2. **A vocabulary chapter before any use.** Chapter 2 defines every term of art — both domain terms (presentation, ptype, input context) and incidental jargon (chrome, prompt, scrollback, hit-testing, marching ants) — in complete plain-language sentences. This chapter exists because of reader feedback (see the revision history below), and it changed the whole guide: later chapters can move at full speed because nothing depends on the reader inferring a contraction.
3. **An end-to-end trace chapter.** Chapter 10 ("Anatomy of a gesture") follows one click through every module with a sequence diagram. Readers reported the per-module chapters only cohering after this chapter existed; keep it current when the gesture path changes.

## The writing method

**Style contract.** All documents follow one style, stated once and enforced by rewriting: prose paragraphs that develop ideas; *why* before *how*; concrete artifacts (code, tables, diagrams, traces) doing the argumentative work; complete sentences in bullet lists; direct claims without hedging; and **no analogies** — difficult concepts are clarified with definitions, diagrams, and traces, never with comparisons to kitchens or traffic. The anti-patterns actively removed during editing were the usual ones: wandering preambles, "it is worth noting", vague bullet fragments, and unexplained shorthand.

**Real code only, verified.** Every code excerpt in every document is real code from the repository, trimmed only for length, and checked against source before inclusion (during the user-guide expansion this meant re-reading `engine.ts` line ranges before quoting them; one citation was off by three lines and corrected). This discipline had a second-order payoff worth institutionalizing: writing the API reference against the source *is a code audit*. The reference pass found three stale source comments (fixed in commit `47fd0ec`'s predecessor) and three real behavioral hazards that are now documented rather than hidden — the invocation log's cap can evict a still-undoable entry; `undoInvocation` marks a record undone before awaiting the undo function; the command line silently discards trailing words beyond bindable arguments. A writer updating the reference should expect, and report, the same class of findings.

**Screenshots are staged, not idle.** The README gallery captures were driven by a Playwright script: each demo was put into a state that *shows the paradigm* — mid-accept with marching ants, a lattice-titled menu open, the schematic after Run Spice with waveforms plotted — then captured at 1600×1000 with a 2× device-scale factor (3,200×2,000 PNGs, crisp on high-density displays). The staging steps live in the session that produced them and, in compressed form, in the commit message of `d1ee4d5`; when the UI changes, re-stage rather than re-cropping idle screens, and keep captions stating what the image *demonstrates*, not what app it is.

**Division of labor.** The API reference was drafted by a subagent working strictly from source with an explicit style brief and a mandate to report discrepancies rather than fix them; the tutorial, user guide, and READMEs were written directly, because their value lies in narrative judgment. This split — mechanical enumeration delegated, pedagogy kept — is a reasonable default for future large additions.

## The revision history as a QA loop

The current text is the third iteration of several documents, and the iterations were driven by specific reader feedback. The loop is the process to continue:

1. **First pass:** the full set written top-down from the implementation (commit `5dd9fdb`).
2. **Thesis-grounding pass:** feedback asked the user guide to "spend time explaining the presentation-based UI concepts … like a real textbook," and explicitly invited reading the original thesis. Result: the two-part restructure, primary-source quotes with line anchors, the presenter/recognizer decomposition chapters (commit `1aadb6c`, first version).
3. **De-cryptification pass:** feedback identified the failure mode precisely — "I have a hard time understanding terms like 'keyboard half' and other contractions, but also domain-specific terms like 'presentation'." Result: the vocabulary chapter, every contraction spelled out at point of use, and a glossary keyed to defining chapters (commit `1aadb6c`, final version).
4. **Tutorial-guidance pass:** "flesh the getting-started out a bit … so that we also guide the user nicely" — deliberately *not* to textbook depth. Result: checkpoints, completed code, the run-it walkthrough, and the troubleshooting table (commit `47fd0ec`).

The pattern to institutionalize: reader feedback here names *symptoms* ("cryptic", "guide me"), and the fix is structural (a vocabulary chapter, checkpoints), not local sentence polish. When the next round of feedback arrives, look for the missing structure first.

## Structural contracts: where prose is coupled to tested behavior

These are the couplings a writer must know before editing examples. Violating them produces documentation that contradicts the test suite.

- **The echo grammar is frozen.** The exact text of engine-printed lines (`Command: <name> (arg) …`, `  arg (a TYPE) ⇒ label`, `[Abort]`, `Undid: <name>`) is pinned byte-for-byte by golden tests (`packages/core/src/golden.test.ts`; regenerate only deliberately with `GOLDEN_UPDATE=1`). Transcript examples in the docs must match it exactly — copy from a real run or from the golden files, never retype from memory.
- **CSS class names are API.** `pbui-eligible`, `pbui-inert`, `pbui-passthru`, `pbui-kbd-target` and the rest are asserted by the e2e suite; the theme README documents them as a contract. Do not "improve" a class name in prose.
- **Command argument keys are user-visible.** In the builder, the `args` object's keys appear verbatim in prompts and echoes, and e2e tests assert prompt strings. Tutorial examples that rename an argument key are proposing a behavior change.
- **Package names.** The packages were renamed from `@pbui/*` to `@go-go-golems/pbui-*` after the first documentation pass; all docs now use the new names. Any older snippet encountered in tickets or diaries with `@pbui/` imports is historical.
- **Numbers drift.** Test counts (53 core / 19 RTL / 26 e2e at the time of writing) and measurements (1.98 renders per hover at N=2,000) appear in several documents. Prefer wording that survives drift ("the core suite", "about two renders") except where the number *is* the point (the perf budget), and re-verify cited numbers when touching those passages.

## Maintenance model: where each fact lives

The set avoids duplication by ownership. When adding a fact, place it in its owner and cross-reference; when the same sentence appears in two documents, one of them is wrong.

| Fact class | Owner | Others may |
|---|---|---|
| what a concept *is* and why it exists | user guide | link to the chapter |
| exact signature, default, define-time error | API reference | show usage without restating the contract |
| the steps to do a task | PORTING-NOTES (apps) or getting-started (first app) | link |
| a package's non-negotiable contracts | that package's README | repeat only if e2e-pinned (state classes) |
| which demo shows a technique | `apps/demos/README.md` reading-order table | name the demo |
| rationale, history, rejected alternatives | `ttmp/` design docs and diaries | cite the ticket |

Verification for documentation changes is currently manual: there is no snippet-compilation or link-checking in CI. The two cheap checks worth adding are noted in the tasks below.

## Open tasks for the next writer

1. **Snippet verification.** Extract the tutorial's code into a compiled (not shipped) fixture, or at minimum add a CI grep that fails when docs reference identifiers that no longer exist. The package rename made the risk concrete.
2. **API-reference regeneration procedure.** The reference is hand-maintained against source. Write the checklist (which files to re-read per package, the discrepancy-reporting convention) or automate extraction of the export inventory; today the procedure lives only in the original agent brief.
3. **A theming guide.** The theme README documents the contract; nobody has written "how to build a second theme" with a worked example. The class vocabulary is small enough for a short how-to.
4. **Per-demo walkthroughs.** The demo README's table says what each demo teaches; the schema and e-commerce demos are rich enough to deserve guided readings (the file headers are the outline).
5. **Screenshot refresh script.** Check the staging steps into `apps/demos/e2e/` as a tagged, non-CI Playwright script so gallery refreshes are one command.
6. **Accessibility findings.** A real screen-reader session is still outstanding (tracked in the CLIM-JSX-004 ticket); its findings will need a user-guide Chapter 19 update and possibly a dedicated how-to.
7. **Publishing docs.** If the packages ever ship to npm (they currently export raw TypeScript), installation sections in every README and the tutorial's Setup section change; the workspace-only instructions are marked by the `workspace:*` dependency blocks.

## Working rules

- One style everywhere: define before use, why before how, no analogies, complete sentences, real code only.
- Read the source before quoting it — code or thesis — and keep line anchors accurate.
- New fact → find its owner document; never duplicate, always cross-reference.
- Transcript and prompt examples come from real runs; they are coupled to golden and e2e tests.
- Reader feedback names symptoms; respond with structure, not sentence polish.
- Documentation passes double as audits: report code discrepancies you find, do not silently absorb them into prose.

## Related notes

- [[PROJ - PBUI - Presentation-Based UIs in TypeScript and React]] — the framework and repository this documentation covers.
- [[ARTICLE - Presentation-Based UIs - Porting the CLIM Interaction Model to React]] — the conceptual deep dive; overlapping subject matter with the user guide's Part I, different audience (vault knowledge vs. in-repo onboarding).
