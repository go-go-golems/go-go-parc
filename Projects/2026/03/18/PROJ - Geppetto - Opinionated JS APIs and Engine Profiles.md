---
title: Geppetto JS APIs and Engine Profiles
aliases:
  - Geppetto JS APIs and Engine Profiles
  - Geppetto Opinionated JS APIs
  - Geppetto Engine Profiles Reset
  - Geppetto March 18 Branch Report
tags:
  - project
  - geppetto
  - javascript
  - profiles
  - inference
  - go
status: active
type: project
created: 2026-03-18
repo: /home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto
---

# Geppetto JS APIs and Engine Profiles

This note is a branch-diff report for the Geppetto work in `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto`, compared against `origin/main`. It is the follow-on note to [[PROJ - Scopedjs Runtime - Geppetto Final State]] and the earlier [[PROJ - Scopedjs Runtime and Demo - Geppetto and Pinocchio]] note, but the center of gravity here is different: this branch is less about adding one new feature package and more about cleaning up the public execution model around engines, profiles, and the JavaScript API.

> [!summary]
> This Geppetto slice has three tightly related outcomes:
> 1. a more opinionated JavaScript runner surface through `gp.runner`
> 2. a hard architectural split between engine configuration and application-owned runtime behavior
> 3. a large documentation-and-diary pass that makes the branch legible as an intentional platform cleanup rather than a pile of renames

## What this report is based on

This report is synthesized from two sources:

- the live Geppetto diff from `origin/main..HEAD`
- the ticket diaries and changelogs for:
  - `GP-46-OPINIONATED-JS-APIS`
  - `GP-47-RUNTIME-METADATA-CLEANUP`
  - `GP-49-ENGINE-PROFILES`

The primary repo-local documents that explain the work are:

- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/ttmp/2026/03/18/GP-46-OPINIONATED-JS-APIS--opinionated-javascript-apis-for-geppetto/reference/01-manuel-investigation-diary.md`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/ttmp/2026/03/18/GP-47-RUNTIME-METADATA-CLEANUP--clean-up-javascript-runtime-metadata-resolution-and-consumption/reference/01-manuel-investigation-diary.md`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/ttmp/2026/03/18/GP-49-ENGINE-PROFILES--reintroduce-engine-profiles-and-separate-them-from-app-runtime-configuration/reference/01-manuel-investigation-diary.md`

## Branch shape at a glance

Against `origin/main`, the Geppetto repo diff is substantial but still coherent:

- 151 files changed
- 9356 insertions
- 5910 deletions

The biggest changed areas by file count are:

- `pkg/engineprofiles/`
- `pkg/js/modules/geppetto/`
- `examples/js/geppetto/`
- `pkg/doc/topics/`
- `pkg/steps/ai/settings/`
- the March 18 ticket workspaces under `ttmp/2026/03/18/`

The commit arc is unusually clean and reads almost exactly like the three-ticket story:

- `677f7a2` to `4fac7e9`: `GP-47` runtime-metadata cleanup and documentation
- `85f4024` to `a4ff5ac`: `GP-46` opinionated JS runner implementation and public-surface rewrite
- `c65c2ad` to `ba205d0`: `GP-49` host-default cleanup, package/type renames, engine-profile hard cut, and closeout

One useful way to read this branch is:

1. clean the old JS runtime-metadata seam
2. build the new JS runner API on top of that seam
3. then simplify the deeper Geppetto architecture so profiles mean engine configuration only

## Why this branch exists

The earlier March 17 scoped runtime work made Geppetto better at preparing host-owned runtimes, but it also exposed two design problems more clearly:

- the JavaScript API still taught advanced builder/session assembly as the default path
- the profile system still mixed together engine configuration and application runtime behavior

Those are different problems, but they were entangled in day-to-day use.

In practice the branch is trying to make one architectural sentence true everywhere:

```text
Geppetto owns engine configuration.
Applications own runtime behavior.
```

Once that sentence becomes the design center, most of the work in this branch stops looking arbitrary:

- engine profiles should resolve only engine settings
- JS should have a runner surface that assembles app runtime behavior explicitly
- docs and examples should stop teaching profile-driven runtime assembly as the default path

## The three tickets and how they fit together

### GP-47: clean up runtime-metadata consumption in the JS module

`GP-47` is the substrate ticket. Its job was not to invent the final public API, but to stop making JS callers hand-translate `profiles.resolve(...)` output into actual execution wiring.

Before this cleanup, the JS layer already knew how to resolve profile runtime metadata, but session assembly still expected callers to manually bridge that data into:

- middlewares
- system prompts
- filtered tool registries
- stamped turn metadata

The main implementation addition is `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/js/modules/geppetto/api_runtime_metadata.go`, plus integration changes in:

- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/js/modules/geppetto/api_profiles.go`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/js/modules/geppetto/api_sessions.go`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/js/modules/geppetto/api_builder_options.go`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/js/modules/geppetto/api_types.go`

The diary makes clear that this was intentionally an internal-first slice. The point was to centralize runtime-metadata interpretation before the higher-level `gp.runner` API existed.

What this changed conceptually:

- resolved profile data became executable input rather than just inspection output
- the JS module itself learned how to materialize system prompts and middleware uses
- tool filtering and runtime identity stamping moved into one shared path

What this changed for users:

- the docs and type surface started treating `resolvedProfile` as a supported low-level execution input
- `examples/js/geppetto/21_resolved_profile_session.js` became the canonical bridge example

This ticket is important not because it is the final UX, but because `GP-46` would have been awkward and repetitive without it.

### GP-46: add the opinionated JavaScript runner surface

`GP-46` is the user-facing productization ticket for the JS module.

The key decision recorded in the diary is that the JS module should not keep growing sideways through more options on `createBuilder(...)` and `createSession(...)`. Instead it should gain a dedicated runner namespace that mirrors the already-simplified Go runner model.

That namespace now exists in `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/js/modules/geppetto/module.go` and `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/js/modules/geppetto/api_runner.go`:

- `gp.runner.resolveRuntime(...)`
- `gp.runner.prepare(...)`
- `gp.runner.run(...)`
- `gp.runner.start(...)`

The important implementation detail is that this did not create a second execution engine. The new runner path reuses the existing session machinery and builder options, then packages that flow into a smaller public contract.

The internal shape is visible in:

- `prepareRunnerOptions(...)`
- `buildPreparedTurn(...)`
- `attachPreparedRunToHandle(...)`
- `preparedRunRef`

That is the real branch pattern here: additive simplification, not replacement.

The prepared-run contract is especially important because it gives one inspectable object that carries:

- `session`
- `turn`
- `runtime`
- `run()`
- `start()`

That makes the high-level API easier to teach without making it opaque.

The diary also records a few useful implementation failures that explain why the final shape looks the way it does:

- undefined `prompt` and `sessionId` access initially caused goja panics until property guards were added
- direct `systemPrompt` in `runner.resolveRuntime(...)` initially updated metadata without rebuilding the corresponding middleware, so execution ignored the prompt until a helper centralized the rewrite

Those bugs matter because they show the real design constraint: the runner path has to be a thin composition layer, but it still has to maintain consistency with the lower-level middleware model.

The public-surface rewrite was broad:

- TypeScript declarations in `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/js/modules/geppetto/spec/geppetto.d.ts.tmpl` and `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/doc/types/geppetto.d.ts`
- JS docs in:
  - `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/doc/topics/13-js-api-reference.md`
  - `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/doc/topics/14-js-api-user-guide.md`
- new runnable examples:
  - `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/examples/js/geppetto/22_runner_run.js`
  - `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/examples/js/geppetto/23_runner_profile_run.js`
  - `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/examples/js/geppetto/24_runner_start_handle.js`

The result is that the default JS story is now much simpler:

```text
resolve or build engine
-> resolve app runtime
-> runner.run(...) or runner.start(...)
```

with `createBuilder(...)` and `createSession(...)` still present, but now clearly the advanced path.

### GP-49: restore engine-only profiles and remove mixed runtime semantics

`GP-49` is the deeper architecture ticket and the biggest conceptual move in the branch.

The diary shows that the trigger was a Pinocchio inspection: profile choice and engine bootstrap had drifted into two overlapping flows. That exposed a core ambiguity in Geppetto:

- is a profile an engine preset?
- or is a profile a runtime policy bundle around prompts, middlewares, and tool selection?

The answer in this branch is deliberately strict:

- Geppetto profiles become engine profiles
- runtime behavior leaves Geppetto core

That decision lands in several layers.

### 1. `pkg/profiles` becomes `pkg/engineprofiles`

The package rename is not just cosmetic. It changes the default mental model for the entire subsystem. The new center of gravity is:

- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/engineprofiles/types.go`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/engineprofiles/registry.go`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/engineprofiles/service.go`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/engineprofiles/source_chain.go`

### 2. `StepSettings` becomes `InferenceSettings`

This rename is also architectural, not only stylistic. The earlier `step` language came from an older lifecycle model, while the actual object is the concrete configuration for inference engines.

The live settings object now sits in:

- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/steps/ai/settings/settings-inference.go`

and engine construction is now described more honestly around `InferenceSettings` and `NewEngineFromSettings(...)`.

### 3. mixed runtime payload is removed from Geppetto core

This is the hard cut that matters most.

The old mixed-model shape carried runtime concerns such as:

- system prompts
- middleware selections
- tool selections
- runtime keys and runtime fingerprints

Those are removed from the Geppetto engine-profile subsystem. `ResolveEngineProfile(...)` now returns engine-only information centered on:

- registry identity
- profile identity
- `InferenceSettings`
- profile metadata

The YAML and codec layer was rewritten around `inference_settings`, and the example profile registries under `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/examples/js/geppetto/profiles/` now reflect that engine-only shape.

This is also where the JS story gets cleaner. Instead of profiles smuggling runtime policy into runner setup, the layers are now:

```text
gp.profiles.resolve(...)
-> engine-only resolved profile
-> gp.engines.fromResolvedProfile(...) or gp.engines.fromProfile(...)
-> gp.runner.resolveRuntime(...) for app-owned runtime behavior
```

That separation is the real product move in the branch.

## Resulting architecture after the branch

The branch leaves Geppetto in a more explicit layered shape than `origin/main`.

### Engine layer

Geppetto core owns engine presets, setting merge behavior, and engine construction.

Important code locations:

- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/engineprofiles/`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/steps/ai/settings/settings-inference.go`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/inference/engine/factory/helpers.go`

### JS runtime layer

The Geppetto JS module now has a better separation between engine construction and runtime assembly.

Important code locations:

- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/js/modules/geppetto/api_engines.go`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/js/modules/geppetto/api_runner.go`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/js/modules/geppetto/api_runtime_metadata.go`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/js/modules/geppetto/api_sessions.go`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/js/modules/geppetto/module.go`

### Examples and teaching layer

This branch did not only change internals. It also changed what Geppetto teaches as the normal path.

Important files:

- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/examples/js/geppetto/README.md`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/examples/js/geppetto/10_engines_from_profile_metadata.js`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/examples/js/geppetto/21_resolved_profile_session.js`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/examples/js/geppetto/22_runner_run.js`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/examples/js/geppetto/23_runner_profile_run.js`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/examples/js/geppetto/24_runner_start_handle.js`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/doc/topics/01-profiles.md`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/doc/topics/13-js-api-reference.md`
- `/home/manuel/workspaces/2026-03-17/add-opinionated-apis/geppetto/pkg/doc/topics/14-js-api-user-guide.md`

This teaching rewrite is a large part of the branch value. Without it, the architecture cleanup would still be technically present but much harder for the next engineer to adopt correctly.

## What changed in the everyday JS mental model

Before this branch, the easiest way to misunderstand the Geppetto JS module was to treat profile resolution, engine construction, and runtime behavior as one blended flow.

After this branch, the better mental model is:

1. pick or resolve an engine profile when you need provider/model settings
2. build the engine explicitly
3. assemble application runtime behavior explicitly
4. execute through `gp.runner`

That means:

- profile registries are for engine configuration
- system prompts are app runtime policy
- middleware selection is app runtime policy
- tool selection/filtering is app runtime policy
- JS scripts have a smaller and more honest default entry point

This is a subtle but important cleanup. It makes Geppetto easier to reason about as a reusable core library because it stops pretending that application runtime policy belongs in the same abstraction as engine presets.

## The diaries as engineering evidence

One notable aspect of this branch is that the repo-local diaries are not decorative. They actually explain the sequencing and the failures that shaped the code.

Useful examples:

- `GP-47` explains why runtime-metadata cleanup had to land before the new JS runner surface
- `GP-46` records the concrete runner bugs around goja undefined properties and system-prompt materialization
- `GP-49` records the problem framing from the Pinocchio side and makes clear that the hard cut was intentional, not accidental rename churn

This makes the branch unusually reviewable. A future engineer can retrace both the code path and the reasoning path.

## Relationship to the March 17 scopedjs note

The March 17 scopedjs work and this March 18 branch are related, but they operate at different layers.

The scopedjs branch was mainly about:

- packaging host-owned runtime capabilities into one composed tool
- clarifying runtime ownership and executor semantics

This branch is mainly about:

- clarifying what Geppetto core owns versus what applications own
- clarifying what a profile means
- clarifying the public JS execution path

So the connection is real:

- scopedjs made host-owned runtime composition more concrete
- this branch makes the surrounding Geppetto APIs and profile semantics match that reality better

## Current status after the branch

As of this branch state:

- `GP-47` is complete
- `GP-46` is complete
- `GP-49` is complete
- the docs and examples now teach the new split
- the codebase terminology now matches the intended architecture more closely

The biggest practical outcome is not one function or one package rename. It is that Geppetto now presents a cleaner contract to downstream applications:

- Geppetto provides engine configuration and engine-building primitives
- applications decide runtime prompts, middleware policy, tool policy, and execution behavior

## Open questions and near-term follow-up

The branch closes the main cleanup tickets, but a few future-facing questions remain:

- Should the JS type names eventually be cleaned further so every public type uses the new engine-profile terminology uniformly?
- Should more downstream apps adopt the `gp.runner` path directly rather than preserving older lower-level assembly patterns?
- Should Geppetto eventually provide even stronger guidance or helpers for app-owned runtime planning, now that that responsibility is intentionally outside the engine-profile subsystem?

Those are follow-on product questions. The branch itself already made the important hard cuts.

## Bottom line

The most accurate summary of the Geppetto work on this branch is:

- `GP-47` made runtime metadata consumable
- `GP-46` turned that substrate into a usable JS runner API
- `GP-49` removed the deeper architectural ambiguity by making engine profiles engine-only

That combination is why this branch matters. It does not merely rename things. It makes the library's execution model more coherent across Go, JavaScript, examples, docs, and downstream adoption.
