---
title: Goja REPL Hardening
aliases:
  - Goja REPL Hardening
  - REPL Hardening
  - Project Goja REPL Hardening
tags:
  - project
  - goja
  - repl
  - go
  - sqlite
  - runtime
status: active
type: project
created: 2026-04-08
repo: /home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja
---

# Goja REPL Hardening

This project was a focused cleanup, bug-fix, and architectural hardening pass over the REPL/session stack in `go-go-goja`. The work started from a branch review of the new REPL service and then turned into three implementation tracks: persistence correctness, evaluation control, and structural cleanup.

The goal was not to redesign the whole system. The goal was to make the current design trustworthy. That meant fixing correctness bugs that could corrupt expectations around persistence, making timeout behavior real instead of partial, and reducing the amount of critical behavior hidden inside one oversized service file.

> [!summary]
> This project delivered three concrete outcomes:
> 1. persistent sessions now behave more correctly, especially around deletion, ID generation, and SQLite integrity settings
> 2. evaluation timeouts now cover both awaited promises and synchronous runaway code, with recovery tests proving the session stays usable
> 3. the `replsession` package is now split into clearer responsibility areas, so review and maintenance are substantially easier

## Why this project exists

The original review of the REPL branch found a pattern that is common in fast-moving subsystems: the code mostly worked for happy-path usage, but the invariants were weaker than they looked. Some of the most important problems were not dramatic crashes. They were more subtle:

- deleted sessions could still appear in normal reads
- durable session IDs were generated in a way that could collide across processes
- SQLite foreign key enforcement was configured too weakly for pooled runtime connections
- timeout handling existed in partial form but did not yet give a complete operational story
- `pkg/replsession/service.go` had become too large and too responsibility-dense to review confidently

None of these issues individually required a total rewrite. But together they made the subsystem harder to trust. A REPL service is infrastructure code. Infrastructure code needs invariants that are simple enough to explain and strong enough to test.

## Current project status

This hardening pass is complete at the planned ticket level.

The three main implementation tracks were:

- `GOJA-040`: persistence correctness
- `GOJA-041`: evaluation control
- `GOJA-042`: cleanup and refactor

The code work for all three tracks is implemented on the branch `task/add-repl-service`. The outcome is not just a cleaner package layout. The more important result is that the system now has a better behavioral contract:

- deleted persistent sessions are hidden from normal reads
- default durable session IDs no longer depend on process-local counters
- SQLite integrity settings are applied on connection open
- evaluation deadlines can stop both never-settling async flows and synchronous infinite loops
- sessions remain usable after timeout recovery
- the package structure now better reflects the actual conceptual boundaries in the subsystem

## Project shape

At a high level, the project touched three layers at once:

1. **Persistence layer**
   - how sessions are stored
   - how sessions are listed and looked up
   - which database invariants are actually enforced
2. **Evaluation layer**
   - how JavaScript code is executed
   - how `await` is handled
   - how timeouts interrupt or fail work
3. **Session orchestration layer**
   - how the REPL service owns runtime state
   - how evaluation results are summarized
   - how persistence state and runtime state are tied together

That means this was not a pure refactor and not a pure bug-fix sprint. It was a reliability pass across the seams between storage, runtime control, and service structure.

## Architecture

The current mental model is:

```text
user / API request
  -> replapi
  -> replsession.Service
  -> engine runtime owner
  -> goja VM execution
  -> result shaping / observation
  -> persistence updates
  -> repldb / SQLite
```

A more detailed internal view after the cleanup looks like this:

```text
pkg/replapi
  -> request/config parsing
  -> create session options
  -> call replsession

pkg/replsession/service.go
  -> lifecycle / session wiring / high-level orchestration

pkg/replsession/evaluate.go
  -> code rewrite path
  -> sync eval
  -> await handling
  -> timeout and interrupt flow

pkg/replsession/persistence.go
  -> shapes persisted session and history state
  -> translates runtime/session state into DB-facing records

pkg/replsession/observe.go
  -> summaries, variable snapshots, cell observations

pkg/repldb
  -> SQLite open/bootstrap/read/write
```

The important design lesson here is that the REPL system is not just "execute some JS". It is a stateful service that has to coordinate four things correctly:

- JavaScript runtime ownership
- persistence semantics
- timeout/interruption behavior
- API option resolution

## Persistence hardening

The persistence work focused on making the database-backed session behavior actually match the intended semantics.

### Main fixes

- deleted sessions are now hidden from normal read paths
- default persistent session IDs are collision-resistant
- SQLite integrity settings are applied when connections are opened, not only during bootstrap

### Why those fixes matter

The deleted-session bug was dangerous because it creates policy drift. The system looked like it supported soft deletion, but normal read paths still surfaced deleted data. That means the actual contract was "deleted unless you hit the wrong code path," which is not a real contract.

The session ID issue was a durability bug. A process-local counter is not a valid strategy for persisted IDs if more than one process can write to the same backing store. That is exactly the kind of problem that can stay invisible in single-process testing and then fail later under normal CLI or service usage.

The SQLite issue mattered because `PRAGMA foreign_keys = ON` is connection-local. Setting it once during bootstrap is weaker than it looks if later operations happen on other pooled connections. The right invariant is not "we once enabled foreign keys." The right invariant is "every active connection is opened with the intended integrity settings."

### Key code locations

- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/pkg/repldb/read.go`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/pkg/repldb/store.go`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/pkg/replsession/service.go`

### Conceptual invariant

```text
If session.deleted_at is set,
then normal list/get paths must behave as if the session does not exist.
```

### Persistence pseudocode

```text
open database with integrity settings

when creating a persistent session:
  if user did not provide id:
    generate opaque unique id
  insert session row

when listing or fetching sessions:
  exclude rows marked deleted

when deleting:
  mark deleted_at
  future normal reads must not return it
```

## Evaluation control hardening

The evaluation-control work was the most subtle part of the project because it involved both asynchronous and synchronous failure modes.

### Main fixes

- session policy now includes `timeoutMs`
- promise waiting is deadline-aware
- synchronous runaway execution can be interrupted on timeout
- interrupt state is cleared after unwind so the session remains usable
- tests now prove recovery after timeout

### Why this was tricky

There was an early false lead during investigation: an interrupt experiment using `goja_nodejs/eventloop` appeared to show that interruption would not work. That conclusion turned out to be too broad because the experiment was not interrupting the same runtime that the actual service path used.

The decisive experiment reproduced the real `engine.Runtime -> Owner.Call -> rt.VM.RunString(...)` path. In that actual path, interrupting the active VM and then clearing the interrupt state after unwind worked correctly. That changed the design from "timeouts probably need a bigger rebuild strategy" to "the current architecture can support real synchronous timeout recovery."

### Evaluation flow

```text
evaluate code
  -> rewrite if needed
  -> run inside runtime owner
  -> start timeout watcher
  -> if context deadline fires:
       interrupt VM
  -> wait for unwind
  -> clear interrupt state
  -> return timeout result
```

### Recovery invariant

```text
After a timed-out evaluation,
the same session must still be able to evaluate a later cell successfully.
```

### Key code locations

- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/pkg/replsession/policy.go`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/pkg/replsession/evaluate.go`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/pkg/replsession/service_policy_test.go`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/ttmp/2026/04/07/GOJA-041-EVALUATION-CONTROL--add-timeouts-interruption-and-eval-edge-case-tests/scripts/04-engine-runtimeowner-interrupt-sync-loop/main.go`

### Important caveat

Raw-mode declaration-style top-level `await` is still unsupported by design. Expression-style top-level `await` works, but declaration-style cases such as `const x = await ...` are still outside the supported raw-mode contract. That is documented and tested, but not expanded.

## Cleanup and refactor work

The cleanup track was not meant to produce fewer lines of code. It was meant to produce code that has fewer hidden responsibilities per file.

Before this pass, `pkg/replsession/service.go` was carrying too much conceptual load:

- lifecycle setup
- evaluation flow
- persistence shaping
- runtime observation
- summary generation
- helper logic for multiple domains

That made review harder because every change had to be understood in the context of many neighboring concerns.

### Main refactor result

The package is now split roughly like this:

- `service.go`: lifecycle and top-level service orchestration
- `evaluate.go`: evaluation pipeline and timeout/interrupt behavior
- `persistence.go`: persisted session and history shaping
- `observe.go`: summaries, snapshots, and observation helpers

This is a separation-of-concerns improvement, not a code-size optimization. The total amount of logic is similar, but the mapping between file and responsibility is much clearer.

### Boundary clarification

One useful cleanup result was making the `replapi.SessionOptions` versus `replsession.SessionOptions` split easier to understand. The project did not add a backwards-compatibility adapter layer. Instead, it made the current boundary easier to read and added focused coverage for create-session option resolution.

The review also concluded that the Bobatea evaluator path was not dead deprecated code. It is still part of the active system and should be treated as such unless removed deliberately.

### Key code locations

- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/pkg/replsession/service.go`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/pkg/replsession/evaluate.go`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/pkg/replsession/persistence.go`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/pkg/replsession/observe.go`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/pkg/replapi/config.go`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/pkg/replapi/config_test.go`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/pkg/repl/adapters/bobatea/replapi.go`

## Validation

The work was validated continuously while the implementation was being split into reviewable commits.

Main validation commands:

```bash
go test ./pkg/repldb ./pkg/replapi ./pkg/replsession
go test ./pkg/replapi ./pkg/repl/adapters/bobatea ./pkg/repl/evaluators/javascript
go test ./...
golangci-lint run -v
```

The ticket documentation was also validated with `docmgr doctor`, and the ticket bundles were refreshed to reMarkable after implementation.

## Important project docs

The most important repo-local documentation for this hardening pass is:

- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/ttmp/2026/04/07/GOJA-040-PERSISTENCE-CORRECTNESS--fix-repl-persistence-correctness-and-sqlite-integrity/`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/ttmp/2026/04/07/GOJA-041-EVALUATION-CONTROL--add-timeouts-interruption-and-eval-edge-case-tests/`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/ttmp/2026/04/07/GOJA-042-REPL-CLEANUP--refactor-session-kernel-and-api-shape-cleanup/`
- `/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja/ttmp/2026/04/08/repl-hardening-project-report.md`

Those ticket directories include the analysis docs, implementation diaries, scripts, tasks, and changelogs for each track.

## Open questions

- Should raw-mode top-level `await` support eventually be broadened beyond the current expression-style contract?
- Is the current runtime ownership model the long-term architecture, or should timeout/interruption behavior eventually be isolated behind a stronger execution boundary?
- Are there still API-shape cleanups worth doing in `replapi`, or is the current boundary now clear enough to stop?
- Should the current ticket docs be turned into permanent repo docs after the branch is merged?

## Near-term next steps

- split the branch work into clean PRs if that has not been done yet
- review CI closely for timeout-related flakes
- decide whether any remaining raw-mode `await` limitations deserve a follow-up ticket
- consider promoting the strongest parts of the ticket documentation into stable repo docs

## Project working rule

> [!important]
> Prefer strengthening invariants before adding new behavior.
> In the REPL/session stack, subtle correctness bugs are usually more important than adding one more convenience feature.

## KB reviews

- [[KB-BATCH6-mixed-domain]] (2026-05-11) — concept extraction + classification
