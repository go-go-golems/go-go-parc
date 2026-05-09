---
title: Surf CLI - ChatGPT Transcript Extraction
aliases:
  - Surf ChatGPT Transcript Extraction
  - ChatGPT DOM Extraction
  - Surf CLI Transcript Research
tags:
  - project
  - surf-cli
  - chatgpt
  - browser-automation
  - dom-extraction
  - native-messaging
status: active
type: project
created: 2026-04-11
repo: /home/manuel/code/others/llms/pi/nicobailon/surf-cli
---

# Surf CLI - ChatGPT Transcript Extraction

This project implements reliable transcript extraction from ChatGPT conversations through DOM-based browser automation. The system navigates to conversation pages, extracts message content using data attributes, and handles edge cases like duplicate nodes and citation fragments.

> [!summary]
> The project delivers two related capabilities:
> 1. **Interactive ChatGPT provider** (`surf chatgpt`) - sends prompts and polls for responses
> 2. **Post-hoc transcript export** (`surf chatgpt-transcript`) - extracts full conversation history from existing pages
> 
> Both rely on the same core DOM extraction algorithm that survived a significant bug where citation fragments were mistaken for full assistant responses.

## Why this project exists

The Surf CLI needs to interact with ChatGPT as one of several AI providers (alongside Claude, Gemini, Grok, and Perplexity). Unlike APIs with stable endpoints, ChatGPT's web interface requires browser automation. The transcript extraction problem emerged when the interactive provider returned garbled output—source citations like "MIT OpenCourseWare" and "Mathematical Association of America"—instead of the actual assistant response body.

The research documented in [[SURF-20260408-R4]] established that the transcript data is available in the rendered DOM, but requires careful extraction to avoid common pitfalls:

- Duplicate message nodes (wrappers vs content containers)
- Citation/source fragments that appear as separate assistant-marked elements
- Activity/thought traces that need optional expansion

## Current project status

The implementation is functional and has survived real-world validation. The core extraction algorithm works, though the completion-gate polling behavior for long-running research responses may need refinement.

What works today:

- `surf chatgpt-transcript` command exports full conversations to Markdown or JSON
- `--with-activity` flag expands thought traces for reasoning models
- Turn-based extraction prevents the citation-fragment bug
- Deduplication by `data-message-id` handles ChatGPT's duplicate DOM nodes

Recent validation (April 10, 2026):

- A conversation that previously returned only citation fragments now extracts correctly
- The host logs show `turnCount=2` with `foundAssistant=true` and stable non-zero text growth
- `chatgpt-transcript` confirmed the full 18,933-character response was present in the DOM

## Project shape

The extraction system has three layers:

```
surf-go CLI command
  -> chatgpt_transcript.go (Glazed dual-mode command)
  -> embedded chatgpt_transcript.js (browser-side extractor)
  -> CDP/Extension bridge (native messaging to Chrome)
  -> ChatGPT conversation page DOM
```

Key code locations:

- `go/internal/cli/commands/chatgpt_transcript.go` - Go command implementation
- `go/internal/cli/commands/scripts/chatgpt_transcript.js` - embedded browser extractor
- `go/internal/host/providers/chatgpt.go` - interactive provider polling logic
- `go/internal/cli/commands/js.go` - underlying `surf-go js` command used during research
- `ttmp/2026/04/08/SURF-20260408-R4--surf-go-non-provider-cli-parity-architecture-and-implementation-guide/scripts/` - research probe scripts

## Architecture

### DOM Extraction Strategy

The core insight from the research diary: ChatGPT renders conversation data into the DOM with stable data attributes. The extraction algorithm:

1. **Select conversation turns**: Walk `section[data-testid^="conversation-turn-"]` in DOM order
2. **Collect candidates**: Within each turn, find all `[data-message-author-role]` nodes
3. **Deduplicate by message ID**: Group nodes by `data-message-id` attribute
4. **Select longest text**: Keep the candidate with maximum `text.length` per message ID
5. **Filter empty**: Skip nodes with no text content

This approach is robust against ChatGPT's DOM structure where both wrapper containers and content nodes carry the same `data-message-author-role` attribute.

### Turn-Based vs Global Selection

The critical fix for the citation-fragment bug: extract within conversation turn boundaries rather than scanning the entire document globally.

```javascript
// Anti-pattern (caused the bug)
const allAssistantNodes = document.querySelectorAll('[data-message-author-role="assistant"]');
const lastAssistant = allAssistantNodes[allAssistantNodes.length - 1];

// Correct approach (turn-based)
const turns = document.querySelectorAll('section[data-testid^="conversation-turn-"]');
const lastTurn = turns[turns.length - 1];
const candidates = lastTurn.querySelectorAll('[data-message-author-role="assistant"]');
// ...deduplicate and select best within turn boundary
```

Citation fragments appear as separate assistant-marked nodes, but they have short text lengths. The turn-based longest-text selection naturally prefers the full response body over these fragments.

### Activity/Thought Trace Expansion

For reasoning models (o3, o4-mini, etc.), ChatGPT shows "Thought for N seconds" buttons that expand to reveal the model's reasoning chain:

```javascript
// Activity detection and expansion
const thoughtButton = section.querySelector('button');
if (/Thought for/i.test(thoughtButton?.textContent)) {
  button.click();
  // Wait for flyout with Activity header matching duration
  const activitySection = waitForActivityFlyout(duration);
  // Attach activity text back to assistant turn
}
```

The implementation handles race conditions by:
- Matching the Activity flyout header text against the button's duration
- Retrying once if the first click doesn't produce a matching flyout
- Waiting up to 7 seconds for the flyout to appear

## Implementation details

### Browser-Side Extractor (chatgpt_transcript.js)

The embedded JavaScript runs in the ChatGPT page context via CDP's `Runtime.evaluate`:

```javascript
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function extractSectionMessage(section, index) {
  const candidates = Array.from(section.querySelectorAll('[data-message-author-role]'));
  
  // Deduplicate by message ID, keeping longest text
  const byMessageId = new Map();
  for (const node of candidates) {
    const role = node.getAttribute('data-message-author-role') || 'unknown';
    const messageId = node.getAttribute('data-message-id') || `${role}:${index}:${byMessageId.size}`;
    const model = node.getAttribute('data-message-model-slug') || null;
    const text = (node.innerText || '').trim();
    
    if (!text) continue;
    
    const existing = byMessageId.get(messageId);
    if (!existing || text.length > existing.text.length) {
      byMessageId.set(messageId, { role, model, messageId, text, textLength: text.length });
    }
  }
  
  // Select best candidate for this turn
  const items = Array.from(byMessageId.values()).sort((a, b) => b.textLength - a.textLength);
  const best = items[0];
  
  // Check for thought button
  const thoughtButton = Array.from(section.querySelectorAll('button'))
    .find((node) => /Thought for/i.test((node.textContent || '').trim()));
  
  return {
    index,
    role: best.role,
    model: best.model,
    messageId: best.messageId,
    text: best.text,
    hasThought: !!thoughtButton,
    thoughtButtonText: thoughtButton?.textContent?.trim(),
  };
}
```

### Go Command Structure

The `chatgpt-transcript` command implements Glazed's dual-mode pattern:

```go
// Writer mode (default): Renders Markdown transcript to stdout
func (c *ChatGPTTranscriptCommand) RunIntoWriter(ctx context.Context, w io.Writer, parsedLayers *layers.ParsedLayers, ps map[string]interface{}) error

// Glaze mode (--with-glaze-output): Structured rows for downstream processing
func (c *ChatGPTTranscriptCommand) RunIntoGlazeProcessor(ctx context.Context, gp *glazed.GlazeProcessor, parsedLayers *layers.ParsedLayers, ps map[string]interface{}) error
```

Command flags:

| Flag | Purpose |
|------|---------|
| `--with-activity` | Expand thought traces for reasoning models |
| `--activity-limit N` | Only expand first N activity buttons |
| `--export-file path` | Write transcript to file (Markdown or JSON) |
| `--export-format` | `markdown` or `json` |
| `--with-glaze-output` | Emit structured rows instead of Markdown |

### Research Probe Scripts

The development process involved systematic DOM exploration through the `surf-go js` command:

| Script | Purpose |
|--------|---------|
| `chatgpt_transcript_dom_summary.js` | Raw inventory of message nodes |
| `chatgpt_transcript_resource_scan.js` | Identify backend endpoints (found `/textdocs` but requires auth) |
| `chatgpt_transcript_backend_probe.js` | Test direct API calls (returned 401) |
| `chatgpt_transcript_cache_scan.js` | Check localStorage/sessionStorage for cached data |
| `chatgpt_transcript_indexeddb_scan.js` | Inspect IndexedDB contents |
| `chatgpt_transcript_extract_dom.js` | Refined extractor with deduplication |

Key finding: The `/backend-api/conversation/<id>/textdocs` endpoint exists but requires a bearer token not available to page JavaScript. DOM extraction remains the most reliable approach.

### Completion Detection (Interactive Provider)

The interactive `chatgpt` command uses polling logic in `waitForResponse`:

```javascript
// Poll every 400ms until:
// 1. Stop button not visible (generation complete)
// 2. Turn shows finished markers (copy/good response buttons)
// 3. OR: Text stable for 6 consecutive polls and 1200ms minimum
const finished = Boolean(lastAssistantTurn.querySelector(
  '[data-testid="copy-turn-action-button"], [data-testid="good-response-turn-action-button"]'
));
const stopVisible = Boolean(document.querySelector('[data-testid="stop-button"]'));
```

The stability heuristic prevents premature return during streaming, but may delay on long-running browsing/research responses where `stopVisible` remains true for extended periods.

## The Citation-Fragment Bug

### Symptoms

User-visible failure: Output consisted of repeated source labels:

```
MIT OpenCourseWare
MIT Press
Mathematical Association of America
MIT OpenCourseWare
...
```

Missing: The actual substantive response about "The Art of Insight in Science and Engineering."

### Root Cause

The original polling logic found the globally last assistant-marked node:

```javascript
const assistantNodes = document.querySelectorAll('[data-message-author-role="assistant"]');
const lastNode = assistantNodes[assistantNodes.length - 1];
```

ChatGPT renders citations as separate assistant-marked elements at the end of the document. The last such node was a citation fragment, not the main response body.

### Fix

Changed to turn-based extraction that mirrors the transcript command:

1. Find the last conversation turn containing assistant content
2. Gather all assistant candidates within that turn only
3. Deduplicate by `data-message-id`
4. Select the longest non-empty text

Validation: The same conversation that returned fragments now returns the full 18,933-character response.

## Current user-facing commands

```bash
# Export transcript from current ChatGPT tab
surf-go chatgpt-transcript --socket-path /path/to/surf.sock

# Export with thought traces expanded
surf-go chatgpt-transcript --with-activity --socket-path /path/to/surf.sock

# Save to file
surf-go chatgpt-transcript --export-file transcript.md --export-format markdown

# Structured output for processing
surf-go chatgpt-transcript --with-glaze-output --output json

# Interactive ChatGPT query (separate path, uses same extraction)
surf chatgpt "Explain quantum computing"
```

## Important project docs

Ticket documentation in repo:

- `ttmp/2026/04/08/SURF-20260408-R4--surf-go-non-provider-cli-parity-architecture-and-implementation-guide/reference/02-chatgpt-transcript-download-research-diary.md`
- `ttmp/2026/04/10/SURF-20260410-R6--shared-tab-readiness-helper-and-chatgpt-extraction-bug/reference/01-chatgpt-extraction-bug-report.md`

These contain:
- Step-by-step research methodology
- All probe scripts with exact commands used
- Failed approaches (backend API, IndexedDB, localStorage)
- Decision log for DOM-based approach

## Open questions

- Should the completion gate continue waiting for `stopVisible == false` on long browsing/research responses, or is stability-based detection sufficient?
- Is there a reliable way to extract the bearer token for the `/textdocs` backend endpoint, or should DOM extraction remain the permanent solution?
- Should the transcript command support automatic pagination for very long conversations?

## Near-term next steps

- Validate end-to-end interactive `surf chatgpt` on long-form prompts with the updated host
- Decide whether to add a `--streaming` flag for real-time partial response delivery
- Consider adding transcript export directly from the interactive command (auto-save conversation)

## Project working rule

> [!important]
> DOM structure changes. The extraction selectors should be validated periodically against live ChatGPT pages, and the probe scripts in `ttmp/` preserved for rapid re-validation when issues are reported.
