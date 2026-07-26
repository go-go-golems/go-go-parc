---
title: Architecture Garden — Upwork Tracker
aliases:
  - Upwork Tracker architecture study
  - marketplace tracker architecture
tags:
  - architecture-garden
  - upwork-tracker
  - local-first
  - sqlite
  - xgoja
status: active
type: architecture-garden-project
created: 2026-07-26
analyzed: 2026-07-26
repository: /home/manuel/code/wesen/go-go-golems/upwork
repository_commit: 460b005427496672418096551b09f338d3cdc438
garden_base_commit: 384ba7df1df20538d6c2964de1f71464b7c92458
source_ticket: UPWORK-TRACKER-SELF-CONTAINMENT-2026-07-25
source_reports:
  - /home/manuel/code/wesen/go-go-golems/upwork/ttmp/2026/07/25/UPWORK-TRACKER-SELF-CONTAINMENT-2026-07-25--make-upwork-tracker-self-contained-and-separate-operational-state/design-doc/01-upwork-tracker-self-containment-analysis-design-and-implementation-guide.md
  - /home/manuel/code/wesen/go-go-golems/upwork/ttmp/2026/07/25/UPWORK-TRACKER-SELF-CONTAINMENT-2026-07-25--make-upwork-tracker-self-contained-and-separate-operational-state/design-doc/02-upwork-tracker-xdg-restic-backup-and-restore-design.md
related_files:
  - README.md
  - cmd/tracker/main.go
  - internal/importer/schema.go
  - internal/ingestion/ingestion.go
  - internal/projection/projection.go
  - verbs/lib/store.js
  - verbs/lib/agent-service.js
  - verbs/lib/pages.js
  - xgoja.yaml
  - Makefile
---

# Architecture Garden — Upwork Tracker

Upwork Tracker is a local-first evidence and workflow application for marketplace research, triage, proposal preparation, and human-confirmed submission records. It combines native Go ingestion and operational commands, a SQLite evidence and workflow store, an xgoja JavaScript application, a server-driven React workspace, a stable agent API, and private operator-owned state. The repository contains both unusually strong safety ideas and several transitional implementations that violate those ideas below the adapter layer.

> [!summary]
> - The strongest architecture separates immutable remote evidence, rebuildable projections, and locally owned workflow state.
> - CLI, REST, and Widget interfaces are most reliable when they converge on one domain service and one transactional mutation policy.
> - Submission confirmation, source/state separation, and WAL-safe backup show the intended shape of explicit human and operational safety contracts; the audited implementation gaps are recorded alongside them.
> - The audited commit also contains a critical service-level submission bypass and several dual-authority paths that must not become ecosystem standards.

## Snapshot identity

| Field | Value |
|---|---|
| Repository | `/home/manuel/code/wesen/go-go-golems/upwork` |
| Source commit | `460b005427496672418096551b09f338d3cdc438` |
| Analysis date | 2026-07-26 |
| Garden base commit | `384ba7df1df20538d6c2964de1f71464b7c92458` |
| Source ticket | `UPWORK-TRACKER-SELF-CONTAINMENT-2026-07-25` |

The analysis uses repository code and wholly fictional fixtures only. It does not read the operator's live database, proposal bodies, captures, receipts, audit logs, credentials, or untracked archive contents. Future readers should compare the current repository commit with the source commit before treating any safety or debt finding as current.

## Scope

This study covers:

- capture, ingestion, observations, projection, and reconciliation;
- SQLite identity, ownership, migrations, workflow, and evidence records;
- proposal drafting and submission-confirmation boundaries;
- shared agent service, REST, CLI, and Widget adapters;
- URL-backed and keyboard-first browser interaction;
- generated xgoja host and embedded SPA delivery;
- source-only repository policy, XDG direction, and WAL-safe Restic backup;
- synthetic end-to-end validation and privacy gates;
- observed architecture debt at commit `460b005`.

It does not evaluate proposal quality, live marketplace behavior, or operator data.

## Reading path

1. [[Research/Software Architecture Garden/upwork-tracker/01 - Project Architecture Overview|Project Architecture Overview]] maps the complete system and ownership boundaries.
2. [[Research/Software Architecture Garden/upwork-tracker/02 - Capture Ingestion Projection and Local State|Capture, Ingestion, Projection, and Local State]] studies evidence flow and rebuildability.
3. [[Research/Software Architecture Garden/upwork-tracker/03 - SQLite Evidence and Workflow Ledger|SQLite Evidence and Workflow Ledger]] explains identity, tables, migrations, provenance, and single-writer requirements.
4. [[Research/Software Architecture Garden/upwork-tracker/04 - Shared Service Across CLI REST and Widget Adapters|Shared Service Across CLI, REST, and Widget Adapters]] analyzes adapter convergence, CAS, idempotency, and API separation.
5. [[Research/Software Architecture Garden/upwork-tracker/05 - Proposal Lifecycle and Human Submission Boundary|Proposal Lifecycle and Human Submission Boundary]] explains drafts, receipts, transitions, confirmation, and the audited bypass.
6. [[Research/Software Architecture Garden/upwork-tracker/06 - Keyboard First Workspace and URL State|Keyboard-First Workspace and URL State]] studies human interaction, selection, pagination, and multi-selection.
7. [[Research/Software Architecture Garden/upwork-tracker/07 - Generated XGoja Host and Single Binary Delivery|Generated xgoja Host and Single-Binary Delivery]] maps Go, JavaScript, React, help, assets, and exact provider pins.
8. [[Research/Software Architecture Garden/upwork-tracker/08 - Source State Separation XDG and WAL Safe Backup|Source/State Separation, XDG, and WAL-Safe Backup]] studies operational deployment and recovery.
9. [[Research/Software Architecture Garden/upwork-tracker/09 - Synthetic Full Stack Validation and Privacy Gates|Synthetic Full-Stack Validation and Privacy Gates]] explains the test and repository-hygiene architecture.
10. [[Research/Software Architecture Garden/upwork-tracker/10 - Architecture Debt and Patterns Not to Repeat|Architecture Debt and Patterns Not to Repeat]] records critical and structural failures.
11. [[Research/Software Architecture Garden/upwork-tracker/11 - Candidate Ecosystem Guidelines|Candidate Ecosystem Guidelines]] compares findings with existing Garden candidates.

## System pattern map

```mermaid
flowchart TD
    MARKET[Marketplace through Surf] --> CAPTURE[immutable capture artifacts]
    CAPTURE --> PLAN[validated ingestion plan]
    PLAN --> OBS[immutable observations]
    OBS --> PROJECTION[rebuildable remote projection]
    PROJECTION --> SQLITE[SQLite application store]
    LOCAL[local workflow and operator evidence] --> SQLITE

    SQLITE --> SERVICE[shared JavaScript agent service]
    SERVICE --> REST[/api/v1 REST adapter]
    SERVICE --> CLI[jsverbs CLI adapter]
    SQLITE --> WIDGET[Widget page and action application]
    WIDGET --> REACT[embedded React workspace]

    RECEIPT[verified draft receipt] --> CONFIRM[human-confirmed submission transaction]
    CONFIRM --> SQLITE

    SQLITE --> SNAPSHOT[SQLite online backup]
    SNAPSHOT --> RESTIC[encrypted Restic repository]
```

The design is strongest where arrows represent explicit contracts. Capture does not silently mutate workflow. Projection is rebuildable. Local decisions survive projection. Submission confirmation is transactionally bound to a verified receipt, but the audited eligibility checks do not yet require the current proposal version, ready state, or receipt-associated terms. Backup runs through SQLite rather than copying live WAL files.

## Pattern maturity summary

| Pattern | Maturity | Assessment |
|---|---|---|
| Immutable capture followed by reviewed ingestion | Candidate ecosystem pattern | Strong validation and plan fingerprint; currently bypassed by a second import path. |
| Observation → rebuildable projection → local state | Candidate ecosystem pattern | Excellent ownership model; compatibility mirrors remain inconsistent. |
| Namespaced marketplace identity | Established | Enforced in importer/database paths and prevents cross-marketplace collisions. |
| Shared service behind REST and CLI | Emergent | Strong serializers, cursors, CAS, and error contracts; general transactions are not atomic. |
| Verified receipt plus human submission confirmation | Candidate ecosystem pattern | Atomic write/rollback is strong; generic transition bypass and incomplete eligibility checks are critical defects. |
| Keyboard-first URL-backed workspace | Established for singular state | Search, paging, sort, and active selection are durable; multi-selection is process-global. |
| Generated xgoja host plus embedded SPA | Established | Declarative provider graph and thin React host; runtime JavaScript remains large. |
| Source-only checkout plus XDG state | Candidate ecosystem pattern | Design and backup exist, but CWD-relative defaults remain in product code. |
| WAL-safe logical snapshot before Restic | Candidate ecosystem pattern (operationally attested) | Source ticket records the correct consistency boundary and an external implementation; implementation artifacts are not committed here. |
| Synthetic full-stack smoke | Candidate ecosystem pattern | Broad, private-data-safe coverage; monolithic and under-isolated. |

## The most important architectural tension

The Tracker has a clear desired model and a transitional actual model.

The desired model is:

```text
immutable evidence
    → one canonical ingestion path
    → rebuildable remote projection
    + locally owned workflow state
    → one transactional domain service
    → several adapters
```

The actual commit still includes:

- canonical ingestion and direct legacy import semantics for the same envelope;
- Go schema ownership and JavaScript startup DDL;
- local state in both `jobs` and a stale `job_local_state` shadow;
- an atomic dedicated submission transaction with incomplete eligibility checks, plus an unsafe generic submitted transition;
- stable `/api/v1`, direct Widget mutation paths, and undocumented legacy GET/POST routes whose POST bypasses CAS and idempotency;
- XDG design and backup, but repository-relative database defaults.

The Garden records both because the transition itself teaches an ecosystem rule: architecture ownership must be executable. Documentation cannot establish one authority while runtime code continues writing through two paths.

## Source notes

- [[Projects/2026/07/17/ARTICLE - Upwork Tracker Agent Interfaces - Safe REST and jsverbs Automation]]
- [[Projects/2026/07/22/ARTICLE - Upwork Freelance Bid Operations - Tracker, Surf, Facts, and Human Submission]]
- [[Projects/2026/07/26/PROJECT REPORT - Upwork Tracker Self-Containment - XDG State and WAL-Safe Restic Backups]]
- [[Research/Software Architecture Garden/rag-evaluation-system/README]] — upstream Widget/runtime comparison.
