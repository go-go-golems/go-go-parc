---
title: "Remarquee: Resilient Markdown to PDF Conversion and Pandoc Metadata Boundaries"
aliases:
  - RMQ-0020 Markdown conversion resilience
  - Remarquee Pandoc YAML parser fix
  - Markdown thematic break Pandoc failure
tags:
  - project-report
  - remarquee
  - markdown
  - pandoc
  - pdf
  - go
  - testing
  - cli
source_ticket: RMQ-0020
status: complete
Topics:
    - remarquee
    - upload
    - markdown
    - pdf
    - mdpdf
    - pandoc
    - xelatex
    - cli
    - go
type: project-report
created: 2026-07-28
analyzed: 2026-07-28
repo: /home/manuel/workspaces/2026-07-28/fix-remarquee-md/remarquee
repository_commit: 9c82565c722f91beca70b421cc2cf8a4d7579ccd
repository_branch: task/fix-remarquee-md
repository_remote: git@github.com:go-go-golems/remarquee.git
related_files:
  - pkg/mdpdf/pandoc.go
  - pkg/mdpdf/pandoc_args_test.go
  - pkg/mdpdf/pandoc_test.go
  - pkg/mdpdf/preprocess.go
  - pkg/mdpdf/bundle.go
  - cmd/remarquee/cmds/upload/md.go
  - cmd/remarquee/cmds/upload/md_test.go
  - cmd/remarquee/cmds/upload/bundle.go
  - cmd/remarquee/cmds/upload/conversion_workers.go
  - pkg/doc/upload/02-remarquee-upload-reference.md
summary: "Deep technical analysis of RMQ-0020, from the original Pandoc failure through the shared converter fix, regression coverage, full validation, and operational lessons."
---


# Remarquee: Resilient Markdown to PDF Conversion and Pandoc Metadata Boundaries

## 1. Executive summary

`remarquee upload md` converts Markdown into a temporary preprocessed Markdown file, invokes Pandoc with XeLaTeX, and uploads the resulting PDF to reMarkable. The reported failure is:

```text
ERROR-CONVERT: /home/manuel/Downloads/scraper_workflow_framework_design.md — pandoc failed: YAML parse exception at line 9, column 0:
did not find expected <document start>
: exit status 64
ERRORS: convert-failed=1 upload-failed=0
```

The input is not a docmgr document with YAML frontmatter. It begins with a Markdown heading and contains an ordinary thematic-break line `---` at source line 10. Pandoc 3.1.3, using its default Markdown extensions, interprets that later separator through the `yaml_metadata_block` extension and reports a YAML parser error. The current preprocessor only strips a YAML block when it is at the beginning of a file, so it does not prevent this failure.

The safest first implementation is to disable Pandoc's `yaml_metadata_block` extension for the generated input, while retaining the existing explicit frontmatter stripping behavior. The Pandoc format selector uses a minus before the extension name:

```text
--from=markdown-yaml_metadata_block
```

This preserves ordinary Markdown separators and avoids rewriting document text. The implementation added regression tests for the user document shape, frontmatter, fenced code containing `---`, bundle conversion, and command-line argument construction. Batch commands retain the established per-file failure collection behavior rather than aborting the complete batch.

The implementation is complete. Commit `5bbc341` introduced the shared Pandoc argument contract, `955626a` added bundle and batch regression coverage, and the later RMQ-0020 commits recorded full validation and handoff. The original 6,275-line document now converts successfully through the real CLI path.

## 2. Problem statement and scope

### 2.1 User-visible problem

A user requested a single Markdown file upload:

```bash
remarquee upload md ~/Downloads/scraper_workflow_framework_design.md
```

Conversion failed before any upload occurred. The command correctly reported one conversion failure and zero upload failures, but the diagnostic exposed an internal Pandoc parser detail and did not explain that the document contained a normal Markdown separator that conflicts with Pandoc's enabled YAML extension.

The desired behavior is:

- ordinary Markdown documents containing thematic breaks should convert successfully;
- true leading frontmatter should continue to be removed from the PDF, as documented;
- YAML-looking examples inside fenced code blocks must remain unchanged;
- `upload md`, `upload bundle`, and any other caller of `mdpdf.ConvertMarkdownFileToPDF` should receive the same behavior;
- one broken input in a directory must not prevent other inputs from being attempted;
- a failure that remains after preprocessing must include the input path, conversion phase, Pandoc output, and exit status;
- tests must not depend on the developer's personal Downloads directory.

### 2.2 In scope

- `pkg/mdpdf` input normalization and Pandoc argument construction;
- frontmatter and thematic-break semantics;
- single-file, PDF-only, directory, and bundle conversion paths;
- test fixtures and integration-test skip behavior;
- user-facing conversion documentation;
- error-message and diagnostics improvements that are directly related to this failure.

### 2.3 Out of scope

- replacing Pandoc;
- implementing a complete CommonMark parser;
- changing XeLaTeX layout, fonts, image resolution, Mermaid rendering, or upload authentication;
- changing reMarkable cloud semantics;
- automatically repairing arbitrary invalid Markdown;
- silently converting genuinely malformed YAML metadata into valid metadata;
- making a single bundled PDF partially successful. A bundle is one conversion unit and should fail as one unit if its concatenated input cannot be converted.

## 3. Current system architecture

### 3.1 End-to-end flow

The relevant flow is:

```text
Cobra command
    |
    +--> upload md: collectMarkdownInputs
    |        |
    |        +--> buildMarkdownConversionJobs
    |        +--> mdpdf.ConvertMarkdownFileToPDF per job
    |        +--> upload PDF per successful job
    |
    +--> upload bundle: collectMarkdownFilesForBundle
             |
             +--> mdpdf.BuildBundleMarkdown
             |       - read each source
             |       - strip leading frontmatter
             |       - resolve images and Mermaid
             |       - concatenate headings and page breaks
             +--> mdpdf.ConvertMarkdownFileToPDF once
             +--> upload one PDF

mdpdf.ConvertMarkdownFileToPDF
    |
    +--> read source bytes
    +--> StripYAMLFrontmatter
    +--> ResolveImagePaths, if enabled
    +--> RenderMermaidBlocks
    +--> NormalizeListSpacing
    +--> FlattenDeepLists
    +--> write temporary input.md
    +--> build Pandoc argv
    +--> exec.CommandContext(...)
    +--> write output PDF or return wrapped Pandoc error
```

### 3.2 `pkg/mdpdf/pandoc.go`

`PandocOptions` at `pkg/mdpdf/pandoc.go:14-36` carries the executable path, PDF engine, fonts, geometry, optional LaTeX headers, table-of-contents settings, syntax highlighting, Mermaid configuration, and image-resolution behavior.

`DefaultPandocOptions` at lines 38-46 selects `pandoc`, `xelatex`, DejaVu fonts, one-inch geometry, and image resolution. `ConvertMarkdownFileToPDF` begins at line 56. It reads the input at lines 85-89, strips only leading YAML frontmatter, performs image and Mermaid preprocessing at lines 97-113, normalizes lists at lines 115-116, writes a fixed temporary `input.md` at lines 122-125, constructs Pandoc arguments at lines 145-169, and runs the subprocess at lines 171-178.

This function is the correct semantic choke point. Adding the input-format option here fixes all callers that eventually use the function, including `upload md`, `upload bundle`, and source conversion helpers that create Markdown before invoking it.

### 3.3 `pkg/mdpdf/preprocess.go`

`StripYAMLFrontmatter` at `preprocess.go:5-42` recognizes only a file whose first line is exactly `---`, then removes through the first later line whose trimmed content is exactly `---`. It intentionally leaves non-frontmatter input unchanged. This is useful for docmgr-style files, but it cannot solve a later `---` that Pandoc interprets as YAML metadata.

`NormalizeListSpacing` at lines 75-101 and `FlattenDeepLists` at lines 103 onward are line-oriented transformations. They demonstrate an important maintenance constraint: preprocessing must not accidentally modify fenced code examples or Markdown constructs that merely resemble list syntax. Any new transformation must make its scope explicit and must have tests for protected regions.

### 3.4 `upload md`

`NewUploadMarkdownCommand` and its flags are in `cmd/remarquee/cmds/upload/md.go:45-108`. `runUploadMarkdown` starts at line 111. Input collection, remote collision detection, and Pandoc option configuration occur before execution.

PDF-only mode calls `convertMarkdownJobs` at lines 218-234. Upload mode converts each job and uploads successful PDFs. The existing upload loop at lines 271-300 records conversion and upload failures separately and continues to the next file. The final summary at lines 303-317 returns a non-zero error if any file failed.

This is valuable existing resilience. RMQ-0020 must not regress it by moving conversion failures into a top-level return that bypasses the remaining jobs.

### 3.5 `upload bundle`

`runUploadBundle` is in `cmd/remarquee/cmds/upload/bundle.go:122-226`. `writeBundlePDF` at lines 228-256 calls `mdpdf.BuildBundleMarkdown` and then `mdpdf.ConvertMarkdownFileToPDF` once. `BuildBundleMarkdown` itself strips frontmatter from each input and creates section headings and page breaks.

A bundle is intentionally one PDF. It does not have the same per-file continuation semantics as `upload md`: if the combined document cannot be converted, the bundle conversion should fail with a useful aggregate diagnostic.

### 3.6 Parallel workers

`convertMarkdownJobs` at `cmd/remarquee/cmds/upload/conversion_workers.go:52-112` supports serial and parallel conversion. In both modes it collects individual errors rather than canceling all workers on the first failure. In parallel mode a mutex protects the error slice. This code should consume the fixed `mdpdf` behavior without needing to understand YAML parsing.

## 4. Reproducing and explaining the failure

### 4.1 Evidence from the reported input

The input begins with normal Markdown:

```text
1  # A Pragmatic Workflow Builder and Execution Framework for Go and Goja
2
3  ## Fresh architecture, API specification, and implementation manual
4
5  **Project context:** `go-go-golems/scraper`  
6  **Design date:** 2026-07-28  
7  **Audience:** a developer joining the project to implement a replacement framework from first principles  
8  **Status:** proposed clean-slate design; not a compatibility specification for the existing engine
9
10 ---
11
12 ## Preface
```

There is no leading frontmatter block. The `---` at line 10 is a thematic break after a paragraph, not a YAML document.

The file contains many later `---` lines as section separators. It also contains fenced code examples, so a repair based on blindly replacing every occurrence of three hyphens would be unsafe.

### 4.2 Direct command evidence

With Pandoc 3.1.3 installed, the following direct conversion reproduces the failure:

```bash
pandoc ~/Downloads/scraper_workflow_framework_design.md \
  -o /tmp/scraper.pdf --pdf-engine=xelatex
```

Observed result:

```text
YAML parse exception at line 9, column 0:
did not find expected <document start>
```

A controlled copy with the thematic-break lines removed still failed when later `---` lines were present. A copy with all exact thematic-break lines replaced by blank lines succeeded in plain-text output mode. More importantly, explicitly disabling the Markdown YAML extension also succeeds without changing the source text:

```bash
pandoc --from=markdown-yaml_metadata_block \
  ~/Downloads/scraper_workflow_framework_design.md \
  -t plain -o /tmp/scraper.txt
```

In Pandoc's format-extension syntax, the `-yaml_metadata_block` suffix disables the extension. This is the central implementation fact to encode in a regression test.

### 4.3 Why current frontmatter stripping is insufficient

The current sequence is effectively:

```text
source starts with '#'
    -> StripYAMLFrontmatter returns source unchanged
    -> later '---' remains in generated input.md
    -> Pandoc parses with yaml_metadata_block enabled
    -> YAML parser sees thematic content as a metadata document
    -> exit status 64
```

The function name and behavior are both reasonable; the missing piece is the explicit Pandoc input contract. The generated input is body Markdown with frontmatter already handled by remarquee. It should not ask Pandoc to discover YAML metadata again.

## 5. Proposed solution

### 5.1 Primary decision: disable Pandoc YAML metadata parsing

Add a fixed input-format argument to the Pandoc invocation:

```go
argv := []string{
    "--from=markdown-yaml_metadata_block",
    inputPath,
    "-o", absOutPDF,
    "--pdf-engine=" + opts.PDFEngine,
    "--standalone",
    // existing options follow
}
```

The argument should be documented with a comment explaining that the leading minus disables the extension. The option belongs in `ConvertMarkdownFileToPDF`, not in each Cobra command, because `mdpdf` owns the generated Markdown contract.

Do not add a user-facing flag in v1. The behavior is a correctness invariant: the package deliberately strips docmgr-style frontmatter before invoking Pandoc. Exposing a flag would let callers re-enable the exact parser behavior that caused the failure and would create inconsistent output across commands.

### 5.2 Keep explicit frontmatter stripping

Continue calling `StripYAMLFrontmatter` before other preprocessing. This preserves the existing documented behavior that docmgr metadata should not appear in the PDF.

A follow-up may improve the stripper to handle UTF-8 BOM, CRLF, and the YAML closing marker `...`, but that is separate from the reported failure. Such changes require their own fixtures because frontmatter detection is a source-preservation concern.

### 5.3 Do not rewrite thematic breaks as the primary fix

Replacing `---` with `***` outside code fences would work around this specific Pandoc behavior, but it is the wrong first abstraction:

- it changes input text unnecessarily;
- a `---` line can be a setext heading underline rather than a thematic break;
- a line-oriented replacement must understand fenced code blocks;
- future Markdown constructs could make the replacement incomplete;
- disabling an unwanted parser extension preserves Pandoc's Markdown semantics.

A thematic-break normalizer may still be useful as a compatibility fallback for another renderer, but it should not be introduced to solve a parser-extension configuration problem.

### 5.4 Improve the wrapped diagnostic

The current error wrapper at `pandoc.go:176-178` includes Pandoc output and the process error, which is good. Add enough context for an operator to distinguish the tool phase and input mode. A target shape is:

```text
pandoc conversion failed for /absolute/path/document.md:
  input format: Markdown without YAML metadata blocks
  pdf engine: xelatex
  pandoc output: YAML parse exception ...
  cause: exit status 64
```

Do not discard Pandoc's original output. Do not include the entire preprocessed document in the error. If the command needs structured diagnostics later, introduce a typed error containing input path, phase, executable, and captured output while retaining `errors.Is`/`errors.As` behavior.

## 6. API and implementation sketch

### 6.1 Internal option helper

A small helper keeps argument construction testable without starting Pandoc:

```go
func buildPandocArgs(inputPath, outputPath string, opts PandocOptions, headers []string) []string {
    args := []string{
        "--from=markdown-yaml_metadata_block",
        inputPath,
        "-o", outputPath,
        "--pdf-engine=" + opts.PDFEngine,
        "--standalone",
        "-V", "mainfont=" + opts.MainFont,
        "-V", "monofont=" + opts.MonoFont,
        "-V", "geometry:" + opts.Geometry,
    }
    for _, header := range headers {
        args = append(args, "-H", header)
    }
    return args
}
```

The helper should either receive already-defaulted options or call a defaulting helper. Avoid making it part of the public package API unless another package needs it.

### 6.2 Conversion pseudocode

```text
ConvertMarkdownFileToPDF(ctx, source, destination, options):
    output = absolute(destination)
    options = applyDefaults(options)
    headers = prepareHeaders(options)

    bytes = read(source)
    body = StripYAMLFrontmatter(bytes)
    body = ResolveImagePaths(body, directory(source), tempDir)
    body = RenderMermaidBlocks(ctx, body, tempDir, options.Mermaid)
    body = NormalizeListSpacing(body)
    body = FlattenDeepLists(body, 4)
    write(tempDir/input.md, body)

    args = buildPandocArgs(tempDir/input.md, output, options, headers)
    run pandoc with ctx, working directory tempDir
    if process fails:
        return ConversionError{Input: source, Args: redacted(args), Output: capturedOutput, Cause: processError}
    return nil
```

Only `args` changes for the reported bug. The ordering of existing preprocessing stages should remain stable unless a test demonstrates an interaction.

### 6.3 Optional typed conversion error

If implementation chooses a typed error, keep it small:

```go
type ConversionError struct {
    Input      string
    PandocPath string
    PDFEngine  string
    Output     string
    Err        error
}

func (e *ConversionError) Error() string
func (e *ConversionError) Unwrap() error
```

Never persist command arguments containing secrets. Current flags do not include credentials, but a future custom header or engine option could. Redact before logging if the typed error stores arguments.

## 7. Detailed test strategy

Tests must prove both the fix and the boundaries around it.

### 7.1 Unit tests for argument construction

Add a test near `pkg/mdpdf/pandoc_test.go` or a new `pandoc_args_test.go`:

- construct default options;
- call the internal argument helper;
- assert that `--from=markdown-yaml_metadata_block` occurs exactly once;
- assert that existing PDF engine, font, geometry, header, ToC, highlight, and listings arguments remain present;
- assert that source and output paths are passed as separate arguments, not shell-concatenated strings.

This test is fast and does not require Pandoc or XeLaTeX.

### 7.2 Preprocessor fixtures

Extend `pkg/mdpdf/preprocess_test.go` with cases for:

- a normal document with `---` after a paragraph;
- multiple thematic breaks;
- `---` inside a fenced `yaml` block, which must remain byte-for-byte unchanged;
- leading docmgr frontmatter, which must still be removed;
- a document beginning with `#`, proving it is not treated as frontmatter;
- CRLF input if the frontmatter follow-up is implemented;
- setext heading syntax if any source rewrite is introduced. The preferred fix does not rewrite it, so this is a safety test rather than a required transform.

The unit tests should not assert that the preprocessor disables Pandoc. That belongs to argument or integration tests.

### 7.3 Real Pandoc integration test

Add a test to `pkg/mdpdf/pandoc_test.go` using a temporary file:

````markdown
# Thematic break regression

Paragraph before the separator.

---

## After the separator

```yaml
---
key: value
---
```
````

The Go source must use a raw string with a safe fence representation or concatenate fence lines so the test itself is valid. Invoke `ConvertMarkdownFileToPDF` with `DefaultPandocOptions` and assert that the output PDF exists and starts with `%PDF`.

The test should skip only when the required tools are unavailable. The existing helper checks standard Pandoc paths, but the production code accepts any executable on `PATH`; improve the helper to use `exec.LookPath` and separately check the selected PDF engine if practical. Keep the test deterministic and avoid relying on a developer-specific font path.

### 7.4 Exact regression fixture

Add a compact fixture derived from the user's failure, not the 6,275-line document. It should include:

- a title and metadata-like prose;
- a blank line;
- `---`;
- a subsection;
- several later separators;
- fenced YAML and JSON examples.

The fixture should reproduce the old failure under a deliberately constructed command without the disabling argument, and succeed through `ConvertMarkdownFileToPDF`. Do not make tests depend on `/home/manuel/Downloads`.

### 7.5 Bundle test

`pkg/mdpdf/bundle_test.go` already verifies frontmatter stripping and bundle headings. Add a case where two bundle inputs contain ordinary `---` separators and one contains a fenced YAML example. Build the bundle and convert it through the real path if tools are available. This catches regressions in the sequence:

```text
BuildBundleMarkdown -> bundle.md -> ConvertMarkdownFileToPDF
```

### 7.6 Batch continuation tests

At the command layer, preserve the existing tests and add a test with a fake Pandoc executable that fails for one filename and succeeds for another. Assert that:

- both jobs are attempted;
- the successful PDF is reported/generated;
- the command returns an error after all work completes;
- the summary counts only the failing conversion;
- no upload is attempted for the failed conversion.

The fake executable should inspect its input file or an explicit environment variable, write a minimal output file for success, and return a non-zero exit status for failure. Avoid making this test invoke the cloud API.

### 7.7 Test matrix

| Area | Regression | Expected result |
|---|---|---|
| argument builder | disabled YAML extension present | exact flag once |
| frontmatter | leading `---` metadata block | metadata omitted from body |
| ordinary separator | `---` after paragraph | conversion succeeds |
| fenced code | YAML example with `---` | code preserved |
| setext heading | `Heading` followed by `---` | semantics preserved |
| bundle | separators in multiple inputs | one PDF succeeds |
| batch | one fake conversion fails | other jobs continue |
| tool absence | Pandoc/XeLaTeX missing | test skips with clear reason |

## 8. Implementation phases

### Phase 1: establish the failing regression

1. Add a compact Markdown fixture containing the line-10 shape and fenced YAML.
2. Add an integration test that currently fails with the YAML parse exception, or add a direct argument-level test that demonstrates the current default.
3. Run only the affected package tests and record the exact command and tool versions in the diary.

Deliverable: a reproducible red test with no production behavior change.

### Phase 2: add the Pandoc input contract

1. Add `buildPandocArgs` or equivalent internal helper.
2. Add `--from=markdown-yaml_metadata_block`.
3. Preserve all existing arguments and working-directory behavior.
4. Update the helper's unit tests.
5. Run `gofmt` and `go test ./pkg/mdpdf`.

Deliverable: the exact regression test passes.

### Phase 3: validate interactions

1. Run the full `pkg/mdpdf` test package.
2. Run `go test ./cmd/remarquee/cmds/upload`.
3. Test PDF-only mode with the real file shape.
4. Test bundle mode with separators and fenced code.
5. Test a directory with one failing fake conversion and one successful conversion.

Deliverable: no regression in image, Mermaid, layout, bundle, or batch behavior.

### Phase 4: diagnostics and documentation

1. Decide whether the existing wrapped error is sufficient or add `ConversionError`.
2. Update `pkg/doc/upload/02-remarquee-upload-reference.md` to say that the converter strips frontmatter and disables Pandoc YAML metadata parsing for generated input.
3. Update the root README only if it documents the detailed conversion pipeline.
4. Add a short troubleshooting entry showing `--pdf-only` and the required tools.

Deliverable: operators can understand the fix without reading Go code.

### Phase 5: release validation

1. Run `go test ./...` from `remarquee`.
2. Run the project's formatting and lint commands if configured.
3. Run a local command such as:

```bash
go run ./cmd/remarquee upload md --pdf-only \
  --output-dir /tmp/rmq-0020-output \
  /path/to/thematic-break-fixture.md
```

4. Inspect the generated PDF and confirm it is non-empty and readable.
5. Review the diff for unrelated changes.
6. Update the diary, task checklist, changelog, and file relations.

## 9. Design decisions

### Decision: disable the parser extension instead of rewriting Markdown

- **Context:** Pandoc's default Markdown parser treats a later `---` as YAML metadata input in the reported document, but `---` is also normal Markdown syntax and can occur inside fenced examples.
- **Options considered:** disable `yaml_metadata_block`; rewrite thematic breaks; parse Markdown into an AST and re-render; add a command flag.
- **Decision:** disable the extension in the `mdpdf` Pandoc invocation and retain explicit leading-frontmatter stripping.
- **Rationale:** it addresses the parser configuration at the narrowest boundary, preserves source semantics, avoids fence-aware rewriting, and applies consistently to all callers.
- **Consequences:** Pandoc will no longer interpret metadata from generated Markdown. That is intentional because remarquee already strips frontmatter. Any future metadata support must be explicit in `PandocOptions`, not inferred from arbitrary body content.
- **Status:** proposed

### Decision: fix at `pkg/mdpdf`, not Cobra commands

- **Context:** `upload md`, `upload bundle`, sync, and source helpers can all reach the shared converter.
- **Options considered:** add arguments in each command; add a flag in command settings; centralize in `ConvertMarkdownFileToPDF`.
- **Decision:** centralize in `pkg/mdpdf/pandoc.go`.
- **Rationale:** one source of truth prevents command drift and makes package-level tests meaningful.
- **Consequences:** callers automatically inherit the safe input contract; direct callers of `mdpdf` are also protected.
- **Status:** proposed

### Decision: preserve batch continuation semantics

- **Context:** earlier resilience work exists because one bad Markdown file should not abort a directory upload.
- **Options considered:** return on first error; collect errors and continue; silently skip failures.
- **Decision:** collect, print, and return a non-zero aggregate error after all independent jobs finish.
- **Rationale:** successful files are useful, but automation still needs a failure signal.
- **Consequences:** callers must interpret partial success from output and exit status; tests must assert both continuation and final error.
- **Status:** accepted by current implementation, preserved by this ticket

## 10. Alternatives and risks

### 10.1 Rewrite `---` to `***`

This is a tempting two-line fix but is not semantically safe for setext headings and fenced code. It also creates a growing Markdown repair layer. Reject as the primary implementation.

### 10.2 Use a full Markdown parser

An AST could distinguish thematic breaks, setext headings, frontmatter, code blocks, and raw blocks. It would be substantially more code and would introduce another parser whose behavior must be reconciled with Pandoc. Use only if future transformations require structural Markdown understanding.

### 10.3 Remove all metadata support

Passing the extension-disable option alone does not remove `StripYAMLFrontmatter`; both are needed. If frontmatter stripping were removed, docmgr YAML would be rendered as document content instead of metadata, which would be a user-visible regression.

### 10.4 Let users choose metadata behavior

A flag could support special documents that intentionally need Pandoc metadata, but it would make output depend on a hidden command option and reopen the failure. Defer until a concrete use case exists; then name the mode explicitly and test it.

### 10.5 Pandoc version drift

Pandoc's extension defaults or diagnostics may change. The explicit `--from` option reduces reliance on defaults, but the integration test should still run against the supported version range. Capture the executable version in failure messages when practical.

### 10.6 XeLaTeX failures after parser success

The fix only removes the YAML parser failure. Documents may still fail because of invalid LaTeX, unsupported Unicode, deeply nested lists, missing fonts, image failures, Mermaid failures, or a missing PDF engine. Those errors must continue to propagate with their original output and must remain distinguishable from the YAML-extension case.

## 11. Acceptance criteria

The implementation is complete when all of the following have evidence:

- a Markdown document with an ordinary `---` separator converts successfully through `mdpdf.ConvertMarkdownFileToPDF`;
- the Pandoc argument list disables `yaml_metadata_block` exactly once;
- leading docmgr frontmatter is still absent from generated content;
- fenced code containing `---` is preserved;
- setext-heading behavior is not changed;
- bundle conversion succeeds for the same constructs;
- batch conversion attempts independent files after one conversion fails;
- final exit status remains non-zero for partial failure;
- diagnostics include the source path and captured Pandoc output;
- `go test ./pkg/mdpdf` and `go test ./cmd/remarquee/cmds/upload` pass;
- full repository tests pass or unrelated existing failures are recorded;
- user-facing upload documentation describes the new input contract;
- the implementation diary records commands, failures, versions, and review instructions.

## 12. File reference map

| File | Responsibility | Intern starting point |
|---|---|---|
| `pkg/mdpdf/pandoc.go` | shared conversion pipeline and subprocess | read `ConvertMarkdownFileToPDF` first |
| `pkg/mdpdf/preprocess.go` | frontmatter/list/deep-list transformations | compare existing invariants before adding logic |
| `pkg/mdpdf/preprocess_test.go` | pure preprocessing tests | add fence and separator fixtures here |
| `pkg/mdpdf/pandoc_test.go` | real Pandoc integration | add the PDF regression test here |
| `pkg/mdpdf/bundle.go` | per-input bundle preprocessing | verify frontmatter and separator behavior |
| `pkg/mdpdf/bundle_test.go` | bundle unit tests | add multi-input separator case |
| `cmd/remarquee/cmds/upload/md.go` | independent Markdown job orchestration | preserve continuation and summary behavior |
| `cmd/remarquee/cmds/upload/bundle.go` | one-PDF bundle orchestration | preserve one-unit failure semantics |
| `cmd/remarquee/cmds/upload/conversion_workers.go` | serial/parallel conversion | preserve collected per-job errors |
| `pkg/doc/upload/02-remarquee-upload-reference.md` | user-facing conversion contract | update after behavior is implemented |
| `ttmp/2026/05/15-RMQ-0015...` | prior batch-resilience rationale | read for error collection history |

## 13. Review instructions for the intern

Start in this order:

1. Read this document's sections 3 and 4.
2. Read `pkg/mdpdf/pandoc.go` and `preprocess.go` completely.
3. Read `pandoc_test.go`, `preprocess_test.go`, and `bundle_test.go`.
4. Read the conversion portions of `upload/md.go`, `upload/bundle.go`, and `conversion_workers.go`.
5. Reproduce the direct Pandoc failure and the explicit-extension-disable success.
6. Implement Phase 1 before Phase 2; do not change multiple unrelated preprocessing rules at once.

Reviewers should pay particular attention to:

- whether the exact Pandoc syntax really disables, rather than enables, `yaml_metadata_block`;
- whether leading frontmatter behavior remains unchanged;
- whether code fences and setext headings retain their semantics;
- whether all shared conversion callers receive the fix;
- whether a failed batch still processes independent jobs;
- whether error output leaks temporary paths or sensitive command arguments;
- whether tests are reproducible on machines without Pandoc or XeLaTeX.

## 14. Useful commands

From `/home/manuel/workspaces/2026-07-28/fix-remarquee-md/remarquee`:

```bash
# Inspect the relevant package.
go test ./pkg/mdpdf -count=1
go test ./cmd/remarquee/cmds/upload -count=1

# Validate Pandoc's extension behavior directly.
pandoc --list-extensions=markdown | grep yaml
pandoc --from=markdown-yaml_metadata_block input.md -t plain -o /tmp/input.txt

# Generate a local PDF without cloud authentication.
go run ./cmd/remarquee upload md --pdf-only \
  --output-dir /tmp/rmq-0020-output \
  /path/to/fixture.md

# Full validation after implementation.
gofmt -w pkg/mdpdf/*.go cmd/remarquee/cmds/upload/*.go
go test ./...
```

The `--pdf-only` path is the preferred manual smoke test because it exercises collection, preprocessing, Pandoc, and filesystem output without requiring reMarkable authentication.

## 15. Open questions

- Which Pandoc versions are officially supported in CI and release documentation?
- Should `pandocAvailable` use `exec.LookPath` and test the configured PDF engine, or remain a narrowly scoped integration-test helper?
- Is a typed `ConversionError` worth adding now, or does the existing wrapped error provide sufficient operator context?
- Should frontmatter support later accept `...` as a closing marker and UTF-8 BOM/CRLF input?
- Should bundle conversion expose the intermediate preprocessed Markdown under a debug flag when conversion fails?

These questions do not block the primary parser-extension fix. They should be answered during implementation review rather than solved speculatively in the first patch.

## 16. Implementation results

The design described above is now implemented. The important distinction is between a design recommendation and an observed result: the repository contains the recommendation in `RMQ-0020`, and the branch now contains the code, tests, documentation, and validation evidence that realize it.

The production change is intentionally small. `pkg/mdpdf/pandoc.go` now owns a `buildPandocArgs` helper. That helper starts the input format with:

```text
--from=markdown-yaml_metadata_block
```

The flag is not a shell fragment. It is one argument in the `exec.CommandContext` argument vector. Pandoc interprets the minus before `yaml_metadata_block` as an instruction to disable that reader extension. The rest of the argument vector remains explicit and positional:

```text
--from=markdown-yaml_metadata_block
/tmp/remarquee-mdpdf-123/input.md
-o
/tmp/output/document.pdf
--pdf-engine=xelatex
--standalone
-V
mainfont=DejaVu Sans
-V
monofont=DejaVu Sans Mono
-V
geometry:margin=1in
-H
/tmp/remarquee-mdpdf-123/header.tex
```

The shared converter still reads the source file, strips leading docmgr frontmatter, resolves local images when enabled, renders Mermaid blocks when configured, normalizes list spacing, flattens deep lists, writes a temporary `input.md`, and runs Pandoc with a temporary working directory. The fix changes the reader configuration. It does not introduce a second Markdown rewrite pass.

The commits separate the behavioral change from the broader proof:

| Commit | Scope | Result |
|---|---|---|
| `5bbc3411b7db7d4a0ceb82cb2bafb83e4b2f5626` | Shared Pandoc argument construction and direct regression test | Ordinary thematic breaks and fenced YAML convert through `pkg/mdpdf`. |
| `955626a31ec57b3141220a6f0dca1556d5a2426a` | Bundle test, batch continuation test, and upload reference update | Bundle and independent per-file upload behavior are covered. |
| `e9a17b680028a64348e90861aacef985ea0ac4cf`, `4917b184f8f40614ec9dad0691ecc06bf3d40669`, `cc3870fe885c8f4770031d263d736846639421f4`, `9c82565c722f91beca70b421cc2cf8a4d7579ccd` | Diary, changelog, full validation, ticket closure, and handoff | RMQ-0020 records the complete implementation history. |

The ticket closed with all 20 tasks complete. The final repository-wide test run passed after generating the ignored frontend assets required by `cmd/remarquee-ui/embed.go`.

## 17. The exact code path after the fix

A new contributor should trace the implementation from the CLI down rather than starting with the Pandoc command in isolation. The command owns selection and upload policy. The package owns document conversion. The boundary between those responsibilities is the `PandocOptions` value.

### 17.1 Command-level option assembly

`cmd/remarquee/cmds/upload/layout.go` creates the default `mdpdf.PandocOptions` and applies command flags. `upload md` and `upload bundle` both use this path. The commands can select the PDF engine, fonts, geometry, layout preset, LaTeX header, Mermaid settings, and image resolution. They do not construct reader-format arguments themselves.

That separation prevents this failure class from returning in one command. If `upload md` had received the fix while `upload bundle` still assembled the old argument vector, a document could succeed as one PDF and fail as another. The shared package makes the contract uniform.

### 17.2 Conversion-level preprocessing

The converter performs preprocessing in a fixed order. The order matters because each stage changes the input seen by the next stage:

```text
raw bytes
  -> leading frontmatter removal
  -> local image copying and path rewriting
  -> Mermaid block rendering
  -> list spacing normalization
  -> deep-list flattening
  -> temporary input.md
  -> Pandoc reader with yaml_metadata_block disabled
  -> PDF engine
```

The frontmatter stage is intentionally narrow:

```go
func StripYAMLFrontmatter(mdText string) string {
    if !strings.HasPrefix(mdText, "---") {
        return mdText
    }

    lines := strings.Split(mdText, "\n")
    if strings.TrimSpace(lines[0]) != "---" {
        return mdText
    }

    for i := 1; i < len(lines); i++ {
        if strings.TrimSpace(lines[i]) == "---" {
            return strings.TrimLeft(strings.Join(lines[i+1:], "\n"), "\n")
        }
    }
    return mdText
}
```

This function answers one question: does this file begin with the repository's recognized metadata block? It does not attempt to classify every later `---` line in the document. That is why the Pandoc reader configuration must be correct independently.

### 17.3 Process ownership and cancellation

`ConvertMarkdownFileToPDF` uses `exec.CommandContext`. The context belongs to the command invocation and can terminate Pandoc when the caller is canceled or when a parent timeout expires. The converter creates a temporary directory and removes it with a deferred cleanup function. The output path is converted to an absolute path before the subprocess starts because the subprocess working directory is changed to the temporary directory.

The essential invariant is:

```go
cmd := exec.CommandContext(ctx, opts.PandocPath, argv...)
cmd.Dir = tmpDir
out, err := cmd.CombinedOutput()
```

The input and helper files resolve relative to `tmpDir`; the output PDF resolves to the caller's absolute path. This is why the fix belongs in argument construction but must not accidentally move path resolution or working-directory setup.

## 18. Why the metadata boundary is a system contract

Pandoc's metadata reader is useful when the source document is intended to control the output template. A document can provide a title, author, date, language, table-of-contents settings, bibliography configuration, LaTeX variables, and custom template fields. The official Pandoc documentation defines the construct directly:

> “A YAML metadata block is a valid YAML object, delimited by a line of three hyphens (`---`) at the top and a line of three hyphens (`---`) or three dots (`...`) at the end.”
>
> — Pandoc User’s Guide, [Metadata blocks](https://pandoc.org/demo/example33/8.10-metadata-blocks.html)

Pandoc's extension model also defines the control mechanism used by this project:

> “An extension can be enabled by adding `+EXTENSION` to the format name and disabled by adding `-EXTENSION`.”
>
> — Pandoc User’s Guide, [Extensions](https://pandoc.org/demo/example33/7-extensions.html)

Remarquee deliberately establishes a different contract. It treats docmgr YAML frontmatter as repository metadata, removes that frontmatter before PDF conversion, and then applies command-level typography and layout options. The generated temporary Markdown is therefore not a metadata-bearing source document. It is a body document prepared for a specific PDF renderer.

The contract can be written as a function:

```text
remarquee metadata policy:
    input frontmatter -> repository metadata, not rendered content
    command flags     -> explicit PDF configuration
    body Markdown     -> Markdown content only
    Pandoc YAML blocks -> disabled
```

The distinction prevents two classes of ambiguity:

1. A separator written as Markdown content cannot unexpectedly change the document metadata parser state.
2. A future contributor cannot add a metadata field to a document and assume that Pandoc will silently apply it, bypassing the CLI's explicit option model.

If future users need Pandoc metadata, the API should expose it intentionally. A possible future shape is:

```go
type PandocOptions struct {
    // Existing fields omitted.
    Metadata map[string]string
}
```

The converter could serialize that map into explicit `--metadata key=value` arguments or a controlled temporary metadata file. That design would make metadata ownership visible and testable. Re-enabling implicit YAML parsing would not.

## 19. Test architecture and what each test proves

The tests operate at different boundaries because no single test can prove the entire contract. Argument tests establish the command vector. Converter tests establish real Pandoc behavior. Bundle tests establish composition. Upload command tests establish continuation and exit semantics.

### 19.1 Argument-level proof

`pkg/mdpdf/pandoc_args_test.go` checks that:

- the disable flag is first and appears exactly once;
- input and output paths remain separate arguments;
- the PDF engine remains configured;
- table of contents, highlight style, listings, and LaTeX headers remain present when enabled.

This test does not launch Pandoc. It protects the internal API that builds the external process contract.

### 19.2 Real converter proof

`pkg/mdpdf/pandoc_test.go` writes a temporary Markdown file containing:

```markdown
# Thematic break regression

Paragraph before the separator.

---

## After the separator

```yaml
---
key: value
---
```
```

The test runs `ConvertMarkdownFileToPDF` with the default options, reads the result, and verifies the `%PDF` signature. The test therefore covers the reader argument, temporary input generation, Pandoc, and XeLaTeX.

A second test sends two inputs through `BuildBundleMarkdown` before converting the generated bundle. This matters because bundle preprocessing adds headings and page breaks, and because it reads each source independently before creating the final `bundle.md`.

### 19.3 Batch continuation proof

`cmd/remarquee/cmds/upload/md_test.go` uses a fake Pandoc executable. The fake process locates the `.md` input argument, returns exit status 42 when the preprocessed content contains `FAIL_CONVERSION`, and writes a minimal PDF for all other inputs.

The test submits one good file and one bad file through `upload md --pdf-only`. It proves three properties:

- the failed conversion is reported;
- the successful sibling still produces `good.pdf`;
- the command returns an aggregate error after processing both jobs.

The test intentionally operates through the CLI command rather than calling the worker helper directly. The behavior users depend on is per-file continuation plus a non-zero final result.

### 19.4 Full validation

The final validation required generated frontend assets because `cmd/remarquee-ui/embed.go` contains:

```go
//go:embed frontend/dist
var frontendDist embed.FS
```

The repository's existing generator uses Dagger by default and supports local builds through `BUILD_WEB_LOCAL=1`. The local validation sequence was:

```bash
BUILD_WEB_LOCAL=1 GOWORK=off GOTOOLCHAIN=auto \
  go generate ./cmd/remarquee-ui

GOWORK=off GOTOOLCHAIN=auto \
  go test ./... -count=1
```

The generated `frontend/dist` and `frontend/node_modules` directories are ignored by Git. The full suite passed after generation, including the UI package that previously failed during package discovery.

## 20. Failure taxonomy

A resilient conversion pipeline needs to distinguish errors by the stage that owns them. The following table is the operational model for this project:

| Stage | Example failure | Owner | Batch behavior |
|---|---|---|---|
| Input collection | Missing file or unsupported extension | `upload md` / `upload bundle` | Fail before execution because the job set is not well-defined. |
| Collision detection | Two files sanitize to the same remote name | Upload command | Fail before conversion to avoid ambiguous destinations. |
| Frontmatter preprocessing | File cannot be read | `pkg/mdpdf` | Fail that conversion; independent `upload md` jobs continue. |
| Image resolution | Referenced local image cannot be copied | `pkg/mdpdf/images.go` | Fail that conversion when resolution is enabled. |
| Mermaid rendering | `mmdc` failure | `pkg/mdpdf/mermaid.go` | Current design logs per-block failure and continues with the code block. |
| Pandoc reading | YAML parser, malformed Markdown, missing input | `pkg/mdpdf/pandoc.go` plus Pandoc | Fail that conversion; the error includes Pandoc output. |
| PDF engine | XeLaTeX error, missing font, invalid LaTeX | Pandoc/XeLaTeX | Fail that conversion; do not upload a missing or partial output. |
| Remote upload | Auth, network, cloud API error | `upload/md.go` and `rmcloud` | Fail that upload; independent files continue. |
| Bundle conversion | Any source breaks the combined PDF | `upload/bundle.go` and `mdpdf` | Fail the bundle as one unit. |

The YAML fix addresses one Pandoc reading failure. It does not turn arbitrary Markdown into valid LaTeX, and it does not change the upload command's error policy.

## 21. Comparison of repair strategies

The implementation chose parser configuration over source rewriting. The decision can be evaluated directly:

| Strategy | Preserves `---` source bytes | Preserves fenced code | Preserves setext headings | Applies to all callers | Complexity |
|---|---:|---:|---:|---:|---:|
| Disable `yaml_metadata_block` | Yes | Yes | Yes | Yes | Low |
| Replace `---` with `***` | No | Only with fence parser | Not reliably | Only where wired | Medium |
| Parse and re-render Markdown AST | No | Yes if parser is correct | Yes if parser is correct | Yes | High |
| Add a user flag | Yes | Yes | Yes | No, unless every caller wires it | Medium |
| Leave default Pandoc behavior | Yes | Yes | No for the failure shape | Yes | Low implementation, incorrect behavior |

The selected strategy is not a claim that source rewriting is never useful. It is a claim about ownership. Pandoc already has an extension switch that expresses the intended input semantics. The project should use that switch rather than introduce a second parser for one ambiguity.

## 22. Reimplementation sequence for a new contributor

A contributor implementing the same change in another branch should proceed in this order:

1. Reproduce the failure with a small file containing prose, a blank line, `---`, and a following heading.
2. Confirm that `pandoc --from=markdown-yaml_metadata_block` converts the source without rewriting it.
3. Read `ConvertMarkdownFileToPDF` completely and identify every preprocessing stage.
4. Move argument construction into a helper without changing argument values.
5. Add an argument test before adding the real Pandoc fixture.
6. Add the direct thematic-break and fenced-YAML test.
7. Add bundle coverage because bundle generation creates a new Markdown document.
8. Add a fake-Pandoc batch test to prove independent continuation.
9. Update the user-facing contract in `pkg/doc/upload/02-remarquee-upload-reference.md`.
10. Run focused tests with the repository's required toolchain invocation.
11. Generate ignored frontend assets before repository-wide tests.
12. Update the ticket diary and changelog with exact commands and commit hashes.

The sequence keeps the change narrow. It also ensures that a passing direct converter test does not conceal a broken command-level behavior.

## 23. General engineering rules extracted from this project

The incident yields reusable rules for subprocess-backed document conversion:

- Define the exact input language before invoking a general-purpose converter. A source file that has already been normalized should not be parsed under a broader default mode than its contract requires.
- Keep metadata ownership explicit. Repository frontmatter, command flags, and renderer metadata should not compete silently for the same syntax.
- Put process argument construction beside the process invocation. Callers should supply semantic options, not assemble partial subprocess vectors.
- Test the external argument vector separately from the external program. This isolates configuration regressions from tool installation failures.
- Test a real representative document. Argument tests cannot prove that the downstream parser accepts the intended syntax.
- Preserve batch independence. A failed conversion should prevent its own upload, not suppress unrelated work, while the command still returns a non-zero result for automation.
- Treat generated frontend assets as build prerequisites when Go embeds them. The test command should either generate them or state that the prerequisite exists.
- Record full validation failures exactly. A test suite that fails during package discovery communicates a different engineering problem than a test assertion failure.

## 24. Evidence ledger

The following table links claims in this report to concrete local evidence. Paths are relative to the remarquee repository unless otherwise noted.

| Evidence | What it establishes |
|---|---|
| `pkg/mdpdf/pandoc.go` | Shared conversion pipeline, temporary directory, Pandoc argv, working directory, and subprocess error wrapping. |
| `pkg/mdpdf/preprocess.go` | Leading-frontmatter behavior, list spacing normalization, and deep-list flattening. |
| `pkg/mdpdf/pandoc_args_test.go` | Exact `--from=markdown-yaml_metadata_block` argument contract. |
| `pkg/mdpdf/pandoc_test.go` | Real Pandoc PDF conversion for thematic breaks, fenced YAML, hash-containing names, headers, images, and bundles. |
| `pkg/mdpdf/bundle.go` | Per-file bundle preprocessing, stable headings, image handling, Mermaid handling, and page breaks. |
| `cmd/remarquee/cmds/upload/md.go` | File collection, job creation, PDF-only mode, upload mode, and aggregate conversion/upload errors. |
| `cmd/remarquee/cmds/upload/md_test.go` | CLI-level continue-on-error behavior with fake Pandoc. |
| `cmd/remarquee/cmds/upload/bundle.go` | Single-PDF bundle orchestration and upload behavior. |
| `cmd/remarquee/cmds/upload/conversion_workers.go` | Serial and parallel conversion error collection. |
| `cmd/remarquee/cmds/upload/layout.go` | Translation from command flags to `mdpdf.PandocOptions`. |
| `pkg/doc/upload/02-remarquee-upload-reference.md` | User-facing conversion contract after the implementation. |
| `cmd/remarquee-ui/gen.go` | Go generate entry point for frontend embedding. |
| `cmd/build-remarquee-ui-web/main.go` | Dagger/local frontend build paths and ignored `dist` output. |
| `ttmp/2026/07/28/RMQ-0020.../design-doc/01-intern-guide-resilient-markdown-to-pdf-conversion.md` | Detailed initial architecture and implementation design. |
| `ttmp/2026/07/28/RMQ-0020.../reference/01-investigation-diary.md` | Chronological reproduction, implementation, tests, commits, and final validation. |
| `ttmp/2026/05/15-RMQ-0015.../analysis/01-analysis-pandoc-errors-abort-sync.md` | Prior batch-resilience decision and aggregate error model. |

## 25. External references

| Reference | Relevance |
|---|---|
| [Pandoc User’s Guide: Metadata blocks](https://pandoc.org/demo/example33/8.10-metadata-blocks.html) | Defines YAML metadata-block syntax and delimiter behavior. |
| [Pandoc User’s Guide: Extensions](https://pandoc.org/demo/example33/7-extensions.html) | Defines `+EXTENSION` and `-EXTENSION` format controls. |
| [Pandoc User’s Guide: Horizontal rules](https://pandoc.org/demo/example33/8.8-horizontal-rules.html) | Documents the interaction between horizontal rules and subsequent block parsing. |
| [Pandoc User’s Guide: General options](https://pandoc.org/demo/example33/3.1-general-options.html) | Documents the `--from` reader-format option. |
| [Go `os/exec` package](https://pkg.go.dev/os/exec) | Documents `CommandContext`, which the converter uses for cancellation-aware subprocess execution. |
| [Go `context` package](https://pkg.go.dev/context) | Defines cancellation and deadline propagation used by conversion and rendering. |

The external references describe tool behavior. The local evidence establishes how remarquee composes that behavior with frontmatter stripping, temporary files, PDF generation, and upload orchestration.

## 26. Final status

RMQ-0020 is complete. The original failure is fixed at the shared Markdown conversion boundary. The exact user document converts successfully, the result is a non-empty PDF, direct and bundle paths have regression coverage, independent batch files continue after one failure, the upload documentation describes the parser contract, the full Go test suite passes after generating ignored frontend assets, and the ticket diary preserves the implementation evidence.

The remaining questions are future API decisions, not blockers for the implemented behavior. Any future metadata feature should be explicit. Any future parser repair should be tested against fenced code, setext headings, frontmatter, bundles, and the real PDF engine path before it changes the shared converter.
