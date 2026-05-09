---
title: "PROPOSAL - Go AST-Based Refactoring Tool for Type Substitution"
aliases:
  - Go AST Refactoring Tool
  - Type Substitution Tool
  - go-refactor
tags:
  - research
  - proposal
  - institute
  - go
  - ast
  - refactoring
  - tooling
status: proposal
type: proposal
created: 2026-04-08
triggered-by: GLAZE-HELP-REVIEW
---

# Go AST-Based Refactoring Tool for Type Substitution

A proposal for a general-purpose Go refactoring tool that performs type-safe identifier replacement, struct unwrapping, and import management — the operations that sed and regex-based tools fundamentally cannot do correctly.

> [!summary]
> During the GLAZE-HELP-REVIEW cleanup (eliminating a wrapper type across 10+ files), sed-based renaming produced three systematic failure modes: double-prefixing, field-name corruption, and struct-literal unwrapping errors. An AST-aware tool would have handled all three in a single pass. Go's `golang.org/x/tools` already provides all the building blocks — no one has packaged them into a usable CLI.

---

## The Problem

When refactoring Go codebases, the most common operation is **type substitution**: replacing one type with another across a codebase, updating all references, adjusting imports, and unwrapping intermediate wrapper types. The current tooling landscape has a gap:

| Operation | `gopls rename` | `sed` | `gofmt` | AST script |
|---|---|---|---|---|
| Rename an identifier in its package | ✅ | ⚠️ fragile | ❌ | ✅ |
| Move a type between packages | ❌ | ⚠️ fragile | ❌ | ✅ |
| Delete a wrapper type, redirect callers | ❌ | ❌ | ❌ | ✅ |
| Unwrap embedded struct literals | ❌ | ❌ | ❌ | ✅ |
| Fix imports after type moves | ✅ | ❌ | ✅ (partial) | ✅ |

The gap is **cross-package type substitution with semantic understanding**. `gopls rename` can rename within a package but cannot redirect callers from one package's type to another. `sed` can replace text but cannot distinguish field names from type names from value expressions. No existing tool handles the "delete a wrapper type and redirect all callers" pattern.

### The triggering incident

During the glazed help browser cleanup (ticket GLAZE-HELP-REVIEW, commit `5c82e58`), we eliminated a `help.Section` wrapper type that embedded `*model.Section`. The refactoring touched 10 files and required:

1. **Re-export removal**: `help.SectionGeneralTopic` → `model.SectionGeneralTopic` (remove `const` aliases)
2. **Type replacement**: `*help.Section` → `*model.Section` in function signatures, struct fields, and variables
3. **Struct literal unwrapping**: `help.Section{Section: &model.Section{Slug: "x"}}` → `&model.Section{Slug: "x"}`
4. **Import management**: add `model` import, remove `help` import where no longer needed

Using `sed`, this required 6 passes, each followed by manual cleanup of:
- **Double-prefixing**: sed replaced `SectionGeneralTopic` inside already-qualified `model.SectionGeneralTopic`, producing `model.model.SectionGeneralTopic`
- **Field-name corruption**: sed replaced `SectionType` in struct literal field positions (`{SectionType: ...}`), producing invalid Go
- **Variable shadowing**: a test variable named `model` shadowed the `model` package import after qualification changes

Total time: ~25 minutes of sed + cleanup. Estimated time with an AST tool: ~5 minutes.

---

## Proposed Tool: `go-refactor`

A CLI tool that performs type-aware refactorings on Go codebases using the Go AST and type checker.

### Core operations

```
go-refactor redirect-type --from help.Section --to model.Section ./pkg/help/...
go-refactor unwrap-field --type help.Section --field Section ./pkg/help/...
go-refactor qualify --name SectionGeneralTopic --pkg model ./pkg/help/...
go-refactor delete-reexports --file pkg/help/help.go --names SectionGeneralTopic,SectionExample,...
```

### Operation 1: `redirect-type`

Replaces all references to one type with another, across package boundaries.

```bash
go-refactor redirect-type \
  --from github.com/go-go-golems/glazed/pkg/help.Section \
  --to github.com/go-go-golems/glazed/pkg/help/model.Section \
  ./...
```

**What it does:**
- For each file, uses `go/packages` to load the AST with type information
- Finds every `*ast.SelectorExpr` where the type resolves to `help.Section`
- Replaces the package identifier: `help.Section` → `model.Section`
- Updates imports: adds `"github.com/go-go-golems/glazed/pkg/help/model"`, removes `"github.com/go-go-golems/glazed/pkg/help"` if no longer used
- Preserves pointer/bracket wrappers: `*help.Section` → `*model.Section`, `[]*help.Section` → `[]*model.Section`

**Why sed can't do this:** The pointer (`*`) and brackets (`[]`) are separate AST nodes wrapping the `SelectorExpr`. sed sees `*help.Section` as text and would mangle `*model.Section` if the qualifier changed.

### Operation 2: `unwrap-field`

Removes a wrapper struct by extracting one field from all struct literals.

```bash
go-refactor unwrap-field \
  --type github.com/go-go-golems/glazed/pkg/help.Section \
  --field Section \
  ./...
```

**What it does:**
- Finds all composite literals of type `help.Section`
- Identifies the `Section` element (either by key name or by position for embedded fields)
- Replaces the entire composite literal with just that element's value
- Handles both keyed (`help.Section{Section: x}` → `x`) and unkeyed (`help.Section{x}` → `x`) forms

**Why sed can't do this:** This requires type-checking to know that `help.Section` has a field named `Section`. It also requires tree surgery: replacing a parent node with one of its children.

### Operation 3: `qualify`

Replaces unqualified identifier usage with package-qualified usage.

```bash
go-refactor qualify \
  --name SectionGeneralTopic \
  --pkg model \
  ./pkg/help/...
```

**What it does:**
- Finds every bare `*ast.Ident` with name `SectionGeneralTopic` that resolves to the re-exported const
- Replaces with `*ast.SelectorExpr{X: "model", Sel: "SectionGeneralTopic"}`
- **Preserves field names** in struct literals: `{SectionType: ...}` is left alone because the `Ident` is in a `KeyValueExpr.Key` position
- **Preserves already-qualified usage**: `model.SectionGeneralTopic` is already a `SelectorExpr`, not a bare `Ident`
- Adds `model` import if not present

**Why sed can't do this:** sed cannot distinguish between `SectionType` used as a field name (left side of `:`) vs as a type/constant reference (right side of `:` or standalone).

### Operation 4: `delete-reexports`

Removes `const` blocks, `type` aliases, and `var` re-exports, then redirects all callers.

```bash
go-refactor delete-reexports \
  --file pkg/help/help.go \
  --names SectionGeneralTopic,SectionExample,SectionType
```

**What it does:**
- Parses the target file, finds the `const` block or `type` alias declaration
- Resolves each name to its original definition (e.g., `SectionGeneralTopic` → `model.SectionGeneralTopic`)
- Deletes the declaration from the source file
- Runs `qualify` on all callers to redirect them to the original

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  CLI (cobra)                      │
│  redirect-type | unwrap-field | qualify | ...    │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│            Package Loader                        │
│  go/packages.Load with NeedTypesInfo             │
│  → *types.Info with full type resolution         │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│           AST Rewriter                           │
│  astutil.Apply with cursor.Replace()             │
│  Type-aware: checks types.Info before replacing  │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│          Import Manager                          │
│  astutil.AddImport / DeleteImport                │
│  goimports-style unused import cleanup           │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│          File Writer                             │
│  go/format.Node → write back to disk             │
│  Preserves comments via astutil                  │
└─────────────────────────────────────────────────┘
```

### Key design decisions

1. **Type-checked before rewriting.** Load with `packages.NeedTypesInfo` so every identifier resolves to its definition. Never rewrite based on name alone.
2. **AST cursor replacement, not text substitution.** Use `astutil.Apply` with `cursor.Replace()` to swap AST nodes. The formatter handles rendering.
3. **One operation per pass.** Each command does one semantic operation. Combine them in a shell script for multi-step refactors.
4. **Dry-run by default.** Print the diff, require `--write` to modify files.

---

## Pseudocode: The Core Rewrite Engine

```go
// RewriteEngine holds the shared state for a refactoring pass
type RewriteEngine struct {
    fset    *token.FileSet
    pkgs    []*packages.Package
    dryRun  bool
}

func NewRewriteEngine(patterns []string) (*RewriteEngine, error) {
    fset := token.NewFileSet()
    pkgs, err := packages.Load(&packages.Config{
        Fset: fset,
        Mode: packages.NeedName | packages.NeedSyntax |
              packages.NeedTypesInfo | packages.NeedTypes,
    }, patterns...)
    if err != nil {
        return nil, err
    }
    return &RewriteEngine{fset: fset, pkgs: pkgs}, nil
}

// RedirectType replaces fromType with toType everywhere
func (e *RewriteEngine) RedirectType(fromType, toType types.Type) error {
    for _, pkg := range e.pkgs {
        for i, file := range pkg.Syntax {
            changed := false
            info := pkg.TypesInfo

            astutil.Apply(file, func(cursor *astutil.Cursor) bool {
                expr, ok := cursor.Node().(ast.Expr)
                if !ok {
                    return true
                }

                // Check if this expression's type matches fromType
                tv, ok := info.Types[expr]
                if !ok {
                    return true
                }
                if !types.Identical(tv.Type, fromType) {
                    return true
                }

                // Replace with toType selector
                toPkg := getPackagePath(toType)
                toName := getTypeName(toType)
                cursor.Replace(&ast.SelectorExpr{
                    X:   ast.NewIdent(toPkg),
                    Sel: ast.NewIdent(toName),
                })
                changed = true
                return true
            }, nil)

            if changed {
                e.fixImports(pkg, i, file)
                e.writeFile(pkg.GoFiles[i], file)
            }
        }
    }
    return nil
}
```

---

## Existing Building Blocks

| Component | Package | Status |
|---|---|---|
| Package loading + type checking | `golang.org/x/tools/go/packages` | Stable, well-documented |
| AST traversal + rewriting | `golang.org/x/tools/go/ast/astutil` | Stable |
| Type system queries | `golang.org/x/tools/go/types` | Part of Go standard release cycle |
| Import management | `golang.org/x/tools/imports` (goimports) | Stable |
| Source formatting | `go/format` | Standard library |
| Rename refactoring | `gopls` (internal) | Exists but not extractable as library |

The building blocks all exist and are production-quality. What's missing is the orchestration layer that ties them together for cross-package type substitution.

### Prior art

- **`gorename`** (deprecated) — handled type-aware renaming but was brittle and unmaintained
- **`gopls` rename** — works within a package, not across packages for type substitution
- **`mpvl/refactor`** (experimental, never shipped) — exactly this use case
- **`golang.org/x/tools/go/analysis`** — framework for analysis passes, but designed for diagnostics, not rewrites
- **Rust's `oxc`** and TypeScript's `ts-morph`** — equivalent tools in other ecosystems that demonstrate the pattern works

---

## Scope and Estimate

### Minimum viable tool (MVP)

Focus on the two most impactful operations:

1. **`redirect-type`** — cross-package type replacement
2. **`qualify`** — unqualified → qualified identifier rewriting

These two cover 80% of the GLAZE-HELP-REVIEW refactoring workload. The `unwrap-field` operation is useful but can be done manually for the handful of struct literal sites.

### Estimated effort

| Component | Time |
|---|---|
| Package loading + CLI skeleton | 2h |
| `redirect-type` with type checking | 4h |
| `qualify` with field-name awareness | 3h |
| Import management integration | 2h |
| Dry-run / diff output | 1h |
| Testing on real codebases | 2h |
| **Total** | **~14h** |

### Future scope (post-MVP)

- `unwrap-field` — struct literal unwrapping
- `delete-reexports` — automated re-export deletion + caller redirect
- `extract-method` — extract method to interface
- Integration with `gopls` as a code action

---

## Concrete Starting Point: The GLAZE-HELP-REVIEW Session

The refactoring session that triggered this proposal is the best test case for building and validating the tool. The repo, branch, and exact commits are:

- **Repo**: `github.com/go-go-golems/glazed`
- **Branch**: `task/glaze-help-browser`
- **Session start commit**: `d6ac109` (Phase 1 Tasks 2-7 — help browser scaffold)
- **Session end commit**: `a6ada80` (docs: update diary and changelog for step 14)
- **Refactoring commits**: `d97240c` through `5c82e58` (T1–T11, the cleanup phase)

### Commits where the tool would have helped

| Commit | Operation | What happened with sed | What the tool would do |
|--------|-----------|----------------------|---------------------|
| `f257a6a` (T4) | `qualify` | sed replaced `SectionGeneralTopic` → `model.SectionGeneralTopic` everywhere, double-prefixed already-qualified names to `model.model.SectionGeneralTopic`, corrupted struct field names `SectionType:` → `model.SectionType:` | AST-aware qualify skips `KeyValueExpr.Key` positions and `SelectorExpr` already qualified |
| `2d76053` (T6-T8) | `redirect-type` | No sed needed — extracted new function, updated two callers manually. Clean commit but manual. | `redirect-type` could verify all callers of the old parser were found |
| `5c82e58` (T9-T11) | `redirect-type` + `unwrap-field` | 6 sed passes across 10 files, each followed by `s/model\.model\./model./g` cleanup. Struct literal unwrapping `Section: &model.Section{...}` → `&model.Section{...}` had to be done manually. Variable shadowing (`model` local vs `model` package) in test files broke compilation. | `redirect-type` replaces `*help.Section` → `*model.Section` with type checking. `unwrap-field` removes the wrapper embedding. No double-prefixing possible. Variable shadowing caught at compile time. |

### Test plan for the MVP

1. Checkout `d6ac109` (before any cleanup)
2. Run `go-refactor qualify --name SectionGeneralTopic --pkg model ./pkg/help/...` — should produce the same result as commit `f257a6a` but without the `model.model.` corruption
3. Run `go-refactor redirect-type --from help.Section --to model.Section ./pkg/help/...` — should produce the same result as commit `5c82e58` but without the struct literal breakage
4. `go build ./...` and `go test ./pkg/help/...` should pass after each operation

If the tool can reproduce commits `f257a6a` and `5c82e58` cleanly on the first try, it's ready for real use.

---

## Open Questions

1. **Should this be a standalone CLI or a `gopls` extension?** Standalone is faster to build but `gopls` integration would give editor support. Propose: build standalone first, consider `gopls` extension later.

2. **How to handle build-tagged files?** `go/packages` loads files based on the current build tags. A refactoring that touches `query_fts5.go` and `query_nofts.go` (mutually exclusive via build tags) needs both loaded simultaneously. May require two loads with different `-tags`.

3. **Comment preservation?** `go/format.Node` preserves most comments but can shift their position. Need to test with comment-heavy files.

4. **Module boundary handling?** If `from` and `to` types are in different Go modules, the tool needs to update `go.mod` files. Out of scope for MVP.

---

## Related Notes

- [[Code Review with go-minitrace]] — the guideline that triggered the refactoring session where this need was identified
- [[Agent-Assisted Research Patterns]] — working with AI agents on refactoring tasks
