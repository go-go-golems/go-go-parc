# KB Batch 9: Tree-sitter and Structured Text Systems

## Batch scope

This batch processes the handoff document's **Batch C — Tree-sitter and structured text systems**.

Analyzed project reports:

1. [[PROJ - Query Treesitter - Tree-sitter Query Language Prototypes and Design]]
2. [[PROJ - Sanitize - Tree-sitter Structured Text Sanitizer]]
3. [[PROJ - Tree-sitter Templating - Syntax-Aware Code Expansion System]]
4. [[PROJ - Sanitize - JSON Recovery Experiments and Limits]]
5. [[PROJ - Sanitize - YAML Sanitizing Deep Dive]]
6. [[PROJ - Scenario Runtime Workbench - Scenario-Driven Reconciliation Demo]]

## Executive summary

Batch C produced one threshold-triggered On-Ramp entry and several strong tribal candidates. The dominant theme is not simply "Tree-sitter." The deeper pattern is **syntax structure as an engineering signal**: parse trees, spans, query matches, and parse errors drive repair decisions, editor expansion proposals, semantic query experiments, and scenario debugging surfaces.

The strongest immediate KB action was creating [[On-Ramp/tree-sitter-for-go-tools]]. Tree-sitter is lookupable, but the public docs do not explain our Go-tooling usage: parse once, preserve spans, add semantic/heuristic layers above the tree, and keep automatic transforms conservative.

## What was written

### New On-Ramp entry

- [[On-Ramp/tree-sitter-for-go-tools]] — created because Tree-sitter now appears across at least five project reports in this campaign:
  - Query Treesitter
  - Sanitize structured-text overview
  - Tree-sitter Templating
  - Sanitize JSON recovery
  - Sanitize YAML deep dive

The entry is intentionally Go-tooling oriented. It does not reproduce the Tree-sitter manual. It explains how our projects use Tree-sitter as a structural prefilter, span source, incremental editor parser, and repair/diagnostic witness.

## What could / should be written later

No new Tribal entry was created from this batch. Several patterns are strong but should be reviewed by implementers before promotion because they depend on scar tissue from concrete code paths.

### Tribal candidates promoted or reinforced

| Concept | Seen in | Status | Notes |
|---------|---------|--------|-------|
| **Tree-sitter as structural prefilter plus semantic layer** | Query Treesitter, Tree-sitter Templating, Sanitize YAML/JSON | 3/3 — READY, needs implementer review | Pattern is real, but likely overlaps the new Tree-sitter On-Ramp. Better reviewed before creating a separate Tribal entry. |
| **Conservative repair boundary** | Sanitize overview, YAML deep dive, JSON recovery | 3/3 — READY, needs implementer review | Strongest Sanitize-specific tribal candidate: fix only what can be explained; lint when intent is ambiguous. |
| **Shared parse-aware analysis object** | Sanitize overview, YAML deep dive, JSON recovery | 3/3 — READY, needs implementer review | `documentAnalysis` / format analysis as source of truth for parse, lint, duplicate-key traversal, and fix orchestration. |
| **Backend-authoritative syntax tooling** | Tree-sitter Templating, Scenario Runtime Workbench, Glazed/help-style prior batches | 2/3 or 3/3 depending scope | Backend owns parse/runtime truth; frontend renders snapshots/proposals. Needs sharper definition before writing. |
| **Scenario package contract** | Scenario Runtime Workbench | 1/3 | Folder-level contract: metadata + desired state + generated UI + JS stages. |
| **Observe/compare/plan/execute reconciliation loop** | Scenario Runtime Workbench | 1/3 | Strong on-ramp/fundamental candidate if more controller-style reports appear. |

## What was updated / reinforced

- [[Tribal/goja-execution-model]] is reinforced by Scenario Runtime Workbench as another Go-owned runtime with JavaScript scenario semantics. It is not a direct REPL/session instance, so it should be listed as a variation rather than counted as a new exact instance.
- [[Tribal/reduction-ladder-debugging]] is lightly reinforced by the Sanitize JSON report's parse matrices, heuristic probes, detection buckets, overlap studies, and repair matrix. The project shrank a vague "repair malformed LLM JSON" problem into concrete categories with explicit limits.
- [[On-Ramp/tree-sitter-for-go-tools]] now covers the common newcomer orientation for Tree-sitter across this batch.

## Per-project extraction

### 1. Query Treesitter

**Role in batch**: language-design lab for AST query systems.

**Tribal candidates**:
- Tree-sitter as structural prefilter plus semantic layer — native queries remain the fast structural substrate; higher-level relations/unification/custom predicates handle the rest.
- Repeated-variable subtree equality — TUQL treats repeated variables as structural equality, not object identity.
- User-defined named AST queries — teams build reusable query vocabulary instead of one-off giant patterns.
- Host-language custom predicates and binders — declarative query language with JS escape hatches.

**On-Ramp candidates**:
- Tree-sitter query language — now covered by [[On-Ramp/tree-sitter-for-go-tools]].
- First-order unification for AST matching — lookupable, but not enough project demand yet.
- Lexical scope / declaration-use resolution — candidate if more analysis tools appear.

**Fundamental concepts**:
- Logic programming / unification.
- Relational query planning.
- Compiler front-end symbol resolution.

### 2. Sanitize — Tree-sitter Structured Text Sanitizer

**Role in batch**: umbrella structured-text repair tool with YAML/JSON engines and a browser inspection UI.

**Tribal candidates**:
- Conservative repair boundary — prefer explainable repair over aggressive guessing.
- Format-specific engines under one CLI/server surface — YAML and JSON have parallel packages but different safe-fix boundaries.
- Example corpus as repair evidence loop — fixture corpora and playground are part of the engineering method.
- Parse/lint/fix as inspectable local workflow — CLI plus browser UI exposes the reasoning instead of acting as a black box.

**On-Ramp candidates**:
- Tree-sitter for Go tools — created.
- Structured text recovery for LLM outputs — 2/5 if paired with JSON report; domain seed.

**Fundamental concepts**:
- Parsing vs validation.
- Ambiguity in program repair.

### 3. Tree-sitter Templating

**Role in batch**: syntax-aware code expansion prototype with Go backend and React/Monaco frontend.

**Tribal candidates**:
- Backend-authoritative syntax tooling — frontend sends edits; backend owns parse state, rule evaluation, and proposals.
- Rule = query + trigger + guard + expansion — syntax-aware behavior decomposed into data-driven pieces.
- Fired-key idempotence for editor proposals — session-local memory prevents repeated expansion proposals.
- Changed-range filtered rule evaluation — incremental parser changes limit which rules fire.

**On-Ramp candidates**:
- Tree-sitter for Go tools — created.
- Monaco editor integration with Go backend — 1/5.
- WebSocket editor protocol — 1/5.

**Fundamental concepts**:
- Incremental parsing.
- Idempotence in generated edits.

### 4. Sanitize — JSON Recovery Experiments and Limits

**Role in batch**: negative-space report defining where conservative JSON repair must stop.

**Tribal candidates**:
- Conservative repair boundary — JSON proves why lint-only is sometimes the correct product behavior.
- Strict-parser plus Tree-sitter dual validation — tree shape and `encoding/json` acceptance answer different questions.
- Detection vs repair separation — a malformed pattern can be detectable without being safe to rewrite.
- Repair matrix as engineering artifact — generated evidence prevents overclaiming.

**On-Ramp candidates**:
- Tree-sitter for Go tools — created.
- Malformed LLM JSON recovery — 1/5 domain seed.

**Fundamental concepts**:
- Ambiguous repair spaces.
- Parser error recovery vs language validity.

### 5. Sanitize — YAML Sanitizing Deep Dive

**Role in batch**: mature example of parse-aware lint and repair working well.

**Tribal candidates**:
- Shared parse-aware analysis object — `documentAnalysis` holds tree text, parse errors, duplicate keys, and line index.
- Conservative iterative repair loop — analyze → lint → fix → reanalyze until convergence.
- Parser plus heuristic classification — parse-only, heuristic-only, and hybrid failures are different fix classes.
- Span-rich diagnostics as UI/API contract — lint issues carry byte and row/column spans.

**On-Ramp candidates**:
- Tree-sitter for Go tools — created.
- YAML parser recovery and duplicate-key behavior — 1/5.

**Fundamental concepts**:
- Fixed-point iteration / convergence.
- Structured diagnostics.

### 6. Scenario Runtime Workbench

**Role in batch**: adjacent structured runtime: Go owns lifecycle, JavaScript owns scenario semantics, React renders snapshots.

**Tribal candidates**:
- Scenario package contract — `scenario.json`, `spec.json`, `ui.json`, and four stage files form a reusable authoring shape.
- Observe/compare/plan/execute as visible reconciliation loop — controller reasoning is split into inspectable phases.
- Backend snapshot as source of truth — UI is a renderer/debugger, not local truth owner.
- Go-owned lifecycle with JS-owned scenario semantics — related to goja execution model but not identical to REPL/session semantics.

**On-Ramp candidates**:
- Reconciliation loops / controller pattern — 1/5.
- Goja sandbox for scenario scripts — covered partly by goja entries, but newcomer orientation may still be needed later.

**Fundamental concepts**:
- Control loops and reconciliation.
- Desired vs observed state.

## Candidate decisions

### Created now

- [[On-Ramp/tree-sitter-for-go-tools]] — threshold hit; lookupable concept with our-specific Go-tooling angle.

### Do not create yet without review

- **Conservative repair boundary** — strong candidate, but the entry needs implementer scar tissue from Sanitize's YAML and JSON code paths.
- **Shared parse-aware analysis object** — strong candidate, but probably too Sanitize-specific unless generalized carefully.
- **Tree-sitter as structural prefilter plus semantic layer** — may be a Tribal entry later, but the new On-Ramp may cover enough for readers until more implementation examples appear.

## Suggested index changes

Add Batch 9 entries for all six projects and update campaign counts:

- Analyzed so far: 55
- Remaining: 112
- On-Ramp entries: 17

Update candidate tracking:

- Add Tree-sitter On-Ramp as created.
- Add the three strong but review-needed tribal candidates above.
- Mark Scenario Runtime Workbench as reinforcing goja/runtime patterns but not as a direct threshold trigger.

## Follow-up review questions

1. Should **Conservative repair boundary** become a Tribal entry now, or should it wait for another non-Sanitize project?
2. Should **Tree-sitter as structural prefilter plus semantic layer** remain covered by the On-Ramp, or does it deserve a separate Tribal entry after implementer review?
3. Should Scenario Runtime Workbench count toward [[Tribal/goja-execution-model]] as a variation, or should scenario runtimes become their own future pattern?
