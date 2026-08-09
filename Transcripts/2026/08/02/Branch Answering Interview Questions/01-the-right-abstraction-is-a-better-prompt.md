# The Right Abstraction Is a Better Prompt

## Abstract mathematics as a compression format for programming with LLMs

Consider this code:

```ts
const displayPrices: string[] = [];

for (const price of prices) {
  const taxed = addTax(price);
  const converted = convertCurrency(taxed);
  const rounded = roundPrice(converted);
  const display = formatPrice(rounded);
  displayPrices.push(display);
}
```

There is nothing terribly wrong with it. It works. It is readable. You can put a breakpoint in it. A Go programmer is already reaching for the reply button to tell me this is all anybody ever needed.

Now ask an LLM:

> Simplify this code.

You might get a helper function. You might get four chained maps. You might get a `reduce`, because the model has read the same Medium articles as everybody else. You might get a class called `PriceTransformationPipeline`, an interface, a factory, fourteen unit tests and a README explaining the Strategy Pattern.

Or you can tell it:

> These are pure transformations over the same collection. Compose the transformations first, then map the composed function over the collection once.

And it will probably produce something close to:

```ts
const toDisplayPrice = flow(
  addTax,
  convertCurrency,
  roundPrice,
  formatPrice,
);

const displayPrices = prices.map(toDisplayPrice);
```

Same model. Same code. The difference was not intelligence. It was that I finally told the model what shape the problem had.

This is why I have been learning abstract mathematics.

Which is a fairly ridiculous sentence for me to write.

I had remedial math in school. I dropped out of university in no small part because I could not get through statistics and calculus. Numbers have always turned into a kind of static in my head. But I could spend weeks reading about compilers, proof systems, model checking, type systems and the more abstract parts of theoretical computer science.

This confused me for a long time. I thought those things were mathematics too.

It turns out that they are. They are just often mathematics with fewer numbers.

What attracted me was structure: things related to other things, transformations preserving some properties while changing others, little machines that could be composed into larger machines. I could understand the shape of a system even when I could not reliably calculate my share of a restaurant bill.

Then LLMs arrived, and suddenly this way of thinking became useful in a much more direct way.

## The model has to cross the gap you leave it

When we ask a model to change a program, it does not receive the program we have in our head. It receives tokens.

It gets the code, the prompt, whatever documentation fits into the context window, some tool output, and a vast amount of learned statistical structure. It then has to move between representations:

```text
code
→ probable intent
→ repeated pattern
→ possible abstraction
→ implementation strategy
→ new code
```

Every arrow is somewhere the model can drift.

Maybe it decides the point of the loop is mutation. Maybe it decides the point is performance. Maybe it notices the sequence of transformations but reaches for `reduce`. Maybe the word “simplify” activates a large cloud of training examples involving helper classes, design patterns and explanatory comments.

This is not an exotic failure mode. It is most of programming with LLMs.

We write a sentence in one linguistic world and ask the model to produce an artifact in another. The user talks about being unable to reach the navigation. The product manager talks about a sticky header preference. The designer thinks in CSS constraints. The programmer thinks in state transitions. The computer eventually gets instructions.

The model is useful because it can cross these worlds. But the fact that it can cross them does not mean every crossing is equally reliable.

The closer the representation in the prompt is to the representation in the answer, the less interpretive work remains.

This was already the core of my argument about notation: the right notation makes the problem tractable. Abstract mathematics gives us a catalog of unusually dense notations for the shapes that programs take.

A mathematical word is sometimes a tiny program.

## Math is a vocabulary for shapes

The popular image of mathematics is calculation. Mine certainly was: long division, quadratic equations, statistics exams, symbols moving around for reasons that everybody else apparently understood.

A lot of abstract mathematics is doing something else. It identifies structures that recur in very different places, gives them names, and studies the operations that preserve them.

A monoid is not a mystical Haskell creature that lives under a bridge and refuses to approve your pull request. It is a thing with an associative way of combining values and an identity value.

Strings under concatenation form one:

```ts
const identity = "";
const combine = (a: string, b: string) => a + b;
```

Lists under concatenation form one:

```ts
const identity: unknown[] = [];
const combine = <T>(a: T[], b: T[]) => [...a, ...b];
```

Numbers under addition form one:

```ts
const identity = 0;
const combine = (a: number, b: number) => a + b;
```

The concrete values are different. The shared shape is:

```text
combine(combine(a, b), c) = combine(a, combine(b, c))
combine(identity, a) = a
combine(a, identity) = a
```

Once you recognize that shape, you get things for free.

You know how partial results can be combined. You know parallel reduction is possible under the right operational conditions. You know what an empty result should be. You know several properties you can test. You have a word you can put into a prompt.

Instead of explaining:

> There should be a value representing no accumulated output, and combining that value with any accumulated output should leave it unchanged. The grouping of intermediate combinations should not change the final value.

You can say:

> Model the accumulator as a monoid and test the identity and associativity laws.

This is shorter, but compression is not the only benefit. The word points toward a cluster of code, explanations, laws and examples in the model’s training data. It narrows the continuation.

Ordinary words summon examples. Mathematical words summon examples plus laws.

## A functor, reluctantly explained

The word I kept circling in the recording that became this article was *functor*.

This is where programming explanations traditionally become unbearable, because somebody says “a functor is just a monoid in the category of endofunctors,” and six innocent frontend developers close the tab forever.

For the limited purpose of this article, a functor is a structure you can map over while preserving its surrounding shape.

You have a function:

```ts
const formatPrice = (price: Price): DisplayPrice => {
  // ...
};
```

You can apply it to an array:

```ts
const displays: DisplayPrice[] = prices.map(formatPrice);
```

You can apply it to an optional value without manually unpacking and rebuilding the optional value:

```ts
const display: Option<DisplayPrice> = maybePrice.map(formatPrice);
```

You can apply it to a tree:

```ts
const displayTree: Tree<DisplayPrice> = priceTree.map(formatPrice);
```

The array remains an array. The option remains an option. The tree remains a tree. The values inside change from `Price` to `DisplayPrice`.

In a Haskell-shaped notation, this is:

```text
map : (A → B) → F<A> → F<B>
```

Give me a function from `A` to `B`, and I can lift it into a function from a structure containing `A` values to the same kind of structure containing `B` values.

The important part is not the fancy word. The important part is what the word lets us notice.

The original loop was not fundamentally about iteration. Iteration was the mechanism. The structure was “apply a transformation to every value while preserving the collection.”

That distinction changes the prompt.

> Rewrite the loop.

leaves the model choosing what the loop means.

> Express this as a map over the collection.

tells it.

And:

> Compose the pure transformations, then map once.

tells it even more.

## The abstraction budget

I have started thinking of a model as having an abstraction budget.

This is not a benchmarked quantity or a mechanistic claim. It is a working description of what I observe while programming with these things.

A task can require the model to infer several unstated transformations:

```text
customer complaint
→ desired product behavior
→ domain concept
→ state model
→ API
→ implementation
→ validation
```

A sufficiently capable model can sometimes do all of that in one pass. This is the magic trick. It is also why agentic programming can feel like a casino.

Every unstated transition introduces variance. The model can choose a different domain concept, a different state model, a different API. Each choice conditions everything generated after it. The early words and early files become load-bearing.

The context window might be large enough. The abstraction budget might not be.

Naming the structure spends less of it.

Instead of asking the model to discover that a feature is a state machine, represent the feature as a state machine. Instead of describing repeated normalization behavior in prose, call the operation idempotent. Instead of asking it to invent how partial results combine, identify the monoid. Instead of asking it to manually unpack and rebuild containers, ask whether the operation is a map.

These words are not spells. Models can misuse them with tremendous confidence. The point is that a correct abstraction removes a degree of freedom.

Good prompting is often less about adding detail than removing possible interpretations.

## From words to laws

There is another reason abstract mathematics works unusually well with LLM programming: the abstraction does not only suggest an implementation. It suggests ways to reject implementations.

Suppose we ask the model to write a normalizer:

```ts
normalizeUserInput(input)
```

If we recognize normalization as idempotent, we get a property:

```ts
normalizeUserInput(normalizeUserInput(input))
===
normalizeUserInput(input)
```

Suppose we write serialization and deserialization:

```ts
decode(encode(value))
===
value
```

At least for values in the supported domain, that should round-trip.

Suppose we implement `map` for a tree. Functors have identity and composition laws:

```text
map(identity, tree) = tree

map(compose(f, g), tree)
=
map(f, map(g, tree))
```

These are not examples picked by a human who happened to remember an edge case. They are statements about the structure.

This connects abstract mathematics to property-based testing. Instead of writing only a handful of expected input-output pairs, we state a property and generate many inputs looking for a counterexample.

The LLM can help at every stage:

1. Recognize a candidate structure.
2. State the relevant laws.
3. Translate the laws into executable properties.
4. Generate input strategies.
5. Run the tests.
6. Shrink a failure to a small counterexample.
7. Explain whether the structure was misidentified or the implementation is wrong.

The model is not the authority here. The executable property is.

This is the part of LLM programming I find most exciting: not using a model to spray more unit tests over whatever architecture it happened to generate, but using a human-recognized abstraction to constrain both the code and its validation.

The abstraction tells the model what to build. The laws tell us when not to trust what it built.

## A small experiment

I wanted a minimal example that did not depend on trusting my aesthetic preference for functional code.

Take four pure functions over integers:

```ts
const addTax = (x: number) => x * 1.2;
const convert = (x: number) => x * 0.92;
const round = (x: number) => Math.round(x * 100) / 100;
const format = (x: number) => `$${x.toFixed(2)}`;
```

There are two obvious implementations.

One loop:

```ts
function loopVersion(prices: number[]): string[] {
  const out: string[] = [];

  for (const price of prices) {
    out.push(format(round(convert(addTax(price)))));
  }

  return out;
}
```

And one composed map:

```ts
const toDisplay = (x: number) =>
  format(round(convert(addTax(x))));

function mapVersion(prices: number[]): string[] {
  return prices.map(toDisplay);
}
```

For randomly generated finite lists of finite numbers, the outputs are equivalent. This does not prove that every loop can become a map. Side effects, short-circuiting, asynchronous work, mutation, error behavior and intermediate materialization all matter. It proves the narrower thing we claimed: when the loop is already a pure element-wise transformation, the structure gives us a valid rewrite and an obvious equivalence property.

A useful LLM experiment would go further:

- Give several models the loop and ask only to “simplify.”
- Give them the same loop and name the structure.
- Sample each prompt repeatedly.
- Compare output variance, introduced concepts, correctness, token count and the number of follow-up corrections.
- Repeat with a smaller model.

My prediction is not that the mathematical prompt always wins. It is that, where the abstraction is correct and represented in the model’s training, it reduces architectural variance.

That is a testable claim. It should be treated like one.

## This is not a theory of model internals

There is a tempting, much larger claim hiding behind all of this.

LLMs learn relationships between tokens in an enormous high-dimensional space. They can transform a screenshot into code, a transcript into a business plan, a Markdown template into a filled document. They appear able to move from concrete examples toward reusable concept-like representations and back again.

It is very tempting to look at category theory—objects characterized through morphisms, structures related by functors, transformations between transformations—and say: *this is what the model is doing inside*.

I feel the pull of that idea. It is one of the reasons I started learning this material.

But I do not know that it is true.

Research does find abstract, concept-like and sometimes cross-lingual features in model representations. Research also shows that compositional generalization remains difficult and that whatever concepts models learn are distributed, unstable and not guaranteed to line up with clean human abstractions.

So I am making a claim about the interface, not the ontology of the machine.

Category theory and related mathematics give *us* a language for describing structure. LLMs are unusually good at translating between languages and representations. Therefore mathematical language can be a powerful way to communicate programming intent to them.

That is already useful. It does not require discovering a tiny internal Haskell programmer living in the latent space.

## The point is to make the next transformation obvious

I am not learning abstract mathematics because I expect to prove theorems while writing CRUD applications.

I am learning it because programming with an LLM is increasingly the work of selecting representations.

The model can write a loop. It can write a map. It can write a state machine, a reducer, a parser, an event log, a recursive descent nightmare or a beautiful little algebra. The hard part is recognizing which representation makes the essential behavior obvious and the accidental complexity difficult to express.

Abstract math is a catalog of those representations.

It gives names to repeated shapes. The names compress prompts. The laws constrain code. The structures compose. And when the abstraction is right, the code begins to read almost word for word like the thing we meant:

```ts
const displayPrices = prices.map(toDisplayPrice);
```

Transform the prices into display prices.

No `PriceTransformationPipelineManager`. No architecture astronautics. No hoping the model infers the same shape I saw.

The right abstraction did not make the model smarter.

It made the next transformation smaller.
