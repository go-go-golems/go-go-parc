---
title: "Deep Dive: Building a Modern XML CLI in Go — Part 2"
aliases:
  - XML CLI Part 2
  - Schema Workbench
  - DTD Tooling
tags:
  - article
  - go
  - xml
  - helium
  - glazed
  - cli
  - schema
  - xsd
  - dtd
  - diff
  - inference
status: active
type: article
created: 2026-05-11
repo: /home/manuel/code/wesen/2026-05-11--helium-xml-tool
---

# Deep Dive: Building a Modern XML CLI in Go — Part 2

This article is the second in a series about building `xml`, a production-grade command-line tool for XML processing in Go. Part 1 covered the three-layer architecture, the validation pipeline, and the Glazed command skeleton. This part covers the Phase 2 additions: the schema workbench and DTD subcommands. By the end of Part 2, you will understand how to introspect a compiled XSD schema's type graph, how schema inference turns raw documents into type declarations, how semantic diff classifies changes as breaking or safe, and how a regex-based DTD parser detects billion laughs attacks.

The target audience is a developer who read Part 1 and wants to see how the engine layer extends beyond validation into schema analysis, or a developer who maintains XSD schemas and needs tooling that `xmllint` does not provide.

> [!summary]
> This article covers four core ideas:
> 1. Schema introspection through the XSD `Schema` type: how `NamedTypes()`, `LookupType()`, and the `TypeDef` tree provide enough structure for explain, graph, lint, and refs without parsing raw XSD.
> 2. Schema inference from documents: how walking helium's DOM with `DocumentElement()`, `FirstChild()`, `ForEachAttribute()` produces an `InferredSchema`, and how simple type widening (boolean → integer → decimal → string) works.
> 3. Semantic diff and breakage analysis: how comparing two type maps classifies changes by severity, and why inherited attributes produce false positives.
> 4. DTD analysis with regex parsing: how a non-validating parser extracts declarations and detects entity expansion attacks.

## The problem Part 2 solves

Validation tells you whether a document conforms to a schema. That is necessary but not sufficient. A schema author also needs to understand what a schema contains, see how its components relate, know which components are unused, compare two versions to find breaking changes, and generate a starting schema from example data. These are authoring tasks, not validation tasks, and they require a different kind of engine access — not the `Validator` that checks documents, but the `Schema` object that represents the compiled type system.

The same gap exists for DTDs. DTDs are still common in publishing, government, and SGML-migration contexts. Tooling for DTDs is thin: `xmllint` can validate against a DTD, but it cannot inspect the DTD's declarations, flatten its parameter entity includes, or flag dangerous entity expansion patterns. The `xml dtd` commands fill this gap.

## The XSD Schema object as a query target

The helium `xsd` package compiles an XSD file into a `Schema` struct. This struct is not just a validation artifact — it is a queryable representation of the type system. Every named type, every element declaration, every attribute use, and every content model is accessible through typed Go fields.

The key insight: once the schema is compiled, the CLI does not need to re-parse the XSD source. It queries the `Schema` object directly.

### What the Schema type exposes

The `Schema` struct provides five access methods:

| Method | Returns | Purpose |
|--------|---------|---------|
| `NamedTypes()` | `[]QName` | All named type definitions, sorted by namespace then local name |
| `LookupType(local, ns)` | `*TypeDef, bool` | Look up a type by name |
| `LookupElement(local, ns)` | `*ElementDecl, bool` | Look up a global element by name |
| `SubstGroupMembers(head)` | `[]*ElementDecl` | Members of a substitution group |
| `TargetNamespace()` | `string` | The schema's target namespace |

The `TypeDef` struct is the richest type in the hierarchy:

```go
type TypeDef struct {
    Name         QName
    ContentType  ContentTypeKind   // empty, simple, element-only, mixed
    ContentModel *ModelGroup        // the particle tree for complex types
    BaseType     *TypeDef            // nil for root types
    Attributes   []*AttrUse         // declared and inherited attributes
    Derivation   DerivationKind     // extension, restriction, or none
    Facets       *FacetSet           // enumeration, pattern, length constraints
    Variety      TypeVariety         // atomic, list, or union
    ItemType     *TypeDef            // for list types
    MemberTypes  []*TypeDef         // for union types
    Abstract     bool
}
```

The `ModelGroup` and `Particle` types form a recursive tree:

```text
ModelGroup
├── Compositor: sequence | choice | all
├── MinOccurs, MaxOccurs
└── Particles[]
    ├── ElementDecl (term)
    ├── ModelGroup (term, recursive)
    └── Wildcard (term, xs:any)
```

This tree is exactly what `xml schema explain` walks to produce child element lists, and what `xml schema graph` walks to produce dependency edges.

### The explain command: from type tree to prose

The explain command takes a QName and produces a `TypeExplanation` struct with a generated prose description. For the `GenreType` in the book schema:

```bash
xml schema explain --schema book-full.xsd --name GenreType --namespace http://example.com/book
```

The output includes:

```json
{
  "kind": "simple-type",
  "content-type": "simple",
  "base-type": "{http://www.w3.org/2001/XMLSchema}string",
  "derivation": "restriction",
  "enumeration": ["fiction", "non-fiction", "technical", "poetry"],
  "description": "simple-type {http://example.com/book}GenreType. Base type: {http://www.w3.org/2001/XMLSchema}string (derived by restriction). Allowed values: fiction, non-fiction, technical, poetry"
}
```

The `description` field is the key output. It is generated by `buildTypeDescription`, which walks the `TypeDef` fields and concatenates sentences:

```go
func buildTypeDescription(td *xsd.TypeDef, expl *TypeExplanation) string {
    var b strings.Builder
    fmt.Fprintf(&b, "%s {%s}%s", expl.Kind, expl.Namespace, expl.Name)

    if expl.ContentType != "" && expl.Kind == "complex-type" {
        fmt.Fprintf(&b, " with %s content", expl.ContentType)
    }

    if expl.BaseType != "" {
        fmt.Fprintf(&b, ". Base type: %s", expl.BaseType)
        if expl.Derivation != "" {
            fmt.Fprintf(&b, " (derived by %s)", expl.Derivation)
        }
    }

    if len(expl.Children) > 0 {
        fmt.Fprintf(&b, ". Child elements: %s", strings.Join(expl.Children, ", "))
    }
    // ... attributes, enumeration, pattern ...
    return b.String()
}
```

This is a simple template engine. The complexity is not in the formatting — it is in the data extraction. The `fillTypeDetails` function must correctly interpret `ContentType`, walk `ContentModel` to find child element names, extract attributes from `AttrUse` slices, and pull facets from the `FacetSet`.

### The child element walk

Extracting child element names from a `ModelGroup` requires recursive descent because particles can contain nested model groups:

```go
func collectElementNames(mg *xsd.ModelGroup, names *[]string) {
    for _, p := range mg.Particles {
        if elem, ok := p.Term.(*xsd.ElementDecl); ok {
            *names = append(*names, qnameStr(elem.Name))
        }
        if sub, ok := p.Term.(*xsd.ModelGroup); ok {
            collectElementNames(sub, names)
        }
    }
}
```

The type switch `p.Term.(type)` dispatches on the `ParticleTerm` interface, which has three implementations: `*ElementDecl`, `*ModelGroup`, and `*Wildcard`. The wildcard case is ignored for the explain command because it represents `xs:any`, which has no concrete element name.

## Schema dependency graphs

The graph command turns the `Schema` object into a directed graph of nodes and edges. The graph is built in a single pass over `NamedTypes()`:

```pseudocode
function BuildSchemaGraph(schema):
    graph = empty graph
    for each type in schema.NamedTypes():
        add node for type
        if type has base type:
            add base-type edge from type to base
        if type has content model:
            walk content model to find element refs
            for each element ref:
                add ref edge from type to element
                add type-of edge from element to element's type
    return graph
```

The graph can be rendered as Mermaid or DOT. Mermaid is useful for documentation and Markdown embedding; DOT is useful for producing images via Graphviz:

```bash
xml schema graph --schema book-full.xsd --graph-format mermaid
xml schema graph --schema book-full.xsd --graph-format dot | dot -Tpng -o schema.png
```

The Mermaid renderer color-codes nodes by kind:

| Kind | Color | Mermaid class |
|------|-------|---------------|
| Element | Green | `:::elem` |
| Complex type | Blue | `:::ctype` |
| Simple type | Orange | `:::stype` |
| Attribute group | Purple | `:::agroup` |
| Model group | Gray | `:::group` |

Edge styles encode the relationship:

| Edge kind | Style | Meaning |
|-----------|-------|---------|
| `type-of` | Solid `-->` | Element's declared type |
| `base-type` | Dashed `-.->` | Type derivation |
| `ref` | Solid `-->` | Content model reference |
| `subst-group` | Bold `==>` | Substitution group membership |

### A concrete graph trace

For the book schema, `BookType` contains seven child elements. Each child has a `type-of` edge to its declared type. `ExtendedBookType` has a `base-type` edge to `BookType`. The graph contains 45 edges for a schema with 6 user-defined types, because inheritance causes the base type's content model to be replicated in the derived type's particle tree.

This replication is a property of helium's internal representation, not a design choice of the CLI. When `ExtendedBookType` extends `BookType`, the compiled `TypeDef` for `ExtendedBookType` contains a full copy of `BookType`'s content model particles plus the extension particles. The graph builder walks this tree as-is, which produces duplicate edges for inherited content. Future versions could prune inherited content to produce cleaner graphs.

## Schema lint: finding dead code in the type system

Schema lint is static analysis for XSD. It answers the question: which parts of this schema are unreachable, unused, or overly complex?

### Unused type detection

A type is unused if no element declaration and no other type references it. The detection walks the type graph and collects all referenced type names, then subtracts from the full set:

```pseudocode
function LintSchema(schema):
    referenced = empty set
    for each type in schema.NamedTypes():
        if type.BaseType exists:
            add type.BaseType.Name to referenced
        for each element in type.ContentModel:
            add element.Type.Name to referenced
        for each member in type.MemberTypes:
            add member.Name to referenced
        if type.ItemType exists:
            add type.ItemType.Name to referenced

    for each type in schema.NamedTypes():
        if type.Name not in referenced:
            emit "unused-type" finding
```

XSD built-in types (namespace `http://www.w3.org/2001/XMLSchema`) are excluded from the findings. They are always present in a compiled schema and are rarely all referenced by user types. Without this filter, every schema would produce 40+ unused-type findings for types like `gYearMonth` and `unsignedByte`.

### Abstract types without concrete derivations

An abstract type that has no concrete derivation is unreachable by document instances. XSD requires that abstract types be used through `xsi:type` or substitution groups, and if neither exists, the type is dead code:

```go
if td.Abstract && td.ContentType != xsd.ContentTypeSimple {
    hasConcrete := false
    for _, qn2 := range schema.NamedTypes() {
        td2, _ := schema.LookupType(qn2.Local, qn2.NS)
        if td2 != nil && td2.BaseType == td && !td2.Abstract {
            hasConcrete = true
            break
        }
    }
    if !hasConcrete {
        findings = append(findings, SchemaLintFinding{
            Severity: "warning",
            Category: "unreachable-element",
            ...
        })
    }
}
```

### Deep nesting detection

A content model with nesting depth greater than 5 is flagged as a complexity warning. The depth is measured by the maximum recursion depth of `ModelGroup` → `Particle` → `ModelGroup` chains:

```go
func maxModelNesting(mg *xsd.ModelGroup, depth int) int {
    maxDepth := depth
    for _, p := range mg.Particles {
        if sub, ok := p.Term.(*xsd.ModelGroup); ok {
            d := maxModelNesting(sub, depth+1)
            if d > maxDepth {
                maxDepth = d
            }
        }
    }
    return maxDepth
}
```

The threshold of 5 is a heuristic. A content model with 6 levels of nested sequences and choices is not necessarily wrong, but it is likely to be difficult for humans to understand and for validators to process efficiently.

## Schema inference: from documents to declarations

Schema inference is the inverse of validation. Validation asks: does this document conform to this schema? Inference asks: what schema would this document conform to?

The implementation walks the DOM tree of each input document and builds an `InferredSchema` — a map from element names to `InferredElem` structs that record observed content models, attributes, cardinalities, and simple types.

### The walk function

The core of inference is `walkElement`, which is called recursively for every element in the document:

```pseudocode
function walkElement(elem, schema, opts):
    key = elementKey(elem.LocalName, elem.NamespaceURI)
    if schema.Elements[key] does not exist:
        create InferredElem for key
    ie = schema.Elements[key]
    ie.Count++

    // Analyze text content
    for each text child of elem:
        content = trim(text.Content())
        if content is not empty:
            ie.HasText = true
            if opts.SimpleTypes:
                ie.TextType = inferSimpleType(content, ie.TextType)
            if len(ie.EnumValues) < 50 and content not in ie.EnumValues:
                add content to ie.EnumValues

    // Analyze attributes
    elem.ForEachAttribute(func(attr):
        update or create InferredAttr for attr.LocalName())

    // Analyze child elements
    for each child element of elem:
        walkElement(child, schema, opts)
        record child occurrence count
```

This function uses the helium DOM API directly. The key calls are:

- `elem.LocalName()` — the element's local name
- `elem.Namespace().URI()` — the element's namespace URI
- `elem.FirstChild()` / `child.NextSibling()` — sibling iteration
- `child.(*helium.Element)` — type assertion to distinguish elements from text nodes
- `text.Content()` — the text content as `[]byte`
- `elem.ForEachAttribute(func(*helium.Attribute) bool)` — attribute iteration
- `attr.LocalName()`, `attr.URI()`, `attr.Value()` — attribute access

### Simple type inference

Type inference follows a widening rule: a type can only widen, never narrow. The widening chain is:

```text
boolean → integer → decimal → string
```

The logic for `inferSimpleType`:

1. If the current type is `string`, it is already the widest. Return immediately.
2. If the current type is `boolean` or empty, try to parse the value as boolean (`true`, `false`, `1`, `0`). If it fails, widen to `integer`.
3. If the current type is `integer` or empty, try to parse as integer (digits only, optional leading minus). If it fails, widen to `decimal`.
4. If the current type is `decimal` or empty, try to parse as decimal (digits with optional single dot). If it fails, widen to `string`.

```go
func inferSimpleType(value, currentType string) string {
    if currentType == "string" {
        return "string" // already widest
    }
    // Try boolean
    if currentType == "" || currentType == "boolean" {
        if value == "true" || value == "false" || value == "1" || value == "0" {
            if currentType == "" { return "boolean" }
            return currentType
        }
        if currentType == "boolean" { currentType = "integer" }
    }
    // Try integer, then decimal, then fall through to string
    // ...
    return "string"
}
```

This widening ensures that a field observed as `42` in one document and `hello` in another ends up as `string`, not as a type error. The inference is conservative — it never produces a type that would reject a previously observed value.

### Cardinality inference

Cardinality is inferred from occurrence counts. If an element appears in every occurrence of its parent, it is required. If it is absent from some parents, it is optional:

```go
func finalizeCardinalities(schema *InferredSchema) {
    for _, ie := range schema.Elements {
        for i := range ie.Children {
            child := &ie.Children[i]
            if child.Count < ie.Count {
                child.MinOccurs = 0  // optional
            }
            if child.MaxOccurs > 1 {
                child.MaxOccurs = -1  // unbounded
            }
        }
    }
}
```

The comparison `child.Count < ie.Count` means: this child was seen fewer times than the parent. Therefore some parent instances omitted this child. Therefore it is optional.

### XSD generation

The inferred schema is converted to XSD by `InferredSchemaToXSD`, which emits a `complexType` for each element with the observed content model, attributes, and simple types:

```xml
<xs:complexType name="BookType">
  <xs:sequence>
    <xs:element name="title" minOccurs="1"/>
    <xs:element name="author" minOccurs="1"/>
    <xs:element name="genre" minOccurs="1"/>
    <xs:element name="isbn" minOccurs="1"/>
    <xs:element name="price" minOccurs="1"/>
    <xs:element name="published" minOccurs="0"/>
    <xs:element name="description" minOccurs="0"/>
  </xs:sequence>
  <xs:attribute name="version" type="xs:string"/>
  <xs:attribute name="lang" type="xs:string" use="optional"/>
</xs:complexType>
```

This is a starting point, not a final product. Inferred schemas lack key XSD features: key constraints, substitution groups, type hierarchies, and named model groups. But they are correct enough to validate the documents they were inferred from, and they provide a human-editable skeleton that a schema author can refine.

## Semantic diff: comparing type systems

Schema diff compares two compiled XSD schemas and classifies every difference as `breaking`, `safe`, or `warning`. This is the operation that answers the question: can I deploy this schema change without breaking existing documents?

### The diff algorithm

The algorithm builds a type map from each schema and then compares them:

```pseudocode
function DiffSchemas(oldPath, newPath):
    oldSchema = CompileSchema(oldPath)
    newSchema = CompileSchema(newPath)
    oldTypes = buildTypeMap(oldSchema)  // name → TypeDef
    newTypes = buildTypeMap(newSchema)

    // Types in old but not new = removed (breaking)
    for name in oldTypes:
        if name not in newTypes:
            emit DiffChange{category: "type-removed", severity: "breaking"}

    // Types in new but not old = added (safe)
    for name in newTypes:
        if name not in oldTypes:
            emit DiffChange{category: "type-added", severity: "safe"}

    // Types in both = compare structure
    for name in oldTypes ∩ newTypes:
        compareTypes(name, oldTypes[name], newTypes[name])
```

### Severity classification

The severity of a change depends on whether it narrows or widens the type's constraints:

| Change | Narrowing or widening | Severity |
|--------|-----------------------|----------|
| Type removed | Eliminates a valid type | `breaking` |
| Type added | Introduces a new type | `safe` |
| Content type narrowed (e.g., mixed → empty) | Fewer valid documents | `breaking` |
| Content type widened (e.g., empty → mixed) | More valid documents | `safe` |
| Content type changed otherwise | Structural change | `warning` |
| Enumeration value removed | Fewer valid values | `breaking` |
| Enumeration value added | More valid values | `safe` |
| Required attribute added | Documents missing it become invalid | `breaking` |
| Optional attribute added | New information, existing docs valid | `safe` |
| Abstract → concrete | More instances possible | `safe` |
| Concrete → abstract | Existing instances may be invalid | `breaking` |
| MinLength tightened | Fewer valid values | `breaking` |
| MaxLength tightened | Fewer valid values | `breaking` |
| Pattern changed | Hard to classify automatically | `warning` |
| Base type changed | Structural change | `warning` |

This classification is sound but incomplete. Some changes that are classified as `warning` could be more precisely classified with deeper analysis. For example, a base type change from `string` to `integer` is clearly breaking, while a change from `string` to `token` is safe. The current implementation conservatively marks both as `warning` because it does not analyze the semantic relationship between the old and new base types.

### The inherited attribute problem

When helium compiles a schema with type derivation, the derived type's `Attributes` slice includes inherited attributes from the base type. This means that comparing `TextbookType`'s attributes between two compilations of the same schema can produce false positives if the internal representation differs.

The fix is to build an "inherited attributes" set from the base type chain and skip those attributes in the comparison:

```go
func buildInheritedAttrs(td *xsd.TypeDef) map[string]bool {
    inherited := map[string]bool{}
    if td.BaseType == nil {
        return inherited
    }
    for base := td.BaseType; base != nil; base = base.BaseType {
        for _, attr := range base.Attributes {
            inherited[qnameStr(attr.Name)] = true
        }
    }
    return inherited
}
```

Without this filter, diffing the same schema against itself would intermittently produce 2 false-positive "attribute removed" changes for `TextbookType`'s inherited `version` and `lang` attributes. The non-determinism comes from Go's map iteration order, which causes helium to sometimes include inherited attributes in the derived type's `Attributes` slice and sometimes not. The filter eliminates this class of false positive entirely.

### Breakage analysis with a corpus

The breakage command extends diff by validating a corpus of documents against the new schema. Without a corpus, breakage analysis classifies changes by severity alone (breaking changes get `affectedCount: -1`). With a corpus, each document is validated against the new schema, and the number of documents that fail is recorded:

```pseudocode
function AnalyzeBreakage(oldPath, newPath, corpusPaths):
    diff = DiffSchemas(oldPath, newPath)
    newSchema = CompileSchema(newPath)

    affectedFiles = empty set
    for each file in corpus:
        doc = Parse(file)
        errors = Validate(doc, newSchema)
        if errors > 0:
            add file to affectedFiles

    for each breaking change in diff:
        associate affectedFiles with the change

    return result
```

The corpus-based approach provides concrete evidence. A breaking change that affects 3 out of 500 documents is very different from one that affects 490 — the first is a low-impact migration, the second is a major incompatibility. The diff alone cannot make this distinction.

## DTD analysis: regex parsing and attack detection

DTDs are not well-formed XML. A DTD file contains `<!ELEMENT>`, `<!ATTLIST>`, `<!ENTITY>`, and `<!NOTATION>` declarations, but these are not wrapped in an XML document structure. They cannot be parsed by helium's XML parser.

The `xml dtd` commands use a regex-based parser instead. This parser is not a validating DTD processor — it does not build a content model or check declaration consistency. It extracts declarations for inspection, flattening, and safety analysis.

### The regex parser

The parser removes comments first, then applies four regex patterns:

```go
// ENTITY declarations (including multi-line)
entityRe := regexp.MustCompile(`(?s)<!ENTITY\s+(\S+)\s+(.*?)>`)

// ELEMENT declarations
elemRe := regexp.MustCompile(`<!ELEMENT\s+(\S+)\s+(.*?)>`)

// ATTLIST declarations (including multi-line)
attlistRe := regexp.MustCompile(`(?s)<!ATTLIST\s+(\S+)\s+(.*?)>`)

// NOTATION declarations
notationRe := regexp.MustCompile(`<!NOTATION\s+(\S+)\s+(.*?)>`)
```

The `(?s)` flag makes `.` match newlines, which is necessary for ATTLIST declarations that span multiple lines. This is a common pattern in DTDs where attributes are listed one per line:

```dtd
<!ATTLIST book version CDATA #IMPLIED
               lang CDATA "en">
```

Without `(?s)`, the regex would match only up to the first newline, missing the `lang` attribute.

The parser distinguishes general entities from parameter entities by checking for the `%` prefix:

```go
kind := "general-entity"
if strings.HasPrefix(name, "%") {
    kind = "parameter-entity"
    name = strings.TrimPrefix(name, "%")
}
```

It also distinguishes internal from external entities by checking for `SYSTEM` or `PUBLIC` keywords:

```go
entityType := "internal"
if strings.HasPrefix(value, "SYSTEM") || strings.HasPrefix(value, "PUBLIC") {
    entityType = "external"
}
```

### Billion laughs detection

The billion laughs attack (XML entity expansion attack) works by defining entities that reference other entities, causing exponential expansion:

```dtd
<!ENTITY boom "&boom1;&boom1;">
<!ENTITY boom1 "&boom2;&boom2;&boom2;&boom2;">
<!ENTITY boom2 "&boom3;&boom3;&boom3;&boom3;&boom3;&boom3;">
```

When an XML parser resolves `&boom;`, it expands to 2 × `&boom1;`, which expands to 2 × 4 × `&boom2;`, which expands to 2 × 4 × 6 × `&boom3;`. If each `&boom3;` is a small string, the total expansion is 48 copies — manageable. But if the pattern continues with more levels, the expansion becomes exponential.

The audit command detects this by counting entity references within each entity's value:

```go
func countEntityRefs(value string) int {
    re := regexp.MustCompile(`&[^;]+;|%[^;]+;`)
    return len(re.FindAllString(value, -1))
}
```

Entities with more than 5 references are flagged as `error` (potential billion laughs vector). Entities with more than 2 references are flagged as `warning`. The thresholds are conservative — a legitimate entity with 3 references is unusual but not dangerous.

### External entity warnings

External entities that reference local files are a security concern:

```dtd
<!ENTITY extdata SYSTEM "file:///etc/passwd">
```

The audit command flags all external entities with `severity: warning` and suggests disabling external entity resolution in production. This is the DTD equivalent of SSRF in web applications — the XML parser can be tricked into reading arbitrary files if it resolves external entities.

### Missing declaration detection

The audit checks for element declarations without ATTLIST declarations and ATTLIST declarations without matching element declarations:

```pseudocode
elemNames = all ELEMENT names
attlistElems = all ATTLIST element names

for name in elemNames:
    if name not in attlistElems:
        emit "missing-decl" info

for name in attlistElems:
    if name not in elemNames:
        emit "missing-decl" warning
```

An element without an ATTLIST is not necessarily a problem — many elements have no attributes. The finding is `info` severity because it is not an error, but it may indicate a forgotten attribute declaration. An ATTLIST without a matching element is more concerning — it declares attributes for an element that does not exist, which is likely a typo or a leftover from a refactoring.

## Command registration: the schema and dtd parents

Both `xml schema` and `xml dtd` are parent commands with subcommands. The registration pattern uses a Cobra parent command and adds Glazed subcommands:

```go
func Register(root *cobra.Command) error {
    schemaCmd := &cobra.Command{
        Use:   "schema",
        Short: "Schema authoring, analysis, and conversion",
    }

    commands := []struct {
        name string
        cmd  cmds.GlazeCommand
    }{
        {"explain", mustCmd(NewExplainCommand())},
        {"graph", mustCmd(NewGraphCommand())},
        {"lint", mustCmd(NewLintCommand())},
        {"refs", mustCmd(NewRefsCommand())},
        {"infer", mustCmd(NewInferCommand())},
        {"diff", mustCmd(NewDiffCommand())},
        {"breakage", mustCmd(NewBreakageCommand())},
        {"list", mustCmd(NewListCommand())},
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
        schemaCmd.AddCommand(cobraCmd)
    }

    root.AddCommand(schemaCmd)
    return nil
}
```

The `mustCmd` helper panics on error, which is acceptable during initialization because command construction failures are programming errors, not runtime conditions.

Each subcommand follows the same three-struct pattern established in Part 1. The `ExplainCommand` embeds `*cmds.CommandDescription`, `ExplainSettings` maps flags to typed Go fields with `glazed:` tags, and `RunIntoGlazeProcessor` implements the command logic.

## Test design for Phase 2

Phase 2 adds 28 unit tests to the engine package, bringing the total from 148 to 176.

### Schema introspection tests (10 tests)

- `TestCompileSchema_ValidXSD` — compiling a real XSD produces a non-nil `Schema`
- `TestCompileSchema_NonexistentFile` — nonexistent path returns an error
- `TestCompileSchema_InvalidSchema` — malformed XSD returns an error
- `TestExplainType_ExistingType` — explaining `BookType` produces correct kind, content type, and children
- `TestExplainType_SimpleType` — explaining `GenreType` produces correct derivation and enumeration
- `TestExplainType_NonexistentType` — nonexistent type returns an error
- `TestBuildSchemaGraph_UserTypes` — graph contains nodes for user-defined types and base-type edges
- `TestGraphToMermaid` — Mermaid output starts with `graph TD` and contains type names
- `TestGraphToDOT` — DOT output starts with `digraph schema` and contains type names
- `TestListComponents_UserTypes` — listing produces at least 4 user-defined components

### Diff and breakage tests (3 tests)

- `TestDiffSchemas_DetectChanges` — diffing v1 and v2 schemas produces breaking and safe changes
- `TestDiffSchemas_SameSchema` — diffing a schema against itself produces no user breaking changes
- `TestAnalyzeBreakage_NoCorpus` — breakage analysis without a corpus classifies changes by severity

### Inference tests (5 tests)

- `TestInferSchema_SingleFile` — inferring from one file produces one source file and a non-empty root element
- `TestInferSchema_NoInputFiles` — empty input returns an error
- `TestInferSchema_NonexistentFile` — nonexistent file returns an error
- `TestInferredSchemaToXSD` — XSD output contains `xs:schema` and `xs:complexType`
- `TestInferSimpleType` — table-driven test for 6 widening cases

### DTD tests (5 tests)

- `TestParseDTD_Elements` — parsing a real DTD produces element declarations
- `TestParseDTD_Entities` — parsing produces entity declarations
- `TestAuditDTD_BillionLaughs` — recursive entities are flagged as `entity-expansion`
- `TestAuditDTD_ExternalEntity` — SYSTEM entities are flagged as `external-entity`
- `TestFlattenDTD` — flattening produces non-empty content
- `TestParseDTD_NonexistentFile` — nonexistent file returns an error

### Test data

Phase 2 adds three test data files:

- `test/testdata/schemas/book-full.xsd` — a rich XSD schema with named types, type derivation (BookType → ExtendedBookType → TextbookType), simple type restrictions (GenreType with enumeration, ISBNType with pattern), and an unused global element (`publisher`)
- `test/testdata/schemas/book-v2.xsd` — a modified version with safe changes (new type, new enum value, abstract→concrete) and breaking changes (required attribute added, element removed)
- `test/testdata/schemas/book.dtd` — a DTD with recursive entity expansion, external entity references, and multi-line ATTLIST declarations

## What comes next

Phase 3 adds Schematron and XSLT workflows. The `xml sch` commands compile Schematron schemas into XSLT, run them against documents, and produce structured SVRL/JSON/HTML output. The `xml xsl` commands run XSLT stylesheets, test them with XSpec, profile template execution, and analyze static dependencies.

The schema workbench architecture supports these additions without restructuring. The `CompileSchema` function is a pattern that will be replicated for `CompileSchematron` and `CompileStylesheet`. The `DiffChange` type is a pattern that will be replicated for stylesheet diff. The `SchemaLintFinding` type is a pattern that will be replicated for stylesheet lint. The domain primitives grow in capability but do not change in shape.
