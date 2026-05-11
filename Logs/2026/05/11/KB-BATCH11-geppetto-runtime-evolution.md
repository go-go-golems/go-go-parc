# KB Batch 11: Geppetto / Scopedjs / Pinocchio Runtime Evolution

## Batch scope

This batch processes the handoff document's **Batch B — Geppetto / Scopedjs / Pinocchio runtime evolution**.

Analyzed project reports:

1. [[PROJ - Scopedjs Runtime and Demo - Geppetto and Pinocchio]]
2. [[PROJ - Scopedjs Runtime - Geppetto Final State]]
3. [[PROJ - Geppetto - Opinionated JS APIs and Engine Profiles]]
4. [[PROJ - Geppetto - OpenAI Responses Image Support]]
5. [[PROJ - PinocchioRC - Declarative Config Plans and Cleanup]]
6. [[PROJ - Goja REPL Essay - Implementation Deep Dive]]

## Executive summary

Batch B produced one new Tribal entry: [[Tribal/geppetto-engine-config-vs-runtime-behavior]]. The central repeated pattern is that reusable infrastructure should own generic primitives, while applications own runtime policy. Geppetto owns engine settings, provider serializers, engine profiles, and reusable runtime packaging. Applications such as Pinocchio, scopedjs adopters, and the Goja essay own prompts, tools, scope, local config precedence, teaching routes, and UX-specific behavior.

The batch also reinforced [[Tribal/goja-execution-model]], [[Tribal/goja-embedding-in-go]], [[Tribal/dsl-normalized-config-compiled-plan]], and [[Tribal/app-config-vs-command-config-separation]], but the new Geppetto runtime-boundary entry is the main output.

## What was written

### New Tribal entry

- [[Tribal/geppetto-engine-config-vs-runtime-behavior]] — created because the same separation appears across scopedjs, Geppetto engine profiles, PinocchioRC config plans, Goja REPL Essay, and the narrow OpenAI Responses serializer fix.

## What could / should be written later

### Tribal candidates promoted or reinforced

| Concept | Seen in | Status | Notes |
|---------|---------|--------|-------|
| **Prepared JavaScript environment as one model-facing tool** | Scopedjs Runtime, Scopedjs Final State, Geppetto JS runner/API work | 3/3 — covered for now by [[Tribal/geppetto-engine-config-vs-runtime-behavior]] and [[Tribal/goja-embedding-in-go]] | Could become separate if more non-demo adopters appear. |
| **Serialized shared runtime executor** | Scopedjs Final State, goja execution model, scenario/runtime patterns | 2/3 or 3/3 depending scope | Likely a variation of [[Tribal/goja-execution-model]]. |
| **Thin teaching surface over real backend** | Goja REPL Essay, Pinocchio scopedjs demo, go-minitrace HTML/export readers | 3/3 — candidate | Teaching/demo surfaces should visualize real backend behavior instead of reenacting it. |
| **Narrow provider serializer fix** | Geppetto OpenAI Responses image support, Geppetto Open Responses boundary work | 2/3 | Fix provider wire translation first; do not redesign the whole schema in the same patch. |
| **Declarative layered config plan** | PinocchioRC, app config vs command config cluster | 2/3 | Strongly reinforces [[Tribal/app-config-vs-command-config-separation]]. |

### On-Ramp candidates

| Concept | Seen in | Status | What's missing from public docs |
|---------|---------|--------|--------------------------------|
| **OpenAI Responses API content parts** | Geppetto Open Responses, OpenAI Responses Image Support | 2/5 | OpenAI docs exist, but Geppetto's provider-neutral turn translation gotchas are not public. |
| **Argo CD / local-path PVC sync waves** | Goja Essay Deployment if included later, platform batches | 1/5 | Not counted in this batch because the REPL Essay implementation report was used instead of the deployment report. |
| **Storybook/MSW for live technical essays** | Goja REPL Essay, future frontend teaching surfaces | 1/5 | Public docs are tool-specific, not about backend-faithful technical essays. |

## What was updated / reinforced

- [[Tribal/goja-execution-model]] — reinforced by scopedjs shared-runtime serialization and Goja REPL Essay's real session/evaluation teaching surface.
- [[Tribal/goja-embedding-in-go]] — reinforced by prepared runtime environments, native modules/globals/bootstrap, and runtime packaging.
- [[Tribal/dsl-normalized-config-compiled-plan]] — reinforced by PinocchioRC's explicit config-plan model and scopedjs builder/runtime construction.
- [[Tribal/app-config-vs-command-config-separation]] — reinforced by PinocchioRC's removal of hidden config-path helpers and preservation of provenance.

## Per-project extraction

### 1. Scopedjs Runtime and Demo

**Role in batch**: first implementation slice for packaging a bounded JavaScript environment as one LLM-facing tool.

**Tribal candidates**:
- Prepared JavaScript environment as one model-facing tool — `EnvironmentSpec` + `Builder` + `BuildRuntime` + `RegisterPrebuilt` / `NewLazyRegistrar`.
- App-owned scope, modules, and helper docs — Geppetto owns packaging, app owns meaning.
- Runtime manifest as model-facing capability description.
- Demo surface as observability for tool calls — Pinocchio TUI renders JavaScript, input, console output, and result.

**On-Ramp candidates**:
- goja embedding and native modules — covered by existing goja KB entries.

### 2. Scopedjs Runtime Final State

**Role in batch**: cleaned-up final scopedjs contract.

**Tribal candidates**:
- Serialized shared runtime executor — reused runtime evaluation protected around the whole eval lifecycle.
- Honest lifecycle descriptions — prebuilt, lazy, and future per-session are distinct API claims.
- Static manifest for lazy runtime descriptions — model-facing capability docs must not disappear in lazy mode.
- Tri-state eval option overrides — options need to distinguish unset from explicit false.

**On-Ramp candidates**:
- None new.

### 3. Geppetto JS APIs and Engine Profiles

**Role in batch**: canonical engine-config vs runtime-behavior split.

**Tribal entries**:
- [[Tribal/geppetto-engine-config-vs-runtime-behavior]]

**Tribal candidates**:
- Engine profiles are engine-only — provider/model/settings, not prompt/tool/runtime policy.
- Opinionated JS runner as default public path — `gp.runner` wraps lower-level session machinery.
- Runtime metadata materialization must be centralized — prompt/middleware updates must rebuild execution wiring consistently.

**On-Ramp candidates**:
- Engine profiles in Geppetto (lookupable only inside our docs; covered by Tribal entry for now).

### 4. Geppetto OpenAI Responses Image Support

**Role in batch**: provider serializer bugfix and live validation case.

**Tribal candidates**:
- Narrow provider serializer fix — fix `input_image` translation in the Responses engine without inventing a general media model.
- Live smoke for multimodal grounding — prove the model actually saw image-only facts.
- Provider-neutral turn model translated by engine-specific serializer.
- Shared request builder for inference and token-count paths.

**On-Ramp candidates**:
- OpenAI Responses API content parts (2/5).
- Multimodal request validation with synthetic fixtures (1/5).

### 5. PinocchioRC Declarative Config Plans and Cleanup

**Role in batch**: configuration analog of the same separation principle.

**Tribal entries**:
- Reinforces [[Tribal/geppetto-engine-config-vs-runtime-behavior]] and [[Tribal/app-config-vs-command-config-separation]].

**Tribal candidates**:
- Declarative layered config plan — precedence as explicit data, not hidden path helpers.
- Provenance-aware config loading — parsed field history records which layer/source wrote a value.
- Remove old architecture stories — delete Viper-era helpers so new code cannot bypass plan model.
- App-owned local profile policy — Pinocchio declares `.pinocchio-profile.yml`; Glazed/Geppetto provide generic plan machinery.

**On-Ramp candidates**:
- Glazed declarative config plans (1/5, internal-domain seed).

### 6. Goja REPL Essay

**Role in batch**: teaching surface that exercises real backend session behavior.

**Tribal candidates**:
- Thin teaching surface over real backend — essay routes are wrappers over `replapi` / `replsession`, not a second implementation.
- Live technical essay with backend instruments — prose, buttons, and raw payloads stay synchronized with real API responses.
- Storybook/MSW as article component development loop.
- Article-only profile override route — demo behavior scoped to teaching routes instead of prematurely broadening public API.

**On-Ramp candidates**:
- Storybook/MSW for backend-faithful technical essays (1/5).

## Candidate decisions

### Created now

- [[Tribal/geppetto-engine-config-vs-runtime-behavior]] — threshold reached and broad enough to cover the batch without spawning narrow docs.

### Do not create yet

- **Prepared JavaScript environment as one model-facing tool** — strong candidate but currently covered by the new entry plus goja KB entries; split later if non-demo adoption grows.
- **Thin teaching surface over real backend** — good candidate across Goja Essay, Pinocchio demos, and minitrace readers; defer until one more teaching/reporting batch confirms it.
- **OpenAI Responses API content parts** — on-ramp candidate only 2/5.

## Suggested index changes

Add Batch 11 entries for all six projects and update campaign counts:

- Analyzed so far: 68
- Remaining: 99
- Tribal entries: 20

Update candidate tracking:

- Add [[Tribal/geppetto-engine-config-vs-runtime-behavior]] as created.
- Add thin teaching surface over real backend as a 3/3 review-needed candidate.
- Add OpenAI Responses API content parts as a 2/5 On-Ramp candidate.

## Follow-up review questions

1. Should prepared JavaScript environment as one model-facing tool eventually split out from the Geppetto runtime-boundary entry?
2. Should thin teaching surfaces over real backends become a separate Tribal entry after the frontend/reporting batches?
3. Should OpenAI Responses content parts get an On-Ramp if another multimodal project appears?
