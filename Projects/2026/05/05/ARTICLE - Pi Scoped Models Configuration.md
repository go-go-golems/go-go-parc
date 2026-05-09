---
title: "Pi Scoped Models Configuration"
aliases:
  - Pi Enabled Models
  - Pi Model Cycling
  - Pi Scoped Models
tags:
  - article
  - playbook
  - pi
  - configuration
  - llm
  - models
status: active
type: article
created: 2026-05-05
repo: /home/manuel/code/gec/2026-03-16--gec-rag
---

# Pi Scoped Models Configuration

Pi's model selector is powerful by default: it lists every built-in and custom provider model that the system knows about. But in practice, an engineer working on a coding task rarely needs access to twenty or thirty models. What they need is a curated shortlist — the models they actually use, ordered by preference, accessible with a single keyboard shortcut. Pi solves this with *scoped models*, a configurable subset of the full model registry that is cycled through with Ctrl+P and Shift+Ctrl+P. This article explains how scoped models work, how to configure them, and how to reason about which models belong in your personal shortlist.

> [!summary]
> Three principles govern effective scoped model configuration:
> 1. Use the `enabledModels` array in `settings.json` to define your cycle list
> 2. Prefer provider-qualified IDs (`zai/glm-5.1`, `wafer/GLM-5.1`) when multiple providers offer the same model name
> 3. Scoped models cycle with Ctrl+P; thinking level is toggled independently with Shift+Tab

## Why Scoped Models Exist

The full Pi model list can be overwhelming. On a typical workstation with several custom providers, the output of `pi --list-models` may contain dozens of entries: every Anthropic Claude variant, every OpenAI GPT release, every self-hosted Ollama model, every third-party provider. Scrolling through this list with `/model` or Ctrl+L is fine for occasional exploration, but it is inefficient for the common case of switching between your two or three preferred models mid-session.

Scoped models solve this by letting you declare a *working set*. Once declared, Ctrl+P cycles forward through the set and Shift+Ctrl+P cycles backward. The cycle is instantaneous — no network calls, no provider checks, just a local registry lookup. This makes it practical to switch models as often as you switch mental modes: from a fast cheap model for quick bash commands, to a large reasoning model for complex architecture decisions, to a multimodal model when you need to inspect an image.

## The `enabledModels` Setting

Scoped models are controlled by the `enabledModels` field in Pi's settings. The setting accepts an array of model identifier patterns. Each entry can be:

- A plain model ID: `"gpt-5.5"`, `"DeepSeek-V4-Pro"`
- A provider-qualified ID: `"zai/glm-5.1"`, `"wafer/GLM-5.1"`
- A wildcard pattern: `"claude-*"`, `"gpt-5*"`, `"gemini-2*"`

The patterns are matched against the full model registry after all custom providers have been loaded. The order of entries in the array determines the cycle order.

### Where to set it

`enabledModels` can be set globally or per-project:

| Location | File | Scope |
|----------|------|-------|
| Global | `~/.pi/agent/settings.json` | All projects |
| Project | `.pi/settings.json` (in working directory) | Current project only |

Project settings override global settings, so you can maintain a default shortlist globally and specialize it for particular codebases.

### The matching rules

When Pi resolves `enabledModels`, it performs a pattern match against every registered model's identifier. The identifier format is `provider/model-id` internally, but you can match on either the full qualified form or just the model ID:

- `
`"gpt-5.5"` matches the model with ID `gpt-5.5` from any provider
- `"zai/glm-5.1"` matches only the `glm-5.1` model from the `zai` provider
- `"wafer/GLM-5.1"` matches only the `GLM-5.1` model from the `wafer` provider

This distinction matters when multiple providers host the same model family. Z.AI and Wafer both offer a `GLM-5.1` model, but with different characteristics. Z.AI's version supports reasoning and generates up to 128K output tokens. Wafer's version does not support reasoning and caps output at 32.8K tokens. Using the unqualified `"glm-5.1"` would match both, potentially including an unwanted variant in your cycle. Provider qualification eliminates ambiguity.

## A Concrete Example: The Author's Working Set

The following configuration demonstrates a practical scoped model list for a developer who works across multiple model families and providers:

```json
{
  "enabledModels": [
    "gpt-5.5",
    "kimi-for-coding",
    "zai/glm-5.1",
    "wafer/GLM-5.1",
    "DeepSeek-V4-Pro",
    "Qwen3.5-397B-A17B"
  ]
}
```

The reasoning behind each entry:

**`gpt-5.5`** — The default model. A general-purpose frontier model with strong reasoning, image understanding, and a 272K context window. It is the baseline against which other models are compared.

**`kimi-for-coding`** — A specialized coding model from the Kimi family, optimized for code generation and repository-scale context. It provides a different architectural approach than the GPT series, which is useful when the baseline model produces suboptimal code patterns.

**`zai/glm-5.1`** — Z.AI's flagship model with reasoning support and a 128K output capacity. This is the model to reach for when a task requires extended chain-of-thought reasoning or when the response itself needs to be long (documentation generation, test scaffolding, detailed analysis).

**`wafer/GLM-5.1`** — The same underlying model family as the Z.AI version, but hosted on Wafer's optimized inference stack. It lacks reasoning support and has a smaller output cap (32.8K), but it is significantly faster and included in a flat-rate subscription. This entry exists for speed-sensitive tasks where reasoning is not required.

**`DeepSeek-V4-Pro`** — A 1.6T parameter MoE model with explicit thinking support. The thinking mechanism is exposed through a `thinking` object in the API request, and Pi's `reasoning: true` flag enables thinking-level controls for this model. It is the choice for deep architectural reasoning, complex debugging, and multi-step planning.

**`Qwen3.5-397B-A17B`** — A 397B parameter MoE model with both reasoning and multimodal support. It rounds out the set as an alternative frontier model with different strengths in coding and mathematics.

The cycle order is deliberate. It starts with the general-purpose default, moves through specialized coding and reasoning variants, and ends with another frontier model. This creates a natural progression from "quick and general" to "deep and specialized" and back.

## How Thinking Levels Interact with Scoped Models

A common misconception is that scoped models can carry per-model thinking levels. They cannot. The `enabledModels` array only controls *which* models are in the cycle. Thinking level is a separate axis of configuration.

Pi supports six thinking levels: `off`, `minimal`, `low`, `medium`, `high`, `xhigh`. These are controlled through three mechanisms:

| Mechanism | Scope | How |
|-----------|-------|-----|
| `defaultThinkingLevel` | Global default | Set in `settings.json` |
| `--thinking` flag | Per invocation | `pi --thinking high "solve this"` |
| Shift+Tab | Per session | Toggle during an active session |

There is one shortcut that combines model and thinking: the `--model` CLI flag accepts a thinking suffix. `pi --model sonnet:high` selects the model *and* sets thinking to `high` in a single argument. However, this syntax does not work inside `enabledModels`. The scoped list contains model identifiers only; thinking is adjusted separately.

In practice, this separation is a feature, not a limitation. It lets you cycle through your model shortlist and independently tune the thinking depth for the task at hand. If you are doing rapid exploration with a fast model, you might run at `low` thinking. When you switch to a reasoning model for a hard problem, you bump to `high` with a single Shift+Tab press. The two controls compose cleanly.

## Practical Configuration Workflow

The recommended workflow for building a scoped model list is iterative:

### Step 1: Survey the full registry

Run `pi --list-models` to see everything that is currently registered. This includes built-in providers, custom providers from `models.json`, and any provider packages loaded through `packages` in `settings.json`.

### Step 2: Identify candidates

Look for models that complement each other. A good shortlist usually contains:

- One general-purpose frontier model (the default)
- One fast/cheap model for quick tasks
- One reasoning model for hard problems
- One multimodal model for image tasks
- One or two experimental models from different families

Avoid including models that are too similar. If two models have nearly identical specs and behavior, only one belongs in the cycle.

### Step 3: Handle name collisions

If multiple providers offer the same model ID, use provider-qualified patterns. Run `pi --list-models | grep <model-name>` to see all matches before deciding whether qualification is needed.

### Step 4: Edit settings.json

Add the `enabledModels` array to `~/.pi/agent/settings.json` (global) or `.pi/settings.json` (project). Validate the JSON with `jq` before testing.

### Step 5: Verify the cycle

Open Pi and press Ctrl+P repeatedly. Confirm that the model name in the footer cycles through your entries in the expected order. If a model is missing, check that its ID matches exactly (case-sensitive for some providers) and that the provider is loaded.

### Step 6: Refine over time

Scoped models are not permanent. Add new models as providers release them. Remove models that you never select. Reorder the list as your workflow evolves. The cost is a few seconds of editing `settings.json` — no restart required.

## Anti-Patterns

### Including every available model

If `enabledModels` contains twenty entries, Ctrl+P cycling becomes slower than using `/model` directly. The point of scoped models is curation. If you find yourself skipping past entries, remove them.

### Mixing providers without qualification

`"glm-5.1"` in `enabledModels` will match every provider that hosts a model with that ID. If you intended only the Z.AI version but Wafer also offers one, both will appear in your cycle. Always qualify when ambiguity exists.

### Expecting per-model thinking defaults

Do not try to encode thinking levels in `enabledModels`. `wafer/DeepSeek-V4-Pro:high` is not valid syntax. Set thinking globally or toggle it per-session.

### Forgetting about project overrides

If you set `enabledModels` in `.pi/settings.json` for one project and later wonder why your global list is not active, remember that project settings take precedence. This is usually correct behavior — different codebases benefit from different model specialties — but it can be surprising if you forgot about the override.

## Related Configuration

Scoped models interact with several other Pi settings:

- **`defaultProvider` and `defaultModel`** — These determine which model is active at startup. If the default model is not in `enabledModels`, it will still be the starting point, but the first Ctrl+P will jump to the first entry in the scoped list.
- **`packages`** — Provider packages (like `npm:@thesethrose/pi-zai-provider`) add models to the registry. A model cannot be scoped until its provider package is loaded.
- **`thinkingBudgets`** — Custom token budgets per thinking level can be defined in `settings.json`. These apply globally across all models that support reasoning.

## References

- Pi settings documentation: `~/.nvm/versions/node/v22.22.1/lib/node_modules/@mariozechner/pi-coding-agent/docs/settings.md`
- Pi model configuration: `~/.nvm/versions/node/v22.22.1/lib/node_modules/@mariozechner/pi-coding-agent/docs/models.md`
- Author's current settings: `~/.pi/agent/settings.json`
- Author's current model registry: `~/.pi/agent/models.json`
