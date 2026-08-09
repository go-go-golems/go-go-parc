# The Right Abstraction Is a Better Prompt

## Abstract mathematics as a compression format for programming with LLMs

I can give a coding model this:

```ts
const taxed: number[] = [];
for (const price of prices) {
  taxed.push(addTax(price));
}

const converted: number[] = [];
for (const price of taxed) {
  converted.push(convertCurrency(price));
}

const rounded: number[] = [];
for (const price of converted) {
  rounded.push(roundPrice(price));
}

const formatted: string[] = [];
for (const price of rounded) {
  formatted.push(formatPrice(price));
}
```

and say:

> Simplify this.

This feels like a small prompt. It is three words. It is also a request for the model to rummage through most of software history and guess what kind of simplicity I care about.

It might extract a helper. It might replace the loops with four calls to `map`. It might use `reduce`, because `reduce` is what programmers reach for when they want to demonstrate that they have encountered functional programming. It might create a `PriceTransformationPipeline`, because somewhere in the training corpus there is an enterprise Java application patiently waiting to ruin my afternoon. It might preserve every intermediate array because they look intentional. It might decide that “simplify” means “make shorter” and turn the whole thing into an unreadable one-liner.

Or I can say:

> These are pure, element-wise transformations over the same collection. Compose them into one function called `toDisplayPrice`, then map that function over `prices` once. Preserve order and the final output type.

And get something like:

```ts
const toDisplayPrice = (price: number): string =>
  formatPrice(
    roundPrice(
      convertCurrency(
        addTax(price),
      ),
    ),
  );

const formatted = prices.map(toDisplayPrice);
```

Same model. Same source code. The useful difference is not that the second prompt contains more details. It is that it tells the model what **shape** the problem has.

The first prompt asks the model to discover the abstraction and then implement it. The second prompt gives it the abstraction and asks for a fairly mechanical translation.

A couple of months ago I started learning abstract mathematics because I kept noticing this exact pattern. I am not doing this because I have secretly become good at math. Math has always been something I really, really struggled with. I had remedial math at school. I dropped out of university partly because I could not do statistics and calculus. This is not the usual origin story for someone voluntarily opening a category theory book.

But over the years I spent a lot of time around compilers, proof systems, model checking, types, programming languages, and the more abstract parts of theoretical computer science. I had much less trouble with those, for the extremely sophisticated reason that there were not many numbers. There were mostly structures: things that related to other things, operations you could perform, rules that had to remain true.

It turns out that this is also an unusually useful way to think about programming with LLMs.

## The prompt had an entire compiler hidden inside it

When I write “simplify this”, I am hiding a sequence of transformations from myself:

```text
source code
→ observable behavior
→ repeated structural pattern
→ candidate abstraction
→ suitable notation
→ replacement program
→ evidence that the replacement is equivalent
```

I do not claim that this is a literal trace of what happens inside a model. It is a description of the work I left unspecified at the interface.

The model has to infer that every loop preserves order, produces exactly one output for every input, does not depend on shared mutable state, and exists only to apply another function. It has to notice that the intermediate collections are not semantically important. It has to decide that composition is the kind of simplicity I want. Then it has to choose a programming notation for that idea.

Once I say “pure element-wise transformations”, “compose”, and “map once”, most of those branches disappear:

```text
named structure + constraints
→ ordinary code expressing that structure
```

This is the same argument I have made before about [every word in a prompt being load-bearing](https://gogogolems.substack.com/p/from-prompt-and-pray-to-prompt-engineering), except mathematical words carry a particularly useful kind of weight. A word like “diary” summons a cultural pattern: chronology, reflection, notes to oneself. A word like “idempotent” summons a pattern **and a law**.

That distinction is the whole article:

> Ordinary words summon examples. Mathematical words summon examples plus laws.

The law is what turns the word from a vibe into an engineering tool.

## Math is a vocabulary for recurring shapes

Abstract mathematics has an accessibility problem, which is that the vocabulary sounds as if it was developed to make ordinary people leave the room.

Monoid. Functor. Morphism. Natural transformation. Fixed point. Partial order.

The useful part is not that these words make simple programs sound profound. The useful part is that one strange word can replace fifteen paragraphs of almost-English.

Take a monoid. In the programming-adjacent version, I need:

1. Some kind of value.
2. A way to combine two values into another value of the same kind.
3. An empty value that changes nothing when combined.
4. A guarantee that regrouping combinations does not change the result.

For an append-only list of diagnostics:

```ts
type Diagnostics = readonly string[];

const emptyDiagnostics: Diagnostics = [];

const combineDiagnostics = (
  left: Diagnostics,
  right: Diagnostics,
): Diagnostics => [...left, ...right];
```

The identity laws say:

```text
combine(empty, x) = x
combine(x, empty) = x
```

Associativity says:

```text
combine(combine(a, b), c)
=
combine(a, combine(b, c))
```

This does **not** say that order is irrelevant. String and list concatenation are associative but not commutative. `a + b` does not generally equal `b + a`. The law says I can change the parentheses, which is exactly what I need if I want to aggregate chunks in a tree, split work across processes, or refactor a left-associated pipeline into a balanced one.

Now compare these two prompts:

> Collect diagnostics from all workers. Make sure empty workers do not cause trouble and parallel aggregation produces the same result.

and:

> Model ordered diagnostics as a monoid under concatenation: `[]` is the identity and `combine` must be associative. Add property tests for both laws.

The second prompt is not better because the model likes Haskell programmers. It is better because the word “monoid” gives a compact name to the operation, the identity, and the law that makes regrouping safe. I have reduced the number of concepts the model has to invent while generating the answer.

Of course this only works when the abstraction is actually correct. A wrong abstraction is an aggressively compressed bug. If `combine` depends on the wall clock, mutates shared state, deduplicates differently depending on grouping, or treats “first error wins” inconsistently, calling it a monoid does not bless it. It merely causes the model to produce confident code around a false premise.

That is why learning the laws matters more than collecting the vocabulary.

## Category theory, very reluctantly

Category theory is the particularly abstract branch of mathematics hovering behind a lot of these programming words. The informal attraction is that it lets you study things through their relationships and transformations instead of constantly opening them up and examining their internals.

The formal definition is less vague: a category has objects and morphisms between objects, an identity morphism for every object, and an associative way to compose compatible morphisms.[^riehl-category] That precision matters. “Things connected to other things” is a graph. It is not automatically a category.

The programming intuition I care about is composition. If I have:

```text
A → B
B → C
```

then I can compose them into:

```text
A → C
```

Again, this sounds almost insultingly obvious. But an enormous amount of software is made difficult by APIs that fail to compose, transformations that silently discard information, effects that leak into the middle of otherwise clean pipelines, and data structures whose representation has become part of every caller.

The obvious rule goes deep because it forces questions:

- What is the input and output of this operation?
- Can the next operation consume the previous output directly?
- What properties survive the transformation?
- Is there an identity operation?
- Does regrouping change behavior?
- Can I replace one representation with another without changing what callers can observe?

These questions are useful when writing code. They are even more useful when asking a probabilistic machine to write code, because every unanswered question becomes another branch in generation.

## A functor, reluctantly explained

Functor is one of those words Haskell programmers use in a way that makes everybody else suspect a prank.

Here is the useful programming version.

Suppose I have a function:

```ts
const formatPrice = (price: Price): DisplayPrice => {
  // ...
};
```

I can apply it to an array of prices without manually dismantling and rebuilding the array:

```ts
const displays: DisplayPrice[] = prices.map(formatPrice);
```

I can do the same thing to a tree if the tree provides its own mapping operation:

```ts
type Tree<T> =
  | { type: "leaf"; value: T }
  | { type: "branch"; left: Tree<T>; right: Tree<T> };

function mapTree<A, B>(tree: Tree<A>, fn: (value: A) => B): Tree<B> {
  if (tree.type === "leaf") {
    return { type: "leaf", value: fn(tree.value) };
  }

  return {
    type: "branch",
    left: mapTree(tree.left, fn),
    right: mapTree(tree.right, fn),
  };
}

const displayTree: Tree<DisplayPrice> = mapTree(priceTree, formatPrice);
```

The function still goes from `Price` to `DisplayPrice`. The surrounding structure knows how to lift that into a transformation from `Array<Price>` to `Array<DisplayPrice>`, or from `Tree<Price>` to `Tree<DisplayPrice>`, while preserving the array-ness or tree-ness of the thing.

That is a useful intuition for a functor: a structured context with a lawful way to map functions over it. The full categorical definition maps objects and morphisms between categories while preserving identities and composition.[^riehl-functor]

The laws matter again. In programmer notation:

```text
map(identity) = identity
map(g ∘ f) = map(g) ∘ map(f)
```

For an array, that means mapping a function that does nothing should leave the elements unchanged:

```ts
prices.map(price => price)
```

And, for pure unary functions, mapping `f` followed by `g` should produce the same elements as mapping their composition:

```ts
prices.map(f).map(g)
```

should agree with:

```ts
prices.map(value => g(f(value)))
```

The equality here is about the resulting elements, not JavaScript object identity. `map` still creates a new array.

While recording the original version of this article, I slid from this into saying that turning a list into a tree was therefore “transforming one functor into another”. That is exactly the kind of sentence that sounds right once you have learned four nouns and should make you stop. A function from lists to trees is just a function from lists to trees. Calling a family of such functions a natural transformation requires an additional naturality condition.[^riehl-natural] I had the vibe before I had the law.

This is not an embarrassing exception to the argument. It is the argument. The notation gives me something strict enough to reveal where my understanding ends.

## Mathematical vocabulary constrains generations

There is no magic prompt where adding `monoid` makes a model write good software. Mathematical terms work when they remove genuine ambiguity.

Consider a retryable operation. I can say:

> Make this safe to retry.

The model now has to decide what “safe” means. No duplicate row? Same HTTP response? No second charge? No repeated email? Is a repeated log entry allowed? What if the first request partially succeeded?

Or I can say:

> Make `capturePayment` idempotent with respect to the idempotency key. After the first successful application, repeating the same request must not change externally observable payment state. Persist and return the original result. Add a property test covering repeated delivery.

“Idempotent” gives the central law:

```text
f(f(x)) = f(x)
```

The rest of the prompt defines what counts as the same operation and which observations matter. The mathematical word compresses the center of the requirement; the domain language pins it to reality.

A few other examples:

```text
“Represent the checkout flow as an explicit state machine.”
```

This suggests named states, explicit transitions, and handling for invalid transitions instead of booleans accumulating until the codebase becomes a poorly documented state machine anyway.

```text
“Treat dependency reachability as a partial order when the graph is acyclic;
produce a topological schedule and report cycles explicitly.”
```

This distinguishes dependency constraints from a single arbitrary total sequence.

```text
“Normalize this value to a fixed point and assert that applying normalization
a second time makes no further change.”
```

This turns “clean it up repeatedly until it looks stable” into an executable condition.

```text
“Expose a lawful `map` over the contained value without exposing the container’s
representation.”
```

This tells the model which operation belongs on an `Option`, `Result`, or tree, and which properties should survive a refactor.

These are not just implementation hints. They shape the API, the names, the tests, and the ways the resulting pieces can be combined later.

This is why abstract mathematics feels like a compression format for prompts. The model has seen the term in textbooks, library documentation, type-class definitions, proofs, code, arguments between Scala programmers, and many thousands of examples. A precise term puts that whole cluster of patterns near the generation.

But compression is only useful when both sides share the dictionary. “Functor” is overloaded across mathematics, Haskell, OCaml, C++, and ordinary English uses of “function object”. A prompt that says only “make this a functor” can still spray. A prompt that says “model `Tree<T>` as a covariant functor over `T`; implement `map` and test identity and composition” is much harder to misunderstand.

Every word is still load-bearing. Mathematical words are just unusually dense building materials.

## The laws become tests

The most valuable thing about recognizing a mathematical structure is not that the generated code looks elegant. It is that the structure arrives with ways to falsify the implementation.

Property-based testing takes a general claim about behavior and checks it over generated inputs, looking for counterexamples rather than relying only on a handful of examples.[^quickcheck] The laws above translate almost word for word.

Using `fast-check` in TypeScript:

```ts
import fc from "fast-check";

const identity = <T>(value: T): T => value;

fc.assert(
  fc.property(fc.array(fc.integer()), values => {
    expect(values.map(identity)).toEqual(values);
  }),
);
```

Composition:

```ts
fc.assert(
  fc.property(
    fc.array(fc.integer()),
    fc.func(fc.integer()),
    fc.func(fc.string()),
    (values, f, g) => {
      // Wrap both generated functions so JavaScript's extra map callback
      // arguments (index and array) are not part of the function being tested.
      const sequential = values
        .map(value => f(value))
        .map(value => g(value));
      const composed = values.map(value => g(f(value)));

      expect(sequential).toEqual(composed);
    },
  ),
);
```

Idempotent normalization:

```ts
const normalize = (value: string): string =>
  value.trim().replace(/\s+/g, " ").toLowerCase();

fc.assert(
  fc.property(fc.string(), value => {
    expect(normalize(normalize(value))).toBe(normalize(value));
  }),
);
```

Round trips give another common property:

```text
decode(encode(x)) = x
```

A monoid gives identity and associativity tests. A state machine gives transition invariants. A parser and printer may give round-trip properties. A canonicalizer should usually be idempotent. A sorting operation should be ordered and preserve the input multiset. Once the abstraction is explicit, I can ask the model to produce candidate properties, generators, and counterexamples instead of asking it to invent twenty example tests that happen to resemble the current implementation.

This is where the combination of LLMs and abstract math becomes much more useful than “put a fancy word in your prompt”. The same abstraction helps generate the program and helps reject the program.

## Composition can make the program cheaper too

In the opening example, replacing four loops with one `map` removes three full intermediate collections. The exact performance difference depends on the runtime, the functions, the data, and what the optimizer manages to do.

A small benchmark run for this draft used 500,000 numbers, four pure numeric transformations, Node 22.16.0, eight warm-up rounds, and twenty measured rounds. Four `map` passes took a median of 63.13 ms. One `map` with the functions composed took 16.06 ms: about 3.93 times faster in that particular container.[^benchmark]

That number is not a new law of computer science. The structural facts are more useful: the four-pass version invokes array traversal four times and constructs four result arrays; the fused version traverses once and constructs one result array. The timing merely confirms that this can matter in an ordinary runtime.

The purity qualification is load-bearing. These two programs can return the same values while performing effects in a different order.

Separate maps:

```text
f1, f2, f3, g2, g3, g4
```

Fused map:

```text
f1, g2, f2, g3, f3, g4
```

If `f` and `g` write logs, mutate state, perform network requests, throw exceptions, or depend on timing, the transformation may change observable behavior. In the experiment used for this draft, the pure outputs matched exactly, while a deliberately effectful trace demonstrated the ordering difference.

This is another reason the abstraction is useful: it does not merely suggest a refactor. Its assumptions tell me when the refactor is valid.

And honestly, the performance improvement is not the main reason I want the composed version. This is:

```ts
const formatted = prices.map(toDisplayPrice);
```

The code now almost says the same thing as the requirement: transform prices into display prices. The ugly mechanics have collapsed into a named arrow from one domain concept to another. The prompt, the code, and the mental model line up.

That alignment is valuable to a tired programmer. It is also valuable to a model generating one token after another, because there are fewer unrelated structures to keep alive in the surrounding context.

## This does not prove there is a category theorist in the model

The tempting jump is to say that LLMs must internally discover the same abstractions mathematics discovered. I made some version of this jump in the recording: maybe different domains share a common region of latent space; maybe the model has learned a fuzzy internal equivalent of the abstractions I am naming.

There is interesting evidence in that direction, but not enough for the strong claim.

Researchers have found internal representations corresponding to Othello board state in a sequence model, linear representations of spatial and temporal information in language models, and both linear and irreducibly multidimensional representations of concepts in model activations.[^representations] There are also benchmarks on which current language models perform poorly at novel abstract reasoning and broad generalization.[^abstract-reasoning]

So: models clearly learn more than a lookup table of complete sentences. They develop internal features and representations that can sometimes be decoded and causally manipulated. But that does not mean there is a clean, human-readable library of monoids and functors inside the network, or that a model’s successful use of a term demonstrates human-like understanding.

Fortunately I do not need that claim.

I am making an interface claim: changing the representation of a task changes how tractable the task is for a model. Research on scratchpads, decomposition, and program-aided reasoning makes the broader point that intermediate representations and executable notation can materially change model performance.[^representation-prompting] My claim for programming is more practical and narrower: when I can name the actual structure of a problem, the prompt contains fewer hidden translations, the generated API is usually clearer, and the laws give me better ways to test it.

Whether the model internally represents “functor” the way a category theorist does is interesting. Whether the prompt gives me correct, composable code is the engineering question.

## Back to the loops

The original code was not bad because it contained `for`. Go is not morally inferior because it makes loops normal, and Haskell does not become correct merely by surrounding a mistake with enough types.

The problem was that the structure was present but unnamed. Every element went through the same sequence of pure transformations. The intermediate arrays were accidental. The operations composed. Once I recognized that, I could say it directly:

```ts
const formatted = prices.map(toDisplayPrice);
```

The real prompt engineering happened before I typed the prompt. It happened when I looked at four concrete loops and recognized one abstract operation.

That is why I am learning abstract math. Not because I expect to prove theorems while writing CRUD applications, and not because every codebase should become a category theory demonstration. I am learning it because it gives me a catalog of structures that recur across programs, APIs, tests, and domains. It gives me names for the shapes I was already seeing badly.

Programming with an LLM is largely the work of finding a representation in which the next transformation becomes obvious — to the machine, and to me when I am tired.

The right abstraction is not decoration added after the program works.

It is often the smallest prompt that tells the model what program we were writing in the first place.

---

## Notes

[^riehl-category]: Emily Riehl, [*Category Theory in Context*](https://emilyriehl.github.io/files/context.pdf), Definition 1.1.1, pp. 3–4. A category includes objects, morphisms with specified domains and codomains, identity morphisms, and associative, unital composition.

[^riehl-functor]: Riehl, [*Category Theory in Context*](https://emilyriehl.github.io/files/context.pdf), Definition 1.3.1, p. 14. A functor maps objects and morphisms and preserves identities and composition. The “mappable container” explanation used here is a programming intuition for common endofunctors, not the full definition.

[^riehl-natural]: Riehl, [*Category Theory in Context*](https://emilyriehl.github.io/files/context.pdf), Definition 1.4.1, p. 25. A natural transformation is a family of morphisms between parallel functors satisfying a commuting naturality square; an arbitrary conversion function between two data structures is not automatically one.

[^quickcheck]: Koen Claessen and John Hughes, [“QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs”](https://dl.acm.org/doi/10.1145/351240.351266) (ICFP 2000); John Hughes, [“How to Specify It! A Guide to Writing Properties of Pure Functions”](https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf) (TFP 2019/2020). Hughes distinguishes properties such as invariants, postconditions, metamorphic properties, inductive properties, and model-based properties.

[^benchmark]: Reproducible drafting experiment, 2026-08-02: Linux/x64, Node v22.16.0, V8 12.4, 500,000-element ordinary JavaScript array, four pure numeric transforms, eight warm-ups, twenty alternating measured rounds with explicit GC between runs. Median: four maps 63.1346 ms; one fused map 16.0621 ms; ratio 3.9307×. Outputs were compared element-by-element. This is a microbenchmark, not a portable performance guarantee. Full script and output are included in the accompanying editorial/research log.

[^representations]: Kenneth Li et al., [“Emergent World Representations: Exploring a Sequence Model Trained on a Synthetic Task”](https://openreview.net/forum?id=DeG07_TcZvT) (ICLR 2023); Wes Gurnee and Max Tegmark, [“Language Models Represent Space and Time”](https://arxiv.org/abs/2310.02207) (2023/2024); Kiho Park, Yo Joong Choe, and Victor Veitch, [“The Linear Representation Hypothesis and the Geometry of Large Language Models”](https://arxiv.org/abs/2311.03658) (ICML 2024); Joshua Engels et al., [“Not All Language Model Features Are Linear”](https://arxiv.org/abs/2405.14860) (2024). These papers study particular models, concepts, and intervention methods; they do not establish a single universal account of abstraction in LLMs.

[^abstract-reasoning]: Gaël Gendron et al., [“Large Language Models Are Not Strong Abstract Reasoners”](https://www.ijcai.org/proceedings/2024/693) (IJCAI 2024), reports limited performance on a benchmark designed to test abstraction beyond memorized surface patterns. The result should not be treated as the last word on rapidly changing models, but it is a useful counterweight to broad claims about internal abstraction.

[^representation-prompting]: Maxwell Nye et al., [“Show Your Work: Scratchpads for Intermediate Computation with Language Models”](https://arxiv.org/abs/2112.00114) (2021); Denny Zhou et al., [“Least-to-Most Prompting Enables Complex Reasoning in Large Language Models”](https://arxiv.org/abs/2205.10625) (2022); Wenhu Chen et al., [“Program of Thoughts Prompting”](https://arxiv.org/abs/2211.12588) (2022); Luyu Gao et al., [“PAL: Program-aided Language Models”](https://arxiv.org/abs/2211.10435) (ICML 2023). These works are not direct tests of category-theoretic prompting; they support the broader claim that decomposition and the choice of intermediate representation can change task performance.
