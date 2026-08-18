---
title: Snapshot Ordinals Require a Transactional Read Cut
aliases:
  - Cursor and rows from one consistency cut
  - Prefix-coherent materialized snapshots
  - Transactional snapshot read pattern
status: candidate
type: architecture-garden-design
created: 2026-08-18
analyzed: 2026-08-18
repository: /home/manuel/workspaces/2026-08-13/ragkit-coinvault-mysql/sessionstream
repository_remote: https://github.com/go-go-golems/sessionstream
source_pull_request: https://github.com/go-go-golems/sessionstream/pull/15
source_commit: 05028e4c119d2dd74a5738541c531af38df28e36
source_branch: task/ragkit-coinvault-mysql
tracking_issue: https://github.com/go-go-golems/sessionstream/issues/19
architecture_catalog: https://github.com/orgs/go-go-golems/projects/3
published_note_url: https://parc.yolo.scapegoat.dev/note/research/software-architecture-garden/sessionstream/designs/08-snapshot-ordinals-require-a-transactional-read-cut
repository_note_url: https://github.com/go-go-golems/go-go-parc/blob/main/Research/Software%20Architecture%20Garden/sessionstream/designs/08%20-%20Snapshot%20Ordinals%20Require%20a%20Transactional%20Read%20Cut.md
tags:
  - architecture-garden
  - sessionstream
  - snapshots
  - database
  - transactions
  - mvcc
  - event-sourcing
  - go
related_files:
  - /home/manuel/workspaces/2026-08-13/ragkit-coinvault-mysql/sessionstream/pkg/sessionstream/hydration.go
  - /home/manuel/workspaces/2026-08-13/ragkit-coinvault-mysql/sessionstream/pkg/sessionstream/hydration/mysql/store.go
  - /home/manuel/workspaces/2026-08-13/ragkit-coinvault-mysql/sessionstream/pkg/sessionstream/hydration/sqlite/store.go
  - /home/manuel/workspaces/2026-08-13/ragkit-coinvault-mysql/sessionstream/pkg/sessionstream/transport/ws/server.go
related_notes:
  - "[[Research/Software Architecture Garden/sessionstream/README|Architecture Garden — sessionstream]]"
  - "[[Research/Software Architecture Garden/sessionstream/designs/05 - Volatile Admission Is Not Durable Append]]"
  - "[[Research/Software Architecture Garden/sessionstream/Index of Design Patterns#Consistent SQLite snapshot cut]]"
  - "[[Research/Software Architecture Garden/sessionstream/Index of Design Patterns#Snapshot cut plus live suffix]]"
---

# Snapshot Ordinals Require a Transactional Read Cut

A snapshot is not a cursor read followed by some rows. It is a claim that one set of rows represents one declared version. If cursor and rows come from different database moments, transport can faithfully send an internally inconsistent snapshot before live events.

> [!summary]
> - A snapshot is the pair `(declared cut, state at that cut)`, not two independent queries.
> - Every returned entity must be valid at or before the declared snapshot ordinal.
> - Use one database read transaction or reconstruct rows explicitly from versions bounded by the captured ordinal.
> - Snapshot-before-live transport ordering cannot repair a database-incoherent cut.
> - Consistency level and transaction boundaries belong in the public snapshot contract.

## Why this note exists

Sessionstream’s `Snapshot` first calls `Cursor`, then queries either current entities or historical entity versions. In both SQLite and the new MySQL store, these are separate operations. The MySQL adapter uses a pool of up to 20 connections, making concurrent `Apply` between the two reads straightforward.

A reader can therefore return:

```text
SnapshotOrdinal = 10
Entities = state after event 11
```

The WebSocket adapter may correctly send this snapshot before buffered live event 11, but the entity already includes 11. The transport fence is ordered; the database cut is not coherent.

## Pattern statement

> **A versioned snapshot must read its declared version and all represented state from one consistency cut.** Use a read-only repeatable-read transaction, or query temporal/version rows bounded by a captured ordinal on one transaction. Never claim that transport ordering makes separately read database state atomic.

## Snapshot as a mathematical object

For session $s$, let $H_s^n=e_1\ldots e_n$ be the event prefix through ordinal $n$, and let $F$ be the materialization fold.

A snapshot is:

$$
\operatorname{Snapshot}(s,n)=(n,F(S_0,H_s^n)).
$$

For every returned entity $x$:

$$
\operatorname{lastEventOrdinal}(x)\le n.
$$

If an entity reflects event $n+1$ while the snapshot declares $n$, the pair is not a valid snapshot under this model.

## Concrete race

```mermaid
sequenceDiagram
    participant R as Snapshot reader
    participant DB as Database
    participant W as Apply writer

    R->>DB: SELECT snapshot_ordinal
    DB-->>R: 10
    W->>DB: BEGIN; update entities to 11; cursor=11; COMMIT
    R->>DB: SELECT current entities
    DB-->>R: entities at 11
    R-->>R: return ordinal 10 + state 11
```

The bug does not require dirty reads. Each query can be individually correct under read committed semantics while their pair is inconsistent.

## The two safe shapes

### Shape A: one repeatable-read transaction

```go
func (s *Store) Snapshot(ctx context.Context, sid SessionId, asOf uint64) (Snapshot, error) {
    tx, err := s.db.BeginTx(ctx, &sql.TxOptions{
        ReadOnly:  true,
        Isolation: sql.LevelRepeatableRead,
    })
    if err != nil { return Snapshot{}, err }
    defer tx.Rollback()

    cut := queryCursor(tx, sid)
    if asOf > 0 && asOf < cut { cut = asOf }
    entities := queryEntitiesAt(tx, sid, cut)

    if err := tx.Commit(); err != nil { return Snapshot{}, err }
    return Snapshot{SessionId: sid, SnapshotOrdinal: cut, Entities: entities}, nil
}
```

All reads observe one MVCC snapshot. The exact isolation mapping must be verified for MySQL/Aurora and SQLite.

### Shape B: version-bound rows

Even for latest state, capture `cut`, then reconstruct from `entity_versions`:

```sql
SELECT v.*
FROM entity_versions v
JOIN (
  SELECT kind, entity_id, MAX(ordinal) AS ordinal
  FROM entity_versions
  WHERE session_id = ? AND ordinal <= ?
  GROUP BY kind, entity_id
) latest USING (kind, entity_id, ordinal)
WHERE v.session_id = ?;
```

Run the cursor and version query in one read transaction. The ordinal predicate makes the state-cut relation explicit and avoids relying on a mutable “current” table.

Current entities can remain as a performance projection, but using them in a versioned snapshot requires proof that they are from the same cut.

## Database and transport cuts are different

Sessionstream’s WebSocket hydration protocol has another fence:

```text
register/buffer live
load snapshot at n
send snapshot
remove buffered events <= n
send buffered suffix > n
switch to live
```

This correctly orders a coherent snapshot and its live suffix. It does not create database coherence. Two laws compose:

```text
Store law:     snapshot rows represent declared cut n
Transport law: delivered live suffix contains only events after n
```

Both are required. Either one without the other is insufficient.

## Mathematical and CS foundations

### Consistent cuts

In a distributed/concurrent execution, a cut is consistent when it does not include an effect without its causal predecessors. Here the declared ordinal is a compact cut coordinate. Rows reflecting event 11 while declaring cut 10 include an effect beyond the cut.

### MVCC and snapshot isolation

MVCC lets one transaction read a stable historical database version while writers continue. The relevant guarantee comes from all reads sharing one transaction snapshot, not from each query independently using a transactional engine.

### Linearizability versus snapshot consistency

A snapshot need not be linearizable at a single wall-clock instant if the API promises a historical `asOf` cut. It must still be internally consistent with that cut. “Latest” can linearize at the transaction’s snapshot establishment point.

### Temporal materialization

Entity versions model:

$$
\operatorname{entityAt}(kind,id,n)
$$

and are the natural source for as-of reconstruction. The current-entity table is a cache/read model of the maximum applied version, not a substitute for a declared historical cut without a shared transaction.

## Pattern vocabulary

- **Unit of Work / read transaction:** one transaction owns the snapshot operation.
- **MVCC snapshot:** stable database version for concurrent reads.
- **Consistent cut:** selected state has no post-cut effects.
- **Temporal table/materialization:** versions retain state over ordinals.
- **Snapshot + live suffix:** transport composes a coherent cut with later observations.
- **Watermark/cursor:** coordinate summarizing represented progress; it is a claim, not just a number.

## Why tempting alternatives fail

### “The cursor query is fast”

A small race window is still a race. Correctness should not depend on query timing.

### “SQLite has one connection”

Serialization lowers probability but does not make separate API calls one transaction. A writer can run after the cursor query releases the connection.

### “Filter current entities by `last_event_ordinal <= cut`”

That can omit entities updated after the cut rather than recover their prior versions. Version history is required for a real as-of result.

### “The client discards live events at or below the cut”

If the snapshot already contains later state, discarding/ordering live frames may duplicate or hide transitions; transport cannot infer the database race.

### “Repeat the read if cursor changed”

An optimistic retry can work only with a complete validation rule and starvation policy. A read transaction is simpler and gives a direct database guarantee.

## Failure evidence

The original sessionstream Garden study already records “Consistent SQLite snapshot cut” as an open correctness obligation. PR #15 ports the same two-step shape to MySQL while increasing connection concurrency. The PR review provides a concrete interleaving demonstrating ordinal/row mismatch.

No production incident is claimed. This is a source-backed counterexample and open correctness obligation.

## Testing and verification

### Deterministic interleaving test

Instrument or lock the store so the test forces:

1. reader captures cursor 10;
2. writer commits Apply 11;
3. reader queries rows;
4. assert returned pair is either all 10 or all 11, never cut 10 with state 11.

### Contract assertions

```text
for every entity x in Snapshot(s,n):
    x.LastEventOrdinal <= n

Snapshot(s,asOf=n) is stable under later Apply calls
Snapshot(s,0) corresponds to one committed database cut
```

### Differential backends

Run the same snapshot history and controlled concurrency suite against SQLite and MySQL. Backend-specific transaction syntax may differ; the observable law must not.

### Migration/rebuild cross-check

Rebuild materialization from the event prefix through `n`, then compare with `Snapshot(s,n)`. This validates live materialization and historical reconstruction against one reference fold.

## Applicability

Use for versioned API responses, event-sourced read models, cursor-plus-row pagination snapshots, exports with revision headers, configuration snapshots, and reconnect protocols.

A non-versioned “best effort latest list” may not need this guarantee, but then it must not expose a cursor/revision that readers treat as describing the rows.

## Candidate ecosystem guidance

1. Treat `(revision, rows)` as one object with one consistency contract.
2. Bind all reads to one transaction snapshot.
3. Use temporal versions for true as-of reconstruction.
4. Keep storage cuts and transport fences separate and compose both explicitly.
5. Test forced interleavings, not only sequential snapshots.
6. Do not advertise a cursor as a cut unless every returned row is bounded by it.

## Open questions

- Should latest snapshots always read versions, or use current rows inside repeatable-read transactions for performance?
- What exact isolation options are portable across MySQL/Aurora and SQLite drivers?
- Should `Snapshot` expose a database/rebuild version in addition to event ordinal?
- How should snapshots behave if version history is compacted?
- Which other Garden projects can validate the same cursor-and-rows law?

## Evidence and references

- PR #15: https://github.com/go-go-golems/sessionstream/pull/15
- `pkg/sessionstream/hydration.go`: Snapshot contract surface.
- `pkg/sessionstream/hydration/mysql/store.go`: separate cursor/current-row reads.
- `pkg/sessionstream/hydration/sqlite/store.go`: existing two-read reference and version history.
- `pkg/sessionstream/transport/ws/server.go`: snapshot-before-live transport fence.
- [[Research/Software Architecture Garden/sessionstream/Index of Design Patterns#Consistent SQLite snapshot cut|Consistent SQLite snapshot cut]]
- [[Research/Software Architecture Garden/sessionstream/Index of Design Patterns#Snapshot cut plus live suffix|Snapshot cut plus live suffix]]
