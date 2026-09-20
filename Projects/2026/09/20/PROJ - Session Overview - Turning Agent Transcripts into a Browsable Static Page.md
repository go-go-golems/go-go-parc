---
title: Session Overview — Turning Agent Transcripts into a Browsable Static Page
aliases:
  - Session overview skill
  - go-minitrace summary page
  - agent transcript summary page
tags:
  - project
  - go-minitrace
  - transcripts
  - reporting
  - static-html
  - skills
status: implemented
type: project
created: 2026-09-20
project_date: 2026-09-20
repo: /home/manuel/.codex/skills
secondary_repos:
  - /home/manuel/code/wesen/go-go-golems/go-minitrace
ticket: SESSION-OVERVIEW-002
---

# Session Overview: Turning Agent Transcripts into a Browsable Static Page

A coding-agent transcript records everything a session did: every tool call, every file it touched, every message it exchanged with the model. The difficulty is not collecting this record. The difficulty is reading it. A long session can run to a thousand turns and several hundred tool calls, and the information a person actually wants — what was I asked to do, what did I finish, what is still open, and which files did that change — is distributed across the whole document.

This report describes a tool built to answer those questions for a set of sessions at once. It is a single Python script that shells out to `go-minitrace` for discovery and normalization, reads the normalized archives, and emits one self-contained interactive HTML page. No server is involved, and no network request is made by the page itself. The work is committed to `/home/manuel/.codex/skills` under ticket `SESSION-OVERVIEW-002`.

The report covers the data model of the archive, the extraction rules, the summary-block convention that Pi sessions emit, the per-checkpoint file delta algorithm, the rendering strategy, and the verification that was actually performed. It also records the measurement trap that made an earlier analysis wrong, because that trap is likely to catch the next person working with these archives.

> [!summary]
> - `go-minitrace` already discovers, converts, queries and serves agent transcripts; the missing capability was **synthesis into one shareable page**, so the tool was built as a thin layer over the existing normalized archives rather than a second ingestion pipeline.
> - Pi sessions emit `<summary>` checkpoints with four fixed fields. The tool parses all of them, shows the latest on each session card, and offers an expanded view to read every block; each block also carries the files written since the previous checkpoint.
> - A whole-file `grep '<summary>'` over an archive returns zero matches because Go's `encoding/json` writes `<` as `\u003c`. The data was present the entire time. Decoding the JSON is required.

## 1. The question the tool answers

Three separate questions look similar in conversation but need different machinery.

*Attribution* asks which session performed a specific piece of work, and whether it authored a particular commit. This is an evidence problem. The `go-minitrace-transcript-analysis` skill covers it: discover candidates, convert a narrow set, query the normalized tables for targeted operations, then verify against Git.

*Diagnosis* asks why one session struggled, or which documentation the agent consumed before failing. This is an analysis problem over tool calls, symbols and failure episodes, and the `transcript-doc-friction-analysis` skill covers it.

*Orientation* asks something simpler: given a set of sessions, what happened in each of them? This is a synthesis-and-presentation problem. It does not need SQL, and it does not need a hypotheses-first investigation. It needs a readable artifact that a person can scan, filter, search, and share.

`SESSION-OVERVIEW-002` built the third capability. The distinction matters because the first two skills already own the hard parts of ingestion and query semantics, and duplicating them would create a second definition of what a session contains.

## 2. What already existed, and what was actually missing

Before writing any code, the existing surface was inventoried, because building on it was the cheaper and more correct choice.

| Capability | Provided by | What it does | What it does not do |
|---|---|---|---|
| Native discovery | `go-minitrace discover pi\|codex\|claude-code` | Finds session files, reports `cwd`, start time and `last_activity_at` | Not a content index |
| Normalization | `go-minitrace convert …` | Produces `*.minitrace.json` archives with a stable schema | Does not summarize |
| Query | `go-minitrace query run` and `query commands` | SQL over `sessions`, `turns`, `tool_calls`, `files`, `metrics`, … | Returns rows, not a page |
| Service | `go-minitrace serve` | HTTP backend for a Transcript Explorer UI | Needs the frontend running |
| Frontend | `go-minitrace/web` (React, MUI, Redux) | Interactive exploration of one archive set | Not a single shareable file |

The gap was narrow and specific: there was no artifact that a person could open as a file, send to someone else, and read without any service running. The normalized archive already contained everything the page needed, so the tool reads archives directly instead of re-parsing native JSONL or re-implementing the query layer.

```mermaid
flowchart TD
    A[Native stores<br/>~/.pi, ~/.codex, ~/.claude] --> B[go-minitrace discover<br/>cwd + activity filter]
    B --> C[Source lists]
    C --> D[go-minitrace convert]
    D --> E[Normalized archives<br/>*.minitrace.json]
    E --> F[Extraction<br/>session / turns / tool_calls]
    F --> G[Summary parsing<br/>+ per-checkpoint deltas]
    G --> H[Embedded JSON<br/>data island]
    H --> I[Single static HTML<br/>interactive]
    I --> J[Browser, no server]
```

The tool occupies only the region from `E` onward. Everything above that boundary is delegated.

## 3. Four ways to give the tool its input

The tool exposes four input modes because the request "make a summary page for these transcripts" arrives in four different shapes.

| Mode | Flag | Use when |
|---|---|---|
| Workspace | `--workspace DIR` | The user wants every session that ran in one directory |
| Explicit files | `--source-session PATH` (repeatable) | The user names specific transcripts |
| A list file | `--source-list FILE` | A shortlist was produced by another step |
| Converted archives | `--from-glob GLOB` | Normalization already happened; skip it |

The first three require conversion, which requires knowing each transcript's framework. That is inferred from the path rather than asked for:

```python
def detect_framework(path: str) -> str | None:
    p = os.path.abspath(os.path.expanduser(path))
    if "/.pi/" in p or "/pi/agent/sessions/" in p:
        return "pi"
    if "/.codex/" in p:
        return "codex"
    if "/.claude/" in p:
        return "claude-code"
    return None
```

Discovery is a direct wrapper over the CLI, and it uses `--active-since` rather than `--since`. The distinction is not cosmetic: `--since` filters on start time and would silently miss a long-running session that began earlier and was still working inside the window. That is exactly the situation for a session left open across days.

```python
cmd = ["go-minitrace", "discover", fw,
       "--source-dir", os.path.expanduser(source_dirs[fw]),
       "--cwd-contains", fragment, "--output", "json"]
if since:
    cmd += ["--active-since", since]
```

Two properties of discovery are preserved into the output rather than smoothed over. First, `cwd` is a shortlist signal, not a content index: a session started in a parent directory, or one that began in one repository and later worked in this one, will not appear. Second, Codex converts to opaque `exec` wrappers, so its archives carry no per-file ledger. The page states "No structured file targets in this transcript" for those sessions instead of implying that no files changed.

Conversion writes into a temporary work directory, which is printed in the page's method note so the archive set is reproducible:

```python
work_dir = args.work_dir or tempfile.mkdtemp(prefix="session-overview-")
```

The scratch directory is deliberately not deleted. Reproducing a page requires the archives it was built from, and a temp path that vanishes after the process exits makes the artifact unreproducible.

## 4. The archive document

An archive is a single JSON object. The tool reads six of its regions.

| Region | Fields used | Why |
|---|---|---|
| `id` | session id | Card identity and anchor |
| `environment` | `agent_framework`, `model` | Framework colour and model label |
| `timing` | `started_at`, `ended_at`, `active_duration_seconds` | Ordering and duration |
| `operational_context` | `working_directory`, `git_branch` | Footer and provenance |
| `metrics` | `turn_count`, `tool_call_count` | Meta row |
| `turns` | `index`, `timestamp`, `role`, `content` | Task, final report, summary blocks |
| `tool_calls` | `operation_type`, `emitting_turn_index`, `input.file_path` | File ledger and deltas |
| `provenance` | `source_path` | Traceability to the native file |

The shape of `turns` is what makes most of the page possible. A turn carries a role, a monotonically increasing `index`, a `timestamp`, and the message content. Assistant content is where the agent's own summary checkpoints live, embedded in the text.

Two extraction rules turn that raw sequence into the card's headline text. The first is a noise filter, because the earliest user turn in many sessions is not the user's request at all:

```python
NOISE_PREFIXES = (
    "<local-command", "<command-name", "<command-message",
    "<system-reminder", "<user_info>", "[REMINDER]",
    "# AGENTS.md instructions", "Caveat:",
)
```

These appear because the harness injects command output, extension reminders and environment metadata into the same stream the model sees. Without the filter, the first card in the earlier prototype read `Set model to Opus 5 (1M context)` instead of the actual task.

The second rule selects the task and the final report: the first user turn that survives the noise filter, and the last assistant turn of at least forty characters. The length threshold exists to skip one-line acknowledgements such as "I'll start by finding the ticket."

Both are heuristics and are labelled as such on the page. The final message is presented under the heading *Final report (agent's claim)*, because an agent's statement that work is complete is a claim, not verification.

## 5. The summary-block convention

Pi sessions emit a structured checkpoint at the end of most responses. The convention is imposed by an extension rather than by the model's own preference. The extension appends a reminder to every user prompt and injects an instruction into the system prompt:

```
=== MANDATORY SESSION SUMMARY RULE ===

At the VERY END of every response, after all tool calls and all text, you MUST
output exactly one <summary>...</summary> block.
```

The required body has four headings in a fixed order: `This turn:`, `Session so far:`, `Issues:`, `Next steps:`. The extension that defines this lives at `~/.pi/agent/extensions/session-summary` and parses the block back out with `fullText.matchAll(/<summary>([\s\S]*?)<\/summary>/gi)` to drive a terminal widget.

Because the reminder is Pi-specific, the convention appears **only** in Pi transcripts. That is a measurable property of the corpus, not an assumption:

| Framework | Sessions | Summary blocks | File targets |
|---|---:|---:|---:|
| Pi | 5 | 117 | 447 |
| Claude Code | 8 | 0 | 223 |
| Codex | 4 | 0 | 0 |

A tool that reported summaries for Claude or Codex sessions would be inventing them. Counts of zero are the correct output, and the page's `has summary` filter narrows 17 sessions to 4.

### 5.1 Parsing the four fields

The parser walks the body line by line. A line matching `Name: value` whose name is one of the four known fields opens a section; subsequent lines append to that section until another field begins. Text that appears before any recognised field is kept separately rather than discarded.

```python
SUMMARY_FIELDS = ("this turn", "session so far", "issues", "next steps")

def parse_summary_block(block: str) -> tuple[dict[str, str], str]:
    sections = {key: [] for key in SUMMARY_FIELDS}
    fallback: list[str] = []
    current: str | None = None
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"^([A-Za-z][A-Za-z ]*?):\s*(.*)$", line)
        key = match.group(1).strip().lower() if match else None
        if key in sections:
            current = key
            rest = match.group(2).strip()
            if rest:
                sections[current].append(rest)
        elif current:
            sections[current].append(line)
        else:
            fallback.append(line)
    return ({k: " ".join(v) for k, v in sections.items()}, " ".join(fallback))
```

The fallback branch is not defensive padding. Free-prose summaries do occur, and a parser that returned nothing for them would silently drop real content. The block is stored either way, and the renderer chooses between the field grid and the paragraph.

### 5.2 A measurement trap worth recording

An earlier investigation in this same line of work concluded that no summary blocks survived conversion, because this command returned nothing:

```bash
grep -o '<summary>' analysis/pi/active/*/*.minitrace.json | wc -l
# 0
```

The conclusion was wrong. `go-minitrace` is written in Go, and Go's `encoding/json` escapes `<`, `>` and `&` by default so that JSON can be embedded safely in HTML. The bytes on disk contain `\u003csummary\u003e`, not `<summary>`.

```bash
grep -c 'u003csummary' analysis/pi/active/2026-09/*01a077ba*.minitrace.json
# 117
```

Decoding the JSON restores the original text, which is why the Python extraction finds every block. Two lessons follow. First, a zero from `grep` on a serialized format is a statement about the serializer as much as about the data. Second, when a structured format is involved, the reliable check is to decode and inspect, not to pattern-match the bytes.

The same effect explains why `grep -l 'Session so far'` *did* match while `grep -o '<summary>'` did not: the field names are plain ASCII, and only the angle brackets are escaped.

## 6. Per-checkpoint file deltas

The card shows the session-wide file ledger. The expanded view answers a different question: what changed *between* checkpoints.

The rule is stated as a half-open interval. A summary block emitted at turn *N* owns every `NEW` or `MODIFY` tool call whose `emitting_turn_index` is greater than the previous block's turn and less than or equal to *N*. The first block owns everything before it, because there is no previous checkpoint.

```mermaid
flowchart LR
    T0[turn 0] --> A["block 1<br/>owns writes ≤ turn_a"]
    A --> T1[turn a] --> B["block 2<br/>owns writes in (a, b]"]
    B --> T2[turn b] --> C["block 3<br/>owns writes in (b, c]"]
```

The implementation is deliberately conservative in what it accepts:

```python
for tc in tool_calls:
    if tc.get("operation_type") not in ("NEW", "MODIFY"):
        continue
    path = tool_input_path(tc)
    turn = tc.get("emitting_turn_index")
    if not path or not isinstance(turn, int) or isinstance(turn, bool):
        continue
    events.append((turn, shorten(path, prefixes), tc["operation_type"]))
```

A tool call is used only when it has both a resolved file path and a usable turn index. Anything else is skipped. The consequence is that a delta can understate what changed; it cannot invent a file. That direction of error is the correct one for a report, because an omitted file is a known incompleteness while a phantom file is a false statement.

The `isinstance(turn, bool)` guard is not decoration. In Python, `bool` is a subclass of `int`, so `True` passes an `isinstance(x, int)` test and would be attributed to turn 1. The guard costs one clause and removes an entire class of silent misattribution.

Measured on the working corpus, the deltas behave as the model predicts. Sessions whose final message is summary-only end with an empty delta, because no writes occurred after the last real checkpoint. Sessions that end mid-work carry their final increments:

| Session | Blocks | Sum of deltas | Final block delta |
|---|---:|---:|---:|
| Kernel study (`01a0630e`) | 3 | 5 | 4 |
| Identity cutover (`01a0686e`) | 37 | 119 | 15 |
| PicoCalc native (`01a06d83`) | 43 | 356 | 0 |
| TTC SQL + PBUI visual (`01a077ba`) | 34 | 232 | 0 |

The two zeroes are real. In both sessions the agent's last response was a summary block and nothing else, so there was nothing to attribute.

## 7. Rendering: one file, no server

The output is a single HTML document with three parts: a CSS block, a static DOM skeleton, and a `<script>` containing the session records as a JSON literal. Regenerating the page rewrites the data island and leaves the template untouched.

The data is embedded rather than fetched, which is why the page opens from `file://`. The embedding has one requirement that is easy to miss: a JSON string containing `</script>` would terminate the script element early. The tool escapes the three characters that matter:

```python
data = json.dumps(sessions, ensure_ascii=False)
data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
```

This is the same escaping Go applies, for the same reason. A file path or a prompt containing an angle bracket is otherwise enough to break the page.

The interactive layer is plain DOM manipulation with no framework and no dependencies. Its state is one object:

```javascript
const state = { q:"", fw:new Set(FW), filesOnly:false, summariesOnly:false,
                sort:"time-asc", open:new Set(), expandAll:false };
```

Because filtering re-renders the card list from the embedded data, every derived view is consistent by construction. The counter, the sidebar index, and the visible cards are all computed from the same filtered array in a single pass, so they cannot disagree.

### 7.1 What the page exposes

| Control | Effect |
|---|---|
| Search | Filters on title, task, final message, model, branch, **summary text**, and file paths; highlights matches |
| Framework chips | Toggle `claude-code` / `pi` / `codex` independently |
| Sort | Oldest, newest, most files, most turns |
| `has files` | Sessions with a structured file ledger |
| `has summary` | Sessions with parsed summary blocks |
| `expand files` | Opens every per-session ledger |
| `browse all N` | Opens the expanded summary modal |
| Click a path or session id | Copies it to the clipboard |

The summary modal is the piece the request specifically asked for. It presents the block list on the left, each entry showing its `This turn` line and timestamp, and the selected block's full fields plus its file delta on the right. Navigation is by click, by `prev`/`next`, and by `ArrowUp`/`ArrowDown`; `Escape` and a backdrop click close it.

![Session card showing the latest parsed summary with its four fields and the checkpoint file count](_assets/session-overview-latest-summary.png)

The card places the summary between the task and the free-form final report. That ordering is deliberate: the structured checkpoint is the concise statement, and the final report is the noisier text that often repeats it.

![Expanded modal listing every summary block for one session, with the selected block's fields on the right](_assets/session-overview-browse-blocks.png)

Handling two keyboard layers required an explicit guard. The document-level handler owns `/` for search and `Escape` for clearing it; once a modal is open, both keys must defer to the modal. The handler early-returns while the overlay is visible:

```javascript
if(!$("#overlay").hidden){
  if(e.key === "Escape"){ e.preventDefault(); ovClose(); }
  else if(e.key === "ArrowDown"){ e.preventDefault(); ovSelect(ovIndex+1); }
  else if(e.key === "ArrowUp"){ e.preventDefault(); ovSelect(ovIndex-1); }
  return;
}
```

![Block detail showing the files written since the previous checkpoint, with NEW and MODIFY badges](_assets/session-overview-files-since-last.png)

## 8. Verification

The tool was exercised through all four input modes and inspected in a browser. These are the checks that were actually run, with their results.

| Check | Command or action | Result |
|---|---|---|
| Archive mode | `--from-glob '/tmp/ws-minitrace/analysis/*/active/*/*.minitrace.json'` | 17 sessions, 670 file targets, 117 summary blocks |
| Workspace mode | `--workspace …/add-plot-editor --framework pi --active-since 2026-09-20` | discover → convert → render, 2 sessions |
| Explicit source | `--source-session ~/.claude/projects/…/fe03313e….jsonl` | 1 converted Claude session |
| JSON sidecar | `--json /tmp/so-final.json` | 117 blocks over 4 sessions; deltas sum to 5 / 119 / 356 / 232 |
| Search | query `picoCalc` | 2 of 17 sessions |
| Framework filter | toggle `codex` off | 13 of 17 sessions |
| `has files` | click | 8 of 17 sessions |
| `has summary` | click | 4 of 17 sessions |
| Modal | open PicoCalc card | 43 blocks, selected 43 of 43, four fields rendered |
| Keyboard | `ArrowUp` | selection moved to 42 of 43, detail pane updated |
| Close | `Escape` | modal hidden, `overflow:hidden` released from `<body>` |
| Syntax | `python3 -m py_compile` | clean |

Two failures during development are worth recording because they were diagnosis problems rather than code defects.

The first was a Playwright strict-mode violation: `locator('.sum-open') resolved to 4 elements`. The page had four sessions with summaries and therefore four matching buttons. The selector was wrong, not the page. Selecting by the session id fixed it.

The second was the initial report that the modal did nothing. In fact the modal opened and closed correctly; the assertion had clicked a button belonging to a different session than the one it then inspected. Both incidents are the same category of error: an assertion that was too loose to distinguish between the states it was meant to test.

## 9. What the tool does not establish

A page like this invites over-reading, so its limits are stated on the page itself and repeated here.

**File targets are tool-call evidence, not authorship.** A `NEW` or `MODIFY` operation records that the agent invoked a write against a path. It does not prove the file changed, that the change persisted, or that no other process touched it. Verifying that requires Git.

**Codex sessions expose no ledger.** Four of the seventeen sessions normalize only as `exec` wrappers. Their zero file counts are a property of the adapter, not of the work performed.

**Four Claude sessions show zero structured targets** even though they wrote files, because those edits occurred inside shell heredocs that the adapter does not decompose.

**Summary fields are parsed leniently.** A field name appearing in ordinary prose could open a section. The parsed result is in the JSON sidecar, so it can be checked against the transcript before being quoted.

**The modal is not fully accessible.** It sets `role="dialog"` and `aria-modal="true"` and moves focus to the close button, but it neither traps focus nor restores it to the calling button on close.

**Selection is by recorded working directory.** The workspace mode cannot see a session that started elsewhere.

**The page is a snapshot.** It renders the archives it was given. It does not re-read the native stores, and it does not detect that a session has continued since conversion.

## 10. An operational observation about the summary pipeline

While locating the parser, a diagnostic log at `~/.pi/agent/logs/session-summary.log` was found to be approximately 192 MiB. The extension appends a JSON line for every turn, including a 500-character tail of the message text, and never rotates the file.

The extension also logs a running count of turns where no summary block was found. That counter is not evidence that the model omitted the block. `turn_end` fires for interim assistant responses that contain only thinking and a tool call, and those have no final text yet. A turn that ends in a tool call legitimately produces zero matches. Reading the counter as a compliance rate would overstate the number of missing summaries.

## 11. Commits and ticket

The work was carried out under ticket `SESSION-OVERVIEW-002` in `~/.codex/skills`, with four code checkpoints and one documentation checkpoint.

| Commit | Contents |
|---|---|
| `6aa8c20` | `parse_summary_block`, `extract_summaries`; summary counts in stdout |
| `f7b9984` | Latest-summary card section, meta badge, `has summary` filter, summary-aware search |
| `d56af49` | Expanded modal browser with list/detail, prev/next and keyboard navigation |
| `1205e2e` | `attach_summary_files` and the per-checkpoint delta list; `SKILL.md` documentation |
| `80d8f27` | Diary, changelog, tasks, physical slip receipts, vocabulary entries |

The ticket carries an investigation-format diary at `ttmp/2026/09/20/SESSION-OVERVIEW-002--summaries-in-the-session-overview-page/reference/01-implementation-diary.md` recording the prompts verbatim, the Go escaping trap, the Playwright selector failure, and the `bool`/`int` guard. Nine physical slips — one plan plus START/DONE for each of four phases — were printed and archived with their receipts.

## 12. Reproducing the page

```bash
S=~/.pi/agent/skills/session-overview/scripts/session_overview.py

# every session that ran in a workspace
python3 "$S" --workspace /home/manuel/workspaces/2026-09-01/add-plot-editor \
  --active-since 2026-09-01

# explicit transcripts, framework inferred from each path
python3 "$S" --source-session ~/.pi/agent/sessions/--slug--/abc.jsonl

# an existing archive set, no conversion
python3 "$S" --from-glob './analysis/*/active/*/*.minitrace.json' --no-open
```

The default output is `~/tmp/session-overview-<slug>.html`, opened in a browser unless `--no-open` is passed. `--json` writes the extracted records beside it, which is the artifact to inspect when a claimed count needs checking.

## 13. What would come next

Four follow-ups are implied by the current state rather than invented.

Deduplicating the embedded summary from the final report would remove the one visible redundancy on the card, at the cost of deciding which of the two is canonical when they disagree.

Trap and restore focus in the modal, which is a contained change.

Parsing nested `<summary>` blocks inside thinking content, if any sessions are found that place them there rather than in the final text.

Adding a generated-at timestamp and archive fingerprint to the page footer, so a snapshot can be identified rather than merely dated by its file mtime.

The deeper conclusion is about layering. The expensive parts of this problem — discovering sessions, normalizing three different transcript formats into one schema, and querying them — were already solved by `go-minitrace`. The missing piece was a presentation layer of roughly nine hundred lines that reads the normalized form and emits a file. Building it that way meant the tool inherited every correctness property of the existing pipeline, including its known limitations, instead of silently re-deriving them.
