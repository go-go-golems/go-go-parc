# SQLite atomic commit as a durability reference point

- Source: SQLite documentation, “Atomic Commit In SQLite”.
- URL: https://www.sqlite.org/atomiccommit.html
- Accessed: 2026-07-10.

SQLite defines atomic commit as an all-or-nothing transaction property that remains meaningful across process, operating-system, and power failures. It describes rollback journals, locking, flush ordering, and recovery. VeriSQL-HW does not implement this class of protocol: table rows are appended and fsynced, while catalog replacement uses a temporary file and rename, but there is no transaction journal coordinating them.
