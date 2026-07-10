# SQL three-valued logic

- Source: PostgreSQL 18 documentation, “Logical Operators”.
- URL: https://www.postgresql.org/docs/current/functions-logical.html
- Accessed: 2026-07-10.

SQL logical expressions range over TRUE, FALSE, and UNKNOWN. For conjunction, FALSE dominates UNKNOWN, while TRUE AND UNKNOWN remains UNKNOWN. The prototype avoids an explicit three-valued Boolean encoding in hardware by supporting only conjunctions of leaf predicates and returning one bit per leaf: TRUE maps to one; FALSE and UNKNOWN both map to zero. This collapse preserves the final WHERE retention decision for conjunctions but would not be a general implementation of OR and NOT.
