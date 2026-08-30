---
title: "Executable Architecture Constraints in a TypeScript Visualization Library"
aliases:
  - Executable Architecture Constraints
  - HSPLOT Architecture Guardrails
  - Testing Visualization Boundaries
tags:
  - article
  - typescript
  - visualization
  - architecture
  - testing
  - packaging
status: active
type: article
created: 2026-08-30
repo: /home/manuel/workspaces/2026-08-24/use-optkit/plot
source_files:
  - src/architecture.test.ts
  - scripts/consumer-smoke.mjs
  - package.json
---

# Executable Architecture Constraints in a TypeScript Visualization Library

A visualization package can preserve its architecture only if its tests make prohibited designs fail. TypeScript types describe valid values at selected boundaries, but they do not by themselves prevent a planner from importing React, a renderer from interpreting grammar algebra, CSS from recreating absent presentation, or a published tarball from exposing an unusable entrypoint. `@hyperslop-systems/plot` addresses these failure modes with a small architectural test suite in `/home/manuel/workspaces/2026-08-24/use-optkit/plot/src/architecture.test.ts` and a complementary clean-consumer package test in `scripts/consumer-smoke.mjs`.

The important property of this approach is its scope. These tests do not claim to prove every semantic property of the compiler. They protect a set of explicit boundaries that would otherwise be easy to erode during ordinary maintenance. The compiler accepts a serializable `PlotDocument`, normalizes it into `NormalizedGrammar`, produces a complete `PlotPlan`, derives renderer-neutral semantics and a scene, and lets React and SVG act only at the final host boundary. The tests assert that this division remains visible in imports, symbols, types, CSS selectors, package exports, and a separately installed consumer.

> [!summary]
> - `src/architecture.test.ts` uses source-level negative assertions to keep canonical IR, React-free compiler boundaries, mechanical scene lowering, and plan-owned presentation intact.
> - The suite treats deleted names and compatibility aliases as architectural liabilities: their reappearance is a test failure, not an accidental API restoration.
> - `scripts/consumer-smoke.mjs` tests what textual guards cannot: packed exports, declaration usability, peer dependency resolution, CSS delivery, and an author-only installation without React.
> - These are bounded guardrails. They must be maintained alongside semantic, unit, integration, and browser tests rather than presented as a complete correctness proof.

## Why architecture needs executable constraints

The central execution path has several stages with distinct responsibilities. `PlotDocument` is the public, serializable language. `compileGrammar` checks and normalizes that language. The normalized form supports data materialization, statistics, position adjustment, scale training, geometry planning, coordinate transformation, and layout. `planPlot` returns presentation and mark geometry. `buildScene` lowers planned geometry to renderer-neutral nodes. `SvgRenderer` and `PlotHost` consume the scene at the UI edge.

Each boundary exists because decisions made at one stage must not be silently recomputed at another. Scale training should not happen in a renderer. A scene builder should not decide whether an axis receives layout space. React should not become a dependency of document validation. A consumer that uses the functional authoring API should construct the same canonical document that a caller could write as a literal object. These are design statements, but design statements decay if they are not connected to observable checks.

The architecture suite converts selected statements into source assertions. Its helper reads source files relative to the test using `readFileSync` and `fileURLToPath`. Each test then examines a deliberately limited set of production modules. This is not a compiler test that imports the modules and exercises their outputs. It is an explicit structural test: the assertion is about source-level dependency or forbidden vocabulary. That directness is valuable when the undesired condition is itself structural.

For example, importing React in `compile.ts` might not change a unit test result. A bundled application might still render correctly. Yet that import changes the package’s runtime and dependency boundary. A textual assertion can detect the import at the point it appears. In the same way, reintroducing a `panel` shortcut on `PlotPlan` may retain compatibility while compromising the rule that every panel is first-class. A test can identify that particular declaration before downstream callers begin to depend on it again.

## The canonical grammar boundary

The first architectural assertion requires downstream stages to consume `NormalizedGrammar` rather than `PlotDocument`. The test reads `plan.ts`, `stats.ts`, the group, position, scale, geometry, and coordinate pipeline modules, `coordinates.ts`, `variables.ts`, `semantics.ts`, and `scene.ts`. It first checks that `plan.ts` contains `NormalizedGrammar`, then rejects the word `PlotDocument` as a whole symbol from every listed downstream module.

This is a narrow but useful test. It establishes a directional rule: surface grammar reaches the compiler; downstream code receives normalized contracts. It does not prohibit every module in the repository from knowing `PlotDocument`, because authoring and compilation legitimately need it. It also does not depend on the details of the normalized type. The guarded property is that planning, statistics, variable evaluation, semantics, and scene construction do not accept the public surface document as an alternate input.

That distinction matters in a grammar-driven library. `PlotDocument` permits author-friendly optional fields and source-level forms. `NormalizedGrammar` makes effective composition, defaults, presentation choices, coordinate defaults, and diagnostic paths concrete. If a later stage can take either representation, every change must account for two forms and can bypass compilation. A caller may then receive different diagnostics or behavior depending on an internal entrypoint. The architecture test blocks the simplest way to create that second path.

The same test file protects the removal of legacy mapping and compatibility contracts. It concatenates `document.ts`, `compile.ts`, `plan.ts`, and `stats.ts`, then rejects `MappingSpec`, `BoundMapping`, `inheritMapping`, `compilePlot`, versioned `PlotDocumentV` names, and migration-related vocabulary. These names are not merely implementation details. Their return would indicate either that old mapping semantics are being restored or that a migration layer is being placed in the active production path.

Deletion is sometimes the correct API decision. A compatibility shim can preserve an obsolete conceptual model and give new code a convenient path around the canonical model. The test expresses that the old vocabulary is intentionally absent. It will need revision if a future version has a concrete, reviewed reason to support migration; until then, a failing assertion forces that decision into review instead of allowing an incidental import or helper to restore it.

## Symbols, aliases, and the shape of the plan

Structural compatibility is not limited to imports. A type can expose an alias that makes an invalid shortcut attractive even if no module imports an old name. `architecture.test.ts` specifically extracts the `PlotPlan` interface body from `plan.ts` and rejects root-level readonly `panel`, `xScale`, `yScale`, `axes`, or `layers` members.

The protected rule is that a plan has panels, not one privileged panel. Faceted output needs panel-local bounds, scales, guides, layers, and facet identity. Root aliases based on the first panel encode a false generalization. They simplify the first consumer that reads a plan but make later consumers likely to ignore facets. They also create a compatibility promise: once callers use `plan.xScale`, removing it becomes costly even though the value cannot correctly describe every panel.

This test uses an intentionally focused regular expression rather than a broad rejection of those words. The terms may be valid inside a panel contract, a local variable, or a comment explaining the architecture. The forbidden condition is the exact root interface member. The test therefore documents both the rule and its scope. It is not trying to police prose or all identifiers; it is preventing a specific public structural alias.

Named branches receive similar treatment. The production grammar modules are combined and checked for `geom.sparkline`, `chartType`, `chartKind`, and `namedChart`. Compact plots are expressed by ordinary variable composition, line geometry, presentation presence, and requested viewport. There is no separate chart identity that causes compilation, planning, or rendering to take a special route. This prevents a product convenience from becoming a parallel grammar with different scale, grouping, coordinate, or diagnostic behavior.

Source-level name checks have a maintenance cost. They can be too broad, can match a harmless comment, and can miss an equivalent design hidden behind a differently named abstraction. The answer is not to avoid them. The answer is to select names that correspond to reviewed forbidden concepts, constrain the files under inspection, and pair the check with behavioral tests. A test named “production grammar has no named-chart or sparkline branch” gives a future maintainer a clear reason to reconsider a failure rather than teaching them to rename an identifier to make CI green.

## React-free boundaries are package boundaries

The suite’s React and DOM test is another negative dependency test. It reads the document, compiler, stat definitions, statistics, pipeline modules, coordinates, variables, semantics, and planner. For each file it rejects React imports, `HTMLElement` and `SVGElement`, `globalThis.document`, `window.`, and imports whose path contains `svg` or `react`.

This asserts that the core can compile and plan without a browser or a React runtime. The rule is stronger than “the core does not render.” Browser globals and DOM types can still make server-side processing, worker execution, test setup, and package dependency installation more difficult. React imports can pull a UI assumption into code that should remain data-oriented. Keeping these files free of both allows callers to validate documents, calculate plans, inspect semantics, and generate scenes outside a browser host.

The authoring package receives its own guard. The test joins source from `author.ts`, its index and constructors, all authoring modules, and the sparkline preset. It rejects React imports, CSS imports, `PlotHost`, `SvgRenderer`, classes, `.build()`, registries, and calls or imports for `compileGrammar`, `planPlot`, and `buildScene`. It separately asserts that `compile.ts` does not import `./author`.

This preserves a functional and side-effect-free author boundary. Author helpers create plain grammar values; they do not run compilation and do not depend on a renderer. The compiler does not depend on convenience constructors. The result is useful beyond aesthetics: a plain JavaScript caller can import `/author`, create a document, then decide independently when and where to render it. The dependency direction remains from authoring surface to canonical document, then from compiler to normalized IR, rather than from core back into a convenience API.

The package manifest provides the distribution counterpart. It exports `.`, `./author`, `./react`, and `./styles.css` separately. React and `react-dom` are peer dependencies, while CSS is declared as a side effect. Separate export paths let a consumer choose authoring without importing the React host, and let a React consumer import the package stylesheet explicitly. The source guard confirms the intended code boundary; the package test confirms the published artifact honors it.

## Algebra and grammar must be lowered before consumption

The document language includes `VariableExpression` and `AlgebraExpr` values. Variables can be fields, constants, derived expressions, or unity values. Algebra composition can use `variable`, `unity`, `cross`, `nest`, and `blend`. Those forms are surface syntax. They must be compiled and materialized before planning and rendering.

The architecture suite reads `plan.ts`, `scene.ts`, `react/PlotHost.tsx`, and `renderers/svg/SvgRenderer.tsx`. It rejects imports whose paths contain `algebra` or `variables`, the type names `AlgebraExpr` and `VariableExpression`, and direct discriminant checks for `cross`, `nest`, `blend`, or `unity`. This verifies that neither planning nor either rendering boundary interprets algebra programs.

The rule is not that planned output may never contain values derived from algebra. It plainly must: a plot constructed with cross or blend composition has to reach statistics and geometry. The rule is that those programs are lowered into ordinary normalized composition before the planner and renderer receive their inputs. Later stages work with resolved dimensions, groups, facets, rows, scales, and geometry, not with an algebra abstract syntax tree.

This separation avoids duplicated semantic interpreters. If `SvgRenderer` recognizes `cross`, it must decide dimensional placement and failure behavior itself. If `PlotHost` recognizes a derived variable, its behavior can differ from a non-React consumer that calls `renderPlot`. If `scene.ts` imports variable evaluation, scene construction ceases to be a lowering stage and gains invisible data semantics. The source assertions stop those direct dependencies, while algebra, compilation, and pipeline tests provide the positive evidence that legal algebra actually lowers correctly.

The semantics guard applies the same reasoning to accessibility and inspection output. `semantics.ts` may project from grammar and stages, but it must not import `./scene`, mention `SceneGraph` or `SceneNode`, or emit SVG. Semantics are independently derived structured meaning, not labels reverse-engineered from rendering nodes. This makes semantics inspectable when a host is absent and prevents visual implementation details from becoming the only account of what a plot means.

## CSS ownership belongs to the plan

Presentation boundaries can be violated after compilation by a stylesheet. `styles.css` owns host-level layout, theming variables, diagnostics, and opt-in styling under `[data-hs-plot]:not([data-unstyled])`. It defines colors and typography, sizes the SVG container, and gives diagnostics their visible treatment. That is appropriate host ownership.

It must not recreate plot framing that the plan intentionally omitted. The architecture test extracts the `[data-part="viewport"]` rule and rejects `border:` and `background:` declarations from its body. This is a precise ownership test. A compact plot may request no frame or background through presentation policy. If viewport CSS always adds either, rendering contradicts the serializable plan despite correct planner output.

The check does not prohibit borders and backgrounds everywhere. Diagnostic boxes use them, and a theme may provide CSS variables. It only forbids them in the viewport rule that wraps the planned plot. This preserves a useful separation: CSS can provide product defaults and host layout, but the scene and plan control whether a plot itself has visual framing.

A related geometry assertion reads `pipeline/geometry.ts` and rejects `PlannedGuide`, `PlannedAxis`, and the words `title`, `legend`, and `grid`. Geometry planning is responsible for marks. Guides and presentation nodes arise from presentation resolution and layout. Combining them in one stage would make mark geometry choose explanatory policy and could cause guides to vary according to implementation details of a geom.

Finally, `scene.ts` is checked for imports of presentation and layout modules, grammar and scale terms, data-scale calculation, and ad hoc panel or tick computation. It must contain the spread operations `...guide.axis` and `...entry.swatch`, evidence that it consumes already planned guide and legend geometry. This is the positive half of a negative boundary: scene lowering does not create presentation geometry, but it faithfully lowers the complete presentation geometry it receives.

## What textual guards can and cannot prove

Textual architectural tests are effective because they are simple, local, and failure-oriented. They catch an import, a global, a deleted alias, a forbidden branch, or a CSS declaration without requiring a particular runtime input. They also survive refactoring of behavior because the intended dependency rule is stable. Their main limitation is that source text is not a semantic model.

A regex cannot prove that all planner behavior is deterministic. It cannot prove that no dynamically loaded module reaches React, that a renamed helper does not perform algebra evaluation, or that an import path without the string `svg` does not lead to SVG code. It may match a comment, string literal, or type-only import that does not create runtime coupling. Conversely, an architectural violation can be hidden behind indirection and evade a token check. These tests therefore define a protected perimeter, not a formal proof of layering.

Their reliability depends on disciplined construction. Inspect exact production files rather than the entire repository. Match whole symbols where possible. Inspect a specific interface body for a specific alias. Give test names the language of the rule they protect. Avoid treating an assertion’s implementation technique as the architecture itself: the architectural rule is “no first-panel compatibility aliases,” not “this regular expression must exist forever.” If the source layout changes, update the test while retaining the rule.

Negative checks also need positive and behavioral companions. `architecture.test.ts` confirms that `buildScene` does not train scales; plan and scene tests should verify that plots still obtain correct scales and geometry. It confirms that an author helper does not compile; author tests should establish that helper output is valid canonical grammar. It confirms a renderer does not inspect algebra; algebra tests should show that algebraic input produces expected normalized output and scenes. A healthy suite uses the fastest check for each failure mode instead of trying to force all guarantees through source scanning.

## The complementary package-consumer test

`scripts/consumer-smoke.mjs` validates a condition that internal tests cannot: whether the packed npm artifact works when consumed as a package. The script builds first, runs `npm pack` into a fresh temporary directory, locates the one emitted tarball, and installs that tarball into two independent temporary projects. It uses the npm registry cache and registry settings inside the temporary root, then removes both roots in `finally` even when an assertion fails.

The author-only consumer imports branded ID constructors and `renderPlot` from the package root, then imports the author DSL from `@hyperslop-systems/plot/author`. It creates `field`, `derived`, and algebraic variables, uses `algebra.cross`, coordinate transpose, a point layer, a configured right-side guide, and an annotation. It executes the authoring result in plain JavaScript, calls `renderPlot`, and fails if there is no scene or any error diagnostic. It then verifies that `node_modules/react` is absent. This directly demonstrates both author export usability and the intended React-free installation boundary.

The React consumer writes a `tsconfig.json`, HTML entrypoint, and `main.tsx` in another clean directory. It imports the root package, authoring API, `PlotHost` from `/react`, and CSS from `/styles.css`. The fixture uses `satisfies PlotSchema`, constructs a document, invokes `renderPlot`, and passes the resulting scene and diagnostics into React. The script runs `npm install`, TypeScript no-emit checking, and a Vite production build. It then asks `npm ls react --all --json` to verify that exactly one React version is resolved and inspects generated HTML for an asset reference.

This test complements source guards rather than duplicating them. It detects missing `exports` entries, bad declaration paths, missing packaged output, broken CSS mappings, peer dependency conflicts, and install-time resolution behavior. It also exercises the declarations from a consumer’s module-resolution configuration rather than the library’s project configuration. None of those properties follow from a passing `vitest` run inside the source repository.

The package test has boundaries too. It does not run a browser interaction test, inspect pixels, guarantee a complete public API inventory, or prove compatibility with every bundler and package manager. It exercises one clean npm consumer, one author-only path, one React path, TypeScript, and Vite. That is an appropriate smoke-test scope. Browser evidence, Storybook, API extraction, compatibility matrices, and release checks can extend it when the project requires those guarantees.

## Working rules

Use executable architecture constraints when a violation has a clear observable signature and a high cost of accidental reintroduction. Keep the checks near the implementation, name the protected rule, and make them fail for the smallest relevant set of files. Do not turn all source code into a forbidden-word list. A small set of explicit constraints is reviewable; an unbounded list becomes noise.

The key points to retain are:

- A public document and a normalized IR must have one directed transition. Do not let downstream stages accept both forms.
- Deleted symbols, migration vocabulary, and convenience aliases deserve tests when retaining them would reintroduce an obsolete model.
- React-free code requires checks for imports, DOM globals, DOM types, and package installation behavior; any one of these alone is insufficient.
- Grammar algebra and derived-variable expressions must be interpreted once, before planning and rendering. Downstream render paths consume lowered data and geometry.
- CSS is part of architecture. Styles for a host wrapper must not recreate visual decisions that belong to a serializable plan.
- Textual guards are intentionally incomplete. Pair them with unit, integration, semantic, package, and browser checks that demonstrate correct positive behavior.
- A packed consumer test verifies distribution reality: exports, declarations, peer dependencies, CSS, and toolchain integration must work outside the repository.

The result is a TypeScript visualization library whose architecture is not only described in diagrams and review comments. Its important negative space is executable. A contributor who attempts to import React into the planner, revive a first-panel alias, move algebra interpretation into a renderer, add a named-chart branch, or restore an omitted frame through viewport CSS receives a focused failure at the time of change. A release that packages the wrong exports or makes authoring require React fails in a clean consumer. These checks do not replace design review, but they keep the reviewed design present in the repository’s daily feedback loop.

## Related note

- [[Hyperslop Plot - Completing the Compiler from Mechanical Scenes to Plot Algebra]] records the broader HSPLOT-005 through HSPLOT-010 compiler work and the pipeline that these constraints protect.
