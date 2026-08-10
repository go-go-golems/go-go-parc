---
name: pattern-zoo-authoring
description: Researches recurring semantic, mathematical, and architectural patterns across transcripts, theses, design documents, and code, then writes an evidence-backed Pattern Zoo textbook with first-day explanations, rigorous laws, advanced-math sections, worked examples, alias maps, and exact source citations. Use when asked to identify common patterns across multiple design attempts, create a pattern catalog/zoo, distill an overcomplicated research corpus into a semantic kernel, or write a professional ELI5-plus-advanced textbook from project documents.
---

# Pattern Zoo Authoring

## Purpose

Create a Pattern Zoo that does more than collect repeated terminology. The result should identify recurring **problems, semantic objects, laws, and implementation consequences** across multiple attempts at a system, including cases where different documents use different names for the same mathematical structure.

The default audience is a professional developer joining the project. Explain each pattern concretely before introducing notation, then provide a separate advanced section that develops the category theory or abstract mathematics where it adds explanatory power.

Read [the full playbook](references/PLAYBOOK.md) before beginning substantial research. Use [the book template](references/BOOK-TEMPLATE.md) when drafting.

## Required output qualities

A finished Pattern Zoo must:

1. distinguish independent design attempts from duplicated or branched artifacts;
2. identify patterns by shared laws, not shared nouns;
3. map aliases and overloaded terms back to exact documents and headings;
4. explain each pattern for a newly joined professional developer;
5. derive the mathematics from a concrete example;
6. state what the mathematics guarantees operationally;
7. state where the abstraction would be an overclaim;
8. include worked examples, pseudocode, failure modes, and adoption boundaries;
9. cite sources with path-qualified Obsidian wikilinks where applicable;
10. pass structural, link, Markdown, math-rendering, and substantive review.

## Workflow

### 1. Establish the corpus

Inventory the candidate transcripts, theses, reports, source files, and generated artifacts. Record:

- exact path;
- document family or branch;
- date and provenance;
- whether it is an independent attempt, revision, duplicate, transcript, generated thesis, or executable evidence;
- which system boundary it studies.

Do not count copied theses in several branch directories as independent confirmation. Hash or diff suspicious duplicates.

### 2. Read representative primary material

Read the actual documents, not only inventories or filenames. Start with one primary artifact per independent attempt, then follow the sections where it defines:

- identity and sameness;
- state and transitions;
- composition;
- evidence/provenance;
- change and invalidation;
- comparison and decision;
- trust and authorization;
- release/publication semantics.

Use summaries as navigation, never as the sole evidence for a pattern.

### 3. Extract candidate patterns

For each candidate, capture:

```text
Problem:
Semantic objects:
Transformation or relation:
Laws/invariants:
Operational consequence:
Names used:
Source headings:
Counterexamples/limits:
Core or optional elaboration:
```

Accept a pattern when the same law solves the same class of problem in at least two meaningful contexts or attempts. A repeated word is not enough.

### 4. Normalize without flattening

Build an alias matrix. Separate:

- genuine aliases: free plan / typed operation graph / wiring syntax;
- related specializations: semantic ID / release ID;
- overloaded collisions: trusted kernel / Markov kernel;
- superficially similar but distinct structures: dependency graph / provenance graph.

Prefer one pedagogical name while preserving every source-local name in “Names and sightings.”

### 5. Find the restrained kernel

Classify each result as:

- **domain-neutral nucleus** — small values and laws shared without domain semantics;
- **domain kernel** — small and rigorous but owned by RAG, optimization, security, etc.;
- **infrastructure protocol** — retries, leases, queues, storage, activation;
- **product policy** — judges, thresholds, prompts, UI, human authority;
- **optional formalism** — valuable explanatory theory without demonstrated runtime need.

Do not turn the full research vocabulary into one framework.

### 6. Write two reading lanes

Every pattern chapter must contain these sections in this order:

```markdown
# Pattern N — Name

## The first-day version
## The problem it solves
## The mathematical model
## Advanced reader: category theory and abstract mathematics
## Worked example and pseudocode
## Failure modes
## Names and sightings
## Key points
```

The first-day section uses plain professional language and a tiny real example. The mathematical model introduces every symbol from that example. The advanced section may assume comfort with abstraction but must still state the architectural payoff and limits.

### 7. Derive the mathematics

Use this order:

```text
concrete values
  -> named sets/types
  -> functions/relations/operations
  -> laws
  -> operational consequence
  -> limits of the claim
```

Do not begin with a category name and search for an implementation afterward.

Examples:

- duplicate-safe accumulation → associative, commutative, idempotent join → finite join-semilattice;
- typed plan syntax → identity and associative sequence → free category;
- independent retained branches → tensor/product → symmetric monoidal structure;
- outcome alternatives → coproduct/sum type;
- trace accumulation → typed monoids or writer-like decoration;
- stochastic trial → Markov kernel; paired trial → coupling;
- invalidation → support and closure operator;
- durable history → free event monoid folded by a partial reducer;
- eligibility before preference → predicate intersection, product preorder, Pareto front;
- disclosure control → noninterference and graph domination.

### 8. Cite exact sightings

Use path-qualified links:

```markdown
[[Transcripts/.../document-name#Exact heading|local name]]
```

A sighting table should identify:

| Source name | Local term | What is actually shared | Important difference |
|---|---|---|---|

Generated documents are design evidence, not independent peer review. Say so.

### 9. Validate and review

Run the bundled validator from the repository root:

```bash
python3 .pi/skills/pattern-zoo-authoring/scripts/validate_pattern_zoo.py \
  "path/to/Pattern Zoo.md" --expected-patterns 12
```

Then obtain a substantive review focused on:

- mathematical type correctness;
- pseudocode actually satisfying the stated invariant;
- consistency between beginner and advanced sections;
- release/lease and retry races;
- experiment coordinate completeness;
- soundness versus completeness claims;
- authorization bypass paths;
- claims that exceed the cited evidence.

Structural validation cannot catch those errors.

### 10. Publish deliberately

Update the relevant research index and cluster note. If creating a PDF or reMarkable bundle, render before uploading and use Pandoc-compatible math:

- prefer `$...$` and `$$...$$`;
- avoid `\(...\)` and `\[...\]` in this environment;
- avoid commands requiring unstated packages such as `\llbracket`, `\xRightarrow`, or custom `\bind`;
- use `\mathcal I`, `\xrightarrow`, and `\operatorname{bind}` as portable alternatives.

## Delegation guidance

For a large corpus, delegate by independent attempt or pattern family, not arbitrary file count. Give each worker a distinct output file. Ask for:

- exact headings and formulations;
- alias mappings;
- minimal kernel candidates;
- overcomplex or optional machinery;
- contradictions and revisions.

The controlling agent must cross-read the outputs, deduplicate claims, and own final synthesis. Subagent agreement is not independent evidence when all agents read duplicated source text.

## Stop conditions

Do not call the book complete until:

- every claimed pattern has evidence from the corpus;
- all patterns have both reading lanes;
- every equation has defined symbols and an operational interpretation;
- all source links and heading anchors resolve;
- examples and pseudocode survive substantive review;
- the final index points to the book;
- temporary research outputs are removed or deliberately archived.
