---
title: "Article: Design System Unification — Making a Package Canonical"
aliases:
  - Design System Unification
  - Package Canonical Migration
  - Design System Unification Article
tags:
  - article
  - design-system
  - react
  - storybook
  - packaging
  - architecture
  - unification
status: active
type: article
created: 2026-06-07
repo: /home/manuel/workspaces/2026-05-27/rag-evaluation-system
---

# Article: Design System Unification — Making a Package Canonical

This article documents the step-by-step unification of a duplicated React design system within a monorepo. The problem is common: a shared component library gets copied into an application layer, then both layers diverge, and the application becomes the implicit source of truth. The solution is a migration that makes the package layer the canonical source and reduces the application layer to app-specific routes, containers, and views.

The work is from the `2026-05-27--rag-evaluation-system` repository. It covers workspace wiring, barrel redirects, Storybook ownership migration, duplicate deletion, and automated visual regression.

> [!summary]
> 1. `packages/rag-evaluation-site` owns reusable atoms, foundation primitives, layout primitives, and shared molecules. `web/` owns routes, containers, backend-connected views, and app-specific molecules.
> 2. The migration proceeded in six ordered steps: inventory, workspace dependency, barrel redirects, Storybook migration, visual verification, duplicate deletion.
> 3. Visual parity is captured with Storybook-based css-visual-diff sweeps across every package-owned story. The sweep produces 0 changed pixels on self-comparison, establishing a deterministic baseline.

## Why this note exists

This note preserves the migration process as a reusable pattern. The same steps apply whenever a design system exists in two places — an application directory and a shared package — and the application directory ends up with newer implementations, additional component files, or stories that should live in the package.

The specific incident that triggered this migration was a review of the `wesen/2026-05-27--rag-evaluation-system` repository. The repository already had `packages/rag-evaluation-site` as a published npm package and `web/` as its application front end. Both contained implementations of the same atoms (Button, TextInput, SelectInput, CheckboxRow, ErrorCallout, IconButton), foundation primitives (Text, Caption, CodeText, Divider, StatusText, VisuallyHidden), layout primitives (Panel, Stack, Inline, AppShell, DashboardGrid, FormRow, ScrollRegion, TabList), and shared molecules (AppNav, DataTable, MetadataGrid). Both contained WidgetRenderer and Widget IR definitions.

The package version already included newer fixes from PR review (custom row key support, normalized DataTable selectedKey). The `web/` layer had stories for all shared components plus additional application-specific stories. The package had no Storybook configuration of its own.

The migration goal was to make `packages/rag-evaluation-site` the single authoritative source for all reusable components, preserve visual parity through automated diffing, and leave `web/` with only app-specific code.

## When to use this pattern

Use this migration pattern when:

- A shared React component library exists as a separate npm package in a monorepo
- The application layer has its own copies of the same component files
- The application layer has newer fixes, additional features, or stories that should belong in the package
- You need a clear ownership boundary between reusable and app-specific code

Do not use this pattern when:

- The package has zero shared components — it is purely an internal implementation detail
- The application layer has no duplicate component implementations at all
- You are building a greenfield project (define ownership boundaries from the start)

## Core mental model

The design system has a single ownership boundary:

```text
packages/rag-evaluation-site/
  ├── src/components/          # atoms, foundation, layout, shared molecules
  ├── src/widgets/             # Widget IR, WidgetRenderer, cell renderers
  ├── src/hooks/               # widget page hooks
  └── .storybook/              # Storybook for package review

web/
  ├── src/components/          # web-only molecules (CoveragePanel, QueryPresetList), corpus/workflow organisms, pages
  ├── src/widgets/             # thin compatibility barrel only (re-exports package)
  ├── src/services/            # API clients, RTK Query slices
  ├── src/store/               # Redux store configuration
  ├── src/routes/              # Application routes
  └── .storybook/              # Storybook for app/container review
```

The package owns reusable implementations and their stories. The application owns everything that depends on backend APIs, Redux state, or application routing. When the application imports a package component, it does so through a workspace dependency. After the migration, the application also keeps thin compatibility barrels so that existing import paths continue to work during transition.

## Architecture

The monorepo has two workspace members:

```text
rag-evaluation-system/
├── pnpm-workspace.yaml        # workspace declaration
├── packages/
│   └── rag-evaluation-site/   # reusable design system package
│       ├── src/components/    # atom/foundation/layout/molecule implementations
│       ├── src/widgets/       # Widget IR + renderer
│       ├── .storybook/        # package Storybook
│       └── package.json       # publishable npm package
├── web/                       # application front end
│   ├── src/components/        # app-specific components, thin compatibility barrels
│   ├── src/widgets/           # thin compatibility barrel (re-exports package)
│   ├── src/services/          # backend API clients
│   ├── src/store/             # Redux store
│   ├── .storybook/            # web Storybook
│   └── vite.config.ts         # Vite aliases for package imports
└── internal/web/              # embedded build output
```

The pnpm workspace declaration:

```yaml
# pnpm-workspace.yaml
packages:
  - 'web/'
  - 'packages/rag-evaluation-site/'
```

The application depends on the package via workspace protocol:

```json
// web/package.json
{
  "dependencies": {
    "@go-go-golems/rag-evaluation-site": "workspace:*"
  }
}
```

Vite aliases in the application resolve the package subpaths for development:

```typescript
// web/vite.config.ts
resolve: {
  alias: [
    { find: '@go-go-golems/rag-evaluation-site/app', replacement: '../packages/rag-evaluation-site/src/app/index.ts' },
    { find: '@go-go-golems/rag-evaluation-site/ir', replacement: '../packages/rag-evaluation-site/src/widgets/ir.ts' },
    { find: '@go-go-golems/rag-evaluation-site', replacement: '../packages/rag-evaluation-site/src/index.ts' },
  ],
}
```

The alias ordering matters: the `/app` and `/ir` subpath aliases are matched before the root package alias. This prevents Vite from resolving `@go-go-golems/rag-evaluation-site/ir` through the root package path, which would produce an invalid resolution like `../packages/rag-evaluation-site/src/index.ts/ir`.

## Implementation steps

The migration proceeded in six ordered steps. Each step completed typechecking and build before proceeding to the next.

### Step 1: Inventory and baseline

Before making any changes, the duplication was quantified. A script scanned both `web/src` and `packages/rag-evaluation-site/src` and found:

- **Components**: 72 byte-for-byte identical files between `web/src/components` and `packages/rag-evaluation-site/src/components`. Only two files differed: `components/index.ts` and `components/molecules/index.ts` (barrel re-export differences).
- **Widgets**: Three files identical (`ir.ts`, `cellRenderers.tsx`, `index.ts`). Two files differed (`actions.ts` and `WidgetRenderer.tsx` — the package versions included newer PR fixes).
- **Hooks**: Non-overlapping. Package had `useWidgetPage`, web had application-specific hooks.
- **Stories**: `web/` had Storybook stories for all shared components plus web-only components. The package had no Storybook configuration.
- **CSS**: Package components used CSS Modules (`.module.css`). Web components used the same CSS Modules format.

The package already included newer implementations: WidgetRenderer had custom row key support and normalized `DataTable.selectedKey` to string, both fixes from PR review.

### Step 2: Add workspace dependency

The package became a workspace dependency of the application:

```bash
pnpm add @go-go-golems/rag-evaluation-site@workspace:* --dir web
```

The package added Storybook dev dependencies:

```json
{
  "devDependencies": {
    "@storybook/react-vite": "^10.4.1",
    "storybook": "^10.4.1"
  }
}
```

The package added Storybook scripts:

```json
{
  "scripts": {
    "storybook": "storybook dev -p 6007",
    "build-storybook": "storybook build"
  }
}
```

Typechecking passed for both the package and the application. The package build (`tsc -p tsconfig.build.json && vite build`) also passed, confirming no circular dependencies.

### Step 3: Redirect barrel imports

Before moving stories or deleting files, the application's barrel files were redirected to re-export from the package. This step preserved all existing import paths while changing the implementation source:

```typescript
// web/src/components/atoms/index.ts (after)
export {
  Button,
  CheckboxRow,
  ErrorCallout,
  IconButton,
  SelectInput,
  TextInput,
} from '@go-go-golems/rag-evaluation-site';
export type { ButtonSize, ButtonVariant } from '@go-go-golems/rag-evaluation-site';

// web/src/components/layout/index.ts (after)
export {
  AppShell,
  DashboardGrid,
  FormRow,
  Inline,
  Panel,
  ScrollRegion,
  Stack,
  TabList,
} from '@go-go-golems/rag-evaluation-site';
export type { DashboardGridRecipe, InlineGap, InlineJustify, StackAlign, StackGap } from '@go-go-golems/rag-evaluation-site';

// web/src/components/molecules/index.ts (after)
export * from './CoveragePanel';
export * from './QueryPresetList';
export { AppNav, DataTable, MetadataGrid } from '@go-go-golems/rag-evaluation-site';
export type { AppNavItem, DataTableColumn, MetadataGridItem } from '@go-go-golems/rag-evaluation-site';
```

The molecules barrel kept `CoveragePanel` and `QueryPresetList` as web-only exports because those components import from backend APIs and Redux state — they do not belong in the reusable package.

The widgets barrel was redirected similarly:

```typescript
// web/src/widgets/index.ts (after)
export {
  WidgetRenderer,
  bindAction,
  dispatchWidgetAction,
  renderCell,
  renderRenderable,
  rowKey,
  component,
  element,
  isWidgetNode,
  text,
} from '@go-go-golems/rag-evaluation-site';
export type { /* all widget types */ } from '@go-go-golems/rag-evaluation-site';
```

This step was the critical pivot point. After the barrel redirect, any application code that imported `from '../components/atoms'` or `from '../widgets'` automatically received package implementations.

### Step 4: Move Storybook ownership

The shared component stories were moved from `web/` into the package. The stories were copied to matching paths under `packages/rag-evaluation-site/src/`:

- 6 atom stories → `packages/rag-evaluation-site/src/components/atoms/*/`
- 7 foundation stories → `packages/rag-evaluation-site/src/components/foundation/*/`
- 8 layout stories → `packages/rag-evaluation-site/src/components/layout/*/`
- 3 shared molecule stories → `packages/rag-evaluation-site/src/components/molecules/*/`
- 1 WidgetRenderer story → `packages/rag-evaluation-site/src/widgets/WidgetRenderer.stories.tsx`

The package got its own Storybook configuration:

```typescript
// packages/rag-evaluation-site/.storybook/main.ts
export default {
  stories: ['../src/**/*.stories.@(ts|tsx)'],
  addons: [],
  framework: { name: '@storybook/react-vite', options: {} },
};
```

```typescript
// packages/rag-evaluation-site/.storybook/preview.ts
import type { Preview } from '@storybook/react-vite';
import '../src/styles.css';

const preview: Preview = {
  parameters: { layout: 'padded' },
};

export default preview;
```

Stories were excluded from the package declaration build:

```json
// packages/rag-evaluation-site/tsconfig.build.json
{
  "exclude": ["src/**/*.stories.tsx", "src/**/*.stories.ts", "src/**/*.stories.module.css"]
}
```

Stories that used RTK Query hooks (the WidgetRenderer story) continued to work because the WidgetRenderer story was moved into the package alongside the package's own WidgetRenderer implementation. The package's WidgetRenderer and Widget IR were self-contained.

The web Storybook kept its app-specific stories: coverage panel stories, corpus organism stories, workflow panel stories, page stories, and retro Mac-style component stories.

### Step 5: Visual verification with css-visual-diff

Two layers of visual verification were applied:

**Package parity check.** A Storybook parity story rendered local `web/src` shared components side by side with package shared components. A css-visual-diff compare ran against both selectors with a 1500ms wait to ensure rendered output:

```bash
css-visual-diff compare \
  --url1 http://127.0.0.1:18607/iframe.html?id=design-system-package-parity--shared-components \
  --selector1 '[data-cvd="local-shared-components"]' \
  --url2 http://127.0.0.1:18607/iframe.html?id=design-system-package-parity--shared-components \
  --selector2 '[data-cvd="package-shared-components"]' \
  --viewport-w 1440 --viewport-h 1000 \
  --wait-ms1 1500 --wait-ms2 1500 \
  --threshold 30 \
  --out compare-shared-components/
```

Result: 0 changed pixels, 0% diff.

**Package storybook sweep.** A script enumerated all 48 package-owned stories from the Storybook `index.json`, served the static build, and ran `css-visual-diff compare` for each story against itself using `#storybook-root` as the selector. This established a deterministic visual baseline for every package component:

```bash
# Generates per-story:
# - 01-compare.md (markdown report with frontmatter)
# - compare.json (pixel diff stats)
# - url1_screenshot.png, url2_screenshot.png (element screenshots)
# - diff_comparison.png, diff_only.png (diff images)
```

All 48 stories reported 0 changed pixels on self-comparison, confirming no unintended style changes.

### Step 6: Delete duplicate implementations

After all imports were redirected and Storybook stories were moved, the duplicated implementations were removed from `web/`:

- `web/src/components/atoms/*/` — 6 directories (Button, CheckboxRow, ErrorCallout, IconButton, SelectInput, TextInput) — deleted
- `web/src/components/foundation/*/` — 6 directories (Caption, CodeText, Divider, StatusText, Text, VisuallyHidden) — deleted
- `web/src/components/layout/*/` — 8 directories (AppShell, DashboardGrid, FormRow, Inline, Panel, ScrollRegion, Stack, TabList) — deleted
- `web/src/components/molecules/AppNav/`, `DataTable/`, `MetadataGrid/` — 3 directories deleted
- `web/src/widgets/WidgetRenderer.tsx`, `actions.ts`, `cellRenderers.tsx`, `ir.ts` — deleted
- `web/src/components/PackageParity.stories.tsx` — deleted (it depended on local copies that no longer existed)

The thin compatibility barrels were kept:

- `web/src/components/atoms/index.ts` — re-exports package atoms
- `web/src/components/foundation/index.ts` — re-exports package foundation
- `web/src/components/layout/index.ts` — re-exports package layout
- `web/src/components/molecules/index.ts` — keeps CoveragePanel/QueryPresetList + re-exports package molecules
- `web/src/widgets/index.ts` — re-exports package widget APIs

The web-only molecules `CoveragePanel` and `QueryPresetList` were kept in `web/` because they import from application services (API clients, RTK Query slices, Redux store) and do not belong in the reusable package.

The `web/src/reference-pages/css-entry.ts` file was updated to import CSS modules from package source paths instead of the now-deleted web-local files.

## Design decisions

### Keep thin compatibility barrels

The migration kept thin re-export barrels in `web/` rather than rewriting every import path. This means existing application code continues to work without changes. If the barrels are removed in a later cleanup step, every import must be audited and rewritten.

### Do not move backend-connected molecules

`CoveragePanel` and `QueryPresetList` import from `../../services/api` and Redux slices. These dependencies are application-specific and do not belong in the reusable package. Moving them would require extracting their presentation logic into pure components first.

### Widget IR belongs in the package

The WidgetRenderer, Widget IR types (`ir.ts`), action bindings (`actions.ts`), and cell renderers (`cellRenderers.tsx`) were all moved into the package. The `web/` layer kept only a thin barrel that re-exports everything. This means the Widget DSL definition lives in one place, eliminating any possibility of divergence.

### Alias ordering matters

Vite resolves aliases in order. The `/app` and `/ir` subpath aliases must be listed before the root package alias. If the root alias is listed first, `@go-go-golems/rag-evaluation-site/ir` resolves to `../packages/rag-evaluation-site/src/index.ts/ir` — an invalid path that produces the error: `Not a directory (os error 20)`.

The alias array form (vs object form) is required because Vite's alias resolution uses ordered matching. Object keys are not guaranteed to be iterated in insertion order.

## Common failure modes

### Storybook build fails after deleting local components

If you delete local component files before Stories are moved to the package, the package Storybook build will fail because it has no stories for its components. Always move stories into the package before deleting the local implementations.

### Import resolution fails after package rename

If the package's `package.json` `name` field changes (e.g., from `@go-go-golems/rag-evaluation-site` to something else), all Vite aliases must be updated. The aliases use the package name as the resolve key.

### css-visual-diff captures spinners instead of rendered content

When comparing Storybook stories, the full-page screenshots may capture a loading spinner if taken before React has rendered. The fix is to add `--wait-ms1 1500` and `--wait-ms2 1500` to give React time to render before screenshot capture.

### Missing CSS module imports break reference rendering

The `web/src/reference-pages/css-entry.ts` file imports CSS modules from side-effect-only paths so Vite includes them in the build. If the component files are deleted without updating these imports, the reference renderer will fail at runtime because the CSS module objects are no longer available.

## Working rules

1. **One source of truth.** Each reusable component lives in exactly one directory — never two. If a new component is added, add it to the package, not the application.

2. **Barrels first, deletion last.** Redirect imports through barrels before deleting local implementations. This ensures no import breaks mid-migration.

3. **Stories before implementations.** Move Stories into the package before deleting local component implementations. Otherwise the package Storybook has no coverage.

4. **Verify with diffs.** Run css-visual-diff between local and package components after barrel redirects and before deletion. This catches unintended style changes.

5. **Keep application-specific code in the application.** Components that import from API clients, Redux slices, or application routes stay in `web/`.

6. **Alias ordering.** In Vite config, list subpath aliases before the root package alias. Use the array form of the alias config, not the object form.

7. **Exclude stories from declaration builds.** Add `src/**/*.stories.tsx` to `tsconfig.build.json` exclude so the package declaration build does not include story type declarations.

## Pseudocode: the migration sequence

```
Step 0: Inventory
  scan(web/src/components) → { identical: N, different: M }
  scan(web/src/widgets) → { identical: N, different: M }

Step 1: Workspace dependency
  pnpm add @go-go-golems/rag-evaluation-site@workspace:* --dir web
  add storybook devDeps to package.json

Step 2: Barrel redirects
  web/src/components/atoms/index.ts → export from package
  web/src/components/foundation/index.ts → export from package
  web/src/components/layout/index.ts → export from package
  web/src/components/molecules/index.ts → export package molecules + keep web-only
  web/src/widgets/index.ts → export from package
  tsc --noEmit (verify)

Step 3: Story migration
  copy web stories to package matching paths
  add .storybook/ to package
  tsc --noEmit (verify)
  storybook build (verify)

Step 4: Visual verification
  css-visual-diff compare (local vs package)
  → 0 changed pixels

Step 5: Delete implementations
  rm web/src/components/atoms/*/ (directories)
  rm web/src/components/foundation/*/ (directories)
  rm web/src/components/layout/*/ (directories)
  rm web/src/components/molecules/{AppNav,DataTable,MetadataGrid}/ (directories)
  rm web/src/widgets/{WidgetRenderer,actions,cellRenderers,ir} (files)
  rm web/src/components/PackageParity.stories.tsx
  update web/src/reference-pages/css-entry.ts (package CSS imports)
  tsc --noEmit (verify)
  storybook build (verify)
```

## Related notes

- [[PROJ - RAG Evaluation System - Architecture and Design System Review]] — original design system audit
- [[PROJ - Widget DSL - UI DSL and Kanban DSL Design and Implementation]] — Widget DSL foundation
- [[PROJ - Widget DSL Visual Quality - Visual Quality Analysis]] — visual quality analysis and fixes
