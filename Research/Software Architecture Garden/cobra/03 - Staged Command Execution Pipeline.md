---
title: Staged Command Execution Pipeline
aliases:
  - Cobra execution lifecycle
  - Parse validate execute pipeline
status: established
type: architecture-garden-design
created: 2026-08-16
analyzed: 2026-08-16
repository: https://github.com/spf13/cobra
repository_remote: https://github.com/spf13/cobra.git
repository_commit: adbc8813901bba65827259daa8e22ff94ec1f30e
tags:
  - architecture-garden
  - cobra
  - lifecycle
  - validation
  - execution
related_files:
  - command.go
  - args.go
  - command_test.go
related_notes:
  - "[[Research/Software Architecture Garden/cobra/README|Cobra architecture study]]"
  - "[[Research/Software Architecture Garden/cobra/04 - Late Defaults with User Override]]"
  - "[[Research/Software Architecture Garden/cobra/05 - Constraint Metadata Drives Validation and Completion]]"
---

# Staged Command Execution Pipeline

## Why this note exists

A CLI command is not just a callback. Before an effect should run, the framework must identify the target command, parse the right flag scope, validate positional arguments, run preparation hooks, enforce required and cross-flag constraints, and establish context. Cobra makes that ordering visible in `ExecuteC` and `execute` rather than scattering it among command handlers.

> [!summary]
> **Pattern:** funnel every invocation through an ordered execution pipeline whose validation and preparation stages complete before the effect-owning handler runs.
>
> **Law:** the main command effect runs only after routing, parsing, argument validation, pre-run preparation, required-flag validation, and flag-group validation have succeeded.

## Concrete pipeline

At the root, `ExecuteC` establishes a background context when none exists, normalizes execution to the root command, initializes default infrastructure, chooses `Find` or `Traverse`, propagates context to the selected child, and then calls the child's internal `execute` method.

The selected command then proceeds through a stricter sequence:

```text
initialize default help/version flags
parse flags
handle help/version short-circuits
require runnable command
run framework initializers
validate positional arguments
run persistent pre-run hook(s)
run local PreRun/PreRunE
validate required flags
validate flag groups
run Run/RunE
run local PostRun/PostRunE
run persistent post-run hook(s)
framework finalizers are deferred after initialization
```

`args.go` supplies small validator functions (`NoArgs`, `ExactArgs`, `RangeArgs`, `OnlyValidArgs`, etc.) and `MatchAll` composes validators into one `PositionalArgs` contract.

## Why it works

The pipeline gives framework concerns stable linearization points. A handler does not need to remember to check required flags after parsing, nor does every subcommand need to reimplement parent preparation.

The separation is particularly useful for error semantics. `RunE` owns the domain effect and can return an error; parsing and validation return before it is entered. This makes “invalid invocation” distinct from “effect attempted and failed.”

## Hook ordering

Persistent hooks are hierarchy-aware. With `EnableTraverseRunHooks` disabled, Cobra executes only the first applicable persistent pre/post hook found according to its traversal. With it enabled, pre-hooks run root-to-leaf and post-hooks leaf-to-root. Tests assert these sequences explicitly.

This is a useful refinement of the generic middleware idea: ordering is part of the contract, not just “some hooks run.”

## Critical non-guarantee: post-hooks are not cleanup

Cobra's local and persistent `PostRun*` functions are ordinary later pipeline stages. If argument validation fails, a required flag is absent, a flag group is invalid, or `RunE` returns an error, execution returns before those post-hooks.

Framework `OnFinalize` callbacks are different: after `preRun()` is entered, `postRun()` is installed with `defer`, so those finalizers have stronger exit-path behavior for the scope they cover.

Therefore:

```text
PostRun / PersistentPostRun != finally / defer
```

A command that acquires a resource inside `RunE` and must release it on every path should use Go `defer` in the effect-owning scope (or another guaranteed cleanup construct), not rely on `PostRunE`.

## Failure modes and tricky details

### Hook behavior can be process-global

`EnableTraverseRunHooks` changes persistent-hook semantics for the process. A reusable execution engine should prefer executor- or graph-scoped policy unless global behavior is deliberately part of compatibility.

### Validation placement has semantics

Argument validation occurs before persistent/local pre-run hooks, while required-flag and flag-group validation occur after pre-run hooks. Code placed in pre-hooks may therefore run for an invocation later rejected by flag constraints. Applications should keep pre-hooks idempotent and avoid irreversible effects when later validation can still fail.

### `DisableFlagParsing` changes the boundary

Commands may opt out of Cobra flag parsing and receive raw arguments. This intentionally opens the pipeline for wrapper/plugin commands but transfers parsing and validation responsibility to the command.

## Testing and evidence

`command_test.go` contains focused lifecycle tests, context propagation tests, routing tests, and persistent-hook order assertions. `args.go` makes positional validation composable and independently testable. The pipeline is directly visible in `command.go` rather than inferred from documentation.

## Applicability

Reuse this pattern for CLIs, job runners, request dispatchers, plugin hosts, and workflow engines where effects should have a clear admission sequence.

Do not over-stage trivial functions. The value appears when multiple commands share parsing, validation, policy, and lifecycle semantics and when the ordering itself prevents mistakes.

## Candidate ecosystem guidance

> **Make effect admission an explicit ordered pipeline. Name the point at which an invocation becomes eligible to perform effects, test hook order, and document which later-stage hooks are skipped on error.**

## Evidence and references

- `command.go`: `ExecuteC`, `execute`, context propagation, hook ordering, required/flag-group validation, deferred finalizers.
- `args.go`: reusable positional argument validators and `MatchAll` composition.
- `command_test.go`: command routing, context, lifecycle and persistent hook ordering tests.
