---
title: "PROJECT REPORT - Seeding go-go-datadrop and go-go-goja Instrumentation from ChatGPT Conversations"
aliases:
  - Seeding Repos from ChatGPT Conversations
  - go-go-datadrop setup report
  - GOJA-069 instrumentation setup report
  - docmgr ticket seeding from surf transcripts
tags:
  - project
  - surf-go
  - surf-cli
  - chatgpt
  - docmgr
  - go-go-golems
  - go-template
  - browser-automation
  - data-extraction
status: active
type: project
created: 2026-07-24
repo: /home/manuel/code/wesen/go-go-golems/go-go-datadrop
---

# PROJECT REPORT - Seeding go-go-datadrop and go-go-goja Instrumentation from ChatGPT Conversations

This report documents a two-part workflow performed on 2026-07-24: bootstrapping a new `go-go-golems` Go binary repository from the `go-template` GitHub template, and seeding two repositories with design material retrieved from prior ChatGPT conversations using the `surf` CLI. The goal is to make the entire pipeline legible: how a template is normalized into a named project, how a ChatGPT conversation's transcript and attached files are pulled into a docmgr ticket's `sources/` directory, and where the tooling breaks down and requires workarounds.

The report covers two concrete deliverables. The first is `go-go-datadrop`, a brand-new repository created from a template and seeded with the "Open Source Wolfram Datadrop" conversation. The second is `go-go-goja`, an existing repository where ticket `GOJA-069` was created and seeded with the "JavaScript Interpreter Instrumentation" conversation. Both follow the same shape — create a docmgr ticket, download a transcript, download attached files, reorganize the files into clean paths, write a design doc scoped to a first milestone — but the two conversations exposed different failure modes in the retrieval tooling.

> [!summary]
> The work combines three tools into one seed-and-document pipeline:
> 1. **The `go-go-golems/go-template` GitHub template** is cloned, then normalized by replacing placeholder names (`XXX`, `go-go-golems.XXX`, `GO GO TEMPLATE`) across the module path, Makefile, goreleaser config, command directory, and logcopter prefix, until a placeholder scan returns no matches.
> 2. **The `surf` CLI** drives the ChatGPT backend API from inside the page context to list conversations, render a transcript to Markdown, and download every attached file. Two tooling failure modes appeared and were worked around: tab ids print in scientific notation and must be coerced to integers, and the file inventory is empty until the tab is navigated to the conversation URL.
> 3. **`docmgr`** creates a ticket workspace, receives the imported sources, and is validated with `docmgr doctor` after missing vocabulary slugs are added.

## Why this project exists

A research design conversation in ChatGPT produces dense, valuable material: full design documents, code-interpreter artifacts, rendered monographs, reference source tarballs. That material is locked inside a browser tab unless it is deliberately extracted. The two repositories here are the start of implementation work, and each needs to begin from the design that was already produced rather than re-deriving it from scratch.

`go-go-datadrop` is a new server for storing research data, modeled on Wolfram's Data Drop. The design conversation produced an 11,000-word design document, a browser-PDS architecture amendment, and a working Go reference slice built on `go-go-golems/tiny-idp`. None of that should be lost or re-done.

`go-go-goja` is the go-go-golems JavaScript interpreter, and the instrumentation work adds an eBPF-style probe layer to the goja runtime. The design conversation produced an engineering design and a 52-page research monograph formalizing the semantics. That monograph is the evidence base for every scope decision in the first milestone.

The shared need is identical: take a conversation id, pull its transcript and all its files into a docmgr ticket's `sources/` directory, and write a design doc that scopes the first implementation milestone from the retrieved material. The pipeline must be deterministic enough to repeat, because the same shape will be applied to future conversations.

## Part 1 — Bootstrapping go-go-datadrop from the go-template

The `go-go-golems` organization maintains a template repository, `go-go-golems/go-template`, that bootstraps a new Go binary with a Makefile, logcopter integration, goreleaser config, golangci-lint, lefthook hooks, and GitHub Actions. The template uses placeholder names that must be replaced before feature work begins.

### Template creation and clone

The repository is created from the template without cloning through `gh`, then cloned explicitly into the standard code directory:

```bash
gh repo create go-go-golems/go-go-datadrop \
  --public \
  --template go-go-golems/go-template \
  --clone=false \
  --description "Server to store your research data"

cd /home/manuel/code/wesen/go-go-golems
gh repo clone go-go-golems/go-go-datadrop
cd go-go-datadrop
wsm discover .
```

`wsm discover .` registers the new repository in the workspace manager's repository registry. It reported 367 repositories discovered, confirming the new clone was recognized.

### Normalizing placeholders

The template ships with placeholder names scattered across configuration files. A placeholder scan before normalization returns matches in the module path, the logcopter generate directive, the Makefile, the goreleaser config, and the README:

```
./go.mod:1:module github.com/go-go-golems/XXX
./logcopter_generate.go:3:... -area-prefix go-go-golems.XXX -strip-prefix github.com/go-go-golems/XXX ./pkg/...
./Makefile:70:XXX_BINARY=$(shell which XXX)
./Makefile:72: GOWORK=off go build -o ./dist/XXX ./cmd/XXX && \
./.goreleaser.yaml:1:project_name: XXX
./README.md:1:# GO GO TEMPLATE
```

These are replaced with a script that performs ordered substitutions, the more specific patterns first so that `github.com/go-go-golems/XXX` is replaced before a bare `XXX` catch-all:

| Template value | Replacement |
|---|---|
| `github.com/go-go-golems/XXX` | `github.com/go-go-golems/go-go-datadrop` |
| `go-go-golems.XXX` | `go-go-golems.go-go-datadrop` |
| `XXX_BINARY` | `GO_GO_DATADROP_BINARY` |
| `./cmd/XXX` | `./cmd/go-go-datadrop` |
| `./dist/XXX` | `./dist/go-go-datadrop` |
| `GO GO TEMPLATE` | `go-go-datadrop` |
| `package XXX` | `package go_go_datadrop` |

The command directory is moved with `git mv cmd/XXX/main.go cmd/go-go-datadrop/main.go` so the rename is tracked as a move rather than a delete-plus-add. After edits, a second placeholder scan confirms no matches remain outside `ttmp/`:

```bash
rg -n "XXX|go-template|GO GO TEMPLATE" . --glob '!ttmp/**' --glob '!.git/**'
# (no output)
```

### docmgr initialization and the bootstrap commit

`docmgr init --root ttmp --seed-vocabulary` creates the `ttmp/` documentation root, a `.ttmp.yaml` config, and a seeded vocabulary. A common failure mode is staging only `ttmp/` and leaving `.ttmp.yaml` uncommitted, so both are staged together:

```bash
docmgr init --root ttmp --seed-vocabulary
git add .ttmp.yaml ttmp AGENT.md Makefile README.md go.mod go.sum logcopter_generate.go pkg cmd .goreleaser.yaml
git commit -m "Initialize go-go-datadrop project"
```

Validation uses `GOWORK=off go test ./...` rather than plain `go test`, because inside a workspace an outer `go.work` can pull in modules requiring a newer Go version and break the test run. With `GOWORK=off`, the repository is validated in isolation.

### Forking to wesen and remote layout

The convention keeps `origin` pointed at the upstream `go-go-golems` repository and adds a `wesen` fork as a second remote:

```bash
gh repo fork go-go-golems/go-go-datadrop --remote=false --clone=false
git remote add wesen git@github.com:wesen/go-go-datadrop.git
git push wesen main
```

The module path stays under `github.com/go-go-golems/go-go-datadrop`. It is never rewritten to `github.com/wesen/...`. The result of this part is a repository at `/home/manuel/code/wesen/go-go-golems/go-go-datadrop` with two remotes, a clean build, and a docmgr workspace initialized.

## Part 2 — The surf retrieval pipeline

Both tickets are seeded with the same retrieval pipeline. The pipeline has four stages: find the conversation, download the transcript, navigate the tab and download files, reorganize the files into clean paths. The `surf` CLI drives the ChatGPT backend API from inside the page context, the same approach documented in [[PROJECT REPORT - surf-go ChatGPT File Downloader - Driving the Backend API Through the Page Context]].

### Finding a conversation by title and date

The ChatGPT backend exposes a conversations list at `/backend-api/conversations?order=updated`. It is queried by executing JavaScript inside the open chatgpt.com tab via `surf js`:

```bash
surf js --tab-id "$TAB_ID" --timeout-ms 30000 "
const s = await fetch('/api/auth/session', {credentials: 'include'});
const token = (await s.json()).accessToken;
const r = await fetch('/backend-api/conversations?offset=0&limit=100&order=updated', {
  credentials: 'include', headers: { Authorization: 'Bearer ' + token },
});
const j = await r.json();
const items = j.items || [];
return items.map(it => (it.update_time||'').slice(0,10) + ' | ' + it.id + ' | ' + (it.title||'Untitled')).join('\n');
"
```

The script obtains an `accessToken` from `/api/auth/session`, uses it as a bearer token, and returns a newline-joined list of date, conversation id, and title. The conversation id is the UUID in the `/c/<id>` URL and is the input to the transcript and download commands.

### The tab id scientific notation failure

The first failure mode appears at this stage. `surf tab list` emits its output in a YAML-ish format where the `id:` field is a floating-point number in scientific notation:

```
- active: false
  id: 4.41401394e+08
  title: Notifications
```

The `surf js --tab-id` flag parses its argument with `strconv.ParseInt`, which rejects scientific notation:

```
Error: invalid argument "4.41401427e+08" for "--tab-id" flag:
strconv.ParseInt: parsing "4.41401427e+08": invalid syntax
```

The fix is to coerce the id to a plain integer before passing it. The archive skill's awk extraction yields the float string, so a Python one-liner converts it:

```bash
TAB_ID=$(surf tab list 2>/dev/null | python3 -c "
import sys, re
txt = sys.stdin.read()
for b in txt.split('- active'):
    if 'url: https://chatgpt.com/' in b:
        m = re.search(r'id:\s*([0-9.e+]+)', b)
        if m: print(int(float(m.group(1)))); break
")
```

This produces `441401427`, which `--tab-id` accepts. The failure is silent in the sense that `surf tab list` succeeds; it is the downstream `surf js` call that errors. Any workflow that extracts a tab id from `surf tab list` and passes it to another subcommand must perform this coercion.

### Downloading the transcript

The transcript is downloaded with `surf chatgpt transcript --from-api`, which fetches the conversation JSON from `/backend-api/conversation/{id}` and renders it to Markdown:

```bash
surf chatgpt transcript --from-api \
  --conversation-id "$CID" \
  --tab-id "$TAB_ID" \
  --export-file sources/open-source-wolfram-datadrop-transcript.md
```

The `--from-api` mode is more reliable than the default DOM scraping, because it reads the canonical conversation JSON rather than depending on the rendered page structure. The output is a Markdown file where user turns are blockquotes and assistant turns are prose with collapsible thinking traces and fenced code blocks.

### The file inventory navigation requirement

The second failure mode appears when listing and downloading files. `surf chatgpt download --conversation-id <id> --list` queries the same backend API, but with only the chatgpt.com root page open, it returns an empty inventory:

```
Conversation: 6a627dd1-0dbc-83ea-a80f-4fac74f8610a
Inputs: 0
Outputs: 0
```

The inventory populates only after the tab is navigated to the conversation URL. The `surf navigate` verb does not accept a trailing URL positional in this version (`Error: Too many arguments`), so navigation is performed by setting `window.location.href` through `surf js`:

```bash
surf js --tab-id "$TAB_ID" --timeout-ms 30000 "
window.location.href = 'https://chatgpt.com/c/${CID}';
return 'navigating';
"
sleep 5
surf chatgpt download --conversation-id "$CID" --tab-id "$TAB_ID" --list
```

After navigation, the same `--list` call returns the full inventory. For the datadrop conversation, this was 1 input and 12 outputs. For the goja conversation, it was 32 inputs and 2 outputs. The cause is that the file extraction walks the conversation's message tree, and the tree is only fully populated in the backend's response when the conversation is the active context. Running the download against the chatgpt.com root does not resolve the conversation's file references.

### Downloading all files

Once the inventory is populated, `surf chatgpt download` fetches every file:

```bash
surf chatgpt download \
  --conversation-id "$CID" \
  --tab-id "$TAB_ID" \
  --output-dir sources/
```

The command writes files into a per-conversation subdirectory named after the conversation id, and it mangles filenames by concatenating the original path with a hash suffix. A `manifest.json` records the mapping between original names and downloaded filenames. Two distinct download outcomes appeared across the two conversations.

### The expired download URL failure

The datadrop conversation had 12 output files, but 7 of them returned `no download_url`:

```
[output] tinyidp-opendrop-git-format.patch — no download_url
[output] tinyidp-opendrop-full.bundle — no download_url
[output] tinyidp-opendrop-DELIVERY.md — no download_url
```

These are code-interpreter artifacts whose signed download URLs had expired or were never resolvable. They were not retriable. The 5 files that did download included the essential design documents and the reference source tarball, and the tarball's contents (`BUILD-REPORT.md`, `APPLY.md`, `VALIDATION.txt`, `MANIFEST.txt`) covered the same delivery and validation material as the missing files. No information was actually lost.

The goja conversation had no such failures: all 34 files (32 input PNGs and 2 monograph outputs) downloaded successfully.

## Part 3 — Reorganizing downloaded files into clean paths

The downloaded file layout is not directly usable. Files land in a conversation-id subdirectory with hashed names, and the manifest is a side artifact. The reorganization step flattens the structure and recovers clean names.

### The datadrop reorganization

For `go-go-datadrop`, the conversation had 5 downloadable files with distinct, recognizable names. They were moved out of the conversation-id subdirectory into `sources/` directly, the input screenshot was renamed to `probe_status.png`, and the empty subdirectory and manifest were removed:

```bash
mv "$CONV_DIR/opendrop-design.md" "$SOURCES/opendrop-design.md"
mv "$CONV_DIR/opendrop-browser-pds-profile.md" "$SOURCES/opendrop-browser-pds-profile.md"
mv "$CONV_DIR/opendrop-pod-mvp.zip" "$SOURCES/opendrop-pod-mvp.zip"
mv "$CONV_DIR/tinyidp-opendrop-source.tar.gz" "$SOURCES/tinyidp-opendrop-source.tar.gz"
mv "$CONV_DIR/user-...probe_sta.png-65d9c654" "$SOURCES/probe_status.png"
rm -rf "$CONV_DIR"
rm -f "$SOURCES/manifest.json"
```

### The goja reorganization via manifest parsing

For `go-go-goja`, the 32 input files were page images whose original paths encoded a directory structure: `_semantic_probes_work/render/page-38.png` and `_semantic_probes_work/render_final/page-39.png`. The downloaded filenames were mangled to a hash-suffixed form, so the manifest was parsed to recover the original path and move each file to a clean location:

```python
import json, os, shutil
manifest = json.load(open(os.path.join(sources_dir, "manifest.json")))
for f in manifest["files"]:
    name = f.get("name", "")
    if "_semantic_probes_work/" in name:
        rel = name.split("_semantic_probes_work/", 1)[1]   # render/page-38.png
        dest = os.path.join(sources_dir, "semantic-probes-pages", rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(f["downloaded_path"], dest)
```

This moved the 32 PNGs into `sources/semantic-probes-pages/render/` (pages 38–55) and `sources/semantic-probes-pages/render_final/` (pages 39–52), recovering the two render passes as separate directories. The two monograph outputs were moved to `sources/` directly. The conversation-id subdirectory and manifest were then removed.

The manifest is the source of truth for the original path. Without parsing it, the hashed filenames cannot be reliably mapped back to their semantic names, and the directory structure (`render` vs `render_final`) would be lost.

## Part 4 — Creating the docmgr ticket and writing the design doc

Both repos use the same ticket creation flow. The ticket is created with a topic set, which seeds the standard directory layout (`design/`, `reference/`, `sources/`, `scripts/`, `archive/`, `various/`, `playbooks/`) plus an `index.md`, `tasks.md`, and `changelog.md`.

### Ticket numbering conventions

The two repos use different numbering conventions. `go-go-datadrop` is a fresh repo with no prior tickets, so the first ticket is `DATADROP-1`. `go-go-goja` is an established repo with 147 existing tickets following a `GOJA-NNN` convention; the highest existing number was `GOJA-068`, so the new ticket is `GOJA-069`. The next number is found by sorting all existing ticket numbers numerically and taking the maximum plus one.

### docmgr doctor and vocabulary

After writing the ticket docs, `docmgr doctor --ticket <id> --stale-after 30` validates frontmatter and vocabulary. Both runs initially produced `unknown_topics` warnings for slugs not in the repo's vocabulary. Missing slugs are added before re-running:

```bash
docmgr vocab add --category topics --slug mvp --description "Minimum viable product slice"
docmgr vocab add --category topics --slug server --description "HTTP/API server component"
docmgr doctor --ticket DATADROP-1 --stale-after 30
# → ✅ All checks passed
```

The goja repo's vocabulary was already large (it listed 75 known topics), so only `instrumentation` and `design` needed adding. The datadrop repo's vocabulary was freshly seeded and needed `mvp`, `server`, and `design`.

### The design doc shape

Each ticket gets a design doc that scopes the first milestone from the retrieved sources. The doc follows a consistent shape: an executive summary, a problem statement with explicit in-scope and out-of-scope lists, a current-state architecture section that summarizes the source artifacts, a gap analysis table, a proposed architecture with draft data models or interfaces, decision records, a phased implementation plan, a testing strategy, risks, and a references list pointing back to the `sources/` files.

The decision records are the most important part. Each records context, options considered, the decision, the rationale, consequences, and a status. For `go-go-datadrop`, the key decision was building a standalone binary rather than reusing the `tinyidp-opendrop` reference slice, because the reference slice is bound to TinyIDP's identity layer and the MVP needs to be demonstrable without that deployment. For `go-go-goja`, the key decision was deferring the verified probe bytecode VM until after the event model is proven correct, because the transcript explicitly warns that building a sound verifier for an unsound event model produces a system that is wrong in a principled way.

## The two seeded tickets

The concrete outputs are two docmgr tickets, each with imported sources and a scoped first-milestone design.

### DATADROP-1 in go-go-datadrop

Path: `ttmp/2026/07/24/DATADROP-1--go-go-datadrop-mvp-research-data-storage-server/`

| Source file | Size | Content |
|---|---|---|
| `sources/open-source-wolfram-datadrop-transcript.md` | 95 KB | Full 3954-line conversation transcript |
| `sources/opendrop-design.md` | 83 KB | The 11,350-word full design document |
| `sources/opendrop-browser-pds-profile.md` | 38 KB | Browser-native PDS / DPoP architecture amendment |
| `sources/opendrop-pod-mvp.zip` | 92 KB | Standalone MVP pod |
| `sources/tinyidp-opendrop-source.tar.gz` | 57 KB | Reference Go slice on TinyIDP |
| `sources/probe_status.png` | 1.5 KB | User-uploaded input screenshot |

The design doc scopes a v0.1 MVP: a single `datadrop` binary with append-only event streams, SQLite storage, a CloudEvents-style envelope, JSON Schema validation, latest-N and time-range queries, SSE subscriptions, CSV/NDJSON/JSON export, and bearer token auth. DPoP, browser sessions, ATproto federation, function runtimes, live sites, and Parquet cold storage are deferred.

### GOJA-069 in go-go-goja

Path: `ttmp/2026/07/24/GOJA-069--javascript-interpreter-instrumentation/`

| Source file | Size | Content |
|---|---|---|
| `sources/javascript-interpreter-instrumentation-transcript.md` | 71 KB | Full 1950-line conversation transcript |
| `sources/verified_semantic_probes_monograph.pdf` | 1.7 MB | 52-page research monograph |
| `sources/verified_semantic_probes_monograph.docx` | 1.3 MB | Editable monograph |
| `sources/semantic-probes-pages/render/` | 18 PNGs | Earlier monograph render pass (pages 38–55) |
| `sources/semantic-probes-pages/render_final/` | 14 PNGs | Final monograph render pass (pages 39–52) |

The design doc scopes a first milestone: a goja fork with a trusted read-only Go event sink for the core call-frame event set (call/enter/return/throw/construct/host), stable function and call-site IDs, frame-local state, counter/histogram/ring-buffer maps, uncatchable invariant violations, and a `go-go-goja` `RuntimeInitializer` integration. The verified probe bytecode VM and verifier are deferred to Phase 3.

## Repository paths

The two repositories live at different roots because one is a primary clone and the other is a workspace worktree.

- `go-go-datadrop`: `/home/manuel/code/wesen/go-go-golems/go-go-datadrop` — primary clone, on branch `main`, with `origin` → `go-go-golems/go-go-datadrop` and `wesen` → `wesen/go-go-datadrop`
- `go-go-goja`: `/home/manuel/workspaces/2026-07-24/go-go-goja-instrumentation/go-go-goja` — workspace worktree, on branch `task/go-go-goja-instrumentation`, with `origin` → `go-go-golems/go-go-goja` and `wesen` → `wesen/go-go-goja`

The go-go-datadrop bootstrap commit is `df58b33` ("Initialize go-go-datadrop project") and the sources commit is `51cbdb5` ("docs: create DATADROP-1 MVP ticket, import OpenDrop conversation sources"). The go-go-goja sources commit is `fdde39c` ("docs: create GOJA-069 instrumentation ticket, import JS interpreter instrumentation sources").

## The surf command surface used

The pipeline uses four `surf` subcommands. Their roles and the flags that matter are:

| Command | Purpose | Key flags |
|---|---|---|
| `surf tab new` | Open a chatgpt.com tab | `--args-json '{"url":"https://chatgpt.com/"}'` |
| `surf tab list` | List tabs to find the ChatGPT tab id | (parsed for the id, coerced to int) |
| `surf js` | Execute JavaScript in the page context; used to list conversations and navigate | `--tab-id <int>`, `--timeout-ms` |
| `surf chatgpt transcript` | Render a conversation to Markdown via the backend API | `--from-api`, `--conversation-id`, `--tab-id`, `--export-file` |
| `surf chatgpt download` | List and download all files in a conversation | `--conversation-id`, `--tab-id`, `--list`, `--output-dir` |

The `--from-api` flag on `transcript` is essential. Without it, the command scrapes the DOM, which depends on the rendered page structure and breaks on UI changes. The API mode reads the canonical conversation JSON, which is stable.

## Key points

- The `go-template` is normalized by ordered placeholder replacement, with specific patterns (`github.com/go-go-golems/XXX`, `go-go-golems.XXX`) replaced before a bare `XXX` catch-all, and the command directory moved with `git mv` so the rename is tracked. A final `rg` scan for `XXX|go-template|GO GO TEMPLATE` confirms no placeholders remain.
- `surf tab list` prints tab ids in scientific notation (`4.41401427e+08`), which `--tab-id` rejects via `strconv.ParseInt`. Any workflow extracting a tab id must coerce it to a plain integer before passing it to a subcommand.
- The file inventory from `surf chatgpt download --list` is empty until the tab is navigated to the conversation URL. With only the chatgpt.com root open, the same call returns zero files. Navigation is done by setting `window.location.href` through `surf js`, because `surf navigate` rejects a trailing URL positional.
- Code-interpreter outputs can return `no download_url`, meaning their signed URLs expired or were never resolvable. These are not retriable. The bundled source tarball typically contains the same delivery and validation material, so no information is lost.
- Downloaded files land in a conversation-id subdirectory with hash-suffixed mangled names, plus a `manifest.json`. The manifest is the source of truth for original paths and must be parsed to recover clean names and directory structure, especially when the original paths encode subdirectories like `render/` and `render_final/`.
- `docmgr doctor` validates frontmatter and vocabulary. Missing topic slugs produce `unknown_topics` warnings and are added with `docmgr vocab add` before re-running. A freshly seeded repo needs more slugs added; an established repo's vocabulary is already large.
- Each ticket's design doc uses decision records to capture the choices that shape the milestone. The two most consequential decisions were standalone-binary-vs-TinyIDP-overlay for datadrop, and defer-the-probe-VM-until-the-event-model-is-proven for goja.

## Open questions

- Why does `surf chatgpt download --list` return an empty inventory when the tab is on the chatgpt.com root rather than the conversation? The extraction walks the conversation's message tree, and the tree appears to populate fully only when the conversation is the active context. Confirming whether this is a backend behavior or a client-side population step would let the download command work without prior navigation.
- Should the tab-id coercion be fixed in `surf tab list` itself, so it prints integers rather than scientific notation? The current behavior forces every consumer to perform the conversion, and the failure is silent until a downstream subcommand rejects the float.
- Should `surf navigate` accept a trailing URL positional? The current `Error: Too many arguments` forces the `window.location.href` workaround via `surf js`, which is functional but indirect.
- For the 7 missing files in the datadrop conversation, is there a retry path that refreshes the signed URLs, or are expired `download_url` values terminal? Re-opening the conversation fresh did not resolve them in this session.

## Near-term next steps

- Begin `go-go-datadrop` Phase 1: skeleton `cmd/datadrop/main.go` with cobra command stubs, a `net/http` ServeMux, and SQLite open/close, per the design doc's phased plan.
- Confirm the `go-go-goja` DR-1 decision (fork goja vs. upstream instrumentation API) before starting Phase 1, since the fork maintenance strategy affects every subsequent step.
- Extract the goja monograph's formal definitions into a reference doc if the Phase 3 verifier design needs them, rather than re-reading the 52-page PDF each time.
- Consider archiving both transcripts into the vault's `Transcripts/YYYY/MM/DD/` structure and linking them to the relevant KB Project MOCs, per the chatgpt-transcript-archiving skill's daily workflow.

## Related notes

- [[PROJECT REPORT - surf-go ChatGPT File Downloader - Driving the Backend API Through the Page Context]] — the design of `surf chatgpt download` and `surf chatgpt transcript --from-api`, which this pipeline uses as its retrieval engine
- [[PROJ - Surf CLI - ChatGPT Transcript Extraction]] — the earlier DOM-based transcript extraction work
- [[ARTICLE - surf-go Browser Verbs - Using JS Probes to Build Reliable Web Automation]] — the browser-side verb pattern that `surf js` follows

## Project working rule

> [!important]
> Retrieve before designing. A conversation's transcript and files are the evidence base for every scope decision; pulling them into `sources/` first means the design doc is grounded in what was actually produced, not in a paraphrase from memory.
> When `surf chatgpt download --list` returns zero files, navigate the tab to the conversation URL before concluding the conversation has no attachments. The inventory populates only when the conversation is the active page context.
