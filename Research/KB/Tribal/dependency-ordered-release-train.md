---
title: "Dependency-Ordered Release Trains — How We Do It"
aliases:
  - release train
  - dependency-ordered release
  - multi-repo release
  - ggg rollout
  - go-go-golems release train
  - PR readiness
tags: [knowledge-base, tribal, release, go, dependencies, github, ci, codex, rollout]
status: active
type: knowledge-base
created: 2026-05-31
repos:
  - /home/manuel/code/wesen/go-go-golems/infra-tooling
---

# Dependency-Ordered Release Trains — How We Do It

> [!summary]
> A release train moves one change through several Go repositories that depend on each other, enforcing a single invariant: a repository may merge only after every upstream module version it requires has already been merged, tagged, and made visible to normal Go module resolution. The dependency order is built from `go.mod` direct requirements automatically. Three independent gates (local validation, GitHub checks, Codex review) must pass before merge. The `ggg` CLI provides read-only planning (`inventory → init → plan → validate`) and mutating execution (`branch → push-prs → apply`). A small dashboard (SQLite + Python + HTTP) tracks batch state. The Glazed linter enforces three project conventions that prevent common release-train failures.

## The pattern

A release train is a dependency-ordered batch of PRs across multiple repos. The core invariant:

> A repository may merge only after every upstream module version it requires has already been merged, tagged, and made visible to normal Go module resolution.

This is stricter than "the code compiles in a branch" and stricter than "the PR is merged." Go downstream users import module versions, not pull requests. If a downstream PR needs `go-go-goja@v0.6.0`, then `v0.6.0` must exist and be visible through `GOWORK=off go list -m -versions`.

### Building the dependency graph from `go.mod`

The dependency order is not hand-maintained. It is derived from `go.mod`:

```bash
awk '/^require[[:space:]]+github\.com\/go-go-golems\// { print $2 } \
     /^[[:space:]]*github\.com\/go-go-golems\// { print $1 }' go.mod | sort -u
```

This handles both single-line `require` and `require (...)` blocks. If the dependencies change, the order changes. The method remains the same.

Example xgoja rollout order:

```
go-go-goja
  → geppetto
      → pinocchio
          → css-visual-diff
  → direct go-go-goja leaf repositories
      → discord-bot, go-minitrace, loupedeck, workspace-manager, goja-git
```

### Three independent gates before merge

| Gate | What it checks | Failure response |
|---|---|---|
| **Local validation** | `GOWORK=off go test ./...` proves the published dependency graph works | Fix the code or bump dependencies |
| **GitHub checks** | CI status: test, lint, vulnerability scan, GoSec, CodeQL | Fix the reported issue |
| **Codex review** | AI review feedback on the current head | Address substantive feedback; wait for thumbs-up |

All three must be satisfied independently. A PR with passing CI but stale Codex feedback is not ready. A PR with current Codex thumbs-up but failing checks is not ready.

### ggg rollout verbs

The `ggg` CLI follows a read-only-first, mutate-later discipline:

```bash
ggg rollout inventory    # list affected repositories
ggg rollout init         # create rollout state file
ggg rollout plan         # compute dependency order and PR list
ggg rollout validate     # run read-only checks on all repos
ggg rollout branch       # create feature branches (mutating)
ggg rollout push-prs     # push branches and open PRs (mutating)
ggg rollout status       # show current batch state
ggg rollout report       # emit final report
```

The read-only commands (`inventory`, `init`, `plan`, `validate`) can be run safely without changing any repository. The mutating commands (`branch`, `push-prs`, `apply`) change state and should be tested with dry runs first.

### PR readiness model

A PR is ready when:

1. At least one status check exists
2. Every check run is completed with `SUCCESS`, `SKIPPED`, or `NEUTRAL`
3. Every legacy status context is successful
4. A Codex signal exists
5. The latest Codex signal has no `EYES` reaction
6. The latest Codex signal has a thumbs-up or satisfied body
7. A Codex-authored body is not substantive review feedback

The batch readiness table is an operator dashboard:

```
STATUS             FAILED_CHECKS        PR
READY              -                    geppetto/pull/362
WAITING_CODEX      -                    discord-bot/pull/9
WAITING_CHECKS     pending_checks       workspace-manager/pull/20
FAILED_CHECKS      checks,lint          goja-git/pull/1
CODEX_FEEDBACK     checks,test          css-visual-diff/pull/8
```

### Dashboard: intentionally small

The INFRA-004 dashboard is one SQLite database, one Python CLI, and one auto-refreshing HTTP page. It tracks batches, states, validation records, events, PR URLs, merge SHAs, and main-branch verification. It does not try to be a full CI system.

### The Glazed linter: three conventions that prevent release-train failures

The `glazedclilint` analyzer enforces three rules:

1. **No direct `os.Getenv`** in CLI code — use Glazed parameter binding instead
2. **No raw Cobra/go flag definitions** in Glazed verbs — use `glazedflag` wrappers
3. **No output flags on non-structured commands** — structured output commands must declare their format explicitly

These rules prevent the most common class of release-train friction: a repository that builds locally but fails `golangci-lint run` in CI because of undocumented flag assumptions or environment-variable dependencies.

## Why we do it this way

**`GOWORK=off` is the difference between "compiles for me" and "compiles for users."** A local `go.work` file lets sibling repositories develop together, but it hides missing tags. During release validation, the same `go.work` makes downstream repositories resolve against local checkouts instead of published versions. Disabling it makes Go resolve dependencies as an external user would.

**Early PRs reduce feedback latency; late merges enforce correctness.** Opening a downstream PR starts CI and Codex review immediately. The dependency invariant applies to merge and release, not to opening a review branch. In the xgoja rollout, downstream PRs were opened for all 8 repositories simultaneously, but merged only after upstream tags were published.

**Three independent gates prevent single-point-of-failure release decisions.** If CI and Codex were merged into one gate, a passing Codex review would not catch CI failures and vice versa. Keeping them independent means each gate catches what the others miss.

**The dependency graph from `go.mod` is always current.** A manually curated package list becomes wrong as soon as the repository adds or removes a dependency. Reading `go.mod` follows the file Go actually uses.

**The read-only planner prevents accidental mutations.** `ggg rollout plan` and `validate` can be run safely without changing any repository. Only `branch`, `push-prs`, and `apply` mutate state. This discipline prevents "I ran the wrong command and now I have 10 branches to clean up."

## Evidence

| Report | Date | Contribution |
|---|---|---|
| [[ARTICLE - Implementing Go Analysis Linters - Glazed CLI Linter Deep Dive]] | 2026-05-24 | Glazed linter: three conventions, go vet analyzer, analysistest fixtures, audit-before-enforce |
| [[ARTICLE - Logcopter - Package Scoped Logging for Go CLIs]] | 2026-05-25 | Logcopter: stable package area names, hierarchical levels, generated loggers, `make logcopter-check` |
| [[ARTICLE - Managing Go-Go-Golems Release Trains]] | 2026-05-26 | Canonical description: invariant, dependency graph, GOWORK=off, early PRs / late merges, PR readiness model, Codex interaction |
| [[ARTICLE - ggg - Codex-Aware Release Tooling for Go-Go-Golems]] | 2026-05-27 | ggg CLI: prready.Snapshot, state machine, structured rows + exit codes, testdata fixtures |
| [[ARTICLE - ggg Rollout Automation - Real-World Testing and Implementation]] | 2026-05-27 | rollout verbs: inventory → plan → validate → branch → push-prs, INFRA-002 live test, policy corrections |
| [[ARTICLE - INFRA-004 Release Train Machinery - Dashboard, PR Workflow, and Rollout Control]] | 2026-05-28 | Dashboard, batch tracking, three gates, main-branch verification, failure modes catalog |

## Working rules

1. **Build the release order from `go.mod` direct requirements.** This produces a correct dependency DAG automatically. Never hand-maintain the list.

2. **Always validate with `GOWORK=off`.** Workspace tests use local replaces and are not sufficient for release readiness. `GOWORK=off go test ./...` proves the published dependency graph works.

3. **Three independent gates before merge:** local validation, GitHub checks, Codex review state. All must pass independently.

4. **Open downstream PRs early to collect feedback, but merge and publish in dependency order.** Opening a PR starts feedback. Merging a PR consumes published dependencies. These are different phases.

5. **Stop after upstream merge when an operator must approve the release tag.** Publishing a release changes the dependency graph available to downstream repositories. An operator should verify before that step.

6. **`ggg rollout` verbs follow read-only-first, mutate-later discipline.** `inventory → init → plan → validate` are safe. `branch → push-prs → apply` mutate state.

7. **Dashboard is intentionally small:** one SQLite database, one Python CLI, one auto-refreshing HTTP page. Do not grow it into a full CI system.

8. **Glazed linter enforces three conventions:** no direct `os.Getenv`, no raw Cobra flags in Glazed verbs, no output flags on non-structured commands. Treat initial failures as an audit report before making rules mandatory.

9. **Bump all go-go-golems dependencies at once**, not one at a time. Use the `bump-go-go-golems` Makefile target that scans `go.mod` and bumps every direct dependency with `GOWORK=off`.

10. **Pin the linter version.** Never use `@latest` for the linter — a breaking change in a new linter version can fail CI across all repositories simultaneously.

## Gotchas

1. **Stale Codex feedback.** Codex review state can be from a previous commit. Always check that the Codex signal targets the current head, not an earlier push. The `prready.Snapshot` compares commit identity to detect this.

2. **Go toolchain directives cause CI failures.** `go 1.26.3` in `go.mod` vs `go 1.26` in CI can cause `govulncheck` to report false positives because the vulnerability database lists fixes by exact patch version.

3. **GoReleaser scaffold placeholders cause release failures.** New repos created from templates have `.Template` placeholders in `goreleaser.yml`. These must be filled in before tagging or the release workflow fails.

4. **CGO-enabled builds fail for tree-sitter packages.** If the release workflow doesn't set `CGO_ENABLED=1` and appropriate flags, tree-sitter packages fail to build. Check the GoReleaser config for each repo that uses CGO.

5. **Generated logger areas must be preserved during rollouts.** Logcopter generates package-scoped loggers. A rollout that overwrites generated files without running `go generate` first breaks logging. Use `make logcopter-check` to verify.

6. **`no_runs` on main is a successful terminal state.** When verifying merged work on `main`, repositories that have no GitHub Actions runs should not be treated as failures. They simply don't have CI configured.

7. **Archived repositories cannot be merged.** An archived GitHub repository rejects push attempts. Remove archived repos from the rollout plan before attempting to branch.

8. **Global `log` conflicts.** Some repositories have a package-level `log` variable that conflicts with the `logcopter` generated logger. The linter catches this, but it surfaces as a confusing CI failure.

9. **`@latest` linter fallback breaks batch rollouts.** If the linter is referenced as `@latest` in a Makefile, a new release of the linter can introduce breaking checks across all repositories in the same rollout. Pin the version explicitly.

10. **Workspace `go.work` hides missing tags.** Running `go test ./...` without `GOWORK=off` can pass even when the published dependency graph is broken. Always disable the workspace for release validation.

## Related KB entries

- [[Tribal/dsl-normalized-config-compiled-plan]] — The ggg rollout plan is a compiled plan: the rollout spec is the DSL, the dependency graph and PR list are the normalized config, the validation gates produce the compiled plan. The read-only planner follows the same three-stage pipeline.
- [[Tribal/goja-runtime-ownership-and-context-propagation]] — The xgoja runtime API rollout (the canonical release train example) propagated renamed types (`RuntimeOwner`, `RuntimeServices`) across 8 downstream repositories.
