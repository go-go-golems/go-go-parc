---
title: "Deep Dive: Building a Modern XML CLI in Go — Part 3"
aliases:
  - XML CLI Part 3
  - Schematron Workflows
  - XSLT Analysis
tags:
  - article
  - go
  - xml
  - helium
  - glazed
  - cli
  - schematron
  - xslt
  - coverage
  - static-analysis
status: active
type: article
created: 2026-05-11
repo: /home/manuel/code/wesen/2026-05-11--helium-xml-tool
---

# Deep Dive: Building a Modern XML CLI in Go — Part 3

This article is the third in a series about building `xml`, a production-grade command-line tool for XML processing in Go. Part 1 covered the three-layer architecture, the validation pipeline, and the Glazed command skeleton. Part 2 covered schema introspection, inference, diff, and DTD analysis. This part covers Phase 3: Schematron workflows and XSLT execution and static analysis. By the end of Part 3, you will understand how Schematron validation produces structured results through an error handler, how Schematron coverage analysis measures rule effectiveness across a document corpus, how XSLT transformations are compiled and executed through the helium API, and why XSLT static analysis requires DOM walking rather than querying the compiled stylesheet.

The target audience is a developer who read Parts 1 and 2 and wants to see how the engine layer extends to rule-based validation and transformation workflows, or a developer who maintains Schematron schemas and XSLT stylesheets and needs tooling that goes beyond "does it validate" to "which rules fire" and "which templates are unused."

> [!summary]
> This article covers four core ideas:
> 1. Schematron validation through the `ErrorHandler` pattern: how the `schResultCollector` intercepts validation errors and classifies them as asserts (severity: error) or reports (severity: info), producing `SchValidateResult` rows.
> 2. Schematron coverage analysis: how running validation against a document corpus and aggregating which rules fire produces a coverage map with `covered`, `uncovered`, and `failed` statuses.
> 3. XSLT compilation and execution: how `xslt3.CompileStylesheet` and `Stylesheet.Transform` produce a working transformation pipeline, and the current limitation around parameter passing.
> 4. XSLT static analysis via DOM walking: why the compiled `Stylesheet` struct's unexported fields force the CLI to parse the raw XSLT document instead, and how `walkXSLTElements` extracts templates, functions, variables, and imports from the DOM tree.

## The problem Part 3 solves

Schema validation answers a structural question: does this document conform to this type system? Schematron answers a different question: does this document satisfy these business rules? A book element with a title child is structurally valid against an XSD that declares `<xs:element name="title" type="xs:string"/>`. But a Schematron rule can assert that the title must not be empty, that the author must be listed in an external registry, or that the publication year cannot be in the future. These are constraints that operate on the content of elements, not on their structure.

XSLT answers yet another question: how do I transform this document into that format? A transformation engine is a different kind of tool than a validation engine, but in the XML ecosystem, the two are deeply connected. Schematron itself compiles to XSLT before execution. An XSLT developer who maintains a library of templates and functions needs the same kind of static analysis that a schema author gets from `xml schema lint` and `xml schema refs`.

Phase 3 adds two command groups: `xml sch` (5 commands) and `xml xsl` (6 commands). Together they cover the full Schematron and XSLT development lifecycle.

## Schematron: from schema to structured results

The helium `schematron` package follows the same three-step pattern established in Part 1 for XSD and RELAX NG:

```text
Parse  →  Compile  →  Validate
```

The compile step produces a `Schema` object. The validate step runs the compiled schema against a document and delivers errors through an `ErrorHandler`. What makes Schematron different from XSD validation is the semantics of the errors: an XSD error means "this element does not conform to the type system," while a Schematron error means "this XPath assertion evaluated to false on this context node."

### The compiled Schema

The helium `schematron.Schema` struct contains the parsed rule structure:

```go
type Schema struct {
    patterns   []*pattern
    namespaces map[string]string
    title      string
}

type pattern struct {
    name  string
    rules []*rule
}

type rule struct {
    context     string
    contextExpr *xpath1.Expression
    tests       []*test
    lets        []*letBinding
    line        int
}

type test struct {
    typ      testType      // testAssert or testReport
    expr     string
    compiled *xpath1.Expression
    message  []messagePart
    line     int
}
```

The `test` struct distinguishes between asserts and reports. An assert fires when its XPath expression evaluates to false — the assertion is violated. A report fires when its expression evaluates to true — the condition is present. This distinction is critical for structured output because a failed assert is an error, while a fired report is informational.

The `message` field is a slice of `messagePart` values. A message part can be literal text (`textPart`), an element name reference (`namePart`), or a value-of expression (`valueOfPart`). These parts are concatenated at validation time to produce the human-readable message. The CLI does not need to understand the message structure — it receives the final message text through the error handler.

### Compilation

The `CompileSchematron` function follows the established pattern:

```go
func CompileSchematron(ctx context.Context, path string) (*schematron.Schema, error) {
    abs, _ := filepath.Abs(path)
    if _, err := os.Stat(abs); err != nil {
        return nil, fmt.Errorf("cannot access schema: %w", err)
    }
    schema, err := schematron.NewCompiler().
        Label(abs).
        CompileFile(ctx, abs)
    if err != nil {
        return nil, fmt.Errorf("compiling Schematron: %w", err)
    }
    return schema, nil
}
```

The `Label` method sets the filename used in error messages. Without it, compilation errors reference `(string)` instead of the actual file path. The compiler reads the file, parses it with helium's XML parser, and then compiles the Schematron structure — walking the DOM tree to find `<pattern>`, `<rule>`, `<assert>`, and `<report>` elements, compiling their XPath expressions, and storing the results in the `Schema` object.

### Validation and the error handler

Schematron validation delivers results through the `ErrorHandler` interface. This is the same interface used by XSD and RELAX NG validation in Part 1. The difference is in how the results are interpreted:

```go
func SchValidate(ctx context.Context, schema *schematron.Schema,
    file string, noNetwork bool) ([]SchValidateResult, error) {

    buf, _ := os.ReadFile(file)
    parser := helium.NewParser()
    if noNetwork {
        parser = parser.AllowNetwork(false)
    }
    doc, _ := parser.Parse(ctx, buf)

    collector := &schResultCollector{file: file}
    _ = schematron.NewValidator(schema).
        Label(file).
        ErrorHandler(collector).
        Validate(ctx, doc)

    return collector.results, nil
}
```

The `schResultCollector` implements `helium.ErrorHandler`:

```go
type schResultCollector struct {
    results []SchValidateResult
    file    string
}

func (c *schResultCollector) Handle(_ context.Context, err error) {
    msg := err.Error()
    severity := "error"
    testType := "assert"
    if strings.Contains(msg, "report:") ||
        strings.Contains(strings.ToLower(msg), "report") {
        severity = "info"
        testType = "report"
    }
    c.results = append(c.results, SchValidateResult{
        File:     c.file,
        Message:  msg,
        Type:     testType,
        Severity: severity,
    })
}
```

The severity classification uses heuristic string matching because helium's `ValidationError` does not expose a structured field that distinguishes asserts from reports. The error message contains the word "report" when a `<xsl:report>` rule fires, and contains "error" or "assert" when a `<xsl:assert>` rule fails. This heuristic works for all Schematron schemas compiled by helium because the error message format is controlled by the validation engine.

The returned error from `Validate` is discarded (`_ =`). This is intentional. The validator returns `ErrValidationFailed` when any assertion fails, but the CLI does not treat this as a command-level error. Instead, the structured results in `collector.results` are emitted as Glazed rows, and the command layer decides the exit code based on whether any result has severity `error`.

### A concrete validation trace

Given a Schematron schema:

```xml
<schema xmlns="http://www.ascc.net/xml/schematron">
  <pattern name="book-rules">
    <rule context="book">
      <assert test="title">Book must have a title</assert>
      <assert test="author or editor">Book must have an author or editor</assert>
    </rule>
  </pattern>
</schema>
```

And a document without a title:

```xml
<book><author>Jane Doe</author></book>
```

The `schResultCollector` receives one error from the validator: the first assert (`test="title"`) evaluated to false because the `book` element has no `title` child. The collector classifies it as `severity: "error"`, `type: "assert"`. The `SchValidateResult`:

```json
{
  "file": "book-no-title-sch.xml",
  "message": "book-no-title-sch.xml:3: element book: schematron error : /book line 3: Book must have a title\n",
  "pattern": "",
  "rule": "",
  "severity": "error",
  "type": "assert"
}
```

The `pattern` and `rule` fields are empty because helium's `ValidationError` does not expose the originating pattern and rule names. The message text contains the context and the assertion message, which is the most specific information available.

For a document that passes all assertions, the collector receives no errors, and the returned slice is empty. The validate command emits zero rows and exits with code 0.

## Schematron commands: five operations on one compiled schema

The five `xml sch` commands all begin by compiling the Schematron schema. They differ in what they do with the compiled result and how they present it.

| Command | Operation | Output |
|---------|-----------|--------|
| `xml sch validate` | Validate one document | Error rows per failed assert / fired report |
| `xml sch compile` | Compile the schema | Single row confirming compilation |
| `xml sch test` | Validate one document | Single row: PASS or FAIL |
| `xml sch report` | Validate one document | Detailed rows with pattern, rule, message |
| `xml sch coverage` | Validate a corpus | Rows per rule with hits and status |

The compile command is the simplest — it compiles the schema and returns a row with `status: "compiled"`. Its value is in confirming that the schema is syntactically valid without running it against any document. A CI pipeline can use `xml sch compile` as a fast check before running the more expensive validation step.

The test command wraps validation in a pass/fail verdict. It counts error-severity results and produces a single row with `result: PASS` or `result: FAIL`. This is useful in test harnesses that need a binary outcome rather than a list of errors:

```bash
xml sch test --schema rules.sch valid-doc.xml
# → file=valid-doc.xml result=PASS errors=0 total=0

xml sch test --schema rules.sch invalid-doc.xml
# → file=invalid-doc.xml result=FAIL errors=1 total=1
```

The report command is validation with a different column selection. It includes the `pattern` and `rule` columns even when they are empty, providing a consistent schema for report consumers:

```bash
xml sch report --schema rules.sch doc.xml --output json
# → {file, severity, type, pattern, rule, message}
```

The coverage command is the most complex of the five. It walks a directory, collects all `.xml` files, and validates each against the compiled schema. The results are aggregated per rule.

## Schematron coverage: which rules fire against which documents

Coverage analysis answers the question: do my Schematron rules actually exercise the documents in my corpus? A rule that never fires against any corpus document might be dead code, or it might indicate a gap in the test data.

### The coverage algorithm

```pseudocode
function SchCoverageAnalysis(schema, corpusPaths, noNetwork):
    ruleHits  = empty map  // rule key → count of documents where rule fired
    ruleFails = empty map  // rule key → count of documents where rule produced errors

    for each path in corpusPaths:
        results = SchValidate(schema, path, noNetwork)
        for each result in results:
            key = result.Rule
            if key is empty:
                key = result.Message  // fall back to message text
            ruleHits[key]++
            if result.Severity == "error":
                ruleFails[key]++

    coverage = empty list
    for each key in ruleHits:
        status = "covered"
        if ruleFails[key] > 0:
            status = "failed"
        append SchCoverage{Rule: key, Hits: hits[key], Status: status}

    return coverage
```

The rule key is the `Rule` field from `SchValidateResult`. When this field is empty — which is currently always the case because helium's `ValidationError` does not expose the rule name — the function falls back to the `Message` field. This means each unique error message is treated as a distinct rule. Two documents that trigger the same assert with the same message are counted as two hits on the same rule. Two documents that trigger different asserts produce two distinct rule entries.

The status classification:

| Condition | Status | Meaning |
|-----------|--------|---------|
| `ruleFails[key] > 0` | `failed` | The rule produced at least one error in at least one document |
| `ruleFails[key] == 0 && ruleHits[key] > 0` | `covered` | The rule fired but only as informational reports |
| `key not in ruleHits` | (omitted) | The rule never fired — it is uncovered |

The uncovered case is not emitted because the function does not have access to the full list of rules in the schema. The `schematron.Schema` struct's `patterns` field is unexported, so the CLI cannot enumerate all rules and check which ones never fired. A future version could walk the schema DOM directly (as the XSLT static analysis does) to extract the complete rule list and emit explicit "uncovered" entries.

### A concrete coverage trace

Running coverage against a corpus directory containing one document that fails the "Book must have a title" assert:

```bash
xml sch coverage --schema rules.sch --corpus testdata/invalid/
```

Output:

```json
{
  "rule": "book-no-title-sch.xml:3: element book: schematron error : /book line 3: Book must have a title\n",
  "hits": 1,
  "status": "failed"
}
```

Running against a corpus of valid documents produces no output rows because no rules fire. This is the "no evidence of coverage" case — the rules exist in the schema, but the corpus does not exercise them. The developer who sees empty coverage output knows they need to add documents that trigger the rules, or they need to add reports (not just asserts) to their Schematron schema so that positive validation outcomes also produce visible results.

## XSLT compilation and execution

The helium `xslt3` package provides XSLT 3.0 compilation and execution. The compilation path is:

```text
Read file → Parse XML → CompileStylesheet → Stylesheet
```

And the execution path is:

```text
Stylesheet.Transform(doc) → Invocation → Invocation.Do(ctx) → Result Document
```

### Compilation

The `CompileXSLT` function reads the stylesheet file, parses it as XML, and compiles it:

```go
func CompileXSLT(ctx context.Context, path string) (*xslt3.Stylesheet, error) {
    abs, _ := filepath.Abs(path)
    buf, _ := os.ReadFile(abs)
    doc, _ := helium.NewParser().Parse(ctx, buf)
    ss, err := xslt3.CompileStylesheet(ctx, doc)
    if err != nil {
        return nil, fmt.Errorf("compiling stylesheet: %w", err)
    }
    return ss, nil
}
```

The compilation is expensive — it walks the stylesheet DOM, resolves imports, compiles XPath expressions, builds template tables, and checks for circular dependencies. The compiled `Stylesheet` is a rich object with 30+ fields. But these fields are all unexported, which is the central constraint that shapes the XSLT static analysis design.

### Execution

The `XSLTRun` function compiles the stylesheet, parses the input document, builds an invocation, and executes it:

```go
func XSLTRun(ctx context.Context, stylesheetPath, inputPath string,
    params map[string]string, outputPath string, noNetwork bool) (*XSLTRunResult, error) {

    ss, _ := CompileXSLT(ctx, stylesheetPath)

    inputBuf, _ := os.ReadFile(inputPath)
    parser := helium.NewParser()
    if noNetwork {
        parser = parser.AllowNetwork(false)
    }
    inputDoc, _ := parser.Parse(ctx, inputBuf)

    inv := ss.Transform(inputDoc)

    // Parameter setting is a known limitation (see below)
    for name, value := range params {
        _ = name
        _ = value
    }

    result, err := inv.Do(ctx)
    if err != nil {
        return nil, fmt.Errorf("executing transformation: %w", err)
    }

    // Serialize the result document
    var resultStr string
    if result != nil {
        writer := helium.NewWriter()
        var out strings.Builder
        writer.WriteTo(&out, result)
        resultStr = out.String()
    }

    // Write to file or return in result
    outputDest := "stdout"
    if outputPath != "" {
        os.WriteFile(outputPath, []byte(resultStr), 0644)
        outputDest = "file"
    }

    return &XSLTRunResult{...}, nil
}
```

The execution follows a builder pattern. `ss.Transform(inputDoc)` returns an `Invocation` object. The invocation can be configured with initial template calls, global parameters, and output definitions before calling `Do(ctx)`. The `Do` method returns a `*helium.Document` — the transformed result as a DOM tree.

### The parameter passing limitation

The `Invocation` type supports a `SetParameter(name string, value xpath3.Sequence)` method for setting global stylesheet parameters. The `value` argument must be an `xpath3.Sequence`, which is the XPath 3.1 data model representation. Constructing a sequence from a plain string requires either:

1. Calling `xpath3.StringToSequence(s)` (if such a function exists)
2. Parsing the string as an XPath expression and evaluating it
3. Manually constructing a sequence containing a single text node

None of these paths are straightforward in helium's current API. The `xpath3` package provides `Sequence` as an interface with multiple implementations (node sequences, atomic value sequences, empty sequences), and the correct construction depends on the parameter's declared type in the stylesheet.

The current implementation accepts `--params "key1=val1,key2=val2"` and parses the key-value pairs, but does not pass them to the invocation. This is documented as a known limitation. A future version will need to either add a convenience function in the engine layer that wraps `xpath3.Sequence` construction, or require the user to specify the type of each parameter so the engine can construct the correct sequence.

### Serialization

The result document is serialized using `helium.NewWriter()`, which produces XML output. The writer respects the stylesheet's `<xsl:output>` declaration (method, encoding, indentation, etc.) because the compiled stylesheet's output definition is applied during serialization. The `WriteTo` method takes an `io.Writer` and a `*helium.Document`, producing the final text output.

## XSLT static analysis: why DOM walking is necessary

The compiled `xslt3.Stylesheet` struct contains all the information that `xml xsl list`, `xml xsl refs`, `xml xsl unused`, and `xml xsl graph` need: templates, functions, variables, imports, and their relationships. But every field in the struct is unexported:

```go
type Stylesheet struct {
    version              string
    templates            []*template
    namedTemplates       map[string]*template
    modeTemplates        map[string][]*template
    globalVars           []*variable
    globalParams         []*param
    functions            map[funcKey]*xslFunction
    // ... 25 more unexported fields
}
```

Go's visibility rules prevent the CLI from accessing any of these fields. The `Stylesheet` type does not expose accessor methods for templates, functions, or variables. It only exposes `Transform`, `ApplyTemplates`, `CallTemplate`, `CallFunction`, and `DefaultOutputDef`.

This means the CLI has two choices:

1. Add accessor methods to the `Stylesheet` type in the helium library.
2. Parse the raw XSLT document and extract information from the DOM.

Option 1 requires modifying the upstream library, which is outside the scope of the CLI project. Option 2 is what `ParseStylesheet` implements.

### The ParseStylesheet function

`ParseStylesheet` reads the XSLT file, parses it as XML, and walks the DOM tree to find elements in the XSL namespace:

```go
func ParseStylesheet(ctx context.Context, path string) (
    []XSLTTemplate, []XSLTFunction, []XSLTVariable, []XSLTImport, error) {

    buf, _ := os.ReadFile(path)
    doc, _ := helium.NewParser().Parse(ctx, buf)

    var templates []XSLTTemplate
    var functions []XSLTFunction
    var variables []XSLTVariable
    var imports []XSLTImport

    root := doc.DocumentElement()
    walkXSLTElements(root, &templates, &functions, &variables, &imports)

    return templates, functions, variables, imports, nil
}
```

### The walk function

The walk function checks each element's namespace URI against the XSL namespace and dispatches on the local name:

```go
func walkXSLTElements(elem *helium.Element,
    templates *[]XSLTTemplate, functions *[]XSLTFunction,
    variables *[]XSLTVariable, imports *[]XSLTImport) {

    local := elem.LocalName()
    ns := ""
    if elemNs := elem.Namespace(); elemNs != nil {
        ns = elemNs.URI()
    }

    if ns == "http://www.w3.org/1999/XSL/Transform" {
        switch local {
        case "template":
            t := XSLTTemplate{
                Name:       getAttr(elem, "name"),
                Match:      getAttr(elem, "match"),
                Mode:       getAttr(elem, "mode"),
                Visibility: getAttr(elem, "visibility"),
            }
            *templates = append(*templates, t)
        case "function":
            f := XSLTFunction{Name: getAttr(elem, "name")}
            *functions = append(*functions, f)
        case "variable":
            v := XSLTVariable{
                Name:   getAttr(elem, "name"),
                Type:   "variable",
                Select: getAttr(elem, "select"),
            }
            *variables = append(*variables, v)
        case "param":
            v := XSLTVariable{
                Name:   getAttr(elem, "name"),
                Type:   "parameter",
                Select: getAttr(elem, "select"),
            }
            *variables = append(*variables, v)
        case "import":
            imp := XSLTImport{Href: getAttr(elem, "href"), Type: "import"}
            *imports = append(*imports, imp)
        case "include":
            imp := XSLTImport{Href: getAttr(elem, "href"), Type: "include"}
            *imports = append(*imports, imp)
        }
    }

    // Recurse into children
    for child := elem.FirstChild(); child != nil; child = child.NextSibling() {
        if childElem, ok := child.(*helium.Element); ok {
            walkXSLTElements(childElem, templates, functions, variables, imports)
        }
    }
}
```

The namespace check `ns == "http://www.w3.org/1999/XSL/Transform"` ensures that non-XSL elements are skipped. A stylesheet that embeds HTML or documentation elements in a different namespace will not produce spurious findings.

The recursion uses `FirstChild()` and `NextSibling()` to walk the entire DOM tree. This catches `<xsl:template>` elements nested inside `<xsl:stylesheet>` and also catches `<xsl:param>` elements nested inside `<xsl:template>` (local parameters). The current implementation records local parameters alongside global parameters in the `variables` slice — they are distinguished by the `Type` field, which is `"parameter"` for both, but a local parameter could be further distinguished by tracking the parent template name.

### What DOM walking captures and what it misses

DOM walking captures the syntactic structure of the stylesheet: what elements exist, what attributes they have, and how they are nested. It does not capture the compiled structure: resolved imports, template priority computation, import precedence, or the effective type of a variable's `select` expression.

This distinction matters for the `unused` command. A named template is flagged as unused only if no other named template or function in the same stylesheet references it. But DOM walking does not trace `<xsl:call-template name="...">` or `<xsl:apply-templates select="...">` inside template bodies — it only records the top-level declarations. A future version could extend the walk to scan template bodies for call-template references, but this would require parsing XPath expressions within `select` attributes, which is beyond what a simple attribute extraction can do.

The current `FindUnusedTemplates` function uses a conservative heuristic: match-only templates (those with a `match` attribute and no `name`) are always considered potentially used because they can be invoked by `<xsl:apply-templates>`. Named templates without a match attribute are considered unused unless they share a name with another template that has a match attribute:

```go
func FindUnusedTemplates(templates []XSLTTemplate,
    functions []XSLTFunction, variables []XSLTVariable) []XSLTTemplate {

    referenced := map[string]bool{}

    // All match templates are potentially used by apply-templates
    for _, t := range templates {
        if t.Match != "" {
            referenced[t.Name] = true
        }
    }

    var unused []XSLTTemplate
    for _, t := range templates {
        if t.Name == "" {
            continue // anonymous match templates are always potentially used
        }
        if !referenced[t.Name] {
            unused = append(unused, t)
        }
    }

    return unused
}
```

A template like `<xsl:template name="f:format-date">` with no `match` attribute is flagged as unused if no other template in the stylesheet shares the name `f:format-date`. This is a reasonable first approximation, but it has false negatives — a template that is called from a stylesheet module that imports this one would be marked unused even though it is used. The limitation follows from the static analysis not resolving imports.

### A concrete list trace

Given a stylesheet with 5 templates, 1 function, 2 global variables, and 2 local parameters:

```bash
xml xsl list --stylesheet book-transform.xsl --output json
```

Output (abbreviated):

```json
{"kind": "template", "name": "",          "match": "/",     "mode": "", "visibility": ""}
{"kind": "template", "name": "",          "match": "book",  "mode": "", "visibility": ""}
{"kind": "template", "name": "",          "match": "title", "mode": "", "visibility": ""}
{"kind": "template", "name": "",          "match": "author","mode": "", "visibility": ""}
{"kind": "template", "name": "f:format-date", "match": "", "mode": "", "visibility": ""}
{"kind": "function", "name": "f:normalize-text", "match": "", ...}
{"kind": "parameter","name": "debug",     ...}
{"kind": "variable", "name": "version",   ...}
{"kind": "parameter","name": "date",     ...}
{"kind": "parameter","name": "text",     ...}
```

The two trailing parameters (`date`, `text`) are local parameters declared inside the `f:format-date` template and the `f:normalize-text` function. They appear in the list because the DOM walk recurses into template bodies. A future version could add a `scope` column to distinguish global from local declarations.

## XSLT dependency graphs

The `xml xsl graph` command produces a dependency graph of stylesheet components. The graph is built from the static analysis results:

```go
func BuildXSLTGraph(analysis *XSLTStaticAnalysis) *XSLTGraph {
    graph := &XSLTGraph{}
    seen := map[string]bool{}

    addNode := func(id, label, kind string) {
        if !seen[id] {
            graph.Nodes = append(graph.Nodes, XSLTGraphNode{
                ID: id, Label: label, Kind: kind,
            })
            seen[id] = true
        }
    }

    for _, t := range analysis.Templates {
        id := templateNodeID(t)
        label := t.Name
        if label == "" {
            label = t.Match
        }
        addNode(id, label, "template")
    }

    for _, f := range analysis.Functions {
        addNode("fn_"+safeID(f.Name), f.Name, "function")
    }

    for _, v := range analysis.Variables {
        addNode("var_"+safeID(v.Name), v.Name, v.Type)
    }

    for _, imp := range analysis.Imports {
        id := "ss_" + safeID(imp.Href)
        addNode(id, imp.Href, "stylesheet")
        graph.Edges = append(graph.Edges, XSLTGraphEdge{
            From: "root", To: id, Kind: imp.Type,
        })
    }

    return graph
}
```

The node IDs are sanitized versions of the component names, replacing characters that are invalid in Mermaid and DOT identifiers (`{`, `}`, `:`, `/`, `.`, ` `, `-`) with underscores. The `safeID` function:

```go
func safeID(s string) string {
    r := strings.NewReplacer(
        "{", "_", "}", "_", ":", "_", "/", "_",
        ".", "_", " ", "_", "-", "_",
    )
    return r.Replace(s)
}
```

The graph currently only produces edges for import and include relationships. Call-graph edges (which template calls which template) would require tracing `<xsl:call-template>` and `<xsl:apply-templates>` inside template bodies, which is not yet implemented.

### Mermaid and DOT rendering

The `XSLTGraphToMermaid` function renders the graph in Mermaid syntax:

```text
graph TD
  tmpl_match__[["/"]]
  tmpl_match_book["book"]
  tmpl_match_title["title"]
  tmpl_match_author["author"]
  tmpl_f_format_date["f:format-date"]
  fn_f_normalize_text["f:normalize-text"]
  var_debug["debug"]
  var_version["version"]
```

The `XSLTGraphToDOT` function renders in Graphviz DOT syntax:

```text
digraph xslt {
  rankdir=TB;
  tmpl_match__ [label="/"];
  tmpl_match_book [label="book"];
  ...
}
```

Both renderers are straightforward string builders. The choice of format depends on the consumer: Mermaid is rendered natively by GitHub, Obsidian, and many documentation tools. DOT requires a separate Graphviz invocation but produces publication-quality images with layout control.

## The `xml xsl run` command: end-to-end transformation

The run command combines compilation, execution, and serialization into one invocation. The CLI flags are:

| Flag | Purpose | Default |
|------|---------|---------|
| `--stylesheet` | XSLT file path | required |
| `--input` | Input XML file path | required |
| `--xml-output` | Output file path | stdout |
| `--params` | Comma-separated key=value parameters | none |
| `--no-network` | Block network access | false |

The `--xml-output` flag is named with the `xml-` prefix to avoid collision with Glazed's built-in `--output` flag, which controls the output format (json, table, csv, yaml). This is the same approach used for `xml lint --xml-output` in Part 1.

### Output destination logic

When `--xml-output` is not specified, the transformation result is included in the Glazed row under the `result` field. When `--xml-output` is specified, the result is written to the file and the row records only the destination and size:

```go
row := types.NewRow(
    types.MRP("stylesheet", s.Stylesheet),
    types.MRP("input", s.Input),
    types.MRP("output-dest", outputDest),
    types.MRP("output", s.Output),
    types.MRP("result-size", fmt.Sprintf("%d", result.ResultSize)),
)
if s.Output == "" && result != nil {
    row.Set("result", result.Output)
}
```

This design supports two workflows. In interactive use, the developer pipes the result to stdout or inspects it in JSON format. In batch use, the developer writes to a file and gets a structured summary row for logging.

## The `xml xsl deps` and `xml xsl refs` commands

The deps command lists import and include dependencies. It uses the `imports` return value from `ParseStylesheet`:

```bash
xml xsl deps --stylesheet transform.xsl
```

For a stylesheet that imports a utility module and includes a shared definitions file:

```json
{"type": "import",  "href": "utils.xsl"}
{"type": "include", "href": "defs.xsl"}
```

The distinction between import and include matters for import precedence. XSLT's `<xsl:import>` gives the importing stylesheet higher precedence than the imported one, while `<xsl:include>` gives equal precedence. A developer who sees an import can predict that template overrides in the importing module take priority; an include means both modules contribute at the same precedence level.

The refs command searches for a named template or function across the parsed stylesheet. It checks template names, match patterns (for substring matches), function names, and variable names. This is useful for answering "where is this template used?" before refactoring:

```bash
xml xsl refs --stylesheet transform.xsl --name f:normalize
```

The search is by exact match on names and substring match on match patterns. A match pattern like `book|article` that contains the substring `book` will match a search for `book`, even though the pattern is not exclusively about books. This is a known imprecision — a future version could parse match patterns as union expressions and check each alternative individually.

## Command registration: the sch and xsl parents

Both `xml sch` and `xml xsl` follow the same registration pattern established in Part 2 for `xml schema` and `xml dtd`:

```go
func Register(root *cobra.Command) error {
    schCmd := &cobra.Command{
        Use:   "sch",
        Short: "Schematron validation, compilation, and coverage",
        Long: `Schematron sub-commands for rule-based validation,
schema compilation, testing, reporting, and coverage analysis.`,
    }

    commands := []struct {
        name string
        cmd  cmds.GlazeCommand
    }{
        {"validate", mustCmd(NewValidateCommand())},
        {"compile",  mustCmd(NewCompileCommand())},
        {"test",     mustCmd(NewTestCommand())},
        {"report",   mustCmd(NewReportCommand())},
        {"coverage", mustCmd(NewCoverageCommand())},
    }

    for _, c := range commands {
        cobraCmd, err := cli.BuildCobraCommandFromCommand(c.cmd,
            cli.WithParserConfig(cli.CobraParserConfig{
                AppName:           "xml",
                ShortHelpSections: []string{slug},
                MiddlewaresFunc:   cli.CobraCommandDefaultMiddlewares,
            }),
        )
        if err != nil {
            return fmt.Errorf("building %s command: %w", c.name, err)
        }
        schCmd.AddCommand(cobraCmd)
    }

    root.AddCommand(schCmd)
    return nil
}
```

The `mustCmd` helper panics on construction errors, which is acceptable during initialization because these errors are programming mistakes (invalid field definitions, conflicting flag names), not runtime conditions.

Each command follows the three-struct pattern: the command struct embeds `*cmds.CommandDescription`, the settings struct maps flags to typed Go fields with `glazed:` tags, and the `RunIntoGlazeProcessor` method implements the command logic. This pattern is consistent across all 11 Phase 3 commands and all 21 commands from Parts 1 and 2.

## Test design for Phase 3

Phase 3 adds 19 unit tests to the engine package, bringing the total from 176 to 195.

### Schematron tests (6 tests)

- `TestCompileSchematron_Valid` — compiling a real Schematron file produces a non-nil `Schema`
- `TestCompileSchematron_NonexistentFile` — nonexistent path returns an error
- `TestSchValidate_ValidDoc` — a valid document produces zero results
- `TestSchValidate_InvalidDoc` — an invalid document produces at least one error-severity result
- `TestSchValidate_NonexistentFile` — validating a nonexistent file returns an error
- `TestSchCoverageAnalysis` — coverage analysis against a corpus produces non-empty coverage data

### XSLT compilation and execution tests (6 tests)

- `TestCompileXSLT_Valid` — compiling a real XSLT file produces a non-nil `Stylesheet`
- `TestCompileXSLT_NonexistentFile` — nonexistent path returns an error
- `TestXSLTRun_Transformation` — running a transformation produces a non-empty result
- `TestXSLTRun_NonexistentStylesheet` — nonexistent stylesheet returns an error
- `TestXSLTRun_NonexistentInput` — nonexistent input file returns an error
- `TestXSLTRun_OutputFile` — writing to an output file produces `OutputDest: "file"` and the file exists

### XSLT static analysis tests (7 tests)

- `TestParseStylesheet_Valid` — parsing produces non-empty template, function, and variable slices
- `TestParseStylesheet_NonexistentFile` — nonexistent file returns an error
- `TestParseStylesheet_TemplateDetails` — the root template (`match="/"`) and the named template (`name="f:format-date"`) are both found
- `TestFindUnusedTemplates` — a named template without a match attribute and without a matching name elsewhere is flagged as unused
- `TestBuildXSLTGraph` — building a graph from a static analysis produces non-empty nodes
- `TestXSLTGraphToMermaid` — Mermaid output starts with `graph TD`
- `TestXSLTGraphToDOT` — DOT output starts with `digraph xslt`

### Test data

Phase 3 adds one test data file:

- `test/testdata/schemas/book-transform.xsl` — an XSLT 3.0 stylesheet with 5 templates (4 match-only, 1 named), 1 function, 2 global variables/parameters, and 2 local parameters. The named template `f:format-date` has no call-site, making it the expected unused template.

## Architecture at this point

After Phase 3, the tool contains 12 top-level commands and 32 subcommands:

| Command | Subcommands | Phase |
|---------|------------|-------|
| `xml validate` | (standalone) | 1 |
| `xml lint` | (standalone) | 1 |
| `xml xpath` | (standalone) | 1 |
| `xml catalog` | init, add, resolve, check | 1 |
| `xml explain-error` | (standalone) | 1 |
| `xml schema` | explain, graph, lint, refs, infer, diff, breakage, list | 2 |
| `xml dtd` | inspect, flatten, entities, audit | 2 |
| `xml sch` | validate, compile, test, report, coverage | 3 |
| `xml xsl` | run, list, refs, unused, graph, deps | 3 |

The engine layer contains 7,762 lines of production code across 14 source files. The test layer contains 2,926 lines across 11 test files. All 195 tests pass.

## What comes next

Phase 4 adds interactive and integration features. The `xml validate --tui` command launches a Bubble Tea terminal UI that shows validation results in real time as documents are edited. The `xmlls` language server provides completion, hover, diagnostics, and go-to-definition for XML, XSD, and XSLT files. The `xml generate sample` and `xml generate invalid` commands produce synthetic test data from a schema. Rich HTML validation reports produce a standalone web page from a validation run.

The architecture supports these additions without restructuring. The `CompileSchematron` pattern will be reused for the TUI's watch-and-revalidate loop. The `ParseStylesheet` function will be extended to support the language server's symbol resolution. The `InferredSchemaToXSD` function from Part 2 provides the foundation for sample generation. The domain primitives continue to grow in capability without changing in shape.
