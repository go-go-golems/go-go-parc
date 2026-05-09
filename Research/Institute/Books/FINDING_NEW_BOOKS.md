# Efficiently Finding New Books on the Tablet

> **Purpose:** Strategies for detecting and cataloging new additions to the reMarkable programming book collection  
> **Last Updated:** 2026-04-10

---

## Overview

The reMarkable tablet accumulates documents from multiple sources:
- Direct uploads via remarquee/rmapi
- Web articles saved via browser extensions
- AI-generated research documents (in `/ai/`)
- Project work products (in `/Projects/`)
- Manual uploads of PDFs and EPUBs

**Goal:** Distinguish new *books* (published, comprehensive technical works) from ephemeral content (articles, notes, generated docs).

---

## Strategy 1: Timestamp-Based Detection (Recommended)

### Approach
Use the `modified_client` field from structured JSON output to find recently added files.

### Basic Usage

```bash
# Get all files sorted by modification time (newest first)
remarquee cloud find / --with-glaze-output --output json 2>&1 | \
  jq '[.[] | select(.is_dir == false)] | sort_by(.modified_client) | reverse | .[:20]' | \
  jq '.[] | {title: .name, path: .path, modified: .modified_client}'
```

### Find Books Added Since Specific Date

```bash
#!/bin/bash
# find_new_since_date.sh

CUTOFF_DATE="2026-03-01T00:00:00Z"  # Set to last check date

echo "=== BOOKS ADDED SINCE $CUTOFF_DATE ==="

remarquee cloud find / --with-glaze-output --output json 2>&1 | \
  jq --arg cutoff "$CUTOFF_DATE" '
    [.[] | select(.is_dir == false) | 
     select(.modified_client > $cutoff) |
     select(
       .name | test("z-library|Anna.s Archive|Springer|O.Reilly|Manning|Addison-Wesley|Prentice|No Starch|Apress|Packt|Wiley|programming|software|code|compiler|operating"; "i")
     ) |
     {title: .name, path: .path, modified: .modified_client, id: .id}
    ]'
```

### Weekly Automation Script

```bash
#!/bin/bash
# weekly_book_check.sh

BASELINE_FILE=".last_check_date"
CANDIDATES_FILE="new_candidates_$(date +%Y%m%d).json"

# Determine cutoff date
if [ -f "$BASELINE_FILE" ]; then
  CUTOFF=$(cat "$BASELINE_FILE")
else
  # Default: 7 days ago
  CUTOFF=$(date -u -d '7 days ago' '+%Y-%m-%dT%H:%M:%SZ')
fi

echo "Checking for books since: $CUTOFF"

# Query and filter
remarquee cloud find / --with-glaze-output --output json 2>&1 | \
  jq --arg cutoff "$CUTOFF" \
     --arg book_pattern "z-library|Anna.s Archive|Springer|O.Reilly|Manning|Addison-Wesley|Prentice|programming|software|code|compiler|operating|algorithm|language|lisp|prolog|javascript|python|java" \
     --arg exclude_pattern "/ai/|/trash/|/Deep Researches/|/Projects/|/Articles/|/Notes/" '
    [.[] | select(.is_dir == false) |
     select(.modified_client > $cutoff) |
     select(.path | test($exclude_pattern; "i") | not) |
     select(.name | test($book_pattern; "i")) |
     {id: .id, title: .name, path: .path, modified: .modified_client}
    ]' > "$CANDIDATES_FILE"

COUNT=$(jq 'length' "$CANDIDATES_FILE")
echo "Found $COUNT new candidate(s)"

if [ "$COUNT" -gt 0 ]; then
  echo ""
  echo "=== New Candidates ==="
  jq '.[] | "\(.modified): \(.title)"' -r "$CANDIDATES_FILE"
fi

# Update baseline date
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$BASELINE_FILE"
```

---

## Strategy 2: Directory Monitoring with Structured Output

### High-Yield Directories to Monitor

| Priority | Directory | Rationale |
|----------|-----------|-----------|
| 🔴 High | `/` (root) | New uploads often land here initially |
| 🔴 High | `/Books/` | Explicit book storage location |
| 🔴 High | `/Books/Software/` | Programming book subcategory |
| 🔴 High | `/Books/AI/` | AI/ML book subcategory |
| 🟡 Medium | `/Books/Mathematics/` | Technical reference books |
| 🟡 Medium | `/Books/Technology/` | Computing history and tech books |
| 🟢 Low | `/Articles/` | Usually web articles, not books |
| 🟢 Low | `/Projects/` | Project work, not published books |

### Monitoring Commands (JSON)

**Check root for new items (sorted by date):**

```bash
remarquee cloud ls / --with-glaze-output --output json 2>&1 | \
  jq '[.[] | select(.is_dir == false)] | sort_by(.modified_client) | reverse | .[:10]' | \
  jq '.[] | "\(.modified_client) | \(.name)"' -r
```

**Deep check /Books directory with timestamps:**

```bash
remarquee cloud find /Books --with-glaze-output --output json 2>&1 | \
  jq '[.[] | select(.is_dir == false)] | sort_by(.modified_client) | reverse | .[] | 
      "\(.modified_client) | \(.path)"' -r
```

---

## Strategy 3: Source-Based Detection (Structured)

### Recognize Book Sources

New books will have these telltale markers in their names:

| Source | Pattern | jq Regex |
|--------|---------|----------|
| Z-Library | `(z-library.sk, 1lib.sk, z-lib.sk)` | `z-library` |
| Anna's Archive | `-- Anna's Archive` | `Anna.s Archive` |
| Academic Publishers | `Springer`, `Cambridge`, `MIT Press` | `Springer\|Cambridge` |
| Technical Publishers | `O'Reilly`, `Manning`, `No Starch` | `O.Reilly\|Manning` |

**Search for any new entries with these markers:**

```bash
remarquee cloud find / --with-glaze-output --output json 2>&1 | \
  jq '[.[] | select(.is_dir == false) | select(
    .name | test("z-library|Anna.s Archive|Springer|O.Reilly|Manning|Addison-Wesley|Prentice|No Starch|Apress|Packt|Wiley|Cambridge|MIT Press"; "i")
  ) | {title: .name, path: .path, modified: .modified_client, id: .id}]'
```

---

## Strategy 4: Pattern-Based Discovery

### Programming Book Keywords

Search for new files containing these high-confidence programming terms:

```bash
KEYWORDS="programming|software|code|compiler|operating system|distributed|language|algorithm|data structure|lisp|prolog|javascript|python|java|c\\+\\+|rust|zig|kernel|architecture|design patterns|functional|object-oriented|type theory|virtual machine|abstract machine"

remarquee cloud find / --with-glaze-output --output json 2>&1 | \
  jq --arg pattern "$KEYWORDS" '
    [.[] | select(.is_dir == false) |
     select(.path | test("/ai/|/trash/|/Deep Researches/|/Projects/|/Articles/|/Notes/"; "i") | not) |
     select(.name | test($pattern; "i")) |
     {title: .name, path: .path, modified: .modified_client, id: .id}
    ]'
```

---

## Strategy 5: Size/Scope Heuristics with JSON

### Score-Based Filtering

Assign confidence scores using jq:

```bash
remarquee cloud find / --with-glaze-output --output json 2>&1 | \
  jq '[.[] | select(.is_dir == false) |
    select(.path | test("/ai/|/trash/|/Deep Researches/"; "i") | not) |
    {
      title: .name,
      path: .path,
      modified: .modified_client,
      id: .id,
      score: (
        (if .name | test("z-library|Anna.s Archive"; "i") then 3 else 0 end) +
        (if .name | test("Springer|O.Reilly|Manning|Addison-Wesley"; "i") then 3 else 0 end) +
        (if .path | test("/Books/"; "i") then 2 else 0 end) +
        (if .name | test("programming|software|code|compiler|operating"; "i") then 2 else 0 end) +
        (if .name | test("algorithm|language|lisp|prolog|javascript|python"; "i") then 1 else 0 end)
      )
    } | select(.score >= 3)
  ] | sort_by(.score) | reverse'
```

---

## Recommended Maintenance Workflow

### Weekly Quick Check (5 minutes)

```bash
#!/bin/bash
# weekly_quick_check.sh

# Get 10 most recently modified non-dir items everywhere
remarquee cloud find / --with-glaze-output --output json 2>&1 | \
  jq '[.[] | select(.is_dir == false)] | sort_by(.modified_client) | reverse | .[:10]' | \
  jq '.[] | "\(.modified_client) | \(.path)"' -r
```

### Monthly Deep Scan (30 minutes)

1. **Generate current catalog with structured output:**
   ```bash
   remarquee cloud find / --with-glaze-output --output json 2>&1 | \
     jq '[.[] | select(.is_dir == false)]' > current_catalog.json
   ```

2. **Compare with master list using IDs:**
   ```bash
   # Extract IDs from current catalog
   jq '[.[] | .id]' current_catalog.json | sort > current_ids.json
   
   # Extract IDs from master catalog
   jq '[.books[].id? // empty]' books.json | sort > master_ids.json
   
   # Find new IDs
   comm -13 <(jq -r '.[]' master_ids.json | sort) <(jq -r '.[]' current_ids.json | sort)
   ```

3. **Review candidates:**
   - Check each new entry against book criteria
   - Add valid books to master catalog
   - Update metadata (export date, total count)

---

## Semi-Automated New Book Detection

### One-Liner for Weekly Use

```bash
CUTOFF=$(date -u -d '7 days ago' '+%Y-%m-%dT%H:%M:%SZ')

remarquee cloud find / --with-glaze-output --output json 2>&1 | \
  jq --arg cutoff "$CUTOFF" \
     --arg exclude "/ai/|/trash/|/Deep Researches/|/Projects/|/Articles/" '
    [.[] | select(.is_dir == false) |
     select(.modified_client > $cutoff) |
     select(.path | test($exclude; "i") | not) |
     select(.name | test("z-library|Anna.s Archive|Springer|O.Reilly|Manning|programming|software|code|compiler"; "i")) |
     {title: .name, path: .path, modified: .modified_client, id: .id}
    ]' > candidates_$(date +%Y%m%d).json && \
  echo "Found $(jq 'length' candidates_$(date +%Y%m%d).json) new candidate(s)"
```

### Review New Candidates Against Master

```bash
#!/bin/bash
# find_truly_new.sh

CANDIDATES="candidates_$(date +%Y%m%d).json"
MASTER="books.json"

# Get candidate IDs
cat "$CANDIDATES" | jq -r '.[].id' | sort > candidate_ids.txt

# Get master IDs (handle both id field and books without id)
cat "$MASTER" | jq -r '.books[] | (.id // (.title + .author))' 2>/dev/null | sort > master_ids.txt

# Show candidates not in master
echo "=== NEW BOOKS NOT IN MASTER CATALOG ==="
cat "$CANDIDATES" | jq --argfile master <(cat master_ids.txt | jq -R . | jq -s .) '
  [.[] | select(.id as $id | $master | index($id) | not)]'
```

---

## Red Flags (Likely Not Books)

Exclude entries matching these patterns:

| Pattern | Example | jq Exclude |
|---------|---------|------------|
| `/ai/` paths | `/ai/2026/03/20/TICKET-001/report` | `test("/ai/"; "i")` |
| Date prefixes | `2026-01-15 meeting notes` | `test("^\\d{4}-\\d{2}-\\d{2}"; "i")` |
| `Notebook` | `Notebook 5`, `Notebook 7` | `test("Notebook"; "i")` |
| `Draft` | `Draft article v2` | `test("Draft"; "i")` |
| `tmp-` | `tmp-remarquee/` | `test("tmp-"; "i")` |
| Short cryptic names | `doc1`, `file2` | `(.name \| length) < 20` |

**Complete exclusion filter:**

```bash
EXCLUDE_PATTERN="/ai/|/trash/|/Deep Researches/|/Projects/|/Articles/|/Notes/|tmp-|Draft"
NAME_EXCLUDE="^\\d{4}-\\d{2}-\\d{2}|Notebook|doc[0-9]+|file[0-9]+"

remarquee cloud find / --with-glaze-output --output json 2>&1 | \
  jq --arg path_exclude "$EXCLUDE_PATTERN" \
     --arg name_exclude "$NAME_EXCLUDE" '
    [.[] | select(.is_dir == false) |
     select(.path | test($path_exclude; "i") | not) |
     select(.name | test($name_exclude; "i") | not)
    ]'
```

---

## Integration with Library Index Project

### When New Books Are Found

1. **Add to JSON catalog:**
   ```bash
   # Extract candidate and format for catalog
   jq '.[] | {
     id: .id,
     title: (.name | sub(" \\([^)]*\\)$"; "") | sub(" -- .*$"; "")),
     author: (.name | capture("\\(([^)]+)\\)").1 // "Unknown"),
     path: .path,
     category: "TBD",
     tags: [],
     modified_client: .modified_client,
     summary_pending: true
   }' candidates_$(date +%Y%m%d).json
   ```

2. **Flag for summary writing:**
   - Mark status: `"summary_pending": true`
   - Assign to reviewer
   - Schedule for next summary batch

3. **Update statistics:**
   - Increment `total_books` in metadata
   - Add new category if needed
   - Update `exported_at` timestamp

---

## Quick Reference: Is It a Book?

| ✅ Likely Book | ❌ Likely Not a Book |
|---------------|---------------------|
| Has author in parentheses | No author attribution |
| Publisher/source marker | Just a title |
| Located in `/Books/` | Located in `/ai/`, `/Articles/` |
| Comprehensive title | Single topic, blog-like |
| Technical depth indicator | Surface-level, news-like |
| Classic CS subject matter | Current events, trends |
| Long, descriptive filename | Short, abbreviated |

### jq Scoring Formula

```bash
score = 0
if name matches "z-library|Anna's Archive" → +3
if name matches "Springer|O'Reilly|Manning|Addison-Wesley" → +3
if path matches "/Books/" → +2
if name matches "programming|software|code|compiler|operating" → +2
if name matches "algorithm|language|lisp|prolog|javascript|python" → +1

if score >= 3 → likely a book
```

---

## Automation Ideas

### Future Enhancements

1. **Metadata extraction:** Download sample pages via `remarquee cloud get <id>` and OCR/extract metadata
2. **Duplicate detection:** Hash-based duplicate identification using IDs
3. **Auto-categorization:** ML-based classification from title + tags
4. **API integration:** Query OpenLibrary/Google Books using extracted ISBN
5. **Change monitoring:** Cron job to email weekly new book candidates with timestamps

### Sample Cron Setup

```bash
# Add to crontab: Weekly check every Monday at 9am
0 9 * * 1 /path/to/weekly_book_check.sh >> /var/log/remarquee_books.log 2>&1
```

---

## Summary: Most Efficient Approach

**Weekly (2 minutes):**
```bash
# Timestamp-based detection
CUTOFF=$(date -u -d '7 days ago' '+%Y-%m-%dT%H:%M:%SZ')
remarquee cloud find / --with-glaze-output --output json 2>&1 | \
  jq --arg c "$CUTOFF" '[.[] | select(.is_dir==false and .modified_client > $c) | select(.name|test("z-library|Anna.s Archive|Springer|O.Reilly"; "i"))]'
```

**Monthly (15 minutes):**
1. Export full catalog with `--with-glaze-output`
2. Diff against previous export using `id` and `modified_client`
3. Review and integrate new books

**Key Advantage:** The `modified_client` timestamp eliminates false positives from reorganized files—only truly new uploads appear.
