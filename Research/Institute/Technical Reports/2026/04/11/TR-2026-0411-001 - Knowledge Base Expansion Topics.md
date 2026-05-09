---
title: "TR-2026-0411-001 Knowledge Base Expansion Topics"
subtitle: "Foundational Concepts and Patterns from ChatGPT Transcript Extraction Worthy of Dedicated Vault Entries"
aliases:
  - ChatGPT Extraction Knowledge Base
  - TR-2026-0411-001 KB Topics
tags:
  - research
  - technical-report
  - surf-cli
  - knowledge-base
  - dom-extraction
  - browser-automation
  - command-architecture
related:
  - "[[TR-2026-0411-001 - ChatGPT Transcript Extraction System - Implementation and Methodology]]"
  - "[[TR-2026-0411-001 - Further Research Points]]"
  - "[[REPL Semantics, Lexical Scope, and Source-to-Source Transformation]]"
status: draft
type: knowledge-base-expansion
created: 2026-04-11
parent-report: TR-2026-0411-001
---

# TR-2026-0411-001 Knowledge Base Expansion Topics

This document lists technical topics from the [[TR-2026-0411-001 - ChatGPT Transcript Extraction System - Implementation and Methodology|ChatGPT Transcript Extraction System report]] that warrant dedicated entries in the vault's knowledge base. Unlike the [[TR-2026-0411-001 - Further Research Points|Further Research Points]] document (which covers open investigation questions), these are **foundational concepts, patterns, and platform knowledge** that would serve as reusable reference material for future projects.

Each topic includes the concrete evidence from the TR, source files, and research diaries that establishes why this knowledge is worth preserving.

---

## 1. DOM Extraction Patterns

### 1.1 Turn-Based Deduplication Algorithm

**What it is**: An algorithm for extracting semantic content from React SPA DOMs that render the same logical message as multiple nested nodes with identical attributes.

**Concrete evidence this matters**:

- **The citation-fragment bug** (SURF-20260410-R6 bug report): The interactive provider used global "last assistant node" selection and returned citation labels (`MIT OpenCourseWare`, `MIT Press`) instead of the 18,933-character response body.
- **Host log proof**: `turnCount=0, len=187, foundAssistant=false` before fix → `turnCount=2, len=18933, foundAssistant=true` after fix.
- **The transcript command as validator**: Running `chatgpt-transcript` on the same tab confirmed the answer existed in the DOM — proving the extraction algorithm was the bug, not the underlying data.

**Source code**:
- `go/internal/cli/commands/scripts/chatgpt_transcript.js` lines 58-94 (`extractSectionMessage` function)
- `go/internal/host/providers/chatgpt.go` (provider polling logic that was fixed)

**Research diary**: `SURF-20260408-R4` Step 6 — "Build a cleaned-up DOM transcript extractor" explicitly names "Deduplication by `data-message-id`" and "Selecting longest text per message ID to avoid wrapper duplicates" as the working approach.

**Generalizable to**: Claude, Gemini, Perplexity, and any React/Vue/Svelte app that wraps content in redundant containers.

---

### 1.2 Longest-Text Selection Heuristic

**What it is**: Using text length as a ranking signal to select the "best" node among candidates with identical semantic roles.

**Concrete evidence this matters**:

- **The deduplication mechanism** (chatgpt_transcript.js line 91): `items.sort((a, b) => b.textLength - a.textLength)` — the algorithm sorts all candidates for a message ID by text length descending and takes `items[0]`.
- **Why it works for ChatGPT**: Wrapper nodes have short text (metadata, role names). Content nodes have long text (the actual message). Citations have medium text. Sorting by length naturally prioritizes content over wrappers and citations.
- **The 187 vs 18933 contrast**: The buggy provider captured 187 characters (citation fragment). The working extractor captured 18933 characters (full response). Length difference: 100x.

**Source code**:
```javascript
// chatgpt_transcript.js line 83-91
const existing = byMessageId.get(messageId);
if (!existing || text.length > existing.text.length) {
  byMessageId.set(messageId, { ..., text, textLength: text.length });
}
const items = Array.from(byMessageId.values());
items.sort((a, b) => b.textLength - a.textLength);
const best = items[0];  // Longest text wins
```

**Pitfalls to document**:
- Breaks when annotations are longer than content (e.g., very short responses with verbose citations)
- Does not work when all nodes are wrappers (e.g., during streaming, before content is rendered)

**Suggested vault entry**: `KNOWLEDGE - Content Selection Heuristics` — covers longest-text, first-match, score-based, and hybrid selection strategies.

---

### 1.3 Flyout/Flyover Panel Extraction

**What it is**: A pattern for extracting content from modal overlays that require user interaction to open and have non-deterministic appearance timing.

**Concrete evidence this matters**:

- **Discovery in research diary**: `SURF-20260408-R4` Step 8-11 documented that "Thought for N seconds" buttons open a flyout with reasoning chain content, but:
  - The flyout takes 400-7000ms to appear
  - First click may not open the flyout (race condition)
  - Multiple flyouts may exist; must match by duration
  - The flyout may show "Sources" instead of "Activity" on first open
- **17 scripts written**: Including `chatgpt_thought_trace_scan.js`, `chatgpt_thought_trace_click_probe.js`, `chatgpt_activity_open_single.js`, `chatgpt_activity_export_first_three.js`, `chatgpt_activity_button_map.js`

**Source code**:
- `go/internal/cli/commands/scripts/chatgpt_transcript.js` lines 26-55 (`normalizeAndOpen` function)
- Key parameters: 2 attempts, 7000ms timeout, 400ms retry interval, `scrollIntoView` before click, duration-matched header text

**Selector discovered**:
```javascript
// chatgpt_transcript.js lines 8-11
const ACTIVITY_SELECTORS = [
  'body > div:nth-child(5) > div > ... > section',  // Exact path from DOM analysis
  '[class*="stage-thread-flyout"] section',         // Fallback class match
];
```

**Pattern components to document**:
1. Trigger identification (button text matching `/Thought for/i`)
2. Match key extraction (duration string from button)
3. Click + poll with retry
4. Header matching to confirm correct flyout
5. Content extraction and dismiss

**Suggested vault entry**: `KNOWLEDGE - Interactive Overlay Extraction` — covers flyouts, modals, dropdowns, tooltips; generalizable beyond ChatGPT.

---

## 2. Browser Automation Patterns

### 2.1 Probe Script Methodology

**What it is**: A disciplined approach to browser automation that treats the live page as the primary source of truth: probe → document → identify → freeze → validate.

**Concrete evidence this matters**:

- **17 numbered scripts created**: All preserved in `ttmp/2026/04/08/SURF-20260408-R4/scripts/`:
  ```
  chatgpt_transcript_dom_summary.js           # Phase II: DOM inventory
  chatgpt_transcript_resource_scan.js         # Phase III: Resource discovery
  chatgpt_transcript_backend_probe.js          # Phase III: Backend API probing
  chatgpt_transcript_auth_surface_scan.js     # Phase III: Token investigation
  chatgpt_transcript_cache_scan.js            # Phase III: Storage investigation
  chatgpt_transcript_indexeddb_scan.js       # Phase III: IndexedDB investigation
  chatgpt_thought_trace_scan.js               # Phase IV: Thought pattern detection
  chatgpt_thought_trace_click_probe.js        # Phase IV: Click behavior analysis
  chatgpt_activity_*.js                      # Phase IV: Flyout extraction
  ```
- **Research diary documents the process**: `SURF-20260408-R4` is a step-by-step log of what was tried, what failed, and why DOM extraction was chosen over the backend API approach.
- **Failure was productive**: The 6-phase probe process found that backend `/textdocs` returns 401, storage has no token, IndexedDB has no transcript — all ruling out easier paths.

**The command that drove it**: `surf-go js --file <probe-script.js>` was the primary tool for all investigation. See `go/internal/cli/commands/js.go` and `js_test.go`.

**Why this is worth preserving**:
- The methodology applies to any new provider (Claude, Gemini, Perplexity, Grok)
- Future work can follow the same probe → freeze workflow
- The numbered script archive preserves the decision trail

**Reference**: [[ARTICLE - surf-go Browser Verbs - Using JS Probes to Build Reliable Web Automation]] — this playbook formalizes the methodology.

**Suggested vault entry**: `PLAYBOOK - Browser Probe Script Methodology`

---

### 2.2 Tab Readiness Detection

**What it is**: A deterministic protocol for determining when a browser tab is ready to accept extraction commands after creation.

**Concrete evidence this matters**:

- **Race condition that motivated it**: Pages report `readyState === "complete"` before React SPAs have hydrated. Commands could open the correct tab and still scrape the wrong content because the data view was empty.
- **Exact criteria codified**: `go/internal/cli/commands/tab_ready.go`:
  ```go
  state.ReadyState == "complete" &&
  state.Href != "" &&
  state.Href != "about:blank" &&
  tabURLMatches(state.Href, opts)
  ```
- **"Cannot find default execution context" error is ignored**: This error is expected during React hydration and is explicitly excluded from retry termination.
- **Applied to Kagi and Gmail**: The same `tab_ready.go` helper is used by `kagi_search.go` and `kagi_assistant.go`. Proven reusable.

**Source code**:
- `go/internal/cli/commands/tab_ready.go` — full implementation
- `go/internal/cli/commands/kagi_search.go` — integration example
- `go/internal/cli/commands/kagi_assistant.go` — integration example

**Parameters to preserve**:
- Timeout: 20s default
- Retry interval: 400ms
- Probe script: `return { href: location.href, title: document.title, readyState: document.readyState }`

**Research diary**: `SURF-20260410-R6` design doc `01-shared-tab-readiness-helper-design.md` — captures the architecture decision.

**Suggested vault entry**: `KNOWLEDGE - Tab Readiness Detection`

---

### 2.3 Duration-Matching Retry Pattern

**What it is**: A retry strategy for race conditions where the correct target must be identified by matching against a duration string extracted from the trigger.

**Concrete evidence this matters**:

- **The flyout race condition**: From `SURF-20260408-R4` research diary Step 8: "The flyout takes 400-1200ms to appear after click. The Activity header must be matched against the button's duration text to confirm the correct flyout opened."
- **Multiple flyout types exist**: A conversation turn may have a "Sources" flyout and an "Activity" flyout. The duration-matching confirms which one opened.
- **2-attempt retry with 400ms delay**: From `chatgpt_transcript.js` `normalizeAndOpen()`:
  ```javascript
  for (let attempt = 1; attempt <= 2; attempt += 1) {
    button.click();
    const hit = await waitForCondition(..., 7000);  // 7s timeout per attempt
    if (hit) return hit;
    await sleep(400);  // Wait before retry
  }
  ```

**Source code**:
- `go/internal/cli/commands/scripts/chatgpt_transcript.js` lines 38-55
- The `durationFromButtonText()` and `activityMatchesDuration()` functions are the core

**Why this pattern is worth generalizing**:
- Similar race conditions exist in: dropdown menus, autocomplete suggestions, toast notifications, lazy-loaded modals
- The pattern: extract match key from trigger → click → poll → match key from result → retry if mismatch

**Suggested vault entry**: `KNOWLEDGE - Race Condition Retry Patterns`

---

## 3. Command Architecture

### 3.1 Dual-Mode Glazed Commands

**What it is**: A command that implements both `WriterCommand` (human-readable Markdown) and `GlazeCommand` (structured data rows) simultaneously, controlled by `--with-glaze-output`.

**Concrete evidence this matters**:

- **The chatgpt-transcript command is the primary example**: Both interfaces are implemented in `go/internal/cli/commands/chatgpt_transcript.go`:
  ```go
  var _ cmds.GlazeCommand = (*ChatGPTTranscriptCommand)(nil)
  var _ cmds.WriterCommand = (*ChatGPTTranscriptCommand)(nil)
  ```
- **The "critical implementation detail"**: The TR Section 4.1 explicitly documents: "When implementing both interfaces, the command builder must use `cli.WithDualMode(true)` and `cli.WithGlazeToggleFlag('with-glaze-output')`. Without dual mode, the writer path takes precedence."
- **Two execution paths**: `RunIntoWriter()` calls `renderChatGPTTranscriptMarkdown()`; `RunIntoGlazeProcessor()` calls `chatGPTTranscriptDataToRows()`.

**Source code**:
- `go/internal/cli/commands/chatgpt_transcript.go` lines 81-159 (both interface implementations)
- The Glazed schema definition in `NewChatGPTTranscriptCommand()`

**Row expansion to preserve** (chatgpt_transcript.go lines 201-230):
- Flattened metadata per turn: `index, role, model, messageId, textLength, text, hasThought, thoughtButtonText, activityText, activityAttempts, activityWaitedMs`
- Conversation-level fields: `href, title, turnCount, withActivity, activityLimit, activityExported`

**Why this is worth a playbook**:
- The dual-mode pattern is used across Surf CLI commands
- The Glazed toggle flag integration is non-obvious (easy to miss)
- The row expansion logic (flattening nested data for tabular output) is a reusable pattern

**Suggested vault entry**: `PLAYBOOK - Dual-Mode Glazed Commands`

---

### 3.2 Embedded Script Architecture (go:embed + SURF_OPTIONS)

**What it is**: A pattern for injecting configuration from Go into JavaScript scripts embedded at compile time via `go:embed`.

**Concrete evidence this matters**:

- **The SURF_OPTIONS pattern**: From `go/internal/cli/commands/chatgpt_transcript.go` lines 81-91:
  ```go
  //go:embed scripts/chatgpt_transcript.js
  var chatGPTTranscriptScript string

  func buildChatGPTTranscriptCode(s *ChatGPTTranscriptSettings) (string, error) {
    options := map[string]any{
      "withActivity":  s.WithActivity,
      "activityLimit": s.ActivityLimit,
    }
    b, _ := json.Marshal(options)
    return fmt.Sprintf("const SURF_OPTIONS = %s;\n%s", string(b), chatGPTTranscriptScript), nil
  }
  ```
- **Why SURF_OPTIONS over runtime parsing**: User code is wrapped in an IIFE by the service worker. Passing options as a JSON object assigned to a global avoids parsing complexity.
- **Compile-time embedding**: No runtime file I/O, script is versioned with the Go binary.

**Benefits documented in the TR**:
- Single source of truth: script is versioned with Go
- No runtime file I/O
- Compile-time validation of script syntax

**Constraints documented**:
- Script must reference `SURF_OPTIONS` (not parse a string)
- Template literals with `${...}` are unsafe when wrapped by the service worker (see Section 5.4)

**Suggested vault entry**: `KNOWLEDGE - Embedded Script Injection Patterns`

---

### 3.3 jsverbs: JavaScript-to-Glazed Command Layer

**What it is**: A system for authoring CLI commands in JavaScript while getting Go/Glazed schema generation, Cobra integration, structured output, and help pages.

**Concrete evidence this matters**:

- **Separate project in vault**: `Projects/2026/03/16/PROJ - go-go-goja jsverbs - JavaScript to Glazed Commands`
- **Conceptual overlap with embedded scripts**: Both involve JS-defined behavior with Go infrastructure. The difference: jsverbs is for authoring *new commands*; embedded scripts are for authoring *JS logic* called by existing commands.
- **Layers to document**:
  1. Source discovery (scan `.js` files)
  2. Metadata extraction (YAML frontmatter → AST parsing)
  3. Command compilation (schema → Glazed command)
  4. Runtime invocation (execute JS with goja)
  5. Help packaging (frontmatter → Glazed help entry)

**Source code** (from vault project):
- `pkg/jsverbs/scan.go` — file discovery
- `pkg/jsverbs/model.go` — AST-based metadata extraction
- `pkg/jsverbs/binding.go` — command compilation
- `pkg/jsverbs/command.go` — Glazed integration
- `pkg/jsverbs/runtime.go` — goja execution

**Why this matters for Surf CLI**: The chatgpt_transcript script is Go-authored JS (embedded). jsverbs would enable surf-cli users to author new browser commands in JS directly.

**Suggested vault entry**: `ARCH - jsverbs System Design`

---

## 4. Validation & Debugging

### 4.1 Ground-Truth Validation via Extractor

**What it is**: Using a separate, independently validated extraction tool as the reference (ground truth) to debug an interactive provider.

**Concrete evidence this matters**:

- **The citation-fragment bug** (SURF-20260410-R6): The bug was diagnosed by:
  1. Running `chatgpt-transcript` on the same tab that `surf chatgpt` had garbled
  2. `chatgpt-transcript` returned the correct 18,933-character response
  3. This proved the underlying DOM had the correct data, narrowing the bug to the provider's extraction logic
- **Key phrase from bug report**: "A direct transcript export of that exact conversation shows that the full assistant response is present in the DOM and can be extracted correctly."
- **Why this pattern is generalizable**: Any time an interactive tool (provider) and a static tool (extractor) operate on the same page, the extractor can serve as ground truth for debugging the interactive tool.

**The asymmetry that makes this work**:
- `chatgpt-transcript` runs against known, settled DOM state (after generation completes)
- `surf chatgpt` polls during generation, with timing-dependent state transitions
- The extractor is simpler and more reliable → it can validate the complex polling tool

**Suggested vault entry**: `METHOD - Extractor-as-Validator Debug Pattern`

---

### 4.2 Host Log Analysis

**What it is**: Interpreting structured log output from the native host process to diagnose behavior during browser automation.

**Concrete evidence this matters**:

- **The exact log format** from the bug report:
  ```
  [chatgpt] waitForResponse poll=47 len=187 stop=true finished=false ... turnCount=0 foundAssistant=false
  [chatgpt] waitForResponse poll=523 len=18933 stop=false finished=true ... turnCount=2 foundAssistant=true
  ```
- **How to read it**:
  - `poll=N`: number of polls since start
  - `len=N`: character count of last extracted text
  - `stop=true/false`: stop button visibility
  - `finished=true/false`: completion markers detected
  - `turnCount=N`: conversation turns detected
  - `foundAssistant=true/false`: assistant node found in last turn
- **What each field reveals**:
  - `turnCount=0` with `foundAssistant=false` → extraction is running but finding nothing (wrapper nodes only)
  - `len=187` with `turnCount=0` → short fragment selected (citation), not full turn
  - `turnCount=2` → user + assistant turns detected correctly

**Where logs live**:
- `snap run --shell chromium -c 'tail -n 120 /tmp/surf-host-go.log'`

**Suggested vault entry**: `KNOWLEDGE - Surf CLI Host Log Format`

---

### 4.3 Completion Gate Timing

**What it is**: A known issue where long research responses remain in polling state because the `stopVisible` flag stays `true` during browsing/tool use phases.

**Concrete evidence this matters**:

- **Bug report "Remaining Issue"**: "the provider now tracks the correct assistant turn, but on research-heavy responses the command may remain in polling because `stopVisible` stays `true` for a long time even after the extracted text stabilizes"
- **Root cause**: ChatGPT may run a browsing tool during response generation. The stop button remains visible during tool execution, confusing the completion detector.
- **Current workaround**: 6-cycle stability heuristic (6 consecutive polls with no text change over 1200ms minimum). This catches completion even when `stopVisible` is misleading.

**Source code** (in `go/internal/host/providers/chatgpt.go`):
- The polling loop checks both `stopVisible` and `finished` (copy/good response buttons)
- Text stability is tracked separately as a fallback

**Why this matters beyond ChatGPT**: Other AI providers likely have similar completion-state ambiguity. The stability heuristic is a general pattern for completion detection when primary signals are unreliable.

**Suggested vault entry**: `KNOWLEDGE - AI Provider Completion Detection`

---

## 5. Platform-Specific: ChatGPT

### 5.1 ChatGPT DOM Structure Reference

**What it is**: The documented set of attributes, selectors, and DOM nesting patterns for ChatGPT's conversation page.

**Concrete evidence this matters**:

- **Discovered through probe scripts**: `chatgpt_transcript_dom_summary.js` enumerated all relevant attributes
- **Attributes documented**:
  - `data-message-author-role`: "user" | "assistant" | "system"
  - `data-message-id`: UUID format (unique per message)
  - `data-message-model-slug`: "gpt-5-4-thinking", "gpt-4o", etc.
  - `data-message-content`: content container (contains `.markdown` child)
  - `data-testid^="conversation-turn-"`: turn boundary
- **DOM nesting pattern** discovered:
  ```
  section[data-testid="conversation-turn-N"]
    └─ div[data-message-author-role][data-message-id]  ← wrapper
        └─ div[data-message-author-role]               ← inner (duplicate, shorter text)
            └─ div.markdown                            ← actual content
  ```
- **Why this is worth a reference note**: The attributes are undocumented OpenAI internals. Future updates may change them. A reference document with timestamp and model versions would help detect drift.

**Source files**:
- `ttmp/.../scripts/chatgpt_transcript_dom_summary.js` — original discovery script
- `go/internal/cli/commands/scripts/chatgpt_transcript.js` — production selectors

**Suggested vault entry**: `REFERENCE - ChatGPT DOM Selectors`

---

### 5.2 Activity Flyout Pattern

**What it is**: The ChatGPT reasoning model UI: "Thought for N seconds" button → click → flyout with "Activity" header and reasoning chain text.

**Concrete evidence this matters**:

- **Discovered in research diary**: `SURF-20260408-R4` Steps 8-11
- **5 dedicated probe scripts**: `chatgpt_thought_trace_scan.js`, `chatgpt_thought_trace_click_probe.js`, `chatgpt_activity_button_map.js`, `chatgpt_activity_open_single.js`, `chatgpt_activity_export_first_three.js`
- **Button selector**: Text matching `/Thought for/i` on a `<button>` element
- **Flyout selectors discovered**:
  - Primary: `body > div:nth-child(5) > div > ... > section` (exact path)
  - Fallback: `[class*="stage-thread-flyout"] section`
- **Flyout content**: "Activity\nThought for 12 seconds" header, reasoning chain body, "Sources" section footer

**Timing parameters from `normalizeAndOpen()`**:
- 250ms `scrollIntoView` delay before click
- 7s maximum wait per attempt
- 2 attempts
- 400ms inter-attempt delay
- 500ms inter-turn delay in batch mode

**Source code**: `go/internal/cli/commands/scripts/chatgpt_transcript.js` lines 26-55, 120-140

**Suggested vault entry**: `REFERENCE - ChatGPT Activity Flyout Extraction`

---

### 5.3 Backend API Inaccessibility

**What it is**: The `/backend-api/conversation/<id>/textdocs` endpoint is real but requires a bearer token not available to page-context JavaScript.

**Concrete evidence this matters**:

- **Endpoint confirmed real**: `chatgpt_transcript_resource_scan.js` found the endpoint loaded in the browser
- **401 response confirmed**: `chatgpt_transcript_backend_probe.js` and `chatgpt_transcript_textdocs_probe.js` both returned `401 Unauthorized - Access token is missing`
- **Storage surfaces investigated and ruled out**:
  - `localStorage`: no bearer token (SURF-20260408-R4 Step 5)
  - `sessionStorage`: no bearer token
  - `document.cookie`: only `__Secure-next-auth.session-token`
  - `IndexedDB`: no ChatGPT application database visible to page context
- **Conclusion from research diary**: "The access token needed by `/textdocs` is not trivially available to page JS. DOM extraction is not just possible; it is the cleanest readily available strategy."

**The implications documented**:
- DOM extraction is the only viable path from the current automation surface
- Backend API access would require token capture from network layer or extension storage

**Source files**:
- `ttmp/.../scripts/chatgpt_transcript_backend_probe.js`
- `ttmp/.../scripts/chatgpt_transcript_auth_surface_scan.js`
- `ttmp/.../scripts/chatgpt_transcript_indexeddb_scan.js`

**Suggested vault entry**: `KNOWLEDGE - ChatGPT Backend API Token Capture` (as a guide for the future research point)

---

## 6. Foundational Concepts

These are general concepts that appear throughout the TR and would benefit from dedicated vault entries. Each one has a concrete source that motivates the need.

### 6.1 IIFE Wrapping

**What exists**: [[REPL Semantics, Lexical Scope, and Source-to-Source Transformation]] covers the theory extensively.

**What's missing**: The specific IIFE pattern used by the Surf CLI service worker and its practical implications.

**Concrete evidence**:
- **The wrapping code** (`src/service-worker/index.ts` line 1938):
  ```typescript
  const expression = "(async () => {\n'use strict';\n" + message.code + "\n})()";
  ```
- **Practical implications documented** (SURF-20260408-R4 Step 1):
  - Scripts must use explicit `return` statements to emit values
  - Template literals with `${...}` are corrupted by the outer string wrapping
- **Where this matters**: Every `surf-go js` command goes through this wrapper. Any probe script writer needs to know this.

**Suggested vault entry**: `KNOWLEDGE - Service Worker JS Wrapping` (as a companion to the REPL Semantics article, focused on the browser extension context)

---

### 6.2 Native Messaging (Browser Extension → Native Host)

**What it is**: The communication protocol between the Surf CLI browser extension and the `surf-host-go` native binary.

**Concrete evidence this matters**:

- **The socket connection**: `go/internal/cli/commands/chatgpt_transcript.go` line 135: `client := transport.NewClient(s.Socket, ...)`
- **The message types used**:
  - `js` — execute JavaScript (used by transcript command, tab readiness, all probe scripts)
  - `tab.new`, `tab.close`, `tab.switch` — tab management
  - `GET_CHATGPT_COOKIES`, `CHATGPT_NEW_TAB`, `CHATGPT_EVALUATE`, `CHATGPT_CLOSE_TAB`, `CHATGPT_CDP_COMMAND` — ChatGPT-specific
  - `UPLOAD_FILE` — file attachment
- **Request/response shape** (from `chatgpt_transcript.go`):
  ```go
  resp, err := ExecuteTool(ctx, client, "js", map[string]any{"code": code}, tabID, windowID)
  ```
- **The transport layer**: `gohost/internal/cli/transport/client.go` — NDJSON framing over Unix socket

**Why this matters**:
- Understanding this path explains the full execution chain from `surf-go js` to page JS
- Adding new message types requires understanding the protocol
- Debugging requires knowing where things can go wrong (extension ↔ host ↔ CDP)

**Suggested vault entry**: `ARCH - Surf CLI Native Messaging Protocol`

---

### 6.3 Chrome DevTools Protocol (CDP)

**What it is**: The protocol the Surf CLI native host uses to control the browser.

**Concrete evidence this matters**:

- **CDP is the execution engine**: `src/service-worker/index.ts` line 1925:
  ```typescript
  const result = await cdp.evaluateInFrame(tabId, message.frameId, message.code);
  ```
- **The polling loop is CDP**: `go/internal/host/providers/chatgpt.go` uses `CHATGPT_EVALUATE` (which wraps CDP `Runtime.evaluate`) in a 400ms polling loop
- **tab_ready.go uses CDP**: `probeTabReady()` sends a JS snippet via the `js` tool, which ultimately calls CDP `Runtime.evaluate`
- **CDP is used for CDP commands too**: `CHATGPT_CDP_COMMAND` passes raw CDP commands through

**Key CDP domains used by Surf CLI**:
- `Runtime.evaluate` — execute JS (primary)
- `Runtime.addBinding` — inject callable functions (for streaming, future work)
- `Log.enable` / `Log.entryAdded` — capture console output (for streaming, future work)
- `DOMStorage.getCookies` — read cookies
- `Target.createTarget` — open new tabs

**Why this matters**:
- The TR's entire JS execution infrastructure runs on CDP
- Future features (streaming, bindings, console interception) require deeper CDP knowledge
- CDP is Chrome-specific but the Surf CLI is Chromium-based (snap package)

**Suggested vault entry**: `KNOWLEDGE - Chrome DevTools Protocol for Browser Automation`

---

### 6.4 Service Worker JS Execution

**What it is**: The execution pipeline from user `surf-go js` command through extension service worker to CDP.

**Concrete evidence this matters**:

- **The full pipeline** (`src/service-worker/index.ts` lines 1930-1943):
  1. User calls `surf-go js 'return document.title'`
  2. Go command sends `{type: "EXECUTE_JAVASCRIPT", code: "return document.title"}` via socket
  3. Extension service worker receives message (line 1930: `case "EXECUTE_JAVASCRIPT"`)
  4. Service worker wraps code in async IIFE (line 1938)
  5. Native host receives wrapped code, calls CDP `Runtime.evaluate` (line 1925)
  6. CDP returns result
  7. Native host sends back to extension
  8. Extension sends result to Go command via socket
  9. Result printed to terminal

- **Why explicit `return` is needed**: The IIFE returns the last expression's value. Without `return`, the result is `undefined`.

- **Why template literals are dangerous**: The outer wrapping uses string concatenation: `"(async () => {\n'use strict';\n" + message.code + "\n})()"`. Any `${...}` in user code is interpolated by the JavaScript string concatenation, corrupting the user's template literal.

- **Where this is documented**: SURF-20260408-R4 Step 1 — "Important implementation detail: The current extension-side EXECUTE_JAVASCRIPT implementation wraps the provided code inside an async IIFE and only returns the value if the script explicitly uses `return ...` at top level. That means research scripts sent through `surf-go js --file` should avoid template literals and should end in an explicit top-level `return`."

**Suggested vault entry**: `ARCH - Browser Extension JS Execution Pipeline`

---

## Summary: Suggested Priority Order with Concrete Grounding

| Priority | Topic | Type | Evidence Source | Why Now |
|----------|-------|------|-----------------|---------|
| 1 | **ChatGPT DOM Selectors** | Reference | 17 probe scripts + chatgpt_transcript.js | Immediately useful for future probes |
| 2 | **Browser Probe Script Methodology** | Playbook | 17 scripts in ttmp/, SURF-20260408-R4 research diary | Reusable across all providers |
| 3 | **Tab Readiness Detection** | Knowledge | tab_ready.go, kagi_search.go, kagi_assistant.go | Reusable for Kagi, Gmail, etc. |
| 4 | **Native Messaging Protocol** | Architecture | transport.NewClient(), ExecuteTool(), message types in chatgpt.go | Core infrastructure documentation |
| 5 | **Chrome DevTools Protocol** | Knowledge | cdp.evaluateInFrame(), polling loop in chatgpt.go | Foundational for all browser automation |
| 6 | **Service Worker JS Execution** | Architecture | src/service-worker/index.ts lines 1930-1943 | Explains the whole execution path |
| 7 | **IIFE Wrapping (service worker)** | Knowledge | src/service-worker/index.ts line 1938, SURF-20260408-R4 Step 1 | Companion to existing REPL article |
| 8 | **Interactive Overlay Extraction** | Knowledge | normalizeAndOpen() in chatgpt_transcript.js, 5 activity probe scripts | Generalizable beyond ChatGPT |
| 9 | **Dual-Mode Glazed Commands** | Playbook | chatgpt_transcript.go lines 81-159 | Reusable command authoring pattern |
| 10 | **AI Provider Completion Detection** | Knowledge | Bug report "Remaining Issue", chatgpt.go polling logic | Generic pattern for all AI providers |

---

## Cross-References

- [[TR-2026-0411-001 - ChatGPT Transcript Extraction System - Implementation and Methodology]] — Parent report
- [[TR-2026-0411-001 - Further Research Points]] — Open investigation questions
- [[REPL Semantics, Lexical Scope, and Source-to-Source Transformation]] — IIFE theory (partial overlap)
- [[PROJ - go-go-goja jsverbs - JavaScript to Glazed Commands]] — Command authoring pattern
- [[PROJ - DOM Scraping Experiment - Web to Markdown via JS DOM Queries]] — Parallel DOM work
- [[ARTICLE - surf-go Browser Verbs - Using JS Probes to Build Reliable Web Automation]] — Methodology context

---

*This document is a catalog of knowledge base expansion priorities with concrete evidence. Each topic should be developed into a standalone vault entry referencing the specific files and research diary steps that motivate it.*
