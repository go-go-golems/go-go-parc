# DuckDB Queries Used in Investigation

## Preset Queries

```bash
# List sessions with metadata
go-minitrace query duckdb --archive-glob '<path>/*.minitrace.json' --preset session-list

# Framework summary
go-minitrace query duckdb --archive-glob '<path>/*.minitrace.json' --preset framework-summary

# Tool operations
go-minitrace query duckdb --archive-glob '<path>/*.minitrace.json' --preset tool-operation-breakdown

# Timing analysis
go-minitrace query duckdb --archive-glob '<path>/*.minitrace.json' --preset timing-analysis

# Read ratio distribution
go-minitrace query duckdb --archive-glob '<path>/*.minitrace.json' --preset read-ratio-distribution
```

## Custom SQL Queries

### Count by Model
```sql
SELECT
  environment->>'model' AS model,
  COUNT(*) AS sessions,
  SUM(CAST(metrics->>'turn_count' AS INT)) AS total_turns
FROM sessions_base
GROUP BY model
ORDER BY sessions DESC
```

### Token Analysis with UNNEST
```sql
SELECT
  t.turn->>'model' AS model,
  SUM(CAST(t.turn->'usage'->>'input_tokens' AS BIGINT)) AS input,
  SUM(CAST(t.turn->'usage'->>'output_tokens' AS BIGINT)) AS output,
  SUM(CAST(t.turn->'usage'->>'cache_read_tokens' AS BIGINT)) AS cache_read
FROM sessions_base, UNNEST(turns) AS t(turn)
WHERE t.turn->>'model' = 'glm-5.1'
GROUP BY model
```
