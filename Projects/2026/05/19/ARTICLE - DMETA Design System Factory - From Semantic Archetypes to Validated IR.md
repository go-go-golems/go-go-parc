---
title: "DMETA Design System Factory: From Semantic Archetypes to Validated IR"
aliases:
  - DMETA Design System Factory Deep Dive
  - Semantic Archetypes to Validated IR
  - Dense Operational UI DSL Project Report
  - Presentation-Based Design System Factory Report
tags:
  - article
  - project-report
  - design-system
  - dsl
  - presentation-based-ui
  - code-generation
  - react
  - frontend
  - validated-ir
  - dense-operational-ui
status: active
type: article
created: 2026-05-19
repo: /home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta
source_tickets:
  - DMETA-001
  - DMETA-002
  - DMETA-003
related_docs:
  - /home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/design-docs/01-design-system-factory-vision-and-scope.md
  - /home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/design-docs/02-semantic-archetype-and-capability-model.md
  - /home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/design-docs/03-dense-operational-ui-graphic-design-and-ux-archetype.md
  - /home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/design-docs/04-concrete-dmeta-system-spec.md
  - /home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/design-docs/05-dmeta-core-model-and-widget-ir-spec.md
  - /home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/design-docs/06-dmeta-design-language-and-tooling-spec.md
  - /home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/sources/dmeta-ir/01-core-model.yaml
  - /home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/cmd/dmeta/main.go
---

# DMETA Design System Factory: From Semantic Archetypes to Validated IR

DMETA is an attempt to make the authoring of dense operational user interfaces explicit enough to generate, validate, review, and reuse. The project began from two working pressures. The first pressure was semantic: applications that display logs, agent runs, shipments, orders, events, metrics, and process state need to treat displayed values as typed semantic presentations, not as strings embedded in components. The second pressure was visual: these applications need a sober, low-chrome, information-dense interface style that can be used for long periods without forcing the user to fight visual decoration.

The work described here turned those pressures into a small design-system factory. It now has long-term design documents, a compact source IR, a split semantic core model, a working Go/Glazed validator, and a reviewed design for the next generator. The implementation is still early, but the important boundary has been crossed: the system is no longer only a discussion about design systems. It has a validated intermediate representation that tools can read.

> [!summary]
> - DMETA separates **semantic archetypes**, **capabilities**, **presentations**, **actions**, **widgets**, and **design-language rules** so dense operational interfaces can be specified without hardcoding one application domain.
> - The first concrete IR is intentionally small: `00-index.yaml`, `01-core-model.yaml` plus split `core-model/*.yaml` files, `02-design-language.yaml`, and `03-widgets.yaml`.
> - The first executable tool is a Go/Glazed validator, `dmeta validate-ir`, which loads the split IR package, checks cross-references, and emits structured validation findings.
> - The visual system is defined as a sober, subtle cool-grey, low-chrome, texture-free dense operational UI archetype. It is not a fixed theme and not a decorative skin.
> - The next tool, planned in DMETA-003, is a TypeScript core registry generator that will project the validated semantic model into frontend types, registries, and action-matching helpers.

## Why this work exists

Dense operational applications have a recurring structure. They show large numbers of records. Those records have identities, labels, states, timestamps, relations, metrics, and actions. The concrete nouns vary by domain. An agent workflow dashboard has agents, sessions, tool definitions, tool runs, tool events, and logs. A retail logistics dashboard has carriers, warehouses, orders, shipments, packages, scan events, and delays. The UI problems are similar even when the domain vocabulary changes.

A typical component library does not capture this common structure. It provides tables, badges, cards, drawers, menus, and buttons. The semantic rules remain scattered across application code. A badge in one table means shipment state; a badge in another table means tool-run status; a menu item in a row knows which backend mutation it should call because that row component was hand-wired for that application. The component library supplies visual primitives, but it does not know why a displayed value is selectable, which operations are valid for it, or how to fill an action argument from another value on the screen.

DMETA starts from a different claim: a dense operational design system should include an authoring language for the semantic and interaction structure of the UI. The goal is not to generate every line of React. The goal is to make the stable parts of the design explicit enough that tools can validate and project them.

The stable parts are:

- which reusable semantic roles exist;
- which capabilities those roles carry;
- which projections a capability exposes;
- which presentations can render those projections;
- which actions can start from those presentations;
- which widgets consume the presentations;
- which visual and interaction rules must be shared across widgets;
- which validation checks prevent the authoring system from drifting.

This is the difference between a component library and a design-system factory. A component library gives developers implementation parts. A design-system factory gives the team a process and a language for producing coherent parts.

## The real source project: incorporating HAIR-041

The most important thing about the DMETA work so far is that it did not start from a blank whiteboard. It started by deliberately carrying over a body of work from HAIR-041 in the hair-booking project and then subjecting that material to a second reading under a different problem.

That source material included:

- a technical specification for the design-system toolchain;
- a widget IR catalog;
- a formal widget-definition YAML format specification;
- a design-language IR;
- widget family YAML files;
- a Storybook coverage manifest;
- multiple implementation and review playbooks;
- audit guides and review diaries.

The carry-over was not mechanical copying. It was interpretive work. We had to answer questions like:

- Which parts of HAIR-041 are specific to a CRUD/admin backend?
- Which parts are really about a reusable design-system authoring process?
- Which artifacts are runtime-adjacent and which are authoring-only?
- Which YAML splits were essential because tooling consumed them, and which splits existed only because the widget inventory had grown large?
- Which review practices mattered because they kept the generated and hand-written parts aligned?

This is why the DMETA work is interesting as a meta-project. The core activity has not been "design a new design system from scratch." The core activity has been "extract the reusable engineering process from a previous design-system project, then adapt it to a more generic and semantically explicit problem space."

## What was carried over from HAIR-041

Several things survived almost unchanged.

### 1. The pass model

The strongest reusable lesson from HAIR-041 was that design-system work becomes tractable when it is broken into named passes with explicit inputs and outputs.

In HAIR-041 the practical pipeline looked like this:

```text
renderer inventory
  -> widget catalog
  -> widget IR formalization
  -> design-language IR formalization
  -> scaffold generation
  -> shared helper generation
  -> manual widget promotion
  -> Storybook hardening
  -> lint / validation
  -> audit and compliance review
```

DMETA keeps the same logic, but inserts semantic archetypes and presentations earlier in the stack:

```text
semantic/archetype model
  -> presentation/action model
  -> design-language model
  -> widget IR
  -> validation
  -> generation
  -> promotion
  -> audit
```

The important carry-over is not the exact sequence of filenames. It is the rule that every stage should produce durable artifacts and that transitions between stages should be reviewable.

### 2. The split between Markdown and machine-consumed IR

HAIR-041 was valuable partly because it did **not** pretend that everything should be YAML. Long-form reasoning lived in Markdown. Tool inputs lived in YAML. Review, audits, and playbooks lived in Markdown. Generated code lived elsewhere.

DMETA adopted that separation directly.

Markdown now holds:

- vision and scope;
- semantic model rationale;
- visual archetype rationale;
- concrete system spec;
- tooling plans;
- diaries and changelogs;
- implementation guides.

YAML now holds:

- core semantic package;
- design-language package;
- widget IR.

That separation is easy to overlook, but it is one of the most important aspects of the meta-approach. It prevents the project from turning conceptual reasoning into prematurely formal configuration.

### 3. Deterministic generation plus manual promotion

HAIR-041 showed that code generation becomes useful when it generates the boring, repeatable, structurally predictable parts:

- file layout;
- shared types;
- scaffold components;
- story stubs;
- metadata sidecars;
- shared helper modules.

It also showed that generation should stop before the point where visual judgment, accessibility nuance, or domain-specific interaction detail begins.

DMETA inherits that rule exactly. The validator is generated-tooling infrastructure. The planned `generate-core` command will generate registries and helpers. Future widget scaffolding will generate structures. But a promoted dense table, stream, or detail drawer will still require human implementation judgment.

### 4. The review and audit layer

HAIR-041 contributed more than source files. It contributed a culture of documentation and review:

- implementation playbooks;
- review playbooks;
- audit guides;
- compliance reports;
- detailed diaries.

This matters because a design-system factory fails if it only produces artifacts and never checks whether those artifacts still describe the real implementation. DMETA has already adopted the same discipline: every substantive step is recorded in ticket diaries and changelogs, and long-term documents are promoted out of the ticket workspace when they become durable knowledge.

### 5. The adapter boundary

One of the best engineering rules from HAIR-041 was the adapter boundary:

> The runtime transport format is not the widget contract.

That rule survives into DMETA as a first-class architectural boundary:

- runtime data stays JSON-safe;
- the adapter reads raw transport data;
- widgets receive typed props and semantic presentation references;
- widgets emit typed callbacks or action requests;
- backend dispatch remains outside widget code.

For designers this may sound like an implementation detail, but it is essential. It is what allows a presentation-based semantic UI to remain testable, generated, and auditable.

## What had to change from HAIR-041

The carry-over was real, but so was the transformation.

### Widget-first became semantic-first

HAIR-041 was built around a widget-definition IR extracted from an admin/backend renderer. DMETA begins one layer earlier. Before widget classes, it defines:

- archetypes;
- capabilities;
- presentations;
- actions.

This shift matters because the problem is no longer only "what widgets exist?" It is "what kinds of semantic things can appear on screen, and how can they be acted on?"

### Domain-specific nouns became archetypes

HAIR-041's source material was already specific: admin shells, resource tables, forms, panels. DMETA had to generalize aggressively. `Agent`, `Shipment`, `Order`, `ToolRun`, and `ScanEvent` are no longer the model. They are examples mapped onto:

- `Actor`
- `WorkItem`
- `Event`
- `Resource`
- `Metric`
- `TimelineSpan`
- `ActionSpec`
- `ActionInvocation`

This is the core meta move. It is what turns one design-system project into a framework for many design-system instances.

### Visual language became an archetype, not a theme

HAIR-041 contributed the discipline of a design-language IR. DMETA pushed that discipline further by making the visual system itself range-based and reusable. Instead of locking onto one aesthetic, the project defines a sober dense operational UI archetype with:

- cool-grey / neutral texture-free surfaces;
- low chrome;
- strong typographic hierarchy;
- compact density modes;
- semantic color;
- explicit focus/selection/candidate states.

The point is not to freeze one look. The point is to freeze the constraints that make the look usable.

## Why this is a rigorous framework rather than a loose pattern

The visual target is a sober dense operational UI. The phrase is deliberately specific. The interface should make large amounts of operational state readable. It should use typography, alignment, spacing, keylines, density modes, and semantic color. It should avoid decorative background noise. During the work, an earlier paper-grain direction was removed. The current design language is texture-free: subtle cool grey or neutral surfaces, low chrome, restrained status color, and careful hierarchy.

For designers, this matters because the system is not asking for a single fixed visual theme. It is asking for a range-constrained design archetype that can be instantiated for concrete applications. A design-system instance can choose exact typefaces, grey values, row heights, and accent colors. The generic archetype defines the acceptable design space.

The active design-language source is:

```text
/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/sources/dmeta-ir/02-design-language.yaml
```

It contains theme axes such as:

```yaml
theme_axes:
  density:
    values: [compact, regular, spacious]
    default: regular
  neutral_tone:
    values: [subtle_cool_gray, neutral_gray, white_panel, dark_console]
    default: subtle_cool_gray
  type_mode:
    values: [mono_only, sans_with_mono, sans_only_with_tabular]
    default: sans_with_mono
```

The important point is that this is not a mood board. It is not a CSS file either. It is an authoring artifact. A later generator can turn it into helper code, and a later linter can reject raw colors, unauthorized typography roles, local status badge styles, or heavy static shadows.

The design-language document defines the visual rules at several levels:

| Level | Purpose |
| --- | --- |
| Theme axes | Controlled variation across concrete design-system instances. |
| Typography roles | Named semantic text roles instead of arbitrary font sizes. |
| Density modes | Shared row height and padding constraints for compact, regular, and spacious contexts. |
| Color semantics | Neutral surfaces and status/category colors with explicit meaning. |
| Presentation recipes | Visual recipes for semantic presentations such as `compact_ref`, `status_badge`, and `dense_row`. |
| Interaction states | Shared states such as rest, hover, focus, selected, candidate, active, disabled, and error. |
| Lint rules | Future checks that prevent visual drift in promoted widgets. |

The design contribution is therefore not only the look of a table or badge. It is the decision that certain visual relationships must become named, validated, and generated. A status badge is not a local style. It is the presentation of the `stateful` capability. A compact reference is not just small text. It is the presentation of identifiable and labelable semantic subjects.

## The engineering problem for programmers

For programmers, the central problem is to keep runtime behavior and authoring semantics separate without losing type information. The frontend eventually needs plain TypeScript types, registries, helper functions, widgets, and adapters. The authoring system needs YAML and Markdown because the semantic model is still design material that humans must review.

The first concrete system spec established this artifact stack:

```text
dmeta/
  design-docs/
    01-design-system-factory-vision-and-scope.md
    02-semantic-archetype-and-capability-model.md
    03-dense-operational-ui-graphic-design-and-ux-archetype.md
    04-concrete-dmeta-system-spec.md
    05-dmeta-core-model-and-widget-ir-spec.md
    06-dmeta-design-language-and-tooling-spec.md
  playbooks/
    01-collaborative-schema-design-sessions-for-presentation-based-ui.md
    02-dmeta-design-system-factory-runthrough-playbook.md
  sources/dmeta-ir/
    00-index.yaml
    01-core-model.yaml
    core-model/
      core-model.yaml
      archetypes.yaml
      capabilities.yaml
      presentations.yaml
      examples/
        agent-workflow.yaml
        retail-logistics.yaml
    02-design-language.yaml
    03-widgets.yaml
  cmd/dmeta/main.go
  pkg/dmeta/validator/
```

The Markdown files explain the system. The YAML files are source artifacts for tools. The Go CLI reads and validates the YAML. Future generators will project the YAML into TypeScript files for React applications.

The first executable command is:

```bash
cd /home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta
GOWORK=off go run ./cmd/dmeta validate-ir --root ./sources/dmeta-ir --include-info --output table
```

It currently emits:

```text
+----------+---------------+----------+------+-------------------------------------------------+------+
| severity | code          | artifact | path | message                                         | hint |
+----------+---------------+----------+------+-------------------------------------------------+------+
| info     | validation_ok | package  |      | DMETA IR package has no error-severity findings |      |
+----------+---------------+----------+------+-------------------------------------------------+------+
```

That output matters because it marks the first point where the design-system factory becomes executable. The IR is no longer only a set of notes. It has a validation boundary.

## The semantic model

The semantic model starts with archetypes and capabilities. These two words have precise roles in DMETA.

An archetype is a reusable operational role. It describes what a thing is for in the UI, not what it is called in a particular domain. `Actor`, `WorkItem`, `Event`, `Resource`, `TimelineSpan`, `ActionSpec`, and `ActionInvocation` are archetypes.

A capability is a reusable affordance or projection set. It describes what the UI and tools can rely on. `identifiable`, `labelable`, `stateful`, `temporal`, `inspectable`, `relatable`, `actionable`, `measurable`, and `parameterized` are capabilities.

The distinction matters because many UI rules attach more naturally to capabilities than to archetypes. A status badge is a representation of `stateful`. A timestamp display is a representation of `temporal`. A compact ID is a representation of `identifiable`. A dense row, by contrast, is usually an archetype-level presentation because it composes several capabilities.

The active archetype source is:

```text
dmeta/sources/dmeta-ir/core-model/archetypes.yaml
```

Each archetype now has a short `description` and a longer `long_description`. This change was important. The YAML is not only for machines; it will also feed generated documentation, intern guides, code reviews, and LLM-assisted workflows. A terse label is not enough for a concept that will guide code generation.

A simplified archetype entry looks like this:

```yaml
WorkItem:
  description: Unit of work that can be tracked, progressed, completed, failed, retried, or inspected.
  long_description: >
    WorkItem represents a unit of operational work that moves through a lifecycle.
    It may be an order, shipment, tool run, background job, ticket, build,
    pipeline step, import, or incident task. WorkItems are usually stateful
    and temporal: they can be pending, running, blocked, failed, completed,
    retried, cancelled, or inspected. The core UI responsibility is to show
    many WorkItems densely while preserving state, owner/actor, timing,
    relation, and action affordances.
  default_capabilities:
    - identifiable
    - labelable
    - stateful
    - temporal
    - actionable
    - inspectable
    - relatable
  recommended_presentations:
    - compact_ref
    - dense_row
    - summary_card
    - detail_panel
```

The active capability source is:

```text
dmeta/sources/dmeta-ir/core-model/capabilities.yaml
```

A capability defines projections that later tooling and widgets can depend on. For example, `stateful` requires a `state` projection and optionally accepts `state_label` and `state_tone`.

```yaml
stateful:
  description: Subject has state/status that can be shown, filtered, and acted on.
  long_description: >
    Stateful means a subject has lifecycle, status, or condition semantics that
    users need to scan, filter, and act on. The state may represent execution
    state, shipment status, health, availability, alert condition, or workflow
    phase. Stateful presentations such as status badges must pair text with
    tone; color reinforces meaning but does not replace it.
  projections:
    state:
      type: string
      required: true
      description: Canonical state value.
    state_label:
      type: string
      required: false
      description: Human-readable state label.
    state_tone:
      type: tone
      required: false
      description: Optional semantic tone override.
  presentations:
    - status_badge
    - state_cell
  actions:
    - filter_by_state
```

This is the level where design and programming meet. Designers care that state is displayed consistently. Programmers care that state can be typed, validated, filtered, and used for action discovery. The capability binds those requirements together.

## Presentations and actions

Presentation-based UI is the interaction model that turns semantic metadata into user operations. In DMETA, a presentation is not just a visual component. It is a display contract.

A presentation declares:

- which layer it belongs to: capability, archetype, or domain;
- which capabilities or archetypes it applies to;
- which projections it requires;
- which optional projections it can use;
- whether it is selectable, copyable, or context-menu enabled;
- which design-language recipe should render it.

The active presentation and action source is:

```text
dmeta/sources/dmeta-ir/core-model/presentations.yaml
```

A simplified status badge looks like this:

```yaml
status_badge:
  description: Compact state/status badge.
  layer: capability
  applies_to:
    capabilities: [stateful]
  requires: [state]
  optional: [state_label, state_tone]
  role: badge
  density: compact
  interaction:
    selectable: true
    context_menu: true
    copy: false
  style_recipe: status_badge
```

The action system uses the same semantic selectors. An action can accept a capability, archetype, presentation, or domain type. This is how a single action definition can work across domains.

```yaml
filter_by_state:
  description: Add a filter matching the selected state.
  category: filter
  accepts:
    - capability: stateful
    - presentation: status_badge
    - presentation: state_cell
  arguments:
    state:
      mode: selected_presentation
      required: true
      accepts:
        - capability: stateful
  result:
    kind: apply_filter
```

A React component should not need to know every possible domain-specific state. It should receive a presentation reference and ask the action registry which actions match that reference. The generated action-matching helper planned in DMETA-003 will implement this rule in TypeScript.

The runtime shape is expected to look like this:

```ts
export type PresentationRef = {
  semanticId: string;
  domainType: string;
  archetypes: ArchetypeId[];
  capabilities: CapabilityId[];
  presentationId: PresentationId;
  label: string;
  value?: unknown;
  copyValue?: string;
  sourceSurface: string;
  sourcePath?: string;
};
```

`PresentationRef` is the key runtime object. It is what a rendered token, row, cell, badge, or compact reference can hand to an action system. It is also the boundary that keeps widgets from parsing arbitrary raw domain data.

## Domain examples as pressure tests

The core model includes two example domains. They are not production domain schemas. They are pressure tests.

```text
dmeta/sources/dmeta-ir/core-model/examples/agent-workflow.yaml
dmeta/sources/dmeta-ir/core-model/examples/retail-logistics.yaml
```

The agent workflow example maps concrete domain types to generic archetypes:

```yaml
ToolRun:
  description: Concrete tool execution.
  archetypes: [ActionInvocation, WorkItem]
  capabilities:
    identifiable:
      id: call_id
    labelable:
      label: tool_name
    stateful:
      state: status
    temporal:
      start_time: started_at
      end_time: finished_at
      duration_ms: duration_ms
    relatable:
      actor_ref: agent_id
    executable:
      execution_state: status
```

The logistics example uses the same generic vocabulary:

```yaml
Shipment:
  description: Shipment lifecycle for an order or package set.
  archetypes: [WorkItem, TimelineSpan]
  capabilities:
    identifiable:
      id: shipment_id
    labelable:
      label: tracking_number
      subtitle: destination
    stateful:
      state: shipment_status
    temporal:
      start_time: created_at
      end_time: delivered_at
    spatial:
      origin: origin_facility
      destination: destination_address
    relatable:
      actor_ref: carrier_id
      resource_ref: order_id
```

These two examples are deliberately different. A `ToolRun` and a `Shipment` are not the same domain object. They are functionally similar enough that the UI can treat both as `WorkItem` instances with `identifiable`, `labelable`, `stateful`, `temporal`, and `relatable` capabilities. This is what makes a generic dense operational design system possible.

## The widget IR

The widget IR is still intentionally small. It lives at:

```text
dmeta/sources/dmeta-ir/03-widgets.yaml
```

It defines generic dense-operational widget classes such as:

- `PresentationToken`
- `StatusBadge`
- `CompactReference`
- `MetricCell`
- `RecordStream`
- `DenseTable`
- `DetailDrawer`
- `ActionPalette`

A widget definition does not redefine the semantic model. It references presentations, capabilities, and archetypes from the core model.

A simplified widget entry looks like this:

```yaml
- id: dmeta.presentation_token
  name: PresentationToken
  status: draft
  classification:
    level: atom
    role: semantic_presentation
  intent:
    purpose: Render a single presentation ref as inline selectable text/token/chip.
    adapter_boundary: Receives typed PresentationRef; does not parse runtime JSON.
  consumes:
    presentations: [compact_id, display_label, status_badge, timestamp_inline, compact_ref, inline_token]
  contract:
    props:
      PresentationTokenProps:
        fields:
          subject:
            type: PresentationRef
            required: true
          variant:
            type: PresentationId
            required: true
```

The key field is `adapter_boundary`. DMETA keeps the HAIR-041 rule: the adapter reads raw runtime data, widgets receive typed props, widgets emit typed callbacks, and the adapter or backend dispatch layer handles side effects.

## The validator

DMETA-002 produced the first executable tool:

```text
dmeta/cmd/dmeta/main.go
dmeta/pkg/dmeta/cmds/validate_ir.go
dmeta/pkg/dmeta/validator/
```

The command is a Go CLI using the Glazed framework. Glazed matters because validation findings are structured rows, not unstructured log lines. A finding has a severity, code, artifact, path, message, and hint. That makes it suitable for humans, scripts, CI output, and future reports.

The validator performs several passes:

| Pass | What it checks |
| --- | --- |
| Artifact identity | `artifact_type` and `schema_version` for each YAML artifact. |
| Index paths | `00-index.yaml` entries point to existing files with matching artifact types. |
| Core references | Archetypes, capabilities, presentations, actions, and domain examples point to known ids. |
| Design-language references | Theme defaults, typography roles, presentation recipes, interaction states, and lint severities are coherent. |
| Widget references | Widgets consume known presentations, capabilities, and archetypes and have unique output paths. |
| Prose context | Core model package has `long_summary`; every archetype and capability has `long_description`. |

The split core-model package required a loader change. `01-core-model.yaml` no longer contains every semantic section directly. The loader now reads the package index and merges the subfiles into one `CoreModelFile` for validation and future generation.

The important logic is in:

```text
dmeta/pkg/dmeta/validator/load.go
dmeta/pkg/dmeta/validator/validate.go
```

In pseudocode, loading now works like this:

```text
LoadPackage(root):
  index = load(root/00-index.yaml)
  coreIndex = load(root/01-core-model.yaml)

  if coreIndex already contains archetypes/capabilities/presentations:
    use it as monolithic model
  else:
    metadata = load(root/coreIndex.files.core_model)
    archetypes = load(root/coreIndex.files.archetypes)
    capabilities = load(root/coreIndex.files.capabilities)
    presentations = load(root/coreIndex.files.presentations)
    for each example file in coreIndex.files.examples:
      load domain example

    merge all sections into CoreModelFile

  design = load(root/02-design-language.yaml)
  widgets = load(root/03-widgets.yaml)
  return Package(index, core, design, widgets)
```

The validator does not generate code. It defines the trust boundary for generators. A generator can rely on `validator.LoadPackage` and `validator.ValidateRoot` rather than reimplementing file traversal and reference checks.

## The generator design

DMETA-003 is currently a design ticket, not an implementation ticket. It produced an intern-facing guide for the next tool:

```text
dmeta/ttmp/2026/05/19/DMETA-003--generate-typescript-core-registries-from-dmeta-v0-ir/design-doc/01-dmeta-typescript-core-registry-generator-intern-guide.md
```

That guide was uploaded to reMarkable for review. Implementation has not started.

The planned command is:

```bash
GOWORK=off go run ./cmd/dmeta generate-core \
  --root ./sources/dmeta-ir \
  --out ./generated/dmeta-core
```

The generator will produce:

```text
generated/dmeta-core/
  archetypes.ts
  capabilities.ts
  presentations.ts
  actions.ts
  PresentationRef.ts
  actionMatching.ts
  index.ts
```

The first generated behavior should be action matching. The generated `actionMatching.ts` should implement the selector rules from the IR:

```text
selectorMatchesPresentationRef(selector, ref):
  if selector.capability exists:
    require ref.capabilities contains selector.capability
    require all selector.requiresCapabilities are present

  if selector.archetype exists:
    require ref.archetypes contains selector.archetype
    require all selector.requiresCapabilities are present

  if selector.presentation exists:
    require ref.presentationId equals selector.presentation

  if selector.domainType exists:
    require ref.domainType equals selector.domainType
```

This helper will be the first runtime projection of the semantic model. A context menu, command palette, dense table, or stream row can call it to discover which actions apply to a selected presentation.

## Implementation chronology

The work happened in three main tickets.

### DMETA-001: the factory foundation

DMETA-001 created the long-term documents and the first IR. It established the distinction between:

- semantic archetypes;
- capabilities;
- presentations;
- actions;
- widgets;
- design-language rules;
- runtime wire format;
- generated helpers;
- manual promotion;
- validation and audit.

It also imported the HAIR-041 design-system DSL material and extracted the reusable process. The HAIR-041 lesson was not that YAML is intrinsically useful. The lesson was that a design system becomes maintainable when the team separates authoring artifacts, generated structure, manual implementation, Storybook evidence, lint, audit, diary, and changelog.

DMETA-001 then narrowed the initial formal YAML set. Instead of creating many files at once, it started with four source artifacts:

```text
00-index.yaml
01-core-model.yaml
02-design-language.yaml
03-widgets.yaml
```

Later, `01-core-model.yaml` was split because the semantic sections needed longer prose context.

### DMETA-002: the validator

DMETA-002 created the first executable tool and an intern guide. The deliverables were:

- `dmeta validate-ir`
- YAML loading for the v0 package
- validation findings as Glazed rows
- cross-reference checks
- current IR validation with no errors
- reMarkable upload of the intern guide

The validator made the IR operational. It is now possible to change a YAML file and immediately check whether the package still holds together.

### DMETA-003: the core generator design

DMETA-003 created the guide for the next tool and stopped before implementation. This was intentional. The generator will affect the frontend API shape, so the design should be reviewed before code is written.

The guide currently recommends:

- using `validator.LoadPackage` to read the split package;
- generating TypeScript string-union types with `as const` arrays;
- generating plain metadata objects;
- generating `PresentationRef`;
- generating `actionMatching.ts`;
- generating into `generated/dmeta-core` for now;
- avoiding React component generation in this ticket.

## Current state of the repository

The DMETA repository currently has the following important files:

```text
/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/
  README.md
  go.mod
  cmd/dmeta/main.go
  pkg/dmeta/cmds/validate_ir.go
  pkg/dmeta/validator/
  design-docs/
  playbooks/
  sources/dmeta-ir/
  ttmp/2026/05/19/DMETA-001--...
  ttmp/2026/05/19/DMETA-002--...
  ttmp/2026/05/19/DMETA-003--...
```

The latest important commits are:

```text
6bba4a7 Split and enrich DMETA core model IR
957803a Add DMETA core registry generator guide
7b7a567 Remove texture references from DMETA design language
abe6270 Close DMETA validator ticket
70730d5 Record DMETA validator completion
2f221be Implement DMETA IR validator CLI
```

DMETA-002 is closed. DMETA-003 is open for review. The implementation tasks in DMETA-003 remain intentionally open.

## What designers should take from this

The design system is being specified at the level where visual choices become shared operational semantics. The `status_badge` presentation is not only a style. It is the design expression of the `stateful` capability. The `compact_ref` presentation is not only small text. It is the design expression of identifiable and labelable semantic subjects that can be copied, inspected, related, and used as action arguments.

The visual direction is now intentionally restrained:

- cool-grey or neutral surfaces;
- no decorative texture;
- no background noise;
- low chrome;
- named typography roles;
- density modes;
- semantic color;
- explicit focus, selection, candidate, and active states.

Design decisions in this system should be written into the design-language IR when they are shared, repeated, and enforceable. Local widget styling should be reserved for genuinely local implementation details. If a visual pattern appears repeatedly, it should become a named recipe or helper so generated scaffolds, reviews, and lint rules can refer to it.

## What programmers should take from this

The code is moving toward a standard sequence:

```text
YAML IR
  -> validator
  -> TypeScript core registry generator
  -> design helper generator
  -> widget scaffold generator
  -> manual promotion
  -> lint/audit
```

Programmers should not treat the YAML files as loose configuration. They are source artifacts. They need stable ids, references, and prose context because downstream tools will depend on them.

The immediate programming rules are:

- Use `validator.LoadPackage` when a tool needs the core model. Do not manually re-read the split core-model files.
- Run `dmeta validate-ir` before generation.
- Keep generated files deterministic by sorting map keys.
- Generate plain TypeScript types, constants, and metadata first. Do not generate React implementation before the core registry stabilizes.
- Preserve the adapter boundary: raw runtime data becomes typed props and presentation references before widgets see it.
- Treat `PresentationRef` as the runtime bridge between rendered values and actions.

## The next technical step

The next step is to review DMETA-003 and then implement `dmeta generate-core`. That command should generate TypeScript core registry files from the validated IR. It should not generate widgets yet. It should establish the frontend semantic API.

The expected implementation sequence is:

1. Add a generator package under `pkg/dmeta/generator/core`.
2. Use `validator.LoadPackage` and `validator.ValidateRoot` before generation.
3. Render deterministic TypeScript files for archetypes, capabilities, presentations, actions, `PresentationRef`, action matching, and barrel exports.
4. Add a Glazed command in `pkg/dmeta/cmds/generate_core.go`.
5. Register it in `cmd/dmeta/main.go`.
6. Run a dry run and real generation.
7. Review generated TypeScript.
8. Add golden tests when the output stabilizes.

The first generator will answer a concrete question: can the semantic model become a usable frontend API? If the answer is yes, the following tools can build on it: design helper generation, widget scaffolding, Storybook coverage, and domain-specific design-system instantiation.

## Working rules going forward

- Keep Markdown for rationale, design reasoning, implementation guides, reviews, and diaries.
- Keep YAML for facts that validators, generators, registries, lint rules, or review manifests consume.
- Give formal YAML enough prose context to be understandable without external chat history.
- Keep archetypes domain-neutral and composable.
- Attach presentations to the lowest reusable layer that expresses the behavior: capability first, archetype second, domain only when necessary.
- Run the validator after every IR change.
- Review generator designs before implementation when they define frontend API shapes.
- Do not let a concrete domain such as agent workflows become the implicit universal model.
- Do not let the visual system drift toward decorative texture or local ad hoc styles.

## Related notes

- [[ARTICLE - Playbook - A DSL for Creating Design Systems]]
- [[ARTICLE - Presentation-Based UI for Log Viewing]]
- [[ARTICLE - From Print Pastiche to Intentful Language - Evolving a Design System by Subtraction]]

## Repository and ticket references

- Repository: `/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta`
- DMETA-001: `/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/ttmp/2026/05/19/DMETA-001--design-system-factory-first-runthrough-of-presentation-based-ui-dsl-for-high-volume-data-applications`
- DMETA-002: `/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/ttmp/2026/05/19/DMETA-002--build-glazed-cli-validator-for-dmeta-v0-ir`
- DMETA-003: `/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/ttmp/2026/05/19/DMETA-003--generate-typescript-core-registries-from-dmeta-v0-ir`
