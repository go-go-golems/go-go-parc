# PostgreSQL write-ahead logging

- Source: PostgreSQL 18 documentation, “Write-Ahead Logging”.
- URL: https://www.postgresql.org/docs/current/wal-intro.html
- Accessed: 2026-07-10.

The WAL rule requires log records describing a change to reach durable storage before the associated data-file change. Recovery can then redo changes not yet reflected in data pages. VeriSQL-HW has no WAL, LSN, checkpoint, redo path, or transactional commit record. Its storage layer should therefore be described as persistent append-only storage, not as a transactional database storage engine.
