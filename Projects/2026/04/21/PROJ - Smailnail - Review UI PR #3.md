---
title: Smailnail PR #3 — Review UI, Feedback & Guidelines (Deep Dive)
aliases:
  - Smailnail PR #3
  - Smailnail Review UI
  - Smailnail task/add-review-ui
tags:
  - project
  - smailnail
  - annotations
  - review-ui
  - feedback
  - guidelines
  - protobuf
  - buf
  - codegen
  - react
  - frontend
  - backend
  - sqlite
  - transactional
status: active
type: project
created: 2026-04-21
repo: /home/manuel/workspaces/2026-04-03/js-repl-smailnail/smailnail
---

# Smailnail PR #3 — Review UI, Feedback & Guidelines

This is a 60-commit PR that adds a complete review workflow to the smailnail annotation system. The work spans protobuf-based contract codegen, a new SQLite-backed review feedback and guideline repository, a full React UI with 14 phased implementation steps, and systematic documentation. This is not a feature branch — it is a parallel track of work that diverged from `main` and is now ready to merge.

> [!summary]
> This PR has four intertwined identities:
> 1. A protobuf-first shared contract layer using Buf + `go generate` that eliminates Go↔TypeScript wire drift
> 2. A transactional review feedback and guideline repository that enforces atomicity across review state, comments, and guideline links
> 3. A 14-phase React UI buildout from shared badges to full guidelines management pages
> 4. A disciplined implementation diary culture with code review, recovery planning, and a durable playbook for keeping the UI consistent

## The Starting Problem

The smailnail project has an annotation system for email triage. Annotations are structured judgments — tags, notes, review states — attached to messages, threads, senders, and domains. The original annotation UI was a basic browse-and-filter tool over SQLite: list pending annotations, expand a row, see the detail.

The problem was that reviewing annotations was a dead end. You could mark something "to_review" or "reviewed" but you couldn't:
- record why you made a judgment (feedback with context)
- attach a reusable policy reference (guidelines)
- link guidelines to agent runs so future annotations get measured against the same standard
- do any of this in bulk without clicking through each row

The codebase also had a structural problem: the TypeScript frontend and the Go backend had drifted on the feedback create payload. The frontend sent `targetIds` as a string array, but the Go handler expected `targets` as an array of `{targetType, targetId}` objects. This kind of mismatch is exactly what code generation prevents.

## Architecture Decision: SQLite Serve, Not smailnaild

The first architectural decision was where to host the new backend. The existing HTTP server was `smailnaild`, but that binary manages hosted credentials and IMAP rules — it knows about user accounts, authentication, and the `smailnaild.sqlite` app database. The annotation UI talks to a *mirror* SQLite database (the one that stores the locally-synced email corpus).

These are different databases, different concerns, and different security boundaries. A reviewer looking at annotations should not need an IMAP password. So the work created a new `smailnail sqlite serve` command that hosts the annotation UI against a mirror database, reusing the existing built frontend assets from `pkg/smailnaild/web` but with its own routing behavior.

This was the right call. The alternative — bolting annotation browsing onto `smailnaild` — would have dragged hosted auth concepts into a browse-only context and created a confusing `/` shell for the annotation pages.

## Phase 1: The Backend Foundation

The implementation diaries capture the first three steps of backend work in detail.

**Step 1** established the ticket workspace and the architecture correction. The existing frontend contract was easy to confirm from `ui/src/api/annotations.ts` and the existing RTK Query types — it expected 16 bare JSON endpoints. The mismatch was that the handoff spec pointed implementation at `smailnaild`. The corrected approach was a dedicated `pkg/annotationui` package and a `smailnail sqlite serve` command.

**Step 2** extended the annotation repository with run summaries, batch review support, and aggregated run detail queries. The key insight was that these capabilities belong in the repository layer (not the HTTP layer) because they are useful whether the caller is HTTP, CLI, or future automation. A sharp edge emerged around SQLite aggregate scanning: the existing entity types use `time.Time`, but aggregate rows are safer as string fields because SQLite returns expression results differently from table-backed columns. Using strings kept the JSON shape aligned with the frontend without fighting the driver's scanning rules.

**Step 3** landed the HTTP server. This was the biggest backend slice: `pkg/annotationui/server.go` plus handlers for annotations, senders, and the query workbench. The query workbench is read-only and intentionally conservative — keyword-based enforcement prevents writes to the mirror database. The SPA serving was tricky: the built frontend still had a legacy `/` redirect to the hosted account shell, so the sqlite server had to treat `/` specially and fall back to `index.html` only for annotation/query routes. A naive `GET /` redirect registration was too broad and intercepted `/annotations` — confirmed by a failing handler test that caught the bug before it reached production.

The initial server smoke revealed three real bugs that the handler tests caught:
- root redirect matching too broadly and intercepting `/annotations`
- a bad batch-review test fixture selection
- an over-constrained sender-list assertion

These were fixed directly rather than weakening coverage.

## Phase 2: Review Feedback and Guidelines

After the annotation UI backend was stable, the work moved to the review feedback and guideline feature. The diary describes this as Phase 2, but it was actually implemented in two separate pushes with a recovery step in between.

### The Transactional Bug

The first Phase 2 attempt had a semantic bug. The design doc required that review-state update + optional feedback creation + optional run-guideline linking should succeed or fail together when triggered by one user action. But the handler layer extended `handleReviewAnnotation` by updating review state first and then doing optional feedback/guideline work with ignored errors:

```go
// Wrong: these can partially fail and return success
_, _ = h.annotations.UpdateAnnotationReviewState(...)
_, _ = h.annotations.CreateReviewFeedback(...)
_, _ = h.annotations.LinkGuidelineToRun(...)
```

The fix moved the combined operation into the repository layer with explicit transactions. Two new public methods were added:

```go
// Repository method: atomic review + optional comment + optional guideline links
func (r *Repository) ReviewAnnotationWithArtifacts(
    ctx context.Context,
    annotationID string,
    action ReviewAnnotationActionInput,
) (*Annotation, error)

// Repository method: atomic batch review + optional comment + optional guideline links
func (r *Repository) BatchReviewWithArtifacts(
    ctx context.Context,
    ids []string,
    action BatchReviewActionInput,
) ([]Annotation, error)
```

The `ReviewAnnotationActionInput` type carries the review state plus optional feedback fields:

```go
type ReviewAnnotationActionInput struct {
    ReviewState    string
    Comment        *ReviewCommentInput   // nil means no comment
    GuidelineIDs   []string              // empty means no guideline linking
    MailboxName    string
}
```

Inside `BatchReviewWithArtifacts`, there is a careful semantic check: guideline linking is run-scoped, but a batch of annotations may span multiple runs. The implementation is intentionally strict — it returns an error if guideline linking is requested across multiple runs, rather than guessing which run to link to:

```go
// Only link guidelines if all selected annotations belong to one run
if len(action.GuidelineIDs) > 0 {
    singleRunID, err := r.inferSingleRunIDForAnnotationsTx(ctx, tx, ids)
    if err != nil {
        return nil, err
    }
    if singleRunID == "" {
        return nil, fmt.Errorf(
            "cannot link guidelines: batch spans multiple runs; " +
            "either select annotations from one run or omit guideline_ids",
        )
    }
    // proceed with linking in the same transaction
}
```

### The Schema

The new tables added in V4 of the annotation schema:

```sql
-- Feedback attached to a review action
CREATE TABLE review_feedback (
    id TEXT PRIMARY KEY,
    scope_kind TEXT NOT NULL DEFAULT 'selection',  -- selection, annotation, run, sender
    agent_run_id TEXT NOT NULL DEFAULT '',
    mailbox_name TEXT NOT NULL DEFAULT '',
    feedback_kind TEXT NOT NULL DEFAULT 'comment',  -- comment, reject_request, guideline_request, clarification
    status TEXT NOT NULL DEFAULT 'open',           -- open, acknowledged, resolved, archived
    title TEXT NOT NULL DEFAULT '',
    body_markdown TEXT NOT NULL DEFAULT '',
    created_by TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Targets that feedback is attached to
CREATE TABLE review_feedback_targets (
    feedback_id TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    PRIMARY KEY (feedback_id, target_type, target_id)
);

-- Reusable review criteria
CREATE TABLE review_guidelines (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    scope_kind TEXT NOT NULL DEFAULT 'global',  -- global, selection, run, sender
    status TEXT NOT NULL DEFAULT 'active',      -- active, draft, archived
    priority INTEGER NOT NULL DEFAULT 0,
    body_markdown TEXT NOT NULL DEFAULT '',
    created_by TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Links between agent runs and review guidelines
CREATE TABLE run_guideline_links (
    agent_run_id TEXT NOT NULL,
    guideline_id TEXT NOT NULL,
    linked_by TEXT NOT NULL DEFAULT '',
    linked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (agent_run_id, guideline_id)
);
```

### The Recovery Lesson

The Phase 2 recovery diary is worth reading carefully. The assistant's first attempt at Phase 2 produced useful code but introduced redundant handler scaffolding (duplicate request types, unused helpers) that caused `unused` lint failures. More importantly, the combined review operation was not transactional.

The recovery plan documented in the diary was:
1. remove duplicate/unused types and helpers
2. add transactional repository methods for single + batch review with artifacts
3. rewire handlers to call those repository methods
4. validate with `gofmt`, `go test -tags sqlite_fts5 ./...`, and `make lint`
5. commit only after all three succeed

This discipline mattered. An earlier docs-only commit attempt failed because older staged versions of backend files were still in the git index — the pre-commit hook ran tests against the stale staged copy, not the cleaned working tree.

## Phase 3: Protobuf Contract Codegen

The contract codegen ticket (SMN-20260406-CONTRACT-CODEGEN) was the most architecturally significant piece of work. It introduced a shared IDL and code generation pipeline so that Go and TypeScript wire contracts are driven by the same `.proto` source.

### Why Protobuf

The immediate motivation was the feedback create drift:
- TypeScript: `targetIds?: string[]`
- Go: `targets: [{ targetType, targetId }]`

But the deeper goal was structural. The annotation UI had three layers of type definitions that could drift independently:
1. Go domain/repository structs in `pkg/annotate/types.go`
2. Go HTTP DTOs in `pkg/annotationui/types_feedback.go`
3. TypeScript frontend DTOs in `ui/src/types/reviewFeedback.ts`

Protobuf gives one source of truth. Generated Go structs anchor the HTTP boundary; generated TypeScript interfaces anchor the frontend layer.

### Design Decisions

**String-valued workflow fields over protobuf enums.** The wire format keeps workflow/status/kind values as strings (e.g., `"status": "open"`) rather than integers. This preserves the current REST JSON shape and keeps it human-readable. A later schema revision can upgrade to protobuf enums if the API is ready to change.

**ts-proto over @bufbuild/protobuf.** The TypeScript generator uses `ts-proto` via Buf remote plugins so output is plain TypeScript interfaces, not message-runtime branded objects. The alternative — `@bufbuild/protobuf` with `fromJson()` calls — would have added runtime complexity for simple REST JSON payloads. The frontend uses RTK Query and plain JSON; it doesn't need a protobuf runtime.

**Repository/domain structs stay hand-written.** The generated code only lives at the HTTP wire boundary. Repository structs, database queries, and business logic remain in `pkg/annotate/`. The mappers between generated wire types and domain structs live in `pkg/annotationui/contracts_review.go`.

### The Pipeline

```text
proto/smailnail/annotationui/v1/review.proto
        │
        ▼
cmd/generate-annotationui-contracts (go run ./cmd/generate-annotationui-contracts)
        │
        ▼
    buf generate
      /      \
     ▼        ▼
pkg/gen/smailnail/    ui/src/gen/smailnail/
 annotationui/v1/       annotationui/v1/
  review.pb.go          review.ts
```

The generator is wired into `go generate` via `pkg/annotationui/generate.go`:

```go
//go:generate go run ../cmd/generate-annotationui-contracts
```

So `go generate ./pkg/annotationui` reproduces the full pipeline locally.

### The Proto Schema

```protobuf
message ReviewFeedback {
  string id = 1;
  string scope_kind = 2;
  string agent_run_id = 3;
  string mailbox_name = 4;
  string feedback_kind = 5;
  string status = 6;
  string title = 7;
  string body_markdown = 8;
  string created_by = 9;
  string created_at = 10;
  string updated_at = 11;
  repeated FeedbackTarget targets = 12;
}

message CreateFeedbackRequest {
  string scope_kind = 1;
  string agent_run_id = 2;
  string mailbox_name = 3;
  string feedback_kind = 4;
  string title = 5;
  string body_markdown = 6;
  repeated FeedbackTarget targets = 7;  // note: not targetIds
}

message ReviewAnnotationRequest {
  string review_state = 1;
  optional ReviewComment comment = 2;
  repeated string guideline_ids = 3;
  string mailbox_name = 4;
}
```

The key fix: `CreateFeedbackRequest.targets` is now `repeated FeedbackTarget`, matching the Go handler's expectation.

### List Response Wrappers

List endpoints use explicit wrapper messages with `items`:

```protobuf
message ReviewFeedbackListResponse {
  repeated ReviewFeedback items = 1;
}
```

The frontend unwraps these in RTK Query's `transformResponse`:

```typescript
transformResponse: (response: { items: T[] }) => response.items,
```

This keeps the frontend API layer clean without hand-writing parallel DTOs.

## The React UI: 14 Phased Steps

The frontend work was implemented in 14 disciplined phases. Each phase was committed separately with a diary entry.

### Phases 3–5: Types, Mocks, and Shared Components

Phase 3 added TypeScript types and RTK Query contracts for feedback and guidelines. Phase 4 added MSW mock data and handlers. Phase 5 created shared badge widgets: `MailboxBadge`, `FeedbackKindBadge`, `FeedbackStatusBadge`, and `GuidelineScopeBadge`. These shared components established a visual language early so the specialized widgets could compose them.

### Phases 6–8: ReviewFeedback Widgets

Phase 6 created the `ReviewFeedback/` widget directory: `GuidelinePicker`, `GuidelineLinkPicker`, `ReviewCommentDrawer`, `ReviewCommentInline`, and `FeedbackCard`. The `GuidelineLinkPicker` is a modal that lets reviewers attach one or more guidelines to the current action. The `ReviewCommentDrawer` became the shared form for feedback entry.

Phase 7 enhanced `ReviewQueuePage` with the `ReviewCommentDrawer` for batch reject flows. "Reject & Explain" opens the drawer; "Just Dismiss" fast path still works without it.

Phase 8 continued polishing the ReviewFeedback widgets with Storybook stories.

### Phase 9: RunGuideline Widgets

Phase 9 created `RunGuideline/` with `GuidelineCard` and `RunGuidelineSection`. `GuidelineCard` is a compact card showing a guideline with scope badge, priority, status, and an optional unlink button. `RunGuidelineSection` wraps the list and provides "Link Existing" + "Create New" buttons, integrating the `GuidelineLinkPicker` from Phase 6.

The "Create New" button navigates to a guidelines page with a `?runId=` query param, avoiding embedding a full guideline creation form inside the run detail page.

### Phase 10: RunDetailPage Integration

Phase 10 wired `RunGuidelineSection` and `RunFeedbackSection` into the existing run detail page. Guidelines appear before the timeline; feedback appears after. This is deliberate — it follows the reviewer's mental flow: understand the rules → see what happened → provide feedback → drill into annotations.

The diary for this phase documents a painful lesson: the edit tool requires exact byte-for-byte matching. After three failed edit attempts (due to stale file contents from prior edits), the approach was restored from git and four small targeted edits compiled on first try. The rule: always re-read the file immediately before editing.

### Phases 11–12: Guidelines Management Pages

Phase 11 created the full guidelines management UI: `GuidelineSummaryCard`, `GuidelineForm` (with view/edit/create modes and Markdown preview tabs), `GuidelineLinkedRuns`, plus `GuidelinesListPage` and `GuidelineDetailPage`. The list page supports status filter chips and search. The detail page detects mode from the route (`/new` vs `/:id`) and handles the create-then-link-to-run flow via the `?runId=` query param.

Phase 12 added the "Guidelines" entry to the sidebar and wired the three routes into `App.tsx`. Route order matters: `guidelines/new` must come before `guidelines/:guidelineId` to avoid `:guidelineId` matching "new".

### Phases 13–14: Mailbox Context and Redux Slice

Phase 13 added a Mailbox column to the message preview table in the sender detail page. A notable observation: Phase 13's tasks 13A/13B (mailbox in AnnotationTable/AnnotationDetail) couldn't be implemented because the `Annotation` type doesn't carry `mailboxName` — that field only exists on `MessagePreview`. The data model doesn't have mailbox provenance on annotations, only on messages.

Phase 14 added `commentDrawerOpen` and `filterMailbox` to the Redux `annotationUiSlice`. These enable cross-component drawer coordination and prepare for future mailbox filter pills.

## Performance Work

The review queue had a perceived delay when toggling row checkboxes — the Redux action felt dispatched a second late.

Investigation revealed the issue was not dispatch latency. The real problem was render work. The annotation table recomputed related-annotation lists for every row on every render, even though only the expanded row ever displayed them. The fix was surgical: only call `getRelated(ann)` when `isExpanded` is true.

A broader follow-up introduced a memoized `AnnotationTableItem` that owns both the visible row and the optional detail row. The table now derives `selectedSet` with `useMemo`, computes the expanded row's related annotations once, and only mounts `AnnotationDetail` for the expanded row. The key insight: it is cheaper to render nothing than to render many collapsed components.

```typescript
const AnnotationTableItem = memo(
  // ...
  (prev, next) =>
    prev.annotation === next.annotation &&
    prev.isSelected === next.isSelected &&
    prev.isExpanded === next.isExpanded &&
    prev.relatedAnnotations === next.relatedAnnotations &&
    prev.feedback === next.feedback &&
    prev.guidelines === next.guidelines &&
    // callback stability matters more once React.memo is involved
    prev.onToggleSelect === next.onToggleSelect &&
    prev.onToggleExpand === next.onToggleExpand &&
    prev.onApprove === next.onApprove &&
    prev.onDismiss === next.onDismiss &&
    prev.onDismissExplain === next.onDismissExplain &&
    prev.onNavigateTarget === next.onNavigateTarget &&
    prev.columnCount === next.columnCount,
);
```

The drawer state was migrated from local `useState` to Redux `toggleExpandedId` so the expand action stays stable after memoization.

## The Dismiss-Explain UX Fix

Early in the review queue UX, batch "Reject & Explain" rendered inline below the batch action bar. This forced reviewers to scroll down to fill in the form. The fix converted it to a centered `Dialog`. The same affordance was added to sender detail and run detail annotation rows for single-item feedback.

The `ReviewCommentDrawer` became a shared component used in three contexts:
- batch reject from the review queue (mode: "batch")
- per-row dismiss from annotation detail (mode: "single")
- run-level feedback from the run detail page (mode: "run")

The drawer uses `useEffect` to reset form state on open/cancel/submit:

```typescript
useEffect(() => {
  if (open) {
    resetForm();
  }
}, [open, mode]);
```

### Mixed-Run Guideline Linking Guard

A code review finding surfaced a bug: `ReviewQueuePage` sent `guidelineIds` in batch review requests without `agentRunId`. But the backend only allows run-guideline linking when either an explicit `agentRunId` is provided or all selected annotations belong to one run. In the review queue, selections can span multiple runs — so mixed selections would hit a transactional rollback.

The fix derives `singleSelectedRunId` from the current selection:

```typescript
const selectedRunIds = new Set(
  selectedAnnotations.map((ann) => ann.agentRunId).filter(Boolean),
);
const singleSelectedRunId =
  selectedRunIds.size === 1 ? [...selectedRunIds][0] : undefined;
```

When `singleSelectedRunId` is undefined (mixed runs), guideline attachment UI is disabled with an explanation. This prevents confusing rollback errors and gives reviewers clear feedback about why the feature is unavailable.

## The UI Consistency Playbook

The final major documentation artifact is the Annotation UI Review Consistency Playbook. It captures the core invariant that keeps the multi-page UI coherent: each routed page is a composition boundary, and every visible artifact must come from an explicit query with an explicit invalidation path.

The mental model:

```
Page = base entity query
     + explicit artifact subqueries
     + explicit invalidation map
```

The RTK Query tag families are: `Annotations`, `Runs`, `Senders`, `Feedback`, `Guidelines`, `Groups`, `Logs`, `Queries`. Every mutation must invalidate at least one tag; every query must provide at least one tag. Without this discipline, writes succeed but pages stay stale — a class of bug that is easy to introduce and hard to diagnose without explicit contracts.

The playbook also codifies page ownership rules. Run detail is the reference composed page: it owns run summary counters, run annotations, linked guidelines, run-scoped feedback, and annotation-scoped feedback for the expanded row. Sender detail owns sender profile, annotations, logs, messages, annotation feedback, and guideline-linked runs. Guideline detail owns guideline fields, linked runs, and create/edit/link flows.

## Code Review Passes

The PR went through two code review passes. The first was a detailed review finding the mixed-run guideline linking bug and several other issues. The second was an "intern-facing" review that assessed the code from the perspective of an engineer who hadn't written it — looking for clarity, obvious missing tests, and behavior that would surprise a newcomer.

The intern review was valuable. It surfaced the exact issue that would bite a new engineer first: the repository methods that extend annotation review state with feedback/guideline linking don't validate that the calling context has the right mailbox context. A reviewer dismissing annotations from the INBOX mailbox should not silently attach feedback to a "sent mail" guideline.

## What's Left

The PR is feature-complete for the review workflow as designed. Remaining considerations:

- **Annotation-level mailbox provenance**: the `Annotation` type doesn't carry `mailboxName`. Adding it would enable annotation-level mailbox filtering and badges, which Phase 13 couldn't implement.
- **Guideline recommendation from dismissal explanations**: the dismiss-explain flow creates feedback but doesn't auto-generate guideline suggestions from the explanation text. This is a future product decision.
- **Run-level guideline linking as a first-class operation**: currently, linking a guideline to a run happens as a side effect of reviewing. A dedicated "manage run guidelines" flow would be cleaner.
- **Transaction failure testing**: the diary explicitly calls for repository + handler tests that simulate failure in feedback creation or guideline linking and verify that review state is not committed independently.

## Files Worth Reading

If you want to understand one piece of this PR, start here:

| File | Why |
|------|-----|
| `pkg/annotate/repository_feedback.go` | Transactional review + feedback + guideline linking in 810 lines |
| `pkg/annotationui/handlers_feedback.go` | Thin HTTP handlers over the repository |
| `pkg/annotationui/contracts_review.go` | Mappers between generated protobuf and domain types |
| `proto/smailnail/annotationui/v1/review.proto` | The single source of truth for the wire contract |
| `ui/src/components/AnnotationTable/AnnotationTable.tsx` | Memoized table architecture |
| `ui/src/components/ReviewFeedback/ReviewCommentDrawer.tsx` | Shared feedback form in three modes |
| `pkg/doc/annotationui-review-consistency-playbook.md` | The invariant that keeps multi-page UI coherent |
| `pkg/doc/annotationui-contract-codegen-playbook.md` | How to extend the protobuf codegen pipeline |
| `ttmp/.../reference/02-diary.md` (ANNOTATION-BACKEND) | The 19-step implementation diary |

## Related notes

- [[PROJ - Smailnail]] — parent project
- [[ttmp/SMN-20260403-ANNOTATION-BACKEND]] — backend ticket
- [[ttmp/SMN-20260403-RUN-REVIEW]] — run review + guidelines ticket  
- [[ttmp/SMN-20260406-CONTRACT-CODEGEN]] — codegen implementation
- [[ttmp/SMN-20260407-ANNOTATION-UI-CONSISTENCY-TTMP]] — UI consistency pass
