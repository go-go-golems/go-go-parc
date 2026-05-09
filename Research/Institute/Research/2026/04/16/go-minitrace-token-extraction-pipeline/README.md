# go-minitrace Token Extraction Pipeline

A complete pipeline for extracting token usage and billing information from AI agent transcripts using go-minitrace.

## Quick Start

```bash
# View the project report
cat PROJECT_REPORT.md | less

# Run the complete hourly analysis
python3 scripts/05_tokens_by_hour_complete.py

# Read token accounting guide
cat diary/token_accounting_explained.md
```

## What's in This Project

This project demonstrates how to:
1. Convert Pi agent session logs to minitrace format
2. Query and extract token usage data
3. Validate accuracy against raw JSONL files
4. Build time-series analysis of billing tokens

## Directory Structure

```
├── PROJECT_REPORT.md          # Complete project documentation
├── README.md                  # This file
├── diary/                     # Investigation logs
│   ├── 00_investigation_diary.md
│   ├── token_accounting_explained.md
│   └── SCRIPT_README.md
├── scripts/                   # Python extraction pipeline (v1-v5)
│   ├── 01_extract_tokens_v1.py
│   ├── 02_extract_tokens_v2_billing.py
│   ├── 03_extract_tokens_validation.py
│   ├── 04_tokens_by_hour_basic.py
│   └── 05_tokens_by_hour_complete.py
├── queries/                   # DuckDB query reference
│   └── README.md
└── data/                      # Extracted datasets
    └── glm51_turns_dataset.json
```

## Key Results

**GLM-5.1 Token Usage (April 15-16, 2026):**

| Metric | Count |
|--------|-------|
| API Calls | 402 |
| Input Tokens | 587,724 |
| Output Tokens | 86,856 |
| **Billing Tokens** | **674,580** |
| Cache Tokens | 35,757,824 |

**Peak Hour:** Apr 16 18:00 - 275,618 billing tokens (40.9% of total)

## Pipeline Workflow

```
Raw Pi JSONL → go-minitrace convert → DuckDB query → Python/jq analysis → Hourly breakdown
```

## Documentation

- **[PROJECT_REPORT.md](PROJECT_REPORT.md)** - Full project report with architecture, insights, and lessons learned
- **[diary/token_accounting_explained.md](token_accounting_explained.md)** - What each token type means (input, output, cached, billing)
- **[diary/SCRIPT_README.md](SCRIPT_README.md)** - Script documentation and usage examples
- **[queries/README.md](Research/Institute/Research/2026/04/16/go-minitrace-token-extraction-pipeline/queries/README.md)** - DuckDB query reference

## Example Output

```
====================================================================================================
COMPLETE HOURLY BREAKDOWN - ALL TOKEN TYPES
====================================================================================================

Hour                 Calls      Input     Output       Cached        Total    Billing
------------------------------------------------------------------------------------------------------------------------
2026-04-15 15:00        30     52,692      5,284    1,335,744    1,393,720     57,976
2026-04-16 18:00       144    246,209     29,409   12,052,096   12,327,714    275,618
2026-04-16 19:00       103    164,858     28,914   13,881,472   14,075,244    193,772
2026-04-16 20:00       125    123,965     23,249    8,488,512    8,635,726    147,214
------------------------------------------------------------------------------------------------------------------------
TOTAL                  402    587,724     86,856   35,757,824   36,432,404    674,580
```

## Key Insight

**Cache tokens are 98% of total but NOT 98% of cost.**

- Cache tokens (35M) are reused conversation context
- They're billed at heavily discounted rates or free
- Actual cost is based on **Billing** = Input + Output (674,580 tokens)
- Estimated cost: ~$0.50-2.00 (not $35+)

## Tools Used

- **go-minitrace** - Convert and query transcript archives
- **DuckDB** - SQL analytics engine
- **Python** - Data extraction and aggregation
- **jq** - JSON processing

## Date

2026-04-16
