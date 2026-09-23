---
title: "Pi Image Byte Budget — Diagnosing and Fixing 413 PAYLOAD_TOO_LARGE in an Agent Context"
aliases: [image-budget extension, pi image byte budget, PAYLOAD_TOO_LARGE deep dive]
tags: [project-report, pi, coding-agent, images, context-window, lunaroute, extensions]
status: active
type: project-report
created: 2026-09-23
updated: 2026-09-23
audience: engineer building on or extending the pi coding agent
repo: /Users/manuel.odendahl/code/wesen/2026-04-21--pi-extensions
source_ticket: PI-EXT-IMAGE-BUDGET
---

# Pi Image Byte Budget — Diagnosing and Fixing 413 PAYLOAD_TOO_LARGE in an Agent Context

## 0. What this document is

This is the deep-dive writeup of the **image-budget** extension for the pi
coding agent: why an image-heavy session died with
`413 PAYLOAD_TOO_LARGE` while its token context was nearly empty, which parts
of pi's architecture made that failure invisible, and how the extension
closes the gap. It doubles as a technical analysis of pi's context pipeline,
because you cannot fix a metering blind spot without understanding what is
being metered, where, and when.

Everything here was verified against the installed pi distribution
(`/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent`, version
0.87.0), the user configuration at `~/.pi/agent/`, and a 78 MB forensic
session file that contained the actual 413. Where a claim comes from public
model documentation rather than the local installation, the text says so.

| Artifact | Location |
|---|---|
| Extension source | `~/code/wesen/2026-04-21--pi-extensions/extensions/image-budget/` |
| Ticket (report, intern guide, diary, tasks) | `ttmp/2026/09/23/PI-EXT-IMAGE-BUDGET--image-byte-budget-extension-view-slim-and-gate-context-images/` |
| Forensic session (live, handle with care) | `~/.pi/agent/sessions/--Users-manuel.odendahl-code-tulip-worktrees-.../2026-09-23T18-49-11-315Z_01a0cf99-....jsonl` |

## 1. The failure

The session that motivated this work ran on the Lunaroute gateway
(`https://gw.lunaroute.com/v1`) and died repeatedly with:

```json
{"code":"PAYLOAD_TOO_LARGE",
 "declared_bytes":17706402,
 "max_bytes":16777216,
 "message":"Request body exceeds the configured limit"}
```

Two numbers in that error deserve attention before anything else.
`max_bytes` is 16,777,216 — exactly 16 MiB, a round power of two, which
identifies it as a configured gateway limit rather than a model property.
`declared_bytes` is the Content-Length of the serialized JSON request body.
The limit applies to the entire HTTP request, not to any single image.

To understand why pi never warned about this, you need one structural fact
about agent loops: **pi resends the entire conversation history on every
request.** A coding agent is not a chat app with server-side history; each
turn ships the full transcript — every message, every tool result, every
image as base64 — to the provider again. Two independent ceilings therefore
sit over the same payload:

1. **The model's context window, measured in tokens.** Pi models this
   (`Model.contextWindow`) and meters it continuously.
2. **The request body size, measured in bytes.** Determined by the HTTP
   path between client and model. Pi nominally models it
   (`ModelInputLimits.maxRequestBytes`) but, as section 4 shows, never
   enforces it.

The failing session sat at roughly 4% of ceiling 1 while exceeding ceiling
2 by 5.5%. The failure mode is not exotic; it is what happens whenever a
system meters one dimension of a two-dimensional constraint. Images are
precisely the payload class where the two dimensions diverge: a 4 MB PNG and
a 30 KB thumbnail differ by two orders of magnitude in bytes while a
token-counting system may treat them as identical.

### 1.1 How much is 16 MiB, really

For a single-shot image API, 16 MiB is a normal limit. Per-image caps
elsewhere: Anthropic 5 MB, OpenAI roughly 20 MB, Google 20 MB inline,
DeepSeek's native API 32 MB per image and 48 MiB per request. For an agent
loop, the comparison that matters is different, because the budget is
consumed by *cumulative* history:

| Gateway / provider | Request body limit |
|---|---|
| Lunaroute | 16 MiB (16,777,216 B, configured) |
| Google Gemini inline | 20 MB total request |
| Anthropic | 5 MB/image, ≤100 images/request |
| OpenAI | ~20 MB/image, ~50 MB requests |
| DeepSeek native | 48 MiB request, 32 MiB/image |
| Kong-style gateways (default) | 128 MB |

Two conclusions follow. First, with correctly encoded images (150–600 KB
each, section 7), 16 MiB holds roughly 55 images — livable. The failing
session carried 4 MB PNGs, which fit only four to a budget. Second, the
limit is 3× tighter than what the DeepSeek model behind it accepts
natively, and the error text itself says "the configured limit", so it is
worth asking the gateway operator whether `max_bytes` is tunable per
account. Both paths were pursued: resize profiles to make images small, and
the extension to make bytes visible.

## 2. How pi stores conversations

Pi persists a session as one append-only JSONL file. Each line is a
`SessionEntry`; the entries that matter here are:

- `SessionMessageEntry` (`type: "message"`) — wraps an `AgentMessage`.
  Images live inside content arrays as `ImageContent` blocks:

```typescript
interface ImageContent {
  type: "image";
  data: string;      // base64-encoded image bytes — this is the byte cost
  mimeType: string;  // "image/png", "image/jpeg", ...
}
```

- `CompactionEntry` (`type: "compaction"`) —
  `{ summary, firstKeptEntryId, systemMessage, tokensBefore, ... }`. When
  one is on the active branch, everything before `firstKeptEntryId`
  collapses into `summary`.
- `ContextEditEntry` (`type: "context_edit"`) — `{ targetId, replacement }`.
  This entry is the load-bearing mechanism for retroactive changes and gets
  its own section (8).
- `ModelChangeEntry`, `CustomEntry` (extension state, never sent to the
  model), `CustomMessageEntry` (extension-injected, sent), `LabelEntry`,
  `UsageEntry`.

The model-visible view is built in three steps, and the distinction between
them is what makes correct metering possible:

```typescript
buildContextEntries(): SessionEntry[]
//  walks leaf → root; if a CompactionEntry is on the path, uses the latest:
//  the compaction entry, then kept entries from firstKeptEntryId onward.

buildSessionProjection(): SessionProjection
//  applies, for each target, the LATEST context_edit on the active branch.
//  returns { entries, messages } where each message is paired with its
//  source entry — the attribution the meter needs.

buildSessionContext()
//  resolves model and thinking level from the path → final LLM message list.
```

`buildSessionProjection()` is the function to internalize. It is the exact
boundary between "what is stored" and "what the model sees". Any meter that
wants to reflect the provider's view must scan the projection, not the raw
entries — otherwise it counts images that a compaction already summarized
away or an edit already replaced. In the forensic session this distinction
is measurable: the raw file holds 60 images and 79 MB of base64; the
projection at the 413 held 16 images and 17.32 MB.

## 3. Why the token meter could not see it

Pi decides when to compact from token counts, produced by an estimator in
`dist/core/compaction/compaction.js`:

```javascript
const ESTIMATED_IMAGE_CHARS = 4800;              // ≈ 1200 tokens, ALWAYS

function estimateTextAndImageContentChars(content) {
  if (typeof content === "string") return content.length;
  let chars = 0;
  for (const block of content) {
    if (block.type === "text") chars += block.text.length;
    else if (block.type === "image") chars += ESTIMATED_IMAGE_CHARS;
  }
  return chars;
}

export function estimateTokens(message) { /* Math.ceil(chars / 4) per role */ }
```

Every image costs 1200 estimated tokens regardless of whether it is a
20 KB thumbnail or a 4 MB screenshot. Compaction triggers when:

```javascript
export const DEFAULT_COMPACTION_SETTINGS = {
  enabled: true, reserveTokens: 16384, keepRecentTokens: 20000,
};
export function shouldCompact(contextTokens, contextWindow, settings) {
  return settings.enabled
    && contextTokens > contextWindow - settings.reserveTokens;
}
```

Run the numbers for the failing session: 16 images ≈ 19,200 estimated
tokens against a 524,288-token window. The estimator was 489,000 tokens
away from the compaction threshold while the request body was 5.5% over
the byte limit. The compaction meter in the status bar — a faithful
renderer of these numbers — reported a nearly empty context. It was not
broken; it was answering a different question than the one the gateway
asked.

There is a further wrinkle worth stating precisely: the flat 1200-token
estimate does not undercount what the *provider* charges. DeepSeek-4.1
resizes every image toward an ~800×800 pixel count server-side and bills
at most 384 tokens per image; GLM vision models keep roughly the shorter
side at 1.5k pixels and bill ~117–384 image tokens. So pi
*overestimates* image tokens while ignoring image bytes entirely. The
binding constraint for a byte-capped gateway is transport size, and no
component of pi models it.

## 4. Three mechanisms that almost caught it

It would be wrong to say pi has no defenses here. It has three, and
understanding why each one misses is the core of this analysis.

**Per-image resize at ingestion.** Every image entering history passes
through `processImage` (prompt attachments, the `read` tool) or
`normalizeToolResultImages` (tool results), both wired in
`dist/core/agent-session.js` to the active model's resize profile:

```javascript
// agent-session.js, afterToolCall (~line 281):
const resizeOptions = this.model?.inputLimits?.images?.resize;
const normalizedContent = await normalizeToolResultImages(content, {
  autoResizeImages: this.settingsManager.getImageAutoResize(),
  ...(resizeOptions ? { resizeOptions } : {}),
});
```

The defaults in `dist/utils/image-resize-core.js` are 2000×2000 pixels
and 4.5 MB base64 per image, JPEG quality 80. The failing session's 4 MB
PNGs were all *within* these defaults. The mechanism is per-image; nothing
accumulates across images. Sixteen legal 4 MB images are collectively
illegal, and no code notices.

**Overflow detection with compact-and-retry.** `pi-ai/dist/utils/overflow.js`
matches assistant error messages against 23 `OVERFLOW_PATTERNS` and, on a
match, `agent-session.js:2067` runs one bounded compact-and-retry. The list
already contains byte-size 413s for two providers:

```javascript
/request_too_large/i,   // Anthropic request byte-size overflow (HTTP 413)
/^4(?:00|13)\s*(?:status code)?\s*\(no body\)/i,  // Cerebras bodyless 413
```

Lunaroute's `PAYLOAD_TOO_LARGE` matches none of the patterns. Verified
against the installed matcher:

```javascript
isContextOverflow(
  new Error('413: {"code":"PAYLOAD_TOO_LARGE","declared_bytes":17706402,...}')
)  // → false
```

So the 413 arrived as a hard, non-retryable error — which matches the
transcript exactly: repeated 413 error entries, seven manual model
switches, no compaction attempt. The recovery machinery existed; the error
string simply was not in its vocabulary.

**Declarative `maxRequestBytes`.** The model schema
(`@earendil-works/pi-ai/dist/types.d.ts:800`) accepts:

```typescript
export interface ModelInputLimits {
  maxRequestBytes?: number;  // "Maximum serialized provider request size in bytes"
  images?: ModelImageInputLimits;  // { resize, maxPerMessage, maxPerRequest }
}
```

A grep across the entire installed runtime finds `maxRequestBytes`,
`maxPerMessage`, and `maxPerRequest` only in schema definitions. No code
reads them. They are validated, accepted into `models.json`, and ignored.
The field that would have made this failure visible has been declared but
never wired.

These three near-misses define the extension's requirements precisely:
accumulate bytes across images (the resize does not), recognize the error
class (the overflow matcher does not), and enforce the declared budget
(the config does not).

## 5. The byte accounting model

The meter at the center of the extension estimates the serialized request
body as:

```
estimatedBody ≈ Σ base64Len(image.data)     (base64 inflates binary by ×4/3)
              + Σ textLen(text blocks)
              + ~1.5% framing overhead      (JSON keys, tool declarations)
```

Validation came from the 413 itself. Reconstructing the active context at
the failing assistant entry — branch walk, latest compaction, latest
context edit per target, mirroring `buildSessionProjection()` — produced:

| Measure | Value |
|---|---|
| Images in context | 16 |
| Σ base64 image data | 17.32 MB |
| Σ text | 0.21 MB |
| **Estimated body** | **17.53 MB** |
| Lunaroute `declared_bytes` | 17,706,402 (17.71 MB) |

Within 1%. The formula is not a guess; it is a measurement with an error
bar. Image dimensions come from header parsing rather than an image
library: PNG stores width and height as big-endian u32 at byte offsets 16
and 20 (immediately after the signature and the IHDR chunk header); JPEG
requires walking markers from offset 2 until a start-of-frame segment;
GIF keeps two little-endian u16 values at offsets 6 and 8; WebP has
VP8X/VP8/VP8L chunk headers. About thirty lines of code in total, and the
meter decodes only the first 512 base64 characters of each image, so the
scan of a 78 MB session stays fast.

## 6. Configuration that works today

Before any extension code, one native fix is available and live: the
resize profile. `~/.pi/agent/models.json` accepts per-provider and
per-model `inputLimits.images.resize`, deep-merged field-by-field by
`mergeInputLimits` in `dist/core/provider-composer.js`:

```json
{
  "providers": {
    "lunaroute": {
      "modelOverrides": {
        "deepseek-4.1-flash": {
          "inputLimits": { "images": { "resize": {
            "maxWidth": 1280, "maxHeight": 1280,
            "maxBytes": 350000, "jpegQuality": 80 } } }
        },
        "glm-5.3-vision": {
          "inputLimits": { "images": { "resize": {
            "maxWidth": 2560, "maxHeight": 1600,
            "maxBytes": 500000, "jpegQuality": 80 } } }
        }
      }
    }
  }
}
```

The numbers are not arbitrary. DeepSeek-4.1-Flash resizes images
server-side toward an ~800×800 pixel count and caps billing at 384 tokens
per image regardless of input resolution; a 2000×2000 and a 5000×5000
image cost the same after resize. GLM vision keeps roughly a 1500-pixel
shorter side. Pixels beyond those caps buy nothing from the model and
cost the full base64 price in transport. For UI screenshots, converting
PNG to JPEG at these dimensions is a ≥90% size reduction with no
perceptible loss; for text-dense or very wide captures the correct
operation is cropping, because the model's detail ceiling is enforced
server-side and cannot be bought back with megapixels.

This config has one structural limit: it applies at ingestion. Images
already in history keep their encoding, and the profile never accumulates
across images. That is what the extension exists to fix.

## 7. The extension

`extensions/image-budget/` closes the loop with six cooperating modules:

```text
extensions/image-budget/
├── index.ts        registerPiExtension + event/command wiring
├── meter.ts        byte accounting, dimension sniffing, formatting
├── budget.ts       settings + budget resolution (16 MiB default for lunaroute)
├── profile.ts      session quality profiles + CustomEntry persistence
├── gate.ts         tool_result / input gating before history
├── slim.ts         retroactive pass via appendContextEdit
└── images-view.ts  /images overlay (multi-select)

session events ──▶ meter ──▶ report ──▶ status widget ("imgs 14.2/16.0MB ██▓ 89%")
                              │──▶ /images overlay
                              └──▶ gate (projected-body check)
tool_result/input ────────────gate──▶ resizeImage() → replacement content
after_provider_response(413) ─▶ slim flow
slim ─▶ appendContextEdit() per image ─▶ recompute meter
```

**The meter** scans `buildSessionProjection()` — the model-visible truth,
including compaction and edits — and produces per-image rows (entry id,
dimensions, mime, base64 bytes, share of budget) plus the estimated body
against the budget. The budget resolves in priority order: explicit
setting, the model's `inputLimits.maxRequestBytes` (inert in core today,
forward-compatible if enforcement arrives), per-provider default
(lunaroute: 16,777,216), else off.

**Gating** hooks `tool_result` and `input`. Both run *before* pi's own
`normalizeToolResultImages` — the ordering is guaranteed in the
`afterToolCall` source ("runs after the extension hook so images injected
or replaced by extensions are normalized too"), which means an extension
that returns pre-resized images gets them passed through untouched. When a
new image would push the projected body past a warn threshold (default 80%
of budget), the extension asks — downscale, keep, drop — or downscale
silently in `auto` mode. The image enters history already small.

**The quality profile** (`lossy80`, `lossy95`, `lossless`) is session state.
It is written through `pi.appendEntry("image-budget-config", {...})` as a
`CustomEntry` — a state entry that is never sent to the model — and
replayed on `session_start` by walking the branch for the latest such
entry. This is the documented pi state-reconstruction pattern, and it makes
the setting survive resume and branching. There is an alternative worth
knowing about and rejecting: `pi.setModel({...ctx.model, inputLimits: ...})`
works immediately because `setModel` (verified at `agent-session.js:1645`)
accepts any model object without registry validation, and the resize
profile is re-read from the active model at every ingestion. But the
patched profile is lost when the session resumes — pi re-resolves
provider and model id from the registry — and every toggle appends a
`model_change` entry. The `CustomEntry` route has neither defect.

## 8. Retroactive slimming

The retroactive mechanism is the `ContextEditEntry`, and its semantics are
what make the feature safe:

```typescript
appendContextEdit(targetId: string, replacement: ContextEditEntry["replacement"]): string;
// replacement === null        → omit the target from model context entirely
// replacement: full message   → replace ONLY the target message content
```

Four properties, each verified against the implementation and the session
format: the entry is append-only (raw history, UI, exports, and accounting
keep the original); it affects only future model context; it is
branch-relative (navigating the tree to a point before the edit reveals
the original again); and the latest edit wins when several target the
same entry. A tool-result replacement may carry a content array including
new `ImageContent` blocks, which is what allows downscaled images to
replace originals without dropping the surrounding message.

The cost is prompt-cache invalidation from the first edited entry
forward. This is the one genuinely irreversible consequence, and the
confirm dialog states it before any edit is appended. In the situation
the flow exists for — a request that is already rejected — the cache for
the affected range is worthless anyway, so the trade is correct. What
must not happen is silent slimming; the flow always asks.

The implementation detail that took the most care was age ordering.
"Downscale all but the last N images" is entry-age semantics, but the
report sorts images by bytes. The slim pass therefore maps entry ids to
their positions in a fresh projection and filters by age there — the
projection is needed in that function regardless, to read the original
messages for replacement construction.

## 9. Validation

The extension was tested against a copy of the forensic session — the
78 MB file with the real 413 in it — driven through tmux
(`pi --session <copy>` inside `tmux new-session`, keystrokes via
`send-keys`, evidence via `capture-pane`). Testing on a copy is not
paranoia: the original file turned out to be still growing under a
separate live pi instance, from 785 entries at forensics time to 1091 by
test time.

The recorded sequence:

1. **Startup meter**: `imgs:48.2MB` — budget unresolved because the
   session's model was `openai-codex/gpt-6-luna`; 36 images, 430 KB of
   text, 49.4 MB estimated body.
2. **`/model lunaroute/glm-5.3`**: widget switched to
   `imgs 49.4MB/16.0MB ██████████ 309%` — the budget resolved from the
   provider default and the `model_select` handler refreshed.
3. **`/images`**: overlay listing all 36 images with decoded dimensions
   (1920×1080 PNGs, 1613×1728, 2000×458, 1680×1221 JPEGs), entry ids
   matching the earlier file forensics.
4. **Slim**: select all → downscale → confirm →
   `image-budget: slimmed 36 image(s), saved ~38.3MB of context bytes.`
   The meter fell to `imgs 10.5MB/16.0MB` — 66%, under budget.
5. **File diff**: exactly 38 new entries — 36 `context_edit` (one per
   image; replacements are `image/jpeg`, largest 269,176 base64 chars,
   under the 350 KB profile cap), one `model_change`, one
   `thinking_level_change`. Raw history untouched.
6. **Persistence**: `/image-quality` set to lossless appended an
   `image-budget-config` CustomEntry; after `/exit` and restart, the
   profile replayed and the meter still read 10.5MB/66%.

Two real defects surfaced during this testing, and both are worth
recording exactly because they are the kind that only interactive
validation finds.

**A crash.** The first `/images` keypress killed pi. The crash log
(`~/.pi/agent/crashes.json`) contained:

```text
TypeError: Cannot read properties of undefined (reading 'toLowerCase')
    at parseKeyId (…/pi-tui/dist/keys.js:604)
    at matchesKey (…/pi-tui/dist/keys.js:634)
    at ImagesViewModal.handleInput (…/extensions/image-budget/images-view.ts:29)
```

The cause: pi-tui's `Key` helper defines only special keys —
`Key.escape`, `Key.enter`, `Key.up`, `Key.ctrl("c")`. `Key.q` and
`Key.ctrl_c` are `undefined`, and `matchesKey(data, undefined)` throws
inside pi's input dispatch, which takes the process down. The fix is to
compare letters directly (`data === "q"`, `data === "a"`) and to use the
function form for modifiers (`Key.ctrl("c")`). A fail-soft
`matchesKey` would be a reasonable upstream improvement.

**A stale widget cluster.** After a model switch, the extension's
`ctx.ui.setStatus` entry updated immediately, but the launcher's
dashboard status cluster — the segment of the footer that renders
registered widgets — kept its startup render. The launcher
(`extensions/launcher/index.ts`) calls `refreshDashboard(ctx)` only on
`session_start`; the cluster is otherwise rendered once per session. The
compaction-meter's cluster entry was stale the same way, which confirms
it is a launcher-level behavior, not an extension bug. The fix inside
image-budget: call the shared `refreshDashboard(ctx)` after every report
refresh, so both meters now update on model switches. The upstream cure
would be the launcher refreshing its cluster on `model_select` and
`message_end`.

## 10. What remains

Three items are open, recorded here with their reasons rather than as
vague follow-ups.

- **Live gating and 413-recovery tests** need a provider round trip. The
  gating logic is threshold arithmetic shared with the validated meter,
  and the 413 path is a status check plus the tested slim flow, but
  neither has been exercised against a real request. A low-cost test
  exists: set `warnThreshold` to 0.5 in a scratch session and attach one
  image.
- **Payload calibration** — measuring the real serialized payload in
  `before_provider_request` and feeding the ratio back into the overhead
  constant — was deliberately deferred. `JSON.stringify` of a 17 MB
  payload on every request is not free, and the 1.5% constant is already
  validated to within 1%.
- **Upstream changes worth requesting**: runtime enforcement of
  `maxRequestBytes`; byte-awareness in `estimateTokens`;
  `PAYLOAD_TOO_LARGE` in `OVERFLOW_PATTERNS` (or a pluggable pattern hook,
  which would have made the Lunaroute 413 recoverable with zero extension
  code).

The general lesson stands independently of pi. When a system reports one
unit of a constraint (tokens) while an enforcement point uses another
(bytes), the failure arrives as an error the system cannot classify —
and the fix starts with an accounting model of the unit that actually
binds, validated against the enforcement point's own numbers.
