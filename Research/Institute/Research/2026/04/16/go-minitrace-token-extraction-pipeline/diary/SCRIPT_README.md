# Python Scripts for go-minitrace Investigation

This directory contains Python scripts used to analyze glm-5.1 token usage from Pi sessions.

## Scripts Overview

### 1. `extract_tokens.py`
**Purpose:** Initial token extraction from raw Pi JSONL files  
**Created:** During investigation to validate minitrace conversion  
**Output:** Per-session token counts by model (input, output, cache_read, total)

```bash
python3 /tmp/extract_tokens.py
```

### 2. `extract_tokens_v2.py`
**Purpose:** Improved version with proper token accounting  
**Created:** After discovering Pi's `totalTokens = input + output + cacheRead + cacheWrite`  
**Key Finding:** Shows billing tokens (input+output) vs total processed tokens

```bash
python3 /tmp/extract_tokens_v2.py
```

**Output Format:**
- Input Tokens (billed)
- Output Tokens (billed)
- Billing Total (input + output)
- Cache Read (discounted/free)
- Total Processed (input + output + cache)

### 3. `extract_tokens_from_raw_pi.py`
**Purpose:** Final validation script with complete token breakdown  
**Created:** To cross-reference minitrace with raw Pi JSONL  
**Validates:** That minitrace conversion is accurate and complete

```bash
python3 /tmp/extract_tokens_from_raw_pi.py
```

**Validates:**
- Input: 587,724 ✓
- Output: 86,856 ✓
- Cache Read: 35,757,824 ✓
- Total matches raw Pi JSONL exactly

### 4. `tokens_by_hour.py`
**Purpose:** Time-series analysis of glm-5.1 token usage  
**Created:** To answer "count them over time, by hour" question  
**Output:** Hourly breakdown of calls, input, output, billing, and cache tokens

```bash
python3 /tmp/tokens_by_hour.py
```

**Output:**
- Per-session hourly breakdown
- Combined hourly summary
- Daily summary (Apr 15 vs Apr 16)
- ASCII bar chart of hourly distribution

## Data Files

### `glm51_turns.json`
**Content:** All 402 glm-5.1 turns from 3 sessions with timestamps and token usage  
**Created:** Extracted from minitrace files for time-series analysis  
**Size:** ~79KB  
**Format:** JSON array of turn objects

```json
{
  "session_id": "d5862158-...",
  "timestamp": "2026-04-15T15:50:51.051Z",
  "model": "glm-5.1",
  "input": 40233,
  "output": 64,
  "cache_read": 704
}
```

## Key Findings from Scripts

### Token Accounting
Pi JSONL usage structure:
```json
{
  "usage": {
    "input": 410,        // Billed
    "output": 250,       // Billed
    "cacheRead": 7680,   // Discounted/free
    "cacheWrite": 0,
    "totalTokens": 8340  // input + output + cacheRead + cacheWrite
  }
}
```

### GLM-5.1 Totals (April 15-16, 2026)
| Metric | Value |
|--------|-------|
| API Calls | 402 |
| Input | 587,724 |
| Output | 86,856 |
| **Billing** | **674,580** |
| Cache Read | 35,757,824 |

### Hourly Distribution
| Hour | Billing Tokens | % of Total |
|------|----------------|------------|
| Apr 15 15:00 | 57,976 | 8.6% |
| Apr 16 18:00 | 275,618 | 40.9% |
| Apr 16 19:00 | 193,772 | 28.7% |
| Apr 16 20:00 | 147,214 | 21.8% |

## Minitrace Validation

All scripts confirmed that go-minitrace conversion is **complete and accurate**:
- `usage.input_tokens` ✓
- `usage.output_tokens` ✓
- `usage.cache_read_tokens` ✓ (matches raw Pi exactly)
- `usage.cache_creation_tokens` ✓

## Commands to Reproduce

```bash
# Convert Pi sessions
go-minitrace convert pi --source-dir ~/.pi/agent/sessions/<session-dir> --output-dir /tmp/minitrace-analysis/pi-sessions

# Run validation scripts
python3 /tmp/extract_tokens_from_raw_pi.py
python3 /tmp/tokens_by_hour.py

# Extract turns for custom analysis
cat /tmp/minitrace-analysis/pi-sessions/active/2026-04/<session>.minitrace.json | \
  jq '[.turns[] | select(.model == "glm-5.1" and .usage != null)]' > /tmp/glm51_turns.json
```

## Investigation Timeline

1. **Phase 1:** Discovered Pi sessions from Apr 15-16
2. **Phase 2:** Converted to minitrace format
3. **Phase 3:** Initial token extraction (appeared low)
4. **Phase 4:** Cross-referenced with raw Pi JSONL (validation)
5. **Phase 5:** Discovered cache tokens in minitrace (complete picture)
6. **Phase 6:** Time-series analysis by hour

## Final Answer

**GLM-5.1 billing tokens (April 15-16, 2026): 674,580**
- Input: 587,724
- Output: 86,856
- Cache: 35,757,824 (typically free/discounted)
