---
title: ZK Tool
aliases:
  - ZK Tool
  - Project ZK Tool
tags:
  - project
  - zk
  - obsidian
  - go
  - javascript
status: active
type: project
created: 2026-03-15
repo: /home/manuel/code/wesen/2026-03-14--zk-tool
---

# ZK Tool

This project is a local toolchain for working with an Obsidian-based Zettelkasten vault. Its original purpose was quick capture and filing of ZK notes, but it now also includes a Go-based JavaScript runner that can talk to the local Obsidian CLI through a native `require("obsidian")` API.

> [!summary]
> The project currently has two important identities:
> 1. a ZK filing and note-routing project for an Obsidian vault
> 2. a local experimentation platform for Obsidian automation in Go + JavaScript

## Why this project exists

The vault is large enough that quick capture, filing, and structured retrieval are worth automating. The goal is not only to dump text into Obsidian, but to place new notes into the right conceptual neighborhood with the right structure, naming, and links.

The project also exists because the vault already has a real internal logic:

- Luhmann-style codes for ZK claims
- structure notes that act as hubs
- multiple parallel knowledge areas such as `ZK`, `Wiki`, `Notes`, `Writing`, and `Inbox`
- established naming conventions that are easy for a human to follow but tedious to enforce manually

## Current project status

The repository is in an active prototyping phase.

What already exists:

- a local Go CLI: `zk`
- a Glazed command for running JavaScript against Obsidian:
  - `zk obsidian run-script <script.js>`
- a local native JS module:
  - `require("obsidian")`
- a set of read-only smoke scripts in `scripts/js-tests/`
- embedded CLI help pages for onboarding, architecture, API reference, and testing

What is still incomplete:

- a polished end-user `zk "<thought>"` filing workflow
- write-safe higher-level workflows for claim creation and routing
- branch/code suggestion and confirmation UX integrated into the new Go/JS path

## Project shape

At a high level, the project has three layers:

1. **ZK workflow design**
   - capture a thought
   - classify it
   - place it into the vault correctly
2. **Obsidian automation runtime**
   - run JavaScript locally
   - call a Go native module
   - delegate to the local Obsidian wrapper
3. **Documentation and exploration**
   - smoke-test scripts
   - Glazed help pages
   - design notes and implementation notes in the repo

## Architecture

```text
user
  -> zk CLI
  -> Glazed command
  -> JS runtime bridge
  -> require("obsidian")
  -> Go Obsidian client
  -> ~/.local/bin/obsidian
  -> running Obsidian app
  -> active vault
```

Key code locations:

- `cmd/zk/main.go`
- `cmd/zk/cmds/obsidian/run_script.go`
- `pkg/obsidianjs/runner.go`
- `modules/obsidian/module.go`
- `pkg/obsidian/client.go`
- `pkg/obsidiancli/runner.go`
- `pkg/obsidianmd/`
- `pkg/doc/`

## Vault analysis

The vault already contains a mature ZK system. That means the tool should adapt to the vault rather than trying to impose a new model.

### ZK claims

The core ZK area contains a large set of atomic claim notes and structure notes.

- Claims are filed under `ZK/Claims/`
- Structure notes act as topic hubs
- many claim filenames follow:
  - `ZK - {Luhmann code} - {claim}.md`
  - `ZK - {date} - {claim}.md`
  - `ZK - {claim}.md`

### Parallel knowledge areas

Important sibling areas include:

- `Wiki/`
- `Notes/`
- `Writing/Ideas/`
- `Inbox/`
- `TIL/`
- `Snippets/`

This matters because not every captured thought should become a ZK claim. Some inputs are blog ideas, wiki pages, inbox items, or reference notes.

### Luhmann code system

The claim hierarchy uses alternating number-letter branching.

```text
2       = category
2a      = first branch
2a0     = first sub-branch
2a0a    = deeper branch
2a0a1   = deeper leaf
```

The filing workflow eventually needs to respect this structure instead of generating arbitrary identifiers.

## Current user-facing commands

The current most stable command is the JavaScript runner:

```bash
go run ./cmd/zk obsidian run-script scripts/js-tests/obsidian-version.js
go run ./cmd/zk obsidian run-script scripts/js-tests/obsidian-query-sample.js --output json
go run ./cmd/zk help
go run ./cmd/zk help zk-obsidian-js-api-reference
```

This is the safest current entry point for exploration because it is scriptable, inspectable, and mostly read-only in practice.

## Current read-only smoke coverage

The project already has working read-only scripts for:

- version lookup
- file listing
- note reads
- hydrated note inspection
- query builder runs
- raw `exec()` calls
- batch mapping
- markdown helper parsing

These live in:

- `scripts/js-tests/`

## Intended workflow direction

The long-term workflow still looks like this:

1. capture a thought
2. classify the note type
3. choose or suggest the right ZK branch or alternate location
4. generate a note scaffold
5. let the user confirm or edit
6. write the note
7. optionally update nearby structure notes or links

That original intent is still good. What changed is that the repository now has a better local automation substrate for building it.

## Important project docs

These are currently repo-local rather than vault-local:

- `/home/manuel/code/wesen/2026-03-14--zk-tool/DESIGN-obsidian-js-api.md`
- `/home/manuel/code/wesen/2026-03-14--zk-tool/pkg/doc/01-zk-obsidian-system-overview.md`
- `/home/manuel/code/wesen/2026-03-14--zk-tool/pkg/doc/02-zk-obsidian-intern-guide.md`
- `/home/manuel/code/wesen/2026-03-14--zk-tool/pkg/doc/03-zk-obsidian-js-api-reference.md`
- `/home/manuel/code/wesen/2026-03-14--zk-tool/pkg/doc/04-zk-obsidian-smoke-tests-playbook.md`
- `/home/manuel/code/wesen/2026-03-14--zk-tool/pkg/doc/05-zk-obsidian-implementation-diary.md`

## Open questions

- Should the final user workflow stay script-first, or become a dedicated Go command?
- Should claim creation happen through Obsidian CLI writes, direct filesystem writes, or a hybrid?
- How should branch/code suggestion be implemented and reviewed safely?
- Should structure notes be updated automatically when a new claim is filed?
- How much of the old Python-based workflow should be preserved versus replaced?

## Near-term next steps

- turn the current read-only exploration into one or two concrete claim-filing prototypes
- define a stable JavaScript workflow for note classification and proposed filing
- decide on the write path for new notes
- add a project-level command that wraps a real ZK use case instead of only `run-script`

## Project working rule

> [!important]
> Prefer proving behavior with read-only scripts first.
> Only add write-capable workflows after the read path, query path, and output shape are all stable.
