# Forgetful functors in CS

- URL: https://chatgpt.com/c/6a6e9e34-d4a8-83ea-901e-a016e1cff57b
- Created: 2026-08-02T01:33:24.215Z

---

> Forgetful functors examples, if possible from cs Give me examples of forgetful functors if possible from computer science.

A **forgetful functor** is a functor that "forgets" some structure or properties while keeping the underlying objects and functions. They are extremely common in both mathematics and computer science.

Here are several examples, starting with CS-flavored ones.

### 1. Typed languages → Sets (very common in programming)

Think of the category where:

- Objects = types (e.g. `Int`, `Bool`, `String`, `List<Int>`)
- Morphisms = total functions between types

A forgetful functor sends

- each type to its underlying set of values,
- each function to the same underlying function.

It forgets that these are **programming language types** and remembers only the sets of values.

For example,

- `Bool` → `{true, false}`
- `Int` → the set of integers
- `Bool -> Int` remains the same function as a function of sets.

---

### 2. Monoids → Sets (strings under concatenation)

This is perhaps the most important CS example.

Consider the monoid

- all strings over an alphabet Σ,
- operation = concatenation,
- identity = empty string.

The forgetful functor

\[
U : \mathbf{Mon} \to \mathbf{Set}
\]

maps

- the monoid \((\Sigma^*, \cdot, \varepsilon)\)
- to the underlying set \(\Sigma^*\).

It forgets

- concatenation,
- the identity element,

and remembers only the collection of strings.

This appears everywhere in automata theory and formal languages.

---

### 3. Deterministic automata → Graphs

A deterministic finite automaton consists of

- states,
- transitions,
- start state,
- accepting states.

A forgetful functor can map a DFA to its underlying directed graph.

It forgets

- which state is initial,
- which are accepting,
- determinism,
- alphabet labels (depending on the choice of category),

and keeps only the graph structure.

---

### 4. Graphs → Sets

A graph

\[
(V,E)
\]

has

- vertices,
- edges.

A forgetful functor sends it to

- the set of vertices.

It forgets

- edges,
- adjacency.

This is used when defining free graph constructions.

---

### 5. Categories → Directed graphs

Every category has

- objects,
- morphisms,
- identities,
- composition.

A forgetful functor

\[
\mathbf{Cat} \to \mathbf{Graph}
\]

keeps

- objects,
- arrows,

and forgets

- composition,
- identities,
- associativity.

This example is important because the **free category** construction is left adjoint to this forgetful functor.

---

### 6. Semirings → Monoids

Natural numbers form a semiring

\[
(\mathbb N,+,\times).
\]

A forgetful functor

\[
\mathbf{SemiRing}\to\mathbf{Mon}
\]

may keep only the additive monoid

\[
(\mathbb N,+,0)
\]

and forget multiplication.

This is relevant in weighted automata and dynamic programming.

---

### 7. Ordered sets → Sets

Suppose a type has an ordering:

```text
Int
```

with

```text
≤
```

The forgetful functor removes the ordering and keeps only the underlying collection of values.

Many algorithms exploit order, but sometimes we intentionally ignore it.

---

### 8. Datatypes with algebraic structure → Plain datatypes

Suppose we know that lists form a monoid:

```text
([], ++)
```

The forgetful functor ignores the concatenation operation and remembers only the datatype

```text
List A
```

This is a good way to think about libraries that provide algebraic interfaces (`Monoid`, `Semigroup`, etc.): forgetting the interface leaves just the underlying type.

---

## Functional programming example

Consider the Haskell type class

```haskell
class Monoid m where
    mempty  :: m
    (<>)    :: m -> m -> m
```

An instance

```haskell
[String]
```

comes equipped with

- `mempty = []`
- `(<>) = (++)`

The forgetful functor maps this monoid to the underlying type

```haskell
[String]
```

forgetting

- `mempty`
- `(<>)`

while retaining the carrier type.

---

## Free/Forgetful pairs in CS

Many familiar constructions arise as **free–forgetful adjunctions**:

| Forgetful functor | Left adjoint ("free" construction) |
|-------------------|-------------------------------------|
| Monoids → Sets | Free monoid (strings/lists) |
| Categories → Graphs | Free category (paths) |
| Vector spaces → Sets | Free vector space |
| Boolean algebras → Sets | Free Boolean algebra |

The first two are especially important in computer science:

- **Free monoid** = lists or strings over an alphabet.
- **Free category** = all paths in a graph, which underlies operational semantics, automata, and program control-flow representations.

---

### Intuition

A forgetful functor removes *structure* but not the *underlying data*. In computer science, this often means:

- **typed objects → underlying values**,
- **algebraic interfaces → raw data types**,
- **automata → graphs**,
- **graphs → sets**,
- **categories → graphs**.

These examples illustrate the general pattern: preserve the carrier and morphisms as much as possible, while discarding operations, relations, or laws that give the objects their richer structure.

