---
title: css-visual-diff
aliases:
  - css-visual-diff
  - Project css-visual-diff
  - CSS Visual Diff
  - css-visual-diff Script Runtime
  - css-visual-diff JS DSL
tags:
  - project
  - css
  - visual-regression
  - browser-automation
  - chromedp
  - goja
  - javascript
  - glazed
status: active
type: project
created: 2026-04-21
repo: /home/manuel/workspaces/2026-04-21/hair-v2/css-visual-diff
---

# css-visual-diff

This project is a Go-based browser evidence and visual-diff tool for comparing rendered HTML/CSS across two targets. It started life as a rough Python prototype, was then reset onto a clean Go baseline using `sbcap`, and is now moving toward a richer JavaScript-driven runtime where embedded scripts can expose higher-level comparison workflows as real CLI verbs.

> [!summary]
> The project currently has two important identities:
> 1. a concrete HTML/CSS comparison tool built on `chromedp`, computed-style diffing, matched-style inspection, and pixel diffing
> 2. an emerging host platform for sandboxed JavaScript workflows backed by Go primitives and exposed as full Glazed/Cobra commands

## Why this project exists

There is a recurring need to compare pieces of UI with much more precision than a single screenshot diff provides. In practice, the useful questions are often things like:

- why does this widget feel tighter or looser?
- which CSS properties actually changed?
- which selector or inline declaration won in the cascade?
- how different is the visual output in pixel terms?
- what concise evidence should a coding agent receive so it can make the next implementation change?

The project exists to answer those questions in a browser-realistic way. It is intended to work on whole pages, small widgets, or any focused sub-region that matters for a migration or fidelity task.

The newer direction also exists because fixed CLI flags only go so far. Once the tool is stable enough, it should be able to host tiny task-specific JavaScript programs that gather only the evidence needed for a given question and return compact output rather than token-heavy raw dumps.

## Current project status

The repository is in an active transition from “rebuilt baseline” to “programmable runtime.”

What already exists:

- a working Go CLI at:
  - `cmd/css-visual-diff`
- browser capture using `chromedp`
- computed CSS diffing
- matched-style / cascade winner analysis
- pixel diff image generation
- a YAML-driven batch path (`run`)
- a direct compare path (`compare`)
- a chromedp sanity-check path (`chromedp-probe`)
- a first `go-go-goja` / `jsverbs` integration slice with embedded script-backed verbs under:
  - `script compare region`
  - `script compare brief`
- root-level logging flags such as:
  - `--log-level debug`

What is still incomplete:

- a lower-level `page` host module and a fuller public JS DSL surface
- optional visual-LLM integration as a real runtime module
- a larger catalog of embedded default scripts
- a cleaner long-term service split between CLI mode code and JS-hosted runtime services
- user-supplied external script directories beyond the embedded default set

## Project shape

At a high level, the project now has four layers:

1. **Browser evidence engine**
   - open pages
   - set viewport
   - capture screenshots
   - inspect computed styles and matched rules
   - compute pixel diffs
2. **Comparison/report services**
   - generate structured compare results
   - build concise brief/report output
3. **Runtime and script integration**
   - embedded JavaScript scanning via `pkg/jsverbs`
   - caller-owned `go-go-goja` runtime per invocation
   - Go-backed runtime modules like `diff` and `report`
4. **CLI and docs**
   - Cobra/Glazed root command
   - script-backed verbs under normal help/logging/output behavior
   - ticket docs and reMarkable-ready design deliverables

## Architecture

```mermaid
flowchart TD
    A[user] --> B[css-visual-diff CLI]
    B --> C[hand-written commands]
    B --> D[script-backed jsverbs commands]

    C --> E[compare / run / chromedp-probe]
    D --> F[embedded JS scripts]
    F --> G[go-go-goja runtime]
    G --> H[require("diff") / require("report")]

    H --> I[Go comparison services]
    I --> J[chromedp driver]
    J --> K[left target]
    J --> L[right target]

    I --> M[computed style diffs]
    I --> N[matched-style winners]
    I --> O[pixel diff artifacts]
    H --> P[concise agent brief]
```

Key code locations in the current repo:

- `cmd/css-visual-diff/main.go`
- `internal/cssvisualdiff/driver/chrome.go`
- `internal/cssvisualdiff/modes/compare.go`
- `internal/cssvisualdiff/modes/cssdiff.go`
- `internal/cssvisualdiff/modes/matched_styles.go`
- `internal/cssvisualdiff/dsl/embed.go`
- `internal/cssvisualdiff/dsl/host.go`
- `internal/cssvisualdiff/dsl/registrar.go`
- `internal/cssvisualdiff/dsl/scripts/compare.js`
- `internal/cssvisualdiff/services/agent_brief.go`

## Implementation details

The current direction is best understood as “Go services + JS orchestration,” not “rewrite the tool in JavaScript.” The project is using `go-go-goja`'s runtime builder/factory and `pkg/jsverbs`'s JavaScript-to-command pipeline to make small embedded scripts behave like real commands.

### Current runtime path

The current script-backed path works roughly like this:

```text
embedded JS source
  -> jsverbs.ScanFS(...)
  -> Registry + VerbSpecs
  -> CommandsWithInvoker(customInvoker)
  -> root Cobra command
  -> selected script command runs
  -> custom invoker builds caller-owned go-go-goja runtime
  -> runtime registrar exposes require("diff") and require("report")
  -> JS function orchestrates host calls
  -> Go compare/report services return result
  -> Glazed renders rows or writer output
```

### Current embedded script shape

The first embedded script file defines a package under `script compare` and exposes two verbs:

- `region`
  - structured result path
- `brief`
  - text output path

Conceptually it looks like:

```javascript
__package__({ name: "compare", parents: ["script"] })

function region(targets, viewport, output, selectors) {
  return require("diff").compareRegion({...})
}

function brief(targets, viewport, output, selectors, question) {
  const result = region(targets, viewport, output, selectors)
  return require("report").renderAgentBrief({ question, evidence: result })
}
```

The important detail is that the JavaScript stays thin. The browser and diff mechanics remain in Go.

### First host-module slice

The first runtime-scoped modules are:

- `diff`
  - exposes a high-level `compareRegion(...)`
- `report`
  - exposes deterministic brief-building helpers

This is the right first slice because it keeps the scripts concise and immediately useful. A lower-level `page` module may still arrive later, but the current implementation proved that high-level orchestration verbs are enough to validate the architecture.

### Reusable compare result extraction

A small but important refactor happened in the Go layer: the old direct compare path was split so the host runtime can reuse comparison logic without going through the command/report surface.

That now gives the project a service-like flow:

```go
result, err := modes.GenerateCompareResult(ctx, settings)
err = modes.WriteCompareArtifacts(result, writeJSON, writeMarkdown)
```

That is not yet the final long-term service package shape, but it is the first real seam between command-specific orchestration and reusable browser evidence generation.

### Deterministic brief generation

The report path for the script-backed brief command is currently deterministic rather than model-driven. It takes the compare result and produces a concise text summary based on:

- pixel diff percentage
- changed computed properties
- selected winner-diff/cascade changes

That is a good project rule at this stage because it keeps the first script runtime explainable and easy to validate. An LLM-based explanation module can come later once the evidence-gathering side is stable.

## Current user-facing commands

The current core commands are:

```bash
GOWORK=off go run ./cmd/css-visual-diff --help
GOWORK=off go run ./cmd/css-visual-diff compare --help
GOWORK=off go run ./cmd/css-visual-diff chromedp-probe --help
GOWORK=off go run ./cmd/css-visual-diff script compare region --help
GOWORK=off go run ./cmd/css-visual-diff script compare brief --help
```

The script-backed brief path can now be used like this:

```bash
GOWORK=off go run ./cmd/css-visual-diff --log-level debug \
  script compare brief "What should change?" \
  --leftUrl http://127.0.0.1:58013/left.html \
  --rightUrl http://127.0.0.1:58013/right.html \
  --leftSelector '#cta' \
  --rightSelector '#cta' \
  --width 390 \
  --height 844
```

That currently produces a concise text brief such as:

- visual drift percentage
- padding changes
- radius changes
- color/background changes

## Important project docs

The most important current design/research docs are ticket-local rather than repo-local:

- `ttmp/2026/04/21/HAIR-017--analyze-sbcap-and-extract-a-standalone-screen-diff-application/design-doc/01-sbcap-analysis-architecture-and-standalone-screen-diff-extraction-guide.md`
- `ttmp/2026/04/21/HAIR-018--rebuild-css-visual-diff-from-sbcap-and-retire-python-prototype/design-doc/01-short-implementation-plan.md`
- `ttmp/2026/04/21/HAIR-019--design-a-sandboxed-javascript-dsl-for-css-visual-diff-evidence-gathering/design-doc/01-sandboxed-javascript-dsl-for-css-visual-diff.md`
- `ttmp/2026/04/21/HAIR-019--design-a-sandboxed-javascript-dsl-for-css-visual-diff-evidence-gathering/design-doc/02-go-go-goja-runtime-and-jsverbs-integration-plan.md`
- `ttmp/2026/04/21/HAIR-019--design-a-sandboxed-javascript-dsl-for-css-visual-diff-evidence-gathering/reference/01-investigation-diary.md`

Important upstream runtime/docs references in the neighboring repo:

- `/home/manuel/workspaces/2026-04-21/hair-v2/go-go-goja/README.md`
- `/home/manuel/workspaces/2026-04-21/hair-v2/go-go-goja/pkg/doc/01-introduction.md`
- `/home/manuel/workspaces/2026-04-21/hair-v2/go-go-goja/pkg/doc/03-async-patterns.md`
- `/home/manuel/workspaces/2026-04-21/hair-v2/go-go-goja/pkg/doc/10-jsverbs-example-developer-guide.md`
- `/home/manuel/workspaces/2026-04-21/hair-v2/go-go-goja/pkg/doc/11-jsverbs-example-reference.md`

## Current validation shape

The project now has both automated and script-level validation for the new runtime path.

Stable checks include:

```bash
cd /home/manuel/workspaces/2026-04-21/hair-v2/css-visual-diff
GOWORK=off go test ./...
GOWORK=off go build ./cmd/css-visual-diff
```

There are also ticket-local smoke scripts in `HAIR-019`, including:

- a `go-go-goja/jsverbs` smoke script
- a `css-visual-diff` script-verb smoke script

These are especially useful because they validate the actual command-registration and runtime-hosting path instead of only package-level tests.

## Open questions

- Should the first public JS API stay fairly high-level (`diff`, `report`) or should a lower-level `page` module be exposed sooner?
- Should user-supplied external script directories be supported in the first public release, or should the product stay embedded-script-first for a while?
- Should one runtime be created per command invocation long-term, or is a runtime pool worth the extra complexity later?
- How should the eventual visual-LLM module be introduced without turning the early runtime into an async tangle too soon?
- How aggressively should the old hand-written commands be retired once script-backed defaults are stronger?

## Near-term next steps

- add more embedded script verbs beyond the first compare slice
- decide whether to expose a lower-level `page` host module next
- extract more explicit long-term service packages from the current mode code
- design the first real `llm` runtime module only after the evidence path is stable
- add optional user-supplied script directory support after the embedded path is solid
- improve structured output for script-backed compare verbs so they can be piped into coding-agent workflows more directly

## Project working rule

> [!important]
> Keep JavaScript verbs small and orchestration-focused.
> Put browser mechanics, diff computation, and deterministic reporting in Go services and runtime modules.
> Only add lower-level JS power when a concrete workflow proves it is needed.
