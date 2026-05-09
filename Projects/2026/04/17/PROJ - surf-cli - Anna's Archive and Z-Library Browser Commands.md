---
title: "surf-cli - Anna's Archive and Z-Library Commands"
aliases: ["surf-cli annas-archive", "surf-cli libgen", "surf-go paper download", "surf-go book download"]
tags:
  - project
  - surf-cli
  - browser-automation
  - cli
  - glazed
  - go
status: active
type: project
created: 2026-04-17
repo: /home/manuel/code/others/llms/pi/nicobailon/surf-cli
---

# surf-cli — Anna's Archive and Z-Library Browser Commands

This project added two new sets of browser-automation commands to surf-go for downloading papers and books from Anna's Archive (annas-archive.gl) and Z-Library's 1lib.sk mirror.

> [!summary]
> - Added `surf-go annas-archive` command for scientific paper download via DOI lookup or search
> - Added `surf-go libgen` command suite (search, download, suggestions, collections) for 1lib.sk
> - Both use the browser-side verb pattern with embedded JavaScript extraction
> - Key discovery: 1lib.sk uses custom HTML elements (`<z-booklist>`, `<z-cover>`) that require attribute-based parsing

## Why This Project Exists

surf-go is a CLI tool that wraps browser automation for web interactions. The original codebase had patterns for browser-side commands but lacked support for two major knowledge repositories: scientific paper archives and ebook libraries. This project fills that gap.

## Current Project Status

**Anna's Archive commands**: Complete and working.
**Z-Library (1lib.sk) commands**: Complete and working, with fixes for dynamic content loading.

## Project Shape

### Repository Structure

```
surf-cli/
├── AGENTS.md                          # Project instructions
├── go/
│   ├── cmd/surf-go/main.go           # Command registration
│   └── internal/cli/commands/
│       ├── annas_archive.go          # Parent command
│       ├── annas_archive_search.go  # Search subcommand
│       ├── annas_archive_download.go  # Download subcommand
│       ├── libgen.go                 # Parent command
│       ├── libgen_search.go         # Search subcommand
│       ├── libgen_download.go        # Download subcommand
│       ├── libgen_suggestions.go    # Suggestions subcommand
│       ├── libgen_collections.go    # Collections subcommand
│       ├── libgen_collection.go      # Books in collection subcommand
│       └── helpers.go                # Shared utilities
└── ttmp/.../SURF-20260417-ANNAS1/  # Research diary and scripts
```

### Anna's Archive Commands

```bash
# Search for papers
surf-go annas-archive search --query "machine learning"

# Download by DOI (recommended)
surf-go annas-archive download --doi 10.1038/nature12373

# List available mirrors
surf-go annas-archive download --doi 10.1038/nature12373 --list-mirrors

# Select specific mirror
surf-go annas-archive download --doi 10.1038/nature12373 --mirror slow --mirror-index 0

# Download to file
surf-go annas-archive download --doi 10.1038/nature12373 --save-to ~/papers/thermometry.pdf
```

### Z-Library Commands

```bash
# Search for books
surf-go libgen search --query "Project Hail Mary"

# Get download link
surf-go libgen download --url "https://1lib.sk/book/4vrAp1VDOn/project-hail-mary.html"

# Get suggested books
surf-go libgen suggestions --url "https://1lib.sk/book/mZ3oDW8qZo/..."

# Get collections a book appears in
surf-go libgen collections --url "https://1lib.sk/book/mZ3oDW8qZo/..."

# Get books in a collection
surf-go libgen collection --id 527560
```

## Implementation Details

### Architecture

Both command sets follow the same pattern:

1. **Transport layer**: Connect to surf-go browser socket via `transport.NewClient()`
2. **Tab management**: Open new tab or navigate existing one to target URL
3. **Wait cycle**: Sleep + scroll to trigger lazy loading
4. **JS extraction**: Execute embedded JavaScript to parse page content
5. **Response parsing**: Parse JSON response from JS execution
6. **Output**: Return Markdown or Glaze rows based on flags

### Anna's Archive Download Flow

```
DOI query → Search page → Extract MD5 hash → Navigate to paper page → Extract metadata and download URLs → Return results
```

Key URL patterns:
- Search: `https://annas-archive.gl/search?q={doi}&index=journals`
- Paper: `https://annas-archive.gl/md5/{md5}`
- Fast download: `/fast_download/{md5}/0/{serverIndex}` (requires membership)
- Slow download: `/slow_download/{md5}/0/{serverIndex}` (works without membership)

Mirror selection:
- Fast mirrors: 12 servers (0-11), servers 0-5 marked "recommended"
- Slow mirrors: 8 servers (0-7), no membership required
- Default: random slow mirror

Download wait handling:
```go
// Poll for download page to appear
for i := 0; i < 40; i++ {
    time.Sleep(3 * time.Second)
    resp, _ := ExecuteTool(...)
    // Check page state: waiting → download_page → found
}
```

### 1lib.sk Discovery: Custom HTML Elements

The critical discovery was that 1lib.sk uses custom web components rather than standard HTML elements:

```html
<!-- Collections (booklists) use z-booklist -->
<z-booklist href="/booklist/527560/..." topic="Self-Development" quantity="699">
  <z-cover title="Book Title" author="Author Name" />
</z-booklist>

<!-- Books use z-book or z-cover -->
<z-book href="/book/abc123/..." title="..." author="..." />
<z-cover href="/book/xyz789/..." title="..." author="..." />
```

Extraction JavaScript must query these custom elements and read their attributes:

```javascript
// Parse collections
var booklistElements = document.querySelectorAll('z-booklist');
booklistElements.forEach(function(el) {
  var href = el.getAttribute('href');
  var topic = el.getAttribute('topic');
  var quantity = el.getAttribute('quantity');
  // ...
});

// Parse suggestions
var coverElements = document.querySelectorAll('z-cover');
coverElements.forEach(function(el) {
  var title = el.getAttribute('title');
  var author = el.getAttribute('author');
  // ...
});
```

### 1lib.sk Search: Parsing Body Text

1lib.sk loads search results dynamically, and the book links aren't immediately in the DOM. The solution parses numbered titles from `document.body.innerText`:

```javascript
// Pattern: "1\nTitle\n2\nTitle2" format
var numberPattern = /(\d+)\s*\n([^\n]{5,300})/g;
var match;
while ((match = numberPattern.exec(bodyText)) !== null && count < maxResults) {
  var title = match[2].trim();
  // Skip headers, footers, navigation...
  // Extract metadata from surrounding text
  // ...
}
```

Wait and scroll cycle to trigger lazy loading:
```go
time.Sleep(5 * time.Second)
for i := 0; i < 8; i++ {
    _, _ = ExecuteTool(ctx, client, "js", map[string]any{
        "code": `window.scrollTo(0, document.body.scrollHeight); ...`
    }, tabID, windowID)
    time.Sleep(2 * time.Second)
}
```

### Command Registration Pattern

Commands implement the `cmds.GlazeCommand` and `cmds.WriterCommand` interfaces:

```go
type LibgenSearchCommand struct {
    *cmds.CommandDescription
}

var _ cmds.GlazeCommand = (*LibgenSearchCommand)(nil)
var _ cmds.WriterCommand = (*LibgenSearchCommand)(nil)

func (c *LibgenSearchCommand) RunIntoGlazeProcessor(...) error { ... }
func (c *LibgenSearchCommand) RunIntoWriter(...) error { ... }
```

Registration in `main.go`:
```go
libgenCmd, _ := commands.NewLibgenCommand()
cobraLibgen, _ := buildGlazedCommand(libgenCmd)

libgenSearchCmd, _ := commands.NewLibgenSearchCommand()
cobraLibgenSearch, _ := buildDualModeCommand(libgenSearchCmd)

cobraLibgen.AddCommand(cobraLibgenSearch, ...)
rootCmd.AddCommand(cobraLibgen)
```

## Research Scripts

Located in `ttmp/2026/04/16/SURF-20260417-ANNAS1/scripts/`:

| Script | Purpose |
|--------|---------|
| `01-page-shape-probe.js` | Initial page exploration |
| `02-search-result-extractor.js` | Search result extraction validation |
| `03-paper-detail-extractor.js` | Paper page extraction validation |
| `04-download-url-extractor.js` | Download URL extraction from SciDB |

## Important Project Rules

### js Tool Limitation

The `js` tool requires an explicit `return` statement:
```javascript
var result = {test: true};
return result;  // This works
// result;       // This does NOT work
```

IIFEs don't work:
```javascript
(function() { return {test: true}; })();  // returns undefined
```

### Emoji in Go Strings

Emoji literals cause Go string parsing issues. Avoid:
```javascript
// BAD
text.includes('📚')

// GOOD
text.toLowerCase().includes('download')
```

### Mirror Selection

Fast mirrors require Anna's Archive membership. Always reject with clear message:
```go
if mirror == "fast" {
    return nil, fmt.Errorf("--mirror fast is not supported: fast mirrors require Anna's Archive membership")
}
```

### Flag Naming

Glazed uses `--output` for format selection. Use `--save-to` for file paths:
```go
fields.New("save-to", fields.TypeString, fields.WithDefault(""), ...)
```

## Open Questions

- [ ] Test actual PDF download (not just URL extraction) for annas-archive
- [ ] Test libgen collection subcommand with a valid collection ID
- [ ] Add unit tests for extraction functions
- [ ] Consider caching extracted book IDs for faster re-search

## Near-Term Next Steps

1. Test `--save-to` with annas-archive to verify file download works
2. Test `libgen collection --id 527560` to validate collection book extraction
3. Clean up debug output in production
4. Add embedded help documentation

## Related Notes

- `01-building-browser-side-verbs.md` — Tutorial for browser-side commands in surf-go
- `PROJ - surf-cli` — Main surf-cli project note (if exists)
