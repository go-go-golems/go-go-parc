---
title: Tree-sitter Templating
aliases:
  - Tree-sitter Templating
  - Syntax-Aware Code Expansion System
  - Project Tree-sitter Templating
tags:
  - project
  - tree-sitter
  - go
  - react
  - monaco
  - websocket
status: active
type: project
created: 2026-03-14
repo: /home/manuel/code/wesen/2026-03-14--treesitter-templating
---

# Tree-sitter Templating

This project is a working prototype for syntax-aware code expansion. The goal is to sit between static snippets and unconstrained AI generation: a Go backend parses the current document with Tree-sitter, evaluates rule presets against AST matches, and sends deterministic code proposals to a React + Monaco frontend over WebSocket.

> [!summary]
> The project currently has three clear identities:
> 1. a Tree-sitter integration prototype for incremental parsing and query-driven matching
> 2. a rule-driven code expansion system with presets, guards, and proposal modes
> 3. a browser-based editor demo that makes those expansions visible and accept/rejectable

## Why this project exists

The underlying problem is real and narrow: developers often know that one structural piece of code implies several nearby follow-up pieces, but the current tooling choices are awkward.

- Static snippets are too context-blind.
- Full AI generation is too unconstrained and non-deterministic.
- Raw Tree-sitter queries are good at matching syntax, but they are not themselves a user-facing expansion workflow.

This repo is trying to make a more reliable middle layer: recognize a syntax pattern, check a few structural conditions, and propose a small set of concrete edits that are easy to preview and accept.

## Current project status

This repository is already beyond the pure-design stage. The main architecture from the ticket plan exists in code, and the core backend packages have tests that pass.

What already exists:

- a Go HTTP/WebSocket server in `cmd/server/`
- incremental JavaScript parsing in `pkg/parser/`
- a rule engine in `pkg/rules/` that runs Tree-sitter queries, filters by changed ranges, applies trigger policies, checks idempotence guards, and renders text edits
- per-session document state in `pkg/session/`
- preset loading from JSON in `pkg/presets/`
- a React + Monaco frontend in `frontend/` with a preset picker, suggestion UI, and debug panel
- example preset files in `presets/`
- integration tests for parser, rules, and WebSocket flow
- a docmgr ticket workspace in `ttmp/2026/03/14/TST-001--tree-sitter-templating-syntax-aware-code-expansion-system/`

What is still unfinished or intentionally partial:

- backend language support is effectively JavaScript-only today even though some frontend types mention TypeScript and TSX
- debounce and workflow-order trigger strategies are still placeholders rather than finished runtime behavior
- the current UI is a prototype shell rather than a polished editing product
- there is no persistent session store or multi-user model yet

## The simplest mental model

The simplest way to think about the project is:

1. the frontend sends editor changes and cursor position
2. the backend reparses incrementally with Tree-sitter
3. rules inspect changed syntax regions and decide whether to fire
4. the backend returns either proposals or patches
5. the frontend previews or applies those edits

That is the whole system. The intelligence is meant to live in the rule and preset layer, not in the browser.

## Project shape

The repo is organized in a clean three-part shape.

### 1. Go backend

- `cmd/server/main.go` starts the HTTP server, WebSocket endpoint, preset API, and optional static frontend serving.
- `pkg/parser/` owns Tree-sitter initialization, incremental reparsing, and query execution.
- `pkg/rules/` owns rule definitions, trigger policies, guard checks, fired-key idempotence, and expansion planning.
- `pkg/session/` owns in-memory per-session state such as current text, version, active rules, cursor position, and fired keys.
- `pkg/protocol/` owns the typed message protocol and the WebSocket handler.
- `pkg/presets/` loads preset JSON from disk.

### 2. Frontend demo

- `frontend/src/App.tsx` composes the editor, preset picker, suggestion UI, and debug panel.
- `frontend/src/components/Editor.tsx` mounts Monaco, sends text changes, listens for patches, and binds accept/reject shortcuts.
- `frontend/src/ws/client.ts` handles the WebSocket session lifecycle.
- `frontend/src/store/useStore.ts` keeps the local session, proposal, debug, and editor state in Zustand.

### 3. Documentation and planning

- `ttmp/.../design-doc/01-architecture-and-implementation-plan.md` is the cleanest statement of intended architecture and rollout phases.
- `ttmp/.../tasks.md` shows all ten planned phases as completed.
- `ttmp/.../reference/01-diary.md` explains what was implemented, what was tricky, and what remains weak.

## Architecture

At runtime the system looks like this:

```text
Monaco editor
  -> WebSocket client
  -> Go protocol handler
  -> session manager
  -> incremental Tree-sitter parser
  -> rule engine
  -> expansion proposal or document patch
  -> frontend preview / accept / reject
```

A few architectural choices matter more than the rest:

- The backend is authoritative. The browser does not invent expansions.
- Presets are data-driven JSON bundles rather than hard-coded UI features.
- Rules combine four layers: query match, trigger policy, guard policy, and expansion action.
- Idempotence is handled both structurally and session-locally through required-missing-symbol checks and fired-key memory.

## Current user-facing commands

The practical entrypoints are simple:

```bash
make build
make frontend-build
make test
go run ./cmd/server
```

The default development shape is a local Go server plus the Vite frontend in `frontend/`.

## What the prototype demonstrates well

The project already proves a few important things.

### 1. Tree-sitter is viable as the structural backbone

`pkg/parser/parser.go` shows a clean incremental parse loop: initialize the parser, edit the old tree, parse against the edited tree, and inspect changed ranges. That confirms the repo's core technical assumption.

### 2. The preset abstraction is good enough to drive real behavior

The preset files are not just configuration theater. They define query patterns, trigger strategies, guard policies, and expansion templates for concrete workflows like function scaffolding and React-style handler follow-ups.

### 3. The end-to-end proposal loop exists

The frontend opens a session, sends edits, receives debug/proposal messages, and can accept a proposal into the document. This is already a real interactive prototype rather than a disconnected backend library.

## Important current limitations

There are also a few clear boundaries in the current implementation.

### 1. Some trigger modes are still stubs

The rule engine currently treats `node-stable-for-ms` as effectively always true, and ordered workflow completion is still a TODO. The architecture anticipates richer behavior than the runtime currently enforces.

### 2. Versioning is intentionally loose

The session layer documents the version field as informational rather than strict. That keeps the prototype simple, but it also means conflict handling is not yet the main design concern.

### 3. The frontend is functional but thin

The app proves the interaction loop, but it is still mostly a debugging and exploration surface. The visual layer is not yet the core product.

### 4. Language scope is narrower than the vocabulary suggests

The frontend types mention `typescript` and `tsx`, but the backend parser wiring currently supports `javascript`. This is better understood as a JavaScript-first prototype with an obvious expansion path.

## Important project docs

The most useful repo-local references are:

- `/home/manuel/code/wesen/2026-03-14--treesitter-templating/ttmp/2026/03/14/TST-001--tree-sitter-templating-syntax-aware-code-expansion-system/design-doc/01-architecture-and-implementation-plan.md`
- `/home/manuel/code/wesen/2026-03-14--treesitter-templating/ttmp/2026/03/14/TST-001--tree-sitter-templating-syntax-aware-code-expansion-system/tasks.md`
- `/home/manuel/code/wesen/2026-03-14--treesitter-templating/ttmp/2026/03/14/TST-001--tree-sitter-templating-syntax-aware-code-expansion-system/changelog.md`
- `/home/manuel/code/wesen/2026-03-14--treesitter-templating/ttmp/2026/03/14/TST-001--tree-sitter-templating-syntax-aware-code-expansion-system/reference/01-diary.md`

## Open questions

- Should presets stay JSON-only, or eventually become editable in the UI?
- Should the next grammar target be TypeScript/TSX, or should the project deepen JavaScript semantics first?
- How strict should session versioning and conflict handling become once the prototype grows beyond a single-user demo?
- Should expansion templates stay simple string substitution, or move to a more expressive templating layer?
- Is the long-term value mainly editor UX, or mainly a reusable backend expansion engine that other tools can call?

## Near-term next steps

- finish real debounce and workflow-order trigger behavior
- add TypeScript/TSX grammar support if multi-language editing is a goal
- add stronger frontend E2E coverage
- improve the proposal/preview UX beyond the current debug-oriented shell
- decide whether the project is primarily a demo app or a reusable engine plus protocol

## Project working rule

> [!important]
> Keep the backend authoritative and data-driven.
> If a behavior matters, make it emerge from parse state, rules, and presets rather than from ad hoc frontend heuristics.

## KB reviews

- [[KB-BATCH9-tree-sitter-structured-text]] (2026-05-11) — Batch C analysis; contributed to [[On-Ramp/tree-sitter-for-go-tools]] and backend-authoritative syntax tooling candidates.

## Related KB entries

- [[On-Ramp/tree-sitter-for-go-tools]] — incremental parsing, query-driven matching, and backend-owned syntax behavior.

**Tribal candidates** (not yet written / needs review):
- Backend-authoritative syntax tooling (1/3) — backend owns parse state, rule evaluation, and proposals; frontend renders and applies.
- Rule = query + trigger + guard + expansion (1/3) — data-driven decomposition of syntax-aware expansion behavior.
- Fired-key idempotence for editor proposals (1/3) — session-local memory prevents repeated suggestions.
- Changed-range filtered rule evaluation (1/3) — incremental parse changes limit which rules fire.
