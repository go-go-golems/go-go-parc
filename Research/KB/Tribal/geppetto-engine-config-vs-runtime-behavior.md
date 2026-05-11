---
title: "Geppetto Engine Config vs Runtime Behavior — How We Do It"
aliases: [engine config vs runtime behavior, geppetto engine profiles, app-owned runtime behavior, scoped runtime behavior]
tags: [knowledge-base, tribal, geppetto, pinocchio, configuration, runtime, javascript]
status: active
type: knowledge-base
created: 2026-05-11
---

# Geppetto Engine Config vs Runtime Behavior — How We Do It

> [!summary]
> Geppetto owns engine configuration: provider, model, API settings, and inference defaults. Applications own runtime behavior: prompts, tools, middleware, scoped JavaScript environments, local profile policy, and teaching/demo routes. This split keeps reusable inference infrastructure from absorbing app-specific behavior.

## The pattern

When using Geppetto, separate two questions early:

```text
engine config:    Which provider/model/settings produce tokens?
runtime behavior: What app context, tools, prompts, profiles, and routes shape the work?
```

Engine config belongs in Geppetto primitives: engine profiles, `InferenceSettings`, engine factories, and provider serializers. Runtime behavior belongs in the host application or in explicit runtime packages such as `scopedjs`, Pinocchio profile bootstrap, or REPL essay routes.

That is why the current Geppetto JS API shape is layered:

```text
gp.profiles.resolve(...)        -> engine-only resolved profile
gp.engines.fromResolvedProfile  -> engine construction
gp.runner.resolveRuntime(...)   -> app-owned runtime behavior
gp.runner.run(...)              -> execution
```

The same rule appears in `scopedjs`: Geppetto exposes a prepared JavaScript environment as one tool, but the application decides modules, globals, docs, and scope.

## Why we do it this way

The old failure mode is configuration becoming a junk drawer. A profile starts as a provider/model preset, then grows prompts, middleware, tool filters, runtime metadata, and app defaults. That feels convenient for one app, but it makes the reusable core ambiguous: changing a profile might alter the engine, the tool surface, or the application policy.

The March Geppetto cleanup made the hard cut: profiles are engine profiles. Runtime policy moved out of that subsystem. PinocchioRC made the same move for config loading: app policy is an explicit plan, while Glazed/Geppetto provide generic plan and bootstrap machinery. Goja REPL Essay keeps `pkg/replessay` as a thin lens over the real REPL instead of reimplementing sessions in the article.

This split keeps docs honest. If the runtime is shared, fresh-per-call, or future per-session, the API must say so. If a profile is engine-only, examples should not teach it as a hidden prompt/tool bundle. If an article creates a session with a profile override, that should be an article route around the real API, not frontend-only behavior.

## Where it lives

| Repo / area | Path | Use |
|-------------|------|-----|
| Geppetto | `pkg/engineprofiles/`, `pkg/steps/ai/settings/` | engine-only profiles and inference settings |
| Geppetto | `pkg/js/modules/geppetto/api_runner.go` | JS runner surface for explicit runtime assembly |
| Geppetto | `pkg/inference/tools/scopedjs/` | prepared JavaScript environments as one model-facing tool |
| PinocchioRC workspace | `glazed/pkg/config/`, `geppetto/pkg/cli/bootstrap/`, `pinocchio/pkg/cmds/profilebootstrap/` | config plans and app-owned local profile policy |
| go-go-goja | `pkg/replessay/`, `pkg/replapi/`, `pkg/replsession/` | essay routes as thin wrappers over real REPL runtime behavior |

### Related PARC project reports

- [[PROJ - Scopedjs Runtime and Demo - Geppetto and Pinocchio]] — first implementation slice: host app prepares one bounded JS environment and exposes it as one tool.
- [[PROJ - Scopedjs Runtime - Geppetto Final State]] — cleanup pass: honest lifecycle descriptions, static manifests, serialized shared runtime.
- [[PROJ - Geppetto - Opinionated JS APIs and Engine Profiles]] — canonical hard cut: engine profiles are engine-only; app runtime policy is explicit.
- [[PROJ - PinocchioRC - Declarative Config Plans and Cleanup]] — same separation applied to config discovery: generic plan machinery vs app-owned precedence policy.
- [[PROJ - Goja REPL Essay - Implementation Deep Dive]] — article routes remain thin wrappers over real REPL sessions and evaluation semantics.
- [[PROJ - Geppetto - OpenAI Responses Image Support]] — provider serializer bugfix stays narrow and does not smuggle a general media runtime model into the engine layer.

## Common mistakes

### Mixing prompts and tools into engine profiles

This is the mistake the Geppetto March 18 branch corrected. Engine profiles should answer provider/model/settings questions. System prompts, middleware, and tool selection are runtime policy. If a profile changes both, no caller can tell whether it selected a model or changed application behavior.

### Letting demo or article layers reimplement the runtime

The Goja REPL Essay keeps `pkg/replessay` narrow. It creates article-friendly routes and payloads, but session creation, evaluation, rewrite reporting, and persistence stay in `replapi` and `replsession`. A teaching surface that forks semantics stops being trustworthy.

### Promising lifecycle modes the implementation does not enforce

The scopedjs cleanup found that lifecycle language was stronger than implementation. The fixed shape uses honest current modes: prebuilt shared runtime with serialized execution, lazy fresh runtime per call, and future per-session support tracked separately. Runtime reuse must be visible in the API and protected by code.

### Hiding config precedence behind path helpers

PinocchioRC removed string-list config callbacks and Viper-era helpers because they lost provenance. When precedence matters, represent it as a plan: system, home, XDG, repo, cwd, explicit. Parsed field history should explain which layer wrote a value.

### Turning a provider bugfix into a schema redesign

OpenAI Responses image support fixed the serializer dropping `PayloadKeyImages`; it did not introduce a full file/audio/media model. Provider bugs should be narrow, tested, and live-validated before broader abstractions are introduced.

## Variations

- **Scoped JavaScript tool runtime** — Geppetto owns the reusable runtime packaging API; apps own modules, globals, scope, and helper docs.
- **JS runner API** — Geppetto exposes `gp.runner` as the simpler execution path while preserving lower-level session APIs for advanced callers.
- **Declarative config plans** — Glazed/Geppetto own generic plan resolution and provenance; Pinocchio owns `.pinocchio-profile.yml` policy.
- **Thin teaching surfaces** — Goja REPL Essay and Pinocchio demos visualize real backend behavior rather than inventing local truth.
- **Narrow provider serializer fixes** — OpenAI Responses image support changes request serialization without collapsing provider-neutral design into one patch.
