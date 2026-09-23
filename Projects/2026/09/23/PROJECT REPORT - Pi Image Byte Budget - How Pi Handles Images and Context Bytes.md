---
title: "Pi Image Byte Budget — How the Pi Coding Agent Handles Images and Context Bytes"
aliases:
  - Pi image byte budget report
  - Pi 413 PAYLOAD_TOO_LARGE investigation
  - Pi image-budget extension report
  - How Pi handles images and context bytes
tags: [project-report, pi, pi-extensions, images, context-window, compaction, lunaroute, vision-models, token-accounting]
status: active
type: project-report
created: 2026-09-23
repo: /Users/manuel.odendahl/code/wesen/2026-04-21--pi-extensions
source_ticket: PI-EXT-IMAGE-BUDGET
---

# Pi Image Byte Budget — How the Pi Coding Agent Handles Images and Context Bytes

This report explains why an image-heavy Pi coding-agent session kept dying with `413 PAYLOAD_TOO_LARGE` on the Lunaroute gateway while its token context was nearly empty, and it teaches the design of the fix: the **image-budget** extension that makes image bytes in the model context visible, retroactively reducible, and gateable. The goal is not only to record the failure. The goal is to teach how Pi actually works: how sessions store images, why the token-based compaction meter is structurally blind to image bytes, where images get resized on their way into history, which model-level config knobs exist (and which are dead), how overflow recovery pattern-matches provider errors, and which extension hooks cover each part of the problem. Everything here was verified against the installed Pi distribution and a 78 MB forensic session file, with file paths, symbols, signatures, and pseudocode, so that implementation work does not have to re-derive it.

> [!summary]
> A byte-capped gateway (Lunaroute, 16 MiB request body) rejects image-heavy sessions that Pi's token meter considers nearly empty: Pi estimates every image at a flat 1200 tokens (`ESTIMATED_IMAGE_CHARS = 4800`), so auto-compaction never fires while base64 image payloads accumulate to 17.7 MB. The fix has three layers — configure per-model `inputLimits.images.resize` profiles in `models.json` (works today), build the `image-budget` extension (byte meter widget, retroactive slimming via `appendContextEdit`, upfront gating + 413 recovery), and validate byte accounting with `Σ base64 + Σ text + ~1–2% overhead`, which matched Lunaroute's `declared_bytes` within 1%.

## Goal

This document is the background text for the **image-budget** extension: a pi extension that makes image bytes in the model context visible, retroactively reducible, and gateable. It collects everything verified about pi's internals during the investigation of 2026-09-23, with file paths, symbols, signatures, and pseudocode, so that implementation work does not have to re-derive it.

Everything in this document was verified against the installed pi distribution at `/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/` (dist tree, `@earendil-works/pi-ai` and `@earendil-works/pi-agent-core` in its `node_modules/`), the user configuration at `~/.pi/agent/`, and the forensic session file referenced in [Chapter 9](#9-the-byte-accounting-model-validated). Where a claim comes from public web sources rather than the local installation, it is labeled as such.

## Context

A coding-agent session on the Lunaroute gateway (`https://gw.lunaroute.com/v1`) repeatedly died with:

```
413: {"code":"PAYLOAD_TOO_LARGE","declared_bytes":17706402,"max_bytes":16777216,
      "message":"Request body exceeds the configured limit"}
```

The session's *token* context was nearly empty (its model declares a 524k–1M token window); the *serialized HTTP request body*, dominated by base64 images, was 17.7 MB against a 16 MiB gateway cap. This is the motivating failure: **a transport-byte limit that is invisible to every token-based safety mechanism in pi**.

---

## 1. The Failure Mode: Byte-Capped Gateways

### 1.1 Two independent limits

Every agent harness — pi included — resends the *entire* conversation history with every LLM request. Two limits therefore apply simultaneously:

1. **Model context window (tokens).** Determined by the model. Pi models it via `Model.contextWindow` and meters it with the machinery in [Chapter 3](#3-token-estimation-why-the-meter-is-blind).
2. **Request body size (bytes).** Determined by the HTTP path between client and model. Pi models this — nominally — via `ModelInputLimits.maxRequestBytes`, but **never enforces it** (see [Chapter 5](#5-model-input-limits-configuration-and-dead-config)).

Image tokens are *capped server-side* on modern vision models (DeepSeek: ≤384 tokens/image regardless of resolution; GLM: ~117–384; see [Chapter 8](#8-vision-model-sizing-facts)). Image *bytes* are not capped by the model at all — they are capped by whoever runs the HTTP gateway.

### 1.2 The 413 anatomy

Lunaroute's error is precise and useful:

```json
{"code":"PAYLOAD_TOO_LARGE",
 "declared_bytes":17706402,     // Content-Length of the JSON request body
 "max_bytes":16777216}          // 16 MiB configured gateway limit
```

`declared_bytes` counts the **whole serialized JSON request**: all message text, all base64 image payloads (base64 inflates binary data by ×4/3, plus JSON string escaping), tool declarations, and framing.

### 1.3 Is 16 MiB low?

For single-shot image APIs, no: per-image caps elsewhere are 5–32 MB (Anthropic 5 MB/image, OpenAI ~20 MB, Google 20 MB inline). For an agent loop where the body is the *cumulative history*, it is tight:

| Gateway / provider | Request body limit |
|---|---|
| **Lunaroute** | **16 MiB (16,777,216 B), configured** |
| Google Gemini (inline) | 20 MB total request |
| Anthropic | 5 MB/image, ≤100 images/request |
| OpenAI | ~20 MB/image, ~50 MB requests |
| **DeepSeek native API** | **48 MiB request, 32 MiB/image** |
| Kong-style gateways (default) | 128 MB |

Two conclusions: (a) properly-encoded images (150–600 KB, [Chapter 8](#8-vision-model-sizing-facts)) fit ~55 into 16 MiB, so the limit is livable with correct sizing; (b) the limit is a *configuration* ("the configured limit"), and it is 3× tighter than what the DeepSeek model behind it natively accepts — worth asking Lunaroute whether `max_bytes` is tunable per account.

---

## 2. Pi's Session Model

*Source: `dist/core/session-manager.js`, `dist/core/messages.js`, `docs/session-format.md`.*

### 2.1 Entries and messages

A session is an append-only JSONL file. Each line is a **`SessionEntry`**; the union of types (from `session-manager.d.ts:128`):

```typescript
export type SessionEntry =
  | SessionMessageEntry      // type: "message" — role messages
  | ThinkingLevelChangeEntry // type: "thinking_level_change"
  | ModelChangeEntry         // type: "model_change" {provider, modelId}
  | UsageEntry               // type: "usage" — non-conversation usage (cache warm etc.)
  | CompactionEntry          // type: "compaction" {summary, firstKeptEntryId, systemMessage, ...}
  | BranchSummaryEntry       // type: "branch_summary" {summary, fromId}
  | CustomEntry              // type: "custom" — extension state, NOT in LLM context
  | CustomMessageEntry       // type: "custom_message" — extension message, IN LLM context
  | ContextEditEntry         // type: "context_edit" {targetId, replacement}
  | LabelEntry               // type: "label" {targetId, label}
  | SessionInfoEntry;        // type: "session_info"
```

Messages embed `AgentMessage` objects with typed content blocks. The one that matters here:

```typescript
interface ImageContent {
  type: "image";
  data: string;      // base64-encoded image bytes
  mimeType: string;  // "image/png", "image/jpeg", ...
}
```

Images appear in `user`, `toolResult`, and `custom` message content arrays. In the forensic session, **60 of 60 images were `toolResult` blocks produced by the `read` tool**.

### 2.2 Context building: the projection pipeline

Three `SessionManager` methods build what the model sees, and the distinction matters:

```typescript
buildContextEntries(): SessionEntry[]   // branch walk + compaction applied
buildSessionProjection(): Projection     // + latest context_edit per target
buildSessionContext(): {...}             // + model/thinking replay → LLM message list
```

`buildContextEntries()` walks leaf→root and, if a `CompactionEntry` is on the path, uses the latest one: it includes the compaction entry, then non-system entries from `firstKeptEntryId` up to the compaction, then everything after. `buildSessionProjection()` then applies, for each target, **the latest `context_edit` on the active branch** (latest edit wins; edits are branch-relative — navigating before an edit reveals the original content again).

### 2.3 The ContextEditEntry: retroactive context surgery

This is the load-bearing mechanism for "retroactive image reduction" (from `session-manager.d.ts:119-127, 281`):

```typescript
export type ContextEditableContent =
  | UserMessage["content"] | AssistantMessage["content"]
  | ToolResultMessage["content"] | CustomMessage["content"];

appendContextEdit(targetId: string, replacement: ContextEditEntry["replacement"]): string;
// replacement: null → omit the target entry from model context entirely
// replacement: full message object → replaces ONLY the target message content
```

Properties (per `docs/session-format.md` and the entry docs):

- Append-only: raw history, UI, exports, and session accounting keep the original.
- Only *future model context* changes.
- String replacements for assistant/tool-result targets are normalized to a single text block (those roles require content arrays).
- A tool-result replacement may carry a content array including new `ImageContent` blocks — so **a downscaled image can replace the original without dropping the message**.

### 2.4 SessionManager surface used by extensions

Via `ctx.sessionManager` (read-only access, but `append*` methods are callable — the selective-compaction extension and pi's own `/edit` use them):

```typescript
getEntries(): SessionEntry[]            // all entries
getBranch(fromId?): SessionEntry[]      // current branch
buildContextEntries()                   // compaction-aware
getLeafId(): string
getSessionFile(): string | undefined    // for forensics / external scripts
appendContextEdit(targetId, replacement): string
appendCustomEntry(customType, data?): string
appendCompaction(summary, firstKeptEntryId, tokensBefore, details?, fromHook?, usage?): string
```

---

## 3. Token Estimation: Why the Meter Is Blind

*Source: `dist/core/compaction/compaction.js`.*

### 3.1 The chars/4 heuristic with a flat image rate

```javascript
const ESTIMATED_IMAGE_CHARS = 4800;  // ≈ 1200 tokens per image, ALWAYS

function estimateTextAndImageContentChars(content) {
  if (typeof content === "string") return content.length;
  let chars = 0;
  for (const block of content) {
    if (block.type === "text") chars += block.text.length;
    else if (block.type === "image") chars += ESTIMATED_IMAGE_CHARS;  // ← flat rate
  }
  return chars;
}

export function estimateTokens(message): number {  // Math.ceil(chars / 4) per role
  switch (message.role) {
    case "user": case "toolResult": case "custom":
      return Math.ceil(estimateTextAndImageContentChars(message.content) / 4);
    // system adds sections + toolsAdded JSON; assistant adds thinking/toolCall JSON;
    // bashExecution adds command+output; *Summary adds summary length
  }
}
```

A 4 MB PNG and a 30 KB thumbnail cost the same 1200 estimated tokens. Note the irony verified in [Chapter 8](#8-vision-model-sizing-facts): the *providers* actually bill ≤384 tokens/image, so pi **overestimates tokens while ignoring bytes entirely** — the binding constraint for byte-capped gateways.

### 3.2 Context metering and compaction triggering

```javascript
export function calculateContextTokens(usage): number {
  return usage.totalTokens || usage.input + usage.output + usage.cacheRead + usage.cacheWrite;
}

export function estimateContextTokens(messages) {
  // usage from last valid assistant message + estimateTokens() of trailing messages
  // skips stopReason "aborted"/"error" and all-zero usage
}

export function estimateProjectedContextTokens(projection, branchEntries) {
  // like above, but distrusts usage captured before a later context_edit or compaction
}

export const DEFAULT_COMPACTION_SETTINGS = {
  enabled: true, reserveTokens: 16384, keepRecentTokens: 20000,
};

export function shouldCompact(contextTokens, contextWindow, settings) {
  return settings.enabled && contextTokens > contextWindow - settings.reserveTokens;
}
```

Auto-compaction fires from `AgentSession._compactBeforeNextTurn()`:

```javascript
if (shouldCompact(estimateProjectedContextTokens(projection, branch).tokens,
                  model.contextWindow, settings)) {
  await this._runAutoCompaction("threshold", /* notify */ false);
}
```

**The blindness, quantified.** In the forensic session: 16 images in context ≈ 19k estimated tokens of a 524k window → `shouldCompact` was ~50k tokens away from even *starting* to think about compaction, while the request body was 17.7 MB. The compaction meter (`extensions/compaction-meter/`) is a faithful renderer of these numbers — it cannot show bytes because the core does not model them.

---

## 4. The Image Ingestion Pipeline

*Source: `dist/utils/image-process.js`, `dist/utils/image-resize-core.js`, `dist/utils/image-resize.js`, `dist/utils/tool-result-images.js`, `dist/core/agent-session.js`.*

### 4.1 The resize primitive

```typescript
export interface ImageResizeOptions {
  maxWidth?: number;    // default 2000
  maxHeight?: number;   // default 2000
  maxBytes?: number;    // default 4.5 * 1024 * 1024 (base64 size!)
  jpegQuality?: number; // default 80
}

export interface ResizedImage {
  data: string; mimeType: string;
  originalWidth: number; originalHeight: number;
  width: number; height: number; wasResized: boolean;
}

// dist/utils/image-resize-core.js
const DEFAULT_MAX_BYTES = 4.5 * 1024 * 1024;
const DEFAULT_OPTIONS = { maxWidth: 2000, maxHeight: 2000,
                          maxBytes: DEFAULT_MAX_BYTES, jpegQuality: 80 };

export async function resizeImageInProcess(
  inputBytes: Uint8Array, mimeType: string, options: ImageResizeOptions
): Promise<ResizedImage | null>;
```

Resize strategy (documented in the source header, verified in the body):

1. If already within `maxWidth`×`maxHeight` and `base64 < maxBytes` → **returned unchanged** (no re-encode — a PNG stays a PNG).
2. Else: scale down to fit `maxWidth/maxHeight`, **try both PNG and JPEG, keep the smaller**, with JPEG quality steps `Array.from(new Set([jpegQuality, 85, 70, 55, 40]))`, then progressively shrink dimensions toward 1×1 until under `maxBytes`. Returns `null` only if even 1×1 exceeds `maxBytes`.

`resizeImage` is **publicly exported** by the host package (`dist/index.d.ts:34`), with a worker-process fallback for compiled-binary layouts:

```typescript
import { resizeImage, type ResizedImage } from "@earendil-works/pi-coding-agent";
```

This is the extension's resize engine — no sharp/sips dependency needed.

### 4.2 Where profiles are applied

```typescript
// dist/utils/image-process.ts
export interface ProcessImageOptions {
  autoResizeImages?: boolean;  // default true; from settings images.autoResize
  resizeOptions?: ImageResizeOptions; // ← model profile, else defaults above
}
export async function processImage(bytes, mimeType, options): Promise<ProcessImageResult>;

// dist/utils/tool-result-images.ts
export interface NormalizeToolResultImagesOptions {
  autoResizeImages?: boolean;
  resizeOptions?: ModelImageResizeOptions;
}
export async function normalizeToolResultImages(content, options): Promise<ToolResultContent[]>;
```

The source comment states the design intent precisely:

> The `read` tool and `@file` CLI attachments run their images through `processImage`, but tools that produce images themselves (extensions, MCP bridges, screenshot tools) hand back arbitrary base64 payloads that go straight into session history and every subsequent provider request. **Oversized images make the provider reject the whole conversation, not just the offending turn**, so normalize them once as they enter history.

### 4.3 The two wiring points in `AgentSession`

```javascript
// dist/core/agent-session.js — afterToolCall (≈line 281)
this.agent.afterToolCall = async ({ toolCall, args, result, isError }) => {
  const hookResult = runner.hasHandlers("tool_result") ? await runner.emitToolResult({...}) : undefined;
  const content = hookResult?.content ?? result.content ?? [];
  // Runs after the extension hook so images injected or replaced by extensions are normalized too.
  const resizeOptions = this.model?.inputLimits?.images?.resize;
  const normalizedContent = await normalizeToolResultImages(content, {
    autoResizeImages: this.settingsManager.getImageAutoResize(),
    ...(resizeOptions ? { resizeOptions } : {}),
  });
  ...
};

// prompt-attachment path (≈line 1187) uses the same resizeOptions for processImage.
```

Two facts follow directly:

1. **Ordering guarantee**: an extension's `tool_result` hook runs *before* pi's normalizer. An extension that returns already-resized images gets them passed through untouched (they fit the profile), so the extension can own the encoding decision.
2. **The profile is read from the *active model object at ingestion time*** (`this.model` is dereferenced per call). This is what makes mid-session profile changes effective for all subsequently ingested images ([Chapter 7.3](#73-session-scoped-and-mid-session-quality-toggles)).

### 4.4 Settings

Global, blunt, from `docs/settings.md`:

| Setting | Default | Effect |
|---|---|---|
| `images.autoResize` | `true` | Master switch for ingestion-time resize to 2000×2000/profile |
| `images.blockImages` | `false` | Block all images from being sent to the LLM |
| `terminal.showImages` | `true` | TUI inline image display |

There are **no session-scoped or per-model knobs in settings.json**; per-model profiles live in `models.json` ([Chapter 5](#5-model-input-limits-configuration-and-dead-config)).

---

## 5. Model Input Limits: Configuration and Dead Config

*Source: `@earendil-works/pi-ai/dist/types.d.ts:785-804`, `dist/core/model-config.js:166,180`, `dist/core/provider-composer.js:36-48`.*

### 5.1 The schema (pi-ai)

```typescript
export interface ModelImageResizeOptions {          // types.d.ts:785
  maxWidth?: number; maxHeight?: number;
  maxBytes?: number;      // Maximum base64-encoded payload size in bytes
  jpegQuality?: number;
}
export interface ModelImageInputLimits {           // types.d.ts:792
  resize?: ModelImageResizeOptions;  // Cache-safe profile applied before an image
                                     // enters conversation history
  maxPerMessage?: number;            // Maximum images per provider message
  maxPerRequest?: number;            // Maximum images per provider request
}
export interface ModelInputLimits {                // types.d.ts:800
  maxRequestBytes?: number;          // "Maximum serialized provider request size in bytes"
  images?: ModelImageInputLimits;
}
```

### 5.2 Where it is configurable

`~/.pi/agent/models.json`, at provider level (`providers.<id>.models[]`) and per model (`providers.<id>.modelOverrides.<modelId>`), both validated with `Type.Optional(ModelInputLimitsSchema)` (`model-config.js:166,180`). Overrides deep-merge with the base model profile — `provider-composer.js`:

```javascript
function mergeInputLimits(base, override) {
  if (!override) return base;
  return {
    ...base, ...override,
    images: override.images
      ? { ...base?.images, ...override.images,
          resize: override.images.resize
            ? { ...base?.images?.resize, ...override.images.resize }
            : base?.images?.resize }
      : base?.images,
  };
}
function applyModelOverride(model, override) {
  return { ...model, /* ... */ inputLimits: mergeInputLimits(model.inputLimits, override.inputLimits), /* ... */ };
}
```

So a partial override (`{ "images": { "resize": { "maxBytes": 350000 } } }`) inherits the unspecified fields from the model's base profile (or the resizer defaults).

### 5.3 Dead config, verified

- **`maxRequestBytes`**: schema-validated, **never read by any runtime code** (grep across `dist/core`, `dist/modes`, and the `pi-ai` package finds only schema definitions). Declaring it changes nothing today. It is, however, the natural budget source for the image-budget extension, and forward-compatible if pi grows enforcement.
- **`images.maxPerMessage` / `images.maxPerRequest`**: same status — declared, validated, unread.
- **`images.resize`**: fully live, wired at the two ingestion points ([4.3](#43-the-two-wiring-points-in-agentsession)).

### 5.4 Current user config state (2026-09-23)

`~/.pi/agent/models-store.json` defines 11 lunaroute models (`deepseek-4.1-flash`, `glm-5.2-vision`, `glm-5.3`, `glm-5.3-vision`, `-background`/`-flex` variants, ...), all `input: ["text","image"]`, context windows 524288–1048576, `api: "openai-completions"`, **and none declare `inputLimits`**. Hence all images entered history at the loose resizer defaults (2000×2000 / 4.5 MB) — the forensic session's 4 MB PNGs were "legal" images.

### 5.5 The recommended override block

```json
{
  "providers": {
    "lunaroute": {
      "modelOverrides": {
        "deepseek-4.1-flash": {
          "inputLimits": {
            "maxRequestBytes": 16777216,
            "images": { "resize": { "maxWidth": 1280, "maxHeight": 1280, "maxBytes": 350000, "jpegQuality": 80 } }
          }
        },
        "glm-5.2-vision": {
          "inputLimits": {
            "maxRequestBytes": 16777216,
            "images": { "resize": { "maxWidth": 2560, "maxHeight": 1600, "maxBytes": 500000, "jpegQuality": 80 } }
          }
        },
        "glm-5.3-vision": {
          "inputLimits": {
            "maxRequestBytes": 16777216,
            "images": { "resize": { "maxWidth": 2560, "maxHeight": 1600, "maxBytes": 500000, "jpegQuality": 80 } }
          }
        }
      }
    }
  }
}
```

The `resize` blocks work today; `maxRequestBytes` is inert but serves as the extension's budget source. (Rationale for the numbers: [Chapter 8](#8-vision-model-sizing-facts).)

---

## 6. Overflow Detection and Recovery

*Source: `@earendil-works/pi-ai/dist/utils/overflow.js`, `dist/core/agent-session.js:2067,2625-2640`.*

### 6.1 The pattern list

pi detects context overflow by regex-matching the assistant error message. `OVERFLOW_PATTERNS` contains 23 patterns for known providers; the byte-size cases:

```javascript
/request_too_large/i,          // Anthropic request byte-size overflow (HTTP 413)
/^4(?:00|13)\s*(?:status code)?\s*\(no body\)/i,  // Cerebras bodyless 413 (special-cased)
```

plus token-overflow patterns for OpenAI (`/exceeds the context window/i`), Anthropic (`/prompt (?:is )?too long/i`), Google, xAI, Groq, OpenRouter, Together, llama.cpp, LM Studio, MiniMax, Kimi, DS4, Cerebras, Mistral, z.ai, DashScope/Qwen, Ollama, and generic fallbacks (`/context[_ ]length[_ ]exceeded/i`, `/too many tokens/i`, `/token limit exceeded/i`). `NON_OVERFLOW_PATTERNS` excludes throttling-style false positives (`/rate limit/i`, `/too many requests/i`, Bedrock prefixes).

```typescript
export function isContextOverflow(message: AssistantMessage, contextWindow?: number): boolean;
// Case 1: stopReason "error" + errorMessage matches a pattern (and no non-overflow pattern)
// Case 2: silent overflow — stopReason "stop" but usage.input + cacheRead > contextWindow (z.ai)
// Case 3: length-stop overflow — stopReason "length", output === 0, input fills ≥99% of window (Xiaomi MiMo)

export function isRecoverableLength(message, desiredMaxOutput): boolean;
export function getOverflowPatterns(): RegExp[];   // for testing
```

### 6.2 What happens on a match

`dist/core/agent-session.js:2067` — an overflow error triggers **one bounded compact-and-retry attempt**:

```javascript
const explicitOverflow = assistantMessage.stopReason === "error"
  && isContextOverflow(assistantMessage);
const contextOverflow = sameModel && explicitOverflow && assistantRetainedForExplicitRecovery;
if (contextOverflow || recoverableLength) {
  // retried error → compact then retry once; clean stop → compact, no retry
  await this._runAutoCompaction("overflow", false);
}
// _isRetryableError: overflow is NOT retryable — compaction handles it
```

### 6.3 The gap: Lunaroute's error is invisible

Verified live against the installed matcher:

```javascript
const err = new Error('413: {"code":"PAYLOAD_TOO_LARGE","declared_bytes":17706402,"max_bytes":16777216}');
isContextOverflow(err)        // → false
isRecoverableLength(err)      // → false
```

`PAYLOAD_TOO_LARGE` matches none of the 23 patterns, so the 413 surfaced as a plain hard error: no compaction attempt, no retry — exactly what the forensic session shows (repeated 413 error entries followed by 7 manual model changes). Consequences:

- **Upstream ask**: Lunaroute returning an Anthropic-style `request_too_large` code would trip pi's existing recovery (compaction alone would help, since a compaction summary replaces old messages including their images).
- **Extension responsibility**: hook `pi.on("after_provider_response", ({ status }) => ...)` for `status === 413` and drive the image-slim flow — pi core gives the event, the extension supplies the byte-aware recovery that `OVERFLOW_PATTERNS` doesn't.

---

## 7. The Extension API Surface

*Source: `docs/extensions.md`, `dist/core/extensions/runner.js`, verified against dist code.*

### 7.1 The events that matter for image budgeting

```typescript
pi.on("tool_result", async (event, ctx) => {
  // event: { toolName, toolCallId, input, content, details, isError, usage }
  // event.content: (TextContent | ImageContent)[] — images as base64 blocks
  return { content };   // replacement content; pi normalizes AFTER this hook
});

pi.on("input", async (event, ctx) => {
  // user prompt text/images; return { transform ... } to modify before send
});

pi.on("context", async (event, ctx) => {           // per-request, non-destructive
  return { messages };                              // prompt/tools re-projected ahead
});
pi.on("context_with_system", async (event, ctx) => {/* owns full request list */});

pi.on("before_provider_request", (event, ctx) => {
  // event.payload — provider-specific serialized payload, right before send
  console.log(JSON.stringify(event.payload).length);  // ← exact request bytes
  return { ...event.payload };                      // optional replacement
});

pi.on("before_provider_headers", (event, ctx) => { event.headers["x"] = "y"; });
pi.on("after_provider_response", (event, ctx) => {
  // event.status (HTTP), event.headers — THE 413 DETECTION POINT
});

pi.on("session_before_compact", ...); pi.on("session_compact", ...);
pi.on("model_select", ...); pi.on("message_end", ...); pi.on("turn_end", ...);
```

### 7.2 ExtensionContext essentials

```typescript
ctx.sessionManager                 // SessionManager (Chapter 2.4)
ctx.model: Model | undefined      // ACTIVE model object (incl. inputLimits)
ctx.modelRegistry                 // getProvider, getApiKeyAndHeaders, streamSimple, find, ...
ctx.getContextUsage(): { tokens, ... } | undefined   // token-based only (Chapter 3)
ctx.compact({ customInstructions, onComplete, onError }): void
ctx.getSystemPrompt(): string
ctx.ui                            // notify, confirm, select, editor, custom, setWidget, ...
ctx.mode                          // "tui" | "rpc" | "json" | "print"
```

`ExtensionAPI` methods relevant here: `registerTool`, `registerCommand(name, {description, handler})`, `registerShortcut`, `registerFlag`, `registerMessageRenderer(customType, renderer)`, `registerEntryRenderer`, `sendMessage`, `sendUserMessage`, `appendEntry(customType, data)` (→ `CustomEntry`, not in LLM context), `setLabel`, `setModel(model)`, `registerProvider(name, config)`, `exec`.

**State reconstruction pattern** (from `docs/extensions.md` State Management): extensions with state replay it on `session_start` by walking `ctx.sessionManager.getBranch()` for their tool `details` or `CustomEntry` payloads — this is how the image-budget session profile survives resume and branches.

### 7.3 Session-scoped and mid-session quality toggles

Three mechanisms, in increasing durability:

**(a) `pi.setModel` with a patched model copy — works today.** Verified at `agent-session.js:1645`:

```javascript
async setModel(model, options = {}) {
  if (!(await this._modelRuntime.checkAuth(model.provider)))
    throw new Error(`No API key for ${model.provider}/${model.id}`);
  this.agent.state.model = model;               // ← ANY Model object; no registry validation
  this.sessionManager.appendModelChange(model.provider, model.id);
  ...
}
```

Because ingestion re-reads `this.model?.inputLimits?.images?.resize` per image ([4.3](#43-the-two-wiring-points-in-agentsession)), this immediately changes encoding for all *future* images:

```typescript
await pi.setModel({
  ...ctx.model,
  inputLimits: { ...ctx.model.inputLimits,
    images: { ...ctx.model.inputLimits?.images,
      resize: { ...ctx.model.inputLimits?.images?.resize,
                maxWidth: 4000, maxHeight: 4000, maxBytes: 5_000_000 } } },
});
```

Caveats: appends a `model_change` entry per toggle; **no prompt-cache break** (provider/id/payload shape unchanged); **lost on session resume** — pi persists `provider`+`modelId` and re-resolves from the registry. An extension must re-apply it on `session_start`.

**(b) Registered clone provider — resume-stable.** `pi.registerProvider("lunaroute-hq", { baseUrl, apiKey, api, models: [...with hq inputLimits] })`; the user switches via `/model`. Re-registered at every startup, so it survives resume. Clunky as a toggle.

**(c) Extension-owned session profile — recommended.** The extension keeps `{ quality: "lossy80" | "lossy95" | "lossless", maxWidth, maxBytes }` as session state, re-encodes in its own `tool_result`/`input` hooks *before* returning content (so pi's normalizer passes the results through), exposes `/image-quality`, and persists the choice via `pi.appendEntry("image-budget-config", {...})` + `session_start` replay. Changes apply only to subsequently ingested images; historical images need the [Chapter 10](#10-the-image-budget-extension-design) slim pass.

Note on "100% quality": pi's resizer semantics don't include "q100 JPEG" — untouched images keep their original encoding, and re-encodes pick the *smaller* of PNG/JPEG. A useful profile model distinguishes `lossless` (keep PNG, no dimension cap, high maxBytes) from `lossy` (dimension cap + JPEG quality), rather than exposing a raw `jpegQuality` number alone.

---

## 8. Vision Model Sizing Facts

*Web-sourced (2026-09-23, Kagi): DeepSeek API docs + launch coverage; z.ai docs + GLM-5.3-Flash blog; Latent.Space; baseten GLM-5.2-Vision model cards.*

### 8.1 DeepSeek-4.1-Flash (a.k.a. `deepseek-flash`)

- **Server-side resize toward ~800×800 pixel count** (~640k px); every image billed at **≤ 384 tokens** — "a 2000×2000 image and a 5000×5000 image consume the same number of tokens after resizing" (DeepSeek Vision guide).
- Native limits: **request body 48 MiB; single image ≤ 32 MiB base64**; formats JPEG/PNG/GIF/WebP.
- Implication: anything beyond ~1024–1280px long edge is pure payload waste.

### 8.2 GLM vision family (z.ai / Lunaroute)

- Upstream **GLM-5.3 is text-only**; image input is via **GLM-5.3-Flash/FlashX** (native multimodal, 1M context) and **GLM-5.2-Vision** (MoonViT dynamic-resolution vision tower + 49.5M-param projector on a frozen backbone — baseten NVFP4/FP8 builds). Lunaroute's store declaring `glm-5.3: input=["text","image"]` is gateway-side routing metadata, not upstream truth.
- z.ai resize policy: **"shorter side at least 1.5K pixels, consistent with other frontier models"** (GLM-5.3-Flash blog).
- Reported GLM-5.3 image billing: **~117–384 tokens per image** (Latent.Space).

### 8.3 Sizing rules

| Knob | deepseek-4.1-flash | GLM vision |
|---|---|---|
| Dimensions | long edge ~1024–1280 px | shorter side ~1500 px (cap long edge ~2400–2560) |
| Format | JPEG q75–85 | JPEG q75–85 |
| Target bytes | ~150–350 KB | ~300–600 KB |

1. **PNG→JPEG is the biggest single win for UI screenshots** (4 MB PNG → 150–400 KB; ≥90% reduction, no perceptible loss at these dimensions). PNG only for tiny pixel-precise graphics.
2. **Size to the model's working resolution** — resolution beyond the server cap buys nothing and costs the 16 MiB budget.
3. **Text-heavy/wide screenshots: crop, don't shrink** — the detail ceiling is enforced server-side; crop to the region of interest.
4. Never upscale; don't exceed ~2× the cap.

Budget arithmetic: 16 MiB ≈ 55 images at 300 KB vs ≈ 4 images at 4 MB.

---

## 9. The Byte-Accounting Model, Validated

Forensic subject (78 MB session file):

```
/Users/manuel.odendahl/.pi/agent/sessions/--Users-manuel.odendahl-code-tulip-worktrees-
2026-09-20-2026-09-14--factory-videos-CLASSIFIER-DSL-001--classifier-core--/
2026-09-23T18-49-11-315Z_01a0cf99-b192-75b4-a590-eb82158eea13.jsonl
```

Session census: 785 entries (650 messages, 79 `context_edit`, 26 `custom`, 20 `thinking_level_change`, 7 `model_change`, 1 `compaction`). **60 images, 79 MB of base64, all `toolResult` from `read`**, all PNG or JPEG. Repeated `fetch failed` errors, one older 413 shape (`"request body too large"`), and the target: `PAYLOAD_TOO_LARGE` at assistant entry `70e45446`.

Reconstructing the active context at the 413 (branch walk + compaction + context_edits, mirroring `buildSessionProjection()`):

| Measure | Value |
|---|---|
| Images in context | 16 |
| Sum of base64 image data | 17.32 MB |
| Sum of text | 0.21 MB |
| **Estimated body** | **17.53 MB** |
| Lunaroute `declared_bytes` | 17,706,402 (17.71 MB) |

**Δ ≈ 1%** — the accounting model is:

```
requestBytes ≈ Σ base64Len(image.data)        // ×(4/3) inflation already in base64
             + Σ textLen(text blocks)          // + JSON-escaped tool JSON etc.
             + ~1–2% framing overhead          // role keys, tool declarations, headers' body share
```

At the *current* leaf the same session projects to **30 surviving images = 44.66 MB** — 2.7× the cap — i.e. the problem persists after the fact and must be solved retroactively, not just prevented.

Pseudocode of the meter (stage 1 of the extension):

```typescript
function contextImageReport(projection: Projection, budgetBytes: number) {
  let bytes = 0, textBytes = 0;
  const images: ImageRow[] = [];
  for (const { message, sourceEntry } of projection) {   // model-visible messages
    for (const block of content(message)) {
      if (block.type === "image") {
        bytes += block.data.length;
        images.push({
          entryId: sourceEntry.id,
          role: message.role, toolName: message.toolName,
          mime: block.mimeType,
          b64Bytes: block.data.length,
          width, height,               // from PNG IHDR / JPEG SOF header parse
        });
      } else if (block.type === "text") textBytes += block.text.length;
    }
  }
  return {
    images: images.sort(byBytesDesc),
    imageBytes: bytes, textBytes,
    estimatedBody: bytes + textBytes + overhead(bytes),   // overhead ≈ 1–2%
    budgetBytes, pct: estimatedBody / budgetBytes,
  };
}
```

Dimension sniffing needs no image library: PNG stores width/height at decoded-byte offsets 16–24 (IHDR); JPEG requires walking markers to an SOF frame. Both are ~20-line parsers.

---

## 10. The Image-Budget Extension Design

Target layout (per repository conventions in `AGENTS.md`): `extensions/image-budget/`, registered via `registerPiExtension()` from `extensions/_shared/registry.ts`, UI pieces from `extensions/_shared/ui/`, docs paths relative. Read `docs/pi-shared-extension-framework-guide.md` and `docs/pi-tui-ui-authoring-guide.md` before writing UI.

### 10.1 Settings

```jsonc
{
  "imageBudget": {
    "budgetBytes": "auto",        // model.inputLimits.maxRequestBytes → provider default (lunaroute 16 MiB) → off
    "providerDefaults": { "lunaroute": 16777216 },
    "warnThreshold": 0.8,         // % of budget
    "mode": "ask",                // "ask" | "auto" | "off" — stage-3 behavior
    "downscale": { "maxWidth": 1280, "maxHeight": 1280, "maxBytes": 350000, "jpegQuality": 80 },
    "sessionProfile": "lossy80"   // "lossy80" | "lossy95" | "lossless" — Chapter 7.3(c)
  }
}
```

### 10.2 Stage 1 — Visibility

- `contextImageReport()` (Chapter 9) recomputed on `message_end`, `session_start`, compaction, and `context_edit` events.
- **Status widget** (pattern: `extensions/compaction-meter/`): `imgs 14.2/16.0MB ██▓ 89%`, color-coded at the warn threshold. `registerPiExtension` metadata exposes it to the launcher/dashboard.
- **`/images` command** → dashboard overlay (pattern: `_shared/ui` overlay + `ctx.ui.custom`): rows `entry 1efcbe26 · read · 2400×1080 · png · 4068KB · 23% ▓▓▓`, sorted by bytes, with per-row actions (stage 2).

### 10.3 Stage 2 — Retroactive reduction ("slim")

```typescript
pi.registerCommand("image-slim", { handler: slimFlow });

async function slimFlow(ctx) {
  const report = contextImageReport(ctx.sessionManager.buildSessionProjection(), budget(ctx));
  const picks = await pickImages(ctx, report);        // keep-last-N / older-than-T / manual
  for (const img of picks) {
    const replacement = await downscaleOrPlaceholder(img);   // resizeImage() or text note
    ctx.sessionManager.appendContextEdit(img.entryId, {
      ...originalMessage(img.entryId),
      content: replacement,                                  // image or text blocks
    });
  }
  await maybeDescribe(ctx, picks);   // optional: LLM descriptions via ctx.modelRegistry.streamSimple
  ctx.sessionManager.appendCustomEntry("image-budget-slim", { edited: ids, bytesBefore, bytesAfter });
}
```

Semantics inherited from `ContextEditEntry`: append-only, raw history intact, branch-relative, latest-edit-wins. The confirm dialog must state the cache consequence: a `context_edit` invalidates the provider prompt cache from the first edited entry forward (irrelevant when the request is already dead) — and `estimateProjectedContextTokens` explicitly distrusts usage captured before a later edit, so the token meter stays consistent.

### 10.4 Stage 3 — Upfront gating and 413 recovery

```typescript
pi.on("tool_result", async (event, ctx) => {
  if (!hasImages(event.content)) return;
  const report = contextImageReport(currentProjection(ctx), budget(ctx));
  const projected = report.estimatedBody + imageBytes(event.content) - replacedBytes;
  if (projected > warn && settings.mode === "ask") {
    const choice = await ctx.ui.confirm("…", "Downscale / Keep / Drop");
    // return modified event.content → pi's normalizeToolResultImages runs after (4.3)
  }
});

pi.on("before_provider_request", (event, ctx) => {
  // exact byte measurement point: JSON.stringify(event.payload).length
  // over budget + auto mode → rewrite payload's image blocks for this request
});

pi.on("after_provider_response", (event, ctx) => {
  if (event.status === 413) { notify(...); launchSlimFlow(ctx); }   // Chapter 6.3 gap
});
```

The 413 path is the byte-aware recovery that pi's `OVERFLOW_PATTERNS` cannot provide (a compaction alone would also work — a `CompactionEntry` replaces old messages including their images — and `ctx.compact()` is available to the extension).

### 10.5 What must NOT be reimplemented

- Ingestion-time resize: pi already does it once `inputLimits.images.resize` is configured ([5.5](#55-the-recommended-override-block)) — the extension's re-encoder exists for *session-scoped overrides and gating*, not to duplicate the default pipeline.
- Compaction: `ctx.compact()` + `session_before_compact` hooks exist; image-budget only adds the byte dimension.
- Retroactive editing: `appendContextEdit` is the only supported mechanism; never rewrite the JSONL.

---

## 11. Open Questions

1. Is Lunaroute's `max_bytes` configurable per account/key? (Error says "the configured limit"; DeepSeek native accepts 48 MiB.)
2. Does the `fetch failed` storm in the forensic session share a root cause with the 413 (e.g. gateway instability), or is it unrelated?
3. Upstream pi feature requests worth filing: (a) runtime enforcement of `maxRequestBytes` with auto image-slim before send; (b) byte-aware `estimateTokens`; (c) `PAYLOAD_TOO_LARGE` in `OVERFLOW_PATTERNS` or a pluggable overflow-pattern hook.

## Related

- Source ticket: `ttmp/2026/09/23/PI-EXT-IMAGE-BUDGET--image-byte-budget-extension-view-slim-and-gate-context-images/` in the pi-extensions repo (this report is a copy of `reference/01-how-pi-handles-images-and-context-bytes-a-technical-investigation.md`)
- Ticket diary: the same ticket's `reference/03-investigation-diary.md`
- Widget pattern: `extensions/compaction-meter/meter.ts` (pi-extensions repo)
- Context-edit/compaction entry patterns: `extensions/selective-compaction/session.ts` (pi-extensions repo)
- Extension framework guide: `docs/pi-shared-extension-framework-guide.md` (pi-extensions repo)
- TUI authoring guide: `docs/pi-tui-ui-authoring-guide.md` (pi-extensions repo)
