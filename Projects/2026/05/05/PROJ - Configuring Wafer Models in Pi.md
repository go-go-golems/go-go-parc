---
title: Configuring Wafer Models in Pi
aliases:
  - Wafer Models in Pi
  - Pi Wafer Configuration
tags:
  - project
  - pi
  - wafer
  - llm
  - configuration
  - models
status: completed
type: project
created: 2026-05-05
repo: /home/manuel/code/gec/2026-03-16--gec-rag
---

# Configuring Wafer Models in Pi

Modern coding agents such as Pi rely on external language model providers to power their inference. While Pi ships with built-in support for many commercial providers — Anthropic, OpenAI, Google, Groq, and others — it also permits users to register arbitrary OpenAI-compatible endpoints through a declarative configuration file. This project documents the end-to-end process of adding Wafer Pass, a fast open-source model inference service, to Pi's model registry. The work involved understanding Pi's configuration schema, gathering authoritative model specifications from the provider's documentation, transforming that data into the correct JSON shape, and verifying the result through Pi's own model enumeration command.

> [!summary]
> This project achieved three outcomes:
> 1. Registered Wafer Pass as a custom provider in Pi via `~/.pi/agent/models.json`
> 2. Captured three models — DeepSeek-V4-Pro, Qwen3.5-397B-A17B, and GLM-5.1 — with exact context windows, max output tokens, reasoning flags, image support, and per-token costs sourced from official documentation
> 3. Verified live registration through `pi --list-models`, confirming all three models appear with correct metadata

## Why This Configuration Matters

Coding agent harnesses are only as useful as the models they can reach. A harness that is locked to a single provider or a static model list limits the engineer's ability to experiment with newer, faster, or cheaper alternatives. Pi's design philosophy explicitly rejects this constraint: it exposes a `models.json` file that any user can edit to add new providers, new models, or override built-in defaults.

Wafer Pass represents a specific class of provider that is worth registering: it serves optimized, open-weight models (DeepSeek-V4-Pro, Qwen3.5-397B-A17B, GLM-5.1) through a standard OpenAI-compatible Chat Completions endpoint, at speeds claimed to be "multiples faster than base SGLang on Wafer's stack." For a coding workflow, this means lower latency on long-context reasoning tasks, access to thinking-enabled models for complex refactoring, and a flat-rate subscription model rather than unpredictable per-token billing.

The broader lesson is that any OpenAI-compatible endpoint — whether Wafer, a self-hosted vLLM server, a LiteLLM proxy, or a corporate gateway — can be integrated into Pi using the same pattern demonstrated here.

## Pi's Model Configuration System

Before modifying anything, one must understand how Pi discovers and registers models. Pi maintains a `models.json` file in its agent configuration directory (by default `~/.pi/agent/models.json`). This file is not a flat list of model names. It is a structured JSON document with a top-level `providers` object, where each provider key maps to an object containing:

- `baseUrl`: the API endpoint root
- `api`: the API dialect — for most third-party providers this is `openai-completions`
- `apiKey`: authentication, which can be a literal string, an environment variable name, or a shell command
- `models`: an array of model descriptors, each with fields like `id`, `name`, `contextWindow`, `maxTokens`, `reasoning`, `input`, and `cost`

Pi reloads this file each time the model selector is opened (via `/model` or Ctrl+L). No daemon restart is required. This hot-reload behavior makes iterative configuration safe: one can edit the file, open the model selector, and immediately see whether the new entries are valid.

The `models.json` format is documented in Pi's own help at `docs/models.md` within the Pi package installation. Two important rules govern custom providers:

1. **Provider-level defaults cascade to models.** If a provider declares `api: "openai-completions"`, every model under it inherits that dialect unless overridden.
2. **Custom providers are merged with built-ins.** A provider key that does not match a built-in provider (such as `anthropic`, `openai`, `google`) is treated as entirely custom. Its models are added to the registry alongside all built-in entries.

## The Wafer Pass Service

Wafer Pass is a subscription-based inference service hosted at `https://pass.wafer.ai/v1`. It exposes two endpoints:

- **OpenAI-compatible:** `https://pass.wafer.ai/v1` (Chat Completions)
- **Anthropic-compatible:** `https://pass.wafer.ai/v1/messages` (Messages API)

The service currently hosts three models, each with distinct characteristics:

| Model | Family | Max Context Tokens | Max Output Tokens | Reasoning | Images | Overage Input | Overage Output | Overage Cached |
|---|---|---|---|---|---|---|---|---|
| DeepSeek-V4-Pro | DeepSeek, 1.6T MoE | 262,144 | 32,768 | Yes | No | N/A (no overage) | N/A | N/A |
| Qwen3.5-397B-A17B | Qwen3.5, 397B MoE | 262,144 | 32,768 | Yes | Yes | $0.60 / M | $3.60 / M | $0.06 / M |
| GLM-5.1 | Z.AI flagship | 202,752 | 32,768 | No | Yes | $1.50 / M | $4.50 / M | $0.15 / M |

A few details are worth emphasizing because they affect how the models are configured in Pi:

**Context windows are hard caps.** The documentation states explicitly that requests exceeding the max context token limit return HTTP `400`. This means the `contextWindow` field in `models.json` should match the provider's documented cap exactly, not a rounded estimate. For DeepSeek-V4-Pro and Qwen3.5-397B-A17B, this is `262144`. For GLM-5.1, it is `202752`.

**Max output tokens differ from context window.** While the models can accept up to ~262K tokens of input, their generation capacity is bounded separately. The Wafer documentation does not explicitly state a generation limit, but the setup examples for agent harnesses (Cline, Roo Code, etc.) consistently recommend `32768` as the Max Output Tokens value. This figure was adopted as the `maxTokens` field for all three models.

**Reasoning and image support are model-specific.** DeepSeek-V4-Pro supports extended thinking via a `thinking` object in the request body, but it is not multimodal. Qwen3.5-397B-A17B supports both reasoning and image input. GLM-5.1 supports images but not reasoning. These boolean flags (`reasoning`, `input`) control how Pi renders model capabilities in the selector and whether it offers thinking-level toggles for a given model.

**Cost structure matters for the registry.** Even though Wafer Pass operates on a subscription model with included requests, it also publishes overage rates. Including these in `models.json` allows Pi to compute and display estimated costs during long sessions, which is valuable for budgeting context.

## Gathering Authoritative Specifications

The first step in any provider registration is obtaining authoritative model metadata. There are three common sources:

1. **The provider's `/v1/models` endpoint** — returns a machine-readable list
2. **The provider's public documentation** — usually the most reliable source for context windows, pricing, and feature flags
3. **The model family's upstream documentation** (Hugging Face, model cards, research papers) — useful for cross-checking, but the provider may impose its own limits

In this case, the `/v1/models` endpoint returned HTTP `503`, indicating the service was temporarily unavailable. Rather than rely on estimates, the official documentation at `https://docs.wafer.ai/wafer-pass` was fetched using the Defuddle CLI, which extracts clean markdown from web pages. The resulting document, stored at `/home/manuel/code/wesen/claw-stuff/docs/wafer-pass.md`, contains the exact token limits, pricing table, and reasoning flags used in the final configuration.

This pattern — documentation-first, API-second — is a robust heuristic for model registration. Provider APIs can be down, rate-limited, or return stale data. A well-maintained documentation page is usually the source of truth for hard caps and pricing.

## The Registration Process

With the specifications in hand, the registration process follows a clear sequence:

### Step 1: Locate the Configuration File

The active Pi configuration lives at:

```
~/.pi/agent/models.json
```

This file was already present and contained two existing custom providers (`openai-codex` and `fireworks`). The task was to add a third provider block without disrupting the existing entries.

### Step 2: Define the Provider Block

A new provider key `wafer` was added under the `providers` object with the following structure:

```json
"wafer": {
  "baseUrl": "https://pass.wafer.ai/v1",
  "api": "openai-completions",
  "apiKey": "YOUR_WAFER_API_KEY",
  "models": [
    {
      "id": "Qwen3.5-397B-A17B",
      "name": "Qwen 3.5 397B A17B",
      "reasoning": true,
      "input": ["text", "image"],
      "contextWindow": 262144,
      "maxTokens": 32768,
      "cost": {
        "input": 0.6,
        "output": 3.6,
        "cacheRead": 0.06,
        "cacheWrite": 0
      }
    },
    {
      "id": "DeepSeek-V4-Pro",
      "name": "DeepSeek V4 Pro",
      "reasoning": true,
      "input": ["text"],
      "contextWindow": 262144,
      "maxTokens": 32768,
      "cost": {
        "input": 0,
        "output": 0,
        "cacheRead": 0,
        "cacheWrite": 0
      }
    },
    {
      "id": "GLM-5.1",
      "name": "GLM 5.1",
      "reasoning": false,
      "input": ["text", "image"],
      "contextWindow": 202752,
      "maxTokens": 32768,
      "cost": {
        "input": 1.5,
        "output": 4.5,
        "cacheRead": 0.15,
        "cacheWrite": 0
      }
    }
  ]
}
```

Each field choice is deliberate:

- **`baseUrl`** points to the OpenAI-compatible root, not the `/v1/messages` Anthropic path, because Pi's `openai-completions` dialect is the standard integration path for third-party providers.
- **`apiKey`** is stored as a literal value in the local configuration file. Pi supports environment variable references and shell commands (prefix with `!`), but a literal key is the simplest approach for a personal workstation.
- **`reasoning`** is `true` for DeepSeek-V4-Pro and Qwen3.5-397B-A17B because both support extended thinking modes. This flag tells Pi to offer thinking-level controls (minimal, low, medium, high, xhigh) when these models are selected.
- **`input`** is `["text", "image"]` for the multimodal models (Qwen and GLM) and `["text"]` for DeepSeek, which does not accept image input through the Wafer endpoint.
- **`contextWindow`** matches the hard caps from the documentation exactly: `262144` for DeepSeek and Qwen, `202752` for GLM.
- **`maxTokens`** is set to `32768` for all three, derived from the standard agent harness setup recommendations in the Wafer documentation.
- **`cost`** uses the documented overage rates per million tokens. DeepSeek-V4-Pro has no overage support yet, so its costs are recorded as zeros.

### Step 3: Validate JSON Structure

After editing, the file was validated with `jq` to ensure it remained parseable. This step caught a structural issue: a missing closing brace that had been introduced during the insertion. JSON validation is not optional when hand-editing configuration files; a single syntax error will prevent Pi from loading any custom providers.

### Step 4: Verify Live Registration

The final verification step is to ask Pi itself whether it recognizes the new models:

```bash
pi --list-models
```

The output confirmed all three entries:

```
wafer         DeepSeek-V4-Pro                             262.1K   32.8K    yes       no
wafer         GLM-5.1                                     202.8K   32.8K    no        yes
wafer         Qwen3.5-397B-A17B                           262.1K   32.8K    yes       yes
```

The columns show provider, model name, context window, max output tokens, reasoning support, and image support. The match between the configured values and the live listing confirms the registration is correct.

## A Note on the Parallel Pinocchio Configuration

This project modified Pi's `models.json` directly. The same workstation also maintains a `profiles.yaml` for Pinocchio (another coding agent harness) at `~/.config/pinocchio/profiles.yaml`. That file already contained a `wafer-base` profile and several stacked model profiles (`wafer-deepseek-v4-pro`, `wafer-qwen3.5-397b`, etc.). The Pi configuration and the Pinocchio configuration are independent systems that happen to point at the same API endpoint. There is no requirement that they stay in sync, but for operational clarity it is useful to keep their model IDs and context window values consistent. The `profiles.yaml` was left untouched because it was already correct; only Pi's registry needed the new entries.

## Lessons and Reusable Patterns

Several patterns from this project generalize to any provider registration task:

### 1. Documentation-first discovery

When an API endpoint is unavailable, public documentation is usually the most reliable fallback. The Defuddle CLI tool is particularly useful here: it strips navigation, ads, and interactive elements from a documentation page, producing a clean markdown file that is easy to search and cite. The captured document at `/home/manuel/code/wesen/claw-stuff/docs/wafer-pass.md` now serves as a durable, offline reference for Wafer's current model specifications.

### 2. Distinguish model family limits from provider limits

The upstream Qwen3.5-397B-A17B model is advertised with a 1M token context window on some hosting platforms. Wafer, however, enforces a hard cap of 262,144 tokens. The provider's limit is the one that matters for configuration. Always use the provider's documented cap, not the model family's theoretical maximum.

### 3. JSON validation before runtime testing

A malformed `models.json` does not produce a helpful error message in Pi; it simply omits the custom providers from the model list. Validating with `jq '.' models.json` before testing saves time and eliminates a common failure mode.

### 4. The `pi --list-models` command is the ground truth

After any change to `models.json`, running `pi --list-models` is the fastest way to confirm that Pi has loaded the new entries. This command does not require a network connection to the provider; it only checks the local registry. If a model appears here but fails at inference time, the problem is likely authentication, rate limiting, or a provider-side issue rather than a configuration error.

### 5. Preserve cost data even for subscription providers

Wafer Pass bills through a subscription, but it also publishes overage rates. Recording these in `models.json` gives Pi the data it needs to show cost estimates in the status bar. This is especially valuable during long coding sessions where context window usage can grow quickly.

## Open Questions

- Will Wafer add a native `/v1/responses` endpoint for Codex compatibility? The documentation currently recommends a LiteLLM proxy for this use case.
- Will DeepSeek-V4-Pro eventually support overage billing, or will it remain subscription-quota-only?
- Should the `maxTokens` value be revisited if Wafer publishes explicit generation limits per model?

## Related Files and References

- Pi configuration: `~/.pi/agent/models.json`
- Wafer documentation (local copy): `/home/manuel/code/wesen/claw-stuff/docs/wafer-pass.md`
- Pinocchio profiles: `~/.config/pinocchio/profiles.yaml`
- Pi model configuration documentation: `~/.nvm/versions/node/v22.22.1/lib/node_modules/@mariozechner/pi-coding-agent/docs/models.md`

## KB reviews

- [[KB-BATCH14-pi-extensions-tooling]] (2026-05-11) — Batch K Pi extension/tooling review; created [[Tribal/pi-extension-event-seams]] and advanced Pi TUI/model-config candidates.

## Related KB entries

- [[Tribal/pi-extension-event-seams]] — Pi lifecycle/event seams, prompt shaping, tool-call mutation, TUI surfaces, and model/config integration discipline.
- [[Fundamentals/host-mediated-sandbox-principles]] — the host/runtime boundary principle behind narrow extension capabilities and mediated side effects.

## Near-Term Next Steps

- Monitor Wafer's documentation for new models or updated context window values
- Consider adding Wafer models to Pi's scoped model list (`/scoped-models`) for quick Ctrl+P cycling during coding sessions
- Evaluate whether the `maxTokens` value should be increased if Wafer raises generation limits
