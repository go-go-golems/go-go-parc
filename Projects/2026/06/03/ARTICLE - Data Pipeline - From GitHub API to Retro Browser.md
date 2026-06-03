---
title: "A Daily Changelog Pipeline: From GitHub API to Retro Browser"
aliases:
  - Daily Changelog Pipeline
  - Retro Browser Data Pipeline
tags:
  - python
  - sqlite
  - github-api
  - web-server
  - retro-ui
  - data-pipeline
  - article
status: active
type: article
created: 2026-06-03
repo: /home/manuel/code/wesen/claw-stuff/ttmp/2026/06/03/DAILY-CHANGELOG-2026-06-02--daily-changelog-report-for-2026-06-02/scripts
---

# A Daily Changelog Pipeline: From GitHub API to Retro Browser

This article describes a data pipeline that collects GitHub activity for a given day, correlates it with docmgr ticket documents, stores everything in SQLite, and serves it through a retro Mac OS 1 monochrome web browser. The pipeline is three Python scripts and a static HTML/CSS/JS frontend served by a fourth Python script.

The concrete target is the date 2026-06-02, which produced 123 events across 15 canonical repos, 64 commits with 87,411 additions and 40,916 deletions, 11 pull requests, and 20 touched docmgr tickets. The numbers are not the point; the architecture that produces them is.

> [!summary]
> - The pipeline uses the GitHub Events API, Commits API, and Contents API to fetch activity and documents.
> - SQLite is the single source of truth: four tables for raw data, one for ticket documents.
> - Fork deduplication happens at two layers: first by repo name matching, then by commit SHA deduplication.
> - Ticket discovery uses commit file paths as ground truth, not repo scanning, which avoids downloading hundreds of irrelevant tickets.
> - The web server is Python's `http.server` subclass with per-endpoint SQLite queries and a hash-routed single-page app.
> - The retro UI uses pure CSS with 1-bit monochrome colors, diagonal stripe patterns, and no window chrome.

## Why this pipeline exists

The goal is to answer the question "What happened yesterday?" with enough detail to write a meaningful report. GitHub provides activity data, but it is fragmented across API endpoints and mixed with noise (fork events, branch creations, automated formula updates). Docmgr tickets contain design documents and diaries that explain the why behind the commits, but they live in Markdown files inside repo trees, not in the GitHub activity stream.

The pipeline brings these two data sources together into one SQLite database that a single query script can format as markdown, JSON, or a summary. The web browser adds a visual layer for exploration.

## Architecture

```mermaid
flowchart TD
    subgraph Collect["Data Collection"]
        A[GitHub Events API] --> B[01-fetch-github-events.py]
        C[GitHub Contents API] --> D[02-fetch-docmgr-docs.py]
        B --> E[(SQLite daily_changelog.db)]
        D --> E
    end

    subgraph Query["Query & Report"]
        E --> F[03-query-changelog.py]
        F --> G[Markdown Report]
        F --> H[JSON Report]
        F --> I[Summary]
    end

    subgraph Browse["Web Browser"]
        E --> J[04-web-server.py]
        J --> K[/api/overview]
        J --> L[/api/commits]
        J --> M[/api/tickets]
        K --> N[Static HTML/CSS/JS]
        L --> N
        M --> N
    end

    style E fill:#1a3a5c,stroke:#3a7cbd
    style N fill:#2d4a22,stroke:#4a7c3f
```

## Step 1: Fetching GitHub events

`01-fetch-github-events.py` calls `gh api /users/{user}/events` with `--paginate` to retrieve all events for a target date. The Events API returns at most 100 events per page and keeps history for approximately 90 days. The script filters by `created_at` date range and stops paging when it crosses the date boundary.

The script extracts three types of data:

1. **Raw events** stored in the `events` table (event type, repo, payload, actor).
2. **Commits** from `PushEvent` payloads. For each push, the script fetches the head SHA and individual commit SHAs via the Commits API (`/repos/{repo}/commits/{sha}`), which returns file-level diff stats. This is critical: the file paths in the diff identify which docmgr tickets were touched.
3. **Pull requests** from `PullRequestEvent` payloads, stored with action, title, branch refs, and state.

Fork deduplication happens here at the commit level. The same commit SHA can appear in both `wesen/` fork repos and their `go-go-golems/` upstreams. The script deduplicates by SHA, so the same commit is only fetched once. The repo name stored is the one from the event, which may be the fork; downstream consumers must canonicalize.

The SQLite schema for this phase:

```sql
CREATE TABLE events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    repo TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload TEXT,
    actor_login TEXT
);

CREATE TABLE commits (
    sha TEXT PRIMARY KEY,
    repo TEXT NOT NULL,
    message TEXT,
    author_name TEXT,
    author_email TEXT,
    author_date TEXT,
    url TEXT,
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    total_files INTEGER DEFAULT 0,
    files_json TEXT DEFAULT '[]'
);
```

The `files_json` column stores a JSON array of `{filename, status, additions, deletions}` objects. This is the ground truth for which files were modified on the target date.

## Step 2: Fetching docmgr ticket documents

`02-fetch-docmgr-docs.py` solves the problem of identifying which docmgr tickets were actually touched on the target date. The naive approach—scan all repos for `ttmp/` directories—would download hundreds of tickets across dozens of repos, most of them unrelated to the day's activity.

The working approach uses commit `files_json` as ground truth. The script:

1. Queries the `commits` table for all file paths modified on the target date.
2. Extracts ticket directory paths using regex: `ttmp/YYYY/MM/DD/TICKET-ID--slug/`.
3. Filters out `_guidelines` and `_templates` directories that match the pattern but are not tickets.
4. Groups extracted tickets by their canonical repo ( prefers `go-go-golems/*` over `wesen/*` forks).
5. Downloads `index.md`, diary documents (files with "diary" in the name), and design documents (files in `design/` subdirectories) via the GitHub Contents API.

Fork deduplication at the repo level uses simple basename matching. If `wesen/foo` and `go-go-golems/foo` both appear in events, the script prefers the canonical `go-go-golems/foo` and skips the fork. This is not robust against renamed forks, but it handles the common case.

There is a secondary path for date-prefixed experiment repos (`wesen/YYYY-MM-DD--*`). These repos may contain `ttmp/` tickets that do not show up in commit file lists because the entire repo is new. For these repos, the script fetches the full Git tree and looks for `ttmp/` paths matching the target date.

The `docmgr_tickets` table stores ticket ID, repo, title, index content, diary content, and design documents as a JSON array:

```sql
CREATE TABLE docmgr_tickets (
    ticket_id TEXT,
    repo TEXT NOT NULL,
    title TEXT,
    index_md TEXT,
    diary_md TEXT,
    design_docs TEXT DEFAULT '[]',
    ticket_path TEXT,
    PRIMARY KEY (ticket_id, repo)
);
```

On 2026-06-02, this process found 20 tickets across 15 canonical repos, downloading 95 documents total.

## Step 3: Querying and reporting

`03-query-changelog.py` is the read-only consumer of the database. It provides three output formats:

- **Markdown**: a full report with sections for overview, commits by repo (grouped and deduplicated), pull requests, and touched tickets.
- **JSON**: structured data suitable for further processing or machine consumption.
- **Summary**: a one-screen text summary for quick human scanning.

The query script re-implements fork deduplication at the repo level. When counting commits or generating the repo list, it skips `wesen/*` repos if a matching `go-go-golems/*` repo exists in the events set. This ensures the report does not double-count commits that appear in both the fork and upstream.

The markdown report is the primary human-readable output. It groups commits by repo, shows short SHA links, and lists touched tickets with their available document types (diary, design, or index only).

## Step 4: The retro web browser

`04-web-server.py` is a Python `http.server.HTTPServer` subclass that serves static files from `web/` and handles `/api/` endpoints with SQLite queries. It is a single-file server with no external dependencies beyond the Python standard library.

### API surface

| Endpoint | Parameters | Returns |
|----------|------------|---------|
| `/api/overview` | none | Event count, commit count, additions/deletions, PR count, ticket count, event type breakdown |
| `/api/repos` | none | List of repos with commit counts and diff stats |
| `/api/commits` | `?repo=` optional | Commit list with short message, SHA, author, diff stats |
| `/api/pull_requests` | none | PR list with action, title, branches, state |
| `/api/tickets` | none | Ticket list with repo, title, and document sizes |
| `/api/ticket_detail` | `?ticket_id=&repo=` | Full ticket content: index, diary, and parsed design docs |
| `/api/events` | none | All events with type, repo, timestamp |
| `/api/search_commits` | `?q=` | Commits matching message search |

The server opens a new SQLite connection per request. This is simple but not optimal for high load; for a local browser serving one user, it is sufficient.

### The UI aesthetic

The frontend is a static single-page app with no build step: `index.html`, `style.css`, and `app.js`. The aesthetic is Macintosh System 1 monochrome: black and white only, 1px solid borders everywhere, no rounded corners, no gradients, no shadows.

Key visual elements:

- **Title bar**: diagonal black-and-white stripes created with `repeating-linear-gradient(-45deg, ...)`, with white uppercase text.
- **Tab bar**: rectangular tabs with 1px borders, active tab inverted (black background, white text).
- **Content lists**: items separated by 1px bottom borders, hover state inverts colors.
- **Stat boxes**: grid layout with 1px gaps creating visible grid lines.
- **Event bars**: horizontal bar charts with filled black rectangles inside bordered tracks.
- **Scrollbars**: custom WebKit styling with striped thumb patterns.
- **Typography**: `Courier New` / `Monaco` monospace throughout, sizes 8–16px.

The CSS uses CSS custom properties for colors so a theme switch could be implemented by changing four variables, though only the monochrome theme is implemented:

```css
:root {
  --bg: #ffffff;
  --fg: #000000;
  --border: #000000;
  --dim: #555555;
}
```

### Hash-based routing

The application uses URL hash fragments for navigation instead of query parameters. This choice was driven by a bug, not a preference: early versions used `encodeURIComponent` in `onclick` handlers to pass repo names like `go-go-golems/go-go-goja`. When the browser parsed the `onclick` attribute, it decoded the `%2F` slashes once. When the JavaScript later called `decodeURIComponent` on the parameter, it decoded them a second time, turning `%252F` back into `%2F` instead of `/`. The result was "Ticket not found" errors for every repo with a slash in its name.

The fix was to eliminate manual encoding entirely. Instead of constructing URLs with string concatenation, the app uses a global `setHash(tab, params)` helper that builds the hash with `URLSearchParams`:

```javascript
function setHash(tab, params) {
  const usp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    usp.set(k, v);
  }
  window.location.hash = tab + '?' + usp.toString();
}
```

Reading parameters back uses `URLSearchParams` on the query portion of the hash:

```javascript
function getHashParam(key) {
  const hash = window.location.hash.slice(1);
  const params = new URLSearchParams(hash.split('?')[1] || '');
  return params.get(key);
}
```

Routes are parsed from `window.location.hash` on every `hashchange` event:

- `#overview`
- `#repos`
- `#repo-commits?repo=go-go-golems%2Fgo-go-goja`
- `#commits`
- `#prs`
- `#tickets`
- `#ticket?ticket_id=...&repo=...`
- `#events`

Because `URLSearchParams` handles both encoding and decoding, the double-encoding bug cannot recur.

### Markdown rendering in the browser

The ticket detail view renders Markdown content (index, diary, design docs) using a custom lightweight renderer, not a library. It handles headers, bold, inline code, links, horizontal rules, and bullet lists with regex replacements:

```javascript
function renderMarkdown(md) {
  let html = escHtml(md);
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/`([^`]+)`/g, '<code style="background:#000;color:#fff;padding:0 2px">$1</code>');
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  html = html.replace(/^- (.+)$/gm, '• $1');
  return html;
}
```

This is sufficient for the docmgr Markdown convention, which does not use tables, blockquotes, or nested lists. The renderer runs on the client, so the server only needs to serve raw Markdown text.

## The fork deduplication problem

Fork deduplication appears in three places in the pipeline:

1. **Event fetcher**: Deduplicates commit SHAs across fork/upstream pairs so the same commit is only fetched once.
2. **Doc fetcher**: Prefers canonical repos over forks when building the ticket discovery set.
3. **Query script**: Skips `wesen/*` repos in reports when a matching `go-go-golems/*` repo exists.

The logic is the same in all three places: given a repo name, extract the basename. If the repo starts with `wesen/` and a `go-go-golems/{basename}` exists in the same dataset, the `wesen/` version is considered a fork and skipped. This is imperfect—it fails if a fork has a different name from its upstream—but it handles the typical case where forks are literal mirrors.

A more robust approach would use the GitHub API's `fork` field in repo metadata, but the Events API does not return full repo objects, only names. The basename matching heuristic was chosen because it requires no additional API calls.

## Running the pipeline

The complete workflow for a given day:

```bash
# 1. Collect data
python3 01-fetch-github-events.py --date 2026-06-02
python3 02-fetch-docmgr-docs.py --date 2026-06-02

# 2. Generate report
python3 03-query-changelog.py --date 2026-06-02 --format markdown > report.md

# 3. Start browser
python3 04-web-server.py --port 8092
```

The browser runs in a tmux session (`changelog-browser`) and remains accessible at `http://localhost:8092` until stopped.

## Testing the data

For 2026-06-02, the collected data is:

| Metric | Value |
|--------|-------|
| Events | 123 |
| Commits | 64 |
| Additions | 87,411 |
| Deletions | 40,916 |
| Repos (canonical) | 15 |
| Pull requests | 11 |
| Docmgr tickets | 20 |

The web browser's overview screen displays these numbers in a 3x2 grid of stat boxes. Clicking through to the Repos tab shows each repo's commit count and diff stats. The Commits tab lists all 64 commits with searchable messages. The Tickets tab groups tickets by repo and shows which document types are available. Clicking a ticket opens its detail view with tabs for Index, Diary, and Design documents.

## Failure modes

### "Ticket not found" in browser

Cause: double-encoding of repo names with slashes when using `encodeURIComponent` in HTML attributes.  
Fix: use hash-based routing with `URLSearchParams` instead of manual string encoding.

### Duplicate commits in report

Cause: fork deduplication not applied in the query script or event fetcher.  
Fix: ensure all three scripts use the same `wesen/` → `go-go-golems/` skip logic.

### 0 tickets found

Cause: commit file paths do not match the `ttmp/` pattern, or the regex is too restrictive.  
Fix: check that commits actually touch `ttmp/` files, and verify the regex handles the date prefix format.

### Port already in use

Cause: another development server is running on the default port.  
Fix: pass `--port` to use an alternative port (the pipeline uses 8092).

## Architecture diagram: browser internals

```mermaid
flowchart TD
    subgraph Browser["Single-Page App"]
        A[Hash Router] --> B[Tab Dispatcher]
        B --> C[Overview]
        B --> D[Repos]
        B --> E[Commits]
        B --> F[PRs]
        B --> G[Tickets]
        B --> H[Ticket Detail]
        B --> I[Events]

        H --> J[Markdown Renderer]
        J --> K[Tab: Index]
        J --> L[Tab: Diary]
        J --> M[Tab: Design]
    end

    subgraph Server["Python HTTP Server"]
        N[/api/*] --> O[SQLite Queries]
        P[Static Files] --> Q[index.html style.css app.js]
    end

    O --> R[(daily_changelog.db)]
    A --> N
    Q --> A

    style R fill:#1a3a5c,stroke:#3a7cbd
    style Browser fill:#2d4a22,stroke:#4a7c3f
```

## Related notes

- [[ARTICLE - xgoja - Building a Query Tool with Jsverbs and Embedded Modules]] — the xgoja-based diary querying tool built on this data
- [[DAILY-CHANGELOG-2026-06-02]] — the docmgr ticket containing all scripts and data
- [[ttmp/2026/06/03/DAILY-CHANGELOG-2026-06-02--daily-changelog-report-for-2026-06-02/scripts/01-fetch-github-events.py]] — event fetcher
- [[ttmp/2026/06/03/DAILY-CHANGELOG-2026-06-02--daily-changelog-report-for-2026-06-02/scripts/02-fetch-docmgr-docs.py]] — docmgr doc fetcher
- [[ttmp/2026/06/03/DAILY-CHANGELOG-2026-06-02--daily-changelog-report-for-2026-06-02/scripts/04-web-server.py]] — web server and API
