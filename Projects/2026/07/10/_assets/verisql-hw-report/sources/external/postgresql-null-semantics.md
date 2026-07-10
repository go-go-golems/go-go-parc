# SQL comparison and NULL semantics

- Source: PostgreSQL 18 documentation, “Comparison Functions and Operators”.
- URL: https://www.postgresql.org/docs/current/functions-comparison.html
- Accessed: 2026-07-10.

Ordinary comparisons with a NULL operand produce NULL, representing UNKNOWN. `IS NULL` and `IS NOT NULL` return ordinary Boolean results. VeriSQL-HW maps UNKNOWN to a rejected row at the predicate cell. That mapping is correct for its WHERE-only conjunction grammar because SQL WHERE retains rows only when the full condition is TRUE.
