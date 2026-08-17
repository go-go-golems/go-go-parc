---
title: Cobra — Index of Design Patterns
aliases:
  - Cobra design pattern index
  - Cobra architecture glossary
status: active
type: architecture-garden-index
created: 2026-08-16
analyzed: 2026-08-16
analysis_schema: architecture-garden-v1
repository: https://github.com/spf13/cobra
repository_commit: adbc8813901bba65827259daa8e22ff94ec1f30e
derived_from: Research/Software Architecture Garden/cobra/README.md
tags:
  - architecture-garden
  - cobra
  - design-pattern-index
  - cli
  - command-tree
related_notes:
  - "[[Research/Software Architecture Garden/cobra/README]]"
  - "[[Research/Software Architecture Garden/cobra/Index of Design Patterns - Rationale]]"
  - "[[Research/Software Architecture Garden/README]]"
---

# Cobra — Index of Design Patterns

This is the back-of-the-book index for the [[Research/Software Architecture Garden/cobra/README|Cobra architecture study]]. It is filed by how a reader is likely to remember the knowledge, not by the exact spelling used in the source. Each canonical entry is a heading, carries a one-sentence glossary definition, and points to the focused design note or project study that substantively treats it.

## How to read this index

- **See** redirects alternate vocabulary to the canonical entry.
- **see also** connects related but non-equivalent concepts.
- Maturity labels come from the [[Research/Software Architecture Garden/README#Pattern maturity vocabulary|Garden vocabulary]].
- The [[#Runtime handles and notation|notation table]] is for concrete Cobra handles a reader is likely to encounter in code.
- Failure modes and non-guarantees are indexed deliberately; this is not a list of only successful patterns.

---

## A

### Annotation-driven constraints

*See* [[#Constraint metadata drives validation and completion]].

### Arguments as injectable input

`SetArgs` makes argv an execution dependency rather than a mandatory read from `os.Args`, enabling the same executor to run in tests and embedded contexts. [Established] [[Research/Software Architecture Garden/cobra/07 - Injectable Process Boundaries for Deterministic Tests|design 07]]. *see also* [[#Injectable process boundary]], [[#Context propagation]].

## C

### Command graph as semantic authority

One parent/child `Command` graph is the source of truth for dispatch, availability, help, completion, validation scope, and generated documentation. [Established] [[Research/Software Architecture Garden/cobra/01 - Command Graph as Semantic Authority|design 01]], [[Research/Software Architecture Garden/cobra/README#Candidate common vocabulary|project vocabulary]]. *see also* [[#One model, many interpreters]], [[#Model-derived documentation]], [[#Hidden completion protocol]].

### Command tree

*See* [[#Command graph as semantic authority]].

### Completion directives

A compact bit-map returned by the internal completion protocol tells shell adapters how to treat candidates — no-space, no-file-completion, file filters, directory filters, or keep-order — without teaching the shell Cobra internals. [[Research/Software Architecture Garden/cobra/06 - Hidden Protocol Commands for Interactive Tooling|design 06]]. *see also* [[#Hidden completion protocol]].

### Constraint metadata drives validation and completion

Cross-flag laws are stored as annotations and interpreted both by runtime validation and completion guidance, avoiding two independent rule sets. [Established] [[Research/Software Architecture Garden/cobra/05 - Constraint Metadata Drives Validation and Completion|design 05]]. *see also* [[#Flag groups]], [[#One model, many interpreters]].

### Context propagation

`ExecuteContext` installs caller-owned cancellation/state on the command graph and propagates it to the selected child when the child has no local context. [Established] [[Research/Software Architecture Garden/cobra/07 - Injectable Process Boundaries for Deterministic Tests|design 07]]. *see also* [[#Injectable process boundary]].

## D

### Declarative flag relationships

*See* [[#Constraint metadata drives validation and completion]].

### Documentation from executable schema

*See* [[#Model-derived documentation]].

## E

### Executable as query server

*See* [[#Hidden completion protocol]].

### Execution pipeline

Every invocation passes through routing, parsing, argument validation, preparation hooks, required/group validation, and only then `Run`/`RunE`; ordering is a first-class contract. [Established] [[Research/Software Architecture Garden/cobra/03 - Staged Command Execution Pipeline|design 03]]. *see also* [[#Post-hooks are not cleanup]], [[#Persistent hook traversal]].

## F

### Flag groups

Required-together, one-required, and mutually-exclusive relations are declarative constraints attached to flags rather than checks buried only in a handler. [Established] [[Research/Software Architecture Garden/cobra/05 - Constraint Metadata Drives Validation and Completion|design 05]]. *see also* [[#Constraint metadata drives validation and completion]].

### Flag inheritance

Persistent ancestor flags become part of a descendant's effective flag set while locally shadowed names are excluded from the inherited view. [Established] [[Research/Software Architecture Garden/cobra/02 - Hierarchical Policy Inheritance with Local Shadowing|design 02]]. *see also* [[#Hierarchical policy inheritance]], [[#Local shadowing]].

### Framework defaults as fallbacks

*See* [[#Late defaults with user override]].

## H

### Help and version synthesis

Cobra adds default help/version flags and help commands only when needed and when the application has not already claimed the slot. [Established] [[Research/Software Architecture Garden/cobra/04 - Late Defaults with User Override|design 04]]. *see also* [[#Late defaults with user override]].

### Hidden completion protocol

The executable exposes hidden `__complete` queries that resolve partial command lines through the live command graph and emit candidate lines plus a final directive. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/cobra/06 - Hidden Protocol Commands for Interactive Tooling|design 06]]. *see also* [[#Completion directives]], [[#Command graph as semantic authority]].

### Hierarchical policy inheritance

A descendant resolves local policy first and otherwise walks ancestors, allowing application-wide defaults without erasing subtree/leaf ownership. [Established] [[Research/Software Architecture Garden/cobra/02 - Hierarchical Policy Inheritance with Local Shadowing|design 02]]. *see also* [[#Flag inheritance]], [[#Local shadowing]].

## I

### Injectable process boundary

Arguments, context, stdin, stdout, and stderr can be caller-controlled so tests and embedded callers execute the production command pipeline in process. [Established] [[Research/Software Architecture Garden/cobra/07 - Injectable Process Boundaries for Deterministic Tests|design 07]]. *see also* [[#Arguments as injectable input]], [[#Context propagation]].

### Interactive tooling query

*See* [[#Hidden completion protocol]].

## L

### Late defaults with user override

Framework conveniences are synthesized at the latest practical phase and presence-checked so explicit application definitions retain authority. [Established] [[Research/Software Architecture Garden/cobra/04 - Late Defaults with User Override|design 04]]. *see also* [[#Help and version synthesis]], [[#Mutable model phase]].

### Local shadowing

A descendant can locally redefine an inherited policy slot; for flags, the shadowed ancestor value is no longer reported as inherited. [Established] [[Research/Software Architecture Garden/cobra/02 - Hierarchical Policy Inheritance with Local Shadowing|design 02]]. *see also* [[#Hierarchical policy inheritance]].

## M

### Model-derived documentation

Markdown/man/reST reference material is rendered by walking the assembled runtime `Command` model, including actual command paths and local/inherited flags. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/cobra/08 - Generate Documentation from the Runtime Model|design 08]]. *see also* [[#Command graph as semantic authority]], [[#Generated artifact collision]].

### Mutable model phase

Cobra's command graph can be modified and can receive synthesized commands/flags during execution or completion; tools need to know which assembled phase they are observing. [Architecture debt / tradeoff] [[Research/Software Architecture Garden/cobra/README#Architecture debt and patterns not to repeat|project debt]], [[Research/Software Architecture Garden/cobra/04 - Late Defaults with User Override|design 04]].

## O

### One model, many interpreters

*See* [[#Command graph as semantic authority]].

## P

### Persistent flags

Flags declared persistent on an ancestor participate in descendant parsing and tooling unless a descendant shadows the name locally. [Established] [[Research/Software Architecture Garden/cobra/02 - Hierarchical Policy Inheritance with Local Shadowing|design 02]]. *see also* [[#Flag inheritance]].

### Persistent hook traversal

Persistent pre/post hooks can either stop at the first applicable hook or, under the global traversal switch, run pre-hooks root-to-leaf and post-hooks leaf-to-root. [Established] [[Research/Software Architecture Garden/cobra/03 - Staged Command Execution Pipeline|design 03]]. *see also* [[#Execution pipeline]], [[#Process-global extension state]].

### Post-hooks are not cleanup

`PostRun*` and `PersistentPostRun*` are later pipeline stages and are skipped when earlier validation or `RunE` returns; they are not a `finally`/`defer` guarantee. [Open correctness obligation / non-guarantee] [[Research/Software Architecture Garden/cobra/03 - Staged Command Execution Pipeline#Critical non-guarantee: post-hooks are not cleanup|design 03]].

### Process-global extension state

Behavior switches, template functions, initializer/finalizer lists, and the flag-completion registry live at package scope, reducing per-command-tree isolation. [Architecture debt / compatibility tradeoff] [[Research/Software Architecture Garden/cobra/README#Process-global extension state|project debt]]. *see also* [[#Hierarchical policy inheritance]].

## R

### Reference documentation generation

*See* [[#Model-derived documentation]].

## S

### Semantic command graph

*See* [[#Command graph as semantic authority]].

### Staged execution

*See* [[#Execution pipeline]].

### Stream inheritance

Input/output/error streams set on an ancestor can be consumed by descendants that do not locally override them. [Established] [[Research/Software Architecture Garden/cobra/02 - Hierarchical Policy Inheritance with Local Shadowing|design 02]], [[Research/Software Architecture Garden/cobra/07 - Injectable Process Boundaries for Deterministic Tests|design 07]].

## T

### Testable CLI without subprocesses

*See* [[#Injectable process boundary]].

### Tooling protocol

*See* [[#Hidden completion protocol]].

## Runtime handles and notation

| Handle | Kind | Meaning | Where |
|---|---|---|---|
| `Command` | semantic node | Command identity, topology, metadata, lifecycle, flags and execution-scoped state. | [[#Command graph as semantic authority]] |
| `AddCommand` | graph mutation | Attaches child nodes and establishes parent topology. | [[#Command graph as semantic authority]] |
| `Find` / `Traverse` | routing interpreters | Resolve argv into a command; `Traverse` parses parent-local flags while descending. | [[#Execution pipeline]] |
| `PersistentFlags()` | inherited declaration | Flags declared to flow to descendants. | [[#Persistent flags]] |
| `LocalFlags()` | provenance view | Flags treated as local to the current command. | [[#Local shadowing]] |
| `InheritedFlags()` | provenance view | Parent persistent flags visible here and not shadowed locally. | [[#Flag inheritance]] |
| `RunE` | effect stage | Error-returning main command handler after admission stages. | [[#Execution pipeline]] |
| `PersistentPreRunE` / `PersistentPostRunE` | lifecycle hooks | Hierarchy-aware preparation/post stages; post is not guaranteed cleanup. | [[#Persistent hook traversal]], [[#Post-hooks are not cleanup]] |
| `__complete` | hidden protocol command | Machine entry point for shell completion queries with descriptions. | [[#Hidden completion protocol]] |
| `__completeNoDesc` | hidden protocol alias | Completion query without descriptions. | [[#Hidden completion protocol]] |
| `ShellCompDirective` | protocol bit map | Tells shell adapter how to treat completion candidates. | [[#Completion directives]] |
| flag annotations | constraint metadata | Encodes required, grouped, filename and other machine-readable flag semantics. | [[#Constraint metadata drives validation and completion]] |
| `SetArgs`, `SetIn`, `SetOut`, `SetErr` | process adapters | Replace ambient process boundaries for tests/embedding. | [[#Injectable process boundary]] |
| `ExecuteContext` | execution adapter | Executes with caller-owned context. | [[#Context propagation]] |
| `GenMarkdownTree*` | model interpreter | Produces reference docs by recursively walking commands. | [[#Model-derived documentation]] |

## Failure modes and non-guarantees quick index

- [[#Post-hooks are not cleanup]] — later lifecycle stages are skipped on earlier errors.
- [[#Process-global extension state]] — tree instances are not fully isolated from package configuration.
- [[#Mutable model phase]] — synthesized defaults and completion can mutate the graph.
- [[#Generated artifact collision]] — flattened command paths can collide for some hyphenated/nested names.

### Generated artifact collision

Cobra documents a Markdown-tree filename ambiguity for certain hyphenated command names and nested paths, illustrating that a generated flat namespace must have an injective path encoding. [Candidate ecosystem caution] [[Research/Software Architecture Garden/cobra/08 - Generate Documentation from the Runtime Model|design 08]].
