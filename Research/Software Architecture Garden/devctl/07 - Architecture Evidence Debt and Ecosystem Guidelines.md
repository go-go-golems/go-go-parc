---
title: devctl — Architecture Evidence, Debt, and Ecosystem Guidelines
aliases:
  - devctl architecture assessment
  - devctl ecosystem guideline candidates
tags:
  - architecture-garden
  - devctl
  - testing
  - architecture-debt
  - ecosystem-guidelines
status: active
type: architecture-guideline-candidates
pattern_maturity: mixed
created: 2026-07-26
analyzed: 2026-07-26
analysis_schema: architecture-garden-v1
repository: /home/manuel/workspaces/2026-07-07/prod-tiny-idp/devctl
repository_remote: git@github.com:go-go-golems/devctl.git
repository_commit: 303e264ab9f0d9721fc8a03eac8ed95e822735c8
repository_ref: task/prod-tiny-idp
repository_commit_date: 2026-07-26T17:44:09-04:00
repository_worktree: clean
analysis_commit: 7379e4deefc8167e0e6049b440fc1721cab83e21
source_ticket: DEVCTL-OPERATOR-UX-001
related_files:
  - pkg/runstate/store_test.go
  - pkg/runstate/identity_linux_test.go
  - pkg/runlog/reader_test.go
  - pkg/operator/controller_test.go
  - pkg/operator/reconcile_test.go
  - cmd/devctl/cmds/help_tree_test.go
  - cmd/devctl/cmds/dynamic_commands_test.go
  - pkg/tui/model_test.go
  - pkg/tui/testdata/overview-44x16.golden
  - pkg/doc/topics/devctl-v2-upgrade.md
  - ttmp/2026/07/24/DEVCTL-OPERATOR-UX-001--heavy-user-reliability-logging-cli-and-tui-analysis-and-design/reference/01-investigation-diary.md
related_notes:
  - "[[Research/Software Architecture Garden/devctl/README]]"
  - "[[Research/Software Architecture Garden/rag-evaluation-system/09 - Candidate Ecosystem Guidelines]]"
---

# Architecture Evidence, Debt, and Ecosystem Guidelines

Architecture becomes durable when behavior is asserted at the boundary where it matters. `devctl` contains strong evidence in state goldens, process-identity tests, lifecycle tests, JSONL contracts, command-tree tests, dynamic catalog drift tests, TUI goldens, race runs, security checks, live tmux exercises, and a chronological investigation diary. This evidence also reveals the remaining limits more accurately than a package diagram alone.

## Tests as architecture evidence

The test suite protects different contract types with different methods.

| Contract | Evidence |
|---|---|
| Persisted schema | golden `environment-v2` JSON and store validation tests |
| Atomic update and revisions | runstate atomic/store tests |
| Process ownership | Linux PID/start-token tests |
| Lock exclusion | runstate lock tests |
| Wrapper handshake | supervisor wrapper/request tests |
| Lifecycle ordering | controller tests, including start-all-before-health |
| Reconciliation | artifact/identity fixtures and snapshot exit tests |
| Journal framing | oversized and partial record tests |
| Query/follow | filter, cursor, replacement, exit-artifact tests |
| CLI schema | JSONL, phase, profile, logs, usage tests |
| Command discoverability | help-tree and completion tests |
| Dynamic injection | collision, drift, provider selection tests |
| TUI behavior | fake controller model tests |
| Terminal layout | three golden terminal sizes |
| Concurrency | focused race tests |
| End-to-end behavior | smoke tests and tmux operator matrix |

The method matches the contract. Serialized data receives goldens and decode tests. Process behavior receives real child processes. Terminal layout receives golden views. CLI streaming receives line-oriented framing tests. This supports a broader guideline already emerging from the `rag-evaluation-system` study: validation technique should correspond to the kind of promise being made.

## Review findings as architecture probes

Pull request #11 identified three issues that are useful beyond their patches.

### Start all wrappers before health

The original loop started and health-checked one service before starting the next. This treated launch-plan order as a hidden dependency. The corrected two-pass algorithm recognizes the selected services as one environment. The regression test asserts that every wrapper is started before the first health completion call.

### Follow durable exit evidence

The original follower checked only `run.json`. Since the wrapper writes `exit.json` asynchronously, the follower could deliver final output and still wait forever. The fix teaches a broader rule: a derived projection must not outrank the durable event that makes it stale.

### Preserve successful health

Reconciliation initially converted every live run with a health specification to `starting`, even after a successful health result. The fix preserves stronger evidence. Reconciliation should not be a reset to conservative defaults; it should be a monotonic interpretation of valid evidence where possible.

These comments found design errors because they followed cross-component sequences, not because individual functions were malformed.

## Live testing as evidence

The ticket diary records tmux-based tests against short-lived and multi-service fixtures. Live testing found the stale snapshot problem that unit tests had not originally represented. A wrapper wrote `exit.json`, but status remained ready until another mutating command reconciled.

The resulting rule is now encoded in `Controller.Snapshot`: projection reads reconcile under the repository lock. The diary is valuable because it preserves the path from observed output to architectural correction. Without it, the commit would show what changed but not why the earlier model was insufficient.

## Solid patterns

The following patterns have enough source and test evidence to be treated as strong local implementations:

- PID plus start-token process ownership.
- Atomic JSON state with version and revision validation.
- Repository-scoped mutation locking.
- Wrapper request, ownership, readiness, and exit artifacts.
- Desired environment separated from run attempts.
- Reconciliation from artifacts and current process facts.
- Start-all-before-health lifecycle staging.
- Raw streams plus sequenced JSONL.
- Cursor follow with journal replacement detection and exit-artifact termination.
- Typed controller consumed by CLI and TUI.
- Static command precedence and deterministic dynamic command conflicts.
- Live provider validation after catalog selection.
- Embedded Glazed help and structured CLI output.

## Architecture debt and explicit limits

### Manual retention

Completed runs are preserved indefinitely. This is safe for diagnosis and unsafe for long-term disk bounds. A retention design needs policies and invariants:

- never delete a current run;
- preserve recent failed runs longer than routine successes;
- support dry-run reporting;
- coordinate deletion with followers;
- bound by count, age, and total bytes;
- keep state and artifacts internally consistent.

Deletion should not be added as an incidental `down` side effect.

### Polling

Runlog follow and TUI refresh use polling. Polling is understandable, testable, and adequate at current repository scale. Its debt is potential latency and repeated I/O, not demonstrated incorrectness. Measurement should precede filesystem notification or a daemon.

### Older low-level APIs

The repository still contains `pkg/state`, `pkg/supervise` methods predating the controller boundary, and `pkg/servicecontrol`. Some remain active implementation dependencies; others may have external consumers. They should not be removed or wrapped speculatively.

A cleanup requires:

1. enumerate internal call sites;
2. search known downstream repositories;
3. classify each symbol as implementation detail, supported API, or dead path;
4. decide whether breaking removal is acceptable;
5. remove obsolete behavior and tests together.

The ecosystem preference against compatibility adapters applies here. Do not create another layer merely to preserve an API without known consumers.

### Cross-platform process identity

Linux has a strong `/proc` start token. Other platforms may have weaker or different implementations. The schema is portable, but the strength of ownership evidence depends on the platform implementation. Cross-platform release claims should state and test those guarantees explicitly.

### Test fixture timing

`TestSupervisor_PostReadyCrashIsObservable` uses a Python HTTP server terminated after a short interval. It passed in isolated and full validation for the analyzed commit, but an earlier run demonstrated sensitivity under load. The production contract is valid; the fixture can be made more deterministic with a repository-owned helper that binds, announces readiness, and exits on a controlled timer.

### Security scan boundary

`gosec` passed during the implementation campaign. `govulncheck` was not completed when external dependency metadata access was not authorized. These are different checks. The record should not imply that source static analysis proves dependency vulnerability status.

## Patterns not to repeat

- Do not let each UI infer process state independently.
- Do not use PID existence as ownership.
- Do not overwrite a prior run when restarting a named service.
- Do not run health checks before the whole selected environment has started.
- Do not make a follower wait only on a stale projection when a durable exit artifact exists.
- Do not downgrade proven healthy state during reconciliation.
- Do not use raw formatted terminal output as an automation API.
- Do not let plugin load order resolve command ambiguity.
- Do not trust cached provider metadata for side-effecting execution.
- Do not keep compatibility commands without consumers and removal criteria.

## Candidate ecosystem guidelines

### Candidate 1: Separate intent, attempt, evidence, and projection

**Rule:** A durable operator should model desired state, concrete attempt identity, immutable evidence, and user-facing projection as separate concepts.

**Evidence:** `EnvironmentState`, `RunRecord`, wrapper artifacts, and `Snapshot`.

**Compare against:** deployment controllers, release runs, ingestion jobs, device sessions.

**Promotion test:** A failed or restarted attempt remains diagnosable without corrupting the desired-state model.

### Candidate 2: Persist process start identity

**Rule:** Any tool that later signals a persisted PID must also validate an operating-system process-start identity.

**Evidence:** `ProcessIdentity` and Linux `/proc` tests.

**Compare against:** local web-server launchers, demo runners, test harnesses, browser drivers.

**Promotion test:** PID reuse cannot cause the tool to signal an unrelated process.

### Candidate 3: Use atomic documents plus a transaction lock

**Rule:** Atomic rename protects a document; a repository lock protects a lifecycle transition spanning documents and processes. Use both when both scopes exist.

**Evidence:** `writeJSONAtomic`, revisions, and `Locker.WithExclusive`.

**Compare against:** local indexes, code-generation manifests, release state, sync tools.

**Promotion test:** Readers never observe truncated data, and concurrent mutations fail deterministically.

### Candidate 4: Reconcile from the strongest evidence

**Rule:** Reconciliation should validate all available evidence, preserve stronger proven states, and return unknown on contradiction.

**Evidence:** ready/health preservation, exit reconciliation, identity mismatch.

**Compare against:** GitOps status, background job recovery, cache rebuilds.

**Promotion test:** Repeated reconciliation is idempotent and never converts contradiction into false success.

### Candidate 5: Share one application controller across interfaces

**Rule:** CLI, TUI, HTTP, and editor surfaces should call one typed application boundary rather than invoke or parse each other.

**Evidence:** `operator.Controller`, CLI commands, fake-controller TUI tests.

**Compare against:** release tooling, infrastructure CLIs, knowledge-base applications.

**Promotion test:** Adding a presentation surface requires no new lifecycle semantics.

### Candidate 6: Preserve raw evidence beside structured projections

**Rule:** When exact source bytes and machine query are both legitimate requirements, capture both from the source rather than reconstructing one from the other.

**Evidence:** raw stdout/stderr plus `logs.jsonl`.

**Compare against:** transcript normalization, audit events, HTTP capture, evaluation traces.

**Promotion test:** Structured consumers have identity and bounds while forensic consumers retain exact input.

### Candidate 7: Discovery metadata does not authorize execution

**Rule:** Use catalogs to select candidates, then validate the live provider before side effects.

**Evidence:** plugin catalog fingerprint and runtime handshake comparison.

**Compare against:** xgoja providers, Widget registries, release graphs, tool catalogs.

**Promotion test:** stale or ambiguous metadata produces a deterministic error before execution.

### Candidate 8: Start an environment before evaluating inter-service readiness

**Rule:** For a selected multi-service environment, establish all process presence before waiting on service health unless explicit dependency stages say otherwise.

**Evidence:** PR #11 controller fix and regression test.

**Compare against:** Compose-like tools, integration harnesses, tiny-idp demo applications.

**Promotion test:** readiness dependencies do not rely on accidental list order.

### Candidate 9: Documentation is part of the executable contract

**Rule:** Embed operational tutorials and migration guides in versioned CLI binaries when commands and state contracts change together.

**Evidence:** Glazed help topics and v2/plugin migration guides.

**Compare against:** other Glazed applications and generated help browsers.

**Promotion test:** an installed binary can explain its own state format, migration, and troubleshooting without an external version lookup.

### Candidate 10: Match tests to contracts

**Rule:** Use schema goldens for serialized data, behavioral tests for lifecycle, race tests for concurrency, terminal goldens for layout, and live fixtures for cross-process sequences.

**Evidence:** the layered devctl suite and diary.

**Compare against:** rag-evaluation-system Storybook/goldens, publish-vault reload tests, identity-service acceptance.

**Promotion test:** every architectural invariant names a validation method capable of detecting its failure.

## Consolidation agenda

The next useful work is comparison, not immediate standardization.

1. Analyze tiny-idp development and demo launchers against the devctl operator boundary.
2. Compare devctl run journals with go-minitrace transcript and event identity.
3. Compare the plugin catalog with xgoja provider declarations and Widget registries.
4. Compare atomic state and snapshot reconciliation with publish-vault reload state.
5. Extract a Tribal guideline only after at least two projects share the same constraint and invariant.

## Key points

- Tests reveal architecture most clearly when they target the correct contract type.
- PR review exposed sequence-level defects across components.
- The strongest patterns have both durable representations and failure tests.
- Manual retention, polling, legacy API coexistence, and cross-platform identity remain explicit limits.
- Ten candidate rules are ready for comparison, not automatic ecosystem promotion.
