---
title: "Category Theory and Logic — Foundations for Type Systems, Semantics, and Verification"
aliases:
  - category theory and logic
  - category-theory-and-logic
  - topos theory
  - monic and epic arrows
  - subobject classifier
tags:
  - knowledge-base
  - fundamental
  - category-theory
  - logic
  - type-theory
  - semantics
  - verification
status: active
type: knowledge-base
created: 2026-07-21
---

# Category Theory and Logic — Foundations for Type Systems, Semantics, and Verification

Category theory provides an abstract language for structure-preserving transformations: functors, natural transformations, adjunctions, limits, and colimits. In computer science, these abstractions surface in type systems, denotational semantics, program logics, database schemas, and verification frameworks. The subobject classifier from topos theory is the categorical formalization of a truth-value object, and it underpins the connection between categories and intuitionistic logic.

> [!summary]
> - **Monic and epic arrows** characterize information-preserving and information-complete maps, but they are not simply "injective" and "surjective" in arbitrary categories — the distinction matters for type systems and data modeling.
> - **Isomorphisms** require both monic and epic plus an inverse; monic + epic alone does not imply isomorphism in general categories.
> - **Topos theory's subobject classifier** connects categorical structure to internal logic, giving semantics for dependent types, subtyping, and refinement logics.

## Why this matters to our work

Several go-go-golems projects touch category-theoretic concepts without naming them:

- **Type systems in goja embedding** — native module registration and fluent DSLs are functorial in the sense that they preserve structure between Go types and JavaScript objects.
- **Denotational semantics for interpreters** — the tiny-idp interpreter work (serialized continuations, invocation capabilities) models program states categorically.
- **Verification and proof** — the interpreter instrumentation work (eBPF-style probes for invariant assertion) relates to categorical logic and refinement types.
- **Widget IR and projections** — the widget DSL's separation of intent, IR, and target rendering mirrors the categorical pattern of functors between structured categories.

## Core concepts

### Monic and epic arrows

A morphism $f: A \to B$ is **monic** (a monomorphism) if it is left-cancellable: $f \circ g = f \circ h \implies g = h$. It is **epic** (an epimorphism) if it is right-cancellable: $g \circ f = h \circ f \implies g = h$.

In **Set**, monic coincides with injective and epic with surjective. In other categories this is not guaranteed. The practical consequence for computer science: a monic function preserves information (no two distinct inputs collapse), and an epic function covers the codomain (every output is reachable), but the converse implications depend on the category.

### Isomorphism is not monic + epic

An isomorphism requires an inverse: $f \circ g = \text{id}$ and $g \circ f = \text{id}$. A morphism that is both monic and epic is called a **bimorphism**. In Set, every bimorphism is an isomorphism. In general categories (e.g., topological spaces, certain algebraic categories), bimorphisms exist that are not isomorphisms. This distinction matters when modeling type equivalence: two types may be "morally the same" (monic and epic between them) without being definitionally equal.

### Subobject classifier

In a topos, the subobject classifier $\Omega$ is an object that represents the collection of truth values. There is a monic arrow $\text{true}: 1 \to \Omega$ from the terminal object, and for every subobject (monic arrow $m: S \to X$), there is a unique characteristic arrow $\chi_m: X \to \Omega$ making a pullback square.

In **Set**, $\Omega = \{0, 1\}$ and the subobject classifier is the characteristic function. In richer topoi (sheaves, effective topos), $\Omega$ carries more structure, enabling internal logics that are not classical — intuitionistic, modal, or linear.

## Connection to computer science

| Concept | CS manifestation |
|---------|-----------------|
| Monic arrow | Injective function, type embedding, lossless encoding |
| Epic arrow | Surjective function, total serializer, covering map |
| Isomorphism | Type equivalence, bijective serialization |
| Subobject classifier | Boolean type, refinement predicate, proof object |
| Pullback | Dependent product, database join, fibered type |
| Functor | Structure-preserving map between type categories |
| Natural transformation | Polymorphic function, parametricity |

## Related transcripts

These ChatGPT conversations explored category-theoretic concepts with a focus on building intuition through exercises and concrete examples:

- [[CHATGPT TRANSCRIPT - Monic Epic Arrows Intuition — Category Theory]] — progressive exercise set on monic/epic arrows with computer science examples
- [[CHATGPT TRANSCRIPT - Topos Theory Subobject Classifier]] — importance of the subobject classifier in computer science
- [[CHATGPT TRANSCRIPT - Mikhail Gromov LLMs]] — Mikhail Gromov's perspectives on large language models

## Related notes

- [[Research/KB/Fundamentals/access-control-models]] — authorization as a categorical concept (permissions as subobjects)
- [[Research/KB/Projects/go-go-goja]] — goja embedding and type-preserving module registration
- [[Research/KB/Projects/tiny-idp]] — interpreter semantics and serialized continuations

## Open questions

- How far should the go-go-golems type system explicitly use categorical vocabulary versus staying in concrete Go types?
- Can the widget IR be formalized as a functor from an intent category to a target category, and does that formalization pay for itself?
- Are there verification properties in the tiny-idp interpreter work that are naturally expressed as topos-theoretic subobject conditions?
