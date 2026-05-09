# go-minitrace Investigation Diary: glm-5.1 Token Usage

**Investigation Goal:** Find token usage for the glm-5.1 model in yesterday and today's Pi sessions.

**Started:** 2026-04-16

---

## Phase 1: Discovery of Pi Sessions

First, I need to discover what Pi sessions exist from yesterday (2026-04-15) and today (2026-04-16). Pi sessions are stored under `~/.pi/agent/sessions/--slugged-cwd--/*.jsonl`.

Current working directory: `/home/manuel/code/wesen/corporate-headquarters/go-minitrace`

### Sessions Found (Apr 15 and 16, 2026):

**April 15, 2026 (Yesterday):**
- `--home-manuel-code-wesen-2026-04-15--8080-rom--` (11:44)
- `--home-manuel-code-wesen-corporate-headquarters-go-go-labs--` (20:29)
- `--home-manuel-code-wesen-corporate-headquarters-poll-modem--` (13:12)
- `--home-manuel-code-wesen-crib-k3s--` (21:35)
- `--home-manuel-code-wesen-obsidian-vault--` (18:23)
- `--home-manuel-code-wesen-obsidian-vault-Research-Institute-Research-2026-04-15-compiler-writing-hn--` (17:08)
- `--home-manuel-code-wesen-patreon-videos-003-rabbit-hole-out--` (12:40)
- `--home-manuel-workspaces-2026-04-15-x264-test-debug--` (15:03)
- `--home-manuel-workspaces-2026-04-15-x264-test-debug-2026-04-09--screencast-studio--` (04:08)

**April 16, 2026 (Today):**
- `--home-manuel-code-wesen-corporate-headquarters-go-minitrace--` (16:47) ← **Current session directory**
- `--home-manuel-workspaces-2026-04-10-pinocchiorc--` (14:17)

Let me list the actual session files in these directories.

### Session Files Found (Apr 15-16, 2026):

| Session Path | Size | Timestamp |
|-------------|------|-----------|
| go-minitrace: 2026-04-16T19-34-14-646Z | 1.9MB | Apr 16 16:47 |
| go-minitrace: 2026-04-16T20-44-41-256Z | 20KB | Apr 16 16:47 |
| go-go-labs: 2026-04-15T17-04-07-199Z | 5.3MB | Apr 15 22:43 |
| go-go-labs: 2026-04-16T00-29-23-851Z | 1.5KB | Apr 15 20:29 |
| 8080-rom: 2026-04-15T15-32-21-356Z | 532KB | Apr 15 11:40 |
| 8080-rom: 2026-04-15T15-44-38-065Z | 1.7MB | Apr 15 11:56 |
| obsidian-vault: 2026-04-15T22-23-37-308Z | 170KB | Apr 15 18:32 |
| obsidian-vault-research: 2026-04-15T21-07-45-789Z | 690KB | Apr 15 17:30 |
| x264-test-debug: 2026-04-15T08-07-51-757Z | 3.5MB | Apr 16 16:45 |
| crib-k3s: 2026-04-16T01-34-34-242Z | 3.5MB | Apr 16 16:25 |
| pinocchiorc: 2026-04-16T18-17-22-406Z | 292KB | Apr 16 14:34 |
| pinocchiorc: 2026-04-10T22-50-12-244Z | 12MB | Apr 16 16:47 |
| poll-modem: 2026-04-15T17-12-28-953Z | 5KB | Apr 15 13:12 |
| patreon-videos: 2026-04-15T16-39-10-540Z | 168KB | Apr 15 12:54 |

---

## Phase 2: Convert Pi Sessions to Minitrace Format

Now I'll convert all these Pi sessions to minitrace format using go-minitrace.

### Conversion Results:

Successfully converted 27 sessions to minitrace format in `/tmp/minitrace-analysis/pi-sessions/active/2026-04/`

**Key Sessions from Apr 15-16:**
| Session ID | Turn Count | Tool Call Count | Size |
|------------|------------|-----------------|------|
| 27ced5a6-cdda-4d81-b8fb-4653d092efa9 (go-minitrace, Apr 16) | 179 | 198 | 1.1MB |
| 045ccd1a-c605-4d4e-a531-956b32f35134 (go-minitrace, Apr 16) | 10 | 13 | 46KB |
| 3ee65b80-847e-4268-a479-47432e9594f4 (go-go-labs, Apr 15) | 1209 | 1216 | 4.3MB |
| e1d9f16f-d297-437c-890f-b4d6dbaa3b18 (go-go-labs, Apr 15) | 2 | 0 | 3.7KB |
| 2035dd97-cfb1-47ba-a90d-41096ae624d5 (crib-k3s, Apr 16) | 813 | 777 | 2.9MB |
| 07fe66a4-97ee-4b3a-a802-da3b615bc9f2 (pinocchiorc, Apr 16) | 60 | 61 | 307KB |
| cebcabb3-8bea-4587-b894-ddabdde34093 (8080-rom, Apr 15) | 29 | 29 | 294KB |
| d5862158-d05b-49ac-b6be-15e9795c1a67 (8080-rom, Apr 15) | 95 | 98 | 390KB |
| b07abedd-6d59-46e2-bd12-2ace7bde997d (obsidian-vault, Apr 15) | 26 | 17 | 118KB |
| 5ef65ebb-c16f-4e60-9a68-38cf1eaf6032 (obsidian-research, Apr 15) | 107 | 94 | 507KB |
| c75b8d1f-d98e-4440-aba1-7634afe6150f (poll-modem, Apr 15) | 5 | 2 | 9.6KB |
| 0d303aea-c087-49f3-bc04-d93406cca5c0 (patreon-videos, Apr 15) | 29 | 17 | 92KB |
| 372d3551-dc90-4ce1-8f61-89c59d959003 (x264-test, Apr 15) | 811 | 736 | 3.7MB |

Total: 27 sessions converted.

---

## Phase 3: Built-in go-minitrace Commands and Queries

Before diving into the glm-5.1 analysis, I discovered these built-in go-minitrace capabilities:

### Available Commands:
- **annotate** - Manage annotations on minitrace sessions
- **convert** - Convert native session stores (pi, codex) into minitrace
- **discover** - Inspect native session stores without converting
- **query** - Query converted archives (duckdb, commands)
- **serve** - Serve the minitrace transcript explorer API
- **validate** - Validate JSON files for minitrace processing

### Two Query Interfaces

go-minitrace provides **two** query interfaces:

**1. `query duckdb` - Ad-hoc SQL and Presets:**
| Preset | Description |
|--------|-------------|
| `session-list` | One row per session: id, framework, model, title, turns, tools, duration, etc. |
| `framework-summary` | Aggregate stats by agent framework |
| `tool-operation-breakdown` | Tool call counts grouped by framework and operation type |
| `timing-analysis` | Duration, active time, TTFA, idle ratio, min/max duration |
| `read-ratio-distribution` | Per-session breakdown of reads, modifies, creates, executes |
| `annotations` | All annotations unnested with session ID, annotator, category, etc. |

**2. `query commands` - Structured Repository-Backed Commands:**
| Preset | Description |
|--------|-------------|
| `session-list` | One row per session: id, framework, model, title, turns, tools, duration, etc. |
| `framework-summary` | Aggregate stats by agent framework |
| `tool-operation-breakdown` | Tool call counts grouped by framework and operation type |
| `timing-analysis` | Duration, active time, TTFA, idle ratio, min/max duration |
| `read-ratio-distribution` | Per-session breakdown of reads, modifies, creates, executes |
| `annotations` | All annotations unnested with session ID, annotator, category, etc. |

Structured commands are **sqleton-style** SQL files with YAML frontmatter that define:
- Command name and help text
- Typed flags (string, int, bool, choice, stringList, etc.)
- SQL templates with `{{TABLE_NAME}}` and `{{ .flag_name }}` variables

**Command Groups:**
| Group | Commands | Description |
|-------|----------|-------------|
| `overview` | `session-list`, `framework-summary`, `annotations`, `aliases` | Session overview queries |
| `files` | `file-operations`, `file-timeline` | File operation tracking |
| `tools` | `tool-operation-breakdown`, `tool-failures`, `read-ratio-distribution` | Tool analysis |
| `timing` | `timing-analysis` | Timing metrics |

**Aliases:** Commands can have `.alias.yaml` files that provide pre-filled defaults.

Let me run some of these commands:

**Structured Query Commands Results:**

```bash
# List all sessions with filtering
go-minitrace query commands overview session-list \
  --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json'

# Track file operations
go-minitrace query commands files file-operations \
  --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json' \
  --limit 20

# List tool failures
go-minitrace query commands tools tool-failures \
  --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json'
```

**Tool Failures Found:**
| Turn | Tool | Error Type | Example |
|------|------|------------|---------|
| 1 | read | EISDIR | "illegal operation on a directory, read" |
| 2 | bash | Command error | "failed to initialize workspace index" |
| 3 | bash | Unknown flag | "unknown flag: --stat" |
| 4 | bash | GitHub API | "diff exceeded the maximum number of lines" |
| 5 | bash | DuckDB error | "Referenced column not found" |
| 5 | bash | Git error | "not a git repository" |
| 6 | bash | Unknown option | "unknown option '--response-fields'" |
| 6 | read | ENOENT | "no such file or directory" |
| 7 | bash | Unknown flag | "unknown flag: --name" |
| 8 | read | ENOENT | "no such file or directory" |

---

## Phase 4: Query for glm-5.1 Model Token Usage

Now I need to query the minitrace archive to find all sessions that used the glm-5.1 model and get the token usage.

### Built-in Query Results

**Session List (glm-5.1 sessions):**
| Session ID | Date | Duration (s) | Turns | Tools | Title |
|------------|------|--------------|-------|-------|-------|
| fac4b2da-8e9a-4bc1-8041-cbcd37cfefde | 2026-04-06 | 991.3 | 40 | 47 | Analyze the Inbox and write up a document... |
| d5862158-d05b-49ac-b6be-15e9795c1a67 | 2026-04-15 | 695.2 | 95 | 98 | Use go-minitrace to analyze how we researched vt100... |
| 2035dd97-cfb1-47ba-a90d-41096ae624d5 | 2026-04-16 | 67854.7 | 813 | 777 | We are working with proxmox on root@pve, I want to setup jellyfin... |
| 07fe66a4-97ee-4b3a-a802-da3b615bc9f2 | 2026-04-16 | 1004.0 | 60 | 61 | Explain this PR to me: https://github.com/go-go-golems/geppetto... |

**Tool Operation Breakdown (All Pi Sessions):**
| Operation | Count |
|-----------|-------|
| EXECUTE | 3,628 |
| READ | 1,952 |
| NEW | 737 |
| MODIFY | 720 |
| OTHER | 104 |

**Timing Analysis:**
- Average session duration: 10.4 hours
- Average active time: 1.0 hour
- Average time to first action: 57.3 seconds
- Average idle ratio: 31%
- Min/Max duration: 1.3s / 141.9 hours

---

## Phase 5: Final glm-5.1 Token Usage Results

### Filtered for April 15-16, 2026 Only

After investigating the glm-5.1 sessions, I found that **only 3 sessions** were actually from yesterday (April 15) and today (April 16):

**Session 1: d5862158-d05b-49ac-b6be-15e9795c1a67 (8080-rom, Apr 15)**
- Turns: 95 (30 using glm-5.1, 56 using kimi-k2p5-turbo)
- Duration: 695.2 seconds (~11.6 minutes)
- **glm-5.1 Input Tokens: 52,692**
- **glm-5.1 Output Tokens: 5,284**
- Title: "Use go-minitrace to analyze how we researched the vt100 resources..."

**Session 2: 2035dd97-cfb1-47ba-a90d-41096ae624d5 (crib-k3s, Apr 16)**
- Turns: 813 (337 using glm-5.1, 397 using MiniMax-M2.7)
- Duration: 67,854.7 seconds (~18.8 hours)
- **glm-5.1 Input Tokens: 459,026**
- **glm-5.1 Output Tokens: 76,461**
- Title: "We are working with proxmox on root@pve, I want to setup jellyfin..."

**Session 3: 07fe66a4-97ee-4b3a-a802-da3b615bc9f2 (pinocchiorc, Apr 16)**
- Turns: 60 (35 using glm-5.1, 20 using kimi-k2p5-turbo)
- Duration: 1,004 seconds (~16.7 minutes)
- **glm-5.1 Input Tokens: 76,006**
- **glm-5.1 Output Tokens: 5,111**
- Title: "Explain this PR to me: https://github.com/go-go-golems/geppetto/pull/331..."

---

## FINAL ANSWER

### Total glm-5.1 Token Usage (April 15-16, 2026)

| Metric | Value | Notes |
|--------|-------|-------|
| **Sessions with glm-5.1** | 3 | Apr 15: 1 session, Apr 16: 2 sessions |
| **Total glm-5.1 API Calls** | 402 | Each turn with tool result = 1 call |
| **glm-5.1 Input Tokens** | **587,724** | New tokens sent to API |
| **glm-5.1 Output Tokens** | **86,856** | Generated tokens from API |
| **→ BILLING TOTAL** | **674,580** | input + output (what you pay for) |
| **glm-5.1 Cache Read** | 35,757,824 | Cached context (discounted/free) |
| **→ TOTAL PROCESSED** | 36,432,404 | input + output + cache |

**For cost purposes: 674,580 billing tokens** (the cache tokens are not billed at full rates).

**Validation:** Cross-referenced with raw Pi JSONL files - minitrace extraction was accurate.

---

## Cross-Reference Validation with Raw Pi JSONL

To verify the accuracy of the minitrace extraction, I cross-referenced the token counts with the **raw Pi session JSONL files** using a Python script.

### Python Validation Script Results:

| Session | Model | Calls | Input | Output | Billing (I+O) | Cache Read | Total (I+O+Cache) |
|---------|-------|-------|-------|--------|---------------|------------|-------------------|
| d5862158 (Apr 15) | glm-5.1 | 30 | 52,692 | 5,284 | **57,976** | 1,335,744 | 1,393,720 |
| 2035dd97 (Apr 16) | glm-5.1 | 337 | 459,026 | 76,461 | **535,487** | 32,505,408 | 33,040,895 |
| 07fe66a4 (Apr 16) | glm-5.1 | 35 | 76,006 | 5,111 | **81,117** | 1,916,672 | 1,997,789 |
| **TOTAL** | | **402** | **587,724** | **86,856** | **674,580** | **35,757,824** | **36,432,404** |

### Token Accounting Discovery:

The raw Pi JSONL shows the following usage structure:
```json
{
  "usage": {
    "input": 410,        // New tokens sent to API (BILLED)
    "output": 250,       // Generated tokens (BILLED)
    "cacheRead": 7680,   // Tokens read from cache (discounted)
    "cacheWrite": 0,     // Tokens written to cache
    "totalTokens": 8340  // input + output + cacheRead + cacheWrite
  }
}
```

**Key Finding:** The minitrace extraction was **CORRECT**. The minitrace format includes:
- `usage.input_tokens` ✓
- `usage.output_tokens` ✓
- `usage.cache_read_tokens` ✓ (matches raw Pi cacheRead exactly)
- `usage.cache_creation_tokens` ✓

The conversion properly maps Pi's `cacheRead` → `cache_read_tokens`. I just wasn't extracting them initially.

### Minitrace Cache Token Extraction:
```bash
# Cache tokens ARE in minitrace (verified matching raw Pi)
cat <session>.minitrace.json | jq '[.turns[] | select(.usage != null and .model == "glm-5.1") | .usage.cache_read_tokens] | add'
```

Results: **35,757,824 cache_read tokens** (exact match with raw Pi ✓)

**For cost analysis: 674,580 billing tokens** (587,724 input + 86,856 output).
Cache tokens (35M+) are typically billed at discounted rates.

---

## Data Quality Notes

1. **Model Routing**: The Pi system appears to use multiple models per session. The session environment shows "glm-5.1" but individual turns may be routed to other models like `kimi-k2p5-turbo` or `MiniMax-M2.7`.

2. **Session fac4b2da** (April 6, 2026): This session had glm-5.1 in its environment but was from April 6, not April 15-16. It used 35 glm-5.1 turns with 108,882 input tokens and 15,151 output tokens. **This session was excluded from the April 15-16 totals.**

3. **Mixed Model Usage**: 
   - Session d5862158: 30 glm-5.1 turns + 56 kimi-k2p5-turbo turns
   - Session 2035dd97: 337 glm-5.1 turns + 397 MiniMax-M2.7 turns
   - Session 07fe66a4: 35 glm-5.1 turns + 20 kimi-k2p5-turbo turns

---

## Commands Used

```bash
# Convert Pi sessions
go-minitrace convert pi --source-dir ~/.pi/agent/sessions/<session-dir> --output-dir /tmp/minitrace-analysis/pi-sessions

# ============================================
# query duckdb - Ad-hoc SQL and Presets
# ============================================

# Built-in presets
go-minitrace query duckdb --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json' --preset session-list
go-minitrace query duckdb --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json' --preset framework-summary
go-minitrace query duckdb --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json' --preset tool-operation-breakdown
go-minitrace query duckdb --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json' --preset timing-analysis
go-minitrace query duckdb --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json' --preset read-ratio-distribution
go-minitrace query duckdb --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json' --preset annotations

# Custom SQL
go-minitrace query duckdb --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json' --sql "
  SELECT environment->>'model' AS model, COUNT(*) AS sessions
  FROM sessions_base GROUP BY model ORDER BY sessions DESC
"

# SQL from file
go-minitrace query duckdb --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json' --sql-file ./my-query.sql

# ============================================
# query commands - Structured Repository Commands
# ============================================

# Overview commands
go-minitrace query commands overview session-list --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json'
go-minitrace query commands overview framework-summary --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json'
go-minitrace query commands overview annotations --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json'

# Files commands
go-minitrace query commands files file-operations --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json' --limit 50
go-minitrace query commands files file-timeline --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json' --path-pattern "*.go"

# Tools commands
go-minitrace query commands tools tool-operation-breakdown --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json'
go-minitrace query commands tools tool-failures --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json'
go-minitrace query commands tools read-ratio-distribution --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json'

# Timing commands
go-minitrace query commands timing timing-analysis --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json'

# Using aliases
go-minitrace query commands overview aliases codex-framework-summary --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json'

# With custom query repositories
go-minitrace query commands overview session-list \
  --query-repository ./my-query-commands \
  --archive-glob '/tmp/minitrace-analysis/pi-sessions/active/*/*.minitrace.json'

# ============================================
# Direct JSON analysis with jq
# ============================================

# Extract token data from minitrace JSON for specific model
cat <session>.minitrace.json | jq '[.turns[] | select(.usage != null and .model == "glm-5.1") | .usage.input_tokens] | add'

# Get all models used in a session
cat <session>.minitrace.json | jq '[.turns[] | select(.usage != null) | .model] | unique'

# Get model distribution across turns
cat <session>.minitrace.json | jq '[.turns[] | select(.usage != null) | .model] | group_by(.) | map({model: .[0], count: length})'
```

---

**Investigation Complete** ✅

**Total glm-5.1 tokens used in April 15-16, 2026 Pi sessions: 674,580 tokens** (587,724 input + 86,856 output)

---

## Token Accounting Reference

For detailed explanation of token types, see: **`/tmp/token_accounting_explained.md`**

### Quick Reference:

| Token Type | Count | What It Means | Billed? |
|------------|-------|---------------|---------|
| **Input** | 587,724 | New tokens sent TO API | ✅ YES |
| **Output** | 86,856 | Tokens generated BY API | ✅ YES |
| **Billing** | 674,580 | **Input + Output** (cost) | = Cost |
| **Cache Read** | 35,757,824 | Reused context | ⚠️ Discounted |
| **Total Processed** | 36,432,404 | Input + Output + Cache | ≠ Cost |

**Why cache is huge:** 35M cache tokens means Pi efficiently reused conversation context across 402 API calls. Each call only sent ~1,460 new input tokens on average, but had access to all previous context via cache.

**Cost estimate:** ~$0.50-2.00 (not $35+ because cache is cheap/free)

---

## Hourly Token Breakdown - All Types

Generated by: `python3 /tmp/tokens_by_hour_complete.py`

### Complete Hourly Table:

| Hour | Calls | Input | Output | Cached | Total | Billing |
|------|-------|-------|--------|--------|-------|---------|
| 2026-04-15 15:00 | 30 | 52,692 | 5,284 | 1,335,744 | 1,393,720 | 57,976 |
| 2026-04-16 18:00 | 144 | 246,209 | 29,409 | 12,052,096 | 12,327,714 | 275,618 |
| 2026-04-16 19:00 | 103 | 164,858 | 28,914 | 13,881,472 | 14,075,244 | 193,772 |
| 2026-04-16 20:00 | 125 | 123,965 | 23,249 | 8,488,512 | 8,635,726 | 147,214 |
| **TOTAL** | **402** | **587,724** | **86,856** | **35,757,824** | **36,432,404** | **674,580** |

### What Each Column Means:

| Column | Definition | Used For |
|--------|------------|----------|
| **Input** | New tokens sent to API | Cost calculation |
| **Output** | Tokens generated by AI | Cost calculation |
| **Cached** | Reused context from previous turns | Efficiency metric |
| **Total** | Input + Output + Cached | Total processing load |
| **Billing** | Input + Output | **Actual cost** |

**Why cache is 98% of tokens:** Pi (the AI system) caches conversation context across API calls. Each new turn only sends small "input" (1,460 tokens avg), but the AI can "see" all previous context through the cache (35M tokens). This makes:
- API calls faster (no need to re-process full context)
- Cheaper (cache tokens are discounted/free vs sending full context each time)

### Hourly Distribution (% of Billing):

```
Hour              Billing    % of Total    Visual
─────────────────────────────────────────────────
Apr 15 15:00       57,976         8.6%    ████
Apr 16 18:00      275,618        40.9%    ████████████████████
Apr 16 19:00      193,772        28.7%    ██████████████
Apr 16 20:00      147,214        21.8%    ██████████
```

