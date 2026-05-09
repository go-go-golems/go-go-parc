---
title: "surf-go Browser Verbs: Using JS Probes to Build Reliable Web Automation"
aliases:
  - surf-go JS Verb Playbook
  - Browser Verb Iteration Report
tags:
  - article
  - playbook
  - surf-go
  - javascript
  - browser
  - automation
  - glazed
  - chatgpt
  - kagi
  - gmail
status: active
type: article
created: 2026-04-10
repo: /home/manuel/code/others/llms/pi/nicobailon/surf-cli
---

# surf-go Browser Verbs: Using JS Probes to Build Reliable Web Automation

This note captures the actual process used to build and refine the new `surf-go` browser verbs in the Surf CLI project. The core lesson is simple: the hard part of a browser automation verb is almost never the Go plumbing. The hard part is figuring out what the page is really doing, proving the interaction sequence on the live site, and only then freezing that logic into an embedded script and a Glazed command.

The important change in this project was treating `surf-go js` as the first-class prototyping tool rather than trying to write the final Go command immediately. Once that became the normal workflow, the commands got better: more reliable page readiness handling, cleaner output, fewer junk tabs, and much better evidence when something broke.

> [!summary]
> The stable workflow is now: probe the live page with `surf-go js`, save the probes in a numbered ticket `scripts/` folder, identify the real selectors and waits, move the final logic into an embedded `go:embed` script, expose it through a dual-mode Glazed command, and validate it both in tests and in a real browser session. The quality of the final verb depends more on the quality of those early probes than on the amount of Go code around them.

## Why this note exists

Before this round of work, it was too easy to treat a new browser verb as a thin wrapper over an existing host message and assume the browser state would line up automatically. That assumption failed repeatedly. Pages reported themselves as loaded while the actual data view was still empty. Single-page apps reused DOM shells between states. A command could open the correct tab and still scrape the wrong thing because the page was not actually ready.

The result was a predictable debugging trap: command output looked wrong, transport was blamed first, and a lot of time was wasted before looking at the real issue, which was usually page readiness, selector choice, or extraction logic.

The new process fixes that by making page investigation explicit.

## What changed in the project

The main user-facing changes from this work were:

- provider verbs were grouped under real families:
  - `surf-go chatgpt ask`
  - `surf-go chatgpt transcript`
  - `surf-go kagi search`
  - `surf-go kagi assistant`
  - `surf-go gmail list`
  - `surf-go gmail search`
- `surf-go js` became the standard mechanism for page-side prototyping
- production browser scripts were moved into embedded files under `go/internal/cli/commands/scripts`
- tab creation and page readiness were unified around exact `tabId` ownership instead of vague "active tab" assumptions
- commands that create a tab now close it by default unless `--keep-tab-open` is set
- dual-mode Glazed output became the pattern: Markdown by default, structured rows behind `--with-glaze-output`

The technical result is not just a nicer CLI. It is a safer development process for future verbs.

## Important code paths

If you need to continue this work in the repo, start with these files:

- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/pkg/doc/tutorials/01-building-browser-side-verbs.md`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/pkg/doc/tutorials/02-building-stateful-gmail-verbs.md`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/tab_ready.go`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/chatgpt_transcript.go`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/kagi_search.go`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/kagi_assistant.go`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/gmail_list.go`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/gmail_search.go`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/scripts/`

The ticket work that fed these commands is also worth reading because it preserves the numbered investigation scripts and the intermediate failures, not just the final code:

- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/ttmp/2026/04/08/SURF-20260408-R4--surf-go-non-provider-cli-parity-architecture-and-implementation-guide`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/ttmp/2026/04/10/SURF-20260410-R5--provider-verb-groups-and-gmail-search-list-command-plan`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/ttmp/2026/04/10/SURF-20260410-R6--shared-tab-readiness-helper-and-chatgpt-extraction-bug`

## The mental model

A browser verb in this project has two different halves.

The first half lives in the browser page. It is responsible for:

- finding the right DOM
- opening the right controls
- waiting for the page to settle
- extracting the actual data

The second half lives in Go. It is responsible for:

- choosing or creating the tab
- owning cleanup
- passing options to the script
- parsing the returned payload
- rendering Markdown or structured rows
- exposing a clean command-line interface through Glazed

The mistake is to merge those halves mentally. When a command is unreliable, separate them again. Ask two different questions:

1. Does the browser script actually work on the live page?
2. Does the Go command call that script with the right tab, timing, and output shaping?

That separation made the debugging much faster.

## The actual build process

### 1. Start with the live page, not the Go code

The first useful command for a new verb is usually not the final command. It is a tiny probe:

```bash
cd /home/manuel/code/others/llms/pi/nicobailon/surf-cli/go
go run ./cmd/surf-go js 'return { href: location.href, title: document.title, ready: document.readyState }'
```

This proves almost nothing except that the command can execute JavaScript. That is still valuable, because it establishes the base of the stack.

The next probes should answer concrete questions:

- what selectors identify the real rows, turns, or cards?
- are there duplicate containers?
- does the page expose a stable id such as `data-message-id` or a final URL?
- is the page fully hydrated when the first container appears, or only later?
- does clicking the visible button immediately open the target panel, or is there delay and re-rendering?

Those probes belong in the ticket `scripts/` folder with explicit numeric prefixes. That turns the investigation into a replayable sequence rather than a pile of forgotten one-offs.

### 2. Save the investigation, do not trust memory

The ticket scripts now serve as the real research trail. The pattern that emerged was:

- `01-...` page markers
- `02-...` inventory of the relevant rows or buttons
- `03-...` interaction probe
- `04-...` submit/wait probe
- `05-...` extraction probe

This mattered more than expected. It became possible to go back and answer questions like: when did we discover the Gmail row selector, when did the search route bug become clear, and which probe proved that the ChatGPT Activity panel was real DOM and not an inaccessible shadow view?

Without those scripts, the answer would have been "somewhere in the transcript." That is not good enough for a project that keeps changing.

### 3. Stabilize the browser algorithm before writing the command

The first probe that returns something plausible is not the end of the browser phase. It is the start of the stabilization phase.

For example:

- ChatGPT transcript extraction only became correct after treating each conversation turn as a section, enumerating message candidates, and choosing the longest non-empty candidate per message. A simpler selector kept pulling source chips and fragments instead of the full assistant body.
- Kagi search only became reliable after waiting for real hydrated result rows instead of assuming the page shell meant the results were ready.
- Gmail search only became reliable after waiting for both the search route and a changed row snapshot, because Gmail reuses the inbox shell while the search results are still transitioning.

The practical rule is: if the extraction depends on one lucky timing window, it is not ready to become a verb.

### 4. Move the final browser logic into an embedded production script

Once the browser algorithm is stable, move it out of the ticket script and into a production script under:

`/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/scripts`

Then embed it with `go:embed` in the owning command.

That matters for two reasons.

First, it keeps the production logic visible and easy to edit. The script is a real file with syntax highlighting rather than a buried raw string.

Second, it keeps the command self-contained. Someone reading the command can find the script immediately, and someone modifying the script does not have to search through a giant Go string literal.

The ticket scripts remain the research trail. The embedded script becomes the maintained implementation.

### 5. Pass options in, parse once, render late

The script should return a clean payload. The Go code should parse it once and only then decide how to present it.

That separation was important for dual-mode output. A command such as `chatgpt transcript` or `kagi search` should not format Markdown in the browser script. The script should return structured data. The Go layer can then:

- emit structured rows for `--with-glaze-output`
- render Markdown for the writer mode
- optionally write an export artifact

This kept the browser code focused on page logic and kept the Go code focused on CLI ergonomics.

### 6. Treat tab ownership as part of the API

One of the larger design improvements was making exact `tabId` ownership explicit.

The wrong mental model is: open a tab, then somehow talk to "the browser" or "the active tab."

The right mental model is:

1. create a tab and capture its `tabId`
2. wait for that exact tab to become executable
3. optionally wait again for the page-specific state to become real
4. run the script against that exact tab
5. if the command created the tab, close it by default

This change fixed more than just cleanup. It reduced ambiguity. Commands stopped accidentally depending on whichever tab happened to be focused, and the later readiness helper gave the Kagi and Gmail commands a common foundation.

## Concrete examples from this work

### ChatGPT transcript

The transcript command started as a DOM scraping problem and turned into a subtle extraction problem. The page contained multiple plausible assistant nodes, and the early provider-side extraction logic kept selecting short chip-like content instead of the actual message body.

The fix came from comparing the interactive provider logic against the transcript-export logic. The transcript path, which walked conversation turn sections and chose the strongest candidate per turn, became the better reference implementation. That comparison produced a concrete bug report and a better extraction algorithm.

A second branch of the work dealt with the Activity sidebar. The first assumption was that only the "Thought for ..." chip text was visible. Later probes proved that the richer Activity panel content was extractable once the flyout was actually open. That distinction matters: the existence of a visible chip does not mean the detailed content is present in the main page DOM. Sometimes the real payload is only materialized after the UI interaction.

### Kagi search

Kagi search looked simple. It was not.

The early command could open the correct page and still return "No results found" because it was waiting on the wrong signal. The search shell appeared before the result rows were hydrated. The fix was not "sleep a bit more" in the abstract. The fix was to identify the actual result row selectors and wait for extractable rows, not just for the page to look loaded.

This is the recurring lesson for web apps: `document.readyState === 'complete'` is usually not enough.

### Kagi assistant

Kagi Assistant pushed the pattern from page scraping into stateful UI manipulation. The command had to reliably select:

- assistant profile
- model
- lens
- web search mode
- tags

The important lesson here was that stateful commands still follow the same development pattern. They simply spend more time in the browser algorithm phase. The end result was still the same architectural shape: numbered probe scripts, an embedded production script, a Glazed command, and tab cleanup rules.

### Gmail list and search

Gmail introduced a more serious state problem. The page shell persists, the route changes in the hash fragment, and the row container can contain inbox rows before search results are actually ready.

That forced a stronger rule: readiness is not a single thing.

There is transport readiness, which says the tab exists and can execute JavaScript.
There is DOM readiness, which says the shell is rendered.
There is state readiness, which says the specific data view you care about is actually active.

Gmail search only became trustworthy when the command waited for the search route and for the row snapshot to change away from the inbox baseline.

## Failure modes that mattered

### The page is executable but not ready

This showed up everywhere. The existence of a tab, or even of a DOM node, is not proof that the data is ready to scrape.

The fix is always the same: define a page-specific readiness condition and wait for that, not just for generic load completion.

### The wrong node looks plausible

This was the ChatGPT extraction bug. The page exposed many text nodes that looked assistant-related. Only some of them were the real message body.

The fix was to extract at the level of logical turns rather than at the level of arbitrary descendant nodes.

### A command leaves browser junk behind

A research CLI that leaves a trail of tabs behind is not ergonomic. The fix was to make tab ownership explicit and close owned tabs by default.

### JavaScript execution infrastructure can break valid scripts

One non-obvious failure was in the service worker wrapper around `js` execution. Wrapping user scripts in a template literal broke valid scripts that themselves contained template literals. The fix was to stop embedding the script that way and to improve error reporting so syntax failures surfaced with line and column context.

This is worth remembering because infrastructure bugs can masquerade as page bugs.

## Working rules for future verbs

If I were continuing this project tomorrow, I would follow these rules strictly.

1. Do not start with the final Go command. Start with `surf-go js`.
2. Save every meaningful probe in the ticket `scripts/` folder with numeric prefixes.
3. Promote browser logic to production only after the selectors, waits, and dedupe rules are explicit.
4. Put production page logic in embedded script files, not raw Go string literals.
5. Treat tab ownership and cleanup as part of the command contract.
6. Keep the browser script responsible for extraction and the Go layer responsible for rendering.
7. Validate in three layers: unit tests, mock-host integration, real browser session.
8. When a command output is wrong, compare it to the closest existing verb that already solves the same extraction problem.

## Source examples

A future contributor should not just read the prose. They should open the exact artifacts that made the process concrete. The useful examples fall into three layers: numbered research probes in ticket folders, embedded production scripts in the command package, and the Go commands that wrap those scripts in a real CLI surface.

### Numbered ticket probes

These are the best examples of the exploratory phase. They show how the browser model was discovered step by step instead of guessed all at once.

- ChatGPT transcript and Activity panel investigation:
  - `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/ttmp/2026/04/08/SURF-20260408-R4--surf-go-non-provider-cli-parity-architecture-and-implementation-guide/scripts/chatgpt_transcript_dom_summary.js`
  - `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/ttmp/2026/04/08/SURF-20260408-R4--surf-go-non-provider-cli-parity-architecture-and-implementation-guide/scripts/chatgpt_transcript_extract_dom.js`
  - `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/ttmp/2026/04/08/SURF-20260408-R4--surf-go-non-provider-cli-parity-architecture-and-implementation-guide/scripts/chatgpt_activity_open_single.js`
  - `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/ttmp/2026/04/08/SURF-20260408-R4--surf-go-non-provider-cli-parity-architecture-and-implementation-guide/scripts/chatgpt_activity_export_first_three.js`
- Gmail state and row-shape investigation:
  - `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/ttmp/2026/04/10/SURF-20260410-R5--provider-verb-groups-and-gmail-search-list-command-plan/scripts/01-gmail-page-markers.js`
  - `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/ttmp/2026/04/10/SURF-20260410-R5--provider-verb-groups-and-gmail-search-list-command-plan/scripts/02-gmail-inbox-row-inventory.js`
  - `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/ttmp/2026/04/10/SURF-20260410-R5--provider-verb-groups-and-gmail-search-list-command-plan/scripts/04-gmail-search-submit-probe.js`
  - `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/ttmp/2026/04/10/SURF-20260410-R5--provider-verb-groups-and-gmail-search-list-command-plan/scripts/06-gmail-semantic-field-probe.js`

The point of reading these scripts is not to reuse them verbatim. The point is to see the shape of a good investigation: first identify the page markers, then inventory the interesting nodes, then prove the interaction sequence, then prove the extraction.

### Embedded production scripts

These are the examples to follow once the browser algorithm is stable enough to ship.

- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/scripts/chatgpt_transcript.js`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/scripts/kagi_search.js`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/scripts/kagi_assistant.js`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/scripts/gmail_list.js`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/scripts/gmail_search.js`

Each one shows the same pattern in a slightly different context:

- read options from the injected command context
- wait for page-specific readiness, not just generic load completion
- return structured data rather than preformatted Markdown
- keep UI interaction, waits, and extraction in one browser-side script

### Go command wrappers

These are the examples to follow on the CLI side.

- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/chatgpt_transcript.go`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/kagi_search.go`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/kagi_assistant.go`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/gmail_list.go`
- `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/gmail_search.go`
- shared readiness helper: `/home/manuel/code/others/llms/pi/nicobailon/surf-cli/go/internal/cli/commands/tab_ready.go`

These files show the higher-level engineering decisions that sit above the browser script:

- whether to reuse a target tab or create a fresh one
- how to wait for the exact `tabId` that the command owns
- when to close the tab by default
- how to render Markdown versus Glazed row output
- how to write tests that lock the request sequence down

### Concrete command examples

The following commands are good reproductions of the workflow in practice:

```bash
export SURF_SOCKET_PATH=/home/manuel/snap/chromium/common/surf-cli/surf.sock

cd /home/manuel/code/others/llms/pi/nicobailon/surf-cli/go

go run ./cmd/surf-go js 'return { href: location.href, title: document.title }'
go run ./cmd/surf-go kagi search --query "hello" --keep-tab-open
go run ./cmd/surf-go kagi assistant "Explain the history of IIFEs" --assistant Quick
go run ./cmd/surf-go chatgpt transcript --with-activity
go run ./cmd/surf-go gmail list --inbox --max-results 10
go run ./cmd/surf-go gmail search "from:noreply@github.com newer_than:30d" --max-results 10
```

If a new verb does not naturally fit into this pattern, that is a signal to stop and decide whether it is really a browser-side verb or whether it needs a different architecture entirely.

## The larger point

The main thing I would want a future contributor to understand is that complex browser verbs are not built by guessing the right final abstraction. They are built by interrogating the live page until the page gives up a stable model of itself.

The `js` command changed the project because it made that interrogation cheap. Once that became cheap, it became natural to save the probes, compare them, turn the final ones into embedded scripts, and then wrap them in a proper Glazed command.

That is the actual playbook now. Not "write some Go and hope the browser cooperates." Probe first, stabilize second, embed third, glaze fourth, validate last.

## Related notes

- [[Deep Research with Web Tools]]
- [[Writing Style for Knowledge Base Articles]]
