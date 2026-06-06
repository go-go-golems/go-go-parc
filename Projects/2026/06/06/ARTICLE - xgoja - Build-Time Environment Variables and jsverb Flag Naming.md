---
title: "xgoja - Build-Time Environment Variables and jsverb Flag Naming"
aliases:
  - "xgoja go env"
  - "xgoja build env"
  - "xgoja jsverb field naming"
tags:
  - article
  - xgoja
  - javascript
  - build-system
status: active
type: article
created: 2026-06-06
---

# xgoja - Build-Time Environment Variables and jsverb Flag Naming

This article documents two changes made to xgoja during the goja-bleve vector search project: support for build-time environment variables in xgoja specs, and normalization of JavaScript verb field names from camelCase/snake_case to kebab-case CLI flags. Both changes address practical gaps that blocked concrete use cases—FAISS-linked Bleve builds and idiomatic command-line interfaces.

> [!summary]
> 1. xgoja now supports `go.env` in `xgoja.yaml` for build-time environment variables such as `CGO_LDFLAGS`, enabling FAISS-linked binaries without shell-dependent build invocations.
> 2. Top-level JavaScript verb parameters and fields now expose kebab-case CLI flags (`--profile-path` for `profilePath`) while preserving original parameter names at invocation.

## Why This Article Exists

The goja-bleve project required building Bleve with the `vectors` build tag and linking against FAISS. Bleve's vector search implementation uses CGO, and the required linker flags (`-lfaiss_c -lfaiss -lstdc++ -lm`) are too specific to bake into `ldflags`. Prior to the `go.env` change, vector-enabled xgoja builds still depended on manually exporting `CGO_LDFLAGS` in the shell. The build spec had `tags` and `ldflags` but no mechanism for build-time environment variables.

Separately, when building the RAG indexing tool, verb field names like `profilePath` were exposed literally as `--profilePath`, producing command lines that do not match the idiomatic kebab-case used throughout the Glazed ecosystem. The jsverb subsystem already normalized command names through `cleanCommandWord`, which converts camelCase to kebab-case. Field names received no such treatment.

Both gaps were closed with focused changes to `go-go-goja`.

## Build-Time Environment Variables

### The Problem

xgoja generates Go code that calls `go build` with configurable `tags` and `ldflags`:

```yaml
go:
  tags:
    - vectors
  ldflags:
    - -r
    - /usr/local/lib
```

This works for most cases. It does not work when the build requires environment variables. Bleve's vector search implementation is a concrete example:

```yaml
go:
  tags:
    - vectors
  ldflags:
    - -r
    - /usr/local/lib
  env:
    CGO_LDFLAGS: "-L/usr/local/lib -lfaiss_c -lfaiss -lstdc++ -lm"
```

The `CGO_LDFLAGS` variable controls the C linker flags that CGO passes to the system linker. Without it, `go build -tags=vectors` produces a binary that links against Bleve's vector code but fails at runtime because FAISS symbols are unresolved.

The build environment variable is a `go` build detail, not a runtime concern. It does not affect the JavaScript module surface or the runtime behavior of the generated binary. It is a pure build-time concern.

### How It Was Added

The xgoja build spec schema gains a new field in `GoSpec`:

```go
type GoSpec struct {
    Version string            `yaml:"version" json:"version"`
    Module  string            `yaml:"module" json:"module"`
    Tags    []string          `yaml:"tags" json:"tags,omitempty"`
    LDFlags []string          `yaml:"ldflags" json:"ldflags,omitempty"`
    Env     map[string]string `yaml:"env" json:"env,omitempty"`
    Imports []GoImportSpec    `yaml:"imports" json:"imports,omitempty"`
}
```

The build execution layer threads this field through `buildexec.GoBuild`:

```go
func GoBuild(ctx context.Context, dir string, output string, tags []string, ldflags []string, env map[string]string) (Result, error) {
    // ... build args construction ...
    return run(ctx, dir, env, "go", args...)
}
```

The `run` function appends the env map entries to `os.Environ()` before executing the command:

```go
func run(ctx context.Context, dir string, env map[string]string, name string, args ...string) (Result, error) {
    cmd := exec.CommandContext(ctx, name, args...)
    cmd.Dir = dir
    if len(env) > 0 {
        cmd.Env = append(os.Environ(), sortedEnv(env)...)
    }
    // ... execution ...
}
```

Environment entries are sorted by key for deterministic build diagnostics. The command string in build results includes the env prefix so failures are traceable:

```
CGO_LDFLAGS="-L/usr/local/lib -lfaiss_c -lfaiss -lstdc++ -lm" go build -o dist/app -tags vectors .
```

This approach does not modify the generated `go.mod` or `go.sum`. The environment variables are applied at process execution time, not at module resolution time. The generated binary remains identical regardless of how it was built.

### Why Not ldflags?

Linker flags can be expressed in `ldflags` using `-X`, `-s`, `-w`, and `-extldflags`. The `-extldflags` flag passes flags directly to the external linker:

```yaml
ldflags:
  - -extldflags "-L/usr/local/lib -lfaiss_c -lfaiss -lstdc++ -lm"
```

This approach has three problems:

1. Platform specificity. `-L/usr/local/lib` works on Linux and macOS but not on systems where FAISS is installed elsewhere. The build environment variable makes the path configurable per system.

2. CGO interaction. When CGO is involved, the linker invocation involves multiple stages: the Go toolchain first compiles Go files to object files, then invokes the C compiler and linker. `CGO_LDFLAGS` controls the flags passed to the C linker stage, which is separate from the Go linker stage controlled by `-extldflags`. Mixing these concerns leads to subtle build failures.

3. Build reproducibility. The `go.env` field in the spec is a declarative declaration of build requirements. `-extldflags` embeds the configuration in the command line, which is harder to inspect in build logs and less portable across build tools.

For FAISS, the three flags have distinct roles:

- `-lfaiss_c` links the C API wrapper used by go-faiss.
- `-lfaiss` links the core FAISS library.
- `-lstdc++` links the C++ standard library, required because FAISS is implemented in C++.
- `-lm` links the math library, required by some FAISS internal routines.

These flags are not arbitrary. They are the minimal set needed for any Go binary that uses `go-faiss` and the `bleve` `vectors` build tag.

## jsverb Field Name Normalization

### The Problem

xgoja converts JavaScript functions into Glazed CLI commands. Each JavaScript function parameter becomes a CLI field. Command names already go through `cleanCommandWord`, which normalizes `camelCase` and `snake_case` to `kebab-case`:

```
parseDocs         → parse-docs
buildTextIndex    → build-text-index
fooBarBaz         → foo-bar-baz
```

Field names did not receive the same treatment. A JavaScript function declared as:

```javascript
function indexQuery(profilePath, docsJson, foo_bar) {
  return { profilePath, docsJson, foo_bar };
}

__verb__("indexQuery", {
  fields: {
    profilePath: { help: "Profile path" },
    docsJson: { help: "Documents" },
    foo_bar: { help: "Example" }
  }
});
```

would expose CLI flags as `--profilePath`, `--docsJson`, and `--foo_bar`. These do not match the kebab-case convention used throughout Glazed and Cobra.

### How It Works

The normalization is applied in `buildFieldDefinition` when `normalizeName` is true:

```go
func buildFieldDefinition(spec *FieldSpec, normalizeName bool) (*fields.Definition, error) {
    name := strings.TrimSpace(spec.Name)
    if normalizeName {
        name = cliFieldName(name)
    }
    // ...
}
```

The `cliFieldName` function delegates to `cleanCommandWord`, which uses the same `kebabCase` implementation already used for command names.

The normalization is selective. It applies only to top-level JavaScript function parameters and verb fields, not to section fields. The distinction matters because section fields are bound to objects passed into JavaScript as structured data:

```javascript
function summarize(filters) {
  return { state: filters.state, labelCount: filters.labels.length };
}

__verb__("summarize", {
  fields: {
    filters: { bind: "filters" }
  }
});
```

If section field names were normalized, the `filters` object received by `summarize` would contain keys like `state` and `labels-length` instead of `state` and `labels`. This would break JavaScript code that accesses object properties by name. Top-level parameters are positional values passed to the function signature, not object properties. Normalizing them does not affect JavaScript semantics.

### The Invocation Path

The normalization is a CLI boundary concern. JavaScript invocation receives original parameter names. The `buildArguments` function in `runtime.go` looks up values using the normalized key when resolving positional parameters:

```go
case BindingModePositional:
    value := sectionValues[binding.SectionSlug][cliFieldName(binding.Field.Name)]
```

The Glazed field definition stores the normalized key. The parsed values map stores the normalized key. The `buildArguments` function retrieves values using the normalized key and passes the raw value (not the key) to the JavaScript function. The function signature receives values in positional order; the parameter names in the JavaScript source are irrelevant to invocation.

### Test Evidence

The regression test demonstrates the behavior:

```go
func TestTopLevelFieldNamesUseKebabCaseCLI(t *testing.T) {
    registry, err := ScanSource("naming.js", `
function show(profilePath, foo_bar) {
  return [{ profilePath, foo_bar }];
}

__verb__("show", {
  fields: {
    profilePath: { help: "Profile path" },
    foo_bar: { help: "Foo bar" }
  }
});
`)
    require.NoError(t, err)
    verb, ok := registry.Verb("naming show")
    require.True(t, ok)
    desc, err := registry.CommandDescriptionForVerb(verb)
    require.NoError(t, err)
    flags := desc.GetDefaultFlags()
    _, ok = flags.Get("profile-path")
    require.True(t, ok, "camelCase field should be exposed as kebab-case CLI flag")
    _, ok = flags.Get("foo-bar")
    require.True(t, ok, "snake_case field should be exposed as kebab-case CLI flag")
    _, ok = flags.Get("profilePath")
    require.False(t, ok, "camelCase field should not be exposed literally")
    _, ok = flags.Get("foo_bar")
    require.False(t, ok, "snake_case field should not be exposed literally")
}
```

The test confirms that the flag names `--profile-path` and `--foo-bar` exist in the CLI while the JavaScript function still receives `profilePath` and `foo_bar` as parameter names.

## Runtime Section Schema Preservation

A secondary fix was made during the same project. The `appendSectionsToCommandDescription` function in `pkg/xgoja/app/module_sections.go` replaces command schema sections with runtime config sections. This caused jsverb commands to lose their original fields when runtime sections were appended.

The fix preserves existing command sections before appending runtime sections:

```go
func appendSectionsToCommandDescription(desc *cmds.CommandDescription, seen map[string]string, sections []schema.Section, source string) error {
    collected := []schema.Section{}
    if desc != nil && desc.Schema != nil {
        desc.Schema.ForEach(func(_ string, section schema.Section) {
            collected = append(collected, section)
        })
    }
    if err := providerutil.AppendUniqueSections(&collected, seen, sections, source); err != nil {
        return err
    }
    desc.SetSections(collected...)
    return nil
}
```

The regression test verifies that a command argument survives runtime section attachment:

```go
func TestAddSectionsToCommandDescriptionPreservesCommandSchema(t *testing.T) {
    desc := cmds.NewCommandDescription("fixture",
        cmds.WithArguments(fields.New("query", fields.TypeString)),
    )
    runtimeSection, err := schema.NewSection("runtime", "Runtime", schema.WithFields(fields.New("debug", fields.TypeBool)))
    // ... assertion that query argument survives ...
}
```

This fix affects all xgoja-generated commands, not just the goja-bleve project. It was discovered when the `rag` command group appeared as a help-only parent with no child commands. The `rag plan` and `rag index-query` commands existed in the jsverb registry but were not materializing in the generated command tree because their original field definitions were replaced by the runtime section merge.

## Documentation

Both changes are documented in the xgoja bundled help pages:

- `cmd/xgoja/doc/06-buildspec-reference.md` documents `go.env` with the FAISS example.
- `cmd/xgoja/doc/02-user-guide.md` adds a discoverability note for `go.env`.
- `pkg/xgoja/doc/02-jsverbs.md` documents the field naming behavior with code examples.
- `pkg/doc/11-jsverbs-example-reference.md` documents the field naming behavior in the jsverbs example reference.

The bundled documentation is embedded into every generated xgoja binary via `go:embed` and accessible through the `help` command.

## Working Rules

- `go.env` values are applied at process execution time, not at module resolution time. They do not affect the generated binary's module dependencies.
- jsverb field normalization applies only to top-level parameters and verb fields. Section fields are not normalized to avoid breaking JavaScript object property access.
- The `cleanCommandWord` function converts `camelCase`, `snake_case`, `PascalCase`, and `kebab-case` consistently. Multiple consecutive separators collapse into a single hyphen. Trailing and leading hyphens are trimmed.
- Runtime sections are merged into command schemas after existing sections. Duplicate slugs are rejected by `AppendUniqueSections`.

## Files Changed

### go-go-goja

- `cmd/xgoja/internal/buildexec/buildexec.go` — `GoBuild` accepts `env map[string]string`; `run` appends sorted env entries to `cmd.Env`.
- `cmd/xgoja/internal/buildspec/build_spec.go` — `GoSpec.Env` added.
- `cmd/xgoja/cmd_build.go` — threads env through `GoBuild` call.
- `pkg/jsverbs/command.go` — `buildFieldDefinition` accepts `normalizeName bool`; calls `cliFieldName` for top-level fields.
- `pkg/jsverbs/runtime.go` — `buildArguments` looks up positional parameter values using `cliFieldName(binding.Field.Name)`.
- `pkg/jsverbs/jsverbs_test.go` — `TestTopLevelFieldNamesUseKebabCaseCLI` regression test.
- `pkg/xgoja/app/module_sections.go` — `appendSectionsToCommandDescription` preserves existing sections.
- `pkg/xgoja/app/module_sections_test.go` — `TestAddSectionsToCommandDescriptionPreservesCommandSchema` regression test.
- `cmd/xgoja/doc/06-buildspec-reference.md` — `go.env` documentation with FAISS example.
- `cmd/xgoja/doc/02-user-guide.md` — `go.env` discoverability note.
- `pkg/xgoja/doc/02-jsverbs.md` — field naming documentation in bundled jsverbs help.
- `pkg/doc/11-jsverbs-example-reference.md` — field naming documentation in jsverbs example reference.

### goja-bleve

- `cmd/goja-bleve/jsverbs/rag.js` — RAG indexing and querying tool combining Geppetto embeddings with Bleve vector/hybrid search.
- `cmd/goja-bleve/xgoja.yaml` — updated with Geppetto provider, core/host modules, root-mounted jsverbs.
- `cmd/goja-bleve/xgoja-vectors.yaml` — vector build with `go.env.CGO_LDFLAGS` for FAISS linking.
- `pkg/provider.go` — migrated to new `providerapi.ProviderRegistry` and `NewModuleFactory` API.
- `pkg/xgoja/providers/bleve/bleve.go` — provider package migrated to new API.
- `README.md` — updated provider API usage example.

### geppetto

- `pkg/js/modules/geppetto/api_embeddings.go` — `embeddings(settings)` JS module with `embed`, `embedBatch`, and `model` methods.
- `pkg/js/modules/geppetto/api_embeddings_test.go` — unit tests for embeddings builder.
- `pkg/js/modules/geppetto/module.go` — registers `embeddings` export.
- `pkg/js/modules/geppetto/spec/geppetto.d.ts.tmpl` — TypeScript declaration template updated.
- `pkg/doc/types/geppetto.d.ts` — generated TypeScript declaration updated.
- Hardcut test and profile updates to exercise embeddings through a registry profile.

## Commits

- `go-go-goja` `24edeed` — `xgoja: support build env and normalize jsverb flags`
- `go-go-goja` `7a57aa4` — `xgoja: document build env and jsverb flag naming`
- `geppetto` `cb9b6c17` — `geppetto: expose embeddings to JavaScript`
- `goja-bleve` `236bd10` — `goja-bleve: add xgoja rag vector tool`

## Validation

All changes validated before commit:

```bash
# go-go-goja targeted tests
go test ./pkg/jsverbs -run TestTopLevelFieldNamesUseKebabCaseCLI -count=1
go test ./cmd/xgoja/internal/buildexec ./cmd/xgoja/internal/buildspec ./cmd/xgoja ./pkg/xgoja/app -count=1

# geppetto targeted tests
go test ./pkg/js/modules/geppetto ./pkg/js/modules/geppetto/provider -count=1

# goja-bleve non-vector tests
GOWORK=off go test ./... -count=1

# goja-bleve vector tests with FAISS linker flags
GOWORK=off CGO_LDFLAGS="-L/usr/local/lib -lfaiss_c -lfaiss -lstdc++ -lm" go test -tags=vectors -ldflags "-r /usr/local/lib" ./pkg -count=1

# Full RAG smoke test with local Ollama all-minilm embeddings
./dist/goja-bleve-vectors rag index-query \
  --profile-path ../../../geppetto/examples/js/geppetto/profiles/40-embeddings.yaml \
  --embedding-profile ollama-all-minilm-embedding \
  --output json \
  privacy
```

The smoke test indexed 3 demo documents and returned the correct ranking for the query `privacy`: `chunk-1` (privacy preserving retrieval) ranked first, `chunk-3` (vector search and hybrid reciprocal rank fusion) ranked second, and `chunk-2` (flowering shrubs and ornamental trees) ranked third.

## Related Notes

- PROJ - ZK Tool — project note pattern
- ARTICLE - Playbook - Self-Contained Go Wasm and JavaScript Browser Applications — article style exemplar
