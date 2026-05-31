---
title: "DMETA Design System Compiler Pipeline — How We Do It"
aliases:
  - DMETA compiler pipeline
  - DMETA layered IR
  - DMETA Interaction IR
  - DMETA MetaDesignSystem
  - design system compiler
  - DMETA code generation
tags: [knowledge-base, tribal, dmeta, design-system, compiler, code-generation, react, ir]
status: active
type: knowledge-base
created: 2026-05-31
repos:
  - /home/manuel/code/wesen/go-go-golems/dmeta
---

# DMETA Design System Compiler Pipeline — How We Do It

> [!summary]
> DMETA is a design system compiler that transforms semantic design intent into generated React components through layered intermediate representations: `Semantic IR → Interaction IR → Web MetaDesignSystem → React target`. Each layer is a separate Go package with its own types, validation, and lowering pass. Widgets belong to the target layer, not the universal layer. Generated scaffolds carry semantic context as guidance (reflection-first), not as mandatory layout instructions. The visual source of truth is the imported original design; after each parity pass, the settled shape is backfilled into IR.

## The pattern

DMETA is organized as a compiler pipeline. Each layer answers a different question and has a different consumer. The layers are ordered from most abstract (closest to human intent) to most concrete (closest to running code).

```
Semantic IR → Interaction IR → Web MetaDesignSystem → React target

Semantic IR:     archetypes, capabilities, projections, domain examples
Interaction IR:  actions, representations, semantic selectors, elaboration rules (modality-neutral)
Web MDS:         web widget templates, slots, visual states, layout, event bindings, lowering rules
React target:    component names, props, file plans, stories, CSS modules, metadata sidecars
```

The CLI commands follow the same pipeline:

```bash
dmeta validate-ir           # validate semantic IR
dmeta plan-instance         # select widgets for a concrete app
dmeta elaborate-interactions # lower semantic IR → interaction IR
dmeta lower-web             # lower interaction IR → web MDS
dmeta plan-scaffold --target react   # plan React file generation
dmeta scaffold-react        # generate React scaffolds
```

### Semantic IR: archetypes and capabilities

Archetypes are reusable functional roles that appear across many applications. They form an explicit inheritance tree rooted at the abstract `Archetype` class with `extends: []`. Capabilities declare what affordances an object can have. Both archetypes and capabilities use semantic inheritance:

```yaml
Composition:
  extends: [Archetype]    # abstract root
ProductComposition:
  extends: [Composition]  # abstract: something assembled into a sellable product
MenuItem:
  extends: [ProductSpec, ProductComposition]  # concrete: a sellable menu item
```

The rule is strict: `Archetype` and `Capability` are explicit abstract roots with `extends: []`. Non-root archetypes must declare parents. Stale flat definitions fail validation.

### Interaction IR: modality-neutral actions and representations

The Interaction IR sits between semantics and concrete design systems. It defines **Actions** (what the user can do) and **Representations** (how values can appear) grounded in intent, semantic selectors, projections, constraints, and natural-language rationale. It does not mention cards, rows, buttons, CSS, Storybook, or React.

The key insight: the word `presentation` previously did too much work — it named a semantic display intent, a design-system rendering choice, and a concrete UI artifact. The Interaction IR split resolves this by making `Representation` the semantic concept and `Web Widget` the rendering concept.

### Web MetaDesignSystem: owns the mapping to web widgets

The Web MetaDesignSystem owns Web widget templates, lowering rules, slots, visual states, layout concepts, event bindings, and Web lowering rules. React is a target below Web, not the meaning of DMETA widgets.

### React target: concrete code generation

The React target produces component names, props, file plans, stories, CSS modules, metadata sidecars, and write behavior. Generated files use `.generated.*` naming and are separate from promoted maintained components.

### File lifecycle

The generator enforces three file lifecycle modes:

| Mode | Behavior | Use for |
|---|---|---|
| **Regenerate-only** | Overwritten on each generation run. | Prop types, generated widget scaffolds, manifest metadata. |
| **Scaffold-once** | Protected after first generation. Promoted components. | Hand-owned React components that the developer customizes. |
| **Sidecar** | Can be regenerated for merge review. | JSON metadata sidecars, CSS modules. |

### Reflection-first scaffold philosophy

Generated widgets carry semantic context as guidance, not as mandatory layout instructions. A scaffold explains *why* a widget was selected and *which projections may matter*, but the implementor decides the final prop shape and markup. This is the "reflection-first" approach: the scaffold reflects the semantic decision, and the promoted component reflects the implementor's judgment.

## Why we do it this way

**Layered IRs prevent domain leakage.** Without the Interaction IR, semantic archetypes directly decided that something was a card, row, badge, or button. That put `MenuItem` into the base factory — domain leakage. The Interaction IR keeps semantics modality-neutral: a `MenuItem` is a `ProductComposition` with certain capabilities; how it renders is a target-specific decision.

**The hard cutover was the right call.** The pre-refactor system had `Semantic IR → generic widget templates → React-ish scaffolds`. The old `scaffold-instance` command and generic widget renderer mixed concerns across layers. Instead of maintaining backward compatibility with shims, the refactor removed them entirely. When the model is wrong, cut rather than shim.

**Visual source of truth is the imported original.** After each parity pass, the settled shape is backfilled into IR. The accelerated promotion pass had made reasonable product-oriented choices (extra buttons, badges, merchandising chips), but those were not the imported visual baseline. The original design was simpler. Making the imported original the visual source of truth keeps the IR honest.

**File lifecycle enforcement prevents accidental overwrites.** Without it, a developer who spent hours customizing a promoted component could lose work to an accidental regeneration. The three-mode lifecycle makes the contract explicit at the file level.

Alternatives considered and rejected:
- **Direct code generation from semantic IR.** Faster to build, but conflates "what this is about" with "how it renders." Every new rendering target requires changes to the semantic model.
- **Single-stage IR.** Merging semantics + interaction + rendering into one layer. Works for small prototypes, but makes the system unable to answer "what can this object do?" without also answering "what does it look like?"

## Evidence

| Report                                                                                                       | Date       | Contribution                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------ | ---------- | ---------------------------------------------------------------------------------------------------------------------------- |
| [[ARTICLE - DMETA Design System Factory - From Semantic Schemas to Generated React Widgets]]                 | 2026-05-23 | Canonical description: nine-layer model, archetypes, capabilities, widget templates, scaffold generation, promotion workflow |
| [[ARTICLE - DMETA Semantic Inheritance - From Flat Tags to Deli Ordering]]                                   | 2026-05-23 | Explicit abstract roots, `extends: []` validation, Street Deli domain mapping                                                |
| [[ARTICLE - DMETA as a Design System Compiler - Layered IRs and MetaDesignSystems]]                          | 2026-05-24 | Proposal for Interaction IR, MetaDesignSystem concept, modality-neutral actions/representations                              |
| [[ARTICLE - DMETA Compiler Refactor - Hard Cut to Interaction IR Web MetaDesignSystem and React Target]]     | 2026-05-24 | Implementation: removed old scaffold-instance, new pipeline `validate → plan → elaborate → lower → scaffold`                 |
| [[ARTICLE - DMETA PBUI Street Deli CLIM React Research Report - From Conceptual Cleanup to Concrete Target]] | 2026-05-25 | CLIM PBUI profile pattern: reusable shell surfaces vs. app-specific overrides, action/command binding layer                  |
| [[ARTICLE - TTC DMETA React Workflow - Semantic IR to Storybook Garden Assistant]]                           | 2026-05-27 | File lifecycle enforcement, CSS token lowering path, generated vs. promoted component workflow                               |
| [[ARTICLE - TTC DMETA Visual Parity - Preserving IR and Codegen While Matching the Original Design]]         | 2026-05-28 | Visual source of truth = imported original, IR simplification, backfilling after parity passes                               |
| [[ARTICLE - Building a Reusable CLIM React Package]]                                                         | 2026-05-26 | CLIM interaction modes as discriminated union, semantic intents driving visual rendering, Tailwind npm packaging             |
| [[ARTICLE - Typography Debug Palette - Design System, Live Overrides, and Modular Scale]]                    | 2026-05-28 | CSS token validation from design-language IR, debug palette for live overrides                                               |

## Working rules

1. **When the model is wrong, cut rather than shim.** The hard cutover removed old `scaffold-instance` entirely instead of maintaining backward compatibility. Compatibility aliases should not be added unless there is a concrete external user requirement.

2. **Widgets belong to targets, not the universal layer.** Universal DMETA stops at semantic facts and modality-neutral interaction obligations. Semantic IR must not define Web widgets, React components, CSS, Storybook, or visual states. Interaction IR must remain modality-neutral. Web MetaDesignSystem owns the rendering mapping.

3. **Reflection-first scaffolds carry context, not commands.** A scaffold explains *why* a widget was selected; the implementor decides the final shape. Generated widgets carry semantic provenance as metadata, not as mandatory layout instructions.

4. **File lifecycle must be enforced.** Regenerate-only files are overwritten; scaffold-once files are protected; sidecar files can be regenerated for merge review. The generator must never overwrite a promoted component.

5. **Visual source of truth is the imported original.** After each parity pass, the settled promoted shape is backfilled into DMETA IR and regenerated into `.generated.*` files. The accelerated promotion variants may be useful later but are not the baseline.

6. **`Archetype` and `Capability` are explicit abstract roots.** Non-root archetypes/capabilities must declare parents via `extends`. Stale flat definitions fail validation.

7. **The word `presentation` must be disambiguated.** It names a semantic display intent (Representation in Interaction IR), a design-system rendering choice (Web Widget in MetaDesignSystem), and a concrete UI artifact (React Component). Never use `presentation` without specifying which layer you mean.

8. **Generated scaffolds must be promoted before customization.** Copy the scaffold into a hand-owned component, then customize. Never edit a `.generated.*` file directly — it will be overwritten.

9. **CSS tokens should be validated from design-language IR.** Design-language IR should produce lint rules, not just visual guidelines. Tokens are defined in YAML, lowered into CSS variables, and enforced by generated CSS modules.

10. **CLIM PBUI profile pattern: separate common shell from app-specific overrides.** Common shell surfaces (shell, command palette, status bar) belong in a reusable CLIM profile. App-specific action bindings and presentation overrides belong in the app profile. Never mix them in one package.

## Gotchas

1. **The word `presentation` does too much work.** It names a semantic display intent, a design-system rendering choice, and a concrete UI artifact. The Interaction IR split resolves this by renaming to `Representation` (semantic) and `Web Widget` (rendering). If you find yourself saying "presentation" without qualifying the layer, stop and disambiguate.

2. **Generated scaffolds are not final components.** They must be promoted — copying the scaffold into a hand-owned component and then customizing it. Editing `.generated.*` files directly will lose work on the next generation run.

3. **CSS token validation is still incomplete.** Design-language IR should produce lint rules, not just visual guidelines. The current system generates tokenized CSS modules but does not yet enforce them with a linter.

4. **Tailwind v4 does not scan `node_modules` by default.** When extracting a reusable CLIM React package into an npm package, consumers must add `@source` directives. Without them, the generated CSS will be silently incomplete — classes present in the package but absent in the final CSS output.

5. **CLIM interaction modes as discriminated union.** CLIM has three modes (normal, select, confirm). Representing these as a discriminated union eliminates impossible states at the type level. Using three separate booleans allows impossible states (normal=true, select=true, confirm=true).

6. **Semantic intents drive visual rendering, not per-component logic.** Every action carries intents (navigate, mutate, dangerous, confirm) derived from its specification. These intents drive visual rendering, confirmation gates, and context-sensitive hints. If you find yourself writing per-component rendering logic for action styling, you're duplicating what the intent system should handle.

7. **The action/command binding layer is still an open design area.** The concrete mapping from Interaction IR actions to PBUI action presentations, command labels, input mappings, handlers, and view-model behavior is not yet fully specified. Future work should address this before generating more complex applications.

8. **IR simplification is a real tension.** The TTC Visual Parity work deliberately simplified IR: TypeScript source blocks define component contracts, CSS source blocks define style baselines, YAML carries metadata and intent. There is pressure to put more into IR (layout hints, responsive behavior, animation specs) which would make the IR harder to maintain. Keep IR minimal and let promoted components carry the details.

## Related KB entries

- [[Tribal/dsl-normalized-config-compiled-plan]] — The DSL→Normalized Config→Compiled Plan pattern. DMETA is a concrete instance with four layers instead of three. The Factory freezes module policy (like a compiled plan), and each lowering pass is a compilation step.
- [[Tribal/goja-runtime-ownership-and-context-propagation]] — The goja runtime substrate is used by the DMETA xgoja binaries when generating and evaluating JavaScript-bound design system components.
