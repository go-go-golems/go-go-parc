---
title: Upwork Tracker — Candidate Ecosystem Guidelines
aliases:
  - Tracker ecosystem architecture candidates
tags:
  - architecture-garden
  - ecosystem-guidelines
  - go-go-golems
  - local-first
status: active
type: architecture-guideline-candidates
created: 2026-07-26
analyzed: 2026-07-26
repository: /home/manuel/code/wesen/go-go-golems/upwork
repository_commit: 460b005427496672418096551b09f338d3cdc438
garden_base_commit: 384ba7df1df20538d6c2964de1f71464b7c92458
source_ticket: UPWORK-TRACKER-SELF-CONTAINMENT-2026-07-25
related_files:
  - AGENTS.md
  - internal/ingestion/ingestion.go
  - internal/projection/projection.go
  - internal/importer/schema.go
  - verbs/lib/agent-service.js
  - verbs/lib/store.js
  - xgoja.yaml
  - Makefile
---

# Candidate Ecosystem Guidelines

The Upwork Tracker confirms several candidates from the first Garden studies and adds new local-first, evidence, agent API, and operational-state candidates. These rules remain provisional until another repository with the same constraints confirms them or a new implementation demonstrates reduced failure and maintenance cost.

> [!summary]
> - The Tracker strongly confirms explicit ownership boundaries, serialized actions, generated-host packaging, embedded SPA delivery, and contract-matched validation.
> - It adds evidence-ledger, reviewed-ingestion, human-confirmation, CAS/idempotency, XDG custody, and WAL-safe backup candidates.
> - Its defects sharpen a recurring Garden rule: stated architecture is not authoritative while bypass writers remain callable.

## Confirmed candidates from rag-evaluation-system

### Cross-process behavior is data

The Tracker's Widget actions, row context, REST resources, and CLI envelopes reinforce the rule from `rag-evaluation-system`: effects and intent cross boundaries as data. Browser callbacks remain inside the browser.

**Status:** stronger candidate; observed in producer/renderer and active consumer.

### Generated hosts select capabilities explicitly

`xgoja.yaml` selects providers, aliases, help, sources, assets, and artifacts. The composition root configures the plan. This confirms the generated-provider pattern in a consumer application.

**Status:** ready for comparison with `go-go-course` or another xgoja host before Tribal promotion.

### Published packages expose product boundaries

The Tracker uses a thin React host and an exact published renderer pin. It does not alias a sibling source checkout. This supports the package-boundary rule.

**Status:** strong candidate.

### Match validation to contract type

The Tracker uses Go tests, lifecycle tests, Widget migration checks, xgoja doctor, module listing, frontend build, API/CLI/IR smoke, browser DOM checks, and package pins. The same layered test principle appears across projects.

**Status:** approaching ecosystem guideline; compare with `go-go-datadrop` structural guards and `rag-ttc` semantic replay tests.

## New candidate 1: Separate evidence occurrence from content identity

**Rule:** An unchanged remote record observed in a later run remains a new occurrence. Store content hashes for comparison, not as global occurrence uniqueness.

**Evidence:** Tracker's global fingerprint uniqueness can discard later unchanged observations and lose recency evidence.

**Compare against:** webhook deliveries, scraped pages, imported documents, polling systems, mail sync.

**Promotion test:** another ingestion system preserves repeated occurrences while deduplicating content storage or processing safely.

## New candidate 2: Reviewed ingestion has plan and apply phases

**Rule:** High-volume or externally sourced ingestion first produces a deterministic plan containing the exact accepted/rejected write set. Apply requires the reviewed plan hash.

**Evidence:** canonical Tracker ingestion validates envelopes, emits explicit rejection diagnostics, fingerprints the plan, and applies transactionally.

**Compare against:** reconciliation, database imports, GitOps changes, batch file processing.

**Promotion test:** plan review catches or prevents a real bad import without forcing operators to inspect SQL.

## New candidate 3: Rebuildable remote projection and local decisions have separate owners

**Rule:** Remote observations may be replayed and reprojected; local human decisions survive every rebuild.

**Evidence:** Tracker projection reconstructs remote facts and search while preserving workflow intent. The stale `job_local_state` mirror shows that ownership must be enforced by writers.

**Compare against:** CRM sync, email clients, calendar sync, GitHub issue mirrors, identity projections.

**Promotion test:** a rebuild from source evidence leaves local tags, notes, decisions, and workflow unchanged.

## New candidate 4: Stable agent APIs begin with capabilities and schemas

**Rule:** Agents discover supported filters, sorts, operations, safety constraints, and OpenAPI before mutation. They do not scrape human UI protocols.

**Evidence:** Tracker exposes capabilities, OpenAPI, stable resources, opaque cursors, action affordances, structured errors, and private opt-in.

**Compare against:** devctl plugins, Glazed dynamic commands, local automation servers.

**Promotion test:** an agent can operate safely from discovery responses without repository-specific prompt knowledge.

## New candidate 5: CAS, domain mutation, audit, and idempotency form one transaction

**Rule:** A stable mutation atomically claims the expected version, changes domain state, appends evidence/audit, and records the replay response.

**Evidence:** Tracker's dedicated submission confirmation atomically groups writes, events, revision, rollback, and idempotency, providing the transaction skeleton. Its eligibility checks remain incomplete; general mutations separately demonstrate the failure when idempotency is recorded afterward.

**Compare against:** agent APIs, payment workflows, deployment controllers, local-first synchronization.

**Promotion test:** injected failure at every stage leaves no partial mutation and retries return exactly one result.

## New candidate 6: High-consequence states have dedicated evidence-gated commands

**Rule:** Generic state transition APIs cannot enter states that assert consequential external events. A dedicated command validates immutable evidence and human confirmation.

**Evidence:** Proposal submission should require ready state, current-version verified receipt binding, receipt-associated validated terms, and explicit confirmation. The audited generic bypass and incomplete dedicated validation prove why adapter/UI readiness checks fail.

**Compare against:** deployment approved, payment sent, certificate issued, contract signed, destructive operation completed.

**Promotion test:** every path to the gated state calls the same evidence-validating transaction.

## New candidate 7: A replaceable checkout cannot select live state by CWD

**Rule:** Source repositories contain code and fictional fixtures. Operator state resolves under XDG or an explicit absolute path. Tests never discover live state.

**Evidence:** Tracker's self-containment design and backup follow this rule; current defaults show the migration gap.

**Compare against:** devctl state, local knowledge tools, mail/search applications, personal automation databases.

**Promotion test:** the repository can be cloned, built, tested, moved, and deleted without affecting live data.

## New candidate 8: WAL databases require application-aware snapshots

**Rule:** Backups, test clones, checksums, and reconciliation snapshots use SQLite online backup or logical read transactions rather than copying/hashing the live main file.

**Evidence:** Tracker backup and smoke clone correctly use `.backup`; reconciliation drift hashing does not.

**Compare against:** every local SQLite application using WAL.

**Promotion test:** backup/restore under concurrent writes passes integrity, foreign-key, and application smoke checks.

## New candidate 9: Trusted-local is an enforced deployment mode

**Rule:** Public-local routes are acceptable only with loopback binding, restrictive filesystem permissions, redaction defaults, and explicit prohibition of untrusted network exposure.

**Evidence:** Tracker routes are public in the host and carry private operations; safety depends on local reachability.

**Compare against:** local model servers, browser automation tools, dev dashboards, agent control planes.

**Promotion test:** configuration rejects or warns on non-loopback binding unless authentication/authorization is configured.

## New candidate 10: Synthetic fixtures are privacy architecture

**Rule:** Private-domain applications ship realistic, wholly fictional fixtures that exercise relational and safety invariants without copying operational data.

**Evidence:** Tracker's smoke suite covers proposals, receipts, lifecycle, REST, CLI, and browser behavior with synthetic records.

**Compare against:** CRM, identity, finance, mail, and customer-support tools.

**Promotion test:** CI can reproduce critical production relationships without any private artifact.

## New candidate 11: Human batch actions preserve domain concurrency

**Rule:** A human bulk toolbar does not bypass revisions, transition policy, transactionality, or audit because it is convenient or interactive.

**Evidence:** Tracker's UI properly bounds and confirms selection but its mutation path lacks CAS and one transaction.

**Compare against:** admin tables, CRM boards, job queues, content moderation.

**Promotion test:** concurrent modification causes explicit all-or-nothing conflict rather than silent overwrite or partial success.

## Comparison table

| Candidate | rag-evaluation-system | Upwork Tracker | Next comparison |
|---|---|---|---|
| Serialized intent and host-owned effects | ActionSpec architecture | Widget actions and service resources | go-go-course |
| Generated provider packaging | Provider producer | Active generated-host consumer | go-go-goja |
| Explicit package boundaries | npm package design | Exact external package pin | go-go-os frontend |
| Contract-matched validation | Stories/goldens/consumer smoke | Go/CLI/REST/IR/browser smoke | go-go-datadrop |
| Evidence occurrence vs content | Not central | Capture fingerprint defect | scraper or webhook project |
| Rebuildable projection vs local state | Protocol/render projection | Remote facts vs operator decisions | identity or CRM sync |
| Atomic CAS/audit/idempotency | Action transport only | Domain mutation requirement | devctl reconciliation |
| Replaceable checkout/XDG | Not central | Primary self-containment design | another local-first DB app |
| WAL-safe snapshot | Not central | Backup and test clone | any SQLite WAL service |

## Promotion priorities

The following candidates have evidence across enough projects to consider a dedicated cross-project synthesis next:

1. Generated hosts select capabilities explicitly.
2. Match validation method to contract type.
3. Published packages expose product boundaries.
4. Cross-process behavior is serialized intent plus runtime-owned effects.
5. Tests and operational tooling must use application-aware SQLite snapshots.

The following need a second comparable system:

1. Evidence occurrence versus content identity.
2. Reviewed ingestion plan/apply.
3. Evidence-gated human confirmation.
4. Stable local-agent capability discovery.
5. Replaceable checkout with XDG state custody.

## Guideline implementation path

```text
Garden comparison
    → dedicated cross-project synthesis note
    → Tribal guideline
    → repository template / skill / CI check
    → adoption in a new project
    → measure prevented failures and maintenance cost
```

A rule should not become template code merely because two documents use similar words. The same constraint and invariant must recur.

## Related notes

- [[Research/Software Architecture Garden/README]]
- [[Research/Software Architecture Garden/rag-evaluation-system/09 - Candidate Ecosystem Guidelines]]
- [[Research/Software Architecture Garden/go-go-datadrop/09 - Candidate Ecosystem Guidelines]]
- [[Research/Software Architecture Garden/upwork-tracker/10 - Architecture Debt and Patterns Not to Repeat]]
