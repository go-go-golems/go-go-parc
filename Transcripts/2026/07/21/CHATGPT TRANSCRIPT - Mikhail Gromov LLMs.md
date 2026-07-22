# Mikhail Gromov LLMs

- URL: https://chatgpt.com/c/6a5f1e37-a98c-83ea-aa05-1ffdd086ae85
- Created: 2026-07-21T07:22:33.929Z

## Turn 0 - user

- Message ID: `4c0ebdc4-d254-44e6-9833-b6c061de903d`

Mikhail gromov- llms

## Turn 1 - assistant

- Message ID: `3c33593c-804a-40b4-9624-d5dba45eb48e`
- Model: `gpt-5-6-thinking`

I’ll check whether this refers to a recent talk, article, or commentary by mathematician Mikhail Gromov about large language models.

## Turn 2 - assistant

- Message ID: `b97f9feb-0cf6-44e8-b85d-88f1185880b2`
- Model: `gpt-5-6-thinking`



## Turn 3 - assistant

- Message ID: `5d72d316-cdf7-4597-a525-4fc054bd7c8b`
- Model: `gpt-5-6-thinking`

iturn625483image0

You’re probably referring to **Mikhail “Misha” Gromov’s recent lectures connecting mathematics, biology, cognition, and large language models**.

In April 2026, Gromov—an Abel Prize–winning geometer—released a four-part lecture series titled:

**“Generation, Transformation, Transmission, Memorization, Storage and Expression of Information: From Cell to LLM — Signals, Structures, Knowledge and Learning.”** citeturn114705view0

His approach is not a conventional explanation of transformers, attention, or model training. He places LLMs inside a much broader class of **information-processing systems**, comparing them with:

- biological cells and viruses;
- evolutionary processes;
- memory and transmission mechanisms;
- human language and cognition;
- mathematical structures that emerge from large collections of signals.

A recurring underlying question is: **What does it mean for a system to learn, know, represent, or understand something?** This continues themes from his 2018 manuscript *Learning and Understanding in the Mirror of Mathematics*, where he argues that natural-language understanding—and even human understanding of our own understanding—remains conceptually unresolved. citeturn114705view2

The four lectures total slightly over six hours and are hosted on Carmin/IHES. They are best regarded as speculative, interdisciplinary mathematical philosophy rather than an introductory LLM course. The surrounding IHES program explicitly seeks mathematical structures explaining what LLMs implicitly learn, while also studying how LLMs can be used to do mathematics. citeturn114705view3

Would you like a lecture-by-lecture summary or a critical analysis of Gromov’s ideas?

## Turn 4 - user

- Message ID: `efefe549-d5ef-491d-b34e-30b58167e3de`

Ihes - llms

## Turn 5 - assistant

- Message ID: `afc82305-df16-4006-ad15-4360b234ceca`
- Model: `gpt-5-6-thinking`

I’ll identify the IHES program, lectures, and available recordings related to large language models.

## Turn 6 - assistant

- Message ID: `23185adc-b885-411a-8b1e-86d5b1d3adde`
- Model: `gpt-5-6-thinking`



## Turn 7 - assistant

- Message ID: `245811fa-d800-424b-a1bb-2ac10457fa4c`
- Model: `gpt-5-6-thinking`

## IHES and LLMs

**IHES**—the *Institut des Hautes Études Scientifiques* near Paris—is developing a research program around **mathematics and large language models**. Its central event is the annual conference **“Mathematics for and by Large Language Models.”** citeturn852802view2turn852802view0

The program studies two directions:

- **Mathematics for LLMs:** mathematical descriptions of what models learn, their representations, expressive power, training dynamics, and limitations.
- **LLMs for mathematics:** using language models, agents, and formal systems for conjecturing, proving, calculating, and exploring mathematical problems. citeturn852802view1

### 2026 conference

The third edition took place on **May 28, 2026**. Organizers included Michael Douglas, Amaury Hayat, Julio Parra-Martinez, and Yiannis Vlassopoulos. Speakers included researchers from Google DeepMind, École Normale Supérieure, Athena Research Center, and IHES. citeturn852802view0

The recordings include:

- **The Expressive Power of Large Language Models** — Gabriel Peyré  
- **Why AI Needs Formal Mathematics** — Edward Lockhart  
- **Agents and ML Algorithms in Mathematics** — Bogdan Georgiev  
- **ReLU and Softplus Neural Nets as Games** — Yiannis Vlassopoulos  
- **A Demo of Numina Studio** — Jia Li citeturn452984view0

### Mikhail Gromov’s separate IHES series

Gromov’s four lectures, delivered from **April 7–28, 2026**, are titled **“From Cell to LLM: Signals, Structures, Knowledge and Learning.”** They treat LLMs as one instance of a broader information system, alongside biological cells, evolution, signaling, memory, language, and cognition. citeturn452984view1turn678210search11

The most direct route is the **2026 conference recordings** for technical AI-and-mathematics content, and **Gromov’s four lectures** for the broader conceptual framework.

## Turn 8 - user

- Message ID: `b4a11f38-6c38-4209-bc0e-09162091a9f2`

The Expressive Power of Large Language Models — Gabriel Pey

## Turn 9 - assistant

- Message ID: `918e69f0-6e40-4eef-8d7e-48f827d00ecf`
- Model: `gpt-5-6-thinking`

I’ll locate the official recording and summarize Gabriel Peyré’s main claims, mathematical framework, and conclusions.

## Turn 10 - assistant

- Message ID: `08a87376-a124-4faf-8d55-d961130c7ff0`
- Model: `gpt-5-6-thinking`



## Turn 11 - assistant

- Message ID: `220ce4e0-4e87-4ded-97b6-b8324a8ded40`
- Model: `gpt-5-6-thinking`



## Turn 12 - assistant

- Message ID: `138093a6-b192-4d80-9dcc-529405bf1728`
- Model: `gpt-5-6-thinking`



## Turn 13 - assistant

- Message ID: `72144bc2-2359-49c5-9266-7e3574121902`
- Model: `gpt-5-6-thinking`

iturn166130image0

## *The Expressive Power of Large Language Models* — Gabriel Peyré

The correct spelling is **Gabriel Peyré**. This is a researcher-level IHES lecture recorded on **28 May 2026** for the third *Mathematics for and by Large Language Models* conference. The official recording is in English and lasts roughly one hour. citeturn694179view0turn554365view0

### Central question

Peyré asks:

> What classes of functions can transformers approximate, particularly when the number of input tokens is variable or arbitrarily large?

An LLM alternates two fundamentally different operations:

1. **MLP layers** transform each token separately.
2. **Self-attention layers** make each token depend on the entire collection of tokens.

Classical universal-approximation theory explains MLPs reasonably well when the input belongs to a fixed finite-dimensional space. Attention is harder because its input is a sequence whose length may change. The resulting object is closer to a function acting on a **distribution of tokens** than to an ordinary finite-dimensional function. This contrast is the stated focus of the lecture. citeturn694179view1turn453519view0

### The measure-theoretic viewpoint

For tokens \(x_1,\ldots,x_n\), represent the context by the empirical probability measure

\[
\mu_n=\frac1n\sum_{i=1}^{n}\delta_{x_i}.
\]

Instead of treating a prompt merely as one long vector, the theory treats it as a probability distribution over token representations.

An in-context operation can then be written schematically as

\[
(x,\mu)\longmapsto F(x,\mu),
\]

where \(x\) is the token being updated and \(\mu\) describes its context.

The relevant continuity is measured using a **Wasserstein distance** between token distributions. This gives a single framework covering finite sequences, sequences of different lengths, and limiting distributions containing infinitely many tokens.

### Main expressivity result behind the talk

Peyré’s closely related work with Takashi Furuya and Maarten de Hoop proves a transformer universal-approximation theorem:

- deep transformers can approximate continuous in-context mappings;
- the approximation is uniform on compact token domains;
- one transformer can handle an arbitrary, potentially infinite, number of context tokens;
- the token embedding dimension remains fixed;
- the number of attention heads can also remain fixed, proportional to the token dimension;
- the theory covers both ordinary bidirectional attention and masked causal attention used in language models. citeturn175097academia16

Thus the theoretical power of attention is not tied to a predetermined context length.

### Why attention matters

An MLP can construct complicated nonlinear functions of an individual token, but it cannot by itself aggregate information from the context. Attention supplies operations resembling integrals against the contextual distribution:

\[
x\longmapsto
\frac{\int e^{\langle Qx,Ky\rangle}Vy\,d\mu(y)}
     {\int e^{\langle Qx,Ky\rangle}\,d\mu(y)}.
\]

By composing these contextual aggregation operations with tokenwise MLPs, a transformer can construct increasingly general functions of both a token and its surrounding distribution.

The proof strategy is therefore different from a standard MLP proof: it must establish approximation in an **infinite-dimensional space of probability measures**, not merely in \(\mathbb R^d\).

### Important limitation

“Universal” does **not** mean that a transformer:

- will learn the desired function from realistic data;
- will learn it efficiently;
- will generalize outside its training distribution;
- will reason reliably;
- or will represent the function with practical depth and parameter count.

Expressivity only establishes that suitable transformer parameters **exist**. Optimization, sample complexity, robustness and generalization are separate problems.

Peyré’s related analysis also shows why stability is nontrivial: the Lipschitz constant of self-attention can grow approximately as \(\sqrt n\) with sequence length in one regime, although a sequence-length-independent mean-field regime emerges for sufficiently large contexts. citeturn175097academia19

### Bottom line

The lecture’s main conceptual move is:

\[
\text{variable-length token sequence}
\quad\longrightarrow\quad
\text{probability distribution of tokens}.
\]

That transformation lets transformer expressivity be studied using Wasserstein geometry and infinite-dimensional approximation theory. It provides a rigorous explanation of why attention can implement highly general context-dependent operations, while leaving open whether those operations can be learned efficiently or reliably in real LLMs. The official recording is available on the Carmin/IHES page. citeturn694179view0

## Turn 14 - user

- Message ID: `9104503e-4e3d-4153-8ff6-b07710a98440`

Analyze and explain the gromov paper

## Turn 15 - assistant

- Message ID: `b46bf23b-cbe7-4d38-a1d5-b16133a210b3`
- Model: `gpt-5-6-thinking`

I’ll treat this as Gromov’s **“Learning and Understanding in the Mirror of Mathematics”** and analyze its argument, structure, strengths, and weaknesses.

## Turn 16 - assistant

- Message ID: `f52217ac-d504-4c73-a52e-6523478c981d`
- Model: `gpt-5-6-thinking`



## Turn 17 - assistant

- Message ID: `fb8e896a-2b0d-4a99-a494-ec4f9d304a83`
- Model: `gpt-5-6-thinking`



## Turn 18 - assistant

- Message ID: `f2f7f11f-8aa6-4fc8-8012-8d6430c1ae64`
- Model: `gpt-5-6-thinking`

## Scope

This analyzes Mikhail “Misha” Gromov’s 2018 draft **_Learning and Understanding in the Mirror of Mathematics, Chapters 1 and 2_**. It is not a conventional mathematical paper with definitions, theorems, and proofs. Gromov explicitly describes the proposed framework as incomplete, imprecise, and lacking an adequate mathematical language. It is better read as a **research program for mathematically reconstructing cognition**. citeturn149615view0turn149615view1

## The central thesis

Gromov begins from a skeptical premise: our subjective feeling that we understand something tells us almost nothing about how understanding actually works. Introspection is distorted, while observable behavior is only an external projection of hidden mental structure. He therefore proposes studying relatively “impersonal” manifestations of cognition—especially language, mathematics, and chess—and reconstructing the machinery capable of producing them. citeturn149615view0turn103129view0

His core idea is:

> Understanding is a structured internal network learned from streams of signals.

The system does not store every sentence, image, or chess position. It discovers reusable patterns, relations, transformations, similarities, and abstractions that allow it to interpret vastly more inputs than it has explicitly encountered.

## Gromov’s basic mathematical picture

He introduces three principal objects.

### Signal flows: \(\mathrm{SIG}\)

A signal flow may consist of text, speech, images, motion, tactile information, or synchronized combinations of modalities. The important point is that the learner initially receives signals, not ready-made objects, meanings, grammatical rules, or concepts. citeturn149615view1

### The understanding network: \(\mathrm{NET}\)

From the signal flow, the learner constructs a multiscale, multilayer, “colored” network:

\[
\mathrm{SIG}\longrightarrow \mathrm{NET}.
\]

A modernized interpretation is:

- **nodes** represent recurring units, patterns, or concepts;
- **edges** represent associations and transformations;
- **edge colors** represent different types of relations;
- **higher levels** represent abstractions, classes, and generalizations.

The network is created by suppressing redundancy, identifying recurring structures, and grouping similar signals. It is dynamic: perception activates it, responses are generated from it, and learning continually modifies it. citeturn149615view1turn411876view3

### The learning operation: \(L\)

Gromov wants a general learning rule of the form

\[
\mathrm{NET}_{t+1}
   =L(\mathrm{NET}_t,\mathrm{SIG}_t).
\]

The learner begins with a relatively small “baby” network and repeatedly updates it through exposure to signals. He proposes defining understanding as a **quasi-stationary state**: the network has become sufficiently organized that ordinary new signals refine it without radically reorganizing it. citeturn411876view1

That is one of the paper’s most important distinctions:

\[
\text{simple learning rules}
\quad\not\Rightarrow\quad
\text{simple learned representation}.
\]

A short algorithm may produce an enormously complicated network, just as simple dynamical laws can generate extremely intricate trajectories.

## The “atoms” of understanding

Chapter 2 attempts to identify elementary operations from which understanding might be assembled.

### Discretization

Continuous or complicated signal streams are divided into units: phonemes, words, phrases, objects, motions, situations, and eventually abstract concepts. Some nodes correspond directly to perceptible units; others are higher-order constructions such as “animal,” “word,” or “something moving.” citeturn812588view3

This is not merely tokenization. Gromov is interested in how a system discovers the appropriate units rather than receiving them all in advance.

### Concurrency and association

Signals occurring near one another become candidates for functional relationships. Nearby words, simultaneous visual features, and recurring combinations produce persistent links in the internal network. Higher-order relations then emerge from combinations of simpler ones. citeturn411876view3

### Similarity

Recognition depends on repeated patterns and on the ability to recognize different instances as “the same” in some relevant respect.

Gromov gives a notably modern distributional principle: two units are similar when their functional partners are similar. For language, similarity is therefore not principally a matter of spelling or internal shape; it depends on how words interact with large contexts. citeturn812588view5

This is close to the logic behind embedding spaces: words or concepts become neighbors because they participate in comparable relational structures.

### Transformations and invariance

Understanding includes recognizing an object through transformations:

- changes of viewpoint or scale;
- active-to-passive sentence transformations;
- statement-to-question transformations;
- translations between languages;
- reformulations and summaries.

The object is understood partly through what can be changed while preserving some relevant structure. Gromov consequently emphasizes transformation arrows and borrows language from category theory—objects, morphisms, compositions, and functors. citeturn411876view5

His category-theoretic point is conceptual rather than technical:

> An object is not understood in isolation; it is understood through its relations and transformations within a community of objects.

He calls this **communality**. The internal nature of an object is revealed by the network of arrows entering and leaving it. citeturn812588view1

### Reduction and abstraction

Classification, clustering, summarization, quotienting, and generalization all reduce a large collection of signals to a smaller structural description.

Examples include:

\[
\text{individual cat}\rightarrow\text{cat}\rightarrow\text{animal},
\]

or

\[
\text{long text}\rightarrow\text{summary}.
\]

Understanding therefore involves compression, but not arbitrary compression. The reduced representation must preserve relations important for prediction, reconstruction, action, or further reasoning. citeturn149615view2turn441816view0

### Context and disambiguation

The meaning of a signal cannot generally be assigned independently of its surrounding flow. Context identifies which interpretation of an ambiguous word or structure is active. Gromov treats disambiguation as an interaction between prior network structure and cues in the current input. citeturn812588view4turn441816view0

## Gromov’s account of meaning

Gromov adopts a version of the **distributional hypothesis**:

\[
\text{the meaning of a unit is determined by its functional relations}.
\]

In his network vocabulary, meanings are something like types or “colors” attached to similarity and functional links. A word does not possess meaning as an isolated object; its meaning comes from its position in a relational system. citeturn149615view2turn441816view0

But he does not endorse a purely textual account. Distributional meaning can connect with reference to objects and events only when language is embedded in a sufficiently broad signal flow containing perception and other information from the world. In modern terminology, he anticipates the distinction between:

- **linguistic distributional competence**, learned from text;
- **grounded meaning**, learned through relationships between text, perception, and action.

That qualification is central to assessing LLMs.

## Prediction and generation

Near the end of the draft, Gromov describes predictive competence as one component of “descriptive understanding.” A system extracts features, learns correlations between them, and predicts future structures from past signal patterns. But he treats prediction as only one element inside a richer hierarchy of reductions and relations. citeturn441816view0

He also proposes a reverse map:

\[
\mathrm{NET}\longrightarrow\mathrm{SIG}.
\]

The network formed from language must itself generate language. Speech or text production can be viewed as movement through a network of learned rules and relationships. He therefore sees perception and generation as dual processes:

\[
\mathrm{SIG}\rightleftarrows\mathrm{NET}.
\]

This is strikingly close to the encoder–generative-model distinction, although Gromov does not specify a neural implementation. citeturn812588view7turn441816view0

## Relation to modern LLMs

The paper is not specifically a transformer or LLM paper. Nevertheless, several parts align closely with what later large models demonstrated.

Transformers process each token in relation to other tokens through self-attention, while autoregressive language models learn by predicting continuations of large textual signal streams. Scaling such training produces task-general behavior without explicitly programming separate grammatical or semantic modules. citeturn481232academia17turn481232search0

This resembles Gromov’s program in several respects:

- training is based on formal signal relationships rather than hand-coded meanings;
- context dynamically changes the representation of a unit;
- similar functional usage produces similar internal representations;
- prediction acts as a learning signal;
- a general algorithm produces a complicated, domain-rich internal structure;
- the learned structure supports both perception and generation.

Multimodal systems also move toward Gromov’s broader proposal by learning joint relationships between language and images rather than treating language as an isolated signal flow. CLIP, for example, learns a shared image–text representation through correspondence between paired signals. citeturn481232search1turn481232search3

But Gromov’s \(\mathrm{NET}\) should not be identified literally with a transformer. An LLM’s knowledge is distributed across parameters and context-dependent activations, not stored as an explicit graph with interpretable nodes and typed edges. His network is an abstract target description of cognitive organization, not an architecture specification.

## What the paper gets right

Its strongest insight is that the simplicity should be sought in the **learning dynamics**, not in the final representation. Modern foundation models reinforce this: a relatively uniform training objective can produce representations supporting translation, classification, completion, question answering, and limited forms of reasoning. citeturn411876view1turn481232search0

The paper also correctly emphasizes:

- context rather than isolated symbols;
- relational rather than purely intrinsic representations;
- hierarchy and compression;
- invariance under transformations;
- prediction as a component of understanding;
- multimodal grounding;
- the difference between grammatical legality and semantic plausibility.

His chess comparison is useful here. Chess syntax specifies legal moves, but chess competence concerns the much smaller and highly structured subset of positions that are strategically plausible. Similarly, a language model must learn more than which sentences are grammatically constructible; it must learn which structures normally occur and how they function. citeturn411876view2turn411876view4

## Main weaknesses

The framework remains largely metaphorical. “Colors,” “similarity,” “naturality,” “quasi-equivalence,” “understanding,” and the space of all understanding networks are not defined precisely enough to support a theorem or executable algorithm. Gromov acknowledges this limitation himself. citeturn149615view1turn411876view1

Defining understanding through quasi-stability is also insufficient. A network can become stable while encoding systematic errors. Stability must be supplemented by criteria involving truth, calibration, causal intervention, generalization, or successful action.

The category-theoretic language is suggestive but underdeveloped. Gromov admits that ordinary category theory does not directly apply: many cognitive transformations are only approximately composable, can be irreversible, and may change their relational “colors.” citeturn812588view1turn411876view5

Finally, his biological and evolutionary discussions contain broad conjectures and rough numerical estimates rather than a validated cognitive theory. They motivate constraints—simplicity, universality, parallelism, and evolutionary accessibility—but do not derive the proposed architecture.

## Overall assessment

The paper’s most useful formulation is:

\[
\boxed{
\text{Understanding is a stable, multiscale relational model
constructed from signal flows by universal learning rules.}
}
\]

It is a strong conceptual blueprint but not a finished theory. Modern LLMs provide evidence that several ingredients—distributional learning, contextual representation, prediction, compression, and general-purpose generation—are remarkably powerful. They do **not** establish that these ingredients alone satisfy Gromov’s larger conception of understanding, especially where grounding, causal structure, self-modeling, and reliable abstraction are concerned.

Gromov is asking a deeper question than whether a transformer can approximate a function: **what internal mathematical organization would make competent prediction and generation count as understanding?** His paper identifies promising primitives for that organization, but leaves their precise synthesis open.

