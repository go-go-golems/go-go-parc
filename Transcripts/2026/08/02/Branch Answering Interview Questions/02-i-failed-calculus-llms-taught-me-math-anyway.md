# I Failed Calculus. LLMs Taught Me Math Anyway

## Using language models to move between examples, code, notation and proofs

I had remedial math in school and dropped out of university partly because I could not pass statistics and calculus.

Twenty years later, I spend an unreasonable number of mornings learning category theory for fun.

The suspicious part is that my tutor is a machine famous for confidently inventing mathematics.

This should not work.

And, used in the obvious way, it does not. You cannot ask an LLM to explain a difficult theorem, nod along to the answer and assume you have learned either the theorem or something true. Models are extremely good at producing the texture of an explanation. Mathematical explanations have a particularly recognizable texture: definitions, notation, a few “therefore”s, perhaps a commutative diagram if the machine is feeling theatrical.

The fact that the prose sounds inevitable does not make the argument valid.

But “tell me the answer” is not how I use LLMs to learn math.

I use them to move.

## The level where I get stuck

The way I was taught mathematics often felt like being dropped onto one rung of a ladder.

Here is the notation. Here is a worked example. Here are twenty exercises that look almost but not entirely like it. Everybody else has apparently understood the invisible connection between them. Good luck.

When I get stuck, it is often not because the idea is impossible. I am stuck at the wrong representation.

I might not understand this:

```text
fmap (g ∘ f) = fmap g ∘ fmap f
```

But I can understand:

```ts
tree.map(x => g(f(x)))
```

and compare it with:

```ts
tree.map(f).map(g)
```

I might not understand an identity morphism, but I understand a refactor that should not change anything.

I might not understand a monoid from the definition, but I understand combining log fragments, merging partial reports or concatenating command-line arguments. I understand that there needs to be an empty value, and that it would be alarming if changing the parentheses changed the result.

The LLM lets me ask for another rung.

```text
concrete data
→ program
→ type signature
→ algebraic structure
→ laws
→ proof
```

Or back down:

```text
proof
→ diagram
→ pseudocode
→ tiny example
→ counterexample
```

A textbook cannot dynamically rewrite itself around the exact misunderstanding I have at 7:30 in the morning. A patient human tutor can, but I do not have a patient category theorist living in my kitchen.

The machine is always available, never embarrassed by repetition and perfectly happy to explain the same idea through a database migration, a compiler pass, a cooking recipe and three bad analogies until one of them finally attaches to something in my head.

That is an extraordinary learning interface.

It is not a source of truth.

## Math without numbers

For most of my life I thought my problem was that I was bad at math.

The more precise version is that I am bad at a large set of activities associated with school mathematics: remembering procedures, doing calculations without losing a sign, manipulating notation before I understand what it represents, and performing all of this under time pressure.

I have much less trouble with abstract structures once they are connected to a concrete system.

This is probably why I ended up around compilers, formal verification, model checking and type systems. They look forbidding from outside, but internally they are full of little worlds with explicit rules.

A parser turns one structure into another. A type checker propagates constraints. A model checker explores state transitions. A proof system tells you which transformations preserve validity.

There are symbols, but the symbols are attached to machinery.

Category theory attracted me for the same reason. At a very rough level, it studies structures through the relationships and transformations between them. Categories have objects and morphisms. Morphisms compose. Every object has an identity morphism. Functors map between categories while preserving identities and composition. Natural transformations relate functors in a coherent way.

That is enough terminology to ruin a dinner party.

But put it next to programming and parts become almost offensively ordinary.

Functions compose. Pipelines compose. Parsers compose. Transformations over containers preserve shape. An API can be characterized by what other things can do with it, rather than by reaching into its internals. A representation is valuable when valid transformations stay valid after you move to another representation.

The abstraction is not floating above the concrete example. It is the reusable shape left after you remove the details.

Once I can move back and forth between the two, the abstraction almost disappears.

## My actual workflow

I do not begin by asking:

> Teach me category theory.

This produces a miniature bad textbook.

I start with a thing I already care about.

For example:

> I have arrays, optional values and trees. In each case I can apply a function to the values without manually rebuilding the surrounding structure. What is the shared abstraction? Start from TypeScript, not mathematical notation.

Then I make the model alternate between explanation and interrogation.

### 1. Ask for several examples and a near-miss

> Give me three programming examples of this structure and one object that looks similar but fails one required law. Do not tell me which is the near-miss until after I guess.

The near-miss is important. Explanations tell me what fits. Counterexamples tell me where the boundary is.

A model will happily say that almost anything is a monad if you let it. Asking it to construct something that violates associativity, identity or composition forces the distinction into view.

### 2. Translate every symbol

> Rewrite the definition with explicit types. Under each line, show the equivalent TypeScript operation. Do not introduce a new symbol without defining it.

Mathematical notation is compression. Compression is wonderful after you know what was compressed. Before that, it is a `.zip` file with no decompressor.

I make the model unpack it.

### 3. Move one rung at a time

> Explain only the jump from this code example to the type signature. Do not explain functors yet.

This has been one of the most useful prompting rules. Models love completing the whole educational arc. They see `map`, race toward monads, then drag in applicatives, Kleisli arrows and a burrito joke from 2012.

I want the next missing transformation, not the entire latent blogosphere.

### 4. Ask it to attack my explanation

After I think I understand something, I write it back:

> A functor is a container with a map function.

Then I ask:

> Treat that statement as a proposed definition. What is wrong, incomplete or misleading about it? Give the smallest counterexample to my wording.

This catches a lot.

Not every functor is usefully described as a container. Having something called `map` is not enough. The mapping must preserve identity and composition. Programming-language encodings and mathematical definitions are related but not identical.

The model is often better at finding problems in a concrete statement than at spontaneously producing a perfectly calibrated explanation.

### 5. Generate exercises, not answers

> Give me five tiny examples. For each, ask whether the operation obeys the identity and composition laws. Do not solve them until I answer.

Or:

> Give me a function and two candidate implementations of `map` for this tree. One should subtly violate a functor law. Write a property test that finds the violation.

The machine can generate an effectively infinite exercise book tailored to the exact concept and programming language I am using.

This is where it becomes much more than conversational search.

### 6. Verify outside the conversation

I keep a real source open.

For category theory, that might be Emily Riehl’s *Category Theory in Context*. For a Haskell concept, it might be the language documentation or a standard reference. For a proof, it might be Lean, Agda, Coq or simply a careful derivation on paper. For a programming law, it can often be executable property-based tests.

The LLM is the translation layer. The book, proof checker or test runner is the court of appeal.

## Counterexamples are better than confidence

The most dangerous property of an LLM tutor is not that it makes mistakes. Textbooks contain mistakes. Teachers make mistakes. I make an impressive number of mistakes before breakfast.

The dangerous property is smoothness.

A model can cross a missing logical step without changing tone. It does not cough. It does not look worried. The false sentence arrives with exactly the same typography as the true sentence.

So I try to build friction into the learning process.

I ask:

> Which step in this argument first requires a fact that has not been established?

I ask:

> Search for a finite counterexample.

I ask:

> State the definition verbatim before applying it.

I ask:

> Separate what follows formally from what is only an intuition.

I ask:

> Give this argument to a skeptical reviewer and list the objections.

Then I check.

This does not eliminate hallucinations. It changes the shape of the interaction from passive acceptance to adversarial editing.

That difference matters because the main educational benefit is not receiving an explanation. It is producing and repairing representations.

## The abstraction ladder

Here is a small example.

Suppose I have fragments of a report generated by several agents:

```ts
type Report = {
  warnings: string[];
  notes: string[];
};
```

I need to combine them.

The concrete implementation is obvious:

```ts
function combine(a: Report, b: Report): Report {
  return {
    warnings: [...a.warnings, ...b.warnings],
    notes: [...a.notes, ...b.notes],
  };
}
```

Then I ask the model to move upward.

What is the identity value?

```ts
const emptyReport: Report = {
  warnings: [],
  notes: [],
};
```

What property should combination have?

```text
combine(combine(a, b), c)
=
combine(a, combine(b, c))
```

What is the named structure?

A monoid.

Now move down somewhere else.

If reports form a monoid, an agent can process separate files, produce partial reports, and combine them in arbitrary groupings without changing the logical result. A reducer has an obvious initial value. Property tests can generate random reports and check identity and associativity.

The abstract name gave me:

- an implementation pattern,
- a parallelization strategy,
- an empty value,
- two laws,
- and a compact prompt for an LLM.

This is when abstract math stops feeling abstract. The word “monoid” almost vanishes into the engineering.

## What the model is unusually good at

LLMs are good at translation between redundant representations.

They have seen prose descriptions, code, equations, tutorials, Stack Overflow answers, papers, diagrams serialized into captions, and millions of examples where one representation is explained through another. They can often connect a concept to the particular technical world I already know.

This does not mean the internal mechanism resembles the human abstraction. It means the interface is extraordinarily capable at moving between forms.

I can ask:

> Show me the same idea as:
>
> 1. a TypeScript API,
> 2. a relational database operation,
> 3. a state-machine diagram described in text,
> 4. a categorical definition,
> 5. and a property-based test.

A normal search engine returns documents. The LLM attempts the transformations.

That “attempts” is doing a lot of work. Some transformations will be false friends. A programming analogy can preserve the mood of a concept while destroying the definition. A model can quietly conflate a function between data structures with a natural transformation between functors. It can call a type a monoid when it means a type equipped with a particular operation and identity.

But these are also productive errors when treated as objects of study.

Why is this analogy wrong? Which property did it fail to preserve? What extra condition would make the statement true?

The failure becomes another exercise.

## Learning math changed how I prompt

I began this because I suspected abstract mathematics might help me understand LLMs.

The immediate payoff was more practical: it helped me communicate with them.

A vague programming prompt often requires the model to discover the structure before it can implement the solution.

> Clean this up.

> Make this more robust.

> Refactor the repeated logic.

These prompts can work, but they leave a large search space.

A structural prompt is different:

> Represent the workflow as a finite state machine. Make invalid transitions unrepresentable and generate transition-table tests.

> Treat normalization as idempotent. Add a property test asserting that a second normalization does not change the result.

> The partial outputs form a monoid under merge. Define the identity explicitly and use it for parallel reduction.

> This operation should be a natural transformation between these two application-level wrappers; verify that it commutes with mapping.  
>  
> (And then check carefully whether I am using “natural transformation” correctly, because this is exactly the kind of sentence an LLM will enthusiastically validate.)

The mathematical vocabulary gives the prompt a target shape. The laws provide acceptance criteria. The notation makes the requested transformation smaller.

I started learning math to climb into abstraction. I found a way to make the model climb less.

## What this workflow cannot do

There are several ways to fool yourself here.

The first is mistaking recognition for understanding. Reading an explanation and thinking “yes, that sounds familiar” is not the same as being able to derive, apply or challenge it.

The second is allowing the model to choose the curriculum. It tends toward statistically central explanations, popular analogies and smooth conceptual arcs. That can leave out the exact technical distinctions that matter.

The third is staying in analogy forever. At some point I have to use the definition, manipulate the notation, construct the proof or implement the law.

The fourth is trusting generated citations. I follow references to their sources. Papers, books and documentation get opened. A title that merely sounds plausible is not a citation.

The fifth is believing every abstract structure improves software. Sometimes the correct program is a loop. Sometimes the algebra hides operational behavior that matters. Sometimes a lawful interface is less legible to the people maintaining it. Sometimes I am just enjoying naming a thing.

Mathematics is a tool for seeing structure, not a moral ranking system for code.

## The machine did not make me good at calculation

I still suck at math in several of the traditional senses.

I lose signs. I forget notation. I can spend an hour understanding something and fail to retrieve it the next morning. There are pages of textbooks where every sentence appears to be written in English and none of them enter my brain.

The LLM did not fix that.

It gave me a different interface to the material.

I can move from the page to code, from code to a diagram, from the diagram to a failed law, from the failed law to a counterexample, and from the counterexample back to the definition. I can ask for one missing rung instead of pretending I followed the leap. I can generate exercises faster than I can exhaust them. I can argue with an explanation until the disagreement becomes precise enough to verify.

The model does not remove the work. It makes the work navigable.

This is also, increasingly, how I think about programming with LLMs.

The quality of the result depends on the representations we choose and the transformations we ask the model to perform. When a task is failing, I no longer only ask whether the model is capable enough. I ask whether I have placed the problem on the wrong rung.

The machine did not make me good at calculation.

It gave me a way to keep changing the representation until calculation stopped being the interesting part.
