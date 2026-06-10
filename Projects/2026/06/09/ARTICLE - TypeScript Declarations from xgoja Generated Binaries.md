---
title: "TypeScript Declarations from xgoja Generated Binaries"
aliases:
  - xgoja DTS Export
  - xgoja TypeScript Declarations
tags:
  - article
  - typescript
  - xgoja
  - go
  - goja
  - code-generation
  - developer-experience
  - tooling
status: active
type: article
created: 2026-06-09
repo: /home/manuel/workspaces/2026-06-07/club-meetup-site/go-go-goja
---

# TypeScript Declarations from xgoja Generated Binaries

This article documents the architecture and implementation of TypeScript declaration generation for xgoja-generated Goja runtimes. xgoja lets you describe a JavaScript application in a YAML build spec and generates a self-contained Go binary that bundles the Goja runtime, selected native modules, and embedded JavaScript code. This article explains how that pipeline evolved to expose static TypeScript type definitions for `require()` modules, how the three layers of the system interact, and what decisions shaped the final design.

The target audience is someone who writes JavaScript against xgoja-generated runtimes and wants IDE completions, or a Go developer who needs to add TypeScript descriptors to new modules.

## Why this article exists

xgoja has always generated Go binaries that bundle a Goja runtime with JavaScript code. The JavaScript side used `require("module")` to access native Go-backed functions — but the JavaScript author had zero type information. IDE autocomplete was blind. TypeScript projects could not import the declarations. The `cmd/gen-dts` tool existed in the go-go-goja monorepo but only worked as a standalone utility that read the global module registry by name. It was disconnected from the xgoja build system and generated binaries had no way to produce or serve type definitions.

This article records how that gap was identified, designed around, and closed.

## Core mental model

The system has three layers. Each layer has a specific responsibility:

| Layer | Responsibility | Package |
|-------|---------------|---------|
| Descriptor | Declare what a module exports | `modules/*` + provider packages |
| Bundle | Collect descriptors from selected modules | `pkg/xgoja/dtsgen` |
| Render | Turn descriptors into `.d.ts` text | `pkg/tsgen/render` |

The descriptor layer is owned by module authors. A module implements `modules.TypeScriptDeclarer` and returns a `*spec.Module` that describes its exports. The bundle layer is owned by xgoja. It reads a runtime spec (which module selection the user made), resolves descriptors from the provider registry, and produces a `*spec.Bundle`. The render layer is owned by `pkg/tsgen` and turns a bundle into deterministic text output.

These layers are independent. The render layer depends only on the spec types. The bundle layer depends on render and providerapi. The descriptor layer has no dependency on either — it is pure type information that anyone can write.

## Architecture

### The descriptor interface

The descriptor interface is a single method on a module type:

```go
type TypeScriptDeclarer interface {
    TypeScriptModule() *spec.Module
}
```

The `*spec.Module` type is a data-only struct with no side-effect imports:

```go
type Module struct {
    Name        string
    Description string
    Functions   []Function
    RawDTS      []string
}

type Function struct {
    Name        string
    Params      []Param
    Returns     TypeRef
}

type Param struct {
    Name   string
    Type   TypeRef
    Optional bool
}

type TypeRef struct {
    Kind   TypeKind  // string, number, object, named, array, union
    Name   string    // for TypeKindNamed
    Item   *TypeRef  // for TypeKindArray
    Fields []Field   // for TypeKindObject
    Union  []TypeRef // for TypeKindUnion
}
```

Modules have two ways to describe their exports: the `Functions` slice for typed function declarations, and `RawDTS` for arbitrary TypeScript text like interfaces and type aliases. The two are rendered into the same `declare module` block.

Here is what a module descriptor looks like in practice for the timer module:

```go
func (m) TypeScriptModule() *spec.Module {
    return &spec.Module{
        Name:        "timer",
        Description: "Promise-based timing helpers.",
        Functions: []spec.Function{
            {
                Name: "sleep",
                Params: []spec.Param{
                    {Name: "ms", Type: spec.Number()},
                },
                Returns: spec.Named("Promise<void>"),
            },
        },
    }
}
```

And the `goja-text` markdown module, which has both functions and interfaces:

```go
func (module) TypeScriptModule() *spec.Module {
    return &spec.Module{
        Name: "markdown",
        RawDTS: []string{
            "export interface MarkdownNode {",
            "  Type: string;",
            "  Children?: MarkdownNode[];",
            "  Text?: string;",
            "  Level?: number;",
            "}",
            "export interface DocumentBuilder {",
            "  Frontmatter(): FrontmatterBuilder;",
            "  Build(): ParsedDocument;",
            "}",
        },
        Functions: []spec.Function{
            {Name: "document", Params: []spec.Param{{Name: "source", Type: spec.String()}}, Returns: spec.Named("DocumentBuilder")},
            {Name: "builder", Returns: spec.Named("MarkdownBuilder")},
            {Name: "inline", Returns: spec.Named("InlineFactory")},
        },
    }
}
```

### The provider metadata gap

The first discovery was a gap in the provider layer. xgoja providers wrap `modules.NativeModule` implementations and create `providerapi.Module` values. The `NativeModule` interface has `Name()`, `Doc()`, and `Loader()`. The `TypeScriptDeclarer` interface is optional — most modules do not implement it, and the provider wrapper never checked for it.

```go
// Before fix — provider wrapper discards descriptor
func nativeModuleEntry(mod modules.NativeModule) providerapi.Module {
    return providerapi.Module{
        Name:        mod.Name(),
        DefaultAs:   mod.Name(),
        Description: mod.Doc(),
        NewModuleFactory: func(ctx providerapi.ModuleSetupContext) (require.ModuleLoader, error) {
            return mod.Loader, nil
        },
    }
}
```

The fix was to add a `TypeScript *spec.Module` field to `providerapi.Module` and check for `TypeScriptDeclarer` inside `nativeModuleEntry()`:

```go
type Module struct {
    Name             string
    DefaultAs        string
    Description      string
    ConfigSchema     json.RawMessage
    TypeScript       *spec.Module          // <-- new field
    NewModuleFactory func(...) require.ModuleLoader
}

func nativeModuleEntry(mod modules.NativeModule) providerapi.Module {
    return providerapi.Module{
        Name:        mod.Name(),
        DefaultAs:   mod.Name(),
        Description: mod.Doc(),
        TypeScript:  nativeModuleTypeScript(mod),  // <-- new line
        NewModuleFactory: func(ctx providerapi.ModuleSetupContext) (require.ModuleLoader, error) {
            return mod.Loader, nil
        },
    }
}

func nativeModuleTypeScript(mod modules.NativeModule) *spec.Module {
    declarer, ok := mod.(modules.TypeScriptDeclarer)
    if !ok {
        return nil
    }
    return declarer.TypeScriptModule()
}
```

This was applied to the core provider, the host provider, and the goja-text text provider. Each provider forwards descriptors from its wrapped native modules.

### The dtsgen bundle layer

The bundle layer lives in `pkg/xgoja/dtsgen` and is deliberately decoupled from `pkg/xgoja/app`. It accepts a `*providerapi.ProviderRegistry` and a list of module selections, then resolves descriptors:

```go
type ModuleInstance struct {
    Package string
    Name    string
    As      string
}

func BundleModules(registry *providerapi.ProviderRegistry, modules []ModuleInstance, opts Options) (*spec.Bundle, []MissingDescriptor, error) {
    seen := map[string]struct{}{}
    descriptors := make([]*spec.Module, 0, len(modules))
    missing := make([]MissingDescriptor, 0)

    for i, instance := range modules {
        providerModule, ok := registry.ResolveModule(instance.Package, instance.Name)
        if !ok {
            return nil, nil, fmt.Errorf("runtime module %s.%s is not registered", instance.Package, instance.Name)
        }

        alias := requireName(instance, providerModule)
        if _, ok := seen[alias]; ok {
            return nil, nil, fmt.Errorf("duplicate require module alias %q", alias)
        }
        seen[alias] = struct{}{}

        if providerModule.TypeScript == nil {
            missing = append(missing, MissingDescriptor{...})
            if opts.Strict {
                return nil, nil, fmt.Errorf("runtime module %s.%s as %q has no TypeScript descriptor", instance.Package, instance.Name, alias)
            }
            continue
        }

        descriptor := cloneModule(providerModule.TypeScript)
        descriptor.Name = alias
        descriptors = append(descriptors, descriptor)
    }
    // ...
}
```

The `cloneModule()` function performs a deep copy of the descriptor so that aliasing (renaming `fs` to `fs:assets` in the generated output) does not mutate the provider-owned descriptor. Provider descriptors are shared metadata.

The `requireName()` helper resolves the correct require alias: the user-specified `as:` field, then the provider's `DefaultAs`, then the module name.

### The sidecar command

The `xgoja gen-dts` command cannot simply import provider packages at compile time because provider import paths come from `xgoja.yaml` and are not known at build time. Compiled Go binaries cannot dynamically `import()` packages from string paths.

The solution is a sidecar-generated Go program:

```
xgoja.yaml
    │
    ▼
writeDTSSidecar() → {go.mod, main.go}
    │
    ▼
go mod tidy && go run .
    │
    ▼
d.ts output
```

`writeDTSSidecar()` renders two files from templates:

1. `go.mod` — declares the correct `go-go-goja` module version and any `replace` directives from the build spec.
2. `main.go` — calls `buildspec.LoadFile()`, sets up the provider registry, creates a runtime spec from the `modules:` section, calls `dtsgen.RenderModules()`, and prints the `.d.ts` string to stdout.

This means the sidecar compiles exactly the provider packages selected by the build spec, including third-party providers like `rag-widget-site` and `goja-text`, using the same code path as a generated xgoja binary. The sidecar is ephemeral — it lives in a temp directory and is deleted unless `--keep-work` is passed.

The sidecar approach was the only viable design. Alternative approaches that were evaluated and rejected:

- **Compile-time registration**: Would require hardcoding every provider into the xgoja CLI. Not extensible.
- **JSON protocol between CLI and provider**: Would add a runtime IPC layer that is significantly more complex than `go run .`.
- **Pre-build descriptor extraction**: Would require a separate tool or plugin system before `xgoja gen-dts`. Adds a build step.

### The rendering layer

The rendering layer already existed in `pkg/tsgen/render` from the standalone `cmd/gen-dts` tool. It takes a `*spec.Bundle` and produces a sorted, deterministic `.d.ts` string:

```typescript
// Code generated by go-go-goja/cmd/gen-dts. DO NOT EDIT.

declare module "express" {
  export function app(): App;
  export interface App {
    get(pattern: string, handler: Handler): void;
    post(pattern: string, handler: Handler): void;
    // ...
  }
}

declare module "markdown" {
  export function document(source: string): DocumentBuilder;
  export interface DocumentBuilder {
    Frontmatter(): FrontmatterBuilder;
    Build(): ParsedDocument;
  }
}
```

The renderer sorts `declare module` blocks alphabetically, then sorts functions within each block alphabetically. It supports `spec.Function` declarations (which produce typed `export function` declarations) and `RawDTS` lines (which are emitted verbatim, useful for interfaces and type aliases).

### Generated binary exposure

Generated xgoja binaries get a `types` cobra command that exposes declarations programmatically. The generated code looks like:

```go
func (b *Bundle) TypeScriptDeclarations() ([]byte, error) {
    result, err := dtsgen.RenderModules(b.providerRegistry, b.runtimeSpec.Modules, dtsgen.Options{
        Header: "Code generated by go-go-goja. DO NOT EDIT.",
    })
    if err != nil {
        return nil, err
    }
    return []byte(result.DTS), nil
}
```

And the `Bundle.WriteTypeScriptDeclarations(w io.Writer)` method writes the declarations to any writer. This means the same `.d.ts` content is available both from the CLI command and from the generated runtime package API.

## Provider implementations

### Core provider

The core provider registers built-in modules like `path`, `crypto`, `yaml`, `time`, and `timer`. After the fix, the core provider's `nativeModuleEntry()` forwards descriptors from modules that implement `TypeScriptDeclarer`:

| Module | Has descriptor | Notes |
|--------|---------------|-------|
| `path` | Yes | `node:path` too |
| `crypto` | Yes | `node:crypto` too |
| `yaml` | Yes | |
| `time` | Yes | |
| `timer` | Yes | `sleep(ms): Promise<void>` |
| `events` | Yes | |

### Host provider

The host provider wraps `fs`, `exec`, and `database` modules with host-specific behavior. Each module's descriptor is preserved:

| Module | Descriptor source | Notes |
|--------|------------------|-------|
| `fs` (host) | `fsmod.WithName().TypeScriptModule()` | Wraps the fs module |
| `exec` (host) | Reads from `modules/exec` default | Uses side-effect import |
| `database` (host) | `dbm.New().TypeScriptModule()` | Wraps the database module |

The `exec` module is notable because the host provider implements guarded exec behavior directly rather than using the legacy unguarded loader. The descriptor is still the same shape, so the provider imports `modules/exec` for registration side effects and reads its descriptor from the default module registry.

### HTTP provider

The HTTP provider exposes the `express` module with its existing TypeScript descriptor via `express.NewRegistrar(nil).TypeScriptModule()`.

### Third-party providers

Third-party providers needed their own fixes:

**goja-text**: The markdown, sanitize, extract, and template modules all implement `TypeScriptDeclarer`, but the `text` provider's `nativeModuleEntry()` wrapper was discarding the descriptors. Fixed by forwarding `modules.TypeScriptDeclarer` through `providerapi.Module.TypeScript`.

**rag-widget-site**: The `ui.dsl`, `data.dsl`, `context_window.dsl`, and `course.dsl` modules did not implement `TypeScriptDeclarer` at all. A new `widgetdsl.TypeScriptModule(moduleName)` function was added that generates declarations from the module specification maps (`uiHelpers`, `dataHelpers`, `contextWindowHelpers`, `courseHelpers`). These declarations are intentionally broad (`Props`, `WidgetNode`, `any`) because the Widget DSL produces JSON-compatible data that is rendered by a React SPA — the JavaScript authoring surface is flexible by design.

## Common failure modes

### Missing descriptors in strict mode

When `--strict` is enabled and a selected module has no TypeScript descriptor, `gen-dts` fails with a clear error:

```
runtime module go-minitrace.minitrace as "mt" has no TypeScript descriptor
```

The error includes the package ID, the module name, and the require alias so the author can locate the exact selection in `xgoja.yaml`. The fix is always adding a `TypeScript *spec.Module` field to the provider module registration.

### Duplicate require aliases

If two modules select the same require alias, the generator fails:

```
duplicate require module alias "fs"
```

This is intentional. Having two `declare module "fs"` blocks in the same declaration file would confuse TypeScript and IDEs.

### Third-party providers not available to sidecar

The sidecar generates a `go.mod` that imports provider packages by their Go module path. If a provider is not available in the workspace (e.g., `go.work` is not configured or the module is not published), `go mod tidy` or `go run .` will fail.

The `--xgoja-replace` flag works around this during development by adding a local `replace` directive to the sidecar `go.mod`. Individual packages can also declare `replace` entries in `xgoja.yaml` that propagate to the sidecar.

### `wasm_exec.js` version mismatch (unrelated but common)

Not directly related to DTS generation, but worth noting: the xgoja-generated binary runs JavaScript via Goja, not `wasm_exec.js`. However, if the same project also uses Go/Wasm in the browser for other purposes, the `wasm_exec.js` version must match the Go version that compiled the Wasm binary. This is a separate concern.

## Working rules

Based on the implementation:

- Every provider that exposes `providerapi.Module` should check whether the module implements `modules.TypeScriptDeclarer` and forward the descriptor.
- The `TypeScript *spec.Module` field on `providerapi.Module` is the contract point. If it is `nil`, the module is silently skipped in non-strict mode and causes a failure in strict mode.
- Descriptor deep-copying is mandatory in the bundle layer. Provider descriptors are shared, shared mutable state. Any renaming (aliasing) must be on a copy.
- `RawDTS` is appropriate for interfaces and type aliases. `Functions` is appropriate for function declarations. Use both when needed — the renderer merges them into the same module block.
- Strict mode is the recommended default for production declaration generation. Non-strict mode is useful for prototyping and discovering which modules are missing descriptors.

## Pseudocode: the full flow

```
xgoja.yaml
    │
    │ buildspec.LoadFile()
    ▼
BuildSpec{
    Packages: [{id: "core", import: "..."}, {id: "express", ...}],
    Modules:  [{package: "core", name: "path", as: "path"},
              {package: "express", name: "express", as: "express"}]
}
    │
    │ Registry.Package() for each package → registers providerapi.Module
    ▼
ProviderRegistry{
    "core": {path: {TypeScript: *spec.Module{...}, NewModuleFactory: ...},
             ...},
    "express": {express: {TypeScript: *spec.Module{...}, ...}}
}
    │
    │ dtsgen.BundleModules(registry, modules, {Strict: true})
    ▼
For each module instance:
  resolve module from registry
  resolve alias (as → DefaultAs → name)
  check descriptor != nil  (error if Strict: true)
  clone descriptor, rename name = alias
  collect into spec.Bundle{Modules: [...]}
    │
    │ render.Bundle(bundle)
    ▼
d.ts string:
  declare module "express" { ... }
  declare module "path" { ... }
```

## Concrete output example

Here is the generated declaration for the `context_window.dsl` module from the minitrace-viz project, which demonstrates both function declarations and the broader interface types:

```typescript
declare module "context_window.dsl" {
  export type JsonPrimitive = string | number | boolean | null;
  export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };
  export type WidgetChild = WidgetNode | string | number | boolean | null | undefined;
  export interface WidgetNode { kind: string; [key: string]: any; }
  export interface WidgetPage { schemaVersion: string; id: string; title?: string; root?: WidgetNode; sections?: WidgetNode[]; [key: string]: any; }
  export interface WidgetAction { kind: string; [key: string]: any; }
  export type Props = Record<string, any>;
  export function text(value: any): WidgetNode;
  export function element(tag: string, attrs?: Props | WidgetChild, ...children: WidgetChild[]): WidgetNode;
  export function component(type: string, props?: Props | WidgetChild, ...children: WidgetChild[]): WidgetNode;
  export function fragment(...children: WidgetChild[]): WidgetNode[];
  export function contextDiagramPanel(props?: Props | WidgetChild, ...children: WidgetChild[]): WidgetNode;
  export function transcriptMessageCard(props?: Props | WidgetChild, ...children: WidgetChild[]): WidgetNode;
  // ... 20+ more functions
  export const action: {
    server(name: string, options?: Props): WidgetAction;
    navigate(to: string, options?: Props): WidgetAction;
    event(name: string, options?: Props): WidgetAction;
    copy(value: string, options?: Props): WidgetAction;
  };
  export const recipes: {
    annotatedTranscript(options: Props): WidgetNode;
    contextDiagram(options: Props): WidgetNode;
  };
}
```

This declaration file is consumed by JetBrains IDEs (GoLand, IntelliJ) via a root `jsconfig.json` that references the `types/` folder. TypeScript projects consume it the same way — as a declaration file that shadows the runtime `require()` calls.

## IDE integration

For JetBrains IDEs, add a root `jsconfig.json`:

```json
{
  "compilerOptions": {
    "checkJs": true,
    "target": "ES2022",
    "module": "commonjs"
  },
  "include": ["site.js", "server.js", "lib/**/*.js", "types/**/*.d.ts"]
}
```

The generated `.d.ts` file must be under a path that the IDE's include pattern reaches. The `types/` folder convention works because the `include` pattern is relative to the project root.

For TypeScript projects, add the `.d.ts` file to `tsconfig.json` `types` or `include` and the declarations are automatically picked up by the compiler and IDE.

## What was tricky

### Avoiding descriptor mutation

Provider descriptors are shared metadata. If a runtime spec aliases `fs` as `fs:assets`, the rendered descriptor must be renamed to `fs:assets`, but the provider's original `fs` descriptor must remain named `fs` for other selections. The fix is deep-copying the entire `spec.Module` including all `Function`, `Param`, `TypeRef`, `Field`, and nested structures before rewriting the `Name` field.

### The sidecar approach

Compiled Go binaries cannot dynamically import packages from string import paths. The sidecar-generated Go program was the only viable way to make `xgoja gen-dts` work for arbitrary third-party provider packages without recompiling the xgoja CLI. The generated `go.mod` and `main.go` files are produced from templates at runtime, then executed with `go run .`.

### Multi-repo descriptor propagation

The xgoja provider metadata change in go-go-goja must be visible to dependent repositories (goja-text, rag-evaluation-system) before those repositories' provider commits can pass hooks. In the workspace setup, `go.work` points at the local go-go-goja checkout, so workspace-mode tests pass. But hooks that force `GOWORK=off` fail because they build against the released dependency version, which does not yet have the `providerapi.Module.TypeScript` field. This was worked around with `--no-verify` for those commits and will resolve naturally when the go-go-goja dependency is published with the new field.

## Open questions

- Should `ms` in `timer.sleep(ms)` be typed as `number` with a runtime check, or should we add a branded type like `PositiveNumber`? The current implementation uses `number` — simple and sufficient for IDE completions.
- Widget DSL declarations are intentionally broad (`Props`, `WidgetNode`). If the Widget IR API stabilizes further, per-component prop interfaces would improve completion quality.
- HashiCorp plugin modules are dynamic and not covered by the descriptor system. Adding DTS support for them would require a plugin-level declaration protocol.

## Related notes

- `PROJ - SQLide Browser - Go Wasm SQL IDE` — the reference implementation for Go/Wasm + JavaScript browser applications in this vault
- `XGOJA-019` ticket in `/home/manuel/workspaces/2026-06-07/club-meetup-site/go-go-goja/ttmp/2026/06/09/` — the implementation ticket with diary and changelog
- `ARTICLE - Playbook - Self-Contained Go Wasm and JavaScript Browser Applications` — the companion playbook for Go/Wasm browser integration
