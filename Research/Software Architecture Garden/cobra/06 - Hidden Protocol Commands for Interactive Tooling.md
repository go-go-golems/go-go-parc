---
title: Hidden Protocol Commands for Interactive Tooling
aliases:
  - Cobra completion protocol
  - Executable as completion server
status: candidate
type: architecture-garden-design
created: 2026-08-16
analyzed: 2026-08-16
repository: https://github.com/spf13/cobra
repository_remote: https://github.com/spf13/cobra.git
repository_commit: adbc8813901bba65827259daa8e22ff94ec1f30e
tags:
  - architecture-garden
  - cobra
  - completion
  - protocol
  - tooling
related_files:
  - completions.go
  - completions_test.go
  - shell_completions.go
related_notes:
  - "[[Research/Software Architecture Garden/cobra/README|Cobra architecture study]]"
  - "[[Research/Software Architecture Garden/cobra/01 - Command Graph as Semantic Authority]]"
  - "[[Research/Software Architecture Garden/cobra/05 - Constraint Metadata Drives Validation and Completion]]"
---

# Hidden Protocol Commands for Interactive Tooling

## Why this note exists

Shell completion needs the application's real command graph, dynamic argument providers, flag state, and traversal semantics. A separate completion binary or hand-generated static catalog would duplicate that knowledge. Cobra instead lets shell scripts query the executable itself through hidden `__complete` and `__completeNoDesc` commands.

> [!summary]
> **Pattern:** expose interactive tooling through a small machine protocol implemented by the same executable and semantic model that handle normal requests.
>
> **Law:** the tooling query must resolve the target through the same command graph and parsing semantics as ordinary execution, so assistance cannot drift into a second parser.

## Concrete shape

`initCompleteCmd` constructs a hidden command with flag parsing disabled and a minimum-argument contract. The shell passes the partially typed command line to this command. Cobra then:

1. identifies the real command with `Find` or `Traverse`;
2. initializes help/version flags that normal execution would otherwise install;
3. parses enough flag state to determine the completion position;
4. applies required/group constraints;
5. gathers command, flag, static argument, or dynamic function completions;
6. prints one completion per line;
7. prints a final `:<directive>` integer that tells the shell how to treat the candidates;
8. sends human diagnostics to stderr, which the completion script ignores.

`ShellCompDirective` is a bit map for behaviors such as no-space, no-file-completion, file-extension filtering, directory filtering, and order preservation.

The command is added only for completion resolution and removed when the current invocation is not actually a completion request. This prevents the internal protocol endpoint from permanently changing a root-only application's topology.

## Why it works

The executable becomes an **introspection server over its own live model**. Shell-specific scripts remain thin adapters: they ask the application what is legal now, then translate a small response protocol into Bash/Zsh/Fish/PowerShell behavior.

This is especially useful for dynamic completions. `ValidArgsFunction` and registered flag completion functions execute in the application's Go process with the selected command and its context, so completion can reflect runtime knowledge without teaching the shell the application's internal model.

## Behavioral contract

### Guarantees

- Completion routes through the same root command graph and honors `TraverseChildren` when configured.
- Hidden/deprecated commands are not suggested as ordinary subcommands.
- flag completion uses inherited and non-inherited flag views, including commands that disable Cobra's normal flag parsing.
- completion returns an explicit shell directive even when no candidates are produced.
- the current command context is propagated to dynamic completion functions.

### Non-guarantees

- This protocol is not a security boundary. Running completion may execute application-supplied completion functions; those functions must be designed as safe, bounded queries.
- Completion output is a strict protocol. Accidental stdout logging can corrupt it; diagnostics belong on stderr.
- Dynamic completion is advisory. Runtime execution and authorization remain authoritative.
- The protocol has latency implications because a shell may invoke the executable repeatedly while a user types.

## Failure modes and tricky details

### Side effects in completion functions

Because completion runs application code, a function that performs writes, prompts, expensive network calls, or irreversible initialization creates a poor interactive boundary. Treat completion functions as query interpreters and make remote calls cancellable through context.

### Protocol pollution

Anything printed to stdout besides candidates and the final directive can be interpreted as a completion. Cobra deliberately separates diagnostic stderr from machine stdout; reusers should make that channel separation explicit.

### Incomplete input is not normal argv

The last token is intentionally partial and flag values may be syntactically incomplete. Completion cannot simply call the normal executor and wait for an error; it needs a parser mode designed for partial programs.

## Testing and evidence

`completions_test.go` is unusually large because the protocol is a compatibility surface. It tests subcommand visibility, descriptions, traversal, persistent/local flags, valid args, dynamic completion, directives, and grouped flag behavior. This makes the protocol a strong candidate pattern rather than an undocumented trick.

## Applicability

Reuse this pattern for command completion, editor language tooling, local introspection, schema queries, plugin discovery, or “explain this invocation” features when the authoritative executable can cheaply answer the query.

Do not use it when merely invoking the executable has dangerous startup effects, when completion must work without the application binary, or when a network service with explicit authentication/version negotiation is the actual boundary.

## Candidate ecosystem guidance

> **For interactive tooling that must understand a live executable schema, prefer a narrow machine-query protocol over a duplicated parser. Keep stdout protocol-pure, keep queries side-effect-light, and reuse the normal model without invoking the normal effects.**

## Evidence and references

- `completions.go`: hidden completion commands, protocol output, directives, partial parsing and dynamic completion.
- `completions_test.go`: executable compatibility tests across routing, flags, arguments and directives.
- shell completion generators: adapters consume the internal protocol rather than reconstruct the application schema independently.
