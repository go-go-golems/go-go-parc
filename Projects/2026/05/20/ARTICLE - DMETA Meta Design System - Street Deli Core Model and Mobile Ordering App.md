---
title: "DMETA Meta Design System: Deriving a Core Model and Mobile Ordering App for a Street Deli"
aliases:
  - DMETA Street Deli Deep Dive
  - Intelligent Ingredient Replacement Design System
tags:
  - article
  - dmeta
  - design-system
  - dsl
  - presentation-based-ui
  - food-ordering
  - intelligent-replacement
  - mobile
status: active
type: article
created: 2026-05-20
repo: /home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta
---

# DMETA Meta Design System: Deriving a Core Model and Mobile Ordering App for a Street Deli

This article documents the derivation of a meta design system from an existing abstract design-system factory (DMETA v0) down to a concrete mobile ordering app for a street deli. The work splits into two connected parts: first, extending the abstract core model with domain-specific archetypes and capabilities needed for intelligent ingredient replacement; second, deriving a mobile-first design language and widget inventory from that model, then building a working prototype that proves the replacement engine works in practice.

The target audience is someone who wants to understand how a semantic model drives both visual design and implementation choices — not as abstract theory, but as a concrete, reviewable path from archetype definitions to working CSS.

> [!summary]
> - The core model introduces **ingredient roles** as a first-class concept: the replacement engine reasons about why an ingredient exists in a dish (richness, protein, structural), not what category of food it belongs to. "No cheese → avocado" works because both provide richness.
> - The design language derives directly from the model: role colors, substitution badge styles, and dietary flag placement all trace back to capability definitions in the YAML source.
> - The prototype proves that 14 ingredient roles, 4 new capabilities, and 2 new archetypes are sufficient to build a working intelligent replacement system for an 11-item American deli menu.

## Why this note exists

DMETA v0 is a design-system factory built for dense operational monitoring interfaces — agent workflow dashboards, retail logistics pipelines, sensor monitoring consoles. The deli ordering domain is none of those things. It is mobile, touch-first, composition-centric, and food-safety-aware. The purpose of this article is to show how the factory's abstract vocabulary (archetypes, capabilities, presentations, actions) adapts to a domain that has fundamentally different interaction patterns, and to record every design decision that connects the model to the final UI.

## Part 1: Deriving the Core Model

### The base model and its vocabulary

DMETA v0 defines a set of reusable semantic building blocks:

- **Archetypes** are operational roles that recur across domains: Actor, WorkItem, Event, Resource, Relation, Metric, TimelineSpan, ActionSpec, ActionInvocation, Annotation.
- **Capabilities** are cross-cutting affordances that attach to archetypes: identifiable, labelable, stateful, temporal, inspectable, relatable, actionable, streamable, append_only, measurable, aggregatable, schedulable, executable, spatial, parameterized.
- **Presentations** are display contracts: compact_ref, status_badge, dense_row, summary_card, detail_panel, and so on.
- **Actions** are typed operations: inspect, copy_reference, filter_by_value, filter_by_state, open_related.

This vocabulary was designed for dense operational consoles where keyboard navigation, dense tables, and stream monitoring are the primary interactions. A mobile deli ordering app has none of those patterns. The question was whether the vocabulary could be extended without breaking its internal consistency.

### Mapping the deli domain

The first task was mapping concrete deli concepts to existing archetypes. Some mappings were immediate:

| Deli concept | Base archetype | Rationale |
|---|---|---|
| Customer | Actor | Places orders, has a dietary profile |
| Order | WorkItem + TimelineSpan | Moves through a preparation lifecycle |
| OrderItem | WorkItem + Composition | A customized line item |
| PrepEvent | Event | Append-only status observation |
| Station | Actor + Resource | Has identity, status, location |

These five mappings reuse existing archetypes directly. No new concepts are needed for customers, orders, events, or stations — they behave like the same operational subjects the base model already describes.

Three concepts did not map cleanly: MenuItem, Ingredient, and the substitution relationship between ingredients. The base model has no mechanism for describing a thing that is assembled from replaceable parts, and it has no mechanism for describing replacement rules.

### The Composition archetype

A menu item is not just a product or a resource. It is an assemblage of parts that serve functional roles. A BLT has structural parts (bread), protein parts (bacon), crunch parts (lettuce), acidity parts (tomato), richness parts (mayo), and umami parts (bacon again). Removing bacon does not just delete an ingredient — it creates unfilled roles in the composition.

This is why `Composition` is an archetype, not a capability. A Composition is a first-class semantic subject: it has identity, it has a parts list with role assignments, it has integrity constraints (required roles vs optional roles), and it has its own set of presentations (composition_card, composition_detail, ingredient_list).

The key design decision is that the composition tracks **roles**, not food categories. Cheese and avocado belong to different food categories (dairy vs fruit), but they share the "richness" role. This is what makes the replacement engine work: it matches on role overlap, not on category similarity.

### The Substitution archetype

A substitution rule is not a simple 1:1 swap. "No cheese" can map to avocado (richness, creaminess, freshness), nutritional yeast (umami, sharpness), or hummus (richness, moisture, umami) — each candidate fills different subsets of the removed ingredient's roles, with different dietary compatibility, different allergen profiles, different flavor fit, and different price impact.

The `Substitution` archetype carries enough metadata for the replacement engine to reason about:

- `replaces`: which ingredient is being removed
- `replacement_candidates`: ranked list of alternatives
- `role_preservation`: which roles the replacement fills
- `dietary_compatibility`: which dietary constraints the replacement satisfies
- `allergen_flags`: allergen differences between original and replacement
- `flavor_fit`: qualitative flavor compatibility assessment
- `price_delta_cents`: cost impact
- `auto_suggest`: whether the system proactively offers this substitution

The `auto_suggest` flag is the boundary between intelligent assistance and upselling. If the replacement engine suggested the most expensive option by default, it would be perceived as a sales tactic. The flag ensures that auto-suggestions are based on role preservation quality, not revenue.

### The composable capability

The `composable` capability defines what it means for a subject to be assembled from parts with functional roles. Its projections are:

```yaml
composable:
  projections:
    parts:
      type: list
      required: true
      description: List of ingredient/part references with role assignments.
    required_roles:
      type: list
      required: false
      description: Roles that must be filled for the composition to be valid.
    optional_roles:
      type: list
      required: false
      description: Roles that enhance but are not required.
```

The `required_roles` projection is what enables the UI to warn when a removal breaks composition integrity. A sandwich without a structural part (bread) is broken; a sandwich without a crunch part (lettuce) is diminished but valid. The replacement engine uses this distinction to decide whether a substitution is a suggestion or a necessity.

### The substitutable capability

The `substitutable` capability defines what it means for a part to be replaceable. Its projections encode the replacement engine's reasoning:

```yaml
substitutable:
  projections:
    replaces: string          # ingredient being replaced
    replacement_candidates: list  # ranked alternatives
    role_preservation: list   # roles the replacement must fill
    dietary_compatibility: list  # dietary constraints satisfied
    allergen_flags: list      # allergen differences
    flavor_fit: string        # exact | similar | complementary | creative
    price_delta_cents: integer  # cost impact
    auto_suggest: boolean     # proactive vs on-demand
```

Each projection has a consumer. `replaces` is consumed by the UI to label the removal ("No cheese"). `replacement_candidates` is consumed by the replacement engine to rank options. `role_preservation` is consumed by the composition integrity checker. `dietary_compatibility` is consumed by the dietary filter. `allergen_flags` is consumed by the allergen warning presenter. `flavor_fit` is consumed by the substitution detail sheet. `price_delta_cents` is consumed by the price display. `auto_suggest` is consumed by the substitution badge renderer.

If a field has no consumer, it should not be in the YAML. This is the DMETA consumer test: every field must answer at least one of "which generator reads this?", "which validator checks this?", "which runtime registry uses this?", "which lint rule depends on this?", or "which presentation consumes this?".

### The configurable and dietary capabilities

Two additional capabilities handle aspects of the ordering flow that are distinct from substitution:

`configurable` covers scalar or categorical options beyond composition — size (half, whole), spice level (mild, medium, hot, extra hot), temperature (hot, cold), toast level, and so on. These modify the item without changing its ingredient list, and the UI must present them separately from the ingredient customization surface.

`dietary` carries dietary constraint tags and allergen metadata. This capability is the safety layer: it filters substitutions, displays dietary badges on menu items, and triggers allergen warnings when a substitution introduces a new allergen. In a food ordering context, hiding dietary information behind interactions is a safety risk, not just a UX choice. The `dietary` capability and its associated presentations enforce visibility at the design-system level.

### Ingredient roles as a first-class logical type

The core model's `core-model.yaml` defines `ingredient_role` as a first-class logical type with 14 values:

| Role | What it means | Example ingredient |
|---|---|---|
| structural | Foundation that holds the composition together | Bread, wrap, roll |
| protein | Primary protein source | Bacon, turkey, tofu, egg |
| richness | Creamy, fatty, or satiating contribution | Cheese, avocado, mayo |
| moisture | Wetness or lubrication | Mayo, sauce, dressing |
| acidity | Sour or tangy contribution | Pickle, mustard, vinegar |
| heat | Spicy or pungent contribution | Hot sauce, jalapeño |
| crunch | Crisp or textural contrast | Lettuce, onion, chips |
| umami | Savory depth | Bacon, cheese, mushrooms |
| sweetness | Sugary or sweet contribution | Honey, fruit |
| bitterness | Bitter or earthy depth | Arugula, radicchio |
| freshness | Light, bright, clean flavor | Lettuce, tomato, herbs |
| binding | Holds other ingredients together | Egg, mayo, cheese melt |
| garnish | Finishing touch or visual accent | Herbs, sprouts, seasoning |
| base | Bulk carrier or starchy foundation | Rice, potatoes, greens |

The number 14 is not arbitrary. Fewer than 10 and the replacement engine cannot distinguish between cheese (richness) and mayo (moisture), which is the entire point. More than 20 and the system becomes unwieldy for both authors and users. 14 covers the functional spectrum of sandwich, bowl, and platter construction without over-specifying.

### Domain example: the pressure test

The `street-deli-ordering.yaml` file maps 8 concrete domain types and provides 4 complete replacement scenarios. Each scenario shows the full reasoning chain:

**No cheese → avocado** (dairy-free or preference). Cheese provides richness, creaminess, and umami. Removing it creates three unfilled roles. Avocado fills richness and creaminess (similar flavor fit), is dairy-free and vegan-compatible, and adds freshness as a bonus role. Nutritional yeast fills umami and sharpness (complementary flavor fit), is also dairy-free, but does not provide creaminess — so it is a weaker role match. Hummus fills richness and moisture, adds umami, but may contain sesame — an allergen flag that the UI must surface.

**No bacon → smoked tofu** (vegan or preference). Bacon provides protein, umami, heat, and crunch. Smoked tofu fills protein and umami (similar flavor fit), contains soy (allergen flag), and costs the same. Tempeh bacon fills protein, umami, and crunch — the most complete role match — but costs $2.00 more.

**No bread → lettuce wrap** (gluten-free or keto). Bread provides the structural role. A sandwich without structural integrity is broken. Lettuce wrap provides structural and freshness roles, is gluten-free, vegan, dairy-free, and low-carb. It changes the eating experience but preserves composition integrity.

**No mayo → hummus** (egg-free or vegan). Mayo provides moisture and binding. Hummus provides moisture, richness, binding, and umami — it fills more roles than mayo did. Avocado mash provides moisture, richness, and binding with a milder flavor shift. Mustard provides moisture and acidity but loses binding — a partial role match.

These four scenarios test every aspect of the model: role overlap, dietary filtering, allergen flagging, flavor fit classification, price delta transparency, and auto-suggest vs on-demand distinction.

## Part 2: Deriving the Design System and Implementation

### From the core model to the design language

The design language for the deli prototype is not a skin applied after the fact. It derives from the model's capabilities and logical types.

**Ingredient role colors** come directly from the `ingredient_role` logical type. The base DMETA design language defines semantic color roles (neutral, info, success, warning, danger, pending, active, selected). The deli extension adds `ingredient_role_colors`:

| Role | Color token | Hue |
|---|---|---|
| structural | `--role-structural` | Amber (#C49A3C) |
| protein | `--role-protein` | Warm brown (#8B5E3C) |
| richness | `--role-richness` | Avocado green (#6B8E4E) |
| moisture | `--role-moisture` | Light blue (#5B8DB8) |
| acidity | `--role-acidity` | Yellow-green (#9AB844) |
| crunch | `--role-crunch` | Lettuce green (#7AB648) |
| heat | `--role-heat` | Red-orange (#C85A3A) |
| umami | `--role-umami` | Earthy brown (#7A5A3E) |
| garnish | `--role-garnish` | Herb green (#6B9E6B) |

These colors appear on role tags next to ingredient names in the customizer, on substitution candidate cards showing which roles each replacement fills, and on unfilled-role warnings when a removal breaks composition integrity. The colors are derived from the model, not chosen for decoration. A user who learns that amber means structural and green means richness can scan any composition in the system and immediately see which roles are filled and which are empty.

![The customizer bottom sheet for the Classic BLTA, showing each ingredient with its role tags and dietary badges.](hsd-03-customizer.png)

**Dietary badge colors** come from the `dietary` capability. The base model's semantic color roles map to dietary compatibility states: green for "matches your dietary profile" (safe), yellow for "compatible with caveats" (caveat), red for "contains allergen" (conflict). This mapping is not a design choice — it is a safety requirement. A dairy-free customer who cannot see that a substitution candidate contains dairy is at risk.

**Substitution badge tone** comes from the `substitutable` capability's state. A suggested substitution uses info tone (blue). An applied substitution shifts to success tone (green). A rejected substitution is dismissed. This state progression is the same pattern the base model uses for `status_badge` — the deli extension applies it to a different semantic subject.

### From the model to the widget inventory

The widget inventory is derived from the presentation contracts defined in the core model. Each widget consumes a specific set of presentations and exposes a specific set of action slots.

**RoleTag** (atom) consumes the `ingredient_role` logical type. It renders a compact label with the role's color token. It has no interaction states — it is a visual marker, not a control. The model says ingredient roles are "for interns, reviewers, generated docs, and LLM-assisted workflows." The widget says they are also for customers who want to understand why avocado replaces cheese.

**DietaryBadge** (atom) consumes the `dietary` capability. It renders a compact tag (V, VG, GF, DF, NF) with a compatibility color (safe, caveat, conflict). Tapping it triggers the `filter_by_dietary` action. The model says dietary tags "filter which substitutions are valid." The widget makes that filtering visible and interactive.

**SubstitutionChip** (atom) consumes the `substitutable` capability and the `substitution_badge` presentation. It renders "No X → Y" with role tags, dietary flags, and price delta. Tapping it applies the substitution; long-pressing opens the `substitution_detail` presentation for full alternatives. The model says substitutions "can be accepted with a single tap." The widget implements that contract.

**IngredientRow** (molecule) consumes the `composable` capability and the `ingredient_list` presentation. It renders an ingredient with name, role tags, dietary badges, and swipe-to-remove/substitute actions. The `substitution_suggestion` prop is the inline SubstitutionChip that appears when the ingredient has been removed. The model says "ingredient lists should visually distinguish required vs optional parts." The widget implements that by applying a `required` flag that changes the row's visual treatment.

**CompositionCustomizer** (organism) consumes the `Composition` archetype, the `composable`, `substitutable`, `configurable`, and `dietary` capabilities, and six presentations. It is the primary interaction surface where the replacement engine's suggestions become visible. It combines ingredient list, inline substitution chips, config selectors, dietary summary, and add-to-order action. The model says the flow from "see menu item" to "add to order" should be under 5 taps. The widget implements that contract with a bottom sheet that requires one tap to open, one swipe per removal, one tap per substitution, and one tap to add.

### The prototype implementation

The prototype is three self-contained files: `index.html` (5.7 KB), `styles.css` (20.5 KB), and `app.js` (49 KB). It implements the full ordering flow without a build step, without a framework, and without a backend.

![The Hudson Street Deli menu browser, showing 11 items across three categories with dietary filter chips at the top.](hsd-02-mobile-menu.png)

#### Menu data and substitution rules

The `app.js` file contains two large data structures: `MENU` (11 items) and `SUBSTITUTIONS` (20+ rule sets with 50+ candidate replacements). The MENU array mirrors the domain example YAML — each item has `id`, `name`, `category`, `basePrice`, `description`, `ingredients` (with `id`, `name`, `roles`, `required`, `dietary`), and item-level `dietary` and `allergens` fields.

The SUBSTITUTIONS object maps ingredient IDs to rule sets. Each rule set contains a `candidates` array with the same fields defined by the `substitutable` capability: `name`, `roles`, `dietary`, `allergens`, `flavor`, `priceDelta`, `auto`, and `reasoning`. The `reasoning` field is not consumed by any generator or validator — it exists for the substitution detail sheet, where it provides the human-readable explanation of why the system suggested this replacement.

An alias resolution mechanism handles ingredient ID duplication. The menu has three separate bacon entries (`bacon`, `bacon-2`, `bacon-3`) because each belongs to a different item. The SUBSTITUTIONS object stores the rules once under `bacon` and marks the aliases as `null`. The `resolveSubKey()` function strips trailing numeric suffixes and falls back to name matching to find the canonical rule set.

#### The replacement engine

The replacement engine is not a separate module — it is a pattern that emerges from the interaction between the customizer's state management and the substitution rules data. When the user removes an ingredient:

1. `removeIngredient(id)` sets `ing.removed = true` and clears `ing.substitution`.
2. `renderCustomizer()` detects removed ingredients without substitutions.
3. `renderSubstitutionZone()` looks up the ingredient's substitution rules via `resolveSubKey()`.
4. The rules' top candidates are rendered as inline SubstitutionCards.
5. When the user taps a card, `applySubstitution(id, candidateIdx)` copies the candidate data into `ing.substitution` and calls `recalcCustomizerPrice()`.
6. `checkAllergenWarnings()` compares the item's base allergens against each substitution's allergens. If a substitution introduces a new allergen, the warning banner appears.

This is the entire engine. No ML, no ranking algorithm, no server roundtrip. The ranking is defined at authoring time in the SUBSTITUTIONS object, where candidates are ordered by the deli operator's judgment of which replacement best preserves role integrity.

![After removing bacon from the BLTA, the Smart Substitutions zone appears with Smoked Tofu (auto-suggest) and Tempeh Bacon as ranked replacements.](hsd-04-bacon-removed.png)

![After applying the Smoked Tofu substitution, the ingredient row shows "Smoked Tofu (was Bacon)" in accent green with the replacement's roles (protein, umami) and a ↶ undo button.](hsd-05-sub-applied.png)

#### The substitution detail sheet

The "See all options" link opens a second bottom sheet that renders all replacement candidates — not just the top two shown inline. Each candidate card shows the full reasoning chain: name, reasoning text, role tags, dietary badges, flavor fit classification, price delta, and allergen warnings.

![The substitution detail sheet for mayonnaise, showing three replacement candidates with unfilled roles (moisture, binding), reasoning, dietary compatibility, and price deltas.](hsd-06-sub-detail.png)

This sheet is the `substitution_detail` presentation from the core model. The model says it should "rank candidates by compatibility score, show which roles each candidate fills, display dietary and allergen flags, indicate flavor fit, and show price deltas." The prototype implements every projection from the `substitutable` capability in this sheet.

#### The "no cheese → avocado" flow

The Grilled Cheese item provides the canonical example of the replacement system. Cheddar cheese provides protein, richness, and umami. Removing it creates three unfilled roles. The top auto-suggest is avocado, which fills richness and adds freshness. Nutritional yeast fills umami and adds sharpness. Cashew cheese fills richness and moisture but introduces a tree nut allergen.

![Removing cheddar cheese from the Grilled Cheese triggers the replacement engine, suggesting Avocado as the top auto-suggest replacement with a +$1.50 price delta.](hsd-07-no-cheese-avocado.png)

The reasoning text is crucial for trust. A suggestion that appears without explanation feels like an ad. A suggestion that says "Avocado provides similar richness and creaminess. Dairy-free and vegan-compatible" feels like a knowledgeable counter worker who understands the menu. The `reasoning` field in the substitution rules exists for this purpose.

#### Cart and order tracking

The cart screen shows each order item with applied substitutions, configuration summary, and line price. The `↳ Bacon → Smoked Tofu` lines under item names are derived from the composition state — they are not separate data, they are views of the `ing.substitution` objects that the customizer wrote into the composition when the user applied substitutions.

![The cart screen showing a Classic BLTA with the Bacon → Smoked Tofu substitution visible, total price, and Place Order button.](hsd-08-cart.png)

The order tracker is a simple animated progress indicator. It is not connected to a real backend — it simulates the four-step lifecycle (received → preparing → ready → picked up) with `setTimeout` calls. The tracker exists to prove that the full flow works end-to-end, not to demonstrate a real-time kitchen display system.

![The order tracker showing animated progress from Received through Preparing toward Ready.](hsd-09-tracker.png)

### How the core model influenced graphical choices

Every visual decision in the prototype traces back to the core model:

- **Warm neutral background** (`#FAF8F5`) replaces the base model's cool gray (`subtle_cool_gray`) because the deli domain calls for a paper-menu aesthetic. The base model's `neutral_tone` axis allows this variation.
- **Rounded sans-serif** (`DM Sans`, `Nunito`) replaces the base model's `Inter`/`IBM Plex Sans` because the deli calls for approachable rather than clinical typography. The base model's `type_mode` axis allows this variation.
- **Ingredient role colors** are a deli extension that does not exist in the base model. They derive from the `ingredient_role` logical type, which does not exist in the base model either. Both are domain-specific additions that follow the base model's extension policy ("additive, not reductive").
- **Touch targets (44×44pt minimum)** replace the base model's keyboard-first interaction model. The base model's `density` axis allows this variation — compact mode on mobile means larger targets, not smaller rows.
- **Bottom sheets** replace the base model's detail drawers because mobile touch interaction favors sheet patterns over side panels. The base model's layout primitives do not prescribe sheet vs drawer — they prescribe "inspection surface that preserves context."
- **Dietary badge visibility** is enforced by a lint rule (`dietary_always_visible`, severity: error) that derives from the `dietary` capability's safety requirement. This is not a UX preference — it is a design-system constraint that prevents any implementation from hiding dietary information behind an interaction.

### How the core model influenced UX choices

The replacement engine's behavior is specified by the model, not invented by the UI:

- **Auto-suggest vs on-demand**: The `auto_suggest` flag on each substitution candidate determines whether the SubstitutionChip appears automatically after a removal or whether the user must explicitly request alternatives. The UI does not decide which substitutions to promote — the substitution rules do.
- **Required vs optional roles**: The `required_roles` projection on the `composable` capability determines whether removing an ingredient triggers a warning. The UI renders the warning; the model defines when it is necessary.
- **Allergen warnings**: The `allergen_flags` projection on the `substitutable` capability determines whether applying a substitution triggers an allergen conflict warning. The UI renders the warning; the model defines the condition.
- **Price transparency**: The `price_delta_cents` projection determines whether a substitution shows a price impact. The lint rule `no_hidden_substitution_costs` (severity: warning) enforces that the UI must display this before the substitution is confirmed.
- **Substitution is not upselling**: The lint rule `substitution_not_upsell` (severity: warning) enforces that the replacement engine's ranking is based on role preservation, not price. A higher-priced candidate may appear first, but only because it is the best role match.

## Key design decisions

The following decisions shaped the entire system. Reversing any of them would require revisiting the model and the prototype together.

- **Roles, not categories.** The replacement engine reasons about ingredient function, not food type. This is the core insight. Without it, "no cheese → avocado" would require a hand-coded pair rather than a role-matching algorithm.

- **Compositions carry role integrity constraints.** A sandwich without bread is broken; a sandwich without lettuce is diminished. The `required_roles` projection enables the UI to distinguish these cases.

- **Substitution rules are authored, not learned.** The ranking of replacement candidates is defined by the deli operator, not by a machine learning model. This is deliberate: the operator knows the menu, the ingredients, and the customers. The system's intelligence comes from encoding that knowledge, not from inferring it.

- **Dietary transparency is non-negotiable.** The `dietary` capability and its associated lint rules enforce that dietary tags and allergen warnings are always visible. The design system treats this as a safety requirement, not a UX preference.

- **The model is the source of truth; the UI is a projection.** Every visual element, interaction, and piece of logic in the prototype traces back to a specific archetype, capability, projection, presentation, or action in the YAML source. If the model changes, the UI changes. If the model does not justify a UI element, the element should not exist.

## What the model does not cover

The model leaves several questions open:

- **Cascading substitutions** — removing bread triggers a lettuce wrap substitution, which itself changes which condiments work. The current model treats each substitution independently; cascading is not modeled.
- **Out-of-stock ingredients** — a required ingredient that is unavailable is different from an ingredient the customer chooses to remove. The model does not distinguish these cases.
- **Customer dietary profiles** — the model defines `dietary` as a capability on ingredients and menu items, but it does not model a persistent customer profile that pre-filters substitutions.
- **Station capacity and wait time** — the model defines Station as an Actor + Resource, but it does not model queue depth or preparation time.
- **Substitution acceptance patterns** — the model does not learn from which substitutions customers accept or reject over time.

These are not bugs; they are scope boundaries. The model was designed to prove that role-based replacement works, not to solve every problem in a food ordering system.

## File layout

```
dmeta/examples/street-deli-ordering/
  00-index.yaml                          # IR package manifest
  01-core-model.yaml                     # Core model package index
  core-model/
    core-model.yaml                      # Metadata, dietary tags, ingredient roles, flavor profiles
    archetypes.yaml                      # Composition, Substitution (extending base)
    capabilities.yaml                    # composable, substitutable, configurable, dietary
    presentations.yaml                   # 12 presentations + 8 actions
    street-deli-ordering.yaml            # Domain example with 4 replacement scenarios
  02-design-language.yaml                # Mobile deli ordering design language
  03-widgets.yaml                        # 14 widgets (5 atoms, 3 molecules, 6 organisms)
  prototype/
    index.html                            # Semantic HTML structure
    styles.css                            # Mobile-first design language implementation
    app.js                                # Menu data, replacement engine, cart, tracker
```

## Working rules

- Every ingredient in a composition must carry at least one role. Ingredients without roles cannot participate in the replacement system.
- Every substitution candidate must include `reasoning` text. A suggestion without explanation is an ad.
- The `auto_suggest` flag controls proactive vs on-demand presentation. The UI must not promote a non-auto substitution without user request.
- Dietary badges must be visible on menu cards, ingredient rows, and substitution candidates. This is enforced by the `dietary_always_visible` lint rule.
- Allergen conflicts between substitutions and the customer's dietary profile must produce explicit warnings. This is enforced by the `allergen_warning_visible` lint rule.
- The replacement engine's ranking is based on role preservation quality, not price. This is enforced by the `substitution_not_upsell` lint rule.

## Open questions

- Should the replacement engine be client-side (current approach), server-side API, or hybrid with local caching of substitution rules?
- Should cascading substitutions be modeled (e.g., removing bread → lettuce wrap → which condiments work with a wrap)?
- Should the system model out-of-stock ingredients as a distinct case from customer-requested removals?
- Should customer dietary profiles persist across sessions or remain per-order?
- Should the replacement engine learn from acceptance/rejection patterns over time?

## Related notes

- The base DMETA v0 design system factory and its design documents are at `/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/design-docs/`
- The docmgr ticket for this work is `STREET-DELI-001` at `/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/ttmp/2026/05/20/STREET-DELI-001--street-deli-mobile-ordering-meta-design-system/`
