---
title: "JS-Defined Glazed Commands — How We Do It"
aliases:
  - jsverbs pattern
  - javascript glazed commands
  - scanner-first js commands
  - js command catalog
tags: [knowledge-base, tribal, glazed, javascript, jsverbs, goja]
status: active
type: knowledge-base
created: 2026-05-11
---

# JS-Defined Glazed Commands — How We Do It

> [!summary]
> JavaScript files can be first-class command definitions when the host scans metadata before execution and compiles it into Glazed/Cobra surfaces. The host owns discovery, schema extraction, parsing, and runtime composition; JavaScript owns behavior. This pattern appears in generic jsverbs, Discord-bot operational verbs, and go-minitrace's JS command catalog.

## The pattern

A JS command system has two phases:

1. **Scan phase** — discover JS files, extract command metadata, sections, and bindings without executing arbitrary behavior.
2. **Run phase** — compose a runtime, parse flags/args from the compiled schema, and invoke the selected JS function.

In practice, JS files declare metadata explicitly, for example with `__verb__` and `__section__` style declarations. The host scans these declarations and produces the same command model that a native Glazed command would use.

## Why we do it this way

**Discoverability comes from metadata, not runtime inference.** A JS function becomes a CLI command because it declares itself as one, not because the host guesses.

**Glazed stays the host-level source of truth for command UX.** Help text, typed fields, aliases, and parser behavior all come from the compiled command description.

**JavaScript remains a behavior language.** The JS file implements what the command does. The host still owns discovery, parsing, execution context, and output formatting.

This gives the flexibility of JS with the operational clarity of a typed CLI framework.

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `go-go-goja` | `pkg/jsverbs/` | canonical scan/compile/invoke implementation |
| `2026-04-20--js-discord-bot` | planned jsverbs integration | operational bot-adjacent verbs |
| `corporate-headquarters/go-minitrace` | JS commands in command catalog | JS and SQL coexist in one command system |

### Related PARC project reports

- [[PROJ - go-go-goja jsverbs - JavaScript to Glazed Commands]] — canonical implementation
- [[PROJ - JS Discord Bot - Adding jsverbs Support]] — second host integrating JS-authored verbs
- [[PROJ - go-minitrace PR #6 - JS Commands, Structured Query Catalog, and Framework Metadata]] — third implementation with mixed SQL/JS catalog

## Common mistakes

1. **Trying to infer commands from arbitrary JS functions.** Explicit metadata is much safer than guessing which functions are public verbs.

2. **Executing files during discovery.** Discovery should scan metadata, not run behavior.

3. **Letting runtime bot DSL and CLI verb DSL collapse into one thing.** Discord bot runtime behavior and short-lived operator verbs are related but distinct surfaces.

4. **Compiling directly to ad hoc Cobra code.** The value comes from compiling into a shared command model, not from hand-wiring each JS file as a special case.

5. **Skipping duplicate-path or duplicate-name detection.** Multi-repository command catalogs need explicit collision rules.

6. **Blurring SQL commands and JS commands conceptually.** They can coexist in one catalog, but each still has its own runtime semantics.

## Variations

- **Generic jsverbs** — JS files become Glazed verbs through a reusable scan/registry/runtime pipeline.
- **Operational CLI over a host runtime** — Discord bot uses JS verbs for testing, admin, and maintenance workflows separate from the live gateway runtime.
- **Mixed SQL/JS catalogs** — go-minitrace lets SQL and JS share one catalog and one CLI surface while dispatching to different runtimes.
