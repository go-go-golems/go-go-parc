---
title: "devctl — Repository-Local Development Environment Orchestration"
aliases:
  - devctl
  - devctl MOC
  - devctl architecture
  - development environment operator
tags:
  - knowledge-base
  - project
  - devctl
  - go
  - orchestration
  - plugins
status: active
type: knowledge-base
created: "2026-09-13"
repo: /home/manuel/code/wesen/go-go-golems/devctl
---

# devctl — Repository-Local Development Environment Orchestration

`devctl` is a Go operator for repository-defined development environments. Plugins compute configuration, execute bounded preparation phases, and describe services; the core operator owns lifecycle transactions, process supervision, durable run evidence, structured logs, and CLI/TUI presentation.

> [!summary]
> - **Description:** profile-selected plugins produce validated lifecycle recipes and launch plans.
> - **Control:** the operator and wrappers own service startup, health, restart, shutdown, and process identity.
> - **Evidence:** repository-local state, immutable run records, journals, and artifact provenance make failures inspectable.
> - **Extension namespace:** built-in and plugin commands share one validated `CommandNamespace` registry.

## Architecture garden

Read the garden in order for the architectural narrative:

1. [[Research/Software Architecture Garden/devctl/01 - Project Architecture Overview|Project Architecture Overview]] — four-plane system map and the command namespace registry pattern.
2. [[Research/Software Architecture Garden/devctl/02 - Durable State Process Identity and Wrapper Evidence|Durable State, Process Identity, and Wrapper Evidence]].
3. [[Research/Software Architecture Garden/devctl/03 - Reconciliation and the Shared Operator Boundary|Reconciliation and the Shared Operator Boundary]].
4. [[Research/Software Architecture Garden/devctl/04 - Structured Run Journals and Observable Execution|Structured Run Journals and Observable Execution]].
5. [[Research/Software Architecture Garden/devctl/05 - Declarative Plugins and Validated Dynamic Commands|Declarative Plugins and Validated Dynamic Commands]].
6. [[Research/Software Architecture Garden/devctl/06 - CLI TUI Help and Contract Shaped Presentation|CLI, TUI, Help, and Contract-Shaped Presentation]].
7. [[Research/Software Architecture Garden/devctl/07 - Architecture Evidence Debt and Ecosystem Guidelines|Architecture Evidence Debt and Ecosystem Guidelines]].

## Deep dives and implementation history

- [[PROJECT REPORT - devctl - Transactional Lifecycles, Process Ownership, and Executable Provenance]] — detailed analysis of staged lifecycle transactions, bounded plugin shutdown, immutable native executable identity, truthful state projections, catalog provenance, and command namespace policy.
- [[PROJECT REPORT - devctl - Durable Operator State, Structured Logs, and Robust Dynamic Commands]] — durable operator and dynamic-command implementation report.
- [[ARTICLE - devctl Service Lifecycle Controls - Start Stop Restart and the Midstream Redesign]] — lifecycle control evolution.
- [[ARTICLE - devctl Service Restart - Replanning Service Specs Without Persisting Secrets]] — safe restart replanning.
- [[ARTICLE - Devctl Trace Profiles - Pinocchio and CoinVault]] — practical profile integrations.

## Reusable patterns

### Command namespace registry

An extensible CLI owns a symbol table shared by built-ins and provider-defined commands. `CommandNamespace` registers canonical names and aliases once, validates plugin catalog candidates against immutable snapshots, and prevents catalog production from disagreeing with later command installation.

The pattern generalizes to routes, event types, schema identifiers, and capability names: register host symbols and validate extension symbols through one policy object rather than maintaining a parallel reserved-name list. See [[Research/Software Architecture Garden/devctl/01 - Project Architecture Overview#Pattern command namespace registry|Pattern: command namespace registry]].

### Lifecycle recipe and prepared launch

Effect-free resolution produces a versioned recipe; effectful preparation produces a candidate launch; validation under the lifecycle lock rejects stale configuration before changing the running environment.

### Durable ownership evidence

PID plus process start token, wrapper-owned process groups, run-scoped records, and explicit readiness/exit publication distinguish current authority from historical observation.

### Content-addressed executable provenance

Build-produced native executables are copied into immutable SHA-256 paths, linked to run records, revalidated before launch, and garbage-collected by current/previous references.

## Ecosystem relationships

- [[glazed]] — structured command schemas, output middleware, Cobra integration, and embedded help used by devctl. The command namespace registry complements Glazed by governing host/plugin names before Cobra rendering.
- [[go-go-goja]] — JavaScript host and provider ecosystem that can participate in plugin-authored tooling.
- [[pinocchio]] — a consumer of devctl profiles and orchestration workflows.
- [[docmgr]] — ticket documentation and implementation provenance used for devctl design work.

## Repository map

Repository: `/home/manuel/code/wesen/go-go-golems/devctl`

| Concern | Location |
|---|---|
| Root CLI and command namespace | `cmd/devctl/cmds/root.go`, `command_namespace.go` |
| Dynamic plugin commands and catalog UX | `cmd/devctl/cmds/dynamic_commands.go`, `plugins.go` |
| Plugin protocol runtime | `pkg/runtime` |
| Pipeline and launch descriptions | `pkg/engine`, `pkg/operator/planner.go` |
| Lifecycle transactions | `pkg/operator/controller.go` |
| Durable environment and run state | `pkg/runstate` |
| Service/wrapper supervision | `pkg/supervise` |
| Structured logs | `pkg/runlog` |
| Terminal UI | `pkg/tui` |
| Embedded operational help | `pkg/doc/topics` |

## Working rules

- Plugins describe intent; the operator owns lifecycle and long-running processes.
- Resolve effect-free facts before executing preparation work.
- Revalidate prepared state under the repository lock before mutation.
- Keep current projections distinct from retained historical evidence.
- Route all root command names and aliases through the command namespace registry.
- Preserve exact machine-readable error and output contracts across CLI and TUI surfaces.
