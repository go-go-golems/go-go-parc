---
title: devctl — Project Architecture Overview
aliases:
  - devctl architecture overview
  - devctl operator system map
tags:
  - architecture-garden
  - devctl
  - architecture
  - operator
status: active
type: architecture-pattern-study
pattern_maturity: candidate-ecosystem-pattern
created: 2026-07-26
analyzed: 2026-07-26
analysis_schema: architecture-garden-v1
repository: /home/manuel/workspaces/2026-07-07/prod-tiny-idp/devctl
repository_remote: git@github.com:go-go-golems/devctl.git
repository_commit: 303e264ab9f0d9721fc8a03eac8ed95e822735c8
repository_ref: task/prod-tiny-idp
repository_commit_date: 2026-07-26T17:44:09-04:00
repository_worktree: clean
analysis_commit: 7379e4d2ff9be55f546a1361f87e3f43c244f7ab
source_ticket: DEVCTL-OPERATOR-UX-001
related_files:
  - cmd/devctl/main.go
  - cmd/devctl/cmds/root.go
  - pkg/repository/repository.go
  - pkg/engine/pipeline.go
  - pkg/operator/controller.go
  - pkg/operator/planner.go
  - pkg/operator/requests.go
  - pkg/operator/results.go
  - pkg/operator/events.go
  - pkg/operator/errors.go
  - pkg/tui/model.go
related_notes:
  - "[[Research/Software Architecture Garden/devctl/README]]"
  - "[[PROJECT REPORT - devctl - Durable Operator State, Structured Logs, and Robust Dynamic Commands]]"
---

# Project Architecture Overview

`devctl` turns repository-specific knowledge into a controlled development environment. A repository declares plugins and profiles. Plugins derive configuration, validate prerequisites, execute finite build or preparation phases, and return a launch plan. The operator converts that plan into durable service attempts. Wrappers own long-running child processes. CLI and TUI clients inspect and manipulate the resulting environment through typed contracts.

The architecture is easier to understand when divided into four planes:

1. The **description plane** computes what the repository wants.
2. The **control plane** performs lifecycle transactions.
3. The **evidence plane** records what actually happened.
4. The **presentation plane** exposes the control and evidence contracts to people and scripts.

These planes are not separate programs. They are responsibility boundaries inside one Go binary and its plugin processes.

## The system boundary

The core binary owns orchestration, process supervision, state validation, log capture, output contracts, and user interfaces. A plugin owns repository-specific policy. A launched service owns its application behavior but not its supervision metadata.

| Concern | Owner | Representation |
|---|---|---|
| Plugin selection | Repository/profile loader | `.devctl.yaml`, optional override, profile |
| Effective configuration | Engine pipeline | configuration patches |
| Build and preparation | Plugin operations | typed phase requests and results |
| Intended services | Planner | `engine.LaunchPlan` |
| Lifecycle transaction | `operator.Controller` | typed request, event stream, result |
| Durable environment | `runstate.Store` | `.devctl/state.json` |
| Concrete execution attempt | `runstate.Store` | `.devctl/runs/<run-id>/run.json` |
| Process ownership | Supervisor and wrapper | PID/start token, owner and ready artifacts |
| Terminal result | Wrapper and reconciliation | `exit.json`, `ExitSummary` |
| Exact service output | Wrapper | `stdout.log`, `stderr.log` |
| Machine-readable output | `runlog` | sequenced `logs.jsonl` |
| Human and scripted operation | CLI/TUI | Glazed rows, JSONL, Bubble Tea views |

The key constraint is ownership. If a plugin started and supervised the service, the operator could not safely stop it. If the TUI maintained a separate process model, CLI and TUI status could disagree. If the wrapper decided which services should exist, repository policy would leak into a low-level process component. The current design keeps those responsibilities separate.

## The complete `up` path

An `up` command crosses every major boundary:

```mermaid
sequenceDiagram
    participant U as User
    participant C as Cobra/Glazed command
    participant R as Repository loader
    participant P as Plugin pipeline
    participant O as Operator controller
    participant S as runstate.Store
    participant V as Supervisor
    participant W as Wrapper
    participant A as Application service

    U->>C: devctl up [service...]
    C->>O: Up(ctx, request, eventSink)
    O->>R: load config and selected profile
    R->>P: start selected plugins
    P-->>O: LaunchPlan
    O->>S: lock, reconcile, create planned runs
    O->>V: start every prepared wrapper
    V->>W: __wrap-service --request request.json
    W->>A: start child process group
    W->>S: owner.json and ready.json
    O->>V: complete health for every started run
    V->>S: phase=ready and HealthResult
    O-->>C: typed events and OperationResult
    C-->>U: table, JSON, or JSONL
```

The 2026-07-26 reviewed snapshot deliberately uses two passes: all selected wrappers start before any health check begins. This ordering matters when an earlier service becomes healthy only after a later service is present. A single start-and-health loop would encode accidental launch-plan ordering as a readiness dependency.

Pseudocode for the control flow is:

```text
plan = planner.Plan(request)
selected = select(plan.services, request.selection)

with repositoryLock:
    reconcileExistingState()
    runs = createPlannedRuns(selected)
    publishDesiredEnvironment(runs)

    startErrors = {}
    for run in runs:
        startErrors[run.id] = supervisor.startWrapper(run)

    for run in runs:
        if startErrors[run.id]:
            recordStartFailure(run)
            continue
        if supervisor.completeHealth(run) fails:
            stopOwnedRun(run)
            recordHealthFailure(run)
            continue
        recordReady(run)
```

The two-pass staging is a small local algorithm with a broad architectural implication: a plan is treated as one environment, not a list of independent sequential programs.

## The description plane

`pkg/repository` loads configuration, resolves the selected profile, discovers plugin specifications, and constructs runtime inputs. `pkg/runtime` starts each provider and implements the NDJSON request/response transport. `pkg/engine.Pipeline` sequences supported operations such as:

- `config.mutate`;
- `build.run`;
- `prepare.run`;
- `validate.run`;
- `launch.plan`.

The engine does not supervise the long-running services returned by `launch.plan`. It produces the description consumed by the operator. This distinction permits plugins in Python, shell, JavaScript, or another language while preserving one Go implementation of process safety.

The pipeline also handles strictness, dry-run behavior, and merged configuration. These are description-time concerns. Once a `ServiceSpec` becomes a run record, it is copied into durable state so the concrete attempt can be inspected independently of a later config change.

## The control plane

`pkg/operator.Controller` is the public application boundary:

```go
type Controller interface {
    Up(context.Context, UpRequest, EventSink) (OperationResult, error)
    Down(context.Context, DownRequest, EventSink) (OperationResult, error)
    Restart(context.Context, RestartRequest, EventSink) (OperationResult, error)
    Snapshot(context.Context, SnapshotRequest) (Snapshot, error)
    Logs() runlog.Reader
    Doctor(context.Context, DoctorRequest) (DoctorReport, error)
}
```

The interface is narrow enough for the TUI to fake in tests and rich enough for the CLI to stream progress. It returns domain values rather than presentation text. The controller accepts injected planning, supervision, clocks, identifiers, and log readers through `ControllerOptions`, which makes lifecycle tests deterministic without replacing the public API.

The controller does not run continuously. Each command reconstructs the necessary view from durable state and artifacts. This is the defining difference between devctl and a daemon-based supervisor.

## The evidence plane

The evidence plane contains two levels:

- `state.json` describes the current desired environment and points to current or last runs.
- each run directory describes one execution attempt and contains its evidence.

The wrapper continues after the initiating CLI exits. It writes ownership and readiness artifacts, captures both streams, writes structured records, waits for the child, and publishes an exit artifact. Reconciliation later compares those artifacts with stored identities and current operating-system process facts.

This design accepts that no single writer observes the whole lifecycle synchronously. The controller observes planning and startup. The wrapper observes the child. A later CLI observes durable evidence. Reconciliation is the algorithm that joins those observations.

## The presentation plane

The CLI is a Cobra application with Glazed fields and renderers. The TUI is a Bubble Tea model. Both are clients:

```mermaid
flowchart LR
    CTRL[operator.Controller] --> SNAP[Snapshot]
    CTRL --> EVT[OperatorEvent]
    LOG[runlog.Reader] --> REC[LogRecord]
    SNAP --> CLI[CLI status/lifecycle]
    EVT --> CLI
    REC --> CLI
    SNAP --> TUI[Overview/Runs]
    REC --> TUI2[Logs]
```

This arrangement permits multiple output formats without multiplying lifecycle implementations. The CLI can render rows or JSONL. The TUI can maintain selection, modal state, and terminal dimensions. Neither decides whether a PID is owned or whether an exit artifact is valid.

Embedded Glazed help forms a third presentation surface. It teaches the same command and protocol contracts from Markdown compiled into the binary. The help system is initialized once in `cmd/devctl/main.go`, alongside logging and command registration.

## Why the architecture works

The system works because it distinguishes three kinds of fact:

- **Intent**: the selected profile and desired service state.
- **Evidence**: immutable observations about a concrete run.
- **Projection**: the current snapshot shown to a user.

A plan is intent. A ready artifact is evidence. A status row is a projection. Confusing these categories produces most supervision errors. For example, a desired-running service can have an exited run. Reporting only one value would lose either the operator's intent or the observed failure.

The design also gives each cross-process transition a durable publication point. Atomic files are visible only when complete. Run IDs prevent a restart from overwriting the prior attempt. Start tokens prevent PID reuse from turning old state into authority over a new process. Sequence cursors prevent timestamps from being the only log ordering mechanism.

## Failure paths define the architecture

Normal startup alone does not justify the design. The stronger evidence lies in failure handling:

- A malformed or old state version fails explicitly instead of being guessed.
- A concurrent lifecycle command receives an operation-busy error.
- A wrapper without readiness evidence cannot be treated as ready.
- A healthy process whose exit artifact later appears is reconciled to terminal state.
- A PID/start-token mismatch is not signaled.
- A health failure stops only the owned run and preserves the failed attempt.
- A dynamic command whose provider handshake changed is rejected as stale.
- A log journal replaced during follow is treated as corrupt rather than silently reset.

The error types and tests make these behaviors contracts rather than documentation claims.

## When another project should reuse this shape

This four-plane architecture applies to tools that:

- compute an environment or workflow from repository policy;
- start long-running local processes;
- must survive the initiating command;
- need several user interfaces;
- require post-failure evidence;
- can share a repository-local filesystem.

It is not automatically appropriate for a single foreground command, a production cluster already governed by Kubernetes, or a remote multi-user control plane. Those systems have different authority and consistency requirements.

## Key points

- Plugins describe repository policy; the operator owns lifecycle semantics.
- The desired environment and concrete run attempts are distinct durable objects.
- Wrappers own child processes and publish evidence after the initiating command exits.
- Reconciliation joins stored claims, wrapper artifacts, and operating-system facts.
- CLI, TUI, and help are presentation clients, not independent control planes.
- Two-pass start and health staging treats the launch plan as a complete environment.
