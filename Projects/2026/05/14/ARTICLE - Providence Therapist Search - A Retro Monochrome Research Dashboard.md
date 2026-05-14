---
title: "Providence Therapist Search: A Retro Monochrome Research Dashboard"
aliases:
  - Therapist Search Dashboard Deep Dive
  - THERAPIST-PVD-2026 Technical Report
  - Claw Therapist Pipeline
  - Psychology Today Scraper Dashboard
tags:
  - project-report
  - article
  - python
  - sqlite
  - react
  - redux
  - rtk-query
  - playwright
  - vite
  - web-scraping
  - healthcare
status: active
type: article
created: 2026-05-14
repo: /home/manuel/code/wesen/claw-stuff/therapist-search
source_ticket: THERAPIST-PVD-2026
related_docs:
  - /home/manuel/code/wesen/claw-stuff/ttmp/2026/05/14/THERAPIST-PVD-2026--providence-medicaid-autism-adhd-lgbtq-therapist-search/reference/01-diary.md
  - /home/manuel/code/wesen/claw-stuff/ttmp/2026/05/14/THERAPIST-PVD-2026--providence-medicaid-autism-adhd-lgbtq-therapist-search/reference/02-research-findings.md
  - /home/manuel/code/wesen/claw-stuff/therapist-search/README.md
updated: 2026-05-14
---
Ma
# Providence Therapist Search: A Retro Monochrome Research Dashboard

This article explains how the Providence Therapist Search dashboard was built, why each architectural layer exists, and how the pieces connect. The result is a local-first research tool that scrapes therapist directory sites with Playwright, stores provider records and evidence quotes in SQLite, and presents a Finder-style split-pane dashboard built with React, Redux, and RTK Query. The dashboard runs entirely on localhost with no cloud dependencies, no user accounts, and no external runtime costs.

Understanding this system matters because it demonstrates a pattern that applies far beyond therapist search: when you need to gather structured data from opaque web sources, evaluate it against multiple criteria, track your outreach progress, and do all of this without leaking personal health information to third-party services, the architecture looks like this. The same pattern works for housing searches, legal provider research, school comparisons, or any domain where the data is public but the curation is personal.

## 1. The Problem: Directory Data Is Stale, Scattered, and Unverifiable

Therapist directories like Psychology Today expose filter-based search interfaces. You can filter by location, insurance type, and specialty categories. What they do not provide is a way to cross-reference across filters, track whether a provider actually accepts a specific Medicaid managed-care plan, remember that you already called someone, or note that they mentioned a three-month waitlist.

The directory displays what a provider self-reported when they created their profile. That information may be months or years out of date. A therapist listed under the "Medicaid" filter may have stopped accepting Medicaid since their last profile update. A therapist who does not appear under the "Autism" filter may still specialize in neurodivergent adults but did not check that category box. The directory is a starting point, not a verified database.

The design goal was therefore not to build a better directory, but to build a local research tool that:

1. Captures raw data from multiple directory filter passes
2. Merges and deduplicates across those passes
3. Extracts evidence quotes that justify why a provider was surfaced
4. Scores providers based on accumulated evidence, not any single filter
5. Lets a human curate the results with persistent starring, outreach tracking, and contact notes
6. Persists all state locally in SQLite, not in browser localStorage or a remote database

## 2. Architecture Overview

The system has four layers. Each layer has a single responsibility and communicates with adjacent layers through well-defined interfaces.

| Layer | Technology | Responsibility |
|-------|------------|----------------|
| Scraping | Playwright (Node.js) | Browse directory pages, extract structured provider data and evidence quotes, write raw JSON |
| Ingestion | Python | Read raw JSON, classify evidence, score providers, deduplicate by profile URL, write SQLite |
| Storage | SQLite | Single-file relational database with providers, evidence, source runs, and curation columns |
| Dashboard | Vite + React + Redux + RTK Query | Browse providers, review details, curate starred/emailed/called status, persist mutations back to SQLite |

The data flows in one direction during a research session: scraper produces JSON, Python imports it into SQLite, the dashboard reads SQLite and presents it. Curation mutations flow back through a small POST API to SQLite. There is no webhook, no message queue, no distributed cache. The Python server reads SQLite fresh on every API request, which means the dashboard always shows current data without any manual refresh mechanism beyond RTK Query's built-in polling.

```
Playwright scraper  →  raw JSON files  →  Python import  →  therapists.sqlite
                                                           ↑  ↓
                                              Vite/React dashboard (reads + mutates)
```

This architecture trades throughput for simplicity and auditability. A scrape takes two to three minutes. An import takes under a second. The dashboard polls every three seconds. For a personal research tool used by one person on one machine, these latencies are irrelevant. What matters is that every piece of data has a provenance trail: which source produced it, which filter surfaced it, which quote justified the evidence tag.

## 3. The Scraping Layer: Playwright as a Research Browser

### Why Playwright, not requests + BeautifulSoup

Psychology Today renders therapist listings client-side. The listing cards appear after JavaScript execution, and the therapist profile pages load additional content dynamically. A static HTTP request returns a shell page with no provider data. Playwright runs a real browser, executes the JavaScript, waits for content to appear, and then extracts what the browser actually renders.

This is the central tradeoff of any scraping approach: static scrapers are fast and lightweight but miss dynamic content; browser scrapers are slow and heavyweight but see what a human sees. For a research tool that runs once every few days, the slower option is the correct one.

### The listing scraper

The listing scraper (`scripts/scrape-psychology-today.spec.js`) navigates to Psychology Today's therapist search with specific filter parameters. Three filter passes are run sequentially:

| Filter URL suffix | What it captures |
|---|---|
| `?category=medicaid` | Providers who self-report accepting Medicaid |
| `?category=autism` | Providers who list autism as a specialty |
| `?category=gay` | Providers who list LGBTQ-affirming care |

Each pass paginates through the first two pages of results and extracts provider names, profile URLs, phone numbers, and listing snippets. The scraper writes raw JSON after each pass so that a timeout on a later pass does not discard earlier results.

The extraction logic runs inside `page.evaluate()`, which executes JavaScript in the browser context. This means the scraper can use the same DOM APIs that a front-end developer would use: `querySelectorAll`, `innerText`, attribute access. The scraper does not parse HTML with regex or string manipulation; it queries the live DOM.

### The profile scraper

The listing scraper captures surface-level data. The profile scraper (`scripts/scrape-profile-pages.spec.js`) goes deeper. For each profile URL discovered by the listing scraper, it navigates to the individual profile page and extracts:

- Full page body text (up to 12,000 characters), which contains specialties, insurance details, client focus, treatment approach, and availability information that never appears in the listing card
- Therapist photo URL from Psychology Today's CDN (pattern: `photos.psychologytoday.com/<uuid>/<version>/320x400.jpeg`)
- Email link and website link if present
- Section headings for structural context

The profile scraper writes its output incrementally after each page, which is important because scraping 79 profile pages at roughly one second per page exceeds Playwright's default test timeout. If the scraper only wrote output at the end of the test, a timeout at profile 78 would discard 77 successful captures. Incremental writes prevent this data loss.

### Incremental writes as a reliability pattern

This pattern—write partial results after every iteration, not just at the end—is worth stating explicitly because it applies to any long-running scraping or batch processing script. The implementation is straightforward:

```javascript
for (const seed of seeds) {
  // ... scrape one profile ...
  providers.push(rec);
  fs.writeFileSync(OUT, JSON.stringify({ providers, /* ... */ }, null, 2));
}
```

The `writeFileSync` call after each `push` means the JSON file always contains everything scraped so far. If the process crashes, the file reflects the last successful iteration, not an empty or stale state. The cost is additional disk I/O, which is negligible for a local research tool.

## 4. The Ingestion Layer: Evidence Classification and Scoring

The ingestion script (`scripts/import_json.py`) reads all raw JSON files from `data/raw/` and upserts provider records into SQLite. "Upsert" means insert if the profile URL does not exist, or update specific fields if it does. This is necessary because the same provider can appear in multiple filter passes—a Medicaid scrape, an autism scrape, and an LGBTQ scrape—and the database should contain one row per provider, not three.

### Keyword-based evidence extraction

The ingestion script classifies provider text against keyword lists:

```python
KEYWORDS = {
    "autism": ["autism", "autistic", "neurodiverg", "audhd", "asperger"],
    "adhd": ["adhd", "executive function", "executive functioning", "attention-deficit"],
    "lgbtq": ["lgbt", "queer", "trans", "nonbinary", "gender identity", "sexuality"],
    "medicaid": ["medicaid", "medical assistance"],
    "new_clients": ["accepting", "taking new", "new clients", "no wait"],
}
```

When a keyword appears in the provider's listing snippet or profile text, the script creates an evidence record linking that provider to the claim type and the specific keyword that matched. The evidence record also stores a verbatim quote (up to 1200 characters) so that a human reviewer can later verify whether the keyword was used in a meaningful context or appeared incidentally.

Keyword classification is intentionally simple. It misses synonyms it does not know about ("spectrum" without "autism", "neurodiverse" without "neurodivergent"). It catches incidental mentions ("I do not treat autism"). The scoring compensates for these limitations by treating scores as triage signals, not rankings. A score of 55 means "this provider matches two of our criteria and is worth investigating," not "this provider is 55% likely to be a good fit."

### Cross-source score computation

The score for each provider is computed from the set of distinct evidence claim types, not from any single import record. This is the second important design decision in the ingestion layer, and it deserves attention.

If the scoring simply took the maximum evidence score from any single import row, a provider who appeared in both the Medicaid and autism filters would score the same as a provider who appeared in only one of them. That understates the cross-source corroboration. A provider who self-reports both Medicaid acceptance and autism specialization is a stronger candidate than one who reports only one of those.

The fix is a post-import recomputation step:

```python
for (pid,) in conn.execute("SELECT id FROM providers"):
    claims = {row[0] for row in conn.execute(
        "SELECT DISTINCT claim_type FROM evidence WHERE provider_id = ?", (pid,)
    )}
    new_score = sum(weights.get(c, 0) for c in claims)
    conn.execute("UPDATE providers SET fit_score = ? WHERE id = ?", (new_score, pid))
```

The weights are:

| Claim type | Weight |
|---|---:|
| Medicaid | 30 |
| Autism | 25 |
| ADHD | 20 |
| LGBTQ | 20 |
| New clients | 5 |

These weights reflect the search priorities: Medicaid acceptance is mandatory (weight 30), autism and ADHD specialization are the clinical need (25 and 20), LGBTQ-affirming care is essential (20), and current availability is useful but easily verified by phone (5).

### Deduplication by profile URL

The `providers` table uses `profile_url` as a unique constraint. The SQLite `ON CONFLICT(profile_url) DO UPDATE SET ...` clause handles the merge: when a provider already exists, the import updates only the fields that have new or longer values (phone number, profile text, website URL). The canonical name, credentials, and existing curation state are preserved.

This approach means that a provider's `starred`, `emailed`, `called`, `contact_notes`, and `status` columns are never overwritten by an import. Curation state survives re-scraping and re-importing.

## 5. The Storage Layer: SQLite as a Single-File Research Database

### Schema design

The database has three tables and one view.

**`providers`** holds one row per deduplicated therapist. It contains identity fields (name, credentials, phone, URLs), evidence-derived fields (fit_score, accepts_medicaid, evidence_tags via the view), and curation fields (starred, emailed, called, contact_notes, status, email_date, call_date, last_contacted_at, profile_text, photo_url).

**`evidence`** holds one row per keyword match. Each row links a provider to a claim type, the specific keyword that triggered the match, a verbatim quote, and the source that produced the match. This table is append-only during normal operation; re-importing the same raw JSON produces duplicate evidence rows for the same provider+claim_type+claim_value combination, which is harmless (the view aggregates with `group_concat(DISTINCT ...)`).

**`source_runs`** logs each import pass with a timestamp, status, and note describing how many records were processed. This table makes it possible to answer "when did we last scrape?" and "did the Medicaid scrape succeed?"

**`provider_summary`** is a view that joins providers with their aggregated evidence. The dashboard reads this view exclusively, never the raw tables.

### Schema evolution with ALTER TABLE

The schema has evolved across seven development steps. New columns were added for starring, email/call tracking, contact notes, profile text, and photo URLs. None of these additions required rebuilding the database from scratch.

SQLite supports `ALTER TABLE ADD COLUMN` for adding new columns to existing tables. The migration script (`scripts/migrate_db.py`) and the dashboard server's startup both use this mechanism: check `PRAGMA table_info(providers)`, add any missing columns, and recreate the view. This means the database file survives schema changes without data loss.

The one migration hazard is `CREATE TABLE IF NOT EXISTS`. This statement creates the table only if it does not exist; it does not add new columns to an existing table. If the migration script uses `executescript()` with the full `CREATE TABLE` definition, and the table already exists, the new columns are silently ignored. The `ALTER TABLE ADD COLUMN` approach is the correct way to evolve an existing SQLite schema.

## 6. The API Layer: A Minimal Python Server

The Python server (`scripts/serve_dashboard.py`) is a `ThreadingHTTPServer` with three endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/progress` | GET | Return all providers, evidence, runs, and stats as JSON |
| `/api/provider` | POST | Update curation fields (starred, emailed, called, status, contact_notes) |
| `/healthz` | GET | Liveness check |

The server reads SQLite fresh on every `/api/progress` request. There is no in-memory cache, no write-ahead optimization, no connection pooling. For a single-user local tool with a 79-row database, these omissions are features, not bugs. Every API response reflects the current state of the database, which means the dashboard can never show stale data.

The `POST /api/provider` endpoint accepts a JSON body with an `id` field and any combination of allowed curation fields. It constructs a dynamic `UPDATE ... SET` statement from the provided fields, executes it, and returns `{"ok": true, "provider_id": N}`. If the provider ID does not exist, it returns 404.

The server also runs the schema migration on startup: it checks for missing columns and adds them. This means that starting the server after a code update automatically migrates the database to the latest schema.

## 7. The Dashboard Layer: React, Redux, and RTK Query

### Why not vanilla JS

The original dashboard was a single HTML file with inline JavaScript. It used `fetch()` for API calls and manually patched the DOM on every poll cycle. This approach has two problems that compound over time.

First, mutation calls were invisible. The code called `fetch('/api/provider', { method: 'POST', ... })` and then called `poll()`, but the relationship between the mutation and the re-fetch was implicit. If the poll interval was long, the user would not see their change reflected immediately. If the poll interval was short, the user would see redundant network traffic. There was no mechanism to say "this mutation invalidated this query; re-fetch now."

Second, the DOM patching was fragile. Each poll cycle rebuilt large sections of innerHTML, which destroyed textarea focus, lost cursor positions in contact notes, and created subtle race conditions between user input and data refresh. Fixing these issues in vanilla JS requires increasing amounts of bookkeeping code that duplicates what a rendering framework does by default.

### RTK Query's cache invalidation model

RTK Query solves both problems. The API slice defines two endpoints:

```typescript
getProgress: builder.query<ProgressPayload, void>({
  query: () => ({ url: '/progress', params: { _: Date.now() } }),
  providesTags: ['Progress'],
  keepUnusedDataFor: 0,
}),

patchProvider: builder.mutation<{ ok: boolean; provider_id: number }, PatchProviderRequest>({
  query: (body) => ({ url: '/provider', method: 'POST', body }),
  invalidatesTags: ['Progress'],
}),
```

When `patchProvider` succeeds, RTK Query sees that it invalidates the `Progress` tag. It then checks which queries provide that tag—`getProgress` does—and automatically re-fetches them. The dashboard component re-renders with the new data. The user sees their change reflected immediately without any manual refresh or explicit `poll()` call.

The `pollingInterval: 3000` on `useGetProgressQuery` adds a background re-fetch every three seconds. This catches changes from other sources (for example, if someone runs the import script while the dashboard is open). The combination of mutation-driven invalidation (immediate feedback) and polling (background sync) covers both the interactive and the background cases.

### The UI slice: all client-side state in one place

The `uiSlice` Redux slice manages everything that is not server data: current view, browse mode (cards vs list), selected provider ID, modal state, and filter settings. These are pure client-side concerns. They do not need API calls; they need reactive updates.

Putting UI state in Redux rather than component-local `useState` has one practical benefit: any component can read and write any piece of UI state through the store, without prop drilling. The `Controls` component sets the search query; the `BrowseView` component reads it. Neither component needs to know about the other.

The URL hash is also managed through the UI slice. When the user selects a provider, the `selectProvider` action writes `#<provider_id>` to the URL via `history.replaceState`. On page load, the app reads the hash and dispatches `selectProvider` to restore the selection. Browser back/forward is handled by a `hashchange` event listener.

### Component structure

The dashboard has seven React components:

| Component | What it renders |
|---|---|
| `Header` | Title, polling timestamp |
| `Metrics` | Six stat cards (providers, shortlist, starred, emailed, called, evidence) |
| `Controls` | Search input, score filter, contact filter, view tabs |
| `BrowseView` | Split-pane: cards/list on the left, detail sidebar on the right |
| `TrackerView` | Full-width contact log table |
| `RunsSection` | Togglable source runs and evidence panel |
| `ModalOverlay` | One-by-one review browser with photo, details, and keyboard navigation |

The split-pane layout in `BrowseView` uses a CSS grid with two columns: `minmax(0, 1fr) 320px`. The left column scrolls independently and contains either a card grid or a compact list. The right column is a fixed-width detail sidebar that shows the selected provider's photo, credentials, evidence tags, phone, curation controls, contact notes, and profile text. The entire pane uses `flex: 1 1 0%` inside a flex-column `main` element with `height: 100vh`, so the split pane fills exactly the remaining viewport space after the header, metrics, and controls.

The modal overlay uses a full-viewport backdrop and a centered panel with a two-column layout (photo left, details right). Keyboard navigation (arrow keys for prev/next, S for star, Escape to close) is handled by a global `keydown` listener that is active only when the modal is open.

## 8. The Visual Design: System 1 Retro Monochrome

The dashboard uses a monochrome aesthetic inspired by early Macintosh System 1 interface conventions. Every interactive element has a 2-pixel solid black border and a 2-pixel box-shadow offset. Buttons invert to white-on-black when pressed. Window chrome uses a repeating linear-gradient stripe pattern for title bars. The background uses a subtle horizontal stripe pattern.

These are not decorative choices. The monochrome palette removes visual noise that does not serve the task. When you are comparing 79 therapists across multiple evidence dimensions, color coding adds cognitive load without adding information. The score badge, the evidence tags, and the starred outline use the same black-on-paper contrast as everything else. The visual hierarchy comes from weight, size, and position, not from color.

The `pagetext` class renders profile text as readable prose with `line-height: 1.5`, no border, and a transparent background. This distinguishes it from editable textareas (contact notes, which have borders and backgrounds). Read-only reference material should not visually compete with input fields.

## 9. The Curation Workflow

The dashboard supports a specific research workflow that evolved from using the tool:

1. **Triage**: Start on the Browse view. Use the score filter to show only providers with score 50+. These are providers who matched at least two of the search criteria. Click through the cards to see their detail sidebar.

2. **Deep review**: Click "▶ Review" to open the modal. Use arrow keys to browse one by one. Press S to star providers worth contacting. The star is persisted immediately via `POST /api/provider`.

3. **Outreach**: Switch to the "All + contact log" tracker view. Filter by "Starred" to see only starred providers. Check "emailed" or "called" as you reach out. Write contact notes (e.g., "left voicemail 5/14", "not accepting new clients", "waitlist 3 months"). The notes are persisted on blur with a 600ms debounce.

4. **Verification**: Every piece of directory data must be verified by phone. The Medicaid filter on Psychology Today means the provider self-reported accepting Medicaid at some point. It does not mean they accept your specific Medicaid managed-care plan (Neighborhood Health Plan, Tufts Health Plan, UnitedHealthcare Community Plan). Call and confirm.

This workflow is encoded in the database schema through the `status` column, which accepts: `needs_review`, `promising`, `contacted`, `waitlist`, `rejected`. The tracker view exposes this as a dropdown on each row.

## 10. Running the System

The system requires two processes: the Python API server and the Vite development server.

```bash
# Terminal 1: API server on port 8766
cd therapist-search
python3 scripts/serve_dashboard.py

# Terminal 2: Vite dev server on port 8765 (proxies /api to 8766)
cd therapist-search/dashboard
npx vite --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765` in a browser. The Vite server handles the React application and proxies any `/api/*` request to the Python server on port 8766. Vite's hot module replacement pushes code changes to the browser without a full reload.

To refresh the research data:

```bash
npm run scrape:pt          # Scrape listing pages (~20s)
MAX_PROFILES=79 npm run scrape:profiles  # Scrape profile pages (~3min)
npm run import             # Import raw JSON into SQLite (<1s)
```

The dashboard picks up new data within 3 seconds of the import completing, because RTK Query's polling interval triggers a re-fetch.

## Key Points

- The system uses Playwright for scraping because therapist directories render content client-side; static HTTP requests return empty shells.
- Raw scrapers write JSON incrementally after every record, so a timeout does not discard already-captured data.
- The ingestion layer classifies evidence with keyword matching and scores providers from accumulated distinct claim types across multiple source filters.
- SQLite stores providers, evidence quotes, source run logs, and curation state in a single file. `ALTER TABLE ADD COLUMN` handles schema evolution without data loss.
- RTK Query's `invalidatesTags` mechanism provides immediate UI feedback after mutations and eliminates the need for manual `poll()` calls after every star or email checkbox change.
- The split-pane layout uses CSS flexbox with `flex: 1 1 0%` so the browse area fills exactly the remaining viewport space.
- All curation state is persisted server-side in SQLite, not in browser localStorage. This means data survives browser crashes, tab closures, and cache clears.
- Directory data must be verified by phone. A provider's self-reported Medicaid acceptance on Psychology Today does not guarantee they accept a specific Medicaid managed-care plan.

## What Was Built, What Was Not

The system provides data capture, evidence tracking, curation, and outreach management. It does not provide:

- Automated phone verification. Calling providers to confirm Medicaid acceptance is a human task.
- Multi-user access. The SQLite database is single-writer. Concurrent access from multiple browser tabs is safe (reads are concurrent; writes are serialized by SQLite's WAL mode), but there is no authentication or authorization.
- Source diversity beyond Psychology Today. The RI EOHHS Medicaid provider search, Neighborhood Health Plan provider directory, Zencare, TherapyDen, Inclusive Therapists, and ND Therapists are all candidates for future scrapers.
- Photo caching. Therapist photos are loaded directly from Psychology Today's CDN. If PT blocks hotlinking or changes their CDN, photos will break. A future pass could download photos to `data/photos/`.
- Production deployment. The system runs on localhost with a Vite dev server. A production build would use `vite build` to produce static assets served by the Python server.
