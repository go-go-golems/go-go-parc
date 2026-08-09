# Branch · Answering Interview Questions

- URL: https://chatgpt.com/c/6a6f8cc1-1a88-83ea-8f10-9a09e9ab8274
- Created: 2026-08-02T18:30:26.444Z

---

> ---
> note_id: 0cb27c2c-383d-4db0-b805-98a7b5443efc
> recorded_at: 2026-08-02T16:43:44Z
> created_at: 2026-08-02T17:00:13.989753Z
> title: "LLMs and Abstract Math"
> ---
>
> # LLMs and Abstract Math
>
> All right. Um, I'm gonna walk through an article I wanna write, which is, um... And this, this might be a little bit too much, maybe a two-parter, but the, the-- basically it's about how I use LLMs to learn abstract math, and also why I learn abstract math and what you can do with it. So, starting a couple of months ago, and, and math has always been something I really, really struggle with. I had remedial math at school, and I dropped out of university because I couldn't do statistics and calculus. But over the years, I've, uh, I've tried to, to learn a lot, and I've also like read a lot, played a lot with compilers and proof systems and model checking and all the like more abstract part of, uh, of, uh, theoretical computer science, which I had much less problems with, um, 'cause there weren't really any numbers. They were just like abstract structures. So anyway, um, I knew that there was something about looking at core structures of basically abstraction and in LLMs, that LLMs are ultimately like pattern matchers and pattern transformers. Um, which you can see if you give it, say, a markdown structure document, and then you ask it to fill it with a certain type of context content, it will merge both structures. It will adapt the content to fit into the markdown structure, for example. And you can see it in programming, right? Like you give it a task and you give it an API, and it will combine both or it will even maybe start using patterns out of the training corpus. So I always had this feeling that there's a really deep connection between abstract mathematics, uh, which is, uh, if you, if you take category theory is in a way, uh, recognizing the structure, how being able to describe something purely by its relationships, um, without being able to look into the structure itself, um, or like look into the thing itself, was something that was really fundamental to, um, even before LLMs computer programming, but with LLMs, uh, e-even more so since, um, since these patterns exist, right? Like recognizing that something like types are, uh, can be modeled as a monoid or all these funky words that Haskell programmers use. Functors, that you can recognize the list of something as a functor, and you can like then transform a functor to another functor. So say list of a type T can be transformed to a tree of type T 'cause you can just like traverse a tree to turn it into a list, right? So there's these really deep connections that once you put the abstraction in connection with the concrete is very obvious. So obvious that it actually is really hard to explain what the abstraction is 'cause it's almost disappearing. Uh, but these, these abstractions can be composed. So i-again, comp-- category theory being about describing something in terms of the relationships of its objects, of its constituents, without even looking into the constituents, but also very much about transforming structures into other structures while conserving certain properties, right? Like that's, that's basically the only things that are given in category theory is things, relationship between things called arrows or morphisms. And then, um, these morphisms have to compose. Uh, which means that, um, if you-- if something is in relationship with something else and this some other thing is in relationship with a third thing, then the first thing is in relationship to the third thing, which sounds absolutely abstract, um, and almost entirely obvious, um, but goes really deep. So, so anyway, this was an excursion about category theory. Um, and s-so the, the immediate connection to, to LLMs is that LLMs only understand the world through the relationship of symbols to other symbols, right? If you describe a token as a symbol, the only way LLMs kind of do intelligence, do have a relationship to concrete things is by, uh, just modeling relationship between every token to another token. And out of that, after it's been learned, obviously there's like an insane amount of, um, dimensions to these relationships. Um, you, you, you get whatever LLMs do these days, right? Um, there, there's nothing else. There, there's like a big way of putting tokens in relationship to other tokens. Um, and I think what's happening in LLMs is that they are able to internally recognize abstractions that work. And math or in a certain sense, any kind of like theoretical approach to certain disciplines is about identifying abstractions that work and then putting these abstractions to use. Um, and so really, really abstract stuff like category theory allows you to take structures that work in a certain domain and then realize, "Oh, but they're the structure that works in another domain." So in a way, uh, there's a good chance that the LLM internally has like kind of a common part of the latent space that maybe corresponds to it. So this is, this is just vibes because I am not actually a machine learning LLM expert. So this is just me as a user and experimenting a lot with these, with these devices, um, that LLMs are able to recognize Abstractions that increasingly are, um, are out of human comprehension, right? I mean, th-they always were, but they are now so effective, yet completely outside of what we know. Because they do have, say, the abstraction of turning an image into a webpage, right? [chuckles] Which, which is, which is something that, that no one really, uh... I mean, humans obviously do, right? But nobody is able to kind of express. Um, we have all these books about good design and about good web programming and so, but, but LLMs have built an internal representation of what that actually is. Like, they are able to put it in terms of, of math at the end of the day. Um, so this is about, like, the relationship between LLMs and abstract math, is that s- if they have built these internal structures that allow them to abstract away from the concrete, but also go back from the abstraction back to the concrete, um, say the abstraction of a m- certain markdown structure or the abstraction of a bullet point list, and then take the abstraction of... Or, like, the very concrete representation of, say, a business plan, but a business plan as a transcript of an audio recording, they are able to transform this to the abstract space of a bullet point list, and then put it back into, into basically a, a bullet point list for a business plan. So recognizing which abstractions work well for an LLM and then just composing them make it really easy for an LLM to do a good job. And I think that was always the strength that I had, is like, from the beginning, my mental representation of an LLM was as something that puts things into relationship to another and is able to transpose that, uh, to transform things. And I, I, I was always, like, confused by the fact that calling an LLM a stochastic parrot is, like, kind of a bad thing because it actually shows how amazing it is to stochastically model something to then create these, like, very powerful abstractions that are fuzzy, and as such, are able to kind of brute force things, so they're not always correct. Um, but that's kind of what we do with programming as well, right? Like, one of the, the beautiful things about programming is that as much structure as there is in it, you can kind of fuck around. [chuckles] And you can, you can be like, "Well, this doesn't really obey the laws of a monoid. Whatever, fuck it. It's still working. It's still shippable." Um, which is, which is really a really big strength in many ways, because the amount of work you have to do to prove something mathematically or to, to say, be able to compose the abstractions that certain Haskell or Scala programmers like to use, which is, like, literally use the mathematical terms in the code they write, um, eliminates a whole part of the programming population that maybe has much more... Has a, a, a whole different set of value to, to provide. Like, they have a good business sense. They know how to talk to users. They have a good design sense. They are very good at, uh, validating their work. They're... You know, they- there, there's so many ca- ca- ca- capabilities that go into making good software. Being correct, being just, like, a tiny part of, of it, right? And, uh, um, so, so anyway, uh, uh, LLMs being machines that are able to go back and forth the ladder of abstraction is, is a, is a, is a magical thing. And k- knowing which abstractions... You know, having, like, as a human, a, a, like a deep understanding of these structures or deep knowledge of these different structures allows you to prompt an LLM in the way that you help it do a sequence of transformations that work well. So for example, um, you can have an LLM do, like, a lot of for loops, or you can have it use, you know, a functional pipeline if you understand that these for loops actually do obey the structure of a functional pipeline with map. Um, map often being called a functor when it's used in, in programming because it allows you to apply a func- a function of A on something that's a functor of A. So if you, if we say that list of integers is a functor, um, it means that we can take a function F that operates on integers, say transforms an integer to a string, and then we can map that onto a list of integers, so a functor of int. A- and we're able to then suddenly have a list of strings, so a functor, uh, uh, of strings, right? Um, so being able to suddenly say, "Hey, these 15 for loops are actually 15 map compositions," and actually the map composition allows you to compose the function up front and then just do a single map. Uh, s- suddenly you have not only a much faster algorithm, but it's, it's about [chuckles] it, it, it's about, you know, f- a hundred times less tokens, and you're able to give it good names, right? Like a for loop, you can, you can say that a for loop is about transforming, uh, prices into, uh, a display, display representation. So like from integers, uh, decimal floating... Decimal point integers to, you know, a dollar string representation of something. Um, suddenly you're able to say, "Hey," uh, you know, just like prices.map to display or like price to display, and suddenly you have the... You have abstracted... You have recognized that in the for loops there is actually abstraction of applying something to a list of things- And you are even able to give a name to this something, um, which might be less obvious in the for loop. Uh, and then suddenly you're back into like totally normal, um, um, English language. 'Cause you, you can say transform the list of prices into, uh, uh, a list of display values, and the code actually matches that almost word for word. Um, so this is no secret, right? Like, this has always been, uh, uh, kind of not like a point of debate, for example, across programmers. Like, say, Golang being like pushing you very hard into the, the for loop space, while programming in Haskell will push you very strongly into the functional pipeline space. But the thing is that if you, if you tell the model like, "Hey, you know, this is a functor," model it as a functor and then write the solution to it allows you to have a very, very effective prompt. Uh, use a very, very small model because there is not much linguistic abstraction transposing work to be done, and, uh, also requires the model to do very few of these abstraction steps. While the abstraction of transforming, you know, apply-- uh, uh, transform the list of prices and then mapping that to a for loop is much higher than just mapping words to words and being like, "Yeah, I, I'm kind of, uh, I'm kind of, uh, tired. I, I can do this," right? It's like, it's like having Arabic numerals and algebraic notations kind of allow us to solve polynomials even when really, really tired because we can write it out on paper and kind of apply some very basic transformation rules. Not knowing that suddenly solving at least quadratic polynomials or like, like, um, quadratic equations, uh, or, or, uh, um, s- s- like single dimension equations, I, I suck at math. Um, because you're able to write it on paper suddenly becomes easy. And in, in a way that's kind of... LLMs are very similar to us in, in that kind of way, is that they think linearly, they use notation, they use symbols, and then they are good at applying like rote patterns to things. Um, so this was all an excursion of like why, uh, abstract mathematics can lead to really, really good prompts, is like abstract mathematics helps us write composable code or like recognize structures in code and transform them into notation. Um, and, um, that allows us to, to have really good prompting techniques that lead to elegant APIs that can then be composed without introducing complexity. Thus, the code is like less fragile. It also allows us to, uh, reason about this code much more easily because it has a mathematical foundation that we can now prove or add at least a couple of it invariants or do like quick check type of unit testing where we use, uh, um, the mathematical abstraction to create test cases. Um, it allows us to compose things while being able to assert invariants on the composition of them. Um, so really, really powerful and, uh, maybe this is enough for a first article, right? It's like the link between these two things, and I, I could, uh, probably go back and illustrate these things. So thinking about illustrations, one is definitely showing what a functor, the functor of list and the functor of trees, uh, allows one to do. Um, just as a couple of code examples and then showing how that maps to, to, uh, to the prompt, um, I think is a, is a pretty good idea to just introduce the, the whole thing. And with the sake of shipping all of this and not making like three articles out of it, 'cause this is not something that I didn't even wanna cover, I'm gonna stop it here.
>
> ---
>
> Suggest some article ideas / structures for my blog about programming with LLMs (see gogogolems.substack.com for my style and voice and content)

I’ll compare this transcript with a few representative posts from your Substack, then propose article angles, outlines, and likely splits that fit your existing voice.

```json
{"system1_search_query":[{"q":"site:gogogolems.substack.com gogogolems Substack programming LLMs"},{"q":"site:gogogolems.substack.com category theory LLM programming"},{"q":"site:gogogolems.substack.com \"Gogo Golems\" Substack"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

The transcript contains at least three viable essays. The strongest version is not a general “category theory explains LLMs” piece; it is a concrete argument that mathematical notation reduces the number of transformations a model must perform.

```json
{"system1_search_query":[{"q":"site:gogogolems.substack.com/p \"Manuel Odendahl\" \"LLM\" \"notation\""},{"q":"site:gogogolems.substack.com/p \"generalization\" \"Manuel Odendahl\""},{"q":"site:gogogolems.substack.com/p \"abstraction\" \"Manuel Odendahl\" \"programming\""},{"q":"site:gogogolems.substack.com/p \"Agents\" \"Manuel Odendahl\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Refining the article**

I’m identifying the strongest themes and checking technical precision. I’ll emphasize category theory as a communication framework, while noting that functors, natural transformations, composition, and model mechanisms shouldn’t be conflated.

**Refined the article**

**Shaping article ideas**

I’m separating the concepts so they don’t repeat earlier representation arguments. My strongest options are a personal “math without numbers” essay, an experiment-driven prompt piece, and a practical category-theory guide.

**Shaped article ideas**

**Searched 1 website**

</details>

There is also a useful split between what is publishable now and what needs evidence. The practical claim can be demonstrated with code and repeated generations; the latent-space/category-theory claim should remain explicitly metaphorical unless you add research support.

```json
{"system1_search_query":[{"q":"site:math.jhu.edu riehl category theory in context pdf functor natural transformation"},{"q":"site:math.mit.edu category theory functor natural transformation lecture notes pdf"},{"q":"site:arxiv.org transformer representations abstractions language models latent space compositional structure"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

## Editorial diagnosis

This transcript contains **at least three articles**. Trying to preserve every thread would produce a long essay whose real argument appears too late.

Your published pieces usually begin with something concrete—the sticky-header request, an agent diary excerpt, a single ambiguous word—then widen into a claim about programming with models. They often return to the original example for the conclusion. citeturn667691view1turn667691view2turn667691view4

That suggests one major change: **do not open this article with category theory or your mathematical history. Open with two pieces of code.**

There is also some overlap with your existing argument. “Simplicity” already says that a prompt becomes easy when it maps closely to a suitable formal notation, while “Slowing Down” identifies choosing the right notation as part of the remaining human work. citeturn729296search0turn729296search1

The new contribution should therefore be:

> **Abstract mathematics is a catalog of named structures. Knowing those names lets you give an LLM a smaller, more constrained transformation to perform.**

That is sharper than “LLMs and category theory are deeply connected.”

# Recommended two-part series

## 1. The Right Abstraction Is a Better Prompt

**Possible subtitle:** *Abstract mathematics as a compression format for programming with LLMs*

This is the strongest article already present in the recording.

### Central claim

LLMs are often capable of producing the right program, but natural-language requests leave them to infer both the structure of the problem and its implementation. Naming the mathematical structure removes one of those jobs.

### Opening

Show an ugly but recognizable program:

```ts
const formatted = [];

for (const price of prices) {
  const taxed = addTax(price);
  const converted = convertCurrency(taxed);
  const rounded = roundPrice(converted);
  const display = formatPrice(rounded);
  formatted.push(display);
}
```

Then compare two prompts:

> Simplify this code.

versus:

> This is a sequence of pure transformations over the same collection. Compose the transformations and map the resulting function over the collection once.

The second prompt might produce:

```ts
const toDisplayPrice = flow(
  addTax,
  convertCurrency,
  roundPrice,
  formatPrice,
);

const formatted = prices.map(toDisplayPrice);
```

Then give the thesis in your usual blunt form:

> Same model. Same code. The difference was not intelligence. It was that I finally told the model what shape the problem had.

### Suggested structure

#### 1. I was terrible at math

Briefly establish the remedial classes, statistics/calculus failure, and attraction to compilers, proof systems, and model checking.

Keep this to perhaps four paragraphs. It explains why your understanding of mathematics is structural rather than numerical, but it should not delay the demonstration.

#### 2. Math is a vocabulary for shapes

Introduce abstract mathematics as the naming of structures that recur in otherwise unrelated domains.

Avoid explaining category theory in full. The reader only needs:

- A structure has operations.
- The operations obey certain laws.
- Once you recognize the structure, you inherit a collection of valid transformations and tests.

A strong line might be:

> The useful part of abstract math is not that it makes ordinary things sound incomprehensible. It is that one incomprehensible word can replace fifteen paragraphs of almost-English.

#### 3. The model otherwise has to discover the abstraction

Compare the transformations required by the two prompts.

The vague prompt requires something like:

```text
code
→ intended behavior
→ repeated structural pattern
→ possible abstraction
→ suitable programming notation
→ new code
```

The structure-aware prompt is closer to:

```text
map composition
→ code expressing map composition
```

This is the core of the article.

#### 4. A functor, reluctantly explained

Use one narrow programming example. Arrays, optional values, and promises are better than list-to-tree conversion because they demonstrate the same operation while preserving each container’s shape:

```ts
prices.map(formatPrice)
maybePrice.map(formatPrice)
pricePromise.then(formatPrice)
```

The useful intuition:

> I have a function from `Price` to `DisplayPrice`. The surrounding structure knows how to lift that function so I do not have to manually unpack and rebuild everything.

Then move on. Do not make the reader pass a category-theory exam.

#### 5. Mathematical words constrain generations

Connect this to your existing “every word is load-bearing” argument.

A word such as `diary` pulls a large, culturally stable pattern from training. A mathematical term can do something similar, but with stricter expectations: `idempotent`, `monoid`, `state machine`, `fixed point`, `partial order`, `parser combinator`.

The distinction is useful:

> Ordinary words summon examples. Mathematical words summon examples plus laws.

#### 6. Show the experiment

This section would make the essay much stronger than the transcript.

For three small tasks, compare:

1. A normal request.
2. A request naming the structure.
3. Several regenerations of each.
4. Possibly a smaller model.

Measure practical things rather than claiming formal proof:

- How many unrelated architectures appear?
- How many files or lines are produced?
- Does the model preserve the required invariants?
- How much correction is needed?
- How much output variance is there?

That connects directly to your spray-test approach.

#### 7. The laws become tests

Show how recognizing a structure produces validation criteria.

Examples:

- Serialization followed by deserialization should round-trip.
- Normalization should be idempotent.
- Combining with an identity value should change nothing.
- Mapping an identity function should preserve the container.
- Two transformations composed first should behave like mapping them successively.

This is where the article becomes more than a prompting trick. The abstraction helps generate the code **and** supplies ways to reject bad code.

#### 8. End on notation, not category theory

Return to the initial loop.

A suitable concluding claim:

> I am not learning abstract math because I expect to prove theorems while writing CRUD applications. I am learning it because programming with an LLM is largely the work of finding a representation in which the next transformation becomes obvious—even to a tired machine, and even to a tired me.

---

## 2. I Failed Calculus. LLMs Taught Me Math Anyway

**Alternative title:** *Math Without Numbers*

**Possible subtitle:** *Using language models to climb between examples, code, notation, and proofs*

The recording promises this article, but does not yet contain enough practical detail for it. It needs your actual learning workflow.

### Central claim

Traditional mathematical teaching repeatedly left you stranded at one level of abstraction. An LLM lets you move between levels until one representation clicks.

### Suggested opening

Start with the contradiction:

> I had remedial math in school and dropped out of university partly because I could not pass statistics and calculus. Twenty years later, I spend my mornings learning category theory for fun.

Then immediately add the complication:

> The suspicious part is that my tutor is a machine famous for confidently inventing mathematics.

### Suggested structure

#### 1. The math I could not do

Brief personal history. Distinguish calculation-heavy classroom math from your attraction to formal systems and relationships.

#### 2. The abstraction ladder

Show one concept at several levels:

```text
Concrete data
→ code
→ type signature
→ algebraic structure
→ laws
→ proof
```

For example:

```text
joining strings
→ concatenate(a, b)
→ String × String → String
→ associative binary operation with an identity
→ monoid
```

#### 3. How I interrogate a concept

Give exact prompts from a real learning session:

- “Give me three programming examples and one non-programming example.”
- “Now give me something that almost fits but violates one law.”
- “Translate the notation into TypeScript.”
- “Do not solve the exercise; identify the first unjustified step.”
- “Generate a finite counterexample.”
- “Explain which parts are analogy and which parts are definition.”

#### 4. Counterexamples are more useful than explanations

LLMs are particularly useful for rapidly generating candidate examples, near-misses, diagrams, and alternate representations.

But present the model as a **translation and exercise interface**, not an authority. Keep a textbook, formal reference, proof assistant, or executable test as the source of truth.

#### 5. From abstract back to concrete

Demonstrate how a concept changed an actual API, refactor, test suite, or prompt.

Without this section, the piece risks becoming a generic “AI tutor” article.

#### 6. What I can now see

Describe the practical result as pattern recognition:

- duplicated traversal,
- accidental state machines,
- missing identity elements,
- operations that should be idempotent,
- representations that prevent composition,
- API names that conceal the underlying operation.

#### 7. Learning the machine while learning math

Your final turn can be that the process is reciprocal: asking the LLM to translate a concept reveals how strongly its behavior depends on notation and representation.

Possible closer:

> The model did not make me good at calculation. It gave me a way to keep changing the representation until the calculation stopped being the interesting part.

# Strong single-article version

To ship one article instead of a series, use:

## Category Theory for People Who Prompt Computers

**Subtitle:** *Why naming the shape of a problem changes what an LLM can do with it*

Structure:

1. Two prompts, two implementations.
2. Your history with math.
3. Abstract math as named, lawful structure.
4. One functor example.
5. The abstraction ladder.
6. Three before-and-after prompts.
7. Laws as generated tests.
8. What this does **not** prove about model internals.
9. Return to the initial example.

Keep the teaching material subordinate to the programming argument. The article is not “an introduction to category theory”; it is “why one small piece of category theory changed how I communicate with models.”

# Additional articles hiding in the transcript

## The Stochastic Parrot Is the Point

**Thesis:** People use “stochastic parrot” as a dismissal, but fuzzy statistical recombination is precisely what allows the machine to move between imperfect human representations.

Suggested progression:

1. Markdown template plus messy transcript.
2. Why literal deterministic transformations would be less useful.
3. Fuzziness as both power and source of failure.
4. Programming also contains a pragmatic gap between formal laws and shippable systems.
5. Engineering consists of controlling where fuzziness is acceptable.
6. Conclusion: parroting became interesting when the parrot learned transformations.

This is provocative and likely readable, but should avoid claiming that stochasticity itself explains abstraction.

## Mathematical Words Are Tiny Programs

**Thesis:** Certain words do a disproportionate amount of prompting work because they imply operations, constraints, and laws.

Use a sequence of mini-case studies:

- diary,
- state machine,
- idempotent,
- monoid,
- fixed point,
- event log,
- parser,
- reducer.

For each, show what the model produces before and after the word is introduced.

This would connect cleanly to both the diary article and “every word is load-bearing.”

## The Abstraction Budget

**Thesis:** Every agent task contains a limited number of representational leaps that a model can perform reliably. Good prompting spends that budget deliberately.

A task might require translating:

```text
user complaint
→ product behavior
→ domain model
→ API
→ implementation
→ validation
```

You can ask a strong model to infer every stage, but each unstated stage introduces variance. Good architecture and notation externalize some of those transformations.

This gives you a useful term that could recur in future posts:

> The problem was not outside the model’s context window. It was outside its abstraction budget.

## Correctness Is Not the Whole Product

The transcript’s attack on mathematically pure programming is a separate essay.

**Thesis:** Formal correctness is one valuable software property among usability, timing, aesthetic quality, business fit, observability, reversibility, and the ability to learn from users.

The tension:

- Mathematical structures make software easier to compose and verify.
- Insisting that every program perfectly instantiate them can exclude useful contributors and optimize the wrong property.
- LLMs make it easier to translate between informal product judgment and formal implementation.
- The goal is not to turn every programmer into a Haskell programmer; it is to make mathematical leverage available without demanding mathematical identity.

This essay needs care because “correctness is a tiny part” is too broad. A safer argument is that correctness is necessary but radically incomplete.

# What I would cut from the first article

### The latent-space theory

Keep it to one explicitly speculative paragraph. There is evidence that transformers can develop abstract or concept-like representations, but findings are task- and model-dependent, and other work finds fragmented rather than cleanly unified compositional representations. That does not currently justify saying the model has an internal category-theory object corresponding to your abstraction. citeturn383380academia30turn383380academia32turn383380academia33

A good formulation would be:

> I do not know whether the model represents any of this in a way that resembles category theory internally. I am making a claim about the interface: category-theoretic language often gives the model a useful and compact description of the transformation I want.

### The image-to-webpage example

It expands the question from programming technique into machine-learning interpretation. Save it for “The Stochastic Parrot Is the Point.”

### The extended Haskell-versus-Go discussion

One joke or paragraph is enough. Otherwise the article risks becoming a programming-language culture-war piece.

### The argument about correctness

It is interesting but interrupts the main chain:

```text
mathematical vocabulary
→ constrained prompt
→ clearer implementation
→ inherited laws and tests
```

Move it into its own essay.

# Technical guardrails

A few phrases from the recording should be tightened before publication:

- A category is not merely a collection of arbitrary relationships. It includes objects, morphisms, identity morphisms, and an associative composition operation. Category theory is indeed used as a language for comparing structures across mathematical contexts, but the formal requirements matter. citeturn383380search3
- A list can be treated as a functor; `map` is the operation by which that functor acts on functions. Saying “map is a functor” collapses the distinction.
- Converting a list to a tree is not automatically “transforming one functor into another.” It is a function between data structures. Calling it a natural transformation requires additional conditions.
- A type is not generally a monoid. A set or type equipped with an associative binary operation and identity may form one.
- Fifteen maps can often be fused by composing their pure functions, but not safely when order, mutation, asynchronous behavior, exceptions, short-circuiting, or intermediate materialization are semantically important.
- Replace “LLMs think linearly” with “LLMs generate autoregressively.” The former is a useful metaphor but sounds like a mechanistic claim.

## My pick

Publish **“The Right Abstraction Is a Better Prompt”** first. It advances the arguments already on the blog, gives readers something immediately usable, and provides a natural reason to introduce abstract mathematics without asking them to accept a speculative theory of model internals.

Then publish **“I Failed Calculus. LLMs Taught Me Math Anyway”** once you have captured one complete learning session with the prompts, mistakes, counterexamples, source material, and the concrete programming result.


---

> Write out both articles, using my voice, and output as markdown. Also write a third document (which actually kind of has to be written first / during the main article writing) which is your internal though process and editing process while you write the articles, and it should include original citations and references and also some research you did and experiments potentially you write to validate the ideas of the articles, etc... Citing the original transcript parts will help you stay grounded in my style of "writing" and thinking, but do use the clear structures above, geared towards developers who are working with LLMs, but also a slightly broader audience of technically minded people.

I’ll produce three Markdown files: two finished essays and a research/editing notebook. The notebook will document decisions, source checks, experiments, and revisions without exposing hidden private reasoning.

<details><summary>💭 Thinking</summary>

**Refining article concepts**

I’m separating overlapping ideas and checking technical precision. The strongest directions are a personal “math without numbers” essay, an experiment-driven piece, and a practical category-theory guide emphasizing communication without conflating mathematical concepts with model mechanisms.

**Refined article concepts**

</details>

```json
{"system1_search_query":[{"q":"site:gogogolems.substack.com/p programming LLMs abstraction notation simplicity prompt engineering"},{"q":"site:gogogolems.substack.com/p \"Simplicity in the Age of AI-Assisted\""},{"q":"site:gogolems.substack.com/p \"Slowing Down\" LLM programming"},{"q":"site:gogogolems.substack.com/p diary agent LLM"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

The source checks support a narrow claim: category-theoretic vocabulary can describe transformations and laws compactly. They do not support treating category theory as a literal account of an LLM’s internal representations, so that remains clearly marked speculation.

```unknown
from pathlib import Path
from textwrap import dedent

out = Path("/mnt/data")
out.mkdir(exist_ok=True)

article1 = dedent(r'''
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
''').strip() + "\n"

article2 = dedent(r'''
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
''').strip() + "\n"

notebook = dedent(r'''
# Research and Editing Notebook

## For “The Right Abstraction Is a Better Prompt” and “I Failed Calculus. LLMs Taught Me Math Anyway”

> This document is an editorial and research record, not a transcript of hidden chain-of-thought. It records the source material, explicit decisions, checks, discarded directions, validation work and remaining uncertainties used to produce the two essays.

## 1. Source thesis inventory

The original voice recording contains several separate claims. The first editing task was to separate them rather than force all of them into one article.

### Claim A: personal relationship with mathematics

Original transcript:

> “Math has always been something I really, really struggle with. I had remedial math at school, and I dropped out of university because I couldn't do statistics and calculus.”

And:

> “I’ve also like read a lot, played a lot with compilers and proof systems and model checking and all the like more abstract part of theoretical computer science, which I had much less problems with, ’cause there weren’t really any numbers. They were just like abstract structures.”

This became the spine of the second essay. It appears in the first essay only long enough to establish why the author approaches mathematics structurally.

### Claim B: LLMs as pattern transformers

Original transcript:

> “LLMs are ultimately like pattern matchers and pattern transformers.”

And:

> “You give it, say, a markdown structure document, and then you ask it to fill it with a certain type of content, it will merge both structures.”

This remains as an interface-level observation. The essays avoid converting it into a complete mechanistic theory.

### Claim C: abstract mathematics can improve prompting

Original transcript:

> “Knowing which abstractions work well for an LLM and then just composing them make it really easy for an LLM to do a good job.”

And:

> “Abstract mathematics can lead to really, really good prompts.”

This became the central claim of the first essay, narrowed to:

> Correctly naming a structure can reduce the number of interpretive transformations required from the model and provide laws that constrain the result.

“Narrowed” matters. The recording sometimes moves from an effective prompting observation to a claim about what exists inside a model’s latent space. The article does not need that larger claim.

### Claim D: mathematical abstractions produce tests

Original transcript:

> “It has a mathematical foundation that we can now prove or add at least a couple of invariants or do like QuickCheck type of unit testing where we use the mathematical abstraction to create test cases.”

This became the bridge from prompting technique to engineering practice. It prevents the first article from being merely “use fancy words in prompts.”

### Claim E: fuzzy systems are useful

Original transcript:

> “Calling an LLM a stochastic parrot is, like, kind of a bad thing because it actually shows how amazing it is to stochastically model something…”

This is strong material but belongs in a separate article. Including it would require a larger discussion of stochastic generation, representation learning and the limits of the “parrot” metaphor.

### Claim F: correctness is only one software value

Original transcript:

> “There’s so many capabilities that go into making good software. Being correct, being just, like, a tiny part of it.”

This was removed from both essays. The intuitive point is valuable: formal elegance and product value are not identical. The exact wording is too broad. Correctness is not “tiny” in safety-critical, financial or infrastructural systems. A future article could argue that correctness is necessary but insufficient.

## 2. Voice observations from existing posts

The drafts were shaped against several characteristics of the existing blog.

### Concrete object first

“Simplicity in the age of AI-assisted coding” opens with a sticky-header request and follows it through multiple representations. The argument emerges from the object instead of beginning with a framework.

Applied decision: Article 1 opens with a loop and two prompts. Article 2 opens with the contradiction between failing calculus and studying category theory.

Reference:

- Manuel Odendahl, [“Simplicity in the age of AI-assisted coding”](https://gogogolems.substack.com/p/simplicity-in-the-age-of-ai-assisted)

### Personal admission as an argumentative tool

The posts often use personal limitations—difficulty with CSS, memory for code, anxiety around probabilistic systems—not as memoir for its own sake but to explain why a workflow evolved.

Applied decision: “I failed calculus” is not inspirational framing. It explains why the abstraction ladder and translation workflow matter.

Reference:

- Manuel Odendahl, [“Slowing Down in the Age of Coding Agents”](https://gogogolems.substack.com/p/slowing-down-in-the-age-of-coding)

### Recurring concern with vocabulary

“Slowing Down” treats words in prompts and generated designs as load-bearing architectural choices. “Why I Make My Agents Keep Diaries” shows how one ordinary word—*diary*—pulls a useful narrative structure from the model.

Applied decision: Article 1 includes the line “Ordinary words summon examples. Mathematical words summon examples plus laws.”

References:

- Manuel Odendahl, [“Slowing Down in the Age of Coding Agents”](https://gogogolems.substack.com/p/slowing-down-in-the-age-of-coding)
- Manuel Odendahl, [“Why I Make My Agents Keep Diaries”](https://gogogolems.substack.com/p/why-i-make-my-agents-keep-diaries)

### Engineering through replayable failures

“From prompt and pray to prompt engineering” argues for preserving failures as benchmarks rather than evaluating models on vibes.

Applied decision: Article 1 proposes a repeated-sampling experiment instead of presenting a one-off successful prompt as proof.

Reference:

- Manuel Odendahl, [“From ‘prompt and pray’ to prompt engineering”](https://gogogolems.substack.com/p/from-prompt-and-pray-to-prompt-engineering)

### Controlled profanity and jokes

The transcript contains several good pressure-release lines, especially around Haskell vocabulary and “fuck around” programming. The finished drafts retain the irreverence but reduce repetition and filler. The jokes occur after technical density rather than replacing technical detail.

## 3. Structural decisions

### Why the transcript became two essays

A single draft would need to carry all of these:

1. personal history with mathematics,
2. an explanation of category theory,
3. a theory of model representations,
4. a prompting technique,
5. a functional-programming example,
6. property-based testing,
7. an AI tutoring workflow,
8. caveats about hallucinated mathematics.

That creates two unrelated reader promises:

- “Here is a useful way to program with LLMs.”
- “Here is how I learned abstract math with an LLM.”

The first essay now answers the first promise. The second answers the second.

### Why Article 1 begins with code

The most defensible claim is practical and demonstrable. Beginning with latent space would make the reader accept speculative premises before receiving value.

The loop/map example also mirrors the blog’s established method: concrete representation → alternate representation → broader claim → return to concrete example.

### Why Article 2 begins with failure

The learning essay requires stakes. “How to use an LLM as a math tutor” is generic. “I failed the conventional interface to math, then found a representation-switching interface that matched how I think” is specific.

### Why category theory is only partially introduced

A precise introduction to categories, functors and natural transformations could consume the entire article. The drafts give only the formal distinctions necessary to avoid obvious misuse.

The key source used for calibration was Emily Riehl’s *Category Theory in Context*, which presents category theory as a language for mathematical analogy and emphasizes studying mathematical objects through morphisms and constructions.

Reference:

- Emily Riehl, [*Category Theory in Context*](https://math.jhu.edu/~eriehl/context/)

## 4. Technical corrections made from the transcript

### “Map is called a functor”

Transcript tendency:

> “Map often being called a functor…”

Correction:

A functor is the structure/mapping between categories; in programming, a `Functor` type constructor supports an `fmap`/`map` operation satisfying identity and composition laws. `map` is not itself the functor.

References:

- [HaskellWiki: Functor](https://www.haskell.org/haskellwiki/Functor)
- Paulo Vasconcelos, [“Functors and Applicatives”](https://www.dcc.fc.up.pt/~pbv/aulas/tapf/handouts/applicative.html)

### “List to tree is a natural transformation”

Transcript tendency:

> “List of a type T can be transformed to a tree of type T…”

A function from `List<T>` to `Tree<T>` is not automatically a natural transformation. To call a family of such functions natural, it must commute with the relevant mappings for every function between element types.

This detail was kept mostly out of the main essays. It appears as a warning that LLMs will confidently validate category-theoretic terminology.

### “A type is a monoid”

Correction:

A bare type is not generally a monoid. A type/set together with a selected associative binary operation and identity may form a monoid. A given type can support multiple monoid structures—for example, integers under addition and integers under multiplication.

### “Fifteen maps can always become one”

Correction:

Pure sequential maps can be fused by function composition in many settings:

```text
map(g, map(f, xs)) = map(g ∘ f, xs)
```

But operational equivalence can fail or become complicated when there are side effects, exceptions, asynchronous boundaries, laziness/strictness differences, short-circuiting, mutation, resource constraints or intentional intermediate materialization.

The article therefore uses a deliberately pure example and states the limits.

### “LLMs think linearly”

Correction:

The precise claim is that common LLMs generate autoregressively, one token after another, while using representations computed from the context. “Think linearly” is an anthropomorphic metaphor and was not used as a factual mechanism.

## 5. Research notes

### Category theory as a language for recurring structure

Riehl describes category theory as a mathematical language deployable across mathematical contexts and as a way to formalize analogy. This supports the article’s use of category theory as a vocabulary for shapes, but not the stronger claim that every programming abstraction should be expressed categorically.

Source:

- Emily Riehl, [*Category Theory in Context*](https://math.jhu.edu/~eriehl/context/)

### Functor laws

The programming account relies on two standard laws:

```text
fmap id = id
fmap (g ∘ f) = fmap g ∘ fmap f
```

They justify the article’s claim that the abstraction supplies testable properties rather than only terminology.

Sources:

- [HaskellWiki: Functor](https://www.haskell.org/haskellwiki/Functor)
- [Haskell Wikibook: The Functor class](https://en.wikibooks.org/wiki/Haskell/The_Functor_class)

### Property-based testing

QuickCheck introduced a practical method where programmers formulate properties as executable functions and test them against generated inputs. Modern descriptions characterize property-based tests as executable specifications checked over many generated cases.

This supports the transition from algebraic laws to generated tests.

Sources:

- Koen Claessen and John Hughes, [“QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs”](https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf)
- Harrison Goldstein et al., [“Property-Based Testing in Practice”](https://harrisongoldste.in/papers/icse24-pbt-in-practice.pdf)

### Abstract and compositional representations in neural models

The transcript speculates that an LLM may contain a common latent representation corresponding to abstractions shared across domains.

Relevant research provides partial reasons for interest but not confirmation of that specific picture:

- Work on compositional generalization studies whether learned primitives can be recombined in novel tasks.
- Some studies find abstract representations that support generalization in artificial neural networks.
- Recent work reports shared feature directions for grammatical concepts across languages in particular models.
- Surveys emphasize that compositional generalization remains an open and inconsistently defined challenge.
- A 2026 position/design paper argues that current LLM concepts are implicit and distributed rather than explicit, stable symbolic components.

Sources:

- Takuya Ito et al., [“Compositional generalization through abstract representations in human and artificial neural networks”](https://arxiv.org/abs/2209.07431)
- Sania Sinha, Tanawan Premsri, and Parisa Kordjamshidi, [“A Survey on Compositional Learning of AI Models”](https://arxiv.org/abs/2406.08787)
- Jannik Brinkmann et al., [“Large Language Models Share Representations of Latent Grammatical Concepts Across Typologically Diverse Languages”](https://arxiv.org/abs/2501.06346)
- [“Concepts as a Design Axis for Large Language Models”](https://arxiv.org/html/2607.26825v2)

Editorial conclusion:

The essays say that models can act as powerful translators between representations and that mathematical vocabulary can constrain the interface. They do **not** claim that a model internally implements category theory.

## 6. Validation experiment performed

A local deterministic check was used for the loop-versus-map example.

### Functions

```python
def add_tax(x):
    return x * 1.2

def convert(x):
    return x * 0.92

def round_price(x):
    return round(x, 2)

def format_price(x):
    return f"${x:.2f}"
```

### Implementations

```python
def loop_version(prices):
    out = []
    for price in prices:
        out.append(format_price(round_price(convert(add_tax(price)))))
    return out

def map_version(prices):
    def to_display(x):
        return format_price(round_price(convert(add_tax(x))))
    return list(map(to_display, prices))
```

### Input generation

10,000 randomly generated finite lists were tested. List lengths ranged from 0 to 100. Values were finite floating-point numbers sampled from a bounded interval.

### Result

The implementations returned identical lists for every generated case.

### What this validates

It validates only the semantic equivalence of the two implementations under the selected pure functions and generated domain.

### What it does not validate

It does not show:

- that composed-map code is always more readable,
- that it is always faster,
- that arbitrary loops can be rewritten this way,
- or that an LLM is more likely to produce it when given mathematical vocabulary.

Those require separate experiments.

## 7. Proposed LLM experiment

No claim of having run this model experiment is made. The following is a protocol suitable for turning the article’s main intuition into evidence.

### Tasks

Create 12 small refactoring tasks representing:

- map/functor-like element transformations,
- folds over monoidal accumulators,
- idempotent normalization,
- finite-state workflows,
- parser composition,
- round-trip encoders/decoders.

### Prompt conditions

For each task:

**Condition A: vague**

> Refactor this code to be simpler and more robust.

**Condition B: descriptive**

> Identify repeated behavior, extract it, reduce duplication and preserve semantics.

**Condition C: structural**

> Treat this as a pure map over the collection. Compose the element transformations and preserve the collection shape.

The structural prompt changes according to the task.

### Sampling

- At least three model families.
- A large and small model from each family where possible.
- 20 independent samples per task and condition.
- Fixed temperature and tool configuration.
- Fresh context for each run.

### Measurements

1. Functional correctness against hidden tests.
2. Property-law compliance.
3. Number of new named concepts introduced.
4. Diff size.
5. Output token count.
6. Architectural variance across samples.
7. Human-rated clarity.
8. Number of follow-up turns required to obtain an acceptable result.
9. Whether the model blindly follows an intentionally incorrect structural label.

The final measurement is critical. A vocabulary-aware model may become *more* confidently wrong when the human misidentifies the abstraction.

### Hypothesis

Where the named abstraction is correct and familiar in the training distribution, Condition C should reduce architectural variance and follow-up correction cost.

A good result would not need to show universal improvement. It would identify the task classes where structural vocabulary helps and the classes where it becomes jargon or misdirection.

## 8. Editing changes by article

### Article 1

Removed:

- extended discussion of image-to-webpage generation,
- a broad defense of the “stochastic parrot” label,
- the Go-versus-Haskell culture-war thread,
- the claim that correctness is a tiny part of software,
- natural-transformation details that would derail the argument.

Added:

- an opening code example,
- the “abstraction budget” working concept,
- a clean separation between interface claim and model-internals speculation,
- explicit property-law examples,
- an experiment proposal.

### Article 2

Added material not present in detail in the transcript:

- a concrete tutoring workflow,
- prompts for counterexamples and near-misses,
- the “one rung at a time” rule,
- external verification practices,
- a monoidal report-merging example,
- limitations of LLM tutoring.

These additions were inferred from the author’s published workflow: slow review, vocabulary tracking, external artifacts, replayable failures and using models as structured collaborators rather than unquestioned authorities.

## 9. Phrases retained or transformed from the recording

### Retained conceptually

Original:

> “Math with no numbers.”

Draft:

> “They are just often mathematics with fewer numbers.”

Original:

> “Go back and forth the ladder of abstraction.”

Draft:

> “I use them to move,” followed by the abstraction ladder.

Original:

> “It’s almost disappearing.”

Draft:

> “Once I can move back and forth between the two, the abstraction almost disappears.”

Original:

> “Arabic numerals and algebraic notations kind of allow us to solve…”

Transformed into the broader idea that notation is compression and that the learner needs a decompressor. The quadratic-equation example was removed because the transcript itself expresses uncertainty about the terminology.

Original:

> “This is just vibes because I am not actually a machine learning LLM expert.”

Draft:

> “I do not know that it is true,” followed by a boundary around the claim.

The revised sentence keeps the epistemic honesty while avoiding using “vibes” as a substitute for identifying exactly what is unknown.

## 10. Remaining editorial questions

### Should Article 1 use “category theory” in the title?

Current title avoids it. This likely reaches the broader technical audience and allows category theory to arrive as a tool rather than a gatekeeping signal.

A more provocative alternate title:

> **Category Theory for People Who Prompt Computers**

This is stronger for an audience already interested in the topic, but it promises more category theory than the current article teaches.

### Should the TypeScript examples use a real `flow` implementation?

The current example treats `flow` as familiar pseudocode. Publication options:

- import `flow` from a specific library,
- define a tiny typed helper,
- or avoid it and use a named function with direct nesting.

Defining a helper would increase technical completeness but distract from the representational point.

### Should the essays include citations inline?

The blog’s current style is light on academic apparatus. Recommended publication treatment:

- Link the first mention of Riehl’s book.
- Link QuickCheck/property-based testing.
- Put model-representation research in a compact “Notes” section.
- Keep the main prose uncluttered.

### Does the LLM-learning essay need a complete session transcript?

Yes, eventually. The finished article is structurally complete, but its strongest future revision would replace one invented/generalized workflow sequence with a real annotated session:

1. the original confusion,
2. exact prompts,
3. a wrong model answer,
4. the source check,
5. the counterexample,
6. the corrected understanding,
7. the programming application.

That would make the method replayable and align it with the blog’s benchmark/diary ethos.

## 11. Reference list

### Author’s blog

- Manuel Odendahl. [“Simplicity in the age of AI-assisted coding.”](https://gogogolems.substack.com/p/simplicity-in-the-age-of-ai-assisted)
- Manuel Odendahl. [“Slowing Down in the Age of Coding Agents.”](https://gogogolems.substack.com/p/slowing-down-in-the-age-of-coding)
- Manuel Odendahl. [“Why I Make My Agents Keep Diaries.”](https://gogogolems.substack.com/p/why-i-make-my-agents-keep-diaries)
- Manuel Odendahl. [“From ‘prompt and pray’ to prompt engineering.”](https://gogogolems.substack.com/p/from-prompt-and-pray-to-prompt-engineering)

### Mathematics and testing

- Emily Riehl. [*Category Theory in Context.*](https://math.jhu.edu/~eriehl/context/)
- [HaskellWiki: “Functor.”](https://www.haskell.org/haskellwiki/Functor)
- Paulo Vasconcelos. [“Functors and Applicatives.”](https://www.dcc.fc.up.pt/~pbv/aulas/tapf/handouts/applicative.html)
- Koen Claessen and John Hughes. [“QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs.”](https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf)
- Harrison Goldstein et al. [“Property-Based Testing in Practice.”](https://harrisongoldste.in/papers/icse24-pbt-in-practice.pdf)

### Model representations and compositionality

- Takuya Ito et al. [“Compositional generalization through abstract representations in human and artificial neural networks.”](https://arxiv.org/abs/2209.07431)
- Sania Sinha, Tanawan Premsri, and Parisa Kordjamshidi. [“A Survey on Compositional Learning of AI Models.”](https://arxiv.org/abs/2406.08787)
- Jannik Brinkmann et al. [“Large Language Models Share Representations of Latent Grammatical Concepts Across Typologically Diverse Languages.”](https://arxiv.org/abs/2501.06346)
- [“Concepts as a Design Axis for Large Language Models.”](https://arxiv.org/html/2607.26825v2)
''').strip() + "\n"

# Run and record the deterministic validation mentioned in the notebook.
import random
def add_tax(x): return x * 1.2
def convert(x): return x * 0.92
def round_price(x): return round(x, 2)
def format_price(x): return f"${x:.2f}"

def loop_version(prices):
    out = []
    for price in prices:
        out.append(format_price(round_price(convert(add_tax(price)))))
    return out

def map_version(prices):
    def to_display(x):
        return format_price(round_price(convert(add_tax(x))))
    return list(map(to_display, prices))

rng = random.Random(20260802)
for i in range(10_000):
    xs = [rng.uniform(-1_000_000, 1_000_000) for _ in range(rng.randint(0, 100))]
    assert loop_version(xs) == map_version(xs), (i, xs)

files = {
    "01-the-right-abstraction-is-a-better-prompt.md": article1,
    "02-i-failed-calculus-llms-taught-me-math-anyway.md": article2,
    "03-research-and-editing-notebook.md": notebook,
}
for name, text in files.items():
    (out / name).write_text(text, encoding="utf-8")

[(name, len(text.split()), (out/name).stat().st_size) for name, text in files.items()]

```

Completed three Markdown documents. The research notebook includes transcript excerpts, editorial decisions, technical corrections, source references, a deterministic 10,000-case equivalence check, and a proposed multi-model experiment. It documents the process without presenting hidden chain-of-thought.

1. [The Right Abstraction Is a Better Prompt](sandbox:/mnt/data/01-the-right-abstraction-is-a-better-prompt.md)  
   A practical argument that mathematical structures compress prompts, reduce interpretive variance, and provide laws for validating generated code.

2. [I Failed Calculus. LLMs Taught Me Math Anyway](sandbox:/mnt/data/02-i-failed-calculus-llms-taught-me-math-anyway.md)  
   A personal article about using LLMs to move between concrete examples, code, notation, counterexamples, laws, and proofs.

3. [Research and Editing Notebook](sandbox:/mnt/data/03-research-and-editing-notebook.md)  
   Source inventory, voice analysis, structural decisions, transcript grounding, research references, corrections around functors and monoids, experiment results, proposed LLM benchmark, and unresolved editorial questions.

The category-theory definitions were checked against Emily Riehl’s *Category Theory in Context*, while the testing discussion draws on the original QuickCheck paper and later property-based-testing research. citeturn958611search0turn958611search2turn958611search22 The voice and article architecture were informed by your posts on simplicity, slower agent-assisted development, agent diaries, and replayable prompting failures. citeturn807028search0turn807028search1turn807028search2turn807028search3

