---
title: Scenario Runtime Workbench
aliases:
  - Scenario Runtime Workbench
  - Pod Deployment Demo
  - pod-deployment-demo
tags:
  - project
  - go
  - react
  - reconciliation
  - scenario-runtime
status: active
type: project
created: 2026-03-13
repo: /home/manuel/code/wesen/2026-03-13--pod-deployment-demo
---

# Scenario Runtime Workbench

This project is a scenario-driven reconciliation demo built as an interactive workbench. The current product identity is broader than the repository name suggests: the codebase started from a pod deployment demo, but it now behaves as a generic runtime for inspectable controller-style loops where Go owns the lifecycle, JavaScript owns scenario semantics, and React renders the resulting snapshots.

> [!summary]
> The project currently has three tightly related identities:
> 1. a teaching tool for visible reconciliation loops
> 2. a debugging workbench for observe, compare, plan, and execute behavior
> 3. a small platform for authoring scenario packages in JavaScript on top of a stable Go runtime

## Why this project exists

Most controller demos only show outcomes. This one is designed to show reasoning.

The central idea is that a reconciliation loop should be inspectable as four distinct stages:

- observe the world
- compare actual state to desired state
- plan corrective actions
- execute those actions

The project exists to make those boundaries visible to a user at runtime. Instead of hiding everything inside one opaque reconcile function, the system publishes snapshots that expose desired state, observed state, computed drift, planned actions, and execution logs. That makes it useful both for onboarding and for debugging controller-like behavior.

## Current project status

The repository is in an active prototyping and cleanup phase.

What already exists:

- a Go server and CLI entrypoint under `cmd/scenario-demo`
- a generic scenario catalog loader in `internal/scenario/catalog`
- a session/runtime layer in `internal/scenario/runtime`
- HTTP and WebSocket transport in `internal/scenario/server`
- an embedded React workbench in `ui/` and `internal/web`
- three example scenario packages:
  - `scenarios/taco-fleet`
  - `scenarios/zombie-fleet`
  - `scenarios/space-station`
- embedded help and reference docs in `internal/doc/`

What is still in motion:

- the repo and module still carry `pod-deployment-demo` naming even though the product has generalized into a scenario runtime workbench
- there are active ticket workspaces in `ttmp/2026/03/13/` for runtime cleanup and UI polish
- the project is still refining its frontend presentation and internal modular boundaries rather than sitting in a finished product state

## Project shape

At a high level, the project has four layers:

1. **Scenario package**
   - `scenario.json`
   - `spec.json`
   - `ui.json`
   - `observe.js`
   - `compare.js`
   - `plan.js`
   - `execute.js`
2. **Generic Go runtime**
   - catalog loading
   - session lifecycle
   - tick execution
   - event publication
3. **Transport layer**
   - HTTP snapshot and mutation endpoints
   - WebSocket event stream
4. **React workbench**
   - preset selection
   - generated controls
   - runtime controls
   - structured state panels and logs

## Architecture

```text
React workbench
  -> HTTP + WebSocket API
  -> Go session/runtime
  -> Goja sandbox
  -> scenario package with JS stage files
```

This asymmetry is deliberate.

Go owns lifecycle, session state, timing, transport, and snapshot publication. JavaScript owns scenario-specific meaning: what the world looks like, what counts as drift, what plan should be proposed, and what side effects execution should produce. React stays presentation-focused and renders backend-authored snapshots rather than inventing local truth.

Key code locations:

- `cmd/scenario-demo/main.go`
- `internal/app/`
- `internal/scenario/catalog/catalog.go`
- `internal/scenario/runtime/session.go`
- `internal/scenario/runtime/vm.go`
- `internal/scenario/server/handler.go`
- `internal/web/`
- `ui/src/ScenarioApp.tsx`
- `ui/src/scenario/useScenarioSession.ts`

## Scenario model

Each scenario is a complete package under `scenarios/<id>/`. The runtime expects every package to provide metadata, desired-state defaults, generated UI control definitions, and the four JavaScript stage files. That package structure is rigid on purpose: the runtime stays generic because every scenario speaks the same contract even when the internal domain is completely different.

The Goja sandbox is intentionally narrow. Scenario code can use helper functions such as `getState`, `setState`, `log`, `randomFloat`, `randomInt`, and `round`, but it does not get arbitrary access to server internals. That keeps presets expressive without turning the runtime into a general-purpose plugin host.

## Current user-facing commands

The most important current entrypoints are:

```bash
go run ./cmd/scenario-demo serve
go run ./cmd/scenario-demo serve --addr :4010 --scenarios-dir ./scenarios
go run ./cmd/scenario-demo help
go run ./cmd/scenario-demo help operating-the-demo
go run ./cmd/scenario-demo help runtime-architecture
go generate ./internal/web
go test ./...
```

The browser surface is centered on `http://localhost:3001` by default. For debugging, `/api/session/snapshot` is the authoritative backend state and is the first thing to compare against the UI when behavior looks wrong.

## Important project docs

The most useful repo-local docs are:

- `/home/manuel/code/wesen/2026-03-13--pod-deployment-demo/README.md`
- `/home/manuel/code/wesen/2026-03-13--pod-deployment-demo/internal/doc/pod-deployment-demo.md`
- `/home/manuel/code/wesen/2026-03-13--pod-deployment-demo/internal/doc/operating-the-demo.md`
- `/home/manuel/code/wesen/2026-03-13--pod-deployment-demo/internal/doc/runtime-architecture.md`
- `/home/manuel/code/wesen/2026-03-13--pod-deployment-demo/internal/doc/reconciliation-loop-reference.md`
- `/home/manuel/code/wesen/2026-03-13--pod-deployment-demo/internal/doc/authoring-scenarios.md`
- `/home/manuel/code/wesen/2026-03-13--pod-deployment-demo/internal/doc/intern-guide-to-scenario-runtime.md`

There are also active ticket workspaces that show the current development direction:

- `/home/manuel/code/wesen/2026-03-13--pod-deployment-demo/ttmp/2026/03/13/SCENARIO-CLEANUP-001--cleanup-and-modularization-plan-for-scenario-runtime-and-workbench/`
- `/home/manuel/code/wesen/2026-03-13--pod-deployment-demo/ttmp/2026/03/13/UI-POLISH-001--syntax-highlighted-code-view-and-ui-navigation-improvements/`

## Open questions

- Should the repository itself be renamed to match the current scenario-runtime identity?
- How far should the frontend remain a thin snapshot renderer versus gaining richer local ergonomics?
- What is the right long-term boundary between generic runtime behavior in Go and authoring affordances for scenario packages?
- Should scenario authoring eventually become a more formal extension workflow rather than a folder convention?

## Near-term next steps

- continue the cleanup and modularization work around the scenario runtime and workbench
- keep consolidating docs so the current embedded help remains the canonical explanation
- refine the React workbench around code visibility, navigation, and debugging workflow
- add or evolve presets in ways that prove the runtime is truly generic rather than only a renamed pod simulator

## Project working rule

> [!important]
> Treat the backend session snapshot as the source of truth.
> If the UI looks wrong, compare it to `/api/session/snapshot` before debugging presentation code.

## KB reviews

- [[KB-BATCH9-tree-sitter-structured-text]] (2026-05-11) — Batch C analysis; treated this as an adjacent structured runtime and Goja variation rather than a Tree-sitter project.

## Related KB entries

- [[Tribal/goja-execution-model]] — related variation: Go owns lifecycle and runtime boundaries while JavaScript owns scenario semantics.

**Tribal candidates** (not yet at 3-project threshold):
- Scenario package contract (1/3) — metadata, desired state, UI schema, and stage scripts as a reusable authoring shape.
- Observe/compare/plan/execute visible reconciliation loop (1/3) — controller reasoning split into inspectable phases.
- Backend snapshot as source of truth (1/3) — UI renders backend-authored snapshots instead of inventing local truth.
- Go-owned lifecycle with JS-owned scenario semantics (1/3) — scenario-specific behavior in JS on top of a stable Go runtime.
