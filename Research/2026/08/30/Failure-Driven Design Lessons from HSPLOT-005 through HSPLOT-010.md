---
title: "Failure-Driven Design Lessons from HSPLOT-005 through HSPLOT-010"
aliases:
  - HSPLOT Failure-Driven Design Lessons
  - Plot Grammar Failure Analysis
  - HSPLOT-005 through HSPLOT-010 Lessons
tags:
  - article
  - playbook
  - plotting
  - grammar-of-graphics
  - typescript
  - validation
status: active
type: article
created: 2026-08-30
repo: /home/manuel/workspaces/2026-08-24/use-optkit/plot
source_tickets:
  - HSPLOT-005
  - HSPLOT-006
  - HSPLOT-007
  - HSPLOT-008
  - HSPLOT-009
  - HSPLOT-010
---

# Failure-Driven Design Lessons from HSPLOT-005 through HSPLOT-010

HSPLOT-005 through HSPLOT-010 expanded a serializable plotting grammar without adding a second compiler, a renderer-specific language, or named-chart exceptions. The most durable results are not the added features. They are the contracts made explicit after implementation and validation exposed places where an apparently valid intermediate result was insufficient.

The source repository is `/home/manuel/workspaces/2026-08-24/use-optkit/plot`. The implementation diaries under `ttmp/2026/08/29/` and the source tests show a repeated pattern: a defect occurred at a boundary between semantic intent and visible output, between a source contract and a test fixture, or between one diagnostic and another. The correction was usually not a local patch. It was a sharper contract, a test at the correct stage, and an explicit distinction between an error that invalidates work and a warning that truthfully describes degraded work.

> [!summary]
> - A valid scene, path, or normalized document is not sufficient evidence that a plot is correct; browser visibility, topology, semantics, and diagnostics require separate proof.
> - The reliable repair was to assign ownership to one compiler stage: planning owns geometry, product adapters own continuity, coordinates transform data geometry but not typography metrics, and algebra lowers before downstream planning.
> - Tests must use valid fixtures, explicit comparators, and assertions that preserve all truthful diagnostics rather than forcing the implementation to emit only one.

## The operational model: failures locate missing contracts

The package pipeline is deliberately staged:

```text
PlotDocument + schema
  → compileGrammar → NormalizedGrammar
  → materializePlotData → statistics and positions
  → scale training → PlotPlan → SceneGraph → SVG/host
```

The pipeline has a separate `PlotSemantics` projection. That distinction matters when evaluating a failure. A compiler diagnostic identifies an invalid surface document. A planning diagnostic identifies a document that compiled but cannot produce a valid plan. A renderer defect can leave both the plan and scene correct while making the output unusable in a browser. A fixture failure can indicate that the test never reached the behavior it claimed to exercise.

HSPLOT-005 established this ownership model by making `PlotPlan` complete and `buildScene` mechanical. `src/plan.ts` resolves panel bounds, guide geometry, legend layout, annotation geometry, and mark geometry. `src/scene.ts` lowers those planned values into renderer-neutral nodes. The diary records removal of first-panel root aliases such as `panel`, `xScale`, `yScale`, `axes`, and `layers`: each panel became the only valid owner of its own plan state. This was a compatibility break, but it removed a structurally privileged path that could bypass facets.

That change made later failures diagnosable. When an output was wrong, reviewers could first inspect the plan. If plan geometry was correct but pixels were not, the defect belonged in lowering, styling, or the host. If the plan was invalid, there was no reason to change SVG. This is failure-driven design in a strict sense: each observed failure assigns a missing responsibility to one contract boundary.

## Invisible valid marks: structural validity is not visual validity

The HSPLOT-007 grouped sparse sparkline initially passed structural checks. Its path was present, its coordinates were finite, and it produced no compiler diagnostic. Browser inspection nevertheless found an almost invisible line: the computed stroke was `rgb(243, 243, 239)` against a white background. The mark existed but did not meet the user-facing requirement to be visible.

The defect was a neutral fallback color, not grouping, line geometry, or data validation. The correction in `src/scales.ts` set the neutral mark color to `var(--hs-plot-foreground, #171916)`. A CSS variable remains a serializable style value; the host resolves the theme. `src/author.test.ts` asserts the resulting stroke value. The browser proof checked computed style rather than only scene structure.

This incident changed the validation contract. A compact-plot proof now needs at least four forms of evidence:

1. The plan must contain intended marks with finite geometry.
2. The scene must contain the intended mark nodes.
3. The rendered DOM must have the intended dimensions and finite attributes.
4. Computed style must make the marks perceptible against the active host background.

The fourth check cannot be inferred from the first three. Color tokens, CSS inheritance, host themes, opacity, clipping, and dimensions are renderer/host facts. They do not turn a static server’s missing `/favicon.ico` into a plot failure, however. The Storybook server’s favicon 404 was a harmless warning: it affected server chrome, not plot execution, geometry, console behavior attributable to the plot, or rendered marks. Treating it as a product defect would obscure the actual visual regression.

## One-point paths: mathematical paths can have no visible extent

The same hardening phase found a second failure in grouped lines. A group with one datum lowered to a path containing only `M x y`. That command is valid SVG and valid scene data. It has no painted segment, so a one-point line group was invisible.

The fix did not introduce a sparkline exception or a new chart type. `src/pipeline/geometry.ts` assigns the deterministic `singlePointRadius: 2.5` to grouped-line planning. `src/scene.ts` lowers exactly one datum as an ordinary symbol node while multi-point groups remain paths. The geometry contract became: a line layer with one valid datum must have a visible planned representation. It is a line-geometry lowering rule that applies to every consumer, not a preset behavior.

This distinction prevents two bad responses. First, do not declare the path invalid; it remains a correct geometric description of the data point. Second, do not let every renderer independently decide whether to add a dot. The plan carries the decision, and lowering is mechanical. Tests must cover empty input, one point, flat domains, and sparse groups because each state tests a different contract: no data should report empty data truthfully; one point should be visible; flat values require a stable scale domain; sparse groups must not invent continuity.

## Guide compatibility: compare the explanation, not the implementation family

Configured guides in HSPLOT-008 exposed a failure in semantic identity. The first guide-compatibility implementation referenced an undefined local `scale`, causing 32 tests to fail. That was a direct runtime defect. After correcting it, a more important contract error remained: it compared channel-specific scale specifications too strictly. Color, fill, and shape mappings for the same variable split into separate guides, changing existing output from two guides to five.

The final compatibility rule uses mapped-variable identity, resolved domain and order, orientation, and title. It does not require identical aesthetic scale-family declarations. `src/scale-families.test.ts` names the expected behavior: compatible guides merge while executable row fields remain intact. The change states what a guide explains. It is not merely a container for a color scale or a shape scale.

The lesson is that compatibility predicates need a semantic definition written before their fields are chosen. “Same scale” was ambiguous because a scale has both an operational mapping and an explanatory role. The operational mappings may differ by channel while the explanatory information is identical. Conversely, equal labels alone are insufficient: a different domain, order, orientation, or variable identity must not merge.

This also distinguishes a defect from an intentional limit. HSPLOT-008 does not wrap horizontal legend entries with DOM text measurement. It reserves deterministic space and supports bounded entry count. That is a documented limitation, not a warning or rendering error. A future wrapping feature needs its own deterministic measurement inputs and tests; it should not appear as a renderer heuristic.

## Semantic-type lookup: discriminated data must be narrowed at its owner

Guide formatter validation initially reported `semanticType: null` for values that had a known type. The compiler was reading semantic type directly from `CompiledVariableRef`; the type belongs on `value.variable` after narrowing the compiled value union. Consequently, temporal and quantitative formatter validation used the wrong lookup path.

The repair was small in code and large in discipline: retrieve semantic properties from the discriminated variant that owns them. Do not duplicate a convenient subset onto a parent reference merely to avoid narrowing. Duplication becomes stale as the language grows, particularly once constants, field variables, after-stat outputs, derived variables, and generated algebra variables all participate.

The resulting validation contract is precise. A formatter is accepted only when its bounded format kind is compatible with the semantic type of the referenced value. Explicit temporal ticks are serialized ISO strings but are converted to numeric milliseconds only at the scale boundary. The formatter configuration remains a closed JSON union; no callback crosses the document boundary.

Tests should assert both diagnostic code and canonical path. A message such as “invalid format” is not enough for an editor or an authoring API to repair a nested document. The diaries repeatedly emphasize paths such as `presentation.xGuide.options.ticks.values[1]` and `variables.logged-response.expression`. Stable paths are part of the public language.

## Typography offsets: coordinate systems do not transform layout metrics

HSPLOT-009 correctly transformed plotted positions in normalized panel space, then initially applied the same transform to axis-label offsets. In a non-square panel, a 39-pixel bottom-label offset was normalized, swapped, and denormalized against the other dimension. The label moved partly outside the SVG.

The failure separated two coordinate spaces that had been conflated:

| Quantity | Correct space | Transformation rule |
|---|---|---|
| Data points, paths, rectangles, and guide anchor positions | normalized panel geometry | Transform for transpose or polar coordinates. |
| Tick lengths, label gaps, font metrics, and text offsets | device-space layout | Keep fixed on the resolved display side. |

`src/coordinates.ts` remains React-, DOM-, and SVG-free because it transforms geometry. Guide planning in `src/plan.ts` resolves display side and applies fixed device-space typography offsets afterwards. Under transpose, original x semantics appear on the vertical display axis and original y semantics appear on the horizontal display axis, but neither variable identity nor label spacing becomes a transformed data value.

The contract avoids a broader class of bugs: text collision, padding, line width, symbol radius, and other device quantities should not silently acquire data-space semantics. A coordinate feature must specify which quantities transform, which are recomputed on display sides, and which remain invariant. HSPLOT-009’s unsupported polar topologies follow the same discipline. Area, ribbon, error-bar, and boxplot shapes are omitted with `coordinate.geometry.unsupported`; the package does not approximate their boundaries from arbitrary transformed vertices.

## Multiple diagnostics: preserve every independent truth

HSPLOT-010 materializes derived variables before statistics. Invalid `log`, `sqrt`, division, power, overflow, or nonnumeric operations become `null` and increment a counted transform diagnostic. In an early test, every transformed value was invalid. The test expected the transform warning to be the only diagnostic, but the later data stage also correctly emitted its existing no-valid-positional-data error.

The correction used `arrayContaining` in `src/algebra.test.ts` rather than changing production code to suppress one result. The two diagnostics answer different questions:

- `variable.transform.invalid` says how many values failed a specified transform domain.
- The data-stage diagnostic says no valid values remain to plan a plot.

Neither replaces the other. A compiler that reports only the later error hides the cause. A compiler that reports only the transform count hides the rendering consequence. The diagnostic contract must preserve independent facts, provided they are not duplicates of the same fact at the same stage.

This is also where severity matters. Compile-time unknown references, cycles, invalid semantic types, empty blends, incompatible composition overlap, and invalid coordinate bounds are errors: no normalized value should be produced. Runtime transform-domain failures are warnings when valid rows remain: the plot can proceed while reporting dropped values and their count. If all usable positional values disappear, the downstream error is necessary and the plan/scene should not be fabricated.

An unresolved datum annotation in HSPLOT-008 follows the warning/omission form as well. Datum anchors are structurally accepted but await stable datum identity from HSPLOT-011. The planner emits a notice and no annotation node; it does not guess a row. This is a known capability boundary, not a malformed document and not a successful rendered annotation.

## Lexical sorting: output order needs a type-aware comparator

The first blend-value assertion sorted numeric values with JavaScript’s default `sort()`. It produced `[100, 60, 80, 90]`, lexical order rather than numeric order. The production pipeline already uses explicit comparisons where numeric order matters and `localeCompare` for stable string keys, visible in `src/stats.ts`, `src/pipeline/geometry.ts`, and `src/pipeline/groups.ts`. The test itself was wrong.

The correction in `src/algebra.test.ts` uses `(left, right) => left - right`. This is a fixture lesson with broader force: test normalization is part of the asserted contract. A default sort can create a false regression, mask an ordering regression, or make a test pass only because input values have convenient digit lengths.

The right comparator follows the semantic value being tested. Numeric scale values use numeric ordering. Temporal values use their numeric instant representation. Stable group and category keys use a documented string comparison. Cross algebra preserves author-supplied operand order and must not be sorted at all, because its position operands are noncommutative. Blend expansion preserves source-row and operand order before any later operation needs a comparator.

## Malformed commands and fixture mistakes: repair evidence before repairing code

Several diary failures were process failures, not package defects. They still changed the working validation contract.

The command `pnpm smoke:consumer` failed because no such script exists; the actual package script is `pnpm consumer:smoke`. The failure did not imply a broken consumer package. The diary records the exact correction and the successful authoritative command. Similarly, a malformed browser-evaluation expression caused `SyntaxError: Unexpected token ')'`. Replacing it with a smaller explicit traversal yielded reliable browser evidence. The browser probe was defective, not the plot.

The transform-before-summary test initially failed with `Cannot read properties of undefined (reading 'multiplier')`. The summary statistic required an explicit interval configuration, and the fixture omitted it. Adding the standard-error interval allowed the test to reach its stated target: transformed `log(e¹)` and `log(e³)` values should be averaged to `2`, rather than averaging raw values and then taking a logarithm.

Fixture mistakes should be classified before code changes. A useful sequence is:

1. Confirm that the command is defined in `package.json` and run the canonical script.
2. Confirm that the fixture satisfies the grammar and statistic preconditions unrelated to the behavior under test.
3. Confirm that a browser probe is syntactically valid and observes the intended DOM scope.
4. Only then assign failure to compiler, planner, scene, renderer, or host code.

This sequence prevents a dangerous response: weakening production validation so an incomplete fixture passes. The summary interval requirement was not incidental. It is part of the statistic’s contract, so the test had to declare it.

## A validation protocol for future grammar changes

The six tickets leave a practical protocol for new grammar features. First, define the surface union, normalized representation, diagnostic paths, and explicit non-goals. Second, decide the last stage at which the new syntax exists. HSPLOT-010 algebra disappears before planning; HSPLOT-009 coordinates appear only in late geometry; configured guides become complete plan components before scene lowering. Third, write a minimal valid fixture that reaches the intended stage. Fourth, add negative cases that prove errors, warnings, omissions, and unsupported topology are distinguished.

Then validate across boundaries. Contract tests inspect normalized grammar and canonical paths. Numeric tests use hand-calculated values and explicit comparators. Plan and scene tests inspect finite geometry and node roles. Architecture tests reject imports and branches that would make downstream stages interpret the wrong language. Packed-consumer tests prove entrypoint boundaries. Browser inspection checks dimensions, computed styles, path counts, and visible output. Finally, classify incidental tool warnings honestly.

The implementation diaries and tests provide the evidence locations:

- HSPLOT-005 `reference/01-implementation-diary.md`, `src/presentation.test.ts`, `src/presentation-golden.test.ts`, and `src/architecture.test.ts` establish complete planning and mechanical lowering.
- HSPLOT-006 `reference/01-implementation-diary.md` and `src/author.test.ts` prove pure serializable authoring and edge cases.
- HSPLOT-007 `reference/01-implementation-diary.md`, `src/pipeline/geometry.ts`, `src/scales.ts`, and compact Storybook stories document visible marks and one-point lowering.
- HSPLOT-008 `reference/01-implementation-diary.md`, `src/configured-guides-annotations.test.ts`, and `src/scale-families.test.ts` document guide compatibility and structured components.
- HSPLOT-009 `reference/01-implementation-diary.md`, `src/coordinates.ts`, and `src/coordinates.test.ts` document geometry versus typography space.
- HSPLOT-010 `reference/01-implementation-diary.md`, `src/variables.ts`, and `src/algebra.test.ts` document materialization, multiple diagnostics, and fixture discipline.

The central rule is straightforward: when failure reveals that an output is valid at one stage but wrong at another, do not patch the symptom at the lowest layer. State the missing contract, assign it to the correct stage, test the boundary, and retain every diagnostic that describes an independent consequence.
