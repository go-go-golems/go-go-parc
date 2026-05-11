---
title: "Tree-sitter for Go Tools"
aliases: [tree-sitter go, tree-sitter queries, syntax-aware tooling, ast tooling]
tags: [knowledge-base, on-ramp, tree-sitter, go, ast, parsing, tooling]
status: active
type: knowledge-base
created: 2026-05-11
---

# Tree-sitter for Go Tools

> [!summary]
> Tree-sitter gives Go tools fast, concrete syntax trees with error recovery and incremental parsing. Our projects use it for AST query experiments, syntax-aware code expansion, YAML/JSON sanitizing, and parser-backed repair workflows where regexes alone are too blind and compiler front ends are too heavy.

## The idea in one paragraph

Tree-sitter is a parsing library that produces concrete syntax trees for source code and structured text. It was designed for editor workflows: it can parse incomplete text, preserve exact source spans, and update a tree incrementally after edits. In our Go tools it sits between line regexes and full compilers: it tells us what shape the text has, where it is broken, and which spans are safe enough to inspect or transform.

## Why we care

Several PARC reports are hard to read without this mental model. `Query Treesitter` explores query languages on top of syntax trees. `Tree-sitter Templating` uses incremental parses and query matches to propose deterministic editor expansions. `Sanitize` uses Tree-sitter for YAML/JSON diagnostics, conservative repair targeting, and browser parse-tree inspection. The shared idea is: **syntax structure becomes an engineering signal**. It decides whether a rule fires, whether a repair is safe, and whether a UI can explain what happened.

Public docs explain grammars and queries, but not the Go-tooling pattern our projects use: parse once, preserve spans, layer heuristics or semantic relations on top, and keep fixes conservative.

## The 5 things to understand

### 1. Tree-sitter gives structure, not meaning

A Tree-sitter tree can show that a JavaScript function has a name node, a YAML mapping has repeated-looking keys, or a JSON document contains an `ERROR` node. It does not know your application semantics. That is why our projects add layers above it: TUQL experiments with relations such as `desc`, `inside`, and `same_tree`; Hybrid TUQL adds `declares`, `uses`, and `resolves_to`; `Sanitize` adds duplicate-key traversal, strict parser checks, and line heuristics.

### 2. Queries are a structural prefilter

Tree-sitter queries are excellent for local syntax shapes. They become awkward when a tool needs repeated subtree equality, declaration/use resolution, or multi-step joins. The likely direction from `Query Treesitter` is layered: Tree-sitter for fast prefiltering, a readable query surface for authoring, joins for relationships, and host-language predicates for project-specific logic.

### 3. Incremental parsing matters in editors

`Tree-sitter Templating` depends on the editor-oriented part of Tree-sitter. The frontend sends text changes; the Go backend reparses incrementally; the rule engine filters matches by changed range; then it returns proposals or patches. The browser does not invent expansions, so every suggestion is traceable to parse state, rule state, and guard state.

### 4. Error recovery is not validity

Tree-sitter can produce a tree for malformed text. That is useful, but it does not mean the input is valid for downstream tools. The JSON side of `Sanitize` tracks both Tree-sitter structural health and strict `encoding/json` validity. Comments and multiple top-level values may still have parseable-looking trees while strict JSON rejects them. Tree-sitter can localize trouble; it does not by itself authorize a rewrite.

### 5. Spans are the bridge to fixes and UI

The practical value is often the span: byte ranges, rows, columns, and nodes that a CLI or UI can point at. The YAML side of `Sanitize` became coherent once `documentAnalysis` kept parse errors, duplicate-key occurrences, and line indexes together. After that, parse, lint, duplicate-key handling, and fix orchestration reused the same structural facts instead of each pass inventing its own view of the file.

## The gotchas we've hit

### Treating queries as a full semantic engine

`Query Treesitter` exists because raw queries are not enough for repeated subtree equality, lexical scope, and declaration/use reasoning. Native Tree-sitter remains the right structural substrate, but semantic relations need another layer.

### Letting the frontend invent syntax-aware behavior

`Tree-sitter Templating` keeps parse state, rules, trigger policies, and guards in the Go backend. If Monaco-side heuristics start deciding which expansion should fire, the system becomes two engines that can disagree.

### Confusing parser recovery with valid output

The JSON recovery work showed this most clearly. Wrapper stripping, comments, Python literals, duplicate commas, and trailing commas can be repaired narrowly. Missing commas, missing colons, single quotes, unquoted keys, duplicate keys, and multiple top-level values mostly stay lint-only because repair would require guessing intent.

### Writing regex fixers without structural evidence

The YAML engine improved when Tree-sitter stopped being a sidecar and became part of one shared analysis object. Duplicate-key traversal, parse errors, mixed indentation, and span-rich diagnostics now flow through the same analysis path, which makes fixes more explainable.

### Auto-repairing beyond the evidence

Both YAML and JSON converge on the same rule: conservative repair over aggressive magic. Tree-sitter makes the boundary visible, but the tool still has to stop when intent is ambiguous.

## Where to go deeper

1. **Tree-sitter documentation** — <https://tree-sitter.github.io/tree-sitter/> — parsers, queries, incremental parsing, and grammar tooling.
2. **Tree-sitter Go bindings** — <https://github.com/tree-sitter/go-tree-sitter> — parser and query integration from Go.
3. [[PROJ - Query Treesitter - Tree-sitter Query Language Prototypes and Design]] — query layers above raw Tree-sitter.
4. [[PROJ - Tree-sitter Templating - Syntax-Aware Code Expansion System]] — Go backend + Monaco example.
5. [[PROJ - Sanitize - Tree-sitter Structured Text Sanitizer]] — parse-aware lint/repair workflow.

### Related PARC project reports

- [[PROJ - Query Treesitter - Tree-sitter Query Language Prototypes and Design]] — TUQL, unification, relational AST queries, and semantic relations above Tree-sitter.
- [[PROJ - Tree-sitter Templating - Syntax-Aware Code Expansion System]] — Tree-sitter as backend authority for syntax-aware expansion proposals.
- [[PROJ - Sanitize - Tree-sitter Structured Text Sanitizer]] — format-aware CLI, library, and browser playground.
- [[PROJ - Sanitize - YAML Sanitizing Deep Dive]] — shared parse-aware analysis feeding lint and conservative fixes.
- [[PROJ - Sanitize - JSON Recovery Experiments and Limits]] — parser recovery checked against strict validation before output is trusted.
