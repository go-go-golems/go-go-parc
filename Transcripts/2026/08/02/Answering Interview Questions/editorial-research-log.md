# Editorial and Research Log: “LLMs and Abstract Math”

> This document records the source material, editorial decisions, fact-checking, experiments, and revision history behind the two article drafts. It is designed to make the work auditable and reusable.
>
> It is **not** a transcript of hidden model reasoning. Raw private chain-of-thought is neither necessary nor reliable as an editorial artifact. What follows is the useful part: the claims considered, evidence consulted, tests run, alternatives rejected, and reasons for the published wording.

- Source note ID: `0cb27c2c-383d-4db0-b805-98a7b5443efc`
- Source recording: `2026-08-02T16:43:44Z`
- Source title: `LLMs and Abstract Math`
- Drafting and research date: `2026-08-02`
- Outputs:
  1. [`the-right-abstraction-is-a-better-prompt.md`](./the-right-abstraction-is-a-better-prompt.md)
  2. [`i-failed-calculus-llms-taught-me-math-anyway.md`](./i-failed-calculus-llms-taught-me-math-anyway.md)

## Executive summary

The recording contained two strong articles and several additional essays trying to occupy the same space.

The two retained theses are:

1. **Programming thesis:** Abstract mathematics supplies compact names for recurring structures and their laws. Correctly naming such a structure can reduce the number of unstated transformations an LLM has to perform, shape a clearer API, and generate properties with which to test the result.
2. **Learning thesis:** An LLM is useful for learning abstract mathematics because it can cheaply translate between concrete examples, code, types, notation, laws, tests, and proofs. It should be treated as a translation and exercise interface, not as the final authority on mathematical truth.

The strongest speculative thesis in the recording—that LLMs may contain a common latent representation corresponding to human mathematical abstractions—was retained only as a qualified aside. Existing research supports the existence of decodable and sometimes causally useful internal representations in particular models and tasks. It does not establish a clean category-theoretic abstraction layer inside general-purpose LLMs.

Two local experiments were run:

- A JavaScript microbenchmark compared four pure `map` passes with one fused `map`. On the drafting environment, the fused version had a 3.93× lower median runtime for 500,000 values. This supports the limited implementation claim, not a universal performance ratio.
- A seeded, dependency-free property-check script ran 10,000 cases each for array identity, array composition, and idempotent normalization; all passed. It also generated/verified the binary-average associativity counterexample and demonstrated that map fusion changes effect ordering when functions are impure.

A proposed multi-run LLM prompt experiment is documented below but was not run. No controlled independent model harness was available in the drafting environment, and inventing results would defeat the point of the article.

## 1. Source transcript map

The transcript was conversational and repetitive in a productive way: it circled a few ideas until their connections became visible. The article drafts preserve those connections but separate them into arguments a reader can follow.

The excerpt IDs below are local references for this log.

### T1 — Personal mathematical history

> “math has always been something I really, really struggle with”

> “I had remedial math at school, and I dropped out of university because I couldn't do statistics and calculus.”

**Use:** This became the opening contradiction of Article 2 and a shorter credibility-setting section in Article 1. It explains why the essays approach mathematics through structure rather than calculation.

**Editing choice:** The drafts do not invent a redemption arc in which the author became broadly “good at math”. The narrower change is access to representations and vocabulary.

### T2 — Abstract computer science was easier

> “there weren't really any numbers. They were just like abstract structures.”

> “compilers and proof systems and model checking and all the like more abstract part of theoretical computer science, which I had much less problems with”

**Use:** Article 2 reframes “bad at math” as an overbroad diagnosis and uses compilers, model checking, types, parsers, and proof assistants as familiar mathematical structures.

**Editing choice:** “No numbers” is kept as personal perception, not a literal description of those fields.

### T3 — Models as pattern transformers

> “LLMs are ultimately like pattern matchers and pattern transformers.”

> “you give it, say, a markdown structure document, and then you ask it to fill it with a certain type of content, it will merge both structures.”

**Use:** This became the practical interface claim: models are good at moving between representations, and prompts can make the required transformation more or less explicit.

**Editing choice:** The drafts avoid presenting “pattern matcher” as a complete mechanistic theory of transformers.

### T4 — Category theory and relationships

> “category theory is in a way recognizing the structure, how being able to describe something purely by its relationships”

> “the only things that are given in category theory is things, relationship between things called arrows or morphisms. And then these morphisms have to compose.”

**Use:** Article 1 includes a deliberately small category-theory section focused on objects, morphisms, identities, and composition.

**Editing choice:** The informal “relationships” account was tightened. A category is not an arbitrary graph or a generic transitive relation. Its morphisms have specified domains/codomains, identity morphisms, and an associative, unital composition operation.

### T5 — The latent-space speculation

> “there's a good chance that the LLM internally has like kind of a common part of the latent space that maybe corresponds to it.”

> “this is just vibes because I am not actually a machine learning LLM expert.”

**Use:** Article 1 preserves the speculation and, crucially, the disclaimer. It then separates evidence from inference.

**Editing choice:** The article makes the stronger, supportable interface claim and treats the internal-representation theory as unresolved.

### T6 — The ladder of abstraction

> “LLMs being machines that are able to go back and forth the ladder of abstraction is a magical thing.”

> “having ... a deep understanding of these structures ... allows you to prompt an LLM in the way that you help it do a sequence of transformations that work well.”

**Use:** This became the organizing metaphor of Article 2: concrete values ↔ code ↔ types ↔ structures ↔ laws ↔ tests ↔ proofs.

**Editing choice:** “Magical” remains part of the emotional thesis, but the method is made concrete and reproducible.

### T7 — Repeated loops and map composition

> “being able to suddenly say, ‘Hey, these 15 for loops are actually 15 map compositions’”

> “the map composition allows you to compose the function up front and then just do a single map.”

**Use:** This became the opening example of Article 1 and the local map-fusion benchmark.

**Editing choice:** The original claim that this can produce “a hundred times” fewer tokens or a much faster algorithm was narrowed. The draft explains the structural benefit and reports one measured 3.93× microbenchmark result with strong caveats.

### T8 — Notation as cognitive scaffolding

> “Arabic numerals and algebraic notations kind of allow us to solve polynomials even when really, really tired because we can write it out on paper and kind of apply some very basic transformation rules.”

**Use:** Article 2 connects mathematical notation, code, scratchpads, and program-aided reasoning as ways of externalizing intermediate state.

**Editing choice:** The draft says LLMs generate autoregressively rather than saying they “think linearly”.

### T9 — Laws, invariants, and testing

> “it has a mathematical foundation that we can now prove or add at least a couple of invariants or do like quick check type of unit testing”

> “use the mathematical abstraction to create test cases”

**Use:** This became a central part of both articles rather than a late aside. The laws are what distinguish mathematical vocabulary from a stylistic keyword.

**Editing choice:** Property-based testing is distinguished from proof. Passing generated cases can find counterexamples; it does not establish a universal theorem.

### T10 — The natural article break

> “maybe this is enough for a first article, right? It's like the link between these two things”

**Use:** The transcript itself recognized the split. Article 1 covers the connection between abstract structure and prompting. Article 2 covers the personal learning method.

## 2. Voice and style audit

The request was not simply to clean up the transcript. It was to write in the established voice of [GO GO GOLEMS](https://gogogolems.substack.com/). Four recent posts were used as the primary style sample.

### “Simplicity in the age of AI-assisted coding”

Source: [gogogolems.substack.com/p/simplicity-in-the-age-of-ai-assisted](https://gogogolems.substack.com/p/simplicity-in-the-age-of-ai-assisted)

Observed pattern:

- Starts with a compact claim, then immediately grounds it in a sticky-header example.
- Moves the same problem through several representations: user language, product ticket, configuration, CSS, and code.
- Broadens into an argument about inherited complexity and human judgment.
- Returns explicitly to the sticky header in the conclusion.

**Applied:** Article 1 begins with four concrete loops, expands into abstraction and model behavior, then returns to the loops at the end. Article 2 begins with a personal contradiction, works through one complete averaging example, and returns to the untrusted tutor.

### “Slowing Down in the Age of Coding Agents”

Source: [gogogolems.substack.com/p/slowing-down-in-the-age-of-coding](https://gogogolems.substack.com/p/slowing-down-in-the-age-of-coding)

Observed pattern:

- First-person workflow details are used to support a general engineering argument.
- Vocabulary and notation are treated as major architecture choices.
- The prose tolerates long paragraphs, parenthetical comments, and blunt judgments.
- The conclusion states a broader bottleneck: deciding what should be written and choosing the words that shape it.

**Applied:** Both drafts keep first-person claims and show the actual prompts and code through which the general idea becomes useful.

### “Why I Make My Agents Keep Diaries”

Source: [gogogolems.substack.com/p/why-i-make-my-agents-keep-diaries](https://gogogolems.substack.com/p/why-i-make-my-agents-keep-diaries)

Observed pattern:

- Opens with a striking concrete artifact rather than an abstract thesis.
- Builds a large argument around one dense word—“diary”—and the cluster of behavior it summons from the training corpus.
- Treats the generated artifact as something useful to both the model and the human.

**Applied:** Article 1 deliberately extends this argument: ordinary dense words summon patterns; mathematical terms can summon patterns plus explicit laws.

### “From ‘prompt and pray’ to prompt engineering”

Source: [gogogolems.substack.com/p/from-prompt-and-pray-to-prompt-engineering](https://gogogolems.substack.com/p/from-prompt-and-pray-to-prompt-engineering)

Observed pattern:

- Concrete frustration is reframed as an engineering problem.
- The “spray test” treats output variance as evidence about prompt ambiguity.
- Single words are shown to push generation toward different regions of the training distribution.
- Diffs are described as compiled output; the prompt and encountered context are treated as source.
- The prose uses memorable metaphors without abandoning the engineering claim.

**Applied:** Article 1 describes “simplify this” as an underspecified branching request and treats mathematical vocabulary as a way to narrow the generation. The proposed prompt experiment below adopts the same multi-run spray-test idea.

### Voice decisions

The transcript’s spoken disfluencies were **not** copied into the articles. The published blog voice is conversational but edited. The drafts retain:

- first-person admissions and self-deprecation;
- concrete code before theory;
- long causal paragraphs;
- occasional profanity or jokes where they carry an argument;
- strong, reusable lines;
- skepticism toward fashionable abstractions and toward LLM mysticism;
- conclusions that return to the opening image.

The drafts avoid artificially introducing typos or stutters. Existing posts contain some, but deliberate error imitation would make the writing less authentic rather than more.

## 3. Why the material became two articles

### Article 1: “The Right Abstraction Is a Better Prompt”

**Final thesis:** Abstract mathematics is a catalog of named structures with laws. Naming the correct structure reduces hidden inferential work in a coding prompt, guides API shape, and supplies properties for testing the generated implementation.

**Required movement:**

```text
concrete repeated loops
→ hidden prompt transformations
→ mathematical vocabulary
→ functor/monoid examples
→ laws as tests
→ cautious model-internals discussion
→ return to loops
```

### Article 2: “I Failed Calculus. LLMs Taught Me Math Anyway”

**Final thesis:** The model’s value as a math tutor is not final authority but cheap translation between representations. Learning improves when definitions, examples, code, non-examples, laws, property tests, and proofs can be traversed in both directions.

**Required movement:**

```text
personal contradiction
→ “bad at math” versus structural ability
→ abstraction ladder
→ complete average/associativity example
→ counterexamples and Socratic prompting
→ verification hierarchy
→ practical programming patterns
→ untrusted tutor conclusion
```

### Material deliberately reserved for other essays

The transcript also contains at least three separate arguments:

1. **“The Stochastic Parrot Is the Point”** — fuzzy statistical transformation as capability rather than insult.
2. **“Correctness Is Not the Whole Product”** — formal correctness alongside design sense, user understanding, business fit, and validation.
3. **“The Abstraction Budget”** — the number of unstated representational leaps a model can perform reliably in one task.

Trying to preserve these in Article 1 would have delayed the thesis and turned the conclusion into a second introduction.

## 4. Technical claim ledger

| Transcript formulation | Risk or error | Published formulation | Main source / check |
|---|---|---|---|
| Category theory describes things “purely by relationships”. | Too broad; describes graphs/relations as well. | A category has objects, morphisms, identities, and associative, unital composition. The useful intuition is emphasis on composition and structure-preserving transformations. | Emily Riehl, *Category Theory in Context*, Def. 1.1.1. |
| If A relates to B and B to C, A relates to C. | Sounds like ordinary relational transitivity. Category composition produces a specified composite morphism; there can be many morphisms, and equality of paths is additional structure. | Compatible morphisms compose; composition is associative and has identities. | Riehl, Def. 1.1.1. |
| “map often being called a functor”. | `map`/`fmap` is an operation associated with a functor; it is not itself the whole functor. | A functor maps objects and morphisms and preserves identities/composition; arrays/trees give a programming intuition via lawful mapping. | Riehl, Def. 1.3.1. |
| Converting a list of `T` into a tree of `T` is transforming one functor into another. | An arbitrary conversion function is not automatically a natural transformation. | A family of conversions must satisfy the naturality condition to qualify. | Riehl, Def. 1.4.1. |
| “types can be modeled as a monoid”. | A bare type is not generally a monoid. | A type/set equipped with an associative binary operation and identity may form a monoid. | Riehl, Def. 1.6.2. |
| Fifteen maps can be composed and then run once. | Only semantics-preserving under relevant purity/effect assumptions; error and effect ordering can change. | Safe for the demonstrated pure element-wise transformations; explicit counterexample shows different side-effect order. | Local executable experiment; ECMAScript `map` semantics. |
| The fused version is “a hundred times” less code/faster. | Unmeasured and workload-dependent. | One local benchmark measured 3.93× median runtime improvement; the portable claim is fewer passes and intermediate arrays. | Local benchmark, Node 22.16.0. |
| “LLMs think linearly.” | Anthropomorphic and mechanistically imprecise. | Text models generate autoregressively; external notation can make intermediate steps local and checkable. | GPT/scratchpad/program-aided reasoning literature. |
| LLMs understand concrete things only through token-token relationships. | Too strong, particularly for multimodal models; attention is not the whole trained representation. | At the text interface, the user supplies symbol sequences; models learn internal features/representations whose exact organization remains under investigation. | Representation papers listed below. |
| There may be a common latent area corresponding to cross-domain abstractions. | Plausible speculation, not established by available evidence. | Some models contain decodable and causally useful representations for particular concepts/tasks; this does not prove a clean universal abstraction layer. | Li et al.; Gurnee & Tegmark; Park et al.; Engels et al.; Gendron et al. |
| Mathematical structure lets us “prove” code correct. | Recognition of a structure alone is not a proof, and software semantics may violate ideal laws. | Structures suggest properties; property tests search for counterexamples; proof assistants check formalized claims under explicit assumptions. | QuickCheck/Hughes; Lean documentation. |
| Correctness is a tiny part of good software. | Overbroad and distracting in this essay. | Removed from both drafts; retained as a separate potential article. | Editorial scope decision. |

## 5. Research notes

### 5.1 Category theory definitions

Primary source: Emily Riehl, [*Category Theory in Context*](https://emilyriehl.github.io/files/context.pdf).

Relevant passages:

- **Category:** Definition 1.1.1, pp. 3–4.
- **Functor:** Definition 1.3.1, p. 14.
- **Natural transformation:** Definition 1.4.1, p. 25.
- **Monoid:** Definition 1.6.2, p. 39.

Editorial result:

- Category theory is introduced through composition, but the formal minimum is stated.
- “Mappable container” is explicitly labeled a programming intuition, not the full definition of a functor.
- The transcript’s list-to-tree claim is corrected rather than silently removed; the correction itself demonstrates why laws are useful.

### 5.2 Property-based testing

Primary sources:

- Koen Claessen and John Hughes, [“QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs”](https://dl.acm.org/doi/10.1145/351240.351266), ICFP 2000.
- John Hughes, [“How to Specify It! A Guide to Writing Properties of Pure Functions”](https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf), TFP 2019/2020.
- Current JavaScript implementation documentation: [fast-check: What is Property-Based Testing?](https://fast-check.dev/docs/introduction/what-is-property-based-testing/).

Research result:

Hughes distinguishes several routes to properties, including invariants, postconditions, metamorphic properties, inductive properties, and model-based properties. This supports a broader treatment than “random unit tests”. The articles use laws as executable relations over generated values and repeatedly state that such tests are not formal proofs.

### 5.3 Internal representations in language models

Primary sources:

- Kenneth Li et al., [“Emergent World Representations: Exploring a Sequence Model Trained on a Synthetic Task”](https://openreview.net/forum?id=DeG07_TcZvT), ICLR 2023.
- Wes Gurnee and Max Tegmark, [“Language Models Represent Space and Time”](https://arxiv.org/abs/2310.02207), 2023/2024.
- Kiho Park, Yo Joong Choe, and Victor Veitch, [“The Linear Representation Hypothesis and the Geometry of Large Language Models”](https://arxiv.org/abs/2311.03658), ICML 2024.
- Joshua Engels et al., [“Not All Language Model Features Are Linear”](https://arxiv.org/abs/2405.14860), 2024.
- Gaël Gendron et al., [“Large Language Models Are Not Strong Abstract Reasoners”](https://www.ijcai.org/proceedings/2024/693), IJCAI 2024.

Research result:

The positive papers show that particular trained models can contain internal variables corresponding to board state, spatial/temporal coordinates, or interpretable concept geometries, sometimes supported by intervention rather than probe accuracy alone. Engels et al. complicate the simple linear-feature story with multidimensional/circular representations. Gendron et al. provide a behavioral counterweight: success on language tasks does not imply robust generalization on novel abstract reasoning benchmarks.

Editorial result:

The articles do not use this literature to claim that a model internally implements category theory. They say only that models learn nontrivial internal representations and that the organization of those representations is still an active research area.

### 5.4 Representation and decomposition at the model interface

Primary sources:

- Maxwell Nye et al., [“Show Your Work: Scratchpads for Intermediate Computation with Language Models”](https://arxiv.org/abs/2112.00114), 2021.
- Denny Zhou et al., [“Least-to-Most Prompting Enables Complex Reasoning in Large Language Models”](https://arxiv.org/abs/2205.10625), 2022.
- Wenhu Chen et al., [“Program of Thoughts Prompting”](https://arxiv.org/abs/2211.12588), 2022.
- Luyu Gao et al., [“PAL: Program-aided Language Models”](https://arxiv.org/abs/2211.10435), ICML 2023.

Research result:

These works show, in different settings, that external intermediate steps, decomposition, or executable programs can improve task performance. They do **not** directly test the article’s exact claim that naming a mathematical structure improves code generation.

Editorial result:

The papers are cited only for the broader point that representation and decomposition affect tractability. The proposed prompt experiment below is the proper way to test the narrower claim.

### 5.5 LLMs as mathematics tutors

Primary studies:

- Zachary A. Pardos and Shreya Bhandari, [“ChatGPT-generated help produces learning gains equivalent to human tutor-authored help on mathematics skills”](https://doi.org/10.1371/journal.pone.0304013), *PLOS ONE*, 2024.
- Yuyang Ding et al., [“Boosting Large Language Models with Socratic Method for Conversational Mathematics Teaching”](https://doi.org/10.1145/3627673.3679881), CIKM 2024.
- Rose E. Wang et al., [“Tutor CoPilot: A Human-AI Approach for Scaling Real-Time Expertise”](https://arxiv.org/abs/2410.03017), 2024.

Research result:

- Pardos and Bhandari found learning gains from generated hints in their study, but the initial generated help failed quality checks on 32% of problems. Mitigation reduced the failure rate substantially.
- Ding et al. explicitly identify answer dumping and reliability as problems and evaluate a more structured Socratic tutoring approach.
- Tutor CoPilot is evidence for a human-in-the-loop pattern: generated guidance helped tutors in a randomized field trial, while the paper still reports limitations such as suggestions that were not grade-level appropriate.

Editorial result:

Article 2 presents the LLM as an elevator between representations, not the foundation of mathematical truth. It recommends artifacts that can be independently rejected: executable examples, property tests, primary definitions, and proof-checker output.

### 5.6 Proof checking

Primary/current documentation:

- [Theorem Proving in Lean 4](https://lean-lang.org/theorem_proving_in_lean4/)
- [Lean Language Reference](https://lean-lang.org/doc/reference/latest/)

Editorial result:

The article says Lean’s kernel checks proof terms, but it also states the specification problem: a checker can validate the formal statement while the statement still fails to represent the real requirement.

## 6. Experiments

All experiment files are in [`./experiments/`](./experiments/).

Drafting environment:

```text
Linux/x64
Node v22.16.0
V8 12.4.254.21-node.26
Python 3.13.5
```

### 6.1 Map-fusion microbenchmark

Files:

- [`experiments/map_fusion_benchmark.mjs`](./experiments/map_fusion_benchmark.mjs)
- [`experiments/map_fusion_benchmark_output.json`](./experiments/map_fusion_benchmark_output.json)

Question:

> For an ordinary JavaScript array and four pure numeric transformations, does composing the transformations and mapping once preserve output and reduce runtime in this environment?

Compared programs:

```js
function fourMaps(input) {
  return input
    .map(addTax)
    .map(convertCurrency)
    .map(roundCents)
    .map(addFee);
}

function oneMap(input) {
  return input.map(x => addFee(roundCents(convertCurrency(addTax(x)))));
}
```

Method:

- 500,000-element ordinary array.
- Four deterministic, pure numeric functions.
- Full element-by-element equality check before timing.
- Eight warm-up iterations.
- Twenty measured iterations per implementation.
- Execution order alternated by round to reduce systematic first/second bias.
- Explicit garbage collection between measured runs (`node --expose-gc`).
- A sampled checksum consumed the outputs.

Observed result:

```json
{
  "four_maps": {
    "median_ms": 63.13464349999981,
    "min_ms": 61.01162699999986,
    "max_ms": 74.2826540000001
  },
  "one_map": {
    "median_ms": 16.062125499999865,
    "min_ms": 15.6283269999999,
    "max_ms": 17.883659999999963
  },
  "median_speedup": 3.9306531069004746,
  "outputs_equal": true
}
```

Interpretation used in Article 1:

- The output-equivalence claim holds for these pure functions and data.
- The fused implementation had a 3.93× lower median runtime in this environment.
- The more portable structural observation is that four `map` calls create four result arrays and make four passes, while one call creates one result array and makes one pass.
- The experiment does not support “map fusion is always 4× faster”, much less the transcript’s casual “hundred times” implication.
- JIT state, garbage collection, callback cost, data type, array shape, engine, and surrounding code can change the ratio.

### 6.2 Law checks and counterexamples

Files:

- [`experiments/law_checks.mjs`](./experiments/law_checks.mjs)
- [`experiments/law_checks_output.json`](./experiments/law_checks_output.json)

The script uses a fixed `0xC0FFEE` seed and no dependencies. It is intentionally smaller than a real property-testing framework; the purpose is to make the draft’s examples executable.

Checks:

1. Array mapping identity:

```text
xs.map(identity) = xs
```

2. Array mapping composition for generated integer arrays and generated affine integer functions:

```text
xs.map(f).map(g) = xs.map(x => g(f(x)))
```

3. Idempotence of a string normalizer:

```text
normalize(normalize(x)) = normalize(x)
```

4. Non-associativity of binary average.
5. Difference in observable effect ordering between separate and fused maps.

Observed result:

```json
{
  "checks": {
    "array_functor_identity": { "cases": 10000, "passed": true },
    "array_functor_composition": { "cases": 10000, "passed": true },
    "normalization_idempotence": { "cases": 10000, "passed": true }
  },
  "non_associative_average_counterexample": {
    "values": [0, 0, 10],
    "left": 5,
    "right": 2.5
  },
  "side_effect_ordering_counterexample": {
    "separate_maps_trace": ["f1", "f2", "f3", "g2", "g3", "g4"],
    "fused_map_trace": ["f1", "g2", "f2", "g3", "f3", "g4"],
    "same_trace": false
  }
}
```

Interpretation used in the articles:

- The passing randomized checks illustrate the laws; they do not prove them for all JavaScript values and functions.
- The average example is a compact demonstration that a plausible binary operation can fail associativity.
- The trace is evidence that “compose and map once” requires an effect/purity qualification. Both versions can return the same values while performing side effects in different orders.

### 6.3 Proposed LLM spray test — not run

The core empirical claim of Article 1 deserves a controlled model experiment:

> Does naming a correct mathematical structure reduce output variance and improve invariant satisfaction relative to a semantically equivalent ordinary-language prompt?

No controlled independent LLM harness was available during drafting. Running a few generations through the same authoring model and reporting them as evidence would be contaminated and misleading. Therefore no result is claimed.

A publishable experiment could use the following protocol.

#### Tasks

1. **Idempotent normalizer:** Implement a canonicalizer that is stable on repeated application.
2. **Associative aggregation:** Combine shard-level statistics without changing results under regrouping.
3. **Explicit state machine:** Replace interacting booleans with states and guarded transitions.
4. **Functor-like mapping:** Add a representation-preserving `map` to `Tree<T>` and test identity/composition.
5. **Map fusion:** Refactor repeated pure element-wise passes while preserving behavior.

#### Prompt conditions

- **A — vague:** Ordinary request such as “simplify”, “make safe to retry”, or “clean up the state handling”.
- **B — structure-named:** Same requirements plus the correct term and explicit laws.
- **C — law-only ordinary language:** State the laws without the mathematical noun. This distinguishes vocabulary compression from the information content of the law itself.
- **D — wrong abstraction control:** Supply a plausible but incorrect mathematical label. This measures the cost of confident misclassification.

#### Controls

- Fixed model snapshot, system prompt, tools, repository state, and harness.
- New context for every run.
- At least 20–30 runs per condition/task.
- Fixed sampling parameters where the provider exposes them.
- Blind evaluation of outputs without showing evaluators the prompt condition.

#### Measures

- Hidden test pass rate.
- Explicit invariant/property pass rate.
- Number of distinct architecture families produced.
- Lines/files changed.
- Unrequested abstractions introduced.
- Correction turns required.
- Output token count.
- Cross-run structural variance.
- Whether the model notices when the supplied abstraction is false.

#### Expected informative outcomes

- If B outperforms A but not C, the advantage comes mainly from explicitly stating the laws, not from the noun.
- If B is shorter and as reliable as C, the mathematical term is functioning as compression.
- If D strongly degrades results, the experiment supports the article’s warning that a wrong abstraction is a compressed bug.
- If results vary by model family, the term may be anchored differently across training corpora and instruction tuning.

## 7. Drafting and revision record

### Pass 0 — Extract the claims

The transcript was reduced to four claim clusters:

1. Models transform between representations.
2. Abstract mathematics names reusable structures.
3. Naming structures can improve prompts and code.
4. LLMs can help a learner move among representations.

The first three form Article 1. The fourth forms Article 2.

### Pass 1 — Replace the abstract opening

Rejected opening:

> Category theory is about describing something purely through its relationships...

Reason:

- It requires readers to accept a difficult abstraction before seeing why it matters.
- It repeats a loose definition that then needs correction.
- It does not match the strongest pattern in the existing blog: concrete artifact first.

Chosen opening:

- Four repeated price-transformation loops.
- A vague “Simplify this” prompt.
- A structure-aware prompt.
- A direct claim: the second prompt names the shape.

### Pass 2 — Identify the new contribution relative to existing posts

The blog already argues that:

- every word in a prompt is load-bearing;
- notation determines tractability;
- LLMs inherit patterns and complexity;
- the human bottleneck is selecting the right representation.

Therefore “notations matter” was not enough. The new contribution had to be:

> Abstract mathematical terms are unusually dense vocabulary because they imply operations **and laws**, and those laws can be turned into tests.

This line became the organizing distinction:

> Ordinary words summon examples. Mathematical words summon examples plus laws.

### Pass 3 — Fact-check the mathematical vocabulary

Definitions were checked against Riehl before the examples were finalized.

Concrete changes:

- “map is a functor” became “mapping is the operation through which the functor acts on functions” in the notes and a simpler lawful-mapping intuition in the body.
- List-to-tree conversion was explicitly identified as not automatically natural.
- A bare type was not called a monoid.
- Category composition was distinguished from generic relation transitivity.
- Array equality was described extensionally (same elements), not by object identity.

### Pass 4 — Choose a worked example for Article 2

Candidates considered:

- string/list concatenation as a monoid;
- idempotent normalization;
- functor mapping over array/tree;
- average aggregation.

Chosen example: **binary average fails associativity; carry sum and count instead.**

Reasons:

- The counterexample is tiny and calculable by almost any reader.
- It demonstrates a law, a failure, a representation change, and a production concern (parallel aggregation).
- It shows abstract mathematics changing an API rather than merely renaming code.
- It naturally introduces semigroup/monoid without requiring category theory first.
- It creates a useful floating-point caveat, showing the difference between mathematical and machine semantics.

### Pass 5 — Run experiments before retaining performance language

The benchmark was run because the transcript made a concrete performance claim. The result supported the direction but not the magnitude.

Draft consequence:

- No universal speed claim.
- Exact environment and medians moved to a footnote.
- Main text emphasizes traversal/allocation and purity assumptions.
- The side-effect trace was added so the optimization does not read as unconditional.

### Pass 6 — Separate internal-mechanism claims from interface claims

The latent-space material was divided into:

- **Evidence:** particular models learn interpretable, decodable, and sometimes causally useful internal representations.
- **Speculation:** these may support cross-domain abstractions in ways analogous to mathematical structure.
- **Unsupported leap:** the model has a category-theoretic common latent object.
- **Article claim:** naming structure at the interface changes the requested transformation and often gives better constraints/tests.

Only the last claim is necessary for the article.

### Pass 7 — Preserve voice without preserving transcription noise

Edits used to maintain voice:

- Retained blunt lines such as “a wrong abstraction is an aggressively compressed bug.”
- Used the enterprise `PriceTransformationPipeline` joke and skepticism toward `reduce`/Haskell culture.
- Kept admissions of ignorance and self-correction.
- Used code and concrete prompts as the primary explanatory medium.
- Allowed long paragraphs where the causal argument benefited.

Edits made for readability:

- Removed spoken repetition and filler.
- Split several tangents into separate headings.
- Reduced repeated explanations of category theory.
- Kept profanity sparse enough that it has force.

### Pass 8 — Build the verification hierarchy in Article 2

The second article initially risked becoming a generic “AI tutor” post. To keep it specific to programming and abstract math, it was organized around artifacts:

```text
explanation
→ examples
→ counterexample search
→ property tests
→ primary source
→ proof checker
```

The model is useful because it translates between these artifacts. Authority moves outward to execution, sources, and formal checking.

### Pass 9 — Citation pass

Citation rules used:

- Primary mathematical texts for definitions.
- Original or venue-hosted research papers for empirical claims.
- Official current documentation for Lean and `fast-check`.
- Footnotes in the articles to preserve the blog’s conversational flow.
- Full source commentary in this log.

No research paper is cited as directly proving the central prompt claim. The articles say explicitly where the evidence is adjacent rather than direct.

## 8. Rejected titles and structures

### Article 1 title alternatives

- **Category Theory for People Who Prompt Computers** — memorable, but overpromises category theory and may repel readers before the concrete claim appears.
- **Mathematical Words Are Tiny Programs** — strong future essay title, but narrower than the article’s structure/test argument.
- **The Abstraction Budget** — useful concept, but would require a different article centered on multi-stage task decomposition.
- **Abstract Math as Prompt Compression** — accurate but less active and less voice-driven.

Chosen: **The Right Abstraction Is a Better Prompt**.

### Article 2 title alternatives

- **Math Without Numbers** — elegant, but understates the LLM learning method.
- **The Abstraction Elevator** — captures the metaphor but loses the personal contradiction.
- **How I Use an Unreliable Machine to Learn Exact Things** — accurate and voice-compatible, but long.

Chosen: **I Failed Calculus. LLMs Taught Me Math Anyway**.

### Rejected combined structure

A single article would have required this sequence:

```text
personal history
→ category theory
→ LLM internals
→ prompting
→ functors
→ map fusion
→ testing
→ tutoring workflow
→ verification
```

The main programming claim would arrive too late, and the learning method would read as an appendix. The transcript’s own “maybe this is enough for a first article” comment supports the split.

## 9. Claims intentionally phrased with uncertainty

The drafts use explicit uncertainty in three places:

1. **Model internals:** evidence of representations does not specify a universal ontology.
2. **Performance:** a local benchmark is not a portable law.
3. **Tutoring effectiveness:** studies show promise under particular conditions while also documenting quality failures and the value of human oversight.

This is not rhetorical hedging. These are boundaries in the evidence.

## 10. Suggested publication work before posting

1. **Verify autobiographical wording.** Confirm whether “dropped out partly because” matches the intended causal emphasis and whether “a couple of months ago” should remain time-relative.
2. **Rerun the benchmark locally** if the article will use first-person language around it. The draft currently says it was “run for this draft” and gives the drafting container, avoiding false attribution.
3. **Run the TypeScript snippets in the target project setup.** The snippets were reviewed for consistency, but the `fast-check` examples were not executed in this container because the package was not installed. The API usage follows current official documentation.
4. **Decide citation density.** The footnotes are deliberately heavier than existing GO GO GOLEMS posts because the topic mixes mathematics, mechanistic interpretation, and education research. They can be shortened for publication while keeping this log as the full evidence file.
5. **Consider two illustrations.** A ladder diagram for Article 2 and a “vague prompt versus structure-aware prompt” transformation diagram for Article 1 would add value. A functor diagram is useful only if it remains simpler than the prose.
6. **Run the proposed spray test** before making a strong empirical claim that mathematical vocabulary lowers cross-run variance. The present articles frame this primarily as an engineering method and hypothesis grounded in examples.
7. **Check internal links.** Article 1 naturally links to the posts on prompt engineering, simplicity, slowing down, and diaries.

## 11. Bibliography and source index

### Source transcript

- Manuel Odendahl, “LLMs and Abstract Math”, private recorded note, note ID `0cb27c2c-383d-4db0-b805-98a7b5443efc`, recorded 2026-08-02.

### GO GO GOLEMS style and continuity

- Manuel Odendahl, [“Simplicity in the age of AI-assisted coding”](https://gogogolems.substack.com/p/simplicity-in-the-age-of-ai-assisted), 2026-03-15.
- Manuel Odendahl, [“Slowing Down in the Age of Coding Agents”](https://gogogolems.substack.com/p/slowing-down-in-the-age-of-coding), 2026-03-21.
- Manuel Odendahl, [“Why I Make My Agents Keep Diaries”](https://gogogolems.substack.com/p/why-i-make-my-agents-keep-diaries), 2026-03-24.
- Manuel Odendahl, [“From ‘prompt and pray’ to prompt engineering”](https://gogogolems.substack.com/p/from-prompt-and-pray-to-prompt-engineering), 2026-04-07.

### Mathematics and property-based testing

- Emily Riehl, [*Category Theory in Context*](https://emilyriehl.github.io/files/context.pdf), Dover, 2016.
- Koen Claessen and John Hughes, [“QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs”](https://dl.acm.org/doi/10.1145/351240.351266), ICFP 2000.
- John Hughes, [“How to Specify It! A Guide to Writing Properties of Pure Functions”](https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf), TFP 2019/2020.
- [fast-check documentation: “What is Property-Based Testing?”](https://fast-check.dev/docs/introduction/what-is-property-based-testing/), accessed 2026-08-02.
- [ECMAScript Language Specification: `Array.prototype.map`](https://tc39.es/ecma262/multipage/indexed-collections.html), accessed 2026-08-02.
- [Theorem Proving in Lean 4](https://lean-lang.org/theorem_proving_in_lean4/), accessed 2026-08-02.
- [Lean Language Reference](https://lean-lang.org/doc/reference/latest/), accessed 2026-08-02.

### LLM representations and abstract reasoning

- Kenneth Li, Aspen K. Hopkins, David Bau, Fernanda Viégas, Hanspeter Pfister, and Martin Wattenberg, [“Emergent World Representations: Exploring a Sequence Model Trained on a Synthetic Task”](https://openreview.net/forum?id=DeG07_TcZvT), ICLR 2023.
- Wes Gurnee and Max Tegmark, [“Language Models Represent Space and Time”](https://arxiv.org/abs/2310.02207), 2023/2024.
- Kiho Park, Yo Joong Choe, and Victor Veitch, [“The Linear Representation Hypothesis and the Geometry of Large Language Models”](https://arxiv.org/abs/2311.03658), ICML 2024.
- Joshua Engels, Isaac Liao, Eric J. Michaud, Wes Gurnee, and Max Tegmark, [“Not All Language Model Features Are Linear”](https://arxiv.org/abs/2405.14860), 2024.
- Gaël Gendron, Qiming Bao, Michael Witbrock, and Gillian Dobbie, [“Large Language Models Are Not Strong Abstract Reasoners”](https://www.ijcai.org/proceedings/2024/693), IJCAI 2024.

### Representation and prompting

- Maxwell Nye et al., [“Show Your Work: Scratchpads for Intermediate Computation with Language Models”](https://arxiv.org/abs/2112.00114), 2021.
- Denny Zhou et al., [“Least-to-Most Prompting Enables Complex Reasoning in Large Language Models”](https://arxiv.org/abs/2205.10625), 2022.
- Wenhu Chen et al., [“Program of Thoughts Prompting: Disentangling Computation from Reasoning for Numerical Reasoning Tasks”](https://arxiv.org/abs/2211.12588), 2022.
- Luyu Gao et al., [“PAL: Program-aided Language Models”](https://arxiv.org/abs/2211.10435), ICML 2023.

### Mathematics tutoring

- Zachary A. Pardos and Shreya Bhandari, [“ChatGPT-generated help produces learning gains equivalent to human tutor-authored help on mathematics skills”](https://doi.org/10.1371/journal.pone.0304013), *PLOS ONE* 19(5), 2024.
- Yuyang Ding, Hanglei Hu, Jie Zhou, Qin Chen, Bo Jiang, and Liang He, [“Boosting Large Language Models with Socratic Method for Conversational Mathematics Teaching”](https://doi.org/10.1145/3627673.3679881), CIKM 2024.
- Rose E. Wang, Ana T. Ribeiro, Carly D. Robinson, Susanna Loeb, and Dora Demszky, [“Tutor CoPilot: A Human-AI Approach for Scaling Real-Time Expertise”](https://arxiv.org/abs/2410.03017), 2024.

## 12. Final editorial assessment

The two drafts now make different promises:

- Article 1 gives developers a practical reason to learn mathematical vocabulary: it can compress prompts, improve composition, and generate tests.
- Article 2 gives technically minded readers a practical way to learn the vocabulary without trusting the model that teaches it.

They meet in one principle:

> The useful work is choosing a representation in which the next transformation becomes explicit and checkable.

That principle is grounded in the transcript, continuous with the existing blog, technically narrowed where the recording was handwavy, and supported by executable examples rather than a claim that the model contains a miniature mathematician.
