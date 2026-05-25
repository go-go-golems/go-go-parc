---
title: DMETA PBUI Street Deli CLIM React Research Report - From Conceptual Cleanup to Concrete Target
aliases:
  - DMETA PBUI Street Deli CLIM React Research Report
  - Street Deli PBUI React Proof of Concept Report
tags:
  - article
  - dmeta
  - pbui
  - clim
  - react
  - code-generation
  - design-systems
status: active
type: article
created: 2026-05-25
repo: /home/manuel/code/wesen/go-go-golems/dmeta
---

# DMETA PBUI Street Deli CLIM React Research Report - From Conceptual Cleanup to Concrete Target

This report records the current DMETA PBUI research state after a major clarification of the architecture. The work began as a generator-first attempt to produce a Street Deli CLIM-style React application from Semantic IR, Interaction IR, PBUI lowering, and a concrete presentation profile. That work produced useful compiler infrastructure, but it also exposed a conceptual barrier: the target React architecture was not yet understood well enough to generate correctly.

The current direction is to pause the deepest generation work, separate reusable PBUI/CLIM concepts from Street Deli-specific concepts, and build a concrete hand-authored React proof of concept. The proof of concept is not a retreat from code generation. It is the step that defines a better target for future generation.

> [!summary]
> - The shared IR layers are being narrowed so global packages contain reusable concepts, while Street Deli-specific actions, representations, views, and bindings live with the example.
> - A reusable CLIM PBUI profile now holds common shell surfaces and presentation bindings, while the Street Deli PBUI profile keeps app-specific overrides.
> - A standalone Vite/React/Tailwind/RTK Query/Storybook proof of concept now exists at `proof-of-concept/deli-pbui-react` to discover the correct target architecture before regenerating it.
> - The main unresolved design area is the concrete action/command binding layer that maps Interaction IR actions into PBUI action presentations, command labels, input mappings, handlers, and view-model behavior.

## Why this report exists

The project reached a point where more generated files were not the most useful next output. The compiler had enough layers to express intent, but the target application still felt incomplete. It had a CLIM shell, generated presentation components, metadata, and stories, but it did not yet behave like a domain-specific ordering system. It did not have a convincing model for Street Deli actions, command aliases, typed action requests, handler stubs, or view-model-driven selectors.

The important research question changed from "Can we generate files?" to "What files should a correct generator produce?" That question is best answered by writing the target by hand once, with a strict separation between reusable PBUI/CLIM code and Street Deli domain code. The generator can then be adjusted to reproduce the stable parts.

This report explains the current structure so that a future reader can understand why the repository now contains both compiler passes and a hand-authored proof-of-concept package.

## Current repository anchors

The relevant repository is:

```text
/home/manuel/code/wesen/go-go-golems/dmeta
```

The most important paths are:

```text
sources/dmeta-ir/interactions/
  Shared generic Interaction IR package.

examples/street-deli-ordering/interactions/
  Street Deli interaction package that inherits the shared package and adds deli actions, representations, and elaboration rules.

sources/dmeta-ir/meta-design-systems/pbui/
  Global PBUI MetaDesignSystem package: presentation types, lowering rules, and generic PBUI React target.

sources/dmeta-ir/meta-design-systems/pbui/profiles/clim/
  Reusable CLIM PBUI profile pieces: common surfaces and presentation bindings.

examples/street-deli-ordering/meta-design-systems/pbui/
  Street Deli concrete PBUI profile: view models, style profile, local binding overrides, and app target settings.

examples/street-deli-ordering/www/clim-react/
  Existing generated concrete CLIM React app scaffold.

proof-of-concept/deli-pbui-react/
  New standalone hand-authored React proof of concept.
```

The key distinction is now visible in the directory structure: shared packages contain reusable vocabulary; examples contain application vocabulary; the proof of concept contains hand-authored target code used to discover future generation templates.

## The conceptual barrier that was blocking progress

The earlier pipeline could be summarized as:

```text
Semantic IR
  -> Interaction IR
  -> PBUI lowering
  -> concrete PBUI presentation profile
  -> React app scaffold
```

This is a reasonable compiler shape, but the final target was underdefined. The generated React app had files named like a CLIM app, but several important concepts were still placeholders:

- actions were not fully represented as typed runtime descriptors in the concrete app;
- view-model definitions were not compiled into strong TypeScript registries and selectors;
- command labels such as `PLACE-ORDER` were not mapped to Interaction IR action ids such as `submit_order` through an explicit binding layer;
- action input mappings were not described concretely;
- action handlers and result presentations were not scaffolded in a useful way;
- generic CLIM runtime code and app-specific Deli code were not separated sharply enough.

The problem was not that generation failed. The problem was that generation was being asked to produce a target that the project had not yet designed.

## What changed: from generator-first to target-first

The current strategy is target-first. That means the next source of truth for the React target is not a generator template. It is a working proof-of-concept package:

```text
proof-of-concept/deli-pbui-react
```

This package is deliberately hand-authored. It uses:

- Vite for the standalone React application;
- Storybook for reviewable widget states;
- Tailwind for fast visual iteration;
- RTK Query for an API-shaped data layer, even while using fixture data;
- a `widget.tsx` and `widget.stories.tsx` pattern for the primary review surface.

The package is small, but it encodes the architectural separation that future generation should reproduce.

```text
src/generic/clim/
  reusable CLIM/PBUI types and components

src/domain/deli/
  Street Deli domain data, actions, view models, and fixture API

src/widgets/DeliPbuiWorkbench/
  composition point where generic CLIM code meets Deli domain code
```

The proof of concept exists to answer concrete design questions before those answers are frozen into generated code.

## Shared interactions vs Street Deli interactions

One major conceptual cleanup was moving concrete interaction vocabulary out of the global interaction package.

The global package now lives at:

```text
sources/dmeta-ir/interactions/
```

It keeps only generic interaction vocabulary:

```text
Actions:
  Action
  inspect_subject
  copy_reference
  select_subject
  filter_by_state

Representations:
  Representation
  object_reference
  compact_reference
  state_indicator
  inspection_entrypoint

Rules:
  identifiable_labelable_to_compact_reference
  inspectable_to_inspection
  stateful_to_state_indicator
```

Street Deli now has its own inherited interaction package:

```text
examples/street-deli-ordering/interactions/
  00-index.yaml
  actions.yaml
  representations.yaml
  elaboration-rules.yaml
```

The local package declares:

```yaml
inherits:
  interactions_root: ../../sources/dmeta-ir
```

The loader merges the shared package and local package into one effective interaction package. The merge rule is intentionally simple:

```text
base actions + local actions -> effective actions
base representations + local representations -> effective representations
base rules followed by local rules -> effective elaboration rules
```

Local definitions with the same id override base definitions. Rule lists append so that generic obligations and domain-specific obligations can both be emitted.

Street Deli now owns application actions such as:

```text
select_menu_item
filter_by_dietary
remove_part
undo_remove_part
add_part
change_config
apply_substitution
reject_substitution
see_alternatives
add_to_order
remove_cart_item
submit_order
return_to_menu
```

It also owns application representations such as:

```text
composition_summary
composition_breakdown
ingredient_composition_row
role_label
dietary_summary
configuration_summary
substitution_candidate
substitution_price_delta
order_lifecycle_progress
cart_summary
```

This split matters because it stops the global Interaction IR from pretending that every domain has menu items, carts, dietary substitutions, and order submission. The shared package now provides a smaller vocabulary that other examples can inherit without inheriting Street Deli assumptions.

## Reusable CLIM PBUI profile vs Street Deli PBUI profile

A second cleanup separated common CLIM surface/binding concepts from the Street Deli app profile.

Reusable CLIM profile files now live under:

```text
sources/dmeta-ir/meta-design-systems/pbui/profiles/clim/
  surfaces.yaml
  presentation-bindings.yaml
```

These files describe reusable CLIM structure:

- shell;
- header;
- active view area;
- command line;
- context menu;
- confirmation prompt;
- generic presentation reference line;
- generic action presentation;
- action chooser;
- inspector panel;
- lifecycle status block;
- generic composition presentation block.

Street Deli keeps app-specific PBUI profile data under:

```text
examples/street-deli-ordering/meta-design-systems/pbui/
  presentation-system.yaml
  style-profile.yaml
  surfaces.yaml
  view-models.yaml
  presentation-bindings.yaml
  targets/react-app.yaml
```

The Street Deli `presentation-system.yaml` now references the reusable CLIM profile:

```yaml
inherits:
  meta_design_system: pbui
  pbui_root: ../../../sources/dmeta-ir/meta-design-systems/pbui
  surfaces: ../../../../sources/dmeta-ir/meta-design-systems/pbui/profiles/clim/surfaces.yaml
  presentation_bindings: ../../../../sources/dmeta-ir/meta-design-systems/pbui/profiles/clim/presentation-bindings.yaml
```

The profile loader merges inherited surfaces and inherited presentation bindings with local overrides. This makes the current structure explicit:

```text
Reusable CLIM profile
  common shell and presentation-system vocabulary

Street Deli PBUI profile
  style, views, Deli composition overrides, app target settings
```

The local Street Deli `presentation-bindings.yaml` now keeps the Deli-specific composition binding details: menu item header, ingredient rows, substitutions, role labels, cart items, and local class names. Those details should not live in the reusable CLIM profile.

## The proof-of-concept React package

The new package is:

```text
proof-of-concept/deli-pbui-react
```

It is standalone. It has its own `package.json`, Vite config, Storybook config, Tailwind/PostCSS config, TypeScript config, and app entrypoint.

The package currently builds and its Storybook builds:

```bash
cd proof-of-concept/deli-pbui-react
npm run build
npm run build-storybook
```

Storybook emits the usual large chunk warning, but the build completes successfully.

### Package structure

```text
proof-of-concept/deli-pbui-react/
  src/
    generic/
      clim/
        types.ts
        components.tsx
    domain/
      deli/
        types.ts
        fixtures.ts
        actions.ts
        viewModels.ts
        deliApi.ts
    app/
      store.ts
    widgets/
      DeliPbuiWorkbench/
        widget.tsx
        widget.stories.tsx
```

The structure is the main result. It separates three concerns that were blurred in the generated scaffold:

1. **Generic CLIM/PBUI runtime code** belongs in `src/generic/clim`.
2. **Street Deli domain code** belongs in `src/domain/deli`.
3. **Composed reviewable UI** belongs in `src/widgets/DeliPbuiWorkbench`.

## Generic CLIM/PBUI target shape

The generic CLIM layer defines a minimal reusable runtime vocabulary:

```ts
export type InteractionMode = 'normal' | 'select' | 'confirm';

export interface PresentationRef<TType extends string = string> {
  type: TType;
  id: string;
  label: string;
  capabilities: string[];
  metadata?: Record<string, string | number | string[]>;
}

export interface ActionDescriptor<TAction extends string = string> {
  id: TAction;
  label: string;
  description: string;
  inputTypes: Record<string, 'SemanticRef' | 'string' | 'number' | 'boolean'>;
  mutatesBackend: boolean;
  requiresConfirmation: boolean;
}

export interface ActionPresentation<TAction extends string = string> {
  descriptor: ActionDescriptor<TAction>;
  disabledReason?: string;
  subject?: PresentationRef;
}
```

These types are not Street Deli-specific. They are candidate reusable runtime types for a future PBUI React CLIM package.

The generic component layer currently includes:

```text
ClimShell
PresentationRefLine
ActionPresentationInline
ActionHintBar
```

This is not enough for the final runtime, but it is enough to establish the generic/component boundary. The next generic additions should be:

- command parser;
- action request builder;
- compatible action selector;
- normal/select/confirm state machine;
- context menu component;
- confirmation prompt component;
- Storybook shell.

## Street Deli domain target shape

The Street Deli domain layer is where application concepts live.

```text
src/domain/deli/types.ts
src/domain/deli/fixtures.ts
src/domain/deli/actions.ts
src/domain/deli/viewModels.ts
src/domain/deli/deliApi.ts
```

The domain action registry is especially important:

```ts
export const deliActionDescriptors: Record<DeliActionId, ActionDescriptor<DeliActionId>> = {
  select_menu_item: {...},
  remove_part: {...},
  apply_substitution: {...},
  add_to_order: {...},
  submit_order: {...},
  return_to_menu: {...},
};
```

This shape is missing from the generated CLIM app. The compiler already knows about actions in YAML, but the concrete app needs a typed runtime registry that React code can import, inspect, render, and use to build action requests.

The domain view-model registry is also important:

```ts
export const deliViewModels = {
  menu: {
    id: 'menu',
    modeLabel: 'MENU',
    primaryPresentations: ['pbui.presentation_ref', 'pbui.action_chooser', 'pbui.action_presentation'],
    defaultActions: ['select_menu_item', 'return_to_menu'],
  },
  detail: {...},
  cart: {...},
};
```

This is the TypeScript shape that `examples/street-deli-ordering/meta-design-systems/pbui/view-models.yaml` should eventually generate. The proof of concept writes it by hand first so the target can be refined without changing generators repeatedly.

RTK Query is introduced through a fixture-backed API:

```ts
export const deliApi = createApi({
  reducerPath: 'deliApi',
  baseQuery: fakeBaseQuery(),
  endpoints: (builder) => ({
    getMenu: builder.query<MenuItem[], void>({
      queryFn: () => ({ data: menuItems }),
    }),
  }),
});
```

This means the app is API-shaped from the beginning. The data source can change later without rewriting the presentation layer.

## The widget as a generation target sketch

The main widget is:

```text
src/widgets/DeliPbuiWorkbench/widget.tsx
```

It composes the generic CLIM layer and the Street Deli domain layer. Its key function projects a Deli domain object into a generic presentation object:

```ts
function menuItemPresentation(item: MenuItem): PresentationRef<'MenuItem'> {
  return {
    type: 'MenuItem',
    id: item.id,
    label: `${item.name} $${item.price.toFixed(2)}`,
    capabilities: ['labelable', 'composable', 'substitutable'],
    metadata: { category: item.category, tags: item.tags },
  };
}
```

This is a central pattern. Domain data should not be rendered directly by generic CLIM components. Domain data is first projected into presentation objects. Generic CLIM components render those presentation objects.

The future compiler should probably generate or scaffold this kind of projection function from Semantic IR capabilities, PBUI presentation bindings, and app-specific view-model rules.

## The missing action binding layer

The most important remaining design gap is action binding. The project now has:

```text
Interaction IR action definitions
Street Deli action descriptors in the proof of concept
Street Deli view models
PBUI action presentation concepts
```

It still needs a YAML layer that connects these concepts to application commands and handlers.

A future file should probably live at:

```text
examples/street-deli-ordering/meta-design-systems/pbui/action-bindings.yaml
```

A binding should say:

```yaml
PLACE-ORDER:
  action: submit_order
  label: PLACE-ORDER
  views: [cart]
  presentation_type: pbui.action_presentation
  input_mapping:
    cart_ref: current_cart
  confirmation:
    surface: confirm_prompt
  handler: order.submit
```

This layer is not the same as Interaction IR. Interaction IR says what `submit_order` means. The action binding says how the Street Deli PBUI application exposes that action in a view, what command label users see, where inputs come from, whether confirmation is shown, and which handler implements the behavior.

Without this layer, the compiler can list actions but cannot produce a convincing app.

## Updated compiler direction

The current direction is no longer to generate the final CLIM app directly from broad abstract IR. The next compiler iteration should use the proof-of-concept target as evidence.

The target chain should become:

```text
Shared Semantic IR
  domain object vocabulary and capabilities

Shared generic Interaction IR
  generic object reference, inspection, selection, state actions

Street Deli interaction package
  Deli actions, Deli representations, Deli elaboration rules

Global PBUI MetaDesignSystem
  abstract presentation-system concepts

Reusable CLIM PBUI profile
  shell surfaces and common presentation bindings

Street Deli PBUI profile
  views, style, composition binding overrides, action bindings

Hand-proven React target shape
  generic CLIM runtime package + Deli domain registries + widget stories

Future generation
  reproduce the stable target shape from the layers above
```

The proof of concept should be treated as a research target. When a pattern works there, it can move upward into one of three places:

1. reusable CLIM React package;
2. Street Deli-specific generated domain files;
3. compiler templates and IR schemas.

## What has been clarified

Several conceptual barriers have been cleared.

### Shared does not mean first-used

A concept should not live in `sources/dmeta-ir` just because Street Deli was the first app to use it. Shared packages should contain concepts that are expected to apply across domains. Deli-specific concepts now live with the Deli example.

### PBUI is not React

PBUI describes presentation-system obligations. React is one target that can render them. The reusable CLIM profile describes a concrete presentation-system idiom, but the proof-of-concept React code is still a target implementation.

### A view model is not a component

`view-models.yaml` should not merely name generated React views. It should describe mode labels, primary presentation families, default actions, command echoes, and the way a view organizes presentation-system state. The proof of concept starts to show the TypeScript registry shape this YAML should generate.

### An action is not a command label

`submit_order` is an action id. `PLACE-ORDER` is a command label. A PBUI application needs a binding layer between them. That layer should also define input mapping, confirmation behavior, view availability, and handler identity.

### Generation should follow a known target

The current React proof of concept is the target discovery surface. Once it proves the right boundaries, generation can resume with less guesswork.

## Current validation status

The following checks passed after the interaction split and proof-of-concept setup:

```bash
go test ./pkg/dmeta/... ./cmd/dmeta -count=1

go run ./cmd/dmeta validate-interactions \
  --root ./sources/dmeta-ir \
  --include-info \
  --output table

go run ./cmd/dmeta validate-interactions \
  --root ./examples/street-deli-ordering \
  --include-info \
  --output table

go run ./cmd/dmeta validate-pbui \
  --pbui-root ./sources/dmeta-ir/meta-design-systems/pbui \
  --interactions-root ./examples/street-deli-ordering \
  --include-info \
  --output table

go run ./cmd/dmeta validate-pbui-profile \
  --profile-root ./examples/street-deli-ordering/meta-design-systems/pbui \
  --pbui-root ./sources/dmeta-ir/meta-design-systems/pbui \
  --interactions-root ./examples/street-deli-ordering \
  --include-info \
  --output table

go run ./cmd/dmeta plan-pbui-react-app \
  --root ./examples/street-deli-ordering \
  --interactions-root ./examples/street-deli-ordering \
  --pbui-root ./sources/dmeta-ir/meta-design-systems/pbui \
  --profile-root ./examples/street-deli-ordering/meta-design-systems/pbui \
  --output-dir ./examples/street-deli-ordering/www/clim-react \
  --output table

cd proof-of-concept/deli-pbui-react && npm run build && npm run build-storybook
```

Storybook produced the standard Vite large chunk warning. The build completed successfully.

## Near-term next steps

### 1. Add action bindings

Create:

```text
examples/street-deli-ordering/meta-design-systems/pbui/action-bindings.yaml
```

This should map command labels to Interaction IR action ids, input mappings, handler ids, confirmation behavior, and view availability.

### 2. Extend the proof-of-concept state machine

Add generic CLIM state transitions:

```text
normal -> select
select -> normal
normal -> confirm
confirm -> normal
```

Use Street Deli actions to test the transitions.

### 3. Add Deli composition and cart state

The proof of concept needs more than menu browsing. Add:

- selected menu item;
- composition draft;
- removed ingredients;
- substitution candidates;
- cart items;
- order submission confirmation state.

### 4. Add more Storybook states

Storybook should show:

- menu mode;
- detail mode;
- remove ingredient select mode;
- substitution candidate mode;
- cart mode;
- confirmation prompt;
- disabled action state;
- inspector/help state.

### 5. Convert stable proof-of-concept shapes back into generation

Once stable, generate:

```text
src/domain/deli/generated/objectTypes.ts
src/domain/deli/generated/actionDescriptors.ts
src/domain/deli/generated/viewModels.ts
src/domain/deli/generated/presentationBindings.ts
src/domain/deli/generated/commandBindings.ts
```

This should happen after the hand-authored version proves the shape.

## Working rule

The current working rule is:

> Do not generate a target shape that has not first been proven in concrete React code.

This rule does not weaken the compiler plan. It makes the compiler plan more precise. The proof-of-concept package should become the evidence base for the next generation pass.

## Related local docs

The most relevant ticket documents are:

```text
ttmp/2026/05/25/DMETA-DELI-PBUI-POC--street-deli-pbui-react-proof-of-concept/design-doc/01-street-deli-pbui-react-proof-of-concept-architecture-and-implementation-guide.md

ttmp/2026/05/25/DMETA-DELI-PBUI-POC--street-deli-pbui-react-proof-of-concept/reference/01-diary.md

ttmp/2026/05/24/DMETA-GENERATED-METADATA--generated-file-metadata-and-promotion-guidance/design-doc/01-generated-file-metadata-and-promotion-guidance-implementation-guide.md

ttmp/2026/05/24/DMETA-FOLDED-METADATA--fold-generated-metadata-into-shared-package-metadata/design-doc/01-folded-generated-metadata-architecture-and-implementation-guide.md
```

The report should be read with the proof-of-concept package open. The report explains why the package exists; the package shows the target structure that future DMETA code generation should learn to produce.
