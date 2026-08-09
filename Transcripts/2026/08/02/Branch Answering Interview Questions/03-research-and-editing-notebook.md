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
