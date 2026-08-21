# Track topos + LLM papers

- URL: https://chatgpt.com/c/6a8475fc-4e9c-83ea-82b3-c30a22b4fecd
- Created: 2026-08-18T15:10:55.728Z

---

> Chinese telecoms giant Huawei believes his esoteric concept of the topos could be key to building the next generation of AI, and has hired Fields medal-winner Laurent Lafforgue to explore this subject.
>
> ---
>
> tell me more about that

The “topos” here is almost certainly **Alexander Grothendieck’s** notion from modern geometry, not a standard AI technique. I’ll separate what Huawei/Lafforgue are actually reported to be doing from the more speculative claim that this could underpin a new AI architecture.

```json
{"system1_search_query":[{"q":"Huawei Laurent Lafforgue topos artificial intelligence Grothendieck Huawei AI"},{"q":"\"Laurent Lafforgue\" Huawei topos AI"},{"q":"Huawei Fields medal Laurent Lafforgue topos research artificial intelligence"},{"q":"Grothendieck topos artificial intelligence Huawei Lafforgue"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Explaining the connection**

I’m connecting the mathematician’s background, Huawei’s research context, and his critique of today’s AI. The key idea is that topos theory could provide structured semantics beyond statistical pattern matching.

**Explained the connection**

**Clarifying the mathematical bridge**

I’m framing topos theory as both generalized geometry and logic. The AI analogy is conceptual, not an established implementation: local information can be organized, related, and combined while preserving explicit meaning.

**Clarified the mathematical bridge**

**Searched 23 websites**

</details>

The “his” in that sentence is **Alexander Grothendieck**. And the Huawei story is real, although “topos could be the key to next-generation AI” is a much stronger claim than anything demonstrated so far.

Huawei began discussions with French mathematician **Laurent Lafforgue** in 2017, funded a two-year topos-theory project, created a Huawei algebraic-geometry chair at IHÉS in 2019, and hired Lafforgue directly into Huawei Technologies France in September 2021. Huawei explicitly said his work would concern Grothendieck toposes and their possible applications, with the research being published openly. Lafforgue's current homepage still lists Huawei Technologies France. citeturn135105view3turn808295view5turn580410search0

### What on earth is a topos?

Grothendieck invented the concept in the 1960s while rebuilding the foundations of algebraic geometry. It is not fringe mathematics: topos theory became a major part of category theory, geometry and mathematical logic. A 2025 introduction by Lafforgue and Olivia Caramello describes it as a framework unifying **geometry, topology, algebra and logic**. citeturn992170view0

The intuitive route is through **sheaves**.

Imagine you're trying to describe the weather over Europe. You don't have one gigantic observation of all of Europe. Instead, you have information defined locally:

Paris → temperature, humidity  
London → temperature, humidity  
Berlin → temperature, humidity  
etc.

When two regions overlap, their descriptions have to agree. A **sheaf** is, very roughly, a mathematical mechanism for saying:

> here are many pieces of locally valid information, together with rules for when those pieces can be consistently glued into a global description.

A **topos** is essentially an entire mathematical universe of such sheaves.

Grothendieck discovered that you can treat these universes almost as if they were spaces themselves. Much later, mathematicians recognized an extraordinary second interpretation: a topos can also behave like **a universe of logical propositions and models**. Caramello and Lafforgue describe this duality as one in which spaces can become categories of sheaves while formal theories can be represented by associated “classifying toposes.” citeturn992170view0turn992170view4

That geometry–logic duality is the part that makes people think about AI.

### Why Lafforgue thinks this matters for AI

Lafforgue's starting criticism of conventional machine learning is fairly radical.

A photograph is normally handed to a neural network as millions of numbers. A sentence becomes token IDs and eventually vectors containing thousands of floating-point coordinates. The network learns transformations between these numerical representations.

Lafforgue argues that the **meaning isn't explicit in those numbers**. In his 2022 presentation he complains that when real-world information is reduced to pixels or numerical vectors, its meaning disappears from the representation; most points in the enormous vector space don't represent anything meaningful at all. citeturn135105view0

He wants to ask a different question:

**What if the computer manipulated mathematical objects that already carry their structural/semantic relationships, instead of turning everything immediately into giant arrays of numbers?**

His 2024 presentation frames AI around two problems: finding formal languages suited to describing things such as images or texts, and then transforming information from one such language into another. He proposes representing individual pieces of data using **subtoposes**, which simultaneously admit geometric and logical interpretations, and processing them through chains of toposes corresponding to successive formal languages. He explicitly calls this a possible form of “topossic deep learning.” citeturn808295view4

So you can contrast the philosophies approximately like this:

**Today's neural AI**

`image → pixels → vectors → neural-network layers → vectors → "cat"`

**Lafforgue's speculative direction**

`image → structured mathematical description → logical/geometric object → meaning-preserving transformations → "cat"`

The second diagram is an intuition, not an implemented Huawei architecture.

### What Huawei sees in it

There are several fairly concrete research directions behind the grand rhetoric:

- **Invariant perception.** Huawei has publicly discussed with Lafforgue whether objects could be represented geometrically rather than primarily through pixels, potentially making recognition less sensitive to illumination, viewpoint and other irrelevant changes. citeturn135105view2
- **Automated reasoning and theorem proving.** Huawei says it has been investigating topos theory for category proving, congruence reasoning and automated theorem derivation, with the hope of improving formal verification and problems such as state-space explosion. citeturn229165search2
- **Explicit semantics.** Because the same topos can correspond to different formal theories, ideas from Caramello's “toposes as bridges” program potentially provide machinery for translating between different descriptions of the same underlying structure. Lafforgue has proposed trying to automate this bridge technique. citeturn808295view4
- **A mathematical model of induction.** Lafforgue has sketched ways in which examples could determine a common formal theory, turning “learning from examples” into operations on subtoposes rather than merely optimization of neural-network weights. citeturn808295view4

The particularly striking mathematical fact is that **logical proof can sometimes be translated into a geometric/topological problem**. Lafforgue and Caramello's recent work develops procedures translating first-order provability questions into the generation of Grothendieck topologies. citeturn992170view4

You can see why a computer company might find that tantalizing: reasoning becomes geometry, geometry can sometimes be computed, and different representations of the same underlying object can be translated through a common invariant.

### Is this actually a competitor to transformers?

Not presently.

From the public work I found, this remains overwhelmingly **foundational research**. Lafforgue's September 2024 presentation says that implementation of one component, “topology computing,” had begun at Huawei's Lagrange Center with researcher Anthony Bordg. But the same presentation is still phrased in terms such as “project,” “proposition,” and “looking for some topossic deep learning.” citeturn808295view4

I did not find a public Huawei model showing, for example,

`ToposNet beats a Transformer on ImageNet using 1/20 the data`

or anything remotely that mature.

Indeed, Lafforgue and Caramello were still publishing hundreds of pages of foundational topos theory in 2025, including work on the relationship between topology, logic and provability. citeturn992170view0turn992170view4

So this is better understood as a **20-year-style research bet** than as Huawei having secretly discovered the successor to the transformer.

### What makes the idea genuinely interesting

It attacks one of the deepest unresolved questions in AI.

Modern AI has become extraordinarily good at **learning statistical representations of meaning** without having an explicit mathematical theory of what “meaning” is.

Grothendieck's machinery happens to sit at an unusual intersection:

**geometry ↔ local/global structure ↔ symmetry ↔ logic ↔ semantics**

That is almost uncannily close to a wish list for a mathematical theory of intelligence.

The bet Lafforgue is exploring is essentially:

> Maybe intelligence shouldn't ultimately be modeled as gigantic functions between vector spaces. Maybe it should be modeled as transformations between structured mathematical worlds.

That is a very different vision from scaling today's LLMs.

And there is a historical irony here: **Grothendieck invented toposes to solve extremely abstract problems in pure mathematics, with no conceivable connection to artificial intelligence at the time.** Sixty years later, Huawei is paying a Fields medalist to investigate whether precisely that abstraction might provide a mathematical language for machines that reason about meaning.

If you're interested, the next useful thing to unpack is **one concrete example of how you could represent an image using sheaves/toposes instead of a pixel vector**. That makes Lafforgue's proposal much less mysterious.


---

> I am very curious about framing LLMs in a similar manner than:
>
> `image → structured mathematical description → logical/geometric object → meaning-preserving transformations → "cat"`

For LLMs, the analogous move is to stop treating a sentence primarily as a sequence of vectors and instead treat it as a **network of locally compatible claims, entities, relations, and contexts**. Then generation becomes a transformation of that structured object rather than only next-token prediction.

```json
{"system2_search_query":[{"q":"site:arxiv.org topos theory language semantics sheaf category theory LLM"},{"q":"site:arxiv.org categorical compositional distributional semantics language category theory DisCoCat"},{"q":"site:laurentlafforgue.org topos AI language text formal language 2024"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Mapping language structures**

I’m relating text to local semantic contexts, compatible interpretations, and global coherent meanings. I’ll distinguish today’s transformer-based approximation from a more explicit topos-style architecture using categorical maps for inference and translation.

**Mapped language structures**

**Searched 3 websites**

</details>

There is a useful distinction here: **(1) reinterpret today’s transformer mathematically**, versus **(2) build a different language model whose latent state is explicitly semantic/topological**. The second is the more interesting analogue of your image pipeline.

<details><summary>💭 Thinking</summary>

**Formalizing a semantic pipeline**

I’m shaping this as a compiler-like model: text becomes contextual interpretations, compatible local meanings assemble globally, internal logic supports reasoning, and structure-preserving maps transform results before linguistic realization.

**Formalized a semantic pipeline**

</details>

Yes. A fairly clean “topos-flavored LLM” analogue would be:

$$
\boxed{
\text{text}
\rightarrow
\text{local semantic descriptions}
\rightarrow
\text{sheaf of contextual meanings}
\rightarrow
\text{global logical/geometric object}
\rightarrow
\text{structure-preserving transformations}
\rightarrow
\text{text}
}
$$

That is substantially different from how an ordinary transformer is organized.

Today, crudely:

```text
"The trophy doesn't fit in the suitcase because it is too big."

        ↓ tokenize

[tokens]

        ↓ embedding

[v₁, v₂, ..., vₙ] ∈ ℝᵈ

        ↓ transformer

[h₁, h₂, ..., hₙ]

        ↓ next-token probabilities

answer
```

The model may internally encode entities, syntax, causality and coreference, but **none of those things is an explicit mathematical object that the architecture is required to preserve**.

A topos-inspired architecture could instead make that structure first-class.

### 1. Text → local semantic descriptions

Take:

> The trophy doesn't fit in the suitcase because it is too big.

Instead of immediately saying “this is 15 vectors,” construct local descriptions:

```text
objects:
    trophy
    suitcase

relations:
    fit(trophy, suitcase) = false

property:
    big(?)

causal relation:
    big(?) → not_fit(trophy, suitcase)

possible referents:
    ? ∈ {trophy, suitcase}
```

These need not be traditional symbolic-logic expressions. They could themselves contain embeddings, probability distributions, types, graphs, programs, etc.

The key change is that **the model knows what kind of thing each representation represents**.

Lafforgue explicitly frames AI this way: first find an appropriate *formal language* in which to describe some aspect of reality, and then study transformations between such languages. He specifically cites LLMs as transformations of human-language text into high-dimensional vector languages. citeturn223430search10turn223430search12

---

## 2. Local meanings → a sheaf

This is where things become interesting.

Imagine every fragment of the discourse has its own set of possible interpretations.

For example:

```text
Context A:
"The trophy doesn't fit in the suitcase"

Possible meaning:
    not_fit(trophy, suitcase)
```

Another context:

```text
Context B:
"it is too big"

Possible meanings:
    big(trophy)
    big(suitcase)
```

And a larger context:

```text
Context C:
"The trophy doesn't fit in the suitcase because it is too big."
```

A **presheaf** can associate possible semantic states with each context and provide restriction maps telling us how an interpretation of a larger context must look when restricted to a smaller one.

Schematically:

```text
             whole sentence
                   │
          ┌────────┴────────┐
          ↓                 ↓
 "trophy doesn't fit"   "it is too big"
          │                 │
          ↓                 ↓
       trophy             "it"
       suitcase         {trophy,
                         suitcase}
```

Then the sheaf condition asks:

> Can these locally valid interpretations be glued together into one globally coherent interpretation?

In this example, world knowledge and the causal construction favor

```text
it = trophy
```

and therefore:

```text
trophy:
    big
    does_not_fit_in → suitcase
```

rather than:

```text
suitcase:
    big
```

This isn't merely a metaphor. Abramsky and Sadrzadeh developed a sheaf-theoretic formulation of natural-language semantics in which local meanings of discourse fragments are glued into global interpretations, including examples involving anaphora resolution. citeturn760492academia29

So one could reinterpret **context understanding itself as a gluing problem**.

---

# 3. Meaning becomes something like a global section

This gives us a very different notion of an LLM's “latent state.”

Current transformer:

$$
\text{meaning} \approx (h_1,\ldots,h_n)
$$

where $h_i$ are learned vectors.

Topos/sheaf model:

$$
\text{meaning} \approx
\text{a globally compatible family of local semantic states}.
$$

Or, in sheaf terminology, something resembling a **global section**.

This is conceptually powerful.

Consider a long document containing:

```text
Page 2:
Alice owns Acme.

Page 17:
Acme owns Beta Ltd.

Page 34:
She sold the company in 2019.

Page 51:
Beta remained an Acme subsidiary until 2021.
```

Each paragraph creates local semantic information.

The system attempts to glue these into:

```text
Alice
  │
  └── owns → Acme
                │
                └── owns → Beta Ltd
```

with appropriate temporal qualifications.

If some other paragraph says:

```text
Alice never owned Acme.
```

there may no longer be a consistent global section.

And that is extremely interesting for AI.

Instead of simply having:

```text
high probability of contradiction
```

you can potentially have:

```text
these two local semantic states
cannot be glued.
```

The inconsistency acquires an explicit mathematical location.

---

# 4. From a sheaf to a topos

A topos takes this idea considerably further.

Very loosely, instead of having one particular sheaf of information, you have an entire universe of objects whose information behaves according to these locality/gluing rules:

$$
\mathcal E = \mathbf{Sh}(C,J)
$$

where $C$ is some category of contexts and $J$ specifies which families of contexts constitute adequate covers.

The beautiful part is that $\mathcal E$ isn't merely geometric.

It has **internal logic**.

You can ask things like:

$$
\text{owns}(\mathrm{Alice},\mathrm{Acme})?
$$

or

$$
\exists x:\mathrm{Company},\quad
\mathrm{owns}(\mathrm{Alice},x)
$$

inside the semantic universe.

Thus you start getting something like:

```text
geometry of context
         ↕
logic of meaning
```

rather than separating “neural representation” and “reasoning engine.”

That geometry/logic duality is exactly part of what attracts Lafforgue to the subject. His proposed AI program goes further and considers pieces of information represented using subtoposes and transformations through successive formal languages/toposes. citeturn223430search10turn223430search11

---

# 5. Now replace neural layers with meaning-preserving transformations

This is perhaps the deepest change.

A transformer essentially computes:

$$
H_{k+1}=f_k(H_k).
$$

There's no intrinsic semantic interpretation of layer 19 versus layer 20.

Lafforgue points out precisely this “mysterious intermediate languages” aspect of deep learning. citeturn223430search12

A categorical version might instead have:

```text
natural language
      ↓
discourse representation
      ↓
event representation
      ↓
causal representation
      ↓
task-specific theory
      ↓
answer
```

with each arrow being some mathematically characterized transformation:

$$
\mathcal E_0
\longrightarrow
\mathcal E_1
\longrightarrow
\mathcal E_2
\longrightarrow
\cdots
\longrightarrow
\mathcal E_n.
$$

Depending on the formalization, those arrows could be functors, adjunctions, geometric morphisms, natural transformations, pullbacks/pushouts, etc.

Importantly, **not every categorical map automatically preserves “meaning.”** You would specify which structure needs to survive the transformation.

For example:

```text
English
"The dog chased the cat."

         ↓ semantic transformation

event representation
Chase(
    agent = dog,
    patient = cat
)

         ↓ translation

French semantic representation
Chasser(
    agent = chien,
    patient = chat
)

         ↓ linguistic realization

"Le chien a poursuivi le chat."
```

The surface form has changed completely.

But this diagram should commute:

```text
 English text ─────────────→ French text
      │                           │
      ↓                           ↓
 English semantics ───────→ French semantics
```

In category-theoretic language, **commuting diagrams** become an extremely natural way of expressing “different transformations preserve the same underlying semantic relation.”

Categorical approaches to compositional language semantics already exist independently of Lafforgue's program—most notably DisCoCat, which combines grammatical composition with distributional/vector semantics. citeturn223430academia6turn223430academia8

---

# 6. The most plausible architecture would actually be hybrid

I would not throw away transformers.

I'd do this:

```text
                     NEURAL
                       │
                       ▼
              ┌─────────────────┐
text ────────→│ semantic parser │
              └─────────────────┘
                       │
                       ▼
              local interpretations
                       │
                       ▼
              ┌─────────────────┐
              │ sheaf / topos   │
              │ semantic layer  │
              └─────────────────┘
                       │
             gluing / inference
             consistency / logic
             abstraction / analogy
                       │
                       ▼
              global semantic state
                       │
                       ▼
              ┌─────────────────┐
              │ neural decoder  │
              └─────────────────┘
                       │
                       ▼
                     text
```

The transformer would become **the perception and realization machinery**, rather than the entire cognition system.

It could learn things like:

```text
text
 ↓
candidate entities

text
 ↓
candidate predicates

text
 ↓
candidate restriction maps

text
 ↓
probabilities over local sections
```

Then the geometric layer would enforce compatibility.

Neural sheaf networks already demonstrate the more general idea that neural learning and sheaf structure can coexist: the sheaf supplies relational structure while learned parameters operate within that structure. citeturn760492academia30

---

## This produces an intriguing new interpretation of attention

You could even reinterpret attention.

Ordinary attention asks roughly:

$$
\text{How relevant is token }j\text{ to token }i?
$$

A semantic/sheaf architecture might instead ask:

$$
\text{How does information valid in context }U
\text{ restrict or transfer to context }V?
$$

So rather than:

```text
token ↔ token
```

you get something closer to:

```text
context
   │
   ├── entity structure
   ├── temporal structure
   ├── causal structure
   ├── speaker beliefs
   └── possible worlds

            ↕ compatibility maps

other context
```

That's richer than attention weights.

---

# And RAG becomes particularly interesting

Imagine a RAG system retrieves ten documents.

Currently:

```text
query
  ↓
embedding search
  ↓
10 chunks
  ↓
stuff chunks into context
  ↓
LLM generates answer
```

A sheaf-inspired RAG system could instead do:

```text
document A → local theory A ─┐
document B → local theory B ─┤
document C → local theory C ─┤
document D → local theory D ─┼→ GLUE
document E → local theory E ─┘
                              │
                         global theory
                              │
                    ┌─────────┴─────────┐
                    ↓                   ↓
              compatible facts     obstructions
                                  contradictions
                              │
                              ↓
                            answer
```

That would make **provenance and disagreement structural properties of the representation**, rather than text instructions saying “please pay attention to source conflicts.”

I think this is one of the most compelling possible applications of sheaf ideas to LLM systems.

---

## So I would rewrite your original pipeline as

For vision:

```text
image
→ structured mathematical description
→ logical/geometric object
→ meaning-preserving transformations
→ "cat"
```

For language:

```text
text
→ local contextual meanings
→ compatible semantic structure
→ sheaf / logical-geometric universe
→ inference + translation + abstraction
→ semantic result
→ text
```

Or, more compactly:

$$
\boxed{
\text{language}
\rightarrow
\text{meaning geometry}
\rightarrow
\text{reasoning}
\rightarrow
\text{meaning geometry}
\rightarrow
\text{language}
}
$$

And this suggests a rather profound alternative to the usual conception of an LLM.

An LLM currently learns approximately

$$
P(\text{next token}\mid\text{context}).
$$

A system along these lines would instead try to learn something more like

$$
P(\text{local semantic structure}\mid\text{observation})
$$

while **mathematical constraints determine which local structures can coexist globally**.

The neural network supplies uncertainty and induction.

The topos/sheaf machinery supplies **composition, locality, compatibility, and logic**.

That division of labor is, to me, the much more interesting interpretation of the Huawei/Lafforgue direction—not “replace matrix multiplication with obscure mathematics,” but **change the fundamental latent representation from points in vector space to structured worlds of mutually constrained meanings**.

There is now at least one explicit 2025 proposal titled *Topos Theory for Generative AI and LLMs*, which explores categorical constructions such as pullbacks, pushouts and subobject classifiers as components of generative architectures. It is exploratory rather than evidence of a competitive replacement for transformers. citeturn223430academia9turn760492search14

If you want to push this one step further, the really interesting exercise is to **design a toy “Topos-LLM” architecture**—define exactly what its contexts, stalks/sections, restriction maps, global sections, and decoder would be. At that point this goes from philosophical analogy to something close to an implementable research proposal.


---

> Search for [Olivia Caramello](https://arxiv.org/search/math?searchtype=author\&query=Caramello,+O), [Laurent Lafforgue](https://arxiv.org/search/math?searchtype=author\&query=Lafforgue,+L) and related work on this LLM stuff?

I’ll trace three buckets: work by **Caramello**, work by **Lafforgue**, and independent papers that explicitly connect **topos/sheaf/category theory to LLMs or generative AI**. I’ll also flag which items are foundational math versus actual AI-architecture proposals.

```json
{"system1_search_query":[{"q":"site:arxiv.org Caramello Lafforgue topos AI LLM"},{"q":"site:arxiv.org Olivia Caramello Laurent Lafforgue topos theory artificial intelligence"},{"q":"site:arxiv.org topos theory generative AI LLM"},{"q":"site:arxiv.org sheaf theory language models LLM semantics"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 7 websites**

</details>

A first pattern is already clear: **Caramello/Lafforgue themselves are not mainly publishing “LLM papers.”** Their joint arXiv work is building the topos/logical machinery; their AI program appears more directly in talks, notes, Huawei work, and Caramello’s recent “syntactic learning / relative toposes” program. The papers explicitly saying “LLM” are mostly by other authors building on that direction.

```json
{"system1_search_query":[{"q":"site:arxiv.org Olivia Caramello relative toposes artificial general intelligence syntactic learning"},{"q":"site:oliviacaramello.com \"Relative toposes\" \"artificial\" intelligence"},{"q":"site:aroundtoposes.com Olivia Caramello relative toposes AGI Raven ARC syntactic learning"},{"q":"site:arxiv.org Laurent Lafforgue artificial intelligence toposes future AI image representation"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Organizing sources**

I’m separating established topos-theoretic work from speculative LLM applications. The strongest references concern semantic structure, learning, and transformers, while direct large-language-model implementations remain largely exploratory.

**Organized sources**

</details>

```json
{"system2_search_query":[{"q":"site:arxiv.org Bottman Liu Richardson 2026 operadic consistency LLM companion paper"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Mapping related research**

I’m finding a fragmented but promising research stack: foundational topos theory, categorical learning, semantic charts, operadic reasoning, and transformer interpretations. I’m distinguishing published mechanisms from my own proposed synthesis.

**Mapped related research**

**Searched 3 websites**

</details>

Yes. I searched this fairly broadly, including Caramello’s and Lafforgue’s own sites and the newer arXiv literature. The interesting result is that the research program we were sketching **does exist**, but it is fragmented across several communities.

The closest synthesis I can give is:

$$
\boxed{
\text{text/data}
\to
\text{formal vocabulary + local theories}
\to
\text{subtoposes / semantic worlds}
\to
\text{geometric operations / gluing / proof}
\to
\text{invariant semantic state}
\to
\text{language}
}
$$

Caramello and Lafforgue are working mostly on the **middle mathematical machinery**. Other researchers are beginning to connect that machinery explicitly to transformers and LLMs.

## Caramello: much closer to our idea than I initially realized

Caramello's 2023 talk **“Syntactic learning via Topos Theory”** is probably the first thing I would read. Her proposal is that an AI system be supplied with a large formal vocabulary in which it can express concepts, while learning logical rules from data and potentially proposing new vocabulary when it discovers invariances. She explicitly contrasts this with learning only inside a particular numerical semantics. citeturn518370search6

Her architecture is approximately:

$$
T_0\subseteq T_1\subseteq T_2\subseteq\cdots
$$

where successive theories encode progressively richer knowledge. Through classifying-topos constructions, this becomes a corresponding sequence of **relative toposes**. She argues that putting explicit constraints into the logical formalism could reduce the parameter space the learner has to explore. citeturn536252view0turn518370search6

That is very close to what we were calling

```text
tokens
→ local semantic description
→ increasingly structured semantic worlds
→ reasoning
```

rather than

```text
tokens
→ ℝ^d
→ ℝ^d
→ ℝ^d
→ logits
```

Her 2024 **“Relative toposes and meta-learning”** develops this further: information is organized relative to previously acquired information, so learning can proceed through multiple abstraction levels. She describes chains of relative toposes with the bottom level corresponding to raw data and higher levels corresponding to increasingly structured knowledge. citeturn518370search3

And there is an especially relevant Caramello slide deck on **toposes and AI** where she explicitly discusses transformers from a sheaf/topos viewpoint. The idea sketched there is to model different local views by toposes and organize their combination through something like a stack of toposes, exploiting sheaf-like local-to-global compatibility rather than merely concatenating numerical observations. citeturn130143search22

By 2025, her **“Relative toposes for artificial general intelligence”** course was already discussing initial applications to Raven progressive matrices and ARC-type abstraction tasks. So the program has moved at least somewhat from pure philosophy toward toy reasoning problems. citeturn287934search3

## Lafforgue: the clearest version of the architecture we imagined

Lafforgue's February 2024 **“Some sketches for a topos-theoretic AI”** develops the relevant relationship

$$
\text{subtopos}
\longleftrightarrow
\text{quotient theory}.
$$

A subtopos can correspond to taking a formal theory and adding axioms—in other words, making its description more specific. citeturn447155search11

Then his September 2024 presentation becomes remarkably concrete. He proposes that, for a family of data, one construct a starting formal language $T$; individual pieces of data are represented by **subtoposes** of its classifying topos, hence by corresponding quotient theories. Those representations are then processed through **chains of toposes connecting successive formal languages**. citeturn447155search9

So Lafforgue is almost literally proposing:

```text
datum
    ↓
formal description
    ↓
subtopos / quotient theory
    ↓
topos-to-topos transformation
    ↓
new formal language
    ↓
new semantic representation
```

That is extremely close to the architecture you reacted to.

His publication list shows this becoming a sustained AI research program from 2022 onward: knowledge representations and toposes, image representation, probability measures as Grothendieck topologies, “Some sketches for a topos-theoretic AI,” syntactic learning, geometry of language elaboration, and related work. citeturn447155search0

## The major Caramello–Lafforgue result from 2025

This may ultimately be more important for AI than their talks.

Their 249-page **“Generation of Grothendieck topologies, provability and operations on subtoposes”** establishes constructive connections between:

$$
\boxed{\text{logical provability}\quad\leftrightarrow\quad
\text{generation of Grothendieck topologies}}
$$

and develops operations such as union, intersection, difference, pushforward and pullback of subtoposes. citeturn253465view0

That gives you a potential mathematical engine for manipulating semantic states.

Suppose an AI's current semantic state is represented by a theory $T$, or equivalently by some associated topos:

$$
T \leftrightarrow \mathcal E_T.
$$

Learning a new fact could produce a quotient theory

$$
T' = T+\{\text{new constraint}\},
$$

corresponding geometrically to

$$
\mathcal E_{T'}\hookrightarrow\mathcal E_T.
$$

Reasoning about whether

$$
T'\vdash\phi
$$

can then, in suitable circumstances, be translated into a **geometric/topological generation problem**. That last interpretation is my synthesis of how their mathematics could be used computationally; the provability/topology correspondence itself is precisely what their paper develops. citeturn253465view0

Their companion 611-page introduction from 2025 is useful background because it deliberately develops the reversible relationships

$$
\text{local}\leftrightarrow\text{global},\qquad
\text{syntax}\leftrightarrow\text{semantics},\qquad
\text{space}\leftrightarrow\text{theory}.
$$

Those dual viewpoints are exactly what an AI application would exploit. citeturn253465view1

---

## Then there is a separate, explicitly LLM-focused literature

Here is the landscape I found.

| Work | Core idea | How close to our proposed LLM? |
|---|---|---|
| **Abramsky & Sadrzadeh, _Semantic Unification_ (2014)** | Treat discourse semantics as local meanings glued into global meanings by sheaves. citeturn697572view0 | **Very close semantically**, predates LLMs |
| **Belfiore & Bennequin, _Topos and Stacks of Deep Neural Networks_ (2021/22)** | Places DNNs inside a canonical Grothendieck topos and connects network semantics, invariance and stacks. citeturn253465view4 | Foundational neural/topos theory |
| **Villani & McBurney, _The Topos of Transformer Networks_ (2024)** | Analyzes transformer expressivity via topos completion; argues transformers differ categorically from ordinary piecewise-linear networks. citeturn253465view2 | Directly about transformers, but analytical rather than a replacement architecture |
| **Huntsman, Robinson & Huntsman (2024)** | LLMs score local logical consistency; sheaf machinery combines those scores into global consistency information. citeturn253465view6 | **Very plausible hybrid architecture** |
| **Mahadevan, _GAIA_ (2024)** | Builds a categorical architecture for generative AI involving simplicial objects, Kan extensions, sheaves, topoi and categorical probability. citeturn890293view3 | Explicit alternative architecture, highly theoretical |
| **Mahadevan, _Topos Theory for Generative AI and LLMs_ (2025)** | Proposes LLM architectures composed with pullbacks, pushouts, equalizers, exponentials and subobject classifiers. citeturn697572view2 | **Most explicitly “topos-native LLM” paper I found** |
| **Mahadevan, _Categorical Homotopy Theory for LLMs_ (2025)** | Treats paraphrases as different arrows that should be identified through weak/homotopy equivalence. citeturn451391view1 | Directly attacks “same meaning, different surface form” |
| **Javidnia, _A Gauge Theory of Superposition_ (2026)** | Represents LLM features as a **sheaf atlas of local semantic charts**, with measurable gluing/transport obstructions. Tests it on Llama-3.2-3B. citeturn451391view0 | **Probably the most interesting empirical connection so far** |
| **Bottman & Richardson, _Operads for compositional reasoning in LLMs_ (2026)** | Formalizes decomposition of questions and recomposition of answers using operads. citeturn890293view1 | Not topos theory, but directly relevant to structure-preserving reasoning |

The last one is notable because it has actual empirical teeth. Its companion paper evaluates **operadic consistency** across twelve LLMs and four multi-hop QA datasets and reports very strong correlations between the categorical consistency measure and answer accuracy. citeturn796724academia0

---

# One paper jumped out at me: Javidnia 2026

This one is extremely close to the model we discussed.

Instead of assuming that an LLM has one global feature dictionary such as

$$
\text{feature }f_{1842}=\text{“legal obligation”},
$$

the paper proposes that semantic features may only make sense **locally in context**.

So you might have:

```text
context: contract law
    local semantic coordinate system A

context: casual conversation
    local semantic coordinate system B

context: mathematics
    local semantic coordinate system C
```

and maps telling you how representations translate where contexts overlap.

That is literally an **atlas** in the geometric sense.

The paper models these local charts using sheaf/gauge machinery and asks whether they can be consistently transported into one another. It introduces measurable failures such as shearing and nontrivial holonomy and tests them on a frozen Llama-3.2-3B model. citeturn451391view0

This suggests a surprisingly concrete version of:

$$
\text{meaning} \neq \text{one vector}.
$$

Instead,

$$
\boxed{
\text{meaning}
=
\text{compatible family of context-dependent representations}.
}
$$

That may be a much better mathematical formulation of contextual polysemy.

For example:

```text
"bank"
```

doesn't have to possess some Platonic embedding vector $v_{\rm bank}$.

Instead:

```text
finance context:
    bank ↦ financial institution

river context:
    bank ↦ river boundary

aviation context:
    bank ↦ rotational maneuver
```

with compatibility maps wherever contexts interact.

That is fundamentally sheaf-like.

---

# Mahadevan goes in a somewhat different direction

Mahadevan's **Topos Theory for Generative AI and LLMs** isn't primarily saying:

> convert sentences into logical theories.

Instead he treats whole Transformer-computed functions categorically and asks what new architectures become available from universal constructions:

$$
\text{pullback},\quad
\text{pushout},\quad
\text{equalizer},\quad
\text{coequalizer},\quad
\text{exponential},\quad
\Omega.
$$

The idea is that instead of assembling models only as

```text
layer → layer → layer → layer
```

or

```text
experts → router → output,
```

we could build architectures corresponding to arbitrary categorical diagrams. citeturn697572view2

That is interesting, but it is conceptually different from Caramello/Lafforgue.

**Mahadevan:** use category/topos theory to build new compositions of neural functions.

**Caramello/Lafforgue:** use toposes as representations of **semantic information, formal theories, invariants and abstraction**.

For the direction you're interested in, I think the second is deeper.

---

# And the older Abramsky–Sadrzadeh paper is unexpectedly important

Their 2014 paper contains almost exactly the semantic layer I described previously.

They start from:

$$
\text{local sentence meanings}
$$

and define **semantic unification** as gluing them into

$$
\text{global discourse meaning}.
$$

They specifically treat ambiguous anaphoric references and allow multiple possible gluings with probabilistic ranking. citeturn697572view0

That gives us:

```text
LLM encoder
      ↓
candidate local meanings
      ↓
presheaf / sheaf
      ↓
gluing
      ↓
globally consistent discourse state
```

And now Caramello/Lafforgue give us machinery for turning that global state into something much richer:

```text
global semantic state
       ↓
classifying topos
       ↕
formal theory
       ↓
subtoposes
       ↓
reasoning / learning / abstraction
```

That combination seems much more promising to me than simply saying “a transformer is a topos.”

---

# The research program I'd extract from all of this

Putting these papers together—not claiming that any one author proposes this exact architecture—I get:

```text
                         TRANSFORMER
                              │
                              ▼
                     contextual parsing
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
        local meaning U₁             local meaning U₂
                │                           │
                └───────── overlap ─────────┘
                              │
                              ▼
                         SHEAF GLUING
                              │
                              ▼
                    coherent semantic state
                              │
                              ▼
                    CLASSIFYING TOPOS
                              │
                  ┌───────────┴───────────┐
                  ▼                       ▼
             formal theory           geometry
                  │                       │
                  └───────────┬───────────┘
                              ▼
                subtopos / quotient theory
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
               proof       abstraction   analogy
                 │            │            │
                 └────────────┼────────────┘
                              ▼
                    new semantic state
                              │
                              ▼
                         LLM decoder
```

The component mappings have genuine antecedents in the literature: local-to-global linguistic semantics in Abramsky–Sadrzadeh; syntactic learning and relative toposes in Caramello; subtoposes/formal-language transformations in Lafforgue; and constructive provability/topology machinery in their joint 2025 work. citeturn697572view0turn518370search6turn447155search9turn253465view0

What **doesn't** exist yet, as far as I can find, is somebody putting all of that together and training a serious language model whose native latent semantic state is a sheaf/classifying-topos structure. The explicitly architectural papers remain largely theoretical; the strongest empirical work I've found instead applies sheaf/categorical ideas to **existing** LLMs, such as Javidnia's frozen-Llama experiments and Bottman et al.'s operadic reasoning measurements. citeturn697572view2turn451391view0turn796724academia0

## What I would read first

1. **Caramello — _Syntactic learning via Topos Theory_**. This gives the AI philosophy and is short. citeturn518370search6  
2. **Lafforgue — _Some sketches for a topos-theoretic AI_**, then his September 2024 presentation. This gives the subtopos/formal-language architecture. citeturn447155search11turn447155search9  
3. **Abramsky & Sadrzadeh — _Semantic Unification_**. This supplies a concrete language/sheaf interpretation. citeturn697572view0  
4. **Caramello & Lafforgue — _Generation of Grothendieck topologies..._**. Hard math, but probably the crucial logical engine. citeturn253465view0  
5. **Javidnia — _A Gauge Theory of Superposition_**. This shows what a context-local/sheaf view of actual LLM representations might look like experimentally. citeturn451391view0  
6. Then read **Mahadevan** and **Villani/McBurney** to see the alternative “categorify the Transformer itself” route. citeturn697572view2turn253465view2

The next step I think would be worthwhile is to take these papers and derive a **precise toy architecture**: define the site $C$, what an object/context is, what the stalks or sections contain, how an LLM predicts restriction maps, what constitutes a global section, and how Caramello–Lafforgue subtopos operations become differentiable/computable. That would tell us whether this is merely attractive language or whether there is an implementable research program hiding inside it.

I can also keep an eye on arXiv for new work specifically combining topoi/sheaves/category theory with LLMs.

genui{"suggest_automation":{"label":"Track topos + LLM papers"}}

```json
{"title":"Track topos + LLM papers","prompt":"Check for new papers, preprints, talks, or research updates connecting topos theory, sheaf theory, category theory, or related categorical methods with LLMs and generative AI, with particular attention to Olivia Caramello, Laurent Lafforgue, and closely related work. Notify me only when there are meaningful new developments, and briefly summarize why each item matters. If there is nothing meaningfully new, do not notify me.","schedule":"BEGIN:VEVENT\nRRULE:FREQ=DAILY\nEND:VEVENT","timing_mode":"condition_watch"}
```

Created **Track topos + LLM papers**. It will check daily for meaningful new work involving Caramello, Lafforgue, topos/sheaf/category theory, LLMs, and generative AI, and only notify you when something substantive appears.

There are a few worthwhile updates.

- **The most relevant new item is Sridhar Mahadevan’s “Odyssey” framework** (arXiv, June 25, 2026), followed by an ICML tutorial on July 6. ODYSSEY explicitly models foundation-model knowledge as an organized sheaf over local contexts: local representation families, restriction maps, gluing rules, obstruction signals, and promotion gates are all first-class objects. It then uses **left and right Kan extensions** to construct and validate larger semantic structures from local evidence. This is unusually close to the architecture we were discussing: `local meanings → compatibility/gluing → global semantic structure → verified inference`. The paper says the framework is implemented and tested across several “foundries,” although I have not found independent empirical validation comparable to standard LLM benchmarks yet. citeturn815555academia19turn815555search2

- **A useful reality check arrived on August 3: _Benchmarking Sheaf Neural Networks for Inductive Tasks_.** Fiorini, Coppola and Liò ran 1,890 controlled experiments over 14 datasets. Their main result is important for anyone contemplating a sheaf-native LLM: the choice of **restriction maps** matters a lot, but ordinary architectural choices around the sheaf operator explain even more variance, and the sheaf models did **not** beat the strongest baselines under matched protocols. So sheaf machinery appears computationally workable, but there is no evidence yet that the mathematics itself supplies a performance free lunch. citeturn643522academia44

- **Olivia Caramello has just made videos from a Paris-Saclay “Toposes and AI” conference publicly available.** Her contribution is titled *Toposes and ‘bridges’ for artificial general intelligence* and explicitly presents Grothendieck toposes, geometric logic and relative toposes as a framework for structuring AGI. This is not a new theorem or LLM architecture, but it is a current statement of how she herself is framing the AI program. Her existing course material continues to emphasize relative toposes as models of learning at multiple levels of abstraction, including applications to Raven matrices and ARC-like tasks. citeturn701742search9turn876929search3

I did **not** find a new Caramello–Lafforgue arXiv paper superseding their 2025 joint work on Grothendieck topologies/provability or their large introduction to sites and toposes. Those remain the mathematical backbone of their program. citeturn574935academia34turn574935academia33

The item I would pay the most attention to is **ODYSSEY/Kan Extension Transformers**, because it has moved beyond “topos theory might be useful for AI” into an explicit computational design with contexts, restriction maps, gluing, obstructions and categorical extension operators. That is the closest thing I have found so far to an actual implementation of the semantic architecture we were sketching.

