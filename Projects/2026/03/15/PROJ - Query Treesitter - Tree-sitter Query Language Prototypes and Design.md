---
title: Query Treesitter
aliases:
  - Query Treesitter
  - Tree-sitter Query Language
  - Project Query Treesitter
tags:
  - project
  - tree-sitter
  - ast
  - python
  - javascript
status: active
type: project
created: 2026-03-14
repo: /home/manuel/code/wesen/2026-03-14--query-treesitter
---

# Query Treesitter

This project is a small research repo about how to build a better query language for Tree-sitter-style syntax trees. It is not a production parser framework yet. It is closer to a design lab: a place to explore different ways of querying ASTs, compare their tradeoffs, and work out what a real long-term query system should look like.

The core idea is that raw Tree-sitter queries are very good at local structural matching, but they become awkward once the query needs to express richer relationships:

- repeated subtree equality,
- descendant and ancestor joins,
- lexical-scope reasoning,
- declaration/use resolution,
- reusable higher-level query definitions,
- or project-specific custom analysis logic.

This repo explores that space through three related prototypes.

## What the project is about

The project is trying to answer a fairly specific question:

**What is the best query language to sit on top of Tree-sitter if the goal is not just tree grep, but a more expressive AST analysis system?**

The interesting part is that the repo does not answer that with one single approach. Instead, it breaks the problem apart and tries three angles:

1. exact logic-style unification over tree terms,
2. a readable relational query language over normalized Tree-sitter nodes,
3. a hybrid query engine that adds lightweight semantic reasoning such as scope and declaration resolution.

The result is that the repo feels less like "one tool" and more like a staged design conversation:

- what should the core matching primitive be,
- what should the user-facing syntax look like,
- how far should semantic reasoning go before the system turns into a compiler,
- and where should JavaScript or host-language extension hooks enter the picture.

That is what makes the project interesting.

## The simplest mental model

The simplest mental model is:

- a Tree-sitter query language experiments repo,
- with one branch focused on symbolic unification,
- one branch focused on readable declarative syntax,
- and one branch focused on semantic relations over syntax trees.

Or, more concretely:

- `norvig/` asks: what if AST matching is built on classic first-order unification?
- `tuql/` asks: what if Tree-sitter queries had a more readable relational surface language?
- `hybrid-tuql/` asks: what if that language also knew a little about declarations, uses, scopes, and ordering?

## What the repo contains

The repo is intentionally compact. The important directories are:

### 1. `norvig/`

This is the logic core.

It implements a Python version of the Norvig/PAIP unifier and adapts Tree-sitter-like nodes into first-order terms. In this model, AST nodes become symbolic terms, fields become structured term wrappers, and repeated variables enforce equality by unification.

Why this matters:

- it gives the project a principled formal core,
- it makes subtree equality natural,
- and it shows how AST matching can be treated as a logic problem instead of only as pattern matching.

This prototype is exact and relatively low-level. It is closer to a semantic kernel than to a finished end-user query language.

### 2. `tuql/`

This is the main language experiment.

TUQL stands for **Tree Unification Query Language**. It is a small relational DSL for Tree-sitter-style parse trees. It adds a more readable query surface with:

- variables like `$x`,
- node patterns like `identifier[text="foo"]`,
- field matching,
- ordered child matching,
- rest captures such as `..$rest`,
- and relations such as `match`, `desc`, `child`, `inside`, `has`, `same_tree`, and `same_node`.

The key semantic move in TUQL is that repeated variables mean **structural subtree equality** rather than object identity. That means a pattern like:

```tuql
binary_expression{left: $x, right: $x}
```

matches `a + a` because the left and right subtrees are structurally the same, even if they are different node objects.

This part of the repo is really about language ergonomics. It is trying to find a query surface that feels more natural for multi-step AST reasoning than raw Tree-sitter S-expressions.

### 3. `hybrid-tuql/`

This is the most ambitious prototype in the repo.

Hybrid TUQL keeps the TUQL surface syntax but backs it with Norvig-style unification and adds a semantic layer for lightweight lexical reasoning. It introduces relations such as:

- `before` / `after`,
- `inside_loop`,
- `scope`,
- `same_scope`,
- `declares`,
- `uses`,
- `resolves_to`.

This is the point where the project stops being just a prettier tree matcher and starts looking like a real code analysis system.

It is still intentionally lighter than a full compiler front-end. The repo is not trying to do full control-flow analysis, import resolution, or language-lawyer symbol tables. The goal is the useful middle ground:

- much more expressive than raw Tree-sitter queries,
- much lighter than building full semantic infrastructure.

## What the project is for

The project exists to work out what a practical AST query system should look like if it needs to support both:

- declarative structural matching,
- and more semantic or custom analysis patterns.

That means it is really aimed at future tooling use cases such as:

- code search,
- lint-like analysis,
- refactoring assistants,
- code intelligence,
- semantic indexing,
- or AI systems that want better AST-level query primitives.

A plain Tree-sitter query can say "find this local shape." This project is interested in the next level up:

- find a use that resolves to a declaration,
- find two structurally equal subtrees,
- find a pattern inside a specific ancestor context,
- or define a reusable higher-level query that can be called from other queries.

## Why the project matters

The repo is valuable because it isolates several design questions that often get blurred together in larger tools.

### 1. Structural matching vs semantic matching

Tree-sitter is excellent at structure. But once queries care about scope, declaration resolution, or semantic relationships between separate captures, a second layer is needed. This repo makes that boundary visible.

### 2. Surface syntax vs execution model

The nicest user-facing query language is not necessarily the best execution substrate. One of the important conclusions from this repo is that a readable language like TUQL can sit above a lower-level engine such as native Tree-sitter queries plus a relational evaluator.

### 3. Declarative queries vs programmable escape hatches

Not every useful AST pattern fits comfortably in a declarative DSL. This project keeps pointing toward a future design where the query language stays declarative by default, but can call out to custom host-language logic for harder cases.

That is where the JavaScript angle becomes especially interesting.

## The likely long-term direction

The best long-term direction for this project is probably not "replace Tree-sitter queries entirely." It is more likely:

1. keep Tree-sitter's native query engine as the fast structural prefilter,
2. keep a TUQL-like surface language for readability,
3. keep unification for repeated-variable equality and relational joins,
4. support user-defined named queries,
5. and let a JavaScript runtime register custom predicates or binders for project-specific logic.

That is the most compelling design because it keeps the best piece from each approach:

- Tree-sitter for structural speed,
- TUQL for authoring ergonomics,
- Norvig unification for principled equality semantics,
- Hybrid TUQL for semantic relations,
- JavaScript for custom extensions and ad-hoc AST queries.

## Why user-defined queries are important

One of the strongest ideas to come out of this repo is that the final system should let people define their own reusable queries.

That matters because a real query language becomes much more useful once teams can build their own vocabulary on top of the base primitives. Instead of writing one-off giant patterns every time, users should be able to define named queries like:

- duplicate operand,
- self-named parameter,
- loop-carried use,
- suspicious reassignment,
- or framework-specific idioms.

In other words, the language should not only match syntax. It should let users build abstractions over syntax.

## Why JavaScript matters here

The repo itself is currently Python-based, but the project direction clearly points toward a system that could be embedded in a JavaScript or TypeScript environment.

That matters for two reasons:

### 1. Host integration

A JS runtime makes the query system much easier to embed into editors, analysis tools, browser tooling, and AI systems that already live in JS/TS.

### 2. Custom query logic

Some patterns are too awkward to encode cleanly in a declarative query language. A good future design would let the user write a normal JS function that can:

- inspect bound AST nodes,
- compute extra facts,
- filter candidate matches,
- or extract a derived value to unify back into the query.

That gives the system an escape hatch without forcing everything into raw imperative traversal from the start.

## What the repo is not

It helps to be explicit about what this project is **not**.

It is not:

- a production-ready Tree-sitter framework,
- a full compiler front-end,
- a full dataflow engine,
- or a finished end-user product.

It is a focused prototyping repo about query language design.

That is why the code is valuable even though it is small. The point is not breadth. The point is to make the language and execution tradeoffs visible.

## Current shape of the project, in plain terms

If I describe the project without naming the prototype directories, the repo is about:

- turning syntax trees into something queryable,
- exploring the right query surface,
- preserving structural equality semantics,
- layering in navigation and lexical reasoning,
- and figuring out how to combine declarative queries with programmable extensions.

That is the real topic of the project.

## What is reusable from it

Even if the repo later gets rewritten or folded into a larger system, several ideas here are reusable:

- normalized `NodeView`-style tree adapters,
- field-aware tree-to-term encoding,
- repeated-variable subtree equality,
- a relational query layer over ASTs,
- lightweight semantic indexing for declarations and uses,
- and a future hybrid design where native Tree-sitter queries handle structure while a higher-level runtime handles joins and custom predicates.

## Current research output

There is now also a detailed design and implementation guide in the repo's ticket workspace under:

`/home/manuel/code/wesen/2026-03-14--query-treesitter/ttmp/2026/03/15/TSQ-001--tree-sitter-query-language-research-and-design`

That ticket writes down the likely next step for the project in explicit terms:

- a layered TUQL 2 design,
- user-defined named queries,
- JavaScript predicates and binders,
- and a planner that compiles structural pieces to Tree-sitter queries and evaluates the rest in a relational engine.

So the repo is now both:

- a prototype playground,
- and a design reference for what the real system could become.

## KB reviews

- [[KB-BATCH9-tree-sitter-structured-text]] (2026-05-11) — Batch C analysis; contributed to [[On-Ramp/tree-sitter-for-go-tools]] and the structural-prefilter-plus-semantic-layer tribal candidate.

## Related KB entries

- [[On-Ramp/tree-sitter-for-go-tools]] — Tree-sitter as the structural substrate for Go tooling, query layers, and span-aware analysis.

**Tribal candidates** (not yet written / needs review):
- Tree-sitter as structural prefilter plus semantic layer (3/3, review before creating) — native queries for fast structure, higher-level relations/unification/predicates above them.
- Repeated-variable subtree equality (1/3) — TUQL repeated variables mean structural equality, not object identity.
- User-defined named AST queries (1/3) — reusable query vocabulary over raw one-off patterns.
- Host-language custom predicates and binders (1/3) — declarative query surface with JS escape hatches.
