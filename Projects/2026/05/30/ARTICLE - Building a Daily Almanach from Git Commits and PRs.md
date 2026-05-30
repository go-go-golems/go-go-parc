---
title: Building a Daily Almanach from Git Commits, Pull Requests, and Agent Sessions
aliases:
  - almanach-collector
  - daily-almanach
tags:
  - almanach
  - reporting
  - git
  - sqlite
  - thermal-printer
  - data-pipeline
status: active
type: article
created: 2026-05-30
repo: /home/manuel/code/wesen/claw-stuff
ticket: ALMANACH-20260529
---

# Building a Daily Almanach from Git Commits, Pull Requests, and Agent Sessions

This article explains a system that collects daily engineering activity from multiple sources—git commits, GitHub pull requests, and Pi agent sessions—and transforms that raw data into a printed thermal-paper almanach. The system is designed to answer a specific question: what did I work on yesterday? The answer is delivered not as a dashboard or a notification, but as a physical object: a strip of thermal paper that can be read once and discarded, or pinned to a wall as a tangible record of the day.

The implementation uses a sqlite database as the central data store, a collection of Python scripts to gather data, and the almanach-render-service to turn a YAML layout into a rendered bitmap that is sent to a thermal printer. This article covers the architecture of the data pipeline, the schema design, the layout format, the rendering process, and the operational details of running the system on a daily basis.

> [!summary]
> - A sqlite database serves as the central ledger for commits, PRs, and agent sessions.
> - Python scripts collect data from git, the GitHub CLI, and go-minitrace archives.
> - A YAML layout file describes the almanach page as a sequence of narrative blocks.
> - The almanach-render-service converts the layout into a bitmap and sends it to a thermal printer.
> - The system collected 206 commits, 32 PRs, and agent session metadata for a single day.

## Why This System Exists

Engineering work is distributed across many repositories, workspaces, and tools. A single day of work might span a feature branch in one repo, a documentation update in another, a pull request review in a third, and an agent-assisted session in a fourth. No single tool shows all of this activity in one place. GitHub shows PRs but not local commits that have not been pushed. Git shows commits but not PR descriptions or agent sessions. The Pi agent logs sessions but does not correlate them with git activity.

The almanach collector exists to aggregate these disparate signals into a single coherent view. The aggregation is not a real-time dashboard; it is a batch process that runs once per day, gathers everything from the previous 24 hours, and produces a single artifact. The artifact is designed to be read quickly, not studied in depth. It tells a story: what projects were active, what shipped, what broke, and what was learned.

The choice of a thermal printer as the output device is deliberate. Thermal paper is ephemeral. It does not accumulate. It does not require a screen. It produces a physical reminder of the day that can be read at a glance, then discarded. The constraints of the medium—384 pixels wide, black and white, limited length—force the content to be concise. The almanach is not a comprehensive report; it is a distillation.

## The Data Pipeline

The pipeline has three stages: collection, storage, and rendering. Each stage is independent. The collector scripts write to sqlite. The renderer reads from sqlite (or from a data context file derived from sqlite). The printer receives a bitmap from the renderer. This separation means that any stage can be replaced without affecting the others.

### Stage 1: Collection

The collector scripts are stored in the ticket's `scripts/` directory. They are numbered to indicate execution order, though they can also be run independently.

#### 1.1 Git Commits

The `11-collect-git.py` script discovers git repositories by walking a set of search directories and looking for `.git` directories. It then runs `git log --since=<date> --until=<date>` against each repository and inserts the results into the `git_commits` table.

The script handles several practical concerns:

- **Repository deduplication.** A repository might appear multiple times if it is checked out in multiple locations (for example, as a worktree in a workspace and again in the main code directory). The script deduplicates by repository path.
- **Commit metadata.** For each commit, the script collects the full hash, short hash, author, email, date, subject, body, branch, remote URL, and file statistics (insertions, deletions, files changed).
- **Stat parsing.** The script parses `git show --stat` output to extract insertion and deletion counts. This is done with regular expressions rather than machine-readable format strings because `git show --stat` does not have a stable machine-readable output format that includes both file names and counts in a single invocation.

The script collected 206 commits across 40 repositories for 2026-05-29. Of these, 9 repositories contained what we classify as "primary work streams"—projects where the commits reflect direct manual engineering effort rather than automated baseline rollout. The remaining 31 repositories contained commits from the B5 logcopter baseline rollout, an automated infrastructure update that touched many repositories at once.

#### 1.2 GitHub Pull Requests

The `12-collect-gh-prs.py` script uses the `gh` CLI to search for pull requests merged on the target date. It queries the `go-go-golems` and `wesen` organizations and inserts the results into the `github_prs` table.

The GitHub search API has constraints. The `--merged-at` filter is available, but the JSON output fields are limited. The script performs an initial search to get the PR number, title, repository, and URL, then runs `gh pr view` against each PR to collect the full body, addition/deletion statistics, changed file count, commit count, base branch, head branch, and author.

For 2026-05-29, the script collected 32 merged pull requests. The majority were B5 logcopter baseline PRs with identical bodies describing generated loggers, Makefile targets, and CI workflow upgrades. A smaller set were manual feature PRs with unique descriptions:

- `md-view#1`: Image resolution, copy-to-clipboard button, reMarkable upload, toolbar buttons.
- `remarquee#16`: Page selection for `rmdoc render-v6` and `rmdoc render-legacy`.
- `infra-tooling#15`: Refinement of the `open-gitops-pr` action and release process documentation.
- `publish-vault#2`: Media serving pipeline and configurable page titles.

#### 1.3 Pi Agent Sessions

The `14-collect-pi.py` script reads go-minitrace archives and inserts session metadata into the `pi_sessions` table. Pi sessions are stored as JSONL files under `~/.pi/agent/sessions/<slugged-cwd>/<timestamp>_<uuid>.jsonl`. The go-minitrace tool converts these JSONL files into `.minitrace.json` archives, which contain structured session metadata including start time, end time, duration, turn count, tool call count, agent framework, model, and working directory.

The script filters sessions by start date. For 2026-05-29, it found sessions in the `2026-04-21--pi-extensions` directory (a project that had active agent sessions on that date) and the `2026-05-07--md-server` directory.

### Stage 2: Storage

The storage layer is a sqlite database with five tables. The schema is managed by a migration script (`10-migrate-schema.py`) that tracks applied migrations in a `_migrations` table.

| Table | Purpose |
|---|---|
| `git_commits` | One row per commit. Stores hash, author, date, subject, body, stats, branch, remote. |
| `github_prs` | One row per pull request. Stores number, title, state, author, dates, body, stats, branches. |
| `pi_sessions` | One row per agent session. Stores id, framework, model, timing, turn counts, tool counts, cwd. |
| `tickets` | Placeholder for docmgr ticket metadata. |
| `ticket_docs` | Placeholder for docmgr document metadata. |

The schema is intentionally flat. There are no foreign keys between commits and PRs or between sessions and commits. The relationship between these entities is temporal, not structural: they all occurred on the same day. The query layer joins them by date when generating reports.

The choice of sqlite over a more complex database is deliberate. The data volume is small (hundreds of rows per day). Sqlite requires no server, no configuration, and no credentials. The database file can be inspected with the `sqlite3` CLI, backed up with `cp`, and archived alongside the ticket documentation.

### Stage 3: Rendering

The rendering stage has two parts: report generation and almanach layout rendering.

#### 3.1 Report Generation

The `20-generate-report.py` script queries the sqlite database and writes a markdown report. The report is structured for human readability, not machine parsing. It includes:

- A summary of commits by repository.
- A separation between primary work streams and automated baseline commits.
- Detailed commit lists for primary projects, with short hash, timestamp, and subject.
- GitHub PR summaries with author, stats, and body excerpts.
- Pi session summaries with turn counts and tool counts.
- A daily stats footer.

The report is not the final output. It is an intermediate artifact that can be reviewed, edited, or used as input for the almanach layout.

#### 3.2 Almanach Layout Rendering

The almanach-render-service reads a YAML layout file and produces a bitmap. The layout is not a generic document format; it is a domain-specific language for thermal paper pages. A layout consists of a header (version, theme, paper width, body scale, feed lines) and a list of blocks.

Each block has a type and a data dictionary. The block types are:

| Block Type | Purpose |
|---|---|
| `title` | Main title and subtitle. |
| `date` | Date and day of week. |
| `divider` | Horizontal rule. |
| `note` | Narrative text with a label and author. |
| `word` | Word of the day with definition. |
| `did` | Bulleted list of accomplishments. |
| `quote` | Quotation with attribution. |
| `image` | Embedded image with caption. |

The layout for 2026-05-29 uses `bodyScale: 1.6`, which enlarges the text for readability. The page is structured as four narrative notes (morning, midday, afternoon, evening), a word block, a did-list, a quote, daily stats, and an image. The narrative notes distill the raw commit data into prose paragraphs that describe what happened in each part of the day.

The rendering process works as follows:

1. The YAML layout is parsed into a JSON object.
2. A headless Chrome instance renders the JSON as HTML using the almanach Studio UI.
3. Chrome captures a screenshot of the rendered page at 384 pixels wide.
4. The screenshot is thresholded to black and white.
5. If the bitmap exceeds the printer's TCP receive limit (~38 KiB), it is split into segments.
6. Each segment is sent as a POST request to the printer's `/api/print/bitmap` endpoint.

The remote rendering service at `https://almanach.crib.scapegoat.dev` handles steps 2–6. The local CLI (`print-remote`) only needs to send the layout YAML.

## How the System Was Built

The system was built during a single agent session on 2026-05-30. The work was tracked in a docmgr ticket (`ALMANACH-20260529`) with a diary and changelog. The implementation proceeded through the following steps.

### Step 1: Schema Design

The first decision was the storage format. A sqlite database was chosen because it requires no infrastructure, supports structured queries, and produces a single file that can be archived. The schema was designed to capture the essential fields from each data source without over-normalizing. Each table has a natural key (commit hash, PR number, session ID) and a set of metadata fields.

The migration system uses a simple `_migrations` table to track which schema versions have been applied. This allows the schema to evolve without manual intervention.

### Step 2: Git Collection

The first attempt at git collection used an `awk` script to parse `git log --numstat` output. This approach failed because `git log` output is not reliably machine-parseable: commit messages can contain newlines, file names can contain spaces, and the `numstat` format changes depending on whether files are binary. The `awk` script produced corrupted rows with misaligned fields.

The fix was to use Python with `subprocess` to run `git log -1 --format=...` for each commit hash individually. This is slower than batch parsing, but it is correct. The script collects the full hash first, then iterates over hashes to collect metadata and statistics.

### Step 3: GitHub PR Collection

The GitHub CLI (`gh`) was used because it handles authentication and API pagination automatically. The initial script used `--merged-at` as a filter, but this required trial and error because the `gh search prs` JSON field set is limited and differs from the `gh pr view` field set. The final approach uses two-phase collection: first, search for PRs with basic fields; second, enrich each PR with `gh pr view` for full body and statistics.

### Step 4: Pi Session Collection

Pi sessions are stored in go-minitrace archives under `data/minitrace/`. The go-minitrace tool converts JSONL session files into `.minitrace.json` files with structured metadata. The collection script reads these JSON files directly with Python's `json` module and inserts rows into sqlite. This avoids the CSV parsing issues that plagued earlier attempts to pipe go-minitrace output into sqlite.

### Step 5: Report Generation

The report generator was designed to separate primary work from automated baseline noise. A repository is classified as a primary work stream if its name starts with a date (`2026-...`) or if it is one of a small set of known active projects (`md-server`, `remarquee`, `infra-tooling`, etc.). All other repositories with commits on the target date are classified as infra baseline. This heuristic is not perfect, but it is sufficient for daily use.

### Step 6: Almanach Layout

The layout was written by hand in YAML. The design goal was to produce a readable narrative rather than a data dump. Each note block corresponds to a part of the day and summarizes the commits from that time period in prose. The body scale of 1.6 was chosen to make the text readable on thermal paper without requiring a magnifier.

The image block embeds an owl engraving from the almanach image library as a base64 data URL. This avoids network dependencies during rendering. The image library is stored at `~/.pi/agent/skills/almanach-printing/images/` and contains 138 pre-cropped engravings.

### Step 7: Printing

The almanach was printed via the remote rendering service. The local CLI sent the layout YAML to `https://almanach.crib.scapegoat.dev/api/render-and-print`. The service rendered the layout, split the bitmap into 4 segments (because the total size exceeded the printer's TCP receive limit), and sent each segment to the printer at `192.168.0.126`.

## How to Use This System

Running the system for a new day requires the following steps.

1. **Create a ticket.** Use `docmgr ticket create-ticket` to create a new almanach ticket for the target date.
2. **Run the schema migration.** `python3 scripts/10-migrate-schema.py data/almanach.db`
3. **Collect git commits.** `python3 scripts/11-collect-git.py data/almanach.db`
4. **Collect GitHub PRs.** `python3 scripts/12-collect-gh-prs.py data/almanach.db` followed by `python3 scripts/13-enrich-prs.py data/almanach.db`
5. **Collect Pi sessions.** Convert Pi sessions with `go-minitrace convert pi`, then run `python3 scripts/14-collect-pi.py data/almanach.db`
6. **Generate the report.** `python3 scripts/20-generate-report.py data/almanach.db report.md`
7. **Write the layout.** Create `almanach-layout.yaml` by hand, using the report as input. Set `bodyScale` to `1.6` for readable text.
8. **Render and print.** `almanach-render-service print-remote --layout almanach-layout.yaml`

The system can be run for any date by changing the `SINCE` and `UNTIL` constants in the collector scripts. The date constants are hardcoded in each script; they are not parameterized. This is a deliberate choice: the scripts are designed to be read and modified, not to be a generic tool.

## How to Contribute

The system is intentionally small and modular. Contributions can take several forms.

### Adding New Data Sources

The sqlite schema has migration support. To add a new table—for example, `github_issues` or `discord_messages`—write a new migration in `10-migrate-schema.py` and a new collector script. The pattern is: run an external command or API, parse the output, insert rows into sqlite. The existing collector scripts (`11-collect-git.py`, `12-collect-gh-prs.py`, `14-collect-pi.py`) serve as reference implementations.

### Improving the Report Generator

The report generator currently uses a simple heuristic to separate primary work from automated baseline commits. A better approach would be to use commit message patterns, author filtering, or repository tagging. The generator is a single Python script (`20-generate-report.py`) that queries sqlite and writes markdown. Any improvement to the query logic or output format can be made there.

### Automating the Layout

The almanach layout is currently written by hand. A natural extension is to generate the layout automatically from the report or directly from sqlite. The almanach-render-service supports template variables (`{{key}}`) and data context files. A script could query sqlite, write a `data.yaml` context file, and render a template layout. This would eliminate the manual step of writing the layout.

### Adding a Web UI

The almanach-render-service has a Studio UI at `/almanach` that can be used to preview layouts. A web-based collector UI could run the collection scripts, display the results in a table, and let the user edit the layout before printing. This would turn the CLI pipeline into an interactive workflow.

## Next Steps

The system is functional but not yet reusable. The following improvements would make it suitable for daily use without manual intervention.

1. **Parameterize the date.** Replace hardcoded `SINCE`/`UNTIL` constants with a `--date` CLI argument. This would allow the system to be run for any date without editing scripts.
2. **Filter automated commits.** The B5 logcopter baseline produced 149 commits across 31 repositories on a single day. These commits have identical subjects and bodies. A filter that excludes commits matching known automated patterns would reduce noise.
3. **Generate the layout automatically.** Write a script that reads the sqlite database, classifies commits by time of day, and generates the narrative note blocks automatically. The generated layout would still need human review, but it would eliminate the blank-page problem.
4. **Schedule daily runs.** Use `cron` or `systemd` timer to run the collector at a fixed time each day. The printed almanach would be waiting when the user starts work.
5. **Archive old databases.** The sqlite database grows by a few hundred rows per day. After a month, it will contain thousands of rows. A compaction script could archive old data to a read-only database and start a new one for the current month.
6. **Add workspace detection.** The `wsm` tool knows which workspaces were active on a given date. Integrating `wsm list workspaces` into the collector would provide additional context: which projects were actively being worked on, not just which repositories had commits.

## Key Implementation Details

### Git Stat Parsing

The `git show --stat` output is parsed with regular expressions rather than with `git diff --numstat` because `--numstat` requires a second invocation and does not include the commit body. The regex handles three cases: insertions only, deletions only, and both insertions and deletions.

```python
import re

for line in stat_output.split('\n'):
    line = line.strip()
    if '|' in line:
        fname = line.split('|')[0].strip()
        files.append(fname)
        m = re.search(r'(\d+) insertion', line)
        if m:
            insertions += int(m.group(1))
        m = re.search(r'(\d+) deletion', line)
        if m:
            deletions += int(m.group(1))
```

This parser is brittle: if `git` changes the `--stat` output format, the parser will silently produce zeros. A more robust approach would use `git diff-tree --numstat` for the counts and `git log -1 --format=...` for the metadata separately.

### GitHub CLI JSON Field Mismatch

The `gh search prs` command accepts `--json` with a limited set of fields. The `mergedAt` field is not available in search output, only in `gh pr view` output. This means the collector cannot filter by merged date and retrieve full metadata in a single call. The two-phase approach (search then enrich) adds one API call per PR, which is acceptable for small result sets but would hit rate limits for larger ones.

### Minitrace Archive Structure

go-minitrace produces archives in the following structure:

```
<output-dir>/
  <session-slug>/
    active/
      <year-month>/
        <session-id>.minitrace.json
    manifest.json
```

The Pi session collector walks this tree with `glob` and filters by `started_at`. The session files contain the following top-level fields:

| Field | Type | Description |
|---|---|---|
| `id` | string | UUID of the session |
| `title` | string | Session title (often empty for Pi) |
| `environment.agent_framework` | string | `pi` or `codex` |
| `environment.model` | string | Model name (e.g., `claude-sonnet-4`) |
| `timing.started_at` | ISO8601 | Session start time |
| `timing.duration_seconds` | float | Total session duration |
| `metrics.turn_count` | int | Total turns |
| `metrics.tool_call_count` | int | Total tool calls |

### Thermal Printer Segmentation

The ESP32 printer firmware has a TCP receive limit of approximately 38 KiB. The almanach-render-service detects bitmaps larger than this limit and splits them into segments. Each segment is sent as a separate HTTP POST to `/api/print/bitmap`. Only the final segment carries the paper feed command. This is handled transparently by the render service.

## Related Notes

- [[PROJ - TTF VM Renderer]] — The primary project active on 2026-05-29, described in the almanach's evening note.
- [[PROJ - Infra Tooling]] — The release train and dashboard work described in the midday note.
- [[PROJ - Remarquee]] — The `rmdoc` page selection feature described in the almanach's did-list.
- [[ARTICLE - Almanach Render Service]] — Documentation for the rendering and printing service.
