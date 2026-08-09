# Natural Transformations in CS

- URL: https://chatgpt.com/c/6a6c8800-5380-83ea-8bc8-b3d6bc392e09
- Created: 2026-07-31T11:34:08.502Z

---

> Motivate the topic of natural transformations in category theory with examples from CS and exercises that build up to it based on knowing functors and products/coproducts (if that helps, I’m a noob)

I’ll build this as a short learning path: intuition first, then CS examples, then exercises that gradually force the definition to emerge.

<details><summary>💭 Thinking</summary>

**Clarifying the concept**

I’m framing a natural transformation as a uniform adapter between container shapes, using the equation \(Gf \circ \eta_A=\eta_B\circ Ff\). I’ll explain why uniformity matters, then give approachable examples such as `Maybe` to lists.

**Clarified the concept**

**Building examples and exercises**

I’m refining the explanation with a commuting-square diagram: “transform, then map” must equal “map, then transform.” I’ll contrast natural examples with `nub` and `sort`, then add beginner exercises that gradually build intuition.

**Built examples and exercises**

</details>

# Natural transformations: the “generic adapter” idea

A useful programming interpretation is:

- A **functor** is a generic context or data shape equipped with `map`.
- A **natural transformation** is a uniform adapter from one functorial context to another.
- **Naturality** says it does not matter whether you transform the values before or after adapting the context.

Examples of functorial contexts include:

- `List<A>`: zero or more `A`s
- `Option<A>`: zero or one `A`
- `Result<E, A>`: either an error or an `A`
- `Reader<R, A> = R -> A`: a computation requiring an environment
- `Const<N, A> = N`: metadata that contains no `A`

The key mental model is:

> `map` changes the payload while preserving the context.  
> A natural transformation changes the context while treating the payload uniformly.

---

## 1. From polymorphic functions to natural transformations

Suppose `F` and `G` are functors. Consider a generic function

```text
eta<A>: F<A> -> G<A>
```

There is one such function for every type `A`.

For `eta` to be a natural transformation, it must satisfy:

```text
mapG(f, eta(x)) = eta(mapF(f, x))
```

for every function `f: A -> B` and every `x: F<A>`.

Categorically, for every `f: A -> B`, this diagram must commute:

```text
          eta_A
    F<A> --------> G<A>
     |              |
 F(f)│              │G(f)
     v              v
    F<B> --------> G<B>
          eta_B
```

There are two routes:

1. Change the values with `F(f)`, then change context with `eta_B`.
2. Change context with `eta_A`, then change the values with `G(f)`.

Naturality says the results are identical.

---

## 2. Why require this law?

Without naturality, a “transformation” could behave arbitrarily at every type:

```text
eta<Int>     behaves one way
eta<String>  behaves completely differently
eta<User>    does something unrelated
```

That would not constitute one coherent, reusable operation.

Naturality forces the implementation to be independent of the particular payload type. It may:

- drop values,
- duplicate values,
- reorder values,
- add or remove structural information,

but it cannot treat an `Int` specially merely because it is an `Int`.

This connects naturality to **parametric polymorphism** and “free theorems.” In a pure language without type inspection or similar escape hatches, a function of type

```text
forall A. F<A> -> G<A>
```

often has little choice but to be natural.

---

# 3. First example: `Option` to `List`

Define:

```text
optionToList<A>: Option<A> -> List<A>

optionToList(None)    = []
optionToList(Some(x)) = [x]
```

This changes the container but leaves the payload alone.

Let `f: A -> B`. We check:

```text
mapList(f, optionToList(value))
=
optionToList(mapOption(f, value))
```

For `None`:

```text
mapList(f, [])
= []
= optionToList(None)
```

For `Some(x)`:

```text
mapList(f, [x])
= [f(x)]
= optionToList(Some(f(x)))
```

So `optionToList` is natural.

The implementation only observes whether the option is empty. It never investigates the value inside.

---

## 4. `safeHead`: `List` to `Option`

Define:

```text
safeHead<A>: List<A> -> Option<A>

safeHead([])       = None
safeHead(x :: xs)  = Some(x)
```

Its naturality law is:

```text
mapOption(f, safeHead(xs))
=
safeHead(mapList(f, xs))
```

For a nonempty list, both sides produce `Some(f(firstElement))`. For an empty list, both produce `None`.

Thus:

```text
safeHead: List => Option
```

is a natural transformation.

This is a common CS operation: converting between two generic APIs while preserving their payload type.

---

## 5. Transformations can rearrange structure

Consider:

```text
reverse<A>: List<A> -> List<A>
```

It satisfies:

```text
map(f, reverse(xs)) = reverse(map(f, xs))
```

Mapping changes each element independently. Reversing changes only the positions. These operations do not interfere.

Similarly, these are natural:

```text
takeThree<A>: List<A> -> List<A>
duplicateEach<A>: List<A> -> List<A>
```

where:

```text
duplicateEach([x, y]) = [x, x, y, y]
```

A natural transformation does not have to preserve the exact shape. It must manipulate the shape uniformly.

---

# 6. A non-example: removing duplicates

Suppose:

```text
nub<A>: List<A> -> List<A>
```

removes duplicate values.

Take:

```text
xs = [0, 1]
f  = constant(0)
```

First remove duplicates, then map:

```text
map(f, nub([0, 1]))
= map(f, [0, 1])
= [0, 0]
```

First map, then remove duplicates:

```text
nub(map(f, [0, 1]))
= nub([0, 0])
= [0]
```

The results differ:

```text
[0, 0] != [0]
```

So duplicate removal is not a natural transformation `List => List` in the category of sets and arbitrary functions.

The problem is that `nub` examines relationships between payload values. An arbitrary function may turn previously different values into equal values.

Sorting has a similar problem. It depends on extra payload structure—an ordering—and therefore is not a natural transformation between plain `List` functors over arbitrary types and functions.

---

# 7. A transformation that throws the payload away

Define the constant functor:

```text
Const<N, A> = N
```

The type parameter `A` is ignored. Its `map` operation does nothing:

```text
mapConst(f, n) = n
```

Now list length has the type:

```text
length<A>: List<A> -> Const<NaturalNumber, A>
```

In ordinary notation this just looks like:

```text
length<A>: List<A> -> NaturalNumber
```

Naturality says:

```text
length(map(f, xs)) = length(xs)
```

This is true because mapping does not alter the list’s length.

Therefore `length` is a natural transformation:

```text
List => Const<NaturalNumber>
```

This shows that natural transformations may discard all payload values. They simply cannot base their structural output on what those values happen to be.

---

# 8. Products give natural transformations automatically

Suppose `F` and `G` are functors. Their pointwise product is:

```text
(F × G)<A> = (F<A>, G<A>)
```

Mapping is done in both components:

```text
map(f, (fa, ga)) = (mapF(f, fa), mapG(f, ga))
```

The projections are natural transformations:

```text
first<A>:  (F<A>, G<A>) -> F<A>
second<A>: (F<A>, G<A>) -> G<A>
```

Why is `first` natural?

```text
first(map(f, (fa, ga)))
= first(mapF(f, fa), mapG(f, ga))
= mapF(f, fa)
```

while:

```text
mapF(f, first(fa, ga))
= mapF(f, fa)
```

The two routes agree.

More generally, given natural transformations

```text
alpha: H => F
beta:  H => G
```

you can combine them:

```text
pair(alpha, beta): H => F × G
```

componentwise:

```text
pair(alpha, beta)_A(x) = (alpha_A(x), beta_A(x))
```

This is the familiar universal property of products, now applied to functors and natural transformations.

---

# 9. Coproducts work similarly

The pointwise coproduct is:

```text
(F + G)<A> = Either<F<A>, G<A>>
```

Its two injections are natural:

```text
left<A>:  F<A> -> Either<F<A>, G<A>>
right<A>: G<A> -> Either<F<A>, G<A>>
```

Given:

```text
alpha: F => H
beta:  G => H
```

we can combine them by case analysis:

```text
either(alpha, beta): F + G => H
```

defined by:

```text
either(alpha, beta)(Left(fa))  = alpha(fa)
either(alpha, beta)(Right(ga)) = beta(ga)
```

So products and coproducts are not required to define natural transformations, but they provide systematic ways to construct them.

In fact, when the target category has products and coproducts, the category of functors often has them **pointwise**.

---

# 10. Reader computations and dependency adaptation

Fix a type `R`. Define:

```text
Reader<R, A> = R -> A
```

Mapping a function `f: A -> B` means post-composition:

```text
mapReader(f, computation) = f ∘ computation
```

Now suppose:

```text
extract: S -> R
```

An `S` contains enough information to obtain an `R`. We can transform computations requiring `R` into computations requiring `S`:

```text
adapt<A>: Reader<R, A> -> Reader<S, A>

adapt(computation) = computation ∘ extract
```

Naturality follows from associativity of function composition:

```text
adapt(f ∘ computation)
= (f ∘ computation) ∘ extract
= f ∘ (computation ∘ extract)
= mapReader(f, adapt(computation))
```

In software terms, this is dependency or environment adaptation:

- an old component expects configuration `R`,
- the new application provides configuration `S`,
- `extract: S -> R` tells you how to satisfy the old component.

The adaptation works for every possible result type `A`.

---

# 11. Interpreters are often natural transformations

Suppose `Program<A>` describes a program that will eventually produce an `A`, and `IO<A>` represents executing an effectful computation.

An interpreter may have the form:

```text
run<A>: Program<A> -> IO<A>
```

The expected naturality law is:

```text
mapIO(f, run(program))
=
run(mapProgram(f, program))
```

You may either:

1. interpret the program and then process its result, or
2. add the result-processing step to the abstract program and then interpret it.

A well-behaved interpreter should give equivalent results.

This pattern appears in:

- effect systems,
- embedded domain-specific languages,
- free monads,
- tagless-final programming,
- database query interpreters,
- test interpreters that replace real effects with simulated ones.

In Scala libraries this idea is sometimes represented by a type such as:

```text
FunctionK<F, G>
```

or notation resembling:

```text
F ~> G
```

---

# 12. What the definition is really expressing

A functor tells you how a context reacts to a function:

```text
A -> B
```

A natural transformation tells you how to translate between two contexts:

```text
F<A> -> G<A>
```

Naturality ensures these two directions of abstraction are compatible:

```text
change the payload, then translate the context
```

equals:

```text
translate the context, then change the payload
```

This compatibility is the important idea—not merely having a polymorphic collection of functions.

---

# Exercises

## Stage 1: Discovering naturality

### Exercise 1: Calculate both paths

Let:

```text
optionToList(None)    = []
optionToList(Some(x)) = [x]
```

Take:

```text
f: Integer -> String
f(n) = decimal representation of n
```

Calculate both paths around the naturality square for:

```text
Some(42)
```

Then repeat for `None`.

---

### Exercise 2: Prove `safeHead` is natural

Prove by cases that:

```text
mapOption(f, safeHead(xs))
=
safeHead(mapList(f, xs))
```

Consider:

1. `xs = []`
2. `xs = x :: rest`

---

### Exercise 3: Structural list operations

Determine which of these are natural transformations `List => List`:

```text
reverse
takeThree
dropThree
duplicateEach
sort
removeDuplicates
```

For every operation you think is not natural, find a concrete function `f` and list `xs` that violate naturality.

---

## Stage 2: Constant information

### Exercise 4: Other transformations into `Const`

Which of the following define natural transformations?

```text
isEmpty<A>: List<A> -> Boolean
length<A>: List<A> -> NaturalNumber
firstIsEqualToLast<A>: List<A> -> Boolean
```

Interpret the codomain as a suitable constant functor.

Ask: does mapping an arbitrary function over the payload have any chance of changing the result?

---

### Exercise 5: A list-shape summary

Define:

```text
shape<A>: List<A> -> List<Unit>
```

by replacing every element with `Unit`.

For example:

```text
shape(["a", "b", "c"]) = [Unit, Unit, Unit]
```

Prove that `shape` is natural.

What information about the original list does it retain?

---

## Stage 3: Products and coproducts

### Exercise 6: Product projections

For functors `F` and `G`, prove that:

```text
first:  F × G => F
second: F × G => G
```

are natural transformations.

Write out the naturality equation for `first`.

---

### Exercise 7: Pairing transformations

Suppose:

```text
alpha: H => F
beta:  H => G
```

Define:

```text
gamma_A(x) = (alpha_A(x), beta_A(x))
```

Prove:

```text
gamma: H => F × G
```

is natural.

The proof should use the naturality of both `alpha` and `beta`.

---

### Exercise 8: Coproduct case analysis

Suppose:

```text
alpha: F => H
beta:  G => H
```

Define a transformation from `F + G` to `H` by case analysis.

Prove its naturality separately for:

```text
Left(fa)
Right(ga)
```

---

## Stage 4: Building transformations

### Exercise 9: Composition

Suppose:

```text
alpha: F => G
beta:  G => H
```

Define:

```text
gamma_A = beta_A ∘ alpha_A
```

Prove that:

```text
gamma: F => H
```

is natural.

This proves that functors can be treated as objects and natural transformations as morphisms. They form a **functor category**.

---

### Exercise 10: Reader adaptation

Let:

```text
extract: S -> R
adapt_A(k) = k ∘ extract
```

where `k: R -> A`.

Prove that `adapt` is a natural transformation:

```text
Reader<R, -> Reader<S, ->
```

Use associativity of function composition.

---

## Stretch exercise: classify `Option => List`

Try to describe every natural transformation:

```text
eta<A>: Option<A> -> List<A>
```

Questions to consider:

1. What can `eta(None)` contain when it has no `A` available?
2. When given `Some(x)`, what values can the resulting list contain?
3. Can it manufacture a different value of type `A`?
4. Can it place `x` into the output more than once?

You should discover a family of transformations:

```text
None    -> []
Some(x) -> [x, ..., x]
```

where the output contains some fixed number of copies of `x`.

Examples include:

```text
Some(x) -> []
Some(x) -> [x]
Some(x) -> [x, x]
Some(x) -> [x, x, x]
```

Each fixed choice gives a different natural transformation.

---

# Checkpoints

<details>
<summary>Exercise checkpoints</summary>

**Exercise 1:** Both paths produce `["42"]` for `Some(42)` and `[]` for `None`.

**Exercise 3:** `reverse`, `takeThree`, `dropThree`, and `duplicateEach` are natural. Sorting and duplicate removal are not natural over arbitrary sets and functions.

**Exercise 4:** `isEmpty` and `length` are natural. `firstIsEqualToLast` is not: an arbitrary function can collapse two unequal values into one equal value.

**Exercise 5:** `shape` retains exactly the number and positions of list cells, but no payload information.

**Exercise 9:** The proof is:

```text
H(f) ∘ beta_A ∘ alpha_A
= beta_B ∘ G(f) ∘ alpha_A
= beta_B ∘ alpha_B ∘ F(f)
```

using naturality first for `beta`, then for `alpha`.

</details>

The central test to remember is:

```text
map after adapting = adapt after mapping
```

or, conceptually:

> A natural transformation is a context conversion that cannot care what type of values happens to be inside.


---

> [image: sediment://file_00000000d4fc81f7800f13ceffd16f78]
> So here c / d could be any types say int and string, and f is just int to strings, but the context F could be « a list of » so F(c) is a list of ints, and F(d) a list of strings, and F(f) is applying f to the list, but then G could be say, a tree, and alpha c how to turn a list of int into a tree of int (say sorted), and then alpha d out to turn a list of string to a tree of string , but the construction of the tree has to be such that the map over the tree preserves the structure

<details><summary>💭 Thinking</summary>

**Checking naturality**

I’m testing the equation \(G(f)\circ\alpha_c=\alpha_d\circ F(f)\). Since mapping preserves tree shape, sorting or balancing by values generally fails for arbitrary \(f\). A shape-only conversion can be natural; order-preserving maps may rescue sorting in a restricted setting.

**Checked naturality**

**Refining the criterion**

Your equation is right: \(G(f)(\alpha_c(xs))=\alpha_d(F(f)(xs))\). The important correction is that sorting usually fails for arbitrary \(f\), while a conversion based only on list positions or length remains natural because mapping preserves structure.

**Refined the criterion**

</details>

You are very close. The square says that for any types \(c,d\), any function

\[
f:c\to d,
\]

and any \(xs:F(c)\),

\[
G(f)(\alpha_c(xs))
=
\alpha_d(F(f)(xs)).
\]

With your choices:

- \(c=\texttt{Int}\)
- \(d=\texttt{String}\)
- \(F=\texttt{List}\)
- \(G=\texttt{Tree}\)
- \(F(f)=\texttt{mapList}(f)\)
- \(G(f)=\texttt{mapTree}(f)\)

the law becomes:

```text
mapTree(f, alpha_Int(xs))
=
alpha_String(mapList(f, xs))
```

So these two procedures must agree:

```text
List<Int>
  ──build tree──> Tree<Int>
  ──map f───────> Tree<String>
```

and:

```text
List<Int>
  ──map f───────> List<String>
  ──build tree──> Tree<String>
```

## The important correction: sorting is generally not natural

Suppose \(\alpha\) sorts the list before creating the tree. Take:

```text
xs = [1, 2]

f(1) = "z"
f(2) = "a"
```

Going across and then down:

```text
sort [1, 2]       = [1, 2]
build tree        = Tree(1, 2)
map f over tree   = Tree("z", "a")
```

Going down and then across:

```text
map f [1, 2]      = ["z", "a"]
sort strings      = ["a", "z"]
build tree        = Tree("a", "z")
```

These are different:

```text
Tree("z", "a") != Tree("a", "z")
```

Therefore, sorting-based conversion is not a natural transformation between ordinary `List` and `Tree` functors.

The problem is that an arbitrary function \(f\) does not have to preserve ordering.

## A natural list-to-tree conversion

A conversion that depends only on list positions or length can be natural. For example:

```text
alpha_A([])          = Empty
alpha_A([x])         = Leaf(x)
alpha_A(x :: xs)     = Node(Leaf(x), alpha_A(xs))
```

This builds a fixed right-branching tree:

```text
[a, b, c]

Node(
  Leaf(a),
  Node(
    Leaf(b),
    Leaf(c)
  )
)
```

It never examines what `a`, `b`, or `c` actually are.

Therefore:

```text
mapTree(f, alpha_A([a, b, c]))
```

and:

```text
alpha_B([f(a), f(b), f(c)])
```

produce exactly the same tree shape, with corresponding values transformed by \(f\).

A balanced conversion based on list length would also work:

```text
split list in half
recursively build each subtree
```

because mapping changes the elements but not the list length.

## The precise intuition

It is slightly stronger than saying that “mapping over the tree preserves structure.” `Tree.map` already preserves tree structure as part of being a functor.

The naturality requirement says:

> The structure chosen by \(\alpha\) must be compatible with mapping.

For ordinary types and arbitrary functions, this usually means that the tree’s shape cannot depend on properties of the payload values. It can depend on:

- list length,
- element positions,
- a fixed rearrangement,
- a fixed duplication or deletion scheme.

It generally cannot depend on:

- whether values are equal,
- their numerical size,
- their alphabetical ordering,
- comparisons between values.

One further nuance: a binary search tree is usually not a functor over arbitrary functions. Mapping an arbitrary function over a valid search tree can destroy its search-tree ordering invariant. It can be treated functorially only after restricting which functions are permitted—for example, to suitable order-preserving functions.

