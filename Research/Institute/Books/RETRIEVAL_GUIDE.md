# ReMarkable Book Retrieval Guide

> **Institute:** Research Institute  
> **Purpose:** Library index maintenance for programming/computer science collection  
> **Last Updated:** 2026-04-10

---

## Overview

This document describes how to extract a catalog of programming and computer science books from the reMarkable tablet using the `remarquee` CLI tool with structured JSON/YAML output.

---

## Prerequisites

- `remarquee` CLI tool installed and configured
- Valid reMarkable cloud credentials (via rmapi)
- Network access to reMarkable cloud services
- `jq` tool for JSON processing (recommended)

```bash
# Install jq if not present
sudo apt-get install jq  # Ubuntu/Debian
brew install jq          # macOS
```

---

## Structured Output (Recommended)

Use `--with-glaze-output --output json` (or `yaml`) to get machine-parseable data with timestamps:

```bash
remarquee cloud ls / --with-glaze-output --output json
```

### JSON Output Schema

Each entry includes:

```json
{
  "id": "uuid-string",
  "is_dir": false,
  "modified_client": "2026-04-10T08:30:00Z",
  "modified_time": "2026-04-10T08:30:00Z",
  "name": "Book Title (Author) (z-library.sk, 1lib.sk, z-lib.sk)",
  "parent_id": "parent-uuid",
  "path": "/Books/Category/Book Title",
  "type": "DocumentType",
  "version": 0
}
```

| Field | Use For |
|-------|---------|
| `id` | Unique reference, downloading files |
| `is_dir` | Filter files (`false`) vs directories (`true`) |
| `modified_client` / `modified_time` | Detecting new additions |
| `name` | Title extraction, author parsing |
| `path` | Location, categorization |
| `type` | `DocumentType` = file, `CollectionType` = folder |

---

## Step-by-Step Retrieval Process

### Step 1: Verify Cloud Connection

Test that remarquee can connect to your reMarkable cloud account:

```bash
remarquee cloud account
```

Expected output: Account information showing your reMarkable user ID.

---

### Step 2: List All Documents (Structured)

Get all files at the root with full metadata:

```bash
remarquee cloud ls / --with-glaze-output --output json 2>&1 | \
  jq '.[] | select(.is_dir == false) | {name: .name, path: .path, modified: .modified_client}'
```

---

### Step 3: Filter for Books Using jq

Programming books on the tablet typically have these indicators:

| Indicator | Example Pattern |
|-----------|-----------------|
| Z-Library | `(z-library.sk, 1lib.sk, z-lib.sk)` |
| Anna's Archive | `-- Anna's Archive` |
| Publisher names | `Springer`, `O'Reilly`, `Manning`, `Addison-Wesley` |

**Filter for books with publisher/source markers:**

```bash
remarquee cloud ls / --with-glaze-output --output json 2>&1 | \
  jq '.[] | select(.is_dir == false) | select(
    .name | test("z-library|Anna.s Archive|Springer|O.Reilly|Manning|Addison-Wesley|Prentice|No Starch|Apress|Packt|Wiley"; "i")
  ) | {title: .name, path: .path, id: .id, modified: .modified_client}'
```

---

### Step 4: Exclude Non-Book Content

Filter out directories containing generated content:

| Directory | Contents | Exclude Pattern |
|-----------|----------|-----------------|
| `/ai/` | AI-generated research | `.path \| test("/ai/"; "i")` |
| `/trash/` | Deleted items | `.path \| test("/trash/"; "i")` |
| `/Deep Researches/` | Research digests | `.path \| test("/Deep Researches/"; "i")` |
| `/Projects/` | Project documents | `.path \| test("/Projects/"; "i")` |
| `/Articles/` | Web articles | `.path \| test("/Articles/"; "i")` |
| `/Notes/` | Personal notes | `.path \| test("/Notes/"; "i")` |

**Full exclusion pattern with jq:**

```bash
remarquee cloud ls / --with-glaze-output --output json 2>&1 | \
  jq '.[] | select(.is_dir == false) | select(
    (.path | test("/ai/|/trash/|/Deep Researches/|/Projects/|/Articles/|/Notes/"; "i") | not)
  ) | select(
    .name | test("z-library|Anna.s Archive|Springer|O.Reilly|Manning"; "i")
  ) | {title: .name, path: .path, modified: .modified_client}'
```

---

### Step 5: Search by Category

**Search the `/Books` directory specifically:**

```bash
remarquee cloud ls /Books --with-glaze-output --output json 2>&1 | \
  jq '.[] | select(.is_dir == false) | {title: .name, path: .path, modified: .modified_client}'
```

**Deep search all subdirectories:**

```bash
remarquee cloud find /Books --with-glaze-output --output json 2>&1 | \
  jq '.[] | select(.is_dir == false) | {title: .name, path: .path, modified: .modified_client}'
```

---

## Complete Retrieval Script

```bash
#!/bin/bash
# retrieve_books_structured.sh - Extract programming books using JSON output

OUTPUT_FILE="books_$(date +%Y%m%d).json"

# Get all files, filter for books using structured data
remarquee cloud find / --with-glaze-output --output json 2>&1 | \
  jq '[.[] | select(.is_dir == false) | select(
    (.path | test("/ai/|/trash/|/Deep Researches/|/Projects/|/Articles/|/Notes/"; "i") | not)
  ) | select(
    .name | test("z-library|Anna.s Archive|Springer|O.Reilly|Manning|Addison-Wesley|Prentice|No Starch|Apress|Packt|Wiley|programming|software|code|compiler|operating|algorithm|language|lisp|prolog|javascript|python|java|c\\+\\+"; "i")
  ) | {id: .id, title: .name, path: .path, modified: .modified_client}]' \
  > "$OUTPUT_FILE"

echo "Found $(jq 'length' "$OUTPUT_FILE") potential books"
echo "Saved to: $OUTPUT_FILE"

# Pretty print first 5 entries
echo ""
echo "=== Sample entries ==="
jq '.[:5]' "$OUTPUT_FILE"
```

---

## JSON Schema for Book Entries

Each book entry in the catalog follows this structure:

```json
{
  "id": "uuid-for-download",
  "title": "Book Title",
  "author": "Author Name(s)",
  "path": "/Books/Category",
  "category": "Subject Category",
  "tags": ["keyword1", "keyword2", "keyword3"],
  "modified_client": "2026-04-10T08:30:00Z"
}
```

---

## Finding Recently Added Books (Timestamp Method)

The structured output includes `modified_client` timestamps, perfect for finding new additions:

```bash
#!/bin/bash
# find_new_books_by_date.sh

CUTOFF_DATE="2026-03-01T00:00:00Z"  # Adjust to your last check date

remarquee cloud find / --with-glaze-output --output json 2>&1 | \
  jq --arg cutoff "$CUTOFF_DATE" '
    [.[] | select(.is_dir == false) | select(.modified_client > $cutoff) | select(
      .name | test("z-library|Anna.s Archive|Springer|O.Reilly|Manning"; "i")
    ) | {title: .name, path: .path, modified: .modified_client}]'
```

---

## File Locations

| File | Purpose |
|------|---------|
| `books.json` | Master catalog with metadata |
| `RETRIEVAL_GUIDE.md` | This documentation |

---

## Downloading Books by ID

Once you have a book's `id` from the structured output, you can download it:

```bash
# Download a specific book by ID (get the .rmdoc archive)
remarquee cloud get <uuid> --output book.rmdoc

# Example using jq to extract first book ID and download
BOOK_ID=$(remarquee cloud ls /Books --with-glaze-output --output json 2>&1 | \
  jq -r '.[] | select(.is_dir == false) | .id' | head -1)

remarquee cloud get "$BOOK_ID" --output first_book.rmdoc
```

---

## Troubleshooting

### Authentication Issues

If you see authentication errors:
```bash
remarquee cloud ls / --reauth
```

This forces re-authentication with the reMarkable cloud.

### JSON Parsing Errors

If jq reports invalid JSON:
```bash
# Verify raw output first
remarquee cloud ls / --with-glaze-output --output json 2>&1 | head -c 500

# Check for error messages mixed with JSON
remarquee cloud ls / --with-glaze-output --output json 2>/dev/null | jq '.'
```

### Missing Books

If books you know exist don't appear:
1. Check if they're in `/trash/` (deleted but not purged)
2. Verify `is_dir` is `false` (not a directory)
3. Check subdirectories: `/Books/`, `/Reading/`, etc.
4. Look for encoding issues in names (special characters)

---

## Maintenance Notes

- **Export Date:** Include in metadata when regenerating
- **Deduplication:** Use `id` field for unique identification
- **Category Assignment:** Review and normalize categories periodically
- **Timestamps:** Use `modified_client` to detect new additions
