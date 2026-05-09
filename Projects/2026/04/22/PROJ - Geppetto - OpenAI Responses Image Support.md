---
title: Geppetto OpenAI Responses Image Support
aliases:
  - Geppetto OpenAI Responses Image Support
  - Project Geppetto OpenAI Responses Image Support
  - Geppetto multimodal image support
  - GP-53
  - OpenAI Responses image support in Geppetto
tags:
  - project
  - geppetto
  - openai
  - responses-api
  - multimodal
  - vision
  - images
  - go
status: active
type: project
created: 2026-04-22
repo: /home/manuel/workspaces/2026-04-21/hair-v2/geppetto
---

# Geppetto OpenAI Responses Image Support

This project slice is the work of adding real image-input support to Geppetto's OpenAI Responses engine so that applications using `ai-api-type=openai-responses` can send screenshots and other image evidence as actual multimodal request parts instead of silently degrading to text-only prompts.

It started as a downstream product debugging problem in `css-visual-diff`, but the actual defect lived one layer lower in Geppetto itself. The right fix was therefore not a product shim and not a profile tweak. The right fix was to patch the provider request serializer inside Geppetto, document the behavior clearly, and then prove with a live smoke that the model really looked at the image.

> [!summary]
> This work currently has three important identities:
> 1. a concrete OpenAI Responses engine bugfix in Geppetto that adds `input_image` request-part support
> 2. a small but important clarification of Geppetto's current multimodal turn contract around `PayloadKeyImages`
> 3. a live validation effort proving the patched local engine can ground answers in image content, while also revealing that the installed `pinocchio` binary is older and therefore not a valid comparison target for the new fix

## Why this project exists

The immediate motivation came from a visual-review workflow in `css-visual-diff`. That tool had already been wired to use Geppetto for OpenAI Responses-backed multimodal review, and it looked as though image-based review should have been possible. But a deeper audit showed an uncomfortable mismatch: the product was building multimodal turns, the profile/bootstrap path was resolving correctly, and the model call was succeeding, yet the Geppetto Responses request builder still only serialized text parts for ordinary messages.

That kind of bug is especially deceptive because it can still produce plausible results. If the application also sends a strong textual summary of the evidence, the model may answer well enough that the lack of real image transport is easy to miss. The project therefore exists to close that gap and to make Geppetto's behavior match both the official OpenAI Responses API contract and the expectations set by Geppetto's own higher-level turn model.

There is also a broader architectural reason this work matters. Geppetto already had working image handling in the regular OpenAI chat-completions path, and it already had a turn helper for user multimodal blocks. That meant the Responses engine was the odd one out. Fixing it improves consistency across provider engines and makes Geppetto's provider-neutral turn model more trustworthy.

## Current project status

This slice is functionally successful.

What is now implemented:

- OpenAI Responses `input_image` serialization in:
  - `pkg/steps/ai/openai_responses/helpers.go`
- request-part fields for:
  - `image_url`
  - `file_id`
  - `detail`
- mixed message serialization where a user message can now contain:
  - `input_text`
  - one or more `input_image` parts
- support for these image transports:
  - remote URL
  - inline bytes converted to base64 data URL
  - inline base64 string content
  - direct `data:` URL passthrough
  - optional `file_id` passthrough on `input_image`
- regression coverage for:
  - URL image input
  - inline bytes
  - mixed text + multiple images
  - token-count request shape
- documentation updates for the Responses engine and multimodal helper contract
- a live smoke proving that the local patched engine causes the model to actually inspect the image

What is not solved yet:

- canonical provider-neutral `input_file` support in the turn model
- audio or broader generalized media modeling
- a deduplicated shared media-normalization layer between OpenAI chat-completions and OpenAI Responses
- validation through a locally built `go run ./cmd/pinocchio ... --images ...` path, because the local `pinocchio` repo currently does not build cleanly in this workspace due to an unrelated Clay/Glazed mismatch

## Project shape

At a high level, this work sits at the intersection of four layers:

1. **The provider-neutral conversation model**
   - `Turn`
   - `Block`
   - payload keys such as `PayloadKeyText` and `PayloadKeyImages`
2. **The OpenAI Responses request builder**
   - convert Geppetto blocks into `/v1/responses` JSON input items
3. **Downstream consumers of the same request shape**
   - normal inference
   - `/responses/input_tokens`
4. **Validation and proof tooling**
   - unit tests
   - ticket-local repro scripts
   - live smoke image fixture

The most useful mental model is that Geppetto engines are translators. They do not invent the product's semantics from scratch. They take a provider-neutral turn model and translate it into provider-specific wire format. The bug here was therefore a translation omission.

## Architecture

```mermaid
flowchart TD
    A[Application / CLI / runner] --> B[Geppetto Turn + Block model]
    B --> C[OpenAI Responses engine]
    C --> D[buildResponsesRequest]
    D --> E[buildInputItemsFromTurn]
    E --> F[/v1/responses request JSON]
    F --> G[OpenAI Responses API]
    D --> H[/v1/responses/input_tokens request JSON]

    subgraph Turn model
      B1[PayloadKeyText]
      B2[PayloadKeyImages]
    end

    subgraph Responses content parts
      P1[input_text]
      P2[input_image]
    end

    B --> B1
    B --> B2
    E --> P1
    E --> P2
```

The critical detail is that both the inference path and the token-count path reuse the same request builder. That is a strong architectural choice because it means a serializer fix propagates naturally to both behaviors.

## Project status boundary

A lot of the value in this work came from drawing the boundary correctly.

The OpenAI Responses API supports more than just image input. The official docs also describe `input_file`, and the system is clearly part of a wider multimodal interface. But Geppetto's provider-neutral turn model does not yet have a fully fleshed-out, first-class cross-provider representation for files, audio, or arbitrary content-part arrays comparable to the current image path.

So the working rule for this project became:

- fix real image parity now
- keep the patch small and explicit
- do not smuggle a whole new canonical media model into the same change

That decision made the implementation safer, the review surface smaller, and the live validation much easier to interpret.

## Implementation details

The implementation is best understood as a narrow extension of the existing OpenAI Responses serializer, not as a redesign of Geppetto's engine framework.

### The original defect

Before the patch, `pkg/steps/ai/openai_responses/helpers.go` defined a `responsesContentPart` structure that only handled text, function-call, and tool-result fields. The ordinary message path inside `buildInputItemsFromTurn(...)` only inspected `PayloadKeyText` and emitted `input_text` or `output_text`. It never looked at `PayloadKeyImages`.

That meant a user block like this conceptually existed in Geppetto:

```go
turns.NewUserMultimodalBlock(
    "What changed in this screenshot?",
    []map[string]any{{
        "media_type": "image/png",
        "content": imageBytes,
    }},
)
```

but the Responses engine would serialize only the text part.

### The fix

The patch extended the Responses content-part model with image-capable fields:

- `image_url`
- `file_id`
- `detail`

Then the old text-only message builder was replaced with a slightly richer path that still preserves the previous behavior for text, reasoning, and tools while now appending `input_image` parts for non-assistant messages that carry `PayloadKeyImages`.

Conceptually the new path works like this:

```text
payload
  -> extract text
  -> emit input_text or output_text
  -> if role is not assistant:
       inspect PayloadKeyImages
       for each image:
         normalize url / content / file_id
         emit input_image
```

### Image normalization behavior

The image normalization helper now accepts the existing Geppetto image map shape and supports several useful cases:

1. **Remote URL**

```go
{
  "media_type": "image/png",
  "url": "https://example.com/image.png",
}
```

becomes an `input_image` with `image_url` set to that URL.

2. **Inline bytes**

```go
{
  "media_type": "image/png",
  "content": []byte(...),
}
```

becomes an `input_image` whose `image_url` is a base64 data URL.

3. **Inline base64 string**

```go
{
  "media_type": "image/jpeg",
  "content": "...base64...",
}
```

also becomes a base64 data URL.

4. **Direct `data:` URL string**

If the content already arrives as a `data:` URL, it is passed through.

5. **Optional `file_id`**

If a provider-specific `file_id` is present, it can be passed through on `input_image` even though canonical cross-provider file support is not yet the main subject of this project.

6. **Image detail**

Valid `detail` values such as `high` are preserved, while absent or invalid detail values default safely to `auto`.

### Current algorithm shape

A simplified version of the current logic looks like this:

```go
func buildResponsesMessageParts(role string, payload map[string]any) []responsesContentPart {
    parts := []responsesContentPart{}

    if text := extractText(payload); text != "" {
        partType := "input_text"
        if role == "assistant" {
            partType = "output_text"
        }
        parts = append(parts, responsesContentPart{Type: partType, Text: text})
    }

    if role == "assistant" {
        return parts
    }

    for _, img := range extractImages(payload) {
        if part, ok := responsesImagePartFromMap(img); ok {
            parts = append(parts, part)
        }
    }

    return parts
}
```

and the image normalizer behaves roughly like:

```go
func responsesImagePartFromMap(img map[string]any) (responsesContentPart, bool) {
    detail := normalizeDetail(img["detail"])

    if url := firstNonEmptyString(img["url"], img["image_url"]); url != "" {
        return inputImage(url, "", detail), true
    }

    if content := img["content"]; content != nil {
        if isDataURLString(content) {
            return inputImage(content.(string), "", detail), true
        }
        if mediaType := firstNonEmptyString(img["media_type"]); mediaType != "" {
            return inputImage(dataURL(mediaType, content), "", detail), true
        }
    }

    if fileID := firstNonEmptyString(img["file_id"]); fileID != "" {
        return responsesContentPart{Type: "input_image", FileID: fileID, Detail: detail}, true
    }

    return responsesContentPart{}, false
}
```

### Why the patch stayed small

The existing reasoning/tool logic inside `buildInputItemsFromTurn(...)` is careful and subtle. It preserves:

- reasoning items
- assistant follower messages
- function-call chains
- function-call outputs

That code was already correct and already well-tested. The implementation therefore avoided a large structural refactor and instead focused the change around ordinary message-part construction. That is exactly the kind of small, high-leverage patch that is easier to review and less likely to destabilize unrelated behavior.

## Live validation

The most important part of this project is that it did not stop at unit tests.

A synthetic image fixture was created with facts not present in the prompt text:

- a visible passcode: `4319`
- a blue triangle on the left

Then the exact local Geppetto GP-53 code path was exercised against the live OpenAI Responses API using a ticket-local Go program.

The prompt was intentionally impossible to answer from prompt text alone:

> What four-digit passcode is shown in the image, and what shape/color appears on the left?

The results were the proof point.

### Without the image

The model said, in effect, that it could not see the image and asked for an upload or description.

### With the image

The model answered correctly:

> The passcode is 4319, and a blue triangle appears on the left.

That result matters because it proves real visual grounding, not merely successful request serialization.

## Reproduction assets

The work is fully retraceable from ticket-local assets.

### Ticket docs

- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/ttmp/2026/04/22/GP-53-OPENAI-RESPONSES-MULTIMODAL-MEDIA--add-multimodal-media-support-to-geppetto-openai-responses/design-doc/01-openai-responses-multimodal-media-support-analysis-design-and-implementation-guide.md`
- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/ttmp/2026/04/22/GP-53-OPENAI-RESPONSES-MULTIMODAL-MEDIA--add-multimodal-media-support-to-geppetto-openai-responses/reference/01-investigation-diary.md`

### Repro scripts

- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/ttmp/2026/04/22/GP-53-OPENAI-RESPONSES-MULTIMODAL-MEDIA--add-multimodal-media-support-to-geppetto-openai-responses/scripts/01_live_openai_responses_image_smoke.sh`
- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/ttmp/2026/04/22/GP-53-OPENAI-RESPONSES-MULTIMODAL-MEDIA--add-multimodal-media-support-to-geppetto-openai-responses/scripts/01_live_openai_responses_image_smoke.go`
- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/ttmp/2026/04/22/GP-53-OPENAI-RESPONSES-MULTIMODAL-MEDIA--add-multimodal-media-support-to-geppetto-openai-responses/scripts/02_pinocchio_image_probe.sh`

### Fixture and outputs

- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/ttmp/2026/04/22/GP-53-OPENAI-RESPONSES-MULTIMODAL-MEDIA--add-multimodal-media-support-to-geppetto-openai-responses/sources/01-live-responses-image-smoke/passcode-card.png`
- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/ttmp/2026/04/22/GP-53-OPENAI-RESPONSES-MULTIMODAL-MEDIA--add-multimodal-media-support-to-geppetto-openai-responses/various/01-live-responses-image-smoke/output.log`
- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/ttmp/2026/04/22/GP-53-OPENAI-RESPONSES-MULTIMODAL-MEDIA--add-multimodal-media-support-to-geppetto-openai-responses/various/02-pinocchio-image-probe/output.log`

## Commits

The implementation and documentation were recorded in a clean sequence of commits:

- `4b65391` — `Add image inputs to OpenAI Responses engine`
- `0f65946` — `Document Responses image input support`
- `2953218` — `Record GP-53 image support implementation`
- `b68c8a3` — `Record GP-53 live image validation`

That sequence is useful because it separates:

- code change,
- repo docs change,
- ticket docs/bookkeeping,
- live proof and repro capture.

## Important project docs

The main source of truth for this slice is the ticket workspace in the Geppetto repo:

- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/ttmp/2026/04/22/GP-53-OPENAI-RESPONSES-MULTIMODAL-MEDIA--add-multimodal-media-support-to-geppetto-openai-responses/`

The most important code locations are:

- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/pkg/steps/ai/openai_responses/helpers.go`
- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/pkg/steps/ai/openai_responses/helpers_test.go`
- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/pkg/steps/ai/openai_responses/token_count_test.go`
- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/pkg/doc/topics/06-inference-engines.md`
- `/home/manuel/workspaces/2026-04-21/hair-v2/geppetto/pkg/turns/helpers_blocks.go`

## Open questions

- Should the current OpenAI chat-completions image normalization logic and the Responses image normalization logic eventually be deduplicated into a shared helper?
- What is the right provider-neutral turn representation for canonical `input_file` support?
- Should audio and broader content-part modeling be handled by extending the current payload-map pattern or by introducing a more strongly typed content model?
- Once local `pinocchio` builds cleanly again, does `go run ./cmd/pinocchio ... --images ...` behave correctly against the patched Geppetto in the workspace?

## Near-term next steps

- open a follow-up ticket when there is a concrete need for canonical provider-neutral file or audio support
- investigate the local `pinocchio` build failure in this workspace so that the live image smoke can also be reproduced through the local Pinocchio CLI path
- consider whether a durable multimodal regression harness should live in Geppetto outside ticket-local scripts

## Project working rule

> [!important]
> Keep provider bugfixes narrow, evidence-backed, and live-validated. If the bug is in the serializer, fix the serializer first, prove the model can ground on the media, and only then consider broader cross-provider schema redesign.
