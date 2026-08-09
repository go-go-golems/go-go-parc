# Answering Interview Questions

- URL: https://chatgpt.com/c/6a6f7b8e-19d0-83ea-96fc-fb240d35f0d3
- Created: 2026-08-02T17:17:27.674Z

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

```json
{"search_query":[{"q":"site:gogogolems.substack.com gogogolems programming LLMs"},{"q":"site:gogogolems.substack.com/p \"Simplicity\" \"AI-assisted\""},{"q":"site:gogogolems.substack.com/p \"Slowing Down\" LLM programming"},{"q":"site:gogogolems.substack.com/p \"every word is load-bearing\""}],"response_length":"long"}
```

I’ll produce two polished Markdown essays plus an editorial research log documenting sources, experiments, claim checks, revisions, and discarded approaches—not private chain-of-thought.

<details><summary>💭 Thinking</summary>

**Planning article research**

I’m outlining an article arguing that abstract mathematical vocabulary can make prompts more precise. I’ll support it with accurate examples, verified code experiments, and research rather than claiming unsupported language-model results.

**Planned article research**

**Refining documentation plans**

I’m shaping the article around the supplied transcript, paraphrasing rather than reproducing it. I’ll include citations and references in the document, while keeping the final response focused on the completed artifacts.

**Refined documentation plans**

**Researching supporting evidence**

I’m looking for research on structured prompting, formal specifications, mathematical reasoning, and learning with language models. I’ll distinguish established findings from my article’s practical hypothesis, avoiding overconfident claims.

**Researched supporting evidence**

</details>

```json
{"search_query":[{"q":"site:gogogolems.substack.com/p/ \"GO GO GOLEMS\" \"LLM\" Manuel Odendahl"},{"q":"site:gogolems.substack.com Manuel Odendahl"},{"q":"site:gogogolems.substack.com/p \"generalization shaping\""},{"q":"site:gogogolems.substack.com/p \"notation\" \"LLM\" \"Manuel Odendahl\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```json
{"search_query":[{"q":"Emily Riehl Category Theory in Context category definition functor PDF"},{"q":"Haskell Data.Functor functor laws official documentation"},{"q":"Haskell Data.Monoid monoid laws official documentation"},{"q":"QuickCheck original paper property based testing PDF Claessen Hughes"}],"response_length":"long"}
```

The split is holding: article one emphasizes abstraction, vocabulary, and verification; article two covers the learning workflow. I’m validating code and tightening category-theory claims.

<details><summary>💭 Thinking</summary>

**Planning the article set**

I’m preparing two publishable Markdown articles and a separate editorial notebook. The notebook will document sources, claim checks, experiments, and revisions without exposing private internal reasoning.

**Planned the article set**

</details>

```json
{"search_query":[{"q":"site:science.org generative AI tutor randomized controlled trial learning 2025 Kestin"},{"q":"site:nber.org Tutor CoPilot randomized trial generative AI tutoring paper"},{"q":"site:arxiv.org large language models mathematics tutoring hallucination verification study primary paper"},{"q":"site:acm.org large language model math education tutoring randomized controlled trial"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 29 websites**

</details>

```json
{"search_query":[{"q":"site:arxiv.org large language model code generation type constraints type information improves accuracy"},{"q":"site:dl.acm.org LLM code generation type constraints programming languages paper"},{"q":"site:aclanthology.org code generation type signatures language models"},{"q":"site:arxiv.org grammar constrained decoding code generation large language models formal constraints"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 4 websites**

</details>

```unknown
bash -lc mkdir -p /mnt/data/llms-abstract-math && cat > /mnt/data/llms-abstract-math/property_experiments.mjs <<'EOF'
import assert from 'node:assert/strict';

// Deterministic pseudo-random generator for reproducible checks.
function mulberry32(seed) {
  return function () {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const random = mulberry32(0x0cb27c2c);
const randomInt = (min, max) => Math.floor(random() * (max - min + 1)) + min;
const randomArray = () => Array.from({ length: randomInt(0, 24) }, () => randomInt(-1000, 1000));
const randomString = () => Array.from(
  { length: randomInt(0, 20) },
  () => String.fromCharCode(randomInt(97, 122)),
).join('');

const identity = x => x;
const f = x => x * 3 - 2;
const g = x => `v:${x}`;

let arrayCases = 0;
let monoidCases = 0;
let idempotenceCases = 0;

for (let i = 0; i < 10_000; i += 1) {
  const xs = randomArray();

  // Functor identity: map(identity) = identity.
  assert.deepEqual(xs.map(identity), xs);

  // Functor composition: map(g ∘ f) = map(f) followed by map(g).
  assert.deepEqual(xs.map(x => g(f(x))), xs.map(f).map(g));
  arrayCases += 1;

  // String concatenation as a monoid.
  const a = randomString();
  const b = randomString();
  const c = randomString();
  assert.equal(a + '', a);       // right identity
  assert.equal('' + a, a);       // left identity
  assert.equal(a + (b + c), (a + b) + c); // associativity
  monoidCases += 1;

  // A deliberately ordinary normalizer whose useful property is idempotence.
  const noisy = `  ${a.toUpperCase()}   ${b.toUpperCase()}  `;
  const normalizeTag = value => value.trim().toLowerCase().replace(/\s+/g, '-');
  assert.equal(normalizeTag(normalizeTag(noisy)), normalizeTag(noisy));
  idempotenceCases += 1;
}

// Pure map fusion preserves returned values.
const input = [1, 2, 3];
const separateValues = input.map(f).map(g);
const fusedValues = input.map(x => g(f(x)));
assert.deepEqual(fusedValues, separateValues);

// But effects expose a semantic difference in evaluation order.
const separateTrace = [];
const separateEffectful = input
  .map(x => {
    separateTrace.push(`f(${x})`);
    return f(x);
  })
  .map(x => {
    separateTrace.push(`g(${x})`);
    return g(x);
  });

const fusedTrace = [];
const fusedEffectful = input.map(x => {
  fusedTrace.push(`f(${x})`);
  const y = f(x);
  fusedTrace.push(`g(${y})`);
  return g(y);
});

assert.deepEqual(fusedEffectful, separateEffectful);
assert.notDeepEqual(fusedTrace, separateTrace);

const report = {
  seed: '0x0cb27c2c',
  arrayFunctorLawCases: arrayCases,
  stringMonoidLawCases: monoidCases,
  normalizationIdempotenceCases: idempotenceCases,
  pureMapFusionSameReturnedValues: true,
  effectfulMapFusionSameTrace: false,
  separateTrace,
  fusedTrace,
};

console.log(JSON.stringify(report, null, 2));
EOF
node /mnt/data/llms-abstract-math/property_experiments.mjs | tee /mnt/data/llms-abstract-math/property_experiments_output.json
```

<details><summary>💭 Thinking</summary>

**Ran reproducible abstract math experiments**

</details>

```json
{"search_query":[{"q":"QuickCheck original paper Claessen Hughes PDF property based testing Haskell"},{"q":"Hackage QuickCheck official documentation property testing"},{"q":"site:dl.acm.org QuickCheck lightweight tool random testing Haskell programs"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 13 websites**

</details>

```unknown
bash -lc cat > /mnt/data/llms-abstract-math/01-the-right-abstraction-is-a-better-prompt.md <<'EOF'
# The Right Abstraction Is a Better Prompt

## Abstract mathematics as a compression format for programming with LLMs

I asked a model to simplify this code:

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

This is not bad code. It is barely code. A junior programmer can read it, a senior programmer can pretend to have opinions about it, and a model can generate it while otherwise occupied with the heat death of the universe.

My first prompt was approximately:

> Simplify this code.

The model did what models do when you ask them to simplify something without saying what simplicity means. It moved a few lines around, extracted a helper, changed some variable names, and explained that the result was more readable. The code was different in the way that a hotel room is different after housekeeping has aligned the pillows.

Then I wrote:

> These are pure transformations over the same collection. Compose the transformations, give the composition a domain name, and map it over the prices once.

It produced something like this:

```ts
const toDisplayPrice = flow(
  addTax,
  convertCurrency,
  roundPrice,
  formatPrice,
);

const displayPrices = prices.map(toDisplayPrice);
```

Same model. Same code. I had not given it a clever algorithm. I had given it the shape of the problem.

That is increasingly how I think about prompting coding models. The model can usually perform a transformation once it knows which transformation it is performing. The expensive, unreliable part is often making it infer the abstraction from a pile of concrete details.

Abstract mathematics is, among other things, an absurdly compressed vocabulary for these shapes.

I am learning it because the right abstraction is often a better prompt.

## I was terrible at math

This is an inconvenient argument for me to make because I have always been terrible at math.

I had remedial math in school. I dropped out of university partly because I could not do statistics and calculus. Even now I can look at an equation, understand every symbol separately, and experience the same sensation as reading a sentence where all the words are in a language I speak but have been arranged by a hostile committee.

At the same time, I have spent years playing with compilers, type systems, proof systems, model checking, parsers, and the more formal parts of computer science. Those never felt like math to me because, as I would have said, there were no numbers.

This was obviously nonsense. There was math everywhere. I just liked the math that dealt with structures, transformations, and relationships, and disliked the math that arrived as a page of calculations I had to execute correctly under time pressure.

Category theory was the most extreme version of the former. It describes mathematical objects through the transformations between them and studies which parts of a construction survive when you move from one setting to another. A category has objects, morphisms between objects, identity morphisms, and an associative way to compose compatible morphisms.[^riehl]

That definition is precise, and the precision matters. But the intuition that first interested me was much less dignified:

> There are shapes hiding inside programs, and the same shape keeps showing up in completely different programs.

Once a shape has a name, I can point at it. Once I can point at it, I can ask a model to use it. Once I can ask a model to use it, the model no longer has to rediscover it from scratch every time.

## Math is a vocabulary for shapes

Programmers already do this constantly without calling it abstract mathematics.

We say something is a queue rather than describing an array where we usually add things at one end and remove them from the other. We say a parser rather than describing a function that consumes some input, may fail, and returns a value together with the unconsumed input. We say a state machine rather than narrating every possible sequence of booleans that happens to encode the state.

The name is not decoration. It brings operations and expectations with it.

A queue suggests enqueueing, dequeueing, and ordering. A state machine suggests states, transitions, and illegal transitions. A parser suggests sequencing, alternatives, and errors tied to positions in an input. The word compresses a small design document.

Mathematical names go one step further because many of them bring laws.

Calling an operation **idempotent** does not merely suggest a family resemblance. It asserts:

```text
f(f(x)) = f(x)
```

Calling a value and an operation a **monoid** asserts an associative combination and an identity value:

```text
combine(x, empty) = x
combine(empty, x) = x
combine(x, combine(y, z)) = combine(combine(x, y), z)
```

Calling a data type a **functor** asserts that it supports a lawful way to apply a function to values inside the structure while preserving the structure.[^functor]

These words are tiny programs. They carry APIs, transformations, and tests.

I have written before that every word in a prompt is load-bearing. Ordinary words can pull a large pattern out of the model’s training: *diary*, *compiler*, *ticket*, *postmortem*, *ledger*. Mathematical words can do the same thing, except the useful ones also tell me what must remain true.

Ordinary words summon examples. Mathematical words summon examples plus laws.

That is a very good deal for one token.

## The abstraction work has to happen somewhere

Suppose I ask a model:

> Take these prices, add tax, convert the currency, round them, and format them for display.

To produce the functional version, it has to perform a sequence of translations something like this:

```text
English description
→ intended business operation
→ recognition that each step transforms one price
→ recognition that the steps are composable
→ recognition that the same composition applies to every item
→ choice of a collection operation
→ TypeScript
```

A capable model can do this. A capable human can do this. Both also fail at it in boring ways, especially when the real prompt is three pages long and the codebase contains seven competing conventions left by people who have since changed jobs.

Now compare:

> Define a pure `Price -> DisplayPrice` composition and map it over the collection.

The translation is closer to:

```text
specified transformation
→ TypeScript notation for that transformation
```

I have removed several choices. More importantly, I have made the remaining choices inspectable.

This is similar to what notation does for humans. Arabic numerals, algebraic notation, type signatures, inference rules, diagrams, and little boxes with arrows are not just concise ways to publish an answer after somebody has understood it. They are external machinery for doing the thinking.

I can solve things on paper that I cannot solve in my head because the notation stores intermediate structure and gives me small, local rewrites to perform. I do not need to contemplate the entire equation as one spiritual object. I move a term, apply a rule, check what changed, and repeat.

LLMs generate autoregressively: they produce a sequence one token at a time, conditioned on the context and the sequence so far. That does not mean their internal computation is “linear” in the ordinary sense, but at the interface they benefit from the same kind of thing I do: a representation that makes the next transformation locally obvious.

The better the notation, the less intelligence I need at each step.

This is why I can do algebra when tired if I write everything down. It is also why a smaller model can sometimes perform surprisingly well when the prompt gives it the correct representation. I am not asking it to be insightful and syntactically correct and architecturally tasteful in one leap. I am asking it to apply a pattern that has already been selected.

## A functor, reluctantly explained

Unfortunately, I now have to explain a functor.

Not because every web application should be turned into a Haskell conference talk. Most should not. But because this is a good example of a word that sounds deliberately hostile until it is connected to ordinary code.

Suppose I have a function:

```ts
type Price = number;
type DisplayPrice = string;

const formatPrice = (price: Price): DisplayPrice =>
  `$${(price / 100).toFixed(2)}`;
```

I can apply it to one price:

```ts
const displayPrice = formatPrice(price);
```

I can also apply it to a price inside an array:

```ts
const displayPrices = prices.map(formatPrice);
```

Or inside an optional value:

```ts
type Option<T> =
  | { kind: "some"; value: T }
  | { kind: "none" };

const mapOption = <A, B>(
  option: Option<A>,
  fn: (value: A) => B,
): Option<B> =>
  option.kind === "some"
    ? { kind: "some", value: fn(option.value) }
    : option;

const displayPrice = mapOption(maybePrice, formatPrice);
```

Or inside a tree:

```ts
type Tree<T> = {
  value: T;
  children: Tree<T>[];
};

const mapTree = <A, B>(
  tree: Tree<A>,
  fn: (value: A) => B,
): Tree<B> => ({
  value: fn(tree.value),
  children: tree.children.map(child => mapTree(child, fn)),
});
```

The function changes from `Price -> DisplayPrice`. The surrounding structure stays an array, an option, or a tree.

Very roughly, that surrounding type is behaving as a functor when it provides this lawful mapping operation. `map` is not itself “a functor.” The structure with a suitable `map` is the functor, and `map` is how the functor acts on functions.

The laws are simple:

```text
map(identity) = identity
map(g ∘ f) = map(g) ∘ map(f)
```

Mapping a function that changes nothing should change nothing. Mapping two functions in sequence should agree with composing them first and mapping once.

This sounds obvious because a good abstraction often becomes invisible once connected to a concrete example. Of course mapping the identity function over an array should return the same values. Of course these two snippets should agree when `f` and `g` are pure:

```ts
const separate = values.map(f).map(g);
const fused = values.map(value => g(f(value)));
```

The useful part is not the surprise. The useful part is that the obvious thing has a name, a type, and laws I can hand to a model.

Instead of asking:

> Please refactor all of these loops and repeated null checks into something more reusable without changing behavior.

I can sometimes ask:

> The domain operation is `A -> B`. Represent the collection, optional value, and tree as lawful mappable structures, reuse the same domain function, and add tests for identity and composition.

That prompt is dramatically more specific. It tells the model what should vary, what should remain unchanged, and how to test the result.

It can also be completely wrong.

If the transformations log, mutate shared state, throw in order-dependent ways, make network calls, or rely on intermediate materialization, composing them may change observable behavior. A fancy word does not waive causality.

I ran a tiny local check while writing this. For pure functions, the separate and fused mappings returned the same values. Then I added logging. The values still matched, but the order of effects changed:

```text
separate:
f(1), f(2), f(3), g(1), g(4), g(7)

fused:
f(1), g(1), f(2), g(4), f(3), g(7)
```

The word **pure** in the prompt was load-bearing.

This is another advantage of mathematical vocabulary: it makes assumptions available for inspection. “Clean this up” hides them. “Compose these pure functions” puts one directly in the sentence where I can challenge it.

## The model loves names, including the wrong ones

There is an obvious failure mode here.

LLMs love abstractions. They have read every overexcited blog post in which somebody discovered monads and immediately redesigned a billing system. If I tell a model that my problem is a functor, it will usually find a way to agree with me. If I tell it the problem is event sourcing, hexagonal architecture, a CRDT, or a small dependent type waiting to be born, it will produce something with the confidence of a consultant billing by the diagram.

The abstraction is useful only when it buys something concrete.

For me, that means at least one of the following:

- a transformation I can reuse;
- an illegal state I can make unrepresentable;
- a law I can test;
- a composition rule I can rely on;
- a smaller interface;
- a vocabulary that matches the domain more closely than the implementation details do.

Otherwise it is just another layer.

The prompt should not be “use category theory.” The prompt should be closer to:

> Normalizing an already normalized value must not change it. Treat normalization as idempotent, keep the implementation local, and add a property test for `normalize(normalize(x)) === normalize(x)`.

Or:

> This workflow has five valid states. Model it as a state machine, enumerate the legal transitions, reject all other transitions, and test that terminal states cannot transition.

Or:

> These partial summaries must be combinable in any grouping, including an empty batch. Define an associative `combine` operation and an identity summary, then test both identity laws and associativity.

The mathematical term is useful because it compresses the requirement. The requirement remains in charge.

This is also a good filter for whether I understand the term. If I cannot say which law I need, what operation it gives me, or what failure it prevents, I probably do not need it in the prompt. I may merely enjoy saying it.

## Laws turn into tests

This is the part that makes the whole thing more than a prompting aesthetic.

A named abstraction can help the model generate an implementation. Its laws can help me reject the implementation.

Consider a normalizer:

```ts
const normalizeTag = (value: string): string =>
  value
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "-");
```

A few example-based tests are useful:

```ts
expect(normalizeTag("  Hello World  ")).toBe("hello-world");
expect(normalizeTag("ONE   TWO")).toBe("one-two");
```

But the property I actually care about is broader:

```ts
normalizeTag(normalizeTag(value)) === normalizeTag(value)
```

Once the model and I agree that normalization should be idempotent, it can generate many test cases rather than the two I happened to imagine. This is the basic move behind property-based testing: state a general property and automatically exercise it over generated inputs.[^quickcheck]

The same works for other structures.

For a monoid-like aggregation:

```ts
combine(value, empty) === value
combine(empty, value) === value
combine(a, combine(b, c)) === combine(combine(a, b), c)
```

For serialization:

```ts
decode(encode(value)) === value
```

For a canonical formatter:

```ts
format(parse(format(value))) === format(value)
```

For a functor-like mapping operation:

```ts
map(identity, value) === value
map(compose(g, f), value) === map(g, map(f, value))
```

For a retryable operation that claims to be idempotent:

```ts
run(run(state, command), command) === run(state, command)
```

The exact equality may need to ignore timestamps, generated IDs, or other irrelevant details. That is not a nuisance around the abstraction. Deciding what counts as equality is part of understanding the domain.

This changes my relationship to generated code. I am not merely reading a diff and asking whether it looks plausible. I can ask the model to derive properties from the abstraction, run them, find counterexamples, and reduce those counterexamples to something I can understand.

The model generates candidates. The laws provide pressure.

## A more useful prompt experiment

There is a temptation to treat all of this as philosophy. It is testable.

Take a small coding task and prepare three prompts:

```text
A. Vague
"Refactor this code to be cleaner and more reusable."

B. Structural
"These are pure transformations over one collection. Compose them and map once."

C. Structural plus laws
"These are pure transformations over one collection. Compose them and map once.
Preserve map identity and composition, and add property tests."
```

Run each prompt repeatedly with the same model, context, temperature, and tool access. Do not grade whether the answer feels functional-programming-shaped. Grade things that matter:

- Does it pass the existing tests?
- Does it satisfy the stated laws?
- How many unrelated architectures appear across runs?
- How many repair turns are required?
- How many new concepts, files, and dependencies does it introduce?
- Does a smaller model now succeed at the task?

My hypothesis is not that mathematical words always improve output. It is that a correct structural description reduces variance because it removes latent design decisions from the model’s job.

There is adjacent evidence for the general direction. More detailed prompts can improve code-generation performance, with explicit interfaces, edge cases, and stepwise specifications doing much of the work.[^specificity] Formal constraints can go further: type-constrained decoding has been shown to reduce compilation errors and improve functional correctness in code-generation tasks.[^types]

Neither result proves that saying “monoid” in a prompt is magical. It should not be. The point is narrower: useful constraints prune the space of plausible programs. A mathematical abstraction is one compact way to state several related constraints at once.

## I do not know what is inside the model

There is a more exciting version of this argument, and I do not trust it yet.

That version says that LLMs themselves learn deep abstractions in their latent spaces; that category theory is therefore somehow the natural language for communicating with them; that there is a common internal structure corresponding to “turn this content into that shape”; perhaps that an image-to-webpage model and a transcript-to-business-plan model are performing instances of the same hidden transformation.

I find this intuitively plausible. It is also, in this form, mostly vibes.

There is evidence that sequence models can learn internal representations that track underlying structure. In a controlled Othello experiment, researchers found a recoverable internal representation of board state and showed that intervening on it could influence the model’s output.[^othello] Other work has found concept-like geometric representations in language models. But these results do not establish that a general-purpose coding model contains a clean internal object corresponding to my preferred category-theory explanation.

Fortunately, I do not need that claim.

I am making a claim about the interface.

The model has seen a great deal of code, documentation, mathematics, and discussion connecting these terms. When I use a precise structural name correctly, I give it a compact region of that material to draw from. I reduce ambiguity. I suggest operations. I expose laws. I make the output easier to test.

There does not need to be a tiny category theorist living in the latent space.

## Going up and down the ladder

The magical thing about LLMs is not merely that they produce code. It is that they move between representations.

I can give a model a transcript and a Markdown template, and it will turn the transcript into a document whose content follows the template. I can give it an API and a product request, and it will express the product request through the API. I can give it imperative code and a domain operation, and it can sometimes reveal that the code is a map, a fold, a state machine, a parser, or a constraint problem.

It can move upward from concrete examples toward an abstraction, then downward from that abstraction into a different concrete form.

That movement is fuzzy. It is why the model is useful and why it is dangerous. A deterministic compiler refuses when the source does not type-check. An LLM often guesses which program I meant, invents the missing assumptions, and hands me something that looks finished.

Knowing more abstractions does not make the guessing disappear. It gives me intermediate representations where I can inspect it.

Instead of:

```text
messy request → code
```

I can work through:

```text
messy request
→ domain operation
→ structural description
→ laws and invariants
→ API
→ code
→ generated counterexamples
```

Each arrow is smaller. Each intermediate artifact gives me something to argue with. The prompt becomes less like a wish and more like source code.

This is, I think, the connection between abstract mathematics and programming with LLMs that matters right now. Not that every program is secretly category theory. Not that models think like mathematicians. Not that a Haskell vocabulary grants enlightenment.

Abstract mathematics is a catalog of structures that survived contact with many different concrete problems. Those structures have names. The names imply transformations. The transformations obey laws. The laws become tests.

I am not learning this material because I expect to prove theorems while building a CRUD application.

I am learning it because programming with an LLM is largely the work of finding a representation in which the next transformation becomes obvious—to a machine generating one token at a time, and to me when I am tired.

The loop was never difficult.

Recognizing what the loop *was* was the work.

---

## Notes

[^riehl]: Emily Riehl presents category theory as a cross-disciplinary language emphasizing transformations and gives the formal definition of categories, functors, and natural transformations in [*Category Theory in Context*](https://emilyriehl.github.io/files/context.pdf). The book is also available from the [Johns Hopkins Mathematics Department](https://math.jhu.edu/~eriehl/context/).

[^functor]: The GHC `base` documentation gives the programming definition and laws for [`Functor`](https://downloads.haskell.org/~ghc/latest/docs/libraries/base-4.22.0.0-66f8/Data-Functor.html). Its [`Monoid`](https://downloads.haskell.org/~ghc/latest/docs/libraries/base-4.22.0.0-66f8/Data-Monoid.html) documentation states the identity and associativity laws used here.

[^quickcheck]: Koen Claessen and John Hughes, [“QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs”](https://dl.acm.org/doi/10.1145/351240.351266), ICFP 2000.

[^specificity]: Yangtian Zi, Harshitha Menon, and Arjun Guha, [“More Than a Score: Probing the Impact of Prompt Specificity on LLM Code Generation”](https://arxiv.org/abs/2508.03678), 2025. Their result concerns increasing specification detail, not mathematical vocabulary specifically.

[^types]: Niels Mündler et al., [“Type-Constrained Code Generation with Language Models”](https://arxiv.org/abs/2504.09246), PLDI 2025. This work constrains decoding with a type system, which is stronger than merely naming a type-level structure in a natural-language prompt.

[^othello]: Kenneth Li et al., [“Emergent World Representations: Exploring a Sequence Model Trained on a Synthetic Task”](https://arxiv.org/abs/2210.13382), 2022/2023. The result is evidence from a controlled board-game setting, not proof of a general theory of LLM concepts.
EOF
wc -w /mnt/data/llms-abstract-math/01-the-right-abstraction-is-a-better-prompt.md
```

Validation showed map fusion preserves values only for pure functions; effects alter evaluation order. Benchmarks showed 2.5–2.8× gains for arrays, but negligible typed-array improvement.

<details><summary>💭 Thinking</summary>

**Drafted math prompting articles, research notebook, and packaged validated Markdown files**

</details>

Completed. Both articles are publication-length Markdown drafts with footnotes and source references. The third document contains the transcript-to-article mapping, voice analysis, fact-check ledger, research notes, reproducible experiments and outputs, rejected structures, and the editing record. It documents the auditable editorial process rather than private hidden reasoning.

### Articles

1. [The Right Abstraction Is a Better Prompt](sandbox:/mnt/data/llms-and-abstract-math/the-right-abstraction-is-a-better-prompt.md)  
   Abstract mathematics as prompt compression: composition, functors, monoids, laws, property tests, map fusion, and the limits of claims about model internals.

2. [I Failed Calculus. LLMs Taught Me Math Anyway](sandbox:/mnt/data/llms-and-abstract-math/i-failed-calculus-llms-taught-me-math-anyway.md)  
   A concrete learning method built around moving between examples, code, types, definitions, counterexamples, laws, tests, and machine-checked proofs.

### Editorial and research record

3. [Editorial and Research Log: LLMs and Abstract Math](sandbox:/mnt/data/llms-and-abstract-math/editorial-research-log.md)  
   Includes the transcript excerpt index, GO GO GOLEMS style audit, technical corrections, annotated research bibliography, benchmark methodology and results, property checks, an unrun spray-test protocol, and the complete revision record.

### Complete bundle

[Download all three documents and the reproducible experiment files](sandbox:/mnt/data/llms-and-abstract-math-drafts.zip)

