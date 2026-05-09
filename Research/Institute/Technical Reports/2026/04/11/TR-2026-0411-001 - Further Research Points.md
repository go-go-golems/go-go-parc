---
title: "TR-2026-0411-001 Further Research Points"
subtitle: "Open Problems and Investigation Agenda from the ChatGPT Transcript Extraction System Report"
aliases:
  - ChatGPT Extraction Further Research
  - TR-2026-0411-001 Research Agenda
tags:
  - research
  - technical-report
  - surf-cli
  - chatgpt
  - dom-extraction
  - browser-automation
  - research-agenda
related:
  - "[[TR-2026-0411-001 - ChatGPT Transcript Extraction System - Implementation and Methodology]]"
  - "[[PROJ - DOM Scraping Experiment - Web to Markdown via JS DOM Queries]]"
  - "[[ARTICLE - surf-go Browser Verbs - Using JS Probes to Build Reliable Web Automation]]"
status: active
type: research-agenda
created: 2026-04-11
parent-report: TR-2026-0411-001
---

# TR-2026-0411-001 Further Research Points

This document collects the open research questions and investigation paths that emerged from the [[TR-2026-0411-001 - ChatGPT Transcript Extraction System - Implementation and Methodology|ChatGPT Transcript Extraction System report]]. Each point includes the problem statement, why it matters, current state of knowledge, and a tentative research path.

---

## 1. Token Capture for Backend API Access

### Problem Statement

The ChatGPT web interface has a `/backend-api/conversation/<id>/textdocs` endpoint that returns structured transcript data. This endpoint requires a bearer token. Page-context JavaScript cannot access this token. The TR confirmed this through:

- `localStorage` scan: no bearer token
- `sessionStorage` scan: no bearer token
- `document.cookie` scan: only `__Secure-next-auth.session-token`, not API bearer
- Global window keys: no obvious Apollo/GraphQL auth caches

### Why It Matters

DOM extraction is fragile. ChatGPT's DOM structure changes without notice, selectors break, and the current deduplication algorithm relies on undocumented attributes (`data-message-id`, `data-testid^="conversation-turn-"`) that are implementation details. A backend API approach would be:

- More stable across UI updates
- Faster (no DOM traversal, no polling)
- Capable of extracting data that isn't rendered in the DOM (edit history, version snapshots, deleted messages)

### Current State

The `/textdocs` endpoint is confirmed to exist (returns 401 Unauthorized). The token appears to live in one of:

1. **Extension storage** — the Surf CLI browser extension could capture the token during the OAuth flow
2. **Network interception** — the extension's service worker could capture the token from HTTP headers on any ChatGPT API request
3. **Memory of the page process** — CDP's `Runtime.evaluate` might expose token globals if they're assigned to `window` in the page's JavaScript context
4. **Background page context** — if ChatGPT stores the token in `localStorage` but the extension has cross-origin access to ChatGPT's storage

### Tentative Research Path

**Step 1: Network Interception Probe**
Write a service worker probe that logs all fetch requests matching `chat.openai.com/backend-api/*`. The first such request after page load will contain the Authorization header.

**Step 2: Storage Access Investigation**
Use CDP's `DOMStorage.getCookies` or `StorageAccessAPI` to check if the extension can read ChatGPT's localStorage. If so, search for patterns matching bearer tokens (base64 strings, "Bearer " prefixes).

**Step 3: Page Context Token Probe**
Run `Object.keys(window).filter(k => /token|auth|bearer|openai/i.test(k))` in the page context. Also probe for `window.__NEXT_DATA__`, GraphQL cache objects, and Apollo client state.

**Step 4: Extension Background Page**
If the extension has a background/service worker that persists across navigations, it may hold the token from the OAuth handshake. Probe the extension's `chrome.storage.local` and message passing channels.

**Deliverable**: A decision document stating whether backend API access is viable, which capture path works, and what the implementation would look like.

---

## 2. Streaming Extraction via CDP Bindings

### Problem Statement

The current interactive provider polls the DOM at 400ms intervals using CDP's `Runtime.evaluate`. This means:

- Partial responses are delayed up to 400ms
- The polling loop keeps the CDP session active continuously
- High-frequency polling may cause DOM stability issues on large responses

### Why It Matters

For long responses (the 18,933-character research response in the bug report), users want to see text as it arrives, not after the full generation completes. Streaming extraction would also reduce CDP session overhead and enable the transcript command to capture partial transcripts during generation.

### Current State

CDP offers two event-driven alternatives to polling:

1. **`Runtime.addBinding`** — inject a JavaScript function that the page calls when state changes. ChatGPT does call internal event handlers, but whether they surface to a custom binding is unknown.

2. **`DOMutationObserver` via JS** — the page's JavaScript could register a MutationObserver that calls a CDP binding on DOM mutations. ChatGPT likely already has MutationObservers; the question is whether they can be supplemented with a custom observer.

3. **`console` API interception** — ChatGPT may log token chunks or turn boundaries to `console.log`. CDP's `Log.enable` and `Log.entryAdded` can capture these without page-side modifications.

### Tentative Research Path

**Step 1: Console API Probe**
Enable CDP logging (`Log.enable`) and capture all console messages during a ChatGPT generation. Look for patterns: token counts, turn boundaries, model names, partial text chunks.

**Step 2: MutationObserver Injection**
Inject a script that registers a `MutationObserver` watching `[data-message-content]` elements. On mutation, call `window.surfStreamHit()` — a binding added via `Runtime.addBinding`. Log the binding calls in CDP.

**Step 3: CDP Event Surface Survey**
Use `Runtime.discardContextResults`, `Debugger.enable`, and `Log.enable` simultaneously during a generation. Build a complete event log to identify which CDP events fire during token arrival.

**Step 4: Binding Feasibility Test**
Try `Runtime.addBinding({ name: 'surfStream' })` before sending a prompt. Inject the binding function alongside the prompt and see if ChatGPT's React internals ever call it.

**Deliverable**: A streaming architecture document specifying which event source works, the latency characteristics, and how to integrate with the existing dual-mode command pipeline.

---

## 3. Conversation Pagination and Lazy Loading

### Problem Statement

The DOM extraction algorithm assumes all conversation turns are present in the DOM. For long conversations, ChatGPT may lazy-load historical turns as the user scrolls up. The current algorithm would only extract the visible subset.

### Why It Matters

Post-hoc transcript extraction is the primary use case. Users who want to export a 200-turn conversation will get an incomplete result if pagination isn't handled.

### Current State

The TR's probe scripts ran on conversations with 2-5 turns. No investigation of pagination behavior exists. Open questions:

- Does ChatGPT virtualize (remove off-screen turns from the DOM) or just lazy-load?
- Is there a "load more" mechanism in the DOM, or does it use infinite scroll?
- Does the conversation have a unique ID that can be used with a backend pagination API?
- Does the `data-testid="conversation-turn-N"` numbering reset on pagination?

### Tentative Research Path

**Step 1: Long Conversation DOM Survey**
Open a ChatGPT conversation with 50+ turns. Use CDP to:

- Count `section[data-testid^="conversation-turn-"]` nodes
- Check for virtual scrolling indicators (`overflow`, `height`, `transform` on parent containers)
- Scroll to top and count again to see if nodes are added

**Step 2: Pagination Mechanism Identification**
Look for "Load more", "Continue", or spinner elements. Check if `IntersectionObserver` is watching a sentinel element at the top of the conversation.

**Step 3: Scroll-to-Load Script**
Write a probe script that:
1. Records the current turn count
2. Scrolls to the top
3. Waits for new nodes to appear
4. Repeats until turn count stabilizes
5. Reports the final count and any pagination API calls observed

**Step 4: Backend Pagination Probe**
If a conversation ID is extractable from the page URL (`/c/<id>`), test if the backend API supports pagination for that ID without authentication.

**Deliverable**: Pagination handling plan specifying whether the fix is scroll-automation, backend API, or both.

---

## 4. Selector Fallback Chain

### Problem Statement

The current extraction relies on undocumented ChatGPT attributes:

- `data-message-author-role`
- `data-message-id`
- `data-message-model-slug`
- `data-testid^="conversation-turn-"`

OpenAI can change these at any time, breaking extraction silently.

### Why It Matters

Production reliability. A broken extractor means users can't export conversations, which is a core feature regression.

### Current State

No fallback chain exists. The TR notes this as a long-term concern but doesn't specify the fallback strategy.

### Tentative Research Path

**Step 1: Attribute Stability Survey**
Track ChatGPT's attribute usage across:
- Multiple conversation types (text, code, vision)
- Multiple models (GPT-4o, GPT-5, o3, o4-mini)
- Multiple browser sessions
- App updates (if detectable via version strings)

**Step 2: Natural Language Fallback**
If `data-message-author-role` disappears, try:
- `article[role="article"]` with ARIA roles
- `.markdown` content containers
- Text-based role detection ("User:", "Assistant:" prefixes)

**Step 3: Selector Ladder Implementation**
Build a selector chain in priority order:
```
1. [data-message-author-role]         # Primary (documented above)
2. [data-turn]                         # Fallback turn attribute
3. section > div > div                 # DOM structure fallback
4. .markdown                            # Content class fallback
5. font[size][class*="assistant"]       # Text formatting fallback
```

Each level should be tested independently with a confidence score.

**Step 4: Self-Healing Probe**
Write a probe script that runs a fallback chain against a known conversation, reports which selectors matched, and logs the structural features of each level. This can be run periodically or on-demand to detect selector drift.

**Deliverable**: A self-documenting selector ladder with per-level confidence scores and a detection script for selector drift.

---

## 5. Cross-Provider DOM Extraction Patterns

### Problem Statement

The Surf CLI supports Claude, Gemini, Perplexity, and Grok in addition to ChatGPT. Each provider has its own DOM structure, its own reasoning model UI, and its own extraction challenges.

### Why It Matters

The methodology proven in this TR — systematic probe scripts, turn-based deduplication, Activity flyout extraction — is likely generalizable. A shared framework would reduce per-provider investigation time from weeks to days.

### Current State

No systematic extraction documentation exists for the other providers. The only parallel work is the [[PROJ - DOM Scraping Experiment - Web to Markdown via JS DOM Queries|DOM Scraping Experiment]], which covers general web pages but not AI provider interfaces.

### Tentative Research Path

**Step 1: Provider DOM Comparison**
For each provider, run the same probe script structure:

1. DOM inventory (what attributes, roles, structures exist?)
2. Message boundary detection (how is a turn defined in the DOM?)
3. Assistant content identification (what makes a node "assistant" vs "user"?)
4. Reasoning/thought trace identification (do reasoning models have a visible thought trace?)
5. Export capability (is there a native download/export mechanism?)

**Step 2: Pattern Abstraction**
Extract the common algorithm skeleton:

```
For each provider:
  1. Identify turn boundaries (section | article | role-marked container)
  2. Within turn: collect role-marked nodes
  3. Deduplicate by message ID or content similarity
  4. Select best content node (longest text, correct role)
  5. Handle provider-specific overlays (thought traces, citations, code blocks)
```

**Step 3: Provider-Specific Overlays**
Each provider has unique overlay patterns:

| Provider | Reasoning UI | Notes |
|----------|--------------|-------|
| ChatGPT | "Thought for Ns" flyout | Documented in TR |
| Claude | Thinking block in response | Needs investigation |
| Gemini | "Thinking" expandable | Needs investigation |
| Perplexity | "N seconds thinking" | Needs investigation |
| Grok | "Reasoning" inline | Needs investigation |

**Step 4: Unified Extraction Framework**
Design a provider interface:

```typescript
interface ProviderExtractor {
  name: string;
  detectTurn(node: Element): TurnInfo | null;
  extractMessage(node: Element): MessageContent | null;
  extractThoughtTrace?(node: Element): ThoughtContent | null;
  selectorLadder: string[];  // Priority-ordered selectors
}
```

**Deliverable**: A cross-provider extraction framework with at least ChatGPT (proven), Claude (investigated), and one more provider.

---

## 6. go-minitrace Integration for Probe Script Sessions

### Problem Statement

The TR produced 17 probe scripts across multiple investigation sessions. These are preserved as individual files in `ttmp/`, but they aren't systematically searchable, queryable, or comparable. The [[PROJ - Improving Minitrace and Transcript Analysis|Minitrace project]] exists precisely for this kind of session analysis.

### Why It Matters

Future investigations will follow the same pattern: probe scripts, discovery logs, failed attempts, final solution. Without a transcript analysis framework, these sessions are dead artifacts. With it, patterns across investigations can be found.

### Current State

The TR's probe scripts are stored as plain `.js` files with numbered prefixes. No minitrace annotations exist. The research diary in `ttmp/` captures decisions but isn't structured for query.

### Tentative Research Path

**Step 1: Probe Script Annotation Standard**
Define a comment-based annotation format for probe scripts:

```javascript
// @minitrace:start probe=chatgpt_transcript_dom_summary
// @minitrace:tag phase=dom-inventory
// @minitrace:tag site=chatgpt
// @minitrace:expect selector=[data-message-author-role]
```

**Step 2: Session Conversion**
Write a converter that:

1. Reads annotated probe scripts
2. Extracts the annotations as minitrace events
3. Attaches execution metadata (timestamp, duration, success/failure, output)
4. Produces a minitrace archive

**Step 3: Cross-Investigation Queries**
Test queries like:

- "Show all probe scripts that failed on selector `[data-message-id]`"
- "Compare probe execution times across ChatGPT, Claude, and Perplexity"
- "Find all scripts that required retry logic"

**Step 4: Investigation Diary Automation**
Generate a research diary from the minitrace archive: timeline of probes, which worked, which failed, and why.

**Deliverable**: A probe script annotation standard and a conversion pipeline that feeds into the existing go-minitrace infrastructure.

---

## 7. Template Literal Restrictions in Service Worker IIFE

### Problem Statement

The service worker's `EXECUTE_JAVASCRIPT` handler wraps user code in:

```typescript
const expression = "(async () => {\n'use strict';\n" + message.code + "\n})()";
```

User code containing `${...}` template literal syntax will be corrupted by the outer string wrapping.

### Why It Matters

Researchers writing probe scripts must remember to avoid template literals. This is a footgun that will cause silent failures.

### Current State

Documented as a known limitation in the TR. No fix exists. Workaround is to use string concatenation instead of template literals.

### Tentative Research Path

**Step 1: Alternative Wrapper Design**
Explore wrapping options that don't break template literals:

1. **Function constructor**: `new Function('code', code)` — handles template literals but changes `this` binding
2. **Dedicated callback channel**: Send code to the service worker, which evaluates and returns via `chrome.runtime.sendMessage` — avoids wrapping entirely
3. **eval with controlled scope**: Use `Reflect.eval` or iframe sandboxing to isolate eval context

**Step 2: Backward Compatibility Test**
If changing the wrapper, test that existing probe scripts still work. The risk is breaking every existing command.

**Step 3: Script Preprocessor**
Instead of changing the wrapper, add a preprocessor step that rewrites template literals in user code before wrapping. This is the approach the goja REPL uses (see [[PROJ - go-go-goja jsverbs - JavaScript to Glazed Commands|jsverbs]] source rewriting).

**Step 4: Error Detection**
Add a runtime check: after evaluation, check if the returned value contains `\${` (indicating corrupted template literal). If so, return an error with a clear message.

**Deliverable**: A fix that either removes template literal restrictions or provides a clear error when they're used incorrectly.

---

## Priority Order

Based on impact and effort, the suggested investigation order is:

| Priority | Research Point | Impact | Effort | Rationale |
|----------|--------------|--------|--------|-----------|
| 1 | Selector Fallback Chain | High | Medium | Prevents silent breakage |
| 2 | Cross-Provider DOM Patterns | High | High | Multiplies value of methodology |
| 3 | Token Capture | High | High | Solves fundamental limitation |
| 4 | Conversation Pagination | Medium | Medium | Core use case completeness |
| 5 | Streaming via CDP | Medium | Medium | UX improvement |
| 6 | go-minitrace Integration | Low | Low | Workflow improvement |
| 7 | Template Literal Fix | Low | Medium | Footgun removal |

---

## Cross-References

- [[TR-2026-0411-001 - ChatGPT Transcript Extraction System - Implementation and Methodology]] — Parent report
- [[PROJ - DOM Scraping Experiment - Web to Markdown via JS DOM Queries]] — Parallel DOM extraction work
- [[PROJ - Claude Agent SDK - Teaching an AI to Write Web Scrapers]] — Automated DOM investigation
- [[PROJ - Improving Minitrace and Transcript Analysis]] — Transcript analysis infrastructure
- [[ARTICLE - surf-go Browser Verbs - Using JS Probes to Build Reliable Web Automation]] — Methodology context
- [[PROJ - go-go-goja jsverbs - JavaScript to Glazed Commands]] — Command authoring patterns

---

*This document is a living research agenda. Update as investigations complete or new questions emerge.*
