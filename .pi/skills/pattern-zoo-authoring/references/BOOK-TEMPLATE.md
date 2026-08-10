---
title: <Domain> Pattern Zoo
aliases:
  - <Alternative title>
status: draft
created: YYYY-MM-DD
tags:
  - research
  - design-patterns
  - textbook
---

# <Domain> Pattern Zoo

## Why this book exists

State which repeated attempts or systems this book compares, what recurring problem they address, and why their vocabulary obscures a smaller common structure.

State the audience explicitly:

> This book is written for a professional developer joining the project. It assumes software-engineering experience but no prior category theory, abstract algebra, probability theory, or formal methods.

> [!important] What “the math explains the system” means
> State how laws determine which implementation variations preserve promised behavior.

## How to read a pattern

1. Start with the first-day version.
2. Read the problem and concrete example.
3. Treat each equation as a testable contract.
4. Use the advanced section to generalize the pattern.
5. Follow source sightings for provenance and alternative terminology.

## System overview

Describe one end-to-end path through the domain. Add a Mermaid diagram if it clarifies value flow, authority, or state transitions.

## Pattern index

1. [[#Pattern 1 — <Name>]]
2. [[#Pattern 2 — <Name>]]

## Recurring vocabulary

| Term | Meaning in this book | Concrete software question |
|---|---|---|
| Projection | A function retaining selected fields. | Which fields define this claim of sameness? |
| ... | ... | ... |

## Source map

- [[path/to/primary-document|Primary document]] — evidence role and caveat.

---

# Pattern 1 — <Pedagogical name>

## The first-day version

Give the smallest professional explanation in two or three paragraphs. Include a tiny concrete example using realistic values or types.

Avoid notation here unless one symbol genuinely makes the example clearer.

## The problem it solves

Explain the ambiguity, race, unsound reuse, invalid comparison, disclosure risk, or duplicated authority that exists without the pattern.

Answer directly:

- What breaks without it?
- Why is the obvious implementation insufficient?
- At which boundary does the problem become visible?

## The mathematical model

Introduce symbols from the tiny example:

```text
Let X be ...
Let P: X -> Y be ...
```

State each law separately and follow it immediately with its operational consequence.

**Law name.**

$$
<equation>
$$

Operationally, this means ...

State assumptions and distinguish exact equality from hash, approximate, stochastic, or observation-relative claims.

## Advanced reader: category theory and abstract mathematics

Identify the larger formal structure only after the concrete model is established.

Cover:

1. objects and morphisms/relations;
2. algebraic or categorical laws;
3. any universal property, quotient, order, closure, coupling, or factorization;
4. the theorem-like implementation consequence;
5. required assumptions;
6. where the analogy or abstraction stops.

Include exact source links:

- [[path/to/document#Exact heading|local term]].

## Worked example and pseudocode

Use a realistic scenario. Walk through values before showing pseudocode.

```text
function example(...):
    ...
```

Check the pseudocode against the mathematical law. Include retry, missing-data, race, or adversarial paths when relevant.

## Failure modes

- **Failure name:** symptom, cause, and correction.
- **Failure name:** symptom, cause, and correction.

Include at least one failure caused by confusing this pattern with a neighboring pattern.

## Names and sightings

| Source | Local name | Shared structure | Important difference |
|---|---|---|---|
| [[path/to/doc#Heading|Document]] | `local term` | ... | ... |

Call out overloaded terms explicitly.

## Key points

- Each bullet is a complete sentence.
- Summarize the law and operational consequence.
- Do not introduce new material here.

---

<!-- Repeat the pattern chapter for every accepted pattern. -->

# Combining the Patterns

Follow one realistic change or request through every relevant pattern. Link back to chapter headings.

## The restrained kernel

### Domain-neutral nucleus

List only values and laws genuinely shared across at least two consumers.

### Domain-owned semantics

List small rigorous kernels that remain domain-specific.

### Infrastructure-owned protocols

List operational mechanisms that carry semantic identities without defining them.

### Product-owned policy

List thresholds, prompts, judges, presentation, and human authority.

## What not to unify

List graph, identity, evidence, kernel, port, and parallelism collisions relevant to this domain.

## Practical adoption sequence

Order changes so that low-risk semantic clarification comes before broad frameworks.

## Suggested reading paths

Provide role-oriented paths for new developers, domain engineers, optimization/evaluation engineers, infrastructure engineers, and advanced readers.

> [!warning] Evidence status
> State which claims are generated designs, implementations, tests, proofs, or independently reproduced evidence.
