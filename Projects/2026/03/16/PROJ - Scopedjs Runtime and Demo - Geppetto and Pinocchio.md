---
title: Scopedjs Runtime and Demo
aliases:
  - Scopedjs Runtime and Demo
  - Add Scoped JS
  - Scopedjs Geppetto Pinocchio
tags:
  - project
  - scopedjs
  - geppetto
  - pinocchio
  - go
  - javascript
status: active
type: project
created: 2026-03-15
repo: /home/manuel/workspaces/2026-03-15/add-scoped-js
---

# Scopedjs Runtime and Demo

This project is a cross-repository implementation slice that introduces a reusable scoped JavaScript eval tool in Geppetto and then teaches that runtime through concrete examples in Geppetto and a full Bubble Tea demo in Pinocchio.

> [!summary]
> The project currently has three tightly related layers:
> 1. a reusable `geppetto/pkg/inference/tools/scopedjs` package for bounded JavaScript eval tools
> 2. runnable Geppetto examples that show the package in small and composed forms
> 3. a Pinocchio TUI demo that makes the tool behavior visible in a live prompt-to-tool timeline
>
> If you are new to this code: the main idea is "prepare one coherent JavaScript environment, expose it as one tool, and let the model compose several capabilities inside that one runtime."

## Why this project exists

The immediate problem is that some application behaviors are easier to describe as one prepared JavaScript environment than as many small atomic tools. A model may need file access, a scoped database facade, note helpers, and a fake webserver surface all at once. Without a reusable runtime wrapper, each application would have to hand-roll the runtime bootstrap, capability description, tool registration, and eval contract again.

The scopedjs work exists to solve that packaging problem once at the Geppetto layer and then make the result teachable through examples and UI. In practice, the branch is doing for JavaScript runtime composition what the recent `scopeddb` work did for bounded SQLite tools.

## What an intern should understand first

The feature is not "JavaScript support in general." Geppetto and go-go-goja already knew how to run JavaScript before this work.

The feature is a narrower and more useful product shape:

- a host application declares one bounded environment
- that environment may contain modules, globals, bootstrap helpers, and docs
- Geppetto turns the environment into one LLM-facing tool such as `eval_project_ops`
- the model sends `{ code, input }`
- the runtime executes the code and returns one structured result envelope

That means the primary design question is not "can the VM run code?" The primary design question is "how do we package and describe one safe, scoped, understandable runtime so an application can adopt it cleanly?"

## Core concepts

These names show up repeatedly in the code and ticket docs.

### `scopedjs`

`scopedjs` is the Geppetto package at `geppetto/pkg/inference/tools/scopedjs`. It is the reusable abstraction this branch is really about.

It owns:

- the host-side API for defining a runtime environment
- the builder used to collect modules, globals, helpers, and docs
- runtime construction
- eval execution
- result shaping
- tool description generation
- tool registration helpers

It does **not** own application-specific business logic. The app still decides what `db` means, what `obsidian` means, what scope means, and which files or helpers exist.

### Scope

Scope is the app-owned data that determines what the runtime should be bound to. In the demo, scope is basically a chosen fake workspace. In a real application it might be a project ID, session object, or request-specific root directory.

The point of scope is to avoid ambient global behavior. A scoped tool should feel intentionally prepared for one limited context.

### Meta

Meta is optional app-owned information returned when a runtime is built. It is not for the model directly. It is for the host app or demo shell to show useful side information such as workspace name, task counts, or file counts.

### `EnvironmentSpec`

This is the top-level host configuration object. Conceptually it says:

```text
here is the tool identity
here are the default eval options
here is how to populate the runtime for one scope
```

If you are orienting yourself in code, `EnvironmentSpec` is the first type to read.

### `Builder`

The builder is the mutable collection surface used during configuration.

You add:

- native modules
- manual modules
- globals
- bootstrap sources or files
- helper documentation

The builder is not the runtime itself. It is more like a runtime build plan.

### `BuildRuntime(...)`

This turns the builder output into a live goja runtime plus metadata:

- the runtime instance
- the manifest describing what was installed
- cleanup behavior
- optional app-owned meta

This is the step that turns "declared environment" into "live tool-ready environment."

### `RegisterPrebuilt(...)`

This registers a tool against an already-built runtime. The practical consequence is that the tool calls reuse that runtime instance.

This is important because some of the cleanup work exists precisely because the description currently talks about lifecycle semantics more flexibly than the implementation really does.

### `NewLazyRegistrar(...)`

This registers a tool that resolves scope at call time, builds a runtime for that scope, executes the eval, and then cleans up.

This path is useful when the runtime depends on request or session context. It is also where one of the current design rough edges appears: the lazy path does not currently surface capability descriptions as well as the prebuilt path.

### `EvalInput` and `EvalOutput`

The tool contract is intentionally simple:

- input: JavaScript `code` plus optional structured `input`
- output: `result`, optional `console`, timing, and error information

The model is meant to work inside one prepared environment rather than orchestrate many separate tools.

## Current project status

The project is in an active implementation-and-cleanup phase.

The feature is no longer only conceptual. The runtime package exists, the examples exist, the TUI demo exists, and there are follow-up docs and review tickets around them.

What already exists:

- a reusable Geppetto package at `geppetto/pkg/inference/tools/scopedjs`
- Geppetto runnable examples at:
  - `geppetto/cmd/examples/scopedjs-tool`
  - `geppetto/cmd/examples/scopedjs-dbserver`
- a Pinocchio TUI demo at:
  - `pinocchio/cmd/examples/scopedjs-tui-demo`
- adoption documentation in:
  - `geppetto/pkg/doc/playbooks/09-adopt-scopedjs-eval-tools.md`
- a bug ticket for JavaScript `Error` rejection message loss:
  - `geppetto/ttmp/2026/03/16/GP-35--preserve-javascript-error-messages-in-scopedjs-promise-rejections`
- a cleanup review ticket that audits both the package and the demo:
  - `geppetto/ttmp/2026/03/16/GP-36--review-and-cleanup-scopedjs-and-scopedjs-demo-work-since-origin-main`

What is still unsettled:

- `StateMode` currently promises lifecycle semantics more strongly than the implementation delivers
- lazy runtime registration loses most of the model-facing capability description
- eval option override semantics are still a bit weak for boolean fields
- the Pinocchio `scopeddb` and `scopedjs` demos share copied shell and renderer scaffolding that should be extracted
- fake demo modules are duplicated between Geppetto examples and the Pinocchio demo instead of living in one obvious reusable test-double layer

So the current status is not "design only" and not "done." It is "implemented, useful, and ready for a cleanup pass before more users build on it."

## Project shape

At a high level, the branch has four working areas:

### 1. Reusable core runtime

This is the heart of the feature:

- `geppetto/pkg/inference/tools/scopedjs/schema.go`
- `geppetto/pkg/inference/tools/scopedjs/builder.go`
- `geppetto/pkg/inference/tools/scopedjs/runtime.go`
- `geppetto/pkg/inference/tools/scopedjs/eval.go`
- `geppetto/pkg/inference/tools/scopedjs/description.go`
- `geppetto/pkg/inference/tools/scopedjs/tool.go`

What each file is for:

- `schema.go`
  - public API types such as `EnvironmentSpec`, tool description types, and eval option types
- `builder.go`
  - host-side collection of modules, globals, bootstrap helpers, and docs
- `runtime.go`
  - build a live runtime and return a manifest plus cleanup
- `eval.go`
  - run JavaScript, capture console, wait on promises, and export structured output
- `description.go`
  - synthesize model-facing tool descriptions from the manifest and options
- `tool.go`
  - register the environment as a Geppetto tool through prebuilt or lazy helpers

### 2. Geppetto examples and onboarding

These are not production apps. They are adoption proofs.

- `geppetto/cmd/examples/scopedjs-tool`
  - the smallest real example
  - proves the package can expose a simple filesystem-scoped runtime
- `geppetto/cmd/examples/scopedjs-dbserver`
  - the more composed example
  - shows several capabilities living in one environment
- `geppetto/pkg/doc/playbooks/09-adopt-scopedjs-eval-tools.md`
  - the best "how would I adopt this in my own app?" document

### 3. Pinocchio teaching and demo surface

This is where the feature becomes visible and easy to reason about interactively.

- `pinocchio/cmd/examples/scopedjs-tui-demo/main.go`
  - command shell, profiles, backend, Bubble Tea wiring
- `pinocchio/cmd/examples/scopedjs-tui-demo/environment.go`
  - fake runtime contents, environment spec, direct helpers
- `pinocchio/cmd/examples/scopedjs-tui-demo/fake_data.go`
  - deterministic workspaces, tasks, notes, and fixture materialization
- `pinocchio/cmd/examples/scopedjs-tui-demo/renderers.go`
  - timeline rendering for tool calls and tool results
- `pinocchio/cmd/examples/scopedjs-tui-demo/README.md`
  - run instructions and prompt suggestions

### 4. Ticketed design and cleanup docs

These are the written project memory:

- `GP-032`
  - Pinocchio scopeddb demo work
- `GP-033`
  - Pinocchio scopedjs demo work
- `GP-034`
  - Geppetto scopedjs core design and implementation
- `GP-035`
  - scopedjs promise rejection bug around JavaScript `Error` objects
- `GP-036`
  - cleanup-oriented review of both the package and the demo

## Architecture

The simplest mental model is:

```text
host app scope/context
  -> scopedjs.EnvironmentSpec
  -> scopedjs.Builder
  -> BuildRuntime(...)
  -> RegisterPrebuilt(...) or NewLazyRegistrar(...)
  -> one eval_xxx tool
  -> model sends { code, input }
  -> JavaScript runs inside a prepared runtime
  -> result, console output, and errors return as one structured tool result
```

In the Geppetto examples, that runtime may expose things like `fs`, `db`, `require("obsidian")`, and `require("webserver")`. In the Pinocchio demo, the same idea is wrapped in a TUI so the user can watch the tool call, inspect the JavaScript, and see the structured results rendered in the timeline.

## How the runtime works

At a practical level, the runtime build-and-exec path looks like this:

```text
host app scope/context
  -> EnvironmentSpec
  -> Configure(ctx, builder, scope)
  -> builder accumulates modules/globals/bootstrap/docs
  -> BuildRuntime(...)
  -> runtime + manifest + cleanup + meta
  -> RegisterPrebuilt(...) or NewLazyRegistrar(...)
  -> model calls eval_xxx
  -> RunEval(...)
  -> structured EvalOutput
```

The eval path in `eval.go` is where most of the tricky behavior lives:

1. normalize options
2. inject structured input into the runtime
3. optionally replace `console`
4. wrap the model code in an async function
5. execute the code
6. if a promise is returned, wait for it to settle
7. export the result or error into one tool payload

This is why `eval.go` is the right file to read if you are debugging:

- promise rejection behavior
- console capture
- timeout behavior
- output truncation
- JS error formatting

## How the Pinocchio demo works

The Pinocchio demo is valuable because it shows what a real adopter has to write around the reusable package.

The demo flow is:

```text
fake fixture data
  -> workspace scope
  -> scopedjs environment spec
  -> tool registry entry: eval_project_ops
  -> Pinocchio toolloop backend
  -> agent event forwarding
  -> Bubble Tea timeline
  -> custom renderers for tool call and tool result
```

The demo is intentionally fake but concrete. It uses:

- a real temp workspace on disk
- a fake `db` facade for tasks and notes
- a fake `obsidian` module for note creation metadata
- a fake `webserver` module that records routes instead of binding sockets
- the real `fs` native module from `go-go-goja`

This mix is deliberate. It keeps the example testable and deterministic while still proving that a real native module can live inside the environment.

## What the demo is trying to teach

The demo is not mainly about JavaScript syntax. It is teaching three things at once:

1. how Pinocchio hosts Geppetto tool-calling in a Bubble Tea application
2. how `scopedjs` exposes a composed runtime as one tool
3. how structured tool activity can be rendered so a human can understand what the model actually did

That is why the timeline matters so much. The point is not only "the model succeeded." The point is "the user can see the JavaScript, the tool input, the console output, and the structured result."

## Recommended way to read the code

If you are onboarding to the project, this order is efficient:

1. `geppetto/pkg/doc/playbooks/09-adopt-scopedjs-eval-tools.md`
2. `geppetto/cmd/examples/scopedjs-tool/main.go`
3. `geppetto/pkg/inference/tools/scopedjs/schema.go`
4. `geppetto/pkg/inference/tools/scopedjs/tool.go`
5. `geppetto/pkg/inference/tools/scopedjs/eval.go`
6. `pinocchio/cmd/examples/scopedjs-tui-demo/README.md`
7. `pinocchio/cmd/examples/scopedjs-tui-demo/environment.go`
8. `pinocchio/cmd/examples/scopedjs-tui-demo/renderers.go`
9. `geppetto/ttmp/.../GP-36.../design-doc/...`

That path gives:

- a product-level understanding first
- then the smallest example
- then the core package
- then the richer demo
- then the cleanup critique

## Ticket map

### `GP-34`: create reusable scoped JavaScript tool runtime for LLM eval

This is the core design-and-implementation ticket for the reusable package. If you want to understand why the package exists and what it is supposed to own, start here.

Main idea:

- Geppetto should own the shared runtime packaging pattern
- applications should only own their specific modules, globals, scope derivation, and helper docs

### `GP-35`: preserve JavaScript `Error` messages in scopedjs promise rejections

This is a focused bug ticket. The issue is that promise rejections built from real JavaScript `Error` objects can lose their message and surface as `Promise rejected: map[]`.

Main idea:

- string rejections survive
- JS `Error` object rejections do not currently export well enough
- the bug lives in the eval/export path, not in the high-level tool design

### `GP-36`: review and cleanup scopedjs and scopedjs demo work since origin main

This is the main critique ticket and probably the most important read for a new engineer after basic orientation.

The major findings are:

- `StateMode` is not as honest as it should be
- lazy registrations lose capability description detail
- eval option overrides need better boolean semantics
- the Pinocchio demo copied too much shell scaffolding from the scopeddb demo
- the renderer layer also copied too much shared logic
- fake modules are duplicated across examples instead of living in a reusable test-double layer

### `GP-032` and `GP-033`

These are the app/demo-side tickets in Pinocchio.

- `GP-032` is the `scopeddb` TUI precedent
- `GP-033` is the `scopedjs` TUI demo

If `GP-34` explains the reusable package, `GP-033` explains how the package feels in a real user-facing loop.

## Rough edges and why they matter

### Lifecycle semantics

The review found that `StateMode` currently reads more like a promise than a reflection of implemented behavior. This matters because tool descriptions should be honest. If the runtime is reused, the docs should not claim fresh-per-call behavior.

### Description quality in lazy mode

Prebuilt runtimes can surface a strong manifest of modules, globals, and helpers. The lazy path currently loses much of that richness. This matters because the model depends heavily on the tool description to discover what is available.

### Eval option overrides

Boolean override behavior is not expressive enough right now. This matters because runtime behavior like console capture should be easy to override intentionally and test precisely.

### Copied demo shell code

The Pinocchio `scopeddb` and `scopedjs` demos currently share near-copy shell wiring and renderer plumbing. This matters because future changes will drift unless the common shell and renderer layers are extracted.

### Duplicated fake modules

The fake `obsidian` and `webserver` layers appear in more than one place. This matters because there is no single canonical set of test doubles for future examples.

## Ticket ownership hygiene

The current repository split is mostly correct.

Geppetto should own:

- reusable `scopedjs` runtime and API design
- bugs in eval behavior and error propagation
- cleanup work whose primary goal is to improve the Geppetto package contract
- reusable example or test-double layers that are meant to be shared by multiple adopters

Pinocchio should own:

- TUI demo applications
- renderer and UX work that exists to teach a tool in a terminal UI
- example-specific fixtures, prompts, and walkthroughs

Based on the recent tickets, I would **not** move `GP-032` or `GP-033` into Geppetto. Both are fundamentally Pinocchio demo tickets even though they teach Geppetto packages. The stronger hygiene issue is not repo placement but freshness and clarity inside the docs:

- `pinocchio/ttmp/2026/03/16/GP-033--add-scopedjs-tui-demo-example-in-pinocchio/index.md` still says the ticket contains planning only, while its changelog records a finished implementation and manual validation
- `pinocchio/ttmp/2026/03/15/GP-032--add-scopeddb-tui-demo-example-in-pinocchio-based-on-removed-temporal-relationships-tui-patterns/index.md` still points at an older workspace checkout in some `RelatedFiles`
- `geppetto/ttmp/2026/03/16/GP-36--review-and-cleanup-scopedjs-and-scopedjs-demo-work-since-origin-main` is correctly cross-repo in practice because the review is anchored on Geppetto package cleanup, even though several findings apply to Pinocchio code

My working rule for future hygiene is:

> Put the ticket where the primary stable abstraction lives.
> If the work is mainly about teaching or visualizing that abstraction in an app, keep it in the app repo.

## Main commands and demos

These are the most useful commands for getting oriented.

### Geppetto examples

Use the smallest example first:

```bash
go run ./geppetto/cmd/examples/scopedjs-tool
```

Then look at the more composed example:

```bash
go run ./geppetto/cmd/examples/scopedjs-dbserver
```

### Pinocchio demo

List the available fake workspaces:

```bash
go run ./pinocchio/cmd/examples/scopedjs-tui-demo --list-workspaces
```

Run the default demo:

```bash
go run ./pinocchio/cmd/examples/scopedjs-tui-demo
```

Run a specific workspace:

```bash
go run ./pinocchio/cmd/examples/scopedjs-tui-demo --workspace mercury
```

Some prompt ideas once the TUI is running:

- summarize the open tasks and identify the most urgent one
- create a dashboard note from the open tasks and return the note path
- register a `/tasks` route and report the registered route
- create a note and a route in one tool call
- intentionally read a missing file and explain the failure without inventing success

## Important project docs

The most useful starting points are:

- `/home/manuel/workspaces/2026-03-15/add-scoped-js/geppetto/ttmp/2026/03/15/GP-34--create-reusable-scoped-javascript-tool-runtime-for-llm-eval/analysis/01-scoped-javascript-tool-runtime-analysis-and-proposal.md`
- `/home/manuel/workspaces/2026-03-15/add-scoped-js/geppetto/ttmp/2026/03/15/GP-34--create-reusable-scoped-javascript-tool-runtime-for-llm-eval/design-doc/01-scoped-javascript-eval-tools-architecture-design-and-implementation-guide.md`
- `/home/manuel/workspaces/2026-03-15/add-scoped-js/geppetto/ttmp/2026/03/16/GP-36--review-and-cleanup-scopedjs-and-scopedjs-demo-work-since-origin-main/design-doc/01-scopedjs-and-demo-review-cleanup-analysis-design-and-implementation-guide.md`
- `/home/manuel/workspaces/2026-03-15/add-scoped-js/geppetto/pkg/doc/playbooks/09-adopt-scopedjs-eval-tools.md`
- `/home/manuel/workspaces/2026-03-15/add-scoped-js/pinocchio/ttmp/2026/03/16/GP-033--add-scopedjs-tui-demo-example-in-pinocchio/analysis/01-scopedjs-tui-demo-recommendation-and-implementation-plan.md`
- `/home/manuel/workspaces/2026-03-15/add-scoped-js/pinocchio/ttmp/2026/03/16/GP-033--add-scopedjs-tui-demo-example-in-pinocchio/design/01-scopedjs-tui-demo-analysis-design-and-intern-implementation-guide.md`
- `/home/manuel/workspaces/2026-03-15/add-scoped-js/pinocchio/cmd/examples/scopedjs-tui-demo/README.md`

## Open questions

- Should `StateMode` be removed or renamed unless real runtime reuse modes are implemented?
- Should scopedjs separate static capability description from dynamic runtime construction so lazy tools describe themselves as well as prebuilt tools?
- Should Pinocchio extract a shared example shell and renderer harness before building a third comparable demo?
- Should Geppetto provide a `scopedjstest` package for fake `obsidian` and `webserver` modules that examples can share?
- Should the recent Pinocchio ticket indices be refreshed so the ticket summaries match the implemented state of the branch?

## Near-term next steps

- resolve the JavaScript `Error` rejection-message bug tracked in `GP-35`
- execute the cleanup sequence proposed in `GP-36`
- refresh stale ticket index metadata in `GP-032` and `GP-033`
- keep future runtime/API tickets in Geppetto and future UI/demo tickets in Pinocchio unless a ticket is explicitly cross-repo review work

## Project mental model in one sentence

If you only remember one thing, remember this:

> `scopedjs` lets an application package a prepared JavaScript environment as one well-described tool, and Pinocchio exists here to make that tool observable and teachable in a real chat UI.

## Project working rule

> [!important]
> Keep reusable scoped runtime semantics, API contracts, and adoption docs in Geppetto.
> Keep demo shells, renderer UX, and teaching-oriented TUI examples in Pinocchio.

## KB reviews

- [[KB-BATCH11-geppetto-runtime-evolution]] (2026-05-11) — Batch B analysis; contributed to [[Tribal/geppetto-engine-config-vs-runtime-behavior]] and scoped runtime candidates.

## Related KB entries

- [[Tribal/geppetto-engine-config-vs-runtime-behavior]] — Geppetto owns reusable runtime packaging; apps own scope, modules, globals, and helper docs.
- [[Tribal/goja-embedding-in-go]] — prepared goja runtime, native modules, globals, and host-owned capabilities.

**Tribal candidates** (not yet written / covered by broader entries):
- Prepared JavaScript environment as one model-facing tool (3/3, covered for now) — `EnvironmentSpec` + `Builder` + runtime registration.
- Runtime manifest as model-facing capability description (1/3).
- Demo surface as observability for tool calls (1/3).
