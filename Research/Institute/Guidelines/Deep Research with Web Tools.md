---
title: Deep Research with Web Tools
aliases:
  - Research Playbook
  - Web Research Guidelines
tags:
  - research
  - guidelines
  - institute
  - kagi
  - chatgpt
  - surf
  - methodology
status: active
type: guideline
created: 2026-04-03
updated: 2026-04-16
source_repo: /home/manuel/code/others/llms/pi/nicobailon/surf-cli
---

# Deep Research with Web Tools

This is the current practical workflow for doing deep technical research with the `surf` browser automation stack, `defuddle`, and `docmgr`. The important shift is that the browser work is no longer centered on ad hoc Playwright calls. It is now centered on stable grouped `surf` verbs backed by the Surf extension and the local native host.

The current command families are:

- `surf chatgpt ask` — ask ChatGPT questions and get answers
- `surf chatgpt transcript` — export ChatGPT conversation transcripts
- `surf kagi search` — search the web via Kagi
- `surf kagi assistant` — use Kagi's AI assistant for synthesis and comparisons
- `surf js` — browser-side probing and one-off extraction work

> [!summary]
> For most research sessions, the working loop is now: define questions, open a `docmgr` ticket, use `surf kagi search` to gather URLs, clean those URLs with `defuddle`, use `surf kagi assistant` for structured synthesis, use `surf chatgpt ask` for longer-form analysis, then export the resulting conversation with `surf chatgpt transcript`.

---

## The Ideal Order

1. Read the local repo or source material first and write 3-6 concrete research questions.
2. Create a `docmgr` ticket and an initial task list.
3. Use `surf kagi search` to gather the first set of authoritative URLs.
4. Use `defuddle` to clean and save the best URLs locally.
5. Use `surf kagi assistant` for spec-level synthesis and comparisons.
6. Use `surf chatgpt ask` for the longer cross-source analysis once the source set is already good.
7. Export the finished ChatGPT conversation with `surf chatgpt transcript`.
8. Write the resulting knowledge base notes in article style.
9. Update the ticket diary, changelog, and task checkboxes.

The order matters. Search comes before synthesis. Source cleaning comes before long-form model output. Transcript export happens after the answer is done, not during the initial ask.

## Tool Selection

| Question type | Best tool |
|--------------|-----------|
| "Find the right URLs, specs, docs, or blog posts" | `surf kagi search` |
| "Explain why this mechanism works and compare approaches" | `surf kagi assistant` |
| "Write a longer structured analysis across many sources" | `surf chatgpt ask` |
| "Export the answer I already got from ChatGPT" | `surf chatgpt transcript` |
| "Fetch and clean a specific URL" | `defuddle parse <url> --md` |
| "Probe a page that does not yet have a dedicated verb" | `surf js` |

## Prerequisites

### Browser setup

The Surf extension must be loaded in Chromium from:

`/home/manuel/code/others/llms/pi/nicobailon/surf-cli/dist`

The native host must be running, and the CLI must point at the correct socket. In the current Snap Chromium setup that means:

```bash
export SURF_SOCKET_PATH=/home/manuel/snap/chromium/common/surf-cli/surf.sock
```

If a command says the socket is missing, reload the Surf extension in `chromium://extensions` first.

### Accounts

Log into the web apps in the browser session before you start:

- **Kagi** — for `surf kagi search` and `surf kagi assistant`
- **ChatGPT** — for `surf chatgpt ask` and `surf chatgpt transcript`

These commands use the live browser session. They do not log you in for you.

### Tab ownership rule

The newer browser verbs create their own tab when they need one and close it by default when they are done. If you want to inspect the page afterwards, pass:

```bash
--keep-tab-open
```

This is the right default because research automation should not leave behind junk tabs after every run.

---

## Kagi Search

Use `surf kagi search` to find authoritative URLs quickly.

Example:

```bash
surf kagi search --query "lexical environment eval ecma-262"
```

The command now creates a fresh Kagi tab when needed, waits for that exact tab to become ready, waits again for real result rows to hydrate, extracts the search results, and closes the tab unless you keep it open.

Use `--keep-tab-open` when you want to inspect the page:

```bash
surf kagi search --query "sanjoy mahajan art of insight review" --keep-tab-open
```

Use `--with-glaze-output` if you want machine-readable rows instead of Markdown:

```bash
surf kagi search \
  --query "javascript module pattern history" \
  --with-glaze-output --output yaml
```

Good query shape:

- 4-8 concrete terms
- public terminology, not private implementation names
- one mechanism or concept per query

Once you have useful URLs, clean them with `defuddle`:

```bash
defuddle parse https://example.com/article --md -o sources/web/article.md
```

## Kagi Assistant

Use `surf kagi assistant` when search is no longer enough and you want a structured synthesis.

> [!important]
> **Timeout requirement:** Use at least 5 minutes (300 seconds) timeout for all `surf kagi assistant` queries. These commands involve browser automation, page hydration, model response generation, and extraction. Short timeouts will cause failures.

Example:

```bash
surf kagi assistant \
  "Explain why immediate invocation became important in JavaScript module patterns, and contrast it with ES modules." \
  --assistant Quick
```

With explicit timeout:

```bash
timeout 300 surf kagi assistant \
  "Your query here" \
  --assistant Quick
```

The newer implementation can also list and select the live options exposed by Kagi:

```bash
surf kagi assistant --list-all-options --with-glaze-output --output yaml
```

That command family supports:

- assistant selection
- model selection
- lens selection
- web search mode
- tag application

Example with explicit options:

```bash
surf kagi assistant \
  "Compare Goja REPL persistence to notebook kernels." \
  --assistant Quick \
  --model gpt-5-mini \
  --lens Programming \
  --web-search-mode on
```

Use Kagi Assistant for explanation, comparison, and spec interpretation. Do not use it as a substitute for collecting the underlying URLs. The best workflow is still search first, synthesis second.

## ChatGPT Ask

Use `surf chatgpt ask` for the long-form pass once you already understand the question and have a decent source set.

> [!important]
> **Timeout requirement:** Use at least 5 minutes (300 seconds) timeout for all `surf chatgpt ask` queries. Long-form analysis involves browser navigation, prompt submission, streaming response generation, and extraction. These operations routinely exceed 60-120 seconds.

Example:

```bash
surf chatgpt ask \
  "Write a detailed analysis of Sanjoy Mahajan's The Art of Insight in Science and Engineering. Cover the thesis, target audience, techniques taught, structure, examples, author background, what makes it distinctive, and the writing style."
```

With explicit timeout:

```bash
timeout 300 surf chatgpt ask \
  "Your long-form query here"
```

This is the right place for:

- long-form synthesis
- comparative analysis
- outlining a technical topic as an article or report
- taking a pile of already-good sources and turning them into one coherent answer

It is not the right first tool when you still do not know what the primary sources are.

## ChatGPT Transcript Export

After the ChatGPT conversation is finished, export it with `surf chatgpt transcript`.

Example:

```bash
surf chatgpt transcript
```

If you want the richer Activity sidebar content when it exists:

```bash
surf chatgpt transcript --with-activity
```

If you want a durable artifact:

```bash
surf chatgpt transcript \
  --export-file /tmp/chatgpt-transcript.md
```

This command works on the current ChatGPT conversation page. It is designed for after-the-fact export, not for submitting the original prompt.

## `surf js` as the Escape Hatch

When there is no dedicated verb yet, use `surf js`.

Example:

```bash
surf js 'return { href: location.href, title: document.title }'
```

This is now the standard way to prototype the next browser verb. The working loop is:

1. inspect the live page with tiny probes
2. save the useful probes in the ticket `scripts/` folder
3. stabilize selectors and waits
4. move the final script into an embedded production file with `go:embed`
5. wire the Go command and tests around it

In other words, `surf js` is not just a convenience function. It is the prototyping layer for future browser automation.

---

## Writing Knowledge Base Documents

The deliverable is still a durable note, not just a pile of command output.

The practical sequence is:

1. use `surf kagi search` to find URLs
2. use `defuddle` to clean them
3. use `surf kagi assistant` and `surf chatgpt ask` to synthesize
4. use `surf chatgpt transcript` to preserve the long-form model output
5. write the final note in article style

The article should still:

- open with a concrete problem
- explain the mechanism in prose
- make the so-what explicit
- cite the key sources cleanly
- avoid dumping raw model output directly into the vault

The model output is an intermediate artifact. The note is the real deliverable.

## docmgr Bookkeeping

The bookkeeping pattern is unchanged. After each substantial step:

```bash
# Check off completed tasks
docmgr task check --ticket PROJ-01 --id N

# Relate sources to the document
docmgr doc relate \
  --doc "ttmp/.../reference/02-PROJECT - Topic.md" \
  --file-note "/abs/path/sources/web/chatgpt-transcript.md:ChatGPT transcript export"

# Update changelog
docmgr changelog update --ticket PROJ-01 \
  --entry "Wrote reference/02. Sources: Kagi search + Kagi assistant + ChatGPT transcript." \
  --file-note "/abs/path/reference/02-PROJECT - Topic.md:New knowledge base doc"
```

---

## Common Gotchas

> [!bug] Kagi search returns no results from a fresh tab
> This is usually a readiness problem, not a query problem. The tab may exist before the result rows are hydrated. The fix is to wait for real result rows, not just the page shell.

> [!bug] Kagi assistant works in the browser but not from the command
> Verify the browser session is still logged in and that you are using the correct `SURF_SOCKET_PATH`. If you want to inspect the UI state after the run, use `--keep-tab-open`.

> [!bug] ChatGPT output looks garbled or source-chip-heavy
> Compare the extraction logic to `surf chatgpt transcript`. The transcript command became the reference for turn-based assistant extraction because the earlier provider-side polling was selecting the wrong nodes.

> [!bug] A command leaves too many tabs behind
> New browser verbs should close tabs they created by default. Use `--keep-tab-open` only when you are deliberately debugging or inspecting the page.

---

## Related Notes

- [[docmgr - Ticket Workflow]]
- [[Writing Style for Knowledge Base Articles]]
- [[ARTICLE - surf Browser Verbs - Using JS Probes to Build Reliable Web Automation]]
