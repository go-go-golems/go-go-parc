---
title: "go-go-os Frontend npm Packages: Publishing, Standalone Consumption, and Trusted CI/CD"
aliases:
  - go-go-os npm publishing deep dive
  - go-go-os package publishing report
  - go-go-os standalone consumer report
  - go-go-os trusted publishing report
  - go-go-os npm ci cd report
tags:
  - article
  - npm
  - trusted-publishing
  - github-actions
  - provenance
  - react
  - vite
  - storybook
  - rtk-query
  - design-system
  - go-go-golems
  - frontend
  - go-go-os
  - quickjs
  - vm-runtime
status: active
type: article
created: 2026-05-11
updated: 2026-05-12
repo: /home/manuel/workspaces/2026-05-11/npm-packages-go-go-os
source_repo: https://github.com/go-go-golems/go-go-os-frontend
examples_repo: https://github.com/go-go-golems/go-go-os-examples
live_examples: https://go-go-os-examples.yolo.scapegoat.dev/
---

# go-go-os Frontend npm Packages: Publishing, Standalone Consumption, and Trusted CI/CD

This is the frontend-package and publishing branch of the [[go-go-os]] project map.

This article documents the full technical path from a private frontend monorepo to a public npm package family, a real standalone consumer application, a deployed examples site, and finally a GitHub Actions Trusted Publishing pipeline with npm provenance.

The work started with a narrow question: can the reusable frontend pieces in `go-go-os-frontend` be published as public npm packages and consumed outside the source monorepo? It ended with a complete release system:

- npm packages are published under the public `@go-go-golems/*` scope;
- a standalone examples app consumes the public packages rather than sibling workspace aliases;
- VM/runtime packages work without package-internal Vite `?raw` workarounds;
- the examples app is deployed publicly as a static site;
- npmjs Trusted Publishing is configured for the package family;
- GitHub Actions can publish package releases to npmjs using OIDC and provenance, without an `NPM_TOKEN`;
- the first coordinated package stack has been published through the trusted pipeline.

The main source repositories are:

```text
/home/manuel/workspaces/2026-05-11/npm-packages-go-go-os/go-go-os-frontend
/home/manuel/workspaces/2026-05-11/npm-packages-go-go-os/2026-05-11--npm-go-go-os-test
```

The public examples repository and site are:

```text
https://github.com/go-go-golems/go-go-os-examples
https://go-go-os-examples.yolo.scapegoat.dev/
```

> [!summary]
> The final system has four durable results.
> 1. The public package family now includes core UI, REPL, shell, chat, confirmation, widget, scripting, UI-card, and Kanban runtime packages.
> 2. The external examples app validates the package surfaces through progressive stages from theme smoke tests to QuickJS VM Kanban rendering.
> 3. The examples app is deployed as a static Vite site through a shared Caddy/K3s static hosting pattern.
> 4. npmjs Trusted Publishing is configured and proven end-to-end with GitHub Actions provenance for the coordinated package stack.

---

## 1. Why this report exists

The first publication of a package family concentrates several classes of risk in one place. A package can look reusable inside a monorepo while still depending on hidden assumptions: path aliases, workspace dependency resolution, global CSS side effects, local npm registry configuration, unpublished transitive packages, and human-controlled CLI credentials.

This report records how those assumptions were made explicit and then removed or documented. It is meant to be useful for future package extraction work, future npm releases, and future consumer applications that want to depend on `go-go-os` packages without cloning the source monorepo.

The central standard used throughout the project was:

```text
A package is public only after an independent consumer can install it from npmjs,
import it through documented exports, build it with normal frontend tooling,
render it correctly in a browser, and upgrade it through a repeatable release path.
```

That standard is stricter than “npm publish succeeded.” It requires package publication, consumer validation, production build validation, runtime validation, and release automation.

---

## 2. Initial package extraction: from package-shaped folders to public packages

Before publication, `go-go-os-frontend` already had package-shaped directories under `packages/`. Important package names already existed:

```text
@go-go-golems/os-core
@go-go-golems/os-repl
@go-go-golems/os-widgets
@go-go-golems/os-kanban
```

But those directories were not yet hardened public packages. The metadata and tooling still reflected internal assumptions:

- packages were private or internally oriented;
- scoped npm config could route `@go-go-golems` to GitHub Packages;
- `workspace:*` dependencies needed conversion for public consumers;
- TypeScript build prerequisites were not fully established;
- CSS theme entrypoints needed explicit side-effect preservation;
- no independent consumer application had installed the packages from public npm.

The first public release was deliberately small:

| Package | Role | First release |
|---|---|---|
| `@go-go-golems/os-core` | low-level UI primitives, theme entrypoints, Redux slices, desktop primitives | `0.1.0` |
| `@go-go-golems/os-repl` | REPL/terminal component, driver contracts, theme | `0.1.0` |
| `@go-go-golems/os-widgets` | higher-level widgets and widget primitives | `0.1.0` |

This was the smallest coherent first wave. `os-core` provides the theme and primitive foundation. `os-repl` is independently useful and is consumed by richer widgets. `os-widgets` proves that the higher-level component surface can also leave the monorepo.

---

## 3. The publication build pipeline

The source packages are authored as TypeScript and CSS. The public npm artifacts are built into `dist/` directories by:

```text
scripts/packages/build-dist.mjs
```

The build script does several important transformations:

1. compiles TypeScript to JavaScript and declaration files;
2. copies CSS and `.vm.js` runtime assets;
3. removes test/story artifacts from publish output;
4. rewrites `exports`, `main`, and `types` from source paths to dist paths;
5. rewrites `workspace:*` dependencies to concrete package versions;
6. writes a publishable `dist/package.json`;
7. copies package README files into `dist`.

The publication surface is therefore not the source directory. It is:

```text
packages/<package>/dist
```

This matters because npm consumers should receive built JavaScript, declarations, CSS assets, generated VM source modules, package metadata, and README documentation — not the source tree and local test fixtures.

### Initial build failure: TypeScript availability

The first build validation exposed that TypeScript was not available in the way the package build expected. Installing it with npm failed because npm did not accept the workspace protocol shape in this repository:

```text
npm error code EUNSUPPORTEDPROTOCOL
npm error Unsupported URL Type "workspace:": workspace:*
```

The practical fix was to use pnpm for the workspace install and make TypeScript available through the workspace dependency graph. This established the first operational rule:

```text
Use pnpm for repository dependency installation and npm only for npm CLI publication commands.
```

### Registry targeting failure: GitHub Packages versus npmjs

Another early failure came from scoped npm configuration. A user-level config mapped the `@go-go-golems` scope to GitHub Packages:

```ini
@go-go-golems:registry=https://npm.pkg.github.com
```

That produced permission failures when the intended target was npmjs. The repo now has a project `.npmrc` that points the scope at npmjs:

```ini
@go-go-golems:registry=https://registry.npmjs.org/
access=public
```

Later, the user-level npm config was also cleaned so local verification works normally:

```bash
npm config set @go-go-golems:registry https://registry.npmjs.org/ --location=user
```

The general lesson is:

```text
Package metadata does not determine the registry by itself. npm configuration does.
```

---

## 4. Public package chronology

The package family grew in waves.

### First wave

```text
@go-go-golems/os-core@0.1.0
@go-go-golems/os-repl@0.1.0
@go-go-golems/os-widgets@0.1.0
```

These releases proved the basic npmjs publication path and independent installation.

### README/docs patch wave

```text
@go-go-golems/os-core@0.1.1
@go-go-golems/os-repl@0.1.1
@go-go-golems/os-widgets@0.1.1
```

These made the npm package pages usable for consumers.

### REPL focus and dependent package wave

A browser interaction bug appeared in the REPL: after pressing Enter, the input lost focus. The root cause was that the input line used a real DOM `disabled` attribute during command execution. Browsers blur disabled inputs. The fix was to use `aria-disabled` instead so the input remained focusable.

Published fixes:

```text
@go-go-golems/os-repl@0.1.5
@go-go-golems/os-widgets@0.1.2
```

A package-local focus repro was added under:

```text
packages/os-repl/repro/focus
```

### Shell and VM package wave

The standalone examples needed public shell and VM/runtime surfaces. The next package family was published:

```text
@go-go-golems/os-shell@0.1.0
@go-go-golems/os-chat@0.1.0
@go-go-golems/os-confirm@0.1.0
@go-go-golems/os-scripting@0.1.0
@go-go-golems/os-ui-cards@0.1.0
@go-go-golems/os-kanban@0.1.0
```

This moved the project from a widget-only package family to a runtime package family. Consumers could now use the shell/window-manager boundary, QuickJS runtime host, VM UI-card renderer, and VM Kanban renderer.

---

## 5. The standalone consumer evolved into progressive examples

The first consumer app was an OS1 Control Panel. It used public packages in a normal React/Vite/Redux/Storybook application. That proved the basic package surfaces, but the project soon needed a better teaching and regression structure.

The app became a progressive examples workspace, published publicly as:

```text
https://github.com/go-go-golems/go-go-os-examples
```

The examples are numbered so each stage validates a specific package boundary:

| Stage | Directory | Purpose |
|---|---|---|
| 00 | `examples/00-theme-smoke` | Theme imports and root scoping contract |
| 01 | `examples/01-os-core-primitives` | `os-core` primitive components |
| 02 | `examples/02-local-state-forms` | local React state with package controls |
| 03 | `examples/03-rtk-query-control-panel` | Redux Toolkit and RTK Query app structure |
| 04 | `examples/04-rich-widgets` | richer widgets from `os-widgets` |
| 05 | `examples/05-window-manager-shell` | public `os-shell` shell/window-manager boundary |
| 06 | `examples/06-repl-console` | `MacRepl`, custom drivers, completions, host effects |
| 07 | `examples/07-vm-ui-card` | QuickJS runtime rendering `ui.card.v1` |
| 08 | `examples/08-vm-events-and-intents` | VM handlers dispatching draft updates and host notifications |
| 09 | `examples/09-vm-kanban-runtime` | VM-authored `kanban.v1` rendering via `os-kanban` |

The root app is only a navigator. The examples are the contract tests.

### Theme contract

Every consumer must import the theme layers and render inside the theme scope:

```ts
import '@go-go-golems/os-core/theme';
import '@go-go-golems/os-core/desktop-theme-macos1';
import '@go-go-golems/os-widgets/theme';
```

```tsx
<div data-widget="hypercard" className="theme-macos1">
  <App />
</div>
```

The theme system is not merely CSS. It is a CSS import plus a DOM scoping contract.

---

## 6. VM runtime packaging: removing package-internal raw imports

The most technical package boundary was the VM runtime family. VM packages need to provide JavaScript source strings to the QuickJS runtime. Initial releases used package-internal Vite raw imports such as:

```ts
import stackBootstrapSource from './stack-bootstrap.vm.js?raw';
import uiPackagePrelude from './runtime-packages/ui.package.vm.js?raw';
import kanbanPackagePrelude from './runtime-packages/kanban.package.vm.js?raw';
```

This worked in some contexts but failed in Vite dependency optimization when the raw imports came from `node_modules`:

```text
No matching export in "node_modules/@go-go-golems/os-kanban/runtime-packages/kanban.package.vm.js?raw" for import "default"
No matching export in "node_modules/@go-go-golems/os-scripting/plugin-runtime/stack-bootstrap.vm.js?raw" for import "default"
No matching export in "node_modules/@go-go-golems/os-ui-cards/runtime-packages/ui.package.vm.js?raw" for import "default"
```

The durable fix was “Option A”: keep readable `.vm.js` files as source of truth, but generate committed TypeScript modules that export source strings.

Generator:

```text
scripts/packages/generate-vm-source-modules.mjs
```

Generated files:

```text
packages/os-scripting/src/plugin-runtime/stackBootstrapSource.generated.ts
packages/os-ui-cards/src/runtime-packages/uiPackageSource.generated.ts
packages/os-kanban/src/runtime-packages/kanbanPackageSource.generated.ts
```

The package runtime now imports normal TypeScript modules, not `?raw` package-internal URLs:

```ts
import stackBootstrapSource from './stackBootstrapSource.generated';
```

The invariant is enforced by:

```bash
pnpm run check:vm-sources
```

Published raw-source fix packages:

```text
@go-go-golems/os-scripting@0.1.1
@go-go-golems/os-ui-cards@0.1.1
@go-go-golems/os-kanban@0.1.1
```

README/docs patch releases followed:

```text
@go-go-golems/os-scripting@0.1.2
@go-go-golems/os-ui-cards@0.1.2
@go-go-golems/os-kanban@0.1.2
```

The consumer app then removed its temporary Vite workaround:

```ts
optimizeDeps: {
  exclude: [...],
  include: ['debug'],
}
```

This restored the intended package contract: consumers may use raw imports for their own local `.vm.js` bundles, but published package internals no longer require consumers to configure Vite around dependency raw imports.

---

## 7. Runtime host notifications and provider boundaries

Stage 08 exposed a subtle runtime-host issue. The VM handler dispatched:

```js
ctx.dispatch({
  type: 'notify.show',
  payload: { message: 'Notification dispatched from QuickJS' },
});
```

The runtime route correctly converted that to a `showToast` action. The missing piece was a toast presenter inside the same isolated VM example Redux provider. The fix was to render host chrome from inside `VmExampleHost`:

```tsx
function VmExampleToast() {
  const dispatch = useDispatch();
  const toast = useSelector((state) => selectToast(state));

  if (!toast) {
    return null;
  }

  return <Toast message={toast} onDone={() => dispatch(clearToast())} />;
}
```

This established another public-runtime rule:

```text
If a VM dispatches host-facing system actions, the host must render the corresponding host chrome inside the same store/provider boundary.
```

---

## 8. Production CSS side effects and the Kanban failure

The deployed examples site revealed a production-only CSS failure in stage 09. The Kanban DOM rendered, but the board was unstyled. Computed styles showed block layout rather than flex layout, and the built stylesheet lacked Kanban selectors.

The consumer already imported:

```ts
import '@go-go-golems/os-kanban/theme';
```

The package metadata was the problem. It preserved CSS files:

```json
"sideEffects": ["**/*.css"]
```

But the public theme entrypoint was a JavaScript module that imported CSS:

```js
import './kanban.css';
```

If a bundler tree-shakes the JavaScript theme module, the CSS import inside it never runs. The fix was to preserve the JS theme entrypoints too:

```json
"sideEffects": [
  "**/*.css",
  "./theme/index.js",
  "./theme/*.js"
]
```

Published fix:

```text
@go-go-golems/os-kanban@0.1.3
```

Live validation after redeploy showed:

```json
{
  "kbDisplay": "flex",
  "boardDisplay": "flex",
  "boardOverflowX": "auto",
  "columnWidth": "200px",
  "hasKanbanCssRule": true
}
```

The same audit later found related theme-entry risks in `os-chat` and `os-core`, leading to metadata fixes and Trusted Publishing releases:

```text
@go-go-golems/os-chat@0.1.1
@go-go-golems/os-core@0.1.2
```

---

## 9. Browser regressions in the examples app

The manual failures became automated browser checks in the examples app. Playwright was added with:

```text
playwright.config.ts
tests/e2e/runtime-stages.spec.ts
scripts/check-kanban-css.mjs
```

The tests cover:

- stage 06: REPL input stays focused after submitting `status`;
- stage 08: clicking `Notify host` shows `Notification dispatched from QuickJS`;
- stage 09: Kanban computed styles prove theme CSS is present;
- no unexpected browser console or page errors.

The production CSS script checks built stylesheets for representative Kanban selectors:

```text
[data-part=kb-board]
[data-part=kb-card]
[data-part=kb-column]
```

Validation command set:

```bash
npm run build
npm run check:kanban-css
npm run test:e2e
```

The first Playwright run failed because browser binaries were not installed locally:

```text
Executable doesn't exist ... Please run: npx playwright install
```

After:

```bash
npx playwright install chromium
```

all tests passed.

---

## 10. Public static examples deployment

The examples app was published as a public static site:

```text
https://go-go-os-examples.yolo.scapegoat.dev/
```

The repository publishes a static artifact image:

```text
ghcr.io/go-go-golems/go-go-os-examples-static:sha-<short-sha>
```

The image contains `/site`, not a web server. The K3s cluster has a shared Caddy static host that serves many static sites from a shared PVC:

```text
/srv/sites/{host}/current
```

For the examples site:

```text
/srv/sites/go-go-os-examples.yolo.scapegoat.dev/current -> releases/sha-e41d1c5ed7bc
```

This matters because the deployment is another consumer validation layer. The packages must work not only in Vite dev and Storybook, but also in a production Vite build served through the cluster.

---

## 11. npm Trusted Publishing: replacing token publication with OIDC

Manual token publication proved the package family, but it was not the desired long-term release path. The final pipeline uses npmjs Trusted Publishing.

npmjs package settings now trust this identity for all public packages:

```text
Repository: go-go-golems/go-go-os-frontend
Workflow: publish-npm.yml
Environment: npm-production
```

Configured package-side trusted publishers:

```text
@go-go-golems/os-core
@go-go-golems/os-repl
@go-go-golems/os-widgets
@go-go-golems/os-shell
@go-go-golems/os-chat
@go-go-golems/os-confirm
@go-go-golems/os-scripting
@go-go-golems/os-ui-cards
@go-go-golems/os-kanban
```

The workflow is:

```text
.github/workflows/publish-npm.yml
```

The publish job declares:

```yaml
environment: npm-production
permissions:
  contents: read
  id-token: write
```

The real publish command uses provenance:

```bash
npm publish packages/<pkg>/dist \
  --access public \
  --tag latest \
  --registry=https://registry.npmjs.org/ \
  --provenance
```

No `NPM_TOKEN` is required for this path.

### Workflow inputs

The workflow is manual (`workflow_dispatch`) and supports:

```text
package_set: single | os-core | first-wave | shell-stack | vm-stack | all
package_name: package name or package dir for single-package releases
npm_tag: latest | next | canary | ...
dry_run: true by default
skip_existing: true by default
confirm_latest_publish: must be CONFIRM_LATEST for real latest publishes
```

There are two guards for real `latest` releases:

1. the workflow input must contain `CONFIRM_LATEST`;
2. the helper script refuses a real `latest` publish unless `CONFIRM_LATEST_PUBLISH=true` is present.

### Publish helper

The workflow calls:

```text
scripts/packages/publish-npm-package-set.mjs
```

The helper:

- resolves package sets and single package names;
- reads built `dist/package.json` files;
- checks whether each `name@version` already exists on npmjs;
- skips existing versions when requested;
- publishes only from `dist`;
- uses npmjs explicitly;
- includes provenance for real publishes.

Package sets live in:

```text
scripts/packages/package-sets.mjs
```

The `vm-stack` set includes `os-widgets` because `os-kanban` depends on it:

```text
os-core
os-scripting
os-ui-cards
os-widgets
os-kanban
```

### Lockfile and CI install determinism

`pnpm-lock.yaml` is now committed. Workflows use:

```yaml
cache: pnpm
```

and:

```bash
pnpm install --frozen-lockfile
```

This fixed the earlier compromise where the workflow used non-frozen installs because the lockfile was ignored.

### Node version

The publish workflow uses Node 24 for repository commands:

```yaml
node-version: '24'
```

This provides npm 11.x, which supports Trusted Publishing and provenance without mutating npm during the workflow.

GitHub still emits a non-failing warning that some action implementations run on Node 20. That warning is about the internals of `actions/checkout`, `actions/setup-node`, and `pnpm/action-setup`, not the project command runtime.

---

## 12. Trusted Publishing release chronology

The first dry-run workflow could not be dispatched until `publish-npm.yml` existed on `main`. After pushing it to `main`, the first run exposed two setup issues:

1. `actions/setup-node` with `cache: pnpm` failed because `pnpm-lock.yaml` was not tracked;
2. `npm install -g npm@latest` failed under Node 22 with `Cannot find module 'promise-retry'`.

The fixes were:

- commit `pnpm-lock.yaml` and restore `pnpm install --frozen-lockfile`;
- use Node 24 and remove the npm self-upgrade step.

The first successful dry-run was:

```text
25705092100 — os-core dry-run, skipped existing version
```

The first real Trusted Publishing release was:

```text
@go-go-golems/os-chat@0.1.1
Run: 25705272997
Provenance: https://search.sigstore.dev/?logIndex=1513355990
```

Then `os-core` was published through the same pipeline:

```text
@go-go-golems/os-core@0.1.2
Run: 25705516239
Provenance: https://search.sigstore.dev/?logIndex=1513414083
```

Finally the full coordinated package stack was published:

```text
Run: 25706017029
```

Skipped existing versions:

```text
@go-go-golems/os-core@0.1.2
@go-go-golems/os-repl@0.1.5
@go-go-golems/os-chat@0.1.1
```

Published new versions:

```text
@go-go-golems/os-scripting@0.1.3
@go-go-golems/os-ui-cards@0.1.3
@go-go-golems/os-confirm@0.1.1
@go-go-golems/os-shell@0.1.1
@go-go-golems/os-widgets@0.1.3
@go-go-golems/os-kanban@0.1.4
```

Provenance logs from the coordinated publish:

```text
os-scripting@0.1.3   https://search.sigstore.dev/?logIndex=1513569688
os-ui-cards@0.1.3    https://search.sigstore.dev/?logIndex=1513570254
os-confirm@0.1.1     https://search.sigstore.dev/?logIndex=1513570738
os-shell@0.1.1       https://search.sigstore.dev/?logIndex=1513571277
os-widgets@0.1.3     https://search.sigstore.dev/?logIndex=1513571856
os-kanban@0.1.4      https://search.sigstore.dev/?logIndex=1513572491
```

Registry verification confirmed Trusted Publisher metadata:

```text
@go-go-golems/os-core@0.1.2        publisher=GitHub Actions trusted=github
@go-go-golems/os-chat@0.1.1        publisher=GitHub Actions trusted=github
@go-go-golems/os-scripting@0.1.3   publisher=GitHub Actions trusted=github
@go-go-golems/os-ui-cards@0.1.3    publisher=GitHub Actions trusted=github
@go-go-golems/os-confirm@0.1.1     publisher=GitHub Actions trusted=github
@go-go-golems/os-shell@0.1.1       publisher=GitHub Actions trusted=github
@go-go-golems/os-widgets@0.1.3     publisher=GitHub Actions trusted=github
@go-go-golems/os-kanban@0.1.4      publisher=GitHub Actions trusted=github
```

`os-repl@0.1.5` was skipped because it already existed, so that version still shows its original manual publisher. A future `os-repl@0.1.6` would prove Trusted Publishing for `os-repl` itself.

---

## 13. Current aligned public package stack

The current aligned public stack is:

```text
@go-go-golems/os-core@0.1.2
@go-go-golems/os-chat@0.1.1
@go-go-golems/os-repl@0.1.5
@go-go-golems/os-scripting@0.1.3
@go-go-golems/os-ui-cards@0.1.3
@go-go-golems/os-confirm@0.1.1
@go-go-golems/os-shell@0.1.1
@go-go-golems/os-widgets@0.1.3
@go-go-golems/os-kanban@0.1.4
```

The examples app now consumes this stack directly from npmjs. Its `package.json` was updated to the matching caret ranges, `npm install` resolved without peer conflicts, and local validation passed:

```bash
npm run build
npm run check:kanban-css
npm run test:e2e
```

The validation result was:

```text
Production build passed.
Kanban CSS selector check passed.
3 Playwright runtime regression tests passed.
```

This alignment was necessary because updating only a consumer app to `os-core@0.1.2` failed while older packages still depended on or peered against `os-core@0.1.1`:

```text
npm error ERESOLVE unable to resolve dependency tree
npm error Found: @go-go-golems/os-core@0.1.2
npm error Could not resolve dependency:
npm error peer @go-go-golems/os-core@"0.1.1" from @go-go-golems/os-widgets@0.1.2
```

The coordinated package releases fixed that class of conflict by rebuilding and publishing downstream packages with updated dependency metadata.

---

## 14. Release runbook

The release process is now documented in:

```text
ttmp/2026/05/11/npm-trusted-publishing-cicd--set-up-npmjs-trusted-publishing-ci-cd-for-public-packages/playbooks/01-npm-trusted-publishing-release-runbook.md
```

The single-package release flow is:

```bash
# 1. bump package version
# 2. update lockfile if needed
pnpm install --lockfile-only
pnpm install --frozen-lockfile

# 3. local validation
pnpm --filter @go-go-golems/os-core run typecheck
pnpm --filter @go-go-golems/os-core run test
pnpm --filter @go-go-golems/os-core run build:dist
node scripts/packages/pack-smoke.mjs packages/os-core
node scripts/packages/publish-npm-package-set.mjs --package packages/os-core --tag latest --dry-run

# 4. commit and push to main
# 5. run workflow dry-run
# 6. run real workflow publish with confirm_latest_publish=CONFIRM_LATEST
```

Verification can use npm directly now that local scope config is cleaned:

```bash
npm view @go-go-golems/os-core@0.1.2 version --registry=https://registry.npmjs.org/
```

For provenance details, the registry API remains useful because it exposes the trusted publisher fields:

```python
import json, urllib.request
pkg = '@go-go-golems/os-core'
ver = '0.1.2'
url = f"https://registry.npmjs.org/{pkg.replace('/', '%2F')}/{ver}"
with urllib.request.urlopen(url) as r:
    data = json.load(r)
print(data['_npmUser'])
```

---

## 15. Lessons from the finished pipeline

### Lesson 1: publishability is transitive

Publishing `os-core@0.1.2` was not enough. Packages that depended on or peered against `os-core@0.1.1` also needed patch releases. Frontend package systems often require coordinated publication even when the source change is metadata-only.

### Lesson 2: dry-runs and real OIDC publishes prove different things

Dry-runs validate package contents, scripts, and workflow setup. They do not prove npm accepts the OIDC identity. The first real publish is the only proof that Trusted Publishing is configured correctly.

### Lesson 3: CSS side effects require JS entrypoint preservation

Marking `**/*.css` as side-effectful is insufficient when the public theme export is a JS module that imports CSS. Public theme JS entrypoints must also be preserved.

### Lesson 4: local npm config can invalidate verification

A stale user-level scoped registry can make a correct package appear inaccessible. The pipeline should force npmjs in CI, and local development should keep the scope registry aligned with the intended public registry.

### Lesson 5: generated runtime source needs CI enforcement

The VM runtime packages depend on generated source-string modules. `check:vm-sources` now runs in CI and release workflows because stale generated modules would silently break published runtime packages.

### Lesson 6: an examples app is an integration test, not a marketing page

The examples workspace caught focus bugs, host notification provider mistakes, Vite raw-import packaging problems, and production CSS tree-shaking failures. It is part of the package quality system.

---

## 16. Important tickets and documents

### Package publication

```text
go-go-os-frontend/ttmp/2026/05/11/npm-widget-packages--extract-widgets-and-theme-packages-as-public-npm-packages
```

### VM raw source modules

```text
go-go-os-frontend/ttmp/2026/05/11/vm-raw-source-modules--generate-bundler-agnostic-vm-source-modules-for-published-runtime-packages
```

### Trusted Publishing CI/CD

```text
go-go-os-frontend/ttmp/2026/05/11/npm-trusted-publishing-cicd--set-up-npmjs-trusted-publishing-ci-cd-for-public-packages
```

Important files:

```text
.github/workflows/publish-npm.yml
.github/workflows/launcher-ci.yml
.github/workflows/publish-github-package-canary.yml
scripts/packages/build-dist.mjs
scripts/packages/generate-vm-source-modules.mjs
scripts/packages/package-sets.mjs
scripts/packages/pack-smoke.mjs
scripts/packages/publish-npm-package-set.mjs
pnpm-lock.yaml
```

### Examples app

```text
2026-05-11--npm-go-go-os-test/ttmp/2026/05/11/example-workspaces--build-progressive-example-workspaces-for-published-go-go-os-packages
```

Important files:

```text
playwright.config.ts
tests/e2e/runtime-stages.spec.ts
scripts/check-kanban-css.mjs
examples/shared/src/VmExampleHost.tsx
examples/06-repl-console
examples/08-vm-events-and-intents
examples/09-vm-kanban-runtime
```

---

## 17. Final consumer deployment

After the coordinated trusted-published package stack was available on npmjs, the public examples app was updated to consume it and redeployed. This closed the loop between package publication and external consumption.

The examples repo commit that updated the package stack was:

```text
6adb83f Use trusted-published go-go-os package stack
```

A later diary-only commit moved the examples repository head to:

```text
c363726 Diary: record examples package stack push
```

The static artifact workflow published:

```text
ghcr.io/go-go-golems/go-go-os-examples-static:sha-c36372695688
```

The K3s GitOps repo then updated the `go-go-os-examples` publish Job to that artifact. Deployment is Argo CD driven: Argo reconciles the `go-go-os-examples` Application, creates the new publish Job, the Job copies `/site` from the artifact image into the shared Caddy PVC, and Caddy serves the new release directory.

Final Argo CD state:

```text
go-go-os-examples   Synced   Healthy
static-sites-host   Synced   Healthy
```

Final publish Job:

```text
publish-go-go-os-examples-sha-c36372695688   Complete   1/1
```

The publish Job log confirmed the live release directory:

```text
/srv/sites/go-go-os-examples.yolo.scapegoat.dev/releases/sha-c36372695688/index.html
/srv/sites/go-go-os-examples.yolo.scapegoat.dev/releases/sha-c36372695688/assets/index-Bo0T2Qsq.css
/srv/sites/go-go-os-examples.yolo.scapegoat.dev/releases/sha-c36372695688/assets/index-C2LYUfLG.js
```

The final live browser smoke returned:

```json
{
  "title": "Go-Go OS1 Component Lab",
  "replFocused": true,
  "toastVisible": true,
  "kanban": {
    "kbDisplay": "flex",
    "boardDisplay": "flex",
    "boardOverflowX": "auto",
    "columnWidth": "200px",
    "hasKanbanCssRule": true
  },
  "errors": []
}
```

The live site is therefore serving the trusted-published package stack at:

```text
https://go-go-os-examples.yolo.scapegoat.dev/
```

## 18. What remains

The pipeline is complete enough to use. Remaining work is incremental hardening, not first-time setup.

1. Optionally publish a future `@go-go-golems/os-repl@0.1.6` through Trusted Publishing so every package has at least one trusted-provenance release. The current `os-repl@0.1.5` was skipped in the coordinated publish because it already existed.

2. Consider adding a clean install-smoke workflow that creates a temporary consumer project and installs the latest package stack from npmjs.

3. Add `PLAYWRIGHT_BASE_URL` support to the examples Playwright config so the same runtime tests can run against both local Vite and the deployed public site.

4. Consider path filters for the examples static artifact workflow so docs-only changes under `ttmp/**` do not build and publish a new image.

5. Monitor GitHub's Node 20 action deprecation warnings and upgrade action versions when upstream actions publish Node 24-compatible versions.

---

## Closing

The project is no longer only a successful manual npm publication. It is now a public frontend package system with an external consumer app, VM runtime examples, production deployment, browser regressions, generated-source checks, deterministic CI installs, and npmjs Trusted Publishing with provenance.

That changes the engineering standard for future work. A new package change can now be judged against concrete gates:

```text
source build -> dist artifact -> pack smoke -> npm Trusted Publishing -> external examples app -> production build -> browser regression -> Argo CD static-site deployment -> live browser smoke
```

The strongest result is that the package family now has external evidence. It can be installed from npmjs, composed in a separate React application, rendered in a public browser site, released again through a repeatable OIDC-based CI/CD pipeline, and redeployed through Argo CD as a static production site. That is the difference between a monorepo component collection and a frontend system.
