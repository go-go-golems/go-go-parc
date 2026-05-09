---
title: Sanitize
aliases:
  - Sanitize
  - Project Sanitize
tags:
  - project
  - sanitize
  - yaml
  - json
  - tree-sitter
  - go
status: active
type: project
created: 2026-03-05
repo: /home/manuel/code/wesen/2026-03-05--yaml-sanitizing
---

# Sanitize

This project is a Go-based structured-text sanitizer centered on tree-sitter parsing, rule-driven linting, and conservative automatic repair. It started as a YAML sanitizing experiment and now looks more like a reusable `sanitize` toolchain for malformed YAML, malformed JSON, and interactive inspection in a bundled browser UI.

> [!summary]
> The project currently has three connected identities:
> 1. a CLI for linting, parsing, and repairing YAML and JSON
> 2. a reusable Go library split into `pkg/yaml` and `pkg/json`
> 3. a local web playground for parse-tree inspection and repair review

## Why this project exists

The repository exists to deal with a recurring failure mode in structured text: data is almost-valid, but not valid enough to pass strict parsers or downstream tools. That shows up in hand-written YAML, generated config, and especially LLM-produced JSON that often arrives wrapped in prose, Markdown fences, comments, Python literals, or trailing commas.

The project does not try to become a fully permissive parser. Its working model is narrower and more useful: parse with tree-sitter, surface structural errors clearly, lint for known malformed patterns, and apply only conservative fixes that are easy to justify.

## Current project status

The repository is active and already usable.

What clearly exists today:

- a shipped CLI binary, `sanitize`, with `fix`, `lint`, `parse`, `rules`, and `serve`
- a reusable Go module, `github.com/go-go-golems/sanitize`
- separate YAML and JSON engines in `pkg/yaml` and `pkg/json`
- a bundled HTTP server and single-page UI in `internal/server/`
- embedded example corpora for YAML and JSON in `examples/`
- test coverage across the CLI, server, YAML package, JSON package, and example loader

Current evidence of working state:

- `go test ./...` passes in `/home/manuel/code/wesen/2026-03-05--yaml-sanitizing` as of 2026-03-15
- the most recent local commits show JSON recovery, server/API integration, and UI support landing on 2026-03-13

What is still evolving:

- YAML architecture cleanup is still in flight, especially around the tree-sitter-aware shared analysis direction documented in `SANITIZE-004`
- the UI was recently split and improved, but it still reads as a practical local playground rather than a polished end-user product
- the conservative-repair boundary is intentional, so there is still active judgment about which malformed cases should be auto-fixed versus only diagnosed

## Project shape

At a high level, the repository has five layers:

1. command entry points in `cmd/sanitize` and `internal/cli`
2. format-specific engines in `pkg/yaml` and `pkg/json`
3. shared example corpora in `examples/yaml` and `examples/json`
4. an embedded local web server in `internal/server`
5. research and delivery history in `ttmp/2026/03/13/SANITIZE-*`

The main mental model is simple:

```text
input text
  -> format-aware parse/analyze pass
  -> lint issues + parse errors
  -> conservative iterative fixes
  -> final sanitized text + diagnostics + fix log
```

JSON adds one more constraint than YAML: the code tracks both tree-sitter structural health and strict `encoding/json` parse health, which matches the project’s emphasis on malformed LLM JSON recovery.

## Architecture

The most important code paths are:

- `cmd/sanitize/main.go`
- `internal/cli/root.go`
- `internal/cli/commands.go`
- `pkg/yaml/sanitize.go`
- `pkg/yaml/lint.go`
- `pkg/yaml/parse.go`
- `pkg/json/sanitize.go`
- `pkg/json/lint.go`
- `pkg/json/parse.go`
- `internal/server/server.go`
- `internal/server/static/index.html`
- `internal/server/static/js/app.js`
- `internal/server/static/css/style.css`

The repo is architecturally clean in one useful way: YAML and JSON are parallel packages with similar concepts, which makes the project easier to reason about as a library and easier to extend format-by-format. The `pkg/json` implementation appears to be the newer, more explicitly analysis-driven side of the codebase, while `pkg/yaml` still carries some older lint/fix structure that is being revisited.

## Current user-facing commands

The CLI surface is already broad enough to describe the project concretely:

```bash
sanitize fix broken.yaml
sanitize lint broken.yaml
sanitize parse broken.yaml
sanitize rules --format json
sanitize fix --format json llm-output.txt
sanitize parse --format json --json broken.json
sanitize serve
```

The most important user-level distinction is:

- `fix` tries to repair conservatively and returns sanitized output plus status
- `lint` diagnoses issues without changing input
- `parse` exposes tree-sitter structure and parse errors directly
- `rules` exposes the rule catalog, which makes the engine inspectable instead of opaque
- `serve` turns the project into a local interactive playground

## Example corpus and playground role

The example corpus is not just demo material. It is part of the project’s working method.

The YAML and JSON corpora are embedded and surfaced through the server so the browser UI can act as a recovery lab for specific malformed cases. The JSON corpus in particular is explicitly organized around malformed LLM-output patterns, including wrappers, comments, Python literals, duplicate commas, and mixed recovery cases.

That makes the project more than a one-shot CLI utility. It is also a small experimental platform for deciding which repairs are safe enough to automate.

## Important project docs

These repo-local docs are the most important orientation points:

- `/home/manuel/code/wesen/2026-03-05--yaml-sanitizing/README.md`
- `/home/manuel/code/wesen/2026-03-05--yaml-sanitizing/ttmp/2026/03/13/SANITIZE-004--improve-yaml-linting-and-sanitizing-with-tree-sitter-aware-analysis/index.md`
- `/home/manuel/code/wesen/2026-03-05--yaml-sanitizing/ttmp/2026/03/13/SANITIZE-005--split-ui-into-css-js-html-and-improve-preset-loading/index.md`
- `/home/manuel/code/wesen/2026-03-05--yaml-sanitizing/ttmp/2026/03/13/SANITIZE-007--add-json-support-with-focus-on-malformed-llm-json-recovery/index.md`

Those ticket docs make the current direction unusually legible. They show the repo moving from a YAML sanitizer into a more general structured-text sanitizing package with a local research workflow, a real UI, and release-readiness ambitions.

## Open questions

- Should the project remain tightly focused on YAML + JSON, or become a broader structured-text sanitizing framework?
- How much of the newer `pkg/json` analysis style should be pulled back into `pkg/yaml`?
- Where should the boundary sit between “safe automatic fix” and “diagnose only” for malformed JSON cases?
- Is the bundled browser UI mainly a developer tool, or should it become a more user-facing product surface?
- What release/readiness work is still needed to make the library and CLI feel stable outside this repo’s immediate workflow?

## Near-term next steps

- finish the tree-sitter-aware YAML architecture cleanup described in `SANITIZE-004`
- keep extending malformed JSON coverage without weakening the conservative repair rule
- continue using the example corpora and UI as an evidence loop for new fixers
- tighten public-release ergonomics around docs, examples, and rule discoverability

## Project working rule

> [!important]
> Prefer conservative, explainable repair over aggressive “magic.”
> If a malformed case is ambiguous, the project should surface it clearly before it tries to guess.
