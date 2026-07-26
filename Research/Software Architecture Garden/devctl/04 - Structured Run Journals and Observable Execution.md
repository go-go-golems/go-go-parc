---
title: devctl — Structured Run Journals and Observable Execution
aliases:
  - devctl runlog architecture
  - devctl structured journal pattern
tags:
  - architecture-garden
  - devctl
  - logging
  - observability
status: active
type: architecture-pattern-study
pattern_maturity: candidate-ecosystem-pattern
created: 2026-07-26
analyzed: 2026-07-26
analysis_schema: architecture-garden-v1
repository: /home/manuel/workspaces/2026-07-07/prod-tiny-idp/devctl
repository_remote: git@github.com:go-go-golems/devctl.git
repository_commit: 303e264ab9f0d9721fc8a03eac8ed95e822735c8
repository_ref: task/prod-tiny-idp
repository_commit_date: 2026-07-26T17:44:09-04:00
repository_worktree: clean
analysis_commit: 7379e4d2ff9be55f546a1361f87e3f43c244f7ab
source_ticket: DEVCTL-OPERATOR-UX-001
related_files:
  - pkg/runlog/contracts.go
  - pkg/runlog/writer.go
  - pkg/runlog/framer.go
  - pkg/runlog/reader.go
  - pkg/runlog/follow.go
  - pkg/runlog/framer_test.go
  - pkg/runlog/reader_test.go
  - cmd/devctl/cmds/wrap_service.go
  - cmd/devctl/cmds/logs.go
  - pkg/tui/logs.go
related_notes:
  - "[[Research/Software Architecture Garden/devctl/README]]"
  - "[[Research/Software Architecture Garden/devctl/02 - Durable State Process Identity and Wrapper Evidence]]"
---

# Structured Run Journals and Observable Execution

Service output has two legitimate consumers. A human debugging an application may need the exact bytes written to stdout or stderr. A program rendering, filtering, following, or merging output needs stable records with identity and ordering. `devctl` preserves both forms. The wrapper writes raw stream files and a run-scoped JSONL journal from the same captured pipes.

## The five original information planes

The architecture audit identified several pre-redesign forms of logging and events:

- service stdout and stderr files;
- devctl and plugin diagnostic logs;
- plugin protocol stream events;
- ephemeral TUI events;
- JavaScript-parsed log events.

The problem was not that several kinds of information existed. The problem was overlapping authority and incompatible access. A TUI event could disappear, raw files lacked record identity, and a separate parser created another interpretation layer.

The redesign narrows the durable service-output contract to:

```text
child stdout ─┬─> stdout.log  (exact raw stream)
              └─> logs.jsonl  (structured records)

child stderr ─┬─> stderr.log  (exact raw stream)
              └─> logs.jsonl  (structured records)
```

Plugin diagnostics remain stderr on the plugin transport boundary, and operator events remain typed operation progress. These sources are not forced into one undifferentiated log string.

## Record contract

`pkg/runlog/contracts.go` defines:

```go
type LogRecord struct {
    Version  int
    RunID    string
    Sequence uint64
    Time     time.Time
    Source   SourceKind
    Service  string
    Stream   StreamKind
    Level    string
    Text     string
    Partial  bool
    Fields   map[string]any
}
```

The important fields are identity, sequence, source, and stream.

- `RunID` connects output to an immutable service attempt.
- `Sequence` orders records within that run without relying only on time.
- `Source` distinguishes service, pipeline, plugin, and system records.
- `Stream` distinguishes stdout, stderr, and event records.
- `Partial` states that bounded framing split or terminated an incomplete line.
- `Fields` permits structured enrichment without changing the text contract.

Versioning makes schema evolution explicit. A reader can reject an unsupported version instead of decoding a record into a structurally similar but semantically different Go value.

## Capture and framing

`cmd/devctl/cmds/wrap_service.go` opens the raw files and journal with restrictive permissions. It obtains stdout and stderr pipes from the child before starting it, then invokes the runlog capture path.

Two streams can emit concurrently. The writer assigns one sequence space to their merged records, preserving the order in which the capture layer accepts fragments. Exact byte order across independent operating-system pipes is not globally defined, but the resulting journal has a deterministic order for consumers.

The framer cannot use an unbounded scanner. A service may write:

- a newline-terminated line;
- a partial final line;
- one line larger than normal scanner limits;
- arbitrary control bytes;
- output without any newline.

The bounded framer emits fragments when a record exceeds its maximum. Such fragments carry `Partial=true`. This converts an adversarial or accidental large line from an unbounded-memory problem into a sequence of valid records.

```text
while bytes arrive:
    append up to maximum frame size
    if newline appears:
        emit complete record
    else if maximum reached:
        emit partial record
    on EOF:
        emit remaining bytes as partial record
```

The raw file still preserves the exact stream. Structured framing therefore does not claim to be lossless byte representation; it is a bounded record projection.

## Query model

`runlog.Query` can filter:

- run IDs;
- services;
- source kinds;
- streams;
- levels;
- time bounds;
- text containment;
- tail count.

`FileReader.Query` resolves selected runs, reads journals, validates records, composes filters, tails per run, and merges results in stable order. Tailing per run matters. A global tail could let one noisy service hide the final output of another selected service.

```text
for each selected run:
    records = decode(run.logs.jsonl)
    records = applyAllFilters(records)
    if tail > 0:
        records = finalN(records, tail)

return stableMerge(allRunRecords)
```

The CLI can render the returned records as human text, a table, JSON, or JSONL. The TUI can store a bounded window and format it for the current terminal dimensions. Neither reader parses decorated output from the other.

## Cursor-based follow

A cursor is:

```go
type Cursor struct {
    RunID    string
    Sequence uint64
}
```

`FollowRequest.After` supplies a cursor per run. The follower queries records, emits only sequences greater than the cursor, advances after successful sink delivery, and polls for more.

The cursor includes the run ID to prevent a sequence from one attempt being applied to another. Since sequence numbers restart per run, a bare integer would be ambiguous.

Follow also records journal file identity and rejects replacement while following. A replaced file may have reused sequence numbers or unrelated content. Silently reopening it would violate cursor semantics. The reader returns a typed corruption error.

## Terminal detection and the exit artifact

The 2026-07-26 snapshot incorporates another PR review correction. A naturally exiting service may have:

- `run.json` still marked `ready`;
- final records already flushed to `logs.jsonl`;
- a valid `exit.json` written by the wrapper.

Waiting only for `run.Phase` to become terminal would make `logs --follow` wait forever until another command reconciled state. `allRunsTerminal` now treats a valid durable exit artifact as terminal even before `run.json` is updated.

```text
function allRunsTerminal(runIDs):
    for runID in runIDs:
        run = loadRun(runID)
        if run.phase is exited or failed:
            continue
        if valid exit.json exists:
            continue
        return false
    return runIDs is not empty
```

The implementation parses `exit.json`; file existence alone is insufficient. An invalid artifact returns an error. The wrapper writes the exit record after capture completion, so the follower can perform one final query, deliver the final records, and terminate on the next empty pass.

## TUI safety

Service output is untrusted terminal input. `pkg/tui/logs.go` sanitizes control characters before rendering and stores only a bounded record history. These are presentation-level protections built on the structured record contract:

- the runlog framer bounds individual records;
- the TUI bounds aggregate in-memory records;
- terminal sanitization prevents output from controlling the terminal;
- selection and scroll state remain TUI concerns.

This layered approach is preferable to embedding terminal rules in the journal writer. A non-terminal consumer may want different text handling.

## Why the dual representation works

Raw files and structured journals serve distinct contracts and derive from the same pipes. Neither is reconstructed from the other:

| Need | Representation |
|---|---|
| Exact original stdout bytes | `stdout.log` |
| Exact original stderr bytes | `stderr.log` |
| Merge streams | `logs.jsonl` |
| Filter by source or stream | `LogRecord` |
| Resume after a known point | `(runID, sequence)` cursor |
| Render safely in a terminal | bounded and sanitized record view |
| Diagnose structured corruption | typed `ReadError` |

The cost is additional disk use and capture complexity. The benefit is avoiding a false choice between human-forensic data and machine-oriented observability.

## Limits and future work

Following uses polling. This is simple and portable but adds latency and repeated filesystem reads. No evidence in the analyzed snapshot shows that polling is a performance problem at current scale. An event-notification layer should be added only after measurement and should preserve cursor semantics.

Retention is manual. Completed run directories remain until an operator archives or removes them. This preserves diagnosis but can consume unbounded disk over long periods. A future retention policy must never remove a current run and should distinguish age, count, total size, and failed-run preservation.

The journal is per run, not a global operation journal. Cross-run ordering uses timestamp plus stable merge rules, not one global sequence. This is appropriate for current service logs but should be documented if a future consumer interprets the merged output as a causal trace.

## Candidate ecosystem guidance

- Preserve exact source data and a typed projection when both forensic and machine consumers matter.
- Give every record stable source identity and sequence identity.
- Bound framing before parsing or rendering.
- Make cursor identity include the stream or run namespace.
- Treat journal replacement as a contract violation, not an implicit reset.
- Let terminal detection use the strongest durable terminal artifact available.
- Keep UI memory bounds and terminal sanitization at the presentation boundary.

## Key points

- Raw logs and structured journals are complementary, not competing.
- Run-scoped sequence numbers give stable ordering and resumption.
- Bounded partial records protect memory without discarding raw bytes.
- Queries compose filters and tail per run before stable merging.
- Follow validates journal identity and observes `exit.json` directly.
- Retention and polling are explicit current limits.
