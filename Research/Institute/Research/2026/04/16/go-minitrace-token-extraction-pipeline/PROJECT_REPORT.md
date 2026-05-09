# Project: Building a Token Usage and Billing Extraction Pipeline with go-minitrace

**Date:** 2026-04-16  
**Project Location:** `~/code/wesen/obsidian-vault/Research/Institute/2026-04-16/go-minitrace-token-extraction-pipeline/`  
**Tools Used:** go-minitrace, DuckDB, Python, jq  
**Source Data:** Pi agent session JSONL files (Apr 15-16, 2026)

---

## Executive Summary

This project demonstrates how to build a complete token usage and billing extraction pipeline using **go-minitrace** to analyze AI agent transcripts. The pipeline converts native Pi session logs into minitrace format, validates accuracy against raw data, and extracts detailed token metrics including:

- Input/output tokens (billed)
- Cache read tokens (discounted)
- Time-series analysis by hour
- Billing calculations (input + output)

**Key Result:** Successfully extracted and validated 674,580 billing tokens across 402 API calls from 3 sessions.

---

## 1. Project Architecture

### 1.1 Pipeline Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌────────────────┐
│  Raw Pi JSONL   │───▶│ go-minitrace     │───▶│  DuckDB/SQL     │───▶│  Python/jq     │
│  Session Files  │    │ convert pi       │    │  Query Engine   │    │  Analysis      │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └────────────────┘
       │                        │                       │                    │
       │                        │                       │                    │
       ▼                        ▼                       ▼                    ▼
  ~/.pi/agent/            .minitrace.json         SELECT model,         Hourly breakdown
  sessions/               (unified format)        SUM(input_tokens)     Validation
```

### 1.2 Directory Structure

```
go-minitrace-token-extraction-pipeline/
├── diary/                          # Investigation log and documentation
│   ├── 00_investigation_diary.md   # Step-by-step process
│   ├── SCRIPT_README.md            # Script documentation
│   └── token_accounting_explained.md  # Token type definitions
├── scripts/                        # Python extraction scripts (5 versions)
│   ├── 01_extract_tokens_v1.py
│   ├── 02_extract_tokens_v2_billing.py
│   ├── 03_extract_tokens_validation.py
│   ├── 04_tokens_by_hour_basic.py
│   └── 05_tokens_by_hour_complete.py
├── queries/                        # DuckDB queries used
│   └── README.md
├── data/                           # Extracted datasets
│   └── glm51_turns_dataset.json
└── PROJECT_REPORT.md               # This file
```

---

## 2. Phase 1: Data Discovery and Conversion

### 2.1 Discovering Source Sessions

**Goal:** Find Pi sessions from April 15-16, 2026 that used the glm-5.1 model.

**Approach:**
```bash
# Locate Pi session directories
ls ~/.pi/agent/sessions/ | grep -E "Apr (15|16)"

# List session files
ls -la ~/.pi/agent/sessions/--home-manuel-code-wesen-*/
```

**Discovery Results:**
- Found 10+ session directories with timestamps from Apr 15-16
- Filtered to 3 sessions with glm-5.1 model usage
- Total raw data: ~5.4 MB of JSONL files

### 2.2 Conversion to Minitrace Format

**Command:**
```bash
go-minitrace convert pi \
  --source-dir ~/.pi/agent/sessions/--home-manuel-code-wesen-corporate-headquarters-go-minitrace-- \
  --output-dir ./pi-sessions
```

**Conversion Results:**
| Session | Source Size | Turns | Tool Calls | Quality |
|---------|-------------|-------|------------|---------|
| d5862158 | 1.7 MB | 95 | 98 | A |
| 2035dd97 | 3.5 MB | 813 | 777 | A |
| 07fe66a4 | 292 KB | 60 | 61 | A |

**Output Format:** `.minitrace.json` files with unified schema including:
- `id`, `timestamp`, `model`
- `usage.input_tokens`, `usage.output_tokens`
- `usage.cache_read_tokens`, `usage.cache_creation_tokens`

---

## 3. Phase 2: Query Interface Analysis

### 3.1 Built-in Query Presets

go-minitrace provides two query interfaces:

**Interface 1: `query duckdb` - Ad-hoc SQL**

Available presets:
| Preset | Purpose |
|--------|---------|
| `session-list` | Per-session metadata |
| `framework-summary` | Aggregate stats by framework |
| `tool-operation-breakdown` | Tool calls by operation type |
| `timing-analysis` | Duration, TTFA, idle ratio |
| `read-ratio-distribution` | Read/modify/create/execute counts |
| `annotations` | Annotation data |

**Example Usage:**
```bash
go-minitrace query duckdb \
  --archive-glob './pi-sessions/active/*/*.minitrace.json' \
  --preset session-list
```

**Interface 2: `query commands` - Structured Repository**

Command groups:
- `overview`: `session-list`, `framework-summary`, `annotations`
- `files`: `file-operations`, `file-timeline`
- `tools`: `tool-operation-breakdown`, `tool-failures`
- `timing`: `timing-analysis`

### 3.2 Custom SQL for Token Extraction

**Challenge:** Built-in presets don't unnest turn-level token data.

**Solution:** Custom SQL with `UNNEST(turns)`:

```sql
SELECT
  t.turn->>'model' AS model,
  t.turn->>'timestamp' AS timestamp,
  CAST(t.turn->'usage'->>'input_tokens' AS BIGINT) AS input,
  CAST(t.turn->'usage'->>'output_tokens' AS BIGINT) AS output,
  CAST(t.turn->'usage'->>'cache_read_tokens' AS BIGINT) AS cache_read
FROM sessions_base, UNNEST(turns) AS t(turn)
WHERE t.turn->>'model' = 'glm-5.1'
  AND t.turn->'usage'->>'input_tokens' IS NOT NULL
```

**Result:** Granular turn-level token data for time-series analysis.

---

## 4. Phase 3: Validation and Cross-Reference

### 4.1 The Token Accounting Challenge

**Initial Problem:** Raw Pi JSONL shows different token structure than expected.

**Pi JSONL Format:**
```json
{
  "type": "message",
  "message": {
    "model": "glm-5.1",
    "usage": {
      "input": 410,           // Billed
      "output": 250,          // Billed
      "cacheRead": 7680,      // Discounted
      "cacheWrite": 0,
      "totalTokens": 8340     // input + output + cacheRead + cacheWrite
    }
  }
}
```

**Key Finding:** `totalTokens` is NOT billing tokens. It's the sum of all token types.

### 4.2 Python Validation Pipeline

Created 3 validation scripts to cross-reference:

**Script 1: Basic Extraction**
```python
def extract_tokens_from_session(filepath):
    model_stats = defaultdict(lambda: {
        "calls": 0, "input": 0, "output": 0, 
        "cache_read": 0, "total_tokens": 0
    })
    
    for line in open(filepath):
        entry = json.loads(line)
        if entry.get('type') == 'message':
            message = entry.get('message', {})
            usage = message.get('usage')
            model = message.get('model')
            
            if usage and model:
                model_stats[model]["input"] += usage.get('input', 0)
                model_stats[model]["output"] += usage.get('output', 0)
                model_stats[model]["cache_read"] += usage.get('cacheRead', 0)
```

**Script 2: Billing Calculation**
Added billing tokens calculation:
```python
model_stats[model]["billing_tokens"] = (
    usage.get('input', 0) + usage.get('output', 0)
)
```

**Script 3: Minitrace Cross-Reference**
Validated minitrace conversion accuracy:
- Raw Pi cacheRead: 35,757,824
- Minitrace cache_read_tokens: 35,757,824 ✓
- Exact match confirmed

### 4.3 Validation Results

| Metric | Raw Pi JSONL | Minitrace | Match |
|--------|--------------|-----------|-------|
| Input | 587,724 | 587,724 | ✓ |
| Output | 86,856 | 86,856 | ✓ |
| Cache Read | 35,757,824 | 35,757,824 | ✓ |
| Billing (I+O) | 674,580 | 674,580 | ✓ |

**Conclusion:** Minitrace conversion is complete and accurate. Cache tokens ARE included but weren't initially extracted in our queries.

---

## 5. Phase 4: Time-Series Analysis Pipeline

### 5.1 Building the Hourly Extractor

**Challenge:** Need to aggregate tokens by hour across multiple sessions with different time ranges.

**Solution:** Python script with datetime parsing:

```python
def extract_tokens_by_hour(filepath):
    hourly_stats = defaultdict(lambda: {
        "calls": 0, "input": 0, "output": 0, "cache_read": 0
    })
    
    for turn in data.get('turns', []):
        if turn.get('model') != 'glm-5.1':
            continue
            
        timestamp = turn.get('timestamp')
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        hour_key = dt.strftime('%Y-%m-%d %H:00')
        
        hourly_stats[hour_key]["input"] += usage.get('input_tokens', 0)
        hourly_stats[hour_key]["output"] += usage.get('output_tokens', 0)
        hourly_stats[hour_key]["cache_read"] += usage.get('cache_read_tokens', 0)
```

### 5.2 Complete Token Table

Generated table with all 5 token metrics:

| Hour | Calls | Input | Output | Cached | Total | Billing |
|------|-------|-------|--------|--------|-------|---------|
| 2026-04-15 15:00 | 30 | 52,692 | 5,284 | 1,335,744 | 1,393,720 | 57,976 |
| 2026-04-16 18:00 | 144 | 246,209 | 29,409 | 12,052,096 | 12,327,714 | 275,618 |
| 2026-04-16 19:00 | 103 | 164,858 | 28,914 | 13,881,472 | 14,075,244 | 193,772 |
| 2026-04-16 20:00 | 125 | 123,965 | 23,249 | 8,488,512 | 8,635,726 | 147,214 |
| **TOTAL** | **402** | **587,724** | **86,856** | **35,757,824** | **36,432,404** | **674,580** |

### 5.3 Visualization

Created ASCII bar chart for billing distribution:
```
Hour              Billing    % of Total    Visual
─────────────────────────────────────────────────
Apr 15 15:00       57,976         8.6%    ████
Apr 16 18:00      275,618        40.9%    ████████████████████
Apr 16 19:00      193,772        28.7%    ██████████████
Apr 16 20:00      147,214        21.8%    ██████████
```

---

## 6. Key Technical Insights

### 6.1 Token Types Explained

| Token Type | Definition | Billed? | Typical Rate |
|------------|------------|---------|--------------|
| **Input** | New tokens sent to API | Yes | ~$0.50-2.00/M |
| **Output** | Generated response tokens | Yes | ~$1.00-5.00/M |
| **Cache Read** | Reused context from cache | Discounted | ~$0.00-0.50/M |
| **Cache Write** | Context written to cache | Usually free | Free |
| **Billing** | Input + Output | = Cost | Sum of above |
| **Total** | Input + Output + Cache | ≠ Cost | Informational only |

### 6.2 Why Cache Tokens Are 98% of Total

The 35,757,824 cache tokens represent conversation context that Pi reuses across API calls:

- Each API call sends ~1,460 input tokens on average
- But the AI "sees" all previous context via cache (~89K tokens per call)
- Cache hits = faster responses + cheaper than re-sending full context
- Cache ratio: 35.7M / 36.4M = 98.1% of all tokens

### 6.3 Minitrace Schema Advantages

The minitrace format provides:
- **Unified schema** across Pi and Codex sessions
- **Hierarchical structure** with session → turns → usage
- **Standardized field names** (input_tokens, output_tokens, cache_read_tokens)
- **JSON queryability** with jq or DuckDB

---

## 7. Pipeline Reproducibility

### 7.1 Full Pipeline Commands

```bash
# Step 1: Convert Pi sessions
go-minitrace convert pi \
  --source-dir ~/.pi/agent/sessions/<session-dir> \
  --output-dir ./minitrace-output

# Step 2: Query with DuckDB
go-minitrace query duckdb \
  --archive-glob './minitrace-output/active/*/*.minitrace.json' \
  --preset session-list

# Step 3: Extract turns with jq
cat session.minitrace.json | jq '[.turns[] | select(.model == "glm-5.1")]'

# Step 4: Run Python analysis
python3 scripts/05_tokens_by_hour_complete.py
```

### 7.2 Adaptation Guide

To analyze different models or time periods:

1. **Change model filter:**
   ```python
   if turn.get('model') != 'claude-3-opus':  # Change model name
   ```

2. **Change date range:**
   ```python
   if '2026-04-15' <= hour_key <= '2026-04-16':  # Adjust dates
   ```

3. **Add new metrics:**
   ```python
   hourly_stats[hour]["tool_calls"] += len(turn.get('tool_calls_in_turn', []))
   ```

---

## 8. Lessons Learned

### 8.1 What Worked Well

1. **go-minitrace conversion** preserved all token data accurately
2. **Python validation** caught potential discrepancies early
3. **Incremental script development** (v1 → v5) refined the approach
4. **Cross-referencing with raw data** confirmed accuracy

### 8.2 Challenges Overcome

1. **Token terminology confusion:** Initially thought "total" meant billing
   - **Solution:** Validated against raw Pi JSONL to understand accounting
   
2. **DuckDB type errors:** Complex JSON paths caused casting issues
   - **Solution:** Used Python for final time-series aggregation
   
3. **Multi-model sessions:** Sessions used multiple models (glm-5.1 + kimi-k2p5-turbo)
   - **Solution:** Filtered by turn-level model, not session-level

### 8.3 Best Practices Established

1. **Always validate conversions** against raw source data
2. **Understand token accounting** before calculating costs
3. **Use turn-level filtering** for model-specific analysis
4. **Cache tokens are not billing tokens** - don't use for cost estimation

---

## 9. Deliverables

### 9.1 Scripts (Version-Controlled Evolution)

| Version | Script | Purpose | Key Feature |
|---------|--------|---------|-------------|
| v1 | 01_extract_tokens_v1.py | Initial validation | Basic input/output extraction |
| v2 | 02_extract_tokens_v2_billing.py | Cost calculation | Added "billing" column (I+O) |
| v3 | 03_extract_tokens_validation.py | Cross-reference | Validated against raw Pi JSONL |
| v4 | 04_tokens_by_hour_basic.py | Time series | Hourly aggregation, 4 columns |
| v5 | 05_tokens_by_hour_complete.py | Complete analysis | 5 columns: input/output/cache/total/billing |

### 9.2 Documentation

- `00_investigation_diary.md` - Step-by-step process log
- `token_accounting_explained.md` - Token type definitions
- `SCRIPT_README.md` - Script usage guide
- `queries/README.md` - DuckDB query reference

### 9.3 Data

- `glm51_turns_dataset.json` - 402 turns with complete token data

---

## 10. Conclusion

This project demonstrates a complete pipeline for extracting token usage and billing information from AI agent transcripts:

1. **Data Conversion:** go-minitrace successfully converts Pi JSONL → unified format
2. **Query Flexibility:** DuckDB for presets, Python/jq for custom analysis
3. **Validation:** Cross-reference with raw data ensures accuracy
4. **Time-Series:** Hourly breakdown reveals usage patterns
5. **Cost Clarity:** Input+Output = billing, Cache = discounted

**Final Result:** 674,580 billing tokens (input + output) across 4 hours of active usage, with 98% of all tokens being efficiently cached context.

---

## Appendix A: File Locations

All project files are in:
```
~/code/wesen/obsidian-vault/Research/Institute/2026-04-16/
└── go-minitrace-token-extraction-pipeline/
    ├── PROJECT_REPORT.md (this file)
    ├── diary/
    ├── scripts/
    ├── queries/
    └── data/
```

## Appendix B: Running the Pipeline

```bash
cd ~/code/wesen/obsidian-vault/Research/Institute/2026-04-16/go-minitrace-token-extraction-pipeline

# View complete hourly table
python3 scripts/05_tokens_by_hour_complete.py

# Read token accounting guide
cat diary/token_accounting_explained.md

# View investigation diary
cat diary/00_investigation_diary.md | less
```

---

**Project Status:** ✅ Complete  
**Validation Status:** ✅ Cross-referenced with raw Pi JSONL  
**Accuracy:** ✅ Exact match on all token counts
