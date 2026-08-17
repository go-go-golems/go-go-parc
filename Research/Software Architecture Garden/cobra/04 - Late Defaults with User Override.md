---
title: Late Defaults with User Override
aliases:
  - Cobra synthesized defaults
  - Late-bound framework convenience
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
  - defaults
  - extensibility
  - compatibility
related_files:
  - command.go
  - completions.go
related_notes:
  - "[[Research/Software Architecture Garden/cobra/README|Cobra architecture study]]"
  - "[[Research/Software Architecture Garden/cobra/01 - Command Graph as Semantic Authority]]"
  - "[[Research/Software Architecture Garden/cobra/06 - Hidden Protocol Commands for Interactive Tooling]]"
---

# Late Defaults with User Override

## Why this note exists

Framework convenience becomes architecture debt when built-in behavior quietly outranks application intent. Cobra supplies help flags, version flags, a help command, a completion command, and an internal completion command, but it generally delays synthesis until the feature is needed and checks whether the application already supplied an equivalent definition.

> [!summary]
> **Pattern:** synthesize framework defaults at the latest practical point, and make presence of an application-owned definition suppress or replace the default.
>
> **Law:** framework convenience must not overwrite an explicit application definition of the same semantic slot.

## Concrete shape

`InitDefaultHelpFlag` merges applicable flags and adds `--help` only when no help flag already exists. `InitDefaultVersionFlag` does nothing when the command has no version and adds a version flag only when one is absent; it also avoids taking `-v` when that shorthand is already used.

`InitDefaultHelpCmd` creates the `help [command]` subcommand only for commands with subcommands and only when the application has not installed its own help command. It re-adds the help command so its parent and ordering state remain consistent.

Completion follows an even stricter form. `initCompleteCmd` temporarily adds the hidden `__complete` command, resolves the invocation, and removes the synthetic command unless the invocation is actually asking for completion. The source explicitly notes that retaining it would change whether a root-only application appears to have a subcommand.

## Why it works

Defaults are most useful at the edge where the framework knows enough context to determine that they are needed. Delaying synthesis has two benefits:

1. **override safety** — applications get the first opportunity to define behavior;
2. **semantic minimalism** — unused framework features do not unnecessarily perturb the command graph.

This is a general extensibility pattern: defaults are fallback implementations, not privileged implementations.

## Behavioral contract

### Guarantees

- An existing `help` flag prevents Cobra from adding its default help flag.
- An existing version flag prevents duplicate synthesis; an occupied `-v` shorthand causes the generated version flag to omit the shorthand.
- An application-defined help command remains the help command.
- The hidden completion command is retained only for the completion request path.

### Non-guarantees

- Late synthesis still mutates the model. Code observing the command graph before and during execution may see different topology.
- “Default” does not imply pure or deterministic initialization. Default generation may depend on current command state and configuration.
- Presence checks are semantic only to the extent the framework can identify the slot. Two different commands with similar meanings are not automatically deduplicated.

## Failure modes and tricky details

### Eager defaults create phantom semantics

If a framework installs helper commands during object construction, those commands can affect routing, documentation, “has subcommands” checks, or plugin discovery even when never used. Cobra's completion code contains a concrete defense against this category.

### Override points need stable names

Late defaults depend on recognizable names such as `help`, `version`, and the internal completion command. Changing those identifiers is a compatibility change because applications may reserve or override them.

### Lazy mutation complicates snapshots

A tool that serializes a command graph before initialization may not see the same shape a user sees at runtime. Model-derived tooling should either invoke the same initialization steps or state which phase of the model it captures.

## Applicability

Reuse this pattern for framework-provided routes, middleware, health endpoints, generated flags, serializers, plugin commands, default handlers, or adapters that applications may replace.

Do not use lazy synthesis when the model must be immutable after construction, cryptographically signed, or reproducible without an initialization phase. In those systems, build the fully resolved model explicitly and treat defaults as a compile/build step.

## Candidate ecosystem guidance

> **Treat framework defaults as fallbacks. Install them only after application customization has had a chance to claim the slot, and avoid letting unused defaults alter the semantic model.**

## Evidence and references

- `command.go`: `InitDefaultHelpFlag`, `InitDefaultVersionFlag`, `InitDefaultHelpCmd`.
- `completions.go`: `initCompleteCmd` temporarily installs and conditionally removes the hidden completion command to avoid side effects.
