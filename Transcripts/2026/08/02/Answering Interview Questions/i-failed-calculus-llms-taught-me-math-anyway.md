# I Failed Calculus. LLMs Taught Me Math Anyway

## How I use models to move between examples, code, notation, laws, and proofs

I had remedial math at school. I dropped out of university partly because I could not do statistics and calculus. A couple of months ago I started learning category theory for fun.

This is a strange trajectory.

The more suspicious part is that my tutor is a machine famous for confidently making things up.

I do not think LLMs suddenly made mathematics easy, and I definitely do not think asking ChatGPT whether a proof is correct makes the proof correct. What changed for me is more specific: an LLM lets me keep changing the **representation** of an idea until I find one my brain can hold on to.

A textbook gives me the explanation the author wrote. A lecture gives me the explanation the lecturer prepared. Both might be excellent, but they have a fixed direction and a limited amount of space. If I fail to understand a symbol on page 18, page 19 does not notice. It just keeps going, with the grim confidence of a train whose next stop is an exam I am going to fail.

An LLM lets me say:

> Stop. Explain the same thing using a compiler.

Then:

> I still don’t get it. Show me the TypeScript type.

Then:

> Give me a concrete example with three values.

Then:

> Now give me something that looks almost the same but violates one law.

Then:

> Translate every symbol in the definition back into the example.

Then:

> Do not explain it again. Ask me a question that will reveal which part I misunderstood.

That ability to go up and down the ladder of abstraction is what finally made abstract math accessible to me.

I did not hate abstraction. I hated being trapped on one floor.

## The math I could do did not look like math

I always struggled with calculation-heavy mathematics. But over the years I happily played with compilers, proof systems, model checking, types, parsers, and programming language semantics. These are not non-mathematical subjects. They are soaked in math. They just present it as structures and transformations instead of a page full of numbers.

A compiler takes one representation and transforms it through several others while preserving meaning:

```text
source text
→ tokens
→ syntax tree
→ typed intermediate representation
→ optimized intermediate representation
→ machine code
```

A model checker explores a state space and asks whether invariants survive every allowed transition. A type system gives rules for which expressions compose. A parser turns sequences into structure. A proof assistant reduces a human claim to a formal object a small kernel can check.

I was doing abstract mathematics badly and informally for years. I just did not have the vocabulary for it.

This matters because “bad at math” is an extremely broad diagnosis. It compresses together arithmetic fluency, symbolic manipulation, spatial reasoning, proof, abstraction, memory, classroom anxiety, notation, and whether the explanation happened to fit the student’s brain. I was bad at several of those things. I was not equally bad at all of them.

LLMs did not repair every weakness. They gave me a way to route around some of them long enough to build a better mental model.

## The abstraction ladder

When I learn a new concept, I now try to place it on a ladder like this:

```text
concrete values
↕
example program
↕
type signature
↕
abstract structure
↕
laws
↕
property tests
↕
proof
```

The arrows go both ways. That is important.

A lot of math education only moves upward. Here are some numbers. Now replace them with variables. Now accept this definition. Now prove something. If I lose the thread, the prescribed solution is usually to stare harder at the higher rung.

An LLM makes downward movement cheap. I can take a definition and ask for code. I can take the code and ask for three executions. I can take a failed execution and ask which law it violates. I can take the law and ask for a property test. I can take the test and ask what it would mean to prove the claim instead of sampling it.

None of these representations is the concept by itself. Each makes different mistakes visible.

Code makes types and execution concrete, but it can hide the generality. A type signature removes implementation detail, but it does not state the laws. A law can reveal the structure, but notation can make an obvious thing look alien. Property tests find counterexamples, but passing ten thousand cases is not a proof. A proof can be correct while formalizing the wrong requirement.

The learning process is moving between these views until they agree.

## A complete example: averaging is not composable

Suppose I am collecting latency measurements from several workers and want to combine partial results. The first implementation might look like this:

```ts
const average = (left: number, right: number): number =>
  (left + right) / 2;
```

This looks like a perfectly respectable “combine” operation. It takes two numbers and returns one number. It is symmetric. It feels as if I should be able to average each worker’s result and then average those averages.

So I ask the model:

> I want to aggregate values in parallel, where the runtime may regroup operations. Do not name the abstract structure yet. What law must a binary `combine` operation satisfy so regrouping cannot change the result? Find a small integer counterexample for binary average.

The important instruction is “do not name the structure yet”. I want to start from the operational problem, not memorize another noun.

The law is associativity:

```text
combine(combine(a, b), c)
=
combine(a, combine(b, c))
```

And binary average fails almost immediately:

```text
average(average(0, 0), 10) = 5
average(0, average(0, 10)) = 2.5
```

The parentheses changed the answer. That means a parallel runtime, a tree reduction, or a harmless-looking refactor can change the result.

Now I can move up one rung and ask:

> What is the smallest standard algebraic structure that names an associative binary operation? What additional value would make it possible to represent an empty aggregation?

An associative binary operation gives a semigroup. Add an identity value and it becomes a monoid.[^riehl-monoid]

But the point is not to put `Monoid` in a class name. The point is that the law told me my representation was wrong.

A single average throws away the information needed to combine groups correctly. I need to carry the sum and the count:

```ts
type Stats = {
  sum: number;
  count: number;
};

const emptyStats: Stats = {
  sum: 0,
  count: 0,
};

const combineStats = (left: Stats, right: Stats): Stats => ({
  sum: left.sum + right.sum,
  count: left.count + right.count,
});

const observe = (value: number): Stats => ({
  sum: value,
  count: 1,
});

const mean = ({ sum, count }: Stats): number | null =>
  count === 0 ? null : sum / count;
```

Now partial results can be regrouped without losing the weights:

```ts
const result = chunks
  .map(chunk => chunk.map(observe).reduce(combineStats, emptyStats))
  .reduce(combineStats, emptyStats);
```

The abstract concept produced a concrete API improvement. The bug was not in the averaging formula. It was in choosing `number` as the state of an aggregation that needed two pieces of information.

There is an additional computer-shaped trap: JavaScript numbers use floating-point arithmetic, and floating-point addition is not strictly associative because of rounding. The mathematical structure is exact over integers or real numbers; the implementation may only satisfy an approximate version for floating values. This is the kind of annoying detail that makes the abstraction more useful, not less. It tells me exactly which assumption the machine violates and forces me to decide whether I need integer units, decimal arithmetic, compensated summation, a tolerance, or simply a documented practical approximation.

This is what I want from math: not decorative generality, but a word and a law that reveal why a program cannot safely compose.

## The model is an elevator, not the foundation

My use of an LLM here is mostly translation.

I start with code I understand. I ask for the law hiding inside it. I ask for examples and non-examples. I ask for the notation. I ask the model to generate a counterexample. I run the counterexample. I ask for a repaired representation. Then I check the formal definition in a real source.

The model moves me between floors. It does not hold up the building.

This distinction is important because LLMs are extremely good at producing explanations that feel complete. A smooth explanation removes the sensation of confusion much faster than it removes the confusion itself. You can finish a conversation with the model, recognize every sentence, and still be unable to produce an example without assistance.

So I force the interaction to become executable.

Instead of:

> Explain associativity.

I ask:

> Give me three operations that are associative, three tempting operations that are not, and a smallest counterexample for each failure. I will predict the result before you reveal it.

Instead of:

> Is my implementation a monoid?

I ask:

> State the candidate operation and identity separately. Write the two identity properties and associativity as executable tests. Search for a counterexample before telling me whether the structure qualifies.

Instead of:

> Is this proof correct?

I ask:

> Do not rewrite the proof. Identify the first step that is not justified by a definition, theorem, or previously established result. Then give me the exact obligation I still need to prove.

The output is still untrusted. But it has become much easier to challenge.

## Ask for non-examples before asking for more explanation

Explanations are dangerously cooperative. They keep finding new metaphors that preserve the central misunderstanding.

Counterexamples are less polite.

If I think every operation of type:

```text
A × A → A
```

is somehow “monoid-like”, binary average destroys that idea. If I think every container with a method called `map` is automatically a lawful functor, a counterexample to identity or composition destroys that. If I think any list-to-tree conversion is a natural transformation, writing down the naturality condition forces me to specify a family of conversions that commutes with mapping; an arbitrary conversion does not get the title for free.[^riehl-natural]

While drafting these articles, that last point corrected a sentence from the original recording. I had the intuition that lists and trees are both mappable structures, and then jumped to saying that transforming one into the other was therefore a functor transformation. The intuition is useful. The sentence was not yet justified. Once the actual condition entered the document, the handwaving stopped surviving.

That is a good learning loop:

```text
vague intuition
→ formal definition
→ attempted example
→ failed obligation
→ corrected intuition
```

I now routinely ask:

> Give me something that matches the analogy but fails the definition.

or:

> What is the smallest finite counterexample to my claim?

or:

> Which word in my explanation is doing more work than I have justified?

Models are often useful at generating candidate counterexamples because they can move quickly across many familiar examples. But candidate is the important word. I execute them, calculate them, or check them against a source. A fabricated counterexample can be as persuasive as a fabricated theorem.

## Make the model label what kind of statement it is making

One recurring failure mode in math explanations is that definitions, intuitions, analogies, conventions, and consequences blend into one smooth paragraph.

I use a prompt like this:

```text
I am learning [CONCEPT] from the perspective of a programmer.

For every important statement, label it as one of:
- Definition
- Law / axiom
- Derived consequence
- Example
- Non-example
- Analogy

Start from this concrete code or problem: [EXAMPLE].
Translate every symbol in the formal definition back to the example.
Give one near-miss that satisfies all but one requirement.
Do not treat an analogy as evidence.
End with executable properties and a primary source for the definition.
```

This is not a universal tutor prompt. It is a way to prevent the model from hiding a logical transition in good prose.

The labels also tell me what kind of verification I need.

- A definition needs a source.
- An example needs calculation or execution.
- A derived consequence needs an argument.
- An analogy needs nothing except usefulness, but it should not quietly become a theorem.
- A property test needs generated inputs and a clear equality relation.
- A proof needs a checker or enough detail for independent review.

The model’s greatest strength here is linguistic flexibility. Its greatest danger is also linguistic flexibility. The same ability that translates a definition into five useful metaphors can make a false connection feel inevitable.

## Do not let the tutor answer too quickly

General-purpose LLMs tend to answer the question in front of them. That is useful when I need a result and bad when I am trying to learn how to produce the result.

Research on LLM tutoring has found the same problem: models often provide solutions directly, while systems explicitly designed around Socratic guidance try to review the learner’s state, provide a hint, correct errors, and summarize instead.[^socratic]

So I often tell the model:

```text
Do not solve the exercise.
Ask one question at a time.
Choose the question that best distinguishes between the two most likely
misconceptions in my previous answer.
After I answer, tell me only whether the answer satisfies the relevant law.
```

Or:

```text
I will attempt the proof.
Do not continue it for me.
At each turn, identify only the first unsupported step and name the definition
or lemma that would justify it.
```

This makes the interaction slower. That is the point.

A model can generate twenty pages of explanation in the time it takes me to understand one diagram. The bottleneck is not the supply of text. It is whether my mental model changed.

I use the model to create a feedback loop around my thinking, not to replace the thinking with a completed answer I can nod at.

## Turn the laws into running code

For programming-adjacent mathematics, executable checks are the easiest bridge between intuition and rigor.

The average counterexample can be a unit test:

```ts
expect(average(average(0, 0), 10))
  .not.toBe(average(0, average(0, 10)));
```

The repaired integer-valued `Stats` combination can be tested with generated values:

```ts
import fc from "fast-check";

const statsArbitrary = fc.record({
  sum: fc.integer(),
  count: fc.nat(),
});

fc.assert(
  fc.property(statsArbitrary, stats => {
    expect(combineStats(emptyStats, stats)).toEqual(stats);
    expect(combineStats(stats, emptyStats)).toEqual(stats);
  }),
);

fc.assert(
  fc.property(
    statsArbitrary,
    statsArbitrary,
    statsArbitrary,
    (a, b, c) => {
      expect(combineStats(combineStats(a, b), c)).toEqual(
        combineStats(a, combineStats(b, c)),
      );
    },
  ),
);
```

Property-based testing does not prove the law for every value, but it changes the learning task. I have to state the law precisely enough to execute it. The framework can search for counterexamples and, in mature systems such as QuickCheck and `fast-check`, shrink failures toward smaller examples.[^property-testing]

For some concepts, I can go further and use a proof assistant. Lean is both a programming language and an interactive theorem prover; its small kernel checks proof terms against the formal system.[^lean] I can ask an LLM to translate an informal claim into Lean, but the useful authority is Lean accepting the proof, not the model saying the proof “looks correct”.

Even then, the checker proves the statement I formalized under the assumptions I supplied. It does not prove that I formalized the product requirement correctly. There is always another representation boundary where human judgment enters.

The hierarchy I use is roughly:

```text
plausible explanation
< worked examples
< executable counterexample search
< primary mathematical source
< machine-checked proof of the formalized statement
```

This is not a universal ranking. A proof of the wrong model is less useful than a good test of the real system. It is simply a reminder that fluent prose sits at the bottom.

## Useful does not mean reliable

There is empirical evidence that LLM-generated math help can support learning, but the reliability caveat is not theoretical.

A 2024 randomized study comparing no help, human-authored help, and ChatGPT-generated help across several mathematics areas found learning gains from the generated help. It also found that the initial generated material failed quality checks on 32% of problems; mitigation techniques reduced that rate substantially, but did not make the underlying risk disappear.[^pardos]

A separate randomized trial of Tutor CoPilot found gains when LLM-generated guidance was supplied to human tutors in live K–12 mathematics tutoring. The system supported a human already in the loop rather than pretending the language model was an autonomous source of mathematical truth.[^tutor-copilot]

This matches my experience. The model is most useful when I can make it produce an artifact another system can reject:

- code a runtime can execute,
- a property a test runner can falsify,
- a citation I can open,
- a definition I can compare to a textbook,
- a proof a kernel can check,
- a counterexample I can calculate by hand.

It is least safe when I ask a broad question, receive a beautiful answer, and treat the feeling of recognition as knowledge.

## What I can see in programs now

Learning abstract math has not turned my code into Haskell. It has changed which patterns I notice.

I see operations that should be idempotent because they will be retried.

I see reducers that cannot be parallelized because their combine operation is not associative.

I see three booleans and two nullable timestamps that are secretly an invalid state machine.

I see a function that manually unwraps and rebuilds `Result` values when it really wants a lawful map over the successful value.

I see normalization functions that should reach a fixed point.

I see dependency graphs where the business requirement gives a partial order but the implementation accidentally freezes one total sequence.

I see cache keys that need an equivalence relation and canonical representation, not another round of string concatenation.

Most importantly, I can name these things in a prompt.

The LLM does not have to infer the entire structure from a pile of code and prose. I can tell it which operation I think is present, which laws should hold, and which counterexamples would prove me wrong. That leads to better code, but it also creates a much better conversation. Instead of arguing about whether a refactor “feels cleaner”, I can ask whether it preserves identity, composition, ordering, or an invariant.

The abstraction becomes a shared debugging object between me and the model.

## Learning math also taught me how to use the model

There is a loop here.

I started learning abstract math because I suspected it would give me better ways to prompt LLMs. Then using an LLM as a translator taught me something about abstraction itself.

A model is unusually good at moving between representations: transcript to outline, API documentation to code, code to explanation, example to generalized pattern, formal notation to ordinary language. It is not uniformly correct at these transformations, but it makes them cheap enough that I can try several and compare them.

Research on scratchpads, decomposition, and program-aided reasoning shows a related effect on the model side: changing how intermediate work is represented can make multi-step tasks more tractable.[^model-representation] Algebraic notation does this for humans. We write symbols on paper so we do not have to hold the whole problem in working memory; then we apply small transformation rules. Code and formal notation can play a similar externalizing role for a language model generating sequentially.

I do not need to say that LLMs “think like us”. That phrase hides more than it explains. The practical observation is enough: both the human and the model can perform better when the problem is moved into a notation where the next step is local, explicit, and checkable.

That is the real value of the abstraction ladder. I am not trying to remain at the highest level. I am trying to choose the level where the current confusion becomes visible.

## The tutor I do not trust

I still do not trust the model on mathematics.

I trust it to produce another explanation. I trust it to generate candidate examples quickly. I trust it to translate notation into TypeScript, to suggest a property, to propose a counterexample, to point me toward a term I did not know.

Then I trust something else.

I trust the execution result. I trust the definition in a serious source. I trust a property test to find the case I missed. I trust a proof checker within the limits of the formalization. I trust the discomfort that appears when two representations do not line up.

The model did not make me good at calculation. It gave me a way to keep changing the representation until calculation stopped being the interesting part.

It did not remove the hard part of learning. It made the hard part easier to locate.

Instead of staring at a wall of symbols and deciding that math is something other people can do, I can go down to code, sideways to a diagram, back up to a law, and then hand the claim to a machine that is much less charming and much more trustworthy than my tutor.

For the first time, I do not experience abstraction as the place where concrete understanding disappears.

It is the thing that lets me move between concrete examples without losing what they have in common.

---

## Notes

[^riehl-monoid]: Emily Riehl, [*Category Theory in Context*](https://emilyriehl.github.io/files/context.pdf), Definition 1.6.2, p. 39, presents a monoid as an object with an associative multiplication and a two-sided identity. In ordinary algebra/programming language, a semigroup has the associative operation; a monoid adds the identity.

[^riehl-natural]: Riehl, [*Category Theory in Context*](https://emilyriehl.github.io/files/context.pdf), Definition 1.4.1, p. 25. The naturality condition is what turns a family of component maps between two functors into a natural transformation.

[^socratic]: Yuyang Ding et al., [“Boosting Large Language Models with Socratic Method for Conversational Mathematics Teaching”](https://doi.org/10.1145/3627673.3679881) (CIKM 2024). The paper explicitly contrasts general models’ tendency to provide solutions with a structured tutoring approach based on review, guidance, correction, and summarization. Its experiments concern a constructed tutoring dataset and should not be read as proof that general-purpose LLMs are reliable autonomous tutors.

[^property-testing]: Koen Claessen and John Hughes, [“QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs”](https://dl.acm.org/doi/10.1145/351240.351266) (ICFP 2000); John Hughes, [“How to Specify It! A Guide to Writing Properties of Pure Functions”](https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf) (TFP 2019/2020); [fast-check documentation](https://fast-check.dev/docs/introduction/what-is-property-based-testing/). The drafting experiments for this article used a dependency-free seeded generator rather than `fast-check`; 10,000 cases each passed for array identity, array composition, and an idempotent string normalizer. The same script produced the `average(0, 0, 10)` associativity counterexample and the map-fusion effect-ordering counterexample. Full details are in the editorial/research log.

[^lean]: [*Theorem Proving in Lean 4*](https://lean-lang.org/theorem_proving_in_lean4/) and the [Lean Language Reference](https://lean-lang.org/doc/reference/latest/). Lean’s kernel checks proof terms in dependent type theory; using Lean does not remove the need to validate that the formal statement matches the intended real-world claim.

[^pardos]: Zachary A. Pardos and Shreya Bhandari, [“ChatGPT-generated help produces learning gains equivalent to human tutor-authored help on mathematics skills”](https://doi.org/10.1371/journal.pone.0304013), *PLOS ONE* 19(5), 2024. The study used 274 participants across elementary algebra, intermediate algebra, college algebra, and statistics. Its reported quality-check failures are a useful warning against treating generated tutoring content as automatically correct.

[^tutor-copilot]: Rose E. Wang et al., [“Tutor CoPilot: A Human-AI Approach for Scaling Real-Time Expertise”](https://arxiv.org/abs/2410.03017) (2024). The preregistered randomized trial involved 900 tutors and 1,800 K–12 students and reported higher topic mastery when tutors had access to generated guidance, with the largest gains among lower-rated tutors. The paper also reports limitations, including suggestions that were not grade-level appropriate.

[^model-representation]: Maxwell Nye et al., [“Show Your Work: Scratchpads for Intermediate Computation with Language Models”](https://arxiv.org/abs/2112.00114) (2021); Denny Zhou et al., [“Least-to-Most Prompting Enables Complex Reasoning in Large Language Models”](https://arxiv.org/abs/2205.10625) (2022); Wenhu Chen et al., [“Program of Thoughts Prompting”](https://arxiv.org/abs/2211.12588) (2022); Luyu Gao et al., [“PAL: Program-aided Language Models”](https://arxiv.org/abs/2211.10435) (ICML 2023). These studies concern particular prompting/training settings and tasks; they support the limited point that decomposition and external representation affect performance, not a claim that model reasoning is identical to human mathematical reasoning.
