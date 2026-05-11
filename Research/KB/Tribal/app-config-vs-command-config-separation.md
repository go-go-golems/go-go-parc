---
title: "App Config vs Command Config Separation — How We Do It"
aliases:
  - config separation
  - app vs command config
  - bootstrap config vs runtime config
tags: [knowledge-base, tribal, config, glazed, sqleton, vault]
status: active
type: knowledge-base
created: 2026-05-11
---

# App Config vs Command Config Separation — How We Do It

> [!summary]
> Some configuration answers “how does the application boot and find its dependencies?” and other configuration answers “what should this command do right now?” We keep those separate. App config selects environments, providers, repositories, and bootstrap settings. Command config defines parameters, defaults, and behavior for one executable unit. Three projects converged on this: Sqleton, BYOK Host, and Glazed Vault bootstrap.

## The pattern

We split configuration into two layers:

1. **App config** — long-lived process/bootstrap concerns.
   - where repositories live
   - how to connect to Vault
   - what profile/environment to use
   - global database/runtime settings

2. **Command config** — one command's schema and runtime values.
   - flags and arguments
   - defaults for that command
   - templates, aliases, or action-specific behavior

The rule is simple:

```text
App config decides how the host starts.
Command config decides what one invocation does.
```

If those layers mix, precedence becomes hard to reason about and commands stop being portable.

## Why we do it this way

**Bootstrap concerns happen before commands exist.** In Glazed Vault, the app must know how to talk to Vault before it can hydrate secret-backed command fields. That forced a bootstrap parse of only the Vault settings. If Vault settings lived inside ordinary command config, you'd get a chicken-and-egg problem.

**Commands should be reusable across apps and contexts.** In Sqleton, a SQL command file carries its own metadata and defaults. The app config points to command repositories and database connections, but the command itself owns its parameters. That keeps command files portable.

**Global config and per-command overrides have different precedence rules.** BYOK Host has app-level identity/runtime setup and command/request-level operational inputs. Treating both as one flat settings bag makes it unclear what should win.

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `go-go-golems/sqleton` | command loading + app bootstrap | repository/runtime config vs SQL command metadata |
| `2026-04-17--byok-host` | auth/broker runtime | host/bootstrap config vs request/operation inputs |
| `add-vault-middleware-to-glazed/glazed` | `pkg/cmds/sources/vault.go` | bootstrap parse of Vault settings before command hydration |

### Related PARC project reports

- [[PROJ - Sqleton SQL Command Cleanup - Technical Project Report]] — SQL command files own command metadata; app config owns repository/runtime wiring
- [[PROJ - BYOK Host - Project Report]] — host/broker setup is separate from operation-level inputs
- [[PROJ - Glazed Secret Redaction and Vault Bootstrap - Technical Project Report]] — bootstrap parsing for provider settings before full command parse

## Common mistakes

1. **Putting provider/bootstrap settings in command config.** If a command needs Vault to hydrate secrets, the Vault connection settings must be available before the command parse completes.

2. **Letting app config define command behavior.** If a command's defaults or semantic behavior live in app config, the command stops being portable and reviewable on its own.

3. **Flattening precedence into one bag.** App config, env, flags, bootstrap provider settings, and command defaults often have different timing and priority. One flat merge hides that.

4. **Making repository discovery a per-command concern.** Command repositories are app/bootstrap context. A specific command shouldn't have to re-declare where commands live.

5. **Assuming all config is parseable in one pass.** Glazed Vault shows the counterexample: sometimes you need a tiny bootstrap parse first, then the real parse.

6. **Treating aliases as app config.** Aliases and command wrappers belong with command definitions, not with global runtime configuration.

## Variations

- **Sqleton** — SQL files own command schema; app config owns connection and repository setup.
- **Glazed Vault** — bootstrap parse of provider settings, then full command parse with Vault as a source middleware.
- **Project-local catalogs** — go-minitrace's `.go-minitrace.yml` keeps repository discovery in app/project config while each command file keeps behavior metadata.
