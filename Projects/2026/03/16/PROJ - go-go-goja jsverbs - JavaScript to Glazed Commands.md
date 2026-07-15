---
title: go-go-goja jsverbs
aliases:
  - go-go-goja jsverbs
  - jsverbs
  - Project jsverbs
tags:
  - project
  - goja
  - glazed
  - javascript
  - go
status: active
type: project
created: 2026-03-16
repo: /home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja
---

# go-go-goja jsverbs

This is the JavaScript-to-Glazed command-generation branch of the [[go-go-goja]] project map.

This project adds a JavaScript-defined command layer to `go-go-goja` so that plain `.js` files can be scanned, interpreted as command definitions, and exposed as ordinary Glazed verbs. The practical goal is to let a developer author command behavior in JavaScript while still getting Glazed schema generation, Cobra integration, structured output, help pages, and predictable runtime binding on the Go side.

> [!summary]
> The project currently has two tightly related identities:
> 1. a prototype JS-to-Glazed command exporting path inside `go-go-goja`
> 2. a hardening pass that turns the first spike into a reusable package with stricter parsing, diagnostics, and a clearer contract

## Why this project exists

The underlying problem is that `go-go-goja` already has a strong JavaScript runtime story, but authoring full Glazed commands directly in Go is still comparatively heavy when the command logic itself is naturally script-like. The jsverbs work closes that gap by letting JavaScript act as a command authoring surface instead of only as an embedded runtime language.

This is useful for at least three reasons. First, it lowers the cost of prototyping new commands and command trees. Second, it creates a path for packaging script-defined behaviors behind ordinary CLI ergonomics. Third, it tests a broader architectural idea inside the repo: JavaScript should not only call Go modules, but should also be able to define first-class CLI behavior that the Go host can discover, validate, and run.

## Current project status

The project is in active prototype-plus-hardening mode. The first pass proved that JavaScript files could be scanned, converted into Glazed command definitions, and executed through a source-overlay runtime that preserved relative `require()` behavior. A second pass then cleaned up the largest correctness and maintainability risks from that prototype.

What already exists:

- a reusable package in `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/pkg/jsverbs`
- an example runner in `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/cmd/jsverbs-example`
- fixture coverage in `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/testdata/jsverbs`
- shared Glazed help entries in `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/pkg/doc`
- design, postmortem, and hardening ticket docs in the repo's `ttmp/` tree

What was improved during hardening:

- the old JS-to-JSON metadata rewrite was replaced with strict AST-based literal parsing
- scanning now supports disk directories, generic `fs.FS`, and direct in-memory source strings
- scan diagnostics were added so bad metadata can fail clearly
- schema generation and runtime binding now share one internal binding plan
- promise waiting is still polling, but it is explicitly marked as a first-version tradeoff rather than accidental final design

What is still incomplete:

- runtime construction still happens per invocation instead of through a longer-lived execution service
- promise completion is still implemented with polling
- the example runner is intentionally a runner, not yet a polished production integration point for another real CLI

## Project shape

At a high level, the system has five layers:

1. source discovery
2. metadata extraction
3. command compilation
4. runtime invocation
5. help and example packaging

The important repo locations are:

- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/pkg/jsverbs/scan.go`
- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/pkg/jsverbs/model.go`
- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/pkg/jsverbs/binding.go`
- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/pkg/jsverbs/command.go`
- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/pkg/jsverbs/runtime.go`
- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/cmd/jsverbs-example/main.go`
- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/testdata/jsverbs`
- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/pkg/doc`

The simplest mental model is that `pkg/jsverbs` acts like a compiler pipeline. It scans JavaScript source for static command metadata, normalizes that metadata into typed Go structures, compiles those structures into Glazed commands, and then uses the original JavaScript source as the executable implementation at invocation time.

## Architecture

```text
JS files / embed.FS / raw source strings
  -> pkg/jsverbs/scan.go
  -> Registry + VerbSpec + SectionSpec + diagnostics
  -> pkg/jsverbs/binding.go
  -> shared binding plan
  -> pkg/jsverbs/command.go
  -> Glazed command descriptions
  -> pkg/jsverbs/runtime.go
  -> Goja runtime + source overlay loader
  -> JS function execution
  -> structured rows or text output
```

The scanner is responsible for discovery and static understanding. It recognizes top-level functions plus sentinel calls such as `__package__`, `__section__`, and `__verb__`. Those sentinels are intentionally limited to static metadata. The package now evaluates literal AST nodes directly instead of trying to rewrite JavaScript object syntax into JSON text. That change matters because it makes the contract much clearer: metadata is declarative data, not arbitrary code.

The binding layer is the contract that sits between schema generation and execution. Earlier versions risked drift because command compilation and runtime invocation each had their own interpretation of how arguments, flags, and sections should bind into JavaScript parameters. The newer binding plan centralizes that policy. That is one of the most important internal cleanup wins because it reduces a subtle class of bugs where a command could parse correctly but invoke incorrectly.

The runtime layer is deliberately practical rather than elegant. It keeps the original JavaScript source in the registry, exposes that source through an in-memory loader, and evaluates the selected function when the command runs. Relative `require()` resolution is preserved, which was one of the key runtime assumptions that the early experiments needed to prove. Promise completion is still handled through polling. That is not ideal, but it is explicit and documented as version-1 behavior rather than hidden complexity.

## Current user-facing commands

The current easiest way to see the system is the example runner:

```bash
go run ./cmd/jsverbs-example --dir ./testdata/jsverbs list
go run ./cmd/jsverbs-example --dir ./testdata/jsverbs basics greet Manuel --excited
go run ./cmd/jsverbs-example --dir ./testdata/jsverbs basics banner Manuel
go run ./cmd/jsverbs-example --dir ./testdata/jsverbs help jsverbs-example-reference
```

These commands demonstrate the major output shapes:

- ordinary structured Glazed output
- raw text writer-style output
- nested package/section command trees
- embedded help content that explains how the fixture format and package contract work

From a package API perspective, the most important entry points are:

- `ScanDir(...)`
- `ScanFS(...)`
- `ScanSource(...)`
- `ScanSources(...)`

Those four scanning modes make the project more reusable than a simple directory walker. They create a path for loading command definitions from embedded assets, generated source blobs, tests, or higher-level registries that are not tied to a local filesystem tree.

## Validation and quality checks

The implementation was exercised as both a prototype and a cleanup target. The core validation path today is:

```bash
go test ./pkg/jsverbs ./cmd/jsverbs-example
./.bin/golangci-lint run ./pkg/jsverbs ./cmd/jsverbs-example
```

The fixtures in `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/testdata/jsverbs` cover a useful spread of behaviors: inferred public functions, explicit verb metadata, shared sections, rest arguments, binding modes, promise returns, raw text output, and relative helper imports. The hardening pass also added failure-path tests for malformed metadata and invalid binding combinations, which is important because this subsystem now has a much clearer notion of what it rejects and why.

## Important project docs

The most important repo-local design and review documents are:

- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/ttmp/2026/03/16/GOJA-04-JS-GLAZED-EXPORTS--add-glazed-command-exporting-from-javascript/design-doc/01-js-to-glazed-command-exporting-design-and-implementation-guide.md`
- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/ttmp/2026/03/16/GOJA-04-JS-GLAZED-EXPORTS--add-glazed-command-exporting-from-javascript/design-doc/02-js-verbs-prototype-postmortem-and-code-review.md`
- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/ttmp/2026/03/16/GOJA-05-JSVERBS-HARDENING--harden-jsverbs-scanner-sources-diagnostics-and-binding-plan/design-doc/01-jsverbs-hardening-plan-and-implementation-guide.md`

The current user-facing help content lives in:

- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/pkg/doc/08-jsverbs-example-overview.md`
- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/pkg/doc/09-jsverbs-example-fixture-format.md`
- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/pkg/doc/10-jsverbs-example-developer-guide.md`
- `/home/manuel/workspaces/2026-03-16/add-glazed-js-layer/go-go-goja/pkg/doc/11-jsverbs-example-reference.md`

## Open questions

- Should runtime construction stay per-invocation, or should the package grow a longer-lived executor or service object?
- Should the registry gain a public incremental API such as `AddSource(...)` for callers that want to assemble command sets dynamically?
- Is the current promise polling good enough for the intended command latency profile, or should a less polling-heavy bridge be designed next?
- Should public-function inference remain part of the default contract, or should a future version require more explicit metadata?
- What is the first real non-example CLI that should consume `pkg/jsverbs` as a production integration?

## Near-term next steps

- commit the current hardening and documentation changes
- decide whether the runtime layer should be refactored around a reusable executor object
- keep extending failure-path tests as the metadata contract becomes stricter
- integrate the package into a less toy-like command surface than `jsverbs-example`
- keep the help pages and ticket docs aligned so the package contract does not drift from the implementation

## Project working rule

> [!important]
> Prefer strict static metadata, shared binding contracts, and explicit failure modes over clever inference or permissive parsing.
> This subsystem is much easier to maintain when scanning stays declarative and runtime behavior follows the same plan the schema used.

## KB reviews

- [[KB-BATCH3-goja-ecosystem]] (2026-05-11) — concept extraction + classification

## Related KB entries

- [[Tribal/goja-embedding-in-go]] — the Go+JS runtime pattern

**Tribal candidates** (not yet at 3-project threshold):
- JS-defined Glazed commands (2/3)
