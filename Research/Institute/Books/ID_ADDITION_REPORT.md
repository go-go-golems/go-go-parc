# ID Addition Report

> **Date:** 2026-04-10  
> **Task:** Programmatically add reMarkable IDs to all books in the library catalog  
> **Result:** ✅ All 90 books now have unique reMarkable IDs

---

## Methodology

### Data Sources

1. **Source Catalog:** `books.json` (90 programming books with titles, authors, paths)
2. **reMarkable Cloud:** Retrieved via `remarquee cloud ls --with-glaze-output --output json`
3. **Total Files Scanned:** 252 unique documents across multiple directories

### Directories Scanned

| Directory | Files Found |
|-----------|-------------|
| `/` (root) | 109 |
| `/Books` | 20 |
| `/Books/Software` | 49 |
| `/Books/AI` | 18 |
| `/Books/Technology` | 10 |
| `/Books/Mathematics` | 13 |
| `/Books/Software/Javascript` | 7 |
| `/Books/Software/Hypercard` | 11 |
| `/Books/Software/Lisp` | 15 |
| **Total Unique** | **252** |

---

## Matching Process

### Step 1: Title Normalization

Created a `normalize` function in `jq` to handle title variations:

```jq
def normalize:
  ascii_downcase |
  # Remove edition info
  gsub("\\s*\\(\\d+(?:nd|rd|th|st) edition\\s*\\)"; "") |
  # Handle C/C++ variations: CC++, C/C++, C C++
  gsub("c/c\\+\\+|cc\\+\\+|c\\s*c\\+\\+"; "ccpp") |
  # Handle C++ variations
  gsub("c\\+\\+"; "cpp") |
  # Remove all non-alphanumeric
  gsub("[^a-z0-9]"; "") |
  # Collapse spaces
  gsub("\\s+"; "")
;
```

### Step 2: Extract Clean Titles from reMarkable

reMarkable filenames include author and source information:
- Format: `Title (Author) (z-library.sk, 1lib.sk, z-lib.sk)`
- Or: `Title -- Author -- Publisher -- ISBN -- Anna's Archive`

Extracted just the title part (before ` (` or ` -- `) and normalized for matching.

### Step 3: Build Lookup Index

Created a JSON object mapping normalized titles to IDs:

```json
{
  "multiagentsystemsalgorithmicgametheoreticandlogicalfoundations": {
    "id": "f1aa0d8d-979b-4cb8-81aa-8f4dfca07445",
    "original_name": "Multiagent Systems Algorithmic..."
  },
  ...
}
```

### Step 4: Match Books

For each book in `books.json`:
1. Normalize its title
2. Look up in the reMarkable index
3. If found: add the `id` field
4. If not found: flag for manual mapping

---

## Results

### Match Statistics

| Method | Count | Percentage |
|--------|-------|------------|
| **Automatic (jq normalization)** | 77 | 85.6% |
| **Manual mappings** | 13 | 14.4% |
| **Failed** | 0 | 0% |
| **Total** | **90** | **100%** |

### Manual Mappings Required

These 13 books needed manual mappings due to significant title differences:

| Book Title | Why Manual? |
|------------|-------------|
| Mindstorms: Children, Computers... | File named "Papert Mindstorms" |
| Agile AI in Pharo | Underscores instead of spaces |
| Automated Planning | Missing colon in filename |
| Language Implementation Patterns | Extra subtitle in filename |
| Ted Nelson Autobiography | Missing colon |
| LISP Lore | Missing colon + extra text |
| Deep RL with Python | Edition info removal edge case |
| Designing Secure Software | Two versions (short/long) |
| Virtual Machine C/C++ | CC++ vs C/C++ normalization |
| Concepts and Semantics 2 | "2" vs "2nd Edition" |

### Matching Edge Cases Handled

| Issue | Example | Solution |
|-------|---------|----------|
| C/C++ variations | "CC++" vs "C/C++" | Unified to "ccpp" |
| Missing colons | "Automated Planning Theory..." | Manual mapping |
| Underscores | "Pharo_Implementing_Neural" | Included in normalization |
| Edition suffixes | "(2nd Edition)" | Stripped before matching |
| Author name in title | "Papert Mindstorms" | Manual mapping |
| Subtitle differences | Full vs abbreviated | Manual mapping |
| Duplicate files | 2 copies of same book | Used first occurrence |

---

## Validation

### Schema Verification

All 90 books now have complete records:

```json
{
  "has_title": true,    // 100%
  "has_author": true,   // 100%
  "has_id": true,       // 100% ✅
  "has_category": true  // 100%
}
```

### Sample Records

```json
{
  "title": "Multiagent Systems (2nd Edition)",
  "author": "Gerhard Weiss",
  "path": "/Books/AI",
  "category": "AI/Agents",
  "tags": ["multiagent systems", "distributed AI"],
  "id": "8ac30671-099a-4b93-960b-e80b3ab131d9"
}
```

```json
{
  "title": "Virtual Machine Design and Implementation in C/C++",
  "author": "Bill Blunden",
  "path": "/",
  "category": "Systems Programming",
  "tags": ["virtual machines", "C", "C++", "systems programming"],
  "id": "35b51e36-4058-489a-bac2-a8c4bfc8531a"
}
```

---

## Files Updated

| File | Change |
|------|--------|
| `books.json` | Added `id` field to all 90 book entries; updated metadata |

---

## How to Use the IDs

### Download a Specific Book

```bash
# Get ID from books.json
BOOK_ID=$(jq -r '.books[] | select(.title | test("Virtual Machine Design")) | .id' books.json)

# Download the book
remarquee cloud get "$BOOK_ID" --output book.rmdoc
```

### Batch Download by Category

```bash
# Download all Security books
jq -r '.books[] | select(.category == "Security") | .id' books.json | \
  while read id; do
    remarquee cloud get "$id" --output "$id.rmdoc"
  done
```

### Find Book by ID on Tablet

```bash
# List file details using ID
remarquee cloud stat <id>
```

---

## Scripts Used

### 1. Data Collection

```bash
#!/bin/bash
# collect_rm_data.sh

DIRS=("/" "/Books" "/Books/Software" "/Books/AI" "/Books/Technology" "/Books/Mathematics" "/Books/Software/Javascript" "/Books/Software/Hypercard" "/Books/Software/Lisp")

for dir in "${DIRS[@]}"; do
  safe_name=$(echo "$dir" | tr '/' '_')
  remarquee cloud ls "$dir" --with-glaze-output --output json 2>/dev/null | \
    jq '[.[] | select(.is_dir == false)]' > "rm${safe_name}.json"
done

# Merge and deduplicate
jq -s 'add | unique_by(.id)' rm*.json > rm_all.json
```

### 2. Matching Script

See: `/tmp/match_books_final.jq`

Key features:
- Title normalization for fuzzy matching
- Automatic index building
- Manual mapping overlay
- Match method tracking

### 3. Manual Mappings

See: `/tmp/manual_mappings_v2.json`

13 entries for edge cases that couldn't be matched automatically.

---

## Lessons Learned

1. **Structured data is essential:** `--with-glaze-output --output json` made this possible
2. **Normalization handles 85% of cases:** Simple text normalization solved most mismatches
3. **Manual intervention needed for edge cases:** ~15% needed human judgment
4. **File naming inconsistencies:** Anna's Archive vs Z-Library formats differ significantly
5. **ReMarkable truncates long filenames:** Some titles get abbreviated

---

## Maintenance

When adding new books:

1. Run the collection script to get latest reMarkable data
2. Run the matching script (should auto-match ~85%)
3. Review unmatched books and add manual mappings if needed
4. Validate all books have IDs before committing

---

## Conclusion

✅ **All 90 books in the library catalog now have their corresponding reMarkable IDs.**

This enables:
- Direct download of any book by ID
- Batch operations by category
- Syncing between catalog and tablet
- Verifying book presence on tablet
