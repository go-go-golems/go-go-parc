---
title: Upwork Tracker — Proposal Lifecycle and Human Submission Boundary
aliases:
  - human-confirmed submission architecture
tags:
  - architecture-garden
  - proposal-lifecycle
  - human-in-the-loop
  - safety
  - evidence
status: active
type: architecture-pattern-study
pattern_maturity: candidate-ecosystem-pattern
created: 2026-07-26
analyzed: 2026-07-26
repository: /home/manuel/code/wesen/go-go-golems/upwork
repository_commit: 460b005427496672418096551b09f338d3cdc438
garden_base_commit: 384ba7df1df20538d6c2964de1f71464b7c92458
source_ticket: UPWORK-TRACKER-SELF-CONTAINMENT-2026-07-25
related_files:
  - verbs/lib/application-lifecycle.js
  - verbs/lib/store.js
  - verbs/lib/agent-service.js
  - verbs/upwork.js
  - internal/importer/draft_receipt_import.go
  - testdata/fixture/draft-receipts/hourly-v1.json
  - testdata/fixture/draft-receipts/fixed-milestones-v1.json
  - docs/help/upwork-agent-safe-workflow.md
---

# Proposal Lifecycle and Human Submission Boundary

Proposal preparation contains several facts that are often collapsed into one status: a draft exists, a remote form was observed, a form was filled and verified, and a proposal was actually submitted. Upwork Tracker models these as separate evidence and lifecycle records. Its dedicated submission-confirmation transaction is a strong human-in-the-loop pattern. The audited commit also contains a generic service path that can bypass this transaction, showing why the invariant must be centralized.

> [!summary]
> - Drafting, form verification, and remote submission are different durable claims.
> - A submitted record requires explicit human confirmation bound to verified evidence.
> - The dedicated transaction atomically records submission, lifecycle, events, audit, CAS, and idempotency, but its eligibility checks are incomplete at the audited commit.
> - Both the generic submitted transition and the incomplete dedicated confirmation validation are critical safety defects.

## Lifecycle state machine

The application lifecycle is:

```text
not_started → planning → drafting → review → ready → submitted → withdrawn
```

`skipped` and `expired` are pre-submission terminal states that can return to planning under explicit transitions.

A transition graph prevents arbitrary status assignment. The UI presents only legal next states. A planner can compute a shortest legal path such as:

```text
drafting → review → ready
```

State machines are valuable because they make invalid jumps explicit. They are insufficient when one legal transition has additional evidence requirements.

## Evidence model

### Form observation

Records the remote application form, Connects requirement, rate prefill, questions, and provenance. It does not claim a form was filled.

### Proposal version

Stores immutable authored draft text and change commentary. Editing creates a new version rather than rewriting history.

### Draft receipt

Records a fill-only browser verification. It includes contract details, Connects, milestones, content hashes, and `submitted: false`. It must not be interpreted as marketplace submission.

### Application terms

Records the economic terms intended for the proposal: hourly/fixed payment mode, currency, rates, totals, milestones, and Connects.

### Submission

Records the local claim that a human confirmed the remote action occurred. This claim is stronger than every preceding artifact.

### Application event

Provides append-only lifecycle evidence such as confirmed submission, withdrawal, or reopening.

## Dedicated confirmation transaction

The dedicated path has a strong **atomic write boundary**. It checks idempotency, claims the expected job revision, inserts the submission, appends transition and confirmation events, updates application/job status, appends activity, records the replay response, and commits them together. The smoke suite injects failure after several stages and asserts complete rollback.

Its **eligibility validation is incomplete** at the audited commit. `confirmSubmitted` verifies that the selected receipt belongs to the job, has status `verified_for_human_review`, and is bound to some proposal version. It does not:

- require the application to already be `ready`; it computes and records a path from the current state to `ready`;
- require the receipt's proposal version to equal the current proposal version;
- require normalized terms to exist;
- require the loaded terms to originate from the selected receipt;
- validate Connects or contract totals before inserting the submission.

The workspace readiness code computes several of these blockers for display, but the transaction does not invoke that readiness policy. The correct target is:

```pseudo
function confirmSubmitted(jobId, receiptId, expectedVersion, idempotencyKey, note):
    begin immediate transaction

    return prior matching idempotent response when present
    claim exact job revision
    require application.status == ready
    load current proposal version
    load selected receipt and require:
        receipt belongs to job
        receipt is verified_for_human_review
        receipt.proposalVersion == currentProposalVersion
    load terms and require terms.sourceReceiptId == receiptId
    validate Connects and fixed/hourly totals
    require no prior confirmed submission unless replaying the same request

    insert submission and append confirmation event
    update application and job projections
    append activity/audit
    record idempotent response
    commit
```

The transaction structure is reusable; the audited validation policy is not yet sufficient.

## Human confirmation is not remote automation

The command records a local fact after a human confirms remote submission. It does not click the marketplace button, spend Connects, or prove remote state cryptographically.

The distinction should remain explicit in names and docs:

```text
confirm-submitted
    records human-confirmed local evidence

submit
    would imply performing remote marketplace action
```

The system should not expose a remote submission verb unless a separately approved automation design exists.

## Content-addressed receipt binding

Receipt import uses content hashes to associate a filled form with an authored proposal version. If more than one proposal version matches, import rejects ambiguous binding rather than guessing.

This is a general evidence principle: automation should fail on ambiguous provenance instead of choosing a convenient record.

## Critical finding UT-P0-001: generic submitted transition bypass

The lifecycle graph permits `ready → submitted`. The shared agent service calls a generic `setApplicationStatus`, which can write `submitted_at`, Connects, and job status without requiring:

- a verified receipt;
- binding to the current proposal version;
- an `application_submissions` row;
- the dedicated confirmation note;
- the single atomic confirmation transaction.

The Widget action route explicitly rejects `submitted`, but REST and CLI share the service path. This contradicts the advertised human-confirmation boundary.

This is one of two critical findings; [[Research/Software Architecture Garden/upwork-tracker/10 - Architecture Debt and Patterns Not to Repeat#UT-P0-001 — generic submitted transition bypass|the debt register]] is canonical. The fix is not another adapter guard. The domain transition operation must reject `submitted` universally:

```pseudo
function transitionApplication(target):
    if target == submitted:
        fail submission_requires_confirmation
    apply ordinary legal transition
```

Only a corrected `confirmSubmitted` implementation can create the submitted state.

## Critical finding UT-P0-002: incomplete dedicated confirmation validation

Even after the generic path is blocked, the dedicated command must enforce readiness, current-version receipt binding, receipt-associated terms, and repeat-confirmation policy inside its transaction. UI workspace blockers are not enforcement. This finding is also recorded in the canonical debt register.

## Why append-only events matter

A current status cannot explain how the application arrived there. Events answer:

- Was submission human-confirmed?
- Which verified receipt supported it?
- Which proposal version was current?
- Which terms and Connects were recorded?
- Was the application later withdrawn?
- Was a skipped application reopened?

For high-consequence states, the event and evidence row should be authoritative. The current status is a projection for queries and UI.

## Privacy boundary

Proposal bodies, comments, facts, and receipts are private. Stable resources omit proposal body by default and require explicit `includePrivate`. Audit descriptions must avoid copying proposal text or secrets.

The same separation should apply to observability. Logs can record job ID, action kind, receipt ID, and outcome without recording the proposal body.

## When to use this pattern

Use evidence-backed human confirmation when a local system tracks an external action it is not authorized to perform or cannot verify automatically. Examples include:

- marketplace submission;
- payment or transfer confirmation;
- production deployment approval;
- legal signing;
- destructive remote administration.

The pattern is especially valuable when automation can prepare everything except the consequential final action.

## Candidate ecosystem rules

- Model preparation artifacts separately from completion claims.
- A high-consequence terminal state has one dedicated command.
- Bind confirmation to the current immutable proposal version and the selected verified receipt.
- Require terms associated with that receipt and validate totals inside the transaction.
- Make confirmation, event, audit, revision, and idempotency atomic.
- Generic state transitions cannot enter evidence-gated states.
- Adapter guards improve UX but never define the only safety boundary.
- Name local human-confirmation records so they do not imply remote automation.
- Redact content while preserving non-sensitive provenance and action metadata.

## Related notes

- [[Projects/2026/07/22/ARTICLE - Upwork Freelance Bid Operations - Tracker, Surf, Facts, and Human Submission]]
- [[Research/Software Architecture Garden/upwork-tracker/03 - SQLite Evidence and Workflow Ledger]]
- [[Research/Software Architecture Garden/upwork-tracker/04 - Shared Service Across CLI REST and Widget Adapters]]
- [[Research/Software Architecture Garden/upwork-tracker/10 - Architecture Debt and Patterns Not to Repeat]]
