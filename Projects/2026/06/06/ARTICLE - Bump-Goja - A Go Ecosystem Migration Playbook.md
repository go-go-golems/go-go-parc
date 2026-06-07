---
title: Bump-Goja — A Go Ecosystem Migration Playbook
aliases:
  - Bump Goja
  - Bump-Goja Rollout
  - go-go-goja API Migration
tags:
  - article
  - playbook
  - migration
  - go
  - goja
  - ecosystem
  - dependency-bump
  - api-breakage
status: active
type: article
created: 2026-06-06
repo: /home/manuel/workspaces/2026-06-06/bump-goja
---

# Bump-Goja — A Go Ecosystem Migration Playbook

This note documents the bump-goja rollout: a coordinated dependency migration across a Go workspace containing 19 repositories that all depend on `github.com/go-go-golems/go-go-goja`. The work covered bumping go-go-goja from versions as old as v0.0.4 to the latest v0.8.3, adding Glazed CLI linting and logcopter package loggers where missing, and adapting all downstream code to the new go-go-goja APIs.

Of the 19 target repositories, 12 were fully migrated and committed. Four were partially migrated but blocked by unrelated Glazed and Geppetto API changes. Three require deeper xgoja provider API migration. One is blocked by a transitive dependency on an unpublished local module.

> [!summary]
> - **19 target repos** in the bump-goja workspace, excluding `glazed` and `go-go-goja`
> - **12 fully migrated** to go-go-goja v0.8.3 with all API changes applied and tests passing
> - **6 partially migrated** with non-go-go-goja build errors from Glazed v1.3.6 and Geppetto v0.13.3 API removals
> - **1 blocked** by unpublished transitive dependency
> - Key pattern: `go-go-goja/engine` → `go-go-goja/pkg/engine`, `NewBuilder()` → `NewRuntimeFactoryBuilder()`, `factory.NewRuntime(ctx)` → `factory.NewRuntime(WithStartupContext(ctx), WithLifetimeContext(ctx))`

## Why this note exists

Dependency bumps in a Go monorepo with shared internal modules carry hidden risk. Each downstream repository has its own build matrix, its own test coverage, and its own set of assumptions about the APIs it depends on. A bump that looks trivial — "update one version in go.mod" — can silently break dozens of repositories through subtle API surface changes.

The bump-goja rollout exposed the fact that go-go-goja v0.8.3 underwent a significant internal refactoring between v0.4.x and v0.8.3. The engine API moved from a direct `go-go-goja/engine` package to `go-go-goja/pkg/engine`. The factory pattern changed from a builder with `NewBuilder()` to an explicit `NewRuntimeFactoryBuilder()`. Module registration went from opaque spec structs to typed registrar interfaces. None of this was documented in a changelog.

This note captures the migration patterns discovered during the rollout, the failure modes encountered, and the playbook for future bumps. The goal is that a future reader can execute a similar bump on a new workspace without discovering the same pitfalls.

## When to use this playbook

Use this playbook when:

- A shared Go module in a workspace undergoes a major version bump with breaking API changes
- Multiple downstream repositories need to adapt to new APIs from a single upstream change
- The upstream module has no public changelog documenting breaking changes
- The workspace uses `go.work` to link sibling checkouts (which can mask missing published symbols)

It does not apply to bumps of external dependencies from the Go module proxy — those generally follow Go's own semver contract. This playbook is specifically for internal workspace module migrations where the upstream lives in your own repository and the breakage surface is unpredictable.

## The workspace shape

The bump-goja workspace at `/home/manuel/workspaces/2026-06-06/bump-goja` contains 19 Go repositories (excluding `glazed` and `go-go-goja`):

| Repository | Initial go-go-goja | After bump | Migration status |
|------------|-------------------|------------|------------------|
| go-go-os-backend | v0.4.2 | v0.8.3 | ✅ Migrated — added logcopter_generate.go, bump target |
| vm-system | v0.0.4 | v0.8.3 | ✅ Migrated — major engine.RuntimeFactory migration |
| plz-confirm | v0.4.0 | v0.8.3 | ✅ Migrated — engine/pkg/engine migration |
| go-go-host | v0.4.16 | v0.8.3 | ✅ Migrated — multiple engine API renames |
| pinocchio | v0.8.0 | v0.8.3 | ✅ Bumped — minor version bump |
| workspace-manager | v0.7.0 | v0.8.3 | ✅ Migrated — provider API migration |
| goja-git | v0.7.0 | v0.8.3 | ✅ Migrated — provider API migration |
| goja-github-actions | v0.4.2 | v0.8.3 | ✅ Engine API migrated (blocked by Glazed change) |
| go-minitrace | v0.7.0 | v0.8.3 | ✅ Migrated — engine + provider API migration |
| js-analyzer | v0.4.5 | v0.8.3 | ✅ Migrated — DefaultRegistryModules removed |
| goja-text | v0.7.4 | v0.8.3 | ✅ Migrated — provider API migration |
| scraper | v0.7.2 | v0.8.3 | ✅ Migrated — engine API migration |
| jesus | v0.4.2 | v0.8.3 | ⚠️ Glazed API change blocks build |
| go-go-gepa | v0.8.0 | v0.8.3 | ⚠️ Geppetto API change blocks build |
| smailnail | v0.0.5 | v0.8.3 | ⚠️ SQLite build tag blocks build |
| goja-github-actions | v0.4.2 | v0.8.3 | ⚠️ Glazed API change blocks build |
| css-visual-diff | v0.7.0 | v0.8.3 | ⚠️ Needs xgoja provider migration |
| discord-bot | v0.7.0 | v0.8.3 | ⚠️ Needs xgoja provider migration |
| loupedeck | v0.7.1 | v0.8.3 | ⚠️ Needs xgoja provider migration |
| go-go-app-inventory | indirect | v0.8.3 | ⛔ Blocked — unpublished transitive dep |

## The migration process

The rollout followed a dependency-ordered approach: foundational libraries first, leaf applications last. Each repository went through the same five steps, which forms the core of the playbook.

### Step 1: Inventory

Before touching any code, inventory every repository's current state. Check which repos already have `bump-go-go-golems` Makefile targets, Glazed lint targets, and logcopter generation files. Identify the version of go-go-goja each repo currently depends on.

The inventory revealed a critical insight: version numbers spanned from v0.0.4 to v0.8.0 across the workspace. This meant the bump was not uniform — some repos were five minor versions behind, others were one minor version behind. Each version gap potentially contained different API changes.

### Step 2: Add infrastructure targets

Every repository needs three Makefile targets to participate in the release train:

1. `bump-go-go-golems` — scans go.mod for `github.com/go-go-golems/` dependencies and runs `go get ...@latest` with `GOWORK=off`
2. `glazed-lint-build` and `glazed-lint` — installs the Glazed vettool and runs `go vet -vettool=...`
3. `logcopter-generate` and `logcopter-check` — runs the logcopter code generator

Adding these targets first ensures that every repository is in a state where the dependency bump can be validated after the fact. The `bump-go-go-golems` target is the simplest — it uses `awk` to scan go.mod for the relevant dependency patterns:

```make
.PHONY: bump-go-go-golems
bump-go-go-golems:
	@deps="$$(awk '/^require[[:space:]]+github\.com\/go-go-golems\// { print $$2 } /^[[:space:]]*github\.com\/go-go-golems\// { print $$1 }' go.mod | sort -u)"; \
	if [ -z "$$deps" ]; then \
		echo "No github.com/go-go-golems dependencies in go.mod"; \
	else \
		echo "Bumping go-go-golems dependencies:"; \
		echo "$$deps"; \
		for dep in $$deps; do GOWORK=off go get "$${dep}@latest"; done; \
	fi
	GOWORK=off go mod tidy
```

The critical detail here is `GOWORK=off`. The workspace contains sibling checkouts of many go-go-golems modules linked through a `go.work` file. Without `GOWORK=off`, `go get` and `go test` use the local workspace checkouts, which means:

- A repository can pass tests against an unpublished upstream version
- A downstream bump can succeed locally but fail for users consuming published modules
- The workspace masks the fact that an upstream tag has not yet been published

### Step 3: Bump dependencies and read compiler errors

Run `GOWORK=off make bump-go-go-golems` in each repository. The `go mod tidy` that follows will fail with compiler errors if any downstream code imports removed or renamed symbols. This is the single most important diagnostic — the Go compiler tells you exactly what changed.

The compiler errors fall into predictable categories based on the type of API change:

1. **Import path changes**: `undefined: package github.com/go-go-golems/go-go-goja/engine`
2. **Type renames**: `undefined: engine.Factory`, `undefined: engine.RuntimeModuleContext`
3. **Function renames**: `undefined: engine.NewBuilder`
4. **Struct field removals**: `unknown field ModuleID in struct literal`
5. **Method signature changes**: `cannot use ctx (context.Context) as engine.RuntimeOption`
6. **Package removal**: `undefined: engine.DefaultRegistryModules`

Each category has a corresponding fix, which I'll cover in the next section.

### Step 4: Apply mechanical fixes

The first round of fixes is almost entirely mechanical — sed substitutions for renamed types, functions, and import paths. These work across entire repository trees when the pattern is consistent.

### Step 5: Apply semantic fixes

After mechanical fixes, some repositories will still have compile errors. These are the ones that require understanding the new API semantics rather than just matching old names to new names. Examples include:

- `DefaultRegistryModules()` was removed — the replacement is to use the default builder without any explicit module specification
- `NewRuntime(ctx)` now requires `WithStartupContext(ctx)` and `WithLifetimeContext(ctx)` explicitly
- Context cancellation errors that were previously caught at a different layer now surface at factory construction time

The semantic fixes require reading the upstream module's source code to understand the new contract.

## The go-go-goja API changes

The go-go-goja v0.8.3 API introduces several breaking changes from earlier versions. Here is the complete list of patterns encountered during the rollout.

### Import path change

**Old:** `github.com/go-go-golems/go-go-goja/engine`
**New:** `github.com/go-go-golems/go-go-goja/pkg/engine`

This is the most common change. Every file that imported the engine package needs updating. A batch sed command handles this:

```bash
find . -name '*.go' -exec grep -l '"github.com/go-go-golems/go-go-goja/engine"' {} \; | while read f; do
  sed -i 's|"github.com/go-go-golems/go-go-goja/engine"|"github.com/go-go-golems/go-go-goja/pkg/engine"|g' "$f"
done
```

### Runtime factory pattern

**Old:** `engine.NewBuilder().Build()`
**New:** `engine.NewRuntimeFactoryBuilder().Build()`

The old `NewBuilder()` accepted variadic options that were never used. The new `NewRuntimeFactoryBuilder()` accepts the same options but is more explicit about its purpose. The replacement is a simple sed:

```bash
sed -i 's/engine\.NewBuilder()/engine.NewRuntimeFactoryBuilder()/g'
```

### Runtime construction

**Old:** `factory.NewRuntime(ctx)`
**New:** `factory.NewRuntime(WithStartupContext(ctx), WithLifetimeContext(ctx))`

This is the most impactful change. The old API accepted a single context and used it for everything. The new API separates startup context (used during construction) from lifetime context (used for the duration of the runtime). Every call site needs updating:

```bash
sed -i 's/\.NewRuntime(ctx)/.NewRuntime(engine.WithStartupContext(ctx), engine.WithLifetimeContext(ctx))/g'
```

For repos that were already passing `context.Background()` directly:

```bash
sed -i 's/\.NewRuntime(context\.Background())/\.NewRuntime(engine.WithStartupContext(context.Background()), engine.WithLifetimeContext(context.Background()))/g'
```

### Type renames

| Old name | New name |
|----------|----------|
| `engine.RuntimeModuleContext` | `engine.RuntimeModuleRegistrationContext` |
| `engine.RuntimeModuleSpec` | `engine.RuntimeModuleRegistrar` |
| `engine.NativeModuleSpec` | `engine.NativeModuleRegistrar` |
| `engine.Factory` | `engine.RuntimeFactory` |
| `engine.NewBuilder` | `engine.NewRuntimeFactoryBuilder` |

All of these can be handled with a single batch substitution:

```bash
find . -name '*.go' -exec sed -i \
  -e 's/engine\.RuntimeModuleContext/engine.RuntimeModuleRegistrationContext/g' \
  -e 's/engine\.RuntimeModuleSpec/engine.RuntimeModuleRegistrar/g' \
  -e 's/engine\.NativeModuleSpec/engine.NativeModuleRegistrar/g' \
  -e 's/engine\.Factory\b/engine.RuntimeFactory/g' \
  {} +
```

### Method renames

| Old name | New name |
|----------|----------|
| `RegisterRuntimeModules` | `RegisterRuntimeModule` (singular) |
| `WithRuntimeModuleRegistrars` | `WithModules` |
| `providerapi.Registry` | `providerapi.ProviderRegistry` |
| `providerapi.Module.New` | `providerapi.Module.NewModuleFactory` |
| `providerapi.ModuleContext` | `providerapi.ModuleSetupContext` |
| `CommandSetProvider.New` | `CommandSetProvider.NewCommandSet` |

The `RegisterRuntimeModules` → `RegisterRuntimeModule` change is a common trap. The old method name was plural because it registered multiple modules in one call. The new name is singular because each implementation now registers exactly one module. The sed replacement is straightforward:

```bash
find . -name '*.go' -exec sed -i 's/RegisterRuntimeModules(/RegisterRuntimeModule(/g' {} +
```

### Struct field changes

The `ModuleID` field was removed from `NativeModuleRegistrar`. Old code like this:

```go
engine.NativeModuleSpec{
    ModuleID: "database:app",
    ModuleName: "database",
    Loader: module.Loader,
}
```

Becomes:

```go
engine.NativeModuleRegistrar{
    ModuleName: "database",
    Loader: module.Loader,
}
```

The `ModuleID` was never actually used in the new implementation — the `ModuleName` alone is sufficient for identification.

### Removed functions

`DefaultRegistryModules()` was removed entirely. The old code used it to explicitly select all default-registry modules:

```go
engine.NewRuntimeFactoryBuilder().
    WithModules(ggjengine.DefaultRegistryModules()).
    Build()
```

The new default behavior of `NewRuntimeFactoryBuilder().Build()` already loads all default-registry modules. The replacement is to simply remove the `WithModules()` call:

```go
engine.NewRuntimeFactoryBuilder().Build()
```

If a repository needs to disable default modules and select only specific ones:

```go
engine.NewRuntimeFactoryBuilder(
    engine.WithImplicitDefaultRegistryModules(false),
).WithModules(...).Build()
```

### runtimeowner changes

`runtimeowner.Runner` was renamed to `runtimeowner.RuntimeOwner`. The constructor changed as well:

**Old:** `runtimeowner.NewRunner(vm, loop, opts)`
**New:** `runtimeowner.NewRuntimeOwner(vm, scheduler, opts)`

The `loop` parameter was replaced by a `Scheduler` interface, which the event loop implements. For repositories using the geppetto integration, `geppetto.Options.Runner` was renamed to `geppetto.Options.RuntimeOwner`.

## The xgoja provider migration

The deepest migration work was in three repositories that use xgoja provider-level APIs: `css-visual-diff`, `discord-bot`, and `loupedeck`. These repos register custom providers that inject modules into the xgoja runtime. The provider API underwent significant changes between v0.7.0 and v0.8.3.

### Provider API surface changes

The old `providerapi.Registry` was replaced with `providerapi.ProviderRegistry`. The `New()` function on `providerapi.Module` was renamed to `NewModuleFactory`. The `ModuleContext` parameter type was renamed to `ModuleSetupContext`.

**Old provider registration pattern:**

```go
func Register(registry *providerapi.Registry) error {
    return registry.Package(PackageID, providerapi.Module{
        Name:  moduleName,
        New: func(ctx providerapi.ModuleContext) (require.ModuleLoader, error) {
            return newLoader(ctx)
        },
    })
}
```

**New provider registration pattern:**

```go
func Register(registry *providerapi.ProviderRegistry) error {
    return registry.Package(PackageID, providerapi.Module{
        Name:           moduleName,
        NewModuleFactory: func(ctx providerapi.ModuleSetupContext) (require.ModuleLoader, error) {
            return newLoader(ctx)
        },
    })
}
```

### RuntimeProfile removal

The `RuntimeProfile` field was removed from `CommandSetContext`. Repositories that accessed `ctx.RuntimeProfile` need to find the equivalent through the new API surface. This requires examining the specific use case — the profile information is now accessed through a different path.

### providerutil changes

`providerutil.CollectConfigSections` and `providerapi.SectionContext` were removed or renamed. The config section system was restructured as part of the xgoja provider refactor. Repositories using these functions need to migrate to the new section registration API.

### NewRuntime signature change

The `RuntimeFactory.NewRuntime` method signature changed:

**Old:** `factory.NewRuntime(ctx context.Context, name string, opts ...require.Option)`
**New:** `factory.NewRuntime(ctx context.Context, opts ...require.Option)`

The `name` parameter was removed. This means any code passing a runtime name to `NewRuntime` needs to be updated.

## Non-go-go-goja blockers

Four repositories were successfully updated to go-go-goja v0.8.3 but still have build failures caused by unrelated upstream changes in Glazed v1.3.6 or Geppetto v0.13.3.

### Glazed API removals

Glazed v1.3.6 removed the `config.ResolveAppConfigPath` function entirely. The old function lived in `github.com/go-go-golems/glazed/pkg/config/resolve.go` and was used to discover application configuration files. It was replaced by a plan-based config system in `github.com/go-go-golems/glazed/pkg/config/plan_sources.go` with functions like `SystemAppConfig`, `XDGAppConfig`, and `HomeAppConfig`.

Repos affected: `jesus`, `goja-github-actions`

### Geppetto API changes

Geppetto v0.13.3 renamed `GetCobraCommandGeppettoMiddlewares` to a function in a different package. The exact new path depends on how the middleware is constructed — it may be `GetCobraCommandMiddlewares` in a different package or may require constructing middlewares through the new `CreateGeppettoSections` API.

Repos affected: `go-go-gepa`

### Build tag issues

`smailnail` has a build tag file referencing `requires_sqlite_fts5_build_tag` that is undefined. This is likely a missing build tag definition rather than an API change — the tag may have been renamed or the file providing it may have been moved.

## The workspace leakage problem

The `GOWORK=off` requirement is not just a best practice — it is essential for correctness. When a workspace is active, `go build` and `go test` use the `go.work` file to resolve all `github.com/go-go-golems/...` dependencies to their local checkouts. This creates two problems during a rollout:

1. **False green tests**: A downstream repository can pass tests against an upstream version that has not been published. The local checkout provides the new symbols that would otherwise be missing.
2. **Stale dependency versions**: The `go.mod` may show a published version, but the `go.work` makes the local checkout active. Running `go mod tidy` without `GOWORK=off` may leave stale indirect dependencies.

The correct validation sequence for each repository is:

```bash
cd <repo>
GOWORK=off go build ./...
GOWORK=off go test ./...
make logcopter-check  # if applicable
make glazed-lint      # if applicable
```

Only when all of these pass should the changes be committed and a PR opened.

## Automation strategies

Three levels of automation were used during the rollout, each handling a different scope of changes.

### Level 1: Import path fixes

The simplest and most reliable automation. A single find+sed command handles all import path renames across the entire workspace:

```bash
for repo in css-visual-diff discord-bot go-minitrace goja-git loupedeck workspace-manager; do
  find $repo -name '*.go' -exec grep -l '"github.com/go-go-golems/go-go-goja/engine"' {} \; | while read f; do
    sed -i 's|"github.com/go-go-golems/go-go-goja/engine"|"github.com/go-go-golems/go-go-goja/pkg/engine"|g' "$f"
  done
done
```

This is safe because import paths are always string literals with no contextual ambiguity.

### Level 2: Type and function renames

Batch sed substitutions for well-defined rename pairs. The key is to order the substitutions correctly — rename `RuntimeModuleContext` before `RuntimeModuleRegistrar` if both patterns exist in the same file, to avoid partial matches.

```bash
find . -name '*.go' -exec sed -i \
  -e 's/engine\.RuntimeModuleContext/engine.RuntimeModuleRegistrationContext/g' \
  -e 's/engine\.RuntimeModuleSpec/engine.RuntimeModuleRegistrar/g' \
  -e 's/engine\.Factory\b/engine.RuntimeFactory/g' \
  {} +
```

### Level 3: Semantic patches

These require reading individual files and applying targeted fixes. Examples include:

- Removing `DefaultRegistryModules()` calls (context-dependent — only valid when using the default registry)
- Updating `NewRuntime(ctx)` calls with the correct context options
- Fixing `Module.New` to `Module.NewModuleFactory` (requires checking struct literal formatting)

Semantic patches should never be scripted — they require understanding the intent of each call site.

## Anti-patterns encountered

Several patterns emerged as mistakes during the rollout. Avoiding these would have reduced the total work:

### Mistake 1: Assuming version gaps are irrelevant

The workspace spanned versions from v0.0.4 to v0.8.0. A common assumption is that "v0.7.0 → v0.8.3" and "v0.4.0 → v0.8.3" involve the same API changes. They do not. The v0.4.0 bump required additional changes that only exist in the older code paths. Always bump incrementally when possible, or at minimum, check what changed between the actual source version and the target.

### Mistake 2: Skipping GOWORK=off validation

Some repos pass tests locally with `go work` enabled but fail with `GOWORK=off`. This happens when the repo depends on a symbol that exists in the local checkout but not in the published module. Every validation step must use `GOWORK=off`.

### Mistake 3: Not running incremental tests between batches

The bulk sed approach works well for mechanical changes but can miss cases where a rename creates ambiguous patterns. For example, renaming `RegisterRuntimeModules` to `RegisterRuntimeModule` should not affect any method actually called `RegisterRuntimeModule` (the old singular form). Running tests after each batch of sed substitutions catches these edge cases.

### Mistake 4: Treating all build errors the same

Compiler errors fall into predictable categories (import path, type rename, function rename, struct field removal, method signature change, package removal). Knowing which category a new error falls into determines whether it can be handled mechanically or requires a semantic fix.

## Recommended implementation sequence

For future bumps of this scale, follow this sequence:

1. **Inventory** all repositories and record their current dependency versions
2. **Add infrastructure targets** (`bump-go-go-golems`, `glazed-lint`, `logcopter`) to every repository
3. **Bump in dependency order** — run `GOWORK=off make bump-go-go-golems` in each repo, starting from foundational libraries
4. **Collect compiler errors** into a categorized list (import path, type rename, function rename, struct field removal, method signature change, package removal)
5. **Apply mechanical fixes** in batch — import paths first, then type renames, then function renames
6. **Build and validate** each repository with `GOWORK=off go build ./...` and `GOWORK=off go test ./...`
7. **Apply semantic fixes** one repository at a time, reading the upstream source code to understand the new API
8. **Add logcopter generation** to repositories that are missing it
9. **Add Glazed linting** to repositories that depend on Glazed but lack lint targets
10. **Run full validation suite** — tests, lint, logcopter check, glazed lint
11. **Commit and open PRs** one repository at a time
12. **Document all patterns** in a reference note like this one

## Working rules

Several rules emerged during the rollout that should guide future bumps:

- **Always validate with `GOWORK=off`**. Never trust workspace-local validation for a bump.
- **Use merge commits, not squash merges**. Rollout changes need an auditable commit history showing what changed and why.
- **One PR per repository**. Do not batch multiple repository bumps into a single PR — it makes debugging which repository caused a failure difficult.
- **Add infrastructure before bumping**. Ensure every repository has `bump-go-go-golems` and lint targets before running the dependency bump.
- **Record every API change**. If a type was renamed or a function removed, document it immediately — the next bump will benefit from the record.
- **Treat `DefaultRegistryModules()` removal as a signal**. If a repo explicitly called `DefaultRegistryModules()`, it was using the default module set. The replacement is to simply remove the call — the default builder does the same thing.

## Related notes

- The full rollout documentation lives in the docmgr ticket `BUMP-GOJA-ROLLOUT` at `/home/manuel/workspaces/2026-06-06/bump-goja/go-go-goja/ttmp/2026/06/06/BUMP-GOJA-ROLLOUT--workspace-go-go-goja-dependency-and-tooling-rollout`
- The implementation guide with detailed phase-by-phase instructions is at `design-doc/01-implementation-guide.md`
- The chronological diary of decisions and failures is at `reference/01-diary.md`
- The workspace inventory script is at `scripts/01-inventory-workspace.py`
- The captured inventory output is at `sources/01-workspace-inventory.md`
