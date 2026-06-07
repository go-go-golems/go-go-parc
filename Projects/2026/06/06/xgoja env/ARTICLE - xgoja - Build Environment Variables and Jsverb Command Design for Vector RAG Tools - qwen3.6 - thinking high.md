---
title: "xgoja - Build Environment Variables and Jsverb Command Design for Vector RAG Tools"
aliases:
  - "xgoja build env"
  - "xgoja jsverb flags"
  - "xgoja vector RAG"
  - "bleve faiss xgoja"
  - "geppetto embeddings goja"
tags:
  - article
  - xgoja
  - goja
  - bleve
  - faiss
  - vector-search
  - rag
  - geppetto
  - javascript
status: active
type: article
created: 2026-06-06
---

# xgoja - Build Environment Variables and Jsverb Command Design for Vector RAG Tools

This article documents the engineering work that enabled native Bleve vector search through the goja JavaScript runtime, and the supporting changes to the xgoja build system and jsverb command framework that made it possible. The work spans three repositories: `go-go-goja` (xgoja and core modules), `geppetto` (embeddings), and `goja-bleve` (Bleve bindings). Each change addresses a concrete gap that blocked the vector RAG use case.

> [!summary]
> 1. **Build environment variables**: xgoja now supports `go.env` in `xgoja.yaml` for passing build-time environment variables like `CGO_LDFLAGS`, enabling FAISS-linked Bleve builds without shell-dependent workarounds.
> 2. **Jsverb flag naming**: Top-level JavaScript parameters and fields are now normalized to kebab-case CLI flags while preserving JavaScript parameter names at invocation.
> 3. **Runtime section schema preservation**: Fixed a bug where provider runtime config sections replaced jsverb command fields instead of being merged.
> 4. **Geppetto embeddings**: Exposed `geppetto.embeddings(settings)` to JavaScript for document embedding through resolved inference profiles.
> 5. **RAG vector tool**: Combined Bleve vector search with Geppetto embeddings into a single xgoja-generated command that indexes and queries documents end-to-end.

## The Problem Space

Bleve is a full-text search library for Go. Its vector search feature—enabled by the `vectors` build tag—requires linking against FAISS, a C++ library for similarity search. The Go bindings are provided by `go-faiss` and `blevesearch/go-faiss`. Building a binary that uses this feature requires:

```bash
CGO_LDFLAGS="-L/usr/local/lib -lfaiss_c -lfaiss -lstdc++ -lm" \
  go build -tags=vectors
```

The `CGO_LDFLAGS` variable controls the C linker flags. The `-lstdc++` flag is required because FAISS is implemented in C++. The `-lm` flag links the math library, which FAISS uses internally. These flags are not arbitrary; they are the minimum set of linker dependencies for any Go binary that uses FAISS through go-faiss.

xgoja generates Go code that calls `go build` with configurable `tags` and `ldflags`, but it had no mechanism for build-time environment variables. The build environment was entirely shell-dependent:

```bash
# Before: manual shell setup required
export CGO_LDFLAGS="-L/usr/local/lib -lfaiss_c -lfaiss -lstdc++ -lm"
go run github.com/go-go-golems/go-go-goja/cmd/xgoja@v0.8.1 build -f xgoja-vectors.yaml
```

This was not a minor inconvenience. The environment variable was not captured in the spec file, so reproducing builds required documenting the shell setup separately. It also meant that different developers might use different linker paths, leading to build failures that were hard to diagnose.

The same project required exposing Geppetto embeddings to JavaScript. Geppetto is the inference framework for managing models, profiles, and embedding providers. The existing JavaScript bindings exposed inference engines, profiles, and tools, but not embeddings. Without embeddings, a JavaScript RAG tool could not generate the vector representations needed for vector search.

Finally, the jsverb command framework had two issues that became apparent when building the RAG tool. First, field names from JavaScript were exposed on the CLI with their literal names—`profilePath` became `--profilePath`, not the idiomatic `--profile-path`. Second, provider runtime config sections were replacing command schema fields instead of being merged with them, which caused some commands to appear as help-only parents with no children.

## Build Environment Variables

### The Implementation

The `go.env` field was added to the `GoSpec` struct in the xgoja build spec:

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

The environment variables are passed to `go build` by appending them to the process environment in `buildexec.run()`:

```go
func run(ctx context.Context, dir string, env map[string]string, name string, args ...string) (Result, error) {
    cmd := exec.CommandContext(ctx, name, args...)
    cmd.Dir = dir
    if len(env) > 0 {
        cmd.Env = append(os.Environ(), sortedEnv(env)...)
    }
    out, err := cmd.CombinedOutput()
    result := Result{
        Command: commandString(env, name, args),
        Output:  string(out),
    }
    if err != nil {
        return result, fmt.Errorf("%s failed: %w\n%s", result.Command, err, result.Output)
    }
    return result, nil
}
```

The `sortedEnv` function sorts environment keys alphabetically for deterministic build output:

```go
func sortedEnv(env map[string]string) []string {
    keys := make([]string, 0, len(env))
    for key := range env {
        keys = append(keys, key)
    }
    sort.Strings(keys)
    out := make([]string, 0, len(keys))
    for _, key := range keys {
        out = append(out, key + "=" + env[key])
    }
    return out
}
```

The `commandString` function includes the environment variables in the build command output for traceability:

```go
func commandString(env map[string]string, name string, args []string) string {
    cmd := name + " " + joinSpace(args)
    if len(env) == 0 {
        return cmd
    }
    return joinSpace(sortedEnv(env)) + " " + cmd
}
```

### Why Environment Variables, Not ldflags?

FAISS linking cannot be expressed through `ldflags` alone. The Go linker flags (`-ldflags`) control the Go linker, not the C linker. For C libraries, the flags must reach the C compiler's linker invocation, which happens through `CGO_LDFLAGS`.

The distinction matters because FAISS linking involves multiple stages:

1. **Go compilation**: The Go toolchain compiles Go source files and cgo wrapper code to object files.
2. **C compilation**: The C compiler compiles the cgo wrapper files.
3. **C linking**: The C linker links the object files against C libraries. `CGO_LDFLAGS` controls the flags passed to this step.
4. **Go linking**: The Go linker produces the final binary. `-ldflags` controls this step.

The `-lstdc++` and `-lm` flags must reach the C linker, not the Go linker. `-ldflags "-lstdc++"` would be rejected by the Go linker as an unknown flag.

### The xgoja-vectors.yaml Spec

The vector build spec captures all required build configuration declaratively:

```yaml
name: goja-bleve-vectors
go:
  tags:
    - vectors
  ldflags:
    - -r
    - /usr/local/lib
  env:
    CGO_LDFLAGS: "-L/usr/local/lib -lfaiss_c -lfaiss -lstdc++ -lm"
target:
  kind: xgoja
  output: dist/goja-bleve-vectors
packages:
  - id: goja-bleve
    import: github.com/go-go-golems/goja-bleve/pkg/xgoja/providers/bleve
    version: v0.0.0
    replace: ../..
  - id: geppetto
    import: github.com/go-go-golems/geppetto/pkg/js/modules/geppetto/provider
    version: v0.0.0
    replace: ../../../geppetto
  - id: go-go-goja-core
    import: github.com/go-go-golems/go-go-goja/pkg/xgoja/providers/core
    replace: ../../../go-go-goja
  - id: go-go-goja-host
    import: github.com/go-go-golems/go-go-goja/pkg/xgoja/providers/host
    replace: ../../../go-go-goja
modules:
  - package: goja-bleve
    name: bleve
    as: bleve
  - package: geppetto
    name: geppetto
    as: geppetto
  - package: go-go-goja-core
    name: path
    as: path
  - package: go-go-goja-core
    name: yaml
    as: yaml
  - package: go-go-goja-host
    name: fs
    as: fs
    config:
      allow: true
commands:
  eval:
    enabled: true
  run:
    enabled: true
  repl:
    enabled: true
  jsverbs:
    enabled: true
    name: verbs
    mount: root
jsverbs:
  - id: goja-bleve-bundled-verbs
    path: ./jsverbs
    embed: true
```

The spec selects four provider packages: `goja-bleve` for Bleve bindings, `geppetto` for embeddings, `go-go-goja-core` for standard library helpers, and `go-go-goja-host` for filesystem access. The `rpath` ldflag embeds a runtime library search path so the generated binary finds FAISS at runtime without requiring `LD_LIBRARY_PATH`.

### Build Command

The build process takes three steps:

```bash
cd goja-bleve/cmd/goja-bleve
GOWORK=off go run github.com/go-go-golems/go-go-goja/cmd/xgoja@v0.8.1 \
  build -f xgoja-vectors.yaml \
  --work-dir . --keep-work --xgoja-version v0.8.1
```

The `GOWORK=off` flag disables workspace mode so the generated binary compiles against the local copies of the provider packages rather than the workspace versions. The `--keep-work` flag preserves the generated build directory for debugging. The `--xgoja-version` flag selects the xgoja generator version.

The build output shows the environment variables in the command trace:

```
CGO_LDFLAGS="-L/usr/local/lib -lfaiss_c -lfaiss -lstdc++ -lm" go build -o dist/goja-bleve-vectors -tags vectors .
```

This trace is captured in the `Result.Command` field and printed after the build completes. It provides immediate visibility into the build configuration without requiring the developer to inspect the spec file.

## Jsverb Flag Naming

### The Problem

JavaScript verb commands expose their fields as CLI flags. Before this change, field names were used verbatim:

```javascript
function indexQuery(profilePath, query, docsJson) { ... }

__verb__("indexQuery", {
  fields: {
    profilePath: { help: "Profile path" },
    docsJson: { help: "Documents" }
  }
});
```

The generated CLI would expose `--profilePath` and `--docsJson`. This does not match the kebab-case convention used throughout Glazed and Cobra. The command naming layer already normalized names through `cleanCommandWord()`, which converts `camelCase` to `kebab-case`. Field names skipped this normalization.

### The Solution

The `buildFieldDefinition()` function was modified to accept a `normalizeName` parameter:

```go
func buildFieldDefinition(spec *FieldSpec, normalizeName bool) (*fields.Definition, error) {
    name := strings.TrimSpace(spec.Name)
    if normalizeName {
        name = cliFieldName(name)
    }
    if name == "" {
        return nil, fmt.Errorf("field name is empty")
    }
    // ... rest of field construction ...
}
```

The `cliFieldName()` function delegates to `cleanCommandWord()`:

```go
func cliFieldName(name string) string {
    return cleanCommandWord(name)
}
```

The normalization is applied only to top-level JavaScript function parameters and verb fields. Section fields are not normalized. The distinction matters because section fields are bound to objects passed into JavaScript as structured data. If a section field named `state` were normalized to `state`, the field name would not change. But if a section field named `localOnly` were normalized to `local-only`, the JavaScript object would receive `{ "local-only": value }` instead of `{ localOnly: value }`. JavaScript property access uses the exact key, so normalization would break object field access.

Top-level parameters are positional values passed to the function signature. The function receives values by position, not by key. Normalizing the CLI flag name does not affect the JavaScript parameter name.

### The Invocation Path

The runtime builds arguments for JavaScript invocation by looking up values from the parsed command output:

```go
case BindingModePositional:
    value := sectionValues[binding.SectionSlug][cliFieldName(binding.Field.Name)]
    // ...
```

The lookup uses the normalized field name to find the value in the parsed section. The value is then passed to the JavaScript function by position. The JavaScript parameter name in the function signature is unchanged.

### Normalized Flag Table

| JavaScript Field | CLI Flag | JavaScript Parameter |
|-----------------|----------|---------------------|
| `profilePath` | `--profile-path` | `profilePath` |
| `docsJson` | `--docs-json` | `docsJson` |
| `foo_bar` | `--foo-bar` | `foo_bar` |
| `indexPath` | `--index-path` | `indexPath` |
| `limit` | `--limit` | `limit` |

The normalization preserves the JavaScript API while producing idiomatic CLI flags. The `__verb__()` metadata does not change; only the CLI flag name is adjusted.

### Test Evidence

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
    require.NotNil(t, flags)
    _, ok = flags.Get("profile-path")
    require.True(t, ok, "camelCase field should be exposed as kebab-case CLI flag")
    _, ok = flags.Get("foo-bar")
    require.True(t, ok, "snake_case field should be exposed as kebab-case CLI flag")
}
```

## Runtime Section Schema Preservation

### The Bug

Provider packages can expose Glazed config sections that become command flags. When a command is executed, these sections are merged into the command's schema. The merge logic in `appendSectionsToCommandDescription()` was replacing the existing schema instead of merging with it:

```go
func appendSectionsToCommandDescription(desc *cmds.CommandDescription, seen map[string]string, sections []schema.Section, source string) error {
    collected := []schema.Section{}
    // BUG: collected was initialized as empty, dropping existing sections
    if err := providerutil.AppendUniqueSections(&collected, seen, sections, source); err != nil {
        return err
    }
    desc.SetSections(collected...)
    return nil
}
```

This caused commands whose field definitions were added before the runtime section merge to lose their fields. The `rag` command in the goja-bleve project appeared as a help-only parent because its children's field definitions were dropped during the merge.

### The Fix

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

The fix iterates over the existing schema and copies each section into the collected list before appending the runtime sections. The `providerutil.AppendUniqueSections` function deduplicates by section slug, so duplicate slugs are rejected with a clear error.

## Geppetto Embeddings

### The Implementation

The Geppetto JavaScript module was extended to expose embeddings. The `embeddings()` function accepts inference settings and returns an `EmbeddingsProvider` object:

```javascript
const gp = require("geppetto");
const settings = gp.inferenceProfiles.load(profilePath).resolve("assistant");
const embedder = gp.embeddings(settings);
const model = embedder.model();
const vector = embedder.embed("search text");
const vectors = embedder.embedBatch(["doc 1", "doc 2", "doc 3"]);
```

The Go implementation resolves inference settings, creates an embeddings provider, and exposes three methods on the returned JavaScript object:

```go
func (m *moduleRuntime) embeddingsBuilder(call goja.FunctionCall) goja.Value {
    settingsRef, err := m.requireInferenceSettingsRef(call.Arguments[0])
    if err != nil {
        panic(m.vm.NewGoError(err))
    }
    provider, err := embeddings.NewSettingsFactoryFromInferenceSettings(settingsRef.settings).NewProvider()
    if err != nil {
        panic(m.vm.NewGoError(err))
    }
    return m.newEmbeddingsObject(&embeddingsRef{api: m, provider: provider})
}
```

The `EmbeddingsProvider` interface exposes `embed()`, `embedBatch()`, and `model()`:

```typescript
export interface EmbeddingsProvider {
    embed(text: string): number[];
    embedBatch(texts: string[]): number[][];
    model(): EmbeddingModel;
}

export interface EmbeddingModel {
    name: string;
    dimensions: number;
}
```

The `model()` method returns the model name and dimension count, which is required for building the Bleve index mapping.

### Profile Integration

The embeddings API works with the existing profile system. Profiles are YAML files that define inference settings:

```yaml
slug: embeddings
profiles:
  assistant:
    inference_settings:
      api:
        base_urls:
          ollama-base-url: http://localhost:11434
      embeddings:
        type: ollama
        engine: all-minilm
        dimensions: 384
```

The profile is loaded through `inferenceProfiles.load()` and resolved by profile slug. The resolved settings contain the embeddings configuration, which is passed to `embeddings()` to create the provider.

## RAG Vector Tool

### Architecture

The RAG tool combines Geppetto embeddings with Bleve vector search in a single xgoja-generated binary. The tool has two commands:

- `rag plan`: Validates the wiring without calling an embedding provider. Shows available modules and the expected command line.
- `rag index-query`: Embeds documents with Geppetto, indexes them with Bleve vectors, and queries with KNN or hybrid RRF.

```bash
./dist/goja-bleve-vectors rag index-query \
  --profile-path profiles.yaml \
  --embedding-profile ollama-all-minilm-embedding \
  privacy
```

The command line uses kebab-case flags (`--profile-path`, `--embedding-profile`) while the JavaScript function receives camelCase parameter names (`profilePath`, `embeddingProfile`).

### Implementation

The `indexQuery` function performs five steps:

1. **Parse documents**: Parse the JSON document list or use the default demo corpus.
2. **Resolve embedder**: Load the profile registry, resolve the embedding profile, and create an embeddings provider.
3. **Build index**: Create a Bleve index with text, source, and vector fields. The vector field uses cosine similarity and the dimension count from the resolved embedding model.
4. **Index documents**: Embed each document and add it to the index through a batch.
5. **Query**: Embed the query text, build a search request with KNN and optional hybrid scoring, execute the search, and return results.

The search request builder supports two modes:

```javascript
const requestBuilder = bleve.search()
  .query((mode || "hybrid") === "knn" ? bleve.matchNone() : bleve.match(queryText).field("text"))
  .knn("embedding", queryVector, Number(limit || 5), 1.0)
  .fields(["text", "source"])
  .size(Number(limit || 5));
if ((mode || "hybrid") !== "knn") {
  requestBuilder.score("rrf").scoreRankConstant(60).scoreWindowSize(docs.length);
}
```

The `knn()` method adds a KNN search request to the search. The `score()` method selects the fusion strategy: "rrf" for reciprocal rank fusion, "rsf" for reciprocal sum of ranks, or "default" for the Bleve default. The `scoreRankConstant()` and `scoreWindowSize()` methods configure the fusion parameters.

### Validation Output

The validation test produces this output:

```json
{
  "docCount": 3,
  "hits": [
    { "id": "chunk-1", "rank": 1, "score": 0.0328, "text": "privacy preserving retrieval for evaluation systems" },
    { "id": "chunk-3", "rank": 2, "score": 0.0161, "text": "vector search and hybrid reciprocal rank fusion" },
    { "id": "chunk-2", "rank": 3, "score": 0.0159, "text": "flowering shrubs and ornamental trees" }
  ],
  "mode": "hybrid",
  "model": { "dimensions": 384, "name": "all-minilm" },
  "ok": true
}
```

The query `privacy` returns `chunk-1` (privacy preserving retrieval) as the top hit, confirming that the vector search correctly captures semantic similarity.

## Working Rules

1. **Build environment variables are process-level, not module-level**. They are applied at command execution time through `cmd.Env`, not at module resolution time through `go.mod`. This means the environment variables do not affect the generated binary's module dependencies.

2. **Keberos is the standard for CLI flags**. JavaScript parameter names preserve their original casing. CLI flags are normalized to kebab-case. The normalization is applied only to top-level parameters and verb fields, not to section fields.

3. **Section fields are object keys, not CLI flags**. Bound section fields are passed to JavaScript as structured data. Normalizing section field names would change object keys and break JavaScript property access.

4. **Runtime sections are merged, not replaced**. Provider config sections are appended to existing command schema sections. Duplicate slugs are rejected with a clear error message.

5. **Embedding dimensions are required for vector indexing**. The Bleve index mapping must declare the vector field dimensions before documents can be indexed. The dimensions come from the resolved embedding model.

## Files Changed

### go-go-goja

| File | Change |
|------|--------|
| `cmd/xgoja/internal/buildexec/buildexec.go` | `GoBuild` accepts `env map[string]string`; `run` appends sorted env entries to `cmd.Env` |
| `cmd/xgoja/internal/buildspec/build_spec.go` | `GoSpec.Env` added |
| `cmd/xgoja/cmd_build.go` | Threads env through `GoBuild` call |
| `pkg/jsverbs/command.go` | `buildFieldDefinition` accepts `normalizeName bool`; calls `cliFieldName` for top-level fields |
| `pkg/jsverbs/runtime.go` | `buildArguments` looks up positional parameter values using `cliFieldName(binding.Field.Name)` |
| `pkg/jsverbs/jsverbs_test.go` | `TestTopLevelFieldNamesUseKebabCaseCLI` regression test |
| `pkg/xgoja/app/module_sections.go` | `appendSectionsToCommandDescription` preserves existing sections |
| `pkg/xgoja/app/module_sections_test.go` | `TestAddSectionsToCommandDescriptionPreservesCommandSchema` regression test |
| `cmd/xgoja/doc/06-buildspec-reference.md` | `go.env` documentation with FAISS example |
| `cmd/xgoja/doc/02-user-guide.md` | `go.env` discoverability note |
| `pkg/xgoja/doc/02-jsverbs.md` | Field naming documentation in bundled jsverbs help |
| `pkg/doc/11-jsverbs-example-reference.md` | Field naming documentation in jsverbs example reference |

### geppetto

| File | Change |
|------|--------|
| `pkg/js/modules/geppetto/api_embeddings.go` | `embeddings()` builder with `embed()`, `embedBatch()`, `model()` methods |
| `pkg/js/modules/geppetto/api_embeddings_test.go` | Unit tests for embeddings builder |
| `pkg/js/modules/geppetto/module.go` | Registers `embeddings` export |
| `pkg/js/modules/geppetto/spec/geppetto.d.ts.tmpl` | TypeScript declaration template updated |
| `pkg/doc/types/geppetto.d.ts` | Generated TypeScript declaration updated |
| Hardcut tests and profiles | Updated to exercise embeddings through a registry profile |

### goja-bleve

| File | Change |
|------|--------|
| `cmd/goja-bleve/jsverbs/rag.js` | RAG indexing and querying tool combining Geppetto embeddings with Bleve vector/hybrid search |
| `cmd/goja-bleve/xgoja.yaml` | Updated with Geppetto provider, core/host modules, root-mounted jsverbs |
| `cmd/goja-bleve/xgoja-vectors.yaml` | Vector build with `go.env.CGO_LDFLAGS` for FAISS linking |
| `pkg/provider.go` | Migrated to new `providerapi.ProviderRegistry` and `NewModuleFactory` API |
| `pkg/xgoja/providers/bleve/bleve.go` | Provider package migrated to new API |
| `README.md` | Updated provider API usage example |

## Commits

- `go-go-goja` `24edeed` — `xgoja: support build env and normalize jsverb flags`
- `go-go-goja` `7a57aa4` — `xgoja: document build env and jsverb flag naming`
- `geppetto` `cb9b6c17` — `geppetto: expose embeddings to JavaScript`
- `goja-bleve` `236bd10` — `goja-bleve: add xgoja rag vector tool`

## Validation

All changes validated before commit with targeted tests and a full RAG smoke test. The smoke test indexed 3 demo documents and returned the correct ranking for the query `privacy`: `chunk-1` (privacy preserving retrieval) ranked first, `chunk-3` (vector search and hybrid reciprocal rank fusion) ranked second, and `chunk-2` (flowering shrubs and ornamental trees) ranked third.

## Related Notes

- `PROJ - ZK Tool` — project note pattern
- `ARTICLE - Playbook - Self-Contained Go Wasm and JavaScript Browser Applications` — article style exemplar
