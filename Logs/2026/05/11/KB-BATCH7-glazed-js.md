---
title: "KB Playbook Batch 7: Glazed/JS Command Surfaces (6 Projects)"
doc-type: reference
topics: parc, knowledge-base, glazed, javascript, jsverbs, help-browser
owners: manuel
created: "2026-05-11"
---

# KB Playbook Batch 7: Glazed/JS Command Surfaces

Strategic batch targeting Glazed/JS command-definition and help-surface patterns.

## Projects analyzed

1. JS Discord Bot — Building a Discord Bot with a JavaScript API
2. JS Discord Bot — Adding jsverbs Support
3. go-minitrace PR #6 — JS Commands, Structured Query Catalog, and Framework Metadata
4. go-minitrace Local Query Repository Config
5. Glazed Serve — Help Browser, Embedded Docs, and SPA
6. Glazed Static Help Export — render-site and Static Snapshot Publishing

---

## Candidates pushed to 3/3

### JS-defined Glazed commands (3/3 → READY)

| Project | Contribution |
|---------|-------------|
| go-go-goja jsverbs | canonical scanner/registry/runtime pattern |
| JS Discord Bot — Adding jsverbs Support | second host integrating JS-authored verbs as operational CLI |
| go-minitrace PR #6 | third implementation: JS commands alongside SQL in one catalog |

**Core insight**: JavaScript files can be first-class command definitions when command metadata is scanned before execution and compiled into Glazed/Cobra surfaces. The host owns discovery, schema extraction, parsing, and runtime composition; JS owns behavior.

---

## Other candidate updates

### App config vs command config separation (reinforced)

`go-minitrace Local Query Repository Config` cleanly separates:
- app/runtime config discovery (`.go-minitrace.yml`, env, flags)
- command catalog contents (SQL/JS command repositories)

This is the same core pattern as Sqleton and Glazed Vault bootstrap parsing.

### New candidates

| Concept | Seen in | Status |
|---------|---------|--------|
| Dual-mode frontend over live API or static snapshot | Glazed Serve, Glazed Static Help Export | 2/3 |
| Shared canonical model across delivery modes | Glazed Serve, Glazed Static Help Export | 2/3 |
| Scanner-first JS command extraction | jsverbs, go-minitrace PR #6 | 2/3 |
| Repository-local command catalogs | go-minitrace query repositories, Pinocchio-style local overlays | 2/3 |

---

## Key patterns extracted

### JS Discord Bot — Building a Discord Bot with a JavaScript API
- Go owns Discord session lifecycle, token management, and host runtime
- JS should own behavior only after the host contract is stable
- Runtime JS API and CLI jsverbs are separate JavaScript surfaces

### JS Discord Bot — Adding jsverbs Support
- CLI-exposed JS commands should be explicit opt-in, not inferred from runtime bot registration
- `list|run|help` is the clearest stable-action surface for JS verbs
- Operational scripts and long-lived bot behavior should remain separate

### go-minitrace PR #6
- Two command-definition languages, one catalog: SQL and JS coexist cleanly
- Scanner-first extraction of `__verb__` and `__section__` produces the same command model as SQL preambles
- Runtime dispatch chooses SQL render vs JS execute by runtime kind
- Framework metadata preservation matters because the analysis layer depends on adapter-specific details

### go-minitrace Local Query Repository Config
- Project-local command repositories should be discoverable via checked-in config, not only long flags
- Relative repository paths must resolve relative to the config file, not cwd
- Command catalogs are part of project context, not just global user config

### Glazed Serve
- One canonical section model, one canonical parser, one canonical store/query system
- Embedded SPA inside the Go binary is a viable delivery mode for docs/help
- Explicit paths should replace preloaded docs, not silently add to them

### Glazed Static Help Export
- Static export is a second delivery mode for the same help system, not a second help system
- The frontend can browse live `/api/*` or static `site-data/*.json` with the same app
- Route-backed section selection matters for static publishing just as much as for live serving

---

## Playbook feedback (Batch 7)

1. **The JS-command pattern is now clearly real.** We have three independent uses of JavaScript as a command-definition language: generic jsverbs, Discord-bot operational verbs, and go-minitrace analysis commands.
2. **Glazed help stack suggests a new on-ramp cluster.** The serve/export work opens a Go+embedded-SPA documentation-hosting domain that may deserve future on-ramp entries.
3. **Local command catalogs are a recurring pattern.** Query repositories and repo-local config make commands part of project context, not just user-global tooling.
